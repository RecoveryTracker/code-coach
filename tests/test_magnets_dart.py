"""The Dart code magnets: the same rules as tests/test_magnets.py.

The load-bearing test is again `test_every_puzzle_prints_what_it_claims`.
A magnet is marked by running what was arranged and comparing what it
printed, so the typed-out expected output is the whole marker, and here
it is held to what `dart run` prints.

These read DART_MAGNETS directly rather than through `magnets()`, so
they check the content whether or not it has been registered with the
mode yet. The tests that go through the API — marking an arrangement,
serving the list — can only see a registered puzzle, so they skip until
it is.

Dart comes with Flutter and is not on every machine. Without it the
tests that run Dart are skipped rather than failed; the ones that only
read the content still run.
"""

from __future__ import annotations

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.magnets import Magnet, magnet, magnets, same_pieces
from code_coach.magnets.content_dart import DART_MAGNETS

FAMILY = "Dart"
NEEDS_DART = "needs dart (it comes with Flutter)"
#: Registered once `magnets()` hands back the very objects in this file.
REGISTERED = all(magnet(m.id) is m for m in DART_MAGNETS)
NOT_REGISTERED = "DART_MAGNETS is not in magnets() yet"


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="dart")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[:200]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str) -> Magnet:
    return next(m for m in DART_MAGNETS if m.id == magnet_id)


class ShapeTests(unittest.TestCase):
    def test_there_are_six_in_one_family(self) -> None:
        self.assertEqual(len(DART_MAGNETS), 6)
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.family, FAMILY)

    def test_every_one_is_run_as_dart(self) -> None:
        """The marker runs a puzzle in its own language. A Dart program
        left on the JavaScript default would fail every arrangement,
        including the right one."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.language, "dart")

    def test_ids_are_unique(self) -> None:
        ids = [m.id for m in DART_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_id_is_taken_by_another_puzzle(self) -> None:
        """`magnet(id)` returns the first match, so a clash would hand
        out somebody else's puzzle to be marked against."""
        mine = {m.id for m in DART_MAGNETS}
        others = [
            m.id for m in magnets()
            if not any(m is d for d in DART_MAGNETS)
        ]
        self.assertFalse(mine & set(others))

    def test_every_one_is_a_whole_program(self) -> None:
        """Dart runs nothing that is not reached from main."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(m.code.count("main()"), 1)

    def test_there_is_something_to_arrange(self) -> None:
        """The same ceiling as the JavaScript puzzles, because once these
        are registered that suite holds them to it too. The floor is
        higher: a Dart program spends two magnets on main alone."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 8)
                self.assertLessEqual(
                    len(m.pieces), 12, f"{m.id} has {len(m.pieces)} magnets")

    def test_no_magnet_is_blank(self) -> None:
        for m in DART_MAGNETS:
            for piece in m.pieces:
                with self.subTest(magnet=m.id):
                    self.assertTrue(piece.strip())

    def test_the_ranking_was_done(self) -> None:
        """Easiest first in the file as well as in `magnets()`, which
        sorts by level — so reading the file is reading the course."""
        levels = [m.level for m in DART_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreater(
                    len(m.note), 120, f"{m.id}'s note explains nothing")
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())


@unittest.skipUnless(dart_available(), NEEDS_DART)
class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        """The one the marking rests on: what a person typed against
        what Dart does."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    _run(m.code), m.expect.strip(),
                    f"{m.id}: dart disagrees with the expected output")

    def test_the_order_matters_at_all(self) -> None:
        """Some arrangement of the lines has to print something other
        than the answer, or there is no puzzle in it. Stated that way
        round for the reason given in tests/test_magnets.py: a
        particular jumble may be genuinely correct."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                differs = any(
                    _run("\n".join(m.shuffled(seed=s))) != m.expect.strip()
                    for s in range(8)
                )
                self.assertTrue(
                    differs,
                    f"{m.id} prints its answer whatever order it is in")

    def test_a_different_correct_order_also_prints_the_answer(self) -> None:
        """Dart reads every top-level declaration before it runs, so a
        class can sit below the main that uses it. That arrangement is
        right, and it is the reason marking runs the program rather
        than comparing orders."""
        m = _find("magnet-dart-named-constructor")
        pieces = list(m.pieces)
        at = pieces.index("void main() {")
        moved = [*pieces[at:], *pieces[:at]]
        self.assertNotEqual(moved, list(m.pieces))
        self.assertTrue(same_pieces(m, moved))
        self.assertEqual(_run("\n".join(moved)), m.expect)

    def test_the_catch_all_first_is_wrong_but_runs(self) -> None:
        """The switch puzzle's note claims `_` first still compiles and
        gives every value the same advice. That is its lesson, so it is
        checked rather than trusted: if Dart ever made it a compile
        error, the note would be teaching something false."""
        m = _find("magnet-dart-switch-enum")
        pieces = list(m.pieces)
        wild = next(p for p in pieces if p.strip().startswith("_ =>"))
        pieces.remove(wild)
        pieces.insert(2, wild)
        printed = _run("\n".join(pieces))
        self.assertFalse(printed.startswith("(exit"), printed)
        self.assertNotEqual(printed, m.expect)
        self.assertEqual(
            {line.split(": ", 1)[1] for line in printed.splitlines()},
            {"go as you are"})

    def test_moving_a_print_across_an_await_moves_it_in_the_output(
        self,
    ) -> None:
        """The async puzzle's note, checked: the same lines, with the
        second print above the await instead of below it."""
        m = _find("magnet-dart-await")
        pieces = list(m.pieces)
        resumes = next(p for p in pieces if "load resumes" in p)
        pieces.remove(resumes)
        pieces.insert(2, resumes)
        self.assertEqual(
            _run("\n".join(pieces)),
            "load starts\nload resumes\nmain carries on\ndata")


