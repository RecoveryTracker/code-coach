"""The glossary: the WORDS a learner meets while reading code, taught where they meet them.

"Explain my code" says what each line does; it never said what *falsy* or *scope*
or *precedence* mean, so a learner could ask forever and never learn the word.
This package is that vocabulary - plain definitions, the exact rules, a small
example whose output is verified - and `find_words` picks the few that matter for
a snippet (see CLAUDE.md, "Glossary").

    terms_*.py   data: each module has `TERMS`, a list of `Entry` (use `both`, `py`, `js`
                 from entry.py). A module is found BY NAME, so a new theme is a new file
                 and a new word is one more line in a list - nothing else to register.
    contexts.py  words a screen always teaches (the Brain Drills activities).
    __init__.py  the loader, `find_words`, `lookup`, `words_for_context`.

Every example is RUN by tests/test_glossary.py with the real interpreter and must print
exactly `example_output`, and every falsy/truthy list is run through bool()/Boolean():
the glossary must never teach something false.
"""

from __future__ import annotations

import importlib
import pkgutil
import re
from typing import Any, Iterable

from .contexts import CONTEXTS, concepts_for
from .entry import LANGUAGES, Entry, all3, both, code, dart, entry, js, py

__all__ = [
    "CONTEXTS", "Entry", "LANGUAGES", "LOAD_ERRORS", "all3", "all_entries", "both", "code", "dart", "entry",
    "find_words", "js", "language_for", "lookup", "payload", "py", "resolve", "words_for_context",
]

#: Languages the app can read that borrow another one's glossary. The farm's own language
#: is Python's syntax; TypeScript is JavaScript with types. Dart is a glossary language of its own
#: (and Flutter is Dart, so its words live in the Dart glossary).
ALIASES = {"tfwr": "python", "typescript": "javascript"}

#: A module that fails to import is skipped and recorded here (the tests fail on it).
LOAD_ERRORS: dict[str, str] = {}

#: Longest code `find_words` reads; the rest is ignored (a glossary is never worth a stall).
MAX_CODE = 20_000


def language_for(language_id: str | None) -> str:
    """The glossary language for an app language id: "" when there is none."""
    lang = (language_id or "").strip().lower()
    lang = ALIASES.get(lang, lang)
    return lang if lang in LANGUAGES else ""


# ── Loading ─────────────────────────────────────────────────────────────

_cache: dict[str, Any] = {}


def _load() -> dict[str, dict[str, Entry]]:
    """{language: {id: Entry}}, from every terms_* module, in module then list order."""
    if "by_lang" in _cache:
        return _cache["by_lang"]
    by_lang: dict[str, dict[str, Entry]] = {lang: {} for lang in LANGUAGES}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        if not info.name.startswith("terms_"):
            continue
        try:
            module = importlib.import_module(f"{__name__}.{info.name}")
            for item in module.TERMS:
                bucket = by_lang.get(item.language)
                if bucket is None:
                    raise ValueError(f"{item.id}: unknown language {item.language!r}")
                if item.id in bucket:
                    raise ValueError(f"duplicate {item.language} id {item.id!r}")
                bucket[item.id] = item
        except Exception as exc:  # a bad content file must not take the app down
            LOAD_ERRORS[info.name] = f"{type(exc).__name__}: {exc}"
    _cache["by_lang"] = by_lang
    _cache["compiled"] = {}
    return by_lang


def all_entries(language: str) -> list[Entry]:
    """Every entry for a language (or the app language id's glossary), in file order."""
    return list(_load().get(language_for(language), {}).values())


def lookup(language: str, term: str) -> Entry | None:
    """One entry by id, display term or alternate spelling (case does not matter)."""
    key = term.strip().lower() if isinstance(term, str) else ""
    if not key:
        return None
    entries = _load().get(language_for(language), {})
    if key in entries:
        return entries[key]
    for item in entries.values():
        if key in item.keys():
            return item
    return None


