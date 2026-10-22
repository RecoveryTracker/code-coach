"""Classes and objects Pack, JavaScript side: the same eight activities with JavaScript's rules.

Class syntax, this, the constructor, getters and static members, extends and
super, instanceof, the prototype and object literals with methods. Every
answer is modelled by hand and tests/test_brain_packs.py runs every template
through the real node. The template writers (`T`, `YN`, `L`) are the ones the
Python side uses; JavaScript's own parts are only the spelling of the answer
(true/false/undefined) and of the oracle.

No template literals in a prompt (the shape tests keep a dollar sign out of
every prompt), so strings are joined with + and join().
"""

from __future__ import annotations

from ._classes_py import L, factory
from ._model import UNDEF, js_show, reverse, upper, yes_no_js

T, YN = factory(js_show, yes_no_js)

# A class body most templates start from: the constructor stores n.
JI = ("class $A {", "  constructor(n) { this.n = n; }")


def _fact(k: int) -> int:
    out = 1
    for i in range(2, k + 1):
        out *= i
    return out


def _find_over(xs: list[int], lim: int):
    for x in xs:
        if x > lim:
            return x
    return UNDEF


# ── 1. Attribute Value ──────────────────────────────────────────────────

JATTR = [
    T(L(*JI, "}", "const x = new $A($a);", "x.n;"), lambda p: p.a, "The constructor ran with n = $a and stored it in this.n."),
    T(L("class $A {", "  constructor(n = $a) { this.n = n; }", "}", "new $A().n;"), lambda p: p.a, "Nothing was passed, so n took its default, $a."),
    T(L("class $A {", "  constructor(n = $a) { this.n = n; }", "}", "new $A($b).n;"), lambda p: p.b, "The argument $b replaces the default."),
    T(L("class $A {", "  constructor(n, m) { this.n = n; this.m = m; }", "}", "new $A($a).m;"), UNDEF,
      "A missing argument is undefined, and that is what m stored."),
    T(L("class $A {", "  constructor(n) { this.n = n * 2; }", "}", "new $A($a).n;"), lambda p: p.a * 2, "The constructor stores n doubled."),
    T(L(*JI, "  up() { this.n++; }", "}", "const x = new $A($a);", "x.up();", "x.n;"), lambda p: p.a + 1, "up() adds 1 to this.n."),
    T(L(*JI, "  grow(k) { this.n += k; }", "}", "const x = new $A($a);", "x.grow($b);", "x.grow($c);", "x.n;"),
      lambda p: p.a + p.b + p.c, "Each grow adds to the same this.n: $a + $b + $c."),
    T(L(*JI, "  reset() { this.n = 0; }", "}", "const x = new $A($a);", "x.reset();", "x.n;"), 0, "reset() sets this.n to 0."),
    T(L(*JI, "}", "const x = new $A($a);", "x.n = $b;", "x.n;"), lambda p: p.b, "Assigning to x.n replaces the stored value."),
    T(L(*JI, "}", "const x = new $A($a);", 'x.tag = "$w";', "x.tag;"), lambda p: p.w, "An object can take a new property at any time."),
    T(L(*JI, "}", "const x = new $A($a);", "x.tag;"), UNDEF, "There is no tag property, so reading it gives undefined, not an error."),
    T(L("class $A {", "  constructor(w, h) { this.w = w; this.h = h; this.area = w * h; }", "}", "const r = new $A($a, $b);",
        "r.w = $c;", "r.area;"), lambda p: p.a * p.b, "area was worked out once in the constructor; changing w later does not update it."),
    T(L(*JI, "}", "const x = new $A($a);", "const y = x;", "y.n = $b;", "x.n;"), lambda p: p.b,
      "y is another name for the same object, so x.n changed too."),
    T(L(*JI, "}", "const x = new $A($a);", "const y = new $A($b);", "x.n += $c;", "y.n;"), lambda p: p.b,
      "Changing x does not touch y: they have separate properties."),
    T(L("class $A {", "  items = [];", "  add(x) { this.items.push(x); }", "}", "const x = new $A();", 'x.add("$w");', 'x.add("$v");',
        "x.items.length;"), 2, "Two adds, two items."),
    T(L("class $A {", "  items = [];", "  add(x) { this.items.push(x); }", "}", "const x = new $A();", 'x.add("$w");', 'x.add("$v");',
        "x.items.at(-1);"), lambda p: p.v, ".at(-1) is the item added last."),
    T(L(*JI, "  get twice() { return this.n * 2; }", "}", "const x = new $A($a);", "x.twice;"), lambda p: p.a * 2,
      "A getter is read like a property, but it runs the method."),
    T(L(*JI, "  get twice() { return this.n * 2; }", "}", "const x = new $A($a);", "x.n = $b;", "x.twice;"), lambda p: p.b * 2,
      "The getter runs each time, from the current n."),
    T(L(*JI, "  set double(v) { this.n = v * 2; }", "}", "const x = new $A($a);", "x.double = $b;", "x.n;"), lambda p: p.b * 2,
      "Assigning to x.double runs the setter, which stores twice $b in n."),
    T(L("class $A {", "  #n = $a;", "  up() { this.#n++; }", "  get n() { return this.#n; }", "}", "const x = new $A();", "x.up();", "x.n;"),
      lambda p: p.a + 1, "The private #n is changed by up() and read through the getter."),
    T(L("class $A {", "  #n = $a;", "}", "new $A().n;"), UNDEF, "#n is private: there is no public n, so the read is undefined."),
    T(L("const o = { n: $a, up() { this.n++; } };", "o.up();", "o.up();", "o.n;"), lambda p: p.a + 2, "Each o.up() adds 1 to o.n."),
    T(L("const n = $a;", "const o = { n };", "o.n;"), lambda p: p.a, "{ n } is short for { n: n }."),
    T(L("const { n, m } = { n: $a, m: $b };", "m;"), lambda p: p.b, "Destructuring pulls out the property named m."),
    T(L(*JI, "  add(k) { this.n += k; return this; }", "}", "new $A($a).add($b).add($c).n;"), lambda p: p.a + p.b + p.c,
      "add returns this, so the calls chain onto the same object."),
    T(L(*JI, "}", "const x = new $A($a);", "x.tag = $b;", "Object.keys(x).length;"), 2, "x has two own properties: n and tag."),
    T(L(*JI, "}", "const x = new $A($a);", '"n" in x;'), True, "n is a property of x."),
    T(L(*JI, "}", "const x = new $A($a);", "delete x.n;", "x.n;"), UNDEF, "delete removed the property, so reading it gives undefined."),
    T(L(*JI, "  static make() { return new $A($a); }", "}", "$A.make().n;"), lambda p: p.a, "make() builds an object with n = $a."),
    T(L(*JI, "}", "const x = new $A($a);", "Object.assign({}, x).n;"), lambda p: p.a, "Object.assign copies x's own properties into a new object."),
    T(L(*JI, "}", "const x = new $A($a);", "({ ...x, n: $b }).n;"), lambda p: p.b, "The spread copies n, then n: $b replaces it."),
    T(L(*JI, "}", "class $B extends $A {}", "new $B($a).n;"), lambda p: p.a, "$B inherits the constructor from $A."),
    T(L(*JI, "}", "class $B extends $A {", "  constructor(n) { super(n); this.m = n + 1; }", "}", "new $B($a).m;"), lambda p: p.a + 1,
      "m is one more than n."),
    T(L("class $A {", "  constructor(n) { this.n = Math.max(n, 0); }", "}", "new $A(-$a).n;"), 0, "Math.max(-$a, 0) is 0."),
    T(L("class $A {", "  constructor(n) { this.n = Math.min(n, $b); }", "}", "new $A($a).n;"), lambda p: min(p.a, p.b),
      "Math.min keeps the smaller of $a and $b."),
    T(L("class $A {", "  constructor(n) { this.big = n > 5; }", "}", "new $A($a).big;"), lambda p: p.a > 5, "$a > 5 is stored as a boolean."),
    T(L("class $A {", "  constructor(items) { this.items = items; }", "}", "const src = [$a, $b];", "const x = new $A(src);", "src.push($c);",
        "x.items.length;"), 3, "x.items is the very array src, so the push shows."),
    T(L("class $A {", "  constructor(items) { this.items = [...items]; }", "}", "const src = [$a, $b];", "const x = new $A(src);", "src.push($c);",
        "x.items.length;"), 2, "The spread made a copy, so the push is not seen."),
    T(L("class $A {", "  constructor(name) { this.name = name.toUpperCase(); }", "}", 'new $A("$w").name;'), lambda p: upper(p.w),
      "The constructor stores the name in capitals."),
    T(L("class $A {", "  constructor(name) { this.name = name; }", "}", 'new $A("$w").name[0];'), lambda p: p.w[0], "[0] is the first character."),
    T(L("class $A {", "  constructor(name) { this.name = name; }", "}", 'new $A("$w").name.length;'), lambda p: len(p.w), "length counts the characters."),
    T(L(*JI, "}", "JSON.stringify(new $A($a));"), lambda p: '{"n":' + str(p.a) + "}", "JSON.stringify writes the own properties."),
    T(L(*JI, "  get twice() { return this.n * 2; }", "}", "JSON.stringify(new $A($a));"), lambda p: '{"n":' + str(p.a) + "}",
      "A getter lives on the prototype, not on the object, so JSON leaves it out."),
]

