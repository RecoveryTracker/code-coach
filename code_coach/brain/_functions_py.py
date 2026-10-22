"""Functions and scope pack, Python side.

Eight activities: Which x (scope), Default Args, Count the Calls, Closure
Counter, Args Count, Recursion Result, Map Filter Reduce, Pass or Copy.
Python's pool is the bigger one (40 or more templates each). Every answer is
modelled by hand - recursion is spelled out as a recursion, a fold as a loop,
a stable sort as an insertion sort - and tests/test_brain_packs.py runs every
template through the real interpreter.

The prompt's last line is an expression, and its value is the answer (the
oracle takes the value of the last line). `trow` builds a template from a
table row: `fmt` has $a $b $c $d (different ints 2-9), $n (10-40), $w $v
(words), $k (1-3), $x (a letter) and, here too, $m (2-5), $r (2-4), $s (3-8),
$big (a 3- or 4-digit number without zeros), $p $q (different letters) and
$gx $gy (two numbers with a common factor).
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from ._model import Maker, fdiv, fmod, isort, params, py_div, py_show, reverse, upper
from .items import Item

LETTERS = "abcdefghkmnpqrstwxyz"


def tparams(rng: random.Random) -> dict[str, Any]:
    p = params(rng)
    p["m"] = rng.randint(2, 5)
    p["r"] = rng.randint(2, 4)
    p["s"] = rng.randint(3, 8)
    p["big"] = int("".join(str(rng.randint(1, 9)) for _ in range(rng.randint(3, 4))))
    p["p"], p["q"] = rng.sample(LETTERS, 2)
    g = rng.choice((2, 3, 4, 5))
    u, v = rng.sample(range(2, 9), 2)
    p["gx"], p["gy"] = g * u, g * v
    p["pw"] = rng.choice(PALINDROMES + NOT_PALINDROMES)
    return p


def _text(got: Any) -> str:
    assert isinstance(got, (str, int)) and not isinstance(got, bool), f"say how to print {got!r}"
    return str(got)


def trow(fmt: str, answer: Any, why: Any = "", check: Callable[[str, dict], str] | None = None) -> Maker:
    """A template from a table row: `answer` is a value or a function of the parameters (ints are printed as
    they are; give lists, tuples and booleans as text with py_show)."""
    def make(rng: random.Random) -> Item:
        p = tparams(rng)
        prompt = Template(fmt).substitute(p)
        got = _text(answer(p) if callable(answer) else answer)
        text = why(p) if callable(why) else Template(why).safe_substitute(p)
        return Item(prompt, got, text, check=check(prompt, p) if check else "")
    make.__name__ = "t_" + fmt[:24]
    return make


def prow(setup: str, body: str, changed: Any, why: str = "", snap: str = "repr(a)") -> Maker:
    """A Pass or Copy template: `setup` makes `a` (and defines the functions), `body` is the call, and the
    question is whether `a` ended up different. The oracle program snapshots `snap` after the setup and again
    after the call."""
    def make(rng: random.Random) -> Item:
        p = tparams(rng)
        s, b = Template(setup).substitute(p), Template(body).substitute(p)
        yes = changed(p) if callable(changed) else changed
        check = s + f"\n_before = {snap}\n" + b + f'\n"no" if {snap} == _before else "yes"'
        return Item(s + "\n" + b, "yes" if yes else "no", Template(why).safe_substitute(p), check=check)
    make.__name__ = "pass_" + body[:20]
    return make


# ── Hand models: the programs, spelled out ──────────────────────────────

def fact(n: int) -> int:
    return 1 if n <= 1 else n * fact(n - 1)


def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib1(n: int) -> int:
    """The Fibonacci that starts 1, 1."""
    return 1 if n <= 1 else fib1(n - 1) + fib1(n - 2)


def fib_calls(n: int) -> int:
    """How many times fib(n) runs, itself included."""
    return 1 if n < 2 else 1 + fib_calls(n - 1) + fib_calls(n - 2)


def gcd(a: int, b: int) -> int:
    return a if b == 0 else gcd(b, fmod(a, b))


def digit_sum(n: int) -> int:
    return n if n < 10 else fmod(n, 10) + digit_sum(fdiv(n, 10))


def digit_count(n: int) -> int:
    return 1 if n < 10 else 1 + digit_count(fdiv(n, 10))


def bits(n: int) -> str:
    return "" if n == 0 else bits(fdiv(n, 2)) + str(fmod(n, 2))


def collatz(n: int) -> int:
    if n == 1:
        return 0
    return 1 + (collatz(fdiv(n, 2)) if fmod(n, 2) == 0 else collatz(3 * n + 1))


def popcount(n: int) -> int:
    return n if n < 2 else popcount(fdiv(n, 2)) + fmod(n, 2)


def flip_digits(n: int, acc: int = 0) -> int:
    return acc if n == 0 else flip_digits(fdiv(n, 10), acc * 10 + fmod(n, 10))


def every_other(s: str) -> str:
    return "" if s == "" else s[0] + every_other(s[2:])


def halvings(n: int) -> int:
    """How many times halve(n) runs: it calls itself with n // 2 while n > 1."""
    return 1 if n <= 1 else 1 + halvings(fdiv(n, 2))


def tree_calls(n: int) -> int:
    """f(n) calls f(n - 1) twice while n > 0: how many calls in all."""
    return 1 if n <= 0 else 1 + 2 * tree_calls(n - 1)


def hanoi(n: int) -> int:
    return 0 if n == 0 else 2 * hanoi(n - 1) + 1


def fold(xs: list, step: Callable[[Any, Any], Any], start: Any) -> Any:
    acc = start
    for x in xs:
        acc = step(acc, x)
    return acc


def stable_sort(xs: list, key: Callable[[Any], Any]) -> list:
    """A stable sort by key, by insertion."""
    out: list = []
    for x in xs:
        k = len(out)
        while k > 0 and key(out[k - 1]) > key(x):
            k -= 1
        out.insert(k, x)
    return out


def first_best(xs: list, key: Callable[[Any], Any], biggest: bool) -> Any:
    """min(xs, key=) / max(xs, key=): the first of the ties wins."""
    best = xs[0]
    for x in xs[1:]:
        if (key(x) > key(best)) if biggest else (key(x) < key(best)):
            best = x
    return best


def count_in(s: str, ch: str) -> int:
    n = 0
    for c in s:
        if c == ch:
            n += 1
    return n


def is_palindrome(s: str) -> bool:
    return True if len(s) < 2 else s[0] == s[-1] and is_palindrome(s[1:-1])


def is_pal_word(w: str) -> str:
    return py_show(is_palindrome(w))


def join_ints(xs: list[int], sep: str) -> str:
    out = ""
    for i, x in enumerate(xs):
        out += (sep if i else "") + str(x)
    return out


# ── 1. Which x ──────────────────────────────────────────────────────────

T = trow

SCOPE = [
    T("x = $a\ndef f():\n    return x\nf()", lambda p: p["a"],
      "f makes no x of its own, so it reads the global x."),
    T("x = $a\ndef f():\n    x = $b\n    return x\nf()", lambda p: p["b"],
      "Assigning inside f makes a local x, which hides the global one."),
    T("x = $a\ndef f():\n    x = $b\nf()\nx", lambda p: p["a"],
      "The x inside f is a separate local; the global x never changed."),
    T("x = $a\ndef f():\n    global x\n    x = $b\nf()\nx", lambda p: p["b"],
      "global x makes the assignment change the module's x."),
    T("count = $a\ndef bump():\n    global count\n    count += 1\nbump()\nbump()\ncount", lambda p: p["a"] + 2,
      "global lets bump change count, and it runs twice."),
    T("x = $a\ndef f():\n    global x\n    x = $b\nx", lambda p: p["a"],
      "f was never called, so x is still $a."),
    T("def outer():\n    x = $a\n    def inner():\n        nonlocal x\n        x = $b\n    inner()\n    return x\nouter()",
      lambda p: p["b"], "nonlocal makes inner change outer's x."),
    T("def outer():\n    x = $a\n    def inner():\n        x = $b\n    inner()\n    return x\nouter()",
      lambda p: p["a"], "Without nonlocal, inner's x = ... makes its own local x."),
    T("def outer():\n    x = $a\n    def inner():\n        return x + $b\n    return inner()\nouter()",
      lambda p: p["a"] + p["b"], "inner reads x from the function around it."),
    T("x = $a\ndef f(x):\n    return x * 2\nf($b)", lambda p: p["b"] * 2,
      "The parameter x is a local that hides the global x."),
    T("x = $a\ndef f(x):\n    x += 1\n    return x\nf($b)\nx", lambda p: p["a"],
      "Changing the parameter x never touches the global x."),
    T("x = $a\ndef f():\n    x = $b\n    def g():\n        return x\n    return g()\nf()", lambda p: p["b"],
      "g looks outward: f's x comes before the global x."),
    T("for i in range($m):\n    pass\ni", lambda p: p["m"] - 1,
      "A loop variable stays after the loop: Python has no block scope."),
    T("n = $a\nif n > 1:\n    y = $b\ny", lambda p: p["b"],
      "An if makes no scope of its own, so y lives on after it."),
    T("i = $a\nxs = [i for i in range($m)]\ni", lambda p: p["a"],
      "A comprehension has its own scope: its i never leaks out."),
    T("x = $a\nys = [x * i for i in range(3)]\nys", lambda p: py_show([0, p["a"], 2 * p["a"]]),
      "The comprehension reads the global x and has its own i."),
    T("log = []\ndef add(v):\n    log.append(v)\nadd($a)\nadd($b)\nlog", lambda p: py_show([p["a"], p["b"]]),
      "append changes the list; there is no assignment, so no global is needed."),
    T("log = [$a]\ndef reset():\n    log = []\nreset()\nlog", lambda p: py_show([p["a"]]),
      "log = [] inside reset makes a local; the global list is untouched."),
    T("def setup():\n    global score\n    score = $a\nsetup()\nscore", lambda p: p["a"],
      "global lets a function create a module-level name."),
    T("x = 0\ndef up():\n    global x\n    x += $a\ndef down():\n    global x\n    x -= $b\nup()\ndown()\nx",
      lambda p: p["a"] - p["b"], "Both functions change the one global x."),
    T("x = $a\ndef f():\n    return x\nx = $b\nf()", lambda p: p["b"],
      "A global is looked up when f runs, not when it is defined."),
    T("def outer():\n    x = $a\n    def inner():\n        return x\n    x = $b\n    return inner()\nouter()",
      lambda p: p["b"], "inner reads x when it runs, and x is $b by then."),
    T("x = $a\ndef f():\n    x = $b\n    return x + 1\nf() + x", lambda p: p["b"] + 1 + p["a"],
      "f gives its local x + 1, and the global x is still $a."),
    T("x = $a\nf = lambda y: x + y\nf($b)", lambda p: p["a"] + p["b"],
      "A lambda reads the global x just as a def does."),
    T("x = $a\nf = lambda x: x * 2\nf($b)", lambda p: p["b"] * 2,
      "The lambda's parameter x hides the global x."),
    T("x = $a\ndef f():\n    global x\n    x = x * 2\nf()\nf()\nx", lambda p: p["a"] * 4,
      "Each call doubles the global x, and f runs twice."),
    T("def make():\n    n = 0\n    def inc():\n        nonlocal n\n        n += $a\n        return n\n    inc()\n    return inc()\nmake()",
      lambda p: p["a"] * 2, "Each call adds $a to the same n, so the second call gives twice that."),
    T("def outer():\n    x = $a\n    def inner():\n        x = $b\n        return x\n    inner()\n    return x\nouter()",
      lambda p: p["a"], "inner's x is its own local, so outer's x is untouched."),
    T("total = 0\ndef add_all(xs):\n    global total\n    for v in xs:\n        total += v\nadd_all([$a, $b, $c])\ntotal",
      lambda p: p["a"] + p["b"] + p["c"], "global total makes every += change the module's total."),
    T("total = $d\ndef add_all(xs):\n    total = 0\n    for v in xs:\n        total += v\n    return total\nadd_all([$a, $b, $c]) + total",
      lambda p: p["a"] + p["b"] + p["c"] + p["d"], "The function's total is its own local; the global total is still $d."),
    T('x = "$w"\ndef f():\n    x = "$v"\n    return x\nf() + x', lambda p: p["v"] + p["w"],
      "f gives its local x ($v), then + joins the global x ($w)."),
    T('name = "$w"\ndef shout():\n    return name + "!"\nshout()', lambda p: p["w"] + "!",
      "shout reads the global name."),
    T("x = $a\ndef f(flag):\n    if flag:\n        x = $b\n    return x\nf(True)", lambda p: p["b"],
      "An assignment anywhere in f makes x local to f; with flag True it is set before the return."),
    T("def f():\n    x = $a\n    x += $b\n    return x\nx = $c\nf() + x", lambda p: p["a"] + p["b"] + p["c"],
      "f works on its own local x; the global x is $c."),
    T("x = $a\ndef f():\n    def g():\n        return x\n    return g()\nf()", lambda p: p["a"],
      "f has no x, so g's search goes on out to the global x."),
    T("x = $a\ny = $b\ndef f():\n    y = x + 1\n    return y\nf() + y", lambda p: p["a"] + 1 + p["b"],
      "f's y is a local; the global y is still $b."),
    T('def f():\n    y = $a\nf()\n"y" in globals()', lambda p: py_show(False),
      "y was local to f and is gone, so the module has no y."),
    T("n = $a\ndef f(n):\n    n = n + $b\nf(n)\nn", lambda p: p["a"],
      "Rebinding a parameter never touches the caller's variable."),
    T("x = $a\ndef f():\n    for x in range($m):\n        pass\n    return x\nf()", lambda p: p["m"] - 1,
      "The loop variable is a local of f, and it keeps its last value."),
    T("x = $a\ndef f():\n    for x in range($m):\n        pass\nf()\nx", lambda p: p["a"],
      "The for inside f assigns a local x; the global x is untouched."),
    T("x = $a\ndef f():\n    global x\n    for x in range($m):\n        pass\nf()\nx", lambda p: p["m"] - 1,
      "With global x the loop assigns the module's x, and it keeps its last value."),
    T("def f():\n    x = $a\n    def g():\n        nonlocal x\n        x += 1\n    g()\n    g()\n    return x\nf()",
      lambda p: p["a"] + 2, "Each g() adds 1 to f's x."),
    T("x = [$a]\ndef f():\n    x.append($b)\n    return len(x)\nf()\nf()", lambda p: 3,
      "The global list grows on each call: 2 items after the first, 3 after the second."),
]


