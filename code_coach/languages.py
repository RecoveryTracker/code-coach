"""Which languages Code Coach can teach.

Scaffolding. Python is the only one that actually works today; the registry
exists so adding another is a matter of filling in the pieces listed on each
entry rather than hunting for every place the language is assumed.

What a language needs before `available` can flip to True:

  runner      execute a file and capture stdout/stderr (engine.run_file)
  checks      structural checks for build lessons — Python uses its `ast`
              module, so another language needs its own parser or a
              text-based fallback
  bank        the solutions themselves, per pattern
  tracer      step-by-step values for "Watch it run" (optional; the rest of
              the app works without it)

The verbatim type-along and the diff messages are language-agnostic — they
compare text and indentation, so they come for free.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Language:
    id: str
    name: str
    # Monaco's identifier for syntax highlighting.
    monaco: str
    extension: str
    # False until the pieces below actually exist.
    available: bool = False
    # What's still missing, shown in the picker so it isn't a mystery.
    note: str = ""
    # Which of the four pieces are done — keeps the UI honest as work lands.
    ready: tuple[str, ...] = field(default_factory=tuple)


LANGUAGES: tuple[Language, ...] = (
    Language(
        id="python",
        name="Python",
        monaco="python",
        extension="py",
        available=True,
        ready=("runner", "checks", "bank", "tracer"),
    ),
    Language(
        id="dart",
        name="Dart (Flutter)",
        monaco="dart",
        extension="dart",
        available=False,
        note=(
            "Not yet — needs a Dart SDK runner, structural checks, and the "
            "solutions written in Dart. The typing drills themselves are "
            "language-agnostic and will work as soon as those land."
        ),
    ),
)

DEFAULT_LANGUAGE = "python"


def get_language(language_id: str | None) -> Language:
    """The named language, falling back to Python rather than failing —
    a stored id from a future version shouldn't brick the app."""
    for lang in LANGUAGES:
        if lang.id == language_id:
            return lang
    return LANGUAGES[0]


def is_available(language_id: str | None) -> bool:
    return get_language(language_id).available


def languages_payload() -> list[dict]:
    return [
        {
            "id": lang.id,
            "name": lang.name,
            "monaco": lang.monaco,
            "extension": lang.extension,
            "available": lang.available,
            "note": lang.note,
            "ready": list(lang.ready),
        }
        for lang in LANGUAGES
    ]
