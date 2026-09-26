"""The Ruby crashes, held to the rules every crash keeps.

`test_errors.py` and `test_errors_dart2.py`, applied to RUBY_CRASHES
before it is registered in `crashes()`. `engine_report` does not read
Ruby's error format yet (it looks for ".js:", ".py" and ".dart:" and
takes the first line naming an Error whole, path and all), so the
load-bearing check goes through `ruby_report` below - the parsing
engine_report needs - and the message and line each crash records are
what Ruby 4 printed.
"""

from __future__ import annotations

import contextlib
import functools
import re
import unittest
from unittest import mock

import code_coach.errors as errors_module
from code_coach.engine import ruby_available, run_code
from code_coach.errors import crash, crashes
from code_coach.errors.content_ruby import RUBY_CRASHES

#: Ruby's first line of red:
#:   C:/.../tmpab12.rb:3:in '<main>': undefined method 'x' for nil (NoMethodError)
#: The path can hold a drive letter's colon, so it is matched lazily up
#: to ".rb:<digits>:". The "in '...': " part is absent for a syntax
#: error, so it is optional.
RUBY_LINE = re.compile(r"^(?:.+?)\.rb:(\d+):(?:in '[^']*': ?)?\s*(.*)$")


def ruby_report(code: str) -> tuple[str, int]:
    """engine_report for Ruby: the message after the method, and the line.

    Returns ("", 0) if the program did not fail.
    """
    _out, err, exit_code = _run(code)
    if exit_code == 0:
        return "", 0
    for raw in err.splitlines():
        found = RUBY_LINE.match(raw.strip())
        if found:
            return found.group(2).strip(), int(found.group(1))
    return "", 0


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="ruby")


def _with_mine(base: tuple) -> tuple:
    have = {c.id for c in base}
    return (*base, *(c for c in RUBY_CRASHES if c.id not in have))


@contextlib.contextmanager
def _registered():
    """crashes() and crash_families() as they will be once RUBY_CRASHES
    is registered."""
    real_crashes, real_families = crashes, errors_module.crash_families

    def with_mine(family: str | None = None):
        everything = _with_mine(real_crashes())
        if family is not None:
            everything = tuple(c for c in everything if c.family == family)
        return tuple(sorted(everything, key=lambda c: c.level))

    def families_with_mine():
        seen = list(real_families())
        return (*seen, "Ruby") if "Ruby" not in seen else tuple(seen)

    with mock.patch.object(errors_module, "crashes", with_mine), \
            mock.patch.object(errors_module, "crash_families",
                              families_with_mine):
        yield