# ── 2. Default Args ─────────────────────────────────────────────────────

ADD = "def add(x, acc=[]):\n    acc.append(x)\n    return acc\n"
ADD2 = "def add(a, b=[]):\n    b.append(a)\n    return b\n"
ONCE = "A default list is made once, when the def runs, and every call that leaves it out shares it."

DEFAULTS = [
    T("def f(a, b=$b):\n    return a + b\nf($a)", lambda p: p["a"] + p["b"], "b falls back to its default, $b."),
    T("def f(a, b=$b):\n    return a + b\nf($a, $c)", lambda p: p["a"] + p["c"],
      "A value passed in replaces the default."),
    T("def f(a, b=$b):\n    return a - b\nf(b=$c, a=$a)", lambda p: p["a"] - p["c"],
      "Keywords match by name, not by position."),
    T(ADD + "add($a)\nadd($b)", lambda p: py_show([p["a"], p["b"]]), ONCE),
    T(ADD + "add($a)\nadd($b)\nadd($c)", lambda p: py_show([p["a"], p["b"], p["c"]]), ONCE),
    T(ADD + "add($a)\nadd($b)\nlen(add($c))", lambda p: 3, ONCE),
    T(ADD + "add($a)\nadd($b, [])\nadd($c)", lambda p: py_show([p["a"], p["c"]]),
      "Passing your own list skips the shared default, so $b never reached it."),
    T("def add(x, acc=None):\n    if acc is None:\n        acc = []\n    acc.append(x)\n    return acc\nadd($a)\nadd($b)",
      lambda p: py_show([p["b"]]), "With None as the default, each call builds its own fresh list."),
    T('def count(w, seen={}):\n    seen[w] = seen.get(w, 0) + 1\n    return seen\ncount("$w")\ncount("$w")\ncount("$v")',
      lambda p: py_show({p["w"]: 2, p["v"]: 1}), "A default dict is made once and shared by every call."),
    T("def f(n, total=0):\n    total += n\n    return total\nf($a)\nf($b)", lambda p: p["b"],
      "A number cannot change in place, so total starts at 0 on every call."),
    T("x = $a\ndef f(y=x):\n    return y\nx = $b\nf()", lambda p: p["a"],
      "A default is worked out once, when the def line runs: x was $a then."),
    T("def f(a, b=2, c=3):\n    return a + b + c\nf($a)", lambda p: p["a"] + 5, "Both b and c use their defaults: a + 2 + 3."),
    T("def f(a, b=2, c=3):\n    return a + b + c\nf($a, $b)", lambda p: p["a"] + p["b"] + 3,
      "The second argument goes to b; c keeps its default 3."),
    T("def f(a, b=2, c=3):\n    return a + b + c\nf($a, c=$b)", lambda p: p["a"] + 2 + p["b"],
      "c is set by name, and b keeps its default 2."),
    T("def f(a, b=2, c=3):\n    return a + b + c\nf($a, $b, $c)", lambda p: p["a"] + p["b"] + p["c"],
      "Every default is replaced."),
    T('def greet(name, greeting="hi"):\n    return greeting + " " + name\ngreet("$w")', lambda p: "hi " + p["w"],
      "greeting falls back to \"hi\"."),
    T('def greet(name, greeting="hi"):\n    return greeting + " " + name\ngreet("$w", "yo")', lambda p: "yo " + p["w"],
      "The second argument replaces the default greeting."),
    T('def greet(name, greeting="hi"):\n    return greeting + " " + name\ngreet(greeting="yo", name="$w")',
      lambda p: "yo " + p["w"], "Keywords can come in any order."),
    T('def tag(s, end=""):\n    return s + end\ntag("$w", "!")', lambda p: p["w"] + "!", "end is replaced by the second argument."),
    T("def f(xs=[$a, $b]):\n    xs.append($c)\n    return len(xs)\nf()\nf()", lambda p: 4,
      "The same default list grows by one on each call: 3, then 4."),
    T("def f(xs=[$a]):\n    xs += [$b]\n    return xs\nf()\nf()", lambda p: py_show([p["a"], p["b"], p["b"]]),
      "+= changes the shared default list in place, once per call."),
    T("def f(xs=[$a]):\n    xs = xs + [$b]\n    return xs\nf()\nf()", lambda p: py_show([p["a"], p["b"]]),
      "xs + [...] builds a new list each time, so the default is never changed."),
    T("def f(n=None):\n    return n or $a\nf(0)", lambda p: p["a"], "0 is falsy, so or takes the right side."),
    T("def f(n=None):\n    return $a if n is None else n\nf(0)", lambda p: 0,
      "is None only catches None, so 0 is kept."),
    T("def power(x, n=2):\n    return x ** n\npower($a)", lambda p: p["a"] * p["a"], "n defaults to 2: a square."),
    T("def power(x, n=2):\n    return x ** n\npower($a, 3)", lambda p: p["a"] * p["a"] * p["a"], "n is replaced by 3: a cube."),
    T("def area(w, h=None):\n    if h is None:\n        h = w\n    return w * h\narea($a)", lambda p: p["a"] * p["a"],
      "With no h it falls back to w: a square."),
    T("def f(a, b=$b):\n    return a * b\nf($a, b=$c)", lambda p: p["a"] * p["c"], "b is set by name."),
    T("def f(a=$a, b=$b):\n    return a - b\nf(b=$c)", lambda p: p["a"] - p["c"], "Only b is given; a keeps its default."),
    T("f = lambda x, y=$b: x * y\nf($a)", lambda p: p["a"] * p["b"], "A lambda can have defaults too."),
    T("fs = [lambda x=i: x for i in range($m)]\nfs[-1]()", lambda p: p["m"] - 1,
      "The default x=i is fixed when each lambda is made, so the last one holds the last i."),
    T("fs = [lambda x=i: x for i in range($m)]\nfs[0]()", lambda p: 0, "Each lambda kept the i it was made with: the first holds 0."),
    T(ADD2 + "x = add($a)\ny = add($b)\nx is y", lambda p: py_show(True),
      "Both calls hand back the one shared default list."),
    T(ADD2 + "x = add($a)\ny = add($b)\nlen(x)", lambda p: 2, "x is the shared list, and the second call grew it."),
    T(ADD2 + "x = add($a)\nadd($b)\nx", lambda p: py_show([p["a"], p["b"]]), "x is the shared list, so it shows the later append."),
    T('def add(x, s=""):\n    s += x\n    return s\nadd("$w")\nadd("$v")', lambda p: p["v"],
      "A string cannot change in place, so s starts as \"\" on every call."),
    T("def f(n, seen=set()):\n    seen.add(n)\n    return len(seen)\nf($a)\nf($b)\nf($a)", lambda p: 2,
      "The default set is shared: it holds $a and $b, and the repeat adds nothing."),
    T("def f(x, acc=[]):\n    acc.append(x)\n    return sum(acc)\nf($a)\nf($b)", lambda p: p["a"] + p["b"],
      "The shared list holds both values by the second call."),
    T("def f(a, b=$b):\n    return a if a > b else b\nf($a)", lambda p: p["a"] if p["a"] > p["b"] else p["b"],
      "Whichever of a and the default b is bigger."),
    T("def f(a, *, scale=$b):\n    return a * scale\nf($a)", lambda p: p["a"] * p["b"],
      "scale falls back to its default $b."),
    T("def f(a, *, scale=$b):\n    return a * scale\nf($a, scale=$c)", lambda p: p["a"] * p["c"],
      "After the *, scale can only be given by name."),
    T("def f(x=None):\n    return x\nf()", lambda p: "None", "The default is None."),
    T("def f(x=None):\n    return x is None\nf(0)", lambda p: py_show(False), "0 was passed, so x is 0, not None."),
    T("def f(a, b=$b):\n    b += a\n    return b\nf($a)\nf($a)", lambda p: p["a"] + p["b"],
      "b is a number, so it starts at $b again on every call."),
    T("def f(n=$a):\n    return n\nf(n=$b)", lambda p: p["b"], "A keyword argument replaces the default."),
    T("def f(a, b=[]):\n    b = b + [a]\n    return b\nf($a)\nf($b)", lambda p: py_show([p["b"]]),
      "b + [a] builds a new list, so the default stays empty."),
    T("def f(items=[]):\n    items.append(1)\n    return items\nf()\nf()\nf()", lambda p: py_show([1, 1, 1]),
      "All three calls append to the one default list."),
    T('def hello(name="$w"):\n    return name\nhello(None)', lambda p: "None",
      "None was passed, so the default is not used."),
    T('def hello(name="$w"):\n    return name\nhello()', lambda p: p["w"], "No argument, so the default is used."),
    T("def f(a, b=$b, c=$c):\n    return a + c\nf($a, $d)", lambda p: p["a"] + p["c"],
      "The second value goes to b, so c keeps its default $c."),
    T("def f(a, b=$b, c=$c):\n    return c\nf($a, c=$d)", lambda p: p["d"], "c is set by name."),
    T("def make(n, items=None):\n    items = items or []\n    items.append(n)\n    return items\nmake($a)\nmake($b)",
      lambda p: py_show([p["b"]]), "Each call gets a fresh list when none is passed."),
    T("n = $a\ndef f(x=n + 1):\n    return x\nn = $b\nf()", lambda p: p["a"] + 1,
      "n + 1 was worked out when the def ran, with n = $a."),
    T('def f(a, b=len("$w")):\n    return a + b\nf($a)', lambda p: p["a"] + len(p["w"]),
      "The default is the length of the word, worked out once."),
]


