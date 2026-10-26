"""C pointers and structs pack, part 3: Struct Copy (assignment copies, `->`, structs in and out of functions, linked
nodes on the stack) and Struct Init (partial and designated initialisers, compound literals, arrays inside structs).

Struct values are modelled with `Struct` from `_cpointers_model.py` where the copy rule matters (its `copy()` copies a
nested struct and an array member in full, a pointer member only as an address); the rest is plain arithmetic. Nothing
asks for `sizeof` of a struct (padding is the compiler's business), nothing uses `malloc`: nodes are local variables.
"""

from __future__ import annotations

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._cpointers_model import Struct, ints
from ._model import Maker

SP = r'struct P { int x, y; };'
SPA = r'struct P a = {$a, $b};'
PS3 = r'struct P ps[3] = {{$a, $b}, {$c, $d}, {$b, $a}};'
MAIN = r'int main(void) {'
INOUT = r'struct In { int u, v; }; struct Out { struct In in; int k; };'
NODES = r'struct N { int v; struct N *next; };'
NODE3 = r'struct N c = {$c, NULL}, b = {$b, &c}, a = {$a, &b};'


def _copy_independent(p: dict) -> str:
    a = Struct(x=p["a"], y=p["b"])
    b = a.copy()
    b.x = p["c"]
    return ints(a.x, b.x)


def _nested_copy(p: dict) -> str:
    o = Struct(inn=Struct(u=p["a"], v=p["b"]), k=p["c"])
    o2 = o.copy()
    o2.inn.u = p["d"]
    return ints(o.inn.u, o2.inn.u)


def _array_member_copy(p: dict) -> str:
    s = Struct(v=[p["a"], p["b"], p["c"]])
    t = s.copy()
    t.v[0] = 0
    return ints(s.v[0], t.v[0])


def _pointer_member_copy(p: dict) -> int:
    from ._cpointers_model import Ptr, var

    x = var(p["a"])
    r = Struct(p=Ptr(x))
    q = r.copy()
    q.p.set(p["b"])
    return r.p.get()


def _name_copy(p: dict) -> str:
    a = Struct(name=p["w"], n=p["a"])
    b = a.copy()
    b.name = p["X"] + b.name[1:]
    return f"{a.name} {b.name}"


def _rect_copy(p: dict) -> str:
    r = Struct(tl=Struct(x=p["a"], y=p["b"]), br=Struct(x=p["a"] + p["c"], y=p["b"] + p["d"]))
    s = r.copy()
    s.tl.x = 0
    return ints(r.tl.x, s.tl.x)


# ── 5. Struct Copy ──────────────────────────────────────────────────────

