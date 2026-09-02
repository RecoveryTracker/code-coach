"""The rest of the ramp: strings, conditions, lists and functions.

`emit` covers arithmetic and counting loops, where all seven languages are
spelled closely enough that one exercise is plainly one question. These
shapes are the ones where they stop agreeing — a list is not the same object
in C as in Python, and a string is not the same object at all.

They were written for Python, JavaScript and Dart first, on the assumption
that the others would need the exercise faked. They did not: each language
answers the same question the way that language actually would, which is the
interesting part rather than the obstacle. Seeing what it costs to grow a
list in C is most of what C has to teach.

This module holds the languages with a list type and string methods;
`emit_more_native` holds C, C++ and Rust.

The rule from `emit` still holds and is the thing to be careful about: every
language's answer must print exactly the same characters. That is why nothing
here prints a whole list (Python says [1, 2], Node says [ 1, 2 ]) or a
boolean (True against true), and why division is absent — the shapes print
numbers and plain lines, one per line, and the differences stay inside the
code where they belong.
"""

from __future__ import annotations

from typing import Callable

from code_coach.workbook.emit import NL, Shape, _lines, _q

# Everywhere the workbook runs. SQL is the only one left out, and for the
# same reason as in `emit`: no statement that prints a line, and no loop.
LANGUAGES: tuple[str, ...] = (
    "python",
    "javascript",
    "typescript",
    "dart",
    "c",
    "cpp",
    "rust",
)


