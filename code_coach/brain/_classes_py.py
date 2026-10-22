"""Classes and objects Pack, Python side: eight activities about what a class gives back.

Attribute Value, Method Returns, Class or Instance, Inherit It, Is It, Same
Object, Counter Class, Default Printing. Every answer is modelled by hand (the
numbers are added up here, the strings are built here) and tests/test_brain_packs.py
runs every template through the real interpreter.

A template is written with `T(source, answer, why)`: the source is a
`string.Template` (holes `$A $B $C` are class names, `$a $b $c $d` different
ints 2-9, `$w $v` words, `$n` 10-40), the answer a value or a function of the
parameters `p` (`p.a`, `p.w`...). `YN` is the same for the yes/no activities.
`factory` is shared with the JavaScript side.
"""

from __future__ import annotations

import random
from string import Template
from typing import Any, Callable

from ._model import WORDS, Maker, py_show, reverse, upper, yes_no_py
from .items import Item

CLASSES = ("Plot", "Crop", "Drone", "Barn", "Robot", "Lamp", "Tree", "Seed", "Cart", "Box", "Gate", "Well",
           "Hive", "Tank")


class P(dict):
    """The parameters of one item: p["a"] is also p.a."""

    __getattr__ = dict.__getitem__


def params(rng: random.Random) -> P:
    A, B, C, D = rng.sample(CLASSES, 4)
    a, b, c, d = rng.sample(range(2, 10), 4)
    w, v = rng.sample(WORDS, 2)
    return P(A=A, B=B, C=C, D=D, a=a, b=b, c=c, d=d, w=w, v=v, n=rng.randint(10, 40))


def L(*lines: str) -> str:
    return "\n".join(lines)


def factory(show: Callable[[Any], str], yes_no: Callable[[str], str]):
    """(T, YN): template writers for one language. `show` prints an answer value the way the language does."""

    def T(src: str, ans, why: str | Callable[[P], str] = "", run: str | None = None) -> Maker:
        """A typed-answer template. `run` (a Template) replaces the prompt's last line in the oracle's program,
        for a prompt whose last line prints (print(x)) so that the oracle can read a value instead."""

        def make(rng: random.Random) -> Item:
            p = params(rng)
            prompt = Template(src).substitute(p)
            value = ans(p) if callable(ans) else ans
            text = why(p) if callable(why) else Template(why).safe_substitute(p)
            check = ""
            if run is not None:
                check = prompt.rpartition("\n")[0] + "\n" + Template(run).substitute(p)
            return Item(prompt, show(value), text, check=check)

        make.__name__ = "t_" + src.split("\n")[-1][:30]
        return make

    def YN(src: str, yes: bool | Callable[[P], bool], why: str | Callable[[P], str] = "") -> Maker:
        def make(rng: random.Random) -> Item:
            p = params(rng)
            prompt = Template(src).substitute(p)
            ok = yes(p) if callable(yes) else yes
            text = why(p) if callable(why) else Template(why).safe_substitute(p)
            return Item(prompt, "yes" if ok else "no", text, check=yes_no(prompt))

        make.__name__ = "yn_" + src.split("\n")[-1][:30]
        return make

    return T, YN


T, YN = factory(py_show, yes_no_py)

# A few class bodies several templates share.
INIT = ("class $A:", "    def __init__(self, n):", "        self.n = n")
UP = INIT + ("    def up(self):", "        self.n += 1")
GROW = INIT + ("    def grow(self, k):", "        self.n += k")
ITEMS = ("class $A:", "    def __init__(self):", "        self.items = []", "    def add(self, x):",
         "        self.items.append(x)")


# ── 1. Attribute Value ──────────────────────────────────────────────────

ATTR = [
    T(L(*INIT, "x = $A($a)", "x.n"), lambda p: p.a, "__init__ ran with n = $a and stored it in self.n."),
    T(L("class $A:", "    def __init__(self, n=$a):", "        self.n = n", "x = $A()", "x.n"), lambda p: p.a,
      "Nothing was passed, so n took its default, $a."),
    T(L("class $A:", "    def __init__(self, n=$a):", "        self.n = n", "x = $A($b)", "x.n"), lambda p: p.b,
      "The argument $b replaces the default."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n * 2", "x = $A($a)", "x.n"),
      lambda p: p.a * 2, "__init__ stores n doubled."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n + $b", "$A($a).n"), lambda p: p.a + p.b,
      "__init__ adds $b before storing."),
    T(L("class $A:", "    def __init__(self, w, h):", "        self.w = w", "        self.h = h", "r = $A($a, $b)",
        "r.h"), lambda p: p.b, "The second argument went into h."),
    T(L(*UP, "x = $A($a)", "x.up()", "x.n"), lambda p: p.a + 1, "up() adds 1 to self.n."),
    T(L(*GROW, "x = $A($a)", "x.grow($b)", "x.grow($c)", "x.n"), lambda p: p.a + p.b + p.c,
      "Each grow adds to the same self.n: $a + $b + $c."),
    T(L(*INIT, "    def reset(self):", "        self.n = 0", "x = $A($a)", "x.reset()", "x.n"), 0,
      "reset() sets self.n to 0."),
    T(L(*INIT, "x = $A($a)", "x.n = $b", "x.n"), lambda p: p.b, "Assigning to x.n replaces the stored value."),
    T(L(*INIT, "x = $A($a)", 'x.tag = "$w"', "x.tag"), lambda p: p.w,
      "An instance can take a new attribute at any time."),
    T(L("class $A:", "    def __init__(self, w, h):", "        self.w = w", "        self.h = h",
        "        self.area = w * h", "r = $A($a, $b)", "r.w = $c", "r.area"), lambda p: p.a * p.b,
      "area was worked out once in __init__; changing w later does not update it."),
    T(L(*INIT, "x = $A($a)", "y = $A($b)", "x.n"), lambda p: p.a, "Each object keeps its own n."),
    T(L(*INIT, "x = $A($a)", "y = $A($b)", "x.n += $c", "y.n"), lambda p: p.b,
      "Changing x does not touch y: they have separate attributes."),
    T(L(*INIT, "x = $A($a)", "y = x", "y.n = $b", "x.n"), lambda p: p.b,
      "y is another name for the same object, so x.n changed too."),
    T(L(*ITEMS, "x = $A()", 'x.add("$w")', 'x.add("$v")', "len(x.items)"), 2, "Two adds, two items."),
    T(L(*ITEMS, "x = $A()", 'x.add("$w")', 'x.add("$v")', "x.items[-1]"), lambda p: p.v,
      "[-1] is the item added last."),
    T(L(*ITEMS, "x = $A()", 'x.add("$w")', 'x.add("$v")', "x.items[0]"), lambda p: p.w,
      "[0] is the item added first."),
    T(L(*ITEMS, "x = $A()", 'x.add("$w")', "y = $A()", "len(y.items)"), 0,
      "__init__ made a fresh list for y, so y has nothing."),
    T(L("class $A:", "    def __init__(self):", "        self.n = 0", "        self.bump()", "    def bump(self):",
        "        self.n += $a", "$A().n"), lambda p: p.a, "__init__ calls bump(), which adds $a."),
    T(L(*INIT, "    def add(self, k):", "        self.n += k", "        return self", "$A($a).add($b).add($c).n"),
      lambda p: p.a + p.b + p.c, "add returns self, so the calls chain onto the same object."),
    T(L(*INIT, "    @property", "    def twice(self):", "        return self.n * 2", "x = $A($a)", "x.twice"),
      lambda p: p.a * 2, "A property is read like an attribute, but it runs the method."),
    T(L(*INIT, "    @property", "    def twice(self):", "        return self.n * 2", "x = $A($a)", "x.n = $b",
        "x.twice"), lambda p: p.b * 2, "The property is worked out each time it is read, from the current n."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name.upper()", '$A("$w").name'),
      lambda p: upper(p.w), "__init__ stores the name in capitals."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", 'x = $A("$w")', "x.name[0]"),
      lambda p: p.w[0], "name is a string, and [0] is its first character."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", 'x = $A("$w")', "len(x.name)"),
      lambda p: len(p.w), "len counts the characters of the stored name."),
    T(L("class $A:", "    def __init__(self, n):", '        self.stock = {"$w": n}', "x = $A($a)",
        'x.stock["$w"] += $b', 'x.stock["$w"]'), lambda p: p.a + p.b, "The dict inside the object changed in place."),
    T(L(*INIT, "x = $A($a)", 'setattr(x, "n", $b)', 'getattr(x, "n")'), lambda p: p.b,
      "setattr(x, 'n', v) is x.n = v spelled with a string."),
    T(L(*INIT, "x = $A($a)", 'getattr(x, "missing", $d)'), lambda p: p.d,
      "There is no such attribute, so getattr gives the default."),
    T(L(*INIT, "$A($a).n + $A($b).n"), lambda p: p.a + p.b, "Two separate objects, one n each."),
    T(L("class $B:", "    def __init__(self, n):", "        self.n = n", "class $A:", "    def __init__(self, n):",
        "        self.part = $B(n)", "x = $A($a)", "x.part.n"), lambda p: p.a,
      "x.part is a $B object, and it holds n."),
    T(L("class $B:", "    def __init__(self, n):", "        self.n = n", "class $A:", "    def __init__(self, n):",
        "        self.part = $B(n)", "x = $A($a)", "x.part.n += $b", "x.part.n"), lambda p: p.a + p.b,
      "The inner object changed."),
    T(L("class $A:", "    def __init__(self, w, h):", "        self.w = w", "        self.h = h",
        "$A(h=$a, w=$b).w"), lambda p: p.b, "Keyword arguments go by name, not by position: w is $b."),
    T(L(*INIT, "x = $A($a)", "x.tag = $b", "len(vars(x))"), 2, "vars(x) lists x's own attributes: n and tag."),
    T(L(*INIT, "x = $A($a)", 'x.__dict__["n"]'), lambda p: p.a, "__dict__ is the dict of an object's attributes."),
    T(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    x: int", "    y: int",
        "z = $A($a, $b)", "z.y"), lambda p: p.b, "A dataclass writes __init__ for you: fields in order."),
    T(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    n: int = $a", "$A().n"),
      lambda p: p.a, "The field's default is used when nothing is passed."),
    T(L("from collections import namedtuple", '$A = namedtuple("$A", "x y")', "z = $A($a, $b)", "z.y"),
      lambda p: p.b, "A namedtuple's fields are named in order."),
    T(L("from collections import namedtuple", '$A = namedtuple("$A", "x y")', "z = $A($a, $b)",
        "z._replace(x=$c).x"), lambda p: p.c, "_replace returns a copy with that field changed."),
    T(L(*INIT, "x = $A($a)", "del x.n", 'hasattr(x, "n")'), False, "del removed the attribute, so it is gone."),
    T(L("class $A:", "    def __init__(self, x, y):", "        self.x = x", "        self.y = y", "c = $A($a, $b)",
        "c.x, c.y = c.y, c.x", "c.x"), lambda p: p.b, "The swap trades the two attributes."),
    T(L("class $A:", "    def __init__(self):", "        self.total = 0", "    def add(self, k):",
        "        self.total += k", "x = $A()", "x.add($a)", "x.add($b)", "x.total"), lambda p: p.a + p.b,
      "total keeps the running sum: $a + $b."),
    T(L(*INIT, "class $B($A):", "    pass", "$B($a).n"), lambda p: p.a, "$B inherits __init__ from $A."),
    T(L(*INIT, "class $B($A):", "    def __init__(self, n):", "        super().__init__(n)",
        "        self.m = n + 1", "$B($a).m"), lambda p: p.a + 1, "m is one more than n."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = max(n, 0)", "$A(-$a).n"), 0,
      "max(-$a, 0) is 0."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = min(n, $b)", "$A($a).n"),
      lambda p: min(p.a, p.b), "min keeps the smaller of $a and $b."),
    T(L("class $A:", "    def __init__(self, n):", "        self.big = n > 5", "$A($a).big"), lambda p: p.a > 5,
      "$a > 5 is worked out in __init__ and stored."),
    T(L("class $A:", "    def __init__(self, items):", "        self.items = items", "src = [$a, $b]", "x = $A(src)",
        "src.append($c)", "len(x.items)"), 3, "x.items is the very list src, so the append shows."),
    T(L("class $A:", "    def __init__(self, items):", "        self.items = list(items)", "src = [$a, $b]",
        "x = $A(src)", "src.append($c)", "len(x.items)"), 2, "list() made a copy, so the append is not seen."),
    T(L("class $A:", "    def __init__(self, name):", '        self.name = name + "s"', '$A("$w").name'),
      lambda p: p.w + "s", "__init__ adds an s to the name."),
    T(L(*INIT, "x = $A($a)", "x.pos = ($b, $c)", "x.pos[1]"), lambda p: p.c, "pos is a tuple; [1] is its second item."),
]

