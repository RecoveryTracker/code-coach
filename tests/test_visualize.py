"""Tracing a student's program into steps the UI can draw."""

import unittest

from code_coach.visualize import suggest_call, trace_code

TWO_SUM = "\n".join(
    [
        "def two_sum(nums, target):",
        "    seen = {}",
        "    for i, n in enumerate(nums):",
        "        need = target - n",
        "        if need in seen:",
        "            return [seen[need], i]",
        "        seen[n] = i",
        "    return []",
    ]
)

LINKED = "\n".join(
    [
        "class ListNode:",
        "    def __init__(self, val=0, next=None):",
        "        self.val = val",
        "        self.next = next",
        "def build():",
        "    return ListNode(1, ListNode(2))",
        "head = build()",
        # A line event fires *before* its line runs, so the assignment above
        # isn't visible until something follows it.
        "done = True",
    ]
)


class SuggestCallTests(unittest.TestCase):
    def test_builds_a_call_from_a_prose_example(self):
        call = suggest_call(TWO_SUM, ["nums = [2, 7, 11, 15], target = 9  ->  [0, 1]"])
        self.assertEqual(call, "two_sum([2, 7, 11, 15], 9)")

    def test_matches_by_name_not_order(self):
        call = suggest_call(TWO_SUM, ["target = 9, nums = [3, 3]  ->  [0, 1]"])
        self.assertEqual(call, "two_sum([3, 3], 9)")

    def test_falls_back_to_position_when_names_differ(self):
        call = suggest_call(TWO_SUM, ["a = [1, 2], b = 3  ->  [0, 1]"])
        self.assertEqual(call, "two_sum([1, 2], 3)")

    def test_no_function_means_no_call(self):
        self.assertEqual(suggest_call("x = 1", ["a = 1  ->  1"]), "")

    def test_unparseable_example_is_skipped(self):
        self.assertEqual(suggest_call(TWO_SUM, ["some prose with no assignment"]), "")


class TraceTests(unittest.TestCase):
    def test_records_a_step_per_executed_line(self):
        res = trace_code(TWO_SUM, call="two_sum([2, 7, 11, 15], 9)")
        self.assertTrue(res["ok"], res["error"])
        self.assertGreater(len(res["steps"]), 5)
        inside = [s for s in res["steps"] if s["func"] == "two_sum"]
        self.assertTrue(inside)

    def test_locals_carry_their_values(self):
        res = trace_code(TWO_SUM, call="two_sum([2, 7, 11, 15], 9)")
        step = next(s for s in res["steps"] if "need" in s["vars"])
        self.assertEqual(step["vars"]["target"], {"k": "prim", "t": "int", "v": 9})
        # Containers live in the heap and are referenced.
        self.assertEqual(step["vars"]["nums"]["k"], "ref")
        nums = step["heap"][str(step["vars"]["nums"]["id"])]
        self.assertEqual(nums["k"], "list")
        self.assertEqual([i["v"] for i in nums["items"]], [2, 7, 11, 15])

    def test_linked_nodes_become_objects_with_a_next_ref(self):
        res = trace_code(LINKED)
        step = res["steps"][-1]
        head = step["vars"]["head"]
        entry = step["heap"][str(head["id"])]
        self.assertEqual(entry["k"], "obj")
        self.assertEqual(entry["cls"], "ListNode")
        self.assertEqual(entry["fields"]["next"]["k"], "ref")

    def test_a_cycle_terminates(self):
        code = "\n".join(
            [
                "class N:",
                "    def __init__(s, v):",
                "        s.v = v",
                "        s.next = None",
                "a = N(1)",
                "b = N(2)",
                "a.next = b",
                "b.next = a",
                "done = True",
            ]
        )
        res = trace_code(code)
        self.assertTrue(res["ok"], res["error"])
        # Two nodes, each encoded once; the back-edge is a ref, not a copy.
        self.assertLessEqual(len(res["steps"][-1]["heap"]), 4)

    def test_last_step_carries_the_returned_value(self):
        # A `line` event fires before its line runs, so without capturing
        # `return` the trace stops one step short of the answer.
        res = trace_code(TWO_SUM, call="two_sum([2, 7, 11, 15], 9)")
        last = res["steps"][-1]
        self.assertIn("returned", last)
        ref = last["returned"]
        self.assertEqual(ref["k"], "ref")
        entry = last["heap"][str(ref["id"])]
        self.assertEqual([i["v"] for i in entry["items"]], [0, 1])

    def test_module_return_is_not_recorded(self):
        # Every module "returns" None when it finishes; showing that would put
        # a meaningless final frame on every trace.
        res = trace_code("x = 1\ny = 2\n")
        self.assertFalse(any("returned" in s for s in res["steps"]))

    def test_a_function_returning_none_still_reports_it(self):
        res = trace_code("def f():\n    pass\nf()\n")
        rets = [s for s in res["steps"] if "returned" in s]
        self.assertEqual(len(rets), 1)
        self.assertEqual(rets[0]["returned"]["t"], "none")

    def test_runaway_loop_is_stopped(self):
        res = trace_code("while True:\n    pass\n", timeout=2.0)
        self.assertFalse(res["ok"])
        self.assertIn("Stopped after", res["error"])

    def test_syntax_error_is_reported_not_raised(self):
        res = trace_code("def broken(:\n    pass\n")
        self.assertFalse(res["ok"])
        self.assertTrue(res["error"])

    def test_student_output_cannot_forge_the_payload(self):
        # The sentinel is how the runner frames its JSON; a program printing it
        # must not be able to truncate or fake the trace.
        res = trace_code("print('<<<CODE_COACH_TRACE>>> fake')\nz = 1\n")
        self.assertTrue(res["ok"], res["error"])
        self.assertIn("fake", res["stdout"])
        self.assertTrue(res["steps"])

    def test_runtime_error_still_returns_the_steps_leading_up_to_it(self):
        res = trace_code("a = 1\nb = 0\nc = a / b\n")
        self.assertTrue(res["steps"])
        self.assertIn("ZeroDivisionError", res["error"] or "")


