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
    #: For a practice whose screen follows the language picker: which
    #: language each item is in, as {id: language}.
    #:
    #: Without it the queue deals items in every language, and a screen
    #: that only shows the chosen language then opens on something else
    #: - the card says one hunt and you land on another. With it, the
    #: queue deals only what that screen will actually show. Left as
    #: None, a practice is dealt whole, which is how the rest still work.
    #: An item written in several languages maps to all of them.
    languages: Callable[[], dict[str, str | tuple[str, ...]]] | None = None


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


def _hunt_languages() -> dict[str, str]:
    from code_coach.bughunt import hunts

    return {h.id: h.language for h in hunts()}


def _regex_items() -> list[tuple[str, str]]:
    from code_coach.regex import tasks

    return [(t.id, t.title) for t in tasks()]


def _puzzle_items() -> list[tuple[str, str]]:
    from code_coach.puzzles import puzzles

    return [(p.id, p.title) for p in puzzles()]


def _puzzle_languages() -> dict[str, tuple[str, ...]]:
    from code_coach.puzzles import NAMES, puzzles, supports

    return {p.id: tuple(lang for lang in NAMES if supports(lang)) for p in puzzles()}


def _ticket_items() -> list[tuple[str, str]]:
    from code_coach.tickets import projects

    return [(t.id, t.title) for p in projects() for t in p.tickets]


def _flutter_items() -> list[tuple[str, str]]:
    from code_coach.flutter import questions

    return [(q.id, q.name) for q in questions()]


def _case_items() -> list[tuple[str, str]]:
    from code_coach.casefiles import cases

    return [(c.id, c.title) for c in cases()]


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
           "bughunt_counts", "bughunt_last", languages=_hunt_languages),
    Source("puzzles", "Puzzles", _puzzle_items,
           "puzzle_counts", "puzzle_last", languages=_puzzle_languages),
    Source("regex", "Regex", _regex_items, "regex_counts", "regex_last"),
    Source("cases", "Case files", _case_items, "case_counts", "case_last"),
    Source("flutter", "Flutter", _flutter_items, "flutter_counts", "flutter_last"),
    Source("tickets", "Tickets", _ticket_items, "ticket_counts", "ticket_last"),
    Source("magnets", "Magnets", _magnet_items,
           "magnet_counts", "magnet_last"),
    Source("predict", "Predict", _predict_items,
           "predict_counts", "predict_last"),
    Source("styles", "HTML & CSS", _css_items, "css_counts", "css_last"),
    Source("drills", "Type it", _drill_items, "markup_counts", "markup_last"),
)


def dealable(source: Source, progress) -> list[tuple[str, str]]:
    """The items this practice can deal to this person, as (id, name).

    All of them, unless the practice follows the language picker, in
    which case only the ones in the chosen language. One definition,
    used by the queue and by anything that needs to know what the queue
    could hand out - so the two cannot disagree about it.
    """
    items = source.items()
    if source.languages is None:
        return items
    language_of = source.languages()
    chosen = getattr(progress, "language", "") or "python"
    return [(i, n) for i, n in items if _speaks(language_of.get(i), chosen)]


def _speaks(entry, chosen: str) -> bool:
    """Whether an item is in the chosen language - one, or one of several."""
    if entry is None:
        return False
    return chosen == entry if isinstance(entry, str) else chosen in entry


def _coldest(source: Source, progress) -> list[dict]:
    """One practice's items, coldest first.

    Fewest goes, and of those the longest ago. Never having been done
    sorts first because its date is empty, which is before every real
    one — the same trick each screen uses.
    """
    counts = getattr(progress, source.counts_attr)()
    last = getattr(progress, source.last_attr)()
    items = dealable(source, progress)
    rows = [
        {
            "practice": source.key,
            "label": source.label,
            "id": item_id,
            "name": name,
            "done": counts.get(item_id, 0),
            "last": last.get(item_id, ""),
        }
        for item_id, name in items
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


# ── History ──────────────────────────────────────────────────
#
# The queue answers "what next". History answers the questions a queue
# cannot: how much of each practice have I touched at all, and which of
# the things I did are old enough to be worth doing again. It is built
# from the same counts and dates, so it cannot disagree with the queue.

#: The refresh gaps a person can pick, in days.
REFRESH_CHOICES = (3, 7, 14, 30)


def _age_days(stamp: str, now) -> float | None:
    """How many days ago an ISO timestamp was, or None if there is none."""
    from datetime import datetime, timezone

    if not stamp:
        return None
    try:
        when = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return (now - when).total_seconds() / 86400


def history(progress, refresh_days: int = 7, now=None, recent_size: int = 20) -> dict:
    """What has been done, what has not, and what is due for a refresh.

    Due means done at least once and last done more than refresh_days
    ago - oldest first, because the longest-unvisited is the most likely
    to have faded. Recent is everything done, newest first, across every
    practice: a log of the last few sessions.
    """
    from datetime import datetime, timezone

    now = now or datetime.now(timezone.utc)
    practices = []
    recent = []
    for source in SOURCES:
        rows = _coldest(source, progress)
        tried = [r for r in rows if r["done"]]
        due = []
        for row in tried:
            age = _age_days(row["last"], now)
            if age is not None:
                recent.append({**row, "days_ago": round(age, 1)})
                if age > refresh_days:
                    due.append({**row, "days_ago": round(age, 1)})
        due.sort(key=lambda r: -r["days_ago"])
        practices.append({
            "key": source.key,
            "label": source.label,
            "total": len(rows),
            "tried": len(tried),
            "due": due,
        })
    recent.sort(key=lambda r: r["days_ago"])
    return {
        "refresh_days": refresh_days,
        "practices": practices,
        "recent": recent[:recent_size],
    }
