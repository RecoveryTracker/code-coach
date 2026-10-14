"""The "Web servers and HTTP" Python pages (352-361).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_pyweb directly,
so nothing here depends on the dispatch in emit.py or the workbook package.
Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.

The expected outputs are worked out with small models in Python (a URL
splitter, a query-string decoder, a percent-encoder, a relative-URL resolver,
a status table, a request parser, a router, the little server each program
stands up, a cookie writer, a WSGI app, a template engine), never by running
the programs; the run test is what proves python prints the same characters.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import emit_pyweb
from code_coach.workbook.content_pyweb import PYWEB_PAGES

NEW = [(p, e) for p in PYWEB_PAGES for e in p.exercises]
REGISTERED = any(p.id == PYWEB_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in PYWEB_PAGES}
SERVERS = emit_pyweb.SERVERS
FIRST = 352


def _expect(e) -> str:
    return emit_pyweb.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_pyweb.solution("python", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    Not the review pages: they are built from the pages above and replay
    their exercises on purpose, so once these are registered a review page
    carries every one of these shapes.
    """
    mine = {id(p) for p in PYWEB_PAGES}
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
        self.assertEqual(len(PYWEB_PAGES), 10)
        for p in PYWEB_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("py-web-"))
                self.assertTrue(p.name.startswith("Web: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("python",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in PYWEB_PAGES]
        self.assertEqual(used, list(emit_pyweb.SHAPE_IDS))
        for shape in emit_pyweb.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("py_web_"))
                self.assertTrue(emit_pyweb.handles(shape))
                self.assertIsNotNone(emit_pyweb.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_pyweb.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_pyweb.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in PYWEB_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(PYWEB_PAGES))
        for p in PYWEB_PAGES:
            for i, e in enumerate(p.exercises):
                self.assertEqual(e.id, f"{p.id}-{i + 1:02d}")
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_are_consecutive_and_unused(self) -> None:
        numbers = [p.number for p in PYWEB_PAGES]
        self.assertEqual(numbers, list(range(numbers[0], numbers[0] + 10)))
        self.assertGreaterEqual(numbers[0], FIRST)
        mine = {p.id for p in PYWEB_PAGES}
        # No other Python page uses these numbers, registered or not. The
        # review pages are left out because they are numbered from whatever
        # the last page is, so they move up.
        theirs = {p.number for p in pages("python")
                  if p.id not in mine and p.tier != "review"}
        theirs |= {p.number for p in _others()
                   if p.applies_to("python") and p.tier != "review"}
        self.assertFalse(theirs & set(numbers))

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in PYWEB_PAGES:
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
                        emit_pyweb.solution(language, e.shape, e.args))
            self.assertIsNotNone(emit_pyweb.solution("python", e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a small program, not a project.

        A server, a router and a WSGI app are the exceptions: a handler
        class, a thread and a client cannot be done in ten lines, so those
        get room (emit_pyweb.limit_for), and no more.
        """
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), emit_pyweb.limit_for(e.shape))
        for shape in emit_pyweb.SHAPE_IDS:
            if shape in SERVERS:
                self.assertLessEqual(emit_pyweb.limit_for(shape), 28)
            else:
                self.assertLessEqual(emit_pyweb.limit_for(shape), 18)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in PYWEB_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)

        def outputs(page, **match):
            return [_expect(e) for e in BY_ID[page].exercises
                    if all(e.args.get(k) == v for k, v in match.items())]

        # URLs: an empty part is none, a missing port is None, the hostname
        # is lower case, a blank parameter is dropped, an accent is two
        # escapes, a space is a plus in a query and %20 in a path, and a
        # .. is resolved.
        self.assertIn("none", outputs("py-web-url", want="part"))
        ports = outputs("py-web-url", want="port")
        self.assertTrue(any(o.endswith(" None") for o in ports))
        self.assertTrue(any(o.startswith("example.com ") and "Example" not in o for o in ports))
        self.assertTrue(any("'b'" not in o for o in outputs("py-web-url", want="qs", show="dict")))
        self.assertTrue(any("%C3%A9" in o for o in outputs("py-web-url", want="quote")))
        self.assertTrue(any("a%20b/c" == o for o in outputs("py-web-url", want="quote")))
        self.assertTrue(any("%2F" in o for o in outputs("py-web-url", want="quote")))
        encoded = outputs("py-web-url", want="urlencode")
        self.assertTrue(any("+" in o for o in encoded))
        self.assertIn("tag=a&tag=b&page=1", encoded)
        self.assertIn("https://example.com/a/d.html", outputs("py-web-url", want="join"))
        # Status: every class of answer turns up, and the retry list leaves
        # the 4xx codes out bar 429.
        classes = "\n".join(outputs("py-web-status", want="classify"))
        for word in ("informational", "success", "redirection", "client error",
                     "server error"):
            self.assertIn(word, classes)
        for o in outputs("py-web-status", want="retry"):
            self.assertNotIn("404", o)
        # Headers: carriage returns show up, bytes are not characters, and
        # a charset is added to text only.
        self.assertTrue(all("\\r\\n" in o for o in outputs("py-web-headers", want="raw")))
        for e in BY_ID["py-web-headers"].exercises:
            if e.args["want"] == "length":
                self.assertGreaterEqual(int(_expect(e).split(" ")[1]), len(e.args["body"]))
        sizes = [int(_expect(e).split(" ")[1]) - len(e.args["body"])
                 for e in BY_ID["py-web-headers"].exercises if e.args["want"] == "length"]
        self.assertTrue(any(s > 0 for s in sizes) and any(s == 0 for s in sizes))
        kinds = outputs("py-web-headers", want="ctype")
        self.assertIn("text/html; charset=utf-8", kinds)
        self.assertIn("application/octet-stream", kinds)
        self.assertIn("image/png", kinds)
        self.assertIn("none", {o.split(" ")[-1] for o in outputs("py-web-headers", want="mediatype")})
        # Request: no query is none, a request line can be wrong, and a
        # Host with no port means 80.
        self.assertIn("/about\nnone",outputs("py-web-request", want="path"))
        self.assertEqual(set(outputs("py-web-request", want="valid")), {"ok", "400 Bad Request"})
        ports = {o.split(" ")[1] for o in outputs("py-web-request", want="hostport")}
        self.assertIn("80", ports)
        self.assertTrue(ports - {"80"})
        # Route: a path can be missing or have the wrong method, and a
        # pattern can fail to match.
        for page, want in (("py-web-route", "dispatch"), ("py-web-route", "decorator")):
            self.assertTrue(any("404 Not Found" in o for o in outputs(page, want=want)))
        self.assertTrue(any("405 Method Not Allowed" in o
                            for o in outputs("py-web-route", want="methods")))
        patterns = outputs("py-web-route", want="pattern")
        self.assertIn("None", patterns)
        self.assertTrue(any(o.startswith("{") for o in patterns))
        # Server GETs: both statuses, a 405 with its Allow header, a 501 the
        # base class makes, a redirect that is followed, a missing name.
        routed = {line.split(" ")[1] for o in outputs("py-web-get", want="route")
                  for line in o.split("\n")}
        self.assertEqual(routed, {"200", "404"})
        methods = "\n".join(outputs("py-web-get", want="methods"))
        for text in ("405 GET", "200 -", "404 -"):
            self.assertIn(text, methods)
        self.assertTrue(all(o.startswith("501 Unsupported method")
                            for o in outputs("py-web-get", want="unsupported")))
        self.assertIn("200 /c", outputs("py-web-get", want="redirect"))
        self.assertTrue(any("stranger" in o for o in outputs("py-web-get", want="query")))
        self.assertTrue(any("none" in o for o in outputs("py-web-get", want="tags", show="join")))
        sums = "\n".join(outputs("py-web-get", want="sum"))
        self.assertIn("200 5", sums)
        self.assertIn("400 bad request", sums)
        # JSON API: a good body, a body with no name and a body that is not
        # JSON; ids count up from what is stored.
        invalid = [o.split(" ")[0] for o in outputs("py-web-api", want="invalid")]
        self.assertEqual(set(invalid), {"200", "400"})
        creates = outputs("py-web-api", want="create")
        self.assertIn("201 1", creates[0])
        self.assertTrue(any(o.startswith("201 2") for o in creates))
        lengths = outputs("py-web-api", want="length")
        self.assertTrue(all(o.startswith("application/json\n") for o in lengths))
        self.assertEqual(len({o.split("\n")[1] for o in lengths}), len(lengths))
        # Cookies: attributes come out sorted, not as set; a flag parses as
        # True; membership goes both ways.
        attrs = outputs("py-web-cookies", want="attrs")
        self.assertIn("Set-Cookie: session=abc123; HttpOnly; Path=/", attrs)
        self.assertTrue(any("Max-Age=3600; Path=/; Secure" in o for o in attrs))
        self.assertIn("True", outputs("py-web-cookies", want="parseattr"))
        # output() sorts the cookies by name too.
        for e in BY_ID["py-web-cookies"].exercises:
            if e.args["want"] == "many":
                names = [k for k, _ in e.args["pairs"]]
                shown = [line.split(":")[1].split("=")[0].strip()
                         for line in _expect(e).split("\n")]
                self.assertEqual(shown, sorted(names))
                self.assertNotEqual(shown, names)
        self.assertEqual(set(outputs("py-web-cookies", want="has")), {"True", "False"})
        self.assertIn("3", outputs("py-web-cookies", want="value"))
        # WSGI: all three statuses, and a middleware changes only the body.
        statuses = {o.split(" ")[0] + " " + o.split(" ")[1]
                    for o in outputs("py-web-wsgi", want="path")
                    + outputs("py-web-wsgi", want="method")}
        self.assertEqual(statuses, {"200 OK", "404 Not", "405 Method"})
        self.assertTrue(any("application/json" in o for o in outputs("py-web-wsgi", want="accept")))
        self.assertTrue(any("text/plain" in o for o in outputs("py-web-wsgi", want="accept")))
        self.assertTrue(any("HELLO WORLD" in o for o in outputs("py-web-wsgi", want="middleware")))
        # Templates: a placeholder left alone, a name reported missing, a
        # dollar sign kept, markup escaped.
        self.assertTrue(any("$amount" in o for o in outputs("py-web-template", want="safe")))
        self.assertTrue(any(o.startswith("missing ") for o in outputs("py-web-template", want="keyerror")))
        self.assertTrue(any(not o.startswith("missing ")
                            for o in outputs("py-web-template", want="keyerror")))
        self.assertTrue(any("$" in o for o in outputs("py-web-template", want="dollar")))
        escaped = "\n".join(outputs("py-web-template", want="escape"))
        for text in ("&amp;", "&lt;", "&gt;", "&quot;"):
            self.assertIn(text, escaped)

    def test_servers_listen_on_localhost_only(self) -> None:
        for _, e in NEW:
            if e.shape not in SERVERS:
                continue
            code = _answer(e)
            with self.subTest(exercise=e.id):
                self.assertIn('HTTPServer(("127.0.0.1", 0), Handler)', code)
                self.assertIn("server.shutdown()", code)
                self.assertIn("server.server_close()", code)
                self.assertIn("daemon=True", code)
                # Without this poll interval shutdown() waits half a second.
                self.assertIn("serve_forever, args=(0.01,)", code)
                hosts = set(re.findall(r"https?://[^/\"{]+(?:\{[^}]*\})?", code))
                self.assertEqual(hosts, {"http://127.0.0.1:{server.server_port}"})
                self.assertNotIn("0.0.0.0", code)

    def test_nothing_else_opens_a_socket_and_no_port_is_printed(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                if e.shape not in SERVERS:
                    for word in ("socket", "HTTPServer", "urlopen", "threading"):
                        self.assertNotIn(word, code)
                for line in code.splitlines():
                    if "print(" in line:
                        self.assertNotIn("server_port", line)
                        self.assertNotIn("reply.url", line)
                self.assertNotRegex(_expect(e), r"127\.0\.0\.1|localhost")
                # No clock, no randomness: every run prints the same.
                for word in ("datetime", "time.", "random", "uuid", "secrets"):
                    self.assertNotIn(word, code)

    def test_the_oracle_is_a_model_not_the_library(self) -> None:
        """The module that works out the answers imports none of the
        libraries the answers use, so it cannot agree with them by being
        them."""
        modules = {name for name, value in vars(emit_pyweb).items()
                   if inspect.ismodule(value)}
        self.assertEqual(modules, {"re"})
        source = inspect.getsource(emit_pyweb)
        for library in ("json", "urllib", "http", "string", "html", "io",
                        "socket", "threading", "wsgiref", "email"):
            self.assertNotRegex(source, rf"(?m)^\s*(import|from)\s+{library}\b")

    def test_complexity_notes_do_not_contradict_the_code(self) -> None:
        """The rule in test_workbook, held to every program rather than the
        first of each shape: constant means no loop over data, linear means
        no loop inside a loop."""
        for _, e in NEW:
            note = emit_pyweb.for_shape(e.shape)
            depth = _data_loop_depth(ast.parse(_answer(e)))
            with self.subTest(exercise=e.id, label=note.label):
                if note.label == "O(1)":
                    self.assertEqual(depth, 0)
                elif note.label == "O(n)":
                    self.assertLess(depth, 2)
                elif note.label.startswith("O(n²)"):
                    self.assertGreaterEqual(depth, 2)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_pyweb.expected_output

        def refuses(why: str, shape: str, **args) -> None:
            with self.subTest(why=why):
                with self.assertRaises(ValueError):
                    out(shape, args)

        ok_url = "https://example.com/a/b/c.html"
        refuses("a port out of range", "py_web_url", want="port",
                url="http://example.com:99999/a")
        refuses("a part urlsplit does not have", "py_web_url", want="part",
                url=ok_url, part="host")
        refuses("a URL with no scheme", "py_web_url", want="part",
                url="example.com/a", part="path")
        refuses("a semicolon in a query", "py_web_url", want="qs",
                query="a=1;b=2", show="dict")
        refuses("a key that is not in the query", "py_web_url", want="qs",
                query="a=1&a=2", show="first", key="z")
        refuses("a list of one is not a repeat", "py_web_url", want="qs",
                query="a=1&b=2", show="all", key="a")
        refuses("a quote that quotes nothing new", "py_web_url", want="quote",
                text="a/b")
        refuses("safe none with no slash to encode", "py_web_url", want="quote",
                text="a b", safe="")
        refuses("a list needs doseq", "py_web_url", want="urlencode",
                params=[("tag", ["a", "b"]), ("page", 1)])
        refuses("a .. above the root", "py_web_url", want="join",
                base="https://example.com/a.html", ref="../../x.html")
        refuses("a scheme the model does not resolve", "py_web_url", want="join",
                base=ok_url, ref="mailto:ada")
        refuses("a code not on the list", "py_web_status", want="phrase", code=418)
        refuses("a count that is all of them", "py_web_status", want="count",
                codes=[301, 302, 307], klass=3)
        refuses("a retry that retries everything", "py_web_status", want="retry",
                codes=[500, 502, 503])
        refuses("a 408 is a puzzle", "py_web_status", want="retry",
                codes=[200, 408, 503])
        refuses("two codes the same", "py_web_status", want="lookup",
                codes=[200, 200, 404])
        refuses("duplicate header names", "py_web_headers", want="raw", status=200,
                headers=[("X-A", "1"), ("x-a", "2")], body="hi")
        refuses("a body with a quote in it", "py_web_headers", want="raw",
                status=200, headers=[("X-A", "1")], body="it's")
        refuses("a Content-Length given and added", "py_web_headers", want="rawlen",
                status=200, headers=[("Content-Length", "2")], body="hi")
        refuses("an ask in upper case", "py_web_headers", want="lookup",
                headers=[("Accept", "x"), ("X-A", "y")], ask="Accept")
        refuses("a header that is not there", "py_web_headers", want="lookup",
                headers=[("Accept", "x"), ("X-A", "y")], ask="etag")
        refuses("a request line that is not a request", "py_web_request",
                want="method", line="hello there")
        refuses("a method not on the list", "py_web_request", want="method",
                line="BREW /pot HTTP/1.1")
        refuses("one header only", "py_web_request", want="count",
                line="GET / HTTP/1.1", headers=[("Host", "a.com")])
        refuses("a Content-Length that lies", "py_web_request", want="body",
                line="POST / HTTP/1.1", body="hello",
                headers=[("Host", "a.com"), ("Content-Length", "9")])
        refuses("a header asked in a different case from lower", "py_web_request",
                want="header", line="GET / HTTP/1.1",
                headers=[("Host", "a.com"), ("Accept", "x")], ask="Host")
        refuses("a function name that is not a name", "py_web_route",
                want="dispatch", routes=[("/", "Home", "x"), ("/a", "about", "y")],
                paths=["/", "/a", "/b"])
        refuses("every path routed", "py_web_route", want="dispatch",
                routes=[("/", "home", "x"), ("/a", "about", "y")],
                paths=["/", "/a", "/"])
        refuses("a trailing page with no slash to strip", "py_web_route",
                want="trailing", routes=[("/", "home", "x"), ("/a", "about", "y")],
                paths=["/", "/a", "/b"])
        refuses("methods that never say 404", "py_web_route", want="methods",
                routes=[("GET", "/", "home", "x"), ("POST", "/a", "about", "y")],
                requests=[("GET", "/"), ("GET", "/a"), ("POST", "/a")])
        refuses("a pattern with a capital", "py_web_route", want="pattern",
                pattern="/Users/<id>", path="/Users/7")
        refuses("a 200 route table with a repeated page", "py_web_get", want="route",
                pages=[("/", "a"), ("/", "b")], paths=["/", "/x", "/y"])
        refuses("every path found", "py_web_get", want="route",
                pages=[("/", "a"), ("/b", "b")], paths=["/", "/b", "/"])
        refuses("a status that is not an error", "py_web_get", want="error",
                status=200, text="ok")
        refuses("no path asked twice", "py_web_get", want="hits",
                paths=["/a", "/b", "/c"])
        refuses("a method that is not asked", "py_web_get", want="methods",
                path="/a", requests=[("PUT", "/a"), ("GET", "/a"), ("GET", "/b")])
        refuses("a method that gets a 405 from the model", "py_web_get",
                want="unsupported", method="POST")
        refuses("a redirect that is not one", "py_web_get", want="redirect",
                code=200, chain=[("/a", "/b")], start="/a")
        refuses("a start that is not redirected", "py_web_get", want="redirect",
                code=301, chain=[("/a", "/b")], start="/z")
        refuses("every sum a good one", "py_web_get", want="sum",
                paths=["/add?a=1&b=2", "/add?a=3&b=4", "/add?a=5&b=6"])
        refuses("a body that is not an error", "py_web_api", want="invalid",
                kind="bad", text="[1, 2, 3]")
        refuses("a missing key that is the key", "py_web_api", want="invalid",
                kind="missing", key="name", value="Ada")
        refuses("a palindrome reversed", "py_web_api", want="word", word="level",
                how="reverse")
        refuses("numbers that repeat", "py_web_api", want="total", op="sum",
                numbers=[3, 3, 4])
        refuses("an op the server lacks", "py_web_api", want="total", op="avg",
                numbers=[1, 2, 3])
        refuses("too many posts", "py_web_api", want="create",
                names=["a", "b", "c", "d", "e"])
        refuses("attributes already in order", "py_web_cookies", want="attrs",
                name="s", value="x", attrs=[("httponly", True), ("path", "/")])
        refuses("a flag set to a string", "py_web_cookies", want="attrs",
                name="s", value="x", attrs=[("path", "/"), ("secure", "yes")])
        refuses("cookies already in order: output() would not show its sort",
                "py_web_cookies", want="many", pairs=[("a", 1), ("b", 2)])
        refuses("a cookie value with a space", "py_web_cookies", want="value",
                pairs=[("a", "x y"), ("b", "z")], ask="a")
        refuses("a cookie name that is not there", "py_web_cookies", want="value",
                pairs=[("a", "1"), ("b", "2")], ask="c")
        refuses("an attribute that is not set", "py_web_cookies", want="parseattr",
                header="a=1; Path=/", name="a", attr="secure")
        refuses("a unknown attribute", "py_web_cookies", want="parseattr",
                header="a=1; Weird=2", name="a", attr="weird")
        refuses("a mime type the model has not", "py_web_wsgi", want="hello",
                type="image/png", body="x")
        refuses("a method that is not on the list", "py_web_wsgi", want="method",
                allowed="PUT", method="GET", body="x")
        refuses("a body the middleware does not change", "py_web_wsgi",
                want="middleware", how="upper", body="123")
        refuses("a body with a double space", "py_web_wsgi", want="post",
                data="a  b", reply="words")
        refuses("a placeholder never filled", "py_web_template", want="template",
                text="<p>$a $b</p>", values={"a": "x"})
        refuses("a placeholder left alone by safe_substitute that is not there",
                "py_web_template", want="safe", text="<p>$a</p>", values={"a": "x"})
        refuses("a lone dollar sign", "py_web_template", want="dollar",
                text="Cost: $$ and $ ", values={"amount": 5})
        refuses("braces that are not fields", "py_web_template", want="format",
                text="{} and {", args=["a"])
        refuses("a price that is not in quarters", "py_web_template", want="table",
                rows=[("tea", 3.3), ("cake", 12.25)])
        refuses("nothing to escape", "py_web_template", want="escape",
                items=["tea", "cake"])
        with self.assertRaises(ValueError):  # a double quote in a plain string
            emit_pyweb.solution("python", "py_web_url",
                                {"want": "quote", "text": 'a"b'})
        with self.assertRaises(KeyError):
            out("py_web_nothing", {})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("python"), _answer(e))
                self.assertIsNone(e.answer("javascript"))
        for shape in emit_pyweb.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        import tempfile

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