# ── 2. Method Returns ───────────────────────────────────────────────────

STACK = ("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def pop(self):",
         "        return self.items.pop()")


def _fact(k: int) -> int:
    out = 1
    for i in range(2, k + 1):
        out *= i
    return out


def _first_over(xs: list[int], lim: int):
    for x in xs:
        if x > lim:
            return x
    return None


METH = [
    T(L(*INIT, "    def add(self, k):", "        return self.n + k", "x = $A($a)", "x.add($b)"),
      lambda p: p.a + p.b, "add returns n + k: $a + $b."),
    T(L(*INIT, "    def add(self, k):", "        return self.n + k", "x = $A($a)", "x.add($c)", "x.add($b)"),
      lambda p: p.a + p.b, "add never changes self.n, so the second call starts from $a again."),
    T(L(*INIT, "    def add(self, k):", "        self.n += k", "        return self.n", "x = $A($a)", "x.add($b)",
        "x.add($b)"), lambda p: p.a + 2 * p.b, "This add changes self.n, so the second call builds on the first."),
    T(L(*UP, "x = $A($a)", "x.up()"), None, "up() has no return, so the call gives None."),
    T(L(*STACK, "$A().pop()"), lambda p: p.c, "pop takes off the last item, $c."),
    T(L(*STACK, "x = $A()", "x.pop()", "x.pop()"), lambda p: p.b, "The first pop removed $c; the second gives $b."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def take(self):",
        "        return self.items.pop(0)", "$A().take()"), lambda p: p.a, "pop(0) takes from the front."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def peek(self):",
        "        return self.items[-1]", "x = $A()", "x.items.pop()", "x.peek()"),
      lambda p: p.b, "peek only looks at the last item, which is $b once $c is gone."),
    T(L(*STACK, "x = $A()", "x.pop()", "len(x.items)"), 2, "One item was taken off the three."),
    T(L(*INIT, "    def twice(self):", "        return self.n * 2", "    def quad(self):",
        "        return self.twice() * 2", "$A($a).quad()"), lambda p: p.a * 4, "quad calls twice(), then doubles again."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "    def inc(self, k=1):", "        self.n += k",
        "        return self.n", "$A($a).inc()"), lambda p: p.a + 1, "k defaults to 1."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "    def inc(self, k=1):", "        self.n += k",
        "        return self.n", "x = $A($a)", "x.inc()", "x.inc($b)"), lambda p: p.a + 1 + p.b,
      "The first call adds 1 and the second adds $b."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", "    def hi(self):",
        '        return self.name + "!"', '$A("$w").hi()'), lambda p: p.w + "!", "hi joins a ! on the name."),
    T(L("class $A:", "    def __init__(self, name, n):", "        self.name = name", "        self.n = n",
        "    def tag(self):", "        return self.name + str(self.n)", '$A("$w", $a).tag()'),
      lambda p: p.w + str(p.a), "str(n) turns the number into text so + can join them."),
    T(L(*INIT, "    def big(self):", "        return self.n > $b", "$A($a).big()"), lambda p: p.a > p.b,
      "$a > $b is the answer."),
    T(L(*INIT, "    def older(self, o):", "        return self.n > o.n", "$A($a).older($A($b))"),
      lambda p: p.a > p.b, "The method compares its own n with the other object's n."),
    T(L(*INIT, "    def gap(self, o):", "        return abs(self.n - o.n)", "$A($a).gap($A($b))"),
      lambda p: abs(p.a - p.b), "abs drops the sign of $a - $b."),
    T(L("class $A:", "    def __init__(self, items):", "        self.items = items", "    def total(self):",
        "        return sum(self.items)", "$A([$a, $b, $c]).total()"), lambda p: p.a + p.b + p.c, "sum adds the list."),
    T(L("class $A:", "    def __init__(self, items):", "        self.items = items", "    def many(self):",
        "        return len([x for x in self.items if x > $b])", "$A([$a, $c, $d]).many()"),
      lambda p: len([x for x in (p.a, p.c, p.d) if x > p.b]), "Count the items bigger than $b."),
    T(L(*INIT, "    def get(self):", "        return self.n", "    def set(self, k):", "        self.n = k",
        "        return self", "$A($a).set($b).get()"), lambda p: p.b, "set returns self, so .get() asks the same object."),
    T(L(*INIT, "    @classmethod", "    def make(cls):", "        return cls($a)", "$A.make().n"), lambda p: p.a,
      "make builds an object with n = $a."),
    T(L("class $A:", "    @staticmethod", "    def double(x):", "        return x * 2", "$A.double($a)"),
      lambda p: p.a * 2, "A static method is a plain function kept inside the class."),
    T(L(*INIT, "    @staticmethod", "    def double(x):", "        return x * 2", "$A($b).double($a)"),
      lambda p: p.a * 2, "A static method ignores the object: it doubles $a."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def __len__(self):",
        "        return len(self.items)", "len($A())"), 3, "len(x) calls __len__."),
    T(L("class $A:", "    def __init__(self, x):", "        self.x = x", "    def __add__(self, o):",
        "        return $A(self.x + o.x)", "($A($a) + $A($b)).x"), lambda p: p.a + p.b, "+ calls __add__."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def __getitem__(self, i):",
        "        return self.items[i]", "$A()[1]"), lambda p: p.b, "x[1] calls __getitem__(1): the second item."),
    T(L(*INIT, "    def __call__(self, k):", "        return self.n + k", "x = $A($a)", "x($b)"), lambda p: p.a + p.b,
      "x(...) calls __call__."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b]", "    def __contains__(self, k):",
        "        return k in self.items", "$a in $A()"), True, "in calls __contains__, and $a is in the list."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b]", "    def __contains__(self, k):",
        "        return k in self.items", "$c in $A()"), False, "$c is not one of the two items."),
    T(L(*INIT, "    def __bool__(self):", "        return self.n > 0", "bool($A(0))"), False,
      "bool() calls __bool__: 0 > 0 is False."),
    T(L(*INIT, "    def __lt__(self, o):", "        return self.n < o.n", "sorted([$A($a), $A($b)])[0].n"),
      lambda p: min(p.a, p.b), "sorted uses __lt__, so the smaller n comes first."),
    T(L("class $A:", "    def __init__(self):", "        self.items = [$a, $b, $c]", "    def __iter__(self):",
        "        return iter(self.items)", "sum($A())"), lambda p: p.a + p.b + p.c,
      "sum loops over the object through __iter__."),
    T(L(*INIT, "    def fill(self, xs):", "        xs.append(self.n)", "xs = [$b]", "$A($a).fill(xs)", "xs[-1]"),
      lambda p: p.a, "fill appended n to the list it was given."),
    T(L("class $A:", "    def __init__(self, x, y):", "        self.x = x", "        self.y = y", "    def pair(self):",
        "        return self.x, self.y", "p, q = $A($a, $b).pair()", "q"), lambda p: p.b, "pair gives back a tuple (x, y)."),
    T(L(*INIT, "    def doubled(self):", "        return $A(self.n * 2)", "$A($a).doubled().n"), lambda p: p.a * 2,
      "doubled returns a new object holding twice n."),
    T(L(*INIT, "    def doubled(self):", "        return $A(self.n * 2)", "x = $A($a)", "x.doubled()", "x.n"),
      lambda p: p.a, "doubled builds a new object and leaves x alone."),
    T(L("class $A:", "    def fact(self, k):", "        return 1 if k <= 1 else k * self.fact(k - 1)",
        "$A().fact($a)"), lambda p: _fact(p.a), "k * (k-1) * ... * 1 for k = $a."),
    T(L(*INIT, "    def get(self):", "        n = $b", "        return self.n", "$A($a).get()"), lambda p: p.a,
      "n is a local name; self.n is the attribute."),
    T(L(*INIT, "    def total(self, *xs):", "        return self.n + sum(xs)", "$A($a).total($b, $c)"),
      lambda p: p.a + p.b + p.c, "*xs gathers the extra arguments."),
    T(L(*INIT, "    def scale(self, k=1):", "        return self.n * k", "$A($a).scale(k=$b)"), lambda p: p.a * p.b,
      "k was passed by name."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", "    def loud(self):",
        "        return self.name.upper()", '$A("$w").loud()'), lambda p: upper(p.w), "upper() gives capitals."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", "    def size(self):",
        "        return len(self.name)", '$A("$w").size()'), lambda p: len(p.w), "len counts the characters."),
    T(L(*INIT, "    def get(self):", "        return self.n", "x = $A($a)", "x.get() * 2 + x.get()"),
      lambda p: p.a * 3, "Each call gives $a: $a * 2 + $a."),
    T(L("class $A:", "    items = [$a, $b, $c]", "    def first_over(self, lim):",
        "        for i in self.items:", "            if i > lim:", "                return i",
        "$A().first_over($d)"), lambda p: _first_over([p.a, p.b, p.c], p.d),
      "It returns the first item over $d, or None when the loop ends without one."),
    T(L("class $A:", "    def __init__(self, items):", "        self.items = items", "    def has(self, k):",
        "        return k in self.items", "$A([$a, $b]).has($c)"), False, "$c is not in the list."),
    T(L(*INIT, "    def __eq__(self, o):", "        return self.n == o.n", "$A($a) == $A($a)"), True,
      "__eq__ compares the n values, and both are $a."),
    T(L(*INIT, "    def even(self):", "        return self.n % 2 == 0", "$A($a).even()"), lambda p: p.a % 2 == 0,
      "$a % 2 is the remainder after halving."),
    T(L("class $A:", "    def __init__(self, *parts):", "        self.parts = parts", "    def path(self):",
        '        return "-".join(self.parts)', '$A("$w", "$v").path()'), lambda p: p.w + "-" + p.v,
      "join puts the - between the parts."),
]

