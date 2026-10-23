"""The Dart oracle for Brain Drills: hold a batch of Dart snippets to the real `dart`, in ONE process.

`dart run` costs ~0.7-1 s a program, and a pack has thousands of items, so the items are batched:

* every item whose program has no `main` is the BODY of a function `iN()` in one library (`snip.dart`);
* every item that is a complete program (it declares classes, or is `Future<void> main() async`) is its own
  library `fN.dart` (so two items may both declare a `class Dog`), and its `main` is called through an import prefix;
* `main.dart` calls them all, one after the other, each inside a Zone that captures `print` (so the output of one
  item can never leak into another's), awaits ~30 turns of the event loop so that microtasks and
  `Future.delayed(Duration.zero)` callbacks finish, and writes ONE line `@@RESULTS@@<json>` with, per item, its
  printed lines and the name of the error that escaped it (if any). Then `dart run main.dart` compiles once and runs
  once - about 2 s for 1500 items.

If an item does not compile it must not hide the rest: the compiler's `file:line: Error:` lines name the item (a
function's line range in `snip.dart`, or the `fN.dart` file), it is taken out and its words kept, and the batch runs
again; an error that names no item is bisected. A compile failure is reported as that item's result, never raised.

What a Dart item is (the convention shared with "Run it" in web/src/lib/brainRound.ts and written up in
code_coach/brain/_dart_model.py): the program is `item.check`, or the prompt when `check` is empty; with a `main(`
it is complete, else it is the body of `main` whose last line is printed if it is a bare expression.

Use from a test:

    from tests.dart_oracle import dart_values
    got = dart_values([item.check or item.prompt for item in items], mode="value")

`mode` is how the printed output is turned into the value compared with `item.answer` (the Activity's `oracle`):
"value" (the lines joined with a newline; a typed answer is one line), "lines" (the lines joined with nothing:
Async Order's letters), "error" ("error" if it did not compile or threw, else "fine"). Without `dart` on the
machine `DART` is None and tests skip.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

DART: str | None = None
try:  # the SDK's own dart.exe, never Flutter's .bat shim (it leaves the real process running when killed)
    from code_coach.farm.stubs.render import dart_executable

    DART = dart_executable()
except Exception:  # pragma: no cover - a machine without Dart
    DART = None

#: A program that mentions `main(` is a complete program.
MAIN = re.compile(r"\bmain\s*\(")
#: The compiler's way of naming a place: `snip.dart:12:3: Error: ...` (a path may come first).
ERROR_LINE = re.compile(r"(?:^|[\\/\s])((?:snip|f\d+|main)\.dart):(\d+):(\d+): Error: (.*)$", re.M)
RESULTS = "@@RESULTS@@"


# ── What an item's program is ───────────────────────────────────────────

def is_complete(code: str) -> bool:
    return bool(MAIN.search(code))


def body_of(code: str) -> str:
    """The statements of a body, indented two spaces; the last line printed when it is a bare expression."""
    lines = code.rstrip().split("\n")
    last = lines[-1].strip()
    if not (last.startswith("print(") or last.endswith(";") or last.endswith("}")):
        lines[-1] = f"print({last});"
    return "\n".join("  " + ln if ln.strip() else ln for ln in lines)


def full_program(code: str) -> str:
    """The program "Run it" runs for an item's program: as is when complete, else wrapped in `void main()`."""
    if is_complete(code):
        return code
    return "void main() {\n" + body_of(code) + "\n}"


# ── The batch ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DartRun:
    #: What `print` wrote, line by line (empty when the program did not compile).
    lines: tuple[str, ...] = ()
    #: The type of the error that ended the program ("RangeError"), "" if none did.
    error: str = ""
    #: The compiler's first complaint, "" if it compiled.
    compile_error: str = ""

    def value(self, mode: str = "value") -> str:
        if mode == "error":
            return "error" if self.compile_error or self.error else "fine"
        if self.compile_error:
            return "COMPILE ERROR: " + self.compile_error
        if self.error:
            return "ERROR " + self.error + (" after: " + " | ".join(self.lines) if self.lines else "")
        return ("" if mode == "lines" else "\n").join(self.lines)


MAIN_TEMPLATE = """\
import 'dart:async';
import 'dart:convert';
{imports}

Future<List<dynamic>> _run(Function f) async {{
  final buf = <String>[];
  var err = '';
  await runZonedGuarded(() async {{
    try {{
      final r = Function.apply(f, []);
      if (r is Future) await r;
    }} catch (e) {{
      err = e.runtimeType.toString();
    }}
    for (var k = 0; k < 30; k++) {{
      await Future.delayed(Duration.zero);
    }}
  }}, (e, st) {{
    err = e.runtimeType.toString();
  }}, zoneSpecification: ZoneSpecification(print: (self, parent, zone, line) {{
    buf.addAll(line.split('\\n'));
  }}));
  return [buf, err];
}}

Future<void> main() async {{
  final out = <dynamic>[];
{calls}
  print('{marker}' + jsonEncode(out));
}}
"""


def _kill(proc: subprocess.Popen) -> None:
    from code_coach.canvas.pyharness.session import kill_tree

    kill_tree(proc)


