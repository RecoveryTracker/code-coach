"""
FastAPI server for the Code Coach IAE.

  uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from code_coach import __version__
from code_coach.api.schemas import (
    ChatRequest,
    ChatResponse,
    CheckAnswerRequest,
    CheckAnswerResponse,
    CheckItem,
    DrillEvaluateRequest,
    DrillEvaluateResponse,
    ExplainRequest,
    ExplainResponse,
    HealthResponse,
    KataCaseResult,
    KataCheckRequest,
    KataCheckResponse,
    PracticeSession,
    CssCheckRequest,
    CssCheckResponse,
    DrillCheckRequest,
    DrillCheckResponse,
    ErrorCheckRequest,
    ErrorCheckResponse,
    TraceCheckRequest,
    TraceCheckResponse,
    MagnetCheckRequest,
    MagnetCheckResponse,
    PredictCheckRequest,
    PredictCheckResponse,
    ProgressResponse,
    ProgressSettingsUpdate,
    LanguageInfo,
    SkillInfo,
    StudyInfo,
    VisualizeRequest,
    VisualizeResponse,
    WaypointInfo,
    WorkbookCheckRequest,
    WorkbookDraftRequest,
    WorkbookCheckResponse,
)
from code_coach.leetcode.bank import study_payload as leetcode_study_payload
from code_coach.curriculum.catalog import (
    catalog_payload,
    hint_lines_for_step,
    supports_for_build_step,
)
from code_coach.curriculum.runtime import (
    back_from_review,
    enter_review,
    get_active_drill,
    goto_lesson,
    goto_position,
    lesson_meta_for_drill,
    navigate_step,
)
from code_coach.dictation.bank import chat_reply
from code_coach.engine import run_code
from code_coach.practice.session import (
    coach_style_for,
    evaluate_drill,
    mark_drill_complete,
    progress_summary,
)
from code_coach.progress.store import active_store, StudentProgress
from code_coach.skills.catalog import get_skill, list_skills
from code_coach.skills.drills import get_drill, set_class1_batch
from code_coach.api.schemas import (
    GotoLessonRequest,
    GotoProblemRequest,
    HintInfo,
    HintsRequest,
    HintsResponse,
    NavigateRequest,
    ReviewRequest,
    SupportLinkInfo,
    TypingCatalogResponse,
    TypingCourseResponse,
    TypingDrillResponse,
    TypingGuideResponse,
    TypingRecordInfo,
    TypingRunRequest,
    TypingRunResponse,
    TypingModeInfo,
    TypingSectionInfo,
    TypingTargetInfo,
    BugHuntCauseRequest,
    BugHuntFixRequest,
    BugHuntFixResponse,
    BugHuntLineRequest,
    BugHuntStepResponse,
    BugHuntTryRequest,
    BugHuntTryResponse,
    CaseAnswerRequest,
    CaseAnswerResponse,
    CaseQueryRequest,
    CaseQueryResponse,
    PuzzleCheckRequest,
    PuzzleCheckResponse,
    RegexCheckRequest,
    RegexCheckResponse,
    RegexRow,
    TypingShapeInfo,
    TypingShapesResponse,
    TypingThemeInfo,
)
from code_coach.typing.blends import split_id as split_theme_id
from code_coach.typing.drills import (
    MODES_BY_ID as TYPING_MODES_BY_ID,
    SECTIONS_BY_ID as TYPING_SECTIONS_BY_ID,
    THEMES_BY_ID as TYPING_THEMES_BY_ID,
    build_drill as build_typing_drill,
    catalog as typing_sections,
    teach_languages as typing_teach_languages,
    theme_catalog as typing_themes,
    theme_name_for,
    shape_catalog as typing_shape_catalog,
)
from code_coach.typing.guide import guide_payload
from code_coach.typing.records import Record, RecordStore
from code_coach.typing.keys import (
    FINGER_NAMES,
    SYMBOL_NAMES,
    finger_for,
    keyboard_payload,
)

app = FastAPI(
    title="Code Coach",
    description="Coach-first Integrated Agent Environment API",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only these hostnames may reach the API. CORS is browser-only and doesn't stop
# a DNS-rebinding attack (a malicious page whose domain resolves to 127.0.0.1):
# the browser would send that domain in the Host header, and this rejects it.
# The server executes student code, so keeping the surface to real localhost
# clients matters.
_ALLOWED_HOSTNAMES = {"127.0.0.1", "localhost", "::1"}


def host_allowed(host_header: str) -> bool:
    """True if a request's Host header is a real localhost client. An empty
    header is allowed (some probes omit it); any other hostname is rejected."""
    hostname = host_header.rsplit(":", 1)[0] if host_header else ""
    hostname = hostname.strip("[]")  # unwrap IPv6 literal
    return not hostname or hostname in _ALLOWED_HOSTNAMES


@app.middleware("http")
async def _guard_host(request: Request, call_next):
    if not host_allowed(request.headers.get("host", "")):
        return JSONResponse(
            status_code=403,
            content={"detail": "Forbidden: unexpected Host header."},
        )
    return await call_next(request)


_store = active_store()


def _progress_response() -> ProgressResponse:
    p = _store.load()
    return ProgressResponse(**progress_summary(p))


def _session_from_progress() -> PracticeSession:
    progress = _store.load()

    # A class with no material in the chosen language would hand out Python
    # exercises to type into a .dart file. Move to one that exists instead.
    from code_coach.curriculum.catalog import (
        class_available_in,
        first_class_for_language,
    )

    lang_id = getattr(progress, "language", "python") or "python"
    current_class = progress.curriculum_class or "foundations"
    if not class_available_in(current_class, lang_id):
        progress.curriculum_class = first_class_for_language(lang_id)
        progress.curriculum_lesson = 1
        progress.current_drill_id = None
        progress.review_skill = None
        _store.save(progress)

    drill = get_active_drill(progress)
    if progress.current_drill_id != drill.id:
        progress.current_drill_id = drill.id
        _store.save(progress)

    from code_coach.languages import get_language

    lang = get_language(getattr(progress, "language", None))
    skill = get_skill(drill.skill)
    level = progress.coach_level
    meta = lesson_meta_for_drill(drill.id, progress)
    role = meta["lesson_role"]

    steps: list[WaypointInfo] = []
    for i, s in enumerate(drill.steps):
        hint_lines = hint_lines_for_step(drill, i)
        raw_supports = supports_for_build_step(drill.id, i)
        supports = [SupportLinkInfo(**x) for x in raw_supports]
        kind = "build" if role == "build" else "dictation"
        raw_study = leetcode_study_payload(
            getattr(s, "pattern_id", None),
            getattr(s, "problem_number", None),
            lang.id,
        )
        steps.append(
            WaypointInfo(
                id=s.id,
                label=s.label,
                tip=getattr(s, "why", None) or getattr(s, "concept", None),
                keyboard_tip=getattr(s, "hint", None),
                hint_lines=hint_lines,
                supports=supports,
                kind=kind,
                study=StudyInfo(**raw_study) if raw_study else None,
            )
        )

    title = meta.get("display_title") or drill.title
    if role == "build":
        level_for_style = max(level, 2)
    else:
        level_for_style = 1 if role in ("dictation", "review") else level

    # Lesson 1 of every class is the endless type-along fallback layer.
    endless = int(meta.get("lesson_number") or 1) == 1 and role == "dictation"

    # How big this class really is, and where this window of 8 sits in it. The
    # window counter alone resets to 1/8 every time you load more, which reads
    # as going back to the start when you've actually moved forward.
    class_total, class_position = 0, 0
    if endless:
        from code_coach.dictation.bank import WINDOW_SIZE
        from code_coach.fundamentals.base import window_start

        class_id_now = progress.curriculum_class or "foundations"
        d_level_now = max(1, min(5, int(getattr(progress, "dictation_level", 1) or 1)))
        class_total = _class_material_total(class_id_now, lang.id, d_level_now)
        if class_total:
            # Where this window actually starts in the class, worked out the
            # same way the window itself is cut. Deriving it from `len(steps)`
            # instead was wrong for the short final window of a class, which
            # then reported itself as line 1.
            class_position = window_start(
                class_total,
                batch=progress.batch_for(class_id_now),
                count=WINDOW_SIZE,
            )
    d_level = max(1, min(5, int(getattr(progress, "dictation_level", 1) or 1)))
    from code_coach.dictation.bank import DICTATION_LEVEL_LABELS

    return PracticeSession(
        drill_id=drill.id,
        title=title,
        skill=drill.skill,
        skill_name=skill.name if skill else drill.skill,
        difficulty=drill.difficulty,
        prompt=drill.prompt,
        starter=drill.starter,
        steps=steps,
        mode=progress.mode,
        coach_level=level_for_style,
        coach_style=coach_style_for(level_for_style),
        meter=level_for_style,
        progress=_progress_response(),
        is_lesson=True,
        class_id=meta["class_id"],
        class_number=int(meta.get("class_number") or 1),
        class_name=meta["class_name"],
        lesson_number=meta["lesson_number"],
        lesson_role=role,
        is_review=role == "review",
        can_go_lesson_2=True,
        curriculum=catalog_payload(lang.id),
        exercise_count=len(steps),
        class_total=class_total,
        class_position=class_position,
        window=(
            progress.batch_for(progress.curriculum_class or "foundations")
            if endless
            else 0
        ),
        endless=endless,
        dictation_level=d_level,
        dictation_level_label=DICTATION_LEVEL_LABELS.get(d_level, f"Level {d_level}"),
        lines_done=progress.lines_for(meta["class_id"]),
        language=lang.id,
        editor_language=lang.monaco,
        can_visualize="tracer" in lang.ready,
        can_explain="explainer" in lang.ready,
    )


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, version=__version__)


@app.get("/api/typing/catalog", response_model=TypingCatalogResponse)
def typing_catalog() -> TypingCatalogResponse:
    """Sections, the modes each one supports, and the keyboard to draw."""
    return TypingCatalogResponse(
        sections=[
            TypingSectionInfo(
                id=s["id"],
                name=s["name"],
                description=s["description"],
                modes=[TypingModeInfo(**m) for m in s["modes"]],
            )
            for s in typing_sections()
        ],
        themes=[TypingThemeInfo(**t) for t in typing_themes()],
        teach_languages=typing_teach_languages(),
        keyboard=keyboard_payload(),
        fingers=FINGER_NAMES,
        names=dict(SYMBOL_NAMES),
    )


_typing_records = RecordStore()


def _record_info(record: Record) -> TypingRecordInfo:
    """Attach display names, so the board reads without a second lookup."""
    section = TYPING_SECTIONS_BY_ID.get(record.section)
    mode = TYPING_MODES_BY_ID.get(record.mode)
    return TypingRecordInfo(
        section=record.section,
        mode=record.mode,
        section_name=section.name if section else record.section,
        mode_name=mode.name if mode else record.mode,
        best_wpm=record.best_wpm,
        best_accuracy=record.best_accuracy,
        best_reaction_ms=record.best_reaction_ms,
        best_streak=record.best_streak,
        runs=record.runs,
        total_keys=record.total_keys,
        last_wpm=record.last_wpm,
        last_accuracy=record.last_accuracy,
        updated=record.updated,
    )


@app.get("/api/typing/course", response_model=TypingCourseResponse)
def typing_course() -> TypingCourseResponse:
    """The numbered path through the keyboard, with your progress folded in."""
    from dataclasses import asdict

    from code_coach.typing.course import course_payload

    records = {
        f"{r.section}:{r.mode}": asdict(r) for r in _typing_records.all_records()
    }
    return TypingCourseResponse(**course_payload(records))


@app.get("/api/typing/records", response_model=list[TypingRecordInfo])
def typing_records() -> list[TypingRecordInfo]:
    """Every section-and-mode you've finished a run on, best first."""
    return [_record_info(r) for r in _typing_records.all_records()]