# ── 3. Class or Instance ────────────────────────────────────────────────

CN = ("class $A:", "    n = $a")
TOTAL2 = ("    def total(self):", "        return self.n * 2")

SHARED = [
    T(L(*CN, "x = $A()", "x.n = $b", "$A.n"), lambda p: p.a, "x.n = $b made a new attribute on x only; the class still says $a."),
    T(L(*CN, "x = $A()", "y = $A()", "x.n = $b", "y.n"), lambda p: p.a, "Only x got its own n; y still reads the class's $a."),
    T(L(*CN, "x = $A()", "$A.n = $b", "x.n"), lambda p: p.b, "x has no n of its own, so it reads the class's, now $b."),
    T(L(*CN, "x = $A()", "x.n = $b", "$A.n = $c", "x.n"), lambda p: p.b, "x's own n ($b) hides the class's, whatever the class says."),
    T(L(*CN, "x = $A()", "x.n += $b", "$A.n"), lambda p: p.a, "x.n += $b reads the class's $a but writes a new n onto x."),
    T(L(*CN, "x = $A()", "x.n += $b", "x.n"), lambda p: p.a + p.b, "It read $a from the class, added $b, and stored the sum on x."),
    T(L(*CN, "x = $A()", "y = $A()", "x.n += $b", "y.n"), lambda p: p.a, "The sum landed on x only; y still reads the class's $a."),
    T(L("class $A:", "    items = []", "x = $A()", "y = $A()", "x.items.append($a)", "y.items"),
      lambda p: [p.a], "items belongs to the class, so x and y share one list."),
    T(L("class $A:", "    items = []", "x = $A()", "y = $A()", "x.items.append($a)", "y.items.append($b)",
        "len(x.items)"), 2, "Both appends went into the one shared list."),
    T(L("class $A:", "    def __init__(self):", "        self.items = []", "x = $A()", "y = $A()",
        "x.items.append($a)", "len(y.items)"), 0, "__init__ gives each object its own list."),
    T(L("class $A:", "    count = $a", "    def __init__(self):", "        $A.count += 1", "$A()", "$A()", "$A.count"),
      lambda p: p.a + 2, "$A.count += 1 changes the class's count: $a plus two objects."),
    T(L("class $A:", "    count = 0", "    def __init__(self):", "        self.count += 1", "$A()", "$A()", "$A.count"), 0,
      "self.count += 1 writes onto each new object; the class's count never moves."),
    T(L("class $A:", "    count = 0", "    def __init__(self):", "        self.count += 1", "x = $A()", "y = $A()",
        "y.count"), 1, "Each object reads 0 from the class and stores 1 on itself."),
    T(L("class $A:", "    count = 0", "    def __init__(self):", "        type(self).count += 1", "x = $A()",
        "y = $A()", "y.count"), 2, "type(self).count is the class's count, shared by both."),
    T(L("class $A:", "    count = 0", "    def __init__(self):", "        self.__class__.count += 1", "x = $A()",
        "y = $A()", "x.count"), 2, "self.__class__ is the class, so both objects bumped the shared count."),
    T(L(*CN, "x = $A()", "x.n = $b", "len(vars(x))"), 1, "x has one attribute of its own: n."),
    T(L(*CN, "x = $A()", "y = $A()", "x.n = $b", "len(vars(y))"), 0, "y has no attributes of its own."),
    T(L(*CN, "x = $A()", "y = $A()", "x.n = $b", '"n" in vars(y)'), False, "Only x has its own n."),
    T(L(*CN, "x = $A()", "x.n = $b", "del x.n", "x.n"), lambda p: p.a, "Deleting x's own n uncovers the class's $a again."),
    T(L("class $A:", '    kind = "$w"', "x = $A()", "y = $A()", 'x.kind = "$v"', "y.kind"), lambda p: p.w,
      "Only x was changed."),
    T(L(*CN, "class $B($A):", "    n = $b", "$B().n"), lambda p: p.b, "$B has its own n, which wins."),
    T(L(*CN, "class $B($A):", "    n = $b", "$A().n"), lambda p: p.a, "$A is the parent: its n is untouched."),
    T(L(*CN, "class $B($A):", "    pass", "$B().n"), lambda p: p.a, "$B has no n, so it borrows $A's."),
    T(L(*CN, "class $B($A):", "    pass", "$A.n = $b", "$B.n"), lambda p: p.b, "$B reads through to $A, which now says $b."),
    T(L(*CN, "class $B($A):", "    pass", "$B.n = $c", "$A.n"), lambda p: p.a, "Assigning on $B gives $B its own n; $A is unchanged."),
    T(L("class $A:", "    items = []", "class $B($A):", "    pass", "$B.items.append($a)", "$A.items"),
      lambda p: [p.a], "$B never made its own list; it shares $A's."),
    T(L(*CN, "x = $A()", 'setattr($A, "n", $b)', "x.n"), lambda p: p.b, "setattr on the class changes what every object reads."),
    T(L(*CN, *TOTAL2, "x = $A()", "x.n = $b", "x.total()"), lambda p: p.b * 2, "self.n finds x's own n first."),
    T(L(*CN, *TOTAL2, "x = $A()", "y = $A()", "x.n = $b", "y.total()"), lambda p: p.a * 2, "y has no n of its own: it uses the class's $a."),
    T(L("class $A:", "    n = $a", "    def total(self):", "        return $A.n * 2", "x = $A()", "x.n = $b",
        "x.total()"), lambda p: p.a * 2, "total asks the class directly, ignoring x's own n."),
    T(L("class $A:", "    rate = $a", "    def __init__(self, q):", "        self.q = q", "    def cost(self):",
        "        return self.q * self.rate", "$A($b).cost()"), lambda p: p.a * p.b, "rate comes from the class: $b * $a."),
    T(L(*CN, "x = $A()", "x.n = $b", "x.__class__.n"), lambda p: p.a, "x.__class__ is the class, so this skips x's own n."),
    T(L("class $A:", "    reg = {}", "x = $A()", "y = $A()", 'x.reg["k"] = $a', 'y.reg["k"]'), lambda p: p.a,
      "reg is one dict on the class, seen by x and y alike."),
    T(L("class $A:", "    reg = {}", "x = $A()", "y = $A()", "x.reg = {}", 'x.reg["k"] = $a', '"k" in y.reg'), False,
      "x.reg = {} gave x its own dict, so y's lookup finds the class's empty one."),
    T(L("class $A:", "    items = []", "x = $A()", "x.items += [$a]", "$A.items"), lambda p: [p.a],
      "+= on a list changes it in place - the class's list - and then rebinds x.items to it."),
    T(L("class $A:", "    items = []", "x = $A()", "x.items = x.items + [$a]", "$A.items"), [],
      "+ builds a new list, which is stored on x; the class's list is still empty."),
    T(L(*CN, "x = $A()", "y = $A()", "x.n = x.n + $b", "y.n = y.n + $c", "x.n + y.n"), lambda p: 2 * p.a + p.b + p.c,
      "Each one reads $a and stores its own sum: ($a + $b) + ($a + $c)."),
    T(L(*CN, "x = $A()", "del $A.n", 'hasattr(x, "n")'), False, "Without the class's n and no n of its own, x has none."),
    T(L("class $A:", "    total = 0", "    def __init__(self, n):", "        $A.total += n", "$A($a)", "$A($b)", "$A.total"),
      lambda p: p.a + p.b, "Every object adds to the one class-wide total."),
    T(L("class $A:", "    total = 0", "    def __init__(self, n):", "        self.total += n", "x = $A($a)", "y = $A($b)",
        "$A.total"), 0, "self.total += n stored the sums on x and y; the class's total stayed 0."),
    T(L("class $A:", "    total = 0", "    def __init__(self, n):", "        self.total += n", "x = $A($a)", "y = $A($b)",
        "y.total"), lambda p: p.b, "y read 0 from the class and added $b."),
    T(L("class $A:", "    nxt = $a", "    def __init__(self):", "        self.id = $A.nxt", "        $A.nxt += 1",
        "x = $A()", "y = $A()", "y.id"), lambda p: p.a + 1, "x took $a and moved the counter on, so y took the next number."),
    T(L("class $A:", "    nxt = $a", "    def __init__(self):", "        self.id = $A.nxt", "        $A.nxt += 1",
        "x = $A()", "y = $A()", "x.id"), lambda p: p.a, "x was first: it took the counter's starting value."),
    T(L("class $A:", "    n = $a", "    @classmethod", "    def bump(cls):", "        cls.n += 1", "$A.bump()", "$A().bump()",
        "$A.n"), lambda p: p.a + 2, "A classmethod gets the class even when called on an object."),
    T(L(*CN, "    def bump(self):", "        self.n += 1", "x = $A()", "x.bump()", "x.bump()", "$A.n"), lambda p: p.a,
      "bump wrote onto x each time; the class's n never changed."),
    T(L(*CN, "    def bump(self):", "        self.n += 1", "x = $A()", "x.bump()", "x.bump()", "x.n"), lambda p: p.a + 2,
      "The first bump created x.n from the class's $a; the second added to it."),
    T(L("class $A:", "    n = $a", "    def __init__(self, n=None):", "        if n is not None:", "            self.n = n",
        "$A().n + $A($b).n"), lambda p: p.a + p.b, "The first has no n of its own and reads $a; the second stored $b."),
    T(L(*CN, "x = $A()", "x.n = $b", "$A.n = $c", "y = $A()", "x.n + y.n"), lambda p: p.b + p.c,
      "x keeps its own $b; the new y reads the class's $c."),
]

