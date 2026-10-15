"""Momentum's memory: `momentum.json`, beside the progress file.

One `Momentum` object is the whole feature. It owns a lock (two awards at once
must both land), reads the file, applies a rule from `rules.py`, writes the file
whole and moved into place. The clock and the random source are plain
attributes, so a test can hold both still.

The file::

    {"version": 1, "xp": 340, "best_streak": 9, "freezes": 1,   # last two: for people reading it
     "combo": {"count": 3, "last_at": 1768000000.0},
     "lifetime": {"kata": 12, ...},
     "baseline": null | {streak carried from days we no longer keep},
     "days": {"2026-10-15": {"xp": 120, "awards": 6, "kinds": {...}, "keys": ["kata:x"],
                              "quests": [...], "done": [...],
                              "chest": false, "chest_xp": 0, "chest_freeze": false}}}

The streak, the freezes in hand and the best streak are always worked out again
from the days (`rules.simulate`), never trusted from the file; the two copies in
the file are written for convenience only. About 400 days are kept; older ones
are folded into `baseline` first, and their `keys` (needed only for the
once-a-day rule) are dropped after three days.
"""

from __future__ import annotations

import json
import logging
import os
import random
import threading
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

from . import rules

log = logging.getLogger(__name__)

VERSION = 1
KEEP_DAYS = 400
KEEP_KEYS_DAYS = 3


class UnknownKind(ValueError):
    """The client named a kind of award the server has no price for."""


def save_path() -> Path:
    """Beside the progress file, as the farm and Brain Drills keep theirs."""
    from code_coach.progress.store import active_store

    return active_store().path.with_name("momentum.json")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    # The farm's writer: whole file to a temp name, then moved into place, waiting
    # out Windows' brief refusals (a scanner holding the file we just wrote).
    from code_coach.farm.runner import _write_json as write

    write(path, payload)


def _fresh() -> dict[str, Any]:
    return {"version": VERSION, "xp": 0, "best_streak": 0, "freezes": 0,
            "combo": {"count": 0, "last_at": None}, "lifetime": {}, "baseline": None, "days": {}}


def _int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def _iso(text: Any) -> date | None:
    try:
        return date.fromisoformat(str(text))
    except ValueError:
        return None