@app.post("/api/typing/records", response_model=TypingRunResponse)
def typing_submit_run(body: TypingRunRequest) -> TypingRunResponse:
    """Record a finished run and report what it beat."""
    if body.section not in TYPING_SECTIONS_BY_ID:
        raise HTTPException(
            status_code=404, detail=f"no typing section {body.section!r}"
        )
    if body.mode not in TYPING_MODES_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing mode {body.mode!r}")
    record, improvement = _typing_records.submit(
        section=body.section,
        mode=body.mode,
        wpm=body.wpm,
        accuracy=body.accuracy,
        reaction_ms=body.reaction_ms,
        streak=body.streak,
        keystrokes=body.keystrokes,
        when=datetime.now().isoformat(timespec="seconds"),
    )
    return TypingRunResponse(
        record=_record_info(record),
        beat_wpm=improvement.wpm,
        beat_accuracy=improvement.accuracy,
        beat_reaction=improvement.reaction,
        beat_streak=improvement.streak,
    )


@app.get("/api/typing/guide", response_model=TypingGuideResponse)
def typing_guide() -> TypingGuideResponse:
    """Finger assignments, technique and the FAQ — the teaching half."""
    return TypingGuideResponse(**guide_payload())


@app.get("/api/typing/shapes", response_model=TypingShapesResponse)
def typing_shapes(theme: str = "pycode") -> TypingShapesResponse:
    """Which shapes this theme can drill, for the Same Shape picker.

    Its own endpoint rather than a field on the catalogue, because the
    answer depends on the theme and the theme changes while the app is
    open. Folding it into the catalogue would mean either shipping the
    shapes of all sixty-odd themes on every load, or a catalogue that
    goes stale the moment somebody changes the text.
    """
    for part in split_theme_id(theme):
        if part not in TYPING_THEMES_BY_ID:
            raise HTTPException(
                status_code=404, detail=f"no typing theme {part!r}"
            )
    return TypingShapesResponse(
        theme=theme,
        shapes=[TypingShapeInfo(**s) for s in typing_shape_catalog(theme)],
    )


@app.get("/api/typing/drill", response_model=TypingDrillResponse)
def typing_drill(
    section: str,
    mode: str,
    theme: str = "mixed",
    seed: str = "typing",
    count: int = 30,
    shape: str = "",
) -> TypingDrillResponse:
    """One generated run. `seed` varies the draw, so a retry isn't identical."""
    if section not in TYPING_SECTIONS_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing section {section!r}")
    if mode not in TYPING_MODES_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing mode {mode!r}")
    # A theme may name several, comma separated, which is how the
    # picker asks for Python lore and Python code in one pool. Every
    # named part has to exist; an unknown one is still a 404, because
    # silently dropping it would serve a drill nobody asked for.
    for part in split_theme_id(theme):
        if part not in TYPING_THEMES_BY_ID:
            raise HTTPException(
                status_code=404, detail=f"no typing theme {part!r}"
            )
    drill = build_typing_drill(
        section, mode, theme_id=theme, seed=seed,
        count=max(4, min(count, 120)),
        # Not validated against the theme here. A shape that this theme
        # does not have falls back to the draw, because the picker can
        # hold a stale id for a second after the text is changed and a
        # 404 mid-drill would be the wrong answer to that.
        shape_id=shape,
    )
    return TypingDrillResponse(
        id=drill.id,
        section=drill.section,
        section_name=TYPING_SECTIONS_BY_ID[drill.section].name,
        mode=drill.mode,
        mode_name=TYPING_MODES_BY_ID[drill.mode].name,
        theme=drill.theme,
        # Not a lookup: a blended drill's theme id is not a key in the
        # catalogue, and the drill already knows what it is called.
        theme_name=theme_name_for(drill.theme),
        description=drill.description,
        hidden=drill.hidden,
        scoring=drill.scoring,  # type: ignore[arg-type]
        targets=[
            TypingTargetInfo(
                text=t.text,
                prompt=t.prompt,
                shift=t.shift,
                note=t.note,
                # The finger for the first character, which is the one the
                # keyboard highlights when the target comes up.
                finger=finger_for(t.text[0]) if t.text else "th",
            )
            for t in drill.targets
        ],
    )


@app.get("/api/skills", response_model=list[SkillInfo])
def skills() -> list[SkillInfo]:
    return [
        SkillInfo(
            id=s.id,
            name=s.name,
            description=s.description,
            order=s.order,
            base_difficulty=s.base_difficulty,
        )
        for s in list_skills()
    ]


@app.get("/api/languages", response_model=list[LanguageInfo])
def languages() -> list[LanguageInfo]:
    """Languages the drills can be written in.

    Only Python is implemented; the rest are listed with a note saying what's
    missing, so the picker shows the roadmap instead of hiding it.
    """
    from code_coach.languages import languages_payload

    return [LanguageInfo(**x) for x in languages_payload()]


@app.get("/api/progress", response_model=ProgressResponse)
def get_progress() -> ProgressResponse:
    return _progress_response()


