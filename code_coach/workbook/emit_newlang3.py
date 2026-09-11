"""Conditionals and while loops, in the nine languages added tonight.

Pages 15 to 20 and their practice pages at 70 to 72. Six shapes: print
only when a condition holds, print one thing or another, print whichever
of two is bigger, join two conditions with and or or, and the two while
loops.

The dialect table in emit_newlang2 says how each language prints and
declares and loops. These shapes need four things it does not carry — an
else, a mutable variable, an assignment, and a while — so those live here
in a second record rather than being added to the first, which is
imported and in use.

Every language here has a toolchain, so none of this is written on trust:
each of the nine runs every exercise and the output is compared against
the same expected value Python's own answer produces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from code_coach.workbook.emit_newlang2 import (
    DIALECTS,
    _block,
    _nest,
    _q,
    to_prefix,
)

SHAPES: tuple[str, ...] = (
    "if_print",
    "if_else_print",
    "bigger_print",
    "and_or_print",
    "while_count",
    "while_sum",
)


@dataclass(frozen=True)
class Extra:
    """What conditionals and while loops need beyond the base dialect."""

    #: The else half of an if, and what closes the whole thing. Some
    #: languages close the if before the else and some do not, so the
    #: opener carries whatever brace or keyword belongs in front of it.
    otherwise: tuple[str, ...] = ("else:",)
    close_if: tuple[str, ...] = ()
    #: A variable that will be reassigned, and the reassignment.
    let_mut: Callable[[str, str], str] = lambda n, v: f"{n} = {v}"
    assign: Callable[[str, str], str] = lambda n, e: f"{n} = {e}"
    bump: Callable[[str], str] = lambda n: f"{n} += 1"
    #: A while loop and how it closes.
    while_: Callable[[str], str] = lambda c: f"while {c}:"
    close_while: tuple[str, ...] = ()
    #: How this language spells and, or, and a comparison of two names.
    both: str = "and"
    either: str = "or"


EXTRAS: dict[str, Extra] = {
    "go": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"{n} := {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n}++",
        while_=lambda c: f"for {c} {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "php": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"${n} = {v};",
        assign=lambda n, e: f"${n} = {e};",
        bump=lambda n: f"${n}++;",
        while_=lambda c: f"while ({c}) {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "lua": Extra(
        otherwise=("else",),
        close_if=("end",),
        let_mut=lambda n, v: f"local {n} = {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n} = {n} + 1",
        while_=lambda c: f"while {c} do",
        close_while=("end",),
        both="and",
        either="or",
    ),
    "ruby": Extra(
        otherwise=("else",),
        close_if=("end",),
        let_mut=lambda n, v: f"{n} = {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n} += 1",
        while_=lambda c: f"while {c}",
        close_while=("end",),
        both="&&",
        either="||",
    ),
    "java": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"int {n} = {v};",
        assign=lambda n, e: f"{n} = {e};",
        bump=lambda n: f"{n}++;",
        while_=lambda c: f"while ({c}) {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "csharp": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"int {n} = {v};",
        assign=lambda n, e: f"{n} = {e};",
        bump=lambda n: f"{n}++;",
        while_=lambda c: f"while ({c}) {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "odin": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"{n} := {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n} += 1",
        while_=lambda c: f"for {c} {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "zig": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"var {n}: i32 = {v};",
        assign=lambda n, e: f"{n} = {e};",
        bump=lambda n: f"{n} += 1;",
        while_=lambda c: f"while ({c}) {{",
        close_while=("}",),
        both="and",
        either="or",
    ),
    "kotlin": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"var {n} = {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n} += 1",
        while_=lambda c: f"while ({c}) {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "swift": Extra(
        otherwise=("} else {",),
        close_if=("}",),
        let_mut=lambda n, v: f"var {n} = {v}",
        assign=lambda n, e: f"{n} = {e}",
        bump=lambda n: f"{n} += 1",
        while_=lambda c: f"while {c} {{",
        close_while=("}",),
        both="&&",
        either="||",
    ),
    "lisp": Extra(
        # Lisp has no else keyword: the if form takes both branches as
        # arguments, so the shapes below build it as one expression
        # rather than as two indented blocks.
        otherwise=(),
        close_if=(),
        let_mut=lambda n, v: f"(defparameter {n} {v})",
        assign=lambda n, e: f"(setf {n} {e})",
        bump=lambda n: f"(setf {n} (+ {n} 1))",
        while_=lambda c: f"(loop while {c} do",
        close_while=(")",),
        both="and",
        either="or",
    ),
}


def handles(shape: str) -> bool:
    return shape in SHAPES


def _lisp_if(cond: str, then: str, other: str | None = None) -> str:
    """Lisp's if is one form, not a block with an else after it."""
    if other is None:
        return f"(when {cond} {then})"
    return f"(if {cond} {then} {other})"


