"""/api/explain and /api/visualize told which language a snippet is in.

The server used to read every snippet as the app's saved language. A screen
that shows code in a language of its own - a Brain Drills question - has to be
able to say so, or a Python drill gets read as JavaScript when the app is set
to JavaScript (and the other way round). Blank still means the saved language.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.api import server
from code_coach.api.schemas import ExplainRequest, VisualizeRequest
from code_coach.brain import make_round, round_payload

PY = "for i in range(3):\n    print(i)\n"
JS = "for (let i = 0; i < 3; i++) {\n  console.log(i);\n}\n"
HAS_NODE = shutil.which("node") is not None


def saved(language: str) -> None:
    progress = server._store.load()
    progress.language = language
    server._store.save(progress)


def explain(code: str, language: str = ""):
    return server.explain(ExplainRequest(code=code, language=language))


def read_as_python(r) -> bool:
    """Python's explainer names the loop and what print() printed on each pass."""
    return any("loop" in L.text.lower() for L in r.lines) and "0" in " ".join(r.output_notes)


@unittest.skipUnless(HAS_NODE, "needs node")
class ExplainLanguage(unittest.TestCase):
    def test_python_code_is_read_as_python_when_the_app_is_set_to_javascript(self):
        saved("javascript")
        blank = explain(PY)
        asked = explain(PY, "python")
        self.assertFalse(read_as_python(blank), "blank means the saved language, here JavaScript")
        self.assertTrue(read_as_python(asked))
        self.assertIsNone(asked.error_note)

    def test_javascript_code_is_read_as_javascript_when_the_app_is_set_to_python(self):
        saved("python")
        blank = explain(JS)
        asked = explain(JS, "javascript")
        self.assertIsNotNone(blank.error_note, "read as Python, the JavaScript is a syntax error")
        self.assertIn("SyntaxError", blank.error_note)
        self.assertIsNone(asked.error_note)
        self.assertTrue(asked.lines)
        self.assertTrue(any("console.log" in L.source for L in asked.lines))

    def test_a_named_javascript_program_with_no_function_is_run_to_say_what_it_printed(self):
        saved("python")
        asked = explain("let n = 2 + 3;\nconsole.log(n);\n", "javascript")
        self.assertIn("5", " ".join(asked.output_notes))

    def test_blank_is_the_saved_language_as_before(self):
        saved("python")
        self.assertTrue(read_as_python(explain(PY)))
        self.assertTrue(read_as_python(explain(PY, "")))
        self.assertTrue(read_as_python(explain(PY, "   ")))
        saved("javascript")
        self.assertEqual(explain(JS).lines[0].source, explain(JS, "javascript").lines[0].source)
        self.assertIsNone(explain(JS).error_note)

    def test_an_unknown_language_falls_back_to_the_saved_one_not_to_python(self):
        saved("javascript")
        r = explain(JS, "klingon")
        self.assertIsNone(r.error_note)
        self.assertEqual([L.source for L in r.lines], [L.source for L in explain(JS).lines])
        saved("python")
        self.assertTrue(read_as_python(explain(PY, "klingon")))

    def test_the_request_defaults_to_blank(self):
        self.assertEqual(ExplainRequest(code="x").language, "")

    def test_a_language_without_an_explainer_still_says_so(self):
        saved("python")
        r = explain("SELECT 1;", "sql")
        self.assertFalse(r.ok)
        self.assertIn("no reader", r.summary)


@unittest.skipUnless(HAS_NODE, "needs node")
class VisualizeJavaScriptErrors(unittest.TestCase):
    """A JavaScript run that throws used to be an Internal Server Error: the
    tracer reports {type, message, line} and the response wanted text."""

    def test_a_thrown_error_is_text(self):
        saved("python")
        r = server.visualize(VisualizeRequest(code="console.log(1);\nnull.x;\n", language="javascript"))
        self.assertIsInstance(r.error, str)
        self.assertIn("TypeError", r.error)
        self.assertIn("line 2", r.error)
        self.assertEqual(r.stdout.strip(), "1")

    def test_a_syntax_error_is_text_and_says_syntax_error(self):
        r = server.visualize(VisualizeRequest(code="const x = [1,;\n", language="javascript"))
        self.assertIsInstance(r.error, str)
        self.assertTrue(r.error.startswith("SyntaxError"))

    def test_a_clean_run_has_no_error(self):
        r = server.visualize(VisualizeRequest(code='console.log(5 == "5");', language="javascript"))
        self.assertTrue(r.ok)
        self.assertIsNone(r.error)
        self.assertEqual(r.stdout.strip(), "true")

    def test_python_errors_are_as_they_were(self):
        r = server.visualize(VisualizeRequest(code="print(1)\nx.foo\n", language="python"))
        self.assertIn("NameError", r.error)
        self.assertEqual(r.stdout.strip(), "1")


class RoundPayload(unittest.TestCase):
    def test_every_item_carries_its_check_code(self):
        for language in ("javascript", "python"):
            payload = round_payload("loops", 3, language)
            real = make_round("loops", 3, language)
            self.assertEqual([i["check"] for i in payload["items"]], [i.check for i in real])
            self.assertTrue(all(i["check"] for i in payload["items"]))


if __name__ == "__main__":
    unittest.main()