# ── 2. Method Returns ───────────────────────────────────────────────────

JSTACK = ("class $A {", "  items = [$a, $b, $c];", "  pop() { return this.items.pop(); }")

JMETH = [
    T(L(*JI, "  add(k) { return this.n + k; }", "}", "const x = new $A($a);", "x.add($b);"), lambda p: p.a + p.b, "add returns n + k: $a + $b."),
    T(L(*JI, "  add(k) { return this.n + k; }", "}", "const x = new $A($a);", "x.add($c);", "x.add($b);"), lambda p: p.a + p.b,
      "add never changes this.n, so the second call starts from $a again."),
    T(L(*JI, "  add(k) { this.n += k; return this.n; }", "}", "const x = new $A($a);", "x.add($b);", "x.add($b);"), lambda p: p.a + 2 * p.b,
      "This add changes this.n, so the second call builds on the first."),
    T(L(*JI, "  up() { this.n++; }", "}", "const x = new $A($a);", "x.up();"), UNDEF, "up() has no return, so the call gives undefined."),
    T(L(*JSTACK, "}", "new $A().pop();"), lambda p: p.c, "pop takes off the last item, $c."),
    T(L(*JSTACK, "}", "const x = new $A();", "x.pop();", "x.pop();"), lambda p: p.b, "The first pop removed $c; the second gives $b."),
    T(L("class $A {", "  items = [$a, $b, $c];", "  take() { return this.items.shift(); }", "}", "new $A().take();"), lambda p: p.a,
      "shift takes from the front."),
    T(L("class $A {", "  items = [$a, $b, $c];", "  peek() { return this.items.at(-1); }", "}", "const x = new $A();", "x.items.pop();", "x.peek();"),
      lambda p: p.b, "peek only looks at the last item, which is $b once $c is gone."),
    T(L(*JSTACK, "}", "const x = new $A();", "x.pop();", "x.items.length;"), 2, "One item was taken off the three."),
    T(L(*JI, "  twice() { return this.n * 2; }", "  quad() { return this.twice() * 2; }", "}", "new $A($a).quad();"), lambda p: p.a * 4,
      "quad calls twice(), then doubles again."),
    T(L(*JI, "  inc(k = 1) { this.n += k; return this.n; }", "}", "new $A($a).inc();"), lambda p: p.a + 1, "k defaults to 1."),
    T(L(*JI, "  inc(k = 1) { this.n += k; return this.n; }", "}", "const x = new $A($a);", "x.inc();", "x.inc($b);"), lambda p: p.a + 1 + p.b,
      "The first call adds 1 and the second adds $b."),
    T(L("class $A {", "  constructor(name) { this.name = name; }", '  hi() { return this.name + "!"; }', "}", 'new $A("$w").hi();'),
      lambda p: p.w + "!", "hi joins a ! on the name."),
    T(L("class $A {", "  constructor(name, n) { this.name = name; this.n = n; }", "  tag() { return this.name + this.n; }", "}",
        'new $A("$w", $a).tag();'), lambda p: p.w + str(p.a), "A string + a number joins them into a string."),
    T(L("class $A {", "  constructor(name, n) { this.name = name; this.n = n; }", "  tag() { return this.n + this.name; }", "}",
        'new $A("$w", $a).tag();'), lambda p: str(p.a) + p.w, "A number + a string also joins them: the number is turned into text."),
    T(L(*JI, "  big() { return this.n > $b; }", "}", "new $A($a).big();"), lambda p: p.a > p.b, "$a > $b is the answer."),
    T(L(*JI, "  older(o) { return this.n > o.n; }", "}", "new $A($a).older(new $A($b));"), lambda p: p.a > p.b,
      "The method compares its own n with the other object's n."),
    T(L(*JI, "  gap(o) { return Math.abs(this.n - o.n); }", "}", "new $A($a).gap(new $A($b));"), lambda p: abs(p.a - p.b),
      "Math.abs drops the sign of $a - $b."),
    T(L("class $A {", "  constructor(items) { this.items = items; }", "  total() { return this.items.reduce((s, x) => s + x, 0); }", "}",
        "new $A([$a, $b, $c]).total();"), lambda p: p.a + p.b + p.c, "reduce adds the items up from 0."),
    T(L("class $A {", "  constructor(items) { this.items = items; }", "  many() { return this.items.filter(x => x > $b).length; }", "}",
        "new $A([$a, $c, $d]).many();"), lambda p: len([x for x in (p.a, p.c, p.d) if x > p.b]), "Count the items bigger than $b."),
    T(L(*JI, "  get() { return this.n; }", "  set(k) { this.n = k; return this; }", "}", "new $A($a).set($b).get();"), lambda p: p.b,
      "set returns this, so .get() asks the same object."),
    T(L("class $A {", "  static double(x) { return x * 2; }", "}", "$A.double($a);"), lambda p: p.a * 2, "A static method is called on the class."),
    T(L(*JI, "  static double(x) { return x * 2; }", "}", "typeof new $A($a).double;"), "undefined",
      "A static method belongs to the class; an object does not have it."),
    T(L(*JI, "  valueOf() { return this.n; }", "}", "new $A($a) + 1;"), lambda p: p.a + 1, "+ asks the object for valueOf(), which is the number n."),
    T(L(*JI, "  valueOf() { return this.n; }", "}", "new $A($a) * $b;"), lambda p: p.a * p.b, "* turns the object into a number with valueOf()."),
    T(L("class $A {", "  items = [$a, $b, $c];", "  *[Symbol.iterator]() { yield* this.items; }", "}", "[...new $A()].length;"), 3,
      "The spread loops over the object through its iterator."),
    T(L("class $A {", "  items = [$a, $b, $c];", "  *[Symbol.iterator]() { yield* this.items; }", "}", "Math.max(...new $A());"),
      lambda p: max(p.a, p.b, p.c), "The spread hands each item to Math.max."),
    T(L("class $A {", "  constructor(x, y) { this.x = x; this.y = y; }", "  pair() { return [this.x, this.y]; }", "}",
        "const [p, q] = new $A($a, $b).pair();", "q;"), lambda p: p.b, "pair gives back an array, and q takes its second item."),
    T(L(*JI, "  doubled() { return new $A(this.n * 2); }", "}", "new $A($a).doubled().n;"), lambda p: p.a * 2, "doubled returns a new object holding twice n."),
    T(L(*JI, "  doubled() { return new $A(this.n * 2); }", "}", "const x = new $A($a);", "x.doubled();", "x.n;"), lambda p: p.a,
      "doubled builds a new object and leaves x alone."),
    T(L("class $A {", "  fact(k) { return k <= 1 ? 1 : k * this.fact(k - 1); }", "}", "new $A().fact($a);"), lambda p: _fact(p.a),
      "k * (k-1) * ... * 1 for k = $a."),
    T(L(*JI, "  total(...xs) { return this.n + xs.reduce((s, x) => s + x, 0); }", "}", "new $A($a).total($b, $c);"), lambda p: p.a + p.b + p.c,
      "...xs gathers the extra arguments into an array."),
    T(L(*JI, "  scale({ k = 1 } = {}) { return this.n * k; }", "}", "new $A($a).scale({ k: $b });"), lambda p: p.a * p.b, "k comes out of the object that was passed."),
    T(L("class $A {", "  constructor(name) { this.name = name; }", "  loud() { return this.name.toUpperCase(); }", "}", 'new $A("$w").loud();'),
      lambda p: upper(p.w), "toUpperCase() gives capitals."),
    T(L(*JI, "  get() { return this.n; }", "}", "const x = new $A($a);", "x.get() * 2 + x.get();"), lambda p: p.a * 3, "Each call gives $a: $a * 2 + $a."),
    T(L("class $A {", "  items = [$a, $b, $c];", "  firstOver(lim) { return this.items.find(i => i > lim); }", "}", "new $A().firstOver($d);"),
      lambda p: _find_over([p.a, p.b, p.c], p.d), "find gives the first item over $d, or undefined when none is."),
    T(L("class $A {", "  items = [$a, $b];", "  has(k) { return this.items.includes(k); }", "}", "new $A().has($c);"), False, "$c is not in the array."),
    T(L(*JI, "  equals(o) { return this.n === o.n; }", "}", "new $A($a).equals(new $A($a));"), True, "The two n values are both $a."),
    T(L(*JI, "  even() { return this.n % 2 === 0; }", "}", "new $A($a).even();"), lambda p: p.a % 2 == 0, "$a % 2 is the remainder after halving."),
    T(L("class $A {", "  constructor(...parts) { this.parts = parts; }", '  path() { return this.parts.join("-"); }', "}", 'new $A("$w", "$v").path();'),
      lambda p: p.w + "-" + p.v, "join puts the - between the parts."),
    T(L(*JI, "  get() { return this.n; }", "}", "const x = new $A($a);", "x.get.call({ n: $b });"), lambda p: p.b,
      "call runs the method with this set to the object we pass: { n: $b }."),
    T(L(*JI, "  get() { return this.n; }", "}", "const x = new $A($a);", "const f = x.get.bind({ n: $b });", "f();"), lambda p: p.b,
      "bind fixed this to { n: $b }, so x is not used."),
    T(L(*JI, "  later() { return [1].map(() => this.n)[0]; }", "}", "new $A($a).later();"), lambda p: p.a,
      "An arrow function keeps the this of the method around it."),
]

