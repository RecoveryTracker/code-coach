"""Momentum's rules: pure functions, no files and no clock.

Everything here takes its inputs as arguments (dates, a random source, a day's
records) so each rule can be tested on its own, against an independent model.
`engine.py` is the part that remembers things.

The numbers, in one place:

* XP per kind (`XP`) - the client sends a kind and a key, never an amount.
* Levels: the XP needed to *reach* level n is `LEVEL_STEP * n * (n - 1)`
  (100 for level 2, 300 for 3, 600 for 4, 1000 for 5 ...). Level n therefore
  spans `2 * LEVEL_STEP * n` XP, so each one is a little longer than the last
  and the first few come quickly.
* Combo: awards less than `COMBO_WINDOW` seconds apart build a combo. The
  multiplier is 1.0 for the first award, +0.1 for each one after it, capped
  at 2.0 (the eleventh in a row).
* Lucky: about one award in six rolls a bonus multiplier of 2 to 5.
* Streak: see `simulate`.
* Quests and the chest: see `pick_quests` and `roll_chest`.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable, Iterable, Mapping

# ── XP ──────────────────────────────────────────────────────────────────

#: What each kind of success is worth, before the combo and any luck.
#: Add a kind here and use `award("kind", key)` somewhere in web/src (or list it
#: in `UNUSED_KINDS` with a reason): tests/test_momentum.py checks both ways.
XP: dict[str, int] = {
    "workbook_page": 20,
    "kata": 25,
    "predict": 10,
    "trace": 10,
    "errors": 10,
    "bughunt": 25,
    "casefile": 40,
    "ticket": 40,
    "magnets": 15,
    "puzzle": 20,
    "regex": 15,
    "lesson": 20,
    "typing_run": 15,
    "concept": 10,
    "canvas_step": 30,
    "farm_buy": 15,
    "leetcode": 40,
    "drill": 5,
    "brain_item": 2,
    "brain_round": 30,
    "check_age": 50,
}

#: Kinds the server knows that no screen sends yet, and why. Empty is the goal.
UNUSED_KINDS: dict[str, str] = {}

#: Kinds only the server pays, from what it sees for itself (the Farm's world is
#: authoritative, so the Farm never asks the browser to say a milestone happened).
#: `POST /api/momentum/award` refuses them (400, like any kind not in `XP`); the
#: number here is the default base, and the caller may name another (a milestone
#: carries its own price, a welcome-back is worked out from what is ripe).
SERVER_XP: dict[str, int] = {
    "farm_milestone": 25,
    "farm_return": 15,
}

#: Kinds paid once ever per key, not once a day: a milestone is a first, and a
#: first happens once. Everything else keeps the once-a-day rule.
LIFETIME_KINDS = frozenset({"farm_milestone"})

#: Awards nobody did on purpose: they keep the combo and count for the streak, but
#: they are not "a thing solved" or "a mode used" for a quest.
PASSIVE_KINDS = frozenset(SERVER_XP)

#: The Farm's welcome-back: opening it after this many seconds away offers a small
#: payout, `WELCOME_BASE` plus one XP per ten ripe tiles, at most `WELCOME_BONUS_MAX` extra.
WELCOME_AWAY = 30 * 60
WELCOME_BASE = SERVER_XP["farm_return"]
WELCOME_PER = 10
WELCOME_BONUS_MAX = 10


def welcome_xp(ripe: int) -> int:
    """The base pay for a welcome-back with `ripe` tiles ripe: 15, +1 per 10 ripe, up to 25."""
    return WELCOME_BASE + min(WELCOME_BONUS_MAX, max(0, int(ripe)) // WELCOME_PER)


#: A one-key answer in Brain Drills pays two XP; it keeps the combo alive and
#: counts for the streak, but it is not "a thing solved" for a quest.
MICRO_KINDS = frozenset({"brain_item"})
FIX_KINDS = frozenset({"bughunt", "errors", "ticket"})

MAX_KEY = 200


def clean_key(key: object) -> str:
    """The key as stored: text, trimmed, and not enormous."""
    return str(key if key is not None else "").strip()[:MAX_KEY]


# ── Levels ──────────────────────────────────────────────────────────────

LEVEL_STEP = 50

#: One title per level, then round again (level 13 is "Beginner II").
TITLES = (
    "Beginner", "Tinkerer", "Learner", "Student", "Apprentice", "Coder",
    "Practitioner", "Journeyman", "Specialist", "Expert", "Master", "Grandmaster",
)


def xp_to_reach(level: int) -> int:
    """Total XP at which `level` begins. Level 1 begins at 0."""
    n = max(1, int(level))
    return LEVEL_STEP * n * (n - 1)


def level_for(xp: int) -> int:
    """The level a total of `xp` is in: the largest n with `xp_to_reach(n) <= xp`."""
    m = max(0, int(xp)) // LEVEL_STEP  # n(n-1) is a whole number, so flooring is exact
    return (1 + math.isqrt(1 + 4 * m)) // 2


def _roman(n: int) -> str:
    out = ""
    for value, text in ((1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
                        (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                        (5, "V"), (4, "IV"), (1, "I")):
        while n >= value:
            out += text
            n -= value
    return out


def title_for(level: int) -> str:
    n = max(1, int(level)) - 1
    lap = n // len(TITLES)
    name = TITLES[n % len(TITLES)]
    return name if lap == 0 else f"{name} {_roman(lap + 1)}"


def level_info(xp: int) -> dict[str, Any]:
    """`level`, `title`, `xp_in_level` (progress into it) and `xp_for_next` (its length)."""
    xp = max(0, int(xp))
    n = level_for(xp)
    start = xp_to_reach(n)
    return {
        "level": n,
        "title": title_for(n),
        "xp_in_level": xp - start,
        "xp_for_next": xp_to_reach(n + 1) - start,
    }


# ── Combo and luck ──────────────────────────────────────────────────────

#: Awards closer together than this (seconds) keep a combo going.
COMBO_WINDOW = 600.0
COMBO_STEP = 0.1
COMBO_MAX = 2.0


def next_combo(count: int, last_at: float | None, now: float) -> int:
    """The combo count after an award at `now`, given the one before it."""
    if last_at is not None and 0 <= now - last_at < COMBO_WINDOW:
        return int(count) + 1
    return 1


def combo_multiplier(count: int) -> float:
    """x1.0 for one, 1.1 for two ... capped at x2.0 (11 or more)."""
    return min(COMBO_MAX, round(1.0 + COMBO_STEP * (max(1, int(count)) - 1), 2))


LUCKY_CHANCE = 1 / 6
LUCKY_VALUES = (2, 3, 4, 5)
LUCKY_WEIGHTS = (55, 25, 14, 6)


def roll_lucky(rng: Any) -> int | None:
    """Usually nothing; about one time in six a multiplier from 2 to 5 (2 most often).

    `rng` is anything with `random()` and `choices(population, weights)`: a
    `random.Random`, or a stub in a test.
    """
    if rng.random() >= LUCKY_CHANCE:
        return None
    return int(rng.choices(LUCKY_VALUES, weights=LUCKY_WEIGHTS)[0])


def payout(base: int, combo_mult: float, lucky: int | None) -> int:
    """XP gained: base x combo, rounded half up, then x the lucky multiplier.

    The multiplier is a whole number of tenths, so this is done in whole numbers
    (float 16.5 would round to even, and 15 x 1.1 should pay 17).
    """
    tenths = round(combo_mult * 10)
    gained = (base * tenths + 5) // 10
    return gained * lucky if lucky else gained


# ── Streak ──────────────────────────────────────────────────────────────

MAX_FREEZES = 2
FREEZE_EVERY = 7


@dataclass(frozen=True)
class Carry:
    """Where the streak stood the day before the first day we still keep.

    Days older than ~400 are dropped from the file; this is what they added up
    to, so a long streak does not shrink when its oldest days are forgotten.
    `gap` is how many days in a row were missed just before `through` (0, 1, or
    2 meaning two or more).
    """

    through: date | None = None
    streak: int = 0
    freezes: int = 0
    gap: int = 2
    best: int = 0


@dataclass(frozen=True)
class Streak:
    streak: int
    best: int
    freezes: int
    today_counted: bool
    #: Days a freeze covered (only once a later counted day made it matter).
    used: tuple[date, ...] = ()
    #: Days on which reaching a 7th streak day earned a freeze.
    earned: tuple[date, ...] = ()


def _run(counted: set[date], carry: Carry, bonus: Mapping[date, int],
         last: date) -> tuple[int, int, int, int, list[date], list[date]]:
    """Walk day by day from the carry to `last` inclusive, every day treated as over."""
    streak, freezes, gap, best = carry.streak, carry.freezes, carry.gap, carry.best
    used: list[date] = []
    earned: list[date] = []
    if carry.through is not None:
        d = carry.through + timedelta(days=1)
    elif counted:
        d = min(counted)
    else:
        return streak, freezes, gap, best, used, earned
    while d <= last:
        if d in counted:
            if streak == 0 or gap >= 2:
                streak = 1
            elif gap == 0:
                streak += 1
            elif freezes > 0:  # exactly one missed day, and a freeze to cover it
                freezes -= 1
                used.append(d - timedelta(days=1))
                streak += 1
            else:
                streak = 1
            gap = 0
            if streak % FREEZE_EVERY == 0 and freezes < MAX_FREEZES:
                freezes += 1
                earned.append(d)
            freezes = min(MAX_FREEZES, freezes + max(0, int(bonus.get(d, 0))))
            best = max(best, streak)
        else:
            gap = min(2, gap + 1)
            if gap >= 2:
                streak = 0
        d += timedelta(days=1)
    return streak, freezes, gap, best, used, earned


def simulate(days: Iterable[date], today: date, carry: Carry | None = None,
             bonus: Mapping[date, int] | None = None) -> Streak:
    """The streak, the freezes in hand and the best ever, as of `today`.

    A day counts if it is in `days` (the caller passes the days with at least
    one real, non-repeat award). The streak is the run of counted days ending
    today or yesterday: today not being counted *yet* does not break it, it
    just reads `today_counted = False`.

    One missed day in the middle of a run is bridged by a freeze if one is in
    hand. It is spent only when the next counted day arrives (a freeze is never
    burned on a day you then never come back from). Two missed days in a row
    end the run whatever you hold. You earn a freeze each time the streak
    reaches a multiple of 7 (up to 2 held), and the daily chest can add one
    (`bonus`: date -> freezes granted that day). A bridged day adds nothing to
    the streak and does not break it.
    """
    carry = carry or Carry()
    bonus = bonus or {}
    counted = {d for d in days if d <= today}
    yesterday = today - timedelta(days=1)
    streak, freezes, gap, best, used, earned = _run(counted, carry, bonus, yesterday)
    today_counted = today in counted
    if today_counted:
        # Today: the same rules, one more day.
        c = Carry(through=yesterday, streak=streak, freezes=freezes, gap=gap, best=best)
        streak, freezes, gap, best, used2, earned2 = _run(counted, c, bonus, today)
        used += used2
        earned += earned2
    else:
        # Today is not over. A missed yesterday only keeps the run alive if a freeze
        # is in hand to bridge it; no freeze (or older gap) means the run is over.
        if gap >= 2 or (gap == 1 and freezes == 0):
            streak = 0
    return Streak(
        streak=streak, best=best, freezes=freezes, today_counted=today_counted,
        used=tuple(used), earned=tuple(earned),
    )


def fold(days: Iterable[date], carry: Carry | None, bonus: Mapping[date, int] | None,
         through: date) -> Carry:
    """The carry after every day up to and including `through` is forgotten."""
    carry = carry or Carry()
    bonus = bonus or {}
    counted = {d for d in days if d <= through}
    if carry.through is not None and through <= carry.through:
        return carry
    streak, freezes, gap, best, _, _ = _run(counted, carry, bonus, through)
    return Carry(through=through, streak=streak, freezes=freezes, gap=gap, best=best)


# ── Daily quests ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DayStats:
    """What a day's records add up to, for quest progress."""

    xp: int = 0
    awards: int = 0
    kinds: Mapping[str, int] = field(default_factory=dict)
    #: Kinds used today that were not used on any of the six days before.
    fresh_kinds: frozenset[str] = frozenset()
    #: Things counted without being awards (no XP of their own): `farm_items`, the
    #: items the day's farm harvests. Quests read them; they do not count for the streak.
    counters: Mapping[str, int] = field(default_factory=dict)

    def count(self, kinds: Iterable[str]) -> int:
        return sum(int(self.kinds.get(k, 0)) for k in kinds)

    def counter(self, name: str) -> int:
        return int(self.counters.get(name, 0))

    @property
    def things(self) -> int:
        """Awards that count as a thing solved (not the two-XP micro ones, nor the passive ones)."""
        return sum(n for k, n in self.kinds.items() if k not in MICRO_KINDS | PASSIVE_KINDS)

    @property
    def modes(self) -> int:
        return sum(1 for k, n in self.kinds.items() if n and k not in MICRO_KINDS | PASSIVE_KINDS)


