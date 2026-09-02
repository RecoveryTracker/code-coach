"""
Local JSON progress — survives app restarts.

Default path: ~/.code_coach/student_progress.json
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Literal

Mode = Literal["progressive", "skill", "random", "reps"]
# How the coach talks — not a content filter slider.
# 1 = type-along (dictation)  2 = vocabulary  (3+ later: patterns)
CoachLevel = int

DEFAULT_PATH = Path.home() / ".code_coach" / "student_progress.json"

# A workbook answer is a handful of lines. This is only here so a paste
# of something enormous cannot quietly turn the progress file into one.
MAX_ANSWER_CHARS = 4000

# The one store the app is using. Everything that needs to know about the
# student reads it through here, so there is a single answer rather than one
# per caller that happens to construct its own.
_ACTIVE: "ProgressStore | None" = None


def active_store() -> "ProgressStore":
    """The store this process is working with, made on first use."""
    global _ACTIVE
    if _ACTIVE is None:
        _ACTIVE = ProgressStore()
    return _ACTIVE


def use_store(store: "ProgressStore") -> "ProgressStore":
    """Point the app at a different store, and hand back the previous one.

    Tests swap in a temporary store this way; returning the old one means
    they can put it back rather than leaving the process pointed somewhere
    unexpected.
    """
    global _ACTIVE
    previous = active_store()
    _ACTIVE = store
    return previous


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DrillRecord:
    count: int = 0
    last_at: str | None = None


@dataclass
class StudentProgress:
    version: int = 3
    mode: Mode = "progressive"
    # Coach style: 1 type-along, 2 vocabulary (max 2 for now).
    # (v2 also stored a `difficulty` alias of this — dropped in v3; the API
    # still serves a computed alias for older clients.)
    coach_level: CoachLevel = 1
    selected_skills: list[str] = field(default_factory=list)
    completed_drills: dict[str, DrillRecord] = field(default_factory=dict)
    completed_waypoints: dict[str, list[str]] = field(default_factory=dict)
    current_drill_id: str | None = None
    total_completes: int = 0
    skill_xp: dict[str, int] = field(default_factory=dict)
    # Endless Lesson-1 type-along, per class: how many windows loaded and how
    # many lines finished (lifetime). v2 kept these for foundations only, as
    # class1_batch / class1_lines_done — migrated in from_dict.
    dictation_batches: dict[str, int] = field(default_factory=dict)
    dictation_lines: dict[str, int] = field(default_factory=dict)
    # User-controlled type-along difficulty: 1 single lines … 5 functions
    dictation_level: int = 1
    # Curriculum position: class id + lesson number
    curriculum_class: str = "foundations"
    curriculum_lesson: int = 1
    # Supporting-lesson detour
    review_skill: str | None = None
    review_return_lesson: int | None = None
    review_return_class: str | None = None
    # Current exercise index (optional; client also tracks)
    exercise_index: int = 0
    # Which language the drills are in. Only Python is implemented; see
    # code_coach/languages.py for what a second one needs.
    language: str = "python"
    # Workbook exercises finished, keyed by language. Solving "print the
    # numbers 1 to 5" in Python does not mean you can do it in Rust, so these
    # are counted separately rather than being one shared tick.
    workbook_done: dict[str, list[str]] = field(default_factory=dict)
    # The page you were last working on, per language, so the workbook opens
    # where you left it rather than back at page 1.
    workbook_page: dict[str, str] = field(default_factory=dict)
    # The code you wrote for each exercise you got right: language, then
    # exercise id. Your own answers are the one thing in this app you cannot
    # get back if it is not kept.
    workbook_answers: dict[str, dict[str, str]] = field(default_factory=dict)
    updated_at: str = field(default_factory=_now)

    # ── Per-class endless counters ──
    def batch_for(self, class_id: str) -> int:
        return int(self.dictation_batches.get(class_id, 0) or 0)

    def lines_for(self, class_id: str) -> int:
        return int(self.dictation_lines.get(class_id, 0) or 0)

    def set_batch(self, class_id: str, batch: int) -> int:
        """Land on a specific window. Used when a lesson links to a problem
        that is not in the window you happen to be on."""
        self.dictation_batches[class_id] = max(0, int(batch))
        return self.dictation_batches[class_id]

    def bump_batch(self, class_id: str) -> int:
        nxt = self.batch_for(class_id) + 1
        self.dictation_batches[class_id] = nxt
        return nxt

    def add_lines(self, class_id: str, n: int) -> int:
        total = self.lines_for(class_id) + int(n)
        self.dictation_lines[class_id] = total
        return total

    # ── Workbook ──
    def workbook_for(self, language: str) -> list[str]:
        return list(self.workbook_done.get(language, []))

    def mark_workbook(self, language: str, exercise_id: str) -> bool:
        """Record a solved exercise. True when it is the first time."""
        done = self.workbook_done.setdefault(language, [])
        if exercise_id in done:
            return False
        done.append(exercise_id)
        return True

    def remember_workbook_answer(
        self, language: str, exercise_id: str, code: str
    ) -> None:
        """Keep what they wrote. A later correct answer replaces an earlier
        one — it is the version they would want to look back at."""
        # Bounded so a pasted novel cannot bloat the file. Nothing on these
        # pages is longer than a few lines.
        self.workbook_answers.setdefault(language, {})[exercise_id] = code[
            :MAX_ANSWER_CHARS
        ]

    def workbook_answers_for(self, language: str) -> dict[str, str]:
        return dict(self.workbook_answers.get(language, {}))

    def workbook_page_for(self, language: str) -> str:
        return self.workbook_page.get(language, "")

    def set_workbook_page(self, language: str, page_id: str) -> None:
        self.workbook_page[language] = page_id

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> StudentProgress:
        drills_raw = raw.get("completed_drills") or {}
        completed_drills: dict[str, DrillRecord] = {}
        for k, v in drills_raw.items():
            if isinstance(v, dict):
                completed_drills[k] = DrillRecord(
                    count=int(v.get("count", 0)),
                    last_at=v.get("last_at"),
                )
            else:
                completed_drills[k] = DrillRecord(count=int(v), last_at=None)

        mode = raw.get("mode", "progressive")
        if mode not in ("progressive", "skill", "random", "reps"):
            mode = "progressive"

        # Prefer coach_level; fall back to old difficulty field (v2 alias)
        if "coach_level" in raw:
            coach_level = int(raw["coach_level"])
        else:
            coach_level = int(raw.get("difficulty", 1))
        # Focus band for now: only 1–2
        coach_level = max(1, min(2, coach_level))

        # v3 per-class counters; migrate v2's foundations-only fields.
        batches = {
            str(k): int(v)
            for k, v in (raw.get("dictation_batches") or {}).items()
        }
        lines = {
            str(k): int(v)
            for k, v in (raw.get("dictation_lines") or {}).items()
        }
        if not batches and raw.get("class1_batch"):
            batches["foundations"] = int(raw["class1_batch"])
        if not lines and raw.get("class1_lines_done"):
            lines["foundations"] = int(raw["class1_lines_done"])

        return cls(
            version=3,
            mode=mode,  # type: ignore[arg-type]
            coach_level=coach_level,
            selected_skills=list(raw.get("selected_skills") or []),
            completed_drills=completed_drills,
            completed_waypoints={
                str(k): list(v)
                for k, v in (raw.get("completed_waypoints") or {}).items()
            },
            current_drill_id=raw.get("current_drill_id"),
            total_completes=int(raw.get("total_completes", 0)),
            skill_xp={str(k): int(v) for k, v in (raw.get("skill_xp") or {}).items()},
            dictation_batches=batches,
            dictation_lines=lines,
            dictation_level=max(1, min(5, int(raw.get("dictation_level", 1)))),
            curriculum_class=str(raw.get("curriculum_class") or "foundations"),
            curriculum_lesson=int(raw.get("curriculum_lesson") or 1),
            review_skill=raw.get("review_skill"),
            review_return_lesson=(
                int(raw["review_return_lesson"])
                if raw.get("review_return_lesson") is not None
                else None
            ),
            review_return_class=raw.get("review_return_class"),
            exercise_index=int(raw.get("exercise_index") or 0),
            # Unknown ids fall back to Python rather than failing to load.
            language=_known_language(raw.get("language")),
            workbook_done={
                str(k): [str(x) for x in (v or [])]
                for k, v in (raw.get("workbook_done") or {}).items()
            },
            workbook_page={
                str(k): str(v)
                for k, v in (raw.get("workbook_page") or {}).items()
            },
            workbook_answers={
                str(k): {
                    str(ex): str(code)[:MAX_ANSWER_CHARS]
                    for ex, code in (v or {}).items()
                }
                for k, v in (raw.get("workbook_answers") or {}).items()
            },
            updated_at=str(raw.get("updated_at") or _now()),
        )


# Windows refuses to replace a file that another handle has open, and reports
# it as a permission error rather than waiting. The app opens this file on
# nearly every request, so two that arrive together are enough: one saves
# while the other reads, and the save raises.
#
# The overlap lasts microseconds. Retrying briefly is the whole fix; anything
# still failing after that is a real permissions problem and is raised, since
# a save that quietly does not happen is worse than an error that says so.
_REPLACE_ATTEMPTS = 12
_REPLACE_PAUSE = 0.01


def _replace_with_retry(source: str, target: Path) -> None:
    for attempt in range(_REPLACE_ATTEMPTS):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == _REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(_REPLACE_PAUSE)


def _known_language(value: object) -> str:
    """A stored language id, or Python. Imported lazily so the progress store
    stays free of app-level imports."""
    from code_coach.languages import DEFAULT_LANGUAGE, get_language

    if not value:
        return DEFAULT_LANGUAGE
    return get_language(str(value)).id


def default_progress() -> StudentProgress:
    return StudentProgress()


class ProgressStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or DEFAULT_PATH
        # One reader or one writer at a time. The server answers requests on a
        # thread pool and the UI fires several at once on load, so without
        # this a save could land while another thread had the file open —
        # which on Windows is a permission error, not a wait, and surfaced as
        # a 500 on startup.
        #
        # Reentrant because a caller holding it may go on to save what it just
        # loaded, and that should not deadlock.
        self._lock = threading.RLock()

    def load(self) -> StudentProgress:
        with self._lock:
            return self._load()

    def _load(self) -> StudentProgress:
        if not self.path.exists():
            return default_progress()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return default_progress()
            return StudentProgress.from_dict(raw)
        except (OSError, json.JSONDecodeError):
            return default_progress()

    def save(self, progress: StudentProgress) -> StudentProgress:
        with self._lock:
            return self._save(progress)

    def _save(self, progress: StudentProgress) -> StudentProgress:
        progress.updated_at = _now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(progress.to_dict(), indent=2, sort_keys=True) + "\n"
        # Unique temp name avoids races when two requests save at once
        # (shared student_progress.tmp was causing FileNotFoundError → 500).
        fd, tmp_name = tempfile.mkstemp(
            prefix="student_progress_",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(payload)
            _replace_with_retry(tmp_name, self.path)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        return progress

    def update(self, mutator) -> StudentProgress:
        progress = self.load()
        mutator(progress)
        return self.save(progress)
