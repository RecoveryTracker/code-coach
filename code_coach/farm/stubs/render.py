"""Turn a player's program into files a real Python, Node or Dart process runs.

A program is one or more files, each with a name - main, utils - and the
one that runs, the entry. The files import each other the way their
language does (import utils / import { f } from "./utils.js" /
import 'utils.dart';), and every one of them sees the farm's names without
importing anything.

The farm's three libraries sit beside this file - farm_api.py, farm_api.js
and farm_api.dart - each with a NAMES block that is nearly empty in the
file itself. prepare() fills that block from data.py and protocol.py every
time a program starts, so the names a program sees are always the farm's
own: an entity added to data.py is in all three languages the next time
anyone presses Run, and no name can be spelled one way here and another
way there.

What comes back is everything the runner needs and nothing it has to know
about a particular language: the files to write into an empty folder (as
UTF-8; a path may have a folder in it), the command to run in that folder,
and where each of the player's files went, so an error can point at their
file and line. Each file keeps every line where the player wrote it.

The same files and command start every drone of a run, too: the runner
only adds FARM_DRONE (and, for JavaScript, FARM_TS) to the environment.
Dart is the one language that needs a word here first - see dart_runner().
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path

from code_coach.engine import dart_path
from code_coach.farm import data, protocol

#: "original" is the game's own language, run by farm_lang.py (an interpreter
#: that charges ticks for every operation, as the game does).
LANGUAGES = ("original", "python", "javascript", "dart")

_HERE = Path(__file__).resolve().parent

#: What a file of the player's can be called: lowercase letters, digits and
#: _, not starting with a digit. Lowercase, because Windows can't tell
#: Utils.py from utils.py; and every such name is a name each language can
#: import a file by.
FILE_NAME = re.compile(r"[a-z_][a-z0-9_]*")

#: Names the farm's own files have beside the player's, which no file of
#: the player's can take: farm_api (the library), runner (runner.dart) and
#: package (JavaScript's package.json).
RESERVED_NAMES = frozenset({"farm_api", "runner", "package"})


def program_files(files: Mapping[str, str] | str, entry: str = "main") -> dict[str, str]:
    """A program's files as {name: code}, checked. A plain string is a
    program of one file, main. Raises ValueError, in words a player can
    read, for a name a file can't have or an entry that isn't one of them."""
    if isinstance(files, str):
        files = {"main": files}
    program: dict[str, str] = {}
    for name, code in files.items():
        if not isinstance(name, str) or not FILE_NAME.fullmatch(name):
            raise ValueError(f"{name!r} can't be the name of a file: use lowercase letters, digits "
                             "and _, and don't start with a digit.")
        if name in RESERVED_NAMES:
            raise ValueError(f"{name!r} is the name of one of the farm's own files: call yours "
                             "something else.")
        if not isinstance(code, str):
            raise ValueError(f"The file {name!r} should hold text.")
        program[name] = code
    if entry not in program:
        raise ValueError(f"There is no file called {entry!r} to run.")
    return program


class MissingRuntime(RuntimeError):
    """The language's own program - node, or dart - is not installed here."""


def _groups() -> dict[str, tuple[str, ...]]:
    """Each group of named values, in the order the libraries declare them."""
    return {
        "Entities": tuple(data.ENTITIES),
        "Items": tuple(data.ITEMS),
        "Grounds": tuple(data.GROUNDS),
        "Unlocks": tuple(data.UNLOCKS),
        "Hats": tuple(data.HATS),
    }


# ── The NAMES block, per language ───────────────────────────────────────
#
# JSON is used for the lists because a JSON list of strings is a list in
# Python and an array in JavaScript as it stands.


def _python_names() -> str:
    """The game's own spellings: farm_api.py builds Items.Weird_Substance from these."""
    groups = "".join(
        f"    {json.dumps(title)}: {json.dumps(list(members))},\n"
        for title, members in _groups().items()
    )
    return (
        f"DIRECTIONS = {json.dumps(list(data.DIRECTIONS))}\n"
        f"GROUPS = {{\n{groups}}}\n"
        f"FUNCTIONS = {json.dumps([f.py for f in protocol.FUNCTIONS])}"
    )