# ── 3. Count the Calls ──────────────────────────────────────────────────

def fact_calls(n: int) -> int:
    """How many times fact(n) runs, with the base case at n <= 1."""
    return 1 if n <= 1 else 1 + fact_calls(n - 1)


def evens_below(n: int) -> int:
    """How many i in range(n) have i % 2 == 0."""
    c = 0
    for i in range(n):
        if fmod(i, 2) == 0:
            c += 1
    return c


def checks_until_big(xs: list[int], limit: int) -> int:
    """How many items a loop looks at before it breaks on the first one over the limit."""
    n = 0
    for x in xs:
        n += 1
        if x > limit:
            break
    return n


def over(xs: list[int], limit: int) -> int:
    n = 0
    for x in xs:
        if x > limit:
            n += 1
    return n


COUNT = "calls = 0\ndef f():\n    global calls\n    calls += 1\n"
SQ = "calls = 0\ndef sq(x):\n    global calls\n    calls += 1\n    return x * x\n"
LOGF = "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
TICK = "n = 0\ndef tick():\n    global n\n    n += 1\n    return n\n"
HELLO = "calls = 0\ndef hello():\n    global calls\n    calls += 1\ndef repeat(fn, k):\n    for _ in range(k):\n        fn()\n"
BIG = "calls = 0\ndef is_big(x):\n    global calls\n    calls += 1\n    return x > 5\n"
GEN = "calls = 0\ndef gen():\n    global calls\n    for i in range($m):\n        calls += 1\n        yield i\n"

CALLS = [
    T(COUNT + "for i in range($m):\n    f()\ncalls", lambda p: p["m"], "The loop calls f once per turn."),
    T(COUNT + "for i in range($a):\n    f()\ncalls", lambda p: p["a"], "The loop calls f once per turn: $a turns."),
    T(COUNT + "f()\nf()\nf()\ncalls", lambda p: 3, "Three lines call f, so three calls."),
    T("n = 0\ndef down(k):\n    global n\n    n += 1\n    if k > 0:\n        down(k - 1)\ndown($a)\nn", lambda p: p["a"] + 1,
      "It runs for $a, then every number below down to 0: one call more than $a."),
    T("calls = 0\ndef fib(n):\n    global calls\n    calls += 1\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\nfib($s)\ncalls",
      lambda p: fib_calls(p["s"]), "Each call below 2 stops; every other one makes two more calls."),
    T("calls = 0\ndef fact(n):\n    global calls\n    calls += 1\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\nfact($a)\ncalls",
      lambda p: fact_calls(p["a"]), "One call for each of $a, $a - 1, ... down to 1."),
    T('out = ""\ndef f(c):\n    global out\n    out += c\ndef g():\n    f("$p")\n    f("$q")\ng()\ng()\nout',
      lambda p: p["p"] + p["q"] + p["p"] + p["q"], "Each g() adds $p then $q, and g runs twice."),
    T(LOGF + "f(0) and f($a)\nlen(log)", lambda p: 1, "f(0) is falsy, so and skips the second call."),
    T(LOGF + "f($a) and f($b)\nlen(log)", lambda p: 2, "f($a) is truthy, so and goes on to the second call."),
    T(LOGF + "f($a) or f($b)\nlen(log)", lambda p: 1, "f($a) is truthy, so or stops: the second call never happens."),
    T(LOGF + "f(0) or f($a)\nlen(log)", lambda p: 2, "f(0) is falsy, so or goes on to the second call."),
    T(LOGF + "f($a) + f($b) * f($c)\nlog", lambda p: py_show([p["a"], p["b"], p["c"]]),
      "The calls happen left to right, whatever the operators."),
    T("calls = 0\ndef ok(i):\n    global calls\n    calls += 1\n    return i < $m\ni = 0\nwhile ok(i):\n    i += 1\ncalls",
      lambda p: p["m"] + 1, "The test runs once for each pass, plus the final test that fails."),
    T(SQ + "xs = [sq(i) for i in range($m)]\ncalls", lambda p: p["m"], "The comprehension calls sq once per item."),
    T(SQ + "xs = [sq(i) for i in range($s) if i % 2 == 0]\ncalls", lambda p: evens_below(p["s"]),
      "sq only runs for the even i."),
    T("from functools import lru_cache\nlog = []\n@lru_cache\ndef f(n):\n    log.append(n)\n    return n * 2\nf($a)\nf($b)\nf($a)\nlen(log)",
      lambda p: 2, "lru_cache remembers answers, so the repeat of $a never runs the body."),
    T("def dive(n, depth=1):\n    if n == 0:\n        return depth\n    return dive(n - 1, depth + 1)\ndive($a)",
      lambda p: p["a"] + 1, "The calls stack up one deeper each time, $a + 1 deep at the bottom."),
    T("calls = 0\ndef halve(n):\n    global calls\n    calls += 1\n    if n > 1:\n        halve(n // 2)\nhalve($n)\ncalls",
      lambda p: halvings(p["n"]), "Count how many times n can be halved before it reaches 1, plus the first call."),
    T("log = []\ndef even(n):\n    log.append(n)\n    return n == 0 or odd(n - 1)\ndef odd(n):\n    log.append(n)\n    return n != 0 and even(n - 1)\neven($s)\nlen(log)",
      lambda p: p["s"] + 1, "They hand over to each other, one call per number from $s down to 0."),
    T('log = []\ndef f():\n    log.append("$p")\n    g()\n    log.append("$q")\ndef g():\n    log.append("$x")\nf()\n"".join(log)',
      lambda p: p["p"] + p["x"] + p["q"], "f logs, calls g, which logs, then f logs again."),
    T('log = []\ndef f(x):\n    log.append("$p")\n    return x\ndef g(x):\n    log.append("$q")\n    return x\ng(f($a))\n"".join(log)',
      lambda p: p["p"] + p["q"], "The argument f($a) is worked out before g can run."),
    T(LOGF + "max(f($a), f($b), f($c))\nlen(log)", lambda p: 3, "All three arguments are worked out before max looks at them."),
    T(LOGF + "any(f(x) for x in [0, $a, $b])\nlen(log)", lambda p: 2,
      "any stops at the first truthy value, so $b is never reached."),
    T(LOGF + "all(f(x) for x in [$a, 0, $b])\nlen(log)", lambda p: 2, "all stops at the first falsy value."),
    T(LOGF + "any([f($a), f($b)])\nlen(log)", lambda p: 2, "A list is built in full before any sees it."),
    T(LOGF + "sorted([$a, $b, $c], key=f)\nlen(log)", lambda p: 3, "The key function is called once for each item."),
    T(LOGF + "list(map(f, [$a, $b, $c, $d]))\nlen(log)", lambda p: 4, "list() pulls every item through map."),
    T(LOGF + "map(f, [$a, $b])\nlen(log)", lambda p: 0, "map is lazy: nothing runs until something asks for the items."),
    T(LOGF + "m = map(f, [$a, $b, $c])\nnext(m)\nlen(log)", lambda p: 1, "next asks for one item, so f runs once."),
    T(BIG + "for v in [$a, $b, $c, $d]:\n    if is_big(v):\n        break\ncalls",
      lambda p: checks_until_big([p["a"], p["b"], p["c"], p["d"]], 5), "The loop stops at the first value over 5."),
    T(TICK + "[tick(), tick(), tick()]", lambda p: py_show([1, 2, 3]), "Each tick() adds 1 and gives the new n, in order."),
    T(TICK + "tick() * 10 + tick()", lambda p: 12, "The first tick() is 1, the second is 2: 1 * 10 + 2."),
    T(TICK + "tick() - tick()", lambda p: -1, "The left call happens first: 1 - 2."),
    T(TICK + "tick()\ntick()\ntick() * $a", lambda p: 3 * p["a"], "The third tick() gives 3."),
    T(HELLO + "repeat(hello, $a)\ncalls", lambda p: p["a"], "repeat calls the function it was given $a times."),
    T(HELLO + "repeat(hello, $a)\nrepeat(hello, $b)\ncalls", lambda p: p["a"] + p["b"], "$a calls, then $b more."),
    T(COUNT + "for i in range($m):\n    for j in range($r):\n        f()\ncalls", lambda p: p["m"] * p["r"],
      "$r calls on each of $m turns of the outer loop."),
    T("calls = 0\ndef f(n):\n    global calls\n    calls += 1\n    if n > 0:\n        f(n - 1)\n        f(n - 1)\nf($r)\ncalls",
      lambda p: tree_calls(p["r"]), "Every call above 0 makes two more, so the count roughly doubles each level."),
    T("moves = 0\ndef hanoi(n):\n    global moves\n    if n == 0:\n        return\n    hanoi(n - 1)\n    moves += 1\n    hanoi(n - 1)\nhanoi($m)\nmoves",
      lambda p: hanoi(p["m"]), "Each level does its own move between two copies of the level below."),
    T("log = []\ndef c():\n    log.append(1)\ndef b():\n    c()\n    c()\nfor _ in range($r):\n    b()\nlen(log)",
      lambda p: 2 * p["r"], "b runs $r times, and each b calls c twice."),
    T(COUNT.replace("calls += 1\n", "calls += 1\n    return calls\n") + "f() + f() * $a",
      lambda p: 1 + 2 * p["a"], "f() gives 1 on the first call and 2 on the second: 1 + 2 * $a."),
    T(LOGF + "[f(x) for x in [$a, $b, $c] if x > 4]\nlen(log)", lambda p: over([p["a"], p["b"], p["c"]], 4),
      "f only runs for the items over 4; the test itself is not a call."),
    T("log = []\ndef make():\n    log.append(1)\n    return []\ndef f(x=make()):\n    return x\nf()\nf()\nf()\nlen(log)",
      lambda p: 1, "A default is worked out once, when the def runs, not on each call."),
    T(COUNT + "g = lambda: f()\ncalls", lambda p: 0, "Making a lambda does not call anything."),
    T(COUNT + "g = lambda: f()\ng()\ng()\ncalls", lambda p: 2, "Each g() calls f once."),
    T(COUNT + "x = f\ny = f()\ncalls", lambda p: 1, "x = f only gives f another name; f() is the one call."),
    T(COUNT + "callbacks = [f, f, f]\nfor cb in callbacks:\n    cb()\ncalls", lambda p: 3, "Each cb() is a call to f."),
    T(GEN + "g = gen()\nnext(g)\nnext(g)\ncalls", lambda p: 2, "A generator runs only as far as it is asked: two next calls, two turns."),
    T(GEN + "g = gen()\ncalls", lambda p: 0, "Making the generator runs none of its body."),
    T(LOGF + "r = f($a) if f($b) > $a else f($c)\nlog",
      lambda p: py_show([p["b"], p["a"] if p["b"] > p["a"] else p["c"]]),
      "The test runs first; then only the branch that was chosen."),
]