# ── 4. Inherit It ───────────────────────────────────────────────────────

HI_A = ("class $A:", "    def hi(self):", '        return "$w"')

INHERIT = [
    T(L(*HI_A, "class $B($A):", "    pass", "$B().hi()"), lambda p: p.w, "$B has no hi, so it runs $A's."),
    T(L(*HI_A, "class $B($A):", "    def hi(self):", '        return "$v"', "$B().hi()"), lambda p: p.v,
      "$B's own hi overrides $A's."),
    T(L(*HI_A, "class $B($A):", "    def hi(self):", '        return "$v"', "$A().hi()"), lambda p: p.w,
      "$A is the parent: it never sees $B's version."),
    T(L(*HI_A, "class $B($A):", "    def hi(self):", '        return super().hi() + "!"', "$B().hi()"),
      lambda p: p.w + "!", "super().hi() runs $A's hi, then ! is joined on."),
    T(L(*HI_A, "class $B($A):", "    def hi(self):", '        return "$v" + super().hi()', "$B().hi()"),
      lambda p: p.v + p.w, "$v first, then what $A's hi gives."),
    T(L(*HI_A, "class $B($A):", "    pass", "class $C($B):", "    def hi(self):", '        return super().hi() + "!"',
        "$C().hi()"), lambda p: p.w + "!", "super() inside $C finds hi by going up: $B has none, so $A's."),
    T(L("class $A:", '    def f(self): return "a"', "class $B($A):", '    def f(self): return super().f() + "b"',
        "class $C($B):", '    def f(self): return super().f() + "c"', "$C().f()"), "abc",
      "Each f runs its parent's first, then adds its own letter."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def __init__(self, n):",
        "        super().__init__(n + $b)", "$B($a).n"), lambda p: p.a + p.b, "$B passes n + $b up, and $A stores it."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def __init__(self, n):",
        "        super().__init__(n)", "        self.n *= 2", "$B($a).n"), lambda p: p.a * 2, "$A stored n, then $B doubled it."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def __init__(self, n):",
        "        self.m = n", 'hasattr($B($a), "n")'), False, "$B's __init__ replaced $A's and never called it, so n was never set."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def double(self):",
        "        return self.n * 2", "$B($a).double()"), lambda p: p.a * 2, "$B inherits __init__, so n is set; double uses it."),
    T(L("class $A:", "    def run(self):", '        return self.name() + "!"', "    def name(self):", '        return "$w"',
        "class $B($A):", "    def name(self):", '        return "$v"', "$B().run()"), lambda p: p.v + "!",
      "run is $A's, but self.name() finds $B's override."),
    T(L("class $A:", "    def total(self):", "        return self.base() + 1", "    def base(self):", "        return 1",
        "class $B($A):", "    def base(self):", "        return $b", "$B().total()"), lambda p: p.b + 1,
      "total calls self.base(), and self is a $B."),
    T(L("class $A:", "    def run(self):", "        return self.step() + self.step()", "    def step(self):",
        "        return 1", "class $B($A):", "    def step(self):", "        return $a", "$B().run()"), lambda p: p.a * 2,
      "Both calls go to $B's step."),
    T(L("class $A:", '    def f(self): return "$w"', "class $B:", '    def f(self): return "$v"', "class $C($A, $B):",
        "    pass", "$C().f()"), lambda p: p.w, "With two parents, the first listed is searched first."),
    T(L("class $A:", '    def f(self): return "$w"', "class $B:", '    def f(self): return "$v"', "class $C($B, $A):",
        "    pass", "$C().f()"), lambda p: p.v, "Now $B is listed first."),
    T(L("class $A:", '    def f(self): return "a"', "class $B($A): pass", "class $C($A):",
        '    def f(self): return "c"', "class $D($B, $C): pass", "$D().f()"), "c",
      "The search order is $D, $B, $C, $A: $C is reached before $A."),
    T(L("class $A: pass", "class $B($A): pass", "class $C($A): pass", "class $D($B, $C): pass", "len($D.__mro__)"), 5,
      "The order is $D, $B, $C, $A, object."),
    T(L("class $A: pass", "class $B($A): pass", "class $C($B): pass", "len($C.__mro__)"), 4,
      "$C, $B, $A, object."),
    T(L("class $A:", '    sound = "$w"', "    def speak(self):", "        return self.sound", "class $B($A):",
        '    sound = "$v"', "$B().speak()"), lambda p: p.v, "self is a $B, so self.sound is $B's."),
    T(L("class $A:", '    sound = "$w"', "    def speak(self):", "        return self.sound * 2", "class $B($A):",
        "    pass", "$B().speak()"), lambda p: p.w * 2, "A string times 2 repeats it."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def extra(self):",
        "        return self.n + 1", "$B($a).extra()"), lambda p: p.a + 1, "$B adds a method; __init__ still comes from $A."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "    def add(self, k):", "        return self.n + k",
        "class $B($A):", "    def add(self, k):", "        return super().add(k) * 2", "$B($a).add($b)"),
      lambda p: (p.a + p.b) * 2, "super().add(k) gives $a + $b, then $B doubles it."),
    T(L("class $A:", "    def f(self):", "        raise NotImplementedError", "class $B($A):", "    def f(self):",
        "        return $a", "$B().f()"), lambda p: p.a, "$B supplies the f that $A only promised."),
    T(L(*HI_A, "class $B($A):", "    def hi(self):", '        return $A.hi(self) + "$v"', "$B().hi()"),
      lambda p: p.w + p.v, "$A.hi(self) calls the parent's hi directly."),
    T(L("class $A:", "    def __init__(self):", '        self.kind = "$w"', "class $B($A):", "    def __init__(self):",
        "        super().__init__()", '        self.kind = "$v"', "$B().kind"), lambda p: p.v,
      "$B sets kind after $A did, so $B's value wins."),
    T(L("class $A:", "    def __init__(self):", '        self.kind = "$w"', "class $B($A):", "    def __init__(self):",
        '        self.kind = "$v"', "        super().__init__()", "$B().kind"), lambda p: p.w,
      "$A's __init__ ran last and overwrote kind."),
    T(L("class $A:", "    def __init__(self, n):", "        self.n = n", "class $B($A):", "    def __init__(self, n):",
        "        self.n = $b", "        super().__init__(n)", "$B($a).n"), lambda p: p.a, "$A's __init__ ran after and stored n."),
    T(L("class $A:", "    @classmethod", "    def make(cls):", "        return cls().name()",
        '    def name(self): return "$w"', "class $B($A):", '    def name(self): return "$v"', "$B.make()"), lambda p: p.v,
      "cls is $B when called as $B.make(), so cls() is a $B."),
    T(L("class $A:", "    def who(self):", "        return type(self).__name__", "class $B($A):", "    pass", "$B().who()"),
      lambda p: p.B, "type(self) is the object's own class: $B."),
    T(L("class $A:", "    def who(self):", '        return "$A"', "class $B($A):", "    pass", "$B().who()"),
      lambda p: p.A, "who is inherited and returns a fixed word."),
    T(L("class $A:", "    def cost(self): return $a", "class $B($A):", "    def cost(self): return super().cost() + $b",
        "class $C($B):", "    def cost(self): return super().cost() + $c", "$C().cost()"), lambda p: p.a + p.b + p.c, "Each level adds its own number to its parent's."),
    T(L("class $A:", "    n = $a", "    def up(self):", "        self.n += 1", "class $B($A):", "    pass", "x = $B()",
        "x.up()", "x.n"), lambda p: p.a + 1, "up is inherited and works on x."),
    T(L("class $A:", "    n = $a", "class $B($A):", "    def __init__(self):", "        self.n = $b", "$B().n"),
      lambda p: p.b, "The object's own n beats the class's."),
    T(L("class $C:", '    def hi(self): return "$w"', "class $A: pass", "class $B($C, $A): pass", "$B().hi()"),
      lambda p: p.w, "$C is a mixin: $B picks hi up from it."),
    T(L("class $A: pass", "class $B($A): pass", "$B.__bases__[0].__name__"), lambda p: p.A, "__bases__ lists the parents."),
    T(L("class $A:", "    def f(self): return $a", "class $B($A):", "    def f(self): return $b", "$A().f() + $B().f()"),
      lambda p: p.a + p.b, "Each object runs its own class's f."),
    T(L("class $A:", "    def f(self): return $a", "class $B($A):", "    def f(self): return super().f() + super().f()",
        "$B().f()"), lambda p: p.a * 2, "super().f() is $a, called twice."),
    T(L("class $A:", "    def __init__(self, name):", "        self.name = name", "class $B($A):", "    def __init__(self, name):",
        "        super().__init__(name.upper())", '$B("$w").name'), lambda p: upper(p.w), "$B hands the name up in capitals."),
    T(L("class $A:", "    def __init__(self):", "        self.items = []", "class $B($A):",
        "    def add(self, k): self.items.append(k)", "x = $B()", "x.add($a)", "len(x.items)"), 1,
      "$A's __init__ built the list; $B's add used it."),
    T(L("class $A:", "    @property", "    def v(self): return $a", "class $B($A):", "    @property",
        "    def v(self): return super().v + $b", "$B().v"), lambda p: p.a + p.b, "super().v reads the parent's property."),
    T(L("class $A:", "    def base(self):", "        return $a", "class $B($A):", "    def total(self):",
        "        return self.base() * 2", "$B().total()"), lambda p: p.a * 2, "base is inherited, so self.base() works."),
    T(L("class $A:", "    def __init__(self):", "        self.n = $a", "class $B($A):", "    pass", "$B().n"),
      lambda p: p.a, "$B has no __init__ of its own, so $A's runs."),
    T(L("class $A:", "    def __init__(self, n=$a):", "        self.n = n", "class $B($A):", "    def __init__(self):",
        "        super().__init__()", "$B().n"), lambda p: p.a, "super().__init__() passes nothing, so n takes its default."),
]

