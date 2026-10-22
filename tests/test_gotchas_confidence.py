"""Gotchas: how sure you were, your own reasoning, and My traps (server side).

The store is built over the same small made-up decks as tests/test_gotchas_store.py. The expectations are the
rules written down in `gotchas/store.py` and CLAUDE.md, worked out here by hand:

* a miss comes back 5-10 answers later; a miss you were SURE about 2-4 later and ahead of the other due cards;
  a right answer you only GUESSED ("shaky") once, 10-20 later;
* a note is trimmed, cut to 300 characters, and the last 3 are kept per card with their day and verdict;
* a trap is a card answered wrong at least once whose last two answers are not both right-and-Sure, and only
  ever a card that has been answered.

The browser-side half (keys, wording, sorting helpers) is in tests/test_gotchas_ts.py.
"""

from __future__ import annotations

import json
import shutil
import unittest
from datetime import timedelta

from fastapi import HTTPException

from code_coach import gotchas
from code_coach.api import server
from code_coach.api.schemas import GotchaAnswerRequest, GotchaUserRequest
from code_coach.gotchas import DECKS, served_options
from code_coach.gotchas.store import NOTE_MAX, RETURNS, return_offset, sort_traps
from tests.test_gotchas_store import StoreCase

NODE = shutil.which("node")


class Base(StoreCase):
    def play(self, store, item, right, language="python", confidence="", note=""):  # type: ignore[override]
        spot = self.spot(store, item)
        return store.answer(language, item.id, spot if right else (spot + 1) % 4,
                            confidence=confidence, note=note)

    def card(self, store, i: int):
        return store.find("python", f"t-{i}")[0]

    def stats(self) -> dict:
        return json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))["stats"]

    def due_in(self, i: int, language: str = "python") -> int:
        """How many answers after the last one this card is due, read from the saved file."""
        state = json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))
        return state["stats"][f"{language}:t-{i}"]["due"] - state["ticks"][language]

    def others_until_back(self, s, first, limit: int = 30) -> int:
        """Answer other cards (right, no claim about confidence) until `first` is served again; count them."""
        others = 0
        while True:
            nxt, why = s.pick("python")
            if nxt.id == first.id:
                self.assertEqual(why, "again")
                return others
            self.play(s, nxt, True)
            others += 1
            self.assertLess(others, limit, "the card must resurface")