# ── 4. Closure Counter ──────────────────────────────────────────────────

MAKE = "def make(n=0):\n    def inc():\n        nonlocal n\n        n += 1\n        return n\n    return inc\n"
ADDER = "def make_adder(n):\n    return lambda x: x + n\n"
COMPOSE = "def compose(f, g):\n    return lambda x: f(g(x))\ninc = lambda x: x + 1\ndbl = lambda x: x * 2\n"
ACC = "def acc():\n    total = 0\n    def add(v):\n        nonlocal total\n        total += v\n        return total\n    return add\n"
TWICE = "def twice(f):\n    def wrapper(x):\n        return f(f(x))\n    return wrapper\n"
FRESH_N = "Each call of make builds its own n, so the counters do not share."

CLOSURE = [
    T(MAKE + "c = make()\n[c() for _ in range($m)][-1]", lambda p: p["m"], "Each call adds 1 to the n that inc remembers."),
    T(MAKE + "c = make($a)\n[c() for _ in range($m)][-1]", lambda p: p["a"] + p["m"],
      "n starts at $a and the closure adds 1 on each of the $m calls."),
    T("def make(step):\n    n = 0\n    def inc():\n        nonlocal n\n        n += step\n        return n\n    return inc\nc = make($b)\n[c() for _ in range($m)][-1]",
      lambda p: p["b"] * p["m"], "Each call adds $b to the remembered n."),
    T(MAKE + "c = make()\nd = make()\n[c(), c(), d()][-1]", lambda p: 1, FRESH_N),
    T(MAKE + "c = make()\nd = c\n[c(), d(), c()][-1]", lambda p: 3, "d = c is the very same counter, so all three calls count together."),
    T("fs = []\nfor i in range($m):\n    fs.append(lambda: i)\nfs[0]()", lambda p: p["m"] - 1,
      "Every lambda reads the one variable i when it is called, after the loop ended on $m - 1."),
    T("fs = []\nfor i in range($m):\n    fs.append(lambda i=i: i)\nfs[0]()", lambda p: 0,
      "i=i fixes each lambda's own copy when it is made: the first one keeps 0."),
    T("fs = [lambda: i for i in range($m)]\nfs[0]() + fs[1]()", lambda p: 2 * (p["m"] - 1),
      "Both lambdas see the final i, $m - 1, so the sum is twice that."),
    T("fs = [lambda i=i: i for i in range($m)]\nfs[0]() + fs[1]()", lambda p: 1, "Each keeps its own i: 0 + 1."),
    T(ADDER + "add = make_adder($a)\nadd($b)", lambda p: p["a"] + p["b"], "The lambda remembers n from make_adder."),
    T(ADDER + "add = make_adder($a)\nadd(add($b))", lambda p: 2 * p["a"] + p["b"], "Two additions of $a to $b."),
    T(ADDER + "adders = [make_adder(i) for i in range($m)]\nadders[1]($a)", lambda p: 1 + p["a"],
      "Each call of make_adder has its own n, so there is no late binding here: n is 1."),
    T(ADDER + "adders = [make_adder(i) for i in range($m)]\nadders[-1]($a)", lambda p: p["m"] - 1 + p["a"],
      "The last adder remembers n = $m - 1."),
    T(ACC + "f = acc()\n[f($a), f($b), f($c)][-1]", lambda p: p["a"] + p["b"] + p["c"], "The closure keeps a running total."),
    T("def counter():\n    n = [0]\n    def inc():\n        n[0] += 1\n        return n[0]\n    return inc\nc = counter()\n[c() for _ in range($m)][-1]",
      lambda p: p["m"], "n[0] += 1 changes the list, so no nonlocal is needed."),
    T("def make():\n    items = []\n    def add(x):\n        items.append(x)\n        return len(items)\n    return add\nadd = make()\n[add($a), add($b), add($c)][-1]",
      lambda p: 3, "The closure's list grows by one on each call."),
    T("def times(n):\n    return lambda x: x * n\ndouble = times(2)\ntriple = times(3)\ndouble($a) + triple($b)",
      lambda p: 2 * p["a"] + 3 * p["b"], "double remembers 2 and triple remembers 3."),
    T(COMPOSE + "compose(inc, dbl)($a)", lambda p: 2 * p["a"] + 1, "dbl runs first, then inc."),
    T(COMPOSE + "compose(dbl, inc)($a)", lambda p: 2 * (p["a"] + 1), "inc runs first, then dbl."),
    T("x = $a\nf = lambda: x\nx = $b\nf()", lambda p: p["b"], "The lambda reads x when it is called, not when it was made."),
    T("def make():\n    fs = []\n    for i in range($m):\n        fs.append(lambda: i)\n    return fs\nmake()[0]()",
      lambda p: p["m"] - 1, "All the lambdas share the one i of that call, which ended on $m - 1."),
    T("def make():\n    n = 0\n    def inc():\n        nonlocal n\n        n += 1\n    return inc\nc = make()\nc()",
      lambda p: "None", "inc changes n but has no return, so the call gives None."),
    T("def make():\n    n = 0\n    def inc():\n        nonlocal n\n        n += 1\n    return inc, lambda: n\ninc, get = make()\n[inc() for _ in range($m)]\nget()",
      lambda p: p["m"], "inc and get share the one n."),
    T("def account(balance):\n    def deposit(x):\n        nonlocal balance\n        balance += x\n        return balance\n    return deposit\nd = account($a * 10)\n[d($b), d($c)][-1]",
      lambda p: p["a"] * 10 + p["b"] + p["c"], "The balance carries over from one deposit to the next."),
    T('ops = {"add": lambda x: x + $a, "mul": lambda x: x * $a}\nops["mul"]($b)', lambda p: p["a"] * p["b"],
      "The mul lambda multiplies by $a."),
    T("fs = [lambda x, n=n: x + n for n in range($m)]\nfs[-1]($a)", lambda p: p["a"] + p["m"] - 1,
      "n=n fixes each lambda's n: the last one adds $m - 1."),
    T("fs = [lambda x: x + n for n in range($m)]\nfs[0]($a)", lambda p: p["a"] + p["m"] - 1,
      "Late binding: even the first lambda sees the final n, $m - 1."),
    T("fs = list(map(lambda n: lambda x: x + n, range($m)))\nfs[1]($a)", lambda p: p["a"] + 1,
      "Each call of the outer lambda has its own n, so fs[1] adds 1."),
    T("def make(n):\n    def f():\n        return n\n    n = n + 1\n    return f\nmake($a)()", lambda p: p["a"] + 1,
      "f reads n when it runs, after n was changed."),
    T(TWICE + "def inc(x):\n    return x + 1\ntwice(inc)($a)", lambda p: p["a"] + 2, "wrapper remembers f and applies it twice."),
    T(TWICE + "@twice\ndef add3(x):\n    return x + 3\nadd3($a)", lambda p: p["a"] + 6,
      "@twice replaces add3 with the wrapper, which adds 3 twice."),
    T('def make(w):\n    return lambda: w + "!"\nshout = make("$w")\nshout()', lambda p: p["w"] + "!", "The lambda remembers w."),
    T('def make(w):\n    return lambda: w + "!"\ngreeters = [make(w) for w in ["$w", "$v"]]\ngreeters[1]()', lambda p: p["v"] + "!",
      "Each call of make has its own w."),
    T('fs = [lambda: w for w in ["$w", "$v"]]\nfs[0]()', lambda p: p["v"], "Late binding: both lambdas read the final w."),
    T('fs = []\nfor w in ["$w", "$v"]:\n    fs.append(lambda w=w: w)\nfs[0]()', lambda p: p["w"], "w=w gives each lambda its own copy."),
    T("def make():\n    x = $a\n    def get():\n        return x\n    x = x + $b\n    return get\nmake()()", lambda p: p["a"] + p["b"],
      "get reads x when it runs, after x was changed."),
    T("def outer():\n    n = 0\n    def inc():\n        nonlocal n\n        n += $a\n    inc()\n    inc()\n    return n\nouter()",
      lambda p: 2 * p["a"], "Each inc() adds $a to outer's n."),
    T("def make(items):\n    i = 0\n    def nxt():\n        nonlocal i\n        i += 1\n        return items[i - 1]\n    return nxt\nn = make([$a, $b, $c])\n[n(), n()][-1]",
      lambda p: p["b"], "The second call gives the second item."),
    T("def make(items):\n    i = 0\n    def nxt():\n        nonlocal i\n        i += 1\n        return items[i - 1]\n    return nxt\nn = make([$a, $b, $c])\n[n(), n(), n()][-1]",
      lambda p: p["c"], "The third call gives the third item."),
    T("def multiplier(n):\n    def m(x):\n        return x * n\n    return m\nmultiplier($a)($b)", lambda p: p["a"] * p["b"],
      "m remembers n."),
    T("def make(n):\n    return lambda: n\nf = make($a)\nn = $b\nf()", lambda p: p["a"], "The lambda uses make's n, not the global n."),
    T("k = $a\ndef make():\n    return lambda: k\nf = make()\nk = $b\nf()", lambda p: p["b"],
      "k is a global, read when the lambda runs."),
    T("def make():\n    total = 0\n    def add(x):\n        nonlocal total\n        total += x\n        return total\n    return add\ns1 = make()\ns2 = make()\n[s1($a), s2($b)][-1]",
      lambda p: p["b"], "s2 has its own total, so $a never reached it."),
    T("fs = [lambda: i for i in range($m)]\n[f() for f in fs]", lambda p: py_show([p["m"] - 1] * p["m"]),
      "Every lambda reads the final i."),
    T("fs = [lambda i=i: i for i in range($m)]\n[f() for f in fs]", lambda p: py_show(list(range(p["m"]))),
      "Each lambda kept its own i."),
]


