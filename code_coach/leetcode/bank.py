"""
Turn LeetCode solutions into Code Coach exercises.

Three lesson shapes per pattern:

  Lesson 1  Type-along (endless)  — verbatim, difficulty 1–5 (line → whole solution)
  Lesson 2  Full solutions        — every solution start to finish, in order
  Lesson 3  Build from memory     — structural checks, no line to copy

Difficulty for the type-along:
  1  short single lines      the atoms (left, right = 0, len(nums) - 1)
  2  every single line       including long ones and def signatures
  3  two-line windows        a condition and what it does
  4  five-line windows       loop bodies and helper functions
  5  whole solutions         the full function, top to bottom

Unlike the Foundations pools these are NOT randomly generated — the material is
finite and ordered, so batch N is always the same slice. Working through the
class front to back covers every solution exactly once before it wraps.
"""

from __future__ import annotations

import ast
import hashlib
import textwrap
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable

from code_coach.checks import (
    defines_function,
    returns_value,
    uses_for,
    uses_if,
    uses_while,
)
from code_coach.dictation.bank import KEYBOARD_TIPS, LineSpec, make_block_check
from code_coach.leetcode.problems import (
    ALL_CLASS_ID,
    PATTERNS,
    Pattern,
    Problem,
    get_pattern,
)
from code_coach.skills.drills import Drill, DrillStep, requirements_check

# Every LeetCode class id the catalog exposes.
LEETCODE_CLASS_IDS: tuple[str, ...] = (ALL_CLASS_ID,) + tuple(p.id for p in PATTERNS)

# Longest a line can be and still count as a level-1 "atom".
_ATOM_MAX = 34

# Window sizes for the middle difficulties.
_WINDOW_FOR_LEVEL = {3: 2, 4: 5}

# Lines that read as fragments when a window starts on them. Dart's closers
# and continuations differ from Python's, so both sets are listed — a line
# starting with `}` or `..` is no more a sensible opening than `elif ` is.
_FRAGMENT_STARTS = (
    "else:", "elif ", "except", "finally:", "or ", "and ",
    ")", "]", "}", "};", "});", "})",
    "} else", "..", "?", ":",
)


def is_leetcode_class(class_id: str) -> bool:
    return class_id in LEETCODE_CLASS_IDS


def patterns_for_language(language: str) -> tuple[Pattern, ...]:
    """The solution bank in the chosen language.

    Both banks carry the same problems in the same order, so switching
    language keeps your place in the curriculum.
    """
    if language == "dart":
        from code_coach.leetcode.problems_dart import PATTERNS as DART_PATTERNS

        return DART_PATTERNS
    if language == "javascript":
        from code_coach.leetcode.problems_js import PATTERNS as JS_PATTERNS

        return JS_PATTERNS
    if language == "typescript":
        from code_coach.leetcode.problems_ts import PATTERNS as TS_PATTERNS

        return TS_PATTERNS
    return PATTERNS


def current_language() -> str:
    """The student's chosen language.

    Read here rather than threaded through every call: the bank is reached
    from drill generation, catalog building and the study panel, and each of
    those would otherwise need a language argument it doesn't care about.
    """
    try:
        from code_coach.progress.store import ProgressStore

        return getattr(ProgressStore().load(), "language", "python") or "python"
    except Exception:
        return "python"


# ── Units ───────────────────────────────────────────────────


@dataclass(frozen=True)
class Unit:
    """One thing to type, plus the coaching line that explains it."""

    example: str
    tip: str
    pattern_id: str | None = None
    problem_number: int | None = None


def _patterns_for(class_id: str, language: str | None = None) -> tuple[Pattern, ...]:
    patterns = patterns_for_language(language or current_language())
    if class_id == ALL_CLASS_ID:
        return patterns
    found = next((p for p in patterns if p.id == class_id), None)
    return (found,) if found else ()


def _lines(code: str) -> list[str]:
    return [ln for ln in code.splitlines() if ln.strip()]


def _dedent(lines: list[str]) -> str:
    return textwrap.dedent("\n".join(lines))


def _problem_tip(problem: Problem, pattern: Pattern) -> str:
    return (
        f"{pattern.name} · {problem.label} ({problem.difficulty}) — "
        f"{problem.idea} · {problem.complexity}"
    )


def _setup_tip(pattern: Pattern) -> str:
    return f"{pattern.name} setup — the solutions below assume this."


