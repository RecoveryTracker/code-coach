"""The "Scripting" Python pages (342-351).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_pyscript
directly, so nothing here depends on the dispatch in emit.py or the workbook
package. Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.

The expected outputs are worked out with small models in Python (a path
splitter, an argparse model, a JSON writer and parser, a csv reader and
writer, a logging filter), never by running the programs; the run test is
what proves python prints the same characters.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
import tempfile
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import emit_pyscript
from code_coach.workbook.content_pyscript import PYSCRIPT_PAGES

NEW = [(p, e) for p in PYSCRIPT_PAGES for e in p.exercises]
REGISTERED = any(p.id == PYSCRIPT_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in PYSCRIPT_PAGES}
SERVERS = ("py_script_http",)


def _expect(e) -> str:
    return emit_pyscript.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_pyscript.solution("python", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    Not the review pages: they are built from the pages above and replay
    their exercises on purpose, so once these are registered a review page
    carries every one of these shapes.
    """
    mine = {id(p) for p in PYSCRIPT_PAGES}
    found = {id(p): p for p in pages() if id(p) not in mine and not p.id.startswith("review-")}
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


def _data_loop_depth(node, d: int = 0) -> int:
    """How deeply the program loops over data (the rule in test_workbook)."""

    def fixed(it) -> bool:
        if isinstance(it, (ast.Tuple, ast.List)):
            return True
        return (isinstance(it, ast.Call) and isinstance(it.func, ast.Name)
                and it.func.id == "range"
                and all(isinstance(a, ast.Constant) for a in it.args))

    best = d
    for child in ast.iter_child_nodes(node):
        step = 0
        if isinstance(child, (ast.For, ast.AsyncFor)):
            step = 0 if fixed(child.iter) else 1
        elif isinstance(child, ast.While):
            step = 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp,
                                ast.GeneratorExp)):
            step = sum(0 if fixed(g.iter) else 1 for g in child.generators)
        best = max(best, _data_loop_depth(child, d + step))
    return best


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(PYSCRIPT_PAGES), 10)
        for p in PYSCRIPT_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("py-script-"))
                self.assertTrue(p.name.startswith("Scripting: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("python",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in PYSCRIPT_PAGES]
        self.assertEqual(used, list(emit_pyscript.SHAPE_IDS))
        for shape in emit_pyscript.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("py_script_"))
                self.assertTrue(emit_pyscript.handles(shape))
                self.assertIsNotNone(emit_pyscript.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_pyscript.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_pyscript.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in PYSCRIPT_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(PYSCRIPT_PAGES))
        for p in PYSCRIPT_PAGES:
            for i, e in enumerate(p.exercises):
                self.assertEqual(e.id, f"{p.id}-{i + 1:02d}")
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_last_python_page(self) -> None:
        numbers = [p.number for p in PYSCRIPT_PAGES]
        self.assertEqual(numbers, list(range(342, 352)))
        mine = {p.id for p in PYSCRIPT_PAGES}
        # No other Python page uses these numbers, registered or not; later
        # pages may follow at 352. The review pages are left out because they
        # are numbered from whatever the last page is, so they move up.
        theirs = {p.number for p in pages("python")
                  if p.id not in mine and p.tier != "review"}
        theirs |= {p.number for p in _others()
                   if p.applies_to("python") and p.tier != "review"}
        self.assertFalse(theirs & set(numbers))
        from code_coach.workbook.content_graph import GRAPH_PAGES

        self.assertEqual(numbers[0], max(p.number for p in GRAPH_PAGES) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in PYSCRIPT_PAGES:
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
            for language in ("javascript", "typescript", "dart", "rust"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_pyscript.solution(language, e.shape, e.args))
            self.assertIsNotNone(emit_pyscript.solution("python", e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a small program, not a project.

        A server is the exception: a handler class, a thread and a client
        cannot be done in ten lines, so those get room, and no more.
        """
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(
                    len(lines),
                    emit_pyscript.SERVER_LIMIT if e.shape in SERVERS
                    else emit_pyscript.LIMIT)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in PYSCRIPT_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)

        def outputs(page, **match):
            return [_expect(e) for e in BY_ID[page].exercises
                    if all(e.args.get(k) == v for k, v in match.items())]

        # Absolute and not; a relative path outside its base; a dotfile has
        # no suffix, a double extension keeps the last; a suffix is added
        # to a name that has none.
        self.assertEqual(set(outputs("py-script-path", want="abs")), {"True", "False"})
        self.assertIn("outside", outputs("py-script-path", want="rel"))
        stems = outputs("py-script-path", want="stem")
        self.assertTrue(any(s.endswith("none") for s in stems))
        self.assertTrue(any(s.endswith(".gz") for s in stems))
        self.assertIn("/srv/app/Makefile.bak",
                      outputs("py-script-path", want="with_suffix"))
        # A flag is on and off, and the parser quits for some and not others.
        flags = {_expect(e) for e in BY_ID["py-script-args"].exercises
                 if e.args["show"].get("attr") == "verbose"
                 and any(s["kind"] == "flag" and "--verbose" in s["flags"]
                         for s in e.args["spec"])}
        self.assertEqual(flags, {"True", "False"})
        errors = {_expect(e).split(" ")[0] for e in BY_ID["py-script-args"].exercises
                  if e.args["want"] == "error"}
        self.assertEqual(errors, {"ok", "exit"})
        # A count with no default is None, which is not 0.
        self.assertIn("None", outputs("py-script-args", want="attr"))
        # Bytes are not characters.
        for e in BY_ID["py-script-files"].exercises:
            if e.args["want"] == "size":
                with self.subTest(exercise=e.id):
                    self.assertGreaterEqual(int(_expect(e)), len(e.args["text"]))
        sizes = [int(_expect(e)) - len(e.args["text"])
                 for e in BY_ID["py-script-files"].exercises
                 if e.args["want"] == "size"]
        self.assertTrue(any(s > 0 for s in sizes) and any(s == 0 for s in sizes))
        # The first line of a file that is not there, and the same after a write.
        steps = {line for e in BY_ID["py-script-files"].exercises
                 if e.args["want"] == "steps" for line in _expect(e).split("\n")}
        self.assertEqual(steps, {"True", "False"})
        # A bad JSON text is caught, and a good one is not.
        safe = {_expect(e) == "invalid" for e in BY_ID["py-script-json"].exercises
                if e.args["want"] == "safe"}
        self.assertEqual(safe, {True, False})
        # json.dumps puts a space after the comma and the colon.
        self.assertTrue(any(": " in o for o in outputs("py-script-json", want="update")))
        # All three ways a mkdir can go.
        modes = {e.args["mode"] for e in BY_ID["py-script-dirs"].exercises
                 if e.args["want"] == "mkdir"}
        self.assertEqual(modes, {"exists", "exist_ok", "noparents"})
        # Sorting matters: 'file10' lands before 'file2'.
        self.assertTrue(any("file10.txt, file2.txt" in o
                            for o in outputs("py-script-dirs", want="list")))
        # A field that needs quotes, with and without a quote inside it.
        written = outputs("py-script-csv", want="write")
        self.assertTrue(any('"' in o and '""' not in o for o in written))
        self.assertTrue(any('""' in o for o in written))
        # Some records are dropped by the level, and loggers have names.
        for e in BY_ID["py-script-log"].exercises:
            if e.args["want"] == "emit":
                with self.subTest(exercise=e.id):
                    self.assertLessEqual(len(_expect(e).split("\n")),
                                         len(e.args["calls"]))
        self.assertTrue(any(len(_expect(e).split("\n")) < len(e.args["calls"])
                            for e in BY_ID["py-script-log"].exercises
                            if e.args["want"] == "emit"))
        self.assertTrue(any("app.db" in o for o in outputs("py-script-log", want="emit")))
        # Some runs end in an error and some do not; sys.exit() is None.
        exits = {_expect(e).splitlines()[-1] for e in BY_ID["py-script-env"].exercises
                 if e.args["want"] == "exit"}
        self.assertEqual(exits, {"exit code 0", "exit code 1"})
        self.assertIn("None", outputs("py-script-env", want="sysexit"))
        # A request can hit a route, miss it, or ask in a different way.
        statuses = {_expect(e).split(" ")[0] for e in BY_ID["py-script-http"].exercises
                    if e.args["want"] in ("query", "pages")}
        self.assertEqual(statuses, {"200", "404"})
        self.assertIn("application/json\n5", outputs("py-script-http", want="calc"))
        # A wait can time out and can finish.
        waits = {_expect(e) == "timeout" for e in BY_ID["py-script-async"].exercises
                 if e.args["want"] == "timeout"}
        self.assertEqual(waits, {True, False})

    def test_text_is_always_written_as_utf8(self) -> None:
        """The machine's default encoding is not the same on every machine."""
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertNotIn("read_text()", code)
                self.assertNotIn("open()", code)
                for line in code.splitlines():
                    if "write_text(" in line or ".open(" in line:
                        self.assertIn('encoding="utf-8"', line)

    def test_file_programs_stay_in_a_temporary_folder(self) -> None:
        """Files are made in a TemporaryDirectory and no path is ever printed."""
        files = ("py_script_files", "py_script_json", "py_script_dirs")
        temp = tempfile.gettempdir().lower()
        for _, e in NEW:
            if e.shape not in files or e.args.get("want") == "safe":
                continue
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertIn("with tempfile.TemporaryDirectory() as tmp:", code)
                self.assertNotRegex(
                    code, r"print\(\s*(tmp|file|root|target|moved)\s*[,)]")
                self.assertNotIn("tmp", _expect(e).lower())
                self.assertNotIn(temp, _expect(e).lower())

    def test_servers_listen_on_localhost_only(self) -> None:
        for _, e in NEW:
            if e.shape not in SERVERS:
                continue
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertIn('HTTPServer(("127.0.0.1", 0), Handler)', code)
                self.assertIn("server.shutdown()", code)
                self.assertIn("daemon=True", code)
                # Without this poll interval shutdown() waits half a second.
                self.assertIn("serve_forever, args=(0.01,)", code)
                hosts = set(re.findall(r"https?://[^/\"{]+(?:\{[^}]*\})?", code))
                self.assertEqual(hosts, {"http://127.0.0.1:{server.server_port}"})
                self.assertNotIn("0.0.0.0", code)

    def test_the_oracle_is_a_model_not_the_library(self) -> None:
        """The module that works out the answers imports none of the
        libraries the answers use, so it cannot agree with them by being
        them."""
        modules = {name for name, value in vars(emit_pyscript).items()
                   if inspect.ismodule(value)}
        self.assertEqual(modules, {"re"})
        source = inspect.getsource(emit_pyscript)
        for library in ("json", "csv", "logging", "argparse", "pathlib",
                        "asyncio", "urllib", "subprocess", "tempfile"):
            self.assertNotRegex(source, rf"(?m)^\s*(import|from)\s+{library}\b")

    def test_complexity_notes_do_not_contradict_the_code(self) -> None:
        """The rule in test_workbook, held to every program rather than the
        first of each shape: constant means no loop over data, linear means
        no loop inside a loop."""
        for _, e in NEW:
            note = emit_pyscript.for_shape(e.shape)
            depth = _data_loop_depth(ast.parse(_answer(e)))
            with self.subTest(exercise=e.id, label=note.label):
                if note.label == "O(1)":
                    self.assertEqual(depth, 0)
                elif note.label == "O(n)":
                    self.assertLess(depth, 2)
                elif note.label.startswith("O(n²)"):
                    self.assertGreaterEqual(depth, 2)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_pyscript.expected_output

        def refuses(why: str, shape: str, **args) -> None:
            with self.subTest(why=why):
                with self.assertRaises(ValueError):
                    out(shape, args)

        refuses("nothing for pathlib to treat specially", "py_script_path",
                want="join", base="/srv", rest=["a", "b"], how="slash")
        refuses("the same place, which prints as a dot", "py_script_path",
                want="rel", p="/a/b", base="/a/b")
        refuses("parents index off the end", "py_script_path",
                want="parent", p="/a/b", up=1)
        refuses("a name ending in a dot", "py_script_path", want="parts", p="/a/b.")
        refuses("a dot piece in a plain path", "py_script_path",
                want="stem", p="/a/./b.txt")
        refuses("argparse accepts an abbreviation", "py_script_args",
                want="attr", spec=[{"kind": "flag", "flags": ["--verbose"]}],
                argv=["--verb"], show={"attr": "verbose"})
        refuses("positionals split by an option", "py_script_args",
                want="join", spec=[{"kind": "flag", "flags": ["-v"]},
                                   {"kind": "positional", "name": "files", "many": True}],
                argv=["a", "-v", "b"], show={"join": "files"})
        refuses("a negative number is special", "py_script_args",
                want="sum", spec=[{"kind": "positional", "name": "numbers",
                                   "many": True, "type": "int"}],
                argv=["-3", "4"], show={"sum": "numbers"})
        refuses("a run that quits but does not catch it", "py_script_args",
                want="attr", spec=[{"kind": "option", "flags": ["--port"], "type": "int"}],
                argv=["--port", "abc"], show={"attr": "port"})
        refuses("a tie for the longest line", "py_script_files",
                want="longest", file="a.txt", lines=["ab", "cd", "e"])
        refuses("unlinking what is not there", "py_script_files",
                want="steps", steps=["delete", "check"])
        refuses("a blank line", "py_script_files",
                want="count", file="a.txt", lines=["a", "", "c"])
        refuses("a floating-point value", "py_script_json",
                want="safe", text="[1.5]")
        refuses("keys already sorted", "py_script_json",
                want="sorted", obj={"a": 1, "b": 2, "c": 3})
        refuses("a step of nothing", "py_script_json",
                want="update", obj={"count": 5}, key="count", step=0)
        refuses("a saved value equal to the default", "py_script_json",
                want="default", key="theme", default="light", saved="light")
        refuses("already sorted: nothing to show", "py_script_dirs",
                want="list", names=["a.txt", "b.txt", "c.txt"])
        refuses("an extension that keeps everything", "py_script_dirs",
                want="ext", names=["a.js", "b.js", "c.js"], ext="js")
        refuses("a folder name that is not plain", "py_script_dirs",
                want="mkdir", path=["a", "2024"], mode="exists")
        refuses("a field that needs no quotes", "py_script_csv",
                want="write", rows=[["a", "b"], ["1", "2"], ["3", "4"]])
        refuses("a key that never repeats", "py_script_csv",
                want="group", rows=[["k", "n"], ["a", "1"], ["b", "2"]],
                key="k", num="n")
        refuses("a delimiter that is a comma", "py_script_csv",
                want="delimiter", rows=[["a", "b"], ["1", "2"], ["3", "4"]],
                row=1, col=0)
        refuses("a format without the message", "py_script_log",
                want="emit", fmt="%(levelname)s", level="INFO",
                calls=[(None, "info", "a"), (None, "error", "b")])
        refuses("a field this page does not know", "py_script_log",
                want="emit", fmt="%(asctime)s %(message)s", level="INFO",
                calls=[(None, "info", "a"), (None, "error", "b")])
        refuses("nothing gets through", "py_script_log",
                want="emit", fmt="%(message)s", level="CRITICAL",
                calls=[(None, "info", "a"), (None, "error", "b")])
        refuses("a count that drops nothing", "py_script_log",
                want="count", fmt="%(message)s", level="DEBUG",
                calls=[(None, "info", "a"), (None, "error", "b")])
        refuses("an argument too many", "py_script_log",
                want="args", fmt="%(message)s", level="INFO",
                calls=[("info", "one %d", [1, 2]), ("info", "two", [])])
        refuses("a PORT of zero", "py_script_env",
                want="port", env={"PORT": "0"}, default=3000)
        refuses("a program the model does not know", "py_script_env",
                want="child", code="import os; os._exit(9)")
        refuses("an exit code that does not fit a byte", "py_script_env",
                want="child", code="raise SystemExit(300)")
        refuses("a 404 on the plain page", "py_script_http",
                want="body", status=404, text="gone")
        refuses("a method with a body to read", "py_script_http",
                want="method", method="POST", path="/items")
        refuses("a header that is not on the list", "py_script_http",
                want="header", header="Content-Type", value="x", text="y")
        refuses("a repeated query parameter", "py_script_http",
                want="query", fallback="x", path="/hello?name=a&name=b")
        refuses("a result of zero", "py_script_http",
                want="calc", keys=["a", "b"], op="-", x=3, y=3)
        refuses("timers closer than 20 ms", "py_script_async",
                want="order", jobs=[("a", 30), ("b", 10), ("c", 20)])
        refuses("jobs already in order", "py_script_async",
                want="results", jobs=[("a", 20), ("b", 40), ("c", 60)])
        refuses("a delay too close to its limit", "py_script_async",
                want="timeout", delay=40, limit=30, word="done")
        refuses("a sync line that is also a label", "py_script_async",
                want="tasks", jobs=[("a", 30), ("go", 10)], sync="go")
        refuses("a delay that is not a multiple of ten", "py_script_async",
                want="completed", jobs=[("a", 65), ("b", 20), ("c", 40)])
        with self.assertRaises(ValueError):  # an odd quote in a string
            emit_pyscript.solution(
                "python", "py_script_files",
                {"want": "count", "file": "a.txt", "lines": ["it's", "b", "c"]})
        with self.assertRaises(KeyError):
            out("py_script_nothing", {})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("python"), _answer(e))
                self.assertIsNone(e.answer("javascript"))
        for shape in emit_pyscript.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        temp = tempfile.gettempdir()
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                stdout, stderr, code_ = run_code(code, language="python")
                if code_ == self.TIMED_OUT:
                    stdout, stderr, code_ = run_code(code, language="python")
                self.assertEqual(code_, 0, (stderr or stdout)[:400])
                self.assertTrue(
                    matches(stdout, _expect(e)),
                    f"printed {stdout!r}, wanted {_expect(e)!r}\n{code}")
                self.assertNotIn(temp, stdout)


if __name__ == "__main__":
    unittest.main()