COPY: list[Maker] = [
    C(T(SP, SPA, r'struct P b = a;', r'b.x = $c;', PF("%d %d", "a.x, b.x")), _copy_independent,
      "b = a copies every member: b is a separate struct, so changing b.x leaves a alone."),
    C(T(SP, SPA, r'struct P b;', r'b = a;', r'a.y = $c;', PF("%d", "b.y")), lambda p: p["b"],
      "The assignment copied a into b once; a later change to a does not reach b."),
    C(T(SP, SPA, r'struct P *p = &a;', r'p->x = $c;', PF("%d", "a.x")), lambda p: p["c"],
      "p->x is the member x of the struct p points at: a itself."),
    C(T(SP, SPA, r'struct P *p = &a;', r'(*p).y += $c;', PF("%d", "a.y")), lambda p: p["b"] + p["c"],
      "(*p).y and p->y mean the same: follow the pointer, then pick the member."),
    C(T(SP, SPA, r'struct P *p = &a;', r'p->x++;', PF("%d %d", "a.x, p->x")), lambda p: ints(p["a"] + 1, p["a"] + 1),
      "p->x++ adds 1 to the member; a and p->x are the same place."),
    C(T(SP, SPA, r'struct P *p = &a;', r'struct P b = *p;', r'b.x = 0;', PF("%d %d", "a.x, p->x")), lambda p: ints(p["a"], p["a"]),
      "*p is a copy source: b holds its own copy, and zeroing b.x touches neither a nor p->x."),
    C(T(SP, SPA, r'struct P b = {$c, $d};', r'struct P *p = &a, *q = &b;', r'*p = *q;', r'q->x = 0;', PF("%d %d", "a.x, a.y")),
      lambda p: ints(p["c"], p["d"]), "*p = *q copies the whole struct into a; zeroing b afterwards does not change that copy."),
    C(T(INOUT, r'struct Out o = {{$a, $b}, $c};', PF("%d", "o.in.v + o.k")), lambda p: p["b"] + p["c"],
      "o.in is a struct inside o; .v picks its second member."),
    C(T(INOUT, r'struct Out o = {{$a, $b}, $c};', r'struct Out o2 = o;', r'o2.in.u = $d;', PF("%d %d", "o.in.u, o2.in.u")), _nested_copy,
      "A struct inside a struct is part of it, so copying o copies o.in too."),
    C(T(INOUT, r'struct Out o = {{$a, $b}, $c};', r'struct In *ip = &o.in;', r'ip->v = $d;', PF("%d", "o.in.v")), lambda p: p["d"],
      "&o.in is the address of the inner struct inside o: writing through it changes o."),
    C(T(SP, PS3, r'ps[1].x = $n;', PF("%d", "ps[0].x + ps[1].x")), lambda p: p["a"] + p["n"],
      "ps[1].x is the x of the second struct in the array."),
    C(T(SP, PS3, r'struct P *p = ps;', r'p++;', PF("%d %d", "p->x, p->y")), lambda p: ints(p["c"], p["d"]),
      "p++ steps over a whole struct, to the second element."),
    C(T(SP, PS3, r'struct P *p = &ps[2];', PF("%d %d", "(int)(p - ps), p->x")), lambda p: ints(2, p["b"]),
      "p - ps counts structs, not bytes: p is two elements in."),
    C(T(SP, PS3, r'struct P *p = ps;', PF("%d %d", "(p + 1)->y, (*(p + 2)).x")), lambda p: ints(p["d"], p["b"]),
      "p + 1 is the second struct and p + 2 the third; -> and (*). both reach a member."),
    C(T(SP, r'struct P make(int x, int y) { struct P r = {x, y}; return r; }', MAIN, r'    printf("%d\n", make($a, $b).y);', r'}'),
      lambda p: p["b"], "A function can return a whole struct by value; .y picks a member of the result."),
    C(T(SP, r'struct P sw(struct P p) { int t = p.x; p.x = p.y; p.y = t; return p; }', MAIN, r'    struct P a = {$a, $b};', r'    struct P b = sw(a);',
        r'    printf("%d %d %d %d\n", a.x, a.y, b.x, b.y);', r'}'),
      lambda p: ints(p["a"], p["b"], p["b"], p["a"]),
      "sw gets a copy of a, swaps the copy and returns it: a is unchanged, b is the swapped struct."),
    C(T(SP, r'void bump(struct P p) { p.x++; }', MAIN, r'    struct P a = {$a, $b};', r'    bump(a);', r'    printf("%d\n", a.x);', r'}'),
      lambda p: p["a"], "A struct is passed by value like an int: bump changed its own copy."),
    C(T(SP, r'void bump(struct P *p) { p->x++; }', MAIN, r'    struct P a = {$a, $b};', r'    bump(&a);', r'    printf("%d\n", a.x);', r'}'),
      lambda p: p["a"] + 1, "Passing the address lets the function change the caller's struct."),
    C(T(SP, r'struct P add(struct P a, struct P b) { a.x += b.x; return a; }', MAIN, r'    struct P a = {$a, $b}, b = {$c, $d};',
        r'    struct P s = add(a, b);', r'    printf("%d %d\n", s.x, a.x);', r'}'),
      lambda p: ints(p["a"] + p["c"], p["a"]), "add works on copies: only the returned sum is new, the caller's a stays."),
    C(T(SP, SPA, r'struct P b = a;', PF("%d", "b.x == a.x && b.y == a.y")), 1, "A copy has equal members (C cannot compare whole structs with ==)."),
    C(T(r'struct S { int v[3]; };', r'struct S s = {{$a, $b, $c}};', r'struct S t = s;', r't.v[0] = 0;', PF("%d %d", "s.v[0], t.v[0]")), _array_member_copy,
      "An array inside a struct is copied with it, unlike an array passed to a function."),
    C(T(r'struct S { int v[3]; };', r'void zero(struct S s) { s.v[0] = 0; }', MAIN, r'    struct S s = {{$a, $b, $c}};', r'    zero(s);',
        r'    printf("%d\n", s.v[0]);', r'}'), lambda p: p["a"],
      "The struct arrives as a copy, array and all, so zeroing its array does not reach the caller."),
    C(T(r'struct R { int *p; };', r'int x = $a;', r'struct R r = {&x};', r'struct R q = r;', r'*q.p = $b;', PF("%d", "*r.p")), _pointer_member_copy,
      "Copying a struct copies the pointer inside, not what it points at: both point at x."),
    C(T(SP, PS3, r'ps[0] = ps[2];', PF("%d %d", "ps[0].x, ps[0].y")), lambda p: ints(p["b"], p["a"]),
      "Array elements that are structs can be assigned whole."),
    C(T(SP, SPA, r'struct P b = {$c, $d};', r'struct P t = a;', r'a = b;', r'b = t;', PF("%d %d", "a.x, b.x")), lambda p: ints(p["c"], p["a"]),
      "Swapping two structs with a third as the temporary, like swapping two ints."),
    C(T(SP, PS3, r'struct P *q = &ps[1];', r'q->x = $n;', PF("%d", "ps[1].x")), lambda p: p["n"],
      "q points at the second element, so q->x is ps[1].x."),
    C(T(r'struct N { char name[8]; int n; };', r'struct N a = {"$w", $a};', r'struct N b = a;', r"b.name[0] = '$X';", PF("%s %s", "a.name, b.name")), _name_copy,
      "The name array lives inside the struct, so b has its own letters to change."),
    C(T(SP, SPA, r'struct P *p = &a;', r'p->x += p->y;', PF("%d", "a.x")), lambda p: p["a"] + p["b"],
      "Both p->x and p->y are members of a."),
    C(T(SP, SPA, r'int *px = &a.y;', r'*px = $c;', PF("%d", "a.y")), lambda p: p["c"],
      "&a.y is the address of the member, and writing through it changes the member."),
    C(T(SP, SPA, r'struct P *p = &a;', r'int *py = &p->y;', r'*py = $c;', PF("%d", "a.y")), lambda p: p["c"],
      "&p->y is the address of the y member of the struct p points at."),
    C(T(SP, r'struct P *larger(struct P *a, struct P *b) { return a->x > b->x ? a : b; }', MAIN, r'    struct P a = {$a, $b}, b = {$c, $d};',
        r'    larger(&a, &b)->y = 0;', r'    printf("%d %d\n", a.y, b.y);', r'}'),
      lambda p: ints(0, p["d"]) if p["a"] > p["c"] else ints(p["b"], 0),
      "larger returns the address of the struct with the bigger x; ->y = 0 changes that one."),
    C(T(SP, PS3, r'for (struct P *p = ps; p < ps + 3; p++)', r'    p->x *= 2;', PF("%d", "ps[2].x")), lambda p: 2 * p["b"],
      "The pointer visits each struct of the array and doubles its x."),
    C(T(SP, PS3, r'for (int i = 0; i < 3; i++) {', r'    struct P t = ps[i];', r'    t.x = 0;', r'}', PF("%d", "ps[0].x + ps[1].x + ps[2].x")),
      lambda p: p["a"] + p["c"] + p["b"], "t is a copy of each element; zeroing the copy leaves the array alone."),
    C(T(SP, r'struct R { struct P tl, br; };', r'struct R r = {{$a, $b}, {$a + $c, $b + $d}};', PF("%d", "(r.br.x - r.tl.x) * (r.br.y - r.tl.y)")),
      lambda p: p["c"] * p["d"], "The width is c and the height d, read from the corners inside r."),
    C(T(SP, r'struct R { struct P tl, br; };', r'struct R r = {{$a, $b}, {$a + $c, $b + $d}};', r'struct R s = r;', r's.tl.x = 0;', PF("%d %d", "r.tl.x, s.tl.x")),
      _rect_copy, "The corners are inside the rectangle, so the copy has its own."),
    C(T(NODES, NODE3, PF("%d", "a.next->next->v")), lambda p: p["c"],
      "a.next is &b and b.next is &c: two arrows reach the third node."),
    C(T(NODES, NODE3, r'int s = 0;', r'for (struct N *p = &a; p; p = p->next)', r'    s += p->v;', PF("%d", "s")), lambda p: p["a"] + p["b"] + p["c"],
      "The loop follows next pointers until the null one: all three nodes are added."),
    C(T(NODES, NODE3, r'int n = 0;', r'for (struct N *p = &a; p; p = p->next)', r'    n++;', PF("%d", "n")), 3,
      "Three nodes are linked; the last next is NULL, which ends the loop."),
    C(T(NODES, NODE3, r'a.next->v = $d;', PF("%d", "b.v")), lambda p: p["d"],
      "a.next is the address of b, so a.next->v is b.v."),
    C(T(SP, r'int dot(const struct P *a, const struct P *b) { return a->x * b->x + a->y * b->y; }', MAIN, r'    struct P a = {$a, $b}, b = {$c, $d};',
        r'    printf("%d\n", dot(&a, &b));', r'}'), lambda p: p["a"] * p["c"] + p["b"] * p["d"],
      "dot reads both structs through const pointers: nothing is copied."),
    C(T(SP, r'struct P bump(struct P p) { p.x++; return p; }', MAIN, r'    struct P a = {$a, $b};', r'    struct P b = bump(bump(a));',
        r'    printf("%d %d\n", a.x, b.x);', r'}'), lambda p: ints(p["a"], p["a"] + 2),
      "Each call bumps and returns a copy; only b receives the final one."),
    C(T(SP, SPA, r'struct P *p = &a;', r'struct P *q = p;', r'q->x = $c;', PF("%d", "p->x")), lambda p: p["c"],
      "q = p copies the address, so both pointers reach the same struct."),
    C(T(SP, SPA, r'struct P *p = &a;', PF("%d", "(*p).x + p->y")), lambda p: p["a"] + p["b"], "(*p).x and p->x are the same member."),
    C(T(r'struct T { char c; int n; };', r"struct T t = {'$x', $a};", r'struct T u = t;', r'u.c++;', PF("%c%c %d", "t.c, u.c, u.n")),
      lambda p: f"{p['x']}{chr(ord(p['x']) + 1)} {p['a']}", "u is a copy: its char moves on to the next letter while t keeps its own."),
    C(T(SP, r'struct P get(struct P *ps, int i) { return ps[i]; }', MAIN, r'    struct P ps[2] = {{$a, $b}, {$c, $d}};', r'    struct P g = get(ps, 1);',
        r'    g.x = 0;', r'    printf("%d\n", ps[1].x);', r'}'), lambda p: p["c"],
      "get returns a copy of the element, so changing g leaves the array alone."),
    C(T(SP, r'struct P make(int x, int y) { struct P r = {x, y}; return r; }', MAIN, r'    printf("%d\n", make($a, $b).x + make($c, $d).y);', r'}'),
      lambda p: p["a"] + p["d"], "Each call builds a struct; only one member of each is used."),
    C(T(SP, SPA, r'struct P b = {$c, $d};', r'struct P *big = a.x > b.x ? &a : &b;', r'big->x = 0;', PF("%d %d", "a.x, b.x")),
      lambda p: ints(0, p["c"]) if p["a"] > p["c"] else ints(p["a"], 0), "big points at the struct with the bigger x, and only that one is zeroed."),
]