def _javascript_names() -> str:
    """Each group as {JavaScript name: game name}, and each function as [py, js]."""
    lines = [f"const DIRECTIONS = {json.dumps(list(data.DIRECTIONS))};", "const GROUPS = {"]
    for title, members in _groups().items():
        spelled = {protocol.js_member(m): f"{title}.{m}" for m in members}
        lines.append(f"  {title}: {json.dumps(spelled)},")
    lines += ["};", "const FUNCTIONS = ["]
    lines += [f"  [{json.dumps(f.py)}, {json.dumps(f.js)}]," for f in protocol.FUNCTIONS]
    lines.append("];")
    return "\n".join(lines)


def _dart_enum(name: str, members: list[tuple[str, str]]) -> str:
    """One Dart enum whose values each carry their game name: hay('Items.Hay')."""
    values = ",\n".join(f"  {member}('{wire}')" for member, wire in members)
    return (
        f"enum {name} implements _Wired {{\n"
        f"{values};\n"
        f"\n"
        f"  const {name}(this.wire);\n"
        f"\n"
        f"  @override\n"
        f"  final String wire;\n"
        f"}}"
    )


def _dart_names() -> str:
    """Dart's enums have to be written out, so this block is code, not data:
    an enum of the directions (with north, east, south and west as plain
    constants too, as the game has them), one enum per group, and the list
    of all of them that the library looks answers up in."""
    enums = [_dart_enum("Direction", [(protocol.dart_member(d), d) for d in data.DIRECTIONS])]
    for title, members in _groups().items():
        enums.append(_dart_enum(title, [(protocol.dart_member(m), f"{title}.{m}") for m in members]))
    constants = [
        f"const {protocol.dart_member(d)} = Direction.{protocol.dart_member(d)};"
        for d in data.DIRECTIONS
    ]
    every = ", ".join(f"{name}.values" for name in ("Direction", *_groups()))
    return "\n\n".join([
        *enums,
        "\n".join(constants),
        f"const List<List<_Wired>> _groups = [{every}];",
    ])


def _original_names() -> str:
    """The game's own language: the same names as Python's library. Its FUNCTIONS
    are the ones that go straight to the farm - print, min, max and spawn_drone
    the interpreter handles itself."""
    own = {"print", "quick_print", "min", "max", "spawn_drone"}
    groups = "".join(
        f"    {json.dumps(title)}: {json.dumps(list(members))},\n"
        for title, members in _groups().items()
    )
    return (
        f"DIRECTIONS = {json.dumps(list(data.DIRECTIONS))}\n"
        f"GROUPS = {{\n{groups}}}\n"
        f"FUNCTIONS = {json.dumps([f.py for f in protocol.FUNCTIONS if f.py not in own])}"
    )


#: Per language: the library's file, how its comments start, and its names.
_LIBRARIES = {
    "original": ("farm_lang.py", "#", _original_names),
    "python": ("farm_api.py", "#", _python_names),
    "javascript": ("farm_api.js", "//", _javascript_names),
    "dart": ("farm_api.dart", "//", _dart_names),
}


def _fill(template: str, names: str, comment: str) -> str:
    """The template with everything between its NAMES markers replaced."""
    start, end = f"{comment} NAMES-START\n", f"{comment} NAMES-END"
    before, found_start, rest = template.partition(start)
    _, found_end, after = rest.partition(end)
    if not (found_start and found_end):
        raise ValueError(f"no '{start.strip()}' ... '{end}' block to fill")
    return f"{before}{start}{names}\n{end}{after}"


def library(language: str) -> str:
    """The farm's library for a language, with every name filled in."""
    filename, comment, names = _LIBRARIES[language]
    template = (_HERE / filename).read_text(encoding="utf-8")
    return _fill(template, names(), comment)


# ── Dart's extra files ──────────────────────────────────────────────────

#: Put in front of each Dart file of the player's, on its first line, so
#: every line of it keeps its number.
DART_IMPORT = "import 'farm_api.dart'; "

