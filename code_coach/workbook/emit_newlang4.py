"""Lists, in the nine languages added tonight.

Pages 21 to 26 and 35 to 45, plus their practice pages — everything the
workbook does with a list of numbers before it reaches strings and
functions. Eighteen shapes, and the reason they arrive together is that
they all rest on the same four things: writing a list down, walking it,
reaching into it by position, and building one up.

The dialect table in `emit_newlang2` says how each language prints and
declares and loops, and `emit_newlang3` added what conditionals and while
loops need. This adds the list vocabulary as a third record, for the same
reason the second one exists: the first two are imported and in use, and a
table that is already relied on is not the place to grow a new column.

Lua declines two pages, and the refusal is honest rather than a gap. Lua
counts from one, and the loops here run from one to the length, which is
the Lua a Lua programmer writes and prints the same characters as everyone
else. What it cannot do is a page *about* index zero — reaching in at a
named position, and reporting the position something was found at. Those
answers are different numbers in Lua, so Lua is given no reference for
them and `pages` drops the page rather than teaching a number that is
wrong.

Every language here has a toolchain, so none of this is written on trust:
each one runs every exercise, and the output is compared against the same
expected value Python's answer produces.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from code_coach.workbook.emit_newlang2 import DIALECTS, _nest, _q, to_prefix
from code_coach.workbook.emit_newlang3 import EXTRAS

SHAPES: tuple[str, ...] = (
    "list_loop",
    "list_sum",
    "list_index",
    "list_filter",
    "list_build",
    "list_max",
    "list_min",
    "list_reverse",
    "find_index",
    "count_matches",
    "running_total",
    "label_each",
    "two_lists",
    "grid_print",
    "grid_sum",
    "step_loop",
    "times_table",
    "swap_print",
)

#: The shapes whose answer is a position in the list rather than a value
#: in it. A language that counts from one answers these differently.
POSITIONAL: tuple[str, ...] = ("list_index", "find_index")

#: The languages that count from one.
ONE_BASED: tuple[str, ...] = ("lua",)


@dataclass(frozen=True)
class Lists:
    """How one language writes a list down, walks it, and builds one."""

    #: A list of ints, from the name and the items already rendered.
    lit: Callable[[str, str], str]
    #: Walk the values. Closed by the dialect's `close_loop`.
    each: Callable[[str, str], str]
    #: Walk the positions, and the element at one.
    upto: Callable[[str, str], str]
    at: Callable[[str, str], str]
    #: Walk the positions backwards. Some languages count down and some
    #: count up and subtract, so the element expression comes with it.
    down: Callable[[str, str], str]
    down_at: Callable[[str, str], str]
    #: An empty list to add to, adding to it, and walking what was
    #: built. The walk is its own field because a language without a
    #: growable list builds into a fixed array and has to say how much of
    #: it is real.
    empty: Callable[[str], str]
    push: Callable[[str, str], str]
    #: A list of lists, and walking one. Given the rows rather than a
    #: rendered string, because Zig's type has the width in it.
    grid: Callable[[str, list], str]
    rows: Callable[[str, str], str]
    cols: Callable[[str, str], str]
    #: `3 x 4 = 12`, built the way this language builds a sentence.
    times: Callable[[str, str, str], str]
    #: lo to hi in steps.
    stepped: Callable[[str, str, str, str], str]
    #: Stop the loop here, terminator included: `break` is a statement
    #: like any other and half of these languages end one with a
    #: semicolon.
    stop: str = "break"
    #: What the first position is called, for the languages that differ.
    first: str = "0"
    #: How to walk what was built, when that is not how you walk a list
    #: written down. Only the language with no growable list needs it.
    built_walk: Callable[[str, str], str] | None = None


def _items(values) -> str:
    return ", ".join(str(v) for v in values)


def _braced(rows) -> str:
    return ", ".join("{" + _items(r) + "}" for r in rows)


def _bracketed(rows) -> str:
    return ", ".join("[" + _items(r) + "]" for r in rows)


def _csharp_grid(rows) -> str:
    # Jagged, so each row is its own `new int[]`.
    return ", ".join("new int[] {" + _items(r) + "}" for r in rows)


def _listed(rows) -> str:
    """Kotlin nests its list constructor rather than using brackets."""
    return ", ".join("listOf(" + _items(r) + ")" for r in rows)


def _zig_grid(rows) -> str:
    return ", ".join("[_]i32{ " + _items(r) + " }" for r in rows)


LISTS: dict[str, Lists] = {
    "go": Lists(
        lit=lambda n, xs: f"{n} := []int{{{xs}}}",
        each=lambda v, n: f"for _, {v} := range {n} {{",
        upto=lambda k, n: f"for {k} := 0; {k} < len({n}); {k}++ {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: f"for {k} := len({n}) - 1; {k} >= 0; {k}-- {{",
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"{n} := []int{{}}",
        push=lambda n, e: f"{n} = append({n}, {e})",
        grid=lambda n, rs: f"{n} := [][]int{{{_braced(rs)}}}",
        rows=lambda r, n: f"for _, {r} := range {n} {{",
        cols=lambda c, r: f"for _, {c} := range {r} {{",
        times=lambda n, i, p: f'fmt.Println({n}, "x", {i}, "=", {p})',
        stepped=lambda v, lo, hi, s: (
            f"for {v} := {lo}; {v} <= {hi}; {v} += {s} {{"),
    ),
    "php": Lists(
        lit=lambda n, xs: f"${n} = [{xs}];",
        each=lambda v, n: f"foreach (${n} as ${v}) {{",
        upto=lambda k, n: f"for (${k} = 0; ${k} < count(${n}); ${k}++) {{",
        at=lambda n, k: f"${n}[{k}]",
        down=lambda k, n: (
            f"for (${k} = count(${n}) - 1; ${k} >= 0; ${k}--) {{"),
        down_at=lambda n, k: f"${n}[{k}]",
        empty=lambda n: f"${n} = [];",
        push=lambda n, e: f"${n}[] = {e};",
        grid=lambda n, rs: f"${n} = [{_bracketed(rs)}];",
        rows=lambda r, n: f"foreach (${n} as ${r}) {{",
        cols=lambda c, r: f"foreach (${r} as ${c}) {{",
        times=lambda n, i, p: f'echo {n}, " x ", {i}, " = ", {p}, PHP_EOL;',
        stepped=lambda v, lo, hi, s: (
            f"for (${v} = {lo}; ${v} <= {hi}; ${v} += {s}) {{"),
        stop="break;",
    ),
    "lua": Lists(
        lit=lambda n, xs: f"local {n} = {{{xs}}}",
        each=lambda v, n: f"for _, {v} in ipairs({n}) do",
        upto=lambda k, n: f"for {k} = 1, #{n} do",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: f"for {k} = #{n}, 1, -1 do",
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"local {n} = {{}}",
        push=lambda n, e: f"{n}[#{n} + 1] = {e}",
        grid=lambda n, rs: f"local {n} = {{{_braced(rs)}}}",
        rows=lambda r, n: f"for _, {r} in ipairs({n}) do",
        cols=lambda c, r: f"for _, {c} in ipairs({r}) do",
        times=lambda n, i, p: (
            f'print({n} .. " x " .. {i} .. " = " .. {p})'),
        stepped=lambda v, lo, hi, s: f"for {v} = {lo}, {hi}, {s} do",
        first="1",
    ),
    "ruby": Lists(
        lit=lambda n, xs: f"{n} = [{xs}]",
        each=lambda v, n: f"{n}.each do |{v}|",
        upto=lambda k, n: f"{n}.each_index do |{k}|",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: f"({n}.length - 1).downto(0) do |{k}|",
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"{n} = []",
        push=lambda n, e: f"{n} << {e}",
        grid=lambda n, rs: f"{n} = [{_bracketed(rs)}]",
        rows=lambda r, n: f"{n}.each do |{r}|",
        cols=lambda c, r: f"{r}.each do |{c}|",
        times=lambda n, i, p: f'puts "#{{{n}}} x #{{{i}}} = #{{{p}}}"',
        stepped=lambda v, lo, hi, s: f"{lo}.step({hi}, {s}) do |{v}|",
    ),
    "java": Lists(
        lit=lambda n, xs: f"int[] {n} = {{{xs}}};",
        each=lambda v, n: f"for (int {v} : {n}) {{",
        upto=lambda k, n: f"for (int {k} = 0; {k} < {n}.length; {k}++) {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: (
            f"for (int {k} = {n}.length - 1; {k} >= 0; {k}--) {{"),
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"java.util.List<Integer> {n} = new java.util.ArrayList<>();",
        push=lambda n, e: f"{n}.add({e});",
        grid=lambda n, rs: f"int[][] {n} = {{{_braced(rs)}}};",
        rows=lambda r, n: f"for (int[] {r} : {n}) {{",
        cols=lambda c, r: f"for (int {c} : {r}) {{",
        times=lambda n, i, p: (
            f'System.out.println({n} + " x " + {i} + " = " + ({p}));'),
        stepped=lambda v, lo, hi, s: (
            f"for (int {v} = {lo}; {v} <= {hi}; {v} += {s}) {{"),
        stop="break;",
    ),
    "csharp": Lists(
        lit=lambda n, xs: f"int[] {n} = {{{xs}}};",
        each=lambda v, n: f"foreach (int {v} in {n}) {{",
        upto=lambda k, n: f"for (int {k} = 0; {k} < {n}.Length; {k}++) {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: (
            f"for (int {k} = {n}.Length - 1; {k} >= 0; {k}--) {{"),
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"var {n} = new System.Collections.Generic.List<int>();",
        push=lambda n, e: f"{n}.Add({e});",
        grid=lambda n, rs: f"int[][] {n} = {{{_csharp_grid(rs)}}};",
        rows=lambda r, n: f"foreach (int[] {r} in {n}) {{",
        cols=lambda c, r: f"foreach (int {c} in {r}) {{",
        times=lambda n, i, p: (
            f'System.Console.WriteLine($"{{{n}}} x {{{i}}} = {{{p}}}");'),
        stepped=lambda v, lo, hi, s: (
            f"for (int {v} = {lo}; {v} <= {hi}; {v} += {s}) {{"),
        stop="break;",
    ),
    "odin": Lists(
        lit=lambda n, xs: f"{n} := []int{{{xs}}}",
        each=lambda v, n: f"for {v} in {n} {{",
        upto=lambda k, n: f"for {k} := 0; {k} < len({n}); {k} += 1 {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: f"for {k} := len({n}) - 1; {k} >= 0; {k} -= 1 {{",
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"{n} := make([dynamic]int)",
        push=lambda n, e: f"append(&{n}, {e})",
        grid=lambda n, rs: f"{n} := [][]int{{{_braced(rs)}}}",
        rows=lambda r, n: f"for {r} in {n} {{",
        cols=lambda c, r: f"for {c} in {r} {{",
        times=lambda n, i, p: f'fmt.printf("%d x %d = %d\\n", {n}, {i}, {p})',
        stepped=lambda v, lo, hi, s: (
            f"for {v} := {lo}; {v} <= {hi}; {v} += {s} {{"),
    ),
    "zig": Lists(
        lit=lambda n, xs: f"const {n} = [_]i32{{ {xs} }};",
        each=lambda v, n: f"for ({n}) |{v}| {{",
        upto=lambda k, n: f"for (0..{n}.len) |{k}| {{",
        at=lambda n, k: f"{n}[{k}]",
        # No reversed iterator, so it counts forwards and subtracts. That
        # is what the standard library's own reverse helpers do inside.
        down=lambda k, n: f"for (0..{n}.len) |{k}| {{",
        down_at=lambda n, k: f"{n}[{n}.len - 1 - {k}]",
        # No growable list without an allocator, so it builds into a
        # fixed array and carries how much of it is real — which is the
        # same answer C gives on this page.
        empty=lambda n: f"var {n}: [64]i32 = undefined;\nvar len: usize = 0;",
        push=lambda n, e: f"{n}[len] = {e};\nlen += 1;",
        built_walk=lambda v, n: f"for ({n}[0..len]) |{v}| {{",
        grid=lambda n, rs: f"const {n} = [_][{len(rs[0])}]i32{{ {_zig_grid(rs)} }};",
        rows=lambda r, n: f"for ({n}) |{r}| {{",
        cols=lambda c, r: f"for ({r}) |{c}| {{",
        times=lambda n, i, p: (
            f'try out.print("{{d}} x {{d}} = {{d}}\\n", .{{ {n}, {i}, {p} }});'),
        stepped=lambda v, lo, hi, s: (
            f"var {v}: i32 = {lo};\nwhile ({v} <= {hi}) : ({v} += {s}) {{"),
        stop="break;",
    ),
    "kotlin": Lists(
        lit=lambda n, xs: f"val {n} = listOf({xs})",
        each=lambda v, n: f"for ({v} in {n}) {{",
        upto=lambda k, n: f"for ({k} in {n}.indices) {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: f"for ({k} in {n}.indices.reversed()) {{",
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"val {n} = mutableListOf<Int>()",
        push=lambda n, e: f"{n}.add({e})",
        grid=lambda n, rs: f"val {n} = listOf({_listed(rs)})",
        rows=lambda r, n: f"for ({r} in {n}) {{",
        cols=lambda c, r: f"for ({c} in {r}) {{",
        times=lambda n, i, p: (
            'println("${' + n + '} x ${' + i + '} = ${' + p + '}")'),
        stepped=lambda v, lo, hi, s: (
            f"for ({v} in {lo}..{hi} step {s}) {{"),
    ),
    "swift": Lists(
        lit=lambda n, xs: f"let {n} = [{xs}]",
        each=lambda v, n: f"for {v} in {n} {{",
        upto=lambda k, n: f"for {k} in 0..<{n}.count {{",
        at=lambda n, k: f"{n}[{k}]",
        down=lambda k, n: (
            f"for {k} in stride(from: {n}.count - 1, through: 0, by: -1) {{"),
        down_at=lambda n, k: f"{n}[{k}]",
        empty=lambda n: f"var {n}: [Int] = []",
        push=lambda n, e: f"{n}.append({e})",
        grid=lambda n, rs: f"let {n} = [{_bracketed(rs)}]",
        rows=lambda r, n: f"for {r} in {n} {{",
        cols=lambda c, r: f"for {c} in {r} {{",
        times=lambda n, i, p: f'print("\\({n}) x \\({i}) = \\({p})")',
        stepped=lambda v, lo, hi, s: (
            f"for {v} in stride(from: {lo}, through: {hi}, by: {s}) {{"),
    ),
}


def handles(shape: str) -> bool:
    return shape in SHAPES


def supports(language: str, shape: str) -> bool:
    """Whether this language is given this page at all."""
    if shape not in SHAPES:
        return False
    if language in ONE_BASED and shape in POSITIONAL:
        return False
    # Lisp is not a row in the table — see `_lisp` below for why — but it
    # answers all the same shapes.
    return language in LISTS or language == "lisp"


def solution(language: str, shape: str, args: dict) -> str | None:
    """The reference answer, or None when this language is not given it."""
    if not supports(language, shape):
        return None
    d = DIALECTS.get(language)
    x = EXTRAS.get(language)
    ls = LISTS.get(language)
    if d is None or x is None:
        return None

    a = args
    fix = d.fix

    if language == "lisp":
        lisp_rows = _lisp(shape, a, fix)
        return _nest(d, *lisp_rows) if lisp_rows else None

    if ls is None:
        return None
    rows: list[tuple[int, str]] = []

    def line(depth: int, text: str) -> None:
        # One entry may be two statements — Zig's counted loops are a
        # variable and a while, because its for has no third clause. The
        # stored form carries its own indent, which is right at the top
        # level and wrong anywhere else, so the depth supplies it here.
        for part in text.split("\n"):
            rows.append((depth, part.strip()))

    def close(depth: int, closers) -> None:
        for text in closers:
            line(depth, text)

    if shape == "list_loop":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, ls.each("n", "nums"))
        line(1, d.say(fix(a["expr"])))
        close(0, d.close_loop)

    elif shape == "list_sum":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, d.total)
        line(0, ls.each("n", "nums"))
        line(1, d.add(fix("n")))
        close(0, d.close_loop)
        line(0, d.say_total)

    elif shape == "list_index":
        line(0, ls.lit("nums", _items(a["items"])))
        for index in a["indexes"]:
            line(0, d.say(ls.at("nums", str(index))))

    elif shape == "list_filter":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, ls.each("n", "nums"))
        line(1, d.when(fix(a["cond"])))
        line(2, d.say(fix("n")))
        close(1, x.close_if)
        close(0, d.close_loop)

    elif shape == "list_build":
        # Not `out`: that is what Zig calls its writer, and shadowing it
        # is a compile error in the one language where it matters.
        walk = ls.built_walk or ls.each
        line(0, ls.empty("built"))
        line(0, d.ranged("i", str(a["lo"]), str(a["hi"])))
        line(1, ls.push("built", fix(a["expr"])))
        close(0, d.close_loop)
        line(0, walk("n", "built"))
        line(1, d.say(fix("n")))
        close(0, d.close_loop)

    elif shape in ("list_max", "list_min"):
        beats = ">" if shape == "list_max" else "<"
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, x.let_mut("best", ls.at("nums", ls.first)))
        line(0, ls.each("n", "nums"))
        line(1, d.when(fix(f"n {beats} best")))
        line(2, x.assign("best", fix("n")))
        close(1, x.close_if)
        close(0, d.close_loop)
        line(0, d.say(fix("best")))

    elif shape == "list_reverse":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, ls.down("k", "nums"))
        line(1, d.say(ls.down_at("nums", fix("k"))))
        close(0, d.close_loop)

    elif shape == "find_index":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, ls.upto("k", "nums"))
        line(1, d.when(f"{ls.at('nums', fix('k'))} == {a['target']}"))
        line(2, d.say(fix("k")))
        line(2, ls.stop)
        close(1, x.close_if)
        close(0, d.close_loop)

    elif shape == "count_matches":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, d.total)
        line(0, ls.each("n", "nums"))
        line(1, d.when(fix(a["cond"])))
        line(2, d.add("1"))
        close(1, x.close_if)
        close(0, d.close_loop)
        line(0, d.say_total)

    elif shape == "running_total":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, d.total)
        line(0, ls.each("n", "nums"))
        line(1, d.add(fix("n")))
        line(1, d.say_total)
        close(0, d.close_loop)

    elif shape == "label_each":
        line(0, ls.lit("nums", _items(a["items"])))
        line(0, ls.each("n", "nums"))
        line(1, d.when(fix(a["cond"])))
        line(2, d.say_text(_q(a["yes"])))
        for text in x.otherwise:
            line(1, text)
        line(2, d.say_text(_q(a["no"])))
        close(1, x.close_if)
        close(0, d.close_loop)

    elif shape == "two_lists":
        line(0, ls.lit("xs", _items(a["xs"])))
        line(0, ls.lit("ys", _items(a["ys"])))
        line(0, ls.upto("k", "xs"))
        line(1, d.let("x", ls.at("xs", fix("k"))))
        line(1, d.let("y", ls.at("ys", fix("k"))))
        line(1, d.say(fix(a["expr"])))
        close(0, d.close_loop)

    elif shape == "grid_print":
        line(0, ls.grid("grid", a["rows"]))
        line(0, ls.rows("row", "grid"))
        line(1, ls.cols("v", "row"))
        line(2, d.say(fix(a["expr"])))
        close(1, d.close_loop)
        close(0, d.close_loop)

    elif shape == "grid_sum":
        line(0, ls.grid("grid", a["rows"]))
        line(0, d.total)
        line(0, ls.rows("row", "grid"))
        line(1, ls.cols("v", "row"))
        line(2, d.add(fix("v")))
        close(1, d.close_loop)
        close(0, d.close_loop)
        line(0, d.say_total)

    elif shape == "step_loop":
        line(0, ls.stepped("i", str(a["lo"]), str(a["hi"]), str(a["step"])))
        line(1, d.say(fix(a["expr"])))
        close(0, d.close_loop)

    elif shape == "times_table":
        n = str(a["n"])
        line(0, d.ranged("i", "1", str(a["upto"])))
        line(1, ls.times(n, fix("i"), fix(f"{n} * i")))
        close(0, d.close_loop)

    elif shape == "swap_print":
        line(0, x.let_mut("a", str(a["value1"])))
        line(0, x.let_mut("b", str(a["value2"])))
        line(0, d.let("t", fix("a")))
        line(0, x.assign("a", fix("b")))
        line(0, x.assign("b", fix("t")))
        line(0, d.say(fix("a")))
        line(0, d.say(fix("b")))

    else:
        return None

    return _nest(d, *rows)


__all__ = ["LISTS", "SHAPES", "handles", "solution", "supports", "to_prefix"]


# ── Lisp, which is not a row in the table ────────────────────
#
# Every other language here differs from its neighbour by punctuation, so
# one table with a column each says all of it. Lisp differs by shape: a
# condition is a form rather than an infix expression, a loop is one form
# with keywords inside it rather than a header and a body, and reaching
# into a list is a function call. Writing it as a row would have meant a
# column per shape, which is not a table.


def _lisp(shape: str, a: dict, fix) -> list[tuple[int, str]] | None:
    """The rows for one Lisp answer, or None if it has none."""
    rows: list[tuple[int, str]] = []

    def add(depth: int, text: str) -> None:
        rows.append((depth, text))

    def say(expr: str) -> str:
        return f'(format t "~a~%" {expr})'

    def lit(name: str, values) -> str:
        return f"(defparameter {name} (list {' '.join(str(v) for v in values)}))"

    def grid(name: str, grid_rows) -> str:
        inner = " ".join(
            "(list " + " ".join(str(v) for v in row) + ")" for row in grid_rows
        )
        return f"(defparameter {name} (list {inner}))"

    if shape == "list_loop":
        add(0, lit("nums", a["items"]))
        add(0, "(loop for n in nums do")
        add(1, say(fix(a["expr"])))
        add(0, ")")

    elif shape == "list_sum":
        add(0, lit("nums", a["items"]))
        add(0, "(defparameter total 0)")
        add(0, "(loop for n in nums do")
        add(1, "(setf total (+ total n))")
        add(0, ")")
        add(0, say("total"))

    elif shape == "list_index":
        add(0, lit("nums", a["items"]))
        for index in a["indexes"]:
            add(0, say(f"(nth {index} nums)"))

    elif shape == "list_filter":
        add(0, lit("nums", a["items"]))
        add(0, "(loop for n in nums do")
        add(1, f"(when {fix(a['cond'])}")
        add(2, say("n"))
        add(1, ")")
        add(0, ")")

    elif shape == "list_build":
        add(0, "(defparameter built (list))")
        add(0, f"(loop for i from {a['lo']} to {a['hi']} do")
        add(1, f"(setf built (append built (list {fix(a['expr'])})))")
        add(0, ")")
        add(0, "(loop for n in built do")
        add(1, say("n"))
        add(0, ")")

    elif shape in ("list_max", "list_min"):
        beats = ">" if shape == "list_max" else "<"
        add(0, lit("nums", a["items"]))
        add(0, "(defparameter best (nth 0 nums))")
        add(0, "(loop for n in nums do")
        add(1, f"(when ({beats} n best)")
        add(2, "(setf best n)")
        add(1, ")")
        add(0, ")")
        add(0, say("best"))

    elif shape == "list_reverse":
        add(0, lit("nums", a["items"]))
        add(0, "(loop for k from (1- (length nums)) downto 0 do")
        add(1, say("(nth k nums)"))
        add(0, ")")

    elif shape == "find_index":
        add(0, lit("nums", a["items"]))
        add(0, "(loop for k from 0 below (length nums) do")
        add(1, f"(when (= (nth k nums) {a['target']})")
        add(2, say("k"))
        add(2, "(return)")
        add(1, ")")
        add(0, ")")

    elif shape == "count_matches":
        add(0, lit("nums", a["items"]))
        add(0, "(defparameter total 0)")
        add(0, "(loop for n in nums do")
        add(1, f"(when {fix(a['cond'])}")
        add(2, "(setf total (+ total 1))")
        add(1, ")")
        add(0, ")")
        add(0, say("total"))

    elif shape == "running_total":
        add(0, lit("nums", a["items"]))
        add(0, "(defparameter total 0)")
        add(0, "(loop for n in nums do")
        add(1, "(setf total (+ total n))")
        add(1, say("total"))
        add(0, ")")

    elif shape == "label_each":
        add(0, lit("nums", a["items"]))
        add(0, "(loop for n in nums do")
        add(1, f"(if {fix(a['cond'])}")
        add(2, f'(format t "~a~%" "{a["yes"]}")')
        add(2, f'(format t "~a~%" "{a["no"]}")')
        add(1, ")")
        add(0, ")")

    elif shape == "two_lists":
        add(0, lit("xs", a["xs"]))
        add(0, lit("ys", a["ys"]))
        add(0, "(loop for x in xs for y in ys do")
        add(1, say(fix(a["expr"])))
        add(0, ")")

    elif shape == "grid_print":
        add(0, grid("grid", a["rows"]))
        add(0, "(loop for row in grid do")
        add(1, "(loop for v in row do")
        add(2, say(fix(a["expr"])))
        add(1, ")")
        add(0, ")")

    elif shape == "grid_sum":
        add(0, grid("grid", a["rows"]))
        add(0, "(defparameter total 0)")
        add(0, "(loop for row in grid do")
        add(1, "(loop for v in row do")
        add(2, "(setf total (+ total v))")
        add(1, ")")
        add(0, ")")
        add(0, say("total"))

    elif shape == "step_loop":
        add(0, f"(loop for i from {a['lo']} to {a['hi']} by {a['step']} do")
        add(1, say(fix(a["expr"])))
        add(0, ")")

    elif shape == "times_table":
        n = a["n"]
        add(0, f"(loop for i from 1 to {a['upto']} do")
        add(1, f'(format t "~a x ~a = ~a~%" {n} i (* {n} i))')
        add(0, ")")

    elif shape == "swap_print":
        add(0, f"(defparameter a {a['value1']})")
        add(0, f"(defparameter b {a['value2']})")
        add(0, "(defparameter t2 a)")
        add(0, "(setf a b)")
        add(0, "(setf b t2)")
        add(0, say("a"))
        add(0, say("b"))

    else:
        return None

    return rows
