"""The second Rust code magnet set: shape, and every order run for real.

`expect` for each was worked out by hand (see the comments beside each wrong
order); the tests build with rustc (the engine's -O build) and must agree.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.magnets import magnet, same_pieces
from code_coach.magnets.content_rust import RUST_MAGNETS
from code_coach.magnets.content_rust2 import RUST_MAGNETS_2


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="rust")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-200:]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str):
    return next(m for m in RUST_MAGNETS_2 if m.id == magnet_id)


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
    def test_ten_new_rust_magnets(self) -> None:
        self.assertEqual(len(RUST_MAGNETS_2), 10)
        ids = [m.id for m in RUST_MAGNETS_2]
        self.assertEqual(len(ids), len(set(ids)))
        old = {m.id for m in RUST_MAGNETS}
        for m in RUST_MAGNETS_2:
            self.assertTrue(m.id.startswith("magnet-rust2-"))
            self.assertNotIn(m.id, old)
            self.assertEqual((m.language, m.family), ("rust", "Rust"))
            self.assertIs(magnet(m.id), m)
        levels = [m.level for m in RUST_MAGNETS_2]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3, 4, 5})

    def test_names_differ_from_the_first_set(self) -> None:
        self.assertFalse({m.name for m in RUST_MAGNETS_2} & {m.name for m in RUST_MAGNETS})

    def test_stages_cover_every_line(self) -> None:
        for m in RUST_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertEqual("\n".join(l for _, ls in m.stages for l in ls), m.code)
                self.assertGreater(len(m.note), 120)
                self.assertTrue(4 <= len(m.pieces) <= 12)

    def test_no_hashmap_is_ever_used(self) -> None:
        for m in RUST_MAGNETS_2:
            self.assertNotIn("HashMap", m.code)
            self.assertNotIn("HashSet", m.code)


class OutputTests(unittest.TestCase):
    def test_every_intended_order_prints_expect(self) -> None:
        for m in RUST_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertEqual(_run(m.code), m.expect)

    def test_the_order_matters_at_all(self) -> None:
        for m in RUST_MAGNETS_2:
            with self.subTest(magnet=m.id):
                self.assertTrue(any(_run("\n".join(m.shuffled(seed=s))) != m.expect
                                    for s in range(4)))

    # --- hand-worked wrong orders ---------------------------------------
    def test_wrong_orders_rustc_refuses(self) -> None:
        cases = [
            # `let add` above `let base`: E0425, cannot find `base`.
            ("magnet-rust2-closure-capture", _swap(7, 1, 2)),
            # bare `self.count` before `+= 1`: the body ends in a statement, E0308.
            ("magnet-rust2-struct-new", _swap(12, 4, 5)),
            # println above `let b`: E0425.
            ("magnet-rust2-enum-data", _move(12, 10, 8)),
            # println above `let d`: E0425.
            ("magnet-rust2-trait-default", _swap(12, 9, 10)),
            # `Ok(x + y)` above the lets that make x and y: E0425.
            ("magnet-rust2-result-question", _move(12, 3, 1)),
            # `first` is printed before the let that makes it: E0425.
            ("magnet-rust2-closure-counter", _move(10, 8, 6)),
        ]
        for mid, idx in cases:
            with self.subTest(magnet=mid):
                got = _run(_order(_find(mid), idx))
                self.assertTrue(got.startswith("(exit"), got)

    def test_wrong_orders_that_run_but_print_something_else(self) -> None:
        cases = [
            # print before the call that adds: the list is still [1].
            ("magnet-rust2-mut-vec", _swap(9, 6, 7), "[1]"),
            # pushes swapped: 4 lands before 2.
            ("magnet-rust2-mut-vec", _swap(9, 1, 2), "[1, 4, 2]"),
            # print before the loop pops anything: empty.
            ("magnet-rust2-while-let-pop", [0, 1, 2, 6, 3, 4, 5, 7], "[]"),
            # the plain Option print above the if let.
            ("magnet-rust2-option-if-let", [0, 1, 2, 3, 4, 8, 5, 6, 7, 9],
             "None\nlong word bear at 2"),
            # the match (error line) before the first println.
            ("magnet-rust2-result-question", [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 6, 11],
             "error: invalid digit found in string\nOk(9)"),
            # the print loop before the count loop: the map is still empty.
            ("magnet-rust2-btreemap-count", [0, 1, 2, 3, 7, 8, 9, 4, 5, 6, 10], ""),
            # `let second` first: it gets 1, `first` gets 2.
            ("magnet-rust2-closure-counter", _swap(10, 6, 7), "2 1"),
        ]
        for mid, idx, want in cases:
            with self.subTest(magnet=mid, want=want):
                self.assertEqual(_run(_order(_find(mid), idx)), want)

    def test_free_orders_still_print_expect(self) -> None:
        cases = [
            ("magnet-rust2-enum-data", _swap(12, 3, 4)),          # match arms in either order
            ("magnet-rust2-trait-default", _move(12, 4, 0)),      # items sit in any order
            ("magnet-rust2-btreemap-count", _move(11, 0, 10)),    # `use` at the bottom
            ("magnet-rust2-result-question", _swap(12, 1, 2)),    # x and y are independent
            ("magnet-rust2-while-let-pop", _swap(8, 1, 2)),
        ]
        for mid, idx in cases:
            with self.subTest(magnet=mid):
                m = _find(mid)
                self.assertEqual(_run(_order(m, idx)), m.expect)


class RegisteredTests(unittest.TestCase):
    def test_served_with_the_first_set(self) -> None:
        from code_coach.api import server

        fam = next(f for f in server.magnet_list()["families"] if f["name"] == "Rust")
        served = {r["id"] for r in fam["magnets"]}
        self.assertTrue({m.id for m in RUST_MAGNETS + RUST_MAGNETS_2} <= served)
        self.assertTrue(same_pieces(RUST_MAGNETS_2[0], list(RUST_MAGNETS_2[0].pieces)))


if __name__ == "__main__":
    unittest.main()
