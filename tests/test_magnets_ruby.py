"""The Ruby code magnets: the same rules as tests/test_magnets.py.

The load-bearing test is again `test_every_puzzle_prints_what_it_claims`.
A magnet is marked by running what was arranged and comparing what it
printed, so the typed-out expected output is the whole marker, and here
it is held to what Ruby prints.

These read RUBY_MAGNETS directly rather than through `magnets()`, so they
check the content whether or not it has been registered with the mode
yet. The tests that go through the API skip until it is. Without Ruby
the tests that run it are skipped rather than failed.
"""

from __future__ import annotations

import os
import unittest

from code_coach.engine import ruby_available, run_code
from code_coach.magnets import Magnet, magnet, magnets, same_pieces
from code_coach.magnets.content_ruby import RUBY_MAGNETS

FAMILY = "Ruby"
NEEDS_RUBY = "Ruby is not installed"
#: Registered once `magnets()` hands back the very objects in this file.
REGISTERED = all(magnet(m.id) is m for m in RUBY_MAGNETS)
NOT_REGISTERED = "RUBY_MAGNETS is not in magnets() yet"


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="ruby")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[:200]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str) -> Magnet:
    return next(m for m in RUBY_MAGNETS if m.id == magnet_id)


def _moved(m: Magnet, line: str, to: int) -> str:
    """The program with one line taken out and put back at `to`."""
    pieces = list(m.pieces)
    pieces.remove(line)
    pieces.insert(to, line)
    return "\n".join(pieces)


