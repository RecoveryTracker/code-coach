"""Python web servers and HTTP.

Ten pages of programs that run as plain `python file.py`: URLs with
urllib.parse, status codes and reasons, headers and content types, a raw
request parsed by hand, a router made from a dict, GET routes on http.server,
a JSON API, cookies, a WSGI app called as a plain function, and HTML built
from templates.

Everything is deterministic:

- a server binds 127.0.0.1 on port 0 (the system picks a free port), runs
  in a daemon thread with serve_forever(0.01) so that shutdown() returns at
  once, answers the requests the program makes to it with urllib.request,
  and is shut down and closed again; no program prints a port or a path;
- the pages that only need to understand HTTP never open a socket: a raw
  request is a string, a response is built from a dict, and a WSGI app is
  called as a function with a made-up environ and a start_response;
- headers are printed with the cookie and header functions that give a fixed
  order, and nothing here prints a date, a random token or a timing.

The oracle never runs the Python it describes. It works every answer out
with small models written here (a URL splitter, a query-string decoder, a
percent-encoder, a relative-URL resolver, a status table, a request parser,
a router, the little server each program stands up, a cookie writer, a WSGI
app and a template engine), and the tests then hold python to it. The
models are the reason this module imports only `re`. Rows that could print
two ways are refused with ValueError.
"""

from __future__ import annotations

import re

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("py_web_url", "urllib.parse: urlsplit, parse_qs, urlencode, quote and urljoin"),
    Shape("py_web_status", "http.HTTPStatus phrases and names, and classifying status codes"),
    Shape("py_web_headers", "building a raw response from a dict: status line, headers, content types"),
    Shape("py_web_request", "splitting a raw HTTP request into its line, headers and body"),
    Shape("py_web_route", "routing a path to a handler function with a dict"),
    Shape("py_web_get", "a tiny http.server in a thread: GET routes, queries, 404 and 405"),
    Shape("py_web_api", "a JSON API on http.server: POST a body, get JSON back"),
    Shape("py_web_cookies", "http.cookies.SimpleCookie: parsing, building and attributes"),
    Shape("py_web_wsgi", "a WSGI app called as a function with a fake environ"),
    Shape("py_web_template", "string.Template and str.format building HTML"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: How long a program may be. A server needs a handler class, a thread and
#: a client, which no honest program does in ten lines; a router, a WSGI app
#: and a template page need room for a few functions.
LIMIT = 10
SERVER_LIMIT = 28
_LIMITS = {
    "py_web_route": 18,
    "py_web_wsgi": 16,
    "py_web_template": 12,
    "py_web_get": SERVER_LIMIT,
    "py_web_api": SERVER_LIMIT,
}

#: The shapes that stand a server up.
SERVERS = ("py_web_get", "py_web_api")


def limit_for(shape: str) -> int:
    return _LIMITS.get(shape, LIMIT)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Writing things the program types ─────────────────────────

#: Text that sits safely inside a double-quoted Python string.
_PLAIN = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()\-]+")
#: A URL, or a piece of one: no spaces, and an ampersand is allowed.
_URLCH = re.compile(r"[A-Za-z0-9_.,:/=@%+?#&\-]+")
#: Text for percent-encoding: a few characters that are not safe, and an accent.
_QTEXT = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()&é\-]+")
#: Text that goes into HTML: angle brackets, ampersands and quotes too.
_HTMLCH = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()<>&'\"\-]+")
_WORD = re.compile(r"[a-z][a-z0-9]*")
_HEADER = re.compile(r"[A-Z][A-Za-z]*(-[A-Z][A-Za-z]*)*")
_PATH = re.compile(r"/[A-Za-z0-9/._\-]*")


def _ok(rx, x, why: str = "plain text only"):
    if not isinstance(x, str) or not rx.fullmatch(x):
        raise ValueError(f"{x!r}: {why}")
    return x


def _s(x) -> str:
    """A string literal. Quotes, backslashes and the like are refused."""
    return _q(_ok(_PLAIN, x))


def _u(x) -> str:
    """A string literal for a URL."""
    return _q(_ok(_URLCH, x, "a URL with no spaces"))


def _lit(x, rx=None) -> str:
    """A string literal for HTML: single quotes when it holds double ones."""
    _ok(rx or _HTMLCH, x, "plain text, or HTML")
    if '"' in x and "'" in x:
        raise ValueError(f"{x!r}: both kinds of quote")
    return "'" + x + "'" if '"' in x else _q(x)


def _int(x) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: a whole number")
    return x


def _word(x) -> str:
    return _ok(_WORD, x, "one lowercase word")


def _path(x) -> str:
    """A plain URL path, with no query string."""
    return _ok(_PATH, x, "a plain URL path")


def _unique(items, what: str = "items") -> list:
    items = list(items)
    if len(set(items)) != len(items):
        raise ValueError(f"{what} must be unique")
    return items


def _fit(lines, limit: int = LIMIT) -> str:
    """The program, with blank lines dropped one by one if it runs long."""
    lines = list(lines)
    while len(lines) > limit and "" in lines:
        lines.remove("")
    if len(lines) > limit:
        raise ValueError(f"{len(lines)} lines is too many")
    return NL.join(lines)


def _pyval(v) -> str:
    """A Python literal for a plain value."""
    if isinstance(v, bool) or v is None:
        return repr(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, str):
        return _s(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_pyval(i) for i in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{_s(k)}: {_pyval(x)}" for k, x in v.items()) + "}"
    raise ValueError(f"{v!r}: not a plain value")


def _qval(v) -> str:
    """A literal for a value that is going to be percent-encoded."""
    if isinstance(v, list):
        return "[" + ", ".join(_qval(x) for x in v) + "]"
    if isinstance(v, str):
        return _q(_ok(_QTEXT, v))
    return _pyval(v)


def _pairs(pairs) -> list[tuple[str, str]]:
    pairs = [tuple(p) for p in pairs]
    if any(len(p) != 2 for p in pairs):
        raise ValueError("pairs")
    return pairs


# ── Percent-encoding, by hand ────────────────────────────────

_UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-~")


def _pct(text: str, safe: str = "", plus: bool = False) -> str:
    """Percent-encode: every byte that is not plain becomes %XX, upper case."""
    out = []
    for ch in text:
        if ch in _UNRESERVED or ch in safe:
            out.append(ch)
        elif ch == " " and plus:
            out.append("+")
        else:
            out.extend(f"%{b:02X}" for b in ch.encode("utf-8"))
    return "".join(out)


def _unpct(text: str) -> str:
    """The other way: + is a space and %XX is a byte of UTF-8."""
    text = text.replace("+", " ")
    out = bytearray()
    i = 0
    while i < len(text):
        if text[i] == "%":
            code = text[i + 1:i + 3]
            if not re.fullmatch(r"[0-9A-Fa-f]{2}", code):
                raise ValueError("a bad escape")
            out.append(int(code, 16))
            i += 3
        else:
            out.extend(text[i].encode("utf-8"))
            i += 1
    return out.decode("utf-8")


def _qs(query: str) -> dict[str, list[str]]:
    """A query string read by hand: values in lists, blanks dropped."""
    if ";" in query:
        raise ValueError("no semicolons")
    found: dict[str, list[str]] = {}
    for pair in query.split("&"):
        if not pair:
            continue
        key, eq, value = pair.partition("=")
        if not key:
            raise ValueError("every parameter needs a name")
        if not eq or not value:
            continue  # parse_qs drops a parameter with no value
        found.setdefault(_unpct(key), []).append(_unpct(value))
    return found


_SHOWN = re.compile(r"[A-Za-z0-9 _.,:;/=@+!?#()\-]*")


def _tame(found: dict[str, list[str]]) -> None:
    """Values whose repr is the same on every road: no quotes, no accents."""
    for k, vs in found.items():
        for x in (k, *vs):
            if not _SHOWN.fullmatch(x):
                raise ValueError(f"{x!r}: plain text once decoded")


# ── 1. URLs ──────────────────────────────────────────────────

_PARTS = ("scheme", "netloc", "path", "query", "fragment")
_SCHEMED = re.compile(
    r"([A-Za-z][A-Za-z0-9+.\-]*)://([^/?#]*)([^?#]*)(?:\?([^#]*))?(?:#(.*))?")
_HOST = re.compile(r"[A-Za-z0-9.\-]+(:[0-9]+)?")


def _split_url(url: str) -> tuple[str, str, str, str, str]:
    m = _SCHEMED.fullmatch(_ok(_URLCH, url, "a URL with no spaces"))
    if not m:
        raise ValueError(f"{url!r}: scheme://host/path")
    scheme, netloc, path, query, frag = m.groups()
    if not _HOST.fullmatch(netloc):
        raise ValueError(f"{netloc!r}: a plain host")
    return scheme.lower(), netloc, path, query or "", frag or ""


def _host_port(netloc: str) -> tuple[str, int | None]:
    host, colon, port = netloc.partition(":")
    if not colon:
        return host.lower(), None
    if not port.isdigit() or not 1 <= int(port) <= 65535:
        raise ValueError("a port from 1 to 65535")
    return host.lower(), int(port)


def _dots(path: str) -> str:
    """Remove . and .. pieces from an absolute path."""
    pieces = path.split("/")
    out: list[str] = []
    for i, piece in enumerate(pieces):
        last = i == len(pieces) - 1
        if piece == ".":
            if last:
                out.append("")
        elif piece == "..":
            if len(out) <= 1:
                raise ValueError("a .. that climbs above the root")
            out.pop()
            if last:
                out.append("")
        else:
            out.append(piece)
    return "/".join(out)


_REF = re.compile(r"(?://([^/?#]*))?([^?#]*)(?:\?([^#]*))?(?:#(.*))?")


def _join(base: str, ref: str) -> str:
    """A relative URL resolved against a base, the way a browser does."""
    scheme, netloc, path, query, _ = _split_url(base)
    if not path.startswith("/") or not ref:
        raise ValueError("a base with a path, and a reference")
    _ok(_URLCH, ref, "a URL with no spaces")
    if re.match(r"[A-Za-z][A-Za-z0-9+.\-]*://", ref):
        _split_url(ref)
        return ref
    if ":" in ref:
        raise ValueError("a colon is a scheme to urljoin")
    m = _REF.fullmatch(ref)
    r_net, r_path, r_query, r_frag = m.groups()
    if r_net is not None:
        if not r_path.startswith("/"):
            raise ValueError("a host reference needs a path")
        r_path = _dots(r_path)
        netloc, query = r_net, r_query or ""
    elif r_path == "":
        r_path = path
        if r_query is not None:
            query = r_query
    elif r_path.startswith("/"):
        r_path, query = _dots(r_path), r_query or ""
    else:
        r_path = _dots(path[:path.rfind("/") + 1] + r_path)
        query = r_query or ""
    return (f"{scheme}://{netloc}{r_path}" + (f"?{query}" if query else "")
            + (f"#{r_frag}" if r_frag else ""))


