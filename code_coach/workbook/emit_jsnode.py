"""JavaScript: Node.js practice.

Ten pages of programs that run in plain node, outside the browser: the path
module, command-line arguments, reading and writing files, JSON on disk,
directories, events and timers and streams, environment variables and exit
codes, and a small HTTP server that the program then calls itself.

Everything is deterministic and runs as `node file.js` with no arguments:

- files live in a folder made with mkdtempSync under os.tmpdir(), and no
  program ever prints a path;
- process.argv and process.env cannot be passed in, so the programs are
  given an array or an object to stand in for them;
- the path pages use path.posix, so Windows and Linux print the same;
- servers listen on port 0 on 127.0.0.1, ask themselves with fetch, print
  what came back and close.

The oracle never runs the JavaScript. It works each answer out in Python
(posixpath, json, urllib.parse and plain logic), and the tests then hold node
to it. Rows that could print two ways are refused with ValueError.
"""

from __future__ import annotations

import json
import posixpath
import re
from urllib.parse import parse_qs, urlsplit

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines
from code_coach.workbook.emit_jsgame import _bool, _num

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_node_path", "the path module: join, resolve, basename, extname, dirname"),
    Shape("js_node_args", "reading flags and values out of an argv array"),
    Shape("js_node_read", "writing a temporary file and reading its lines back"),
    Shape("js_node_write", "writing, appending, overwriting, renaming and deleting files"),
    Shape("js_node_json", "saving and loading JSON, and catching a bad parse"),
    Shape("js_node_dirs", "making a folder, filling it and listing what is in it"),
    Shape("js_node_events", "EventEmitter, timers and a readable stream"),
    Shape("js_node_env", "environment defaults, thrown errors and the exit event"),
    Shape("js_node_http", "a tiny HTTP server that fetches from itself"),
    Shape("js_node_routes", "routes, query strings, 404s and request bodies"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Writing things the program types ─────────────────────────

#: Text that sits safely inside a single-quoted JavaScript string.
_TEXT = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()é日本\U0001F642-]+")
_NAME = re.compile(r"[a-z][a-z0-9]*(\.[a-z0-9]+)*")
_WORD = re.compile(r"[a-z]+")


def _s(x) -> str:
    """A string literal. Quotes, backslashes and the like are refused."""
    if not isinstance(x, str) or not _TEXT.fullmatch(x):
        raise ValueError(f"{x!r}: plain text only")
    return f"'{x}'"


def _arr(items) -> str:
    return "[" + ", ".join(_s(i) for i in items) + "]"


def _int(x) -> str:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: a whole number")
    return str(x)


def _name(x: str) -> str:
    """A file name: lowercase, with an optional extension."""
    if not isinstance(x, str) or not _NAME.fullmatch(x):
        raise ValueError(f"{x!r}: a plain lowercase file name")
    return x


def _ident(x: str) -> str:
    """A lowercase word used as a key or an event name."""
    if not isinstance(x, str) or not _WORD.fullmatch(x):
        raise ValueError(f"{x!r}: one lowercase word")
    return x


def _unique(items, what: str = "names") -> list:
    items = list(items)
    if len({str(i).lower() for i in items}) != len(items):
        raise ValueError(f"{what} must be unique, even ignoring case")
    return items


def _jsval(v) -> str:
    if isinstance(v, bool):
        return _bool(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return _s(v)
    if isinstance(v, list) and v:
        return "[" + ", ".join(_jsval(i) for i in v) + "]"
    raise ValueError(f"{v!r}: not a plain value")


def _obj(d: dict) -> str:
    """{ name: 'Ada', age: 36 }. Keys are plain lowercase words."""
    if not d:
        raise ValueError("an object with something in it")
    body = ", ".join(f"{_ident(k)}: {_jsval(v)}" for k, v in d.items())
    return "{ " + body + " }"


def _compact(value) -> str:
    """JSON.stringify's text, for values with no floats."""
    _plain(value)
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def _plain(value) -> None:
    """Refuse what JSON.stringify and json.dumps would print differently."""
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, int):
        if abs(value) >= 2**53:
            raise ValueError("too big for a double")
        return
    if isinstance(value, list):
        for v in value:
            _plain(v)
        return
    if isinstance(value, dict):
        for k, v in value.items():
            if not isinstance(k, str) or not k or k.isdigit():
                raise ValueError(f"{k!r}: whole-number keys are reordered by JS")
            _plain(v)
        return
    raise ValueError(f"{value!r}: no floats here")


# ── Programs that work in a temporary folder ─────────────────

_FS_HEAD = (
    "const fs = require('node:fs');",
    "const os = require('node:os');",
    "const path = require('node:path');",
    "const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cc-'));",
)
_CLEAN = "fs.rmSync(dir, { recursive: true });"


def _in_dir(*body: str, file: str | None = None) -> str:
    """The body in a fresh temporary folder, tidied away if it all fits."""
    lines = [*_FS_HEAD]
    if file is not None:
        lines.append(f"const file = path.join(dir, {_s(_name(file))});")
    lines.extend(body)
    if len(lines) < 10:
        lines.append(_CLEAN)
    return _lines(*lines)


def _literal_text(lines, eol: str = "\\n", end: bool = True) -> str:
    """The text of a file as a JS string: 'a\\nb\\n'."""
    lines = list(lines)
    if not lines:
        raise ValueError("a file with something in it")
    for line in lines:
        _s(line)
        if line != line.strip():
            raise ValueError(f"{line!r}: no spaces at the ends of a line")
    return "'" + eol.join(lines) + (eol if end else "") + "'"


# ── 1. The path module ───────────────────────────────────────

_PATH = "const path = require('node:path').posix;"
_ABS = re.compile(r"/[A-Za-z0-9_.\-]+(/[A-Za-z0-9_.\-]+)*")
_SEG = re.compile(r"[A-Za-z0-9_.\-]+")


def _abs(p: str) -> str:
    if not isinstance(p, str) or not _ABS.fullmatch(p):
        raise ValueError(f"{p!r}: an absolute path, no trailing slash")
    if any(seg in (".", "..") for seg in p.split("/")):
        raise ValueError(f"{p!r}: already tidy, no dots")
    return _s(p)


def _file_parts(p: str) -> tuple[str, str]:
    """A path's base name and extension, checked so both agree."""
    base = posixpath.basename(p)
    if not base or base.endswith("."):
        raise ValueError(f"{p!r}: a file path with a plain name")
    return base, posixpath.splitext(base)[1]


