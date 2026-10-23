"""Dart flow pack, part 7: Control Flow - loops, labels, switches, ternaries, collection-for: what ends up printed?

Almost every template is the BODY of main whose last line is a `print(...)` of one value (oracle `value`). The model
is a Python loop that does what the Dart loop does, written out step by step, plus these Dart rules:

* a `switch` case does NOT fall through to the next one (Dart 3): only the case that matches runs; cases with no
  statements of their own are grouped with the next one; `continue label` jumps on to another case on purpose;
* `break` inside a `switch` leaves the switch (not the loop around it), `continue` goes on with the loop;
* a labelled `break`/`continue` leaves/continues the OUTER loop; a `do ... while` body runs at least once;
* `for (var i...)` gives each turn its own `i` (a closure made in the turn keeps that turn's value), a `while` loop's
  variable is one shared variable; `i++` is the old value, `++i` the new one; `?:` is the loosest operator;
* `assert` is switched OFF by `dart run` (and on in Flutter debug builds), so no template relies on it.
"""

from __future__ import annotations

from ._dart_model import DSet, dmod, tdiv_
from ._dartflow_model import F
from ._model import Maker


def C(fmt: str, solve, why: str, pre=None) -> Maker:
    return F(fmt, solve, why, pre)


def pre_ab(p, rng):
    p["a"], p["b"] = rng.sample(range(2, 8), 2)


def pre_n_small(p, rng):
    p["n"] = rng.randint(7, 14)


def pre_k12(p, rng):
    p["k"] = rng.randint(1, 2)


def pre_case(p, rng):
    p["c"] = rng.randint(1, 4)


def pre_word(p, rng):
    p["w"] = rng.choice(["carrot", "pumpkin", "barn", "maple", "robot", "cloud", "brick", "stone", "river"])


def pre_digits(p, rng):
    p["m"] = rng.randint(100, 9999)


def pre_ladder(p, rng):
    p["n"] = rng.randint(5, 39)


def digit_sum(n: int) -> int:
    t = 0
    while n > 0:
        t += n % 10
        n //= 10
    return t


def two_vars(n: int, di: int, dj: int, want: str):
    """for (var i = 0, j = n; i < j; i += di, j -= dj): the count of turns, the last i or the last j."""
    i, j, count = 0, n, 0
    while i < j:
        count += 1
        i += di
        j -= dj
    return {"count": count, "i": i, "j": j}[want]


