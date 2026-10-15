"""Momentum: XP, levels, combo, luck, the day streak and its freezes, quests, the chest.

The rules are pure functions (code_coach/momentum/rules.py) and are tested against
models written separately from them: the streak against a run-by-run reference
worked out from the rules in words, levels by round trip, luck by a stub random
source and by a large sample. The engine (engine.py) is tested through a real file
with a clock and a random source held still.

Tests that depend on the price list use `XP[kind]` and never a number, so the table
can grow or be re-tuned; the formula tests inject their own table or compute the
expectation from the rule's definition.
"""

from __future__ import annotations

import json
import math
import random
import re
import tempfile
import threading
import unittest
from datetime import date, datetime, timedelta
from fractions import Fraction
from pathlib import Path

from fastapi import HTTPException

from code_coach import momentum
from code_coach.api import server
from code_coach.api.schemas import MomentumAwardRequest
from code_coach.momentum import Momentum, UnknownKind, rules
from code_coach.momentum.rules import XP

ROOT = Path(__file__).resolve().parent.parent
D0 = date(2026, 3, 1)


def day(n: int) -> date:
    return D0 + timedelta(days=n)


def expected_pay(base: int, mult: float) -> int:
    """base x mult rounded half up, worked out exactly (the multiplier is a count of tenths)."""
    exact = Fraction(base) * Fraction(round(mult * 10), 10)
    return math.floor(exact + Fraction(1, 2))


def stamp(d: date, hour: int = 9, minute: int = 0, second: int = 0) -> float:
    return datetime(d.year, d.month, d.day, hour, minute, second).timestamp()


class Stub:
    """A random source that says what it is told. `randoms` cycle; `picks` index `choices`."""

    def __init__(self, randoms=(0.99,), picks=(0,), ints=(None,)) -> None:
        self.randoms, self.picks, self.ints = list(randoms), list(picks), list(ints)
        self.calls = 0

    def random(self) -> float:
        self.calls += 1
        return self.randoms[(self.calls - 1) % len(self.randoms)]

    def choices(self, population, weights=None):
        self.calls += 1
        return [population[self.picks[(self.calls - 1) % len(self.picks)]]]

    def randint(self, lo, hi):
        self.calls += 1
        want = self.ints[(self.calls - 1) % len(self.ints)]
        return lo if want is None else max(lo, min(hi, want))


class Clock:
    def __init__(self, t: float) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