def _url(a: dict) -> str:
    want = a["want"]
    head = "from urllib.parse import "
    if want in ("part", "port"):
        _split_url(a["url"])
        lines = [head + "urlsplit", "", f"parts = urlsplit({_u(a['url'])})"]
        if want == "port":
            return _fit([*lines, "print(parts.hostname, parts.port)"])
        part = a["part"]
        if part not in _PARTS:
            raise ValueError(part)
        return _fit([*lines, f'print(parts.{part} or "none")'])
    if want == "qs":
        key = a.get("key")
        shown = {"dict": "print(found)", "keys": "print(list(found))",
                 "first": f"print(found[{_s(key)}][0])" if key else "",
                 "all": f"print(found[{_s(key)}])" if key else ""}[a["show"]]
        return _fit([head + "parse_qs", "", f"query = {_u(a['query'])}",
                     "found = parse_qs(query)", shown])
    if want == "quote":
        text, safe = a["text"], a.get("safe")
        call = "quote(text)" if safe is None else 'quote(text, safe="")'
        return _fit([head + "quote", "", f"text = {_q(_ok(_QTEXT, text))}", f"print({call})"])
    if want == "urlencode":
        doseq = bool(a.get("doseq"))
        params = _pairs(a["params"])
        literal = "{" + ", ".join(f"{_s(k)}: {_qval(v)}" for k, v in params) + "}"
        call = "urlencode(params, doseq=True)" if doseq else "urlencode(params)"
        return _fit([head + "urlencode", "", f"params = {literal}", f"print({call})"])
    if want == "join":
        return _fit([head + "urljoin", "", f"base = {_u(a['base'])}",
                     f"print(urljoin(base, {_u(a['ref'])}))"])
    raise ValueError(want)


def _url_out(a: dict) -> str:
    want = a["want"]
    if want in ("part", "port"):
        scheme, netloc, path, query, frag = _split_url(a["url"])
        if want == "port":
            host, port = _host_port(netloc)
            return f"{host} {port}"
        part = a["part"]
        if part not in _PARTS:
            raise ValueError(part)
        got = {"scheme": scheme, "netloc": netloc, "path": path,
               "query": query, "fragment": frag}[part]
        return got or "none"
    if want == "qs":
        found = _qs(_ok(_URLCH, a["query"], "a query string"))
        _tame(found)
        if not found:
            raise ValueError("a query with something in it")
        show, key = a["show"], a.get("key")
        if show == "dict":
            return repr(found)
        if show == "keys":
            return repr(list(found))
        if key not in found:
            raise ValueError("a key that is there")
        if show == "first":
            return found[key][0]
        if show == "all":
            if len(found[key]) < 2:
                raise ValueError("a key that repeats")
            return repr(found[key])
        raise ValueError(show)
    if want == "quote":
        text, safe = _ok(_QTEXT, a["text"]), a.get("safe")
        if safe not in (None, ""):
            raise ValueError("the default safe set, or none")
        if safe is None and "/" in text and " " not in text:
            raise ValueError("a space, so the encoding shows")
        if safe == "" and "/" not in text:
            raise ValueError("a slash to encode")
        return _pct(text, safe="/" if safe is None else "")
    if want == "urlencode":
        doseq = bool(a.get("doseq"))
        parts = []
        for key, value in _pairs(a["params"]):
            _word(key)
            if isinstance(value, list):
                if not doseq or len(value) < 2:
                    raise ValueError("lists need doseq, and two items at least")
                values = value
            elif isinstance(value, (str, int)) and not isinstance(value, bool):
                values = [value]
            else:
                raise ValueError(f"{value!r}: text or a whole number")
            for v in values:
                text = str(v) if isinstance(v, int) else _ok(_QTEXT, v)
                parts.append(f"{_pct(key, plus=True)}={_pct(text, plus=True)}")
        _unique([k for k, _ in a["params"]], "keys")
        if len(parts) < 2:
            raise ValueError("two parameters at least")
        return "&".join(parts)
    if want == "join":
        return _join(a["base"], a["ref"])
    raise ValueError(want)


# ── 2. Status codes ──────────────────────────────────────────

#: Phrases that have read the same in every Python that has HTTPStatus.
_REASONS = {
    100: "Continue", 101: "Switching Protocols", 200: "OK", 201: "Created",
    202: "Accepted", 204: "No Content", 301: "Moved Permanently", 302: "Found",
    304: "Not Modified", 307: "Temporary Redirect", 308: "Permanent Redirect",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
    405: "Method Not Allowed", 408: "Request Timeout", 409: "Conflict",
    410: "Gone", 429: "Too Many Requests", 500: "Internal Server Error",
    501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable",
    504: "Gateway Timeout",
}
_KINDS = ("informational", "success", "redirection", "client error", "server error")


def _code(x) -> int:
    if _int(x) not in _REASONS:
        raise ValueError(f"{x!r}: a status code on the list")
    return x


def _member(code: int) -> str:
    """The name of the HTTPStatus member: the phrase in capitals."""
    return _REASONS[_code(code)].upper().replace(" ", "_")


def _codes(codes, low: int = 3, high: int = 6) -> list[int]:
    codes = [_code(c) for c in codes]
    if not low <= len(codes) <= high:
        raise ValueError(f"{low} to {high} codes")
    return _unique(codes, "codes")


def _status(a: dict) -> str:
    want = a["want"]
    imp = ["from http import HTTPStatus", ""]
    if want == "value":
        _code(a["code"])
        return _fit([*imp, f"print(HTTPStatus.{_member(a['code'])}.value)"])
    if want in ("phrase", "name"):
        return _fit([*imp, f"print(HTTPStatus({_code(a['code'])}).{want})"])
    if want == "line":
        return _fit([*imp, f"status = HTTPStatus({_code(a['code'])})",
                     'print(f"{status.value} {status.phrase}")'])
    codes = "[" + ", ".join(str(c) for c in _codes(a["codes"])) + "]"
    if want == "lookup":
        return _fit([*imp, f"codes = {codes}", "for code in codes:",
                     "    print(code, HTTPStatus(code).phrase)"])
    if want == "classify":
        kinds = "[" + ", ".join(f'"{k}"' for k in _KINDS) + "]"
        return _fit([f"KINDS = {kinds}", "", "def kind(code):",
                     "    return KINDS[code // 100 - 1]", "",
                     f"for code in {codes}:", "    print(code, kind(code))"])
    if want == "count":
        digit = _int(a["klass"])
        if not 1 <= digit <= 5:
            raise ValueError(digit)
        return _fit([f"codes = {codes}",
                     f"hits = [code for code in codes if code // 100 == {digit}]",
                     "print(len(hits))"])
    if want == "retry":
        return _fit([f"codes = {codes}",
                     "retry = [code for code in codes if code == 429 or code >= 500]",
                     "print(retry)"])
    raise ValueError(want)


def _status_out(a: dict) -> str:
    want = a["want"]
    if want in ("value", "phrase", "name", "line"):
        code = _code(a["code"])
        return {"value": str(code), "phrase": _REASONS[code], "name": _member(code),
                "line": f"{code} {_REASONS[code]}"}[want]
    codes = _codes(a["codes"])
    if want == "lookup":
        return NL.join(f"{c} {_REASONS[c]}" for c in codes)
    if want == "classify":
        return NL.join(f"{c} {_KINDS[c // 100 - 1]}" for c in codes)
    if want == "count":
        digit = _int(a["klass"])
        if not 1 <= digit <= 5:
            raise ValueError(digit)
        hits = [c for c in codes if str(c)[0] == str(digit)]
        if not hits or len(hits) == len(codes):
            raise ValueError("some codes in the class, and some outside it")
        return str(len(hits))
    if want == "retry":
        again = [c for c in codes if c == 429 or c >= 500]
        if not again or len(again) == len(codes):
            raise ValueError("some codes worth retrying, and some not")
        if 408 in codes:
            raise ValueError("408 is a puzzle of its own")
        return repr(again)
    raise ValueError(want)


# ── 3. Headers and content types ─────────────────────────────

_CRLF = "\\r\\n"
_UNI = re.compile(r"[A-Za-z0-9 _.,é日本\U0001F642-]+")


def _bytes_in(text: str) -> int:
    """The length of the UTF-8 form, counted from the code points."""
    total = 0
    for ch in text:
        point = ord(ch)
        total += 1 if point < 0x80 else 2 if point < 0x800 else 3 if point < 0x10000 else 4
    return total


def _headers_in(headers) -> list[tuple[str, str]]:
    pairs = _pairs(headers)
    names = [_ok(_HEADER, k, "a header name") for k, _ in pairs]
    if len({n.lower() for n in names}) != len(names):
        raise ValueError("header names must differ, even ignoring case")
    for _, v in pairs:
        _s(v)
        if v != v.strip():
            raise ValueError("no spaces at the ends of a value")
    return pairs


def _dict_text(pairs) -> str:
    return "{" + ", ".join(f"{_s(k)}: {_s(v)}" for k, v in pairs) + "}"


def _headers(a: dict) -> str:
    want = a["want"]
    if want == "statusline":
        return _fit(["from http import HTTPStatus", "", f"code = {_code(a['code'])}",
                     "status = HTTPStatus(code)",
                     'print(f"HTTP/1.1 {status.value} {status.phrase}")'])
    if want == "length":
        return _fit([f"body = {_q(_ok(_UNI, a['body']))}",
                     'size = len(body.encode("utf-8"))',
                     'print(f"Content-Length: {size}")'])
    if want == "ctype":
        types = _pairs(a["types"])
        lines = [f"TYPES = {_dict_text(types)}", f"name = {_s(a['name'])}",
                 'kind = TYPES.get(name.rsplit(".", 1)[-1].lower(), "application/octet-stream")']
        if a.get("charset"):
            lines += ['if kind.startswith("text/"):', '    kind += "; charset=utf-8"']
        return _fit([*lines, "print(kind)"])
    if want == "lookup":
        return _fit([f"headers = {_dict_text(_headers_in(a['headers']))}",
                     "lowered = {name.lower(): value for name, value in headers.items()}",
                     f"print(lowered[{_s(a['ask'])}])"])
    if want == "mediatype":
        return _fit([f"value = {_s(a['value'])}",
                     'media, _, params = value.partition(";")', 'charset = "none"',
                     'for param in params.split(";"):',
                     '    key, _, setting = param.strip().partition("=")',
                     '    if key == "charset":', "        charset = setting",
                     "print(media, charset)"])
    if want in ("raw", "rawlen"):
        status, body = _code(a["status"]), a["body"]
        lines = ["from http import HTTPStatus", "",
                 f"status, body = {status}, {_s(body)}",
                 f"headers = {_dict_text(_headers_in(a['headers']))}"]
        if want == "rawlen":
            lines.append('headers["Content-Length"] = str(len(body))')
        lines += ['lines = [f"HTTP/1.1 {status} {HTTPStatus(status).phrase}"]',
                  'lines += [f"{name}: {value}" for name, value in headers.items()]',
                  'print(repr("\\r\\n".join(lines) + "\\r\\n\\r\\n" + body))']
        return _fit(lines)
    raise ValueError(want)


