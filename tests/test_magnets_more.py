"""The second Python and C sets, and the TypeScript and Rust code magnets.

Held to the rules tests/test_magnets.py keeps for every set: each puzzle
prints exactly what it claims in the real language, the order matters (some
shuffle of it does not print the answer), the stage labels cover every line
once and in order without giving a line away, and the route serves each
family under its own language so the language picker can find it.
"""

from __future__ import annotations

import unittest

from code_coach.engine import c_available, run_code, typescript_available
from code_coach.magnets import magnet, magnets, same_pieces
from code_coach.magnets.content_c2 import C_MAGNETS_2
from code_coach.magnets.content_python2 import PY_MAGNETS_2
from code_coach.magnets.content_rust import RUST_MAGNETS
from code_coach.magnets.content_rust2 import RUST_MAGNETS_2
from code_coach.magnets.content_ts import TS_MAGNETS
from code_coach.magnets.content_ts2 import TS_MAGNETS_2

SETS = (("python", "Python", PY_MAGNETS_2), ("typescript", "TypeScript", TS_MAGNETS), ("rust", "Rust", RUST_MAGNETS),
        ("typescript", "TypeScript", TS_MAGNETS_2), ("rust", "Rust", RUST_MAGNETS_2),
        ("c", "C", C_MAGNETS_2))
GIVEAWAYS = ("(", ")", ":", "=", "[", "]", "{", "}", "#", "@", "\"", "'", "*", "+", "<", ">", ";", "&", "?")


def _run(code: str, language: str) -> str:
    out, err, code_out = run_code(code, language=language)
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-200:]}"
    return out.replace("\r\n", "\n").strip()


def _usable(language: str) -> bool:
    if language == "c":
        return c_available()
    return language != "typescript" or typescript_available()


class ShapeTests(unittest.TestCase):
    def test_each_set_is_registered_in_one_language(self) -> None:
        for language, family, items in SETS:
            for m in items:
                with self.subTest(magnet=m.id):
                    self.assertEqual((m.language, m.family), (language, family))
                    self.assertIs(magnet(m.id), m)
        ids = [m.id for m in magnets()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_each_is_a_real_puzzle_with_a_note(self) -> None:
        for _, _, items in SETS:
            levels = [m.level for m in items]
            self.assertEqual(levels, sorted(levels))
            self.assertGreater(len(set(levels)), 2)
            for m in items:
                with self.subTest(magnet=m.id):
                    self.assertGreaterEqual(len(m.pieces), 4)
                    self.assertLessEqual(len(m.pieces), 12)
                    self.assertTrue(all(p.strip() for p in m.pieces), "no blank magnets")
                    self.assertGreater(len(m.note), 120)

    def test_the_stages_cover_every_line_and_give_none_away(self) -> None:
        for _, _, items in SETS:
            for m in items:
                with self.subTest(magnet=m.id):
                    self.assertGreaterEqual(len(m.plan), 2)
                    self.assertTrue(all(n > 0 for _, n in m.plan))
                    self.assertEqual("\n".join(line for _, lines in m.stages for line in lines), m.code)
                    self.assertEqual(len(set(m.labels)), len(m.labels))
                    for label in m.labels:
                        self.assertLessEqual(len(label), 48)
                        self.assertTrue(label[0].isupper())
                        for g in GIVEAWAYS:
                            self.assertNotIn(g, label, label)

    def test_the_shuffle_keeps_every_piece_and_never_solves_it(self) -> None:
        for _, _, items in SETS:
            for m in items:
                for seed in range(6):
                    got = m.shuffled(seed=seed)
                    self.assertNotEqual(got, m.pieces, m.id)
                    self.assertTrue(same_pieces(m, list(got)), m.id)


class OutputTests(unittest.TestCase):
    def test_every_puzzle_prints_what_it_claims(self) -> None:
        for language, _, items in SETS:
            if not _usable(language):
                continue
            for m in items:
                with self.subTest(magnet=m.id):
                    self.assertEqual(_run(m.code, language), m.expect)

    def test_the_order_matters(self) -> None:
        for language, _, items in SETS:
            if not _usable(language):
                continue
            for m in items:
                with self.subTest(magnet=m.id):
                    self.assertTrue(any(_run("\n".join(m.shuffled(seed=s)), language) != m.expect
                                        for s in range(4)))


class RouteTests(unittest.TestCase):
    def test_served_as_their_language_and_marked(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        served = {f["name"]: f for f in server.magnet_list()["families"]}
        for language, family, items in SETS:
            if not _usable(language):
                continue
            with self.subTest(family=family):
                rows = {r["id"]: r for r in served[family]["magnets"]}
                for m in items:
                    self.assertEqual(rows[m.id]["language"], language)
                    self.assertNotIn("plan", rows[m.id])
                m = items[0]
                got = server.magnet_check(MagnetCheckRequest(magnet_id=m.id, lines=list(m.pieces)))
                self.assertTrue(got.passed, got.broke or got.printed)


if __name__ == "__main__":
    unittest.main()
