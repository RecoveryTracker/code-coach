"""Read the CSS, say what the browser computes.

The same question the predict mode asks about Python and JavaScript,
asked about the cascade — because that is where CSS is actually learned.
Writing CSS until it looks right teaches you which declarations you have
tried. Being asked which of two rules wins, guessing, and being wrong
teaches you the rule that decided it.

Where the answers come from
---------------------------
Nothing here is run at marking time. There is no browser engine in this
project and adding a half-built one would be worse than none: jsdom's
computed styles get inheritance and shorthands wrong often enough that a
green suite would mean less than no suite.

So the oracle is a real browser, used once, on purpose:
`tools/verify_css.py` writes a page holding every quiz in this file. You
open it and it renders each one in an isolated iframe, asks
getComputedStyle for the property in question, and compares what
Chromium says with what is recorded here. A disagreement is printed, in
red, with both values.

That makes the expected values evidence rather than assertion, and the
evidence can be re-gathered in ten seconds whenever a quiz is added or
changed. What the pytest suite can check is that no quiz escapes the
page: `test_css.py` asserts every id in this file appears in the
generated page, so a quiz cannot be added and quietly skipped.

Why multiple choice
-------------------
A computed colour is `rgb(0, 128, 0)` and a computed width is `240px`.
Nobody types those from memory, and a free-text box would be marking
spelling rather than understanding. The choices are the misconceptions:
each wrong one is what you get if you believe a particular wrong thing
about the cascade, and the explanation says which.

The choices are sorted before they are shown, so their order carries no
information about which is right.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StyleQuiz:
    """One page, one question about what the browser worked out."""

    id: str
    name: str
    family: str
    #: The markup, as it goes inside <body>. No html/head/body tags.
    html: str
    #: The stylesheet, as it goes inside <style>.
    css: str
    #: Which element is being measured. Must match exactly one element —
    #: the verifier fails the quiz rather than measuring the first, since
    #: a selector that matches two is a quiz whose answer depends on
    #: which one you meant.
    target: str
    #: What to read off the element.
    #:
    #: Normally a computed property, spelled as CSS spells it. But
    #: computed style is not always the interesting number, and twice it
    #: is actively misleading: `width: 300px` on a span and `z-index: 5`
    #: on a static div both compute to what you wrote while having no
    #: effect at all. So `rect.width` and `rect.height` are also
    #: allowed, and read getBoundingClientRect instead - the space the
    #: element actually takes on the page, which is the number those
    #: questions are about.
    prop: str
    #: What Chromium computes, copied from the verifier's output.
    expect: str
    #: What else it could plausibly be. Each is a belief about the
    #: cascade that someone holds; `why` says which belief gives which.
    #: The right answer is not listed here — it is added and the whole
    #: lot sorted, so nothing about the order gives it away.
    distractors: tuple[str, ...]
    #: Shown after the answer, either way.
    why: str
    #: 1 to 5: how far the answer is from what a careful reader guesses.
    level: int = 2

    @property
    def choices(self) -> tuple[str, ...]:
        """Everything offered, in an order that says nothing."""
        return tuple(sorted({self.expect, *self.distractors}))

    def page(self) -> str:
        """The quiz as a standalone document, for the verifier and for
        Watch it run. One string, so that what the student sees rendered
        and what the verifier measured cannot drift apart."""
        return (
            "<!doctype html>\n"
            "<html><head><meta charset=\"utf-8\"><style>\n"
            + self.css
            + "\n</style></head>\n<body>\n"
            + self.html
            + "\n</body></html>"
        )


def _q(**kw) -> StyleQuiz:
    return StyleQuiz(**kw)


def quizzes(family: str | None = None) -> tuple[StyleQuiz, ...]:
    """Every quiz, or one family's, easiest first within the family.

    The imports are inside the function because the content modules
    import StyleQuiz from here. Same shape as the katas: the record is
    defined at the top of the package and the content is pulled in at
    call time, so neither file has to know about the other's ordering.
    """
    from code_coach.css.content import BOX, CASCADE
    from code_coach.css.content2 import INHERIT, LAYOUT

    everything = (*CASCADE, *BOX, *INHERIT, *LAYOUT)
    if family is not None:
        everything = tuple(q for q in everything if q.family == family)
    return tuple(sorted(everything, key=lambda q: q.level))


def css_families() -> tuple[str, ...]:
    """The family names, in the order they are worth working through."""
    seen: list[str] = []
    from code_coach.css.content import BOX, CASCADE
    from code_coach.css.content2 import INHERIT, LAYOUT

    for q in (*CASCADE, *BOX, *INHERIT, *LAYOUT):
        if q.family not in seen:
            seen.append(q.family)
    return tuple(seen)


def quiz(quiz_id: str) -> StyleQuiz | None:
    return next((q for q in quizzes() if q.id == quiz_id), None)
