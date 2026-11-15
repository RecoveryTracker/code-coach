"""The acceptance corpus for the Dart / C / SQL explainers: the code the app itself shows.

Three sources per language: every Brain Drills prompt (several seeds), every Gotchas card of that language, and
the Workbook's reference solutions in that language where the Workbook has them. Used by tests/test_explain_*.py.
"""

from __future__ import annotations

from functools import lru_cache

SEEDS = (1, 2, 3)


@lru_cache(maxsize=None)
def brain(language: str) -> tuple[tuple[str, str], ...]:
    """(label, code) for every Brain Drills prompt in the language, over several seeds."""
    from code_coach import brain as B

    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for act in B.activities_in(language):
        for seed in SEEDS:
            try:
                items = B.make_round(act.id, seed, language)
            except Exception:  # a pack that cannot make a round is the pack tests' business
                continue
            for item in items:
                if item.prompt not in seen:
                    seen.add(item.prompt)
                    out.append((act.id, item.prompt))
    return tuple(out)


@lru_cache(maxsize=None)
def gotchas(language: str) -> tuple[tuple[str, str], ...]:
    from code_coach import gotchas as G

    return tuple((it.id, it.code) for it in G.DECKS.get(language, ()))


@lru_cache(maxsize=None)
def workbook(language: str) -> tuple[tuple[str, str], ...]:
    """The Workbook's solutions in the language (only those it can write)."""
    from code_coach import workbook as W
    from code_coach.workbook import emit

    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    try:
        pages = W.pages(language)
    except Exception:
        return ()
    for page in pages:
        for ex in page.exercises:
            try:
                code = ex.answer(language)
            except Exception:
                code = None
            if code and code not in seen:
                seen.add(code)
                out.append((f"{page.id}/{ex.id}", code))
    del emit
    return tuple(out)


def corpora(language: str) -> dict[str, tuple[tuple[str, str], ...]]:
    return {"brain": brain(language), "gotchas": gotchas(language), "workbook": workbook(language)}


# ── shared checks for tests/test_explain_{dart,c,sql}.py ────────────────────

import re  # noqa: E402
from collections import Counter  # noqa: E402

#: A rule sentence's checkable claim: `EXPR` gives `VALUE` (an expression's value) or `printf(...)` prints `OUTPUT`.
CLAIM = re.compile(r"`([^`]+)` (?:gives|prints) `([^`]*)`")


def claims(facts: dict[str, str]) -> list[tuple[str, str, str]]:
    """(fact id, expression, claimed value) for every claim written into a rule sentence."""
    return [(fid, m.group(1), m.group(2)) for fid, text in facts.items() for m in CLAIM.finditer(text)]


def shape(source: str) -> str:
    return re.sub(r"\d+", "N", source.strip())[:70]


def coverage(read_rows, language: str) -> dict[str, tuple[int, int, Counter]]:
    """Per corpus: (non-structural lines, lines that got the fallback, the most common fallback shapes).

    `read_rows(code) -> (rows, n_lines, [fallback line numbers as text])` is each reader's `_read_rows`."""
    out: dict[str, tuple[int, int, Counter]] = {}
    for name, items in corpora(language).items():
        total = bad = 0
        shapes: Counter = Counter()
        for _label, code in items:
            _rows, n, badlines = read_rows(code)
            total += n
            bad += len(badlines)
            raw = code.split("\n")
            for b in badlines:
                shapes[shape(raw[int(b) - 1])] += 1
        out[name] = (total, bad, shapes)
    return out


def assert_coverage(read_rows, language: str, minimum: float = 0.90) -> dict[str, float]:
    got = coverage(read_rows, language)
    problems = []
    numbers = {}
    for name, (total, bad, shapes) in got.items():
        if not total:
            continue
        ratio = (total - bad) / total
        numbers[name] = ratio
        if ratio < minimum:
            top = "\n".join(f"  {n:4d}  {s}" for s, n in shapes.most_common(15))
            problems.append(f"{language} {name}: {ratio:.1%} specific ({bad} of {total} lines fell back); the commonest:\n{top}")
    assert not problems, "\n".join(problems)
    return numbers


JUNK = ["", "   \n\n", "}}}}", "(((", "'unterminated", '"unterminated\nx', "/* open comment", "\x00\x01", "@@@ ### $$$", "a" * 3000,
        "(" * 500, "[" * 400 + "]" * 10, "{ { { {", "int", "var x =", "SELECT", "SELECT * FROM", "CREATE TABLE t(", "INSERT INTO", "for (", "if (x", "class {",
        "printf(", 'printf("%d', "#define", "#include <", "switch (x) { case", "WITH RECURSIVE", "x = (1 +", "é ü 日本語", "'''", "\\", "`", "--", "; ; ;"]


def check_never_raises(explain, extra=()):
    """Junk, empty and half-typed input: always the answer dict, never an exception."""
    for code in list(JUNK) + list(extra):
        r = explain(code, run=False)
        assert isinstance(r, dict) and "summary" in r and isinstance(r["lines"], list), repr(code[:30])


def check_alignment(explain, language: str, per_corpus: int = 400):
    """Every row's `line` and `source` match the code, depths are not negative and rows are in line order."""
    for name, items in corpora(language).items():
        for label, code in items[:per_corpus]:
            r = explain(code, run=False)
            raw = code.split("\n")
            last = 0
            for row in r["lines"]:
                assert 1 <= row["line"] <= len(raw), (name, label, row)
                assert row["source"] == raw[row["line"] - 1].strip(), (name, label, row)
                assert row["depth"] >= 0 and isinstance(row["text"], str) and row["text"].strip(), (name, label, row)
                assert row["line"] >= last, (name, label, "rows out of line order")
                last = row["line"]
