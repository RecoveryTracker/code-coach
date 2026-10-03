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
import shutil
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from code_coach.farm import data
from code_coach.farm.protocol import FUNCTIONS, STOP, answer, decode_request, refuse
from code_coach.farm.world import Refusal, World, spell_function

LANGUAGES = ("python", "javascript", "dart")
#: How far the farm may move on between two looks when nothing is running.
IDLE_CATCH_UP = 2.0
#: A program that sends no drone command for this long (real seconds) is
#: stuck in a loop with nothing in it; it is stopped and told so.
SILENT_LIMIT = 15.0
#: Dart compiles before it runs; its first command can take a while.
FIRST_COMMAND_GRACE = 30.0
#: Warps the screen offers; 0 means as fast as the machine goes.
WARPS = (1, 2, 4, 8, 16, 64, 0)

STARTER_CODE = {
    "python": "# Your first program: harvest the grass under the drone.\n"
              "# Run it a few times, collect hay, and buy Loops.\nharvest()\n",
    "javascript": "// Your first program: harvest the grass under the drone.\n"
                  "// Run it a few times, collect hay, and buy Loops.\nharvest();\n",
    "dart": "// Your first program: harvest the grass under the drone.\n"
            "// Run it a few times, collect hay, and buy Loops.\nvoid main() {\n  harvest();\n}\n",
}


def save_path() -> Path:
    from code_coach.progress.store import active_store

    return active_store().path.with_name("farm_save.json")


@dataclass
class Run:
    id: int
    language: str
    warp: float
    status: str = "starting"  # starting, running, done, stopped, error
    error: str = ""
    error_line: int = 0
    proc: subprocess.Popen | None = None
    stop: bool = False
    started: float = field(default_factory=time.monotonic)
    commands: int = 0
    last_command: float = field(default_factory=time.monotonic)
    workdir: str = ""


