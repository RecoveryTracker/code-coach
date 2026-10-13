"""Pages 342-351: Python scripting and the standard library.

The standard library a script leans on once it leaves the exercises: pathlib
for paths, argparse for the command line, files and JSON on disk, folders,
csv, logging, the environment and exit codes, a small HTTP server that asks
itself a question, and asyncio. It is the Python counterpart of the Node
pages (238-247 in the JavaScript book), and like them the first half is the
file system and the process and the last two pages are the network and the
clock.

Everything runs as plain `python file.py` with no arguments and no network
beyond 127.0.0.1. sys.argv and os.environ cannot be passed in, so argparse is
handed a list and the environment pages use a dict. Files live in a
tempfile.TemporaryDirectory and no program prints a path. The path page uses
PurePosixPath, so Windows and Linux print the same.

Reading files and writing files share a page (the list asked for ten, and
the two are one idea: bytes in a file, in and out), so the set is ten pages
for eleven topics.

Python only, numbered after page 341, the last of the Python book before the
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


#: Where a file program does its work.
_TMP = "a temporary folder made with tempfile.TemporaryDirectory"


def _say(v) -> str:
    return str(v)


def _describe(obj: dict) -> str:
    parts = []
    for k, v in obj.items():
        if isinstance(v, list):
            parts.append(f"{k} as the list {_and(_say(x) for x in v)}")
        else:
            parts.append(f"{k} {_say(v)}")
    return _and(parts)


# ── 342. pathlib ─────────────────────────────────────────────

_PATHS = (
    ("parts", {"p": "/srv/app/logs/today.txt"}),
    ("parts", {"p": "src/app/main.py"}),
    ("parts", {"p": "/home/ada/music/albums"}),
    ("stem", {"p": "/home/ada/notes.txt"}),
    ("stem", {"p": "/srv/backups/archive.tar.gz"}),
    ("stem", {"p": "/etc/.bashrc"}),
    ("suffixes", {"p": "/srv/data/archive.tar.gz"}),
    ("suffixes", {"p": "/srv/app/Makefile"}),
    ("with_suffix", {"p": "/home/ada/notes.txt", "suffix": ".md"}),
    ("with_suffix", {"p": "/srv/data/archive.tar.gz", "suffix": ".zip"}),
    ("with_suffix", {"p": "/srv/app/Makefile", "suffix": ".bak"}),
    ("parent", {"p": "/home/ada/projects/app/main.py", "up": 2}),
    ("parent", {"p": "docs/guide/en/intro.md", "up": 1}),
    ("join", {"base": "/srv/app", "rest": ["..", "logs", "today.txt"], "how": "joinpath"}),
    ("join", {"base": "assets", "rest": ["img", ".", "logo.png"], "how": "slash"}),
    ("join", {"base": "/home/ada", "rest": ["/etc", "hosts"], "how": "joinpath"}),
    ("rel", {"p": "/srv/app/logs/today.txt", "base": "/srv/app"}),
    ("rel", {"p": "/srv/app/logs/today.txt", "base": "/etc"}),
    ("abs", {"p": "/usr/local/bin"}),
    ("abs", {"p": "src/index.py"}),
)


def _path_row(row):
    want, a = row
    args = {"want": want, **a}
    p = a.get("p")
    if want == "parts":
        return (f"Make a PurePosixPath from the text {p} and print its parts.", args)
    if want == "stem":
        return (f"Make a PurePosixPath from the text {p}. Print its stem, then "
                f"its suffix, or the word none when it has no suffix.", args)
    if want == "suffixes":
        return (f"Make a PurePosixPath from the text {p} and print the list of "
                f"all its suffixes.", args)
    if want == "with_suffix":
        return (f"Make a PurePosixPath from the text {p} and print the path you "
                f"get by changing its suffix to {a['suffix']}.", args)
    if want == "parent":
        return (f"Make a PurePosixPath from the text {p}. Print its parent, then "
                f"the entry of its parents sequence with index {a['up']}.", args)
    if want == "join":
        pieces = _quoted(a["rest"])
        how = ("with its joinpath method" if a["how"] == "joinpath"
               else "one at a time with the / operator")
        return (f"Start from the PurePosixPath {a['base']}, add the pieces "
                f"{pieces} to it {how}, and print the result.", args)
    if want == "rel":
        return (f"Make a PurePosixPath from the text {p}. Print the path "
                f"relative to {a['base']}, or the word outside when it is not "
                f"under {a['base']}.", args)
    return (f"Print whether the PurePosixPath made from the text {p} is "
            f"absolute.", args)


PATH_PAGE = _page(
    "py-script-path", 342, "Scripting: pathlib paths",
    "pathlib turns a path from a string into an object that knows its own "
    "parts. PurePosixPath always uses slashes, so these exercises print the "
    "same on Windows and Linux (Path picks the right one for the machine). "
    "path.parts is a tuple with the root as its own first piece, path.name "
    "the last piece, path.suffix the extension with its dot (the last one "
    "only: archive.tar.gz has .gz, and path.suffixes lists them all), "
    "path.stem the name without it, and a name that only starts with a dot, "
    "such as .bashrc, has no suffix. with_suffix swaps the extension, "
    "parent is the folder above and parents[n] the ones further up. "
    "joinpath and the / operator add pieces, and they do not tidy: '..' "
    "stays where you put it, a lone '.' disappears, and a piece that starts "
    "with a slash throws away everything before it. relative_to takes a "
    "prefix off, and raises ValueError when the path is not under it.",
    "from pathlib import PurePosixPath; path = PurePosixPath('/srv/app/"
    "notes.txt') gives path.name notes.txt, path.stem notes, path.suffix "
    ".txt, path.parent /srv/app and path.with_suffix('.md') /srv/app/"
    "notes.md; PurePosixPath('/srv') / 'app' / '..' is /srv/app/..",
    "py_script_path",
    tuple(_path_row(row) for row in _PATHS),
)


# ── 343. Command-line arguments ──────────────────────────────


def _opt(flags, *, default=None, type=None, choices=None) -> dict:
    e = {"kind": "option", "flags": list(flags)}
    if default is not None:
        e["default"] = default
    if type:
        e["type"] = type
    if choices:
        e["choices"] = list(choices)
    return e


def _flag(*flags) -> dict:
    return {"kind": "flag", "flags": list(flags)}


def _count(*flags, default=None) -> dict:
    e = {"kind": "count", "flags": list(flags)}
    if default is not None:
        e["default"] = default
    return e


def _pos(name, *, many=False, type=None) -> dict:
    e = {"kind": "positional", "name": name}
    if many:
        e["many"] = True
    if type:
        e["type"] = type
    return e


def _dest(e: dict) -> str:
    if e["kind"] == "positional":
        return e["name"]
    long = [f for f in e["flags"] if f.startswith("--")]
    return (long[0] if long else e["flags"][0]).lstrip("-").replace("-", "_")


def _spec_text(e: dict) -> str:
    kind = e["kind"]
    if kind == "positional":
        text = f"a positional argument {e['name']}"
        if e.get("many"):
            text += " that takes one or more values"
        if e.get("type"):
            what = "whole numbers" if e["type"] == "int" else "decimal numbers"
            text += f", read as {what}"
        return text
    flags = " or ".join(e["flags"])
    if kind == "flag":
        return f"a flag {flags} that is true when given and false when not"
    if kind == "count":
        default = f"default {e['default']}" if "default" in e else "no default"
        return f"a counting flag {flags} that adds one each time it appears ({default})"
    text = f"an option {flags}"
    if e.get("type"):
        text += " that reads a whole number"
    if "choices" in e:
        text += f" that only allows the choices {_and(e['choices'])}"
    if "default" in e:
        text += f" (default {e['default']})"
    return text


def _show_text(show: dict) -> str:
    if "attr" in show:
        tail = {None: "", "next": " plus one", "double": " doubled"}[show.get("op")]
        return f"print the value of {show['attr']}{tail}"
    if "vars" in show:
        return "print everything it parsed as a dictionary, with vars"
    if "sum" in show:
        return f"print the sum of {show['sum']}"
    if "join" in show:
        return f"print {show['join']} joined by a comma and a space"
    return ""


def _args_row(row):
    spec, argv, show = row
    args = {"want": next(iter(show)) if "error" not in show else "error",
            "spec": spec, "argv": argv, "show": show}
    listing = "[" + ", ".join(f"'{x}'" for x in argv) + "]"
    built = (f"Build an argument parser with {_and(_spec_text(e) for e in spec)}, "
             f"added in that order.")
    if "error" in show:
        dest = show["error"]
        return (f"{built} Parse the list {listing} inside a try block. If the "
                f"parser quits, catch the SystemExit and print the word exit, a "
                f"space and its code; otherwise print the word ok, a space and "
                f"the value of {dest}.", args)
    return f"{built} Parse the list {listing} and {_show_text(show)}.", args


_VERBOSE = ("-v", "--verbose")

_ARGS = (
    ([_opt(["--name"], default="Guest"), _flag(*_VERBOSE)],
     ["--name", "Ada", "-v"], {"attr": "name"}),
    ([_opt(["--out"], default="dist"), _flag(*_VERBOSE)],
     ["-v"], {"attr": "out"}),
    ([_opt(["--user"], default="anon"), _flag("-q", "--quiet")],
     ["--quiet", "--user=grace"], {"attr": "user"}),
    ([_flag(*_VERBOSE)], ["-v"], {"attr": "verbose"}),
    ([_flag(*_VERBOSE), _opt(["--name"], default="Guest")],
     ["--name", "Ada"], {"attr": "verbose"}),
    ([_opt(["--port"], default=3000, type="int")],
     ["--port", "8080"], {"attr": "port", "op": "next"}),
    ([_opt(["--port"], default=3000, type="int"), _flag(*_VERBOSE)],
     ["-v"], {"attr": "port", "op": "double"}),
    ([_opt(["--retries"], default=1, type="int"), _flag(*_VERBOSE)],
     ["--retries=4", "-v"], {"attr": "retries", "op": "double"}),
    ([_flag(*_VERBOSE), _pos("files", many=True)],
     ["-v", "a.txt", "b.txt"], {"join": "files"}),
    ([_pos("command"), _flag("-f", "--force")],
     ["copy", "--force"], {"attr": "command"}),
    ([_count(*_VERBOSE, default=0)], ["-vvv"], {"attr": "verbose"}),
    ([_count(*_VERBOSE)], [], {"attr": "verbose"}),
    ([_opt(["--name"], default="Guest"), _flag("--dry-run")],
     ["--dry-run"], {"vars": True}),
    ([_pos("files", many=True), _opt(["--out"], default="dist"), _flag("-q", "--quiet")],
     ["a.txt", "b.txt", "--out", "build"], {"vars": True}),
    ([_pos("numbers", many=True, type="int")],
     ["4", "10", "3"], {"sum": "numbers"}),
    ([_pos("numbers", many=True, type="float")],
     ["2.5", "0.5", "7.0"], {"sum": "numbers"}),
    ([_opt(["--mode"], default="fast", choices=["fast", "slow"]), _flag(*_VERBOSE)],
     ["--mode", "slow"], {"error": "mode"}),
    ([_opt(["--mode"], default="fast", choices=["fast", "slow"])],
     ["--mode", "medium"], {"error": "mode"}),
    ([_opt(["--port"], default=3000, type="int")],
     ["--port", "abc"], {"error": "port"}),
    ([_pos("command")], [], {"error": "command"}),
)

ARGS_PAGE = _page(
    "py-script-args", 343, "Scripting: command-line arguments",
    "argparse reads the command line for you. ArgumentParser() makes a "
    "parser, add_argument describes each thing it should accept, and "
    "parse_args(list) reads a list of strings and returns an object with one "
    "attribute for each. A script reads sys.argv[1:] when you call "
    "parse_args() with nothing, so passing a list is how you try it out. "
    "An option takes a value (--name Ada or --name=Ada) and has a default "
    "for when it is missing, type=int turns the text into a number, and "
    "choices limits what is allowed. action='store_true' makes a flag, "
    "false until it appears, and action='count' adds one each time, so -vvv "
    "is 3 (with no default it starts as None, not 0). A name with no dashes "
    "is a positional argument, and nargs='+' takes one or more. The attribute "
    "is the long name with dashes turned to underscores, so --dry-run is "
    "dry_run, and vars(args) shows them all, in the order they were added. "
    "When the arguments are wrong the parser prints a usage message and "
    "raises SystemExit with the code 2, which try/except SystemExit can "
    "catch.",
    "import argparse; parser = argparse.ArgumentParser(); parser.add_argument("
    "'--name', default='Guest'); args = parser.parse_args(['--name', 'Ada']) "
    "gives args.name Ada, and parse_args([]) gives Guest",
    "py_script_args",
    tuple(_args_row(row) for row in _ARGS),
)


# ── 344. Reading and writing files ───────────────────────────

_FILES = (
    ("count", {"file": "fruit.txt", "lines": ["apple", "banana", "cherry"]}),
    ("count", {"file": "colours.txt", "lines": ["red", "green", "blue", "yellow"]}),
    ("last", {"file": "days.txt", "lines": ["Monday", "Tuesday", "Wednesday"]}),
    ("words", {"file": "poem.txt", "lines": ["the quick brown fox", "jumps over", "the lazy dog"]}),
    ("longest", {"file": "pets.txt", "lines": ["cat", "elephant", "dog"]}),
    ("longest", {"file": "paint.txt", "lines": ["red", "orange", "blue", "green"]}),
    ("sum", {"file": "numbers.txt", "lines": ["5", "10", "-3"]}),
    ("sum", {"file": "scores.txt", "lines": ["100", "250", "75", "25"]}),
    ("find", {"file": "shop.txt", "lines": ["red apple", "green pear", "yellow banana"], "word": "pear"}),
    ("find", {"file": "stock.txt", "lines": ["red apple", "green pear", "yellow banana"], "word": "plum"}),
    ("crlf", {"file": "windows.txt", "lines": ["one", "two", "three"]}),
    ("append_count", {"first": "one", "more": ["two", "three"]}),
    ("append_text", {"first": "Hello", "more": [", ", "world"]}),
    ("append_text", {"first": "2024", "more": ["-10", "-05"]}),
    ("overwrite", {"texts": ["version one", "version two"]}),
    ("overwrite", {"texts": ["red", "green", "blue"]}),
    ("size", {"text": "hello world"}),
    ("size", {"text": "café"}),
    ("size", {"text": "日本"}),
    ("steps", {"steps": ["check", "write", "check"]}),
    ("steps", {"steps": ["write", "check", "delete", "check"]}),
    ("rename", {"file": "draft.txt", "moved": "final.txt", "text": "hello"}),
)

_STEP_WORDS = {
    "check": "print whether it exists",
    "write": "write the text data to it",
    "delete": "delete it",
}


def _files_row(row):
    want, a = row
    args = {"want": want, **a}
    if want in ("count", "last", "words", "longest", "sum", "find"):
        file, lines = a["file"], a["lines"]
        put = (f"Write the lines {_and(lines)} to the text file {file} in {_TMP}, "
               f"one per line, then read the file back")
        if want == "count":
            return f"{put} and print how many lines it has.", args
        if want == "last":
            return f"{put} and print its last line.", args
        if want == "words":
            return (f"{put} and print how many words it holds in all, counting "
                    f"every run of spaces and line breaks as a gap between "
                    f"words.", args)
        if want == "longest":
            return f"{put} and print its longest line.", args
        if want == "sum":
            return (f"{put}, turn each line into a whole number, and print the "
                    f"sum of them.", args)
        return (f"{put} and print the number of the first line that contains "
                f"the text {a['word']}, counting from 1, or 0 when no line "
                f"does.", args)
    if want == "crlf":
        return (f"Write the lines {_and(a['lines'])} to the file {a['file']} in "
                f"{_TMP}, as raw bytes with Windows line endings (a carriage "
                f"return then a newline after every line except the last). Read "
                f"the file back as text and print how many lines it has, then "
                f"print the size of the file in bytes.", args)
    if want == "append_count":
        more = a["more"]
        return (f"In {_TMP}, write the line {a['first']} to a file, then add "
                f"the lines {_and(more)} to the end of it by opening it in "
                f"append mode, one at a time, and print how many lines the "
                f"file has.", args)
    if want == "append_text":
        pieces = _and(f"'{m}'" for m in a["more"])
        return (f"In {_TMP}, write the text '{a['first']}' to a file, then "
                f"append {pieces} to it one at a time, adding no newlines, and "
                f"print the whole text of the file.", args)
    if want == "overwrite":
        texts = a["texts"]
        again = _then(f"'{t}'" for t in texts[1:])
        return (f"In {_TMP}, write the text '{texts[0]}' to a file, then write "
                f"{again} to the same file with write_text each time, and "
                f"print what the file holds at the end.", args)
    if want == "size":
        return (f"In {_TMP}, write the text '{a['text']}' to a file as UTF-8, "
                f"then print the file's size in bytes.", args)
    if want == "steps":
        todo = _then(_STEP_WORDS[s] for s in a["steps"])
        return (f"In {_TMP}, take a file path inside it, and with nothing "
                f"written yet: {todo}.", args)
    return (f"In {_TMP}, write the text '{a['text']}' to the file {a['file']}, "
            f"rename the file to {a['moved']}, then print whether "
            f"{a['file']} still exists, then the text of {a['moved']}.", args)


FILES_PAGE = _page(
    "py-script-files", 344, "Scripting: reading and writing files",
    "Path.write_text(text) creates the file or replaces whatever was there, "
    "so writing twice leaves only the second text, and Path.read_text() "
    "gives the whole file back as a string. Pass encoding='utf-8' every "
    "time: without it Python uses the machine's own default, which is not "
    "the same on Windows and Linux, and a file's size in bytes is not its "
    "number of characters (é takes two bytes, 日 three). text.splitlines() "
    "cuts a file into lines without the line breaks, and unlike split('\\n') "
    "it copes with Windows line endings (\\r\\n) and leaves no empty piece "
    "after a final newline; text.split() with no argument cuts on every run "
    "of spaces and breaks, which is how to count words. Path has no append "
    "method: open it with file.open('a') and write to the handle, which adds "
    "to the end and makes the file if it is missing, but adds exactly what "
    "you give it, so a line needs its own '\\n'. file.exists() answers True "
    "or False, file.unlink() deletes (and raises FileNotFoundError when it is "
    "not there), file.rename(new) moves it and file.stat().st_size is the "
    "size in bytes. Every program here works inside tempfile."
    "TemporaryDirectory(), which makes an empty folder and deletes it again "
    "when the with block ends, so nothing is left lying about. Never print "
    "its path: it is different every time.",
    "with tempfile.TemporaryDirectory() as tmp: file = Path(tmp) / 'a.txt'; "
    "file.write_text('apple\\nbanana\\n', encoding='utf-8'); then "
    "file.read_text(encoding='utf-8').splitlines() is ['apple', 'banana'] "
    "and file.stat().st_size is 13 on any machine",
    "py_script_files",
    tuple(_files_row(row) for row in _FILES),
)


# ── 345. JSON on disk ────────────────────────────────────────

_ITEMS_A = [("pen", 3, 4), ("ink", 8, 2), ("pad", 5, 3)]
_ITEMS_B = [("bolt", 2, 50), ("nut", 1, 80), ("washer", 1, 30)]
_ITEMS_C = [("pen", 3, 4), ("ink", 8, 2), ("pad", 5, 3), ("lamp", 20, 1)]
_ITEMS_D = [("tea", 2, 10), ("cake", 6, 1), ("jam", 4, 2)]

_JSONS = (
    ("field", {"obj": {"name": "Ada", "age": 36}, "key": "age"}),
    ("field", {"obj": {"title": "Dune", "year": 1965, "read": True}, "key": "read"}),
    ("field", {"obj": {"city": "Oslo", "pop": 709000}, "key": "city"}),
    ("update", {"obj": {"count": 5}, "key": "count", "step": 3}),
    ("update", {"obj": {"name": "Ada", "score": 10}, "key": "score", "step": 5}),
    ("pretty", {"obj": {"name": "Ada", "langs": ["js", "py"]}}),
    ("pretty", {"obj": {"id": 7, "tags": ["a", "b", "c"], "ok": True}}),
    ("sorted", {"obj": {"name": "Ada", "age": 36, "city": "Oslo"}}),
    ("sorted", {"obj": {"zebra": 1, "apple": 2, "mango": 3}}),
    ("total", {"items": _ITEMS_A}),
    ("total", {"items": _ITEMS_B}),
    ("names", {"items": _ITEMS_C, "limit": 4}),
    ("names", {"items": _ITEMS_D, "limit": 3}),
    ("default", {"key": "theme", "default": "light", "saved": None}),
    ("default", {"key": "theme", "default": "light", "saved": "dark"}),
    ("default", {"key": "lang", "default": "en", "saved": "fr"}),
    ("safe", {"text": '{ "a": 1, "b": [true, null] }'}),
    ("safe", {"text": '{"a":1,}'}),
    ("safe", {"text": "[1, 2, 3]"}),
    ("safe", {"text": '{name: "Ada"}'}),
)


def _json_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "field":
        return (f"In {_TMP}, save a dictionary with {_describe(a['obj'])} to a "
                f"JSON file, load it back, and print its {a['key']}.", args)
    if want == "update":
        return (f"In {_TMP}, save a dictionary with {_describe(a['obj'])} to a "
                f"JSON file. Load it, add {a['step']} to its {a['key']}, save "
                f"it again, and print the text of the file.", args)
    if want == "pretty":
        return (f"In {_TMP}, save a dictionary with {_describe(a['obj'])} to a "
                f"JSON file indented with two spaces, and print the text of "
                f"the file.", args)
    if want == "sorted":
        return (f"In {_TMP}, save a dictionary with {_describe(a['obj'])} to a "
                f"JSON file with its keys sorted, and print the text of the "
                f"file.", args)
    if want in ("total", "names"):
        things = _and(f"{n} at {p} each, {q} of them" for n, p, q in a["items"])
        base = (f"In {_TMP}, save a list of dictionaries, each with a name, a "
                f"price and a qty: {things}, to a JSON file, and load it back.")
        if want == "total":
            return f"{base} Print the total cost, the sum of price times qty.", args
        return (f"{base} Print the names of the items that cost more than "
                f"{a['limit']}, in order, joined by a comma and a space.", args)
    if want == "default":
        key, d, s = a["key"], a["default"], a["saved"]
        have = (f"First save a dictionary with {key} {s} to a JSON file named "
                f"settings.json. " if s is not None else
                "No settings.json file has been written. ")
        return (f"In {_TMP}, start with the settings dictionary with {key} {d}. "
                f"{have}If settings.json exists, load it in place of the "
                f"defaults. Print the {key}.", args)
    return (f"Parse the text {a['text']} as JSON inside a try block. When it "
            f"parses, print the data written back out as JSON text; when "
            f"parsing raises a JSONDecodeError, print the word invalid.", args)


JSON_PAGE = _page(
    "py-script-json", 345, "Scripting: JSON on disk",
    "A file only holds text, so a dictionary has to be turned into text to "
    "be saved: json.dumps(data) makes the text, json.loads(text) turns it "
    "back into data, and with write_text and read_text that is a save file "
    "in two lines. To change one field, load the file, change the "
    "dictionary, then write the whole thing back. json.dumps writes "
    "separators with a space after each comma and colon ({\"a\": 1, \"b\": "
    "2}, where JavaScript gives {\"a\":1,\"b\":2}), indent=2 puts each item "
    "on its own line indented two spaces, and sort_keys=True orders the keys "
    "alphabetically. Python's True, False and None come out as true, false "
    "and null. JSON is strict, much stricter than a Python dictionary: keys "
    "need double quotes, strings cannot use single quotes and nothing may end "
    "with a trailing comma. json.loads raises json.JSONDecodeError on a bad "
    "text, so wrap it in try/except when the text came from outside. "
    "file.exists() lets a program fall back to defaults the first time it "
    "runs, before anything has been saved.",
    "file.write_text(json.dumps({'count': 5})) leaves {\"count\": 5} in the "
    "file, and json.loads(file.read_text())['count'] is 5; json.dumps({'b': "
    "1, 'a': 2}, sort_keys=True) is {\"a\": 2, \"b\": 1}; json.loads('{\"a\":"
    "1,}') raises JSONDecodeError",
    "py_script_json",
    tuple(_json_row(row) for row in _JSONS),
)


# ── 346. Directories ─────────────────────────────────────────

_DIRS = (
    ("list", {"names": ["b.txt", "c.txt", "a.txt"]}),
    ("list", {"names": ["zebra.md", "apple.md", "mango.md", "kiwi.md"]}),
    ("list", {"names": ["file10.txt", "file2.txt", "file1.txt"]}),
    ("ext", {"names": ["a.js", "b.txt", "c.js", "d.md"], "ext": "js"}),
    ("ext", {"names": ["notes.txt", "app.js", "todo.txt", "main.py", "log.txt"], "ext": "txt"}),
    ("extcount", {"names": ["index.html", "style.css", "app.js", "about.html"], "ext": "html"}),
    ("extcount", {"names": ["a.png", "b.jpg", "c.png", "d.png", "e.gif"], "ext": "png"}),
    ("dirs", {"folders": ["src", "docs"], "plain": ["a.txt", "b.txt"]}),
    ("dirs", {"folders": ["lib", "test", "bin"], "plain": ["readme.md", "index.js"]}),
    ("files", {"folders": ["src", "docs"], "plain": ["notes.txt", "a.txt", "todo.md"]}),
    ("size", {"files": {"a.txt": "hello", "b.txt": "hi", "c.txt": "abc"}}),
    ("size", {"files": {"big.log": "lorem ipsum dolor", "small.log": "ok", "mid.log": "sit amet"}}),
    ("mkdir", {"path": ["a", "b"], "mode": "exists"}),
    ("mkdir", {"path": ["logs", "archive"], "mode": "exist_ok"}),
    ("mkdir", {"path": ["x", "y", "z"], "mode": "noparents"}),
    ("rglob_ext", {"names": ["a.py", "pkg/b.py", "pkg/c.txt", "pkg/sub/d.py"], "ext": "py"}),
    ("rglob_all", {"names": ["a.txt", "docs/b.md", "docs/img/c.png"]}),
    ("rglob_files", {"names": ["a.txt", "docs/b.md", "docs/c.md", "docs/img/d.png"]}),
    ("delete", {"names": ["a.txt", "b.txt", "c.txt", "d.txt"], "gone": ["b.txt"]}),
    ("delete", {"names": ["one.js", "two.js", "three.js", "four.js", "five.js"], "gone": ["two.js", "four.js"]}),
)


def _dirs_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "list":
        return (f"In {_TMP}, make empty files called {_and(a['names'])}. Print "
                f"the names in the folder in alphabetical order, joined by a "
                f"comma and a space.", args)
    if want in ("ext", "extcount"):
        made = f"In {_TMP}, make empty files called {_and(a['names'])}."
        if want == "ext":
            return (f"{made} Use glob to print the names in the folder that end "
                    f"in .{a['ext']}, in alphabetical order, joined by a comma "
                    f"and a space.", args)
        return (f"{made} Use glob to print how many names in the folder end in "
                f".{a['ext']}.", args)
    if want == "size":
        things = _and(f"{n} holding the text '{t}'" for n, t in a["files"].items())
        return (f"In {_TMP}, make the files {things}. Print the total size of "
                f"all the files in the folder, in bytes.", args)
    if want in ("dirs", "files"):
        what = "folders" if want == "dirs" else "files"
        return (f"In {_TMP}, make the empty folders {_and(a['folders'])} and the "
                f"empty files {_and(a['plain'])}. Go through the entries in "
                f"the folder and print the names of the {what}, in "
                f"alphabetical order, joined by a comma and a space.", args)
    if want == "mkdir":
        nested = "/".join(a["path"])
        if a["mode"] == "exists":
            return (f"In {_TMP}, make the nested folder {nested}, creating the "
                    f"parents it needs. Then try to make it a second time "
                    f"inside a try block, and print the word exists when that "
                    f"raises the error for a folder that is already there.", args)
        if a["mode"] == "exist_ok":
            return (f"In {_TMP}, make the nested folder {nested}, creating the "
                    f"parents it needs, then make it again, this time allowing "
                    f"it to exist. Print whether it is a folder, then the "
                    f"names of everything below the temporary folder, sorted "
                    f"and joined by a comma and a space.", args)
        return (f"In {_TMP}, try to make the nested folder {nested} without "
                f"asking for its parents, inside a try block, and print the "
                f"words no parent when that raises the error for a missing "
                f"folder. Then make it properly, creating its parents, and "
                f"print whether it is a folder.", args)
    made = (f"In {_TMP}, make empty files at the paths {_and(a['names'])}, "
            f"making any folders they need on the way.")
    if want == "rglob_ext":
        return (f"{made} Search everything below the temporary folder, folders "
                f"included, for names ending in .{a['ext']} with rglob, and "
                f"print their paths relative to the temporary folder, with "
                f"forward slashes, sorted and joined by a comma and a "
                f"space.", args)
    if want == "rglob_all":
        return (f"{made} Search everything below the temporary folder with "
                f"rglob, and print every path it finds, files and folders, "
                f"relative to the temporary folder with forward slashes, "
                f"sorted and joined by a comma and a space.", args)
    if want == "rglob_files":
        return (f"{made} Search everything below the temporary folder with "
                f"rglob, and print how many of the things it finds are files "
                f"rather than folders.", args)
    return (f"In {_TMP}, make empty files called {_and(a['names'])}, then "
            f"delete {_and(a['gone'])} with unlink. Print the names left in "
            f"the folder in alphabetical order, joined by a comma and a "
            f"space.", args)


DIRS_PAGE = _page(
    "py-script-dirs", 346, "Scripting: directories",
    "folder.iterdir() yields a Path for each thing inside a folder and "
    "folder.glob('*.js') only those whose names match, but neither promises "
    "an order, because the operating system decides it. Wrap them in "
    "sorted() before printing anything you want to be the same every time: "
    "strings sort by character code, so 'file10.txt' lands before "
    "'file2.txt', since 1 comes before 2. p.name is the name without its "
    "folder, p.is_dir() and p.is_file() tell folders from files, and "
    "p.stat().st_size is a file's size in bytes. path.mkdir() makes one "
    "folder and raises FileNotFoundError when its parent is missing and "
    "FileExistsError when it is already there; mkdir(parents=True) makes the "
    "parents too, and exist_ok=True stops the second complaint. "
    "folder.rglob('*') walks everything below, folders included, and "
    "p.relative_to(folder).as_posix() writes a path from the starting folder "
    "with forward slashes. file.touch() makes an empty file and "
    "file.unlink() removes one. The folder from TemporaryDirectory starts "
    "empty, so a listing holds exactly what the program made. Names here "
    "are lowercase, since glob ignores case on Windows and not on Linux.",
    "root = Path(tmp); for name in ['b.txt', 'a.txt']: (root / name).touch(); "
    "sorted(p.name for p in root.iterdir()) is ['a.txt', 'b.txt'], and "
    "', '.join(...) of it is a.txt, b.txt",
    "py_script_dirs",
    tuple(_dirs_row(row) for row in _DIRS),
)


# ── 347. The csv module ──────────────────────────────────────


def _csv_lines(rows, delim: str = ",") -> list[str]:
    """The lines of the text, as the prompt shows them."""
    out = []
    for r in rows:
        fields = []
        for f in r:
            f = str(f)
            if any(c in f for c in (delim, '"')):
                f = '"' + f.replace('"', '""') + '"'
            fields.append(f)
        out.append(delim.join(fields))
    return out


def _csv_source(rows, delim: str = ",") -> str:
    lines = _quoted(_csv_lines(rows, delim))
    return f"Take the text made of the lines {lines}, each ending in a newline."


def _row_text(r) -> str:
    return "(" + ", ".join(f"'{f}'" if isinstance(f, str) else str(f) for f in r) + ")"


_PEOPLE = [["name", "age"], ["Ada", "36"], ["Linus", "54"], ["Grace", "45"]]
_CITIES = [["city", "pop", "country"], ["Oslo", "709", "Norway"], ["Rome", "2873", "Italy"]]
_HOMES = [["name", "city"], ["Ada", "London"], ["Linus", "Helsinki"], ["Grace", "New York"]]
_FRUIT = [["item", "colour"], ["apple", "red"], ["pear", "green"], ["plum", "purple"]]
_TEAMS = [["team", "coach", "wins"], ["Reds", "Kim", "12"], ["Blues", "Lee", "9"]]
_STOCK = [["item", "qty"], ["pen", "4"], ["ink", "2"], ["pad", "3"]]
_LEVELS = [["name", "points", "level"], ["Ada", "30", "1"], ["Linus", "12", "2"], ["Grace", "58", "1"]]
_STEPS = [["day", "steps"], ["mon", "4200"], ["tue", "5100"], ["wed", "3900"]]
_NOTES = [["name", "note"], ["Ada", "likes tea, hot"], ["Linus", "plain"]]
_QUOTES = [["quote", "by"], ['She said "hi"', "Ada"], ["plain", "Linus"]]
_BOOKS = [["title", "author"], ["Hello, World", "Ada"], ["Dune", "Frank"]]
_PRICES = [["item", "price"], ["pen", "3,50"], ["ink", "8,25"]]

_CSVS = (
    ("rows", {"rows": _PEOPLE}),
    ("rows", {"rows": _CITIES}),
    ("dictreader", {"rows": _HOMES, "row": 1, "col": "city"}),
    ("dictreader", {"rows": _FRUIT, "row": 2, "col": "colour"}),
    ("dictreader", {"rows": _TEAMS, "row": 0, "col": "coach"}),
    ("total", {"rows": _STOCK, "col": "qty"}),
    ("total", {"rows": _LEVELS, "col": "points"}),
    ("total", {"rows": _STEPS, "col": "steps"}),
    ("quoted", {"rows": _NOTES, "row": 1, "col": 1}),
    ("quoted", {"rows": _QUOTES, "row": 1, "col": 0}),
    ("write", {"rows": _NOTES}),
    ("write", {"rows": [["item", "qty"], ["pen, blue", 4], ["ink", 2]]}),
    ("write", {"rows": _QUOTES}),
    ("dictwriter", {"names": ["name", "age"], "rows": [["Ada", 36], ["Linus", 54]]}),
    ("dictwriter", {"names": ["city", "pop"], "rows": [["Oslo", 709], ["Rome", 2873]]}),
    ("delimiter", {"rows": _NOTES, "delim": ";", "row": 1, "col": 1}),
    ("delimiter", {"rows": _PRICES, "delim": ";", "row": 2, "col": 1}),
    ("group", {"rows": [["team", "points"], ["Reds", "3"], ["Blues", "1"], ["Reds", "2"], ["Blues", "1"]],
               "key": "team", "num": "points"}),
    ("group", {"rows": [["city", "sales"], ["Oslo", "10"], ["Rome", "7"], ["Oslo", "5"]],
               "key": "city", "num": "sales"}),
    ("group", {"rows": [["fruit", "kg"], ["pear", "2"], ["plum", "9"], ["pear", "4"],
                        ["fig", "1"], ["plum", "3"]], "key": "fruit", "num": "kg"}),
)


def _csv_row(row):
    want, a = row
    args = {"want": want, **a}
    rows = a["rows"]
    delim = a.get("delim", ",")
    if want == "rows":
        return (f"{_csv_source(rows)} Read it with csv.reader over a StringIO, "
                f"and print how many rows there are after the header.", args)
    if want == "dictreader":
        return (f"{_csv_source(rows)} Read it with csv.DictReader over a "
                f"StringIO, and print the {a['col']} in row number {a['row']}, "
                f"counting the first row after the header as 0.", args)
    if want == "total":
        return (f"{_csv_source(rows)} Read it with csv.DictReader over a "
                f"StringIO, and print the sum of the {a['col']} column.", args)
    if want == "quoted":
        return (f"{_csv_source(rows)} Read it with csv.reader over a StringIO. "
                f"Print how many fields row {a['row']} has, counting the "
                f"header as row 0, then the text of its field number "
                f"{a['col']}, counting from 0.", args)
    if want == "delimiter":
        return (f"{_csv_source(rows, delim)} Read it with csv.reader over a "
                f"StringIO, telling it that fields are separated by "
                f"'{delim}', and print the text of field number {a['col']} in "
                f"row {a['row']}, counting the header as row 0 and the first "
                f"field as 0.", args)
    if want == "write":
        things = _and(_row_text(r) for r in rows)
        return (f"Write the rows {things} with csv.writer to a StringIO, using "
                f"a newline as the line terminator, and print what the buffer "
                f"holds.", args)
    if want == "dictwriter":
        names = a["names"]
        things = _and(
            "{" + ", ".join(f"{n}: {v}" for n, v in zip(names, r)) + "}"
            for r in rows)
        return (f"Write the dictionaries {things} with csv.DictWriter to a "
                f"StringIO, with the field names {_and(names)}, a header row "
                f"and a newline as the line terminator, and print what the "
                f"buffer holds.", args)
    return (f"{_csv_source(rows)} Read it with csv.DictReader over a StringIO. "
            f"Add up the {a['num']} for each {a['key']}, and print each "
            f"{a['key']} and its total on its own line, the key then a space "
            f"then the total, in alphabetical order of the keys.", args)


CSV_PAGE = _page(
    "py-script-csv", 347, "Scripting: the csv module",
    "The csv module reads and writes comma-separated text, and it works on "
    "any file-like object, so io.StringIO(text) lets you try it without a "
    "file. csv.reader(f) yields each row as a list of strings, numbers "
    "included, so int() is yours to call. csv.DictReader(f) uses the first "
    "row as names and yields a dictionary for each row after it. Do not "
    "split on commas yourself: a field in quotes can hold a comma, and a "
    "doubled quote inside it is one quote. delimiter=';' reads other "
    "separators. csv.writer(buffer).writerows(rows) writes them, quoting "
    "only the fields that need it (a comma, a quote or a line break in "
    "them), and doubling any quotes inside; by default every line ends in "
    "\\r\\n, so these programs pass lineterminator='\\n'. csv.DictWriter "
    "needs fieldnames, and writeheader() writes them as the first line. "
    "buffer.getvalue() is everything written so far.",
    "import csv, io; rows = list(csv.reader(io.StringIO('a,b\\n1,\"x, y\"\\n'))) "
    "is [['a', 'b'], ['1', 'x, y']]; buffer = io.StringIO(); csv.writer("
    "buffer, lineterminator='\\n').writerow(['1', 'x, y']) makes buffer."
    "getvalue() 1,\"x, y\"",
    "py_script_csv",
    tuple(_csv_row(row) for row in _CSVS),
)


# ── 348. Logging ─────────────────────────────────────────────

_FMT_LEVEL = "%(levelname)s:%(message)s"

_LOGS = (
    ("emit", {"fmt": "%(levelname)s:%(message)s", "level": "WARNING",
              "calls": [(None, "info", "starting"), (None, "warning", "disk low"),
                        (None, "error", "disk full")]}),
    ("emit", {"fmt": "[%(levelname)s] %(message)s", "level": "INFO",
              "calls": [(None, "debug", "raw bytes"), (None, "info", "connected"),
                        (None, "warning", "slow reply")]}),
    ("emit", {"fmt": "%(name)s - %(levelname)s - %(message)s", "level": "INFO",
              "calls": [(None, "info", "hello"), (None, "debug", "hidden")]}),
    ("emit", {"fmt": "%(levelno)d %(message)s", "level": "DEBUG",
              "calls": [(None, "debug", "first"), (None, "error", "second")]}),
    ("emit", {"fmt": "%(levelname)-8s|%(message)s", "level": "INFO",
              "calls": [(None, "info", "ready"), (None, "critical", "meltdown"),
                        (None, "debug", "noise")]}),
    ("emit", {"fmt": "%(message)s (%(levelname)s)", "level": "ERROR",
              "calls": [(None, "warning", "careful"), (None, "error", "failed"),
                        (None, "critical", "stop")]}),
    ("emit", {"fmt": "%(name)s: %(message)s", "level": "INFO",
              "calls": [("app.db", "info", "connected"), ("app.web", "warning", "slow"),
                        (None, "warning", "root says hi")]}),
    ("emit", {"fmt": "%(name)s %(levelname)s %(message)s", "level": "WARNING",
              "calls": [("app.db", "info", "skipped"), ("app.db", "error", "timeout"),
                        ("app.cache", "warning", "cold")]}),
    ("emit", {"fmt": "%(levelname)s %(levelno)d %(message)s", "level": "INFO",
              "calls": [(None, "info", "a"), (None, "warning", "b"),
                        (None, "debug", "c"), (None, "error", "d")]}),
    ("emit", {"fmt": "%(name)s [%(levelname)s] %(message)s", "level": "ERROR",
              "calls": [("app", "error", "boom"), ("app", "warning", "hmm")]}),
    ("args", {"fmt": "%(message)s", "level": "INFO",
              "calls": [("debug", "cache has %d items", [7]),
                        ("info", "loaded %d rows from %s", [120, "data.csv"])]}),
    ("args", {"fmt": "%(levelname)s: %(message)s", "level": "WARNING",
              "calls": [("warning", "%s is at %d percent", ["disk", 91]),
                        ("info", "%s is fine", ["cpu"])]}),
    ("args", {"fmt": "[%(levelname)s] %(message)s", "level": "DEBUG",
              "calls": [("debug", "user %s logged in", ["ada"]),
                        ("error", "retry %d of %d failed", [2, 3])]}),
    ("count", {"fmt": "%(message)s", "level": "WARNING",
               "calls": [(None, "info", "a"), (None, "warning", "b"),
                         (None, "error", "c"), (None, "debug", "d")]}),
    ("count", {"fmt": "%(message)s", "level": "INFO",
               "calls": [(None, "debug", "a"), (None, "info", "b"),
                         (None, "warning", "c"), (None, "error", "d")]}),
    ("count", {"fmt": "%(message)s", "level": "CRITICAL",
               "calls": [(None, "error", "a"), (None, "critical", "b"),
                         (None, "warning", "c"), (None, "critical", "d")]}),
    ("count", {"fmt": "%(message)s", "level": "WARNING",
               "calls": [(None, "info", "a"), (None, "info", "b"),
                         (None, "warning", "c")]}),
    ("named", {"fmt": "%(name)s %(levelname)s %(message)s", "name": "app.db",
               "calls": [("info", "connected"), ("warning", "slow query")]}),
    ("named", {"fmt": "%(name)s: %(message)s", "name": "app.web",
               "calls": [("error", "timeout"), ("debug", "trace")]}),
    ("named", {"fmt": "%(levelname)s|%(name)s|%(message)s", "name": "worker",
               "calls": [("critical", "out of memory")]}),
)


def _article(level: str) -> str:
    return "an" if level[0] in "aeiou" else "a"


def _call_text(call, named: bool) -> str:
    if len(call) == 3 and isinstance(call[2], list):
        level, template, values = call
        shown = _and(f"'{v}'" if isinstance(v, str) else v for v in values)
        return (f"{_article(level)} {level} message '{template}' with the "
                f"values {shown}")
    if len(call) == 3:
        name, level, message = call
        where = (f"to the logger {name}, " if name else "to the root logger, ") if named else ""
        return f"{where}{_article(level)} {level} message '{message}'"
    level, message = call
    return f"{_article(level)} {level} message '{message}'"


def _log_row(row):
    want, a = row
    args = {"want": want, **a}
    named = any(len(c) == 3 and not isinstance(c[2], list) and c[0] for c in a["calls"])
    calls = _then(_call_text(c, named) for c in a["calls"])
    if want == "emit":
        return (f"Send the logging output to a StringIO with basicConfig, using "
                f"the format {a['fmt']} and the level {a['level']}. Then log, "
                f"in order: {calls}. Print what the StringIO holds.", args)
    if want == "args":
        return (f"Send the logging output to a StringIO with basicConfig, using "
                f"the format {a['fmt']} and the level {a['level']}. Then log, "
                f"in order, using the root logger and passing the values as "
                f"arguments: {calls}. Print what the StringIO holds.", args)
    if want == "count":
        return (f"Send the logging output to a StringIO with basicConfig, using "
                f"the format {a['fmt']} and the level {a['level']}. Then log, "
                f"in order: {calls}. Print how many lines the StringIO "
                f"holds.", args)
    return (f"Make a logger called {a['name']} with a StreamHandler that writes "
            f"to a StringIO, formatted with {a['fmt']}, and set no level "
            f"anywhere. Log, in order: {calls}. Print what the StringIO "
            f"holds.", args)


LOG_PAGE = _page(
    "py-script-log", 348, "Scripting: logging",
    "logging is print with a dial. logging.basicConfig(stream=stream, "
    "format=..., level=...) sets up the root logger once, and then "
    "logging.info('text') and the others (debug, warning, error, critical, "
    "from quietest to loudest) send a record to it. A record below the "
    "level is dropped: the default is WARNING, so info and debug vanish "
    "until you ask for them. The format fills in %(levelname)s, %(name)s "
    "(root, unless the record came from logging.getLogger('app.db')), "
    "%(message)s and %(levelno)d, and %(levelname)-8s pads a field to eight "
    "characters. Pass values as arguments rather than formatting them "
    "yourself: logging.info('loaded %d rows', n) only builds the message if "
    "it is going to be written. A logger's name is dotted, and a child "
    "such as app.db hands its records up to its parents. Without a level of "
    "its own a logger takes its parent's, and the root's is WARNING. "
    "StreamHandler(stream) writes to any file-like object, io.StringIO "
    "included, which is how these programs keep the output in a variable "
    "(print it with end='', since every record already ends in a newline), "
    "and handler.setFormatter(logging.Formatter(...)) gives one handler its "
    "own format.",
    "stream = io.StringIO(); logging.basicConfig(stream=stream, format="
    "'%(levelname)s:%(message)s', level=logging.WARNING); logging.info('a'); "
    "logging.error('b') leaves stream.getvalue() as ERROR:b with a newline: "
    "the info call is below WARNING",
    "py_script_log",
    tuple(_log_row(row) for row in _LOGS),
)


# ── 349. Environment and exit codes ──────────────────────────

_ENVS = (
    ("port", {"env": {"PORT": "8080", "HOST": "localhost"}, "default": 3000}),
    ("port", {"env": {"HOST": "localhost"}, "default": 3000}),
    ("port", {"env": {"PORT": "", "MODE": "dev"}, "default": 4000}),
    ("flag", {"env": {"DEBUG": "true", "NAME": "ada"}, "key": "DEBUG"}),
    ("flag", {"env": {"DEBUG": "1"}, "key": "DEBUG"}),
    ("flag", {"env": {"NAME": "ada", "SHELL": "bash"}, "key": "VERBOSE"}),
    ("mode", {"env": {"APP_ENV": "production"}, "key": "APP_ENV", "default": "development"}),
    ("mode", {"env": {"LOG_LEVEL": ""}, "key": "LOG_LEVEL", "default": "info"}),
    ("list", {"env": {"TAGS": "red,green,blue"}}),
    ("list", {"env": {"USER": "ada"}}),
    ("exit", {"rule": "even", "input": 7}),
    ("exit", {"rule": "even", "input": 8}),
    ("exit", {"rule": "small", "input": 250}),
    ("sysexit", {"kind": "none"}),
    ("sysexit", {"kind": "three"}),
    ("sysexit", {"kind": "text"}),
    ("child", {"code": "raise SystemExit(3)"}),
    ("child", {"code": "1 / 0"}),
    ("atexit", {"lines": ["one", "two"], "handlers": ["bye"]}),
    ("atexit", {"lines": ["start", "end"], "handlers": ["first", "second"]}),
)

_RULE_TEXT = {
    "even": ("an even number", "must be even"),
    "positive": ("a number above zero", "must be positive"),
    "small": ("a number under 100", "must be under 100"),
}

_EXIT_WORDS = {
    "none": "no argument",
    "zero": "the number 0",
    "three": "the number 3",
    "text": "the text 'bad input'",
}


def _env_say(env: dict) -> str:
    return "{" + ", ".join(f"'{k}': '{v}'" for k, v in env.items()) + "}"


def _env_row(row):
    want, a = row
    args = {"want": want, **a}
    if want in ("port", "flag", "mode", "list"):
        head = (f"Take env to be the dictionary {_env_say(a['env'])}, standing "
                f"in for os.environ.")
    if want == "port":
        return (f"{head} Print the PORT as a number, using {a['default']} when "
                f"it is missing or empty.", args)
    if want == "flag":
        return f"{head} Print whether {a['key']} is exactly the text true.", args
    if want == "mode":
        return (f"{head} Print the name {a['key']}, a space, the word is, a "
                f"space and the value of {a['key']}, or {a['default']} when it "
                f"is missing or empty.", args)
    if want == "list":
        return (f"{head} TAGS, when it is there, is a list separated by commas. "
                f"Print how many tags there are (none when it is missing), then "
                f"the tags joined by a space, a bar and a space, or the word "
                f"none when there are no tags.", args)
    if want == "exit":
        kind, message = _RULE_TEXT[a["rule"]]
        return (f"A program is given the number {a['input']}, and needs {kind}. "
                f"Raise SystemExit with the message '{message}' when it is not, "
                f"and catch it, setting a variable called code to 1; otherwise "
                f"code stays 0. Print ok and the number when all is well, or "
                f"error: and the message (the code attribute of the exception) "
                f"when it is not, then print the words exit code and the value "
                f"of code.", args)
    if want == "sysexit":
        return (f"Inside a try block call sys.exit with {_EXIT_WORDS[a['kind']]}, "
                f"catch the SystemExit, and print its code attribute.", args)
    if want == "child":
        return (f"Run a second Python process on the one-line program "
                f"{a['code']} with subprocess.run, using the current "
                f"interpreter from sys.executable and capturing its output, "
                f"and print its return code.", args)
    handlers = a["handlers"]
    if len(handlers) == 1:
        register = f"Use atexit to register a call of print with the word '{handlers[0]}'"
    else:
        register = (f"Use atexit to register a call of print for each of the words "
                    f"{_and(f'{chr(39)}{h}{chr(39)}' for h in handlers)}, in that order")
    return (f"{register}, then print the lines {_and(a['lines'])} in order.", args)


ENV_PAGE = _page(
    "py-script-env", 349, "Scripting: environment and exit codes",
    "os.environ behaves like a dictionary of the environment variables the "
    "program started with. Every value is a string, and a variable that was "
    "never set is simply missing, so env.get('PORT') is None and "
    "env.get('PORT', '3000') supplies a default. An empty string is also "
    "set, and `or` treats it like a missing one, so env.get('PORT') or 3000 "
    "is what usually wants writing. Convert with int() when a number is "
    "needed, and compare with == 'true' for a flag, since the text 'false' "
    "is truthy. A program tells the system how it went through its exit "
    "code: 0 means success and anything else means failure. sys.exit(3) "
    "and raise SystemExit(3) both end the program with 3 by raising "
    "SystemExit, which except SystemExit as err can catch, and err.code is "
    "whatever was passed: None for sys.exit() (which still means 0), a "
    "number, or a message, which Python prints to stderr and turns into "
    "the code 1. A script that dies from an uncaught exception also exits "
    "with 1. subprocess.run([sys.executable, '-c', code]).returncode runs a "
    "second Python and reads the code it ended with. "
    "atexit.register(function, *args) runs the function when the program "
    "ends, after every other line, and the last one registered runs first.",
    "env = {'PORT': '8080'}; int(env.get('PORT') or 3000) is 8080, and with "
    "no PORT it is 3000; try: sys.exit(3) except SystemExit as err: err.code "
    "is 3; atexit.register(print, 'bye') prints bye after everything else",
    "py_script_env",
    tuple(_env_row(row) for row in _ENVS),
)


# ── 350. A small http server ─────────────────────────────────

_HTTPS = (
    ("body", {"status": 201, "text": "created"}),
    ("body", {"status": 200, "text": "hello"}),
    ("body", {"status": 202, "text": "accepted"}),
    ("header", {"header": "X-Greeting", "value": "hello", "text": "ok"}),
    ("json", {"obj": {"name": "Ada", "age": 36}, "key": "name"}),
    ("json", {"obj": {"ok": True, "count": 3}, "key": "ok"}),
    ("method", {"method": "DELETE", "path": "/items/7?force=1"}),
    ("method", {"method": "PUT", "path": "/items/7"}),
    ("count", {"start": 0, "n": 3}),
    ("count", {"start": 10, "n": 2}),
    ("query", {"fallback": "stranger", "path": "/hello?name=Ada"}),
    ("query", {"fallback": "friend", "path": "/hello?name=Ada%20Lovelace"}),
    ("query", {"fallback": "guest", "path": "/hello"}),
    ("query", {"fallback": "stranger", "path": "/goodbye?name=Ada"}),
    ("calc", {"keys": ["a", "b"], "op": "+", "x": 2, "y": 3}),
    ("calc", {"keys": ["x", "y"], "op": "*", "x": 4, "y": 6}),
    ("pages", {"pages": [("/", "home"), ("/about", "about us")], "path": "/about"}),
    ("pages", {"pages": [("/hello", "Hi!"), ("/bye", "Goodbye!")], "path": "/bye?lang=en"}),
    ("post", {"field": "numbers", "value": [3, 4, 5], "reply": "sum"}),
    ("post", {"field": "word", "value": "stressed", "reply": "upper"}),
)

_SERVE = ("Start an http.server HTTPServer on port 0 of 127.0.0.1 (let the "
          "system choose the port), serving from a daemon thread, with a "
          "handler ")
_ASK = "Once it is running, use urllib.request to ask it for "
_STOP = "and shut the server down."

_POST_REPLIES = {
    "sum": "sending back the sum of those numbers",
    "max": "sending back the biggest of those numbers",
    "upper": "sending back that text in capital letters",
    "length": "sending back the number of characters in that text",
}


def _http_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "body":
        return (f"{_SERVE}that answers every GET request with the status "
                f"{a['status']} and the text '{a['text']}'. {_ASK}its address, "
                f"print the status and then the body text, {_STOP}", args)
    if want == "header":
        return (f"{_SERVE}that answers every GET request with the header "
                f"{a['header']} set to '{a['value']}' and the body text "
                f"'{a['text']}'. {_ASK}its address, print the value of that "
                f"header and then the body text, {_STOP}", args)
    if want == "json":
        return (f"{_SERVE}that answers every GET request with a dictionary "
                f"with {_describe(a['obj'])}, written as JSON, with the "
                f"content type set to application/json. {_ASK}its address, "
                f"read the body as JSON, print its {a['key']}, {_STOP}", args)
    if want == "method":
        return (f"{_SERVE}that answers every request with the request's "
                f"method, a space and the request's path. {_ASK}"
                f"{a['path']} with the {a['method']} method, print the "
                f"answer, {_STOP}", args)
    if want == "count":
        return (f"{_SERVE}that keeps a counter starting at {a['start']} and "
                f"answers every GET request by adding one to it and sending "
                f"back the new value. {_ASK}its address {a['n']} times in a "
                f"row, one after the other, print the answers on one line "
                f"joined by a comma and a space, {_STOP}", args)
    if want == "query":
        return (f"{_SERVE}that answers the path /hello with Hello, a comma, a "
                f"space, the value of the name query parameter and an "
                f"exclamation mark, or the word {a['fallback']} when there is "
                f"no name, and answers any other path with the status 404 and "
                f"the text not found. {_ASK}{a['path']}, catching the error "
                f"urlopen raises for a 404, print the status and then the "
                f"text, {_STOP}", args)
    if want == "calc":
        x, y = a["keys"]
        verb = {"+": "sum", "-": "difference", "*": "product"}[a["op"]]
        return (f"{_SERVE}that reads the query parameters {x} and {y} as whole "
                f"numbers, and answers with JSON holding their {verb} as "
                f"result, with the content type set to application/json. "
                f"{_ASK}/calc?{x}={a['x']}&{y}={a['y']}, print the content "
                f"type, then on the next line the result from the JSON, "
                f"{_STOP}", args)
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        return (f"{_SERVE}that answers the path {p1} with the text '{t1}', the "
                f"path {p2} with the text '{t2}' (ignoring any query string), "
                f"and every other path with the status 404 and the text not "
                f"found. {_ASK}{a['path']}, catching the error urlopen raises "
                f"for a 404, print the status and then the text, {_STOP}", args)
    field, value = a["field"], a["value"]
    body = _describe({field: value})
    return (f"{_SERVE}that answers a POST request by reading its JSON body, a "
            f"dictionary, and {_POST_REPLIES[a['reply']]} under the key "
            f"{field}. {_ASK}its address with a POST request whose body is the "
            f"JSON for a dictionary with {body}, print the answer, {_STOP}", args)


HTTP_PAGE = _page(
    "py-script-http", 350, "Scripting: a small http server",
    "http.server's HTTPServer(address, Handler) makes a web server, and "
    "Handler is a subclass of BaseHTTPRequestHandler with a method named "
    "for each verb it answers: do_GET, do_POST and so on. Inside, "
    "self.path holds the path and the query string together, such as "
    "/hello?name=Ada, and self.command the method. Answer in three steps: "
    "self.send_response(status), then any self.send_header(name, value) "
    "calls, then self.end_headers(), and only after that "
    "self.wfile.write(bytes) with the body, which has to be bytes, "
    "not a string, so text is b'...' or text.encode(). A request body is "
    "read with self.rfile.read(n), where n is the Content-Length header. "
    "urllib.parse.urlparse(self.path) splits the path from the query, "
    "and parse_qs(query) gives a dictionary of lists, decoded, so %20 and + "
    "both come out as spaces: parse_qs('name=Ada')['name'][0] is Ada. "
    "HTTPServer(('127.0.0.1', 0), Handler) asks the system for any free "
    "port, so nothing clashes, and server.server_port says which it was. "
    "serve_forever() blocks, so it runs in a daemon thread, and "
    "serve_forever(0.01) checks for a shutdown every ten milliseconds, "
    "where the default waits half a second. On the other side, "
    "urllib.request.urlopen(url) gives a response with .status, "
    ".headers['Name'] and .read(), which is bytes, so decode() it; for a "
    "404 or a 500 it raises urllib.error.HTTPError instead, which is itself "
    "a response with the same .status and .read(). Finish with "
    "server.shutdown(). Stay on 127.0.0.1: that address cannot be reached "
    "from outside the machine. The server's own log line goes to stderr, "
    "not to what the program prints.",
    "class Handler(BaseHTTPRequestHandler): def do_GET(self): self."
    "send_response(200); self.end_headers(); self.wfile.write(b'hi'); then "
    "server = HTTPServer(('127.0.0.1', 0), Handler), a daemon Thread running "
    "server.serve_forever, and urllib.request.urlopen(f'http://127.0.0.1:"
    "{server.server_port}/').read() is b'hi'",
    "py_script_http",
    tuple(_http_row(row) for row in _HTTPS),
)


# ── 351. asyncio ─────────────────────────────────────────────

_ASYNCS = (
    ("order", {"jobs": [("a", 60), ("b", 20), ("c", 40)]}),
    ("order", {"jobs": [("cook", 50), ("chop", 20), ("serve", 70)]}),
    ("order", {"jobs": [("x", 60), ("y", 20), ("z", 40), ("w", 90)]}),
    ("results", {"jobs": [("a", 60), ("b", 20), ("c", 40)]}),
    ("results", {"jobs": [("red", 40), ("green", 20), ("blue", 60)]}),
    ("results", {"jobs": [("x", 60), ("y", 20), ("z", 40)]}),
    ("total", {"jobs": [(3, 40), (5, 20), (10, 60)]}),
    ("total", {"jobs": [(1, 30), (4, 10), (2, 50), (7, 70)]}),
    ("timeout", {"delay": 70, "limit": 30, "word": "done"}),
    ("timeout", {"delay": 20, "limit": 60, "word": "ready"}),
    ("timeout", {"delay": 90, "limit": 40, "word": "late"}),
    ("timeout", {"delay": 30, "limit": 80, "word": "early"}),
    ("sequence", {"jobs": [("a", 60), ("b", 20), ("c", 40)]}),
    ("sequence", {"jobs": [("one", 80), ("two", 20), ("three", 40)]}),
    ("tasks", {"jobs": [("a", 30), ("b", 10)], "sync": "scheduled"}),
    ("tasks", {"jobs": [("x", 20), ("y", 60), ("z", 40)], "sync": "waiting"}),
    ("tasks", {"jobs": [("one", 50), ("two", 10)], "sync": "started"}),
    ("completed", {"jobs": [("a", 60), ("b", 20), ("c", 40)]}),
    ("completed", {"jobs": [("slow", 60), ("fast", 10), ("medium", 30)]}),
    ("completed", {"jobs": [("w", 90), ("x", 50), ("y", 20), ("z", 70)]}),
)


def _after(jobs) -> str:
    return _and(f"{label} after {ms / 1000} seconds" for label, ms in jobs)


def _async_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "order":
        return (f"Run these jobs at the same time with asyncio.gather, started "
                f"in this order: {_after(a['jobs'])}. Each job sleeps for its "
                f"delay and then prints its label.", args)
    if want == "results":
        return (f"Run these jobs at the same time with asyncio.gather, started "
                f"in this order: {_after(a['jobs'])}. Each job sleeps for its "
                f"delay and then returns its label. Print the list that "
                f"gather gives back.", args)
    if want == "total":
        jobs = _and(f"the number {n} after {ms / 1000} seconds"
                    for n, ms in a["jobs"])
        return (f"Run these jobs at the same time with asyncio.gather: {jobs}. "
                f"Each job sleeps for its delay and then returns its number "
                f"doubled. Print the sum of the list that gather gives "
                f"back.", args)
    if want == "timeout":
        return (f"Wait for a sleep of {a['delay'] / 1000} seconds that returns "
                f"the text {a['word']}, using asyncio.wait_for with a timeout "
                f"of {a['limit'] / 1000} seconds. Print the text when it "
                f"arrives, or the word timeout when the wait times "
                f"out.", args)
    if want == "sequence":
        return (f"Await these jobs one after another in a loop, in the order "
                f"listed: {_after(a['jobs'])}. Each job sleeps for its delay "
                f"and then prints its label.", args)
    if want == "tasks":
        jobs = _and(f"{label} after {ms / 1000} seconds" for label, ms in a["jobs"])
        return (f"Turn each of these sleeps into a task with "
                f"asyncio.create_task, in this order: {jobs}. Each sleep "
                f"returns its label. Straight after creating the tasks, print "
                f"the word {a['sync']}, then await each task in order and "
                f"print their results on one line, separated by spaces.", args)
    return (f"Use asyncio.as_completed over these sleeps: {_after(a['jobs'])}. "
            f"Each sleep returns its label. Print each label as it "
            f"finishes.", args)


ASYNC_PAGE = _page(
    "py-script-async", 351, "Scripting: asyncio",
    "An async def function makes a coroutine, which does nothing until it is "
    "awaited or scheduled, and asyncio.run(main()) starts the loop that runs "
    "it. await asyncio.sleep(delay) pauses only that coroutine and lets the "
    "others carry on, which is the point. asyncio.gather(a, b, c) runs them "
    "all at once and returns their results as a list in the order you passed "
    "them, whichever finished first; the time it takes is the longest "
    "delay, where awaiting them one after another takes the total. "
    "asyncio.create_task(coro) starts one running straight away and gives "
    "back a task to await later, and nothing runs until the code reaches an "
    "await, so anything printed before it comes first. "
    "asyncio.as_completed(coros) hands them over in the order they finish. "
    "asyncio.wait_for(coro, timeout) gives up after timeout seconds and "
    "raises TimeoutError. asyncio.sleep(delay, result) returns result "
    "when it wakes, which makes a handy stand-in for a slow call. The "
    "delays here are tens of milliseconds apart, so the order is certain.",
    "async def job(label, delay): await asyncio.sleep(delay); print(label); "
    "then asyncio.gather(job('a', 0.03), job('b', 0.01)) prints b then a, "
    "and await asyncio.gather(asyncio.sleep(0.03, 'a'), asyncio.sleep(0.01, "
    "'b')) is ['a', 'b']",
    "py_script_async",
    tuple(_async_row(row) for row in _ASYNCS),
)


PYSCRIPT_PAGES: tuple[Page, ...] = (
    PATH_PAGE,
    ARGS_PAGE,
    FILES_PAGE,
    JSON_PAGE,
    DIRS_PAGE,
    CSV_PAGE,
    LOG_PAGE,
    ENV_PAGE,
    HTTP_PAGE,
    ASYNC_PAGE,
)