# ── 5. Is It ────────────────────────────────────────────────────────────

H2 = ("class $A: pass", "class $B($A): pass", "x = $B()")
H3 = ("class $A: pass", "class $B($A): pass", "class $C($A): pass")
HAS = ("class $A:", "    def __init__(self, n):", "        self.n = n")

ISA = [
    YN(L(*H2, "isinstance(x, $B)"), True, "x was made by $B()."),
    YN(L(*H2, "isinstance(x, $A)"), True, "A $B is also a $A, because $B inherits from $A."),
    YN(L(*H2[:2], "isinstance($A(), $B)"), False, "A plain $A is not a $B: the parent is not an instance of its child."),
    YN(L(*H2[:2], "issubclass($B, $A)"), True, "$B is built on $A."),
    YN(L(*H2[:2], "issubclass($A, $B)"), False, "The parent is not a subclass of the child."),
    YN(L(*H2[:1], "issubclass($A, $A)"), True, "Every class counts as a subclass of itself."),
    YN(L(*H2, "isinstance(x, object)"), True, "Every object is an instance of object."),
    YN(L(*H2, "isinstance(x, (str, $A))"), True, "A tuple means: any of these. x is a $A."),
    YN(L(*H2, "isinstance(x, (str, int))"), False, "x is neither a str nor an int."),
    YN("isinstance($a, int)", True, "$a is a whole number."),
    YN("isinstance(True, int)", True, "bool is a subclass of int, so True counts as an int."),
    YN("isinstance($a, bool)", False, "$a is an int, not a bool."),
    YN('isinstance("$w", str)', True, "Text is a str."),
    YN("isinstance([$a], list)", True, "Square brackets make a list."),
    YN("isinstance(($a,), list)", False, "That is a tuple, not a list."),
    YN("isinstance($a + 0.5, int)", False, "Adding 0.5 makes a float."),
    YN("isinstance($a, float)", False, "A whole number is an int."),
    YN(L(*H3, "isinstance($B(), $C)"), False, "$B and $C are siblings: neither is the other."),
    YN(L(*H3, "isinstance($C(), $A)"), True, "$C inherits from $A."),
    YN(L(*H2, "type(x) == $A"), False, "type(x) is the exact class, $B."),
    YN(L(*H2, "type(x) is $B"), True, "x was made by $B()."),
    YN(L(*H2[:1], "type($A()) == $A"), True, "The exact class of $A() is $A."),
    YN(L(*HAS, "hasattr($A($a), 'n')"), True, "__init__ sets n."),
    YN(L(*HAS, "x = $A($a)", "hasattr(x, 'm')"), False, "Nothing ever set m."),
    YN(L(*HAS, "x = $A($a)", "x.m = $b", "hasattr(x, 'm')"), True, "x.m = ... created it."),
    YN(L("class $A:", "    def hi(self): pass", "class $B($A): pass", "hasattr($B, 'hi')"), True, "$B inherits hi from $A."),
    YN(L("class $A:", "    def hi(self): pass", "class $B($A): pass", "hasattr($B(), 'hi')"), True, "An object finds inherited methods too."),
    YN(L("class $A: pass", "class $B($A):", "    def hi(self): pass", "hasattr($A, 'hi')"), False,
       "Only the child has hi; a parent does not get its children's methods."),
    YN(L("class $A:", "    def hi(self): pass", "x = $A()", "callable(x.hi)"), True, "A method can be called."),
    YN(L(*HAS, "x = $A($a)", "callable(x.n)"), False, "An int is not callable."),
    YN(L("class $A:", "    def __call__(self): pass", "callable($A())"), True, "__call__ makes an object callable."),
    YN(L("class $A: pass", "callable($A())"), False, "Without __call__ an object cannot be called."),
    YN(L("class $A: pass", "class $B($A): pass", "class $C($B): pass", "issubclass($C, $A)"), True,
       "$C is built on $B, which is built on $A."),
    YN(L(*H2, "y = $A()", "isinstance(x, type(y))"), True, "type(y) is $A, and x is a $A."),
    YN(L(*H2, "y = $A()", "isinstance(y, type(x))"), False, "type(x) is $B, and y is only a $A."),
    YN(L(*H2, "issubclass(type(x), $A)"), True, "type(x) is $B, a subclass of $A."),
    YN(L("class $A: pass", "isinstance($A, type)"), True, "A class is itself an object, an instance of type."),
    YN(L(*H2, "isinstance(x, type)"), False, "x is an instance, not a class."),
    YN(L("class $A: pass", "isinstance(None, $A)"), False, "None is not a $A."),
    YN("isinstance(None, type(None))", True, "None is the one instance of NoneType."),
    YN(L(*H2, "hasattr(x, '__init__')"), True, "Every object inherits an __init__."),
    YN(L(*H2, "x.__class__ is $B"), True, "x.__class__ is the class of x."),
    YN(L(*H2, "x.__class__.__name__ == '$B'"), True, "The class's name is $B."),
    YN(L(*H2, "x.__class__.__name__ == '$A'"), False, "x's class is $B, not $A."),
    YN(L("class $A: pass", "class $B($A): pass", "class $C: pass", "x = $B()",
         "isinstance(x, $A) and not isinstance(x, $C)"), True, "x is a $A, and $C is unrelated."),
    YN(L(*HAS, "x = $A($a)", "'n' in vars(x)"), True, "vars(x) lists x's own attributes, and n is one."),
    YN(L(*H2, "isinstance(x, (list, $B))"), True, "x is a $B, and a tuple means any of them."),
    YN("issubclass(bool, int)", True, "bool is built on int."),
    YN("issubclass(int, bool)", False, "int is the parent of bool, not the child."),
    YN("isinstance(int, type)", True, "int is a class, and classes are instances of type."),
    YN(L("class $A: pass", 'isinstance("$w", $A)'), False, "Text is not a $A."),
]

