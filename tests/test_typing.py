"""The typing trainer's drills have to be honest about what they're testing.

Most of these are guards against ways a generated drill can look fine and
teach nothing: a prompt that hands you the answer, a word that needs a key the
section never covers, or the same key asked for twice running.
"""

from __future__ import annotations

import unittest

from code_coach.typing import english, thesaurus
from code_coach.typing.snippets import ALL_SNIPPETS
from code_coach.typing.drills import (
    CODE_LINES,
    DEFAULT_LINES,
    MODES_BY_ID,
    SECTIONS,
    SECTIONS_BY_ID,
    THEMES,
    THEMES_BY_ID,
    build_drill,
    catalog,
    theme_catalog,
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

    def test_themed_speed_runs_serve_their_own_text(self) -> None:
        """Picking Scripture must give scripture, not the stock pangrams."""
        for theme_id in ("scripture", "affirmations", "conscious", "tricks"):
            wanted = {p.text for p in THEMES_BY_ID[theme_id].passages}
            drill = build_drill("letters", "speed", theme_id=theme_id, seed="t")
            for target in drill.targets:
                self.assertIn(target.text, wanted, theme_id)

    def test_the_theme_travels_with_any_section(self) -> None:
        """Which keys and what the words say are independent choices."""
        wanted = {p.text for p in THEMES_BY_ID["scripture"].passages}
        for section_id in ("home", "letters", "everything", "coding"):
            drill = build_drill(section_id, "speed", theme_id="scripture", seed="t")
            for target in drill.targets:
                self.assertIn(target.text, wanted, section_id)

    def test_scripture_passages_carry_their_reference(self) -> None:
        drill = build_drill("letters", "speed", theme_id="scripture", seed="t")
        for target in drill.targets:
            self.assertTrue(target.note.strip(), target.text)

    def test_a_theme_a_mode_cannot_use_falls_back(self) -> None:
        """Scripture has no word list, so Words mode can't be driven by it —
        but asking for it must not produce an empty drill."""
        drill = build_drill("letters", "words", theme_id="scripture", seed="t")
        self.assertTrue(drill.targets)
        self.assertNotEqual(drill.theme, "scripture")

    def test_define_never_falls_back_to_words_with_no_meaning(self) -> None:
        for theme_id in ("mixed", "scripture", "useful"):
            drill = build_drill("letters", "define", theme_id=theme_id, seed="t")
            for target in drill.targets:
                self.assertTrue(target.prompt.strip(), f"{theme_id}: {target.text}")
                self.assertNotEqual(target.prompt, target.text)

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

    def test_every_section_and_mode_works_with_every_theme(self) -> None:
        """The theme is an independent axis, so no combination may break."""
        for entry in catalog():
            for mode in entry["modes"]:
                for theme in theme_catalog():
                    drill = build_drill(
                        entry["id"], mode["id"], theme_id=theme["id"], seed="x"
                    )
                    self.assertTrue(
                        drill.targets,
                        f"{entry['id']}/{mode['id']}/{theme['id']} is empty",
                    )

    def test_theme_catalog_reports_what_each_can_drive(self) -> None:
        for entry in theme_catalog():
            theme = THEMES_BY_ID[entry["id"]]
            self.assertEqual(entry["has_words"], bool(theme.words))
            self.assertEqual(entry["has_passages"], bool(theme.passages))

    def test_mixed_is_the_default_and_brings_no_content_of_its_own(self) -> None:
        self.assertEqual(THEMES[0].id, "mixed")
        self.assertFalse(THEMES[0].passages)

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

    def test_code_themes_serve_their_own_snippets(self) -> None:
        for theme_id in ("school", "tricks", "visuals", "fractals", "useful"):
            wanted = {p.text for p in THEMES_BY_ID[theme_id].passages}
            drill = build_drill("everything", "speed", theme_id=theme_id, seed="t")
            for target in drill.targets:
                self.assertIn(target.text, wanted, theme_id)

    def test_random_never_serves_words_the_section_cannot_type(self) -> None:
        """The number row was being handed "point" and "great"."""
        for section_id in ("numbers", "symbols", "coding", "home", "bottom"):
            allowed = set(SECTIONS_BY_ID[section_id].chars)
            drill = build_drill(section_id, "random", seed="t")
            self.assertTrue(drill.targets, section_id)
            for target in drill.targets:
                # Space is always allowed; every other key has to be one the
                # section actually teaches. Exempting whole lines here hid
                # Home Row being handed a pangram.
                self.assertFalse(
                    set(target.text.lower()) - allowed - {" "},
                    f"{section_id}: {target.text!r}",
                )

    def test_a_section_never_asks_for_a_key_it_does_not_teach(self) -> None:
        """A pangram needs the whole alphabet, so a single row can't type one —
        and a punctuation-only section can't type `print(f"{name}")`."""
        for section_id in ("home", "top", "bottom", "numbers", "symbols", "coding"):
            allowed = set(SECTIONS_BY_ID[section_id].chars) | {" "}
            for mode_id in ("speed", "random", "perfect"):
                for target in build_drill(section_id, mode_id, seed="t").targets:
                    self.assertFalse(
                        set(target.text.lower()) - allowed,
                        f"{section_id}/{mode_id}: {target.text!r}",
                    )

    def test_random_never_repeats_a_line(self) -> None:
        """Independent samples overlap, so the same passage turned up twice."""
        for section_id in ("everything", "letters", "home", "numbers"):
            texts = [t.text for t in build_drill(section_id, "random", seed="t").targets]
            self.assertEqual(len(texts), len(set(texts)), section_id)

    def test_random_serves_real_prose_before_shuffled_words(self) -> None:
        """A line of shuffled words reads as filler next to actual writing."""
        targets = build_drill("everything", "random", seed="t").targets
        filler = [t for t in targets if t.note == "from these keys"]
        self.assertEqual(filler, [])

    def test_the_code_section_serves_whole_lines_of_code(self) -> None:
        """A code section that served pangrams would be a letters section with
        a different name."""
        for mode_id in ("random", "speed", "perfect"):
            targets = build_drill("code", mode_id, seed="t").targets
            self.assertTrue(targets, mode_id)
            for target in targets:
                self.assertIn(target.text, {p.text for p in CODE_LINES}, mode_id)

    def test_every_code_line_explains_itself(self) -> None:
        """Reading code at a glance is its own skill — the note teaches it."""
        for target in build_drill("code", "speed", seed="t").targets:
            self.assertTrue(target.note.strip(), target.text)

    def test_code_symbols_stays_punctuation_only(self) -> None:
        """The two code sections do different jobs and mustn't merge."""
        allowed = set(SECTIONS_BY_ID["coding"].chars)
        self.assertFalse(any(c.isalnum() for c in allowed))

    def test_no_target_contains_a_character_off_the_keyboard(self) -> None:
        """Prose is written with em dashes and curly quotes without anyone
        thinking about it, and a target containing one cannot be finished."""
        for entry in catalog():
            for mode in entry["modes"]:
                for theme in theme_catalog():
                    drill = build_drill(
                        entry["id"], mode["id"], theme_id=theme["id"], seed="t"
                    )
                    for target in drill.targets:
                        for char in target.text:
                            self.assertIn(
                                char,
                                BY_CHAR,
                                f"{entry['id']}/{mode['id']}/{theme['id']}: "
                                f"{char!r} in {target.text!r}",
                            )

    def test_the_word_chain_walks_from_one_word_to_a_related_one(self) -> None:
        targets = build_drill("everything", "chain", seed="t").targets
        self.assertGreater(len(targets), 4)
        self.assertEqual(targets[0].note, "starting here")
        for before, after in zip(targets, targets[1:]):
            word = before.text.split(" - ")[0]
            self.assertEqual(after.note, f"from {word}")

    def test_the_word_chain_never_doubles_back(self) -> None:
        """Returning to a word you just left is not a journey."""
        words = [
            t.text.split(" - ")[0]
            for t in build_drill("everything", "chain", seed="t").targets
        ]
        self.assertEqual(len(words), len(set(words)))

    def test_the_word_chain_is_offered_on_the_letter_sections(self) -> None:
        """Requiring the punctuation as well hid it on seven sections of
        nine, which is not where a headline mode should live."""
        offered = {
            entry["id"]
            for entry in catalog()
            if any(m["id"] == "chain" for m in entry["modes"])
        }
        for section_id in ("letters", "everything", "code", "vocab"):
            if section_id in SECTIONS_BY_ID:
                self.assertIn(section_id, offered, section_id)
        self.assertNotIn("numbers", offered)
        self.assertNotIn("symbols", offered)

    def test_the_chain_only_uses_keys_its_section_teaches(self) -> None:
        for section_id in ("letters", "everything", "code"):
            allowed = set(SECTIONS_BY_ID[section_id].chars) | {" "}
            for target in build_drill(section_id, "chain", seed="t").targets:
                self.assertFalse(
                    set(target.text) - allowed, f"{section_id}: {target.text!r}"
                )

    def test_every_thesaurus_link_leads_somewhere(self) -> None:
        """A walk must never reach a dead end."""
        dangling = {
            name
            for entry in thesaurus.ENTRIES
            for name in entry.near
            if name not in thesaurus.BY_WORD
        }
        self.assertEqual(dangling, set())

    def test_no_word_is_defined_twice(self) -> None:
        words = [entry.word for entry in thesaurus.ENTRIES]
        self.assertEqual(len(words), len(set(words)))

    def test_the_language_themes_carry_their_own_lore(self) -> None:
        for theme_id, needle in (
            ("python", "Python"),
            ("javascript", "JavaScript"),
            ("dart", "Dart"),
        ):
            sources = {p.source for p in THEMES_BY_ID[theme_id].passages}
            self.assertTrue(
                any(needle in s for s in sources), f"{theme_id}: {sources}"
            )

    def test_python_ships_its_own_zen(self) -> None:
        texts = {p.text for p in THEMES_BY_ID["python"].passages}
        self.assertIn("Explicit is better than implicit.", texts)
        self.assertIn("Readability counts.", texts)

    def test_the_default_material_is_worth_reading(self) -> None:
        """Twenty minutes of practice may as well say something. Every line
        is real prose and carries a note saying where it came from."""
        for target in build_drill("everything", "random", seed="t").targets:
            self.assertTrue(target.note.strip(), target.text)
            self.assertIn(" ", target.text)
            self.assertGreater(len(target.text), 25, target.text)

    def test_the_default_pool_is_big_enough_not_to_repeat(self) -> None:
        """A drill that keeps handing you the same sentence stops being
        practice and becomes recitation."""
        self.assertGreaterEqual(len(DEFAULT_LINES), 90)
        seen: set[str] = set()
        for i in range(8):
            for target in build_drill("everything", "random", seed=str(i)).targets:
                seen.add(target.text)
        self.assertGreaterEqual(len(seen), 40)

    def test_no_line_is_repeated_inside_one_run(self) -> None:
        for section_id in ("everything", "letters", "code"):
            texts = [t.text for t in build_drill(section_id, "random", seed="t").targets]
            self.assertEqual(len(texts), len(set(texts)), section_id)

    def test_random_keeps_one_format_throughout(self) -> None:
        """Random means the text is unpredictable, not the format. Cycling
        between single words, key pairs and sentences inside one run turns a
        plain drill into a tour of the other modes."""
        for section_id in ("everything", "letters", "home", "numbers", "symbols"):
            targets = build_drill(section_id, "random", seed="t").targets
            self.assertTrue(targets, section_id)
            lengths = [len(t.text) for t in targets]
            # Every target is a line, so none of them is a lone key or pair.
            self.assertGreater(min(lengths), 6, f"{section_id}: {targets}")

    def test_random_reads_as_lines_not_single_words(self) -> None:
        targets = build_drill("letters", "random", seed="t").targets
        self.assertTrue(all(" " in t.text for t in targets))

    def test_the_whole_keyboard_comes_first_and_is_the_default(self) -> None:
        """Everything else is a narrower slice of it, so it leads."""
        self.assertEqual(SECTIONS[0].id, "everything")
        self.assertEqual(SECTIONS[0].name, "All")
        self.assertEqual(catalog()[0]["id"], "everything")

    def test_each_language_has_its_own_code_to_type(self) -> None:
        """Learning one language means wanting that language's punctuation in
        your hands, not an average of several."""
        for theme_id, needle in (
            ("pycode", "def "),
            ("jscode", "const "),
            ("dartcode", "final "),
            ("sqlcode", "SELECT "),
        ):
            texts = " ".join(p.text for p in THEMES_BY_ID[theme_id].passages)
            self.assertIn(needle, texts, theme_id)

    def test_language_code_themes_are_real_code_with_notes(self) -> None:
        for theme_id in ("pycode", "jscode", "dartcode", "sqlcode"):
            theme = THEMES_BY_ID[theme_id]
            self.assertGreaterEqual(len(theme.passages), 15, theme_id)
            for passage in theme.passages:
                self.assertTrue(passage.source.strip(), passage.text)
                self.assertNotIn("\n", passage.text)

    def test_sections_are_a_curriculum_not_a_content_list(self) -> None:
        """Scripture isn't a step in learning the keyboard the way Top Row is."""
        section_ids = {s.id for s in SECTIONS}
        for content in ("scripture", "affirmations", "conscious", "school"):
            self.assertNotIn(content, section_ids)
            self.assertIn(content, THEMES_BY_ID)

    def test_named_keys_have_speakable_names(self) -> None:
        self.assertEqual(name_for("|"), "pipe")
        self.assertEqual(name_for(" "), "space")
        self.assertEqual(name_for("A"), "capital A")


if __name__ == "__main__":
    unittest.main()
