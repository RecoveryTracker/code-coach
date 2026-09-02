"""Reference solutions, built per language from a small set of shapes.

An exercise says what the program must print and nothing about how, because
that part is the same question in every language. The answer is not: printing
a number is one line in Python and four in C.

So an exercise carries a *shape* — "loop from a to b printing this" — and each
language knows how to write each shape. Ten shapes, seven languages, and
every exercise on a page is the same shape with different numbers. That is
what makes a page of them cheap to write and repetitive to work through,
which is the whole point of a workbook page.

The shapes are deliberately few. An eleventh shape is a new thing to learn; a
hundredth exercise in an existing shape is practice.

Expressions are passed through as text (`i * 2`, `i % 3 == 0`). Infix
arithmetic and comparison happen to be spelled identically in all seven, so
the exercise can hold the expression and stay language-agnostic. Anything
where they differ — integer division, string building — belongs in a shape
rather than in an expression.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# Languages the workbook runs in. SQL is left out on purpose: it has no
# statement that prints a line and no loop, so every shape here would have to
# be faked, and a faked exercise teaches the fake.
LANGUAGES: tuple[str, ...] = (
    "python",
    "javascript",
    "typescript",
    "dart",
    "c",
    "cpp",
    "rust",
)

NL = "\n"


@dataclass(frozen=True)
class Shape:
    """One program skeleton, named, with the arguments it takes."""

    id: str
    # What the student is being asked to do, for the page header.
    teaches: str


SHAPES: tuple[Shape, ...] = (
    Shape("print_text", "putting a line of text on the screen"),
    Shape("print_expr", "evaluating an expression and printing the result"),
    Shape("let_print", "holding a value in a variable, then printing it"),
    Shape("let2_print", "combining two variables into a result"),
    Shape("for_print", "a loop that runs a fixed number of times"),
    Shape("for_range_print", "a loop over a range you choose"),
    Shape("for_sum", "carrying a running total through a loop"),
    Shape("for_if_print", "a decision inside a loop"),
    Shape("for_down", "a loop that counts backwards"),
    Shape("for_nested", "a loop inside a loop"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def _q(text: str) -> str:
    """A double-quoted literal, safe for every language here."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _lines(*parts: str) -> str:
    return NL.join(parts)


# ── Python ───────────────────────────────────────────────────

def _python(shape: str, a: dict) -> str:
    if shape == "print_text":
        return f"print({_q(a['text'])})"
    if shape == "print_expr":
        return f"print({a['expr']})"
    if shape == "let_print":
        return _lines(f"{a['name']} = {a['value']}", f"print({a['expr']})")
    if shape == "let2_print":
        return _lines(
            f"{a['name1']} = {a['value1']}",
            f"{a['name2']} = {a['value2']}",
            f"print({a['expr']})",
        )
    if shape == "for_print":
        return _lines(
            f"for i in range({a['count']}):", f"    print({a['expr']})"
        )
    if shape == "for_range_print":
        return _lines(
            f"for i in range({a['lo']}, {a['hi']} + 1):",
            f"    print({a['expr']})",
        )
    if shape == "for_sum":
        return _lines(
            "total = 0",
            f"for i in range({a['lo']}, {a['hi']} + 1):",
            f"    total += {a['expr']}",
            "print(total)",
        )
    if shape == "for_if_print":
        return _lines(
            f"for i in range({a['lo']}, {a['hi']} + 1):",
            f"    if {a['cond']}:",
            f"        print({a['expr']})",
        )
    if shape == "for_down":
        return _lines(
            f"for i in range({a['hi']}, {a['lo']} - 1, -1):",
            f"    print({a['expr']})",
        )
    if shape == "for_nested":
        return _lines(
            f"for i in range(1, {a['rows']} + 1):",
            f"    for j in range(1, {a['cols']} + 1):",
            f"        print({a['expr']})",
        )
    raise KeyError(shape)


# ── JavaScript and TypeScript ────────────────────────────────