@app.put("/api/progress", response_model=ProgressResponse)
def update_progress(body: ProgressSettingsUpdate) -> ProgressResponse:
    progress = _store.load()
    if body.mode is not None:
        progress.mode = body.mode
    # coach_level preferred; difficulty accepted as alias
    level = body.coach_level if body.coach_level is not None else body.difficulty
    if level is not None:
        progress.coach_level = max(1, min(2, int(level)))
    if body.selected_skills is not None:
        progress.selected_skills = list(body.selected_skills)
    if body.language is not None:
        # Refuse rather than silently store a language with no drills behind
        # it — the picker would then look like it worked.
        from code_coach.languages import get_language

        lang = get_language(body.language)
        if lang.id != body.language or not lang.available:
            raise HTTPException(
                status_code=400,
                detail=lang.note or f"{body.language} isn't available yet.",
            )
        progress.language = lang.id
    if body.dictation_level is not None:
        progress.dictation_level = max(1, min(5, int(body.dictation_level)))
        # New difficulty → fresh endless window at this level, in the class
        # the student is currently practicing (each class has its own endless
        # Lesson 1 now).
        class_id = progress.curriculum_class or "foundations"
        batch = progress.bump_batch(class_id)
        progress.curriculum_lesson = 1
        progress.review_skill = None
        progress.current_drill_id = None
        if class_id == "foundations":
            set_class1_batch(
                seed="local-student",
                batch=batch,
                level=progress.dictation_level,
            )
    # Changing path mode/skills refreshes current; coach level keeps the same drill
    if body.mode is not None or body.selected_skills is not None:
        progress.current_drill_id = None
    _store.save(progress)
    return _progress_response()


@app.get("/api/practice/current", response_model=PracticeSession)
def practice_current() -> PracticeSession:
    return _session_from_progress()


def _class_material_total(class_id: str, language: str, level: int) -> int:
    """How many type-along units this class holds, or 0 when it has no end.

    Python's fundamentals are generated from combinatorial pools with a seeded
    RNG, so there is genuinely no last line to reach. Every other class draws
    from a declared bank — the LeetCode solutions, and the per-language
    fundamentals in code_coach/fundamentals — and those run out.
    """
    if class_id.startswith("lc-"):
        from code_coach.leetcode.bank import unit_count

        return unit_count(class_id, level)

    from code_coach.fundamentals.base import CLASS_IDS, material_count

    if language == "python" or class_id not in CLASS_IDS:
        return 0
    return material_count(language, class_id, level)


def _next_class_after(
    class_id: str, progress: StudentProgress, batch: int, level: int
) -> str | None:
    """The class to move on to, once this one's material is used up.

    Returns None while there's more of this class left, for classes with no
    fixed end (Python's Foundations generates its lines), and at the last
    class — where there is nowhere further to go and wrapping is the right
    behaviour.
    """
    from code_coach.curriculum.catalog import classes_for_language
    from code_coach.dictation.bank import WINDOW_SIZE

    language = getattr(progress, "language", "python") or "python"
    total = _class_material_total(class_id, language, level)
    # The window is trimmed to fit a small class, so the stride is whichever
    # is smaller. Using the nominal eight here meant a four-answer class was
    # counted as finished after half a pass.
    stride = min(WINDOW_SIZE, total) or WINDOW_SIZE
    if not total or batch * stride < total:
        return None

    ids = [c.id for c in classes_for_language(language)]
    if class_id not in ids:
        return None
    position = ids.index(class_id)
    return ids[position + 1] if position + 1 < len(ids) else None


@app.post("/api/practice/more", response_model=PracticeSession)
def practice_more_lines() -> PracticeSession:
    """Next window of the current class's Lesson-1 type-along (endless)."""
    from code_coach.dictation.bank import WINDOW_SIZE
    from code_coach.fundamentals.base import window_start

    progress = _store.load()
    class_id = progress.curriculum_class or "foundations"
    language = getattr(progress, "language", "python") or "python"
    progress.curriculum_lesson = 1
    progress.review_skill = None
    level = max(1, min(5, int(getattr(progress, "dictation_level", 1) or 1)))

    # Count the finished window toward this class's lifetime lines — what it
    # actually held, since the last window of a class stops at the end of the
    # material rather than being padded back out to eight.
    total = _class_material_total(class_id, language, level)
    served = WINDOW_SIZE
    if total:
        start = window_start(
            total, batch=progress.batch_for(class_id), count=WINDOW_SIZE
        )
        served = min(WINDOW_SIZE, total - start)
    progress.add_lines(class_id, served)
    batch = progress.bump_batch(class_id)

    # A class with a declared bank holds a fixed set of answers. Once you've
    # been through them, looping back to the top is busywork — the next class
    # is the point. Python's fundamentals are generated rather than declared,
    # so those are the ones with no end to reach.
    graduated = _next_class_after(class_id, progress, batch, level)
    if graduated:
        goto_position(progress, class_id=graduated, lesson_number=1)
        progress.exercise_index = 0
        _store.save(progress)
        return _session_from_progress()
    if class_id == "foundations":
        set_class1_batch(seed="local-student", batch=batch, level=level)
        progress.current_drill_id = "class-1-dictation"
    else:
        # get_active_drill regenerates the window for this class/batch
        progress.current_drill_id = None
    progress.exercise_index = 0
    _store.save(progress)
    return _session_from_progress()


@app.post("/api/practice/goto-problem", response_model=PracticeSession)
def practice_goto_problem(body: GotoProblemRequest) -> PracticeSession:
    """Open the type-along for one problem, from a lesson.

    Returns the session with `jump_to_exercise` set to where the problem sits
    in the window, so the client can land on it rather than on the window's
    first line.
    """
    from code_coach.leetcode.bank import batch_holding, has_own_bank

    progress = _store.load()
    language = getattr(progress, "language", "python") or "python"
    level = max(1, min(5, int(getattr(progress, "dictation_level", 1) or 1)))

    # Without its own bank there is no problem to open, and the session that
    # would come back is the fundamentals one — so the link used to land you
    # on "Hello, world!" with nothing said. Better to name the reason.
    if not has_own_bank(language):
        raise HTTPException(
            status_code=409,
            detail=(
                f"The problems aren't written in {language} yet, so this one "
                "can't be opened here. Switch language to work through it."
            ),
        )

    found = batch_holding(body.pattern_id, body.problem_number, level, language)
    if found is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"#{body.problem_number} isn't in {body.pattern_id} at this "
                "difficulty."
            ),
        )
    batch, offset = found

    goto_position(progress, class_id=body.pattern_id, lesson_number=1)
    progress.set_batch(body.pattern_id, batch)
    progress.current_drill_id = None
    progress.exercise_index = offset
    _store.save(progress)

    session = _session_from_progress()
    session.jump_to_exercise = offset
    return session


@app.post("/api/hints", response_model=HintsResponse)
def hints(body: HintsRequest) -> HintsResponse:
    """Reminders about code that will not run.

    Free mode turns the coach off, and this is deliberately not the coach:
    it says nothing about whether you solved anything, only that a quote is
    open or a bracket never closes. Empty most of the time, which is the
    point — a hint on working code is worse than no hint.
    """
    from code_coach.syntax_hints import hints_for

    found = hints_for(body.code or "", body.language or "python")
    return HintsResponse(
        hints=[HintInfo(line=h.line, message=h.message) for h in found]
    )


def _viewing_language(asked: str | None) -> str:
    """Which language a reading screen should show.

    The reading screens carry a language picker of their own, so they can ask
    for one explicitly. Asking beats the stored value because the two round
    trips race otherwise: the panel refetches as soon as the switch is
    acknowledged, which can be before the save has landed. An unknown name
    falls back rather than 404s — the sheet or the topics simply come back
    for the stored language.
    """
    from code_coach.languages import LANGUAGES

    if asked and any(lang.id == asked for lang in LANGUAGES):
        return asked
    progress = _store.load()
    return getattr(progress, "language", "python") or "python"


@app.get("/api/reference")
def reference(language: str | None = None) -> dict:
    """The cheat sheet for the language being practised.

    A desk mat rather than a lesson: the lines worth having in your head,
    densest and most-used first. Flashcards are drawn from the same entries,
    so there is one place to add something rather than two.
    """
    from code_coach.reference import sheet_for

    language = _viewing_language(language)
    sheet = sheet_for(language)
    if sheet is None:
        # Better to say so than to quietly hand over another language's.
        return {"language": language, "sections": [], "has_sheet": False}
    return {
        "language": language,
        "has_sheet": True,
        "sections": [
            {
                "name": section.name,
                "blurb": section.blurb,
                "entries": [
                    {"code": e.code, "note": e.note} for e in section.entries
                ],
            }
            for section in sheet.sections
        ],
    }


@app.get("/api/concepts")
def concepts(language: str | None = None) -> list[dict]:
    """The concept questions, grouped by topic.

    The half of a systems or quant interview that is not a coding problem —
    what happens on a page fault, why acquire and release come in pairs, what
    a branch misprediction costs. Most of it is about the machine and goes to
    everybody; the one topic on the language's own semantics follows whichever
    language you are in, so a Python student is not opened on the rule of five.
    """
    from code_coach.concepts import payload

    return payload(_viewing_language(language))


