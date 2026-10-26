"""C core pack, part 3: Loop Trace, Operator Order and Scope & Storage.

Every answer is worked out by hand: a loop is simulated with a Python loop, a precedence question with the order
written out in brackets (`_c_model.py`), and tests/test_brain_packs.py compiles every template with the real compilers in
batches (tests/c_oracle.py). Prompts are the BODY of `main` unless they define `main` (then a complete program with helper
functions and globals); both print their own answer. No template relies on an unspecified order of evaluation or an
unsequenced modification: independent calls are only ever ordered by `&&`, `||`, `?:` or the comma.
"""

from __future__ import annotations

from ._c_model import C, fixed
from ._ccore_numbers import T
from ._ccore_text import PF
from ._model import Maker, tdiv, tmod


def seq(values) -> str:
    return " ".join(str(v) for v in values)


# ── 1. Loop Trace ───────────────────────────────────────────────────────

def _sum_to(n: int) -> int:
    s = 0
    for i in range(1, n + 1):
        s += i
    return s


def _collatz(n: int) -> int:
    steps = 0
    while n != 1:
        n = 3 * n + 1 if n % 2 else n // 2
        steps += 1
    return steps


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, tmod(a, b)
    return a


def _fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _two_pointer(n: int) -> tuple[int, int]:
    i, j = 0, n
    while i < j:
        i += 1
        j -= 1
    return i, j


def _digits(n: int) -> list[int]:
    out = []
    while n:
        out.append(n % 10)
        n //= 10
    return out


