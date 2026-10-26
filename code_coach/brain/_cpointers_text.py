"""C pointers and structs pack, part 4: String Pointers (a `char *` into a char array or a literal) and Function Pointers
(tables, callbacks, a function that returns a function).

Strings are modelled with `cstr`/`text`/`Ptr` from `_cpointers_model.py` (a NUL-terminated list of codes, which refuses to
read past the end); function pointers are plain Python callables. A string literal is only ever READ (writing one is
undefined), and two string literals are never compared by address. Complete programs use every function they define
(a static function nobody calls is a compiler warning), and stay within the 220-character prompt.
"""

from __future__ import annotations

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._cpointers_model import Ptr, cstr, ints, slen, text
from ._model import Maker

MAIN = r'int main(void) {'


def _tail_from(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s) + p["i"]
    return f"{text(q)} {chr(q.get())}"


def _walk_len(p: dict) -> int:
    s = cstr(p["w"])
    q = Ptr(s)
    while q.get() != 0:
        q = q + 1
    return q - Ptr(s)


def _read_two(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s)
    c = q.get()
    q = q + 1
    return chr(c) + chr(q.get())


def _cut(p: dict) -> str:
    s = cstr(p["w"])
    s[p["i"]] = 0
    return f"{text(Ptr(s))} {slen(Ptr(s))}"


def _cut_past(p: dict) -> str:
    s = cstr(p["w"])
    s[p["i"]] = 0
    return "[" + text(Ptr(s) + (p["i"] + 1)) + "]" if p["i"] + 1 < len(s) else "[]"


def _cut_sizeof(p: dict) -> str:
    s = cstr(p["w"])
    s[p["i"]] = 0
    return ints(slen(Ptr(s)), len(s))


def _store_two(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s)
    q.set(ord("A"))
    q = q + 1
    q.set(ord("B"))
    return text(Ptr(s))


def _copy_loop(p: dict) -> str:
    src, dst = cstr(p["w"]), [0] * 10
    a, b = Ptr(src), Ptr(dst)
    while True:
        c = a.get()
        a = a + 1
        b.set(c)
        b = b + 1
        if c == 0:
            break
    return text(Ptr(dst))


def _reverse(p: dict) -> str:
    s = cstr(p["w"])
    i, j = Ptr(s), Ptr(s) + (len(p["w"]) - 1)
    while i < j:
        t = i.get()
        i.set(j.get())
        j.set(t)
        i, j = i + 1, j - 1
    return text(Ptr(s))


def _count_letter(p: dict) -> int:
    return p["w"].count(p["f"])


def _upper(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s)
    while q.get() != 0:
        q.set(q.get() - 32)
        q = q + 1
    return text(Ptr(s))


def _index_of(p: dict) -> int:
    return p["w"].index(p["f"])


def _last_of(p: dict) -> str:
    return p["w"][p["w"].rindex(p["f"]):]


def _toggle(p: dict) -> str:
    s = cstr(p["w"])
    s[p["j"]] ^= 32
    return text(Ptr(s))


def _star(p: dict) -> str:
    return p["w"].replace(p["f"], "*")


def _vowels(p: dict) -> int:
    return sum(1 for c in p["w"] if c in "aeiou")


def _after_nul(p: dict) -> str:
    s = cstr(p["w"])
    s[1] = 0
    return f"{text(Ptr(s))}|{text(Ptr(s) + 2)}"


def _swap_ends(p: dict) -> str:
    s = cstr(p["w"])
    i, j = Ptr(s), Ptr(s) + (len(p["w"]) - 1)
    t = i.get()
    i.set(j.get())
    j.set(t)
    return text(Ptr(s))


def _rev_print(p: dict) -> str:
    return p["w"][::-1]


def _tail_tail(p: dict) -> str:
    return "[" + p["w"][2:] + "]"


def _tail_from_c(p: dict) -> str:
    return f"{p['w'][p['i']]} {p['w'][p['i']:]}"


def _rest_from_first(p: dict) -> str:
    return p["w"][p["w"].index(p["f"]):]


