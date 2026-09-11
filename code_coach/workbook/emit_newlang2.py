"""Pages two to fourteen, in the languages added tonight.

The first page proved a language could print. These are the twelve shapes
that follow it: arithmetic, variables, the four loop shapes, a nested pair,
a labelled value, a repeat and a quoted line.

Written as a dialect table rather than ninety-six functions. Every one of
these languages says the same twelve things and differs only in how, so
what varies is captured once per language — how it prints, how it declares
a variable, how it opens a counted loop — and the shapes are built from
that. Twelve shapes times eight languages hand-written would be ninety-six
chances to make a typo in a language I have only just installed.

The one thing that could not be tabled is the expression. A shape carries
`expr` as a fragment like `i * 2` or `n + 5`, written once and meant to
work everywhere, and it nearly does: the arithmetic is the same in all
eight. PHP is the exception, because it spells a variable with a dollar
sign, so the fragment has to be rewritten before it can be pasted in. That
rewrite is a small parser and it is the only clever thing in this file,
which is why it has its own tests below rather than being trusted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from code_coach.workbook.emit import NL

SHAPES: tuple[str, ...] = (
    "print_expr",
    "let_print",
    "let2_print",
    "for_print",
    "for_range_print",
    "for_sum",
    "for_if_print",
    "for_down",
    "for_nested",
    "say_value",
    "repeat_text",
    "quoted_text",
)

#: Words that are not variables if they turn up in a fragment. A shape's
#: `expr` and `cond` are arithmetic and comparison over the names the
#: shape itself declared, so in practice this stays empty — but naming the
#: exceptions is the safe way round. The first version of this listed the
#: variables instead, which meant a page using `price` or `size` produced
#: PHP referring to an undefined constant. A list of what to rewrite goes
#: stale the moment someone writes a new page; a list of what to leave
#: alone does not.
_NOT_VARIABLES = frozenset({"true", "false", "null", "and", "or", "not"})

_WORD = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")


def _dollars(expr: str) -> str:
    """`i * 2` becomes `$i * 2`, and `10` stays `10`.

    Every identifier is a variable unless it is in `_NOT_VARIABLES`,
    because in these fragments everything else is one. Numbers are not
    identifiers so they are untouched, and a keyword that did appear would
    be left alone rather than turned into a variable.
    """
    return _WORD.sub(
        lambda m: (
            m.group(1) if m.group(1).lower() in _NOT_VARIABLES
            else "$" + m.group(1)
        ),
        expr,
    )


def _same(expr: str) -> str:
    return expr


def _operand_start(expr: str, at: int) -> int:
    """Where the thing to the left of `at` begins."""
    i = at - 1
    while i >= 0 and expr[i] == " ":
        i -= 1
    if i >= 0 and expr[i] == ")":
        depth = 0
        while i >= 0:
            if expr[i] == ")":
                depth += 1
            elif expr[i] == "(":
                depth -= 1
                if depth == 0:
                    return i
            i -= 1
        return 0
    while i >= 0 and (expr[i].isalnum() or expr[i] == "_"):
        i -= 1
    return i + 1


def _operand_stop(expr: str, at: int) -> int:
    """Where the thing to the right of `at` ends."""
    i = at + 1
    while i < len(expr) and expr[i] == " ":
        i += 1
    if i < len(expr) and expr[i] == "(":
        depth = 0
        while i < len(expr):
            if expr[i] == "(":
                depth += 1
            elif expr[i] == ")":
                depth -= 1
                if depth == 0:
                    return i
            i += 1
        return len(expr) - 1
    while i < len(expr) and (expr[i].isalnum() or expr[i] == "_"):
        i += 1
    return i - 1


def _zig_rem(expr: str) -> str:
    """`i % 3` becomes `@rem(i, 3)`.

    Zig refuses % on signed integers, because it will not quietly pick
    between truncated and floored remainder for you — @rem rounds toward
    zero and @mod toward negative infinity, and they differ once a
    negative number turns up. Every value on these pages is positive, so
    either would do and @rem is the one that matches what the other
    languages here already do.

    Precedence survives the rewrite: `n % m + m` becomes `@rem(n, m) + m`,
    which is what it meant.

    This reads the operands rather than matching a pattern, and it does so
    because the pattern it replaced said "both sides are a name or a
    number, which is every form these shapes produce" — which was true
    when it was written and stopped being true when a page asked for
    `(a + b) % 10`. One exercise in two thousand three hundred, and it
    failed to compile rather than printing the wrong thing, which is the
    only reason it was cheap.
    """
    while True:
        at = expr.find("%")
        if at == -1:
            return expr
        start = _operand_start(expr, at)
        stop = _operand_stop(expr, at)
        left = expr[start:at].strip()
        right = expr[at + 1:stop + 1].strip()
        expr = f"{expr[:start]}@rem({left}, {right}){expr[stop + 1:]}"


def _q(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


@dataclass(frozen=True)
class Dialect:
    """How one language says the dozen things these pages ask for."""

    #: Lines before the body, and the body's opening and closing.
    header: tuple[str, ...] = ()
    open_body: tuple[str, ...] = ()
    close_body: tuple[str, ...] = ()
    #: The indent the body sits at. Java's body is two braces deep, so
    #: this is eight spaces there and the nesting step below is four.
    indent: str = "    "
    #: One further level of nesting inside the body. Empty means the same
    #: as `indent`, which is right everywhere the body opens once.
    step: str = ""
    #: Whether a line of nothing but closing brackets belongs on the end
    #: of the line above it. True of Lisp and of nothing else: a paren on
    #: its own line is the one thing no Lisp programmer writes.
    hug_closers: bool = False
    #: Print a number, and print a string literal.
    say: Callable[[str], str] = lambda e: f"print({e})"
    say_text: Callable[[str], str] = lambda t: f"print({t})"
    #: Print `label: value` on one line.
    say_labelled: Callable[[str, str], str] = (
        lambda label, e: f'print("{label}: " + str({e}))'
    )
    #: Declare a variable, and a running total that will be added to.
    let: Callable[[str, str], str] = lambda n, v: f"{n} = {v}"
    total: str = "total = 0"
    add: Callable[[str], str] = lambda e: f"total += {e}"
    say_total: str = "print(total)"
    #: Loops. `counted` runs i from 0 to count-1; `ranged` runs lo..hi
    #: inclusive; `down` runs hi..lo inclusive descending.
    counted: Callable[[str, str], str] = lambda var, count: (
        f"for {var} in range({count}):"
    )
    ranged: Callable[[str, str, str], str] = lambda var, lo, hi: (
        f"for {var} in range({lo}, {hi} + 1):"
    )
    down: Callable[[str, str, str], str] = lambda var, lo, hi: (
        f"for {var} in range({hi}, {lo} - 1, -1):"
    )
    close_loop: tuple[str, ...] = ()
    #: `if cond` and how it closes.
    when: Callable[[str], str] = lambda c: f"if {c}:"
    #: How an expression fragment has to be rewritten for this language.
    fix: Callable[[str], str] = _same
    #: Conditions are fragments too, and get the same treatment.
    dialect_of_cond: bool = True


def _hug(dialect: Dialect, lines: list[str]) -> list[str]:
    """Pull lines that are only closing brackets onto the line above."""
    if not dialect.hug_closers:
        return lines
    out: list[str] = []
    for line in lines:
        bare = line.strip()
        if out and bare and set(bare) == {")"}:
            out[-1] += bare
        else:
            out.append(line)
    return out


def _block(dialect: Dialect, *body: str) -> str:
    """The whole file: header, opening, indented body, closing."""
    lines = list(dialect.header)
    lines += list(dialect.open_body)
    depth = 1 if dialect.open_body else 0
    for line in body:
        lines.append((dialect.indent * depth if line else "") + line)
    lines += list(dialect.close_body)
    return NL.join(_hug(dialect, lines)) + NL


def _nest(dialect: Dialect, *rows: tuple[int, str]) -> str:
    """Like `_block`, but each line says how deep it sits."""
    lines = list(dialect.header)
    lines += list(dialect.open_body)
    base = dialect.indent if dialect.open_body else ""
    step = dialect.step or dialect.indent
    for depth, line in rows:
        lines.append((base + step * depth if line else "") + line)
    lines += list(dialect.close_body)
    return NL.join(_hug(dialect, lines)) + NL


# ── Lisp is the one that is not infix ────────────────────────

#: Binding power, loosest first, and what each operator is called in
#: Common Lisp. The shapes only ever produce these seven.
_PRECEDENCE: tuple[tuple[tuple[str, ...], int], ...] = (
    (("==", "!=", "<=", ">=", "<", ">"), 1),
    (("+", "-"), 2),
    (("*", "/", "%"), 3),
)

_LISP_OP = {
    "==": "=", "!=": "/=", "%": "mod", "<": "<", ">": ">",
    "<=": "<=", ">=": ">=", "+": "+", "-": "-", "*": "*", "/": "/",
}

_TOKENS = re.compile(r"\s*(==|!=|<=|>=|[-+*/%<>()]|[A-Za-z_]\w*|\d+)")


def _tokenise(expr: str) -> list[str]:
    out, at = [], 0
    while at < len(expr):
        m = _TOKENS.match(expr, at)
        if not m:
            raise ValueError(f"cannot read {expr!r} at {at}")
        out.append(m.group(1))
        at = m.end()
    return out


def _binding(token: str) -> int:
    for ops, power in _PRECEDENCE:
        if token in ops:
            return power
    return 0


def to_prefix(expr: str) -> str:
    """`i * 2 + 1` becomes `(+ (* i 2) 1)`.

    Precedence climbing, because the shapes write infix once and every
    language but this one can paste it in unchanged. Left associative, so
    `100 - 33 - 21` becomes `(- (- 100 33) 21)` and means what it did.

    Correctness here is not a matter of reading it: every expression the
    workbook contains is evaluated in Python and in Lisp and the two
    answers compared, which is the only way to know.
    """
    tokens = _tokenise(expr)
    pos = 0

    def atom() -> str:
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if token == "(":
            inner = climb(1)
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            return inner
        return token

    def climb(power: int) -> str:
        nonlocal pos
        left = atom()
        while pos < len(tokens) and _binding(tokens[pos]) >= power:
            op = tokens[pos]
            pos += 1
            right = climb(_binding(op) + 1)
            left = f"({_LISP_OP[op]} {left} {right})"
        return left

    return climb(1)


# ── The dialects ─────────────────────────────────────────────

_ZIG_OPEN = (
    "pub fn main() !void {",
    "    var threaded: std.Io.Threaded = .init(std.heap.page_allocator, .{});",
    "    defer threaded.deinit();",
    "    const io = threaded.io();",
    "    var buf: [256]u8 = undefined;",
    "    var w = std.Io.File.stdout().writer(io, &buf);",
    "    const out = &w.interface;",
)

DIALECTS: dict[str, Dialect] = {
    "go": Dialect(
        header=("package main", "", 'import "fmt"', ""),
        open_body=("func main() {",),
        close_body=("}",),
        indent="\t",
        say=lambda e: f"fmt.Println({e})",
        say_text=lambda t: f"fmt.Println({t})",
        say_labelled=lambda label, e: f'fmt.Printf("{label}: %d\\n", {e})',
        let=lambda n, v: f"{n} := {v}",
        total="total := 0",
        add=lambda e: f"total += {e}",
        say_total="fmt.Println(total)",
        counted=lambda var, c: f"for {var} := 0; {var} < {c}; {var}++ {{",
        ranged=lambda var, lo, hi: f"for {var} := {lo}; {var} <= {hi}; {var}++ {{",
        down=lambda var, lo, hi: f"for {var} := {hi}; {var} >= {lo}; {var}-- {{",
        close_loop=("}",),
        when=lambda c: f"if {c} {{",
    ),
    "php": Dialect(
        header=("<?php",),
        indent="  ",
        say=lambda e: f"echo {e}, PHP_EOL;",
        say_text=lambda t: f"echo {t}, PHP_EOL;",
        say_labelled=lambda label, e: f'echo "{label}: ", {e}, PHP_EOL;',
        let=lambda n, v: f"${n} = {v};",
        total="$total = 0;",
        add=lambda e: f"$total += {e};",
        say_total="echo $total, PHP_EOL;",
        counted=lambda var, c: f"for (${var} = 0; ${var} < {c}; ${var}++) {{",
        ranged=lambda var, lo, hi: f"for (${var} = {lo}; ${var} <= {hi}; ${var}++) {{",
        down=lambda var, lo, hi: f"for (${var} = {hi}; ${var} >= {lo}; ${var}--) {{",
        close_loop=("}",),
        when=lambda c: f"if ({c}) {{",
        fix=_dollars,
    ),
    "lua": Dialect(
        indent="  ",
        say=lambda e: f"print({e})",
        say_text=lambda t: f"print({t})",
        say_labelled=lambda label, e: f'print("{label}: " .. tostring({e}))',
        let=lambda n, v: f"local {n} = {v}",
        total="local total = 0",
        add=lambda e: f"total = total + {e}",
        say_total="print(total)",
        counted=lambda var, c: f"for {var} = 0, {c} - 1 do",
        ranged=lambda var, lo, hi: f"for {var} = {lo}, {hi} do",
        down=lambda var, lo, hi: f"for {var} = {hi}, {lo}, -1 do",
        close_loop=("end",),
        when=lambda c: f"if {c} then",
    ),
    "ruby": Dialect(
        indent="  ",
        say=lambda e: f"puts {e}",
        say_text=lambda t: f"puts {t}",
        say_labelled=lambda label, e: f'puts "{label}: #{{{e}}}"',
        let=lambda n, v: f"{n} = {v}",
        total="total = 0",
        add=lambda e: f"total += {e}",
        say_total="puts total",
        counted=lambda var, c: f"(0...{c}).each do |{var}|",
        ranged=lambda var, lo, hi: f"({lo}..{hi}).each do |{var}|",
        down=lambda var, lo, hi: f"{hi}.downto({lo}) do |{var}|",
        close_loop=("end",),
        when=lambda c: f"if {c}",
    ),
    "java": Dialect(
        open_body=("public class Main {",
                   "    public static void main(String[] args) {"),
        close_body=("    }", "}"),
        indent="        ",
        step="    ",
        say=lambda e: f"System.out.println({e});",
        say_text=lambda t: f"System.out.println({t});",
        say_labelled=lambda label, e: f'System.out.println("{label}: " + ({e}));',
        let=lambda n, v: f"int {n} = {v};",
        total="int total = 0;",
        add=lambda e: f"total += {e};",
        say_total="System.out.println(total);",
        counted=lambda var, c: f"for (int {var} = 0; {var} < {c}; {var}++) {{",
        ranged=lambda var, lo, hi: f"for (int {var} = {lo}; {var} <= {hi}; {var}++) {{",
        down=lambda var, lo, hi: f"for (int {var} = {hi}; {var} >= {lo}; {var}--) {{",
        close_loop=("}",),
        when=lambda c: f"if ({c}) {{",
    ),
    "csharp": Dialect(
        indent="  ",
        say=lambda e: f"System.Console.WriteLine({e});",
        say_text=lambda t: f"System.Console.WriteLine({t});",
        say_labelled=lambda label, e: f'System.Console.WriteLine($"{label}: {{{e}}}");',
        let=lambda n, v: f"int {n} = {v};",
        total="int total = 0;",
        add=lambda e: f"total += {e};",
        say_total="System.Console.WriteLine(total);",
        counted=lambda var, c: f"for (int {var} = 0; {var} < {c}; {var}++) {{",
        ranged=lambda var, lo, hi: f"for (int {var} = {lo}; {var} <= {hi}; {var}++) {{",
        down=lambda var, lo, hi: f"for (int {var} = {hi}; {var} >= {lo}; {var}--) {{",
        close_loop=("}",),
        when=lambda c: f"if ({c}) {{",
    ),
    "odin": Dialect(
        header=("package main", "", 'import "core:fmt"', ""),
        open_body=("main :: proc() {",),
        close_body=("}",),
        indent="\t",
        say=lambda e: f"fmt.println({e})",
        say_text=lambda t: f"fmt.println({t})",
        say_labelled=lambda label, e: f'fmt.printf("{label}: %d\\n", {e})',
        let=lambda n, v: f"{n} := {v}",
        total="total := 0",
        add=lambda e: f"total += {e}",
        say_total="fmt.println(total)",
        counted=lambda var, c: f"for {var} := 0; {var} < {c}; {var} += 1 {{",
        ranged=lambda var, lo, hi: f"for {var} := {lo}; {var} <= {hi}; {var} += 1 {{",
        down=lambda var, lo, hi: f"for {var} := {hi}; {var} >= {lo}; {var} -= 1 {{",
        close_loop=("}",),
        when=lambda c: f"if {c} {{",
    ),
    "kotlin": Dialect(
        open_body=("fun main() {",),
        close_body=("}",),
        indent="    ",
        say=lambda e: f"println({e})",
        say_text=lambda t: f"println({t})",
        say_labelled=lambda label, e: (
            'println("' + label + ': ${' + e + '}")'),
        let=lambda n, v: f"val {n} = {v}",
        total="var total = 0",
        add=lambda e: f"total += {e}",
        say_total="println(total)",
        counted=lambda var, c: f"for ({var} in 0 until {c}) {{",
        ranged=lambda var, lo, hi: f"for ({var} in {lo}..{hi}) {{",
        down=lambda var, lo, hi: (
            f"for ({var} in {hi} downTo {lo}) {{"),
        close_loop=("}",),
        when=lambda c: f"if ({c}) {{",
    ),
    "swift": Dialect(
        indent="    ",
        say=lambda e: f"print({e})",
        say_text=lambda t: f"print({t})",
        # Swift interpolates with a backslash and parentheses, which is a
        # sequence Python does not know — escaped, or it is a warning that
        # happens to produce the right string.
        say_labelled=lambda label, e: f'print("{label}: \\({e})")',
        let=lambda n, v: f"let {n} = {v}",
        total="var total = 0",
        add=lambda e: f"total += {e}",
        say_total="print(total)",
        counted=lambda var, c: f"for {var} in 0..<{c} {{",
        ranged=lambda var, lo, hi: f"for {var} in {lo}...{hi} {{",
        down=lambda var, lo, hi: (
            f"for {var} in stride(from: {hi}, through: {lo}, by: -1) {{"),
        close_loop=("}",),
        when=lambda c: f"if {c} {{",
    ),
    "lisp": Dialect(
        indent="  ",
        hug_closers=True,
        say=lambda e: f'(format t "~a~%" {e})',
        say_text=lambda t: f'(format t "~a~%" {t})',
        say_labelled=lambda label, e: f'(format t "{label}: ~a~%" {e})',
        let=lambda n, v: f"(defparameter {n} {v})",
        total="(defparameter total 0)",
        add=lambda e: f"(setf total (+ total {e}))",
        say_total='(format t "~a~%" total)',
        counted=lambda var, c: f"(dotimes ({var} {c})",
        ranged=lambda var, lo, hi: f"(loop for {var} from {lo} to {hi} do",
        down=lambda var, lo, hi: f"(loop for {var} from {hi} downto {lo} do",
        close_loop=(")",),
        when=lambda c: f"(when {c}",
        fix=to_prefix,
    ),
    "zig": Dialect(
        header=('const std = @import("std");', ""),
        open_body=_ZIG_OPEN,
        # The writer is buffered, so without this the program exits
        # cleanly having printed nothing at all: status zero, empty
        # stdout, and five hundred exercises failing for one missing line.
        close_body=("    try out.flush();", "}"),
        indent="    ",
        say=lambda e: 'try out.print("{d}\\n", .{' + e + "});",
        say_text=lambda t: 'try out.print("{s}\\n", .{' + t + "});",
        say_labelled=lambda label, e: (
            'try out.print("' + label + ': {d}\\n", .{' + e + "});"
        ),
        let=lambda n, v: f"const {n}: i32 = {v};",
        total="var total: i32 = 0;",
        add=lambda e: f"total += {e};",
        say_total='try out.print("{d}\\n", .{total});',
        counted=lambda var, c: (
            f"var {var}: i32 = 0;\n    while ({var} < {c}) : ({var} += 1) {{"
        ),
        ranged=lambda var, lo, hi: (
            f"var {var}: i32 = {lo};\n    while ({var} <= {hi}) : ({var} += 1) {{"
        ),
        down=lambda var, lo, hi: (
            f"var {var}: i32 = {hi};\n    while ({var} >= {lo}) : ({var} -= 1) {{"
        ),
        close_loop=("}",),
        when=lambda c: f"if ({c}) {{",
        fix=_zig_rem,
    ),
}


# ── The shapes ───────────────────────────────────────────────


def handles(shape: str) -> bool:
    return shape in SHAPES


def solution(language: str, shape: str, args: dict) -> str | None:
    """The reference program, for a language with a dialect and a runner."""
    d = DIALECTS.get(language)
    if d is None or shape not in SHAPES:
        return None
    a = args
    fix = d.fix

    if shape == "print_expr":
        return _block(d, d.say(fix(a["expr"])))

    if shape == "let_print":
        return _block(
            d,
            d.let(a["name"], str(a["value"])),
            d.say(fix(a["expr"])),
        )

    if shape == "let2_print":
        return _block(
            d,
            d.let(a["name1"], str(a["value1"])),
            d.let(a["name2"], str(a["value2"])),
            d.say(fix(a["expr"])),
        )

    if shape == "for_print":
        return _nest(
            d,
            (0, d.counted("i", str(a["count"]))),
            (1, d.say(fix(a["expr"]))),
            *[(0, line) for line in d.close_loop],
        )

    if shape == "for_range_print":
        return _nest(
            d,
            (0, d.ranged("i", str(a["lo"]), str(a["hi"]))),
            (1, d.say(fix(a["expr"]))),
            *[(0, line) for line in d.close_loop],
        )

    if shape == "for_sum":
        return _nest(
            d,
            (0, d.total),
            (0, d.ranged("i", str(a["lo"]), str(a["hi"]))),
            (1, d.add(fix(a["expr"]))),
            *[(0, line) for line in d.close_loop],
            (0, d.say_total),
        )

    if shape == "for_if_print":
        return _nest(
            d,
            (0, d.ranged("i", str(a["lo"]), str(a["hi"]))),
            (1, d.when(fix(a["cond"]))),
            (2, d.say(fix(a["expr"]))),
            *[(1, line) for line in d.close_loop],
            *[(0, line) for line in d.close_loop],
        )

    if shape == "for_down":
        return _nest(
            d,
            (0, d.down("i", str(a["lo"]), str(a["hi"]))),
            (1, d.say(fix(a["expr"]))),
            *[(0, line) for line in d.close_loop],
        )

    if shape == "for_nested":
        return _nest(
            d,
            (0, d.ranged("i", "1", str(a["rows"]))),
            (1, d.ranged("j", "1", str(a["cols"]))),
            (2, d.say(fix(a["expr"]))),
            *[(1, line) for line in d.close_loop],
            *[(0, line) for line in d.close_loop],
        )

    if shape == "say_value":
        return _block(d, d.say_labelled(a["label"], fix(a["expr"])))

    if shape == "repeat_text":
        return _nest(
            d,
            (0, d.counted("i", str(a["count"]))),
            (1, d.say_text(_q(a["text"]))),
            *[(0, line) for line in d.close_loop],
        )

    if shape == "quoted_text":
        return _block(d, d.say_text(_q(a["text"])))

    return None
