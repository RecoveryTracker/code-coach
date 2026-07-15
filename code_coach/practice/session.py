"""
Pick the next drill from mode + coach level, and score student code.
"""

from __future__ import annotations

import random
from typing import Any, Literal

from code_coach.progress.store import StudentProgress
from code_coach.skills.catalog import get_skill, list_skills
from code_coach.skills.drills import DRILLS, Drill, get_drill, list_drills

CoachStyle = Literal["dictation", "vocabulary"]


def _completion_count(progress: StudentProgress, drill_id: str) -> int:
    rec = progress.completed_drills.get(drill_id)
    return rec.count if rec else 0


def coach_style_for(level: int) -> CoachStyle:
    return "dictation" if level <= 1 else "vocabulary"


def _progressive_pool() -> list[Drill]:
    return sorted(
        [d for d in DRILLS if d.in_progressive],
        key=lambda d: (d.path_order, d.id),
    )


def _filter_pool(progress: StudentProgress) -> list[Drill]:
    """Skill / reps practice: keep content easy while learner is on coach L1–L2."""
    skills = progress.selected_skills or None
    # Coach levels 1–2 → content difficulty 1–2 only
    max_d = 2 if progress.coach_level <= 2 else 5
    return list_drills(skills=skills, min_difficulty=1, max_difficulty=max_d)


def pick_next_drill(
    progress: StudentProgress,
    *,
    prefer_id: str | None = None,
    rng: random.Random | None = None,
) -> Drill | None:
    rng = rng or random.Random()
    mode = progress.mode

    # Resume unfinished current only
    if prefer_id:
        stuck = get_drill(prefer_id)
        if stuck and _completion_count(progress, prefer_id) == 0:
            return stuck

    if mode == "progressive":
        ordered = _progressive_pool()
        for d in ordered:
            if _completion_count(progress, d.id) == 0:
                return d
        if not ordered:
            ordered = sorted(DRILLS, key=lambda d: d.path_order)
        return min(
            ordered,
            key=lambda d: (_completion_count(progress, d.id), d.path_order),
        )

    pool = _filter_pool(progress)
    if not pool:
        skills = progress.selected_skills or None
        pool = list_drills(skills=skills, max_difficulty=2)
    if not pool:
        pool = list(DRILLS)

    if mode == "random":
        unfinished = [d for d in pool if _completion_count(progress, d.id) == 0]
        return rng.choice(unfinished or pool)

    if mode == "reps":
        simple = [d for d in pool if d.difficulty <= 2] or pool
        # Prefer micro-reps over full lessons for pure typing practice
        micros = [d for d in simple if not d.id.startswith("lesson-")] or simple
        micros.sort(
            key=lambda d: (
                _completion_count(progress, d.id),
                d.difficulty,
                d.path_order,
            )
        )
        top = micros[: min(5, len(micros))]
        return rng.choice(top)

    # skill mode
    unfinished = [d for d in pool if _completion_count(progress, d.id) == 0]
    if unfinished:
        unfinished.sort(key=lambda d: (d.difficulty, d.path_order, d.id))
        return unfinished[0]
    pool.sort(
        key=lambda d: (_completion_count(progress, d.id), d.difficulty, d.path_order)
    )
    return pool[0]


