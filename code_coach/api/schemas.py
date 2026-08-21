"""Request/response models for the Code Coach API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Mode = Literal["progressive", "skill", "random", "reps"]
CoachStyle = Literal["dictation", "vocabulary"]


class CheckItem(BaseModel):
    id: str | None = None
    label: str
    passed: bool


class SupportLinkInfo(BaseModel):
    skill_id: str
    label: str
    lesson_title: str = "Foundations · Lesson 1"


class ProblemBriefInfo(BaseModel):
    """The question behind the line you're typing, restated in our words."""

    number: int
    title: str
    difficulty: str
    statement: str
    examples: list[str] = []
    note: str = ""
    idea: str = ""
    complexity: str = ""
    url: str = ""
    # Full reference solution, for "show answer" / "check my work".
    solution: str = ""


class PatternLessonInfo(BaseModel):
    """The reading that makes a pattern's problems make sense."""

    id: str
    name: str
    summary: str
    when: str
    template: str
    steps: list[str] = []
    pitfalls: list[str] = []


class StudyInfo(BaseModel):
    problem: ProblemBriefInfo | None = None
    lesson: PatternLessonInfo | None = None


class WaypointInfo(BaseModel):
    id: str
    label: str
    tip: str | None = None
    keyboard_tip: str | None = None
    hint_lines: list[str] = []
    supports: list[SupportLinkInfo] = []
    kind: str = "dictation"  # dictation | build
    # Present only for LeetCode exercises — powers the Study panel.
    study: StudyInfo | None = None


class ChatRequest(BaseModel):
    message: str = ""


class ChatResponse(BaseModel):
    reply: str


class ExplainRequest(BaseModel):
    code: str = ""


class ExplainLine(BaseModel):
    line: int
    depth: int = 0
    source: str = ""
    text: str


class ExplainResponse(BaseModel):
    ok: bool = True
    summary: str
    lines: list[ExplainLine] = []
    output_notes: list[str] = []
    error_note: str | None = None


class GotoLessonRequest(BaseModel):
    lesson_number: int | None = None
    class_id: str | None = None
    # relative step: lesson_delta ±1 or class_delta ±1
    lesson_delta: int | None = None
    class_delta: int | None = None


class ReviewRequest(BaseModel):
    skill_id: str


class CurriculumClassInfo(BaseModel):
    id: str
    name: str
    description: str
    lessons: list[dict]


class NavigateRequest(BaseModel):
    """Free navigation across class / lesson / exercise."""
    class_id: str | None = None
    lesson_number: int | None = None
    exercise_index: int | None = None  # 0-based; client mainly owns this
    class_delta: int | None = None
    lesson_delta: int | None = None
    exercise_delta: int | None = None


class HealthResponse(BaseModel):
    ok: bool
    version: str


class SkillInfo(BaseModel):
    id: str
    name: str
    description: str
    order: int
    base_difficulty: int


class LanguageInfo(BaseModel):
    id: str
    name: str
    # Monaco's syntax-highlighting id.
    monaco: str
    extension: str
    available: bool
    # Why it isn't selectable yet.
    note: str = ""
    # Which pieces exist: runner / checks / bank / tracer.
    ready: list[str] = []


class ProgressSettingsUpdate(BaseModel):
    mode: Mode | None = None
    coach_level: int | None = Field(default=None, ge=1, le=2)
    # alias accepted for older clients
    difficulty: int | None = Field(default=None, ge=1, le=5)
    selected_skills: list[str] | None = None
    # Foundations type-along difficulty: 1 single lines … 5 functions
    dictation_level: int | None = Field(default=None, ge=1, le=5)
    # Only languages marked available are accepted.
    language: str | None = None


class ReviewDueItem(BaseModel):
    skill_id: str
    name: str
    days: int


