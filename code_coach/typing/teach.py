"""Read it by typing it, then type the thing it describes.

Reading an explanation is easy to do badly — the eye slides over prose it half
recognises. Typing it does not allow that: every word has to be looked at.
And the code lands differently when the sentence explaining it is still in
your fingers from ten seconds ago.

So a teaching pair is prose and then the code it is about, in that order,
always adjacent. The material already exists in four places and none of it is
copied here — a pair is a view over something that is already written and
already checked.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pair:
    """One idea, and the code that shows it."""

    prose: str
    code: str
    source: str

    def __post_init__(self) -> None:  # pragma: no cover - dataclass guard
        pass


# Below this, the prose is a label rather than an explanation and typing it
# teaches nothing. "print anything" is a fine note on a card and a poor thing
# to be asked to copy.
MIN_PROSE = 30


def _clean(text: str) -> str:
    """One line, no double spaces — it is being typed, not laid out."""
    return " ".join(text.split())


def has_own_solutions(language: str) -> bool:
    """True when this language has its own LeetCode bank.

    Delegates to bank.py, where the fallback this protects against lives.
    """
    from code_coach.leetcode.bank import has_own_bank

    return has_own_bank(language)


def solution_pairs(language: str) -> list[Pair]:
    """The idea behind a LeetCode solution, then the solution.

    The best-matched source there is: the idea is one sentence saying what to
    do, and the code is exactly the example of doing it.
    """
    from code_coach.leetcode.bank import patterns_for_language

    if not has_own_solutions(language):
        return []
    out: list[Pair] = []
    for pattern in patterns_for_language(language):
        for problem in pattern.problems:
            prose = _clean(problem.idea)
            if len(prose) >= MIN_PROSE and problem.code.strip():
                out.append(
                    Pair(
                        prose=prose,
                        code=problem.code,
                        source=f"#{problem.number} {problem.title}",
                    )
                )
    return out


def lesson_pairs() -> list[Pair]:
    """A stage of a lesson: what the move is, then the code after it.

    Language-neutral, in the same style as the pattern templates, so these are
    offered whichever language you are practising.
    """
    from code_coach.leetcode.worked import WORKED

    out: list[Pair] = []
    for number, worked in sorted(WORKED.items()):
        for stage in worked.stages:
            prose = _clean(stage.explain)
            if len(prose) >= MIN_PROSE and stage.code.strip():
                out.append(
                    Pair(prose=prose, code=stage.code, source=f"lesson #{number}")
                )
    return out


def fundamentals_pairs(language: str) -> list[Pair]:
    """A declared snippet and the tip that goes with it."""
    from code_coach.fundamentals.base import CLASS_IDS, snippets_for

    out: list[Pair] = []
    seen: set[str] = set()
    for class_id in CLASS_IDS:
        for level in (4, 5):
            for snippet in snippets_for(language, class_id, level):
                prose = _clean(snippet.tip)
                if len(prose) < MIN_PROSE or snippet.code in seen:
                    continue
                seen.add(snippet.code)
                out.append(
                    Pair(prose=prose, code=snippet.code, source=class_id)
                )
    return out


def reference_pairs(language: str) -> list[Pair]:
    """A cheat sheet note, where it is long enough to be worth typing."""
    from code_coach.reference import sheet_for

    sheet = sheet_for(language)
    if sheet is None:
        return []
    out: list[Pair] = []
    seen: set[str] = set()
    for section in sheet.sections:
        for entry in section.entries:
            prose = _clean(entry.note)
            if len(prose) < MIN_PROSE or entry.code in seen:
                continue
            seen.add(entry.code)
            out.append(Pair(prose=prose, code=entry.code, source=section.name))
    return out


def teaching_pairs(language: str) -> list[Pair]:
    """Everything, easiest first.

    Reference notes are a line and a line; fundamentals are a small whole
    program; lesson stages and solutions are the real thing. Ordering them
    that way means a run starts where you can keep up.
    """
    # Python only. The lesson stages are pseudocode in a Python-leaning
    # style — fine to READ in any language, and wrong to type in any other,
    # because `for price in prices[1:]` is not something a Dart student
    # should be practising. Every other language has its own solutions,
    # fundamentals and cheat sheet to draw on instead.
    lessons = lesson_pairs() if language == "python" else []
    pairs = (
        reference_pairs(language)
        + fundamentals_pairs(language)
        + lessons
        + solution_pairs(language)
    )
    # The same code can reach here from two sources — a fundamentals snippet
    # and a reference entry can be the same line. Keep the first.
    seen: set[str] = set()
    out: list[Pair] = []
    for pair in pairs:
        if pair.code in seen:
            continue
        seen.add(pair.code)
        out.append(pair)
    return out