def _dart_run(folder: Path, timeout: float) -> tuple[int, str]:
    """`dart run main.dart` in `folder`: (exit code, stdout + stderr)."""
    from code_coach.canvas.pyharness.session import child_flags
    from code_coach.gotchas.toolchains import _tool_env

    assert DART, "no dart on this machine"
    out_path, err_path = folder / "out.txt", folder / "err.txt"
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        proc = subprocess.Popen([DART, "run", str(folder / "main.dart")], cwd=folder, env=_tool_env(folder),
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err, creationflags=child_flags())
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            return -9, "TIMEOUT after %ss" % timeout
    text = out_path.read_bytes().decode("utf-8", "replace") + "\n" + err_path.read_bytes().decode("utf-8", "replace")
    return code, text.replace("\r\n", "\n")


def _build(folder: Path, programs: dict[int, str]) -> dict[int, tuple[int, int]]:
    """Write the batch's files; returns, for the items inside snip.dart, their (first, last) line numbers."""
    for old in folder.glob("*.dart"):
        old.unlink()
    snip: list[str] = []
    spans: dict[int, tuple[int, int]] = {}
    imports = ["import 'snip.dart' as s;"]
    calls: list[str] = []
    for idx, code in programs.items():
        if is_complete(code):
            (folder / f"f{idx}.dart").write_text(code + "\n", encoding="utf-8")
            imports.append(f"import 'f{idx}.dart' as f{idx};")
            calls.append(f"  out.add(await _run(f{idx}.main));")
        else:
            body = body_of(code)
            head = "Future<void> i%d() async {" % idx if re.search(r"\bawait\b", code) else "void i%d() {" % idx
            first = len(snip) + 1
            snip.extend([head, *body.split("\n"), "}"])
            spans[idx] = (first, len(snip))
            calls.append(f"  out.add(await _run(s.i{idx}));")
    (folder / "snip.dart").write_text("\n".join(snip) + "\n", encoding="utf-8")
    (folder / "main.dart").write_text(
        MAIN_TEMPLATE.format(imports="\n".join(imports), calls="\n".join(calls), marker=RESULTS), encoding="utf-8")
    return spans


def _blame(text: str, spans: dict[int, tuple[int, int]], programs: dict[int, str]) -> dict[int, str]:
    """The items the compiler's complaints name, each with its first complaint."""
    blamed: dict[int, str] = {}
    for m in ERROR_LINE.finditer(text):
        name, line, message = m.group(1), int(m.group(2)), m.group(4).strip()
        if name == "snip.dart":
            for idx, (lo, hi) in spans.items():
                if lo <= line <= hi:
                    blamed.setdefault(idx, f"{message} (line {line - lo} of the snippet)")
        elif name.startswith("f"):
            idx = int(name[1:-5])
            if idx in programs:
                blamed.setdefault(idx, f"{message} (line {line})")
    return blamed


def _batch(folder: Path, programs: dict[int, str], timeout: float) -> dict[int, DartRun]:
    results: dict[int, DartRun] = {}
    todo = dict(programs)
    for _ in range(6):
        if not todo:
            return results
        spans = _build(folder, todo)
        code, text = _dart_run(folder, timeout)
        marker = text.rfind(RESULTS)
        if marker >= 0:
            data = json.loads(text[marker + len(RESULTS):].splitlines()[0])
            for idx, (lines, err) in zip(todo, data):
                results[idx] = DartRun(tuple(lines), err)
            return results
        blamed = _blame(text, spans, todo)
        if re.search(r"(?:^|[\\/\s])main\.dart:\d+:\d+: Error", text, re.M):  # the harness itself: a bug in this file
            raise AssertionError("the oracle's own main.dart does not compile:\n" + text[-2000:])
        if blamed:
            for idx, message in blamed.items():
                results[idx] = DartRun(compile_error=message)
                del todo[idx]
            continue
        # An error naming no item (a timeout, a crash, an unexpected message): split the batch to find the culprit.
        if len(todo) == 1:
            (idx,) = todo
            results[idx] = DartRun(compile_error="did not run: " + (text.strip()[:300] or f"exit code {code}"))
            return results
        keys = list(todo)
        half = len(keys) // 2
        for part in (keys[:half], keys[half:]):
            results.update(_batch(folder, {k: todo[k] for k in part}, timeout))
        return results
    for idx in todo:  # six rounds of fixing and still failing: say so for each remaining one
        results[idx] = DartRun(compile_error="did not compile after removing the others that failed")
    return results


def run_batch(programs: list[str], timeout: float = 240.0) -> list[DartRun]:
    """Run every program (an item's `check`, or its prompt) for real, in one dart process where possible."""
    if not programs:
        return []
    from code_coach.canvas.pyharness.session import remove_folder

    folder = Path(tempfile.mkdtemp(prefix="dart_oracle_"))
    try:
        found = _batch(folder, dict(enumerate(programs)), timeout)
    finally:
        remove_folder(folder)
    return [found[i] for i in range(len(programs))]


def dart_values(programs: list[str], mode: str = "value", timeout: float = 240.0) -> list[str]:
    """The value of each program as Dart prints it (see the module docstring for `mode`)."""
    return [r.value(mode) for r in run_batch(programs, timeout)]
