"""The Rust and TypeScript crashes, held to the rules every crash keeps.

The load-bearing test is `test_the_engine_says_exactly_this`: the message and
line each one records are what rustc or tsc printed, read through
`engine_report`. For Rust that is the `error[E...]` line and the line after
its ` --> `, or, for a panic, the line after `panicked at file.rs:L:C:`. For
TypeScript it is the first `error TS...` and the line in its brackets.
"""

from __future__ import annotations

import shutil
import unittest
from unittest import mock

from code_coach.engine import typescript_available
from code_coach.errors import crash, crashes, engine_report
from code_coach.errors.content_rust import RUST_CRASHES
from code_coach.errors.content_ts import TS_CRASHES

SETS = (("rust", "Rust", RUST_CRASHES), ("typescript", "TypeScript", TS_CRASHES))


def _usable(language: str) -> bool:
    return typescript_available() if language == "typescript" else shutil.which("rustc") is not None


class ShapeTests(unittest.TestCase):
    def test_each_set_is_registered_in_one_language(self) -> None:
        ids = [c.id for c in crashes()]
        self.assertEqual(len(ids), len(set(ids)))
        for language, family, items in SETS:
            self.assertGreaterEqual(len(items), 12)
            levels = [c.level for c in items]
            self.assertEqual(levels, sorted(levels))
            for c in items:
                with self.subTest(crash=c.id):
                    self.assertEqual((c.language, c.family), (language, family))
                    self.assertIs(crash(c.id), c)
                    self.assertLessEqual(len(c.numbered), 10)
                    self.assertGreaterEqual(c.line, 1)
                    self.assertLessEqual(c.line, len(c.numbered))
                    self.assertTrue(c.numbered[c.line - 1][1].strip())
                    self.assertNotIn("\n", c.message)
                    self.assertGreater(len(c.fix), 120)

    def test_the_choices_are_fair(self) -> None:
        for _, family, items in SETS:
            for c in items:
                with self.subTest(crash=c.id):
                    self.assertGreaterEqual(len(c.choices), 4)
                    self.assertNotIn(c.meaning, c.decoys)
                    self.assertEqual(list(c.choices), sorted(c.choices))
            longest = sum(len(c.meaning) > max(len(d) for d in c.decoys) for c in items)
            with self.subTest(family=family):
                self.assertLessEqual(longest, len(items) // 2, "the answer is the longest too often")
                self.assertGreater(longest, 0, "the answer is never the longest, which is a tell too")


class ParserTests(unittest.TestCase):
    def _report(self, err: str, language: str):
        with mock.patch("code_coach.engine.run_code", return_value=("", err, 1)):
            return engine_report("x", language)

    def test_rust_compile_error(self) -> None:
        err = ("error[E0382]: borrow of moved value: `s`\n"
               " --> C:\\Users\\x\\AppData\\Local\\Temp\\tmp1.rs:4:23\n  |\n")
        self.assertEqual(self._report(err, "rust"), ("error[E0382]: borrow of moved value: `s`", 4))

    def test_rust_panic(self) -> None:
        err = ("\nthread 'main' (20440) panicked at C:\\Temp\\tmp2.rs:4:21:\n"
               "index out of bounds: the len is 3 but the index is 5\nnote: run with `RUST_BACKTRACE=1`\n")
        self.assertEqual(self._report(err, "rust"), ("index out of bounds: the len is 3 but the index is 5", 4))

    def test_typescript_type_error(self) -> None:
        err = "../../Temp/tmp3.ts(2,1): error TS2322: Type 'string' is not assignable to type 'number'.\n"
        self.assertEqual(self._report(err, "typescript"),
                         ("error TS2322: Type 'string' is not assignable to type 'number'.", 2))


class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for language, _, items in SETS:
            if not _usable(language):
                continue
            for c in items:
                with self.subTest(crash=c.id):
                    self.assertEqual(engine_report(c.code, language), (c.message, c.line))


class RouteTests(unittest.TestCase):
    def test_served_without_answers_and_marked(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        served = {f["name"]: f for f in server.error_list()["families"]}
        for language, family, items in SETS:
            with self.subTest(family=family):
                rows = served[family]["crashes"]
                self.assertEqual({r["id"] for r in rows}, {c.id for c in items})
                for r in rows:
                    self.assertEqual(r["language"], language)
                    for hidden in ("line", "meaning", "fix"):
                        self.assertNotIn(hidden, r)
                c = items[0]
                self.assertTrue(server.error_check(ErrorCheckRequest(crash_id=c.id, line=c.line, meaning=c.meaning)).passed)
                self.assertFalse(server.error_check(ErrorCheckRequest(crash_id=c.id, line=c.line, meaning=c.decoys[0])).passed)


if __name__ == "__main__":
    unittest.main()
