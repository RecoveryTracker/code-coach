"""Web (Python): the library (`from web import app, ...`), the child driver and the sessions.

Every test talks to a real child process (`python -I -u -X utf8 driver.py serve`)
that serves a learner-style program on 127.0.0.1, over real HTTP, through the
same registry the Try it panel uses - or, for the checks, through
run_pyweb_check. Expected values are worked out by hand from the HTTP rules
(RFC 9110), Python's own tables (http.HTTPStatus) and the program text, never
from what the library printed. The content tests are in test_canvas_pywebapp.py.

The routes at the end call the route functions directly, with the real step
looked up in the (not yet registered) Web (Python) track.
"""

from __future__ import annotations

import base64
import http
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

from code_coach.canvas.pyharness.session import Unknown
from code_coach.canvas.pyweb import session as webses
from code_coach.canvas.pyweb.check import run_pyweb_check
from code_coach.canvas.pyweb.session import WebRegistry

KITCHEN = r'''
import threading
import time

from web import (Response, abort, app, escape, json_response, redirect, render, request, safe)

barrier = threading.Barrier(2, timeout=3)


@app.get("/")
def home():
    print("home was asked")
    return "home"


@app.get("/hello/<name>")
def hello(name):
    return f"hi {name}"


@app.get("/n/<int:id>")
def number(id):
    return f"{type(id).__name__}:{id}"


@app.get("/users/<name>")
def user(name):
    return "user " + name


@app.get("/users/me")
def me():
    return "me"


@app.get("/q")
def query():
    return {"args": request.args, "all": request.args_all, "path": request.path, "qs": request.query_string}


@app.get("/t-str")
def t_str():
    return "text"


@app.get("/t-dict")
def t_dict():
    return {"a": [1, 2], "b": None, "c": "é"}


@app.get("/t-list")
def t_list():
    return [1, "two"]


@app.get("/t-status")
def t_status():
    return "made", 201


@app.get("/t-headers")
def t_headers():
    return "plain", 202, {"X-Thing": "1", "Content-Type": "text/plain"}


@app.get("/t-resp")
def t_resp():
    r = Response("r", 203, {"X-A": "b"})
    r.headers["X-B"] = "c"
    return r


@app.get("/t-bytes")
def t_bytes():
    return b"\x00\xff"


@app.get("/t-none")
def t_none():
    pass


@app.get("/t-int")
def t_int():
    return 5


@app.get("/t-204")
def t_204():
    return "body", 204


@app.get("/t-jr")
def t_jr():
    return json_response({"a": 1}, 207, {"X-J": "1"})


@app.get("/t-badstatus")
def t_badstatus():
    return "x", "ok"


@app.get("/t-newline")
def t_newline():
    return "x", 200, {"X-Bad": "a\r\nSet-Cookie: pwned=1"}


@app.get("/boom")
def boom():
    return 1 / 0


@app.get("/abort/<int:code>")
def aborting(code):
    abort(code, "msg <b>")


@app.route("/m", methods=["GET", "POST"])
def multi():
    return request.method


@app.post("/only-post")
def only_post():
    return "posted"


@app.put("/put-it")
def put_it():
    return "put"


@app.delete("/delete-it")
def delete_it():
    return "deleted"


@app.get("/cookie-set")
def cookie_set():
    r = Response("set")
    r.set_cookie("a", "1", httponly=True, max_age=60, samesite="Lax")
    r.set_cookie("msg", "hello world; x")
    return r


@app.get("/cookie-del")
def cookie_del():
    r = Response("gone")
    r.delete_cookie("a")
    return r


@app.get("/cookie-read")
def cookie_read():
    return dict(request.cookies)


@app.get("/redir")
def redir():
    return redirect("/hello/there")


@app.get("/redir303")
def redir303():
    return redirect("/q?x=1&y=<2>", 303)


@app.get("/redir-bad")
def redir_bad():
    return redirect("/x", 200)


@app.post("/form")
def form():
    return dict(request.form)


@app.post("/json")
def js():
    return {"got": request.json}


@app.post("/echo-body")
def echo_body():
    return request.text, 200, {"X-Len": str(len(request.body))}


@app.get("/hdr")
def hdr():
    return {"lower": request.headers.get("x-custom"), "upper": request.headers["X-CUSTOM"],
            "missing": request.headers.get("nope", "dflt"), "has": "x-CUSTOM" in request.headers,
            "host": request.headers.get("Host")}


@app.get("/esc")
def esc():
    return render("<p>$v</p>", v=request.args.get("v", ""))


@app.get("/esc-safe")
def esc_safe():
    return render("<p>$v|$w|$$|${v}s</p>", v=safe("<b>"), w=escape("<i>&"))


@app.get("/esc-missing")
def esc_missing():
    return render("<p>$nope</p>", other=1)


@app.get("/esc-dollar")
def esc_dollar():
    return render("costs $5")


@app.get("/rendezvous/<who>")
def rendezvous(who):
    barrier.wait()
    return f"met {who}"


@app.get("/print")
def printing():
    print("one")
    print("two", 3)
    return "ok"


@app.get("/big")
def big():
    return "x" * 1_500_000


@app.get("/loop")
def loop():
    while True:
        pass


@app.get("/swallow")
def swallow():
    try:
        while True:
            pass
    except BaseException:
        while True:
            pass


@app.get("/no-request-outside")
def outside():
    return str(request.method)
'''

OK_CODE = 'from web import app\n\n\n@app.get("/")\ndef home():\n    return "ok"\n'


def line_of(code: str, text: str) -> int:
    """The 1-based line of the first line of `code` equal to `text` (hand-counted from the program)."""
    return code.splitlines().index(text) + 1


@pytest.fixture(scope="module")
def kitchen():
    registry = WebRegistry(handler_seconds=1.0)
    started = registry.start("s", KITCHEN)
    assert started["error"] is None, started
    yield registry, started["session"], started
    registry.close_all()


def ask(kitchen, method, path, headers=None, body=None):
    registry, sid, _ = kitchen
    return registry.request(sid, method, path, headers, body)


def head(got, name):
    """First value of a header in a request reply (case-insensitive), or None."""
    return next((v for k, v in got["headers"] if k.lower() == name.lower()), None)


def heads(got, name):
    return [v for k, v in got["headers"] if k.lower() == name.lower()]


def pid_alive(pid: int) -> bool:
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
    return str(pid) in out


def gone(pid: int, within: float = 5.0) -> bool:
    deadline = time.time() + within
    while time.time() < deadline:
        if not pid_alive(pid):
            return True
        time.sleep(0.05)
    return not pid_alive(pid)


# ---------------------------------------------------------------- routing


def test_a_route_answers_and_print_comes_back_as_logs(kitchen) -> None:
    got = ask(kitchen, "GET", "/")
    assert (got["status"], got["reason"], got["body"], got["error"]) == (200, "OK", "home", "")
    assert got["logs"] == ["home was asked"]
    assert head(got, "Content-Type") == "text/html; charset=utf-8"
    assert head(got, "Content-Length") == "4"