def _headers_out(a: dict) -> str:
    want = a["want"]
    if want == "statusline":
        return f"HTTP/1.1 {_code(a['code'])} {_REASONS[a['code']]}"
    if want == "length":
        return f"Content-Length: {_bytes_in(_ok(_UNI, a['body']))}"
    if want == "ctype":
        types = dict(_pairs(a["types"]))
        name = _ok(_PLAIN, a["name"])
        ext = name[name.rfind(".") + 1:].lower()
        kind = types.get(ext, "application/octet-stream")
        if a.get("charset") and kind.startswith("text/"):
            kind += "; charset=utf-8"
        if len(types) < 3:
            raise ValueError("three types at least")
        return kind
    if want == "lookup":
        pairs = _headers_in(a["headers"])
        ask = _ok(_PLAIN, a["ask"])
        if ask != ask.lower():
            raise ValueError("ask in lower case")
        hits = [v for k, v in pairs if k.lower() == ask]
        if len(hits) != 1:
            raise ValueError("one header with that name")
        if ask in (k for k, _ in pairs):
            raise ValueError("ask in a different case from the header")
        return hits[0]
    if want == "mediatype":
        value = _ok(_PLAIN, a["value"])
        media, _, rest = value.partition(";")
        if not re.fullmatch(r"[a-z]+/[a-z+.\-]+", media):
            raise ValueError("a media type")
        charset = "none"
        for param in (p.strip() for p in rest.split(";")) if rest else []:
            if param.startswith("charset="):
                charset = param[len("charset="):]
            elif not re.fullmatch(r"[a-z]+=[A-Za-z0-9\-]+", param):
                raise ValueError("plain parameters")
        if charset != "none" and not re.fullmatch(r"[a-z0-9\-]+", charset):
            raise ValueError("a plain charset")
        return f"{media} {charset}"
    if want in ("raw", "rawlen"):
        status, body = _code(a["status"]), _ok(_PLAIN, a["body"])
        pairs = _headers_in(a["headers"])
        if "'" in body or not body.isascii():
            raise ValueError("a body with no quotes")
        if not 1 <= len(pairs) <= 3:
            raise ValueError("one to three headers")
        if body != body.strip():
            raise ValueError("no spaces at the ends of the body")
        if want == "rawlen":
            if any(k.lower() == "content-length" for k, _ in pairs):
                raise ValueError("the length is added by the program")
            pairs = [*pairs, ("Content-Length", str(len(body)))]
        head = [f"HTTP/1.1 {status} {_REASONS[status]}"] + [f"{k}: {v}" for k, v in pairs]
        return "'" + _CRLF.join(head) + _CRLF + _CRLF + body + "'"
    raise ValueError(want)


# ── 4. A raw request ─────────────────────────────────────────

_METHODS = ("GET", "POST", "PUT", "DELETE", "HEAD")


def _raw_literal(line: str, headers, body: str | None = None) -> str:
    """The request as the text a program is handed, with CRLF line breaks."""
    pairs = _headers_in(headers) if headers else []
    parts = [_ok(_URLCH_LINE, line, "a request line")]
    parts += [f"{k}: {v}" for k, v in pairs]
    text = _CRLF.join(parts) + _CRLF + _CRLF
    if body:
        text += _ok(_URLCH_LINE, body, "a plain body")
    return '"' + text + '"'


#: A request line or a body: URL characters and spaces.
_URLCH_LINE = re.compile(r"[A-Za-z0-9 _.,:/=@%+?#&\-]+")

_HEADER_LOOP = [
    "headers = {}", "for line in header_lines:",
    '    name, _, value = line.partition(":")',
    "    headers[name.strip().lower()] = value.strip()",
]
_HEAD_LINES = [
    'head, _, body = raw.partition("\\r\\n\\r\\n")',
    'request_line, *header_lines = head.split("\\r\\n")',
    'method, target, version = request_line.split(" ")',
]


def _request(a: dict) -> str:
    want = a["want"]
    if want == "valid":
        return _fit([f"raw = {_raw_literal(a['line'], a.get('headers'))}",
                     'request_line = raw.split("\\r\\n")[0]',
                     'parts = request_line.split(" ")',
                     'ok = len(parts) == 3 and parts[2].startswith("HTTP/")',
                     'print("ok" if ok else "400 Bad Request")'])
    raw = f"raw = {_raw_literal(a['line'], a.get('headers'), a.get('body'))}"
    head = [raw, *_HEAD_LINES]
    if want == "method":
        return _fit([*head, "print(method)"])
    if want == "target":
        return _fit([*head, "print(target)"])
    if want == "version":
        return _fit([*head, 'print(version.split("/")[1])'])
    if want == "triple":
        return _fit([*head, "print(method, target, version)"])
    if want == "path":
        return _fit([*head, 'path, _, query = target.partition("?")',
                     "print(path)", 'print(query or "none")'])
    if want == "count":
        return _fit([*head, "print(len(header_lines))"])
    if want == "names":
        return _fit([*head,
                     'print(", ".join(line.partition(":")[0] for line in header_lines))'])
    if want == "header":
        return _fit([*head, *_HEADER_LOOP, f"print(headers[{_s(a['ask'])}])"])
    if want == "hostport":
        return _fit([*head, *_HEADER_LOOP,
                     'host, _, port = headers["host"].partition(":")',
                     'print(host, port or "80")'])
    if want == "body":
        return _fit([*head, *_HEADER_LOOP, 'size = int(headers["content-length"])',
                     "print(size, body[:size])"])
    raise ValueError(want)


def _request_out(a: dict) -> str:
    want = a["want"]
    line = _ok(_URLCH_LINE, a["line"], "a request line")
    if want == "valid":
        good = re.fullmatch(r"[^ ]+ [^ ]+ HTTP/[^ ]*", line) is not None
        if a.get("headers"):
            _headers_in(a["headers"])
        return "ok" if good else "400 Bad Request"
    m = re.fullmatch(r"([A-Z]+) ([^ ]+) HTTP/([0-9.]+)", line)
    if not m:
        raise ValueError("METHOD target HTTP/x.y")
    method, target, number = m.groups()
    if method not in _METHODS:
        raise ValueError(method)
    pairs = _headers_in(a["headers"]) if a.get("headers") else []
    body = a.get("body")
    if want == "method":
        return method
    if want == "target":
        return target
    if want == "version":
        return number
    if want == "triple":
        return f"{method} {target} HTTP/{number}"
    if want == "path":
        path, _, query = target.partition("?")
        if "?" in query:
            raise ValueError("one question mark")
        return NL.join([path, query or "none"])
    if want == "count":
        if len(pairs) < 2:
            raise ValueError("two headers at least")
        return str(len(pairs))
    if want == "names":
        if len(pairs) < 2:
            raise ValueError("two headers at least")
        return ", ".join(k for k, _ in pairs)
    if want == "header":
        ask = _ok(_PLAIN, a["ask"])
        if ask != ask.lower():
            raise ValueError("ask in lower case")
        hits = [v for k, v in pairs if k.lower() == ask]
        if len(hits) != 1 or len(pairs) < 2:
            raise ValueError("one header with that name, among others")
        if any(v.count(":") for k, v in pairs if k.lower() != "host"):
            raise ValueError("no colons in a value, bar the host")
        return hits[0]
    if want == "hostport":
        hits = [v for k, v in pairs if k.lower() == "host"]
        if len(hits) != 1:
            raise ValueError("one Host header")
        host, _, port = hits[0].partition(":")
        if not re.fullmatch(r"[a-z.]+", host) or (port and not port.isdigit()):
            raise ValueError("a host and a port")
        return f"{host} {port or '80'}"
    if want == "body":
        if not body or len(pairs) < 2:
            raise ValueError("a body, and two headers")
        lengths = [v for k, v in pairs if k.lower() == "content-length"]
        if len(lengths) != 1 or int(lengths[0]) != len(body):
            raise ValueError("a Content-Length that matches the body")
        return f"{len(body)} {body}"
    raise ValueError(want)


# ── 5. Routing with a dict ───────────────────────────────────

_FUNC = re.compile(r"[a-z][a-z_]*")
_NOT_FOUND = "404 Not Found"


def _routes_in(routes, low: int = 2, high: int = 2) -> list[tuple[str, str, str]]:
    """(path, function name, text) rows."""
    routes = [tuple(r) for r in routes]
    if not low <= len(routes) <= high or any(len(r) != 3 for r in routes):
        raise ValueError(f"{low} to {high} routes of three")
    _unique([r[0] for r in routes], "paths")
    _unique([r[1] for r in routes], "names")
    for path, name, text in routes:
        _path(path)
        _ok(_FUNC, name, "a function name")
        _s(text)
        if text != text.strip() or text == _NOT_FOUND or not text.isascii():
            raise ValueError("plain text")
    return routes


def _paths_in(paths, low: int = 3, high: int = 4) -> list[str]:
    paths = list(paths)
    if not low <= len(paths) <= high:
        raise ValueError(f"{low} to {high} paths")
    for p in paths:
        _path(p)
    return paths


def _defs(routes) -> list[str]:
    lines = []
    for _, name, text in routes:
        lines += [f"def {name}():", f"    return {_s(text)}", ""]
    return lines


def _table(routes) -> str:
    return "{" + ", ".join(f"{_s(p)}: {n}" for p, n, _ in routes) + "}"


def _list_of(items) -> str:
    return "[" + ", ".join(_s(i) for i in items) + "]"


