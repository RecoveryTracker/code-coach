"""Personal bests for the typing drills.

Kept in its own file next to the progress store rather than inside it. The
progress file tracks a curriculum position and is migrated when the curriculum
changes; these are just scores, and losing a score because a lesson was
renumbered would be a poor trade.

One record per section-and-mode pair, because that's the unit that's
comparable: a wpm on Home Row Words and a wpm on Coding Punctuation are not
the same measurement, and putting them in one table would only invite the
wrong comparison.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_PATH = Path.home() / ".code_coach" / "typing_records.json"

# Below this many keystrokes a run is too short to mean anything — a couple of
# lucky keys would otherwise sit at the top of the board forever. Kept low on
# purpose: only finished runs are submitted, and some drills are legitimately
# short (a Bottom Row sweep is seven keys), so a high floor would lock those
# out of their own record permanently.
MIN_KEYSTROKES = 5


@dataclass
class Record:
    section: str
    mode: str
    best_wpm: int = 0
    best_accuracy: int = 0
    # Lower is better, so 0 means "nothing recorded yet" rather than "perfect".
    best_reaction_ms: int = 0
    best_streak: int = 0
    runs: int = 0
    total_keys: int = 0
    last_wpm: int = 0
    last_accuracy: int = 0
    updated: str = ""


@dataclass
class Improvement:
    """What, if anything, this run beat. Drives the "new best" callout."""

    wpm: bool = False
    accuracy: bool = False
    reaction: bool = False
    streak: bool = False

    @property
    def any(self) -> bool:
        return self.wpm or self.accuracy or self.reaction or self.streak


@dataclass
class RecordBook:
    entries: dict[str, Record] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"entries": {k: asdict(v) for k, v in self.entries.items()}}

    @classmethod
    def from_dict(cls, raw: dict) -> RecordBook:
        entries: dict[str, Record] = {}
        for key, value in (raw.get("entries") or {}).items():
            if not isinstance(value, dict):
                continue
            # Ignore fields this version doesn't know, so an older file and a
            # newer one can coexist without either losing data.
            known = {f: value[f] for f in Record.__annotations__ if f in value}
            try:
                entries[key] = Record(**known)
            except TypeError:
                continue
        return cls(entries=entries)


def _key(section: str, mode: str) -> str:
    return f"{section}:{mode}"


class RecordStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_PATH

    def load(self) -> RecordBook:
        if not self.path.exists():
            return RecordBook()
        try:
            return RecordBook.from_dict(
                json.loads(self.path.read_text(encoding="utf-8"))
            )
        except (OSError, json.JSONDecodeError):
            # A corrupt scores file shouldn't stop you typing.
            return RecordBook()

    def save(self, book: RecordBook) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(book.to_dict(), indent=2, sort_keys=True) + "\n"
        self.path.write_text(payload, encoding="utf-8")

    def submit(
        self,
        *,
        section: str,
        mode: str,
        wpm: int,
        accuracy: int,
        reaction_ms: int,
        streak: int,
        keystrokes: int,
        when: str = "",
    ) -> tuple[Record, Improvement]:
        """Fold one finished run into the book, and say what it beat."""
        book = self.load()
        key = _key(section, mode)
        record = book.entries.get(key) or Record(section=section, mode=mode)

        record.runs += 1
        record.total_keys += max(0, keystrokes)
        record.last_wpm = wpm
        record.last_accuracy = accuracy
        record.updated = when

        improvement = Improvement()
        # A run too short to mean anything still counts as a run — it just
        # can't set a record.
        if keystrokes >= MIN_KEYSTROKES:
            if wpm > record.best_wpm:
                record.best_wpm = wpm
                improvement.wpm = True
            if accuracy > record.best_accuracy:
                record.best_accuracy = accuracy
                improvement.accuracy = True
            if reaction_ms > 0 and (
                record.best_reaction_ms == 0 or reaction_ms < record.best_reaction_ms
            ):
                record.best_reaction_ms = reaction_ms
                improvement.reaction = True
            if streak > record.best_streak:
                record.best_streak = streak
                improvement.streak = True

        book.entries[key] = record
        self.save(book)
        return record, improvement

    def all_records(self) -> list[Record]:
        """Every recorded pair, best first — the board."""
        return sorted(
            self.load().entries.values(),
            key=lambda r: (-r.best_wpm, r.section, r.mode),
        )
