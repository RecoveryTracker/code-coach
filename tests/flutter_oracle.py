"""The Flutter oracle for Brain Drills: hold a batch of widget snippets to REAL Flutter, in one `flutter test` run.

A Flutter item shows a short widget tree and asks for a number or a word that Flutter itself computes (a width, a
left offset, a count of rows, "overflow"). Like the Dart oracle (tests/dart_oracle.py) it is batched, because
`flutter test` costs ~7 s to start and compile and then ~10 ms a widget test:

* every item becomes ONE `testWidgets('iN', ...)` in ONE generated test file (never one file per item: Flutter starts
  a process per file); `flutter test --no-pub --reporter json` runs it and the `@@iN@@value` lines the tests print
  are read back by test id (`print` events), the way tests/test_flutter_questions.py reads its results;
* an item that does not compile is named by file and line (the "loading" test's error text), taken out, and the
  batch runs again; an error that names no item is bisected. A compile failure becomes that item's result
  (`COMPILE ERROR: ...`), never an exception. A Flutter error while pumping (an overflow nobody asked about, an
  unbounded constraint) or a throwing check is that item's result too (`ERROR: ...`);
* the throwaway project is `%TEMP%/code_coach_flutter_brain/fq`, SEPARATE from the one of test_flutter_questions
  (`code_coach_flutter_questions/fq`), created once (a hand-written pubspec and `flutter pub get --offline`, with the
  online fallback) and reused by every later run; each run uses its own folder of generated files inside it, removed
  afterwards, so two test processes can share the project.

THE ITEM CONVENTION (what an Item of a Flutter activity is; the Activity says `oracle="flutter"`):

* `item.prompt` is the WIDGET EXPRESSION shown to the learner (no trailing `;`), optionally led by `//` comment lines
  (the question: `// left of c?`). The host is not shown (the activity's blurb explains it once): the app's view is
  exactly 400 x 300 logical pixels at devicePixelRatio 1.0, so the expression is the root widget and is given TIGHT
  400 x 300 constraints, under a `Directionality(ltr)`. All of `package:flutter/material.dart` is in scope.
  Declarations are allowed: a prompt with top-level classes (a column-0 `}` line) is its own library, the classes
  first and the widget expression after the last column-0 `}`; two items may both declare `class Counter`.
* `Box(id, {w = 50, h = 50})` is a `SizedBox(key: ValueKey(id), width: w, height: h)`: any widget may carry
  `key: ValueKey('id')` (or `Key('id')`) to be measured.
* `item.check` is the MEASUREMENT, a Dart expression evaluated after `pumpWidget`, using `w(id) h(id) x(id) y(id)
  r(id) b(id)` (width, height, left, top, right, bottom of the keyed widget, in screen coordinates; the screen starts
  at 0, 0), `count(finder)`, `overflowed` (did a RenderFlex report an overflow?), and everything in flutter_test. A
  check that contains `await` or `return` is the body of `Future<Object?> Function(WidgetTester tester)` instead
  (tap, pump, then `return ...`). Numbers print as an integer when whole (`120`), else Dart's way (`96.5`); a bool
  prints `true`/`false`; anything else is `'$value'`. An empty check is an error.
* A Flutter error that reaches `FlutterError.onError` during the item (an overflow, a layout assertion) is the
  result `ERROR: <first line>` UNLESS the check read `overflowed`: asking about overflow is how an item says it
  expected one.

Use from a test:

    from tests.flutter_oracle import flutter_values
    got = flutter_values([(i.prompt, i.check) for i in items])      # one string per item

Without Flutter on the machine `FLUTTER` is None and tests skip.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

#: Items per generated test file (compile time grows with the file; a run with more splits into files).
PER_FILE = 800


def _flutter() -> Path | None:
    """The flutter launcher, or None where there is no SDK (the same search as tests/test_flutter_questions.py)."""
    names = ("flutter.bat", "flutter") if os.name == "nt" else ("flutter",)
    roots = []
    if os.environ.get("FLUTTER_ROOT"):
        roots.append(Path(os.environ["FLUTTER_ROOT"]))
    found = shutil.which("flutter")
    if found:
        roots.append(Path(found).resolve().parent.parent)
    roots.append(Path("C:/Flutter/flutter"))
    for root in roots:
        for name in names:
            candidate = root / "bin" / name
            if candidate.is_file():
                return candidate
    return None


FLUTTER = _flutter()

HOME = Path(tempfile.gettempdir()) / "code_coach_flutter_brain"
PROJECT = HOME / "fq"
RESULT = re.compile(r"^@@(i\d+)@@(.*)$", re.S)
#: `test/b/<run>/batch_test.dart:12:5: Error: ...` or `lib/brain_prelude.dart:3:1: Error: ...`
ERROR_LINE = re.compile(r"(?:^|[\\/\s])((?:lib|test)[\\/][^\s:]+\.dart):(\d+):(\d+): Error: (.*)$", re.M)

PUBSPEC = """\
name: fq
description: "Brain Drills Flutter oracle (generated by tests/flutter_oracle.py)."
publish_to: 'none'
version: 1.0.0+1
environment:
  sdk: ^3.7.0