def _route(a: dict) -> str:
    want = a["want"]
    if want == "dispatch":
        routes, paths = _routes_in(a["routes"]), _paths_in(a["paths"])
        return _fit([*_defs(routes), f"ROUTES = {_table(routes)}", "",
                     "def dispatch(path):", "    handler = ROUTES.get(path)",
                     f'    return handler() if handler else "{_NOT_FOUND}"', "",
                     f"for path in {_list_of(paths)}:", "    print(dispatch(path))"],
                    _LIMITS["py_web_route"])
    if want in ("trailing", "names"):
        routes, paths = _routes_in(a["routes"]), _paths_in(a["paths"])
        lines = [*_defs(routes), f"ROUTES = {_table(routes)}", "",
                 f"for path in {_list_of(paths)}:"]
        if want == "trailing":
            lines += ['    clean = path.rstrip("/") or "/"', "    handler = ROUTES.get(clean)",
                      f'    print(handler() if handler else "{_NOT_FOUND}")']
        else:
            lines += ["    handler = ROUTES.get(path)",
                      '    print(handler.__name__ if handler else "none")']
        return _fit(lines, _LIMITS["py_web_route"])
    if want == "methods":
        routes = [tuple(r) for r in a["routes"]]
        if len(routes) != 2 or any(len(r) != 4 for r in routes):
            raise ValueError("two routes of four")
        shaped = _routes_in([(p, n, t) for _, p, n, t in routes])
        table = "{" + ", ".join(
            f"({_s(m)}, {_s(p)}): {n}" for (m, _, _, _), (p, n, _) in zip(routes, shaped)) + "}"
        requests = [tuple(r) for r in a["requests"]]
        if not 3 <= len(requests) <= 4:
            raise ValueError("three or four requests")
        shown = "[" + ", ".join(f"({_s(m)}, {_s(_path(p))})" for m, p in requests) + "]"
        return _fit([*_defs(shaped), f"ROUTES = {table}", "",
                     "def dispatch(method, path):", "    handler = ROUTES.get((method, path))",
                     "    if handler:", "        return handler()",
                     "    known = any(p == path for _, p in ROUTES)",
                     f'    return "405 Method Not Allowed" if known else "{_NOT_FOUND}"', "",
                     f"for request in {shown}:", "    print(dispatch(*request))"],
                    _LIMITS["py_web_route"])
    if want == "pattern":
        pattern, path = a["pattern"], a["path"]
        _ok(_PATTERN, pattern, "a pattern like /users/<id>")
        _ok(_PATH, path, "a plain URL path")
        return _fit([
            "def match(pattern, path):",
            '    want, got = pattern.split("/"), path.split("/")',
            "    if len(want) != len(got):", "        return None", "    found = {}",
            "    for piece, actual in zip(want, got):",
            '        if piece.startswith("<"):', '            found[piece.strip("<>")] = actual',
            "        elif piece != actual:", "            return None", "    return found", "",
            f"print(match({_q(pattern)}, {_s(path)}))"], _LIMITS["py_web_route"])
    if want == "decorator":
        routes, paths = _routes_in(a["routes"]), _paths_in(a["paths"])
        lines = ["ROUTES = {}", "", "def route(path):", "    def register(func):",
                 "        ROUTES[path] = func", "        return func", "    return register", ""]
        for path, name, text in routes:
            lines += [f"@route({_s(path)})", f"def {name}():", f"    return {_s(text)}", ""]
        lines += [f"for path in {_list_of(paths)}:",
                  f'    print(ROUTES[path]() if path in ROUTES else "{_NOT_FOUND}")']
        return _fit(lines, _LIMITS["py_web_route"])
    raise ValueError(want)


_PATTERN = re.compile(r"(/[a-z]+|/<[a-z]+>)+")


def _route_out(a: dict) -> str:
    want = a["want"]
    if want in ("dispatch", "trailing", "names"):
        routes, paths = _routes_in(a["routes"]), _paths_in(a["paths"])
        table = {p: (n, t) for p, n, t in routes}
        lines = []
        for path in paths:
            if want == "trailing":
                path = (path.rstrip("/") or "/")
            hit = table.get(path)
            if want == "names":
                lines.append(hit[0] if hit else "none")
            else:
                lines.append(hit[1] if hit else _NOT_FOUND)
        if _NOT_FOUND not in lines and "none" not in lines:
            raise ValueError("a path that is not routed")
        if len(set(lines)) < 2:
            raise ValueError("different answers")
        if want == "trailing" and not any(p != (p.rstrip("/") or "/") for p in paths):
            raise ValueError("a path with a trailing slash")
        return NL.join(lines)
    if want == "methods":
        routes = [tuple(r) for r in a["routes"]]
        shaped = _routes_in([(p, n, t) for _, p, n, t in routes])
        table = {(m, p): t for (m, _, _, _), (p, _, t) in zip(routes, shaped)}
        known = {p for _, p in table}
        lines = []
        for method, path in (tuple(r) for r in a["requests"]):
            _path(path)
            if (method, path) in table:
                lines.append(table[(method, path)])
            elif path in known:
                lines.append("405 Method Not Allowed")
            else:
                lines.append(_NOT_FOUND)
        if not {"405 Method Not Allowed", _NOT_FOUND} <= set(lines):
            raise ValueError("both a 405 and a 404")
        return NL.join(lines)
    if want == "pattern":
        pattern, path = _ok(_PATTERN, a["pattern"]), _ok(_PATH, a["path"])
        pieces = pattern.split("/")
        regex = "/".join(r"(?P<%s>[^/]+)" % p[1:-1] if p.startswith("<") else re.escape(p)
                         for p in pieces)
        m = re.fullmatch(regex, path)
        if len(pieces) != len(path.split("/")):
            return "None"
        if not m:
            return "None"
        return repr(m.groupdict())
    if want == "decorator":
        routes, paths = _routes_in(a["routes"]), _paths_in(a["paths"])
        table = {p: t for p, _, t in routes}
        lines = [table.get(p, _NOT_FOUND) for p in paths]
        if _NOT_FOUND not in lines or len(set(lines)) < 2:
            raise ValueError("a path that is routed and one that is not")
        return NL.join(lines)
    raise ValueError(want)


# ── Servers: the program every server page shares ────────────


def _imports(extra) -> list[str]:
    """Plain imports first, then the from-imports, each in order."""
    plain = {"threading", "urllib.request"}
    froms = {"from http.server import BaseHTTPRequestHandler, HTTPServer"}
    for m in extra:
        (froms if m.startswith("from ") else plain).add(m)
    return [f"import {m}" for m in sorted(plain)] + sorted(froms)


def _server_program(shape, extra, pre, handler, client) -> str:
    """Handler class, server in a daemon thread, a client, a clean shutdown."""
    lines = _imports(extra)
    lines += ["", *pre, "class Handler(BaseHTTPRequestHandler):"]
    lines += [f"    {h}" if h else h for h in handler]
    lines += [
        "", 'server = HTTPServer(("127.0.0.1", 0), Handler)',
        "threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()",
        'base = f"http://127.0.0.1:{server.server_port}"',
        *client, "server.shutdown()", "server.server_close()",
    ]
    return _fit(lines, _LIMITS[shape])


def _indent(lines, n: int = 1) -> list[str]:
    return [("    " * n + x) if x else x for x in lines]


def _reply(status, headers=(), body="") -> list[str]:
    lines = [f"self.send_response({status})"]
    lines += [f"self.send_header({_s(k)}, {_s(v)})" for k, v in headers]
    lines += ["self.end_headers()"]
    if body:
        lines.append(f"self.wfile.write({body})")
    return lines


def _tried(call: str, show: str) -> list[str]:
    """Ask for something that may answer with an error status."""
    return ["try:", f"    reply = {call}", "except urllib.error.HTTPError as err:",
            "    reply = err", show]


# ── 6. GET routes on http.server ─────────────────────────────

_ERRORS = (401, 403, 404, 409, 410, 500, 503)
_QUERY = re.compile(r"(\?[A-Za-z0-9_=&%+.\-]*)?")


def _get(a: dict) -> str:
    want = a["want"]
    shape = "py_web_get"
    if want == "route":
        pages = _pairs(a["pages"])
        pre = ["PAGES = {" + ", ".join(f"{_s(_path(p))}: {_s(t)}" for p, t in pages) + "}", ""]
        handler = ["def do_GET(self):", "    text = PAGES.get(self.path)",
                   "    self.send_response(200 if text else 404)", "    self.end_headers()",
                   '    self.wfile.write((text or "not found").encode())']
        paths = _list_of(_path(p) for p in a["paths"])
        client = [f"for path in {paths}:",
                  *_indent(_tried("urllib.request.urlopen(base + path)",
                                  "print(path, reply.status, reply.read().decode())"))]
        return _server_program(shape, ["urllib.error"], pre, handler, client)
    if want == "ctype":
        kind, charset = a["type"], a.get("charset")
        value = kind if charset is None else f"{kind}; charset={charset}"
        handler = ["def do_GET(self):", *_indent(_reply(200, [("Content-Type", value)], 'b"hello"'))]
        client = ['with urllib.request.urlopen(base + "/") as reply:',
                  "    print(reply.headers.get_content_type(), reply.headers.get_content_charset())"]
        return _server_program(shape, [], [], handler, client)
    if want == "error":
        status, text = _int(a["status"]), a["text"]
        handler = ["def do_GET(self):",
                   *_indent(_reply(status, [], "b" + _s(text)))]
        client = _tried('urllib.request.urlopen(base + "/")',
                        "print(reply.status, reply.reason, reply.read().decode())")
        return _server_program(shape, ["urllib.error"], [], handler, client)
    if want == "hits":
        paths = _list_of(_path(p) for p in a["paths"])
        handler = ["hits = {}", "", "def do_GET(self):",
                   "    Handler.hits[self.path] = Handler.hits.get(self.path, 0) + 1",
                   *_indent(_reply(200, [], "str(Handler.hits[self.path]).encode()"))]
        client = ["seen = []", f"for path in {paths}:",
                  "    with urllib.request.urlopen(base + path) as reply:",
                  "        seen.append(reply.read().decode())",
                  'print(", ".join(seen))']
        return _server_program(shape, [], [], handler, client)
    if want == "query":
        fallback = _s(a["fallback"])
        queries = "[" + ", ".join(_q(_ok(_QUERY, q)) for q in a["queries"]) + "]"
        handler = ["def do_GET(self):", "    query = parse_qs(urlparse(self.path).query)",
                   f'    name = query.get("name", [{fallback}])[0]',
                   *_indent(_reply(200, [], 'f"Hello, {name}!".encode()'))]
        client = [f"for query in {queries}:",
                  '    with urllib.request.urlopen(base + "/" + query) as reply:',
                  "        print(reply.read().decode())"]
        return _server_program(shape, ["from urllib.parse import parse_qs, urlparse"],
                               [], handler, client)
    if want == "tags":
        paths = "[" + ", ".join(_u(p) for p in a["paths"]) + "]"
        if a["show"] == "join":
            body = f'{_s(a["sep"])}.join(tags) or "none"'
        else:
            body = "str(len(tags))"
        handler = ["def do_GET(self):",
                   '    tags = parse_qs(urlparse(self.path).query).get("tag", [])',
                   *_indent(_reply(200, [], f"({body}).encode()"))]
        client = [f"for path in {paths}:",
                  "    with urllib.request.urlopen(base + path) as reply:",
                  "        print(reply.read().decode())"]
        return _server_program(shape, ["from urllib.parse import parse_qs, urlparse"],
                               [], handler, client)
    if want == "sum":
        paths = "[" + ", ".join(_u(p) for p in a["paths"]) + "]"
        handler = [
            "def do_GET(self):", "    query = parse_qs(urlparse(self.path).query)", "    try:",
            '        text, status = str(int(query["a"][0]) + int(query["b"][0])), 200',
            "    except (KeyError, ValueError):", '        text, status = "bad request", 400',
            "    self.send_response(status)", "    self.end_headers()",
            "    self.wfile.write(text.encode())",
        ]
        client = [f"for path in {paths}:",
                  *_indent(_tried("urllib.request.urlopen(base + path)",
                                  "print(reply.status, reply.read().decode())"))]
        return _server_program(shape, ["urllib.error", "from urllib.parse import parse_qs, urlparse"],
                               [], handler, client)
    if want == "redirect":
        chain = _pairs(a["chain"])
        table = "{" + ", ".join(f"{_s(_path(x))}: {_s(_path(y))}" for x, y in chain) + "}"
        code = _int(a["code"])
        handler = ["def do_GET(self):", "    target = REDIRECTS.get(self.path)",
                   f"    self.send_response({code} if target else 200)", "    if target:",
                   '        self.send_header("Location", target)', "    self.end_headers()",
                   '    self.wfile.write(b"" if target else self.path.encode())']
        client = [f'with urllib.request.urlopen(base + {_s(_path(a["start"]))}) as reply:',
                  "    print(reply.status, reply.read().decode())"]
        return _server_program(shape, [], [f"REDIRECTS = {table}", ""], handler, client)
    if want == "methods":
        path = _path(a["path"])
        requests = "[" + ", ".join(f"({_s(m)}, {_s(_path(p))})" for m, p in a["requests"]) + "]"
        handler = [
            "def do_GET(self):",
            f"    self.send_response(200 if self.path == {_s(path)} else 404)",
            "    self.end_headers()", "",
            "def do_POST(self):",
            f"    self.send_response(405 if self.path == {_s(path)} else 404)",
            f"    if self.path == {_s(path)}:",
            '        self.send_header("Allow", "GET")', "    self.end_headers()",
        ]
        client = [
            f"for method, path in {requests}:",
            "    request = urllib.request.Request(base + path, method=method)",
            *_indent(_tried("urllib.request.urlopen(request)",
                            'print(method, path, reply.status, reply.headers.get("Allow", "-"))')),
        ]
        return _server_program(shape, ["urllib.error"], [], handler, client)
    if want == "unsupported":
        method = a["method"]
        handler = ["def do_GET(self):", *_indent(_reply(200, [], 'b"ok"'))]
        client = [f'request = urllib.request.Request(base + "/", method={_s(method)})',
                  "try:", "    urllib.request.urlopen(request)",
                  "except urllib.error.HTTPError as err:", "    print(err.code, err.reason)"]
        return _server_program(shape, ["urllib.error"], [], handler, client)
    raise ValueError(want)


