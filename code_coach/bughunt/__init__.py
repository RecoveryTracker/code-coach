"""Bug Hunt: a bug report, a program, and the process of finding it.

Forms already has Fix the bug: a short broken function and its failing
cases. That trains the repair. What it does not train is the part that
comes first and takes longer - getting from "a customer says this is
wrong" to the line that is wrong - and that part is a process that can
be taught. A study of first-year students found that teaching debugging
as explicit steps moved median correctness from 60% to 80% and cut the
median time from 28.7 minutes to 10.7; more than half of working
developers say they were never taught it at all.

So a hunt is those steps, in order, each one checked:

  reproduce  call the function until you find an input that shows the
             bug. The engine decides whether you have - it runs the
             broken program and the correct answer and compares them.
  locate     click the line where it goes wrong.
  explain    say what is actually wrong, out of a few misreadings.
  fix        change it, and every case has to pass, including the ones
             that already worked.

Where the answers come from
---------------------------
Not from anyone typing them in, as far as that is possible.

Whether an input reproduces the bug is computed: the broken program is
run on it, the oracle is asked, and the two compared. The line to click
is computed too - it is the line that differs between the broken
program and the fixed one, so it cannot disagree with the fix. What a
person does write is the explanation and its decoys, and the few
answers typed out by hand that the oracle is held to, which is the same
split the katas use.

The programs are longer than a kata's on purpose. In a four-line
function there is nothing to locate. Several of these put the symptom
in one function and the cause in another, because following a value
back to where it went wrong is most of what debugging is.
"""

from __future__ import annotations

import ast
import copy
import json
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class Hunt:
    """One bug, the report that found it, and the program it lives in."""

    id: str
    #: A short name for the list.
    title: str
    family: str
    language: str
    level: int
    #: The bug report, in the voice of whoever noticed it. It says what
    #: went wrong, never where.
    report: str
    #: The function you call to reproduce it, and its parameters.
    name: str
    params: tuple[str, ...]
    #: The whole program, with the bug in it.
    start: str
    #: The same program with the bug fixed. Same number of lines, one or
    #: two of them different - which is what makes "the line that is
    #: wrong" something that can be computed rather than asserted.
    fixed: str
    #: The correct behaviour, as a Python oracle. Python whatever the
    #: hunt is written in, for the reason the katas give.
    solve: Callable[..., Any]
    #: The input the report describes. It has to reproduce the bug,
    #: which the suite checks - a report that is not true is worse than
    #: no report.
    reported: tuple
    #: The cases the fix is run against. Some show the bug and some do
    #: not, so a fix that breaks what worked fails.
    cases: tuple[tuple, ...]
    #: What is actually wrong, in plain words.
    cause: str
    #: Misreadings people make, sorted in with the cause.
    decoys: tuple[str, ...]
    #: The general lesson, shown once it is fixed.
    lesson: str
    #: A nudge for the reproduce step, which is where people stall.
    hint: str
    #: Answers worked out by hand, as (arguments, answer). The only
    #: values here that did not come out of the code being checked.
    checks: tuple[tuple[tuple, Any], ...] = field(default_factory=tuple)
    #: For a Dart hunt: each parameter's type and the return type, so the
    #: driver can hand the function a List<String> rather than JSON's
    #: List<dynamic>. See Kata.types.
    types: tuple[str, ...] = ()
    returns: str = ""

    @property
    def lines(self) -> tuple[str, ...]:
        return tuple(self.start.rstrip("\n").split("\n"))

    @property
    def bug_lines(self) -> tuple[int, ...]:
        """The 1-based lines the fix changes. Computed, never typed."""
        before = self.start.rstrip("\n").split("\n")
        after = self.fixed.rstrip("\n").split("\n")
        return tuple(
            i + 1 for i, (a, b) in enumerate(zip(before, after)) if a != b
        )

    @property
    def choices(self) -> tuple[str, ...]:
        """Every explanation on offer, in an order that says nothing."""
        return tuple(sorted({self.cause, *self.decoys}))

    @property
    def signature(self) -> str:
        if self.language == "dart":
            typed = ", ".join(f"{k} {p}" for k, p in zip(self.types, self.params))
            return f"{self.returns} {self.name}({typed})"
        return f"{self.name}({', '.join(self.params)})"

    def answer(self, args) -> Any:
        return self.solve(*copy.deepcopy(tuple(args)))


# ── Reading an input someone typed ───────────────────────────


class BadInput(ValueError):
    """An input that cannot be used, with a message saying why."""


#: Long enough for any reasonable input, short enough that the box is
#: not a way to hand the runner something enormous.
MAX_INPUT = 400


