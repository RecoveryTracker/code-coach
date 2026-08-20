"""The typing trainer's drills have to be honest about what they're testing.

Most of these are guards against ways a generated drill can look fine and
teach nothing: a prompt that hands you the answer, a word that needs a key the
section never covers, or the same key asked for twice running.
"""

from __future__ import annotations

import unittest

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

    def test_named_keys_have_speakable_names(self) -> None:
        self.assertEqual(name_for("|"), "pipe")
        self.assertEqual(name_for(" "), "space")
        self.assertEqual(name_for("A"), "capital A")


if __name__ == "__main__":
    unittest.main()