def _fetch_all(table: dict[str, str], paths) -> list[str]:
    return [f"{p} {200 if p in table else 404} {table.get(p, 'not found')}" for p in paths]


def _get_out(a: dict) -> str:
    want = a["want"]
    if want == "route":
        pages = _pairs(a["pages"])
        table = {_path(p): _s(t) and t for p, t in pages}
        if len(table) != len(pages) or not 2 <= len(pages) <= 3:
            raise ValueError("two or three pages")
        for t in table.values():
            if not t or t != t.strip() or not t.isascii():
                raise ValueError("plain text")
        paths = _unique(_path(p) for p in a["paths"])
        lines = _fetch_all(table, paths)
        if not 3 <= len(paths) <= 4 or not any(p in table for p in paths) \
                or all(p in table for p in paths):
            raise ValueError("three paths, some of them missing")
        return NL.join(lines)
    if want == "ctype":
        kind, charset = a["type"], a.get("charset")
        if kind not in ("text/html", "text/plain", "text/csv", "application/json"):
            raise ValueError(kind)
        if charset not in (None, "utf-8", "iso-8859-1"):
            raise ValueError(charset)
        return f"{kind} {charset}"
    if want == "error":
        status, text = _int(a["status"]), a["text"]
        if status not in _ERRORS:
            raise ValueError("an error status from the list")
        _s(text)
        if not text or text != text.strip() or not text.isascii():
            raise ValueError("plain text")
        return f"{status} {_REASONS[status]} {text}"
    if want == "hits":
        paths = [_path(p) for p in a["paths"]]
        if not 3 <= len(paths) <= 5 or len(set(paths)) == len(paths) or len(set(paths)) < 2:
            raise ValueError("three to five requests, some paths asked for twice")
        seen: dict[str, int] = {}
        out = []
        for p in paths:
            seen[p] = seen.get(p, 0) + 1
            out.append(str(seen[p]))
        return ", ".join(out)
    if want == "query":
        _s(a["fallback"])
        lines = []
        for q in a["queries"]:
            found = _qs(_ok(_QUERY, q).lstrip("?"))
            name = found.get("name", [a["fallback"]])[0]
            if not name or not name.isascii():
                raise ValueError("a plain name")
            lines.append(f"Hello, {name}!")
        if not 3 <= len(lines) <= 4 or len(set(lines)) < 3:
            raise ValueError("three different answers")
        return NL.join(lines)
    if want == "tags":
        lines = []
        for p in a["paths"]:
            base, _, q = _ok(_URLCH, p).partition("?")
            if base != "/":
                raise ValueError("the root path")
            tags = _qs(q).get("tag", [])
            if any(not re.fullmatch(r"[a-z]+", t) for t in tags):
                raise ValueError("plain tags")
            if a["show"] == "join":
                _s(a["sep"])
                lines.append(a["sep"].join(tags) or "none")
            elif a["show"] == "count":
                lines.append(str(len(tags)))
            else:
                raise ValueError(a["show"])
        if len(a["paths"]) != 2 or len(set(lines)) != 2:
            raise ValueError("two paths with different answers")
        return NL.join(lines)
    if want == "sum":
        lines = []
        for p in a["paths"]:
            base, _, q = _ok(_URLCH, p).partition("?")
            if base != "/add":
                raise ValueError("the /add path")
            found = _qs(q)
            a_, b_ = found.get("a", [""])[0], found.get("b", [""])[0]
            if all(re.fullmatch(r"-?[0-9]+", v) for v in (a_, b_)):
                lines.append(f"200 {int(a_) + int(b_)}")
            else:
                lines.append("400 bad request")
        if len(lines) != 3 or not any(x.startswith("200") for x in lines) \
                or not any(x.startswith("400") for x in lines):
            raise ValueError("three requests, some good and some not")
        return NL.join(lines)
    if want == "redirect":
        chain = dict(_pairs(a["chain"]))
        code = _int(a["code"])
        if code not in (301, 302, 307, 308):
            raise ValueError("a redirect status")
        here = _path(a["start"])
        hops = 0
        while here in chain:
            here = _path(chain[here])
            hops += 1
            if hops > 5:
                raise ValueError("a chain that ends")
        if hops < 1 or len(chain) != len(a["chain"]):
            raise ValueError("at least one hop")
        return f"200 {here}"
    if want == "methods":
        path = _path(a["path"])
        lines = []
        for method, p in (tuple(r) for r in a["requests"]):
            _path(p)
            if method == "GET":
                lines.append(f"GET {p} {200 if p == path else 404} -")
            elif method == "POST":
                lines.append(f"POST {p} {405 if p == path else 404} {'GET' if p == path else '-'}")
            else:
                raise ValueError(method)
        statuses = {x.split(" ")[2] for x in lines}
        if statuses != {"200", "404", "405"} or not 3 <= len(lines) <= 4:
            raise ValueError("a 200, a 404 and a 405")
        return NL.join(lines)
    if want == "unsupported":
        method = a["method"]
        if method not in ("DELETE", "PUT", "PATCH"):
            raise ValueError(method)
        return f"501 Unsupported method ('{method}')"
    raise ValueError(want)


# ── 7. A JSON API ────────────────────────────────────────────

#: Bodies that are not JSON: bare words, unquoted keys, single quotes, a
#: missing bracket.
_JSONCH = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()<>'\"{}\[\]\-]+")
_BAD_JSON = ("oops", "{name: 1}", '{"name": "Ada"', "[1, 2", "{'name': 'Ada'}")
_NUMBER_OPS = {"sum": ("total", "sum(data[\"numbers\"])"),
               "max": ("biggest", "max(data[\"numbers\"])"),
               "min": ("smallest", "min(data[\"numbers\"])")}


def _post_handler(result: str, status: int = 200, headers=()) -> list[str]:
    return ["def do_POST(self):",
            "    data = json.loads(self.rfile.read(int(self.headers[\"Content-Length\"])))",
            f"    body = json.dumps({result}).encode()",
            *_indent(_reply(status, headers, "body"))]


def _post_client(payload: str, show: list[str]) -> list[str]:
    return [f"body = json.dumps({payload}).encode()",
            "request = urllib.request.Request(base, data=body)",
            "with urllib.request.urlopen(request) as reply:", *_indent(show)]


def _jtext(obj: dict) -> str:
    """A flat dict as json.dumps writes it."""
    items = []
    for k, v in obj.items():
        items.append(f'"{k}": ' + (f'"{v}"' if isinstance(v, str) else str(v)))
    return "{" + ", ".join(items) + "}"


def _jplain(obj) -> None:
    for k, v in obj.items():
        _word(k)
        if isinstance(v, str):
            _s(v)
            if not v.isascii() or v != v.strip():
                raise ValueError("plain text")
        elif isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("text or a whole number")


def _numbers(v) -> list[int]:
    if not isinstance(v, list) or not 3 <= len(v) <= 5:
        raise ValueError("three to five numbers")
    for x in v:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1:
            raise ValueError("positive whole numbers")
    return _unique(v, "numbers")


