"""The game-code magnets: the same rules as tests/test_magnets.py.

The load-bearing test is again `test_every_puzzle_prints_what_it_claims`.
A magnet is marked by running what was arranged and comparing what it
printed, so the typed-out expected output is the whole marker, and here
it is held to what Node prints.

These read JS_GAME_MAGNETS directly rather than through `magnets()`, so
they check the content whether or not it has been registered with the
mode yet. The route tests patch the set into `magnets()` for their
duration, so they mean the same thing before and after it is.
"""

from __future__ import annotations

import contextlib
import functools
import os
import unittest
from unittest import mock

import code_coach.magnets as magnets_module
from code_coach.engine import run_code
from code_coach.magnets import Magnet, magnets, same_pieces
from code_coach.magnets.content_jsgame import GAME, JS_GAME_MAGNETS


@functools.lru_cache(maxsize=None)
def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="javascript")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[:200]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str) -> Magnet:
    return next(m for m in JS_GAME_MAGNETS if m.id == magnet_id)


def _moved(m: Magnet, line: str, to: int) -> str:
    """The program with one line taken out and put back at `to`."""
    pieces = list(m.pieces)
    pieces.remove(line)
    pieces.insert(to, line)
    return "\n".join(pieces)


@contextlib.contextmanager
def _registered():
    """magnets() and magnet_families() as they will be once the set is
    registered."""
    real = magnets_module.magnets
    real_families = magnets_module.magnet_families

    def with_mine(family: str | None = None):
        have = {m.id for m in real()}
        everything = (*real(), *(m for m in JS_GAME_MAGNETS
                                 if m.id not in have))
        if family is not None:
            everything = tuple(m for m in everything if m.family == family)
        return tuple(sorted(everything, key=lambda m: m.level))

    def families_with_mine():
        names = list(real_families())
        if GAME not in names:
            names.append(GAME)
        return tuple(names)

    with mock.patch.object(magnets_module, "magnets", with_mine), \
            mock.patch.object(magnets_module, "magnet_families",
                              families_with_mine):
        yield


