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
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from code_coach.engine import RUN_TIMEOUT_SECONDS

_RUNNER = Path(__file__).with_name("_trace_runner.py")
_SENTINEL = "<<<CODE_COACH_TRACE>>>"

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


def suggest_call(code: str, examples: list[str]) -> str:
    """A call line that will actually exercise the student's function.

    Matches the example's variable names to the function's parameters, so
    `two_sum(nums, target)` plus `nums = [...], target = 9` becomes
    `two_sum([...], 9)`. Falls back to positional order when the names differ.
    """
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


def trace_code(
    code: str,
    *,
    call: str = "",
    timeout: float = RUN_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Run `code` (optionally followed by `call`) and return execution steps."""
    source = code if not call.strip() else f"{code.rstrip()}\n\n{call.strip()}\n"

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(source)
            tmp_path = Path(tmp.name)

        proc = subprocess.run(
            [sys.executable, str(_RUNNER), str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
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
