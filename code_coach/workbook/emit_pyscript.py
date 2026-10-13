"""Python scripting and the standard library.

Ten pages of programs that run as plain `python file.py`: pathlib paths,
argparse over an explicit list, reading and writing files, JSON on disk,
directories, the csv module, logging to a StringIO, environment variables
and exit codes, a small HTTP server that the program then asks itself, and
asyncio with sleeps.

Everything is deterministic:

- files live in a tempfile.TemporaryDirectory that cleans itself up, and no
  program ever prints a path; text is always written and read as UTF-8, so
  Windows and Linux agree;
- sys.argv and os.environ cannot be passed in, so argparse is handed a list
  and the environment pages use a dict that stands in for it;
- the path page uses PurePosixPath, so Windows and Linux print the same;
- servers bind 127.0.0.1 on port 0, run in a daemon thread, answer a request
  or two from urllib.request, print what came back and shut down;
- asyncio sleeps are tens of milliseconds apart.

The oracle never runs the Python it describes. It works every answer out
with small models written here (a path splitter, an argparse model, a JSON
writer and parser, a csv reader and writer, a logging filter, a query-string
decoder), and the tests then hold python to it. The models are the reason
this module imports none of the libraries it describes. Rows that could
print two ways are refused with ValueError.
"""

from __future__ import annotations

import re

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("py_script_path", "pathlib: parts, stem, suffix, parents, joining and relative paths"),
    Shape("py_script_args", "argparse over an explicit list: options, flags, counts, positionals"),
    Shape("py_script_files", "writing, appending and reading back text files in a temporary folder"),
    Shape("py_script_json", "saving and loading JSON, indent and sort_keys, and catching a bad parse"),
    Shape("py_script_dirs", "making folders, filling them and listing, globbing and walking them"),
    Shape("py_script_csv", "the csv module over StringIO: readers, writers and dictionaries"),
    Shape("py_script_log", "logging to a StringIO handler with a fixed format"),
    Shape("py_script_env", "environment defaults, SystemExit, exit codes and atexit"),
    Shape("py_script_http", "a tiny http.server in a thread, asked with urllib.request"),
    Shape("py_script_async", "asyncio.gather, create_task, wait_for and sleeps"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: How long a program may be. A server needs a handler class, a thread and
#: a client, which no honest program does in ten lines.
LIMIT = 10
SERVER_LIMIT = 26


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Writing things the program types ─────────────────────────

#: Text that sits safely inside a double-quoted Python string.
_PLAIN = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()\-]+")
#: Text that is plain once a few non-ASCII characters are allowed.
_UNI = re.compile(r"[A-Za-z0-9 _.,é日本\U0001F642-]+")
_NAME = re.compile(r"[a-z][a-z0-9]*(\.[a-z0-9]+)*")
_WORD = re.compile(r"[a-z][a-z0-9]*")


def _s(x) -> str:
    """A string literal. Quotes, backslashes and the like are refused."""
    if not isinstance(x, str) or not _PLAIN.fullmatch(x):
        raise ValueError(f"{x!r}: plain text only")
    return _q(x)


def _int(x) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: a whole number")
    return x


def _name(x) -> str:
    """A file name: lowercase, with an optional extension."""
    if not isinstance(x, str) or not _NAME.fullmatch(x):
        raise ValueError(f"{x!r}: a plain lowercase file name")
    return x


def _word(x) -> str:
    if not isinstance(x, str) or not _WORD.fullmatch(x):
        raise ValueError(f"{x!r}: one lowercase word")
    return x


def _unique(items, what: str = "names") -> list:
    items = list(items)
    if len({str(i).lower() for i in items}) != len(items):
        raise ValueError(f"{what} must be unique, even ignoring case")
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
    if isinstance(v, str):
        return _s(v)
    if isinstance(v, (list, tuple)):
        return "[" + ", ".join(_pyval(i) for i in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{_s(k)}: {_pyval(x)}" for k, x in v.items()) + "}"
    raise ValueError(f"{v!r}: not a plain value")


def _say(v) -> str:
    """What print shows for a plain value."""
    if isinstance(v, (bool, int)) or v is None:
        return str(v)
    if isinstance(v, str):
        return v
    raise ValueError(f"{v!r}: not a single value")


def _in_tmp(imports, body, file: str | None = None) -> str:
    """The body inside a TemporaryDirectory, which tidies itself away."""
    lines = [f"import {m}" for m in sorted({"tempfile", *imports})]
    lines += ["from pathlib import Path", "", "with tempfile.TemporaryDirectory() as tmp:"]
    if file is not None:
        lines.append(f'    file = Path(tmp) / "{_name(file)}"')
    lines += [f"    {b}" for b in body]
    return _fit(lines)


def _text_literal(lines, end: bool = True, eol: str = "\\n") -> str:
    """The text of a file as a string literal: "a\\nb\\n"."""
    lines = list(lines)
    if not lines:
        raise ValueError("a file with something in it")
    for line in lines:
        _s(line)
        if line != line.strip():
            raise ValueError(f"{line!r}: no spaces at the ends of a line")
    return '"' + eol.join(lines) + (eol if end else "") + '"'


# ── 1. pathlib ───────────────────────────────────────────────

_PATH_RE = re.compile(r"/?[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)*")
_PP = "from pathlib import PurePosixPath"


def _clean(p) -> str:
    """A path with nothing for pathlib to tidy: no dots, no extra slashes."""
    if not isinstance(p, str) or not _PATH_RE.fullmatch(p):
        raise ValueError(f"{p!r}: a plain path, no trailing slash")
    segs = p[1:].split("/") if p.startswith("/") else p.split("/")
    for seg in segs:
        if seg in (".", "..") or seg.endswith("."):
            raise ValueError(f"{p!r}: no dot pieces and no names ending in a dot")
    return p


def _piece(x) -> str:
    """A piece to join: a name, a path, or one of the dots."""
    if x in (".", ".."):
        return x
    return _clean(x)


def _split(p: str) -> tuple[bool, list[str]]:
    """How pathlib reads text: empty pieces and single dots vanish."""
    return p.startswith("/"), [x for x in p.split("/") if x not in ("", ".")]


def _text(absolute: bool, parts: list[str]) -> str:
    body = "/".join(parts)
    if absolute:
        return "/" + body
    return body or "."


def _suffix_of(name: str) -> str:
    i = name.rfind(".")
    return name[i:] if 0 < i < len(name) - 1 else ""


def _stem_of(name: str) -> str:
    i = name.rfind(".")
    return name[:i] if 0 < i < len(name) - 1 else name


def _suffixes_of(name: str) -> list[str]:
    if name.endswith("."):
        return []
    return ["." + s for s in name.lstrip(".").split(".")[1:]]


def _file_path(p) -> tuple[bool, list[str]]:
    """A path that ends in a file name: at least two pieces."""
    absolute, parts = _split(_clean(p))
    if len(parts) < 2:
        raise ValueError("a folder and a file name at least")
    return absolute, parts


def _path(a: dict) -> str:
    want = a["want"]
    if want == "join":
        base, rest, how = _clean(a["base"]), list(a["rest"]), a["how"]
        for r in rest:
            _piece(r)
        if how == "joinpath":
            tail = ", ".join(_s(r) for r in rest)
            return _fit([_PP, "", f"base = PurePosixPath({_s(base)})",
                         f"print(base.joinpath({tail}))"])
        if how == "slash":
            tail = "".join(f" / {_s(r)}" for r in rest)
            return _fit([_PP, "", f"base = PurePosixPath({_s(base)})",
                         f"print(base{tail})"])
        raise ValueError(how)
    p = a.get("p")
    head = [_PP, "", f"path = PurePosixPath({_s(_clean(p))})"]
    if want == "parts":
        return _fit([*head, "print(path.parts)"])
    if want == "stem":
        return _fit([*head, "print(path.stem)", 'print(path.suffix or "none")'])
    if want == "suffixes":
        return _fit([*head, "print(path.suffixes)"])
    if want == "with_suffix":
        return _fit([*head, f"print(path.with_suffix({_s(a['suffix'])}))"])
    if want == "parent":
        return _fit([*head, "print(path.parent)",
                     f"print(path.parents[{_int(a['up'])}])"])
    if want == "rel":
        return _fit([*head, "try:",
                     f"    print(path.relative_to({_s(_clean(a['base']))}))",
                     "except ValueError:", '    print("outside")'])
    if want == "abs":
        return _fit([*head, "print(path.is_absolute())"])
    raise ValueError(want)


def _path_out(a: dict) -> str:
    want = a["want"]
    if want == "join":
        absolute, parts = _split(_clean(a["base"]))
        rest = list(a["rest"])
        if not 1 <= len(rest) <= 3:
            raise ValueError("one to three pieces")
        for r in rest:
            _piece(r)
            if r.startswith("/"):
                absolute, parts = _split(r)
            else:
                parts = parts + _split(r)[1]
        if a["how"] not in ("joinpath", "slash"):
            raise ValueError(a["how"])
        if not any(r in (".", "..") or r.startswith("/") for r in rest):
            raise ValueError("a piece that pathlib treats specially is the point")
        return _text(absolute, parts)
    p = a["p"]
    absolute, parts = _split(_clean(p))
    if want == "parts":
        shown = (["/"] if absolute else []) + parts
        if len(parts) < 2:
            raise ValueError("two pieces at least")
        return repr(tuple(shown))
    if want in ("stem", "suffixes", "with_suffix"):
        _file_path(p)
        name = parts[-1]
        if want == "stem":
            return NL.join([_stem_of(name), _suffix_of(name) or "none"])
        if want == "suffixes":
            return repr(_suffixes_of(name))
        new = a["suffix"]
        if not re.fullmatch(r"\.[a-z0-9]+", new):
            raise ValueError("a new suffix: a dot and letters")
        return _text(absolute, [*parts[:-1], _stem_of(name) + new])
    if want == "parent":
        up = _int(a["up"])
        if up < 1 or up + 1 >= len(parts) or len(parts) < 3:
            raise ValueError("a parents index that stays inside the path")
        return NL.join([_text(absolute, parts[:-1]), _text(absolute, parts[: -(up + 1)])])
    if want == "rel":
        b_abs, b_parts = _split(_clean(a["base"]))
        if b_abs == absolute and parts[: len(b_parts)] == b_parts:
            if len(b_parts) == len(parts) or not b_parts:
                raise ValueError("a base that is strictly inside the path")
            return _text(False, parts[len(b_parts):])
        return "outside"
    if want == "abs":
        return str(absolute)
    raise ValueError(want)


