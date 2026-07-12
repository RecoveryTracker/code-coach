"""Turn dictation LineSpecs into Drill objects for the existing evaluate path."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from code_coach.dictation.bank import (
    DICTATION_LEVEL_LABELS,
    WINDOW_SIZE,
    LineSpec,
    build_class_dictation_steps,
    build_dictation_steps,
)

if TYPE_CHECKING:
    pass

# Re-export for callers
__all__ = [
    "WINDOW_SIZE",
    "make_class1_batch",
    "make_class_dictation_batch",
    "specs_to_drill",
    "tips_payload",
]

# Skill id each class's dictation reports XP under.
_CLASS_SKILLS = {
    "foundations": "basics",
    "decisions": "conditionals",
    "loops": "loops",
}


def specs_to_drill(
    specs: list[LineSpec],
    *,
    drill_id: str = "class-1-dictation",
    title: str = "Class 1 · Foundations · Lesson 1 — Type-along (endless)",
    batch: int = 0,
    level: int = 1,
    starter: str | None = None,
) -> Any:
    # Lazy import avoids circular import with skills.drills
    from code_coach.skills.drills import Drill, DrillStep

    steps = [
        DrillStep(
            id=s.id,
            label=s.example,
            check=s.check,
            concept=s.family,
            why=s.tip,
            hint=s.keyboard_tip,
            example=s.example,
        )
        for s in specs
    ]
    level_label = DICTATION_LEVEL_LABELS.get(level, f"Level {level}")
    base_title = title
    if batch > 0:
        base_title = f"{title} · set {batch + 1}"
    return Drill(
        id=drill_id,
        skill="basics",
        difficulty=level,
        title=base_title,
        prompt=(
            f"Endless type-along · difficulty {level} ({level_label}). "
            "Turn difficulty up for multi-line and functions. Stay here as long as you want."
        ),
        starter=starter or "# Class 1 · Foundations · Lesson 1 — endless type-along\n\n",
        steps=steps,
        tags=["dictation", "class-1", "endless"],
        path_order=1,
        in_progressive=True,
    )


def make_class1_batch(
    seed: str,
    batch: int = 0,
    count: int = WINDOW_SIZE,
    level: int = 1,
) -> Any:
    specs = build_dictation_steps(
        seed=f"{seed}:batch:{batch}:lv{level}",
        count=count,
        include_spine=(batch == 0 and level <= 2),
        level=level,
    )
    title = "Class 1 · Foundations · Lesson 1 — Type-along (endless)"
    return specs_to_drill(
        specs,
        drill_id="class-1-dictation",
        title=title,
        batch=batch,
        level=level,
    )


def make_class_dictation_batch(
    class_id: str,
    *,
    class_number: int,
    class_name: str,
    seed: str,
    batch: int = 0,
    count: int = WINDOW_SIZE,
    level: int = 1,
    drill_id: str | None = None,
) -> Any:
    """Endless Lesson-1 type-along for ANY class — the easy fallback layer that
    drills exactly the syntax this class's build lessons need."""
    if class_id == "foundations":
        return make_class1_batch(seed=seed, batch=batch, count=count, level=level)

    specs = build_class_dictation_steps(
        class_id,
        seed=f"{seed}:batch:{batch}:lv{level}",
        count=count,
        include_spine=(batch == 0 and level <= 2),
        level=level,
    )
    title = (
        f"Class {class_number} · {class_name} · Lesson 1 — Type-along (endless)"
    )
    drill = specs_to_drill(
        specs,
        drill_id=drill_id or f"{class_id}-l1",
        title=title,
        batch=batch,
        level=level,
        starter=(
            f"# Class {class_number} · {class_name} · Lesson 1 — "
            "endless type-along\n\n"
        ),
    )
    drill.skill = _CLASS_SKILLS.get(class_id, drill.skill)
    drill.tags = ["dictation", class_id, "endless"]
    return drill


def tips_payload(specs: list[LineSpec]) -> list[dict[str, str]]:
    return [
        {
            "id": s.id,
            "tip": s.tip,
            "keyboard_tip": s.keyboard_tip,
            "example": s.example,
        }
        for s in specs
    ]
