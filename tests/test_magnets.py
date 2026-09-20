"""The code magnet puzzles.

The load-bearing test is `test_every_puzzle_prints_what_it_claims`. The
puzzles are marked by running what you arranged and comparing the
output, so the expected output is the whole marker — and it is typed
out by a person, which is what makes it worth anything and also what
makes it worth checking. Same way round as the predict puzzles: the
engine is the authority on what a program prints, and the hand-written
copy is what catches a puzzle that has stopped demonstrating what its
note says.

The other one that earns its keep is
`test_a_different_correct_order_also_passes`. Marking by output rather
than by line order is the whole design, and a marker that quietly went
back to comparing orders would pass every test above this one.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.magnets import (
    magnet,
    magnet_families,
    magnets,
    same_pieces,
)


def _run(code: str, language: str = "javascript") -> str:
    out, err, code_out = run_code(code, language=language)
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[:200]}"
    return out.replace("\r\n", "\n").strip()


class ShapeTests(unittest.TestCase):
    def test_there_are_some_in_every_family(self) -> None:
        self.assertGreaterEqual(len(magnets()), 12)
        for family in magnet_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(magnets(family)), 3)

    def test_ids_are_unique(self) -> None:
        ids = [m.id for m in magnets()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_puzzle_is_findable_by_id(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertIs(magnet(m.id), m)

    def test_there_is_something_to_arrange(self) -> None:
        """Two magnets is not a puzzle, and twenty is a jigsaw. The
        thing being practised — which line goes before which — is drilled
        as well by six as by twenty, and six can be done three times."""
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(len(m.pieces), 3)
                self.assertLessEqual(
                    len(m.pieces), 12, f"{m.id} has {len(m.pieces)} magnets")

    def test_no_magnet_is_blank(self) -> None:
        """A blank line is not a piece anybody can place."""
        for m in magnets():
            for piece in m.pieces:
                with self.subTest(magnet=m.id):
                    self.assertTrue(piece.strip())

    def test_the_ranking_was_done(self) -> None:
        for family in magnet_families():
            with self.subTest(family=family):
                levels = [m.level for m in magnets(family)]
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                for level in levels:
                    self.assertIn(level, range(1, 6))

    def test_every_puzzle_says_what_it_is_for(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertGreater(
                    len(m.note), 120, f"{m.id}'s note explains nothing")
                self.assertTrue(m.name.strip())
                self.assertTrue(m.expect.strip())


class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        """The one the marking rests on.

        What a person typed against what the engine does. A puzzle whose
        expected output is wrong marks correct arrangements as wrong,
        and the person has no way of telling which of the two of you is
        at fault.
        """
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    _run(m.code, m.language), m.expect.strip(),
                    f"{m.id}: the engine disagrees with the expected output")

    def test_a_puzzle_prints_something(self) -> None:
        """A program with no output would be marked passed by any
        arrangement at all, including one that does not run."""
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertTrue(m.expect.strip())

    def test_the_order_matters_at_all(self) -> None:
        """The point of the mode: there has to be something to work out.

        Stated carefully, because the first version of this test was
        wrong. It demanded that one particular jumble print something
        else, and `magnet-async-await` failed it — with good reason.
        Marking runs the program, so arrangements that are equally
        correct are equally right, and some jumbles genuinely are.

        What the mode needs is weaker, and is the real claim: at least
        one arrangement of these lines prints something other than the
        answer. A puzzle whose lines work in any order has no puzzle in
        it.

        The async one was caught by this rather than by argument. Its
        call and the line below it printed the same thing either way
        round, so it could not demonstrate the note it carried. It has
        a synchronous log inside the function now, and it can.
        """
        for m in magnets():
            with self.subTest(magnet=m.id):
                differs = any(
                    _run("\n".join(m.shuffled(seed=s)), m.language)
                    != m.expect.strip()
                    for s in range(8)
                )
                self.assertTrue(
                    differs,
                    f"{m.id} prints its answer whatever order it is in")


class ShuffleTests(unittest.TestCase):
    def test_the_pieces_all_come_back(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertEqual(
                    sorted(m.shuffled(seed=1)), sorted(m.pieces))

    def test_it_never_hands_back_the_answer(self) -> None:
        for m in magnets():
            for seed in range(12):
                with self.subTest(magnet=m.id, seed=seed):
                    self.assertNotEqual(m.shuffled(seed=seed), m.pieces)

    def test_a_fresh_jumble_each_go(self) -> None:
        """The same jumble every time turns the second go into
        remembering where the pieces were rather than working out where
        they belong, which is the opposite of the exercise."""
        biggest = max(magnets(), key=lambda m: len(m.pieces))
        seen = {biggest.shuffled() for _ in range(12)}
        self.assertGreater(len(seen), 1)


class PiecesTests(unittest.TestCase):
    """The arrangement has to be made of the pieces handed out."""

    def test_the_right_pieces_are_recognised(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertTrue(same_pieces(m, list(m.shuffled(seed=3))))

    def test_a_missing_piece_is_noticed(self) -> None:
        m = magnets()[0]
        self.assertFalse(same_pieces(m, list(m.pieces)[:-1]))

    def test_an_extra_piece_is_noticed(self) -> None:
        m = magnets()[0]
        self.assertFalse(same_pieces(m, [*m.pieces, "console.log('extra');"]))

    def test_a_repeated_piece_is_counted(self) -> None:
        """Sorted rather than set-compared: a puzzle with two identical
        closing braces has to come back with two."""
        m = magnets()[0]
        doubled = [*m.pieces, m.pieces[0]]
        self.assertFalse(same_pieces(m, doubled))


class MarkingTests(unittest.TestCase):
    """Marking by output rather than by order — which is the design, and
    which every test above this one would pass without."""

    def _check(self, magnet_id: str, lines: list[str]):
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        return server.magnet_check(
            MagnetCheckRequest(magnet_id=magnet_id, lines=lines))

    def test_the_intended_order_passes(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertTrue(self._check(m.id, list(m.pieces)).passed)

    def test_some_arrangement_is_refused(self) -> None:
        """The marker has to be capable of saying no.

        Same care as test_the_order_matters_at_all: a particular jumble
        may be genuinely correct, so what is asserted is that some
        arrangement of the pieces is not.
        """
        for m in magnets():
            with self.subTest(magnet=m.id):
                refused = any(
                    not self._check(m.id, list(m.shuffled(seed=s))).passed
                    for s in range(6)
                )
                self.assertTrue(refused, f"{m.id} accepts every order")

    def test_a_different_correct_order_also_passes(self) -> None:
        """The reason marking runs the program.

        A function declaration is hoisted, so it can sit below the code
        that calls it and the program is identical. An arrangement like
        that is correct, and a marker comparing line orders would call
        it wrong and teach you to guess at the author's preference.
        """
        m = magnet("magnet-rest-spread")
        assert m is not None
        pieces = list(m.pieces)
        # Move `const cart = ...` above the function it is used after.
        cart = next(p for p in pieces if p.startswith("const cart"))
        pieces.remove(cart)
        moved = [cart, *pieces]
        self.assertNotEqual(moved, list(m.pieces))
        self.assertEqual(_run("\n".join(moved), m.language), m.expect)
        self.assertTrue(self._check(m.id, moved).passed)

    def test_pieces_that_are_not_the_puzzles_are_refused(self) -> None:
        m = magnets()[0]
        got = self._check(m.id, ["console.log('hello');"])
        self.assertFalse(got.passed)
        self.assertIn("magnets", got.broke)

    def test_an_unknown_puzzle_is_a_404(self) -> None:
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as caught:
            self._check("no-such-magnet", ["x"])
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()


class SubgoalTests(unittest.TestCase):
    """The labels the board is divided into.

    Subgoal labels are the one thing in this project with direct
    research behind them: given them, students do better on a Parsons
    problem immediately, a week later, and on a task they have not
    seen, than students who invent their own or get none. Which is why
    they are given — and why they have to actually describe the
    program rather than being three words that sound structural.

    The structural half is checked here. The describing half cannot be,
    and is why `test_a_label_is_a_description_not_a_line` exists: a
    label that is a paraphrase of one line of code is a label that has
    stopped scaffolding and started answering.
    """

    def test_every_puzzle_has_stages(self) -> None:
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertGreaterEqual(
                    len(m.plan), 2,
                    f"{m.id} has no stages to divide the board into")

    def test_the_stages_cover_every_line_exactly_once(self) -> None:
        """The program is the stages read in order, so a line in no
        stage could never be placed and a line in two would be typed
        twice."""
        for m in magnets():
            with self.subTest(magnet=m.id):
                counted = sum(count for _, count in m.plan)
                self.assertEqual(
                    counted, len(m.pieces),
                    f"{m.id}: stages cover {counted} lines of "
                    f"{len(m.pieces)}")
                placed = [line for _, lines in m.stages for line in lines]
                self.assertEqual(placed, list(m.pieces))

    def test_no_stage_is_empty(self) -> None:
        for m in magnets():
            for label, count in m.plan:
                with self.subTest(magnet=m.id, label=label):
                    self.assertGreater(count, 0)

    def test_the_labels_are_distinct_within_a_puzzle(self) -> None:
        """Two stages with the same name is two bins nobody can tell
        apart, and the board keys on the label."""
        for m in magnets():
            with self.subTest(magnet=m.id):
                self.assertEqual(len(set(m.labels)), len(m.labels))

    def test_a_label_is_a_description_not_a_line(self) -> None:
        """Plain words. A label carrying code has stopped describing
        the stage and started giving away what goes in it."""
        for m in magnets():
            for label in m.labels:
                with self.subTest(magnet=m.id, label=label):
                    self.assertLessEqual(len(label), 48)
                    self.assertTrue(label[0].isupper(), "starts as a sentence")
                    for giveaway in ("(", ")", ";", "{", "=>", "const "):
                        self.assertNotIn(giveaway, label)

    def test_the_stages_are_in_program_order(self) -> None:
        """Reading the labels top to bottom has to describe the program
        top to bottom, because that is literally how it is rebuilt."""
        for m in magnets():
            with self.subTest(magnet=m.id):
                rebuilt = "\n".join(
                    line for _, lines in m.stages for line in lines)
                self.assertEqual(rebuilt, m.code)


class SubgoalRouteTests(unittest.TestCase):
    def test_the_labels_are_served(self) -> None:
        from code_coach.api import server

        served = server.magnet_list()
        for family in served["families"]:
            for row in family["magnets"]:
                with self.subTest(magnet=row["id"]):
                    self.assertGreaterEqual(len(row["labels"]), 2)

    def test_how_many_lines_each_stage_holds_is_not_served(self) -> None:
        """A count is half the answer. Knowing a stage takes three
        lines narrows the puzzle far more than the label does, so the
        counts stay on the server.
        """
        from code_coach.api import server
        from code_coach.magnets import magnet as find

        served = server.magnet_list()
        for family in served["families"]:
            for row in family["magnets"]:
                with self.subTest(magnet=row["id"]):
                    self.assertNotIn("plan", row)
                    self.assertNotIn("stages", row)
                    real = find(row["id"])
                    assert real is not None
                    self.assertEqual(row["labels"], list(real.labels))
                    for value in row["labels"]:
                        self.assertIsInstance(value, str)