# ── 2. argparse ──────────────────────────────────────────────

_FLAG = re.compile(r"-[a-z]|--[a-z]+(-[a-z]+)*")


class _Quit(Exception):
    """argparse printed its usage and exited with 2."""


def _entries(spec) -> list[dict]:
    """The spec rows, each with the name argparse would give its value."""
    out, seen = [], set()
    for e in spec:
        e = dict(e)
        kind = e["kind"]
        if kind in ("option", "flag", "count"):
            flags = list(e["flags"])
            if not flags or any(not _FLAG.fullmatch(f) for f in flags):
                raise ValueError(f"{flags!r}: flags like -v and --verbose")
            long = [f for f in flags if f.startswith("--")]
            e["dest"] = (long[0] if long else flags[0]).lstrip("-").replace("-", "_")
        elif kind == "positional":
            e["dest"] = _word(e["name"])
        else:
            raise ValueError(kind)
        if e["dest"] in seen:
            raise ValueError("every value needs its own name")
        seen.add(e["dest"])
        out.append(e)
    return out


def _convert(e: dict, raw: str):
    kind = e.get("type")
    if kind == "int":
        if re.fullmatch(r"\d+", raw):
            value = int(raw)
        elif raw.isalpha():
            raise _Quit()
        else:
            raise ValueError("int() accepts odd things: keep to digits or letters")
    elif kind == "float":
        if not re.fullmatch(r"\d+\.[05]", raw):
            raise ValueError("halves only")
        value = float(raw)
    elif kind is None:
        _s(raw)
        value = raw
    else:
        raise ValueError(kind)
    if "choices" in e and value not in e["choices"]:
        raise _Quit()
    return value


def _argparse_model(spec, argv) -> dict:
    """The Namespace argparse would build, as a dict in its order."""
    ents = _entries(spec)
    ns: dict = {}
    for e in ents:
        kind = e["kind"]
        if kind == "option":
            ns[e["dest"]] = e.get("default")
        elif kind == "flag":
            ns[e["dest"]] = False
        elif kind == "count":
            ns[e["dest"]] = e.get("default")
        else:
            ns[e["dest"]] = None
    by_flag = {f: e for e in ents if e["kind"] != "positional" for f in e["flags"]}
    longs = [f for f in by_flag if f.startswith("--")]
    positional = [e for e in ents if e["kind"] == "positional"]
    if len(positional) > 1:
        raise ValueError("one positional at most")
    values: list[str] = []
    where: list[int] = []

    def apply(e: dict, raw: str | None) -> None:
        if e["kind"] == "flag":
            ns[e["dest"]] = True
        elif e["kind"] == "count":
            ns[e["dest"]] = (ns[e["dest"]] or 0) + 1
        else:
            ns[e["dest"]] = _convert(e, raw)

    argv = list(argv)
    i = 0
    while i < len(argv):
        tok = argv[i]
        if re.fullmatch(r"-\d.*", tok):
            raise ValueError("a leading dash and a digit is special to argparse")
        if tok.startswith("--"):
            name, eq, inline = tok.partition("=")
            if name not in by_flag:
                if any(f.startswith(name) for f in longs):
                    raise ValueError("an abbreviation: argparse would accept it")
                raise _Quit()
            e = by_flag[name]
            if e["kind"] == "option":
                if eq:
                    raw = inline
                else:
                    if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                        raise _Quit()
                    i += 1
                    raw = argv[i]
                apply(e, raw)
            elif eq:
                raise _Quit()
            else:
                apply(e, None)
        elif tok.startswith("-") and len(tok) > 1:
            if tok in by_flag and by_flag[tok]["kind"] == "option":
                if i + 1 >= len(argv) or argv[i + 1].startswith("-"):
                    raise _Quit()
                i += 1
                apply(by_flag[tok], argv[i])
            else:
                for ch in tok[1:]:
                    e = by_flag.get("-" + ch)
                    if e is None:
                        raise _Quit()
                    if e["kind"] == "option":
                        raise ValueError("a value stuck to a short option")
                    apply(e, None)
        else:
            values.append(tok)
            where.append(i)
        i += 1
    if where and where != list(range(where[0], where[0] + len(where))):
        raise ValueError("positionals split by options: argparse refuses the rest")
    if positional:
        e = positional[0]
        if e.get("many"):
            if not values:
                raise _Quit()
            ns[e["dest"]] = [_convert(e, v) for v in values]
        else:
            if len(values) != 1:
                raise _Quit()
            ns[e["dest"]] = _convert(e, values[0])
    elif values:
        raise _Quit()
    return ns


def _add_argument(e: dict) -> str:
    kind = e["kind"]
    if kind == "positional":
        extra = ""
        if e.get("many"):
            extra += ', nargs="+"'
        if e.get("type"):
            extra += f", type={e['type']}"
        return f"parser.add_argument({_s(_word(e['name']))}{extra})"
    flags = ", ".join(_s(f) for f in e["flags"])
    if kind == "flag":
        return f'parser.add_argument({flags}, action="store_true")'
    if kind == "count":
        default = f", default={_int(e['default'])}" if "default" in e else ""
        return f'parser.add_argument({flags}, action="count"{default})'
    extra = ""
    if e.get("type"):
        extra += f", type={e['type']}"
    if "choices" in e:
        extra += ", choices=[" + ", ".join(_s(c) for c in e["choices"]) + "]"
    if "default" in e:
        d = e["default"]
        extra += f", default={_int(d) if isinstance(d, int) else _s(d)}"
    return f"parser.add_argument({flags}{extra})"


def _args(a: dict) -> str:
    spec, argv, show = _entries(a["spec"]), list(a["argv"]), a["show"]
    for t in argv:
        _s(t)
    lines = ["import argparse", "", "parser = argparse.ArgumentParser()"]
    lines += [_add_argument(e) for e in spec]
    call = "parser.parse_args([" + ", ".join(_s(t) for t in argv) + "])"
    names = {e["dest"] for e in spec}
    if "error" in show:
        dest = show["error"]
        if dest not in names:
            raise ValueError(dest)
        lines += ["try:", f"    args = {call}", f'    print("ok", args.{dest})',
                  "except SystemExit as err:", '    print("exit", err.code)']
        return _fit(lines)
    lines.append(f"args = {call}")
    if "vars" in show:
        lines.append("print(vars(args))")
        return _fit(lines)
    dest = next(show[k] for k in ("attr", "sum", "join") if k in show)
    if dest not in names:
        raise ValueError(dest)
    if "attr" in show:
        op = {None: "", "next": " + 1", "double": " * 2"}[show.get("op")]
        lines.append(f"print(args.{dest}{op})")
    elif "sum" in show:
        lines.append(f"print(sum(args.{dest}))")
    else:
        lines.append(f'print(", ".join(args.{dest}))')
    return _fit(lines)


def _args_out(a: dict) -> str:
    spec, show = a["spec"], a["show"]
    try:
        ns = _argparse_model(spec, a["argv"])
    except _Quit:
        if "error" not in show:
            raise ValueError("this row quits, so it has to catch it") from None
        return "exit 2"
    if "error" in show:
        return f"ok {_say(ns[show['error']])}"
    if "vars" in show:
        if len(ns) < 2:
            raise ValueError("two values at least")
        return repr(ns)
    if "attr" in show:
        value = ns[show["attr"]]
        op = show.get("op")
        if op is None:
            return _say(value)
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("arithmetic on a number")
        return str(value + 1 if op == "next" else value * 2)
    if "sum" in show:
        values = ns[show["sum"]]
        total = values[0]
        for v in values[1:]:
            total = total + v
        if len(values) < 2:
            raise ValueError("two numbers at least")
        return str(total)
    values = ns[show["join"]]
    if len(values) < 2:
        raise ValueError("two names at least")
    return ", ".join(values)


# ── 3. Reading and writing files ─────────────────────────────