dependencies:
  flutter:
    sdk: flutter
dev_dependencies:
  flutter_test:
    sdk: flutter
flutter:
  uses-material-design: true
"""

PRELUDE = """\
// Generated by tests/flutter_oracle.py: the helpers every Brain Drills Flutter item may use.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

export 'package:flutter/material.dart';
export 'package:flutter_test/flutter_test.dart' show testWidgets, WidgetTester, find, Finder;

// A SizedBox you can measure by its id.
Widget Box(String id, {double w = 50, double h = 50}) =>
    SizedBox(key: ValueKey<String>(id), width: w, height: h);

late WidgetTester _t;
final List<FlutterErrorDetails> _errors = <FlutterErrorDetails>[];
bool _asked = false;

Finder _f(String id) => find.byKey(ValueKey<String>(id));
double w(String id) => _t.getSize(_f(id)).width;
double h(String id) => _t.getSize(_f(id)).height;
double x(String id) => _t.getTopLeft(_f(id)).dx;
double y(String id) => _t.getTopLeft(_f(id)).dy;
double r(String id) => _t.getBottomRight(_f(id)).dx;
double b(String id) => _t.getBottomRight(_f(id)).dy;
int count(Finder finder) => finder.evaluate().length;
bool get overflowed {
  _asked = true;
  return _errors.any((d) => d.exception.toString().contains('overflowed'));
}

String _fmt(Object? v) {
  if (v is double) return v == v.roundToDouble() ? v.round().toString() : v.toString();
  return '$v';
}

String _first(Object e) {
  final lines = e.toString().split('\\n').where((l) => l.trim().isNotEmpty);
  return lines.isEmpty ? e.runtimeType.toString() : lines.first.trim();
}