# ── 6. Same Object ──────────────────────────────────────────────────────

PLAIN = ("class $A: pass", "x = $A()")
EQN = ("class $A:", "    def __init__(self, n):", "        self.n = n", "    def __eq__(self, o):",
       "        return self.n == o.n")
LISTS = ("class $A:", "    def __init__(self):", "        self.items = []")
CLS_LIST = ("class $A:", "    items = []", "x = $A()", "y = $A()")

SAME = [
    YN(L(*PLAIN, "y = x", "x is y"), True, "y = x gave the same object a second name."),
    YN(L(*PLAIN, "y = $A()", "x is y"), False, "Two calls, two separate objects."),
    YN(L(*PLAIN, "y = $A()", "x == y"), False, "Without an __eq__ of its own, == means the same object, and these are two."),
    YN(L(*PLAIN, "x == x"), True, "An object equals itself."),
    YN(L(*PLAIN, "y = x", "x == y"), True, "The same object, so equal."),
    YN(L("import copy", *PLAIN, "y = copy.copy(x)", "y is x"), False, "copy makes a new object."),
    YN(L("import copy", *PLAIN, "y = copy.copy(x)", "y == x"), False, "A copy is a different object, and the default == only says yes for the same one."),
    YN(L(*EQN, "$A($a) == $A($a)"), True, "__eq__ compares n, and both are $a."),
    YN(L(*EQN, "$A($a) == $A($b)"), False, "$a and $b differ."),
    YN(L(*EQN, "$A($a) is $A($a)"), False, "is asks for the same object, whatever __eq__ says: these are two."),
    YN(L(*EQN, "$A($a) != $A($a)"), False, "!= is the opposite of __eq__, which says they are equal."),
    YN(L("import copy", *EQN, "x = $A($a)", "copy.copy(x) == x"), True, "The copy has the same n, so __eq__ says equal."),
    YN(L("import copy", *EQN, "x = $A($a)", "copy.copy(x) is x"), False, "Equal but not the same object."),
    YN(L("class $A: pass", "[$A()] == [$A()]"), False, "The lists hold two different objects."),
    YN(L(*PLAIN, "[x] == [x]"), True, "Same object in both lists."),
    YN(L(*EQN, "[$A($a)] == [$A($a)]"), True, "Lists compare item by item, with __eq__."),
    YN(L(*EQN, "$A($a) in [$A($a)]"), True, "in uses ==, and __eq__ says equal."),
    YN(L("class $A: pass", "$A() in [$A()]"), False, "Without __eq__, == is identity, and these are different objects."),
    YN(L(*PLAIN, "x in {x}"), True, "The set holds x itself."),
    YN(L(*PLAIN, "y = $A()", "y in {x}"), False, "y is a different object, so a set cannot find it by hash."),
    YN(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    x: int", "$A($a) == $A($a)"), True,
       "A dataclass compares its fields."),
    YN(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    x: int", "$A($a) is $A($a)"), False,
       "Two calls, two objects, however equal."),
    YN(L("from collections import namedtuple", '$A = namedtuple("$A", "x y")', "$A($a, $b) == $A($a, $b)"), True,
       "A namedtuple is a tuple: equal fields, equal."),
    YN(L(*CLS_LIST, "x.items is y.items"), True, "items belongs to the class: one list for all."),
    YN(L(*LISTS, "x = $A()", "y = $A()", "x.items is y.items"), False, "__init__ built a list for each."),
    YN(L(*PLAIN, "lst = [x]", "lst[0] is x"), True, "The list holds x itself, not a copy."),
    YN(L(*PLAIN, "lst = [x]", "lst2 = lst.copy()", "lst2[0] is x"), True, "A shallow copy shares the items."),
    YN(L("import copy", *PLAIN, "lst = [x]", "copy.deepcopy(lst)[0] is x"), False, "deepcopy copies the objects too."),
    YN(L(*PLAIN, "x is None"), False, "x is an object, not None."),
    YN(L("class $A: pass", "x = y = $A()", "x is y"), True, "A chained assignment gives both names the one object."),
    YN(L("class $A:", "    def me(self):", "        return self", "x = $A()", "x.me() is x"), True, "me() returns the object itself."),
    YN(L("class $A:", "    def dup(self):", "        return $A()", "x = $A()", "x.dup() is x"), False, "dup() builds a new object."),
    YN(L(*PLAIN, "y = $A()", "x.__class__ is y.__class__"), True, "Both were made by $A."),
    YN(L(*H3, "type($B()) == type($C())"), False, "$B and $C are different classes."),
    YN(L(*PLAIN, "y = x", "id(x) == id(y)"), True, "One object has one id."),
    YN(L(*EQN, "x = $A($a)", "y = x", "x.n == y.n"), True, "They are the same object: same n."),
    YN(L("import copy", "class $A: pass", "x = $A()", "x.part = [$a]", "y = copy.copy(x)", "y.part is x.part"), True,
       "copy is shallow: the list inside is shared."),
    YN(L("import copy", "class $A: pass", "x = $A()", "x.part = [$a]", "y = copy.deepcopy(x)", "y.part is x.part"), False,
       "deepcopy copies the list inside too."),
    YN(L(*PLAIN, 'x == "$w"'), False, "An object is not equal to a string."),
    YN(L("class $A:", "    def __init__(self, n):", "        self.n = n", "    def __eq__(self, o):",
         "        return isinstance(o, $A) and self.n == o.n", "$A($a) == $a"), False, "__eq__ only says yes to another $A."),
    YN(L("class $A:", "    def __eq__(self, o):", "        return True", "$A() == $A()"), True, "__eq__ always says yes."),
    YN(L(*PLAIN, "y = $A()", "x is not y"), True, "They are two objects."),
    YN(L(*HAS, "$A($a).n == $A($a).n"), True, "The two n values are both $a."),
    YN(L("class $A:", "    def __init__(self, name):", "        self.name = name", '$A("$w").name == $A("$w").name'), True,
       "The names are equal strings."),
    YN(L(*LISTS, "x = $A()", "y = $A()", "x.items == y.items"), True, "Two empty lists are equal, though not the same list."),
    YN(L(*HAS, "def f(o):", "    o.n = $b", "x = $A($a)", "f(x)", "x.n == $b"), True, "f changed the object it was handed."),
    YN(L(*HAS, "def f(o):", "    o = $A($b)", "x = $A($a)", "f(x)", "x.n == $b"), False, "f only rebound its own name o."),
    YN(L("class $A: pass", "a = [$A()] * 2", "a[0] is a[1]"), True, "* repeats the same object."),
    YN(L("class $A: pass", "a = [$A() for _ in range(2)]", "a[0] is a[1]"), False, "The comprehension builds two objects."),
    YN(L(*PLAIN, 'ds = {"k": x}', 'ds["k"] is x'), True, "The dict holds x itself."),
    YN(L("import copy", *LISTS, "x = $A()", "copy.copy(x).items is x.items"), True, "A shallow copy shares the list."),
]