class FarmHost:
    """The one farm, its save, and the program running on it."""

    def __init__(self) -> None:
        self.lock = threading.RLock()
        self.world: World | None = None
        self.code: dict[str, str] = dict(STARTER_CODE)
        self.language = "python"
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
        self.code = dict(STARTER_CODE)
        self.output = []
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                self.world = World.from_json(raw.get("world", {}))
                self.code.update({k: v for k, v in raw.get("code", {}).items() if k in LANGUAGES})
                self.language = raw.get("language", "python") if raw.get("language") in LANGUAGES else "python"
                self.warp = float(raw.get("warp", 1))
            except (OSError, ValueError, KeyError, TypeError):
                self.world = World()
        self._last_look = time.monotonic()
        return self.world

    def save(self) -> None:
        with self.lock:
            world = self._load()
            payload = {
                "world": world.to_json(), "code": self.code, "language": self.language,
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
            return {
                "farm": world.snapshot(),
                "items": {k: (int(v) if float(v).is_integer() else round(v, 2)) for k, v in world.items.items()},
                "run": None if run is None else {
                    "id": run.id, "language": run.language, "status": run.status,
                    "error": run.error, "line": run.error_line, "commands": run.commands,
                    "seconds": round(time.monotonic() - run.started, 1),
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
        if language == "python":
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

    def keep_code(self, language: str, code: str) -> None:
        if language not in LANGUAGES:
            return
        with self.lock:
            self._load()
            self.code[language] = code
            self.language = language
            self.save()

    def set_warp(self, warp: float) -> None:
        with self.lock:
            self.warp = warp if warp in WARPS else 1
            if self.run:
                self.run.warp = self.warp

    # ── Running ─────────────────────────────────────────────────────────

    def start(self, language: str, code: str) -> dict[str, Any]:
        """Check the program against what is unlocked, then run it."""
        if language not in LANGUAGES or not self.language_available(language):
            return {"ok": False, "error": f"{language} is not available on this machine."}
        self.stop_run(wait=True)
        with self.lock:
            world = self._load()
            self.code[language] = code
            self.language = language
            from code_coach.farm import gate

            problems = gate.check(code, language, world.unlocked_features())
            if problems:
                return {
                    "ok": False,
                    "violations": [
                        {"feature": p.feature, "line": p.line, "snippet": p.snippet, "message": p.message}
                        for p in problems
                    ],
                }
            from code_coach.farm.stubs.render import prepare

            try:
                files, argv, _user_file = prepare(language, code)
            except (RuntimeError, ValueError) as exc:
                return {"ok": False, "error": str(exc)}
            workdir = tempfile.mkdtemp(prefix="farm-")
            for name, text in files.items():
                Path(workdir, name).write_text(text, encoding="utf-8")
            run = Run(id=self._next_run, language=language, warp=self.warp, workdir=workdir)
            self._next_run += 1
            world.run_ticks = 0
            env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", NO_COLOR="1")
            try:
                run.proc = subprocess.Popen(
                    argv, cwd=workdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, env=env,
                )
            except OSError as exc:
                shutil.rmtree(workdir, ignore_errors=True)
                return {"ok": False, "error": f"Could not start {language}: {exc}"}
            self.run = run
            self._say("info", f"Running your {language.capitalize() if language != 'javascript' else 'JavaScript'} program.")
            self.save()
        threading.Thread(target=self._drive, args=(run,), daemon=True).start()
        threading.Thread(target=self._watch, args=(run,), daemon=True).start()
        return {"ok": True, "run": run.id}

    def stop_run(self, wait: bool = False) -> None:
        run = self.run
        if run is None or run.status not in ("starting", "running"):
            return
        run.stop = True

        def kill() -> None:
            time.sleep(0.5)
            if run.proc and run.proc.poll() is None:
                _kill_tree(run.proc)

        threading.Thread(target=kill, daemon=True).start()
        if wait:
            deadline = time.monotonic() + 3
            while run.status in ("starting", "running") and time.monotonic() < deadline:
                time.sleep(0.02)

    def _say(self, kind: str, text: str) -> None:
        self.output.append({"kind": kind, "text": text})
        if len(self.output) > 2000:
            del self.output[:500]

    def _watch(self, run: Run) -> None:
        """Stop a program that has gone quiet - an empty loop never ends on its own."""
        while run.status in ("starting", "running"):
            time.sleep(0.25)
            limit = FIRST_COMMAND_GRACE if run.commands == 0 else SILENT_LIMIT
            if time.monotonic() - run.last_command > limit and run.proc and run.proc.poll() is None:
                run.error = (
                    f"Your program ran for {int(limit)} seconds without giving the drone a single "
                    "command, so it was stopped. Is there a loop with no drone command inside it?"
                )
                _kill_tree(run.proc)
                return

    def _drive(self, run: Run) -> None:
        proc = run.proc
        assert proc is not None and proc.stdout is not None and proc.stdin is not None
        clock_start = time.monotonic()
        game_seconds = 0.0
        run.status = "running"
        try:
            for raw in iter(proc.stdout.readline, b""):
                line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
                request = None
                try:
                    request = decode_request(line)
                except ValueError:
                    request = None
                if request is None:
                    with self.lock:
                        self._say("out", line)
                    continue
                name, args = request
                run.commands += 1
                run.last_command = time.monotonic()
                if name == "__error__":
                    run.error = str(args[0]) if args else "Your program stopped with an error."
                    run.error_line = int(args[1]) if len(args) > 1 and isinstance(args[1], int) else 0
                    continue
                if run.stop:
                    self._reply(proc, STOP)
                    break
                with self.lock:
                    world = self._load()
                    try:
                        result, seconds = world.call(name, args, run.language)
                        reply = answer(result)
                    except Refusal as exc:
                        result, seconds, reply = None, 0.0, refuse(str(exc))
                    except Exception as exc:  # noqa: BLE001 - a farm bug must not hang the program
                        result, seconds, reply = None, 0.0, refuse(f"The farm could not do that: {exc}")
                    if name in ("print", "quick_print") and not reply.startswith('{"e"'):
                        self._say("print" if name == "print" else "out", str(args[0]) if args else "")
                    self._last_look = time.monotonic()
                    if time.monotonic() - self._last_save > 10:
                        self.save()
                # Pace the program to game time, sped up by the warp.
                game_seconds += seconds
                warp = run.warp
                if warp:
                    target = clock_start + game_seconds / warp
                    while not run.stop:
                        ahead = target - time.monotonic()
                        if ahead <= 0.001:
                            break
                        time.sleep(min(ahead, 0.05))
                    if time.monotonic() - target > 1.0:
                        # A slow command (a big snapshot, a busy machine) should not make
                        # the program rush to catch up afterwards.
                        clock_start = time.monotonic() - game_seconds / warp
                if run.stop:
                    self._reply(proc, STOP)
                    break
                self._reply(proc, reply)
        except (OSError, ValueError):
            pass
        finally:
            self._finish(run)

    @staticmethod
    def _reply(proc: subprocess.Popen, text: str) -> None:
        try:
            assert proc.stdin is not None
            proc.stdin.write((text + "\n").encode("utf-8"))
            proc.stdin.flush()
        except (OSError, ValueError):
            pass

    def _finish(self, run: Run) -> None:
        proc = run.proc
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
        if not run.error and proc is not None and proc.returncode not in (0, None) and not run.stop:
            run.error, run.error_line = _compile_error(stderr, run.language)
        with self.lock:
            world = self._load()
            world.end_run()
            if run.stop and not run.error:
                run.status = "stopped"
                self._say("info", "Stopped.")
            elif run.error:
                run.status = "error"
                where = f" (line {run.error_line})" if run.error_line else ""
                self._say("error", run.error + where)
            else:
                run.status = "done"
                self._say("info", "Your program finished.")
            self.save()
        shutil.rmtree(run.workdir, ignore_errors=True)


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


def _compile_error(stderr: str, language: str) -> tuple[str, int]:
    """The first useful line of a crash the program could not report itself."""
    import re

    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return "Your program stopped with an error.", 0
    if language == "dart" and "runner.dart" in stderr and "main" in stderr and "farm.dart" not in stderr:
        return "A Dart program needs a main function: put your code inside void main() { ... }.", 0
    if language == "dart":
        for line in lines:
            m = re.search(r"farm\.dart:(\d+):\d+: (?:Error|Context): (.*)", line)
            if m:
                return m.group(2), int(m.group(1))
    for line in lines:
        m = re.search(r"farm\.(?:py|js)\D+(\d+)", line)
        if m:
            return lines[-1], int(m.group(1))
    return lines[-1][:300], 0


HOST = FarmHost()


def describe(name: str, language: str) -> str:
    return spell_function(name, language)
