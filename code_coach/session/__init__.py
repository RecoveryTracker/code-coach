"""What to practise next, across every mode at once.

There are eleven screens now. Each one already knows which of its own
items has had fewest goes and longest ago, which is the right rule and
does not help with the question a person actually has at the start of a
session, which is "what should I be doing". Answering that eleven times
by hand is a decision cost paid before any practice happens, and the
practice is the point.

So this builds one queue. It asks every practice for its coldest items —
fewest goes, and of those the longest ago, the same rule each screen
uses on its own — and deals them out round-robin.

Round-robin rather than strictly coldest-first, and that is the one
judgement call here. A queue sorted purely by need would hand over
twenty katas on the first day, because on a fresh profile everything is
equally cold and the sort falls back to whatever order the sources are
listed in. Alternating between kinds keeps a session varied, which is
better practice and much likelier to be finished.

Nothing is scheduled or spaced. This is not a review system pretending
to know when you will forget; it is a queue of what you have touched
least, which is a claim it can actually support.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Source:
    """One practice, and how to ask it what it has."""

    #: What the browser calls it, for sending you to the right screen.
    key: str
    #: What it is called on screen.
    label: str
    #: Every item, as (id, name).
    items: Callable[[], list[tuple[str, str]]]
    #: The progress fields holding its counts and dates.
    counts_attr: str
    last_attr: str


def _kata_items() -> list[tuple[str, str]]:
    from code_coach.kata import katas

    return [(k.id, k.name) for k in katas()]


def _predict_items() -> list[tuple[str, str]]:
    from code_coach.kata.predict import puzzles

    return [(p.id, p.name) for p in puzzles()]


def _css_items() -> list[tuple[str, str]]:
    from code_coach.css import quizzes

    return [(q.id, q.name) for q in quizzes()]


def _drill_items() -> list[tuple[str, str]]:
    from code_coach.markup import drills

    return [(d.id, d.name) for d in drills()]


def _magnet_items() -> list[tuple[str, str]]:
    from code_coach.magnets import magnets

    return [(m.id, m.name) for m in magnets()]


def _error_items() -> list[tuple[str, str]]:
    from code_coach.errors import crashes

    return [(c.id, c.name) for c in crashes()]


def _hunt_items() -> list[tuple[str, str]]:
    from code_coach.bughunt import hunts

    return [(h.id, h.title) for h in hunts()]


def _trace_items() -> list[tuple[str, str]]:
    from code_coach.trace import traces

    return [(t.id, t.name) for t in traces()]


#: Every practice the queue can send you to.
#:
#: The workbook and the LeetCode workspace are deliberately absent. They
#: track a position rather than a set of items — which page you are on,
#: which lesson — so "one item from there" is not a thing they can be
#: asked for, and dropping you at a page mid-sequence would be worse
#: than leaving them out.
SOURCES: tuple[Source, ...] = (
    Source("forms", "Forms", _kata_items, "kata_counts", "kata_last"),
    Source("trace", "Trace", _trace_items, "trace_counts", "trace_last"),
    Source("errors", "Errors", _error_items, "error_counts", "error_last"),
    Source("bughunt", "Bug Hunt", _hunt_items,
           "bughunt_counts", "bughunt_last"),
    Source("magnets", "Magnets", _magnet_items,
           "magnet_counts", "magnet_last"),
    Source("predict", "Predict", _predict_items,
           "predict_counts", "predict_last"),
    Source("styles", "HTML & CSS", _css_items, "css_counts", "css_last"),
    Source("drills", "Type it", _drill_items, "markup_counts", "markup_last"),
)


def _coldest(source: Source, progress) -> list[dict]:
    """One practice's items, coldest first.

    Fewest goes, and of those the longest ago. Never having been done
    sorts first because its date is empty, which is before every real
    one — the same trick each screen uses.
    """
    counts = getattr(progress, source.counts_attr)()
    last = getattr(progress, source.last_attr)()
    rows = [
        {
            "practice": source.key,
            "label": source.label,
            "id": item_id,
            "name": name,
            "done": counts.get(item_id, 0),
            "last": last.get(item_id, ""),
        }
        for item_id, name in source.items()
    ]
    rows.sort(key=lambda r: (r["done"], r["last"]))
    return rows


def queue(progress, size: int = 20) -> list[dict]:
    """The next `size` things to do, dealt round-robin across practices.

    A practice that runs out simply stops being dealt from; the others
    carry on, so a short mode does not cap the length of a session.
    """
    piles = [_coldest(source, progress) for source in SOURCES]
    out: list[dict] = []
    depth = 0
    while len(out) < size and any(depth < len(p) for p in piles):
        for pile in piles:
            if depth < len(pile):
                out.append(pile[depth])
                if len(out) == size:
                    break
        depth += 1
    return out
