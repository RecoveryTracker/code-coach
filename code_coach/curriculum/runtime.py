"""Resolve active drill from curriculum position (class / lesson / review)."""

from __future__ import annotations

from typing import Any

from code_coach.curriculum.catalog import (
    CLASSES,
    catalog_payload,
    get_class,
    resolve_drill,
)
from code_coach.curriculum.foundations import review_drill_for_skill
from code_coach.dictation.session import make_class_dictation_batch
from code_coach.progress.store import StudentProgress
from code_coach.skills.drills import Drill, register_dynamic, set_class1_batch


def lesson_meta_for_drill(drill_id: str, progress: StudentProgress) -> dict[str, Any]:
    if drill_id.startswith("review-"):
        cls = get_class(progress.curriculum_class or "foundations")
        return {
            "class_id": cls.id if cls else "foundations",
            "class_number": cls.number if cls else 1,
            "class_name": cls.name if cls else "Foundations",
            "lesson_number": 1,
            "lesson_role": "review",
            "lesson_title": f"Class {cls.number if cls else 1} · {cls.name if cls else 'Foundations'} · supporting",
            "display_title": None,
            "exercise_count": None,
        }

    class_id = progress.curriculum_class or "foundations"
    lesson_n = int(progress.curriculum_lesson or 1)
    cls = get_class(class_id)
    lesson = cls.lesson(lesson_n) if cls else None
    if lesson and (drill_id == lesson.id or drill_id.startswith(class_id)):
        return {
            "class_id": cls.id,
            "class_number": cls.number,
            "class_name": cls.name,
            "lesson_number": lesson.number,
            "lesson_role": lesson.role,
            "lesson_title": lesson.full_title,
            "display_title": lesson.full_title,
            "exercise_count": None,
        }

    # Fallback by drill id
    for c in CLASSES:
        for L in c.lessons:
            if L.id == drill_id:
                return {
                    "class_id": c.id,
                    "class_number": c.number,
                    "class_name": c.name,
                    "lesson_number": L.number,
                    "lesson_role": L.role,
                    "lesson_title": L.full_title,
                    "display_title": L.full_title,
                    "exercise_count": None,
                }

    return {
        "class_id": "foundations",
        "class_number": 1,
        "class_name": "Foundations",
        "lesson_number": 1,
        "lesson_role": "dictation",
        "lesson_title": "Class 1 · Foundations · Lesson 1",
        "display_title": "Class 1 · Foundations · Lesson 1 — Type-along",
        "exercise_count": None,
    }


def get_active_drill(progress: StudentProgress) -> Drill:
    if progress.review_skill:
        # Class-aware review: foundations skills, or generic lesson1
        if progress.review_skill == "lesson1":
            class_id = progress.curriculum_class or "foundations"
            # Jump to that class lesson 1 as "review"
            _, drill = resolve_drill(class_id, 1)
            return drill
        drill = review_drill_for_skill(progress.review_skill)
        if drill:
            register_dynamic(drill)
            return drill

    class_id = progress.curriculum_class or "foundations"
    lesson_n = int(progress.curriculum_lesson or 1)

    # Lesson 1 of EVERY class: endless type-along windows (never graduates) —
    # the easy fallback layer drilling that class's exact syntax.
    cls = get_class(class_id)
    lesson = cls.lesson(lesson_n) if cls else None
    if cls and lesson and lesson.number == 1 and lesson.role == "dictation":
        level = int(getattr(progress, "dictation_level", 1) or 1)
        batch = progress.batch_for(cls.id)
        if cls.id == "foundations":
            # keep the progressive-pool head in sync for foundations
            set_class1_batch(seed="local-student", batch=batch, level=level)
        drill = make_class_dictation_batch(
            cls.id,
            class_number=cls.number,
            class_name=cls.name,
            seed="local-student",
            batch=batch,
            level=level,
            # From the caller's progress, not read again inside — this is the
            # request's language, and it's already in hand here.
            language=getattr(progress, "language", "python") or "python",
        )
        register_dynamic(drill)
        return drill

    _, drill = resolve_drill(class_id, lesson_n)
    return drill


def goto_position(
    progress: StudentProgress,
    *,
    class_id: str | None = None,
    lesson_number: int | None = None,
) -> StudentProgress:
    if class_id:
        progress.curriculum_class = class_id
    if lesson_number is not None:
        cls = get_class(progress.curriculum_class or "foundations")
        max_l = len(cls.lessons) if cls else 1
        progress.curriculum_lesson = max(1, min(max_l, int(lesson_number)))
    progress.review_skill = None
    progress.review_return_lesson = None
    progress.review_return_class = None
    progress.current_drill_id = None

    cls = get_class(progress.curriculum_class or "foundations")
    lesson = cls.lesson(progress.curriculum_lesson) if cls else None
    if lesson:
        progress.current_drill_id = lesson.id
    return progress


def goto_lesson(progress: StudentProgress, lesson_number: int) -> StudentProgress:
    return goto_position(progress, lesson_number=lesson_number)


def enter_review(progress: StudentProgress, skill_id: str) -> StudentProgress:
    progress.review_return_class = progress.curriculum_class or "foundations"
    progress.review_return_lesson = progress.curriculum_lesson or 2
    progress.review_skill = skill_id
    progress.current_drill_id = f"review-{skill_id}"
    return progress


def back_from_review(progress: StudentProgress) -> StudentProgress:
    ret_class = progress.review_return_class or progress.curriculum_class or "foundations"
    ret_lesson = progress.review_return_lesson or 2
    progress.review_skill = None
    progress.review_return_lesson = None
    progress.review_return_class = None
    return goto_position(
        progress, class_id=ret_class, lesson_number=ret_lesson
    )


def navigate_step(
    progress: StudentProgress,
    *,
    class_delta: int = 0,
    lesson_delta: int = 0,
) -> StudentProgress:
    """Move ±1 class or ±1 lesson within current class."""
    cls = get_class(progress.curriculum_class or "foundations") or CLASSES[0]
    class_ids = [c.id for c in CLASSES]
    ci = class_ids.index(cls.id) if cls.id in class_ids else 0

    if class_delta:
        ci = max(0, min(len(class_ids) - 1, ci + class_delta))
        # Stay on the lesson you were on. Jumping between whole classes is
        # changing the subject, not restarting it: someone working from
        # memory on one pattern wants the next pattern from memory too.
        # goto_position clamps, so a shorter class lands on its last lesson.
        # Stepping *past* a lesson end is different and still rolls into
        # lesson 1 of the next class, further down.
        return goto_position(
            progress,
            class_id=class_ids[ci],
            lesson_number=int(progress.curriculum_lesson or 1),
        )

    lesson_n = int(progress.curriculum_lesson or 1)
    lessons = cls.lessons
    li = max(0, min(len(lessons) - 1, lesson_n - 1 + lesson_delta))
    # Cross class boundaries when stepping past lesson ends
    if lesson_delta > 0 and lesson_n >= len(lessons):
        if ci < len(class_ids) - 1:
            return goto_position(progress, class_id=class_ids[ci + 1], lesson_number=1)
        return progress
    if lesson_delta < 0 and lesson_n <= 1:
        if ci > 0:
            prev = get_class(class_ids[ci - 1])
            last = len(prev.lessons) if prev else 1
            return goto_position(
                progress, class_id=class_ids[ci - 1], lesson_number=last
            )
        return progress

    return goto_position(progress, lesson_number=li + 1)


def catalog_tree() -> list[dict]:
    return catalog_payload()
