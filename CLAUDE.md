# Working on Code Coach

Notes for whoever builds here next - a person or an AI assistant. The README
says what Code Coach is and how to run it; this says how it is put together,
how changes get checked and shipped, and what has bitten before. PLAN.md is
an old build plan, kept for history.

## Run it

- `start.bat` starts both servers and opens the browser. The API is
  FastAPI on 127.0.0.1:8765, served by `tools/serve_api.py`, which restarts
  it whenever a file under `code_coach/` changes (uvicorn's own `--reload`
  wedges on this machine). The UI is Vite on :5173 and proxies `/api`.
- Logs: `logs/api.log`, `logs/ui.log`. "Can't reach the API" in the
  browser right after an edit is usually just the restart; reload.
- It is local only. Don't make the server listen beyond 127.0.0.1: a friend
  who wants it clones the repo and runs their own copy.

## The rules that keep it honest

- **The oracle rule.** Every expected answer comes from somewhere other
  than the code under test: worked out in Python and then run through the
  real runtime (node, dart, python, PostgreSQL, a browser) in the tests.
  Never paste a runtime's output in as the expected answer.
- **Sabotage-check new tests.** Break the thing on purpose, see the test
  fail, put it back. If a permission prompt refuses the sabotage edit, skip
  it and say so - don't route around the refusal.
- **Tests must survive growth.** A test that pins "exactly these sets" or
  "nothing comes after page N" breaks the next time content is added.
  Check subsets and "no other page uses these numbers" instead.
- **Real progress is the user's.** Tests write to a sandbox
  (`tests/__init__.py` redirects the store; every save file lives beside
  the progress file, so it follows). Clicking around the real app writes
  real progress - undo anything you record while testing by hand (the
  Farm has `POST /api/farm/reset`; Brain Drills keeps
  `~/.code_coach/brain_drills.json`).

## Shipping: the full suite, in chunks

Push only after the full suite is green. It takes about 1 hour 45 minutes
serially, and a background command is now stopped after ~30 minutes, so it
runs as chunks, each its own command, each well under the limit:

| Chunk | What | About |
|---|---|---|
| A | `tests/test_[a-c]*.py` | 7 min |
| B | `tests/test_[d-k]*.py` | 9 min |
| C | `tests/test_[l-s]*.py` | 15 min |
| D | `tests/test_[t-v]*.py` | 4 min |
| E1 | `tests/test_workbook.py -k "not _part"` | 24 min |
| E2 | the other `tests/test_w*.py` with `-k "not _part"` | 2 min |
| F | `tests/test_workbook.py tests/test_worked_lessons.py -k "_part1 or _part2 or _parts"` | 16 min |
| G | `tests/test_workbook.py -k "_part3 or _part4"` | 16 min |
| H | `tests/test_workbook.py -k "_part5 or _part6"` | 16 min |

Run each with `./.venv/Scripts/python.exe -m pytest -q -p no:randomly -rf`
and save its log. Before starting, **freeze the list of files the commit
will contain** (`git status --porcelain -uall`), and stage exactly that list
at the end. That means:

- work can carry on while the suite runs, but only in files outside the
  frozen list;
- a file in the list must not change mid-run;
- never `git add -A` at the end of a run.

Parallel pytest (xdist) was tried and rejected: on this 4-core machine the
process start-up contention made tests time out.

## Editing on Windows

- Bash heredocs mangle backslashes. Write scripts with the editor's Write
  tool and run them, rather than inlining them in `bash <<EOF`.
- Many files are CRLF. A script that edits them should read bytes, note
  the line ending, normalise to `\n`, edit, and write back in the original
  ending.
- The Edit tool can turn ` `-style escapes into literal characters; the
  Farm's `farm_api.js` has been hit by this. Check after editing it.
- Dart through Flutter's `dart.BAT` shim can't be killed (the kill reaches
  cmd.exe, not dart.exe). Launch the SDK's real `dart.exe`
  (`stubs/render.dart_executable()`), and kill process trees
  (`taskkill /T`), as `farm/runner.py` does.

