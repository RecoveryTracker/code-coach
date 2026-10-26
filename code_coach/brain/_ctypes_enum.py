"""C types and preprocessor pack, part 3: Enum Value (`ct_enum`) and Typedef Reads (`ct_typedef`).

Enumerators are plain `int` constants numbered by hand-worked rules (start at 0, each is the previous plus one unless it
has an `=`); a typedef is another name for a type, so the answers are ordinary C values. Items that only declare types
and variables in `main` are bodies; the ones with helper functions are complete programs (the oracle makes their
file-level names `static`, so only definitions that come BEFORE their later `extern` declarations are safe: none is used).
"""

from __future__ import annotations

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._model import Maker

COLORS = ["RED", "GREEN", "BLUE", "YELLOW"]
DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
DIRS = ["NORTH", "EAST", "SOUTH", "WEST"]
LEVELS = ["LOW", "MID", "HIGH"]
STATES = ["IDLE", "RUN", "STOP", "DONE"]


def decl(names: list[str], tag: str = "E") -> str:
    return f"enum {tag} {{ " + ", ".join(names) + " };"


def _plain(names: list[str], ask: str) -> Maker:
    return C(T(decl(names), PF("%d", ask)), names.index(ask), f"Enumerators count up from 0 in the order written: {ask} is number {names.index(ask)}.")


def _last_plus(names: list[str], pick: int) -> Maker:
    name = names[pick]
    return C(T(decl(names), PF("%d", f"{name} + {names[-1]}")), pick + len(names) - 1, "Enumerators are ordinary int constants, so they can be added.")


# ── 1. Enum Value ───────────────────────────────────────────────────────

