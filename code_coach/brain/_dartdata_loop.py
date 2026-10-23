"""Dart data pack, part 5: Loop Value - what a variable holds (or what a loop printed) when the loop is over.

for, for-in, while, do-while, break, continue, labelled loops, `i++` inside a condition, and the closures a `for`
loop captures (each turn of a Dart `for` gets its OWN `i`, unlike a variable declared outside a `while`). Each
template simulates the loop in Python by hand; the program's last line prints the answer.
"""

from __future__ import annotations

from ._dartdata_model import R, ints, lit, words
from ._model import Maker


def l_sum(r):
    n = r.randint(3, 9)
    return (f"var s = 0;\nfor (var i = 1; i <= {n}; i++) {{\n  s += i;\n}}\nprint(s);", n * (n + 1) // 2,
            "s adds 1, 2, 3 ... up to n.")


def l_sum_lt(r):
    n = r.randint(3, 9)
    return (f"var s = 0;\nfor (var i = 0; i < {n}; i++) {{\n  s += i;\n}}\nprint(s);", n * (n - 1) // 2,
            "i < n stops before n, so n itself is not added.")


def l_step(r):
    n, k = r.randint(10, 30), r.randint(2, 5)
    return (f"var c = 0;\nfor (var i = 0; i < {n}; i += {k}) {{\n  c++;\n}}\nprint(c);", len(range(0, n, k)),
            "i takes the values 0, k, 2k ... below n; c counts them.")


def l_last_i(r):
    n, k = r.randint(10, 30), r.randint(2, 5)
    last = list(range(0, n, k))[-1]
    return (f"var last = 0;\nfor (var i = 0; i < {n}; i += {k}) {{\n  last = i;\n}}\nprint(last);", last,
            "last keeps the final value i had inside the loop.")


def l_after(r):
    n, k = r.randint(10, 30), r.randint(2, 5)
    i = 0
    while i < n:
        i += k
    return (f"var i = 0;\nfor (; i < {n}; i += {k}) {{}}\nprint(i);", i,
            "The loop ends when i first reaches n or more, and i keeps that value.")


def l_countdown(r):
    n = r.randint(4, 9)
    out = ""
    i = n
    while i > 0:
        out += str(i)
        i -= 2
    return (f"var s = '';\nfor (var i = {n}; i > 0; i -= 2) {{\n  s += '$i';\n}}\nprint(s);", out, "i counts down by 2 while it is positive; each value is added as text.")


def l_double(r):
    t = r.randint(20, 100)
    n, c = 1, 0
    while n < t:
        n *= 2
        c += 1
    return (f"var n = 1;\nvar c = 0;\nwhile (n < {t}) {{\n  n *= 2;\n  c++;\n}}\nprint(c);", c, "Count how many doublings it takes to reach the limit.")


def l_double_n(r):
    t = r.randint(20, 100)
    n = 1
    while n < t:
        n *= 2
    return (f"var n = 1;\nwhile (n < {t}) {{\n  n *= 2;\n}}\nprint(n);", n, "n doubles until it is no longer below the limit.")


def l_halve(r):
    n0 = r.randint(20, 200)
    n, c = n0, 0
    while n > 1:
        n //= 2
        c += 1
    return (f"var n = {n0};\nvar c = 0;\nwhile (n > 1) {{\n  n ~/= 2;\n  c++;\n}}\nprint(c);", c, "Halving (rounding down) until 1: c counts the steps.")


def l_digits(r):
    n0 = r.randint(100, 9999)
    n, s = n0, 0
    while n > 0:
        s += n % 10
        n //= 10
    return (f"var n = {n0};\nvar s = 0;\nwhile (n > 0) {{\n  s += n % 10;\n  n ~/= 10;\n}}\nprint(s);", s, "% 10 takes the last digit, ~/ 10 drops it: the digits are added up.")


def l_reverse(r):
    n0 = r.randint(100, 999)
    n, rev = n0, 0
    while n > 0:
        rev = rev * 10 + n % 10
        n //= 10
    return (f"var n = {n0};\nvar rev = 0;\nwhile (n > 0) {{\n  rev = rev * 10 + n % 10;\n  n ~/= 10;\n}}\nprint(rev);", rev, "Each last digit of n is pushed onto the end of rev.")


