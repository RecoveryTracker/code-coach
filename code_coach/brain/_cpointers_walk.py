"""C pointers and structs pack, part 2: Walk the Array (pointer arithmetic inside one array) and Pointer to Pointer
(`int **`, arrays of pointers, tables of strings, `const` placement).

Every answer is worked out by hand: plain arithmetic where that is all there is, and the `Ptr` model of
`_cpointers_model.py` (which refuses anything out of bounds) where a pointer really moves. Bodies of `main` unless they
define `main`. Nothing prints an address; two pointers are only ever subtracted or ordered inside one array.
"""

from __future__ import annotations

from ._c_model import C
from ._ccore_numbers import T
from ._ccore_text import PF
from ._cpointers_model import Ptr, cstr, ints, text, var
from ._model import Maker

A4 = r'int a[] = {$a, $b, $c, $d};'
A4V = lambda p: [p["a"], p["b"], p["c"], p["d"]]  # noqa: E731  (the values of A4)


def _walk_sum3(p: dict) -> str:
    a = A4V(p)
    q = Ptr(a)
    s = 0
    for _ in range(3):
        s += q.get()
        q = q + 1
    return ints(s, q.get())


def _fill_walk(p: dict) -> str:
    b = [0, 0, 0, 0]
    q = Ptr(b)
    q.set(p["a"])
    q = q + 1
    q.set(p["b"])
    q = q + 1
    return ints(q - Ptr(b), b[0], b[1])


def _two_ends(p: dict) -> str:
    a = A4V(p)
    lo, hi = Ptr(a), Ptr(a, 3)
    while lo < hi:
        t = lo.get()
        lo.set(hi.get())
        hi.set(t)
        lo, hi = lo + 1, hi - 1
    return ints(a[0], a[1])


def _bump_walk(p: dict) -> str:
    a = A4V(p)
    q = Ptr(a)
    q.set(q.get() + 1)
    q = q + 1
    q.set(q.get() + 1)
    return ints(a[0], a[1], q - Ptr(a))


def _post_store(p: dict) -> str:
    a = A4V(p)
    q = Ptr(a)
    q.set(0)  # *p++ = 0 stores through the OLD p, then p moves on
    q = q + 1
    return ints(a[0], q - Ptr(a))


def _gap(p: dict) -> str:
    a = A4V(p)
    base, q = Ptr(a), Ptr(a, 3)
    d1 = q - base
    base = base + 2
    return ints(d1, q - base)


# ── 3. Walk the Array ───────────────────────────────────────────────────