CONTROL: list[Maker] = [
    # ── loops and counters ──
    C("var c = 0;\nfor (var i = 0, j = $n; i < j; i += $a, j -= $b) c++;\nprint(c);", lambda p: two_vars(p["n"], p["a"], p["b"], "count"),
      "Both i and j change at the end of every turn; count the turns until i reaches j."),
    C("var i = 0, j = $n;\nfor (; i < j; i += $a, j -= $b) {}\nprint('$$i $$j');", lambda p: f"{two_vars(p['n'], p['a'], p['b'], 'i')} {two_vars(p['n'], p['a'], p['b'], 'j')}",
      "The loop stops as soon as i is no longer below j; both have been changed once more on the last turn."),
    C("var i = $n;\nwhile (i > $a) i -= $b;\nprint(i);", lambda p: _while_sub(p["n"], p["a"], p["b"]),
      "Keep subtracting b while i is still above a; the last i is the answer.", pre_ab),
    C("var i = $n;\ndo {\n  i += $a;\n} while (i < $b);\nprint(i);", lambda p: p["n"] + p["a"],
      "A do-while runs its body once before it looks at the condition, even though the condition is already false."),
    C("var i = 0;\nwhile (i++ < $a) {}\nprint(i);", lambda p: p["a"] + 1,
      "i++ compares the OLD value, then adds one. The last test fails with i at a, but i is already a + 1."),
    C("var i = $a;\nvar r = i++ + ++i;\nprint(r);", lambda p: p["a"] + (p["a"] + 2),
      "i++ gives the old value a and makes i = a + 1; ++i then makes it a + 2 and gives that."),
    C("var i = $a;\nvar x = i++;\nvar y = ++i;\nprint('$$x $$y $$i');", lambda p: f"{p['a']} {p['a'] + 2} {p['a'] + 2}",
      "x gets the old value; y gets the value after the second increment; i ends at a + 2."),
    C("var s = 0;\nfor (var i = 0; i < $n; i += $a) {\n  s += i;\n}\nprint(s);", lambda p: sum(range(0, p["n"], p["a"])),
      "The loop adds 0, a, 2a, ... while i is below n."),
    C("var s = 0;\nfor (var i = 1; i <= $a; i++) {\n  for (var j = i; j <= $a; j++) s++;\n}\nprint(s);", lambda p: sum(p["a"] - i + 1 for i in range(1, p["a"] + 1)),
      "The inner loop starts at i, so it gets shorter each turn: a + (a-1) + ... + 1."),
    C("var c = 0, i = 1;\nwhile (i < $n) {\n  i *= 2;\n  c++;\n}\nprint(c);", lambda p: _doublings(p["n"]),
      "Count how many doublings it takes to reach n."),
    C("var n = $m, s = 0;\nwhile (n > 0) {\n  s += n % 10;\n  n ~/= 10;\n}\nprint(s);", lambda p: digit_sum(p["m"]),
      "% 10 takes the last digit and ~/ 10 drops it: the digits are added up.", pre_digits),
    C("var n = $a, f = 1;\nwhile (n > 1) f *= n--;\nprint(f);", lambda p: _factorial(p["a"]),
      "f is multiplied by n, then n goes down by one: the factorial."),
    C("var s = '';\nfor (var i = $b; i > 0; i -= 2) {\n  s += '$$i';\n}\nprint(s);", lambda p: "".join(str(i) for i in range(p["b"], 0, -2)),
      "Count down by two, writing each i."),
    C("var s = '';\nfor (var i = 0; i < 6; i++) {\n  s += '$$i';\n  i++;\n}\nprint(s);", lambda p: "024",
      "The body also adds one to i, so the loop only sees every other number."),
    C("var t = 0;\nfor (var i = 1; i <= $n; i++) {\n  if (i % 2 == 0) continue;\n  if (i > $b + 3) break;\n  t += i;\n}\nprint(t);",
      lambda p: _sum_odd_until(p["n"], p["b"] + 3), "continue skips the even numbers; break ends the loop at the first number above the limit.", pre_ab),
    C("var c = 0;\nfor (var i = 1; i <= $a; i++) {\n  for (var j = 1; j <= $b; j++) {\n    if (j > i) break;\n    c++;\n  }\n}\nprint(c);",
      lambda p: sum(min(i, p["b"]) for i in range(1, p["a"] + 1)), "break leaves only the inner loop: each i counts j = 1 up to min(i, b).", pre_ab),
    C("var c = 0;\nouter:\nfor (var i = 0; i < $a; i++) {\n  for (var j = 0; j < $b; j++) {\n    if (j == 1) continue outer;\n    c++;\n  }\n}\nprint(c);",
      lambda p: p["a"], "continue outer starts the next i at once, so each i counts only j = 0.", pre_ab),
    C("var c = 0;\nouter:\nfor (var i = 0; i < $a; i++) {\n  for (var j = 0; j < $b; j++) {\n    if (i == 1 && j == 1) break outer;\n    c++;\n  }\n}\nprint(c);",
      lambda p: p["b"] + 1, "break outer ends both loops: all of i = 0 (b turns) and the j = 0 turn of i = 1.", pre_ab),
    C("var c = 0;\nfor (;;) {\n  c += $a;\n  if (c > $n) break;\n}\nprint(c);", lambda p: _until_over(p["a"], p["n"]),
      "for (;;) never ends by itself; the break ends it at the first c above n."),
    C("var i = 0, c = 0;\ndo {\n  i++;\n  if (i.isOdd) continue;\n  c += i;\n} while (i < $n);\nprint(c);", lambda p: sum(x for x in range(1, p["n"] + 1) if x % 2 == 0),
      "In a do-while, continue jumps to the condition check, so the loop still ends at n.", pre_n_small),
    C("var c = 0;\nfor (var ch in '$w'.split('')) {\n  if ('aeiou'.contains(ch)) c++;\n}\nprint(c);", lambda p: sum(1 for ch in p["w"] if ch in "aeiou"),
      "Count the vowels of the word.", pre_word),
    C("var s = '';\nfor (var i = 0; i < '$w'.length; i++) {\n  s = '$w'[i] + s;\n}\nprint(s);", lambda p: p["w"][::-1],
      "Each letter is put in FRONT of what is already built, so the word comes out reversed.", pre_word),
    C("var s = '';\nfor (var i = 0; i < '$w'.length; i += 2) {\n  s += '$w'[i];\n}\nprint(s);", lambda p: p["w"][::2],
      "Every second letter, starting with the first.", pre_word),
    # ── closures in loops ──
    C("var fs = <int Function()>[];\nfor (var i = 0; i < $k + 2; i++) {\n  fs.add(() => i);\n}\nprint(fs.map((f) => f()).toList());", lambda p: list(range(p["k"] + 2)),
      "A for loop gives every turn its own i, so each closure keeps its own number."),
    C("var fs = <int Function()>[];\nvar i = 0;\nwhile (i < $k + 2) {\n  fs.add(() => i);\n  i++;\n}\nprint(fs.map((f) => f()).toList());", lambda p: [p["k"] + 2] * (p["k"] + 2),
      "A while loop has ONE shared i; all the closures see its final value."),
    C("var fs = <int Function()>[];\nvar i = 0;\nwhile (i < $k + 2) {\n  var j = i;\n  fs.add(() => j);\n  i++;\n}\nprint(fs.map((f) => f()).toList());", lambda p: list(range(p["k"] + 2)),
      "j is declared inside the body, so every turn has its own j."),
    # ── ternary and ?? ──
    C("var x = $n;\nprint(x > 20 ? x > 30 ? 'a' : 'b' : 'c');", lambda p: ("a" if p["n"] > 30 else "b") if p["n"] > 20 else "c",
      "Read from the left: x > 20 picks the first part, which is itself a ternary."),
    C("print($a > $b ? $c : $d + 1);", lambda p: p["c"] if p["a"] > p["b"] else p["d"] + 1, "?: is the loosest operator, so the + 1 belongs to the else part only."),
    C("print(($a > $b ? $c : $d) + 1);", lambda p: (p["c"] if p["a"] > p["b"] else p["d"]) + 1, "With brackets, the + 1 is added to whichever part was picked."),
    C("String? a = null;\nString? b = '$w';\nprint(a ?? b ?? '$v');", lambda p: p["w"], "?? goes along the chain and stops at the first value that is not null."),
    C("String? a = null;\nString? b = null;\nprint(a ?? b ?? '$v');", lambda p: p["v"], "Both are null, so the last fallback is used."),
    C("int? a;\nint? b = $a;\nprint(a ?? b ?? 0);", lambda p: p["a"], "a is null, b is not."),
    C("var n = 0;\nbool no() {\n  n++;\n  return false;\n}\nif (no() && no()) {}\nprint(n);", lambda p: 1, "&& stops at the first false, so no() runs once."),
    C("var n = 0;\nbool no() {\n  n++;\n  return false;\n}\nif (no() || no()) {}\nprint(n);", lambda p: 2, "|| must try the second when the first is false: two calls."),
    C("var n = 0;\nbool yes() {\n  n++;\n  return true;\n}\nif (yes() || yes()) {}\nprint(n);", lambda p: 1, "|| stops at the first true."),
    C("var n = 0;\nbool yes() {\n  n++;\n  return true;\n}\nif (yes() && yes() && yes()) {}\nprint(n);", lambda p: 3, "&& goes on while it is true: three calls."),
    C("var s = $n;\nString g;\nif (s >= 30) {\n  g = 'A';\n} else if (s >= 20) {\n  g = 'B';\n} else if (s >= 10) {\n  g = 'C';\n} else {\n  g = 'D';\n}\nprint(g);",
      lambda p: "A" if p["n"] >= 30 else "B" if p["n"] >= 20 else "C" if p["n"] >= 10 else "D", "The first condition that is true wins, and the rest are skipped.", pre_ladder),
    # ── switch ──
    C("var n = $c;\nvar s = '';\nswitch (n) {\n  case 1:\n    s += '$s1';\n  case 2:\n    s += '$s2';\n  case 3:\n    s += '$s3';\n  default:\n    s += '$s4';\n}\nprint(s);",
      lambda p: p["s%d" % (p["c"] if p["c"] <= 3 else 4)], "A matching case runs alone: Dart cases do not fall through.", pre_case),
    C("var n = $c;\nvar s = '';\nswitch (n) {\n  case 1:\n  case 2:\n    s = '$s1';\n  case 3:\n    s = '$s2';\n  default:\n    s = '$s3';\n}\nprint(s);",
      lambda p: p["s1"] if p["c"] in (1, 2) else p["s2"] if p["c"] == 3 else p["s3"], "A case with no statements shares the next case's code (1 and 2 together).", pre_case),
    C("var n = $c;\nvar s = '';\nswitch (n) {\n  case 1:\n    s += '$s1';\n    continue next;\n  next:\n  case 2:\n    s += '$s2';\n  default:\n    s += '$s3';\n}\nprint(s);",
      lambda p: p["s1"] + p["s2"] if p["c"] == 1 else p["s2"] if p["c"] == 2 else p["s3"], "continue next jumps on to the labelled case on purpose; nothing else falls through.", pre_case),
    C("var s = '';\nfor (var i = 0; i < 4; i++) {\n  switch (i) {\n    case $k:\n      break;\n    case 3:\n      continue;\n    default:\n      s += '$$i';\n  }\n  s += '-';\n}\nprint(s);",
      lambda p: "".join(("-" if i == p["k"] else "" if i == 3 else str(i) + "-") for i in range(4)),
      "break only leaves the switch, so the dash is still added; continue skips the rest of the loop body, dash included.", pre_k12),
    C("var c = 0;\nloop:\nfor (var i = 0; i < 6; i++) {\n  switch (i) {\n    case $a:\n      break loop;\n    default:\n      c++;\n  }\n}\nprint(c);",
      lambda p: p["a"] if p["a"] < 6 else 6, "break loop leaves the for loop itself; plain break would only leave the switch."),
    C("var n = $c;\nprint(switch (n) { 1 => '$s1', 2 || 3 => '$s2', > 3 => '$s3', _ => '$s4' });",
      lambda p: p["s1"] if p["c"] == 1 else p["s2"] if p["c"] in (2, 3) else p["s3"], "A switch expression picks the first pattern that fits: 2 || 3 matches either; > 3 matches bigger numbers.", pre_case),
    C("var n = $n;\nprint(switch (n) { int m when m.isOdd => 'odd$$m', _ => 'even' });", lambda p: ("odd" + str(p["n"])) if p["n"] % 2 else "even",
      "int m when m.isOdd matches odd numbers and names the value m; everything else falls to _."),
    C("var t = '$w';\nprint(switch (t) { 'barn' => 1, 'maple' => 2, _ => 0 });", lambda p: {"barn": 1, "maple": 2}.get(p["w"], 0), "A switch can match strings too; _ is the catch-all.", pre_word),
    C("enum Dir { up, down }\nvoid main() {\n  var d = Dir.$d1;\n  print(switch (d) { Dir.up => '$s1', Dir.down => '$s2' });\n}", lambda p: p["s1"] if p["d1"] == "up" else p["s2"],
      "An enum switch expression must cover every value, and picks the one that matches.", lambda p, rng: p.update(d1=rng.choice(["up", "down"]))),
    # ── patterns, collection-for/if ──
    C("var (a, b) = ($a, $b);\n(a, b) = (b, a);\nprint('$$a-$$b');", lambda p: f"{p['b']}-{p['a']}", "The record on the right is built first, then handed out: a swap."),
    C("print([for (var i = 0; i < $n; i++) if (i.isEven) i * i]);", lambda p: [i * i for i in range(p["n"]) if i % 2 == 0],
      "A collection-for with a collection-if inside: only the even i are squared and kept.", pre_n_small),
    C("print([for (var i = 1; i <= $b; i++) i * $a]);", lambda p: [i * p["a"] for i in range(1, p["b"] + 1)], "A collection-for builds the list from the loop.", pre_ab),
    C("print({for (var i = 1; i <= 5; i++) i % $a});", lambda p: DSet(i % p["a"] for i in range(1, 6)), "In a set, repeated values are kept once."),
    C("print({for (var i = 1; i <= $k + 1; i++) i: i * i});", lambda p: {i: i * i for i in range(1, p["k"] + 2)}, "A map built with collection-for."),
    C("var xs = [$a, $b, $c, $d];\nprint([for (var x in xs) if (x > 5) x]);", lambda p: [x for x in (p["a"], p["b"], p["c"], p["d"]) if x > 5], "Only the items above 5 are kept."),
    C("var more = $a > $b;\nprint([1, if (more) 2, 3]);", lambda p: [1, 2, 3] if p["a"] > p["b"] else [1, 3], "A collection-if adds its item only when the condition is true."),
    C("var more = $a > $b;\nprint([1, if (more) 2 else 9, 3]);", lambda p: [1, 2, 3] if p["a"] > p["b"] else [1, 9, 3], "With else, one of the two items is always added."),
    C("var xs = [1, 2];\nvar ys = [3];\nprint([...xs, if (xs.length > $k) ...ys, 4]);", lambda p: [1, 2, 3, 4] if 2 > p["k"] else [1, 2, 4],
      "The spread inside collection-if adds all of ys, but only when the condition holds."),
    # ── functions and early exit ──
    C("var s = '';\n[1, 2, 3].forEach((x) {\n  if (x == $k) return;\n  s += '$$x';\n});\nprint(s);", lambda p: "".join(str(x) for x in (1, 2, 3) if x != p["k"]),
      "return inside the closure only leaves the closure for that item; forEach goes on with the next."),
    C("int firstEven(List<int> xs) {\n  for (var x in xs) {\n    if (x.isEven) return x;\n  }\n  return -1;\n}\nprint(firstEven([$a, $b, $c, $d]));",
      lambda p: next((x for x in (p["a"], p["b"], p["c"], p["d"]) if x % 2 == 0), -1), "return leaves the whole function at the first even number, or -1 if there is none."),
    C("var x = $n;\nx ~/= $a;\nx %= $b;\nx += 1;\nprint(x);", lambda p: dmod(tdiv_(p["n"], p["a"]), p["b"]) + 1, "Each compound assignment updates x in turn: divide, remainder, add one.", pre_ab),
]


def _while_sub(n: int, a: int, b: int) -> int:
    i = n
    while i > a:
        i -= b
    return i


def _doublings(n: int) -> int:
    i, c = 1, 0
    while i < n:
        i *= 2
        c += 1
    return c


def _factorial(n: int) -> int:
    f = 1
    while n > 1:
        f *= n
        n -= 1
    return f


def _sum_odd_until(n: int, limit: int) -> int:
    t = 0
    for i in range(1, n + 1):
        if i % 2 == 0:
            continue
        if i > limit:
            break
        t += i
    return t


def _until_over(a: int, n: int) -> int:
    c = 0
    while True:
        c += a
        if c > n:
            return c