def _norm(text: str) -> str:
    """A spelling with the differences that do not matter removed: case, hyphens, spaces, dots and
    underscores ('type coercion' == 'type-coercion', 'tostring' == 'toString'). A spelling made only of
    symbols ('===', '?.') is kept as it is, lower-cased."""
    raw = (text or "").strip().lower()
    squeezed = re.sub(r"[^a-z0-9]", "", raw)
    return squeezed or raw


def _spellings(word: str) -> list[str]:
    """The keys a plain word may be looked up by: itself, then without a plural 's'/'es', then with an 's'."""
    key = _norm(word)
    out = [key]
    if len(key) > 3 and key.endswith("es"):
        out.append(key[:-2])
    if len(key) > 2 and key.endswith("s"):
        out.append(key[:-1])
    if key.isalnum():
        out.append(key + "s")
    return out


def _index(language: str) -> dict[str, Entry]:
    """{normalised spelling: entry} for a language. An id beats a display term, which beats an aka."""
    cache: dict[str, dict[str, Entry]] = _cache.setdefault("index", {})
    if language not in cache:
        entries = _load().get(language, {})
        table: dict[str, Entry] = {}
        for tier in (lambda e: (e.id,), lambda e: (e.term,), lambda e: e.aka):
            for item in entries.values():
                for spelling in tier(item):
                    table.setdefault(_norm(spelling), item)
        cache[language] = table
    return cache[language]


def resolve(language: str, word: str) -> Entry | None:
    """The entry a plain word names in a language, tolerantly: `lookup` first (exact id, term or aka), then
    ignoring case, hyphens, spaces and a plural ('Type Coercion', 'closures', 'toString'). None when the
    language has no such word - which is normal: 'range' is Python's, 'nonlocal' is not JavaScript's."""
    exact = lookup(language, word)
    if exact is not None:
        return exact
    lang = language_for(language)
    if not lang or not isinstance(word, str) or not word.strip():
        return None
    table = _index(lang)
    for key in _spellings(word):
        if key in table:
            return table[key]
    return None


def context_words(context_id: str, language: str) -> list[Entry]:
    """One context's entries for a language: the hand-kept ids of the original seven activities, or (for
    any other Brain Drills activity) its `concepts` resolved one by one. Order kept, no duplicates, a word the
    language does not have is skipped."""
    lang = language_for(language)
    entries = _load().get(lang, {})
    cid = (context_id or "").strip().lower()
    out: list[Entry] = []
    if cid in CONTEXTS:
        found = (entries.get(term_id) for term_id in CONTEXTS[cid])
    else:
        found = (resolve(lang, word) for word in concepts_for(cid))
    for item in found:
        if item is not None and all(item.id != seen.id for seen in out):
            out.append(item)
    return out


def words_for_context(context: str | Iterable[str] | None, language: str) -> list[Entry]:
    """The entries a context always teaches, in the context's order, no duplicates."""
    out: list[Entry] = []
    seen: set[str] = set()
    ids = [context] if isinstance(context, str) else list(context or ())
    for cid in ids:
        for item in context_words(cid, language):
            if item.id not in seen:
                seen.add(item.id)
                out.append(item)
    return out


# ── Reading code ────────────────────────────────────────────────────────

_PY_BLANK = re.compile(
    r"""
    (?P<comment>\#[^\n]*)
  | (?P<triple>(?P<tp>[rRbBfFuU]{0,2})(?:\"\"\"[\s\S]*?(?:\"\"\"|\Z)|'''[\s\S]*?(?:'''|\Z)))
  | (?P<str>(?P<sp>[rRbBfFuU]{0,2})(?:"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?))
    """,
    re.X,
)

_JS_BLANK = re.compile(
    r"""
    (?P<comment>//[^\n]*|/\*[\s\S]*?(?:\*/|\Z))
  | (?P<tpl>`(?:\\.|[^`\\])*`?)
  | (?P<str>"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)
    """,
    re.X,
)


