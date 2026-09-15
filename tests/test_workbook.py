"""The workbook: pages of exercises you solve by typing.

The claim this file has to hold up is narrow and load-bearing: every exercise
is solvable, and the output it demands is the output a correct program
actually produces. That cannot be asserted by reading the data — the expected
output is worked out in Python and the student's answer is run by a compiler,
so the only honest check is to run the reference program and compare.

The compiled languages are checked one exercise per shape rather than all 108,
because within a shape only the numbers differ and each extra one is another
compile. The shape is what could be wrong; the numbers are checked in full by
the languages that run in milliseconds.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from code_coach.engine import run_code
from code_coach.workbook import (
    exercise_count,
    expected_output,
    has_workbook,
    matches,
    normalise,
    page,
    pages,
)
from code_coach.workbook.emit import LANGUAGES, all_shape_ids

ALL = [(p, e) for p in pages() for e in p.exercises]

# Fast enough to run every exercise: no compiler in the loop.
INTERPRETED = ("python", "javascript")
# Everything else gets one exercise per shape it actually has.
OTHERS = tuple(lang for lang in LANGUAGES if lang not in INTERPRETED)


def _one_per_shape(language: str | None = None):
    """One exercise for each shape, out of the pages this language has.

    Pages 12 onwards exist in three languages only, so asking C for one of
    those would be asking for a reference that was never meant to exist.
    """
    seen: dict[str, tuple] = {}
    for p in pages(language):
        for e in p.exercises:
            seen.setdefault(e.shape, (p, e))
    return list(seen.values())


class ShapeTests(unittest.TestCase):
    def test_there_is_a_workbook_worth_working_through(self) -> None:
        self.assertGreaterEqual(len(pages()), 9)
        self.assertGreaterEqual(exercise_count(), 100)

    def test_a_page_is_a_dozen_goes_at_one_thing(self) -> None:
        """Three exercises is a demonstration. The repetition is the method.

        Review pages are the deliberate exception and the only one. They
        mix shapes because that is what a review is: the same material met
        again among other material, which is what makes it stick rather
        than merely feel smooth. Every other page is still one thing.
        """
        for p in pages():
            with self.subTest(page=p.id):
                self.assertGreaterEqual(len(p.exercises), 10)
                shapes = {e.shape for e in p.exercises}
                if p.tier == "review":
                    self.assertGreater(
                        len(shapes), 1,
                        f"{p.id} is a review page that revisits one shape, "
                        f"which is a normal page with a misleading name")
                    continue
                self.assertEqual(len(shapes), 1, f"{p.id} mixes {shapes}")

    def test_each_language_is_numbered_in_order_and_once_each(self) -> None:
        """Numbers are unique within one language's book, not across all of
        them.

        They used to be globally unique, which meant a second language could
        only be given numbers continuing on from Python's - so JavaScript's
        first intermediate page would have been 289 in a book that otherwise
        ended at 80. Renumbering per language at serve time is the other
        obvious fix and is worse: the pages refer to each other by number
        ("page 6's loop stopped before its limit"), and C is already missing
        eight beginner pages, so its numbering would shift under those
        references. So a book is numbered as itself, and two languages may
        both have a page 81 because no reader ever sees both.
        """
        for language in LANGUAGES:
            numbers = [p.number for p in pages(language)]
            with self.subTest(language=language):
                self.assertEqual(numbers, sorted(numbers))
                self.assertEqual(len(numbers), len(set(numbers)))

    def test_every_page_says_what_it_adds(self) -> None:
        for p in pages():
            with self.subTest(page=p.id):
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_exercise_asks_for_something_specific(self) -> None:
        for p, e in ALL:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))

    # Shapes whose body can legitimately not run at all: a condition that
    # does not hold, or a filter nothing matches. Keyed on the shape rather
    # than the page, because the same shape gets drilled again on the
    # practice pages and the rule travels with it.
    MAY_PRINT_NOTHING = {"if_print", "for_if_print", "list_filter"}

    def test_an_exercise_prints_something_unless_that_is_the_point(self) -> None:
        """Printing nothing is a real answer where the body may never run.
        Anywhere else an empty expectation is a mistake in the data."""
        for p, e in ALL:
            if e.shape in self.MAY_PRINT_NOTHING:
                continue
            with self.subTest(exercise=e.id):
                self.assertTrue(e.expect.strip(), "prints nothing")

    def test_the_shapes_that_allow_it_really_use_it(self) -> None:
        """If none of them printed nothing, the exemption above would be
        quietly covering shapes that no longer need it."""
        for shape in self.MAY_PRINT_NOTHING:
            with self.subTest(shape=shape):
                self.assertTrue(
                    any(
                        e.expect == "" for _, e in ALL if e.shape == shape
                    ),
                    "nothing with this shape prints nothing any more",
                )

    def test_no_exercise_id_is_used_twice(self) -> None:
        ids = [e.id for _, e in ALL]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        """Repetition means the same shape, not the same numbers — twelve
        copies of one sum is not practice."""
        for p in pages():
            with self.subTest(page=p.id):
                asked = [(e.prompt, e.expect) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_shape_is_used(self) -> None:
        """A shape with no page behind it is code nobody runs."""
        used = {e.shape for _, e in ALL}
        self.assertEqual(used, set(all_shape_ids()))

    def test_a_prompt_never_gives_away_the_syntax(self) -> None:
        """The prompt is the same sentence in every language, so anything that
        only makes sense in one of them is a bug in the prompt."""
        for _, e in ALL:
            with self.subTest(exercise=e.id):
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)


class OutputTests(unittest.TestCase):
    def test_output_is_worked_out_not_guessed(self) -> None:
        self.assertEqual(expected_output("print_expr", {"expr": "3 + 4"}), "7")
        self.assertEqual(
            expected_output("for_range_print", {"lo": 1, "hi": 3, "expr": "i"}),
            "1\n2\n3",
        )
        self.assertEqual(
            expected_output("for_sum", {"lo": 1, "hi": 10, "expr": "i"}), "55"
        )

    def test_a_loop_that_stops_before_its_limit_is_not_the_same(self) -> None:
        """Page 6's whole point. If these two ever compared equal the page
        would be teaching nothing."""
        before = expected_output("for_print", {"count": 5, "expr": "i"})
        inclusive = expected_output(
            "for_range_print", {"lo": 1, "hi": 5, "expr": "i"}
        )
        self.assertNotEqual(before, inclusive)

    def test_trailing_whitespace_is_not_the_exercise(self) -> None:
        self.assertTrue(matches("7\n", "7"))
        self.assertTrue(matches("7", "7\n\n"))
        self.assertTrue(matches("1 \n2\n", "1\n2"))
        self.assertEqual(normalise("a\r\nb\r\n"), "a\nb")

    def test_the_wrong_answer_is_still_wrong(self) -> None:
        """The normalising must forgive whitespace and nothing else."""
        self.assertFalse(matches("8", "7"))
        self.assertFalse(matches("1\n2", "1\n2\n3"))
        self.assertFalse(matches("", "7"))

    def test_an_unknown_shape_is_an_error_not_an_empty_page(self) -> None:
        with self.assertRaises(KeyError):
            expected_output("nonsense", {})


class ReferenceRunTests(unittest.TestCase):
    """The check that matters: run the answer and see what it prints.

    Everything else in this file reads data. This executes it.
    """

    #: run_code's exit code for "killed at the time limit".
    TIMED_OUT = 124

    def _run(self, language: str, exercise) -> None:
        code = exercise.answer(language)
        self.assertIsNotNone(code, f"no reference for {language}")
        stdout, stderr, exit_code = run_code(code, language=language)
        if exit_code == self.TIMED_OUT:
            # Try once more before believing it. These programs finish in
            # well under a tenth of a second and the limit is three, but a
            # machine busy with something else can still starve one past
            # it — that produced sixty-two false failures in one run here,
            # on pages that are demonstrably fine. A real infinite loop
            # times out both times and still fails; contention does not.
            stdout, stderr, exit_code = run_code(code, language=language)
        self.assertEqual(exit_code, 0, (stderr or stdout)[:400])
        self.assertTrue(
            matches(stdout, exercise.expect),
            f"printed {stdout!r}, wanted {exercise.expect!r}",
        )

    def test_every_exercise_solves_in_python(self) -> None:
        """The pages Python is offered, which is no longer all of them:
        JavaScript's own intermediate pages have no Python answer to run."""
        for p in pages("python"):
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self._run("python", e)

    def test_every_exercise_solves_in_javascript(self) -> None:
        """The pages JavaScript is offered — the shared tiers, plus its own
        intermediate pages. Python's intermediate pages are not among
        them."""
        for p in pages("javascript"):
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self._run("javascript", e)

    def test_every_typescript_only_exercise_compiles(self) -> None:
        """TypeScript's own pages, every exercise rather than one per shape.

        The shape-level test below rests on "within a shape only the numbers
        change". For TypeScript that is not true: the rows carry type and
        function names, and a top-level name shares a namespace with the DOM
        globals. An interface named after a global merges with it instead of
        shadowing it, so the object is reported as missing members it never
        heard of.

        That is not hypothetical. A row naming an interface Report compiled
        fine as the first exercise of its shape and failed as the eighteenth,
        and it was found by hand because nothing here was looking. This costs
        a few minutes and would have caught it.
        """
        for p in pages("typescript"):
            if p.number <= 80:
                continue        # the shared tiers, covered per shape below
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self._run("typescript", e)

    def test_every_shape_compiles_and_runs_in_every_language(self) -> None:
        """One per shape rather than all of them: within a shape only the
        numbers change, and each of these is another compile."""
        for language in OTHERS:
            for p, e in _one_per_shape(language):
                with self.subTest(language=language, shape=e.shape):
                    self._run(language, e)

    def test_dart_runs_one_of_every_shape_it_has(self) -> None:
        """Dart's coverage is every shape on a page Dart is offered — which
        is all of them bar the Python-only tier."""
        from code_coach.workbook.emit_python import SHAPE_IDS as PY1
        from code_coach.workbook.emit_python2 import SHAPE_IDS as PY2
        from code_coach.workbook.emit_python3 import SHAPE_IDS as PY3
        from code_coach.workbook.emit_python4 import SHAPE_IDS as PY4
        from code_coach.workbook.emit_python5 import SHAPE_IDS as PY5
        from code_coach.workbook.emit_python6 import SHAPE_IDS as PY6
        from code_coach.workbook.emit_python7 import SHAPE_IDS as PY7
        from code_coach.workbook.emit_python8 import SHAPE_IDS as PY8
        from code_coach.workbook.emit_python9 import SHAPE_IDS as PY9
        from code_coach.workbook.emit_python10 import SHAPE_IDS as PY10
        from code_coach.workbook.emit_python11 import SHAPE_IDS as PY11
        from code_coach.workbook.emit_python12 import SHAPE_IDS as PY12
        from code_coach.workbook.emit_python13 import SHAPE_IDS as PY13
        from code_coach.workbook.emit_python14 import SHAPE_IDS as PY14
        from code_coach.workbook.emit_python15 import SHAPE_IDS as PY15
        from code_coach.workbook.emit_python16 import SHAPE_IDS as PY16
        from code_coach.workbook.emit_python17 import SHAPE_IDS as PY17
        from code_coach.workbook.emit_python18 import SHAPE_IDS as PY18
        from code_coach.workbook.emit_python19 import SHAPE_IDS as PY19
        from code_coach.workbook.emit_python20 import SHAPE_IDS as PY20
        from code_coach.workbook.emit_js import SHAPE_IDS as JS
        from code_coach.workbook.emit_js2 import SHAPE_IDS as JS2
        from code_coach.workbook.emit_js3 import SHAPE_IDS as JS3
        from code_coach.workbook.emit_js4 import SHAPE_IDS as JS4
        from code_coach.workbook.emit_js5 import SHAPE_IDS as JS5
        from code_coach.workbook.emit_js6 import SHAPE_IDS as JS6
        from code_coach.workbook.emit_js7 import SHAPE_IDS as JS7
        from code_coach.workbook.emit_js8 import SHAPE_IDS as JS8
        from code_coach.workbook.emit_ts import SHAPE_IDS as TS
        from code_coach.workbook.emit_ts2 import SHAPE_IDS as TS2
        from code_coach.workbook.emit_ts3 import SHAPE_IDS as TS3
        from code_coach.workbook.emit_ts4 import SHAPE_IDS as TS4
        from code_coach.workbook.emit_ts5 import SHAPE_IDS as TS5
        from code_coach.workbook.emit_ts6 import SHAPE_IDS as TS6
        from code_coach.workbook.emit_algo import SHAPE_IDS as ALGO
        from code_coach.workbook.emit_algo2 import SHAPE_IDS as ALGO2
        from code_coach.workbook.emit_algo3 import SHAPE_IDS as ALGO3
        from code_coach.workbook.emit_sql import SHAPE_IDS as SQL_SHAPES
        from code_coach.workbook.emit_algo4 import SHAPE_IDS as ALGO4
        from code_coach.workbook.emit_nodes import SHAPE_IDS as NODES
        from code_coach.workbook.emit_graph import SHAPE_IDS as GRAPHS
        from code_coach.workbook.emit_c import SHAPE_IDS as C_SHAPES
        from code_coach.workbook.emit_rust import SHAPE_IDS as RUST_SHAPES
        from code_coach.workbook.emit_ts7 import SHAPE_IDS as TS7_SHAPES
        from code_coach.workbook.emit_js9 import SHAPE_IDS as JS9_SHAPES
        from code_coach.workbook.emit_cpp2 import SHAPE_IDS as CPP2_SHAPES
        from code_coach.workbook.emit_sql2 import SHAPE_IDS as SQL2_SHAPES
        from code_coach.workbook.emit_sql3 import SHAPE_IDS as SQL3_SHAPES
        from code_coach.workbook.emit_pg import SHAPE_IDS as PG_SHAPES
        from code_coach.workbook.emit_webnodes import SHAPE_IDS as WEB_SHAPES
        from code_coach.workbook.emit_topup import SHAPE_IDS as TOPUP_SHAPES
        from code_coach.workbook.emit_rust3 import SHAPE_IDS as RUST3_SHAPES
        from code_coach.workbook.emit_python21 import SHAPE_IDS as PY21

        python_only = (
            set(PY1)
            | set(PY2)
            | set(PY3)
            | set(PY4)
            | set(PY5)
            | set(PY6)
            | set(PY7)
            | set(PY8)
            | set(PY9)
            | set(PY10)
            | set(PY11)
            | set(PY12)
            | set(PY13)
            | set(PY14)
            | set(PY15)
            | set(PY16)
            | set(PY17)
            | set(PY18)
            | set(PY19)
            | set(PY20)
            | set(PY21)
            | set(JS)
            | set(JS2)
            | set(JS3)
            | set(JS4)
            | set(JS5)
            | set(JS6)
            | set(JS7)
            | set(JS8)
            | set(TS)
            | set(TS2)
            | set(TS3)
            | set(TS4)
            | set(TS5)
            | set(TS6)
            | set(ALGO)
            | set(ALGO2)
            | set(ALGO3)
            | set(SQL_SHAPES)
            | set(ALGO4)
            | set(NODES)
            | set(GRAPHS)
            | set(C_SHAPES)
            | set(RUST_SHAPES)
            | set(TS7_SHAPES)
            | set(JS9_SHAPES)
            | set(CPP2_SHAPES)
            | set(SQL2_SHAPES)
            | set(SQL3_SHAPES)
            # PostgreSQL's, for the same reason as SQL's: a dialect page
            # is one language's and Dart was never going to answer it.
            | set(PG_SHAPES)
            | set(WEB_SHAPES)
            # dart_more is dart's, but the other three in this block
            # are not, and the roster is what dart does not have.
            | (set(TOPUP_SHAPES) - {"dart_more"})
            | set(RUST3_SHAPES)
        )
        shapes = {e.shape for _, e in _one_per_shape("dart")}
        self.assertEqual(shapes, set(all_shape_ids()) - python_only)


