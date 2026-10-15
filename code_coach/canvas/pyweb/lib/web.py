"""web: a tiny Flask-like library for the "Web (Python)" Canvas track.

    from web import app, request, Response, json_response, redirect, abort, render

The learner writes routes; Code Coach starts the server (the program never
calls app.run - if it does, nothing happens). It is standard library only, on
top of http.server.ThreadingHTTPServer, and it listens on 127.0.0.1, port 0
(the operating system picks a free port) and nowhere else.

ROUTES

    @app.get("/hello/<name>")        <name> is a str (one /segment/, never empty)
    @app.get("/items/<int:id>")      <int:id> matches digits only and arrives as an int
    @app.post(...) @app.put(...) @app.delete(...) @app.patch(...)
    @app.route("/x", methods=["GET", "POST"])     methods default to ["GET"]

A route function takes the path parameters by name and returns the answer. A
trailing slash on a path is ignored ("/about/" is "/about"). Two routes for
the same path and method are an error when the program loads. The most
specific route wins ("/users/me" before "/users/<name>").

  - an unknown path is 404; a known path with the wrong method is 405 with an
    `Allow` header;
  - HEAD is answered by the GET route (same headers, no body); OPTIONS is
    answered with 204 and an `Allow` header, unless a route says otherwise;
  - an exception in a route is a 500 with a short page, and the traceback is
    printed (so it shows in the console).

WHAT A ROUTE MAY RETURN

    "text"                          200, text/html; charset=utf-8
    {...} or [...]                  200, application/json
    (body, 201)                     a status as well
    (body, 201, {"X-Thing": "1"})   headers as well
    Response(body, status=200, headers=None)
    redirect("/where", 303)  json_response(data, 201)  abort(404, "message")

Returning None (a forgotten `return`), a number or anything else is an error.
`abort(status, message)` stops the route and answers with that status; the
page is small HTML (JSON when the client asks for application/json).
`@app.errorhandler(404)` takes over a status: the function gets the error
(`error.status`, `error.message`) and returns like a route - but its status is
200 unless it returns one, as in Flask: return `(page, 404)`.

THE REQUEST (`request`, only inside a route)

    .method .path (decoded, no query) .query_string
    .args       the query as a dict of the FIRST value of each name
    .args_all   the query as a dict of lists (?tag=a&tag=b -> {"tag": ["a", "b"]})
    .form       a dict from an application/x-www-form-urlencoded body, else {}
    .json       the parsed JSON body (Content-Type application/json), None if
                there is none; a body that is not valid JSON answers 400
    .headers    case-insensitive: request.headers["content-type"], .get(name)
    .cookies    a dict   .body bytes   .text the body as a str

COOKIES  Response(...).set_cookie("name", "value", max_age=None, path="/",
httponly=False, secure=False, samesite=None, domain=None) and .delete_cookie(name).

TEMPLATES  render("Hello $name", name=value): string.Template substitution
(`$name` or `${name}`, `$$` for a dollar sign) that HTML-escapes every value,
so a value holding <script> shows as text instead of running. A fragment that
is already safe HTML (another render(), or escape()) passes through: wrap
anything else you really mean as HTML in safe(...).

This file is the whole library; the harness (driver.py) only starts it.
"""

from __future__ import annotations

import contextlib
import html
import http.server
import inspect
import json as _json
import re
import string
import sys
import threading
import traceback
from collections.abc import Mapping
from http.cookies import CookieError, SimpleCookie
from urllib.parse import parse_qs, unquote

#: The learner's program is compiled under this name, so a traceback names it.
APP_FILE = "app.py"
HOST = "127.0.0.1"
#: The largest request body taken (bytes).
MAX_BODY = 1_000_000
_METHODS = ("GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS")
_PARAM = re.compile(r"<(?:(int|str):)?([A-Za-z_][A-Za-z0-9_]*)>")
_REDIRECTS = (301, 302, 303, 307, 308)