class Recording(Base):
    def test_confidence_is_counted_per_card_and_the_old_fields_stay(self) -> None:
        s = self.store()
        a = self.card(s, 0)
        self.play(s, a, True, confidence="sure")
        self.play(s, a, True, confidence="guess")
        self.play(s, a, False, confidence="sure")
        self.play(s, a, False, confidence="guess")
        self.play(s, a, False)  # no claim
        st = self.stats()["python:t-0"]
        self.assertEqual((st["sure_right"], st["guess_right"], st["sure_wrong"], st["guess_wrong"]), (1, 1, 1, 1))
        self.assertEqual((st["seen"], st["right"]), (5, 2), "seen and right keep counting every answer")
        self.assertEqual(st["last_day"], "2026-10-19")

    def test_the_answer_says_how_sure_you_were_and_whether_it_will_come_back(self) -> None:
        s = self.store()
        r = self.play(s, self.card(s, 0), False, confidence="sure")
        self.assertEqual((r["confidence"], r["comes_back"], r["again_soon"], r["correct"]), ("sure", True, True, False))
        r = self.play(s, self.card(s, 1), True, confidence="sure")
        self.assertEqual((r["confidence"], r["comes_back"], r["again_soon"]), ("sure", False, False))
        r = self.play(s, self.card(s, 2), True, confidence="guess")
        self.assertEqual((r["confidence"], r["comes_back"], r["again_soon"]), ("guess", True, False),
                         "again_soon is still 'you missed it'; comes_back is the new, wider idea")

    def test_anything_but_sure_or_guess_is_no_claim_at_all(self) -> None:
        for junk in ("SURE", "Guess", " sure", "maybe", 5, None, True, ["sure"], {"x": 1}, ""):
            with self.subTest(junk=junk):
                s = self.store()
                a = self.card(s, 0)
                r = self.play(s, a, False, confidence=junk)
                self.assertEqual(r["confidence"], "")
                st = self.stats()["python:t-0"]
                self.assertEqual((st["sure_right"], st["sure_wrong"], st["guess_right"], st["guess_wrong"]),
                                 (0, 0, 0, 0))
                self.assertIn(self.due_in(0), range(5, 11), "unclaimed means an ordinary miss")
                (self.dir / "gotchas.json").unlink()

    def test_an_old_file_without_any_of_it_loads_and_keeps_working(self) -> None:
        (self.dir / "gotchas.json").write_text(json.dumps({
            "version": 1,
            "stats": {"python:t-0": {"seen": 2, "right": 1, "last_day": "2026-10-01", "last_tick": 3, "due": 4},
                      "python:t-1": {"seen": 1, "right": 1, "last_day": "2026-10-02", "last_tick": 2, "due": None}},
            "ticks": {"python": 5}, "streak": {"python": {"now": 1, "best": 2}}, "daily": {}}), encoding="utf-8")
        s = self.store()
        self.assertEqual(s.summary("python")["seen"], 2)
        item, why = s.pick("python")
        self.assertEqual((item.id, why), ("t-0", "again"), "an old due card is still due, as a plain miss")
        [t] = s.traps(["python"])
        self.assertEqual((t["id"], t["misses"], t["sure_wrong"], t["shaky"], t["note"]), ("t-0", 1, 0, False, ""))
        r = self.play(s, item, True, confidence="sure")
        self.assertTrue(r["correct"])
        st = self.stats()["python:t-0"]
        self.assertEqual((st["seen"], st["right"], st["sure_right"], st["notes"]), (3, 2, 1, []))

    def test_garbage_in_the_new_fields_is_tolerated(self) -> None:
        (self.dir / "gotchas.json").write_text(json.dumps({"stats": {"python:t-0": {
            "seen": 3, "right": 1, "due": 9, "due_kind": "nonsense", "sure_wrong": "x", "sure_run": -3,
            "note": 12, "notes": [5, {"note": "  ", "day": 1}, {"note": "ok", "day": "d", "correct": 1}, None]}},
            "ticks": {"python": 1}}), encoding="utf-8")
        s = self.store()
        [t] = s.traps(["python"])
        self.assertEqual((t["note"], t["sure_wrong"]), ("ok", 0))
        self.assertIsNotNone(s.pick("python"))


