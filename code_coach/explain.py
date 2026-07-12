"""Local code explainer — plain-English walkthrough of student code.

No cloud AI: an AST walk explains what each line *does*, and a traced run
(print patched to record its caller's line number) explains *why* the
output looks the way it does. Same trust model as the Run button — the
student's own code, temp file, short timeout.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

TRACE_TIMEOUT_SECONDS = 3.0

# ── Trace runner (executed in a subprocess) ─────────────────────────
# Patches print to record (line, text) per call, then execs the student
# file. Writes a JSON report: {"trace": [...], "error": {...} | null}.
_RUNNER = r'''
import builtins, io, json, sys, traceback

SRC = sys.argv[1]
OUT = sys.argv[2]

_trace = []
_real_print = builtins.print

def _coach_print(*args, **kwargs):
    buf = io.StringIO()
    kw = dict(kwargs)
    kw["file"] = buf
    _real_print(*args, **kw)
    try:
        line = sys._getframe(1).f_lineno
    except Exception:
        line = 0
    if len(_trace) < 500:
        _trace.append({"line": line, "text": buf.getvalue()})
    _real_print(*args, **kwargs)

builtins.print = _coach_print

_error = None
try:
    with open(SRC, "r", encoding="utf-8") as f:
        source = f.read()
    code = compile(source, "your code", "exec")
    exec(code, {"__name__": "__main__"})
except SystemExit:
    pass
except BaseException as e:
    line = None
    for fr in traceback.extract_tb(e.__traceback__):
        if fr.filename == "your code":
            line = fr.lineno
    _error = {
        "type": type(e).__name__,
        "message": str(e),
        "line": line,
    }
finally:
    builtins.print = _real_print
    try:
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump({"trace": _trace, "error": _error}, f)
    except Exception:
        pass
'''


def _traced_run(code: str) -> dict[str, Any]:
    """Run the code with print-tracing. Returns {trace, error, timeout}."""
    tmpdir = tempfile.mkdtemp(prefix="code-coach-explain-")
    src = Path(tmpdir) / "student.py"
    runner = Path(tmpdir) / "runner.py"
    out = Path(tmpdir) / "trace.json"
    try:
        src.write_text(code, encoding="utf-8")
        runner.write_text(_RUNNER, encoding="utf-8")
        try:
            subprocess.run(
                [sys.executable, str(runner), str(src), str(out)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=TRACE_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            return {"trace": [], "error": None, "timeout": True}
        if out.exists():
            data = json.loads(out.read_text(encoding="utf-8"))
            data["timeout"] = False
            return data
        return {"trace": [], "error": None, "timeout": False}
    except Exception:
        return {"trace": [], "error": None, "timeout": False}
    finally:
        for p in (src, runner, out):
            try:
                p.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            Path(tmpdir).rmdir()
        except OSError:
            pass


# ── Small helpers ───────────────────────────────────────────────────

_BINOP_WORDS = {
    ast.Add: "plus",
    ast.Sub: "minus",
    ast.Mult: "times",
    ast.Div: "divided by",
    ast.FloorDiv: "divided by (whole part only)",
    ast.Mod: "the remainder after dividing by",
    ast.Pow: "to the power of",
}

_COMPARE_WORDS = {
    ast.Gt: "is greater than",
    ast.Lt: "is less than",
    ast.GtE: "is at least",
    ast.LtE: "is at most",
    ast.Eq: "is equal to",
    ast.NotEq: "is not equal to",
    ast.In: "is inside",
    ast.NotIn: "is not inside",
    ast.Is: "is",
    ast.IsNot: "is not",
}


def _const_value(node: ast.AST) -> Any:
    """Evaluate simple constant math (2 + 3, 10 * 4). None if not constant."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _const_value(node.operand)
        if isinstance(v, (int, float)):
            return -v
        return None
    if isinstance(node, ast.BinOp):
        left = _const_value(node.left)
        right = _const_value(node.right)
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return None
        try:
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow) and abs(right) < 100:
                return left**right
        except (ZeroDivisionError, OverflowError, ValueError):
            return None
    return None