def _js(shape: str, a: dict) -> str:
    if shape == "print_text":
        return f"console.log({_q(a['text'])});"
    if shape == "print_expr":
        return f"console.log({a['expr']});"
    if shape == "let_print":
        return _lines(
            f"const {a['name']} = {a['value']};", f"console.log({a['expr']});"
        )
    if shape == "let2_print":
        return _lines(
            f"const {a['name1']} = {a['value1']};",
            f"const {a['name2']} = {a['value2']};",
            f"console.log({a['expr']});",
        )
    if shape == "for_print":
        return _lines(
            f"for (let i = 0; i < {a['count']}; i++) {{",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "for_range_print":
        return _lines(
            f"for (let i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "for_sum":
        return _lines(
            "let total = 0;",
            f"for (let i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"  total += {a['expr']};",
            "}",
            "console.log(total);",
        )
    if shape == "for_if_print":
        return _lines(
            f"for (let i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"  if ({a['cond']}) {{",
            f"    console.log({a['expr']});",
            "  }",
            "}",
        )
    if shape == "for_down":
        return _lines(
            f"for (let i = {a['hi']}; i >= {a['lo']}; i--) {{",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "for_nested":
        return _lines(
            f"for (let i = 1; i <= {a['rows']}; i++) {{",
            f"  for (let j = 1; j <= {a['cols']}; j++) {{",
            f"    console.log({a['expr']});",
            "  }",
            "}",
        )
    raise KeyError(shape)


# ── Dart ─────────────────────────────────────────────────────

def _dart_body(shape: str, a: dict) -> str:
    if shape == "print_text":
        return f"print({_q(a['text'])});"
    if shape == "print_expr":
        return f"print({a['expr']});"
    if shape == "let_print":
        return _lines(
            f"var {a['name']} = {a['value']};", f"  print({a['expr']});"
        )
    if shape == "let2_print":
        return _lines(
            f"var {a['name1']} = {a['value1']};",
            f"  var {a['name2']} = {a['value2']};",
            f"  print({a['expr']});",
        )
    if shape == "for_print":
        return _lines(
            f"for (var i = 0; i < {a['count']}; i++) {{",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "for_range_print":
        return _lines(
            f"for (var i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "for_sum":
        return _lines(
            "var total = 0;",
            f"  for (var i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    total += {a['expr']};",
            "  }",
            "  print(total);",
        )
    if shape == "for_if_print":
        return _lines(
            f"for (var i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    if ({a['cond']}) {{",
            f"      print({a['expr']});",
            "    }",
            "  }",
        )
    if shape == "for_down":
        return _lines(
            f"for (var i = {a['hi']}; i >= {a['lo']}; i--) {{",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "for_nested":
        return _lines(
            f"for (var i = 1; i <= {a['rows']}; i++) {{",
            f"    for (var j = 1; j <= {a['cols']}; j++) {{",
            f"      print({a['expr']});",
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _dart(shape: str, a: dict) -> str:
    return "void main() {" + NL + "  " + _dart_body(shape, a) + NL + "}"


# ── C ────────────────────────────────────────────────────────

def _printf(expr: str) -> str:
    return 'printf("%d\\n", ' + expr + ");"


def _c_body(shape: str, a: dict) -> str:
    if shape == "print_text":
        return 'printf("%s\\n", ' + _q(a["text"]) + ");"
    if shape == "print_expr":
        return _printf(a["expr"])
    if shape == "let_print":
        return _lines(
            f"int {a['name']} = {a['value']};", "  " + _printf(a["expr"])
        )
    if shape == "let2_print":
        return _lines(
            f"int {a['name1']} = {a['value1']};",
            f"  int {a['name2']} = {a['value2']};",
            "  " + _printf(a["expr"]),
        )
    if shape == "for_print":
        return _lines(
            f"for (int i = 0; i < {a['count']}; i++) {{",
            "    " + _printf(a["expr"]),
            "  }",
        )
    if shape == "for_range_print":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            "    " + _printf(a["expr"]),
            "  }",
        )
    if shape == "for_sum":
        return _lines(
            "int total = 0;",
            f"  for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    total += {a['expr']};",
            "  }",
            "  " + _printf("total"),
        )
    if shape == "for_if_print":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    if ({a['cond']}) {{",
            "      " + _printf(a["expr"]),
            "    }",
            "  }",
        )
    if shape == "for_down":
        return _lines(
            f"for (int i = {a['hi']}; i >= {a['lo']}; i--) {{",
            "    " + _printf(a["expr"]),
            "  }",
        )
    if shape == "for_nested":
        return _lines(
            f"for (int i = 1; i <= {a['rows']}; i++) {{",
            f"    for (int j = 1; j <= {a['cols']}; j++) {{",
            "      " + _printf(a["expr"]),
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _c(shape: str, a: dict) -> str:
    return (
        "#include <stdio.h>"
        + NL
        + NL
        + "int main(void) {"
        + NL
        + "  "
        + _c_body(shape, a)
        + NL
        + "  return 0;"
        + NL
        + "}"
    )


# ── C++ ──────────────────────────────────────────────────────

def _cout(expr: str) -> str:
    return "std::cout << " + expr + ' << "\\n";'


def _cpp_body(shape: str, a: dict) -> str:
    if shape == "print_text":
        return _cout(_q(a["text"]))
    if shape == "print_expr":
        return _cout(a["expr"])
    if shape == "let_print":
        return _lines(
            f"int {a['name']} = {a['value']};", "  " + _cout(a["expr"])
        )
    if shape == "let2_print":
        return _lines(
            f"int {a['name1']} = {a['value1']};",
            f"  int {a['name2']} = {a['value2']};",
            "  " + _cout(a["expr"]),
        )
    if shape == "for_print":
        return _lines(
            f"for (int i = 0; i < {a['count']}; i++) {{",
            "    " + _cout(a["expr"]),
            "  }",
        )
    if shape == "for_range_print":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            "    " + _cout(a["expr"]),
            "  }",
        )
    if shape == "for_sum":
        return _lines(
            "int total = 0;",
            f"  for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    total += {a['expr']};",
            "  }",
            "  " + _cout("total"),
        )
    if shape == "for_if_print":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    if ({a['cond']}) {{",
            "      " + _cout(a["expr"]),
            "    }",
            "  }",
        )
    if shape == "for_down":
        return _lines(
            f"for (int i = {a['hi']}; i >= {a['lo']}; i--) {{",
            "    " + _cout(a["expr"]),
            "  }",
        )
    if shape == "for_nested":
        return _lines(
            f"for (int i = 1; i <= {a['rows']}; i++) {{",
            f"    for (int j = 1; j <= {a['cols']}; j++) {{",
            "      " + _cout(a["expr"]),
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _cpp(shape: str, a: dict) -> str:
    return (
        "#include <iostream>"
        + NL
        + NL
        + "int main() {"
        + NL
        + "  "
        + _cpp_body(shape, a)
        + NL
        + "  return 0;"
        + NL
        + "}"
    )


# ── Rust ─────────────────────────────────────────────────────

def _println(expr: str) -> str:
    return 'println!("{}", ' + expr + ");"


def _rust_body(shape: str, a: dict) -> str:
    if shape == "print_text":
        return _println(_q(a["text"]))
    if shape == "print_expr":
        return _println(a["expr"])
    if shape == "let_print":
        return _lines(
            f"let {a['name']} = {a['value']};", "    " + _println(a["expr"])
        )
    if shape == "let2_print":
        return _lines(
            f"let {a['name1']} = {a['value1']};",
            f"    let {a['name2']} = {a['value2']};",
            "    " + _println(a["expr"]),
        )
    if shape == "for_print":
        return _lines(
            f"for i in 0..{a['count']} {{",
            "        " + _println(a["expr"]),
            "    }",
        )
    if shape == "for_range_print":
        return _lines(
            f"for i in {a['lo']}..={a['hi']} {{",
            "        " + _println(a["expr"]),
            "    }",
        )
    if shape == "for_sum":
        return _lines(
            "let mut total = 0;",
            f"    for i in {a['lo']}..={a['hi']} {{",
            f"        total += {a['expr']};",
            "    }",
            "    " + _println("total"),
        )
    if shape == "for_if_print":
        return _lines(
            f"for i in {a['lo']}..={a['hi']} {{",
            f"        if {a['cond']} {{",
            "            " + _println(a["expr"]),
            "        }",
            "    }",
        )
    if shape == "for_down":
        return _lines(
            f"for i in ({a['lo']}..={a['hi']}).rev() {{",
            "        " + _println(a["expr"]),
            "    }",
        )
    if shape == "for_nested":
        return _lines(
            f"for i in 1..={a['rows']} {{",
            f"        for j in 1..={a['cols']} {{",
            "            " + _println(a["expr"]),
            "        }",
            "    }",
        )
    raise KeyError(shape)


def _rust(shape: str, a: dict) -> str:
    return "fn main() {" + NL + "    " + _rust_body(shape, a) + NL + "}"


_EMITTERS: dict[str, Callable[[str, dict], str]] = {
    "python": _python,
    "javascript": _js,
    "typescript": _js,
    "dart": _dart,
    "c": _c,
    "cpp": _cpp,
    "rust": _rust,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    """The reference program for one exercise, or None when this language
    does not have one.

    The later shapes live in `emit_more` and only exist in three languages;
    everything asks here regardless, so nothing else has to know where a
    given shape is written.
    """
    from code_coach.workbook import (
        emit_more,
        emit_more2,
        emit_more3,
        emit_more4,
        emit_python,
    )

    if emit_python.handles(shape):
        return emit_python.solution(language, shape, args)
    if emit_more4.handles(shape):
        return emit_more4.solution(language, shape, args)
    if emit_more3.handles(shape):
        return emit_more3.solution(language, shape, args)
    if emit_more2.handles(shape):
        return emit_more2.solution(language, shape, args)
    if emit_more.handles(shape):
        return emit_more.solution(language, shape, args)
    emit = _EMITTERS.get(language)
    if emit is None:
        return None
    return emit(shape, args)


def supports(language: str) -> bool:
    """Whether the workbook runs in this language at all."""
    return language in _EMITTERS


def all_shape_ids() -> tuple[str, ...]:
    from code_coach.workbook import (
        emit_more,
        emit_more2,
        emit_more3,
        emit_more4,
        emit_python,
    )

    return (
        SHAPE_IDS
        + emit_more.SHAPE_IDS
        + emit_more2.SHAPE_IDS
        + emit_more3.SHAPE_IDS
        + emit_more4.SHAPE_IDS
        + emit_python.SHAPE_IDS
    )
