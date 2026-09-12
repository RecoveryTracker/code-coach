"""Kata: write a function, and it gets called with inputs you did not choose.

Everything else in this app asks a program to print something and compares
what came out. That is the right check for a drill — there are several
ways to print the numbers one to five and all of them should pass — but it
trains only one thing, because the program is only ever run on the single
input the prompt named.

Codewars and freeCodeCamp work the other way round, and the difference is
not cosmetic. A function called with ten inputs is a function whose empty
list, whose single element, whose zero and whose negative all have to
work. That is the part of problem solving a print-based exercise cannot
reach: you never meet the edge case, because you never run the edge case.

So a kata is a signature, a sentence, and a set of cases. Your code is run
with a driver appended that calls the function once per case and reports
each one. A failure says which input broke it, which is the only feedback
that actually moves you forward.

Two rules hold this together, and both are the ones the workbook already
lives by.

The expected answer is computed, never written down. Each kata carries a
reference solution in Python, and the cases carry only inputs — the
answers come from running the reference. Writing out `digital_root(99) ==
9` by hand for twelve cases is twelve chances to be wrong about the thing
you are marking against.

And the reference is executed, not trusted. The suite runs every kata's
own solution through the same driver a student's would go through, so a
reference that does not actually pass its own cases fails the build
rather than quietly marking correct answers wrong.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Kata:
    """One function to write, and the inputs it will be called with."""

    id: str
    #: The function the student must define.
    name: str
    #: What it has to do, in one sentence.
    brief: str
    #: The parameters, for the signature shown on screen.
    params: tuple[str, ...]
    #: The inputs. Each is the full argument tuple for one call.
    cases: tuple[tuple, ...]
    #: The answer, computed rather than written down. Takes the same
    #: arguments as the function being asked for.
    solve: Callable[..., Any]
    #: A worked example, shown before the first attempt.
    example: str = ""
    #: Which family this belongs to, for grouping on screen.
    family: str = ""
    #: A hint that costs nothing to read and is not the answer.
    hint: str = ""
    #: A few answers written out by hand, as (arguments, answer).
    #:
    #: These exist because the obvious test does not work. Running the
    #: reference against expectations computed from the reference proves
    #: only that it agrees with itself — it passes however wrong the
    #: reference is, which was discovered by breaking one and watching
    #: the suite stay green. An answer typed out by a person is the only
    #: thing in the file that did not come from the code being checked.
    checks: tuple[tuple[tuple, Any], ...] = field(default_factory=tuple)

    @property
    def signature(self) -> str:
        return f"def {self.name}({', '.join(self.params)}):"

    def expected(self) -> tuple[Any, ...]:
        """What the reference says each case should produce."""
        return tuple(self.solve(*case) for case in self.cases)

    def reference(self) -> str:
        """The reference solution as source, for Show answer."""
        import inspect
        import textwrap

        return textwrap.dedent(inspect.getsource(self.solve)).strip()


# ── Running one ──────────────────────────────────────────────
#
# The student's code and a driver, in one file. Nothing new executes it:
# this goes through the same runner as everything else, which means the
# same timeout, the same output cap and the same lack of surprises.


DRIVER = '''

# ── the marker ───────────────────────────────────────────────
import json as _json


def _main() -> None:
    # Naming it something else is a different mistake from getting it
    # wrong, and reporting it as ten failed cases sends you looking in
    # the wrong place entirely.
    target = globals().get("{name}")
    if not callable(target):
        print("<<<KATANAME>>>")
        return
    cases = _json.loads({cases!r})
    results = []
    for args in cases:
        try:
            got = {name}(*args)
        except Exception as error:          # noqa: BLE001 - reported, not raised
            results.append({{"error": f"{{type(error).__name__}}: {{error}}"}})
            continue
        try:
            _json.dumps(got)
        except TypeError:
            got = repr(got)
        results.append({{"got": got}})
    print("<<<KATA>>>" + _json.dumps(results))


_main()
'''


def harness(kata: Kata, code: str) -> str:
    """The student's code with a driver appended."""
    return code.rstrip() + "\n" + DRIVER.format(
        cases=json.dumps([list(case) for case in kata.cases]),
        name=kata.name,
    )


