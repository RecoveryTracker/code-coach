"""Code tracing and Explain for JavaScript.

The tracer's job is to produce exactly the payload the Python one does, since
the same diagrams draw both. The explainer's job is narrower: describe what it
recognises and stay quiet about the rest — a confident wrong sentence about a
line is worse than no sentence.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.explain_js import explain_js
from code_coach.languages import get_language
from code_coach.visualize import suggest_call, trace_code

HAS_NODE = shutil.which("node") is not None

TWO_SUM = """function twoSum(nums, target) {
  const seen = new Map();
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (seen.has(need)) return [seen.get(need), i];
    seen.set(nums[i], i);
  }
  return [];
}
"""


class SuggestCallTests(unittest.TestCase):
    def test_finds_a_function_declaration(self) -> None:
        call = suggest_call(
            TWO_SUM, ["nums = [2,7,11,15], target = 9  ->  [0,1]"], "javascript"
        )
        self.assertEqual(call, "console.log(twoSum([2, 7, 11, 15], 9));")

    def test_finds_an_arrow_function(self) -> None:
        call = suggest_call(
            "const double = (n) => n * 2;\n", ["n = 4  ->  8"], "javascript"
        )
        self.assertEqual(call, "console.log(double(4));")

    def test_python_literals_become_javascript_ones(self) -> None:
        """repr() would emit True and None, which are a ReferenceError in JS."""
        call = suggest_call(
            "function f(flag, thing) {}\n",
            ["flag = True, thing = None  ->  1"],
            "javascript",
        )
        self.assertIn("true", call)
        self.assertIn("null", call)
        self.assertNotIn("True", call)
        self.assertNotIn("None", call)

    def test_no_function_means_no_guess(self) -> None:
        self.assertEqual(suggest_call("const x = 1;\n", [], "javascript"), "")

    def test_python_path_is_unchanged(self) -> None:
        call = suggest_call(
            "def add(a, b):\n    return a + b\n", ["a = 1, b = 2  ->  3"]
        )
        self.assertEqual(call, "add(1, 2)")


@unittest.skipUnless(HAS_NODE, "needs Node on PATH")
class TraceTests(unittest.TestCase):
    def test_traces_a_real_solution(self) -> None:
        result = trace_code(
            TWO_SUM,
            call="console.log(twoSum([2, 7, 11, 15], 9));",
            language="javascript",
        )
        self.assertTrue(result["ok"], result.get("error"))
        self.assertTrue(result["steps"])
        self.assertIn("0", result["stdout"])

    def test_steps_carry_the_variables_in_scope(self) -> None:
        """Block-scoped names are the ones worth watching, and the easiest to
        miss: `i` and `need` live in a block scope, not the function's."""
        result = trace_code(
            TWO_SUM,
            call="console.log(twoSum([2, 7, 11, 15], 9));",
            language="javascript",
        )
        names: set[str] = set()
        for step in result["steps"]:
            names.update(step["vars"])
        self.assertIn("seen", names)
        self.assertIn("i", names)
        self.assertIn("need", names)

    def test_node_module_wrapper_stays_out_of_the_picture(self) -> None:
        result = trace_code(TWO_SUM, call="twoSum([1, 2], 3);", language="javascript")
        for step in result["steps"]:
            for hidden in ("module", "require", "exports", "__dirname"):
                self.assertNotIn(hidden, step["vars"])

    def test_containers_encode_the_way_python_ones_do(self) -> None:
        result = trace_code(
            TWO_SUM,
            call="console.log(twoSum([2, 7, 11, 15], 9));",
            language="javascript",
        )
        kinds = {
            entry.get("k")
            for step in result["steps"]
            for entry in step["heap"].values()
        }
        self.assertIn("list", kinds)  # the array
        self.assertIn("dict", kinds)  # the Map

    def test_class_instances_become_objects_with_fields(self) -> None:
        """Linked-list and tree diagrams are drawn from these."""
        code = (
            "function ListNode(val, next) { this.val = val; this.next = next; }\n"
            "function build() {\n"
            "  const b = new ListNode(2, null);\n"
            "  return new ListNode(1, b);\n"
            "}\n"
        )
        result = trace_code(code, call="build();", language="javascript")
        objects = [
            entry
            for step in result["steps"]
            for entry in step["heap"].values()
            if entry.get("k") == "obj"
        ]
        self.assertTrue(objects)
        self.assertEqual(objects[0]["cls"], "ListNode")
        self.assertIn("val", objects[0]["fields"])

    def test_a_runaway_loop_returns_a_partial_picture(self) -> None:
        """Not a timeout: the steps already captured are worth showing."""
        result = trace_code(
            "function spin() {\n  let n = 0;\n  while (true) {\n    n++;\n  }\n}\n",
            call="spin();",
            language="javascript",
        )
        self.assertTrue(result["truncated"])
        self.assertTrue(result["steps"])

    def test_a_broken_program_reports_the_error(self) -> None:
        result = trace_code("function oops( {\n", call="", language="javascript")
        self.assertTrue(result.get("error"))

    def test_python_tracing_still_works(self) -> None:
        result = trace_code(
            "def add(a, b):\n    total = a + b\n    return total\n", call="add(2, 3)"
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["steps"])