def test_the_start_reply_has_the_routes_in_the_order_written_and_the_host(kitchen) -> None:
    _, sid, started = kitchen
    assert sid and started["host"] == "127.0.0.1" and started["port"] > 0
    pairs = [(r["method"], r["path"]) for r in started["routes"]]
    assert pairs[:5] == [("GET", "/"), ("GET", "/hello/<name>"), ("GET", "/n/<int:id>"),
                         ("GET", "/users/<name>"), ("GET", "/users/me")]
    assert ("GET", "/m") in pairs and ("POST", "/m") in pairs  # one row per method


def test_a_path_parameter_is_decoded_and_a_trailing_slash_is_ignored(kitchen) -> None:
    assert ask(kitchen, "GET", "/hello/Ada")["body"] == "hi Ada"
    assert ask(kitchen, "GET", "/hello/Grace%20Hopper")["body"] == "hi Grace Hopper"
    # %2F is a slash inside one piece, not a new piece.
    assert ask(kitchen, "GET", "/hello/a%2Fb")["body"] == "hi a/b"
    assert ask(kitchen, "GET", "/hello/%C3%A9")["body"] == "hi é"
    assert ask(kitchen, "GET", "/hello/Ada/")["body"] == "hi Ada"
    assert ask(kitchen, "GET", "/hello/")["status"] == 404  # a hole is never empty
    assert ask(kitchen, "GET", "/hello/a/b")["status"] == 404  # and is one piece only


def test_int_parameters_are_ints_and_only_digits_match(kitchen) -> None:
    assert ask(kitchen, "GET", "/n/42")["body"] == "int:42"
    assert ask(kitchen, "GET", "/n/007")["body"] == "int:7"
    for bad in ("abc", "-3", "4.5", "", "99999999999999999999"):
        assert ask(kitchen, "GET", f"/n/{bad}")["status"] == 404, bad


def test_the_most_specific_route_wins(kitchen) -> None:
    # /users/<name> was written before /users/me, but a fixed word beats a hole.
    assert ask(kitchen, "GET", "/users/me")["body"] == "me"
    assert ask(kitchen, "GET", "/users/bob")["body"] == "user bob"


def test_the_query_string_is_parsed_two_ways(kitchen) -> None:
    got = ask(kitchen, "GET", "/q?a=1&a=2&b=&c=%20x&d=%C3%A9#frag")
    data = json.loads(got["body"])
    assert data["args"] == {"a": "1", "b": "", "c": " x", "d": "é"}
    assert data["all"] == {"a": ["1", "2"], "b": [""], "c": [" x"], "d": ["é"]}
    assert data["path"] == "/q" and data["qs"] == "a=1&a=2&b=&c=%20x&d=%C3%A9"
    assert json.loads(ask(kitchen, "GET", "/q")["body"])["args"] == {}


# ---------------------------------------------------------------- return values


def test_each_kind_of_return_value_becomes_the_right_response(kitchen) -> None:
    got = ask(kitchen, "GET", "/t-str")
    assert (got["status"], head(got, "Content-Type")) == (200, "text/html; charset=utf-8")

    got = ask(kitchen, "GET", "/t-dict")
    assert head(got, "Content-Type") == "application/json"
    assert json.loads(got["body"]) == {"a": [1, 2], "b": None, "c": "é"}

    got = ask(kitchen, "GET", "/t-list")
    assert head(got, "Content-Type") == "application/json" and json.loads(got["body"]) == [1, "two"]

    got = ask(kitchen, "GET", "/t-status")
    assert (got["status"], got["reason"], got["body"]) == (201, "Created", "made")

    got = ask(kitchen, "GET", "/t-headers")
    assert got["status"] == 202 and head(got, "X-Thing") == "1"
    assert head(got, "Content-Type") == "text/plain; charset=utf-8"  # text/* gets its charset

    got = ask(kitchen, "GET", "/t-resp")
    assert (got["status"], got["body"], head(got, "X-A"), head(got, "X-B")) == (203, "r", "b", "c")

    got = ask(kitchen, "GET", "/t-jr")
    assert (got["status"], head(got, "X-J"), head(got, "Content-Type")) == (207, "1", "application/json")
    assert json.loads(got["body"]) == {"a": 1}


def test_bytes_come_back_as_base64_with_the_binary_flag(kitchen) -> None:
    got = ask(kitchen, "GET", "/t-bytes")
    assert got["binary"] is True and got["body"] == "AP8="  # 00 ff -> 000000 001111 1100.. -> A P 8 =
    assert base64.b64decode(got["body"]) == b"\x00\xff"
    assert head(got, "Content-Type") == "application/octet-stream"
    assert ask(kitchen, "GET", "/t-str")["binary"] is False


def test_a_204_has_no_body_and_says_so_in_the_console(kitchen) -> None:
    got = ask(kitchen, "GET", "/t-204")
    assert (got["status"], got["body"]) == (204, "")
    assert head(got, "Content-Type") is None and head(got, "Content-Length") is None
    assert any("204" in line and "no body" in line for line in got["logs"])


def test_returning_none_or_a_number_or_a_bad_status_is_a_500_with_a_reason_in_the_console(kitchen) -> None:
    got = ask(kitchen, "GET", "/t-none")
    assert got["status"] == 500
    assert any("returned None" in line and "forget `return`" in line for line in got["logs"])
    got = ask(kitchen, "GET", "/t-int")
    assert got["status"] == 500 and any("returned a int" in line for line in got["logs"])
    got = ask(kitchen, "GET", "/t-badstatus")
    assert got["status"] == 500 and any("status has to be an int" in line for line in got["logs"])


def test_a_header_with_a_line_break_cannot_inject_another_header(kitchen) -> None:
    got = ask(kitchen, "GET", "/t-newline")
    assert got["status"] == 500
    assert heads(got, "Set-Cookie") == []
    assert any("line break" in line for line in got["logs"])


# ---------------------------------------------------------------- errors


def test_unknown_path_is_404_and_a_known_path_with_the_wrong_method_is_405_with_allow(kitchen) -> None:
    got = ask(kitchen, "GET", "/no/such/path")
    assert (got["status"], got["reason"]) == (404, "Not Found")
    assert "404 Not Found" in got["body"] and "/no/such/path" in got["body"]

    got = ask(kitchen, "POST", "/")
    assert (got["status"], got["reason"]) == (405, "Method Not Allowed")
    # GET also gives HEAD, and every known path allows OPTIONS: sorted, comma separated.
    assert head(got, "Allow") == "GET, HEAD, OPTIONS"
    assert "does not accept POST" in got["body"]

    got = ask(kitchen, "GET", "/only-post")
    assert got["status"] == 405 and head(got, "Allow") == "OPTIONS, POST"
    got = ask(kitchen, "DELETE", "/m")
    assert got["status"] == 405 and head(got, "Allow") == "GET, HEAD, OPTIONS, POST"
    assert ask(kitchen, "PUT", "/put-it")["body"] == "put"
    assert ask(kitchen, "DELETE", "/delete-it")["body"] == "deleted"
    assert ask(kitchen, "POST", "/m")["body"] == "POST" and ask(kitchen, "GET", "/m")["body"] == "GET"


