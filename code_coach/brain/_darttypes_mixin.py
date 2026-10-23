"""Dart types pack, part 1: Mixin Order - which method runs when `with` stacks mixins on a class?

The rule (linearisation): `class B extends A with M, N` builds the chain A, then M on top of A, then N on top of M, and
B's own members on top of all of that. A call finds the member in the TOPMOST layer, and `super.f()` steps one layer
down. The templates are complete programs (they declare classes, so they have `main`); Dart's `$` is written `$$`.
"""

from __future__ import annotations

import random
from itertools import product

from ._dart_model import D, P, to_upper
from ._darttypes_model import lin
from ._model import Maker
from .items import Item

TOP = "The last mixin named in with sits on top, so its version is found first."
SUPER = "super.f() steps one layer down the chain, so the tags are glued from the top layer to the bottom."


def _chain(order: tuple[str, ...], flags: dict[str, bool]) -> Maker:
    """Two mixins M and N on A (each answers a tag, with `super.f()` glued after it when its flag is set), applied in
    `order`. The answer is read off the chain with `lin`."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        tags = {"M": p["s2"], "N": p["s3"]}
        lines = [f"class A {{ String f() => '{p['s1']}'; }}"]
        for name in ("M", "N"):
            if flags[name]:
                lines.append(f"mixin {name} on A {{ String f() => '{tags[name]}' + super.f(); }}")
            else:
                lines.append(f"mixin {name} {{ String f() => '{tags[name]}'; }}")
        lines.append(f"class B extends A with {', '.join(order)} {{}}")
        lines.append("void main() => print(B().f());")
        answer = lin(p["s1"], [(tags[n], flags[n]) for n in order])
        top = order[-1]
        if not flags[top]:
            why = f"{top} is the last in with and never calls super, so its tag alone is the answer."
        else:
            why = SUPER
        return Item("\n".join(lines), answer, why)
    make.__name__ = "chain_" + "".join(order) + "".join("1" if flags[n] else "0" for n in ("M", "N"))
    return make


CHAINS: list[Maker] = [
    _chain(order, {"M": fm, "N": fn})
    for order in (("M", "N"), ("N", "M"))
    for fm, fn in product((False, True), repeat=2)
]

MIXINS: list[Maker] = CHAINS + [
    D("class A { String f() => '$s1'; }\nmixin M { String f() => '$s2'; }\nclass B extends A with M {}\nvoid main() => print(B().f());",
      lambda p: p["s2"], "A mixin is stacked on top of the superclass, so its f beats A's."),
    D("class A { String f() => '$s1'; }\nmixin M { String f() => '$s2'; }\nclass B extends A with M {\n  String f() => '$s3';\n}\nvoid main() => print(B().f());",
      lambda p: p["s3"], "The class's own method sits above every mixin."),
    D("class A { String f() => '$s1'; }\nmixin M { String g() => '$s2'; }\nclass B extends A with M {}\nvoid main() => print(B().f() + B().g());",
      lambda p: p["s1"] + p["s2"], "M adds g and leaves f alone, so f still comes from A."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => '$s2' + super.f(); }\nclass B extends A with M {\n  String f() => '$s3' + super.f();\n}\nvoid main() => print(B().f());",
      lambda p: p["s3"] + p["s2"] + p["s1"], SUPER),
    D("class A { String f() => '$s1'; }\nclass B extends A { String f() => '$s2' + super.f(); }\nmixin M on A { String f() => '$s3' + super.f(); }\nclass C extends B with M {}\nvoid main() => print(C().f());",
      lambda p: p["s3"] + p["s2"] + p["s1"], "The mixin goes on top of the whole B chain, so M runs first, then B, then A."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => '$s2' + super.f(); }\nclass B extends A with M {}\nclass C extends B with M {}\nvoid main() => print(C().f());",
      lambda p: p["s2"] + p["s2"] + p["s1"], "C applies M again on top of B, which already had M on top of A."),
    D("class A { int f(int n) => n + 1; }\nmixin M on A { int f(int n) => super.f(n) * 2; }\nmixin N on A { int f(int n) => super.f(n) + $a; }\nclass B extends A with M, N {}\nvoid main() => print(B().f($b));",
      lambda p: (p["b"] + 1) * 2 + p["a"], "N is on top: N calls M, M calls A. So (n + 1) doubled, then plus the extra."),
    D("class A { int f(int n) => n + 1; }\nmixin M on A { int f(int n) => super.f(n) * 2; }\nmixin N on A { int f(int n) => super.f(n) + $a; }\nclass B extends A with N, M {}\nvoid main() => print(B().f($b));",
      lambda p: (p["b"] + 1 + p["a"]) * 2, "M is on top now: M calls N, N calls A. So (n + 1 + extra), all doubled."),
    D("class A { int f() => $a; }\nmixin M on A { int f() => super.f() * $b; }\nclass B extends A with M {}\nvoid main() => print(B().f() + A().f());",
      lambda p: p["a"] * p["b"] + p["a"], "B().f() goes through M, but A().f() is the plain A."),
    D("class A { String f() => '$s1'; }\nmixin M { String f() => '$s2'; }\nclass B extends A with M {}\nclass C extends A {}\nvoid main() => print([B().f(), C().f()]);",
      lambda p: [p["s2"], p["s1"]], "Only B has the mixin; C keeps A's method."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => '$s2' + super.f(); }\nmixin N on A { String f() => '$s3' + super.f(); }\nclass X = A with M, N;\nclass Y = A with N, M;\nvoid main() => print(X().f() + Y().f());",
      lambda p: p["s3"] + p["s2"] + p["s1"] + p["s2"] + p["s3"] + p["s1"], "X reads N, M, A. Y reads M, N, A. The order in with is the order of the stack."),
    D("mixin M { int n = $a; }\nclass B with M {}\nvoid main() => print(B().n);", lambda p: p["a"], "A mixin can carry fields, and the class gets them."),
    D("mixin Count { int n = 0; void inc() => n++; }\nclass T with Count {}\nvoid main() {\n  var a = T(), b = T();\n  a.inc(); a.inc(); b.inc();\n  print('$${a.n}$${b.n}');\n}",
      "21", "Every object gets its own copy of the mixin's field."),
    D("mixin Log { String log = ''; void add(String s) => log += s; }\nclass T with Log {}\nvoid main() {\n  var t = T()..add('$s1')..add('$s2');\n  print(t.log);\n}",
      lambda p: p["s1"] + p["s2"], "Both calls add to the same object's log, in order."),
    D("mixin M { int get v => $a; }\nclass B with M {\n  int get v => 10;\n}\nvoid main() => print(B().v);", 10, "The class's getter overrides the mixin's getter."),
    D("mixin M {}\nclass B with M {}\nvoid main() => print(B() is M);", True, "A class that mixes in M is also an M."),
    D("mixin M {}\nclass A {}\nclass B extends A with M {}\nvoid main() => print(A() is M);", False, "Only B was given the mixin. A plain A is not an M."),
    D("mixin M {}\nclass A {}\nclass B extends A with M {}\nvoid main() => print(B() is A);", True, "B still extends A, so it is an A as well as an M."),
    D("mixin class M { String f() => '$s1'; }\nclass B with M {}\nvoid main() => print(M().f() + B().f());",
      lambda p: p["s1"] + p["s1"], "A mixin class can be used as a mixin and also made on its own."),
    D("mixin Greeter {\n  String name();\n  String hi() => 'hi ' + name();\n}\nclass P with Greeter {\n  String name() => '$w';\n}\nvoid main() => print(P().hi());",
      lambda p: "hi " + p["w"], "The mixin's hi calls name, and the class supplies it."),
    D("mixin Area {\n  int get w;\n  int get h;\n  int get area => w * h;\n}\nclass R with Area {\n  int get w => $a;\n  int get h => $b;\n}\nvoid main() => print(R().area);",
      lambda p: p["a"] * p["b"], "The mixin builds area from the getters the class fills in."),
    D("class A { String f() => '$s1'; }\nmixin M { String f() => '$s2'; }\nmixin N { String f() => '$s3'; }\nclass B = A with M, N;\nvoid main() => print(B().f());",
      lambda p: p["s3"], "class B = A with M, N is the same stack, and the last mixin wins."),
    D("mixin M { static String id() => '$s1'; }\nvoid main() => print(M.id());", lambda p: p["s1"], "A static member belongs to the mixin itself and is called on M."),
    D("mixin M { String toString() => '$s1'; }\nclass B with M {}\nvoid main() => print(B());", lambda p: p["s1"], "print uses toString, and the mixin supplies one."),
    D("mixin M { String toString() => '$s1'; }\nclass B with M {\n  String toString() => '$s2';\n}\nvoid main() => print(B());", lambda p: p["s2"], "The class's own toString is above the mixin's."),
    D("class A { String f() => '$s1'; }\nmixin M { String f() => '$s2'; }\nclass B extends A with M {\n  String f() => super.f() + '$s3';\n}\nvoid main() => print(B().f());",
      lambda p: p["s2"] + p["s3"], "super.f() in B reaches the mixin layer first, which does not go further down."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => super.f() + '$s2'; }\nclass B extends A with M {}\nvoid main() => print(B().f());",
      lambda p: p["s1"] + p["s2"], "M runs super.f() first and adds its tag after it."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => '<' + super.f() + '>'; }\nmixin N on A { String f() => '[' + super.f() + ']'; }\nclass B extends A with M, N {}\nvoid main() => print(B().f());",
      lambda p: "[<" + p["s1"] + ">]", "N is on top: it wraps what M gives, and M wraps what A gives."),
    D("class A { String f() => '$s1'; }\nmixin M on A { String f() => '<' + super.f() + '>'; }\nmixin N on A { String f() => '[' + super.f() + ']'; }\nclass B extends A with N, M {}\nvoid main() => print(B().f());",
      lambda p: "<[" + p["s1"] + "]>", "M is on top now: it wraps what N gives."),
    D("mixin M { String hi() => '$s1'; }\nclass A with M {}\nclass B extends A {}\nvoid main() => print(B().hi());", lambda p: p["s1"], "B inherits from A, and A has the mixin's method."),
    D("mixin M { String hi() => '$s1'; }\nclass A { String hi() => '$s2'; }\nclass B extends A with M {}\nclass C extends B {}\nvoid main() => print(C().hi());",
      lambda p: p["s1"], "C inherits from B, whose chain has M above A."),
    D("class A { String hi() => '$s1'; }\nmixin M { String hi() => '$s2'; }\nclass B extends A with M {}\nvoid main() {\n  A a = B();\n  print(a.hi());\n}",
      lambda p: p["s2"], "The object is a B with the mixin, whatever the variable's type says."),
    D("mixin M { int n = $a; void up() => n += $b; }\nclass T with M {}\nvoid main() {\n  var t = T();\n  t.up();\n  print(t.n);\n}",
      lambda p: p["a"] + p["b"], "The mixin's method changes the mixin's field on the same object."),
    D("mixin Walk { String go() => 'walk'; }\nmixin Swim { String go() => 'swim'; }\nclass Duck with Walk, Swim {}\nvoid main() => print(Duck().go());", "swim", "Swim is last in with, so it wins."),
    D("mixin Walk { String go() => 'walk'; }\nmixin Swim { String go() => 'swim'; }\nclass Duck with Swim, Walk {}\nvoid main() => print(Duck().go());", "walk", "Walk is last in with now, so it wins."),
    D("mixin Walk { String move() => 'walk'; }\nmixin Fly { String move() => 'fly'; }\nclass Bird with Walk, Fly {\n  String move() => 'hop';\n}\nvoid main() => print(Bird().move());", "hop", "A class's own method beats both mixins."),
    D("mixin Walk { String go() => 'walk'; }\nmixin Swim { String sink() => 'sink'; }\nclass Duck with Walk, Swim {}\nvoid main() => print(Duck().go() + ' ' + Duck().sink());", "walk sink", "The mixins have different methods, so the class has both."),
    D("mixin Named { String name = '$w'; }\nmixin Loud on Named { String shout() => name.toUpperCase(); }\nclass P with Named, Loud {}\nvoid main() => print(P().shout());",
      lambda p: to_upper(p["w"]), "Loud needs a Named under it, and Named comes first in with."),
]
