"""
Day 01 — pure dictation.

A step only counts when a *complete finished line* is present.
Partial typing must never unlock the next line.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable


@dataclass
class Waypoint:
    id: str
    label: str
    check: Callable[[str], bool]
    concept: str
    why: str
    hint: str
    example: str


def _code_lines(code: str) -> list[str]:
    return [
        ln.strip()
        for ln in code.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def _balanced_quotes(s: str) -> bool:
    """True if s is a fully closed single- or double-quoted string literal."""
    s = s.strip()
    if len(s) < 3:
        return False
    q = s[0]
    if q not in "\"'":
        return False
    if s[-1] != q:
        return False
    # reject odd number of unescaped quotes mid-string (simple)
    body = s[1:-1]
    # empty body not enough for dictation practice
    if not body:
        return False
    return True


def _complete_print_string(code: str) -> bool:
    """print("...") or print('...') — full line only, quotes + paren closed."""
    for s in _code_lines(code):
        m = re.fullmatch(r"print\s*\((.*)\)\s*", s)
        if not m:
            continue
        inner = m.group(1).strip()
        if _balanced_quotes(inner):
            return True
    return False


def _complete_str_assign(code: str, variable: str) -> bool:
    for s in _code_lines(code):
        m = re.fullmatch(rf"{re.escape(variable)}\s*=\s*(.+)", s)
        if not m:
            continue
        if _balanced_quotes(m.group(1)):
            return True
    return False


def _complete_int_assign(code: str, variable: str) -> bool:
    for s in _code_lines(code):
        m = re.fullmatch(rf"{re.escape(variable)}\s*=\s*(-?\d+)\s*", s)
        if m:
            return True
    return False


def _complete_print_var(code: str, variable: str) -> bool:
    """Whole-line print(var) only — not print(var something mid-type)."""
    for s in _code_lines(code):
        if re.fullmatch(rf"print\s*\(\s*{re.escape(variable)}\s*\)\s*", s):
            return True
    return False


def _wp(
    id: str,
    example: str,
    check: Callable[[str], bool],
    *,
    concept: str,
    why: str,
    hint: str,
) -> Waypoint:
    return Waypoint(
        id=id,
        label=example,
        check=check,
        concept=concept,
        why=why,
        hint=hint,
        example=example,
    )


LESSON = {
    "id": "day-01",
    "title": "Day 01 — Type each line",
    "practice_file": "practice.py",
    "relative_path": "python/day-01/practice.py",
    "waypoints": [
        _wp(
            "print",
            'print("Hello, world!")',
            _complete_print_string,
            concept="print",
            why="Shows text in the terminal.",
            hint="Finish the whole line, including the closing quote and ).",
        ),
        _wp(
            "name_var",
            'name = "Ada"',
            lambda c: _complete_str_assign(c, "name"),
            concept="variable",
            why="Saves text under a name.",
            hint="Finish with closing quotes.",
        ),
        _wp(
            "print_name",
            "print(name)",
            lambda c: _complete_print_var(c, "name"),
            concept="print variable",
            why="No quotes around name.",
            hint="print(name) not print(\"name\")",
        ),
        _wp(
            "city_var",
            'city = "Seattle"',
            lambda c: _complete_str_assign(c, "city"),
            concept="variable",
            why="Another piece of text.",
            hint="Finish with closing quotes.",
        ),
        _wp(
            "favorite_number_var",
            "favorite_number = 7",
            lambda c: _complete_int_assign(c, "favorite_number"),
            concept="number",
            why="Numbers have no quotes.",
            hint="Any whole number is fine.",
        ),
        _wp(
            "print_city",
            "print(city)",
            lambda c: _complete_print_var(c, "city"),
            concept="print variable",
            why="Same as print(name).",
            hint="print(city)",
        ),
        _wp(
            "print_favorite_number",
            "print(favorite_number)",
            lambda c: _complete_print_var(c, "favorite_number"),
            concept="print number",
            why="Works for numbers too.",
            hint="print(favorite_number)",
        ),
    ],
}
