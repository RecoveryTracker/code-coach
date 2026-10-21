"""Gotchas' server side: what is served and in what order, answering, the Daily 5, persistence, and the
cards the user adds ('Add a quiz I found').

The store is built over small made-up decks (so the order rules can be pinned exactly) with a held-still
clock and random source; the routes are called as plain functions, as tests/test_momentum.py does.
The oracle for the user's cards is a real run of the pasted code, done here with this file's own subprocess.
"""

from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import HTTPException

from code_coach import gotchas, momentum
from code_coach.api import server
from code_coach.api.schemas import (GotchaAnswerRequest, GotchaRunRequest, GotchaUserRequest,
                                    MomentumAwardRequest)
from code_coach.gotchas import DECKS, GotchaStore, served_options, user
from code_coach.gotchas.items import Item
from code_coach.momentum.rules import XP

NODE = shutil.which("node")


def fake_deck(n: int, language: str = "python") -> tuple[Item, ...]:
    return tuple(
        Item(id=f"t-{i}", language=language, code=f"print({i})", answer=str(i),
             wrong=(f"{i}a", f"{i}b", f"{i}c"), trap="a trap", why="Because.")
        for i in range(n))


class Held:
    """A clock that only moves when told."""

    def __init__(self, day: date = date(2026, 10, 19)) -> None:
        self.day = day

    def __call__(self) -> date:
        return self.day


class StoreCase(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp(prefix="gotchas_test_"))
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
        self.clock = Held()

    def store(self, n: int = 14, seed: int = 7) -> GotchaStore:
        return GotchaStore(self.dir / "gotchas.json", self.dir / "gotchas_user.json", clock=self.clock,
                           rng=random.Random(seed),
                           builtin=lambda lang: fake_deck(n, lang) if lang in ("python", "javascript") else ())

    @staticmethod
    def spot(store: GotchaStore, item: Item) -> int:
        return served_options(item, store.find(item.language, item.id)[1])[1]

    def play(self, store: GotchaStore, item: Item, right: bool, language: str = "python") -> dict:
        spot = self.spot(store, item)
        return store.answer(language, item.id, spot if right else (spot + 1) % 4)


# ── Serving ─────────────────────────────────────────────────────────────