# ── 6. Struct Init ──────────────────────────────────────────────────────

TRI = r'struct T { int a, b, c; };'
OP = r'struct O { struct P in; int k; };'
SS = r'struct S { int v[4]; };'
NM = r'struct N { char name[8]; int id; };'
RR = r'struct R { int *p; int n; };'

INIT: list[Maker] = [
    C(T(SP, r'struct P p = {$a};', PF("%d %d", "p.x, p.y")), lambda p: ints(p["a"], 0), "The members the braces leave out are set to 0."),
    C(T(SP, r'struct P p = {.y = $a};', PF("%d %d", "p.x, p.y")), lambda p: ints(0, p["a"]), "A designator names the member to set; the other one is 0."),
    C(T(SP, r'struct P p = {.y = $a, .x = $b};', PF("%d %d", "p.x, p.y")), lambda p: ints(p["b"], p["a"]), "Designators can come in any order: each sets the member it names."),
    C(T(TRI, r'struct T t = {$a, $b};', PF("%d %d %d", "t.a, t.b, t.c")), lambda p: ints(p["a"], p["b"], 0), "Two values fill the first two members; the third is 0."),
    C(T(TRI, r'struct T t = {0};', PF("%d", "t.a + t.b + t.c")), 0, "{0} sets the first member, and everything else is zeroed too."),
    C(T(SP, SPA, r'a = (struct P){$c};', PF("%d %d", "a.x, a.y")), lambda p: ints(p["c"], 0),
      "A compound literal is a whole new struct: the member it leaves out is 0, not the old b."),
    C(T(SP, SPA, r'a = (struct P){.y = $c};', PF("%d %d", "a.x, a.y")), lambda p: ints(0, p["c"]),
      "x is not mentioned, so it becomes 0: the old a.x is not kept."),
    C(T(SP, SPA, r'a = (struct P){.x = $c};', PF("%d %d", "a.x, a.y")), lambda p: ints(p["c"], 0),
      "Only x is given, so y becomes 0 (the old y is lost)."),
    C(T(SP, SPA, r'struct P *q = &(struct P){$c, $d};', r'q->x++;', PF("%d %d", "q->x, q->y")), lambda p: ints(p["c"] + 1, p["d"]),
      "A compound literal is an unnamed variable: you can take its address and change it."),
    C(T(r'int *v = (int[]){$a, $b, $c};', PF("%d", "v[1] + v[2]")), lambda p: p["b"] + p["c"],
      "(int[]){...} is an unnamed array; v points at its first element."),
    C(T(SP, OP, r'struct O o = {{$a, $b}, $c};', PF("%d %d", "o.in.y, o.k")), lambda p: ints(p["b"], p["c"]),
      "The inner braces fill the struct inside; the next value is k."),
    C(T(SP, OP, r'struct O o = {$a, $b, $c};', PF("%d %d", "o.in.y, o.k")), lambda p: ints(p["b"], p["c"]),
      "Without inner braces the values still fill the members in order, inner struct first."),
    C(T(SP, OP, r'struct O o = {.in = {.y = $a}, .k = $b};', PF("%d %d %d", "o.in.x, o.in.y, o.k")), lambda p: ints(0, p["a"], p["b"]),
      "Designators can nest: .in = {.y = a} sets only the y of the inner struct."),
    C(T(SP, OP, r'struct O o = {.in.y = $a};', PF("%d %d %d", "o.in.x, o.in.y, o.k")), lambda p: ints(0, p["a"], 0),
      ".in.y reaches straight into the inner struct; everything else is 0."),
    C(T(SS, r'struct S s = {{$a, $b}};', PF("%d", "s.v[0] + s.v[1] + s.v[2] + s.v[3]")), lambda p: p["a"] + p["b"],
      "The array inside has four elements; the two not given are 0."),
    C(T(SS, r'struct S s = {.v = {[2] = $a}};', PF("%d %d", "s.v[1], s.v[2]")), lambda p: ints(0, p["a"]),
      "[2] = a sets index 2 of the array; the rest is 0."),
    C(T(SP, r'struct P ps[3] = {{$a, $b}, {$c}};', PF("%d %d %d", "ps[1].x, ps[1].y, ps[2].x")), lambda p: ints(p["c"], 0, 0),
      "The second struct got only x; the third was not mentioned at all: both are 0."),
    C(T(SP, r'struct P ps[3] = {[2] = {$a, $b}};', PF("%d %d", "ps[0].x, ps[2].y")), lambda p: ints(0, p["b"]),
      "[2] = {...} sets the third struct; the first stays 0."),
    C(T(SP, r'struct P ps[] = {{$a, $b}, {$c, $d}, {$b, $a}};', PF("%zu", "sizeof ps / sizeof ps[0]")), 3,
      "With no number in the brackets the array has as many elements as the braces list."),
    C(T(SP, r'struct P ps[] = {$a, $b, $c, $d};', PF("%zu %d", "sizeof ps / sizeof ps[0], ps[1].x")), lambda p: f"2 {p['c']}",
      "Four numbers fill two structs two by two; the second starts with c."),
    C(T(NM, r'struct N n = {"$w"};', PF("%zu %d", "strlen(n.name), n.id")), lambda p: f"{len(p['w'])} 0",
      "The string fills name; id is not mentioned, so it is 0."),
    C(T(NM, r'struct N n = {.id = $a, .name = "$w"};', PF("%s %d", "n.name, n.id")), lambda p: f"{p['w']} {p['a']}",
      "Designators set the members in any order."),
    C(T(NM, r'struct N n = {"$w"};', PF("%d", "n.name[$L]")), 0,
      "The characters after the word are zeros, so right after the last letter sits a NUL."),
    C(T(SP, r'static struct P g;', PF("%d", "g.x + g.y")), 0, "A static struct starts with every member 0."),
    C(T(SP, r'struct P p;', r'p.x = $a;', r'p.y = $b;', r'struct P q = {p.y, p.x};', PF("%d %d", "q.x, q.y")), lambda p: ints(p["b"], p["a"]),
      "An initialiser of a local struct may use other variables: q gets y first, then x."),
    C(T(SP, SPA, r'struct P b = a;', r'a.x = 0;', PF("%d", "b.x")), lambda p: p["a"], "b = a at its declaration copies a: later changes to a do not reach b."),
    C(T(SP, r'const struct P cp = {$a, $b};', r'struct P q = cp;', r'q.x++;', PF("%d %d", "cp.x, q.x")), lambda p: ints(p["a"], p["a"] + 1),
      "Copying a const struct gives a normal one that can change."),
    C(T(SP, PF("%d", "((struct P){$a, $b}).y")), lambda p: p["b"], "A compound literal is a value like any other: .y picks a member of it."),
    C(T(SP, r'struct P mk(int a) { return (struct P){a, a * 2}; }', MAIN, r'    printf("%d\n", mk($a).y);', r'}'), lambda p: 2 * p["a"],
      "mk returns a compound literal built from its argument."),
    C(T(SP, r'int sum(struct P p) { return p.x + p.y; }', MAIN, r'    printf("%d\n", sum((struct P){$a, $b}));', r'}'), lambda p: p["a"] + p["b"],
      "A compound literal can be written right in the call."),
    C(T(SP, r'int sum(struct P p) { return p.x + p.y; }', MAIN, r'    printf("%d\n", sum((struct P){.y = $a}));', r'}'), lambda p: p["a"],
      "x is not given, so it is 0: the sum is just a."),
    C(T(TRI, r'struct T t = {.b = $a, $b};', PF("%d %d %d", "t.a, t.b, t.c")), lambda p: ints(0, p["a"], p["b"]),
      "After .b = a the next value goes to the NEXT member, c."),
    C(T(r'int v[5] = {[1] = $a, $b};', PF("%d %d %d %d", "v[0], v[1], v[2], v[3]")), lambda p: ints(0, p["a"], p["b"], 0),
      "After [1] = a the next value goes to index 2."),
    C(T(r'int v[] = {[3] = $a};', PF("%zu %d", "sizeof v / sizeof v[0], v[3]")), lambda p: f"4 {p['a']}",
      "The largest designated index decides the size: index 3 means 4 elements."),
    C(T(r"char s[8] = {'$x', '$y'};", PF("%zu %s", "strlen(s), s")), lambda p: f"2 {p['x']}{p['y']}",
      "The rest of the array is zeros, so the two letters are followed by a NUL."),
    C(T(r'char t[10] = "$w";', PF("%zu %zu", "sizeof t, strlen(t)")), lambda p: f"10 {len(p['w'])}",
      "The array is 10 big however short the word is."),
    C(T(SP, r'struct W { struct P a, b; };', r'struct W w = {{$a}, {.y = $b}};', PF("%d %d %d %d", "w.a.x, w.a.y, w.b.x, w.b.y")),
      lambda p: ints(p["a"], 0, 0, p["b"]), "Each inner struct is initialised on its own; what it leaves out is 0."),
    C(T(r'struct M { int n; double d; };', r'struct M m = {.n = $a};', PF("%d %.1f", "m.n, m.d")), lambda p: f"{p['a']} 0.0",
      "A double member left out is 0.0."),
    C(T(r'struct M { int n; double d; };', r'struct M m = {.d = $a / 2.0};', PF("%d %.1f", "m.n, m.d")), lambda p: f"0 {p['a'] / 2:.1f}",
      "Only d is set; n is 0."),
    C(T(r'struct C { char c; int n; };', r"struct C x = {'$x', $a};", PF("%c%d", "x.c, x.n")), lambda p: f"{p['x']}{p['a']}",
      "A character literal initialises the char member."),
    C(T(RR, r'struct R r = {0};', PF("%d %d", "r.p == NULL, r.n")), "1 0", "{0} zeroes every member, and a zeroed pointer is a null pointer."),
    C(T(RR, r'struct R r = {.n = $a};', PF("%d", "r.p == NULL")), 1, "The pointer member was not given, so it is NULL."),
    C(T(RR, r'int x = $a;', r'struct R r = {&x, $b};', r'*r.p += r.n;', PF("%d", "x")), lambda p: p["a"] + p["b"],
      "The struct holds the address of x, so *r.p changes x."),
    C(T(RR, r'int x = $a, y = $b;', r'struct R rs[3] = {{&x}, {&y}};', PF("%d %d", "rs[2].p == NULL, *rs[1].p")), lambda p: f"1 {p['b']}",
      "The third struct was left out, so its pointer is NULL; the second points at y."),
    C(T(SP, r'struct P ps[2] = {[1].x = $a};', PF("%d %d %d", "ps[0].x, ps[1].x, ps[1].y")), lambda p: ints(0, p["a"], 0),
      "[1].x = a names the element and the member in one designator."),
    C(T(SP, r'struct P ps[2] = {0};', PF("%d", "ps[1].y")), 0, "{0} zeroes the whole array of structs."),
    C(T(SP, r'struct P p = {.x = $a};', r'p.y += 5;', PF("%d", "p.y")), 5, "y started at 0, since it was not given."),
    C(T(SP, r'struct P *ps = (struct P[]){{$a, $b}, {$c, $d}};', PF("%d", "ps[1].y")), lambda p: p["d"],
      "A compound literal can be an array of structs."),
    C(T(SP, SPA, r'a = (struct P){a.y, a.x};', PF("%d %d", "a.x, a.y")), lambda p: ints(p["b"], p["a"]),
      "The new struct is built from the old values first and only then assigned: x and y trade."),
]