def l_do_once(r):
    a = r.randint(5, 9)
    return (f"var i = {a};\ndo {{\n  i++;\n}} while (i < 3);\nprint(i);", a + 1, "A do-while runs its body once before checking the test.")


def l_while_never(r):
    a = r.randint(5, 9)
    return (f"var i = {a};\nwhile (i < 3) {{\n  i++;\n}}\nprint(i);", a, "The test is false at the start, so the body never runs.")


def l_do_count(r):
    n = r.randint(3, 8)
    i, c = 0, 0
    while True:
        i += 1
        c += i
        if not i < n:
            break
    return (f"var i = 0;\nvar c = 0;\ndo {{\n  i++;\n  c += i;\n}} while (i < {n});\nprint(c);", c, "i goes 1, 2 ... n and c adds each one.")


def l_post_incr_cond(r):
    n = r.randint(3, 8)
    return (f"var i = 0;\nwhile (i++ < {n}) {{}}\nprint(i);", n + 1, "i++ gives the old value to the test and then adds 1: the last failed test still adds 1.")


def l_pre_incr_cond(r):
    n = r.randint(3, 8)
    return (f"var i = 0;\nwhile (++i < {n}) {{}}\nprint(i);", n, "++i adds first, so the loop stops when i reaches n.")


def l_post_expr(r):
    a = r.randint(2, 9)
    return (f"var i = {a};\nvar j = i++ + ++i;\nprint(j);", a + (a + 2), "i++ gives a (then i is a+1); ++i makes it a+2 and gives that.")


def l_post_expr_i(r):
    a = r.randint(2, 9)
    return (f"var i = {a};\nvar j = i++ + ++i;\nprint(i);", a + 2, "i went up twice.")


def l_post_value(r):
    a = r.randint(2, 9)
    return (f"var i = {a};\nvar j = i++;\nprint('$i $j');", f"{a + 1} {a}", "j got the old value; i is now one more.")


def l_break(r):
    xs = ints(r, 6, 1, 20)
    t = r.randint(8, 14)
    s = 0
    for x in xs:
        if x > t:
            break
        s += x
    return (f"var s = 0;\nfor (var x in {lit(xs)}) {{\n  if (x > {t}) break;\n  s += x;\n}}\nprint(s);", s,
            "break leaves the loop at the first item above the limit; later items are never added.")


def l_continue(r):
    xs = ints(r, 6, 1, 20)
    t = r.randint(8, 14)
    s = sum(x for x in xs if x <= t)
    return (f"var s = 0;\nfor (var x in {lit(xs)}) {{\n  if (x > {t}) continue;\n  s += x;\n}}\nprint(s);", s,
            "continue skips just that item; the loop goes on with the next one.")


def l_break_last(r):
    xs = ints(r, 6, 1, 30)
    t = r.randint(10, 20)
    last = 0
    for x in xs:
        if x > t:
            break
        last = x
    return (f"var last = 0;\nfor (var x in {lit(xs)}) {{\n  if (x > {t}) break;\n  last = x;\n}}\nprint(last);", last,
            "last is the final item before the loop broke out.")


def l_find(r):
    xs = ints(r, 6, 1, 30)
    k = r.randint(2, 4)
    idx = -1
    for i, x in enumerate(xs):
        if x % k == 0:
            idx = i
            break
    return (f"var idx = -1;\nvar xs = {lit(xs)};\nfor (var i = 0; i < xs.length; i++) {{\n  if (xs[i] % {k} == 0) {{\n    idx = i;\n    break;\n  }}\n}}\nprint(idx);",
            idx, "idx is the position of the first multiple, or -1 when there is none.")


def l_skip_multiple(r):
    k, n = r.randint(2, 4), r.randint(8, 15)
    out = [i for i in range(1, n + 1) if i % k != 0]
    return (f"var out = <int>[];\nfor (var i = 1; i <= {n}; i++) {{\n  if (i % {k} == 0) continue;\n  out.add(i);\n}}\nprint(out);", out,
            "Every multiple of k is skipped.")