WALK: list[Maker] = [
    C(T(A4, r'int s = 0;', r'for (int *p = a; p != a + 4; p++)', r'    s += *p;', PF("%d", "s")), lambda p: sum(A4V(p)),
      "p visits each element from a up to, but not including, a + 4, which is one past the end."),
    C(T(A4, r'for (int *p = a; p < a + 4; p++)', r'    *p *= 2;', PF("%d", "a[1] + a[3]")), lambda p: 2 * (p["b"] + p["d"]),
      "The loop doubles every element through p."),
    C(T(A4, r'int n = 0;', r'for (int *p = a; p < a + 4; p++)', r'    if (*p > 5)', r'        n++;', PF("%d", "n")),
      lambda p: sum(1 for v in A4V(p) if v > 5), "n counts the elements bigger than 5."),
    C(T(A4, r'int *p = a;', r'while (*p != $c)', r'    p++;', PF("%d", "(int)(p - a)")), lambda p: A4V(p).index(p["c"]),
      "p stops at the element equal to c; p - a is how many elements it moved: the index."),
    C(T(A4, r'int *p = a + 4;', r'while (p > a) {', r'    p--;', r'    printf("%d ", *p);', r'}'),
      lambda p: ints(*reversed(A4V(p))),
      "p starts one past the end and steps back before each read: the elements come out last to first."),
    C(T(A4, r'int *p = a;', r'int s = 0;', r'for (int i = 0; i < 3; i++)', r'    s += *p++;', PF("%d %d", "s, *p")), _walk_sum3,
      "*p++ reads and then moves on: three elements are added and p ends on the fourth."),
    C(T(A4, r'int b[4];', r'int *p = a, *q = b;', r'while (q != b + 4)', r'    *q++ = *p++;', PF("%d %d", "b[0], b[3]")),
      lambda p: ints(p["a"], p["d"]), "*q++ = *p++ copies one element and moves both pointers: b becomes a copy of a."),
    C(T(r'int b[4] = {0};', r'int *q = b;', r'*q++ = $a;', r'*q++ = $b;', PF("%d %d %d", "(int)(q - b), b[0], b[1]")), _fill_walk,
      "Each *q++ = v stores at q and moves q on; after two stores q is 2 elements from b."),
    C(T(A4, r'int *p = a + $q;', r'p += 2;', PF("%d", "(int)(p - a)")), lambda p: p["q"] + 2,
      "p - a counts the elements between: q to start with, 2 more after the move."),
    C(T(A4, PF("%d", "(int)(&a[3] - a)")), 3, "&a[3] is three elements along from a, and the difference is counted in elements."),
    C(T(A4, PF("%d", "(int)((a + 3) - (a + $q))")), lambda p: 3 - p["q"], "The difference of two pointers into one array is the number of elements between them."),
    C(T(A4, r'int i = $k;', PF("%d", "*(a + i) + *(a + i - 1)")), lambda p: A4V(p)[p["k"]] + A4V(p)[p["k"] - 1],
      "*(a + i) is a[i]: this adds an element and the one before it."),
    C(T(A4, PF("%d %d", "*a + 1, *(a + 1)")), lambda p: ints(p["a"] + 1, p["b"]),
      "*a + 1 is the first element plus 1; *(a + 1) is the second element. The parentheses decide."),
    C(T(A4, PF("%d %d %d", "&a[1] == a + 1, a == &a[0], a + 1 == &a[2]")), "1 1 0",
      "&a[i] and a + i are the same address; a + 1 is the second element, not the third."),
    C(T(A4, r'int *p = &a[$q], *q = &a[3];', PF("%d %d", "p < q, p >= q")), "1 0",
      "Inside one array a smaller index is a smaller address: p is before q."),
    C(T(r'int a[] = {$a, $b, $c, 0, $d};', r'int n = 0;', r'for (int *p = a; *p; p++)', r'    n++;', PF("%d", "n")), 3,
      "The loop stops at the first 0, so only the three elements before it are counted."),
    C(T(r'int a[] = {$a, $b, $c, 0, $d};', r'int s = 0;', r'int *p = a;', r'while (*p)', r'    s += *p++;', PF("%d", "s")),
      lambda p: p["a"] + p["b"] + p["c"], "A 0 ends the walk, like the NUL of a string: the last element is never added."),
    C(T(A4, r'int *lo = a, *hi = a + 3;', r'while (lo < hi) {', r'    int t = *lo; *lo = *hi; *hi = t;', r'    lo++; hi--;', r'}',
        PF("%d %d", "a[0], a[1]")), _two_ends, "Two pointers swap their elements and move inward until they meet: the array is reversed."),
    C(T(A4, r'int *m = a;', r'for (int *p = a + 1; p < a + 4; p++)', r'    if (*p > *m)', r'        m = p;', PF("%d", "(int)(m - a)")),
      lambda p: A4V(p).index(max(A4V(p))), "m remembers where the biggest element so far sits; m - a is its index."),
    C(T(A4, r'int *m = a;', r'for (int *p = a + 1; p < a + 4; p++)', r'    if (*p < *m)', r'        m = p;', PF("%d", "*m")),
      lambda p: min(A4V(p)), "m ends up pointing at the smallest element."),
    C(T(A4, r'int *p = a;', r'(*p)++;', r'p++;', r'(*p)++;', PF("%d %d %d", "a[0], a[1], (int)(p - a)")), _bump_walk,
      "(*p)++ changes the element; p++ moves the pointer: two different things."),
    C(T(A4, r'int *p = a;', r'*p++ = 0;', PF("%d %d", "a[0], (int)(p - a)")), _post_store,
      "*p++ = 0 stores at the old p and then moves p to the next element."),
    C(T(A4, r'int *p = a + 3;', PF("%d", "p[-2] + p[-3]")), lambda p: p["b"] + p["a"],
      "p[-k] is the element k places before p: here a[1] and a[0]."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, $a, $b}};', PF("%d", "*(*(m + 1) + 2)")), lambda p: p["b"],
      "m + 1 is the second row; *(m + 1) is that row; + 2 moves to its third element."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, $a, $b}};', PF("%d", "*(m[1] + 1)")), lambda p: p["a"],
      "m[1] is the second row as a pointer to its first element; + 1 is its second element."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, $a, $b}};', r'int *r = m[1];', PF("%d", "r[0] + r[2]")), lambda p: p["d"] + p["b"],
      "r points at the first element of the second row: r[0] and r[2] are its ends."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, $a, $b}};', r'int (*r)[3] = m;', r'r++;', PF("%d", "(*r)[1]")), lambda p: p["a"],
      "r points at a whole row; r++ moves to the next row, and (*r)[1] is that row's second element."),
    C(T(r'int m[2][3] = {{$a, $b, $c}, {$d, $a, $b}};', r'int (*r)[3] = m;', PF("%d", "r[1][0] + **r")), lambda p: p["d"] + p["a"],
      "r[1][0] is the first element of the second row; **r is the first element of the first."),
    C(T(r'int m[2][3];', r'int (*r)[3] = m;', PF("%zu", "sizeof(*r) / sizeof(**r)")), 3,
      "*r is a row of 3 ints and **r is one int: the ratio is 3."),
    C(T(A4, r'int (*pa)[4] = &a;', PF("%d", "(*pa)[$q] + (*pa)[3]")), lambda p: A4V(p)[p["q"]] + p["d"],
      "pa points at the whole array; (*pa) is the array, so (*pa)[i] is element i."),
    C(T(r'int len(const int *p) { int n = 0; while (*p++) n++; return n; }', r'int main(void) {', r'    int a[] = {$a, $b, 0};',
        r'    printf("%d\n", len(a));', r'}'), 2,
      "len walks its own copy of the pointer until it reads the 0."),
    C(T(r'int *find(int *a, int n, int v) { for (int i = 0; i < n; i++) if (a[i] == v) return &a[i]; return NULL; }',
        r'int main(void) {', r'    int a[] = {$a, $b, $c, $d};', r'    printf("%d\n", (int)(find(a, 4, $c) - a));', r'}'),
      lambda p: A4V(p).index(p["c"]), "find returns the address of the match; subtracting a gives its index."),
    C(T(r'int *find(int *a, int n, int v) { for (int i = 0; i < n; i++) if (a[i] == v) return &a[i]; return NULL; }',
        r'int main(void) {', r'    int a[] = {$a, $b, $c, $d};', r'    printf("%d\n", find(a, 4, $m) == NULL);', r'}'), 1,
      "No element is as big as m, so find returns NULL."),
    C(T(r'int *find(int *a, int v) { while (*a != v) a++; return a; }',
        r'int main(void) {', r'    int a[] = {$a, $b, $c, $d};', r'    *find(a, $b) = 0;', r'    printf("%d\n", a[0] + a[1] + a[2] + a[3]);', r'}'),
      lambda p: p["a"] + p["c"] + p["d"], "find hands back the address of b's element, and the assignment zeroes it."),
    C(T(r'int a[] = {$a, $b, $c, $d, $m, $n};', r'int s = 0;', r'for (int *p = a; p < a + 6; p += 2)', r'    s += *p;', PF("%d", "s")),
      lambda p: p["a"] + p["c"] + p["m"], "p += 2 steps over every other element: indexes 0, 2 and 4."),
    C(T(A4, r'for (int *p = a + 1; p < a + 4; p++)', r'    *p += *(p - 1);', PF("%d", "a[3]")), lambda p: sum(A4V(p)),
      "Each element takes on the running total of the ones before it, so the last holds the sum of all four."),
    C(T(r'int a[6];', r'int *p = a;', r'int steps = 0;', r'while (p < a + 6) {', r'    p += $k;', r'    steps++;', r'}', PF("%d", "steps")),
      lambda p: 6 // p["k"], "Six elements taken k at a time: p reaches the end pointer after 6 / k steps."),
    C(T(A4, r'int *p = a, *q = a + 3;', r'int d1 = (int)(q - p);', r'p += 2;', PF("%d %d", "d1, (int)(q - p)")), _gap,
      "The gap q - p shrinks by 2 when p moves 2 elements closer."),
    C(T(r'int a[4];', r'for (int *p = a; p < a + 4; p++)', r'    *p = (int)(p - a) * $a;', PF("%d", "a[3]")), lambda p: 3 * p["a"],
      "p - a is the index, so each element is its index times a."),
    C(T(r'int a[4];', r'for (int i = 0; i < 4; i++)', r'    *(a + i) = i * i;', PF("%d", "a[$q + 1]")), lambda p: (p["q"] + 1) ** 2,
      "*(a + i) is a[i]: the elements are the squares 0, 1, 4, 9."),
    C(T(A4, r'int *last = &a[sizeof a / sizeof a[0] - 1];', PF("%d", "*last")), lambda p: p["d"],
      "sizeof a / sizeof a[0] is 4, so last points at a[3]."),
    C(T(A4, r'int *end = a + sizeof(a) / sizeof(a[0]);', PF("%d", "(int)(end - a)")), 4,
      "The end pointer is one past the last element: it is 4 elements from a."),
    C(T(A4, r'int t = 0;', r'for (int *p = a; p < a + 4; p++)', r'    t += (int)(p - a) * *p;', PF("%d", "t")),
      lambda p: p["b"] + 2 * p["c"] + 3 * p["d"], "Each element is multiplied by its index: the first counts for nothing."),
    C(T(A4, r'int *p = &a[1], *q = &a[$q + 2];', PF("%d", "(int)(p - q)")), lambda p: 1 - (p["q"] + 2),
      "p is before q, so p - q is negative: the number of elements between, with a minus sign."),
    C(T(A4, r'int *mid = a + 2;', PF("%d %d %d", "mid[-2], mid[0], mid[1]")), lambda p: ints(p["a"], p["c"], p["d"]),
      "mid points at the third element: mid[-2] is the first, mid[1] the fourth."),
    C(T(A4, r'int *p = &a[1];', r'p[1] = $n;', PF("%d", "a[2]")), lambda p: p["n"],
      "p[1] is the element after the one p points at: a[2]."),
    C(T(A4, r'int t = *a;', r'*a = *(a + 3);', r'*(a + 3) = t;', PF("%d %d", "a[0], a[3]")), lambda p: ints(p["d"], p["a"]),
      "The two ends trade places, written with pointer arithmetic instead of indexes."),
]


