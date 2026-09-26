"""Read Flutter widget code and say what it does.

Flutter is learned by building screens, and a screen cannot be run
here — there is no window to draw into, and a picture of pixels would
not be a question with one answer anyway. What can be asked is the
part that decides the pixels: which widget sits above which, how many
of something a build makes, what share of a Row each child is given,
which build methods run again after a setState, in what order a State
is told it has been born, updated and thrown away.

Those are all rules, and every one of them can be read off the code
without drawing anything. They are also the rules a beginner guesses
at, because the screen usually looks right either way until the day
it does not.

Where the answers come from
---------------------------
Flutter. Every snippet is a whole Dart library that the suite puts
into a throwaway Flutter project and runs the analyzer over, so a
snippet that stops compiling fails the suite. Most questions also
carry `verify` — the body of a `testWidgets` test that pumps the
snippet and asserts the answer — and the suite runs those with
`flutter test` whenever Flutter is installed. A question whose answer
has stopped being true of the framework fails the suite rather than
marking somebody wrong.

The few without `verify` rest on the documented rule alone, and say so
by having it empty.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WidgetQuestion:
    """One piece of widget code and one question about it."""

    id: str
    name: str
    family: str
    #: 1 to 5, easiest first within a family.
    level: int
    #: A whole Dart library, imports and all, so the analyzer can hold it
    #: to being real Flutter. Kept to 8-30 lines.
    code: str
    question: str
    answer: str
    #: What people say instead. Sorted in with the answer, so the order
    #: gives nothing away.
    decoys: tuple[str, ...]
    #: Shown either way, because being right by luck teaches nothing.
    why: str
    #: The body of a `testWidgets((tester) async { ... })` callback that
    #: pumps the snippet and asserts the answer. The snippet's names are
    #: in scope unprefixed, and so is `answer`, a Dart string holding
    #: this question's answer: the body compares what Flutter did with it,
    #: so a wrong answer fails rather than a wrong fact going unnoticed.
    #: Empty when the answer rests on the rule alone.
    verify: str = ""
    language: str = "dart"

    @property
    def numbered(self) -> tuple[tuple[int, str], ...]:
        return tuple(
            (i + 1, text) for i, text in enumerate(self.code.split("\n"))
        )

    @property
    def choices(self) -> tuple[str, ...]:
        """Everything on offer, in an order that says nothing."""
        return tuple(sorted({self.answer, *self.decoys}))


def _q(**kw) -> WidgetQuestion:
    return WidgetQuestion(**kw)


def _everything() -> tuple[WidgetQuestion, ...]:
    from code_coach.flutter.content import LAYOUT, LIFECYCLE, STATE, TREE

    return (*TREE, *LAYOUT, *STATE, *LIFECYCLE)


def questions(family: str | None = None) -> tuple[WidgetQuestion, ...]:
    """Every one, or one family's, easiest first within the family."""
    everything = _everything()
    if family is not None:
        everything = tuple(q for q in everything if q.family == family)
    return tuple(sorted(everything, key=lambda q: q.level))


def families() -> tuple[str, ...]:
    seen: list[str] = []
    for q in _everything():
        if q.family not in seen:
            seen.append(q.family)
    return tuple(seen)


def question(question_id: str) -> WidgetQuestion | None:
    return next((q for q in questions() if q.id == question_id), None)
