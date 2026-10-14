"""Pages 352-361: Python, web servers and HTTP.

What happens between a browser and a program, taken apart: the URL and its
query string, the status codes and reasons, the headers, the raw request and
the raw response, a router, a small server that answers GET and POST and
says no with a 404 or a 405, JSON in and out, cookies, a WSGI app, and
templates that turn a list into a page. It is the Python counterpart of the
JavaScript Node pages (246-247), spread over ten pages and kept honest: the
first half needs no server at all, and the servers that appear are asked by
the same program that starts them.

Everything runs as plain `python file.py` with no arguments and no network
beyond 127.0.0.1. A server binds port 0 and runs in a daemon thread, so no
port is ever fixed or printed. A raw request is a string, a response is
built from a dict, and a WSGI app is called as a function, so none of those
needs a socket.

Routing and the 404/405 handling share a page with the GET routes (the list
asked for ten, and the two are one idea: a path that is not there, and a
path that is there for another method), so the set is ten pages for eleven
topics.

Python only, numbered after page 351, the last of the Python book before the
review pages. The review pages are numbered from whatever comes last, so this
tuple has to be registered before them and they move up by ten.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PYTHON = ("python",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=PYTHON,
        tier="intermediate",
    )


def _and(words) -> str:
    words = [str(w) for w in words]
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _then(words) -> str:
    return ", then ".join(str(w) for w in words)


def _quoted(words) -> str:
    return _and(f"'{w}'" for w in words)


# ── 352. URLs ────────────────────────────────────────────────

_URLS = (
    ("part", {"url": "https://example.com/docs/intro?lang=en#top", "part": "netloc"}),
    ("part", {"url": "http://example.com/shop/cart/checkout?step=2", "part": "path"}),
    ("part", {"url": "https://news.example.org/story?id=42&ref=home#comments", "part": "query"}),
    ("part", {"url": "https://example.com/about", "part": "fragment"}),
    ("part", {"url": "ftp://files.example.net/pub/readme.txt", "part": "scheme"}),
    ("port", {"url": "http://example.com:8080/api"}),
    ("port", {"url": "https://Example.COM/index"}),
    ("qs", {"query": "name=Ada&lang=en&lang=fr", "show": "dict"}),
    ("qs", {"query": "q=hello+world%21&page=2", "show": "first", "key": "q"}),
    ("qs", {"query": "tag=a&tag=b&tag=c&n=1", "show": "all", "key": "tag"}),
    ("qs", {"query": "a=1&b=&c=3", "show": "dict"}),
    ("quote", {"text": "a b/c"}),
    ("quote", {"text": "café menu"}),
    ("quote", {"text": "docs/a b&c", "safe": ""}),
    ("urlencode", {"params": [("q", "python web"), ("page", 2)]}),
    ("urlencode", {"params": [("name", "José"), ("tag", "a&b")]}),
    ("urlencode", {"params": [("tag", ["a", "b"]), ("page", 1)], "doseq": True}),
    ("join", {"base": "https://example.com/a/b/c.html", "ref": "d.html"}),
    ("join", {"base": "https://example.com/a/b/c.html", "ref": "../d.html"}),
    ("join", {"base": "https://example.com/a/b/c.html", "ref": "/x/y"}),
    ("join", {"base": "https://example.com/a/b/c.html?x=1#f", "ref": "?page=2"}),
    ("join", {"base": "https://example.com/docs/guide.html?lang=en", "ref": "#top"}),
)


def _url_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "part":
        return (f"Split the URL {a['url']} with urlsplit and print its {a['part']}, "
                f"or the word none when it is empty.", args)
    if want == "port":
        return (f"Split the URL {a['url']} with urlsplit and print its hostname, a "
                f"space and its port.", args)
    if want == "qs":
        q = a["query"]
        if a["show"] == "dict":
            return (f"Parse the query string {q} with parse_qs and print the "
                    f"dictionary it gives back.", args)
        if a["show"] == "first":
            return (f"Parse the query string {q} with parse_qs and print the first "
                    f"value of {a['key']}.", args)
        return (f"Parse the query string {q} with parse_qs and print the list of "
                f"values for {a['key']}.", args)
    if want == "quote":
        if a.get("safe") == "":
            return (f"Percent-encode the text '{a['text']}' with quote, telling it "
                    f"that no character is safe so that the slashes are encoded "
                    f"too, and print the result.", args)
        return f"Percent-encode the text '{a['text']}' with quote and print the result.", args
    if want == "urlencode":
        things = _and(
            f"{k} as the list {_and(v)}" if isinstance(v, list) else f"{k} as {v}"
            for k, v in a["params"])
        how = (" with the lists spread into one pair for each value"
               if a.get("doseq") else "")
        return (f"Build a query string with urlencode from a dictionary with "
                f"{things}{how}, and print it.", args)
    return (f"Resolve the reference {a['ref']} against the base URL {a['base']} "
            f"with urljoin and print the result.", args)


URL_PAGE = _page(
    "py-web-url", 352, "Web: URLs with urllib.parse",
    "urllib.parse takes a URL apart and puts one together. urlsplit(url) "
    "gives scheme, netloc (the host and any port), path, query and fragment "
    "(the part after #, which a browser never sends to the server), and "
    "parts.hostname and parts.port read the netloc: the hostname is lower "
    "case and the port is a number, or None when the URL gives none. "
    "parse_qs(query) gives a dictionary of lists, because a name may repeat, "
    "with %20 and + decoded to spaces, and it silently drops a parameter "
    "with no value. quote(text) writes every unsafe byte as %XX using the "
    "UTF-8 bytes, so é is %C3%A9, and it leaves slashes alone unless you pass "
    "safe=''. urlencode(dict) joins name=value pairs with &, turns spaces "
    "into +, and with doseq=True spreads a list into one pair per item. "
    "urljoin(base, ref) resolves a link the way a browser does: a bare name "
    "replaces the last piece of the base path, .. climbs one folder, a path "
    "starting with / replaces the whole path, ?query keeps the path and swaps "
    "the query, and #fragment keeps both.",
    "from urllib.parse import urlsplit, parse_qs, urlencode, urljoin; "
    "urlsplit('https://example.com/a?x=1#top') has netloc example.com, path "
    "/a, query x=1 and fragment top; parse_qs('x=1&x=2') is {'x': ['1', '2']}; "
    "urlencode({'q': 'a b'}) is q=a+b; urljoin('https://example.com/a/b.html', "
    "'../c.html') is https://example.com/c.html",
    "py_web_url",
    tuple(_url_row(row) for row in _URLS),
)


# ── 353. Status codes ────────────────────────────────────────

_MEMBER = {
    201: "CREATED", 301: "MOVED_PERMANENTLY", 403: "FORBIDDEN", 404: "NOT_FOUND",
    429: "TOO_MANY_REQUESTS", 500: "INTERNAL_SERVER_ERROR",
}

_STATUSES = (
    ("value", {"code": 404}),
    ("value", {"code": 201}),
    ("value", {"code": 500}),
    ("phrase", {"code": 404}),
    ("phrase", {"code": 301}),
    ("phrase", {"code": 503}),
    ("name", {"code": 403}),
    ("name", {"code": 429}),
    ("line", {"code": 201}),
    ("line", {"code": 405}),
    ("lookup", {"codes": [200, 404, 500]}),
    ("lookup", {"codes": [301, 403, 502, 204]}),
    ("classify", {"codes": [200, 404, 503]}),
    ("classify", {"codes": [101, 301, 500, 201]}),
    ("classify", {"codes": [404, 308, 204, 502, 100]}),
    ("count", {"codes": [200, 301, 404, 500, 302], "klass": 3}),
    ("count", {"codes": [200, 404, 403, 500, 410], "klass": 4}),
    ("retry", {"codes": [200, 429, 404, 503]}),
    ("retry", {"codes": [500, 301, 401, 502, 429]}),
    ("retry", {"codes": [201, 503, 404, 504, 429, 200]}),
)

_CLASSES = {1: "1xx", 2: "2xx", 3: "3xx", 4: "4xx", 5: "5xx"}


def _status_row(row):
    want, a = row
    args = {"want": want, **a}
    code = a.get("code")
    if want == "value":
        return (f"Print the number of the HTTPStatus member called "
                f"{_MEMBER[code]}.", args)
    if want == "phrase":
        return f"Print the reason phrase of the HTTP status {code}.", args
    if want == "name":
        return f"Print the name of the HTTPStatus member for the status {code}.", args
    if want == "line":
        return (f"Print the HTTP status {code} as its number, a space and its "
                f"reason phrase.", args)
    codes = _and(a["codes"])
    if want == "lookup":
        return (f"For each of the status codes {codes}, in that order, print the "
                f"code, a space and its reason phrase.", args)
    if want == "classify":
        return (f"Write a function that sorts a status code into informational "
                f"(1xx), success (2xx), redirection (3xx), client error (4xx) or "
                f"server error (5xx). For each of the codes {codes}, in that "
                f"order, print the code, a space and its class.", args)
    if want == "count":
        return (f"Print how many of the status codes {codes} are in the "
                f"{_CLASSES[a['klass']]} class.", args)
    return (f"A client should try again on a 429 and on any 5xx code. Print the "
            f"list of the codes in {codes} that are worth another try.", args)


STATUS_PAGE = _page(
    "py-web-status", 353, "Web: status codes and reasons",
    "The first line of every HTTP response is the status code, a number, "
    "and a reason phrase, such as 404 Not Found. The first digit is the "
    "class: 1xx informational, 2xx success, 3xx redirection (the client "
    "should look somewhere else), 4xx the client got it wrong, and 5xx the "
    "server did. http.HTTPStatus lists the standard ones: HTTPStatus(404) "
    "finds the member from the number, and each member has .value (404), "
    ".phrase ('Not Found') and .name ('NOT_FOUND', the phrase in capitals "
    "with underscores), and HTTPStatus.NOT_FOUND finds it from the name. "
    "Integer division by 100 gives the class, so code // 100 is 4 for any "
    "4xx, which makes a short classifier an index into a list. Codes worth "
    "retrying are the ones that say the server is struggling, not that the "
    "request was wrong: 429 Too Many Requests and 5xx.",
    "from http import HTTPStatus; HTTPStatus(404).phrase is 'Not Found', "
    "HTTPStatus.NOT_FOUND.value is 404 and HTTPStatus(404).name is 'NOT_FOUND'; "
    "['informational', 'success', 'redirection', 'client error', 'server "
    "error'][404 // 100 - 1] is 'client error'",
    "py_web_status",
    tuple(_status_row(row) for row in _STATUSES),
)


# ── 354. Headers and content types ───────────────────────────

_TYPES = [("html", "text/html"), ("css", "text/css"), ("json", "application/json"),
          ("png", "image/png")]

_HEADERS = (
    ("statusline", {"code": 200}),
    ("statusline", {"code": 404}),
    ("statusline", {"code": 500}),
    ("length", {"body": "hello world"}),
    ("length", {"body": "café"}),
    ("length", {"body": "日本"}),
    ("ctype", {"types": _TYPES, "name": "style.css"}),
    ("ctype", {"types": _TYPES, "name": "index.html", "charset": True}),
    ("ctype", {"types": _TYPES, "name": "photo.PNG"}),
    ("ctype", {"types": _TYPES, "name": "archive.zip", "charset": True}),
    ("lookup", {"headers": [("Content-Type", "text/html"), ("X-Mood", "calm")],
                "ask": "content-type"}),
    ("lookup", {"headers": [("Accept", "text/plain"), ("User-Agent", "curl")],
                "ask": "user-agent"}),
    ("lookup", {"headers": [("Cache-Control", "no-cache"), ("ETag", "abc123"),
                            ("Content-Length", "42")], "ask": "etag"}),
    ("mediatype", {"value": "text/html; charset=utf-8"}),
    ("mediatype", {"value": "application/json"}),
    ("mediatype", {"value": "multipart/form-data; boundary=abc; charset=ascii"}),
    ("raw", {"status": 200, "headers": [("Content-Type", "text/plain"), ("X-Mood", "calm")],
             "body": "hello"}),
    ("raw", {"status": 404, "headers": [("Content-Type", "text/html")], "body": "gone"}),
    ("rawlen", {"status": 200, "headers": [("Content-Type", "text/plain")],
                "body": "hello world"}),
    ("rawlen", {"status": 201, "headers": [("Content-Type", "text/plain"), ("X-Mood", "calm")],
                "body": "created"}),
)


def _header_text(pairs) -> str:
    return _and(f"{k} set to {v}" for k, v in pairs)


def _headers_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "statusline":
        return (f"Print the status line of an HTTP/1.1 response with the status "
                f"{a['code']}: the version, the code and the reason phrase, "
                f"separated by spaces.", args)
    if want == "length":
        return (f"Print the Content-Length header, a name, a colon, a space and the "
                f"value, for a response whose body is the text '{a['body']}' "
                f"encoded as UTF-8.", args)
    if want == "ctype":
        types = _and(f"{ext} for {kind}" for ext, kind in a["types"])
        text = (" For a text type, add a semicolon, a space and charset=utf-8."
                if a.get("charset") else "")
        return (f"A dictionary maps the extensions {types}. Print the content type "
                f"for the file {a['name']}, looking up its extension in lower case, "
                f"or application/octet-stream when the extension is not there."
                f"{text}", args)
    if want == "lookup":
        return (f"A response has the headers {_header_text(a['headers'])}. Header "
                f"names do not depend on case, so make a dictionary with the "
                f"names in lower case, and print the value of {a['ask']}.", args)
    if want == "mediatype":
        return (f"Split the Content-Type value '{a['value']}' at its first semicolon. "
                f"Print the media type, a space and the charset from its parameters, "
                f"or the word none when there is no charset.", args)
    things = _header_text(a["headers"])
    extra = (", with a Content-Length header added last that holds the length "
             "of the body" if want == "rawlen" else "")
    return (f"Build the text of an HTTP/1.1 response with the status {a['status']} "
            f"and its reason phrase, the headers {things}{extra}, and the body "
            f"'{a['body']}'. Join the status line and the header lines with "
            f"carriage return and newline, put a blank line between the headers and "
            f"the body, and print the repr of the whole text.", args)


HEADERS_PAGE = _page(
    "py-web-headers", 354, "Web: headers and content types",
    "A response is text before it is anything else. The status line is "
    "HTTP/1.1, a space, the code, a space and the reason; then one line "
    "Name: value for each header; then an empty line; then the body. Every "
    "line ends in carriage return and newline, '\\r\\n', and printing the "
    "repr of the text shows them. Content-Type says what the body is, as a "
    "media type such as text/html with optional parameters after a "
    "semicolon, as in text/html; charset=utf-8; a server picks it from the "
    "file's extension with a table, and falls back to application/octet-"
    "stream, which means 'some bytes'. Content-Length is the number of "
    "bytes of the body, not characters: len(body.encode('utf-8')), so é "
    "counts two and 日 three. Header names are not case sensitive, so look "
    "them up in a dictionary with the names lowered. str.partition(';') "
    "splits at the first semicolon and keeps the separator out; '\\r\\n'.join"
    "(lines) puts the line breaks in.",
    "lines = ['HTTP/1.1 200 OK', 'Content-Type: text/plain']; text = '\\r\\n'"
    ".join(lines) + '\\r\\n\\r\\n' + 'hi'; repr(text) shows 'HTTP/1.1 200 OK"
    "\\r\\nContent-Type: text/plain\\r\\n\\r\\nhi', and len('café'.encode()) is 5",
    "py_web_headers",
    tuple(_headers_row(row) for row in _HEADERS),
)


# ── 355. A raw request ───────────────────────────────────────

_GET = [("Host", "example.com"), ("Accept", "text/html")]
_AGENT = [("Host", "example.com"), ("User-Agent", "curl"), ("Accept", "text/html")]
_FORM = [("Host", "example.com:8080"), ("Content-Type", "application/x-www-form-urlencoded"),
         ("Content-Length", "15")]
_LENGTH = [("Host", "example.com"), ("Content-Length", "11"), ("Accept", "text/plain")]

_REQUESTS = (
    ("method", {"line": "DELETE /items/7 HTTP/1.1", "headers": [("Host", "example.com")]}),
    ("target", {"line": "GET /docs/index.html HTTP/1.1", "headers": _GET}),
    ("target", {"line": "GET /search?q=python&page=2 HTTP/1.1", "headers": _GET}),
    ("version", {"line": "GET / HTTP/1.0"}),
    ("triple", {"line": "PUT /items/7 HTTP/1.1", "headers": [("Host", "example.com")]}),
    ("path", {"line": "GET /search?q=python HTTP/1.1", "headers": _GET}),
    ("path", {"line": "GET /about HTTP/1.1", "headers": _GET}),
    ("path", {"line": "GET /search?q=a&page=2 HTTP/1.1", "headers": _GET}),
    ("header", {"line": "GET / HTTP/1.1", "headers": _GET, "ask": "host"}),
    ("header", {"line": "GET / HTTP/1.1", "headers": _GET, "ask": "accept"}),
    ("header", {"line": "GET /a HTTP/1.1", "headers": _AGENT, "ask": "user-agent"}),
    ("count", {"line": "GET /a HTTP/1.1", "headers": _AGENT}),
    ("names", {"line": "GET / HTTP/1.1", "headers": _GET}),
    ("names", {"line": "GET /a HTTP/1.1", "headers": _AGENT}),
    ("hostport", {"line": "GET / HTTP/1.1", "headers": _FORM[:1] + _GET[1:]}),
    ("hostport", {"line": "GET / HTTP/1.1", "headers": _GET}),
    ("body", {"line": "POST /login HTTP/1.1", "headers": _FORM, "body": "name=Ada&age=36"}),
    ("body", {"line": "POST /notes HTTP/1.1", "headers": _LENGTH, "body": "hello there"}),
    ("valid", {"line": "GET /index.html HTTP/1.1"}),
    ("valid", {"line": "GET /index.html"}),
)


def _lines_text(line: str, headers) -> str:
    parts = [line] + [f"{k}: {v}" for k, v in (headers or [])]
    return _and(f"'{p}'" for p in parts)


def _request_row(row):
    want, a = row
    args = {"want": want, **a}
    headers, body = a.get("headers"), a.get("body")
    text = (f"The text of an HTTP request is made of the lines "
            f"{_lines_text(a['line'], headers)}, each ending in a carriage return "
            f"and a newline, and then an empty line")
    text += f" and the body '{body}'." if body else "."
    if want == "valid":
        return (f"{text} Split the first line at its spaces. When it has exactly "
                f"three pieces and the last starts with HTTP/ print ok, otherwise "
                f"print 400 Bad Request.", args)
    cut = " Split off the request line, and split that line at its spaces into three pieces."
    if want == "method":
        return f"{text}{cut} Print the method.", args
    if want == "target":
        return f"{text}{cut} Print the target.", args
    if want == "version":
        return f"{text}{cut} Print the number after the slash in the version.", args
    if want == "triple":
        return f"{text}{cut} Print the method, the target and the version, separated by spaces.", args
    if want == "path":
        return (f"{text}{cut} Split the target at its question mark. Print the path, "
                f"then on the next line the query, or the word none when there is "
                f"none.", args)
    if want == "count":
        return f"{text} Print how many header lines there are.", args
    if want == "names":
        return (f"{text} Print the names of the headers, in order, joined by a comma "
                f"and a space.", args)
    held = (" Read the header lines into a dictionary with the names in lower "
            "case and the values with their spaces trimmed.")
    if want == "header":
        return f"{text}{cut}{held} Print the value of the {a['ask']} header.", args
    if want == "hostport":
        return (f"{text}{cut}{held} Split the Host header at its colon. Print the "
                f"host, a space and the port, or 80 when there is no port.", args)
    return (f"{text}{cut}{held} Read the number of characters that the "
            f"content-length header says from the body, and print that number, a "
            f"space and those characters.", args)


REQUEST_PAGE = _page(
    "py-web-request", 355, "Web: parsing a raw request",
    "Before any framework, a request is a block of text: the request line "
    "(METHOD target VERSION, split at spaces), then one Name: value line for "
    "each header, then an empty line, then the body if there is one. Lines "
    "end in '\\r\\n'. raw.partition('\\r\\n\\r\\n') cuts the head from the "
    "body at the empty line, head.split('\\r\\n') gives the lines, and "
    "request_line, *header_lines = lines splits off the first. A header "
    "line is cut at the first colon with line.partition(':'), which matters "
    "because a Host value can hold one (example.com:8080): later colons "
    "stay in the value. Strip the spaces from the value, and lower the "
    "name, since header names do not depend on case. The target holds the "
    "path and the query together, and target.partition('?') splits them, "
    "with an empty query when there is none. A body is exactly "
    "Content-Length characters long here, so body[:size] takes what the "
    "header promised. A request line that does not split into three pieces, "
    "or whose version does not start with HTTP/, is a 400 Bad Request.",
    "raw = 'GET /a?x=1 HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n'; head, _, "
    "body = raw.partition('\\r\\n\\r\\n'); request_line, *header_lines = "
    "head.split('\\r\\n'); method, target, version = request_line.split(' ') "
    "gives GET, /a?x=1 and HTTP/1.1, and 'Host: example.com'.partition(':') "
    "gives ('Host', ':', ' example.com')",
    "py_web_request",
    tuple(_request_row(row) for row in _REQUESTS),
)


# ── 356. Routing with a dict ─────────────────────────────────

_HOME = ("/", "home", "Welcome")
_ABOUT = ("/about", "about", "About us")
_TEAM = ("/team", "team", "Our team")

_ROUTES = (
    ("dispatch", {"routes": [_HOME, _ABOUT], "paths": ["/", "/about", "/nope"]}),
    ("dispatch", {"routes": [("/hello", "hello", "Hi there"), ("/bye", "bye", "Goodbye")],
                  "paths": ["/bye", "/hello", "/hi", "/"]}),
    ("dispatch", {"routes": [("/", "index", "Home page"), ("/contact", "contact", "Write to us")],
                  "paths": ["/contact", "/", "/contact/"]}),
    ("dispatch", {"routes": [("/help", "help_page", "Need help?"), ("/faq", "faq", "Questions")],
                  "paths": ["/faq", "/help", "/faq/", "/other"]}),
    ("dispatch", {"routes": [("/pricing", "pricing", "Free for all"),
                             ("/docs", "docs", "Read the manual")],
                  "paths": ["/docs", "/pricing", "/blog"]}),
    ("trailing", {"routes": [_HOME, _TEAM], "paths": ["/team/", "/", "/nope/", "/team//"]}),
    ("trailing", {"routes": [("/shop", "shop", "Browse"), ("/cart", "cart", "Your cart")],
                  "paths": ["/cart/", "/shop", "/blog/"]}),
    ("trailing", {"routes": [("/", "index", "Index"), ("/a", "page_a", "Page A")],
                  "paths": ["/a/", "/b/", "/"]}),
    ("names", {"routes": [_HOME, _ABOUT], "paths": ["/about", "/", "/missing"]}),
    ("names", {"routes": [("/login", "login", "Log in"), ("/logout", "logout", "Bye")],
               "paths": ["/logout", "/login", "/"]}),
    ("names", {"routes": [("/a", "alpha", "First"), ("/b", "beta", "Second")],
               "paths": ["/b", "/c", "/a", "/b"]}),
    ("methods", {"routes": [("GET", "/", "home", "Welcome"), ("POST", "/login", "login", "Log in")],
                 "requests": [("GET", "/"), ("GET", "/login"), ("POST", "/nope"), ("POST", "/login")]}),
    ("methods", {"routes": [("GET", "/items", "items", "Item list"),
                            ("POST", "/items/new", "create", "Created")],
                 "requests": [("GET", "/items"), ("POST", "/items"), ("GET", "/other")]}),
    ("methods", {"routes": [("POST", "/save", "save", "Saved"), ("GET", "/view", "view", "Viewing")],
                 "requests": [("POST", "/save"), ("GET", "/save"), ("GET", "/view"), ("GET", "/edit")]}),
    ("pattern", {"pattern": "/users/<id>", "path": "/users/7"}),
    ("pattern", {"pattern": "/users/<id>/posts/<slug>", "path": "/users/7/posts/hello"}),
    ("pattern", {"pattern": "/users/<id>", "path": "/users/7/posts"}),
    ("pattern", {"pattern": "/blog/<year>/<slug>", "path": "/people/2024/intro"}),
    ("decorator", {"routes": [_HOME, _ABOUT], "paths": ["/", "/about", "/nope"]}),
    ("decorator", {"routes": [("/hello", "hello", "Hi there"), ("/bye", "bye", "Goodbye")],
                   "paths": ["/hello", "/gone", "/bye"]}),
)


def _route_table(routes) -> str:
    return _and(f"{p} to a function called {n} that returns the text '{t}'"
                for p, n, t in routes)


def _route_row(row):
    want, a = row
    args = {"want": want, **a}
    if want in ("dispatch", "trailing", "names", "decorator"):
        routes, paths = a["routes"], a["paths"]
        shown = _quoted(paths)
        if want == "decorator":
            return (f"Make a dictionary called ROUTES, and a decorator route(path) "
                    f"that stores the function it decorates in it under that path. "
                    f"Use it to route {_route_table(routes)}. For each of the paths "
                    f"{shown}, in that order, print what the handler returns, or "
                    f"404 Not Found when the path has none.", args)
        base = f"Make a dictionary that routes {_route_table(routes)}."
        if want == "dispatch":
            return (f"{base} Write a function dispatch(path) that returns what the "
                    f"handler returns, or 404 Not Found when the path has no "
                    f"handler. Print dispatch for each of the paths {shown}, in "
                    f"that order.", args)
        if want == "trailing":
            return (f"{base} A path may end in slashes, so take them off before "
                    f"looking it up, leaving a single slash for the root. For "
                    f"each of the paths {shown}, in that order, print what the "
                    f"handler returns, or 404 Not Found when there is none.", args)
        return (f"{base} For each of the paths {shown}, in that order, print the "
                f"name of its handler function, or the word none when there is "
                f"none.", args)
    if want == "methods":
        things = _and(f"{m} {p} to a function called {n} that returns the text '{t}'"
                      for m, p, n, t in a["routes"])
        asked = _and(f"{m} {p}" for m, p in a["requests"])
        return (f"Make a dictionary keyed by (method, path) pairs that routes "
                f"{things}. Write a function dispatch(method, path) that returns "
                f"what the handler returns; when there is no handler but the path "
                f"is routed for another method it returns 405 Method Not Allowed, "
                f"and otherwise 404 Not Found. Print dispatch for each of these "
                f"requests, in order: {asked}.", args)
    return (f"Write a function match(pattern, path) that splits both at the "
            f"slashes. It returns None when they have a different number of "
            f"pieces or a plain piece differs, and otherwise a dictionary of the "
            f"pieces of the path that sit under a piece of the pattern written "
            f"like <name>, keyed by that name. Print match for the pattern "
            f"{a['pattern']} and the path {a['path']}.", args)


ROUTE_PAGE = _page(
    "py-web-route", 356, "Web: routing with a dict",
    "A router is a table from a request to the function that handles it. In "
    "Python that is a dict whose values are functions: ROUTES = {'/': home, "
    "'/about': about}, and ROUTES.get(path) gives the handler or None, so "
    "'handler() if handler else \"404 Not Found\"' is a whole dispatcher. "
    "Functions are values, so they can sit in a dict and be called later, "
    "and handler.__name__ is the name they were defined with. Normalise "
    "the path first: path.rstrip('/') or '/' removes trailing slashes and "
    "keeps the root. Key the dict on a pair, (method, path), to route a "
    "method too; then a lookup that fails is a 405 if some other method "
    "routes the same path, and a 404 if none does. A path with parts that "
    "change, such as /users/7, is matched piece by piece: split pattern and "
    "path at '/', compare the plain pieces, and collect the pieces that "
    "sit under a <name>. A decorator is a function that returns a function: "
    "@route('/') calls route('/')(home), which can register home in ROUTES "
    "on the way and hand it back unchanged. This is the shape of Flask's "
    "@app.route.",
    "def home(): return 'Welcome'; ROUTES = {'/': home}; ROUTES.get('/')() is "
    "'Welcome' and ROUTES.get('/nope') is None; '/team//'.rstrip('/') or '/' "
    "is '/team'; ROUTES[('GET', '/')] keys on the method too",
    "py_web_route",
    tuple(_route_row(row) for row in _ROUTES),
)


# ── 357. GET routes on http.server ───────────────────────────

_SERVE = ("Start an http.server HTTPServer on port 0 of 127.0.0.1 (let the "
          "system choose the port), serving from a daemon thread, with a "
          "handler ")
_ASK = "Once it is running, use urllib.request to ask it for "
_STOP = "and shut the server down."

_GETS = (
    ("route", {"pages": [("/", "home"), ("/about", "about us")],
               "paths": ["/", "/about", "/nope"]}),
    ("route", {"pages": [("/hello", "Hi there!"), ("/bye", "Goodbye!")],
               "paths": ["/bye", "/hello", "/hi"]}),
    ("ctype", {"type": "text/html", "charset": "utf-8"}),
    ("ctype", {"type": "text/csv", "charset": None}),
    ("error", {"status": 404, "text": "no such page"}),
    ("error", {"status": 503, "text": "try again later"}),
    ("hits", {"paths": ["/a", "/b", "/a"]}),
    ("hits", {"paths": ["/x", "/x", "/y", "/x"]}),
    ("query", {"fallback": "stranger", "queries": ["?name=Ada", "?name=Ada+Lovelace", ""]}),
    ("query", {"fallback": "guest",
               "queries": ["?name=Grace%20Hopper", "", "?name=Linus&lang=en"]}),
    ("tags", {"show": "join", "sep": " + ", "paths": ["/?tag=red&tag=green&tag=blue", "/"]}),
    ("tags", {"show": "count", "sep": "", "paths": ["/?tag=a&tag=b&tag=c", "/"]}),
    ("sum", {"paths": ["/add?a=2&b=3", "/add?a=2", "/add?a=x&b=1"]}),
    ("sum", {"paths": ["/add?a=10&b=-4", "/add?b=5", "/add?a=7&b=8x"]}),
    ("redirect", {"code": 301, "chain": [("/old", "/new")], "start": "/old"}),
    ("redirect", {"code": 302, "chain": [("/a", "/b"), ("/b", "/c")], "start": "/a"}),
    ("methods", {"path": "/items",
                 "requests": [("GET", "/items"), ("POST", "/items"), ("GET", "/other")]}),
    ("methods", {"path": "/status",
                 "requests": [("POST", "/status"), ("GET", "/status"), ("POST", "/nope")]}),
    ("methods", {"path": "/login",
                 "requests": [("GET", "/nope"), ("POST", "/login"), ("GET", "/login"),
                              ("POST", "/other")]}),
    ("unsupported", {"method": "DELETE"}),
    ("unsupported", {"method": "PATCH"}),
)


def _get_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "route":
        pages = _and(f"{p} with the text '{t}'" for p, t in a["pages"])
        return (f"{_SERVE}that answers the paths {pages} with the status 200, and "
                f"any other path with the status 404 and the text not found. "
                f"{_ASK}each of the paths {_quoted(a['paths'])}, in that order, "
                f"catching the error urlopen raises for a 404, print the path, the "
                f"status and the body text on one line, separated by spaces, "
                f"{_STOP}", args)
    if want == "ctype":
        value = a["type"] + (f"; charset={a['charset']}" if a["charset"] else "")
        return (f"{_SERVE}that answers every GET request with the Content-Type "
                f"header set to '{value}' and the body text hello. {_ASK}its "
                f"address, print the content type the response reports (without "
                f"its parameters), a space and the charset it reports, {_STOP}", args)
    if want == "error":
        return (f"{_SERVE}that answers every GET request with the status "
                f"{a['status']} and the text '{a['text']}'. {_ASK}its address, "
                f"catching the error urlopen raises, print the status, the reason "
                f"phrase and the body text, separated by spaces, {_STOP}", args)
    if want == "hits":
        return (f"{_SERVE}that counts the requests for each path separately, and "
                f"answers every GET request with how many times that path has now "
                f"been asked for. {_ASK}the paths {_quoted(a['paths'])}, in that "
                f"order, print the answers on one line joined by a comma and a "
                f"space, {_STOP}", args)
    if want == "query":
        shown = _and(f"'{q}'" if q else "no query string at all" for q in a["queries"])
        return (f"{_SERVE}that answers every GET request with Hello, a comma, a "
                f"space, the value of the name query parameter and an exclamation "
                f"mark, or the word {a['fallback']} when there is no name. {_ASK}"
                f"the root path with each of these query strings, in order: "
                f"{shown}. Print the answers, one per line, {_STOP}", args)
    if want == "tags":
        if a["show"] == "join":
            what = (f"answers with the values of the tag query parameters (there "
                    f"may be several) joined by '{a['sep']}', or the word none "
                    f"when there are none")
        else:
            what = ("answers with how many tag query parameters the path has "
                    "(there may be several, or none)")
        return (f"{_SERVE}that {what}. {_ASK}each of the paths "
                f"{_quoted(a['paths'])}, in that order, print the answers one per "
                f"line, {_STOP}", args)
    if want == "sum":
        return (f"{_SERVE}that adds the whole numbers in the query parameters a "
                f"and b of a GET request and answers with the status 200 and the "
                f"sum, or with the status 400 and the text bad request when "
                f"either is missing or is not a whole number. {_ASK}each of the "
                f"paths {_quoted(a['paths'])}, in that order, catching the error "
                f"urlopen raises for a 400, print the status and the body text on "
                f"one line, separated by a space, {_STOP}", args)
    if want == "redirect":
        hops = _and(f"{x} to {y}" for x, y in a["chain"])
        return (f"{_SERVE}that redirects {hops} with the status {a['code']} and a "
                f"Location header, and answers any other path with the status 200 "
                f"and the path itself as the text. {_ASK}{a['start']}, which "
                f"urlopen follows on its own, print the final status and the "
                f"body text, separated by a space, {_STOP}", args)
    if want == "methods":
        path = a["path"]
        asked = _and(f"{m} {p}" for m, p in a["requests"])
        return (f"{_SERVE}that answers a GET request with the status 200 when the "
                f"path is {path} and 404 otherwise, and answers a POST request "
                f"with 405 and an Allow header set to GET when the path is {path} "
                f"and 404 otherwise. {_ASK}these requests, in order: {asked}. "
                f"Catching the error urlopen raises, print the method, the path, "
                f"the status and the Allow header (a hyphen when there is none) "
                f"on one line, separated by spaces, {_STOP}", args)
    return (f"{_SERVE}that only has a method for GET, answering it with the "
            f"status 200 and the text ok. {_ASK}its address with a "
            f"{a['method']} request, catching the error urlopen raises, print the "
            f"status and the reason phrase, separated by a space, {_STOP}", args)


GET_PAGE = _page(
    "py-web-get", 357, "Web: GET routes, queries and errors on http.server",
    "http.server's HTTPServer(address, Handler) makes a web server, and "
    "Handler is a subclass of BaseHTTPRequestHandler with a method for each "
    "verb it answers: do_GET, do_POST. Inside, self.path holds the path and "
    "the query together, self.command the method, and self.send_response"
    "(status), self.send_header(name, value), self.end_headers() and then "
    "self.wfile.write(bytes) answer, in that order. A path that is not "
    "routed is a 404; a path that exists for another method is a 405 Method "
    "Not Allowed with an Allow header listing what it does take; and a "
    "method the handler has no do_ for at all gets a 501 from the base "
    "class, 'Unsupported method', without any code from you. urllib.parse"
    ".urlparse(self.path) splits path from query and parse_qs gives lists, "
    "so a repeated name arrives as a list of values and a missing one is "
    "just not there. HTTPServer(('127.0.0.1', 0), Handler) takes any free "
    "port, server.server_port says which, serve_forever(0.01) in a daemon "
    "thread checks for a shutdown every ten milliseconds, and "
    "server.shutdown() then server.server_close() tidies up. On the other "
    "side urllib.request.urlopen(url) gives a response with .status, "
    ".headers and .read(); for a 4xx or a 5xx it raises urllib.error."
    "HTTPError instead, which is itself a response with .status, .reason, "
    ".headers and .read(). A 301, 302 or 307 for a GET is followed for "
    "you. Request(url, method='POST') picks the verb. The server's own log "
    "line goes to stderr, not to what the program prints.",
    "class Handler(BaseHTTPRequestHandler): def do_GET(self): self."
    "send_response(200); self.end_headers(); self.wfile.write(b'hi'); then "
    "server = HTTPServer(('127.0.0.1', 0), Handler), a daemon Thread running "
    "server.serve_forever, base = f'http://127.0.0.1:{server.server_port}', "
    "and urllib.request.urlopen(base + '/').read() is b'hi'; "
    "urllib.request.urlopen(base + '/nope') raises HTTPError with .status "
    "404 and .reason 'Not Found' when the handler sends 404",
    "py_web_get",
    tuple(_get_row(row) for row in _GETS),
)


# ── 358. A JSON API ──────────────────────────────────────────

_API_SERVE = _SERVE.replace("with a handler ", "with a handler ")

_APIS = (
    ("total", {"op": "sum", "numbers": [3, 4, 5]}),
    ("total", {"op": "max", "numbers": [8, 2, 9, 5]}),
    ("total", {"op": "sum", "numbers": [10, 20, 30, 5]}),
    ("total", {"op": "min", "numbers": [14, 6, 9]}),
    ("greet", {"name": "Ada"}),
    ("greet", {"name": "Grace"}),
    ("greet", {"name": "Linus"}),
    ("word", {"word": "stressed", "how": "upper"}),
    ("word", {"word": "stressed", "how": "reverse"}),
    ("word", {"word": "drawer", "how": "reverse"}),
    ("stats", {"numbers": [4, 9, 2, 7]}),
    ("stats", {"numbers": [10, 3, 8]}),
    ("length", {"name": "Ada"}),
    ("length", {"name": "Grace"}),
    ("create", {"names": ["tea", "cake", "jam"]}),
    ("create", {"names": ["pen", "ink"], "seeded": 1}),
    ("create", {"names": ["a", "b", "c", "d"]}),
    ("invalid", {"kind": "good", "key": "name", "value": "Ada"}),
    ("invalid", {"kind": "missing", "key": "nome", "value": "Ada"}),
    ("invalid", {"kind": "bad", "text": "oops"}),
    ("invalid", {"kind": "bad", "text": "{'name': 'Ada'}"}),
)

_TOTAL_WORDS = {
    "sum": ("total", "the sum"),
    "max": ("biggest", "the biggest"),
    "min": ("smallest", "the smallest"),
}

_NUMBERS_BODY = "a dictionary with numbers as the list"


def _api_row(row):
    want, a = row
    args = {"want": want, **a}
    post = f"{_SERVE}that answers a POST request by reading its JSON body, a dictionary, "
    asked = "Once it is running, use urllib.request to send it a POST request "
    stop = _STOP
    if want == "total":
        key, noun = _TOTAL_WORDS[a["op"]]
        return (f"{post}and answering with JSON for a dictionary holding {noun} of "
                f"its numbers under the key {key}, with the content type "
                f"application/json. {asked}whose body is the JSON for "
                f"{_NUMBERS_BODY} {_and(a['numbers'])}, print the {key} from the "
                f"JSON that comes back, {stop}", args)
    if want == "greet":
        return (f"{post}and answering with JSON for a dictionary holding the text "
                f"Hello, a comma, a space, its name and an exclamation mark under "
                f"the key message, with the content type application/json. "
                f"{asked}whose body is the JSON for a dictionary with name "
                f"{a['name']}, print the whole dictionary that comes back, {stop}", args)
    if want == "word":
        how = ("in capital letters" if a["how"] == "upper" else "written backwards")
        return (f"{post}and answering with JSON for a dictionary holding its word "
                f"{how} under the key word, with the content type "
                f"application/json. {asked}whose body is the JSON for a "
                f"dictionary with word {a['word']}, print the whole dictionary "
                f"that comes back, {stop}", args)
    if want == "stats":
        return (f"{post}and answering with JSON for a dictionary holding the "
                f"smallest of its numbers under min, the biggest under max and "
                f"how many there are under count, with the content type "
                f"application/json. {asked}whose body is the JSON for "
                f"{_NUMBERS_BODY} {_and(a['numbers'])}, print the whole "
                f"dictionary that comes back, {stop}", args)
    if want == "length":
        return (f"{post}and answering with JSON for a dictionary holding the text "
                f"Hello, a comma, a space, its name and an exclamation mark under "
                f"the key message, with the content type set to application/json "
                f"and the Content-Length header set to the size of the body in "
                f"bytes. {asked}whose body is the JSON for a dictionary with name "
                f"{a['name']}, print the Content-Type header of the reply and "
                f"then, on the next line, its Content-Length, {stop}", args)
    if want == "create":
        had = a.get("seeded", 0)
        start = (f"The server starts with {had} item already stored. " if had else
                 "The server starts with no items stored. ")
        return (f"{_SERVE}that keeps a list of items. {start}It answers a POST "
                f"request by reading its JSON body, a dictionary, adding the text "
                f"under name to the list, and answering with the status 201 and "
                f"JSON for a dictionary holding how many items there are now "
                f"under id. {asked}for each of the names {_quoted(a['names'])}, "
                f"in that order, whose body is the JSON for a dictionary with that "
                f"name, print the status and the id on one line, separated by a "
                f"space, {stop}", args)
    kind = a["kind"]
    handler = (f"{_SERVE}that answers a POST request by reading its JSON body and "
               f"answering with the status 200 and JSON for a dictionary holding "
               f"the name under hello. When the body is not JSON, or has no name, "
               f"it answers with the status 400 and JSON for a dictionary with "
               f"the text bad request under error. ")
    if kind == "bad":
        sent = f"whose body is the text {a['text']}"
    else:
        sent = (f"whose body is the JSON for a dictionary with {a['key']} "
                f"{a['value']}")
    return (f"{handler}{asked}{sent}, catching the error urlopen raises, print the "
            f"status and the dictionary the JSON holds, separated by a space, "
            f"{stop}", args)


API_PAGE = _page(
    "py-web-api", 358, "Web: a JSON API with POST",
    "An API is a server that speaks data instead of pages. A POST request "
    "carries a body, and the handler reads exactly Content-Length bytes of "
    "it with self.rfile.read(int(self.headers['Content-Length'])); "
    "json.loads accepts those bytes and returns a dict, and json.dumps(data)"
    ".encode() turns the answer back into bytes for self.wfile.write. Say "
    "what the bytes are with send_header('Content-Type', 'application/"
    "json'), and send_header('Content-Length', str(len(body))) when you want "
    "the client to know the size. Choose the status that tells the truth: "
    "200 for a plain success, 201 Created when a POST stored something new, "
    "and 400 Bad Request when the body is not JSON (json.loads raises "
    "ValueError, which JSONDecodeError subclasses) or leaves out something "
    "needed (a KeyError). The client side: urllib.request.Request(url, "
    "data=bytes) makes it a POST, urlopen sends it, json.load(reply) reads "
    "the answer straight from the response, and a 400 raises HTTPError, "
    "which can still be read like a reply. A dict printed by Python uses "
    "single quotes and True, where the JSON text used double quotes and "
    "true. HTTPServer takes one request at a time, in order, so a counter "
    "kept on the handler class is safe.",
    "class Handler(BaseHTTPRequestHandler): def do_POST(self): data = json."
    "loads(self.rfile.read(int(self.headers['Content-Length']))); body = json."
    "dumps({'total': sum(data['numbers'])}).encode(); then send_response(200), "
    "end_headers() and wfile.write(body); the client posts urllib.request."
    "Request(base, data=json.dumps({'numbers': [1, 2]}).encode()) and json."
    "load(reply) is {'total': 3}",
    "py_web_api",
    tuple(_api_row(row) for row in _APIS),
)


# ── 359. Cookies ─────────────────────────────────────────────

_PAIRS_A = [("session", "abc123"), ("theme", "dark")]
_PAIRS_B = [("lang", "en"), ("theme", "dark"), ("visits", 3)]
_PAIRS_C = [("cart", "x9"), ("user_id", "ada"), ("theme", "light")]

_COOKIES = (
    ("value", {"pairs": _PAIRS_A, "ask": "session"}),
    ("value", {"pairs": _PAIRS_B, "ask": "visits"}),
    ("value", {"pairs": _PAIRS_C, "ask": "user_id"}),
    ("keys", {"pairs": _PAIRS_A}),
    ("keys", {"pairs": _PAIRS_C}),
    ("has", {"pairs": _PAIRS_B, "ask": "theme"}),
    ("has", {"pairs": _PAIRS_A, "ask": "lang"}),
    ("items", {"pairs": _PAIRS_B}),
    ("output", {"name": "session", "value": "abc123"}),
    ("output", {"name": "visits", "value": 3}),
    ("attrs", {"name": "session", "value": "abc123",
               "attrs": [("path", "/"), ("httponly", True)]}),
    ("attrs", {"name": "token", "value": "x1",
               "attrs": [("secure", True), ("max-age", 3600), ("path", "/")]}),
    ("attrs", {"name": "theme", "value": "dark",
               "attrs": [("samesite", "Lax"), ("path", "/app")]}),
    ("attrs", {"name": "id", "value": "77",
               "attrs": [("secure", True), ("httponly", True), ("domain", "example.com")]}),
    ("many", {"pairs": [("b", 2), ("a", 1)]}),
    ("many", {"pairs": [("theme", "dark"), ("lang", "en"), ("size", "large")]}),
    ("parseattr", {"header": "session=abc123; Path=/app; Max-Age=3600; HttpOnly",
                   "name": "session", "attr": "path"}),
    ("parseattr", {"header": "session=abc123; Path=/app; Max-Age=3600; HttpOnly",
                   "name": "session", "attr": "max-age"}),
    ("parseattr", {"header": "session=abc123; Path=/app; Max-Age=3600; HttpOnly",
                   "name": "session", "attr": "httponly"}),
    ("parseattr", {"header": "id=77; Secure; SameSite=Lax", "name": "id", "attr": "samesite"}),
)

_ATTR_WORDS = {
    "path": "Path", "domain": "Domain", "samesite": "SameSite", "max-age": "Max-Age",
}


def _attr_phrase(attrs) -> str:
    out = []
    for key, value in attrs:
        if value is True:
            out.append("httponly turned on" if key == "httponly" else "secure turned on")
        else:
            out.append(f"{_ATTR_WORDS[key]} set to {value}")
    return _and(out)


def _pair_text(pairs) -> str:
    return "; ".join(f"{k}={v}" for k, v in pairs)


def _cookies_row(row):
    want, a = row
    args = {"want": want, **a}
    if want in ("value", "keys", "has", "items"):
        head = (f"Parse the Cookie header text '{_pair_text(a['pairs'])}' with "
                f"SimpleCookie")
        if want == "value":
            return f"{head} and print the value of the cookie called {a['ask']}.", args
        if want == "keys":
            return f"{head} and print the list of the cookie names, in order.", args
        if want == "has":
            return (f"{head} and print whether there is a cookie called "
                    f"{a['ask']}.", args)
        return (f"{head} and print each cookie's name and value, separated by a "
                f"space, one per line.", args)
    if want == "output":
        return (f"Make a SimpleCookie holding a cookie called {a['name']} with the "
                f"value {a['value']}, and print the Set-Cookie header text it "
                f"makes.", args)
    if want == "attrs":
        return (f"Make a SimpleCookie holding a cookie called {a['name']} with the "
                f"value {a['value']}. Then set, in this order, its "
                f"{_attr_phrase(a['attrs'])}. Print the Set-Cookie header text it "
                f"makes.", args)
    if want == "many":
        things = _and(f"{k} as {v}" for k, v in a["pairs"])
        return (f"Make a SimpleCookie, and add a cookie for each of these names "
                f"and values, in order: {things}. Print its Set-Cookie header "
                f"lines, one per line.", args)
    return (f"Parse the Set-Cookie header text '{a['header']}' with SimpleCookie "
            f"and print the {a['attr']} attribute of the cookie called "
            f"{a['name']}.", args)


COOKIES_PAGE = _page(
    "py-web-cookies", 359, "Web: cookies with SimpleCookie",
    "A cookie is a name and a value the server asks the browser to keep and "
    "send back. The server sets one with a Set-Cookie header; the browser "
    "returns them in a Cookie header, as 'a=1; b=2'. http.cookies."
    "SimpleCookie is a dict of Morsels: SimpleCookie('a=1; b=2') parses a "
    "header, cookie['a'].value is the text '1' (always text, even for a "
    "number), 'a' in cookie and list(cookie) work like a dict, and "
    "SimpleCookie() starts empty so cookie['a'] = 'x' builds one. "
    "cookie.output() writes 'Set-Cookie: a=x' for each cookie, sorted by "
    "name rather than in the order added, and joined by "
    "'\\r\\n' unless you pass sep='\\n'. Attributes live on the morsel: "
    "cookie['a']['path'] = '/', ['httponly'] = True, ['max-age'] = 3600, "
    "['secure'], ['samesite'] and ['domain']. They come out sorted by their "
    "lower-case names, not in the order you set them, and written with "
    "their own capitals: Domain, HttpOnly, Max-Age, Path, SameSite, "
    "Secure. Parsing a Set-Cookie text fills the same attributes in, with "
    "a flag such as HttpOnly read as True and the others as text.",
    "from http.cookies import SimpleCookie; cookie = SimpleCookie('a=1; "
    "b=2'); cookie['a'].value is '1' and list(cookie) is ['a', 'b']; "
    "cookie = SimpleCookie(); cookie['s'] = 'x'; cookie['s']['path'] = '/'; "
    "cookie['s']['httponly'] = True; cookie.output() is 'Set-Cookie: s=x; "
    "HttpOnly; Path=/'",
    "py_web_cookies",
    tuple(_cookies_row(row) for row in _COOKIES),
)


# ── 360. WSGI ────────────────────────────────────────────────

_WS_CALL = ("Call it with {environ} and a start_response function that prints the "
            "status and the list of header pairs. Print the body, decoded, as well.")

_WSGIS = (
    ("hello", {"type": "text/plain", "body": "hello"}),
    ("hello", {"type": "text/html", "body": "<h1>Hi</h1>"}),
    ("hello", {"type": "application/json", "body": '{"ok": true}'}),
    ("path", {"pages": [("/", "home"), ("/about", "about us")], "path": "/about"}),
    ("path", {"pages": [("/", "home"), ("/about", "about us")], "path": "/contact"}),
    ("path", {"pages": [("/hello", "Hi!"), ("/bye", "Goodbye!")], "path": "/bye"}),
    ("method", {"allowed": "GET", "method": "GET", "body": "all good"}),
    ("method", {"allowed": "GET", "method": "DELETE", "body": "all good"}),
    ("method", {"allowed": "POST", "method": "GET", "body": "saved"}),
    ("query", {"query": "name=Ada", "fallback": "stranger"}),
    ("query", {"query": "name=Ada+Lovelace&lang=en", "fallback": "stranger"}),
    ("query", {"query": "lang=en", "fallback": "guest"}),
    ("accept", {"accept": "application/json"}),
    ("accept", {"accept": "text/html"}),
    ("post", {"data": "hello world", "reply": "upper"}),
    ("post", {"data": "the quick brown fox", "reply": "words"}),
    ("post", {"data": "stressed", "reply": "reverse"}),
    ("middleware", {"how": "upper", "body": "hello world"}),
    ("middleware", {"how": "reverse", "body": "stressed"}),
    ("middleware", {"how": "prefix", "body": "hello"}),
)


def _wsgi_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "hello":
        return (f"Write a WSGI app that starts its response with the status 200 OK "
                f"and one header, Content-Type set to {a['type']}, and returns "
                f"the bytes of the text '{a['body']}' in a list. "
                f"{_WS_CALL.format(environ='an empty environ')}", args)
    if want == "path":
        pages = _and(f"{p} with the text '{t}'" for p, t in a["pages"])
        return (f"Write a WSGI app that looks at environ['PATH_INFO'] and answers "
                f"{pages} with the status 200 OK and a Content-Type header of "
                f"text/plain, and any other path with the status 404 Not Found, "
                f"the same header and the text not found. "
                f"{_WS_CALL.format(environ='an environ whose PATH_INFO is ' + a['path'])}",
                args)
    if want == "method":
        return (f"Write a WSGI app that answers a {a['allowed']} request with the "
                f"status 200 OK, a Content-Type header of text/plain and the text "
                f"'{a['body']}'. Any other method gets the status 405 Method Not "
                f"Allowed, the single header Allow set to {a['allowed']}, and the "
                f"text method not allowed. "
                f"{_WS_CALL.format(environ='an environ whose REQUEST_METHOD is ' + a['method'])}",
                args)
    if want == "query":
        shown = a["query"]
        return (f"Write a WSGI app that reads the name from the query string in "
                f"environ['QUERY_STRING'] and answers with the status 200 OK, a "
                f"Content-Type header of text/plain, and Hello, a comma, a space, "
                f"the name and an exclamation mark, or the word {a['fallback']} "
                f"when there is no name. "
                f"{_WS_CALL.format(environ='an environ whose QUERY_STRING is ' + shown)}",
                args)
    if want == "accept":
        given = (f"an environ whose HTTP_ACCEPT is {a['accept']}")
        return (f"Write a WSGI app that answers with the status 200 OK. When "
                f"environ's HTTP_ACCEPT contains the word json it sends a "
                f"Content-Type header of application/json and the text "
                f"{{\"hello\": \"world\"}}; otherwise a Content-Type header of "
                f"text/plain and the text hello world. "
                f"{_WS_CALL.format(environ=given)}", args)
    if want == "post":
        reply = {"upper": "the body in capital letters",
                 "words": "how many words the body has",
                 "reverse": "the body written backwards"}[a["reply"]]
        return (f"Write a WSGI app that reads CONTENT_LENGTH bytes from the "
                f"environ's wsgi.input, and answers with the status 200 OK, a "
                f"Content-Type header of text/plain and {reply}. "
                f"{_WS_CALL.format(environ='an environ with CONTENT_LENGTH set to the text ' + str(len(a['data'])) + ' and wsgi.input an io.BytesIO of the bytes of ' + chr(39) + a['data'] + chr(39))}",
                args)
    change = {"upper": "turns every chunk of the body into capital letters",
              "reverse": "writes every chunk of the body backwards",
              "prefix": "puts a greater-than sign and a space in front of every chunk "
                        "of the body"}[a["how"]]
    return (f"Write a WSGI app that answers with the status 200 OK, a Content-Type "
            f"header of text/plain and the bytes of '{a['body']}'. Then write "
            f"middleware: a function that takes an app and returns a new app that "
            f"calls it and {change}. {_WS_CALL.format(environ='an empty environ').replace('Call it', 'Call the wrapped app')}",
            args)


WSGI_PAGE = _page(
    "py-web-wsgi", 360, "Web: a WSGI app",
    "WSGI is the contract between a Python web app and the server that "
    "runs it, and it is nothing but a function: app(environ, start_response). "
    "environ is a dict describing the request, REQUEST_METHOD, PATH_INFO, "
    "QUERY_STRING without its question mark, CONTENT_LENGTH as text, "
    "wsgi.input as a file to read the body from, and each header as "
    "HTTP_ACCEPT, HTTP_USER_AGENT and so on. The app calls "
    "start_response(status, headers) once with a status text such as "
    "'200 OK' and a list of (name, value) pairs, then returns an iterable "
    "of bytes, usually a list of one. Because it is only a function, you "
    "can test it with no server at all: pass in a dict, pass in a function "
    "that prints, and b''.join(result).decode() is the body. Middleware is "
    "a function that takes an app and returns another app that calls the "
    "first and changes what comes back: a closure over the inner app. The "
    "headers list prints as [('Content-Type', 'text/plain')].",
    "def app(environ, start_response): start_response('200 OK', [('Content-"
    "Type', 'text/plain')]); return [b'hello']; def show(status, headers): "
    "print(status, headers); b''.join(app({}, show)).decode() is 'hello' "
    "after printing 200 OK [('Content-Type', 'text/plain')]",
    "py_web_wsgi",
    tuple(_wsgi_row(row) for row in _WSGIS),
)


# ── 361. Templates ───────────────────────────────────────────

_TEMPLATES = (
    ("template", {"text": "<h1>$title</h1>", "values": {"title": "Hello"}}),
    ("template", {"text": "<p>Dear $name, your order $order has shipped.</p>",
                  "values": {"name": "Ada", "order": 42}}),
    ("braces", {"text": "<b>${word}s</b>", "values": {"word": "cat"}}),
    ("braces", {"text": "<i>${first}_${second}</i>", "values": {"first": "a", "second": "b"}}),
    ("dollar", {"text": "Total: $$$amount", "values": {"amount": 5}}),
    ("dollar", {"text": "<p>Cost: $$${price} each</p>", "values": {"price": 12}}),
    ("safe", {"text": "Hi $name, you owe $amount", "values": {"name": "Ada"}}),
    ("safe", {"text": "<p>$greeting, ${name}!</p>", "values": {"greeting": "Hello"}}),
    ("keyerror", {"text": "Hello $name, you are $age", "values": {"name": "Ada"}}),
    ("keyerror", {"text": "<p>$a and $b</p>", "values": {"a": "x", "b": "y"}}),
    ("format", {"text": "<li>{}</li>", "args": ["tea"]}),
    ("format", {"text": '<a href="{url}">{text}</a>',
                "kwargs": {"url": "/home", "text": "Home"}}),
    ("format", {"text": "<b>{0}</b> and <i>{1}</i>, then <b>{0}</b>", "args": ["tea", "cake"]}),
    ("list", {"kind": "ul", "items": ["tea", "cake", "jam"]}),
    ("list", {"kind": "ol", "items": ["one", "two"]}),
    ("list", {"kind": "numbered", "items": ["tea", "cake", "jam"]}),
    ("escape", {"items": ["Tom & Jerry", "<b>bold</b>"]}),
    ("escape", {"items": ["5 < 6 & 7 > 3", 'say "hi"']}),
    ("table", {"rows": [("tea", 3.5), ("cake", 12.25)]}),
    ("page", {"title": "Menu", "items": ["tea", "cake"]}),
)


def _fill(values: dict) -> str:
    return _and(f"{k} set to {v}" for k, v in values.items())


def _template_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "template":
        return (f"Make a string.Template from the text {a['text']} and fill it in "
                f"with {_fill(a['values'])}. Print the result.", args)
    if want == "braces":
        return (f"Make a string.Template from the text {a['text']}, whose "
                f"placeholders are written with braces so that other text can "
                f"touch them, and fill it in with {_fill(a['values'])}. Print the "
                f"result.", args)
    if want == "dollar":
        return (f"Make a string.Template from the text {a['text']}, in which a "
                f"double dollar sign stands for one dollar sign, and fill it in "
                f"with {_fill(a['values'])}. Print the result.", args)
    if want == "safe":
        return (f"Make a string.Template from the text {a['text']} and fill it in "
                f"with only {_fill(a['values'])}, using the method that leaves "
                f"any placeholder it has no value for as it is. Print the "
                f"result.", args)
    if want == "keyerror":
        return (f"Make a string.Template from the text {a['text']} and fill it in "
                f"with {_fill(a['values'])} inside a try block. If a KeyError is "
                f"raised, print the word missing, a space and the name that was "
                f"missing; otherwise print the result.", args)
    if want == "format":
        given = _and(
            [f"'{v}'" for v in a.get("args", [])]
            + [f"{k} as '{v}'" for k, v in a.get("kwargs", {}).items()])
        return (f"Fill in the format string {a['text']} with the values {given} "
                f"using the format method, and print the result.", args)
    if want == "list":
        items = _and(a["items"])
        if a["kind"] == "ul":
            return (f"Print the HTML for a bulleted list of {items}: a line with "
                    f"<ul>, a line like <li>tea</li> for each item, and a line "
                    f"with </ul>. Build the item lines in one expression and join "
                    f"them.", args)
        if a["kind"] == "ol":
            return (f"Print the HTML for a numbered list of {items}: a line with "
                    f"<ol>, a line like <li>one</li> for each item, and a line "
                    f"with </ol>. Build the item lines in one expression and join "
                    f"them.", args)
        return (f"Print one line like <li>1. tea</li> for each of {items}, with the "
                f"number counting from 1 before the item.", args)
    if want == "escape":
        items = _and(f"'{i}'" if '"' not in i else f"the text {i}" for i in a["items"])
        return (f"Print one line like <li>tea</li> for each of the items {items}, "
                f"with each item escaped for HTML before it goes between the tags, "
                f"so that its ampersands, angle brackets and quotes cannot be "
                f"read as markup.", args)
    if want == "table":
        rows = _and(f"{n} at {p}" for n, p in a["rows"])
        return (f"Print an HTML table: a line with <table>, a line like "
                f"<tr><td>tea</td><td>3.50</td></tr> for each of the rows {rows}, "
                f"with the price written with two decimal places, and a line with "
                f"</table>. Use the format method for each row.", args)
    items = _and(a["items"])
    return (f"Make a string.Template for a page whose lines are <h1>$title</h1>, "
            f"<ul>, $rows and </ul>. Build rows from {items} as a line for each "
            f"item made of two spaces and then <li>item</li>, joined with "
            f"newlines. Fill in the template with the title {a['title']} and "
            f"those rows, and print the page.", args)


TEMPLATE_PAGE = _page(
    "py-web-template", 361, "Web: templates and HTML",
    "A template is a page with holes. string.Template('<h1>$title</h1>') "
    "marks each hole with $name, or ${name} when other letters touch it, "
    "as in ${word}s; $$ is a literal dollar sign. .substitute(title='Hi') "
    "fills them (numbers are turned into text) and raises KeyError, with "
    "the missing name, if a value is absent; .safe_substitute leaves a "
    "placeholder it has no value for exactly as written. str.format uses "
    "braces: '{}' takes the next value, '{0}' and '{1}' a value by its "
    "place, '{url}' a keyword, and '{:.2f}' writes a number with two "
    "decimals. For a list, build the rows with a join: '\\n'.join(f'<li>"
    "{item}</li>' for item in items) makes one line each, where adding "
    "to a string in a loop copies it every time. Anything that came from a "
    "user must go through html.escape before it is put in a page: it "
    "writes & as &amp;, < as &lt;, > as &gt; and the quotes as &quot; and "
    "&#x27;, so that text cannot become markup. enumerate(items, start=1) "
    "counts from 1.",
    "from string import Template; Template('<h1>$title</h1>').substitute("
    "title='Hi') is '<h1>Hi</h1>'; '<li>{}</li>'.format('tea') is '<li>tea"
    "</li>'; import html; html.escape('a < b') is 'a &lt; b'; '\\n'.join("
    "f'<li>{x}</li>' for x in ['a', 'b']) puts each item on its own line",
    "py_web_template",
    tuple(_template_row(row) for row in _TEMPLATES),
)


PYWEB_PAGES: tuple[Page, ...] = (
    URL_PAGE,
    STATUS_PAGE,
    HEADERS_PAGE,
    REQUEST_PAGE,
    ROUTE_PAGE,
    GET_PAGE,
    API_PAGE,
    COOKIES_PAGE,
    WSGI_PAGE,
    TEMPLATE_PAGE,
)
