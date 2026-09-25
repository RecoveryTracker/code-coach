# Code Coach

A local practice environment for learning to program by doing the same things
many times. It runs your code, checks it against answers that were worked out
independently rather than asserted, and tells you which line went wrong.

Everything runs on your machine. No API keys, no cloud calls, no account.

The method is repetition. Nothing here is "completed" — every mode counts how
many goes you have had at each item and offers you whatever you have done least
and longest ago.

---

## What is in it

Thirteen modes, all sharing one row of names at the top of every screen.

| Mode | What you do |
|------|-------------|
| **Session** | One queue across every practice, so a session starts with practice rather than with deciding what to practise |
| **Workbook** | Pages of small exercises solved by typing. 600 pages, ~12,000 exercises, across 20 languages |
| **Lessons** | The LeetCode patterns, taught — how to get from a question to a solution |
| **Forms** | Write a function; it is called with inputs you have not seen. 160 across 18 families, including The Odin Project's computer science section, Fix the bug, and Change it — working code and a change request, in Python, JavaScript, Dart and C |
| **Trace** | Stop a program part way and say what a variable holds, then step through and watch. 21 moments, in Python, JavaScript and Dart |
| **Errors** | A program that crashed and the message it printed. Which line, and what is it telling you? 23 of them, in Python, JavaScript and Dart |
| **Bug Hunt** | A bug report and the program it is about. Reproduce it, find the line, say what is wrong, then fix it — in that order, because the order is the skill. 31 hunts, in Python, JavaScript and Dart |
| **Puzzles** | Two-part puzzles: solve part one and part two changes the rules - same input, a new question, and your part-one code is still there to change. 15 puzzles, in Python, JavaScript and Dart (typed signatures included) |
| **Regex** | Write a pattern that finds the strings on one side and leaves the other side alone, run in the real engine of your language (Python's `re`, JavaScript's `RegExp` or Dart's `RegExp`). 32 tasks, from single letters to lookarounds |
| **Case files** | A mystery in a database. Query real PostgreSQL however you like, then answer each step. 5 cases, 20 steps, from IS NULL up to window functions. Needs the optional PostgreSQL below |
| **Magnets** | The lines of a working program, shuffled. Put them back under the stage each belongs to. JavaScript, Dart and C |
| **Predict** | Read the code, say what it prints. 92 puzzles: Python, 29 JavaScript, 24 Dart and 12 C |
| **HTML & CSS** | Read it: what does the browser compute? 38 questions. Type it: copy the markup and watch what you typed render, 20 drills |
| **LeetCode** | 104 problems across 13 patterns, with the editor, the coach and the terminal |
| **Typing** | Keyboard practice — key sections, symbols, speed, vocabulary |
| **Concepts** | The questions an interview asks that are not coding problems |
| **Reference** | Cheat sheets and flashcards for the language you are in |

The look is a choice: the swatch button in the top bar switches the whole app between Original, Dark, Purple, Light, Northern Lights and Arcade, and remembers it per browser.

### Languages

Twenty are offered, and they are not equally finished.

- **Python, JavaScript, Dart** — everything: workbook, taught course,
  reference, and the tracer behind *Watch it run*.
- **TypeScript** — the same, apart from the tracer.
- **C, C++, Rust** — workbook, taught course, reference, and structural
  checks; no tracer.
- **SQL, PostgreSQL** — their own workbooks and runners. SQL is SQLite and
  needs nothing installed; PostgreSQL is a real server (see below).
- **Go, PHP, Lua, Ruby, Zig, Java, C#, Kotlin, Swift, Common Lisp, Odin** —
  workbook pages and typing material, added for the drill screens rather
  than for the taught course.

The language picker says what each one actually has, so nothing opens an empty
screen. Several need their own toolchain on your PATH to *run* anything — the
drills still work without it.

---

## Setup

> **On Windows?** Follow **[SETUP-WINDOWS.md](SETUP-WINDOWS.md)** — step by step
> from a machine with nothing installed, including troubleshooting.

You need **Python 3.10+** and **Node 18+**. On Windows, tick *"Add to PATH"* in
both installers, then open a **new** terminal so the change takes effect.

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

### Dart and Flutter

Dart is one of the three focus languages, alongside Python and JavaScript, and
it comes with Flutter. Install Flutter with Git (the official route):

```bash
git clone https://github.com/flutter/flutter.git -b stable ~/flutter   # Windows: C:\flutter
~/flutter/bin/flutter --version                                        # downloads Dart the first time
```

The app finds `dart` on your PATH, under `FLUTTER_ROOT`, or in the usual
places (`C:\flutter`, `C:\src\flutter`, `~/flutter`, `~/development/flutter`).
Without it the app still runs: every Dart exercise is left out of the lists
and the Session queue rather than offered and impossible to pass, and the
Dart tests skip.

### PostgreSQL (optional)

Everything else works without this. PostgreSQL is the one language that needs a
real server, because the things worth practising in it — `RETURNING`, `ILIKE`,
`::` casts, `ON CONFLICT`, arrays, JSONB — are exactly the ones SQLite cannot
fake.

Download the Windows or macOS **binaries zip** (no installer, no admin rights)
from [EnterpriseDB](https://www.enterprisedb.com/download-postgresql-binaries),
who publish them for postgresql.org. Put the `pgsql` folder it contains at
`.tools/pgsql`, then:

```bash
.venv/bin/python tools/get_postgres.py
```

That creates a cluster in `.tools/pgdata`, loads the sample tables and runs a
query to prove it works. It listens on **127.0.0.1:55432** — deliberately not
5432, so a PostgreSQL installed for work is never blocked by this one. Run it
again any time to reset the practice data. Undoing all of it is deleting
`.tools/pgdata`.

---

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
.venv/bin/python tools/serve_api.py
```

That runs the API on port 8765 and restarts it whenever a file under
`code_coach/` changes - a fresh process each time, which is sturdier than
uvicorn's own `--reload` (on some machines that one logs "Reloading..." and
never restarts).

```bash
cd web && npm run dev
```

> **Heads up:** the venv's Python is not the same as the `python` on your PATH.
> If you see `No module named uvicorn`, you're using the wrong one — go through
> `.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows).

---

## Getting a newer version

```bash
git pull
```

The API restarts itself: `tools/serve_api.py`, which `start.bat` runs, sees
the changed files and starts a fresh server within a couple of seconds. If it
ever seems stuck - a port held by something else, say - `restart-api.bat` stops
everything and starts it again:

```bash
restart-api.bat
```

Then reload the browser tab. The UI reloads itself as files change, but a
tab that was already open can be holding an older bundle.

Reinstalling dependencies is only needed when they actually change:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

```bash
cd web && npm install
```

`git log --oneline -- requirements.txt web/package.json` says whether either
has moved since the version you had. Nothing else needs doing — your progress
lives in `~/.code_coach/` and the PostgreSQL cluster in `.tools/`, and neither
is in the repo, so a pull cannot touch them.

---

## How the checking works

The rule the whole project is built on: **the expected answer has to come from
somewhere other than the thing being checked.** A test that compares a function
with what that function returned passes just as happily when the function is
wrong.

So each mode gets its answers from a different place, on purpose:

- **Workbook** — the expected output is worked out in Python; your code is run
  by a real compiler or interpreter. Two implementations, so agreeing means
  something. The SQL and PostgreSQL pages compute from a hand-written mirror of
  the rows rather than by running the query.
- **Forms** — a reference implementation computes the answers, and a person
  hand-writes some of them at awkward inputs, because a reference can be wrong.
- **Predict** and **Trace** — the engine and the tracer are the authority on
  what a program prints or holds; the hand-written copy is what catches a
  puzzle that has stopped demonstrating its own point.
- **Errors** — both halves of the answer are the engine's own report: the
  message it printed and the line it blamed.
- **HTML & CSS** — there is no browser engine in the project, so the answers
  were measured in real Chromium by `tools/verify_css.py` and recorded with a
  hash of the exact document measured. Change a quiz without re-measuring and
  the suite fails.
- **Magnets** — marked by running what you arranged, not by comparing your line
  order with the reference, because more than one order is usually correct. The
  stage labels are subgoal labels: given rather than asked for, because that is
  what the research on Parsons problems supports.

### Where your work is kept

- **Code you type** — browser `localStorage`, per exercise.
- **Progress** — `~/.code_coach/student_progress.json`. Counts of goes and when,
  per item, per mode.

Clearing site data wipes typed drafts; **Save** exports anything you want to
keep.

---

## Known limits

Worth knowing before you file a bug, because these are decisions rather
than accidents.

**The HTML & CSS answers were measured in Chromium.** Every expected value
in that mode came out of a real Chromium run, recorded with a hash of the
document measured. Most are the same in any browser; a few are not — the
default font size of a `<button>` differs between Chrome and Firefox, for
instance. If a quiz marks you wrong in Firefox and you are sure you are
right, that is probably why. The rest of the app is browser-agnostic.

**Some languages need their own toolchain to run anything.** The picker
says which. Without the toolchain the drills still work — only Run does
not. Python, JavaScript and SQL need nothing beyond the setup above.

**The full test suite takes about an hour.** It executes every workbook
exercise in every language it has a compiler for. You do not need to run
it to use the app.

**PostgreSQL is opt-in** and needs a 300MB download. Everything else works
without it, and the picker will tell you the server is not there rather
than failing oddly.

**Progress is per-machine.** It lives in `~/.code_coach/student_progress.json`
and is yours — nothing is uploaded, and there is no account to make.

---

## Security

**The server executes the code in your editor.** It writes it to a temp file and
runs it as a real subprocess — no sandbox. That is the point of the app, and it
means anyone who can reach the server can run arbitrary code as you.

So it binds to `127.0.0.1` only, and rejects any request whose `Host` header
isn't localhost (that check stops DNS rebinding, which CORS alone won't). There
is no authentication, because there is nothing safe to authenticate *to*.

