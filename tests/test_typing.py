"""The typing trainer's drills have to be honest about what they're testing.

Most of these are guards against ways a generated drill can look fine and
teach nothing: a prompt that hands you the answer, a word that needs a key the
section never covers, or the same key asked for twice running.
"""

from __future__ import annotations

import unittest

from code_coach.typing import english
from code_coach.typing.snippets import ALL_SNIPPETS
from code_coach.typing.drills import (
    MODES_BY_ID,
    SECTIONS,
    SECTIONS_BY_ID,
    build_drill,
    catalog,
)
from code_coach.typing.keys import (
    ALL_KEYS,
    BY_CHAR,
    FINGER_NAMES,
    finger_for,
    keyboard_payload,
    name_for,
    needs_shift,
)


class KeyboardTests(unittest.TestCase):
    def test_every_key_has_a_known_finger(self) -> None:
        for key in ALL_KEYS:
            self.assertIn(key.finger, FINGER_NAMES, key.char)

    def test_shifted_characters_are_reachable(self) -> None:
        for key in ALL_KEYS:
            self.assertIn(key.shifted, BY_CHAR, key.shifted)

    def test_needs_shift_only_for_shifted_characters(self) -> None:
        self.assertTrue(needs_shift("|"))
        self.assertTrue(needs_shift("A"))
        self.assertFalse(needs_shift("a"))
        self.assertFalse(needs_shift("\\"))

    def test_payload_covers_the_whole_layout(self) -> None:
        payload = keyboard_payload()
        flat = [k for row in payload for k in row]
        self.assertEqual(len(flat), len(ALL_KEYS))


