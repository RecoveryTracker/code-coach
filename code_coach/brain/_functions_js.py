"""Functions and scope pack, JavaScript side: the same eight activities with JavaScript's rules.

Every answer is modelled by hand and tests/test_brain_packs.py runs every
template through the real node. The prompt's last line is an expression and
its value is the answer. Templates use the same table rows as the Python side
(`trow`, `prow`: see _functions_py.py for the $holes); JavaScript's own
differences - var against let, defaults evaluated on every call, arguments,
the arrays node prints as `[ 1, 2 ]` - are the point.
"""

from __future__ import annotations

import random
from string import Template

from . import _functions_py as P
from ._functions_py import (T, biggest, bits, checks_until_big, collatz, count_in, digit_sum, fact, fact_calls, fib,
                            fib_calls, fold, gcd, halvings, hanoi, is_palindrome, popcount, tree_calls)
from ._model import NULL, Maker, isort, js_show, tmod
from .items import Item

UNDEF = "undefined"


def _js_bool(b: bool) -> str:
    return "true" if b else "false"


# ── 1. Which x ──────────────────────────────────────────────────────────

SCOPE = [
    T("let x = $a;\nfunction f() {\n  return x;\n}\nf();", lambda p: p["a"],
      "f makes no x of its own, so it reads the outer x."),
    T("let x = $a;\nfunction f() {\n  let x = $b;\n  return x;\n}\nf();", lambda p: p["b"],
      "let inside f makes a new x that hides the outer one."),
    T("let x = $a;\nfunction f() {\n  let x = $b;\n}\nf();\nx;", lambda p: p["a"],
      "The x inside f is a separate variable; the outer x never changed."),
    T("let x = $a;\nfunction f() {\n  x = $b;\n}\nf();\nx;", lambda p: p["b"],
      "There is no let inside f, so x = ... assigns to the outer x."),
    T("var x = $a;\nfunction f() {\n  var x = $b;\n}\nf();\nx;", lambda p: p["a"],
      "var inside f makes a variable that belongs to f."),
    T("let x = $a;\n{\n  let x = $b;\n}\nx;", lambda p: p["a"],
      "let belongs to its { } block, so the block's x is gone afterwards."),
    T("var x = $a;\n{\n  var x = $b;\n}\nx;", lambda p: p["b"],
      "var ignores blocks: it is the same x, so the block changed it."),
    T("let x = $a;\nif (x > 1) {\n  let x = $b;\n}\nx;", lambda p: p["a"],
      "The let inside the if block is a different x."),
    T("let x = $a;\nif (x > 1) {\n  x = $b;\n}\nx;", lambda p: p["b"],
      "No let in the block, so it assigns the outer x."),
    T("for (let i = 0; i < $m; i++) {}\ntypeof i;", UNDEF,
      "let keeps i inside the loop, so outside there is no i."),
    T("for (var i = 0; i < $m; i++) {}\ni;", lambda p: p["m"],
      "var leaks out of the loop, and i stopped at $m."),
    T("if (true) {\n  var y = $a;\n}\ny;", lambda p: p["a"],
      "var is not block scoped, so y is still there after the if."),
    T("if (true) {\n  let y = $a;\n}\ntypeof y;", UNDEF,
      "let y lives only inside the block."),
    T("let x = $a;\nfunction f(x) {\n  return x * 2;\n}\nf($b);", lambda p: p["b"] * 2,
      "The parameter x hides the outer x."),
    T("let x = $a;\nfunction f(x) {\n  x = x + 1;\n  return x;\n}\nf($b);\nx;", lambda p: p["a"],
      "Changing the parameter x never touches the outer x."),
    T("function outer() {\n  let x = $a;\n  function inner() {\n    return x + $b;\n  }\n  return inner();\n}\nouter();",
      lambda p: p["a"] + p["b"], "inner reads x from the function around it."),
    T("function outer() {\n  let x = $a;\n  function inner() {\n    x = $b;\n  }\n  inner();\n  return x;\n}\nouter();",
      lambda p: p["b"], "inner has no let, so it assigns outer's x: no nonlocal is needed."),
    T("function outer() {\n  let x = $a;\n  function inner() {\n    let x = $b;\n  }\n  inner();\n  return x;\n}\nouter();",
      lambda p: p["a"], "inner's let makes its own x, so outer's x is untouched."),
    T("function f() {\n  const r = x;\n  var x = $a;\n  return r;\n}\nf();", UNDEF,
      "var is hoisted: x exists from the top of f, but holds undefined until its line runs."),
    T("const r = f();\nfunction f() {\n  return $a;\n}\nr;", lambda p: p["a"],
      "A function declaration is hoisted, so it can be called before its line."),
    T("const o = { n: $a };\nfunction f() {\n  o.n = $b;\n}\nf();\no.n;", lambda p: p["b"],
      "f changes the property of the one shared object."),
    T("const x = $a;\nfunction f() {\n  const x = $b;\n  return x;\n}\nf() + x;", lambda p: p["a"] + p["b"],
      "f gives its own x ($b) and the outer x is $a."),
    T("let x = $a;\nfunction f() {\n  return x;\n}\nx = $b;\nf();", lambda p: p["b"],
      "f reads x when it runs, and x is $b by then."),
    T("let x = $a;\nconst f = () => x * 2;\nx = $b;\nf();", lambda p: p["b"] * 2,
      "An arrow function reads the outer x when it runs."),
    T("let x = $a;\nconst f = x => x * 2;\nf($b);", lambda p: p["b"] * 2,
      "The arrow's parameter x hides the outer x."),
    T("let n = $a;\nfunction inc() {\n  n++;\n}\ninc();\ninc();\nn;", lambda p: p["a"] + 2,
      "inc changes the outer n, and it runs twice."),
    T("var x = $a;\nfunction f() {\n  x = $b;\n  var x;\n}\nf();\nx;", lambda p: p["a"],
      "var x inside f is hoisted, so x = $b changes f's own x."),
    T("let x = $a;\ntry {\n  throw 1;\n} catch (x) {\n  x = $b;\n}\nx;", lambda p: p["a"],
      "The catch (x) parameter is its own variable."),
    T("let x = $a;\n{\n  x = $b;\n  {\n    let x = $c;\n  }\n}\nx;", lambda p: p["b"],
      "The inner let x is a new variable; the assignment before it changed the outer x."),
    T("let total = 0;\nfor (const v of [$a, $b, $c]) {\n  total += v;\n}\ntotal;", lambda p: p["a"] + p["b"] + p["c"],
      "total is outside the loop, so every += adds to the same total."),
    T("let i = $a;\nfor (let i = 0; i < 3; i++) {}\ni;", lambda p: p["a"],
      "The loop's let i is its own variable."),
    T("let x = $a;\nfunction f() {\n  x++;\n  return x;\n}\nf() + f();", lambda p: (p["a"] + 1) + (p["a"] + 2),
      "The outer x goes up by 1 on each call: $a + 1, then $a + 2, added."),
    T('let x = "$w";\nfunction f() {\n  let x = "$v";\n  return x;\n}\nf() + x;', lambda p: p["v"] + p["w"],
      "f gives its own x ($v), then + joins the outer x ($w)."),
]


# ── 2. Default Args ─────────────────────────────────────────────────────

ADD = "function add(x, acc = []) {\n  acc.push(x);\n  return acc;\n}\n"
GREET = 'function greet(name, greeting = "hi") {\n  return greeting + " " + name;\n}\n'
FRESH = "JavaScript works a default out again on every call, so each call gets a new array."

