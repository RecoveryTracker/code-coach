"""Tickets: one small codebase, and the team's queue of work against it.

Every other screen in this app hands over a fresh piece of code and
throws it away afterwards. Work does not go like that. There is one
project, it already does things people rely on, and the tickets arrive
in order: a bug report, a feature request, a refactor, a change of
rules. Each ticket starts from the project as it stands after all the
earlier ones, so the code you are editing is code with a history.

A ticket is checked two ways, and the second is the lesson:

  what it asks     the functions this ticket adds or changes, against
                   the new behaviour
  what must keep   every other function in the project, against what
  working          it already did - so a fix that breaks something old
                   fails the ticket, the way it would fail review

The machinery is the kata machinery. Each checked function is a Kata
built on the fly - a name, its parameters, its cases and a Python oracle
- and the learner's whole file goes through `harness` and `judge` like
any kata. The drivers are appended one after another to a single copy of
the file, so a ticket costs one process however many functions it
checks; each driver prints its own marker line, in order, and each line
is judged against its own function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from code_coach.kata import MARKER, NO_FUNCTION, Kata, harness, judge

KINDS = ("bug", "feature", "refactor", "change")


@dataclass(frozen=True)
class Check:
    """One function of the project, and how it must behave."""

    name: str
    params: tuple[str, ...]
    #: Each is the full argument tuple for one call.
    cases: tuple[tuple, ...]
    #: The truth, in Python whatever the project is written in.
    solve: Callable[..., Any]
    #: A few answers written out by hand, as (arguments, answer), so the
    #: oracle is checked against something that did not come from it.
    checks: tuple[tuple[tuple, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Ticket:
    id: str
    title: str
    #: One of KINDS.
    kind: str
    #: The ticket as a teammate wrote it.
    report: str
    #: The whole file before this ticket: the previous ticket's `after`.
    start: str
    #: The whole file with this ticket done - the model answer.
    after: str
    #: Every function of the project as it should behave once this
    #: ticket is done, new and old alike.
    checks: tuple[Check, ...]
    #: The names of the checks this ticket adds or changes. Everything
    #: else in `checks` is a regression check: it already passed.
    new: tuple[str, ...]
    hint: str = ""
    #: Shown once it passes.
    lesson: str = ""


@dataclass(frozen=True)
class Project:
    id: str
    title: str
    #: "python" or "javascript".
    language: str
    story: str
    tickets: tuple[Ticket, ...]


def projects() -> tuple[Project, ...]:
    from code_coach.tickets.content import PROJECTS

    return PROJECTS


def project(project_id: str) -> Project | None:
    return next((p for p in projects() if p.id == project_id), None)


def ticket(project_id: str, ticket_id: str) -> Ticket | None:
    found = project(project_id)
    if found is None:
        return None
    return next((t for t in found.tickets if t.id == ticket_id), None)


def as_kata(proj: Project, tick: Ticket, check: Check) -> Kata:
    """One check as a kata, so the kata driver and marker can run it."""
    return Kata(
        id=f"{tick.id}:{check.name}",
        name=check.name,
        brief="",
        params=check.params,
        cases=check.cases,
        solve=check.solve,
        language=proj.language,
        family=proj.title,
    )


def program(proj: Project, tick: Ticket, code: str) -> str:
    """The learner's file with one driver per checked function after it.

    `harness(kata, "")` is exactly the driver for that kata, so this is
    the kata harness applied once per function to the same file.
    """
    drivers = "".join(
        harness(as_kata(proj, tick, c), "") for c in tick.checks)
    return code.rstrip() + "\n" + drivers


def _split(stdout: str) -> tuple[list[str], str]:
    """The drivers' lines, in order, and whatever the learner printed."""
    found: list[str] = []
    theirs: list[str] = []
    for line in stdout.splitlines():
        at = line.find(MARKER)
        missing = line.find(NO_FUNCTION)
        if at >= 0:
            theirs.append(line[:at])
            found.append(line[at:])
        elif missing >= 0:
            theirs.append(line[:missing])
            found.append(NO_FUNCTION)
        else:
            theirs.append(line)
    return found, "\n".join(t for t in theirs if t)


def judge_ticket(proj: Project, tick: Ticket, stdout: str, stderr: str,
                 exit_code: int) -> dict:
    """Read one combined run and say, function by function, what passed."""
    found, theirs = _split(stdout)
    broke = ""
    if not found:
        # Nothing reached a single driver: the file itself did not run.
        # One message, rather than the same traceback once per function.
        broke = judge(as_kata(proj, tick, tick.checks[0]),
                      theirs, stderr, exit_code).broke or "the file did not run"

    functions = []
    for n, check in enumerate(tick.checks):
        kata = as_kata(proj, tick, check)
        if n < len(found):
            outcome = judge(kata, found[n], "", 0)
        else:
            outcome = judge(kata, theirs, stderr, exit_code)
            if not outcome.broke:
                outcome = type(outcome)(broke="the run stopped before this one")
        functions.append({
            "name": check.name,
            "params": list(check.params),
            "new": check.name in tick.new,
            "passed": outcome.passed,
            "broke": "" if broke else outcome.broke,
            "count": outcome.count,
            "total": len(check.cases),
            "results": [
                {
                    "args": list(r.args),
                    "want": r.want,
                    "got": r.got,
                    "error": r.error,
                    "passed": r.passed,
                    "changed": r.changed,
                }
                for r in outcome.results
            ],
        })
    return {
        "passed": not broke and all(f["passed"] for f in functions),
        "broke": broke,
        "stdout": theirs,
        "functions": functions,
        "new_passed": all(f["passed"] for f in functions if f["new"]),
        "kept_passed": all(f["passed"] for f in functions if not f["new"]),
    }


def run_ticket(proj: Project, tick: Ticket, code: str) -> dict:
    """Run the learner's whole file against every check of this ticket.

    Returns {passed, broke, stdout, functions, new_passed, kept_passed};
    each entry in `functions` is {name, params, new, passed, broke,
    count, total, results}, where `new` says whether it is what the
    ticket asks for or something that must keep working.
    """
    from code_coach.engine import run_code

    stdout, stderr, exit_code = run_code(
        program(proj, tick, code), language=proj.language)
    return judge_ticket(proj, tick, stdout, stderr, exit_code)