class ShuffleTests(unittest.TestCase):
    def test_the_pieces_all_come_back(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    sorted(m.shuffled(seed=1)), sorted(m.pieces))

    def test_it_never_hands_back_the_answer(self) -> None:
        for m in DART_MAGNETS:
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    self.assertNotEqual(m.shuffled(seed=seed), m.pieces)


class PiecesTests(unittest.TestCase):
    def test_the_right_pieces_are_recognised(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertTrue(same_pieces(m, list(m.shuffled(seed=3))))

    def test_a_repeated_closing_brace_is_counted(self) -> None:
        """Every Dart puzzle has several lines that are just `}`, so
        dropping one has to be noticed rather than lost in a set."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                pieces = list(m.pieces)
                self.assertGreaterEqual(pieces.count("}"), 1)
                pieces.remove("}")
                self.assertFalse(same_pieces(m, pieces))


class SubgoalTests(unittest.TestCase):
    """The stage labels, held to the same rules as the JavaScript ones,
    with Dart's own giveaways added to the list a label may not carry."""

    GIVEAWAYS = (
        "(", ")", ";", "{", "}", "=>", "const ", "final ", "..", "<", ">",
        "$",
    )

    def test_every_puzzle_has_stages(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.plan), 2)

    def test_the_stages_cover_every_line_exactly_once(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                counted = sum(count for _, count in m.plan)
                self.assertEqual(
                    counted, len(m.pieces),
                    f"{m.id}: stages cover {counted} lines of "
                    f"{len(m.pieces)}")
                placed = [line for _, lines in m.stages for line in lines]
                self.assertEqual(placed, list(m.pieces))

    def test_no_stage_is_empty(self) -> None:
        for m in DART_MAGNETS:
            for label, count in m.plan:
                with self.subTest(magnet=m.id, label=label):
                    self.assertGreater(count, 0)

    def test_the_labels_are_distinct_within_a_puzzle(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(len(set(m.labels)), len(m.labels))

    def test_a_label_is_a_description_not_a_line(self) -> None:
        for m in DART_MAGNETS:
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper(), "starts as a sentence")
                    for giveaway in self.GIVEAWAYS:
                        self.assertNotIn(giveaway, label)

    def test_the_stages_are_in_program_order(self) -> None:
        for m in DART_MAGNETS:
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
            [m.id for m in DART_MAGNETS])
        for row in family["magnets"]:
            with self.subTest(magnet=row["id"]):
                self.assertEqual(row["language"], "dart")
                self.assertNotIn("plan", row)

    @unittest.skipUnless(dart_available(), NEEDS_DART)
    def test_the_intended_order_passes(self) -> None:
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                got = self._check(m.id, list(m.pieces))
                self.assertTrue(got.passed, got.broke or got.printed)

    @unittest.skipUnless(dart_available(), NEEDS_DART)
    def test_a_class_below_main_is_marked_right(self) -> None:
        m = _find("magnet-dart-named-constructor")
        pieces = list(m.pieces)
        at = pieces.index("void main() {")
        self.assertTrue(
            self._check(m.id, [*pieces[at:], *pieces[:at]]).passed)

    @unittest.skipUnless(dart_available(), NEEDS_DART)
    def test_some_arrangement_is_refused_with_a_reason(self) -> None:
        """A Dart jumble almost never compiles, so the refusal is
        usually a compile error. It has to come back as a reason to
        read, without the scratch file's path in it."""
        for m in DART_MAGNETS:
            with self.subTest(magnet=m.id):
                refused = None
                for seed in range(6):
                    got = self._check(m.id, list(m.shuffled(seed=seed)))
                    if not got.passed:
                        refused = got
                        break
                self.assertIsNotNone(refused, f"{m.id} accepts every order")
                assert refused is not None
                self.assertNotIn(".dart:", refused.broke)


if __name__ == "__main__":
    unittest.main()
