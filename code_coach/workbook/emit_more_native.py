"""The later shapes in C, C++ and Rust.

These are the languages the deep end was originally left out of, because a
list and a string are genuinely different objects here — C has no growable
list at all, and no method on a string. That is exactly why they are worth
having: the exercise is the same question, and finding out what it costs to
answer it in C is most of what C teaches you.

Where a language cannot do the obvious thing, the shape does the honest
equivalent rather than a trick: C grows a list in a fixed array with a count
beside it, and upper-cases a string one character at a time, because that is
what writing it in C actually involves.

The rule from `emit` still holds and is the whole game: every language's
answer prints exactly the same characters. Nothing prints a list, a boolean,
or a division.
"""

from __future__ import annotations

from typing import Callable

from code_coach.workbook.emit import NL, _lines, _q

LANGUAGES: tuple[str, ...] = ("c", "cpp", "rust")


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


# ── C ────────────────────────────────────────────────────────
#
# Everything lives in main except a function definition, which has to sit
# above it — so those shapes write the whole file themselves.

def _c_printf(expr: str) -> str:
    return 'printf("%d\\n", ' + expr + ");"


def _c_puts(text: str) -> str:
    return 'printf("%s\\n", ' + text + ");"


def _c_body(shape: str, a: dict) -> str:
    if shape == "say_value":
        return 'printf("' + a["label"] + ': %d\\n", ' + a["expr"] + ");"
    if shape == "repeat_text":
        return _lines(
            f"for (int i = 0; i < {a['count']}; i++) {{",
            "    " + _c_puts(_q(a["text"])),
            "  }",
        )
    if shape == "quoted_text":
        return _c_puts(_q(a["text"]))
    if shape == "if_print":
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            "    " + _c_puts(_q(a["text"])),
            "  }",
        )
    if shape == "if_else_print":
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            "    " + _c_puts(_q(a["yes"])),
            "  } else {",
            "    " + _c_puts(_q(a["no"])),
            "  }",
        )
    if shape == "bigger_print":
        return _lines(
            f"int {a['name1']} = {a['value1']};",
            f"  int {a['name2']} = {a['value2']};",
            f"  if ({a['name1']} > {a['name2']}) {{",
            "    " + _c_printf(a["name1"]),
            "  } else {",
            "    " + _c_printf(a["name2"]),
            "  }",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['left']} {joiner} {a['right']}) {{",
            "    " + _c_puts(_q(a["yes"])),
            "  } else {",
            "    " + _c_puts(_q(a["no"])),
            "  }",
        )
    if shape == "while_count":
        return _lines(
            f"int i = {a['lo']};",
            f"  while (i <= {a['hi']}) {{",
            "    " + _c_printf(a["expr"]),
            "    i++;",
            "  }",
        )
    if shape == "while_sum":
        return _lines(
            f"int i = {a['lo']};",
            "  int total = 0;",
            f"  while (i <= {a['hi']}) {{",
            f"    total += {a['expr']};",
            "    i++;",
            "  }",
            "  " + _c_printf("total"),
        )
    if shape == "list_loop":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    int n = nums[k];",
            "    " + _c_printf(a["expr"]),
            "  }",
        )
    if shape == "list_sum":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            "  int total = 0;",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    total += nums[k];",
            "  }",
            "  " + _c_printf("total"),
        )
    if shape == "list_index":
        picks = ["  " + _c_printf(f"nums[{i}]") for i in a["indexes"]]
        return _lines(f"int nums[] = {{{_ints(a['items'])}}};", *picks)
    if shape == "list_filter":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    int n = nums[k];",
            f"    if ({a['cond']}) {{",
            "      " + _c_printf("n"),
            "    }",
            "  }",
        )
    if shape == "list_build":
        room = a["hi"] - a["lo"] + 1
        return _lines(
            f"int out[{room}];",
            "  int len = 0;",
            f"  for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    out[len] = {a['expr']};",
            "    len++;",
            "  }",
            "  for (int k = 0; k < len; k++) {",
            "    " + _c_printf("out[k]"),
            "  }",
        )
    if shape == "list_max":
        return _lines(
            f"int nums[] = {{{_ints(a['items'])}}};",
            "  int best = nums[0];",
            f"  for (int k = 0; k < {len(a['items'])}; k++) {{",
            "    if (nums[k] > best) {",
            "      best = nums[k];",
            "    }",
            "  }",
            "  " + _c_printf("best"),
        )
    if shape == "str_length":
        return "  " + _c_printf(f"(int)strlen({_q(a['word'])})")
    if shape == "str_loop":
        return _lines(
            f"const char *w = {_q(a['word'])};",
            "  for (int k = 0; w[k] != 0; k++) {",
            '    printf("%c\\n", w[k]);',
            "  }",
        )
    if shape == "str_upper":
        return _lines(
            f"const char *w = {_q(a['word'])};",
            "  for (int k = 0; w[k] != 0; k++) {",
            "    putchar(toupper((unsigned char)w[k]));",
            "  }",
            '  putchar(chr_newline);',
        )
    raise KeyError(shape)


