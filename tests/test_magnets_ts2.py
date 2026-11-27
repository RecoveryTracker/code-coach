"""The second TypeScript code magnet set: shape, and every order run for real.

`expect` for each was worked out by hand (see the comments beside each wrong
order); the tests run the real `tsc --strict` and node and must agree.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code, typescript_available
from code_coach.magnets import magnet, same_pieces
from code_coach.magnets.content_ts import TS_MAGNETS
from code_coach.magnets.content_ts2 import TS_MAGNETS_2

NEEDS = "needs tsc and node"


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="typescript")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-200:]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str):
    return next(m for m in TS_MAGNETS_2 if m.id == magnet_id)


def _order(m, idx) -> str:
    assert sorted(idx) == list(range(len(m.pieces))), "an order uses every line once"
    return "\n".join(m.pieces[i] for i in idx)


def _swap(n: int, a: int, b: int) -> list[int]:
    idx = list(range(n))
    idx[a], idx[b] = idx[b], idx[a]
    return idx


def _move(n: int, frm: int, to: int) -> list[int]:
    idx = list(range(n))
    idx.remove(frm)
    idx.insert(to, frm)
    return idx


class ShapeTests(unittest.TestCase):
    def test_ten_new_typescript_magnets(self) -> None:
        self.assertEqual(len(TS_MAGNETS_2), 10)
        ids = [m.id for m in TS_MAGNETS_2]
        self.assertEqual(len(ids), len(set(ids)))
        old = {m.id for m in TS_MAGNETS}
        for m in TS_MAGNETS_2:
            self.assertTrue(m.id.startswith("magnet-ts2-"))
            self.assertNotIn(m.id, old)
            self.assertEqual((m.language, m.family), ("typescript", "TypeScript"))
            if typescript_available():
                self.assertIs(magnet(m.id), m)
        levels = [m.level for m in TS_MAGNETS_2]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3, 4, 5})

    def test_names_differ_from_the_first_set(self) -> None:
        self.assertFalse({m.name for m in TS_MAGNETS_2} & {m.name for m in TS_MAGNETS})

    def test_stages_cover_every_line(self) -> None:
        for m in TS_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertEqual("\n".join(l for _, ls in m.stages for l in ls), m.code)
                self.assertGreater(len(m.note), 120)
                self.assertTrue(4 <= len(m.pieces) <= 12)


@unittest.skipUnless(typescript_available(), NEEDS)
class OutputTests(unittest.TestCase):
    def test_every_intended_order_prints_expect(self) -> None:
        for m in TS_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertEqual(_run(m.code), m.expect)

    def test_the_order_matters_at_all(self) -> None:
        for m in TS_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertTrue(any(_run("\n".join(m.shuffled(seed=s))) != m.expect
                                    for s in range(4)))

    # --- hand-worked wrong orders ---------------------------------------
    def test_wrong_orders_refused_by_the_compiler(self) -> None:
        cases = [
            # console.log above `const box`: TS2448, used before declaration.
            ("magnet-ts2-interface-area", _swap(9, 7, 8)),
            # `const nums` below the destructure that reads it: TS2448.
            ("magnet-ts2-tuple-destructure", _swap(6, 3, 4)),
            # the log above the enum it prints: TS2450.
            ("magnet-ts2-enum-switch", _move(10, 9, 0)),
            # `total += it` above the `if (isNum(it))`: `it` is still unknown.
            ("magnet-ts2-type-guard", _swap(11, 6, 7)),
            # the log above `const sum`: TS2448.
            ("magnet-ts2-reduce", _move(5, 4, 2)),
            # Dog before Animal, which it extends: TS2449.
            ("magnet-ts2-abstract-class", [5, 6, 7, 0, 1, 2, 3, 4, 8, 9]),
            # the stack made after the pushes that use it: TS2448.
            ("magnet-ts2-generic-stack", [0, 1, 2, 3, 4, 6, 7, 5, 8]),
        ]
        for mid, idx in cases:
            with self.subTest(magnet=mid):
                got = _run(_order(_find(mid), idx))
                self.assertTrue(got.startswith("(exit"), got)

    def test_wrong_orders_that_run_but_print_something_else(self) -> None:
        cases = [
            # returns swapped under their cases: Green -> stop, Red -> go.
            ("magnet-ts2-enum-switch", _swap(10, 4, 6), "stop go 1"),
            # the bare tick after the log: tick gives 5, count is 5.
            ("magnet-ts2-param-property", _swap(11, 9, 10), "5 5"),
            # print loop before the count loop: the Map is still empty.
            ("magnet-ts2-map-tally", [0, 1, 5, 6, 7, 2, 3, 4], ""),
            # Bo listed first.
            ("magnet-ts2-optional-chaining", _swap(11, 5, 6), "Bo unknown\nAda Rome"),
            # push b then a: pops a, b, then undefined.
            ("magnet-ts2-generic-stack", _swap(9, 6, 7), "a b undefined"),
        ]
        for mid, idx, want in cases:
            with self.subTest(magnet=mid):
                self.assertEqual(_run(_order(_find(mid), idx)), want)

    def test_independent_lines_can_swap_and_still_print_expect(self) -> None:
        for mid, idx in (("magnet-ts2-map-tally", _swap(8, 0, 1)),
                         ("magnet-ts2-reduce", _swap(5, 2, 3)),
                         ("magnet-ts2-type-guard", _swap(11, 3, 4))):
            with self.subTest(magnet=mid):
                m = _find(mid)
                self.assertEqual(_run(_order(m, idx)), m.expect)


class RegisteredTests(unittest.TestCase):
    @unittest.skipUnless(typescript_available(), NEEDS)
    def test_served_with_the_first_set(self) -> None:
        from code_coach.api import server

        fam = next(f for f in server.magnet_list()["families"] if f["name"] == "TypeScript")
        served = {r["id"] for r in fam["magnets"]}
        self.assertTrue({m.id for m in TS_MAGNETS + TS_MAGNETS_2} <= served)
        self.assertTrue(same_pieces(TS_MAGNETS_2[0], list(TS_MAGNETS_2[0].pieces)))


if __name__ == "__main__":
    unittest.main()
