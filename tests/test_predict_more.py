"""The TypeScript, Rust and second C Predict sets, held to Predict's rules.

The load-bearing test is `test_the_language_agrees_with_every_answer`: each
expected output was typed out first and is held to what the real compiler
and runtime print. The Rust and C sets are also held to compiling without a
single warning - the engine throws a successful build's warnings away, so a
passing run alone says nothing about them - and each family belongs to one
language, so the language picker shows it in the right place.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

from code_coach.engine import c_available, run_code, typescript_available
from code_coach.kata.predict import PUZZLES, language_of, predict_families, puzzle
from code_coach.kata.predict_c2 import C_PUZZLES_2
from code_coach.kata.predict_cpp import CPP_PUZZLES
from code_coach.kata.predict_rust import RUST_PUZZLES
from code_coach.kata.predict_ts import TS_PUZZLES

SETS = (("typescript", "TypeScript", TS_PUZZLES), ("rust", "Rust", RUST_PUZZLES), ("c", "C", C_PUZZLES_2),
        ("cpp", "C++", CPP_PUZZLES))
RUSTC = shutil.which("rustc")
CC = shutil.which("clang") or shutil.which("gcc")
CXX = shutil.which("clang++") or shutil.which("g++")


def _can_run(language: str) -> bool:
    return {"typescript": typescript_available(), "rust": RUSTC is not None, "c": c_available(),
            "cpp": CXX is not None}[language]


class ShapeTests(unittest.TestCase):
    def test_each_set_is_one_family_in_one_language(self) -> None:
        for language, family, items in SETS:
            with self.subTest(family=family):
                self.assertGreaterEqual(len(items), 12)
                for p in items:
                    self.assertEqual((p.language, p.family), (language, family), p.id)
                self.assertEqual(language_of(family), language)

    def test_they_are_registered_and_unique(self) -> None:
        ids = [p.id for p in PUZZLES]
        self.assertEqual(len(ids), len(set(ids)))
        for _, family, items in SETS:
            for p in items:
                with self.subTest(puzzle=p.id):
                    self.assertIs(puzzle(p.id), p)
            if _can_run(items[0].language):
                self.assertIn(family, predict_families())

    def test_every_puzzle_is_ranked_and_explained(self) -> None:
        for _, family, items in SETS:
            levels = [p.level for p in items]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels), "least surprising first")
                self.assertGreater(len(set(levels)), 2)
            for p in items:
                with self.subTest(puzzle=p.id):
                    self.assertIn(p.level, range(1, 6))
                    self.assertTrue(p.name.strip())
                    self.assertGreater(len(p.why), 150)
                    self.assertTrue(p.expect.strip())
                    self.assertNotIn(p.expect, p.code, "the answer is sitting in the snippet")
                    self.assertLessEqual(len(p.code.split("\n")), 16)


class OutputTests(unittest.TestCase):
    def test_the_language_agrees_with_every_answer(self) -> None:
        for language, _, items in SETS:
            if not _can_run(language):
                continue
            for p in items:
                with self.subTest(puzzle=p.id):
                    out, err, code = run_code(p.code, language=language)
                    self.assertEqual(code, 0, (err or out)[:300])
                    self.assertEqual(out.replace("\r\n", "\n").rstrip("\n"), p.expect)

    @unittest.skipUnless(RUSTC, "rustc is not installed")
    def test_rust_compiles_without_a_warning(self) -> None:
        for p in RUST_PUZZLES:
            with self.subTest(puzzle=p.id):
                folder = tempfile.mkdtemp(prefix="predict_rs_")
                try:
                    src = os.path.join(folder, "main.rs")
                    with open(src, "w", encoding="utf-8") as f:
                        f.write(p.code)
                    built = subprocess.run(
                        [RUSTC, "--edition", "2021", "--emit=metadata", "-o", os.path.join(folder, "out"), src],
                        capture_output=True, text=True, timeout=120)
                finally:
                    shutil.rmtree(folder, ignore_errors=True)
                self.assertEqual(built.returncode, 0, built.stderr[:300])
                self.assertNotIn("warning", built.stderr, built.stderr[:300])

    @unittest.skipUnless(CC, "no gcc or clang to ask for warnings")
    def test_c_compiles_without_a_warning(self) -> None:
        for p in C_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                fd, path = tempfile.mkstemp(suffix=".c")
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        f.write(p.code)
                    built = subprocess.run([CC, "-std=c17", "-Wall", "-Wextra", "-pedantic", "-fsyntax-only", path],
                                           capture_output=True, text=True, timeout=60)
                finally:
                    os.unlink(path)
                self.assertEqual(built.returncode, 0, built.stderr[:300])
                self.assertEqual(built.stderr.strip(), "", built.stderr[:300])

    def test_c_programs_are_whole_short_programs(self) -> None:
        for p in C_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.code.startswith("#include <stdio.h>\n"))
                self.assertIn("int main(void) {", p.code)


class RouteTests(unittest.TestCase):
    def test_served_with_their_language_and_marked(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        served = {f["name"]: f for f in server.predict_list()["families"]}
        for language, family, items in SETS:
            if not _can_run(language):
                continue
            with self.subTest(family=family):
                self.assertEqual(served[family]["language"], language)
                self.assertNotIn("expect", served[family]["puzzles"][0])
                p = items[0]
                self.assertTrue(server.predict_check(PredictCheckRequest(puzzle_id=p.id, guess=p.expect)).passed)
                self.assertFalse(server.predict_check(PredictCheckRequest(puzzle_id=p.id, guess="nope")).passed)


if __name__ == "__main__":
    unittest.main()