class ComplexityNoteTests(unittest.TestCase):
    """A complexity note is a claim about the code, so check it against it.

    The label cannot be derived from source in general — sorted() has no
    visible loop, recursion has none either, and an amortised while inside
    a for is still linear. But a flat contradiction is detectable: O(1) on
    a program that walks its data, or O(n) on one with nested data loops.

    This exists because a wrong note shipped. times_table was labelled O(n²)
    from the day the notes were written, grouped with the genuinely nested
    shapes, while emitting a single loop over one row. Nobody reading the
    list noticed; comparing the claim against the program did.
    """

    #: Shapes whose note explains why the shape of the code misleads —
    #: amortised passes, library calls that iterate internally, and
    #: structures whose cost is per operation rather than per collection.
    EXPLAINED = frozenset({
        "algo_window_grow", "algo_tree_bfs", "algo_monotonic",
        "algo_window_max", "algo_grid_flood", "algo_union_find",
        "algo_trie", "algo_dijkstra", "algo_two_heaps",
        # A for loop inside a while loop, linear all the same because
        # each node is in exactly one row. The note says so at length.
        "tree_levels",
        "combinations_use", "product_use", "generator_send",
        "js_generator", "js_iterator", "js_yield_star", "js_labelled_break",
        "sqlite_memory", "heapq_use", "heapq_real", "bisect_use",
        "deque_use", "js_map_set", "js_weakmap", "js_memo_map",
        "js_at", "js_sparse", "js_freeze", "js_seal", "js_proxy",
    })

    @staticmethod
    def _fixed_iterable(node) -> bool:
        """A literal tuple, list, or range of constants.

        A loop over `(3, -1)` or `range(5)` is a couple of demonstration
        calls, not a pass over data, and counting it as one would make
        every page look linear.
        """
        import ast as _ast

        if isinstance(node, (_ast.Tuple, _ast.List)):
            return True
        return (
            isinstance(node, _ast.Call)
            and isinstance(node.func, _ast.Name)
            and node.func.id == "range"
            and all(isinstance(a, _ast.Constant) for a in node.args)
        )

    @classmethod
    def _data_loop_depth(cls, node, d: int = 0) -> int:
        import ast as _ast

        best = d
        for child in _ast.iter_child_nodes(node):
            step = 0
            if isinstance(child, (_ast.For, _ast.AsyncFor)):
                step = 0 if cls._fixed_iterable(child.iter) else 1
            elif isinstance(child, _ast.While):
                step = 1
            elif isinstance(child, (_ast.ListComp, _ast.SetComp,
                                    _ast.DictComp, _ast.GeneratorExp)):
                step = sum(
                    0 if cls._fixed_iterable(g.iter) else 1
                    for g in child.generators
                )
            best = max(best, cls._data_loop_depth(child, d + step))
        return best

    def test_every_page_has_a_complexity_note(self) -> None:
        """The panel is either there for every page or it is a gap the
        student notices. A shape with nothing honest to say may be left
        out, but nothing is currently in that position."""
        from code_coach.workbook.complexity import for_shape

        for language in ("python", "javascript", "typescript"):
            for p in pages(language):
                with self.subTest(language=language, page=p.number):
                    self.assertIsNotNone(
                        for_shape(p.exercises[0].shape),
                        f"page {p.number} ({p.id}) has no complexity note",
                    )

    def test_no_note_contradicts_the_code_it_describes(self) -> None:
        import ast as _ast

        from code_coach.workbook.complexity import for_shape

        seen = set()
        # Every shape on the page against an exercise that actually uses
        # it, rather than the page's first exercise. Review pages mix
        # shapes, so reading exercises[0] there would check one exercise
        # in twenty and call the whole page covered.
        for p in pages("python"):
            for ex in p.exercises:
                shape = ex.shape
                if shape in seen or shape in self.EXPLAINED:
                    continue
                seen.add(shape)
                note = for_shape(shape)
                if note is None:
                    continue
                try:
                    tree = _ast.parse(ex.answer("python"))
                except SyntaxError:
                    continue
                depth = self._data_loop_depth(tree)
                with self.subTest(page=p.number, shape=shape):
                    if note.label == "O(1)":
                        self.assertEqual(
                            depth, 0,
                            f"{shape} is called constant but walks its data")
                    elif note.label == "O(n)":
                        self.assertLess(
                            depth, 2,
                            f"{shape} is called linear but nests data loops")
                    elif note.label.startswith("O(n²)"):
                        self.assertGreaterEqual(
                            depth, 2,
                            f"{shape} is called quadratic with no nested loop")