# ── 7. String Pointers ──────────────────────────────────────────────────

STR: list[Maker] = [
    C(T(r'char s[] = "$w";', r'char *p = s;', PF("%c", "p[$j]")), lambda p: p["w"][p["j"]],
      "p points at the first character, and p[j] is the character j places on."),
    C(T(r'char s[] = "$w";', r'char *p = s + $i;', PF("%s %c", "p, *p")), _tail_from,
      "%s starts printing where p points and runs to the NUL; *p is the character p points at."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r'while (*p)', r'    p++;', PF("%d", "(int)(p - s)")), _walk_len,
      "p stops on the NUL, so p - s is the number of characters before it."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r'char c = *p++;', PF("%c%c", "c, *p")), _read_two,
      "*p++ reads the first character and moves p to the second."),
    C(T(r'char s[] = "$w";', r"s[$i] = '\0';", PF("%s %zu", "s, strlen(s)")), _cut,
      "A NUL written into the middle ends the string there: the rest is still in the array, but unseen."),
    C(T(r'char s[] = "$w";', r"s[$i] = '\0';", PF("[%s]", "s + $i + 1")), _cut_past,
      "The characters after the NUL are untouched; starting just past it prints them."),
    C(T(r'char s[] = "$w";', r"s[$i] = '\0';", PF("%zu %zu", "strlen(s), sizeof s")), _cut_sizeof,
      "strlen stops at the new NUL; sizeof is still the size of the whole array."),
    C(T(r'const char *p = "$w";', r'p += $i;', PF("%c %s", "*p, p")), _tail_from_c,
      "p moves along the literal; it only reads, so a literal is fine."),
    C(T(r'const char *p = "$w";', r'int n = 0;', r'while (*p++)', r'    n++;', PF("%d", "n")), lambda p: len(p["w"]),
      "The test reads each character and moves on; n counts the ones that were not NUL."),
    C(T(r'char d[10];', r'const char *s = "$w";', r'char *q = d;', r'while ((*q++ = *s++))', r'    ;', PF("%s", "d")), _copy_loop,
      "The assignment copies a character and its value is the test: the NUL is copied, then the loop ends."),
    C(T(r'void cp(char *d, const char *s) { while ((*d++ = *s++)); }', MAIN, r'    char d[10];', r'    cp(d, "$w");', r'    printf("%s\n", d);', r'}'),
      lambda p: p["w"], "cp is strcpy: it copies up to and including the NUL."),
    C(T(r'int cnt(const char *s, char c) { int n = 0; for (; *s; s++) if (*s == c) n++; return n; }', MAIN,
        r'''    printf("%d\n", cnt("$w", '$f'));''', r'}'), _count_letter,
      "cnt walks its pointer along the string and counts the matches."),
    C(T(r'char s[] = "$w";', r'for (char *p = s; *p; p++)', r'    *p -= 32;', PF("%s", "s")), _upper,
      "Each lower-case letter is turned into its capital by subtracting 32, in place."),
    C(T(r'char s[] = "$w";', r'char *i = s, *j = s + strlen(s) - 1;', r'while (i < j) {', r'    char t = *i; *i = *j; *j = t;', r'    i++; j--;', r'}',
        PF("%s", "s")), _reverse, "Two pointers swap characters and move inward: the word is reversed."),
    C(T(r'char s[] = "$w";', PF("%d", "(int)(strchr(s, \'$f\') - s)")), _index_of,
      "strchr returns a pointer to the first match; subtracting s gives its index."),
    C(T(r'char s[] = "$w";', PF("%s", "strchr(s, \'$f\')")), _rest_from_first,
      "strchr gives a pointer to the first match, and %s prints from there to the end."),
    C(T(r'char s[] = "$w";', PF("%s", "strrchr(s, \'$f\')")), _last_of,
      "strrchr searches from the end: the LAST match, and the rest of the string."),
    C(T(r'char s[] = "$w";', PF("%d", "strchr(s, \'7\') == NULL")), 1, "No 7 in the word, so strchr returns a null pointer."),
    C(T(r'char s[] = "$w";', PF("%zu", "strlen(s + $i)")), lambda p: len(p["w"]) - p["i"],
      "s + i is a string that starts i characters in: it is i shorter."),
    C(T(r'char s[] = "$w";', PF("%zu", "strlen(&s[$i]) + $i")), lambda p: len(p["w"]), "&s[i] is s + i: the rest plus the i skipped is the whole word."),
    C(T(r'char s[] = "$w";', r'char *p = s, *q = s + $i;', PF("%d", "(int)(q - p)")), lambda p: p["i"],
      "Two pointers into one array: q - p counts the characters between them."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r'p += strlen(p) - 1;', PF("%c", "*p")), lambda p: p["w"][-1],
      "strlen(p) - 1 is the index of the last character."),
    C(T(r'char s[] = "$w";', r's[0] = s[$L - 1];', PF("%s", "s")), lambda p: p["w"][-1] + p["w"][1:],
      "The last letter is copied over the first one."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r"*p++ = 'A';", r"*p = 'B';", PF("%s", "s")), _store_two,
      "Two stores: the first character and then the second become A and B."),
    C(T(r'char buf[16] = "$w";', r'strcat(buf, "$z");', PF("%s %zu", "buf, strlen(buf)")), lambda p: f"{p['w']}{p['z']} {len(p['w']) + len(p['z'])}",
      "strcat walks to the NUL of buf and copies the second word from there."),
    C(T(r'char s[] = "   $w";', r'char *p = s;', r"while (*p == ' ')", r'    p++;', PF("[%s] %d", "p, (int)(p - s)")), lambda p: f"[{p['w']}] 3",
      "p skips the three spaces and then points at the word."),
    C(T(r'char s[] = "$w-$z";', r"char *d = strchr(s, '-');", r"*d = '\0';", PF("%s %s", "s, d + 1")), lambda p: f"{p['w']} {p['z']}",
      "Overwriting the dash with a NUL cuts one string into two: s and the one after the dash."),
    C(T(r'const char *p = "$n";', r'int v = 0;', r'while (*p)', r"    v = v * 10 + (*p++ - '0');", PF("%d", "v")), lambda p: p["n"],
      "Each digit character minus '0' is its value; v shifts left one decimal place per digit."),
    C(T(r'const char *p = "$big";', r'int v = 0;', r'while (*p)', r"    v = v * 10 + (*p++ - '0');", PF("%d", "v")), lambda p: p["big"],
      "The same digit-by-digit conversion, for a longer number."),
    C(T(r'int n = 0;', r'for (const char *p = "$w"; *p; p++)', r'    if (strchr("aeiou", *p))', r'        n++;', PF("%d", "n")), _vowels,
      "strchr finds the letter in the vowel list or returns NULL; n counts the vowels."),
    C(T(r'const char *p = "$w";', PF("%d", "p[$L]")), 0, "Right after the last letter sits the NUL terminator: the number 0."),
    C(T(r'char s[] = "$w";', r'char *e = s + strlen(s);', PF("%d %d", "(int)(e - s), *e")), lambda p: f"{len(p['w'])} 0",
      "e points at the NUL: e - s is the length and *e is 0."),
    C(T(r'const char *p = "$w";', r'const char *q = p + $i;', PF("%d %c", "(int)(q - p), *q")), lambda p: f"{p['i']} {p['w'][p['i']]}",
      "q is i characters along from p."),
    C(T(r'const char *tail(const char *s) { return s + 1; }', MAIN, r'    printf("[%s]\n", tail(tail("$w")));', r'}'), _tail_tail,
      "Each tail call drops one more character from the front."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r"while (*p && *p != '$f')", r'    p++;', PF("%d", "(int)(p - s)")), _index_of,
      "The loop stops at the first match, so p - s is its index."),
    C(T(r'char s[8];', r"memset(s, '$x', $k);", r"s[$k] = '\0';", PF("%s", "s")), lambda p: p["x"] * p["k"],
      "memset fills k bytes with the letter; the NUL after them ends the string."),
    C(T(r'char d[8] = {0};', r'memcpy(d, "$w", 3);', PF("%s", "d")), lambda p: p["w"][:3],
      "memcpy copies exactly 3 characters; the zeros already in d end the string."),
    C(T(r'char s[] = "$w";', r'char *p = s;', r"p[1] = '\0';", PF("%s|%s", "s, s + 2")), _after_nul,
      "The NUL at index 1 cuts s to one character; s + 2 still sees the rest."),
    C(T(r'char s[] = "$w";', r'char *p = &s[0], *q = &s[$L - 1];', r'char t = *p;', r'*p = *q;', r'*q = t;', PF("%s", "s")), _swap_ends,
      "The first and last characters trade places."),
    C(T(r'char a[] = "$w", b[] = "$w";', PF("%d %d", "strcmp(a, b) == 0, a == b")), "1 0",
      "Equal text, but two different arrays: strcmp compares the characters, == compares the addresses."),
    C(T(r'const char *p = "$w";', r'const char *q = p;', r'q++;', PF("%c%c", "*p, *q")), lambda p: p["w"][:2],
      "q moved on; p stayed: they show the first two characters."),
    C(T(r'char s[] = "$w";', r's[$j] ^= 32;', PF("%s", "s")), _toggle,
      "XOR with 32 flips a letter between lower and upper case."),
    C(T(r'char s[] = "$w";', r'for (char *p = s; *p; p++)', r"    if (*p == '$f')", r"        *p = '*';", PF("%s", "s")), _star,
      "Every character equal to the letter is replaced by a star."),
    C(T(r'size_t len(const char *s) { const char *e = s; while (*e) e++; return (size_t)(e - s); }', MAIN,
        r'    printf("%zu\n", len("$w") + len("$z"));', r'}'), lambda p: len(p["w"]) + len(p["z"]),
      "len finds the end by walking a pointer and subtracts the start."),
    C(T(r'char s[] = "$w";', r'char *p = &s[$L - 1];', r'while (p > s) {', r'    printf("%c", *p);', r'    p--;', r'}', r'printf("%c", *p);'), _rev_print,
      "The pointer walks from the last character back to the first, printing each."),
]