def evaluate_drill(
    drill: Drill,
    code: str,
    *,
    coach_level: int = 1,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = 0,
    ran: bool = False,
    exercise_index: int | None = None,
) -> dict[str, Any]:
    from code_coach.practice.adapt import build_adaptation

    # Type-along (dictation) drills score each line on its own: the student is
    # copying independent exercises, so line N must not be gated on lines 0..N-1
    # still living in the buffer (they may have moved the caret, changed
    # difficulty, or skipped with the Exercise arrows). Build lessons stay
    # sequential — a later construct genuinely depends on the earlier one.
    is_dictation = "dictation" in (drill.tags or [])

    def _norm_out(text: str) -> str:
        return "\n".join(
            ln.rstrip() for ln in (text or "").strip().splitlines()
        )

    def _output_matches(step: Any) -> bool:
        exp = getattr(step, "expect_output", None)
        if exp is None:
            return True
        return ran and exit_code == 0 and _norm_out(stdout) == _norm_out(exp)

    def _step_ok(step: Any) -> bool:
        # Structure first; when the goal pins output, a Run must confirm it.
        return bool(step.check(code)) and _output_matches(step)

    checks: list[dict[str, Any]] = []
    next_step = None
    passed = 0
    blocked = False
    for step in drill.steps:
        if is_dictation:
            ok = _step_ok(step)
            if not ok and next_step is None:
                next_step = step
        elif blocked:
            ok = False
        else:
            ok = _step_ok(step)
            if not ok:
                blocked = True
                next_step = step
        checks.append({"id": step.id, "label": step.label, "passed": ok})
        if ok:
            passed += 1

    complete = next_step is None and passed == len(drill.steps)
    if not complete and next_step is None:
        # all checks true
        complete = True
    style = coach_style_for(coach_level)

    # Coach feedback focuses on the exercise the student is actually looking
    # at (the client sends its index). Falls back to the first unpassed step.
    focus_step = next_step
    if drill.steps and exercise_index is not None:
        idx = max(0, min(len(drill.steps) - 1, int(exercise_index)))
        focus_step = drill.steps[idx]

    # Build exercises: per-requirement ✓/✗ so the student sees exactly which
    # piece of the goal is still missing.
    requirements = None
    if focus_step is not None and getattr(focus_step, "requirements", None):
        requirements = [
            {"label": label, "passed": bool(fn(code))}
            for label, fn in focus_step.requirements
        ]
    # Output-pinned goals get a checklist row too: it only turns ✓ after a
    # Run whose stdout matches.
    if focus_step is not None and getattr(focus_step, "expect_output", None):
        exp = focus_step.expect_output
        pretty = ", ".join(exp.strip().splitlines())
        matched = _output_matches(focus_step)
        label = f"running it prints exactly: {pretty}"
        if not ran:
            label += "  (press Run ⌘⏎)"
        requirements = (requirements or []) + [
            {"label": label, "passed": matched}
        ]

    next_label = None if complete else next_step.label
    next_concept = None if complete else next_step.concept
    next_why = None if complete else next_step.why
    next_hint = None if complete else next_step.hint
    next_example = None if complete else next_step.example
    next_vocab = None if complete or not next_step else _vocab_word(next_step)

    adapt = build_adaptation(
        code=code,
        step=focus_step,
        style=style,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        ran=ran,
        passed=passed,
        total=len(drill.steps),
        complete=complete,
        requirements=requirements,
    )

    return {
        "drill_id": drill.id,
        "title": drill.title,
        "skill": drill.skill,
        "difficulty": drill.difficulty,
        "prompt": drill.prompt,
        "starter": drill.starter,
        "checks": checks,
        "passed": passed,
        "total": len(drill.steps),
        "complete": complete,
        "coach_level": coach_level,
        "coach_style": style,
        "next_label": next_label,
        "next_concept": next_concept,
        "next_why": next_why,
        "next_hint": next_hint,
        "next_example": next_example,
        "next_suggest": next_example,
        "next_vocab": next_vocab,
        "accepts_own_values": True,
        "observation": adapt["observation"],
        "guidance": adapt["guidance"],
        "adapt_example": adapt["example"],
        "tone": adapt["tone"],
        "status": adapt.get("status"),
        "requirements": requirements,
    }


def _vocab_word(step: Any) -> str:
    """Pick a memorable keyword for vocabulary mode."""
    text = f"{step.concept} {step.example}"
    for word in (
        "print",
        "variable",
        "string",
        "number",
        "if",
        "else",
        "for",
        "while",
        "list",
        "dict",
        "def",
        "return",
        "append",
        "range",
    ):
        if word in text.lower():
            return word
    # fallback: first word of label
    return step.label.split()[0].strip("().")