DEFAULTS = [
    T("function f(a, b = $b) {\n  return a + b;\n}\nf($a);", lambda p: p["a"] + p["b"], "b falls back to its default, $b."),
    T("function f(a, b = $b) {\n  return a + b;\n}\nf($a, $c);", lambda p: p["a"] + p["c"], "A value passed in replaces the default."),
    T("function f(a, b = $b) {\n  return a + b;\n}\nf($a, undefined);", lambda p: p["a"] + p["b"],
      "Passing undefined still uses the default."),
    T("function f(a, b = $b) {\n  return a + b;\n}\nf($a, null);", lambda p: p["a"],
      "null is a value, so no default: a + null is a + 0."),
    T(ADD + "add($a);\nadd($b);", lambda p: js_show([p["b"]]), FRESH),
    T(ADD + "add($a);\nadd($b);\nadd($c).length;", lambda p: 1, FRESH),
    T("function f(a, b = a * 2) {\n  return a + b;\n}\nf($a);", lambda p: p["a"] * 3,
      "A default can use an earlier parameter: b is a * 2."),
    T("function f(a, b = a * 2) {\n  return a + b;\n}\nf($a, $c);", lambda p: p["a"] + p["c"],
      "The passed value replaces the default."),
    T("let n = 0;\nconst next = () => ++n;\nfunction f(x = next()) {\n  return x;\n}\nf();\nf($a);\nf();",
      lambda p: 2, "next() runs only when no argument is given: on the 1st and 3rd calls, so the last gives 2."),
    T("let x = $a;\nfunction f(y = x) {\n  return y;\n}\nx = $b;\nf();", lambda p: p["b"],
      "The default is worked out on each call, so it sees the new x."),
    T("let n = 0;\nfunction f(v = ++n) {\n  return v;\n}\nf($a);\nf($b);\nn;", lambda p: 0,
      "The default never ran, because both calls gave a value."),
    T("function f(x = $a) {\n  return x;\n}\nf(undefined);", lambda p: p["a"], "undefined triggers the default."),
    T("function f(x = $a) {\n  return x;\n}\nf(null);", lambda p: js_show(NULL), "null does not trigger the default."),
    T("function f(x = $a) {\n  return x;\n}\nf(0);", lambda p: 0, "0 is a value, so it stays."),
    T("function f(x = $a) {\n  return x;\n}\nf(false);", lambda p: "false", "false is a value, so it stays."),
    T("const f = (a, b = $b) => a * b;\nf($a);", lambda p: p["a"] * p["b"], "An arrow function can have defaults too."),
    T("function f({ x = $a, y = $b } = {}) {\n  return x + y;\n}\nf();", lambda p: p["a"] + p["b"],
      "With no argument the {} is used, and x and y take their defaults."),
    T("function f({ x = $a, y = $b } = {}) {\n  return x + y;\n}\nf({ x: $c });", lambda p: p["c"] + p["b"],
      "x is given; y keeps its default."),
    T("function f(a, b = $b, c = $c) {\n  return a + b + c;\n}\nf($a, undefined, $d);", lambda p: p["a"] + p["b"] + p["d"],
      "undefined in the middle keeps b's default."),
    T("function f(a = $a, b = $b) {\n  return a - b;\n}\nf(undefined, $c);", lambda p: p["a"] - p["c"],
      "undefined asks for a's default."),
    T("function f(a, b = 1) {}\nf.length;", lambda p: 1, "length counts the parameters before the first default."),
    T("function f(x, y = x + 1) {\n  return y;\n}\nf($a);", lambda p: p["a"] + 1, "y defaults to x + 1."),
    T("function f(a, b = $b) {\n  return arguments.length;\n}\nf($a);", lambda p: 1,
      "arguments counts only what was passed, not defaults."),
    T("function f(a, b = $b) {\n  return arguments.length;\n}\nf($a, undefined);", lambda p: 2,
      "undefined was passed, so it counts."),
    T(GREET + 'greet("$w");', lambda p: "hi " + p["w"], 'greeting falls back to "hi".'),
    T(GREET + 'greet("$w", "yo");', lambda p: "yo " + p["w"], "The second argument replaces the default greeting."),
    T("function f(n = [$a, $b]) {\n  n.push($c);\n  return n.length;\n}\nf();\nf();", lambda p: 3,
      "Each call makes a new array, so the second call also ends at 3."),
    T("function f(n) {\n  n = n || $a;\n  return n;\n}\nf(0);", lambda p: p["a"], "|| skips 0, because 0 is falsy."),
    T("function f(n) {\n  n = n ?? $a;\n  return n;\n}\nf(0);", lambda p: 0, "?? only skips null and undefined."),
    T("const f = (a, b = a + $c) => b;\nf($a, $b);", lambda p: p["b"], "b was passed, so its default is not used."),
    T("function f(o = { n: 0 }) {\n  o.n++;\n  return o.n;\n}\nf();\nf();", lambda p: 1,
      "Each call gets a new default object, so n goes from 0 to 1 every time."),
    T("function f(a, b = $b) {\n  return a * b;\n}\nf($a);", lambda p: p["a"] * p["b"], "b uses its default."),
    T("function f(n = $a) {\n  return n * 2;\n}\nf();", lambda p: p["a"] * 2, "No argument: the default is used."),
]


# ── 3. Count the Calls ──────────────────────────────────────────────────

COUNT = "let calls = 0;\nfunction f() {\n  calls++;\n}\n"
SQ = "let calls = 0;\nconst sq = x => {\n  calls++;\n  return x * x;\n};\n"
LOGF = "const log = [];\nconst f = x => {\n  log.push(x);\n  return x;\n};\n"
TICK = "let n = 0;\nconst tick = () => ++n;\n"
HELLO = "let calls = 0;\nconst hello = () => calls++;\nfunction repeat(fn, k) {\n  for (let i = 0; i < k; i++) fn();\n}\n"
BIG = "let calls = 0;\nconst isBig = x => {\n  calls++;\n  return x > 5;\n};\n"