def _path(a: dict) -> str:
    want = a["want"]
    if want == "join":
        parts = a["parts"]
        return _lines(
            _PATH,
            f"const parts = {_arr(parts)};",
            "console.log(path.join(...parts));",
        )
    if want == "resolve":
        return _lines(
            _PATH,
            f"const base = {_abs(a['base'])};",
            f"const rest = {_arr(a['rest'])};",
            "console.log(path.resolve(base, ...rest));",
        )
    if want == "name":
        return _lines(
            _PATH,
            f"const file = {_abs(a['file'])};",
            "console.log(path.basename(file, path.extname(file)));",
        )
    if want == "ext":
        return _lines(
            _PATH,
            f"const file = {_abs(a['file'])};",
            "const ext = path.extname(file);",
            "console.log(ext === '' ? 'none' : ext);",
        )
    if want == "dir":
        return _lines(
            _PATH,
            f"const file = {_abs(a['file'])};",
            "console.log(path.dirname(file));",
        )
    if want == "rel":
        return _lines(
            _PATH,
            f"const from = {_abs(a['from'])};",
            f"const to = {_abs(a['to'])};",
            "console.log(path.relative(from, to));",
        )
    if want == "abs":
        return _lines(
            _PATH,
            f"const p = {_s(a['p'])};",
            "console.log(path.isAbsolute(p));",
        )
    raise ValueError(want)


def _path_out(a: dict) -> str:
    want = a["want"]
    if want == "join":
        parts = list(a["parts"])
        if len(parts) < 3 or any(not _SEG.fullmatch(p) for p in parts[1:]):
            raise ValueError("three pieces or more, none with a slash in")
        if not (_SEG.fullmatch(parts[0]) or _ABS.fullmatch(parts[0])):
            raise ValueError("the first piece is a folder")
        if ".." not in parts:
            raise ValueError("a piece of '..' is the point of the join")
        out = posixpath.normpath("/".join(parts))
        if out in (".", "/") or out.startswith(".."):
            raise ValueError("the join has to stay inside where it started")
        return out
    if want == "resolve":
        base, rest = a["base"], list(a["rest"])
        _abs(base)
        if not rest or any(r.startswith("/") for r in rest):
            raise ValueError("relative pieces after the base")
        out = posixpath.normpath(posixpath.join(base, *rest))
        if out == "/":
            raise ValueError("not the root")
        return out
    if want in ("name", "ext", "dir"):
        p = a["file"]
        _abs(p)
        base, ext = _file_parts(p)
        if want == "name":
            return base[: len(base) - len(ext)]
        if want == "ext":
            return ext or "none"
        return posixpath.dirname(p)
    if want == "rel":
        start, to = a["from"], a["to"]
        _abs(start)
        _abs(to)
        if start == to:
            raise ValueError("the same place: node says '' and Python '.'")
        return posixpath.relpath(to, start)
    if want == "abs":
        p = a["p"]
        _s(p)
        return _bool(p.startswith("/"))
    raise ValueError(want)


# ── 2. Command-line arguments ────────────────────────────────


def _argv(argv) -> str:
    argv = list(argv)
    if argv[:1] != ["node"] or len(argv) < 3 or not argv[1].endswith(".js"):
        raise ValueError("argv starts with node and a script, then the arguments")
    return f"const argv = {_arr(argv)};"


def _args(argv) -> list[str]:
    _argv(argv)
    return list(argv[2:])


def _args_head(a: dict) -> list[str]:
    return [_argv(a["argv"]), "const args = argv.slice(2);"]


def _args_prog(a: dict) -> str:
    want = a["want"]
    if want == "flag":
        flag, default = _ident(a["flag"]), a["default"]
        return _lines(
            *_args_head(a),
            f"const i = args.indexOf('--{flag}');",
            f"console.log(i === -1 ? {_s(default)} : args[i + 1]);",
        )
    if want == "has":
        short, long = _ident(a["short"]), _ident(a["long"])
        return _lines(
            *_args_head(a),
            f"console.log(args.includes('-{short}') || args.includes('--{long}'));",
        )
    if want == "eq":
        key, op = _ident(a["key"]), a["op"]
        math = {"double": f"{key} * 2", "next": f"{key} + 1"}[op]
        return _lines(
            _argv(a["argv"]),
            f"const arg = argv.slice(2).find((a) => a.startsWith('--{key}='));",
            f"const {key} = arg ? Number(arg.split('=')[1]) : {_int(a['default'])};",
            f"console.log({math});",
        )
    if want == "positional":
        return _lines(
            *_args_head(a),
            "console.log(args.filter((a) => !a.startsWith('-')).join(', '));",
        )
    if want == "count":
        return _lines(
            *_args_head(a),
            "console.log(args.filter((a) => a.startsWith('-')).length);",
        )
    if want == "options":
        return _lines(
            *_args_head(a),
            "const options = {};",
            "for (const arg of args) {",
            "  const [key, value] = arg.slice(2).split('=');",
            "  options[key] = value === undefined ? true : value;",
            "}",
            "console.log(JSON.stringify(options));",
        )
    if want == "sum":
        return _lines(
            *_args_head(a),
            "console.log(args.map(Number).reduce((a, b) => a + b, 0));",
        )
    raise ValueError(want)


def _args_out(a: dict) -> str:
    want = a["want"]
    args = _args(a["argv"])
    flags = [x for x in args if x.startswith("-")]
    plain = [x for x in args if not x.startswith("-")]
    if want == "flag":
        flag = "--" + _ident(a["flag"])
        _s(a["default"])
        found = [i for i, x in enumerate(args) if x == flag]
        if len(found) > 1:
            raise ValueError("the flag is given twice")
        if not found:
            return a["default"]
        i = found[0]
        if i + 1 >= len(args) or args[i + 1].startswith("-"):
            raise ValueError("a flag with no value after it")
        return args[i + 1]
    if want == "has":
        _ident(a["short"])
        _ident(a["long"])
        return _bool(
            f"-{a['short']}" in args or f"--{a['long']}" in args)
    if want == "eq":
        prefix = f"--{_ident(a['key'])}="
        given = [x for x in args if x.startswith(prefix)]
        if len(given) > 1:
            raise ValueError("the option is given twice")
        if given:
            text = given[0][len(prefix):]
            if not text.isdigit():
                raise ValueError("a whole number after the =")
            value = int(text)
        else:
            value = int(_int(a["default"]))
        if a["op"] == "double":
            return str(value * 2)
        if a["op"] == "next":
            return str(value + 1)
        raise ValueError(a["op"])
    if want in ("positional", "count"):
        if not flags or not plain:
            raise ValueError("some flags and some plain arguments, or nothing is filtered")
        if want == "positional":
            return ", ".join(plain)
        return str(len(flags))
    if want == "options":
        out: dict = {}
        for arg in args:
            if not arg.startswith("--"):
                raise ValueError("every argument is an option here")
            key, eq, value = arg[2:].partition("=")
            _ident(key)
            if key in out:
                raise ValueError("an option given twice")
            if eq and (not value.isalnum() or "=" in value):
                raise ValueError("a plain value after the =")
            out[key] = value if eq else True
        if len(out) < 2 or True not in out.values() or all(
                v is True for v in out.values()):
            raise ValueError("a mix of flags with values and flags without")
        return _compact(out)
    if want == "sum":
        total = 0.0
        for x in args:
            if not re.fullmatch(r"-?\d+(\.5)?", x):
                raise ValueError(f"{x!r}: whole numbers and halves only")
            total = total + float(x)
        return _num(total)
    raise ValueError(want)