class EngineCase(unittest.TestCase):
    """A Momentum on a throwaway file, a clock at 09:00 on D0, and luck switched off."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="momentum-test-")
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "momentum.json"
        self.clock = Clock(stamp(D0))
        self.m = Momentum(self.path, clock=self.clock, rng=Stub())
        self.n = 0

    def at(self, d: date, hour: int = 9, minute: int = 0, second: int = 0) -> None:
        self.clock.t = stamp(d, hour, minute, second)

    def award(self, kind: str = "kata", key: str | None = None) -> dict:
        if key is None:
            self.n += 1
            key = f"k{self.n}"
        return self.m.award(kind, key)

    def saved(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8"))


# ── Levels ──────────────────────────────────────────────────────────────


class LevelTests(unittest.TestCase):
    def test_thresholds_rise_and_start_at_zero(self) -> None:
        self.assertEqual(rules.xp_to_reach(1), 0)
        reach = [rules.xp_to_reach(n) for n in range(1, 200)]
        self.assertEqual(reach, sorted(set(reach)))
        gaps = [b - a for a, b in zip(reach, reach[1:])]
        self.assertEqual(gaps, sorted(gaps), "each level is at least as long as the one before")

    def test_level_and_threshold_are_inverses(self) -> None:
        for n in range(1, 300):
            at = rules.xp_to_reach(n)
            self.assertEqual(rules.level_for(at), n)
            if n > 1:
                self.assertEqual(rules.level_for(at - 1), n - 1)

    def test_every_xp_lands_in_the_level_whose_range_holds_it(self) -> None:
        rng = random.Random(7)
        for _ in range(3000):
            xp = rng.randrange(0, 400_000)
            n = rules.level_for(xp)
            self.assertLessEqual(rules.xp_to_reach(n), xp)
            self.assertLess(xp, rules.xp_to_reach(n + 1))
            info = rules.level_info(xp)
            self.assertEqual(info["level"], n)
            self.assertEqual(rules.xp_to_reach(n) + info["xp_in_level"], xp)
            self.assertEqual(info["xp_for_next"], rules.xp_to_reach(n + 1) - rules.xp_to_reach(n))
            self.assertTrue(0 <= info["xp_in_level"] < info["xp_for_next"])

    def test_titles_cycle_and_stay_distinct_per_level(self) -> None:
        laps = len(rules.TITLES)
        self.assertGreaterEqual(laps, 12)
        self.assertEqual(len(set(rules.TITLES)), laps)
        seen = {rules.title_for(n) for n in range(1, 5 * laps + 1)}
        self.assertEqual(len(seen), 5 * laps, "no two levels share a title, even past the first lap")
        self.assertEqual(rules.title_for(1), rules.TITLES[0])
        self.assertTrue(rules.title_for(laps + 1).startswith(rules.TITLES[0]))

    def test_negative_or_odd_totals_do_not_break_it(self) -> None:
        self.assertEqual(rules.level_for(-50), 1)
        self.assertEqual(rules.level_info(0)["xp_in_level"], 0)


# ── Combo and luck ──────────────────────────────────────────────────────


class ComboRules(unittest.TestCase):
    def test_multiplier_climbs_a_tenth_and_stops_at_two(self) -> None:
        got = [rules.combo_multiplier(n) for n in range(1, 16)]
        self.assertEqual(got[:4], [1.0, 1.1, 1.2, 1.3])
        self.assertEqual(got[10], 2.0)
        self.assertEqual(got[11:], [2.0] * 4)
        self.assertEqual(got, sorted(got))

    def test_the_gap_is_strictly_under_the_window(self) -> None:
        w = rules.COMBO_WINDOW
        self.assertEqual(rules.next_combo(4, 1000.0, 1000.0 + w - 1), 5)
        self.assertEqual(rules.next_combo(4, 1000.0, 1000.0 + w), 1)
        self.assertEqual(rules.next_combo(0, None, 5.0), 1)

    def test_payout_rounds_the_combo_then_multiplies_by_luck(self) -> None:
        self.assertEqual(rules.payout(15, 1.1, None), 17, "16.5 rounds up, not to even")
        self.assertEqual(rules.payout(20, 1.3, 3), 26 * 3)
        self.assertEqual(rules.payout(10, 1.0, None), 10)

    def test_payout_with_an_injected_table(self) -> None:
        for base in (2, 5, 10, 25, 40, 50):
            for count in range(1, 14):
                mult = rules.combo_multiplier(count)
                self.assertEqual(rules.payout(base, mult, None), expected_pay(base, mult))
                self.assertEqual(rules.payout(base, mult, 3), 3 * expected_pay(base, mult))


class LuckRules(unittest.TestCase):
    def test_a_low_roll_is_lucky_and_takes_the_weighted_pick(self) -> None:
        for pick, want in enumerate(rules.LUCKY_VALUES):
            self.assertEqual(rules.roll_lucky(Stub(randoms=(0.0,), picks=(pick,))), want)

    def test_a_high_roll_is_nothing_and_asks_nothing_more(self) -> None:
        stub = Stub(randoms=(rules.LUCKY_CHANCE + 0.001,))
        self.assertIsNone(rules.roll_lucky(stub))
        self.assertEqual(stub.calls, 1)

    def test_about_one_in_six_and_two_is_the_commonest(self) -> None:
        rng = random.Random(20261015)
        rolls = [rules.roll_lucky(rng) for _ in range(30000)]
        lucky = [r for r in rolls if r]
        self.assertAlmostEqual(len(lucky) / len(rolls), 1 / 6, delta=0.012)
        self.assertEqual(set(lucky), set(rules.LUCKY_VALUES))
        counts = {v: lucky.count(v) for v in set(lucky)}
        self.assertEqual(max(counts, key=counts.get), min(rules.LUCKY_VALUES))
        self.assertTrue(all(2 <= v <= 5 for v in lucky))


class ComboAndLuckInTheEngine(EngineCase):
    def test_awards_inside_ten_minutes_build_a_combo_and_a_gap_resets_it(self) -> None:
        first = self.award("kata")
        self.assertEqual((first["combo"], first["combo_mult"]), (1, 1.0))
        self.at(D0, 9, 0, 59)
        second = self.award("kata")
        self.assertEqual((second["combo"], second["combo_mult"]), (2, 1.1))
        self.assertEqual(second["gained"], expected_pay(XP["kata"], 1.1))
        self.at(D0, 9, 10, 58)  # 9:59 after the last one: still inside
        self.assertEqual(self.award("kata")["combo"], 3)
        self.at(D0, 9, 20, 58)  # exactly ten minutes: over
        gap = self.award("kata")
        self.assertEqual((gap["combo"], gap["combo_mult"]), (1, 1.0))

    def test_the_multiplier_stops_at_two_and_the_count_keeps_going(self) -> None:
        last = None
        for i in range(14):
            self.at(D0, 9, i)
            last = self.award("typing_run")
        self.assertEqual(last["combo"], 14)
        self.assertEqual(last["combo_mult"], 2.0)
        self.assertEqual(last["gained"], expected_pay(XP["typing_run"], 2.0))

    def test_a_repeat_neither_pays_nor_extends_the_combo(self) -> None:
        self.award("kata", "same")
        self.at(D0, 9, 5)
        rep = self.award("kata", "same")
        self.assertTrue(rep["repeat"])
        self.at(D0, 9, 9)
        nxt = self.award("kata", "other")
        self.assertEqual(nxt["combo"], 2, "the repeat in between did not count, nor refresh the timer")

    def test_lucky_multiplies_the_combo_payout_and_is_reported(self) -> None:
        self.m.rng = Stub(randoms=(0.0,), picks=(1,))  # lucky, the second value
        got = self.award("kata")
        self.assertEqual(got["lucky"], rules.LUCKY_VALUES[1])
        self.assertEqual(got["gained"], XP["kata"] * rules.LUCKY_VALUES[1])
        self.assertEqual(got["xp_total"], got["gained"])

    def test_no_luck_when_the_roll_is_high_and_none_for_repeats(self) -> None:
        stub = Stub(randoms=(0.0,))
        self.m.rng = stub
        self.award("kata", "x")
        asked = stub.calls
        self.assertGreater(asked, 0)
        rep = self.award("kata", "x")
        self.assertTrue(rep["repeat"])
        self.assertIsNone(rep["lucky"])
        self.assertEqual(stub.calls, asked, "a repeat does not roll")
        self.m.rng = Stub()
        self.assertIsNone(self.award("kata")["lucky"])


# ── The streak ──────────────────────────────────────────────────────────


def reference(counted: set[date], today: date, bonus: dict[date, int]) -> dict:
    """The streak rules worked out run by run, written without looking at rules.simulate.

    The rules, in words: the days with an award form runs separated by gaps of missed
    days. A gap of exactly one day is bridged if a freeze is in hand (it is spent then,
    and the streak carries on); any other gap starts the count again. Every 7th day of
    the count earns a freeze (never past 2 held). A chest freeze is added on its day.
    Today not yet counted does not end anything: it only matters whether yesterday's
    run (or a one-day gap a freeze can bridge) is still reachable.
    """
    counted = {d for d in counted if d <= today}
    if not counted:
        return dict(streak=0, best=0, freezes=0, today_counted=False, used=[], earned=[])
    hits = sorted(counted)
    runs: list[list[date]] = []
    for d in hits:
        if runs and (d - runs[-1][-1]).days == 1:
            runs[-1].append(d)
        else:
            runs.append([d])
    count = best = held = 0
    used: list[date] = []
    earned: list[date] = []
    prev_end: date | None = None
    for run in runs:
        if prev_end is not None:
            gap = (run[0] - prev_end).days - 1
            if gap == 1 and held > 0:
                held -= 1
                used.append(prev_end + timedelta(days=1))
            else:
                count = 0
        for d in run:
            count += 1
            if count % 7 == 0 and held < 2:
                held += 1
                earned.append(d)
            held = min(2, held + bonus.get(d, 0))
            best = max(best, count)
        prev_end = run[-1]
    alive = count
    if today not in counted:
        missed = (today - prev_end).days - 1
        if not (missed == 0 or (missed == 1 and held > 0)):
            alive = 0
    return dict(streak=alive, best=best, freezes=held, today_counted=today in counted,
                used=used, earned=earned)


def run_rules(counted, today, bonus=None, carry=None) -> dict:
    s = rules.simulate(counted, today, carry, bonus)
    return dict(streak=s.streak, best=s.best, freezes=s.freezes, today_counted=s.today_counted,
                used=list(s.used), earned=list(s.earned))


class StreakRules(unittest.TestCase):
    def run_of(self, *offsets: int, today: int, bonus=None):
        return run_rules({day(o) for o in offsets}, day(today), bonus)

    def test_nothing_done_is_no_streak(self) -> None:
        got = self.run_of(today=5)
        self.assertEqual((got["streak"], got["freezes"], got["today_counted"]), (0, 0, False))

    def test_today_not_yet_counted_does_not_break_a_streak(self) -> None:
        got = self.run_of(0, 1, 2, today=3)
        self.assertEqual((got["streak"], got["today_counted"]), (3, False))
        got = self.run_of(0, 1, 2, 3, today=3)
        self.assertEqual((got["streak"], got["today_counted"]), (4, True))

    def test_a_missed_day_with_no_freeze_ends_it(self) -> None:
        self.assertEqual(self.run_of(0, 1, 2, today=4)["streak"], 0)
        got = self.run_of(0, 1, 2, 4, today=4)
        self.assertEqual(got["streak"], 1)
        self.assertEqual(got["best"], 3)
        self.assertEqual(got["used"], [])

    def test_the_seventh_day_earns_a_freeze_and_one_missed_day_spends_it(self) -> None:
        week = list(range(7))
        got = self.run_of(*week, today=6)
        self.assertEqual((got["streak"], got["freezes"], got["earned"]), (7, 1, [day(6)]))
        # miss day 7, back on day 8: bridged; the freeze is gone, the streak is 8 not 9
        got = self.run_of(*week, 8, today=8)
        self.assertEqual((got["streak"], got["freezes"], got["used"]), (8, 0, [day(7)]))
        # on day 8 morning, before doing anything, the streak is still alive (a freeze is in hand)
        got = self.run_of(*week, today=8)
        self.assertEqual((got["streak"], got["freezes"], got["used"], got["today_counted"]),
                         (7, 1, [], False))
        # ... but with no freeze to bridge it, the same morning shows 0
        got = self.run_of(0, 1, 2, today=4)
        self.assertEqual(got["streak"], 0)

    def test_two_missed_days_end_it_even_with_freezes_in_hand(self) -> None:
        got = self.run_of(*range(14), 17, today=17)  # two freezes earned, then a two-day hole
        self.assertEqual(got["streak"], 1)
        self.assertEqual(got["best"], 14)
        self.assertEqual(got["freezes"], 2)
        self.assertEqual(got["used"], [])

    def test_at_most_two_freezes_are_held(self) -> None:
        got = self.run_of(*range(28), today=27)
        self.assertEqual(got["freezes"], rules.MAX_FREEZES)
        self.assertEqual(got["earned"], [day(6), day(13)], "the 3rd and 4th would exceed the cap")

    def test_a_chest_freeze_counts_on_its_day(self) -> None:
        got = self.run_of(0, 1, 2, today=2, bonus={day(2): 1})
        self.assertEqual(got["freezes"], 1)
        got = self.run_of(0, 1, 2, 4, today=4, bonus={day(2): 1})
        self.assertEqual((got["streak"], got["used"], got["freezes"]), (4, [day(3)], 0))

    def test_best_survives_a_break(self) -> None:
        got = self.run_of(*range(5), 10, 11, today=11)
        self.assertEqual((got["streak"], got["best"]), (2, 5))

    def test_days_in_the_future_are_ignored(self) -> None:
        got = self.run_of(0, 1, 5, today=1)
        self.assertEqual(got["streak"], 2)

    def test_matches_the_reference_on_random_histories(self) -> None:
        rng = random.Random(1015)
        for case in range(600):
            span = rng.choice((8, 20, 45, 90))
            density = rng.choice((0.3, 0.6, 0.8, 0.92, 1.0))
            counted = {day(i) for i in range(span) if rng.random() < density}
            today = day(rng.randrange(max(1, span - 5), span + 4))
            bonus = {d: 1 for d in counted if rng.random() < 0.08}
            want = reference(counted, today, bonus)
            got = run_rules(counted, today, bonus)
            self.assertEqual(got, want, f"case {case}: days {sorted(d.toordinal() - D0.toordinal() for d in counted)} today {today}")

    def test_forgetting_old_days_into_a_carry_changes_nothing(self) -> None:
        rng = random.Random(77)
        for case in range(300):
            span = rng.choice((30, 60, 120))
            counted = {day(i) for i in range(span) if rng.random() < rng.choice((0.7, 0.9, 1.0))}
            bonus = {d: 1 for d in counted if rng.random() < 0.05}
            today = day(span + rng.randrange(0, 3))
            whole = run_rules(counted, today, bonus)
            cut = day(rng.randrange(1, span))
            carry = rules.fold(counted, None, bonus, cut)
            kept = {d for d in counted if d > cut}
            part = run_rules(kept, today, bonus, carry)
            for field in ("streak", "freezes", "today_counted", "best"):
                self.assertEqual(part[field], whole[field], f"case {case} cut {cut} {field}")


class StreakInTheEngine(EngineCase):
    def test_seven_days_earn_a_freeze_and_a_missed_day_is_bridged(self) -> None:
        for i in range(7):
            self.at(day(i))
            got = self.award()
            self.assertEqual(got["streak"], i + 1)
            self.assertEqual(got["streak_extended"], True)
        self.assertTrue(got["freeze_earned"])
        self.assertEqual(got["freezes"], 1)
        # day 7 is missed; day 8 comes with a freeze to spend
        self.at(day(7))
        morning = self.m.summary()
        self.assertEqual((morning["streak"], morning["today_counted"], morning["freezes"]), (7, False, 1))
        self.at(day(8))
        got = self.award()
        self.assertEqual(got["freeze_used"], day(7).isoformat())
        self.assertEqual((got["streak"], got["freezes"]), (8, 0))
        self.assertTrue(got["streak_extended"])

    def test_the_second_award_of_a_day_extends_nothing(self) -> None:
        self.assertTrue(self.award()["streak_extended"])
        again = self.award()
        self.assertFalse(again["streak_extended"])
        self.assertTrue(again["today_counted"])

    def test_the_morning_after_the_streak_is_alive_but_today_is_not_counted(self) -> None:
        self.award("kata", "x")
        self.at(day(1))
        got = self.m.summary()
        self.assertEqual((got["streak"], got["today_counted"]), (1, False))

    def test_two_missed_days_start_again_and_best_remembers(self) -> None:
        for i in range(3):
            self.at(day(i))
            self.award()
        self.at(day(5))
        got = self.award()
        self.assertEqual(got["streak"], 1)
        self.assertEqual(got["best_streak"], 3)
        self.assertIsNone(got["freeze_used"])

    def test_the_file_keeps_a_best_streak_even_after_the_run_ends(self) -> None:
        for i in range(4):
            self.at(day(i))
            self.award()
        self.at(day(30))
        self.award()
        self.assertEqual(self.saved()["best_streak"], 4)


# ── Dedupe, XP, levels in the engine ────────────────────────────────────


class AwardRules(EngineCase):
    def test_unknown_kind_is_refused_and_writes_nothing(self) -> None:
        with self.assertRaises(UnknownKind):
            self.m.award("definitely_not_a_kind", "k")
        self.assertFalse(self.path.exists())

    def test_the_client_never_names_an_amount(self) -> None:
        got = self.m.award("kata", "k")
        self.assertEqual(got["base"], XP["kata"])
        self.assertEqual(got["xp_total"], got["gained"])

    def test_every_kind_in_the_table_pays_what_the_table_says(self) -> None:
        for kind, base in XP.items():
            m = Momentum(Path(self._tmp.name) / f"{kind}.json", clock=Clock(stamp(D0)), rng=Stub())
            got = m.award(kind, "k")
            self.assertEqual((got["base"], got["gained"]), (base, base), kind)

    def test_the_same_kind_and_key_pays_once_a_day(self) -> None:
        a = self.award("kata", "page-1")
        b = self.award("kata", "page-1")
        self.assertFalse(a["repeat"])
        self.assertTrue(b["repeat"])
        self.assertEqual((b["gained"], b["base"]), (0, 0))
        self.assertEqual(b["xp_total"], a["xp_total"])
        self.assertEqual(self.saved()["days"][D0.isoformat()]["awards"], 1)

    def test_a_different_key_or_a_different_kind_still_pays(self) -> None:
        self.award("kata", "a")
        self.assertFalse(self.award("kata", "b")["repeat"])
        self.assertFalse(self.award("predict", "a")["repeat"])

    def test_it_pays_again_tomorrow(self) -> None:
        self.award("kata", "a")
        self.at(day(1))
        self.assertFalse(self.award("kata", "a")["repeat"])

    def test_mashing_check_cannot_farm_xp(self) -> None:
        first = self.award("workbook_page", "p1")
        for _ in range(50):
            last = self.award("workbook_page", "p1")
        self.assertEqual(last["xp_total"], first["xp_total"])
        self.assertEqual(self.saved()["lifetime"]["workbook_page"], 1)

    def test_keys_are_trimmed_and_blank_ones_still_dedupe(self) -> None:
        self.award("kata", "  spaced  ")
        self.assertTrue(self.award("kata", "spaced")["repeat"])
        self.award("kata", "")
        self.assertTrue(self.award("kata", "   ")["repeat"])

    def test_a_level_up_is_announced_once_with_the_new_level(self) -> None:
        total = 0
        seen = []
        level = 1
        for i in range(400):
            self.at(D0, 9, 0, i)
            got = self.award("casefile")
            total += got["gained"]
            self.assertEqual(got["xp_total"], total)
            if got["level_up"]:
                seen.append(got["level_up"])
                self.assertEqual(got["level_up"]["level"], level + 1)
                self.assertEqual(got["level_up"]["title"], rules.title_for(level + 1))
                level += 1
            self.assertEqual(got["level"], level)
            if level >= 4:
                break
        self.assertEqual([s["level"] for s in seen], [2, 3, 4])

    def test_the_day_records_what_was_done(self) -> None:
        self.award("kata")
        self.award("kata")
        self.award("predict")
        rec = self.saved()["days"][D0.isoformat()]
        self.assertEqual(rec["awards"], 3)
        self.assertEqual(rec["kinds"], {"kata": 2, "predict": 1})
        self.assertEqual(len(rec["keys"]), 3)
        self.assertEqual(self.saved()["lifetime"], {"kata": 2, "predict": 1})


# ── Quests and the chest ────────────────────────────────────────────────


def satisfy(test: EngineCase, d: date, results: list[dict]) -> dict:
    """Award across every kind, with unique keys, until all of the day's quests are done."""
    last = test.m.summary()
    for rounds in range(4):
        if all(q["done"] for q in last["quests"]):
            break
        # The farm quest counts items the farm harvested (no award of its own): the host tells the engine.
        farm = test.m.record_farm_items("python", 100, 100)
        if farm.get("quest"):
            results.append(farm["quest"])
        for kind in XP:
            test.n += 1
            last = test.m.award(kind, f"sat-{rounds}-{kind}-{test.n}")
            results.append(last)
    return last