@app.get("/api/workbook")
def workbook(language: str | None = None) -> dict:
    """The workbook: pages of small exercises you solve by typing.

    Everything else in the app is material to read or type along with. This is
    the part where you are given a sentence and an empty editor and have to
    produce the thing yourself, a dozen times, with one detail changing each
    time.
    """
    from code_coach.languages import get_language
    from code_coach.workbook import has_workbook, payload

    language = _viewing_language(language)
    # The screen writes the name into a sentence ("Write it in Rust"), so it
    # needs the one with the capital letter rather than the id.
    lang = get_language(language)
    name = lang.name
    # Whether Watch it run can answer here, asked of the language rather
    # than written down on the screen. It was hard-coded to Python there,
    # which left the button greyed out in JavaScript and Dart — both of
    # which have had a tracer for as long as the button has existed.
    can_trace = "tracer" in lang.ready
    if not has_workbook(language):
        # Better than a page of exercises that cannot be written.
        return {
            "language": language,
            "language_name": name,
            "has_workbook": False,
            "can_trace": can_trace,
            "pages": [],
            "done": [],
        }
    progress = _store.load()
    return {
        "language": language,
        "language_name": name,
        "has_workbook": True,
        "can_trace": can_trace,
        "pages": payload(language),
        "done": progress.workbook_for(language),
        # Where to open. Empty means the student has not started, so the
        # screen falls back to page one on its own.
        "at": progress.workbook_page_for(language),
        # What they wrote, per exercise. Their own work is worth keeping and
        # is the one thing here they cannot get back any other way.
        "answers": progress.workbook_answers_for(language),
    }


@app.post("/api/workbook/check", response_model=WorkbookCheckResponse)
def workbook_check(body: WorkbookCheckRequest) -> WorkbookCheckResponse:
    """Run what the student typed and compare what it printed.

    Deliberately not a check on the code itself. There are several right ways
    to print the numbers 1 to 5 and all of them should pass; what is being
    asked is whether the program does what the sentence said.
    """
    from code_coach.workbook import exercise as find_exercise
    from code_coach.workbook import has_workbook, matches, page as find_page

    language = _viewing_language(body.language)
    if not has_workbook(language):
        raise HTTPException(
            status_code=409, detail=f"No workbook for {language}"
        )
    found = find_exercise(body.page_id, body.exercise_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown exercise {body.exercise_id}"
        )
    # A page the language is not offered has no reference answer in it, so
    # there is nothing to mark against. This used to be covered by the
    # has_workbook gate above — every language either had the whole shared
    # tier or nothing at all — and stopped being true when SQL arrived with
    # pages of its own and none of anyone else's.
    # Asking whether a reference exists, rather than reading the page's
    # language list: an empty list means "every language the workbook
    # covers", which stopped meaning "every language with these shapes" the
    # moment SQL arrived sharing none of them. The reference is the rule
    # that cannot drift, and it is the same one pages() uses.
    if found.answer(language) is None:
        raise HTTPException(
            status_code=409,
            detail=f"{body.page_id} has no {language} answer",
        )

    stdout, stderr, exit_code = run_code(body.code, language=language)
    expect = found.expect
    passed = exit_code == 0 and matches(stdout, expect)

    progress = _store.load()
    # Where you were is worth keeping whether or not the answer was right —
    # coming back to the page you were stuck on is the point.
    progress.set_workbook_page(language, body.page_id)
    # And so is what you wrote. This used to keep only correct answers, on the
    # grounds that the file should be a record of your work rather than your
    # typos; the effect was that going to another exercise and back threw away
    # everything you had not yet got right, which is exactly the work you most
    # wanted back.
    progress.remember_workbook_answer(language, found.id, body.code)
    if passed:
        progress.mark_workbook(language, found.id)
    _store.save(progress)

    progress = _store.load()
    done = set(progress.workbook_for(language))
    holding = find_page(body.page_id)
    on_page = [e.id for e in holding.exercises] if holding else []
    return WorkbookCheckResponse(
        passed=passed,
        stdout=stdout,
        stderr=stderr,
        expect=expect,
        exit_code=exit_code,
        # An empty run with a bad exit code is a program that never got as far
        # as printing — a compile error, usually. Worth saying separately.
        failed_to_run=exit_code != 0,
        done_on_page=sum(1 for e in on_page if e in done),
        page_total=len(on_page),
    )


@app.post("/api/workbook/draft")
def workbook_draft(body: WorkbookDraftRequest) -> dict:
    """Keep what is in the box, without running it.

    Typing is the work, so it should survive leaving the exercise — whether
    or not it was ever checked, and whether or not it was right. The screen
    sends this shortly after you stop typing and again on the way out of an
    exercise, so what comes back is what you left.
    """
    from code_coach.workbook import exercise as find_exercise
    from code_coach.workbook import has_workbook

    language = _viewing_language(body.language)
    if not has_workbook(language):
        raise HTTPException(
            status_code=409, detail=f"No workbook for {language}"
        )
    found = find_exercise(body.page_id, body.exercise_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown exercise {body.exercise_id}"
        )

    progress = _store.load()
    progress.set_workbook_page(language, body.page_id)
    progress.remember_workbook_answer(language, found.id, body.code)
    _store.save(progress)
    return {"saved": True}


@app.get("/api/lessons")
def lessons(language: str | None = None) -> list[dict]:
    """Every pattern lesson, for the Lessons screen.

    Not tied to the drill you are on: this is the reading, browsed on its own,
    the way the typing trainer is its own place rather than a panel.
    """
    from code_coach.leetcode.bank import lessons_catalogue

    return lessons_catalogue(_viewing_language(language))


@app.get("/api/curriculum")
def curriculum_tree() -> list[dict]:
    progress = _store.load()
    return catalog_payload(getattr(progress, "language", "python") or "python")


@app.post("/api/practice/goto-lesson", response_model=PracticeSession)
def practice_goto_lesson(body: GotoLessonRequest) -> PracticeSession:
    progress = _store.load()
    if body.class_delta or body.lesson_delta:
        navigate_step(
            progress,
            class_delta=int(body.class_delta or 0),
            lesson_delta=int(body.lesson_delta or 0),
        )
    else:
        goto_position(
            progress,
            class_id=body.class_id,
            lesson_number=body.lesson_number,
        )
    _store.save(progress)
    return _session_from_progress()


@app.post("/api/practice/navigate", response_model=PracticeSession)
def practice_navigate(body: NavigateRequest) -> PracticeSession:
    """Free jump: class / lesson (exercise index is client-side)."""
    progress = _store.load()
    if body.class_delta or body.lesson_delta:
        navigate_step(
            progress,
            class_delta=int(body.class_delta or 0),
            lesson_delta=int(body.lesson_delta or 0),
        )
    else:
        goto_position(
            progress,
            class_id=body.class_id,
            lesson_number=body.lesson_number,
        )
    if body.exercise_index is not None:
        progress.exercise_index = max(0, int(body.exercise_index))
    _store.save(progress)
    return _session_from_progress()


@app.post("/api/practice/review", response_model=PracticeSession)
def practice_review(body: ReviewRequest) -> PracticeSession:
    """Click Hint → supporting Lesson 1 skill practice."""
    progress = _store.load()
    enter_review(progress, body.skill_id)
    drill = get_active_drill(progress)
    if drill is None or not drill.id.startswith("review-"):
        raise HTTPException(status_code=404, detail=f"No review for {body.skill_id}")
    _store.save(progress)
    return _session_from_progress()


@app.post("/api/practice/back", response_model=PracticeSession)
def practice_back() -> PracticeSession:
    """Return from supporting lesson to Lesson 2 (or prior)."""
    progress = _store.load()
    back_from_review(progress)
    _store.save(progress)
    return _session_from_progress()


@app.post("/api/practice/check-answer", response_model=CheckAnswerResponse)
def practice_check_answer(body: CheckAnswerRequest) -> CheckAnswerResponse:
    """Diff the student's attempt against a problem's reference solution.

    This is the self-check path: the drill's own grader is verbatim (Lesson 1)
    or structural (Lesson 3), so neither tells you which line of YOUR answer is
    off. Here the whole solution is the target, and the reply names the first
    line that differs.
    """
    from code_coach.dictation.bank import check_block
    from code_coach.leetcode.problems import get_pattern
    from code_coach.practice.adapt import line_diff_note

    if not body.pattern_id or body.problem_number is None:
        raise HTTPException(status_code=400, detail="Need pattern_id and problem_number.")
    pattern = get_pattern(body.pattern_id)
    problem = (
        next((p for p in pattern.problems if p.number == body.problem_number), None)
        if pattern
        else None
    )
    if problem is None:
        raise HTTPException(
            status_code=404, detail=f"No problem {body.problem_number}"
        )

    code = body.code or ""
    matches = check_block(code, problem.code)
    note = "" if matches else (line_diff_note(code, problem.code) or "")
    return CheckAnswerResponse(
        ok=True,
        matches=matches,
        note=note,
        solution=problem.code,
        title=problem.label,
    )