_C_HEAD = _lines(
    "#include <stdio.h>",
    "#include <string.h>",
    "#include <ctype.h>",
    "",
)


def _c(shape: str, a: dict) -> str:
    if shape == "func_print":
        calls = [f"  {a['name']}();" for _ in range(a["times"])]
        return _lines(
            _C_HEAD,
            f"void {a['name']}(void) {{",
            "  " + _c_puts(_q(a["text"])),
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_arg":
        calls = [f"  {a['name']}({v});" for v in a["calls"]]
        return _lines(
            _C_HEAD,
            f"void {a['name']}(int {a['param']}) {{",
            "  " + _c_printf(a["expr"]),
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_return":
        calls = ["  " + _c_printf(f"{a['name']}({v})") for v in a["calls"]]
        return _lines(
            _C_HEAD,
            f"int {a['name']}(int {a['param']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "int main(void) {",
            *calls,
            "  return 0;",
            "}",
        )
    body = _c_body(shape, a).replace("chr_newline", "'\\n'")
    return _lines(_C_HEAD, "int main(void) {", "  " + body.lstrip(), "  return 0;", "}")


# ── C++ ──────────────────────────────────────────────────────

def _cpp_out(expr: str) -> str:
    return "std::cout << " + expr + ' << "\\n";'


def _cpp_body(shape: str, a: dict) -> str:
    if shape == "say_value":
        return f'std::cout << "{a["label"]}: " << ({a["expr"]}) << "\\n";'
    if shape == "repeat_text":
        return _lines(
            f"for (int i = 0; i < {a['count']}; i++) {{",
            "    " + _cpp_out(_q(a["text"])),
            "  }",
        )
    if shape == "quoted_text":
        return _cpp_out(_q(a["text"]))
    if shape == "if_print":
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            "    " + _cpp_out(_q(a["text"])),
            "  }",
        )
    if shape == "if_else_print":
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['cond']}) {{",
            "    " + _cpp_out(_q(a["yes"])),
            "  } else {",
            "    " + _cpp_out(_q(a["no"])),
            "  }",
        )
    if shape == "bigger_print":
        return _lines(
            f"int {a['name1']} = {a['value1']};",
            f"  int {a['name2']} = {a['value2']};",
            f"  if ({a['name1']} > {a['name2']}) {{",
            "    " + _cpp_out(a["name1"]),
            "  } else {",
            "    " + _cpp_out(a["name2"]),
            "  }",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"int {a['name']} = {a['value']};",
            f"  if ({a['left']} {joiner} {a['right']}) {{",
            "    " + _cpp_out(_q(a["yes"])),
            "  } else {",
            "    " + _cpp_out(_q(a["no"])),
            "  }",
        )
    if shape == "while_count":
        return _lines(
            f"int i = {a['lo']};",
            f"  while (i <= {a['hi']}) {{",
            "    " + _cpp_out(a["expr"]),
            "    i++;",
            "  }",
        )
    if shape == "while_sum":
        return _lines(
            f"int i = {a['lo']};",
            "  int total = 0;",
            f"  while (i <= {a['hi']}) {{",
            f"    total += {a['expr']};",
            "    i++;",
            "  }",
            "  " + _cpp_out("total"),
        )
    if shape == "list_loop":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  for (int n : nums) {",
            "    " + _cpp_out(a["expr"]),
            "  }",
        )
    if shape == "list_sum":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  int total = 0;",
            "  for (int n : nums) {",
            "    total += n;",
            "  }",
            "  " + _cpp_out("total"),
        )
    if shape == "list_index":
        picks = ["  " + _cpp_out(f"nums[{i}]") for i in a["indexes"]]
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};", *picks
        )
    if shape == "list_filter":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  for (int n : nums) {",
            f"    if ({a['cond']}) {{",
            "      " + _cpp_out("n"),
            "    }",
            "  }",
        )
    if shape == "list_build":
        return _lines(
            "std::vector<int> out;",
            f"  for (int i = {a['lo']}; i <= {a['hi']}; i++) {{",
            f"    out.push_back({a['expr']});",
            "  }",
            "  for (int n : out) {",
            "    " + _cpp_out("n"),
            "  }",
        )
    if shape == "list_max":
        return _lines(
            f"std::vector<int> nums = {{{_ints(a['items'])}}};",
            "  int best = nums[0];",
            "  for (int n : nums) {",
            "    if (n > best) {",
            "      best = n;",
            "    }",
            "  }",
            "  " + _cpp_out("best"),
        )
    if shape == "str_length":
        return _lines(
            f"std::string w = {_q(a['word'])};",
            "  " + _cpp_out("w.size()"),
        )
    if shape == "str_loop":
        return _lines(
            f"std::string w = {_q(a['word'])};",
            "  for (char c : w) {",
            "    " + _cpp_out("c"),
            "  }",
        )
    if shape == "str_upper":
        return _lines(
            f"std::string w = {_q(a['word'])};",
            "  for (char &c : w) {",
            "    c = (char)std::toupper((unsigned char)c);",
            "  }",
            "  " + _cpp_out("w"),
        )
    raise KeyError(shape)


