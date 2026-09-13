"""Type the markup, and watch what you typed render.

The quizzes next door ask what the browser makes of a page. This asks
you to write the page, and it is the half that puts it in the hands.

Everything else in the app can mark you by running your code and
comparing what it printed. HTML and CSS print nothing, and there is no
browser engine here to ask, so a drill that tried to judge "is this
markup correct" would be judging with an opinion. This does not try.
The reference is a known-good document, you type it, and the check is
character for character. That is the same bargain the workbook's
type-along pages make, and it is honest: the only claim being made is
that what you typed matches the thing in front of you.

What makes it worth doing anyway is the render. The document you typed
goes into an iframe as you type it, so a missing quote or an unclosed
tag is not a message about a missing quote - it is the page going
wrong in front of you, which is how you learn what that mistake looks
like. The browser doing the rendering is the one already on screen, so
this needs nothing the app does not have.

What you type, and what gets rendered
------------------------------------
The shape of a page - doctype, html, head, charset, title, body - is a
thing you should be able to write from memory, so the structure family
makes you write it: those drills are whole documents.

Everywhere else it would be twelve lines of skeleton in front of the
four lines that are the point, typed again on every one of a dozen
goes. Those drills carry a wrapper instead: a known-good document with
the drill's place marked in it. The wrapper is shown beside the box,
greyed, so you can see what your piece sits inside - it is not a
mystery, it is just not what you are practising this minute.

Either way the thing that renders is the whole document, because half
a document renders as nothing much and the render is the point.

They are short. The point is a dozen goes at one of them, not one go
at a long one.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Elements with no closing tag. The suite checks that every other tag
#: a drill opens is closed, and without this list it would demand
#: </meta> and </img>.
VOID = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


@dataclass(frozen=True)
class Drill:
    """One short document to type, and why it is worth typing."""

    id: str
    name: str
    family: str
    #: The document, exactly as it should be typed. A trailing newline
    #: is not part of it — trailing whitespace is invisible, and a drill
    #: you cannot pass because of a character you cannot see teaches you
    #: to distrust the marker.
    code: str
    #: One or two sentences: what this shape is for, and the mistake it
    #: is usually written with. Shown beside the drill, not after it —
    #: you are copying this one, not being tested on it.
    note: str
    #: A document with `{{drill}}` where what you type goes, for the
    #: drills that are a piece of a page rather than a whole one. Empty
    #: when the drill is itself the document.
    wrapper: str = ""
    #: 1 to 5, easiest first within a family.
    level: int = 2

    @property
    def lines(self) -> int:
        return len(self.code.splitlines())

    def document(self, typed: str | None = None) -> str:
        """The whole page, for rendering.

        Takes what the person actually typed, so the iframe shows their
        version rather than the right answer — a preview of the
        reference would be a preview of somebody else's work, and the
        whole value here is watching your own mistake render.
        """
        piece = self.code if typed is None else typed
        if not self.wrapper:
            return piece
        # Straight in, keeping the piece's own indentation. The drills
        # are written already indented to the depth they sit at, so the
        # placeholder is flush left and re-indenting here would add it
        # twice. An earlier version did, and the rendered source came
        # out with its first line stripped and the rest doubly indented.
        return self.wrapper.replace("{{drill}}", piece)


def _d(**kw) -> Drill:
    return Drill(**kw)


def tidy(text: str) -> str:
    """What both sides of the comparison are put through.

    Line endings and trailing spaces are not the exercise. A drill
    failed because the editor left a space at the end of a line, or
    because Windows wrote \\r\\n, would be teaching typing-adjacent
    superstition rather than markup. Indentation inside a line is kept,
    because indentation is half of what makes markup readable and it is
    a real part of what you are practising.
    """
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


def drills(family: str | None = None) -> tuple[Drill, ...]:
    """Every drill, or one family's, easiest first within the family."""
    from code_coach.markup.content import FORMS, LAYOUT, STRUCTURE, STYLING

    everything = (*STRUCTURE, *FORMS, *LAYOUT, *STYLING)
    if family is not None:
        everything = tuple(d for d in everything if d.family == family)
    return tuple(sorted(everything, key=lambda d: d.level))


def drill_families() -> tuple[str, ...]:
    """The family names, in the order they are worth working through."""
    from code_coach.markup.content import FORMS, LAYOUT, STRUCTURE, STYLING

    seen: list[str] = []
    for d in (*STRUCTURE, *FORMS, *LAYOUT, *STYLING):
        if d.family not in seen:
            seen.append(d.family)
    return tuple(seen)


def drill(drill_id: str) -> Drill | None:
    return next((d for d in drills() if d.id == drill_id), None)