def _files(a: dict) -> str:
    want = a["want"]
    name = _name(a.get("file", "notes.txt"))
    enc = 'encoding="utf-8"'
    if want == "crlf":
        lines = list(a["lines"])
        data = _text_literal(lines, end=False, eol="\\r\\n")
        return _in_tmp([], [
            f"file.write_bytes(b{data})",
            f"print(len(file.read_text({enc}).splitlines()))",
            "print(file.stat().st_size)",
        ], file=name)
    if want in ("count", "last", "words", "longest", "sum", "find"):
        lines = list(a["lines"])
        write = f"file.write_text({_text_literal(lines)}, {enc})"
        text = f"file.read_text({enc})"
        if want == "words":
            return _in_tmp([], [write, f"print(len({text}.split()))"], file=name)
        read = f"lines = {text}.splitlines()"
        if want == "find":
            show = (f"print(next((i for i, line in enumerate(lines, start=1) "
                    f"if {_s(a['word'])} in line), 0))")
        else:
            show = {
                "count": "print(len(lines))",
                "last": "print(lines[-1])",
                "longest": "print(max(lines, key=len))",
                "sum": "print(sum(int(line) for line in lines))",
            }[want]
        return _in_tmp([], [write, read, show], file=name)
    name = _name(a.get("file", "out.txt"))
    if want == "append_count":
        more = list(a["more"])
        more_list = "[" + ", ".join(_s(m) for m in more) + "]"
        return _in_tmp([], [
            f"file.write_text({_text_literal([a['first']])}, {enc})",
            f'with file.open("a", {enc}) as handle:',
            f"    for line in {more_list}:",
            '        handle.write(line + "\\n")',
            f"print(len(file.read_text({enc}).splitlines()))",
        ], file=name)
    if want == "append_text":
        more = list(a["more"])
        more_list = "[" + ", ".join(_s(m) for m in more) + "]"
        return _in_tmp([], [
            f"file.write_text({_s(a['first'])}, {enc})",
            f"for piece in {more_list}:",
            f'    with file.open("a", {enc}) as handle:',
            "        handle.write(piece)",
            f"print(file.read_text({enc}))",
        ], file=name)
    if want == "overwrite":
        texts = "[" + ", ".join(_s(t) for t in a["texts"]) + "]"
        return _in_tmp([], [
            f"for text in {texts}:",
            f"    file.write_text(text, {enc})",
            f"print(file.read_text({enc}))",
        ], file=name)
    if want == "size":
        text = a["text"]
        if not isinstance(text, str) or not _UNI.fullmatch(text):
            raise ValueError(f"{text!r}: plain text, or a few accents")
        return _in_tmp([], [
            f'file.write_text("{text}", {enc})',
            "print(file.stat().st_size)",
        ], file=name)
    if want == "steps":
        body = []
        for step in a["steps"]:
            body.append({
                "check": "print(file.exists())",
                "write": f'file.write_text("data", {enc})',
                "delete": "file.unlink()",
            }[step])
        return _in_tmp([], body, file=name)
    if want == "rename":
        moved = _name(a["moved"])
        return _in_tmp([], [
            f"file.write_text({_s(a['text'])}, {enc})",
            f'moved = file.rename(file.with_name("{moved}"))',
            "print(file.exists())",
            f"print(moved.read_text({enc}))",
        ], file=name)
    raise ValueError(want)


def _files_out(a: dict) -> str:
    want = a["want"]
    if want == "crlf":
        lines = list(a["lines"])
        _text_literal(lines)
        if len(lines) < 3 or any(not x for x in lines):
            raise ValueError("three lines at least, none blank")
        size = sum(len(x) for x in lines) + 2 * (len(lines) - 1)
        return NL.join([str(len(lines)), str(size)])
    if want in ("count", "last", "words", "longest", "sum", "find"):
        lines = list(a["lines"])
        _text_literal(lines)
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
        word = a["word"]
        _s(word)
        hits = [i for i, x in enumerate(lines, start=1) if word in x]
        return str(hits[0] if hits else 0)
    if want == "append_count":
        more = list(a["more"])
        _text_literal([a["first"], *more])
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
        if not isinstance(text, str) or not _UNI.fullmatch(text):
            raise ValueError(f"{text!r}: plain text, or a few accents")
        return str(len(text.encode("utf-8")))
    if want == "steps":
        steps = list(a["steps"])
        exists, out = False, []
        for step in steps:
            if step == "check":
                out.append(str(exists))
            elif step == "write":
                exists = True
            elif step == "delete":
                if not exists:
                    raise ValueError("deleting a file that is not there raises")
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
        return NL.join(["False", a["text"]])
    raise ValueError(want)


# ── 4. JSON on disk ──────────────────────────────────────────


def _check_json(v) -> None:
    """Refuse what a hand-written JSON writer and the library would split on."""
    if v is None or isinstance(v, (bool, str)):
        if isinstance(v, str):
            _s(v)
            if not v.isascii():
                raise ValueError("ASCII text only")
        return
    if isinstance(v, int):
        if abs(v) >= 2**31:
            raise ValueError("a modest number")
        return
    if isinstance(v, list):
        for x in v:
            _check_json(x)
        return
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, str) or not _WORD.fullmatch(k):
                raise ValueError(f"{k!r}: a plain lowercase key")
            _check_json(x)
        return
    raise ValueError(f"{v!r}: no floats here")


def _dump(v, indent: int | None = None, sort: bool = False, level: int = 0) -> str:
    """json.dumps by hand: default separators, optional indent and sort."""
    _check_json(v)
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        if not v:
            return "[]"
        items = [_dump(x, indent, sort, level + 1) for x in v]
        if indent is None:
            return "[" + ", ".join(items) + "]"
        pad = " " * (indent * (level + 1))
        return "[\n" + ",\n".join(pad + i for i in items) + "\n" + " " * (indent * level) + "]"
    keys = sorted(v) if sort else list(v)
    if not keys:
        return "{}"
    items = [f'"{k}": ' + _dump(v[k], indent, sort, level + 1) for k in keys]
    if indent is None:
        return "{" + ", ".join(items) + "}"
    pad = " " * (indent * (level + 1))
    return "{\n" + ",\n".join(pad + i for i in items) + "\n" + " " * (indent * level) + "}"


class _Bad(ValueError):
    """Text a strict JSON reader refuses."""


def _parse(text: str):
    """A strict JSON reader: no trailing commas, double quotes only."""
    pos = 0

    def skip() -> None:
        nonlocal pos
        while pos < len(text) and text[pos] in " \t\n\r":
            pos += 1

    def literal(word: str, value):
        nonlocal pos
        if text.startswith(word, pos):
            pos += len(word)
            return value
        raise _Bad(word)

    def string() -> str:
        nonlocal pos
        if text[pos:pos + 1] != '"':
            raise _Bad("a string")
        end = text.find('"', pos + 1)
        if end < 0:
            raise _Bad("unterminated")
        out = text[pos + 1:end]
        if "\\" in out:
            raise ValueError("no escapes here")
        pos = end + 1
        return out

    def value():
        nonlocal pos
        skip()
        ch = text[pos:pos + 1]
        if ch == "{":
            pos += 1
            out: dict = {}
            skip()
            if text[pos:pos + 1] == "}":
                pos += 1
                return out
            while True:
                skip()
                key = string()
                skip()
                if text[pos:pos + 1] != ":":
                    raise _Bad(":")
                pos += 1
                if key in out:
                    raise ValueError("a repeated key")
                out[key] = value()
                skip()
                nxt = text[pos:pos + 1]
                pos += 1
                if nxt == "}":
                    return out
                if nxt != ",":
                    raise _Bad(", or }")
        if ch == "[":
            pos += 1
            items: list = []
            skip()
            if text[pos:pos + 1] == "]":
                pos += 1
                return items
            while True:
                items.append(value())
                skip()
                nxt = text[pos:pos + 1]
                pos += 1
                if nxt == "]":
                    return items
                if nxt != ",":
                    raise _Bad(", or ]")
        if ch == '"':
            return string()
        if text.startswith("true", pos):
            return literal("true", True)
        if text.startswith("false", pos):
            return literal("false", False)
        if text.startswith("null", pos):
            return literal("null", None)
        m = re.compile(r"-?(0|[1-9][0-9]*)").match(text, pos)
        if not m:
            raise _Bad("a value")
        pos = m.end()
        if text[pos:pos + 1] in (".", "e", "E"):
            raise ValueError("no floats here")
        return int(m.group())

    result = value()
    skip()
    if pos != len(text):
        raise _Bad("extra text")
    return result


def _item_list(items) -> list[tuple[str, int, int]]:
    items = [tuple(i) for i in items]
    if len(items) < 3 or len({n for n, _, _ in items}) != len(items):
        raise ValueError("three different items at least")
    for n, p, q in items:
        _s(n)
        if _int(p) < 0 or _int(q) < 1:
            raise ValueError("prices from zero, at least one of each")
    return items