# ── 3. Class or Instance ────────────────────────────────────────────────

PROTO = ("class $A {}", "$A.prototype.n = $a;", "const x = new $A();")

JSHARED = [
    T(L("class $A { static n = $a; }", "$A.n;"), lambda p: p.a, "A static property lives on the class itself."),
    T(L("class $A { static n = $a; }", "new $A().n;"), UNDEF, "A static property is not on the objects: reading it gives undefined."),
    T(L("class $A { static n = $a; }", "const x = new $A();", "x.constructor.n;"), lambda p: p.a, "x.constructor is the class, so its static n is reachable that way."),
    T(L("class $A {}", "$A.prototype.n = $a;", "new $A().n;"), lambda p: p.a, "The object has no n, so the lookup goes on to the prototype: $a."),
    T(L(*PROTO, "x.n = $b;", "$A.prototype.n;"), lambda p: p.a, "x.n = $b made an own property on x; the prototype still says $a."),
    T(L(*PROTO, "const y = new $A();", "x.n = $b;", "y.n;"), lambda p: p.a, "Only x got its own n; y still reads the prototype's $a."),
    T(L(*PROTO, "$A.prototype.n = $b;", "x.n;"), lambda p: p.b, "x has no n of its own, so it reads the prototype's, now $b."),
    T(L(*PROTO, "x.n = $b;", "$A.prototype.n = $c;", "x.n;"), lambda p: p.b, "x's own n hides the prototype's, whatever the prototype says."),
    T(L(*PROTO, "x.n += $b;", "$A.prototype.n;"), lambda p: p.a, "x.n += $b reads the prototype's $a but writes a new n onto x."),
    T(L(*PROTO, "x.n += $b;", "x.n;"), lambda p: p.a + p.b, "It read $a from the prototype, added $b, and stored the sum on x."),
    T(L("class $A {}", "$A.prototype.items = [];", "const x = new $A();", "const y = new $A();", "x.items.push($a);", "y.items.length;"), 1,
      "items is on the prototype, so x and y share one array."),
    T(L("class $A { items = []; }", "const x = new $A();", "const y = new $A();", "x.items.push($a);", "y.items.length;"), 0,
      "A class field makes a fresh array for each object."),
    T(L("class $A {", "  static count = 0;", "  constructor() { $A.count++; }", "}", "new $A();", "new $A();", "new $A();", "$A.count;"), 3,
      "Every new object bumps the one count on the class."),
    T(L("class $A {", "  static count = 0;", "  constructor() { this.count++; }", "}", "new $A();", "new $A();", "$A.count;"), 0,
      "this.count is not the static one; the class's count never moves."),
    T(L("class $A {", "  static count = 0;", "  constructor() { this.constructor.count++; }", "}", "new $A();", "new $A();", "$A.count;"), 2,
      "this.constructor is the class, so both objects bumped the static count."),
    T(L("class $A { n = $a; }", "const x = new $A();", "const y = new $A();", "x.n = $b;", "y.n;"), lambda p: p.a, "A field is made for each object, so y's n is its own."),
    T(L(*PROTO, 'x.hasOwnProperty("n");'), False, "n is on the prototype, not on x itself."),
    T(L(*PROTO, "x.n = $b;", 'x.hasOwnProperty("n");'), True, "The assignment created an own property."),
    T(L(*PROTO, '"n" in x;'), True, "in looks through the prototypes too."),
    T(L(*PROTO, "Object.keys(x).length;"), 0, "Object.keys lists only own properties."),
    T(L(*PROTO, "x.n = $b;", "delete x.n;", "x.n;"), lambda p: p.a, "Deleting x's own n uncovers the prototype's $a again."),
    T(L("class $A { static n = $a; }", "class $B extends $A {}", "$B.n;"), lambda p: p.a, "Static members are inherited: $B finds $A's n."),
    T(L("class $A { static n = $a; }", "class $B extends $A {}", "$B.n = $c;", "$A.n;"), lambda p: p.a, "Assigning on $B gives $B its own n; $A is unchanged."),
    T(L("class $A { static n = $a; }", "class $B extends $A {}", "$A.n = $b;", "$B.n;"), lambda p: p.b, "$B reads through to $A, which now says $b."),
    T(L("class $A {", "  static n = $a;", "  static f() { return this.n; }", "}", "class $B extends $A { static n = $b; }", "$B.f();"), lambda p: p.b,
      "In a static method, this is the class it was called on: $B."),
    T(L("class $A {", "  static nxt = $a;", "  constructor() { this.id = $A.nxt++; }", "}", "const x = new $A();", "const y = new $A();", "y.id;"), lambda p: p.a + 1,
      "x took $a and moved the counter on, so y took the next number."),
    T(L("class $A {", "  static nxt = $a;", "  constructor() { this.id = $A.nxt++; }", "}", "const x = new $A();", "const y = new $A();", "x.id;"), lambda p: p.a,
      "x was first: it took the counter's starting value."),
    T(L("class $A {", "  total() { return this.n * 2; }", "}", "$A.prototype.n = $a;", "const x = new $A();", "x.n = $b;", "x.total();"), lambda p: p.b * 2,
      "this.n finds x's own n first."),
    T(L("class $A {", "  total() { return this.n * 2; }", "}", "$A.prototype.n = $a;", "const x = new $A();", "const y = new $A();", "x.n = $b;", "y.total();"),
      lambda p: p.a * 2, "y has no n of its own: it uses the prototype's $a."),
    T(L("const x = Object.create({ n: $a });", "x.n;"), lambda p: p.a, "Object.create makes x with that object as its prototype."),
    T(L("const x = Object.create({ n: $a });", "x.n = $b;", "Object.getPrototypeOf(x).n;"), lambda p: p.a, "x.n = $b wrote onto x; the prototype object is unchanged."),
    T(L("const base = { reg: {} };", "const x = Object.create(base);", "const y = Object.create(base);", "x.reg.k = $a;", "y.reg.k;"), lambda p: p.a,
      "reg is one object on the prototype, seen by x and y alike."),
    T(L("const base = { reg: {} };", "const x = Object.create(base);", "const y = Object.create(base);", "x.reg = {};", "x.reg.k = $a;", "y.reg.k;"), UNDEF,
      "x.reg = {} gave x its own object, so y finds the prototype's empty one."),
    T(L("class $A {}", "$A.prototype.items = [];", "const x = new $A();", "x.items = [...x.items, $a];", "$A.prototype.items.length;"), 0,
      "The spread built a new array, stored on x; the prototype's is still empty."),
    T(L("class $A {", "  static n = $a;", "  n = $b;", "}", "$A.n + new $A().n;"), lambda p: p.a + p.b, "The static n is on the class ($a); the field n is on each object ($b)."),
    T(L("class $A { f() { return $a; } }", "const x = new $A();", "x.f = () => $b;", "x.f();"), lambda p: p.b, "x's own f hides the one on the prototype."),
    T(L("class $A { f() { return $a; } }", "const x = new $A();", "x.f = () => $b;", "new $A().f();"), lambda p: p.a, "Only x was changed; a fresh object still uses the class's f."),
]

