"""Dart data pack, part 7: Pattern Match - Dart 3 records and patterns.

Records `(1, 'a')` with `$1`/`$2` and named fields, `var (x, y) = ...`, list patterns `[a, b, ...rest]`, map patterns,
switch expressions with relational patterns, `||`, `when` guards and type tests, `if (x case ...)`, object patterns.
Dart 3.0 and later: the 3.7 runtime on this machine has all of it. Each switch ends with `_` (or covers its type), so
none of the prompts is a compile error.
"""

from __future__ import annotations

from ._dartdata_model import R, ints, lit, rec, words
from ._model import Maker


def p_destructure_sub(r):
    a, b = ints(r, 2, 2, 9)
    return f"var (x, y) = ({a}, {b});\nprint(x - y);", a - b, "x gets the first field of the record and y the second."


def p_swap(r):
    a, b = ints(r, 2, 2, 9)
    return f"var (x, y) = ({a}, {b});\n(x, y) = (y, x);\nprint('$x$y');", f"{b}{a}", "A record pattern on the left of = swaps two variables in one step."


def p_field2(r):
    a, w = r.randint(2, 9), words(r, 1)[0]
    return f"var r = ({a}, '{w}');\nprint(r.$2);", w, "Positional fields are numbered from 1: the second field is the string."


def p_field1(r):
    a, w = r.randint(2, 9), words(r, 1)[0]
    return f"var r = ({a}, '{w}');\nprint(r.$1 * 2);", a * 2, "The first field is the number; it is doubled."


def p_named_age(r):
    w, n = words(r, 1)[0], r.randint(10, 40)
    return f"var p = (name: '{w}', age: {n});\nprint(p.age + 1);", n + 1, "A named field is read by its name."


def p_named_name(r):
    w, n = words(r, 1)[0], r.randint(10, 40)
    return f"var p = (name: '{w}', age: {n});\nprint(p.name);", w, "p.name is the string in the name field."


def p_eq_same(r):
    a, b = ints(r, 2, 2, 9)
    return f"print(({a}, {b}) == ({a}, {b}));", True, "Records are equal when all their fields are equal, in the same order."


def p_eq_swapped(r):
    a, b = ints(r, 2, 2, 9)
    return f"print(({a}, {b}) == ({b}, {a}));", False, "The same fields in a different order make a different record."


def p_eq_mixed(r):
    a, w = r.randint(2, 9), words(r, 1)[0]
    return f"print(({a}, '{w}') == ({a}, '{w}'));", True, "Records compare by value: the two strings are equal."


def p_set_len(r):
    a, b = ints(r, 2, 2, 9)
    return f"print({{({a}, {b}), ({a}, {b}), ({b}, {a})}}.length);", 2, "Equal records count once in a set: (a, b) twice, plus (b, a)."


def p_show(r):
    a, b = ints(r, 2, 2, 9)
    return f"print(({a}, {b}));", rec(a, b), "A record prints in round brackets, fields separated by commas."


def p_show_mixed(r):
    a, w = r.randint(2, 9), words(r, 1)[0]
    return f"print(({a}, '{w}', true));", rec(a, w, True), "Strings print without quotes, even inside a record."


def p_show_named(r):
    n = r.randint(2, 9)
    return f"print((age: {n}));", f"(age: {n})", "A named field prints as name: value."