# ── 7. Counter Class ────────────────────────────────────────────────────

C0 = ("class $A:", "    def __init__(self): self.n = 0", "    def up(self): self.n += 1")
CADD = ("class $A:", "    def __init__(self): self.n = 0", "    def add(self, k): self.n += k")
CCOUNT = ("class $A:", "    count = 0", "    def __init__(self): $A.count += 1")


def _fib(k: int) -> int:
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def _evens_below(k: int) -> int:
    return len([i for i in range(k) if i % 2 == 0])


COUNT = [
    T(L(*C0, "x = $A()", "x.up()", "x.up()", "x.up()", "x.n"), 3, "Three calls, three ups."),
    T(L(*C0, "x = $A()", "for _ in range($a):", "    x.up()", "x.n"), lambda p: p.a, "The loop calls up() $a times."),
    T(L(*C0, "x = $A()", "y = $A()", "x.up()", "x.up()", "y.up()", "y.n"), 1, "y was called once; x's calls do not count for y."),
    T(L(*C0, "x = $A()", "y = $A()", "x.up()", "x.up()", "y.up()", "x.n"), 2, "x was called twice."),
    T(L(*CADD, "x = $A()", "x.add($a)", "x.add($b)", "x.n"), lambda p: p.a + p.b, "The two adds together: $a + $b."),
    T(L(*CADD, "x = $A()", "for i in range($a):", "    x.add(i)", "x.n"), lambda p: sum(range(p.a)),
      "i goes 0, 1, 2 ... up to $a - 1, and they all add up."),
    T(L(*C0, "    def down(self): self.n -= 1", "x = $A()", "x.up()", "x.up()", "x.down()", "x.n"), 1,
      "Up twice, down once."),
    T(L(*C0, "    def reset(self): self.n = 0", "x = $A()", "x.up()", "x.reset()", "x.up()", "x.n"), 1,
      "The reset wiped the first up; then one more."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self): self.n = min(self.n + 1, $b)",
        "x = $A()", "for _ in range($a):", "    x.up()", "x.n"), lambda p: min(p.a, p.b), "up() never goes past $b."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self): self.n += 1",
        "    def down(self): self.n = max(self.n - 1, 0)", "x = $A()", "x.down()", "x.down()", "x.up()", "x.n"), 1,
      "down() stops at 0, so only the up counts."),
    T(L(*INIT, "    def up(self): self.n += 1", "x = $A($a)", "x.up()", "x.up()", "x.n"), lambda p: p.a + 2,
      "It starts at $a, then two ups."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self): self.n = (self.n + 1) % $b",
        "x = $A()", "for _ in range($a):", "    x.up()", "x.n"), lambda p: p.a % p.b, "n wraps back to 0 every time it reaches $b."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self):", "        self.n += 1", "        return self.n",
        "x = $A()", "x.up()", "x.up()"), 2, "The last call returns the new n."),
    T(L("class $A:", "    def __init__(self): self.log = []", "    def up(self): self.log.append(len(self.log))",
        "x = $A()", "x.up()", "x.up()", "x.up()", "x.log[-1]"), 2, "Each up appends the length so far: 0, 1, 2."),
    T(L(*CCOUNT, "$A()", "$A()", "$A()", "$A.count"), 3, "Every new object bumps the one shared count."),
    T(L(*CCOUNT, "for _ in range($a):", "    $A()", "$A.count"), lambda p: p.a, "$a objects were made."),
    T(L("class $A:", "    count = 0", "    def up(self): self.count += 1", "x = $A()", "y = $A()", "x.up()", "x.up()", "y.up()",
        "x.count + y.count"), 3, "self.count += 1 gives each object its own count: 2 and 1."),
    T(L(*CCOUNT, "    @classmethod", "    def made(cls): return cls.count", "$A()", "$A()", "$A.made()"), 2,
      "made() reads the class-wide count."),
    T(L("class $A:", "    @staticmethod", "    def one(): return 1", "$A.one() + $A.one()"), 2, "A static method here just returns 1."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def __call__(self):", "        self.n += 1", "        return self.n",
        "x = $A()", "x()", "x()", "x()"), 3, "Each x() call adds 1 and returns it."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def __next__(self):", "        self.n += 1", "        return self.n",
        "x = $A()", "next(x)", "next(x)", "next(x)"), 3, "next(x) calls __next__ each time."),
    T(L(*INIT, "    def grow(self): self.n *= 2", "x = $A($a)", "x.grow()", "x.grow()", "x.n"), lambda p: p.a * 4,
      "Doubled twice: $a * 4."),
    T(L(*INIT, "    def up(self): self.n += 1", "x = $A($a)", "y = $A($b)", "for o in (x, y):", "    o.up()", "x.n + y.n"),
      lambda p: p.a + p.b + 2, "Each of the two went up once."),
    T(L(*C0, "x = $A()", "y = x", "y.up()", "x.up()", "x.n"), 2, "x and y are one object, so both ups count."),
    T(L(*C0, "def make():", "    x = $A()", "    x.up()", "    return x", "make().n"), 1, "make builds a counter and ups it once."),
    T(L(*C0, "xs = [$A() for _ in range(3)]", "xs[0].up()", "xs[0].up()", "sum(c.n for c in xs)"), 2,
      "Only the first counter moved, by 2."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self):", "        self.n += 1", "        return True",
        "x = $A()", "x.up() or x.up()", "x.n"), 1, "or stops once it has a true answer, so up() ran once."),
    T(L(*C0, "x = $A()", "x.up() or x.up()", "x.n"), 2, "up() gives None, which is false, so or tries the second too."),
    T(L("class $A:", "    def __init__(self): self.best = 0", "    def see(self, k): self.best = max(self.best, k)",
        "x = $A()", "x.see($a)", "x.see($b)", "x.see($c)", "x.best"), lambda p: max(p.a, p.b, p.c), "best keeps the largest seen."),
    T(L("class $A:", "    def __init__(self): self.total = self.count = 0", "    def see(self, k):",
        "        self.total += k", "        self.count += 1", "x = $A()", "x.see($a)", "x.see($b)", "x.total // x.count"),
      lambda p: (p.a + p.b) // 2, "The total is $a + $b, over two sightings, rounded down."),
    T(L("class $A:", "    def __init__(self, step):", "        self.n = 0", "        self.step = step",
        "    def up(self): self.n += self.step", "x = $A($a)", "x.up()", "x.up()", "x.n"), lambda p: p.a * 2,
      "Two ups of $a each."),
    T(L("class $A:", "    def __init__(self, box): self.box = box", "    def click(self): self.box[0] += 1",
        "box = [0]", "x, y = $A(box), $A(box)", "x.click()", "y.click()", "box[0]"), 2, "Both clickers count in the one shared list."),
    T(L("class $A:", "    n = 0", "    def __iadd__(self, k):", "        self.n += k", "        return self", "x = $A()", "x += $a",
        "x += $b", "x.n"), lambda p: p.a + p.b, "+= calls __iadd__, which returns the object itself."),
    T(L("class $A:", "    n = 0", "    def __iadd__(self, k):", "        self.n += k", "x = $A()", "x += $a", "x"), None,
      "__iadd__ returned nothing, so x was rebound to None."),
    T(L(*C0, "x = $A()", "while x.n < $a:", "    x.up()", "x.n"), lambda p: p.a, "The loop stops when n reaches $a."),
    T(L(*C0, "    def many(self, k):", "        for _ in range(k): self.up()", "x = $A()", "x.many($a)", "x.many($b)", "x.n"),
      lambda p: p.a + p.b, "many(k) calls up() k times: $a, then $b."),
    T(L(*C0, "x = $A()", "for i in range($a):", "    if i % 2 == 0:", "        x.up()", "x.n"), lambda p: _evens_below(p.a),
      "Count the even i from 0 to $a - 1."),
    T(L("class $A:", "    def __init__(self): self.items = []", "    def __len__(self): return len(self.items)",
        "    def add(self, k): self.items.append(k)", "x = $A()", "for i in range($a):", "    x.add(i)", "len(x)"),
      lambda p: p.a, "len(x) is the number of items added."),
    T(L(*CCOUNT, "$A()", "$A()", "$A.count = 0", "$A()", "$A.count"), 1, "The count was reset to 0, then one more object."),
    T(L("class $A:", "    count = 0", "    def __init__(self): type(self).count += 1", "class $B($A): pass", "$A()", "$B()", "$B()",
        "$A.count"), 1, "$B() bumps $B's own count, not $A's: only the one $A() counted."),
    T(L("class $A:", "    count = 0", "    def __init__(self): type(self).count += 1", "class $B($A): pass", "$A()", "$B()", "$B()",
        "$B.count"), 3, "$B's count started from $A's 1, and two $B() brought it to 3."),
    T(L("class $A:", "    count = 0", "    def __init__(self): $A.count += 1", "class $B($A): pass", "$A()", "$B()", "$B()",
        "$A.count"), 3, "$A.count names $A explicitly, so objects of $B bump it too."),
    T(L("class $A:", "    def __init__(self): self.a, self.b = 0, 1", "    def step(self): self.a, self.b = self.b, self.a + self.b",
        "x = $A()", "for _ in range($a):", "    x.step()", "x.a"), lambda p: _fib(p.a), "The Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8..."),
    T(L(*C0, "x = $A()", "x.up()", "x.n = 10", "x.up()", "x.n"), 11, "Assigning 10 replaced the count; one more up gives 11."),
    T(L(*C0, "x = $A()", "y = $A()", "x.up()", "y.n = x.n + $a", "y.up()", "y.n"), lambda p: p.a + 2,
      "x.n is 1, y.n becomes 1 + $a, and one more up."),
    T(L("class $A:", "    def __init__(self): self.n = 0", "    def up(self, k=1): self.n += k", "x = $A()", "x.up()", "x.up($a)",
        "x.n"), lambda p: p.a + 1, "The first call used the default 1."),
]