class TimeLimit(BaseException):
    """Raised in a route by the harness when it runs too long (not an Exception: `except Exception` won't eat it)."""


class _Hooks:
    """What the harness plugs in; by default nothing."""

    #: `with hooks.guard():` around every route call (a watchdog in the harness).
    guard = staticmethod(contextlib.nullcontext)


hooks = _Hooks()


# -- Headers ------------------------------------------------------------------


class Headers:
    """Case-insensitive headers that keep repeats: h["content-type"], h.get(name, default), name in h."""

    def __init__(self, source=()) -> None:
        self._pairs: list[tuple[str, str]] = []
        pairs = source.items() if isinstance(source, (Mapping, Headers)) else source
        for name, value in pairs:
            self.add(name, value)

    def add(self, name, value) -> None:
        self._pairs.append((str(name), str(value)))

    def set(self, name, value) -> None:
        del self[name]
        self.add(name, value)

    def get(self, name, default=None):
        lowered = str(name).lower()
        for key, value in self._pairs:
            if key.lower() == lowered:
                return value
        return default

    def getlist(self, name) -> list[str]:
        lowered = str(name).lower()
        return [value for key, value in self._pairs if key.lower() == lowered]

    def __getitem__(self, name):
        found = self.get(name)
        if found is None:
            raise KeyError(name)
        return found

    def __setitem__(self, name, value) -> None:
        self.set(name, value)

    def __delitem__(self, name) -> None:
        lowered = str(name).lower()
        self._pairs = [(k, v) for k, v in self._pairs if k.lower() != lowered]

    def __contains__(self, name) -> bool:
        return self.get(name) is not None

    def __iter__(self):
        seen: set[str] = set()
        for key, _ in self._pairs:
            if key.lower() not in seen:
                seen.add(key.lower())
                yield key

    def __len__(self) -> int:
        return len(list(iter(self)))

    def keys(self):
        return list(iter(self))

    def items(self) -> list[tuple[str, str]]:
        """Every (name, value) pair, repeats included."""
        return list(self._pairs)

    def __repr__(self) -> str:
        return f"Headers({self._pairs!r})"


# -- Errors, escaping, templates ---------------------------------------------------


class HTTPError(Exception):
    """What abort() raises: a status, and a message for whoever reads the page."""

    def __init__(self, status: int, message: str = "", headers=None) -> None:
        super().__init__(status, message)
        self.status = int(status)
        self.message = str(message or "")
        self.headers = dict(headers or {})

    @property
    def reason(self) -> str:
        return _reason(self.status)

    def __str__(self) -> str:
        return f"{self.status} {self.reason}" + (f": {self.message}" if self.message else "")


def _reason(status: int) -> str:
    return http.server.BaseHTTPRequestHandler.responses.get(status, ("",))[0]


def abort(status: int, message: str = ""):
    """Stop the route now and answer with this status (and, on the page, this message)."""
    raise HTTPError(status, message)


class safe(str):
    """Text that is already safe HTML: render() will not escape it again."""


def escape(text) -> safe:
    """Make text safe to put in HTML (& < > " ' become entities). Already-safe text is left alone."""
    if isinstance(text, safe):
        return text
    return safe(html.escape(str(text), quote=True))


def render(template, /, **values) -> safe:
    """Fill a $name template; every value is HTML-escaped unless it is safe(...)."""
    cooked = {name: escape(value) for name, value in values.items()}
    try:
        return safe(string.Template(str(template)).substitute(cooked))
    except KeyError as missing:
        raise KeyError(
            f"render(): the template uses ${missing.args[0]} but no value called "
            f"{missing.args[0]!r} was given"
        ) from None
    except ValueError as bad:
        raise ValueError(f"render(): {bad} (a literal dollar sign in a template is written $$)") from None


# -- The request ------------------------------------------------------------------


