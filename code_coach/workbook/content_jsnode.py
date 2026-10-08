"""Pages 238-247: JavaScript, Node.js practice.

Node outside the browser: the path module, command-line arguments, reading
and writing files, JSON on disk, directories, events and timers, environment
variables and exit codes, and a small HTTP server that asks itself a
question. The first half is the file system and the process, the last two
pages are a server.

Everything runs as plain `node file.js` with no arguments and no network
beyond 127.0.0.1. process.argv and process.env cannot be passed in, so the
exercises give an array or an object to stand in for them. Files live in a
folder from mkdtempSync and no program prints a path. The path pages use
path.posix, so Windows and Linux print the same.

Numbered after the bodybuilding pages (228-237, content_jslifting), so this
tuple has to be registered after JSLIFTING_PAGES for the book to stay in
order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


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
        languages=JS_ONLY,
        tier="intermediate",
    )


def _and(words) -> str:
    words = [str(w) for w in words]
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _then(words) -> str:
    words = list(words)
    return ", then ".join(words)


#: Where a file program does its work.
_TMP = "a fresh temporary folder made with mkdtempSync under os.tmpdir()"


# ── 238. The path module ─────────────────────────────────────

_PATHS = (
    ("join", {"parts": ["srv", "app", "..", "logs", "today.txt"]}),
    ("join", {"parts": ["/home", "ada", "projects", "..", "notes", "todo.md"]}),
    ("join", {"parts": ["assets", "img", ".", "icons", "..", "logo.png"]}),
    ("resolve", {"base": "/srv/app", "rest": ["../logs", "today.txt"]}),
    ("resolve", {"base": "/home/ada", "rest": ["projects", "../music", "song.mp3"]}),
    ("resolve", {"base": "/var/www/site", "rest": ["css/../js", "app.js"]}),
    ("name", {"file": "/home/ada/notes.txt"}),
    ("name", {"file": "/srv/backups/archive.tar.gz"}),
    ("name", {"file": "/etc/.bashrc"}),
    ("ext", {"file": "/home/ada/photo.jpeg"}),
    ("ext", {"file": "/srv/data/archive.tar.gz"}),
    ("ext", {"file": "/srv/app/Makefile"}),
    ("dir", {"file": "/home/ada/notes.txt"}),
    ("dir", {"file": "/srv/app/logs/today.log"}),
    ("rel", {"from": "/srv/app", "to": "/srv/logs/today.txt"}),
    ("rel", {"from": "/home/ada", "to": "/home/ada/projects/app"}),
    ("rel", {"from": "/var/www/site", "to": "/etc/nginx"}),
    ("abs", {"p": "/usr/local/bin"}),
    ("abs", {"p": "src/index.js"}),
    ("abs", {"p": "../config.json"}),
)


def _path_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "join":
        return (f"Join the pieces {_and(a['parts'])} into one path with the path "
                f"module, letting it tidy up the dots, and print the result.", args)
    if want == "resolve":
        return (f"Starting from the absolute folder {a['base']}, resolve the "
                f"pieces {_and(a['rest'])} into a full path with the path "
                f"module, and print it.", args)
    if want == "name":
        return (f"Print the name of the file {a['file']} without its "
                f"extension, using the path module.", args)
    if want == "ext":
        return (f"Print the extension of the file {a['file']}, dot included, "
                f"or the word none when it has no extension.", args)
    if want == "dir":
        return (f"Print the folder that the file {a['file']} sits in, using "
                f"the path module.", args)
    if want == "rel":
        return (f"Print the path that gets you from the folder {a['from']} to "
                f"{a['to']}, using the path module.", args)
    return (f"Print whether the path {a['p']} is absolute, using the path "
            f"module.", args)


PATH_PAGE = _page(
    "js-node-path", 238, "Node: the path module",
    "Node ships with a module for building and taking apart file paths, and "
    "require('node:path') loads it. Never join paths with + and a slash: "
    "path.join handles the separators for you and tidies the dots, so "
    "'..' goes up a level and '.' means here. path.resolve does the same "
    "but returns a full path, working left to right from a folder you "
    "give it. path.basename gives the last piece, path.extname the "
    "extension with its dot (the last one only, so archive.tar.gz gives "
    ".gz, and a name that only starts with a dot, such as .bashrc, has none), "
    "path.dirname the folder, path.relative the way from one path to "
    "another and path.isAbsolute whether it starts at the root. Windows "
    "uses backslashes, so these exercises use require('node:path').posix, "
    "which always writes slashes and prints the same everywhere.",
    "const path = require('node:path').posix; path.join('srv', 'app', '..', "
    "'logs') is srv/logs, and path.basename('/home/ada/notes.txt', "
    "'.txt') is notes; path.extname('/home/ada/notes.txt') is .txt",
    "js_node_path",
    tuple(_path_row(row) for row in _PATHS),
)


# ── 239. Command-line arguments ──────────────────────────────

_ARGV = (
    ("flag", ["node", "app.js", "--name", "Ada", "-v"], {"flag": "name", "default": "Guest"}),
    ("flag", ["node", "app.js", "-v", "--out", "build"], {"flag": "out", "default": "dist"}),
    ("flag", ["node", "server.js", "--verbose"], {"flag": "port", "default": "3000"}),
    ("flag", ["node", "app.js", "input.txt", "--user", "grace"], {"flag": "user", "default": "anon"}),
    ("has", ["node", "app.js", "-v"], {"short": "v", "long": "verbose"}),
    ("has", ["node", "app.js", "input.txt", "--verbose"], {"short": "v", "long": "verbose"}),
    ("has", ["node", "app.js", "--debug", "out.txt"], {"short": "q", "long": "quiet"}),
    ("eq", ["node", "app.js", "--port=8080"], {"key": "port", "op": "next", "default": 3000}),
    ("eq", ["node", "app.js", "-v"], {"key": "port", "op": "double", "default": 3000}),
    ("eq", ["node", "app.js", "--retries=4", "--verbose"], {"key": "retries", "op": "double", "default": 1}),
    ("positional", ["node", "app.js", "-v", "input.txt", "output.txt"], {}),
    ("positional", ["node", "app.js", "copy", "--force", "a.txt", "b.txt", "-q"], {}),
    ("positional", ["node", "tool.js", "--dry-run", "build"], {}),
    ("count", ["node", "app.js", "-v", "-q", "input.txt"], {}),
    ("count", ["node", "app.js", "--force", "--dry-run", "a.txt", "--quiet"], {}),
    ("options", ["node", "app.js", "--name=Ada", "--loud"], {}),
    ("options", ["node", "app.js", "--mode=fast", "--port=8080", "--watch"], {}),
    ("options", ["node", "build.js", "--minify", "--target=es2020"], {}),
    ("sum", ["node", "add.js", "4", "10", "-3"], {}),
    ("sum", ["node", "add.js", "2.5", "0.5", "7"], {}),
)


def _args_row(row):
    want, argv, extra = row
    args = {"want": want, "argv": argv, **extra}
    listing = "[" + ", ".join(f"'{x}'" for x in argv) + "]"
    head = f"Take process.argv to be the array {listing}."
    if want == "flag":
        f, d = extra["flag"], extra["default"]
        return (f"{head} Print the value that follows the --{f} flag, or "
                f"{d} when the flag is not there.", args)
    if want == "has":
        s, long = extra["short"], extra["long"]
        return (f"{head} Print whether the arguments include -{s} or "
                f"--{long}.", args)
    if want == "eq":
        k, op, d = extra["key"], extra["op"], extra["default"]
        what = "plus one" if op == "next" else "doubled"
        return (f"{head} Read the number from the argument written like "
                f"--{k}=NUMBER, using {d} when there is none, and print it "
                f"{what}.", args)
    if want == "positional":
        return (f"{head} Print the arguments after the script that do not "
                f"start with a dash, in order, joined by a comma and a "
                f"space.", args)
    if want == "count":
        return (f"{head} Print how many of the arguments after the script "
                f"are flags, meaning they start with a dash.", args)
    if want == "options":
        return (f"{head} Turn the arguments after the script into an object: "
                f"each argument starts with two dashes, one written "
                f"--key=value gives the key the value as a string, and one "
                f"with no equals sign gives the key true. Print the object "
                f"as JSON.", args)
    return (f"{head} Add up all the numbers after the script and print the "
            f"total.", args)


ARGS_PAGE = _page(
    "js-node-args", 239, "Node: command-line arguments",
    "process.argv is an array of strings: the path of node, the path of the "
    "script, and then everything the user typed after it, so the real "
    "arguments start at index 2 and argv.slice(2) gives them. Nothing is "
    "parsed for you. A flag with a value such as --name Ada is two "
    "separate strings: find the flag with indexOf, and the value is the "
    "element after it, args[i + 1]. A flag with no value is just a string "
    "to test for with includes. The form --port=8080 is one string, so "
    "arg.split('=') pulls it apart, and Number() turns the text into a "
    "number: everything arrives as a string, so Number('10') + Number('4') "
    "is 14 where '10' + '4' is 104. Defaults come from a ternary or ||. "
    "Here the array is written out for you, since a script run without "
    "arguments would have nothing to read.",
    "const argv = ['node', 'app.js', '--name', 'Ada', '-v']; "
    "const args = argv.slice(2); const i = args.indexOf('--name'); "
    "args[i + 1] is Ada, and args.includes('-v') is true",
    "js_node_args",
    tuple(_args_row(row) for row in _ARGV),
)


# ── 240. Reading files ───────────────────────────────────────

_READS = (
    ("count", "fruit.txt", ["apple", "banana", "cherry"], None),
    ("count", "colours.txt", ["red", "green", "blue", "yellow"], None),
    ("count", "greek.txt", ["alpha", "beta", "gamma", "delta", "epsilon"], None),
    ("last", "days.txt", ["Monday", "Tuesday", "Wednesday"], None),
    ("last", "points.txt", ["north", "south", "east", "west"], None),
    ("words", "poem.txt", ["the quick brown fox", "jumps over", "the lazy dog"], None),
    ("words", "list.txt", ["one two", "three four five", "six"], None),
    ("words", "song.txt", ["to be or not", "to be"], None),
    ("longest", "pets.txt", ["cat", "elephant", "dog"], None),
    ("longest", "paint.txt", ["red", "orange", "blue", "green"], None),
    ("longest", "sky.txt", ["sun", "moon", "star", "comet", "sky"], None),
    ("sum", "numbers.txt", ["5", "10", "-3"], None),
    ("sum", "scores.txt", ["100", "250", "75", "25"], None),
    ("sum", "digits.txt", ["7", "8", "9"], None),
    ("find", "shop.txt", ["red apple", "green pear", "yellow banana"], "pear"),
    ("find", "stock.txt", ["red apple", "green pear", "yellow banana"], "plum"),
    ("find", "letters.txt", ["alpha", "beta", "gamma", "delta"], "ta"),
    ("crlf", "windows.txt", ["one", "two", "three"], None),
    ("crlf", "greek.txt", ["alpha", "beta", "gamma", "delta"], None),
    ("crlf", "pets.txt", ["cat", "dog", "bird"], None),
)


def _read_row(row):
    want, file, lines, word = row
    args = {"want": want, "file": file, "lines": lines}
    if word is not None:
        args["word"] = word
    listing = _and(lines)
    put = (f"Write the lines {listing} to the text file {file} in {_TMP}, one "
           f"per line, then read the file back")
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
        return (f"{put}, turn each line into a number, and print the sum of "
                f"them.", args)
    if want == "find":
        return (f"{put} and print the number of the first line that contains "
                f"the text {word}, counting from 1, or 0 when no line "
                f"does.", args)
    return (f"Write the lines {listing} to the text file {file} in {_TMP}, "
            f"with Windows line endings: a carriage return then a newline "
            f"after every line except the last. Read the file back, split it "
            f"on either kind of line ending, and print how many lines there "
            f"are, then the length of the last line.", args)


READ_PAGE = _page(
    "js-node-read", 240, "Node: reading files",
    "require('node:fs') is Node's file system module. fs.readFileSync(file, "
    "'utf8') reads a whole file into a string, and without the 'utf8' you get "
    "a Buffer of raw bytes instead. The usual way to work with lines is "
    "text.split('\\n'): a file that ends with a newline gives an empty last "
    "piece, which trim() removes first. Files made on Windows end their "
    "lines with \\r\\n, and splitting on '\\n' alone would leave a stray \\r "
    "on every line, so split(/\\r?\\n/) copes with both. To keep the "
    "exercises tidy and repeatable, each one works in a folder of its own "
    "from fs.mkdtempSync(path.join(os.tmpdir(), 'cc-')), which makes a "
    "new, empty folder with a random name, and removes it again with "
    "fs.rmSync(dir, { recursive: true }). Never print the folder's path: "
    "it is different every time.",
    "fs.writeFileSync(file, 'apple\\nbanana\\ncherry\\n'); "
    "const lines = fs.readFileSync(file, 'utf8').trim().split('\\n'); "
    "lines.length is 3 and lines.at(-1) is cherry",
    "js_node_read",
    tuple(_read_row(row) for row in _READS),
)


# ── 241. Writing files ───────────────────────────────────────

_WRITES = (
    ("append_count", {"first": "one", "more": ["two", "three"]}),
    ("append_count", {"first": "start", "more": ["middle"]}),
    ("append_count", {"first": "a", "more": ["b", "c", "d"]}),
    ("append_text", {"first": "Hello", "more": [", ", "world"]}),
    ("append_text", {"first": "ab", "more": ["cd", "ef"]}),
    ("append_text", {"first": "2024", "more": ["-10", "-05"]}),
    ("append_text", {"first": "node", "more": [".", "js"]}),
    ("overwrite", {"texts": ["version one", "version two"]}),
    ("overwrite", {"texts": ["red", "green", "blue"]}),
    ("overwrite", {"texts": ["hello world", "hi"]}),
    ("size", {"text": "hello world"}),
    ("size", {"text": "café"}),
    ("size", {"text": "日本"}),
    ("size", {"text": "ok \U0001F642"}),
    ("steps", {"steps": ["check", "write", "check"]}),
    ("steps", {"steps": ["write", "check", "delete", "check"]}),
    ("steps", {"steps": ["check", "write", "delete", "check"]}),
    ("steps", {"steps": ["check", "write", "check", "delete"]}),
    ("rename", {"file": "draft.txt", "moved": "final.txt", "text": "hello"}),
    ("rename", {"file": "a.txt", "moved": "b.txt", "text": "copy me"}),
)

_STEP_WORDS = {
    "check": "print whether it exists",
    "write": "write the text data to it",
    "delete": "delete it",
}


def _write_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "append_count":
        first, more = a["first"], a["more"]
        return (f"In {_TMP}, write the line {first} to a file, add the "
                f"{'line' if len(more) == 1 else 'lines'} {_and(more)} to the "
                f"end of it with appendFileSync, one at a time, then read "
                f"the file back and print how many lines it has.", args)
    if want == "append_text":
        first, more = a["first"], a["more"]
        pieces = _and(f"'{m}'" for m in more)
        return (f"In {_TMP}, write the text '{first}' to a file, then append "
                f"{pieces} to it one at a time, adding no newlines, and "
                f"print the whole text of the file.", args)
    if want == "overwrite":
        texts = a["texts"]
        again = _then(f"'{t}'" for t in texts[1:])
        return (f"In {_TMP}, write the text '{texts[0]}' to a file, then "
                f"write {again} to the same file with writeFileSync each "
                f"time, and print what the file holds at the end.", args)
    if want == "size":
        return (f"In {_TMP}, write the text '{a['text']}' to a file, then "
                f"use statSync to print the file's size in bytes.", args)
    if want == "steps":
        todo = _then(_STEP_WORDS[s] for s in a["steps"])
        return (f"In {_TMP}, take a file path inside it, and with nothing "
                f"written yet: {todo}.", args)
    return (f"In {_TMP}, write the text '{a['text']}' to the file "
            f"{a['file']}, rename the file to {a['moved']} with renameSync, "
            f"then print whether {a['file']} still exists, then the text "
            f"of {a['moved']}.", args)


WRITE_PAGE = _page(
    "js-node-write", 241, "Node: writing files",
    "fs.writeFileSync(file, text) creates the file, or replaces whatever "
    "was there: writing twice leaves only the second text. "
    "fs.appendFileSync(file, text) adds to the end instead and makes the "
    "file if it is missing, but it adds exactly what you give it, so a "
    "line needs its own '\\n' on the end. fs.existsSync(file) answers true "
    "or false without throwing, fs.renameSync(old, new) moves a file and "
    "fs.unlinkSync(file) deletes one, throwing if it is not there. "
    "fs.statSync(file).size is the size in bytes, which is not the number "
    "of characters: é takes two bytes, 日 three and an emoji four, because "
    "files hold UTF-8. Every program here writes inside a folder from "
    "mkdtempSync, so nothing is left lying about, and rmSync with "
    "{ recursive: true } clears the folder away at the end.",
    "fs.writeFileSync(file, 'one\\n'); fs.appendFileSync(file, 'two\\n'); "
    "reading the file back gives two lines, and fs.statSync(file).size is 8",
    "js_node_write",
    tuple(_write_row(row) for row in _WRITES),
)


# ── 242. JSON on disk ────────────────────────────────────────

_JSONS = (
    ("field", {"obj": {"name": "Ada", "age": 36}, "key": "age"}),
    ("field", {"obj": {"title": "Dune", "year": 1965, "read": True}, "key": "read"}),
    ("field", {"obj": {"city": "Oslo", "pop": 709000}, "key": "city"}),
    ("update", {"obj": {"count": 5}, "key": "count", "step": 3}),
    ("update", {"obj": {"name": "Ada", "score": 10}, "key": "score", "step": 5}),
    ("update", {"obj": {"visits": 99}, "key": "visits", "step": 1}),
    ("pretty", {"obj": {"name": "Ada", "langs": ["js", "py"]}}),
    ("pretty", {"obj": {"id": 7, "tags": ["a", "b", "c"], "ok": True}}),
    ("pretty", {"obj": {"team": "blue", "scores": [3, 5]}}),
    ("total", {"items": [("pen", 3, 4), ("ink", 8, 2), ("pad", 5, 3)]}),
    ("total", {"items": [("bolt", 2, 50), ("nut", 1, 80), ("washer", 1, 30)]}),
    ("names", {"items": [("pen", 3, 4), ("ink", 8, 2), ("pad", 5, 3), ("lamp", 20, 1)], "limit": 4}),
    ("names", {"items": [("tea", 2, 10), ("cake", 6, 1), ("jam", 4, 2)], "limit": 3}),
    ("default", {"key": "theme", "default": "light", "saved": None}),
    ("default", {"key": "theme", "default": "light", "saved": "dark"}),
    ("default", {"key": "lang", "default": "en", "saved": "fr"}),
    ("safe", {"text": '{ "a": 1, "b": [true, null] }'}),
    ("safe", {"text": '{"a":1,}'}),
    ("safe", {"text": "[1, 2, 3]"}),
    ("safe", {"text": '{name: "Ada"}'}),
)


def _say(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _describe(obj: dict) -> str:
    parts = []
    for k, v in obj.items():
        if isinstance(v, list):
            parts.append(f"{k} as the array {_and(_say(x) for x in v)}")
        else:
            parts.append(f"{k} {_say(v)}")
    return _and(parts)


def _json_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "field":
        return (f"In {_TMP}, save an object with {_describe(a['obj'])} to a "
                f"JSON file, load it back with JSON.parse, and print its "
                f"{a['key']}.", args)
    if want == "update":
        obj = a["obj"]
        return (f"In {_TMP}, save an object with {_describe(obj)} to a JSON "
                f"file. Load it, add {a['step']} to its {a['key']}, save it "
                f"again, and print the text of the file.", args)
    if want == "pretty":
        return (f"In {_TMP}, save an object with {_describe(a['obj'])} to a "
                f"JSON file indented with two spaces, and print the text of "
                f"the file.", args)
    if want in ("total", "names"):
        things = _and(f"{n} at {p} each, {q} of them" for n, p, q in a["items"])
        base = (f"In {_TMP}, save an array of objects, each with a name, a "
                f"price and a qty: {things}, to a JSON file, and load it "
                f"back.")
        if want == "total":
            return (f"{base} Print the total cost, the sum of price times "
                    f"qty.", args)
        return (f"{base} Print the names of the items that cost more than "
                f"{a['limit']}, in order, joined by a comma and a space.",
                args)
    if want == "default":
        key, d, s = a["key"], a["default"], a["saved"]
        have = (f"First save an object with {key} {s} to a JSON file named "
                f"settings.json. " if s is not None else
                "No settings.json file has been written. ")
        return (f"In {_TMP}, start with the settings object with {key} {d}. "
                f"{have}If settings.json exists, load it in place of the "
                f"defaults. Print the {key}.", args)
    return (f"Parse the text {a['text']} as JSON inside a try block. When it "
            f"parses, print the data written back out with JSON.stringify; "
            f"when parsing throws, print the word invalid.", args)


JSON_PAGE = _page(
    "js-node-json", 242, "Node: JSON on disk",
    "A file only holds text, so an object has to be turned into text to be "
    "saved: JSON.stringify(object) makes the text, and JSON.parse(text) "
    "turns it back into an object. Together with readFileSync and "
    "writeFileSync that is a save file in two lines. To change one field, "
    "read the file, change the object, then write the whole thing back. "
    "JSON.stringify(object, null, 2) indents the text with two spaces per "
    "level, which suits a file people will read. JSON is strict, much "
    "stricter than a JavaScript object: keys need double quotes, strings "
    "cannot use single quotes and nothing may end with a trailing comma. "
    "JSON.parse throws a SyntaxError on a bad text, so wrap it in try/catch "
    "when the text came from outside. fs.existsSync(file) lets a program "
    "fall back to defaults the first time it runs, before anything has "
    "been saved.",
    "fs.writeFileSync(file, JSON.stringify({ count: 5 })); the file now "
    "holds {\"count\":5}, and JSON.parse(fs.readFileSync(file, 'utf8')).count "
    "is 5; JSON.parse('{\"a\":1,}') throws",
    "js_node_json",
    tuple(_json_row(row) for row in _JSONS),
)


# ── 243. Directories ─────────────────────────────────────────

_DIRS = (
    ("list", {"names": ["b.txt", "c.txt", "a.txt"]}),
    ("list", {"names": ["zebra.md", "apple.md", "mango.md", "kiwi.md"]}),
    ("list", {"names": ["file10.txt", "file2.txt", "file1.txt"]}),
    ("list", {"names": ["readme.md", "index.js", "app.js", "style.css"]}),
    ("ext", {"names": ["a.js", "b.txt", "c.js", "d.md"], "ext": "js"}),
    ("ext", {"names": ["notes.txt", "app.js", "todo.txt", "main.py", "log.txt"], "ext": "txt"}),
    ("extcount", {"names": ["index.html", "style.css", "app.js", "about.html"], "ext": "html"}),
    ("extcount", {"names": ["a.png", "b.jpg", "c.png", "d.png", "e.gif"], "ext": "png"}),
    ("size", {"files": {"a.txt": "hello", "b.txt": "hi", "c.txt": "abc"}}),
    ("size", {"files": {"one.txt": "x", "two.txt": "yy", "three.txt": "zzz"}}),
    ("size", {"files": {"big.log": "lorem ipsum dolor", "small.log": "ok", "mid.log": "sit amet"}}),
    ("size", {"files": {"a.txt": "12345", "b.txt": "1234567890", "c.txt": "12"}}),
    ("dirs", {"names": ["a.txt", "src/", "b.txt", "docs/"]}),
    ("dirs", {"names": ["lib/", "readme.md", "test/", "index.js", "bin/"]}),
    ("files", {"names": ["a.txt", "src/", "b.txt", "docs/"]}),
    ("files", {"names": ["lib/", "readme.md", "test/", "index.js", "bin/"]}),
    ("delete", {"names": ["a.txt", "b.txt", "c.txt", "d.txt"], "gone": ["b.txt"]}),
    ("delete", {"names": ["one.js", "two.js", "three.js", "four.js", "five.js"], "gone": ["two.js", "four.js"]}),
    ("delete", {"names": ["x.log", "y.log", "z.log", "w.log"], "gone": ["x.log", "z.log"]}),
    ("delete", {"names": ["a.md", "b.md", "c.md", "d.md", "e.md"], "gone": ["a.md"]}),
)


def _dirs_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "list":
        return (f"In {_TMP}, make empty files called {_and(a['names'])}. "
                f"Print the names in the folder in alphabetical order, joined "
                f"by a comma and a space.", args)
    if want in ("ext", "extcount"):
        made = f"In {_TMP}, make empty files called {_and(a['names'])}."
        if want == "ext":
            return (f"{made} Print the names in the folder that end in "
                    f".{a['ext']}, in alphabetical order, joined by a comma "
                    f"and a space.", args)
        return (f"{made} Print how many names in the folder end in "
                f".{a['ext']}.", args)
    if want == "size":
        things = _and(f"{n} holding the text '{t}'" for n, t in a["files"].items())
        return (f"In {_TMP}, make the files {things}. Print the total size "
                f"of all the files in the folder, in bytes.", args)
    if want in ("dirs", "files"):
        folders = _and(n.removesuffix("/") for n in a["names"] if n.endswith("/"))
        plain = _and(n for n in a["names"] if not n.endswith("/"))
        what = "folders" if want == "dirs" else "files"
        return (f"In {_TMP}, make the empty files {plain} and the empty "
                f"folders {folders}. Ask readdirSync for the entries with "
                f"their types, and print the names of the {what} in "
                f"alphabetical order, joined by a comma and a space.", args)
    return (f"In {_TMP}, make empty files called {_and(a['names'])}, then "
            f"delete {_and(a['gone'])} with unlinkSync. Print the names "
            f"left in the folder in alphabetical order, joined by a comma "
            f"and a space.", args)


DIRS_PAGE = _page(
    "js-node-dirs", 243, "Node: directories",
    "fs.mkdirSync(folder) makes a folder, and fs.readdirSync(folder) lists "
    "the names inside it, just the names, not full paths. The list has no "
    "promised order, because the operating system decides it, so call "
    ".sort() before printing anything you want to be the same every time: "
    "sort puts text in code-unit order, so 'file10.txt' lands before "
    "'file2.txt', since 1 comes before 2. To tell files from folders, "
    "readdirSync(folder, { withFileTypes: true }) returns entries that have "
    "a name and answer isDirectory() and isFile(). fs.statSync(file).size "
    "gives a file's size in bytes, so adding the sizes of every name in a "
    "folder is a map and a reduce. path.join(dir, name) builds the full path "
    "for each call, and fs.unlinkSync(file) removes a file. The folder from "
    "mkdtempSync starts empty, so the listing holds exactly what the program "
    "made.",
    "for (const name of ['b.txt', 'a.txt']) fs.writeFileSync("
    "path.join(dir, name), ''); fs.readdirSync(dir).sort().join(', ') is "
    "a.txt, b.txt",
    "js_node_dirs",
    tuple(_dirs_row(row) for row in _DIRS),
)


# ── 244. Events, timers and streams ──────────────────────────

_EVENTS = (
    ("log", {"event": "greet", "word": "Hello", "names": ["Ada", "Linus"]}),
    ("log", {"event": "join", "word": "Welcome", "names": ["Grace", "Alan", "Edsger"]}),
    ("two", {"event": "ping", "labels": ["first", "second"], "prepend": False, "times": 1}),
    ("two", {"event": "save", "labels": ["saved to disk", "logged"], "prepend": False, "times": 2}),
    ("two", {"event": "boot", "labels": ["database", "cache"], "prepend": True, "times": 1}),
    ("count", {"event": "tick", "mode": "on", "n": 3}),
    ("count", {"event": "tick", "mode": "once", "n": 3}),
    ("count", {"event": "hit", "mode": "once", "n": 5}),
    ("returns", {"event": "save", "mode": "on", "emits": ["save", "load"]}),
    ("returns", {"event": "ready", "mode": "once", "emits": ["ready", "ready"]}),
    ("sum", {"event": "add", "numbers": [3, 4, 5]}),
    ("sum", {"event": "score", "numbers": [10, -4, 7, 1]}),
    ("cart", {"event": "buy", "sales": [(3, 2), (5, 1), (10, 4)]}),
    ("cart", {"event": "sale", "sales": [(2, 2), (7, 3)]}),
    ("timers", {"jobs": [("a", 30), ("b", 10), ("c", 20)], "sync": "scheduled"}),
    ("timers", {"jobs": [("cook", 50), ("chop", 20), ("serve", 70)], "sync": "ready"}),
    ("timers", {"jobs": [("x", 60), ("y", 0), ("z", 30)], "sync": "start"}),
    ("upper", {"chunks": ["he", "llo", " world"]}),
    ("count_chunks", {"chunks": ["a", "bb", "ccc", "dddd"]}),
    ("length", {"chunks": ["abc", "de", "f"]}),
)


def _events_row(row):
    want, a = row
    args = {"want": want, **a}
    ev = a.get("event")
    if want == "log":
        return (f"Make an EventEmitter with a listener for the {ev} event "
                f"that prints the word {a['word']}, a comma and a space, the "
                f"name it is given and an exclamation mark. Emit {ev} once "
                f"for each of {_and(a['names'])}, in that order.", args)
    if want == "two":
        one, two = a["labels"]
        n = a["times"]
        how = ("The second is added with prependListener, so it goes first. "
               if a["prepend"] else "")
        return (f"Make an EventEmitter with two listeners for the {ev} event: "
                f"one added first that prints {one}, and one added second "
                f"that prints {two}. {how}Emit {ev} "
                f"{'once' if n == 1 else f'{n} times'}.", args)
    if want == "count":
        how = "once" if a["mode"] == "once" else "on"
        return (f"Make an EventEmitter and count how many times a listener "
                f"added with {how} runs for the {ev} event, then emit {ev} "
                f"{a['n']} times and print the count.", args)
    if want == "returns":
        first = a["emits"]
        how = "once" if a["mode"] == "once" else "on"
        return (f"Make an EventEmitter with an empty listener for the {ev} "
                f"event, added with {how}. For each of {_and(first)}, in "
                f"order, emit the event and print what emit returns.", args)
    if want == "sum":
        return (f"Make an EventEmitter that keeps a running total: each time "
                f"the {ev} event fires with a number, the number is added "
                f"on. Emit {ev} for {_and(a['numbers'])}, and print the "
                f"total.", args)
    if want == "cart":
        sales = _and(f"{p} and {q}" for p, q in a["sales"])
        return (f"Make an EventEmitter that keeps a running total: each time "
                f"the {ev} event fires with a price and a quantity, the price "
                f"times the quantity is added on. Emit {ev} with {sales}, "
                f"and print the total.", args)
    if want == "timers":
        jobs = _and(f"{label} after {ms} ms" for label, ms in a["jobs"])
        return (f"Schedule timers with setTimeout that each print their "
                f"label: {jobs}. Straight after scheduling them, print the "
                f"word {a['sync']}.", args)
    chunks = _and(f"'{c}'" for c in a["chunks"])
    base = f"Make a readable stream from the array of chunks {chunks} with Readable.from."
    if want == "upper":
        return (f"{base} Join the chunks as they arrive in its data events, "
                f"and when it ends, print the text in capital letters.", args)
    if want == "count_chunks":
        return (f"{base} Count its data events, and when it ends, print how "
                f"many there were.", args)
    return (f"{base} Add up the length of each chunk as it arrives in its "
            f"data events, and when it ends, print the total.", args)


EVENTS_PAGE = _page(
    "js-node-events", 244, "Node: events, timers and streams",
    "Much of Node is built on events. new EventEmitter() from "
    "require('node:events') makes an object with on(name, listener), which "
    "registers a function, and emit(name, ...args), which calls every "
    "listener for that name, in the order they were added, passing along "
    "the extra arguments. once is on for a single call, prependListener "
    "adds to the front of the line, and emit returns true if anyone was "
    "listening and false if nobody was. setTimeout(fn, ms) is the same idea "
    "with the clock: the callback runs later, so everything written after "
    "it in the program prints first, and timers fire in order of their "
    "delay, not the order they were created. A readable stream hands over "
    "its content a piece at a time as 'data' events and finishes with an "
    "'end' event: Readable.from(array) turns an array into one, and a data "
    "listener sees each element as a chunk.",
    "const emitter = new EventEmitter(); emitter.on('greet', (name) => "
    "console.log(`Hello, ${name}!`)); emitter.emit('greet', 'Ada') prints "
    "Hello, Ada!; setTimeout(() => console.log('later'), 10) then "
    "console.log('now') prints now, then later",
    "js_node_events",
    tuple(_events_row(row) for row in _EVENTS),
)


# ── 245. Environment and exit codes ──────────────────────────

_ENVS = (
    ("port", {"env": {"PORT": "8080", "HOST": "localhost"}, "default": 3000}),
    ("port", {"env": {"HOST": "localhost"}, "default": 3000}),
    ("port", {"env": {"PORT": "", "MODE": "dev"}, "default": 4000}),
    ("flag", {"env": {"DEBUG": "true", "NAME": "ada"}, "key": "DEBUG"}),
    ("flag", {"env": {"DEBUG": "1"}, "key": "DEBUG"}),
    ("flag", {"env": {"NAME": "ada", "SHELL": "bash"}, "key": "VERBOSE"}),
    ("mode", {"env": {"NODE_ENV": "production"}, "key": "NODE_ENV", "default": "development"}),
    ("mode", {"env": {"HOME": "ada"}, "key": "NODE_ENV", "default": "development"}),
    ("mode", {"env": {"LOG_LEVEL": ""}, "key": "LOG_LEVEL", "default": "info"}),
    ("list", {"env": {"TAGS": "red,green,blue"}}),
    ("list", {"env": {"TAGS": "solo"}}),
    ("list", {"env": {"USER": "ada"}}),
    ("exit", {"rule": "even", "input": 7}),
    ("exit", {"rule": "even", "input": 8}),
    ("exit", {"rule": "positive", "input": -2}),
    ("exit", {"rule": "small", "input": 250}),
    ("exit", {"rule": "small", "input": 42}),
    ("onexit", {"lines": ["one", "two"], "timer": None}),
    ("onexit", {"lines": ["start", "end"], "timer": "timer"}),
    ("onexit", {"lines": ["a", "b", "c"], "timer": None}),
)

_RULE_TEXT = {
    "even": ("an even number", "must be even"),
    "positive": ("a number above zero", "must be positive"),
    "small": ("a number under 100", "must be under 100"),
}


def _env_say(env: dict) -> str:
    return "{ " + ", ".join(
        f"{k}: '{v}'" for k, v in env.items()) + " }"


def _env_row(row):
    want, a = row
    args = {"want": want, **a}
    if want in ("port", "flag", "mode", "list"):
        env = _env_say(a["env"])
        head = f"Take process.env to be the object {env}."
    if want == "port":
        return (f"{head} Print the PORT as a number, using {a['default']} "
                f"when it is missing or empty.", args)
    if want == "flag":
        return (f"{head} Print whether {a['key']} is exactly the text "
                f"true.", args)
    if want == "mode":
        return (f"{head} Print the text {a['key']} is, a space, and the "
                f"value of {a['key']}, or {a['default']} when it is missing "
                f"or empty.", args)
    if want == "list":
        return (f"{head} TAGS, when it is there, is a list separated by "
                f"commas. Print how many tags there are (none when it is "
                f"missing), then the tags joined by a space, a bar and a "
                f"space, or the word none when there are no tags.", args)
    if want == "exit":
        kind, message = _RULE_TEXT[a["rule"]]
        return (f"A program is given the number {a['input']}, and needs {kind}. "
                f"Throw an Error with the message '{message}' when it is "
                f"not, and catch it, setting a variable called code to 1; "
                f"otherwise code stays 0. Print ok and the number when all "
                f"is well, or error: and the message when it is not, then "
                f"print the words exit code and the value of code.", args)
    lines = a["lines"]
    timer = a["timer"]
    extra = (f" Also schedule a timer of 5 ms that prints {timer}." if timer else "")
    return (f"Register a listener for the process's exit event that prints "
            f"the word bye, a space and the exit code it is given, and "
            f"then print {_and(lines)} in order.{extra}", args)


ENV_PAGE = _page(
    "js-node-env", 245, "Node: environment and exit codes",
    "process.env is an object of the environment variables the program "
    "started with. Every value is a string, and a variable that was never "
    "set is undefined, so a default is written env.PORT || 3000; || also "
    "replaces an empty string, which is usually what you want, where ?? "
    "would keep it. Convert with Number() when a number is needed, and "
    "compare with === 'true' for a flag, since the text 'false' is truthy. "
    "A program tells the system how it went through its exit code: 0 means "
    "success and anything else means failure. Code that throws an Error "
    "can be caught with try/catch, and the catch decides what to print and "
    "which code to use: process.exitCode = 1 sets it, and the program "
    "then ends by itself once its work is done. process.on('exit', fn) "
    "runs fn last of all, after every other line and timer, and is given "
    "the code. Because these exercises must finish with code 0, they print "
    "the code instead of setting it.",
    "const env = { PORT: '8080' }; Number(env.PORT || 3000) is 8080, and "
    "with no PORT it is 3000; process.on('exit', (code) => "
    "console.log(`bye ${code}`)) prints bye 0 after everything else",
    "js_node_env",
    tuple(_env_row(row) for row in _ENVS),
)


# ── 246. A small server ──────────────────────────────────────

_HTTPS = (
    ("body", {"status": 201, "text": "created"}),
    ("body", {"status": 404, "text": "no such page"}),
    ("body", {"status": 200, "text": "hello"}),
    ("body", {"status": 418, "text": "short and stout"}),
    ("header", {"header": "X-Greeting", "value": "hello", "text": "ok"}),
    ("header", {"header": "Content-Type", "value": "text/plain", "text": "hi there"}),
    ("header", {"header": "X-Mood", "value": "calm", "text": "done"}),
    ("header", {"header": "Content-Type", "value": "text/html", "text": "page"}),
    ("json", {"obj": {"name": "Ada", "age": 36}, "key": "name"}),
    ("json", {"obj": {"ok": True, "count": 3}, "key": "ok"}),
    ("json", {"obj": {"city": "Oslo", "pop": 709000}, "key": "pop"}),
    ("json", {"obj": {"title": "Dune", "year": 1965}, "key": "year"}),
    ("method", {"method": "GET", "path": "/"}),
    ("method", {"method": "POST", "path": "/items"}),
    ("method", {"method": "PUT", "path": "/items/7"}),
    ("method", {"method": "DELETE", "path": "/items/7?force=1"}),
    ("count", {"start": 0, "n": 3}),
    ("count", {"start": 10, "n": 2}),
    ("count", {"start": 100, "n": 4}),
    ("count", {"start": 0, "n": 5}),
)

_SERVE = ("Start a server with http.createServer on port 0 of 127.0.0.1 "
          "(let the system choose the port), ")


def _http_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "body":
        return (f"{_SERVE}that answers every request with the status "
                f"{a['status']} and the text '{a['text']}'. Once it is "
                f"listening, use fetch to ask it for its address, print the "
                f"status and then the body text, and close the server.", args)
    if want == "header":
        return (f"{_SERVE}that answers every request with the header "
                f"{a['header']} set to '{a['value']}' and the body text "
                f"'{a['text']}'. Once it is listening, use fetch to ask it "
                f"for its address, print the value of that header and then "
                f"the body text, and close the server.", args)
    if want == "json":
        return (f"{_SERVE}that answers every request with the object "
                f"{_describe(a['obj'])} as JSON, with the content type set "
                f"to application/json. Once it is listening, use fetch to ask "
                f"it for its address, read the body as JSON, print its "
                f"{a['key']}, and close the server.", args)
    if want == "method":
        how = (f"with the {a['method']} method" if a["method"] != "GET"
               else "with an ordinary GET")
        return (f"{_SERVE}that answers every request with the request's "
                f"method, a space and the request's url. Once it is "
                f"listening, use fetch to ask it for {a['path']} {how}, "
                f"print the answer, and close the server.", args)
    return (f"{_SERVE}that keeps a counter starting at {a['start']} and "
            f"answers every request by adding one to it and sending back the "
            f"new value. Once it is listening, use fetch {a['n']} times in a "
            f"row, one after the other, print the answers on one line "
            f"joined by a comma and a space, and close the server.", args)


HTTP_PAGE = _page(
    "js-node-http", 246, "Node: a small server",
    "require('node:http').createServer(handler) makes a web server. The "
    "handler runs once per request and is given the request, with "
    "req.method and req.url, and the response: res.writeHead(status, "
    "headers) sets the status and any headers, and res.end(text) sends the "
    "body and finishes. server.listen(0, '127.0.0.1', callback) asks the "
    "system for any free port, so nothing clashes, and server.address()"
    ".port says which it was. Since Node 18 the fetch function is built "
    "in, so a program can call its own server: fetch gives back a promise "
    "of a response with .status, .headers.get('name') (names in lower "
    "case), .text() and .json(), each of which also returns a promise, so "
    "they are awaited inside an async function. Finish with "
    "server.close(), or the program never ends. Stay on 127.0.0.1: that "
    "address cannot be reached from outside the machine.",
    "const server = http.createServer((req, res) => res.end('hi')); "
    "server.listen(0, '127.0.0.1', async () => { const res = await "
    "fetch(`http://127.0.0.1:${server.address().port}/`); "
    "console.log(res.status, await res.text()); server.close(); }) prints "
    "200 hi",
    "js_node_http",
    tuple(_http_row(row) for row in _HTTPS),
)


# ── 247. Routes ──────────────────────────────────────────────

_ROUTES = (
    ("greet", {"fallback": "stranger", "path": "/hello?name=Ada"}),
    ("greet", {"fallback": "friend", "path": "/hello?name=Ada%20Lovelace"}),
    ("greet", {"fallback": "guest", "path": "/hello"}),
    ("greet", {"fallback": "stranger", "path": "/goodbye?name=Ada"}),
    ("sum", {"keys": ["a", "b"], "op": "+", "x": 2, "y": 3}),
    ("sum", {"keys": ["x", "y"], "op": "*", "x": 4, "y": 6}),
    ("sum", {"keys": ["a", "b"], "op": "-", "x": 10, "y": 4}),
    ("sum", {"keys": ["n", "m"], "op": "+", "x": -5, "y": 2}),
    ("pages", {"pages": [("/", "home"), ("/about", "about us")], "path": "/about"}),
    ("pages", {"pages": [("/", "home"), ("/about", "about us")], "path": "/team"}),
    ("pages", {"pages": [("/hello", "Hi!"), ("/bye", "Goodbye!")], "path": "/bye?lang=en"}),
    ("pages", {"pages": [("/docs", "read the docs"), ("/blog", "read the blog")], "path": "/"}),
    ("method", {"allowed": "POST", "sent": "GET", "ok": "saved"}),
    ("method", {"allowed": "POST", "sent": "POST", "ok": "saved"}),
    ("method", {"allowed": "DELETE", "sent": "DELETE", "ok": "removed"}),
    ("post", {"reply": "upper", "body": "hello"}),
    ("post", {"reply": "length", "body": "hello world"}),
    ("post", {"reply": "reverse", "body": "stressed"}),
    ("post", {"reply": "words", "body": "the quick brown fox"}),
    ("post", {"reply": "upper", "body": "node js"}),
)

_REPLIES = {
    "upper": "answers with that body in capital letters",
    "length": "answers with the number of characters in that body",
    "reverse": "answers with that body spelled backwards",
    "words": "answers with the number of words in that body, counting "
             "the gaps between single spaces",
}

_ASK = ("Once it is listening, use fetch to ask it for ")


def _routes_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "greet":
        return (f"Start a server on port 0 of 127.0.0.1 that answers the "
                f"path /hello with Hello, a comma, a space, the value of the "
                f"name query parameter and an exclamation mark, or the word "
                f"{a['fallback']} when there is no name, and answers any "
                f"other path with the status 404 and the text not found. "
                f"{_ASK}{a['path']}, print the status and then the text, and "
                f"close the server.", args)
    if want == "sum":
        x, y = a["keys"]
        verb = {"+": "sum", "-": "difference", "*": "product"}[a["op"]]
        order = "first minus the second" if a["op"] == "-" else "of the two"
        return (f"Start a server on port 0 of 127.0.0.1 that reads the query "
                f"parameters {x} and {y} as numbers, and answers with JSON "
                f"holding their {verb} {order} as result, with the content "
                f"type set to application/json. {_ASK}"
                f"/calc?{x}={a['x']}&{y}={a['y']}, print the content type, "
                f"then the result from the JSON, and close the server.", args)
    if want == "pages":
        (p1, t1), (p2, t2) = a["pages"]
        return (f"Start a server on port 0 of 127.0.0.1 that answers the "
                f"path {p1} with the text '{t1}', the path {p2} with the "
                f"text '{t2}' (ignoring any query string), and every other "
                f"path with the status 404 and the text not found. "
                f"{_ASK}{a['path']}, print the status and then the text, "
                f"and close the server.", args)
    if want == "method":
        allowed, sent, ok = a["allowed"], a["sent"], a["ok"]
        return (f"Start a server on port 0 of 127.0.0.1 that answers a "
                f"{allowed} request with the text '{ok}', and any other "
                f"method with the status 405 and the text use {allowed}. "
                f"{_ASK}/items with a {sent} request, print the status and "
                f"then the text, and close the server.", args)
    return (f"Start a server on port 0 of 127.0.0.1 that reads the whole "
            f"body of each request and {_REPLIES[a['reply']]}. {_ASK}its "
            f"address with a POST request whose body is the text "
            f"'{a['body']}', print the answer, and close the server.", args)


ROUTES_PAGE = _page(
    "js-node-routes", 247, "Node: routes and requests",
    "A server decides what to do from the request. req.url holds the path "
    "and the query string together, such as /hello?name=Ada, so new "
    "URL(req.url, 'http://x') splits them: the second argument is only a "
    "base, because a request's url has no host. url.pathname is /hello, "
    "and url.searchParams.get('name') is Ada, decoded, so %20 and + both "
    "come out as spaces, and null when the parameter is missing. A route is "
    "an if on the pathname, and the last lines, after every if, answer "
    "everything else with res.writeHead(404): return after answering so "
    "the code below does not run as well. req.method says GET or POST, "
    "and a 405 answer means the method is wrong for that route. A request "
    "body arrives in chunks, so collect them with for await (const chunk of "
    "req) body += chunk before using the text. On the other side, fetch(url, "
    "{ method: 'POST', body: 'text' }) sends one.",
    "createServer((req, res) => { const { pathname, searchParams } = new "
    "URL(req.url, 'http://x'); if (pathname !== '/hello') return "
    "res.writeHead(404).end('not found'); res.end(`Hello, "
    "${searchParams.get('name')}!`); }) answers /hello?name=Ada with "
    "Hello, Ada! and /nope with 404",
    "js_node_routes",
    tuple(_routes_row(row) for row in _ROUTES),
)


JSNODE_PAGES: tuple[Page, ...] = (
    PATH_PAGE,
    ARGS_PAGE,
    READ_PAGE,
    WRITE_PAGE,
    JSON_PAGE,
    DIRS_PAGE,
    EVENTS_PAGE,
    ENV_PAGE,
    HTTP_PAGE,
    ROUTES_PAGE,
)