CALLS = [
    T(COUNT + "for (let i = 0; i < $m; i++) {\n  f();\n}\ncalls;", lambda p: p["m"], "The loop calls f once per turn."),
    T(COUNT + "for (let i = 0; i < $a; i++) {\n  f();\n}\ncalls;", lambda p: p["a"], "The loop calls f once per turn: $a turns."),
    T("let n = 0;\nfunction down(k) {\n  n++;\n  if (k > 0) down(k - 1);\n}\ndown($a);\nn;", lambda p: p["a"] + 1,
      "It runs for $a, then every number below down to 0: one call more than $a."),
    T("let calls = 0;\nfunction fib(n) {\n  calls++;\n  if (n < 2) return n;\n  return fib(n - 1) + fib(n - 2);\n}\nfib($s);\ncalls;",
      lambda p: fib_calls(p["s"]), "Each call below 2 stops; every other one makes two more calls."),
    T("let calls = 0;\nfunction fact(n) {\n  calls++;\n  if (n <= 1) return 1;\n  return n * fact(n - 1);\n}\nfact($a);\ncalls;",
      lambda p: fact_calls(p["a"]), "One call for each of $a, $a - 1, ... down to 1."),
    T('let out = "";\nconst f = c => out += c;\nconst g = () => {\n  f("$p");\n  f("$q");\n};\ng();\ng();\nout;',
      lambda p: p["p"] + p["q"] + p["p"] + p["q"], "Each g() adds $p then $q, and g runs twice."),
    T(LOGF + "f(0) && f($a);\nlog.length;", lambda p: 1, "f(0) is falsy, so && skips the second call."),
    T(LOGF + "f($a) && f($b);\nlog.length;", lambda p: 2, "f($a) is truthy, so && goes on to the second call."),
    T(LOGF + "f($a) || f($b);\nlog.length;", lambda p: 1, "f($a) is truthy, so || stops: the second call never happens."),
    T(LOGF + "f(0) || f($a);\nlog.length;", lambda p: 2, "f(0) is falsy, so || goes on to the second call."),
    T(LOGF + "f(null) ?? f($a);\nlog.length;", lambda p: 2, "f(null) gives null, so ?? goes on to the second call."),
    T(LOGF + "f(0) ?? f($a);\nlog.length;", lambda p: 1, "0 is not null or undefined, so ?? stops."),
    T(LOGF + "f($a) + f($b) * f($c);\nlog;", lambda p: js_show([p["a"], p["b"], p["c"]]),
      "The calls happen left to right, whatever the operators."),
    T("let calls = 0;\nconst ok = i => {\n  calls++;\n  return i < $m;\n};\nlet i = 0;\nwhile (ok(i)) i++;\ncalls;",
      lambda p: p["m"] + 1, "The test runs once for each pass, plus the final test that fails."),
    T(SQ + "[$a, $b, $c].map(sq);\ncalls;", lambda p: 3, "map calls sq once for each item."),
    T(SQ + "[$a, $b, $c, $d].filter(x => sq(x) > 20);\ncalls;", lambda p: 4, "filter tests every item, so sq runs 4 times."),
    T("const seen = new Set();\nlet calls = 0;\nfunction f(n) {\n  if (!seen.has(n)) calls++;\n  seen.add(n);\n}\nf($a);\nf($b);\nf($a);\ncalls;",
      lambda p: 2, "The repeat of $a is already in the set, so it is not counted."),
    T("function dive(n, depth = 1) {\n  return n === 0 ? depth : dive(n - 1, depth + 1);\n}\ndive($a);",
      lambda p: p["a"] + 1, "The calls stack up one deeper each time, $a + 1 deep at the bottom."),
    T("let calls = 0;\nfunction halve(n) {\n  calls++;\n  if (n > 1) halve(Math.floor(n / 2));\n}\nhalve($n);\ncalls;",
      lambda p: halvings(p["n"]), "Count how many times n can be halved before it reaches 1, plus the first call."),
    T("const log = [];\nfunction even(n) { log.push(n); return n === 0 || odd(n - 1); }\nfunction odd(n) { log.push(n); return n !== 0 && even(n - 1); }\neven($s);\nlog.length;",
      lambda p: p["s"] + 1, "They hand over to each other, one call per number from $s down to 0."),
    T('const log = [];\nconst g = () => log.push("$x");\nfunction f() {\n  log.push("$p");\n  g();\n  log.push("$q");\n}\nf();\nlog.join("");',
      lambda p: p["p"] + p["x"] + p["q"], "f logs, calls g, which logs, then f logs again."),
    T('const log = [];\nfunction f(x) { log.push("$p"); return x; }\nfunction g(x) { log.push("$q"); return x; }\ng(f($a));\nlog.join("");',
      lambda p: p["p"] + p["q"], "The argument f($a) is worked out before g can run."),
    T(LOGF + "Math.max(f($a), f($b), f($c));\nlog.length;", lambda p: 3, "All three arguments are worked out before max looks at them."),
    T(LOGF + "[0, $a, $b].some(f);\nlog.length;", lambda p: 2, "some stops at the first truthy result, so $b is never reached."),
    T(LOGF + "[$a, 0, $b].every(f);\nlog.length;", lambda p: 2, "every stops at the first falsy result."),
    T(LOGF + "[$a, $b, $c, $d].find(f);\nlog.length;", lambda p: 1, "The first item is truthy, so find stops at once."),
    T(LOGF + "[$a, $b, $c].forEach(f);\nlog.length;", lambda p: 3, "forEach calls f once for each item."),
    T(BIG + "[$a, $b, $c, $d].find(isBig);\ncalls;", lambda p: checks_until_big([p["a"], p["b"], p["c"], p["d"]], 5),
      "find stops at the first value over 5."),
    T(TICK + "[tick(), tick(), tick()];", lambda p: js_show([1, 2, 3]), "Each tick() adds 1 and gives the new n, in order."),
    T(TICK + "tick() * 10 + tick();", lambda p: 12, "The first tick() is 1, the second is 2: 1 * 10 + 2."),
    T(TICK + "tick() - tick();", lambda p: -1, "The left call happens first: 1 - 2."),
    T(TICK + "tick();\ntick();\ntick() * $a;", lambda p: 3 * p["a"], "The third tick() gives 3."),
    T(HELLO + "repeat(hello, $a);\ncalls;", lambda p: p["a"], "repeat calls the function it was given $a times."),
    T(HELLO + "repeat(hello, $a);\nrepeat(hello, $b);\ncalls;", lambda p: p["a"] + p["b"], "$a calls, then $b more."),
    T(COUNT + "for (let i = 0; i < $m; i++) {\n  for (let j = 0; j < $r; j++) f();\n}\ncalls;", lambda p: p["m"] * p["r"],
      "$r calls on each of $m turns of the outer loop."),
    T("let calls = 0;\nfunction f(n) {\n  calls++;\n  if (n > 0) { f(n - 1); f(n - 1); }\n}\nf($r);\ncalls;",
      lambda p: tree_calls(p["r"]), "Every call above 0 makes two more, so the count roughly doubles each level."),
    T("let moves = 0;\nfunction hanoi(n) {\n  if (n === 0) return;\n  hanoi(n - 1);\n  moves++;\n  hanoi(n - 1);\n}\nhanoi($m);\nmoves;",
      lambda p: hanoi(p["m"]), "Each level does its own move between two copies of the level below."),
    T("let n = 0;\nconst c = () => n++;\nconst b = () => {\n  c();\n  c();\n};\nfor (let i = 0; i < $r; i++) b();\nn;",
      lambda p: 2 * p["r"], "b runs $r times, and each b calls c twice."),
    T("let calls = 0;\nfunction make() { calls++; return []; }\nfunction f(x = make()) { return x; }\nf();\nf();\nf();\ncalls;",
      lambda p: 3, "JavaScript works the default out on every call that leaves it out: 3 calls."),
    T("let calls = 0;\nfunction make() { calls++; return []; }\nfunction f(x = make()) { return x; }\nf();\nf([]);\nf();\ncalls;",
      lambda p: 2, "make() runs only on the calls that give no argument."),
    T(COUNT + "const g = () => f();\ncalls;", lambda p: 0, "Making an arrow function does not call anything."),
    T(COUNT + "const g = () => f();\ng();\ng();\ncalls;", lambda p: 2, "Each g() calls f once."),
    T(COUNT + "const x = f;\nconst y = f();\ncalls;", lambda p: 1, "x = f only gives f another name; f() is the one call."),
    T("let calls = 0;\nconst add = (s, x) => {\n  calls++;\n  return s + x;\n};\n[$a, $b, $c, $d].reduce(add);\ncalls;",
      lambda p: 3, "With no starting value the first item is the start, so add runs once fewer than the items."),
    T("let calls = 0;\nconst add = (s, x) => {\n  calls++;\n  return s + x;\n};\n[$a, $b, $c, $d].reduce(add, 0);\ncalls;",
      lambda p: 4, "With a starting value, add runs once for every item."),
    T(LOGF + "const r = f($b) > $a ? f($a) : f($c);\nlog;",
      lambda p: js_show([p["b"], p["a"] if p["b"] > p["a"] else p["c"]]),
      "The test runs first; then only the branch that was chosen."),
]


# ── 4. Closure Counter ──────────────────────────────────────────────────