def test_head_is_the_get_route_without_a_body_and_options_lists_the_methods(kitchen) -> None:
    get = ask(kitchen, "GET", "/hello/Ada")
    got = ask(kitchen, "HEAD", "/hello/Ada")
    assert got["status"] == 200 and got["body"] == ""
    assert head(got, "Content-Length") == head(get, "Content-Length") == str(len("hi Ada"))
    assert head(got, "Content-Type") == head(get, "Content-Type")
    # A path with no GET route has no HEAD either.
    assert ask(kitchen, "HEAD", "/only-post")["status"] == 405
    assert ask(kitchen, "HEAD", "/nowhere")["status"] == 404

    got = ask(kitchen, "OPTIONS", "/m")
    assert (got["status"], got["body"], head(got, "Allow")) == (204, "", "GET, HEAD, OPTIONS, POST")
    assert ask(kitchen, "OPTIONS", "/nowhere")["status"] == 404


def test_an_exception_is_a_500_and_the_traceback_with_the_learners_line_is_in_the_logs(kitchen) -> None:
    got = ask(kitchen, "GET", "/boom")
    assert (got["status"], got["reason"]) == (500, "Internal Server Error")
    assert "ZeroDivisionError" not in got["body"]  # the page is short; the console has the details
    line = line_of(KITCHEN, "    return 1 / 0")
    logs = got["logs"]
    assert logs[0] == "500 Internal Server Error: GET /boom"
    assert logs[1] == "Traceback (most recent call last):"
    assert logs[2] == f'  File "app.py", line {line}, in boom'
    assert logs[3].strip() == "return 1 / 0"  # the learner's own line of code
    assert logs[-1] == "ZeroDivisionError: division by zero"
    # The server carries on.
    assert ask(kitchen, "GET", "/hello/again")["body"] == "hi again"


def test_abort_answers_with_that_status_a_small_escaped_page_or_json(kitchen) -> None:
    got = ask(kitchen, "GET", "/abort/418")
    phrase = http.HTTPStatus(418).phrase
    assert got["status"] == 418 and got["reason"] == phrase
    assert f"<h1>418 {phrase}</h1>".replace("'", "'") in got["body"].replace("&#x27;", "'")
    assert "msg &lt;b&gt;" in got["body"] and "<b>" not in got["body"]  # the message is escaped
    got = ask(kitchen, "GET", "/abort/403", {"Accept": "application/json"})
    assert head(got, "Content-Type") == "application/json"
    assert json.loads(got["body"]) == {"error": "Forbidden", "status": 403, "message": "msg <b>"}
    # A browser asking for HTML as well gets the page.
    got = ask(kitchen, "GET", "/abort/403", {"Accept": "text/html,application/json"})
    assert head(got, "Content-Type").startswith("text/html")


def test_request_outside_a_route_says_so() -> None:
    code = ("from web import app, request\n\ntry:\n    request.method\nexcept RuntimeError as err:\n"
            "    print('caught', err)\n\n@app.get('/')\ndef home():\n    return 'ok'\n")
    registry = WebRegistry()
    try:
        got = registry.start("s", code)
        assert got["error"] is None
        assert got["logs"] == ["caught `request` only works inside a route, while a request is being answered."]
    finally:
        registry.close_all()


# ---------------------------------------------------------------- bodies, headers, cookies


def test_a_form_body_is_parsed_only_when_it_says_it_is_a_form(kitchen) -> None:
    form = {"Content-Type": "application/x-www-form-urlencoded"}
    got = ask(kitchen, "POST", "/form", form, "a=1&a=2&b=%20x&c=&d=%C3%A9&e=a+b")
    assert json.loads(got["body"]) == {"a": "1", "b": " x", "c": "", "d": "é", "e": "a b"}
    got = ask(kitchen, "POST", "/form", {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}, "z=9")
    assert json.loads(got["body"]) == {"z": "9"}
    assert json.loads(ask(kitchen, "POST", "/form", None, "a=1")["body"]) == {}
    assert json.loads(ask(kitchen, "POST", "/form", {"Content-Type": "text/plain"}, "a=1")["body"]) == {}


def test_a_json_body_is_parsed_none_when_absent_and_400_when_broken(kitchen) -> None:
    js = {"Content-Type": "application/json"}
    assert json.loads(ask(kitchen, "POST", "/json", js, '{"a": [1, {"b": null}]}')["body"]) == {"got": {"a": [1, {"b": None}]}}
    assert json.loads(ask(kitchen, "POST", "/json", js, "[1, 2]")["body"]) == {"got": [1, 2]}
    assert json.loads(ask(kitchen, "POST", "/json", {"Content-Type": "application/vnd.x+json"}, "7")["body"]) == {"got": 7}
    assert json.loads(ask(kitchen, "POST", "/json", js, "")["body"]) == {"got": None}  # no body, no JSON
    assert json.loads(ask(kitchen, "POST", "/json", None, '{"a": 1}')["body"]) == {"got": None}  # not labelled JSON
    assert json.loads(ask(kitchen, "POST", "/json", {"Content-Type": "text/plain"}, "{}")["body"]) == {"got": None}
    got = ask(kitchen, "POST", "/json", js, "{oops")
    assert got["status"] == 400 and "not valid JSON" in got["body"]
    # The library answered; the route never crashed, so nothing was printed.
    assert got["logs"] == []


def test_the_body_arrives_whole_and_the_size_limit_is_enforced(kitchen) -> None:
    text = "héllo " * 200
    got = ask(kitchen, "POST", "/echo-body", None, text)
    assert got["body"] == text and head(got, "X-Len") == str(len(text.encode("utf-8")))
    too_big = ask(kitchen, "POST", "/echo-body", None, "x" * 1_000_001)
    assert too_big["status"] == 0 and "over 1 MB" in too_big["error"]


def test_a_big_answer_is_cut_at_one_megabyte(kitchen) -> None:
    got = ask(kitchen, "GET", "/big")
    assert got["status"] == 200 and got["truncated"] is True and len(got["body"]) == 1_000_000
    assert ask(kitchen, "GET", "/hello/x")["truncated"] is False


def test_request_headers_are_case_insensitive_and_the_host_is_not_ours_to_change(kitchen) -> None:
    _, _, started = kitchen
    data = json.loads(ask(kitchen, "GET", "/hdr", {"X-Custom": "v", "Host": "evil.example"})["body"])
    assert data["lower"] == "v" and data["upper"] == "v" and data["has"] is True
    assert data["missing"] == "dflt"
    assert data["host"] == f"127.0.0.1:{started['port']}"  # a Host header from the page is dropped