The wall-clock timeout and output cap apply everywhere. The CPU and memory caps
are POSIX-only, and `RLIMIT_AS` is ignored on macOS — those are guards against
runaway programs, not against attacks.

**Don't expose this to the internet** — not through a tunnel, not on `0.0.0.0`,
not "just for a friend". A secure Wi-Fi network does not help: port forwarding
routes around it, and exposed ports are found by mass scanners within minutes.
Sharing safely would mean sandboxing the executor in a container first.

**If a friend wants to try it, have them clone and run their own copy.** That is
what the app is built for — everything is local, and their progress is theirs.

---

## API

All local, `127.0.0.1:8765`.

| Method | Path | Notes |
|--------|------|-------|
| `GET`  | `/api/health` · `/api/languages` | version check; what each language has |
| `GET` · `PUT` | `/api/progress` | read / update settings |
| `GET`  | `/api/session?size=` | the next things to do, across every practice |
| `GET` · `POST` | `/api/workbook` · `/api/workbook/check` | pages; check an exercise |
| `GET` · `POST` | `/api/kata` · `/api/kata/check` · `/api/kata/answer` | Forms |
| `GET` · `POST` | `/api/predict` · `/api/predict/check` | Predict |
| `GET` · `POST` | `/api/trace` · `/api/trace/check` | Trace |
| `GET` · `POST` | `/api/errors` · `/api/errors/check` | Errors |
| `GET` · `POST` | `/api/magnets` · `/api/magnets/check` | Magnets |
| `GET` · `POST` | `/api/puzzles` · `/api/puzzles/check` · `/api/puzzles/answer` | Puzzles |
| `GET` · `POST` | `/api/regex` · `/api/regex/check` · `/api/regex/answer` | Regex |
| `GET` · `POST` | `/api/cases` · `/api/cases/query` · `/api/cases/answer` · `/api/cases/reveal` | Case files |
| `GET` · `POST` | `/api/css` · `/api/css/check` | HTML & CSS, the reading half |
| `GET` · `POST` | `/api/drills` · `/api/drills/check` | HTML & CSS, the typing half |
| `GET`  | `/api/curriculum` · `/api/practice/current` | LeetCode: tree, active session |
| `POST` | `/api/practice/evaluate` · `check-answer` · `navigate` · `complete` | LeetCode: the workspace |
| `POST` | `/api/explain` · `/api/visualize` | walkthrough; step-by-step values |