# Dart: // and /* */ comments, raw strings r'..' / r".." (no escapes), triple-quoted strings, and ordinary
# strings. `${...}` inside a string is blanked with the rest of it.
_DART_BLANK = re.compile(
    r"""
    (?P<comment>//[^\n]*|/\*[\s\S]*?(?:\*/|\Z))
  | (?P<triple>r?(?:'''[\s\S]*?(?:'''|\Z)|\"\"\"[\s\S]*?(?:\"\"\"|\Z)))
  | (?P<raw>r(?:"[^"\n]*"?|'[^'\n]*'?))
  | (?P<str>"(?:\\.|[^"\\\n])*"?|'(?:\\.|[^'\\\n])*'?)
    """,
    re.X,
)


def _blank_dart(m: re.Match[str]) -> str:
    if m.group("comment") is not None:
        return "\n" * m.group("comment").count("\n")
    if m.group("triple") is not None:
        return '""' + "\n" * m.group("triple").count("\n")
    return '""'


def _blank_py(m: re.Match[str]) -> str:
    if m.group("comment") is not None:
        return ""
    if m.group("triple") is not None:
        return (m.group("tp") or "") + '""' + "\n" * m.group("triple").count("\n")
    return (m.group("sp") or "") + '""'


def _blank_js(m: re.Match[str]) -> str:
    if m.group("comment") is not None:
        return "\n" * m.group("comment").count("\n")
    if m.group("tpl") is not None:
        return "``" + "\n" * m.group("tpl").count("\n")
    return '""'


def blank_code(source: str, language: str) -> str:
    """The code with comments removed and the inside of every string emptied (quotes stay), so a
    word in a string or a comment is never mistaken for code."""
    if language == "python":
        return _PY_BLANK.sub(_blank_py, source)
    if language == "dart":
        return _DART_BLANK.sub(_blank_dart, source)
    return _JS_BLANK.sub(_blank_js, source)


def _compiled(entry_: Entry) -> list[tuple[bool, re.Pattern[str]]]:
    cache: dict[tuple[str, str], list[tuple[bool, re.Pattern[str]]]] = _cache.setdefault("compiled", {})
    key = (entry_.language, entry_.id)
    if key not in cache:
        patterns = []
        for text in entry_.detect:
            raw = text.startswith("raw:")
            patterns.append((raw, re.compile(text[4:] if raw else text, re.M)))
        cache[key] = patterns
    return cache[key]


def find_words(code: str, language: str, context: str | Iterable[str] | None = None, limit: int = 8) -> list[Entry]:
    """The glossary entries that matter for a snippet.

    Context words first (all of them, in the context's order), then the words the code's own
    text shows, by priority and then by where they first appear; never more than `limit`, no
    word twice. An unknown language, nothing matching, empty or garbage code: an empty list or
    just the context's words - never an error.
    """
    lang = language_for(language)
    entries = _load().get(lang)
    if not entries or limit <= 0:
        return []
    out = words_for_context(context, lang)[:limit]
    if len(out) >= limit or not isinstance(code, str) or not code.strip():
        return out
    source = code[:MAX_CODE]
    blanked = blank_code(source, lang)
    seen = {e.id for e in out}
    found: list[tuple[int, int, int, Entry]] = []
    for order, item in enumerate(entries.values()):
        if item.id in seen or not item.detect:
            continue
        first = -1
        for raw, pattern in _compiled(item):
            m = pattern.search(source if raw else blanked)
            if m and (first < 0 or m.start() < first):
                first = m.start()
        if first >= 0:
            found.append((-item.priority, first, order, item))
    found.sort(key=lambda row: row[:3])
    out.extend(row[3] for row in found[: limit - len(out)])
    return out


def payload(item: Entry) -> dict[str, Any]:
    """An entry as the API sends it. `see_also` carries each related word's display term, so a
    chip can be labelled without a second request."""
    entries = _load().get(item.language, {})
    return {
        "id": item.id,
        "term": item.term,
        "language": item.language,
        "definition": item.definition,
        "rules": list(item.rules),
        "example": item.example,
        "example_output": item.example_output,
        "see_also": [{"id": s, "term": entries[s].term} for s in item.see_also if s in entries],
        "counts_false": list(item.counts_false),
        "counts_true": list(item.counts_true),
    }
