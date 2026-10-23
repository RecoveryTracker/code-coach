"""Dart types pack, part 5: Enum Facts - what do enums know about themselves?

An enum constant has an `index` (its place, counting from 0) and a `name`; `values` lists them in order; `byName`
finds one by its name; printing a constant gives `Type.name`. An enhanced enum (Dart 2.17) also has fields, a `const`
constructor, getters, methods and static members. The plain-enum templates pick one of the enums in
`_darttypes_model.ENUMS` and one of its constants at random, so the answers are worked out from the table.
"""

from __future__ import annotations

import random
from typing import Callable

from ._dart_model import D, show
from ._darttypes_model import ENUMS, decl
from ._model import Maker
from .items import Item

Build = Callable[[random.Random, str, tuple[str, ...]], tuple[str, object, str]]


def _enum(build: Build, label: str) -> Maker:
    """A template over a random plain enum. `build(rng, Name, constants)` returns (the rest of the program, the answer,
    the explanation); the enum declaration goes first."""
    def make(rng: random.Random) -> Item:
        name, names = rng.choice(ENUMS)
        rest, answer, why = build(rng, name, names)
        return Item(decl(name, names) + "\n" + rest, show(answer), why)
    make.__name__ = "enum_" + label
    return make


def _prog(expr: str) -> str:
    return f"void main() => print({expr});"


def _two(rng: random.Random, names: tuple[str, ...]) -> tuple[int, int]:
    i, j = rng.sample(range(len(names)), 2)
    return i, j


def t_length(rng, n, names):
    return _prog(f"{n}.values.length"), len(names), "values lists every constant, so its length is how many there are."