#: The Dart program that actually runs. Each of your files is a library;
#: this imports every one of them under a prefix of its own, so nothing
#: you name can clash with anything here, and hands the main() of the one
#: you run to the farm's library - with every top-level function of every
#: file of yours, by name, for the drones.
DART_RUNNER = """\
// Runs {entry}.dart - your program - with the farm's library around it.
import 'farm_api.dart' as farm;
{imports}
void main() => farm.runFarmProgram(program.main, drones: {{
{drones}}});
"""

#: Words the scan never takes for a function's name: Dart's reserved words,
#: its built-in identifiers, and async, sync, await and yield.
_DART_WORDS = frozenset("""
    assert break case catch class const continue default do else enum extends false final
    finally for if in is new null rethrow return super switch this throw true try var void
    while with abstract as covariant deferred dynamic export extension external factory
    Function get implements import interface late library mixin operator part required set
    static typedef async await sync yield
""".split())

#: A top-level item holding any of these words declares something other
#: than a function - a class, a variable, an import - or, after = or =>,
#: is already inside an expression.
_DART_NOT_A_FUNCTION = frozenset({
    "class", "enum", "extension", "mixin", "typedef", "import", "export", "part", "library",
    "final", "const", "var", "late", "external", "static", "augment", "=", "=>",
})

#: What may stand just before a function's name: a return type's last word
#: or bracket, or nothing (the start of the item).
_DART_BEFORE_NAME = frozenset({")", ">", "?"})

#: Words that can't be a return type, so a name after them is not declared.
_DART_NOT_A_TYPE = frozenset({
    "get", "set", "operator", "new", "const", "return", "await", "throw", "yield",
    "in", "is", "as", "case", "else",
})

_DART_TOKEN = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*|\d[A-Za-z0-9_.]*|=>|\S")
_DART_NAME = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


def _dart_skip(code: str, i: int) -> int:
    """If a comment or a string starts at i, the index just past it; else i."""
    if code.startswith("//", i):
        end = code.find("\n", i)
        return len(code) if end < 0 else end
    if code.startswith("/*", i):  # Dart's block comments nest
        depth, j = 0, i
        while j < len(code):
            if code.startswith("/*", j):
                depth, j = depth + 1, j + 2
            elif code.startswith("*/", j):
                depth, j = depth - 1, j + 2
                if depth == 0:
                    return j
            else:
                j += 1
        return len(code)
    raw = code[i] in "rR" and code[i + 1:i + 2] in ("'", '"') and not (
        i > 0 and (code[i - 1].isalnum() or code[i - 1] in "_$"))
    start = i + 1 if raw else i
    if code[start] not in "'\"":
        return i
    quote = code[start] * 3 if code.startswith(code[start] * 3, start) else code[start]
    j = start + len(quote)
    while j < len(code):
        if code.startswith(quote, j):
            return j + len(quote)
        if code[j] == "\n" and len(quote) == 1:
            return j  # never closed: it ends with its line
        if not raw and code[j] == "\\":
            j += 2
        elif not raw and code.startswith("${", j):
            j = _dart_interpolation_end(code, j + 2)
        else:
            j += 1
    return len(code)


def _dart_interpolation_end(code: str, j: int) -> int:
    """From just inside a string's ${, the index just past its closing }."""
    depth = 0
    while j < len(code):
        past = _dart_skip(code, j)
        if past != j:
            j = past
            continue
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            if depth == 0:
                return j + 1
            depth -= 1
        j += 1
    return len(code)


def _dart_code(code: str) -> str:
    """The code with every comment and string blanked out, so that only code
    is left to read - a brace in a string can't be taken for a block."""
    out, i = [], 0
    while i < len(code):
        past = _dart_skip(code, i)
        if past == i:
            out.append(code[i])
            i += 1
        else:
            out.append(re.sub(r"[^\n]", " ", code[i:past]))
            i = past
    return "".join(out)


def _dart_balanced(tokens: list[str], i: int, opening: str, closing: str) -> int:
    """From an opening bracket at i, the index just past its partner."""
    depth = 0
    for j in range(i, len(tokens)):
        if tokens[j] == opening:
            depth += 1
        elif tokens[j] == closing:
            depth -= 1
            if depth == 0:
                return j + 1
    return len(tokens)


