"""Momentum's Farm side: server-only kinds, lifetime dedupe, farm quests, the welcome-back.

These are the engine's half of the Farm tie-in (the farm host's half, with real programs,
is tests/test_farm_momentum.py). Every number is worked out here from the rules the
docstrings state - 15 XP and +1 per ten ripe tiles up to 10, a first is paid once ever, a
quest of 50 farm items - not read back from the code under test.
"""

from __future__ import annotations

import json
import unittest
from datetime import timedelta
from pathlib import Path

from fastapi import HTTPException

from code_coach.api import server
from code_coach.api.schemas import MomentumAwardRequest
from code_coach.momentum import Momentum, UnknownKind, rules
from code_coach.momentum.rules import SERVER_XP, XP
from tests.test_momentum import D0, Clock, EngineCase, Stub, day, expected_pay, stamp

MILESTONE = "farm_milestone"


class ServerKinds(unittest.TestCase):
    def test_server_kinds_are_priced_and_are_not_client_kinds(self) -> None:
        self.assertTrue(SERVER_XP)
        self.assertTrue(all(isinstance(v, int) and v > 0 for v in SERVER_XP.values()))
        self.assertEqual(set(SERVER_XP) & set(XP), set(), "a kind is the browser's or the server's, not both")
        self.assertTrue(rules.LIFETIME_KINDS <= set(SERVER_XP), "lifetime dedupe is for server kinds")
        self.assertEqual(rules.PASSIVE_KINDS, set(SERVER_XP))

    def test_the_browser_cannot_name_one(self) -> None:
        for kind in SERVER_XP:
            with self.assertRaises(HTTPException) as caught:
                server.momentum_award(MomentumAwardRequest(kind=kind, key="python:harvest_grass"))
            self.assertEqual(caught.exception.status_code, 400, kind)

    def test_the_engines_client_entry_refuses_them_and_writes_nothing(self) -> None:
        with TempEngine() as (m, path):
            for kind in SERVER_XP:
                with self.assertRaises(UnknownKind):
                    m.award(kind, "k")
            self.assertFalse(path.exists())

    def test_the_server_entry_refuses_a_client_kind(self) -> None:
        with TempEngine() as (m, path):
            with self.assertRaises(UnknownKind):
                m.award_server("kata", "k")
            self.assertFalse(path.exists())


