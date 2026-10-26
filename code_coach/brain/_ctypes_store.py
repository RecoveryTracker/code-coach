"""C types and preprocessor pack, part 5: Recursion (`ct_recurse`) and Storage & Linkage (`ct_storage`).

Recursion is spelled out in Python with the same recursion (so call counts are counted by a Python counter, never read
from a run); storage is a closure over what the C keeps in `static` variables and globals. All programs are complete
(helper functions and globals before `main`). Linkage note: the oracle makes every file-level name `static` to link
several programs together (`c_oracle.isolate`), so an `extern` declaration only appears AFTER the definition it refers
to, or inside a function once the definition is visible. No template calls two functions with shared state in one
argument list.
"""

from __future__ import annotations

import random

from ._c_model import C, P
from ._ccore_numbers import T
from ._ccore_text import PF
from ._model import Maker, tmod
from .items import Item


def MAIN(*lines: str) -> tuple[str, ...]:
    return ("int main(void) {", *("    " + ln.lstrip() if not ln.startswith(" ") else ln for ln in lines), "}")


# ── Python twins of the C functions ─────────────────────────────────────

def fact(n: int) -> int:
    return 1 if n <= 1 else n * fact(n - 1)


def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib_calls(n: int) -> int:
    return 1 if n < 2 else 1 + fib_calls(n - 1) + fib_calls(n - 2)


def gcd(a: int, b: int) -> int:
    return a if b == 0 else gcd(b, tmod(a, b))