def _json(a: dict) -> str:
    want = a["want"]
    name = _name(a.get("file", "data.json"))
    enc = 'encoding="utf-8"'
    if want == "safe":
        text = a["text"]
        if not re.fullmatch(r"[A-Za-z0-9 _.,:{}\[\]\"'-]+", text) or (
                "'" in text and '"' in text):
            raise ValueError(f"{text!r}: plain JSON-ish text, one kind of quote")
        return _fit([
            "import json", "", f"text = {text!r}", "try:",
            "    data = json.loads(text)", "except json.JSONDecodeError:",
            '    print("invalid")', "else:", "    print(json.dumps(data))",
        ])
    read = f"json.loads(file.read_text({enc}))"
    if want == "field":
        return _in_tmp(["json"], [
            f"file.write_text(json.dumps({_pyval(a['obj'])}), {enc})",
            f"data = {read}",
            f"print(data[{_s(_word(a['key']))}])",
        ], file=name)
    if want == "update":
        key = _s(_word(a["key"]))
        return _in_tmp(["json"], [
            f"file.write_text(json.dumps({_pyval(a['obj'])}), {enc})",
            f"data = {read}",
            f"data[{key}] += {_int(a['step'])}",
            f"file.write_text(json.dumps(data), {enc})",
            f"print(file.read_text({enc}))",
        ], file=name)
    if want in ("pretty", "sorted"):
        option = "indent=2" if want == "pretty" else "sort_keys=True"
        return _in_tmp(["json"], [
            f"settings = {_pyval(a['obj'])}",
            f"file.write_text(json.dumps(settings, {option}), {enc})",
            f"print(file.read_text({enc}))",
        ], file=name)
    if want in ("total", "names"):
        items = _item_list(a["items"])
        rows = "[" + ", ".join(
            f'{{"name": {_s(n)}, "price": {p}, "qty": {q}}}' for n, p, q in items) + "]"
        if want == "total":
            show = 'print(sum(item["price"] * item["qty"] for item in data))'
        else:
            show = (f'print(", ".join(item["name"] for item in data '
                    f'if item["price"] > {_int(a["limit"])}))')
        return _in_tmp(["json"], [
            f"file.write_text(json.dumps({rows}), {enc})",
            f"data = {read}",
            show,
        ], file=name)
    if want == "default":
        key = _word(a["key"])
        write = ([f"file.write_text(json.dumps({{{_s(key)}: {_s(a['saved'])}}}), {enc})"]
                 if a["saved"] is not None else [])
        return _in_tmp(["json"], [
            *write,
            f"config = {{{_s(key)}: {_s(a['default'])}}}",
            "if file.exists():",
            f"    config = {read}",
            f"print(config[{_s(key)}])",
        ], file=name)
    raise ValueError(want)


def _json_out(a: dict) -> str:
    want = a["want"]
    if want == "safe":
        text = a["text"]
        try:
            value = _parse(text)
        except _Bad:
            return "invalid"
        return _dump(value)
    if want in ("field", "update", "pretty", "sorted"):
        obj = dict(a["obj"])
        _check_json(obj)
        if not obj:
            raise ValueError("an object with something in it")
    if want == "field":
        key = a["key"]
        if key not in obj or isinstance(obj[key], (list, dict)):
            raise ValueError("a key that is there, with a single value")
        return _say(obj[key])
    if want == "update":
        key, step = a["key"], _int(a["step"])
        if not isinstance(obj.get(key), int) or isinstance(obj[key], bool) or not step:
            raise ValueError("a number to add to, and a step that does something")
        obj[key] = obj[key] + step
        return _dump(obj)
    if want == "pretty":
        if not any(isinstance(v, list) for v in obj.values()):
            raise ValueError("a list in the object, or indenting hardly shows")
        return _dump(obj, indent=2)
    if want == "sorted":
        if list(obj) == sorted(obj) or len(obj) < 3:
            raise ValueError("three keys, out of order")
        return _dump(obj, sort=True)
    if want in ("total", "names"):
        items = _item_list(a["items"])
        if want == "total":
            return str(sum(p * q for _, p, q in items))
        limit = _int(a["limit"])
        kept = [n for n, p, _ in items if p > limit]
        if not kept or len(kept) == len(items) or any(p == limit for _, p, _ in items):
            raise ValueError("a limit that keeps some, drops some and ties none")
        return ", ".join(kept)
    if want == "default":
        _word(a["key"])
        _s(a["default"])
        if a["saved"] is None:
            return a["default"]
        _s(a["saved"])
        if a["saved"] == a["default"]:
            raise ValueError("the saved value has to differ from the default")
        return a["saved"]
    raise ValueError(want)


# ── 5. Directories ───────────────────────────────────────────


def _make_names(names, count: int = 3) -> list[str]:
    names = _unique(_name(n) for n in names)
    if len(names) < count:
        raise ValueError(f"{count} names at least")
    return names


def _dir_path(p) -> list[str]:
    """A nested folder or file path made of lowercase pieces, no dots in folders."""
    if not isinstance(p, str):
        raise ValueError(f"{p!r}: a path")
    parts = p.split("/")
    for seg in parts[:-1]:
        if not _WORD.fullmatch(seg):
            raise ValueError(f"{seg!r}: a lowercase folder name")
    _name(parts[-1])
    return parts


def _dirs(a: dict) -> str:
    want = a["want"]
    enc = 'encoding="utf-8"'
    if want in ("list", "ext", "extcount", "delete"):
        names = "[" + ", ".join(_s(n) for n in a["names"]) + "]"
        body = ["root = Path(tmp)", f"names = {names}", "for name in names:",
                "    (root / name).touch()"]
        if want == "list":
            body.append('print(", ".join(sorted(p.name for p in root.iterdir())))')
        elif want in ("ext", "extcount"):
            body.append(f'found = sorted(p.name for p in root.glob("*.{_word(a["ext"])}"))')
            body.append('print(", ".join(found))' if want == "ext" else "print(len(found))")
        else:
            gone = "[" + ", ".join(_s(n) for n in a["gone"]) + "]"
            body.append(f"for name in {gone}:")
            body.append("    (root / name).unlink()")
            body.append('print(", ".join(sorted(p.name for p in root.iterdir())))')
        return _in_tmp([], body)
    if want == "size":
        files = ", ".join(f"{_s(n)}: {_s(t)}" for n, t in a["files"].items())
        return _in_tmp([], [
            "root = Path(tmp)", f"files = {{{files}}}",
            "for name, text in files.items():",
            f"    (root / name).write_text(text, {enc})",
            "print(sum(p.stat().st_size for p in root.iterdir()))",
        ])
    if want in ("dirs", "files"):
        folders = "[" + ", ".join(_s(n) for n in a["folders"]) + "]"
        plain = "[" + ", ".join(_s(n) for n in a["plain"]) + "]"
        test = "p.is_dir()" if want == "dirs" else "p.is_file()"
        return _in_tmp([], [
            "root = Path(tmp)",
            f"for name in {folders}:", "    (root / name).mkdir()",
            f"for name in {plain}:", "    (root / name).touch()",
            f'print(", ".join(sorted(p.name for p in root.iterdir() if {test})))',
        ])
    if want == "mkdir":
        target = " / ".join(_s(p) for p in a["path"])
        mode = a["mode"]
        if mode == "exists":
            return _in_tmp([], [
                f"target = Path(tmp) / {target}", "target.mkdir(parents=True)",
                "try:", "    target.mkdir(parents=True)",
                "except FileExistsError:", '    print("exists")',
            ])
        if mode == "exist_ok":
            return _in_tmp([], [
                f"target = Path(tmp) / {target}", "target.mkdir(parents=True)",
                "target.mkdir(parents=True, exist_ok=True)",
                "print(target.is_dir())",
                'print(", ".join(sorted(p.name for p in Path(tmp).rglob("*"))))',
            ])
        if mode == "noparents":
            return _in_tmp([], [
                f"target = Path(tmp) / {target}", "try:", "    target.mkdir()",
                "except FileNotFoundError:", '    print("no parent")',
                "target.mkdir(parents=True)", "print(target.is_dir())",
            ])
        raise ValueError(mode)
    if want in ("rglob_ext", "rglob_all", "rglob_files"):
        names = "[" + ", ".join(_s(n) for n in a["names"]) + "]"
        head = ["root = Path(tmp)", f"for name in {names}:", "    file = root / name",
                "    file.parent.mkdir(parents=True, exist_ok=True)", "    file.touch()"]
        rel = "p.relative_to(root).as_posix()"
        if want == "rglob_ext":
            show = (f'print(", ".join(sorted({rel} for p in '
                    f'root.rglob("*.{_word(a["ext"])}"))))')
        elif want == "rglob_all":
            show = f'print(", ".join(sorted({rel} for p in root.rglob("*"))))'
        else:
            show = 'print(sum(1 for p in root.rglob("*") if p.is_file()))'
        return _in_tmp([], [*head, show])
    raise ValueError(want)


def _dirs_out(a: dict) -> str:
    want = a["want"]
    if want == "list":
        names = _make_names(a["names"])
        if names == sorted(names):
            raise ValueError("already sorted, so sorting shows nothing")
        return ", ".join(sorted(names))
    if want in ("ext", "extcount"):
        names = _make_names(a["names"])
        ext = "." + _word(a["ext"])
        found = [n for n in names if n.endswith(ext)]
        if not found or len(found) == len(names):
            raise ValueError("an extension that keeps some and drops some")
        if want == "extcount":
            return str(len(found))
        if len(found) < 2:
            raise ValueError("two matches, or sorting shows nothing")
        return ", ".join(sorted(found))
    if want == "delete":
        names = _make_names(a["names"])
        gone = _unique(a["gone"], "removals")
        if not gone or any(g not in names for g in gone) or len(gone) >= len(names) - 1:
            raise ValueError("remove some of the names, but leave two or more")
        return ", ".join(sorted(n for n in names if n not in gone))
    if want == "size":
        files = dict(a["files"])
        _make_names(files)
        for text in files.values():
            _s(text)
            if not text.isascii():
                raise ValueError("ASCII text, so characters are bytes")
        return str(sum(len(t) for t in files.values()))
    if want in ("dirs", "files"):
        folders, plain = list(a["folders"]), list(a["plain"])
        for f in folders:
            _word(f)
        _unique([*folders, *plain])
        for n in plain:
            _name(n)
        if len(folders) < 2 or len(plain) < 2:
            raise ValueError("two folders and two files at least")
        return ", ".join(sorted(folders if want == "dirs" else plain))
    if want == "mkdir":
        path, mode = list(a["path"]), a["mode"]
        if len(path) < 2:
            raise ValueError("a nested path")
        for p in path:
            _word(p)
        _unique(path)
        if mode == "exists":
            return "exists"
        if mode == "exist_ok":
            return NL.join(["True", ", ".join(sorted(path))])
        if mode == "noparents":
            return NL.join(["no parent", "True"])
        raise ValueError(mode)
    if want in ("rglob_ext", "rglob_all", "rglob_files"):
        names = _unique(a["names"], "paths")
        files = [_dir_path(n) for n in names]
        if len(files) < 3 or not any(len(f) > 1 for f in files):
            raise ValueError("three paths at least, some of them inside folders")
        folders = {"/".join(f[:i]) for f in files for i in range(1, len(f))}
        every = sorted([*names, *folders])
        if want == "rglob_files":
            return str(len(names))
        if want == "rglob_all":
            return ", ".join(every)
        ext = "." + _word(a["ext"])
        found = [n for n in names if n.endswith(ext)]
        if len(found) < 2 or len(found) == len(names):
            raise ValueError("an extension that keeps some and drops some")
        return ", ".join(sorted(found))
    raise ValueError(want)