class ShapeTests(unittest.TestCase):
    def test_there_are_six_and_all_ruby(self) -> None:
        self.assertEqual(len(RUBY_CRASHES), 6)
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(c.family, "Ruby")
                self.assertEqual(c.language, "ruby")
                self.assertTrue(c.id.startswith("err-rb-"))

    def test_ids_are_unique_and_new(self) -> None:
        ids = [c.id for c in RUBY_CRASHES]
        self.assertEqual(len(ids), len(set(ids)))
        taken = {c.id for c in crashes() if c not in RUBY_CRASHES}
        self.assertFalse(taken & set(ids))

    def test_no_message_repeats(self) -> None:
        messages = [c.message for c in RUBY_CRASHES]
        self.assertEqual(len(messages), len(set(messages)))

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        levels = [c.level for c in RUBY_CRASHES]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))
                self.assertTrue(c.numbered[c.line - 1][1].strip())

    def test_the_message_is_one_line_without_the_path(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn(".rb:", c.message)
                self.assertNotIn("Did you mean", c.message)
                self.assertRegex(c.message, r"\((\w+Error)\)$")


class ParserTests(unittest.TestCase):
    def test_it_reads_ruby_first_line(self) -> None:
        line = ("C:/Users/x/AppData/Local/Temp/tmpab12.rb:3:in '<main>': "
                "undefined method 'upcase' for nil (NoMethodError)")
        found = RUBY_LINE.match(line)
        self.assertEqual(found.group(1), "3")
        self.assertEqual(found.group(2),
                         "undefined method 'upcase' for nil (NoMethodError)")

    def test_it_reads_a_core_method_frame(self) -> None:
        found = RUBY_LINE.match(
            "/tmp/a.rb:2:in 'String#+': no implicit conversion of Integer "
            "into String (TypeError)")
        self.assertEqual(found.group(1), "2")
        self.assertTrue(found.group(2).startswith("no implicit"))


@unittest.skipUnless(ruby_available(), "Ruby is not installed")
class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                message, line = ruby_report(c.code)
                self.assertEqual(
                    message, c.message, f"{c.id}: ruby says {message!r}")
                self.assertEqual(
                    line, c.line, f"{c.id}: ruby blames line {line}")

    def test_every_one_actually_crashes(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                _out, err, exit_code = _run(c.code)
                self.assertNotEqual(exit_code, 0, f"{c.id} does not crash")
                self.assertNotIn("syntax error", err.lower())


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 3)

    def test_the_answer_is_among_them(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertIn(c.meaning, c.choices)

    def test_the_decoys_are_not_the_answer(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(list(c.choices), sorted(c.choices))

    def test_the_answer_is_not_the_longest_one(self) -> None:
        def longest(pool):
            return [c for c in pool
                    if len(c.meaning) > max(len(d) for d in c.decoys)]

        mine = longest(RUBY_CRASHES)
        self.assertLessEqual(
            len(mine), len(RUBY_CRASHES) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in mine))
        everything = _with_mine(crashes())
        self.assertLessEqual(len(longest(everything)), len(everything) // 2)

    def test_every_one_says_what_to_do(self) -> None:
        for c in RUBY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class RouteTests(unittest.TestCase):
    def _list(self):
        from code_coach.api import server

        return server.error_list()

    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_they_are_served_in_the_ruby_family(self) -> None:
        with _registered():
            served = self._list()
        ruby = next(f for f in served["families"] if f["name"] == "Ruby")
        ids = {row["id"] for row in ruby["crashes"]}
        self.assertTrue({c.id for c in RUBY_CRASHES} <= ids)
        for row in ruby["crashes"]:
            self.assertEqual(row["language"], "ruby")

    def test_every_one_is_findable_by_id(self) -> None:
        with _registered():
            for c in RUBY_CRASHES:
                with self.subTest(crash=c.id):
                    self.assertIs(crash(c.id), c)

    def test_the_answer_does_not_ride_along(self) -> None:
        with _registered():
            served = self._list()
        mine = {c.id for c in RUBY_CRASHES}
        ruby = next(f for f in served["families"] if f["name"] == "Ruby")
        for row in ruby["crashes"]:
            if row["id"] not in mine:
                continue
            with self.subTest(crash=row["id"]):
                self.assertNotIn("line", row)
                self.assertNotIn("meaning", row)
                self.assertNotIn("fix", row)
                self.assertIn("message", row)

    def test_the_right_answer_passes(self) -> None:
        with _registered():
            for c in RUBY_CRASHES:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.meaning)
                    self.assertTrue(got.passed)
                    self.assertTrue(got.fix)

    def test_the_wrong_line_does_not(self) -> None:
        with _registered():
            for c in RUBY_CRASHES:
                with self.subTest(crash=c.id):
                    other = 1 if c.line != 1 else 2
                    got = self._check(c.id, other, c.meaning)
                    self.assertFalse(got.passed)
                    self.assertFalse(got.line_right)
                    self.assertTrue(got.meaning_right)

    def test_the_wrong_reading_does_not(self) -> None:
        with _registered():
            for c in RUBY_CRASHES:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.decoys[0])
                    self.assertFalse(got.passed)
                    self.assertTrue(got.line_right)
                    self.assertFalse(got.meaning_right)


if __name__ == "__main__":
    unittest.main()
