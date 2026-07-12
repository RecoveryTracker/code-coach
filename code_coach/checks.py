"""
AST-based structural checks for build-lesson drills.

Substring matching on raw source lets a student "pass" by putting keywords in a
string or comment — e.g. print("if this else that") used to complete the if/else
drill. These predicates parse the code and inspect the syntax tree, so text
inside string literals and comments is ignored. Every predicate returns False on
a SyntaxError (incomplete code is simply "not done yet"), never raises.

Dictation (type-along) drills do NOT use these — they use exact-line matching in
code_coach/dictation/bank.py, which is correct for copy-the-line practice.
"""

from __future__ import annotations

import ast
from typing import Optional


def _tree(code: str) -> Optional[ast.Module]:
    try:
        return ast.parse(code)
    except (SyntaxError, ValueError):
        return None


def _walk(code: str):
    tree = _tree(code)
    if tree is None:
        return []
    return list(ast.walk(tree))


# ── Control flow ────────────────────────────────────────────


def uses_for(code: str) -> bool:
    return any(isinstance(n, ast.For) for n in _walk(code))


def uses_while(code: str) -> bool:
    return any(isinstance(n, ast.While) for n in _walk(code))


def uses_loop(code: str) -> bool:
    return any(isinstance(n, (ast.For, ast.While)) for n in _walk(code))


def uses_if(code: str) -> bool:
    return any(isinstance(n, ast.If) for n in _walk(code))


def uses_if_else(code: str) -> bool:
    """An if that has an else/elif branch (non-empty orelse)."""
    return any(isinstance(n, ast.If) and n.orelse for n in _walk(code))


def uses_and(code: str) -> bool:
    return any(
        isinstance(n, ast.BoolOp) and isinstance(n.op, ast.And)
        for n in _walk(code)
    )


def uses_or(code: str) -> bool:
    return any(
        isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or)
        for n in _walk(code)
    )


def uses_nested_for(code: str) -> bool:
    """A for loop whose body (at any depth) contains another for loop."""
    tree = _tree(code)
    if tree is None:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if child is not node and isinstance(child, ast.For):
                    return True
    return False


def uses_membership(code: str) -> bool:
    """An `x in y` comparison."""
    return any(
        isinstance(n, ast.Compare)
        and any(isinstance(op, ast.In) for op in n.ops)
        for n in _walk(code)
    )


# ── Functions ───────────────────────────────────────────────


def defines_function(code: str, name: Optional[str] = None) -> bool:
    for n in _walk(code):
        if isinstance(n, ast.FunctionDef) and (name is None or n.name == name):
            return True
    return False


def calls_function(code: str, name: str) -> bool:
    """A call like name(...) — the callee is a bare Name."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == name
        ):
            return True
    return False


def returns_value(code: str) -> bool:
    return any(
        isinstance(n, ast.Return) and n.value is not None for n in _walk(code)
    )


def prints_name(code: str, name: str) -> bool:
    """print(name) — a print call with the bare variable as an argument."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == "print"
        ):
            for arg in n.args:
                if isinstance(arg, ast.Name) and arg.id == name:
                    return True
    return False


# ── Names, assignment, values ───────────────────────────────


def references_name(code: str, name: str) -> bool:
    """The identifier appears as a real name somewhere (load or store)."""
    return any(isinstance(n, ast.Name) and n.id == name for n in _walk(code))


def assigns_variable(code: str, name: str) -> bool:
    """name = ..., name += ..., or name: T = ... (a real assignment target)."""
    for n in _walk(code):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return True
        elif isinstance(n, ast.AugAssign):
            if isinstance(n.target, ast.Name) and n.target.id == name:
                return True
        elif isinstance(n, ast.AnnAssign):
            if isinstance(n.target, ast.Name) and n.target.id == name:
                return True
    return False


def assigns_list(code: str, name: str) -> bool:
    """name = [ ... ] — assignment whose value is a list literal."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Assign)
            and isinstance(n.value, ast.List)
            and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)
        ):
            return True
    return False


def assigns_dict(code: str, name: str) -> bool:
    """name = { ... } — assignment whose value is a dict literal."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Dict)
            and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)
        ):
            return True
    return False


def uses_list_literal(code: str) -> bool:
    return any(isinstance(n, ast.List) for n in _walk(code))


def uses_dict_literal(code: str) -> bool:
    return any(isinstance(n, ast.Dict) for n in _walk(code))


def uses_subscript(code: str) -> bool:
    """Any indexing/lookup like x[i]."""
    return any(isinstance(n, ast.Subscript) for n in _walk(code))


def subscripts_name(code: str, name: str) -> bool:
    """name[...] — a subscript whose base object is the given variable."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Subscript)
            and isinstance(n.value, ast.Name)
            and n.value.id == name
        ):
            return True
    return False


def calls_method(code: str, name: str, arg0=None) -> bool:
    """obj.name(...) — a method call. If arg0 is given, require the first
    argument to be a constant equal to it (e.g. pop(0))."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == name
        ):
            if arg0 is None:
                return True
            if n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == arg0:
                return True
    return False


def count_calls(code: str, name: str) -> int:
    """How many times name(...) is called (bare-Name callee)."""
    return sum(
        1
        for n in _walk(code)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Name)
        and n.func.id == name
    )


def calls_function_with_args(code: str, name: str, min_args: int = 2) -> bool:
    """A call like name(a, b, ...) with at least min_args positional args."""
    for n in _walk(code):
        if (
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == name
            and len(n.args) >= min_args
        ):
            return True
    return False


def compares(code: str) -> bool:
    """Any comparison (>, <, ==, etc.) appears."""
    return any(isinstance(n, ast.Compare) for n in _walk(code))


def has_constant(code: str, value) -> bool:
    """A literal constant equal to value appears (number/bool/None), NOT inside
    a string. Matches type as well so 7 != True."""
    for n in _walk(code):
        if isinstance(n, ast.Constant) and not isinstance(n.value, str):
            if n.value == value and type(n.value) is type(value):
                return True
    return False
