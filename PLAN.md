# Code Coach — Build Plan (audit remediation)

Context for the builder: local-first Python learning IDE. FastAPI backend
(`code_coach/`, runs on 127.0.0.1:8765 via `uvicorn code_coach.api.server:app`),
Vite + React 19 + Monaco frontend (`web/`, on :5173, proxies `/api` to backend).
No cloud, no API keys. Venv at `.venv/`; **pytest is NOT installed — tests use
stdlib `unittest`** (`.venv/bin/python -m unittest discover -s tests`). Frontend
typecheck: `cd web && npx tsc --noEmit`. Verify UI changes in the browser preview.

**Already shipped this session (do not redo):** type-along advance fixes
(Monaco auto-close off, independent dictation scoring, per-lesson work is saved
& restored on navigation, coach message follows current exercise), and a
one-time reset of the `class1_lines_done` counter. Tests live in
`tests/test_advance.py` (13 tests, green). Keep them green.

Work the phases in order. Each is independently shippable; commit per phase.

### Status (updated this session)
- ✅ **Phase 1 — Validation rigor** — DONE. AST checks in `code_coach/checks.py`;
  all build drills rewritten; `tests/test_checks.py` (real solutions pass, gaming
  blocked). The optional `expect_output` behavioral path was NOT added yet.
- ✅ **Phase 2 — Dead code + drift** — DONE. 6 orphaned components deleted, legacy
  lesson API removed from `server.py`, `CoachLog*` types removed, README rewritten.
  (Left in place: unused `EvaluateResponse`/`LessonDetail`/etc. Pydantic classes in
  `schemas.py` — harmless; remove if desired.)
- ✅ **Phase 3 — Exec hardening** — DONE. Host-header guard (`host_allowed` +
  middleware) blocks DNS-rebinding; runner has CPU/output caps + process-group
  kill. Memory cap (RLIMIT_AS) is Linux-only — macOS ignores it (documented).
  `tests/test_hardening.py`. A per-session token was NOT added (Host check chosen).
- ✅ **Phase 4 — Frontend resilience** — DONE. `ErrorBoundary` wraps App;
  non-color status glyph (✓/✕/…/•) in `CurriculumNav`.
- ✅ **Phase 5 — Collapse difficulty axes** — DONE. StudentProgress v3: stored
  `difficulty` alias removed (API still serves a computed alias); foundations-only
  `class1_batch`/`class1_lines_done` replaced by per-class `dictation_batches`/
  `dictation_lines` dicts with v2→v3 migration (verified against the real file;
  backup kept at ~/.code_coach/student_progress.backup-*.json).
  `tests/test_progress_migration.py`.
- ✅ **(New, user-requested) Per-class endless dictation** — DONE. Lesson 1 of
  EVERY class is now an infinite verbatim type-along drilling that class's own
  syntax (decisions: comparisons/booleans/if-elif-else; loops: for/while/range/
  accumulate/loop-functions), with curated spines (the old finite L1 content) on
  the first window and generated variety after. Difficulty slider + "more lines"
  + lifetime counter are per-class. Catalog build lessons (decisions-l2, loops-l2,
  foundations-l3) also upgraded to AST checks.
- ✅ **Phase 6 — Test backfill** — DONE. Added `test_checks`, `test_hardening`,
  `test_dictation_bank`, `test_curriculum_nav`, `test_explain`. Suite: 45 tests.
- ✅ **Phase 7 — Packaging & ops** — DONE. `pyproject.toml` (installable,
  `code-coach` CLI entry point, ruff+mypy config), `Makefile` (`make check` =
  ruff + unittest + tsc; `make type` opt-in), dev.sh port fallback via
  API_PORT/UI_PORT env (vite.config reads VITE_API_PORT/VITE_UI_PORT),
  production build verified. BONUS: Monaco was silently CDN-loaded at runtime
  (audit had this wrong) — now bundled locally via `web/src/monaco-setup.ts`,
  so the editor works fully offline (verified: zero jsdelivr requests).