class Scheduling(Base):
    def test_offsets_stay_inside_their_ranges_and_use_all_of_them(self) -> None:
        self.assertEqual(RETURNS, {"miss": (5, 10), "sure_wrong": (2, 4), "shaky": (10, 20)})
        for kind, want in (("miss", set(range(5, 11))), ("sure_wrong", {2, 3, 4}), ("shaky", set(range(10, 21)))):
            seen = {return_offset(kind, f"python:t-{c}", tick) for c in range(40) for tick in range(1, 60)}
            self.assertEqual(seen, want, kind)

    def test_a_sure_and_wrong_card_comes_back_after_two_to_four_answers(self) -> None:
        counts = set()
        for seed in range(12):
            s = self.store(n=60, seed=seed)
            first, _ = s.pick("python")
            self.play(s, first, False, confidence="sure")
            self.assertIn(self.due_in(int(first.id[2:])), (2, 3, 4))
            n = self.others_until_back(s, first)
            self.assertIn(n, (2, 3, 4))
            counts.add(n)
        self.assertGreater(len(counts), 1, "it is spread, not always the same")

    def test_a_wrong_guess_or_no_claim_is_the_ordinary_miss_of_five_to_ten(self) -> None:
        for confidence in ("guess", ""):
            for seed in range(6):
                s = self.store(n=60, seed=seed)
                first, _ = s.pick("python")
                self.play(s, first, False, confidence=confidence)
                n = self.others_until_back(s, first)
                self.assertTrue(5 <= n <= 10, f"{confidence!r}: {n}")

    def test_a_right_answer_you_guessed_comes_back_once_ten_to_twenty_answers_later(self) -> None:
        counts = set()
        for seed in range(10):
            s = self.store(n=80, seed=seed)
            first, _ = s.pick("python")
            r = self.play(s, first, True, confidence="guess")
            self.assertTrue(r["correct"])
            self.assertIn(self.due_in(int(first.id[2:])), range(10, 21))
            n = self.others_until_back(s, first, limit=40)
            self.assertTrue(10 <= n <= 20, n)
            counts.add(n)
            # Answered right and Sure, it is done like any right card: it never comes back "again".
            self.play(s, first, True, confidence="sure")
            self.assertIsNone(self.stats()[f"python:{first.id}"]["due"])
            for _ in range(25):
                nxt, why = s.pick("python")
                self.assertNotEqual((nxt.id, why), (first.id, "again"))
                self.play(s, nxt, True)
        self.assertGreater(len(counts), 1)

    def test_a_guessed_right_card_answered_with_a_guess_again_is_still_shaky(self) -> None:
        s = self.store(n=80)
        a = self.card(s, 0)
        self.play(s, a, True, confidence="guess")
        self.play(s, a, True, confidence="guess")
        self.assertIn(self.due_in(0), range(10, 21))
        self.play(s, a, True)  # right with no claim: plain right, done
        self.assertIsNone(self.stats()["python:t-0"]["due"])

    def test_a_wrong_answer_beats_shaky_and_a_sure_miss_is_sooner_than_a_guessed_one(self) -> None:
        s = self.store(n=80)
        a = self.card(s, 0)
        self.play(s, a, True, confidence="guess")
        self.play(s, a, False, confidence="sure")
        self.assertIn(self.due_in(0), (2, 3, 4))
        self.assertEqual(self.stats()["python:t-0"]["due_kind"], "sure_wrong")

    def test_among_due_cards_the_sure_and_wrong_one_goes_first_whatever_its_date(self) -> None:
        def pick_with(kinds: dict[str, tuple[str, int]]) -> str:
            stats = {f"python:{cid}": {"seen": 2, "right": 0 if kind != "shaky" else 2, "last_day": "2026-10-19",
                                       "last_tick": 1, "due": due, "due_kind": kind, "sure_wrong": 1 if kind == "sure_wrong" else 0}
                     for cid, (kind, due) in kinds.items()}
            (self.dir / "gotchas.json").write_text(json.dumps(
                {"stats": stats, "ticks": {"python": 30}}), encoding="utf-8")
            return self.store(n=20).pick("python")[0].id

        # t-2 was due long ago, t-3 only just: the sure-and-wrong t-3 still goes first.
        self.assertEqual(pick_with({"t-0": ("miss", 31), "t-1": ("miss", 31),
                                    "t-2": ("miss", 3), "t-3": ("sure_wrong", 29)}), "t-3")
        # Two ordinary misses: the one due earlier first (as before).
        self.assertEqual(pick_with({"t-0": ("miss", 12), "t-1": ("miss", 31), "t-2": ("miss", 3),
                                    "t-3": ("miss", 9)}), "t-2")
        # Shaky cards wait behind a due ordinary miss, but still come back.
        self.assertEqual(pick_with({"t-0": ("miss", 31), "t-1": ("miss", 31), "t-2": ("shaky", 3),
                                    "t-3": ("miss", 29)}), "t-3")
        self.assertEqual(pick_with({"t-0": ("miss", 31), "t-1": ("miss", 31), "t-2": ("shaky", 3)}), "t-2")

    def test_scoring_and_streaks_are_the_same_whatever_you_claimed(self) -> None:
        runs = []
        for confidence in ("", "sure", "guess", "nonsense"):
            (self.dir / "gotchas.json").unlink(missing_ok=True)
            s = self.store()
            trail = []
            for i, right in enumerate((True, True, False, True)):
                r = self.play(s, self.card(s, i), right, confidence=confidence)
                trail.append((r["correct"], r["streak"], r["streak_best"], r["seen_before"]))
            runs.append((trail, s.summary("python")["seen"], s.summary("python")["right"]))
        self.assertTrue(all(run == runs[0] for run in runs))

    def test_an_exclude_on_the_card_just_answered_is_still_honoured(self) -> None:
        s = self.store(n=60)
        first, _ = s.pick("python")
        self.play(s, first, False, confidence="sure")
        for _ in range(4):
            item, _ = s.pick("python", exclude={first.id})
            self.assertNotEqual(item.id, first.id)
            self.play(s, item, True)