def _is_fragment_start(line: str) -> bool:
    s = line.strip()
    return any(s.startswith(f) for f in _FRAGMENT_STARTS)


def _units_for_problem(problem: Problem, pattern: Pattern, level: int) -> list[Unit]:
    """Typing units drawn from one solution at the given difficulty."""
    tip = _problem_tip(problem, pattern)
    lines = _lines(problem.code)
    out: list[Unit] = []

    def add(example: str) -> None:
        out.append(
            Unit(
                example=example,
                tip=tip,
                pattern_id=pattern.id,
                problem_number=problem.number,
            )
        )

    if level >= 5:
        add(problem.code)
        return out

    if level <= 2:
        for raw in lines:
            text = raw.strip()
            if level == 1 and len(text) > _ATOM_MAX:
                continue
            if _is_fragment_start(raw):
                continue
            add(text)
        # A solution made only of long lines still deserves a rep at level 1.
        if not out:
            add(lines[0].strip())
        return out

    size = _WINDOW_FOR_LEVEL.get(level, 2)
    for i in range(len(lines)):
        window = lines[i : i + size]
        if len(window) < size:
            break
        if _is_fragment_start(window[0]):
            continue
        add(_dedent(window))
    if not out:
        add(_dedent(lines))
    return out


@lru_cache(maxsize=None)
def _units(class_id: str, level: int, language: str = "python") -> tuple[Unit, ...]:
    """All material for a class at one difficulty, in learning order.

    `language` is part of the cache key, not decoration — without it the first
    language to warm the cache would be served to the other.
    """
    out: list[Unit] = []
    for pattern in _patterns_for(class_id, language):
        for block in pattern.preamble:
            out.append(
                Unit(
                    example=block,
                    tip=_setup_tip(pattern),
                    pattern_id=pattern.id,
                )
            )
        for problem in pattern.problems:
            out.extend(_units_for_problem(problem, pattern, level))

    # Drop consecutive repeats (common short lines like `return True`) so a
    # window never asks for the same text twice in a row.
    deduped: list[Unit] = []
    for unit in out:
        if deduped and deduped[-1].example == unit.example:
            continue
        deduped.append(unit)
    return tuple(deduped)


def unit_count(class_id: str, level: int) -> int:
    return len(_units(class_id, max(1, min(5, level)), current_language()))


# ── Lesson 1 — endless verbatim type-along ──────────────────


def _spec_for(unit: Unit, position: int) -> LineSpec:
    # Content digest, not hash() — str hashing is salted per process, and a
    # restart must not orphan the waypoint ids saved in progress.
    digest = hashlib.sha1(unit.example.encode("utf-8")).hexdigest()[:8]
    return LineSpec(
        id=f"lc-{position}-{digest}",
        example=unit.example,
        check=make_block_check(unit.example),
        tip=unit.tip,
        keyboard_tip=KEYBOARD_TIPS[position % len(KEYBOARD_TIPS)],
        family="leetcode",
        level=1,
        pattern_id=unit.pattern_id,
        problem_number=unit.problem_number,
    )


def leetcode_specs(class_id: str, *, batch: int, count: int, level: int) -> list[LineSpec]:
    """The `batch`-th window of this class's material, wrapping at the end."""
    level = max(1, min(5, int(level)))
    units = _units(class_id, level, current_language())
    if not units:
        return []
    # Never serve more exercises than the class has answers. A class with four
    # whole solutions was padded out to eight by handing each one over twice,
    # which read as "1 of 4" and then kept going past four.
    count = min(count, len(units))
    start = (batch * count) % len(units)
    return [
        _spec_for(units[(start + i) % len(units)], start + i) for i in range(count)
    ]


def make_leetcode_batch(
    class_id: str,
    *,
    class_number: int,
    class_name: str,
    batch: int = 0,
    count: int = 8,
    level: int = 1,
    drill_id: str | None = None,
) -> Any:
    from code_coach.dictation.session import specs_to_drill

    level = max(1, min(5, int(level)))
    specs = leetcode_specs(class_id, batch=batch, count=count, level=level)
    units = _units(class_id, level, current_language())
    total = len(units) or 1
    # The window may have been trimmed to fit the class, so count what was
    # actually served rather than what was asked for.
    served = len(specs) or 1
    done = min((batch * served) % total + served, total)

    title = f"Class {class_number} · {class_name} · Lesson 1 — Type-along (endless)"
    drill = specs_to_drill(
        specs,
        drill_id=drill_id or f"{class_id}-l1",
        title=title,
        batch=batch,
        level=level,
        # Blank on purpose. The instruction is already on screen (Type this
        # panel + coach line); a starter comment just gets deleted every time,
        # and it merges into the first typed line if you don't.
        starter="",
    )
    drill.skill = "leetcode"
    drill.tags = ["dictation", "leetcode", class_id, "endless"]
    drill.prompt = (
        f"Verbatim type-along · difficulty {level} · {done}/{total} of this "
        "class's material. Turn difficulty up for bigger chunks — 5 is whole solutions."
    )
    return drill


