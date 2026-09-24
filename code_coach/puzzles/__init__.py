"""Two-part puzzles: solve part one, and part two changes the rules.

The shape is Advent of Code's, and the second part is the point of it.
Part one is a function against some input. Solving it unlocks part two,
which asks something different of the same input - the peak instead of
the final count, the chain inside the list instead of whether the whole
list is one - and your part-one code is still in the box. So part two is
a change to code you wrote yourself, which is the Change it idea turned
on your own work: the helper you wrote for part one is either reusable
or it is not, and finding out which is the lesson.

Every puzzle can be written in Python or JavaScript and follows the
language picker. The oracle is Python either way, for the reason the
katas give: the answers are numbers, strings, lists and booleans, which
mean the same thing in both.

The rules the suite holds every puzzle to
-----------------------------------------
* Each part's answer passes that part's cases, in both languages, run
  through the same driver as a kata.
* The oracle agrees with answers worked out by hand, on an awkward input.
* Part two really is a new question: the part-one answer, renamed to
  part two's function, fails part two. Without that, part two is part
  one again under another name.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

PARTS = (1, 2)

#: What the functions are called, per language. Fixed across puzzles so
#: part two's box can say "add part_two" without the name ever changing.
NAMES = {
    "python": ("part_one", "part_two"),
    "javascript": ("partOne", "partTwo"),
}


@dataclass(frozen=True)
class Part:
    """One half of a puzzle."""

    #: What this part asks, in a sentence or two.
    brief: str
    params: tuple[str, ...]
    cases: tuple[tuple, ...]
    #: The answer, as a Python oracle.
    solve: Callable[..., Any]
    #: A worked answer in each language, run by the suite.
    py_answer: str
    js_answer: str
    #: A worked example, shown with the brief.
    example: str
    #: Answers worked out by hand, as (arguments, answer).
    checks: tuple[tuple[tuple, Any], ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Puzzle:
    id: str
    title: str
    level: int
    #: The situation, before either part - read once, used by both.
    story: str
    one: Part
    two: Part
    #: What part two taught, shown once it is solved.
    lesson: str

    def part(self, n: int) -> Part:
        return self.one if n == 1 else self.two


def function_name(language: str, n: int) -> str:
    return NAMES.get(language, NAMES["python"])[n - 1]


def answer_for(puzzle: Puzzle, n: int, language: str) -> str:
    part = puzzle.part(n)
    return (part.js_answer if language == "javascript" else part.py_answer).strip()


def as_kata(puzzle: Puzzle, n: int, language: str):
    """One part as a kata, so the kata driver and marker can run it.

    Nothing new executes code: the same driver, runner, timeout and
    comparison rules as every kata, which are already tested.
    """
    from code_coach.kata import Kata

    part = puzzle.part(n)
    return Kata(
        id=f"{puzzle.id}-{n}", name=function_name(language, n),
        brief=part.brief, params=part.params, cases=part.cases,
        solve=part.solve, language=language,
    )


def run_part(puzzle: Puzzle, n: int, code: str, language: str):
    from code_coach.engine import run_code
    from code_coach.kata import harness, judge

    kata = as_kata(puzzle, n, language)
    out, err, exit_code = run_code(harness(kata, code), language=language)
    return judge(kata, out, err, exit_code)


def supports(language: str) -> bool:
    """Whether puzzles can be written in this language.

    Only the two they have answers in. Anything else is told so by the
    screen, the same way Bug Hunt does, rather than being quietly handed
    a different language than the one picked at the top.
    """
    return language in NAMES


def puzzles() -> tuple[Puzzle, ...]:
    from code_coach.puzzles.content import PUZZLES

    return PUZZLES


def puzzle(puzzle_id: str) -> Puzzle | None:
    return next((p for p in puzzles() if p.id == puzzle_id), None)