class TempEngine:
    """A Momentum on a throwaway file, luck off, at D0 09:00."""

    def __enter__(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory(prefix="momentum-farm-")
        self.path = Path(self._tmp.name) / "momentum.json"
        self.clock = Clock(stamp(D0))
        self.m = Momentum(self.path, clock=self.clock, rng=Stub())
        return self.m, self.path

    def __exit__(self, *exc) -> None:
        self._tmp.cleanup()


class LifetimeDedupe(EngineCase):
    def pay(self, key: str, base: int = 10, label: str = "Farm: first hay! (Python)") -> dict:
        return self.m.award_server(MILESTONE, key, base=base, label=label)

    def test_a_milestone_pays_its_own_base_and_says_what_it_was(self) -> None:
        got = self.pay("python:harvest_grass", 10, "Farm: first hay! (Python)")
        self.assertTrue(got["ok"])
        self.assertFalse(got["repeat"])
        self.assertEqual((got["base"], got["gained"]), (10, 10))
        self.assertEqual(got["label"], "Farm: first hay! (Python)")
        self.assertEqual(got["xp_total"], 10)

    def test_it_pays_once_ever_not_once_a_day(self) -> None:
        first = self.pay("python:harvest_grass")
        for n in range(1, 4):
            self.at(day(n))
            again = self.pay("python:harvest_grass")
            self.assertTrue(again["repeat"], f"day {n}")
            self.assertEqual((again["gained"], again["base"]), (0, 0))
            self.assertIsNone(again["label"])
            self.assertEqual(again["xp_total"], first["xp_total"])
        self.assertEqual(self.saved()["lifetime"][MILESTONE], 1)

    def test_the_lifetime_set_survives_a_restart_and_is_in_the_file(self) -> None:
        self.pay("python:harvest_grass")
        self.assertEqual(self.saved()["once"], [f"{MILESTONE}:python:harvest_grass"])
        other = Momentum(self.path, clock=self.clock, rng=Stub())
        self.assertTrue(other.award_server(MILESTONE, "python:harvest_grass", base=10)["repeat"])

    def test_a_different_key_pays(self) -> None:
        self.pay("python:harvest_grass")
        self.assertFalse(self.pay("javascript:harvest_grass")["repeat"])
        self.assertFalse(self.pay("python:harvest_carrot")["repeat"])

    def test_lifetime_and_per_day_dedupe_do_not_touch_each_other(self) -> None:
        # The same words as a key under a day kind are a different thing: kata is once a day.
        self.pay("python:harvest_grass")
        self.assertFalse(self.award("kata", "python:harvest_grass")["repeat"])
        self.assertTrue(self.award("kata", "python:harvest_grass")["repeat"])
        self.at(day(1))
        self.assertFalse(self.award("kata", "python:harvest_grass")["repeat"], "a day kind pays again tomorrow")
        self.assertTrue(self.pay("python:harvest_grass")["repeat"], "a first does not")
        # A milestone takes nothing from the day's keys, and a day kind nothing from the lifetime set.
        rec = self.saved()
        self.assertTrue(all(not k.startswith(MILESTONE) for d in rec["days"].values() for k in d["keys"]))
        self.assertTrue(all(k.startswith(MILESTONE) for k in rec["once"]))

    def test_a_server_award_feeds_the_combo_and_luck_like_any_other(self) -> None:
        a = self.pay("python:harvest_grass", 10)
        self.at(D0, 9, 1)
        b = self.pay("python:harvest_carrot", 10)
        c = self.award("kata", "k")
        self.assertEqual(a["combo"], 1)
        self.assertEqual((b["combo"], b["combo_mult"]), (2, 1.1))
        self.assertEqual(b["gained"], expected_pay(10, 1.1))
        self.assertEqual((c["combo"], c["gained"]), (3, expected_pay(XP["kata"], 1.2)))
        # And luck: a stub that rolls "lucky, the first multiplier" doubles the payout.
        lucky = Momentum(Path(self._tmp.name) / "lucky.json", clock=self.clock,
                         rng=Stub(randoms=(0.0,), picks=(0,)))
        got = lucky.award_server(MILESTONE, "k", base=20)
        self.assertEqual((got["lucky"], got["gained"]), (2, 40))

    def test_a_server_award_counts_for_the_streak_and_the_level(self) -> None:
        got = self.pay("python:harvest_grass", 60)
        self.assertTrue(got["streak_extended"])
        self.assertEqual(got["streak"], 1)
        self.assertEqual(got["level"], 1)
        got = self.pay("python:harvest_carrot", 60)
        self.assertEqual(got["xp_total"], 60 + expected_pay(60, 1.0 + 0.1))
        self.assertEqual(got["level"], rules.level_for(got["xp_total"]))
        self.assertIsNotNone(got["level_up"])

    def test_passive_kinds_are_not_things_solved_or_modes_used(self) -> None:
        self.pay("python:harvest_grass")
        self.m.award_server("farm_return", "2026-03-01", base=15)
        got = self.m.summary()
        stats = self.m._stats(self.m._load(), D0)
        self.assertEqual((stats.things, stats.modes), (0, 0))
        self.assertEqual(stats.fresh_kinds - rules.PASSIVE_KINDS, set())
        self.assertEqual(got["today_xp"], 10 + expected_pay(15, 1.1))  # the second is the combo's second
        # A real thing solved still counts beside them.
        self.award("kata")
        stats = self.m._stats(self.m._load(), D0)
        self.assertEqual((stats.things, stats.modes), (1, 1))

    def test_a_storage_problem_answers_not_ok_and_never_raises(self) -> None:
        blocker = Path(self._tmp.name) / "a-file"
        blocker.write_text("x", encoding="utf-8")
        broken = Momentum(blocker / "momentum.json", clock=self.clock, rng=Stub())
        self.assertEqual(broken.award_server(MILESTONE, "k", base=10), {"ok": False})
        self.assertEqual(broken.record_farm_items("python", 5, 5), {"ok": False})
        self.assertIsNone(broken.farm_visit(3))
        self.assertFalse(broken.claim_welcome()["ok"])
        broken.farm_touch()


class OldFilesStillLoad(EngineCase):
    """A momentum.json as the engine wrote it before the Farm tie-in: no `once`, no `farm`, no counters."""

    OLD = {
        "version": 1, "xp": 340, "best_streak": 3, "freezes": 0,
        "combo": {"count": 2, "last_at": 1768000000.0},
        "lifetime": {"kata": 4, "predict": 2},
        "baseline": None,
        "days": {
            (D0 - timedelta(days=2)).isoformat(): {
                "xp": 100, "awards": 3, "kinds": {"kata": 3}, "keys": ["kata:a"],
                "quests": ["solve3", "typing", "xp100"], "done": ["solve3"],
                "chest": False, "chest_xp": 0, "chest_freeze": False},
            (D0 - timedelta(days=1)).isoformat(): {
                "xp": 120, "awards": 4, "kinds": {"kata": 2, "predict": 2}, "keys": ["kata:b"],
                "quests": ["solve3", "typing", "xp100"], "done": [],
                "chest": False, "chest_xp": 0, "chest_freeze": False},
        },
    }

    def test_xp_streak_and_best_survive(self) -> None:
        self.path.write_text(json.dumps(self.OLD), encoding="utf-8")
        got = self.m.summary()
        self.assertEqual(got["xp_total"], 340)
        self.assertEqual(got["streak"], 2)  # two counted days in a row, today not yet
        self.assertFalse(got["today_counted"])
        self.assertEqual(got["best_streak"], 3)
        self.assertEqual(got["level"], rules.level_for(340))

    def test_new_things_work_on_it_and_the_file_grows_the_new_fields(self) -> None:
        self.path.write_text(json.dumps(self.OLD), encoding="utf-8")
        got = self.m.award_server(MILESTONE, "python:harvest_grass", base=10)
        self.assertEqual(got["xp_total"], 350)
        self.assertEqual(got["streak"], 3)
        self.assertTrue(self.m.award_server(MILESTONE, "python:harvest_grass", base=10)["repeat"])
        self.m.record_farm_items("python", 7, 9)
        rec = self.saved()
        self.assertEqual(rec["once"], [f"{MILESTONE}:python:harvest_grass"])
        self.assertEqual(rec["farm"]["totals"], {"python": 7})
        self.assertEqual(rec["days"][D0.isoformat()]["counters"], {"farm_items": 9})
        self.assertEqual(rec["lifetime"]["kata"], 4)  # what was there is still there
        self.assertIn("kata:a", rec["days"][(D0 - timedelta(days=2)).isoformat()]["keys"])

    def test_a_day_of_the_old_format_has_no_counters_and_quests_read_zero(self) -> None:
        self.path.write_text(json.dumps(self.OLD), encoding="utf-8")
        self.at(D0 - timedelta(days=1))
        got = self.m.summary()
        self.assertEqual([q["id"] for q in got["quests"]], ["solve3", "typing", "xp100"])

    def test_odd_new_fields_are_tolerated(self) -> None:
        bad = dict(self.OLD, once="nope", farm={"totals": [1], "last_seen": "x", "away": {"day": "never"}})
        self.path.write_text(json.dumps(bad), encoding="utf-8")
        self.assertEqual(self.m.summary()["xp_total"], 340)
        self.assertFalse(self.path.with_name("momentum.json.bad").exists())
        self.assertFalse(self.m.award_server(MILESTONE, "k", base=10)["repeat"])


def day_with(quest: str, after: int = 0) -> int:
    """The first day number (from D0) whose three quests include `quest`."""
    return next(n for n in range(after, after + 4000) if quest in rules.pick_quests(day(n)))


class FarmQuests(EngineCase):
    def test_the_pool_has_two_farm_quests_in_one_group(self) -> None:
        farm = [q for q in rules.POOL if q.group == "farm"]
        self.assertEqual({q.id for q in farm}, {"farm_items", "farm_research"})
        for n in range(500):
            ids = rules.pick_quests(day(n))
            self.assertLessEqual(sum(1 for i in ids if rules.POOL_BY_ID[i].group == "farm"), 1)
        # Both come up on some days (the pool is not accidentally never choosing them).
        self.assertTrue(any("farm_items" in rules.pick_quests(day(n)) for n in range(120)))
        self.assertTrue(any("farm_research" in rules.pick_quests(day(n)) for n in range(120)))

    def test_harvesting_50_items_completes_it_once_and_announces_it_once(self) -> None:
        self.at(day(day_with("farm_items")))
        before = self.m.summary()
        self.assertTrue(any(q["id"] == "farm_items" and q["have"] == 0 for q in before["quests"]))
        first = self.m.record_farm_items("python", 30, 30)
        self.assertIsNone(first["quest"], "30 of 50 finishes nothing")
        mid = next(q for q in self.m.summary()["quests"] if q["id"] == "farm_items")
        self.assertEqual((mid["have"], mid["need"], mid["done"]), (30, 50, False))
        second = self.m.record_farm_items("python", 20, 20)
        quest = second["quest"]
        self.assertIsNotNone(quest)
        self.assertEqual(quest["gained"], 0)
        self.assertFalse(quest["repeat"])
        done = [q for q in quest["quests"] if q["just_done"]]
        self.assertEqual([q["id"] for q in done], ["farm_items"])
        self.assertIsNone(self.m.record_farm_items("python", 99, 99)["quest"], "announced once")
        final = next(q for q in self.m.summary()["quests"] if q["id"] == "farm_items")
        self.assertEqual((final["have"], final["done"]), (50, True))  # capped at the need

    def test_the_counter_is_the_days_own_and_main_items_are_separate_from_all_items(self) -> None:
        d = day_with("farm_items")
        self.at(day(d))
        self.m.record_farm_items("python", 10, 40)
        self.at(day(d + 1))
        self.assertTrue(all(q["have"] == 0 for q in self.m.summary()["quests"]))
        rec = self.saved()
        self.assertEqual(rec["days"][day(d).isoformat()]["counters"], {"farm_items": 40})
        self.assertEqual(rec["farm"]["totals"], {"python": 10})

    def test_totals_are_per_language_and_report_either_side(self) -> None:
        a = self.m.record_farm_items("python", 60, 60)
        b = self.m.record_farm_items("original", 60, 60)
        c = self.m.record_farm_items("python", 60, 60)
        self.assertEqual((a["before"], a["after"]), (0, 60))
        self.assertEqual((b["before"], b["after"]), (0, 60))
        self.assertEqual((c["before"], c["after"]), (60, 120))
        again = Momentum(self.path, clock=self.clock, rng=Stub())
        self.assertEqual(again.record_farm_items("python", 1, 1)["before"], 120)

    def test_the_day_a_counter_starts_fixes_its_quests(self) -> None:
        self.m.record_farm_items("python", 1, 1)
        quests = self.saved()["days"][D0.isoformat()]["quests"]
        self.assertEqual(quests, rules.pick_quests(D0))
        self.assertEqual(len(quests), rules.QUESTS_PER_DAY)

    def test_harvesting_alone_does_not_count_for_the_streak(self) -> None:
        self.m.record_farm_items("python", 80, 80)
        got = self.m.summary()
        self.assertEqual((got["streak"], got["today_counted"], got["today_xp"]), (0, False, 0))

    def test_buying_research_completes_the_research_quest(self) -> None:
        self.at(day(day_with("farm_research")))
        got = self.award("farm_buy", "python:Speed:1")
        quest = next(q for q in got["quests"] if q["id"] == "farm_research")
        self.assertTrue(quest["done"] and quest["just_done"])
        # And a passive milestone does not complete it.
        self.at(day(day_with("farm_research", 40)))
        self.m.award_server(MILESTONE, "python:harvest_grass", base=10)
        quest = next(q for q in self.m.summary()["quests"] if q["id"] == "farm_research")
        self.assertFalse(quest["done"])


class WelcomeBack(EngineCase):
    """The welcome-back rules, with the clock in hand. Pay: 15, +1 per 10 ripe, at most +10."""

    @staticmethod
    def pay_for(ripe: int) -> int:
        return 15 + min(10, ripe // 10)

    def test_the_pay_formula(self) -> None:
        for ripe, want in ((0, 15), (9, 15), (10, 16), (37, 18), (99, 24), (100, 25), (101, 25), (5000, 25)):
            self.assertEqual(rules.welcome_xp(ripe), want, ripe)
            self.assertEqual(rules.welcome_xp(ripe), self.pay_for(ripe))

    def test_the_first_visit_ever_is_no_card(self) -> None:
        self.assertIsNone(self.m.farm_visit(12))
        self.assertEqual(self.saved()["farm"]["last_seen"], self.clock.t)

    def test_under_thirty_minutes_is_no_card_and_thirty_is(self) -> None:
        self.m.farm_visit(5)
        self.clock.t += 29 * 60 + 59
        self.assertIsNone(self.m.farm_visit(5))
        # ... and that look counts as the last one: measure from it.
        self.clock.t += 30 * 60
        card = self.m.farm_visit(5)
        self.assertIsNotNone(card)
        self.assertEqual(card["minutes"], 30)

    def test_the_card_says_what_is_ripe_and_what_it_is_worth(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 95 * 60
        card = self.m.farm_visit(37)
        self.assertEqual(card, {"minutes": 95, "ripe": 37, "xp": self.pay_for(37)})

    def test_claim_pays_once_a_day_through_the_normal_award(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 3 * 3600
        self.m.farm_visit(25)
        got = self.m.claim_welcome()
        self.assertTrue(got["ok"])
        self.assertEqual((got["base"], got["gained"]), (self.pay_for(25), self.pay_for(25)))
        self.assertEqual(got["label"], "Welcome back")
        self.assertEqual(got["xp_total"], self.pay_for(25))
        again = self.m.claim_welcome()
        self.assertFalse(again["ok"])
        self.assertEqual(again["reason"], "already_claimed")
        self.assertEqual(again["xp_total"], got["xp_total"])
        self.assertEqual(self.m.summary()["xp_total"], got["xp_total"])
        self.assertEqual(self.saved()["days"][D0.isoformat()]["kinds"], {"farm_return": 1})

    def test_no_pay_without_an_absence(self) -> None:
        for step in (lambda: None, lambda: self.m.farm_visit(9),
                     lambda: setattr(self.clock, "t", self.clock.t + 29 * 60) or self.m.farm_visit(9)):
            step()
            got = self.m.claim_welcome()
            self.assertFalse(got["ok"])
            self.assertEqual(got["reason"], "no_absence")
            self.assertEqual(got["gained"], 0)
        self.assertEqual(self.m.summary()["xp_total"], 0)
        self.assertFalse(self.path.exists() and self.saved()["days"], "a refused claim records nothing")

    def test_an_offer_does_not_carry_over_to_another_day(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 4 * 3600
        self.m.farm_visit(40)  # offered today, never claimed
        self.at(day(1))
        got = self.m.claim_welcome()
        self.assertEqual((got["ok"], got["reason"]), (False, "no_absence"))
        self.assertEqual(self.m.summary()["xp_total"], 0)

    def test_once_claimed_the_same_day_offers_nothing_more(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 2 * 3600
        self.m.farm_visit(3)
        self.assertTrue(self.m.claim_welcome()["ok"])
        self.clock.t += 2 * 3600
        self.assertIsNone(self.m.farm_visit(3))

    def test_the_next_day_after_an_absence_pays_again(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 2 * 3600
        self.m.farm_visit(3)
        first = self.m.claim_welcome()
        self.at(day(2))
        self.assertIsNotNone(self.m.farm_visit(10))
        second = self.m.claim_welcome()
        self.assertTrue(second["ok"])
        self.assertEqual(second["base"], self.pay_for(10))
        self.assertGreater(second["xp_total"], first["xp_total"])

    def test_the_pay_is_the_ripe_count_the_visit_recorded_not_a_later_one(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 2 * 3600
        self.m.farm_visit(60)
        self.assertEqual(self.m.claim_welcome()["base"], self.pay_for(60))

    def test_touching_keeps_the_last_look_fresh(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 2 * 3600
        self.m.farm_touch()  # the farm was on screen all that time
        self.clock.t += 5 * 60
        self.assertIsNone(self.m.farm_visit(4))

    def test_a_quiet_farm_still_pays_the_base(self) -> None:
        self.m.farm_visit(0)
        self.clock.t += 2 * 3600
        card = self.m.farm_visit(0)
        self.assertEqual((card["ripe"], card["xp"]), (0, 15))
        self.assertEqual(self.m.claim_welcome()["gained"], 15)


if __name__ == "__main__":
    unittest.main()
