"""Dart types pack, part 7: Sealed Switch - sealed classes, switch expressions and patterns.

A `sealed` class can only be extended in its own library, so the compiler knows every subclass and makes a `switch` over
it EXHAUSTIVE (no `default` needed). A switch expression runs the first arm whose pattern matches (and whose `when`
guard is true): an object pattern `Sq(:var a)` tests the type and takes a getter into a variable, `Sq(a: 3)` and
`Sq(a: > 5)` test the field, `_` matches anything, `||` joins patterns. The same patterns work on ints, lists, maps,
records and `null`. The sealed families are tiny so that a whole program fits in 220 characters.
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

FIRST = "The arms are tried from the top and the first one that matches runs."

SHAPE = "sealed class S {}\nclass Sq extends S { int a; Sq(this.a); }\nclass Ci extends S { int r; Ci(this.r); }"
RES0 = "sealed class R {}\nclass Ok extends R { int v; Ok(this.v); }\nclass Err extends R {}"
RES = "sealed class R {}\nclass Ok extends R { int v; Ok(this.v); }\nclass Err extends R { String m; Err(this.m); }"
ST = "sealed class T {}\nclass Wait extends T {}\nclass Done extends T { int n; Done(this.n); }\nclass Fail extends T {}"


def _sw(decl: str, typ: str, ret: str, arms: str, call: str, ans, why: str) -> Maker:
    """A switch expression over a sealed family, in a function `f`, called from main."""
    fmt = f"{decl}\n{ret} f({typ} x) => switch (x) {{ {arms} }};\nvoid main() => print({call});"
    return D(fmt, ans, why)


def _fn(sig: str, arms: str, call: str, ans, why: str) -> Maker:
    """A switch expression over ints, lists, strings...: a local function in the body of main, then the call."""
    return D(f"{sig} => switch (x) {{ {arms} }};\n{call}", ans, why)


def _label(a: int, c: int) -> str:
    return "big" if a > c else "small"


SEALED: list[Maker] = [
    # ── shapes: Sq(a), Ci(r) ──
    _sw(SHAPE, "S", "int", "Sq(:var a) => a * a, Ci(:var r) => r * 3", "f(Sq($a))", lambda p: p["a"] ** 2, "Sq(:var a) takes the getter a into a variable, then the arm squares it."),
    _sw(SHAPE, "S", "int", "Sq(:var a) => a * a, Ci(:var r) => r * 3", "f(Ci($a))", lambda p: 3 * p["a"], "The object is a Ci, so the second arm runs."),
    _sw(SHAPE, "S", "String", "Sq(:var a) when a > $c => 'big', _ => 'no'", "f(Sq($a))", lambda p: "big" if p["a"] > p["c"] else "no", "The guard decides: the first arm needs a > c, otherwise _ catches it."),
    _sw(SHAPE, "S", "String", "Sq(:var a) when a > $c => 'big', _ => 'no'", "f(Ci($a))", "no", "A Ci never matches the Sq arm, so _ runs."),
    _sw(SHAPE, "S", "String", "Sq() => 'square', Ci() => 'circle'", "f(Sq($a))", "square", "Sq() only tests the type."),
    _sw(SHAPE, "S", "String", "Sq() => 'square', Ci() => 'circle'", "f(Ci($a))", "circle", "Ci() only tests the type."),
    _sw(SHAPE, "S", "String", "Sq() => 'sq', _ => 'other'", "f(Ci($a))", "other", "_ matches anything the earlier arms did not."),
    _sw(SHAPE, "S", "String", "Sq() => 'sq', _ => 'other'", "f(Sq($a))", "sq", "The first arm matches a Sq, so _ is never reached."),
    _sw(SHAPE, "S", "String", "Sq(a: $a) => 'hit', Sq() => 'sq', Ci() => 'ci'", "f(Sq($a))", "hit", "Sq(a: 3) matches only when the field a equals that constant."),
    _sw(SHAPE, "S", "String", "Sq(a: $a) => 'hit', Sq() => 'sq', Ci() => 'ci'", "f(Sq($b))", "sq", "The field is not the constant, so the plain Sq() arm runs."),
    _sw(SHAPE, "S", "String", "Sq(a: > $c) => 'big', Sq() => 'small', Ci() => 'ci'", "f(Sq($a))", lambda p: _label(p["a"], p["c"]), "A relational pattern tests the field: a > c."),
    _sw(SHAPE, "S", "int", "Sq sq => sq.a, Ci ci => ci.r + 1", "f(Ci($a))", lambda p: p["a"] + 1, "Ci ci tests the type and names the object as a Ci."),
    _sw(SHAPE, "S", "int", "Sq sq => sq.a, Ci ci => ci.r + 1", "f(Sq($a))", lambda p: p["a"], "Sq sq tests the type and names the object as a Sq."),
    _sw(SHAPE, "S", "String", "Sq() || Ci() => 'shape'", "f(Ci($a))", "shape", "|| joins patterns into one arm."),
    D(SHAPE + "\nvoid main() => print(<S>[Sq($a), Ci($b), Sq($c)].whereType<Sq>().length);", 2, "whereType<Sq> keeps only the squares."),
    D(SHAPE + "\nvoid main() {\n  S s = Ci($a);\n  print(s is Sq ? 'sq' : 'not sq');\n}", "not sq", "The object is a Ci."),
    D(SHAPE + "\nvoid main() {\n  S s = Sq($a);\n  print(s is Sq ? s.a + 1 : 0);\n}", lambda p: p["a"] + 1, "After s is Sq, Dart lets s.a be read directly."),
    D(SHAPE + "\nString f(S s) {\n  if (s case Sq(:var a)) return 'sq$$a';\n  return 'other';\n}\nvoid main() => print(f(Sq($a)));", lambda p: f"sq{p['a']}", "if-case runs the block only when the pattern matches, binding a."),
    D(SHAPE + "\nString f(S s) {\n  if (s case Sq(:var a)) return 'sq$$a';\n  return 'other';\n}\nvoid main() => print(f(Ci($a)));", "other", "A Ci does not match, so the code falls through."),
    D(SHAPE + "\nString f(S s) {\n switch (s) {\n  case Sq(): return 'x';\n  case Ci(): return 'y';\n }\n}\nvoid main() => print(f(Ci($a)));", "y", "A switch statement over a sealed type needs no default either."),
    # ── results: Ok(v), Err() ──
    _sw(RES0, "R", "int", "Ok(:var v) => v * 2, Err() => 0", "f(Ok($a))", lambda p: 2 * p["a"], "Ok(:var v) takes the value and doubles it."),
    _sw(RES0, "R", "int", "Ok(:var v) => v * 2, Err() => 0", "f(Err())", 0, "An Err takes the second arm."),
    _sw(RES0, "R", "String", "Ok(:var v) when v.isEven => 'even', Ok() => 'odd', Err() => 'err'", "f(Ok($a))", lambda p: "even" if p["a"] % 2 == 0 else "odd", "The guard asks whether the value is even."),
    _sw(RES0, "R", "String", "Ok(:var v) when v.isEven => 'even', Ok() => 'odd', Err() => 'err'", "f(Err())", "err", "An Err matches neither Ok arm."),
    _sw(RES0, "R", "String", "Ok(v: > $c) => 'high', Ok() => 'low', Err() => 'err'", "f(Ok($a))", lambda p: "high" if p["a"] > p["c"] else "low", "A relational pattern on the field v: v > c."),
    _sw(RES0, "R", "String", "Ok(v: > $c) => 'high', Ok() => 'low', Err() => 'err'", "f(Err())", "err", "An Err is not an Ok, so only the last arm fits."),
    _sw(RES0, "R", "int", "Ok(:var v) => v + 1, Err() => -1", "f(Ok(f(Ok($a))))", lambda p: p["a"] + 2, "The inner call gives a + 1, and the outer one adds 1 more."),
    _sw(RES0, "R", "int", "Ok(:var v) => v + 1, Err() => -1", "f(Ok(f(Err())))", 0, "The inner call gives -1, and the outer one adds 1."),
    D(RES0 + "\nint f((R, R) x) => switch (x) { (Ok(:var v), Ok(v: var w)) => v + w, _ => 0 };\nvoid main() => print(f((Ok($a), Ok($b))));", lambda p: p["a"] + p["b"], "A record pattern matches two results at once."),
    D(RES0 + "\nint f((R, R) x) => switch (x) { (Ok(:var v), Ok(v: var w)) => v + w, _ => 0 };\nvoid main() => print(f((Ok($a), Err())));", 0, "The second result is an Err, so only _ matches."),
    _sw(RES, "R", "String", "Ok() => 'ok', Err(:var m) => m", "f(Err('$w'))", lambda p: p["w"], "Err(:var m) hands the message to the arm."),
    _sw(RES, "R", "int", "Err(m: '$x') => 1, Err() => 2, Ok() => 3", "f(Err('$x'))", 1, "The message equals the constant in the first arm."),
    _sw(RES, "R", "int", "Err(m: '$x') => 1, Err() => 2, Ok() => 3", "f(Err('z'))", 2, "A different message falls to the plain Err() arm."),
    _sw(RES, "R", "int", "Err(m: '$x') => 1, Err() => 2, Ok() => 3", "f(Ok($a))", 3, "An Ok takes the last arm."),
    # ── loading states: Wait, Done(n), Fail ──
    _sw(ST, "T", "int", "Wait() => 0, Done(:var n) => n, _ => -1", "f(Wait())", 0, "Wait() matches the first arm."),
    _sw(ST, "T", "int", "Wait() => 0, Done(:var n) => n, _ => -1", "f(Done($a))", lambda p: p["a"], "The value inside Done is returned."),
    _sw(ST, "T", "int", "Wait() => 0, Done(:var n) => n, _ => -1", "f(Fail())", -1, "Fail is neither of the first two, so _ gives -1."),
    _sw(ST, "T", "int", "Done(:var n) when n > $c => 1, _ => 0", "f(Done($a))", lambda p: 1 if p["a"] > p["c"] else 0, "The guard compares n with c."),
    _sw(ST, "T", "int", "Done(:var n) when n > $c => 1, _ => 0", "f(Wait())", 0, "Wait is not a Done, so _ matches."),
    _sw(ST, "T", "bool", "Wait() || Fail() => false, Done() => true", "f(Fail())", False, "|| puts Wait and Fail in one arm."),
    _sw(ST, "T", "bool", "Wait() || Fail() => false, Done() => true", "f(Done($a))", True, "A Done takes the last arm."),
    D(ST + "\nvoid main() => print(<T>[Wait(), Done($a), Fail(), Done($b)].whereType<Done>().length);", 2, "whereType<Done> keeps the two Done objects."),
    D(ST + "\nvoid main() => print(<T>[Wait(), Done($a), Fail(), Done($b)].where((s) => s is! Wait).length);", 3, "is! keeps everything that is not a Wait."),
    D(ST + "\nvoid main() => print(<T>[Done($a), Fail(), Done($b)].whereType<Done>().map((d) => d.n).join(','));", lambda p: f"{p['a']},{p['b']}", "Only the Done objects stay, and their n values are joined."),
    # ── the same patterns on other values ──
    _fn("String f(int x)", "< 0 => 'neg', 0 => 'zero', > 0 && < 10 => 'small', _ => 'big'", "f(-$a)", "neg", "The first arm is a relational pattern: below 0."),
    _fn("String f(int x)", "< 0 => 'neg', 0 => 'zero', > 0 && < 10 => 'small', _ => 'big'", "f(0)", "zero", "0 matches the constant pattern."),
    _fn("String f(int x)", "< 0 => 'neg', 0 => 'zero', > 0 && < 10 => 'small', _ => 'big'", "f($a)", "small", "&& needs both tests: above 0 and below 10."),
    _fn("String f(int x)", "< 0 => 'neg', 0 => 'zero', > 0 && < 10 => 'small', _ => 'big'", "f($n)", "big", "Ten and over matches none of the first arms."),
    _fn("String f(int x)", "1 || 2 || 3 => 'low', >= 4 && <= 6 => 'mid', _ => 'high'", "f($a)", lambda p: "low" if p["a"] <= 3 else ("mid" if p["a"] <= 6 else "high"), "|| lists values; && joins two tests into a range."),
    _fn("String f(int x)", "> 5 => 'a', > 2 => 'b', _ => 'c'", "f($a)", lambda p: "a" if p["a"] > 5 else ("b" if p["a"] > 2 else "c"), FIRST),
    _fn("String f(int x)", "int y when y.isEven => 'even', _ => 'odd'", "f($a)", lambda p: "even" if p["a"] % 2 == 0 else "odd", "A guard can use the variable the pattern just bound."),
    _fn("int f(List<int> x)", "[] => 0, [var p] => p, [var p, var q] => p + q, [var p, ..., var q] => p * q", "f([$a, $b])", lambda p: p["a"] + p["b"], "Two items match the third arm, before the arm with the dots."),
    _fn("int f(List<int> x)", "[] => 0, [var p] => p, [var p, var q] => p + q, [var p, ..., var q] => p * q", "f([$a, $b, $c])", lambda p: p["a"] * p["c"], "Three items match only the last arm: the first times the last."),
    _fn("int f(List<int> x)", "[] => 0, [var p] => p, [var p, var q] => p + q, [var p, ..., var q] => p * q", "f([$a])", lambda p: p["a"], "One item matches the second arm."),
    _fn("int f(List<int> x)", "[] => 0, [var p] => p, [var p, var q] => p + q, [var p, ..., var q] => p * q", "f([])", 0, "The empty list matches []."),
    _fn("int f(List<int> x)", "[var p, ...] => p, _ => -1", "f([$a, $b, $c])", lambda p: p["a"], "The dots stand for any number of items."),
    _fn("int f(List<int> x)", "[..., var p] => p, _ => -1", "f([$a, $b, $c])", lambda p: p["c"], "The pattern takes the last item."),
    _fn("int f(List<int> x)", "[..., var p] => p, _ => -1", "f([])", -1, "An empty list has no last item, so _ matches."),
    D("String f(int? x) => switch (x) { null => 'none', int v => 'v' + v.toString() };\nf($a)", lambda p: f"v{p['a']}", "A non-null int matches the second arm."),
    D("String f(int? x) => switch (x) { null => 'none', int v => 'v' + v.toString() };\nf(null)", "none", "null matches the null pattern."),
    D("String f(bool a, bool b) => switch ((a, b)) { (true, true) => 'both', (true, false) || (false, true) => 'one', (false, false) => 'none' };\nf($a > $b, $c > $d)", lambda p: ("both" if (p["a"] > p["b"]) and (p["c"] > p["d"]) else "none" if not (p["a"] > p["b"]) and not (p["c"] > p["d"]) else "one"), "A record of two bools has four cases, and || joins two of them."),
    D("String f(String s) => switch (s) { 'a' => 'A', 'b' => 'B', _ => '?' };\nf('$x')", lambda p: {"a": "A", "b": "B"}.get(p["x"], "?"), "String constants are patterns too."),
    D("var r = (x: $a, y: $a);\nvar s = switch (r) { (x: var p, y: var q) when p == q => 'diag', (x: var p, y: _) when p > $c => 'right', _ => 'other' };\ns", "diag", "The guard p == q is true, and the arms are tried in order."),
    D("var r = (x: $a, y: $b);\nvar s = switch (r) { (x: var p, y: var q) when p == q => 'diag', (x: var p, y: _) when p > $c => 'right', _ => 'other' };\ns", lambda p: "right" if p["a"] > p["c"] else "other", "The first guard fails (the numbers differ), so the second guard asks p > c."),
    D("var m = {'k': $a};\nvar o = switch (m) { {'k': var v} => v + 1, _ => 0 };\no", lambda p: p["a"] + 1, "A map pattern takes the value stored under a key."),
]