# ── 5. Args Count ───────────────────────────────────────────────────────

def biggest(xs: list[int]) -> int:
    best = xs[0]
    for x in xs[1:]:
        if x > best:
            best = x
    return best


def smallest(xs: list[int]) -> int:
    best = xs[0]
    for x in xs[1:]:
        if x < best:
            best = x
    return best


def total(xs: list[int]) -> int:
    t = 0
    for x in xs:
        t += x
    return t


STAR = "def f(*args):\n    return len(args)\n"

ARGS = [
    T(STAR + "f($a, $b, $c)", lambda p: 3, "*args collects every extra argument: three here."),
    T(STAR + "f($a, $b)", lambda p: 2, "*args collects both arguments."),
    T(STAR + "f()", lambda p: 0, "With nothing passed, args is empty."),
    T(STAR + "f([$a, $b, $c])", lambda p: 1, "A list passed as it is counts as ONE argument."),
    T(STAR + "f(*[$a, $b, $c])", lambda p: 3, "The * in a call spreads the list into separate arguments."),
    T(STAR + "f(*[$a, $b], $c)", lambda p: 3, "Two spread from the list, plus $c."),
    T(STAR + 'f(*"$w")', lambda p: len(p["w"]), "A string spreads into its letters, one argument each."),
    T(STAR + "f(*range($m))", lambda p: p["m"], "range($m) spreads into $m numbers."),
    T(STAR + "f(*[], *[$a, $b])", lambda p: 2, "An empty list adds nothing."),
    T(STAR + "f(*[$a, $b], *[$c, $d])", lambda p: 4, "Two lists spread: 2 + 2."),
    T("def f(a, *rest):\n    return len(rest)\nf($a, $b, $c, $d)", lambda p: 3, "a takes the first; rest gets the other three."),
    T("def f(a, *rest):\n    return rest\nf($a, $b, $c)", lambda p: py_show((p["b"], p["c"])), "rest is a tuple of what is left."),
    T("def f(*args):\n    return args\nf($a)", lambda p: py_show((p["a"],)), "args is always a tuple, even with one item."),
    T("def f(*args):\n    return args\nf()", lambda p: "()", "No arguments: an empty tuple."),
    T("def f(*args):\n    return sum(args)\nf($a, $b, $c)", lambda p: p["a"] + p["b"] + p["c"], "sum adds up the tuple."),
    T("def f(*args):\n    return args[-1]\nf($a, $b)", lambda p: p["b"], "The last item of the tuple."),
    T("def f(**kw):\n    return len(kw)\nf(x=$a, y=$b)", lambda p: 2, "**kw collects the keyword arguments into a dict."),
    T("def f(**kw):\n    return list(kw)\nf(y=$a, x=$b)", lambda p: py_show(["y", "x"]), "list of a dict gives its keys, in the order given."),
    T("def f(**kw):\n    return sum(kw.values())\nf(p=$a, q=$b, r=$c)", lambda p: p["a"] + p["b"] + p["c"],
      "kw.values() are the three numbers."),
    T("def f(*args, **kw):\n    return len(args) + len(kw)\nf($a, $b, x=$c)", lambda p: 3, "Two positional plus one keyword."),
    T("def f(*args, **kw):\n    return (len(args), len(kw))\nf($a, x=$b, y=$c)", lambda p: py_show((1, 2)),
      "One positional, two keyword."),
    T("def f(a, b):\n    return a - b\nnums = [$a, $b]\nf(*nums)", lambda p: p["a"] - p["b"], "*nums hands over $a then $b."),
    T('def f(a, b):\n    return a - b\nf(**{"b": $a, "a": $b})', lambda p: p["b"] - p["a"], "** matches the dict's keys to the parameter names."),
    T("first, *rest = [$a, $b, $c, $d]\nrest", lambda p: py_show([p["b"], p["c"], p["d"]]), "The starred name takes whatever is left, as a list."),
    T("first, *rest = [$a, $b, $c, $d]\nlen(rest)", lambda p: 3, "first takes one; rest takes the other three."),
    T("*init, last = [$a, $b, $c]\ninit", lambda p: py_show([p["a"], p["b"]]), "last takes the final item; init the rest."),
    T("first, *mid, last = [$a, $b, $c, $d]\nmid", lambda p: py_show([p["b"], p["c"]]), "mid is what is between the first and the last."),
    T("def f(a, b=$b, *args):\n    return len(args)\nf($a, $b, $c, $d)", lambda p: 2, "a and b take the first two; args gets the other two."),
    T("def f(a, *args, k=1):\n    return k\nf($a, $b, k=$c)", lambda p: p["c"], "k is keyword-only: it can only be given by name."),
    T("def f(*args, k=1):\n    return len(args) + k\nf($a, $b, k=$c)", lambda p: 2 + p["c"], "Two in args, plus k."),
    T('d = {**{"a": $a}, **{"b": $b}}\nlen(d)', lambda p: 2, "** merges the two dicts."),
    T('d = {**{"a": $a}, **{"a": $b}}\nd["a"]', lambda p: p["b"], "A later key wins."),
    T("[*[$a, $b], *[$c]]", lambda p: py_show([p["a"], p["b"], p["c"]]), "* unpacks each list into the new one."),
    T('len([*[$a, $b], *"$w"])', lambda p: 2 + len(p["w"]), "The word unpacks into its letters."),
    T("max(*[$a, $b, $c])", lambda p: biggest([p["a"], p["b"], p["c"]]), "max gets three separate arguments."),
    T("def total(*nums):\n    t = 0\n    for n in nums:\n        t += n\n    return t\ntotal(*[$a, $b], $c)",
      lambda p: p["a"] + p["b"] + p["c"], "All three numbers arrive in nums."),
    T('def f(**kw):\n    return kw.get("z", 0)\nf(x=$a, y=$b)', lambda p: 0, "There is no z, so get gives its default."),
    T('def f(**kw):\n    return kw["x"]\nf(**{"x": $a})', lambda p: p["a"], "** turns the dict back into x=$a."),
    T("def f(a, **kw):\n    return len(kw)\nf($a, x=$b, y=$c)", lambda p: 2, "a takes the first; kw gets x and y."),
    T("def f(a, b, *args):\n    return a + b + len(args)\nf($a, $b, $c, $d)", lambda p: p["a"] + p["b"] + 2, "args holds the last two."),
    T("def f(*args):\n    return type(args).__name__\nf($a)", lambda p: "tuple", "*args is a tuple."),
    T("def f(**kw):\n    return type(kw).__name__\nf(x=$a)", lambda p: "dict", "**kw is a dict."),
    T("def show(a, b=2, *c, **d):\n    return len(c) + len(d)\nshow($a, $b, $c, $d, x=$k)", lambda p: 3,
      "a and b take two; c gets two more; d gets x."),
    T("def f(*args):\n    return sum(args) / len(args)\nf($a, $b)", lambda p: py_div(p["a"] + p["b"], 2), "The average of two: a float."),
    T("def f(*args):\n    return sum(args) / len(args)\nf($a, $b, $c, $d)", lambda p: py_div(total([p["a"], p["b"], p["c"], p["d"]]), 4),
      "The average of four: a float."),
    T("def f(*args):\n    return max(args) - min(args)\nf($a, $b, $c)", lambda p: biggest([p["a"], p["b"], p["c"]]) - smallest([p["a"], p["b"], p["c"]]),
      "The biggest minus the smallest."),
    T("def f(*args):\n    return list(reversed(args))\nf($a, $b, $c)", lambda p: py_show([p["c"], p["b"], p["a"]]), "reversed turns it round."),
    T("def f(*args):\n    return [x * 2 for x in args]\nf($a, $b)", lambda p: py_show([p["a"] * 2, p["b"] * 2]), "Double each argument."),
    T("def f(a, b, c):\n    return a + b + c\nf(*[$a], *[$b, $c])", lambda p: p["a"] + p["b"] + p["c"], "Three values spread across the three parameters."),
    T('def f(x, y):\n    return x - y\nkw = {"x": $a, "y": $b}\nf(**kw)', lambda p: p["a"] - p["b"], "x=$a, y=$b."),
    T("def f(*args):\n    args += ($a,)\n    return len(args)\nf($b, $c)", lambda p: 3, "+= on a tuple builds a new, longer one."),
    T("def f(a, b):\n    return b\nf(*[$a, $b])", lambda p: p["b"], "The list spreads into a then b."),
]


# ── 6. Recursion Result ─────────────────────────────────────────────────

def sum_to(n: int) -> int:
    return 0 if n == 0 else n + sum_to(n - 1)


def power(b: int, e: int) -> int:
    return 1 if e == 0 else b * power(b, e - 1)


def rev_text(s: str) -> str:
    return "" if s == "" else rev_text(s[1:]) + s[0]


def down_text(n: int) -> str:
    return "go" if n == 0 else str(n) + down_text(n - 1)


def up_text(n: int) -> str:
    return "" if n == 0 else up_text(n - 1) + str(n)


def max_digit(n: int) -> int:
    if n < 10:
        return n
    rest = max_digit(fdiv(n, 10))
    return fmod(n, 10) if fmod(n, 10) > rest else rest