# ── Lesson 2 — every solution, start to finish ──────────────


def leetcode_solutions_drill(class_id: str) -> Drill:
    """One exercise per solution: type the whole thing, in learning order."""
    patterns = _patterns_for(class_id)
    steps: list[DrillStep] = []
    for pattern in patterns:
        for block in pattern.preamble:
            steps.append(
                DrillStep(
                    id=f"{pattern.id}-setup-{len(steps)}",
                    label=block,
                    check=make_block_check(block),
                    concept="setup",
                    why=_setup_tip(pattern),
                    hint="Type it once — the solutions below build on it.",
                    example=block,
                    pattern_id=pattern.id,
                )
            )
        for problem in pattern.problems:
            steps.append(
                DrillStep(
                    id=f"{pattern.id}-{problem.number}",
                    label=problem.code,
                    check=make_block_check(problem.code),
                    concept=pattern.name,
                    why=_problem_tip(problem, pattern),
                    # Complexity already rides along in the tip — spend the
                    # keyboard slot on an actual key.
                    hint=KEYBOARD_TIPS[len(steps) % len(KEYBOARD_TIPS)],
                    example=problem.code,
                    pattern_id=pattern.id,
                    problem_number=problem.number,
                )
            )

    name = _class_name(class_id)
    return Drill(
        id=f"{class_id}-l2",
        skill="leetcode",
        difficulty=4,
        title=f"{name} · Lesson 2 — Full solutions",
        prompt=(
            "Type each solution start to finish. Same verbatim check as Lesson 1, "
            "but never broken into pieces."
        ),
        starter="",
        steps=steps,
        tags=["leetcode", class_id, "solutions"],
        path_order=900,
        in_progressive=False,
    )


# ── Lesson 3 — build from memory ────────────────────────────


def _defines_class(code: str, name: str) -> bool:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return False
    return any(
        isinstance(n, ast.ClassDef) and n.name == name for n in ast.walk(tree)
    )