def _clean_day(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    kinds = raw.get("kinds") if isinstance(raw.get("kinds"), dict) else {}
    return {
        "xp": _int(raw.get("xp")),
        "awards": _int(raw.get("awards")),
        "kinds": {str(k): _int(v) for k, v in kinds.items() if _int(v)},
        "keys": [str(k) for k in raw.get("keys", []) if isinstance(k, str)]
        if isinstance(raw.get("keys"), list) else [],
        "quests": [str(q) for q in raw.get("quests", [])] if isinstance(raw.get("quests"), list) else [],
        "done": [str(q) for q in raw.get("done", [])] if isinstance(raw.get("done"), list) else [],
        "chest": bool(raw.get("chest")),
        "chest_xp": _int(raw.get("chest_xp")),
        "chest_freeze": bool(raw.get("chest_freeze")),
    }


def _clean(raw: Any) -> dict[str, Any] | None:
    """The file's contents made safe to use, or None when it is not a momentum file at all."""
    if not isinstance(raw, dict) or not isinstance(raw.get("days", {}), dict):
        return None
    state = _fresh()
    state["xp"] = _int(raw.get("xp"))
    state["best_streak"] = _int(raw.get("best_streak"))
    state["freezes"] = min(rules.MAX_FREEZES, _int(raw.get("freezes")))
    combo = raw.get("combo") if isinstance(raw.get("combo"), dict) else {}
    last = combo.get("last_at")
    state["combo"] = {"count": _int(combo.get("count")),
                      "last_at": float(last) if isinstance(last, (int, float)) else None}
    life = raw.get("lifetime") if isinstance(raw.get("lifetime"), dict) else {}
    state["lifetime"] = {str(k): _int(v) for k, v in life.items()}
    base = raw.get("baseline")
    if isinstance(base, dict) and _iso(base.get("through")):
        state["baseline"] = {
            "through": str(base["through"]), "streak": _int(base.get("streak")),
            "freezes": min(rules.MAX_FREEZES, _int(base.get("freezes"))),
            "gap": min(2, _int(base.get("gap"), 2)), "best": _int(base.get("best")),
        }
    for key, value in raw.get("days", {}).items():
        day = _clean_day(value)
        if day is not None and _iso(key):
            state["days"][str(key)] = day
    return state


def _carry(state: dict[str, Any]) -> rules.Carry:
    base = state.get("baseline")
    if not base:
        return rules.Carry()
    return rules.Carry(through=date.fromisoformat(base["through"]), streak=base["streak"],
                       freezes=base["freezes"], gap=base["gap"], best=base["best"])


def _counted(state: dict[str, Any]) -> list[date]:
    return [d for k, v in state["days"].items() if v["awards"] > 0 and (d := _iso(k))]


def _bonus(state: dict[str, Any]) -> dict[date, int]:
    return {d: 1 for k, v in state["days"].items() if v["chest_freeze"] and (d := _iso(k))}


def _new_day(today: date) -> dict[str, Any]:
    return {"xp": 0, "awards": 0, "kinds": {}, "keys": [], "quests": rules.pick_quests(today),
            "done": [], "chest": False, "chest_xp": 0, "chest_freeze": False}


class Momentum:
    """The cross-app XP, streak, quests and chest."""

    def __init__(self, path: Path | None = None, clock: Callable[[], float] = time.time,
                 rng: Any = None) -> None:
        self._path = path
        self.clock = clock
        self.rng = rng if rng is not None else random.Random()
        self._lock = threading.RLock()

    # ── the file ────────────────────────────────────────────────────────

    @property
    def path(self) -> Path:
        return self._path if self._path is not None else save_path()

    def _load(self) -> dict[str, Any]:
        path = self.path
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return _fresh()
        except OSError as exc:
            log.warning("momentum: cannot read %s: %s", path, exc)
            return _fresh()
        try:
            state = _clean(json.loads(text))
        except ValueError:
            state = None
        if state is not None:
            return state
        # Keep what was there: it is the user's, however broken. One .bad is kept.
        bad = path.with_name(path.name + ".bad")
        try:
            os.replace(path, bad)
            log.warning("momentum: %s was not readable; kept as %s and started fresh", path, bad)
        except OSError as exc:
            log.warning("momentum: %s was not readable and could not be set aside: %s", path, exc)
        return _fresh()

    def _save(self, state: dict[str, Any], today: date) -> None:
        self._prune(state, today)
        s = rules.simulate(_counted(state), today, _carry(state), _bonus(state))
        state["best_streak"] = max(state["best_streak"], s.best)
        state["freezes"] = s.freezes
        _write_json(self.path, state)

    def _prune(self, state: dict[str, Any], today: date) -> None:
        cutoff = today - timedelta(days=KEEP_DAYS)
        old = [k for k in state["days"] if (d := _iso(k)) is not None and d < cutoff]
        if old:
            last_old = max(date.fromisoformat(k) for k in old)
            carry = rules.fold(_counted(state), _carry(state), _bonus(state), last_old)
            state["baseline"] = {"through": carry.through.isoformat(), "streak": carry.streak,
                                 "freezes": carry.freezes, "gap": carry.gap, "best": carry.best}
            state["best_streak"] = max(state["best_streak"], carry.best)
            for k in old:
                del state["days"][k]
        keep_keys = today - timedelta(days=KEEP_KEYS_DAYS)
        for k, v in state["days"].items():
            if v["keys"] and (_iso(k) or today) < keep_keys:
                v["keys"] = []

    # ── what a response says ────────────────────────────────────────────

    def _today(self) -> date:
        return datetime.fromtimestamp(self.clock()).date()

    def _stats(self, state: dict[str, Any], today: date) -> rules.DayStats:
        day = state["days"].get(today.isoformat())
        if not day:
            return rules.DayStats()
        before: set[str] = set()
        for back in range(1, 7):
            earlier = state["days"].get((today - timedelta(days=back)).isoformat())
            if earlier:
                before.update(k for k, n in earlier["kinds"].items() if n)
        fresh = frozenset(k for k, n in day["kinds"].items() if n and k not in before)
        return rules.DayStats(xp=day["xp"], awards=day["awards"], kinds=dict(day["kinds"]),
                              fresh_kinds=fresh)

    def _quests(self, state: dict[str, Any], today: date) -> list[dict[str, Any]]:
        day = state["days"].get(today.isoformat())
        ids = day["quests"] if day and day["quests"] else rules.pick_quests(today)
        return rules.quest_progress(ids, self._stats(state, today))

    def _view(self, state: dict[str, Any], today: date, streak: rules.Streak | None = None) -> dict[str, Any]:
        streak = streak or rules.simulate(_counted(state), today, _carry(state), _bonus(state))
        day = state["days"].get(today.isoformat())
        quests = self._quests(state, today)
        for q in quests:
            q["just_done"] = False
        all_done = bool(quests) and all(q["done"] for q in quests)
        claimed = bool(day and day["chest"])
        last14 = []
        for back in range(13, -1, -1):
            d = today - timedelta(days=back)
            rec = state["days"].get(d.isoformat())
            last14.append({"day": d.isoformat(), "xp": rec["xp"] if rec else 0})
        return {
            "ok": True,
            "xp_total": state["xp"],
            **rules.level_info(state["xp"]),
            "streak": streak.streak,
            "today_counted": streak.today_counted,
            "best_streak": max(state["best_streak"], streak.best),
            "freezes": streak.freezes,
            "quests": quests,
            "chest_ready": all_done and not claimed,
            "chest_claimed": claimed,
            "today_xp": day["xp"] if day else 0,
            "days_last_14": last14,
        }

    # ── the three things the screens ask ────────────────────────────────

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return self._view(self._load(), self._today())

    def award(self, kind: str, key: str) -> dict[str, Any]:
        """Pay out one success. Raises `UnknownKind` for a kind not in the table; nothing else."""
        if kind not in rules.XP:
            raise UnknownKind(kind)
        key = rules.clean_key(key)
        try:
            with self._lock:
                return self._award(kind, key)
        except Exception:  # a storage problem must never reach the screen it came from
            log.exception("momentum: award %s failed", kind)
            return {"ok": False}

    def _award(self, kind: str, key: str) -> dict[str, Any]:
        state = self._load()
        now = self.clock()
        today = self._today()
        iso = today.isoformat()
        day = state["days"].get(iso)
        if day is None:
            day = state["days"][iso] = _new_day(today)
        elif not day["quests"]:
            day["quests"] = rules.pick_quests(today)

        before = rules.simulate(_counted(state), today, _carry(state), _bonus(state))
        token = f"{kind}:{key}"
        if token in day["keys"]:
            out = self._view(state, today, before)
            return {**out, "repeat": True, "base": 0, "combo": state["combo"]["count"],
                    "combo_mult": rules.combo_multiplier(state["combo"]["count"]),
                    "lucky": None, "gained": 0, "level_up": None,
                    "streak_extended": False, "freeze_used": None, "freeze_earned": False}

        level_before = rules.level_for(state["xp"])
        combo = rules.next_combo(state["combo"]["count"], state["combo"]["last_at"], now)
        mult = rules.combo_multiplier(combo)
        base = rules.XP[kind]
        lucky = rules.roll_lucky(self.rng)
        gained = rules.payout(base, mult, lucky)

        state["combo"] = {"count": combo, "last_at": now}
        state["xp"] += gained
        state["lifetime"][kind] = state["lifetime"].get(kind, 0) + 1
        day["xp"] += gained
        day["awards"] += 1
        day["kinds"][kind] = day["kinds"].get(kind, 0) + 1
        day["keys"].append(token)

        after = rules.simulate(_counted(state), today, _carry(state), _bonus(state))
        newly_used = [d for d in after.used if d not in before.used]
        out = self._view(state, today, after)

        # A quest announces itself once: the first award that completes it.
        stored = set(day["done"])
        for q in out["quests"]:
            if q["done"] and q["id"] not in stored:
                q["just_done"] = True
                day["done"].append(q["id"])

        level_after = out["level"]
        self._save(state, today)
        return {
            **out,
            "repeat": False, "base": base, "combo": combo, "combo_mult": mult,
            "lucky": lucky, "gained": gained,
            "level_up": {"level": level_after, "title": out["title"]} if level_after > level_before else None,
            "streak_extended": after.today_counted and not before.today_counted,
            "freeze_used": newly_used[-1].isoformat() if newly_used else None,
            "freeze_earned": today in after.earned and today not in before.earned,
        }

    def claim_chest(self) -> dict[str, Any]:
        """Open today's chest: once a day, and only when all three quests are done."""
        try:
            with self._lock:
                return self._claim()
        except Exception:
            log.exception("momentum: chest failed")
            return {"ok": False, "gained": 0, "freeze_earned": False}

    def _claim(self) -> dict[str, Any]:
        state = self._load()
        today = self._today()
        day = state["days"].get(today.isoformat())
        view = self._view(state, today)
        no = {"gained": 0, "freeze_earned": False, "level_up": None}
        if day is None or not view["chest_ready"]:
            return {**view, **no, "ok": False,
                    "reason": "already_claimed" if view["chest_claimed"] else "not_ready"}
        level_before = rules.level_for(state["xp"])
        streak = rules.simulate(_counted(state), today, _carry(state), _bonus(state))
        xp, freeze = rules.roll_chest(self.rng, can_freeze=streak.freezes < rules.MAX_FREEZES)
        day["chest"] = True
        day["chest_xp"] = xp
        day["chest_freeze"] = freeze
        day["xp"] += xp
        state["xp"] += xp
        self._save(state, today)
        out = self._view(state, today)
        return {**out, "gained": xp, "freeze_earned": freeze,
                "level_up": ({"level": out["level"], "title": out["title"]}
                             if out["level"] > level_before else None)}
