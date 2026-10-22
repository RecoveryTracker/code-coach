"""One glossary entry, and the two helpers a terms module writes entries with.

An entry teaches ONE word in ONE language. A word that means the same in Python
and JavaScript (a loop, a variable) is written once with `both(...)`, which makes
the two entries from a shared definition plus a per-language example, so the
rules and the example can never leak from one language into the other.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field
from typing import Any

LANGUAGES = ("python", "javascript")


@dataclass(frozen=True)
class Entry:
    id: str
    #: How the word is shown ("Falsy", "None", "f-string").
    term: str
    language: str
    #: One or two plain sentences; no word in it that the glossary does not also define.
    definition: str
    #: Short bullet rules. They are claims about the language, held to the real one by tests.
    rules: tuple[str, ...] = ()
    #: A small program in this language that prints example_output (run for real by the tests).
    example: str = ""
    example_output: str = ""
    #: Ids of related entries in the same language.
    see_also: tuple[str, ...] = ()
    #: Other spellings someone might look the word up by ("==", "casting").
    aka: tuple[str, ...] = ()
    #: Regexes (MULTILINE) run on the code with comments and string contents blanked out.
    #: A pattern starting "raw:" is run on the code as written instead.
    detect: tuple[str, ...] = ()
    #: Higher shows first when a snippet matches more words than there is room for.
    priority: int = 50
    #: Truthy and Falsy only: source expressions that count as false / as true. The tests
    #: run every one through bool() / Boolean().
    counts_false: tuple[str, ...] = ()
    counts_true: tuple[str, ...] = ()
    #: Free grouping label for the UI (unused so far; kept so adding one is not a schema change).
    group: str = field(default="", compare=False)

    def keys(self) -> set[str]:
        """Every lower-case spelling this entry answers to."""
        return {self.id.lower(), self.term.lower(), *(a.lower() for a in self.aka)}


def code(text: str) -> str:
    """A multi-line example written indented in the source, without the margin."""
    return textwrap.dedent(text).strip("\n")


def _as_tuple(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    return tuple(value or ())


_FIELDS = {
    "term", "definition", "rules", "example", "out", "see", "aka", "detect", "priority",
    "counts_false", "counts_true",
}


def entry(language: str, id: str, term: str, definition: str, **kw: Any) -> Entry:
    """Build one entry. `out` is the example's printed output, `see` the related ids."""
    unknown = set(kw) - _FIELDS
    if unknown:
        raise TypeError(f"unknown glossary field(s) {sorted(unknown)} in {id!r}")
    example = kw.get("example", "")
    return Entry(
        id=id,
        term=term,
        language=language,
        definition=" ".join(definition.split()),
        rules=tuple(" ".join(r.split()) for r in _as_tuple(kw.get("rules"))),
        example=code(example) if example else "",
        example_output=(kw.get("out") or "").strip("\n"),
        see_also=_as_tuple(kw.get("see")),
        aka=_as_tuple(kw.get("aka")),
        detect=_as_tuple(kw.get("detect")),
        priority=int(kw.get("priority", 50)),
        counts_false=_as_tuple(kw.get("counts_false")),
        counts_true=_as_tuple(kw.get("counts_true")),
    )


def py(id: str, term: str, definition: str, **kw: Any) -> list[Entry]:
    return [entry("python", id, term, definition, **kw)]


def js(id: str, term: str, definition: str, **kw: Any) -> list[Entry]:
    return [entry("javascript", id, term, definition, **kw)]


def both(
    id: str,
    term: str,
    definition: str,
    *,
    python: dict[str, Any] | None = None,
    javascript: dict[str, Any] | None = None,
    **common: Any,
) -> list[Entry]:
    """The same word in both languages. `common` is shared; each language dict overrides it
    (and must hold at least its own `example` and `out`). Leave a language's dict as None
    to write the word for only the other one."""
    out: list[Entry] = []
    for language, own in (("python", python), ("javascript", javascript)):
        if own is None:
            continue
        merged = {**common, **own}
        out.append(
            entry(language, id, merged.pop("term", term), merged.pop("definition", definition), **merged)
        )
    return out