# ── 3. Reading files ─────────────────────────────────────────


def _read(a: dict) -> str:
    want, lines = a["want"], list(a["lines"])
    name = _name(a.get("file", "notes.txt"))
    if want == "crlf":
        text = _literal_text(lines, "\\r\\n", end=False)
        return _in_dir(
            f"fs.writeFileSync(file, {text});",
            "const lines = fs.readFileSync(file, 'utf8').split(/\\r?\\n/);",
            "console.log(lines.length);",
            "console.log(lines[lines.length - 1].length);",
            file=name,
        )
    text = _literal_text(lines)
    write = f"fs.writeFileSync(file, {text});"
    if want == "words":
        return _in_dir(
            write,
            "const text = fs.readFileSync(file, 'utf8');",
            "console.log(text.trim().split(/\\s+/).length);",
            file=name,
        )
    read = "const lines = fs.readFileSync(file, 'utf8').trim().split('\\n');"
    show = {
        "count": "console.log(lines.length);",
        "last": "console.log(lines.at(-1));",
        "longest": "console.log(lines.reduce((a, b) => (b.length > a.length ? b : a)));",
        "sum": "console.log(lines.map(Number).reduce((a, b) => a + b, 0));",
    }
    if want == "find":
        word = _s(a["word"])
        show[want] = f"console.log(lines.findIndex((l) => l.includes({word})) + 1);"
    if want not in show:
        raise ValueError(want)
    return _in_dir(write, read, show[want], file=name)


def _read_out(a: dict) -> str:
    want, lines = a["want"], list(a["lines"])
    _literal_text(lines)
    if any(not x for x in lines):
        raise ValueError("no blank lines")
    if want == "count":
        if len(lines) < 3:
            raise ValueError("three lines at least")
        return str(len(lines))
    if want == "last":
        return lines[-1]
    if want == "words":
        if any("  " in x for x in lines):
            raise ValueError("single spaces only, so words are unambiguous")
        return str(sum(len(x.split(" ")) for x in lines))
    if want == "longest":
        top = max(len(x) for x in lines)
        best = [x for x in lines if len(x) == top]
        if len(best) != 1:
            raise ValueError("a tie for the longest line")
        return best[0]
    if want == "sum":
        if any(not re.fullmatch(r"-?\d+", x) for x in lines):
            raise ValueError("whole numbers, one a line")
        return str(sum(int(x) for x in lines))
    if want == "find":
        word = a["word"]
        _s(word)
        hits = [i for i, x in enumerate(lines, start=1) if word in x]
        return str(hits[0] if hits else 0)
    if want == "crlf":
        if len(lines) < 3:
            raise ValueError("three lines at least")
        return NL.join([str(len(lines)), str(len(lines[-1]))])
    raise ValueError(want)


# ── 4. Writing files ─────────────────────────────────────────


def _write(a: dict) -> str:
    want, name = a["want"], _name(a.get("file", "out.txt"))
    if want == "append_count":
        first, more = a["first"], list(a["more"])
        return _in_dir(
            f"fs.writeFileSync(file, {_literal_text([first])});",
            *(f"fs.appendFileSync(file, {_literal_text([m])});" for m in more),
            "console.log(fs.readFileSync(file, 'utf8').trim().split('\\n').length);",
            file=name,
        )
    if want == "append_text":
        first, more = a["first"], list(a["more"])
        return _in_dir(
            f"fs.writeFileSync(file, {_s(first)});",
            *(f"fs.appendFileSync(file, {_s(m)});" for m in more),
            "console.log(fs.readFileSync(file, 'utf8'));",
            file=name,
        )
    if want == "overwrite":
        return _in_dir(
            *(f"fs.writeFileSync(file, {_s(t)});" for t in a["texts"]),
            "console.log(fs.readFileSync(file, 'utf8'));",
            file=name,
        )
    if want == "size":
        return _in_dir(
            f"fs.writeFileSync(file, {_s(a['text'])});",
            "console.log(fs.statSync(file).size);",
            file=name,
        )
    if want == "steps":
        body = []
        for step in a["steps"]:
            body.append({
                "check": "console.log(fs.existsSync(file));",
                "write": "fs.writeFileSync(file, 'data');",
                "delete": "fs.unlinkSync(file);",
            }[step])
        return _in_dir(*body, file=name)
    if want == "rename":
        moved = _name(a["moved"])
        return _in_dir(
            f"const moved = path.join(dir, {_s(moved)});",
            f"fs.writeFileSync(file, {_s(a['text'])});",
            "fs.renameSync(file, moved);",
            "console.log(fs.existsSync(file));",
            "console.log(fs.readFileSync(moved, 'utf8'));",
            file=name,
        )
    raise ValueError(want)


def _write_out(a: dict) -> str:
    want = a["want"]
    if want == "append_count":
        more = list(a["more"])
        _literal_text([a["first"], *more])
        if not 1 <= len(more) <= 3:
            raise ValueError("one to three appends")
        return str(1 + len(more))
    if want == "append_text":
        more = list(a["more"])
        _s(a["first"])
        if not 1 <= len(more) <= 3:
            raise ValueError("one to three appends")
        text = a["first"] + "".join(_s(m) and m for m in more)
        if text != text.strip():
            raise ValueError("no spaces at the ends of the printed text")
        return text
    if want == "overwrite":
        texts = list(a["texts"])
        if not 2 <= len(texts) <= 3 or len(set(texts)) != len(texts):
            raise ValueError("two or three different texts")
        for t in texts:
            _s(t)
        if texts[-1] != texts[-1].strip():
            raise ValueError("no spaces at the ends of the printed text")
        return texts[-1]
    if want == "size":
        text = a["text"]
        _s(text)
        return str(len(text.encode("utf-8")))
    if want == "steps":
        steps = list(a["steps"])
        exists, out = False, []
        for step in steps:
            if step == "check":
                out.append(_bool(exists))
            elif step == "write":
                exists = True
            elif step == "delete":
                if not exists:
                    raise ValueError("deleting a file that is not there throws")
                exists = False
            else:
                raise ValueError(step)
        if not out or len(steps) > 4:
            raise ValueError("up to four steps, with a check")
        return NL.join(out)
    if want == "rename":
        _name(a["moved"])
        _s(a["text"])
        if a["moved"] == a.get("file", "out.txt"):
            raise ValueError("a new name")
        return NL.join(["false", a["text"]])
    raise ValueError(want)


