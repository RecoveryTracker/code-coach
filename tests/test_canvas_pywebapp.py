"""Canvas: the "Web (Python)" track - a Link Saver app, one step at a time.

Each step's check makes real HTTP requests to the learner's app (run_pyweb_check
starts it in a child process and talks to it over a socket). So the suite holds
every check to the same four things as the other tracks: the step's own
solution passes, its starter (the step before, finished) does not, the mistakes
people really make at that step fail it - JSON returned as a string with the
wrong content type, 200 where 201 or 404 belongs, a value that is not escaped,
state that is not kept, a 302 where 303 is asked for, a cookie that is set and
never read back, an id that is used twice - and other ways of writing the same
behaviour pass.

The tests look steps up by id in their own module, so they need no
registration in canvas/__init__.py.
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas.content_pyweb_track import PYWEBAPP_STEPS as STEPS
from code_coach.canvas.pyweb.check import run_pyweb_check

BY_ID = {s.id: s for s in STEPS}
CHECKED = [s.id for s in STEPS if s.check]

# A change is a list of (old, new) swaps applied together; each entry is (label, [swaps]).
Change = tuple[str, list[tuple[str, str]]]


def _apply(code: str, swaps: list[tuple[str, str]]) -> str:
    for old, new in swaps:
        assert code.count(old) >= 1, old
        code = code.replace(old, new)
    return code


# The routes each check asks for. The goal has to name every one, or a learner cannot know them.
NAMED_IN_GOAL: dict[str, list[str]] = {
    "pywa-01-hello": ["GET /"],
    "pywa-02-params": ["/hello/<name>", "/hello/Ada", "/hello/Grace%20Hopper"],
    "pywa-03-query": ["/search", "q=py", "q=py&q=mdn", "text/plain", "BOOKMARKS"],
    "pywa-04-html": ["/bookmarks", "<h1>", "<li>", "<a href", "Fish &amp; &lt;chips&gt;"],
    "pywa-05-json": ["/api/bookmarks", "application/json", "BOOKMARKS"],
    "pywa-06-form": ["POST /add", "title", "url", "400", "201", "BOOKMARKS"],
    "pywa-07-api": ["/api/bookmarks", "/api/bookmarks/<int:bookmark_id>", "POST", "PUT", "DELETE", "204", "404"],
    "pywa-08-status": ["errorhandler(404)", "/api/", "Page not found", "<a href=\"/\">", "/status/<int:code>", "Status"],
    "pywa-09-redirect": ["POST /add", "303", "Location: /bookmarks", "/api/bookmarks"],
    "pywa-10-cookies": ["/visits", "visits", "Visits: N", "httponly"],
    "pywa-11-login": ["/login", "/me", "/admin", "/logout", "session", "401", "403", "303"],
}

# -- Pieces of the solutions the mistakes cut out --------------------------------------

_ADD_VALID = (
    "    message = problem(title, url)\n    if message:\n        abort(400, message)\n"
)
_SEARCH_COMP = (
    '    titles = [\n        b["title"]\n        for b in BOOKMARKS\n'
    '        if any(q.lower() in b["title"].lower() for q in wanted)\n    ]\n'
)
_ROWS = '    rows = "".join(render(ROW, **b) for b in BOOKMARKS)\n    return render(PAGE, rows=safe(rows))'
_ADD_ID = '    bookmark = {"id": NEXT_ID, "title": title, "url": url}\n    NEXT_ID += 1\n'
_FIND = (
    '    for bookmark in BOOKMARKS:\n        if bookmark["id"] == bookmark_id:\n            return bookmark\n'
    '    abort(404, "No bookmark with that id.")\n'
)
_NF_RETURN = "    return render(NOT_FOUND, path=request.path), 404\n"
_API_CREATE = "    title, url = read_json_bookmark()\n    return add_bookmark(title, url), 201\n"
_PUT_BODY = '    bookmark = find(bookmark_id)\n    bookmark["title"], bookmark["url"] = read_json_bookmark()\n    return bookmark\n'
_VISITS_READ = '    raw = request.cookies.get("visits", "")\n    count = int(raw) if raw.isdigit() else 0\n    count += 1\n'
_COOKIE = 'response.set_cookie("visits", str(count), httponly=True)'
_ADMIN_CHECK = '    if user not in ADMINS:\n        abort(403, "Admins only.")\n'
_TOKEN = "    token = secrets.token_hex(16)\n    SESSIONS[token] = user\n"
_LOGIN_CHECK = '    if USERS.get(user) != password:\n        abort(401, "Wrong username or password.")\n'
_SET_SESSION = 'response.set_cookie("session", token, httponly=True)'
_RESP_IMPORT_9 = ("from web import abort, app, redirect, render, request, safe\n",
                  "from web import Response, abort, app, redirect, render, request, safe\n")
_JSON_RESP_IMPORT_4 = ("from web import app, render, request, safe\n",
                       "from web import app, json_response, render, request, safe\n")
_RESP_IMPORT_4 = ("from web import app, render, request, safe\n",
                  "from web import Response, app, render, request, safe\n")
_RESP_IMPORT_6 = ("from web import abort, app, render, request, safe\n",
                  "from web import Response, abort, app, json_response, render, request, safe\n")

#: Wrong programs, each a real mistake at that step, that the check must fail.
MISTAKES: dict[str, list[Change]] = {
    "pywa-01-hello": [
        ("the wrong path", [('@app.get("/")', '@app.get("/home")')]),
        ("a POST route where a GET is asked", [('@app.get("/")', '@app.post("/")')]),
        ("print instead of return", [('return "Link Saver"', 'print("Link Saver")')]),
        ("the wrong text", [('"Link Saver"', '"Bookmarks"')]),
        ("no decorator, so no route", [('@app.get("/")\n', "")]),
        ("nothing returned (a forgotten return)", [('    return "Link Saver"', '    "Link Saver"')]),
    ],
    "pywa-02-params": [
        ("the f is forgotten", [('f"Hello, {name}!"', '"Hello, {name}!"')]),
        ("the exclamation mark is forgotten", [('f"Hello, {name}!"', 'f"Hello, {name}"')]),
        ("no hole in the path", [('"/hello/<name>"', '"/hello"'), ("def hello(name):", 'def hello(name="x"):')]),
        ("the parameter is named differently from the hole",
         [('def hello(name):\n    return f"Hello, {name}!"', 'def hello(person):\n    return f"Hello, {person}!"')]),
        ("the hole only takes numbers", [('"/hello/<name>"', '"/hello/<int:name>"')]),
        ("always greets the same person", [('f"Hello, {name}!"', 'f"Hello, Ada!"')]),
        ("the name is not decoded", [('f"Hello, {name}!"', 'f"Hello, {name.replace(\' \', \'%20\')}!"')]),
    ],
    "pywa-03-query": [
        ("a missing q is a KeyError", [('wanted = request.args_all.get("q", [""])', 'wanted = [request.args["q"]]')]),
        ("only the first q", [('wanted = request.args_all.get("q", [""])', 'wanted = [request.args.get("q", "")]')]),
        ("case matters", [('if any(q.lower() in b["title"].lower() for q in wanted)', 'if any(q in b["title"] for q in wanted)')]),
        ("no q means nothing matches", [('request.args_all.get("q", [""])', 'request.args_all.get("q", [])')]),
        ("a title is listed once per matching q", [(_SEARCH_COMP, (
            "    titles = []\n    for q in wanted:\n        for b in BOOKMARKS:\n"
            "            if q.lower() in b[\"title\"].lower():\n                titles.append(b[\"title\"])\n"))]),
        ("sent as HTML", [('return "\\n".join(titles), 200, {"Content-Type": "text/plain"}', 'return "\\n".join(titles)')]),
        ("every q must match", [("if any(q.lower()", "if all(q.lower()")]),
        ("titles on one line", [('"\\n".join(titles)', '", ".join(titles)')]),
    ],
    "pywa-04-html": [
        ("nothing is escaped", [(_ROWS, (
            '    rows = "".join(f\'<li><a href="{b["url"]}">{b["title"]}</a></li>\' for b in BOOKMARKS)\n'
            '    return "<h1>Bookmarks</h1><ul>" + rows + "</ul>"'))]),
        ("the rows are escaped a second time", [("rows=safe(rows)", "rows=rows")]),
        ("only the title is escaped, not the url", [
            ("from web import app, render, request, safe\n", "from web import app, escape, render, request, safe\n"),
            (_ROWS, '    rows = "".join(f\'<li><a href="{b["url"]}">{escape(b["title"])}</a></li>\' for b in BOOKMARKS)\n'
                    "    return render(PAGE, rows=safe(rows))")]),
        ("no heading", [('PAGE = "<h1>Bookmarks</h1><ul>$rows</ul>"', 'PAGE = "<ul>$rows</ul>"')]),
        ("sent as plain text", [("    return render(PAGE, rows=safe(rows))", '    return render(PAGE, rows=safe(rows)), 200, {"Content-Type": "text/plain"}')]),
        ("no list items", [("<li><a href=\"$url\">$title</a></li>", "<p><a href=\"$url\">$title</a></p>")]),
        ("no links", [("<li><a href=\"$url\">$title</a></li>", "<li>$title</li>")]),
    ],
    "pywa-05-json": [
        ("str() of the list", [("    return BOOKMARKS\n", "    return str(BOOKMARKS)\n")]),
        ("a JSON string sent as HTML", [
            ("from web import app, render, request, safe\n", "import json\n\nfrom web import app, render, request, safe\n"),
            ("    return BOOKMARKS\n", "    return json.dumps(BOOKMARKS)\n")]),
        ("the titles escaped for HTML", [
            ("from web import app, render, request, safe\n", "import html\n\nfrom web import app, render, request, safe\n"),
            ("    return BOOKMARKS\n", '    return [{**b, "title": html.escape(b["title"])} for b in BOOKMARKS]\n')]),
        ("only the titles", [("    return BOOKMARKS\n", '    return [b["title"] for b in BOOKMARKS]\n')]),
        ("the list wrapped in an object", [("    return BOOKMARKS\n", '    return {"bookmarks": BOOKMARKS}\n')]),
        ("the ids are left out", [("    return BOOKMARKS\n", '    return [{"title": b["title"], "url": b["url"]} for b in BOOKMARKS]\n')]),
    ],
    "pywa-06-form": [
        ("200 where 201 Created belongs", [("    return add_bookmark(title, url), 201\n", "    return add_bookmark(title, url)\n")]),
        ("reads the query string, not the form", [
            ('request.form.get("title", "")', 'request.args.get("title", "")'),
            ('request.form.get("url", "")', 'request.args.get("url", "")')]),
        ("the title is not stripped", [('request.form.get("title", "").strip()', 'request.form.get("title", "")')]),
        ("no validation at all", [(_ADD_VALID, "")]),
        ("a javascript: url is accepted", [(
            '    if not url.startswith(("http://", "https://")):\n        return "The url must start with http:// or https://"\n', "")]),
        ("saved first, then refused", [(
            _ADD_VALID + "    return add_bookmark(title, url), 201\n",
            "    bookmark = add_bookmark(title, url)\n" + _ADD_VALID + "    return bookmark, 201\n")]),
        ("the list is re-assigned without global", [("    BOOKMARKS.append(bookmark)\n", "    BOOKMARKS = BOOKMARKS + [bookmark]\n")]),
        ("the bookmark is added to a copy", [("    BOOKMARKS.append(bookmark)\n", "    kept = list(BOOKMARKS)\n    kept.append(bookmark)\n")]),
        ("NEXT_ID is changed without global", [("    global NEXT_ID\n", "")]),
        ("every bookmark gets the same id", [("    NEXT_ID += 1\n", "")]),
        ("the 400 does not say what is wrong", [('return "A title is required."', 'return "Bad input."')]),
    ],
    "pywa-07-api": [
        ("delete answers 200", [('    return "", 204\n', '    return ""\n')]),
        ("a missing id is a crash, not a 404", [('    abort(404, "No bookmark with that id.")\n', "    return None\n")]),
        ("an id is reused after a delete", [(_ADD_ID, '    bookmark = {"id": max(b["id"] for b in BOOKMARKS) + 1, "title": title, "url": url}\n')]),
        ("an id is len + 1", [(_ADD_ID, '    bookmark = {"id": len(BOOKMARKS) + 1, "title": title, "url": url}\n')]),
        ("create answers 200", [(_API_CREATE, "    title, url = read_json_bookmark()\n    return add_bookmark(title, url)\n")]),
        ("reads the form, not the JSON", [("    data = request.json\n", "    data = request.form\n")]),
        ("PUT takes anything", [(
            '    bookmark["title"], bookmark["url"] = read_json_bookmark()\n',
            '    data = request.json or {}\n    bookmark["title"], bookmark["url"] = data.get("title"), data.get("url")\n')]),
        ("PUT of a missing id creates one", [(_PUT_BODY, "    title, url = read_json_bookmark()\n    return add_bookmark(title, url)\n")]),
        ("a JSON list is not refused", [(
            '    if not isinstance(data, dict):\n        abort(400, "Send a JSON object with a title and a url.")\n', "")]),
        ("the hole is not an int", [('@app.get("/api/bookmarks/<int:bookmark_id>")', '@app.get("/api/bookmarks/<bookmark_id>")')]),
        ("the new bookmark goes into a copy", [("    BOOKMARKS.append(bookmark)\n", "    kept = list(BOOKMARKS)\n    kept.append(bookmark)\n")]),
        ("delete removes nothing", [("    BOOKMARKS.remove(find(bookmark_id))\n", "    find(bookmark_id)\n")]),
    ],
    "pywa-08-status": [
        ("the 404 page is a 200", [(_NF_RETURN, "    return render(NOT_FOUND, path=request.path)\n")]),
        ("the path is put into the page unescaped", [(_NF_RETURN, '    return NOT_FOUND.replace("$path", request.path), 404\n')]),
        ("/api/ gets the page too", [('    if request.path.startswith("/api/"):\n        return {"error": "not found"}, 404\n', "")]),
        ("the page does not say Page not found", [("<h1>Page not found</h1>", "<h1>Oops</h1>")]),
        ("no link back home", [('<p><a href="/">Back to Link Saver</a></p>', "")]),
        ("the JSON 404 is a 200", [('        return {"error": "not found"}, 404\n', '        return {"error": "not found"}\n')]),
        ("the status route is always 200", [('    return f"Status {code}", code\n', '    return f"Status {code}"\n')]),
        ("any code is accepted", [('    if not 200 <= code <= 599:\n        abort(400, "Use a status from 200 to 599.")\n', "")]),
        ("the page does not show the path", [("<code>$path</code>", "<code>that page</code>")]),
        ("the wrong handler status", [("@app.errorhandler(404)", "@app.errorhandler(405)")]),
    ],
    "pywa-09-redirect": [
        ("302 where 303 is asked", [('return redirect("/bookmarks", 303)', 'return redirect("/bookmarks")')]),
        ("a 301", [('return redirect("/bookmarks", 303)', 'return redirect("/bookmarks", 301)')]),
        ("redirects to the home page", [('return redirect("/bookmarks", 303)', 'return redirect("/", 303)')]),
        ("redirects before saving", [(
            '    add_bookmark(title, url)\n    return redirect("/bookmarks", 303)\n',
            '    return redirect("/bookmarks", 303)\n    add_bookmark(title, url)\n')]),
        ("a refused form is redirected too", [(
            "    if message:\n        abort(400, message)\n    add_bookmark(title, url)\n",
            '    if message:\n        return redirect("/bookmarks", 303)\n    add_bookmark(title, url)\n')]),
        ("303 without a Location", [_RESP_IMPORT_9, ('return redirect("/bookmarks", 303)', 'return Response("", 303)')]),
        ("the JSON API redirects too", [(_API_CREATE, '    title, url = read_json_bookmark()\n    add_bookmark(title, url)\n    return redirect("/bookmarks", 303)\n')]),
        ("still answers 201", [('    add_bookmark(title, url)\n    return redirect("/bookmarks", 303)\n', "    return add_bookmark(title, url), 201\n")]),
    ],
    "pywa-10-cookies": [
        ("the cookie is set and never read back", [('    raw = request.cookies.get("visits", "")\n', '    raw = ""\n')]),
        ("a count on the server, shared by everybody", [
            (_VISITS_READ, "    global TOTAL\n    TOTAL += 1\n    count = TOTAL\n"),
            ('@app.get("/visits")', 'TOTAL = 0\n\n\n@app.get("/visits")')]),
        ("junk in the cookie crashes the page", [("count = int(raw) if raw.isdigit() else 0", "count = int(raw or 0)")]),
        ("the cookie keeps the old count", [(_COOKIE, 'response.set_cookie("visits", str(count - 1), httponly=True)')]),
        ("not httponly", [(_COOKIE, 'response.set_cookie("visits", str(count))')]),
        ("a different text", [('f"Visits: {count}"', 'f"Visit count {count}"')]),
        ("no cookie is set", [("    " + _COOKIE + "\n", "")]),
        ("a negative cookie is believed", [("raw.isdigit()", 'raw.lstrip("-").isdigit()')]),
        ("the count is one behind", [("    count += 1\n", "")]),
    ],
    "pywa-11-login": [
        ("the username is the cookie", [(_TOKEN, "    token = user\n    SESSIONS[token] = user\n")]),
        ("the cookie is believed as it is", [
            ('    return SESSIONS.get(request.cookies.get("session", ""))', '    return request.cookies.get("session")')]),
        ("everybody is an admin", [(_ADMIN_CHECK, "")]),
        ("401 where 403 belongs", [('abort(403, "Admins only.")', 'abort(401, "Admins only.")')]),
        ("any password works", [(_LOGIN_CHECK, '    if user not in USERS:\n        abort(401, "Wrong username or password.")\n')]),
        ("a failed login is 403", [('abort(401, "Wrong username or password.")', 'abort(403, "Wrong username or password.")')]),
        ("a token that is too short", [("secrets.token_hex(16)", "secrets.token_hex(2)")]),
        ("the same token every time", [("secrets.token_hex(16)", '"abcdef0123456789abcdef"')]),
        ("logout does not forget the token", [('    SESSIONS.pop(request.cookies.get("session", ""), None)\n', "")]),
        ("logout does not delete the cookie", [('    response.delete_cookie("session")\n', "")]),
        ("the cookie is not httponly", [(_SET_SESSION, 'response.set_cookie("session", token)')]),
        ("login answers 200", [('    response = redirect("/me", 303)\n', '    response = Response("welcome")\n')]),
        ("the admin page needs no login", [(
            '    user = current_user()\n    if user is None:\n        abort(401, "Please log in first.")\n    if user not in ADMINS:',
            "    user = current_user()\n    if user is not None and user not in ADMINS:")]),
        ("/me is open to everyone", [('    if user is None:\n        abort(401, "Please log in first.")\n    return f"You are {user}."',
                                      '    return f"You are {user}."')]),
        ("a wrong login still sets a cookie", [(_LOGIN_CHECK, (
            '    if USERS.get(user) != password:\n        response = Response("Wrong username or password.", 401)\n'
            '        response.set_cookie("session", "x")\n        return response\n'))]),
    ],
}

#: Right programs written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[list[tuple[str, str]]]] = {
    "pywa-01-hello": [
        [('@app.get("/")', '@app.route("/")')],
        [('@app.get("/")', '@app.route("/", methods=["GET"])')],
        [('return "Link Saver"', 'return "<h1>Link Saver</h1>"')],
        [('return "Link Saver"', 'return "Link Saver", 200')],
        [("from web import app\n", "from web import Response, app\n"), ('return "Link Saver"', 'return Response("Link Saver")')],
        [("def home():", "def index():")],
        [('return "Link Saver"', 'return "Link Saver\\n"')],
    ],
    "pywa-02-params": [
        [('f"Hello, {name}!"', '"Hello, " + name + "!"')],
        [('f"Hello, {name}!"', '"Hello, {}!".format(name)')],
        [('f"Hello, {name}!"', 'f"<h1>Hello, {name}!</h1>"')],
        [('@app.get("/hello/<name>")', '@app.route("/hello/<name>")')],
        [("def hello(name):", "def hello(name: str):")],
        [('@app.get("/hello/<name>")', '@app.get("/hello/<str:name>")')],
    ],
    "pywa-03-query": [
        [(_SEARCH_COMP, (
            "    titles = []\n    for b in BOOKMARKS:\n        for q in wanted:\n"
            "            if q.lower() in b[\"title\"].lower():\n                titles.append(b[\"title\"])\n                break\n"))],
        [(".lower()", ".casefold()")],
        [('wanted = request.args_all.get("q", [""])', 'wanted = request.args_all.get("q") or [""]')],
        [("from web import app, request\n", "from web import Response, app, request\n"),
         ('return "\\n".join(titles), 200, {"Content-Type": "text/plain"}',
          'return Response("\\n".join(titles), headers={"Content-Type": "text/plain; charset=utf-8"})')],
        [('return "\\n".join(titles), 200,', 'return "\\n".join(titles) + "\\n", 200,')],
    ],
    "pywa-04-html": [
        [("from web import app, render, request, safe\n", "import html\n\nfrom web import app, render, request, safe\n"),
         (_ROWS, '    rows = "".join(\n        f\'<li><a href="{html.escape(b["url"])}">{html.escape(b["title"])}</a></li>\'\n'
                 '        for b in BOOKMARKS\n    )\n    return "<!doctype html><h1>Bookmarks</h1><ul>" + rows + "</ul>"')],
        [("from web import app, render, request, safe\n", "from web import app, escape, render, request, safe\n"),
         (_ROWS, '    rows = "".join(f\'<li><a href="{escape(b["url"])}">{escape(b["title"])}</a></li>\' for b in BOOKMARKS)\n'
                 "    return render(PAGE, rows=safe(rows))")],
        [('PAGE = "<h1>Bookmarks</h1><ul>$rows</ul>"', 'PAGE = "<!doctype html><title>Bookmarks</title><h1>Bookmarks</h1><ul>$rows</ul>"')],
        [("    return render(PAGE, rows=safe(rows))", "    return render(PAGE, rows=safe(rows)), 200")],
    ],
    "pywa-05-json": [
        [_JSON_RESP_IMPORT_4, ("    return BOOKMARKS\n", "    return json_response(BOOKMARKS)\n")],
        [("    return BOOKMARKS\n", "    return BOOKMARKS, 200\n")],
        [("    return BOOKMARKS\n", "    return list(BOOKMARKS)\n")],
        [("    return BOOKMARKS\n", "    return [dict(b) for b in BOOKMARKS]\n")],
        [("from web import app, render, request, safe\n", "import json\n\nfrom web import Response, app, render, request, safe\n"),
         ("    return BOOKMARKS\n", '    return Response(json.dumps(BOOKMARKS), headers={"Content-Type": "application/json"})\n')],
    ],
    "pywa-06-form": [
        [_RESP_IMPORT_6, ("    return add_bookmark(title, url), 201\n", "    return json_response(add_bookmark(title, url), 201)\n")],
        [("    return add_bookmark(title, url), 201\n", '    return add_bookmark(title, url), 201, {"Content-Type": "application/json"}\n')],
        [("        abort(400, message)\n", "        return message, 400\n")],
        [('request.form.get("title", "").strip()', '(request.form.get("title") or "").strip()')],
        [('if not url.startswith(("http://", "https://")):', 'if not url.lower().startswith(("http://", "https://")):')],
        [("from web import abort, app, render, request, safe\n", "from web import Response, abort, app, render, request, safe\n"),
         ("    return add_bookmark(title, url), 201\n", "    return Response(__import__('json').dumps(add_bookmark(title, url)), 201, {'Content-Type': 'application/json'})\n")],
    ],
    "pywa-07-api": [
        [('    bookmark["title"], bookmark["url"] = read_json_bookmark()\n',
          "    title, url = read_json_bookmark()\n    bookmark.update(title=title, url=url)\n")],
        [("    BOOKMARKS.remove(find(bookmark_id))\n", "    bookmark = find(bookmark_id)\n    BOOKMARKS[:] = [b for b in BOOKMARKS if b is not bookmark]\n")],
        [("from web import abort, app, render, request, safe\n", "from web import Response, abort, app, render, request, safe\n"),
         ('    return "", 204\n', '    return Response("", 204)\n')],
        [('    return "", 204\n', '    return "", 204, {}\n')],
        [(_FIND, '    found = next((b for b in BOOKMARKS if b["id"] == bookmark_id), None)\n'
                 '    if found is None:\n        abort(404, "No bookmark with that id.")\n    return found\n')],
        [(_API_CREATE, "    title, url = read_json_bookmark()\n    return json_response(add_bookmark(title, url), 201)\n"),
         ("from web import abort, app, render, request, safe\n", "from web import abort, app, json_response, render, request, safe\n")],
    ],
    "pywa-08-status": [
        [('request.path.startswith("/api/")', 'request.path.startswith("/api")')],
        [('request.path.startswith("/api/")', 'request.path.split("/")[1] == "api"')],
        [("from web import abort, app, render, request, safe\n", "from web import abort, app, json_response, render, request, safe\n"),
         ('        return {"error": "not found"}, 404\n', '        return json_response({"error": "not found"}, 404)\n')],
        [("from web import abort, app, render, request, safe\n", "from web import Response, abort, app, render, request, safe\n"),
         ('    return f"Status {code}", code\n', '    return Response(f"Status {code}", code)\n')],
        [("if not 200 <= code <= 599:", "if code < 200 or code > 599:")],
        [("from web import abort, app, render, request, safe\n", "import html\n\nfrom web import abort, app, render, request, safe\n"),
         (_NF_RETURN, '    return NOT_FOUND.replace("$path", html.escape(request.path)), 404\n')],
    ],
    "pywa-09-redirect": [
        [('return redirect("/bookmarks", 303)', 'return redirect("/bookmarks", code=303)')],
        [_RESP_IMPORT_9, ('return redirect("/bookmarks", 303)', 'return Response("", 303, {"Location": "/bookmarks"})')],
        [('return redirect("/bookmarks", 303)', 'return "See other", 303, {"Location": "/bookmarks"}')],
    ],
    "pywa-10-cookies": [
        [(_VISITS_READ, ('    try:\n        count = int(request.cookies.get("visits", "0"))\n    except ValueError:\n'
                         "        count = 0\n    count = max(count, 0) + 1\n"))],
        [(_COOKIE, 'response.set_cookie("visits", count, httponly=True)')],
        [(_COOKIE, 'response.set_cookie("visits", str(count), httponly=True, max_age=3600)')],
        [("raw.isdigit()", "raw.isdecimal()")],
        [(_COOKIE, 'response.set_cookie("visits", str(count), httponly=True, path="/", samesite="Lax")')],
    ],
    "pywa-11-login": [
        [("import secrets\n", "import uuid\n"), ("secrets.token_hex(16)", "uuid.uuid4().hex")],
        [("secrets.token_hex(16)", "secrets.token_urlsafe(16)")],
        [('return f"You are {user}."', 'return f"Hello, {user}!"')],
        [('abort(401, "Wrong username or password.")', 'return "Wrong username or password.", 401')],
        [("if user not in ADMINS:", 'if user != "ada":')],
        [('    SESSIONS.pop(request.cookies.get("session", ""), None)\n',
          '    token = request.cookies.get("session")\n    if token in SESSIONS:\n        del SESSIONS[token]\n')],
        [("    return f\"You are {user}.\"", "    return f\"You are {user}.\", 200")],
    ],
}


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids)) == 12
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pywa-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_web_steps_in_python_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Web (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert {s.surface for s in STEPS} == {"web"}
        assert all(s.kind == "web" for s in STEPS)
        assert all(not s.html and not s.css and not s.world for s in STEPS)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(STEPS, STEPS[1:]):
            assert after.starter == before.solution, after.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]
        assert STEPS[-1].starter == STEPS[-1].solution

    def test_every_program_is_python_that_compiles_and_uses_the_library(self) -> None:
        for s in STEPS:
            for code in (s.starter, s.solution):
                compile(code, s.id, "exec")
                assert "from web import" in code, s.id
                assert "flask" not in code.lower() and "app.run" not in code, s.id

    def test_every_check_compiles(self) -> None:
        for s in STEPS:
            if s.check:
                compile(s.check, s.id, "exec")

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS) + list(NAMED_IN_GOAL):
            assert step_id in BY_ID, step_id

    def test_every_checked_step_has_two_real_mistakes_and_a_hint(self) -> None:
        for s in STEPS:
            if s.check:
                assert len(MISTAKES.get(s.id, [])) >= 2, f"{s.id} has fewer than two mistakes the check is held against"
                assert s.hint, s.id

    def test_every_route_the_check_asks_for_is_named_in_the_goal(self) -> None:
        for step_id, words in NAMED_IN_GOAL.items():
            goal = BY_ID[step_id].goal
            for word in words:
                assert word in goal, f"{step_id}: the goal does not say {word!r}"

    def test_the_teaches_text_has_its_code_in_indented_blocks_only_where_meant(self) -> None:
        # The page shows a paragraph whose lines all start with four spaces as code.
        assert "    routes = {}" in BY_ID["pywa-01-hello"].teaches  # the toy decorator
        for s in STEPS:
            for block in s.teaches.split("\n\n"):
                lines = block.split("\n")
                assert all(l.startswith("    ") for l in lines) or not any(l.startswith("    ") for l in lines), s.id

    def test_the_concepts_the_track_promises_are_taught(self) -> None:
        text = " ".join(s.teaches + " " + s.goal for s in STEPS).lower()
        for word in ("decorator", "query string", "xss", "idempotent", "201", "204", "404", "303", "set-cookie",
                     "401", "403", "httponly", "global", "escape", "content-type", "json", "secrets"):
            assert word in text, word


class TestChecks:
    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_solution_passes_its_check(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_pyweb_check(s.solution, s.check)
        assert got.passed, f"{s.id}: {got.message}"

    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_starter_fails_its_check_and_says_why(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_pyweb_check(s.starter, s.check)
        assert not got.passed, s.id
        assert got.message, s.id
        # The first thing it says is a request and what came back, or a plain sentence about the page.
        assert re.match(r"(GET|POST|PUT|DELETE) /|The |Your |A |Visit|Logout|Following", got.message), got.message

    @pytest.mark.parametrize("step_id", sorted(MISTAKES))
    def test_real_mistakes_fail(self, step_id: str) -> None:
        s = BY_ID[step_id]
        for label, swaps in MISTAKES[step_id]:
            got = run_pyweb_check(_apply(s.solution, swaps), s.check)
            assert not got.passed, f"{step_id}: the check let this mistake through: {label}"
            assert got.message, f"{step_id}: {label}"

    @pytest.mark.parametrize("step_id", sorted(OTHER_WAYS))
    def test_other_right_answers_pass(self, step_id: str) -> None:
        s = BY_ID[step_id]
        for swaps in OTHER_WAYS[step_id]:
            got = run_pyweb_check(_apply(s.solution, swaps), s.check)
            assert got.passed, f"{step_id}: {swaps[0][0][:60]!r} -> {swaps[-1][1][:60]!r}: {got.message}"

    def test_the_open_step_always_passes(self) -> None:
        # No check to run: the harness answers without starting anything.
        from code_coach.canvas.content import Step

        assert STEPS[-1].check == ""
        assert isinstance(STEPS[-1], Step)

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        s = BY_ID["pywa-01-hello"]
        got = run_pyweb_check(s.solution.replace('    return "Link Saver"', '    "Link Saver"'), s.check)
        assert got.message.startswith("GET / returned 500 Internal Server Error, expected 200.")
        assert "returned None" in got.message and "forget `return`" in got.message

        s = BY_ID["pywa-08-status"]
        got = run_pyweb_check(s.solution.replace(_NF_RETURN, "    return render(NOT_FOUND, path=request.path)\n"), s.check)
        assert got.message.startswith("GET /nowhere returned 200 OK, expected 404.")

        s = BY_ID["pywa-09-redirect"]
        got = run_pyweb_check(s.solution.replace('return redirect("/bookmarks", 303)', 'return redirect("/bookmarks")'), s.check)
        assert got.message.startswith("POST /add returned 302 Found, expected 303.")

        s = BY_ID["pywa-11-login"]
        got = run_pyweb_check(s.solution.replace(_ADMIN_CHECK, ""), s.check)
        assert "bob is logged in but is not an admin: 403 Forbidden" in got.message
        got = run_pyweb_check(_apply(s.solution, [(_TOKEN, "    token = user\n    SESSIONS[token] = user\n")]), s.check)
        assert "not the username" in got.message

        s = BY_ID["pywa-10-cookies"]
        got = run_pyweb_check(s.solution.replace('    raw = request.cookies.get("visits", "")\n', '    raw = ""\n'), s.check)
        assert "Visit number 2 from the same browser should say Visits: 2" in got.message

    def test_a_crash_at_the_top_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_pyweb_check(s.starter + "\nnope()\n", s.check)
        assert not got.passed
        assert got.message == "Your code threw on line 6: NameError: name 'nope' is not defined"

    def test_an_endless_loop_at_the_top_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_pyweb_check(s.solution + "\nwhile True:\n    pass\n", s.check)
        assert not got.passed
        assert "loop that never ends" in got.message

    def test_a_route_that_never_returns_fails_the_check_instead_of_hanging_it(self) -> None:
        s = STEPS[0]
        code = s.solution.replace('    return "Link Saver"', "    while True:\n        pass")
        got = run_pyweb_check(code, s.check)
        assert not got.passed and got.message.startswith("GET / returned 500")
        assert "ran out of time" in got.message or "Your app crashed" in got.message