def _top_level_names(code: str) -> tuple[list[str], list[str]]:
    """(function names, class names) defined anywhere in the source."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return [], []
    funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    return funcs, classes


def _requirements_for(
    problem: Problem, language: str = "python"
) -> list[tuple[str, Callable[[str], bool]]]:
    """The structural pieces a from-memory attempt must contain.

    Derived from the reference solution rather than hand-written, so it stays
    honest: it asks for the shape of the algorithm, not one exact phrasing.
    """
    code = problem.code
    if language in ("dart", "javascript", "typescript"):
        from code_coach import brace_checks as chk

        names = chk.top_level_names
        defines_fn = chk.defines_function
        defines_cls = chk.defines_class
        uses_for_fn, uses_while_fn, uses_if_fn = chk.uses_for, chk.uses_while, chk.uses_if
        returns_fn = chk.returns_value
        fn_label = "{name}(...)"
        cls_label = "class {name}"
    else:
        names = _top_level_names
        defines_fn = defines_function
        defines_cls = _defines_class
        uses_for_fn, uses_while_fn, uses_if_fn = uses_for, uses_while, uses_if
        returns_fn = returns_value
        fn_label = "def {name}(...)"
        cls_label = "class {name}:"

    funcs, classes = names(code)
    reqs: list[tuple[str, Callable[[str], bool]]] = []

    if classes:
        name = classes[0]
        reqs.append(
            (cls_label.format(name=name), lambda c, n=name: defines_cls(c, n))
        )
    elif funcs:
        name = funcs[0]
        reqs.append(
            (fn_label.format(name=name), lambda c, n=name: defines_fn(c, n))
        )
        # Where there's an inner helper (backtrack, dfs, depth…) it IS the
        # pattern, so ask for it by name.
        if funcs[1:]:
            helper = funcs[1]
            reqs.append(
                (
                    f"an inner helper — {helper}(...)",
                    lambda c, n=helper: defines_fn(c, n),
                )
            )

    if uses_while_fn(code):
        reqs.append(("a while loop", uses_while_fn))
    if uses_for_fn(code):
        reqs.append(("a for loop", uses_for_fn))
    if uses_if_fn(code) and len(reqs) < 4:
        reqs.append(("an if that decides something", uses_if_fn))
    if returns_fn(code):
        reqs.append(("a return that hands back a value", returns_fn))

    return reqs[:5]


def leetcode_build_drill(class_id: str) -> Drill:
    """Write each solution from the idea alone — no line to copy."""
    language = current_language()
    patterns = _patterns_for(class_id, language)
    steps: list[DrillStep] = []
    for pattern in patterns:
        for problem in pattern.problems:
            reqs = _requirements_for(problem, language)
            steps.append(
                DrillStep(
                    id=f"{pattern.id}-build-{problem.number}",
                    label=f"{problem.label} — {problem.idea}",
                    check=requirements_check(reqs),
                    concept=pattern.name,
                    why=f"{pattern.tell} Target: {problem.complexity}.",
                    hint="Stuck? Lesson 1 drills these exact lines.",
                    example=problem.code,
                    requirements=reqs,
                    pattern_id=pattern.id,
                    problem_number=problem.number,
                )
            )

    name = _class_name(class_id)
    return Drill(
        id=f"{class_id}-l3",
        skill="leetcode",
        difficulty=5,
        title=f"{name} · Lesson 3 — Build from memory",
        prompt=(
            "No line to copy — you get the idea and the target complexity. "
            "The checklist shows which pieces are still missing; Hint reveals the solution."
        ),
        starter="",
        steps=steps,
        tags=["leetcode", class_id, "build"],
        path_order=901,
        in_progressive=False,
    )


# ── Naming ──────────────────────────────────────────────────


def study_payload(
    pattern_id: str | None,
    problem_number: int | None,
    language: str = "python",
) -> dict[str, Any] | None:
    """Question + pattern lesson for one exercise, or None if not LeetCode.

    `language` is a parameter, not looked up here: this runs once per step, so
    resolving it internally meant re-reading and re-parsing the progress file
    eight times to build one session.
    """
    from code_coach.leetcode.study import brief_for, lesson_for
    from code_coach.leetcode.worked import worked_for

    if not pattern_id:
        return None
    # Look the pattern up in the active language's bank so the complexity and
    # idea shown match the code on screen.
    patterns = patterns_for_language(language)
    pattern = next((p for p in patterns if p.id == pattern_id), None) or get_pattern(
        pattern_id
    )
    out: dict[str, Any] = {"problem": None, "lesson": None}

    lesson = lesson_for(pattern_id)
    if lesson and pattern:
        out["lesson"] = {
            "id": pattern.id,
            "name": pattern.name,
            "summary": lesson.summary,
            "when": lesson.when,
            "template": lesson.template,
            "steps": list(lesson.steps),
            "pitfalls": list(lesson.pitfalls),
        }
        # The lesson proper: one problem taken from the question to a
        # finished solution. Everything above says what the pattern is; this
        # is the part that shows how anyone gets there.
        worked = worked_for(pattern_id)
        if worked:
            out["lesson"]["worked"] = {
                "problem": worked.problem,
                "naive": worked.naive,
                "why_not": worked.why_not,
                "insight": worked.insight,
                "stages": [
                    {"explain": st.explain, "code": st.code}
                    for st in worked.stages
                ],
            }

    if problem_number is not None and pattern:
        problem = next(
            (p for p in pattern.problems if p.number == problem_number), None
        )
        brief = brief_for(problem_number)
        if problem and brief:
            out["problem"] = {
                "number": problem.number,
                "title": problem.title,
                "difficulty": problem.difficulty,
                "statement": brief.statement,
                "examples": list(brief.examples),
                "note": brief.note,
                "idea": problem.idea,
                "complexity": problem.complexity,
                "url": brief.url,
                # The whole solution, not just the chunk being typed — this is
                # what "check my work" compares against.
                "solution": problem.code,
            }

    if out["problem"] is None and out["lesson"] is None:
        return None
    return out


def _class_name(class_id: str) -> str:
    if class_id == ALL_CLASS_ID:
        return "LeetCode — Every Answer"
    pattern = get_pattern(class_id)
    return f"LeetCode — {pattern.name}" if pattern else "LeetCode"
