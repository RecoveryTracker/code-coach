"""Slides: passive, watch-only tutorials.

A deck is a short run of slides on one topic (data types, syntax, patterns).
Nothing is asked of the reader and nothing is saved: you watch, or you step
through at your own pace. Every slide's `output` is what its `code` prints,
worked out by hand; tests/test_slides.py runs each program for real and
requires the two to agree (the oracle rule).

Only Python has decks so far, but every deck names its `language`, so another
language is a new `content_*.py` module and a line in `_MODULES`.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module


@dataclass(frozen=True)
class Slide:
    title: str
    text: str
    code: str = ""
    output: str = ""  # exactly what `code` prints, without the final newline
    point: str = ""


@dataclass(frozen=True)
class Deck:
    id: str
    title: str
    language: str
    blurb: str
    slides: tuple[Slide, ...]


#: A deck module that failed to import (or has no DECK): skipped and recorded here, never fatal; the tests fail on it.
LOAD_ERRORS: dict[str, str] = {}


def _discover() -> tuple[Deck, ...]:
    """Every `content_*.py` beside this file that has a `DECK`, found BY NAME (a new deck is a new file, nothing to
    register), in the order of each module's `ORDER` (an int: lower is earlier, beginner decks first; default 100),
    then by file name."""
    import pkgutil

    found: list[tuple[int, str, Deck]] = []
    for info in pkgutil.iter_modules(__path__):
        if not info.name.startswith("content_"):
            continue
        try:
            module = import_module(f"{__name__}.{info.name}")
            found.append((int(getattr(module, "ORDER", 100)), info.name, module.DECK))
        except Exception as e:  # a broken deck is skipped and recorded
            LOAD_ERRORS[info.name] = f"{type(e).__name__}: {e}"
    return tuple(d for _, _, d in sorted(found, key=lambda t: (t[0], t[1])))


DECKS: tuple[Deck, ...] = _discover()


def decks_for(language: str) -> list[Deck]:
    """The decks written for a language (empty for one with none yet)."""
    return [d for d in DECKS if d.language == language]


def deck(deck_id: str) -> Deck | None:
    return next((d for d in DECKS if d.id == deck_id), None)


def list_payload(language: str) -> dict:
    return {
        "language": language,
        "decks": [
            {"id": d.id, "title": d.title, "blurb": d.blurb, "count": len(d.slides)}
            for d in decks_for(language)
        ],
    }


def deck_payload(d: Deck) -> dict:
    """The whole deck, with the colouring rules for its language."""
    from code_coach.gotchas import langs

    syntax = langs.syntax_payload().get(d.language)
    return {
        "id": d.id,
        "title": d.title,
        "language": d.language,
        "blurb": d.blurb,
        "syntax": syntax,
        "slides": [
            {"title": s.title, "text": s.text, "code": s.code, "output": s.output, "point": s.point}
            for s in d.slides
        ],
    }