SHAPES: tuple[Shape, ...] = (
    Shape("say_value", "putting a worked-out value inside a line of text"),
    Shape("repeat_text", "a loop whose body does not use the counter"),
    Shape("quoted_text", "quotation marks inside a quoted string"),
    Shape("if_print", "doing something only when a condition holds"),
    Shape("if_else_print", "choosing between two outcomes"),
    Shape("bigger_print", "comparing two values and keeping one"),
    Shape("and_or_print", "two conditions joined into one"),
    Shape("while_count", "a loop that runs until you stop it"),
    Shape("while_sum", "accumulating inside a while loop"),
    Shape("list_loop", "visiting every item of a list"),
    Shape("list_sum", "totalling a list"),
    Shape("list_index", "reaching one item by its position"),
    Shape("list_filter", "printing only the items that qualify"),
    Shape("list_build", "growing a list as you go"),
    Shape("list_max", "carrying the best-so-far through a loop"),
    Shape("func_print", "naming a piece of work and running it"),
    Shape("func_arg", "a function that takes a value"),
    Shape("func_return", "a function that hands a value back"),
    Shape("str_length", "asking a string how long it is"),
    Shape("str_loop", "visiting every character"),
    Shape("str_upper", "calling a method on a string"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def _list_literal(items) -> str:
    """Spelled the same everywhere it is used, which is what lets the shape
    carry the numbers and leave the language to the emitter."""
    return "[" + ", ".join(str(n) for n in items) + "]"


# ── Python ───────────────────────────────────────────────────

def _python(shape: str, a: dict) -> str:
    if shape == "say_value":
        return 'print(f"' + a["label"] + ': {' + a["expr"] + '}")'
    if shape == "repeat_text":
        return _lines(
            f"for i in range({a['count']}):", f"    print({_q(a['text'])})"
        )
    if shape == "quoted_text":
        return f"print({_q(a['text'])})"
    if shape == "if_print":
        return _lines(
            f"{a['name']} = {a['value']}",
            f"if {a['cond']}:",
            f"    print({_q(a['text'])})",
        )
    if shape == "if_else_print":
        return _lines(
            f"{a['name']} = {a['value']}",
            f"if {a['cond']}:",
            f"    print({_q(a['yes'])})",
            "else:",
            f"    print({_q(a['no'])})",
        )
    if shape == "bigger_print":
        return _lines(
            f"{a['name1']} = {a['value1']}",
            f"{a['name2']} = {a['value2']}",
            f"if {a['name1']} > {a['name2']}:",
            f"    print({a['name1']})",
            "else:",
            f"    print({a['name2']})",
        )
    if shape == "and_or_print":
        joiner = "and" if a["op"] == "and" else "or"
        return _lines(
            f"{a['name']} = {a['value']}",
            f"if {a['left']} {joiner} {a['right']}:",
            f"    print({_q(a['yes'])})",
            "else:",
            f"    print({_q(a['no'])})",
        )
    if shape == "while_count":
        return _lines(
            f"i = {a['lo']}",
            f"while i <= {a['hi']}:",
            f"    print({a['expr']})",
            "    i += 1",
        )
    if shape == "while_sum":
        return _lines(
            f"i = {a['lo']}",
            "total = 0",
            f"while i <= {a['hi']}:",
            f"    total += {a['expr']}",
            "    i += 1",
            "print(total)",
        )
    if shape == "list_loop":
        return _lines(
            f"nums = {_list_literal(a['items'])}",
            "for n in nums:",
            f"    print({a['expr']})",
        )
    if shape == "list_sum":
        return _lines(
            f"nums = {_list_literal(a['items'])}",
            "total = 0",
            "for n in nums:",
            "    total += n",
            "print(total)",
        )
    if shape == "list_index":
        picks = [f"print(nums[{i}])" for i in a["indexes"]]
        return _lines(f"nums = {_list_literal(a['items'])}", *picks)
    if shape == "list_filter":
        return _lines(
            f"nums = {_list_literal(a['items'])}",
            "for n in nums:",
            f"    if {a['cond']}:",
            "        print(n)",
        )
    if shape == "list_build":
        return _lines(
            "out = []",
            f"for i in range({a['lo']}, {a['hi']} + 1):",
            f"    out.append({a['expr']})",
            "for n in out:",
            "    print(n)",
        )
    if shape == "list_max":
        return _lines(
            f"nums = {_list_literal(a['items'])}",
            "best = nums[0]",
            "for n in nums:",
            "    if n > best:",
            "        best = n",
            "print(best)",
        )
    if shape == "func_print":
        return _lines(
            f"def {a['name']}():",
            f"    print({_q(a['text'])})",
            "",
            *[f"{a['name']}()" for _ in range(a["times"])],
        )
    if shape == "func_arg":
        return _lines(
            f"def {a['name']}({a['param']}):",
            f"    print({a['expr']})",
            "",
            *[f"{a['name']}({v})" for v in a["calls"]],
        )
    if shape == "func_return":
        return _lines(
            f"def {a['name']}({a['param']}):",
            f"    return {a['expr']}",
            "",
            *[f"print({a['name']}({v}))" for v in a["calls"]],
        )
    if shape == "str_length":
        return f"print(len({_q(a['word'])}))"
    if shape == "str_loop":
        return _lines(f"for c in {_q(a['word'])}:", "    print(c)")
    if shape == "str_upper":
        return f"print({_q(a['word'])}.upper())"
    raise KeyError(shape)


# ── JavaScript ───────────────────────────────────────────────

def _js(shape: str, a: dict) -> str:
    tick = chr(96)
    if shape == "say_value":
        return (
            "console.log("
            + tick
            + a["label"]
            + ": ${"
            + a["expr"]
            + "}"
            + tick
            + ");"
        )
    if shape == "repeat_text":
        return _lines(
            f"for (let i = 0; i < {a['count']}; i++) {{",
            f"  console.log({_q(a['text'])});",
            "}",
        )
    if shape == "quoted_text":
        return f"console.log({_q(a['text'])});"
    if shape == "if_print":
        return _lines(
            f"const {a['name']} = {a['value']};",
            f"if ({a['cond']}) {{",
            f"  console.log({_q(a['text'])});",
            "}",
        )
    if shape == "if_else_print":
        return _lines(
            f"const {a['name']} = {a['value']};",
            f"if ({a['cond']}) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "bigger_print":
        return _lines(
            f"const {a['name1']} = {a['value1']};",
            f"const {a['name2']} = {a['value2']};",
            f"if ({a['name1']} > {a['name2']}) {{",
            f"  console.log({a['name1']});",
            "} else {",
            f"  console.log({a['name2']});",
            "}",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"const {a['name']} = {a['value']};",
            f"if ({a['left']} {joiner} {a['right']}) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "while_count":
        return _lines(
            f"let i = {a['lo']};",
            f"while (i <= {a['hi']}) {{",
            f"  console.log({a['expr']});",
            "  i++;",
            "}",
        )
    if shape == "while_sum":
        return _lines(
            f"let i = {a['lo']};",
            "let total = 0;",
            f"while (i <= {a['hi']}) {{",
            f"  total += {a['expr']};",
            "  i++;",
            "}",
            "console.log(total);",
        )
    if shape == "list_loop":
        return _lines(
            f"const nums = {_list_literal(a['items'])};",
            "for (const n of nums) {",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "list_sum":
        return _lines(
            f"const nums = {_list_literal(a['items'])};",
            "let total = 0;",
            "for (const n of nums) {",
            "  total += n;",
            "}",
            "console.log(total);",
        )
    if shape == "list_index":
        picks = [f"console.log(nums[{i}]);" for i in a["indexes"]]
        return _lines(f"const nums = {_list_literal(a['items'])};", *picks)
    if shape == "list_filter":
        return _lines(
            f"const nums = {_list_literal(a['items'])};",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            "    console.log(n);",
            "  }",
            "}",
        )
    if shape == "list_build":
        return _lines(
            "const out = [];",
            f"for (let i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"  out.push({a['expr']});",
            "}",
            "for (const n of out) {",
            "  console.log(n);",
            "}",
        )
    if shape == "list_max":
        return _lines(
            f"const nums = {_list_literal(a['items'])};",
            "let best = nums[0];",
            "for (const n of nums) {",
            "  if (n > best) {",
            "    best = n;",
            "  }",
            "}",
            "console.log(best);",
        )
    if shape == "func_print":
        return _lines(
            f"function {a['name']}() {{",
            f"  console.log({_q(a['text'])});",
            "}",
            "",
            *[f"{a['name']}();" for _ in range(a["times"])],
        )
    if shape == "func_arg":
        return _lines(
            f"function {a['name']}({a['param']}) {{",
            f"  console.log({a['expr']});",
            "}",
            "",
            *[f"{a['name']}({v});" for v in a["calls"]],
        )
    if shape == "func_return":
        return _lines(
            f"function {a['name']}({a['param']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            *[f"console.log({a['name']}({v}));" for v in a["calls"]],
        )
    if shape == "str_length":
        return f"console.log({_q(a['word'])}.length);"
    if shape == "str_loop":
        return _lines(
            f"for (const c of {_q(a['word'])}) {{", "  console.log(c);", "}"
        )
    if shape == "str_upper":
        return f"console.log({_q(a['word'])}.toUpperCase());"
    raise KeyError(shape)


# ── Dart ─────────────────────────────────────────────────────
#
# Everything but a function definition goes inside main(); functions have to
# sit outside it, so those shapes build the whole file themselves.

def _dart_body(shape: str, a: dict) -> str:
    if shape == "say_value":
        return 'print("' + a["label"] + ': ${' + a["expr"] + '}");'
    if shape == "repeat_text":
        return _lines(
            f"for (var i = 0; i < {a['count']}; i++) {{",
            f"    print({_q(a['text'])});",
            "  }",
        )
    if shape == "quoted_text":
        return f"print({_q(a['text'])});"
    if shape == "if_print":
        return _lines(
            f"var {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            f"    print({_q(a['text'])});",
            "  }",
        )
    if shape == "if_else_print":
        return _lines(
            f"var {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            f"    print({_q(a['yes'])});",
            "  } else {",
            f"    print({_q(a['no'])});",
            "  }",
        )
    if shape == "bigger_print":
        return _lines(
            f"var {a['name1']} = {a['value1']};",
            f"  var {a['name2']} = {a['value2']};",
            f"  if ({a['name1']} > {a['name2']}) {{",
            f"    print({a['name1']});",
            "  } else {",
            f"    print({a['name2']});",
            "  }",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"var {a['name']} = {a['value']};",
            f"  if ({a['left']} {joiner} {a['right']}) {{",
            f"    print({_q(a['yes'])});",
            "  } else {",
            f"    print({_q(a['no'])});",
            "  }",
        )
    if shape == "while_count":
        return _lines(
            f"var i = {a['lo']};",
            f"  while (i <= {a['hi']}) {{",
            f"    print({a['expr']});",
            "    i++;",
            "  }",
        )
    if shape == "while_sum":
        return _lines(
            f"var i = {a['lo']};",
            "  var total = 0;",
            f"  while (i <= {a['hi']}) {{",
            f"    total += {a['expr']};",
            "    i++;",
            "  }",
            "  print(total);",
        )
    if shape == "list_loop":
        return _lines(
            f"var nums = {_list_literal(a['items'])};",
            "  for (var n in nums) {",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "list_sum":
        return _lines(
            f"var nums = {_list_literal(a['items'])};",
            "  var total = 0;",
            "  for (var n in nums) {",
            "    total += n;",
            "  }",
            "  print(total);",
        )
    if shape == "list_index":
        picks = [f"  print(nums[{i}]);" for i in a["indexes"]]
        return _lines(f"var nums = {_list_literal(a['items'])};", *picks)
    if shape == "list_filter":
        return _lines(
            f"var nums = {_list_literal(a['items'])};",
            "  for (var n in nums) {",
            f"    if ({a['cond']}) {{",
            "      print(n);",
            "    }",
            "  }",
        )
    if shape == "list_build":
        return _lines(
            "var out = [];",
            f"  for (var i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    out.add({a['expr']});",
            "  }",
            "  for (var n in out) {",
            "    print(n);",
            "  }",
        )
    if shape == "list_max":
        return _lines(
            f"var nums = {_list_literal(a['items'])};",
            "  var best = nums[0];",
            "  for (var n in nums) {",
            "    if (n > best) {",
            "      best = n;",
            "    }",
            "  }",
            "  print(best);",
        )
    if shape == "str_length":
        return f"print({_q(a['word'])}.length);"
    if shape == "str_loop":
        return _lines(
            f"for (var c in {_q(a['word'])}.split(\"\")) {{",
            "    print(c);",
            "  }",
        )
    if shape == "str_upper":
        return f"print({_q(a['word'])}.toUpperCase());"
    raise KeyError(shape)


def _dart(shape: str, a: dict) -> str:
    # A function has to live outside main, so these three write the file
    # rather than a body to be wrapped in one.
    if shape == "func_print":
        calls = [f"  {a['name']}();" for _ in range(a["times"])]
        return _lines(
            f"void {a['name']}() {{",
            f"  print({_q(a['text'])});",
            "}",
            "",
            "void main() {",
            *calls,
            "}",
        )
    if shape == "func_arg":
        calls = [f"  {a['name']}({v});" for v in a["calls"]]
        return _lines(
            f"void {a['name']}(int {a['param']}) {{",
            f"  print({a['expr']});",
            "}",
            "",
            "void main() {",
            *calls,
            "}",
        )
    if shape == "func_return":
        calls = [f"  print({a['name']}({v}));" for v in a["calls"]]
        return _lines(
            f"int {a['name']}(int {a['param']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "void main() {",
            *calls,
            "}",
        )
    return "void main() {" + NL + "  " + _dart_body(shape, a) + NL + "}"



# ── TypeScript ───────────────────────────────────────────────
#
# JavaScript with the types written down. Worth its own emitter rather than
# reusing the JS one: the runner type-checks before it runs, so the answers
# have to be properly annotated — and the annotations are the reason to be
# writing TypeScript at all.

def _ts(shape: str, a: dict) -> str:
    tick = chr(96)
    if shape == "say_value":
        return (
            "console.log("
            + tick
            + a["label"]
            + ": ${"
            + a["expr"]
            + "}"
            + tick
            + ");"
        )
    if shape == "repeat_text":
        return _lines(
            f"for (let i = 0; i < {a['count']}; i++) {{",
            f"  console.log({_q(a['text'])});",
            "}",
        )
    if shape == "quoted_text":
        return f"console.log({_q(a['text'])});"
    if shape == "if_print":
        return _lines(
            f"const {a['name']}: number = {a['value']};",
            f"if ({a['cond']}) {{",
            f"  console.log({_q(a['text'])});",
            "}",
        )
    if shape == "if_else_print":
        return _lines(
            f"const {a['name']}: number = {a['value']};",
            f"if ({a['cond']}) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "bigger_print":
        return _lines(
            f"const {a['name1']}: number = {a['value1']};",
            f"const {a['name2']}: number = {a['value2']};",
            f"if ({a['name1']} > {a['name2']}) {{",
            f"  console.log({a['name1']});",
            "} else {",
            f"  console.log({a['name2']});",
            "}",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"const {a['name']}: number = {a['value']};",
            f"if ({a['left']} {joiner} {a['right']}) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "while_count":
        return _lines(
            f"let i: number = {a['lo']};",
            f"while (i <= {a['hi']}) {{",
            f"  console.log({a['expr']});",
            "  i++;",
            "}",
        )
    if shape == "while_sum":
        return _lines(
            f"let i: number = {a['lo']};",
            "let total: number = 0;",
            f"while (i <= {a['hi']}) {{",
            f"  total += {a['expr']};",
            "  i++;",
            "}",
            "console.log(total);",
        )
    if shape == "list_loop":
        return _lines(
            f"const nums: number[] = {_list_literal(a['items'])};",
            "for (const n of nums) {",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "list_sum":
        return _lines(
            f"const nums: number[] = {_list_literal(a['items'])};",
            "let total: number = 0;",
            "for (const n of nums) {",
            "  total += n;",
            "}",
            "console.log(total);",
        )
    if shape == "list_index":
        picks = [f"console.log(nums[{i}]);" for i in a["indexes"]]
        return _lines(
            f"const nums: number[] = {_list_literal(a['items'])};", *picks
        )
    if shape == "list_filter":
        return _lines(
            f"const nums: number[] = {_list_literal(a['items'])};",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            "    console.log(n);",
            "  }",
            "}",
        )
    if shape == "list_build":
        return _lines(
            "const out: number[] = [];",
            f"for (let i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"  out.push({a['expr']});",
            "}",
            "for (const n of out) {",
            "  console.log(n);",
            "}",
        )
    if shape == "list_max":
        return _lines(
            f"const nums: number[] = {_list_literal(a['items'])};",
            "let best: number = nums[0];",
            "for (const n of nums) {",
            "  if (n > best) {",
            "    best = n;",
            "  }",
            "}",
            "console.log(best);",
        )
    if shape == "func_print":
        return _lines(
            f"function {a['name']}(): void {{",
            f"  console.log({_q(a['text'])});",
            "}",
            "",
            *[f"{a['name']}();" for _ in range(a["times"])],
        )
    if shape == "func_arg":
        return _lines(
            f"function {a['name']}({a['param']}: number): void {{",
            f"  console.log({a['expr']});",
            "}",
            "",
            *[f"{a['name']}({v});" for v in a["calls"]],
        )
    if shape == "func_return":
        return _lines(
            f"function {a['name']}({a['param']}: number): number {{",
            f"  return {a['expr']};",
            "}",
            "",
            *[f"console.log({a['name']}({v}));" for v in a["calls"]],
        )
    if shape == "str_length":
        return f"console.log({_q(a['word'])}.length);"
    if shape == "str_loop":
        return _lines(
            f"for (const c of {_q(a['word'])}) {{", "  console.log(c);", "}"
        )
    if shape == "str_upper":
        return f"console.log({_q(a['word'])}.toUpperCase());"
    raise KeyError(shape)


_EMITTERS: dict[str, Callable[[str, dict], str]] = {
    "python": _python,
    "javascript": _js,
    "typescript": _ts,
    "dart": _dart,
}


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def solution(language: str, shape: str, args: dict) -> str | None:
    """The reference program, or None if this language has no workbook.

    C, C++ and Rust live in `emit_more_native` — the shapes are the same
    questions but the answers are a different kind of code, and keeping them
    apart stops either file becoming a wall of near-identical branches.
    """
    emit = _EMITTERS.get(language)
    if emit is not None:
        return emit(shape, args)
    from code_coach.workbook import emit_more_native

    return emit_more_native.solution(language, shape, args)


# ── What each of them prints ─────────────────────────────────
#
# Kept next to the emitters rather than with the others, because these two
# have to agree and the way to keep them agreeing is to change them in the
# same place. The suite runs every reference program in all three languages
# and holds it to what this says.


def expected_output(shape: str, args: dict, value) -> str:
    """`value` is the workbook's expression evaluator, passed in so this does
    not import back into the package that imports it."""
    a = args
    lines: list[str] = []
    if shape == "say_value":
        lines = [f"{a['label']}: {value(a['expr'], {})}"]
    elif shape == "repeat_text":
        lines = [a["text"]] * a["count"]
    elif shape == "quoted_text":
        lines = [a["text"]]
    elif shape == "if_print":
        names = {a["name"]: a["value"]}
        lines = [a["text"]] if value(a["cond"], names) else []
    elif shape == "if_else_print":
        names = {a["name"]: a["value"]}
        lines = [a["yes"] if value(a["cond"], names) else a["no"]]
    elif shape == "bigger_print":
        first, second = a["value1"], a["value2"]
        lines = [str(first if first > second else second)]
    elif shape == "and_or_print":
        names = {a["name"]: a["value"]}
        left, right = value(a["left"], names), value(a["right"], names)
        held = (left and right) if a["op"] == "and" else (left or right)
        lines = [a["yes"] if held else a["no"]]
    elif shape == "while_count":
        lines = [
            str(value(a["expr"], {"i": i}))
            for i in range(a["lo"], a["hi"] + 1)
        ]
    elif shape == "while_sum":
        lines = [
            str(
                sum(
                    value(a["expr"], {"i": i})
                    for i in range(a["lo"], a["hi"] + 1)
                )
            )
        ]
    elif shape == "list_loop":
        lines = [str(value(a["expr"], {"n": n})) for n in a["items"]]
    elif shape == "list_sum":
        lines = [str(sum(a["items"]))]
    elif shape == "list_index":
        lines = [str(a["items"][i]) for i in a["indexes"]]
    elif shape == "list_filter":
        lines = [str(n) for n in a["items"] if value(a["cond"], {"n": n})]
    elif shape == "list_build":
        lines = [
            str(value(a["expr"], {"i": i}))
            for i in range(a["lo"], a["hi"] + 1)
        ]
    elif shape == "list_max":
        lines = [str(max(a["items"]))]
    elif shape == "func_print":
        lines = [a["text"]] * a["times"]
    elif shape in ("func_arg", "func_return"):
        lines = [
            str(value(a["expr"], {a["param"]: v})) for v in a["calls"]
        ]
    elif shape == "str_length":
        lines = [str(len(a["word"]))]
    elif shape == "str_loop":
        lines = list(a["word"])
    elif shape == "str_upper":
        lines = [a["word"].upper()]
    else:
        raise KeyError(shape)
    return NL.join(lines)
