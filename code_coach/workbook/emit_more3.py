"""A fourth batch of shapes: labelling, stepping, tables and two-argument work.

Same rules as the three modules before it. All seven languages side by side,
everything inside what C can do without pretending, and every answer prints
exactly the same characters.

The theme here is the loop body getting a job of its own — a decision that
produces a word, a total that shows its working, a line with three values in
it — rather than the loop itself getting harder.
"""

from __future__ import annotations

from typing import Callable

from code_coach.workbook.emit import NL, Shape, _lines, _q

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
    Shape("label_each", "a word for every item, decided one at a time"),
    Shape("running_total", "showing the total as it grows, not just at the end"),
    Shape("step_loop", "counting in something other than ones"),
    Shape("times_table", "three values in one line of text"),
    Shape("grid_sum", "one total across two loops"),
    Shape("func_two", "a function that takes two values"),
    Shape("func_word", "a function that hands back a word"),
    Shape("char_at", "one character, by its position"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Python ───────────────────────────────────────────────────

def _python(shape: str, a: dict) -> str:
    if shape == "label_each":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "for n in nums:",
            f"    if {a['cond']}:",
            f"        print({_q(a['yes'])})",
            "    else:",
            f"        print({_q(a['no'])})",
        )
    if shape == "running_total":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "total = 0",
            "for n in nums:",
            "    total += n",
            "    print(total)",
        )
    if shape == "step_loop":
        return _lines(
            f"for i in range({a['lo']}, {a['hi']} + 1, {a['step']}):",
            f"    print({a['expr']})",
        )
    if shape == "times_table":
        return _lines(
            f"for i in range(1, {a['upto']} + 1):",
            f'    print(f"{a["n"]} x {{i}} = {{{a["n"]} * i}}")',
        )
    if shape == "grid_sum":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"grid = [{rows}]",
            "total = 0",
            "for row in grid:",
            "    for v in row:",
            "        total += v",
            "print(total)",
        )
    if shape == "func_two":
        calls = [f"print({a['name']}({x}, {y}))" for x, y in a["calls"]]
        return _lines(
            f"def {a['name']}({a['param1']}, {a['param2']}):",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "func_word":
        calls = [f"print({a['name']}({v}))" for v in a["calls"]]
        return _lines(
            f"def {a['name']}({a['param']}):",
            f"    if {a['cond']}:",
            f"        return {_q(a['yes'])}",
            f"    return {_q(a['no'])}",
            "",
            *calls,
        )
    if shape == "char_at":
        return f"print({_q(a['word'])}[{a['index']}])"
    raise KeyError(shape)


# ── JavaScript ───────────────────────────────────────────────

def _js(shape: str, a: dict) -> str:
    tick = chr(96)
    if shape == "label_each":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            f"    console.log({_q(a['yes'])});",
            "  } else {",
            f"    console.log({_q(a['no'])});",
            "  }",
            "}",
        )
    if shape == "running_total":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "let total = 0;",
            "for (const n of nums) {",
            "  total += n;",
            "  console.log(total);",
            "}",
        )
    if shape == "step_loop":
        return _lines(
            f"for (let i = {a['lo']}; i <= {a['hi']}; i += {a['step']}) {{",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "times_table":
        line = (
            "  console.log("
            + tick
            + str(a["n"])
            + " x ${i} = ${"
            + str(a["n"])
            + " * i}"
            + tick
            + ");"
        )
        return _lines(
            f"for (let i = 1; i <= {a['upto']}; i++) {{", line, "}"
        )
    if shape == "grid_sum":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"const grid = [{rows}];",
            "let total = 0;",
            "for (const row of grid) {",
            "  for (const v of row) {",
            "    total += v;",
            "  }",
            "}",
            "console.log(total);",
        )
    if shape == "func_two":
        calls = [
            f"console.log({a['name']}({x}, {y}));" for x, y in a["calls"]
        ]
        return _lines(
            f"function {a['name']}({a['param1']}, {a['param2']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            *calls,
        )
    if shape == "func_word":
        calls = [f"console.log({a['name']}({v}));" for v in a["calls"]]
        return _lines(
            f"function {a['name']}({a['param']}) {{",
            f"  if ({a['cond']}) {{",
            f"    return {_q(a['yes'])};",
            "  }",
            f"  return {_q(a['no'])};",
            "}",
            "",
            *calls,
        )
    if shape == "char_at":
        return f"console.log({_q(a['word'])}[{a['index']}]);"
    raise KeyError(shape)


