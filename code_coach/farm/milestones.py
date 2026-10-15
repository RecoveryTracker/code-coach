"""The Farm's milestones and its welcome-back: what the farm tells Momentum.

The farm's world is authoritative: a program runs far faster than the screen polls,
and the browser is not to be trusted with "I harvested a pumpkin". So the host watches
the World itself (`World.listener`), and when one of the firsts below happens it pays
through the Momentum engine, in process. Every payout goes through `Momentum.award_server`
- the normal machinery: combo, the odd lucky bonus, levels, quests - and the answer is
queued here until the screen next reads the farm (`FarmRewards.drain`, which `FarmHost.state`
puts in its answer as `momentum`, a list, oldest first).

**A milestone pays once ever.** Its key is `<language>:<id>` and the kind
(`farm_milestone`) is a lifetime kind, so the dedupe is the engine's `once` set, not the
day's keys: another day, a restart, a Start over or a second program never pays it again.
Each language has its own farm, so each pays its own firsts.

**To add one**: add a row to `MILESTONES` (a unique id, a label that reads after "Farm: ",
an XP price and what triggers it). A new *kind* of trigger needs a few lines in
`FarmRewards`; a new crop needs nothing if it is in `data.PLANTS`.

Nothing here may break the farm: every method of `FarmRewards` that the host calls
swallows what the engine raises.

Not tracked: "a program ran clean after an earlier error", and sizes or totals the farm
had already reached before this existed (a milestone is something that happens, not
something that was true).
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

from code_coach.farm import data

log = logging.getLogger(__name__)

LANGUAGE_NAMES = {"original": "Original", "python": "Python", "javascript": "JavaScript", "dart": "Dart"}

#: The items a plant gives: what "items harvested" counts for the lifetime totals.
MAIN_ITEMS = tuple(sorted({p.item for p in data.PLANTS.values()}))


@dataclass(frozen=True)
class Milestone:
    id: str
    #: Reads after "Farm: " in the toast ("first pumpkin" -> "Farm: first pumpkin! (Python)").
    label: str
    xp: int
    #: What triggers it: "harvest" (arg: the plant harvested), "giant", "patch", "treasure",
    #: "drone", "grow" (arg: the Expand level reached) or "total" (arg: items harvested).
    trigger: str
    arg: str | int = ""


def _harvest(entity: str, label: str, xp: int) -> Milestone:
    return Milestone(f"harvest_{entity.lower()}", label, xp, "harvest", entity)


def _grow(level: int) -> Milestone:
    w, h = data.FARM_SIZES[level]
    return Milestone(f"grow_{w}x{h}", f"expanded to {w}x{h}", 10 + 5 * level, "grow", level)


#: The whole table. XP is the base, before the combo and any luck; a first harvest is
#: worth a little, a hard first (a giant pumpkin, a maze) more, and a size step a little
#: more each time.
MILESTONES: tuple[Milestone, ...] = (
    _harvest("Grass", "first hay", 10),
    _harvest("Bush", "first bush", 10),
    _harvest("Tree", "first tree", 15),
    _harvest("Carrot", "first carrot", 15),
    _harvest("Pumpkin", "first pumpkin", 20),
    _harvest("Sunflower", "first sunflower", 20),
    _harvest("Cactus", "first cactus", 20),
    Milestone("giant_pumpkin", "first giant pumpkin", 30, "giant"),
    Milestone("sorted_cactus", "first sorted cactus patch", 30, "patch"),
    Milestone("maze_treasure", "first maze treasure", 40, "treasure"),
    Milestone("first_drone", "first drone spawned", 30, "drone"),
    *(_grow(level) for level in range(1, len(data.FARM_SIZES))),
    Milestone("total_100", "100 items harvested", 15, "total", 100),
    Milestone("total_1000", "1,000 items harvested", 30, "total", 1000),
    Milestone("total_10000", "10,000 items harvested", 60, "total", 10000),
)

BY_ID = {m.id: m for m in MILESTONES}
#: The plant a "harvest" milestone is for, to the milestone.
FIRST_HARVEST = {str(m.arg): m for m in MILESTONES if m.trigger == "harvest"}
GROWTH = {int(m.arg): m for m in MILESTONES if m.trigger == "grow"}
TOTALS = tuple(sorted((m for m in MILESTONES if m.trigger == "total"), key=lambda m: int(m.arg)))


def key_for(language: str, milestone: Milestone) -> str:
    return f"{language}:{milestone.id}"


def label_for(language: str, milestone: Milestone) -> str:
    return f"Farm: {milestone.label}! ({LANGUAGE_NAMES.get(language, language)})"


class FarmRewards:
    """What one FarmHost tells Momentum, and the answers waiting for the screen."""

    #: Harvested items are added to the engine at most this often (real seconds), and when a run ends.
    FLUSH_SECONDS = 2.0
    #: The Farm counts as "seen" at most this often (real seconds) while it is polled.
    TOUCH_SECONDS = 30.0
    #: Answers kept for the screen; a farm run with the screen closed could earn many.
    QUEUE_CAP = 60

    def __init__(self, engine: Any = None) -> None:
        #: None means the app's own Momentum (looked up each time, so a moved store is followed).
        self.engine = engine
        self.queue: list[dict[str, Any]] = []
        self._lock = threading.RLock()
        #: Keys known to be paid already: a harvest after the first costs a set lookup, no file.
        self._paid: set[str] = set()
        self._paid_for: Any = None
        self._pending: dict[str, list[int]] = {}
        self._flushed = time.monotonic()
        self._touched = 0.0

    # ── the engine ──────────────────────────────────────────────────────

    def _engine(self) -> Any:
        if self.engine is not None:
            return self.engine
        from code_coach import momentum

        return momentum.MOMENTUM

    def _known(self, engine: Any) -> set[str]:
        """The paid-keys cache, dropped whenever the engine's file is a different one."""
        where = (id(engine), str(getattr(engine, "path", "")))
        if self._paid_for != where:
            self._paid, self._paid_for = set(), where
        return self._paid

    def _enqueue(self, answer: dict[str, Any]) -> None:
        self.queue.append(answer)
        if len(self.queue) > self.QUEUE_CAP:
            del self.queue[: len(self.queue) - self.QUEUE_CAP]

    def drain(self) -> list[dict[str, Any]]:
        """Everything paid since the screen last asked, oldest first (and forgets it)."""
        with self._lock:
            out, self.queue = self.queue, []
            return out

    # ── paying ──────────────────────────────────────────────────────────

    def _pay(self, language: str, milestone: Milestone) -> None:
        engine = self._engine()
        key = key_for(language, milestone)
        with self._lock:
            if key in self._known(engine):
                return
        answer = engine.award_server("farm_milestone", key, base=milestone.xp,
                                     label=label_for(language, milestone))
        if not answer.get("ok"):
            return  # the engine could not keep it; try again at the next chance
        with self._lock:
            self._known(engine).add(key)
            if not answer.get("repeat"):
                self._enqueue(answer)

    # ── what the host reports ───────────────────────────────────────────

    def event(self, language: str, world: Any, event: dict[str, Any]) -> None:
        """An action on a real farm. Only a harvest that paid something counts."""
        try:
            if event.get("k") != "harvest" or not event.get("ok"):
                return
            facts = world.facts
            entity = event.get("e")
            items = event.get("items") or {}
            earned = []
            first = FIRST_HARVEST.get(str(entity))
            if first is not None:
                earned.append(first)
            if entity == "Pumpkin" and int(facts.get("giant", 1)) > 1:
                earned.append(BY_ID["giant_pumpkin"])
            if entity == "Cactus" and int(facts.get("patch", 1)) > 1:
                earned.append(BY_ID["sorted_cactus"])
            if facts.get("treasure"):
                earned.append(BY_ID["maze_treasure"])
            for m in earned:
                self._pay(language, m)
            main = sum(int(v) for k, v in items.items() if k in MAIN_ITEMS)
            everything = sum(int(v) for v in items.values())
            with self._lock:
                counts = self._pending.setdefault(language, [0, 0])
                counts[0] += main
                counts[1] += everything
                due = time.monotonic() - self._flushed >= self.FLUSH_SECONDS
            if due:
                self.flush()
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: event failed")

    def bought(self, language: str, unlock: str, level: int) -> None:
        """Research bought on a real farm: an Expand is the farm growing."""
        try:
            if unlock == "Expand" and level in GROWTH:
                self._pay(language, GROWTH[level])
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: purchase failed")

    def drone_spawned(self, language: str) -> None:
        try:
            self._pay(language, BY_ID["first_drone"])
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: drone failed")

    def flush(self) -> None:
        """Hand the engine the items harvested since the last time: the lifetime total (and
        the steps it crossed) and today's `farm_items`, which the farm quest reads."""
        try:
            with self._lock:
                pending, self._pending = self._pending, {}
                self._flushed = time.monotonic()
            engine = self._engine()
            for language, (main, everything) in pending.items():
                got = engine.record_farm_items(language, main, everything)
                if not got.get("ok"):
                    continue
                if got.get("quest"):
                    with self._lock:
                        self._enqueue(got["quest"])
                for step in TOTALS:
                    if got["before"] < int(step.arg) <= got["after"]:
                        self._pay(language, step)
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: flush failed")

    def tick(self) -> None:
        """Called whenever the screen looks at the farm: bring the engine up to date, and note
        that the Farm is being watched (the welcome-back measures from the last look)."""
        try:
            with self._lock:
                due = bool(self._pending) and time.monotonic() - self._flushed >= self.FLUSH_SECONDS
                touch = time.monotonic() - self._touched >= self.TOUCH_SECONDS
                if touch:
                    self._touched = time.monotonic()
            if due:
                self.flush()
            if touch:
                self._engine().farm_touch()
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: tick failed")

    # ── the welcome-back ────────────────────────────────────────────────

    def visit(self, ripe: int) -> dict[str, Any] | None:
        """The Farm was opened: the card to show (or None). See `Momentum.farm_visit`."""
        try:
            with self._lock:
                self._touched = time.monotonic()
            return self._engine().farm_visit(ripe)
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: visit failed")
            return None

    def claim(self) -> dict[str, Any]:
        try:
            return self._engine().claim_welcome()
        except Exception:  # noqa: BLE001
            log.exception("farm rewards: welcome claim failed")
            return {"ok": False, "reason": "error"}
