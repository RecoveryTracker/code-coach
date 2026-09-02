"""A third batch of shapes: pairs, grids, searching and ordering.

Same rules as the two modules before it — an exercise carries a shape and its
numbers, each language answers it the way that language really would, and
every answer must print exactly the same characters.

All seven languages are here in one file rather than split by family. The
split in `emit_more` / `emit_more_native` happened because those shapes were
written months apart for different sets of languages; these were written for
seven from the start, and keeping each shape's seven answers side by side is
what makes it easy to see that they agree.

Everything here stays inside what C can do honestly: fixed arrays with a
count beside them, and no growing. Splitting a sentence and looking things up
by key come later, on pages that name the languages with those types.
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
    Shape("join_words", "sticking two pieces of text together"),
    Shape("swap_print", "exchanging what two variables hold"),
    Shape("count_matches", "counting how many qualify, rather than showing them"),
    Shape("two_lists", "walking two lists in step"),
    Shape("grid_print", "a list of lists, and the two loops it needs"),
    Shape("list_min", "carrying the smallest so far"),
    Shape("list_reverse", "walking a list from the back"),
    Shape("find_index", "stopping as soon as you have found it"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Python ───────────────────────────────────────────────────

def _python(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"first = {_q(a['word1'])}",
            f"second = {_q(a['word2'])}",
            'print(first + " " + second)',
        )
    if shape == "swap_print":
        return _lines(
            f"a = {a['value1']}",
            f"b = {a['value2']}",
            "a, b = b, a",
            "print(a)",
            "print(b)",
        )
    if shape == "count_matches":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "found = 0",
            "for n in nums:",
            f"    if {a['cond']}:",
            "        found += 1",
            "print(found)",
        )
    if shape == "two_lists":
        return _lines(
            f"xs = [{_ints(a['xs'])}]",
            f"ys = [{_ints(a['ys'])}]",
            "for k in range(len(xs)):",
            "    x = xs[k]",
            "    y = ys[k]",
            f"    print({a['expr']})",
        )
    if shape == "grid_print":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"grid = [{rows}]",
            "for row in grid:",
            "    for v in row:",
            f"        print({a['expr']})",
        )
    if shape == "list_min":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "best = nums[0]",
            "for n in nums:",
            "    if n < best:",
            "        best = n",
            "print(best)",
        )
    if shape == "list_reverse":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "for k in range(len(nums) - 1, -1, -1):",
            "    print(nums[k])",
        )
    if shape == "find_index":
        return _lines(
            f"nums = [{_ints(a['items'])}]",
            "for k in range(len(nums)):",
            f"    if nums[k] == {a['target']}:",
            "        print(k)",
            "        break",
        )
    raise KeyError(shape)


# ── JavaScript ───────────────────────────────────────────────

def _js(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"const first = {_q(a['word1'])};",
            f"const second = {_q(a['word2'])};",
            'console.log(first + " " + second);',
        )
    if shape == "swap_print":
        return _lines(
            f"let a = {a['value1']};",
            f"let b = {a['value2']};",
            "const t = a;",
            "a = b;",
            "b = t;",
            "console.log(a);",
            "console.log(b);",
        )
    if shape == "count_matches":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "let found = 0;",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            "    found++;",
            "  }",
            "}",
            "console.log(found);",
        )
    if shape == "two_lists":
        return _lines(
            f"const xs = [{_ints(a['xs'])}];",
            f"const ys = [{_ints(a['ys'])}];",
            "for (let k = 0; k < xs.length; k++) {",
            "  const x = xs[k];",
            "  const y = ys[k];",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "grid_print":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"const grid = [{rows}];",
            "for (const row of grid) {",
            "  for (const v of row) {",
            f"    console.log({a['expr']});",
            "  }",
            "}",
        )
    if shape == "list_min":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "let best = nums[0];",
            "for (const n of nums) {",
            "  if (n < best) {",
            "    best = n;",
            "  }",
            "}",
            "console.log(best);",
        )
    if shape == "list_reverse":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "for (let k = nums.length - 1; k >= 0; k--) {",
            "  console.log(nums[k]);",
            "}",
        )
    if shape == "find_index":
        return _lines(
            f"const nums = [{_ints(a['items'])}];",
            "for (let k = 0; k < nums.length; k++) {",
            f"  if (nums[k] === {a['target']}) {{",
            "    console.log(k);",
            "    break;",
            "  }",
            "}",
        )
    raise KeyError(shape)


# ── TypeScript ───────────────────────────────────────────────

def _ts(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"const first: string = {_q(a['word1'])};",
            f"const second: string = {_q(a['word2'])};",
            'console.log(first + " " + second);',
        )
    if shape == "swap_print":
        return _lines(
            f"let a: number = {a['value1']};",
            f"let b: number = {a['value2']};",
            "const t: number = a;",
            "a = b;",
            "b = t;",
            "console.log(a);",
            "console.log(b);",
        )
    if shape == "count_matches":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "let found: number = 0;",
            "for (const n of nums) {",
            f"  if ({a['cond']}) {{",
            "    found++;",
            "  }",
            "}",
            "console.log(found);",
        )
    if shape == "two_lists":
        return _lines(
            f"const xs: number[] = [{_ints(a['xs'])}];",
            f"const ys: number[] = [{_ints(a['ys'])}];",
            "for (let k = 0; k < xs.length; k++) {",
            "  const x: number = xs[k];",
            "  const y: number = ys[k];",
            f"  console.log({a['expr']});",
            "}",
        )
    if shape == "grid_print":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"const grid: number[][] = [{rows}];",
            "for (const row of grid) {",
            "  for (const v of row) {",
            f"    console.log({a['expr']});",
            "  }",
            "}",
        )
    if shape == "list_min":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "let best: number = nums[0];",
            "for (const n of nums) {",
            "  if (n < best) {",
            "    best = n;",
            "  }",
            "}",
            "console.log(best);",
        )
    if shape == "list_reverse":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "for (let k = nums.length - 1; k >= 0; k--) {",
            "  console.log(nums[k]);",
            "}",
        )
    if shape == "find_index":
        return _lines(
            f"const nums: number[] = [{_ints(a['items'])}];",
            "for (let k = 0; k < nums.length; k++) {",
            f"  if (nums[k] === {a['target']}) {{",
            "    console.log(k);",
            "    break;",
            "  }",
            "}",
        )
    raise KeyError(shape)


# ── Dart ─────────────────────────────────────────────────────

def _dart_body(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"var first = {_q(a['word1'])};",
            f"  var second = {_q(a['word2'])};",
            '  print(first + " " + second);',
        )
    if shape == "swap_print":
        return _lines(
            f"var a = {a['value1']};",
            f"  var b = {a['value2']};",
            "  var t = a;",
            "  a = b;",
            "  b = t;",
            "  print(a);",
            "  print(b);",
        )
    if shape == "count_matches":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  var found = 0;",
            "  for (var n in nums) {",
            f"    if ({a['cond']}) {{",
            "      found++;",
            "    }",
            "  }",
            "  print(found);",
        )
    if shape == "two_lists":
        return _lines(
            f"var xs = [{_ints(a['xs'])}];",
            f"  var ys = [{_ints(a['ys'])}];",
            "  for (var k = 0; k < xs.length; k++) {",
            "    var x = xs[k];",
            "    var y = ys[k];",
            f"    print({a['expr']});",
            "  }",
        )
    if shape == "grid_print":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"var grid = [{rows}];",
            "  for (var row in grid) {",
            "    for (var v in row) {",
            f"      print({a['expr']});",
            "    }",
            "  }",
        )
    if shape == "list_min":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  var best = nums[0];",
            "  for (var n in nums) {",
            "    if (n < best) {",
            "      best = n;",
            "    }",
            "  }",
            "  print(best);",
        )
    if shape == "list_reverse":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  for (var k = nums.length - 1; k >= 0; k--) {",
            "    print(nums[k]);",
            "  }",
        )
    if shape == "find_index":
        return _lines(
            f"var nums = [{_ints(a['items'])}];",
            "  for (var k = 0; k < nums.length; k++) {",
            f"    if (nums[k] == {a['target']}) {{",
            "      print(k);",
            "      break;",
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _dart(shape: str, a: dict) -> str:
    return "void main() {" + NL + "  " + _dart_body(shape, a) + NL + "}"


# ── C ────────────────────────────────────────────────────────

_C_HEAD = _lines("#include <stdio.h>", "#include <string.h>", "")


def _c_body(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"const char *first = {_q(a['word1'])};",
            f"  const char *second = {_q(a['word2'])};",
            '  printf("%s %s\\n", first, second);',
        )
    if shape == "swap_print":
        return _lines(
            f"int a = {a['value1']};",
            f"  int b = {a['value2']};",
            "  int t = a;",
            "  a = b;",
            "  b = t;",
            '  printf("%d\\n", a);',
            '  printf("%d\\n", b);',
        )
    if shape == "count_matches":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            "  int found = 0;",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    int n = nums[k];",
            f"    if ({a['cond']}) {{",
            "      found++;",
            "    }",
            "  }",
            '  printf("%d\\n", found);',
        )
    if shape == "two_lists":
        return _lines(
            f"int xs[] = {{{_ints(a['xs'])}}};",
            f"  int ys[] = {{{_ints(a['ys'])}}};",
            f"  for (int k = 0; k < {len(a['xs'])}; k++) {{",
            "    int x = xs[k];",
            "    int y = ys[k];",
            f'    printf("%d\\n", {a["expr"]});',
            "  }",
        )
    if shape == "grid_print":
        rows = a["rows"]
        body = ", ".join("{" + _ints(r) + "}" for r in rows)
        return _lines(
            f"int grid[{len(rows)}][{len(rows[0])}] = {{{body}}};",
            f"  for (int r = 0; r < {len(rows)}; r++) {{",
            f"    for (int c = 0; c < {len(rows[0])}; c++) {{",
            "      int v = grid[r][c];",
            f'      printf("%d\\n", {a["expr"]});',
            "    }",
            "  }",
        )
    if shape == "list_min":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            "  int best = nums[0];",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    if (nums[k] < best) {",
            "      best = nums[k];",
            "    }",
            "  }",
            '  printf("%d\\n", best);',
        )
    if shape == "list_reverse":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            f"  for (int k = {len(a['items'])} - 1; k >= 0; k--) {{",
            '    printf("%d\\n", nums[k]);',
            "  }",
        )
    if shape == "find_index":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            f"    if (nums[k] == {a['target']}) {{",
            '      printf("%d\\n", k);',
            "      break;",
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _c(shape: str, a: dict) -> str:
    return _lines(
        _C_HEAD, "int main(void) {", "  " + _c_body(shape, a), "  return 0;", "}"
    )


# ── C++ ──────────────────────────────────────────────────────

_CPP_HEAD = _lines("#include <iostream>", "#include <string>", "#include <vector>", "")


def _cpp_body(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"std::string first = {_q(a['word1'])};",
            f"  std::string second = {_q(a['word2'])};",
            '  std::cout << first + " " + second << "\\n";',
        )
    if shape == "swap_print":
        return _lines(
            f"int a = {a['value1']};",
            f"  int b = {a['value2']};",
            "  int t = a;",
            "  a = b;",
            "  b = t;",
            '  std::cout << a << "\\n";',
            '  std::cout << b << "\\n";',
        )
    if shape == "count_matches":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  int found = 0;",
            "  for (int n : nums) {",
            f"    if ({a['cond']}) {{",
            "      found++;",
            "    }",
            "  }",
            '  std::cout << found << "\\n";',
        )
    if shape == "two_lists":
        return _lines(
            f"std::vector<int> xs = {{{_ints(a['xs'])}}};",
            f"  std::vector<int> ys = {{{_ints(a['ys'])}}};",
            "  for (size_t k = 0; k < xs.size(); k++) {",
            "    int x = xs[k];",
            "    int y = ys[k];",
            f'    std::cout << {a["expr"]} << "\\n";',
            "  }",
        )
    if shape == "grid_print":
        rows = ", ".join("{" + _ints(r) + "}" for r in a["rows"])
        return _lines(
            f"std::vector<std::vector<int>> grid = {{{rows}}};",
            "  for (const auto &row : grid) {",
            "    for (int v : row) {",
            f'      std::cout << {a["expr"]} << "\\n";',
            "    }",
            "  }",
        )
    if shape == "list_min":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  int best = nums[0];",
            "  for (int n : nums) {",
            "    if (n < best) {",
            "      best = n;",
            "    }",
            "  }",
            '  std::cout << best << "\\n";',
        )
    if shape == "list_reverse":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  for (int k = (int)nums.size() - 1; k >= 0; k--) {",
            '    std::cout << nums[k] << "\\n";',
            "  }",
        )
    if shape == "find_index":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  for (size_t k = 0; k < nums.size(); k++) {",
            f"    if (nums[k] == {a['target']}) {{",
            '      std::cout << k << "\\n";',
            "      break;",
            "    }",
            "  }",
        )
    raise KeyError(shape)


def _cpp(shape: str, a: dict) -> str:
    return _lines(
        _CPP_HEAD, "int main() {", "  " + _cpp_body(shape, a), "  return 0;", "}"
    )


# ── Rust ─────────────────────────────────────────────────────

def _rust_body(shape: str, a: dict) -> str:
    if shape == "join_words":
        return _lines(
            f"let first = {_q(a['word1'])};",
            f"    let second = {_q(a['word2'])};",
            '    println!("{} {}", first, second);',
        )
    if shape == "swap_print":
        return _lines(
            f"let mut a = {a['value1']};",
            f"    let mut b = {a['value2']};",
            "    let t = a;",
            "    a = b;",
            "    b = t;",
            '    println!("{}", a);',
            '    println!("{}", b);',
        )
    if shape == "count_matches":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    let mut found = 0;",
            "    for n in nums {",
            f"        if {a['cond']} {{",
            "            found += 1;",
            "        }",
            "    }",
            '    println!("{}", found);',
        )
    if shape == "two_lists":
        return _lines(
            f"let xs = [{_ints(a['xs'])}];",
            f"    let ys = [{_ints(a['ys'])}];",
            "    for k in 0..xs.len() {",
            "        let x = xs[k];",
            "        let y = ys[k];",
            f'        println!("{{}}", {a["expr"]});',
            "    }",
        )
    if shape == "grid_print":
        rows = ", ".join("[" + _ints(r) + "]" for r in a["rows"])
        return _lines(
            f"let grid = [{rows}];",
            "    for row in grid {",
            "        for v in row {",
            f'            println!("{{}}", {a["expr"]});',
            "        }",
            "    }",
        )
    if shape == "list_min":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    let mut best = nums[0];",
            "    for n in nums {",
            "        if n < best {",
            "            best = n;",
            "        }",
            "    }",
            '    println!("{}", best);',
        )
    if shape == "list_reverse":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    for k in (0..nums.len()).rev() {",
            '        println!("{}", nums[k]);',
            "    }",
        )
    if shape == "find_index":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    for k in 0..nums.len() {",
            f"        if nums[k] == {a['target']} {{",
            '            println!("{}", k);',
            "            break;",
            "        }",
            "    }",
        )
    raise KeyError(shape)


def _rust(shape: str, a: dict) -> str:
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
    if shape == "join_words":
        lines = [f"{a['word1']} {a['word2']}"]
    elif shape == "swap_print":
        lines = [str(a["value2"]), str(a["value1"])]
    elif shape == "count_matches":
        lines = [str(sum(1 for n in a["items"] if value(a["cond"], {"n": n})))]
    elif shape == "two_lists":
        lines = [
            str(value(a["expr"], {"x": x, "y": y}))
            for x, y in zip(a["xs"], a["ys"])
        ]
    elif shape == "grid_print":
        lines = [
            str(value(a["expr"], {"v": v})) for row in a["rows"] for v in row
        ]
    elif shape == "list_min":
        lines = [str(min(a["items"]))]
    elif shape == "list_reverse":
        lines = [str(n) for n in reversed(a["items"])]
    elif shape == "find_index":
        lines = [str(a["items"].index(a["target"]))]
    else:
        raise KeyError(shape)
    return NL.join(lines)