class ExplainTests(unittest.TestCase):
    def test_describes_a_whole_solution(self) -> None:
        out = explain_js(TWO_SUM)
        self.assertTrue(out["ok"])
        self.assertIn("twoSum", out["summary"])
        by_line = {entry["line"]: entry["text"] for entry in out["lines"]}
        self.assertIn("taking nums, target", by_line[1])
        self.assertIn("lookup table", by_line[2])
        self.assertIn("counts i from 0", by_line[3])

    def test_a_condition_with_a_call_in_it_is_not_cut_in_half(self) -> None:
        """`if (seen.has(need))` used to read as the condition `seen.has(need`."""
        out = explain_js("if (seen.has(need)) return [seen.get(need), i];\n")
        text = out["lines"][0]["text"]
        self.assertIn("seen.has(need)", text)
        self.assertNotIn("seen.has(need,", text)

    def test_a_one_line_if_keeps_its_consequence(self) -> None:
        out = explain_js("if (a === b) return 1;\n")
        self.assertIn("hands back", out["lines"][0]["text"])

    def test_variable_names_keep_their_capitals(self) -> None:
        """`.capitalize()` lower-cased the rest and made lastSeen into lastseen."""
        out = explain_js("lastSeen.set(ch, right);\n")
        self.assertIn("lastSeen", out["lines"][0]["text"])

    def test_math_calls_read_as_english(self) -> None:
        out = explain_js("best = Math.max(best, n);\n")
        self.assertIn("larger", out["lines"][0]["text"])

    def test_unrecognised_lines_are_left_alone(self) -> None:
        """Silence beats a confident wrong description."""
        out = explain_js("@@@ this is not javascript\n")
        self.assertEqual(out["lines"], [])

    def test_comments_are_not_re_explained(self) -> None:
        out = explain_js("// count the letters\nlet n = 0;\n")
        self.assertEqual(len(out["lines"]), 1)

    def test_indentation_becomes_depth(self) -> None:
        out = explain_js("function f() {\n  let a = 1;\n    let b = 2;\n}\n")
        depths = [entry["depth"] for entry in out["lines"]]
        self.assertEqual(depths, [0, 1, 2])

    def test_empty_code_says_so(self) -> None:
        out = explain_js("   \n")
        self.assertFalse(out["ok"])

    def test_trace_output_is_reported(self) -> None:
        out = explain_js(
            "let n = 1;\n",
            {"stdout": "42", "steps": [{}, {}], "truncated": False, "error": None},
        )
        self.assertTrue(any("42" in note for note in out["output_notes"]))

    def test_a_run_that_did_nothing_is_not_reported(self) -> None:
        """One step means only the definition ran — saying so is noise."""
        out = explain_js(
            "let n = 1;\n",
            {"stdout": "", "steps": [{}], "truncated": False, "error": None},
        )
        self.assertEqual(out["output_notes"], [])

    def test_a_runtime_error_is_reported(self) -> None:
        out = explain_js(
            "let n = 1;\n",
            {"error": {"type": "TypeError", "message": "x is not a function",
                       "line": 3}},
        )
        self.assertIn("TypeError", out["error_note"])
        self.assertIn("line 3", out["error_note"])


class CapabilityTests(unittest.TestCase):
    def test_javascript_now_advertises_both_tools(self) -> None:
        ready = get_language("javascript").ready
        self.assertIn("tracer", ready)
        self.assertIn("explainer", ready)

    def test_languages_without_a_tracer_still_say_so(self) -> None:
        for lang_id in ("sql", "c", "rust"):
            self.assertNotIn("tracer", get_language(lang_id).ready, lang_id)


if __name__ == "__main__":
    unittest.main()