# ── 6. The csv module ────────────────────────────────────────


def _field(x, delim: str) -> str:
    """One field, written the way a csv writer minimally quotes it."""
    text = str(x)
    if not text:
        raise ValueError("no empty fields")
    if not isinstance(x, int) and not _PLAIN.fullmatch(text.replace('"', "")):
        raise ValueError(f"{text!r}: plain text, quotes allowed")
    if any(c in text for c in (delim, '"', "\n", "\r")):
        return '"' + text.replace('"', '""') + '"'
    return text


def _csv_rows(rows, delim: str = ",") -> list[list[str]]:
    rows = [list(r) for r in rows]
    if len(rows) < 3 or len({len(r) for r in rows}) != 1:
        raise ValueError("a header and two rows at least, all the same width")
    return rows


def _csv_text(rows, delim: str = ",") -> str:
    return "".join(delim.join(_field(f, delim) for f in r) + "\n" for r in rows)


def _csv_read(text: str, delim: str = ",") -> list[list[str]]:
    """A csv reader by hand: quoted fields, doubled quotes, line breaks."""
    rows, row, field, i, quoted = [], [], "", 0, False
    while i < len(text):
        ch = text[i]
        if quoted:
            if ch == '"':
                if text[i + 1:i + 2] == '"':
                    field += '"'
                    i += 1
                else:
                    quoted = False
            else:
                field += ch
        elif ch == '"' and not field:
            quoted = True
        elif ch == delim:
            row.append(field)
            field = ""
        elif ch == "\n":
            row.append(field)
            rows.append(row)
            row, field = [], ""
        else:
            field += ch
        i += 1
    if field or row:
        row.append(field)
        rows.append(row)
    return rows


_CSV_HEAD = ["import csv", "import io", ""]


def _lit(text: str) -> str:
    return repr(text)


def _cs(f) -> str:
    """A csv field as Python source: text may hold quotes, numbers do not."""
    if isinstance(f, bool) or not isinstance(f, (str, int)):
        raise ValueError(f"{f!r}: text or a whole number")
    _field(f, ",")
    return _q(f) if isinstance(f, str) else str(f)


def _csv(a: dict) -> str:
    want = a["want"]
    delim = a.get("delim", ",")
    if want in ("write", "dictwriter"):
        rows = [list(r) for r in a["rows"]]
        if want == "write":
            body = ", ".join("[" + ", ".join(_cs(f) for f in r) + "]" for r in rows)
            return _fit([
                *_CSV_HEAD[:2], "", "buffer = io.StringIO()",
                'writer = csv.writer(buffer, lineterminator="\\n")',
                f"writer.writerows([{body}])",
                'print(buffer.getvalue(), end="")',
            ])
        names = list(a["names"])
        fields = "[" + ", ".join(_s(n) for n in names) + "]"
        body = ", ".join("{" + ", ".join(
            f"{_s(n)}: {_cs(v)}" for n, v in zip(names, r)
        ) + "}" for r in rows)
        return _fit([
            *_CSV_HEAD[:2], "", "buffer = io.StringIO()",
            f'writer = csv.DictWriter(buffer, fieldnames={fields}, lineterminator="\\n")',
            "writer.writeheader()", f"writer.writerows([{body}])",
            'print(buffer.getvalue(), end="")',
        ])
    rows = _csv_rows(a["rows"], delim)
    text = _lit(_csv_text(rows, delim))
    opts = "" if delim == "," else f", delimiter={_s(delim)}"
    reader = f"csv.reader(io.StringIO(text){opts})"
    dicts = "csv.DictReader(io.StringIO(text))"
    head = [*_CSV_HEAD, f"text = {text}"]
    if want == "rows":
        return _fit([*head, f"rows = list({reader})", "print(len(rows) - 1)"])
    if want in ("delimiter", "quoted"):
        r, c = a["row"], a["col"]
        show = [f"print(rows[{r}][{c}])"]
        if want == "quoted":
            show = [f"print(len(rows[{r}]))", *show]
        return _fit([*head, f"rows = list({reader})", *show])
    if want == "dictreader":
        return _fit([*head, f"rows = list({dicts})",
                     f"print(rows[{a['row']}][{_s(a['col'])}])"])
    if want == "total":
        return _fit([*head, f'print(sum(int(row[{_s(a["col"])}]) for row in {dicts}))'])
    if want == "group":
        key, num = _s(a["key"]), _s(a["num"])
        return _fit([*head, "totals = {}", f"for row in {dicts}:",
                     f"    totals[row[{key}]] = totals.get(row[{key}], 0) + int(row[{num}])",
                     "for name in sorted(totals):", "    print(name, totals[name])"])
    raise ValueError(want)


def _csv_out(a: dict) -> str:
    want = a["want"]
    delim = a.get("delim", ",")
    if delim not in (",", ";", "|"):
        raise ValueError(delim)
    if want in ("write", "dictwriter"):
        rows = [list(r) for r in a["rows"]]
        if want == "dictwriter":
            names = list(a["names"])
            for n in names:
                _word(n)
            rows = [names, *rows]
        _csv_rows(rows)
        if not any(any(c in str(f) for c in ',"') for r in rows[1:] for f in r) \
                and want == "write":
            raise ValueError("a field that needs quotes, or quoting is not shown")
        return _csv_text(rows).rstrip("\n")
    rows = _csv_rows(a["rows"], delim)
    parsed = _csv_read(_csv_text(rows, delim), delim)
    if parsed != [[str(f) for f in r] for r in rows]:
        raise ValueError("the table does not survive being written and read")
    header, body = parsed[0], parsed[1:]
    if want == "rows":
        return str(len(body))
    if want in ("delimiter", "quoted"):
        r, c = a["row"], a["col"]
        out = [parsed[r][c]]
        if want == "quoted":
            if not any(("," in f or '"' in f) for f in parsed[r]):
                raise ValueError("a quoted field in that row")
            out = [str(len(parsed[r])), *out]
        elif delim == ",":
            raise ValueError("a delimiter that is not a comma")
        return NL.join(out)
    if want in ("dictreader", "total", "group"):
        if any("," in f or '"' in f for r in rows for f in r):
            raise ValueError("plain fields on the dictionary pages")
        records = [dict(zip(header, r)) for r in body]
    if want == "dictreader":
        row, col = a["row"], a["col"]
        if col not in header or not 0 <= row < len(records):
            raise ValueError("a row and a column that are there")
        return records[row][col]
    if want == "total":
        col = a["col"]
        if col not in header:
            raise ValueError("a column that is there")
        if any(not re.fullmatch(r"\d+", r[col]) for r in records):
            raise ValueError("whole numbers in the column")
        return str(sum(int(r[col]) for r in records))
    if want == "group":
        key, num = a["key"], a["num"]
        if key not in header or num not in header:
            raise ValueError("columns that are there")
        totals: dict[str, int] = {}
        for r in records:
            if not re.fullmatch(r"\d+", r[num]):
                raise ValueError("whole numbers in the column")
            totals[r[key]] = totals.get(r[key], 0) + int(r[num])
        if len(totals) == len(records):
            raise ValueError("a key that repeats, or grouping does nothing")
        return NL.join(f"{k} {totals[k]}" for k in sorted(totals))
    raise ValueError(want)


# ── 7. Logging ───────────────────────────────────────────────

_LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}
_FMT_TEXT = re.compile(r"[A-Za-z0-9 _.,:;/=@+!?#\[\]|<>%()\-]+")
_TOKEN = re.compile(r"%\((levelname|name|message|levelno)\)(-?\d*)([sd])")


def _fmt(x: str) -> str:
    """A log format: only the four fields this page knows."""
    if not isinstance(x, str) or not _FMT_TEXT.fullmatch(x):
        raise ValueError(f"{x!r}: a plain format")
    if "%" in _TOKEN.sub("", x):
        raise ValueError(f"{x!r}: only levelname, name, message and levelno")
    if "%(message)s" not in x:
        raise ValueError("the message has to be in the format")
    return x


def _level(x: str) -> str:
    """A configured level: UPPER case, as logging spells the constants."""
    if x not in _LEVELS:
        raise ValueError(f"{x!r}: a logging level")
    return x


def _call(x: str) -> str:
    """The level of one call, written the way its method is: lower case."""
    if x != x.lower() or x.upper() not in _LEVELS:
        raise ValueError(f"{x!r}: a logging method")
    return x.upper()


def _record(fmt: str, name: str | None, level: str, message: str) -> str:
    return fmt % {"levelname": level, "name": name or "root",
                  "message": message, "levelno": _LEVELS[level]}