def p_div_record(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"final (q, r) = ({n} ~/ {a}, {n} % {a});\nprint('$q r$r');", f"{n // a} r{n % a}", "One record carries the quotient and the remainder."


def p_named_destructure(r):
    w, n = words(r, 1)[0], r.randint(10, 40)
    return (f"var (:name, :age) = (name: '{w}', age: {n});\nprint('$name $age');", f"{w} {n}",
            "(:name, :age) makes variables called name and age from the fields with those names.")


def p_named_rename(r):
    a, b = ints(r, 2, 2, 9)
    return f"var (x: p, y: q) = (x: {a}, y: {b});\nprint(p * q);", a * b, "(x: p, y: q) reads field x into p and field y into q."


def p_nested(r):
    a, b, c = ints(r, 3, 2, 9)
    return f"var ((x, y), z) = (({a}, {b}), {c});\nprint(x + y + z);", a + b + c, "A pattern can look inside a record inside a record."


def p_from_var(r):
    a, b = ints(r, 2, 2, 9)
    return f"var r = ({a}, {b});\nvar (x, y) = r;\nprint(x * y);", a * b, "The record can come from a variable."


def p_func_record(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return (f"(int, int) f(int n) => (n ~/ {a}, n % {a});\nvoid main() {{\n  var (q, r) = f({n});\n  print(q + r);\n}}", n // a + n % a,
            "A function can return two values at once as a record.")


def p_min_max(r):
    xs = ints(r, 4, 1, 30)
    return (f"(int, int) mm(List<int> xs) {{\n  var s = [...xs]..sort();\n  return (s.first, s.last);\n}}\nvoid main() {{\n  var (lo, hi) = mm({lit(xs)});\n  print(hi - lo);\n}}",
            max(xs) - min(xs), "mm returns the smallest and the biggest as a record; hi - lo is the spread.")


def p_records_in_list(r):
    a, b = ints(r, 2, 2, 9)
    w, v = words(r, 2)
    return (f"var ps = [({a}, '{w}'), ({b}, '{v}')];\nprint(ps.map((p) => p.$1).toList());", [a, b], "The first field of each record: the numbers.")


def p_list_two(r):
    a, b = ints(r, 2, 2, 9)
    return f"var [x, y] = [{a}, {b}];\nprint(x + y);", a + b, "A list pattern takes the items by position."


def p_list_rest(r):
    a, b, c = ints(r, 3, 2, 9)
    return f"var [first, ...rest] = [{a}, {b}, {c}];\nprint(rest);", [b, c], "...rest collects everything after the first item into a list."


def p_list_rest_len(r):
    a, b, c, d = ints(r, 4, 2, 9)
    return f"var [first, ...rest] = [{a}, {b}, {c}, {d}];\nprint(first + rest.length);", a + 3, "first is a, rest has three items."


def p_list_last(r):
    a, b, c = ints(r, 3, 2, 9)
    return f"var [..., last] = [{a}, {b}, {c}];\nprint(last);", c, "... skips the items before; last is the final one."


def p_list_skip(r):
    a, b, c = ints(r, 3, 2, 9)
    return f"var [x, _, z] = [{a}, {b}, {c}];\nprint(x + z);", a + c, "_ matches an item and throws it away."


def p_list_mid(r):
    a, b, c, d = ints(r, 4, 2, 9)
    return f"var [x, ...mid, z] = [{a}, {b}, {c}, {d}];\nprint(mid);", [b, c], "The first and last go to x and z; the middle goes to mid."


def p_list_split(r):
    w, v = words(r, 2)
    return f"var [a, b] = '{w} {v}'.split(' ');\nprint(b + a);", v + w, "split gives a two-item list, and the pattern names its parts."


def p_list_switch(r):
    n = r.randint(0, 4)
    xs = ints(r, n, 2, 9) if n else []
    ans = {0: "empty", 1: "one", 2: "two"}.get(n, "many")
    return (f"var xs = {lit(xs) if xs else '<int>[]'};\nprint(switch (xs) {{\n  [] => 'empty',\n  [_] => 'one',\n  [_, _] => 'two',\n  _ => 'many',\n}});", ans,
            "Each list pattern fixes how many items there are.")


def p_list_ifcase(r):
    n = r.randint(1, 3)
    xs = ints(r, n, 2, 9)
    out = xs[0] + xs[1] if n == 2 else 0
    return (f"var xs = {lit(xs)};\nvar r = 0;\nif (xs case [var f, var s]) r = f + s;\nprint(r);", out,
            "The pattern only matches a list of exactly two items.")


def p_list_ifcase_rest(r):
    n = r.randint(1, 4)
    xs = ints(r, n, 2, 9)
    return (f"var xs = {lit(xs)};\nvar r = -1;\nif (xs case [var f, _, ...]) r = f;\nprint(r);", xs[0] if n >= 2 else -1,
            "[var f, _, ...] needs at least two items; then f is the first.")


def p_list_const(r):
    a = r.randint(2, 9)
    first = r.choice((0, a))
    xs = [first, r.randint(2, 9)]
    ans = "zero first" if first == 0 else "other"
    return (f"var xs = {lit(xs)};\nprint(switch (xs) {{\n  [0, _] => 'zero first',\n  _ => 'other',\n}});", ans,
            "A constant inside the pattern must equal the item at that position.")


def p_list_forin(r):
    a, b, c, d = ints(r, 4, 2, 9)
    return f"var s = 0;\nfor (var [x, y] in [[{a}, {b}], [{c}, {d}]]) {{\n  s += x * y;\n}}\nprint(s);", a * b + c * d, "The loop pattern splits each pair into x and y."


def p_map_vars(r):
    a, b = ints(r, 2, 2, 9)
    return f"var {{'x': x, 'y': y}} = {{'x': {a}, 'y': {b}}};\nprint(x - y);", a - b, "A map pattern looks values up by key."


def p_map_ifcase(r):
    w, n = words(r, 1)[0], r.randint(10, 40)
    return (f"var m = {{'name': '{w}', 'age': {n}}};\nif (m case {{'name': String n, 'age': int a}}) {{\n  print('$n $a');\n}}", f"{w} {n}",
            "Both keys exist with the right types, so the pattern matches and the variables are set.")


def p_map_missing(r):
    n = r.randint(2, 9)
    return f"var m = {{'a': {n}}};\nvar r = 'none';\nif (m case {{'b': var v}}) r = 'has b';\nprint(r);", "none", "The map has no key b, so the pattern does not match."


def p_map_type(r):
    n = r.randint(2, 9)
    return f"var m = <String, Object>{{'a': {n}}};\nvar r = 'no';\nif (m case {{'a': String s}}) r = 'yes';\nprint(r);", "no", "The value of a is an int, not a String, so the pattern fails."


def p_map_shape(r):
    k = r.randint(2, 6)
    kind = r.choice(("circle", "square"))
    area = 3 * k * k if kind == "circle" else k * k
    return (f"var shape = <String, Object>{{'type': '{kind}', 'n': {k}}};\nprint(switch (shape) {{\n  {{'type': 'circle', 'n': int n}} => 3 * n * n,\n  {{'type': 'square', 'n': int n}} => n * n,\n  _ => 0,\n}});", area,
            "The first case whose keys and values fit is used.")


def p_sw_const(r):
    n = r.randint(1, 4)
    ans = {1: "one", 2: "two"}.get(n, "many")
    return f"var n = {n};\nprint(switch (n) {{\n  1 => 'one',\n  2 => 'two',\n  _ => 'many',\n}});", ans, "A switch expression gives the value of the first case that matches."


def p_sw_range(r):
    n = r.choice((-5, -1, 0, 3, 9, 10, 25))
    ans = "neg" if n < 0 else "zero" if n == 0 else "small" if n < 10 else "big"
    return (f"var n = {n};\nprint(switch (n) {{\n  < 0 => 'neg',\n  0 => 'zero',\n  > 0 && < 10 => 'small',\n  _ => 'big',\n}});", ans,
            "Relational patterns compare with the value; && needs both to hold.")


def p_sw_grade(r):
    s = r.choice((95, 90, 85, 80, 79, 61, 40))
    ans = "A" if s >= 90 else "B" if s >= 80 else "C"
    return f"var s = {s};\nprint(switch (s) {{\n  >= 90 => 'A',\n  >= 80 => 'B',\n  _ => 'C',\n}});", ans, "Cases are tried from the top: the first one that fits wins."


def p_sw_or(r):
    n = r.randint(1, 6)
    return f"var n = {n};\nprint(switch (n) {{\n  1 || 2 || 3 => 'low',\n  _ => 'high',\n}});", "low" if n <= 3 else "high", "|| lets one case match several values."


def p_sw_guard(r):
    n = r.randint(2, 30)
    return f"var n = {n};\nprint(switch (n) {{\n  int x when x.isEven => 'even',\n  _ => 'odd',\n}});", "even" if n % 2 == 0 else "odd", "A when guard adds a condition to the pattern."


def p_sw_guard_val(r):
    n = r.randint(2, 30)
    t = r.randint(8, 20)
    return f"var n = {n};\nprint(switch (n) {{\n  int x when x > {t} => x - {t},\n  int x => x,\n}});", n - t if n > t else n, "The first case has a guard; if it fails the next case is tried."


def p_sw_string(r):
    verb = r.choice(("GET", "HEAD", "POST", "PUT"))
    ans = "read" if verb in ("GET", "HEAD") else "write" if verb == "POST" else "other"
    return f"var v = '{verb}';\nprint(switch (v) {{\n  'GET' || 'HEAD' => 'read',\n  'POST' => 'write',\n  _ => 'other',\n}});", ans, "String constants work as patterns too."


def p_sw_type(r):
    kind = r.choice(("int", "str", "dbl", "list"))
    src = {"int": "7", "str": "'hi'", "dbl": "1.5", "list": "[1]"}[kind]
    ans = {"int": "int", "str": "text", "dbl": "double", "list": "other"}[kind]
    return (f"Object o = {src};\nprint(switch (o) {{\n  int() => 'int',\n  String() => 'text',\n  double() => 'double',\n  _ => 'other',\n}});", ans,
            "int() matches any int, String() any string: a type test.")


def p_sw_null(r):
    a = r.randint(2, 9)
    return (f"int? n = {a} > 5 ? {a} : null;\nprint(switch (n) {{\n  null => 'none',\n  int v => 'got $v',\n}});", f"got {a}" if a > 5 else "none",
            "null matches only null; int v matches any non-null number and names it.")


def p_sw_record(r):
    x, y = r.choice([(0, 0), (3, 0), (0, 4), (2, 5)])
    ans = "origin" if (x, y) == (0, 0) else f"x-axis {x}" if y == 0 else f"y-axis {y}" if x == 0 else "plane"
    return (f"var p = ({x}, {y});\nprint(switch (p) {{\n  (0, 0) => 'origin',\n  (var x, 0) => 'x-axis $x',\n  (0, var y) => 'y-axis $y',\n  _ => 'plane',\n}});", ans,
            "Each case describes the whole record; a var inside names that field.")


def p_sw_record_sum(r):
    a, b = ints(r, 2, 2, 9)
    return f"var p = ({a}, {b});\nprint(switch (p) {{\n  (int x, int y) => x + y,\n}});", a + b, "(int x, int y) matches any pair of ints, so this single case is exhaustive."


def p_sw_stmt(r):
    n = r.randint(1, 30)
    k = r.randint(2, 5)
    ans = "fizz" if n % k == 0 else str(n)
    return (f"var n = {n};\nvar s = '';\nswitch (n) {{\n  case int x when x % {k} == 0:\n    s = 'fizz';\n  default:\n    s = '$n';\n}}\nprint(s);", ans,
            "A Dart switch case does not fall through: no break is needed.")


def p_sw_stmt_multi(r):
    n = r.randint(1, 4)
    ans = "low" if n <= 2 else "high"
    return f"var n = {n};\nvar s = '';\nswitch (n) {{\n  case 1 || 2:\n    s = 'low';\n  default:\n    s = 'high';\n}}\nprint(s);", ans, "case 1 || 2 matches either value."


def p_ifcase_guard(r):
    n = r.randint(2, 20)
    t = r.randint(5, 12)
    return f"var n = {n};\nvar r = 0;\nif (n case int x when x > {t}) r = x * 2;\nprint(r);", n * 2 if n > t else 0, "The if-case body runs only when the pattern AND its guard hold."


def p_ifcase_type(r):
    if r.random() < 0.5:
        w = words(r, 1)[0]
        return f"Object o = '{w}';\nvar r = -1;\nif (o case String s) r = s.length;\nprint(r);", len(w), "o is a string, so s is that string and r is its length."
    n = r.randint(2, 9)
    return f"Object o = {n};\nvar r = -1;\nif (o case String s) r = s.length;\nprint(r);", -1, "o is an int, so the String pattern does not match and r stays -1."


def p_ifcase_nonnull(r):
    a = r.randint(2, 9)
    return f"int? n = {a} > 5 ? {a} : null;\nvar r = 0;\nif (n case var v?) r = v + 1;\nprint(r);", a + 1 if a > 5 else 0, "var v? matches only when n is not null, and v is then a plain int."


def p_forin_records(r):
    a, b = ints(r, 2, 2, 9)
    w, v = words(r, 2)
    return f"var s = '';\nfor (var (n, w) in [({a}, '{w}'), ({b}, '{v}')]) {{\n  s += '$n$w ';\n}}\nprint(s.trim());", f"{a}{w} {b}{v}", "Each record is taken apart in the loop header."


def p_entries(r):
    ks = words(r, 2)
    a, b = ints(r, 2, 2, 9)
    return (f"var m = {{'{ks[0]}': {a}, '{ks[1]}': {b}}};\nvar t = 0;\nfor (var MapEntry(:value) in m.entries) {{\n  t += value;\n}}\nprint(t);", a + b,
            "MapEntry(:value) is an object pattern: it reads the value property.")


def p_point(r):
    a, b = ints(r, 2, 2, 9)
    return (f"class Point {{\n  final int x, y;\n  Point(this.x, this.y);\n}}\nvoid main() {{\n  var Point(:x, :y) = Point({a}, {b});\n  print(x * y);\n}}", a * b,
            "An object pattern reads the properties x and y of the Point.")


def p_sealed(r):
    k = r.choice(("A", "B"))
    n = r.randint(2, 9)
    return (f"sealed class S {{}}\nclass A extends S {{ final int n; A(this.n); }}\nclass B extends S {{ final int n; B(this.n); }}\nint f(S s) => switch (s) {{ A(n: var n) => n, B(n: var n) => n * 2 }};\nvoid main() => print(f({k}({n})));",
            n if k == "A" else 2 * n, "A switch over a sealed class must cover every subclass; each case reads the field n.")


PATTERNS: list[Maker] = [R(f) for f in (
    p_destructure_sub, p_swap, p_field2, p_field1, p_named_age, p_named_name, p_eq_same, p_eq_swapped, p_eq_mixed,
    p_set_len, p_show, p_show_mixed, p_show_named, p_div_record, p_named_destructure, p_named_rename, p_nested,
    p_from_var, p_func_record, p_min_max, p_records_in_list, p_list_two, p_list_rest, p_list_rest_len, p_list_last,
    p_list_skip, p_list_mid, p_list_split, p_list_switch, p_list_ifcase, p_list_ifcase_rest, p_list_const,
    p_list_forin, p_map_vars, p_map_ifcase, p_map_missing, p_map_type, p_map_shape, p_sw_const, p_sw_range,
    p_sw_grade, p_sw_or, p_sw_guard, p_sw_guard_val, p_sw_string, p_sw_type, p_sw_null, p_sw_record,
    p_sw_record_sum, p_sw_stmt, p_sw_stmt_multi, p_ifcase_guard, p_ifcase_type, p_ifcase_nonnull,
    p_forin_records, p_entries, p_point, p_sealed)]