# ── 4. Inherit It ───────────────────────────────────────────────────────

JHI = ("class $A {", '  hi() { return "$w"; }', "}")

JINHERIT = [
    T(L(*JHI, "class $B extends $A {}", "new $B().hi();"), lambda p: p.w, "$B has no hi, so it runs $A's."),
    T(L(*JHI, "class $B extends $A {", '  hi() { return "$v"; }', "}", "new $B().hi();"), lambda p: p.v, "$B's own hi overrides $A's."),
    T(L(*JHI, "class $B extends $A {", '  hi() { return "$v"; }', "}", "new $A().hi();"), lambda p: p.w, "$A is the parent: it never sees $B's version."),
    T(L(*JHI, "class $B extends $A {", '  hi() { return super.hi() + "!"; }', "}", "new $B().hi();"), lambda p: p.w + "!", "super.hi() runs $A's hi, then ! is joined on."),
    T(L(*JHI, "class $B extends $A {", '  hi() { return "$v" + super.hi(); }', "}", "new $B().hi();"), lambda p: p.v + p.w, "$v first, then what $A's hi gives."),
    T(L(*JHI, "class $B extends $A {}", "class $C extends $B {", '  hi() { return super.hi() + "!"; }', "}", "new $C().hi();"), lambda p: p.w + "!",
      "super.hi() inside $C goes up: $B has none, so $A's."),
    T(L("class $A { f() { return 'a'; } }", "class $B extends $A { f() { return super.f() + 'b'; } }", "class $C extends $B { f() { return super.f() + 'c'; } }",
        "new $C().f();"), "abc", "Each f runs its parent's first, then adds its own letter."),
    T(L(*JI, "}", "class $B extends $A {", "  constructor(n) { super(n + $b); }", "}", "new $B($a).n;"), lambda p: p.a + p.b, "$B passes n + $b up, and $A stores it."),
    T(L(*JI, "}", "class $B extends $A {", "  constructor(n) { super(n); this.n *= 2; }", "}", "new $B($a).n;"), lambda p: p.a * 2, "$A stored n, then $B doubled it."),
    T(L(*JI, "}", "class $B extends $A {", "  double() { return this.n * 2; }", "}", "new $B($a).double();"), lambda p: p.a * 2,
      "$B inherits the constructor, so n is set; double uses it."),
    T(L("class $A {", '  run() { return this.name() + "!"; }', '  name() { return "$w"; }', "}", "class $B extends $A {", '  name() { return "$v"; }', "}",
        "new $B().run();"), lambda p: p.v + "!", "run is $A's, but this.name() finds $B's override."),
    T(L("class $A {", "  total() { return this.base() + 1; }", "  base() { return 1; }", "}", "class $B extends $A {", "  base() { return $b; }", "}",
        "new $B().total();"), lambda p: p.b + 1, "total calls this.base(), and this is a $B."),
    T(L("class $A {", "  run() { return this.step() + this.step(); }", "  step() { return 1; }", "}", "class $B extends $A {", "  step() { return $a; }", "}",
        "new $B().run();"), lambda p: p.a * 2, "Both calls go to $B's step."),
    T(L("class $A {", '  static make() { return "$w"; }', "}", "class $B extends $A {}", "$B.make();"), lambda p: p.w, "Static methods are inherited too."),
    T(L("class $A {", '  static make() { return "$w"; }', "}", "class $B extends $A {", '  static make() { return super.make() + "!"; }', "}", "$B.make();"),
      lambda p: p.w + "!", "super.make() in a static method reaches $A's static make."),
    T(L("class $A {}", "class $B extends $A {}", "Object.getPrototypeOf($B) === $A;"), True, "A subclass's own prototype is its parent class."),
    T(L("class $A { hi() {} }", "class $B extends $A {}", "$B.prototype.hi === $A.prototype.hi;"), True, "$B has no hi of its own, so it finds $A's."),
    T(L("class $A { hi() {} }", "class $B extends $A { hi() {} }", "$B.prototype.hi === $A.prototype.hi;"), False, "$B defined its own hi: two different functions."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "  get twice() { return this.n * 2; }", "}", "class $B extends $A {}", "new $B($a).twice;"), lambda p: p.a * 2,
      "Getters are inherited like methods."),
    T(L("class $A {", "  get v() { return $a; }", "}", "class $B extends $A {", "  get v() { return super.v + $b; }", "}", "new $B().v;"), lambda p: p.a + p.b,
      "super.v reads the parent's getter."),
    T(L("class $A {", "  who() { return this.constructor.name; }", "}", "class $B extends $A {}", "new $B().who();"), lambda p: p.B,
      "this.constructor is the object's own class: $B."),
    T(L("class $A {", '  who() { return "$A"; }', "}", "class $B extends $A {}", "new $B().who();"), lambda p: p.A, "who is inherited and returns a fixed word."),
    T(L('class $A { kind = "$w"; }', 'class $B extends $A { kind = "$v"; }', "new $B().kind;"), lambda p: p.v, "$B's field is set after $A's, so $B's value wins."),
    T(L("class $A {", "  constructor() { this.v = this.init(); }", "  init() { return $a; }", "}", "class $B extends $A {", "  init() { return $b; }", "}", "new $B().v;"),
      lambda p: p.b, "this.init() in $A's constructor finds $B's override."),
    T(L("class $A {", "  constructor() { this.k = this.f(); }", '  f() { return "$w"; }', "}", "class $B extends $A {", '  x = "$v";', "  f() { return this.x; }", "}",
        "new $B().k;"), UNDEF, "$A's constructor ran before $B's field x was set, so this.x was still undefined."),
    T(L("class $A {}", "class $B extends $A {}", 'Object.assign($B.prototype, { hi() { return "$w"; } });', "new $B().hi();"), lambda p: p.w,
      "Object.assign added a method to $B's prototype."),
    T(L("class $A extends Array {", "  top() { return this[this.length - 1]; }", "}", "const s = new $A();", "s.push($a);", "s.push($b);", "s.top();"), lambda p: p.b,
      "A subclass of Array is an array, with top() added."),
    T(L("class $A extends Error {}", 'new $A("$w").message;'), lambda p: p.w, "Error's constructor stores the message."),
    T(L("class $A extends Error {}", 'new $A("$w") instanceof Error;'), True, "A subclass of Error is an Error."),
    T(L(*JHI, "class $B extends $A {", '  hi() { return "$v"; }', "}", "$A.prototype.hi.call(new $B());"), lambda p: p.w,
      "The call runs $A's function directly, whatever the object is."),
    T(L("class $A { cost() { return $a; } }", "class $B extends $A { cost() { return super.cost() + $b; } }",
        "class $C extends $B { cost() { return super.cost() + $c; } }", "new $C().cost();"), lambda p: p.a + p.b + p.c, "Each level adds its own number to its parent's."),
    T(L(*JHI, "class $B extends $A {", '  later() { return [1].map(() => super.hi())[0]; }', "}", "new $B().later();"), lambda p: p.w,
      "An arrow function keeps super of the method around it."),
    T(L("class $A {", "  constructor() { this.n = $a; }", "}", "class $B extends $A {}", "new $B().n;"), lambda p: p.a, "$B has no constructor of its own, so $A's runs."),
    T(L("class $A {", "  constructor(n = $a) { this.n = n; }", "}", "class $B extends $A {", "  constructor() { super(); }", "}", "new $B().n;"), lambda p: p.a,
      "super() passes nothing, so n takes its default."),
]