class QuestRules(unittest.TestCase):
    def test_three_distinct_quests_decided_by_the_date_alone(self) -> None:
        for n in range(60):
            first = rules.pick_quests(day(n))
            self.assertEqual(first, rules.pick_quests(day(n)))
            self.assertEqual(len(first), rules.QUESTS_PER_DAY)
            self.assertEqual(len(set(first)), rules.QUESTS_PER_DAY)
            groups = [rules.POOL_BY_ID[q].group for q in first]
            self.assertEqual(len(set(groups)), len(groups), "no two quests of one group in a day")

    def test_other_dates_give_other_quests(self) -> None:
        triples = {tuple(rules.pick_quests(day(n))) for n in range(40)}
        self.assertGreater(len(triples), 12)
        used = {q for t in triples for q in t}
        self.assertGreater(len(used), len(rules.POOL) // 2)

    def test_the_pool_is_big_enough_and_each_quest_can_be_met(self) -> None:
        groups = {q.group for q in rules.POOL}
        self.assertGreaterEqual(len(groups), rules.QUESTS_PER_DAY + 3)
        everything = rules.DayStats(xp=10_000, awards=99, kinds={k: 9 for k in XP},
                                    fresh_kinds=frozenset(XP), counters={"farm_items": 10_000})
        nothing = rules.DayStats()
        for q in rules.POOL:
            self.assertGreaterEqual(q.have(everything), q.need, q.id)
            self.assertLess(q.have(nothing), q.need, q.id)

    def test_progress_is_capped_at_the_target_and_names_done(self) -> None:
        stats = rules.DayStats(xp=1000, awards=9, kinds={"kata": 9})
        for q in rules.quest_progress([q.id for q in rules.POOL], stats):
            self.assertLessEqual(q["have"], q["need"])
            self.assertEqual(q["done"], q["have"] >= q["need"])

    def test_brain_items_do_not_count_as_things_solved(self) -> None:
        stats = rules.DayStats(awards=30, kinds={"brain_item": 30})
        self.assertEqual(stats.things, 0)
        self.assertEqual(stats.modes, 0)

    def test_a_quest_gone_from_the_pool_is_skipped_not_fatal(self) -> None:
        self.assertEqual(rules.quest_progress(["no-such-quest"], rules.DayStats()), [])


class QuestsInTheEngine(EngineCase):
    def test_today_has_three_quests_at_zero(self) -> None:
        got = self.m.summary()
        self.assertEqual([q["id"] for q in got["quests"]], rules.pick_quests(D0))
        self.assertTrue(all(q["have"] == 0 and not q["done"] for q in got["quests"]))
        self.assertFalse(got["chest_ready"])

    def test_quests_are_fixed_for_the_day_once_it_starts(self) -> None:
        got = self.award()
        saved = self.saved()["days"][D0.isoformat()]["quests"]
        self.assertEqual(saved, [q["id"] for q in got["quests"]])

    def test_progress_counts_the_days_records_and_each_quest_announces_once(self) -> None:
        results: list[dict] = []
        last = satisfy(self, D0, results)
        self.assertTrue(all(q["done"] for q in last["quests"]))
        announced: dict[str, int] = {}
        for r in results:
            for q in r["quests"]:
                if q["just_done"]:
                    announced[q["id"]] = announced.get(q["id"], 0) + 1
        self.assertEqual(announced, {q["id"]: 1 for q in last["quests"]})
        again = self.m.summary()
        self.assertFalse(any(q["just_done"] for q in again["quests"]), "a reload does not re-announce")

    def test_a_quest_done_early_is_not_undone_and_does_not_announce_again(self) -> None:
        first = self.award("kata")
        done_now = {q["id"] for q in first["quests"] if q["done"]}
        second = self.award("predict")
        for q in second["quests"]:
            if q["id"] in done_now:
                self.assertTrue(q["done"])
                self.assertFalse(q["just_done"])

    def test_progress_is_the_days_own(self) -> None:
        self.award("brain_round")
        self.at(day(1))
        got = self.m.summary()
        self.assertTrue(all(q["have"] == 0 for q in got["quests"]))

    def test_a_new_mode_is_one_not_used_in_the_six_days_before(self) -> None:
        # find a day whose quests include the new-mode quest
        target = next(day(n) for n in range(2, 400) if "newmode" in rules.pick_quests(day(n)))
        self.at(target - timedelta(days=3))
        self.award("kata")
        self.at(target)
        got = self.award("kata", "again-after-3-days")
        newmode = next(q for q in got["quests"] if q["id"] == "newmode")
        self.assertFalse(newmode["done"], "kata was used 3 days ago, so it is not new")
        got = self.award("predict")
        newmode = next(q for q in got["quests"] if q["id"] == "newmode")
        self.assertTrue(newmode["done"])

    def test_a_kind_last_used_a_week_ago_is_new_again(self) -> None:
        target = next(day(n) for n in range(8, 400) if "newmode" in rules.pick_quests(day(n)))
        self.at(target - timedelta(days=7))
        self.award("kata")
        self.at(target)
        got = self.award("kata", "long-ago")
        self.assertTrue(next(q for q in got["quests"] if q["id"] == "newmode")["done"])


class ChestRules(unittest.TestCase):
    def test_xp_is_between_forty_and_a_hundred_fifty_small_ones_commonest(self) -> None:
        rng = random.Random(5)
        rolls = [rules.roll_chest(rng, True) for _ in range(6000)]
        xps = [r[0] for r in rolls]
        self.assertTrue(all(40 <= x <= 150 for x in xps))
        self.assertGreater(min(xps), 39)
        self.assertEqual(min(xps), 40)
        self.assertEqual(max(xps), 150)
        small = sum(1 for x in xps if x <= 70)
        large = sum(1 for x in xps if x >= 111)
        self.assertGreater(small, large * 2)

    def test_a_freeze_comes_one_time_in_five_and_never_when_there_is_no_room(self) -> None:
        rng = random.Random(6)
        freezes = [rules.roll_chest(rng, True)[1] for _ in range(8000)]
        self.assertAlmostEqual(sum(freezes) / len(freezes), 0.2, delta=0.02)
        rng = random.Random(6)
        self.assertFalse(any(rules.roll_chest(rng, False)[1] for _ in range(2000)))


class ChestInTheEngine(EngineCase):
    def finish_quests(self) -> dict:
        results: list[dict] = []
        return satisfy(self, D0, results)

    def test_not_ready_until_all_three_quests_are_done(self) -> None:
        got = self.m.claim_chest()
        self.assertFalse(got["ok"])
        self.assertEqual((got["reason"], got["gained"]), ("not_ready", 0))
        self.award("kata")
        self.assertFalse(self.m.claim_chest()["ok"])

    def test_it_opens_once_a_day_and_adds_its_xp(self) -> None:
        last = self.finish_quests()
        self.assertTrue(last["chest_ready"])
        before = self.m.summary()["xp_total"]
        got = self.m.claim_chest()
        self.assertTrue(got["ok"])
        self.assertTrue(40 <= got["gained"] <= 150)
        self.assertEqual(got["xp_total"], before + got["gained"])
        self.assertTrue(got["chest_claimed"])
        self.assertFalse(got["chest_ready"])
        again = self.m.claim_chest()
        self.assertFalse(again["ok"])
        self.assertEqual((again["reason"], again["gained"]), ("already_claimed", 0))
        self.assertEqual(self.m.summary()["xp_total"], before + got["gained"])

    def test_a_new_day_has_a_new_chest(self) -> None:
        self.finish_quests()
        self.m.claim_chest()
        self.at(day(1))
        self.assertFalse(self.m.summary()["chest_claimed"])
        results: list[dict] = []
        satisfy(self, day(1), results)
        self.assertTrue(self.m.claim_chest()["ok"])

    def test_a_lucky_chest_adds_a_freeze_if_there_is_room(self) -> None:
        self.finish_quests()
        self.m.rng = Stub(randoms=(0.0,), picks=(1,), ints=(100,))  # the middle tier, 100 xp, and a low freeze roll
        got = self.m.claim_chest()
        self.assertTrue(got["freeze_earned"])
        self.assertEqual(got["gained"], 100)
        self.assertEqual(got["freezes"], 1)
        self.assertEqual(self.saved()["freezes"], 1)

    def test_no_freeze_when_two_are_already_held(self) -> None:
        for i in range(14):
            self.at(day(i))
            self.award()
        self.assertEqual(self.m.summary()["freezes"], 2)
        self.at(day(14))
        results: list[dict] = []
        satisfy(self, day(14), results)
        self.m.rng = Stub(randoms=(0.0,))
        got = self.m.claim_chest()
        self.assertTrue(got["ok"])
        self.assertFalse(got["freeze_earned"])
        self.assertEqual(got["freezes"], 2)

    def test_the_chest_can_level_you_up_and_says_so(self) -> None:
        self.finish_quests()
        xp = self.m.summary()["xp_total"]
        level = rules.level_for(xp)
        # put the total one XP short of the next level, then open the chest
        state = self.saved()
        state["xp"] = rules.xp_to_reach(level + 1) - 1
        self.path.write_text(json.dumps(state), encoding="utf-8")
        got = self.m.claim_chest()
        self.assertEqual(got["level_up"]["level"], level + 1)


# ── The file ────────────────────────────────────────────────────────────


class Persistence(EngineCase):
    def test_a_missing_file_starts_fresh_and_a_save_creates_it(self) -> None:
        self.assertFalse(self.path.exists())
        got = self.m.summary()
        self.assertEqual((got["xp_total"], got["streak"], got["level"]), (0, 0, 1))
        self.assertFalse(self.path.exists(), "looking writes nothing")
        self.award()
        self.assertTrue(self.path.exists())

    def test_state_survives_a_new_object_on_the_same_file(self) -> None:
        got = self.award("kata", "z")
        other = Momentum(self.path, clock=self.clock, rng=Stub())
        self.assertEqual(other.summary()["xp_total"], got["xp_total"])
        self.assertTrue(other.award("kata", "z")["repeat"])

    def test_a_corrupt_file_is_kept_as_bad_and_a_fresh_one_started(self) -> None:
        self.path.write_text("{ this is not json", encoding="utf-8")
        got = self.award()
        self.assertTrue(got["ok"])
        self.assertEqual(got["xp_total"], got["gained"])
        bad = self.path.with_name("momentum.json.bad")
        self.assertEqual(bad.read_text(encoding="utf-8"), "{ this is not json")
        self.assertEqual(self.saved()["xp"], got["gained"])

    def test_a_file_of_the_wrong_shape_is_corrupt_too(self) -> None:
        self.path.write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(self.m.summary()["xp_total"], 0)
        self.assertEqual(self.path.with_name("momentum.json.bad").read_text(encoding="utf-8"), "[1, 2, 3]")

    def test_only_one_bad_file_is_kept(self) -> None:
        for text in ("first{", "second{"):
            self.path.write_text(text, encoding="utf-8")
            self.m.summary()
        self.assertEqual(self.path.with_name("momentum.json.bad").read_text(encoding="utf-8"), "second{")

    def test_odd_values_inside_a_good_file_are_tolerated(self) -> None:
        self.path.write_text(json.dumps({
            "xp": "lots", "days": {"2026-03-01": {"xp": None, "awards": "x", "kinds": []},
                                   "not-a-date": {"xp": 5}, "2026-03-02": 7},
            "combo": "no", "lifetime": [], "freezes": 99,
        }), encoding="utf-8")
        got = self.award()
        self.assertTrue(got["ok"])
        self.assertEqual(got["freezes"], 0)  # freezes come from the days, not the cached number
        self.assertFalse(self.path.with_name("momentum.json.bad").exists())

    def test_a_save_leaves_no_temporary_file(self) -> None:
        self.award()
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()), ["momentum.json"])

    def test_a_storage_problem_answers_not_ok_and_never_raises(self) -> None:
        blocker = Path(self._tmp.name) / "a-file"
        blocker.write_text("x", encoding="utf-8")
        broken = Momentum(blocker / "momentum.json", clock=self.clock, rng=Stub())
        got = broken.award("kata", "k")
        self.assertEqual(got, {"ok": False})
        self.assertFalse(broken.claim_chest()["ok"])
        self.assertEqual(broken.summary()["xp_total"], 0)

    def test_it_sits_beside_the_progress_file(self) -> None:
        from code_coach.progress.store import active_store

        self.assertEqual(momentum.save_path(), active_store().path.with_name("momentum.json"))