def test_cookies_are_set_with_their_options_and_read_back(kitchen) -> None:
    got = ask(kitchen, "GET", "/cookie-set")
    cookies = heads(got, "Set-Cookie")
    assert len(cookies) == 2  # two headers, never joined
    first = {part.strip() for part in cookies[0].split(";")}
    assert first == {"a=1", "HttpOnly", "Max-Age=60", "Path=/", "SameSite=Lax"}
    # The value has a space and a semicolon: it is quoted, with the semicolon written as octal 073.
    assert cookies[1].startswith('msg="hello world\\073 x"')
    got = ask(kitchen, "GET", "/cookie-del")
    assert {p.strip() for p in heads(got, "Set-Cookie")[0].split(";")} == {'a=""', "Max-Age=0", "Path=/"}  # an empty value is written as two quotes

    # What a browser sends back. The first of a repeated name wins.
    got = ask(kitchen, "GET", "/cookie-read", {"Cookie": 'a=1; b=two; a=9; msg="hello world\\073 x"; =no; junk'})
    assert json.loads(got["body"]) == {"a": "1", "b": "two", "msg": "hello world; x"}
    assert json.loads(ask(kitchen, "GET", "/cookie-read")["body"]) == {}


def test_redirect_defaults_to_302_is_never_followed_and_escapes_its_page(kitchen) -> None:
    got = ask(kitchen, "GET", "/redir")
    assert (got["status"], got["reason"], head(got, "Location")) == (302, "Found", "/hello/there")
    assert 'href="/hello/there"' in got["body"]
    got = ask(kitchen, "GET", "/redir303")
    assert (got["status"], got["reason"], head(got, "Location")) == (303, "See Other", "/q?x=1&y=<2>")
    assert 'href="/q?x=1&amp;y=&lt;2&gt;"' in got["body"]
    got = ask(kitchen, "GET", "/redir-bad")
    assert got["status"] == 500 and any("the code must be one of" in line for line in got["logs"])


def test_render_escapes_values_unless_they_are_safe(kitchen) -> None:
    got = ask(kitchen, "GET", "/esc?v=%3Cscript%3Ealert(1)%3C/script%3E")
    assert got["body"] == "<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>"
    got = ask(kitchen, "GET", "/esc?v=%22a%27b%22%20%26")
    assert got["body"] == "<p>&quot;a&#x27;b&quot; &amp;</p>"
    # safe() is left alone, escape() output is not escaped twice, $$ is a dollar, ${v} touches text.
    assert ask(kitchen, "GET", "/esc-safe")["body"] == "<p><b>|&lt;i&gt;&amp;|$|<b>s</p>"
    got = ask(kitchen, "GET", "/esc-missing")
    assert got["status"] == 500
    assert any("the template uses $nope but no value called 'nope' was given" in line for line in got["logs"])
    got = ask(kitchen, "GET", "/esc-dollar")
    assert got["status"] == 500 and any("a literal dollar sign in a template is written $$" in line for line in got["logs"])


def test_two_requests_are_served_at_the_same_time(kitchen) -> None:
    # Each route waits at a barrier for the other one: served one after the other, the first would
    # time out (3 s) and fail. Served together, both pass.
    from concurrent.futures import ThreadPoolExecutor

    registry, sid, _ = kitchen
    started = time.time()
    with ThreadPoolExecutor(2) as pool:
        a = pool.submit(registry.request, sid, "GET", "/rendezvous/ann")
        b = pool.submit(registry.request, sid, "GET", "/rendezvous/ben")
        got = a.result(timeout=10), b.result(timeout=10)
    assert [g["body"] for g in got] == ["met ann", "met ben"]
    assert time.time() - started < 2.5


def test_print_inside_a_route_comes_back_with_that_request_only(kitchen) -> None:
    got = ask(kitchen, "GET", "/print")
    assert got["logs"] == ["one", "two 3"]
    assert ask(kitchen, "GET", "/hello/x")["logs"] == []


# ---------------------------------------------------------------- loading the program


def start_once(code: str, **kwargs):
    registry = WebRegistry(**kwargs)
    try:
        return registry.start("s", code), registry
    finally:
        registry.close_all()


def test_a_program_that_cannot_load_has_no_session_and_its_error_has_the_learners_line() -> None:
    got, registry = start_once("from web import app\n\nx = 1\ny = x / 0\n")
    assert got["session"] == "" and len(registry) == 0
    assert got["error"] == {"message": "ZeroDivisionError: division by zero", "line": 4}
    got, _ = start_once("from web import app\n\n@app.get('/'\ndef f():\n    return 1\n")
    assert got["session"] == "" and "SyntaxError" in got["error"]["message"] and got["error"]["line"] in (3, 4)
    got, _ = start_once("import nonexistent_module_xyz\n")
    assert "ModuleNotFoundError" in got["error"]["message"] and got["error"]["line"] == 1


def test_two_routes_for_one_path_and_method_are_refused_when_the_program_loads() -> None:
    code = ('from web import app\n\n\n@app.get("/x")\ndef one():\n    return "1"\n\n\n'
            '@app.get("/x")\ndef two():\n    return "2"\n')
    got, _ = start_once(code)
    assert got["session"] == ""
    assert got["error"]["message"] == "ValueError: GET /x is already a route (`one`): the second one, `two`, could never run"
    assert got["error"]["line"] == 9
    # Different methods, or a different hole name, are fine / are the same route.
    ok = ('from web import app\n\n\n@app.get("/x")\ndef one():\n    return "1"\n\n\n'
          '@app.post("/x")\ndef two():\n    return "2"\n')
    assert start_once(ok)[0]["error"] is None
    holes = ('from web import app\n\n\n@app.get("/x/<a>")\ndef one(a):\n    return "1"\n\n\n'
             '@app.get("/x/<b>")\ndef two(b):\n    return "2"\n')
    assert "could never run" in start_once(holes)[0]["error"]["message"]


def test_a_function_that_does_not_fit_its_route_says_which_parameter() -> None:
    got, _ = start_once('from web import app\n\n\n@app.get("/hello/<name>")\ndef hello():\n    return "x"\n')
    assert got["error"]["message"] == (
        "TypeError: the route '/hello/<name>' passes `name` to hello(), but hello() has no parameter called `name`")
    got, _ = start_once('from web import app\n\n\n@app.get("/hello")\ndef hello(name):\n    return "x"\n')
    assert got["error"]["message"] == "TypeError: hello() needs `name`, but the route '/hello' has no <name> in it"
    got, _ = start_once('from web import app\n\n\n@app.get("hello")\ndef hello():\n    return "x"\n')
    assert "must be a string starting with '/'" in got["error"]["message"]
    got, _ = start_once('from web import app\n\n\n@app.get("/a<b>")\ndef hello(b):\n    return "x"\n')
    assert "filling a whole /segment/" in got["error"]["message"]


def test_app_run_is_a_harmless_note_and_a_program_with_no_routes_is_told() -> None:
    code = ('from web import app\n\n\n@app.get("/")\ndef home():\n    return "x"\n\n\n'
            'if __name__ == "__main__":\n    app.run(debug=True)\n')
    registry = WebRegistry()
    try:
        got = registry.start("s", code)
        assert got["error"] is None
        assert got["logs"] == ["app.run() is not needed here - Code Coach starts your app itself."]
        empty = registry.start("s", "from web import app\n")
        assert empty["error"] is None and empty["routes"] == []
        assert empty["logs"] == ['Your app has no routes yet. Add one: @app.get("/") above a function that returns the page.']
        assert registry.request(empty["session"], "GET", "/")["status"] == 404
    finally:
        registry.close_all()


