# Code Coach

A local, coach-first environment for learning Python by typing real code. It
watches what you write, checks it as you go, and explains what's wrong in terms
of the line you actually got wrong.

Two tracks:

- **Fundamentals** — Foundations, Decisions, Loops.
- **LeetCode patterns** — 52 solutions across 13 patterns (Two Pointers, Hash
  Maps, Sliding Window, Binary Search, Tree DFS/BFS, Graphs, Backtracking,
  Heaps, Topological Sort, DP, and more), drilled as verbatim typing practice
  for muscle memory.

Everything runs on your machine. No API keys, no cloud calls.

---

## Setup

> **On Windows 11?** Follow **[SETUP-WINDOWS.md](SETUP-WINDOWS.md)** instead —
> step-by-step from a machine with nothing installed, including troubleshooting.

You need **Python 3.10+** and **Node 18+**. On Windows, tick *"Add to PATH"* in
both installers, then open a **new** terminal so the PATH change takes effect.

```bash
git clone https://github.com/RecoveryTracker/code-coach.git
cd code-coach
```

**Windows**

```bash
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && cd web && npm install
```

**macOS / Linux**

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd web && npm install
```

## Running it

**Windows** — double-click `start.bat`, or:

```bash
start.bat
```

**macOS / Linux**

```bash
./scripts/dev.sh
```

Either way you get the API on `127.0.0.1:8765`, the UI on `localhost:5173`, and
a browser tab. To run them by hand instead:

```bash
.venv/bin/python -m uvicorn code_coach.api.server:app --reload --host 127.0.0.1 --port 8765
```

```bash
cd web && npm run dev
```

> **Heads up:** the venv's Python is not the same as the `python` on your PATH.
> If you see `No module named uvicorn`, you're using the wrong one — go through
> `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows).

---

## How practice works

Navigation is a breadcrumb: **Class › Lesson › Exercise**, with one back/forward
pair that walks the whole curriculum in order — at the end of a lesson it rolls
into the next one.

Each class has three lessons:

| Lesson | What you do | How it's checked |
|--------|-------------|------------------|
| **1 · Type-along** | Copy exactly what's shown. Never ends — new material keeps loading. | Verbatim, indentation included |
| **2 · Full solutions** | Type each solution start to finish | Verbatim |
| **3 · Build from memory** | Write it yourself from the idea alone | AST structural checks, not string matching |

**Chunk size** (on the Type this panel, lesson 1 only) sets how much you type
before it's checked — a single line up to a whole function.

Nothing auto-advances. When your code is right, **Continue** lights up and waits,
so the finished code stays on screen to read.

### When you get it wrong

The coach names the line, not the whole block:

```
Not yet — line 8 doesn't match.
should be:  return []
you typed:  return[]
                  ^ here (character 7)
```

Indentation mistakes are called out separately, since stripped of whitespace the
two lines look identical.

### Checking your own work

On LeetCode problems the **Problem** panel carries the question restated in
plain words, worked examples, the pattern's template and pitfalls, and two
buttons:

- **Check my work** — diffs your whole attempt against the real solution and
  points at the first line that differs. Works even with scratch code around it.
- **Show answer** — the full reference solution, hidden until you ask.

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ Explain · Ask coach · status · Continue    Code Coach    Save … Run  │
│ Hash Maps › 1. Type-along › 3 / 8   ‹ ›                              │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │ coach message — fixed height, never shifts the editor            │ │
│ └──────────────────────────────────────────────────────────────────┘ │
├────────────────────────────────────┬─────────────────────────────────┤
│                                    │  TYPE THIS      Chunk: [ … ]    │
│  EDITOR (Monaco, Python)           ├─────────────────────────────────┤
│                                    │  PROBLEM  + Check my work       │
├────────────────────────────────────┴─────────────────────────────────┤
│  TERMINAL — Run output / errors                                      │
└──────────────────────────────────────────────────────────────────────┘
```

Every divider drags, and each pane keeps a minimum size so none can be hidden.
Sizes persist.

**Other controls:** **Run** (or `Ctrl`/`⌘`+`Enter`), **Explain my code** for a
line-by-line walkthrough, **Free mode** to switch the coach off, **Save / Load…**
for named scripts, **Start over** to clear a lesson.

### Where your work is kept

- **Code you type** — browser `localStorage`, one buffer per exercise per chunk
  size. Your position in each lesson is restored when you come back.
- **Progress and XP** — `~/.code_coach/student_progress.json`.

Clearing site data wipes typed work; **Save** exports anything you want to keep.

---

## Security

**The server executes the code in your editor.** It writes it to a temp file and
runs it as a real subprocess with a 3-second timeout — no sandbox. That's the
point of the app, but it means anyone who can reach the server can run arbitrary
code on your machine.

So it binds to `127.0.0.1` only, and rejects any request whose `Host` header
isn't localhost (that check stops DNS-rebinding, which CORS alone won't).

**Don't expose this to the internet** — not via a tunnel, not on `0.0.0.0` on an
untrusted network. Sharing it safely means sandboxing the executor first. If a
friend wants to try it, have them clone and run their own copy.

---

## API

All local, `127.0.0.1:8765`.

| Method | Path | Notes |
|--------|------|-------|
| `GET`  | `/api/health` | version check |
| `GET`  | `/api/skills` | list skills |
| `GET` · `PUT` | `/api/progress` | read / update settings |
| `GET`  | `/api/curriculum` | Class → Lesson tree |
| `GET`  | `/api/practice/current` | active session (steps, study payload, position) |
| `POST` | `/api/practice/evaluate` | `{drill_id, code, run?, exercise_index?}` → checks + coach message |
| `POST` | `/api/practice/check-answer` | `{code, pattern_id, problem_number}` → diff against the real solution |
| `POST` | `/api/practice/navigate` · `goto-lesson` · `more` · `review` · `back` | move around |
| `POST` | `/api/practice/complete` | mark done + advance |
| `POST` | `/api/explain` | `{code}` → line-by-line walkthrough |
| `POST` | `/api/chat` | local keyboard/Python FAQ bot |

---

## Project layout

```text
code-coach/
  start.bat               # Windows: both servers + browser
  scripts/dev.sh          # macOS/Linux equivalent
  code_coach/
    cli.py                # file-watch CLI (separate from the web app)
    engine.py             # runs student code in a temp file
    checks.py             # AST predicates for build lessons
    explain.py            # plain-English walkthrough (AST + traced run)
    curriculum/           # Class → Lesson catalog + navigation
    dictation/bank.py     # type-along generators, verbatim + diff logic
    leetcode/
      problems.py         # 52 solutions across 13 patterns
      bank.py             # solutions → exercises
      study.py            # problem briefs + pattern lessons
    practice/             # scoring + coach messages
    progress/store.py     # atomic JSON persistence
    api/server.py         # FastAPI
  web/src/
    App.tsx               # layout, resizing, draft persistence
    components/
      CurriculumNav.tsx   # breadcrumb navigation
      TypeTarget.tsx      # "Type this" panel
      StudyPanel.tsx      # problem + pattern lesson + self-check
      EditorPane.tsx      # Monaco
  tests/                  # stdlib unittest (no pytest)
```

---

## Develop

```bash
.venv/bin/python -m unittest discover -s tests
```

```bash
.venv/bin/python -m ruff check code_coach tests
```

```bash
cd web && npx tsc --noEmit
```

The LeetCode solutions are covered by tests that actually execute them against
real cases — if you add a problem, add its test.

### CLI

The original file-watch CLI still works, independently of the web app:

```bash
python -m code_coach --watch --file "/path/to/practice.py"
```
