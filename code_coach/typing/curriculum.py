"""Typing material drawn from the curriculum itself.

The trainer's code themes used to be a separate hand-written list per
language. That meant two places to add a language, two places to keep in step,
and a typing trainer that knew nothing about the solutions the curriculum was
teaching you three panes away. It also meant the themes were tiny — twenty-odd
lines each, so a couple of drills exhausted them.

These are the same lines the curriculum serves: the LeetCode solution bank and
the fundamentals snippets, in that language, split into individual lines. Add a
problem to the bank and it turns up here too.

Only lines worth typing survive: a bare `}` or `return []` drills nothing that
the line above it didn't already, and a comment is prose, not code.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage

# Below this a line is punctuation and a keyword — the shape is already in the
# longer lines around it, and a drill of them reads as filler.
MIN_LENGTH = 12

# Structural leftovers. These are what's left when a block ends, and typing
# them teaches nothing about the language.
_SKIP_EXACT = frozenset(
    {
        "}", "};", "})", "});", "}),", "}]", "}];", ")", ");", "),",
        "]", "];", "],", "end", "endif", "else", "else:", "else {",
        "return", "return;", "break", "break;", "continue", "continue;",
        "pass", "}else{", "} else {",
    }
)

_COMMENT_STARTS = ("#", "//", "--", "/*", "*", "///")


def _worth_typing(line: str) -> bool:
    text = line.strip()
    if len(text) < MIN_LENGTH:
        return False
    if text in _SKIP_EXACT:
        return False
    # A comment is prose in a code costume — the prose themes do that better.
    return not text.startswith(_COMMENT_STARTS)


def _lines_of(code: str) -> list[str]:
    return [ln.strip() for ln in code.splitlines() if _worth_typing(ln)]


def _has_own_leetcode(language: str) -> bool:
    """True when this language has its own solution bank.

    `patterns_for_language` falls back to Python's rather than failing, so
    without this check a Rust code theme would hand out Python.
    """
    from code_coach.leetcode.bank import patterns_for_language
    from code_coach.leetcode.problems import PATTERNS as PY_PATTERNS

    if language == "python":
        return True
    return patterns_for_language(language) is not PY_PATTERNS


def fundamentals_lines(language: str) -> list[Passage]:
    """The declared per-language fundamentals, longest chunk size first.

    Python's fundamentals are generated rather than declared, so it has none
    here — its material comes from the solution bank instead.
    """
    from code_coach.fundamentals.base import CLASS_IDS, snippets_for

    out: list[Passage] = []
    for class_id in CLASS_IDS:
        for snippet in snippets_for(language, class_id, 5):
            for line in _lines_of(snippet.code):
                out.append(Passage(line, snippet.tip))
    return out


def leetcode_lines(language: str) -> list[Passage]:
    """Every solution in this language, line by line, in learning order."""
    from code_coach.leetcode.bank import patterns_for_language

    if not _has_own_leetcode(language):
        return []
    out: list[Passage] = []
    for pattern in patterns_for_language(language):
        for block in pattern.preamble:
            for line in _lines_of(block):
                out.append(Passage(line, f"{pattern.name} setup"))
        for problem in pattern.problems:
            note = f"#{problem.number} {problem.title}"
            for line in _lines_of(problem.code):
                out.append(Passage(line, note))
    return out


def code_lines_for(
    language: str, *, curated: tuple[Passage, ...] = ()
) -> tuple[Passage, ...]:
    """This language's typing pool: hand-picked lines first, curriculum after.

    The curated lines lead because they were chosen to teach a shape — the
    curriculum lines are real code, which is a different and larger kind of
    useful. Duplicates keep whichever note came first.
    """
    seen: set[str] = set()
    out: list[Passage] = []
    for passage in (*curated, *fundamentals_lines(language), *leetcode_lines(language)):
        if passage.text in seen:
            continue
        seen.add(passage.text)
        out.append(passage)
    return tuple(out)