MAKE = "function make(n = 0) {\n  return () => ++n;\n}\n"
ACC = "function acc() {\n  let total = 0;\n  return v => total += v;\n}\n"
VAR_FS = "const fs = [];\nfor (var i = 0; i < $m; i++) {\n  fs.push(() => i);\n}\n"
LET_FS = "const fs = [];\nfor (let i = 0; i < $m; i++) {\n  fs.push(() => i);\n}\n"
FRESH_N = "Each call of make builds its own n, so the counters do not share."

CLOSURE = [
    T(MAKE + "const c = make();\nc();\nc();\nc();", lambda p: 3, "Each call adds 1 to the n that the arrow remembers."),
    T(MAKE + "const c = make($a);\nfor (let i = 0; i < $m; i++) c();\nc();", lambda p: p["a"] + p["m"] + 1,
      "n starts at $a and the closure adds 1 on each of its $m + 1 calls."),
    T("function make(step) {\n  let n = 0;\n  return () => n += step;\n}\nconst c = make($b);\nc();\nc();", lambda p: 2 * p["b"],
      "Each call adds $b to the remembered n."),
    T(MAKE + "const c = make();\nconst d = make();\nc();\nc();\nd();", lambda p: 1, FRESH_N),
    T(MAKE + "const c = make();\nconst d = c;\nc();\nd();\nc();", lambda p: 3, "d = c is the very same counter, so all three calls count together."),
    T(VAR_FS + "fs[0]();", lambda p: p["m"], "var makes one i for the whole loop, and it ended on $m."),
    T(LET_FS + "fs[0]();", lambda p: 0, "let makes a fresh i for each turn, so the first arrow keeps 0."),
    T(LET_FS + "fs[1]();", lambda p: 1, "let gives each turn its own i."),
    T(VAR_FS + "fs[0]() + fs[1]();", lambda p: 2 * p["m"], "Both arrows read the one i, which is $m."),
    T(LET_FS + "fs[0]() + fs[1]();", lambda p: 1, "Each arrow kept its own i: 0 + 1."),
    T("const fs = [];\nfor (var i = 0; i < $m; i++) {\n  fs.push((j => () => j)(i));\n}\nfs[0]();", lambda p: 0,
      "The inner function is called at once with the current i, so each arrow keeps its own j."),
    T("const add = n => x => x + n;\nadd($a)($b);", lambda p: p["a"] + p["b"], "The inner arrow remembers n."),
    T("const adders = [1, 2, 3].map(n => x => x + n);\nadders[1]($a);", lambda p: p["a"] + 2, "adders[1] remembers n = 2."),
    T(ACC + "const f = acc();\nf($a);\nf($b);\nf($c);", lambda p: p["a"] + p["b"] + p["c"], "The closure keeps a running total."),
    T("function make() {\n  let n = 0;\n  return { inc() { n++; }, get() { return n; } };\n}\nconst c = make();\nfor (let i = 0; i < $m; i++) c.inc();\nc.get();",
      lambda p: p["m"], "inc and get share the one n."),
    T("const twice = f => x => f(f(x));\ntwice(x => x + $b)($a);", lambda p: p["a"] + 2 * p["b"], "The function is applied twice."),
    T("const compose = (f, g) => x => f(g(x));\nconst inc = x => x + 1;\nconst dbl = x => x * 2;\ncompose(inc, dbl)($a);",
      lambda p: 2 * p["a"] + 1, "dbl runs first, then inc."),
    T("const compose = (f, g) => x => f(g(x));\nconst inc = x => x + 1;\nconst dbl = x => x * 2;\ncompose(dbl, inc)($a);",
      lambda p: 2 * (p["a"] + 1), "inc runs first, then dbl."),
    T('function limit(f, k) {\n  let n = 0;\n  return () => ++n <= k ? f() : "stop";\n}\nconst g = limit(() => $a, 2);\ng();\ng();\ng();',
      lambda p: "stop", "The third call is over the limit of 2."),
    T("let x = $a;\nconst f = () => x;\nx = $b;\nf();", lambda p: p["b"], "The arrow reads x when it is called, not when it was made."),
    T("function make(n) {\n  const f = () => n;\n  n = n + 1;\n  return f;\n}\nmake($a)();", lambda p: p["a"] + 1,
      "f reads n when it runs, after n was changed."),
    T("function make(n) {\n  return () => n++;\n}\nconst c = make($a);\nc();\nc();\nc();", lambda p: p["a"] + 2,
      "n++ gives the old value, so the third call gives $a + 2."),
    T("const fs = [];\n[$a, $b, $c].forEach(v => fs.push(() => v));\nfs[1]();", lambda p: p["b"], "Each callback call has its own v."),
    T("const fs = [];\nfor (const v of [$a, $b, $c]) fs.push(() => v);\nfs[0]();", lambda p: p["a"], "const in a for-of is new on each turn."),
    T(VAR_FS + "fs.map(f => f());", lambda p: js_show([p["m"]] * p["m"]), "Every arrow reads the one i, which is $m."),
    T(LET_FS + "fs.map(f => f());", lambda p: js_show(list(range(p["m"]))), "Each arrow kept its own i."),
    T("function account(balance) {\n  return x => balance += x;\n}\nconst d = account($a * 10);\nd($b);\nd($c);",
      lambda p: p["a"] * 10 + p["b"] + p["c"], "The balance carries over from one deposit to the next."),
    T("function make() {\n  let t = 0;\n  return x => t += x;\n}\nconst s1 = make();\nconst s2 = make();\ns1($a);\ns2($b);",
      lambda p: p["b"], "s2 has its own t, so $a never reached it."),
    T('function make(w) {\n  return () => w + "!";\n}\nmake("$w")();', lambda p: p["w"] + "!", "The arrow remembers w."),
    T('const fs = [];\nfor (var w of ["$w", "$v"]) fs.push(() => w);\nfs[0]();', lambda p: p["v"],
      "var makes one w for the whole loop, and it ended on $v."),
    T("function make() {\n  let n = 0;\n  return function () {\n    n += $a;\n    return n;\n  };\n}\nconst c = make();\nc();\nc();",
      lambda p: 2 * p["a"], "Each call adds $a to the remembered n."),
    T("function make(items) {\n  let i = 0;\n  return () => items[i++];\n}\nconst next = make([$a, $b, $c]);\nnext();\nnext();",
      lambda p: p["b"], "The second call gives the second item."),
    T("function make(items) {\n  let i = 0;\n  return () => items[i++];\n}\nconst next = make([$a, $b]);\nnext();\nnext();\nnext();",
      lambda p: "undefined", "Past the end there is no item."),
    T("let n = 0;\nconst make = () => () => ++n;\nconst c = make();\nconst d = make();\nc();\nd();\nc();", lambda p: 3,
      "Both closures use the one outer n, so all three calls count together."),
    T("const fs = [];\nfor (var i = 0; i < $m; i++) {\n  fs.push(function () { return i * 2; });\n}\nfs[0]();",
      lambda p: 2 * p["m"], "The one shared i ended on $m, so the first function gives $m * 2."),
]


# ── 5. Args Count ───────────────────────────────────────────────────────

REST = "function f(...args) {\n  return args.length;\n}\n"
ARGS_LEN = "function f() {\n  return arguments.length;\n}\n"

