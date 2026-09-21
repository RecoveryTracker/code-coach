"""Lines grouped by the shape they share, for drilling one shape at a time.

The request this exists for: "console.log, perhaps with a different
thing like total or whatever else is commonly there — ten times in a
row, with just what gets printed changing. That way I get super fast at
individual lines that are the most common."

That is a real training method and a different one from the rest of the
trainer. Every other drill deliberately varies what comes next, because
recognising an unfamiliar line is its own skill. This one deliberately
does not: the frame stays put and only the payload moves, so the
punctuation stops being a decision and becomes a reflex. Both are worth
doing; they are not substitutes.

Where the variations come from
------------------------------
Real lines out of the curriculum, not lines this module wrote.

Inventing twenty plausible `console.log(...)` calls would have been
quicker and it is the wrong trade. Made-up filler drills made-up
habits: the arguments would be whatever I happened to think of, and the
distribution of what people actually log would be lost. The bank
already holds 1,900 lines of real solutions, so the shapes and their
payloads are both taken from code that was written to do a job.

The cost of that choice is honest and visible: a shape only becomes a
drill once enough real lines share it. Rare shapes are simply not
offered, rather than being padded out.

How a shape is identified
-------------------------
Not by a second set of rules. line_notes.py already classifies a line
by matching one of its rules and producing a fixed English frame with
the line's own names dropped into it - "add X onto the end of Y". That
frame is the shape, so the key is the description with the borrowed
words blanked out again.

Deriving it from the describer rather than restating it is the point.
A hand-written list of shapes would be a second place to edit every
time a rule changes, and this project has been bitten by five of those.
Here a new rule in the describer becomes a new shape for free, and a
rule that changes cannot leave the two disagreeing, because there is
only one of them.
"""

from __future__ import annotations

import re
from collections import defaultdict

from code_coach.typing.line_notes import describe
from code_coach.typing.texts import Passage

#: How many real lines a shape needs before it is worth ten in a row.
#:
#: Under this the drill starts repeating itself within one sitting,
#: which trains recall of those particular lines rather than fluency
#: with the shape - the opposite of the point.
MIN_LINES = 8

#: What a blanked-out payload is written as inside a shape key. Not
#: shown to anyone; keys are internal.
BLANK = "X"

_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _words_in(line: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(line)}


def shape_key(line: str, language: str) -> str | None:
    """The shape of a line, or None when it has no describable shape.

    Two lines get the same key when the describer said the same thing
    about them apart from the names involved.
    """
    described = describe(line, language)
    if not described:
        return None
    borrowed = _words_in(line)
    out: list[str] = []
    for token in described.split():
        word = token.strip(".,;:()[]{}'\"")
        # Blanked when it came out of the line, and when it is not a
        # word at all - an operator or a literal is payload too, so
        # `if a == b` and `if a > b` are one shape rather than two.
        if not word or word.lower() in borrowed or not _WORD.fullmatch(word):
            out.append(BLANK)
        else:
            out.append(word.lower())
    collapsed = re.sub(rf"(?:{BLANK} )+{BLANK}", BLANK, " ".join(out))
    return collapsed.strip()


def shape_label(lines: list[str], language: str) -> str:
    """A name for a shape, taken from the shortest line that has it.

    A real example beats a description of one. "console.log(total);" in
    a menu says what the drill is in a way that "show X" does not, and
    it is the thing you are about to type.
    """
    return min(lines, key=lambda line: (len(line), line))


def group_by_shape(
    passages: tuple[Passage, ...] | list[Passage], language: str
) -> dict[str, list[Passage]]:
    """Every describable line in a pool, bucketed by shape."""
    buckets: dict[str, list[Passage]] = defaultdict(list)
    for passage in passages:
        key = shape_key(passage.text, language)
        if key:
            buckets[key].append(passage)
    return dict(buckets)


def drillable_shapes(
    passages: tuple[Passage, ...] | list[Passage], language: str
) -> list[tuple[str, str, list[Passage]]]:
    """The shapes worth drilling: (key, label, lines), commonest first.

    Commonest first because the whole request was about the lines you
    write most - a shape with two hundred examples is one you will type
    for the rest of your life, and a shape with nine is a curiosity.
    """
    buckets = group_by_shape(passages, language)
    big = [
        (key, shape_label([p.text for p in lines], language), lines)
        for key, lines in buckets.items()
        if len(lines) >= MIN_LINES
    ]
    # Ties broken by label so the menu order cannot change between runs.
    big.sort(key=lambda item: (-len(item[2]), item[1]))
    return big