def parse_args(text: str, arity: int, name: str = "it") -> tuple:
    """The arguments someone typed, as values.

    Written the way you would write the call: `100`, `[1, 2, 3]`,
    `"flour", true`. JSON first, because that is what JavaScript
    literals mostly are; then Python literals, so `True`, `None` and
    single quotes work as well. Never evaluated as code - literal_eval
    only reads literals.
    """
    text = (text or "").strip()
    if not text:
        raise BadInput("Type the arguments to call it with.")
    if len(text) > MAX_INPUT:
        raise BadInput("That input is longer than it needs to be.")
    try:
        values = json.loads(f"[{text}]")
    except json.JSONDecodeError:
        try:
            values = ast.literal_eval(f"[{text}]")
        except (ValueError, SyntaxError):
            raise BadInput(
                "That is not something a call can take - write it the way "
                "you would in the code, like 100 or [1, 2] or \"text\"."
            ) from None
    if len(values) != arity:
        raise BadInput(
            f"{name} takes {arity} argument{'s' if arity != 1 else ''}, "
            f"and that is {len(values)}."
        )
    return tuple(values)


# ── Running the broken program on one input ──────────────────


@dataclass(frozen=True)
class Attempt:
    """What one call did, next to what it should have done."""

    reproduced: bool
    got: Any = None
    want: Any = None
    error: str = ""
    #: The call changed its argument when it should not have.
    changed: bool = False


def _as_kata(hunt: Hunt, cases: tuple[tuple, ...]):
    """The hunt as a kata, so the kata driver and marker can run it.

    Nothing new executes code here: this goes through the same driver,
    runner, timeout and comparison rules as every kata, which are
    already tested.
    """
    from code_coach.kata import Kata

    return Kata(
        id=hunt.id, name=hunt.name, brief="", params=hunt.params,
        cases=cases, solve=hunt.solve, language=hunt.language,
        types=hunt.types, returns=hunt.returns,
    )


def run_cases(hunt: Hunt, code: str, cases: tuple[tuple, ...] | None = None):
    """Run some code against cases, judged by the oracle."""
    from code_coach.engine import run_code
    from code_coach.kata import harness, judge

    kata = _as_kata(hunt, cases if cases is not None else hunt.cases)
    out, err, exit_code = run_code(harness(kata, code), language=hunt.language)
    return judge(kata, out, err, exit_code)


def try_input(hunt: Hunt, args: tuple) -> Attempt:
    """Call the broken program with one input and say if the bug shows.

    The oracle is asked first. An input it cannot handle - a word where
    a number goes - is not a reproduction of anything, and saying "you
    found the bug" for it would be the app lying.
    """
    try:
        want = hunt.answer(args)
    except Exception:
        raise BadInput(
            f"{hunt.name} was never meant to take that - try the kind of "
            f"value the report is about."
        ) from None
    outcome = run_cases(hunt, hunt.start, (args,))
    if outcome.broke or not outcome.results:
        return Attempt(reproduced=False, want=want, error=outcome.broke)
    result = outcome.results[0]
    return Attempt(
        reproduced=not result.passed,
        got=result.got,
        want=want,
        error=result.error,
        changed=result.changed,
    )


# ── The collection ───────────────────────────────────────────


def hunts(family: str | None = None) -> tuple[Hunt, ...]:
    """Every hunt, or one family's, easiest first."""
    everything = _all()
    if family is not None:
        everything = tuple(h for h in everything if h.family == family)
    return tuple(sorted(everything, key=lambda h: h.level))


def hunt_families() -> tuple[str, ...]:
    """In the order the content lists them, not sorted by level.

    Sorting by level interleaves the families, so the first family would
    be whichever happened to hold the easiest hunt - the katas were
    bitten by exactly that.
    """
    seen: list[str] = []
    for h in _all():
        if h.family not in seen:
            seen.append(h.family)
    return tuple(seen)


def _all() -> tuple[Hunt, ...]:
    """Every hunt in content order: Python, JavaScript, then Dart."""
    from code_coach.bughunt.content import JAVASCRIPT_HUNTS, PYTHON_HUNTS
    from code_coach.bughunt.content2 import JAVASCRIPT_HUNTS_2, PYTHON_HUNTS_2
    from code_coach.bughunt.content3 import DART_HUNTS

    return (PYTHON_HUNTS + PYTHON_HUNTS_2 + JAVASCRIPT_HUNTS
            + JAVASCRIPT_HUNTS_2 + DART_HUNTS)


def hunt(hunt_id: str) -> Hunt | None:
    return next((h for h in hunts() if h.id == hunt_id), None)