# ── TypeScript ───────────────────────────────────────────────

def _ts(shape: str, a: dict) -> str:
    tick = chr(96)
    if shape == "label_each":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            f"    console.log({_q(a['yes'])});",
            "  } else {",
            f"    console.log({_q(a['no'])});",
            "  }",
            "}",
        )
    if shape == "running_total":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "let total: number = 0;",
            "for (const n of nums) {",
            "  total += n;",
            "  console.log(total);",
            "}",
        )
    if shape == "step_loop":
        return _lines(
            f"for (let i = {a['lo']}; i <= {a['hi']}; i += {a['step']}) {{",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "times_table":
        line = (
            "  console.log("
            + tick
            + str(a["n"])
            + " x ${i} = ${"
            + str(a["n"])
            + " * i}"
            + tick
            + ");"
        )
        return _lines(
            f"for (let i = 1; i <= {a['upto']}; i++) {{", line, "}"
        )
    if shape == "grid_sum":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"const grid: number[][] = [{rows}];",
            "let total: number = 0;",
            "for (const row of grid) {",
            "  for (const v of row) {",
            "    total += v;",
            "  }",
            "}",
            "console.log(total);",
        )
    if shape == "func_two":
        calls = [
            f"console.log({a['name']}({x}, {y}));" for x, y in a["calls"]
        ]
        return _lines(
            f"function {a['name']}({a['param1']}: number, {a['param2']}: number): number {{",
            f"  return {a['expr']};",
            "}",
            "",
            *calls,
        )
    if shape == "func_word":
        calls = [f"console.log({a['name']}({v}));" for v in a["calls"]]
        return _lines(
            f"function {a['name']}({a['param']}: number): string {{",
            f"  if ({a['cond']}) {{",
            f"    return {_q(a['yes'])};",
            "  }",
            f"  return {_q(a['no'])};",
            "}",
            "",
            *calls,
        )
    if shape == "char_at":
        return f"console.log({_q(a['word'])}[{a['index']}]);"
    raise KeyError(shape)


# ── Dart ─────────────────────────────────────────────────────

def _dart_body(shape: str, a: dict) -> str:
    if shape == "label_each":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  for (var n in nums) {",
            f"    if ({a['cond']}) {{",
            f"      print({_q(a['yes'])});",
            "    } else {",
            f"      print({_q(a['no'])});",
            "    }",
            "  }",
        )
    if shape == "running_total":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  var total = 0;",
            "  for (var n in nums) {",
            "    total += n;",
            "    print(total);",
            "  }",
        )
    if shape == "step_loop":
        return _lines(
            f"for (var i = {a['lo']}; i <= {a['hi']}; i += {a['step']}) {{",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "times_table":
        return _lines(
            f"for (var i = 1; i <= {a['upto']}; i++) {{",
            '    print("' + str(a["n"]) + ' x ${i} = ${' + str(a["n"]) + " * i}\");",
            "  }",
        )
    if shape == "grid_sum":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"var grid = [{rows}];",
            "  var total = 0;",
            "  for (var row in grid) {",
            "    for (var v in row) {",
            "      total += v;",
            "    }",
            "  }",
            "  print(total);",
        )
    if shape == "char_at":
        return f"print({_q(a['word'])}[{a['index']}]);"
    raise KeyError(shape)