- ✅ **Phase 8 — Pedagogy** — DONE (first pass).
  - Hint escalation on build lessons: Hint → nudge (concept) → "More help"
    (first solution line + …) → "Show solution" (exact lines). Resets per
    exercise; the free tip is hidden on build lessons so level 1 isn't spoiled.
  - Progress panel (top-bar button): per-skill mastery bars + xp, per-class
    type-along lifetime lines, total completions.
  - Light spaced repetition: `review_due` in progress payload (skills
    practiced before but idle ≥3 days, `REVIEW_DUE_AFTER_DAYS` in
    practice/session.py); shown as clickable chips in the panel that jump to
    that class's endless type-along.
  - NOT done (future): full SRS scheduling, per-step wrong-attempt tracking.

Remaining detail for the not-done phases is below.

---

## Phase 1 — Validation rigor (HIGHEST VALUE) 🔴 ✅ DONE

**Problem (confirmed live):** build-drill checks in `code_coach/skills/drills.py`
are bare substring matches on raw source. `print("if this else that")` completes
the if/else drill; a comment `# use while later` completes the while drill. The
app rewards keyword presence, not real code — it can't tell a student their logic
is wrong. This is the core gap vs Codecademy/exercism/boot.dev.

**Fix — AST-based structural checks (primary), optional output checks (secondary).**
The Explain feature (`code_coach/explain.py`) already proves AST parsing works
here; reuse that muscle.

Steps:
1. New module `code_coach/checks.py` with AST predicates that return `False` on
   `SyntaxError` (never raise). Parse once, walk the tree:
   - `uses_for(code)`, `uses_while(code)`, `uses_if(code)`, `uses_if_else(code)`
     (an `ast.If` whose `.orelse` is non-empty), `uses_and(code)`/`uses_or(code)`
     (`ast.BoolOp`), `uses_nested_for(code)` (a For inside a For),
   - `defines_function(code, name=None)` (`ast.FunctionDef`), `calls_function(code, name)`
     (`ast.Call`), `returns_value(code)` (`ast.Return` with a value),
   - `assigns_variable(code, name)` (`ast.Assign`/`ast.AnnAssign` target),
   - `uses_list_literal(code)` (`ast.List`), `uses_dict_literal(code)` (`ast.Dict`),
   - `uses_subscript(code)` (`ast.Subscript`), `calls_method(code, name)`
     (`ast.Call` on `ast.Attribute` with matching `.attr`, e.g. `append`, `pop`).
   Because AST ignores text inside string literals and comments, the gaming cases
   above stop passing automatically.
2. Rewrite every `lambda`/`_has_*` check in `drills.py` (lines ~43–692) to call
   the new predicates. Delete the old `_has_if/_has_while/_has_for/_has_def/
   _has_list_literal/_has_dict_literal/_has_substr` helpers once unused.
   - Keep `_has_assign` behavior but back it with `assigns_variable`.
   - Compound drills that check two facts (e.g. `func-loop-4`: def + loop + return)
     become `defines_function(c) and (uses_for(c) or uses_while(c)) and returns_value(c)`.
3. **Do NOT touch dictation checks.** `make_block_check`/`check_block` in
   `code_coach/dictation/bank.py` are exact-line matches and are correct as-is;
   the type-along is deliberately copy-the-line.
4. (Secondary, same phase if time) Add optional behavioral assertion: extend
   `DrillStep` with `expect_output: str | None = None`. In
   `code_coach/practice/session.py::evaluate_drill`, when a step has
   `expect_output` and the student ran the code, compare normalized `stdout`.
   Wire it for a few drills with deterministic output (`loops-for-1` → `0\n1\n2`,
   `loops-accumulate-3` → `15`). This makes "your output is wrong" possible.
   Reuse the existing sandboxed `run_code` (already called in `practice_evaluate`).

Acceptance:
- `print("if this else that")` does NOT complete `cond-else-2`.
- A comment mentioning `while` does NOT complete `loops-while-2`.
- Real correct solutions for every build drill still complete (regression).
- Syntactically broken code returns all-False checks, no 500.

Tests (`tests/test_checks.py`, new): for each build drill, assert (a) its example
solution passes all steps, (b) a string/comment containing the keywords does not,
(c) a plausible-but-wrong variant does not. Add SyntaxError-returns-False cases.

