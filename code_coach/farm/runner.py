"""Running a player's program against the farm, and keeping the farm.

There is one farm (one save) and at most one program running on it. The
program is a real Python, Node or Dart process; a thread here reads its
drone commands one line at a time, does each on the World, and paces the
answers so the program takes the game time it would take in the game -
an action at the start is half a second - sped up by the time warp you
pick. Stopping answers the next command with "stop", and kills the
process if it is busy elsewhere.

When nothing is running, the farm still lives: each time the screen asks
for it, it moves on by the real time since it last asked (a few seconds at
most, so a closed tab does not come back to a harvest).

The save sits next to the progress file - farm_save.json - with the code
you last wrote in each language.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from code_coach.farm import data
from code_coach.farm.protocol import FUNCTIONS, MARK, STOP, answer, decode_request, refuse
from code_coach.farm.world import Refusal, World, spell_function

#: "original" is the game's own language: Python's syntax, run by our interpreter
#: (stubs/farm_lang.py) so that every operation costs ticks, as in the game.
LANGUAGES = ("original", "python", "javascript", "dart")
#: JavaScript drones read the program with TypeScript's parser (see stubs/farm_api.js).
TYPESCRIPT = Path(__file__).resolve().parents[2] / "web" / "node_modules" / "typescript" / "lib" / "typescript.js"
#: How far the farm may move on between two looks when nothing is running.
IDLE_CATCH_UP = 2.0
#: A program that sends no drone command for this long (real seconds) is
#: stuck in a loop with nothing in it; it is stopped and told so.
SILENT_LIMIT = 15.0
#: Dart compiles before it runs; its first command can take a while.
FIRST_COMMAND_GRACE = 30.0
#: How big a drone's job (function, arguments, globals) may be: it goes in an
#: environment variable, and Windows allows about 32,000 characters for all of them.
DRONE_JOB_LIMIT = 24000
#: Warps the screen offers; 0 means as fast as the machine goes.
WARPS = (1, 2, 4, 8, 16, 64, 0)

STARTER_CODE = {
    "original": "# Your first program: harvest the grass under the drone.\n"
                "# Run it a few times, collect hay, and buy Loops.\nharvest()\n",
    "python": "# Your first program: harvest the grass under the drone.\n"
              "# Run it a few times, collect hay, and buy Loops.\nharvest()\n",
    "javascript": "// Your first program: harvest the grass under the drone.\n"
                  "// Run it a few times, collect hay, and buy Loops.\nharvest();\n",
    "dart": "// Your first program: harvest the grass under the drone.\n"
            "// Run it a few times, collect hay, and buy Loops.\nvoid main() {\n  harvest();\n}\n",
}


#: A file's name: a module name in all three languages, and lowercase because
#: Windows filenames ignore case.
FILE_NAME = re.compile(r"^[a-z_][a-z0-9_]{0,23}$")
#: Names the libraries use for themselves.
RESERVED_FILES = ("farm_api", "runner", "package")

#: What a new file starts with.
STARTER_HELPER = {
    "original": "# Functions here can be used from your other files:\n"
                "#     import {name}   or   from {name} import harvest_column\n\n",
    "python": "# Functions here can be imported from your other files:\n"
              "#     import {name}   or   from {name} import harvest_column\n\n",
    "javascript": "// Export what your other files import:\n"
                  "//     import {{ harvestColumn }} from \"./{name}.js\";\n\n",
    "dart": "// Your other files use this one with:\n"
            "//     import '{name}.dart';\n\n",
}


def _starter_files() -> dict[str, dict[str, str]]:
    return {lang: {"main": STARTER_CODE[lang]} for lang in LANGUAGES}


def save_path() -> Path:
    from code_coach.progress.store import active_store

    return active_store().path.with_name("farm_save.json")


#: (Drone has a field called `time`, which would hide the module inside its body.)
_now = time.monotonic


@dataclass
class Drone:
    """One drone: its process, its own clock of game time, and where it is."""

    id: int
    proc: subprocess.Popen | None = None
    time: float = 0.0
    x: int = 0
    y: int = 0
    hat: str = "Straw_Hat"
    status: str = "running"  # running, done
    #: Waiting for its turn with a command in hand.
    pending: bool = False
    #: Inside wait_for, waiting on another drone: it can't act before that one ends.
    blocked: bool = False
    result: Any = None
    ticks: int = 0
    commands: int = 0
    last_command: float = field(default_factory=_now)


@dataclass
class Run:
    id: int
    language: str
    warp: float
    workdir: str = ""
    argv: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    status: str = "starting"  # starting, running, done, stopped, error
    error: str = ""
    error_line: int = 0
    #: The player's file the error is in, when there are several.
    error_file: str = ""
    stop: bool = False
    finished: bool = False
    started: float = field(default_factory=_now)
    commands: int = 0
    drones: dict[int, Drone] = field(default_factory=dict)
    next_drone: int = 1
    #: Real time and game time when the run began, for pacing.
    clock_start: float = field(default_factory=_now)
    time0: float = 0.0
    #: The program's files and the one that runs, so a simulation can start another.
    files: dict[str, str] = field(default_factory=dict)
    entry: str = "main"
    #: The farm this run plays on: None for the real one; a simulation's own World.
    world: World | None = None
    #: A simulation knows the run that started it; that run knows the simulation
    #: going on now, and waits - every drone of it - until it ends.
    parent: "Run | None" = None
    sim: "Run | None" = None
    sim_file: str = ""
    sim_speedup: float = 0.0


class _Stopped(Exception):
    """The run was stopped while a command was waiting on something."""


class FarmHost:
    """The one farm, its save, and the program running on it."""

    def __init__(self) -> None:
        self.lock = threading.RLock()
        #: Drones take turns under this, in game-time order.
        self.turns = threading.Condition(self.lock)
        self.world: World | None = None
        #: Each language's files (name -> code), and which one Run runs.
        self.files: dict[str, dict[str, str]] = _starter_files()
        self.entry: dict[str, str] = {lang: "main" for lang in LANGUAGES}
        self.language = "original"
        self.warp: float = 1
        self.run: Run | None = None
        self.output: list[dict[str, Any]] = []
        self._next_run = 1
        self._last_look = time.monotonic()
        self._last_save = 0.0
        self._path: Path | None = None

    # ── Saving ──────────────────────────────────────────────────────────

    def _load(self) -> World:
        path = save_path()
        if self.world is not None and self._path == path:
            return self.world
        self._path = path
        self.world = World()
        self.files = _starter_files()
        self.entry = {lang: "main" for lang in LANGUAGES}
        self.output = []
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                self.world = World.from_json(raw.get("world", {}))
                saved = raw.get("files")
                if isinstance(saved, dict):
                    for lang, files in saved.items():
                        if lang in LANGUAGES and isinstance(files, dict):
                            kept = {str(k): str(v) for k, v in files.items() if FILE_NAME.match(str(k))}
                            if kept:
                                self.files[lang] = kept
                else:
                    # A save from before files: its one program becomes "main".
                    for lang, code in raw.get("code", {}).items():
                        if lang in LANGUAGES:
                            self.files[lang]["main"] = str(code)
                for lang, name in (raw.get("entry") or {}).items():
                    if lang in LANGUAGES and name in self.files[lang]:
                        self.entry[lang] = name
                for lang in LANGUAGES:
                    if self.entry[lang] not in self.files[lang]:
                        self.entry[lang] = next(iter(self.files[lang]))
                self.language = raw.get("language") if raw.get("language") in LANGUAGES else "original"
                self.warp = float(raw.get("warp", 1))
            except (OSError, ValueError, KeyError, TypeError):
                self.world = World()
        self._last_look = time.monotonic()
        return self.world

    def save(self) -> None:
        with self.lock:
            world = self._load()
            payload = {
                "world": world.to_json(), "files": self.files, "entry": self.entry,
                "language": self.language,
                "warp": self.warp,
            }
            path = save_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            os.replace(tmp, path)
            self._last_save = time.monotonic()

    def reset(self) -> None:
        self.stop_run(wait=True)
        with self.lock:
            self._load()
            self.world = World()
            self.output = []
            self.save()

    # ── Looking at the farm ─────────────────────────────────────────────

    def _catch_up(self) -> None:
        """No program running: the farm moves on by the real time since it was last seen."""
        now = time.monotonic()
        gap = min(IDLE_CATCH_UP, now - self._last_look)
        self._last_look = now
        if self.run is None or self.run.status not in ("starting", "running"):
            self._load().advance(gap)
            if now - self._last_save > 10:
                self.save()

    def state(self, since: int = 0) -> dict[str, Any]:
        with self.lock:
            world = self._load()
            self._catch_up()
            run = self.run
            farm = world.snapshot()
            items = world.items
            simulation = None
            sim = run.sim if run is not None else None
            if sim is not None and sim.world is not None:
                # While a simulation runs, the screen shows its farm, as the game does.
                farm = sim.world.snapshot()
                items = sim.world.items
                live = [d for d in sim.drones.values() if d.status == "running"]
                if live:
                    farm["drones"] = [{"x": d.x, "y": d.y, "hat": d.hat} for d in live]
                    first = sim.drones.get(0)
                    if first is not None:
                        farm["drone"] = {"x": first.x, "y": first.y, "hat": first.hat}
                simulation = {"file": sim.sim_file, "speedup": sim.sim_speedup}
            elif run is not None and run.status in ("starting", "running") and run.drones:
                live = [d for d in run.drones.values() if d.status == "running"] or list(run.drones.values())
                farm["drones"] = [{"x": d.x, "y": d.y, "hat": d.hat} for d in live]
                main = run.drones.get(0)
                if main is not None:
                    farm["drone"] = {"x": main.x, "y": main.y, "hat": main.hat}
            return {
                "farm": farm,
                "simulation": simulation,
                "items": {k: (int(v) if float(v).is_integer() else round(v, 2)) for k, v in items.items()},
                "run": None if run is None else {
                    "id": run.id, "language": run.language, "status": run.status,
                    "error": run.error, "line": run.error_line, "file": run.error_file,
                    "commands": run.commands,
                    "seconds": round(time.monotonic() - run.started, 1),
                    "drones": sum(1 for d in run.drones.values() if d.status == "running"),
                },
                "output": self.output[since:],
                "outputEnd": len(self.output),
                "warp": self.warp,
            }

    def overview(self) -> dict[str, Any]:
        """Everything the screen needs when it opens."""
        with self.lock:
            world = self._load()
            payload = self.state(len(self.output))
            payload.update({
                "code": self.code,
                "files": self.files,
                "entry": self.entry,
                "language": self.language,
                "warps": list(WARPS),
                "unlocks": self.unlock_list(),
                "features": sorted(world.unlocked_features()),
                "functions": self.function_list(),
                "names": {
                    "Directions": list(data.DIRECTIONS), "Entities": list(data.ENTITIES),
                    "Items": list(data.ITEMS), "Grounds": list(data.GROUNDS), "Hats": list(data.HATS),
                },
                "languages": [lang for lang in LANGUAGES if self.language_available(lang)],
            })
            return payload

    def unlock_list(self) -> list[dict[str, Any]]:
        world = self._load()
        out = []
        for name, u in data.UNLOCKS.items():
            cost = world.next_cost(name)
            out.append({
                "name": name,
                "level": world.level(name),
                "max": u.starts_at + len(u.costs),
                "cost": cost,
                "available": world.available(name),
                "affordable": bool(cost) and world.affordable(cost),
                "needs": list(u.needs),
                "about": u.about,
                "missing": u.missing,
                "upgradable": len(u.costs) > 1,
            })
        return out

    def function_list(self) -> list[dict[str, Any]]:
        world = self._load()
        return [
            {"py": f.py, "js": f.js, "dart": f.dart, "params": list(f.params), "doc": f.doc,
             "unlocked": world.has_function(f.py), "unlock": world.function_unlock(f.py)}
            for f in FUNCTIONS
        ]

    @staticmethod
    def language_available(language: str) -> bool:
        if language in ("original", "python"):
            return True
        if language == "javascript":
            return shutil.which("node") is not None
        if language == "dart":
            from code_coach.engine import dart_path

            return dart_path() is not None
        return False

    # ── Research, code, settings ────────────────────────────────────────

    def buy(self, name: str) -> bool:
        with self.lock:
            ok = self._load().buy(name)
            if ok:
                self.save()
            return ok

    @property
    def code(self) -> dict[str, str]:
        """Each language's file that Run runs."""
        return {lang: self.files[lang].get(self.entry[lang], "") for lang in LANGUAGES}

    def keep_code(self, language: str, code: str, file: str = "") -> None:
        if language not in LANGUAGES:
            return
        with self.lock:
            self._load()
            name = file or self.entry[language]
            if name not in self.files[language]:
                return
            self.files[language][name] = code
            self.language = language
            self.save()

    def file_op(self, language: str, action: str, name: str, new_name: str = "") -> dict[str, Any]:
        """Add, rename, delete or pick (to run) one of a language's files."""
        if language not in LANGUAGES:
            return {"ok": False, "error": f"{language} is not a farm language."}
        with self.lock:
            self._load()
            files = self.files[language]

            def bad_name(n: str) -> str:
                if not FILE_NAME.match(n):
                    return ("A file name is lowercase letters, digits and _, starting with a letter "
                            "or _, up to 24 characters - like utils or harvest_rows.")
                if n in RESERVED_FILES:
                    return f"{n} is a name the farm uses itself; pick another."
                return ""

            if action == "add":
                problem = bad_name(name) or (f"There is already a file called {name}." if name in files else "")
                if problem:
                    return {"ok": False, "error": problem}
                files[name] = STARTER_HELPER[language].format(name=name)
            elif action == "rename":
                problem = "" if name in files else f"There is no file called {name}."
                problem = problem or bad_name(new_name) or (
                    f"There is already a file called {new_name}." if new_name in files else "")
                if problem:
                    return {"ok": False, "error": problem}
                self.files[language] = {(new_name if k == name else k): v for k, v in files.items()}
                if self.entry[language] == name:
                    self.entry[language] = new_name
            elif action == "delete":
                if name not in files:
                    return {"ok": False, "error": f"There is no file called {name}."}
                if len(files) == 1:
                    return {"ok": False, "error": "A program needs at least one file."}
                del files[name]
                if self.entry[language] == name:
                    self.entry[language] = next(iter(files))
            elif action == "select":
                if name not in files:
                    return {"ok": False, "error": f"There is no file called {name}."}
                self.entry[language] = name
            else:
                return {"ok": False, "error": f"Unknown file action {action}."}
            self.language = language
            self.save()
            return {"ok": True}

    def set_warp(self, warp: float) -> None:
        with self.lock:
            self.warp = warp if warp in WARPS else 1
            if self.run:
                self.run.warp = self.warp

    # ── Running ─────────────────────────────────────────────────────────
    #
    # A run is one or more drones. Each is its own process of the player's
    # program - the first runs it from the top, the rest (Megafarm) in
    # drone mode, running just the function they were spawned with - and
    # each has a thread here answering its commands.
    #
    # Each drone keeps its own clock of game time. A command waits for its
    # turn: no drone that might act EARLIER (a lower clock) may still be
    # busy or queued. So two drones harvesting side by side each take half
    # a second of game time - in parallel, as in the game - and the farm's
    # time is the furthest any of them has got.

    def start(self, language: str, code: str, file: str = "") -> dict[str, Any]:
        """Check the program - every file of it - against what is unlocked, then run it.

        `code` is the latest text of `file` (the entry, the one Run runs);
        the other files run as they were last kept.
        """
        if language not in LANGUAGES or not self.language_available(language):
            return {"ok": False, "error": f"{language} is not available on this machine."}
        self.stop_run(wait=True)
        with self.lock:
            world = self._load()
            entry = file or self.entry[language]
            if entry not in self.files[language]:
                return {"ok": False, "error": f"There is no file called {entry}."}
            self.files[language][entry] = code
            self.entry[language] = entry
            self.language = language
            from code_coach.farm import gate

            unlocked = world.unlocked_features()
            violations = []
            for name, text in self.files[language].items():
                # The game's language is Python's syntax: the same gate holds it.
                for p in gate.check(text, "python" if language == "original" else language, unlocked):
                    violations.append({"feature": p.feature, "line": p.line, "snippet": p.snippet,
                                       "message": p.message, "file": name})
            if violations:
                return {"ok": False, "violations": violations}
            from code_coach.farm.stubs.render import prepare

            try:
                files, argv, _player_files = prepare(language, dict(self.files[language]), entry)
            except (RuntimeError, ValueError) as exc:
                return {"ok": False, "error": str(exc)}
            workdir = tempfile.mkdtemp(prefix="farm-")
            for name, text in files.items():
                target = Path(workdir, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", NO_COLOR="1")
            ts = TYPESCRIPT
            if ts.exists():
                env["FARM_TS"] = str(ts)
            env.pop("FARM_DRONE", None)
            run = Run(id=self._next_run, language=language, warp=self.warp, workdir=workdir,
                      argv=list(argv), env=env, time0=world.time,
                      files=dict(self.files[language]), entry=entry)
            self._next_run += 1
            main = Drone(id=0, time=world.time, x=world.x, y=world.y, hat=world.hat)
            try:
                main.proc = self._launch(run, None)
            except OSError as exc:
                shutil.rmtree(workdir, ignore_errors=True)
                return {"ok": False, "error": f"Could not start {language}: {exc}"}
            run.drones[0] = main
            run.status = "running"
            self.run = run
            name = {"javascript": "JavaScript"}.get(language, language.capitalize())
            self._say("info", f"Running your {name} program.")
            self.save()
        threading.Thread(target=self._drive, args=(run, main), daemon=True).start()
        threading.Thread(target=self._watch, args=(run,), daemon=True).start()
        return {"ok": True, "run": run.id}

    @staticmethod
    def _launch(run: "Run", drone_job: dict[str, Any] | None) -> subprocess.Popen:
        env = dict(run.env)
        if drone_job is not None:
            env["FARM_DRONE"] = json.dumps(drone_job)
        return subprocess.Popen(
            run.argv, cwd=run.workdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env,
        )

    def stop_run(self, wait: bool = False) -> None:
        run = self.run
        if run is None or run.status not in ("starting", "running"):
            return
        runs = [run]
        while runs[-1].sim is not None:
            runs.append(runs[-1].sim)
        for r in runs:
            r.stop = True
        with self.turns:
            self.turns.notify_all()

        def kill() -> None:
            time.sleep(0.5)
            for r in runs:
                for d in list(r.drones.values()):
                    if d.proc and d.proc.poll() is None:
                        _kill_tree(d.proc)

        threading.Thread(target=kill, daemon=True).start()
        if wait:
            deadline = time.monotonic() + 4
            while run.status in ("starting", "running") and time.monotonic() < deadline:
                time.sleep(0.02)

    def _say(self, kind: str, text: str) -> None:
        self.output.append({"kind": kind, "text": text})
        if len(self.output) > 2000:
            del self.output[:500]

    def _fail(self, run: "Run", drone: "Drone", message: str, line: int = 0, file: str = "") -> None:
        """One drone's error ends the whole run, as in the game."""
        if not run.error:
            run.error = message if drone.id == 0 else f"Drone {drone.id}: {message}"
            run.error_line = line
            run.error_file = file
        run.stop = True
        with self.turns:
            self.turns.notify_all()

    def _watch(self, run: "Run") -> None:
        """Stop a program that has gone quiet - an empty loop never ends on its own."""
        while run.status in ("starting", "running"):
            time.sleep(0.25)
            now = time.monotonic()
            for d in list(run.drones.values()):
                if d.status != "running" or d.pending or d.blocked or not d.proc or d.proc.poll() is not None:
                    continue
                limit = FIRST_COMMAND_GRACE if d.commands == 0 else SILENT_LIMIT
                if now - d.last_command > limit:
                    who = "Your program" if d.id == 0 else f"Drone {d.id}"
                    self._fail(run, d,
                               f"{who} ran for {int(limit)} seconds without giving the drone a single "
                               "command, so it was stopped. Is there a loop with no drone command inside it?")
                    _kill_tree(d.proc)
                    return

    def _drive(self, run: "Run", drone: "Drone") -> None:
        proc = drone.proc
        assert proc is not None and proc.stdout is not None and proc.stdin is not None
        try:
            for raw in iter(proc.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                try:
                    request = decode_request(line)
                except ValueError:
                    request = None
                if request is None:
                    with self.lock:
                        self._say("out", _prefix(run) + line)
                    continue
                name, args = request
                # The game's language sends the ticks its own operations took.
                spent = 0
                if '"t"' in line:
                    try:
                        spent = max(0, int(json.loads(line[len(MARK):]).get("t", 0) or 0))
                    except (ValueError, TypeError):
                        spent = 0
                drone.commands += 1
                run.commands += 1
                drone.last_command = time.monotonic()
                if name == "__error__":
                    line_no = int(args[1]) if len(args) > 1 and isinstance(args[1], int) else 0
                    where = str(args[2]) if len(args) > 2 and args[2] else ""
                    self._fail(run, drone, str(args[0]) if args else "Your program stopped with an error.",
                               line_no, where)
                    continue
                if name == "__return__":
                    drone.result = args[0] if args else None
                    continue
                if run.stop:
                    self._reply(proc, STOP)
                    break
                reply = self._command(run, drone, name, args, spent)
                # Pace this drone to its game time, sped up by the warp.
                warp = run.warp
                if warp and not run.stop:
                    target = run.clock_start + (drone.time - run.time0) / warp
                    while not run.stop:
                        ahead = target - time.monotonic()
                        if ahead <= 0.001:
                            break
                        time.sleep(min(ahead, 0.05))
                    if drone.id == 0 and time.monotonic() - target > 1.0:
                        # A slow moment (a busy machine) should not make the
                        # program rush to catch up afterwards.
                        run.clock_start = time.monotonic() - (drone.time - run.time0) / warp
                if run.stop:
                    self._reply(proc, STOP)
                    break
                self._reply(proc, reply)
        except (OSError, ValueError):
            pass
        finally:
            self._drone_ended(run, drone)

    def _my_turn(self, run: "Run", drone: "Drone") -> bool:
        """No other drone could still act before this one."""
        if run.sim is not None:
            # The whole farm waits while one of its drones runs a simulation.
            return False
        for d in run.drones.values():
            if d is drone or d.status != "running" or d.blocked:
                continue
            if d.pending:
                if (d.time, d.id) < (drone.time, drone.id):
                    return False
            elif d.time <= drone.time:
                return False
        return True

    def _command(self, run: "Run", drone: "Drone", name: str, args: list[Any], spent: int = 0) -> str:
        """Do one command for one drone, in its turn. Returns the reply line."""
        with self.turns:
            drone.pending = True
            while not run.stop and not self._my_turn(run, drone):
                self.turns.wait(0.05)
            drone.pending = False
            if run.stop:
                self.turns.notify_all()
                return STOP
            world = self._world_of(run)
            if name == "wait_for":
                return self._wait_for(run, drone, args, world)
            world.x, world.y, world.hat = drone.x, drone.y, drone.hat
            world.clock = drone.time
            world.run_ticks = drone.ticks
            if spent:
                world.spend_ticks(spent)
            try:
                if name == "__ticks__":
                    result = None
                elif name == "simulate":
                    result = self._simulate(run, drone, args, world)
                elif name in ("spawn_drone", "num_drones", "max_drones", "has_finished"):
                    result, _seconds = self._drone_command(run, drone, name, args, world)
                else:
                    if name == "change_hat" and args and args[0] == "Hats.Dinosaur_Hat" and any(
                        d is not drone and d.status == "running" and d.hat == "Dinosaur_Hat"
                        for d in run.drones.values()
                    ):
                        raise Refusal("There is only one dinosaur hat, and another drone is wearing it.")
                    result, _seconds = world.call(name, args, run.language)
                reply = answer(result)
            except Refusal as exc:
                reply = refuse(str(exc))
            except _Stopped:
                reply = STOP
            except Exception as exc:  # noqa: BLE001 - a farm bug must not hang the program
                reply = refuse(f"The farm could not do that: {exc}")
            drone.x, drone.y, drone.hat = world.x, world.y, world.hat
            drone.time = world.clock if world.clock is not None else drone.time
            drone.ticks = world.run_ticks
            world.clock = None
            if drone.id == 0:
                pass
            else:
                # The farm's own drone fields belong to the first drone between commands.
                main = run.drones.get(0)
                if main is not None:
                    world.x, world.y, world.hat = main.x, main.y, main.hat
            if name in ("print", "quick_print") and not reply.startswith('{"e"'):
                self._say("print" if name == "print" else "out", _prefix(run) + (str(args[0]) if args else ""))
            self._last_look = time.monotonic()
            if time.monotonic() - self._last_save > 10:
                self.save()
            self.turns.notify_all()
            return reply

    def _world_of(self, run: "Run") -> World:
        return run.world if run.world is not None else self._load()

    def _argv_for(self, run: "Run", file: str) -> list[str]:
        """The command that runs another of the program's files from the top."""
        argv = list(run.argv)
        if run.language == "dart":
            # Dart's runner names the file it runs, so a simulation gets one of its own.
            from code_coach.farm.stubs.render import dart_runner

            name = f"runner_sim_{file}.dart"
            Path(run.workdir, name).write_text(dart_runner(run.files, file), encoding="utf-8")
            return [argv[0], "run", name]
        argv[-1] = file
        return argv

    def _simulate(self, run: "Run", drone: "Drone", args: list[Any], world: World) -> float:
        """simulate(): run one of the program's files on a World of its own, and wait.

        Called holding the turn lock, in the caller's turn. The caller spends
        an action's time; every drone of the calling run waits (see _my_turn);
        the real farm stands still. The answer is the game seconds the
        simulated program took - the only thing that comes back out of it."""
        world.require("simulate", run.language)
        setup = World.simulation_setup(args, run.language)
        if run.parent is not None:
            raise Refusal("A simulation can't start another simulation.")
        if setup["file"] not in run.files:
            raise Refusal(f"There is no file called {setup['file']} to simulate.")
        world.spend_ticks(data.ACTION_TICKS)
        env = dict(run.env)
        env["FARM_GLOBALS"] = json.dumps(setup["globals"])
        child = Run(
            id=self._next_run, language=run.language, warp=setup["speedup"], workdir=run.workdir,
            argv=self._argv_for(run, setup["file"]), env=env, files=run.files, entry=setup["file"],
            world=World.for_simulation(setup), parent=run, sim_file=setup["file"],
            sim_speedup=setup["speedup"], time0=0.0,
        )
        self._next_run += 1
        main = Drone(id=0, time=0.0)
        try:
            main.proc = self._launch(child, None)
        except OSError as exc:
            raise Refusal(f"Could not start the simulation: {exc}") from None
        child.drones[0] = main
        child.status = "running"
        run.sim = child
        drone.blocked = True
        speed = f"at {setup['speedup']:g}x" if setup["speedup"] else "as fast as it goes"
        self._say("info", f"Simulating {setup['file']} {speed}.")
        threading.Thread(target=self._drive, args=(child, main), daemon=True).start()
        threading.Thread(target=self._watch, args=(child,), daemon=True).start()
        self.turns.notify_all()
        try:
            while child.status in ("starting", "running") and not run.stop:
                self.turns.wait(0.05)
        finally:
            run.sim = None
            drone.blocked = False
            drone.last_command = time.monotonic()
        if run.stop:
            raise _Stopped()
        if child.status == "error":
            spot = f" ({child.error_file}, line {child.error_line})" if child.error_line else ""
            raise Refusal(f"The simulation of {setup['file']} stopped with an error: {child.error}{spot}")
        return round(child.world.time, 4)

    def _drone_command(self, run: "Run", drone: "Drone", name: str, args: list[Any],
                       world: World) -> tuple[Any, float]:
        world.require(name, run.language)
        live = [d for d in run.drones.values() if d.status == "running"]
        if name == "num_drones":
            return len(live), world.spend_ticks(data.QUESTION_TICKS)
        if name == "max_drones":
            return world.max_drones(), world.spend_ticks(data.QUESTION_TICKS)
        if name == "has_finished":
            target = run.drones.get(args[0] if args else -1)
            if target is None:
                raise Refusal(f"{spell_function('has_finished', run.language)} needs a drone handle "
                              f"from {spell_function('spawn_drone', run.language)}.")
            return target.status != "running", world.spend_ticks(data.QUESTION_TICKS)
        # spawn_drone
        fn = args[0] if args else None
        if not isinstance(fn, str) or not fn:
            raise Refusal(f"{spell_function('spawn_drone', run.language)} needs a function.")
        if len(live) >= world.max_drones():
            return None, world.spend_ticks(data.FAILED_TICKS)
        seconds = world.spend_ticks(data.ACTION_TICKS)
        job = {
            "fn": fn,
            "args": args[1] if len(args) > 1 and isinstance(args[1], list) else [],
            "globals": args[2] if len(args) > 2 and isinstance(args[2], dict) else {},
        }
        if len(json.dumps(job)) > DRONE_JOB_LIMIT:
            # The job travels in an environment variable, and Windows caps those.
            raise Refusal(
                "Your program's global variables are too big to copy to another drone. Keep "
                "the globals small, or pass the drone what it needs as arguments."
            )
        new = Drone(id=run.next_drone, time=world.clock if world.clock is not None else world.time,
                    x=world.x, y=world.y, hat="Straw_Hat")
        run.next_drone += 1
        try:
            new.proc = self._launch(run, job)
        except OSError as exc:
            raise Refusal(f"Could not start another drone: {exc}") from None
        run.drones[new.id] = new
        threading.Thread(target=self._drive, args=(run, new), daemon=True).start()
        return new.id, seconds

    def _wait_for(self, run: "Run", drone: "Drone", args: list[Any], world: World) -> str:
        """Called holding the turn lock: block this drone until another finishes."""
        try:
            world.require("wait_for", run.language)
        except Refusal as exc:
            self.turns.notify_all()
            return refuse(str(exc))
        target = run.drones.get(args[0] if args else -1)
        if target is None or target is drone:
            self.turns.notify_all()
            return refuse(f"{spell_function('wait_for', run.language)} needs another drone's handle "
                          f"from {spell_function('spawn_drone', run.language)}.")
        drone.blocked = True
        self.turns.notify_all()
        while target.status == "running" and not run.stop:
            self.turns.wait(0.05)
        drone.blocked = False
        if run.stop:
            self.turns.notify_all()
            return STOP
        # The waiting drone catches up to the moment the other one finished.
        drone.time = max(drone.time, target.time)
        world.x, world.y, world.hat = drone.x, drone.y, drone.hat
        world.clock = drone.time
        world.spend_ticks(data.QUESTION_TICKS)
        drone.time = world.clock
        world.clock = None
        self.turns.notify_all()
        return answer(target.result)

    @staticmethod
    def _reply(proc: subprocess.Popen, text: str) -> None:
        try:
            assert proc.stdin is not None
            proc.stdin.write((text + "\n").encode("utf-8"))
            proc.stdin.flush()
        except (OSError, ValueError):
            pass

    def _drone_ended(self, run: "Run", drone: "Drone") -> None:
        proc = drone.proc
        stderr = ""
        if proc is not None:
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                _kill_tree(proc)
                proc.wait()
            if proc.stderr is not None:
                try:
                    stderr = proc.stderr.read().decode("utf-8", errors="replace")
                except (OSError, ValueError):
                    stderr = ""
            if proc.returncode not in (0, None) and not run.stop and not run.error:
                message, line, where = _compile_error(stderr, run.language)
                self._fail(run, drone, message, line, where)
        with self.turns:
            drone.status = "done"
            self.turns.notify_all()
            last = all(d.status != "running" for d in run.drones.values())
        if run.stop:
            # Make sure the others go too.
            for d in list(run.drones.values()):
                if d.status == "running" and d.proc and d.proc.poll() is None:
                    threading.Thread(target=_kill_later, args=(d.proc,), daemon=True).start()
        if last:
            self._finish(run)

    def _finish(self, run: "Run") -> None:
        if run.parent is not None:
            self._finish_simulation(run)
            return
        with self.lock:
            if run.finished:
                return
            run.finished = True
            world = self._load()
            main = run.drones.get(0)
            if main is not None:
                world.x, world.y, world.hat = main.x, main.y, main.hat
            world.clock = None
            world.end_run()
            if run.stop and not run.error:
                run.status = "stopped"
                self._say("info", "Stopped.")
            elif run.error:
                run.status = "error"
                spot = []
                if run.error_file and len(self.files.get(run.language, {})) > 1:
                    spot.append(run.error_file)
                if run.error_line:
                    spot.append(f"line {run.error_line}")
                self._say("error", run.error + (f" ({', '.join(spot)})" if spot else ""))
            else:
                run.status = "done"
                self._say("info", "Your program finished.")
            self.save()
        shutil.rmtree(run.workdir, ignore_errors=True)

    def _finish_simulation(self, run: "Run") -> None:
        with self.turns:
            if run.finished:
                return
            run.finished = True
            if run.stop and not run.error:
                run.status = "stopped"
            elif run.error:
                run.status = "error"
            else:
                run.status = "done"
                assert run.world is not None
                self._say("info", f"The simulation of {run.sim_file} took {run.world.time:.2f} seconds.")
            self.turns.notify_all()


def _prefix(run: "Run") -> str:
    """Output from inside a simulation says so."""
    return "(simulation) " if run.parent is not None else ""


def _kill_later(proc: subprocess.Popen) -> None:
    time.sleep(0.5)
    if proc.poll() is None:
        _kill_tree(proc)


def _kill_tree(proc: subprocess.Popen) -> None:
    """Stop a program and anything it started.

    A launcher (a .bat shim, a venv's python.exe) can start the real
    process as a child; killing only the launcher leaves the program
    running with the pipe open, and the run would never end.
    """
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    if proc.poll() is None:
        proc.kill()


def _compile_error(stderr: str, language: str) -> tuple[str, int, str]:
    """A crash the program could not report itself: (message, line, file).

    Dart compile errors arrive this way, naming the player's file as
    name.dart:LINE:COL. The farm's own files (farm_api, runner) are never
    the player's fault, so a line in them is passed over.
    """
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return "Your program stopped with an error.", 0, ""
    own = ("farm_api", "runner")
    if language == "dart":
        for line in lines:
            m = re.search(r"(?:^|[/\\])([a-z_][a-z0-9_]*)\.dart:(\d+):\d+: (?:Error|Context): (.*)", line)
            if m and m.group(1) not in own:
                return m.group(3), int(m.group(2)), m.group(1)
        if "main" in stderr:
            return "A Dart program needs a main function: put your code inside void main() { ... }.", 0, ""
    for line in lines:
        m = re.search(r"(?:^|[/\\\s\"'])([a-z_][a-z0-9_]*)\.(?:py|js|mjs|cjs)\D+(\d+)", line)
        if m and m.group(1) not in own:
            return lines[-1], int(m.group(2)), m.group(1)
    return lines[-1][:300], 0, ""


HOST = FarmHost()


def describe(name: str, language: str) -> str:
    return spell_function(name, language)