class Serving(StoreCase):
    def test_the_first_two_cards_come_in_deck_order_then_it_goes_random(self) -> None:
        s = self.store()
        a, why = s.pick("python")
        self.assertEqual((a.id, why), ("t-0", "new"))
        self.play(s, a, True)
        b, _ = s.pick("python")
        self.assertEqual(b.id, "t-1")
        self.play(s, b, True)
        seen = {"t-0", "t-1"}
        for _ in range(12):
            c, why = s.pick("python")
            self.assertNotIn(c.id, seen, "an unseen card comes before any seen one")
            self.assertEqual(why, "new")
            seen.add(c.id)
            self.play(s, c, True)
        self.assertEqual(len(seen), 14)

    def test_unseen_cards_are_picked_at_random_not_in_order(self) -> None:
        orders = set()
        for seed in range(6):
            s = self.store(seed=seed)
            for item_id in ("t-0", "t-1"):
                self.play(s, s.find("python", item_id)[0], True)
            orders.add(s.pick("python")[0].id)
        self.assertGreater(len(orders), 1)

    def test_a_missed_card_comes_back_after_five_to_ten_other_answers(self) -> None:
        for seed in range(8):
            s = self.store(n=40, seed=seed)
            first, _ = s.pick("python")
            self.play(s, first, False)
            others = 0
            while True:
                nxt, why = s.pick("python")
                if nxt.id == first.id:
                    self.assertEqual(why, "again")
                    break
                self.play(s, nxt, True)
                others += 1
                self.assertLess(others, 11, "a missed card must resurface")
            self.assertGreaterEqual(others, 5)
            self.assertLessEqual(others, 10)

    def test_a_card_missed_again_is_due_again_and_one_answered_right_is_not(self) -> None:
        s = self.store(n=40)
        first, _ = s.pick("python")
        self.play(s, first, False)
        for _ in range(10):
            nxt, _ = s.pick("python")
            if nxt.id == first.id:
                break
            self.play(s, nxt, True)
        self.play(s, first, True)  # got it this time
        for _ in range(30):
            nxt, why = s.pick("python")
            self.assertNotEqual((nxt.id, why), (first.id, "again"))
            self.play(s, nxt, True)

    def test_exclude_is_honoured_and_never_leaves_nothing(self) -> None:
        s = self.store(n=4)
        for _ in range(20):
            item, _ = s.pick("python", exclude={"t-0", "t-1", "t-2"})
            self.assertNotIn(item.id, {"t-0", "t-1", "t-2"})
            self.play(s, item, True)
        item, _ = s.pick("python", exclude={"t-0", "t-1", "t-2", "t-3"})
        self.assertIn(item.id, {"t-0", "t-1", "t-2", "t-3"})

    def test_when_everything_is_seen_the_longest_ago_comes_first(self) -> None:
        s = self.store(n=6)
        for i in range(6):
            self.play(s, s.find("python", f"t-{i}")[0], True)
        item, why = s.pick("python")
        self.assertEqual((item.id, why), ("t-0", "review"))
        self.play(s, item, True)
        self.assertEqual(s.pick("python")[0].id, "t-1")

    def test_the_card_sent_to_the_browser_has_no_answer_in_it(self) -> None:
        s = self.store()
        item, _ = s.pick("python")
        card = s.present(item)
        self.assertEqual(set(card), {"id", "language", "code", "options", "mine"})
        self.assertEqual(len(card["options"]), 4)
        for secret in ("answer", "answer_index", "trap", "why", "correct"):
            self.assertNotIn(secret, card)
        self.assertNotIn("a trap", json.dumps(card))
        self.assertNotIn("Because", json.dumps(card))

    def test_languages_are_separate_decks_with_their_own_counters(self) -> None:
        s = self.store()
        py, _ = s.pick("python")
        self.play(s, py, True)
        js, _ = s.pick("javascript")
        self.assertEqual(js.id, "t-0", "JavaScript has its own first card")
        self.assertEqual(s.summary("python")["seen"], 1)
        self.assertEqual(s.summary("javascript")["seen"], 0)

    def test_unknown_things_are_refused(self) -> None:
        s = self.store()
        with self.assertRaises(gotchas.UnknownCard):
            s.pick("cobol")
        with self.assertRaises(gotchas.UnknownCard):
            s.answer("python", "nope", 0)
        with self.assertRaises(gotchas.UnknownCard):
            s.answer("cobol", "t-0", 0)
        for bad in (4, -1, 99):
            with self.assertRaises(gotchas.BadChoice):
                s.answer("python", "t-0", bad)


# ── Answering, persistence ──────────────────────────────────────────────


class Answering(StoreCase):
    def test_an_answer_updates_the_stats_and_the_streak(self) -> None:
        s = self.store()
        a = s.find("python", "t-0")[0]
        r = self.play(s, a, True)
        self.assertTrue(r["correct"])
        self.assertEqual((r["answer"], r["trap"], r["why"]), ("0", "a trap", "Because."))
        self.assertEqual((r["streak"], r["streak_best"]), (1, 1))
        self.assertEqual(r["summary"]["daily"]["total"], 5, "the summary that comes with an answer keeps the Daily 5")
        b = s.find("python", "t-1")[0]
        self.play(s, b, True)
        r = self.play(s, s.find("python", "t-2")[0], True)
        self.assertEqual((r["streak"], r["streak_best"]), (3, 3))
        r = self.play(s, s.find("python", "t-3")[0], False)
        self.assertFalse(r["correct"])
        self.assertEqual(r["answer_index"], self.spot(s, s.find("python", "t-3")[0]))
        self.assertEqual((r["streak"], r["streak_best"]), (0, 3))
        r = self.play(s, s.find("python", "t-4")[0], True)
        self.assertEqual((r["streak"], r["streak_best"]), (1, 3))
        sm = s.summary("python")
        self.assertEqual((sm["total"], sm["seen"], sm["right"], sm["streak_best"]), (14, 5, 4, 3))
        state = json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))
        stat = state["stats"]["python:t-3"]
        self.assertEqual((stat["seen"], stat["right"], stat["last_day"]), (1, 0, "2026-10-19"))
        self.assertIsNotNone(stat["due"])

    def test_it_all_survives_a_restart(self) -> None:
        s = self.store()
        for i in range(3):
            self.play(s, s.find("python", f"t-{i}")[0], i != 1)
        again = self.store()
        self.assertEqual(again.summary("python")["seen"], 3)
        self.assertEqual(again.summary("python")["right"], 2)
        self.assertEqual(again.summary("python")["streak"], 1)
        self.assertEqual(again.daily("python"), s.daily("python"))

    def test_a_broken_file_is_kept_as_bad_and_the_deck_starts_over(self) -> None:
        path = self.dir / "gotchas.json"
        path.write_text("{this is not json", encoding="utf-8")
        s = self.store()
        self.assertEqual(s.summary("python")["seen"], 0)
        bad = self.dir / "gotchas.json.bad"
        self.assertEqual(bad.read_text(encoding="utf-8"), "{this is not json")
        self.play(s, s.pick("python")[0], True)
        self.assertEqual(self.store().summary("python")["seen"], 1)
        # A file that is JSON but not a save at all is set aside the same way.
        path.write_text("[1, 2, 3]", encoding="utf-8")
        self.assertEqual(self.store().summary("python")["seen"], 0)
        self.assertEqual(bad.read_text(encoding="utf-8"), "[1, 2, 3]")

    def test_garbage_inside_a_good_file_is_tolerated(self) -> None:
        (self.dir / "gotchas.json").write_text(json.dumps({
            "stats": {"python:t-0": {"seen": "x", "right": -4, "due": True}, "junk": 5, 7: 1},
            "ticks": {"python": "many"}, "streak": {"python": 3}, "daily": {"python": {"ids": "no"}}}),
            encoding="utf-8")
        s = self.store()
        self.assertEqual(s.summary("python")["seen"], 0)
        self.assertIsNotNone(s.pick("python"))

    def test_the_progress_file_is_never_written(self) -> None:
        progress = self.dir / "progress.json"
        progress.write_text('{"keep": "me"}', encoding="utf-8")
        s = self.store()
        self.play(s, s.pick("python")[0], True)
        s.add_card("python", "print(1)", "1", ["2"], False, "Added by you", "x")
        self.assertEqual(progress.read_text(encoding="utf-8"), '{"keep": "me"}')
        self.assertEqual({p.name for p in self.dir.iterdir() if p.is_file()},
                         {"progress.json", "gotchas.json", "gotchas_user.json"})


