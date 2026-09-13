"""What a predict-the-output puzzle is.

Its own module so that the Python snippets and the JavaScript ones can
both describe themselves without either importing the other. Keeping the
record beside one of the two sets would make the other one's import a
cycle, and the usual fix for that — an import at the bottom of the file —
works by accident of ordering rather than by design.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Puzzle:
    """A snippet, what it prints, and why that surprises people."""

    id: str
    name: str
    family: str
    #: The whole program. Short enough to hold in your head at once.
    code: str
    #: Exactly what it prints, typed out by a person.
    expect: str
    #: What is going on, shown after you have answered either way. A
    #: wrong guess with no explanation teaches only that you were wrong.
    why: str
    #: Which language the snippet is in.
    #:
    #: The mode was Python only to begin with and the traps are the
    #: reason it is not any more: JavaScript has more of them, they bite
    #: harder, and the order an async program prints in is something you
    #: cannot work out by reading carefully — you have to know the rule.
    language: str = "python"
    #: How surprising it is, 1 to 5, and the order a family is read in.
    #:
    #: Same arrangement as the katas and the same reason: there is no
    #: measure of this to compute, so the suite checks that the ranking
    #: was done rather than that it is right. Here it means how far the
    #: answer is from what a careful reader would guess — not how long
    #: the snippet is.
    level: int = 2


def _p(**kw) -> Puzzle:
    return Puzzle(**kw)