def test_input_exit_and_an_endless_loop_at_the_top_are_reported() -> None:
    got, _ = start_once("name = input('who? ')\n")
    assert "input() cannot be used in a web app" in got["error"]["message"] and got["error"]["line"] == 1
    got, _ = start_once("import sys\nsys.exit(0)\n")
    assert "called exit()" in got["error"]["message"] and got["error"]["line"] == 2
    started = time.time()
    got, _ = start_once("while True:\n    pass\n", handler_seconds=0.5)
    assert "loop that never ends" in got["error"]["message"] and got["error"]["line"] in (1, 2)
    assert time.time() - started < 6


def test_the_program_runs_in_an_empty_folder_with_a_bare_environment() -> None:
    os.environ["CC_TEST_SECRET"] = "hunter2"
    try:
        code = ("import os\nfrom web import app\n\n\n@app.get('/')\ndef home():\n"
                "    return {'files': os.listdir('.'), 'leak': 'CC_TEST_SECRET' in os.environ, 'cwd': os.getcwd()}\n")
        registry = WebRegistry()
        try:
            sid = registry.start("s", code)["session"]
            data = json.loads(registry.request(sid, "GET", "/")["body"])
            assert data["files"] == [] and data["leak"] is False
            assert os.path.basename(data["cwd"]) == "work"
            assert os.path.basename(os.path.dirname(data["cwd"])).startswith("cc-pyweb-")
        finally:
            registry.close_all()
    finally:
        del os.environ["CC_TEST_SECRET"]


# ---------------------------------------------------------------- limits on a route


def test_an_endless_loop_in_a_route_is_a_500_the_server_survives() -> None:
    registry = WebRegistry(handler_seconds=0.5)
    try:
        sid = registry.start("s", KITCHEN)["session"]
        started = time.time()
        got = registry.request(sid, "GET", "/loop")
        assert got["status"] == 500
        assert any("ran out of time" in line and "never ends" in line for line in got["logs"])
        assert time.time() - started < 4
        assert registry.request(sid, "GET", "/hello/after")["body"] == "hi after"
    finally:
        registry.close_all()


def test_a_route_that_swallows_the_stop_ends_the_process_and_says_it_ran_out_of_time() -> None:
    registry = WebRegistry(handler_seconds=0.5)
    try:
        sid = registry.start("s", KITCHEN)["session"]
        pid = registry._sessions[sid].pid
        started = time.time()
        got = registry.request(sid, "GET", "/swallow")
        assert got["status"] == 0 and "loop that never ends" in got["error"]
        assert time.time() - started < 6  # the limit, the driver's grace, some slack
        assert gone(pid)
        # The session stays as a tomb, answering with the same reason until it is stopped.
        again = registry.request(sid, "GET", "/")
        assert again["status"] == 0 and again["error"] == got["error"]
        registry.stop(sid)
    finally:
        registry.close_all()


def test_a_child_that_dies_is_reported_with_its_stderr() -> None:
    code = ("import os\nfrom web import app\n\n\n@app.get('/die')\ndef die():\n    os._exit(7)\n\n\n"
            "@app.get('/')\ndef home():\n    return 'x'\n")
    registry = WebRegistry()
    try:
        sid = registry.start("s", code)["session"]
        pid = registry._sessions[sid].pid
        got = registry.request(sid, "GET", "/die")
        assert got["status"] == 0 and got["error"].startswith("The program stopped unexpectedly")
        assert gone(pid)
    finally:
        registry.close_all()


# ---------------------------------------------------------------- the server's address


def test_the_server_listens_on_127_0_0_1_only(kitchen) -> None:
    _, _, started = kitchen
    assert started["host"] == "127.0.0.1"
    port = started["port"]
    with socket.create_connection(("127.0.0.1", port), timeout=3):
        pass
    # Any other address of this machine must refuse the connection.
    others = {info[4][0] for info in socket.getaddrinfo(socket.gethostname(), port, socket.AF_INET)}
    others.discard("127.0.0.1")
    if not others:
        pytest.skip("this machine has no address other than loopback to try")
    for address in others:
        with pytest.raises(OSError):
            socket.create_connection((address, port), timeout=2).close()


def test_a_second_copy_of_the_library_binds_loopback_on_a_free_port() -> None:
    lib = Path(webses.__file__).parent / "lib"
    code = ("import sys; sys.path.insert(0, sys.argv[1]); import web; s = web.make_server(); "
            "print(s.server_address[0], s.server_address[1] > 0); s.server_close()")
    out = subprocess.run([sys.executable, "-I", "-c", code, str(lib)], capture_output=True, text=True, timeout=30)
    assert out.stdout.split() == ["127.0.0.1", "True"], out.stderr


# ---------------------------------------------------------------- errorhandler


ERRORS = r'''
from web import abort, app, request


@app.errorhandler(404)
def missing(error):
    return f"nothing at {request.path} ({error.status} {error.message})", 404


@app.errorhandler(418)
def teapot():
    return "short and stout", 418


@app.errorhandler(500)
def broken(error):
    return "oops page", 500


@app.errorhandler(403)
def forbidden(error):
    return "no entry"


@app.get("/")
def home():
    return "home"


@app.get("/tea")
def tea():
    abort(418)


@app.get("/deny")
def deny():
    abort(403, "members only")


@app.get("/boom")
def boom():
    raise ValueError("bad")


@app.post("/p")
def p():
    return "p"
'''


def test_errorhandlers_take_over_a_status_and_a_page_is_200_unless_it_says_otherwise() -> None:
    registry = WebRegistry()
    try:
        sid = registry.start("s", ERRORS)["session"]
        got = registry.request(sid, "GET", "/gone")
        assert got["status"] == 404 and got["body"] == "nothing at /gone (404 Nothing is routed at /gone.)"
        got = registry.request(sid, "GET", "/tea")  # a handler that takes no error is called without one
        assert (got["status"], got["body"]) == (418, "short and stout")
        # Returned without a status: the page is a 200 (as in Flask) - the learner must write (page, 403).
        got = registry.request(sid, "GET", "/deny")
        assert (got["status"], got["body"]) == (200, "no entry")
        got = registry.request(sid, "GET", "/boom")
        assert (got["status"], got["body"]) == (500, "oops page")
        assert got["logs"][-1] == "ValueError: bad"
        # 405 keeps its Allow header even when a handler (here: none for 405) or the default answers.
        got = registry.request(sid, "GET", "/p")
        assert got["status"] == 405 and any(k == "Allow" for k, _ in got["headers"])
    finally:
        registry.close_all()


def test_an_errorhandler_that_crashes_falls_back_to_the_plain_page_and_logs_it() -> None:
    code = ('from web import app\n\n\n@app.errorhandler(404)\ndef missing(error):\n    return 1 / 0\n')
    registry = WebRegistry()
    try:
        sid = registry.start("s", code)["session"]
        got = registry.request(sid, "GET", "/x")
        assert got["status"] == 404 and "404 Not Found" in got["body"]
        assert got["logs"][0] == "500 Internal Server Error: GET /x (the errorhandler for 404 failed)"
        assert got["logs"][-1] == "ZeroDivisionError: division by zero"
    finally:
        registry.close_all()