---

## Phase 2 — Dead code + drift cleanup 🟡 (cheap, high clarity)

Confirmed unused (imported by 0 files):
- `web/src/components/TopBar.tsx`, `SimpleCoach.tsx`, `WaypointPanel.tsx`,
  `PracticeControls.tsx`, `ResizablePanes.tsx`, `CoachPane.tsx` — delete all six.
- `web/src/types.ts`: remove `CoachLogKind` and `CoachLogEntry` (legacy, unused).

Legacy backend lesson system (current UI uses none of it — verify with a grep for
`/api/lessons`, `/api/evaluate`, `/api/run` in `web/src` before deleting):
- In `code_coach/api/server.py` remove endpoints `list_lessons` (`/api/lessons`),
  `get_lesson_detail` (`/api/lessons/{day}`), `evaluate_endpoint` (`/api/evaluate`),
  and `run_endpoint` (`/api/run`) — all ~lines 451–500 — plus the now-unused
  `LESSONS`/`get_lesson`/`UnknownLessonError`/`evaluate_code`/`result_to_dict`
  imports and the `STARTER_CODE`/`_day_numbers`/`_starter_for` helpers.
  **Keep `run_code`** — it's still used by `practice_evaluate` and `explain`.
- After removal, `code_coach/lessons/` + `day01.py` and the CLI's day-based paths
  may be fully dead. Confirm nothing else imports them; if truly orphaned, delete.
  (Lower confidence — grep first: `grep -rn "lessons import\|day01\|LESSONS" code_coach`.)

README: `README.md` documents the OLD app (`/api/lessons`, `day01.py`,
`python3 -m code_coach --watch` as the main flow). Rewrite to describe the actual
current app: curriculum (Class→Lesson→Exercise), endless type-along, the practice
API (`/api/practice/*`, `/api/explain`, `/api/chat`), and the real quick-start
(`scripts/dev.sh`). Update the API table and project-layout tree.

Acceptance: `npx tsc --noEmit` clean; app still boots and runs; no import errors
on backend start (`.venv/bin/python -c "import code_coach.api.server"`).

---

## Phase 3 — Local-exec hardening 🔴

