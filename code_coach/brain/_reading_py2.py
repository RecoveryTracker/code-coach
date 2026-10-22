"""Reading Pack, Python side, part 2: Mutate or Copy, Error or Fine, Return Value, Number Crunch.

Every answer is modelled by hand and tests/test_brain_packs.py runs every
template through the real interpreter.
"""

from __future__ import annotations

import random
from string import Template
from typing import Callable

from ._model import Maker, fdiv, fmod, ipow, isort, params, py_div, py_show, raises_py, row
from .items import Item


# ── 5. Mutate or Copy ───────────────────────────────────────────────────

def _m(setup: str, body: str, changed, why: str = "") -> Maker:
    """A Mutate or Copy template: `a` is set up, the body runs, and the question is whether `a` ended up
    different. The oracle program records repr(a) after the setup and compares it after the body."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        s, b = Template(setup).substitute(p), Template(body).substitute(p)
        yes = changed(p) if callable(changed) else changed
        check = s + "\n_before = repr(a)\n" + b + '\n"no" if repr(a) == _before else "yes"'
        return Item(s + "\n" + b, "yes" if yes else "no", Template(why).safe_substitute(p), check=check)
    make.__name__ = "mut_" + body[:20]
    return make


L2 = "a = [$a, $b]"
L3 = "a = [$a, $b, $c]"
D1 = 'a = {"x": $a}'

MUTATE = [
    _m(L2, "b = a\nb.append($c)", True, "b is the same list as a, so the append shows in both."),
    _m(L2, "b = a.copy()\nb.append($c)", False, "copy() made a separate list."),
    _m(L2, "b = a[:]\nb.append($c)", False, "A full slice is a copy."),
    _m(L2, "b = list(a)\nb.append($c)", False, "list() builds a new list."),
    _m(L2, "b = a + [$c]", False, "+ builds a new list and leaves a alone."),
    _m(L2, "b = a\nb = b + [$c]", False, "b + [...] makes a new list, and b now names that; a is untouched."),
    _m(L2, "b = a\nb += [$c]", True, "+= on a list changes it in place, and b is the same list as a."),
    _m(L2, "a += [$c]", True, "+= extends the list in place."),
    _m(L2, "a = a + [$c]", True, "a now names a longer list."),
    _m("a = ($a, $b)", "b = a\nb += ($c,)", False, "Tuples cannot change; += makes a new one for b."),
    _m('a = "$w"', 'b = a\nb += "!"', False, "Strings cannot change; += makes a new string for b."),
    _m('a = "$w"', "b = a.upper()", False, "upper() returns a new string."),
    _m('a = "$w"', "a.upper()", False, "The new string is thrown away, and a never changes."),
    _m('a = "$w"', "a = a.upper()", True, "a now names the upper-case string."),
    _m(L3, "a.sort()", lambda p: isort([p["a"], p["b"], p["c"]]) != [p["a"], p["b"], p["c"]],
       "sort() works in place: it changes a unless it was already in order."),
    _m(L3, "sorted(a)", False, "sorted() returns a new list and leaves a alone."),
    _m(L3, "b = sorted(a)\nb.append(0)", False, "b is a new list."),
    _m(L3, "a.reverse()", True, "reverse() works in place."),
    _m(L3, "a[::-1]", False, "A slice makes a new list."),
    _m(L3, "reversed(a)", False, "reversed() gives an iterator and does not touch a."),
    _m(L2, "def add(xs):\n    xs.append($c)\nadd(a)", True, "The function got the same list, not a copy."),
    _m(L2, "def add(xs):\n    xs = xs + [$c]\nadd(a)", False, "xs + [...] builds a new list; only the local name xs changes."),
    _m(L2, "def add(xs):\n    xs += [$c]\nadd(a)", True, "+= changes the list in place, and it is a's list."),
    _m(L2, "def add(xs):\n    xs = xs[:]\n    xs.append($c)\nadd(a)", False, "The function copied the list first."),
    _m("a = [[$a], [$b]]", "b = a.copy()\nb[0].append($c)", True, "copy() is shallow: the inner lists are shared."),
    _m("a = [[$a], [$b]]", "b = a.copy()\nb.append([$c])", False, "Only b's outer list grew."),
    _m("a = [[$a], [$b]]", "import copy\nb = copy.deepcopy(a)\nb[0].append($c)", False, "deepcopy copies the inner lists too."),
    _m(D1, "b = a\nb[\"y\"] = $b", True, "b is the same dict as a."),
    _m(D1, "b = a.copy()\nb[\"y\"] = $b", False, "copy() made a separate dict."),
    _m(D1, "b = dict(a)\nb[\"y\"] = $b", False, "dict() builds a new dict."),
    _m(D1, "b = {**a, \"y\": $b}", False, "A new dict is built; a is untouched."),
    _m(D1, "a.update({\"y\": $b})", True, "update changes the dict in place."),
    _m(D1, "a.pop(\"x\")", True, "pop removes the key from a."),
    _m(D1, "del a[\"x\"]", True, "del removes the key."),
    _m(D1, "a.setdefault(\"y\", $b)", True, "setdefault adds the key when it is missing."),
    _m(D1, "a.setdefault(\"x\", $b)", False, "The key is already there, so nothing is added."),
    _m(D1, "a.get(\"y\", $b)", False, "get only looks; it never adds."),
    _m(L3, "for x in a:\n    x += 1", False, "x is a copy of each number; changing it does not touch the list."),
    _m(L3, "for i in range(len(a)):\n    a[i] += 1", True, "a[i] assigns into the list."),
    _m(L3, "b = [x * 2 for x in a]", False, "A comprehension builds a new list."),
    _m("a = [[$a], [$b]]", "for row in a:\n    row.append(0)", True, "Each row is a list in a, and append changes it."),
    _m("a = {$a, $b}", "b = a\nb.add($c)", True, "b is the same set as a."),
    _m("a = {$a, $b}", "b = a | {$c}", False, "| builds a new set."),
    _m("a = {$a, $b}", "a |= {$c}", True, "|= changes the set in place."),
    _m("a = {$a, $b}", "a.add($a)", False, "It was already in the set, so nothing changed."),
    _m("a = {$a, $b}", "a.discard($c)", False, "$c was not in the set, so nothing is removed."),
    _m("a = {$a, $b}", "a.discard($a)", True, "$a was in the set and is removed."),
    _m(L3, "b = a[1:]\nb[0] = 99", False, "A slice is a copy."),
    _m(L2, "b = a\ndel b", False, "del b only removes the name b."),
    _m(L2, "b = a\ndel b[0]", True, "del b[0] removes an item from the shared list."),
    _m(L2, "b = a * 2", False, "* builds a new list."),
    _m(L2, "a *= 2", True, "*= repeats the list in place."),
    _m(L2, "a.extend([$c])", True, "extend adds in place."),
    _m(L2, "a.insert(0, $c)", True, "insert changes the list."),
    _m(L2, "a.pop()", True, "pop removes the last item."),
    _m(L2, "a.remove($a)", True, "remove deletes the first match."),
    _m(L2, "a.clear()", True, "clear empties the list."),
    _m(L2, "a.count($a)", False, "count only looks."),
    _m(L2, "a.index($a)", False, "index only looks."),
    _m(L2, "a[0] = $c", True, "Assigning to an index changes the list."),
    _m(L3, "a[0:1] = [$d, $d]", True, "Assigning to a slice replaces those items."),
    _m('a = "$w"', "b = a\nb = b + \"s\"", False, "Strings cannot change: b is a new string."),
    _m('a = "$w"', 'b = a.replace("$x", "z")', False, "replace returns a new string."),
    _m("a = ([$a], $b)", "a[0].append($c)", True, "The tuple holds a list, and the list can change."),
    _m(L2, "b = a.copy()\nb.sort()", False, "Sorting the copy leaves a alone."),
    _m(L2, "b = a\nb.sort()", lambda p: isort([p["a"], p["b"]]) != [p["a"], p["b"]],
       "b is a's list; sorting changes it unless it was already in order."),
    _m(L2, "b = a\nb = None", False, "b now names None; a is untouched."),
]


# ── 6. Error or Fine ────────────────────────────────────────────────────

def _e(code: str, why: str) -> Maker:
    return row(code, "error", why, check=raises_py)


def _f(code: str, why: str) -> Maker:
    return row(code, "fine", why, check=raises_py)


ERROR = [
    _e("[$a, $b, $c][3]", "IndexError: the list has 3 items, so index 3 is past the end."),
    _e('"$w"[$n]', "IndexError: the string is shorter than that."),
    _e('d = {"a": $a}\nd["b"]', "KeyError: there is no key \"b\"."),
    _e('int("$w")', "ValueError: that text is not a number."),
    _e('int("$a.5")', "ValueError: int() does not read a decimal point."),
    _e('float("$w")', "ValueError: that text is not a number."),
    _e("$a / 0", "ZeroDivisionError: Python will not divide by zero."),
    _e("$a % 0", "ZeroDivisionError: % by zero too."),
    _e("$a // 0", "ZeroDivisionError: // by zero too."),
    _e("$a / 0.0", "ZeroDivisionError: even a float zero is refused."),
    _e("0 ** -1", "ZeroDivisionError: that is 1 / 0."),
    _e("x = None\nx.upper()", "AttributeError: None has no upper."),
    _e("None + $a", "TypeError: None cannot be added."),
    _e('"$w" + $a', "TypeError: a string and a number do not add."),
    _e('$a + "$w"', "TypeError: a number and a string do not add."),
    _e("len($a)", "TypeError: a number has no length."),
    _e("[$a].push($b)", "AttributeError: lists have append, not push."),
    _e('"$w".foo', "AttributeError: strings have no foo."),
    _e("total + $a", "NameError: total was never defined."),
    _e("x = $a\nx()", "TypeError: a number is not callable."),
    _e("t = ($a, $b)\nt[0] = $c", "TypeError: tuples cannot be changed."),
    _e('s = "$w"\ns[0] = "z"', "TypeError: strings cannot be changed."),
    _e("{[$a]: $b}", "TypeError: a list cannot be a dict key."),
    _e("[].pop()", "IndexError: pop from an empty list."),
    _e("[$a, $b].remove($c)", "ValueError: $c is not in the list."),
    _e("max([])", "ValueError: max of nothing."),
    _e("next(iter([]))", "StopIteration: there is no next item."),
    _e('"$w".index("z")', "ValueError: index raises where find gives -1."),
    _e("int(None)", "TypeError: None cannot become an int."),
    _e('abs("$w")', "TypeError: abs of a string."),
    _e('"$w" * "$v"', "TypeError: a string times a string."),
    _e('[$a, $b]["x"]', "TypeError: a list is indexed by whole numbers."),
    _e('{"k": $a}.k', "AttributeError: a dict's keys are not attributes."),
    _e("import nothing_here", "ModuleNotFoundError: there is no such module."),
    _e("a, b = [$a, $b, $c]", "ValueError: three items do not fit two names."),
    _e("a, b, c = ($a, $b)", "ValueError: two items do not fill three names."),
    _e("for x in $a:\n    pass", "TypeError: a number cannot be looped over."),
    _e("x = [$a]\nx[0][0]", "TypeError: a number cannot be indexed."),
    _e("def f(a):\n    return a\nf()", "TypeError: f is missing its argument."),
    _e("def f(a):\n    return a\nf($a, $b)", "TypeError: f got one argument too many."),
    _e('sum(["$w"])', "TypeError: sum starts from 0 and cannot add text."),
    _e('[$a, "$w"].sort()', "TypeError: numbers and strings cannot be ordered."),
    _e("sorted([$a, None])", "TypeError: a number and None cannot be ordered."),
    _e("import math\nmath.sqrt(-$a)", "ValueError: no square root of a negative."),
    _e("t = ([$a], $b)\nt[0] += [$c]", "TypeError: the tuple refuses the assignment (after the list was already extended)."),
    _e('ord("$w")', "TypeError: ord wants one character."),
    _e("list($a)", "TypeError: a number is not iterable."),
    _e("range(1.0)", "TypeError: range wants whole numbers."),
    _e('{}.pop("k")', "KeyError: pop with no default raises."),
    _e("[$a, $b, $c].pop($n)", "IndexError: pop index out of range."),
    _e("s = {$a}\ns.remove($b)", "KeyError: remove raises when the item is missing (discard does not)."),
    _e('"abc".split(1)', "TypeError: the separator must be a string."),
    _e("dict([$a, $b])", "TypeError: dict() wants pairs."),
    _e("chr(-1)", "ValueError: no such character."),
    _e("x = [1]\ndel x[$a]", "IndexError: there is no item at that position."),
    _e('"$w".join([$a])', "TypeError: join wants strings."),
    _e("[1, 2, 3].index(9)", "ValueError: 9 is not in the list."),
    _f("[$a, $b, $c][-1]", "A negative index counts from the end."),
    _f("[$a, $b, $c][1:10]", "A slice that runs past the end is clamped."),
    _f('"$w"[1:99]', "A slice that runs past the end is clamped."),
    _f('{}.get("k")', "get gives None for a missing key."),
    _f('d = {"a": $a}\nd.get("b")', "get gives None for a missing key."),
    _f('d = {"a": $a}\nd["a"]', "The key is there."),
    _f("x = None\nx is None", "A comparison with None is fine."),
    _f('int("$a")', "Digits make a number."),
    _f('int(" $a ")', "int() ignores spaces round the digits."),
    _f("int($a.9)", "int() cuts a float down to a whole number."),
    _f('float("$a.5")', "That text is a number."),
    _f("$a / $b", "Dividing by a non-zero number is fine."),
    _f("0 / $a", "Zero divided by something is fine."),
    _f('"$w" * $a', "A string times a number repeats it."),
    _f('"$w" + str($a)', "str() makes the number text first."),
    _f("[$a] + [$b]", "Two lists join."),
    _f("len([])", "An empty list has length 0."),
    _f("max([$a, $b])", "The biggest of two."),
    _f("max([], default=0)", "default says what to give for nothing."),
    _f("[].sort()", "Sorting nothing is fine."),
    _f('"$w".find("z")', "find gives -1 when there is no match."),
    _f('"  $w ".strip()', "strip removes the spaces."),
    _f("x, y = ($a, $b)", "Two items, two names."),
    _f("first, *rest = [$a, $b, $c]", "The star takes the rest."),
    _f("sum([])", "The sum of nothing is 0."),
    _f('"$x" in "$w"', "in gives True or False, never an error."),
    _f("$a in [$a, $b]", "in gives True or False."),
    _f('"$w" < "$v"', "Two strings compare fine."),
    _f("$a < $b < $c", "A chain of comparisons is fine."),
    _f("None == $a", "== never raises for a mismatch."),
    _f('$a == "$a"', "== just gives False for a mismatch."),
    _f("[None, $a][0]", "None can be an item."),
    _f('d = {}\nd["k"] = $a', "Assigning a new key adds it."),
    _f('d = {}\nd.setdefault("k", []).append($a)', "setdefault makes the list, then append adds to it."),
    _f("($a, $b) + ($c,)", "Two tuples join."),
    _f("x = [$a]\nx[0] += 1", "A list item can be changed."),
    _f("t = ([$a], $b)\nt[0].append($c)", "The tuple holds the list; the list itself can change."),
    _f("def f(a, b=2):\n    return a + b\nf($a)", "b has a default."),
    _f("f = lambda: $a\nf()", "A lambda with no parameters, called with none."),
    _f("True + True", "True is 1 in arithmetic."),
    _f("int(True)", "True is 1."),
    _f('ord("a")', "One character is fine."),
    _f('list("$w")', "A string is iterable."),
    _f("dict([($a, $b)])", "dict() wants pairs, and this is one."),
    _f("[x for x in range(3)][-1]", "The last item."),
    _f('{}.pop("k", None)', "A default makes pop safe."),
    _f("s = {$a}\ns.discard($b)", "discard never raises."),
    _f("[$a, $b, $c].index($b)", "$b is in the list."),
    _f("5 // 2.0", "Floor division by a non-zero float."),
    _f("divmod($a, $b)", "b is not zero."),
    _f("round($a / $b)", "Nothing here can raise."),
    _f('"a,b".split(",")[1]', "Two pieces, so index 1 exists."),
    _f("len(str($a))", "str() first, then len."),
    _f("[$a, $b, $c][::-1]", "A reversed copy."),
    _f("{}[\"k\"] if False else 0", "The failing part never runs."),
]


# ── 7. Return Value ─────────────────────────────────────────────────────

def _r(fmt: str, answer, why: str = "") -> Maker:
    return row(fmt, answer, why)


def _first_even(xs: list[int]) -> str:
    for x in xs:
        if fmod(x, 2) == 0:
            return str(x)
    return "None"


def _fact(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a - b * fdiv(a, b)
    return a


F_ADD = "def f(a, b):\n    return a + b, a * b\n"

RETURN = [
    _r("def f(x):\n    return x * 2\nf($a)", lambda p: str(p["a"] * 2), "The call gives back x * 2."),
    _r("def f(x):\n    x * 2\nf($a)", "None", "There is no return, so the call gives None."),
    _r('def f(x):\n    if x > $b:\n        return "big"\n    return "small"\nf($a)',
       lambda p: "big" if p["a"] > p["b"] else "small", "Only one return runs: the first one reached."),
    _r("def first_even(xs):\n    for x in xs:\n        if x % 2 == 0:\n            return x\nfirst_even([$a, $b, $c])",
       lambda p: _first_even([p["a"], p["b"], p["c"]]), "It returns the first even item, or None if it never returns."),
    _r("def f(a, b=10):\n    return a + b\nf($a)", lambda p: str(p["a"] + 10), "b falls back to its default, 10."),
    _r("def f(a, b=10):\n    return a + b\nf($a, $b)", lambda p: str(p["a"] + p["b"]), "A value passed in replaces the default."),
    _r("def f(a, b):\n    return a - b\nf(b=$a, a=$b)", lambda p: str(p["b"] - p["a"]), "Keywords match by name, not by position."),
    _r(F_ADD + "f($a, $b)", lambda p: py_show((p["a"] + p["b"], p["a"] * p["b"])), "Two values after return make a tuple."),
    _r(F_ADD + "f($a, $b)[1]", lambda p: str(p["a"] * p["b"]), "Index 1 of the pair is the product."),
    _r(F_ADD + "s, p = f($a, $b)\np", lambda p: str(p["a"] * p["b"]), "The pair unpacks into s and p."),
    _r("def total(xs):\n    t = 0\n    for x in xs:\n        t += x\n    return t\ntotal([$a, $b, $c])",
       lambda p: str(p["a"] + p["b"] + p["c"]), "The return is after the loop: it adds them all."),
    _r("def f(xs):\n    for x in xs:\n        return x\nf([$a, $b])", lambda p: str(p["a"]),
       "The return runs on the first turn, so only the first item is seen."),
    _r("def f(n):\n    return 1 if n <= 1 else n * f(n - 1)\nf($a)", lambda p: str(_fact(p["a"])), "n * (n-1) * ... * 1."),
    _r("def add(x, acc=[]):\n    acc.append(x)\n    return acc\nadd($a)\nadd($b)", lambda p: py_show([p["a"], p["b"]]),
       "The default list is made once and shared by every call."),
    _r("def f(x):\n    x = x + 1\n    return x\nn = $a\nf(n)\nn", lambda p: str(p["a"]), "The function changed its own x, not n."),
    _r("def f():\n    pass\nf() is None", "True", "A function with no return gives None."),
    _r("def f(xs):\n    xs.append(0)\n    return len(xs)\nnums = [$a]\nf(nums)\nnums", lambda p: py_show([p["a"], 0]),
       "The function changed the very list it was given."),
    _r("def f(xs):\n    xs.sort()\nr = f([$b, $a, $c])\nr", "None", "sort returns None and f returns nothing, so r is None."),
    _r('def f(s):\n    return s.upper()\nf("$w")', lambda p: "".join(chr(ord(c) - 32) for c in p["w"]), "upper() gives the capitals."),
    _r("def f(n):\n    for i in range(n):\n        if i * i > 10:\n            return i\n    return -1\nf($a)",
       lambda p: "4" if p["a"] > 4 else "-1", "The first i whose square is over 10 is 4; if the loop ends first, -1."),
    _r("def f(*args):\n    return len(args)\nf($a, $b, $c)", "3", "*args collects the extras into a tuple."),
    _r("def f(**kw):\n    return len(kw)\nf(a=$a, b=$b)", "2", "**kw collects the keyword arguments into a dict."),
    _r("def f(a, *rest):\n    return rest\nf($a, $b, $c)", lambda p: py_show((p["b"], p["c"])), "rest is a tuple of what is left."),
    _r("sq = lambda x: x * x\nsq($a)", lambda p: str(p["a"] * p["a"]), "A lambda returns its expression."),
    _r("(lambda a, b: a if a > b else b)($a, $b)", lambda p: str(max(p["a"], p["b"])), "It gives back the bigger one."),
    _r("def make(n):\n    def add(x):\n        return x + n\n    return add\nmake($a)($b)", lambda p: str(p["a"] + p["b"]),
       "add remembers n from make."),
    _r("def f(x):\n    return\nf($a)", "None", "A bare return gives None."),
    _r("def f(n):\n    while True:\n        n -= 3\n        if n < 0:\n            return n\nf($n)",
       lambda p: str(p["n"] - 3 * (fdiv(p["n"], 3) + 1)), "It takes 3 off until n goes below 0, then returns it."),
    _r("def f(a, b):\n    return a // b, a % b\nf($n, $a)", lambda p: py_show((fdiv(p["n"], p["a"]), fmod(p["n"], p["a"]))),
       "The quotient and the remainder, as a tuple."),
    _r('def f(s):\n    return s[0] + s[-1]\nf("$w")', lambda p: p["w"][0] + p["w"][-1], "The first letter and the last."),
    _r('def f(x):\n    if x:\n        return "yes"\nf(0)', "None", "0 is falsy, so the return is skipped and the call gives None."),
    _r('def f(x):\n    if x:\n        return "yes"\nf($a)', "yes", "$a is truthy, so it returns."),
    _r("def f(xs):\n    return [x * 2 for x in xs]\nf([$a, $b])", lambda p: py_show([p["a"] * 2, p["b"] * 2]), "A new list of doubles."),
    _r("def f(n=$a):\n    return n * 2\nf()", lambda p: str(p["a"] * 2), "No argument: the default is used."),
    _r("def f(n=$a):\n    return n * 2\nf($b)", lambda p: str(p["b"] * 2), "The argument replaces the default."),
    _r("def f(x):\n    return x,\nf($a)", lambda p: py_show((p["a"],)), "A trailing comma makes a one-item tuple."),
    _r("def f(a, b):\n    return b\nf(*[$a, $b])", lambda p: str(p["b"]), "* spreads the list into the arguments."),
    _r("def f():\n    return [$a, $b, $c]\nlen(f())", "3", "The call gives a list of three."),
    _r("def f():\n    return $a, $b\ntype(f()).__name__", "tuple", "A bare comma pair is a tuple."),
    _r("def f(x):\n    return not x\nf([])", "True", "An empty list is falsy, so not x is True."),
    _r("def f(x):\n    return not x\nf([$a])", "False", "A list with an item is truthy."),
    _r("def f(n):\n    return n if n > 0 else -n\nf(-$a)", lambda p: str(p["a"]), "It flips a negative: an absolute value."),
    _r("def f(n):\n    total = 0\n    for i in range(n):\n        total += i\n        return total\nf($a)", "0",
       "The return is inside the loop, so it stops after the first turn: total is 0."),
    _r("def f(xs):\n    for x in xs:\n        if x > 3:\n            return True\n        else:\n            return False\nf([$a, $b, $c])",
       lambda p: "True" if p["a"] > 3 else "False", "The else returns on the first item too, so only the first item counts."),
    _r("def f(a):\n    a = a * 2\nresult = f($a)\nresult", "None", "No return: result is None."),
    _r("def f(n, acc=0):\n    if n == 0:\n        return acc\n    return f(n - 1, acc + n)\nf($a)",
       lambda p: str(p["a"] * (p["a"] + 1) // 2), "It adds n + (n-1) + ... + 1."),
    _r('def g():\n    return "a"\n    return "b"\ng()', "a", "The first return ends the function."),
    _r('def f(d):\n    return d.get("x", 0)\nf({"y": $a})', "0", "No key x, so get gives its default."),
    _r('def f(d):\n    return d.get("x", 0)\nf({"x": $a})', lambda p: str(p["a"]), "The key is there."),
    _r("def swap(a, b):\n    return b, a\nx, y = swap($a, $b)\nx", lambda p: str(p["b"]), "swap returns them the other way round."),
    _r('def f(n):\n    return "even" if n % 2 == 0 else "odd"\nf($a)', lambda p: "even" if fmod(p["a"], 2) == 0 else "odd",
       "n % 2 is 0 for even numbers."),
    _r("def count(xs, t):\n    c = 0\n    for x in xs:\n        if x == t:\n            c += 1\n    return c\ncount([$a, $b, $a], $a)", "2",
       "It counts the items equal to the target."),
    _r('def f(s):\n    return s * 2\nf("$w")', lambda p: p["w"] + p["w"], "A string times 2 repeats it."),
    _r("def f(a, b):\n    return a ** b\nf($a, 2)", lambda p: str(p["a"] * p["a"]), "a to the power 2."),
]


# ── 8. Number Crunch ────────────────────────────────────────────────────

def _half_even_tens(n: int) -> int:
    """round(n, -1) for a whole number: ties go to the even ten."""
    tens = fdiv(n, 10)
    r = n - 10 * tens
    if r < 5 or (r == 5 and fmod(tens, 2) == 0):
        return tens * 10
    return (tens + 1) * 10


def _round_half(whole: int) -> int:
    """round(whole + 0.5): the even neighbour."""
    return whole if fmod(whole, 2) == 0 else whole + 1


def _bin(n: int) -> str:
    out = ""
    while n:
        out = str(n - 2 * fdiv(n, 2)) + out
        n = fdiv(n, 2)
    return "0b" + out


def _hex(n: int) -> str:
    digits = "0123456789abcdef"
    out = ""
    while n:
        out = digits[fmod(n, 16)] + out
        n = fdiv(n, 16)
    return "0x" + out


def _digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))


def _n(fmt: str, answer: Callable[[dict], object], why: str = "") -> Maker:
    return row(fmt, lambda p: str(answer(p)), why)


def _div_by(p: dict) -> int:
    return (2, 4, 5, 8)[p["a"] % 4]


def _n_div(rng: random.Random) -> Item:
    d = rng.choice((2, 4, 5, 8))
    n = rng.randint(10, 40)
    return Item(f"{n} / {d}", py_div(n, d), "/ is true division: a float, with the fraction kept.")


NUMBER = [
    _n("$n // $a", lambda p: fdiv(p["n"], p["a"]), "// divides and rounds down."),
    _n("-$n // $a", lambda p: fdiv(-p["n"], p["a"]), "// rounds toward minus infinity, so a negative result goes further from 0."),
    _n("$n // -$a", lambda p: fdiv(p["n"], -p["a"]), "A negative divisor also rounds down: away from 0."),
    _n("$n % $a", lambda p: fmod(p["n"], p["a"]), "% is the remainder."),
    _n("-$n % $a", lambda p: fmod(-p["n"], p["a"]), "A % result takes the sign of the right side: it lands from 0 up to $a - 1."),
    _n("$n % -$a", lambda p: fmod(p["n"], -p["a"]), "A negative divisor gives a result of 0 or below."),
    _n_div,
    _n("$a * $b / $b", lambda p: py_div(p["a"] * p["b"], p["b"]), "/ always gives a float."),
    _n("2 ** $a", lambda p: ipow(2, p["a"]), "2 multiplied by itself $a times."),
    _n("2 ** -$k", lambda p: py_div(1, ipow(2, p["k"])), "A negative power is a fraction: 1 over the power."),
    _n("(-$a) ** 3", lambda p: -ipow(p["a"], 3), "A negative number cubed stays negative."),
    _n("-$a ** 2", lambda p: -ipow(p["a"], 2), "** binds tighter than the minus: -(a ** 2)."),
    _n("2 ** 3 ** 2", lambda p: 512, "** goes right to left: 2 ** 9."),
    _n("round($a.5)", lambda p: _round_half(p["a"]), "round sends an exact half to the even neighbour."),
    _n("round(-$a.5)", lambda p: -_round_half(p["a"]), "Halves go to the even neighbour, on the negative side too."),
    _n("round($a / 2)", lambda p: (fdiv(p["a"], 2) if fmod(p["a"], 2) == 0 else _round_half(fdiv(p["a"], 2))),
       "An odd number over 2 is an exact half, and halves go to even."),
    _n("round($n, -1)", lambda p: _half_even_tens(p["n"]), "Rounds to the nearest ten; an exact tie goes to the even ten."),
    _n("abs(-$a)", lambda p: p["a"], "abs drops the sign."),
    _n("abs(-$a.5)", lambda p: f"{p['a']}.5", "abs of a float is a float."),
    _n("divmod($n, $a)", lambda p: py_show((fdiv(p["n"], p["a"]), fmod(p["n"], p["a"]))), "divmod gives (n // a, n % a)."),
    _n("divmod(-$n, $a)", lambda p: py_show((fdiv(-p["n"], p["a"]), fmod(-p["n"], p["a"]))), "Both parts round down, so the remainder is not negative."),
    _n("int($a.9)", lambda p: p["a"], "int() cuts off the fraction."),
    _n("int(-$a.9)", lambda p: -p["a"], "int() cuts toward zero (unlike //)."),
    _n('int("$a") + $b', lambda p: p["a"] + p["b"], "int() reads the text as a number."),
    _n('float("$a") * 2', lambda p: f"{2 * p['a']}.0", "float() makes a float, so the answer is a float."),
    _n("max($a, $b) - min($a, $b)", lambda p: abs(p["a"] - p["b"]), "The difference between the biggest and the smallest."),
    _n("sum([$a, $b]) / 2", lambda p: py_div(p["a"] + p["b"], 2), "The average of two: a float."),
    _n("sum(range($a))", lambda p: p["a"] * (p["a"] - 1) // 2, "0 + 1 + ... + ($a - 1)."),
    _n("$n // $a * $a + $n % $a", lambda p: p["n"], "The quotient times a, plus the remainder, rebuilds n."),
    _n("1 + $a * $b ** 2", lambda p: 1 + p["a"] * p["b"] ** 2, "** first, then *, then +."),
    _n("($a + $b) * $c ** 2", lambda p: (p["a"] + p["b"]) * p["c"] ** 2, "The brackets first, then **, then *."),
    _n("$a - $b - $c", lambda p: p["a"] - p["b"] - p["c"], "Left to right."),
    _n("$a * $b % $c", lambda p: fmod(p["a"] * p["b"], p["c"]), "* and % share a level: left to right."),
    _n("$n // $a // 2", lambda p: fdiv(fdiv(p["n"], p["a"]), 2), "// twice, left to right."),
    _n("$n // $a % $b", lambda p: fmod(fdiv(p["n"], p["a"]), p["b"]), "// first, then % on its result."),
    _n("True + True + $a", lambda p: p["a"] + 2, "Each True counts as 1."),
    _n("$a * 0.5", lambda p: py_div(p["a"], 2), "A float times a whole number is a float."),
    _n("$a / 2 * 2", lambda p: f"{p['a']}.0", "The division makes a float, and it stays one."),
    _n("0.1 + 0.2", lambda p: "0.30000000000000004", "Floats are binary: 0.1 + 0.2 is a hair over 0.3."),
    _n("0.1 * 3", lambda p: "0.30000000000000004", "The same famous float error."),
    _n("1e3 + $a", lambda p: f"{1000 + p['a']}.0", "1e3 is a float, so the sum is a float."),
    _n("$a // 2.0", lambda p: f"{fdiv(p['a'], 2)}.0", "// with a float rounds down but gives a float."),
    _n("$n % 2.5", lambda p: py_div(fmod(2 * p["n"], 5), 2), "% works on floats too: what is left after taking out 2.5s."),
    _n("-$n // 4.0", lambda p: f"{fdiv(-p['n'], 4)}.0", "Rounds down to a float."),
    _n('int("1$a") + int("$b")', lambda p: 10 + p["a"] + p["b"], "Text '1$a' is the number 1$a."),
    _n('int("$a" * 2)', lambda p: p["a"] * 11, "The string repeats first: '$a$a', then it is read as a number."),
    _n("len(str(2 ** $n))", lambda p: len(str(ipow(2, p["n"]))), "Count the digits of the power."),
    _n('sum(int(c) for c in "$n")', lambda p: _digit_sum(p["n"]), "Add up the digits."),
    _n("bin($a)", lambda p: _bin(p["a"]), "bin shows the base 2 digits after 0b."),
    _n("hex($n)", lambda p: _hex(p["n"]), "hex shows the base 16 digits after 0x."),
    _n('int("ff", 16)', lambda p: 255, "ff in base 16 is 15 * 16 + 15."),
    _n('int("101", 2)', lambda p: 5, "101 in base 2 is 4 + 1."),
    _n('ord("a") + $a', lambda p: 97 + p["a"], "ord gives a letter's number: a is 97."),
    _n("import math\nmath.floor(-$a.5)", lambda p: -(p["a"] + 1), "floor goes down, toward minus infinity."),
    _n("import math\nmath.ceil($a.1)", lambda p: p["a"] + 1, "ceil goes up."),
    _n("import math\nmath.sqrt($a * $a)", lambda p: f"{p['a']}.0", "sqrt always gives a float."),
    _n("import math\nmath.gcd($n, $a)", lambda p: _gcd(p["n"], p["a"]), "The biggest number that divides both."),
    _n("import math\nmath.factorial($a)", lambda p: _fact(p["a"]), "1 * 2 * ... * $a."),
    _n("pow($a, 3, $b)", lambda p: fmod(ipow(p["a"], 3), p["b"]), "Three arguments: a ** 3, then % b."),
    _n("3 - -$a", lambda p: 3 + p["a"], "Minus a negative adds."),
    _n("7 // 2", lambda p: 3, "// rounds down."),
    _n("10 ** -2", lambda p: "0.01", "A negative power is a fraction."),
    _n("5 // 2 + 5 % 2", lambda p: 3, "5 // 2 is 2 and 5 % 2 is 1, so 2 + 1."),
]