def dsum(n: int) -> int:
    return 0 if n == 0 else n % 10 + dsum(n // 10)


def power(b: int, e: int) -> int:
    return 1 if e == 0 else b * power(b, e - 1)


def rev(n: int, acc: int = 0) -> int:
    return acc if n == 0 else rev(n // 10, acc * 10 + n % 10)


def ack(m: int, n: int) -> int:
    if m == 0:
        return n + 1
    if n == 0:
        return ack(m - 1, 1)
    return ack(m - 1, ack(m, n - 1))


def collatz(n: int) -> int:
    return 0 if n == 1 else 1 + collatz(n // 2 if n % 2 == 0 else 3 * n + 1)


def paths(r: int, c: int) -> int:
    return 1 if r == 0 or c == 0 else paths(r - 1, c) + paths(r, c - 1)


def binom(n: int, k: int) -> int:
    if k > n:
        return 0
    return 1 if k == 0 or k == n else binom(n - 1, k - 1) + binom(n - 1, k)


def lucas(n: int) -> int:
    return 2 if n == 0 else (1 if n == 1 else lucas(n - 1) + lucas(n - 2))


def trib(n: int) -> int:
    return 1 if n < 3 else trib(n - 1) + trib(n - 2) + trib(n - 3)


def mccarthy(x: int) -> int:
    return x - 10 if x > 100 else mccarthy(mccarthy(x + 11))


def is_prime(n: int, d: int) -> int:
    if n < 2:
        return 0
    if d * d > n:
        return 1
    return 0 if n % d == 0 else is_prime(n, d + 1)


def ping(n: int) -> int:
    return 1 + pong(n - 1) if n else 0


def pong(n: int) -> int:
    return 2 + ping(n - 1) if n else 0


def droot(n: int) -> int:
    return n if n < 10 else droot(dsum(n))


def fastpow(b: int, e: int) -> int:
    if e == 0:
        return 1
    h = fastpow(b, e // 2)
    return h * h * b if e % 2 else h * h


def sp(*xs) -> str:
    return " ".join(str(x) for x in xs)


def _inout(n: int) -> str:
    if n == 0:
        return "0 0"
    return f"{n} " + _inout(n - 1) + f" {n}"


def _binary(n: int) -> str:
    return (_binary(n // 2) if n > 1 else "") + str(n % 2)


def _digits_in_order(n: int) -> str:
    return (_digits_in_order(n // 10) + " " if n >= 10 else "") + str(n % 10)


def _pal(rng: random.Random) -> Item:
    p = P(rng)
    w = p["w"]
    s = w + w[::-1][1:]
    if rng.random() < 0.5:
        s = ("z" if s[0] != "z" else "y") + s[1:]
    palindrome = s == s[::-1]
    prompt = T("int pal(const char *s, int i, int j) {", "    return i >= j ? 1 : s[i] == s[j] && pal(s, i + 1, j - 1);", "}",
               *MAIN(PF("%d", f'pal("{s}", 0, {len(s) - 1})')))
    return Item(prompt, "1" if palindrome else "0",
                "pal compares the outer letters and then the inner ones; the first mismatch makes the && false, and meeting in the middle is true.")


RECURSE: list[Maker] = [
    C(T("int f(int n) { return n <= 1 ? 1 : n * f(n - 1); }", *MAIN(PF("%d", "f($a)"))), lambda p: fact(p["a"]), "f(n) is n times f(n - 1) down to 1: the factorial."),
    C(T("int f(int n) { return n < 2 ? n : f(n - 1) + f(n - 2); }", *MAIN(PF("%d", "f($a)"))), lambda p: fib(p["a"]), "Each value is the sum of the two before it: 0, 1, 1, 2, 3, 5, 8..."),
    C(T("int calls = 0;", "int f(int n) {", "    calls++;", "    return n < 2 ? n : f(n - 1) + f(n - 2);", "}", *MAIN("    f($a);", PF("%d", "calls"))), lambda p: fib_calls(p["a"]),
      "Every call counts, including the two that each call makes: the count grows like the Fibonacci numbers themselves."),
    C(T("int calls = 0;", "int f(int n) {", "    calls++;", "    return n <= 1 ? 1 : n * f(n - 1);", "}", *MAIN("    f($a);", PF("%d", "calls"))), lambda p: p["a"],
      "One call per level: f(a), f(a-1) ... f(1)."),
    C(T("int g(int a, int b) { return b == 0 ? a : g(b, a % b); }", *MAIN(PF("%d", "g($n, $m)"))), lambda p: gcd(p["n"], p["m"]), "Euclid's rule: the gcd of a and b is the gcd of b and a % b, until b is 0."),
    C(T("int s(int n) { return n == 0 ? 0 : n % 10 + s(n / 10); }", *MAIN(PF("%d", "s($big)"))), lambda p: dsum(p["big"]), "The last digit plus the digit sum of the rest."),
    C(T("int p(int b, int e) { return e == 0 ? 1 : b * p(b, e - 1); }", *MAIN(PF("%d", "p($a, $h)"))), lambda p: power(p["a"], p["h"]), "b to the e is b times b to the e - 1, ending at 1."),
    C(T("int r(int n, int acc) { return n == 0 ? acc : r(n / 10, acc * 10 + n % 10); }", *MAIN(PF("%d", "r($u, 0)"))), lambda p: rev(p["u"]), "Each last digit is moved onto the end of the answer being built: the number reversed."),
    C(T("int s(int n) { return n == 0 ? 0 : n + s(n - 1); }", *MAIN(PF("%d", "s($n)"))), lambda p: p["n"] * (p["n"] + 1) // 2, "n + (n-1) + ... + 1."),
    C(T("int d(int n) { return n < 10 ? 1 : 1 + d(n / 10); }", *MAIN(PF("%d", "d($big)"))), lambda p: len(str(p["big"])), "Each call drops one digit and counts it."),
    C(T("int A(int m, int n) {", "    if (m == 0) return n + 1;", "    if (n == 0) return A(m - 1, 1);", "    return A(m - 1, A(m, n - 1));", "}", *MAIN(PF("%d", "A(1, $a)"))),
      lambda p: ack(1, p["a"]), "Ackermann with m = 1 is n + 2."),
    C(T("int A(int m, int n) {", "    if (m == 0) return n + 1;", "    if (n == 0) return A(m - 1, 1);", "    return A(m - 1, A(m, n - 1));", "}", *MAIN(PF("%d", "A(2, $k)"))),
      lambda p: ack(2, p["k"]), "Ackermann with m = 2 is 2n + 3."),
    C(T("int odd(int);", "int even(int n) { return n == 0 ? 1 : odd(n - 1); }", "int odd(int n) { return n == 0 ? 0 : even(n - 1); }", *MAIN(PF("%d", "even($n)"))),
      lambda p: 1 if p["n"] % 2 == 0 else 0, "The two functions call each other, taking one off n each time: it ends on 0 in even or odd."),
    C(T("void down(int n) {", "    if (n == 0) return;", '    printf("%d ", n);', "    down(n - 1);", "}", *MAIN("    down($a);")), lambda p: sp(*range(p["a"], 0, -1)), "It prints on the way in, so the numbers come out counting down."),
    C(T("void up(int n) {", "    if (n == 0) return;", "    up(n - 1);", '    printf("%d ", n);', "}", *MAIN("    up($a);")), lambda p: sp(*range(1, p["a"] + 1)), "It prints after the deeper call returns, so the numbers come out counting up."),
    C(T("void f(int n) {", '    printf("%d ", n);', "    if (n > 0) f(n - 1);", '    printf("%d ", n);', "}", *MAIN("    f($k);")), lambda p: _inout(p["k"]),
      "One print on the way in and one on the way out: the numbers go down to 0 and back up."),
    C(T("void b(int n) {", "    if (n > 1) b(n / 2);", '    printf("%d", n % 2);', "}", *MAIN("    b($n);")), lambda p: _binary(p["n"]), "The recursion reaches the top bit first, so the bits print from the most significant."),
    C(T("int h(int n) { return n == 0 ? 0 : 2 * h(n - 1) + 1; }", *MAIN(PF("%d", "h($a)"))), lambda p: 2 ** p["a"] - 1, "The Tower of Hanoi: n disks need 2n+1 moves of n-1: 2 to the n, minus 1."),
    C(T("int len(const char *s) { return *s ? 1 + len(s + 1) : 0; }", *MAIN(PF("%d", 'len("$w$z")'))), lambda p: len(p["w"]) + len(p["z"]), "Each call counts one letter and moves on, until the zero byte."),
    _pal,
    C(T("int mx(const int *a, int n) {", "    if (n == 1) return a[0];", "    int m = mx(a, n - 1);", "    return a[n - 1] > m ? a[n - 1] : m;", "}", *MAIN("    int v[] = {$a, $b, $c, $d};", PF("%d", "mx(v, 4)"))),
      lambda p: max(p["a"], p["b"], p["c"], p["d"]), "Each level compares its element with the biggest of all those before it."),
    C(T("int sum(const int *a, int n) { return n == 0 ? 0 : a[n - 1] + sum(a, n - 1); }", *MAIN("    int v[] = {$a, $b, $c, $d};", PF("%d", "sum(v, 4)"))),
      lambda p: p["a"] + p["b"] + p["c"] + p["d"], "The last element plus the sum of the rest."),
    C(T("int w(int r, int c) { return r == 0 || c == 0 ? 1 : w(r - 1, c) + w(r, c - 1); }", *MAIN(PF("%d", "w($k, $a)"))), lambda p: paths(p["k"], p["a"]), "The number of paths across a grid: the sum of the paths from the square above and the square to the left."),
    C(T("int c(int n, int k) {", "    if (k > n) return 0;", "    return k == 0 || k == n ? 1 : c(n - 1, k - 1) + c(n - 1, k);", "}", *MAIN(PF("%d", "c($a, $k)"))),
      lambda p: binom(p["a"], p["k"]), "Pascal's rule: each entry is the two above it added."),
    C(T("int steps(int n) { return n == 1 ? 0 : 1 + steps(n % 2 ? 3 * n + 1 : n / 2); }", *MAIN(PF("%d", "steps($a)"))), lambda p: collatz(p["a"]), "Odd: 3n + 1, even: n / 2; count the steps to 1."),
    C(T("int q(int n) { return n == 0 ? 0 : n * n + q(n - 1); }", *MAIN(PF("%d", "q($a)"))), lambda p: sum(i * i for i in range(1, p["a"] + 1)), "n squared plus the sum of the squares below."),
    C(T("int lg(int n) { return n <= 1 ? 0 : 1 + lg(n / 2); }", *MAIN(PF("%d", "lg($n)"))), lambda p: p["n"].bit_length() - 1, "Halving until 1: how many times."),
    C(T("int l(int n) { return n == 0 ? 2 : n == 1 ? 1 : l(n - 1) + l(n - 2); }", *MAIN(PF("%d", "l($a)"))), lambda p: lucas(p["a"]), "Like Fibonacci but starting 2, 1: 2, 1, 3, 4, 7, 11..."),
    C(T("int t(int n) { return n < 3 ? 1 : t(n - 1) + t(n - 2) + t(n - 3); }", *MAIN(PF("%d", "t($a)"))), lambda p: trib(p["a"]), "Each value adds the three before it: 1, 1, 1, 3, 5, 9..."),
    C(T("int s(int n) { return n <= 0 ? 0 : (n % 2 ? n : 0) + s(n - 1); }", *MAIN(PF("%d", "s($n)"))), lambda p: sum(i for i in range(1, p["n"] + 1) if i % 2), "Only the odd numbers up to n are added."),
    C(T("void d(int n, int *depth) {", "    if (n > 0) { (*depth)++; d(n / 2, depth); }", "}", *MAIN("    int k = 0;", "    d($n, &k);", PF("%d", "k"))),
      lambda p: p["n"].bit_length(), "k counts the levels: n is halved until it reaches 0."),
    C(T("void r(const char *s) {", "    if (*s) {", "        r(s + 1);", "        printf(\"%c\", *s);", "    }", "}", *MAIN('    r("$w");')), lambda p: p["w"][::-1], "It prints after the deeper call returns, so the last letter comes out first."),
    C(T("void f(const char *s) {", "    if (*s) {", "        printf(\"%c\", *s);", "        f(s + 1);", "    }", "}", *MAIN('    f("$w");')), lambda p: p["w"], "It prints on the way in, so the letters come out in order."),
    C(T("void f(char c) {", "    if (c > 'a') f(c - 1);", "    printf(\"%c\", c);", "}", *MAIN("    f('a' + $a);")), lambda p: "".join(chr(97 + i) for i in range(p["a"] + 1)), "It recurses down to 'a' first and prints on the way back: the letters in order."),
    C(T("int f(int n) { return n == 0 ? 0 : f(n - 1) + $a; }", *MAIN(PF("%d", "f($b)"))), lambda p: p["a"] * p["b"], "Each level adds a, and there are b levels."),
    C(T("int f(int n, int acc) { return n <= 1 ? acc : f(n - 1, acc * n); }", *MAIN(PF("%d", "f($a, 1)"))), lambda p: fact(p["a"]), "The product is carried along in acc, so the last call has the answer ready."),
    C(T("int f(int x) { return x > 100 ? x - 10 : f(f(x + 11)); }", *MAIN(PF("%d", "f($m)"))), lambda p: mccarthy(p["m"]), "McCarthy's 91 function: every start up to 100 ends at 91."),
    C(T("int mul(int a, int b) { return b == 0 ? 0 : a + mul(a, b - 1); }", *MAIN(PF("%d", "mul($a, $b)"))), lambda p: p["a"] * p["b"], "Multiplication as repeated addition."),
    C(T("int f(int n) { return n == 0 ? 0 : (n % 3 == 0) + f(n - 1); }", *MAIN(PF("%d", "f($n)"))), lambda p: p["n"] // 3, "Every multiple of 3 up to n adds 1."),
    C(T("int p(int n, int d) {", "    if (n < 2) return 0;", "    if (d * d > n) return 1;", "    return n % d == 0 ? 0 : p(n, d + 1);", "}", *MAIN(PF("%d", "p($m, 2)"))), lambda p: is_prime(p["m"], 2), "Try divisors d = 2, 3, ... while d * d <= n; any exact divisor makes it not prime."),
    C(T("int pong(int);", "int ping(int n) { return n ? 1 + pong(n - 1) : 0; }", "int pong(int n) { return n ? 2 + ping(n - 1) : 0; }", *MAIN(PF("%d", "ping($a)"))), lambda p: ping(p["a"]), "ping and pong take turns adding 1 and 2."),
    C(T("int ds(int n) { return n == 0 ? 0 : n % 10 + ds(n / 10); }", "int dr(int n) { return n < 10 ? n : dr(ds(n)); }", *MAIN(PF("%d", "dr($big)"))), lambda p: droot(p["big"]), "Add the digits again and again until one digit is left."),
    C(T("int pw(int b, int e) {", "    if (e == 0) return 1;", "    int h = pw(b, e / 2);", "    return e % 2 ? h * h * b : h * h;", "}", *MAIN(PF("%d", "pw($a, $h)"))), lambda p: fastpow(p["a"], p["h"]), "Square the half-power, and multiply by b once more if e is odd."),
    C(T("int f(int n) { return n == 0 ? 1 : f(n - 1) + f(n - 1); }", *MAIN(PF("%d", "f($a)"))), lambda p: 2 ** p["a"], "Every level doubles the answer of the one below."),
    C(T("void pd(int n) {", "    if (n >= 10) pd(n / 10);", '    printf("%d ", n % 10);', "}", *MAIN("    pd($u);")), lambda p: _digits_in_order(p["u"]), "The recursion reaches the first digit before anything prints, so the digits come in order."),
]


# ── 2. Storage & Linkage ────────────────────────────────────────────────

STORAGE: list[Maker] = [
    C(T("int next(void) { static int n = $a; return n++; }", *MAIN("    for (int i = 0; i < 3; i++)", '        printf("%d ", next());')), lambda p: sp(p["a"], p["a"] + 1, p["a"] + 2),
      "The static n is set up once and keeps its value between calls."),
    C(T("int add(int x) { static int t; t += x; return t; }", *MAIN("    add($a);", "    add($b);", PF("%d", "add($c)"))), lambda p: p["a"] + p["b"] + p["c"], "The static t starts at 0 and adds up over the three calls."),
    C(T("int hit(int i) { static int c[3]; return ++c[i]; }", *MAIN("    hit(0);", "    hit(0);", "    hit(1);", "    int x = hit(0);", "    int y = hit(1);", PF("%d %d", "x, y"))), "3 2", "Each element of the static array counts its own calls."),
    C(T("int f(void) { static int n = $a * 2; return n--; }", *MAIN("    f();", "    f();", PF("%d", "f()"))), lambda p: p["a"] * 2 - 2, "The initializer runs once, then each call hands out n and counts it down."),
    C(T("int f(int n) {", "    static int depth = 0;", "    depth++;", "    if (n > 0) f(n - 1);", "    return depth;", "}", *MAIN(PF("%d", "f($a)"))), lambda p: p["a"] + 1,
      "All the levels share one depth: it reaches a+1 before the outer call returns it."),
    C(T("static int total;", "void add(int x) { total += x; }", "void sub(int x) { total -= x; }", *MAIN("    add($a);", "    add($b);", "    sub($c);", PF("%d", "total"))), lambda p: p["a"] + p["b"] - p["c"],
      "A file-level static is one variable that both functions share, starting at 0."),
    C(T("int g[5] = {$a, $b};", *MAIN("    int s = 0;", "    for (int i = 0; i < 5; i++)", "        s += g[i];", PF("%d", "s"))), lambda p: p["a"] + p["b"], "The elements without an initializer are 0."),
    C(T("int g[$n];", *MAIN(PF("%d", "g[$a] + $b"))), lambda p: p["b"], "A global array starts as all zeros."),
    C(T("struct P { int x, y; };", "struct P g;", *MAIN(PF("%d", "g.x + g.y + $a"))), lambda p: p["a"], "A global struct starts as all zeros."),
    C(T("char buf[8];", *MAIN(PF("%zu", "strlen(buf) + $a"))), lambda p: p["a"], "A global char array is all zero bytes, so it is an empty string."),
    C(T("int twice(int);", *MAIN(PF("%d", "twice($a)")), "int twice(int x) { return 2 * x; }"), lambda p: 2 * p["a"], "The prototype tells the compiler about twice, so main may call it before its definition."),
    C(T("int counter = $a;", "void bump(void) {", "    extern int counter;", "    counter += 2;", "}", *MAIN("    bump();", "    bump();", PF("%d", "counter"))), lambda p: p["a"] + 4,
      "extern in the function names the file's counter: it is the same variable, not a new one."),
    C(T("int g = $a;", "extern int g;", *MAIN(PF("%d", "g"))), lambda p: p["a"], "extern only declares: it names the g that is defined above."),
    C(T("int g = $a;", *MAIN("    int *p = &g;", "    int g = $b;", PF("%d %d", "g, *p"))), lambda p: f"{p['b']} {p['a']}", "The local g hides the global one, but p was taken before it and still points at the global."),
    C(T("int n = $a;", "int f(void) { static int n = $b; return ++n; }", *MAIN("    f();", "    int r = f();", PF("%d %d", "r, n"))), lambda p: f"{p['b'] + 2} {p['a']}", "The static n inside f hides the global n only in f."),
    C(T("int toggle(void) { static int on; on = !on; return on; }", *MAIN("    int r = 0;", "    for (int i = 0; i < $a; i++)", "        r = toggle();", PF("%d", "r"))), lambda p: p["a"] % 2, "The static on flips each call: 1, 0, 1, 0..."),
    C(T("int best(int x) {", "    static int m;", "    if (x > m) m = x;", "    return m;", "}", *MAIN("    best($a);", "    best($b);", PF("%d", "best($c)"))), lambda p: max(p["a"], p["b"], p["c"]), "The static m remembers the biggest value seen so far (it starts at 0)."),
    C(T("int first(int x) {", "    static int v = 0;", "    if (v == 0) v = x;", "    return v;", "}", *MAIN("    first($a);", PF("%d", "first($b)"))), lambda p: p["a"], "Only the first call finds v still 0, so only it stores its value."),
    C(T("int f(int n) {", "    static int memo[20];", "    if (n < 2) return n;", "    if (memo[n]) return memo[n];", "    return memo[n] = f(n - 1) + f(n - 2);", "}", *MAIN(PF("%d", "f($a)"))), lambda p: fib(p["a"]),
      "The static array remembers answers between (and inside) calls, so the result is just the Fibonacci number."),
    C(T(*MAIN("    for (int i = 0; i < 3; i++) {", "        static int s = 0;", "        int a = 0;", "        s += $a;", "        a += $a;", '        printf("%d,%d ", s, a);', "    }")),
      lambda p: sp(*[f"{p['a'] * (i + 1)},{p['a']}" for i in range(3)]), "The static s keeps growing across the turns; the ordinary a starts again at 0 each turn."),
    C(T("int *slot(void) {", "    static int v;", "    return &v;", "}", *MAIN("    *slot() = $a;", "    *slot() += $b;", PF("%d", "*slot()"))), lambda p: p["a"] + p["b"], "Every call returns the address of the same static v."),
    C(T("int *slot(void) {", "    static int v;", "    return &v;", "}", *MAIN(PF("%d", "slot() == slot()"))), 1, "Both calls return the address of the one static v."),
    C(T("int c(void) { static int c = 0; return ++c; }", *MAIN("    int a = c();", "    int b = c();", PF("%d %d", "b, a"))), "2 1", "The static counter keeps going: the first call gives 1 and the second 2."),
    C(T("static int calls;", "void hello(void) { calls++; }", *MAIN("    for (int i = 0; i < $a; i++)", "        hello();", PF("%d", "calls * 2"))), lambda p: 2 * p["a"], "calls starts at 0 and hello adds 1 per call."),
    C(T("int total(int n) {", "    static int sum;", "    sum += n;", "    return n ? total(n - 1) : sum;", "}", *MAIN(PF("%d", "total($a)"))), lambda p: p["a"] * (p["a"] + 1) // 2, "The static sum is shared by all levels and ends as a + (a-1) + ... + 0."),
    C(T("const char *flip(void) {", "    static int on;", "    on = !on;", '    return on ? "on" : "off";', "}", *MAIN("    const char *s = \"\";", "    for (int i = 0; i < $a; i++) s = flip();", PF("%s", "s"))),
      lambda p: "on" if p["a"] % 2 else "off", "The static on flips every call, starting from off, so an odd number of calls ends on."),
    C(T("const int sq[] = {1, 4, 9, 16};", *MAIN(PF("%d", "sq[$k] + sq[0]"))), lambda p: [1, 4, 9, 16][p["k"]] + 1, "A const array is read like any other: sq[k] + 1."),
    C(T('static const char *days[] = {"mon", "tue", "wed"};', *MAIN(PF("%zu %zu", "sizeof days / sizeof days[0], strlen(days[$q])"))), "3 3", "Three entries, and each three-letter name has length 3."),
    C(T("int g = $a;", "int h = 2 * 5;", *MAIN(PF("%d", "g + h"))), lambda p: p["a"] + 10, "Globals are initialised with constant expressions before main starts."),
    C(T("int g = $a;", "void f(void) { g *= 2; }", *MAIN("    f();", "    f();", PF("%d", "g"))), lambda p: p["a"] * 4, "Both calls change the one global g."),
    C(T("int pick(void) {", "    static int i;", "    static const int v[] = {$a, $b, $c};", "    return v[i++ % 3];", "}",
        *MAIN("    for (int k = 0; k < 4; k++)", '        printf("%d ", pick());')), lambda p: sp(p["a"], p["b"], p["c"], p["a"]), "The static i remembers the position, so the list is read round and round."),
    C(T("int x = $a;", "int f(int x) { return x + 1; }", *MAIN("    int r = f($b);", PF("%d", "r + x"))), lambda p: p["b"] + 1 + p["a"], "Inside f the parameter x hides the global; main still sees the global x."),
    C(T("int sum3(void) {", "    static int v[3];", "    int s = v[0] + v[1] + v[2];", "    v[0] += $a;", "    return s;", "}",
        *MAIN("    sum3();", PF("%d", "sum3()"))), lambda p: p["a"], "The static array starts as zeros; the first call leaves a in v[0], the second call sums it."),
    C(T("int g[$n];", "size_t count(void) { g[0] = 1; return sizeof g / sizeof g[0]; }", *MAIN(PF("%zu", "count()"))), lambda p: p["n"], "g is a real array in scope, not a pointer, so sizeof sees all of it."),
    C(T("const int N = $a;", *MAIN("    int c = 0;", "    for (int i = 0; i < N; i++)", "        c += 2;", PF("%d", "c"))), lambda p: 2 * p["a"], "A const global is a variable that never changes: the loop runs a times."),
    C(T("int next_id(void) { static int id = $m; return id++; }", *MAIN("    next_id();", PF("%d", "next_id()"))), lambda p: p["m"] + 1, "The first call hands out m and leaves m + 1 for the second."),
    C(T("int g;", "void set(int v) { g = v; }", "int get(void) { return g; }", *MAIN("    set($a);", "    set($b);", PF("%d", "get()"))), lambda p: p["b"], "set writes the shared global and get reads it back: the last write wins."),
    # bool without stdbool.h
    C(T("#define bool _Bool", "#define true 1", "#define false 0", *MAIN("    bool a = true, b = true;", PF("%d", "a + b"))), 2, "true is 1, so the two bools add up to 2 (promoted to int first)."),
    C(T("#define bool _Bool", "#define true 1", *MAIN("    bool b = $n;", PF("%d", "b"))), 1, "Converting to _Bool gives 1 for anything nonzero."),
    C(T("#define bool _Bool", "#define true 1", *MAIN("    bool b = true;", "    b = b + $a;", PF("%d", "b"))), 1, "The sum is a number a + 1, but storing it in a bool makes it 1 again."),
    C(T("#define bool _Bool", "#define false 0", *MAIN("    bool b = false;", "    b = !b;", PF("%d", "b + b + $a"))), lambda p: 2 + p["a"], "!false is 1, so b + b is 2."),
    # compile-time checks
    C(T(*MAIN('    _Static_assert(sizeof(uint16_t) == 2, "uint16_t is 2 bytes");', PF("%d", "$a"))), lambda p: p["a"], "A _Static_assert that holds produces no code: the program just prints a."),
    C(T(*MAIN('    _Static_assert(sizeof(int[$a]) == 4 * $a, "int is 4 bytes");', "    int v[$a] = {0};", PF("%zu", "sizeof v / sizeof v[0]"))), lambda p: p["a"], "The check passes silently at compile time; v has a elements."),
]
