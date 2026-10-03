"""Turn a player's program into files a real Python, Node or Dart process runs.

The farm's three libraries sit beside this file - farm_api.py, farm_api.js
and farm_api.dart - each with a NAMES block that is nearly empty in the
file itself. prepare() fills that block from data.py and protocol.py every
time a program starts, so the names a program sees are always the farm's
own: an entity added to data.py is in all three languages the next time
anyone presses Run, and no name can be spelled one way here and another
way there.

What comes back is everything the runner needs and nothing it has to know
about a particular language: the files to write into an empty folder (as
UTF-8), the command to run in that folder, and which file is the player's,
so an error can point at their line.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from code_coach.engine import dart_path
from code_coach.farm import data, protocol

LANGUAGES = ("python", "javascript", "dart")

_HERE = Path(__file__).resolve().parent


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


#: Per language: the library's file, how its comments start, and its names.
_LIBRARIES = {
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

#: Put in front of a Dart program, on its first line, so every line of it
#: keeps its number.
DART_IMPORT = "import 'farm_api.dart'; "

#: The Dart program that actually runs. Your file is a library with a
#: main(); this imports it under a prefix, so nothing you name can clash
#: with anything here, and hands that main() to the farm's library.
DART_RUNNER = """\
// Runs farm.dart - your program - with the farm's library around it.
import 'farm_api.dart' as farm;
import 'farm.dart' as program;

void main() => farm.runFarmProgram(program.main);
"""


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


def prepare(language: str, user_code: str) -> tuple[dict[str, str], list[str], str]:
    """Files to write into an empty temp dir, the command to run there (argv; the
    executable as found by shutil.which / code_coach.engine.dart_path), and the name
    of the file holding the user's code (for error line reporting).

    For Dart the executable is dart_executable(): the SDK behind Flutter's
    shim when there is one, so that killing the process kills the program.

    Raises MissingRuntime if node or dart is not installed, and ValueError
    for a language there is no library for.
    """
    if language == "python":
        files = {"farm_api.py": library("python"), "farm.py": user_code}
        return files, [sys.executable, "-u", "farm_api.py", "farm.py"], "farm.py"
    if language == "javascript":
        node = shutil.which("node")
        if node is None:
            raise MissingRuntime("JavaScript runs on Node.js, which is not installed here.")
        files = {"farm_api.js": library("javascript"), "farm.js": user_code}
        return files, [node, "farm_api.js", "farm.js"], "farm.js"
    if language == "dart":
        dart = dart_executable()
        if dart is None:
            raise MissingRuntime("Dart is not installed here. It comes with Flutter.")
        files = {
            "farm_api.dart": library("dart"),
            "farm.dart": DART_IMPORT + user_code,
            "runner.dart": DART_RUNNER,
        }
        return files, [dart, "run", "runner.dart"], "farm.dart"
    raise ValueError(f"there is no farm library for {language!r}; try one of {', '.join(LANGUAGES)}")