# ── 5. JSON on disk ──────────────────────────────────────────


def _json(a: dict) -> str:
    want, name = a["want"], _name(a.get("file", "data.json"))
    if want == "field":
        key = _ident(a["key"])
        return _in_dir(
            f"const record = {_obj(a['obj'])};",
            "fs.writeFileSync(file, JSON.stringify(record));",
            "const data = JSON.parse(fs.readFileSync(file, 'utf8'));",
            f"console.log(data.{key});",
            file=name,
        )
    if want == "update":
        key = _ident(a["key"])
        return _in_dir(
            f"fs.writeFileSync(file, JSON.stringify({_obj(a['obj'])}));",
            "const data = JSON.parse(fs.readFileSync(file, 'utf8'));",
            f"data.{key} += {_int(a['step'])};",
            "fs.writeFileSync(file, JSON.stringify(data));",
            "console.log(fs.readFileSync(file, 'utf8'));",
            file=name,
        )
    if want == "pretty":
        return _in_dir(
            f"const settings = {_obj(a['obj'])};",
            "fs.writeFileSync(file, JSON.stringify(settings, null, 2));",
            "console.log(fs.readFileSync(file, 'utf8'));",
            file=name,
        )
    if want in ("total", "names"):
        items = ", ".join(
            f"{{ name: {_s(n)}, price: {_int(p)}, qty: {_int(q)} }}"
            for n, p, q in a["items"])
        if want == "total":
            show = "console.log(data.reduce((sum, it) => sum + it.price * it.qty, 0));"
        else:
            show = (f"console.log(data.filter((it) => it.price > {_int(a['limit'])})"
                    ".map((it) => it.name).join(', '));")
        return _in_dir(
            f"const items = [{items}];",
            "fs.writeFileSync(file, JSON.stringify(items));",
            "const data = JSON.parse(fs.readFileSync(file, 'utf8'));",
            show,
            file=name,
        )
    if want == "default":
        key = _ident(a["key"])
        write = ([f"fs.writeFileSync(file, JSON.stringify({{ {key}: {_s(a['saved'])} }}));"]
                 if a["saved"] is not None else [])
        return _in_dir(
            *write,
            f"let config = {{ {key}: {_s(a['default'])} }};",
            "if (fs.existsSync(file)) config = JSON.parse(fs.readFileSync(file, 'utf8'));",
            f"console.log(config.{key});",
            file=name,
        )
    if want == "safe":
        text = a["text"]
        if not re.fullmatch(r"[A-Za-z0-9 _.,:{}\[\]\"-]+", text):
            raise ValueError(f"{text!r}: plain JSON-ish text, no single quotes")
        return _lines(
            f"const text = '{text}';",
            "try {",
            "  console.log(JSON.stringify(JSON.parse(text)));",
            "} catch (err) {",
            "  console.log('invalid');",
            "}",
        )
    raise ValueError(want)


def _no_constants(name: str):
    raise ValueError(f"{name} is not JSON")


def _json_out(a: dict) -> str:
    want = a["want"]
    if want == "field":
        obj, key = dict(a["obj"]), a["key"]
        _obj(obj)
        _plain(obj)
        if key not in obj:
            raise ValueError("a key that is there")
        value = obj[key]
        if isinstance(value, list):
            raise ValueError("a single value, not a list")
        return _bool(value) if isinstance(value, bool) else str(value)
    if want == "update":
        obj = dict(a["obj"])
        _obj(obj)
        _plain(obj)
        key, step = a["key"], a["step"]
        if not isinstance(obj.get(key), int) or isinstance(obj[key], bool) or not step:
            raise ValueError("a number to add to, and a step that does something")
        obj[key] = obj[key] + step
        return _compact(obj)
    if want == "pretty":
        obj = dict(a["obj"])
        _obj(obj)
        _plain(obj)
        if not any(isinstance(v, list) for v in obj.values()):
            raise ValueError("a list in the object, or indenting hardly shows")
        return json.dumps(obj, indent=2, ensure_ascii=False)
    if want in ("total", "names"):
        items = [tuple(i) for i in a["items"]]
        for n, p, q in items:
            _s(n)
            if p < 0 or q < 1:
                raise ValueError("prices from zero, at least one of each")
        if len(items) < 3 or len({n for n, _, _ in items}) != len(items):
            raise ValueError("three different items at least")
        if want == "total":
            return str(sum(p * q for _, p, q in items))
        limit = a["limit"]
        kept = [n for n, p, _ in items if p > limit]
        if not kept or len(kept) == len(items) or any(p == limit for _, p, _ in items):
            raise ValueError("a limit that keeps some, drops some and ties none")
        return ", ".join(kept)
    if want == "default":
        _ident(a["key"])
        _s(a["default"])
        if a["saved"] is None:
            return a["default"]
        _s(a["saved"])
        if a["saved"] == a["default"]:
            raise ValueError("the saved value has to differ from the default")
        return a["saved"]
    if want == "safe":
        text = a["text"]
        try:
            value = json.loads(text, parse_constant=_no_constants)
        except ValueError:
            return "invalid"
        return _compact(value)
    raise ValueError(want)


# ── 6. Directories ───────────────────────────────────────────


def _make_names(names) -> list[str]:
    names = _unique(_name(n) for n in names)
    if len(names) < 3:
        raise ValueError("three names at least")
    return names