## Content: how a new set gets in

Most modes take content as a new module plus a one-line registration:

- **Workbook pages**: `code_coach/workbook/content_<set>.py` +
  `emit_<set>.py` (shapes, `solution`, `expected_output`, `for_shape`
  complexity notes). Register in `content.py`, `__init__.py`
  (expected_output dispatch), `emit.py` (solution dispatch and
  `all_shape_ids`), `complexity.py`, and `tests/test_workbook.py`
  (`python_only` for JS-only shapes). The JavaScript book is numbered in
  order: 168-177 regex, 178-187 data, 188-197 game math, 198-207 building a
  game, 208-217 async, 218-227 planets, 228-237 bodybuilding, 238-247 Node, 248-257 music, 258-267 cooking.
- **Predict / Magnets / Errors / Bug Hunt**: a module per family (e.g.
  `kata/predict_jsasync.py`), added to the registry list in that package.
- **Typing**: themes in `typing/drills.py`. `BESIDE_LORE` keeps a language's
  code themes next to its lore.
- **Session queue**: every source the server deals needs a key in
  `web/src/lastKeys.ts` (`tests/test_session.py` checks both sides agree).

## The Farm (The Farmer Was Replaced)

A copy of the programming game, playable in four languages: **Original**
(the game's own language), Python, JavaScript and Dart. Numbers - costs, growth
times, ticks - come from thefarmerwasreplaced.wiki.gg; where the wiki is
silent (the research tree's prerequisites, farm size per Expand level,
yield per upgrade) they are guesses, marked as such in `data.py`.

```text
code_coach/farm/
  data.py       names, costs, timings, the research tree
  world.py      the field and its rules; one World is one save; World.call
  protocol.py   the line protocol: "\x1eCC"+{"f","a"} out, {"r"}/{"e"}/{"stop"} back
  gate.py       refuses language features not unlocked yet (while, if, for...)
  runner.py     FarmHost: the save, runs, drones, simulations, pacing
  stubs/
    farm_api.py / .js / .dart   the drone library per language
    farm_lang.py                the interpreter for Original
    render.py                   what to write and how to launch, per language
```

- A run is a real process per drone. Each command is one line out and one
  line back, done by `World.call` in the server and paced to game time with
  the time warp.
- **Original** is Python's syntax run by `farm_lang.py`. It charges ticks
  for every operation, as the game does: it sends `"t"` with each command
  and `__ticks__` on its own. It follows the game's scope rules (no
  `global`; assignment always makes a local) and refuses what isn't in the
  game's language.
- **Megafarm**: a drone is a new process in drone mode (env `FARM_DRONE`).
  Each drone keeps its own clock, and commands run in game-time order
  (`FarmHost._my_turn`).
- **Import**: each language has several files and Run runs the open tab.
  JavaScript is real ES modules.
- **Simulation**: `simulate()` starts a child Run on its own World
  (`World.for_simulation`). The caller's whole run waits, and starting
  globals go in via env `FARM_GLOBALS`.
- The save is `farm_save.json` beside the progress file.
- **Playbook** (`farm/playbook.py`, the Playbook button): tips and paste-able
  snippets in all four languages. `tests/test_farm_playbook.py` gates every
  snippet against exactly its research and runs the key ones on a real farm.
- Not built yet: the leaderboard (deliberately skipped).

## Canvas and Brain Drills

- **Canvas**: JavaScript you can watch. Tracks: Dodge, Breakout, Snake,
  Platformer, Asteroids, Farm, To-do, and From blank (five independent projects: a spec
  and a check, no starter code). `canvas/harness.js` runs in the browser preview and in node
  (`node_check.js`, with a stand-in canvas). The check plays the program:
  frames, held keys, the mouse. Each step's starter is the previous step's
  solution. To-do is different - see below.