ARGS = [
    T(REST + "f($a, $b, $c);", lambda p: 3, "...args collects every argument into an array."),
    T(REST + "f();", lambda p: 0, "With nothing passed, args is empty."),
    T(REST + "f([$a, $b, $c]);", lambda p: 1, "An array passed as it is counts as ONE argument."),
    T(REST + "f(...[$a, $b, $c]);", lambda p: 3, "The spread in a call splits the array into separate arguments."),
    T(REST + "f(...[$a, $b], $c);", lambda p: 3, "Two spread from the array, plus $c."),
    T(REST + 'f(..."$w");', lambda p: len(p["w"]), "A string spreads into its letters."),
    T(REST + "f(...[], ...[$a, $b]);", lambda p: 2, "An empty array adds nothing."),
    T("function f(a, ...rest) {\n  return rest.length;\n}\nf($a, $b, $c, $d);", lambda p: 3, "a takes the first; rest gets the other three."),
    T("function f(a, ...rest) {\n  return rest;\n}\nf($a, $b, $c);", lambda p: js_show([p["b"], p["c"]]), "rest is an array of what is left."),
    T("function f(...nums) {\n  return nums.reduce((s, x) => s + x, 0);\n}\nf($a, $b, $c);", lambda p: p["a"] + p["b"] + p["c"],
      "reduce adds the array up."),
    T(ARGS_LEN + "f($a, $b);", lambda p: 2, "arguments holds what was passed."),
    T("function f(a, b, c) {\n  return arguments.length;\n}\nf($a, $b);", lambda p: 2, "arguments counts what was passed, not the parameters."),
    T("function f(a, b, c) {}\nf.length;", lambda p: 3, "A function's length is its number of parameters."),
    T("function f(a, b) {\n  return b;\n}\nf($a);", lambda p: "undefined", "No second argument was passed, so b is undefined."),
    T("function f(a) {\n  return a;\n}\nf($a, $b);", lambda p: p["a"], "The extra argument is ignored."),
    T("Math.max(...[$a, $b, $c]);", lambda p: biggest([p["a"], p["b"], p["c"]]), "The spread gives max three separate numbers."),
    T("const nums = [$a, $b, $c];\nMath.max(...nums, $d);", lambda p: biggest([p["a"], p["b"], p["c"], p["d"]]), "Four numbers reach max."),
    T("Math.max(...[]);", lambda p: "-Infinity", "max of nothing is -Infinity."),
    T('const o = { ...{ x: $a }, ...{ y: $b } };\nObject.keys(o).length;', lambda p: 2, "The spread merges two objects."),
    T("const o = { ...{ x: $a }, ...{ x: $b } };\no.x;", lambda p: p["b"], "A later property wins."),
    T("const [first, ...rest] = [$a, $b, $c, $d];\nrest;", lambda p: js_show([p["b"], p["c"], p["d"]]), "rest takes whatever is left."),
    T("const [x, , y] = [$a, $b, $c];\ny;", lambda p: p["c"], "The empty slot skips the middle item."),
    T("const [x, y = $d] = [$a];\ny;", lambda p: p["d"], "The array has no second item, so y uses its default."),
    T("const { x, ...others } = { x: $a, y: $b, z: $c };\nObject.keys(others).length;", lambda p: 2, "others gets y and z."),
    T("function f() {\n  let t = 0;\n  for (let i = 0; i < arguments.length; i++) t += arguments[i];\n  return t;\n}\nf($a, $b, $c);",
      lambda p: p["a"] + p["b"] + p["c"], "The loop adds every argument."),
    T("function f() {\n  return arguments[1];\n}\nf($a, $b, $c);", lambda p: p["b"], "arguments[1] is the second one."),
    T("const f = (...xs) => xs.length;\nf(...[$a, $b], ...[$c]);", lambda p: 3, "Two spread, then one more spread."),
    T("function f(a, b = $b, ...rest) {\n  return rest.length;\n}\nf($a, $b, $c, $d);", lambda p: 2, "rest gets the last two."),
    T("function f(...args) {\n  return Array.isArray(args);\n}\nf($a);", lambda p: "true", "...args is a real array."),
    T("function f(a, b) {\n  return a - b;\n}\nf.apply(null, [$a, $b]);", lambda p: p["a"] - p["b"], "apply spreads the array into the arguments."),
    T("function f(a, b) {\n  return a - b;\n}\nf.call(null, $a, $b);", lambda p: p["a"] - p["b"], "call takes the arguments one by one."),
    T("function f() {\n  return arguments.length;\n}\n[$a, $b].map(f);", lambda p: js_show([3, 3]), "map gives its callback three arguments: item, index, array."),
    T("function f(...args) {\n  args.push($a);\n  return args.length;\n}\nf($b, $c);", lambda p: 3, "push adds to the args array."),
    T("function sum(...n) {\n  return n.reduce((s, x) => s + x, 0);\n}\nsum(...[$a, $b], $c);", lambda p: p["a"] + p["b"] + p["c"], "All three numbers arrive in n."),
    T("[...[$a, $b], ...[$c]].length;", lambda p: 3, "The spread builds one array of three."),
    T('[..."$w"].length;', lambda p: len(p["w"]), "A string spreads into its letters."),
    T("function f(a, b) {\n  return [a, b];\n}\nf(...[$a, $b, $c]);", lambda p: js_show([p["a"], p["b"]]), "The third value has no parameter, so it is ignored."),
]


# ── 6. Recursion Result ─────────────────────────────────────────────────