def l_squares(r):
    n = r.randint(3, 6)
    return (f"var out = [];\nfor (var i = 1; i <= {n}; i++) {{\n  out.add(i * i);\n}}\nprint(out);", [i * i for i in range(1, n + 1)], "Each turn adds the square of i.")


def l_label_continue(r):
    a, b = r.randint(2, 4), r.randint(2, 4)
    c = 0
    for i in range(a):
        for j in range(b):
            if j == 1:
                break  # continue outer == leave the inner loop
            c += 1
    return (f"var c = 0;\nouter:\nfor (var i = 0; i < {a}; i++) {{\n  for (var j = 0; j < {b}; j++) {{\n    if (j == 1) continue outer;\n    c++;\n  }}\n}}\nprint(c);", c,
            "continue outer jumps to the next turn of the OUTER loop, so each i counts only j = 0.")


def l_label_break(r):
    a, b = r.randint(3, 5), r.randint(3, 5)
    s = r.randint(1, 2)
    c = 0
    done = False
    for i in range(a):
        for j in range(b):
            if i == s and j == 1:
                done = True
                break
            c += 1
        if done:
            break
    return (f"var c = 0;\nouter:\nfor (var i = 0; i < {a}; i++) {{\n  for (var j = 0; j < {b}; j++) {{\n    if (i == {s} && j == 1) break outer;\n    c++;\n  }}\n}}\nprint(c);", c,
            "break outer leaves both loops at once.")


def l_inner_break(r):
    a, b = r.randint(2, 4), r.randint(3, 5)
    c = 0
    for i in range(a):
        for j in range(b):
            if j == 2:
                break
            c += 1
    return (f"var c = 0;\nfor (var i = 0; i < {a}; i++) {{\n  for (var j = 0; j < {b}; j++) {{\n    if (j == 2) break;\n    c++;\n  }}\n}}\nprint(c);", c,
            "A plain break leaves only the inner loop: each i counts j = 0 and 1.")


def l_nested(r):
    a, b = r.randint(2, 4), r.randint(2, 4)
    return (f"var c = 0;\nfor (var i = 0; i < {a}; i++) {{\n  for (var j = 0; j < {b}; j++) {{\n    c++;\n  }}\n}}\nprint(c);", a * b, "The inner loop runs completely for every turn of the outer one.")


def l_triangle(r):
    n = r.randint(3, 5)
    c = 0
    for i in range(n):
        for j in range(i):
            c += 1
    return (f"var c = 0;\nfor (var i = 0; i < {n}; i++) {{\n  for (var j = 0; j < i; j++) {{\n    c++;\n  }}\n}}\nprint(c);", c, "The inner loop runs i times: 0 + 1 + 2 + ...")


def l_table(r):
    a, b = r.randint(2, 4), r.randint(2, 4)
    s = "".join(str(i * j) for i in range(1, a + 1) for j in range(1, b + 1))
    return (f"var s = '';\nfor (var i = 1; i <= {a}; i++) {{\n  for (var j = 1; j <= {b}; j++) {{\n    s += '${{i * j}}';\n  }}\n}}\nprint(s);", s,
            "The products i * j glued together in order.")


def l_closures(r):
    n = r.randint(3, 4)
    return (f"var fs = <int Function()>[];\nfor (var i = 0; i < {n}; i++) {{\n  fs.add(() => i);\n}}\nprint(fs.map((f) => f()).toList());", list(range(n)),
            "Each turn of a Dart for loop has its own i, so every closure remembers a different one.")


def l_closures_while(r):
    n = r.randint(3, 4)
    return (f"var fs = <int Function()>[];\nvar i = 0;\nwhile (i < {n}) {{\n  fs.add(() => i);\n  i++;\n}}\nprint(fs.map((f) => f()).toList());", [n] * n,
            "All the closures share the one i declared outside the loop, which ends at n.")


def l_foreach(r):
    xs = ints(r, 4, 1, 9)
    return (f"var s = 0;\n{lit(xs)}.forEach((x) => s += x);\nprint(s);", sum(xs), "forEach calls the function for every item; the closure adds to s.")


def l_forin_reversed(r):
    xs = ints(r, 4, 1, 9)
    out = "".join(str(x) for x in reversed(xs))
    return (f"var s = '';\nfor (var x in {lit(xs)}.reversed) {{\n  s += '$x';\n}}\nprint(s);", out, "reversed walks the list backwards.")


