"""The C++ code magnets: shape, and every order run for real.

`expect` for each was worked out by hand (see the comment beside each wrong
order); the tests build with the real C++ compiler and must agree.
"""

from __future__ import annotations

import unittest

from code_coach.engine import cpp_available, run_code
from code_coach.magnets import magnet, same_pieces
from code_coach.magnets.content_cpp import CPP_MAGNETS

needs_cpp = unittest.skipUnless(cpp_available(), "no C++ compiler installed")


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="cpp")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-200:]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str):
    return next(m for m in CPP_MAGNETS if m.id == magnet_id)


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
    def test_ten_cpp_magnets(self) -> None:
        self.assertEqual(len(CPP_MAGNETS), 10)
        ids = [m.id for m in CPP_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))
        for m in CPP_MAGNETS:
            self.assertTrue(m.id.startswith("magnet-cpp-"))
            self.assertEqual((m.language, m.family), ("cpp", "C++"))
        levels = [m.level for m in CPP_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3, 4, 5})

    def test_stages_cover_every_line(self) -> None:
        for m in CPP_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual("\n".join(l for _, ls in m.stages for l in ls), m.code)
                self.assertGreater(len(m.note), 120)
                self.assertTrue(4 <= len(m.pieces) <= 12)
                self.assertTrue(any(p.startswith("#include") for p in m.pieces))
                self.assertNotIn("time", m.code)

    @needs_cpp
    def test_registered_when_a_compiler_exists(self) -> None:
        for m in CPP_MAGNETS:
            self.assertIs(magnet(m.id), m)
            self.assertTrue(same_pieces(m, list(m.shuffled(seed=1))))


@needs_cpp
class OutputTests(unittest.TestCase):
    def test_every_intended_order_prints_expect(self) -> None:
        for m in CPP_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(_run(m.code), m.expect)

    def test_wrong_orders_the_compiler_refuses(self) -> None:
        cases = [
            # `v` used before it is declared.
            ("magnet-cpp-vector-push", _swap(10, 3, 4)),
            # `full` built before `last` exists.
            ("magnet-cpp-string-concat", _move(9, 5, 3)),
            # main above `square`: not declared yet.
            ("magnet-cpp-function-before-main", [0, 4, 5, 6, 7, 1, 2, 3]),
            # `public:` after the constructor: it is private, main cannot call it.
            ("magnet-cpp-class-constructor", [0, 1, 3, 4, 2, 5, 6, 7, 8, 9, 10]),
            # bump(x) above `int x`.
            ("magnet-cpp-reference-param", _swap(11, 5, 6)),
            # <vector> moved to the bottom: std::vector unknown.
            ("magnet-cpp-sort-lambda", [0, 1, 3, 4, 5, 6, 7, 8, 9, 2]),
            # the struct sits below main.
            ("magnet-cpp-unique-ptr", [0, 1, 6, 7, 8, 9, 2, 3, 4, 5]),
            # the string overload below main: show(std::string) has no match.
            ("magnet-cpp-overload", [0, 1, 2, 4, 5, 6, 7, 8, 3]),
        ]
        for mid, idx in cases:
            with self.subTest(magnet=mid):
                got = _run(_order(_find(mid), idx))
                self.assertTrue(got.startswith("(exit"), got)

    def test_wrong_orders_that_run_but_print_something_else(self) -> None:
        cases = [
            # pushes swapped: 5 before 3.
            ("magnet-cpp-vector-push", _swap(10, 4, 5), "5\n3"),
            # the loop runs before any push: nothing to print.
            ("magnet-cpp-vector-push", [0, 1, 2, 3, 6, 7, 8, 4, 5, 9], ""),
            # size printed before the name.
            ("magnet-cpp-string-concat", _swap(9, 6, 7), "12\nAda Lovelace"),
            # both bumps happen before the first print.
            ("magnet-cpp-reference-param", _swap(11, 7, 8), "25\n25"),
            # loop before the second pear count: pear is still 1.
            ("magnet-cpp-map-count", [0, 1, 2, 3, 4, 5, 6, 8, 7, 9], "apple 1\npear 1"),
            # printed before sorting: the original order.
            ("magnet-cpp-sort-lambda", [0, 1, 2, 3, 4, 6, 7, 8, 5, 9], "3\n9\n1\n7"),
            # loop before the 80 grade is added.
            ("magnet-cpp-structured-bindings", [0, 1, 2, 3, 4, 5, 7, 8, 9, 6, 10], "70C\n90A"),
            # "walk" before the object is made.
            ("magnet-cpp-unique-ptr", _swap(10, 7, 8), "walk\nborn\ngone"),
            # calls swapped.
            ("magnet-cpp-overload", _swap(9, 5, 6), "string seven\nint 7\nint 8"),
        ]
        for mid, idx, want in cases:
            with self.subTest(magnet=mid, want=want):
                self.assertEqual(_run(_order(_find(mid), idx)), want)

    def test_free_orders_still_print_expect(self) -> None:
        cases = [
            ("magnet-cpp-vector-push", _swap(10, 0, 1)),               # includes
            ("magnet-cpp-string-concat", _swap(9, 3, 4)),              # first / last
            ("magnet-cpp-class-constructor", _swap(11, 4, 5)),         # members in either order
            ("magnet-cpp-class-constructor", _move(11, 2, 3)),         # private fields, still fine
            ("magnet-cpp-map-count", _swap(10, 5, 6)),                 # the map sorts anyway
            ("magnet-cpp-structured-bindings", [0, 1, 2, 3, 6, 4, 5, 7, 8, 9, 10]),
            ("magnet-cpp-unique-ptr", _swap(10, 3, 4)),                # ctor / dtor
            ("magnet-cpp-overload", _swap(9, 2, 3)),                   # the two overloads
        ]
        for mid, idx in cases:
            with self.subTest(magnet=mid):
                m = _find(mid)
                self.assertEqual(_run(_order(m, idx)), m.expect)


if __name__ == "__main__":
    unittest.main()