def _dirs(a: dict) -> str:
    want = a["want"]
    if want in ("list", "ext", "extcount", "delete"):
        names = a["names"]
        lines = [
            f"const names = {_arr(names)};",
            "for (const name of names) fs.writeFileSync(path.join(dir, name), '');",
        ]
        if want == "list":
            lines.append("console.log(fs.readdirSync(dir).sort().join(', '));")
        elif want in ("ext", "extcount"):
            ext = _s("." + _ident(a["ext"]))
            lines.append(
                f"const found = fs.readdirSync(dir).filter((n) => n.endsWith({ext})).sort();")
            lines.append("console.log(found.join(', '));" if want == "ext"
                         else "console.log(found.length);")
        else:
            lines.insert(1, f"const gone = {_arr(a['gone'])};")
            lines.append("for (const n of gone) fs.unlinkSync(path.join(dir, n));")
            lines.append("console.log(fs.readdirSync(dir).sort().join(', '));")
        return _in_dir(*lines)
    if want == "size":
        files = ", ".join(f"{_s(n)}: {_s(t)}" for n, t in a["files"].items())
        return _in_dir(
            f"const files = {{ {files} }};",
            "for (const [name, text] of Object.entries(files)) {"
            " fs.writeFileSync(path.join(dir, name), text); }",
            "const sizes = fs.readdirSync(dir).map((n) => fs.statSync(path.join(dir, n)).size);",
            "console.log(sizes.reduce((a, b) => a + b, 0));",
        )
    if want in ("dirs", "files"):
        test = "e.isDirectory()" if want == "dirs" else "e.isFile()"
        return _in_dir(
            f"const names = {_arr(a['names'])};",
            "for (const n of names) {"
            " if (n.endsWith('/')) fs.mkdirSync(path.join(dir, n));"
            " else fs.writeFileSync(path.join(dir, n), ''); }",
            "const entries = fs.readdirSync(dir, { withFileTypes: true });",
            f"console.log(entries.filter((e) => {test}).map((e) => e.name).sort().join(', '));",
        )
    raise ValueError(want)


def _sorted_names(found: list[str]) -> list[str]:
    return sorted(found)  # code-unit order, as Array.prototype.sort does


def _dirs_out(a: dict) -> str:
    want = a["want"]
    if want == "list":
        names = _make_names(a["names"])
        if names == sorted(names):
            raise ValueError("already sorted, so sorting shows nothing")
        return ", ".join(_sorted_names(names))
    if want in ("ext", "extcount"):
        names = _make_names(a["names"])
        ext = "." + _ident(a["ext"])
        found = [n for n in names if n.endswith(ext)]
        if not found or len(found) == len(names):
            raise ValueError("an extension that keeps some and drops some")
        if want == "extcount":
            return str(len(found))
        if len(found) < 2:
            raise ValueError("two matches, or sorting shows nothing")
        return ", ".join(_sorted_names(found))
    if want == "delete":
        names = _make_names(a["names"])
        gone = _unique(a["gone"], "removals")
        if not gone or any(g not in names for g in gone) or len(gone) >= len(names) - 1:
            raise ValueError("remove some of the names, but leave two or more")
        left = [n for n in names if n not in gone]
        return ", ".join(_sorted_names(left))
    if want == "size":
        files = dict(a["files"])
        _make_names(files)
        for text in files.values():
            _s(text)
            if not text.isascii():
                raise ValueError("ASCII text, so characters are bytes")
        return str(sum(len(t.encode("utf-8")) for t in files.values()))
    if want in ("dirs", "files"):
        names = list(a["names"])
        stems = _unique(n.removesuffix("/") for n in names)
        for stem in stems:
            _name(stem)
        folders = [n.removesuffix("/") for n in names if n.endswith("/")]
        plain = [n for n in names if not n.endswith("/")]
        if len(folders) < 2 or len(plain) < 2:
            raise ValueError("two folders and two files at least")
        return ", ".join(_sorted_names(folders if want == "dirs" else plain))
    raise ValueError(want)


# ── 7. Events, timers and streams ────────────────────────────

_EMITTER = "const { EventEmitter } = require('node:events');"
_NEW = "const emitter = new EventEmitter();"


def _events(a: dict) -> str:
    want = a["want"]
    if want == "log":
        ev, word = _ident(a["event"]), a["word"]
        return _lines(
            _EMITTER,
            _NEW,
            f"emitter.on('{ev}', (name) => console.log(`{_s(word)[1:-1]}, ${{name}}!`));",
            f"for (const name of {_arr(a['names'])}) emitter.emit('{ev}', name);",
        )
    if want == "two":
        ev, (one, two) = _ident(a["event"]), a["labels"]
        second = "prependListener" if a["prepend"] else "on"
        return _lines(
            _EMITTER,
            _NEW,
            f"emitter.on('{ev}', () => console.log({_s(one)}));",
            f"emitter.{second}('{ev}', () => console.log({_s(two)}));",
            *(f"emitter.emit('{ev}');" for _ in range(a["times"])),
        )
    if want == "count":
        ev, mode = _ident(a["event"]), a["mode"]
        if mode not in ("on", "once"):
            raise ValueError(mode)
        return _lines(
            _EMITTER,
            _NEW,
            "let calls = 0;",
            f"emitter.{mode}('{ev}', () => {{ calls++; }});",
            f"for (let i = 0; i < {_int(a['n'])}; i++) emitter.emit('{ev}');",
            "console.log(calls);",
        )
    if want == "returns":
        ev, mode = _ident(a["event"]), a["mode"]
        if mode not in ("on", "once"):
            raise ValueError(mode)
        return _lines(
            _EMITTER,
            _NEW,
            f"emitter.{mode}('{ev}', () => {{}});",
            *(f"console.log(emitter.emit('{_ident(e)}'));" for e in a["emits"]),
        )
    if want == "sum":
        ev = _ident(a["event"])
        return _lines(
            _EMITTER,
            _NEW,
            "let total = 0;",
            f"emitter.on('{ev}', (n) => {{ total += n; }});",
            f"for (const n of [{', '.join(_int(n) for n in a['numbers'])}]) "
            f"emitter.emit('{ev}', n);",
            "console.log(total);",
        )
    if want == "cart":
        ev = _ident(a["event"])
        sales = " ".join(f"emitter.emit('{ev}', {_int(p)}, {_int(q)});"
                          for p, q in a["sales"])
        return _lines(
            _EMITTER,
            _NEW,
            "let total = 0;",
            f"emitter.on('{ev}', (price, qty) => {{ total += price * qty; }});",
            sales,
            "console.log(total);",
        )
    if want == "timers":
        jobs = ", ".join(f"[{_s(label)}, {_int(ms)}]" for label, ms in a["jobs"])
        return _lines(
            f"const jobs = [{jobs}];",
            "for (const [label, ms] of jobs) setTimeout(() => console.log(label), ms);",
            f"console.log({_s(a['sync'])});",
        )
    if want in ("upper", "count_chunks", "length"):
        chunks = _arr(a["chunks"])
        init, on_data, end = {
            "upper": ("let text = '';", "(c) => { text += c; }",
                      "console.log(text.toUpperCase())"),
            "count_chunks": ("let n = 0;", "() => { n++; }", "console.log(n)"),
            "length": ("let n = 0;", "(c) => { n += c.length; }", "console.log(n)"),
        }[want]
        return _lines(
            "const { Readable } = require('node:stream');",
            f"const chunks = {chunks};",
            init,
            f"Readable.from(chunks).on('data', {on_data}).on('end', () => {end});",
        )
    raise ValueError(want)