- **Brain Drills** (`code_coach/brain/`): seven timed reflex activities, in
  JavaScript or Python (`pythonic.py`; scores kept per language), and a
  "code age" from 20 to 80. Every item is modelled in
  Python and held to node in `tests/test_brain.py`. (Not called "Brain
  Age", which is Nintendo's trademark.)

## Checking the UI

Use the in-app browser at a desktop size (1400x900), and measure the DOM
with JavaScript rather than trusting screenshots: screenshots of the pane
time out or catch a canvas before it paints. Reset the viewport when done.

## Canvas's To-do track: a web page, checked in a browser

Built 2026-10-05. Twelve steps build a to-do list on a real page:
querySelector and textContent, classList, a click listener, an input's
value, createElement and append, trim, a form's submit with
preventDefault, remove(), event delegation, a counter, localStorage, and
an open step. The page grows as the steps do (a box at 4, a form at 7, ×
buttons at 8, a counter at 10), and each starter is still the step before.

```text
code_coach/canvas/
  content_dom.py   the steps: html (the page's <body>), css, starter, solution, check
  dom.py           builds the page (preview or check); headless Chrome for the tests
  dom_harness.js   loaded in the page's <head>: storage, cc.click/type/enter/reload
```

- **The check runs in a real browser, never a homemade DOM.** In the app,
  Check loads the page `POST /api/canvas/page` builds (mode `check`) in a
  hidden sandboxed frame. It posts `{type: "result"}` back, and a pass is
  counted with `POST /api/canvas/passed`. The server builds the preview's
  page too, so the preview and the check load the same document. Node
  never checks a page step (`/api/canvas/check` answers 400).
- A check's API is `cc.click(el, label)`, `cc.type`, `cc.enter` (Enter in a
  box, with the browser's implicit submission: it clicks the default
  button, else submits a one-field form), `cc.reload()`, `cc.logs()`,
  `cc.text`, plus `expect`, `$` and `$$`. Checks read the page, never the
  learner's variables.
- **Forms.** A sandbox without `allow-forms` never fires `submit` at all;
  the spec blocks it before the event. So:
  - the check frame has no `allow-forms`, and the harness fires `submit`
    itself, failing the check when nothing calls `preventDefault`;
  - the preview has `allow-forms`, and the harness's last-in-line window
    listener catches an unstopped submit; Code Coach reloads the preview
    and explains why.
- **localStorage.** The sandbox has none, so the harness puts an in-memory
  one on `window` (with property access, as the real one allows). The
  preview posts its contents up, and Run passes them back in, so Run is a
  reload. A check starts with it empty.
- **`cc.reload()`** fires `beforeunload`, `pagehide` and `unload`, then:
  - removes the window/document listeners and timers the code added;
  - puts the HTML back and runs the code again inside `{ }`, so its
    `const` and `let` don't clash with the first run's;
  - fires `DOMContentLoaded` and `load`.
- **Line numbers.** The code goes in as an injected script, so a stack
  reads `<anonymous>:line:col`. Take the line from the stack:
  `JSON.parse`'s error event reports the line of the JSON, not the caller.
- **Tests** (`tests/test_canvas_dom.py`) load every case in one headless
  Chrome (`dom.run_pages`, about 5 seconds), each in a frame sandboxed like
  the app's, and skip when there's no Chrome. The traps:
  - `--dump-dom` doesn't wait for out-of-process frames. Hence
    `--disable-features=IsolateSandboxedIframes`,
    `--disable-site-isolation-trials` and `--virtual-time-budget`, which
    make Chrome finish every frame's tasks first.
  - The host page must listen for messages from its `<head>`, or the
    first frames report before anyone hears.
- **Checking it by hand** in the in-app browser: its clicks and keys don't
  reach into a sandboxed frame. Drive the page from its own code instead,
  for example a draft that calls `requestSubmit()` once, guarded by a
  localStorage flag. When the pane isn't drawing, neither
  `requestAnimationFrame` nor ResizeObserver runs, so measure the DOM.

## Ideas not built yet

- Node practice (files, arguments, a small server).
- A build-from-blank project: spec and tests, no starter.
