# Code Coach

**Product vision:** An AI coding coach that watches what you write and suggests
the next useful change — always based on your current code, not a fixed script.

A local, coach-first **IAE** (Integrated Agent Environment) for learning Python:
an in-app editor, a curriculum of classes and lessons, a difficulty meter, an
"explain my code" walkthrough, and student progress that survives restarts.

---

## What is an IAE here?

Not a full IDE (no file tree, git, debugger). Not a chat-first agent workspace.

**Integrated Agent Environment** means:

1. You type in an in-app Monaco editor.
2. The coach re-scores your steps from your *current* code on every keystroke.
3. Run captures output/errors in the same shell.
4. "Explain my code" gives a plain-English, line-by-line walkthrough of what you
   wrote and why the output looks the way it does.
5. Progress is saved on disk so you resume where you left off — and each lesson's
   work is kept, so you can go back and study it.

The agent is the **coach**, not a code generator you babysit.

---

## The learning model

Work flows **Class → Lesson → Exercise**. Two kinds of lesson:

| Lesson kind | What you do | How it's checked |
|-------------|-------------|------------------|
| **Type-along** (dictation) | Copy the exact line shown, one at a time | Exact-line match |
| **Build** | Solve a goal in your own code | **AST-based** structural checks (and, for some, output) |

- **Class 1 · Foundations · Lesson 1** is an *endless* type-along — it never
  graduates; new windows of lines load forever. A **difficulty meter (1–5)**
  controls single lines → multi-line blocks → functions.
- **Build lessons** validate the *structure* of your code by parsing it, not by
  string-matching — so keywords inside a comment or string don't count as a
  solution. Real code is required.
- **Free mode** turns the coach off for plain coding. **Save / Load…** stores
  named scripts in your browser.

**Progress file:** `~/.code_coach/student_progress.json`

```
┌──────────────────────────────────────────────────────────────┐
│  COACH STRIP   Class · Lesson · Exercise · difficulty · status │
│                Explain my code · Ask coach                      │
├──────────────────────────────────────────────────────────────┤
│  EDITOR        Monaco (Python) — type here                     │
├──────────────────────────────────────────────────────────────┤
│  TERMINAL      Run output / errors                             │
└──────────────────────────────────────────────────────────────┘
```

---

## Quick start (web IAE)

```bash
cd "/Users/justinmonahan/Documents/GitHub/code-coach"

# one-shot helper (starts API on 8765 + UI on 5173)
chmod +x scripts/dev.sh
./scripts/dev.sh
```

Or two terminals:

```bash
# terminal 1 — API (127.0.0.1:8765)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port 8765

# terminal 2 — UI (http://localhost:5173)
cd web && npm install && npm run dev
```

Open **http://localhost:5173**.

- Type in the editor → the coach re-scores live and advances when a line is done.
- **Run** or **⌘⏎** → execute and show output.
- **Explain my code** → line-by-line walkthrough + why the output looks that way.
- **Start over** → reset the current lesson to its starter (the only thing that
  clears your work).

Your work is saved per lesson in `localStorage` and restored when you return.

---

## CLI (still works)

The original file-watch CLI is still here (separate from the web app):

```bash
cd "/Users/justinmonahan/Documents/GitHub/code-coach"
source .venv/bin/activate            # optional; pure stdlib for evaluate

python3 -m code_coach                 # check Learn-to-code day-01 if found nearby
python3 -m code_coach --watch         # live update on save
python3 -m code_coach --watch --file "/path/to/practice.py"
```

---

## Project layout

```text
code-coach/
  README.md
  requirements.txt
  scripts/dev.sh
  code_coach/
    __main__.py
    cli.py                # file-watch CLI
    engine.py             # run code + score legacy day lessons (used by CLI)
    checks.py             # AST predicates for build-lesson validation
    explain.py            # plain-English code walkthrough (AST + traced run)
    lessons/day01.py      # legacy day lesson (CLI only)
    curriculum/           # Class → Lesson catalog + navigation runtime
    dictation/            # endless type-along generators + local coach FAQ
    skills/drills.py      # build-lesson drill bank (AST-checked)
    practice/             # scoring + adaptive coach messages
    progress/store.py     # atomic JSON progress persistence
    api/
      server.py           # FastAPI — practice/explain/chat/skills/progress
      schemas.py
  web/                    # Vite + React 19 + Monaco IAE shell
    src/
      App.tsx
      components/
  tests/                  # stdlib unittest (no pytest)
```

---

## API (local, binds to 127.0.0.1 only)

| Method | Path | Notes |
|--------|------|-------|
| `GET`  | `/api/health` | version check |
| `GET`  | `/api/skills` | list skills |
| `GET`  | `/api/progress` · `PUT` | read / update settings (mode, difficulty) |
| `GET`  | `/api/curriculum` | Class → Lesson tree |
| `GET`  | `/api/practice/current` | active session (steps, starter, position) |
| `POST` | `/api/practice/evaluate` | `{drill_id, code, run?, exercise_index?}` → checks + coach + optional stdout |
| `POST` | `/api/practice/navigate` · `goto-lesson` · `more` · `review` · `back` | move around the curriculum |
| `POST` | `/api/practice/complete` | mark done + advance |
| `POST` | `/api/explain` | `{code}` → line-by-line walkthrough + output notes |
| `POST` | `/api/chat` | local keyboard/Python FAQ bot (no cloud) |

Student code runs in a temp file with a 3-second timeout.

---

## Develop

- Python 3.10+
- Node 18+ for the web shell
- No API keys required — everything is local.
- **Tests:** `.venv/bin/python -m unittest discover -s tests` (stdlib unittest;
  pytest is not used).
- **Typecheck UI:** `cd web && npx tsc --noEmit`.