# ── 4. Pointer to Pointer ───────────────────────────────────────────────

XYZ = r'int x = $a, y = $b, z = $c;'


def _first_diff(p: dict) -> int:
    return ord(p["z"][0]) - ord(p["w"][0])


def _tail_after(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s) + 1  # (*pp)++ moves s itself
    return text(q)


def _skip_to(p: dict) -> str:
    s = cstr(p["w"])
    q = Ptr(s) + p["i"]
    return chr(q.get())


def _total_len(p: dict) -> int:
    return len(p["w"]) + len(p["z"])


def _next_next(p: dict) -> int:
    a = A4V(p)
    q = Ptr(a)
    q = q + 1
    q = q + 1
    return q.get()


def _max_out(p: dict) -> int:
    a = A4V(p)
    out = Ptr(a)
    for i in range(1, 4):
        if a[i] > out.get():
            out = Ptr(a, i)
    return out - Ptr(a)


def _var_cells(p: dict):
    return var(p["a"]), var(p["b"]), var(p["c"])


PTRPTR: list[Maker] = [
    C(T(r'int x = $a;', r'int *p = &x;', r'int **pp = &p;', r'**pp += *p;', PF("%d", "x")), lambda p: 2 * p["a"],
      "*p and **pp are both x: x += x doubles it."),
    C(T(r'int x = $a, y = $b;', r'int *p = &x;', r'int **pp = &p;', r'*pp = &y;', r'*p = $c;', PF("%d %d", "x, y")),
      lambda p: ints(p["a"], p["c"]), "*pp = &y changes p itself, so the next write through p lands in y."),
    C(T(r'int x = $a, y = $b;', r'int *p = &x;', r'int **pp = &p;', r'*pp = &y;', r'**pp += $c;', PF("%d %d %d", "x, y, *p")),
      lambda p: ints(p["a"], p["b"] + p["c"], p["b"] + p["c"]),
      "After *pp = &y, p points at y; **pp is y, and *p sees the same value."),
    C(T(r'void at(int **pp, int *t) { *pp = t; }', r'int main(void) {', r'    int x = $a, y = $b;', r'    int *p = &x;',
        r'    at(&p, &y);', r'    printf("%d\n", *p);', r'}'), lambda p: p["b"],
      "To change where p points, the function needs the address of p: an int **."),
    C(T(r'void at(int *q, int *t) { q = t; }', r'int main(void) {', r'    int x = $a, y = $b;', r'    int *p = &x;',
        r'    at(p, &y);', r'    printf("%d\n", *p);', r'}'), lambda p: p["a"],
      "at only moves its own copy of the pointer; p in main still points at x."),
    C(T(r'int x = $a;', r'int *p = &x;', r'int **pp = &p;', r'**pp *= **pp;', PF("%d", "x")), lambda p: p["a"] ** 2,
      "**pp is x, so x is multiplied by itself."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', r'*arr[1] = $d;', PF("%d", "y")), lambda p: p["d"],
      "arr[1] is a pointer to y; *arr[1] is y."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', PF("%d", "*arr[0] + *arr[2]")), lambda p: p["a"] + p["c"],
      "Each element of arr is a pointer: * reaches the variable behind it."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', r'for (int i = 0; i < 3; i++)', r'    *arr[i] += $k;', PF("%d %d %d", "x, y, z")),
      lambda p: ints(p["a"] + p["k"], p["b"] + p["k"], p["c"] + p["k"]),
      "The loop writes through each of the three pointers, so all three variables change."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', r'int **pp = arr;', r'pp++;', PF("%d", "**pp")), lambda p: p["b"],
      "pp points at arr[0]; pp++ moves it to arr[1], which points at y."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', r'int **pp = arr;', PF("%d", "pp[2][0] + *pp[1]")), lambda p: p["c"] + p["b"],
      "pp[2] is the pointer to z, and [0] reaches z; *pp[1] reaches y."),
    C(T(XYZ, r'int *arr[3] = {&x, &y, &z};', r'int *t = arr[0];', r'arr[0] = arr[2];', r'arr[2] = t;',
        PF("%d %d %d %d", "*arr[0], *arr[2], x, z")), lambda p: ints(p["c"], p["a"], p["a"], p["c"]),
      "Swapping the pointers in the array leaves the variables themselves alone."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%c", "names[1][0]")), lambda p: p["z"][0],
      "names[1] is the second string; [0] is its first character."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%c", "names[0][1]")), lambda p: p["w"][1],
      "names[0] is the first string; [1] is its second character."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%zu", "strlen(names[1])")), lambda p: len(p["z"]),
      "names[1] points at the second string, and strlen counts its characters."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%s", "names[0] + $i")), lambda p: p["w"][p["i"]:],
      "names[0] + i points i characters into the first string."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%c", "**names")), lambda p: p["w"][0],
      "*names is the first string's pointer; ** is its first character."),
    C(T(r'const char *names[] = {"$w", "$z"};', r'names[1] = names[0];', PF("%s", "names[1]")), lambda p: p["w"],
      "Assigning a pointer makes the second entry point at the first string."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%d", "*names[1] - *names[0]")), _first_diff,
      "Each * gives a first character, a small number: the difference of their codes."),
    C(T(r'const char *names[] = {"$w", "$z"};', PF("%c", "**(names + 1)")), lambda p: p["z"][0],
      "names + 1 is the address of the second entry; * gives the pointer, ** its first character."),
    C(T(r'const char *s = "$w";', r'const char **pp = &s;', r'(*pp)++;', PF("%s", "*pp")), _tail_after,
      "(*pp)++ moves s itself one character on, so the string now starts at the second letter."),
    C(T(r'const char *s = "$w";', r'const char **pp = &s;', r'*pp += $i;', PF("%c", "**pp")), _skip_to,
      "*pp += i moves s along i characters; ** reads the character there."),
    C(T(r'int x = $a;', r'int *const p = &x;', r'int *const *pp = &p;', r'**pp = $c;', PF("%d", "x")), lambda p: p["c"],
      "The pointer p is const, but the int behind it is not: **pp may be written."),
    C(T(r'int x = $a;', r'const int *p = &x;', r'const int **pp = &p;', PF("%d", "**pp + 1")), lambda p: p["a"] + 1,
      "Reading through const pointers is fine: **pp is x."),
    C(T(r'int u[2] = {$a, $b}, v[2] = {$c, $d};', r'int *rows[2] = {u, v};', PF("%d", "rows[1][1]")), lambda p: p["d"],
      "rows[1] is v; [1] is its second element."),
    C(T(r'int u[2] = {$a, $b}, v[2] = {$c, $d};', r'int *rows[2] = {u, v};', PF("%d", "*(rows[0] + 1)")), lambda p: p["b"],
      "rows[0] is u; + 1 moves to its second element."),
    C(T(r'int u[2] = {$a, $b}, v[2] = {$c, $d};', r'int *rows[2] = {u, v};', r'rows[0][1] = $n;', PF("%d", "u[1]")), lambda p: p["n"],
      "rows[0] points at u, so the write lands in u itself."),
    C(T(A4, r'int *p = a;', r'int **pp = &p;', r'(*pp)++;', PF("%d", "**pp")), lambda p: p["b"],
      "(*pp)++ moves p to the next element; ** reads it."),
    C(T(A4, r'int *p = a;', r'int **pp = &p;', r'(**pp)++;', PF("%d %d", "a[0], *p")), lambda p: ints(p["a"] + 1, p["a"] + 1),
      "(**pp)++ adds 1 to the element; p did not move."),
    C(T(A4, r'int *p = a;', r'int **pp = &p;', r'*pp += 2;', PF("%d", "*p")), lambda p: p["c"],
      "*pp += 2 is p += 2: p now points at the third element."),
    C(T(A4, r'int *p = a;', r'int **pp = &p;', r'int y = ++**pp;', PF("%d %d", "a[0], y")), lambda p: ints(p["a"] + 1, p["a"] + 1),
      "++**pp adds 1 to the element and gives the new value."),
    C(T(r'void next(int **pp) { (*pp)++; }', r'int main(void) {', r'    int a[] = {$a, $b, $c, $d};', r'    int *p = a;', r'    next(&p);',
        r'    next(&p);', r'    printf("%d\n", *p);', r'}'), _next_next,
      "next moves the caller's pointer, because it was given the address of that pointer."),
    C(T(r'void fmax(int *a, int **o) { for (int i = 1; i < 4; i++) if (a[i] > **o) *o = a + i; }',
        r'int main(void) {', r'    int a[] = {$a, $b, $c, $d};', r'    int *p = a;', r'    fmax(a, &p);', r'    printf("%d\n", (int)(p - a));', r'}'),
      _max_out, "fmax answers through an out-parameter that is a pointer: p ends up pointing at the biggest element."),
    C(T(r'void give(int **pp) { static int v = $a; *pp = &v; }', r'int main(void) {', r'    int *p;', r'    give(&p);', r'    printf("%d\n", *p);', r'}'),
      lambda p: p["a"], "give aims p at a static variable, which lives on after the function returns."),
    C(T(r'int x = $a;', r'int *p = &x;', r'int **pp = &p;', r'int ***ppp = &pp;', r'***ppp = $b;', PF("%d", "x")), lambda p: p["b"],
      "Three stars follow three pointers back to x."),
    C(T(r'int x = $a;', r'int *p = &x;', r'int **pp = &p;', r'int ***ppp = &pp;', PF("%d", "***ppp + **pp")), lambda p: 2 * p["a"],
      "Both expressions end at x."),
    C(T(r'void swapp(int **a, int **b) { int *t = *a; *a = *b; *b = t; }', r'int main(void) {', r'    int x = $a, y = $b;',
        r'    int *p = &x, *q = &y;', r'    swapp(&p, &q);', r'    printf("%d %d %d %d\n", *p, *q, x, y);', r'}'),
      lambda p: ints(p["b"], p["a"], p["a"], p["b"]),
      "swapp swaps the pointers p and q; x and y keep their values."),
    C(T(r'int x = $a, y = $b;', r'int *s[2] = {&x, &y};', r'if (*s[0] > *s[1]) {', r'    int *t = s[0]; s[0] = s[1]; s[1] = t;', r'}',
        PF("%d %d %d", "*s[0], *s[1], x")), lambda p: ints(min(p["a"], p["b"]), max(p["a"], p["b"]), p["a"]),
      "The pointers are put in order, not the variables: x still holds a."),
    C(T(r'int x = $a, y = $b;', r'int *arr[3] = {&x, NULL, &y};', r'int n = 0;', r'for (int i = 0; i < 3; i++)', r'    if (arr[i])',
        r'        n += *arr[i];', PF("%d", "n")), lambda p: p["a"] + p["b"],
      "The null entry is skipped: only the two real pointers are followed."),
    C(T(r'int x = $a, y = $b;', r'int *tab[4] = {&x, &y};', PF("%d %d", "tab[2] == NULL, tab[3] == NULL")), "1 1",
      "The entries that the braces leave out are null pointers."),
    C(T(r'int x = $a;', r'int *p = &x;', r'int **pp = &p;', PF("%d %d %d", "*pp == p, pp == &p, **pp == x")), "1 1 1",
      "*pp is p, pp is the address of p, and **pp is x."),
    C(T(r'int x = $a, y = $b;', r'int *p = &x;', r'int *q = p;', r'int **pp = &p;', r'*pp = &y;', PF("%d %d", "*p, *q")),
      lambda p: ints(p["b"], p["a"]),
      "*pp = &y moved p only: q is a separate copy of the old address."),
    C(T(r'const char *w[] = {"$w", "$z", NULL};', r'int n = 0;', r'while (w[n])', r'    n++;', PF("%d", "n")), 2,
      "A table ended by NULL is walked until the null pointer: two strings."),
    C(T(r'const char *w[] = {"$w", "$z", NULL};', r'const char **p = w;', r'int t = 0;', r'while (*p)', r'    t += (int)strlen(*p++);', PF("%d", "t")),
      _total_len, "p walks the table; *p++ takes each string and moves to the next entry."),
    C(T(r'const char *w[] = {"$w", "$z", NULL};', r'const char **p = w;', r'p++;', PF("%c", "**p")), lambda p: p["z"][0],
      "p++ moves to the second entry; ** is that string's first character."),
    C(T(r'char s1[] = "$w", s2[] = "$z";', r'char *ps[] = {s1, s2};', r"ps[0][0] = '$X';", PF("%s", "s1")),
      lambda p: p["X"] + p["w"][1:], "ps[0] points at s1, so the write changes s1's first letter."),
    C(T(r'char s1[] = "$w", s2[] = "$z";', r'char *ps[] = {s1, s2};', r'ps[1][0] = ps[0][0];', PF("%s", "s2")),
      lambda p: p["w"][0] + p["z"][1:], "The first letter of s1 is copied over the first letter of s2."),
]