def _dart(shape: str, a: dict) -> str:
    if shape == "func_two":
        calls = [f"  print({a['name']}({x}, {y}));" for x, y in a["calls"]]
        return _lines(
            f"int {a['name']}(int {a['param1']}, int {a['param2']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "void main() {",
            *calls,
            "}",
        )
    if shape == "func_word":
        calls = [f"  print({a['name']}({v}));" for v in a["calls"]]
        return _lines(
            f"String {a['name']}(int {a['param']}) {{",
            f"  if ({a['cond']}) {{",
            f"    return {_q(a['yes'])};",
            "  }",
            f"  return {_q(a['no'])};",
            "}",
            "",
            "void main() {",
            *calls,
            "}",
        )
    return "void main() {" + NL + "  " + _dart_body(shape, a) + NL + "}"


# ── C ────────────────────────────────────────────────────────

_C_HEAD = _lines("#include <stdio.h>", "")


def _c_body(shape: str, a: dict) -> str:
    if shape == "label_each":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    int n = nums[k];",
            f"    if ({a['cond']}) {{",
            f'      printf("%s\\n", {_q(a["yes"])});',
            "    } else {",
            f'      printf("%s\\n", {_q(a["no"])});',
            "    }",
            "  }",
        )
    if shape == "running_total":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            "  int total = 0;",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    total += nums[k];",
            '    printf("%d\\n", total);',
            "  }",
        )
    if shape == "step_loop":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i += {a['step']}) {{",
            f'    printf("%d\\n", {a["expr"]});',
            "  }",
        )
    if shape == "times_table":
        n = a["n"]
        return _lines(
            f"for (int i = 1; i <= {a['upto']}; i++) {{",
            f'    printf("%d x %d = %d\\n", {n}, i, {n} * i);',
            "  }",
        )
    if shape == "grid_sum":
        rows = a["rows"]
        body = ", ".join("{" + _ints(r) + "}" for r in rows)
        return _lines(
            f"int grid[{len(rows)}][{len(rows[0])}] = {{{body}}};",
            "  int total = 0;",
            f"  for (int r = 0; r < {len(rows)}; r++) {{",
            f"    for (int c = 0; c < {len(rows[0])}; c++) {{",
            "      total += grid[r][c];",
            "    }",
            "  }",
            '  printf("%d\\n", total);',
        )
    if shape == "char_at":
        return f'printf("%c\\n", {_q(a["word"])}[{a["index"]}]);'
    raise KeyError(shape)


def _c(shape: str, a: dict) -> str:
    if shape == "func_two":
        calls = [
            f'  printf("%d\\n", {a["name"]}({x}, {y}));' for x, y in a["calls"]
        ]
        return _lines(
            _C_HEAD,
            f"int {a['name']}(int {a['param1']}, int {a['param2']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_word":
        calls = [
            f'  printf("%s\\n", {a["name"]}({v}));' for v in a["calls"]
        ]
        return _lines(
            _C_HEAD,
            f"const char *{a['name']}(int {a['param']}) {{",
            f"  if ({a['cond']}) {{",
            f"    return {_q(a['yes'])};",
            "  }",
            f"  return {_q(a['no'])};",
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
        )
    return _lines(
        _C_HEAD, "int main(void) {", "  " + _c_body(shape, a), "  return 0;", "}"
    )


# ── C++ ──────────────────────────────────────────────────────

_CPP_HEAD = _lines("#include <iostream>", "#include <string>", "#include <vector>", "")


def _cpp_body(shape: str, a: dict) -> str:
    if shape == "label_each":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  for (int n : nums) {",
            f"    if ({a['cond']}) {{",
            f'      std::cout << {_q(a["yes"])} << "\\n";',
            "    } else {",
            f'      std::cout << {_q(a["no"])} << "\\n";',
            "    }",
            "  }",
        )
    if shape == "running_total":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  int total = 0;",
            "  for (int n : nums) {",
            "    total += n;",
            '    std::cout << total << "\\n";',
            "  }",
        )
    if shape == "step_loop":
        return _lines(
            f"for (int i = {a['lo']}; i <= {a['hi']}; i += {a['step']}) {{",
            f'    std::cout << {a["expr"]} << "\\n";',
            "  }",
        )
    if shape == "times_table":
        n = a["n"]
        return _lines(
            f"for (int i = 1; i <= {a['upto']}; i++) {{",
            f'    std::cout << {n} << " x " << i << " = " << ({n} * i) << "\\n";',
            "  }",
        )
    if shape == "grid_sum":
        rows = ", ".join("{" + _ints(r) + "}" for r in a["rows"])
        return _lines(
            f"std::vector<std::vector<int>> grid = {{{rows}}};",
            "  int total = 0;",
            "  for (const auto &row : grid) {",
            "    for (int v : row) {",
            "      total += v;",
            "    }",
            "  }",
            '  std::cout << total << "\\n";',
        )
    if shape == "char_at":
        return (
            f"std::string w = {_q(a['word'])};" + NL
            + f'  std::cout << w[{a["index"]}] << "\\n";'
        )
    raise KeyError(shape)


def _cpp(shape: str, a: dict) -> str:
    if shape == "func_two":
        calls = [
            f'  std::cout << {a["name"]}({x}, {y}) << "\\n";'
            for x, y in a["calls"]
        ]
        return _lines(
            _CPP_HEAD,
            f"int {a['name']}(int {a['param1']}, int {a['param2']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "int main() {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_word":
        calls = [
            f'  std::cout << {a["name"]}({v}) << "\\n";' for v in a["calls"]
        ]
        return _lines(
            _CPP_HEAD,
            f"std::string {a['name']}(int {a['param']}) {{",
            f"  if ({a['cond']}) {{",
            f"    return {_q(a['yes'])};",
            "  }",
            f"  return {_q(a['no'])};",
            "}",
            "",
            "int main() {",
            *calls,
            "  return 0;",
            "}",
        )
    return _lines(
        _CPP_HEAD, "int main() {", "  " + _cpp_body(shape, a), "  return 0;", "}"
    )


# ── Rust ─────────────────────────────────────────────────────

def _rust_body(shape: str, a: dict) -> str:
    if shape == "label_each":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    for n in nums {",
            f"        if {a['cond']} {{",
            f'            println!("{{}}", {_q(a["yes"])});',
            "        } else {",
            f'            println!("{{}}", {_q(a["no"])});',
            "        }",
            "    }",
        )
    if shape == "running_total":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    let mut total = 0;",
            "    for n in nums {",
            "        total += n;",
            '        println!("{}", total);',
            "    }",
        )
    if shape == "step_loop":
        return _lines(
            f"for i in ({a['lo']}..={a['hi']}).step_by({a['step']}) {{",
            f'        println!("{{}}", {a["expr"]});',
            "    }",
        )
    if shape == "times_table":
        n = a["n"]
        return _lines(
            f"for i in 1..={a['upto']} {{",
            f'        println!("{{}} x {{}} = {{}}", {n}, i, {n} * i);',
            "    }",
        )
    if shape == "grid_sum":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"let grid = [{rows}];",
            "    let mut total = 0;",
            "    for row in grid {",
            "        for v in row {",
            "            total += v;",
            "        }",
            "    }",
            '    println!("{}", total);',
        )
    if shape == "char_at":
        return (
            f'println!("{{}}", {_q(a["word"])}'
            + f".chars().nth({a['index']}).unwrap());"
        )
    raise KeyError(shape)


def _rust(shape: str, a: dict) -> str:
    if shape == "func_two":
        calls = [
            f'    println!("{{}}", {a["name"]}({x}, {y}));'
            for x, y in a["calls"]
        ]
        return _lines(
            f"fn {a['name']}({a['param1']}: i32, {a['param2']}: i32) -> i32 {{",
            f"    {a['expr']}",
            "}",
            "",
            "fn main() {",
            *calls,
            "}",
        )
    if shape == "func_word":
        calls = [
            f'    println!("{{}}", {a["name"]}({v}));' for v in a["calls"]
        ]
        return _lines(
            f"fn {a['name']}({a['param']}: i32) -> &'static str {{",
            f"    if {a['cond']} {{",
            f"        return {_q(a['yes'])};",
            "    }",
            f"    {_q(a['no'])}",
            "}",
            "",
            "fn main() {",
            *calls,
            "}",
        )
    return "fn main() {" + NL + "    " + _rust_body(shape, a) + NL + "}"


_EMITTERS: dict[str, Callable[[str, dict], str]] = {
    "python": _python,
    "javascript": _js,
    "typescript": _ts,
    "dart": _dart,
    "c": _c,
    "cpp": _cpp,
    "rust": _rust,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    emit = _EMITTERS.get(language)
    if emit is None:
        return None
    return emit(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "label_each":
        lines = [
            a["yes"] if value(a["cond"], {"n": n}) else a["no"]
            for n in a["items"]
        ]
    elif shape == "running_total":
        total = 0
        for n in a["items"]:
            total += n
            lines.append(str(total))
    elif shape == "step_loop":
        lines = [
            str(value(a["expr"], {"i": i}))
            for i in range(a["lo"], a["hi"] + 1, a["step"])
        ]
    elif shape == "times_table":
        n = a["n"]
        lines = [f"{n} x {i} = {n * i}" for i in range(1, a["upto"] + 1)]
    elif shape == "grid_sum":
        lines = [str(sum(v for row in a["rows"] for v in row))]
    elif shape == "func_two":
        lines = [
            str(value(a["expr"], {a["param1"]: x, a["param2"]: y}))
            for x, y in a["calls"]
        ]
    elif shape == "func_word":
        lines = [
            a["yes"] if value(a["cond"], {a["param"]: v}) else a["no"]
            for v in a["calls"]
        ]
    elif shape == "char_at":
        lines = [a["word"][a["index"]]]
    else:
        raise KeyError(shape)
    return NL.join(lines)