# ── The Daily 5 ─────────────────────────────────────────────────────────


class Daily(StoreCase):
    def ids(self, s: GotchaStore, language: str = "python") -> list[str]:
        state = json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))
        return state["daily"][language]["ids"]

    def test_five_distinct_cards_the_same_all_day(self) -> None:
        s = self.store(n=30)
        d = s.daily("python")
        self.assertEqual((d["total"], d["done"], d["complete"], d["dots"]), (5, 0, False, ["todo"] * 5))
        ids = self.ids(s)
        self.assertEqual(len(set(ids)), 5)
        # Answering other cards (which moves the weights) does not change today's set.
        for i in range(10, 16):
            self.play(s, s.find("python", f"t-{i}")[0], i % 2 == 0)
        self.assertEqual(self.ids(s), ids)
        self.assertEqual(self.store(n=30, seed=99).daily("python")["total"], 5)
        self.assertEqual(self.ids(self.store(n=30)), ids)

    def test_the_set_is_decided_by_the_date_and_the_language(self) -> None:
        days = []
        for offset in range(4):
            self.clock.day = date(2026, 10, 19) + timedelta(days=offset)
            fresh = GotchaStore(self.dir / f"g{offset}.json", self.dir / "u.json", clock=self.clock,
                                builtin=lambda lang: fake_deck(40, lang))
            fresh.daily("python")
            again = GotchaStore(self.dir / f"h{offset}.json", self.dir / "u.json", clock=self.clock,
                                builtin=lambda lang: fake_deck(40, lang))
            again.daily("python")
            first = json.loads((self.dir / f"g{offset}.json").read_text(encoding="utf-8"))["daily"]["python"]["ids"]
            second = json.loads((self.dir / f"h{offset}.json").read_text(encoding="utf-8"))["daily"]["python"]["ids"]
            self.assertEqual(first, second, "same date, same history, same set")
            days.append(tuple(first))
        self.assertGreater(len(set(days)), 1, "a different date gives a different set")

    def test_a_new_day_makes_a_new_set(self) -> None:
        s = self.store(n=40)
        s.daily("python")
        today = self.ids(s)
        self.clock.day += timedelta(days=1)
        s.daily("python")
        self.assertNotEqual(self.ids(s), today)

    def test_missed_and_unseen_cards_are_favoured(self) -> None:
        picks = {"seen_right": 0, "missed": 0, "unseen": 0}
        for offset in range(60):
            self.clock.day = date(2026, 1, 1) + timedelta(days=offset)
            s = GotchaStore(self.dir / f"w{offset}.json", self.dir / "u.json", clock=self.clock,
                            builtin=lambda lang: fake_deck(30, lang))
            for i in range(10):
                self.play(s, s.find("python", f"t-{i}")[0], True)
            for i in range(10, 20):
                self.play(s, s.find("python", f"t-{i}")[0], False)
            self.clock.day += timedelta(days=1)  # next morning: the set is made from yesterday's record
            s.daily("python")
            state = json.loads((self.dir / f"w{offset}.json").read_text(encoding="utf-8"))
            for item_id in state["daily"]["python"]["ids"]:
                n = int(item_id.split("-")[1])
                picks["seen_right" if n < 10 else "missed" if n < 20 else "unseen"] += 1
        self.assertGreater(picks["missed"], picks["seen_right"] * 2)
        self.assertGreater(picks["unseen"], picks["seen_right"] * 1.5)

    def test_next_with_daily_serves_todays_unfinished_cards_then_stops(self) -> None:
        s = self.store(n=30)
        todays = set()
        for step in range(5):
            item, why = s.pick("python", daily=True)
            self.assertEqual(why, "daily")
            self.assertNotIn(item.id, todays)
            todays.add(item.id)
            r = self.play(s, item, step != 2)
            self.assertEqual(r["daily"]["done"], step + 1)
            self.assertEqual(r["daily"]["just_completed"], step == 4)
        self.assertEqual(set(self.ids(s)), todays)
        d = s.daily("python")
        self.assertTrue(d["complete"])
        self.assertEqual(d["dots"], ["right", "right", "wrong", "right", "right"])
        item, why = s.pick("python", daily=True)
        self.assertNotEqual(why, "daily", "a finished Daily 5 falls back to the normal feed")

    def test_only_the_first_answer_to_a_daily_card_counts(self) -> None:
        s = self.store(n=30)
        item, _ = s.pick("python", daily=True)
        self.play(s, item, False)
        r = self.play(s, item, True)
        self.assertEqual(r["daily"]["dots"].count("wrong"), 1)
        self.assertEqual(r["daily"]["done"], 1)
        self.assertFalse(r["daily"]["just_completed"])

    def test_a_deleted_card_leaves_the_set(self) -> None:
        s = self.store(n=3)
        d = s.daily("python")
        self.assertEqual(d["total"], 3, "a small deck gives a smaller set")


