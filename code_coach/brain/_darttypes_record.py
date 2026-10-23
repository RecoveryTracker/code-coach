"""Dart types pack, part 6: Record Facts - what do Dart 3 records hold, print and equal?

A record is a small value made of fields written in parentheses: positional ones (`(1, 'a')`, read with `$1`, `$2`...
counting from 1 and skipping the named ones) and named ones (`(x: 1, y: 2)`, read as `r.x`). Two records are equal when
their fields are equal one by one, the NAMES included but not their order; a record prints as its fields in
parentheses. Records are returned from functions to give several values, and taken apart by destructuring patterns.
Most templates are the body of `main` (no `main(` in the text), so the last bare expression is what is printed. Dart's
`$1` is written `$$1` in a template.
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

EQ = "Records are equal when their fields are equal one by one, with the same names."

RECORDS: list[Maker] = [
    D("var r = ($a, $b);\nr.$$1", lambda p: p["a"], "Field 1 is the first positional field."),
    D("var r = ($a, $b);\nr.$$2", lambda p: p["b"], "The second positional field is field 2; counting starts at 1."),
    D("var r = ($a, '$w', $b);\nr.$$2", lambda p: p["w"], "The second field is the string."),
    D("var r = (x: $a, y: $b);\nr.y", lambda p: p["b"], "A named field is read by its name."),
    D("var r = ($a, name: '$w');\nr.name", lambda p: p["w"], "A record can mix positional and named fields."),
    D("var r = ($a, name: '$w');\nr.$$1", lambda p: p["a"], "The one positional field is field 1."),
    D("var r = (x: $a, $b, $c);\nr.$$1", lambda p: p["b"], "Named fields do not count: the first positional field is the second thing written."),
    D("var r = (x: $a, $b, $c);\nr.$$2 + r.x", lambda p: p["c"] + p["a"], "Field 2 is the last positional one, and x is the named one."),
    D("(int, int) p = ($a, $b);\np.$$1 + p.$$2", lambda p: p["a"] + p["b"], "A record type is written as its field types in parentheses."),
    D("({String name, int age}) p = (name: '$w', age: $n);\np.age + 1", lambda p: p["n"] + 1, "age is the named field holding $n."),
    D("var r = ($a, ($b, $c));\nr.$$2.$$1", lambda p: p["b"], "Field 2 is the inner record, and its field 1 is the first value."),
    D("var r = ($a, ($b, $c));\nr.$$2.$$2 - r.$$1", lambda p: p["c"] - p["a"], "The inner record's second field minus the outer first."),
    D("var r = (x: ($a, $b), y: $c);\nr.x.$$2", lambda p: p["b"], "r.x is a record, and its field 2 is the second value."),
    # ── printing ──
    D("($a, $b)", lambda p: f"({p['a']}, {p['b']})", "A record prints its fields in parentheses, separated by commas."),
    D("($a, '$w')", lambda p: f"({p['a']}, {p['w']})", "Strings print without quotes."),
    D("(x: $a, y: $b)", lambda p: f"(x: {p['a']}, y: {p['b']})", "Named fields print with their names."),
    D("($a, name: '$w')", lambda p: f"({p['a']}, name: {p['w']})", "Positional fields come first, then the named ones."),
    D("($a, ($b, $c))", lambda p: f"({p['a']}, ({p['b']}, {p['c']}))", "A record inside a record prints in its own parentheses."),
    D("'$${($a, $b)}'", lambda p: f"({p['a']}, {p['b']})", "Interpolating a record gives the same text print would."),
    D("($a,)", lambda p: f"({p['a']})", "A one-field record prints like its field in parentheses, though it is a record, not a number."),
    D("[($a, '$s1'), ($b, '$s2')]", lambda p: f"[({p['a']}, {p['s1']}), ({p['b']}, {p['s2']})]", "A list of records prints each one in parentheses."),
    D("(x: $a, y: $b).toString().length", lambda p: len(f"(x: {p['a']}, y: {p['b']})"), "The text is (x: a, y: b), and its length counts every character."),
    # ── equality ──
    D("($a, $b) == ($a, $b)", True, EQ),
    D("($a, $b) == ($b, $a)", False, "The fields are compared in order, and a is not b."),
    D("(x: $a, y: $b) == (y: $b, x: $a)", True, "The order of NAMED fields does not matter."),
    D("(x: $a, y: $b) == ($a, $b)", False, "Named and positional fields are different shapes."),
    D("(x: $a, y: $b) == (x: $a, z: $b)", False, "The names must match too."),
    D("($a, '$w') == ($a, '$w')", True, EQ),
    D("($a, '$w') == ($a, '$v')", False, "The second fields differ."),
    D("($a, $b) == ($a, $b, $c)", False, "A different number of fields is a different record."),
    D("($a, ($b, $c)) == ($a, ($b, $c))", True, "Inner records are compared by their fields as well."),
    D("([$a], $b) == ([$a], $b)", False, "The two lists are different objects, and lists compare by identity."),
    D("var l = [$a];\n(l, $b) == (l, $b)", True, "The same list in both records is equal to itself."),
    D("{($a, $b), ($a, $b)}.length", 1, "A set treats equal records as one."),
    D("{($a, $b), ($b, $a)}.length", 2, "The order of positional fields counts, so these are two."),
    D("{($a, $b): '$w'}[($a, $b)]", lambda p: p["w"], "An equal record finds the key."),
    D("($a, $b).hashCode == ($a, $b).hashCode", True, "Equal records have the same hash code."),
    D("var a = ($a, $b);\nvar b = a;\nidentical(a, b)", True, "Both variables hold the very same record."),
    # ── types ──
    D("($a, $b) is (int, int)", True, "Both fields are ints."),
    D("($a, '$w') is (int, int)", False, "The second field is a string."),
    D("($a, $b) is (int, int, int)", False, "A different number of fields is a different type."),
    D("($a, $b) is (num, num)", True, "int fits num, so the record fits too."),
    D("($a,) is int", False, "With the trailing comma it is a record, not a number."),
    D("($a) is int", True, "Without the trailing comma the parentheses just group the number."),
    D("(x: $a, y: $b) is ({int x, int y})", True, "A named record type lists its names and types in braces."),
    # ── returning and destructuring ──
    D("var (p, q) = ($a, $b);\np * q", lambda p: p["a"] * p["b"], "A pattern takes the record apart into two variables."),
    D("var (:x, :y) = (x: $a, y: $b);\nx - y", lambda p: p["a"] - p["b"], "(:x, :y) takes the named fields into variables of the same names."),
    D("var (x: px, y: py) = (x: $a, y: $b);\npy - px", lambda p: p["b"] - p["a"], "x: px puts the field x into the variable px."),
    D("var (p, (q, r)) = ($a, ($b, $c));\nq + r", lambda p: p["b"] + p["c"], "Patterns can nest, like the records they match."),
    D("var a = $a, b = $b;\n(a, b) = (b, a);\n'$$a$$b'", lambda p: f"{p['b']}{p['a']}", "The right side is built first, so the swap works with no helper."),
    D("var [x, y] = [$a, $b];\nx + y", lambda p: p["a"] + p["b"], "A list pattern takes items by position."),
    D("var {'k': v} = {'k': $a};\nv", lambda p: p["a"], "A map pattern takes the value for a key."),
    D("(int, int) divmod(int a, int b) => (a ~/ b, a % b);\nvoid main() {\n  var (q, r) = divmod($n, $a);\n  print('$$q r$$r');\n}", lambda p: f"{p['n'] // p['a']} r{p['n'] % p['a']}", "~/ is the whole part of the division and % is what is left."),
    D("(int, String) f() => ($a, '$w');\nvoid main() => print(f().$$2);", lambda p: p["w"], "The function hands back two values in one record."),
    D("({int lo, int hi}) span(int a, int b) => a < b ? (lo: a, hi: b) : (lo: b, hi: a);\nvoid main() => print(span($a, $b).hi);", lambda p: max(p["a"], p["b"]), "span puts the smaller in lo and the larger in hi."),
    D("({int lo, int hi}) span(int a, int b) => a < b ? (lo: a, hi: b) : (lo: b, hi: a);\nvoid main() {\n  var (:lo, :hi) = span($a, $b);\n  print(hi - lo);\n}", lambda p: abs(p["a"] - p["b"]), "Whichever order the arguments come in, hi minus lo is the gap."),
    D("[($a, 'x'), ($b, 'y')].map((r) => r.$$1).join(',')", lambda p: f"{p['a']},{p['b']}", "map takes the first field of each record."),
    D("[($a, 'x'), ($b, 'y')].map((r) => r.$$1).reduce((p, q) => p + q)", lambda p: p["a"] + p["b"], "The first fields are added."),
    D("([($a, 'x'), ($b, 'y')]..sort((p, q) => p.$$1.compareTo(q.$$1))).first.$$2", lambda p: "x" if p["a"] < p["b"] else "y", "Sorted by the first field, the record with the smaller number comes first."),
    D("var m = {for (var r in [($a, '$s1'), ($b, '$s2')]) r.$$2: r.$$1};\nm", lambda p: {p["s1"]: p["a"], p["s2"]: p["b"]}, "Each record becomes one map entry."),
    D("Object r = ($a, $b);\nif (r case (int p, int q)) print(p + q); else print('no');", lambda p: p["a"] + p["b"], "The pattern matches a record of two ints and names its fields."),
    D("Object r = ($a, '$w');\nif (r case (int p, int q)) print(p + q); else print('no');", "no", "The second field is a string, so the pattern does not match."),
    D("String where((int, int) p) => switch (p) {\n  (0, 0) => 'origin',\n  (var x, 0) => 'x-axis',\n  (0, _) => 'y-axis',\n  _ => 'plane',\n};\nvoid main() => print(where((0, $a)));", "y-axis", "The first value is 0 and the second is not, so the third arm matches."),
    D("String where((int, int) p) => switch (p) {\n  (0, 0) => 'origin',\n  (var x, 0) => 'x-axis',\n  (0, _) => 'y-axis',\n  _ => 'plane',\n};\nvoid main() => print(where(($a, 0)));", "x-axis", "The second value is 0, so the second arm matches."),
    D("String where((int, int) p) => switch (p) {\n  (0, 0) => 'origin',\n  (var x, 0) => 'x-axis',\n  (0, _) => 'y-axis',\n  _ => 'plane',\n};\nvoid main() => print(where(($a, $b)));", "plane", "Neither value is 0, so only the wildcard arm matches."),
]
