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
- **Momentum tie-in** (`farm/milestones.py`; the engine side is in the Momentum section). The
  host wires each real farm's `World.listener` (`FarmHost._wire`; a simulation's world and the
  scratch host - `rewards = None` - have none) and tells `FarmRewards` what happened, so the
  **server** pays: a table of firsts (`MILESTONES`: first harvest of each crop, giant pumpkin,
  sorted cactus patch, maze treasure, first drone, every Expand size, 100/1,000/10,000 items
  harvested) paid once ever per language, through `Momentum.award_server`. Items harvested are
  batched (`flush` every 2 s and when a run ends) into the lifetime total and today's
  `farm_items` counter (the "Harvest 50 items" quest). Answers wait in `FarmRewards.queue`;
  `FarmHost.state()` drains them into `momentum` (a list, oldest first) and `FarmMode` shows
  them with `lib/momentum.ts inject`. **The farm does not run while the app is closed**: an idle
  farm moves on only while it is looked at (at most 2 s a look); only a running program
  (server up) advances it. So the welcome-back card (`GET /api/farm` -> `welcome_back`,
  `POST /api/farm/welcome/claim`) says what *was* ripe when you left, never that anything grew.
  Not tracked: "ran clean after an error", and sizes/totals reached before this existed.
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
- **Brain Drills** (`code_coach/brain/`): timed reflex activities in Python,
  JavaScript or Dart. **The screen has no language switch of its own: it follows
  the app's language picker at the top** (`BrainDrills` takes `appLanguage` from
  `App.tsx`; `brainLanguageFor()` maps python/tfwr -> Python, javascript/typescript ->
  JavaScript, dart -> Dart, anything else -> none, and the screen then says there
  are no drills for that language yet and offers "Switch to Python / JavaScript /
  Dart", which changes the app's language like the picker does). The server routes
  `/api/brain` and `/api/brain/round` still default to Python when no language is
  sent. (`LANGUAGES` = python, javascript, dart, in that order;
  scores kept per language, `Result.language`; the saved
  `brain_drills.json` of older versions has no `"dart"` and still loads, a
  Dart round writes `"language": "dart"` the first time), filed under
  headings on the home screen (`Activity.group`, `GROUPS`: Quick reads,
  Predict the result, Spot the problem, Remember; a language's home lists
  only its own activities and only the headings they sit under), and a "code
  age" from 20 to 80. **An activity is played in a language exactly when it
  has that language's generator** (`make` JavaScript, `make_py` Python,
  `make_dart` Dart: `Activity.languages`, `brain.activities_in(language)`;
  `activity_for(id, language)` raises KeyError for one it is not played in,
  and `/api/brain/round|result` answer 404): the 71 older activities have
  Python and JavaScript, the Dart Core Pack is Dart-only. The Code age check
  is per language: `brain.CHECK` (eval, truthy, brackets) for Python and
  JavaScript, `brain.CHECKS["dart"]` (`dart_eval`, `dart_null`,
  `dart_final`) for Dart, read through `brain.check_for(language)` (the
  home payload's `check`); a check's age needs its three results in THAT
  language. The original seven live in
  `__init__.py` (JavaScript) and `pythonic.py`; every other activity is a
  PACK (below). Every item is modelled by hand in Python and held to the
  real runtime in `tests/test_brain.py` / `test_brain_python.py` (the seven)
  and `tests/test_brain_packs.py` (every discovered activity). (Not called
  "Brain Age", which is Nintendo's trademark.) In a round you can go Back (Alt+Left),
  open the Questions grid and jump anywhere, and Run / Explain an answered
  question's code (`BrainTools.tsx`, `BrainPicker.tsx`). The rules live in the
  pure `web/src/lib/brainRound.ts` (tested in `tests/test_brain_round.py`):
  an answer counts once, the round ends only when every question is answered,
  and the clock stops on any answered question (reading a miss, Back, a jump
  to a finished cell). "Run it" is `/api/visualize` and "Explain" is
  `/api/explain`, both told the drill's language (`language` in the request;
  blank = the app's saved one). `round_payload` carries each item's `check`
  code, which the loop and final-value programs are built from. DART has no
  tracer and no explainer: "Run it" is `POST /api/brain/run {code}`
  (`runBrainCode` in `api.ts`; the Gotchas runner's `run_program("dart")`:
  the SDK's real dart.exe, a bare environment, 5 s after the build, 64 KB;
  snippets up to 4000 characters) and "Explain my code" is disabled with the
  tooltip "Explain my code works in Python and JavaScript so far"; the
  "Words in this question" chips ask the glossary for language `dart` (a full
  third glossary language since 2026-10-22: see "Glossary"), so Dart and Flutter
  drills show their chips with no web change.
- **Brain Drills packs** (how a new activity gets in; the Reading Pack in
  `pack_reading.py` is the model). Add `code_coach/brain/pack_<name>.py`
  exposing `ACTIVITIES: tuple[Activity, ...]` and touch nothing else:
  `brain._discover()` imports `pack_*.py` by name, sorted, after the
  originals; a pack that fails to import (or has a duplicate id, or an
  activity with no generator at all) is skipped, recorded in
  `brain.LOAD_ERRORS` and fails `test_every_pack_imports_cleanly`. An
  `Activity` (`items.py`) carries its languages (`make` JavaScript, `make_py`
  Python, `make_dart` Dart - at least one, a Dart-only activity passes
  `make_dart=` and no `make`; `question_py`/`blurb_py`/`question_dart`/
  `blurb_dart` where the wording differs), `kind` "type" or "pick" (two
  `choices`, left key first), `par`/`slow` seconds per item (look at the existing ones),
  `group`, `concepts` (plain lowercase words: the glossary resolves each one,
  per language, to an entry by id, term or aka - so this is the one place the
  mapping lives, and no glossary edit is needed. A word nobody has written an
  entry for shows up in `tests/test_glossary.py`'s unresolved-concepts test;
  add it as a `terms_brain_*.py` entry) and `oracle="value"`. Build a generator with
  `_model.Pool([template, ...])`: a template is `(rng) -> Item`, or a table
  row from `_model.row(fmt, answer, why, check=...)` with `$a $b $c $d $n
  $w $v $k $x` holes; a pack wants >= 25 templates per language (the Reading
  Pack has >= 40 for Python), and the tests run every template. **Answers are
  modelled by hand** with the helpers in `_model.py` (`fdiv/fmod` by counting,
  `py_slice`, `js_slice`, `py_show`, `js_show`...), never by asking the
  runtime. The oracle (`OracleTests`, both languages, every template and
  many seeds) runs `item.check` - or the prompt when `check` is blank - and
  compares the printed value of its LAST line with `item.answer`; yes/no and
  raises items build a `check` that prints "yes"/"no" (`yes_no_py/js`,
  `raises_py/js`, or a snapshot comparison as Mutate or Copy does). The same
  convention drives "Run it" (`runnableFor` in `brainRound.ts`: the
  default case prints `check` or the prompt; `error` runs the snippet and
  whether it raises is the answer). Rules the shape tests enforce: no
  repeats in a round, prompts <= 220 characters and 10 lines, answers short,
  non-empty, no stray spaces, Python says True/False/None and JavaScript
  true/false/null/undefined, and a Python prompt never looks like
  JavaScript (no `;`, `let `, `null`). Traps: node prints an array of more
  than 6 items in grouped columns (`js_show` refuses one); never print
  inside an item (Run it shows all of stdout); the oracle runs JavaScript in
  a bare `vm` context, so no `structuredClone`/`setTimeout`; avoid `is` on
  ints and strings in Python; `-0` is a real JavaScript answer. Helper
  modules start with `_` so they are not mistaken for packs.
  **Dart packs** (`pack_dartcore.py` is the model; its templates are
  `_dartcore_*.py`, its models `_dart_model.py`, which sits beside
  `_model.py` and is never mixed into it): build the generator with
  `Pool([...])` of `_dart_model.D(fmt, answer, why)` templates (holes
  `$a $b $c $d` ints 2-9, `$n` 10-40, `$w $v` words, `$k` 1-3, `$x $y $z $f
  $e` letters, `$h` 2/4/5/8, `$s1..$s5` capital letters; **Dart's own `$`
  interpolation is written `$$` in a template**, and an explanation never
  contains a `$`), answers worked out with `show`/`ddiv`/`dmod`/`tdiv_`/
  `fixed`/`DSet`/`DIter`... (Dart prints a list `[1, 2]`, a map `{a: 1}`, a
  set `{1, 2}`, an Iterable such as `xs.map(f)` in ROUND brackets, strings
  bare, `2.0`, `true`, `null`). **The item convention**, one rule shared by
  the oracle (`tests/dart_oracle.full_program`), "Run it" (`dartProgram` in
  `brainRound.ts`, held equal by `tests/test_brain_round.py`) and the
  `check` field: the program is `check` or the prompt; if it mentions
  `main(` it is a complete program (classes, `Future<void> main() async`...),
  else it is the body of `main` and its last line is printed when it is a
  bare expression (not `print(...)`, not ending in `;` or `}`); local
  functions are fine in a body, classes and `await` need a complete program.
  `oracle` names how the real dart's printed lines become the value: `value`
  (one line), `lines` (glued together: Async Order's letters) or `error` (a
  fine/error pick: it does not compile or it throws). **The Dart oracle** is
  batched (`tests/dart_oracle.py`): every body-style item is a function of
  one library, every complete program its own library (so two items may both
  declare `class Dog`), `main.dart` runs them one by one in a Zone that
  captures `print` and drains the event loop with zero-duration timers, one
  `dart run` per activity (~2 s per 1500 items; never `Future.delayed` with a
  real duration, a Windows timer tick is 15 ms); an item that does not
  compile is named by file and line and removed, the rest still run.
  `tests/test_brain_packs.py` picks a new Dart pack up with no edit; run just
  it with `-k "Dart"`. Dart on this machine is 3.7 (Flutter 3.29): no dot
  shorthands; type inference traps are real (`fold(0, (s, x) => s + x)` inside
  `print(...)` fails to compile, `Future(() => throw 'x').catchError(...)`
  throws an ArgumentError: the oracle catches both).
- **Flutter pack convention** (Dart-language activities about WIDGETS; `pack_flutterlayout.py`, group "Flutter layout",
  ids `fl_*`, is the model). An activity passes `make_dart=` and `oracle="flutter"`, and **its id must start with
  `fl_`** (the browser's `runnableFor` refuses "Run it" for `fl_*` with "Flutter widgets cannot run here: this answer was
  measured with Flutter itself"; `tests/test_brain_packs.py` holds id prefix == oracle). The oracle is `tests/flutter_oracle.py`
  (`flutter_values([(prompt, check)...])`, `run_batch`): ONE generated `testWidgets` per item, ONE test file per batch
  (up to 800 items; Flutter starts a process per file), `flutter test --no-pub --reporter json`, results read from the
  `@@iN@@value` lines the tests print; a compile failure is mapped by file and line to its item, removed, and the batch
  re-run (`COMPILE ERROR: ... (line 2 of the snippet)`), a Flutter error or throwing check is `ERROR: <first line>`,
  never an exception. The throwaway project is `%TEMP%/code_coach_flutter_brain/fq` (hand-written pubspec + `flutter
  pub get --offline`, made once, shared; each run uses its own folder inside it, so two test processes can run at once;
  separate from test_flutter_questions' project). **The item convention**: `Item.prompt` = a `// width of b` comment
  line (what to measure) + the widget EXPRESSION (no `;`); the host is NOT in the prompt: the view is exactly **400 x 300**
  logical pixels at devicePixelRatio 1.0, the expression is the root widget under `Directionality(ltr)` and gets TIGHT
  400 x 300 constraints (a root `SizedBox(width: 200)` is still 400 wide: a lesson, not a bug), all of
  `package:flutter/material.dart` is in scope; `Box('a', w: 100, h: 40)` is a `SizedBox(key: ValueKey('a'), ...)`, 50 x 50
  unless said; any widget may carry `key: Key('id')`. Every activity's blurb says "400 x 300" and "Box(" (a test holds it).
  `Item.check` = the measurement, a Dart expression evaluated after `pumpWidget`: `w(id) h(id) x(id) y(id)` (size and
  top-left in screen coordinates), `r(id) b(id)` (right and bottom edge), `count(finder)`, `overflowed` (did a RenderFlex
  report an overflow?), anything in flutter_test; `{y('a'), y('b')}.length` counts rows. A check containing `await` or
  `return` is the body of `(tester) async {...}` (tap, `pump`, `return find.text('x').evaluate().length;`), and a prompt
  with top-level classes (a column-0 `}` line) is its own library (classes first, the widget expression after the last
  `}`; two items may both declare `class Counter`). Numbers print as an integer when whole (`120`) else Dart's way
  (`96.5`); a bool prints `true`; an unexpected Flutter error (overflow stripes nobody asked about) is the result
  `ERROR: ...`, so a position question must not overflow. **The model**: `_flutter_model.py` has the node classes (BoxN,
  SizedN, PadN, AlignN, ConstrainedN, UnconstrainedN, AspectN, FractionalN, ContainerN, FlexN + Expanded/Flexible/Spacer,
  StackN + PositionedN, WrapN) that both PRINT Dart (`render`, width 78, lists hugged) and LAY OUT by the render objects'
  rules (`host(root)` -> rectangles, `ctx.overflow`), plus `item(root, id, prop, topics)` (builds the comment, answer,
  check and an explanation from the nodes' own notes), `fit(template)` (re-rolls until the prompt is <= 220 characters
  and 10 lines and the answer whole; a template may `raise Retry`) and `named`. A new Flutter pack needs only NEW files
  (`pack_<x>.py`, `_<x>_*.py`); a pack of state/lifecycle questions writes its own `Item`s with a class in the prompt and
  an `await tester.tap(...)` check, with no model needed. **Running it**: `pytest tests/test_brain_packs.py -k Flutter`
  (~30 s: 2200 items from every flutter activity in ONE `flutter test`, about 7 s to compile + ~10 ms an item; each
  further flutter pack adds its items to that same run), `-k "FlutterShape"` for the instant checks. Flutter here is 3.29.1
  (Dart 3.7). Traps found: a child-less `Container` and a Wrap in a Row (unbounded width) behave very differently from
  what they look like - the model implements both; the oracle caught an unintended `RenderFlex overflowed` in a
  padded-Column position question.

## Glossary ("Words used": the vocabulary under Explain my code)

Built 2026-10-21 because "Explain my code" said what each line does but never what *falsy* or *scope* means. The
package `code_coach/glossary/` is plain data plus a matcher; `/api/explain` adds a `words` list to EVERY reader's answer
(Python, JavaScript, the farm's language) in the handler, once - never inside `explain.py`, `explain_js.py` or
`explain_farm.py` (a test greps for that). The same `WordsUsed` component (`web/src/components/WordsUsed.tsx`, rules in
the pure `web/src/lib/words.ts`, `styles/words.css`) is rendered under every explanation: `ExplainPanel` (coach strip and
Free mode), `BrainTools`, and the Workbook and Forms (`Katas.tsx`) walkthroughs. On a MISSED Brain Drills question,
`QuestionWords` shows a quiet "Words in this question" line of chips that open the same cards.

```text
code_coach/glossary/
  entry.py            Entry (frozen dataclass) + the writers: py(...), js(...), dart(...), both(...) (= all3: up to
                      three languages, one dict each)
  terms_values.py     truthy/falsy/boolean, types, numbers, strings, mutable/immutable, reference
  terms_basics.py     expression, operator, precedence, variable, scope, syntax, brackets, import...
  terms_flow.py       condition, comparison, short-circuit, branch, loops, index/slice, exceptions, recursion
  terms_functions.py  function, parameter/argument, return, closure, callback, class, generator, async...
  terms_python.py     None, list/tuple/dict/set, range, ==/is, f-string, comprehension, lambda, self...
  terms_javascript.py null/undefined/NaN, ==/===, template literal, arrow function, this, promise, event loop...
  terms_brain_*.py    the vocabulary of the Brain Drills packs (added 2026-10-21, ~85 words per language):
                      strings (whitespace, split, join, format, padding, ascii, palindrome...), collections
                      (set operations, min/max, sorting, stable sort, key function / comparator, swap, step, map/
                      filter/reduce in Python, enumerate in JS), functions (default and keyword arguments, mutable
                      default, side effect, call stack, late binding, block scope, shadowing, nested loop,
                      for-else, flag), classes (attribute/property, class vs instance attribute, static and class
                      method, inheritance, override, super, MRO / prototype chain, isinstance / instanceof, string
                      representation), logic (logical operators, De Morgan, truth table, bitwise, shifts, masks,
                      chained comparison, leap year, FizzBuzz, primes, division), errors (runtime error, error
                      message, TypeError / NameError / ReferenceError / IndexError..., traceback, line number, bug)
  terms_dart_*.py     DART, the third language (added 2026-10-22; Dart ids are letters only, kebab-case):
                      core (null safety: null, ?, !, ??, ?., ??=, late, final/const/var, type promotion, dynamic;
                      numbers, bool, String, List/Set/Map, record, enum, typedef; ~/ % (never negative), cascade,
                      spread, collection if/for, is/as; functions: named/optional/required/default parameters,
                      =>, closures, callbacks), types (class, constructors incl. named/factory/const/initializing
                      formals, getters, inheritance/override/super, abstract, implements, mixin, extension, generics,
                      toString, ==/hashCode, identical, private _names, patterns, switch statement/expression,
                      when, if-case, sealed), async (Future, async/await, then/catchError, Stream, async*/sync*,
                      event loop, microtask, isolate; try/on/catch/finally/rethrow, Exception vs Error,
                      FormatException, RangeError, StateError, TypeError, stack trace; interpolation, raw strings,
                      StringBuffer, RegExp, split/join/replace/padding/format; Iterable laziness, map/where/fold,
                      sort/compareTo, reversed, toList; import), basics (the everyday words in Dart form so the packs'
                      concepts resolve: expression, variable, scope, closure, recursion, loops, conditions,
                      short-circuit, index, slice, length...)
  terms_flutter.py    FLUTTER (it is Dart, so these are Dart-glossary entries): widget, StatelessWidget,
                      StatefulWidget, State, build, BuildContext, setState, lifecycle/initState/dispose, widget keys,
                      widget vs element tree, InheritedWidget/Theme/MediaQuery, ValueNotifier/ChangeNotifier/
                      ListenableBuilder, FutureBuilder, runApp, const widgets, hot reload; layout: constraints,
                      tight/loose, Row/Column, main/cross axis, flex, Expanded/Flexible/Spacer, Container, SizedBox,
                      Center/Align, Stack/Positioned, Wrap, AspectRatio, ConstrainedBox, overflow, ListView(.builder),
                      GestureDetector, InkWell, TextField/TextEditingController, Form/validator, Navigator, Route,
                      MaterialApp, Scaffold, Text. Most have NO example (a widget cannot run in plain `dart`).
  contexts.py         CONTEXTS: the seven ORIGINAL Brain Drills activities -> the words they always teach, plus
                      concepts_for(): every other activity's `concepts`, read lazily from code_coach.brain
  __init__.py         the loader (terms_* found BY NAME), find_words, lookup, resolve, context_words, words_for_context, payload
```

- **An entry** teaches one word in one language: `id` (kebab-case, unique per language), `term` (shown), `definition`
  (1-2 plain sentences, 300 characters at most, no word that is not itself defined), `rules` (short bullets), `example` +
  `out` (a small program in THAT language and exactly what it prints), `see` (ids in the same language), `aka`
  (other spellings for lookup), `detect` (regexes), `priority`. A word that means the same in both languages is written
  once with `both("id", "Term", "definition", python=dict(rules=..., example=..., out=...), javascript=dict(...),
  dart=dict(...))` (alias `all3`), which makes one separate entry per dict, so a rule can never leak across languages.
  Use `py(...)` / `js(...)` / `dart(...)` for one language. The Dart files use `dart(...)` with the same ids as Python's and
  JavaScript's for the everyday words (`loop`, `closure`, `scope`...), so a drill's `concepts` resolve in all three; the
  Python and JavaScript spellings of a Dart idea are `aka` (`optional chaining` -> `null-aware-access`, `tuple` ->
  `record`, `lambda` -> `anonymous-function`, `f-string` -> `string-interpolation`, `isinstance` -> `type-check`,
  `keyword argument` -> `named-parameter`, `floor division` -> `truncating-division`, `truthy`/`falsy` -> `boolean`
  (Dart has none), `self` -> `this`). Keep an aka on ONE entry (a test lists no two entries answering to a spelling the
  packs use). A Dart example is a BODY of `main` unless it mentions `main(` (the Brain Drills convention), so
  `print(...)` every line you show; `padding` is one card with a string sense and a Flutter sense on purpose (both
  packs use the word).
- **Adding a term** is one more `*both(...)` / `*py(...)` / `*js(...)` in a `TERMS` list (or a new `terms_<theme>.py`
  with `TERMS = [...]`: nothing to register). Then run `pytest tests/test_glossary.py`.
- **The oracle rule applies to examples AND rules.** Every example is run for real (python, node) and must print
  exactly `out`; the Truthy/Falsy `counts_false` / `counts_true` lists are run through `bool()` / `Boolean()`, the prose
  rule that lists the falsy values is parsed and run too, and the hand-written claims in the test (not read from the
  entries) are checked against the language. **Dart examples all run in ONE `dart run`** (`tests/dart_oracle.run_batch`),
  and every Dart RULE that can run is a program in `DART_RULE_CHECKS` (name = `"<entry id>: the claim"`, a program, the
  expected output or `CE` = "does not compile"; ~190 of them, e.g. `-7 % 3` is 2, `~/` truncates, `[1] == [1]` is false,
  a `const` list throws on `add`, `identical`, null-aware operators, record equality, microtask-before-event order,
  `rethrow` keeping the stack trace, a sealed switch missing a case not compiling); a test requires >= 80% of the Dart
  language words to have one. **Flutter rules** are held to real Flutter by `FLUTTER_CHECKS` (one `flutter test`,
  `tests/flutter_oracle.py`: flex split, Padding, Center loosening, Stack/Positioned, Row/Column overflow, ListView
  laziness, setState vs a plain field, lifecycle order, const widgets not rebuilt, keys, controller, Form.validate,
  Navigator push/pop, ValueNotifier vs ChangeNotifier); the Flutter words with NO check are named in
  `NOT_ORACLE_CHECKED` (widget, StatelessWidget, StatefulWidget, State, build method, BuildContext, widget/element tree,
  InheritedWidget, Theme, ChangeNotifier (only its notify count is checked, under ValueNotifier), ListenableBuilder,
  FutureBuilder, runApp, hot reload, layout, Route, InkWell, Text, ListView): their rules are well-known documented
  Flutter behaviour, and a test makes the list and the checks partition the Flutter ids. The rules of the `terms_brain_*` files are backed by `RULE_CHECKS` in the
  test (one small program per claim, e.g. `sorted` stability, `str.index` raising, JS `replace` changing only the first
  match, `Math.max()` being `-Infinity`, the leap-year rule against `calendar.isleap` / `Date`, De Morgan over all
  four inputs, primes against a sieve): add a line there when you add a runnable rule. Write a rule only if you can say how a test would catch it being false.
  Keep every rule language-correct: Python's empty list is falsy, JavaScript's is truthy; `%` takes the sign of the
  right side in Python and the left in JavaScript; `round(2.5)` is 2 but `Math.round(2.5)` is 3.
- **Detect hygiene.** A regex must never backtrack without end: `(?:[ \t]+[^\n]*\n?)*?` (an OPTIONAL newline after a
  `[^\n]*`) once hung `find_words` on a class with a few methods - use `[ \t]+\S[^\n]*\n` for "one more indented line".
  A test feeds a 40-method class and 300-line loops through every pattern. Generic words (`sum`, `state`, `counter`,
  `character`, `bug`...) carry no `detect` or a priority <= 50, and a test checks that plain snippets (`x = 5`,
  `if x > 3`, a one-method class...) wake none of the `terms_brain_*` cards.
- **Matching** (`find_words(code, language, context=None, limit=8)`): context words first (all of them, in the
  context's order), then the entries whose `detect` regexes hit the code - run on the code with comments removed and
  string contents blanked, so a word inside a string is not code (a pattern starting `raw:` sees the code as written) -
  sorted by `priority` (high first) then first appearance; never more than `limit`, no word twice. An unknown language,
  junk or empty code: `[]` or just the context's words, never an error. `language_for` maps `tfwr` to Python and
  `typescript` to JavaScript, and `dart` is its own language; any other app language has no glossary yet, so `words` is
  empty. Dart strings are blanked by their own rules (`//` and `/* */`, raw `r'..'`, triple quotes, `'` and `"`).
- **Contexts** (what a Brain Drills activity always teaches, shown first by `find_words` and as the "Words in this
  question" chips). The ORIGINAL seven keep their hand-written ids in `contexts.CONTEXTS` (eval: expression, evaluate,
  operator, precedence; truthy: truthy, falsy; loops: loop, iteration, off-by-one, range (Python only); trace: variable,
  assignment, reassign; brackets: bracket, balanced, nesting; recall: variable, value, assignment; syntax: syntax,
  syntax-error, token, keyword). EVERY OTHER activity (every pack) is DERIVED, with no glossary edit: its
  `Activity.concepts` are plain lowercase words, and `glossary.resolve(language, word)` turns each into an entry per
  language - `lookup` first (id, term or aka), then ignoring case, hyphens, spaces and a plural (`type coercion` ==
  `type-coercion`, `tostring` == `toString`, `closures` == `closure`; an id beats a term, which beats an aka). A concept a
  language has no word for is skipped for that language (JavaScript has no `range`, Python no `tostring`); order is
  kept, no word twice. The brain package is imported lazily inside `contexts.concepts_for`, so the glossary never
  imports it at import time (a test holds that). `tests/test_glossary.py` checks, for every activity and each
  language it is PLAYED in (`Activity.languages`: a Dart-only activity is skipped for Python and JavaScript, and
  `/api/glossary?language=dart&context=fl_flex` answers the Dart/Flutter words: Dart concepts are resolved in Dart only), that
  the context is non-empty (>= 2 words when the activity lists >= 2 concepts), and
  `test_concepts_that_resolve_in_no_language_the_activity_is_played_in_are_few_and_visible` fails (naming the words) when
  an activity has more than `MAX_UNRESOLVED_PER_ACTIVITY` concepts that no entry answers to IN A LANGUAGE IT IS PLAYED IN (a
  Dart activity is judged by the Dart glossary alone, so a Dart pack author's new word needs a Dart entry or an `aka` on one;
  today every Dart/Flutter concept of every pack resolves in Dart). The original seven are not played in Dart: their
  hand-kept ids are only required in Python and JavaScript. **Teaching a pack author's new word** = writing
  the entry in a `terms_brain_<theme>.py` (or any `terms_*.py`) with the word as its id, term or an `aka`; a word that
  genuinely exists in only one language is fine - prefer a counterpart under the same word when there is one
  (`nonlocal` -> JS closure, `keyword argument` -> JS options object, `method resolution order` -> JS prototype chain,
  `isinstance` <-> `instanceof`, `self` -> `this`). `BrainTools` passes `activityId` as `context`; every other caller
  passes nothing.
- **API**: `POST /api/explain` takes an optional `context` and answers `words: [{id, term, language, definition, rules,
  example, example_output, see_also: [{id, term}], counts_false, counts_true}]` (the other fields are unchanged; for
  Dart the answer stays `ok: false` with "no reader yet", and `words` still ride along, because the handler adds them
  whenever the language has a glossary but no explainer);
  `GET /api/glossary?language=&term=&context=` gives one word (id, term or alias), a context's words, or the whole
  language, and never an error (unknown means `[]`). "See also" chips jump to a card already on screen or fetch the word.
- **Not yet**: other app languages (C, Go...), the Workbook/Predict modes passing a `context` of their own, a
  syntax-error-aware match (Free mode with a typo shows the words of the code, not "syntax error"), and a Dart/Flutter
  reader for Explain (the chips and cards need none). The Brain Drills Explain button for Dart stays disabled, so its
  "Words used" are seen in Free mode (the coach strip) only.

## Gotchas (the "<Language> Quiz" feed: 19 languages)

Built 2026-10-19 for Python, JavaScript and C; opened to every language the app can run on 2026-10-20 (mode id
`gotchas`, tab "Gotchas" after Session/Brain Drills in `ModeBar.tsx`, branch in `App.tsx`). An endless feed of trap
questions, one at a time: a short program on a dark card with a glowing "Rust Quiz" title in the language's own
accent colour, four answers (click, 1-4 or A-D), instant right/wrong, the one-line trap and a plain "Why", a **Run
it** button, **Next** (Enter, Space, right arrow), a streak ("5 in a row"), "Deck: 34/80 seen", and a language
switch (see "The picker"). It is not part of the session queue (no `lastKeys.ts` entry).

```text
code_coach/gotchas/
  langs.py       THE REGISTRY: one Lang per language (see below) + Syntax for the colourer
  toolchains.py  how to build and run one program per language (engine's toolchain lookup) + availability probes
  runner.py      run_program()/run_twice(): throwaway folder, bare env, no stdin, 5 s run, 15 s build, 64 KB
  __init__.py    DECKS, found BY NAME: content_<stem>, content_<stem>2, 3...; available_languages(), languages_payload()
  content_*.py   the cards. python=content_py/py2/py3 (324), javascript=content_js/js2/js3 (264), c=content_c (116);
                 every other language is content_<id>.py (+ content_<id>2.py...) - 3 seed cards each so far
  items.py       Item; make("rust") builds a card (ids are <prefix>-<slug>: py-, js-, c-, cpp-, rs-, cs-, kt-...)
  store.py       GotchaStore: picking, answering (+ confidence and note), the Daily 5, My traps, the user's cards;
                 gotchas.json / gotchas_user.json
  user.py        'Add a quiz I found': run, check, build the options (any language)
web/src/lib/gotchas.ts          streak, keys, deck line, language choosing (quick buttons, filter, arrows), accent hue
web/src/lib/codeColors.ts       the syntax colourer; knows no language by name, takes the server's Syntax
web/src/components/Gotchas.tsx, GotchaLangMenu.tsx, GotchaAdd.tsx, GotchaTraps.tsx, GotchaCode.tsx; styles/gotchas.css
tests/test_gotchas_langs.py     the one parametrised file: registry, loader, shape of every card, the oracle, routes
tests/test_gotchas_store.py     serving, answering, the Daily 5, user cards, routes
tests/test_gotchas_confidence.py  confidence, notes, scheduling offsets, My traps (store and routes)
tests/test_gotchas_ts.py        the browser-side rules in node (keys, wording, sorting) and the stylesheet's contrast
```

### The registry (`gotchas/langs.py`)

`LANGS` is the display order: Python, JavaScript, TypeScript, C, C++, Java, C#, Go, Rust, Dart, Kotlin, Swift, Ruby,
PHP, Lua, Zig, Odin, Common Lisp, SQL (SQLite). Each `Lang` has: `id`, `name`, `title` ("Rust Quiz"), `prefix` (card id
prefix), `ext`, `module` (the content file stem when it is not the id: python `py`, javascript `js`), `syntax` (keyword,
type and constant sets, comment and string syntax; served to the browser in `/api/gotchas`), `banned` (regex + reason
pairs: patterns a built-in card may not contain, so the answer is the same on every machine and every run), `check`
(a free-form extra test, e.g. Go: ranging over a map needs a sort), `notes` (one paragraph of portability advice for card
writers - read it before writing a deck), `reads_input` (a regex for stdin reads, refused in user cards), `raises`
(whether a card may end in an uncaught error: Python and JavaScript only), `output_on_stderr` (Zig: `std.debug.print`
writes to stderr, so on a clean exit the runner reports stderr as the output) and `missing` (the words for a missing
toolchain). `toolchains.available(id)` is the probe: it rides on the engine's cached PATH lookups (`engine._which`, 60 s),
so a language whose toolchain is missing is simply not offered.

### How a language is run (`toolchains.plan`)

`runner.run_program(language, code)` writes `snippet.<ext>` in a throwaway folder, builds it if the language builds
(15 s ceiling), runs it (5 s, stdin closed, 64 KB, killed as a tree on a timeout) and deletes the folder. Python and
JavaScript are run straight away; C is `engine.compile_c` (gcc, clang or Visual Studio); C++ and Rust use the engine's
`_COMPILERS` (C++ falls back to MSVC); TypeScript is `tsc --strict` then node; Kotlin is `kotlinc` then `java -cp`; Swift
is `swiftc` then the exe with the Swift runtime on PATH; Go, Zig and Odin are built (`go build`, `zig build-exe`, `odin
build`) and the exe run; Ruby, PHP and Lua are run by the engine's interpreter; SQL is a tiny driver script on `sqlite3`
that prints the rows of the LAST SELECT on one line (`a|b` per row, rows joined by `; `, NULL as NULL). Java (`java
Main.java`), C# (`dotnet run file.cs`), Dart (`dart run`) and Lisp (ABCL) compile inside the run command: those are
`Plan.one_step`, and the 5 s clock gets the 15 s build allowance on top (the test allows 9 s). **Environments**: the program
gets `child_env()` (SYSTEMROOT, TEMP, TMP only); the one-step tools and the interpreters that need to find their install
get a whitelist (`_TOOL_KEYS`: PATH, USERPROFILE, LOCALAPPDATA... never keys or tokens), with TEMP pointed into the folder
so what they leave is deleted with it; compilers get the machine's own environment (they need it). Compiler warnings are
never output; a failed build is `compile_error` with `snippet.rs:3:5: error...` (temp paths tidied) and its first error is
what a refusal quotes. **No toolchain => not offered**: `gotchas.available_languages()` is the registry languages whose
probe says yes AND that have at least one card; `/api/gotchas` and `/next` return them as `languages: [{id, name,
count, title}]` (display order); every route answers 400 "No Go toolchain is installed, so the Go quiz is not available on
this computer." (or "...has no cards yet.") for the rest, and the cards are still imported (`DECKS`), just not offered.

### Adding a deck (what a content author does)

Create `code_coach/gotchas/content_<id>.py` (or `content_<id>2.py`, `3`... for more) exposing `ITEMS`, written like the
existing ones (`q = make("<id>")`, then `q("slug", code, answer, [3 wrong], trap, why)`). **Touch nothing else**: the loader
finds the file by name, `__init__.py`, the registry and the tests need no edit. Cards are served in file order, so the first two
of a language's first module are what a new player meets first (`py-score-90`, `py-loop-var-list`, `c-int-division`,
`c-modulo-negative` stay first). Then run `pytest tests/test_gotchas_langs.py -k "<id>-deck"` (the test ids are `<id>-deck`,
so `-k rust-deck` runs just Rust; for the short ids use `-k "c-deck"` / `"go-deck"`): it checks the shape (unique ids with the
language's prefix, 16 lines and 76 columns at most, three distinct wrong options once whitespace is ignored, one-line
options, a trap of 100 characters at most and a 1-4 sentence why, no banned patterns from the registry, no
address-like answers) and then **runs every card for real** with the workbook's own runner (`engine.run_code`, a different code
path from the quiz's), and again with the quiz's runner (one build, two runs: same output, under 5 s). A module that fails
to import is skipped, recorded in `gotchas.LOAD_ERRORS` and fails `test_every_content_module_imports_cleanly` - it never takes
the app down. A language with no cards yet is skipped by the tests ("no <X> cards yet") and not offered; one whose toolchain
is not installed is skipped with the toolchain named. Python, JavaScript and C keep their own exhaustive oracles
(`test_gotchas_content.py`, and `test_gotchas_c.py` for the compilers/sanitizers); the generic file only samples them.
A language's `BANNED` list is the portability idea: make the answer the same on every machine and every run (no clock,
randomness, input, addresses, hash or map/set iteration order, unspecified evaluation order); when a card trips
one, change the card, never the list (unless the pattern is simply wrong).

### The cards

- **The oracle rule, strictly.** The answer written in `content_*.py` is never trusted: the tests run every card in the
  real toolchain and fail unless stdout is exactly the marked answer (Python: three hash seeds; the rest: the workbook runner
  once and the quiz runner twice from one build). **A new card**: `q("slug", code, answer, [3 wrong], trap, why)` - the code
  prints ONE line (`raises=True`, Python and JavaScript only, makes the answer an error name and the program must print
  nothing first); make the wrong options real misreads. Event-loop JS cards collect steps into an array and print once; keep JS
  environment-proof (no top-level `var`, no `window`). A program is at most 16 lines and 76 columns.
- **C**: the card is a whole program, compiled and run for real. `tests/test_gotchas_c.py` builds every card with this
  file's own subprocess calls (`-std=c11 -Wall -Wextra -pedantic`) as clang/gcc at -O0 with `-fsigned-char`, at -O2, at -O1 with
  `-funsigned-char`, under `-fsanitize=address,undefined`, and with Visual Studio at `/Od` and `/O2 /J`, and fails unless
  every build prints exactly the marked answer, the same bytes as the baseline, nothing on stderr; warnings must be in
  `BENIGN_WARNINGS` (never `NEVER_BENIGN`). Portable C only: no undefined behaviour, nothing implementation-defined (plain
  `char`, `sizeof(long)`, `%p`, `%.0f` half cases, argument evaluation order). About 2 minutes.
- **Seeds written while proving the runners** (3 each; extend them): TypeScript, C++, Java, C#, Go, Rust, Dart, Kotlin,
  Swift, Ruby, PHP, Lua, Zig, Odin, Lisp, SQL. Traps found on the way are in each `Lang.notes`: Lua `print(a, b)` is
  tab-separated; Zig prints to stderr; Swift `import Foundation` costs ~90 s the first time; TypeScript's lib is ES2020;
  Odin refuses an untyped 1e21; Go loop variables are per-iteration; Rust prints floats without exponents.
- **Serving** (`GotchaStore.pick`, in order): a card the user just added and not yet answered ("Yours"); the first two
  cards of a language's deck while fewer than two are seen; a card that is due (`ticks` counts
  answers per language; a miss is due 5-10 answers later, a miss you were Sure about 2-4 later and ahead of the
  rest, a right answer you only guessed 10-20 later: see "How sure, my reasoning, my traps"); an unseen card, at random; otherwise the card seen longest ago. `exclude` (the last 3 ids the client
  saw) is honoured unless it would leave nothing. `/api/gotchas/next` never carries the answer, the trap or the why;
  `POST /api/gotchas/answer {id, language, chosen, confidence?, note?}` returns them (`GET /api/gotchas/next?card=<id>` serves one
  named card the same way, answer hidden: that is My traps' Try again). Options are shuffled deterministically: a built-in card's
  right letter comes from a block-wise balanced shuffle (every four consecutive cards use A-D once) - the balance tests only
  look at decks of 40+ cards. Unknown id / language / chosen is 400.
- **Files** beside the progress file, written with Momentum's atomic writer and read with `momentum.engine.read_state`
  (a broken file is kept as `.bad`): `gotchas.json` (per-card `seen/right/last_day/last_tick/due`, per-language `ticks`,
  streak now/best, today's Daily 5, **all keyed by language id and created lazily**, so an old file keeps loading and a
  new language starts empty) and `gotchas_user.json`. Per card also `sure_right/sure_wrong/guess_right/guess_wrong`,
  `sure_run`, `due_kind`, `note` and `notes` (all optional on load: an old file without them is a card with no claims). Nothing goes into the progress file's schema.
- **Run it** is `POST /api/gotchas/run {id, language}`, not `/api/visualize`: the card's own program runs through
  `runner.py` (the same runner that checks a user's card). It takes a card id, never arbitrary code.
- **Daily 5**: five cards per language and calendar day (fewer if the deck is smaller), seeded by date+language, weighted
  missed 4 (any card still due, so a sure-and-wrong or shaky one counts as missed) / unseen 3 / right 1, made on the first request of the day and **kept in `gotchas.json`**. Any first answer to
  one of the five fills its dot; the answer that fills the last says `just_completed`.
- **Add a quiz I found** (`/api/gotchas/user`: GET list, POST create, POST `/preview`, DELETE `/{id}`; 400 on a refusal
  with the reason in words), for every language: the user pastes code (<= 60 lines), optionally types up to 4 options and
  picks the one they think is right. The server runs it **twice** and takes the real stdout as the truth; it refuses empty,
  too long, over 5 s, waiting for input (the language's `reads_input`), different output per run, nothing printed, a
  crash or non-zero exit (every language but Python and JavaScript, whose cards may be error cards), a syntax error, more
  than 10 lines / 300 chars of output - and a program that does not compile, quoting the compiler's first error. Typed options
  that match the real output are kept as the right one, the rest are misreads; blank slots are filled only by
  `generate_distractors`. Cards are served with a "Yours" badge, first right after adding, and can be deleted.
- **Momentum**: `gotcha` (12 XP, key `gotcha:<language>:<id>`, once a day per card, on each right answer only) and
  `gotcha_daily` (30 XP, key `daily:<language>:<date>`). The key is any string (`rules.clean_key`, 200 characters), so a
  new language needs nothing; `tests/test_gotchas_langs.py` pays one for a new language.

### How sure, my reasoning, my traps

Added 2026-10-21 to strengthen the think-hard-then-read-why loop. None of it touches Momentum (XP, keys and prices are unchanged).

- **How sure are you?** A two-way control above the answers, `Sure | Just guessing` (default Sure; clicks, or the keys **S** and **G**
  which *set* it, only before answering; kept for the session in component state, never saved). It is sent with the answer as
  `confidence: "sure" | "guess"`; the store cleans it (`clean_confidence`: anything else, any type, is "", never a 422) and counts it
  per card (`sure_right`, `sure_wrong`, `guess_right`, `guess_wrong`; `seen`/`right` keep counting every answer). After the reveal
  (`feedbackLine` in `lib/gotchas.ts`, the wording is held to no loss/shame words by a test): sure and wrong says "You were sure -
  this one is worth remembering"; right but guessed says "Right - but you guessed, so it will come back"; sure and right is the plain
  success; a wrong guess is the ordinary miss. The answer reply adds `confidence`, `comes_back` and `note`; `again_soon` is still
  just `not correct`.
- **Scheduling** (`store.RETURNS`, `return_offset`: the offset is inside the range, spread by a hash of card + answer count, so it
  is the same on every run): a **miss** (wrong, with a guess or no claim) is due **5-10** answers later; a **sure-and-wrong** miss
  **2-4** later (`due_kind` `sure_wrong`); a **right-but-guessed** card is "shaky" and comes back once **10-20** later (`shaky`).
  Among due cards the order is sure_wrong, then miss, then shaky, then the earlier due (`DUE_RANK`). A shaky card answered right
  and Sure (or right with no claim) is done like any right card; answered right with a guess again it is shaky again; answered wrong
  it is a miss. The browser withholds the last 3 cards it showed (`exclude`), so in the feed a +2 card shows from +3.
- **Mastered / "missed and not yet mastered"**: a card is in **My traps** when it was answered WRONG at least once (`seen - right
  >= 1`) and its last two answers have not both been right AND marked Sure (`sure_run < MASTERED_RUN = 2`; `sure_run` counts the
  current run of right-and-Sure answers, a guess, an unclaimed answer or a miss resets it). An old record has `sure_run` 0, so an old
  missed card shows until it is answered right-and-Sure twice. A card that was only ever right (even if guessed) is not a trap.
- **Your reasoning**: an "Add my reasoning" button under the answers (collapsed; one textarea, 300 characters with a counter,
  placeholder "Why do I think so? (optional)"), before answering only. Sent as `note` (trimmed, cut to 300 by `clean_note`); kept as
  the card's last `note` and a `notes` history of the last 3 `{day, note, correct}`. After the reveal the Why panel shows "What you
  thought:" with it. Never required, never changes scoring. **Keys**: `keyAction()` in `lib/gotchas.ts` is the one decision for
  every quiz key (1-4, A-D, S, G, Enter, Space, right arrow); it returns nothing while focus is in an INPUT, TEXTAREA, SELECT or
  contenteditable (the usual bug: typing a note answered a card), while My traps is open, or with Ctrl/Cmd/Alt. Escape inside the
  box closes the box only (stopPropagation); `tests/test_gotchas_ts.py` also checks the window handler delegates to it.
- **My traps** (`GotchaTraps.tsx`, an inline view that replaces the feed while open; the feed stays mounted, `hidden`, so an
  unfinished Add-a-quiz form survives): the header's "My traps" button, Escape or "Back to the quiz" returns (focus goes back to
  the button). Filter pills: the current language (default) | All languages. Each trap shows the code (compact `<pre>`, scrolls
  inside), language and card title (`card_title`: `py-score-90` is "Score 90", `mine-3` "Your card 3"), the trap line, the Why,
  "Missed N times", badges "Sure but wrong" (`sure_wrong > 0`, ever) and "Shaky" (the last answer was a right guess), "Yours", your
  last note, the last day, and **Try again**, which serves that card in the feed (a card of another language switches to it first).
  `GET /api/gotchas/traps?language=<id>|all` (default `all`; unknown language, or one with no toolchain, is 400; `all` is the offered
  languages) returns `{language, traps: [...]}` sorted by `store.sort_traps` (sure-but-wrong first, then most misses, then most
  recent day, then answer count; `sortTraps` in `lib/gotchas.ts` is the same rule and a test holds the two together). It only
  ever lists cards that have a record (already answered), never carries the answer key, includes your own cards on the same terms,
  and skips a record whose card no longer exists.

### The picker and the look

- **The picker** (`GotchaLangMenu.tsx`; the rules are pure functions in `lib/gotchas.ts`, tested in node): up to 4 quick
  buttons - the language on screen, then the last-used ones (`code-coach:gotchas-recent`), topped up with Python, JavaScript...
  - always shown in registry order so nothing jumps; plus **More** (an accent outline and the `on` class while its menu is
  open) listing every available language with its card count. The menu has a search box that filters as you type (names and
  ids that start with the text first, then ones that contain it), arrow keys / Home / End, Enter to pick, Escape to close
  (focus goes back to More) and closes on an outside click; `aria-activedescendant` keeps the focus in the search box. The
  choice is remembered in `code-coach:gotchas-language`; an id the server does not offer falls back to Python (the saved
  value is kept, so the language is back when its toolchain is). At 375 px the buttons wrap inside the pill and the menu is
  full width; the page never scrolls sideways.
- **Accent**: each card gets `--gq-accent` from `accentStyle(language)`: Python, JavaScript and C keep their old colours,
  every other language a hue from a salted hash of its id at fixed saturation and lightness (`ACCENT_S/L`), which
  `tests/test_gotchas_ts.py` holds to 4.5:1 on the card at EVERY hue, and to at least 5 degrees apart for the registry.
- **Colouring** (`lib/codeColors.ts`): `tokenize(code, syntax)`; every character ends up in exactly one run, so the runs
  join back into the source (tested for every card of every language, and for an odd string under every language's rules).
  Rust lifetimes and Lisp quotes are not strings (`charLiterals`), Lua's `--[[ ]]`, Lisp's `#| |#`, SQL's keywords in any case, Go's
  raw strings, `println!` macros and C-family `#directives` are handled by the data, not by name.
- **Look / accessibility**: the code is real text in a `<pre>`; token colours and card text are held to 4.5:1 by
  `tests/test_gotchas_ts.py`; right/wrong also carry a mark and screen-reader text; all motion is CSS and off under
  `prefers-reduced-motion`. At 375 px the page does not scroll sideways; only the code scrolls, inside the card.
- **Testing by hand**: use the sandbox copy (see Momentum), and note this machine's extra toolchains live in
  `~/toolchains` and the rust proxy in `~/.cargo`: with `USERPROFILE` redirected, make a junction
  (`New-Item -ItemType Junction -Path <temp home>\toolchains -Target C:\Users\Justin\toolchains`) and set `RUSTUP_HOME`
  and `CARGO_HOME` to the real ones, or those languages vanish from the menu (which is also the quickest way to check an
  unavailable language is hidden: delete the junction - only the junction - and restart the sandbox API). Drive it with synthetic
  `keydown` events on `document.body` for volume (the card carries `data-card-id`); `form_input` turns `[1, 2]` into
  `1,2`, so fill option fields through the native value setter instead. The hidden browser pane renders a beat late:
  read state with JavaScript rather than trusting the first screenshot.

### What card writers learned the hard way (per language)

Each deck was written against the real toolchain and the oracle caught these; they are not in `langs.py` notes.
- **Every language:** the harness `strip()`s output and compares the answer stripped, so an answer cannot start or end
  with spaces (start a padding card with a visible character such as `[` or `|`); wrong options are compared after
  collapsing whitespace, so options that differ only in spacing are rejected.
- **TypeScript:** library is ES2020 with no node typings; `NaN == NaN`, `+null` and `switch (2) { case 1: }` are
  `--strict` compile errors. **Java:** the launcher runs the first class in the file (helpers go nested or after `Main`);
  use `Locale.ROOT` in `String.format`. **Go:** `fmt` prints maps sorted (printing a whole map is safe); recent-Go
  features (`min`/`max`, `range N`, range-over-func) are fine on the registry's Go. **Rust:** avoid iterator-consumption
  cards on `zip` over ranges (std-specialised, version dependent).
- **C++:** clang errors on chained comparisons (`a > b > c`); `time` is banned even in a comment or string.
  **C#:** any compiler warning (nullable CS86xx, unused variable) lands in stdout and breaks the card, so cards build
  warning-free (`string?`); print doubles with `FormattableString.Invariant($"...")`; `cond ? 'a' : 0` types as `int`;
  two concurrent `dotnet run` builds can print an NU1900 warning (a flake, not a card problem). **Kotlin:** `List` is
  covariant, `listOf(a) + listOf(3)` appends an element when it type-checks. **Swift:** never import Foundation (a ~90 s
  first build); `Set`/`Dictionary`/`.keys`/`.values` and any `[digits : x]` pattern trip the ban; `lazy` collections can
  re-run closures on subscripting (use `first(where:)`); string ordering is by Unicode scalars.
- **Ruby 4.0:** `1e15.to_s` is `"1.0e+15"` (stay away from that boundary); `Hash#inspect` and `Set#inspect` changed in
  recent versions, so do not print them with `inspect`. **PHP 8.5:** warnings and deprecations print to **stdout** with the
  temp path, so a card that triggers one fails (`"a"++`, a multi-character string-offset write, `null` as an array offset,
  `${var}`, fractional float keys, `%` on floats, a bool-returning `usort` callback); skip version-dependent behaviour
  (`round()` changed in 8.4, `range("1","3")`, negative array keys); `echo` uses `precision=14`, `json_encode` the shortest
  round trip; no `mbstring`. **Lua 5.4:** a string operand in a bitwise op is an error; print a comparison instead of
  `inf`/`nan`; runtime errors carry the script path. **Dart:** `e.runtimeType` of a `TypeError` is the private
  `_TypeError` (use `e is TypeError`); `Future.catchError` throws if the handler's type does not match (use `.then<int>`).
- **Zig:** literal-only arithmetic is folded at compile time (overflow, division, `if` on constants become compile errors),
  so pass values through parameters or a mutated `var`; `{d:.N}` rounds the shortest decimal half up (pin it to a value
  like 0.16); `var x: T = undefined;` and the word `args` are banned; build a `const out = .{...}` to stay within 76
  columns. **Odin:** `[dynamic]int{1,2}` needs `#+feature dynamic-literals` (use `make` + `append`); do not print
  non-ASCII; `%5.2f` zero-pads; a whole-number float prints without `.0`; literal-bound `4..<0` and `~5` on an untyped
  constant are compile errors. **Lisp (ABCL):** `loop ... maximize` over nothing, fresh-binding-per-iteration closures and
  `sort` on a list are implementation-dependent; use `format t` (`print` emits a leading newline). **SQL (SQLite):**
  statements are split on `;` (none inside a string literal); `strftime` with fixed literals is the date route; always
  `ORDER BY` unless the result is one row.

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
- **Server-only kinds** (`rules.SERVER_XP`: `farm_milestone`, `farm_return`): paid by the server
  from what it sees (`Momentum.award_server`, a base the caller names), refused by the award
  route (400) and exempt from the "every kind is sent by a screen" test. `farm_milestone` is a
  lifetime kind (`LIFETIME_KINDS`): its dedupe is the file's `once` list (paid once ever), not the
  day's keys. Both are passive (`PASSIVE_KINDS`): they keep the combo and count for the streak but
  are not a "thing solved" or a "mode used" for a quest. An award answer may carry a `label`
  ("Farm: first pumpkin! (Python)") that the toast says first. Quests can also read per-day
  counters (`DayStats.counters`, a day's `counters`; `record_farm_items`) that are not awards:
  `farm_items` (quest "Harvest 50 items on the farm") and `farm_buy` ("Buy a research upgrade"),
  both in group `farm`. The welcome-back: `farm_visit` (the Farm opened >= 30 min after the last
  look, `farm.last_seen`, kept fresh by the polling's `farm_touch`; first visit ever = none) records
  an offer in `farm.away`; `claim_welcome` pays `welcome_xp(ripe)` = 15 + 1 per 10 ripe (max +10)
  as kind `farm_return`, once a day, only for an offer made today. To see the card in the sandbox,
  set `farm.last_seen` back in its `momentum.json` while the Farm is closed.
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