@app.post("/api/visualize", response_model=VisualizeResponse)
def visualize(body: VisualizeRequest) -> VisualizeResponse:
    """Step-by-step picture of the data while the code runs.

    Complements /api/explain: that one says what each line means, this one says
    what `left`, `seen` and the node pointers actually held at each step.
    """
    from code_coach.languages import get_language
    from code_coach.leetcode.study import brief_for, demo_call_for
    from code_coach.visualize import suggest_call, trace_code

    # Python is traced with sys.settrace and JavaScript with Node's inspector.
    # Everything else has no tracer, and feeding one a SQL query produced
    # "SyntaxError: invalid syntax", which says nothing useful about why.
    # What the request asked for, falling back to the language being
    # worked in. A screen showing a snippet in a language of its own has
    # to be able to say so: the JavaScript predict puzzles would
    # otherwise be traced as Python and fail on the first line.
    lang = get_language(
        body.language or getattr(_store.load(), "language", "python"))
    if "tracer" not in lang.ready:
        return VisualizeResponse(
            ok=False,
            error=(
                f"Code tracing works in Python and JavaScript — it steps "
                f"through the program as it executes, and there's no tracer "
                f"for {lang.name} yet."
            ),
        )

    code = body.code or ""
    call = (body.call or "").strip()

    if not call and lang.id == "python":
        # A hand-written call wins: these are the problems whose input is a
        # structure (a tree, a linked list, a class) that no amount of parsing
        # the example can build. They're written in Python, so they're only
        # usable when Python is what's running.
        call = demo_call_for(body.problem_number)
    if not call:
        examples: list[str] = []
        if body.problem_number is not None:
            brief = brief_for(body.problem_number)
            if brief:
                examples = list(brief.examples)
        call = suggest_call(code, examples, language=lang.id)

    result = trace_code(code, call=call, language=lang.id)
    return VisualizeResponse(
        ok=bool(result.get("ok")),
        steps=result.get("steps", []),
        truncated=bool(result.get("truncated")),
        stdout=result.get("stdout", ""),
        stderr=result.get("stderr", ""),
        error=result.get("error"),
        call=call,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    """Local tips chatbot (keyboard + Python FAQ)."""
    return ChatResponse(reply=chat_reply(body.message or ""))


@app.post("/api/explain", response_model=ExplainResponse)
def explain(body: ExplainRequest) -> ExplainResponse:
    """Plain-English walkthrough of the student's current code + why it
    outputs what it does. Local AST + traced run — no cloud AI."""
    from code_coach.explain import explain_code
    from code_coach.languages import get_language

    lang = get_language(getattr(_store.load(), "language", "python"))
    if "explainer" not in lang.ready:
        # Reading the code needs a reader for that language. Without this,
        # SQL came back as "Python can't run this — there's a syntax error",
        # which blames the student for writing correct SQL.
        return ExplainResponse(
            ok=False,
            summary=(
                f"Explain my code works in Python and JavaScript so far — "
                f"there's no reader for {lang.name} yet."
            ),
        )

    if lang.id in ("javascript", "typescript"):
        from code_coach.explain_js import explain_js
        from code_coach.visualize import suggest_call, trace_code

        code = body.code or ""
        # A traced run lets the explanation talk about what actually happened,
        # not only what the code says — the same pairing the Python explainer
        # uses. Without a call there's nothing to run but the definitions, so
        # the walkthrough stands on its own rather than reporting a non-run.
        call = suggest_call(code, [], language=lang.id)
        trace = trace_code(code, call=call, language=lang.id) if call else None
        return ExplainResponse(**explain_js(code, trace))

    return ExplainResponse(**explain_code(body.code or ""))


@app.post("/api/practice/next", response_model=PracticeSession)
def practice_next() -> PracticeSession:
    """Advance: Foundations L1 stays endless (more lines); else Lesson 1 → 2."""
    progress = _store.load()
    if progress.review_skill:
        back_from_review(progress)
        _store.save(progress)
        return _session_from_progress()
    class_id = progress.curriculum_class or "foundations"
    lesson = int(progress.curriculum_lesson or 1)
    # Foundations type-along never auto-graduates — load next window
    if class_id == "foundations" and lesson <= 1:
        return practice_more_lines()
    if lesson <= 1:
        goto_lesson(progress, 2)
        _store.save(progress)
        return _session_from_progress()
    # Already on lesson 2+ — stay / no-op session
    return _session_from_progress()


@app.post("/api/practice/evaluate", response_model=DrillEvaluateResponse)
def practice_evaluate(body: DrillEvaluateRequest) -> DrillEvaluateResponse:
    drill = get_drill(body.drill_id)
    progress = _store.load()
    if drill is None:
        # Endless per-class windows live in the dynamic registry; after a
        # server restart the client may evaluate before refetching the
        # session. Regenerate from saved progress.
        candidate = get_active_drill(progress)
        if candidate is not None and candidate.id == body.drill_id:
            drill = candidate
    if drill is None:
        raise HTTPException(status_code=404, detail=f"Unknown drill {body.drill_id}")
    stdout, stderr, exit_code = "", "", 0
    if body.run:
        stdout, stderr, exit_code = run_code(
            body.code, language=getattr(progress, "language", "python")
        )

    scored = evaluate_drill(
        drill,
        body.code,
        coach_level=progress.coach_level,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        ran=body.run,
        exercise_index=body.exercise_index,
    )

    just_completed = False
    progress_resp = None
    if scored["complete"]:
        prev = progress.completed_drills.get(drill.id)
        already = prev.count if prev else 0
        if already == 0:
            mark_drill_complete(progress, drill)
            just_completed = True
            _store.save(progress)
        progress_resp = ProgressResponse(**progress_summary(_store.load()))

    return DrillEvaluateResponse(
        drill_id=drill.id,
        title=drill.title,
        skill=drill.skill,
        difficulty=drill.difficulty,
        prompt=drill.prompt,
        code=body.code,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        ran=body.run,
        checks=[CheckItem(**c) for c in scored["checks"]],
        passed=scored["passed"],
        total=scored["total"],
        complete=scored["complete"],
        coach_level=scored["coach_level"],
        coach_style=scored["coach_style"],
        next_label=scored["next_label"],
        next_concept=scored["next_concept"],
        next_why=scored["next_why"],
        next_hint=scored["next_hint"],
        next_example=scored["next_example"],
        next_suggest=scored["next_suggest"],
        next_vocab=scored.get("next_vocab"),
        accepts_own_values=True,
        observation=scored.get("observation"),
        guidance=scored.get("guidance"),
        adapt_example=scored.get("adapt_example"),
        tone=scored.get("tone"),
        status=scored.get("status"),
        just_completed=just_completed,
        progress=progress_resp,
        requirements=scored.get("requirements"),
    )


@app.post("/api/practice/complete", response_model=PracticeSession)
def practice_complete_and_next(body: DrillEvaluateRequest) -> PracticeSession:
    """Mark drill complete (if steps pass) and advance."""
    drill = get_drill(body.drill_id)
    if drill is None:
        raise HTTPException(status_code=404, detail=f"Unknown drill {body.drill_id}")
    progress = _store.load()
    scored = evaluate_drill(drill, body.code, coach_level=progress.coach_level)
    if not scored["complete"]:
        raise HTTPException(
            status_code=400,
            detail="Drill not complete yet — finish all steps first.",
        )
    progress = _store.load()
    mark_drill_complete(progress, drill)
    progress.current_drill_id = None
    _store.save(progress)
    return practice_next()


# ── Katas ────────────────────────────────────────────────────
#
# The other half of problem solving, and the half this app did not have.
# Everywhere else asks a program to print something; here the student
# writes a function and it is called with inputs they did not choose,
# which is what Codewars and freeCodeCamp do and is the only way an edge
# case is ever met.


@app.get("/api/kata")
def kata_list() -> dict:
    """Every kata, grouped the way the screen shows them."""
    from code_coach.kata import (
        families,
        kata_language_of,
        katas,
        languages,
    )

    saved = _store.load()
    counts, last = saved.kata_counts(), saved.kata_last()
    return {
        # The languages on offer, so the screen can filter rather than
        # making someone scroll past fifty-five to reach the eight they
        # came for.
        "languages": list(languages()),
        "families": [
            {
                "name": family,
                "language": kata_language_of(family),
                "katas": [
                    {
                        "id": k.id,
                        "name": k.name,
                        "brief": k.brief,
                        "signature": k.signature,
                        "example": k.example,
                        "hint": k.hint,
                        "cases": len(k.cases),
                        # Filled in for the broken ones, empty for the
                        # rest, which is what the screen keys off.
                        "start": k.start,
                        # What the program does today, for a Change it
                        # drill - the request means nothing without it.
                        "was": k.was,
                        "done": counts.get(k.id, 0),
                        "last": last.get(k.id, ""),
                        "level": k.level,
                    }
                    for k in katas(family)
                ],
            }
            for family in families()
        ]
    }


@app.get("/api/kata/answer")
def kata_answer(kata_id: str = "") -> dict:
    """The worked answer, asked for rather than shipped with the list.

    Its own request on purpose. Sending every answer with the list would
    put them all in the browser whether or not anyone wanted them, and
    the point of the button is that looking is a decision you make.
    """
    from code_coach.kata import kata as find_kata

    found = find_kata(kata_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Unknown form {kata_id}")
    return {"id": found.id, "answer": found.reference()}


@app.post("/api/kata/check", response_model=KataCheckResponse)
def kata_check(body: KataCheckRequest) -> KataCheckResponse:
    """Run the student's function against every case and say which failed."""
    from code_coach.kata import harness, judge, kata as find_kata

    found = find_kata(body.kata_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown form {body.kata_id}"
        )

    # The kata's own language, not Python. This was hard-coded from
    # when Python was the only one, so every JavaScript kata was run
    # through the Python interpreter and came back as "this did not
    # run" whatever was typed into it.
    stdout, stderr, exit_code = run_code(
        harness(found, body.code), language=found.language
    )
    outcome = judge(found, stdout, stderr, exit_code)
    done = 0
    if outcome.passed:
        # Counted here rather than on the screen, so the number survives
        # a reload and a different browser.
        progress = _store.load()
        done = progress.record_kata(found.id)
        _store.save(progress)
    # Whatever the student printed themselves, without the driver's line.
    theirs = stdout.split("<<<KATA>>>")[0]
    return KataCheckResponse(
        passed=outcome.passed,
        count=outcome.count,
        total=len(found.cases),
        broke=outcome.broke,
        stdout=theirs,
        bug=found.bug if outcome.passed else "",
        # Held back until it passes, like the name of a bug: reading why
        # the change had to be that way before making it gives it away.
        change=found.change if outcome.passed else "",
        done=done,
        results=[
            KataCaseResult(
                args=list(r.args),
                want=r.want,
                got=r.got,
                error=r.error,
                passed=r.passed,
                changed=r.changed,
            )
            for r in outcome.results
        ],
    )


# ── Predict the output ───────────────────────────────────────
#
# The other question. The katas ask you to write a function; this asks
# what a piece of correct Python actually does, which is where the gap
# between what you meant and what the language does shows up.


@app.get("/api/predict")
def predict_list() -> dict:
    """Every puzzle, grouped, without its answer.

    The answer is deliberately absent. It is the whole exercise, and a
    payload carrying it is a payload someone can read instead of
    thinking.
    """
    from code_coach.kata.predict import (
        language_of,
        predict_families,
        puzzles,
    )

    saved = _store.load()
    counts, last = saved.predict_counts(), saved.predict_last()
    return {
        "families": [
            {
                "name": family,
                # A family never mixes languages, so this belongs on the
                # family rather than being repeated on every puzzle.
                "language": language_of(family),
                "puzzles": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "code": p.code,
                        "done": counts.get(p.id, 0),
                        "last": last.get(p.id, ""),
                        "level": p.level,
                    }
                    for p in puzzles(family)
                ],
            }
            for family in predict_families()
        ]
    }