def l_vowels(r):
    w = words(r, 1)[0]
    c = sum(1 for ch in w if ch in "aeiou")
    return (f"var c = 0;\nfor (var ch in '{w}'.split('')) {{\n  if ('aeiou'.contains(ch)) c++;\n}}\nprint(c);", c, "Count the letters that appear in 'aeiou'.")


def l_every_other(r):
    w = words(r, 1)[0]
    return (f"var s = '';\nfor (var i = 0; i < '{w}'.length; i += 2) {{\n  s += '{w}'[i];\n}}\nprint(s);", w[::2], "Positions 0, 2, 4 ... of the word.")


def l_build_up(r):
    w = words(r, 1)[0]
    return (f"var s = '';\nfor (var i = 1; i <= 3; i++) {{\n  s += '{w}'.substring(0, i);\n}}\nprint(s);", w[:1] + w[:2] + w[:3], "The prefixes of length 1, 2 and 3 are glued together.")


def l_fib(r):
    n = r.randint(5, 10)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return (f"var a = 0, b = 1;\nfor (var i = 0; i < {n}; i++) {{\n  var t = a + b;\n  a = b;\n  b = t;\n}}\nprint(a);", a, "Each turn moves the pair (a, b) one step along 0, 1, 1, 2, 3, 5 ...")


def l_factorial(r):
    n = r.randint(3, 7)
    p = 1
    for i in range(2, n + 1):
        p *= i
    return (f"var p = 1;\nfor (var i = 2; i <= {n}; i++) {{\n  p *= i;\n}}\nprint(p);", p, "p multiplies 2 * 3 * ... * n.")


def l_collatz(r):
    n0 = r.choice((3, 5, 6, 7, 9, 10, 12, 13))
    n, c = n0, 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return (f"var n = {n0};\nvar c = 0;\nwhile (n != 1) {{\n  n = n.isEven ? n ~/ 2 : 3 * n + 1;\n  c++;\n}}\nprint(c);", c, "Halve when even, triple plus one when odd, until 1.")


def l_gcd(r):
    g, a, b = r.randint(2, 5), r.randint(2, 6), r.randint(2, 6)
    x, y = g * a, g * b
    while y != 0:
        x, y = y, x % y
    return (f"var a = {g * a}, b = {g * b};\nwhile (b != 0) {{\n  var t = b;\n  b = a % b;\n  a = t;\n}}\nprint(a);", x, "Euclid's way: replace (a, b) by (b, a % b) until b is 0.")


def l_two_vars(r):
    n = r.randint(6, 12)
    i, j, c = 0, n, 0
    while i < j:
        i += 1
        j -= 1
        c += 1
    return (f"var i = 0, j = {n};\nvar c = 0;\nwhile (i < j) {{\n  i++;\n  j--;\n  c++;\n}}\nprint(c);", c, "i and j move toward each other until they meet or cross.")


def l_two_vars_for(r):
    n = r.randint(6, 12)
    out = []
    i, j = 0, n
    while i < j:
        out.append(i + j)
        i += 1
        j -= 1
    return (f"var out = <int>[];\nfor (var i = 0, j = {n}; i < j; i++, j--) {{\n  out.add(i + j);\n}}\nprint(out);", out, "i + j stays the same while the two move inwards.")


def l_mod_loop(r):
    k, n = r.randint(2, 4), r.randint(8, 14)
    c = sum(1 for i in range(1, n + 1) if i % k == 0)
    return (f"var c = 0;\nfor (var i = 1; i <= {n}; i++) {{\n  if (i % {k} == 0) c++;\n}}\nprint(c);", c, "Count the multiples of k up to n.")


def l_modify_i(r):
    n = r.randint(6, 10)
    c = 0
    i = 0
    while i < n:
        if i % 2 == 0:
            i += 1
        c += 1
        i += 1
    return (f"var c = 0;\nfor (var i = 0; i < {n}; i++) {{\n  if (i.isEven) i++;\n  c++;\n}}\nprint(c);", c, "Changing i inside the body changes the turns: an even i skips the next value.")