def _message(template: str, values) -> str:
    """A message and its arguments, joined the way %-formatting does."""
    tokens = re.findall(r"%.", template)
    if any(t not in ("%d", "%s") for t in tokens) or len(tokens) != len(values):
        raise ValueError("one %d or %s for each argument")
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, str)):
            raise ValueError("numbers and text")
        if isinstance(v, str):
            _s(v)
    return template % tuple(values)


def _call_line(target: str, level: str, template: str, values=()) -> str:
    args = "".join(f", {_pyval(v)}" for v in values)
    return f"{target}.{level.lower()}({_s(template)}{args})"


def _log(a: dict) -> str:
    want = a["want"]
    head = ["import io", "import logging", "", "stream = io.StringIO()"]
    tail = 'print(stream.getvalue(), end="")'
    if want in ("emit", "count"):
        calls = list(a["calls"])
        cfg = (f"logging.basicConfig(stream=stream, format={_q(_fmt(a['fmt']))}, "
               f"level=logging.{_level(a['level'])})")
        body = []
        for name, level, message in calls:
            target = (f"logging.getLogger({_s(_log_name(name))})"
                      if name else "logging")
            body.append(_call_line(target, _call(level), message))
        show = tail if want == "emit" else "print(len(stream.getvalue().splitlines()))"
        return _fit([*head, cfg, *body, show])
    if want == "args":
        cfg = (f"logging.basicConfig(stream=stream, format={_q(_fmt(a['fmt']))}, "
               f"level=logging.{_level(a['level'])})")
        body = [_call_line("logging", _call(lv), t, v) for lv, t, v in a["calls"]]
        return _fit([*head, cfg, *body, tail])
    if want == "named":
        name = a["name"]
        body = [_call_line("log", _call(lv), m) for lv, m in a["calls"]]
        return _fit([
            *head, "handler = logging.StreamHandler(stream)",
            f"handler.setFormatter(logging.Formatter({_q(_fmt(a['fmt']))}))",
            f"log = logging.getLogger({_s(name)})", "log.addHandler(handler)",
            *body, tail,
        ])
    raise ValueError(want)


def _log_name(name) -> str | None:
    if name is None:
        return None
    if not re.fullmatch(r"[a-z]+(\.[a-z]+)*", name):
        raise ValueError(f"{name!r}: a dotted lowercase logger name")
    return name


def _log_out(a: dict) -> str:
    want = a["want"]
    if want in ("emit", "count"):
        fmt, threshold = _fmt(a["fmt"]), _LEVELS[_level(a["level"])]
        calls = list(a["calls"])
        if not 2 <= len(calls) <= 4:
            raise ValueError("two to four calls")
        shown = []
        for name, level, message in calls:
            _s(message)
            if _LEVELS[_call(level)] >= threshold:
                shown.append(_record(fmt, _log_name(name), _call(level), message))
        if not shown:
            raise ValueError("at least one record gets through")
        if want == "count":
            if len(shown) == len(calls):
                raise ValueError("a threshold that drops something")
            return str(len(shown))
        return NL.join(shown)
    if want == "args":
        fmt, threshold = _fmt(a["fmt"]), _LEVELS[_level(a["level"])]
        shown = []
        for level, template, values in a["calls"]:
            if _LEVELS[_call(level)] >= threshold:
                shown.append(_record(fmt, None, _call(level), _message(template, values)))
        if not shown:
            raise ValueError("at least one record gets through")
        return NL.join(shown)
    if want == "named":
        fmt, name = _fmt(a["fmt"]), _log_name(a["name"])
        if name is None:
            raise ValueError("a logger of its own")
        calls = list(a["calls"])
        if not 1 <= len(calls) <= 2:
            raise ValueError("one or two calls")
        # A new logger has no level of its own, so it takes the root's,
        # which is WARNING until someone says otherwise.
        shown = [_record(fmt, name, _call(lv), _message(m, ()))
                 for lv, m in calls if _LEVELS[_call(lv)] >= _LEVELS["WARNING"]]
        if not shown:
            raise ValueError("at least one record gets through")
        return NL.join(shown)
    raise ValueError(want)


# ── 8. Environment and exit codes ────────────────────────────


def _env_literal(env: dict) -> str:
    if not env:
        raise ValueError("an environment with something in it")
    parts = []
    for k, v in env.items():
        if not re.fullmatch(r"[A-Z][A-Z_]*", k):
            raise ValueError(f"{k!r}: environment names are UPPER_CASE")
        parts.append(f'"{k}": {_s(v) if v != "" else chr(34) * 2}')
    return "env = {" + ", ".join(parts) + "}"


_RULES = {
    "even": ("number % 2", "must be even"),
    "positive": ("number <= 0", "must be positive"),
    "small": ("number >= 100", "must be under 100"),
}

_SYS_EXIT = {"none": "", "zero": "0", "three": "3", "text": '"bad input"'}


def _env(a: dict) -> str:
    want = a["want"]
    if want in ("port", "flag", "mode", "list"):
        env = _env_literal(a["env"])
    if want == "port":
        return _fit([env, f'port = int(env.get("PORT") or {_int(a["default"])})', "print(port)"])
    if want == "flag":
        return _fit([env, f'enabled = env.get("{a["key"]}") == "true"', "print(enabled)"])
    if want == "mode":
        key = a["key"]
        return _fit([env, f'value = env.get("{key}") or {_s(a["default"])}',
                     f'print(f"{key} is {{value}}")'])
    if want == "list":
        return _fit([env, 'tags = env["TAGS"].split(",") if env.get("TAGS") else []',
                     "print(len(tags))", 'print(" | ".join(tags) or "none")'])
    if want == "exit":
        test, message = _RULES[a["rule"]]
        return _fit([
            f"number = {_int(a['input'])}", "code = 0", "try:",
            f"    if {test}:", f'        raise SystemExit("{message}")',
            '    print("ok", number)', "except SystemExit as err:",
            '    print("error:", err.code)', "    code = 1",
            'print("exit code", code)',
        ])
    if want == "sysexit":
        call = _SYS_EXIT[a["kind"]]
        return _fit(["import sys", "", "try:", f"    sys.exit({call})",
                     "except SystemExit as err:", "    print(err.code)"])
    if want == "child":
        code = a["code"]
        if not re.fullmatch(r"[A-Za-z0-9 _.,:;/=()'+*-]+", code) or '"' in code:
            raise ValueError(f"{code!r}: a one-line program")
        return _fit([
            "import subprocess", "import sys", "",
            f'result = subprocess.run([sys.executable, "-c", "{code}"], capture_output=True)',
            "print(result.returncode)",
        ])
    if want == "atexit":
        handlers = list(a["handlers"])
        regs = [f"atexit.register(print, {_s(h)})" for h in handlers]
        lines = [f"print({_s(x)})" for x in a["lines"]]
        return _fit(["import atexit", "", *regs, *lines])
    raise ValueError(want)


def _env_out(a: dict) -> str:
    want = a["want"]
    if want in ("port", "flag", "mode", "list"):
        env = dict(a["env"])
        _env_literal(env)
    if want == "port":
        default, text = _int(a["default"]), env.get("PORT", "")
        if text and not text.isdigit():
            raise ValueError("a PORT that is a whole number")
        if text == "0":
            raise ValueError("a PORT of 0 is an odd one")
        return str(int(text) if text else default)
    if want == "flag":
        if not re.fullmatch(r"[A-Z][A-Z_]*", a["key"]):
            raise ValueError("an UPPER_CASE name")
        return str(env.get(a["key"]) == "true")
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
        rule, n = a["rule"], _int(a["input"])
        if rule == "even":
            bad, message = n % 2 != 0, "must be even"
        elif rule == "positive":
            bad, message = n <= 0, "must be positive"
        elif rule == "small":
            bad, message = n >= 100, "must be under 100"
        else:
            raise ValueError(rule)
        if bad:
            return NL.join([f"error: {message}", "exit code 1"])
        return NL.join([f"ok {n}", "exit code 0"])
    if want == "sysexit":
        return {"none": "None", "zero": "0", "three": "3", "text": "bad input"}[a["kind"]]
    if want == "child":
        code = a["code"]
        if code == "pass":
            return "0"
        m = re.fullmatch(r"raise SystemExit\((\d+)\)", code) or re.fullmatch(
            r"import sys; sys\.exit\((\d+)\)", code)
        if m:
            n = int(m.group(1))
            if n > 255:
                raise ValueError("an exit code fits in a byte")
            return str(n)
        if re.fullmatch(r"raise SystemExit\('[a-z ]+'\)", code):
            return "1"  # a message goes to stderr and the code is 1
        if code in ("1 / 0", "int('x')"):
            return "1"  # an uncaught exception ends the run with 1
        raise ValueError(f"{code!r}: a program the model knows")
    if want == "atexit":
        lines, handlers = list(a["lines"]), list(a["handlers"])
        if len(lines) < 2 or not 1 <= len(handlers) <= 2:
            raise ValueError("two lines to print, one or two exit handlers")
        for x in [*lines, *handlers]:
            _s(x)
        # atexit runs the handler registered last, first.
        return NL.join([*lines, *reversed(handlers)])
    raise ValueError(want)


# ── 9. A small http.server ───────────────────────────────────

_URL = '"http://127.0.0.1:{server.server_port}'
_STATUSES = {200, 201, 202}
_HEADER_NAMES = {"X-Greeting", "X-Mood", "X-Team"}
_ROUTE = re.compile(r"/[A-Za-z0-9/?=&%+._-]*")


def _route(p: str) -> str:
    if not isinstance(p, str) or not _ROUTE.fullmatch(p):
        raise ValueError(f"{p!r}: a plain URL path")
    return p