ENUMS: list[Maker] = [
    _plain(COLORS, "GREEN"), _plain(COLORS, "BLUE"), _plain(COLORS, "YELLOW"), _plain(DAYS, "WED"), _plain(DAYS, "FRI"),
    _plain(DIRS, "EAST"), _plain(DIRS, "WEST"), _plain(LEVELS, "HIGH"), _plain(STATES, "STOP"), _plain(STATES, "DONE"),
    _last_plus(DAYS, 1), _last_plus(COLORS, 2),
    # explicit values
    C(T("enum { A = $a, B, C };", PF("%d %d", "B, C")), lambda p: f"{p['a'] + 1} {p['a'] + 2}", "After an explicit value the numbering goes on from it, one at a time."),
    C(T("enum { X, Y = $n, Z, W };", PF("%d %d", "Z, W")), lambda p: f"{p['n'] + 1} {p['n'] + 2}", "Z and W continue from Y's value, not from 1 and 2."),
    C(T("enum { X, Y = $n, Z };", PF("%d", "X + Z")), lambda p: p["n"] + 1, "X is 0 (the start), Y is n and Z is n + 1."),
    C(T("enum { A = 5, B = 2, C };", PF("%d", "C")), 3, "C follows B, which was set back to 2: so 3."),
    C(T("enum { A = $a, B = A * 2, C = B + 1 };", PF("%d", "C")), lambda p: p["a"] * 2 + 1, "An enumerator can use the ones before it in a constant expression."),
    C(T("enum { A = $n, B = A - $a, C };", PF("%d %d", "B, C")), lambda p: f"{p['n'] - p['a']} {p['n'] - p['a'] + 1}", "B is A - a, and C is one more than B."),
    C(T("enum { LOW = -1, MID, HIGH };", PF("%d %d", "MID, HIGH")), "0 1", "Counting on from -1 gives 0 and 1."),
    C(T("enum { A = -$a, B, C };", PF("%d %d", "B, C")), lambda p: f"{-p['a'] + 1} {-p['a'] + 2}", "Counting on from a negative number climbs toward 0."),
    C(T("enum { A = 1, B = 1, C };", PF("%d", "A + B + C")), 4, "Two enumerators may share a value; C is one more than B: 1 + 1 + 2."),
    C(T("enum { A = 3, B, C = 10, D };", PF("%d", "B + D")), 15, "B is 4 and D is 11."),
    C(T("enum { A = $a, B = A + A, C = B + A };", PF("%d", "C")), lambda p: 3 * p["a"], "B is 2a, C is 3a."),
    C(T("enum { A = 'a', B };", PF("%c", "B")), "b", "A char constant is an int: A is 97, B is 98, which %c prints as b."),
    C(T("enum { A = '0', B, C };", PF("%d", "C")), 50, "'0' is 48: B is 49 and C is 50."),
    # flags
    C(T("enum { R = 1 << 0, W = 1 << 1, X = 1 << 2 };", PF("%d", "R | X")), 5, "1 | 4 sets bit 0 and bit 2."),
    C(T("enum { R = 1 << 0, W = 1 << 1, X = 1 << 2 };", PF("%d", "W | X")), 6, "2 | 4 sets bit 1 and bit 2."),
    C(T("enum { R = 1, W = 2, X = 4 };", PF("%d", "(R | W | X) & ~W")), 5, "All three bits, then bit 1 cleared: 7 & ~2 is 5."),
    C(T("enum { R = 1, W = 2, X = 4 };", "int perm = R | W;", PF("%d %d", "(perm & W) != 0, (perm & X) != 0")), "1 0", "perm has bit W set and bit X not set."),
    C(T("enum { R = 1, W = 2, X = 4 };", "int perm = R;", "perm |= X;", "perm ^= R;", PF("%d", "perm")), 4, "R | X is 5; flipping R off leaves 4."),
    C(T("enum { A = 1 << $k, B = A << 1 };", PF("%d %d", "A, B")), lambda p: f"{1 << p['k']} {2 << p['k']}", "A is 2 to the k, B is twice that."),
    # a sentinel and arrays
    C(T("enum { A, B, C, D, COUNT };", "int slots[COUNT];", PF("%zu", "sizeof slots / sizeof slots[0]")), 4, "COUNT comes last, so it equals the number of enumerators before it: 4."),
    C(T("enum { A, B, C, COUNT };", "int s = 0;", "for (int i = 0; i < COUNT; i++)", "    s += i * $a;", PF("%d", "s")), lambda p: 3 * p["a"], "COUNT is 3: the loop adds 0, a, 2a."),
    C(T("enum Day { MON, TUE, WED, THU, FRI, DAYS };", PF("%d", "DAYS")), 5, "The last enumerator doubles as the count."),
    C(T("enum Day { MON, TUE, WED, THU, FRI, DAYS };", PF("%d", "(FRI + $k) % DAYS")), lambda p: (4 + p["k"]) % 5, "Adding k to FRI and wrapping at DAYS gives the day k later."),
    C(T("enum Day { MON, TUE, WED, THU, FRI, DAYS };", "int d = THU;", "d = (d + 1) % DAYS;", PF("%d", "d")), 4, "THU is 3: the next day is 4, FRI."),
    C(T("enum Day { MON, TUE, WED, THU, FRI, DAYS };", "int d = FRI;", "d = (d + 1) % DAYS;", PF("%d", "d")), 0, "After the last day the % wraps back to MON, 0."),
    C(T("enum { RED, GREEN, BLUE };", 'const char *names[] = {"red", "green", "blue"};', PF("%s", "names[GREEN]")), "green", "The enumerator is the index into the array."),
    C(T("enum { RED, GREEN, BLUE };", 'const char *names[] = {"red", "green", "blue"};', PF("%s", "names[BLUE - 1]")), "green", "BLUE - 1 is 1."),
    C(T("enum { APPLE, PEAR, PLUM };", "int price[] = { [PLUM] = $a, [APPLE] = $b, [PEAR] = $c };", PF("%d", "price[PEAR] + price[PLUM]")),
      lambda p: p["c"] + p["a"], "Designated initializers put each price at its enumerator's index."),
    C(T("enum { N = $a };", "int v[N] = {1, 2};", "int s = 0;", "for (int i = 0; i < N; i++)", "    s += v[i];", PF("%d", "s")), 3, "An enumerator is a constant, so it can size an array: the unset elements are 0."),
    # variables of an enum type
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = BLUE;", PF("%d", "c - 1")), 1, "A variable of an enum type holds an int."),
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = GREEN;", PF("%d", "c == 1")), 1, "GREEN is 1, so the comparison is true."),
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = RED;", "c++;", PF("%d", "c == GREEN")), 1, "Adding 1 to RED (0) gives 1, which is GREEN."),
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = (enum Color)2;", PF("%d", "c == BLUE")), 1, "The cast gives the enum variable the value 2, which is BLUE."),
    C(T("typedef enum { OFF, ON } State;", "State s = ON;", "s = !s;", PF("%d", "s")), 0, "!ON is 0, which is OFF."),
    C(T("typedef enum { OFF, ON } State;", "State s = OFF;", "for (int i = 0; i < $a; i++)", "    s = !s;", PF("%d", "s")), lambda p: p["a"] % 2, "Each turn flips the state; an even number of flips is back to OFF."),
    C(T("typedef enum { LOW = 1, HIGH = 10 } Level;", "Level l = HIGH;", PF("%d", "l + LOW")), 11, "HIGH is 10 and LOW is 1."),
    C(T("enum { RED, GREEN, BLUE };", PF("%d", "BLUE > GREEN && GREEN > RED")), 1, "The values grow in the order written: 2 > 1 > 0."),
    C(T("enum { A = 7, B = 3 };", PF("%d", "A > B")), 1, "Enumerators compare as the numbers they are, not in the order written."),
    # switch on an enum
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = BLUE;", "switch (c) {", '    case RED: printf("r"); break;', '    case GREEN: printf("g"); break;',
        '    case BLUE: printf("b"); break;', "}"), "b", "The case labels are the enumerators' values."),
    C(T("enum Color { RED, GREEN, BLUE };", "enum Color c = (enum Color)$q;", "switch (c) {", '    case RED: printf("r");', '    case GREEN: printf("g"); break;',
        '    case BLUE: printf("b"); break;', "}"), lambda p: ["rg", "g", "b"][p["q"]], "RED has no break, so it falls through and prints g as well."),
    C(T("enum Day { MON, TUE, WED, THU, FRI };", "int sum = 0;", "for (enum Day d = MON; d <= FRI; d++)", "    if (d % 2 == 0)", "        sum += d;", PF("%d", "sum")), 6,
      "The even days are MON, WED and FRI: 0 + 2 + 4."),
    C(T("enum { SMALL = 1, BIG = 100 };", "int x = $a;", PF("%d", "x < $b ? SMALL : BIG")), lambda p: 1 if p["a"] < p["b"] else 100, "The ?: picks one enumerator's value."),
    C(T("enum { SIZE = $a * $b };", PF("%d", "SIZE + 1")), lambda p: p["a"] * p["b"] + 1, "The enumerator's value is a constant expression: a * b."),
]