def _api(a: dict) -> str:
    want = a["want"]
    shape = "py_web_api"
    json_header = [("Content-Type", "application/json")]
    if want == "total":
        key, expr = _NUMBER_OPS[a["op"]]
        payload = '{"numbers": ' + _pyval(_numbers(a["numbers"])) + "}"
        handler = _post_handler("{" + f'"{key}": {expr}' + "}", 200, json_header)
        client = _post_client(payload, [f'print(json.load(reply)["{key}"])'])
        return _server_program(shape, ["json"], [], handler, client)
    if want == "greet":
        name = _ok(_NAME, a["name"], "a name")
        handler = _post_handler('{"message": f"Hello, {data[\'name\']}!"}', 200, json_header)
        client = _post_client('{"name": ' + _s(name) + "}", ["print(json.load(reply))"])
        return _server_program(shape, ["json"], [], handler, client)
    if want == "word":
        word = _word(a["word"])
        how = {"upper": 'data["word"].upper()', "reverse": 'data["word"][::-1]'}[a["how"]]
        handler = _post_handler('{"word": ' + how + "}", 200, json_header)
        client = _post_client('{"word": ' + _s(word) + "}", ["print(json.load(reply))"])
        return _server_program(shape, ["json"], [], handler, client)
    if want == "stats":
        handler = _post_handler(
            '{"min": min(data["numbers"]), "max": max(data["numbers"]), '
            '"count": len(data["numbers"])}', 200, json_header)
        client = _post_client('{"numbers": ' + _pyval(_numbers(a["numbers"])) + "}",
                              ["print(json.load(reply))"])
        return _server_program(shape, ["json"], [], handler, client)
    if want == "length":
        name = _ok(_NAME, a["name"], "a name")
        handler = [
            "def do_POST(self):",
            '    data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))',
            '    body = json.dumps({"message": f"Hello, {data[\'name\']}!"}).encode()',
            "    self.send_response(200)", '    self.send_header("Content-Type", "application/json")',
            '    self.send_header("Content-Length", str(len(body)))', "    self.end_headers()",
            "    self.wfile.write(body)",
        ]
        client = _post_client('{"name": ' + _s(name) + "}",
                              ['print(reply.headers["Content-Type"])',
                               'print(reply.headers["Content-Length"])'])
        return _server_program(shape, ["json"], [], handler, client)
    if want == "create":
        names = list(a["names"])
        seeded = _int(a.get("seeded", 0))
        items = "[" + ", ".join(['"seed"'] * seeded) + "]"
        handler = [
            f"items = {items}", "", "def do_POST(self):",
            '    data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))',
            '    Handler.items.append(data["name"])',
            '    body = json.dumps({"id": len(Handler.items)}).encode()',
            *_indent(_reply(201, [], "body")),
        ]
        client = [f"for name in {_list_of(names)}:",
                  '    body = json.dumps({"name": name}).encode()',
                  "    request = urllib.request.Request(base, data=body)",
                  "    with urllib.request.urlopen(request) as reply:",
                  '        print(reply.status, json.load(reply)["id"])']
        return _server_program(shape, ["json"], [], handler, client)
    if want == "invalid":
        kind = a["kind"]
        if kind == "bad":
            sent = "b" + _lit(a["text"], _JSONCH)
            prep = []
        else:
            sent = "body"
            prep = ["body = json.dumps({" + f'{_s(a["key"])}: {_s(a["value"])}' + "}).encode()"]
        handler = [
            "def do_POST(self):", "    try:",
            '        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))',
            '        status, result = 200, {"hello": data["name"]}',
            "    except (ValueError, KeyError):",
            '        status, result = 400, {"error": "bad request"}',
            "    self.send_response(status)", "    self.end_headers()",
            "    self.wfile.write(json.dumps(result).encode())",
        ]
        client = [*prep, f"request = urllib.request.Request(base, data={sent})",
                  *_tried("urllib.request.urlopen(request)",
                          "print(reply.status, json.load(reply))")]
        return _server_program(shape, ["json", "urllib.error"], [], handler, client)
    raise ValueError(want)


def _api_out(a: dict) -> str:
    want = a["want"]
    if want == "total":
        nums = _numbers(a["numbers"])
        op = a["op"]
        if op not in _NUMBER_OPS:
            raise ValueError(op)
        if op == "sum":
            total = 0
            for n in nums:
                total += n
            return str(total)
        return str(max(nums) if op == "max" else min(nums))
    if want == "greet":
        return repr({"message": f"Hello, {_ok(_NAME, a['name'], 'a name')}!"})
    if want == "word":
        word = _word(a["word"])
        if a["how"] == "upper":
            shown = word.upper()
        elif a["how"] == "reverse":
            shown = "".join(reversed(word))
            if shown == word:
                raise ValueError("a word that is not a palindrome")
        else:
            raise ValueError(a["how"])
        return repr({"word": shown})
    if want == "stats":
        nums = _numbers(a["numbers"])
        return repr({"min": min(nums), "max": max(nums), "count": len(nums)})
    if want == "length":
        text = _jtext({"message": f"Hello, {_ok(_NAME, a['name'], 'a name')}!"})
        return NL.join(["application/json", str(len(text))])
    if want == "create":
        names = list(a["names"])
        seeded = _int(a.get("seeded", 0))
        if not 2 <= len(names) <= 4 or not 0 <= seeded <= 2:
            raise ValueError("two to four posts, up to two already stored")
        for n in names:
            _word(n)
        return NL.join(f"201 {seeded + i}" for i in range(1, len(names) + 1))
    if want == "invalid":
        kind = a["kind"]
        if kind == "bad":
            if a["text"] not in _BAD_JSON:
                raise ValueError("text that is not JSON")
            return "400 " + repr({"error": "bad request"})
        key, value = _word(a["key"]), _s(a["value"]) and a["value"]
        if not value.isascii() or value != value.strip():
            raise ValueError("plain text")
        if kind == "missing":
            if key == "name":
                raise ValueError("a key that is not name")
            return "400 " + repr({"error": "bad request"})
        if kind == "good":
            if key != "name":
                raise ValueError("the name key")
            return "200 " + repr({"hello": value})
        raise ValueError(kind)
    raise ValueError(want)


# ── 8. Cookies ───────────────────────────────────────────────

_COOKIE_VALUE = re.compile(r"[A-Za-z0-9_\-]+")
_ATTR_TEXT = {"domain": "Domain", "httponly": "HttpOnly", "max-age": "Max-Age",
              "path": "Path", "samesite": "SameSite", "secure": "Secure"}
_ATTR_FLAGS = ("httponly", "secure")
_COOKIE_IMPORT = ["from http.cookies import SimpleCookie", ""]


def _cookie_name(x) -> str:
    return _ok(re.compile(r"[a-z][a-z_]*"), x, "a lower-case cookie name")


def _cookie_value(x) -> str:
    if isinstance(x, int) and not isinstance(x, bool):
        return str(x)
    return _ok(_COOKIE_VALUE, x, "a plain cookie value")


def _cookie_header(pairs) -> str:
    pairs = _pairs(pairs)
    names = [_cookie_name(k) for k, _ in pairs]
    _unique(names, "cookie names")
    return "; ".join(f"{k}={_cookie_value(v)}" for k, v in pairs)


def _attr_lines(name: str, attrs) -> list[str]:
    lines = []
    for key, value in attrs:
        if key not in _ATTR_TEXT:
            raise ValueError(key)
        if key in _ATTR_FLAGS:
            if value is not True:
                raise ValueError("a flag is set to True")
            shown = "True"
        elif key == "max-age":
            shown = str(_int(value))
        else:
            shown = _s(value)
        lines.append(f'cookie[{_s(name)}][{_s(key)}] = {shown}')
    return lines


def _cookie_literal(v) -> str:
    return str(v) if isinstance(v, int) and not isinstance(v, bool) else _s(v)


def _cookies(a: dict) -> str:
    want = a["want"]
    if want in ("value", "keys", "has", "items"):
        header = _cookie_header(a["pairs"])
        lines = [*_COOKIE_IMPORT, f"cookie = SimpleCookie({_s(header)})"]
        if want == "value":
            return _fit([*lines, f"print(cookie[{_s(a['ask'])}].value)"])
        if want == "keys":
            return _fit([*lines, "print(list(cookie))"])
        if want == "has":
            return _fit([*lines, f"print({_s(a['ask'])} in cookie)"])
        return _fit([*lines, "for name, morsel in cookie.items():",
                     "    print(name, morsel.value)"])
    if want == "output":
        name, value = _cookie_name(a["name"]), a["value"]
        _cookie_value(value)
        return _fit([*_COOKIE_IMPORT, "cookie = SimpleCookie()",
                     f"cookie[{_s(name)}] = {_cookie_literal(value)}", "print(cookie.output())"])
    if want == "attrs":
        name, value = _cookie_name(a["name"]), a["value"]
        _cookie_value(value)
        return _fit([*_COOKIE_IMPORT, "cookie = SimpleCookie()",
                     f"cookie[{_s(name)}] = {_cookie_literal(value)}",
                     *_attr_lines(name, a["attrs"]), "print(cookie.output())"])
    if want == "many":
        pairs = _pairs(a["pairs"])
        _cookie_header(pairs)
        literal = "{" + ", ".join(f"{_s(k)}: {_cookie_literal(v)}" for k, v in pairs) + "}"
        return _fit([*_COOKIE_IMPORT, f"pairs = {literal}", "cookie = SimpleCookie()",
                     "for name, value in pairs.items():", "    cookie[name] = value",
                     'print(cookie.output(sep="\\n"))'])
    if want == "parseattr":
        header = _ok(_PLAIN, a["header"], "a Set-Cookie value")
        return _fit([*_COOKIE_IMPORT, f"cookie = SimpleCookie({_s(header)})",
                     f"print(cookie[{_s(a['name'])}][{_s(a['attr'])}])"])
    raise ValueError(want)


def _morsel_text(name: str, value: str, attrs) -> str:
    chosen = dict(attrs)
    if len(chosen) != len(list(attrs)):
        raise ValueError("each attribute once")
    parts = [f"{name}={value}"]
    for key in sorted(chosen):
        if key in _ATTR_FLAGS:
            parts.append(_ATTR_TEXT[key])
        else:
            parts.append(f"{_ATTR_TEXT[key]}={chosen[key]}")
    return "; ".join(parts)


def _cookies_out(a: dict) -> str:
    want = a["want"]
    if want in ("value", "keys", "has", "items"):
        pairs = _pairs(a["pairs"])
        _cookie_header(pairs)
        table = {k: str(v) for k, v in pairs}
        if len(pairs) < 2:
            raise ValueError("two cookies at least")
        if want == "keys":
            return repr(list(table))
        if want == "items":
            return NL.join(f"{k} {v}" for k, v in table.items())
        ask = _cookie_name(a["ask"])
        if want == "has":
            return str(ask in table)
        if ask not in table:
            raise ValueError("a cookie that is there")
        return table[ask]
    if want in ("output", "attrs"):
        name, value = _cookie_name(a["name"]), _cookie_value(a["value"])
        attrs = list(a["attrs"]) if want == "attrs" else []
        for key, v in attrs:
            if key not in _ATTR_TEXT:
                raise ValueError(key)
            if key in _ATTR_FLAGS and v is not True:
                raise ValueError("a flag is True")
            if key == "max-age" and (not isinstance(v, int) or v <= 0):
                raise ValueError("a positive Max-Age")
            if key in ("path", "domain", "samesite"):
                _s(v)
        if want == "attrs":
            order = [k for k, _ in attrs]
            if not 2 <= len(order) <= 3 or order == sorted(order):
                raise ValueError("attributes set out of alphabetical order")
        text = _morsel_text(name, value, [(k, str(v)) for k, v in attrs])
        return "Set-Cookie: " + text
    if want == "many":
        pairs = _pairs(a["pairs"])
        _cookie_header(pairs)
        if not 2 <= len(pairs) <= 3:
            raise ValueError("two or three cookies")
        names = [k for k, _ in pairs]
        if names == sorted(names):
            raise ValueError("names out of alphabetical order: output() sorts them")
        # output() writes the cookies sorted by name, not as they were added.
        return NL.join(f"Set-Cookie: {k}={_cookie_value(v)}" for k, v in sorted(pairs))
    if want == "parseattr":
        header = _ok(_PLAIN, a["header"])
        pieces = [p.strip() for p in header.split(";")]
        name = _cookie_name(a["name"])
        first, _, value = pieces[0].partition("=")
        if first != name:
            raise ValueError("the cookie comes first")
        attrs: dict[str, object] = {}
        for piece in pieces[1:]:
            key, eq, val = piece.partition("=")
            low = key.lower()
            if low not in _ATTR_TEXT:
                raise ValueError("a known attribute")
            attrs[low] = val if eq else True
        attr = a["attr"]
        if attr not in attrs:
            raise ValueError("an attribute that is set")
        return str(attrs[attr])
    raise ValueError(want)