MARKER = "<<<KATA>>>"
#: Printed instead when there is no function by that name at all.
NO_FUNCTION = "<<<KATANAME>>>"


@dataclass(frozen=True)
class CaseResult:
    """One call, and whether it was right."""

    args: tuple
    want: Any
    got: Any = None
    error: str = ""
    passed: bool = False


@dataclass(frozen=True)
class Outcome:
    """What happened when the whole kata ran."""

    results: tuple[CaseResult, ...] = field(default_factory=tuple)
    #: Set when the file did not run at all — a syntax error, or no such
    #: function. Distinct from failing cases, because the fix is
    #: different and telling someone "0 of 10 passed" when they have a
    #: typo in a keyword is not help.
    broke: str = ""

    @property
    def passed(self) -> bool:
        return bool(self.results) and all(r.passed for r in self.results)

    @property
    def count(self) -> int:
        return sum(1 for r in self.results if r.passed)


def judge(kata: Kata, stdout: str, stderr: str, exit_code: int) -> Outcome:
    """Read what the driver printed and say which cases passed.

    The marker matters. A student's own print statements are a normal part
    of working something out, and they land on stdout in front of the
    driver's line — so the results are taken from the marker onwards
    rather than from the whole of stdout.
    """
    if NO_FUNCTION in stdout:
        return Outcome(
            broke=f"there is no function called {kata.name} — check the "
                  f"name against the signature above")

    if MARKER not in stdout:
        detail = _tidy((stderr or stdout).strip())
        if exit_code != 0 and not detail:
            detail = f"the program exited with status {exit_code}"
        return Outcome(broke=detail or "nothing was printed by the marker")

    _, _, tail = stdout.partition(MARKER)
    try:
        raw = json.loads(tail.splitlines()[0])
    except (ValueError, IndexError):
        return Outcome(broke="the results could not be read")

    wants = kata.expected()
    if len(raw) != len(wants):
        return Outcome(broke="the run stopped part way through")

    results = []
    for args, want, entry in zip(kata.cases, wants, raw):
        if "error" in entry:
            results.append(
                CaseResult(args=args, want=want, error=entry["error"]))
            continue
        got = entry["got"]
        # JSON has one sequence type and Python has two, so a function
        # that correctly returns a tuple comes back as a list. Compare
        # the shapes rather than the containers.
        results.append(
            CaseResult(args=args, want=want, got=got,
                       passed=_same(got, want)))
    return Outcome(results=tuple(results))


def _tidy(detail: str) -> str:
    """Take the temporary file out of a traceback.

    The file is a scratch path in the system temp directory, which is
    true and unhelpful: it is the student's own code, and naming it after
    wherever it happened to be written reads as though the error is
    somewhere they have never been.
    """
    import re

    return re.sub(r'File "[^"]*", line', 'Line', detail)


def _same(got: Any, want: Any) -> bool:
    """Whether two answers agree, allowing for the round trip through JSON."""
    if isinstance(want, tuple):
        want = list(want)
    if isinstance(want, list) and isinstance(got, list):
        return len(got) == len(want) and all(
            _same(g, w) for g, w in zip(got, want))
    if isinstance(want, dict) and isinstance(got, dict):
        return got.keys() == want.keys() and all(
            _same(got[k], want[k]) for k in want)
    # True == 1 in Python, and a function that returns 1 where the answer
    # is True is not right. The workbook has been bitten by exactly this
    # once already, in a Lisp verification harness.
    if isinstance(want, bool) != isinstance(got, bool):
        return False
    return got == want


def katas(family: str | None = None) -> tuple[Kata, ...]:
    from code_coach.kata.content import KATAS

    if family is None:
        return KATAS
    return tuple(k for k in KATAS if k.family == family)


def kata(kata_id: str) -> Kata | None:
    return next((k for k in katas() if k.id == kata_id), None)


def families() -> tuple[str, ...]:
    seen: list[str] = []
    for k in katas():
        if k.family not in seen:
            seen.append(k.family)
    return tuple(seen)
