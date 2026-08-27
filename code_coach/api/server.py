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
    PracticeSession,
    ProgressResponse,
    ProgressSettingsUpdate,
    LanguageInfo,
    SkillInfo,
    StudyInfo,
    VisualizeRequest,
    VisualizeResponse,
    WaypointInfo,
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
from code_coach.progress.store import ProgressStore, StudentProgress
from code_coach.skills.catalog import get_skill, list_skills
from code_coach.skills.drills import get_drill, set_class1_batch
from code_coach.api.schemas import (
    GotoLessonRequest,
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
    TypingThemeInfo,
)
from code_coach.typing.drills import (
    MODES_BY_ID as TYPING_MODES_BY_ID,
    SECTIONS_BY_ID as TYPING_SECTIONS_BY_ID,
    THEMES_BY_ID as TYPING_THEMES_BY_ID,
    build_drill as build_typing_drill,
    catalog as typing_sections,
    teach_languages as typing_teach_languages,
    theme_catalog as typing_themes,
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


_store = ProgressStore()


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


@app.get("/api/typing/drill", response_model=TypingDrillResponse)
def typing_drill(
    section: str,
    mode: str,
    theme: str = "mixed",
    seed: str = "typing",
    count: int = 30,
) -> TypingDrillResponse:
    """One generated run. `seed` varies the draw, so a retry isn't identical."""
    if section not in TYPING_SECTIONS_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing section {section!r}")
    if mode not in TYPING_MODES_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing mode {mode!r}")
    if theme not in TYPING_THEMES_BY_ID:
        raise HTTPException(status_code=404, detail=f"no typing theme {theme!r}")
    drill = build_typing_drill(
        section, mode, theme_id=theme, seed=seed, count=max(4, min(count, 120))
    )
    return TypingDrillResponse(
        id=drill.id,
        section=drill.section,
        section_name=TYPING_SECTIONS_BY_ID[drill.section].name,
        mode=drill.mode,
        mode_name=TYPING_MODES_BY_ID[drill.mode].name,
        theme=drill.theme,
        theme_name=TYPING_THEMES_BY_ID[drill.theme].name,
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


@app.get("/api/reference")
def reference() -> dict:
    """The cheat sheet for the language being practised.

    A desk mat rather than a lesson: the lines worth having in your head,
    densest and most-used first. Flashcards are drawn from the same entries,
    so there is one place to add something rather than two.
    """
    from code_coach.reference import sheet_for

    progress = _store.load()
    language = getattr(progress, "language", "python") or "python"
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


@app.get("/api/lessons")
def lessons() -> list[dict]:
    """Every pattern lesson, for the Lessons screen.

    Not tied to the drill you are on: this is the reading, browsed on its own,
    the way the typing trainer is its own place rather than a panel.
    """
    from code_coach.leetcode.bank import lessons_catalogue

    progress = _store.load()
    return lessons_catalogue(getattr(progress, "language", "python") or "python")


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
    lang = get_language(getattr(_store.load(), "language", "python"))
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