_CPP_HEAD = _lines(
    "#include <iostream>",
    "#include <string>",
    "#include <vector>",
    "#include <cctype>",
    "",
)


def _cpp(shape: str, a: dict) -> str:
    if shape == "func_print":
        calls = [f"  {a['name']}();" for _ in range(a["times"])]
        return _lines(
            _CPP_HEAD,
            f"void {a['name']}() {{",
            "  " + _cpp_out(_q(a["text"])),
            "}",
            "",
            "int main() {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_arg":
        calls = [f"  {a['name']}({v});" for v in a["calls"]]
        return _lines(
            _CPP_HEAD,
            f"void {a['name']}(int {a['param']}) {{",
            "  " + _cpp_out(a["expr"]),
            "}",
            "",
            "int main() {",
            *calls,
            "  return 0;",
            "}",
        )
    if shape == "func_return":
        calls = ["  " + _cpp_out(f"{a['name']}({v})") for v in a["calls"]]
        return _lines(
            _CPP_HEAD,
            f"int {a['name']}(int {a['param']}) {{",
            f"  return {a['expr']};",
            "}",
            "",
            "int main() {",
            *calls,
            "  return 0;",
            "}",
        )
    return _lines(
        _CPP_HEAD,
        "int main() {",
        "  " + _cpp_body(shape, a),
        "  return 0;",
        "}",
    )


# ── Rust ─────────────────────────────────────────────────────

def _rs(expr: str) -> str:
    return 'println!("{}", ' + expr + ");"


def _rust_body(shape: str, a: dict) -> str:
    if shape == "say_value":
        return 'println!("' + a["label"] + ': {}", ' + a["expr"] + ");"
    if shape == "repeat_text":
        return _lines(
            f"for _ in 0..{a['count']} {{",
            "        " + _rs(_q(a["text"])),
            "    }",
        )
    if shape == "quoted_text":
        return _rs(_q(a["text"]))
    if shape == "if_print":
        return _lines(
            f"let {a['name']} = {a['value']};",
            f"    if {a['cond']} {{",
            "        " + _rs(_q(a["text"])),
            "    }",
        )
    if shape == "if_else_print":
        return _lines(
            f"let {a['name']} = {a['value']};",
            f"    if {a['cond']} {{",
            "        " + _rs(_q(a["yes"])),
            "    } else {",
            "        " + _rs(_q(a["no"])),
            "    }",
        )
    if shape == "bigger_print":
        return _lines(
            f"let {a['name1']} = {a['value1']};",
            f"    let {a['name2']} = {a['value2']};",
            f"    if {a['name1']} > {a['name2']} {{",
            "        " + _rs(a["name1"]),
            "    } else {",
            "        " + _rs(a["name2"]),
            "    }",
        )
    if shape == "and_or_print":
        joiner = "&&" if a["op"] == "and" else "||"
        return _lines(
            f"let {a['name']} = {a['value']};",
            f"    if {a['left']} {joiner} {a['right']} {{",
            "        " + _rs(_q(a["yes"])),
            "    } else {",
            "        " + _rs(_q(a["no"])),
            "    }",
        )
    if shape == "while_count":
        return _lines(
            f"let mut i = {a['lo']};",
            f"    while i <= {a['hi']} {{",
            "        " + _rs(a["expr"]),
            "        i += 1;",
            "    }",
        )
    if shape == "while_sum":
        return _lines(
            f"let mut i = {a['lo']};",
            "    let mut total = 0;",
            f"    while i <= {a['hi']} {{",
            f"        total += {a['expr']};",
            "        i += 1;",
            "    }",
            "    " + _rs("total"),
        )
    if shape == "list_loop":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    for n in nums {",
            "        " + _rs(a["expr"]),
            "    }",
        )
    if shape == "list_sum":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    let mut total = 0;",
            "    for n in nums {",
            "        total += n;",
            "    }",
            "    " + _rs("total"),
        )
    if shape == "list_index":
        picks = ["    " + _rs(f"nums[{i}]") for i in a["indexes"]]
        return _lines(f"let nums = [{_ints(a['items'])}];", *picks)
    if shape == "list_filter":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    for n in nums {",
            f"        if {a['cond']} {{",
            "            " + _rs("n"),
            "        }",
            "    }",
        )
    if shape == "list_build":
        return _lines(
            "let mut out = Vec::new();",
            f"    for i in {a['lo']}..={a['hi']} {{",
            f"        out.push({a['expr']});",
            "    }",
            "    for n in out {",
            "        " + _rs("n"),
            "    }",
        )
    if shape == "list_max":
        return _lines(
            f"let nums = [{_ints(a['items'])}];",
            "    let mut best = nums[0];",
            "    for n in nums {",
            "        if n > best {",
            "            best = n;",
            "        }",
            "    }",
            "    " + _rs("best"),
        )
    if shape == "str_length":
        return _rs(f"{_q(a['word'])}.len()")
    if shape == "str_loop":
        return _lines(
            f"for c in {_q(a['word'])}.chars() {{",
            "        " + _rs("c"),
            "    }",
        )
    if shape == "str_upper":
        return _rs(f"{_q(a['word'])}.to_uppercase()")
    raise KeyError(shape)


