"""Functions and strings, in the nine languages added tonight.

Pages 27 to 33, 46 to 48, and their practice pages at 77 to 79. Ten
shapes: a function that prints, one that takes a value, one that hands a
value back, one that takes two, one that answers in words, and then the
length of a string, walking its characters, upper case, joining two, and
the character at a position.

This needed a third record rather than another column on the list table,
and for a reason worth writing down. Everything up to here goes *inside*
the body — the file has a shape, and the exercise is statements poured
into it. A function does not: it is a second thing at the top level, and
where "the top level" is differs. Go and Odin and Zig put it above main.
Java puts it inside the class and beside main. PHP, Lua, Ruby, C# and
Lisp have no enclosing body at all, so it simply goes first. So a
definition carries where it goes, as a count of how many of the opening
lines come before it.

Zig needed one more thing than the others. Its writer is a local in main,
so a function that prints has nothing to print to unless it is handed the
writer — which is exactly what the Zig answer is, and is more honest than
pretending a global exists.

Lua declines the character-at-a-position page for the same reason it
declines the two list pages: it counts from one, and the page is about
index zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from code_coach.workbook.emit_newlang2 import DIALECTS, NL, _q
from code_coach.workbook.emit_newlang4 import ONE_BASED

SHAPES: tuple[str, ...] = (
    "func_print",
    "func_arg",
    "func_return",
    "func_two",
    "func_word",
    "str_length",
    "str_loop",
    "str_upper",
    "join_words",
    "char_at",
)

#: The page about index zero, which a language counting from one answers
#: with a different number.
POSITIONAL: tuple[str, ...] = ("char_at",)


@dataclass(frozen=True)
class Funcs:
    """How one language declares a function and calls it."""

    #: Open a definition, given the name, the rendered parameters, and
    #: what it hands back — "" for nothing, "int" or "text".
    define: Callable[[str, str, str], str]
    close_def: tuple[str, ...]
    #: One parameter: its name, and whether it is a number or text.
    param: Callable[[str, str], str]
    #: Hand a value back, as the last thing the function does.
    give: Callable[[str], str]
    #: Call it: as a statement on its own, and as an expression.
    call: Callable[[str, str], str]
    use: Callable[[str, str], str]
    #: How many of the dialect's opening lines come before a definition,
    #: and what it is indented by once it is there.
    #: Hand a value back from the middle. The same in every language
    #: except the one where the last expression is the answer and a bare
    #: value in the middle is simply discarded.
    give_early: Callable[[str], str] | None = None
    defs_at: int = 0
    def_indent: str = ""
    #: Lines the body of a definition needs before anything else. Only
    #: Zig has one, and it is the writer it was handed.
    extra_param: str = ""
    extra_arg: str = ""


@dataclass(frozen=True)
class Strs:
    """How one language asks a string its length and takes it apart."""

    length: Callable[[str], str]
    chars: Callable[[str, str], str]
    upper: Callable[[str], str]
    join: Callable[[str, str], str]
    char_at: Callable[[str, str], str]
    #: Bind a word to a name. The dialect's `let` declares a number, and
    #: the two languages with types would reject a string in it.
    let_text: Callable[[str, str], str] = lambda n, v: f"{n} = {v}"
    #: Printing one character, when that is not printing a string.
    say_char: Callable[[str], str] | None = None
    #: Lines needed before upper case works. Only Zig needs a buffer.
    upper_setup: tuple[str, ...] = field(default_factory=tuple)
    #: An import this language needs before upper case exists. Go will
    #: not compile with an import it does not use, so it is attached to
    #: the one shape that uses it rather than to the header.
    upper_import: str = ""


def _int(kind: str) -> bool:
    return kind == "int"


FUNCS: dict[str, Funcs] = {
    "go": Funcs(
        define=lambda n, p, r: (
            f"func {n}({p})"
            + {"": " {", "int": " int {", "text": " string {"}[r]),
        close_def=("}",),
        param=lambda n, k: f"{n} int" if _int(k) else f"{n} string",
        give=lambda e: f"return {e}",
        call=lambda n, a: f"{n}({a})",
        use=lambda n, a: f"{n}({a})",
    ),
    "odin": Funcs(
        define=lambda n, p, r: (
            f"{n} :: proc({p})"
            + {"": " {", "int": " -> int {", "text": " -> string {"}[r]),
        close_def=("}",),
        param=lambda n, k: f"{n}: int" if _int(k) else f"{n}: string",
        give=lambda e: f"return {e}",
        call=lambda n, a: f"{n}({a})",
        use=lambda n, a: f"{n}({a})",
    ),
    "php": Funcs(
        define=lambda n, p, r: f"function {n}({p}) {{",
        close_def=("}",),
        param=lambda n, k: f"${n}",
        give=lambda e: f"return {e};",
        call=lambda n, a: f"{n}({a});",
        use=lambda n, a: f"{n}({a})",
    ),
    "lua": Funcs(
        define=lambda n, p, r: f"local function {n}({p})",
        close_def=("end",),
        param=lambda n, k: n,
        give=lambda e: f"return {e}",
        call=lambda n, a: f"{n}({a})",
        use=lambda n, a: f"{n}({a})",
    ),
    "ruby": Funcs(
        define=lambda n, p, r: f"def {n}({p})" if p else f"def {n}",
        close_def=("end",),
        param=lambda n, k: n,
        give=lambda e: e,
        give_early=lambda e: f"return {e}",
        call=lambda n, a: f"{n}({a})" if a else n,
        use=lambda n, a: f"{n}({a})" if a else n,
    ),
    "java": Funcs(
        define=lambda n, p, r: (
            {"": "static void ", "int": "static int ",
             "text": "static String "}[r] + f"{n}({p}) {{"),
        close_def=("}",),
        param=lambda n, k: f"int {n}" if _int(k) else f"String {n}",
        give=lambda e: f"return {e};",
        call=lambda n, a: f"{n}({a});",
        use=lambda n, a: f"{n}({a})",
        # Beside main rather than above it: Java has no top level.
        defs_at=1,
        def_indent="    ",
    ),
    "csharp": Funcs(
        define=lambda n, p, r: (
            {"": "void ", "int": "int ", "text": "string "}[r]
            + f"{n}({p}) {{"),
        close_def=("}",),
        param=lambda n, k: f"int {n}" if _int(k) else f"string {n}",
        give=lambda e: f"return {e};",
        call=lambda n, a: f"{n}({a});",
        use=lambda n, a: f"{n}({a})",
    ),
    "zig": Funcs(
        define=lambda n, p, r: (
            f"fn {n}({p})"
            + {"": " !void {", "int": " i32 {", "text": " []const u8 {"}[r]),
        close_def=("}",),
        param=lambda n, k: f"{n}: i32" if _int(k) else f"{n}: []const u8",
        give=lambda e: f"return {e};",
        call=lambda n, a: f"try {n}({a});",
        use=lambda n, a: f"{n}({a})",
        # A function that prints is handed the writer, because in Zig the
        # writer is a local in main and there is no global to reach for.
        extra_param="out: *std.Io.Writer",
        extra_arg="out",
    ),
}


STRS: dict[str, Strs] = {
    "go": Strs(
        length=lambda s: f"len({s})",
        chars=lambda v, s: f"for _, {v} := range {s} {{",
        upper=lambda s: f"strings.ToUpper({s})",
        join=lambda a, b: f'{a} + " " + {b}',
        char_at=lambda s, i: f"string({s}[{i}])",
        say_char=lambda e: f"fmt.Println(string({e}))",
        let_text=lambda n, v: f"{n} := {v}",
        upper_import='import "strings"',
    ),
    "odin": Strs(
        length=lambda s: f"len({s})",
        chars=lambda v, s: f"for {v} in {s} {{",
        upper=lambda s: f"strings.to_upper({s})",
        join=lambda a, b: f'fmt.tprintf("%s %s", {a}, {b})',
        char_at=lambda s, i: f"{s}[{i}]",
        say_char=lambda e: f'fmt.printf("%c\\n", {e})',
        let_text=lambda n, v: f"{n} := {v}",
        upper_import='import "core:strings"',
    ),
    "php": Strs(
        length=lambda s: f"strlen({s})",
        chars=lambda v, s: (
            f"foreach (str_split({s}) as ${v}) {{"),
        upper=lambda s: f"strtoupper({s})",
        join=lambda a, b: f'{a} . " " . {b}',
        char_at=lambda s, i: f"{s}[{i}]",
        let_text=lambda n, v: f"${n} = {v};",
    ),
    "lua": Strs(
        length=lambda s: f"#{s}",
        chars=lambda v, s: f'for {v} in string.gmatch({s}, ".") do',
        upper=lambda s: f"string.upper({s})",
        join=lambda a, b: f'{a} .. " " .. {b}',
        char_at=lambda s, i: f"string.sub({s}, {i}, {i})",
        let_text=lambda n, v: f"local {n} = {v}",
    ),
    "ruby": Strs(
        length=lambda s: f"{s}.length",
        chars=lambda v, s: f"{s}.each_char do |{v}|",
        upper=lambda s: f"{s}.upcase",
        join=lambda a, b: f"{a} + ' ' + {b}",
        char_at=lambda s, i: f"{s}[{i}]",
        let_text=lambda n, v: f"{n} = {v}",
    ),
    "java": Strs(
        length=lambda s: f"{s}.length()",
        chars=lambda v, s: f"for (char {v} : {s}.toCharArray()) {{",
        upper=lambda s: f"{s}.toUpperCase()",
        join=lambda a, b: f'{a} + " " + {b}',
        char_at=lambda s, i: f"{s}.charAt({i})",
        say_char=lambda e: f"System.out.println({e});",
        let_text=lambda n, v: f"String {n} = {v};",
    ),
    "csharp": Strs(
        length=lambda s: f"{s}.Length",
        chars=lambda v, s: f"foreach (char {v} in {s}) {{",
        # Invariant on purpose: the plain overload asks the machine what
        # country it is in, and in Turkish a dotted i upper-cases to a
        # different letter. A drill must print the same thing everywhere.
        upper=lambda s: f"{s}.ToUpperInvariant()",
        join=lambda a, b: f'{a} + " " + {b}',
        char_at=lambda s, i: f"{s}[{i}]",
        say_char=lambda e: f"System.Console.WriteLine({e});",
        let_text=lambda n, v: f"string {n} = {v};",
    ),
    "zig": Strs(
        length=lambda s: f"{s}.len",
        chars=lambda v, s: f"for ({s}) |{v}| {{",
        upper=lambda s: f"std.ascii.upperString(&ubuf, {s})",
        join=lambda a, b: f"{a} ++ \" \" ++ {b}",
        char_at=lambda s, i: f"{s}[{i}]",
        say_char=lambda e: 'try out.print("{c}\\n", .{' + e + "});",
        upper_setup=("var ubuf: [64]u8 = undefined;",),
        let_text=lambda n, v: f"const {n} = {v};",
    ),
}


def handles(shape: str) -> bool:
    return shape in SHAPES


def supports(language: str, shape: str) -> bool:
    if shape not in SHAPES:
        return False
    if language in ONE_BASED and shape in POSITIONAL:
        return False
    return language in FUNCS or language == "lisp"


def _assemble(d, fn: Funcs, defs, body, imports=()) -> str:
    """header, then the definitions where they go, then the body."""
    from code_coach.workbook.emit_newlang2 import _hug

    lines = list(d.header)
    for line in imports:
        if line:
            lines.append(line)
    if imports:
        lines.append("")

    step = d.step or d.indent
    opening = list(d.open_body)
    lines += opening[:fn.defs_at]
    for depth, text in defs:
        lines.append((fn.def_indent + step * depth if text else "") + text)
    if defs:
        lines.append("")
    lines += opening[fn.defs_at:]

    base = d.indent if d.open_body else ""
    for depth, text in body:
        lines.append((base + step * depth if text else "") + text)
    lines += list(d.close_body)
    return NL.join(_hug(d, lines)) + NL


def solution(language: str, shape: str, args: dict) -> str | None:
    if not supports(language, shape):
        return None
    d = DIALECTS.get(language)
    if d is None:
        return None
    if language == "lisp":
        return _lisp(d, shape, args)
    fn, st = FUNCS.get(language), STRS.get(language)
    if fn is None or st is None:
        return None

    a = args
    fix = d.fix
    defs: list[tuple[int, str]] = []
    body: list[tuple[int, str]] = []
    imports: list[str] = []

    def params(*pairs) -> str:
        # Zig's printing functions are handed the writer, and it goes
        # first, the way a receiver would.
        rendered = [fn.param(n, k) for n, k in pairs]
        return ", ".join(rendered)

    def printing_params(*pairs) -> str:
        rendered = [fn.param(n, k) for n, k in pairs]
        if fn.extra_param:
            rendered.insert(0, fn.extra_param)
        return ", ".join(rendered)

    def printing_args(*values) -> str:
        given = [str(v) for v in values]
        if fn.extra_arg:
            given.insert(0, fn.extra_arg)
        return ", ".join(given)

    if shape == "func_print":
        defs.append((0, fn.define(a["name"], printing_params(), "")))
        for _ in range(a["times"]):
            defs.append((1, d.say_text(_q(a["text"]))))
        defs += [(0, line) for line in fn.close_def]
        body.append((0, fn.call(a["name"], printing_args())))

    elif shape == "func_arg":
        p = a["param"]
        defs.append((0, fn.define(a["name"], printing_params((p, "int")), "")))
        defs.append((1, d.say(fix(a["expr"]))))
        defs += [(0, line) for line in fn.close_def]
        for value in a["calls"]:
            body.append((0, fn.call(a["name"], printing_args(value))))

    elif shape == "func_return":
        p = a["param"]
        defs.append((0, fn.define(a["name"], params((p, "int")), "int")))
        defs.append((1, fn.give(fix(a["expr"]))))
        defs += [(0, line) for line in fn.close_def]
        for value in a["calls"]:
            body.append((0, d.say(fn.use(a["name"], str(value)))))

    elif shape == "func_two":
        p1, p2 = a["param1"], a["param2"]
        defs.append(
            (0, fn.define(a["name"], params((p1, "int"), (p2, "int")), "int")))
        defs.append((1, fn.give(fix(a["expr"]))))
        defs += [(0, line) for line in fn.close_def]
        for one, two in a["calls"]:
            body.append((0, d.say(fn.use(a["name"], f"{one}, {two}"))))

    elif shape == "func_word":
        p = a["param"]
        defs.append((0, fn.define(a["name"], params((p, "int")), "text")))
        defs.append((1, d.when(fix(a["cond"]))))
        defs.append((2, (fn.give_early or fn.give)(_q(a["yes"]))))
        defs += [(1, line) for line in _close_if(language)]
        defs.append((1, fn.give(_q(a["no"]))))
        defs += [(0, line) for line in fn.close_def]
        for value in a["calls"]:
            body.append((0, d.say_text(fn.use(a["name"], str(value)))))

    elif shape == "str_length":
        body.append((0, st.let_text("word", _q(a["word"]))))
        body.append((0, d.say(st.length(fix("word")))))

    elif shape == "str_loop":
        body.append((0, st.let_text("word", _q(a["word"]))))
        body.append((0, st.chars("c", fix("word"))))
        say_one = st.say_char or d.say_text
        body.append((1, say_one(fix("c"))))
        body += [(0, line) for line in d.close_loop]

    elif shape == "str_upper":
        if st.upper_import:
            imports.append(st.upper_import)
        body.append((0, st.let_text("word", _q(a["word"]))))
        body += [(0, line) for line in st.upper_setup]
        body.append((0, d.say_text(st.upper(fix("word")))))

    elif shape == "join_words":
        body.append((0, st.let_text("one", _q(a["word1"]))))
        body.append((0, st.let_text("two", _q(a["word2"]))))
        body.append((0, d.say_text(st.join(fix("one"), fix("two")))))

    elif shape == "char_at":
        body.append((0, st.let_text("word", _q(a["word"]))))
        say_one = st.say_char or d.say_text
        body.append((0, say_one(st.char_at(fix("word"), str(a["index"])))))

    else:
        return None

    return _assemble(d, fn, defs, body, imports)


def _close_if(language: str) -> tuple[str, ...]:
    from code_coach.workbook.emit_newlang3 import EXTRAS

    return EXTRAS[language].close_if


# ── Lisp ─────────────────────────────────────────────────────
#
# The one language here where a definition is not a second kind of thing:
# `defun` is a form like any other and sits at the top level beside the
# forms that call it, so none of the placement above applies.


def _lisp(d, shape: str, a: dict) -> str | None:
    from code_coach.workbook.emit_newlang2 import _hug

    fix = d.fix
    rows: list[tuple[int, str]] = []

    def add(depth: int, text: str) -> None:
        rows.append((depth, text))

    def say(expr: str) -> str:
        return f'(format t "~a~%" {expr})'

    if shape == "func_print":
        add(0, f"(defun {a['name']} ()")
        for _ in range(a["times"]):
            add(1, say(f'"{a["text"]}"'))
        add(0, ")")
        add(0, f"({a['name']})")

    elif shape == "func_arg":
        add(0, f"(defun {a['name']} ({a['param']})")
        add(1, say(fix(a["expr"])))
        add(0, ")")
        for value in a["calls"]:
            add(0, f"({a['name']} {value})")

    elif shape == "func_return":
        add(0, f"(defun {a['name']} ({a['param']})")
        add(1, fix(a["expr"]))
        add(0, ")")
        for value in a["calls"]:
            add(0, say(f"({a['name']} {value})"))

    elif shape == "func_two":
        add(0, f"(defun {a['name']} ({a['param1']} {a['param2']})")
        add(1, fix(a["expr"]))
        add(0, ")")
        for one, two in a["calls"]:
            add(0, say(f"({a['name']} {one} {two})"))

    elif shape == "func_word":
        add(0, f"(defun {a['name']} ({a['param']})")
        add(1, f"(if {fix(a['cond'])}")
        add(2, f'"{a["yes"]}"')
        add(2, f'"{a["no"]}"')
        add(1, ")")
        add(0, ")")
        for value in a["calls"]:
            add(0, say(f"({a['name']} {value})"))

    elif shape == "str_length":
        add(0, f'(defparameter word "{a["word"]}")')
        add(0, say("(length word)"))

    elif shape == "str_loop":
        add(0, f'(defparameter word "{a["word"]}")')
        add(0, "(loop for c across word do")
        add(1, say("c"))
        add(0, ")")

    elif shape == "str_upper":
        add(0, f'(defparameter word "{a["word"]}")')
        add(0, say("(string-upcase word)"))

    elif shape == "join_words":
        add(0, f'(defparameter one "{a["word1"]}")')
        add(0, f'(defparameter two "{a["word2"]}")')
        add(0, say('(concatenate (quote string) one " " two)'))

    elif shape == "char_at":
        add(0, f'(defparameter word "{a["word"]}")')
        add(0, say(f"(char word {a['index']})"))

    else:
        return None

    lines = [(d.indent * depth if text else "") + text for depth, text in rows]
    return NL.join(_hug(d, lines)) + NL