class Notes(Base):
    def test_a_note_is_trimmed_capped_and_never_changes_the_scoring(self) -> None:
        s = self.store()
        plain = self.play(s, self.card(s, 0), True, confidence="sure")
        withnote = self.play(s, self.card(s, 1), True, confidence="sure", note="  I read it top to bottom  ")
        self.assertEqual(withnote["note"], "I read it top to bottom")
        self.assertEqual(plain["note"], "")
        same = ("correct", "again_soon", "comes_back", "confidence", "trap", "why", "mine")
        self.assertEqual({k: plain[k] for k in same}, {k: withnote[k] for k in same},
                         "a note changes nothing about the verdict or when the card comes back")
        self.assertEqual((plain["correct"], withnote["correct"], plain["again_soon"], withnote["again_soon"]),
                         (True, True, False, False))
        self.assertEqual(self.stats()["python:t-1"]["note"], "I read it top to bottom")

    def test_the_cap_is_300_characters_after_trimming(self) -> None:
        s = self.store()
        self.play(s, self.card(s, 0), False, note="x" * 500)
        self.assertEqual(self.stats()["python:t-0"]["note"], "x" * NOTE_MAX)
        self.play(s, self.card(s, 1), False, note="  " + "y" * 299 + "   z" * 10)
        stored = self.stats()["python:t-1"]["note"]
        self.assertLessEqual(len(stored), NOTE_MAX)
        self.assertEqual(stored, stored.strip())
        self.assertTrue(stored.startswith("y" * 299))

    def test_only_the_last_three_notes_are_kept_with_their_day_and_verdict(self) -> None:
        s = self.store()
        a = self.card(s, 0)
        plan = [("one", False), ("two", True), ("three", False), ("four", True)]
        for day, (text, right) in enumerate(plan):
            self.clock.day = self.clock.day.replace(day=19 + day)
            self.play(s, a, right, note=text)
        st = self.stats()["python:t-0"]
        self.assertEqual(st["note"], "four")
        self.assertEqual(st["notes"], [{"day": "2026-10-20", "note": "two", "correct": True},
                                       {"day": "2026-10-21", "note": "three", "correct": False},
                                       {"day": "2026-10-22", "note": "four", "correct": True}])

    def test_no_note_or_an_empty_or_odd_one_stores_nothing_and_keeps_the_last(self) -> None:
        s = self.store()
        a = self.card(s, 0)
        self.play(s, a, False, note="first")
        for junk in ("", "   \n ", None, 7, ["x"], {"a": 1}):
            self.play(s, a, False, note=junk)
        st = self.stats()["python:t-0"]
        self.assertEqual((st["note"], [n["note"] for n in st["notes"]]), ("first", ["first"]))

    def test_notes_survive_a_restart(self) -> None:
        s = self.store()
        self.play(s, self.card(s, 0), False, confidence="sure", note="I thought it printed 0")
        [t] = self.store().traps(["python"])
        self.assertEqual((t["note"], t["sure_wrong"]), ("I thought it printed 0", 1))