def t_index(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.{names[k]}.index"), k, "index counts from 0 in the order the constants are written."


def t_name_at(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.values[{k}].name"), names[k], "values[k] is the constant at place k, counting from 0."


def t_print(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.{names[k]}"), f"{n}.{names[k]}", "An enum constant prints as the enum's name, a dot, then its own name."


def t_last(rng, n, names):
    return _prog(f"{n}.values.last.name"), names[-1], "last is the final constant."


def t_by_name(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.values.byName('{names[k]}').index"), k, "byName finds the constant with that name, and index is its place."


def t_wrap(rng, n, names):
    k = rng.randrange(len(names))
    return (_prog(f"{n}.values[({n}.{names[k]}.index + 1) % {n}.values.length].name"), names[(k + 1) % len(names)],
            "Add 1 to the index and wrap around with % to get the next constant.")


def t_odd(rng, n, names):
    odd = [x for i, x in enumerate(names) if i % 2 == 1]
    return (_prog(f"{n}.values.where((e) => e.index.isOdd).map((e) => e.name).join(',')"), ",".join(odd),
            "The constants at the odd places are kept, and their names are joined.")


def t_equal(rng, n, names):
    i, j = _two(rng, names)
    same = rng.random() < 0.5
    if same:
        j = i
    return _prog(f"{n}.{names[i]} == {n}.{names[j]}"), i == j, "A constant is equal only to itself."


def t_less(rng, n, names):
    i, j = _two(rng, names)
    return _prog(f"{n}.{names[i]}.index < {n}.{names[j]}.index"), i < j, "Compare the places in the list."


def t_indexof(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.values.indexOf({n}.{names[k]})"), k, "indexOf finds the place of the constant in values."


def t_reversed(rng, n, names):
    return _prog(f"{n}.values.reversed.first.name"), names[-1], "reversed starts from the end."


def t_skip(rng, n, names):
    return _prog(f"{n}.values.skip(1).first.name"), names[1], "skip(1) leaves out the first constant."


def t_namemap(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.values.asNameMap()['{names[k]}']"), f"{n}.{names[k]}", "asNameMap is a map from each name to its constant."


def t_strlen(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.{names[k]}.toString().length"), len(n) + 1 + len(names[k]), "toString gives Type.name: the type, a dot and the name."


def t_namelen(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.{names[k]}.name.length"), len(names[k]), "name is just the constant's own name."


def t_is_enum(rng, n, names):
    return _prog(f"{n}.{rng.choice(names)} is Enum"), True, "Every enum constant is an Enum."


def t_contains(rng, n, names):
    return _prog(f"{n}.values.contains({n}.{rng.choice(names)})"), True, "values holds every constant."


def t_is_last(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"{n}.values.length - 1 == {n}.{names[k]}.index"), k == len(names) - 1, "The last constant has the highest index, length minus 1."


def t_first_len(rng, n, names):
    k = rng.randrange(len(names))
    first = next(x for x in names if len(x) == len(names[k]))
    return (_prog(f"{n}.values.firstWhere((e) => e.name.length == {len(names[k])}).name"), first,
            "firstWhere stops at the first constant whose name has that length.")


def t_interp(rng, n, names):
    k = rng.randrange(len(names))
    return _prog(f"'${{{n}.{names[k]}.name}}!'"), names[k] + "!", "Interpolating name gives the bare name."


def t_map(rng, n, names):
    vals = [rng.randint(2, 9) for _ in names]
    k = rng.randrange(len(names))
    entries = ", ".join(f"{n}.{x}: {v}" for x, v in zip(names[:3], vals))
    k = k % 3
    return _prog("{" + entries + "}[" + f"{n}.{names[k]}]"), vals[k], "A constant works as a map key, and the lookup finds its value."


def t_switch(rng, n, names):
    vals = [rng.randint(2, 9) for _ in names]
    k = rng.randrange(len(names))
    arms = ", ".join(f"{n}.{x} => {v}" for x, v in zip(names, vals))
    rest = f"int f({n} e) => switch (e) {{ {arms} }};\nvoid main() => print(f({n}.{names[k]}));"
    return rest, vals[k], "A switch expression over an enum must cover every constant, and the arm for this constant runs."


def t_switch_default(rng, n, names):
    k = rng.randrange(len(names))
    j = rng.randrange(len(names))
    rest = (f"String f({n} e) {{\n  switch (e) {{\n    case {n}.{names[j]}: return 'hit';\n"
            f"    default: return 'miss';\n  }}\n}}\nvoid main() => print(f({n}.{names[k]}));")
    return rest, "hit" if k == j else "miss", "Only the named constant takes the case; every other constant falls to default."


def t_sort(rng, n, names):
    picks = rng.sample(range(len(names)), 3)
    shown = ", ".join(f"{n}.{names[i]}" for i in picks)
    rest = f"void main() => print(([{shown}]..sort((p, q) => p.index - q.index)));"
    return rest, [f"{n}.{names[i]}" for i in sorted(picks)], "Sorting by index puts the constants in the order they were declared."


def t_missing(rng, n, names):
    rest = (f"void main() {{\n  try {{ {n}.values.byName('{rng.choice(['zzz', 'nope', 'xyz'])}'); print('found'); }}\n"
            f"  on ArgumentError {{ print('missing'); }}\n}}")
    return rest, "missing", "byName throws an ArgumentError when no constant has that name."


PLAIN: list[Maker] = [_enum(f, f.__name__[2:]) for f in (
    t_length, t_index, t_name_at, t_print, t_last, t_by_name, t_wrap, t_odd, t_equal, t_less, t_indexof, t_reversed,
    t_skip, t_namemap, t_strlen, t_namelen, t_is_enum, t_contains, t_is_last, t_first_len, t_interp, t_map, t_switch,
    t_switch_default, t_sort, t_missing)]

SIZE = "enum Size { s($a), m($b), l($c); final int n; const Size(this.n); }\n"

ENHANCED: list[Maker] = [
    D(SIZE + "void main() => print(Size.m.n);", lambda p: p["b"], "Each constant carries the value it was made with."),
    D(SIZE + "void main() => print(Size.s.n + Size.l.n);", lambda p: p["a"] + p["c"], "Add the values of the two constants."),
    D(SIZE + "void main() => print(Size.values.map((e) => e.n).reduce((x, y) => x + y));", lambda p: p["a"] + p["b"] + p["c"], "map takes each constant's n, and reduce adds them."),
    D(SIZE + "void main() => print(Size.values.map((e) => e.n).toList());", lambda p: [p["a"], p["b"], p["c"]], "The values come out in the order the constants are written."),
    D(SIZE + "void main() => print(Size.values.firstWhere((e) => e.n == $b).name);", "m", "m is the constant made with that value."),
    D(SIZE + "void main() => print(Size.l.index + Size.l.n);", lambda p: 2 + p["c"], "index is 2 for the third constant; n is its own value."),
    D("enum Size { s(1), m(2); final int n; const Size(this.n); int get dbl => n * $a; }\nvoid main() => print(Size.m.dbl);", lambda p: 2 * p["a"], "An enum can have getters that use its fields."),
    D("enum Op { add, mul; int run(int a, int b) => this == Op.add ? a + b : a * b; }\nvoid main() => print(Op.mul.run($a, $b));", lambda p: p["a"] * p["b"], "An enum can have methods, and this is the constant it was called on."),
    D("enum Op { add, mul; int run(int a, int b) => this == Op.add ? a + b : a * b; }\nvoid main() => print(Op.add.run($a, $b));", lambda p: p["a"] + p["b"], "this is Op.add here, so the method adds."),
    D("enum Light {\n  red, green;\n  String toString() => name.toUpperCase();\n}\nvoid main() => print(Light.green);", "GREEN", "print uses toString, and the enum overrides it."),
    D("enum Light {\n  red, green;\n  String toString() => name.toUpperCase();\n}\nvoid main() => print(Light.green.name);", "green", "name is still the plain name; only toString changed."),
    D("enum E {\n  a, b, c;\n  static E parse(String s) => values.byName(s);\n}\nvoid main() => print(E.parse('c').index);", 2, "A static method can use values and byName."),
    D("enum Planet {\n  earth('Earth', 3), mars('Mars', 4);\n  const Planet(this.label, this.pos);\n  final String label;\n  final int pos;\n}\nvoid main() => print(Planet.mars.label + Planet.earth.pos.toString());", "Mars3", "Two fields, set by the constructor."),
    D("enum Unit {\n  km(1000, 'km'), m(1, 'm');\n  final int f; final String s;\n  const Unit(this.f, this.s);\n  String show(int n) => (n * f).toString() + s;\n}\nvoid main() => print(Unit.km.show($a));", lambda p: str(1000 * p["a"]) + "km", "show multiplies by the factor and adds the unit."),
    D("enum Box<T> {\n  i<int>(1), s<String>('a');\n  final T v;\n  const Box(this.v);\n}\nvoid main() => print(Box.s.v);", "a", "An enum can be generic; each constant fixes its own T."),
    D("enum Day { mon, tue, wed }\nvoid main() {\n  const d = Day.wed;\n  print(d.index);\n}", 2, "A constant can be used in a const variable."),
    D("enum Mode { off, on }\nextension on Mode {\n  Mode get flip => this == Mode.on ? Mode.off : Mode.on;\n}\nvoid main() => print(Mode.off.flip);", "Mode.on", "The extension adds flip, and it prints with the type name."),
    D("enum Level { low, mid, high }\nint score(Level l) => switch (l) { Level.low => 1, Level.mid => 5, Level.high => 9 };\nvoid main() => print(Level.values.map(score).reduce((a, b) => a + b));", 15, "The switch gives 1, 5 and 9 for the three constants; their sum is 15."),
    D("enum Level { low, mid, high }\nString tag(Level l) => switch (l) { Level.low || Level.mid => 'ok', Level.high => 'hot' };\nvoid main() => print(Level.values.map(tag).join(' '));", "ok ok hot", "One arm can cover several constants with ||."),
]

ENUMS_ALL: list[Maker] = PLAIN + ENHANCED
