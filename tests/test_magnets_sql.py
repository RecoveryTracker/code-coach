"""The SQL code magnets: shape, and every order run through the real runner.

`expect` for each was worked out by hand (see the comment beside each wrong
order); the tests run the app's SQLite runner (`code_coach/sql_runner.py`)
and must agree. SQL is marked like every other language: the arranged lines
are run and what they print is compared with `expect`, exactly.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.magnets import magnet, magnet_families, same_pieces
from code_coach.magnets.content_sql import SQL_MAGNETS

C = "-1 row(s) affected."


def _run(code: str) -> str:
    out, err, code_out = run_code(code, language="sql")
    if code_out != 0:
        return f"(exit {code_out}) {err.strip()[-200:]}"
    return out.replace("\r\n", "\n").strip()


def _find(magnet_id: str):
    return next(m for m in SQL_MAGNETS if m.id == magnet_id)


def _order(m, idx) -> str:
    assert sorted(idx) == list(range(len(m.pieces))), "an order uses every line once"
    return "\n".join(m.pieces[i] for i in idx)


def _swap(n: int, a: int, b: int) -> list[int]:
    idx = list(range(n))
    idx[a], idx[b] = idx[b], idx[a]
    return idx


def _blocks(*parts: str) -> str:
    return "\n\n".join(parts)


class ShapeTests(unittest.TestCase):
    def test_ten_sql_magnets(self) -> None:
        self.assertEqual(len(SQL_MAGNETS), 10)
        ids = [m.id for m in SQL_MAGNETS]
        self.assertEqual(len(ids), len(set(ids)))
        for m in SQL_MAGNETS:
            self.assertTrue(m.id.startswith("magnet-sql-"))
            self.assertEqual((m.language, m.family), ("sql", "SQL"))
        levels = [m.level for m in SQL_MAGNETS]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3, 4, 5})

    def test_ids_are_new(self) -> None:
        others = [m.id for m in __import__("code_coach.magnets", fromlist=["magnets"]).magnets()
                  if m.family != "SQL"]
        self.assertFalse(set(others) & {m.id for m in SQL_MAGNETS})

    def test_stages_cover_every_line(self) -> None:
        for m in SQL_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual("\n".join(l for _, ls in m.stages for l in ls), m.code)
                self.assertGreater(len(m.note), 120)
                self.assertTrue(4 <= len(m.pieces) <= 12)
                self.assertTrue(all(p.strip() for p in m.pieces))

    def test_registered(self) -> None:
        self.assertIn("SQL", magnet_families())
        for m in SQL_MAGNETS:
            self.assertIs(magnet(m.id), m)
            self.assertTrue(same_pieces(m, list(m.shuffled(seed=1))))


class OutputTests(unittest.TestCase):
    def test_every_intended_order_prints_expect(self) -> None:
        for m in SQL_MAGNETS:
            with self.subTest(magnet=m.id):
                self.assertEqual(_run(m.code), m.expect)

    def test_wrong_orders_that_fail(self) -> None:
        cases = [
            # SELECT above the CREATE: no such table.
            ("magnet-sql-create-insert-select", [3, 0, 1, 2], "no such table: pets"),
            # INSERT above its CREATE.
            ("magnet-sql-create-insert-select", [1, 0, 2, 3], "no such table: pets"),
            # LIMIT before ORDER BY does not parse.
            ("magnet-sql-select-clause-order", [0, 1, 2, 3, 4, 6, 5], "syntax error"),
            # WHERE after ORDER BY does not parse.
            ("magnet-sql-select-clause-order", [0, 1, 2, 3, 5, 4, 6], "syntax error"),
            # HAVING above GROUP BY.
            ("magnet-sql-group-having", [0, 1, 2, 3, 5, 4, 6], "syntax error"),
            # ON above its JOIN.
            ("magnet-sql-join-on", [0, 1, 2, 3, 4, 5, 7, 6, 8], "a JOIN clause is required before ON"),
            # books filled before it exists.
            ("magnet-sql-join-on", [0, 2, 3, 1, 4, 5, 6, 7, 8], "no such table: books"),
            # the query that uses `totals` placed above its WITH.
            ("magnet-sql-cte-before-query", [0, 1, 3, 4, 5, 6, 2], "no such table: totals"),
            # reading the view before it is made.
            ("magnet-sql-view-reads-live", [0, 1, 4, 2, 3], "no such table: pricey"),
        ]
        for mid, idx, why in cases:
            with self.subTest(magnet=mid, idx=idx):
                got = _run(_order(_find(mid), idx))
                self.assertTrue(got.startswith("(exit 1)"), got)
                self.assertIn(why, got)

    def test_wrong_orders_that_run_but_print_something_else(self) -> None:
        cases = [
            # inserts swapped: bird listed before cat.
            ("magnet-sql-create-insert-select", [0, 2, 1, 3],
             _blocks(C, "1 row(s) affected.", "1 row(s) affected.",
                     "name  legs\n----  ----\nbird  2\ncat   4")),
            # SELECT above the UPDATE: still 5, then the UPDATE reports.
            ("magnet-sql-update-then-select", [0, 1, 3, 2],
             _blocks(C, "1 row(s) affected.",
                     "item   qty\n-----  ---\napple  5", "1 row(s) affected.")),
            # DELETE above the first count: it already sees 2 rows.
            ("magnet-sql-delete-between-counts", [0, 1, 3, 2, 4],
             _blocks(C, "4 row(s) affected.", "2 row(s) affected.",
                     "at_start\n--------\n2", "at_end\n------\n2")),
            # counts swapped: at_end first reads 4, then the delete, then at_start reads 2.
            ("magnet-sql-delete-between-counts", [0, 1, 4, 3, 2],
             _blocks(C, "4 row(s) affected.", "at_end\n------\n4",
                     "2 row(s) affected.", "at_start\n--------\n2")),
            # final insert still inside the transaction: rolled back with the draft.
            ("magnet-sql-rollback", [0, 1, 2, 4, 3, 5],
             _blocks(C, C, "1 row(s) affected.", "1 row(s) affected.", C, "(no rows)")),
            # draft inserted after the ROLLBACK: it stays.
            ("magnet-sql-rollback", [0, 1, 3, 2, 4, 5],
             _blocks(C, C, C, "1 row(s) affected.", "1 row(s) affected.",
                     "txt\n-----\ndraft\nfinal")),
            # copy before the source is filled: copies 0 rows.
            ("magnet-sql-insert-select-copy", [0, 1, 3, 4, 5, 2, 6],
             _blocks(C, C, "0 row(s) affected.", "3 row(s) affected.", "(no rows)")),
            # SELECT above the second INSERT: no rug yet.
            ("magnet-sql-view-reads-live", [0, 1, 2, 4, 3],
             _blocks(C, "3 row(s) affected.", C,
                     "item  cents\n----  -----\npad   450\nink   900",
                     "2 row(s) affected.")),
        ]
        for mid, idx, want in cases:
            with self.subTest(magnet=mid, idx=idx):
                got = _run(_order(_find(mid), idx))
                self.assertEqual(got, want)
                self.assertNotEqual(got, _find(mid).expect)

    def test_free_orders_still_print_expect(self) -> None:
        join = _find("magnet-sql-join-on")
        table = join.expect.split("\n\n")[-1]
        view = _find("magnet-sql-view-reads-live")
        copy = _find("magnet-sql-insert-select-copy")
        cases = [
            # the two CREATEs swapped: same output exactly.
            (join, _swap(9, 0, 1), join.expect),
            # the two INSERTs swapped: same table, the row counts report in the other order.
            (join, _swap(9, 2, 3), _blocks(C, C, "3 row(s) affected.", "2 row(s) affected.", table)),
            (copy, _swap(7, 0, 1), copy.expect),
            # the second INSERT before the view: SQLite reads the view live.
            (view, [0, 1, 3, 2, 4],
             _blocks(C, "3 row(s) affected.", "2 row(s) affected.", C, view.expect.split("\n\n")[-1])),
        ]
        for m, idx, want in cases:
            with self.subTest(magnet=m.id, idx=idx):
                self.assertEqual(_run(_order(m, idx)), want)


class MarkingTests(unittest.TestCase):
    def test_the_real_route_marks_the_intended_order_right(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        served = {f["name"]: f for f in server.magnet_list()["families"]}
        self.assertIn("SQL", served)
        self.assertEqual({r["language"] for r in served["SQL"]["magnets"]}, {"sql"})
        for m in SQL_MAGNETS:
            with self.subTest(magnet=m.id):
                got = server.magnet_check(MagnetCheckRequest(magnet_id=m.id, lines=list(m.pieces)))
                self.assertTrue(got.passed, got.broke or got.printed)

    def test_the_real_route_marks_a_wrong_order_wrong(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import MagnetCheckRequest

        m = _find("magnet-sql-update-then-select")
        lines = [m.pieces[i] for i in (0, 1, 3, 2)]
        got = server.magnet_check(MagnetCheckRequest(magnet_id=m.id, lines=lines))
        self.assertFalse(got.passed)
        self.assertIn("apple  5", got.printed)
        m = _find("magnet-sql-group-having")
        lines = [m.pieces[i] for i in (0, 1, 2, 3, 5, 4, 6)]
        got = server.magnet_check(MagnetCheckRequest(magnet_id=m.id, lines=lines))
        self.assertFalse(got.passed)
        self.assertIn("syntax error", got.broke)


if __name__ == "__main__":
    unittest.main()