# ── 8. Default Printing ─────────────────────────────────────────────────

STR_N = ("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return '#' + str(self.n)")
BOTH = ("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return 's' + str(self.n)",
        "    def __repr__(self): return 'r' + str(self.n)")
NAMED = ("class $A:", "    def __init__(self, name): self.name = name", "    def __str__(self): return self.name")
SHOW = "str(x)"

PRINT = [
    T(L(*STR_N, "x = $A($a)", "print(x)"), lambda p: "#" + str(p.a), "print uses __str__.", run=SHOW),
    T(L(*NAMED, 'x = $A("$w")', "print(x)"), lambda p: p.w, "__str__ returns the name.", run=SHOW),
    T(L("class $A:", "    def __init__(self, name, n):", "        self.name = name", "        self.n = n",
        "    def __str__(self): return f'{self.name}:{self.n}'", 'x = $A("$w", $a)', "print(x)"),
      lambda p: p.w + ":" + str(p.a), "The f-string joins name, a colon and n.", run=SHOW),
    T(L(*STR_N, "str($A($a))"), lambda p: "#" + str(p.a), "str(x) calls __str__."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return '<' + str(self.n) + '>'",
        "x = $A($a)", 'f"{x}"'), lambda p: "<" + str(p.a) + ">", "An f-string hole shows str(x)."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __repr__(self): return f'$A({self.n})'", "x = $A($a)",
        "print(x)"), lambda p: p.A + "(" + str(p.a) + ")", "With no __str__, print falls back on __repr__.", run=SHOW),
    T(L(*BOTH, "repr($A($a))"), lambda p: "r" + str(p.a), "repr() uses __repr__."),
    T(L(*BOTH, "str($A($a))"), lambda p: "s" + str(p.a), "str() uses __str__."),
    T(L(*BOTH, "x = $A($a)", "print(x)"), lambda p: "s" + str(p.a), "print asks for str, which __str__ gives.", run=SHOW),
    T(L(*BOTH, "str([$A($a)])"), lambda p: "[r" + str(p.a) + "]", "A list shows its items with repr."),
    T(L(*BOTH, "format($A($a))"), lambda p: "s" + str(p.a), "format() with no spec uses __str__."),
    T(L(*BOTH, '"%s" % $A($a)'), lambda p: "s" + str(p.a), "%s puts in the str() text."),
    T(L(*BOTH, '"%r" % $A($a)'), lambda p: "r" + str(p.a), "%r means repr."),
    T(L(*STR_N, 'str($A($a)) + "!"'), lambda p: "#" + str(p.a) + "!", "The string from __str__, then a !."),
    T(L(*STR_N, "len(str($A($a)))"), lambda p: 1 + len(str(p.a)), "# plus the digit."),
    T(L(*STR_N, "$A($a).__str__()"), lambda p: "#" + str(p.a), "Calling the method directly gives the same text."),
    T(L(*NAMED, 'str($A("$w")).upper()'), lambda p: upper(p.w), "upper() on the name."),
    T(L(*NAMED, 'x = $A("$w")', 'y = $A("$v")', '"-".join([str(x), str(y)])'), lambda p: p.w + "-" + p.v,
      "Each str() gives a name; join puts - between."),
    T(L(*NAMED, 'x = $A("$w")', 'y = $A("$v")', '"+".join(str(o) for o in (x, y))'), lambda p: p.w + "+" + p.v,
      "str(o) runs for each object."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return f'{self.n:03d}'", "str($A($a))"),
      lambda p: "00" + str(p.a), "03d pads the number with zeros to width 3."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return f'{self.n:.1f}'", "str($A($a))"),
      lambda p: str(p.a) + ".0", ".1f shows one decimal place."),
    T(L(*STR_N, "class $B($A): pass", "str($B($a))"), lambda p: "#" + str(p.a), "$B inherits __str__."),
    T(L(*STR_N, "class $B($A):", "    def __str__(self): return 'B' + str(self.n)", "str($B($a))"), lambda p: "B" + str(p.a),
      "$B's own __str__ wins."),
    T(L("class $A:", "    def __init__(self, n): self.n = n",
        "    def __str__(self): return type(self).__name__ + str(self.n)", "class $B($A): pass", "str($B($a))"),
      lambda p: p.B + str(p.a), "type(self) is the object's real class, $B."),
    T(L(*STR_N, "class $B($A):", "    def __str__(self): return super().__str__() + '!'", "str($B($a))"),
      lambda p: "#" + str(p.a) + "!", "super().__str__() is $A's text."),
    T(L(*STR_N, "x = $A($a)", "x.n = $b", "print(x)"), lambda p: "#" + str(p.b), "__str__ runs when asked, using the current n.",
      run=SHOW),
    T(L("class $A:", "    def __init__(self, name): self.name = name", "    def __repr__(self): return f'{self.name!r}'",
        'repr($A("$w"))'), lambda p: "'" + p.w + "'", "!r puts the quotes of repr round the name."),
    T(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    x: int", "print($A($a))"),
      lambda p: p.A + "(x=" + str(p.a) + ")", "A dataclass writes a __repr__ like this.", run="str($A($a))"),
    T(L("from dataclasses import dataclass", "@dataclass", "class $A:", "    x: int", "repr($A($a))"),
      lambda p: p.A + "(x=" + str(p.a) + ")", "name(field=value)."),
    T(L("from collections import namedtuple", '$A = namedtuple("$A", "x")', "str($A($a))"),
      lambda p: p.A + "(x=" + str(p.a) + ")", "A namedtuple prints its field names too."),
    T(L("class $A:", "    def __init__(self, name): self.name = name", "    def __str__(self): return self.name.upper()",
        'str($A("$w"))'), lambda p: upper(p.w), "__str__ returns the name in capitals."),
    T(L("class $A:", "    def __init__(self, *items): self.items = items", "    def __str__(self): return '-'.join(self.items)",
        'str($A("$w", "$v"))'), lambda p: p.w + "-" + p.v, "join puts - between the items."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return '*' * self.n", "str($A($a))"),
      lambda p: "*" * p.a, "'*' * $a repeats the star $a times."),
    T(L(*STR_N, "str($A($a))[::-1]"), lambda p: reverse("#" + str(p.a)), "[::-1] reverses the text."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return str(self.n * 2)", "str($A($a))"),
      lambda p: p.a * 2, "The text of n doubled."),
    T(L("class $A:", "    def __init__(self, on): self.on = on", "    def __str__(self): return 'x' if self.on else 'o'",
        "str($A($a > 5))"), lambda p: "x" if p.a > 5 else "o", "$a > 5 decides which letter."),
    T(L(*BOTH, 'f"{$A($a)!r}"'), lambda p: "r" + str(p.a), "!r in an f-string asks for repr."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return 's' + str(self.n)", "    __repr__ = __str__",
        "repr($A($a))"), lambda p: "s" + str(p.a), "__repr__ was set to the same function as __str__."),
    T(L(*STR_N, "x = $A($a)", "x.__str__ = lambda: '$v'", "str(x)"), lambda p: "#" + str(p.a),
      "str() looks for __str__ on the class, not on the object."),
    T(L(*STR_N, '"{}".format($A($a))'), lambda p: "#" + str(p.a), "format() puts str(x) in the hole."),
    T(L(*STR_N, "x = $A($a)", 'f"{x}{x}"'), lambda p: "#" + str(p.a) + "#" + str(p.a), "Two holes, two copies of str(x)."),
    T(L(*NAMED, 'str($A("$w"))[0]'), lambda p: p.w[0], "The first character of the text."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def label(self): return 'n' + str(self.n)",
        "    def __str__(self): return self.label()", "str($A($a))"), lambda p: "n" + str(p.a), "__str__ calls label()."),
    T(L("class $A:", "    def __init__(self, n): self.n = n", "    def __str__(self): return f'{self.n}{self.n}'", "str($A($a))"),
      lambda p: str(p.a) * 2, "Two copies of the digit, joined as text."),
    T(L("class $A:", "    def __init__(self, a, b):", "        self.a = a", "        self.b = b",
        "    def __str__(self): return f'{self.a}x{self.b}'", "str($A($a, $b))"), lambda p: str(p.a) + "x" + str(p.b),
      "The two values with an x between."),
]