class ShapeTests(unittest.TestCase):
    def test_there_are_six_in_one_family(self) -> None:
        self.assertEqual(len(RUBY_MAGNETS), 6)
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.family, FAMILY)
                self.assertEqual(m.language, "ruby")

    def test_ids_are_unique(self) -> None:
        ids = [m.id for m in RUBY_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_id_is_taken_by_another_puzzle(self) -> None:
        mine = {m.id for m in RUBY_MAGNETS}
        others = [
            m.id for m in magnets()
            if not any(m is r for r in RUBY_MAGNETS)
        ]
        self.assertFalse(mine & set(others))

    def test_there_is_something_to_arrange(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 8)
                self.assertLessEqual(
                    len(m.pieces), 12, f"{m.id} has {len(m.pieces)} magnets")

    def test_no_magnet_is_blank(self) -> None:
        for m in RUBY_MAGNETS:
            for piece in m.pieces:
                with self.subTest(magnet=m.id):
                    self.assertTrue(piece.strip())

    def test_the_ranking_was_done(self) -> None:
        levels = [m.level for m in RUBY_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreater(
                    len(m.note), 120, f"{m.id}'s note explains nothing")
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())


@unittest.skipUnless(ruby_available(), NEEDS_RUBY)
class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    _run(m.code), m.expect.strip(),
                    f"{m.id}: Ruby disagrees with the expected output")

    def test_the_answers_say_nothing_on_stderr(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                _, err, _ = run_code(m.code, language="ruby")
                self.assertEqual(err.strip(), "")

    def test_the_order_matters_at_all(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                differs = any(
                    _run("\n".join(m.shuffled(seed=s))) != m.expect.strip()
                    for s in range(8)
                )
                self.assertTrue(
                    differs,
                    f"{m.id} prints its answer whatever order it is in")

    def test_a_call_above_its_def_fails(self) -> None:
        """The second puzzle's note: Ruby defines a method when it
        reaches the def, so a call above it is a NoMethodError."""
        m = _find("magnet-ruby-define-before-call")
        got = _run(_moved(m, 'puts greet("Ann")', 0))
        self.assertTrue(got.startswith("(exit"))
        self.assertIn("NoMethodError", got)

    def test_the_two_defs_go_either_way_round(self) -> None:
        """Why marking runs the program rather than comparing orders."""
        m = _find("magnet-ruby-define-before-call")
        pieces = list(m.pieces)
        swapped = [*pieces[3:6], *pieces[0:3], *pieces[6:]]
        self.assertTrue(same_pieces(m, swapped))
        self.assertNotEqual(swapped, pieces)
        self.assertEqual(_run("\n".join(swapped)), m.expect)

    def test_counting_after_the_yield_starts_at_zero(self) -> None:
        m = _find("magnet-ruby-yield")
        got = _run(_moved(m, "    count += 1", 4))
        self.assertEqual(got, "go 0\ngo 1\ngo 2\ndone 3")

    def test_skipping_after_adding_skips_nothing(self) -> None:
        m = _find("magnet-ruby-each-with-index")
        got = _run(_moved(m, "  next if fruit.size < 4", 4))
        self.assertEqual(got, "1. apple\n2. fig\n3. kiwi\n3 of 3")

    def test_a_failed_parse_skips_the_rest_of_the_begin(self) -> None:
        """Checked by the absence of a "got 4x" line in the answer."""
        m = _find("magnet-ruby-rescue-ensure")
        self.assertNotIn("got 4x", _run(m.code))


class ShuffleTests(unittest.TestCase):
    def test_the_pieces_all_come_back(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    sorted(m.shuffled(seed=1)), sorted(m.pieces))

    def test_it_never_hands_back_the_answer(self) -> None:
        for m in RUBY_MAGNETS:
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    self.assertNotEqual(m.shuffled(seed=seed), m.pieces)


class PiecesTests(unittest.TestCase):
    def test_the_right_pieces_are_recognised(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertTrue(same_pieces(m, list(m.shuffled(seed=3))))

    def test_a_missing_piece_is_noticed(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertFalse(same_pieces(m, list(m.pieces[1:])))


class SubgoalTests(unittest.TestCase):
    """The stage labels, with Ruby's own giveaways added to the list."""

    GIVEAWAYS = (
        "(", ")", ";", "{", "}", "=>", "#", "*", "&", "[", "]", "%",
        "'", "\"", "<", ">", "\\", "@", "|", ":", "=",
    )

    def test_every_puzzle_has_stages(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.plan), 2)

    def test_the_stages_cover_every_line_exactly_once(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                counted = sum(count for _, count in m.plan)
                self.assertEqual(
                    counted, len(m.pieces),
                    f"{m.id}: stages cover {counted} lines of "
                    f"{len(m.pieces)}")
                placed = [line for _, lines in m.stages for line in lines]
                self.assertEqual(placed, list(m.pieces))

    def test_no_stage_is_empty(self) -> None:
        for m in RUBY_MAGNETS:
            for label, count in m.plan:
                with self.subTest(magnet=m.id, label=label):
                    self.assertGreater(count, 0)

    def test_the_labels_are_distinct_within_a_puzzle(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(len(set(m.labels)), len(m.labels))

    def test_a_label_is_a_description_not_a_line(self) -> None:
        for m in RUBY_MAGNETS:
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper(), "starts as a sentence")
                    for giveaway in self.GIVEAWAYS:
                        self.assertNotIn(giveaway, label)

    def test_the_stages_are_in_program_order(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                rebuilt = "\n".join(
                    line for _, lines in m.stages for line in lines)
                self.assertEqual(rebuilt, m.code)


@unittest.skipUnless(REGISTERED, NOT_REGISTERED)
class RegisteredTests(unittest.TestCase):
    """Through the API, once the puzzles are part of the mode."""

    def _check(self, magnet_id: str, lines: list[str]):
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        return server.magnet_check(
            MagnetCheckRequest(magnet_id=magnet_id, lines=lines))

    def test_the_family_is_served_with_its_language(self) -> None:
        from code_coach.api import server

        served = server.magnet_list()
        family = next(
            f for f in served["families"] if f["name"] == FAMILY)
        self.assertEqual(
            [row["id"] for row in family["magnets"]],
            [m.id for m in RUBY_MAGNETS])
        for row in family["magnets"]:
            with self.subTest(magnet=row["id"]):
                self.assertEqual(row["language"], "ruby")
                self.assertNotIn("plan", row)

    @unittest.skipUnless(ruby_available(), NEEDS_RUBY)
    def test_the_intended_order_passes(self) -> None:
        for m in RUBY_MAGNETS:
            with self.subTest(magnet=m.id):
                got = self._check(m.id, list(m.pieces))
                self.assertTrue(got.passed, got.broke or got.printed)

    @unittest.skipUnless(ruby_available(), NEEDS_RUBY)
    def test_an_error_comes_back_without_the_scratch_path(self) -> None:
        """A call above its def is a Ruby error, and it has to be shown
        as a line number and a reason, not a file in the temp dir."""
        m = _find("magnet-ruby-define-before-call")
        lines = list(m.pieces)
        lines.remove('puts greet("Ann")')
        lines.insert(0, 'puts greet("Ann")')
        got = self._check(m.id, lines)
        self.assertFalse(got.passed)
        self.assertTrue(got.broke)
        self.assertIn("NoMethodError", got.broke)
        self.assertNotIn(".rb:", got.broke)
        self.assertNotIn(os.sep + "Temp", got.broke)
        self.assertNotIn("/Temp", got.broke)


if __name__ == "__main__":
    unittest.main()