REVIEW_DUE_AFTER_DAYS = 3


def _review_due(progress: StudentProgress) -> list[dict[str, Any]]:
    """Skills practiced before but not recently — light spaced repetition.
    A skill is 'due' when its most recent completion is older than
    REVIEW_DUE_AFTER_DAYS."""
    from datetime import datetime, timezone

    last_by_skill: dict[str, str] = {}
    for drill_id, rec in progress.completed_drills.items():
        if not rec.last_at:
            continue
        d = get_drill(drill_id)
        if d is None:
            continue
        prev = last_by_skill.get(d.skill)
        if prev is None or rec.last_at > prev:
            last_by_skill[d.skill] = rec.last_at

    now = datetime.now(timezone.utc)
    due: list[dict[str, Any]] = []
    for skill_id, last_at in last_by_skill.items():
        try:
            then = datetime.fromisoformat(last_at)
        except ValueError:
            continue
        days = (now - then).days
        if days >= REVIEW_DUE_AFTER_DAYS:
            s = get_skill(skill_id)
            due.append(
                {
                    "skill_id": skill_id,
                    "name": s.name if s else skill_id,
                    "days": days,
                }
            )
    due.sort(key=lambda x: -x["days"])
    return due


def progress_summary(progress: StudentProgress) -> dict[str, Any]:
    skills = list_skills()
    by_skill: dict[str, dict[str, int]] = {}
    for s in skills:
        skill_drills = [d for d in DRILLS if d.skill == s.id]
        done = sum(1 for d in skill_drills if _completion_count(progress, d.id) > 0)
        by_skill[s.id] = {
            "name": s.name,
            "done": done,
            "total": len(skill_drills),
            "xp": int(progress.skill_xp.get(s.id, 0)),
        }

    total_drills = len(DRILLS)
    unique_done = sum(1 for d in DRILLS if _completion_count(progress, d.id) > 0)
    return {
        "mode": progress.mode,
        "coach_level": progress.coach_level,
        "difficulty": progress.coach_level,  # alias
        "selected_skills": list(progress.selected_skills),
        "total_completes": progress.total_completes,
        "unique_drills_done": unique_done,
        "total_drills": total_drills,
        "current_drill_id": progress.current_drill_id,
        "by_skill": by_skill,
        "updated_at": progress.updated_at,
        "curriculum_class": getattr(progress, "curriculum_class", "foundations")
        or "foundations",
        "curriculum_lesson": int(getattr(progress, "curriculum_lesson", 1) or 1),
        "review_skill": getattr(progress, "review_skill", None),
        "dictation_level": max(
            1, min(5, int(getattr(progress, "dictation_level", 1) or 1))
        ),
        # API-stable aliases (per-class dicts are the stored truth since v3)
        "class1_lines_done": progress.lines_for("foundations"),
        "class1_batch": progress.batch_for("foundations"),
        # Per-class endless type-along lifetime lines (progress panel)
        "dictation_lines": dict(progress.dictation_lines),
        # Light spaced repetition: skills practiced before, but not recently
        "review_due": _review_due(progress),
    }


def mark_drill_complete(progress: StudentProgress, drill: Drill) -> None:
    from datetime import datetime, timezone

    from code_coach.progress.store import DrillRecord

    rec = progress.completed_drills.get(drill.id) or DrillRecord()
    rec.count += 1
    rec.last_at = datetime.now(timezone.utc).isoformat()
    progress.completed_drills[drill.id] = rec
    progress.total_completes += 1
    progress.skill_xp[drill.skill] = int(progress.skill_xp.get(drill.skill, 0)) + max(
        1, drill.difficulty
    )
    progress.current_drill_id = None