---

## Project layout

```text
code-coach/
  start.bat                 # Windows: both servers + browser
  scripts/dev.sh            # macOS/Linux equivalent
  tools/
    get_postgres.py         # set up the local PostgreSQL
    verify_css.py           # measure every CSS answer in a real browser
  code_coach/
    engine.py               # runs student code; timeouts and caps
    visualize.py            # the tracer
    _js_trace_runner.js     # JavaScript tracing, through Node's inspector
    sql_runner.py           # SQLite, for the SQL pages
    pg_server.py            # the local PostgreSQL, started on demand
    pg_runner.py            # queries, each in a transaction that is rolled back
    languages.py            # what each language actually has
    workbook/               # 600 pages: shapes, per-language emitters, content
    kata/                   # Forms, Fix the bug, Finish the program, Predict
    css/                    # HTML & CSS quizzes, answers measured in Chromium
    markup/                 # HTML & CSS typing drills
    magnets/                # shuffled-program puzzles
    errors/                 # crashes, their messages and what they mean
    trace/                  # one moment in a program, one variable
    session/                # the cross-practice queue
    leetcode/               # 104 problems across 13 patterns
    progress/store.py       # atomic JSON persistence
    api/server.py           # FastAPI
  web/src/
    App.tsx                 # the shell and the mode switching
    components/ModeBar.tsx  # the row of names every screen wears
    components/             # one per mode
  tests/                    # unittest classes; pytest optional
```

---

## Develop

```bash
.venv/bin/python -m pytest -q
```

`pytest` is not in `requirements.txt` — install it with `pip install pytest`.
Plain `python -m unittest discover -s tests` also works and gives plainer
output.

Whichever you use, the suite writes to a throwaway progress file rather than
your real one. That redirect lives in `tests/__init__.py` specifically so it
does not depend on the runner: it used to be in `conftest.py`, which only
pytest loads, and running the suite under unittest silently recorded real
practice into a real progress file with everything green. `SandboxTests` in
`test_progress_migration.py` asserts it, because that failure has no other
symptom.

**The full suite takes about an hour** — it executes every workbook
exercise in every language it has a compiler for, which is over 120,000 checks.
Most changes do not need it. Useful subsets:

```bash
.venv/bin/python -m pytest tests/test_kata.py tests/test_predict.py -q
```

```bash
cd web && npm run build
```

Lint and typecheck:

```bash
.venv/bin/python -m ruff check code_coach tests tools
```

```bash
cd web && npx tsc --noEmit
```

If you add content, add the check that would catch it being wrong — and then
break it on purpose to confirm the check fails. Every mode in this project has
shipped at least one bug that a green suite was quietly ignoring.

### CLI

The original file-watch CLI still works, independently of the web app:

```bash
python -m code_coach --watch --file "/path/to/practice.py"
```