# ── 5. Is It ────────────────────────────────────────────────────────────

JH2 = ("class $A {}", "class $B extends $A {}", "const x = new $B();")
JH3 = ("class $A {}", "class $B extends $A {}", "class $C extends $A {}")
JHASN = ("class $A {", "  constructor(n) { this.n = n; }", "  hi() {}", "}", "const x = new $A($a);")

JISA = [
    YN(L(*JH2, "x instanceof $B;"), True, "x was made by new $B()."),
    YN(L(*JH2, "x instanceof $A;"), True, "A $B is also a $A, because $B extends $A."),
    YN(L(*JH2[:2], "new $A() instanceof $B;"), False, "A plain $A is not a $B: the parent is not an instance of its child."),
    YN(L(*JH2[:2], "$B.prototype instanceof $A;"), True, "$B's prototype object inherits from $A's."),
    YN(L(*JH2, "$A.prototype.isPrototypeOf(x);"), True, "$A's prototype is somewhere up x's chain."),
    YN(L(*JH2, "x instanceof Object;"), True, "Every object is an instance of Object."),
    YN("[] instanceof Array;", True, "[] is an array."),
    YN("[] instanceof Object;", True, "An array is an object too."),
    YN("null instanceof Object;", False, "null is not an object at all."),
    YN("$a instanceof Number;", False, "A plain number is not an object, so instanceof says no."),
    YN('"$w" instanceof String;', False, "A plain string is not an object, so instanceof says no."),
    YN('new String("$w") instanceof String;', True, "new String makes a String object."),
    YN(L(*JH2, 'typeof x === "object";'), True, "typeof an object is the word object."),
    YN(L("class $A {}", 'typeof $A === "function";'), True, "A class is a function underneath."),
    YN('typeof null === "object";', True, "typeof null is object: an old mistake in the language."),
    YN("Array.isArray([$a]);", True, "Square brackets make an array."),
    YN("Array.isArray({});", False, "Curly brackets make a plain object."),
    YN(L(*JH2, "x.constructor === $B;"), True, "x.constructor is the class that made it."),
    YN(L(*JH2, "x.constructor === $A;"), False, "x.constructor is $B, not its parent."),
    YN(L(*JHASN, '"n" in x;'), True, "The constructor set n."),
    YN(L(*JHASN, 'x.hasOwnProperty("n");'), True, "n was set on x itself."),
    YN(L(*JHASN, 'x.hasOwnProperty("hi");'), False, "hi is a method: it lives on the prototype, not on x."),
    YN(L(*JHASN, '"hi" in x;'), True, "in looks up the prototype chain too."),
    YN(L(*JHASN, 'typeof x.hi === "function";'), True, "A method is a function."),
    YN(L(*JHASN, 'typeof x.n === "function";'), False, "n is a number."),
    YN(L(*JH2, "Object.getPrototypeOf(x) === $B.prototype;"), True, "x's prototype is $B's prototype object."),
    YN(L(*JH2[:2], "Object.getPrototypeOf($B) === $A;"), True, "A subclass's own prototype is its parent class."),
    YN(L(*JH3, "new $B() instanceof $C;"), False, "$B and $C are siblings: neither is the other."),
    YN(L("class $A {}", "({}) instanceof $A;"), False, "A plain object was not made by $A."),
    YN(L("class $A {}", "Object.create($A.prototype) instanceof $A;"), True, "Its prototype chain includes $A's prototype."),
    YN("(() => 1) instanceof Function;", True, "An arrow function is a Function."),
    YN(L("class $A {}", "$A instanceof Function;"), True, "A class is a Function object."),
    YN(L(*JH2, "x instanceof Array;"), False, "x is not an array."),
    YN(L("class $A extends Error {}", "new $A() instanceof Error;"), True, "$A extends Error."),
    YN(L(*JHASN, 'typeof x.nope === "undefined";'), True, "A missing property is undefined."),
    YN(L(*JH2, '"toString" in x;'), True, "Every object inherits toString from Object."),
    YN(L(*JH2, 'x.hasOwnProperty("toString");'), False, "toString is inherited, not x's own."),
    YN(L(*JH3, "const x = new $B();", "x instanceof $A && !(x instanceof $C);"), True, "x is a $A, and $C is a sibling of $B."),
    YN("[$a] instanceof Object;", True, "An array is an object."),
    YN('typeof [] === "array";', False, "typeof [] is object: there is no array answer."),
    YN('typeof "$w" === "string";', True, "Text has typeof string."),
]

