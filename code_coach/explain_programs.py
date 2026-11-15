"""Turn a snippet into a program that can run - the ONE place that rule lives for the explainers.

Brain Drills shows fragments: a Dart body with no `main`, a C body with no `int main`, a SQL script. "Run it" in the
browser wraps them with `dartProgram` / `cProgram` (web/src/lib/brainRound.ts) and sends the whole program to
`/api/brain/run`; this module is the same rule in Python, so "Explain my code" can run what the drill shows. Tests hold
it equal to `tests/dart_oracle.full_program`, `tests/c_oracle.full_program` and to the two browser functions' text,
and the browser's own wrapping (what Run it sends) is untouched.

`wrap(language, code)` -> `Program(text, offset, runnable, why_not, printed_last)`:
  text        what to run
  offset      lines the wrapper put in front (an error on line 7 of the program is line 7 - offset of the code)
  runnable    False when the snippet cannot run on its own (Flutter widgets, a library with no `main`)
  why_not     the plain reason, for the note
  printed_last  Dart: the wrapper added a `print(...)` round the last line (a bare expression)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

C_HEADERS = "#include <stdio.h>\n#include <stdint.h>\n#include <string.h>\n#include <stddef.h>\n"
_MAIN = re.compile(r"\bmain\s*\(")

FLUTTER_WHY = "Flutter widgets cannot run here: they need Flutter's own engine, not plain Dart, so there is no printed output to show."
_FLUTTER = re.compile(
    r"package:flutter|\b(?:StatelessWidget|StatefulWidget|MaterialApp|CupertinoApp|Scaffold|BuildContext|setState|"
    r"Placeholder|GestureDetector|InkWell|ValueListenableBuilder|ListenableBuilder|FutureBuilder|TextEditingController|"
    r"TextFormField|TextField|AppBar|ListView|Navigator|Theme|MediaQuery|SizedBox|Padding|Expanded|Flexible|Spacer|"
    r"Positioned|CustomPaint|FlutterLogo|Icon|Builder|ConstrainedBox|AspectRatio|FractionallySizedBox|Wrap|Stack|"
    r"Row|Column|Container|Center|Align|Text|Box|Form|Key|ValueKey|ValueNotifier|ChangeNotifier|runApp|Widget)\b\s*[(<.]?"
)
_FLUTTER_CORE = re.compile(
    r"package:flutter|\b(?:StatelessWidget|StatefulWidget|MaterialApp|CupertinoApp|Scaffold|BuildContext|setState|Placeholder|"
    r"GestureDetector|InkWell|ValueListenableBuilder|ListenableBuilder|FutureBuilder|TextEditingController|TextFormField|"
    r"AppBar|Navigator|SizedBox|Expanded|Flexible|Positioned|CustomPaint|FlutterLogo|ConstrainedBox|AspectRatio|"
    r"FractionallySizedBox|runApp)\b|\b(?:Row|Column|Stack|Container|Center|Align|Padding|Wrap|ListView|Text|Icon|Box|Form|"
    r"Builder|Spacer)\s*\("
)
_TOP_DECL = re.compile(r"^(?:abstract\s+|sealed\s+|base\s+|final\s+|interface\s+)*(?:class|mixin|enum|extension|typedef|import|export|part|library)\b", re.M)


@dataclass(frozen=True)
class Program:
    text: str
    offset: int = 0
    runnable: bool = True
    why_not: str = ""
    printed_last: bool = False


def is_flutter(code: str, context: str = "") -> bool:
    """Flutter widget code: it imports nothing plain Dart can run (a drill id fl_/fs_/fw_ says so too)."""
    if re.match(r"f[lsw]_", context or ""):
        return True
    return bool(_FLUTTER_CORE.search(code))


def dart_body(code: str) -> tuple[str, bool]:
    lines = code.rstrip().split("\n")
    last = lines[-1].strip()
    printed = False
    if not (last.startswith("print(") or last.endswith(";") or last.endswith("}")):
        lines[-1] = f"print({last});"
        printed = True
    return "\n".join("  " + ln if ln.strip() else ln for ln in lines), printed


def dart_program(code: str, context: str = "") -> Program:
    if is_flutter(code, context):
        return Program(code, 0, False, FLUTTER_WHY)
    if _MAIN.search(code):
        return Program(code)
    if _TOP_DECL.search(code):
        return Program(code, 0, False, "There is no main(), so nothing starts running: the walkthrough above says what each piece is.")
    body, printed = dart_body(code)
    return Program("void main() {\n" + body + "\n}", 1, True, "", printed)


def c_program(code: str) -> Program:
    code = code.rstrip("\n")
    if re.search(r"^\s*#\s*include", code, re.M) and _MAIN.search(code):
        return Program(code + "\n")
    if _MAIN.search(code):
        return Program(C_HEADERS + code + "\n", C_HEADERS.count("\n"))
    # a function defined at column 0 with no main cannot run (a body never defines a function)
    if re.search(r'^(?!(?:if|for|while|switch|return|else|do|case|printf|puts)\b)[A-Za-z_][\w \t\*]*[ \t\*]\**[A-Za-z_]\w*[ \t]*\([^;{}]*\)[ \t]*\{?[ \t]*$', code, re.M):
        return Program(code, 0, False, "There is no main(), so nothing starts running: the walkthrough above says what each piece is.")
    body = "\n".join("    " + ln if ln.strip() else ln for ln in code.split("\n"))
    return Program(C_HEADERS + "int main(void) {\n" + body + "\n}\n", C_HEADERS.count("\n") + 1)


def sql_program(code: str) -> Program:
    return Program(code.rstrip())


def wrap(language: str, code: str, context: str = "") -> Program:
    if language == "dart":
        return dart_program(code, context)
    if language == "c":
        return c_program(code)
    if language == "sql":
        return sql_program(code)
    raise ValueError(f"no program convention for {language}")