def _fmt_value(v: Any) -> str:
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, float) and v == int(v):
        return str(int(v)) if abs(v) < 1e15 else str(v)
    return str(v)


def _src(node: ast.AST, code_lines: list[str]) -> str:
    """The source text of a node (unparse fallback)."""
    try:
        return ast.unparse(node)
    except Exception:
        line = getattr(node, "lineno", None)
        if line and 1 <= line <= len(code_lines):
            return code_lines[line - 1].strip()
        return ""


def _describe_expr(node: ast.AST, *, user_functions: set[str]) -> str:
    """Short beginner-English phrase for a value/expression."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            return f'the text {_fmt_value(node.value)}'
        if node.value is True or node.value is False:
            return f"the value {node.value}"
        if node.value is None:
            return "the empty value None"
        return f"the number {_fmt_value(node.value)}"
    if isinstance(node, ast.Name):
        return f"the current value of `{node.id}`"
    if isinstance(node, ast.JoinedStr):
        holes = [
            v.value.id
            for v in node.values
            if isinstance(v, ast.FormattedValue) and isinstance(v.value, ast.Name)
        ]
        if holes:
            names = " and ".join(f"`{h}`" for h in holes)
            return (
                f"an f-string — text with the current value of {names} "
                "filled into the {curly braces}"
            )
        return "an f-string — text with values filled into the {curly braces}"
    if isinstance(node, ast.BinOp):
        result = _const_value(node)
        op_word = None
        for op_type, word in _BINOP_WORDS.items():
            if isinstance(node.op, op_type):
                op_word = word
                break
        left = _describe_operand(node.left, user_functions=user_functions)
        right = _describe_operand(node.right, user_functions=user_functions)
        if op_word is None:
            return f"the result of `{ast.unparse(node)}`"
        base = f"{left} {op_word} {right}"
        if result is not None:
            return f"{base} (Python works this out: {_fmt_value(result)})"
        return base
    if isinstance(node, ast.Compare):
        return _describe_condition(node, user_functions=user_functions)
    if isinstance(node, ast.List):
        n = len(node.elts)
        if n == 0:
            return "a new empty list"
        items = ", ".join(ast.unparse(e) for e in node.elts[:6])
        more = ", …" if n > 6 else ""
        return f"a list holding {n} item{'s' if n != 1 else ''}: {items}{more}"
    if isinstance(node, ast.Dict):
        return f"a dictionary with {len(node.keys)} entry(ies) — pairs of key: value"
    if isinstance(node, ast.Subscript):
        target = _src_name(node.value)
        if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, int):
            i = node.slice.value
            pos = "first" if i == 0 else ("last" if i == -1 else f"position {i}")
            note = " (counting starts at 0)" if i > 0 else ""
            return f"the {pos} item of `{target}`{note}"
        return f"one item picked out of `{target}`"
    if isinstance(node, ast.Call):
        return _describe_call(node, user_functions=user_functions)
    if isinstance(node, ast.Input if hasattr(ast, "Input") else ast.Call):
        pass
    try:
        return f"the result of `{ast.unparse(node)}`"
    except Exception:
        return "this value"


def _src_name(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "it"


def _describe_operand(node: ast.AST, *, user_functions: set[str]) -> str:
    """Compact operand description for inside math phrases."""
    if isinstance(node, ast.Constant):
        return _fmt_value(node.value)
    if isinstance(node, ast.Name):
        return f"`{node.id}`"
    return f"`{_src_name(node)}`"


def _describe_call(node: ast.Call, *, user_functions: set[str]) -> str:
    name = ""
    if isinstance(node.func, ast.Name):
        name = node.func.id
    elif isinstance(node.func, ast.Attribute):
        name = node.func.attr

    if name == "input":
        if node.args and isinstance(node.args[0], ast.Constant):
            return (
                f"whatever the user types after seeing {_fmt_value(node.args[0].value)} "
                "(the program pauses and waits)"
            )
        return "whatever the user types in (the program pauses and waits)"
    if name == "len":
        target = _src_name(node.args[0]) if node.args else "it"
        return f"how many items are in `{target}`"
    if name == "str":
        return "the value turned into text"
    if name == "int":
        return "the value turned into a whole number"
    if name == "float":
        return "the value turned into a decimal number"
    if name == "range":
        return "a counting sequence"
    if name in user_functions:
        return f"whatever your function `{name}(...)` gives back"
    try:
        return f"the result of `{ast.unparse(node)}`"
    except Exception:
        return f"the result of calling `{name}(...)`"


def _describe_condition(node: ast.AST, *, user_functions: set[str]) -> str:
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left = _describe_operand(node.left, user_functions=user_functions)
        right = _describe_operand(node.comparators[0], user_functions=user_functions)
        for op_type, words in _COMPARE_WORDS.items():
            if isinstance(node.ops[0], op_type):
                return f"{left} {words} {right}"
    if isinstance(node, ast.BoolOp):
        joiner = " AND " if isinstance(node.op, ast.And) else " OR "
        parts = [
            _describe_condition(v, user_functions=user_functions)
            for v in node.values
        ]
        return joiner.join(parts)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        inner = _describe_condition(node.operand, user_functions=user_functions)
        return f"NOT ({inner})"
    if isinstance(node, ast.Name):
        return f"`{node.id}` is truthy (not empty / not zero / not False)"
    if isinstance(node, ast.Constant):
        return f"{_fmt_value(node.value)} (always the same!)"
    return f"`{_src_name(node)}` is true"


def _describe_range(node: ast.Call) -> str:
    """English for range(...) used in a for loop."""
    args = node.args
    if len(args) == 1:
        n = _const_value(args[0])
        if isinstance(n, int) and n >= 0:
            if n == 0:
                return "zero times — range(0) is empty, so the body never runs"
            seq = ", ".join(str(i) for i in range(min(n, 4)))
            tail = f", … {n - 1}" if n > 4 else ""
            return f"{n} time{'s' if n != 1 else ''}, counting {seq}{tail}"
        return f"once for each number that `range({_src_name(args[0])})` counts out (starting at 0)"
    if len(args) >= 2:
        a, b = _const_value(args[0]), _const_value(args[1])
        if isinstance(a, int) and isinstance(b, int):
            step = _const_value(args[2]) if len(args) > 2 else 1
            if isinstance(step, int) and step != 0:
                count = max(0, -(-(b - a) // step) if step > 0 else -(-(a - b) // -step))
                return (
                    f"counting from {a} up to (but not including) {b}"
                    + (f" in steps of {step}" if step != 1 else "")
                    + f" — {count} pass{'es' if count != 1 else ''}"
                )
        return "counting from the first number up to (but not including) the second"
    return "once per number in the range"


# ── Statement walk ──────────────────────────────────────────────────


class _Walker:
    def __init__(self, code_lines: list[str], user_functions: set[str]) -> None:
        self.code_lines = code_lines
        self.user_functions = user_functions
        self.items: list[dict[str, Any]] = []
        # variable names assigned so far, in walk order (reassignment wording)
        self.seen_names: set[str] = set()
        # line → enclosing loop header line (for output notes)
        self.loop_of_line: dict[int, int] = {}
        self.counts = {
            "assign": 0,
            "print": 0,
            "for": 0,
            "while": 0,
            "if": 0,
            "def": 0,
            "call": 0,
            "input": 0,
        }

    def add(self, node: ast.AST, depth: int, text: str, *, line: int | None = None) -> None:
        ln = line if line is not None else getattr(node, "lineno", 0)
        src = ""
        if 1 <= ln <= len(self.code_lines):
            src = self.code_lines[ln - 1].strip()
        # One-liner compound (for i in ...: print(i)) — show just this
        # statement for the body row, not the whole line again.
        if any(it["line"] == ln for it in self.items):
            try:
                src = ast.unparse(node)
            except Exception:
                pass
        self.items.append({"line": ln, "depth": depth, "source": src, "text": text})

    def mark_loop(self, body: list[ast.stmt], header_line: int) -> None:
        for stmt in body:
            for sub in ast.walk(stmt):
                ln = getattr(sub, "lineno", None)
                if ln is not None and ln not in self.loop_of_line:
                    self.loop_of_line[ln] = header_line

    # -- statements --

    def walk_body(self, body: list[ast.stmt], depth: int) -> None:
        for stmt in body:
            self.statement(stmt, depth)

    def statement(self, node: ast.stmt, depth: int) -> None:
        uf = self.user_functions
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
                value = _describe_expr(node.value, user_functions=uf)
                uses_self = any(
                    isinstance(sub, ast.Name) and sub.id == name
                    for sub in ast.walk(node.value)
                )
                if name not in self.seen_names:
                    self.counts["assign"] += 1
                    self.seen_names.add(name)
                    self.add(
                        node,
                        depth,
                        f"makes a variable named `{name}` and stores {value} in it",
                    )
                elif uses_self:
                    self.add(
                        node,
                        depth,
                        f"updates `{name}`: works out {value} and stores the "
                        f"result back into `{name}` (the new value replaces "
                        "the old one)",
                    )
                else:
                    self.add(
                        node,
                        depth,
                        f"changes `{name}`: now it holds {value} instead",
                    )
                if isinstance(node.value, ast.Call):
                    self._note_input(node.value)
                return
            if isinstance(target, ast.Subscript):
                self.add(
                    node,
                    depth,
                    f"replaces one item inside `{_src_name(target.value)}` with "
                    f"{_describe_expr(node.value, user_functions=uf)}",
                )
                return
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            self.seen_names.add(name)
            value = _describe_operand(node.value, user_functions=uf)
            word = None
            for op_type, w in _BINOP_WORDS.items():
                if isinstance(node.op, op_type):
                    word = w
                    break
            if isinstance(node.op, ast.Add):
                self.add(
                    node,
                    depth,
                    f"updates `{name}`: takes its current value and adds {value} to it",
                )
            elif word:
                self.add(
                    node,
                    depth,
                    f"updates `{name}`: its current value {word} {value}",
                )
            else:
                self.add(node, depth, f"updates the variable `{name}`")
            return
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            fname = call.func.id if isinstance(call.func, ast.Name) else (
                call.func.attr if isinstance(call.func, ast.Attribute) else ""
            )
            if fname == "print":
                self.counts["print"] += 1
                self.add(node, depth, self._describe_print(call))
                self._note_input(call)
                return
            if fname == "append" and isinstance(call.func, ast.Attribute):
                target = _src_name(call.func.value)
                what = (
                    _describe_expr(call.args[0], user_functions=uf)
                    if call.args
                    else "a value"
                )
                self.add(node, depth, f"adds {what} to the end of the list `{target}`")
                return
            if fname in uf:
                self.counts["call"] += 1
                self.add(
                    node,
                    depth,
                    f"calls your function `{fname}(...)` — Python jumps to its "
                    "`def` line, runs the indented recipe, then comes back here",
                )
                return
            self.add(
                node,
                depth,
                f"calls `{_src_name(call)}`",
            )
            return
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                self.add(
                    node,
                    depth,
                    "a piece of text sitting on its own — Python reads it but "
                    "shows nothing (use print(...) to display it)",
                )
                return
        if isinstance(node, ast.For):
            self.counts["for"] += 1
            var = _src_name(node.target)
            if isinstance(node.target, ast.Name):
                self.seen_names.add(node.target.id)
            header_line = node.lineno
            self.mark_loop(node.body, header_line)
            if (
                isinstance(node.iter, ast.Call)
                and isinstance(node.iter.func, ast.Name)
                and node.iter.func.id == "range"
            ):
                times = _describe_range(node.iter)
                self.add(
                    node,
                    depth,
                    f"a loop — repeats the indented lines below {times}. "
                    f"Each pass, `{var}` holds the current number",
                )
            elif isinstance(node.iter, (ast.Name, ast.List)):
                seq = _src_name(node.iter)
                self.add(
                    node,
                    depth,
                    f"a loop — goes through `{seq}` one item at a time; "
                    f"each pass, `{var}` holds the current item",
                )
            else:
                self.add(
                    node,
                    depth,
                    f"a loop — repeats the indented lines once per item, "
                    f"with `{var}` holding the current one",
                )
            self.walk_body(node.body, depth + 1)
            if node.orelse:
                self.walk_body(node.orelse, depth + 1)
            return
        if isinstance(node, ast.While):
            self.counts["while"] += 1
            self.mark_loop(node.body, node.lineno)
            cond = _describe_condition(node.test, user_functions=uf)
            self.add(
                node,
                depth,
                f"a while-loop — keeps repeating the indented lines as long as "
                f"{cond}; the moment that stops being true, the loop ends",
            )
            self.walk_body(node.body, depth + 1)
            return
        if isinstance(node, ast.If):
            self.counts["if"] += 1
            self._walk_if(node, depth, first=True)
            return
        if isinstance(node, ast.FunctionDef):
            self.counts["def"] += 1
            self.seen_names.update(a.arg for a in node.args.args)
            params = ", ".join(a.arg for a in node.args.args)
            takes = (
                f" It expects you to hand it: {params}." if params else ""
            )
            self.add(
                node,
                depth,
                f"defines a function named `{node.name}` — a recipe Python "
                f"memorizes but does NOT run yet.{takes} It only runs when "
                f"you call `{node.name}(...)`",
            )
            self.walk_body(node.body, depth + 1)
            return
        if isinstance(node, ast.Return):
            if node.value is not None:
                value = _describe_expr(node.value, user_functions=uf)
                self.add(
                    node,
                    depth,
                    f"hands {value} back to wherever the function was called from",
                )
            else:
                self.add(node, depth, "ends the function here and hands back nothing")
            return
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = ", ".join(a.name for a in node.names)
            self.add(
                node,
                depth,
                f"brings in extra tools ({names}) so this file can use them",
            )
            return
        if isinstance(node, ast.Pass):
            self.add(node, depth, "does nothing on purpose — a placeholder")
            return
        if isinstance(node, ast.Break):
            self.add(node, depth, "jumps out of the loop right now, skipping the rest")
            return
        if isinstance(node, ast.Continue):
            self.add(
                node, depth, "skips the rest of this pass and starts the next one"
            )
            return
        # Generic fallback
        self.add(node, depth, f"runs `{_src(node, self.code_lines)}`")

    def _walk_if(self, node: ast.If, depth: int, *, first: bool) -> None:
        cond = _describe_condition(node.test, user_functions=self.user_functions)
        opener = "a decision" if first else "otherwise, another check (elif)"
        self.add(
            node,
            depth,
            f"{opener} — Python checks whether {cond}; the indented lines "
            "below only run when that is true",
        )
        self.walk_body(node.body, depth + 1)
        if not node.orelse:
            return
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self._walk_if(node.orelse[0], depth, first=False)
            return
        else_line = node.orelse[0].lineno - 1
        src_ok = (
            1 <= else_line <= len(self.code_lines)
            and self.code_lines[else_line - 1].strip().startswith("else")
        )
        self.add(
            node.orelse[0],
            depth,
            "otherwise (else) — this block runs only when the check above was false",
            line=else_line if src_ok else node.orelse[0].lineno,
        )
        self.walk_body(node.orelse, depth + 1)

    def _describe_print(self, call: ast.Call) -> str:
        uf = self.user_functions
        if not call.args:
            return "prints a blank line"
        parts = [_describe_expr(a, user_functions=uf) for a in call.args]
        if len(parts) == 1:
            body = parts[0]
        else:
            body = ", then ".join(parts) + " — all together on one line"
        return f"shows {body} on the screen"

    def _note_input(self, call: ast.Call) -> None:
        for sub in ast.walk(call):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Name)
                and sub.func.id == "input"
            ):
                self.counts["input"] += 1
                return


def _comment_items(code_lines: list[str]) -> list[dict[str, Any]]:
    out = []
    for i, raw in enumerate(code_lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("#"):
            out.append(
                {
                    "line": i,
                    "depth": 0,
                    "source": stripped,
                    "text": "a comment — a note for humans; Python skips it completely",
                }
            )
    return out


# ── Error translation ───────────────────────────────────────────────


def _friendly_error(err: dict[str, Any]) -> str:
    etype = err.get("type", "")
    msg = err.get("message", "")
    line = err.get("line")
    at = f" (line {line})" if line else ""
    if etype == "NameError":
        return (
            f"Your program hit a NameError{at}: {msg}. That means it used a "
            "name Python has never seen — usually a typo, or using a variable "
            "before the line that creates it."
        )
    if etype == "TypeError" and "str" in msg and "int" in msg:
        return (
            f"Your program hit a TypeError{at}: you tried to glue text and a "
            "number together with +. Turn the number into text first with "
            'str(...), or use an f-string: f"score: {points}".'
        )
    if etype == "TypeError":
        return (
            f"Your program hit a TypeError{at}: {msg}. Two values didn't fit "
            "together — check that you're combining the right kinds of things."
        )
    if etype == "ZeroDivisionError":
        return f"Your program divided by zero{at} — Python can't do that."
    if etype == "IndexError":
        return (
            f"Your program hit an IndexError{at}: it asked a list for a "
            "position that doesn't exist. Remember positions start at 0, so a "
            "3-item list has positions 0, 1, 2."
        )
    if etype == "KeyError":
        return (
            f"Your program hit a KeyError{at}: it asked a dictionary for a key "
            f"({msg}) that isn't in it."
        )
    if etype == "ValueError" and "int" in msg:
        return (
            f"Your program hit a ValueError{at}: int(...) was given text that "
            "isn't a number, so it couldn't convert it."
        )
    if etype == "EOFError":
        return (
            "Your code calls input(...), which waits for someone to type. The "
            "explainer can't type back, so the run stopped there — in the real "
            "Run this is where your program would pause for the user."
        )
    if etype == "IndentationError":
        return (
            f"Python hit an IndentationError{at}: the spaces at the start of a "
            "line don't line up. Lines inside a loop, if, or def must be "
            "indented the same amount (4 spaces is standard)."
        )
    if etype == "RecursionError":
        return (
            f"Your program hit a RecursionError{at}: a function kept calling "
            "itself with no way to stop."
        )
    return f"Your program stopped with a {etype}{at}: {msg}"


def _friendly_syntax_error(exc: SyntaxError) -> str:
    line = exc.lineno or 0
    at = f" on line {line}" if line else ""
    msg = exc.msg or "invalid syntax"
    hints = []
    if "was never closed" in msg or "EOF" in msg.upper():
        hints.append("check for a missing closing quote, ) or ]")
    if "expected ':'" in msg:
        hints.append("lines that start a block (if / for / while / def) need a : at the end")
    if "invalid syntax" in msg and not hints:
        hints.append(
            "look for a missing colon, quote, or bracket right around that spot"
        )
    hint = f" Tip: {hints[0]}." if hints else ""
    return (
        f"Python couldn't read this yet — a SyntaxError{at}: {msg}.{hint} "
        "Nothing runs until the sentence is complete."
    )


# ── Output walkthrough ──────────────────────────────────────────────


def _output_notes(
    trace: list[dict[str, Any]],
    walker: _Walker,
    code_lines: list[str],
    error: dict[str, Any] | None,
    timeout: bool,
    has_print: bool,
) -> list[str]:
    notes: list[str] = []
    if timeout:
        notes.append(
            "Your program never finished — it ran for 3 seconds and was "
            "stopped. That usually means a while-loop whose condition never "
            "becomes false. Check what would ever end the loop."
        )
        return notes

    if not trace:
        if not has_print:
            notes.append(
                "There's no output because nothing in your code calls "
                "print(...). Variables hold values silently — print is what "
                "puts them on the screen."
            )
        elif error:
            notes.append(
                "No output appeared: the error above stopped the program "
                "before any print(...) line got its turn."
            )
        else:
            notes.append(
                "No output appeared. Your print lines may be inside a block "
                "that never ran (a loop with zero passes, an if that was "
                "false, or a function that's defined but never called)."
            )
        return notes

    # Group consecutive occurrences by code line, preserving first-seen order.
    by_line: dict[int, list[str]] = {}
    order: list[int] = []
    for t in trace:
        ln = int(t.get("line") or 0)
        if ln not in by_line:
            by_line[ln] = []
            order.append(ln)
        by_line[ln].append(str(t.get("text", "")).rstrip("\n"))

    out_pos = 1
    total_out = sum(len(v) for v in by_line.values())
    for ln in order:
        outs = by_line[ln]
        src = (
            code_lines[ln - 1].strip()
            if 1 <= ln <= len(code_lines)
            else "print(...)"
        )
        loop_line = walker.loop_of_line.get(ln)
        shown = ", ".join(f"“{o}”" for o in outs[:5])
        more = f", … ({len(outs)} total)" if len(outs) > 5 else ""
        if len(outs) == 1:
            where = (
                f"output line {out_pos}"
                if total_out > 1
                else "the output"
            )
            notes.append(f"Line {ln} `{src}` printed {where}: {shown}.")
        else:
            because = (
                f" — once per pass of the loop on line {loop_line}"
                if loop_line
                else ""
            )
            notes.append(
                f"Line {ln} `{src}` ran {len(outs)} times{because}, printing: "
                f"{shown}{more}. That's why you see {len(outs)} lines from "
                "this one line of code."
            )
        out_pos += len(outs)

    if error:
        notes.append(
            "Then the program stopped early because of the error above — any "
            "prints after that point never ran."
        )
    return notes


# ── Summary ─────────────────────────────────────────────────────────


def _summary(walker: _Walker, error: bool, timeout: bool) -> str:
    c = walker.counts
    bits: list[str] = []
    if c["def"]:
        bits.append(f"defines {c['def']} function{'s' if c['def'] != 1 else ''}")
    if c["assign"]:
        bits.append(
            f"makes {c['assign']} variable{'s' if c['assign'] != 1 else ''}"
        )
    loops = c["for"] + c["while"]
    if loops:
        bits.append(f"uses {loops} loop{'s' if loops != 1 else ''}")
    if c["if"]:
        bits.append(f"makes {c['if']} decision{'s' if c['if'] != 1 else ''}")
    if c["print"]:
        bits.append(f"prints in {c['print']} place{'s' if c['print'] != 1 else ''}")
    if not bits:
        body = "Python reads it top to bottom"
    elif len(bits) == 1:
        body = f"this code {bits[0]}"
    else:
        body = "this code " + ", ".join(bits[:-1]) + f", and {bits[-1]}"
    tail = ""
    if timeout:
        tail = " Right now it never finishes — see the note below."
    elif error:
        tail = " Right now it stops on an error — explained below."
    return f"Big picture: {body}. Python runs it one line at a time, top to bottom.{tail}"


# ── Entry point ─────────────────────────────────────────────────────


def explain_code(code: str) -> dict[str, Any]:
    stripped = code.strip()
    code_lines = code.split("\n")

    if not stripped or all(
        not L.strip() or L.strip().startswith("#") for L in code_lines
    ):
        comments = _comment_items(code_lines)
        return {
            "ok": True,
            "summary": (
                "There's no runnable code yet — just "
                + ("comments and " if comments else "")
                + "blank space. Type some code and I'll walk you through it."
            ),
            "lines": comments,
            "output_notes": [],
            "error_note": None,
        }

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {
            "ok": True,
            "summary": "Python can't run this yet — there's a syntax error.",
            "lines": [],
            "output_notes": [],
            "error_note": _friendly_syntax_error(exc),
        }

    user_functions = {
        n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
    }
    walker = _Walker(code_lines, user_functions)
    walker.walk_body(tree.body, 0)

    items = walker.items + _comment_items(code_lines)
    items.sort(key=lambda x: (x["line"], x["depth"]))

    has_print = walker.counts["print"] > 0
    run = _traced_run(code)
    error = run.get("error")
    timeout = bool(run.get("timeout"))

    error_note = None
    if timeout:
        pass  # covered in output notes
    elif error:
        error_note = _friendly_error(error)

    notes = _output_notes(
        run.get("trace", []), walker, code_lines, error, timeout, has_print
    )

    return {
        "ok": True,
        "summary": _summary(walker, bool(error), timeout),
        "lines": items,
        "output_notes": notes,
        "error_note": error_note,
    }
