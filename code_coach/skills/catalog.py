"""Skill taxonomy for practice filters and progressive path."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Skill:
    id: str
    name: str
    description: str
    # Order in progressive path (lower = earlier)
    order: int
    # Typical difficulty band this skill lives in
    base_difficulty: int


SKILLS: dict[str, Skill] = {
    s.id: s
    for s in [
        Skill(
            "basics",
            "Basics",
            "print, variables, types — first programs",
            order=10,
            base_difficulty=1,
        ),
        Skill(
            "conditionals",
            "Conditionals",
            "if / elif / else and boolean logic",
            order=20,
            base_difficulty=2,
        ),
        Skill(
            "loops",
            "Loops",
            "while, for, range — repetition patterns",
            order=30,
            base_difficulty=2,
        ),
        Skill(
            "lists",
            "Lists (arrays)",
            "ordered collections, index, append, loop",
            order=40,
            base_difficulty=3,
        ),
        Skill(
            "dicts",
            "Dicts & sets",
            "key→value maps and uniqueness",
            order=50,
            base_difficulty=3,
        ),
        Skill(
            "functions",
            "Functions",
            "def, arguments, return",
            order=60,
            base_difficulty=3,
        ),
        Skill(
            "patterns",
            "Coding patterns",
            "accumulate, filter, search, nest",
            order=70,
            base_difficulty=4,
        ),
        Skill(
            "structures",
            "Data structures",
            "stack, queue, and structure thinking",
            order=80,
            base_difficulty=5,
        ),
    ]
}


def list_skills() -> list[Skill]:
    return sorted(SKILLS.values(), key=lambda s: s.order)


def get_skill(skill_id: str) -> Skill | None:
    return SKILLS.get(skill_id)