def _events_out(a: dict) -> str:
    want = a["want"]
    if want == "log":
        _ident(a["event"])
        _s(a["word"])
        names = _unique(a["names"])
        if len(names) < 2:
            raise ValueError("two names at least")
        return NL.join(f"{a['word']}, {n}!" for n in names)
    if want == "two":
        _ident(a["event"])
        one, two = a["labels"]
        _s(one)
        _s(two)
        if one == two or not 1 <= a["times"] <= 3:
            raise ValueError("two different labels, one to three emits")
        order = [two, one] if a["prepend"] else [one, two]
        return NL.join(order * a["times"])
    if want == "count":
        _ident(a["event"])
        n = a["n"]
        if not isinstance(n, int) or not 2 <= n <= 5:
            raise ValueError("two to five emits")
        return str(n if a["mode"] == "on" else min(n, 1))
    if want == "returns":
        _ident(a["event"])
        mode, emits = a["mode"], list(a["emits"])
        if len(emits) < 2:
            raise ValueError("two emits at least")
        listening, out = True, []
        for e in emits:
            _ident(e)
            heard = listening and e == a["event"]
            out.append(_bool(heard))
            if heard and mode == "once":
                listening = False
        return NL.join(out)
    if want == "sum":
        _ident(a["event"])
        return str(sum(int(_int(n)) for n in a["numbers"]))
    if want == "cart":
        _ident(a["event"])
        return str(sum(int(_int(p)) * int(_int(q)) for p, q in a["sales"]))
    if want == "timers":
        jobs = [tuple(j) for j in a["jobs"]]
        _s(a["sync"])
        delays = sorted(ms for _, ms in jobs)
        if len(jobs) < 3 or any(
                b - x < 10 for x, b in zip(delays, delays[1:])) or delays[-1] > 80:
            raise ValueError("three timers at least, 10 ms apart, under 80 ms")
        labels = _unique(label for label, _ in jobs)
        if a["sync"] in labels or [ms for _, ms in jobs] == delays:
            raise ValueError("a sync line of its own, and jobs out of order")
        return NL.join([a["sync"], *(label for label, _ in sorted(jobs, key=lambda j: j[1]))])
    if want in ("upper", "count_chunks", "length"):
        chunks = list(a["chunks"])
        for c in chunks:
            _s(c)
        if len(chunks) < 3:
            raise ValueError("three chunks at least")
        if want == "upper":
            return "".join(chunks).upper()
        if want == "count_chunks":
            return str(len(chunks))
        return str(sum(len(c) for c in chunks))
    raise ValueError(want)


# ── 8. Environment, exit codes and the exit event ────────────

_RULES = {
    "even": ("input % 2 !== 0", "must be even"),
    "positive": ("input <= 0", "must be positive"),
    "small": ("input >= 100", "must be under 100"),
}


def _env_object(env: dict) -> str:
    if not env:
        raise ValueError("an environment with something in it")
    parts = []
    for k, v in env.items():
        if not re.fullmatch(r"[A-Z][A-Z_]*", k):
            raise ValueError(f"{k!r}: environment names are UPPER_CASE")
        parts.append(f"{k}: {_s(v) if v != '' else chr(39) * 2}")
    return "const env = { " + ", ".join(parts) + " };"


def _env(a: dict) -> str:
    want = a["want"]
    if want == "port":
        return _lines(
            _env_object(a["env"]),
            f"const port = Number(env.PORT || {_int(a['default'])});",
            "console.log(port);",
        )
    if want == "flag":
        key = a["key"]
        return _lines(
            _env_object(a["env"]),
            f"const enabled = env.{key} === 'true';",
            "console.log(enabled);",
        )
    if want == "mode":
        key = a["key"]
        return _lines(
            _env_object(a["env"]),
            f"const value = env.{key} || {_s(a['default'])};",
            f"console.log(`{key} is ${{value}}`);",
        )
    if want == "list":
        return _lines(
            _env_object(a["env"]),
            "const tags = env.TAGS ? env.TAGS.split(',') : [];",
            "console.log(tags.length);",
            "console.log(tags.join(' | ') || 'none');",
        )
    if want == "exit":
        test, message = _RULES[a["rule"]]
        return _lines(
            f"const input = {_int(a['input'])};",
            "let code = 0;",
            "try {",
            f"  if ({test}) throw new Error('{message}');",
            "  console.log(`ok ${input}`);",
            "} catch (err) {",
            "  console.log(`error: ${err.message}`);",
            "  code = 1;",
            "}",
            "console.log(`exit code ${code}`);",
        )
    if want == "onexit":
        timer = ([f"setTimeout(() => console.log({_s(a['timer'])}), 5);"]
                 if a["timer"] else [])
        return _lines(
            "process.on('exit', (code) => console.log(`bye ${code}`));",
            *timer,
            *(f"console.log({_s(x)});" for x in a["lines"]),
        )
    raise ValueError(want)


def _env_out(a: dict) -> str:
    want = a["want"]
    if want in ("port", "flag", "mode", "list"):
        env = dict(a["env"])
        _env_object(env)
    if want == "port":
        default = int(_int(a["default"]))
        text = env.get("PORT", "")
        if text and not text.isdigit():
            raise ValueError("a PORT that is a whole number")
        if text == "0":
            raise ValueError("a PORT of 0 is an odd one")
        return str(int(text) if text else default)
    if want == "flag":
        if not re.fullmatch(r"[A-Z][A-Z_]*", a["key"]):
            raise ValueError("an UPPER_CASE name")
        return _bool(env.get(a["key"]) == "true")
    if want == "mode":
        if not re.fullmatch(r"[A-Z][A-Z_]*", a["key"]):
            raise ValueError("an UPPER_CASE name")
        _s(a["default"])
        return f"{a['key']} is {env.get(a['key']) or a['default']}"
    if want == "list":
        tags = env["TAGS"].split(",") if env.get("TAGS") else []
        if any(not t or " " in t for t in tags):
            raise ValueError("plain tags, none empty")
        return NL.join([str(len(tags)), " | ".join(tags) or "none"])
    if want == "exit":
        test_rule = a["rule"]
        n = int(_int(a["input"]))
        if test_rule == "even":
            bad, message = n % 2 != 0, "must be even"
        elif test_rule == "positive":
            bad, message = n <= 0, "must be positive"
        elif test_rule == "small":
            bad, message = n >= 100, "must be under 100"
        else:
            raise ValueError(test_rule)
        if bad:
            return NL.join([f"error: {message}", "exit code 1"])
        return NL.join([f"ok {n}", "exit code 0"])
    if want == "onexit":
        lines = list(a["lines"])
        if len(lines) < 2:
            raise ValueError("two lines at least")
        for x in lines:
            _s(x)
        timer = [a["timer"]] if a["timer"] else []
        for x in timer:
            _s(x)
        return NL.join([*lines, *timer, "bye 0"])
    raise ValueError(want)