# ── 6. Same Object ──────────────────────────────────────────────────────

JPLAIN = ("class $A {}", "const x = new $A();")
JN = ("class $A {", "  constructor(n) { this.n = n; }", "}")

JSAME = [
    YN(L(*JPLAIN, "const y = x;", "x === y;"), True, "y = x gave the same object a second name."),
    YN(L(*JPLAIN, "const y = new $A();", "x === y;"), False, "Two calls to new, two separate objects."),
    YN(L(*JPLAIN, "const y = new $A();", "x == y;"), False, "Even == compares objects by identity, and these are two."),
    YN(L(*JPLAIN, "x === x;"), True, "An object is the same as itself."),
    YN(L(*JPLAIN, "const y = x;", "x == y;"), True, "The same object, so equal."),
    YN(L(*JN, "const x = new $A($a);", "({ ...x }) === x;"), False, "The spread builds a new object."),
    YN(L(*JN, "const x = new $A($a);", "({ ...x }).n === x.n;"), True, "The copy has the same n value."),
    YN(L(*JN, "JSON.stringify(new $A($a)) === JSON.stringify(new $A($a));"), True, "Both write as the same text."),
    YN(L(*JN, "new $A($a) === new $A($a);"), False, "Two calls, two objects, whatever they hold."),
    YN(L(*JPLAIN, "[x].includes(x);"), True, "includes finds the very same object."),
    YN(L(*JPLAIN, "[x].includes(new $A());"), False, "A new object is not the one in the array."),
    YN(L(*JPLAIN, "new Set([x]).has(x);"), True, "The set holds x itself."),
    YN(L(*JPLAIN, "const y = new $A();", "new Set([x]).has(y);"), False, "y is a different object."),
    YN(L(*JPLAIN, "[x] === [x];"), False, "Each [x] is a new array, and arrays are compared by identity."),
    YN("({ a: 1 }) === ({ a: 1 });", False, "Two object literals are two objects."),
    YN(L("class $A {", "  me() { return this; }", "}", "const x = new $A();", "x.me() === x;"), True, "me() returns the object itself."),
    YN(L("class $A {", "  dup() { return new $A(); }", "}", "const x = new $A();", "x.dup() === x;"), False, "dup() builds a new object."),
    YN(L(*JPLAIN, "const y = new $A();", "x.constructor === y.constructor;"), True, "Both were made by $A."),
    YN(L(*JPLAIN, "const y = x;", "Object.is(x, y);"), True, "Object.is says the same object, yes."),
    YN(L("class $A {}", "$A.prototype.items = [];", "const x = new $A();", "const y = new $A();", "x.items === y.items;"), True, "items is one array on the prototype."),
    YN(L("class $A { items = []; }", "const x = new $A();", "const y = new $A();", "x.items === y.items;"), False, "A field makes an array for each object."),
    YN(L("class $A {}", "const x = new $A();", "x.part = [$a];", "({ ...x }).part === x.part;"), True, "The spread is shallow: the array inside is shared."),
    YN(L("class $A {}", "const x = new $A();", "x.part = [$a];", "JSON.parse(JSON.stringify(x)).part === x.part;"), False, "A trip through JSON builds everything new."),
    YN(L("class $A {", "  constructor(n) { this.n = n; }", "  valueOf() { return this.n; }", "}", "new $A($a) == $a;"), True, "== turns the object into a number with valueOf()."),
    YN(L("class $A {", "  constructor(n) { this.n = n; }", "  valueOf() { return this.n; }", "}", "new $A($a) === $a;"), False, "=== does no conversion: an object is not a number."),
    YN(L("class $A {", "  constructor(n) { this.n = n; }", "  valueOf() { return this.n; }", "}", "new $A($a) > new $A($b);"), lambda p: p.a > p.b,
       "> compares the valueOf() numbers: $a and $b."),
    YN(L("class $A {", "  constructor(name) { this.name = name; }", "  toString() { return this.name; }", "}", 'new $A("$w") == "$w";'), True,
       "== turns the object into text with toString()."),
    YN(L(*JPLAIN, 'x == "[object Object]";'), True, "The default toString of a plain object gives [object Object]."),
    YN(L(*JN, "new $A($a).n === new $A($a).n;"), True, "Equal numbers are equal."),
    YN(L("class $A {", "  constructor(name) { this.name = name; }", "}", 'new $A("$w").name === new $A("$w").name;'), True, "Strings are compared by value."),
    YN('new String("$w") === new String("$w");', False, "Two String objects are two objects."),
    YN('new String("$w") == "$w";', True, "== turns the String object into text first."),
    YN(L(*JPLAIN, "const a = [x, x];", "a[0] === a[1];"), True, "The same object twice."),
    YN(L("class $A {}", "const a = Array(2).fill(new $A());", "a[0] === a[1];"), True, "fill puts the one object in every slot."),
    YN(L("class $A {}", "const a = Array.from({ length: 2 }, () => new $A());", "a[0] === a[1];"), False, "The function runs twice and makes two objects."),
    YN(L(*JN, "function f(o) { o.n = $b; }", "const x = new $A($a);", "f(x);", "x.n === $b;"), True, "f changed the object it was handed."),
    YN(L(*JN, "function f(o) { o = new $A($b); }", "const x = new $A($a);", "f(x);", "x.n === $b;"), False, "f only rebound its own o."),
    YN(L(*JPLAIN, "const y = new $A();", "x !== y;"), True, "They are two objects."),
    YN(L(*JN, "const x = new $A($a);", "Object.assign({}, x) === x;"), False, "Object.assign built a new object."),
    YN(L(*JPLAIN, "x.valueOf() === x;"), True, "The default valueOf returns the object itself."),
    YN(L(*JPLAIN, "const y = new $A();", "[x, y].indexOf(y) === 1;"), True, "indexOf finds y itself in second place."),
    YN(L("class $A {", "  me() { return this; }", "}", "const x = new $A();", "x.me().me() === x;"), True, "Each me() returns the same object."),
]

# ── 7. Counter Class ────────────────────────────────────────────────────

JC0 = ("class $A { n = 0; up() { this.n++; } }",)
JCADD = ("class $A {", "  n = 0;", "  add(k) { this.n += k; }", "}")
JCCOUNT = ("class $A {", "  static count = 0;", "  constructor() { $A.count++; }", "}")


def _fib(k: int) -> int:
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def _evens_below(k: int) -> int:
    return len([i for i in range(k) if i % 2 == 0])