# ── 2. Typedef Reads ────────────────────────────────────────────────────

def _op(name: str, expr: str) -> str:
    return f"int {name}(int a, int b) {{ return {expr}; }}"


OPS = {"add": ("a + b", lambda x, y: x + y), "sub": ("a - b", lambda x, y: x - y), "mul": ("a * b", lambda x, y: x * y)}


def _apply(name: str) -> Maker:
    text, fn = OPS[name]
    return C(T("typedef int (*Op)(int, int);", _op(name, text), "int main(void) {", f"    Op f = {name};", PF("%d", "f($a, $b)"), "}"),
             lambda p: fn(p["a"], p["b"]), f"Op is a pointer to a function taking two ints and returning an int: f calls {name}.")


TYPEDEFS: list[Maker] = [
    _apply("add"), _apply("sub"), _apply("mul"),
    C(T("typedef int (*Op)(int, int);", _op("add", "a + b"), _op("mul", "a * b"), "int main(void) {", "    Op ops[] = {add, mul};",
        PF("%d", "ops[$r]($n, $a)"), "}"), lambda p: p["n"] * p["a"] if p["r"] else p["n"] + p["a"], "ops is an array of functions: ops[0] is add and ops[1] is mul."),
    C(T("typedef int (*Fn)(int);", "int dbl(int x) { return 2 * x; }", "int twice(Fn f, int x) { return f(f(x)); }", "int main(void) {", PF("%d", "twice(dbl, $a)"), "}"),
      lambda p: 4 * p["a"], "twice calls the function it is given two times: doubling twice is times 4."),
    C(T("typedef int (*Fn)(int);", "int inc(int x) { return x + 1; }", "int apply(Fn f, int n, int x) {", "    for (int i = 0; i < n; i++)", "        x = f(x);",
        "    return x;", "}", "int main(void) {", PF("%d", "apply(inc, $a, $n)"), "}"), lambda p: p["n"] + p["a"], "apply calls inc a times: n grows by a."),
    C(T("typedef int Fn(int);", "int sq(int x) { return x * x; }", "int main(void) {", "    Fn *f = sq;", PF("%d", "f($a)"), "}"), lambda p: p["a"] ** 2,
      "Fn is a function TYPE, so Fn * is a pointer to such a function."),
    C(T("typedef uint8_t byte;", "byte b = $u;", "b += $n;", PF("%d", "b")), lambda p: (p["u"] + p["n"]) % 256, "byte is just uint8_t under another name, so it wraps modulo 256."),
    C(T("typedef unsigned char u8;", "u8 x = 250;", PF("%d", "x + $n")), lambda p: 250 + p["n"], "x is promoted to int before the +, so nothing wraps."),
    C(T("typedef int Meters;", "Meters m = $a;", "int *p = &m;", "*p = $b;", PF("%d", "m")), lambda p: p["b"], "A typedef makes no new type: Meters is int, so an int pointer fits."),
    C(T("typedef int A;", "typedef A B;", "typedef B C;", "C x = $a;", PF("%zu", "sizeof(C) + sizeof(x)")), 8, "All three names mean int: 4 + 4."),
    C(T("typedef int Row[3];", "Row r = {$a, $b, $c};", PF("%zu", "sizeof(Row) / sizeof(r[0])")), 3, "Row is an array of 3 ints: its size over one element is 3."),
    C(T("typedef int Row[3];", "Row r = {$a, $b, $c};", PF("%zu", "sizeof(Row)")), 12, "3 ints of 4 bytes each."),
    C(T("typedef int Row[3];", "Row r = {$a, $b, $c};", PF("%d", "r[2]")), lambda p: p["c"], "Row r declares an array of 3 ints; r[2] is the last."),
    C(T("typedef int Row[3];", "Row r[2] = {{1, 2, 3}, {$a, $b, $c}};", PF("%d", "r[1][2]")), lambda p: p["c"], "Two Rows make a 2-by-3 array."),
    C(T("typedef int Grid[$a][$b];", "Grid g;", PF("%zu", "sizeof(Grid) / sizeof g[0]")), lambda p: p["a"], "One row is g[0]; the whole over one row is the number of rows."),
    C(T("typedef uint8_t Grid[$a][$n];", PF("%zu", "sizeof(Grid)")), lambda p: p["a"] * p["n"], "a rows of n one-byte elements."),
    C(T("typedef char Name[$n];", 'Name s = "$w";', PF("%zu %zu", "sizeof(Name), strlen(s)")), lambda p: f"{p['n']} {p['L']}", "The typedef fixes the array at n bytes; the word only fills the start."),
    C(T("typedef const char *Str;", 'Str s = "$w";', PF("%zu", "strlen(s)")), lambda p: p["L"], "Str is a pointer to constant characters; strlen counts the word."),
    C(T("typedef int *IP;", "int x = $a;", "IP p = &x, q = &x;", PF("%d", "*p + *q")), lambda p: 2 * p["a"], "IP hides the *, so in IP p, q both p and q are pointers."),
    C(T("int x = $a;", "int *p = &x, q = $b;", PF("%d", "*p + q")), lambda p: p["a"] + p["b"], "The * belongs to p alone: q is a plain int."),
    C(T("typedef int *IP;", "int v[] = {$a, $b, $c};", "IP p = v;", PF("%d", "*(p + 2)")), lambda p: p["c"], "p points at the first element; +2 moves two elements on."),
    C(T("typedef struct { int x, y; } Pt;", "Pt p = {$a, $b};", PF("%d", "p.x * p.y")), lambda p: p["a"] * p["b"], "Pt is the struct type with members x and y."),
    C(T("typedef struct { int x, y; } Pt;", PF("%zu", "sizeof(Pt)")), 8, "Two ints of 4 bytes."),
    C(T("typedef struct { uint8_t r, g, b; } Rgb;", "Rgb c = {$a, $b, $c};", PF("%zu %d", "sizeof(Rgb), c.r + c.g + c.b")), lambda p: f"3 {p['a'] + p['b'] + p['c']}", "Three one-byte members, no padding; the sum is worked out in int."),
    C(T("typedef struct { int x, y; } Pt;", "Pt p = {$a, $b};", "Pt q = p;", "q.x = $c;", PF("%d %d", "p.x, q.x")), lambda p: f"{p['a']} {p['c']}", "Assigning a struct copies it: changing q leaves p alone."),
    C(T("typedef struct { int x, y; } Pt;", "void move(Pt p) { p.x += 5; }", "int main(void) {", "    Pt p = {$a, $b};", "    move(p);", PF("%d", "p.x"), "}"), lambda p: p["a"],
      "move gets a copy of the struct, so p in main is unchanged."),
    C(T("typedef struct { int x, y; } Pt;", "void move(Pt *p) { p->x += $b; }", "int main(void) {", "    Pt p = {$a, 0};", "    move(&p);", PF("%d", "p.x"), "}"), lambda p: p["a"] + p["b"],
      "move gets the address, so p->x changes main's struct."),
    C(T("typedef struct { int x, y; } Pt;", "Pt add(Pt a, Pt b) { Pt r = {a.x + b.x, a.y + b.y}; return r; }", "int main(void) {", "    Pt p = {$a, $b}, q = {$c, $d};", "    Pt r = add(p, q);",
        PF("%d %d", "r.x, r.y"), "}"), lambda p: f"{p['a'] + p['c']} {p['b'] + p['d']}", "A function can return a struct by value."),
    C(T("typedef struct { int x, y; } Pt;", "Pt pts[] = {{1, 2}, {3, 4}, {$a, $b}};", PF("%zu %d", "sizeof(pts) / sizeof(pts[0]), pts[2].y")), lambda p: f"3 {p['b']}", "Three Pt elements; the third one's y is b."),
    C(T("typedef struct { int x, y; } Pt;", "typedef struct { Pt a, b; } Line;", "Line l = {{$a, $b}, {$c, $d}};", PF("%d", "l.b.x - l.a.x")), lambda p: p["c"] - p["a"], "l.b.x reaches into the nested Pt."),
    C(T("typedef struct Node { int v; struct Node *next; } Node;", "int main(void) {", "    Node c = {$c, NULL}, b = {$b, &c}, a = {$a, &b};", "    int s = 0;",
        "    for (Node *p = &a; p; p = p->next)", "        s += p->v;", PF("%d", "s"), "}"), lambda p: p["a"] + p["b"] + p["c"], "The loop follows the next pointers from a to c, adding each v."),
    C(T("typedef struct Node { int v; struct Node *next; } Node;", "int main(void) {", "    Node c = {$c, NULL}, b = {$b, &c}, a = {$a, &b};", PF("%d", "a.next->next->v"), "}"), lambda p: p["c"], "Two steps along next lead from a to c."),
    C(T("typedef enum { RED, GREEN, BLUE } Color;", "Color c = BLUE;", PF("%d", "c == 2")), 1, "Color is the enum type; BLUE is 2."),
    C(T("typedef struct { int n; int (*f)(int); } Rule;", "int neg(int x) { return -x; }", "int main(void) {", "    Rule r = {$a, neg};", PF("%d", "r.f(r.n)"), "}"), lambda p: -p["a"],
      "A struct member can be a function pointer: r.f is neg."),
    C(T("typedef void (*Cb)(int *);", "void bump(int *p) { *p += $a; }", "void run(Cb f, int *p) { f(p); f(p); }", "int main(void) {", "    int x = $b;", "    run(bump, &x);", PF("%d", "x"), "}"),
      lambda p: p["b"] + 2 * p["a"], "run calls the callback twice on the same variable."),
    C(T("typedef int (*Cmp)(int, int);", "int lo(int a, int b) { return a < b ? a : b; }", "int hi(int a, int b) { return a > b ? a : b; }", "int main(void) {", "    Cmp pick[] = {lo, hi};",
        PF("%d", "pick[$r]($a, $b)"), "}"), lambda p: (max if p["r"] else min)(p["a"], p["b"]), "pick[0] is lo and pick[1] is hi."),
    C(T("typedef struct { int w, h; } Size;", "int area(Size s) { return s.w * s.h; }", "int main(void) {", "    Size s = {$a, $b};", PF("%d", "area(s)"), "}"), lambda p: p["a"] * p["b"], "area reads the two members of its copy."),
    C(T("typedef struct { int v[3]; } Box;", "Box b = {{$a, $b, $c}};", "Box c = b;", "c.v[0] = 0;", PF("%d %d", "b.v[0], c.v[0]")), lambda p: f"{p['a']} 0", "An array inside a struct is copied with the struct."),
    C(T("typedef struct { uint8_t lo, hi; } Pair;", "Pair p = {$a, $b};", PF("%d", "p.lo + p.hi * 256")), lambda p: p["a"] + 256 * p["b"], "Two byte members read as a 16-bit value: lo plus 256 times hi."),
    C(T("typedef int Vec[3];", "Vec v = {$a, $b, $c};", "int s = 0;", "for (size_t i = 0; i < sizeof(Vec) / sizeof(int); i++)", "    s += v[i];", PF("%d", "s")), lambda p: p["a"] + p["b"] + p["c"],
      "sizeof(Vec) / sizeof(int) is 3, so the loop adds all three elements."),
    C(T("typedef long long i64;", "i64 x = (i64)$big * $big;", PF("%lld", "x")), lambda p: p["big"] * p["big"], "i64 is long long, 64 bits wide, so the product fits."),
]