def _parse_cookies(header: str) -> dict[str, str]:
    jar: dict[str, str] = {}
    for part in header.split(";"):
        name, sep, value = part.partition("=")
        name, value = name.strip(), value.strip()
        if not sep or not name:
            continue
        if len(value) >= 2 and value[0] == value[-1] == '"':
            # A quoted value: a backslash and three octal digits is one character, backslash-quote a quote.
            value = re.sub(r"\\(?:([0-3][0-7]{2})|(.))",
                           lambda m: chr(int(m.group(1), 8)) if m.group(1) else m.group(2), value[1:-1])
        jar.setdefault(name, value)
    return jar


class Request:
    def __init__(self, method: str, target: str, headers: Headers, body: bytes) -> None:
        self.method = method
        target = target.split("#", 1)[0]
        raw_path, _, self.query_string = target.partition("?")
        self.raw_path = raw_path or "/"
        self.path = unquote(self.raw_path, errors="replace")
        self.headers = headers
        self.body = body
        self.args_all: dict[str, list[str]] = parse_qs(
            self.query_string, keep_blank_values=True, errors="replace")
        self.args: dict[str, str] = {name: values[0] for name, values in self.args_all.items()}
        self.cookies = _parse_cookies("; ".join(headers.getlist("Cookie")))
        self._form: dict[str, str] | None = None
        self._json: tuple | None = None

    @property
    def content_type(self) -> str:
        return (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()

    @property
    def text(self) -> str:
        return self.body.decode("utf-8", "replace")

    @property
    def form(self) -> dict[str, str]:
        if self._form is None:
            self._form = {}
            if self.content_type == "application/x-www-form-urlencoded":
                parsed = parse_qs(self.text, keep_blank_values=True, errors="replace")
                self._form = {name: values[0] for name, values in parsed.items()}
        return self._form

    @property
    def json(self):
        if self._json is None:
            value = None
            kind = self.content_type
            if self.body.strip() and (kind == "application/json" or kind.endswith("+json")):
                try:
                    value = _json.loads(self.text)
                except ValueError as bad:
                    raise HTTPError(400, f"The request body is not valid JSON ({bad}).") from None
            self._json = (value,)
        return self._json[0]


_local = threading.local()


class _RequestProxy:
    """`request`: whichever request this thread is answering."""

    def _current(self) -> Request:
        current = getattr(_local, "request", None)
        if current is None:
            raise RuntimeError("`request` only works inside a route, while a request is being answered.")
        return current

    def __getattr__(self, name: str):
        return getattr(self._current(), name)

    def __repr__(self) -> str:
        current = getattr(_local, "request", None)
        return f"<request {current.method} {current.path}>" if current else "<request (none right now)>"


request = _RequestProxy()


# -- The response ---------------------------------------------------------------------


def _check_header(name: str, value: str) -> None:
    for text in (name, value):
        if "\r" in text or "\n" in text or "\x00" in text:
            raise ValueError(f"a header cannot contain a line break: {name!r}")
    if not name or not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", name):
        raise ValueError(f"not a header name: {name!r}")


class Response:
    """A whole answer: body (str or bytes), status, headers - and cookies, with set_cookie()."""

    def __init__(self, body="", status: int = 200, headers=None) -> None:
        self.body = body
        self.status = status
        self.headers = Headers(headers or {})
        self._cookies: list[str] = []

    def set_cookie(self, name: str, value="", *, max_age=None, path: str | None = "/", domain=None,
                   secure: bool = False, httponly: bool = False, samesite=None) -> None:
        jar: SimpleCookie = SimpleCookie()
        try:
            jar[str(name)] = str(value)
        except CookieError as bad:
            raise ValueError(f"set_cookie: {bad}") from None
        morsel = jar[str(name)]
        if max_age is not None:
            morsel["max-age"] = int(max_age)
        if path:
            morsel["path"] = path
        if domain:
            morsel["domain"] = domain
        if secure:
            morsel["secure"] = True
        if httponly:
            morsel["httponly"] = True
        if samesite:
            morsel["samesite"] = str(samesite)
        self._cookies.append(morsel.OutputString())

    def delete_cookie(self, name: str, path: str = "/") -> None:
        self.set_cookie(name, "", max_age=0, path=path)


def json_response(data, status: int = 200, headers=None) -> Response:
    """A Response whose body is data as JSON, with the right Content-Type."""
    made = Response(_json.dumps(data), status, headers)
    if "Content-Type" not in made.headers:
        made.headers["Content-Type"] = "application/json"
    return made


def redirect(url: str, code: int = 302) -> Response:
    """A redirect to `url`: the browser (or client) must make a second request there."""
    if code not in _REDIRECTS:
        raise ValueError(f"redirect: the code must be one of {_REDIRECTS}, not {code!r}")
    _check_header("Location", str(url))
    shown = html.escape(str(url), quote=True)
    body = f'<!doctype html><title>Redirecting</title><p>Redirecting to <a href="{shown}">{shown}</a>.</p>'
    return Response(body, code, {"Location": str(url)})


def _looks_like_headers(value) -> bool:
    return isinstance(value, (Mapping, Headers))


def _describe(fn) -> str:
    where = ""
    try:
        where = f", {APP_FILE} line {fn.__code__.co_firstlineno}"
    except AttributeError:
        pass
    return f"`{getattr(fn, '__name__', 'the route')}`{where}"


def make_response(rv, fn=None) -> Response:
    """What a route returned, as a Response (see the module docstring for the rules)."""
    status = headers = None
    body = rv
    if isinstance(rv, tuple):
        if len(rv) == 1:
            (body,) = rv
        elif len(rv) == 2:
            body, second = rv
            if _looks_like_headers(second):
                headers = second
            else:
                status = second
        elif len(rv) == 3:
            body, status, headers = rv
        else:
            raise TypeError("a route may return (body), (body, status) or (body, status, headers)")
    if isinstance(body, Response):
        response = body
    elif body is None:
        raise TypeError(
            f"the route {_describe(fn)} returned None. A route has to return something - "
            "did you forget `return`?")
    elif isinstance(body, bool) or not isinstance(body, (str, bytes, bytearray, dict, list)):
        raise TypeError(
            f"the route {_describe(fn)} returned a {type(body).__name__}. Return a str, a dict or "
            "list (JSON), a tuple (body, status) or a Response.")
    elif isinstance(body, (dict, list)):
        response = json_response(body)
    else:
        response = Response(body)
    if status is not None:
        if isinstance(status, bool) or not isinstance(status, int):
            raise TypeError(f"the status has to be an int like 404, not {status!r}")
        response.status = status
    if headers is not None:
        for name, value in (headers.items() if _looks_like_headers(headers) else headers):
            response.headers[name] = value
    return response


def _finalize(response: Response) -> tuple[int, list[tuple[str, str]], bytes]:
    """Check a Response and turn it into (status, header pairs, body bytes)."""
    status = response.status
    if isinstance(status, bool) or not isinstance(status, int) or not 100 <= status <= 599:
        raise TypeError(f"the status has to be a whole number from 100 to 599, not {status!r}")
    body = response.body
    default_type = "text/html; charset=utf-8"
    if isinstance(body, (bytes, bytearray)):
        data, default_type = bytes(body), "application/octet-stream"
    elif isinstance(body, str):
        data = body.encode("utf-8")
    else:
        raise TypeError(
            f"a Response body has to be a str or bytes, not a {type(body).__name__} "
            "(for a dict or list use json_response)")
    pairs = response.headers.items()
    names = {name.lower() for name, _ in pairs}
    if status < 200 or status in (204, 304):
        if data:
            print(f"A {status} {_reason(status)} answer has no body, so the body was not sent.")
        data = b""
    elif "content-type" not in names:
        pairs.append(("Content-Type", default_type))
    out: list[tuple[str, str]] = []
    for name, value in pairs:
        if name.lower() in ("content-length", "connection", "transfer-encoding"):
            continue
        if name.lower() == "content-type":
            media = value.split(";", 1)[0].strip().lower()
            if media.startswith("text/") and "charset" not in value.lower():
                value = f"{value}; charset=utf-8"
        out.append((name, value))
    out.extend(("Set-Cookie", cookie) for cookie in response._cookies)
    for name, value in out:
        _check_header(name, value)
    return status, out, data


# -- Routing --------------------------------------------------------------------------


class _Route:
    def __init__(self, order: int, methods: set[str], pattern: str, handler) -> None:
        self.order = order
        self.methods = methods
        self.pattern = pattern
        self.handler = handler
        self.parts: list[tuple[str, str]] = []  # ("lit", text) | ("str", name) | ("int", name)
        if pattern != "/":
            for piece in pattern.strip("/").split("/"):
                found = _PARAM.fullmatch(piece)
                if found:
                    self.parts.append((found.group(1) or "str", found.group(2)))
                elif "<" in piece or ">" in piece:
                    raise ValueError(
                        f"the route {pattern!r}: write a parameter as <name> or <int:name>, "
                        "filling a whole /segment/")
                else:
                    self.parts.append(("lit", piece))
        # Static before int before str, then the order they were written.
        self.weight = tuple({"lit": 0, "int": 1, "str": 2}[kind] for kind, _ in self.parts)
        self.shape = tuple((kind, text if kind == "lit" else "") for kind, text in self.parts)

    def match(self, segments: list[str]) -> dict | None:
        if len(segments) != len(self.parts):
            return None
        params: dict = {}
        for (kind, text), segment in zip(self.parts, segments):
            if kind == "lit":
                if segment != text:
                    return None
            elif not segment:
                return None
            elif kind == "int":
                if not (segment.isascii() and segment.isdigit() and len(segment) <= 18):
                    return None
                params[text] = int(segment)
            else:
                params[text] = segment
        return params


def _segments(path: str) -> list[str]:
    stripped = path.strip("/")
    return [unquote(piece, errors="replace") for piece in stripped.split("/")] if stripped else []


def _wants_json(req: Request) -> bool:
    accept = (req.headers.get("Accept") or "").lower()
    return "application/json" in accept and "text/html" not in accept


class App:
    def __init__(self) -> None:
        self._routes: list[_Route] = []
        self._error_handlers: dict[int, object] = {}

    # -- registering ---------------------------------------------------------------
    def route(self, path: str, methods=None):
        """@app.route("/x", methods=["GET", "POST"]): the decorator that registers a route function."""
        if not isinstance(path, str) or not path.startswith("/"):
            raise ValueError(f"a route's path must be a string starting with '/', not {path!r}")
        wanted = {m.upper() for m in ([methods] if isinstance(methods, str) else (methods or ["GET"]))}
        for method in wanted:
            if method not in _METHODS:
                raise ValueError(f"{method!r} is not a method this app serves (use one of {', '.join(_METHODS)})")

        def register(fn):
            rule = _Route(len(self._routes), wanted, path, fn)
            self._check_signature(rule, fn)
            for other in self._routes:
                if other.shape == rule.shape and other.methods & rule.methods:
                    clash = sorted(other.methods & rule.methods)[0]
                    raise ValueError(
                        f"{clash} {path} is already a route (`{other.handler.__name__}`): the second "
                        f"one, `{fn.__name__}`, could never run")
            self._routes.append(rule)
            return fn

        return register

    def get(self, path: str):
        return self.route(path, ["GET"])

    def post(self, path: str):
        return self.route(path, ["POST"])

    def put(self, path: str):
        return self.route(path, ["PUT"])

    def delete(self, path: str):
        return self.route(path, ["DELETE"])

    def patch(self, path: str):
        return self.route(path, ["PATCH"])

    def errorhandler(self, status: int):
        """@app.errorhandler(404): a function(error) that answers instead of the plain error page."""
        if isinstance(status, bool) or not isinstance(status, int) or not 400 <= status <= 599:
            raise TypeError("errorhandler takes a status code such as 404 or 500")

        def register(fn):
            self._error_handlers[status] = fn
            return fn

        return register

    def run(self, *args, **kwargs) -> None:
        print("app.run() is not needed here - Code Coach starts your app itself.")

    def routes(self) -> list[dict]:
        """Every (method, path) the program routed, in the order written."""
        return [{"method": method, "path": rule.pattern}
                for rule in self._routes for method in sorted(rule.methods)]

    @staticmethod
    def _check_signature(rule: _Route, fn) -> None:
        try:
            params = inspect.signature(fn).parameters
        except (TypeError, ValueError):
            return
        names = [name for kind, name in rule.parts if kind != "lit"]
        if any(p.kind is inspect.Parameter.VAR_KEYWORD for p in params.values()):
            return
        for name in names:
            if name not in params:
                raise TypeError(
                    f"the route {rule.pattern!r} passes `{name}` to {fn.__name__}(), but {fn.__name__}() "
                    f"has no parameter called `{name}`")
        for name, p in params.items():
            if name not in names and p.default is inspect.Parameter.empty and p.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                raise TypeError(
                    f"{fn.__name__}() needs `{name}`, but the route {rule.pattern!r} has no <{name}> in it")

    # -- answering -----------------------------------------------------------------
    def _find(self, req: Request):
        """(route, params) for the method, or the error to answer with."""
        segments = _segments(req.raw_path)
        found = [(rule, params) for rule in self._routes
                 if (params := rule.match(segments)) is not None]
        if not found:
            raise HTTPError(404, f"Nothing is routed at {req.path}.")
        method = req.method
        wanted = {method}
        if method == "HEAD":
            wanted = {"HEAD", "GET"}
        usable = [(r, p) for r, p in found if r.methods & wanted]
        allowed = sorted({m for r, _ in found for m in r.methods}
                         | ({"HEAD"} if any("GET" in r.methods for r, _ in found) else set())
                         | {"OPTIONS"})
        if usable:
            usable.sort(key=lambda rp: (rp[0].weight, rp[0].order))
            return usable[0]
        if method == "OPTIONS":
            raise HTTPError(204, "", {"Allow": ", ".join(allowed)})
        raise HTTPError(405, f"{req.path} does not accept {method}. It allows: {', '.join(allowed)}.",
                        {"Allow": ", ".join(allowed)})

    def _run(self, fn, *args, **kwargs):
        with hooks.guard():
            return fn(*args, **kwargs)

    def _default_error(self, err: HTTPError, req: Request) -> Response:
        if _wants_json(req):
            made = json_response({"error": err.reason, "status": err.status, "message": err.message}, err.status)
        else:
            title = f"{err.status} {err.reason}"
            body = (f"<!doctype html><title>{html.escape(title)}</title><h1>{html.escape(title)}</h1>"
                    + (f"<p>{html.escape(err.message)}</p>" if err.message else ""))
            made = Response(body, err.status)
        return made

    def _error_response(self, err: HTTPError, req: Request) -> Response:
        handler = self._error_handlers.get(err.status)
        made = None
        if handler is not None:
            try:
                try:
                    takes = len([p for p in inspect.signature(handler).parameters.values()
                                 if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL)])
                except (TypeError, ValueError):
                    takes = 1
                made = make_response(self._run(handler, err) if takes else self._run(handler), handler)
            except HTTPError:
                made = None
            except TimeLimit:
                print(f"The errorhandler for {err.status} ran out of time.")
            except Exception as exc:  # noqa: BLE001 - the learner's code; reported, then the plain page
                _print_failure(req, exc, f"the errorhandler for {err.status} failed")
        if made is None:
            made = self._default_error(err, req)
        for name, value in err.headers.items():
            made.headers[name] = value
        return made

    def dispatch(self, req: Request) -> tuple[int, list[tuple[str, str]], bytes]:
        """Answer a request: (status, header pairs, body). Never raises for the learner's mistakes."""
        try:
            try:
                rule, params = self._find(req)
                response = make_response(self._run(rule.handler, **params), rule.handler)
            except HTTPError as err:
                if err.status == 204 and req.method == "OPTIONS":
                    response = Response("", 204, err.headers)
                else:
                    response = self._error_response(err, req)
            return _finalize(response)
        except TimeLimit:
            return self._failed(req, None, "the route ran out of time. Is there a loop that never ends?")
        except Exception as exc:  # noqa: BLE001 - the learner's code; reported, answered with a 500
            return self._failed(req, exc, "")

    def _failed(self, req: Request, exc, note: str) -> tuple[int, list[tuple[str, str]], bytes]:
        if exc is not None:
            _print_failure(req, exc, note)
        else:
            print(f"500 Internal Server Error: {req.method} {req.path}\n{note}")
        err = HTTPError(500, "Something went wrong in the app. The console has the details.")
        try:
            return _finalize(self._error_response(err, req))
        except Exception:  # noqa: BLE001 - the 500 page itself must always get out
            return _finalize(self._default_error(err, req))


