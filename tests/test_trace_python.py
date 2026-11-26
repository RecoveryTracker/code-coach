"""The Python trace moments, and the tracer's Python notation.

`test_trace.py` already holds every moment in `traces()` to the tracer; these
add the Python set's own shape and pin `render_python`, which writes the
tracer's values the way Python's repr does (True, None, 'text', (1,), set()),
because a Python learner reading `true` or `null` would be reading the wrong
language. The Trace screen shows only the language picked at the top.
"""

from __future__ import annotations

import unittest

from code_coach.trace import one_trace, render, render_python, traces, value_at
from code_coach.trace.content_python import PY_TRACES


class ShapeTests(unittest.TestCase):
    def test_they_are_one_registered_python_family(self) -> None:
        self.assertGreaterEqual(len(PY_TRACES), 12)
        for t in PY_TRACES:
            with self.subTest(trace=t.id):
                self.assertEqual((t.family, t.language), ("Python", "python"))
                self.assertTrue(t.id.startswith("trace-py-"))
                self.assertIs(one_trace(t.id), t)
                self.assertLessEqual(len(t.numbered), 10)
                self.assertGreater(len(t.why), 150)
                self.assertGreaterEqual(len(t.choices), 4)
        self.assertEqual(len({t.id for t in traces()}), len(traces()))

    def test_the_ranking_was_done(self) -> None:
        levels = [t.level for t in PY_TRACES]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 2)


class TracerTests(unittest.TestCase):
    def test_the_tracer_says_exactly_this(self) -> None:
        for t in PY_TRACES:
            with self.subTest(trace=t.id):
                self.assertEqual(value_at(t.code, t.at_line, t.occurrence, t.variable, "python"), t.expect)

    def test_every_answer_is_written_as_python_writes_it(self) -> None:
        """Run the program up to the moment and print repr(variable): the same text."""
        from code_coach.engine import run_code

        for t in PY_TRACES:
            with self.subTest(trace=t.id):
                lines = t.code.split("\n")
                upto = lines[: t.at_line - 1]
                if t.occurrence > 1 or any(l.startswith((" ", "\t")) for l in lines[t.at_line - 1: t.at_line]):
                    continue  # inside a loop: the tracer test above covers it
                program = "\n".join(upto + [f"print(repr({t.variable}))"])
                out, err, code = run_code(program, language="python")
                self.assertEqual(code, 0, err)
                self.assertEqual(out.strip(), t.expect)


class RenderTests(unittest.TestCase):
    def prim(self, t, v):
        return {"k": "prim", "t": t, "v": v}

    def test_primitives(self) -> None:
        self.assertEqual(render_python(self.prim("bool", True), {}), "True")
        self.assertEqual(render_python(self.prim("none", None), {}), "None")
        self.assertEqual(render_python(self.prim("str", "it's"), {}), '"it\'s"')
        self.assertEqual(render_python(self.prim("float", 2.0), {}), "2.0")
        self.assertEqual(render_python(self.prim("int", 7), {}), "7")

    def test_containers(self) -> None:
        heap = {
            "1": {"k": "list", "tuple": True, "items": [self.prim("int", 1)]},
            "2": {"k": "set", "items": []},
            "3": {"k": "dict", "pairs": [[self.prim("str", "a"), {"k": "ref", "id": 1}]]},
            "4": {"k": "list", "tuple": False, "items": [self.prim("str", "x"), self.prim("none", None)]},
        }
        ref = lambda i: {"k": "ref", "id": i}  # noqa: E731
        self.assertEqual(render_python(ref(1), heap), "(1,)")
        self.assertEqual(render_python(ref(2), heap), "set()")
        self.assertEqual(render_python(ref(3), heap), "{'a': (1,)}")
        self.assertEqual(render_python(ref(4), heap), "['x', None]")

    def test_render_picks_the_notation_by_language(self) -> None:
        self.assertEqual(render(self.prim("bool", False), {}, "python"), "False")
        self.assertEqual(render(self.prim("bool", False), {}), "false", "JavaScript is unchanged")


class RouteTests(unittest.TestCase):
    def test_served_as_python_and_marked(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import TraceCheckRequest

        family = next(f for f in server.trace_list()["families"] if f["name"] == "Python")
        self.assertEqual({r["id"] for r in family["traces"]}, {t.id for t in PY_TRACES})
        for row in family["traces"]:
            self.assertEqual(row["language"], "python")
            self.assertNotIn("expect", row)
        t = PY_TRACES[0]
        self.assertTrue(server.trace_check(TraceCheckRequest(trace_id=t.id, answer=t.expect)).passed)
        self.assertFalse(server.trace_check(TraceCheckRequest(trace_id=t.id, answer=t.decoys[0])).passed)


if __name__ == "__main__":
    unittest.main()