# ── 9. WSGI ──────────────────────────────────────────────────

_SHOW = ["def show(status, headers):", "    print(status, headers)", ""]
_TEXT_HEADER = '[("Content-Type", "text/plain")]'
_STATUS_TEXT = {200: "200 OK", 404: "404 Not Found", 405: "405 Method Not Allowed"}
_TRANSFORMS = {
    "upper": ("shout", "chunk.upper()", lambda t: t.upper()),
    "lower": ("whisper", "chunk.lower()", lambda t: t.lower()),
    "reverse": ("flip", "chunk[::-1]", lambda t: "".join(reversed(t))),
    "prefix": ("quote", 'b"> " + chunk', lambda t: "> " + t),
}
_WS_BODY = re.compile(r"[A-Za-z0-9 _.,:;/=@+!?#()<>'\"{}\[\]\-]+")
_WSQ = re.compile(r"[A-Za-z0-9_=&%+.\-]*")
_NAME = re.compile(r"[A-Za-z]+")


def _bytes_lit(x) -> str:
    _ok(_WS_BODY, x, "plain text")
    return "b" + _lit(x, _WS_BODY)


def _header_list(pairs) -> str:
    return "[" + ", ".join(f"({_s(k)}, {_s(v)})" for k, v in _pairs(pairs)) + "]"


def _wsgi(a: dict) -> str:
    want = a["want"]
    run = "print(b\"\".join(app({environ}, show)).decode())"
    if want == "hello":
        headers = [("Content-Type", a["type"])]
        return _fit(["def app(environ, start_response):",
                     f'    start_response("200 OK", {_header_list(headers)})',
                     f"    return [{_bytes_lit(a['body'])}]", "", *_SHOW,
                     run.format(environ="{}")], _LIMITS["py_web_wsgi"])
    if want == "path":
        pages = _pairs(a["pages"])
        table = "{" + ", ".join(f"{_s(_path(p))}: {_s(t)}" for p, t in pages) + "}"
        return _fit([
            f"PAGES = {table}", "", "def app(environ, start_response):",
            '    text = PAGES.get(environ["PATH_INFO"])',
            f'    start_response("200 OK" if text else "404 Not Found", {_TEXT_HEADER})',
            '    return [(text or "not found").encode()]', "", *_SHOW,
            run.format(environ='{"PATH_INFO": ' + _s(_path(a["path"])) + "}")],
            _LIMITS["py_web_wsgi"])
    if want == "method":
        allowed = a["allowed"]
        return _fit([
            "def app(environ, start_response):",
            f'    if environ["REQUEST_METHOD"] != {_s(allowed)}:',
            f'        start_response("405 Method Not Allowed", [("Allow", {_s(allowed)})])',
            '        return [b"method not allowed"]',
            f'    start_response("200 OK", {_TEXT_HEADER})',
            f'    return [{_bytes_lit(a["body"])}]', "", *_SHOW,
            run.format(environ='{"REQUEST_METHOD": ' + _s(a["method"]) + "}")],
            _LIMITS["py_web_wsgi"])
    if want == "query":
        fallback = _s(a["fallback"])
        return _fit([
            "from urllib.parse import parse_qs", "", "def app(environ, start_response):",
            '    query = parse_qs(environ["QUERY_STRING"])',
            f'    name = query.get("name", [{fallback}])[0]',
            f'    start_response("200 OK", {_TEXT_HEADER})',
            '    return [f"Hello, {name}!".encode()]', "", *_SHOW,
            run.format(environ='{"QUERY_STRING": ' + _q(_ok(_WSQ, a["query"])) + "}")],
            _LIMITS["py_web_wsgi"])
    if want == "accept":
        env = "{}" if a.get("accept") is None else '{"HTTP_ACCEPT": ' + _s(a["accept"]) + "}"
        return _fit([
            "def app(environ, start_response):",
            '    if "json" in environ.get("HTTP_ACCEPT", ""):',
            '        start_response("200 OK", [("Content-Type", "application/json")])',
            "        return [b'{\"hello\": \"world\"}']",
            f'    start_response("200 OK", {_TEXT_HEADER})', '    return [b"hello world"]',
            "", *_SHOW, run.format(environ=env)], _LIMITS["py_web_wsgi"])
    if want == "post":
        reply = {"upper": "data.upper()", "words": "str(len(data.split()))",
                 "reverse": "data[::-1]", "echo": 'f"you sent {data}"'}[a["reply"]]
        text = _ok(_WS_BODY, a["data"])
        return _fit([
            "import io", "", "def app(environ, start_response):",
            '    size = int(environ["CONTENT_LENGTH"])',
            '    data = environ["wsgi.input"].read(size).decode()',
            f'    start_response("200 OK", {_TEXT_HEADER})',
            f"    return [{reply}.encode()]", "", *_SHOW,
            f'environ = {{"CONTENT_LENGTH": "{len(text)}", "wsgi.input": io.BytesIO(b{_lit(text)})}}',
            run.format(environ="environ")], _LIMITS["py_web_wsgi"])
    if want == "middleware":
        name, expr, _ = _TRANSFORMS[a["how"]]
        return _fit([
            "def app(environ, start_response):",
            f'    start_response("200 OK", {_TEXT_HEADER})',
            f"    return [{_bytes_lit(a['body'])}]", "", f"def {name}(inner):",
            "    def wrapper(environ, start_response):",
            f"        return [{expr} for chunk in inner(environ, start_response)]",
            "    return wrapper", "", *_SHOW[:-1], "",
            run.replace("app(", f"{name}(app)(").format(environ="{}")],
            _LIMITS["py_web_wsgi"])
    raise ValueError(want)


def _wsgi_out(a: dict) -> str:
    want = a["want"]
    headers = [("Content-Type", "text/plain")]
    if want == "hello":
        headers = [("Content-Type", a["type"])]
        if a["type"] not in ("text/plain", "text/html", "application/json"):
            raise ValueError(a["type"])
        status, body = "200 OK", a["body"]
    elif want == "path":
        pages = _pairs(a["pages"])
        table = {_path(p): _ok(_PLAIN, t) for p, t in pages}
        if len(table) != 2:
            raise ValueError("two pages")
        text = table.get(_path(a["path"]))
        status, body = ("200 OK", text) if text else ("404 Not Found", "not found")
    elif want == "method":
        allowed, method = a["allowed"], a["method"]
        if allowed not in ("GET", "POST") or method not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("GET or POST")
        if method == allowed:
            status, body = "200 OK", _ok(_PLAIN, a["body"])
        else:
            status, body = "405 Method Not Allowed", "method not allowed"
            headers = [("Allow", allowed)]
    elif want == "query":
        found = _qs(_ok(_WSQ, a["query"]))
        name = found.get("name", [_ok(_PLAIN, a["fallback"])])[0]
        if not name or not name.isascii():
            raise ValueError("a plain name")
        status, body = "200 OK", f"Hello, {name}!"
    elif want == "accept":
        accept = a.get("accept")
        if accept is not None:
            _ok(_PLAIN, accept)
        if accept is not None and "json" in accept:
            headers, body = [("Content-Type", "application/json")], '{"hello": "world"}'
        else:
            body = "hello world"
        status = "200 OK"
    elif want == "post":
        data = _ok(_WS_BODY, a["data"])
        if "'" in data or '"' in data or data != data.strip() or "  " in data:
            raise ValueError("plain text, single spaces")
        status = "200 OK"
        body = {"upper": data.upper(), "words": str(len(data.split(" "))),
                "reverse": "".join(reversed(data)), "echo": f"you sent {data}"}[a["reply"]]
    elif want == "middleware":
        _, _, change = _TRANSFORMS[a["how"]]
        text = _ok(_WS_BODY, a["body"])
        status, body = "200 OK", change(text)
        if body == text:
            raise ValueError("a body the change shows on")
    else:
        raise ValueError(want)
    if not body.strip():
        raise ValueError("a body")
    return NL.join([f"{status} {headers!r}", body])


# ── 10. Templates ────────────────────────────────────────────

_PLACEHOLDER = re.compile(
    r"\$(?:(?P<esc>\$)|(?P<name>[_a-zA-Z][_a-zA-Z0-9]*)|\{(?P<brace>[_a-zA-Z][_a-zA-Z0-9]*)\}|(?P<bad>))")
_TPL = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()<>'\"$\{\}\-]+")


def _tpl(x: str) -> str:
    """A template as a literal. $ and braces are plain text to Python."""
    return _lit(x, _TPL)


def _expand(template: str, values: dict, safe: bool) -> str:
    """string.Template by hand."""
    def one(m):
        if m.group("esc"):
            return "$"
        if m.group("bad") is not None:
            raise ValueError("a lone dollar sign")
        key = m.group("name") or m.group("brace")
        if key in values:
            return str(values[key])
        if safe:
            return m.group(0)
        raise KeyError(key)
    return _PLACEHOLDER.sub(one, template)


def _kwargs(values: dict) -> str:
    out = []
    for k, v in values.items():
        _ok(re.compile(r"[a-z][a-z_]*"), k, "a name")
        out.append(f"{k}={_pyval(v)}")
    return ", ".join(out)


def _names_in(template: str) -> list[str]:
    return [m.group("name") or m.group("brace") for m in _PLACEHOLDER.finditer(template)
            if m.group("name") or m.group("brace")]


_SPEC = re.compile(r"\{([A-Za-z0-9_]*)(?::([^{}]*))?\}")


def _spec(value, spec: str | None) -> str:
    if spec is None:
        return str(value)
    if spec == ".2f":
        if not isinstance(value, float) or (value * 4) != int(value * 4) or value < 0:
            raise ValueError("a price in quarters")
        cents = int(value * 4) * 25
        return f"{cents // 100}.{cents % 100:02d}"
    m = re.fullmatch(r">([0-9]+)", spec)
    if m and isinstance(value, str):
        return value.rjust(int(m.group(1)))
    raise ValueError(f"{spec!r}: .2f or >N")


def _format(template: str, args, kwargs: dict) -> str:
    auto = 0

    def one(m):
        nonlocal auto
        field, spec = m.group(1), m.group(2)
        if field == "":
            value = args[auto]
            auto += 1
        elif field.isdigit():
            value = args[int(field)]
        else:
            value = kwargs[field]
        return _spec(value, spec)

    if _SPEC.sub("", template).count("{") or _SPEC.sub("", template).count("}"):
        raise ValueError("braces that are not fields")
    return _SPEC.sub(one, template)