class ProgressResponse(BaseModel):
    mode: Mode
    coach_level: int
    difficulty: int  # alias of coach_level
    selected_skills: list[str]
    total_completes: int
    unique_drills_done: int
    total_drills: int
    current_drill_id: str | None
    by_skill: dict[str, Any]
    updated_at: str
    curriculum_class: str = "foundations"
    curriculum_lesson: int = 1
    review_skill: str | None = None
    dictation_level: int = 1
    language: str = "python"
    class1_lines_done: int = 0
    class1_batch: int = 0
    # Per-class endless type-along lifetime lines
    dictation_lines: dict[str, int] = {}
    # Skills practiced before but not recently (light spaced repetition)
    review_due: list[ReviewDueItem] = []


class PracticeSession(BaseModel):
    drill_id: str
    title: str
    skill: str
    skill_name: str
    difficulty: int
    prompt: str
    starter: str
    steps: list[WaypointInfo]
    mode: Mode
    coach_level: int
    coach_style: CoachStyle
    meter: int  # alias coach_level
    progress: ProgressResponse
    is_lesson: bool = False
    # Curriculum labels
    class_id: str = "foundations"
    class_number: int = 1
    class_name: str = "Foundations"
    lesson_number: int = 1
    lesson_role: str = "dictation"  # dictation | build | review
    is_review: bool = False
    can_go_lesson_2: bool = True
    # Catalog for nav UI
    curriculum: list[dict] = []
    exercise_count: int = 0
    # Everything this class holds, not just the current window of 8. Without
    # it the counter resets to 1/8 each window and progress looks like a loop.
    class_total: int = 0
    # How far into that total the current window starts.
    class_position: int = 0
    # Endless Foundations type-along
    endless: bool = False
    dictation_level: int = 1
    dictation_level_label: str = "Single lines"
    lines_done: int = 0
    # Language the drill is written in, so the editor highlights it correctly.
    language: str = "python"
    editor_language: str = "python"
    # "Watch it run" needs a tracer, and "Explain my code" reads the code with
    # Python's `ast`. Only Python has either. Without these the buttons are
    # offered everywhere and fail with a parse error about Python syntax.
    can_visualize: bool = True
    can_explain: bool = True


class DrillEvaluateRequest(BaseModel):
    drill_id: str
    code: str = ""
    run: bool = False
    # Which exercise the student is currently on (0-based, client-owned).
    # Focuses the coach's "type this line" message on that line, so the
    # banner never references a different line than the exercise box.
    exercise_index: int | None = None


class CheckAnswerRequest(BaseModel):
    """Compare the student's own attempt against a problem's real solution."""

    code: str = ""
    pattern_id: str | None = None
    problem_number: int | None = None


class CheckAnswerResponse(BaseModel):
    ok: bool = True
    matches: bool = False
    # Where the first difference is, in plain language ("" when it matches).
    note: str = ""
    solution: str = ""
    title: str = ""


class VisualizeRequest(BaseModel):
    code: str = ""
    # Appended before running. Blank means "work one out from the problem's
    # examples" — a LeetCode answer only defines a function, so without a call
    # there is nothing to watch.
    call: str = ""
    pattern_id: str | None = None
    problem_number: int | None = None


class VisualizeResponse(BaseModel):
    ok: bool = True
    steps: list[dict] = []
    truncated: bool = False
    stdout: str = ""
    stderr: str = ""
    error: str | None = None
    # The call actually used, so the UI can show and let you edit it.
    call: str = ""


# ── Typing trainer ──────────────────────────────────────────


class TypingModeInfo(BaseModel):
    id: str
    name: str
    description: str
    hidden: bool
    by_name: bool


class TypingSectionInfo(BaseModel):
    id: str
    name: str
    description: str
    modes: list[TypingModeInfo]


class TypingThemeInfo(BaseModel):
    id: str
    name: str
    description: str
    # Which modes it can drive, so the picker can grey out the rest.
    has_words: bool
    has_passages: bool


