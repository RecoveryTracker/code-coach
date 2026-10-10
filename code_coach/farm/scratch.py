"""Running a program in The Farmer Was Replaced's own language on a farm that is not yours.

Free mode can hold a program written for the game (language id "tfwr").
Running it must not touch the real farm - the one you play on, kept in
farm_save.json - so a run here uses a FarmHost of its own that never reads or
writes the save, on a World built for the purpose:

- every unlock researched (each at its first level, so every function and
  every part of the language is there), Megafarm at three levels (eight
  drones) and Expand at its top, which is the biggest field the farm has;
- a million of every item, so planting and buying never run dry; the ground
  starts as grassland, as a new farm does, so till() works as it does there;
- a fixed seed, so the same program tells the same story twice.

Nothing paces the run to game time (warp 0, as fast as the machine goes), and
two caps stop a program that does not end: MAX_SECONDS of real time and
MAX_COMMANDS drone commands (every command, and the ticks sent on their own,
count). The program runs in the real interpreter (stubs/farm_lang.py), as a
real process, speaking the real line protocol - nothing is reimplemented here.

`run_program` returns a Scratch; `run_scratch` is the (stdout, stderr, code)
form that `engine.run_code` hands to the rest of the app.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from code_coach.farm import data
from code_coach.farm.runner import FarmHost, Run
from code_coach.farm.world import World

#: Real seconds a program may run before it is stopped.
MAX_SECONDS = 10.0
#: Drone commands (actions, questions, prints, tick reports) before it is stopped.
MAX_COMMANDS = 150_000
#: Lines of output kept; a program that prints more is cut off with a note.
MAX_OUTPUT_LINES = 2000
#: How many of each item the scratch farm starts with.
PLENTY = 1_000_000
#: How many Megafarm levels it has (2 ** levels drones).
MEGAFARM_LEVEL = 3
SEED = 2024
#: Items that turn up by themselves (supplies arrive every ten seconds), so
#: they are not something the program "harvested".
_SUPPLIES = ("Water", "Fertilizer")


def make_world() -> World:
    """A fresh farm with everything researched, the biggest field, and plenty."""
    world = World(SEED)
    for name, unlock in data.UNLOCKS.items():
        if unlock.missing:
            continue
        top = unlock.starts_at + len(unlock.costs)
        if name == "Expand":
            world.unlocks[name] = top
        elif name == "Megafarm":
            world.unlocks[name] = min(top, MEGAFARM_LEVEL)
        else:
            world.unlocks[name] = max(unlock.starts_at, 1)
    size = data.FARM_SIZES[min(world.level("Expand"), len(data.FARM_SIZES) - 1)]
    world.width, world.height = size
    world.shrunk = None
    world._fill()
    for item in data.ITEMS:
        world.items[item] = 0 if item == "Power" else PLENTY
    return world


class _ScratchHost(FarmHost):
    """A FarmHost that has one farm, made for the occasion, and keeps no save.

    The real FarmHost finds its World in farm_save.json (`_load`) and writes
    it back (`save`); both are replaced, so nothing here can read or write
    that file. Output is kept in full rather than in the host's 2000-line
    window, because the caller wants every line the program printed."""

    def __init__(self, world: World) -> None:
        super().__init__()
        self.world = world
        self.warp = 0  # unpaced
        self.lines: list[tuple[str, str]] = []
        self.cut = False

    def _load(self) -> World:
        assert self.world is not None
        return self.world

    def save(self) -> None:
        return None

    def _say(self, kind: str, text: str) -> None:
        if kind not in ("out", "print"):
            return
        if len(self.lines) >= MAX_OUTPUT_LINES:
            self.cut = True
            return
        self.lines.append((kind, text))


@dataclass
class Scratch:
    """What one run on the scratch farm did."""

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    #: Lines the program printed, in order.
    printed: list[str] = field(default_factory=list)
    #: "" when it ended by itself, else "time" or "commands" (stopped by a cap).
    stopped: str = ""
    #: The error, as the interpreter worded it, and its line (0 if unknown).
    error: str = ""
    error_line: int = 0
    ticks: int = 0
    commands: int = 0
    #: Game seconds the farm moved on, and the drone's square at the end.
    game_seconds: float = 0.0
    position: tuple[int, int] = (0, 0)
    size: tuple[int, int] = (1, 1)
    #: Net change in each item (positive or negative), nothing that did not move.
    changes: dict[str, int] = field(default_factory=dict)
    drones: int = 1
    real_seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.error and not self.stopped

    @property
    def gained(self) -> dict[str, int]:
        """What the program harvested: the items that went up, biggest first
        (supplies that arrive on their own are left out)."""
        up = {k: v for k, v in self.changes.items() if v > 0 and k not in _SUPPLIES}
        return dict(sorted(up.items(), key=lambda kv: (-kv[1], kv[0])))

    def as_tuple(self) -> tuple[str, str, int]:
        return self.stdout, self.stderr, self.exit_code


def item_phrase(items: dict[str, int], limit: int = 6) -> str:
    """{'Pumpkin': 12, 'Hay': 3} -> '12 pumpkin, 3 hay'."""
    shown = [f"{n} {name.replace('_', ' ').lower()}" for name, n in list(items.items())[:limit]]
    return ", ".join(shown)


def describe_error(message: str, line: int) -> str:
    """The error as stderr shows it: what went wrong, then where."""
    text = message.strip()
    if text.endswith(" isn't defined."):
        text = "NameError: " + text
    return f"{text} (line {line})" if line else text


def _wait(host: _ScratchHost, run: Run, seconds: float, commands: int) -> str:
    """Wait for the run to end, or stop it at a cap. Returns which cap, or ''."""
    start = time.monotonic()
    while run.status in ("starting", "running"):
        if time.monotonic() - start > seconds:
            host.stop_run(wait=True)
            return "time"
        if run.commands > commands:
            host.stop_run(wait=True)
            return "commands"
        time.sleep(0.01)
    return ""


def run_program(code: str, *, seconds: float | None = None, commands: int | None = None) -> Scratch:
    """Run `code` (the game's language) on a fresh scratch farm to the end, or to a cap."""
    seconds = MAX_SECONDS if seconds is None else seconds
    commands = MAX_COMMANDS if commands is None else commands
    began = time.monotonic()
    world = make_world()
    before = dict(world.items)
    host = _ScratchHost(world)
    out = Scratch(size=(world.w, world.h))

    started: dict[str, Any] = host.start("original", code, "main")
    if not started.get("ok"):
        # The gate or the launcher turned it away (everything is unlocked, so
        # it is the launcher: no Python to run the interpreter, say).
        out.error = str(started.get("error") or "The program could not be started.")
        out.exit_code = 1
        out.stderr = describe_error(out.error, 0)
        return out

    run = host.run
    assert run is not None
    cap = _wait(host, run, seconds, commands)
    # The run is over (done, error or stopped); wait for the last bookkeeping.
    deadline = time.monotonic() + 5
    while not run.finished and time.monotonic() < deadline:
        time.sleep(0.01)

    out.printed = [text for _kind, text in host.lines]
    if host.cut:
        out.printed.append(f"... (output cut off after {MAX_OUTPUT_LINES} lines)")
    out.stdout = "".join(line + "\n" for line in out.printed)
    out.commands = run.commands
    out.drones = len(run.drones)
    out.ticks = sum(d.ticks for d in run.drones.values())
    out.game_seconds = round(world.time, 2)
    out.position = (world.x, world.y)
    out.changes = {
        k: int(round(world.items[k] - before[k])) for k in data.ITEMS
        if int(round(world.items[k] - before[k])) != 0
    }
    out.real_seconds = round(time.monotonic() - began, 2)

    if cap:
        out.stopped = cap
        out.exit_code = 124
        if cap == "time":
            out.stderr = (
                f"Stopped after {seconds:g} seconds: the program was still running. "
                "Is there a `while True:` with nothing that ever ends it?"
            )
        else:
            out.stderr = (
                f"Stopped after {commands:,} drone commands: the program was still going. "
                "Is there a `while True:` with nothing that ever ends it?"
            )
    elif run.error:
        out.error = run.error
        out.error_line = run.error_line
        out.exit_code = 1
        out.stderr = describe_error(run.error, run.error_line)
    else:
        summary = _summary_line(out)
        if summary:
            out.stdout += summary + "\n"
    return out


def _summary_line(done: Scratch) -> str:
    """'-- done: 123 ticks, harvested 12 pumpkin, 3 hay --', or '' if nothing happened."""
    parts = []
    if done.ticks:
        parts.append(f"{done.ticks} tick{'' if done.ticks == 1 else 's'}")
    gained = done.gained
    if gained:
        parts.append("harvested " + item_phrase(gained))
    return f"-- done: {', '.join(parts)} --" if parts else ""


def run_scratch(code: str, timeout: float | None = None) -> tuple[str, str, int]:
    """(stdout, stderr, exit code), the shape engine.run_code returns."""
    return run_program(code, seconds=timeout).as_tuple()
