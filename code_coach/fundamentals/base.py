"""Fundamentals drills for any language.

Python's Foundations/Decisions/Loops are generated — combinatorial pools with
a seeded RNG, which gives endless variety but has to be written afresh for
every language. That doesn't scale to six.

So other languages declare their material instead: an ordered list of snippets
per class, each tagged with the chunk size it belongs to. Adding a language is
writing a data file, not a generator. The material is finite and ordered, so a
window wraps when you reach the end — the same shape as the LeetCode bank.

A language is welcome to start with only `foundations` filled in; the classes
it doesn't define simply aren't offered.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

# The three fundamentals classes, in learning order. Ids match Python's so
# navigation and progress keep working across languages.
CLASS_IDS: tuple[str, ...] = ("foundations", "decisions", "loops")


@dataclass(frozen=True)
class Snippet:
    """One thing to type, and why it's worth typing."""

    code: str
    tip: str
    # Smallest chunk size that includes it: 1–2 single lines, 3 two-liners,
    # 4 blocks, 5 whole functions.
    level: int = 1


@dataclass(frozen=True)
class FundamentalsClass:
    id: str
    name: str
    description: str
    snippets: tuple[Snippet, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FundamentalsBank:
    language: str
    classes: tuple[FundamentalsClass, ...] = field(default_factory=tuple)

    def get(self, class_id: str) -> FundamentalsClass | None:
        return next((c for c in self.classes if c.id == class_id), None)


# language id → bank. Registered on import below.
_BANKS: dict[str, FundamentalsBank] = {}


def register(bank: FundamentalsBank) -> None:
    _BANKS[bank.language] = bank


def bank_for(language: str) -> FundamentalsBank | None:
    return _BANKS.get(language)


def has_fundamentals(language: str, class_id: str) -> bool:
    """True when this language actually has material for that class.

    Python's live in the generators, not here — it always has them.
    """
    if language == "python":
        return class_id in CLASS_IDS
    bank = _BANKS.get(language)
    return bool(bank and bank.get(class_id) and bank.get(class_id).snippets)


def classes_with_material(language: str) -> tuple[str, ...]:
    return tuple(c for c in CLASS_IDS if has_fundamentals(language, c))


def snippets_for(language: str, class_id: str, level: int) -> list[Snippet]:
    """Material for one class at one chunk size, in teaching order.

    Levels are cumulative: a level-4 window includes the shorter snippets too,
    because dropping the basics as you turn the size up makes for a strange
    jump. Level 5 shows only whole functions, which is the point of level 5.
    """
    bank = _BANKS.get(language)
    if bank is None:
        return []
    found = bank.get(class_id)
    if found is None:
        return []
    level = max(1, min(5, level))
    if level >= 5:
        whole = [s for s in found.snippets if s.level >= 5]
        return whole or list(found.snippets)
    return [s for s in found.snippets if s.level <= level]


def specs_for(language: str, class_id: str, *, batch: int, count: int, level: int):
    """The `batch`-th window of this class's material, wrapping at the end."""
    from code_coach.dictation.bank import KEYBOARD_TIPS, LineSpec, make_block_check

    snippets = snippets_for(language, class_id, level)
    if not snippets:
        return []

    start = (batch * count) % len(snippets)
    out = []
    for i in range(count):
        position = start + i
        snippet = snippets[position % len(snippets)]
        # Content digest, not hash() — str hashing is salted per process, and a
        # restart must not orphan the waypoint ids saved in progress.
        digest = hashlib.sha1(snippet.code.encode("utf-8")).hexdigest()[:8]
        out.append(
            LineSpec(
                id=f"fn-{language}-{position}-{digest}",
                example=snippet.code,
                check=make_block_check(snippet.code),
                tip=snippet.tip,
                keyboard_tip=KEYBOARD_TIPS[position % len(KEYBOARD_TIPS)],
                family=f"{language}-{class_id}",
                level=snippet.level,
            )
        )
    return out


def material_count(language: str, class_id: str, level: int) -> int:
    return len(snippets_for(language, class_id, level))


def _register_all() -> None:
    """Import the per-language banks for their side effects."""
    from code_coach.fundamentals import (  # noqa: F401
        c,
        cpp,
        dart,
        javascript,
        rust,
        sql,
        typescript,
    )


_register_all()