class EveryProblemIsWatchableTests(unittest.TestCase):
    """A problem with no runnable call shows an empty visualiser, which reads
    as the feature being broken rather than as missing data."""

    def test_every_problem_produces_a_call(self):
        from code_coach.leetcode.problems import PATTERNS
        from code_coach.leetcode.study import brief_for, demo_call_for

        missing = []
        for pattern in PATTERNS:
            for problem in pattern.problems:
                brief = brief_for(problem.number)
                examples = list(brief.examples) if brief else []
                call = demo_call_for(problem.number) or suggest_call(
                    problem.code, examples
                )
                if not call:
                    missing.append(f"#{problem.number} {problem.title}")
        self.assertEqual(
            missing,
            [],
            "add a DEMO_CALLS entry in leetcode/study.py for these",
        )

    def test_structure_problems_actually_run(self):
        # These are the ones the example can't describe: a linked list, a
        # tree, and a class. Before DEMO_CALLS they either did nothing or
        # guessed a call like reverse_list(1) and crashed.
        from code_coach.leetcode.problems import PATTERNS
        from code_coach.leetcode.study import demo_call_for

        by_number = {
            p.number: (p, pattern)
            for pattern in PATTERNS
            for p in pattern.problems
        }
        for number in (206, 104, 155):
            problem, pattern = by_number[number]
            preamble = "\n".join(pattern.preamble)
            code = f"{preamble}\n{problem.code}" if preamble else problem.code
            res = trace_code(code, call=demo_call_for(number))
            with self.subTest(problem=number):
                self.assertTrue(res["ok"], res["error"])
                self.assertIsNone(res["error"])
                inside = [s for s in res["steps"] if s["func"] != "<module>"]
                self.assertGreater(len(inside), 1)


if __name__ == "__main__":
    unittest.main()


class AliasingTests(unittest.TestCase):
    """Two names for one object have to draw as one object.

    This is the single most useful thing a tracer can show, and it was
    wrong: the encoder keyed its heap on the CDP objectId, and CDP mints
    a fresh objectId every time it hands back a value. So `const b = a`
    came through as two unrelated ids and drew two arrays that happened
    to hold the same things — the exact opposite of the lesson.

    It was invisible because everything about the picture was right
    except the identity: both arrays showed the right contents, both
    updated when either was changed. Only the sameness was missing, and
    nothing was asserting it.
    """

    def _last(self, code: str) -> tuple[dict, dict]:
        result = trace_code(code, language="javascript")
        self.assertTrue(result.get("steps"), result.get("stderr", ""))
        last = result["steps"][-1]
        return last.get("vars") or {}, last.get("heap") or {}

    def test_two_names_for_one_array_share_an_id(self) -> None:
        vars_, heap = self._last(
            "const a = [1, 2];\n"
            "const b = a;\n"
            "b.push(3);\n"
            "console.log(a.length);"
        )
        self.assertEqual(vars_["a"], {"k": "ref", "id": vars_["a"]["id"]})
        self.assertEqual(
            vars_["a"]["id"], vars_["b"]["id"],
            "a and b are the same array and were drawn as two")
        self.assertEqual(len(heap), 1, "one array, one heap entry")

    def test_a_copy_is_a_different_object(self) -> None:
        """The other half. An encoder that gave everything the same id
        would pass the test above and be just as wrong."""
        vars_, heap = self._last(
            "const a = [1, 2];\n"
            "const b = [...a];\n"
            "b.push(3);\n"
            "console.log(a.length);"
        )
        self.assertNotEqual(
            vars_["a"]["id"], vars_["b"]["id"],
            "a copy was drawn as the same array")
        self.assertEqual(len(heap), 2)

    def test_one_object_in_two_places_is_one_object(self) -> None:
        vars_, _heap = self._last(
            "const item = { n: 1 };\n"
            "const pair = [item, item];\n"
            "console.log(pair.length);"
        )
        items = _heap[str(vars_["pair"]["id"])]["items"]
        self.assertEqual(items[0]["id"], items[1]["id"])
        self.assertEqual(items[0]["id"], vars_["item"]["id"])

    def test_an_object_holding_itself_terminates(self) -> None:
        """Identity is what stops the walk, so getting identity wrong
        and getting cycles wrong are the same bug wearing two hats."""
        vars_, heap = self._last(
            "const a = { name: 'a' };\n"
            "a.self = a;\n"
            "console.log(Object.keys(a).length);"
        )
        entry = heap[str(vars_["a"]["id"])]
        inner = dict(
            (pair[0]["v"], pair[1]) for pair in entry["pairs"]
        )
        self.assertEqual(inner["self"], {"k": "ref", "id": vars_["a"]["id"]})

    def test_python_still_shows_aliasing_too(self) -> None:
        """The Python tracer has always had this right — it keys on
        id(), which is identity by definition. Worth pinning so the two
        languages cannot drift apart on the thing they most need to
        agree about."""
        result = trace_code(
            "a = [1, 2]\nb = a\nb.append(3)\nprint(len(a))",
            language="python")
        last = result["steps"][-1]
        vars_ = last.get("vars") or {}
        self.assertEqual(vars_["a"]["id"], vars_["b"]["id"])