class EndpointTests(unittest.TestCase):
    def _request(self, **kwargs):
        from code_coach.api.schemas import WorkbookCheckRequest

        return WorkbookCheckRequest(**kwargs)

    def test_it_serves_the_pages_for_a_language(self) -> None:
        from code_coach.api import server

        served = server.workbook("python")
        self.assertTrue(served["has_workbook"])
        self.assertEqual(len(served["pages"]), len(pages("python")))
        first = served["pages"][0]["exercises"][0]
        self.assertTrue(first["prompt"])
        self.assertTrue(first["answer"])

    def test_sql_is_served_its_own_pages(self) -> None:
        """SQL was refused, because it has no print and no loop and so can
        write none of the shared shapes. It now has its own pages, where the
        answer is the rows a query returns."""
        from code_coach.api import server

        served = server.workbook("sql")
        self.assertTrue(served["has_workbook"])
        self.assertTrue(served["pages"])
        for served_page in served["pages"]:
            with self.subTest(page=served_page["id"]):
                self.assertTrue(served_page["id"].startswith("sql-"))

    def test_a_right_answer_passes_and_is_remembered(self) -> None:
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        real = server._store
        try:
            use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
            server._store = active_store()
            got = server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="print(3 + 4)",
                    language="python",
                )
            )
            self.assertTrue(got.passed)
            self.assertEqual(got.done_on_page, 1)
            # Asked of the page rather than written down: this said 12 until
            # the pages went to twenty, and a hard-coded count fails for a
            # change that is not a fault.
            self.assertEqual(got.page_total, len(page("arithmetic").exercises))
            # And it survives a reload — the store's from_dict is an explicit
            # allow-list, so a new field it does not name is silently dropped.
            stored = server._store.load()
            self.assertIn("arithmetic-01", stored.workbook_for("python"))
        finally:
            server._store = real

    def test_a_different_language_is_counted_separately(self) -> None:
        """Solving it in Python does not mean you can write it in Rust."""
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        real = server._store
        try:
            use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
            server._store = active_store()
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="print(3 + 4)",
                    language="python",
                )
            )
            stored = server._store.load()
            self.assertEqual(stored.workbook_for("javascript"), [])
        finally:
            server._store = real

    def test_the_right_answer_written_a_different_way_also_passes(self) -> None:
        """It checks what the program printed, not how it was written."""
        from code_coach.api import server

        for code in ("print(7)", "print(3 + 4)", "x = 3\ny = 4\nprint(x + y)"):
            with self.subTest(code=code):
                got = server.workbook_check(
                    self._request(
                        page_id="arithmetic",
                        exercise_id="arithmetic-01",
                        code=code,
                        language="python",
                    )
                )
                self.assertTrue(got.passed)

    def test_a_wrong_answer_says_what_it_printed(self) -> None:
        from code_coach.api import server

        got = server.workbook_check(
            self._request(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(8)",
                language="python",
            )
        )
        self.assertFalse(got.passed)
        self.assertFalse(got.failed_to_run)
        self.assertEqual(got.stdout.strip(), "8")
        self.assertEqual(got.expect, "7")

    def test_code_that_does_not_run_is_a_different_answer(self) -> None:
        """A syntax error and a wrong number are different problems, and
        reading "wrong" for a program that never started is misleading."""
        from code_coach.api import server

        got = server.workbook_check(
            self._request(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(3 + ",
                language="python",
            )
        )
        self.assertFalse(got.passed)
        self.assertTrue(got.failed_to_run)
        self.assertTrue(got.stderr.strip())

    def test_an_exercise_that_does_not_exist_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server

        with self.assertRaises(HTTPException) as caught:
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-99",
                    code="print(7)",
                    language="python",
                )
            )
        self.assertEqual(caught.exception.status_code, 404)

    def test_a_language_without_a_workbook_is_refused(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server

        with self.assertRaises(HTTPException) as caught:
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="SELECT 7;",
                    language="sql",
                )
            )
        self.assertEqual(caught.exception.status_code, 409)

    def test_lookups_handle_nothing(self) -> None:
        from code_coach.workbook import exercise as find

        self.assertIsNone(page("nonsense"))
        self.assertIsNone(find("nonsense", "x"))
        self.assertIsNone(find("arithmetic", "nope"))


