"""The C code magnets: the same rules as tests/test_magnets.py.

The load-bearing test is again `test_every_puzzle_prints_what_it_claims`.
A magnet is marked by running what was arranged and comparing what it
printed, so the typed-out expected output is the whole marker, and here
it is held to what the compiled program prints.

These read C_MAGNETS directly rather than through `magnets()`, so they
check the content whether or not it has been registered with the mode
yet. The tests that go through the API skip until it is.

A C compiler is not on every machine. The engine compiles with gcc or
clang from PATH, or falls back to MSVC; without any of them the tests
that run C are skipped rather than failed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_coach.engine import msvc_available, run_code
from code_coach.magnets import Magnet, magnet, magnets, same_pieces
from code_coach.magnets.content_c import C_MAGNETS

FAMILY = "C"
NEEDS_C = "needs a C compiler (gcc, clang or MSVC)"
CLANG = shutil.which("clang") or shutil.which("gcc")
#: Registered once `magnets()` hands back the very objects in this file.
REGISTERED = all(magnet(m.id) is m for m in C_MAGNETS)
NOT_REGISTERED = "C_MAGNETS is not in magnets() yet"


def c_available() -> bool:
    """The same search the engine makes: gcc, clang, then MSVC."""
    return bool(shutil.which("gcc") or shutil.which("clang")
                or msvc_available())


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="c")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[:200]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str) -> Magnet:
    return next(m for m in C_MAGNETS if m.id == magnet_id)


def _moved(m: Magnet, line: str, to: int) -> str:
    """The program with one line taken out and put back at `to`."""
    pieces = list(m.pieces)
    pieces.remove(line)
    pieces.insert(to, line)
    return "\n".join(pieces)


class ShapeTests(unittest.TestCase):
    def test_there_are_six_in_one_family(self) -> None:
        self.assertEqual(len(C_MAGNETS), 6)
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.family, FAMILY)

    def test_every_one_is_run_as_c(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.language, "c")

    def test_ids_are_unique(self) -> None:
        ids = [m.id for m in C_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_id_is_taken_by_another_puzzle(self) -> None:
        mine = {m.id for m in C_MAGNETS}
        others = [
            m.id for m in magnets()
            if not any(m is c for c in C_MAGNETS)
        ]
        self.assertFalse(mine & set(others))

    def test_every_one_is_a_whole_program(self) -> None:
        """One include, one main — C runs nothing outside a function."""
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.pieces[0], "#include <stdio.h>")
                self.assertEqual(m.code.count("int main(void) {"), 1)

    def test_there_is_something_to_arrange(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 8)
                self.assertLessEqual(
                    len(m.pieces), 12, f"{m.id} has {len(m.pieces)} magnets")

    def test_no_magnet_is_blank(self) -> None:
        for m in C_MAGNETS:
            for piece in m.pieces:
                with self.subTest(magnet=m.id):
                    self.assertTrue(piece.strip())

    def test_the_ranking_was_done(self) -> None:
        levels = [m.level for m in C_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreater(
                    len(m.note), 120, f"{m.id}'s note explains nothing")
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())


@unittest.skipUnless(c_available(), NEEDS_C)
class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    _run(m.code), m.expect.strip(),
                    f"{m.id}: the compiler disagrees with the expected output")

    @unittest.skipUnless(CLANG, "needs gcc or clang for the warning check")
    def test_the_answers_compile_without_a_warning(self) -> None:
        """Well-defined C only: nothing a strict compiler would query."""
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                with tempfile.TemporaryDirectory() as tmp:
                    src = Path(tmp) / "magnet.c"
                    src.write_text(m.code + "\n", encoding="utf-8")
                    got = subprocess.run(
                        [CLANG, "-std=c17", "-Wall", "-Wextra", "-pedantic",
                         "-fsyntax-only", str(src)],
                        capture_output=True, text=True, timeout=60)
                self.assertEqual(got.returncode, 0, got.stderr)
                self.assertEqual(got.stderr.strip(), "")

    def test_the_order_matters_at_all(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                differs = any(
                    _run("\n".join(m.shuffled(seed=s))) != m.expect.strip()
                    for s in range(8)
                )
                self.assertTrue(
                    differs,
                    f"{m.id} prints its answer whatever order it is in")

    def test_a_function_below_main_does_not_compile(self) -> None:
        """The first puzzle's note: C is read top to bottom, so a helper
        below its caller is an error, not a different right answer."""
        m = _find("magnet-c-function-before-main")
        pieces = list(m.pieces)
        at = pieces.index("int main(void) {")
        moved = [pieces[0], *pieces[at:], *pieces[1:at]]
        self.assertTrue(same_pieces(m, moved))
        self.assertTrue(_run("\n".join(moved)).startswith("(exit"))

    def test_a_struct_below_main_does_not_compile(self) -> None:
        m = _find("magnet-c-struct")
        pieces = list(m.pieces)
        at = pieces.index("int main(void) {")
        moved = [pieces[0], *pieces[at:], *pieces[1:at]]
        self.assertTrue(_run("\n".join(moved)).startswith("(exit"))

    def test_a_different_correct_order_also_prints_the_answer(self) -> None:
        """Two independent declarations can go either way round, which is
        why marking runs the program rather than comparing orders."""
        m = _find("magnet-c-sum-array")
        total = "    int total = 0;"
        again = _moved(m, total, 2)
        self.assertNotEqual(again, m.code)
        self.assertEqual(_run(again), m.expect)

    def test_printing_before_the_fill_shows_zero_pages(self) -> None:
        m = _find("magnet-c-struct")
        line = next(p for p in m.pieces if "printf" in p)
        self.assertEqual(_run(_moved(m, line, 7)), "Dune has 0 pages")

    def test_overwriting_before_saving_loses_the_value(self) -> None:
        """The swap puzzle's note, checked: assign first and both are 2."""
        m = _find("magnet-c-pointer-swap")
        self.assertEqual(
            _run(_moved(m, "    int held = *a;", 3)), "left 2, right 2")

    def test_a_break_in_the_wrong_place_falls_through(self) -> None:
        m = _find("magnet-c-switch-break")
        self.assertEqual(
            _run(_moved(m, "            break;", 8)),
            "one\nmore\nmore\nmore")