# ── 9. A small server ────────────────────────────────────────

_HTTP = "const http = require('node:http');"
_LISTEN = "server.listen(0, '127.0.0.1', async () => {"
_BASE = "`http://127.0.0.1:${server.address().port}"
_CLOSE = ("  server.close();", "});")
_HEADER_NAMES = {"X-Greeting", "X-Mood", "X-Team", "Content-Type"}
_STATUSES = {200, 201, 202, 400, 401, 403, 404, 418, 500}


def _path_text(p: str) -> str:
    if not re.fullmatch(r"/[A-Za-z0-9/?=&%+._-]*", p):
        raise ValueError(f"{p!r}: a plain URL path")
    return p


def _http(a: dict) -> str:
    want = a["want"]
    if want == "body":
        return _lines(
            _HTTP,
            "const server = http.createServer((req, res) => {",
            f"  res.writeHead({_int(a['status'])});",
            f"  res.end({_s(a['text'])});",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}/`);",
            "  console.log(res.status, await res.text());",
            *_CLOSE,
        )
    if want == "header":
        name, value = a["header"], a["value"]
        return _lines(
            _HTTP,
            "const server = http.createServer((req, res) => {",
            f"  res.writeHead(200, {{ {_s(name)}: {_s(value)} }});",
            f"  res.end({_s(a['text'])});",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}/`);",
            f"  console.log(res.headers.get({_s(name.lower())}), await res.text());",
            *_CLOSE,
        )
    if want == "json":
        key = _ident(a["key"])
        return _lines(
            _HTTP,
            "const server = http.createServer((req, res) => {",
            "  res.writeHead(200, { 'Content-Type': 'application/json' });",
            f"  res.end(JSON.stringify({_obj(a['obj'])}));",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}/`);",
            f"  const data = await res.json(); console.log(data.{key});",
            *_CLOSE,
        )
    if want == "method":
        method, path = a["method"], _path_text(a["path"])
        options = f", {{ method: {_s(method)} }}"
        return _lines(
            _HTTP,
            "const server = http.createServer((req, res) => {",
            "  res.end(`${req.method} ${req.url}`);",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}{path}`{options});",
            "  console.log(await res.text());",
            *_CLOSE,
        )
    if want == "count":
        return _lines(
            _HTTP,
            f"let hits = {_int(a['start'])};",
            "const server = http.createServer((req, res) => res.end(String(++hits)));",
            _LISTEN,
            f"  const url = {_BASE}/`;",
            "  const seen = [];",
            f"  for (let i = 0; i < {_int(a['n'])}; i++) "
            "seen.push(await (await fetch(url)).text());",
            "  console.log(seen.join(', '));",
            *_CLOSE,
        )
    raise ValueError(want)


def _http_out(a: dict) -> str:
    want = a["want"]
    if want == "body":
        text = a["text"]
        _s(text)
        if a["status"] not in _STATUSES or text != text.strip():
            raise ValueError("an ordinary status, and text with no spaces at the ends")
        return f"{a['status']} {text}"
    if want == "header":
        name, value, text = a["header"], a["value"], a["text"]
        _s(value)
        _s(text)
        if name not in _HEADER_NAMES or value != value.strip() or text != text.strip():
            raise ValueError("a header name from the list, and plain values")
        return f"{value} {text}"
    if want == "json":
        obj, key = dict(a["obj"]), a["key"]
        _obj(obj)
        _plain(obj)
        value = obj[key]
        if isinstance(value, list):
            raise ValueError("one value")
        return _bool(value) if isinstance(value, bool) else str(value)
    if want == "method":
        method, path = a["method"], _path_text(a["path"])
        if method not in ("GET", "POST", "PUT", "DELETE", "PATCH"):
            raise ValueError(method)
        return f"{method} {path}"
    if want == "count":
        start, n = int(_int(a["start"])), a["n"]
        if not isinstance(n, int) or not 2 <= n <= 5 or start < 0:
            raise ValueError("two to five requests, counting up from zero or more")
        return ", ".join(str(start + i) for i in range(1, n + 1))
    raise ValueError(want)


# ── 10. Routes ───────────────────────────────────────────────

_SERVER = "const server = require('node:http').createServer"


def _routes(a: dict) -> str:
    want = a["want"]
    if want == "greet":
        word, path = _s(a["fallback"]), _path_text(a["path"])
        return _lines(
            f"{_SERVER}((req, res) => {{",
            "  const { pathname, searchParams } = new URL(req.url, 'http://x');",
            "  if (pathname !== '/hello') return res.writeHead(404).end('not found');",
            f"  res.end(`Hello, ${{searchParams.get('name') ?? {word}}}!`);",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}{path}`);",
            "  console.log(res.status, await res.text());",
            *_CLOSE,
        )
    if want == "sum":
        x, y = _ident(a["keys"][0]), _ident(a["keys"][1])
        op = a["op"]
        if op not in ("+", "-", "*"):
            raise ValueError(op)
        path = _path_text(f"/calc?{x}={a['x']}&{y}={a['y']}")
        return _lines(
            f"{_SERVER}((req, res) => {{",
            "  const { searchParams } = new URL(req.url, 'http://x');",
            f"  const result = Number(searchParams.get('{x}')) {op} "
            f"Number(searchParams.get('{y}'));",
            "  res.writeHead(200, { 'Content-Type': 'application/json' })"
            ".end(JSON.stringify({ result }));",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}{path}`);",
            "  console.log(res.headers.get('content-type'), (await res.json()).result);",
            *_CLOSE,
        )
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        path = _path_text(a["path"])
        return _lines(
            f"{_SERVER}((req, res) => {{",
            f"  const pages = {{ {_s(p1)}: {_s(t1)}, {_s(p2)}: {_s(t2)} }};",
            "  const { pathname } = new URL(req.url, 'http://x');",
            "  res.writeHead(pathname in pages ? 200 : 404)"
            ".end(pages[pathname] ?? 'not found');",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}{path}`);",
            "  console.log(res.status, await res.text());",
            *_CLOSE,
        )
    if want == "method":
        allowed, sent, ok = a["allowed"], a["sent"], _s(a["ok"])
        return _lines(
            f"{_SERVER}((req, res) => {{",
            f"  if (req.method !== {_s(allowed)}) "
            f"return res.writeHead(405).end('use {allowed}');",
            f"  res.end({ok});",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}/items`, {{ method: {_s(sent)} }});",
            "  console.log(res.status, await res.text());",
            *_CLOSE,
        )
    if want == "post":
        reply = {
            "upper": "body.toUpperCase()",
            "length": "String(body.length)",
            "reverse": "[...body].reverse().join('')",
            "words": "String(body.split(' ').length)",
        }[a["reply"]]
        return _lines(
            f"{_SERVER}(async (req, res) => {{",
            "  let body = '';",
            "  for await (const chunk of req) body += chunk;",
            f"  res.end({reply});",
            "});",
            _LISTEN,
            f"  const res = await fetch({_BASE}/`, "
            f"{{ method: 'POST', body: {_s(a['body'])} }});",
            "  console.log(await res.text());",
            *_CLOSE,
        )
    raise ValueError(want)


