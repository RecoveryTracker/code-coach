"""Cheat sheets: the lines worth having in your head, laid out to be scanned.

Not a lesson and not a drill. This is the desk mat — the thing you glance at
while writing, and which you stop needing because you have looked at it enough
times. So it is dense, it is ordered most-used first, and the notes are as
short as they can be while still saying something.

The first section of every sheet is the handful of lines you write in the
first minute of any file. What follows widens out from there.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Entry:
    """One line worth knowing, and the shortest useful thing to say about it."""

    code: str
    note: str = ""


@dataclass(frozen=True)
class Section:
    """A group of related lines. The order of these is the order of use."""

    name: str
    blurb: str
    entries: tuple[Entry, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Sheet:
    language: str
    sections: tuple[Section, ...] = field(default_factory=tuple)


_SHEETS: dict[str, Sheet] = {}


def register(sheet: Sheet) -> None:
    _SHEETS[sheet.language] = sheet


def sheet_for(language: str) -> Sheet | None:
    return _SHEETS.get(language)


def languages_with_sheets() -> tuple[str, ...]:
    return tuple(sorted(_SHEETS))


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


def _register_all() -> None:
    """Import the per-language sheets for their side effects."""
    from code_coach.reference import (  # noqa: F401
        javascript,
        python,
        typescript,
    )


_register_all()
