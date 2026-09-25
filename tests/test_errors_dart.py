"""Reading error messages, in Dart.

The same rules `test_errors.py` holds every crash to, applied to the
Dart family before it is registered in `crashes()`. The load-bearing
one is still `test_the_engine_says_exactly_this`: the message and the
line each crash records are what `dart run` really printed, and a Dart
release that rewords a message fails here rather than quietly marking
people wrong.

Why this file reads Dart's output itself
----------------------------------------
`engine_report` does not understand Dart yet, for two reasons that are
both about the shape of what Dart prints:

    Unhandled exception:
    Concurrent modification during iteration: Instance(length:2) ...
    #0      ListIterator.moveNext (dart:_internal/iterable.dart:365:7)
    #1      main (file:///C:/.../tmpabc.dart:3:22)

The message is the line after "Unhandled exception:" and need not say
Error — so the rule "first line that names an error" finds nothing, or,
for a FormatException, finds a frame (`int._handleFormatError`). And the
first frame with a line number is often the SDK's (`dart:...`), not the
program's. `_read_dart` below is the reading engine_report needs; once
it has it, `test_engine_report_agrees` holds the two together.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.errors as errors_module
from code_coach.engine import dart_available, run_code
from code_coach.errors import crash, crash_families, crashes, engine_report
from code_coach.errors.content_dart import DART_CRASHES


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    """Each program once. `dart run` compiles before it runs, which is
    about two seconds a go, and three tests want the same run."""
    return run_code(code, language="dart")


def _read_dart(err: str) -> tuple[str, int]:
    """The message and the line, out of what Dart printed.

    The message is the first non-blank line after "Unhandled exception:".
    Only that line: a FormatException echoes the rejected text and a
    caret on the lines under it, which belong to the terminal, not the
    question.

    The line is the first frame that is not inside the SDK — SDK frames
    read `(dart:core-patch/...)` — and that has a number after `.dart:`.
    A late field's getter is a frame in your own file with no line at
    all, `Profile.name (file:///.../x.dart)`, which is why the number is
    required rather than assumed.
    """
    message, line, previous = "", 0, ""
    for raw in err.splitlines():
        text = raw.strip()
        if not text:
            continue
        if not message and previous == "Unhandled exception:":
            message = text
        previous = text
        if not line and "(dart:" not in text and ".dart:" in text:
            after = text.split(".dart:", 1)[1]
            digits = ""
            for ch in after:
                if ch.isdigit():
                    digits += ch
                else:
                    break
            if digits:
                line = int(digits)
    return message, line


def _dart_report(code: str) -> tuple[str, int]:
    """engine_report's contract — ("", 0) if it did not fail — for Dart."""
    _out, err, exit_code = _run(code)
    if exit_code == 0:
        return "", 0
    return _read_dart(err)


def _with_dart(base: tuple) -> tuple:
    """Everything crashes() returns plus the Dart ones, once each — so
    this keeps working after DART_CRASHES is registered for real."""
    have = {c.id for c in base}
    return (*base, *(c for c in DART_CRASHES if c.id not in have))


@contextlib.contextmanager
def _registered():
    """crashes() and crash_families() as they will be once DART_CRASHES
    is registered, so the rules that are about the whole set, and the
    routes, can be run against it now."""
    real_crashes, real_families = crashes, crash_families

    def with_dart(family: str | None = None):
        everything = _with_dart(real_crashes())
        if family is not None:
            everything = tuple(c for c in everything if c.family == family)
        return tuple(sorted(everything, key=lambda c: c.level))

    def families_with_dart():
        seen = list(real_families())
        return (*seen, "Dart") if "Dart" not in seen else tuple(seen)

    with mock.patch.object(errors_module, "crashes", with_dart), \
            mock.patch.object(errors_module, "crash_families",
                              families_with_dart):
        yield


class ShapeTests(unittest.TestCase):
    def test_there_are_enough_to_be_a_family(self) -> None:
        self.assertGreaterEqual(len(DART_CRASHES), 3)
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(c.family, "Dart")
                self.assertEqual(c.language, "dart")

    def test_ids_are_unique_and_new(self) -> None:
        """Unique among themselves, and not already taken by a crash
        that is registered, or crash(id) would find the wrong one."""
        ids = [c.id for c in DART_CRASHES]
        self.assertEqual(len(ids), len(set(ids)))
        taken = {c.id for c in crashes() if c.language != "dart"}
        self.assertFalse(taken & set(ids))

    def test_every_one_is_a_program(self) -> None:
        """Dart runs nothing without a main, and would fail to compile
        rather than crash — a different lesson from the one on offer."""
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertIn("void main()", c.code)

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        """The line question is only fair if you can see every line at
        once. A thirty-line program turns 'which line' into scrolling."""
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        """Easiest first as written, not only once crashes() sorts."""
        levels = [c.level for c in DART_CRASHES]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))

    def test_the_message_is_one_line(self) -> None:
        """The frames under it are about the runtime, not about you, and
        putting them on screen is what makes people stop reading the
        part that matters."""
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn("#0 ", c.message)
                self.assertNotIn("Unhandled exception", c.message)


