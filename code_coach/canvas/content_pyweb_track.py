"""The "Web (Python)" Canvas track: a small web app, built a step at a time, run by a real server.

The learner writes a Link Saver - a bookmarks app - with a tiny Flask-like
library (`from web import app, request, ...`, canvas/pyweb/lib/web.py). Code
Coach starts a real HTTP server for the program, on 127.0.0.1, and a step's
check makes REAL HTTP requests to it (canvas/pyweb/check.py): it never reads
the program, so any implementation that behaves right passes.

Each step's starter is the previous step's solution; the check for a step
fails on its starter - the suite holds every step to both
(tests/test_canvas_pywebapp.py). The checks say what the request was and what
came back: "GET /hello/Ada returned 404 Not Found, expected 200."

A check is the body of a Python script with `cc` (get, post, put, delete,
follow, jar, cookies, logs), `expect(ok, message)` and `near`. The goals name
every route and behaviour the check relies on.

The steps: a route, a path parameter, the query string, HTML and escaping,
JSON, a form POST, a JSON API (PUT/DELETE, state), status codes and a 404
page, redirect after POST, cookies, a login with a session token, and an open
step. Python along the way: decorators (a toy one is written out in step 1),
dicts as JSON, f-strings, str.strip/lower/isdigit, any(), abort and
exceptions, module-level state with and without `global`, the secrets module.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Web (Python)"


def _program(imports: str, *blocks: str) -> str:
    return imports.strip("\n") + "\n\n\n" + "\n\n\n".join(b.strip("\n") for b in blocks) + "\n"


_IMPORT_1 = "from web import app"
_IMPORT_3 = "from web import app, request"
_IMPORT_4 = "from web import app, render, request, safe"
_IMPORT_6 = "from web import abort, app, render, request, safe"
_IMPORT_9 = "from web import abort, app, redirect, render, request, safe"
_IMPORT_10 = "from web import Response, abort, app, redirect, render, request, safe"
_IMPORT_11 = "import secrets\n\nfrom web import Response, abort, app, redirect, render, request, safe"

# -- the pieces the solutions are put together from ----------------------------

_HOME = r'''
@app.get("/")
def home():
    return "Link Saver"
'''

_HELLO = r'''
@app.get("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"
'''

_DATA = r'''
BOOKMARKS = [
    {"id": 1, "title": "Python docs", "url": "https://docs.python.org/3/"},
    {"id": 2, "title": "MDN", "url": "https://developer.mozilla.org/"},
    {"id": 3, "title": "PyPI", "url": "https://pypi.org/"},
    {"id": 4, "title": "Fish & <chips>", "url": "https://example.com/fish?a=1&b=2"},
]
'''

_SEARCH = r'''
@app.get("/search")
def search():
    wanted = request.args_all.get("q", [""])
    titles = [
        b["title"]
        for b in BOOKMARKS
        if any(q.lower() in b["title"].lower() for q in wanted)
    ]
    return "\n".join(titles), 200, {"Content-Type": "text/plain"}
'''

_TEMPLATES = r'''
ROW = '<li><a href="$url">$title</a></li>'
PAGE = "<h1>Bookmarks</h1><ul>$rows</ul>"
'''

_PAGE = r'''
@app.get("/bookmarks")
def bookmarks_page():
    rows = "".join(render(ROW, **b) for b in BOOKMARKS)
    return render(PAGE, rows=safe(rows))
'''

_API_LIST = r'''
@app.get("/api/bookmarks")
def api_list():
    return BOOKMARKS
'''

_HELPERS = r'''
NEXT_ID = 5


def problem(title, url):
    if not title:
        return "A title is required."
    if not url.startswith(("http://", "https://")):
        return "The url must start with http:// or https://"
    return None


def add_bookmark(title, url):
    global NEXT_ID
    bookmark = {"id": NEXT_ID, "title": title, "url": url}
    NEXT_ID += 1
    BOOKMARKS.append(bookmark)
    return bookmark
'''

_ADD_201 = r'''
@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    message = problem(title, url)
    if message:
        abort(400, message)
    return add_bookmark(title, url), 201
'''

_FIND = r'''
def find(bookmark_id):
    for bookmark in BOOKMARKS:
        if bookmark["id"] == bookmark_id:
            return bookmark
    abort(404, "No bookmark with that id.")


def read_json_bookmark():
    data = request.json
    if not isinstance(data, dict):
        abort(400, "Send a JSON object with a title and a url.")
    title = str(data.get("title", "")).strip()
    url = str(data.get("url", "")).strip()
    message = problem(title, url)
    if message:
        abort(400, message)
    return title, url
'''

_API_ROUTES = r'''
@app.get("/api/bookmarks/<int:bookmark_id>")
def api_get(bookmark_id):
    return find(bookmark_id)


@app.post("/api/bookmarks")
def api_create():
    title, url = read_json_bookmark()
    return add_bookmark(title, url), 201


@app.put("/api/bookmarks/<int:bookmark_id>")
def api_replace(bookmark_id):
    bookmark = find(bookmark_id)
    bookmark["title"], bookmark["url"] = read_json_bookmark()
    return bookmark


@app.delete("/api/bookmarks/<int:bookmark_id>")
def api_delete(bookmark_id):
    BOOKMARKS.remove(find(bookmark_id))
    return "", 204
'''

_NOT_FOUND = r'''
NOT_FOUND = """<h1>Page not found</h1>
<p>Nothing lives at <code>$path</code>.</p>
<p><a href="/">Back to Link Saver</a></p>"""


@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return {"error": "not found"}, 404
    return render(NOT_FOUND, path=request.path), 404


@app.get("/status/<int:code>")
def status(code):
    if not 200 <= code <= 599:
        abort(400, "Use a status from 200 to 599.")
    return f"Status {code}", code
'''

_ADD_303 = r'''
@app.post("/add")
def add():
    title = request.form.get("title", "").strip()
    url = request.form.get("url", "").strip()
    message = problem(title, url)
    if message:
        abort(400, message)
    add_bookmark(title, url)
    return redirect("/bookmarks", 303)
'''

_VISITS = r'''
@app.get("/visits")
def visits():
    raw = request.cookies.get("visits", "")
    count = int(raw) if raw.isdigit() else 0
    count += 1
    response = Response(f"Visits: {count}")
    response.set_cookie("visits", str(count), httponly=True)
    return response
'''

_LOGIN = r'''
USERS = {"ada": "lovelace", "bob": "builder"}
ADMINS = {"ada"}
SESSIONS = {}


def current_user():
    return SESSIONS.get(request.cookies.get("session", ""))


@app.post("/login")
def login():
    user = request.form.get("user", "")
    password = request.form.get("password", "")
    if USERS.get(user) != password:
        abort(401, "Wrong username or password.")
    token = secrets.token_hex(16)
    SESSIONS[token] = user
    response = redirect("/me", 303)
    response.set_cookie("session", token, httponly=True)
    return response


@app.get("/me")
def me():
    user = current_user()
    if user is None:
        abort(401, "Please log in first.")
    return f"You are {user}."


@app.get("/admin")
def admin():
    user = current_user()
    if user is None:
        abort(401, "Please log in first.")
    if user not in ADMINS:
        abort(403, "Admins only.")
    return "Admin area"


@app.post("/logout")
def logout():
    SESSIONS.pop(request.cookies.get("session", ""), None)
    response = redirect("/", 303)
    response.delete_cookie("session")
    return response
'''

# -- the programs ---------------------------------------------------------------------

_STARTER_1 = '''from web import app

# Your app goes here: a function that returns the text, and a route
# that sends requests for "/" to it.
'''

_S1 = _program(_IMPORT_1, _HOME)
_S2 = _program(_IMPORT_1, _HOME, _HELLO)
_S3 = _program(_IMPORT_3, _HOME, _HELLO, _DATA, _SEARCH)
_S4 = _program(_IMPORT_4, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE)
_S5 = _program(_IMPORT_4, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST)
_S6 = _program(_IMPORT_6, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_201)
_S7 = _program(_IMPORT_6, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_201,
               _FIND, _API_ROUTES)
_S8 = _program(_IMPORT_6, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_201,
               _FIND, _API_ROUTES, _NOT_FOUND)
_S9 = _program(_IMPORT_9, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_303,
               _FIND, _API_ROUTES, _NOT_FOUND)
_S10 = _program(_IMPORT_10, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_303,
                _FIND, _API_ROUTES, _NOT_FOUND, _VISITS)
_S11 = _program(_IMPORT_11, _HOME, _HELLO, _DATA, _SEARCH, _TEMPLATES, _PAGE, _API_LIST, _HELPERS, _ADD_303,
                _FIND, _API_ROUTES, _NOT_FOUND, _VISITS, _LOGIN)

# -- the checks ------------------------------------------------------------------------
# Python statements run with `cc`, `expect`, `near`. Nothing here reads the learner's
# names: it asks over HTTP and looks at the answer.

_C1 = r'''
r = cc.get("/")
r.expect_status(200, why="Is there a route for / - a function with @app.get('/') above it?")
expect("Link Saver" in r.text, f"GET / should answer with the text Link Saver, but it sent {r.snippet()}.")
'''

_C2 = r'''
for name, shown in (("Ada", "Ada"), ("Grace%20Hopper", "Grace Hopper")):
    r = cc.get("/hello/" + name)
    r.expect_status(200, why="Is there a route for /hello/<name>, and does its function take a `name` parameter?")
    expect(f"Hello, {shown}!" in r.text,
           f"GET /hello/{name} should answer Hello, {shown}! but it sent {r.snippet()}.")
r = cc.get("/hello/")
expect(r.status == 404, f"GET /hello/ has no name in it, so it should be 404 Not Found, but it returned {r.status}.")
r = cc.get("/")
expect(r.status == 200 and "Link Saver" in r.text, "GET / should still answer Link Saver.")
'''

_C3 = r'''
ALL = ["Python docs", "MDN", "PyPI", "Fish & <chips>"]


def titles(path):
    r = cc.get(path)
    r.expect_status(200, why="Is there a route for /search?")
    r.expect_type("text/plain")
    return [line for line in r.text.splitlines() if line.strip()]


for path, want, why in (
    ("/search", ALL, "With no q at all every title matches."),
    ("/search?q=", ALL, "An empty q matches every title."),
    ("/search?q=py", ["Python docs", "PyPI"], "Both Python docs and PyPI contain py."),
    ("/search?q=PY", ["Python docs", "PyPI"], "Upper and lower case must not matter."),
    ("/search?q=zzz", [], "Nothing contains zzz."),
    ("/search?q=py&q=mdn", ["Python docs", "MDN", "PyPI"],
     "q was given twice: a title matches if it contains EITHER, listed in the order of BOOKMARKS."),
    ("/search?q=mdn&q=mdn", ["MDN"], "A title is listed once, however many q values match it."),
    ("/search?q=fish%20%26", ["Fish & <chips>"], "%20 and %26 are a space and an &: the query must be decoded."),
):
    got = titles(path)
    expect(got == want, f"GET {path} should list {want}, but it listed {got}. {why}")
'''

_C4 = r'''
import re

r = cc.get("/bookmarks")
r.expect_status(200, why="Is there a route for /bookmarks?")
r.expect_type("text/html")
page = r.text
expect("<h1" in page, "The page should have a heading: an <h1>.")
count = len(re.findall(r"<li[\s>]", page))
expect(count == 4, f"The page should have one <li> per bookmark (4), but it has {count}.")
for title, url in (("Python docs", "https://docs.python.org/3/"), ("MDN", "https://developer.mozilla.org/"),
                   ("PyPI", "https://pypi.org/")):
    expect(title in page, f"The page should show the title {title}.")
    expect(f'href="{url}"' in page, f"The title {title} should be a link: <a href=\"{url}\">.")
expect("<chips>" not in page,
       "The title Fish & <chips> reached the page as a real <chips> tag. Anyone who can save a title could "
       "put a <script> in the same way - escape every value that goes into HTML.")
expect("Fish &amp; &lt;chips&gt;" in page,
       "The title Fish & <chips> should be escaped to Fish &amp; &lt;chips&gt; in the HTML, so it shows as text.")
expect("fish?a=1&amp;b=2" in page,
       "A url goes into an attribute, and an & in HTML is written &amp;: the link should be href=\"...fish?a=1&amp;b=2\".")
'''

_C5 = r'''
WANT = [
    {"id": 1, "title": "Python docs", "url": "https://docs.python.org/3/"},
    {"id": 2, "title": "MDN", "url": "https://developer.mozilla.org/"},
    {"id": 3, "title": "PyPI", "url": "https://pypi.org/"},
    {"id": 4, "title": "Fish & <chips>", "url": "https://example.com/fish?a=1&b=2"},
]
r = cc.get("/api/bookmarks")
r.expect_status(200, why="Is there a route for /api/bookmarks?")
r.expect_type("application/json")
got = r.json()
expect(isinstance(got, list), f"The JSON should be a list of bookmarks, but it is a {type(got).__name__}.")
expect(got == WANT, f"The JSON should be exactly the four bookmarks, but it was {got}. "
       "Titles are not escaped in JSON - Fish & <chips> stays as it is.")
'''

_C6 = r'''
import re


def plain(r):
    return re.sub(r"<[^>]*>", " ", r.text).lower()


def listing():
    r = cc.get("/api/bookmarks")
    r.expect_status(200, why="GET /api/bookmarks (the last step) should still work.")
    return r.json()


before = listing()
r = cc.post("/add", form={"title": "  Flask docs ", "url": " https://flask.palletsprojects.com/ "})
r.expect_status(201, why="A form that is fine creates a bookmark, and 201 Created says so. Is there a POST route for /add?")
made = r.expect_json()
expect(isinstance(made, dict) and made.get("title") == "Flask docs" and made.get("url") == "https://flask.palletsprojects.com/",
       f"POST /add should answer with the new bookmark, with the title and url stripped, but it sent {r.snippet()}.")
expect(isinstance(made.get("id"), int) and made["id"] not in [b["id"] for b in before],
       f"The new bookmark needs an id nobody has - it got {made.get('id')!r}.")
after = listing()
expect(len(after) == len(before) + 1 and after[-1] == made,
       "The new bookmark should be added to the end of BOOKMARKS, so GET /api/bookmarks lists it last.")
r2 = cc.post("/add", form={"title": "Second", "url": "http://example.org"})
r2.expect_status(201)
expect(r2.json()["id"] != made["id"], "Two bookmarks must not share an id.")

n = len(listing())
for form, word in (
    ({"title": "   ", "url": "https://x.org"}, "title"),
    ({"url": "https://x.org"}, "title"),
    ({"title": "No link", "url": "ftp://x.org"}, "url"),
    ({"title": "Script", "url": "javascript:alert(1)"}, "url"),
    ({"title": "No url"}, "url"),
):
    r = cc.post("/add", form=form)
    r.expect_status(400, why=f"The form {form} is not valid, so it should be refused with 400 Bad Request.")
    expect(word in plain(r), f"The 400 for {form} should say what is wrong - a message with the word {word}. It sent {r.snippet()}.")
expect(len(listing()) == n, "A refused form must not add a bookmark.")
'''

_C7 = r'''
def listing():
    return cc.get("/api/bookmarks").json()


r = cc.get("/api/bookmarks/2")
r.expect_status(200, why="Is there a GET route for /api/bookmarks/<int:bookmark_id>?")
expect(r.expect_json() == {"id": 2, "title": "MDN", "url": "https://developer.mozilla.org/"},
       f"GET /api/bookmarks/2 should answer with that one bookmark, but it sent {r.snippet()}.")
cc.get("/api/bookmarks/99").expect_status(404, why="No bookmark has id 99.")
cc.get("/api/bookmarks/abc").expect_status(404, why="abc is not an id.")

r = cc.post("/api/bookmarks", json={"title": " Flask ", "url": "https://flask.palletsprojects.com/"})
r.expect_status(201, why="POST /api/bookmarks with a good JSON body creates a bookmark.")
made = r.expect_json()
expect(isinstance(made, dict) and made.get("title") == "Flask" and isinstance(made.get("id"), int),
       f"POST /api/bookmarks should answer with the new bookmark (title stripped, with an id), but it sent {r.snippet()}.")
bid = made["id"]
expect(cc.get(f"/api/bookmarks/{bid}").json() == made, "The new bookmark should be kept: GET it back by id.")

for body, why in (
    ({"title": "", "url": "https://x.org"}, "an empty title"),
    ({"title": "Nope", "url": "ftp://x.org"}, "a url that is not http(s)"),
    ([1, 2], "a JSON list instead of an object"),
):
    cc.post("/api/bookmarks", json=body).expect_status(400, why=f"A body with {why} is refused.")
cc.post("/api/bookmarks", body="{oops", headers={"Content-Type": "application/json"}).expect_status(
    400, why="A body that is not JSON at all is refused.")

new = {"title": "Flask docs", "url": "https://flask.palletsprojects.com/en/latest/"}
r = cc.put(f"/api/bookmarks/{bid}", json=new)
r.expect_status(200, why="PUT replaces a bookmark's title and url and answers with it.")
expect(r.expect_json() == {"id": bid, **new}, f"PUT should answer with the updated bookmark, but it sent {r.snippet()}.")
r = cc.put(f"/api/bookmarks/{bid}", json=new)
r.expect_status(200)
expect(r.json() == {"id": bid, **new}, "PUT twice with the same body must leave the same bookmark (it is idempotent).")
expect(cc.get(f"/api/bookmarks/{bid}").json() == {"id": bid, **new}, "The update should be kept.")
cc.put("/api/bookmarks/99", json=new).expect_status(404, why="There is no bookmark 99 to replace.")
cc.put(f"/api/bookmarks/{bid}", json={"title": "", "url": "https://x.org"}).expect_status(400)
expect(cc.get(f"/api/bookmarks/{bid}").json() == {"id": bid, **new}, "A refused PUT must not change the bookmark.")

r = cc.delete(f"/api/bookmarks/{bid}")
r.expect_status(204, why="DELETE removes it and answers 204 No Content.")
expect(r.body == b"", f"A 204 answer has no body, but it sent {r.snippet()}.")
cc.get(f"/api/bookmarks/{bid}").expect_status(404, why="It was deleted.")
cc.delete(f"/api/bookmarks/{bid}").expect_status(404, why="It is already gone.")
cc.delete("/api/bookmarks/1").expect_status(204)
expect([b["id"] for b in listing()] == [2, 3, 4], "After deleting 1 (and the one just made), ids 2, 3 and 4 are left.")
again = cc.post("/api/bookmarks", json={"title": "After", "url": "https://x.org"})
again.expect_status(201)
expect(again.json()["id"] not in (1, bid, 2, 3, 4),
       f"Ids are never given out twice, but the next bookmark got id {again.json()['id']}, which was used before.")
'''

_C8 = r'''
import re

r = cc.get("/nowhere")
r.expect_status(404, why="An unknown path is 404 Not Found.")
r.expect_type("text/html")
expect("Page not found" in r.text, f"The 404 page should say Page not found, but it sent {r.snippet()}.")
expect("/nowhere" in r.text, "The 404 page should show the path that was asked for: /nowhere.")
expect(re.search(r"""href=["']/["']""", r.text), "The 404 page should link back to the home page: <a href=\"/\">.")

r = cc.get("/%3Cb%3Ex%3C/b%3E")
r.expect_status(404)
expect("<b>x</b>" not in r.text,
       "The asked-for path <b>x</b> was put into the 404 page as real HTML. Paths come from whoever types the "
       "address, so they must be escaped.")
expect("&lt;b&gt;x&lt;/b&gt;" in r.text, "The path <b>x</b> should show escaped, as &lt;b&gt;x&lt;/b&gt;.")

for path in ("/api/nothing", "/api/bookmarks/99"):
    r = cc.get(path)
    r.expect_status(404)
    r.expect_type("application/json")
    expect(r.json() == {"error": "not found"}, f"GET {path}: a 404 under /api/ should be the JSON {{\"error\": \"not found\"}}, not {r.snippet()}.")

for code in (200, 201, 404, 418, 500):
    r = cc.get(f"/status/{code}")
    expect(r.status == code, f"GET /status/{code} should answer with status {code}, but it returned {r.status}.")
    expect(f"Status {code}" in r.text, f"GET /status/{code} should say Status {code}, but it sent {r.snippet()}.")
r = cc.get("/status/204")
expect(r.status == 204 and r.body == b"", "GET /status/204 should be 204 No Content with nothing in the body.")
for code in (99, 600, 1000):
    cc.get(f"/status/{code}").expect_status(400, why=f"{code} is not a status from 200 to 599.")
cc.get("/hello/Ada").expect_status(200, why="/hello/Ada should still work.")
'''

_C9 = r'''
from urllib.parse import urlsplit

r = cc.post("/add", form={"title": "Flask docs", "url": "https://flask.palletsprojects.com/"})
r.expect_status(303, why="After a good POST answer 303 See Other with a Location header, "
                         "so a refresh cannot send the form again.")
expect(r.location and urlsplit(r.location).path == "/bookmarks",
       f"The Location header should point to /bookmarks, but it is {r.location!r}.")
page = cc.follow(r)
page.expect_status(200)
expect("Flask docs" in page.text, "Following the redirect should show the /bookmarks page, with the new title in it.")
cc.follow(r)
cc.follow(r)
n = len(cc.get("/api/bookmarks").json())
expect(n == 5, f"Asking for the page again must not add anything: there should be 5 bookmarks, but there are {n}.")

bad = cc.post("/add", form={"title": "", "url": "https://x.org"})
bad.expect_status(400, why="A bad form is still refused with 400, not redirected.")
expect(bad.location is None, "A refused form must not redirect.")
cc.post("/api/bookmarks", json={"title": "Api one", "url": "https://x.org"}).expect_status(
    201, why="The JSON API still answers 201.")
'''

_C10 = r'''
import re


def count(r):
    found = re.search(r"Visits: (\d+)", r.text)
    return int(found.group(1)) if found else None


cc.jar = True
cc.cookies.clear()
for want in (1, 2, 3):
    r = cc.get("/visits")
    r.expect_status(200, why="Is there a route for /visits?")
    expect(count(r) == want,
           f"Visit number {want} from the same browser should say Visits: {want}, but it sent {r.snippet()}. "
           "The count has to come back to the app in the cookie it set.")
    c = r.cookie("visits")
    expect(c is not None and c["value"] == str(want),
           f"The answer should set the cookie visits to {want} (a Set-Cookie header), but it set {r.cookies}.")
    expect(c["httponly"], "The cookie should be marked httponly=True, so a page's JavaScript cannot read it.")

cc.cookies.clear()
r = cc.get("/visits")
expect(count(r) == 1,
       f"A different browser (no cookie) should start at Visits: 1, but it got {r.snippet()}. "
       "Is the count in a variable the whole server shares, instead of in each browser's cookie?")

cc.jar = False
for sent, want in (("41", 42), ("abc", 1), ("", 1), ("-5", 1)):
    r = cc.get("/visits", cookies={"visits": sent})
    r.expect_status(200, why=f"A cookie visits={sent!r} should not crash the app.")
    expect(count(r) == want, f"With the cookie visits={sent!r} the page should say Visits: {want}, but it sent {r.snippet()}.")
'''

_C11 = r'''
def login(user, password):
    return cc.post("/login", form={"user": user, "password": password})


cc.jar = True
cc.cookies.clear()
cc.get("/me").expect_status(401, why="Nobody is logged in yet.")
cc.get("/admin").expect_status(401, why="Nobody is logged in yet.")

for user, password in (("ada", "wrong"), ("nobody", "x"), ("ada", "")):
    r = login(user, password)
    r.expect_status(401, why=f"{user!r} with the password {password!r} must not get in.")
    expect(not r.cookies.get("session"), "A failed login must not hand out a session cookie.")
expect(cc.post("/login", form={"user": "ada"}).status == 401, "A login without a password must be 401.")
cc.get("/me").expect_status(401, why="The failed logins must not have logged anyone in.")

r = login("ada", "lovelace")
r.expect_status(303, why="A good login answers 303 and sends the browser on (to /me).")
c = r.cookie("session")
expect(c is not None, "A good login should set a cookie called session.")
expect(c["httponly"], "The session cookie should be httponly.")
token = c["value"]
expect(token != "ada" and len(token) >= 16,
       f"The cookie should hold a long random token (secrets.token_hex), not the username - it holds {token!r}.")
page = cc.follow(r)
page.expect_status(200)
expect("ada" in page.text, f"Following the redirect (to /me) should say who you are, but it sent {page.snippet()}.")
me = cc.get("/me")
me.expect_status(200)
expect("ada" in me.text, f"/me should say ada, but it sent {me.snippet()}.")
cc.get("/admin").expect_status(200, why="ada is an admin.")
expect("Admin area" in cc.get("/admin").text, "/admin should say Admin area.")

cc.jar = False
for fake in ("ada", "admin", "0" * 32, "x"):
    cc.get("/me", cookies={"session": fake}).expect_status(
        401, why=f"A cookie session={fake!r} was never handed out by the server. Never trust what the browser says.")
cc.get("/me", cookies={"session": token}).expect_status(200, why="The real token works without anything else.")

cc.jar = True
cc.cookies.clear()
r = login("bob", "builder")
r.expect_status(303)
expect("bob" in cc.follow(r).text, "bob should be able to log in too.")
cc.get("/me").expect_status(200)
cc.get("/admin").expect_status(403, why="bob is logged in but is not an admin: 403 Forbidden (not 401).")

cc.cookies.clear()
second = login("ada", "lovelace").cookie("session")["value"]
expect(second != token, "Every login needs a new token.")
r = cc.post("/logout")
r.expect_status(303, why="Logout answers 303 and sends the browser home.")
expect("session" not in cc.cookies, "Logout should delete the session cookie (response.delete_cookie).")
cc.get("/me").expect_status(401, why="Logged out.")
cc.get("/me", cookies={"session": second}).expect_status(
    401, why="A token that was logged out must stop working even if someone kept a copy: forget it on the server.")
'''

# -- the steps -----------------------------------------------------------------------------

PYWEBAPP_STEPS: tuple[Step, ...] = (
    Step(
        id="pywa-01-hello",
        title="A route that answers",
        teaches=(
            "A web app is a program that waits. A browser sends a request - the method GET and a path, like "
            "GET / - and the app sends back a response: a status, some headers and a body. You write the part "
            "in the middle: a function that returns the body. Code Coach starts a real server for your program "
            "and gives you `app` to hang functions on.\n\n"
            "`@app.get(\"/\")` is a decorator: a line starting with @ above a def. It is nothing magic. This "
            "toy does the same job:\n\n"
            "    routes = {}\n"
            "    def get(path):\n"
            "        def remember(function):\n"
            "            routes[path] = function\n"
            "            return function\n"
            "        return remember\n\n"
            "Writing `@get(\"/\")` above `def home()` means `home = get(\"/\")(home)`: the decorator files the "
            "function in a table under its path and hands it back unchanged. When a request for / arrives, the "
            "server looks the path up and calls the function; what it returns is the page. Use the Try it panel "
            "to send GET / to your app and read the whole response."
        ),
        goal="Add a route for `GET /` whose function returns the text `Link Saver`.",
        starter=_STARTER_1,
        solution=_S1,
        check=_C1,
        hint='@app.get("/")\ndef home():\n    return "Link Saver"',
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-02-params",
        title="Parts of the path",
        teaches=(
            "A path can carry information. In `/hello/<name>` the <name> is a hole: whatever stands in that "
            "place of the address - /hello/Ada, /hello/Grace - is handed to your function as a parameter of the "
            "same name. A route function is just a function, so build the answer with an f-string: "
            "f\"Hello, {name}!\" puts the value of name between the quotes.\n\n"
            "Addresses cannot contain spaces or most symbols, so a browser writes them as %XX codes: a space is "
            "%20, so /hello/Grace%20Hopper reaches your function as the name \"Grace Hopper\". The library "
            "decodes it for you. A hole matches one piece between slashes and never an empty one, so /hello/ has "
            "no name and no route: the server answers 404 Not Found by itself. If the name in the route and the "
            "name of the parameter differ, the program stops with an error that says so."
        ),
        goal=(
            "Add `GET /hello/<name>`, which answers `Hello, ` then the name, then `!` - so `/hello/Ada` "
            "answers `Hello, Ada!` and `/hello/Grace%20Hopper` answers `Hello, Grace Hopper!`."
        ),
        starter=_S1,
        solution=_S2,
        check=_C2,
        hint='@app.get("/hello/<name>")\ndef hello(name):\n    return f"Hello, {name}!"',
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-03-query",
        title="The query string",
        teaches=(
            "After a ? an address can carry a query string: /search?q=py&q=mdn is two pairs, q=py and q=mdn. "
            "The same name may appear twice. `request.args` is a dict with the FIRST value of each name - "
            "`request.args.get(\"q\", \"\")` - and `request.args_all` is a dict of lists with all of them: "
            "{\"q\": [\"py\", \"mdn\"]}. dict.get(key, default) gives the default instead of an error when a "
            "visitor leaves a name out; never trust that a parameter is there.\n\n"
            "Python to lean on: str.lower() to ignore capitals, `in` to test for a piece of text, any(...) for "
            "'does at least one of these hold', a list comprehension to filter, and \"\\n\".join(list) to "
            "put one item on each line. The body is plain text, so say so in the headers: a route may return "
            "a tuple (body, status, headers) - here (text, 200, {\"Content-Type\": \"text/plain\"}). The "
            "Content-Type header tells the browser what the bytes are; without it a str is sent as HTML."
        ),
        goal=(
            "Add `BOOKMARKS` (the four bookmarks in the hint) and `GET /search`, which answers with the title of "
            "every bookmark whose title contains any of the `q` values (ignoring capitals), one title per line "
            "in the order of `BOOKMARKS`, as `text/plain`. With no `q`, every title matches: `/search?q=py` "
            "answers `Python docs` and `PyPI`, and `/search?q=py&q=mdn` adds `MDN`."
        ),
        starter=_S2,
        solution=_S3,
        check=_C3,
        hint=(
            "BOOKMARKS = [\n"
            '    {"id": 1, "title": "Python docs", "url": "https://docs.python.org/3/"},\n'
            '    {"id": 2, "title": "MDN", "url": "https://developer.mozilla.org/"},\n'
            '    {"id": 3, "title": "PyPI", "url": "https://pypi.org/"},\n'
            '    {"id": 4, "title": "Fish & <chips>", "url": "https://example.com/fish?a=1&b=2"},\n'
            "]\n\n"
            'wanted = request.args_all.get("q", [""])   # every q, or one empty q\n'
            'return "\\n".join(titles), 200, {"Content-Type": "text/plain"}'
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-04-html",
        title="HTML, and why to escape",
        teaches=(
            "A str that a route returns is sent as HTML, which a browser draws. HTML puts text and markup in "
            "one string, and that is a danger: a title like Fish & <chips> contains characters that mean "
            "something in HTML. Dropped in raw, <chips> becomes a (made-up) tag and the word vanishes - and if "
            "the title were <script>steal()</script>, the browser would RUN it, in every visitor's page. That "
            "is cross-site scripting, XSS, and it comes from any text you did not write yourself.\n\n"
            "The fix is to escape: < > & and quotes are replaced by entities (&lt; &gt; &amp; &quot;) that display "
            "as the character without acting as markup. `render(template, **values)` fills a $name template and "
            "escapes every value for you. A piece you built yourself that is already safe HTML - the joined "
            "rows - is wrapped in safe(...) so it is not escaped twice. Open the Rendered tab in Try it: the "
            "<chips> title should be visible text. Also try your page with the escaping removed."
        ),
        goal=(
            "Add `GET /bookmarks`: an HTML page with an `<h1>` and one `<li>` per bookmark, each holding a link "
            "(`<a href=\"...\">`) to its url with its title as the text. Escape titles and urls: the title "
            "`Fish & <chips>` must be in the HTML as `Fish &amp; &lt;chips&gt;`, never as a `<chips>` tag."
        ),
        starter=_S3,
        solution=_S4,
        check=_C4,
        hint=(
            "ROW = '<li><a href=\"$url\">$title</a></li>'\n"
            'PAGE = "<h1>Bookmarks</h1><ul>$rows</ul>"\n\n'
            'rows = "".join(render(ROW, **b) for b in BOOKMARKS)\n'
            "return render(PAGE, rows=safe(rows))"
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-05-json",
        title="JSON for programs",
        teaches=(
            "Pages are for people; programs talk in JSON. A Python dict or list maps straight onto it: dict "
            "-> {\"id\": 1}, list -> [...], str, int, bool and None -> \"x\", 1, true, null. A route that returns "
            "a dict or a list gets it sent as JSON automatically, with the header Content-Type: "
            "application/json - the header is how the receiver knows to parse it instead of drawing it.\n\n"
            "The classic mistake is to send the right text with the wrong label: str(my_list) or a hand-made "
            "json.dumps string is returned as text/html, and a client that looks at the header will not treat "
            "it as JSON (str(...) is not even valid JSON: Python writes single quotes). The other mistake is "
            "to escape: JSON is not HTML, and the title Fish & <chips> must travel as it is. Escaping belongs "
            "to the place where text meets HTML, nowhere else. In Try it, look at the headers table as well as "
            "the body."
        ),
        goal=(
            "Add `GET /api/bookmarks`, which answers with `BOOKMARKS` as JSON - a list of `{id, title, url}` "
            "objects, exactly as stored, with the content type `application/json`."
        ),
        starter=_S4,
        solution=_S5,
        check=_C5,
        hint='@app.get("/api/bookmarks")\ndef api_list():\n    return BOOKMARKS',
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-06-form",
        title="POST a form",
        teaches=(
            "GET asks for something and must change nothing. To change something - save a bookmark - a browser "
            "uses POST, and sends the data in the body of the request. An HTML form posts its fields as "
            "title=Flask+docs&url=https%3A%2F%2F..., which the library parses into the dict `request.form`. "
            "Use Try it: choose POST, path /add, the 'form' body, and one field per line.\n\n"
            "Never trust a form. Check it: str.strip() removes spaces around a title, and url.startswith"
            "((\"http://\", \"https://\")) refuses a javascript: link that would run code when someone clicks. "
            "A bad request is the sender's fault, so the status is in the 4xx family: 400 Bad Request, with a "
            "message, and nothing is saved. abort(400, message) stops the function right there. A good one is "
            "201 Created: `return thing, 201` sends a body AND a status.\n\n"
            "State lives in module-level variables, which survive between requests. Changing a list in place "
            "(BOOKMARKS.append(x)) needs nothing special, but re-assigning a number (NEXT_ID += 1) inside a "
            "function needs `global NEXT_ID` - or Python thinks it is a new local variable and crashes."
        ),
        goal=(
            "Add `POST /add`, which reads the form fields `title` and `url` (both `strip()`ped). If the title is "
            "empty or the url does not start with `http://` or `https://`, nothing is saved and it answers `400` "
            "with a message containing the word `title` or `url` for what is wrong. Otherwise it appends "
            "`{\"id\", \"title\", \"url\"}` to `BOOKMARKS` with a new id (5 for the first one) and answers `201` "
            "with that bookmark as JSON."
        ),
        starter=_S5,
        solution=_S6,
        check=_C6,
        hint=(
            "message = problem(title, url)   # None, or text saying what is wrong\n"
            "if message:\n"
            "    abort(400, message)\n"
            "return add_bookmark(title, url), 201\n\n"
            "# in add_bookmark: global NEXT_ID (it re-assigns the number)"
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-07-api",
        title="A JSON API",
        teaches=(
            "A small API is the same path used with different methods: GET /api/bookmarks/2 reads one, "
            "POST /api/bookmarks creates, PUT replaces, DELETE removes. The method is the verb, the path is the "
            "noun. Some are safe to repeat and some are not: GET changes nothing; PUT and DELETE are idempotent "
            "(doing them twice leaves the same result as once); POST is not (twice creates two). That is why a "
            "network can retry a PUT but must be careful with a POST.\n\n"
            "`<int:bookmark_id>` in a route matches digits only and hands you a real int - so /api/bookmarks/abc "
            "has no route at all (404). `request.json` is the parsed JSON body; a body that is not valid "
            "JSON makes the library answer 400 itself, but a valid body can still be the wrong shape (a list, "
            "not an object), so check it. A missing thing is 404 Not Found; a successful DELETE has nothing to "
            "say, so 204 No Content - and a 204 has no body. Return `\"\", 204`.\n\n"
            "Ids must never be handed out twice. max(ids) + 1 or len(list) + 1 repeats an id once the "
            "last bookmark is deleted: that is why NEXT_ID is a counter that only goes up."
        ),
        goal=(
            "Add the JSON API. `GET /api/bookmarks/<int:bookmark_id>` answers one bookmark; `POST /api/bookmarks` "
            "takes a JSON body `{\"title\", \"url\"}` and works like `/add` (201 and the new bookmark, 400 and a "
            "message for a bad title or url, or a body that is not an object); `PUT /api/bookmarks/<int:bookmark_id>` "
            "replaces that bookmark's title and url the same way (200 and the bookmark); `DELETE "
            "/api/bookmarks/<int:bookmark_id>` removes it and answers `204` with no body. An id that does not "
            "exist is `404` for GET, PUT and DELETE. An id is never given out twice, even after a delete."
        ),
        starter=_S6,
        solution=_S7,
        check=_C7,
        hint=(
            "def find(bookmark_id):\n"
            "    ...loop over BOOKMARKS...\n"
            '    abort(404, "No bookmark with that id.")\n\n'
            "# PUT: bookmark = find(id); change its title and url; return bookmark\n"
            '# DELETE: BOOKMARKS.remove(find(id)); return "", 204'
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-08-status",
        title="Status codes and a 404 page",
        teaches=(
            "The first digit of a status code is its family: 2xx it worked (200 OK, 201 Created, 204 No "
            "Content), 3xx go somewhere else, 4xx the request was wrong - the client's fault (400 Bad Request, "
            "401 Unauthorized, 403 Forbidden, 404 Not Found, 405 Method Not Allowed) - and 5xx the server broke "
            "(500). `return body, code` sets any of them. A client reads the status first; the text is for people.\n\n"
            "Your own error pages hang on `@app.errorhandler(404)`: a function that receives the error and "
            "returns like a route does. Careful - it returns a page, and a page is 200 OK unless you say "
            "otherwise, so return `(page, 404)`. A pretty page with status 200 is a 'soft 404': search engines "
            "and programs think it exists.\n\n"
            "And one more escaping lesson: the 404 page shows the path the visitor asked for. Anyone can type "
            "/<script>... into an address bar, or send a link containing it, so that path is untrusted text "
            "too. Escape it like a title."
        ),
        goal=(
            "Add `@app.errorhandler(404)`: a path under `/api/` answers `404` with the JSON "
            "`{\"error\": \"not found\"}`; any other unknown path answers `404` with an HTML page that says "
            "`Page not found`, shows the (escaped) path that was asked for, and links back with `<a href=\"/\">`. "
            "Also add `GET /status/<int:code>`, which answers with that status code and the text `Status <code>` "
            "for codes 200 to 599 (anything else is a `400`)."
        ),
        starter=_S7,
        solution=_S8,
        check=_C8,
        hint=(
            "@app.errorhandler(404)\n"
            "def not_found(error):\n"
            '    if request.path.startswith("/api/"):\n'
            '        return {"error": "not found"}, 404\n'
            "    return render(NOT_FOUND, path=request.path), 404   # 404 again, or it is a 200"
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-09-redirect",
        title="Redirect after POST",
        teaches=(
            "Press refresh on a page that came from a POST and the browser asks 'send the form again?'. That "
            "is how people buy something twice. The cure is the redirect-after-POST pattern: after a successful "
            "POST, do not draw a page - answer with a redirect, a 3xx status plus a Location header, and the "
            "browser makes a fresh GET to that address. Refreshing now repeats the harmless GET.\n\n"
            "Which 3xx? 301 and 308 are permanent moves; 302 is 'temporary' and, historically, ambiguous about "
            "whether a POST becomes a GET; 307 and 308 keep the method and body as they were; 303 See Other "
            "says exactly what you want here: now GET that other address. `redirect(\"/bookmarks\", 303)` builds "
            "the response. The check follows the Location itself, like a browser, one hop at a time. In Try "
            "it, the Follow button does the same; a redirect is never followed for you, so you can see it.\n\n"
            "Do the saving BEFORE you return the redirect - a return ends the function. And a bad form is still a "
            "400 with its message: redirecting an error would hide it."
        ),
        goal=(
            "Change `POST /add`: when the form is valid, save the bookmark and answer `303 See Other` with the "
            "header `Location: /bookmarks` instead of the 201 JSON. Following the redirect shows the "
            "`/bookmarks` page with the new title; asking for that page again does not add another copy. A bad "
            "form is still `400`, and `POST /api/bookmarks` still answers `201`."
        ),
        starter=_S8,
        solution=_S9,
        check=_C9,
        hint='add_bookmark(title, url)\nreturn redirect("/bookmarks", 303)',
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-10-cookies",
        title="Cookies",
        teaches=(
            "HTTP forgets. Every request arrives as if it were the first, so an app that wants to recognise a "
            "visitor asks the browser to carry a note: the response has a header Set-Cookie: visits=3, and from "
            "then on the browser adds Cookie: visits=3 to every request to this app. In the library the note you "
            "read is the dict `request.cookies`, and the note you leave is `response.set_cookie(name, value)` - "
            "so a route that sets one returns a Response object, not just a string: "
            "`response = Response(text)`, then `response.set_cookie(...)`, then `return response`.\n\n"
            "Two things follow. A cookie lives in the browser, so it can be missing, empty or edited by the "
            "visitor to anything at all (\"abc\", \"-5\") - read it defensively: str.isdigit() says whether text "
            "is a whole number before int() blows up on it. And a count in a cookie is per browser, where a "
            "count in a variable on the server would be shared by everybody. The httponly option hides the cookie "
            "from the page's JavaScript. Try it keeps cookies like a browser would: send /visits a few times."
        ),
        goal=(
            "Add `GET /visits`: read the cookie `visits` (missing or not a whole number counts as 0), add one, "
            "answer `Visits: N`, and set the cookie `visits` to N with `httponly=True`. Each browser counts "
            "for itself."
        ),
        starter=_S9,
        solution=_S10,
        check=_C10,
        hint=(
            'raw = request.cookies.get("visits", "")\n'
            "count = int(raw) if raw.isdigit() else 0\n"
            "...\n"
            'response = Response(f"Visits: {count + 1}")\n'
            'response.set_cookie("visits", str(count + 1), httponly=True)\n'
            "return response"
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-11-login",
        title="Logging in",
        teaches=(
            "Cookies make logins. The visitor posts a username and password; if they are right, the app makes "
            "up a long random token, remembers on the SERVER which user it belongs to (the dict SESSIONS), and "
            "puts only the token in the cookie. Later requests bring the token back and the app looks it up.\n\n"
            "Why not just put the username in the cookie? Because the cookie is the visitor's to edit: anyone "
            "could type session=ada and be ada. The server must only believe a token it handed out itself - and "
            "must make it unguessable: secrets.token_hex(16) is 32 random hex digits. Logging out means "
            "forgetting the token on the server too (SESSIONS.pop), not just deleting the cookie, because someone "
            "may have kept a copy.\n\n"
            "Two different refusals: 401 Unauthorized really means 'I don't know who you are' (not logged "
            "in), and 403 Forbidden means 'I know who you are, and you may not'. Passwords here sit in a dict "
            "to keep the lesson small; a real app stores only hashes."
        ),
        goal=(
            "Add a login. `USERS` = {`ada`: `lovelace`, `bob`: `builder`}, and only ada is an admin. `POST /login` "
            "(form fields `user` and `password`): wrong or missing credentials are `401` with no cookie; right ones "
            "set the `httponly` cookie `session` to a new random token (at least 16 characters, never the "
            "username) and answer `303` to `/me`. `GET /me` answers `You are <user>.`, or `401` if the cookie "
            "is not a token you handed out. `GET /admin` is `401` when nobody is logged in, `403` for bob, and "
            "`Admin area` for ada. `POST /logout` forgets the token on the server, deletes the cookie and "
            "answers `303` to `/`."
        ),
        starter=_S10,
        solution=_S11,
        check=_C11,
        hint=(
            "token = secrets.token_hex(16)\n"
            "SESSIONS[token] = user            # the server remembers who it is\n"
            "response = redirect(\"/me\", 303)\n"
            'response.set_cookie("session", token, httponly=True)\n'
            "return response\n\n"
            '# who is it: SESSIONS.get(request.cookies.get("session", ""))'
        ),
        track=TRACK,
        language="python",
        surface="web",
    ),
    Step(
        id="pywa-12-yours",
        title="Make it yours",
        teaches=(
            "Link Saver now has every part a small web app has: routes with parameters, a query string, HTML "
            "that is escaped, a JSON API with state, status codes and an error page, a redirect after POST, "
            "cookies and a login. Everything else - a framework like Flask or Django, a database, templates in "
            "files, forms in the browser - is these same ideas with more machinery around them. Nothing is "
            "checked from here: use Run and the Try it panel and see what you can build."
        ),
        goal=(
            "Make it yours. Ideas: show `/bookmarks` only to logged-in users; give each bookmark `tags` and add "
            "`/search?tag=`; a `/bookmarks/<int:id>/delete` form that POSTs and redirects; a visit counter "
            "per user; JSON errors with a `message`; keep the bookmarks in a file so a restart does not lose them."
        ),
        starter=_S11,
        solution=_S11,
        check="",
        track=TRACK,
        language="python",
        surface="web",
    ),
)