LOOPS: list[Maker] = [
    C(T("int s = 0;", "for (int i = 1; i <= $n; i++)", "    s += i;", PF("%d", "s")), lambda p: _sum_to(p["n"]), "The loop adds 1, 2, 3 ... up to n."),
    C(T("int c = 0;", "for (int i = 0; i < $n; i += $a)", "    c++;", PF("%d", "c")), lambda p: len(range(0, p["n"], p["a"])), "i takes the values 0, a, 2a ... below n: count them."),
    C(T("int s = 0;", "for (int i = 0; i < $a; i++)", "    s += i * i;", PF("%d", "s")), lambda p: sum(i * i for i in range(p["a"])), "i runs from 0 up to a - 1 and the squares are added."),
    C(T("int p = 1;", "for (int i = 1; i <= $a; i++)", "    p *= i;", PF("%d", "p")), lambda p: _fact(p["a"]), "The loop multiplies 1 * 2 * 3 ... up to a."),
    C(T("for (int i = $a; i > 0; i -= $b)", '    printf("%d ", i);'), lambda p: seq(range(p["a"], 0, -p["b"])), "i counts down by b while it is above 0."),
    C(T("for (int i = 0; i < $a; i++)", '    printf("%d ", i * i);'), lambda p: seq(i * i for i in range(p["a"])), "i runs from 0 up to a - 1: its squares are printed."),
    C(T("int i;", "for (i = 0; i < $a; i++) {", "}", PF("%d", "i")), lambda p: p["a"], "The loop stops when i reaches a, so i is a afterwards."),
    C(T("int i;", "for (i = 0; i <= $a; i++) {", "}", PF("%d", "i")), lambda p: p["a"] + 1, "With <= the loop runs once more: it stops when i is a + 1."),
    C(T("int i = 0;", "while (i < $n)", "    i += $a;", PF("%d", "i")), lambda p: -(-p["n"] // p["a"]) * p["a"], "i grows by a until it is no longer below n: the first multiple of a that is n or more."),
    C(T("int n = $n, c = 0;", "while (n > 1) {", "    n /= 2;", "    c++;", "}", PF("%d", "c")), lambda p: p["n"].bit_length() - 1, "Halving until 1: the number of halvings."),
    C(T("int i = $a;", "do {", '    printf("%d ", i);', "    i += 2;", "} while (i < $a);"), lambda p: p["a"], "A do-while runs its body once before it tests the condition."),
    C(T("int i = 0;", "do", "    i++;", "while (i < $a);", PF("%d", "i")), lambda p: p["a"], "The body runs until i reaches a."),
    C(T("int i;", "for (i = 0; i < 100; i++)", "    if (i * i > $n)", "        break;", PF("%d", "i")), lambda p: next(i for i in range(100) if i * i > p["n"]), "The loop stops at the first i whose square is bigger than n."),
    C(T("int s = 0;", "for (int i = 1; i <= $n; i++) {", "    if (i % $a == 0)", "        continue;", "    s += i;", "}", PF("%d", "s")),
      lambda p: sum(i for i in range(1, p["n"] + 1) if i % p["a"]), "continue skips the multiples of a, so only the others are added."),
    C(T("for (int i = 1; i <= 12; i++)", "    if (i % $b == 0)", '        printf("%d ", i);'), lambda p: seq(i for i in range(1, 13) if i % p["b"] == 0), "Only the multiples of b are printed."),
    C(T("int c = 0;", "for (int i = 0; i < $a; i++)", "    for (int j = 0; j < $b; j++)", "        c++;", PF("%d", "c")), lambda p: p["a"] * p["b"], "The inner loop runs b times for each of the a outer turns."),
    C(T("int c = 0;", "for (int i = 0; i < $a; i++)", "    for (int j = 0; j <= i; j++)", "        c++;", PF("%d", "c")), lambda p: p["a"] * (p["a"] + 1) // 2, "The inner loop runs 1, 2, 3 ... times: a triangle."),
    C(T("int i, j;", "for (i = 0, j = $n; i < j; i++, j--)", "    ;", PF("%d %d", "i, j")), lambda p: seq(_two_pointer(p["n"])), "i goes up and j goes down until they meet."),
    C(T("int n = $a * 3, steps = 0;", "while (n != 1) {", "    n = n % 2 ? 3 * n + 1 : n / 2;", "    steps++;", "}", PF("%d", "steps")), lambda p: _collatz(p["a"] * 3), "Odd: 3n + 1, even: n / 2; count the steps to 1."),
    C(T("int n = $u * $a, s = 0;", "while (n) {", "    s += n % 10;", "    n /= 10;", "}", PF("%d", "s")), lambda p: sum(_digits(p["u"] * p["a"])), "% 10 takes the last digit, / 10 drops it: the loop adds the digits."),
    C(T("int n = $u, r = 0;", "while (n) {", "    r = r * 10 + n % 10;", "    n /= 10;", "}", PF("%d", "r")), lambda p: int("".join(str(d) for d in _digits(p["u"]))), "Each last digit becomes the next digit of r: the number is reversed."),
    C(T("int a = $n, b = $m;", "while (b) {", "    int t = b;", "    b = a % b;", "    a = t;", "}", PF("%d", "a")), lambda p: _gcd(p["n"], p["m"]), "Euclid's algorithm: the greatest common divisor."),
    C(T("int a = 0, b = 1;", "for (int i = 0; i < $n; i++) {", "    int t = a + b;", "    a = b;", "    b = t;", "}", PF("%d", "a")), lambda p: _fib(p["n"]), "The pair (a, b) walks along the Fibonacci numbers n steps."),
    C(T("int c = 0;", "for (uint8_t i = 250 + $q; i >= 250 + $q; i++)", "    c++;", PF("%d", "c")), lambda p: 256 - (250 + p["q"]),
      "i counts up to 255 and then wraps to 0, where the condition fails: the loop ends."),
    C(T("int i = 0;", "while (i++ < $a)", "    ;", PF("%d", "i")), lambda p: p["a"] + 1, "i++ < a tests, then adds 1 - also on the last, failing, test."),
    C(T("int i = 0;", "while (++i < $a)", "    ;", PF("%d", "i")), lambda p: p["a"], "++i < a adds 1 first, then tests."),
    C(T("int s = 0;", "for (int i = 0; i < $a; i++)", "    s += i % 2 ? i : -i;", PF("%d", "s")), lambda p: sum(i if i % 2 else -i for i in range(p["a"])), "Odd i are added and even i are subtracted."),
    C(T("int n = $n, c = 0;", "for (;;) {", "    n -= $a;", "    if (n < 0)", "        break;", "    c++;", "}", PF("%d", "c")), lambda p: p["n"] // p["a"], "How many times a can be taken from n without going below 0."),
    C(T("int s = 0;", "for (int i = $a; i < $n; i *= 2)", "    s += i;", PF("%d", "s")), lambda p: sum(_doubling(p["a"], p["n"])), "i doubles each turn: a, 2a, 4a ... while it is below n."),
    C(T("int c = 0;", "for (int i = 0; i < $n; i++)", "    if (i % $a == 0 && i % $b == 0)", "        c++;", PF("%d", "c")), lambda p: sum(1 for i in range(p["n"]) if i % p["a"] == 0 and i % p["b"] == 0), "i counts when it is a multiple of both, and 0 is one."),
    C(T("int i = 10;", "while (i > 0)", "    i -= $a;", PF("%d", "i")), lambda p: 10 - p["a"] * -(-10 // p["a"]), "The loop stops at the first i that is 0 or below."),
    C(T("for (int i = 0; i < 5; i++) {", "    if (i == $k + 1)", "        break;", '    printf("%d ", i);', "}"), lambda p: seq(range(p["k"] + 1)), "break leaves the loop when i reaches k + 1."),
    C(T("for (char c = 'a'; c < 'a' + $a; c++)", '    printf("%c", c);'), lambda p: "".join(chr(97 + i) for i in range(p["a"])), "c runs through the letters from a, a of them."),
    C(T('const char *s = "$w";', "for (int i = (int)strlen(s) - 1; i >= 0; i--)", '    printf("%c", s[i]);'), lambda p: p["w"][::-1], "The loop walks the word from the last letter to the first."),
    C(T("for (int i = 0; i < 3; i++)", "    for (int j = 0; j < 3; j++) {", "        if (j == i)", "            break;", '        printf("%d%d ", i, j);', "    }"), "10 20 21", "break only leaves the inner loop, and j stops before it reaches i."),
    C(T("int c = 0;", "for (int i = 0; i < $a; i++)", "    for (int j = i; j < $a; j++)", "        c++;", PF("%d", "c")), lambda p: p["a"] * (p["a"] + 1) // 2, "The inner loop runs a, a - 1 ... 1 times."),
    C(T("int i = 100;", "for (int i = 0; i < 3; i++) {", "}", PF("%d", "i")), 100, "The loop's own i is a different variable that ends with the loop."),
    C(T("int s = 0, i = 0;", "while (i < $n) {", "    i++;", "    if (i % $a)", "        continue;", "    s += i;", "}", PF("%d", "s")), lambda p: sum(i for i in range(1, p["n"] + 1) if i % p["a"] == 0), "Only the multiples of a get past the continue."),
    C(T("int x = $a;", "while (x < $n)", "    x = x * 2 + 1;", PF("%d", "x")), lambda p: _grow(p["a"], p["n"]), "x doubles and gains 1 until it is n or more."),
    C(T("unsigned u = $a;", "int c = 0;", "while (u-- > 0)", "    c++;", PF("%d %u", "c, u")), lambda p: f"{p['a']} 4294967295", "u-- > 0 tests, then subtracts: after the last test u is 0 and goes on to wrap around."),
    C(T("int n = 0;", "for (int i = 1; i < 100; i *= $a)", "    n++;", PF("%d", "n")), lambda p: len(_powers_below(p["a"], 100)), "i takes the values 1, a, a squared ... below 100."),
    C(T("int s = 0;", "for (int i = 0, j = $a; i < j; i++, j--)", "    s += j - i;", PF("%d", "s")), lambda p: _pair_sum(p["a"]), "i goes up and j down; each turn adds their difference."),
]


def _fact(n: int) -> int:
    out = 1
    for i in range(1, n + 1):
        out *= i
    return out


def _doubling(a: int, n: int) -> list[int]:
    out, i = [], a
    while i < n:
        out.append(i)
        i *= 2
    return out


def _grow(x: int, n: int) -> int:
    while x < n:
        x = x * 2 + 1
    return x


def _powers_below(a: int, limit: int) -> list[int]:
    out, i = [], 1
    while i < limit:
        out.append(i)
        i *= a
    return out


def _pair_sum(a: int) -> int:
    s, i, j = 0, 0, a
    while i < j:
        s += j - i
        i += 1
        j -= 1
    return s


# ── 2. Operator Order ───────────────────────────────────────────────────

CALL = ("int t(int x) {", '    printf("%d ", x);', "    return x;", "}")


def _t(*values) -> str:
    return seq(values)


ORDER: list[Maker] = [
    C(PF("%d", "$a & 1 == 1"), lambda p: p["a"] & (1 == 1), "== ranks above &, so it is a & (1 == 1), which is a & 1."),
    C(PF("%d", "$a | $b == $c"), lambda p: p["a"] | (p["b"] == p["c"]), "== ranks above |: b == c is 0 (they differ), so the answer is a | 0."),
    C(PF("%d", "$a == $b ^ $c"), lambda p: int(p["a"] == p["b"]) ^ p["c"], "== ranks above ^: (a == b) is 0, and 0 ^ c is c."),
    C(PF("%d", "$a < $b == $c"), lambda p: int(int(p["a"] < p["b"]) == p["c"]), "It is (a < b) == c: a 0 or a 1 is never equal to c."),
    C(PF("%d", "!$a == $b"), lambda p: int(int(not p["a"]) == p["b"]), "! binds tighter than ==: (!a) is 0, and 0 is not b."),
    C(PF("%d", "-$a % $b"), lambda p: tmod(-p["a"], p["b"]), "The unary minus goes first, then %; the remainder takes the sign of the left operand."),
    C(PF("%d", "-$a * -$b"), lambda p: p["a"] * p["b"], "Two negatives multiply to a positive."),
    C(PF("%d", "$n / $a * $b"), lambda p: tdiv(p["n"], p["a"]) * p["b"], "/ and * have the same rank: left to right."),
    C(PF("%d", "$a > $b ? $a : $b > $c ? $b : $c"), lambda p: p["a"] if p["a"] > p["b"] else (p["b"] if p["b"] > p["c"] else p["c"]), "?: groups from the right: a > b ? a : (b > c ? b : c)."),
    C(PF("%d", "$a < $b ? $b - $a : $a - $b"), lambda p: abs(p["a"] - p["b"]), "The condition picks which difference is worked out."),
    C(PF("%d", "$r ? $a : $b"), lambda p: p["a"] if p["r"] else p["b"], "A nonzero condition picks the first value, 0 the second."),
    C(PF("%d", "$n > $m ? 1 : 2 + 3"), lambda p: 1 if p["n"] > p["m"] else 5, "+ ranks above ?:, so the false branch is 2 + 3."),
    C(T("int x = ($a, $b, $c);", PF("%d", "x")), lambda p: p["c"], "The comma operator gives its last operand."),
    C(T("int x;", "x = $a, $b;", PF("%d", "x")), lambda p: p["a"], "= ranks above the comma, so x = a is done and b is thrown away."),
    C(T("int x;", "x = ($a, $b);", PF("%d", "x")), lambda p: p["b"], "The brackets make the comma operator the right side: x gets b."),
    C(T("int a, b, c;", "a = b = c = $d;", PF("%d", "a + b + c")), lambda p: 3 * p["d"], "Assignment groups from the right: all three get d."),
    C(T("int x = $a;", "int y = x++ + $b;", PF("%d %d", "x, y")), lambda p: f"{p['a'] + 1} {p['a'] + p['b']}", "x++ gives the old value of x, then x grows."),
    C(T("int x = $a;", "int y = ++x * $b;", PF("%d %d", "x, y")), lambda p: f"{p['a'] + 1} {(p['a'] + 1) * p['b']}", "++x grows first and gives the new value."),
    C(T("int x = $a;", "int y = x-- - $b;", PF("%d %d", "x, y")), lambda p: f"{p['a'] - 1} {p['a'] - p['b']}", "x-- gives the old value of x, then x shrinks."),
    C(T("int x = $a, y = $b;", PF("%d", "x+++y")), lambda p: p["a"] + p["b"], "The scanner reads x++ + y: x is added to y before it grows."),
    C(T("int x = $a;", "x *= $b + $c;", PF("%d", "x")), lambda p: p["a"] * (p["b"] + p["c"]), "The whole right side is worked out before *= multiplies."),
    C(T("int x = $n;", "x -= $b - $a;", PF("%d", "x")), lambda p: p["n"] - (p["b"] - p["a"]), "x -= e subtracts all of e: x - (b - a)."),
    C(T("int x = $n;", "x /= $a + 1;", PF("%d", "x")), lambda p: tdiv(p["n"], p["a"] + 1), "x /= e divides by all of e, cutting the fraction."),
    C(T("int c = 0;", "int r = $a > $b || ++c > 0;", PF("%d %d", "r, c")), lambda p: "1 0" if p["a"] > p["b"] else "1 1", "|| skips the right side when the left is already true."),
    C(T("int c = 0;", "int r = $a > $b && ++c > 0;", PF("%d %d", "r, c")), lambda p: "1 1" if p["a"] > p["b"] else "0 0", "&& skips the right side when the left is already false."),
    C(T("int c = 0;", "int r = $r && ++c;", PF("%d %d", "r, c")), lambda p: "1 1" if p["r"] else "0 0", "The ++c only runs when the left side of && is true."),
    C(T("int c = 0;", "int r = $r || ++c;", PF("%d %d", "r, c")), lambda p: "1 0" if p["r"] else "1 1", "The ++c only runs when the left side of || is false."),
    C(T("int c = 0;", "int r = ++c || ++c;", PF("%d %d", "r, c")), "1 1", "The first ++c is true, so the second operand is never evaluated."),
    C(T("int c = 0;", "int r = (c = $a) && (c = $b);", PF("%d %d", "r, c")), lambda p: f"1 {p['b']}", "Both sides run (a is nonzero), so c ends as b."),
    C(T("int c = 0;", "int v = $r ? ++c : c--;", PF("%d %d", "v, c")), lambda p: "1 1" if p["r"] else "0 -1", "Only the chosen branch runs: ++c gives 1, c-- gives 0 and then c is -1."),
    C(T("int x = 0;", "if (x = $a)", '    printf("yes %d\\n", x);', "else", '    printf("no\\n");'), lambda p: f"yes {p['a']}", "x = a is an assignment, not a comparison: it gives a, which is true."),
    C(T("int x = $a;", "if (x = 0)", '    printf("yes\\n");', "else", '    printf("no %d\\n", x);'), "no 0", "x = 0 assigns 0 and gives 0, which is false: and x has been changed."),
    C(T("int a[] = {$a, $b, $c};", "int *p = a;", "int x = *p++ * 2;", PF("%d %d", "x, *p")), lambda p: f"{p['a'] * 2} {p['b']}", "*p++ reads where p points, then moves p; the * 2 applies to the value read."),
    C(T("int a[] = {$a, $b, $c};", "int *p = a;", "int x = (*p)++;", PF("%d %d", "x, a[0]")), lambda p: f"{p['a']} {p['a'] + 1}", "(*p)++ gives the old value and adds 1 to the element."),
    C(T("int a[] = {$a, $b, $c};", "int *p = a;", "++*p;", PF("%d %d", "a[0], *p")), lambda p: f"{p['a'] + 1} {p['a'] + 1}", "++*p adds 1 to the element p points at."),
    C(PF("%zu", "sizeof(int) * 2 + 1"), 9, "sizeof(int) is 4: 4 * 2 + 1."),
    C(PF("%d", "$a + $b == $c + $d"), lambda p: int(p["a"] + p["b"] == p["c"] + p["d"]), "The sums are worked out before the == compares them."),
    C(PF("%d", "$a * $b > $c + $d"), lambda p: int(p["a"] * p["b"] > p["c"] + p["d"]), "Arithmetic ranks above >, so both sides are worked out first."),
    C(PF("%d", "1 || 0 && 0"), 1, "&& ranks above ||: 1 || (0 && 0)."),
    C(PF("%d", "0 && 0 || 1"), 1, "&& ranks above ||: (0 && 0) || 1."),
    C(PF("%d", "(1 || 0) && 0"), 0, "The brackets force the || first: 1 && 0."),
    C(PF("%d", "!0 + !1"), 1, "! ranks above +: 1 + 0."),
    C(PF("%d", "!!$a"), 1, "!! turns any nonzero number into 1."),
    C(PF("%d", "~!$a"), -1, "!a is 0, and ~0 is all one-bits: -1."),
    C(PF("%d", "$a - -$b"), lambda p: p["a"] + p["b"], "Minus a negative number adds."),
    C(PF("%d", "$a + $b << $k"), lambda p: (p["a"] + p["b"]) << p["k"], "+ ranks above <<: (a + b) << k."),
    C(PF("%.2f", "(double)$n / $a"), lambda p: fixed(p["n"] / p["a"], 2), "The cast applies to n alone, so the division is done in double."),
    C(PF("%.2f", "(double)($n / $a)"), lambda p: fixed(float(tdiv(p["n"], p["a"])), 2), "The division is done in int and cut; only then is it made a double."),
    C(T(*CALL, "int main(void) {", "    if (t($a) > $b && t($c) > $d) {", "    }", "}"), lambda p: _t(p["a"]) if not p["a"] > p["b"] else (_t(p["a"], p["c"])), "&& stops as soon as the left side is false; the calls are in order."),
    C(T(*CALL, "int main(void) {", "    int r = t(0) || t($a) || t($b);", "    (void)r;", "}"), lambda p: _t(0, p["a"]), "|| stops at the first true operand: t(a) is true, so t(b) never runs."),
    C(T(*CALL, "int main(void) {", "    int r = t($a) && t(0) && t($b);", "    (void)r;", "}"), lambda p: _t(p["a"], 0), "&& stops at the first false operand: t(0)."),
    C(T(*CALL, "int main(void) {", "    int x = (t($a), t($b));", "    (void)x;", "}"), lambda p: _t(p["a"], p["b"]), "The comma operator runs its left operand first, then the right."),
    C(T(*CALL, "int main(void) {", "    int x = t($r) ? t($a) : t($b);", "    (void)x;", "}"), lambda p: _t(p["r"], p["a"]) if p["r"] else _t(p["r"], p["b"]), "The condition is evaluated first, then only one of the branches."),
]


# ── 3. Scope & Storage ──────────────────────────────────────────────────

def _calls(n: int) -> int:
    return 1 if n <= 1 else 1 + _calls(n - 1) + _calls(n - 2)


SCOPE: list[Maker] = [
    C(T("int x = $a;", "{", "    int x = $b;", "    x++;", "}", PF("%d", "x")), lambda p: p["a"], "The inner x is a different variable that ends with the block."),
    C(T("int x = $a;", "{", "    x = $b;", "}", PF("%d", "x")), lambda p: p["b"], "There is no new variable here: the block changes the outer x."),
    C(T("int x = $a;", "{", "    int x = $b;", '    printf("%d ", x);', "}", PF("%d", "x")), lambda p: f"{p['b']} {p['a']}", "Inside the block the inner x hides the outer one."),
    C(T("int x = $a;", "for (int i = 0; i < 3; i++) {", "    int x = i;", "    x++;", "}", PF("%d", "x")), lambda p: p["a"], "The x inside the loop body is a new variable each turn."),
    C(T("int i = $a;", "for (int i = 0; i < 3; i++) {", "}", PF("%d", "i")), lambda p: p["a"], "The loop's i hides the outer i and is gone after the loop."),
    C(T("for (int i = 0; i < 3; i++) {", "    static int n = $a;", "    n++;", '    printf("%d ", n);', "}"), lambda p: seq(p["a"] + 1 + i for i in range(3)), "A static local is set up once and keeps its value between turns."),
    C(T("for (int i = 0; i < 3; i++) {", "    int n = $a;", "    n++;", '    printf("%d ", n);', "}"), lambda p: seq([p["a"] + 1] * 3), "An ordinary local starts again from a each turn."),
    C(T("static int n;", "n += $a;", PF("%d", "n")), lambda p: p["a"], "A static variable starts as 0."),
    C(T("int x = $a;", "int *p = &x;", "*p = $b;", PF("%d", "x")), lambda p: p["b"], "p points at x, so writing through p changes x."),
    C(T("int x = $a, y = $b;", "int *p = &x;", "p = &y;", "*p = 0;", PF("%d %d", "x, y")), lambda p: f"{p['a']} 0", "p was moved to y before the write: x is untouched."),
    C(T("int x = $a;", "int *p = &x;", "int *q = p;", "*q = $b;", PF("%d", "*p")), lambda p: p["b"], "p and q point at the same x."),
    C(T("int x = $a;", "int y = x;", "y++;", PF("%d %d", "x, y")), lambda p: f"{p['a']} {p['a'] + 1}", "y is a copy: changing it leaves x alone."),
    C(T("int x = $a;", "if (x > 0) {", "    int x = -1;", '    printf("%d ", x);', "}", PF("%d", "x")), lambda p: f"-1 {p['a']}", "The x inside the if is new and hides the outer one."),
    C(T("int x = $a;", "int *p = &x;", "int **pp = &p;", "**pp = $b;", PF("%d", "x")), lambda p: p["b"], "**pp follows two pointers to x."),
    C(T("void inc(int x) {", "    x++;", "}", "int main(void) {", "    int a = $a;", "    inc(a);", '    printf("%d\\n", a);', "}"), lambda p: p["a"], "C passes a copy: inc changed its own x."),
    C(T("void inc(int *x) {", "    (*x)++;", "}", "int main(void) {", "    int a = $a;", "    inc(&a);", '    printf("%d\\n", a);', "}"), lambda p: p["a"] + 1, "inc gets the address of a, so it changes a itself."),
    C(T("void swap(int *p, int *q) {", "    int t = *p;", "    *p = *q;", "    *q = t;", "}", "int main(void) {", "    int a = $a, b = $b;", "    swap(&a, &b);", '    printf("%d %d\\n", a, b);', "}"), lambda p: f"{p['b']} {p['a']}", "swap writes through the addresses, so the values trade places."),
    C(T("void swap(int p, int q) {", "    int t = p;", "    p = q;", "    q = t;", "}", "int main(void) {", "    int a = $a, b = $b;", "    swap(a, b);", '    printf("%d %d\\n", a, b);', "}"), lambda p: f"{p['a']} {p['b']}", "swap trades its own copies: a and b are unchanged."),
    C(T("int g = $a;", "void f(void) {", "    g += $b;", "}", "int main(void) {", "    f();", "    f();", '    printf("%d\\n", g);', "}"), lambda p: p["a"] + 2 * p["b"], "g is a global: both calls add to the same variable."),
    C(T("int x = $a;", "void f(void) {", "    int x = $b;", "    x++;", "}", "int main(void) {", "    f();", '    printf("%d\\n", x);', "}"), lambda p: p["a"], "f's local x hides the global one: the global is untouched."),
    C(T("int next(void) {", "    static int n = $a;", "    return ++n;", "}", "int main(void) {", "    next();", "    next();", '    printf("%d\\n", next());', "}"), lambda p: p["a"] + 3, "The static n keeps its value between calls: three calls add 3."),
    C(T("int next(void) {", "    int n = $a;", "    return ++n;", "}", "int main(void) {", "    next();", "    next();", '    printf("%d\\n", next());', "}"), lambda p: p["a"] + 1, "An ordinary local starts again at a on every call."),
    C(T("int add(int x) {", "    static int total = 0;", "    total += x;", "    return total;", "}", "int main(void) {", "    add($a);", "    add($b);", '    printf("%d\\n", add($c));', "}"), lambda p: p["a"] + p["b"] + p["c"], "total is static, so it adds up across the three calls."),
    C(T("int calls = 0;", "int f(int n) {", "    calls++;", "    return n <= 1 ? 1 : f(n - 1) + f(n - 2);", "}", "int main(void) {", "    f($k + 2);", '    printf("%d\\n", calls);', "}"), lambda p: _calls(p["k"] + 2), "Every call, including the recursive ones, adds 1 to calls."),
    C(T("int fact(int n) {", "    return n <= 1 ? 1 : n * fact(n - 1);", "}", "int main(void) {", '    printf("%d\\n", fact($a));', "}"), lambda p: _fact(p["a"]), "fact(n) is n times fact(n - 1), down to 1."),
    C(T("int twice(int x) {", "    x *= 2;", "    return x;", "}", "int main(void) {", "    int a = $a;", "    int b = twice(a);", '    printf("%d %d\\n", a, b);', "}"), lambda p: f"{p['a']} {2 * p['a']}", "twice changes its own copy and returns it: a is unchanged."),
    C(T("void reset(int *p) {", "    p = NULL;", "}", "int main(void) {", "    int x = $a;", "    int *p = &x;", "    reset(p);", '    printf("%d\\n", *p);', "}"), lambda p: p["a"], "reset changes its own copy of the pointer, not main's p."),
    C(T("static int count;", "void hit(void) {", "    count++;", "}", "int main(void) {", "    for (int i = 0; i < $a; i++)", "        hit();", '    printf("%d\\n", count);', "}"), lambda p: p["a"], "count starts at 0 and hit adds 1 per call."),
    C(T("int a(void) { static int n; return ++n; }", "int b(void) { static int n; return n += 10; }", "int main(void) {", "    a();", "    b();", '    printf("%d %d\\n", a(), b());', "}"), "2 20", "Each function has its own static n."),
    C(T("void f(int *p) {", "    *p = $b;", "}", "int main(void) {", "    int a[] = {$a, $c};", "    f(&a[1]);", '    printf("%d %d\\n", a[0], a[1]);', "}"), lambda p: f"{p['a']} {p['b']}", "f writes through the address of the second element."),
    C(T("int f(int x) {", "    {", "        int x = $b;", "        x++;", "    }", "    return x + 1;", "}", "int main(void) {", '    printf("%d\\n", f($a));', "}"), lambda p: p["a"] + 1, "The inner x belongs to the block: the parameter x is untouched."),
    C(T("int *counter(void) {", "    static int n = $a;", "    return &n;", "}", "int main(void) {", "    (*counter())++;", "    (*counter())++;", '    printf("%d\\n", *counter());', "}"), lambda p: p["a"] + 2, "counter returns the address of the same static n each time."),
    C(T("int x = $a;", "int main(void) {", "    int x = $b;", '    printf("%d\\n", x);', "}"), lambda p: p["b"], "The local x in main hides the global x."),
    C(T("int n = 0;", "int next(void) {", "    return ++n;", "}", "int main(void) {", "    int s = 0;", "    for (int i = 0; i < $a; i++)", "        s += next();", '    printf("%d %d\\n", s, n);', "}"), lambda p: f"{p['a'] * (p['a'] + 1) // 2} {p['a']}", "next returns 1, 2, 3 ... and the global n counts the calls."),
    C(T("int x = $a;", "void f(void) {", "    x = $b;", "}", "int main(void) {", "    f();", '    printf("%d\\n", x);', "}"), lambda p: p["b"], "f assigns to the global x: there is no local here."),
    C(T("int g;", "int main(void) {", '    printf("%d\\n", g + $a);', "}"), lambda p: p["a"], "A global variable starts as 0."),
    C(T("int add(int a, int b) {", "    return a + b;", "}", "int main(void) {", "    int a = $a, b = $b;", "    a = add(a, b);", '    printf("%d %d\\n", a, b);', "}"), lambda p: f"{p['a'] + p['b']} {p['b']}", "The returned sum is assigned to a; b is unchanged."),
    C(T("void f(int x) {", "    x = $b;", "}", "int main(void) {", "    int x = $a;", "    f(x);", '    printf("%d\\n", x);', "}"), lambda p: p["a"], "The two x are different variables: f's x is a copy."),
    C(T("int a[] = {$a, $b};", "int *p = a;", "int *q = p + 1;", "*q = $c;", PF("%d %d", "a[0], a[1]")), lambda p: f"{p['a']} {p['c']}", "q points at the second element of a, so writing through q changes it."),
    C(T("int sq(int x) {", "    return x * x;", "}", "int main(void) {", "    int a = $a;", '    printf("%d %d\\n", sq(a), a);', "}"), lambda p: f"{p['a'] ** 2} {p['a']}", "sq works on a copy and returns the square; a is unchanged."),
    C(T("int sum(int n) {", "    return n == 0 ? 0 : n + sum(n - 1);", "}", "int main(void) {", '    printf("%d\\n", sum($n));', "}"), lambda p: p["n"] * (p["n"] + 1) // 2, "sum(n) is n plus sum(n - 1), down to sum(0), which is 0."),
    C(T("int depth(int n) {", "    static int most = 0;", "    if (n > most)", "        most = n;", "    return n > 0 ? depth(n - 1) : most;", "}", "int main(void) {", '    printf("%d\\n", depth($a));', "}"), lambda p: p["a"], "The static most is shared by every level of the recursion: it keeps the biggest n."),
    C(T("int x = $a;", "{", "    int y = x + $b;", "    x = y;", "}", PF("%d", "x")), lambda p: p["a"] + p["b"], "The block can see the outer x and changes it through y."),
]
