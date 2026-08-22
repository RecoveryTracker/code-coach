"""Step-through visualisation of a student's code.

`explain_code` says what each line means. This says what the *data* looked like
while it ran — which cell `left` was pointing at, what was in `seen` on step 12,
how the linked list was wired at the moment it broke.

The program runs in a subprocess under a line tracer (see `_trace_runner`), so
a runaway loop is killed by the same timeout as a normal Run.
"""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from code_coach.engine import RUN_TIMEOUT_SECONDS

_RUNNER = Path(__file__).with_name("_trace_runner.py")
_JS_RUNNER = Path(__file__).with_name("_js_trace_runner.js")
_DART_RUNNER = Path(__file__).with_name("_dart_trace_runner.dart")
_SENTINEL = "<<<CODE_COACH_TRACE>>>"

# Dart pays for two VM starts — the tracer and the traced program — plus the
# debugger handshake between them, none of which a Python trace has to do.
_DART_TIMEOUT = 25.0


def _tool(name: str) -> str:
    """Resolve a command to a real path.

    Windows ships `dart` as `dart.bat`, and subprocess does not apply PATHEXT
    to the program name — so a bare "dart" raised FileNotFoundError on a
    machine where Dart was installed and working.
    """
    return shutil.which(name) or name


def _dart_argv(target: Path) -> list[str]:
    """Dart is traced through its own VM service.

    Same shape as the JavaScript runner: the debugger is driven from the
    language's own runtime, because that's the only thing that can read a
    scope from outside it.
    """
    return [_tool("dart"), "run", str(_DART_RUNNER), str(target)]


def _node_argv(target: Path) -> list[str]:
    """JavaScript is traced by Node's own inspector, driven in-process.

    JavaScript has no sys.settrace: you can't enumerate the variables of a
    scope from inside the language. The debugger protocol can, so the runner
    pauses on each statement and reads the scope chain, and emits exactly the
    payload the Python tracer does.
    """
    return [_tool("node"), str(_JS_RUNNER), str(target)]

# "nums = [2, 7, 11, 15], target = 9  ->  [0, 1]" — split the inputs from the
# expected result, which we don't need in order to make the call.
_ARROW = re.compile(r"\s*(?:->|→|=>)\s*")


def _top_level_functions(code: str) -> list[ast.FunctionDef]:
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return []
    return [n for n in tree.body if isinstance(n, ast.FunctionDef)]


def _calls_anything(code: str) -> bool:
    """True if the module does something at import time besides define things.

    A LeetCode answer is usually just `def two_sum(...)`, which produces no
    trace at all — there's nothing to watch until someone calls it.
    """
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # docstring
        return True
    return False


def _split_top_level(text: str) -> list[str]:
    """Split on commas that separate arguments, not ones inside a literal."""
    parts, depth, current = [], 0, ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current)
            current = ""
            continue
        current += ch
    parts.append(current)
    return [p.strip() for p in parts if p.strip()]


def _parse_example_args(example: str) -> dict[str, Any]:
    """`nums = [2, 7, 11, 15], target = 9  ->  [0, 1]` → {'nums': [...], 'target': 9}"""
    inputs = _ARROW.split(example)[0].strip()
    if not inputs:
        return {}
    try:
        tree = ast.parse(inputs, mode="exec")
    except SyntaxError:
        # Commas between assignments make this invalid as one statement, so
        # rebuild it as separate lines and retry.
        try:
            tree = ast.parse("\n".join(_split_top_level(inputs)))
        except SyntaxError:
            return {}

    out: dict[str, Any] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            out[target.id] = ast.literal_eval(node.value)
        except (ValueError, SyntaxError):
            continue
    return out


def _parse_example_values(example: str) -> list[Any]:
    """Bare literals, in order: `["eat","tea"]  ->  [["eat","tea"]]` → [[...]]

    Plenty of examples skip the parameter names and just show the input, so
    matching on names alone leaves those problems with no runnable call at all.
    """
    inputs = _ARROW.split(example)[0].strip()
    if not inputs:
        return []
    out: list[Any] = []
    for part in _split_top_level(inputs):
        try:
            out.append(ast.literal_eval(part))
        except (ValueError, SyntaxError):
            return []  # a non-literal means this isn't a positional example
    return out


# `function twoSum(nums, target) {` and `const twoSum = (nums, target) =>`.
_JS_FUNCTION = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)"
    r"|^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*"
    r"(?:async\s*)?\(([^)]*)\)\s*=>",
    re.MULTILINE,
)


def _js_functions(code: str) -> list[tuple[str, list[str]]]:
    """Top-level function names and their parameters, without a JS parser.

    Only used to guess a demo call, so a regex is honest here: the worst case
    is no suggestion, and the student can type their own call.
    """
    out: list[tuple[str, list[str]]] = []
    for match in _JS_FUNCTION.finditer(code):
        name = match.group(1) or match.group(3)
        raw = match.group(2) if match.group(1) else match.group(4)
        if not name:
            continue
        params = [
            p.strip().split("=")[0].strip()
            for p in (raw or "").split(",")
            if p.strip()
        ]
        out.append((name, params))
    return out


def _literal(value: Any, language: str) -> str:
    """A source literal for this value in the target language.

    JSON happens to be valid source in both JavaScript and Dart for everything
    an example contains, and it's what turns Python's True/None into true/null
    rather than leaving an undefined name in the generated call.
    """
    if language in ("javascript", "typescript", "dart"):
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            return repr(value)
    return repr(value)