RECUR = [
    T("function fact(n) {\n  return n <= 1 ? 1 : n * fact(n - 1);\n}\nfact($s);", lambda p: fact(p["s"]), "n * (n-1) * ... * 1."),
    T("function fib(n) {\n  return n < 2 ? n : fib(n - 1) + fib(n - 2);\n}\nfib($s);", lambda p: fib(p["s"]),
      "Each number is the sum of the two before: 0, 1, 1, 2, 3, 5, 8, 13..."),
    T("function total(n) {\n  if (n === 0) return 0;\n  return n + total(n - 1);\n}\ntotal($s);", lambda p: P.sum_to(p["s"]), "$s + ($s - 1) + ... + 1."),
    T("function digits(n) {\n  if (n < 10) return n;\n  return (n % 10) + digits(Math.floor(n / 10));\n}\ndigits($big);",
      lambda p: digit_sum(p["big"]), "It adds the last digit to the sum of the rest."),
    T("function power(b, e) {\n  if (e === 0) return 1;\n  return b * power(b, e - 1);\n}\npower($a, $r);", lambda p: P.power(p["a"], p["r"]),
      "$a multiplied by itself $r times."),
    T("function g(a, b) {\n  if (b === 0) return a;\n  return g(b, a % b);\n}\ng($gx, $gy);", lambda p: gcd(p["gx"], p["gy"]),
      "Euclid's way: keep replacing (a, b) with (b, a % b) until b is 0."),
    T('function rev(s) {\n  if (s === "") return "";\n  return rev(s.slice(1)) + s[0];\n}\nrev("$w");', lambda p: P.rev_text(p["w"]),
      "Each call puts its first letter after the reverse of the rest."),
    T('function down(n) {\n  if (n === 0) return "go";\n  return String(n) + down(n - 1);\n}\ndown($m);', lambda p: P.down_text(p["m"]),
      "The digits count down, then the base case adds go."),
    T('function up(n) {\n  if (n === 0) return "";\n  return up(n - 1) + n;\n}\nup($m);', lambda p: P.up_text(p["m"]),
      "The smaller case comes first, so the digits count up (the number joins the string)."),
    T('function length(s) {\n  if (s === "") return 0;\n  return 1 + length(s.slice(1));\n}\nlength("$w");', lambda p: len(p["w"]),
      "One for each letter, until the string is empty."),
    T('function count(s, c) {\n  if (s === "") return 0;\n  return (s[0] === c ? 1 : 0) + count(s.slice(1), c);\n}\ncount("$w$v", "$x");',
      lambda p: count_in(p["w"] + p["v"], p["x"]), "It adds 1 for each matching letter."),
    T("function total(xs) {\n  if (xs.length === 0) return 0;\n  return xs[0] + total(xs.slice(1));\n}\ntotal([$a, $b, $c]);",
      lambda p: p["a"] + p["b"] + p["c"], "The first item plus the total of the rest."),
    T("function biggest(xs) {\n  if (xs.length === 1) return xs[0];\n  const rest = biggest(xs.slice(1));\n  return xs[0] > rest ? xs[0] : rest;\n}\nbiggest([$a, $b, $c, $d]);",
      lambda p: P.largest([p["a"], p["b"], p["c"], p["d"]]), "The bigger of the first and the biggest of the rest."),
    T('function pal(s) {\n  if (s.length < 2) return true;\n  return s[0] === s[s.length - 1] && pal(s.slice(1, -1));\n}\npal("$pw");',
      lambda p: _js_bool(is_palindrome(p["pw"])), "It compares the two ends, then the inside."),
    T('function bits(n) {\n  if (n === 0) return "";\n  return bits(Math.floor(n / 2)) + (n % 2);\n}\nbits($n);', lambda p: bits(p["n"]),
      "The binary digits of n, written from the biggest place down."),
    T("function steps(n) {\n  if (n === 1) return 0;\n  if (n % 2 === 0) return 1 + steps(n / 2);\n  return 1 + steps(3 * n + 1);\n}\nsteps($s);",
      lambda p: collatz(p["s"]), "Halve when even, triple and add 1 when odd: count the steps to 1."),
    T("const pow2 = n => n === 0 ? 1 : 2 * pow2(n - 1);\npow2($s);", lambda p: P.power(2, p["s"]), "2 doubled $s times."),
    T("function ones(n) {\n  if (n < 2) return n;\n  return ones(Math.floor(n / 2)) + (n % 2);\n}\nones($n);", lambda p: popcount(p["n"]),
      "The number of 1s in n's binary digits."),
    T("function mul(a, b) {\n  if (b === 0) return 0;\n  return a + mul(a, b - 1);\n}\nmul($a, $r);", lambda p: p["a"] * p["r"], "$a added up $r times."),
    T("function add(a, b) {\n  if (b === 0) return a;\n  return add(a + 1, b - 1);\n}\nadd($a, $b);", lambda p: p["a"] + p["b"], "It moves 1 from b over to a each time."),
    T("const hanoi = n => n === 0 ? 0 : 2 * hanoi(n - 1) + 1;\nhanoi($s);", lambda p: hanoi(p["s"]), "Twice the moves of the smaller tower, plus one."),
    T("function rev(xs) {\n  if (xs.length === 0) return [];\n  return [...rev(xs.slice(1)), xs[0]];\n}\nrev([$a, $b, $c]);",
      lambda p: js_show([p["c"], p["b"], p["a"]]), "The reverse of the rest, then the first item."),
    T("function flat(x) {\n  if (Array.isArray(x)) return x.reduce((s, i) => s + flat(i), 0);\n  return x;\n}\nflat([$a, [$b, $c], [$d]]);",
      lambda p: p["a"] + p["b"] + p["c"] + p["d"], "An array is the sum of its parts; a number is itself."),
    T('function stars(n) {\n  if (n === 0) return "";\n  return stars(n - 1) + "*";\n}\nstars($m);', lambda p: "*" * p["m"], "One star per level."),
    T("function down(n) {\n  if (n === 0) return [];\n  return [n, ...down(n - 1)];\n}\ndown($m);", lambda p: js_show(list(reversed(list(range(1, p["m"] + 1))))),
      "n goes first, then the countdown of the rest."),
    T('function alt(s) {\n  if (s === "") return "";\n  return s[0] + alt(s.slice(2));\n}\nalt("$w");', lambda p: P.every_other(p["w"]),
      "It keeps a letter, skips one, and carries on."),
    T("function f(n) {\n  if (n > 0) f(n - 1);\n}\nf($m);", lambda p: "undefined", "f never returns anything, so the call gives undefined."),
    T("function f(n) {\n  if (n === 0) return 0;\n  f(n - 1) + n;\n}\nf($s);", lambda p: "undefined",
      "The last line works out a sum but never returns it, so the call gives undefined."),
    T("function has(xs, t) {\n  if (xs.length === 0) return false;\n  return xs[0] === t || has(xs.slice(1), t);\n}\nhas([$a, $b, $c], $d);",
      lambda p: _js_bool(P.has([p["a"], p["b"], p["c"]], p["d"])), "True if the target is the first item or somewhere in the rest."),
    T("function sq(n) {\n  if (n === 0) return [];\n  return [...sq(n - 1), n * n];\n}\nsq($m);", lambda p: js_show([k * k for k in range(1, p["m"] + 1)]),
      "The squares from 1 up, smallest first."),
    T("function f(n) {\n  if (n === 0) return 0;\n  return f(n - 1) + 2 * n - 1;\n}\nf($s);", lambda p: p["s"] * p["s"], "The odd numbers 1 + 3 + 5 ... add up to a square."),
    T("function f(n) {\n  if (n <= 0) return 0;\n  return n + f(n - 2);\n}\nf($s);", lambda p: P.skip_two_sum(p["s"]), "It adds every second number down from $s while it is above 0."),
    T("function flip(n, acc = 0) {\n  if (n === 0) return acc;\n  return flip(Math.floor(n / 10), acc * 10 + (n % 10));\n}\nflip($big);",
      lambda p: P.flip_digits(p["big"]), "Each call moves the last digit of n onto the end of acc."),
    T("function f(n) {\n  if (n === 0) return 0;\n  return 1 + f(Math.floor(n / 2));\n}\nf($n);", lambda p: halvings(p["n"]), "It counts how many times n can be halved before it reaches 0."),
    T('function rep(s, n) {\n  return n === 0 ? "" : s + rep(s, n - 1);\n}\nrep("$w", $r);', lambda p: p["w"] * p["r"], "The word, $r times over."),
    T("function f(n, acc = 1) {\n  if (n <= 1) return acc;\n  return f(n - 1, acc * n);\n}\nf($s);", lambda p: fact(p["s"]), "The product builds up in acc as n counts down."),
    T("function f(n) {\n  if (n === 0) return 0;\n  return f(n - 1) + 2;\n}\nf($s);", lambda p: 2 * p["s"], "Each level adds 2."),
]


# ── 7. Map Filter Reduce ────────────────────────────────────────────────

XS3 = "[$a, $b, $c]"
XS4 = "[$a, $b, $c, $d]"