def nested_sum(x: Any) -> int:
    if isinstance(x, list):
        t = 0
        for item in x:
            t += nested_sum(item)
        return t
    return x


def ordered(xs: list[int]) -> bool:
    return True if len(xs) < 2 else xs[0] <= xs[1] and ordered(xs[1:])


def odds_upto(n: int) -> int:
    return 0 if n <= 0 else fmod(n, 2) + odds_upto(n - 1)


def skip_two_sum(n: int) -> int:
    return 0 if n <= 0 else n + skip_two_sum(n - 2)


def triple_fib(n: int) -> int:
    return n if n <= 2 else triple_fib(n - 1) + triple_fib(n - 2) + triple_fib(n - 3)


def range_sum(a: int, b: int) -> int:
    return 0 if a > b else a + range_sum(a + 1, b)


def largest(xs: list[int]) -> int:
    if len(xs) == 1:
        return xs[0]
    rest = largest(xs[1:])
    return xs[0] if xs[0] > rest else rest


def has(xs: list[int], t: int) -> bool:
    return False if not xs else xs[0] == t or has(xs[1:], t)


PALINDROMES = ("level", "radar", "noon", "civic", "kayak")
NOT_PALINDROMES = ("drone", "carrot", "farm", "maple", "pumpkin", "wheat")

RECUR = [
    T("def fact(n):\n    return 1 if n <= 1 else n * fact(n - 1)\nfact($s)", lambda p: fact(p["s"]), "n * (n-1) * ... * 1."),
    T("def fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)\nfib($s)", lambda p: fib(p["s"]),
      "Each number is the sum of the two before: 0, 1, 1, 2, 3, 5, 8, 13..."),
    T("def total(n):\n    if n == 0:\n        return 0\n    return n + total(n - 1)\ntotal($s)", lambda p: sum_to(p["s"]), "$s + ($s - 1) + ... + 1."),
    T("def digits(n):\n    if n < 10:\n        return n\n    return n % 10 + digits(n // 10)\ndigits($big)", lambda p: digit_sum(p["big"]),
      "It adds the last digit to the sum of the rest."),
    T("def power(b, e):\n    if e == 0:\n        return 1\n    return b * power(b, e - 1)\npower($a, $r)", lambda p: power(p["a"], p["r"]),
      "$a multiplied by itself $r times."),
    T("def g(a, b):\n    if b == 0:\n        return a\n    return g(b, a % b)\ng($gx, $gy)", lambda p: gcd(p["gx"], p["gy"]),
      "Euclid's way: keep replacing (a, b) with (b, a % b) until b is 0."),
    T('def rev(s):\n    if s == "":\n        return ""\n    return rev(s[1:]) + s[0]\nrev("$w")', lambda p: rev_text(p["w"]),
      "Each call puts its first letter after the reverse of the rest."),
    T('def down(n):\n    if n == 0:\n        return "go"\n    return str(n) + down(n - 1)\ndown($m)', lambda p: down_text(p["m"]),
      "The digits count down, then the base case adds go."),
    T('def up(n):\n    if n == 0:\n        return ""\n    return up(n - 1) + str(n)\nup($m)', lambda p: up_text(p["m"]),
      "The smaller case comes first, so the digits count up."),
    T('def length(s):\n    if s == "":\n        return 0\n    return 1 + length(s[1:])\nlength("$w")', lambda p: len(p["w"]),
      "One for each letter, until the string is empty."),
    T('def count(s, c):\n    if s == "":\n        return 0\n    return (s[0] == c) + count(s[1:], c)\ncount("$w$v", "$x")',
      lambda p: count_in(p["w"] + p["v"], p["x"]), "True counts as 1, so it adds one for each matching letter."),
    T("def total(xs):\n    if not xs:\n        return 0\n    return xs[0] + total(xs[1:])\ntotal([$a, $b, $c])", lambda p: p["a"] + p["b"] + p["c"],
      "The first item plus the total of the rest."),
    T("def biggest(xs):\n    if len(xs) == 1:\n        return xs[0]\n    rest = biggest(xs[1:])\n    return xs[0] if xs[0] > rest else rest\nbiggest([$a, $b, $c, $d])",
      lambda p: largest([p["a"], p["b"], p["c"], p["d"]]), "The bigger of the first and the biggest of the rest."),
    T("def pal(s):\n    if len(s) < 2:\n        return True\n    return s[0] == s[-1] and pal(s[1:-1])\npal(\"$pw\")",
      lambda p: py_show(is_palindrome(p["pw"])), "It compares the two ends, then the inside."),
    T('def bits(n):\n    if n == 0:\n        return ""\n    return bits(n // 2) + str(n % 2)\nbits($n)', lambda p: bits(p["n"]),
      "The binary digits of n, written from the biggest place down."),
    T("def steps(n):\n    if n == 1:\n        return 0\n    if n % 2 == 0:\n        return 1 + steps(n // 2)\n    return 1 + steps(3 * n + 1)\nsteps($s)",
      lambda p: collatz(p["s"]), "Halve when even, triple and add 1 when odd: count the steps to 1."),
    T("def pow2(n):\n    return 1 if n == 0 else 2 * pow2(n - 1)\npow2($s)", lambda p: power(2, p["s"]), "2 doubled $s times."),
    T("def ones(n):\n    if n < 2:\n        return n\n    return ones(n // 2) + n % 2\nones($n)", lambda p: popcount(p["n"]),
      "The number of 1s in n's binary digits."),
    T("def mul(a, b):\n    if b == 0:\n        return 0\n    return a + mul(a, b - 1)\nmul($a, $r)", lambda p: p["a"] * p["r"],
      "$a added up $r times."),
    T("def add(a, b):\n    if b == 0:\n        return a\n    return add(a + 1, b - 1)\nadd($a, $b)", lambda p: p["a"] + p["b"],
      "It moves 1 from b over to a each time."),
    T("def hanoi(n):\n    if n == 0:\n        return 0\n    return 2 * hanoi(n - 1) + 1\nhanoi($s)", lambda p: hanoi(p["s"]),
      "Twice the moves of the smaller tower, plus one."),
    T("def rev(xs):\n    if not xs:\n        return []\n    return rev(xs[1:]) + [xs[0]]\nrev([$a, $b, $c])", lambda p: py_show([p["c"], p["b"], p["a"]]),
      "The reverse of the rest, then the first item."),
    T("def flat(x):\n    if isinstance(x, list):\n        return sum(flat(i) for i in x)\n    return x\nflat([$a, [$b, $c], [$d]])",
      lambda p: p["a"] + p["b"] + p["c"] + p["d"], "A list is the sum of its parts; a number is itself."),
    T('def stars(n):\n    if n == 0:\n        return ""\n    return stars(n - 1) + "*"\nstars($m)', lambda p: "*" * p["m"], "One star per level."),
    T("def down(n):\n    if n == 0:\n        return []\n    return [n] + down(n - 1)\ndown($m)", lambda p: py_show(list(reversed(list(range(1, p["m"] + 1))))),
      "n goes first, then the countdown of the rest."),
    T('def alt(s):\n    if s == "":\n        return ""\n    return s[0] + alt(s[2:])\nalt("$w")', lambda p: every_other(p["w"]),
      "It keeps a letter, skips one, and carries on."),
    T("def f(n):\n    if n > 0:\n        f(n - 1)\nf($m)", lambda p: "None", "f never returns anything, so the call gives None."),
    T("def f(n):\n    if n == 0:\n        return 0\n    f(n - 1)\nf($s)", lambda p: "None",
      "Only the base case returns; the recursive line throws its answer away, so the call gives None."),
    T("def has(xs, t):\n    if not xs:\n        return False\n    return xs[0] == t or has(xs[1:], t)\nhas([$a, $b, $c], $d)",
      lambda p: py_show(has([p["a"], p["b"], p["c"]], p["d"])), "True if the target is the first item or somewhere in the rest."),
    T("def sq(n):\n    if n == 0:\n        return []\n    return sq(n - 1) + [n * n]\nsq($m)", lambda p: py_show([k * k for k in range(1, p["m"] + 1)]),
      "The squares from 1 up, smallest first."),
    T('def f(n):\n    if n == 0:\n        return "0"\n    return f(n - 1) + str(n)\nf($m)', lambda p: "0" + up_text(p["m"]), "It starts from 0 and adds each number as the calls return."),
    T("def f(n):\n    if n == 0:\n        return 1\n    return 2 * f(n - 1) + 1\nf($m)", lambda p: power(2, p["m"] + 1) - 1,
      "1, 3, 7, 15, 31, ...: each is twice the one before, plus 1."),
    T("def f(n):\n    if n <= 1:\n        return 1\n    return f(n - 1) + f(n - 2)\nf($s)", lambda p: fib1(p["s"]), "Like Fibonacci, but starting 1, 1, 2, 3, 5..."),
    T("def f(n):\n    if n <= 2:\n        return n\n    return f(n - 1) + f(n - 2) + f(n - 3)\nf($s)", lambda p: triple_fib(p["s"]),
      "Each number is the sum of the three before it."),
    T("def f(n):\n    if n == 0:\n        return 0\n    return f(n - 1) + 2 * n - 1\nf($s)", lambda p: p["s"] * p["s"], "The odd numbers 1 + 3 + 5 ... add up to a square."),
    T("def f(n):\n    if n <= 0:\n        return 0\n    return n + f(n - 2)\nf($s)", lambda p: skip_two_sum(p["s"]), "It adds every second number down from $s while it is above 0."),
    T("def flip(n, acc=0):\n    if n == 0:\n        return acc\n    return flip(n // 10, acc * 10 + n % 10)\nflip($big)", lambda p: flip_digits(p["big"]),
      "Each call moves the last digit of n onto the end of acc."),
    T("def digits(n):\n    return 1 if n < 10 else 1 + digits(n // 10)\ndigits($big)", lambda p: digit_count(p["big"]), "One for each digit."),
    T("def f(a, b):\n    if a > b:\n        return 0\n    return a + f(a + 1, b)\nf($a, $b)", lambda p: range_sum(p["a"], p["b"]),
      "It adds a, a + 1, ... up to b, and gives 0 when a is already past b."),
    T("def f(n):\n    if n == 0:\n        return 0\n    return 1 + f(n // 2)\nf($n)", lambda p: halvings(p["n"]), "It counts how many times n can be halved before it reaches 0."),
    T("def f(n):\n    if n < 10:\n        return n\n    return max(n % 10, f(n // 10))\nf($big)", lambda p: max_digit(p["big"]), "The biggest digit."),
    T('def rep(s, n):\n    if n == 0:\n        return ""\n    return s + rep(s, n - 1)\nrep("$w", $r)', lambda p: p["w"] * p["r"], "The word, $r times over."),
    T("def ordered(xs):\n    if len(xs) < 2:\n        return True\n    return xs[0] <= xs[1] and ordered(xs[1:])\nordered([$a, $b, $c])",
      lambda p: py_show(ordered([p["a"], p["b"], p["c"]])), "True only if every item is no bigger than the next."),
    T("def f(n):\n    if n <= 0:\n        return 0\n    return n % 2 + f(n - 1)\nf($s)", lambda p: odds_upto(p["s"]), "n % 2 is 1 for each odd number, so it counts the odds up to $s."),
    T('def rev(s):\n    if len(s) <= 1:\n        return s\n    return s[-1] + rev(s[:-1])\nrev("$w")', lambda p: rev_text(p["w"]), "The last letter first, then the reverse of the rest."),
    T("def f(n):\n    if n == 0:\n        return 0\n    return f(n - 1) + 2\nf($s)", lambda p: 2 * p["s"], "Each level adds 2."),
    T("def f(n, acc=1):\n    if n <= 1:\n        return acc\n    return f(n - 1, acc * n)\nf($s)", lambda p: fact(p["s"]), "The product builds up in acc as n counts down."),
]


