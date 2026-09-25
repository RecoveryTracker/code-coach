"""Code magnets: the lines of a working program, shuffled.

Head First's puzzle, which is a good one and which none of the other
modes here cover. The katas ask you to write a function from nothing.
The typing drills ask you to copy a shape until your hands know it.
This asks something in between and oddly harder: here are the exact
lines of a program that works, in the wrong order — put them back.

It drills the thing that is otherwise only learned by having it go
wrong. Which line has to come before which, where the closing brace
belongs, that a `const` cannot be used above where it is declared, that
the callback goes inside the call and not after it. You cannot fudge
any of that by ordering lines approximately, and you cannot get it by
typing faster.

How it is marked
----------------
By running it. Not by comparing your order with the reference order —
that would fail arrangements that are perfectly correct, and there are
always several: two independent statements can go either way round, a
function declaration can sit above or below its caller. A marker that
called those wrong would be teaching you to guess at the author's
preference instead of at what the language does.

So the lines you arranged are run, and what they print is compared
with what the program should print. Any arrangement that produces the
right output is right, because it is.

Where the expected output comes from
------------------------------------
Typed out by a person, and checked by the suite against what the engine
actually prints — the same way round as the predict puzzles, and the
opposite way round from the katas. Here the engine is the authority on
what a program prints, so the hand-written copy is what catches a
puzzle that has quietly stopped demonstrating what its note claims.
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Magnet:
    """One program, to be put back together."""

    id: str
    name: str
    family: str
    #: The finished program. One line per magnet, so the lines are the
    #: pieces and nothing has to be split by hand later.
    code: str
    #: Exactly what it prints, typed out by a person. The suite runs the
    #: program and holds this to what came back.
    expect: str
    #: What the shape is for, and what ordering it wrong teaches. Shown
    #: with the puzzle — this is not a memory test either.
    note: str
    language: str = "javascript"
    #: 1 to 5: how much the order matters, easiest first in a family.
    level: int = 2
    #: What the program does, in stages: (label, how many lines).
    #:
    #: These are subgoal labels, and they are the best-evidenced thing
    #: in this file. Students given subgoal labels on a Parsons problem
    #: do measurably better than students asked to invent their own or
    #: given none — better immediately, better a week later, and better
    #: on a task they have not seen. So they are given rather than
    #: asked for.
    #:
    #: A count rather than a list of line numbers, because that makes a
    #: stage a run of consecutive lines by construction. The program is
    #: its stages in order, so a stage scattered through the file would
    #: be one the board could not put back together.
    plan: tuple[tuple[str, int], ...] = ()

    @property
    def pieces(self) -> tuple[str, ...]:
        """The magnets, in the order that works."""
        return tuple(self.code.split("\n"))

    @property
    def stages(self) -> tuple[tuple[str, tuple[str, ...]], ...]:
        """Each label with the lines it covers, in order."""
        out: list[tuple[str, tuple[str, ...]]] = []
        lines = self.pieces
        at = 0
        for label, count in self.plan:
            out.append((label, lines[at:at + count]))
            at += count
        return tuple(out)

    @property
    def labels(self) -> tuple[str, ...]:
        """Just the labels — what the board shows.

        The counts stay behind. Telling somebody a stage holds three
        lines answers a good part of the question for them, and a label
        is meant to be a scaffold rather than an answer.
        """
        return tuple(label for label, _ in self.plan)

    def shuffled(self, seed: int | None = None) -> tuple[str, ...]:
        """The magnets, jumbled.

        A fresh jumble per go by default. The point of the mode is a
        dozen goes at one puzzle, and the same jumble every time turns
        the second go into remembering where the pieces were rather
        than working out where they belong.

        It never hands back the finished order. On a two-line puzzle
        there is nowhere else to go, so those are left alone rather
        than looped over forever.
        """
        pieces = list(self.pieces)
        if len(pieces) < 3:
            return tuple(pieces)
        rng = random.Random(seed)
        for _ in range(20):
            rng.shuffle(pieces)
            if tuple(pieces) != self.pieces:
                return tuple(pieces)
        return tuple(reversed(self.pieces))


def _m(**kw) -> Magnet:
    return Magnet(**kw)


def magnets(family: str | None = None) -> tuple[Magnet, ...]:
    """Every puzzle, or one family's, easiest first within the family."""
    from code_coach.magnets.content import ARRAYS, ASYNC, FUNCTIONS, OBJECTS
    from code_coach.engine import if_dart
    from code_coach.magnets.content_dart import DART_MAGNETS

    everything = (*FUNCTIONS, *ARRAYS, *OBJECTS, *ASYNC, *if_dart(DART_MAGNETS))
    if family is not None:
        everything = tuple(m for m in everything if m.family == family)
    return tuple(sorted(everything, key=lambda m: m.level))


def magnet_families() -> tuple[str, ...]:
    from code_coach.magnets.content import ARRAYS, ASYNC, FUNCTIONS, OBJECTS
    from code_coach.engine import if_dart
    from code_coach.magnets.content_dart import DART_MAGNETS

    seen: list[str] = []
    for m in (*FUNCTIONS, *ARRAYS, *OBJECTS, *ASYNC, *if_dart(DART_MAGNETS)):
        if m.family not in seen:
            seen.append(m.family)
    return tuple(seen)


def magnet(magnet_id: str) -> Magnet | None:
    return next((m for m in magnets() if m.id == magnet_id), None)


def same_pieces(magnet: Magnet, lines: list[str]) -> bool:
    """Whether these are that puzzle's magnets and nothing else.

    The exercise is arranging the pieces, so the check is that the
    pieces are the ones given — same lines, same number of each. Sorted
    rather than set-compared, because a puzzle with two identical
    closing braces must still come back with two.
    """
    return sorted(line.rstrip() for line in lines) == sorted(
        piece.rstrip() for piece in magnet.pieces
    )