# ── The cards the user adds ─────────────────────────────────────────────


def real_output(language: str, code: str) -> str:
    """The oracle: run the code with a plain subprocess of this file's own."""
    folder = Path(tempfile.mkdtemp(prefix="gotcha_user_oracle_"))
    try:
        script = folder / ("c.py" if language == "python" else "c.js")
        script.write_text(code + "\n", encoding="utf-8")
        command = [sys.executable, str(script)] if language == "python" else [NODE, str(script)]
        done = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", cwd=folder, timeout=20)
        assert done.returncode == 0, done.stderr
        return done.stdout.strip()
    finally:
        shutil.rmtree(folder, ignore_errors=True)


ARR = "arr = [1, 2, 3]\nfor i in arr:\n    i = i * 2\nprint(arr)"
POLL = ["[2, 4, 6]", "[1, 2, 3]", "[1, 4, 9]", "Error"]


class UserCards(StoreCase):
    def make(self, code: str = ARR, options=None, guess=None, language: str = "python", why: str = ""):
        return user.build(language, code, options, guess)

    def test_the_marked_answer_is_what_the_code_really_prints(self) -> None:
        cases = [("python", ARR, None), ("python", "print(sum(range(5)), 'x' * 2)", None),
                 ("python", "print(0.1 + 0.2 == 0.3)", None), ("python", "d = {1: 2}\nprint(d[1], len(d))", None)]
        if NODE:
            cases += [("javascript", "console.log([1, 2, 3].map(n => n * 2))", None),
                      ("javascript", "console.log(typeof null)", ["undefined"])]
        for language, code, options in cases:
            built = self.make(code, options, language=language)
            self.assertEqual(built.answer, real_output(language, code), code)

    def test_a_deliberately_wrong_guess_does_not_change_the_truth(self) -> None:
        # The user thinks it is [2, 4, 6] (53% of the poll did too) and types options with no right one.
        built = self.make(ARR, ["[2, 4, 6]", "[1, 4, 9]", "Error"], guess=0)
        self.assertEqual(built.answer, real_output("python", ARR))
        self.assertEqual(built.answer, "[1, 2, 3]")
        self.assertFalse(built.matched)
        self.assertIn("None of the options you typed match what it actually prints.", built.notes)
        self.assertEqual(sorted(built.wrong), sorted(["[2, 4, 6]", "[1, 4, 9]", "Error"]))
        self.assertNotIn("[1, 2, 3]", built.wrong)

    def test_the_polls_four_options_make_a_card_whose_right_one_is_the_real_output(self) -> None:
        built = self.make(ARR, POLL, guess=0)
        self.assertTrue(built.matched)
        self.assertEqual(built.answer, "[1, 2, 3]")
        self.assertEqual(sorted(built.wrong), ["Error", "[1, 4, 9]", "[2, 4, 6]"])
        self.assertEqual(built.notes, ["Your pick was not what it prints."])
        self.assertEqual(self.make(ARR, POLL, guess=1).notes, ["Your pick was right."])

    def test_four_wrong_options_lose_the_one_the_user_guessed(self) -> None:
        built = self.make(ARR, ["[2, 4, 6]", "[1, 4, 9]", "Error", "None"], guess=3)
        self.assertEqual(built.answer, "[1, 2, 3]")
        self.assertEqual(sorted(built.wrong), ["Error", "[1, 4, 9]", "[2, 4, 6]"])
        self.assertIn("The real output took the place of one of your options.", built.notes)

    def test_blank_options_are_filled_only_with_honest_misreads(self) -> None:
        built = self.make(ARR)
        self.assertEqual(built.answer, "[1, 2, 3]")
        self.assertEqual(built.wrong, ["[1, 2]", "[2, 3]"], "the same list with the last / first item dropped")
        self.assertEqual(self.make("print(3 > 2)").wrong, ["False"])
        self.assertEqual(self.make("print(7)").wrong, ["8", "6"])
        self.assertEqual(self.make("print('a b c')").wrong, ["a b", "b c"])
        lines = self.make("print(1)\nprint(2)\nprint(3)")
        self.assertEqual(lines.wrong, ["1", "1\n2"])
        self.assertEqual(self.make("print([[1, 2], [3]])").wrong, ["[[1, 2]]", "[[3]]"])
        if NODE:
            self.assertEqual(self.make("console.log([1, 2, 3])", language="javascript").wrong,
                             ["[ 1, 2 ]", "[ 2, 3 ]"])

    def test_no_honest_misread_means_no_card_rather_than_a_made_up_one(self) -> None:
        with self.assertRaises(user.CardRefused) as ctx:
            self.make("print('hello')")
        self.assertIn("at least one other option", str(ctx.exception))
        built = self.make("print('hello')", ["hullo"])
        self.assertEqual((built.answer, built.wrong), ("hello", ["hullo"]))

    def test_whitespace_and_typed_duplicates_do_not_count_as_different_options(self) -> None:
        built = self.make(ARR, ["[1,  2, 3]", "[1, 2, 3]", "[2, 4, 6]"])
        self.assertTrue(built.matched)
        self.assertEqual(built.wrong, ["[2, 4, 6]", "[1, 2]", "[2, 3]"][:3])

    def test_a_program_that_fails_straight_away_becomes_an_error_card(self) -> None:
        built = self.make("print(missing_name)", ["0", "None"])
        self.assertEqual((built.answer, built.raises), ("NameError", True))

    def test_refusals_say_why(self) -> None:
        cases = {
            "": "nothing to run",
            "   \n  ": "nothing to run",
            "\n".join(f"x{i} = {i}" for i in range(61)) + "\nprint(x1)": "too long",
            "print(1)\n" * 5 + "pass #" + "x" * 4000: "too long",
            "name = input()\nprint(name)": "waits for input",
            "import random\nprint(random.random())": "different each time",
            "x = 1": "printed nothing",
            "print('a')\nraise ValueError('x')": "after printing",
            "def f(:\n  pass": "stopped with an error",
        }
        for code, expected in cases.items():
            with self.assertRaises(user.CardRefused, msg=code[:30]) as ctx:
                self.make(code)
            self.assertIn(expected, str(ctx.exception), code[:30])

    def test_a_program_that_runs_too_long_is_stopped_and_refused(self) -> None:
        import time

        started = time.monotonic()
        with self.assertRaises(user.CardRefused) as ctx:
            self.make("while True:\n    pass")
        self.assertIn("longer than 5 seconds", str(ctx.exception))
        self.assertLess(time.monotonic() - started, 9, "a program that never ends is run once, not twice")

    def test_too_much_output_is_refused(self) -> None:
        with self.assertRaises(user.CardRefused):
            self.make("for i in range(20):\n    print(i)")
        with self.assertRaises(user.CardRefused):
            self.make("print('x' * 400)")

    def test_a_card_is_saved_served_and_deleted(self) -> None:
        s = self.store()
        built = self.make(ARR, POLL, guess=0)
        item = s.add_card("python", ARR, built.answer, built.wrong, built.raises, "Added by you",
                          user.why_text(built.answer, built.raises, ""))
        self.assertTrue(item.mine and item.id.startswith("mine-"))
        self.assertEqual(item.why, "Added by you - it printed [1, 2, 3]")
        self.assertEqual(s.summary("python")["total"], 15)
        self.assertEqual(s.summary("python")["mine"], 1)
        self.assertEqual(s.summary("javascript")["mine"], 0)
        # Prioritised: the very next card, once.
        nxt, why = s.pick("python")
        self.assertEqual((nxt.id, why), (item.id, "yours"))
        card = s.present(nxt)
        self.assertTrue(card["mine"])
        for secret in ("answer", "answer_index", "trap", "why"):
            self.assertNotIn(secret, card)
        r = self.play(s, nxt, True)
        self.assertEqual((r["answer"], r["mine"]), ("[1, 2, 3]", True))
        self.assertNotEqual(s.pick("python")[1], "yours")
        # And it survives a restart, then goes away for good when deleted.
        again = self.store()
        self.assertEqual([c.id for c in again.my_cards("python")], [item.id])
        self.assertTrue(again.delete_card("python", item.id))
        self.assertEqual(self.store().my_cards(), [])
        self.assertNotIn(f"python:{item.id}", json.loads((self.dir / "gotchas.json").read_text())["stats"])
        self.assertFalse(again.delete_card("python", item.id))

    def test_a_built_in_card_cannot_be_deleted_and_user_ids_are_not_reused(self) -> None:
        s = self.store()
        self.assertFalse(s.delete_card("python", "t-0"))
        a = s.add_card("python", "print(1)", "1", ["2"], False, "Added by you", "x")
        s.delete_card("python", a.id)
        b = s.add_card("python", "print(1)", "1", ["2"], False, "Added by you", "x")
        self.assertNotEqual(a.id, b.id)

    def test_a_broken_user_file_is_kept_as_bad(self) -> None:
        (self.dir / "gotchas_user.json").write_text("nonsense", encoding="utf-8")
        s = self.store()
        self.assertEqual(s.my_cards(), [])
        self.assertEqual((self.dir / "gotchas_user.json.bad").read_text(encoding="utf-8"), "nonsense")
        s.add_card("python", "print(1)", "1", ["2"], False, "Added by you", "x")
        self.assertEqual(len(self.store().my_cards()), 1)

    def test_your_cards_never_reach_the_built_in_content(self) -> None:
        s = self.store()
        s.add_card("python", "print(1)", "1", ["2"], False, "Added by you", "x")
        for deck in DECKS.values():
            self.assertFalse(any(it.mine or it.id.startswith("mine-") for it in deck))

    def test_a_very_wrong_saved_card_cannot_be_loaded(self) -> None:
        (self.dir / "gotchas_user.json").write_text(json.dumps({"next": 3, "cards": [
            {"id": "mine-1", "language": "python", "code": "print(1)", "answer": "1", "wrong": []},
            {"id": "mine-2", "language": "cobol", "code": "x", "answer": "1", "wrong": ["2"]},
            {"id": "mine-3", "language": "python", "code": "print(1)", "answer": "1", "wrong": ["2"]},
        ]}), encoding="utf-8")
        self.assertEqual([c.id for c in self.store().my_cards()], ["mine-3"])