class TypingCatalogResponse(BaseModel):
    sections: list[TypingSectionInfo]
    # What the words and lines are about — a separate choice from which keys
    # you're drilling.
    themes: list[TypingThemeInfo]
    # The layout, so the on-screen keyboard is drawn from the same model the
    # drills are generated from.
    keyboard: list[list[dict[str, Any]]]
    fingers: dict[str, str]


class TypingTargetInfo(BaseModel):
    text: str
    prompt: str
    shift: bool
    note: str
    finger: str


class TypingDrillResponse(BaseModel):
    id: str
    section: str
    section_name: str
    mode: str
    mode_name: str
    theme: str
    theme_name: str
    description: str
    hidden: bool
    scoring: Literal["reaction", "wpm"]
    targets: list[TypingTargetInfo]


class TypingFingerInfo(BaseModel):
    finger: str
    name: str
    hand: Literal["left", "right"]
    home: str
    keys: list[str]
    note: str


class TypingHomeKeyInfo(BaseModel):
    char: str
    finger: str
    name: str
    # The two keys with a raised bump, which is how you find home by feel.
    anchor: bool


class TypingArticle(BaseModel):
    title: str
    body: str


class TypingQuestion(BaseModel):
    question: str
    answer: str


class TypingGuideResponse(BaseModel):
    fingers: list[TypingFingerInfo]
    home_row: list[TypingHomeKeyInfo]
    tips: list[TypingArticle]
    faq: list[TypingQuestion]


class TypingLessonInfo(BaseModel):
    number: int
    title: str
    why: str
    section: str
    mode: str
    theme: str
    section_name: str
    mode_name: str
    theme_name: str
    target_wpm: int
    target_accuracy: int
    done: bool
    best_wpm: int
    best_accuracy: int
    runs: int


class TypingCourseResponse(BaseModel):
    lessons: list[TypingLessonInfo]
    total: int
    done: int
    # The lesson to carry on with. Nothing is locked — a lesson you can't
    # reach is a lesson you can't practise.
    current: int


class TypingRecordInfo(BaseModel):
    section: str
    mode: str
    section_name: str
    mode_name: str
    best_wpm: int
    best_accuracy: int
    best_reaction_ms: int
    best_streak: int
    runs: int
    total_keys: int
    last_wpm: int
    last_accuracy: int
    updated: str


class TypingRunRequest(BaseModel):
    section: str
    mode: str
    wpm: int = Field(ge=0, le=100000)
    accuracy: int = Field(ge=0, le=100)
    reaction_ms: int = Field(ge=0, le=600000)
    streak: int = Field(ge=0)
    keystrokes: int = Field(ge=0)


class TypingRunResponse(BaseModel):
    record: TypingRecordInfo
    # Which of the four numbers this run beat, so the UI can call it out.
    beat_wpm: bool
    beat_accuracy: bool
    beat_reaction: bool
    beat_streak: bool


class RequirementItem(BaseModel):
    label: str
    passed: bool


class DrillEvaluateResponse(BaseModel):
    drill_id: str
    title: str
    skill: str
    difficulty: int
    prompt: str
    code: str
    stdout: str
    stderr: str
    exit_code: int
    ran: bool
    checks: list[CheckItem]
    passed: int
    total: int
    complete: bool
    coach_level: int = 1
    coach_style: CoachStyle = "dictation"
    next_label: str | None
    next_concept: str | None = None
    next_why: str | None = None
    next_hint: str | None = None
    next_example: str | None = None
    next_suggest: str | None = None
    next_vocab: str | None = None
    accepts_own_values: bool = True
    observation: str | None = None
    guidance: str | None = None
    adapt_example: str | None = None
    tone: str | None = None
    status: str | None = None
    just_completed: bool = False
    progress: ProgressResponse | None = None
    # Build exercises: the goal's pieces with live pass/fail (✓/✗ checklist)
    requirements: list[RequirementItem] | None = None