def _unquote(text: str) -> str:
    """A query value, decoded: + is a space and %XX is a character."""
    text = text.replace("+", " ")
    return re.sub(r"%([0-9A-Fa-f]{2})", lambda m: chr(int(m.group(1), 16)), text)


def _query(path: str) -> tuple[str, dict[str, str]]:
    """A path split from its query string, by hand."""
    base, _, rest = path.partition("?")
    found: dict[str, str] = {}
    for pair in filter(None, rest.split("&")):
        key, _, value = pair.partition("=")
        if key in found:
            raise ValueError("a repeated parameter")
        found[_unquote(key)] = _unquote(value)
    return base, found


def _imports(extra) -> list[str]:
    """Plain imports first, then the from-imports, each in order."""
    plain = {"threading", "urllib.request"}
    froms = {"from http.server import BaseHTTPRequestHandler, HTTPServer"}
    for m in extra:
        (froms if m.startswith("from ") else plain).add(m)
    return [f"import {m}" for m in sorted(plain)] + sorted(froms)


def _server_program(extra, pre, handler, client) -> str:
    """Handler class, server in a daemon thread, a client, a shutdown."""
    lines = _imports(extra)
    lines += ["", *pre, "class Handler(BaseHTTPRequestHandler):"]
    lines += [f"    {h}" if h else h for h in handler]
    lines += [
        "", 'server = HTTPServer(("127.0.0.1", 0), Handler)',
        "threading.Thread(target=server.serve_forever, args=(0.01,), daemon=True).start()",
        *client, "server.shutdown()",
    ]
    return _fit(lines, SERVER_LIMIT)


def _reply(status: str, headers, body: str) -> list[str]:
    lines = [f"self.send_response({status})"]
    lines += [f"self.send_header({_s(k)}, {_s(v)})" for k, v in headers]
    lines += ["self.end_headers()", f"self.wfile.write({body})"]
    return lines


def _plain_client(path: str, show: list[str]) -> list[str]:
    return [f"with urllib.request.urlopen(f{_URL}{path}\") as reply:",
            *[f"    {s}" for s in show]]


def _checked_client(path: str) -> list[str]:
    return [f"url = f{_URL}{path}\"", "try:", "    reply = urllib.request.urlopen(url)",
            "except urllib.error.HTTPError as err:", "    reply = err",
            "print(reply.status, reply.read().decode())"]


_PARSE = "from urllib.parse import parse_qs, urlparse"
_URLPARSE = "from urllib.parse import urlparse"


def _http(a: dict) -> str:
    want = a["want"]
    if want == "body":
        status, text = _int(a["status"]), a["text"]
        return _server_program([], [], [
            "def do_GET(self):", *[f"    {x}" for x in _reply(str(status), [], f"b{_s(text)}")]],
            _plain_client("/", ["print(reply.status, reply.read().decode())"]))
    if want == "header":
        name, value, text = a["header"], a["value"], a["text"]
        return _server_program([], [], [
            "def do_GET(self):",
            *[f"    {x}" for x in _reply("200", [(name, value)], f"b{_s(text)}")]],
            _plain_client("/", [f"print(reply.headers[{_s(name)}], reply.read().decode())"]))
    if want == "json":
        key = _s(_word(a["key"]))
        return _server_program(["json"], [], [
            "def do_GET(self):",
            *[f"    {x}" for x in _reply(
                "200", [("Content-Type", "application/json")],
                f"json.dumps({_pyval(a['obj'])}).encode()")]],
            _plain_client("/", [f"print(json.load(reply)[{key}])"]))
    if want == "method":
        method, path = a["method"], _route(a["path"])
        handler = ["def do_" + method + "(self):",
                   *[f"    {x}" for x in _reply(
                       "200", [], 'f"{self.command} {self.path}".encode()')]]
        if method == "GET":
            return _server_program([], [], handler, _plain_client(
                path, ["print(reply.read().decode())"]))
        client = [f"request = urllib.request.Request(f{_URL}{path}\", "
                  f"method={_s(method)})",
                  "with urllib.request.urlopen(request) as reply:",
                  "    print(reply.read().decode())"]
        return _server_program([], [], handler, client)
    if want == "count":
        start, n = _int(a["start"]), _int(a["n"])
        handler = [f"hits = {start}", "", "def do_GET(self):", "    Handler.hits += 1",
                   *[f"    {x}" for x in _reply("200", [], "str(Handler.hits).encode()")]]
        client = [f"url = f{_URL}/\"", "seen = []", f"for _ in range({n}):",
                  "    with urllib.request.urlopen(url) as reply:",
                  "        seen.append(reply.read().decode())",
                  'print(", ".join(seen))']
        return _server_program([], [], handler, client)
    if want == "query":
        fallback, path = _s(a["fallback"]), _route(a["path"])
        handler = [
            "def do_GET(self):", "    parts = urlparse(self.path)",
            f'    name = parse_qs(parts.query).get("name", [{fallback}])[0]',
            '    found = parts.path == "/hello"',
            "    self.send_response(200 if found else 404)", "    self.end_headers()",
            '    self.wfile.write(f"Hello, {name}!".encode() if found else b"not found")',
        ]
        return _server_program(["urllib.error", _PARSE], [], handler, _checked_client(path))
    if want == "calc":
        x, y = _word(a["keys"][0]), _word(a["keys"][1])
        op = a["op"]
        if op not in ("+", "-", "*"):
            raise ValueError(op)
        path = _route(f"/calc?{x}={_int(a['x'])}&{y}={_int(a['y'])}")
        handler = [
            "def do_GET(self):", "    query = parse_qs(urlparse(self.path).query)",
            f'    result = int(query["{x}"][0]) {op} int(query["{y}"][0])',
            *[f"    {z}" for z in _reply(
                "200", [("Content-Type", "application/json")],
                'json.dumps({"result": result}).encode()')]]
        return _server_program(["json", _PARSE], [], handler, _plain_client(
            path, ['print(reply.headers["Content-Type"])',
                   'print(json.load(reply)["result"])']))
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        path = _route(a["path"])
        pre = [f"PAGES = {{{_s(p1)}: {_s(t1)}, {_s(p2)}: {_s(t2)}}}", ""]
        handler = [
            "def do_GET(self):", "    text = PAGES.get(urlparse(self.path).path)",
            "    self.send_response(200 if text else 404)", "    self.end_headers()",
            '    self.wfile.write((text or "not found").encode())',
        ]
        return _server_program(["urllib.error", _URLPARSE], pre, handler, _checked_client(path))
    if want == "post":
        field = _word(a["field"])
        reply = {
            "sum": f'str(sum(data["{field}"])).encode()',
            "max": f'str(max(data["{field}"])).encode()',
            "upper": f'data["{field}"].upper().encode()',
            "length": f'str(len(data["{field}"])).encode()',
        }[a["reply"]]
        handler = [
            "def do_POST(self):",
            '    size = int(self.headers["Content-Length"])',
            "    data = json.loads(self.rfile.read(size))",
            *[f"    {z}" for z in _reply("200", [], reply)],
        ]
        client = [
            f"body = json.dumps({{{_s(field)}: {_pyval(a['value'])}}}).encode()",
            f'request = urllib.request.Request(f{_URL}/", data=body, method="POST")',
            "with urllib.request.urlopen(request) as reply:",
            "    print(reply.read().decode())",
        ]
        return _server_program(["json"], [], handler, client)
    raise ValueError(want)


def _http_out(a: dict) -> str:
    want = a["want"]
    if want == "body":
        text = a["text"]
        _s(text)
        if a["status"] not in _STATUSES or text != text.strip() or not text.isascii():
            raise ValueError("a success status, and text with no spaces at the ends")
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
        _check_json(obj)
        value = obj[key]
        if isinstance(value, (list, dict)):
            raise ValueError("one value")
        return _say(value)
    if want == "method":
        method, path = a["method"], _route(a["path"])
        if method not in ("GET", "DELETE", "PUT", "PATCH"):
            raise ValueError(method)
        return f"{method} {path}"
    if want == "count":
        start, n = _int(a["start"]), a["n"]
        if not isinstance(n, int) or not 2 <= n <= 5 or start < 0:
            raise ValueError("two to five requests, counting up from zero or more")
        return ", ".join(str(start + i) for i in range(1, n + 1))
    if want == "query":
        _s(a["fallback"])
        base, found = _query(_route(a["path"]))
        if base != "/hello":
            return "404 not found"
        name = found.get("name", a["fallback"])
        if not name:
            raise ValueError("an empty name is a puzzle of its own")
        return f"200 Hello, {name}!"
    if want == "calc":
        if _word(a["keys"][0]) == _word(a["keys"][1]):
            raise ValueError("two different parameter names")
        x, y = _int(a["x"]), _int(a["y"])
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
        return NL.join(["application/json", str(value)])
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        for p in (p1, p2):
            _route(p)
            if "?" in p:
                raise ValueError("page paths have no query string")
        _s(t1)
        _s(t2)
        if p1 == p2 or t1 == t2:
            raise ValueError("two different pages")
        base, _ = _query(_route(a["path"]))
        table = {p1: t1, p2: t2}
        if base in table:
            return f"200 {table[base]}"
        return "404 not found"
    if want == "post":
        field, value = _word(a["field"]), a["value"]
        _check_json({field: value})
        reply = a["reply"]
        if reply in ("sum", "max"):
            if not isinstance(value, list) or len(value) < 2 or any(
                    not isinstance(x, int) or isinstance(x, bool) for x in value):
                raise ValueError("a list of two numbers at least")
            return str(sum(value) if reply == "sum" else max(value))
        if not isinstance(value, str) or not value.isascii():
            raise ValueError("plain text")
        if reply == "upper":
            return value.upper()
        if reply == "length":
            return str(len(value))
        raise ValueError(reply)
    raise ValueError(want)