# ── 8. Function Pointers ────────────────────────────────────────────────

ADD = r'int add(int a, int b) { return a + b; }'
SUB = r'int sub(int a, int b) { return a - b; }'
MUL = r'int mul(int a, int b) { return a * b; }'
INC = r'int inc(int x) { return x + 1; }'
DBL = r'int dbl(int x) { return x * 2; }'
SQ = r'int sq(int x) { return x * x; }'
FN = r'typedef int (*fn)(int);'
OPT = r'typedef int (*op_t)(int, int);'


def _fact(n: int) -> int:
    return 1 if n <= 1 else n * _fact(n - 1)


def _fib(n: int) -> int:
    return n if n < 2 else _fib(n - 1) + _fib(n - 2)


def _twice_inc_dbl(p: dict) -> int:
    return (p["a"] + 1) * 2


def _ops(p: dict):
    return [lambda a, b: a + b, lambda a, b: a - b, lambda a, b: a * b]


FPTR: list[Maker] = [
    C(T(ADD, MUL, MAIN, r'    int (*f)(int, int) = add;', r'    int r = f($a, $b);', r'    f = mul;', r'    printf("%d %d\n", r, f($a, $b));', r'}'),
      lambda p: ints(p["a"] + p["b"], p["a"] * p["b"]), "f holds the address of add, and later of mul; calling f calls whichever it holds."),
    C(T(ADD, SUB, MUL, MAIN, r'    int (*ops[])(int, int) = {add, sub, mul};', r'    printf("%d\n", ops[$q]($a, $b));', r'}'),
      lambda p: _ops(p)[p["q"]](p["a"], p["b"]), "ops[q] is the q-th function in the table; the parentheses call it."),
    C(T(OPT, ADD, MUL, MAIN, r'    op_t f = mul;', r'    op_t g = add;', r'    printf("%d\n", f($a, $b) - g($a, $b));', r'}'),
      lambda p: p["a"] * p["b"] - (p["a"] + p["b"]), "The typedef gives the function-pointer type a short name."),
    C(T(r'int apply(int (*f)(int), int x) { return f(x); }', SQ, DBL, MAIN, r'    printf("%d\n", apply(sq, $a) + apply(dbl, $b));', r'}'),
      lambda p: p["a"] ** 2 + 2 * p["b"], "apply receives a function as an argument and calls it: a callback."),
    C(T(r'int apply_n(int (*f)(int), int x, int n) { while (n--) x = f(x); return x; }', DBL, MAIN, r'    printf("%d\n", apply_n(dbl, $a, $k));', r'}'),
      lambda p: p["a"] * 2 ** p["k"], "apply_n calls the callback k times in a row, feeding each result back in."),
    C(T(r'void map(int *a, int (*f)(int)) { for (int i = 0; i < 3; i++) a[i] = f(a[i]); }', SQ, MAIN, r'    int v[] = {$a, $b, $c};', r'    map(v, sq);',
        r'    printf("%d %d %d\n", v[0], v[1], v[2]);', r'}'),
      lambda p: ints(p["a"] ** 2, p["b"] ** 2, p["c"] ** 2), "map replaces every element with the callback's result for it."),
    C(T(r'int fold(int *a, int r, int (*f)(int, int)) { for (int n = 3; n--;) r = f(r, *a++); return r; }', ADD, MAIN,
        r'    int v[] = {$a, $b, $c};', r'    printf("%d\n", fold(v, 0, add));', r'}'),
      lambda p: p["a"] + p["b"] + p["c"], "fold combines the elements one by one with the callback: with add it is a sum."),
    C(T(r'int fold(int *a, int r, int (*f)(int, int)) { for (int n = 3; n--;) r = f(r, *a++); return r; }', MUL, MAIN,
        r'    int v[] = {$a, $b, $c};', r'    printf("%d\n", fold(v, 1, mul));', r'}'),
      lambda p: p["a"] * p["b"] * p["c"], "The same fold with mul and a starting value of 1 gives the product."),
    C(T(r'int cnt(int *a, int (*p)(int)) { int n = 0; for (int i = 0; i < 4; i++) n += p(a[i]); return n; }', r'int even(int x) { return x % 2 == 0; }',
        MAIN, r'    int v[] = {$a, $b, $c, $d};', r'    printf("%d\n", cnt(v, even));', r'}'),
      lambda p: sum(1 for v in (p["a"], p["b"], p["c"], p["d"]) if v % 2 == 0), "The predicate answers 1 or 0 for each element, and cnt adds the answers."),
    C(T(r'int cnt(int *a, int (*p)(int)) { int n = 0; for (int i = 0; i < 4; i++) n += p(a[i]); return n; }', r'int big(int x) { return x > 5; }',
        MAIN, r'    int v[] = {$a, $b, $c, $d};', r'    printf("%d\n", cnt(v, big));', r'}'),
      lambda p: sum(1 for v in (p["a"], p["b"], p["c"], p["d"]) if v > 5), "Another predicate, another count: how many elements are bigger than 5."),
    C(T(r'int pick2(int x, int y, int (*b)(int, int)) { return b(x, y) ? x : y; }', r'int gt(int x, int y) { return x > y; }', MAIN,
        r'    printf("%d\n", pick2(pick2($a, $b, gt), $c, gt));', r'}'),
      lambda p: max(p["a"], p["b"], p["c"]), "With gt as the comparison, pick2 keeps the bigger of two; nested, it finds the biggest of three."),
    C(T(r'int pick2(int x, int y, int (*b)(int, int)) { return b(x, y) ? x : y; }', r'int lt(int x, int y) { return x < y; }', MAIN,
        r'    printf("%d\n", pick2(pick2($a, $b, lt), $c, lt));', r'}'),
      lambda p: min(p["a"], p["b"], p["c"]), "Swap the comparison for lt and the same pick2 keeps the smaller: the smallest of three."),
    C(T(OPT, ADD, MUL, r'op_t pick(int w) { return w ? mul : add; }', MAIN, r'    printf("%d\n", pick($r)($a, $b));', r'}'),
      lambda p: p["a"] * p["b"] if p["r"] else p["a"] + p["b"], "pick returns a function; pick(r)(a, b) calls what it returned."),
    C(T(ADD, MUL, MAIN, r'    int (*f)(int, int) = add;', r'    printf("%d %d\n", f == add, f == mul);', r'}'), "1 0",
      "A function pointer compares equal to the function it holds."),
    C(T(DBL, MAIN, r'    int (*f)(int) = NULL;', r'    int r = f == NULL;', r'    f = dbl;', r'    printf("%d %d\n", r, f == NULL);', r'}'), "1 0",
      "A function pointer can be null; once assigned it is not."),
    C(T(r'int acc(int x) { static int n; return n += x; }', MAIN, r'    int (*f)(int) = acc;', r'    f($a);', r'    f($b);', r'    printf("%d\n", f(0));', r'}'),
      lambda p: p["a"] + p["b"], "Every call through f runs acc, whose static n keeps its value between calls."),
    C(T(r'void twice(void (*f)(int *), int *p) { f(p); f(p); }', r'void inc(int *p) { (*p)++; }', MAIN, r'    int x = $a;', r'    twice(inc, &x);',
        r'    printf("%d\n", x);', r'}'), lambda p: p["a"] + 2, "twice calls the callback two times with the same address."),
    C(T(r'void twice(void (*f)(int *), int *p) { f(p); f(p); }', r'void dbl(int *p) { *p *= 2; }', MAIN, r'    int x = $a;', r'    twice(dbl, &x);',
        r'    printf("%d\n", x);', r'}'), lambda p: p["a"] * 4, "Doubling twice quadruples x."),
    C(T(FN, DBL, SQ, MAIN, r'    fn f = dbl, g = sq;', r'    fn t = f;', r'    f = g;', r'    g = t;', r'    printf("%d %d\n", f($a), g($a));', r'}'),
      lambda p: ints(p["a"] ** 2, 2 * p["a"]), "The two pointers swap like any two variables: f now squares and g doubles."),
    C(T(INC, DBL, MAIN, r'    int (*fs[])(int) = {inc, dbl};', r'    int x = $a;', r'    for (int i = 0; i < 2; i++)', r'        x = fs[i](x);',
        r'    printf("%d\n", x);', r'}'), _twice_inc_dbl, "The loop calls inc and then dbl on the running value: (a + 1) * 2."),
    C(T(r'void run(void (*cb)(int *), int *v) { if (cb) cb(v); }', r'void inc(int *p) { (*p)++; }', MAIN, r'    int x = $a;', r'    run(inc, &x);',
        r'    run(NULL, &x);', r'    run(inc, &x);', r'    printf("%d\n", x);', r'}'), lambda p: p["a"] + 2, "run calls the callback only when it is not NULL: two of the three calls count."),
    C(T(INC, DBL, r'struct Op { char c; int (*fn)(int); };', MAIN, r"    struct Op ops[] = {{'i', inc}, {'d', dbl}};", r'    printf("%d %c\n", ops[1].fn($a), ops[1].c);', r'}'),
      lambda p: f"{2 * p['a']} d", "A struct can hold a function pointer: ops[1].fn(a) calls dbl."),
    C(T(INC, DBL, r'struct Op { int (*fn)(int); };', MAIN, r'    struct Op ops[] = {{inc}, {dbl}};',
        r'    printf("%d\n", ops[0].fn($a) + ops[1].fn($a));', r'}'),
      lambda p: (p["a"] + 1) + 2 * p["a"], "Each table entry's function is called with a and the two results are added."),
    C(T(INC, DBL, r'struct Op { int (*fn)(int); };', MAIN, r'    struct Op ops[] = {{inc}, {dbl}};', r'    struct Op *p = &ops[1];',
        r'    printf("%d\n", p->fn($a));', r'}'),
      lambda p: 2 * p["a"], "p->fn(a) follows the pointer to the struct, takes its fn member and calls it."),
    C(T(r'int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }', MAIN, r'    int (*f)(int) = fact;', r'    printf("%d\n", f($a));', r'}'),
      lambda p: _fact(p["a"]), "Calling through the pointer is the same as calling fact: n times fact(n - 1), down to 1."),
    C(T(r'int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }', MAIN, r'    int (*f)(int) = fib;', r'    printf("%d\n", f($a));', r'}'),
      lambda p: _fib(p["a"]), "Each call adds the two before it: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34."),
    C(T(r'int compose(int (*f)(int), int (*g)(int), int x) { return f(g(x)); }', INC, DBL, MAIN, r'    printf("%d\n", compose(dbl, inc, $a));', r'}'),
      lambda p: 2 * (p["a"] + 1), "compose(f, g, x) is f(g(x)): inc first, then dbl."),
    C(T(r'int compose(int (*f)(int), int (*g)(int), int x) { return f(g(x)); }', INC, DBL, MAIN, r'    printf("%d\n", compose(inc, dbl, $a));', r'}'),
      lambda p: 2 * p["a"] + 1, "Swap the arguments and the order swaps: dbl first, then inc."),
    C(T(INC, DBL, MAIN, r'    int (*f)(int) = $a > 5 ? dbl : inc;', r'    printf("%d\n", f($b));', r'}'),
      lambda p: 2 * p["b"] if p["a"] > 5 else p["b"] + 1, "The conditional picks which function f holds; then calling f runs that one."),
    C(T(INC, DBL, MAIN, r'    int (*fs[])(int) = {inc, dbl};', r'    fs[1] = fs[0];', r'    printf("%d\n", fs[1]($a));', r'}'),
      lambda p: p["a"] + 1, "Copying a function pointer within the table makes both entries inc."),
    C(T(r'int total;', r'void hit(void) { total += $a; }', MAIN, r'    void (*cb)(void) = hit;', r'    cb();', r'    cb();', r'    printf("%d\n", total);', r'}'),
      lambda p: 2 * p["a"], "Calling cb twice runs hit twice; each adds a to the global total."),
    C(T(r'void on_a(int *s) { *s += 1; }', r'void on_b(int *s) { *s *= 2; }', MAIN, r'    void (*h[])(int *) = {on_a, on_b, on_a};', r'    int s = $a;',
        r'    for (int i = 0; i < 3; i++)', r'        h[i](&s);', r'    printf("%d\n", s);', r'}'),
      lambda p: (p["a"] + 1) * 2 + 1, "The handlers run in table order: add 1, double, add 1."),
    C(T(ADD, MAIN, r'    int (*f)(int, int) = add;', r'    printf("%d %d\n", (*f)($a, $b), (&add)($a, $b));', r'}'),
      lambda p: ints(p["a"] + p["b"], p["a"] + p["b"]), "(*f)(...) and (&add)(...) are the same call as f(...): a function name already is its address."),
    C(T(r'int *first(int *a, int (*p)(int)) { while (!p(*a)) a++; return a; }', r'int big(int x) { return x > 5; }', MAIN,
        r'    int v[] = {$a, $b, $c, $d, 10};', r'    printf("%d\n", (int)(first(v, big) - v));', r'}'),
      lambda p: next(i for i, v in enumerate((p["a"], p["b"], p["c"], p["d"], 10)) if v > 5),
      "first returns a pointer to the first element the predicate accepts; the 10 at the end guarantees a stop."),
    C(T(r'int sum_of(const int *a, int (*f)(int)) { int s = 0; for (int i = 0; i < 3; i++) s += f(a[i]); return s; }', SQ, MAIN,
        r'    int v[] = {$a, $b, $c};', r'    printf("%d\n", sum_of(v, sq));', r'}'),
      lambda p: p["a"] ** 2 + p["b"] ** 2 + p["c"] ** 2, "sum_of adds the callback's result for each element: the sum of squares."),
    C(T(r'int maxi(int a, int b) { return a > b ? a : b; }', r'int mini(int a, int b) { return a < b ? a : b; }', MAIN,
        r'    int (*better)(int, int) = $r ? maxi : mini;', r'    printf("%d\n", better($a, $b));', r'}'),
      lambda p: max(p["a"], p["b"]) if p["r"] else min(p["a"], p["b"]), "The conditional chooses max or min; better(a, b) then calls the choice."),
    C(T(r'void each(int *a, void (*f)(int)) { for (int i = 0; i < 3; i++) f(a[i]); }', r'void show(int x) { printf("%d ", x); }', MAIN,
        r'    int v[] = {$a, $b, $c};', r'    each(v, show);', r'}'),
      lambda p: ints(p["a"], p["b"], p["c"]), "each calls show for every element, and show prints it followed by a space."),
    C(T(r'void each(int *a, void (*f)(int)) { for (int i = 0; i < 3; i++) f(a[i]); }', r'void sq_show(int x) { printf("%d ", x * x); }', MAIN,
        r'    int v[] = {$a, $b, $c};', r'    each(v, sq_show);', r'}'),
      lambda p: ints(p["a"] ** 2, p["b"] ** 2, p["c"] ** 2), "The callback prints each square instead."),
    C(T(r'void one(void) { printf("A"); }', r'void two(void) { printf("B"); }', MAIN, r'    void (*f[])(void) = {two, one, two};', r'    for (int i = 0; i < 3; i++)',
        r'        f[i]();', r'}'), "BAB", "The table is called in order: two, one, two."),
    C(T(INC, DBL, MAIN, r'    int (*tab[])(int) = {inc, dbl, NULL};', r'    int x = $a;', r'    for (int i = 0; tab[i]; i++) x = tab[i](x);', r'    printf("%d\n", x);', r'}'),
      _twice_inc_dbl, "The loop calls each function of the table on the running value until it meets the null entry."),
    C(T(FN, INC, DBL, r"fn pick(char c) { return c == 'd' ? dbl : inc; }", MAIN, r'''    printf("%d\n", pick('d')($a) + pick('x')($a));''', r'}'),
      lambda p: 2 * p["a"] + p["a"] + 1, "pick('d') is dbl and pick('x') is inc: 2a plus a + 1."),
    C(T(FN, SQ, DBL, MAIN, r'    fn f = sq;', r'    fn g = f;', r'    g = dbl;', r'    printf("%d %d\n", f($a), g($a));', r'}'),
      lambda p: ints(p["a"] ** 2, 2 * p["a"]), "g got a copy of f's address and then a new one; f still squares."),
    C(T(r'void inc(int *p) { (*p)++; }', r'void dbl(int *p) { *p *= 2; }', MAIN, r'    int x = $a;', r'    void (*f)(int *) = inc;', r'    f(&x);', r'    f = dbl;', r'    f(&x);',
        r'    printf("%d\n", x);', r'}'), _twice_inc_dbl, "f is inc for the first call and dbl for the second: (a + 1) * 2."),
    C(T(r'int mini(int a, int b) { return a < b ? a : b; }', r'int maxi(int a, int b) { return a > b ? a : b; }', MAIN,
        r'    int (*fs[])(int, int) = {mini, maxi};', r'    printf("%d\n", fs[$a > 5]($a, $b));', r'}'),
      lambda p: max(p["a"], p["b"]) if p["a"] > 5 else min(p["a"], p["b"]), "The comparison gives 0 or 1, and that number is the index: mini or maxi."),
    C(T(ADD, MUL, MAIN, r'    int (*ops[])(int, int) = {add, mul};', r'    printf("%d\n", ops[1]($a, $b) - ops[0]($a, $b));', r'}'),
      lambda p: p["a"] * p["b"] - (p["a"] + p["b"]), "ops[1] is mul and ops[0] is add: the product minus the sum."),
]