def _rust(shape: str, a: dict) -> str:
    if shape == "func_print":
        calls = [f"    {a['name']}();" for _ in range(a["times"])]
        return _lines(
            f"fn {a['name']}() {{",
            "    " + _rs(_q(a["text"])),
            "}",
            "",
            "fn main() {",
            *calls,
            "}",
        )
    if shape == "func_arg":
        calls = [f"    {a['name']}({v});" for v in a["calls"]]
        return _lines(
            f"fn {a['name']}({a['param']}: i32) {{",
            "    " + _rs(a["expr"]),
            "}",
            "",
            "fn main() {",
            *calls,
            "}",
        )
    if shape == "func_return":
        calls = ["    " + _rs(f"{a['name']}({v})") for v in a["calls"]]
        return _lines(
            f"fn {a['name']}({a['param']}: i32) -> i32 {{",
            f"    {a['expr']}",
            "}",
            "",
            "fn main() {",
            *calls,
            "}",
        )
    return "fn main() {" + NL + "    " + _rust_body(shape, a) + NL + "}"


_EMITTERS: dict[str, Callable[[str, dict], str]] = {
    "c": _c,
    "cpp": _cpp,
    "rust": _rust,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    emit = _EMITTERS.get(language)
    if emit is None:
        return None
    return emit(shape, args)
