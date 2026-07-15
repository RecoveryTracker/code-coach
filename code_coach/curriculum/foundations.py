"""
Foundations class
  Lesson 1 — Type-along (dictation of the toolkit)
  Lesson 2 — Build (goals + hint / supporting lesson links)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from code_coach.dictation.bank import (
    check_int_assign,
    check_print_string,
    check_print_var,
    check_str_assign,
)
from code_coach.skills.drills import Drill, DrillStep, requirements_check


@dataclass
class SupportLink:
    skill_id: str
    label: str
    lesson_title: str = "Foundations · Lesson 1"


@dataclass
class BuildTask:
    id: str
    goal: str
    hint_lines: list[str]
    supports: list[SupportLink]
    # The pieces this goal needs, each beginner-labeled. The step check is
    # derived from these (all must pass) and the UI shows them as ✓/✗.
    requirements: list[tuple[str, Callable[[str], bool]]]
    tip: str
    keyboard_tip: str = "End of line: ⌘ →   ·   Down a line: ↓"

    @property
    def check(self) -> Callable[[str], bool]:
        return requirements_check(self.requirements)


FOUNDATIONS_L2_TASKS: list[BuildTask] = [
    BuildTask(
        id="f2-print-msg",
        goal="Make the program show any short message on the screen.",
        hint_lines=['print("Hello, world!")'],
        supports=[
            SupportLink("print_string", "Type-along: print a message"),
        ],
        requirements=[
            ('a complete print("...") with your message in quotes', check_print_string),
        ],
        tip="You need print and quotes around the text.",
    ),
    BuildTask(
        id="f2-store-name",
        goal="Store your name in a variable called name, then print it.",
        hint_lines=['name = "Ada"', "print(name)"],
        supports=[
            SupportLink("assign_str", "Type-along: store text in a variable"),
            SupportLink("print_var", "Type-along: print a variable"),
        ],
        requirements=[
            ('name = "..." (any name, in quotes)', lambda c: check_str_assign(c, "name")),
            ("print(name) — no quotes around name", lambda c: check_print_var(c, "name")),
        ],
        tip="Two moves: assign with = and quotes, then print(name) without quotes around name.",
    ),
    BuildTask(
        id="f2-city-print",
        goal="Store a city in city, then print the city.",
        hint_lines=['city = "Seattle"', "print(city)"],
        supports=[
            SupportLink("assign_str", "Type-along: store text in a variable"),
            SupportLink("print_var", "Type-along: print a variable"),
        ],
        requirements=[
            ('city = "..." (any city, in quotes)', lambda c: check_str_assign(c, "city")),
            ("print(city)", lambda c: check_print_var(c, "city")),
        ],
        tip="Same pattern as name — different variable.",
    ),
    BuildTask(
        id="f2-number",
        goal="Store a whole number in favorite_number, then print it.",
        hint_lines=["favorite_number = 7", "print(favorite_number)"],
        supports=[
            SupportLink("assign_int", "Type-along: store a number"),
            SupportLink("print_var", "Type-along: print a variable"),
        ],
        requirements=[
            (
                "favorite_number = a whole number (NO quotes)",
                lambda c: check_int_assign(c, "favorite_number"),
            ),
            ("print(favorite_number)", lambda c: check_print_var(c, "favorite_number")),
        ],
        tip="Numbers usually have no quotes: favorite_number = 7",
    ),
    BuildTask(
        id="f2-both",
        goal="Create name and city, print both (in any order).",
        hint_lines=[
            'name = "Ada"',
            'city = "Seattle"',
            "print(name)",
            "print(city)",
        ],
        supports=[
            SupportLink("assign_str", "Type-along: store text"),
            SupportLink("print_var", "Type-along: print a variable"),
        ],
        requirements=[
            ('name = "..."', lambda c: check_str_assign(c, "name")),
            ('city = "..."', lambda c: check_str_assign(c, "city")),
            ("print(name)", lambda c: check_print_var(c, "name")),
            ("print(city)", lambda c: check_print_var(c, "city")),
        ],
        tip="Build it from the pieces you typed in Lesson 1.",
    ),
]


def foundations_l2_drill() -> Drill:
    steps = [
        DrillStep(
            id=t.id,
            label=t.goal,  # goal text for build mode
            check=t.check,
            concept="build",
            why=t.tip,
            hint=t.keyboard_tip,
            example="\n".join(t.hint_lines),
            requirements=t.requirements,
        )
        for t in FOUNDATIONS_L2_TASKS
    ]
    return Drill(
        id="foundations-l2",
        skill="basics",
        difficulty=2,
        title="Class 1 · Foundations · Lesson 2 — Build",
        prompt="Goals only — use Hint if you need the exact lines or a supporting lesson.",
        starter="# Class 1 · Foundations · Lesson 2 — build these goals yourself\n\n",
        steps=steps,
        tags=["foundations", "lesson-2", "build"],
        path_order=2,
        in_progressive=True,
    )


def task_by_id(task_id: str) -> BuildTask | None:
    for t in FOUNDATIONS_L2_TASKS:
        if t.id == task_id:
            return t
    return None


# Map skill → review lines (from Lesson 1 toolkit)
REVIEW_LINES: dict[str, list[tuple[str, str, Callable[[str], bool], str]]] = {
    # id, example, check, tip
    "print_string": [
        (
            "rev-print-1",
            'print("Hello, world!")',
            check_print_string,
            "print(...) shows text. Quotes mark a string.",
        ),
        (
            "rev-print-2",
            'print("hi")',
            check_print_string,
            "Any message in quotes is fine.",
        ),
        (
            "rev-print-3",
            'print("I am learning")',
            check_print_string,
            "Finish the whole line: quotes and ).",
        ),
    ],
    "assign_str": [
        (
            "rev-as-1",
            'name = "Ada"',
            lambda c: check_str_assign(c, "name"),
            "Left side is the name; right side is text in quotes.",
        ),
        (
            "rev-as-2",
            'city = "Seattle"',
            lambda c: check_str_assign(c, "city"),
            "Same pattern, different variable.",
        ),
        (
            "rev-as-3",
            'name = "Sam"',
            lambda c: check_str_assign(c, "name"),
            "Close the quotes to finish the line.",
        ),
    ],
    "assign_int": [
        (
            "rev-ai-1",
            "favorite_number = 7",
            lambda c: check_int_assign(c, "favorite_number"),
            "No quotes around the number.",
        ),
        (
            "rev-ai-2",
            "score = 10",
            lambda c: check_int_assign(c, "score"),
            "score = 10 is a number variable.",
        ),
        (
            "rev-ai-3",
            "lives = 3",
            lambda c: check_int_assign(c, "lives"),
            "Whole numbers, no quotes.",
        ),
    ],
    "print_var": [
        (
            "rev-pv-1",
            "print(name)",
            lambda c: check_print_var(c, "name"),
            "No quotes around the variable name.",
        ),
        (
            "rev-pv-2",
            "print(city)",
            lambda c: check_print_var(c, "city"),
            "print(city) prints the value of city.",
        ),
        (
            "rev-pv-3",
            "print(favorite_number)",
            lambda c: check_print_var(c, "favorite_number"),
            "Works for numbers too.",
        ),
    ],
}


def review_drill_for_skill(skill_id: str) -> Drill | None:
    rows = REVIEW_LINES.get(skill_id)
    if not rows:
        return None
    steps = [
        DrillStep(
            id=rid,
            label=example,
            check=check,
            concept=skill_id,
            why=tip,
            hint="End of line: ⌘ →   ·   Down a line: ↓",
            example=example,
        )
        for rid, example, check, tip in rows
    ]
    titles = {
        "print_string": "Print a message",
        "assign_str": "Store text in a variable",
        "assign_int": "Store a number",
        "print_var": "Print a variable",
    }
    return Drill(
        id=f"review-{skill_id}",
        skill="basics",
        difficulty=1,
        title=f"Supporting · {titles.get(skill_id, skill_id)}",
        prompt="Short Lesson 1-style practice for this skill. Then go back to Lesson 2.",
        starter=f"# Review · {titles.get(skill_id, skill_id)}\n\n",
        steps=steps,
        tags=["review", "foundations", "lesson-1"],
        path_order=0,
        in_progressive=False,
    )
