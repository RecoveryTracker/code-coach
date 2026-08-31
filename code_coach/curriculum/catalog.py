"""
Full curriculum tree:

  Class → Lesson → Exercise

Navigation can jump freely among all three levels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from code_coach.checks import (
    calls_function_with_args,
    compares,
    count_calls,
    uses_and,
    uses_for,
    uses_if,
    uses_if_else,
    uses_while,
)
from code_coach.checks import calls_function, references_name
from code_coach.curriculum.foundations import (
    FOUNDATIONS_L2_TASKS,
    foundations_l2_drill,
)
from code_coach.dictation.bank import (
    check_int_assign,
    check_print_var,
    check_str_assign,
)
from code_coach.dictation.session import make_class_dictation_batch
from code_coach.leetcode.bank import (
    is_leetcode_class,
    leetcode_build_drill,
    leetcode_solutions_drill,
    make_leetcode_batch,
)
from code_coach.leetcode.problems import ALL_CLASS_ID, PATTERNS, problem_count
from code_coach.skills.drills import (
    Drill,
    DrillStep,
    register_dynamic,
    requirements_check,
)


@dataclass
class LessonDef:
    number: int
    id: str  # e.g. foundations-l1
    title: str  # short: "Type-along"
    role: str  # dictation | build
    full_title: str  # Foundations · Lesson 1 — Type-along
    resolve: Callable[[], Drill]


@dataclass
class ClassDef:
    id: str
    name: str
    description: str
    number: int  # Class 1, 2, 3…
    lessons: list[LessonDef] = field(default_factory=list)

    def lesson(self, number: int) -> LessonDef | None:
        for L in self.lessons:
            if L.number == number:
                return L
        return self.lessons[0] if self.lessons else None


def _build_step(
    sid: str,
    goal: str,
    requirements,
    tip: str,
    kb: str,
    example: str,
    expect_output: str | None = None,
) -> DrillStep:
    """A build exercise defined by its named requirements — the check passes
    when all of them do, and the UI shows them as a live ✓/✗ checklist.
    expect_output (for goals that pin exact output) additionally requires a
    Run whose stdout matches."""
    return DrillStep(
        sid,
        goal,
        requirements_check(requirements),
        "build",
        tip,
        kb,
        example,
        requirements=requirements,
        expect_output=expect_output,
    )


# ── Decisions (if / else) content ───────────────────────────
# Lesson 1 of every class is an ENDLESS verbatim type-along drilling that
# class's exact syntax (the curated spine + generated variants live in
# dictation/bank.py). It's the easy fallback when the build lessons are
# too hard — pure muscle memory for parens, quotes, colons, comparisons.


def _active_language() -> str:
    """The student's language, read once at drill-construction time.

    Only the curriculum entry points do this; everything below takes it as an
    argument, so the drill builders stay testable without a progress file.
    """
    try:
        from code_coach.progress.store import ProgressStore

        return getattr(ProgressStore().load(), "language", "python") or "python"
    except Exception:
        return "python"


def _decisions_l1_drill() -> Drill:
    return make_class_dictation_batch(
        "decisions",
        class_number=2,
        class_name="Decisions",
        seed="local-student",
        batch=0,
        level=1,
        language=_active_language(),
    )


def _decisions_l2_drill() -> Drill:
    steps = [
        _build_step(
            "d2-1",
            "If score is greater than 10, print win.",
            [
                ("an if line ending with :", uses_if),
                ("a comparison (like score > 10)", compares),
                ("a print(...) call", lambda c: calls_function(c, "print")),
            ],
            "Use if and a comparison. Hint has the exact lines.",
            "⌘ → end of line",
            'score = 12\nif score > 10:\n    print("win")',
        ),
        _build_step(
            "d2-2",
            "Print even or odd for the number n.",
            [
                ("an if line", uses_if),
                ("an else: branch", uses_if_else),
            ],
            "Use if / else and % 2.",
            "↓ new line in block",
            'n = 7\nif n % 2 == 0:\n    print("even")\nelse:\n    print("odd")',
        ),
        _build_step(
            "d2-3",
            "Print go only if age >= 18 and has_pass is True.",
            [
                ("an if line", uses_if),
                ("two conditions joined with and", uses_and),
            ],
            "Combine two conditions with and.",
            "⌘ →",
            'age = 20\nhas_pass = True\nif age >= 18 and has_pass:\n    print("go")',
        ),
    ]
    # Attach hint metadata via example field (already used for hover)
    return Drill(
        id="decisions-l2",
        skill="conditionals",
        difficulty=2,
        title="Class 2 · Decisions · Lesson 2 — Build",
        prompt="Build if/else from scratch. Use Hint for exact lines.",
        starter="",
        steps=steps,
        tags=["decisions", "lesson-2", "build"],
        path_order=11,
        in_progressive=True,
    )


# ── Loops content ───────────────────────────────────────────


def _loops_l1_drill() -> Drill:
    return make_class_dictation_batch(
        "loops",
        class_number=3,
        class_name="Loops",
        seed="local-student",
        batch=0,
        level=1,
        language=_active_language(),
    )


def _loops_l2_drill() -> Drill:
    steps = [
        _build_step(
            "lp2-1",
            "Print the numbers 0, 1, 2 using a for loop.",
            [
                ("a for line ending with :", uses_for),
                ("range(...) after in", lambda c: calls_function(c, "range")),
            ],
            "for i in range(3): print(i)",
            "↓",
            "for i in range(3):\n    print(i)",
            expect_output="0\n1\n2",
        ),
        _build_step(
            "lp2-2",
            "Sum 1 through 5 into total, then print total.",
            [
                ("a for loop", uses_for),
                ("use total inside", lambda c: references_name(c, "total")),
            ],
            "Start total at 0, add each i, print once after the loop.",
            "⌘ →",
            "total = 0\nfor i in range(1, 6):\n    total = total + i\nprint(total)",
            expect_output="15",
        ),
        _build_step(
            "lp2-3",
            "Count down from 3 to 1 with while, printing each time.",
            [
                ("a while line with a condition", uses_while),
            ],
            "while n > 0, print, then n = n - 1.",
            "↓",
            "n = 3\nwhile n > 0:\n    print(n)\n    n = n - 1",
            expect_output="3\n2\n1",
        ),
    ]
    return Drill(
        id="loops-l2",
        skill="loops",
        difficulty=2,
        title="Class 3 · Loops · Lesson 2 — Build",
        prompt="Build loops from scratch. Hint shows exact lines.",
        starter="",
        steps=steps,
        tags=["loops", "lesson-2", "build"],
        path_order=21,
        in_progressive=True,
    )


def _foundations_l1() -> Drill:
    return make_class_dictation_batch(
        "foundations",
        class_number=1,
        class_name="Foundations",
        seed="local-student",
        batch=0,
        level=1,
        language=_active_language(),
    )


def _foundations_l3() -> Drill:
    """Extra build practice in Foundations (more exercises)."""
    steps = [
        _build_step(
            "f3-1",
            "Print two different messages (two print lines).",
            [
                ("two separate print(...) lines", lambda c: count_calls(c, "print") >= 2),
            ],
            "Two complete print(...) lines.",
            "⌘ →",
            'print("one")\nprint("two")',
        ),
        _build_step(
            "f3-2",
            "Store name and favorite_number, print both.",
            [
                ('name = "..." (text in quotes)', lambda c: check_str_assign(c, "name")),
                (
                    "favorite_number = a whole number (NO quotes)",
                    lambda c: check_int_assign(c, "favorite_number"),
                ),
                ("print(name)", lambda c: check_print_var(c, "name")),
                (
                    "print(favorite_number)",
                    lambda c: check_print_var(c, "favorite_number"),
                ),
            ],
            "Mix string and number variables.",
            "↓",
            'name = "Ada"\nfavorite_number = 7\nprint(name)\nprint(favorite_number)',
        ),
        _build_step(
            "f3-3",
            'Print a label and a number together, e.g. print("score:", 10).',
            [
                (
                    "ONE print with two things, separated by a comma",
                    lambda c: calls_function_with_args(c, "print", min_args=2),
                ),
            ],
            "Comma separates multiple things in print.",
            "⌘ →",
            'print("score:", 10)',
        ),
        _build_step(
            "f3-4",
            "Create city and print it.",
            [
                ('city = "..." (in quotes)', lambda c: check_str_assign(c, "city")),
                ("print(city)", lambda c: check_print_var(c, "city")),
            ],
            "assign then print.",
            "↓",
            'city = "Seattle"\nprint(city)',
        ),
    ]
    return Drill(
        id="foundations-l3",
        skill="basics",
        difficulty=2,
        title="Class 1 · Foundations · Lesson 3 — Build more",
        prompt="More from-scratch practice with print and variables.",
        starter="",
        steps=steps,
        tags=["foundations", "lesson-3", "build"],
        path_order=3,
        in_progressive=True,
    )


# ── Catalog tree ────────────────────────────────────────────

CLASSES: list[ClassDef] = [
    ClassDef(
        id="foundations",
        name="Foundations",
        description="print, variables, strings, numbers",
        number=1,
        lessons=[
            LessonDef(
                1,
                "foundations-l1",
                "Type-along (endless)",
                "dictation",
                "Class 1 · Foundations · Lesson 1 — Type-along (endless)",
                _foundations_l1,
            ),
            LessonDef(
                2,
                "foundations-l2",
                "Build",
                "build",
                "Class 1 · Foundations · Lesson 2 — Build",
                foundations_l2_drill,
            ),
            LessonDef(
                3,
                "foundations-l3",
                "Build more",
                "build",
                "Class 1 · Foundations · Lesson 3 — Build more",
                _foundations_l3,
            ),
        ],
    ),
    ClassDef(
        id="decisions",
        name="Decisions",
        description="if, else, comparisons, and/or",
        number=2,
        lessons=[
            LessonDef(
                1,
                "decisions-l1",
                "Type-along (endless)",
                "dictation",
                "Class 2 · Decisions · Lesson 1 — Type-along (endless)",
                _decisions_l1_drill,
            ),
            LessonDef(
                2,
                "decisions-l2",
                "Build",
                "build",
                "Class 2 · Decisions · Lesson 2 — Build",
                _decisions_l2_drill,
            ),
        ],
    ),
    ClassDef(
        id="loops",
        name="Loops",
        description="for, while, range, accumulate",
        number=3,
        lessons=[
            LessonDef(
                1,
                "loops-l1",
                "Type-along (endless)",
                "dictation",
                "Class 3 · Loops · Lesson 1 — Type-along (endless)",
                _loops_l1_drill,
            ),
            LessonDef(
                2,
                "loops-l2",
                "Build",
                "build",
                "Class 3 · Loops · Lesson 2 — Build",
                _loops_l2_drill,
            ),
        ],
    ),
]


# ── LeetCode classes ────────────────────────────────────────
# One class per pattern, plus a first class that walks every answer in the
# bank. All three lessons are optional side-quests: they sit after the
# Foundations→Decisions→Loops spine and are not part of the progressive path.


def _leetcode_class(
    *,
    class_id: str,
    name: str,
    description: str,
    number: int,
) -> ClassDef:
    def _l1(cid: str = class_id, num: int = number, nm: str = name) -> Drill:
        return make_leetcode_batch(
            cid, class_number=num, class_name=nm, batch=0, level=1
        )

    def _l2(cid: str = class_id) -> Drill:
        return leetcode_solutions_drill(cid)

    def _l3(cid: str = class_id) -> Drill:
        return leetcode_build_drill(cid)

    prefix = f"Class {number} · {name}"
    return ClassDef(
        id=class_id,
        name=name,
        description=description,
        number=number,
        lessons=[
            LessonDef(
                1,
                f"{class_id}-l1",
                "Type-along (endless)",
                "dictation",
                f"{prefix} · Lesson 1 — Type-along (endless)",
                _l1,
            ),
            LessonDef(
                2,
                f"{class_id}-l2",
                "Full solutions",
                "dictation",
                f"{prefix} · Lesson 2 — Full solutions",
                _l2,
            ),
            LessonDef(
                3,
                f"{class_id}-l3",
                "Build from memory",
                "build",
                f"{prefix} · Lesson 3 — Build from memory",
                _l3,
            ),
        ],
    )


def _build_leetcode_classes(first_number: int) -> list[ClassDef]:
    out = [
        _leetcode_class(
            class_id=ALL_CLASS_ID,
            name="LeetCode — Every Answer",
            description=(
                f"All {problem_count()} solutions end to end, in learning order"
            ),
            number=first_number,
        )
    ]
    for offset, pattern in enumerate(sorted(PATTERNS, key=lambda p: p.order), start=1):
        out.append(
            _leetcode_class(
                class_id=pattern.id,
                name=f"LeetCode — {pattern.name}",
                description=pattern.blurb,
                number=first_number + offset,
            )
        )
    return out


CLASSES.extend(_build_leetcode_classes(first_number=len(CLASSES) + 1))


def _build_systems_classes(first_number: int) -> list[ClassDef]:
    """Implement-the-primitive classes: the systems and quant material.

    Built from the C++ bank because that is the only language they exist in
    so far; `classes_for_language` is what keeps them out of the others.
    """
    from code_coach.systems import patterns_for_language as systems_for

    out = []
    for offset, pattern in enumerate(
        sorted(systems_for("cpp"), key=lambda p: p.order)
    ):
        out.append(
            _leetcode_class(
                class_id=pattern.id,
                name=f"Systems — {pattern.name}",
                description=pattern.blurb,
                number=first_number + offset,
            )
        )
    return out


CLASSES.extend(_build_systems_classes(first_number=len(CLASSES) + 1))


def get_class(class_id: str) -> ClassDef | None:
    for c in CLASSES:
        if c.id == class_id:
            return c
    return CLASSES[0] if CLASSES else None


def classes_for_language(language: str) -> list[ClassDef]:
    """Classes that actually have material in this language.

    A class is offered when the language has something to put in it: the
    LeetCode classes need a solution bank, the fundamentals classes need
    declared snippets. Offering one without material handed out Python
    exercises to type into a .dart file, so every answer failed.
    """
    # Python used to short-circuit to everything, which was true while every
    # class was either fundamentals or LeetCode. It stopped being true when a
    # family arrived that Python has no answer for — there is no Python
    # version of "write a spinlock" — so it goes through the same filter.

    from code_coach.fundamentals.base import has_fundamentals
    from code_coach.leetcode.bank import has_own_bank
    from code_coach.systems import has_class as has_systems_class
    from code_coach.systems import is_systems_class

    # has_own_bank rather than an identity check written out again here —
    # patterns_for_language falls back to Python's, and asking four separate
    # places to remember that is how one of them forgets.
    has_leetcode = has_own_bank(language)
    out: list[ClassDef] = []
    for c in CLASSES:
        if is_systems_class(c.id):
            # Per class: the C++ bank is ahead of the Rust one.
            if has_systems_class(c.id, language):
                out.append(c)
        elif is_leetcode_class(c.id):
            if has_leetcode:
                out.append(c)
        elif has_fundamentals(language, c.id):
            out.append(c)
    return out


def first_class_for_language(language: str) -> str:
    available = classes_for_language(language)
    return available[0].id if available else CLASSES[0].id


def class_available_in(class_id: str, language: str) -> bool:
    return any(c.id == class_id for c in classes_for_language(language))


def catalog_payload(language: str = "python") -> list[dict]:
    from code_coach.fundamentals.base import bank_for

    bank = bank_for(language)
    out = []
    for c in classes_for_language(language):
        # A language may name a class differently — SQL's third class is
        # "Grouping & Joins", because SQL doesn't loop.
        declared = bank.get(c.id) if bank else None
        out.append(
            {
                "id": c.id,
                "number": c.number,
                "name": declared.name if declared else c.name,
                "description": (
                    declared.description if declared else c.description
                ),
                "lessons": [
                    {
                        "number": L.number,
                        "id": L.id,
                        "title": L.title,
                        "role": L.role,
                        "full_title": L.full_title,
                    }
                    for L in c.lessons
                ],
            }
        )
    return out


def resolve_drill(class_id: str, lesson_number: int) -> tuple[LessonDef, Drill]:
    cls = get_class(class_id) or CLASSES[0]
    lesson = cls.lesson(lesson_number) or cls.lessons[0]
    drill = lesson.resolve()
    register_dynamic(drill)
    return lesson, drill


def supports_for_build_step(drill_id: str, step_index: int) -> list[dict]:
    """Hint supports for foundations L2; generic for other build lessons."""
    if drill_id == "foundations-l2" and 0 <= step_index < len(FOUNDATIONS_L2_TASKS):
        t = FOUNDATIONS_L2_TASKS[step_index]
        return [
            {
                "skill_id": s.skill_id,
                "label": s.label,
                "lesson_title": s.lesson_title,
            }
            for s in t.supports
        ]
    # Other build lessons: point at that class's Lesson 1
    if drill_id.endswith("-l2") or drill_id.endswith("-l3"):
        class_id = drill_id.rsplit("-", 1)[0]
        cls = get_class(class_id)
        if cls:
            return [
                {
                    "skill_id": "lesson1",
                    "label": f"Type-along: {cls.name} Lesson 1",
                    "lesson_title": f"{cls.name} · Lesson 1",
                }
            ]
    return []


def hint_lines_for_step(drill: Drill, step_index: int) -> list[str]:
    if step_index < 0 or step_index >= len(drill.steps):
        return []
    s = drill.steps[step_index]
    if drill.id == "foundations-l2" and step_index < len(FOUNDATIONS_L2_TASKS):
        return list(FOUNDATIONS_L2_TASKS[step_index].hint_lines)
    if s.example and "\n" in s.example:
        return s.example.split("\n")
    if s.example:
        return [s.example]
    if s.label and not s.label[0].isupper() and "(" in s.label:
        # label is code
        return [s.label]
    return [s.example] if s.example else []