def dart_functions(code: str) -> list[str]:
    """The functions a Dart program declares at its top level, by name: the
    ones a drone can be sent to run. Not main, whose run is the program's
    own; not a getter or setter; not a name starting with _, which is
    private to the file and out of runner.dart's reach.

    A name counts when, outside every bracket, it is followed by its
    parameters - after type parameters, if it has them - and then by a
    body: {, =>, async or sync*. That is a function and nothing else at the
    top level, and it is better to miss a strange one (spawnDrone then says
    so) than to list a name runner.dart would fail to compile.
    """
    tokens = _DART_TOKEN.findall(_dart_code(code))
    found: list[str] = []
    depth = 0
    words: set[str] = set()  # the current top-level item's words, outside brackets
    before: str | None = None  # the word just before this one, in this item
    for i, token in enumerate(tokens):
        if depth == 0 and _DART_NAME.fullmatch(token) and not words & _DART_NOT_A_FUNCTION:
            if (token not in _DART_WORDS and token != "main" and not token.startswith("_")
                    and (before is None or before in _DART_BEFORE_NAME
                         or (_DART_NAME.fullmatch(before) and before not in _DART_NOT_A_TYPE))):
                j = i + 1
                if j < len(tokens) and tokens[j] == "<":
                    j = _dart_balanced(tokens, j, "<", ">")
                if j < len(tokens) and tokens[j] == "(":
                    j = _dart_balanced(tokens, j, "(", ")")
                    if j < len(tokens) and tokens[j] in ("{", "=>", "async", "sync") \
                            and token not in found:
                        found.append(token)
        if token in ("(", "[", "{"):
            depth += 1
        elif token in (")", "]", "}"):
            depth = max(0, depth - 1)
        if depth == 0:
            if token in (";", "}"):  # an item ends here, or may
                words.clear()
                before = None
            else:
                if token not in (")", "]"):
                    words.add(token)
                before = token
    return found


def dart_runner(files: Mapping[str, str] | str, entry: str = "main") -> str:
    """runner.dart for a program: the main() of the file it runs, and the
    top-level functions of all its files for the drones, each as
    'harvestColumn': program.harvestColumn.

    The file it runs is imported as program, each other file as
    program_<its name>. A function is listed under its own name - the
    entry's first, then the other files' in the order of their names - and
    when that name is taken already, under utils.harvestColumn instead, so
    every function is there under one name. (A $ in a name is escaped in
    the string, where it would start an interpolation.)"""
    program = program_files(files, entry)
    order = [entry, *sorted(name for name in program if name != entry)]
    prefixes = {name: "program" if name == entry else f"program_{name}" for name in order}
    imports = "".join(f"import '{name}.dart' as {prefixes[name]};\n" for name in order)
    entries, taken = [], set()
    for file in order:
        for name in dart_functions(program[file]):
            key = name if name not in taken else f"{file}.{name}"
            taken.add(key)
            quoted = key.replace("$", "\\$")
            entries.append(f"  '{quoted}': {prefixes[file]}.{name},\n")
    return DART_RUNNER.format(entry=entry, imports=imports, drones="".join(entries))


def dart_executable() -> str | None:
    """The dart to start: the SDK's own, rather than Flutter's shim in front of it.

    dart_path() usually finds Flutter's bin/dart.bat. Every time, before it
    starts the SDK's dart.exe, that shim takes a lock and asks git for
    Flutter's revision, which is half the start-up: 1.6s against 0.75s on
    this machine. Worse, the shim is cmd.exe and dart.exe is its child, so
    stopping the process we started (Popen.kill) leaves dart.exe running.
    A `while (true) {}` would go on spinning out of sight, and whoever reads
    its output would wait for ever, since dart.exe still holds the pipe.

    The SDK the shim would start is right beside it, in bin/cache/dart-sdk.
    Anywhere else - Dart installed on its own - dart_path() is already the
    real thing.
    """
    found = dart_path()
    if found is None:
        return None
    real = Path(found).parent / "cache" / "dart-sdk" / "bin" / ("dart.exe" if os.name == "nt" else "dart")
    return str(real) if real.is_file() else found


