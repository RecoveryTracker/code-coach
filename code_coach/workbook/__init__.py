"""The Workbook: pages of small exercises you solve by typing.

The rest of the app is material — lessons to read, solutions to type along
with, problems to study. This is the other half, and it was missing: a page
of the same small task over and over, each one a little different, until you
stop having to think about it.

The model is a maths workbook. A page of addition, then a page of
subtraction, then a page that mixes them. One new idea per page and a dozen
repetitions of it, because the second one is where the learning is and the
tenth is where it stops being effort.

A page is checked by running what you wrote and comparing what it printed. Not
by looking at your code: there are several right ways to print the numbers 1
to 5 and all of them pass. What is checked is the thing the exercise asked
for.

The exercises are language-agnostic — they say what the program must print,
never how — and the reference answers come from `emit`, which knows how to
write each shape in each language.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from code_coach.workbook.emit import solution, supports


@dataclass(frozen=True)
class Exercise:
    """One thing to type. Small enough that the whole answer fits on screen."""

    id: str
    # What to do, in one sentence, with the numbers in it. No syntax.
    prompt: str
    # The shape of the answer, and its arguments. Both feed `emit`.
    shape: str
    args: dict = field(default_factory=dict)

    @property
    def expect(self) -> str:
        """Exactly what the program has to print."""
        return expected_output(self.shape, self.args)

    def answer(self, language: str) -> str | None:
        return solution(language, self.shape, self.args)


@dataclass(frozen=True)
class Page:
    """A dozen of the same shape, in order. One new idea, many repetitions."""

    id: str
    number: int
    name: str
    # The one new thing this page adds to the page before it.
    teaches: str
    # A worked example, shown before the first exercise: the shape once, with
    # the answer, so the page starts by being shown rather than guessed.
    example: str
    exercises: tuple[Exercise, ...] = field(default_factory=tuple)
    # Which languages this page is written for. Empty means all of the ones
    # the workbook covers, which is true of everything up to and including
    # loops. Past that the languages stop agreeing enough for one exercise to
    # be one question.
    languages: tuple[str, ...] = field(default_factory=tuple)
    # Which section of the book this belongs to. The screen groups by it,
    # because a flat list of everything stops being findable somewhere around
    # page forty.
    #
    #   beginner      teaches an idea for the first time
    #   practice      drills an idea already taught, with fresh values
    #   intermediate  builds on all of it, and adds real language features
    #   advanced      later
    tier: str = "beginner"

    def applies_to(self, language: str) -> bool:
        if not self.languages:
            return True
        return language in self.languages


# ── Working out what a program should print ──────────────────
#
# The shapes mean the same thing in every language, so the expected output can
# be worked out once, here, rather than being written down 108 times and
# getting one of them wrong. The suite then runs every reference program in
# every language and checks it against this, which is what makes that claim
# something other than a hope.


def _value(expr: str, names: dict):
    # A closed expression over the exercise's own names. No builtins reachable,
    # because there is no reason for one to be.
    #
    # The early shapes only ever evaluate arithmetic; the later ones also ask
    # about conditions, so the result is not always a number.
    return eval(expr, {"__builtins__": {}}, dict(names))  # noqa: S307


def expected_output(shape: str, args: dict) -> str:
    from code_coach.workbook import (
        emit_more,
        emit_more2,
        emit_more3,
        emit_more4,
        emit_python,
        emit_python2,
        emit_python3,
        emit_python4,
        emit_python5,
        emit_python6,
        emit_python7,
        emit_python8,
        emit_python9,
        emit_python10,
        emit_python11,
        emit_python12,
        emit_python13,
        emit_python14,
        emit_python15,
        emit_python16,
        emit_python17,
        emit_python18,
        emit_python19,
        emit_python20,
        emit_python21,
        emit_js,
        emit_js2,
        emit_js3,
        emit_js4,
        emit_js5,
        emit_js6,
        emit_js7,
        emit_js8,
        emit_ts,
        emit_ts2,
    )

    if emit_ts2.handles(shape):
        return emit_ts2.expected_output(shape, args, _value)
    if emit_ts.handles(shape):
        return emit_ts.expected_output(shape, args, _value)
    if emit_js8.handles(shape):
        return emit_js8.expected_output(shape, args, _value)
    if emit_js7.handles(shape):
        return emit_js7.expected_output(shape, args, _value)
    if emit_js6.handles(shape):
        return emit_js6.expected_output(shape, args, _value)
    if emit_js5.handles(shape):
        return emit_js5.expected_output(shape, args, _value)
    if emit_js4.handles(shape):
        return emit_js4.expected_output(shape, args, _value)
    if emit_js3.handles(shape):
        return emit_js3.expected_output(shape, args, _value)
    if emit_js2.handles(shape):
        return emit_js2.expected_output(shape, args, _value)
    if emit_js.handles(shape):
        return emit_js.expected_output(shape, args, _value)
    if emit_python21.handles(shape):
        return emit_python21.expected_output(shape, args, _value)
    if emit_python20.handles(shape):
        return emit_python20.expected_output(shape, args, _value)
    if emit_python19.handles(shape):
        return emit_python19.expected_output(shape, args, _value)
    if emit_python18.handles(shape):
        return emit_python18.expected_output(shape, args, _value)
    if emit_python17.handles(shape):
        return emit_python17.expected_output(shape, args, _value)
    if emit_python16.handles(shape):
        return emit_python16.expected_output(shape, args, _value)
    if emit_python15.handles(shape):
        return emit_python15.expected_output(shape, args, _value)
    if emit_python14.handles(shape):
        return emit_python14.expected_output(shape, args, _value)
    if emit_python13.handles(shape):
        return emit_python13.expected_output(shape, args, _value)
    if emit_python12.handles(shape):
        return emit_python12.expected_output(shape, args, _value)
    if emit_python11.handles(shape):
        return emit_python11.expected_output(shape, args, _value)
    if emit_python10.handles(shape):
        return emit_python10.expected_output(shape, args, _value)
    if emit_python9.handles(shape):
        return emit_python9.expected_output(shape, args, _value)
    if emit_python8.handles(shape):
        return emit_python8.expected_output(shape, args, _value)
    if emit_python7.handles(shape):
        return emit_python7.expected_output(shape, args, _value)
    if emit_python6.handles(shape):
        return emit_python6.expected_output(shape, args, _value)
    if emit_python5.handles(shape):
        return emit_python5.expected_output(shape, args, _value)
    if emit_python4.handles(shape):
        return emit_python4.expected_output(shape, args, _value)
    if emit_python3.handles(shape):
        return emit_python3.expected_output(shape, args, _value)
    if emit_python2.handles(shape):
        return emit_python2.expected_output(shape, args, _value)
    if emit_python.handles(shape):
        return emit_python.expected_output(shape, args, _value)
    if emit_more4.handles(shape):
        return emit_more4.expected_output(shape, args, _value)
    if emit_more3.handles(shape):
        return emit_more3.expected_output(shape, args, _value)
    if emit_more2.handles(shape):
        return emit_more2.expected_output(shape, args, _value)
    if emit_more.handles(shape):
        return emit_more.expected_output(shape, args, _value)
    a = args
    lines: list[str] = []
    if shape == "print_text":
        lines = [str(a["text"])]
    elif shape == "print_expr":
        lines = [str(_value(a["expr"], {}))]
    elif shape == "let_print":
        lines = [str(_value(a["expr"], {a["name"]: a["value"]}))]
    elif shape == "let2_print":
        names = {a["name1"]: a["value1"], a["name2"]: a["value2"]}
        lines = [str(_value(a["expr"], names))]
    elif shape == "for_print":
        lines = [str(_value(a["expr"], {"i": i})) for i in range(a["count"])]
    elif shape == "for_range_print":
        lines = [
            str(_value(a["expr"], {"i": i}))
            for i in range(a["lo"], a["hi"] + 1)
        ]
    elif shape == "for_sum":
        total = sum(
            _value(a["expr"], {"i": i}) for i in range(a["lo"], a["hi"] + 1)
        )
        lines = [str(total)]
    elif shape == "for_if_print":
        lines = [
            str(_value(a["expr"], {"i": i}))
            for i in range(a["lo"], a["hi"] + 1)
            if _value(a["cond"], {"i": i})
        ]
    elif shape == "for_down":
        lines = [
            str(_value(a["expr"], {"i": i}))
            for i in range(a["hi"], a["lo"] - 1, -1)
        ]
    elif shape == "for_nested":
        lines = [
            str(_value(a["expr"], {"i": i, "j": j}))
            for i in range(1, a["rows"] + 1)
            for j in range(1, a["cols"] + 1)
        ]
    else:
        raise KeyError(shape)
    return "\n".join(lines)


def normalise(output: str) -> str:
    """What counts as the same output.

    Trailing spaces and a missing or extra newline at the end are not the
    exercise. Getting the numbers right is.
    """
    lines = [line.rstrip() for line in output.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def matches(produced: str, expect: str) -> bool:
    return normalise(produced) == normalise(expect)


# ── The pages ────────────────────────────────────────────────


def pages(language: str | None = None) -> tuple[Page, ...]:
    """Every page, or every page this student can actually do.

    The content lives in `content`, not `pages`: importing a submodule binds
    its name on the package, so a `pages` module would shadow this function
    the first time anything imported it.
    """
    from code_coach.workbook.content import PAGES

    if language is None:
        return PAGES
    # No workbook in this language at all — not even the early pages, which
    # still need something that prints a line.
    if not has_workbook(language):
        return ()
    return tuple(p for p in PAGES if p.applies_to(language))


def page(page_id: str) -> Page | None:
    return next((p for p in pages() if p.id == page_id), None)


def exercise(page_id: str, exercise_id: str) -> Exercise | None:
    found = page(page_id)
    if found is None:
        return None
    return next((e for e in found.exercises if e.id == exercise_id), None)


def exercise_count(language: str | None = None) -> int:
    return sum(len(p.exercises) for p in pages(language))


def has_workbook(language: str) -> bool:
    """SQL has no statement that prints a line and no loop, so every shape on
    every page would have to be faked for it. Better to say so."""
    return supports(language)


def payload(language: str) -> list[dict]:
    """Every page, for the Workbook screen.

    The answers are deliberately included: the screen keeps them hidden until
    you ask, the same way the concept answers are, and having them client-side
    means "show me" is instant rather than another round trip.
    """
    out: list[dict] = []
    for p in pages(language):
        out.append(
            {
                "id": p.id,
                "number": p.number,
                "name": p.name,
                "teaches": p.teaches,
                "example": p.example,
                "tier": p.tier,
                "exercises": [
                    {
                        "id": e.id,
                        "prompt": e.prompt,
                        "expect": e.expect,
                        "answer": e.answer(language) or "",
                    }
                    for e in p.exercises
                ],
            }
        )
    return out