def l_while_true(r):
    n = r.randint(20, 60)
    k = r.randint(3, 7)
    i = 0
    while True:
        i += k
        if i > n:
            break
    return (f"var i = 0;\nwhile (true) {{\n  i += {k};\n  if (i > {n}) break;\n}}\nprint(i);", i, "The first multiple of k above n.")


def l_sum_while_less(r):
    t = r.randint(15, 40)
    s, i = 0, 0
    while s < t:
        i += 1
        s += i
    return (f"var s = 0, i = 0;\nwhile (s < {t}) {{\n  i++;\n  s += i;\n}}\nprint(i);", i, "Add 1, 2, 3 ... until the total reaches the limit: i is the last number added.")


def l_max_loop(r):
    xs = ints(r, 5, 1, 40)
    return (f"var best = 0;\nfor (var x in {lit(xs)}) {{\n  if (x > best) best = x;\n}}\nprint(best);", max(xs), "best remembers the biggest item seen so far.")


def l_count_greater(r):
    xs = ints(r, 6, 1, 30)
    t = r.randint(8, 20)
    c = 0
    for x in xs:
        if x > t:
            c += 1
    return (f"var c = 0;\nfor (var x in {lit(xs)}) {{\n  if (x > {t}) c++;\n}}\nprint(c);", c, "c counts the items above the limit.")


def l_running(r):
    xs = ints(r, 4, 1, 9)
    out, t = [], 0
    for x in xs:
        t += x
        out.append(t)
    return (f"var t = 0;\nvar out = <int>[];\nfor (var x in {lit(xs)}) {{\n  t += x;\n  out.add(t);\n}}\nprint(out);", out, "A running total: each item is added to the sum so far.")


def l_swap(r):
    a, b = r.sample(range(2, 10), 2)
    n = r.randint(2, 5)
    x, y = a, b
    for _ in range(n):
        x, y = y, x
    return (f"var a = {a}, b = {b};\nfor (var i = 0; i < {n}; i++) {{\n  var t = a;\n  a = b;\n  b = t;\n}}\nprint('$a$b');", f"{x}{y}", "Each turn swaps the two: an even number of turns puts them back.")


def l_shrink(r):
    xs = ints(r, 6, 1, 20)
    out = [x for x in xs if x % 2 == 0]
    return (f"var xs = {lit(xs)};\nxs.removeWhere((x) => x.isOdd);\nvar c = 0;\nfor (var x in xs) c += x;\nprint(c);", sum(out), "removeWhere drops the odd items first; the loop adds what is left.")


def l_string_rev(r):
    w = words(r, 1)[0]
    return (f"var s = '';\nfor (var i = '{w}'.length - 1; i >= 0; i--) {{\n  s += '{w}'[i];\n}}\nprint(s);", w[::-1], "Walking from the last index down to 0 reverses the word.")


def l_after_forin(r):
    xs = ints(r, 4, 1, 9)
    return (f"var last;\nfor (var x in {lit(xs)}) {{\n  last = x * 2;\n}}\nprint(last);", xs[-1] * 2, "last holds the value from the final turn.")


def l_empty(r):
    return ("var c = 0;\nfor (var x in <int>[]) {\n  c++;\n}\nprint(c);", 0, "An empty list gives no turns at all.")


LOOPS: list[Maker] = [R(f) for f in (
    l_sum, l_sum_lt, l_step, l_last_i, l_after, l_countdown, l_double, l_double_n, l_halve, l_digits, l_reverse,
    l_do_once, l_while_never, l_do_count, l_post_incr_cond, l_pre_incr_cond, l_post_expr, l_post_expr_i,
    l_post_value, l_break, l_continue, l_break_last, l_find, l_skip_multiple, l_squares, l_label_continue,
    l_label_break, l_inner_break, l_nested, l_triangle, l_table, l_closures, l_closures_while, l_foreach,
    l_forin_reversed, l_vowels, l_every_other, l_build_up, l_fib, l_factorial, l_collatz, l_gcd, l_two_vars,
    l_two_vars_for, l_mod_loop, l_modify_i, l_while_true, l_sum_while_less, l_max_loop, l_count_greater, l_running,
    l_swap, l_shrink, l_string_rev, l_after_forin, l_empty)]