@app.post("/api/predict/check", response_model=PredictCheckResponse)
def predict_check(body: PredictCheckRequest) -> PredictCheckResponse:
    """Compare the guess with what the snippet prints."""
    from code_coach.kata.predict import puzzle as find_puzzle

    found = find_puzzle(body.puzzle_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown puzzle {body.puzzle_id}"
        )
    # Trailing blank lines and stray spaces at the ends of lines are not
    # the thing being tested, and failing someone for one would teach
    # them to distrust the marker rather than to read the code.
    def tidy(text: str) -> str:
        lines = text.replace("\r\n", "\n").split("\n")
        return "\n".join(line.rstrip() for line in lines).strip()

    passed = tidy(body.guess) == tidy(found.expect)
    done = 0
    if passed:
        progress = _store.load()
        done = progress.record_predict(found.id)
        _store.save(progress)
    return PredictCheckResponse(
        passed=passed,
        done=done,
        expect=found.expect,
        guess=body.guess,
        why=found.why,
    )


@app.get("/api/css")
def css_list() -> dict:
    """Every CSS quiz, grouped, with the choices and without the answer.

    The choices come from the quiz rather than being assembled here,
    because they are sorted on the way out and that sort is what stops
    the answer's position giving it away. Assembling them in a second
    place would be a second chance to lose that.
    """
    from code_coach.css import css_families, quizzes

    saved = _store.load()
    counts, last = saved.css_counts(), saved.css_last()
    return {
        "families": [
            {
                "name": family,
                "quizzes": [
                    {
                        "id": q.id,
                        "name": q.name,
                        "html": q.html,
                        "css": q.css,
                        "target": q.target,
                        "prop": q.prop,
                        "choices": list(q.choices),
                        "page": q.page(),
                        "done": counts.get(q.id, 0),
                        "last": last.get(q.id, ""),
                        "level": q.level,
                    }
                    for q in quizzes(family)
                ],
            }
            for family in css_families()
        ]
    }


@app.post("/api/css/check", response_model=CssCheckResponse)
def css_check(body: CssCheckRequest) -> CssCheckResponse:
    """Compare the pick with what Chromium computed.

    Nothing runs here. The answer was measured once by
    tools/verify_css.py and the suite holds it to that measurement, so
    marking is a comparison against evidence rather than against an
    opinion about how the cascade ought to work.
    """
    from code_coach.css import quiz as find_quiz

    found = find_quiz(body.quiz_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown quiz {body.quiz_id}"
        )
    passed = body.choice.strip() == found.expect
    done = 0
    if passed:
        progress = _store.load()
        done = progress.record_css(found.id)
        _store.save(progress)
    return CssCheckResponse(
        passed=passed,
        done=done,
        expect=found.expect,
        choice=body.choice,
        why=found.why,
    )


@app.get("/api/drills")
def drill_list() -> dict:
    """Every typing drill, grouped, with the code you are copying.

    The code is in the payload on purpose — unlike the katas and the
    quizzes, this is not a question with an answer to protect. You are
    copying the thing in front of you, and hiding it would leave
    nothing to copy.
    """
    from code_coach.markup import drill_families, drills

    saved = _store.load()
    counts, last = saved.markup_counts(), saved.markup_last()
    return {
        "families": [
            {
                "name": family,
                "drills": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "code": d.code,
                        "note": d.note,
                        "wrapper": d.wrapper,
                        "lines": d.lines,
                        "done": counts.get(d.id, 0),
                        "last": last.get(d.id, ""),
                        "level": d.level,
                    }
                    for d in drills(family)
                ],
            }
            for family in drill_families()
        ]
    }


@app.post("/api/drills/check", response_model=DrillCheckResponse)
def drill_check(body: DrillCheckRequest) -> DrillCheckResponse:
    """Compare what was typed with the drill, character for character.

    Both sides go through the same tidying, which forgives line endings
    and trailing spaces and forgives nothing else. On a mismatch the
    answer is the first line that differs rather than a diff of the
    whole thing: you are about to type it again, so what you need is
    the one place to look.
    """
    from code_coach.markup import drill as find_drill
    from code_coach.markup import tidy

    found = find_drill(body.drill_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown drill {body.drill_id}"
        )
    want, got = tidy(found.code), tidy(body.typed)
    if want == got:
        progress = _store.load()
        done = progress.record_markup(found.id)
        _store.save(progress)
        return DrillCheckResponse(passed=True, done=done)

    want_lines, got_lines = want.split("\n"), got.split("\n")
    where = 0
    for i in range(max(len(want_lines), len(got_lines))):
        a = want_lines[i] if i < len(want_lines) else ""
        b = got_lines[i] if i < len(got_lines) else ""
        if a != b:
            where = i + 1
            break
    return DrillCheckResponse(
        passed=False,
        first_wrong_line=where,
        want_line=want_lines[where - 1] if where <= len(want_lines) else "",
        typed_line=got_lines[where - 1] if where <= len(got_lines) else "",
    )


@app.get("/api/magnets")
def magnet_list() -> dict:
    """Every puzzle, with its magnets jumbled.

    Jumbled here rather than on the screen, and jumbled afresh on every
    request: the finished order never leaves the server, and coming
    back to a puzzle gives you a new arrangement rather than the one
    you have already learned the shape of.
    """
    from code_coach.magnets import magnet_families, magnets

    saved = _store.load()
    counts, last = saved.magnet_counts(), saved.magnet_last()
    return {
        "families": [
            {
                "name": family,
                "magnets": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "note": m.note,
                        "language": m.language,
                        "pieces": list(m.shuffled()),
                        # Labels only. The counts stay on the server:
                        # "this stage holds three lines" answers a good
                        # part of the puzzle, and a subgoal label is a
                        # scaffold rather than an answer.
                        "labels": list(m.labels),
                        "done": counts.get(m.id, 0),
                        "last": last.get(m.id, ""),
                        "level": m.level,
                    }
                    for m in magnets(family)
                ],
            }
            for family in magnet_families()
        ]
    }