class DrillTests(unittest.TestCase):
    def test_every_offered_mode_builds_a_drill(self) -> None:
        for entry in catalog():
            for mode in entry["modes"]:
                with self.subTest(section=entry["id"], mode=mode["id"]):
                    drill = build_drill(entry["id"], mode["id"], seed="t")
                    self.assertTrue(drill.targets)

    def test_no_target_asks_for_a_key_that_does_not_exist(self) -> None:
        for entry in catalog():
            for mode in entry["modes"]:
                drill = build_drill(entry["id"], mode["id"], seed="t")
                for target in drill.targets:
                    for char in target.text:
                        self.assertIn(
                            char, BY_CHAR, f"{entry['id']}/{mode['id']}: {char!r}"
                        )

    def test_prompts_are_never_empty(self) -> None:
        for entry in catalog():
            for mode in entry["modes"]:
                drill = build_drill(entry["id"], mode["id"], seed="t")
                for target in drill.targets:
                    self.assertTrue(target.prompt.strip())

    def test_recall_prompt_never_gives_the_answer(self) -> None:
        """"Type the key named 'k'" would just be showing you the key."""
        for entry in catalog():
            for mode in entry["modes"]:
                if mode["id"] not in ("recall", "define"):
                    continue
                drill = build_drill(entry["id"], mode["id"], seed="t")
                for target in drill.targets:
                    self.assertNotEqual(
                        target.prompt, target.text, f"{entry['id']}/{mode['id']}"
                    )

    def test_words_only_use_keys_from_their_own_section(self) -> None:
        """A row drill that needs a key from another row isn't a row drill."""
        for entry in catalog():
            if entry["id"] in ("vocab", "jargon", "conscious"):
                continue  # Vocabulary sections draw on the whole keyboard.
            for mode in entry["modes"]:
                if mode["id"] not in ("words", "define"):
                    continue
                section = SECTIONS_BY_ID[entry["id"]]
                allowed = set(section.chars)
                for target in build_drill(entry["id"], mode["id"], seed="t").targets:
                    self.assertFalse(
                        set(target.text) - allowed,
                        f"{entry['id']}: {target.text!r}",
                    )

    def test_reaction_drills_never_repeat_a_key(self) -> None:
        """Pressing the same key twice measures the press, not the search."""
        for entry in catalog():
            for mode in entry["modes"]:
                if mode["id"] not in ("whack", "recall"):
                    continue
                targets = build_drill(entry["id"], mode["id"], seed="t").targets
                for before, after in zip(targets, targets[1:]):
                    self.assertNotEqual(
                        before.text, after.text, f"{entry['id']}/{mode['id']}"
                    )

    def test_seeds_change_the_draw(self) -> None:
        first = build_drill("home", "whack", seed="a").targets
        second = build_drill("home", "whack", seed="b").targets
        self.assertNotEqual(
            [t.text for t in first], [t.text for t in second]
        )

    def test_same_seed_repeats_exactly(self) -> None:
        first = build_drill("symbols", "drill", seed="fixed").targets
        second = build_drill("symbols", "drill", seed="fixed").targets
        self.assertEqual([t.text for t in first], [t.text for t in second])

    def test_passage_sections_serve_their_own_text(self) -> None:
        """Scripture speed drills must be scripture, not the stock pangrams."""
        for section_id in ("scripture", "affirmations", "conscious"):
            section = SECTIONS_BY_ID[section_id]
            wanted = {p.text for p in section.passages}
            drill = build_drill(section_id, "speed", seed="t")
            for target in drill.targets:
                self.assertIn(target.text, wanted, section_id)

    def test_scripture_passages_carry_their_reference(self) -> None:
        for target in build_drill("scripture", "speed", seed="t").targets:
            self.assertTrue(target.note.strip(), target.text)

    def test_unknown_ids_fall_back_rather_than_crash(self) -> None:
        drill = build_drill("nope", "nope", seed="t")
        self.assertTrue(drill.targets)

    def test_finger_is_known_for_every_first_character(self) -> None:
        for entry in catalog():
            for mode in entry["modes"]:
                for target in build_drill(entry["id"], mode["id"], seed="t").targets:
                    self.assertIn(finger_for(target.text[0]), FINGER_NAMES)

    def test_catalog_covers_every_section(self) -> None:
        self.assertEqual(
            [e["id"] for e in catalog()], [s.id for s in SECTIONS]
        )

    def test_every_offered_mode_is_a_real_mode(self) -> None:
        for entry in catalog():
            for mode in entry["modes"]:
                self.assertIn(mode["id"], MODES_BY_ID)

    def test_sweep_asks_for_every_key_exactly_once(self) -> None:
        for entry in catalog():
            if not any(m["id"] == "sweep" for m in entry["modes"]):
                continue
            section = SECTIONS_BY_ID[entry["id"]]
            targets = build_drill(entry["id"], "sweep", seed="t").targets
            self.assertEqual(
                sorted(t.text for t in targets), sorted(section.chars), entry["id"]
            )

    def test_sweep_order_changes_with_the_seed(self) -> None:
        """A fixed order would let you learn the sequence, not the keys."""
        first = [t.text for t in build_drill("letters", "sweep", seed="a").targets]
        second = [t.text for t in build_drill("letters", "sweep", seed="b").targets]
        self.assertNotEqual(first, second)
        self.assertEqual(sorted(first), sorted(second))

    def test_common_words_only_where_the_section_can_type_them(self) -> None:
        offered = {
            entry["id"]
            for entry in catalog()
            if any(m["id"] == "common" for m in entry["modes"])
        }
        # Single rows can't reach enough of English to measure a speed on.
        self.assertNotIn("home", offered)
        self.assertNotIn("bottom", offered)
        self.assertNotIn("symbols", offered)
        self.assertIn("letters", offered)

    def test_common_words_need_no_key_outside_the_section(self) -> None:
        for entry in catalog():
            if not any(m["id"] == "common" for m in entry["modes"]):
                continue
            allowed = set(SECTIONS_BY_ID[entry["id"]].chars)
            for target in build_drill(entry["id"], "common", seed="t").targets:
                self.assertFalse(
                    set(target.text.lower()) - allowed, f"{entry['id']}: {target.text}"
                )

    def test_timed_queues_enough_words_for_a_fast_minute(self) -> None:
        """Running out of words mid-test would end the minute early."""
        targets = build_drill("letters", "timed", seed="t").targets
        self.assertGreaterEqual(len(targets), 200)

    def test_pairs_prefer_real_combinations(self) -> None:
        real = set(english.BIGRAMS) | set(english.TRIGRAMS)
        targets = build_drill("letters", "pairs", seed="t").targets
        self.assertTrue(all(t.text in real for t in targets))

    def test_perfect_targets_are_long_enough_to_be_a_test(self) -> None:
        for entry in catalog():
            if not any(m["id"] == "perfect" for m in entry["modes"]):
                continue
            for target in build_drill(entry["id"], "perfect", seed="t").targets:
                self.assertGreaterEqual(len(target.text), 15, entry["id"])

    def test_no_snippet_contains_a_newline(self) -> None:
        """A target spanning two lines can't be typed as one target."""
        for passage in ALL_SNIPPETS:
            self.assertNotIn("\n", passage.text, passage.text)
            self.assertNotIn("\t", passage.text, passage.text)

    def test_every_snippet_says_what_it_does(self) -> None:
        for passage in ALL_SNIPPETS:
            self.assertTrue(passage.source.strip(), passage.text)

    def test_code_sections_serve_their_own_snippets(self) -> None:
        for section_id in ("school", "tricks", "visuals", "fractals", "useful"):
            wanted = {p.text for p in SECTIONS_BY_ID[section_id].passages}
            for target in build_drill(section_id, "speed", seed="t").targets:
                self.assertIn(target.text, wanted, section_id)

    def test_named_keys_have_speakable_names(self) -> None:
        self.assertEqual(name_for("|"), "pipe")
        self.assertEqual(name_for(" "), "space")
        self.assertEqual(name_for("A"), "capital A")


if __name__ == "__main__":
    unittest.main()