**Problem:** code execution (`practice_evaluate` with `run=true`, plus `explain`)
runs arbitrary Python with the user's full privileges. Confirmed: it returns the
real home dir and runs `import os`. CORS is browser-only; any local process — or a
webpage via DNS-rebinding — can POST to localhost:8765 and execute code. Only
guards today: 3s timeout, 127.0.0.1 bind. Also no memory/output cap
(`x = "a"*10**10` isn't stopped by a timeout).

Fix (pick the lightest that closes it for a local single-user tool):
1. **Host-header check** (simplest): add FastAPI middleware rejecting requests
   whose `Host` isn't `127.0.0.1:8765`/`localhost:8765`. Blocks DNS-rebinding.
2. **Per-session token** (stronger): server mints a random token at startup,
   injects it into the served page / an `/api/session` call; UI sends it as a
   header; middleware requires it on execution endpoints. `api.ts::request`
   adds the header centrally.
3. **Resource caps** in `run_file` (`code_coach/engine.py`): cap captured
   stdout/stderr length (truncate with a notice), and on POSIX set
   `resource.setrlimit(RLIMIT_AS, ...)` + `RLIMIT_CPU` via `preexec_fn`, and
   `start_new_session=True` so a process-group kill reaps grandchildren on timeout.

Acceptance: normal Run/Explain still work; a request with a foreign `Host` header
is rejected; a 10GB-string program is killed/capped, not OOM. Add a unittest for
the output cap and the setrlimit path (skip on non-POSIX).

---

## Phase 4 — Frontend resilience 🟡

- Add `web/src/components/ErrorBoundary.tsx` (class component with
  `componentDidCatch`) rendering a recoverable message + "Reload" button. Wrap
  `<App/>` in `web/src/main.tsx`. One uncaught render error currently white-screens
  the whole app.
- Non-color status cue: coach status is red/green only (`cur-nav-status` classes in
  `workspace.css`). Add a text/glyph cue (✓ / •) alongside color so it's readable
  without color. Nav aria-labels are already good — keep them.

Acceptance: throwing a test error in a child shows the boundary, not a blank page;
status is distinguishable in grayscale.

---

## Phase 5 — Collapse the difficulty axes 🟡 (refactor)

**Problem:** three overlapping concepts — `coach_level` (1–2), `difficulty` (1–5,
self-described "alias"), `dictation_level` (1–5). `store.py` comments apologize for
it. This confusion produced the "17" counter bug and makes the model hard to reason
about.

Fix: pick the two that are actually orthogonal and name them clearly:
- **coach style** (how much the coach reveals) — keep as `coach_level` or rename
  `coach_style_level`.
- **content difficulty** (`dictation_level`, 1–5) — the type-along slider.
- Delete the standalone `difficulty` field; compute any back-compat alias at the
  API boundary only (`ProgressSettingsUpdate`/`ProgressResponse` in `schemas.py`),
  not in the stored model (`store.py::StudentProgress`).
- Make the lifetime line counter authoritative on the server (return a single
  `lifetime_lines` in the practice session payload) instead of the UI computing
  `lines_done + position` in `CurriculumNav.tsx` (~lines 70–72).

This is a breaking change to the stored JSON — bump `StudentProgress.version` and
handle old files in `from_dict` (map old `difficulty` → the surviving field).

Acceptance: existing `~/.code_coach/student_progress.json` still loads; counter and
sliders behave; no field named both "difficulty" and "coach_level" in the model.

---

## Phase 6 — Test backfill 🟡

Add stdlib-unittest coverage (no pytest) for the currently-untested core:
- `tests/test_checks.py` — Phase 1 (see above).
- `tests/test_dictation_bank.py` — `build_dictation_steps`: no duplicate examples
  in a window; level 1–5 each produce valid, parseable lines; spine appears only on
  batch 0 at levels ≤2; window size honored.
- `tests/test_curriculum_nav.py` — `navigate_step`/`goto_position`/`back_from_review`
  in `curriculum/runtime.py`: class/lesson bounds clamp; crossing lesson/class
  boundaries lands correctly; review round-trips to the right return lesson.
- `tests/test_explain.py` — `explain_code` on the battery from earlier (loops,
  vars, error, no-print, syntax error, infinite loop → timeout note); assert shape
  and key attributions, not exact prose.

Acceptance: `.venv/bin/python -m unittest discover -s tests` green; meaningfully
covers generators + navigation + explain + checks.

---

## Phase 7 — Packaging & ops 🟢 (do last)

- Add `pyproject.toml` (name, version, deps from `requirements.txt`, console entry
  point for the server) so the backend is installable, not repo-root-bound.
- Add `ruff` + `mypy` config and a minimal GitHub Actions (or local `make check`)
  running ruff, mypy, and unittest.
- Port fallback: if 8765/5173 busy, pick the next free port (or read from env) in
  `scripts/dev.sh` / `vite.config.ts`, instead of hard failing.
- Confirm `npm run build` produces a working bundle and document serving it
  (currently only the dev servers are exercised).

---

## Phase 8 — Pedagogy & motivation 🟢 (longer-term, optional)

Depends on Phase 1 (real validation) landing first.
- **Hint escalation:** nudge → bigger hint → reveal solution, instead of one Hint
  popover.
- **Progress visualization:** per-skill mastery %, completion map, streak — the
  motivation lever commercial apps lean on. Data mostly exists in `progress_summary`.
- **Spaced repetition:** use the existing review mechanism to *schedule* resurfacing
  of weak skills, not just manual detours.
- **Explain "run twice" note:** `explain.py` re-executes code that Run already ran;
  fine for prints, but guard/skip for side-effecting code, or cache the last run.

---

## Regression guards (must stay true after every phase)
- Type-along advance behavior + per-lesson save/restore (Phase-0 work) intact;
  `tests/test_advance.py` stays green.
- Monaco auto-close stays OFF (typing trainer requirement).
- `~/.code_coach/student_progress.json` from before still loads without data loss.
- App boots with both servers and runs a drill end-to-end.