def _routes_out(a: dict) -> str:
    want = a["want"]
    if want == "greet":
        _s(a["fallback"])
        parts = urlsplit(_path_text(a["path"]))
        if parts.path != "/hello":
            return "404 not found"
        names = parse_qs(parts.query, keep_blank_values=True).get("name")
        if names is not None and not names[0]:
            raise ValueError("an empty name is a puzzle of its own")
        return f"200 Hello, {names[0] if names else a['fallback']}!"
    if want == "sum":
        x, y = int(_int(a["x"])), int(_int(a["y"]))
        if _ident(a["keys"][0]) == _ident(a["keys"][1]):
            raise ValueError("two different parameter names")
        if a["op"] == "+":
            value = x + y
        elif a["op"] == "-":
            value = x - y
        elif a["op"] == "*":
            value = x * y
        else:
            raise ValueError(a["op"])
        if value == 0:
            raise ValueError("a result of 0 prints but proves little")
        return f"application/json {value}"
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        for p in (p1, p2):
            _path_text(p)
        _s(t1)
        _s(t2)
        if p1 == p2 or t1 == t2:
            raise ValueError("two different pages")
        parts = urlsplit(_path_text(a["path"]))
        table = {p1: t1, p2: t2}
        if parts.path in table:
            return f"200 {table[parts.path]}"
        return "404 not found"
    if want == "method":
        allowed, sent = a["allowed"], a["sent"]
        methods = ("GET", "POST", "PUT", "DELETE", "PATCH")
        if allowed not in methods or sent not in methods or allowed == "GET":
            raise ValueError("a method that needs asking for")
        _s(a["ok"])
        if sent == allowed:
            return f"200 {a['ok']}"
        return f"405 use {allowed}"
    if want == "post":
        body = a["body"]
        _s(body)
        if not body.isascii() or body != body.strip() or "  " in body:
            raise ValueError("plain ASCII with single spaces")
        reply = a["reply"]
        if reply == "upper":
            return body.upper()
        if reply == "length":
            return str(len(body))
        if reply == "reverse":
            if body == body[::-1]:
                raise ValueError("a palindrome reverses to itself")
            return body[::-1]
        if reply == "words":
            return str(len(body.split(" ")))
        raise ValueError(reply)
    raise ValueError(want)


_BUILDERS = {
    "js_node_path": _path,
    "js_node_args": _args_prog,
    "js_node_read": _read,
    "js_node_write": _write,
    "js_node_json": _json,
    "js_node_dirs": _dirs,
    "js_node_events": _events,
    "js_node_env": _env,
    "js_node_http": _http,
    "js_node_routes": _routes,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "js_node_path": _path_out,
    "js_node_args": _args_out,
    "js_node_read": _read_out,
    "js_node_write": _write_out,
    "js_node_json": _json_out,
    "js_node_dirs": _dirs_out,
    "js_node_events": _events_out,
    "js_node_env": _env_out,
    "js_node_http": _http_out,
    "js_node_routes": _routes_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_node_path": Cost(
        "O(n)",
        "Linear in the length of the path: every function here walks the "
        "string once, splitting at slashes and dropping the '.' and '..' "
        "pieces. A path is a handful of characters, so it is never the slow "
        "part."),
    "js_node_args": Cost(
        "O(n)",
        "Linear in the number of arguments, n: indexOf, includes, find and "
        "filter each look along the array, and parsing the options object "
        "visits every argument once."),
    "js_node_read": Cost(
        "O(n)",
        "Linear in the size of the file: readFileSync reads all of it into "
        "memory, then split, map and reduce each pass over it once. A huge "
        "file would call for a stream, one chunk at a time, so that memory "
        "stays flat."),
    "js_node_write": Cost(
        "O(n)",
        "Linear in the bytes written: writeFileSync and appendFileSync copy "
        "what they are given to disk. Appending costs only the new text; "
        "rewriting the whole file to add one line costs the whole file every "
        "time. exists, rename and unlink are single calls to the file "
        "system, whatever the file's size."),
    "js_node_json": Cost(
        "O(n)",
        "Linear in the size of the data: JSON.stringify and JSON.parse each "
        "visit every value once, and the file is read or written whole. "
        "Changing one field means loading and saving everything, which is "
        "fine for a settings file and a poor way to run a database."),
    "js_node_dirs": Cost(
        "O(n log n)",
        "n is the number of entries. Reading the folder and filtering it is "
        "one pass of n; the sort is about n log n comparisons, and it is "
        "needed because readdirSync promises no order. Adding up the file "
        "sizes costs one stat call per file."),
    "js_node_events": Cost(
        "O(n)",
        "Linear in the number of calls. emit runs each listener for its "
        "event, in the order they were added, so an event with k listeners "
        "costs k calls every time it fires. Timers run in order of their "
        "delay and a stream's data arrives one chunk at a time, so the total "
        "work grows with the number of chunks."),
    "js_node_env": Cost(
        "O(1)",
        "Constant: a property lookup and a comparison, or one split of a "
        "short list. Throwing and catching an error costs a little more "
        "than an if, but still a fixed amount, however deep the call "
        "was."),
    "js_node_http": Cost(
        "O(n)",
        "Linear in the number of requests, n: the server does a fixed amount "
        "of work for each one, and the program waits for each answer in "
        "turn. The wait is network time, not computing, and listening on "
        "port 0 lets the system pick a free port."),
    "js_node_routes": Cost(
        "O(r)",
        "Linear in the number of routes, r, for a chain of ifs, since a "
        "request that matches none of them has been compared with every "
        "one. Reading a request body is linear in its size, one chunk at a "
        "time. A lookup table makes a route O(1)."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