class Traps(Base):
    def ids(self, s, languages=("python",)) -> list[str]:
        return [t["id"] for t in s.traps(list(languages))]

    def test_only_a_card_missed_at_least_once_is_a_trap_and_never_one_unanswered(self) -> None:
        s = self.store(n=30)
        self.assertEqual(s.traps(["python"]), [])
        self.play(s, self.card(s, 0), True, confidence="sure")   # never missed
        self.play(s, self.card(s, 1), False)                     # missed
        self.assertEqual(self.ids(s), ["t-1"])
        listed = {t["id"] for t in s.traps(["python"])}
        self.assertTrue(listed.isdisjoint({f"t-{i}" for i in range(2, 30)}), "nothing unanswered is ever listed")

    def test_mastered_means_the_last_two_answers_right_and_marked_sure(self) -> None:
        s = self.store(n=30)
        a = self.card(s, 0)
        self.play(s, a, False, confidence="sure")
        self.assertEqual(self.ids(s), ["t-0"])
        self.play(s, a, True, confidence="sure")
        self.assertEqual(self.ids(s), ["t-0"], "one right-and-sure answer is not yet mastered")
        self.play(s, a, True, confidence="guess")
        self.play(s, a, True, confidence="sure")
        self.assertEqual(self.ids(s), ["t-0"], "a guess in between breaks the run")
        self.play(s, a, True)
        self.play(s, a, True, confidence="sure")
        self.assertEqual(self.ids(s), ["t-0"], "right with no claim is not 'sure'")
        self.play(s, a, True, confidence="sure")
        self.assertEqual(self.ids(s), [], "two right-and-sure in a row: mastered")
        self.play(s, a, False, confidence="guess")
        self.assertEqual(self.ids(s), ["t-0"], "and a new miss puts it back")
        self.assertEqual(s.traps(["python"])[0]["misses"], 2)

    def test_the_listing_carries_what_the_panel_shows(self) -> None:
        s = self.store(n=30)
        a = self.card(s, 4)
        self.play(s, a, False, confidence="sure", note="I assumed a copy")
        self.play(s, a, True, confidence="guess")
        [t] = s.traps(["python"])
        self.assertEqual(t, {
            "id": "t-4", "language": "python", "language_name": "Python", "title": "4", "code": "print(4)",
            "trap": "a trap", "why": "Because.", "mine": False, "misses": 1, "sure_wrong": 1, "guess_wrong": 0,
            "shaky": True, "note": "I assumed a copy", "last_day": "2026-10-19", "last_tick": 2})

    def test_shaky_only_while_the_last_answer_was_a_right_guess(self) -> None:
        s = self.store(n=30)
        a = self.card(s, 0)
        self.play(s, a, False)
        self.assertFalse(s.traps(["python"])[0]["shaky"])
        self.play(s, a, True, confidence="guess")
        self.assertTrue(s.traps(["python"])[0]["shaky"])
        self.play(s, a, True, confidence="sure")
        self.assertFalse(s.traps(["python"])[0]["shaky"])

    def test_sure_but_wrong_first_then_most_misses_then_most_recent(self) -> None:
        s = self.store(n=30)
        # t-1: missed once (guess); t-2: missed 3 times (guess); t-3: missed once, sure; t-4: missed once (guess),
        # answered after t-1. The expected order is worked out by the rule, not read off the store.
        self.play(s, self.card(s, 1), False, confidence="guess")
        for _ in range(3):
            self.play(s, self.card(s, 2), False, confidence="guess")
        self.play(s, self.card(s, 3), False, confidence="sure")
        self.play(s, self.card(s, 4), False, confidence="guess")
        self.assertEqual(self.ids(s), ["t-3", "t-2", "t-4", "t-1"])
        # A later day puts a card ahead of equally-missed ones from earlier days.
        self.clock.day += timedelta(days=1)
        self.play(s, self.card(s, 1), False, confidence="guess")   # now missed twice, today
        self.assertEqual(self.ids(s), ["t-3", "t-2", "t-1", "t-4"])

    def test_sort_traps_alone_follows_the_same_rule(self) -> None:
        def t(i, misses, sure, day, tick):
            return {"id": i, "misses": misses, "sure_wrong": sure, "last_day": day, "last_tick": tick}

        rows = [t("a", 5, 0, "2026-10-01", 1), t("b", 1, 1, "2026-10-01", 1), t("c", 5, 0, "2026-10-02", 1),
                t("d", 5, 0, "2026-10-02", 9), t("e", 2, 3, "2026-10-01", 1), t("f", 1, 0, "2026-10-09", 1)]
        self.assertEqual([r["id"] for r in sort_traps(rows)], ["e", "b", "d", "c", "a", "f"])
        self.assertEqual([r["id"] for r in rows], list("abcdef"), "the input is not reordered")

    def test_languages_are_separate_and_unknown_ones_are_ignored(self) -> None:
        s = self.store(n=30)
        self.play(s, self.card(s, 0), False)
        js = s.find("javascript", "t-5")[0]
        self.play(s, js, False, language="javascript")
        self.assertEqual(self.ids(s, ("python",)), ["t-0"])
        self.assertEqual(self.ids(s, ("javascript",)), ["t-5"])
        self.assertEqual(sorted(self.ids(s, ("python", "javascript"))), ["t-0", "t-5"])
        self.assertEqual(s.traps(["cobol"]), [])
        self.assertEqual(s.traps([]), [])

    def test_a_record_whose_card_no_longer_exists_is_skipped(self) -> None:
        s = self.store(n=30)
        self.play(s, self.card(s, 0), False)
        state = json.loads((self.dir / "gotchas.json").read_text(encoding="utf-8"))
        state["stats"]["python:t-gone"] = {**state["stats"]["python:t-0"]}
        state["stats"]["javascript:t-0"] = {**state["stats"]["python:t-0"]}
        (self.dir / "gotchas.json").write_text(json.dumps(state), encoding="utf-8")
        self.assertEqual(self.ids(s), ["t-0"])
        self.assertEqual(self.ids(s, ("javascript",)), ["t-0"], "javascript has a t-0 of its own")

    def test_your_own_cards_are_included_on_the_same_terms(self) -> None:
        s = self.store(n=30)
        item = s.add_card("python", "print(1)", "1", ["2", "3"], False, "Added by you", "My own reason.")
        spot = served_options(item, None)[1]
        self.assertEqual(s.traps(["python"]), [], "not answered yet, so not a trap")
        s.answer("python", item.id, (spot + 1) % 3, confidence="sure")
        [t] = s.traps(["python"])
        self.assertEqual((t["id"], t["mine"], t["title"], t["sure_wrong"], t["why"]),
                         (item.id, True, f"Your card {item.id[5:]}", 1, "My own reason."))
        s.answer("python", item.id, spot, confidence="sure")
        s.answer("python", item.id, spot, confidence="sure")
        self.assertEqual(s.traps(["python"]), [])

    def test_a_deleted_user_card_leaves_the_list(self) -> None:
        s = self.store(n=30)
        item = s.add_card("python", "print(1)", "1", ["2", "3"], False, "Added by you", "x")
        spot = served_options(item, None)[1]
        s.answer("python", item.id, (spot + 1) % 3)
        self.assertEqual(len(s.traps(["python"])), 1)
        s.delete_card("python", item.id)
        self.assertEqual(s.traps(["python"]), [])


