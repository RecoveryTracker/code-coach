"""
FastAPI server for the Code Coach IAE.

  uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port 8765
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from code_coach import __version__
from code_coach.api.schemas import (
    ChatRequest,
    ChatResponse,
    CheckItem,
    DrillEvaluateRequest,
    DrillEvaluateResponse,
    ExplainRequest,
    ExplainResponse,
    HealthResponse,
    PracticeSession,
    ProgressResponse,
    ProgressSettingsUpdate,
    SkillInfo,
    WaypointInfo,
)
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
from code_coach.progress.store import ProgressStore
from code_coach.skills.catalog import get_skill, list_skills
from code_coach.skills.drills import get_drill, set_class1_batch
from code_coach.api.schemas import (
    GotoLessonRequest,
    NavigateRequest,
    ReviewRequest,
    SupportLinkInfo,
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
    drill = get_active_drill(progress)
    if progress.current_drill_id != drill.id:
        progress.current_drill_id = drill.id
        _store.save(progress)

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
        steps.append(
            WaypointInfo(
                id=s.id,
                label=s.label,
                tip=getattr(s, "why", None) or getattr(s, "concept", None),
                keyboard_tip=getattr(s, "hint", None),
                hint_lines=hint_lines,
                supports=supports,
                kind=kind,
            )
        )

    title = meta.get("display_title") or drill.title
    if role == "build":
        level_for_style = max(level, 2)
    else:
        level_for_style = 1 if role in ("dictation", "review") else level

    # Lesson 1 of every class is the endless type-along fallback layer.
    endless = int(meta.get("lesson_number") or 1) == 1 and role == "dictation"
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
        curriculum=catalog_payload(),
        exercise_count=len(steps),
        endless=endless,
        dictation_level=d_level,
        dictation_level_label=DICTATION_LEVEL_LABELS.get(d_level, f"Level {d_level}"),
        lines_done=progress.lines_for(meta["class_id"]),
    )


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, version=__version__)


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


@app.post("/api/practice/more", response_model=PracticeSession)
def practice_more_lines() -> PracticeSession:
    """Next window of the current class's Lesson-1 type-along (endless)."""
    from code_coach.dictation.bank import WINDOW_SIZE

    progress = _store.load()
    class_id = progress.curriculum_class or "foundations"
    progress.curriculum_lesson = 1
    progress.review_skill = None
    # Count finished window toward this class's lifetime lines
    progress.add_lines(class_id, WINDOW_SIZE)
    batch = progress.bump_batch(class_id)
    level = max(1, min(5, int(getattr(progress, "dictation_level", 1) or 1)))
    if class_id == "foundations":
        set_class1_batch(seed="local-student", batch=batch, level=level)
        progress.current_drill_id = "class-1-dictation"
    else:
        # get_active_drill regenerates the window for this class/batch
        progress.current_drill_id = None
    progress.exercise_index = 0
    _store.save(progress)
    return _session_from_progress()


@app.get("/api/curriculum")
def curriculum_tree() -> list[dict]:
    return catalog_payload()


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


@app.post("/api/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    """Local tips chatbot (keyboard + Python FAQ)."""
    return ChatResponse(reply=chat_reply(body.message or ""))


@app.post("/api/explain", response_model=ExplainResponse)
def explain(body: ExplainRequest) -> ExplainResponse:
    """Plain-English walkthrough of the student's current code + why it
    outputs what it does. Local AST + traced run — no cloud AI."""
    from code_coach.explain import explain_code

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
        stdout, stderr, exit_code = run_code(body.code)

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