class Pruning(EngineCase):
    def test_a_long_streak_survives_forgetting_its_oldest_days(self) -> None:
        total = 420
        for i in range(total):
            self.at(day(i))
            got = self.award()
        self.assertEqual(got["streak"], total)
        saved = self.saved()
        self.assertLessEqual(len(saved["days"]), 401)
        self.assertIsNotNone(saved["baseline"])
        self.assertGreaterEqual(saved["best_streak"], total)
        self.assertEqual(self.m.summary()["streak"], total)
        # a missed day with the freezes held bridges it, as it would have without forgetting
        self.at(day(total + 1))
        self.assertEqual(self.award()["streak"], total + 1)

    def test_old_keys_are_dropped_but_todays_stay(self) -> None:
        for i in range(6):
            self.at(day(i))
            self.award()
        days = self.saved()["days"]
        self.assertEqual(days[day(5).isoformat()]["keys"] != [], True)
        self.assertEqual(days[day(0).isoformat()]["keys"], [])
        self.assertEqual(days[day(0).isoformat()]["awards"], 1)


class Concurrency(EngineCase):
    def test_two_threads_awarding_at_once_lose_nothing(self) -> None:
        per = 40
        gained: list[int] = []
        lock = threading.Lock()

        def work(tag: str) -> None:
            for i in range(per):
                got = self.m.award("kata", f"{tag}-{i}")
                with lock:
                    gained.append(got["gained"])

        threads = [threading.Thread(target=work, args=(t,)) for t in ("a", "b")]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(len(gained), 2 * per)
        saved = self.saved()
        self.assertEqual(saved["xp"], sum(gained))
        self.assertEqual(saved["lifetime"]["kata"], 2 * per)
        self.assertEqual(saved["days"][D0.isoformat()]["awards"], 2 * per)
        self.assertEqual(len(set(saved["days"][D0.isoformat()]["keys"])), 2 * per)

    def test_two_threads_with_the_same_key_pay_once(self) -> None:
        results: list[dict] = []
        gate = threading.Barrier(2)

        def work() -> None:
            gate.wait()
            results.append(self.m.award("kata", "same"))

        threads = [threading.Thread(target=work) for _ in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(sorted(r["repeat"] for r in results), [False, True])
        self.assertEqual(self.saved()["lifetime"]["kata"], 1)


# ── The routes ──────────────────────────────────────────────────────────


class Routes(unittest.TestCase):
    """The functions the app serves, called as the other API tests call theirs.

    They use the app's own Momentum, whose file lands beside this test's progress file
    (tests/conftest.py gives every test its own).
    """

    def setUp(self) -> None:
        self.m = momentum.MOMENTUM
        self.saved = (self.m.clock, self.m.rng)
        self.m.clock = Clock(stamp(D0))
        self.m.rng = Stub()
        self.addCleanup(lambda: (setattr(self.m, "clock", self.saved[0]), setattr(self.m, "rng", self.saved[1])))

    def test_the_three_routes_exist_with_the_right_methods(self) -> None:
        seen = {(r.path, tuple(sorted(r.methods))) for r in server.app.routes if hasattr(r, "methods")}
        self.assertIn(("/api/momentum", ("GET",)), seen)
        self.assertIn(("/api/momentum/award", ("POST",)), seen)
        self.assertIn(("/api/momentum/chest", ("POST",)), seen)

    def test_an_unknown_kind_is_http_400(self) -> None:
        with self.assertRaises(HTTPException) as caught:
            server.momentum_award(MomentumAwardRequest(kind="free_xp", key="x"))
        self.assertEqual(caught.exception.status_code, 400)
        with self.assertRaises(HTTPException):
            server.momentum_award(MomentumAwardRequest(kind="", key=""))

    def test_award_then_summary_agree(self) -> None:
        got = server.momentum_award(MomentumAwardRequest(kind="kata", key="a"))
        for field in ("ok", "repeat", "base", "combo", "combo_mult", "lucky", "gained", "xp_total",
                      "level", "level_up", "streak", "streak_extended", "freeze_used",
                      "freeze_earned", "quests", "chest_ready", "chest_claimed"):
            self.assertIn(field, got, field)
        self.assertTrue(got["ok"])
        self.assertEqual(got["gained"], XP["kata"])
        summary = server.momentum_summary()
        for field in ("xp_total", "level", "title", "xp_in_level", "xp_for_next", "streak", "best_streak",
                      "freezes", "today_xp", "today_counted", "days_last_14", "quests",
                      "chest_ready", "chest_claimed"):
            self.assertIn(field, summary, field)
        self.assertEqual(summary["xp_total"], got["xp_total"])
        self.assertEqual(summary["today_xp"], got["gained"])
        self.assertEqual(len(summary["days_last_14"]), 14)
        self.assertEqual(summary["days_last_14"][-1], {"day": D0.isoformat(), "xp": got["gained"]})
        self.assertEqual([q["id"] for q in summary["quests"]], [q["id"] for q in got["quests"]])
        self.assertTrue(all("just_done" in q for q in got["quests"]))

    def test_repeat_and_chest_over_the_routes(self) -> None:
        server.momentum_award(MomentumAwardRequest(kind="kata", key="a"))
        rep = server.momentum_award(MomentumAwardRequest(kind="kata", key="a"))
        self.assertEqual((rep["repeat"], rep["gained"]), (True, 0))
        self.assertFalse(server.momentum_chest()["ok"])
        for round_ in range(4):
            for kind in XP:
                server.momentum_award(MomentumAwardRequest(kind=kind, key=f"r{round_}"))
        self.assertTrue(server.momentum_summary()["chest_ready"])
        got = server.momentum_chest()
        self.assertTrue(got["ok"])
        self.assertGreater(got["gained"], 0)
        self.assertFalse(server.momentum_chest()["ok"])


# ── Every kind the client sends is priced, every price is used ──────────


AWARD_CALL = re.compile(r"""\baward\(\s*["']([a-z_]+)["']""")


class KindsAreConsistent(unittest.TestCase):
    def web_kinds(self) -> dict[str, list[str]]:
        found: dict[str, list[str]] = {}
        for path in (ROOT / "web" / "src").rglob("*.ts*"):
            for kind in AWARD_CALL.findall(path.read_text(encoding="utf-8")):
                found.setdefault(kind, []).append(path.name)
        return found

    def test_every_kind_the_screens_send_has_a_price(self) -> None:
        sent = self.web_kinds()
        self.assertTrue(sent, "no award(...) calls found under web/src")
        unknown = {k: v for k, v in sent.items() if k not in XP}
        self.assertEqual(unknown, {}, "award() kinds the server would refuse with a 400")

    def test_every_priced_kind_is_sent_by_some_screen_or_listed_as_unused(self) -> None:
        sent = self.web_kinds()
        orphans = [k for k in XP if k not in sent and k not in rules.UNUSED_KINDS]
        self.assertEqual(orphans, [], "priced but never awarded: wire it or add it to UNUSED_KINDS with a reason")
        for kind, why in rules.UNUSED_KINDS.items():
            self.assertIn(kind, XP)
            self.assertTrue(why.strip(), f"{kind}: an unused kind needs a reason")

    def test_every_award_call_names_its_kind_as_a_plain_string(self) -> None:
        # A kind picked at run time cannot be checked above, so it is not allowed.
        odd = []
        for path in (ROOT / "web" / "src").rglob("*.ts*"):
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                code = line.split("//")[0]
                if code.lstrip().startswith(("*", "/*")):
                    continue
                for m in re.finditer(r"\baward\(\s*([^\s)])", code):
                    if m.group(1) not in "\"'" and "function award" not in code:
                        odd.append(f"{path.name}:{line_no}")
        self.assertEqual(odd, [])

    def test_prices_are_whole_positive_numbers(self) -> None:
        self.assertTrue(all(isinstance(v, int) and v > 0 for v in XP.values()))


if __name__ == "__main__":
    unittest.main()