class ShuffleTests(unittest.TestCase):
    def test_the_pieces_all_come_back(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    sorted(m.shuffled(seed=1)), sorted(m.pieces))

    def test_it_never_hands_back_the_answer(self) -> None:
        for m in C_MAGNETS:
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    self.assertNotEqual(m.shuffled(seed=seed), m.pieces)


class PiecesTests(unittest.TestCase):
    def test_the_right_pieces_are_recognised(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertTrue(same_pieces(m, list(m.shuffled(seed=3))))

    def test_a_repeated_closing_brace_is_counted(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                pieces = list(m.pieces)
                self.assertGreaterEqual(pieces.count("}"), 1)
                pieces.remove("}")
                self.assertFalse(same_pieces(m, pieces))


class SubgoalTests(unittest.TestCase):
    """The stage labels, with C's own giveaways added to the list."""

    GIVEAWAYS = (
        "(", ")", ";", "{", "}", "=>", "#", "*", "&", "[", "]", "%",
        "'", "\"", "<", ">", "\\",
    )

    def test_every_puzzle_has_stages(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.plan), 2)

    def test_the_stages_cover_every_line_exactly_once(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                counted = sum(count for _, count in m.plan)
                self.assertEqual(
                    counted, len(m.pieces),
                    f"{m.id}: stages cover {counted} lines of "
                    f"{len(m.pieces)}")
                placed = [line for _, lines in m.stages for line in lines]
                self.assertEqual(placed, list(m.pieces))

    def test_no_stage_is_empty(self) -> None:
        for m in C_MAGNETS:
            for label, count in m.plan:
                with self.subTest(magnet=m.id, label=label):
                    self.assertGreater(count, 0)

    def test_the_labels_are_distinct_within_a_puzzle(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(len(set(m.labels)), len(m.labels))

    def test_a_label_is_a_description_not_a_line(self) -> None:
        for m in C_MAGNETS:
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper(), "starts as a sentence")
                    for giveaway in self.GIVEAWAYS:
                        self.assertNotIn(giveaway, label)

    def test_the_stages_are_in_program_order(self) -> None:
        for m in C_MAGNETS:
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
            [m.id for m in C_MAGNETS])
        for row in family["magnets"]:
            with self.subTest(magnet=row["id"]):
                self.assertEqual(row["language"], "c")
                self.assertNotIn("plan", row)

    @unittest.skipUnless(c_available(), NEEDS_C)
    def test_the_intended_order_passes(self) -> None:
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                got = self._check(m.id, list(m.pieces))
                self.assertTrue(got.passed, got.broke or got.printed)

    @unittest.skipUnless(c_available(), NEEDS_C)
    def test_some_arrangement_is_refused_with_a_reason(self) -> None:
        """A C jumble almost never compiles, so the refusal is a compiler
        error. It has to come back without the scratch file's path."""
        for m in C_MAGNETS:
            with self.subTest(magnet=m.id):
                refused = None
                for seed in range(6):
                    got = self._check(m.id, list(m.shuffled(seed=seed)))
                    if not got.passed:
                        refused = got
                        break
                self.assertIsNotNone(refused, f"{m.id} accepts every order")
                assert refused is not None
                self.assertTrue(refused.broke)
                self.assertNotIn(".c:", refused.broke)
                self.assertNotIn(os.sep + "Temp", refused.broke)


if __name__ == "__main__":
    unittest.main()