def solution(language: str, shape: str, args: dict) -> str | None:
    d = DIALECTS.get(language)
    x = EXTRAS.get(language)
    if d is None or x is None or shape not in SHAPES:
        return None
    a = args
    fix = d.fix

    if shape in ("if_print", "if_else_print", "and_or_print"):
        if shape == "and_or_print":
            joiner = x.both if a["op"] == "and" else x.either
            if language == "lisp":
                # The joiner is an operator like any other, so it goes in
                # front of both halves rather than between them.
                cond = f"({joiner} {fix(a['left'])} {fix(a['right'])})"
            else:
                cond = f"{fix(a['left'])} {joiner} {fix(a['right'])}"
        else:
            cond = fix(a["cond"])
        yes = _q(a["text"]) if shape == "if_print" else _q(a["yes"])
        no = None if shape == "if_print" else _q(a["no"])

        if language == "lisp":
            body = [d.let(a["name"], str(a["value"]))]
            then = d.say_text(yes)
            other = d.say_text(no) if no is not None else None
            body.append(_lisp_if(cond, then, other))
            return _block(d, *body)

        rows: list[tuple[int, str]] = [
            (0, d.let(a["name"], str(a["value"]))),
            (0, d.when(cond)),
            (1, d.say_text(yes)),
        ]
        if no is not None:
            rows += [(0, line) for line in x.otherwise]
            rows.append((1, d.say_text(no)))
        rows += [(0, line) for line in x.close_if]
        return _nest(d, *rows)

    if shape == "bigger_print":
        one, two = a["name1"], a["name2"]
        cond = fix(f"{one} > {two}")
        if language == "lisp":
            return _block(
                d,
                d.let(one, str(a["value1"])),
                d.let(two, str(a["value2"])),
                _lisp_if(cond, d.say(one), d.say(two)),
            )
        rows = [
            (0, d.let(one, str(a["value1"]))),
            (0, d.let(two, str(a["value2"]))),
            (0, d.when(cond)),
            (1, d.say(fix(one))),
        ]
        rows += [(0, line) for line in x.otherwise]
        rows.append((1, d.say(fix(two))))
        rows += [(0, line) for line in x.close_if]
        return _nest(d, *rows)

    if shape in ("while_count", "while_sum"):
        lo, hi = str(a["lo"]), str(a["hi"])
        cond = fix(f"i <= {hi}")
        rows = [(0, x.let_mut("i", lo))]
        if shape == "while_sum":
            rows.append((0, d.total))
        rows.append((0, x.while_(cond)))
        if shape == "while_count":
            rows.append((1, d.say(fix(a["expr"]))))
        else:
            rows.append((1, d.add(fix(a["expr"]))))
        rows.append((1, x.bump("i")))
        rows += [(0, line) for line in x.close_while]
        if shape == "while_sum":
            rows.append((0, d.say_total))
        return _nest(d, *rows)

    return None


__all__ = ["EXTRAS", "SHAPES", "handles", "solution", "to_prefix"]