@app.post("/api/magnets/check", response_model=MagnetCheckResponse)
def magnet_check(body: MagnetCheckRequest) -> MagnetCheckResponse:
    """Run what was arranged, and compare what it printed.

    Not a comparison of line orders. There is always more than one
    arrangement that works — a function declaration is hoisted, two
    independent statements can go either way round — and failing those
    would teach you to guess at the author's preference rather than at
    what the language does. Any arrangement that prints the right thing
    is right, because it is.
    """
    from code_coach.engine import run_code
    from code_coach.magnets import magnet as find_magnet
    from code_coach.magnets import same_pieces

    found = find_magnet(body.magnet_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown puzzle {body.magnet_id}"
        )
    if not same_pieces(found, list(body.lines)):
        return MagnetCheckResponse(
            broke=(
                "Those are not this puzzle's magnets — every piece has "
                "to be used, once each."
            ),
            expect=found.expect,
        )

    out, err, exit_code = run_code(
        "\n".join(body.lines), language=found.language)
    printed = out.replace("\r\n", "\n").strip()
    if exit_code != 0:
        return MagnetCheckResponse(
            broke=_tidy_magnet_error(err) or "That arrangement did not run.",
            printed=printed,
            expect=found.expect,
        )

    passed = printed == found.expect.strip()
    done = 0
    if passed:
        progress = _store.load()
        done = progress.record_magnet(found.id)
        _store.save(progress)
    return MagnetCheckResponse(
        passed=passed,
        done=done,
        printed=printed,
        expect=found.expect,
        why=found.note if passed else "",
    )


def _tidy_magnet_error(detail: str) -> str:
    """Take the scratch file and the runtime's sign-off out of an error.

    The path goes for the same reason as in the kata marker: it is true
    and unhelpful, and naming a file in the system temp directory reads
    as though the mistake is somewhere the person has never been.

    The trailer goes because a misplaced line here is a normal event
    rather than a crash — this is the mode where putting a line in the
    wrong stage is supposed to fail — and "Node.js v26.6.0" under the
    message makes an ordinary wrong answer look like the tool broke.
    What is worth reading is the line and the reason.
    """
    from code_coach.kata import _tidy

    keep = [
        line for line in _tidy(detail).splitlines()
        if not line.strip().startswith("Node.js v")
    ]
    return "\n".join(keep).strip()


@app.get("/api/errors")
def error_list() -> dict:
    """Every crash, with its message and without its answers.

    The program and the message are the question and have to be here.
    The line it blames, the right reading and the fix are the answer —
    and the fix says the answer in prose, which is the easy one to
    leave in by accident.
    """
    from code_coach.errors import crash_families, crashes

    saved = _store.load()
    counts, last = saved.error_counts(), saved.error_last()
    return {
        "families": [
            {
                "name": family,
                "crashes": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "code": c.code,
                        "message": c.message,
                        "language": c.language,
                        "choices": list(c.choices),
                        "lines": len(c.numbered),
                        "done": counts.get(c.id, 0),
                        "last": last.get(c.id, ""),
                        "level": c.level,
                    }
                    for c in crashes(family)
                ],
            }
            for family in crash_families()
        ]
    }


@app.post("/api/errors/check", response_model=ErrorCheckResponse)
def error_check(body: ErrorCheckRequest) -> ErrorCheckResponse:
    """Mark the two halves separately, and say what to do about it."""
    from code_coach.errors import crash as find_crash

    found = find_crash(body.crash_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown crash {body.crash_id}"
        )
    line_right = body.line == found.line
    meaning_right = body.meaning.strip() == found.meaning
    passed = line_right and meaning_right
    done = 0
    if passed:
        progress = _store.load()
        done = progress.record_error(found.id)
        _store.save(progress)
    return ErrorCheckResponse(
        passed=passed,
        done=done,
        line_right=line_right,
        meaning_right=meaning_right,
        line=found.line,
        meaning=found.meaning,
        fix=found.fix,
    )


def _hunt_or_404(hunt_id: str):
    from code_coach.bughunt import hunt as find_hunt

    found = find_hunt(hunt_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Unknown hunt {hunt_id}")
    return found


def _show_call(found, args: tuple) -> str:
    """The call as it would be written in the hunt's own language."""
    import json as _json

    if found.language == "python":
        shown = ", ".join(repr(a) for a in args)
    else:
        shown = ", ".join(_json.dumps(a) for a in args)
    return f"{found.name}({shown})"


@app.get("/api/bughunt")
def bughunt_list() -> dict:
    """Every hunt: the report and the program, and none of the answers.

    The report, the program and the explanations on offer are the
    question. The fixed program, the line it changes, the cause and the
    lesson are the answer, and none of them are here - the fixed program
    in particular is the whole answer in one field, which is the easy
    one to leave in by accident.
    """
    from code_coach.bughunt import hunt_families, hunts

    saved = _store.load()
    counts, last = saved.bughunt_counts(), saved.bughunt_last()
    return {
        "families": [
            {
                "name": family,
                "hunts": [
                    {
                        "id": h.id,
                        "title": h.title,
                        "language": h.language,
                        "level": h.level,
                        "report": h.report,
                        "name": h.name,
                        "signature": h.signature,
                        "arity": len(h.params),
                        "code": h.start,
                        "choices": list(h.choices),
                        "hint": h.hint,
                        "cases": len(h.cases),
                        "done": counts.get(h.id, 0),
                        "last": last.get(h.id, ""),
                    }
                    for h in hunts(family)
                ],
            }
            for family in hunt_families()
        ]
    }


@app.post("/api/bughunt/try", response_model=BugHuntTryResponse)
def bughunt_try(body: BugHuntTryRequest) -> BugHuntTryResponse:
    """Call the broken program with an input, and say if the bug shows.

    The engine decides, not a list of accepted answers: the broken
    program runs, the oracle is asked, and the two are compared. Any
    input that shows the bug counts, which is how reproducing works for
    real - there is no single right input to guess.
    """
    from code_coach.bughunt import BadInput, parse_args, try_input

    found = _hunt_or_404(body.hunt_id)
    try:
        args = parse_args(body.args, len(found.params), found.name)
        attempt = try_input(found, args)
    except BadInput as problem:
        return BugHuntTryResponse(problem=str(problem))
    return BugHuntTryResponse(
        reproduced=attempt.reproduced,
        got=attempt.got,
        want=attempt.want,
        error=attempt.error,
        changed=attempt.changed,
        call=_show_call(found, args),
    )


@app.post("/api/bughunt/line", response_model=BugHuntStepResponse)
def bughunt_line(body: BugHuntLineRequest) -> BugHuntStepResponse:
    """Whether this is the line the fix changes. Line 0 asks to be shown."""
    found = _hunt_or_404(body.hunt_id)
    if body.line == 0:
        return BugHuntStepResponse(right=False, reveal=list(found.bug_lines))
    return BugHuntStepResponse(right=body.line in found.bug_lines)


@app.post("/api/bughunt/cause", response_model=BugHuntStepResponse)
def bughunt_cause(body: BugHuntCauseRequest) -> BugHuntStepResponse:
    """Whether this is what is actually wrong. Empty asks to be shown."""
    found = _hunt_or_404(body.hunt_id)
    if not body.cause.strip():
        return BugHuntStepResponse(right=False, reveal=found.cause)
    return BugHuntStepResponse(right=body.cause.strip() == found.cause)


@app.post("/api/bughunt/fix", response_model=BugHuntFixResponse)
def bughunt_fix(body: BugHuntFixRequest) -> BugHuntFixResponse:
    """Run the fixed program against every case, the old ones included."""
    from code_coach.bughunt import run_cases

    found = _hunt_or_404(body.hunt_id)
    outcome = run_cases(found, body.code)
    done = 0
    if outcome.passed:
        progress = _store.load()
        done = progress.record_bughunt(found.id)
        _store.save(progress)
    return BugHuntFixResponse(
        passed=outcome.passed,
        count=outcome.count,
        total=len(found.cases),
        broke=outcome.broke,
        results=[
            KataCaseResult(
                args=list(r.args), want=r.want, got=r.got,
                error=r.error, passed=r.passed, changed=r.changed,
            )
            for r in outcome.results
        ],
        cause=found.cause if outcome.passed else "",
        lesson=found.lesson if outcome.passed else "",
        done=done,
    )


@app.get("/api/bughunt/answer")
def bughunt_answer(hunt_id: str = "") -> dict:
    """The fixed program, asked for rather than shipped with the list."""
    found = _hunt_or_404(hunt_id)
    return {"code": found.fixed}


# ── Regex ────────────────────────────────────────────────────


def _regex_or_404(task_id: str):
    from code_coach.regex import task

    found = task(task_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Unknown regex task {task_id}")
    return found


@app.get("/api/regex")
def regex_list() -> dict:
    """Every task: the strings on both sides, and not the answer."""
    from code_coach.regex import families, tasks

    saved = _store.load()
    counts, last = saved.regex_counts(), saved.regex_last()
    return {
        "families": [
            {
                "name": family,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "level": t.level,
                        "brief": t.brief,
                        "match": list(t.match),
                        "skip": list(t.skip),
                        "capture": dict(t.capture),
                        "hint": t.hint,
                        "done": counts.get(t.id, 0),
                        "last": last.get(t.id, ""),
                    }
                    for t in tasks(family)
                ],
            }
            for family in families()
        ]
    }