# ---------------------------------------------------------------- sessions


def test_stop_ends_the_process_and_deletes_the_folder() -> None:
    registry = WebRegistry()
    sid = registry.start("s", OK_CODE)["session"]
    session = registry._sessions[sid]
    pid, folder = session.pid, session._dir
    assert pid_alive(pid) and folder.exists()
    assert registry.request(sid, "GET", "/")["body"] == "ok"
    registry.stop(sid)
    assert gone(pid) and not folder.exists()
    with pytest.raises(Unknown):
        registry.request(sid, "GET", "/")
    with pytest.raises(Unknown):
        registry.stop(sid)


def test_idle_sessions_are_reaped_on_an_injected_clock() -> None:
    now = [1000.0]
    registry = WebRegistry(idle_seconds=60, clock=lambda: now[0])
    try:
        quiet = registry.start("s", OK_CODE)["session"]
        busy = registry.start("s", OK_CODE)["session"]
        pids = [registry._sessions[quiet].pid, registry._sessions[busy].pid]
        now[0] += 45
        registry.request(busy, "GET", "/")  # used: its idle clock starts again
        now[0] += 30  # quiet: 75 s idle; busy: 30 s
        assert registry.reap() == [quiet]
        assert registry.ids() == [busy]
        assert gone(pids[0]) and pid_alive(pids[1])
        with pytest.raises(Unknown):
            registry.request(quiet, "GET", "/")
        now[0] += 61
        with pytest.raises(Unknown):
            registry.request(busy, "GET", "/")  # asking reaps first: it was idle too long
        assert gone(pids[1]) and len(registry) == 0
    finally:
        registry.close_all()


def test_the_default_idle_time_is_two_minutes_and_at_most_four_sessions_run() -> None:
    assert webses.IDLE_SECONDS == 120 and webses.MAX_SESSIONS == 4
    assert webses.REGISTRY.idle_seconds == 120 and webses.REGISTRY.max_sessions == 4


def test_the_least_recently_used_session_is_evicted_when_there_are_too_many() -> None:
    now = [0.0]
    registry = WebRegistry(max_sessions=2, clock=lambda: now[0])
    try:
        a = registry.start("s", OK_CODE)["session"]
        now[0] += 1
        b = registry.start("s", OK_CODE)["session"]
        now[0] += 1
        registry.request(a, "GET", "/")  # a was used more recently than b
        now[0] += 1
        pid_a, pid_b = registry._sessions[a].pid, registry._sessions[b].pid
        c = registry.start("s", OK_CODE)["session"]
        assert sorted(registry.ids()) == sorted([a, c])
        assert gone(pid_b) and pid_alive(pid_a)
        with pytest.raises(Unknown):
            registry.request(b, "GET", "/")
    finally:
        registry.close_all()


def test_close_all_leaves_no_process_or_folder_behind() -> None:
    registry = WebRegistry()
    ids = [registry.start("s", OK_CODE)["session"] for _ in range(3)]
    pids = [registry._sessions[i].pid for i in ids]
    folders = [registry._sessions[i]._dir for i in ids]
    registry.close_all()
    assert all(gone(p) for p in pids)
    assert not any(f.exists() for f in folders)
    assert len(registry) == 0


def test_a_failed_start_frees_its_slot_and_its_process() -> None:
    registry = WebRegistry(max_sessions=2)
    try:
        good = registry.start("s", OK_CODE)["session"]
        bad = registry.start("s", "x = 1 / 0\n")
        assert bad["session"] == "" and bad["error"]["line"] == 1
        # The failed one was never kept, so it did not push the good one out.
        assert registry.ids() == [good]
    finally:
        registry.close_all()


def test_folders_a_killed_server_left_behind_are_swept_but_recent_ones_are_not() -> None:
    import tempfile

    old = Path(tempfile.mkdtemp(prefix="cc-pyweb-"))
    fresh = Path(tempfile.mkdtemp(prefix="cc-pyweb-"))
    other = Path(tempfile.mkdtemp(prefix="not-ours-"))
    canvas = Path(tempfile.mkdtemp(prefix="cc-pycanvas-"))
    try:
        two_hours_ago = time.time() - 7200
        for folder in (old, other, canvas):
            os.utime(folder, (two_hours_ago, two_hours_ago))
        swept = webses.sweep_stale()
        assert old.name in swept and not old.exists()
        assert fresh.exists() and other.exists() and canvas.exists()  # not ours / too new
        assert all(name.startswith("cc-pyweb-") for name in swept)
    finally:
        for folder in (old, fresh, other, canvas):
            webses.remove_folder(folder)


def test_a_child_whose_server_is_gone_ends_by_itself() -> None:
    proc = subprocess.Popen(
        webses.child_command("serve"), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        env=webses.child_env(), creationflags=webses.child_flags(),
    )
    proc.stdin.write((json.dumps({"op": "start", "code": OK_CODE}) + "\n").encode())
    proc.stdin.flush()
    line = proc.stdout.readline()
    assert line.startswith(b"\x1ePW")
    assert json.loads(line[3:])["host"] == "127.0.0.1"
    proc.stdin.close()  # what the child sees when the server dies
    assert proc.wait(timeout=10) == 0


def test_stray_output_cannot_pose_as_an_answer() -> None:
    code = ('import os\nfrom web import app\n\nos.write(1, b\'{"error": null, "port": 1, "host": "x", "routes": []}\\n\')\n\n\n'
            '@app.get("/")\ndef home():\n    return "ok"\n')
    registry = WebRegistry()
    try:
        got = registry.start("s", code)
        assert got["error"] is None and got["host"] == "127.0.0.1" and got["port"] != 1
        assert registry.request(got["session"], "GET", "/")["body"] == "ok"
    finally:
        registry.close_all()


def test_the_child_command_is_the_isolated_python_that_runs_the_driver() -> None:
    cmd = webses.child_command("serve")
    assert cmd[:5] == [sys.executable, "-I", "-u", "-X", "utf8"] and cmd[5].endswith("driver.py")
    # Only the learner's library is on the path, not this project.
    out = subprocess.run(
        [sys.executable, "-I", "-c", "import sys; sys.path.insert(0, sys.argv[1]); import web; print(web.HOST)",
         str(Path(webses.__file__).parent / "lib")], capture_output=True, text=True, timeout=30)
    assert out.stdout.strip() == "127.0.0.1"


def test_a_request_to_a_session_with_a_bad_header_or_method_is_an_error_not_a_crash() -> None:
    registry = WebRegistry()
    try:
        sid = registry.start("s", OK_CODE)["session"]
        got = registry.request(sid, "GET", "/", {"Bad:Header": "x"})
        assert got["status"] == 0 and "could not be sent" in got["error"]
        got = registry.request(sid, "GET", "/", {"X-A": "line\nbreak"})
        assert got["status"] == 0 and "could not be sent" in got["error"]
        assert registry.request(sid, "GET", "/")["body"] == "ok"  # the app is fine
    finally:
        registry.close_all()


# ---------------------------------------------------------------- checks (run_pyweb_check)