# ── 7. Map Filter Reduce ────────────────────────────────────────────────

RED = "from functools import reduce\n"


def _abc(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"]]


def _abcd(p: dict) -> list[int]:
    return [p["a"], p["b"], p["c"], p["d"]]


def pick(xs: list, keep: Callable[[Any], bool]) -> list:
    out = []
    for x in xs:
        if keep(x):
            out.append(x)
    return out


def change(xs: list, how: Callable[[Any], Any]) -> list:
    return [how(x) for x in xs]


def first_letters(ws: list[str]) -> list[str]:
    return [w[0] for w in ws]


def digit_total(n: int) -> int:
    return digit_sum(n)


XS3 = "[$a, $b, $c]"
XS4 = "[$a, $b, $c, $d]"

MFR = [
    T("list(map(lambda x: x * 2, " + XS3 + "))", lambda p: py_show(change(_abc(p), lambda x: x * 2)), "map applies the lambda to every item: each is doubled."),
    T("list(map(lambda x: x + $d, " + XS3 + "))", lambda p: py_show(change(_abc(p), lambda x: x + p["d"])), "Each item gets $d added."),
    T("list(map(lambda x: x * x, " + XS3 + "))", lambda p: py_show(change(_abc(p), lambda x: x * x)), "Each item is squared."),
    T("list(map(lambda x: x % 3, " + XS4 + "))", lambda p: py_show(change(_abcd(p), lambda x: fmod(x, 3))), "Each item's remainder when divided by 3."),
    T("list(map(lambda x: x // 2, " + XS4 + "))", lambda p: py_show(change(_abcd(p), lambda x: fdiv(x, 2))), "Each item halved, rounded down."),
    T("list(map(str, " + XS3 + "))", lambda p: py_show(change(_abc(p), str)), "str turns each number into text, so the items show in quotes."),
    T("list(map(lambda x: -x, " + XS3 + "))", lambda p: py_show(change(_abc(p), lambda x: -x)), "Each item with its sign flipped."),
    T("list(filter(lambda x: x > 5, " + XS4 + "))", lambda p: py_show(pick(_abcd(p), lambda x: x > 5)), "filter keeps the items for which the lambda is True."),
    T("list(filter(lambda x: x % 2 == 0, " + XS4 + "))", lambda p: py_show(pick(_abcd(p), lambda x: fmod(x, 2) == 0)), "Only the even ones stay."),
    T("list(filter(lambda x: x % 2, " + XS4 + "))", lambda p: py_show(pick(_abcd(p), lambda x: fmod(x, 2) == 1)), "x % 2 is 1 (truthy) for odd numbers: those stay."),
    T("list(filter(lambda x: x != $a, " + XS4 + "))", lambda p: py_show(pick(_abcd(p), lambda x: x != p["a"])), "Everything but $a stays."),
    T("list(filter(lambda x: x < $a, " + XS4 + "))", lambda p: py_show(pick(_abcd(p), lambda x: x < p["a"])), "Only items below $a stay (maybe none: [])."),
    T("sum(map(lambda x: x * 2, " + XS3 + "))", lambda p: 2 * (p["a"] + p["b"] + p["c"]), "Double each, then add them up."),
    T("sum(filter(lambda x: x > 4, " + XS4 + "))", lambda p: fold(pick(_abcd(p), lambda x: x > 4), lambda s, x: s + x, 0), "Add up only the items over 4."),
    T("len(list(filter(lambda x: x % 2 == 0, " + XS4 + ")))", lambda p: len(pick(_abcd(p), lambda x: fmod(x, 2) == 0)), "How many items are even."),
    T(RED + "reduce(lambda acc, x: acc + x, " + XS3 + ")", lambda p: p["a"] + p["b"] + p["c"], "reduce folds the list into one value: here a running sum."),
    T(RED + "reduce(lambda acc, x: acc * x, " + XS3 + ")", lambda p: p["a"] * p["b"] * p["c"], "A running product."),
    T(RED + "reduce(lambda acc, x: acc + x, " + XS3 + ", $d)", lambda p: p["a"] + p["b"] + p["c"] + p["d"], "The third argument is where the running total starts."),
    T(RED + "reduce(lambda acc, x: acc - x, " + XS3 + ")", lambda p: p["a"] - p["b"] - p["c"], "It starts with the first item, then subtracts the others."),
    T(RED + "reduce(lambda acc, x: x - acc, " + XS3 + ")", lambda p: p["c"] - (p["b"] - p["a"]), "Each step is new item minus the running value."),
    T(RED + "reduce(lambda a, b: a if a > b else b, " + XS4 + ")", lambda p: biggest(_abcd(p)), "It keeps the bigger of the running value and each item."),
    T(RED + "reduce(lambda acc, x: acc * 10 + x, " + XS3 + ")", lambda p: 100 * p["a"] + 10 * p["b"] + p["c"], "Each step shifts the digits left and adds the next."),
    T(RED + 'reduce(lambda acc, x: acc + str(x), ' + XS3 + ', "")', lambda p: str(p["a"]) + str(p["b"]) + str(p["c"]), "It joins the numbers as text."),
    T(RED + "reduce(lambda acc, x: [x] + acc, " + XS3 + ", [])", lambda p: py_show([p["c"], p["b"], p["a"]]), "Each item goes in front of the running list: reversed."),
    T("sum(x for x in " + XS4 + " if x > 4)", lambda p: fold(pick(_abcd(p), lambda x: x > 4), lambda s, x: s + x, 0), "A generator with a condition, summed."),
    T("sum([x * x for x in " + XS3 + "])", lambda p: p["a"] * p["a"] + p["b"] * p["b"] + p["c"] * p["c"], "The squares, added up."),
    T("sum(map(lambda x: x % 3, " + XS4 + "))", lambda p: fold(change(_abcd(p), lambda x: fmod(x, 3)), lambda s, x: s + x, 0), "Add up the remainders."),
    T("max(map(lambda x: x % 5, " + XS4 + "))", lambda p: biggest(change(_abcd(p), lambda x: fmod(x, 5))), "The biggest remainder."),
    T("list(map(lambda x, y: x + y, [$a, $b], [$c, $d]))", lambda p: py_show([p["a"] + p["c"], p["b"] + p["d"]]), "map with two lists pairs items by position."),
    T("list(map(lambda t: t[0] * t[1], zip([$a, $b], [$c, $d])))", lambda p: py_show([p["a"] * p["c"], p["b"] * p["d"]]), "zip pairs the items; the lambda multiplies each pair."),
    T("sorted(" + XS4 + ", key=lambda x: x % 3)", lambda p: py_show(stable_sort(_abcd(p), lambda x: fmod(x, 3))),
      "Sorted by remainder; items with the same remainder keep their order."),
    T("min(" + XS4 + ", key=lambda x: abs(x - 5))", lambda p: first_best(_abcd(p), lambda x: abs(x - 5), False), "The item closest to 5 (the first, if two tie)."),
    T("max(" + XS4 + ", key=lambda x: x % 5)", lambda p: first_best(_abcd(p), lambda x: fmod(x, 5), True), "The item with the biggest remainder (the first, if two tie)."),
    T('list(map(len, ["$w", "$v", "$pw"]))', lambda p: py_show([len(p["w"]), len(p["v"]), len(p["pw"])]), "len of each word."),
    T('list(map(str.upper, ["$w", "$v"]))', lambda p: py_show([upper(p["w"]), upper(p["v"])]), "upper-case each word."),
    T("list(filter(None, [0, $a, 0, $b]))", lambda p: py_show([p["a"], p["b"]]), "With None as the test, filter keeps the truthy items."),
    T('list(filter(lambda s: len(s) > 4, ["$w", "$v", "$pw"]))', lambda p: py_show(pick([p["w"], p["v"], p["pw"]], lambda s: len(s) > 4)),
      "Only words longer than 4 letters stay."),
    T('list(map(lambda s: s[0], ["$w", "$v", "$pw"]))', lambda p: py_show(first_letters([p["w"], p["v"], p["pw"]])), "The first letter of each word."),
    T('sum(map(len, ["$w", "$v"]))', lambda p: len(p["w"]) + len(p["v"]), "The lengths, added up."),
    T("any(map(lambda x: x > 8, " + XS4 + "))", lambda p: py_show(biggest(_abcd(p)) > 8), "True if at least one item is over 8."),
    T("all(x > 4 for x in " + XS3 + ")", lambda p: py_show(smallest(_abc(p)) > 4), "True only if every item is over 4."),
    T("list(filter(lambda x: x % 2 == 0, map(lambda x: x * 3, " + XS4 + ")))", lambda p: py_show(pick(change(_abcd(p), lambda x: x * 3), lambda x: fmod(x, 2) == 0)),
      "Triple each, then keep the even results."),
    T("list(map(lambda x: x * 2, filter(lambda x: x > 4, " + XS4 + ")))", lambda p: py_show(change(pick(_abcd(p), lambda x: x > 4), lambda x: x * 2)),
      "Keep the items over 4, then double them."),
    T("[x * 2 for x in " + XS4 + " if x > 4]", lambda p: py_show(change(pick(_abcd(p), lambda x: x > 4), lambda x: x * 2)),
      "A comprehension: filter with if, then double."),
    T(RED + "reduce(lambda acc, x: acc + 1, " + XS4 + ", 0)", lambda p: 4, "It adds 1 for each item: a length."),
    T(RED + 'reduce(lambda acc, w: acc + len(w), ["$w", "$v"], 0)', lambda p: len(p["w"]) + len(p["v"]), "Running total of the word lengths."),
    T("sum(map(int, str($big)))", lambda p: digit_total(p["big"]), "Each digit as a number, added up."),
    T('dict(map(lambda w: (w, len(w)), ["$w", "$v"]))', lambda p: py_show({p["w"]: len(p["w"]), p["v"]: len(p["v"])}), "Each word paired with its length."),
    T("list(map(lambda f: f($a), [lambda x: x + 1, lambda x: x * 2]))", lambda p: py_show([p["a"] + 1, p["a"] * 2]), "Each lambda is called with $a."),
    T("sum(range($m + 1))", lambda p: sum_to(p["m"]), "0 + 1 + ... + $m."),
    T("list(map(lambda x: x * x, range($m)))", lambda p: py_show([k * k for k in range(p["m"])]), "The squares of 0 up to $m - 1."),
    T("list(filter(lambda x: x % 3 == 0, range(10)))", lambda p: py_show([0, 3, 6, 9]), "The multiples of 3 below 10, starting at 0."),
    T("list(map(lambda x: x * x, filter(lambda x: x % 2, range($s))))", lambda p: py_show([k * k for k in range(p["s"]) if fmod(k, 2) == 1]),
      "The squares of the odd numbers below $s."),
]


# ── 8. Pass or Copy ─────────────────────────────────────────────────────

PC = prow

BOX = "class Box:\n    def __init__(self, n):\n        self.n = n\n"
L2 = "a = [$a, $b]"
L3 = "a = [$a, $b, $c]"
D1 = 'a = {"x": $a}'
def _not_sorted(p: dict) -> bool:
    xs = [p["a"], p["b"], p["c"]]
    return isort(xs) != xs


def _desc_changes(p: dict) -> bool:
    xs = [p["a"], p["b"], p["c"]]
    return reverse(isort(xs)) != xs


COPY = [
    PC("def f(n):\n    n += 1\na = $a", "f(a)", False, "A number cannot change in place: n += 1 only rebinds the local n."),
    PC("def f(n):\n    n = n * 2\na = $a", "f(a)", False, "n = ... points the local name n somewhere else; a is untouched."),
    PC('def f(s):\n    s += "!"\na = "$w"', "f(a)", False, "A string cannot change in place; += builds a new one for the local s."),
    PC('def f(s):\n    s.upper()\na = "$w"', "f(a)", False, "upper() gives a new string, which is thrown away."),
    PC("def f(xs):\n    xs.append($c)\n" + L2, "f(a)", True, "The function got the same list, so append changes a's list."),
    PC("def f(xs):\n    xs += [$c]\n" + L2, "f(a)", True, "+= on a list changes it in place."),
    PC("def f(xs):\n    xs = xs + [$c]\n" + L2, "f(a)", False, "xs + [...] builds a new list; only the local xs points to it."),
    PC("def f(xs):\n    xs = [$c]\n" + L2, "f(a)", False, "Pointing xs at a new list leaves a's list alone."),
    PC("def f(xs):\n    xs.sort()\n" + L3, "f(a)", _not_sorted, "sort() works in place: it changes the list unless it was already in order."),
    PC("def f(xs):\n    sorted(xs)\n" + L3, "f(a)", False, "sorted() builds a new list, which is thrown away."),
    PC("def f(xs):\n    xs.reverse()\n" + L3, "f(a)", True, "reverse() works in place."),
    PC("def f(xs):\n    xs[0] = 99\n" + L2, "f(a)", True, "Assigning to an item changes the shared list."),
    PC("def f(xs):\n    xs.clear()\n" + L2, "f(a)", True, "clear() empties the shared list."),
    PC("def f(xs):\n    xs = []\n" + L2, "f(a)", False, "xs = [] points the local name at a new empty list; a keeps its items."),
    PC("def f(xs):\n    del xs[0]\n" + L2, "f(a)", True, "del removes an item from the shared list."),
    PC("def f(xs):\n    xs.pop()\n" + L2, "f(a)", True, "pop removes the last item from the shared list."),
    PC('def f(d):\n    d["k"] = $b\n' + D1, "f(a)", True, "The function got the same dict, so the new key shows in a."),
    PC("def f(d):\n    d = {}\n" + D1, "f(a)", False, "d = {} points the local name at a new dict."),
    PC('def f(d):\n    d.update({"y": $b})\n' + D1, "f(a)", True, "update changes the shared dict in place."),
    PC('def f(d):\n    d = {**d, "y": $b}\n' + D1, "f(a)", False, "{**d, ...} builds a new dict for the local name."),
    PC('def f(d):\n    d.pop("x")\n' + D1, "f(a)", True, "pop removes the key from the shared dict."),
    PC('def f(d):\n    d.get("y", $b)\n' + D1, "f(a)", False, "get only looks."),
    PC('def f(d):\n    d.setdefault("y", $b)\n' + D1, "f(a)", True, "setdefault adds the key when it is missing."),
    PC("def f(t):\n    t += ($c,)\na = ($a, $b)", "f(a)", False, "A tuple cannot change; += builds a new one for the local t."),
    PC("def f(t):\n    t[0].append($c)\na = ([$a], $b)", "f(a)", True, "The tuple holds a list, and the list can change."),
    PC("def f(xs):\n    xs[0].append($c)\na = [[$a], [$b]]", "f(a)", True, "xs[0] is one of a's inner lists, shared."),
    PC("def f(xs):\n    xs = xs[:]\n    xs.append($c)\n" + L2, "f(a)", False, "The function copied the list first, then changed the copy."),
    PC("def f(xs):\n    xs = list(xs)\n    xs.append($c)\n" + L2, "f(a)", False, "list() builds a copy; the append changes only the copy."),
    PC("def f(xs):\n    ys = xs\n    ys.append($c)\n" + L2, "f(a)", True, "ys = xs gives a second name to the same list."),
    PC("def f(xs):\n    return xs + [$c]\n" + L2, "f(a)", False, "The new list is returned and thrown away; a is untouched."),
    PC("def f(xs):\n    return xs + [$c]\n" + L2, "a = f(a)", True, "a = f(a) points a at the new list, so a is different now."),
    PC("def f(xs):\n    xs.append($c)\n    return xs\n" + L2, "b = f(a)", True, "f changes a's list and returns that same list."),
    PC("def f(xs=[]):\n    xs.append($c)\n" + L2, "f()", False, "f() used its own default list, not a's."),
    PC("def f():\n    global a\n    a = a + 1\na = $a", "f()", True, "global a lets f rebind the module's a."),
    PC("def f():\n    a = 5\na = $a", "f()", False, "a = 5 inside f makes a local a."),
    PC("def f():\n    a.append($c)\n" + L2, "f()", True, "f reads the global a and changes the list it names."),
    PC(BOX + "def f(b):\n    b.n += 1\na = Box($a)", "f(a)", True, "The function got the same object, so its n changes.", snap="a.n"),
    PC(BOX + "def f(b):\n    b = Box(0)\na = Box($a)", "f(a)", False, "b now names a new Box; a's Box is untouched.", snap="a.n"),
    PC("def f(s):\n    s.add($c)\na = {$a, $b}", "f(a)", True, "add changes the shared set."),
    PC("def f(s):\n    s = s | {$c}\na = {$a, $b}", "f(a)", False, "| builds a new set for the local name."),
    PC("def f(s):\n    s |= {$c}\na = {$a, $b}", "f(a)", True, "|= changes the shared set in place."),
    PC("def f(xs):\n    xs.extend([$c])\n" + L2, "f(a)", True, "extend adds to the shared list."),
    PC("def f(xs):\n    xs.insert(0, $c)\n" + L2, "f(a)", True, "insert adds to the shared list."),
    PC("def f(xs):\n    xs.remove($a)\n" + L2, "f(a)", True, "remove deletes from the shared list."),
    PC("def f(xs):\n    xs *= 2\n" + L2, "f(a)", True, "*= repeats the list in place."),
    PC("def f(xs):\n    xs = xs * 2\n" + L2, "f(a)", False, "* builds a new list."),
    PC("def f(xs):\n    for x in xs:\n        x += 1\n" + L3, "f(a)", False, "x is a copy of each number."),
    PC("def f(xs):\n    for i in range(len(xs)):\n        xs[i] += 1\n" + L3, "f(a)", True, "xs[i] assigns into the shared list."),
    PC("def f(xs):\n    xs[:] = [$c]\n" + L2, "f(a)", True, "Assigning to xs[:] replaces the contents of the same list."),
    PC("def swap(p, q):\n    p, q = q, p\na = $a\nb = $b", "swap(a, b)", False, "The swap trades the local names; a and b stay as they were."),
    PC("def f(xs):\n    xs[0], xs[1] = xs[1], xs[0]\n" + L2, "f(a)", True, "The swap changes the items of the shared list."),
    PC("def f(xs):\n    return [x * 2 for x in xs]\n" + L3, "f(a)", False, "A comprehension builds a new list."),
    PC("def f(xs):\n    for i in range(len(xs)):\n        xs[i] *= 2\n" + L3, "f(a)", True, "Each item of the shared list is doubled in place."),
    PC('def f(d):\n    d["n"] += 1\na = {"n": $a}', "f(a)", True, "d is the same dict, so its n goes up."),
    PC('def f(d):\n    d = dict(d)\n    d["n"] += 1\na = {"n": $a}', "f(a)", False, "dict() copied it first."),
    PC('def f(d):\n    d = dict(d)\n    d["xs"].append($c)\na = {"xs": [$a]}', "f(a)", True, "dict() is a shallow copy: the inner list is still shared."),
    PC("def add_to(src, dst):\n    dst.append(src[0])\na = [$a]\nb = [$b]", "add_to(b, a)", True, "a is the second argument, dst, which gets the append."),
    PC("def add_to(src, dst):\n    dst.append(src[0])\na = [$a]\nb = [$b]", "add_to(a, b)", False, "a is only read: b is the one that grows."),
    PC("def f(x):\n    x = None\na = [$a]", "f(a)", False, "x = None points the local name away from the list."),
    PC("import copy\ndef f(xs):\n    xs = copy.deepcopy(xs)\n    xs[0].append($c)\na = [[$a], [$b]]", "f(a)", False, "deepcopy copies the inner lists too."),
    PC("def f(xs):\n    xs.sort(reverse=True)\n" + L3, "f(a)", _desc_changes, "It changes the list unless it was already biggest first."),
    PC("def f(xs):\n    del xs[:]\n" + L2, "f(a)", True, "del xs[:] empties the shared list."),
    PC("def f(xs):\n    xs.copy().append($c)\n" + L2, "f(a)", False, "The append changes a copy, which is thrown away."),
    PC("def f(d):\n    d.clear()\n" + D1, "f(a)", True, "clear empties the shared dict."),
    PC("def f(a):\n    a.append($c)\n" + L2, "f(a)", True, "The parameter is also called a, but it is the same list."),
    PC("def f(a):\n    a = a + [$c]\n" + L2, "f(a)", False, "a + [...] builds a new list for the parameter a."),
]