class LanguageReachTests(unittest.TestCase):
    """How far the ramp goes in each language.

    All of it, in every language the workbook runs in. The later pages —
    lists, strings, functions — were three languages deep for a while, on the
    assumption that C would need the exercise faked to take part. It did not.
    SQL is still out, and for a real reason: no statement that prints a line
    and no loop.
    """

    DEEP = (
        "python",
        "javascript",
        "typescript",
        "dart",
        "c",
        "cpp",
        "rust",
    )

    # Where each language's ramp ends, and why. C stops at 48 because
    # splitting text and looking things up by key need types it has not got —
    # and the honest C answer to either is a week of memory management rather
    # than one exercise.
    EVERY_PAGE = (
        "python",
        "javascript",
        "typescript",
        "dart",
        "cpp",
        "rust",
    )

    def test_python_only_misses_pages_another_language_claimed(self) -> None:
        """Python is the language the book goes deep in, so the only pages
        it does not get are ones written for a single other language.

        This used to say Python gets every page there is, which held for as
        long as Python was the only language with a tier of its own.
        JavaScript now has one, so the claim is narrower — and still worth
        making, because a page going missing from Python by accident is
        exactly the mistake it was written to catch.
        """
        claimed = [p for p in pages() if not p.applies_to("python")]
        for p in claimed:
            with self.subTest(page=p.id):
                self.assertEqual(len(p.languages), 1, "claimed by one")
                self.assertNotIn("python", p.languages)
        self.assertEqual(len(pages("python")) + len(claimed), len(pages()))

    def test_the_shared_tiers_go_to_the_languages_that_can_run_them(
        self,
    ) -> None:
        """Beginner and practice are written for several languages; only the
        eight collection pages are ever dropped, and only by C.

        "Shared" means written for more than one language. SQL's pages are
        tiered beginner too — that is the right label in the sidebar, since
        they are its first ten — but they belong to SQL alone and are not
        part of what the other languages should be offered.
        """
        for language in self.EVERY_PAGE:
            shared = [
                p
                for p in pages()
                if p.tier in ("beginner", "practice")
                and len(p.languages) != 1
            ]
            offered = [p for p in pages(language) if p.tier in ("beginner", "practice")]
            with self.subTest(language=language):
                self.assertEqual(len(offered), len(shared))

    def test_an_intermediate_page_belongs_to_exactly_one_language(self) -> None:
        """It was Python only, because one language is what buys the depth.
        Python now has that depth, and so does every other language here.

        The rule that stays is one language per page. A shared intermediate
        page would have to print identical output in every language that got
        it, and escaping exactly that constraint is what the single-language
        tier is for.

        This used to name the three languages that had reached the tier and
        assert the page belonged to one of them. That list went stale the
        moment a fourth arrived, which is the same way the C page count went
        stale. What the rule actually says is that the page belongs to one
        language the workbook covers, so that is what is asserted, and it
        needs no editing when a sixth language gets there.
        """
        # Asked of the workbook rather than listed. This was
        # `set(self.DEEP) | {"sql"}`, and the literal on the end is the
        # third time this rule has gone stale in exactly the way its own
        # docstring warns about: PostgreSQL arrived with seven
        # intermediate pages and failed a test about which languages are
        # allowed to have them, for no reason except that nobody had
        # added a second literal. "A language the workbook covers" is
        # what the rule means, and has_workbook is what knows.
        from code_coach.languages import LANGUAGES
        from code_coach.workbook import has_workbook

        allowed = {lang.id for lang in LANGUAGES if has_workbook(lang.id)}
        for p in pages():
            if p.tier != "intermediate":
                continue
            with self.subTest(page=p.id):
                self.assertEqual(len(p.languages), 1, "one language a page")
                self.assertIn(p.languages[0], allowed)

    def test_c_misses_exactly_the_pages_it_cannot_answer(self) -> None:
        """Deliberate, not an accident — so a later page cannot quietly drop
        C without someone deciding to. Named rather than counted: C keeps
        gaining pages as practice ones land, and the list of what it cannot
        do should not move when that happens."""
        # Of the pages written for more than one language, these are the
        # ones C cannot answer. Single-language pages are a separate matter
        # and are not C being dropped from anything.
        shared = [p for p in pages() if len(p.languages) != 1]
        dropped = {p.id for p in shared if not p.applies_to("c")}
        self.assertEqual(
            dropped,
            {
                "split-words",
                "count-words",
                "join-list",
                "map-lookup",
                "map-build",
                "str-contains",
                "str-slice",
                "str-find",
            },
        )
        # Count the shared pages C receives, not every page it has.
        # The docstring above already says single-language pages are
        # a separate matter, and this line quietly assumed C had none
        # of its own until the C tier landed and it read 80 != 72.
        shared_for_c = [p for p in pages("c") if len(p.languages) != 1]
        self.assertEqual(len(shared_for_c), len(shared) - len(dropped))

    def test_the_languages_that_get_it_are_the_ones_that_can_run_it(self) -> None:
        """No page is offered to a language the engine cannot run.

        This used to compare the workbook's language list against DEEP,
        which worked while those were the same seven languages. They are
        not any more: eight more arrived with a single page each, so DEEP
        now means the languages with a whole book and LANGUAGES means the
        languages offered anything at all.

        The rule underneath was never about that list. It is that a
        language given a page can execute it, so the runner map is what to
        ask, and asking it needs no editing when a ninth arrives.
        """
        from code_coach.engine import _SUFFIXES

        for language in LANGUAGES:
            with self.subTest(language=language):
                self.assertIn(
                    language, _SUFFIXES,
                    f"{language} is offered pages the engine cannot run")

    def test_the_deep_languages_all_have_more_than_one_page(self) -> None:
        """DEEP is now a claim about depth rather than about existing, so
        it should be false the moment one of them stops being deep."""
        for language in self.DEEP:
            with self.subTest(language=language):
                self.assertGreater(len(pages(language)), 1)

    def test_sql_has_its_own_pages_and_shares_none(self) -> None:
        """SQL used to be left out, because it has no print and no loop and
        so cannot write any of the shared shapes. It now has ten pages of
        its own — queries checked against the rows they return — and it
        still shares nothing with the others, which is the part worth
        holding: every page it is offered is a SQL page."""
        self.assertTrue(has_workbook("sql"))
        self.assertNotIn("sql", self.DEEP)
        offered = pages("sql")
        self.assertTrue(offered)
        for p in offered:
            with self.subTest(page=p.id):
                self.assertEqual(p.languages, ("sql",))

    def test_a_language_is_never_offered_a_page_it_cannot_answer(self) -> None:
        """The real check: every page a language is shown must have a
        reference program in it, or the exercise cannot be marked right."""
        for language in LANGUAGES:
            for p in pages(language):
                for e in p.exercises:
                    with self.subTest(language=language, exercise=e.id):
                        self.assertIsNotNone(e.answer(language))

    def test_the_early_pages_are_open_to_everyone(self) -> None:
        """Page numbers are per-language, so this is about the shared pages
        rather than about the number: SQL numbers its own ten from 1, the
        way JavaScript numbers its own from 81."""
        for p in pages():
            if p.number > 11 or len(p.languages) == 1:
                continue
            with self.subTest(page=p.id):
                self.assertEqual(p.languages, ())

    def test_the_later_pages_name_who_they_are_for(self) -> None:
        """Past page 11 a page always says which languages it is for, and
        every name in it is a language the app offers.

        Against LANGUAGES rather than DEEP, which is the thing that went
        stale. A page naming a language means "anyone here who can answer
        me", and pages() already drops a language with no reference
        answer, so naming one that cannot answer costs nothing while
        naming too few hides the page from someone who could do it. What
        is still worth catching is a name that is not a language at all —
        a typo hides a page from everybody and nothing else complains.
        """
        allowed = set(LANGUAGES) | {"sql"}
        for p in pages():
            if p.number <= 11:
                continue
            with self.subTest(page=p.id):
                self.assertTrue(p.languages)
                self.assertTrue(
                    set(p.languages) <= allowed,
                    f"{p.id} names {sorted(set(p.languages) - allowed)}")

    def test_no_two_languages_are_told_to_print_different_things(self) -> None:
        """The rule the multi-language pages rest on. An exercise has one
        expected output, so if two languages would print different characters
        for it the exercise is unanswerable in one of them — and it fails
        quietly, for that language only.

        A page written for exactly one language is exempt, and that exemption
        is the whole point of the Python tier: there it may print a list as a
        list.
        """
        for p in pages():
            if len(p.languages) == 1:
                continue
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self.assertIsInstance(e.expect, str)
                    # Nothing may print a Python container or a Python bool:
                    # those are the two that render differently elsewhere.
                    self.assertNotIn("[", e.expect)
                    self.assertNotIn("True", e.expect)
                    self.assertNotIn("False", e.expect)

    def test_the_single_language_pages_really_use_the_exemption(self) -> None:
        """If none of them printed something the others could not, the
        exemption above would be covering nothing and the tier would not need
        to be single-language at all."""
        printed = " ".join(
            e.expect
            for p in pages()
            if len(p.languages) == 1
            for e in p.exercises
        )
        self.assertIn("[", printed)

    def test_the_payload_only_carries_pages_you_can_do(self) -> None:
        from code_coach.api import server

        for language in ("python", "c", "sql"):
            with self.subTest(language=language):
                served = server.workbook(language)
                self.assertEqual(len(served["pages"]), len(pages(language)))
                for entry in served["pages"]:
                    for item in entry["exercises"]:
                        self.assertTrue(item["answer"])