class ShapeTests(unittest.TestCase):
    def test_there_are_twelve_to_twenty_in_one_family(self) -> None:
        self.assertGreaterEqual(len(JS_GAME_MAGNETS), 12)
        self.assertLessEqual(len(JS_GAME_MAGNETS), 20)
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.family, GAME)
                self.assertEqual(m.language, "javascript")
                self.assertTrue(m.id.startswith("magnet-jsg-"))

    def test_ids_are_unique_and_new(self) -> None:
        ids = [m.id for m in JS_GAME_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))
        others = {m.id for m in magnets()
                  if not any(m is g for g in JS_GAME_MAGNETS)}
        self.assertFalse(set(ids) & others)

    def test_the_family_is_not_another_languages(self) -> None:
        for m in magnets(GAME):
            with self.subTest(magnet=m.id):
                self.assertEqual(m.language, "javascript")

    def test_there_is_something_to_arrange(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 6)
                self.assertLessEqual(
                    len(m.pieces), 12, f"{m.id} has {len(m.pieces)} magnets")

    def test_no_magnet_is_blank(self) -> None:
        for m in JS_GAME_MAGNETS:
            for piece in m.pieces:
                with self.subTest(magnet=m.id):
                    self.assertTrue(piece.strip())

    def test_the_ranking_was_done(self) -> None:
        levels = [m.level for m in JS_GAME_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreater(
                    len(m.note), 120, f"{m.id}'s note explains nothing")
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())

    def test_nothing_needs_a_browser(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                for word in ("document", "window", "requestAnimationFrame"):
                    self.assertNotIn(word, m.code)


class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    _run(m.code), m.expect.strip(),
                    f"{m.id}: node disagrees with the expected output")

    def test_the_answers_say_nothing_on_stderr(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                _, err, _ = run_code(m.code, language="javascript")
                self.assertEqual(err.strip(), "")

    def test_the_order_matters_at_all(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                differs = any(
                    _run("\n".join(m.shuffled(seed=s))) != m.expect.strip()
                    for s in range(8)
                )
                self.assertTrue(
                    differs,
                    f"{m.id} prints its answer whatever order it is in")

    def test_the_helper_can_sit_below_the_loop(self) -> None:
        """The first puzzle's note: a function declaration is hoisted,
        so a different order is also right — which is why marking runs
        the program rather than comparing orders."""
        m = _find("magnet-jsg-tick-loop")
        pieces = list(m.pieces)
        moved = [*pieces[0:2], *pieces[5:9], *pieces[2:5], pieces[9]]
        self.assertTrue(same_pieces(m, moved))
        self.assertNotEqual(moved, pieces)
        self.assertEqual(_run("\n".join(moved)), m.expect)

    def test_a_class_used_above_itself_fails(self) -> None:
        m = _find("magnet-jsg-entity-class")
        got = _run(_moved(
            m, 'const fleet = [new Ship("red", 4), new Ship("blue", 6)];', 0))
        self.assertTrue(got.startswith("(exit"))
        self.assertIn("ReferenceError", got)

    def test_reporting_before_updating_is_a_tick_behind(self) -> None:
        m = _find("magnet-jsg-tick-loop")
        got = _run(_moved(m, "  update();", 7))
        self.assertEqual(got, "tick 1 x 0\ntick 2 x 2\ntick 3 x 4\ndone")

    def test_the_timer_loop_lets_the_last_line_in_early(self) -> None:
        """Checked by where "started" lands in the answer."""
        lines = _find("magnet-jsg-timer-loop").expect.split("\n")
        self.assertEqual(lines.index("started"), 1)


class ShuffleTests(unittest.TestCase):
    def test_the_pieces_all_come_back(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    sorted(m.shuffled(seed=1)), sorted(m.pieces))

    def test_it_never_hands_back_the_answer(self) -> None:
        for m in JS_GAME_MAGNETS:
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    self.assertNotEqual(m.shuffled(seed=seed), m.pieces)


class PiecesTests(unittest.TestCase):
    def test_the_right_pieces_are_recognised(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertTrue(same_pieces(m, list(m.shuffled(seed=3))))

    def test_a_missing_piece_is_noticed(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertFalse(same_pieces(m, list(m.pieces[1:])))


class SubgoalTests(unittest.TestCase):
    """The stage labels, held to the stricter list the Ruby set uses."""

    GIVEAWAYS = (
        "(", ")", ";", "{", "}", "=>", "const ", "#", "*", "&", "[", "]",
        "%", "'", "\"", "<", ">", "\\", "|", ":", "=", "`",
    )

    def test_every_puzzle_has_stages(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.plan), 2)

    def test_the_stages_cover_every_line_exactly_once(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                counted = sum(count for _, count in m.plan)
                self.assertEqual(
                    counted, len(m.pieces),
                    f"{m.id}: stages cover {counted} lines of "
                    f"{len(m.pieces)}")
                placed = [line for _, lines in m.stages for line in lines]
                self.assertEqual(placed, list(m.pieces))

    def test_no_stage_is_empty(self) -> None:
        for m in JS_GAME_MAGNETS:
            for label, count in m.plan:
                with self.subTest(magnet=m.id, label=label):
                    self.assertGreater(count, 0)

    def test_the_labels_are_distinct_within_a_puzzle(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(len(set(m.labels)), len(m.labels))

    def test_a_label_is_a_description_not_a_line(self) -> None:
        for m in JS_GAME_MAGNETS:
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper(), "starts as a sentence")
                    for giveaway in self.GIVEAWAYS:
                        self.assertNotIn(giveaway, label)

    def test_the_stages_are_in_program_order(self) -> None:
        for m in JS_GAME_MAGNETS:
            with self.subTest(magnet=m.id):
                rebuilt = "\n".join(
                    line for _, lines in m.stages for line in lines)
                self.assertEqual(rebuilt, m.code)


class RegisteredTests(unittest.TestCase):
    """Through the API, with the set patched into the mode."""

    def _check(self, magnet_id: str, lines: list[str]):
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        return server.magnet_check(
            MagnetCheckRequest(magnet_id=magnet_id, lines=lines))

    def test_the_family_is_served_with_its_language(self) -> None:
        from code_coach.api import server

        with _registered():
            served = server.magnet_list()
        family = next(
            f for f in served["families"] if f["name"] == GAME)
        self.assertEqual(
            [row["id"] for row in family["magnets"]],
            [m.id for m in JS_GAME_MAGNETS])
        for row in family["magnets"]:
            with self.subTest(magnet=row["id"]):
                self.assertEqual(row["language"], "javascript")
                self.assertNotIn("plan", row)

    def test_the_intended_order_passes(self) -> None:
        with _registered():
            for m in JS_GAME_MAGNETS:
                with self.subTest(magnet=m.id):
                    got = self._check(m.id, list(m.pieces))
                    self.assertTrue(got.passed, got.broke or got.printed)

    def test_some_arrangement_is_refused(self) -> None:
        with _registered():
            for m in JS_GAME_MAGNETS:
                with self.subTest(magnet=m.id):
                    refused = any(
                        not self._check(m.id, list(m.shuffled(seed=s))).passed
                        for s in range(6))
                    self.assertTrue(refused, f"{m.id} accepts every order")

    def test_an_error_comes_back_without_the_scratch_path(self) -> None:
        m = _find("magnet-jsg-entity-class")
        lines = list(m.pieces)
        fleet = 'const fleet = [new Ship("red", 4), new Ship("blue", 6)];'
        lines.remove(fleet)
        lines.insert(0, fleet)
        with _registered():
            got = self._check(m.id, lines)
        self.assertFalse(got.passed)
        self.assertTrue(got.broke)
        self.assertIn("ReferenceError", got.broke)
        self.assertNotIn(".js:", got.broke)
        self.assertNotIn(os.sep + "Temp", got.broke)
        self.assertNotIn("/Temp", got.broke)


if __name__ == "__main__":
    unittest.main()