# ── The routes ──────────────────────────────────────────────────────────


def _wrong(language: str, item_id: str) -> int:
    item, index = gotchas.STORE.find(language, item_id)
    return (served_options(item, index)[1] + 1) % 4


def _right(language: str, item_id: str) -> int:
    item, index = gotchas.STORE.find(language, item_id)
    return served_options(item, index)[1]


def _status(call, *args, **kw) -> int:
    try:
        call(*args, **kw)
    except HTTPException as exc:
        return exc.status_code
    return 200


OLD_FIELDS = {"correct", "answer", "answer_index", "chosen", "trap", "why", "mine", "streak", "streak_best",
              "seen_before", "again_soon", "daily", "summary"}


class Routes(unittest.TestCase):
    def test_an_answer_with_and_without_the_new_fields_keeps_every_old_field(self) -> None:
        plain = server.gotchas_answer(GotchaAnswerRequest(id="py-score-90", language="python",
                                                          chosen=_right("python", "py-score-90")))
        rich = server.gotchas_answer(GotchaAnswerRequest(
            id="py-loop-var-list", language="python", chosen=_right("python", "py-loop-var-list"),
            confidence="sure", note=" because "))
        self.assertTrue(OLD_FIELDS <= set(plain) and OLD_FIELDS <= set(rich))
        self.assertEqual(set(plain), set(rich), "the same shape either way")
        self.assertEqual({"confidence", "comes_back", "note"}, set(plain) - OLD_FIELDS)
        self.assertEqual((plain["correct"], plain["streak"], plain["again_soon"], plain["confidence"], plain["note"]),
                         (True, 1, False, "", ""))
        self.assertEqual((rich["correct"], rich["streak"], rich["again_soon"], rich["confidence"], rich["note"]),
                         (True, 2, False, "sure", "because"))
        self.assertEqual(rich["trap"], gotchas.STORE.find("python", "py-loop-var-list")[0].trap)

    def test_the_request_takes_odd_values_without_a_422(self) -> None:
        for conf, note in ((5, 5), (None, None), ("sure!", ["x"]), ({"a": 1}, {"b": 2})):
            body = GotchaAnswerRequest(id="py-score-90", language="python", chosen=_right("python", "py-score-90"),
                                       confidence=conf, note=note)
            got = server.gotchas_answer(body)
            self.assertEqual((got["confidence"], got["note"]), ("", ""))

    def test_bad_ids_and_choices_are_still_400_with_the_new_fields(self) -> None:
        self.assertEqual(_status(server.gotchas_answer, GotchaAnswerRequest(
            id="nope", language="python", chosen=0, confidence="sure", note="x")), 400)
        self.assertEqual(_status(server.gotchas_answer, GotchaAnswerRequest(
            id="py-score-90", language="python", chosen=9, confidence="sure")), 400)

    def test_traps_lists_only_answered_missed_cards_in_order_with_the_card_inside(self) -> None:
        self.assertEqual(server.gotchas_traps("python")["traps"], [])
        # One card answered right, never missed: not a trap.
        server.gotchas_answer(GotchaAnswerRequest(id="py-score-90", language="python",
                                                  chosen=_right("python", "py-score-90"), confidence="sure"))
        # Two missed cards, one sure.
        server.gotchas_answer(GotchaAnswerRequest(id="py-loop-var-list", language="python",
                                                  chosen=_wrong("python", "py-loop-var-list"), confidence="guess"))
        got = server.gotchas_answer(GotchaAnswerRequest(
            id="py-unbound-local", language="python", chosen=_wrong("python", "py-unbound-local"),
            confidence="sure", note="I thought it would see the global"))
        self.assertTrue(got["comes_back"])
        listing = server.gotchas_traps("python")
        self.assertEqual(listing["language"], "python")
        self.assertEqual([t["id"] for t in listing["traps"]], ["py-unbound-local", "py-loop-var-list"])
        first = listing["traps"][0]
        item = gotchas.STORE.find("python", "py-unbound-local")[0]
        self.assertEqual((first["code"], first["trap"], first["why"], first["note"], first["sure_wrong"],
                          first["misses"], first["language_name"], first["title"]),
                         (item.code, item.trap, item.why, "I thought it would see the global", 1, 1,
                          "Python", "Unbound local"))
        # Nothing unanswered, and no card's answer, is in the listing.
        everything = json.dumps(listing)
        for other in DECKS["python"][2:8]:
            self.assertNotIn(other.id, [t["id"] for t in listing["traps"]])
            self.assertNotIn(f'"id": "{other.id}"', everything)
        self.assertTrue(all("answer" not in t and "answer_index" not in t for t in listing["traps"]),
                        "the listing is for studying a card you saw; it never carries the answer key")

    def test_traps_defaults_to_every_language_and_filters_by_one(self) -> None:
        server.gotchas_answer(GotchaAnswerRequest(id="py-loop-var-list", language="python",
                                                  chosen=_wrong("python", "py-loop-var-list")))
        self.assertEqual([t["id"] for t in server.gotchas_traps()["traps"]], ["py-loop-var-list"])
        self.assertEqual([t["id"] for t in server.gotchas_traps("all")["traps"]], ["py-loop-var-list"])
        if NODE is not None:
            server.gotchas_answer(GotchaAnswerRequest(id="js-typeof-null", language="javascript",
                                                      chosen=_wrong("javascript", "js-typeof-null")))
            self.assertEqual(sorted(t["id"] for t in server.gotchas_traps("all")["traps"]),
                             ["js-typeof-null", "py-loop-var-list"])
            self.assertEqual([t["id"] for t in server.gotchas_traps("javascript")["traps"]], ["js-typeof-null"])
            self.assertEqual([t["id"] for t in server.gotchas_traps("python")["traps"]], ["py-loop-var-list"])

    def test_traps_with_an_unknown_language_is_400_like_the_other_routes(self) -> None:
        self.assertEqual(_status(server.gotchas_traps, "cobol"), 400)
        self.assertEqual(_status(server.gotchas_traps, ""), 400)
        self.assertEqual(_status(server.gotchas_summary, "cobol"), 400)

    def test_a_user_card_is_in_my_traps_once_missed(self) -> None:
        added = server.gotchas_user_add(GotchaUserRequest(language="python", code="print(len('ab'))"))
        self.assertEqual(server.gotchas_traps("python")["traps"], [])
        nxt = server.gotchas_next("python")
        self.assertEqual(nxt["id"], added["id"])
        wrong = next(i for i, o in enumerate(nxt["options"]) if o != added["answer"])
        server.gotchas_answer(GotchaAnswerRequest(id=nxt["id"], language="python", chosen=wrong, confidence="sure"))
        [t] = server.gotchas_traps("python")["traps"]
        self.assertEqual((t["id"], t["mine"], t["sure_wrong"]), (added["id"], True, 1))

    def test_try_again_serves_that_card_with_its_answer_hidden_and_counts_as_a_normal_answer(self) -> None:
        server.gotchas_answer(GotchaAnswerRequest(id="py-unbound-local", language="python",
                                                  chosen=_wrong("python", "py-unbound-local"), confidence="sure"))
        card = server.gotchas_next("python", card="py-unbound-local")
        self.assertEqual((card["id"], card["why_picked"]), ("py-unbound-local", "trap"))
        for secret in ("answer", "answer_index", "trap", "why"):
            self.assertNotIn(secret, card)
        got = server.gotchas_answer(GotchaAnswerRequest(
            id=card["id"], language="python", chosen=_right("python", card["id"]), confidence="sure"))
        self.assertTrue(got["correct"])
        self.assertEqual(server.gotchas_traps("python")["traps"][0]["misses"], 1)
        server.gotchas_answer(GotchaAnswerRequest(
            id=card["id"], language="python", chosen=_right("python", card["id"]), confidence="sure"))
        self.assertEqual(server.gotchas_traps("python")["traps"], [], "two right-and-sure answers master it")

    def test_try_again_on_an_unknown_card_is_400(self) -> None:
        self.assertEqual(_status(server.gotchas_next, "python", card="nope"), 400)
        self.assertEqual(_status(server.gotchas_next, "python", card="js-typeof-null"), 400)

    def test_the_feed_still_deals_a_sure_wrong_card_back_within_a_few_answers(self) -> None:
        first = server.gotchas_next("python")
        server.gotchas_answer(GotchaAnswerRequest(id=first["id"], language="python",
                                                  chosen=_wrong("python", first["id"]), confidence="sure"))
        seen, recent = [], [first["id"]]
        for _ in range(8):
            card = server.gotchas_next("python", exclude=",".join(recent[-3:]))
            seen.append(card["id"])
            recent.append(card["id"])
            server.gotchas_answer(GotchaAnswerRequest(id=card["id"], language="python",
                                                      chosen=_right("python", card["id"]), confidence="sure"))
        self.assertIn(first["id"], seen[:5], "2-4 answers later, +1 for the browser's 3-card exclude window")



def test_traps_for_a_language_without_a_toolchain_is_400_and_all_leaves_it_out(monkeypatch):
    from code_coach.gotchas import toolchains

    lang_id = next(i for i in DECKS if i != "python")
    card = DECKS[lang_id][0]
    gotchas.STORE.answer(lang_id, card.id, _wrong(lang_id, card.id), confidence="sure")
    real = toolchains.available
    if real(lang_id):
        assert [t["id"] for t in server.gotchas_traps(lang_id)["traps"]] == [card.id]
    monkeypatch.setattr(toolchains, "available", lambda i: False if i == lang_id else real(i))
    assert _status(server.gotchas_traps, lang_id) == 400
    assert card.id not in [t["id"] for t in server.gotchas_traps("all")["traps"]]