@dataclass(frozen=True)
class Quest:
    id: str
    #: Two quests of one group never share a day ("solve 3" and "solve 5").
    group: str
    label: str
    need: int
    have: Callable[[DayStats], int]


def _kinds(*names: str) -> Callable[[DayStats], int]:
    return lambda s: s.count(names)


POOL: tuple[Quest, ...] = (
    Quest("solve3", "solve", "Solve 3 things", 3, lambda s: s.things),
    Quest("solve5", "solve", "Solve 5 things", 5, lambda s: s.things),
    Quest("brain", "brain", "Do a Brain Drills round", 1, _kinds("brain_round")),
    Quest("typing", "typing", "Type a snippet", 1, _kinds("typing_run")),
    Quest("xp100", "xp", "Earn 100 XP", 100, lambda s: s.xp),
    Quest("xp200", "xp", "Earn 200 XP", 200, lambda s: s.xp),
    Quest("newmode", "new", "Try a mode you haven't used this week", 1,
          lambda s: len(s.fresh_kinds - MICRO_KINDS - PASSIVE_KINDS)),
    Quest("fix", "fix", "Fix something (Bug Hunt, Errors or Tickets)", 1,
          _kinds(*sorted(FIX_KINDS))),
    Quest("read", "read", "Predict or Trace 2 programs", 2, _kinds("predict", "trace")),
    Quest("three_modes", "modes", "Use 3 different modes today", 3, lambda s: s.modes),
    Quest("workbook2", "workbook", "Solve 2 Workbook pages", 2, _kinds("workbook_page")),
    Quest("build", "build", "Check a Canvas step or buy a Farm upgrade", 1,
          _kinds("canvas_step", "farm_buy")),
    Quest("kata", "kata", "Finish a Forms kata", 1, _kinds("kata")),
    Quest("pattern", "pattern", "Solve a Regex or a Puzzle", 1, _kinds("regex", "puzzle")),
    # The Farm today: at most one of these a day (one group).
    Quest("farm_items", "farm", "Harvest 50 items on the farm", 50,
          lambda s: s.counter("farm_items")),
    Quest("farm_research", "farm", "Buy a research upgrade on the farm", 1, _kinds("farm_buy")),
)