def _abc(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"]]


def _abcd(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"], p["d"]]


def next_over(xs: list[int], limit: int):
    """What find(x => x > limit) gives."""
    for x in xs:
        if x > limit:
            return x
    return UNDEF


def first_index_over(xs: list[int], limit: int) -> int:
    for i in range(len(xs)):
        if xs[i] > limit:
            return i
    return -1


MFR = [
    T(XS3 + ".map(x => x * 2);", lambda p: js_show(P.change(_abc(p), lambda x: x * 2)), "map applies the arrow to every item: each is doubled."),
    T(XS3 + ".map(x => x + $d);", lambda p: js_show(P.change(_abc(p), lambda x: x + p["d"])), "Each item gets $d added."),
    T(XS3 + ".map(x => x * x);", lambda p: js_show(P.change(_abc(p), lambda x: x * x)), "Each item is squared."),
    T(XS4 + ".map(x => x % 3);", lambda p: js_show(P.change(_abcd(p), lambda x: tmod(x, 3))), "Each item's remainder when divided by 3."),
    T(XS3 + ".map(String);", lambda p: js_show(P.change(_abc(p), str)), "String turns each number into text, so the items show in quotes."),
    T(XS3 + ".map(x => -x);", lambda p: js_show(P.change(_abc(p), lambda x: -x)), "Each item with its sign flipped."),
    T(XS3 + ".map((x, i) => x * i);", lambda p: js_show([0, p["b"], 2 * p["c"]]), "The callback also gets the index: 0, 1, 2."),
    T(XS4 + ".filter(x => x > 5);", lambda p: js_show(P.pick(_abcd(p), lambda x: x > 5)), "filter keeps the items for which the arrow is true."),
    T(XS4 + ".filter(x => x % 2 === 0);", lambda p: js_show(P.pick(_abcd(p), lambda x: tmod(x, 2) == 0)), "Only the even ones stay."),
    T(XS4 + ".filter(x => x % 2);", lambda p: js_show(P.pick(_abcd(p), lambda x: tmod(x, 2) == 1)), "x % 2 is 1 (truthy) for odd numbers: those stay."),
    T(XS4 + ".filter(x => x !== $a);", lambda p: js_show(P.pick(_abcd(p), lambda x: x != p["a"])), "Everything but $a stays."),
    T(XS4 + ".filter(x => x < $a).length;", lambda p: len(P.pick(_abcd(p), lambda x: x < p["a"])), "How many items are below $a (maybe none)."),
    T(XS3 + ".map(x => x * 2).reduce((s, x) => s + x, 0);", lambda p: 2 * (p["a"] + p["b"] + p["c"]), "Double each, then add them up."),
    T(XS4 + ".filter(x => x > 4).reduce((s, x) => s + x, 0);", lambda p: fold(P.pick(_abcd(p), lambda x: x > 4), lambda s, x: s + x, 0),
      "Add up only the items over 4."),
    T(XS3 + ".reduce((acc, x) => acc + x);", lambda p: p["a"] + p["b"] + p["c"], "reduce folds the array into one value: here a running sum."),
    T(XS3 + ".reduce((acc, x) => acc * x);", lambda p: p["a"] * p["b"] * p["c"], "A running product."),
    T(XS3 + ".reduce((acc, x) => acc + x, $d);", lambda p: p["a"] + p["b"] + p["c"] + p["d"], "The second argument is where the running total starts."),
    T(XS3 + ".reduce((acc, x) => acc - x);", lambda p: p["a"] - p["b"] - p["c"], "It starts with the first item, then subtracts the others."),
    T(XS3 + ".reduceRight((acc, x) => acc - x);", lambda p: p["c"] - p["b"] - p["a"], "reduceRight works from the last item backwards."),
    T(XS4 + ".reduce((a, b) => a > b ? a : b);", lambda p: biggest(_abcd(p)), "It keeps the bigger of the running value and each item."),
    T(XS3 + ".reduce((acc, x) => acc * 10 + x);", lambda p: 100 * p["a"] + 10 * p["b"] + p["c"], "Each step shifts the digits left and adds the next."),
    T(XS3 + '.reduce((acc, x) => acc + x, "");', lambda p: str(p["a"]) + str(p["b"]) + str(p["c"]), "The empty string start makes + join the numbers as text."),
    T(XS3 + ".reduce((acc, x) => [x, ...acc], []);", lambda p: js_show([p["c"], p["b"], p["a"]]), "Each item goes in front of the running array: reversed."),
    T(XS4 + ".some(x => x > 8);", lambda p: _js_bool(biggest(_abcd(p)) > 8), "true if at least one item is over 8."),
    T(XS3 + ".every(x => x > 4);", lambda p: _js_bool(P.smallest(_abc(p)) > 4), "true only if every item is over 4."),
    T(XS4 + ".find(x => x > 5);", lambda p: str(next_over(_abcd(p), 5)), "find gives the first item over 5, or undefined if there is none."),
    T(XS4 + ".findIndex(x => x > 5);", lambda p: first_index_over(_abcd(p), 5), "findIndex gives the position of the first match, or -1."),
    T(XS4 + ".filter(x => x % 2 === 0).map(x => x * 3);", lambda p: js_show(P.change(P.pick(_abcd(p), lambda x: tmod(x, 2) == 0), lambda x: x * 3)),
      "Keep the even ones, then triple them."),
    T(XS4 + ".map(x => x * 3).filter(x => x % 2 === 0);", lambda p: js_show(P.pick(P.change(_abcd(p), lambda x: x * 3), lambda x: tmod(x, 2) == 0)),
      "Triple each, then keep the even results."),
    T('["$w", "$v"].map(w => w.length);', lambda p: js_show([len(p["w"]), len(p["v"])]), "The length of each word."),
    T('["$w", "$v", "$pw"].map(w => w[0]);', lambda p: js_show(P.first_letters([p["w"], p["v"], p["pw"]])), "The first letter of each word."),
    T('["$w", "$v"].reduce((n, w) => n + w.length, 0);', lambda p: len(p["w"]) + len(p["v"]), "Running total of the word lengths."),
    T("[0, $a, 0, $b].filter(Boolean);", lambda p: js_show([p["a"], p["b"]]), "Boolean keeps the truthy items."),
    T("[$a, $b].flatMap(x => [x, x * 2]);", lambda p: js_show([p["a"], p["a"] * 2, p["b"], p["b"] * 2]), "flatMap maps, then flattens one level."),
    T("Math.max(..." + XS4 + ".map(x => x % 5));", lambda p: biggest(P.change(_abcd(p), lambda x: tmod(x, 5))), "The biggest remainder."),
    T(XS3 + ".map(x => x * 2).join(\"-\");", lambda p: f"{p['a'] * 2}-{p['b'] * 2}-{p['c'] * 2}", "Double each, then join the numbers with -."),
    T("Array.from({ length: $m }, (_, i) => i * $a);", lambda p: js_show([i * p["a"] for i in range(p["m"])]), "Array.from builds an array by calling the arrow with each index."),
    T("[..." + XS4 + "].sort((p, q) => q - p);", lambda p: js_show(P.stable_sort(_abcd(p), lambda x: -x)), "A sort whose comparison is q - p puts the biggest first."),
    T(XS4 + ".map(x => x % 2 === 0 ? \"e\" : \"o\").join(\"\");", lambda p: "".join("e" if tmod(x, 2) == 0 else "o" for x in _abcd(p)),
      "e for each even item, o for each odd one, joined."),
    T("[1, 2, 3, 4].map(x => x * $a).filter(x => x > $b * 2);", lambda p: js_show(P.pick([k * p["a"] for k in (1, 2, 3, 4)], lambda x: x > p["b"] * 2)),
      "Multiply 1 to 4 by $a, then keep those over $b * 2."),
    T(XS4 + ".reduce((s, x) => s + (x > 4 ? 1 : 0), 0);", lambda p: len(P.pick(_abcd(p), lambda x: x > 4)), "A count of the items over 4."),
    T("[..." + XS3 + "].reverse().map(x => x + 1);", lambda p: js_show([p["c"] + 1, p["b"] + 1, p["a"] + 1]), "Reverse a copy, then add 1 to each."),
]


# ── 8. Pass or Copy ─────────────────────────────────────────────────────

def jrow(setup: str, body: str, changed, why: str = "") -> Maker:
    """A Pass or Copy template: `setup` makes `a` (and the functions), `body` is the call. The oracle program
    snapshots JSON.stringify(a) after the setup and again after the call."""
    def make(rng: random.Random) -> Item:
        p = P.tparams(rng)
        s, b = Template(setup).substitute(p), Template(body).substitute(p)
        yes = changed(p) if callable(changed) else changed
        check = (s + "\nconst _before = JSON.stringify(a);\n" + b +
                 '\nJSON.stringify(a) === _before ? "no" : "yes";')
        return Item(s + "\n" + b, "yes" if yes else "no", Template(why).safe_substitute(p), check=check)
    make.__name__ = "pass_" + body[:20]
    return make


PC = jrow
L2 = "let a = [$a, $b];"
L3 = "let a = [$a, $b, $c];"
O1 = "let a = { n: $a };"
BOX = "class Box {\n  constructor(n) { this.n = n; }\n}\n"


def _not_sorted(p: dict) -> bool:
    xs = [p["a"], p["b"], p["c"]]
    return isort(xs) != xs


COPY = [
    PC("function f(n) {\n  n += 1;\n}\nlet a = $a;", "f(a);", False, "A number cannot change in place: n += 1 only changes the local n."),
    PC('function f(s) {\n  s += "!";\n}\nlet a = "$w";', "f(a);", False, "A string cannot change in place; += builds a new one for the local s."),
    PC("function f(xs) {\n  xs.push($c);\n}\n" + L2, "f(a);", True, "The function got the same array, so push changes a's array."),
    PC("function f(xs) {\n  xs = xs.concat([$c]);\n}\n" + L2, "f(a);", False, "concat builds a new array; only the local xs points to it."),
    PC("function f(xs) {\n  xs = [...xs, $c];\n}\n" + L2, "f(a);", False, "The spread builds a new array for the local xs."),
    PC("function f(xs) {\n  xs.concat([$c]);\n}\n" + L2, "f(a);", False, "The new array is thrown away; a's array is untouched."),
    PC("function f(xs) {\n  xs.sort();\n}\n" + L3, "f(a);", _not_sorted, "sort() works in place: it changes the array unless it was already in order."),
    PC("function f(xs) {\n  [...xs].sort();\n}\n" + L3, "f(a);", False, "It sorts a copy made by the spread."),
    PC("function f(xs) {\n  xs.length = 0;\n}\n" + L2, "f(a);", True, "Setting length to 0 empties the shared array."),
    PC("function f(xs) {\n  xs = [];\n}\n" + L2, "f(a);", False, "xs = [] points the local name at a new array; a keeps its items."),
    PC("function f(xs) {\n  xs.splice(0, 1);\n}\n" + L2, "f(a);", True, "splice removes items from the shared array."),
    PC("function f(xs) {\n  xs.slice(1);\n}\n" + L2, "f(a);", False, "slice only copies."),
    PC("function f(xs) {\n  xs.map(x => x * 2);\n}\n" + L3, "f(a);", False, "map builds a new array and does not touch the original."),
    PC("function f(xs) {\n  xs.forEach(x => { x *= 2; });\n}\n" + L3, "f(a);", False, "x is a copy of each number."),
    PC("function f(xs) {\n  for (let i = 0; i < xs.length; i++) xs[i]++;\n}\n" + L3, "f(a);", True, "xs[i]++ assigns into the shared array."),
    PC("function f(o) {\n  o.n = $c;\n}\n" + O1, "f(a);", True, "The function got the same object, so the new n shows in a."),
    PC("function f(o) {\n  o = { n: $c };\n}\n" + O1, "f(a);", False, "o now names a new object; a's object is untouched."),
    PC("function f(o) {\n  o = { ...o, n: $c };\n}\n" + O1, "f(a);", False, "The spread builds a new object for the local o."),
    PC("function f(o) {\n  Object.assign(o, { n: $c });\n}\n" + O1, "f(a);", True, "assign copies into its first argument, the shared object."),
    PC("function f(o) {\n  delete o.n;\n}\n" + O1, "f(a);", True, "delete removes the property from the shared object."),
    PC("function f(o) {\n  o.items.push($c);\n}\nlet a = { items: [$a] };", "f(a);", True, "o.items is the shared inner array."),
    PC("function f(o) {\n  const copy = { ...o };\n  copy.items.push($c);\n}\nlet a = { items: [$a] };", "f(a);", True,
       "The spread is a shallow copy: the inner array is still shared."),
    PC("function f(o) {\n  const copy = JSON.parse(JSON.stringify(o));\n  copy.items.push($c);\n}\nlet a = { items: [$a] };", "f(a);", False,
       "A JSON round trip is a deep copy: the inner array is new too."),
    PC("function f(xs) {\n  return [...xs, $c];\n}\n" + L2, "f(a);", False, "The new array is returned and thrown away; a is untouched."),
    PC("function f(xs) {\n  return [...xs, $c];\n}\n" + L2, "a = f(a);", True, "a = f(a) points a at the new array, so a is different now."),
    PC("function f(xs = []) {\n  xs.push($c);\n}\n" + L2, "f();", False, "f() used its own default array, not a's."),
    PC("function f() {\n  a = a + 1;\n}\nlet a = $a;", "f();", True, "There is no let in f, so a = a + 1 changes the outer a."),
    PC("function f() {\n  let a = 5;\n}\nlet a = $a;", "f();", False, "let a inside f makes a different variable."),
    PC("function f(xs) {\n  [xs[0], xs[1]] = [xs[1], xs[0]];\n}\n" + L2, "f(a);", True, "The swap changes the items of the shared array."),
    PC("function f(xs) {\n  xs.reverse();\n}\n" + L3, "f(a);", True, "reverse() works in place."),
    PC("function f(xs) {\n  xs.pop();\n}\n" + L2, "f(a);", True, "pop removes the last item from the shared array."),
    PC("function f(xs) {\n  xs.shift();\n}\n" + L2, "f(a);", True, "shift removes the first item from the shared array."),
    PC("function f(xs) {\n  xs.unshift($c);\n}\n" + L2, "f(a);", True, "unshift adds to the shared array."),
    PC("function f(xs) {\n  xs.fill(0);\n}\n" + L2, "f(a);", True, "fill overwrites every item of the shared array."),
    PC(BOX + "function f(b) {\n  b.n++;\n}\nlet a = new Box($a);", "f(a);", True, "The function got the same object, so its n changes."),
    PC(BOX + "function f(b) {\n  b = new Box(0);\n}\nlet a = new Box($a);", "f(a);", False, "b now names a new Box; a's Box is untouched."),
    PC("function add_to(src, dst) {\n  dst.push(src[0]);\n}\nlet a = [$a];\nconst b = [$b];", "add_to(b, a);", True,
       "a is the second argument, dst, which gets the push."),
    PC("function add_to(src, dst) {\n  dst.push(src[0]);\n}\nlet a = [$a];\nconst b = [$b];", "add_to(a, b);", False, "a is only read: b is the one that grows."),
    PC("function f(a) {\n  a.push($c);\n}\n" + L2, "f(a);", True, "The parameter is also called a, but it is the same array."),
    PC("function f(a) {\n  a = [...a, $c];\n}\n" + L2, "f(a);", False, "The spread builds a new array for the parameter a."),
    PC("function f(o) {\n  o.n += 1;\n}\nconst a = { n: $a };", "f(a);", True, "const stops reassigning a, not changing the object."),
    PC("function swap(p, q) {\n  [p, q] = [q, p];\n}\nlet a = $a;\nlet b = $b;", "swap(a, b);", False, "The swap trades the local names; a and b stay as they were."),
    PC("function f(xs) {\n  xs.indexOf($a);\n}\n" + L2, "f(a);", False, "indexOf only looks."),
    PC("function f(o) {\n  o.n = o.n + 1;\n  o = null;\n}\n" + O1, "f(a);", True, "The property was changed before o was pointed at null."),
]