CHECK_APP = r'''
from web import Response, app, redirect, request


@app.get("/")
def home():
    print("a log line")
    return "home"


@app.post("/login")
def login():
    r = redirect("/me", 303)
    r.set_cookie("session", "tok", httponly=True)
    return r


@app.get("/me")
def me():
    return "me:" + request.cookies.get("session", "none")


@app.get("/boom")
def boom():
    return 1 / 0


@app.get("/api")
def api():
    return {"a": 1}
'''


def run(check: str, code: str = CHECK_APP):
    return run_pyweb_check(code, check)


def test_a_check_that_holds_passes_and_one_that_does_not_says_what_the_request_was() -> None:
    assert run('r = cc.get("/")\nr.expect_status(200)\nexpect(r.text == "home", "x")\n').passed
    got = run('cc.get("/nope").expect_status(200)\n')
    assert not got.passed
    assert got.message.startswith("GET /nope returned 404 Not Found, expected 200.")
    got = run('cc.post("/", form={"a": "1"}).expect_status(200)\n')
    assert got.message.startswith("POST / returned 405 Method Not Allowed, expected 200.")
    assert "only allows GET, HEAD, OPTIONS" in got.message
    got = run('cc.get("/boom").expect_status(200)\n')
    assert got.message == ("GET /boom returned 500 Internal Server Error, expected 200. "
                           "Your app crashed on it (ZeroDivisionError: division by zero).")
    got = run('cc.get("/").expect_status(200, 201, 202)\ncc.get("/nope").expect_status(200, 201)\n')
    assert "expected 200 or 201" in got.message


def test_the_response_object_has_everything_a_check_needs() -> None:
    check = '''
r = cc.get("/api")
expect(r.status == 200 and r.reason == "OK" and r.ok, "status")
expect(r.headers.get("content-type") == "application/json" and r.headers["Content-Type"] == "application/json", "headers")
expect(r.content_type == "application/json" and r.json() == {"a": 1} and r.expect_json() == {"a": 1}, "json")
expect(r.text == '{"a": 1}' and r.body == b'{"a": 1}' and r.location is None, "body")
expect(r.snippet() == "'{\\"a\\": 1}'" or r.snippet() == repr('{"a": 1}'), "snippet")
r = cc.get("/")
try:
    r.json()
except Exception as err:
    expect("should answer with JSON" in str(err) and "text/html" in str(err), str(err))
else:
    expect(False, "json() on a page should fail")
r.expect_type("text/html")
'''
    got = run(check)
    assert got.passed, got.message


def test_cookies_the_jar_and_following_a_redirect() -> None:
    check = '''
r = cc.post("/login", form={"a": "1"})
expect(r.status == 303 and r.location == "/me", "redirect")
expect(r.cookies == {"session": "tok"} and r.cookie("session")["httponly"] is True, "cookie")
expect(r.cookie("session")["path"] == "/" and r.cookie("nope") is None, "attrs")
# The jar is off: nothing is kept or sent.
expect(cc.cookies == {} and cc.get("/me").text == "me:none", "jar off")
cc.jar = True
r = cc.post("/login")
expect(cc.cookies == {"session": "tok"}, "kept")
page = cc.follow(r)
expect(page.status == 200 and page.text == "me:tok", "follow sent the cookie: " + page.text)
cc.cookies.clear()
expect(cc.get("/me").text == "me:none", "cleared")
cc.jar = False
expect(cc.get("/me", cookies={"session": "x y"}).text == "me:x y", "explicit cookie")
expect(cc.get("/me", headers={"cookie": "session=hdr"}).text == "me:hdr", "explicit header")
'''
    got = run(check)
    assert got.passed, got.message


def test_follow_takes_one_hop_the_way_a_browser_does() -> None:
    code = r'''
from web import Response, app, redirect, request


@app.post("/p303")
def p303():
    return redirect("/landed", 303)


@app.post("/p302")
def p302():
    return redirect("/landed", 302)


@app.post("/p307")
def p307():
    return redirect("/landed", 307)


@app.route("/landed", methods=["GET", "POST"])
def landed():
    return f"{request.method}:{request.text}"


@app.get("/g302")
def g302():
    return redirect("/landed", 302)


@app.get("/away")
def away():
    return redirect("http://example.com/x", 302)


@app.get("/rel")
def rel():
    return redirect("landed?x=1", 302)
'''
    check = '''
expect(cc.follow(cc.post("/p303", body="data")).text == "GET:", "303 makes it a GET and drops the body")
expect(cc.follow(cc.post("/p302", body="data")).text == "GET:", "302 after a POST becomes a GET, as in browsers")
expect(cc.follow(cc.post("/p307", body="data")).text == "POST:data", "307 keeps method and body")
expect(cc.follow(cc.get("/g302")).text == "GET:", "302 after a GET stays a GET")
expect(cc.follow(cc.get("/rel")).text == "GET:", "a relative Location is resolved against the path")
for bad, word in (("/landed", "not a redirect"), ("/away", "not this app")):
    try:
        cc.follow(cc.get(bad))
    except Exception as err:
        expect(word in str(err), str(err))
    else:
        expect(False, bad + " should not be followable")
'''
    got = run(check, code)
    assert got.passed, got.message


def test_logs_can_be_read_by_a_check_and_the_load_error_comes_first() -> None:
    check = 'cc.get("/")\ncc.get("/boom")\nlogs = cc.logs()\nexpect(logs[0] == "a log line", logs)\nexpect(logs[-1] == "ZeroDivisionError: division by zero", logs)\n'
    got = run(check)
    assert got.passed, got.message
    got = run("pass\n", "x = 1\ny = x / 0\n")
    assert not got.passed and got.message == "Your code threw on line 2: ZeroDivisionError: division by zero"
    got = run("pass\n", "while True:\n    pass\n")
    assert not got.passed and "loop that never ends" in got.message


def test_a_check_cannot_be_fooled_by_a_program_that_patches_http() -> None:
    code = ("import http.client\nfrom web import app\n\nhttp.client.HTTPConnection = None\n\n\n"
            '@app.get("/")\ndef home():\n    return "fine"\n')
    got = run('expect(cc.get("/").text == "fine", "x")\n', code)
    assert got.passed, got.message


def test_a_check_that_is_broken_says_where_and_one_that_never_ends_is_stopped() -> None:
    got = run("x = 1\ncc.nope()\n")
    assert not got.passed and got.message.startswith("The check could not run: AttributeError")
    assert "(check line 2)" in got.message
    started = time.time()
    got = run_pyweb_check(CHECK_APP, "while True:\n    pass\n", timeout=3)
    assert not got.passed and "ran out of time" in got.message and time.time() - started < 10


def test_a_check_that_asks_for_a_route_that_hangs_does_not_hang_the_check() -> None:
    code = ('import time\nfrom web import app\n\n\n@app.get("/")\ndef home():\n    while True:\n        pass\n')
    started = time.time()
    got = run('r = cc.get("/")\nr.expect_status(200)\n', code)
    assert not got.passed and "500" in got.message
    assert time.time() - started < 12