# ── The routes ──────────────────────────────────────────────────────────


class Routes(unittest.TestCase):
    def status(self, call, *args, **kw) -> int:
        try:
            call(*args, **kw)
        except HTTPException as exc:
            return exc.status_code
        return 200

    def test_the_whole_loop_over_the_routes(self) -> None:
        summary = server.gotchas_summary("python")
        self.assertEqual((summary["total"], summary["seen"], summary["title"]), (len(DECKS["python"]), 0, "Python Quiz"))
        self.assertEqual(server.gotchas_summary("javascript")["title"], "JavaScript Quiz")
        first = server.gotchas_next("python")
        self.assertEqual(first["id"], "py-score-90")
        self.assertEqual(first["options"], ["A", "B", "C", "D"])
        for secret in ("answer", "answer_index", "trap", "why"):
            self.assertNotIn(secret, first)
        got = server.gotchas_answer(GotchaAnswerRequest(id="py-score-90", language="python", chosen=3))
        self.assertTrue(got["correct"])
        self.assertEqual((got["answer"], got["streak"]), ("D", 1))
        second = server.gotchas_next("python", exclude="py-score-90")
        self.assertEqual(second["id"], "py-loop-var-list")
        self.assertEqual(server.gotchas_summary("python")["seen"], 1)
        # Run it: the card's own program, run for real.
        ran = server.gotchas_run(GotchaRunRequest(id="py-loop-var-list", language="python"))
        self.assertEqual(ran["stdout"], "[1, 2, 3]")
        self.assertEqual(ran["error"], "")

    def test_run_it_on_an_error_card_shows_the_error_without_the_temp_path(self) -> None:
        ran = server.gotchas_run(GotchaRunRequest(id="py-unbound-local", language="python"))
        self.assertEqual(ran["stdout"], "")
        self.assertIn("UnboundLocalError", ran["error"])
        self.assertNotIn("gotcha_run_", ran["error"])
        self.assertIn("snippet.py", ran["error"])

    @pytest.mark.skipif(NODE is None, reason="needs node")
    def test_run_it_for_javascript_including_the_event_loop(self) -> None:
        ran = server.gotchas_run(GotchaRunRequest(id="js-microtask-before-timeout", language="javascript"))
        self.assertEqual(ran["stdout"], "sync promise timeout")

    def test_unknown_ids_languages_and_choices_are_400(self) -> None:
        self.assertEqual(self.status(server.gotchas_summary, "cobol"), 400)
        self.assertEqual(self.status(server.gotchas_next, "cobol"), 400)
        self.assertEqual(self.status(server.gotchas_answer,
                                     GotchaAnswerRequest(id="nope", language="python", chosen=0)), 400)
        self.assertEqual(self.status(server.gotchas_answer,
                                     GotchaAnswerRequest(id="py-score-90", language="cobol", chosen=0)), 400)
        self.assertEqual(self.status(server.gotchas_answer,
                                     GotchaAnswerRequest(id="py-score-90", language="python", chosen=7)), 400)
        self.assertEqual(self.status(server.gotchas_answer,
                                     GotchaAnswerRequest(id="js-typeof-null", language="python", chosen=0)), 400)
        self.assertEqual(self.status(server.gotchas_run, GotchaRunRequest(id="nope", language="python")), 400)
        self.assertEqual(self.status(server.gotchas_user_delete, "py-score-90", "python"), 400)
        self.assertEqual(self.status(server.gotchas_user_list, "cobol"), 400)

    def test_a_user_card_end_to_end_with_the_polls_example(self) -> None:
        # Without options: the card has the real output and two honest misreads.
        added = server.gotchas_user_add(GotchaUserRequest(language="python", code=ARR))
        self.assertTrue(added["saved"])
        self.assertEqual(added["answer"], "[1, 2, 3]")
        self.assertEqual(sorted(added["options"]), ["[1, 2, 3]", "[1, 2]", "[2, 3]"])
        # With the poll's four options and a wrong guess.
        wrong = server.gotchas_user_add(GotchaUserRequest(
            language="python", code=ARR, options=["[2, 4, 6]", "[1, 4, 9]", "Error"], guess=0,
            why="Poll: 53% said [2, 4, 6]"))
        self.assertEqual(wrong["answer"], "[1, 2, 3]")
        self.assertIn("None of the options you typed match what it actually prints.", wrong["notes"])
        four = server.gotchas_user_add(GotchaUserRequest(language="python", code=ARR, options=POLL, guess=1))
        self.assertTrue(four["matched"])
        listed = server.gotchas_user_list("python")["cards"]
        self.assertEqual([c["id"] for c in listed], [added["id"], wrong["id"], four["id"]])
        # Served in the feed with its badge flag, answer withheld.
        nxt = server.gotchas_next("python")
        self.assertEqual(nxt["id"], added["id"])
        self.assertTrue(nxt["mine"] and nxt["why_picked"] == "yours")
        for secret in ("answer", "answer_index", "trap", "why"):
            self.assertNotIn(secret, nxt)
        ans = server.gotchas_answer(GotchaAnswerRequest(
            id=nxt["id"], language="python", chosen=nxt["options"].index("[1, 2, 3]")))
        self.assertTrue(ans["correct"] and ans["mine"])
        self.assertEqual(ans["trap"], "Added by you")
        self.assertEqual(server.gotchas_summary("python")["mine"], 3)
        # Run it works for a user card too, and delete removes it.
        self.assertEqual(server.gotchas_run(GotchaRunRequest(id=wrong["id"], language="python"))["stdout"],
                         "[1, 2, 3]")
        self.assertEqual(server.gotchas_user_delete(wrong["id"], "python")["deleted"], wrong["id"])
        self.assertEqual(self.status(server.gotchas_user_delete, wrong["id"], "python"), 400)
        self.assertEqual(self.status(server.gotchas_run, GotchaRunRequest(id=wrong["id"], language="python")), 400)

    def test_preview_runs_but_saves_nothing(self) -> None:
        got = server.gotchas_user_preview(GotchaUserRequest(language="python", code=ARR, options=POLL, guess=0))
        self.assertFalse(got["saved"])
        self.assertEqual(got["answer"], "[1, 2, 3]")
        self.assertEqual(server.gotchas_user_list("")["cards"], [])

    def test_user_refusals_are_400_with_a_reason(self) -> None:
        for body in (GotchaUserRequest(language="python", code=""),
                     GotchaUserRequest(language="cobol", code="print(1)"),
                     GotchaUserRequest(language="python", code="x = 1"),
                     GotchaUserRequest(language="python", code="print('a')", options=["b" * 300]),
                     GotchaUserRequest(language="python", code="\n".join(["pass"] * 70))):
            with self.assertRaises(HTTPException) as ctx:
                server.gotchas_user_add(body)
            self.assertEqual(ctx.exception.status_code, 400)
            self.assertTrue(str(ctx.exception.detail).strip())
        self.assertEqual(server.gotchas_user_list("")["cards"], [])

    def test_user_cards_stay_per_language(self) -> None:
        server.gotchas_user_add(GotchaUserRequest(language="python", code="print(3)"))
        self.assertEqual(len(server.gotchas_user_list("python")["cards"]), 1)
        self.assertEqual(server.gotchas_user_list("javascript")["cards"], [])
        self.assertEqual(server.gotchas_summary("javascript")["mine"], 0)

    def test_the_daily_over_the_routes_and_its_award(self) -> None:
        summary = server.gotchas_summary("python")
        self.assertEqual(summary["daily"]["total"], 5)
        done = None
        for step in range(5):
            card = server.gotchas_next("python", daily=True)
            self.assertEqual(card["why_picked"], "daily")
            done = server.gotchas_answer(GotchaAnswerRequest(
                id=card["id"], language="python", chosen=0))["daily"]
        self.assertTrue(done["complete"] and done["just_completed"])
        self.assertTrue(server.gotchas_summary("python")["daily"]["complete"])
        key = f"daily:python:{done['day']}"
        got = server.momentum_award(MomentumAwardRequest(kind="gotcha_daily", key=key))
        self.assertTrue(got["ok"])
        self.assertGreater(got["gained"], 0)
        again = server.momentum_award(MomentumAwardRequest(kind="gotcha_daily", key=key))
        self.assertEqual(again.get("gained", 0), 0, "the Daily 5 pays once a day per language")