def suggest_call(code: str, examples: list[str], language: str = "python") -> str:
    """A call line that will actually exercise the student's function.

    Matches the example's variable names to the function's parameters, so
    `two_sum(nums, target)` plus `nums = [...], target = 9` becomes
    `two_sum([...], 9)`. Falls back to positional order when the names differ.
    """
    if language in ("javascript", "typescript"):
        return _suggest_js_call(code, examples, language)
    if language == "dart":
        return _suggest_dart_call(code, examples)

    funcs = _top_level_functions(code)
    if not funcs:
        return ""
    fn = funcs[-1]
    params = [a.arg for a in fn.args.args]

    # Named form first: `nums = [...], target = 9`.
    for example in examples:
        values = _parse_example_args(example)
        if not values:
            continue
        if all(p in values for p in params):
            args = [repr(values[p]) for p in params]
        elif len(values) == len(params):
            args = [repr(v) for v in values.values()]
        else:
            continue
        return f"{fn.name}({', '.join(args)})"

    # Then the bare form: `["eat","tea"]` with no parameter names at all.
    for example in examples:
        positional = _parse_example_values(example)
        if len(positional) == len(params) and params:
            return f"{fn.name}({', '.join(repr(v) for v in positional)})"

    return f"{fn.name}()" if not params else ""


# `List<int> twoSum(List<int> nums, int target) {` — a return type, a name,
# then parameters. Generic arguments mean the parameter list can contain
# commas inside angle brackets, which the split below has to survive.
_DART_FUNCTION = re.compile(
    r"^[A-Za-z_$][\w<>,\s\[\]?]*\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*(?:async\s*)?\{",
    re.MULTILINE,
)


def _suggest_dart_call(code: str, examples: list[str]) -> str:
    """A `main` that exercises the student's function.

    Dart won't run a bare expression, so unlike Python the call has to be
    wrapped in an entry point — and if their file already has one, theirs
    stands and we add nothing.
    """
    if re.search(r"^\s*(?:void\s+)?main\s*\(", code, re.MULTILINE):
        return ""

    found = [
        (m.group(1), m.group(2))
        for m in _DART_FUNCTION.finditer(code)
        if m.group(1) not in ("if", "for", "while", "switch", "catch", "main")
    ]
    if not found:
        return ""
    name, raw = found[-1]
    params = [p.strip().split()[-1] for p in raw.split(",") if p.strip()]

    for example in examples:
        values = _parse_example_args(example)
        if not values:
            continue
        if all(p in values for p in params):
            args = [_literal(values[p], "dart") for p in params]
        elif len(values) == len(params):
            args = [_literal(v, "dart") for v in values.values()]
        else:
            continue
        return f"void main() {{ print({name}({', '.join(args)})); }}"

    for example in examples:
        positional = _parse_example_values(example)
        if len(positional) == len(params) and params:
            args = [_literal(v, "dart") for v in positional]
            return f"void main() {{ print({name}({', '.join(args)})); }}"

    return f"void main() {{ print({name}()); }}" if not params else ""


def _suggest_js_call(code: str, examples: list[str], language: str) -> str:
    """The same idea for JavaScript, wrapped in console.log so the answer shows.

    Python's tracer reports the returned value on the return event; the
    inspector doesn't hand one back the same way, so the result is printed
    instead and lands in the run's output.
    """
    funcs = _js_functions(code)
    if not funcs:
        return ""
    name, params = funcs[-1]

    for example in examples:
        values = _parse_example_args(example)
        if not values:
            continue
        if all(p in values for p in params):
            args = [_literal(values[p], language) for p in params]
        elif len(values) == len(params):
            args = [_literal(v, language) for v in values.values()]
        else:
            continue
        return f"console.log({name}({', '.join(args)}));"

    for example in examples:
        positional = _parse_example_values(example)
        if len(positional) == len(params) and params:
            args = [_literal(v, language) for v in positional]
            return f"console.log({name}({', '.join(args)}));"

    return f"console.log({name}());" if not params else ""


def trace_code(
    code: str,
    *,
    call: str = "",
    timeout: float = RUN_TIMEOUT_SECONDS,
    language: str = "python",
) -> dict[str, Any]:
    """Run `code` (optionally followed by `call`) and return execution steps."""
    source = code if not call.strip() else f"{code.rstrip()}\n\n{call.strip()}\n"

    if language in ("javascript", "typescript"):
        suffix, argv = ".js", _node_argv
    elif language == "dart":
        suffix, argv = ".dart", _dart_argv
        timeout = max(timeout, _DART_TIMEOUT)
    else:
        suffix, argv = ".py", None

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(source)
            tmp_path = Path(tmp.name)

        command = (
            argv(tmp_path)
            if argv
            else [sys.executable, str(_RUNNER), str(tmp_path)]
        )
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        tool, where = (
            ("the Dart SDK", "dart.dev")
            if language == "dart"
            else ("Node", "nodejs.org")
        )
        return _empty(
            f"Code tracing for this language needs {tool} on your PATH — "
            f"install it from {where} and restart the app."
        )
    except subprocess.TimeoutExpired:
        return _empty(
            f"Stopped after {timeout:g}s — check for a loop that never ends."
        )
    except OSError as exc:
        return _empty(f"Couldn't run the visualiser: {exc}")
    finally:
        if tmp_path is not None:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass

    marker = proc.stdout.find(_SENTINEL)
    if marker < 0:
        detail = (proc.stderr or "").strip().splitlines()
        return _empty(detail[-1] if detail else "The program produced no trace.")

    try:
        payload = json.loads(proc.stdout[marker + len(_SENTINEL):])
    except json.JSONDecodeError:
        return _empty("The trace came back unreadable.")

    payload.setdefault("steps", [])
    payload["ok"] = True
    payload["ran"] = source
    return payload


def _empty(note: str) -> dict[str, Any]:
    return {
        "ok": False,
        "steps": [],
        "truncated": False,
        "stdout": "",
        "stderr": "",
        "error": note,
        "ran": "",
    }
