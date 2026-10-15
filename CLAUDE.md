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

The test fixtures remove their own scratch folders (they used to leave one per
test in the temp directory - 190,000 of them - and every Python start scans
that folder, which added minutes to the suite). Parallel pytest (xdist) was tried and rejected: on this 4-core machine the
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
  game, 208-217 async, 218-227 planets, 228-237 bodybuilding, 238-247 Node, 248-257 music, 258-267 cooking. The Python book is numbered
  on its own: its scripting pages (pathlib, argparse, files, JSON, csv, logging,
  exit codes, http.server, asyncio) are 342-351, then web servers and HTTP (352-361) and data practice
  (362-371) - the last base pages; Review pages are numbered after them.
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
- **One save per language**: Original, Python, JavaScript and Dart each have their own
  farm (World), code files, open tab and time warp, in `farm_save_<language>.json`
  beside the progress file; `farm_save.json` only says which language is current. `FarmHost`
  holds one World per language (built lazily, `_world_for`); `_load()` is the current one;
  `start`/`file_op`/`keep_code` switch to the language they name (refused while a run
  is on another language's farm); `reset` clears only the current farm, keeping the code.
  `overview().levels` is every language's research, for the Playbook. The old single-file
  save is split on first load (`_migrate`) and kept as `farm_save.json.before-per-language`;
  tests that run several languages on one host must set up every language's world (see `host()`).
- **Playbook** (`farm/playbook.py`, the Playbook button): tips and paste-able
  snippets in all four languages. `tests/test_farm_playbook.py` gates every
  snippet against exactly its research and runs the key ones on a real farm.
- **The game's language as a language** (`tfwr` in the top-bar picker): Free mode
  runs it on a throwaway farm (`farm/scratch.py`, never the saved one, every
  upgrade bought, capped at 10 s) and "Explain my code" glosses the game's
  commands (`farm/explain_farm.py`). Free mode's Explain button and the coach's
  share `components/ExplainPanel.tsx`.
- **Events**: every action that changes a square (harvest, plant, till, water, fertilize, swap, hat, unlock;
  never moves) is written by `World._record` into a 60-deep ring, sent as `snapshot()["events"]` (oldest first,
  `FarmEvent` in `web/src/types.ts`). `n` comes from one process-wide counter, so it only rises; `d` is the drone
  (`World.drone_id`, set by `FarmHost._command`); a harvest's `items` are read off the barn's change. `tests/test_farm_events.py`.
- Not built yet: the leaderboard (deliberately skipped).

## Canvas and Brain Drills

- **Canvas**: JavaScript (and now Python) you can watch. Tracks: Dodge, Breakout, Snake,
  Platformer, Asteroids, Tower defense, Dungeon, Farm, To-do, Debug it (ten
  programs each with one bug to find), and From blank (five independent projects: a spec
  and a check, no starter code). `canvas/harness.js` runs in the browser preview and in node
  (`node_check.js`, with a stand-in canvas). The check plays the program:
  frames, held keys, the mouse. Each step's starter is the previous step's
  solution. To-do is different - see below.
- **Python Canvas** (`code_coach/canvas/pyharness/`, tracks "Dodge (Python)" in
  `content_pydodge.py`, "Snake (Python)" in `content_pysnake.py`, "Breakout (Python)"
  in `content_pybreakout.py`, and Asteroids, Platformer, Tower defense, Dungeon and
  From blank (Python) in the other `content_py*.py` files). Python cannot draw in a browser, so the learner's
  program runs on the server, in a child process (`python -I -u -X utf8
  driver.py serve`), one frame per request, and `PyCanvasView.tsx` paints the
  recorded draw calls on a real `<canvas>`. The learner writes `from canvas
  import ctx, WIDTH, HEIGHT, on_frame, keys, ...` (`lib/canvas.py`: a snake_case
  `ctx`, `on_frame(fn(dt))`, `keys`, `mouse`, `on_key_down/up`, `on_click`,
  `after/every/cancel`, `now()`; dt is game seconds). Nothing is drawn in
  Python: every `ctx` call is written down as `[name, args, fill_style,
  stroke_style, {lineWidth, font, ...}]`. The protocol is JSON lines behind a
  `PY` marker (`print` is caught and returned as `logs`; stdout is the
  wire): `start {code}`, `step {frames, dt, keys, events}`, `stop`; every reply
  is `{calls, logs, error: {message, line}|null, frames, input}`, the last two
  saying whether the program still wants frames or input (neither: the page
  stops asking). Lines are the learner's own (code is compiled as `game.py`).
  A watchdog thread in the child stops a program that runs past its limit
  (2 s a step) by raising in it; if it swallows that, the child exits (code 3);
  the parent kills the process tree at limit + 2.5 s. Sessions
  (`session.py`, routes `/api/pycanvas/start|step|stop`) live in a registry: at
  most 4 (least recently used evicted), idle 60 s reaped (swept every 5 s),
  child and temp folder removed on stop, evict, idle, crash and server exit; a
  child whose server dies exits on stdin EOF, and its folder is swept (if over
  an hour old) the next time a session starts. A check (`check.py`
  `run_py_check`, dispatched by `Step.language == "python"` in
  `check_step`) runs in one child (`driver.py check`): Python statements with
  `cc` (frames, press, release, click, pointer, rects, arcs, texts, drawn,
  time), `expect`, `near`, `g` (the learner's top-level names, get and set)
  and `WIDTH`, `HEIGHT`; `random` is seeded 20260926 before the code loads.
  It is not a security sandbox - it is the learner's own Python on their own
  machine, with an empty working folder and a bare environment. **A new Python
  track**: a `content_<name>.py` of `Step(language="python", ...)`, one line in
  `canvas/__init__.py` STEPS, and a test file like
  `tests/test_canvas_pydodge.py` (solutions pass, starters fail, MISTAKES fail,
  OTHER_WAYS pass). Checks read fields with a `get()` helper so a dict or a
  dataclass both pass. Verify by hand with the in-app browser: its pane is
  hidden, so `requestAnimationFrame` never fires - stand a `setTimeout` in for
  it on the page, press Run, and read canvas pixels.
- **Python web** (`code_coach/canvas/pyweb/`, track "Web (Python)" in
  `content_pyweb_track.py`, ids `pywa-NN-name`, a Link Saver bookmarks app in 12
  steps). A step has `surface="web"` (so `Step.kind == "web"`, `language="python"`)
  and its preview is `PyWebView.tsx`, a "Try it" panel (method, path, form/JSON
  body, status line, headers, text and a sandboxed Rendered tab, a cookie jar,
  Follow for a redirect). The learner writes `from web import app, request,
  Response, json_response, redirect, abort, render, safe, escape`
  (`lib/web.py`, standard library only, on `ThreadingHTTPServer`): `@app.get/post/put/delete/patch`
  and `@app.route(path, methods=[...])`, `<name>` and `<int:id>` holes, `request`
  (`.args` first values, `.args_all` lists, `.form`, `.json` (None, or 400 for bad
  JSON), `.headers`, `.cookies`, `.body`), returns of str / dict / list /
  `(body, status[, headers])` / `Response` (`set_cookie`, `delete_cookie`),
  `@app.errorhandler(404)` (returns like a route: a bare page is 200),
  404, 405 with `Allow`, HEAD from GET, OPTIONS 204, a 500 plus the traceback
  (learner lines only) in the console; `render("$x", x=v)` escapes values unless
  `safe(...)`. The learner never calls `app.run` (a harmless note). A child
  (`driver.py serve`, `python -I -u -X utf8`, empty folder, bare env) runs the program
  as `app.py`, serves it on `127.0.0.1` port 0 and speaks `PW`-marked JSON lines:
  `start {code, limit}` -> `{error, logs, host, port, routes, pid}`, `logs`, `stop`;
  a watchdog raises in a route that runs over its 3 s (exit code 3 if ignored).
  `session.py` is `WebRegistry(PyRegistry)` (max 4, idle 120 s) and the **server**
  process makes the request with `http.client` (never following redirects, 1 MB,
  5 s): routes `/api/pyweb/start|request|stop` give `{status, reason, headers:
  [[k, v]], body, binary (base64), truncated, seconds, logs, error}`. A check
  (`check.py` `run_pyweb_check`, dispatched by `Step.kind == "web"` in `check_step`)
  runs in one child (`driver.py check`): the app on a thread and the check body in
  the main thread, over real sockets, with `cc` (`get/post/put/delete(path, form=,
  json=, body=, headers=, cookies=)`, `request`, `follow(resp)` (one hop, 303 and
  302-after-POST become GET), `jar = True` with `cc.cookies`, `logs()`), a response
  (`.status .reason .headers .text .json() .cookies .cookie(name) .location
  .content_type .snippet()`, `.expect_status(*codes, why=)`, `.expect_type(prefix)`,
  `.expect_json()`), `expect`, `near`. Checks never read the learner's names, so any
  program that behaves right passes. **A new step**: add a block to
  `content_pyweb_track.py` (the starter is the last solution, name every route the
  check asks for in the goal) and a MISTAKES / OTHER_WAYS entry in
  `tests/test_canvas_pywebapp.py`; library and session behaviour is in
  `tests/test_pyweb_lib.py`.
- **Brain Drills** (`code_coach/brain/`): seven timed reflex activities, in
  JavaScript or Python (`pythonic.py`; scores kept per language), and a
  "code age" from 20 to 80. Every item is modelled in
  Python and held to node in `tests/test_brain.py`. (Not called "Brain
  Age", which is Nintendo's trademark.) In a round you can go Back (Alt+Left),
  open the Questions grid and jump anywhere, and Run / Explain an answered
  question's code (`BrainTools.tsx`, `BrainPicker.tsx`). The rules live in the
  pure `web/src/lib/brainRound.ts` (tested in `tests/test_brain_round.py`):
  an answer counts once, the round ends only when every question is answered,
  and the clock stops on any answered question (reading a miss, Back, a jump
  to a finished cell). "Run it" is `/api/visualize` and "Explain" is
  `/api/explain`, both told the drill's language (`language` in the request;
  blank = the app's saved one). `round_payload` carries each item's `check`
  code, which the loop and final-value programs are built from.

## Momentum (one sense of progress across every mode)

A cross-app layer: XP, levels, a day streak with freezes, three daily quests and a
chest. It rewards and never punishes: no leaderboard, nothing online, no loss
wording ("you'll lose your streak" is out; a streak not yet added to today is shown
dimmed, not red). Server: `code_coach/momentum/` - `rules.py` is pure (the `XP`
price table, levels, combo, luck, `simulate()` for the streak, quests, chest),
`engine.py` is `Momentum` (the lock, `momentum.json` beside the progress file,
written with the farm's `_write_json`, corrupt file kept as `.bad`). Routes:
`GET /api/momentum`, `POST /api/momentum/award {kind,key}` (unknown kind is 400,
a storage problem answers `{ok:false}` and never raises), `POST /api/momentum/chest`.

- **The client sends a kind and a key, never an amount.** Call `award("kind", key)`
  (`web/src/lib/momentum.ts`, fire and forget) exactly once at a mode's real success
  moment (a passing Check, a finished run), with the id of the thing done. The same
  kind and key pays once a day. Kinds are written as string literals: a test reads
  `web/src` and checks every one is in `rules.XP` and every `XP` kind is used (or
  listed, with a reason, in `rules.UNUSED_KINDS`). A new mode needs a kind in `XP`
  and one `award` call; do not award on a failure or on a page view.
- **Formulas**: level n begins at `50*n*(n-1)` XP; the combo is x1.0 +0.1 per award
  under 10 minutes after the last, max x2.0; about 1 award in 6 is lucky (x2..x5);
  the streak is consecutive days with a non-repeat award, today not yet counted does
  not break it, one missed day is bridged by a freeze (spent when you return), a
  freeze is earned at every 7th streak day (max 2) or from the chest, two missed days
  end it. Days are kept ~400; older ones fold into a `baseline` so the streak survives.
- **Screen**: `components/MomentumHud.tsx` (the strip in the mode bar and its popover;
  it is one button, flame + number only below 640px), `components/MomentumToasts.tsx`
  (mounted in `main.tsx`, bottom-centre, pointer-events none except the level-up card,
  CSS-only confetti), `lib/momentumView.ts` (the pure what-to-show logic, tested in
  node by `tests/test_momentum_view.py`). Brain Drills keeps its own stamps/streak.
- **Testing by hand** writes to the real `momentum.json` like everything else: use the
  sandbox copy (API with `USERPROFILE`/`HOME` pointed at a temp folder, `VITE_API_PORT`
  and `VITE_UI_PORT` for the UI). In the dev UI the store is the module the app loaded,
  with its `?t=` suffix: import that exact URL to call `award` from the console.

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