class Momentum(unittest.TestCase):
    def test_both_kinds_are_priced_and_a_card_pays_once_a_day(self) -> None:
        self.assertEqual(XP["gotcha"], 12)
        self.assertEqual(XP["gotcha_daily"], 30)
        key = "gotcha:python:py-score-90"
        first = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=key))
        self.assertTrue(first["ok"])
        self.assertGreater(first["gained"], 0)
        again = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=key))
        self.assertEqual(again["gained"], 0)
        other = server.momentum_award(MomentumAwardRequest(kind="gotcha", key="gotcha:javascript:js-typeof-null"))
        self.assertGreater(other["gained"], 0)
        self.assertEqual(momentum.rules.XP["gotcha"], 12)


def test_the_screen_awards_with_the_keys_the_server_dedupes_on():
    text = (Path(__file__).resolve().parent.parent / "web" / "src" / "components" / "Gotchas.tsx").read_text(
        encoding="utf-8")
    # The keys come from lib/gotchas.ts (tested in test_gotchas_ts.py to read gotcha:<language>:<id> and
    # daily:<language>:<date>); here: the screen sends the right kinds with them, only on a right answer.
    assert re.search(r'if \(r\.correct\) award\("gotcha", cardAwardKey\(', text)
    assert re.search(r'if \(r\.daily\.just_completed\) award\("gotcha_daily", dailyAwardKey\(', text)