@app.post("/api/regex/check", response_model=RegexCheckResponse)
def regex_check(body: RegexCheckRequest) -> RegexCheckResponse:
    """Run the pattern in the real engine of the language picked."""
    from code_coach.regex import check, engine_for

    found = _regex_or_404(body.task_id)
    engine = engine_for(body.language)
    verdict = check(found, body.pattern, engine)
    done = 0
    if verdict.passed:
        progress = _store.load()
        done = progress.record_regex(found.id)
        _store.save(progress)
    return RegexCheckResponse(
        passed=verdict.passed,
        broke=verdict.broke,
        rows=[
            RegexRow(text=text, should_match=should, found=hit, group=group,
                     want_group=want, right=right)
            for text, should, hit, group, want, right in verdict.rows
        ],
        engine=engine,
        lesson=found.lesson if verdict.passed else "",
        done=done,
    )


@app.get("/api/regex/answer")
def regex_answer(task_id: str = "") -> dict:
    return {"answer": _regex_or_404(task_id).answer}


# ── Two-part puzzles ─────────────────────────────────────────


def _puzzle_or_404(puzzle_id: str):
    from code_coach.puzzles import puzzle

    found = puzzle(puzzle_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Unknown puzzle {puzzle_id}")
    return found


def _puzzle_language(language: str) -> str:
    from code_coach.puzzles import supports

    if not supports(language):
        raise HTTPException(
            status_code=400, detail=f"Puzzles are not written in {language} yet")
    return language


@app.get("/api/puzzles")
def puzzle_list() -> dict:
    """Every puzzle, both parts' briefs, and none of the answers.

    Part two's brief is sent too: the screen keeps it behind part one,
    and knowing the question early is no help with part one anyway.
    """
    from code_coach.puzzles import NAMES, puzzles

    saved = _store.load()
    counts, last = saved.puzzle_counts(), saved.puzzle_last()
    return {
        "languages": list(NAMES),
        "names": {lang: list(names) for lang, names in NAMES.items()},
        "puzzles": [
            {
                "id": p.id,
                "title": p.title,
                "level": p.level,
                "story": p.story,
                "parts": [
                    {"brief": part.brief, "example": part.example,
                     "params": list(part.params)}
                    for part in (p.one, p.two)
                ],
                "done": counts.get(p.id, 0),
                "last": last.get(p.id, ""),
            }
            for p in puzzles()
        ],
    }


@app.post("/api/puzzles/check", response_model=PuzzleCheckResponse)
def puzzle_check(body: PuzzleCheckRequest) -> PuzzleCheckResponse:
    """Run one part's cases. The puzzle counts as done when part two passes."""
    from code_coach.puzzles import run_part

    found = _puzzle_or_404(body.puzzle_id)
    language = _puzzle_language(body.language)
    part = 2 if body.part == 2 else 1
    outcome = run_part(found, part, body.code, language)
    done = 0
    if outcome.passed and part == 2:
        progress = _store.load()
        done = progress.record_puzzle(found.id)
        _store.save(progress)
    return PuzzleCheckResponse(
        passed=outcome.passed,
        count=outcome.count,
        total=len(found.part(part).cases),
        broke=outcome.broke,
        results=[
            KataCaseResult(
                args=list(r.args), want=r.want, got=r.got,
                error=r.error, passed=r.passed, changed=r.changed,
            )
            for r in outcome.results
        ],
        lesson=found.lesson if outcome.passed and part == 2 else "",
        done=done,
    )


@app.get("/api/puzzles/answer")
def puzzle_answer(puzzle_id: str = "", part: int = 1, language: str = "python") -> dict:
    from code_coach.puzzles import answer_for

    found = _puzzle_or_404(puzzle_id)
    return {"code": answer_for(found, 2 if part == 2 else 1, _puzzle_language(language))}


# ── SQL case files ───────────────────────────────────────────


def _case_or_404(case_id: str):
    from code_coach.casefiles import case

    found = case(case_id)
    if found is None:
        raise HTTPException(status_code=404, detail=f"Unknown case {case_id}")
    return found


def _step_or_404(found, step: int):
    if not 0 <= step < len(found.steps):
        raise HTTPException(status_code=404, detail=f"No step {step + 1}")
    return found.steps[step]


@app.get("/api/cases")
def case_list() -> dict:
    """Every case: story, tables and questions. No answers, no queries."""
    from code_coach.casefiles import cases, tables

    saved = _store.load()
    counts, last = saved.case_counts(), saved.case_last()
    return {
        "cases": [
            {
                "id": c.id,
                "title": c.title,
                "level": c.level,
                "story": c.story,
                "tables": tables(c),
                "steps": [{"question": s.question, "hint": s.hint} for s in c.steps],
                "done": counts.get(c.id, 0),
                "last": last.get(c.id, ""),
            }
            for c in cases()
        ]
    }


@app.post("/api/cases/query", response_model=CaseQueryResponse)
def case_query(body: CaseQueryRequest) -> CaseQueryResponse:
    """Any query against the case's own tables, rolled back afterwards."""
    from code_coach.casefiles import run_query

    out, err, _ = run_query(_case_or_404(body.case_id), body.sql)
    return CaseQueryResponse(out=out, err=err)


@app.post("/api/cases/answer", response_model=CaseAnswerResponse)
def case_answer(body: CaseAnswerRequest) -> CaseAnswerResponse:
    """One step's answer. The case counts as done when its last step is right."""
    from code_coach.casefiles import same

    found = _case_or_404(body.case_id)
    step = _step_or_404(found, body.step)
    if not same(body.answer, step.answer):
        return CaseAnswerResponse(right=False)
    last_step = body.step == len(found.steps) - 1
    done = 0
    if last_step:
        progress = _store.load()
        done = progress.record_case(found.id)
        _store.save(progress)
    return CaseAnswerResponse(
        right=True,
        lesson=step.lesson,
        ending=found.ending if last_step else "",
        done=done,
    )


@app.get("/api/cases/reveal")
def case_reveal(case_id: str = "", step: int = 0) -> dict:
    """A query that finds the step's answer, asked for rather than shipped."""
    found = _case_or_404(case_id)
    return {"query": _step_or_404(found, step).reference}


@app.get("/api/trace")
def trace_list() -> dict:
    """Every moment, with the question and without the answer.

    The program, the question and the choices are what you are given.
    The value and the explanation are what you are working out, so
    neither is here.
    """
    from code_coach.trace import trace_families, traces

    saved = _store.load()
    counts, last = saved.trace_counts(), saved.trace_last()
    return {
        "families": [
            {
                "name": family,
                "traces": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "code": t.code,
                        "question": t.question,
                        "at_line": t.at_line,
                        "occurrence": t.occurrence,
                        "variable": t.variable,
                        "language": t.language,
                        "choices": list(t.choices),
                        "done": counts.get(t.id, 0),
                        "last": last.get(t.id, ""),
                        "level": t.level,
                    }
                    for t in traces(family)
                ],
            }
            for family in trace_families()
        ]
    }


@app.post("/api/trace/check", response_model=TraceCheckResponse)
def trace_check(body: TraceCheckRequest) -> TraceCheckResponse:
    """Compare the guess with what the tracer reports at that moment."""
    from code_coach.trace import one_trace

    found = one_trace(body.trace_id)
    if found is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown moment {body.trace_id}"
        )
    passed = body.answer.strip() == found.expect
    done = 0
    if passed:
        progress = _store.load()
        done = progress.record_trace(found.id)
        _store.save(progress)
    return TraceCheckResponse(
        passed=passed,
        done=done,
        expect=found.expect,
        answer=body.answer,
        why=found.why,
    )


@app.get("/api/session")
def session_queue(size: int = 20) -> dict:
    """The next things to do, across every practice at once.

    No answers here — it is a list of what to open, and opening it is
    what serves the question. Size is capped so a stray query string
    cannot ask for the whole app in one response.
    """
    from code_coach.session import SOURCES, queue

    saved = _store.load()
    wanted = max(1, min(int(size), 60))
    return {
        "size": wanted,
        "practices": [
            {"key": s.key, "label": s.label} for s in SOURCES
        ],
        "items": queue(saved, wanted),
    }