def _escape(text: str) -> str:
    for old, new in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"),
                     ('"', "&quot;"), ("'", "&#x27;")):
        text = text.replace(old, new)
    return text


def _items(items, low: int = 2, high: int = 4) -> list[str]:
    items = list(items)
    if not low <= len(items) <= high:
        raise ValueError(f"{low} to {high} items")
    for i in items:
        _ok(_HTMLCH, i, "plain text")
    return items


_FROM_TEMPLATE = ["from string import Template", ""]


def _template(a: dict) -> str:
    want = a["want"]
    if want in ("template", "braces", "dollar"):
        text = _tpl(a["text"])
        return _fit([*_FROM_TEMPLATE, f"page = Template({text})",
                     f"print(page.substitute({_kwargs(a['values'])}))"], _LIMITS["py_web_template"])
    if want == "safe":
        return _fit([*_FROM_TEMPLATE, f"page = Template({_tpl(a['text'])})",
                     f"print(page.safe_substitute({_kwargs(a['values'])}))"],
                    _LIMITS["py_web_template"])
    if want == "keyerror":
        return _fit([*_FROM_TEMPLATE, f"page = Template({_tpl(a['text'])})", "try:",
                     f"    print(page.substitute({_kwargs(a['values'])}))",
                     "except KeyError as err:", '    print("missing", err.args[0])'],
                    _LIMITS["py_web_template"])
    if want == "format":
        args = ", ".join(_pyval(v) for v in a.get("args", []))
        kwargs = _kwargs(a.get("kwargs", {}))
        call = ", ".join(x for x in (args, kwargs) if x)
        return _fit(["template = " + _tpl(a["text"]), f"text = template.format({call})",
                     "print(text)"], _LIMITS["py_web_template"])
    if want == "list":
        items = _list_of(_items(a["items"]))
        kind = a["kind"]
        if kind == "ul":
            return _fit([f"items = {items}",
                         'rows = "\\n".join(f"<li>{item}</li>" for item in items)',
                         'print("<ul>\\n" + rows + "\\n</ul>")'], _LIMITS["py_web_template"])
        if kind == "ol":
            return _fit([f"items = {items}",
                         'rows = "\\n".join(f"<li>{item}</li>" for item in items)',
                         'print("<ol>\\n" + rows + "\\n</ol>")'], _LIMITS["py_web_template"])
        return _fit([f"items = {items}",
                     'rows = [f"<li>{i}. {item}</li>" for i, item in enumerate(items, start=1)]',
                     'print("\\n".join(rows))'], _LIMITS["py_web_template"])
    if want == "escape":
        items = "[" + ", ".join(_lit(i) for i in _items(a["items"], 2, 3)) + "]"
        return _fit(["import html", "", f"items = {items}",
                     'print("\\n".join(f"<li>{html.escape(item)}</li>" for item in items))'],
                    _LIMITS["py_web_template"])
    if want == "table":
        rows = "[" + ", ".join(f"({_s(n)}, {_pyval(p)})" for n, p in _pairs(a["rows"])) + "]"
        return _fit([f"rows = {rows}", 'print("<table>")', "for name, price in rows:",
                     '    print("<tr><td>{}</td><td>{:.2f}</td></tr>".format(name, price))',
                     'print("</table>")'], _LIMITS["py_web_template"])
    if want == "page":
        items = _list_of(_items(a["items"], 2, 3))
        title = _s(a["title"])
        return _fit([*_FROM_TEMPLATE, f"items = {items}",
                     'rows = "\\n".join(f"  <li>{item}</li>" for item in items)',
                     'page = Template("<h1>$title</h1>\\n<ul>\\n$rows\\n</ul>")',
                     f"print(page.substitute(title={title}, rows=rows))"],
                    _LIMITS["py_web_template"])
    raise ValueError(want)


def _values(values: dict) -> dict:
    if not values:
        raise ValueError("something to fill in")
    for k, v in values.items():
        _ok(re.compile(r"[a-z][a-z_]*"), k, "a name")
        if isinstance(v, str):
            _ok(_HTMLCH, v)
            if "$" in v:
                raise ValueError("no dollar signs in a value")
        elif isinstance(v, bool) or not isinstance(v, int):
            raise ValueError("text or a whole number")
    return values


def _template_out(a: dict) -> str:
    want = a["want"]
    if want in ("template", "braces", "dollar", "safe", "keyerror"):
        text, values = _ok(_TPL, a["text"]), _values(a["values"])
        if want == "dollar" and "$$" not in text:
            raise ValueError("a $$")
        if want == "braces" and "${" not in text:
            raise ValueError("a ${name}")
        if want in ("template", "braces", "dollar") and set(_names_in(text)) != set(values):
            raise ValueError("every placeholder filled, none to spare")
        if want == "safe":
            missing = [n for n in _names_in(text) if n not in values]
            if not missing:
                raise ValueError("a placeholder left unfilled")
            return _expand(text, values, True)
        if want == "keyerror":
            gone = [n for n in _names_in(text) if n not in values]
            if gone:
                return f"missing {gone[0]}"
        return _expand(text, values, False)
    if want == "format":
        args, kwargs = list(a.get("args", [])), dict(a.get("kwargs", {}))
        for v in [*args, *kwargs.values()]:
            if isinstance(v, str):
                _ok(_HTMLCH, v)
        return _format(_ok(_TPL, a["text"]), args, kwargs)
    if want == "list":
        items = _items(a["items"])
        for i in items:
            if "{" in i:
                raise ValueError("no braces")
        if a["kind"] == "ul":
            return NL.join(["<ul>", *(f"<li>{i}</li>" for i in items), "</ul>"])
        if a["kind"] == "ol":
            return NL.join(["<ol>", *(f"<li>{i}</li>" for i in items), "</ol>"])
        if a["kind"] == "numbered":
            return NL.join(f"<li>{n}. {i}</li>" for n, i in enumerate(items, start=1))
        raise ValueError(a["kind"])
    if want == "escape":
        items = _items(a["items"], 2, 3)
        if not any(_escape(i) != i for i in items):
            raise ValueError("an item that needs escaping")
        return NL.join(f"<li>{_escape(i)}</li>" for i in items)
    if want == "table":
        rows = _pairs(a["rows"])
        if not 2 <= len(rows) <= 3:
            raise ValueError("two or three rows")
        out = ["<table>"]
        for name, price in rows:
            _s(name)
            out.append(f"<tr><td>{name}</td><td>{_spec(price, '.2f')}</td></tr>")
        return NL.join([*out, "</table>"])
    if want == "page":
        items = _items(a["items"], 2, 3)
        title = _ok(_PLAIN, a["title"])
        rows = NL.join(f"  <li>{i}</li>" for i in items)
        return NL.join([f"<h1>{title}</h1>", "<ul>", rows, "</ul>"])
    raise ValueError(want)


_BUILDERS = {
    "py_web_url": _url,
    "py_web_status": _status,
    "py_web_headers": _headers,
    "py_web_request": _request,
    "py_web_route": _route,
    "py_web_get": _get,
    "py_web_api": _api,
    "py_web_cookies": _cookies,
    "py_web_wsgi": _wsgi,
    "py_web_template": _template,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "py_web_url": _url_out,
    "py_web_status": _status_out,
    "py_web_headers": _headers_out,
    "py_web_request": _request_out,
    "py_web_route": _route_out,
    "py_web_get": _get_out,
    "py_web_api": _api_out,
    "py_web_cookies": _cookies_out,
    "py_web_wsgi": _wsgi_out,
    "py_web_template": _template_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "py_web_url": Cost(
        "O(n)",
        "Linear in the length of the URL: urlsplit looks for the colon, the "
        "slashes, the question mark and the hash once, parse_qs walks the "
        "query a pair at a time, and quote and urlencode look at each "
        "character once, turning the unsafe ones into three-character %XX "
        "escapes. A URL is a few dozen characters, so none of it is the "
        "slow part of a request."),
    "py_web_status": Cost(
        "O(n)",
        "Linear in the number of codes you classify: each one is a division "
        "or a comparison, and HTTPStatus(code) is a dictionary lookup. The "
        "number of status codes is fixed and small, so looking one up never "
        "costs more however many requests have been served."),
    "py_web_headers": Cost(
        "O(n)",
        "Linear in the size of the response: one pass over the headers to "
        "write them, one over the body to count its bytes. Content-Length is "
        "the length of the encoded body, not the number of characters, which "
        "is why an accent or a character from another script costs extra."),
    "py_web_request": Cost(
        "O(n)",
        "Linear in the length of the request: partition and split each scan "
        "the text once to find a separator, and reading the headers into a "
        "dictionary is one step per header line. Real servers read from a "
        "socket a bit at a time, but a request is always parsed in one "
        "pass."),
    "py_web_route": Cost(
        "O(n)",
        "A dict of exact paths finds a handler in constant time, however "
        "many routes there are, so the cost is the number of requests, n. "
        "Matching a pattern like /users/<id> compares the path piece by "
        "piece, so it is linear in the number of pieces, and a router with "
        "many patterns tries them one after another."),
    "py_web_get": Cost(
        "O(n)",
        "Linear in the number of requests, n: the server does a fixed amount "
        "of work for each one, and the program waits for each answer in "
        "turn. The wait is network time, not computing. Port 0 lets the "
        "system pick a free port, and serve_forever(0.01) is what makes "
        "shutdown() return in ten milliseconds instead of waiting half a "
        "second."),
    "py_web_api": Cost(
        "O(n)",
        "Linear in the size of the body: reading Content-Length bytes, "
        "json.loads and json.dumps each visit every value once, and a sum or "
        "a maximum is one more pass over the list. HTTPServer handles one "
        "request at a time, so a slow client holds up the next; "
        "ThreadingHTTPServer starts a thread for each."),
    "py_web_cookies": Cost(
        "O(n)",
        "Linear in the length of the header: SimpleCookie splits it at the "
        "semicolons and reads each name=value once. Building one is a step "
        "per cookie, and output() sorts each cookie's attributes, a handful "
        "of items, which is why they come out in alphabetical order and not "
        "the order you set them."),
    "py_web_wsgi": Cost(
        "O(n)",
        "Linear in the size of what the app handles: it reads the request "
        "from the environ dictionary (a lookup) and returns the body as a "
        "list of bytes, which the server writes out chunk by chunk. A WSGI "
        "app is a plain function, which is the point: it needs no server to "
        "test, and middleware is a function that wraps another."),
    "py_web_template": Cost(
        "O(n)",
        "Linear in the size of the page: a Template is scanned once for its "
        "$ placeholders, format makes one pass over its braces, and "
        "''.join over a list builds the HTML in one go, where adding strings "
        "in a loop copies the text built so far each time. Escaping is one "
        "pass per value, and it is the step that keeps a stray < from "
        "becoming markup."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