QUESTS_PER_DAY = 3
POOL_BY_ID = {q.id: q for q in POOL}


def pick_quests(day: date, pool: tuple[Quest, ...] = POOL, n: int = QUESTS_PER_DAY) -> list[str]:
    """Today's quests: decided by the date alone, never two from one group."""
    order = list(pool)
    random.Random(f"momentum-quests-{day.isoformat()}").shuffle(order)
    chosen: list[Quest] = []
    groups: set[str] = set()
    for q in order:
        if q.group not in groups:
            chosen.append(q)
            groups.add(q.group)
        if len(chosen) == n:
            break
    return [q.id for q in chosen]


def quest_progress(ids: Iterable[str], stats: DayStats) -> list[dict[str, Any]]:
    """Each quest as the screen shows it: label, have (capped at need), need, done."""
    out = []
    for qid in ids:
        q = POOL_BY_ID.get(qid)
        if q is None:  # a quest dropped from the pool after the day began
            continue
        have = max(0, int(q.have(stats)))
        out.append({"id": q.id, "label": q.label, "have": min(have, q.need),
                    "need": q.need, "done": have >= q.need})
    return out


# ── The chest ───────────────────────────────────────────────────────────

CHEST_TIERS = ((40, 70), (71, 110), (111, 150))
CHEST_WEIGHTS = (55, 33, 12)
CHEST_FREEZE_CHANCE = 0.20


def roll_chest(rng: Any, can_freeze: bool) -> tuple[int, bool]:
    """XP from 40 to 150 (small ones most often), and a one-in-five freeze if there is room."""
    lo, hi = rng.choices(CHEST_TIERS, weights=CHEST_WEIGHTS)[0]
    xp = int(rng.randint(lo, hi))
    freeze = rng.random() < CHEST_FREEZE_CHANCE
    return xp, bool(freeze and can_freeze)
