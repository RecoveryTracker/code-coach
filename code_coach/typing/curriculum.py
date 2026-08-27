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

    The check now lives beside the fallback it guards, in bank.py — this was
    one of three separate copies of it, and copies drift.
    """
    from code_coach.leetcode.bank import has_own_bank

    return has_own_bank(language)


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


# ── Whole blocks ────────────────────────────────────────────
#
# The same material, not split. A line at a time drills the punctuation; a
# whole function drills the shape — where the body sits under the signature,
# which branch belongs to which test, and pressing Enter as part of writing
# code rather than as the end of a sentence.

# Under this it isn't a block, it's a line with a friend.
MIN_BLOCK_LINES = 2
# Over this it's an endurance test. The longest solutions in the bank run past
# twenty lines, and a mistake on line nineteen is a bad trade for a drill.
MAX_BLOCK_LINES = 14


def _block_ok(code: str) -> bool:
    lines = [ln for ln in code.splitlines() if ln.strip()]
    return MIN_BLOCK_LINES <= len(lines) <= MAX_BLOCK_LINES


def _tidy(code: str) -> str:
    """Trailing whitespace can't be seen, so it can't be typed on purpose."""
    return "\n".join(ln.rstrip() for ln in code.strip("\n").splitlines())


def fundamentals_blocks(language: str) -> list[Passage]:
    """Whole declared snippets — level 5 is the whole-function chunk size."""
    from code_coach.fundamentals.base import CLASS_IDS, snippets_for

    out: list[Passage] = []
    for class_id in CLASS_IDS:
        for snippet in snippets_for(language, class_id, 5):
            code = _tidy(snippet.code)
            if _block_ok(code):
                out.append(Passage(code, snippet.tip))
    return out


def leetcode_blocks(language: str) -> list[Passage]:
    """Whole solutions, plus the node classes the patterns are built on."""
    from code_coach.leetcode.bank import patterns_for_language

    if not _has_own_leetcode(language):
        return []
    out: list[Passage] = []
    for pattern in patterns_for_language(language):
        for block in pattern.preamble:
            code = _tidy(block)
            if _block_ok(code):
                out.append(Passage(code, f"{pattern.name} setup"))
        for problem in pattern.problems:
            code = _tidy(problem.code)
            if _block_ok(code):
                out.append(Passage(code, f"#{problem.number} {problem.title}"))
    return out


def language_name(language: str) -> str:
    from code_coach.languages import get_language

    return get_language(language).name


def code_blocks_for(language: str) -> tuple[Passage, ...]:
    """This language's whole-block pool, simplest material first.

    Every note names the language. A single line of Python and a single line
    of Dart can be told apart at a glance; ten lines of either can look alike
    enough that you have to work it out, and working out what you are looking
    at is not the exercise.
    """
    name = language_name(language)
    seen: set[str] = set()
    out: list[Passage] = []
    for passage in (*fundamentals_blocks(language), *leetcode_blocks(language)):
        if passage.text in seen:
            continue
        seen.add(passage.text)
        out.append(Passage(passage.text, f"{name} · {passage.source}"))
    return tuple(out)