// One item: a 400 x 300 screen at devicePixelRatio 1.0, the widget as its root, then the measurement.
Future<void> runCase(WidgetTester tester, String id, Widget Function() build,
    Future<Object?> Function(WidgetTester tester) check) async {
  _t = tester;
  _errors.clear();
  _asked = false;
  tester.view.physicalSize = const Size(400, 300);
  tester.view.devicePixelRatio = 1.0;
  final old = FlutterError.onError;
  FlutterError.onError = (FlutterErrorDetails d) => _errors.add(d);
  String out;
  try {
    await tester.pumpWidget(Directionality(textDirection: TextDirection.ltr, child: build()));
    out = _fmt(await check(tester));
    if (_errors.isNotEmpty && !_asked) out = 'ERROR: ' + _first(_errors.first.exception);
  } catch (e) {
    out = 'ERROR: ' + _first(e);
  } finally {
    FlutterError.onError = old;
    tester.view.reset();
  }
  print('@@$id@@$out');
}
"""


# ── The project ─────────────────────────────────────────────────────────

def _lock():
    """A directory lock so that two test processes do not create or refresh the project at once."""
    lock = HOME / ".lock"
    HOME.mkdir(parents=True, exist_ok=True)
    start = time.time()
    while True:
        try:
            lock.mkdir()
            return lock
        except FileExistsError:
            if time.time() - start > 600 or (time.time() - lock.stat().st_mtime > 900):
                shutil.rmtree(lock, ignore_errors=True)
            time.sleep(0.5)


def _write_if_changed(path: Path, text: str) -> None:
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{uuid.uuid4().hex[:6]}.tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    tmp.replace(path)


_ready = False


def project() -> Path:
    """The throwaway project, made once (pubspec + `flutter pub get`) and reused by every run and every session."""
    global _ready
    assert FLUTTER is not None, "no flutter on this machine"
    if _ready:
        return PROJECT
    lock = _lock()
    try:
        _write_if_changed(PROJECT / "pubspec.yaml", PUBSPEC)
        if not (PROJECT / ".dart_tool" / "package_config.json").is_file():
            done = subprocess.run([str(FLUTTER), "pub", "get", "--offline"], cwd=PROJECT, capture_output=True,
                                  text=True, timeout=900)
            if done.returncode != 0:
                done = subprocess.run([str(FLUTTER), "pub", "get"], cwd=PROJECT, capture_output=True, text=True,
                                      timeout=900)
            if done.returncode != 0:
                raise RuntimeError(f"flutter pub get failed:\n{done.stdout}\n{done.stderr}")
        _write_if_changed(PROJECT / "lib" / "brain_prelude.dart", PRELUDE)
    finally:
        shutil.rmtree(lock, ignore_errors=True)
    _ready = True
    return PROJECT


# ── What an item's program is ───────────────────────────────────────────

def split_declarations(code: str) -> tuple[str, str]:
    """(declarations, widget expression) of a prompt: declarations end at the last column-0 `}` line."""
    lines = code.rstrip().split("\n")
    last = -1
    for k, ln in enumerate(lines):
        if ln.rstrip() == "}":
            last = k
    decl = "\n".join(lines[:last + 1])
    expr = "\n".join(lines[last + 1:]).strip()
    return decl, expr.rstrip(";").rstrip()


def check_body(check: str) -> str:
    """The Dart closure for a measurement: an expression, or (it mentions `await`/`return`) a statement body."""
    if re.search(r"\b(await|return)\b", check):
        return "(tester) async {\n" + check.rstrip() + "\n}"
    return "(tester) async => (" + check.strip().rstrip(";") + ")"


@dataclass(frozen=True)
class FlutterRun:
    #: The measured value as the test printed it ("" when the item did not compile).
    value: str = ""
    #: The compiler's first complaint ("" if it compiled).
    compile_error: str = ""

    def result(self) -> str:
        return "COMPILE ERROR: " + self.compile_error if self.compile_error else self.value


def _build(folder: Path, cases: dict[int, tuple[str, str]]) -> list[tuple[str, dict[int, tuple[int, int]]]]:
    """Write the generated files of one run into `folder`; returns, per test file, its name and the (first, last)
    line of each item in it."""
    for old in folder.glob("*.dart"):
        old.unlink()
    files: list[tuple[str, dict[int, tuple[int, int]]]] = []
    keys = list(cases)
    for part, start in enumerate(range(0, len(keys), PER_FILE)):
        lines = ["import 'package:fq/brain_prelude.dart';"]
        imports: list[str] = []
        body: list[str] = []
        spans: dict[int, tuple[int, int]] = {}
        for idx in keys[start:start + PER_FILE]:
            widget, check = cases[idx]
            decl, expr = split_declarations(widget)
            if decl:  # its own library (build and check inside it), so that two items may declare the same class
                library = ("import 'package:fq/brain_prelude.dart';\n\n" + decl + "\n\nWidget build() =>\n" + expr
                           + ";\n\nFuture<Object?> Function(WidgetTester) get measure =>\n" + check_body(check) + ";\n")
                (folder / f"d{idx}.dart").write_text(library, encoding="utf-8", newline="\n")
                imports.append(f"import 'd{idx}.dart' as d{idx};")
                chunk = [f"  testWidgets('i{idx}', (tester) => runCase(tester, 'i{idx}', d{idx}.build, d{idx}.measure));"]
            else:
                chunk = [f"  testWidgets('i{idx}', (tester) => runCase(tester, 'i{idx}',", "      () =>"]
                chunk.extend(expr.split("\n"))
                chunk[-1] += ","
                chunk.extend(check_body(check).split("\n"))
                chunk[-1] += "));"
            spans[idx] = (len(body) + 1, len(body) + len(chunk))  # offsets within the body; shifted below
            body.extend(chunk)
        head = lines + imports + ["", "void main() {"]
        shift = len(head)
        text = "\n".join(head + body + ["}"]) + "\n"
        name = f"batch{part}_test.dart"
        (folder / name).write_text(text, encoding="utf-8", newline="\n")
        files.append((name, {i: (a + shift, b + shift) for i, (a, b) in spans.items()}))
    return files


def _blame(text: str, files, cases: dict[int, tuple[str, str]]) -> tuple[dict[int, str], str]:
    """(items the compiler's complaints name -> first complaint, the first complaint about the prelude or '')."""
    blamed: dict[int, str] = {}
    prelude = ""
    for m in ERROR_LINE.finditer(text):
        path, line, message = m.group(1).replace("\\", "/"), int(m.group(2)), m.group(4).strip()
        name = path.rsplit("/", 1)[-1]
        if path.startswith("lib/"):
            prelude = prelude or f"{path}:{line}: {message}"
        elif re.fullmatch(r"d\d+\.dart", name):
            idx = int(name[1:-5])
            if idx in cases:
                blamed.setdefault(idx, f"{message} (line {line} of the item's own file)")
        else:
            for fname, spans in files:
                if fname == name:
                    for idx, (lo, hi) in spans.items():
                        if lo <= line <= hi:
                            blamed.setdefault(idx, f"{message} (line {line - lo} of the snippet)")
    return blamed, prelude


def _kill(proc: subprocess.Popen) -> None:
    from code_coach.canvas.pyharness.session import kill_tree

    kill_tree(proc)


def _flutter_test(folder: Path, files: list[str], timeout: float) -> tuple[int, str]:
    """`flutter test --reporter json` on the generated files: (exit code, stdout)."""
    from code_coach.canvas.pyharness.session import child_flags

    assert FLUTTER
    out_path, err_path = folder / "out.txt", folder / "err.txt"
    rel = [f"test/b/{folder.name}/{n}" for n in files]
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        proc = subprocess.Popen([str(FLUTTER), "test", "--no-pub", "--reporter", "json", *rel], cwd=PROJECT,
                                stdin=subprocess.DEVNULL, stdout=out, stderr=err, creationflags=child_flags())
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill(proc)
            return -9, "TIMEOUT after %ss" % timeout
    return code, out_path.read_bytes().decode("utf-8", "replace") + "\n" + err_path.read_bytes().decode("utf-8", "replace")


def parse_events(stdout: str):
    """(values by item index, compile-failure text, per-test failure text by item index) from the json reporter."""
    names: dict[int, str] = {}
    values: dict[int, str] = {}
    problems: dict[int, list[str]] = {}
    results: dict[int, str] = {}
    compile_text: list[str] = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        kind = event.get("type")
        if kind == "testStart":
            test = event.get("test", {})
            names[test.get("id")] = test.get("name", "")
        elif kind == "print":
            m = RESULT.match(str(event.get("message", "")))
            if m:
                values.setdefault(int(m.group(1)[1:]), m.group(2).rstrip("\r"))
        elif kind == "error":
            tid = event.get("testID")
            text = str(event.get("error", ""))
            if names.get(tid, "").startswith("loading "):
                compile_text.append(text)
            else:
                problems.setdefault(tid, []).append(text)
        elif kind == "testDone" and not event.get("hidden"):
            results[event.get("testID")] = event.get("result", "")
    failed: dict[int, str] = {}
    for tid, name in names.items():
        m = re.fullmatch(r"i(\d+)", name)
        if m and results.get(tid, "success") != "success":
            first = next((ln.strip() for p in problems.get(tid, []) for ln in p.splitlines() if ln.strip()), "")
            failed[int(m.group(1))] = first or results.get(tid, "failed")
    return values, "\n".join(compile_text), failed


def _batch(folder: Path, cases: dict[int, tuple[str, str]], timeout: float) -> dict[int, FlutterRun]:
    results: dict[int, FlutterRun] = {}
    todo = dict(cases)
    for _ in range(8):
        if not todo:
            return results
        files = _build(folder, todo)
        code, text = _flutter_test(folder, [n for n, _ in files], timeout)
        values, compile_text, failed = parse_events(text)
        if not compile_text and not (code == -9) and (values or failed):
            for idx in todo:
                if idx in values:
                    results[idx] = FlutterRun(value=values[idx])
                elif idx in failed:
                    results[idx] = FlutterRun(value="ERROR: " + failed[idx])
                else:
                    results[idx] = FlutterRun(value="ERROR: the test never ran")
            return results
        blamed, prelude = _blame(compile_text or text, files, todo)
        if prelude:  # the harness itself: a bug in this file
            raise AssertionError("the Flutter oracle's own prelude does not compile:\n" + prelude)
        if blamed:
            for idx, message in blamed.items():
                results[idx] = FlutterRun(compile_error=message)
                del todo[idx]
            continue
        if len(todo) == 1:
            (idx,) = todo
            results[idx] = FlutterRun(compile_error="did not run: " + ((compile_text or text).strip()[:300] or f"exit code {code}"))
            return results
        keys = list(todo)
        half = len(keys) // 2
        for part in (keys[:half], keys[half:]):
            results.update(_batch(folder, {k: todo[k] for k in part}, timeout))
        return results
    for idx in todo:
        results[idx] = FlutterRun(compile_error="did not compile after removing the others that failed")
    return results


def run_batch(cases: list[tuple[str, str]], timeout: float = 900.0) -> list[FlutterRun]:
    """Run every (widget code, check) pair for real, in one `flutter test` where possible."""
    if not cases:
        return []
    project()
    folder = PROJECT / "test" / "b" / uuid.uuid4().hex[:10]
    folder.mkdir(parents=True)
    try:
        found = _batch(folder, dict(enumerate(cases)), timeout)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    return [found[i] for i in range(len(cases))]


def flutter_values(cases: list[tuple[str, str]], timeout: float = 900.0) -> list[str]:
    """The measured value of each (widget code, check) as the real Flutter reports it; a compile failure is
    'COMPILE ERROR: ...' and a Flutter error 'ERROR: ...'."""
    return [r.result() for r in run_batch(cases, timeout)]
