"""The Python code magnets: the same rules as tests/test_magnets.py.

The load-bearing test is `test_every_puzzle_prints_what_it_claims`. A
magnet is marked by running what was arranged and comparing what it
printed, so the typed-out expected output is the whole marker, and here
it is held to what Python prints.

The Magnets screen shows only the puzzles in the language picked at the
top (web/src/components/Magnets.tsx), so these are what a Python learner
sees there; before them it showed JavaScript with Python picked.
"""

from __future__ import annotations

import os
import unittest

from code_coach.engine import run_code
from code_coach.magnets import Magnet, magnet, magnets, same_pieces
from code_coach.magnets.content_python import FAMILY, PY_MAGNETS


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="python")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-300:]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str) -> Magnet:
    return next(m for m in PY_MAGNETS if m.id == magnet_id)


def _moved(m: Magnet, line: str, to: int) -> str:
    """The program with one line taken out and put back at `to`."""
    pieces = list(m.pieces)
    pieces.remove(line)
    pieces.insert(to, line)
    return "\n".join(pieces)


class ShapeTests(unittest.TestCase):
    def test_they_are_one_python_family(self) -> None:
        self.assertGreaterEqual(len(PY_MAGNETS), 8)
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.family, FAMILY)
                self.assertEqual(m.language, "python")

    def test_they_are_registered(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertIs(magnet(m.id), m)
        self.assertEqual([m.id for m in magnets(FAMILY)], [m.id for m in PY_MAGNETS])

    def test_no_id_is_taken_by_another_puzzle(self) -> None:
        ids = [m.id for m in magnets()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_there_is_something_to_arrange(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 8)
                self.assertLessEqual(len(m.pieces), 12)
                for piece in m.pieces:
                    self.assertTrue(piece.strip())
                    self.assertNotIn("\t", piece, "four spaces, never a tab")

    def test_the_ranking_was_done(self) -> None:
        levels = [m.level for m in PY_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreater(len(m.note), 120)
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())


class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(_run(m.code), m.expect.strip())

    def test_the_answers_say_nothing_on_stderr(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                _, err, _ = run_code(m.code, language="python")
                self.assertEqual(err.strip(), "")

    def test_the_order_matters_at_all(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertTrue(any(
                    _run("\n".join(m.shuffled(seed=s))) != m.expect.strip()
                    for s in range(8)
                ))

    def test_a_call_above_its_def_fails(self) -> None:
        m = _find("magnet-py-define-before-call")
        got = _run(_moved(m, 'print(greet("ann"))', 0))
        self.assertTrue(got.startswith("(exit"))
        self.assertIn("NameError", got)

    def test_the_defs_go_either_way_round(self) -> None:
        """Why marking runs the program rather than comparing orders."""
        m = _find("magnet-py-define-before-call")
        p = list(m.pieces)
        swapped = [*p[5:7], *p[2:5], *p[0:2], *p[7:]]
        self.assertTrue(same_pieces(m, swapped))
        self.assertNotEqual(swapped, p)
        self.assertEqual(_run("\n".join(swapped)), m.expect)

    def test_counting_down_before_the_yield_is_off_by_one(self) -> None:
        m = _find("magnet-py-generator")
        got = _run(_moved(m, "        n -= 1", 3))
        self.assertEqual(got, "made it\nstart\n2\n1\n0\nliftoff")

    def test_making_the_generator_after_saying_so_is_also_right(self) -> None:
        m = _find("magnet-py-generator")
        self.assertEqual(_run(_moved(m, 'print("made it")', 6)), m.expect)


class StageTests(unittest.TestCase):
    GIVEAWAYS = ("(", ")", ":", "=", "[", "]", "{", "}", "#", "@", "\"", "'", "*", "+", "<", ">")

    def test_the_stages_cover_every_line_in_order(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.plan), 2)
                self.assertTrue(all(n > 0 for _, n in m.plan))
                self.assertEqual("\n".join(line for _, lines in m.stages for line in lines), m.code)

    def test_a_label_is_a_description_not_a_line(self) -> None:
        for m in PY_MAGNETS:
            self.assertEqual(len(set(m.labels)), len(m.labels), m.id)
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper())
                    for giveaway in self.GIVEAWAYS:
                        self.assertNotIn(giveaway, label)

    def test_the_shuffle_keeps_every_piece_and_never_solves_it(self) -> None:
        for m in PY_MAGNETS:
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    got = m.shuffled(seed=seed)
                    self.assertEqual(sorted(got), sorted(m.pieces))
                    self.assertNotEqual(got, m.pieces)
                    self.assertTrue(same_pieces(m, list(got)))


class RouteTests(unittest.TestCase):
    def _check(self, magnet_id: str, lines: list[str]):
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        return server.magnet_check(MagnetCheckRequest(magnet_id=magnet_id, lines=lines))

    def test_the_family_is_served_as_python(self) -> None:
        from code_coach.api import server

        family = next(f for f in server.magnet_list()["families"] if f["name"] == FAMILY)
        self.assertEqual([r["id"] for r in family["magnets"]], [m.id for m in PY_MAGNETS])
        for row in family["magnets"]:
            self.assertEqual(row["language"], "python")
            self.assertNotIn("plan", row)

    def test_the_intended_order_passes(self) -> None:
        for m in PY_MAGNETS:
            with self.subTest(magnet=m.id):
                got = self._check(m.id, list(m.pieces))
                self.assertTrue(got.passed, got.broke or got.printed)

    def test_an_error_comes_back_without_the_scratch_path(self) -> None:
        m = _find("magnet-py-define-before-call")
        lines = list(m.pieces)
        lines.remove('print(greet("ann"))')
        lines.insert(0, 'print(greet("ann"))')
        got = self._check(m.id, lines)
        self.assertFalse(got.passed)
        self.assertIn("NameError", got.broke)
        self.assertNotIn('.py"', got.broke)
        self.assertNotIn(os.sep + "Temp", got.broke)


if __name__ == "__main__":
    unittest.main()