JCOUNT = [
    T(L(*JC0, "const x = new $A();", "x.up();", "x.up();", "x.up();", "x.n;"), 3, "Three calls, three ups."),
    T(L(*JC0, "const x = new $A();", "for (let i = 0; i < $a; i++) x.up();", "x.n;"), lambda p: p.a, "The loop calls up() $a times."),
    T(L(*JC0, "const x = new $A();", "const y = new $A();", "x.up();", "x.up();", "y.up();", "y.n;"), 1, "y was called once; x's calls do not count for y."),
    T(L(*JC0, "const x = new $A();", "const y = new $A();", "x.up();", "x.up();", "y.up();", "x.n;"), 2, "x was called twice."),
    T(L(*JCADD, "const x = new $A();", "x.add($a);", "x.add($b);", "x.n;"), lambda p: p.a + p.b, "The two adds together: $a + $b."),
    T(L(*JCADD, "const x = new $A();", "for (let i = 0; i < $a; i++) x.add(i);", "x.n;"), lambda p: sum(range(p.a)),
      "i goes 0, 1, 2 ... up to $a - 1, and they all add up."),
    T(L("class $A {", "  n = 0; up() { this.n++; } down() { this.n--; }", "}", "const x = new $A();", "x.up();", "x.up();", "x.down();", "x.n;"), 1, "Up twice, down once."),
    T(L("class $A {", "  n = 0; up() { this.n++; } reset() { this.n = 0; }", "}", "const x = new $A();", "x.up();", "x.reset();", "x.up();", "x.n;"), 1,
      "The reset wiped the first up; then one more."),
    T(L("class $A {", "  n = 0;", "  up() { this.n = Math.min(this.n + 1, $b); }", "}", "const x = new $A();", "for (let i = 0; i < $a; i++) x.up();", "x.n;"),
      lambda p: min(p.a, p.b), "up() never goes past $b."),
    T(L(*JI, "  up() { this.n++; }", "}", "const x = new $A($a);", "x.up();", "x.up();", "x.n;"), lambda p: p.a + 2, "It starts at $a, then two ups."),
    T(L("class $A {", "  n = 0;", "  up() { this.n = (this.n + 1) % $b; }", "}", "const x = new $A();", "for (let i = 0; i < $a; i++) x.up();", "x.n;"),
      lambda p: p.a % p.b, "n wraps back to 0 every time it reaches $b."),
    T(L("class $A {", "  n = 0;", "  up() { this.n++; return this.n; }", "}", "const x = new $A();", "x.up();", "x.up();"), 2, "The last call returns the new n."),
    T(L("class $A {", "  n = 0;", "  up() { return this.n++; }", "}", "const x = new $A();", "x.up();", "x.up();"), 1,
      "this.n++ gives back the old value: 0 the first time, 1 the second."),
    T(L("class $A {", "  log = [];", "  up() { this.log.push(this.log.length); }", "}", "const x = new $A();", "x.up();", "x.up();", "x.up();", "x.log.at(-1);"), 2,
      "Each up pushes the length so far: 0, 1, 2."),
    T(L(*JCCOUNT, "new $A();", "new $A();", "new $A();", "$A.count;"), 3, "Every new object bumps the one static count."),
    T(L(*JCCOUNT, "for (let i = 0; i < $a; i++) new $A();", "$A.count;"), lambda p: p.a, "$a objects were made."),
    T(L("class $A {", "  count;", "  up() { this.count++; }", "}", "const x = new $A();", "x.up();", "x.count;"), "NaN",
      "count was never given a number: undefined + 1 is NaN."),
    T(L("class $A {", "  static one() { return 1; }", "}", "$A.one() + $A.one();"), 2, "A static method here just returns 1."),
    T(L("class $A {", "  constructor() { let n = 0; this.up = () => ++n; }", "}", "const x = new $A();", "x.up();", "x.up();"), 2,
      "The arrow keeps its own n in a closure; ++n returns the new value."),
    T(L("class $A {", "  constructor() { let n = 0; this.up = () => ++n; }", "}", "const x = new $A();", "const y = new $A();", "x.up();", "x.up();", "y.up();"), 1,
      "Each object has its own closure and its own n."),
    T(L("class $A {", "  n = 0;", "  up = () => { this.n++; };", "}", "const x = new $A();", "const f = x.up;", "f();", "f();", "x.n;"), 2,
      "An arrow field keeps this, even when the function is taken off the object."),
    T(L("class $A {", "  #n = 0;", "  up() { this.#n++; return this; }", "  get n() { return this.#n; }", "}", "new $A().up().up().up().n;"), 3,
      "Each up returns this, so the three calls chain; n reads the private count."),
    T(L("const c = { n: 0, up() { this.n++; return this; } };", "c.up().up().up().n;"), 3, "Each up() returns c, so they chain."),
    T(L(*JI, "  grow() { this.n *= 2; }", "}", "const x = new $A($a);", "x.grow();", "x.grow();", "x.n;"), lambda p: p.a * 4, "Doubled twice: $a * 4."),
    T(L(*JI, "  up() { this.n++; }", "}", "const x = new $A($a);", "const y = new $A($b);", "for (const o of [x, y]) o.up();", "x.n + y.n;"), lambda p: p.a + p.b + 2,
      "Each of the two went up once."),
    T(L(*JC0, "const x = new $A();", "const y = x;", "y.up();", "x.up();", "x.n;"), 2, "x and y are one object, so both ups count."),
    T(L(*JC0, "function make() { const x = new $A(); x.up(); return x; }", "make().n;"), 1, "make builds a counter and ups it once."),
    T(L(*JC0, "const xs = [0, 1, 2].map(() => new $A());", "xs[0].up();", "xs[0].up();", "xs.reduce((s, c) => s + c.n, 0);"), 2,
      "Only the first counter moved, by 2."),
    T(L("class $A {", "  n = 0;", "  up() { this.n++; return true; }", "}", "const x = new $A();", "x.up() || x.up();", "x.n;"), 1,
      "|| stops once it has a true answer, so up() ran once."),
    T(L(*JC0, "const x = new $A();", "x.up() || x.up();", "x.n;"), 2, "up() gives undefined, which is false, so || tries the second too."),
    T(L("class $A {", "  best = 0;", "  see(k) { this.best = Math.max(this.best, k); }", "}", "const x = new $A();", "x.see($a);", "x.see($b);", "x.see($c);", "x.best;"),
      lambda p: max(p.a, p.b, p.c), "best keeps the largest seen."),
    T(L("class $A {", "  total = 0; count = 0;", "  see(k) { this.total += k; this.count++; }", "}", "const x = new $A();", "x.see($a);", "x.see($b);",
        "Math.floor(x.total / x.count);"), lambda p: (p.a + p.b) // 2, "The total is $a + $b, over two sightings, rounded down."),
    T(L("class $A {", "  n = 0;", "  constructor(step) { this.step = step; }", "  up() { this.n += this.step; }", "}", "const x = new $A($a);", "x.up();", "x.up();", "x.n;"),
      lambda p: p.a * 2, "Two ups of $a each."),
    T(L("class $A {", "  constructor(box) { this.box = box; }", "  click() { this.box[0]++; }", "}", "const box = [0];", "const [x, y] = [new $A(box), new $A(box)];", "x.click();",
        "y.click();", "box[0];"), 2, "Both clickers count in the one shared array."),
    T(L(*JC0, "const x = new $A();", "while (x.n < $a) x.up();", "x.n;"), lambda p: p.a, "The loop stops when n reaches $a."),
    T(L(*JC0, "const x = new $A();", "for (let i = 0; i < $a; i++) {", "  if (i % 2 === 0) x.up();", "}", "x.n;"), lambda p: _evens_below(p.a), "Count the even i from 0 to $a - 1."),
    T(L("class $A {", "  a = 0; b = 1;", "  step() { [this.a, this.b] = [this.b, this.a + this.b]; }", "}", "const x = new $A();", "for (let i = 0; i < $a; i++) x.step();", "x.a;"),
      lambda p: _fib(p.a), "The Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8..."),
    T(L(*JC0, "const x = new $A();", "x.up();", "x.n = 10;", "x.up();", "x.n;"), 11, "Assigning 10 replaced the count; one more up gives 11."),
    T(L("class $A {", "  n = 0;", "  up(k = 1) { this.n += k; }", "}", "const x = new $A();", "x.up();", "x.up($a);", "x.n;"), lambda p: p.a + 1, "The first call used the default 1."),
    T(L(*JCCOUNT, "new $A();", "new $A();", "$A.count = 0;", "new $A();", "$A.count;"), 1, "The count was reset to 0, then one more object."),
    T(L("class $A {", "  static count = 0;", "  constructor() { this.constructor.count++; }", "}", "class $B extends $A {}", "new $A();", "new $B();", "new $B();", "$A.count;"), 1,
      "this.constructor is $B for a $B object, so $B bumps a count of its own."),
    T(L("class $A {", "  static count = 0;", "  constructor() { this.constructor.count++; }", "}", "class $B extends $A {}", "new $A();", "new $B();", "new $B();", "$B.count;"), 3,
      "$B's count started from $A's 1 and two new $B() brought it to 3."),
    T(L(*JCCOUNT, "class $B extends $A {}", "new $A();", "new $B();", "new $B();", "$A.count;"), 3, "The constructor names $A explicitly, so $B objects bump it too."),
    T(L("class $A {", "  items = [];", "  add(k) { this.items.push(k); }", "  get size() { return this.items.length; }", "}", "const x = new $A();", "for (let i = 0; i < $a; i++) x.add(i);", "x.size;"),
      lambda p: p.a, "size is the number of items added."),
]

# ── 8. Default Printing ─────────────────────────────────────────────────

JSTR = ("class $A {", "  constructor(n) { this.n = n; }", '  toString() { return "#" + this.n; }', "}")
JNAMED = ("class $A {", "  constructor(name) { this.name = name; }", "  toString() { return this.name; }", "}")
JVAL = ("class $A {", "  constructor(n) { this.n = n; }", "  valueOf() { return this.n; }", "}")

JPRINT = [
    T(L(*JSTR, "String(new $A($a));"), lambda p: "#" + str(p.a), "String(x) calls toString()."),
    T(L(*JSTR, 'new $A($a) + "";'), lambda p: "#" + str(p.a), "+ with a string asks the object for text: toString() here."),
    T(L(*JSTR, 'new $A($a) + "!";'), lambda p: "#" + str(p.a) + "!", "The text from toString(), then a !."),
    T(L(*JSTR, 'const x = new $A($a);', 'const y = new $A($b);', '[x, y].join("-");'), lambda p: "#" + str(p.a) + "-#" + str(p.b), "join calls toString() on each item."),
    T(L(*JNAMED, 'String(new $A("$w"));'), lambda p: p.w, "toString returns the name."),
    T(L("class $A {}", "String(new $A());"), "[object Object]", "With no toString of its own, an object gives [object Object]."),
    T(L("class $A {}", 'new $A() + "";'), "[object Object]", "Joining an object to text uses the default toString."),
    T(L("class $A {}", "new $A().toString();"), "[object Object]", "The default toString on any plain object."),
    T(L("class $A {}", "[new $A()].join();"), "[object Object]", "join turns each item into text: the default toString."),
    T(L(*JSTR, "String([new $A($a)]);"), lambda p: "#" + str(p.a), "An array becomes text by joining its items' text."),
    T(L(*JSTR, "String([new $A($a), new $A($b)]);"), lambda p: "#" + str(p.a) + ",#" + str(p.b), "Array text joins with a comma and no space."),
    T(L(*JSTR, "new $A($a) + 1;"), lambda p: "#" + str(p.a) + "1", "The object becomes text first, then 1 is joined on."),
    T(L(*JVAL, "new $A($a) + 1;"), lambda p: p.a + 1, "+ asks for valueOf(), which gives a number, so it adds."),
    T(L(*JVAL, 'new $A($a) + "!";'), lambda p: str(p.a) + "!", "valueOf() gives the number, which joins the string."),
    T(L(*JVAL, "String(new $A($a));"), "[object Object]", "String() asks for toString(), not valueOf(), and the default toString gives this."),
    T(L("class $A {", '  get [Symbol.toStringTag]() { return "$w"; }', "}", "String(new $A());"), lambda p: "[object " + p.w + "]",
      "Symbol.toStringTag fills in the word after object."),
    T("Object.prototype.toString.call([]);", "[object Array]", "The default toString knows what kind of thing it was given."),
    T("Object.prototype.toString.call(null);", "[object Null]", "Even null has a tag."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "}", "JSON.stringify(new $A($a));"), lambda p: '{"n":' + str(p.a) + "}", "JSON.stringify writes the own properties."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "}", "JSON.stringify([new $A($a)]);"), lambda p: '[{"n":' + str(p.a) + "}]", "The object sits inside the array's brackets."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "  toJSON() { return this.n; }", "}", "JSON.stringify({ k: new $A($a) });"), lambda p: '{"k":' + str(p.a) + "}",
      "toJSON decides what the object is written as: just the number."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "  hi() {}", "}", "JSON.stringify(new $A($a));"), lambda p: '{"n":' + str(p.a) + "}", "Methods are not written."),
    T(L("class $A {", "  constructor(n) { this.n = n; this.m = undefined; }", "}", "JSON.stringify(new $A($a));"), lambda p: '{"n":' + str(p.a) + "}",
      "A property whose value is undefined is left out."),
    T(L(*JSTR, "class $B extends $A {}", "String(new $B($a));"), lambda p: "#" + str(p.a), "$B inherits toString."),
    T(L(*JSTR, "class $B extends $A {", '  toString() { return "B" + this.n; }', "}", "String(new $B($a));"), lambda p: "B" + str(p.a), "$B's own toString wins."),
    T(L(*JSTR, "class $B extends $A {", '  toString() { return super.toString() + "!"; }', "}", "String(new $B($a));"), lambda p: "#" + str(p.a) + "!",
      "super.toString() is $A's text."),
    T(L(*JSTR, "new $A($a).toString().length;"), lambda p: 1 + len(str(p.a)), "# plus the digit."),
    T(L(*JNAMED, 'String(new $A("$w")).toUpperCase();'), lambda p: upper(p.w), "toUpperCase() on the name."),
    T(L(*JNAMED, 'String(new $A("$w"))[0];'), lambda p: p.w[0], "The first character of the text."),
    T(L(*JSTR, 'String(new $A($a)).split("").reverse().join("");'), lambda p: reverse("#" + str(p.a)), "The characters in reverse order."),
    T(L(*JSTR, "const x = new $A($a);", "x + x;"), lambda p: "#" + str(p.a) + "#" + str(p.a), "Each x becomes its text, then they join."),
    T(L("class $A {", "  constructor(d) { this.d = d; }", '  toString() { return this.d + "C"; }', "}", "String(new $A($a));"), lambda p: str(p.a) + "C", "The number, then a C."),
    T(L(*JSTR, "[new $A($a), new $A($b)].toString();"), lambda p: "#" + str(p.a) + ",#" + str(p.b), "An array's toString joins its items with commas."),
    T(L('const o = { toString() { return "$w"; } };', 'o + "!";'), lambda p: p.w + "!", "An object literal can have toString too."),
    T(L(*JVAL, "Number(new $A($a));"), lambda p: p.a, "Number() uses valueOf()."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "  toString() { return this.n; }", "}", 'String(new $A($a)).padStart(3, "0");'), lambda p: "00" + str(p.a),
      "padStart fills on the left with 0 up to width 3."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "}", "new $A($a).n.toFixed(1);"), lambda p: str(p.a) + ".0", "toFixed(1) shows one decimal place."),
    T(L("class $A {", "  constructor(n) { this.n = n; }", "}", "new $A($a).n.toString();"), lambda p: str(p.a), "A number's toString gives its digits as text."),
    T(L(*JSTR, 'String(new $A($a)) === "#" + $a;'), True, "Both sides are the same text."),
]