class MemoryTests(unittest.TestCase):
    """Where you were, and what you wrote.

    The workbook used to open at page one however far in you were, and threw
    away every answer the moment you moved on. Both are stored in the progress
    file, whose loader is an explicit allow-list — a field it does not name is
    silently dropped on the next read, which has already happened once here.
    So every one of these checks the value comes back after a reload rather
    than only that it was set.
    """

    def _fresh(self):
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
        server._store = active_store()
        return server

    def _check(self, server, page_id, exercise_id, code, language="python"):
        from code_coach.api.schemas import WorkbookCheckRequest

        return server.workbook_check(
            WorkbookCheckRequest(
                page_id=page_id,
                exercise_id=exercise_id,
                code=code,
                language=language,
            )
        )

    def setUp(self) -> None:
        from code_coach.api import server

        self._real = server._store
        self.server = self._fresh()

    def tearDown(self) -> None:
        from code_coach.api import server

        server._store = self._real

    def test_it_opens_where_you_were(self) -> None:
        self._check(
            self.server, "first-loop", "first-loop-01", "for i in range(5):\n    print(i)"
        )
        self.assertEqual(self.server.workbook("python")["at"], "first-loop")

    def test_a_wrong_answer_still_keeps_your_place(self) -> None:
        """Coming back to the page you were stuck on is the point."""
        got = self._check(self.server, "ranges", "ranges-01", "print(0)")
        self.assertFalse(got.passed)
        self.assertEqual(self.server.workbook("python")["at"], "ranges")

    def test_a_new_student_has_no_place_to_return_to(self) -> None:
        """Empty rather than a guess, so the screen can fall back to page one
        itself instead of being sent somewhere arbitrary."""
        self.assertEqual(self.server.workbook("python")["at"], "")

    def test_your_answer_is_kept(self) -> None:
        code = "for i in range(5):\n    print(i)"
        self._check(self.server, "first-loop", "first-loop-01", code)
        answers = self.server.workbook("python")["answers"]
        self.assertEqual(answers["first-loop-01"], code)

    def test_a_wrong_answer_is_kept_too(self) -> None:
        """This used to keep only correct answers, on the grounds that the
        file should be a record of your work rather than your typos.

        The effect was that going to another exercise and back threw away
        everything you had not yet got right — which is the work you most
        wanted back. Being wrong is not a reason to lose it.
        """
        self._check(self.server, "arithmetic", "arithmetic-01", "print(8)")
        answers = self.server.workbook("python")["answers"]
        self.assertEqual(answers["arithmetic-01"], "print(8)")
        # Kept, but still not passed.
        self.assertNotIn("arithmetic-01", self.server.workbook("python")["done"])

    def test_typing_is_kept_without_running_it(self) -> None:
        """Half-typed work survives leaving the exercise, which is the whole
        point: it is saved as you type rather than as you succeed."""
        from code_coach.api.schemas import WorkbookDraftRequest

        self.server.workbook_draft(
            WorkbookDraftRequest(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(3 +",
                language="python",
            )
        )
        got = self.server.workbook("python")
        self.assertEqual(got["answers"]["arithmetic-01"], "print(3 +")
        # Nothing was run, so nothing is done and nothing claims to be.
        self.assertEqual(got["done"], [])

    def test_a_draft_also_keeps_your_place(self) -> None:
        """Typing on a page is being on it."""
        from code_coach.api.schemas import WorkbookDraftRequest

        self.server.workbook_draft(
            WorkbookDraftRequest(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(",
                language="python",
            )
        )
        self.assertEqual(self.server.workbook("python")["at"], "arithmetic")

    def test_a_later_answer_replaces_an_earlier_one(self) -> None:
        self._check(self.server, "arithmetic", "arithmetic-01", "print(7)")
        self._check(self.server, "arithmetic", "arithmetic-01", "print(3 + 4)")
        answers = self.server.workbook("python")["answers"]
        self.assertEqual(answers["arithmetic-01"], "print(3 + 4)")

    def test_it_survives_a_reload(self) -> None:
        """The bit that the allow-list loader breaks if it is forgotten."""
        from code_coach.api import server

        code = "print(3 + 4)"
        self._check(self.server, "arithmetic", "arithmetic-01", code)
        reloaded = server._store.load()
        self.assertEqual(reloaded.workbook_page_for("python"), "arithmetic")
        self.assertEqual(
            reloaded.workbook_answers_for("python")["arithmetic-01"], code
        )

    def test_each_language_is_remembered_separately(self) -> None:
        self._check(self.server, "arithmetic", "arithmetic-01", "print(7)")
        self._check(
            self.server,
            "first-loop",
            "first-loop-01",
            "for (let i = 0; i < 5; i++) { console.log(i); }",
            language="javascript",
        )
        python = self.server.workbook("python")
        javascript = self.server.workbook("javascript")
        self.assertEqual(python["at"], "arithmetic")
        self.assertEqual(javascript["at"], "first-loop")
        self.assertNotIn("first-loop-01", python["answers"])
        self.assertNotIn("arithmetic-01", javascript["answers"])

    def test_an_enormous_answer_cannot_bloat_the_file(self) -> None:
        from code_coach.progress.store import MAX_ANSWER_CHARS

        progress = self.server._store.load()
        progress.remember_workbook_answer("python", "x-01", "a" * 99999)
        self.assertEqual(
            len(progress.workbook_answers_for("python")["x-01"]),
            MAX_ANSWER_CHARS,
        )


if __name__ == "__main__":
    unittest.main()


class RefusedPageTests(unittest.TestCase):
    """A page a language is declared for but not offered.

    `pages` drops a page when the language has no reference answer for
    it, which is what lets a language join the workbook before it can
    answer everything. That mechanism is silent by design, and silence is
    the risk: a page can stop being offered because someone genuinely
    decided it should not be, or because an emitter quietly stopped
    handling a shape, and nothing tells the two apart.

    So every refusal has to have a reason on record. There is one reason
    at the moment — a language that counts from one cannot answer a page
    about index zero, because its answer is a different number — and this
    says so rather than listing which pages those are. A list of the
    three would go stale the first time a fourth is added; asking why
    does not.
    """

    def test_every_refused_page_has_a_reason(self) -> None:
        from code_coach.workbook import emit_newlang4, emit_newlang5
        from code_coach.workbook.content import PAGES

        positional = set(emit_newlang4.POSITIONAL) | set(emit_newlang5.POSITIONAL)

        for language in LANGUAGES:
            offered = {p.id for p in pages(language)}
            for p in PAGES:
                if not p.applies_to(language) or p.id in offered:
                    continue
                with self.subTest(language=language, page=p.id):
                    self.assertIn(
                        language, emit_newlang4.ONE_BASED,
                        f"{language} is quietly not offered {p.id}")
                    self.assertTrue(
                        {e.shape for e in p.exercises} <= positional,
                        f"{p.id} is refused to {language} for no stated "
                        f"reason")

    def test_the_one_based_language_really_does_refuse_them(self) -> None:
        """The other half. If the refusal stopped happening — a reference
        appeared that prints a one where every other language prints a
        zero — the page would come back and quietly be wrong, and the
        rule above would still pass because it only looks at what is
        missing."""
        from code_coach.workbook import emit_newlang4, emit_newlang5

        for language in emit_newlang4.ONE_BASED:
            for shape in emit_newlang4.POSITIONAL:
                with self.subTest(language=language, shape=shape):
                    self.assertFalse(emit_newlang4.supports(language, shape))
            for shape in emit_newlang5.POSITIONAL:
                with self.subTest(language=language, shape=shape):
                    self.assertFalse(emit_newlang5.supports(language, shape))


class KotlinBatchTests(unittest.TestCase):
    """Every Kotlin exercise, compiled in batches rather than one by one.

    The other compiled languages are sampled: `test_every_shape_compiles_
    and_runs_in_every_language` takes one exercise per shape, because
    within a shape only the numbers change and each one is another
    compile. That is a reasonable trade at half a second a compile.

    Kotlin's compiler costs four and a half seconds a file, almost all of
    it starting a JVM, so the same trade would buy forty-seven exercises
    for four minutes. Compiling a folder in one call pays that startup
    once: all fourteen hundred cost less than five, which is thirty times
    the coverage for the same money.

    Each file gets a package of its own. Kotlin puts top-level functions
    in a shared namespace, so two exercises that both declare `fun
    greet()` are conflicting overloads when compiled side by side — an
    artefact of batching rather than anything wrong with the answers, and
    the package is what makes the batch a fair stand-in for compiling
    alone. Checked against compiling alone on a sample, which agreed.
    """

    CHUNK = 60

    @classmethod
    def setUpClass(cls) -> None:
        from code_coach.engine import _kotlin_parts

        parts = _kotlin_parts()
        if parts is None:
            raise unittest.SkipTest("no kotlin toolchain")
        cls.kotlinc, cls.stdlib, cls.java = parts

    def test_every_kotlin_exercise_runs(self) -> None:
        import os
        import shutil
        import subprocess
        import tempfile

        env = dict(os.environ)
        env.setdefault("JAVA_HOME", str(self.java.parent.parent))
        work = [e for p in pages("kotlin") for e in p.exercises]
        self.assertTrue(work, "kotlin is offered no pages")

        for start in range(0, len(work), self.CHUNK):
            batch = work[start:start + self.CHUNK]
            folder = Path(tempfile.mkdtemp())
            try:
                named = []
                for offset, exercise in enumerate(batch):
                    code = exercise.answer("kotlin")
                    self.assertIsNotNone(code, f"no reference for {exercise.id}")
                    tag = f"p{start + offset}"
                    name = f"Ex{start + offset}"
                    (folder / f"{name}.kt").write_text(
                        f"package {tag}\n\n{code}", encoding="utf-8")
                    named.append((f"{tag}.{name}Kt", exercise))

                out = folder / "out"
                built = subprocess.run(
                    [str(self.kotlinc), str(folder), "-d", str(out)],
                    capture_output=True, text=True, timeout=900, env=env)
                self.assertEqual(
                    built.returncode, 0,
                    (built.stderr or built.stdout)[:600])

                classpath = os.pathsep.join([str(out), str(self.stdlib)])
                for entry, exercise in named:
                    with self.subTest(exercise=exercise.id):
                        ran = subprocess.run(
                            [str(self.java), "-cp", classpath, entry],
                            capture_output=True, text=True, timeout=120,
                            stdin=subprocess.DEVNULL, env=env)
                        self.assertEqual(
                            ran.returncode, 0,
                            (ran.stderr or ran.stdout)[:400])
                        self.assertTrue(
                            matches(ran.stdout, exercise.expect),
                            f"printed {ran.stdout!r}, "
                            f"wanted {exercise.expect!r}")
            finally:
                shutil.rmtree(folder, ignore_errors=True)