# ── 10. asyncio ──────────────────────────────────────────────


def _secs(ms) -> str:
    """Milliseconds as the seconds the program writes."""
    if isinstance(ms, bool) or not isinstance(ms, int) or ms % 10 or not 10 <= ms <= 120:
        raise ValueError(f"{ms!r}: tens of milliseconds, 10 to 120")
    return str(ms / 1000)


def _jobs(jobs, minimum: int = 3, shuffled: bool = True) -> list[tuple[str, int]]:
    """Labels and delays in ms: apart enough that the order is certain."""
    jobs = [tuple(j) for j in jobs]
    if len(jobs) < minimum or len(jobs) > 4:
        raise ValueError(f"{minimum} to 4 jobs")
    _unique(label for label, _ in jobs)
    delays = sorted(ms for _, ms in jobs)
    if any(b - x < 20 for x, b in zip(delays, delays[1:])):
        raise ValueError("delays at least 20 ms apart, so the order is certain")
    for label, ms in jobs:
        _s(label)
        _secs(ms)
    if shuffled and [ms for _, ms in jobs] == delays:
        raise ValueError("jobs out of order, or the order proves nothing")
    return jobs


_JOB_PRINT = ["async def job(label, delay):", "    await asyncio.sleep(delay)", "    print(label)"]
_JOB_RETURN = ["async def job(label, delay):", "    await asyncio.sleep(delay)", "    return label"]


def _calls(jobs) -> str:
    return ", ".join(f"job({_s(label)}, {_secs(ms)})" for label, ms in jobs)


def _async(a: dict) -> str:
    want = a["want"]
    head = ["import asyncio", ""]
    if want == "order":
        return _fit([*head, *_JOB_PRINT, "", "async def main():",
                     f"    await asyncio.gather({_calls(a['jobs'])})", "",
                     "asyncio.run(main())"])
    if want == "results":
        return _fit([*head, *_JOB_RETURN, "", "async def main():",
                     f"    print(await asyncio.gather({_calls(a['jobs'])}))", "",
                     "asyncio.run(main())"])
    if want == "total":
        calls = ", ".join(f"job({n}, {_secs(ms)})" for n, ms in a["jobs"])
        return _fit([*head, "async def job(number, delay):",
                     "    await asyncio.sleep(delay)", "    return number * 2", "",
                     "async def main():",
                     f"    print(sum(await asyncio.gather({calls})))", "",
                     "asyncio.run(main())"])
    if want == "timeout":
        return _fit([
            *head, "async def main():", "    try:",
            f'        print(await asyncio.wait_for(asyncio.sleep({_secs(a["delay"])}, '
            f'{_s(a["word"])}), {_secs(a["limit"])}))',
            "    except TimeoutError:", '        print("timeout")', "",
            "asyncio.run(main())"])
    if want == "sequence":
        items = ", ".join(f"({_s(label)}, {_secs(ms)})" for label, ms in a["jobs"])
        return _fit([*head, *_JOB_PRINT, "", "async def main():",
                     f"    for label, delay in [{items}]:", "        await job(label, delay)",
                     "", "asyncio.run(main())"])
    if want == "tasks":
        jobs = _jobs(a["jobs"], minimum=2, shuffled=False)
        names = ["first", "second", "third", "fourth"][: len(jobs)]
        made = [f"    {n} = asyncio.create_task(asyncio.sleep({_secs(ms)}, {_s(label)}))"
                for n, (label, ms) in zip(names, jobs)]
        waited = ", ".join(f"await {n}" for n in names)
        return _fit([*head, "async def main():", *made,
                     f"    print({_s(a['sync'])})", f"    print({waited})", "",
                     "asyncio.run(main())"])
    if want == "completed":
        sleeps = ", ".join(f"asyncio.sleep({_secs(ms)}, {_s(label)})"
                           for label, ms in a["jobs"])
        return _fit([*head, "async def main():",
                     f"    for finished in asyncio.as_completed([{sleeps}]):",
                     "        print(await finished)", "", "asyncio.run(main())"])
    raise ValueError(want)


def _async_out(a: dict) -> str:
    want = a["want"]
    if want == "order":
        jobs = _jobs(a["jobs"])
        return NL.join(label for label, _ in sorted(jobs, key=lambda j: j[1]))
    if want == "results":
        jobs = _jobs(a["jobs"])
        return repr([label for label, _ in jobs])
    if want == "total":
        jobs = _jobs([(f"n{k}", ms) for k, (_, ms) in enumerate(a["jobs"])])
        return str(sum(_int(n) * 2 for n, _ in a["jobs"]) if jobs else 0)
    if want == "timeout":
        delay, limit = a["delay"], a["limit"]
        _secs(delay)
        _secs(limit)
        _s(a["word"])
        if abs(delay - limit) < 30:
            raise ValueError("a delay and a limit at least 30 ms apart")
        return a["word"] if delay < limit else "timeout"
    if want == "sequence":
        jobs = _jobs(a["jobs"])
        return NL.join(label for label, _ in jobs)
    if want == "tasks":
        jobs = _jobs(a["jobs"], minimum=2, shuffled=False)
        if len(jobs) > 3:
            raise ValueError("two or three tasks")
        sync = a["sync"]
        _s(sync)
        if sync in [label for label, _ in jobs]:
            raise ValueError("a sync line of its own")
        return NL.join([sync, " ".join(label for label, _ in jobs)])
    if want == "completed":
        jobs = _jobs(a["jobs"])
        return NL.join(label for label, _ in sorted(jobs, key=lambda j: j[1]))
    raise ValueError(want)


_BUILDERS = {
    "py_script_path": _path,
    "py_script_args": _args,
    "py_script_files": _files,
    "py_script_json": _json,
    "py_script_dirs": _dirs,
    "py_script_csv": _csv,
    "py_script_log": _log,
    "py_script_env": _env,
    "py_script_http": _http,
    "py_script_async": _async,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "py_script_path": _path_out,
    "py_script_args": _args_out,
    "py_script_files": _files_out,
    "py_script_json": _json_out,
    "py_script_dirs": _dirs_out,
    "py_script_csv": _csv_out,
    "py_script_log": _log_out,
    "py_script_env": _env_out,
    "py_script_http": _http_out,
    "py_script_async": _async_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "py_script_path": Cost(
        "O(n)",
        "Linear in the length of the path: pathlib splits the text at the "
        "slashes once, and parts, parent, stem and suffix are all read from "
        "that list of pieces. A path is a handful of characters, so it is "
        "never the slow part."),
    "py_script_args": Cost(
        "O(n)",
        "Linear in the number of arguments, n: argparse walks the list once, "
        "matching each string against the options it knows, and each lookup "
        "is a dictionary hit. Declaring the options costs a little more "
        "once, before parsing starts."),
    "py_script_files": Cost(
        "O(n)",
        "Linear in the size of the file: read_text reads all of it into "
        "memory, then splitlines, sum and max each pass over it once. A huge "
        "file would call for iterating the open file line by line, so memory "
        "stays flat. Appending costs only the new text; rewriting the whole "
        "file to add one line costs the whole file every time."),
    "py_script_json": Cost(
        "O(n)",
        "Linear in the size of the data: json.dumps and json.loads each "
        "visit every value once, and the file is read or written whole. "
        "Changing one field means loading and saving everything, which is "
        "fine for a settings file and a poor way to run a database."),
    "py_script_dirs": Cost(
        "O(n log n)",
        "n is the number of entries. Listing a folder and filtering it is "
        "one pass of n; the sort is about n log n comparisons, and it is "
        "needed because iterdir and glob promise no order. rglob visits "
        "every file below the folder, and each stat call is a trip to the "
        "file system."),
    "py_script_csv": Cost(
        "O(n)",
        "Linear in the size of the text: the reader looks at each character "
        "once to find the commas and the quotes, DictReader builds one "
        "dictionary per row, and the writer quotes each field as it goes. "
        "Grouping with a dictionary is still one pass, not one per key."),
    "py_script_log": Cost(
        "O(n)",
        "Linear in the number of log calls. Each call is a level check "
        "against a number, which is constant, and a record that gets "
        "through is formatted once for each handler that takes it. A call "
        "below the level costs almost nothing, so leaving debug calls in is "
        "cheap."),
    "py_script_env": Cost(
        "O(1)",
        "Constant: a dictionary lookup and a comparison, or one split of a "
        "short list. Raising and catching SystemExit costs a little more "
        "than an if, but still a fixed amount, however deep the call was, "
        "and atexit just keeps a short list of functions to call at the "
        "end."),
    "py_script_http": Cost(
        "O(n)",
        "Linear in the number of requests, n: the server does a fixed amount "
        "of work for each one, and the program waits for each answer in "
        "turn. The wait is network time, not computing. Port 0 lets the "
        "system pick a free port, and serve_forever(0.01) is what makes "
        "shutdown() return in ten milliseconds instead of waiting half a "
        "second."),
    "py_script_async": Cost(
        "O(n)",
        "Linear in the number of tasks, n, for the work of scheduling and "
        "collecting them. The clock is the surprise: gather runs the sleeps "
        "side by side, so the time taken is the longest delay, not the sum "
        "of them, where awaiting one after another takes the sum."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