# ── JavaScript's extra files ────────────────────────────────────────────

#: Beside the player's files, so that Node runs each .js file as an ES
#: module - import and export, as JavaScript is written today.
JS_PACKAGE = '{"type": "module"}\n'


def js_lead(name: str) -> str:
    """Put in front of a JavaScript file of the player's, on its first line,
    so every line keeps its number: it hands farm_api.cjs a way to look up
    a name at the top level of that file - a module's names are its own,
    and only code inside it can see them. spawnDrone uses it to make sure
    a function is one a new drone can find again, and the drone uses it to
    find it. (eval is given the name as arguments[0], not as a parameter,
    so that no name of the player's can be hidden by the parameter's; a
    module can't declare a name arguments, or eval.)"""
    return (f'globalThis[Symbol.for("farm.file")]?.({json.dumps(name)}, '
            f"function () {{ return eval(arguments[0]); }}); ")


def prepare(language: str, files: Mapping[str, str] | str, entry: str = "main",
            ) -> tuple[dict[str, str], list[str], dict[str, str]]:
    """What the runner needs to run a program: the files to write into an
    empty temp dir (relative path -> text; a path may name a folder to
    make), the command to run there (argv; the executable as found by
    shutil.which / code_coach.engine.dart_path), and where each of the
    player's files was put (name -> relative path), for error reporting.

    files is {name: code}, or a plain string for one file, main; entry
    names the one that runs. An error a program reports names the file it
    happened in by its name, without the extension: [message, line, "utils"].

    The layouts:
    - Python: the library is farm/farm_api.py, a folder down, so that a
      file of yours called json.py or random.py can't stand in for a module
      the library imports itself; your files are main.py, utils.py ... and
      the command names the entry: python -u farm/farm_api.py main.
    - JavaScript: farm_api.cjs, package.json ({"type": "module"}) and your
      files as main.js, utils.js ... - ES modules, each with js_lead() on
      its first line; the command is node farm_api.cjs main.
    - Dart: farm_api.dart, runner.dart (which knows the entry) and your
      files as main.dart, utils.dart ... - each with DART_IMPORT on its
      first line; the command is dart run runner.dart.

    For Dart the executable is dart_executable(): the SDK behind Flutter's
    shim when there is one, so that killing the process kills the program.

    Raises MissingRuntime if node or dart is not installed, and ValueError
    for a language there is no library for, a name a file can't have (see
    FILE_NAME and RESERVED_NAMES), or an entry that is not one of the files.
    """
    if language not in LANGUAGES:
        raise ValueError(f"there is no farm library for {language!r}; try one of {', '.join(LANGUAGES)}")
    program = program_files(files, entry)
    if language == "original":
        # The interpreter reads your files from files/ beside it.
        where = {name: f"files/{name}.py" for name in program}
        to_write = {"farm_lang.py": library("original")}
        to_write.update({where[name]: code for name, code in program.items()})
        return to_write, [sys.executable, "-u", "farm_lang.py", entry], where
    if language == "python":
        where = {name: f"{name}.py" for name in program}
        to_write = {"farm/farm_api.py": library("python")}
        to_write.update({where[name]: code for name, code in program.items()})
        return to_write, [sys.executable, "-u", "farm/farm_api.py", entry], where
    if language == "javascript":
        node = shutil.which("node")
        if node is None:
            raise MissingRuntime("JavaScript runs on Node.js, which is not installed here.")
        where = {name: f"{name}.js" for name in program}
        to_write = {"farm_api.cjs": library("javascript"), "package.json": JS_PACKAGE}
        to_write.update({where[name]: js_lead(name) + code for name, code in program.items()})
        return to_write, [node, "farm_api.cjs", entry], where
    dart = dart_executable()
    if dart is None:
        raise MissingRuntime("Dart is not installed here. It comes with Flutter.")
    where = {name: f"{name}.dart" for name in program}
    to_write = {"farm_api.dart": library("dart"), "runner.dart": dart_runner(program, entry)}
    to_write.update({where[name]: DART_IMPORT + code for name, code in program.items()})
    return to_write, [dart, "run", "runner.dart"], where