def _print_failure(req: Request, exc: BaseException, note: str) -> None:
    """The console's copy of a 500: which request, and the traceback as far as the learner's own lines."""
    lines = [f"500 Internal Server Error: {req.method} {req.path}" + (f" ({note})" if note else "")]
    frames = [f for f in traceback.extract_tb(exc.__traceback__) if f.filename == APP_FILE]
    if frames:
        lines.append("Traceback (most recent call last):")
        lines.extend("".join(traceback.format_list(frames)).rstrip().split("\n"))
    lines.extend("".join(traceback.format_exception_only(type(exc), exc)).rstrip().split("\n"))
    print("\n".join(lines))


#: The one app a program has: `from web import app`.
app = App()


# -- The server -------------------------------------------------------------------------


class _Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"  # one request per connection: nothing lingers to be shut down
    server_version = "CodeCoachWeb/1.0"
    sys_version = ""
    timeout = 10  # a client that goes quiet cannot hold a thread for ever

    def version_string(self) -> str:
        return self.server_version

    def log_message(self, format, *args) -> None:  # noqa: A002 - the base class's signature
        pass

    def _answer(self, status: int, pairs, body: bytes, head: bool) -> None:
        self.send_response(status)
        for name, value in pairs:
            self.send_header(name, value)
        if status >= 200 and status not in (204, 304):
            self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if body and not head:
            self.wfile.write(body)

    def _serve(self) -> None:
        method = self.command
        if self.headers.get("Transfer-Encoding"):
            return self._plain(411, "Send a Content-Length instead of chunked encoding.")
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._plain(400, "The Content-Length is not a number.")
        if length < 0:
            return self._plain(400, "The Content-Length is negative.")
        if length > MAX_BODY:
            return self._plain(413, f"The body is over {MAX_BODY} bytes.")
        body = self.rfile.read(length) if length else b""
        headers = Headers(self.headers.items())
        req = Request(method, self.path, headers, body)
        _local.request = req
        try:
            status, pairs, data = app.dispatch(req)
        finally:
            _local.request = None
        self._answer(status, pairs, data, head=method == "HEAD")

    def _plain(self, status: int, message: str) -> None:
        data = f"{status} {_reason(status)}: {message}\n".encode()
        self._answer(status, [("Content-Type", "text/plain; charset=utf-8")], data, head=False)

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_HEAD = do_OPTIONS = _serve


class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False
    request_queue_size = 32

    def handle_error(self, request, client_address) -> None:
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionError, TimeoutError)):
            return  # a client that hung up is not the learner's bug
        traceback.print_exc()


def make_server() -> http.server.ThreadingHTTPServer:
    """The server for `app`, bound to 127.0.0.1 on a port the system picks. Not started."""
    return _Server((HOST, 0), _Handler)