def test_more_than_one_way_to_give_a_body_is_a_mistake_in_the_check() -> None:
    got = run('cc.post("/", form={"a": 1}, json={"b": 2})\n')
    assert not got.passed and "more than one of form, json and body" in got.message


# ---------------------------------------------------------------- the routes


@pytest.fixture()
def web_routes(monkeypatch):
    """The route functions, with the Web (Python) track findable (it is not registered in canvas/__init__.py)."""
    import code_coach.canvas as canvas
    from code_coach.canvas.content_pyweb_track import PYWEBAPP_STEPS

    real = canvas.step
    mine = {s.id: s for s in PYWEBAPP_STEPS}
    monkeypatch.setattr(canvas, "step", lambda step_id: mine.get(step_id) or real(step_id))
    yield mine
    webses.REGISTRY.close_all()


def test_routes_start_request_stop(web_routes) -> None:
    from code_coach.api.schemas import PyWebRequestRequest, PyWebStartRequest, PyWebStopRequest
    from code_coach.api.server import pyweb_request, pyweb_start, pyweb_stop

    step = web_routes["pywa-09-redirect"]
    first = pyweb_start(PyWebStartRequest(step_id=step.id, code=step.solution))
    sid = first["session"]
    assert sid and first["error"] is None and first["host"] == "127.0.0.1"
    assert ("POST", "/add") in [(r["method"], r["path"]) for r in first["routes"]]

    got = pyweb_request(PyWebRequestRequest(session=sid, method="GET", path="/"))
    assert got["status"] == 200 and got["body"] == "Link Saver" and got["error"] == ""
    # A form post is answered with the redirect itself - not followed.
    got = pyweb_request(PyWebRequestRequest(
        session=sid, method="POST", path="/add",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body="title=Flask+docs&url=https%3A%2F%2Fflask.palletsprojects.com%2F"))
    assert got["status"] == 303 and head(got, "Location") == "/bookmarks"
    got = pyweb_request(PyWebRequestRequest(session=sid, method="GET", path="/api/bookmarks"))
    titles = [b["title"] for b in json.loads(got["body"])]
    assert titles == ["Python docs", "MDN", "PyPI", "Fish & <chips>", "Flask docs"]
    assert pyweb_stop(PyWebStopRequest(session=sid)) == {"ok": True}
    assert len(webses.REGISTRY) == 0


def test_a_program_that_fails_to_start_comes_back_with_its_error_and_no_session(web_routes) -> None:
    from code_coach.api.schemas import PyWebStartRequest
    from code_coach.api.server import pyweb_start

    got = pyweb_start(PyWebStartRequest(step_id="pywa-01-hello", code="from web import app\nboom()\n"))
    assert got["session"] == "" and got["error"]["line"] == 2 and "NameError" in got["error"]["message"]
    assert len(webses.REGISTRY) == 0


def test_routes_say_404_for_a_session_that_is_not_there(web_routes) -> None:
    from fastapi import HTTPException

    from code_coach.api.schemas import PyWebRequestRequest, PyWebStopRequest
    from code_coach.api.server import pyweb_request, pyweb_stop

    with pytest.raises(HTTPException) as err:
        pyweb_request(PyWebRequestRequest(session="nope"))
    assert err.value.status_code == 404 and "No web session" in err.value.detail and "Press Run" in err.value.detail
    with pytest.raises(HTTPException) as err:
        pyweb_stop(PyWebStopRequest(session="nope"))
    assert err.value.status_code == 404


def test_start_refuses_an_unknown_step_and_a_step_that_is_not_a_web_one(web_routes) -> None:
    from fastapi import HTTPException

    from code_coach.api.schemas import PyWebStartRequest
    from code_coach.api.server import pyweb_start

    with pytest.raises(HTTPException) as err:
        pyweb_start(PyWebStartRequest(step_id="no-such-step", code="x = 1"))
    assert err.value.status_code == 404
    for not_web in ("pydodge-01-square", "dodge-01-square"):
        with pytest.raises(HTTPException) as err:
            pyweb_start(PyWebStartRequest(step_id=not_web, code="x = 1"))
        assert err.value.status_code == 400 and "not a web step" in err.value.detail
    assert len(webses.REGISTRY) == 0


def test_a_request_path_must_start_with_a_slash(web_routes) -> None:
    from fastapi import HTTPException

    from code_coach.api.schemas import PyWebRequestRequest
    from code_coach.api.server import pyweb_request

    with pytest.raises(HTTPException) as err:
        pyweb_request(PyWebRequestRequest(session="x", path="http://evil.example/"))
    assert err.value.status_code == 400


def test_the_request_is_bounded() -> None:
    from pydantic import ValidationError

    from code_coach.api.schemas import PyWebRequestRequest, PyWebStartRequest

    for bad in ({"method": "TRACE"}, {"method": "get"}, {"path": "/" + "a" * 2000},
                {"headers": {f"h{i}": "v" for i in range(31)}}, {"body": "x" * 1_000_001}):
        with pytest.raises(ValidationError):
            PyWebRequestRequest(session="x", **bad)
    PyWebRequestRequest(session="x", method="PATCH", path="/" + "a" * 1999, body="x" * 1_000_000)
    with pytest.raises(ValidationError):
        PyWebStartRequest(step_id="x", code="x" * 200_001)


def test_the_step_kind_and_the_check_dispatch(web_routes) -> None:
    from code_coach.canvas import check_step
    from code_coach.canvas.content import Step

    first = web_routes["pywa-01-hello"]
    assert first.kind == "web" and first.surface == "web" and first.language == "python"
    # The other kinds are as they were.
    plain = Step("x", "t", "t", "g", "", "", "", language="python")
    dom = Step("y", "t", "t", "g", "", "", "", html="<p>")
    assert (plain.kind, plain.surface, dom.kind) == ("canvas", "canvas", "dom")
    assert Step("z", "t", "t", "g", "", "", "", html="<p>", surface="web").kind == "dom"
    good = check_step(first.id, first.solution)
    assert good is not None and good.passed
    bad = check_step(first.id, first.starter)
    assert bad is not None and not bad.passed and bad.message.startswith("GET / returned 404")
    assert check_step(web_routes["pywa-12-yours"].id, "anything").passed  # the open step


def test_check_goes_to_the_web_harness_for_a_web_step(web_routes) -> None:
    from code_coach.api.schemas import CanvasCheckRequest
    from code_coach.api.server import canvas_check

    first = web_routes["pywa-01-hello"]
    bad = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.starter))
    assert bad.passed is False and bad.message.startswith("GET / returned 404")
    good = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.solution))
    assert good.passed is True


def test_the_library_text_documents_what_the_track_teaches() -> None:
    text = (Path(webses.__file__).parent / "lib" / "web.py").read_text(encoding="utf-8")
    for word in ("@app.get", "<int:id>", "args_all", "set_cookie", "errorhandler", "render(", "safe(", "HEAD", "OPTIONS"):
        assert word in text, word
    assert re.search(r"^import (?!sys$)", text, re.M)  # the standard library only: no third-party import
    third_party = re.findall(r"^(?:from|import) (flask|werkzeug|jinja2|requests|fastapi|starlette)\b", text, re.M)
    assert third_party == []