@unittest.skipUnless(dart_available(), "dart is not on PATH")
class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        """The one everything else rests on.

        Both the message and the line are Dart's own report. If either
        drifts, every person answering this question is being marked
        against something that is not true any more.
        """
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                message, line = _dart_report(c.code)
                self.assertEqual(
                    message, c.message,
                    f"{c.id}: dart says {message!r}")
                self.assertEqual(
                    line, c.line,
                    f"{c.id}: dart blames line {line}")

    def test_every_one_actually_crashes(self) -> None:
        """A program that runs fine has no error to read, and would be
        marked by comparing two blanks."""
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                _out, _err, exit_code = _run(c.code)
                self.assertNotEqual(exit_code, 0, f"{c.id} does not crash")

    def test_it_crashed_running_not_compiling(self) -> None:
        """These are runtime errors: the program compiled and then died.

        A compile error looks superficially similar — also a message,
        also a line — but it is a different lesson, and Dart is strict
        enough that an innocent-looking edit turns one into the other.
        Reading an unassigned late local, for one, is refused at compile
        time. Dart exits 255 for an unhandled exception and 254 for a
        compile error, and only the first begins "Unhandled exception:".
        """
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                _out, err, exit_code = _run(c.code)
                first = next(
                    (t.strip() for t in err.splitlines() if t.strip()), "")
                self.assertEqual(first, "Unhandled exception:", err)
                self.assertEqual(exit_code, 255, err)

    def test_engine_report_agrees(self) -> None:
        """Once engine_report reads Dart, it must read it this way.

        Skipped until then, and says so, rather than passing quietly.
        """
        if engine_report(DART_CRASHES[0].code, "dart") == ("", 0):
            self.skipTest("engine_report does not read Dart yet")
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(
                    engine_report(c.code, c.language), _dart_report(c.code))


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 3)

    def test_the_answer_is_among_them(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertIn(c.meaning, c.choices)

    def test_the_decoys_are_not_the_answer(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(list(c.choices), sorted(c.choices))

    def test_the_answer_is_not_the_longest_one(self) -> None:
        """Which is the oldest tell in multiple choice, and a reader
        picks up on it long before noticing they have. Held within the
        family, and across everything once the family is added, since
        that is the form test_errors.py checks it in."""
        def longest(pool):
            return [c for c in pool
                    if len(c.meaning) > max(len(d) for d in c.decoys)]

        mine = longest(DART_CRASHES)
        self.assertLessEqual(
            len(mine), len(DART_CRASHES) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in mine))
        everything = _with_dart(crashes())
        self.assertLessEqual(len(longest(everything)), len(everything) // 2)

    def test_every_one_says_what_to_do(self) -> None:
        for c in DART_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class RouteTests(unittest.TestCase):
    """What the screen is served, and what it is not — with the family
    registered the way it will be."""

    def _list(self):
        from code_coach.api import server

        return server.error_list()

    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_the_family_is_served_and_complete(self) -> None:
        with _registered():
            served = self._list()
            names = [f["name"] for f in served["families"]]
            self.assertEqual(names, list(errors_module.crash_families()))
            dart = next(f for f in served["families"] if f["name"] == "Dart")
            # Every one of these is served. Not "only these": later Dart
            # sets join the same family.
            self.assertLessEqual(
                {c.id for c in DART_CRASHES},
                {row["id"] for row in dart["crashes"]})
            for row in dart["crashes"]:
                self.assertEqual(row["language"], "dart")

    def test_every_one_is_findable_by_id(self) -> None:
        with _registered():
            for c in DART_CRASHES:
                with self.subTest(crash=c.id):
                    self.assertIs(crash(c.id), c)

    def test_the_answer_does_not_ride_along(self) -> None:
        """The message and the program have to be served — they are the
        question. The line it blames and the right reading must not be,
        and neither must the fix, which names the answer in prose."""
        with _registered():
            served = self._list()
        dart = next(f for f in served["families"] if f["name"] == "Dart")
        for row in dart["crashes"]:
            with self.subTest(crash=row["id"]):
                self.assertNotIn("line", row)
                self.assertNotIn("meaning", row)
                self.assertNotIn("fix", row)
                self.assertIn("message", row)

    def test_the_right_answer_passes(self) -> None:
        with _registered():
            for c in DART_CRASHES:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.meaning)
                    self.assertTrue(got.passed)
                    self.assertTrue(got.fix)

    def test_the_wrong_line_does_not(self) -> None:
        with _registered():
            for c in DART_CRASHES:
                with self.subTest(crash=c.id):
                    other = 1 if c.line != 1 else 2
                    got = self._check(c.id, other, c.meaning)
                    self.assertFalse(got.passed)
                    self.assertFalse(got.line_right)
                    self.assertTrue(got.meaning_right)

    def test_the_wrong_reading_does_not(self) -> None:
        with _registered():
            for c in DART_CRASHES:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.decoys[0])
                    self.assertFalse(got.passed)
                    self.assertTrue(got.line_right)
                    self.assertFalse(got.meaning_right)


if __name__ == "__main__":
    unittest.main()
