"""The "Node" JavaScript pages (238-247).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsnode directly,
so nothing here depends on the dispatch in emit.py or the workbook package.
Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.

The expected outputs are worked out in Python (posixpath, json, urllib and
plain logic), never by running the JavaScript; the run test is what proves
node prints the same characters.
"""

from __future__ import annotations

import importlib
import pkgutil
import re
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import emit_jsnode
from code_coach.workbook.content_jsnode import JSNODE_PAGES

NEW = [(p, e) for p in JSNODE_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSNODE_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in JSNODE_PAGES}


def _expect(e) -> str:
    return emit_jsnode.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsnode.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not."""
    mine = {id(p) for p in JSNODE_PAGES}
    found = {id(p): p for p in pages() if id(p) not in mine}
    for info in pkgutil.iter_modules(workbook.__path__):
        if not info.name.startswith("content_"):
            continue
        try:
            module = importlib.import_module(f"code_coach.workbook.{info.name}")
        except Exception:  # noqa: BLE001 - a set still being written
            continue
        for name, value in vars(module).items():
            if name.endswith("_PAGES") and isinstance(value, tuple):
                for p in value:
                    if isinstance(p, Page) and id(p) not in mine:
                        found.setdefault(id(p), p)
    return list(found.values())


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSNODE_PAGES), 10)
        for p in JSNODE_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-node-"))
                self.assertTrue(p.name.startswith("Node: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSNODE_PAGES]
        self.assertEqual(used, list(emit_jsnode.SHAPE_IDS))
        for shape in emit_jsnode.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("js_node_"))
                self.assertTrue(emit_jsnode.handles(shape))
                self.assertIsNotNone(emit_jsnode.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jsnode.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jsnode.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSNODE_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSNODE_PAGES))
        for p in JSNODE_PAGES:
            for i, e in enumerate(p.exercises):
                self.assertEqual(e.id, f"{p.id}-{i + 1:02d}")
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_bodybuilding_pages(self) -> None:
        numbers = [p.number for p in JSNODE_PAGES]
        self.assertEqual(numbers, list(range(238, 248)))
        mine = {p.id for p in JSNODE_PAGES}
        # No other JavaScript page uses these numbers, registered or not;
        # later pages may follow at 248.
        theirs = {p.number for p in pages("javascript") if p.id not in mine}
        theirs |= {p.number for p in _others() if "javascript" in p.languages}
        self.assertFalse(theirs & set(numbers))
        from code_coach.workbook.content_jslifting import JSLIFTING_PAGES
        from code_coach.workbook.content_jsplanets import JSPLANETS_PAGES

        self.assertEqual(numbers[0], max(p.number for p in JSLIFTING_PAGES) + 1)
        self.assertEqual(
            max(p.number for p in JSPLANETS_PAGES) + 1,
            min(p.number for p in JSLIFTING_PAGES))

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSNODE_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))
                self.assertEqual(
                    len({e.prompt for e in p.exercises}), len(p.exercises))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("python", "typescript", "dart", "rust"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_jsnode.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a small program, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in JSNODE_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)
        for page in ("js-node-path", "js-node-args", "js-node-events",
                     "js-node-env"):
            said = {line for e in BY_ID[page].exercises
                    for line in _expect(e).split("\n")
                    if line in ("true", "false")}
            with self.subTest(page=page):
                self.assertEqual(said, {"true", "false"})
        # Some runs end in an error and some do not.
        exits = {_expect(e).splitlines()[-1] for e in BY_ID["js-node-env"].exercises
                 if e.args["want"] == "exit"}
        self.assertEqual(exits, {"exit code 0", "exit code 1"})
        # A request can hit a route, miss it, or use the wrong method.
        statuses = {_expect(e).split(" ")[0]
                    for e in BY_ID["js-node-routes"].exercises
                    if e.args["want"] in ("pages", "method", "greet")}
        self.assertLessEqual({"200", "404", "405"}, statuses)
        # Parsing a bad JSON text is caught, and a good one is not.
        safe = {_expect(e) == "invalid" for e in BY_ID["js-node-json"].exercises
                if e.args["want"] == "safe"}
        self.assertEqual(safe, {True, False})
        # A dotfile has no extension, and a double extension keeps the last.
        exts = [_expect(e) for e in BY_ID["js-node-path"].exercises
                if e.args["want"] == "ext"]
        self.assertIn("none", exts)
        self.assertIn(".gz", exts)

    def test_file_programs_stay_in_a_temporary_folder(self) -> None:
        """Files are made under os.tmpdir() and no path is ever printed."""
        files = ("js_node_read", "js_node_write", "js_node_json", "js_node_dirs")
        for _, e in NEW:
            if e.shape not in files or e.args.get("want") == "safe":
                continue
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertIn("fs.mkdtempSync(path.join(os.tmpdir()", code)
                self.assertNotRegex(code, r"console\.log\(\s*(dir|file|moved)\s*[,)]")
                self.assertNotIn("tmp", _expect(e).lower())
                self.assertNotIn("cc-", _expect(e))

    def test_servers_listen_on_localhost_only(self) -> None:
        for _, e in NEW:
            if e.shape not in ("js_node_http", "js_node_routes"):
                continue
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertIn("server.listen(0, '127.0.0.1'", code)
                self.assertIn("server.close();", code)
                self.assertEqual(set(re.findall(r"https?://[^/`'\"]+", code)),
                                 {"http://127.0.0.1:${server.address().port}"}
                                 | set(re.findall(r"http://x", code)))

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_jsnode.expected_output
        with self.assertRaises(ValueError):  # the same place: '' against '.'
            out("js_node_path", {"want": "rel", "from": "/a/b", "to": "/a/b"})
        with self.assertRaises(ValueError):  # no '..' to tidy
            out("js_node_path", {"want": "join", "parts": ["a", "b", "c"]})
        with self.assertRaises(ValueError):  # a flag with nothing after it
            out("js_node_args",
                {"want": "flag", "argv": ["node", "a.js", "--name"],
                 "flag": "name", "default": "Guest"})
        with self.assertRaises(ValueError):  # a tie for the longest line
            out("js_node_read",
                {"want": "longest", "file": "a.txt", "lines": ["ab", "cd", "e"]})
        with self.assertRaises(ValueError):  # unlinking what is not there
            out("js_node_write", {"want": "steps", "steps": ["delete", "check"]})
        with self.assertRaises(ValueError):  # already sorted: nothing to show
            out("js_node_dirs", {"want": "list", "names": ["a.txt", "b.txt", "c.txt"]})
        with self.assertRaises(ValueError):  # a floating-point value
            out("js_node_json", {"want": "safe", "text": "[1.5]"})
        with self.assertRaises(ValueError):  # timers closer than 10 ms
            out("js_node_events",
                {"want": "timers", "sync": "go",
                 "jobs": [("a", 20), ("b", 10), ("c", 15)]})
        with self.assertRaises(ValueError):  # an odd quote in a string
            emit_jsnode.solution(
                "javascript", "js_node_read",
                {"want": "count", "file": "a.txt", "lines": ["it's", "b", "c"]})
        with self.assertRaises(ValueError):  # a palindrome reverses to itself
            out("js_node_routes", {"want": "post", "reply": "reverse", "body": "level"})
        with self.assertRaises(ValueError):  # only a GET is the default
            out("js_node_routes",
                {"want": "method", "allowed": "GET", "sent": "POST", "ok": "x"})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsnode.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                stdout, stderr, code_ = run_code(code, language="javascript")
                if code_ == self.TIMED_OUT:
                    stdout, stderr, code_ = run_code(code, language="javascript")
                self.assertEqual(code_, 0, (stderr or stdout)[:400])
                self.assertTrue(
                    matches(stdout, _expect(e)),
                    f"printed {stdout!r}, wanted {_expect(e)!r}\n{code}")


if __name__ == "__main__":
    unittest.main()
