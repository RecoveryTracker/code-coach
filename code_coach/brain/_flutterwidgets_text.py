"""Flutter widgets pack, activity 2: Text Shown.

What text does the screen end up showing? The Text widgets here are built from Dart expressions (arithmetic,
strings, lists, ternaries, `switch`, small helper functions, statements in a Builder) or sit under a widget that
decides which of them is on stage (IndexedStack, Offstage, Visibility, PageView, LayoutBuilder constraints). The
answer is always a number as digits - what `Text.data` holds, read by the oracle's check - so it can be typed. The
Dart is evaluated here by hand with plain Python on small positive numbers (`~/` and `%` agree with `//` and `%`).
"""

from __future__ import annotations


from ._flutterwidgets_kit import G, col, mk, row, template, text

TEMPLATES: list = []

#: The one Text on screen / all the Texts on screen, joined, as the oracle reads them.
SHOWN = "tester.widget<Text>(find.byType(Text)).data"
JOINED = "tester.widgetList<Text>(find.byType(Text)).map((t) => t.data).join()"
ASK = "the number the Text shows"
ASK_ALL = "the Texts on screen, joined (find.byType(Text))"


def shown_text(expr: str) -> G:
    """Text('${expr}')"""
    return G("Text", "'${" + expr + "}'")


def block(lines: list[str]) -> str:
    return "Builder(builder: (c) {\n" + "\n".join("  " + ln for ln in lines) + "\n})"


# ── Dart expressions ────────────────────────────────────────────────────

ARITH = [
    ("{a} + {b} * {c}", lambda a, b, c: a + b * c, "* binds tighter than +"),
    ("({a} + {b}) * {c}", lambda a, b, c: (a + b) * c, "the parentheses go first"),
    ("{a} * {b} - {c}", lambda a, b, c: a * b - c, "the product comes before the subtraction"),
    ("{a} + {b} ~/ {c}", lambda a, b, c: a + b // c, "~/ is integer division and binds like *"),
    ("{a} * {b} % {c}", lambda a, b, c: (a * b) % c, "* and % bind equally, left to right"),
    ("{a} + {b} % {c}", lambda a, b, c: a + b % c, "% is done before the +"),
    ("{a} * {b} ~/ {c}", lambda a, b, c: (a * b) // c, "left to right: multiply, then divide"),
    ("{a} - ({b} - {c})", lambda a, b, c: a - (b - c), "the inner parentheses first"),
]


@template(TEMPLATES)
def arithmetic(rng):
    fmt, fn, why = rng.choice(ARITH)
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 5)
    expr = fmt.format(a=a, b=b, c=c)
    ans = fn(a, b, c)
    return mk(ASK, shown_text(expr), ans, f"{expr} is {ans}: {why}.", SHOWN)


@template(TEMPLATES)
def digit_concat(rng):
    a, b, c = rng.randint(1, 9), rng.randint(1, 9), rng.randint(2, 4)
    forms = [
        (f"{a}.toString() + {b}.toString()", f"{a}{b}", "+ between two Strings joins their text, it does not add the numbers"),
        ("'${" + f"{a} + {b}" + "}${" + str(c) + "}'", f"{a + b}{c}",
         "the first interpolation is the sum, the second the digit; side by side they are just text"),
        ("'${" + f"{a} * {b}" + "}' + '" + str(c) + "'", f"{a * b}{c}", "the product's digits, then the text after the +"),
        (f"{a}.toString() + ({b} + {c}).toString()", f"{a}{b + c}", "the parentheses add first, then both sides are joined as text"),
    ]
    code, ans, why = rng.choice(forms)
    return mk(ASK, G("Text", code), ans, f"{why[0].upper() + why[1:]}: {ans}.", SHOWN)


@template(TEMPLATES)
def repeat_and_join(rng):
    d = rng.sample(range(1, 10), 4)
    kind = rng.choice(("repeat", "reversed", "take", "skip", "where", "sublist"))
    lst = "[" + ", ".join(map(str, d)) + "]"
    if kind == "repeat":
        n = rng.randint(2, 4)
        code, ans, why = f"'{d[0]}' * {n}", str(d[0]) * n, f"String * {n} repeats the text {n} times"
    elif kind == "reversed":
        code, ans, why = f"{lst}.reversed.join()", "".join(map(str, reversed(d))), "reversed walks the list backwards and join() glues the items together"
    elif kind == "take":
        n = rng.randint(2, 3)
        code, ans, why = f"{lst}.take({n}).join()", "".join(map(str, d[:n])), f"take({n}) keeps the first {n} items"
    elif kind == "skip":
        n = rng.randint(1, 2)
        code, ans, why = f"{lst}.skip({n}).join()", "".join(map(str, d[n:])), f"skip({n}) drops the first {n} items"
    elif kind == "where":
        k = rng.randint(3, 6)
        code, ans, why = f"{lst}.where((x) => x > {k}).join()", "".join(str(x) for x in d if x > k), f"only the items greater than {k} are joined"
        if not ans:
            raise_retry()
    else:
        i, j = 1, rng.randint(2, 3)
        code, ans, why = f"{lst}.sublist({i}, {j + 1}).join()", "".join(map(str, d[i:j + 1])), f"sublist({i}, {j + 1}) is items {i} to {j}"
    return mk(ASK, G("Text", code), ans, f"{why[0].upper() + why[1:]}: {ans}.", SHOWN)


def raise_retry():
    from ._flutter_model import Retry
    raise Retry()


@template(TEMPLATES)
def string_facts(rng):
    s = rng.choice(("banana", "flutter", "widget", "balance", "coconut", "pattern"))
    ch = rng.choice(sorted(set(s)))
    forms = [
        (f"'{s}'.length", str(len(s)), f"{s} has {len(s)} characters"),
        (f"'{s}'.indexOf('{ch}')", str(s.find(ch)), f"the first '{ch}' sits at index {s.find(ch)} (counting from 0)"),
        (f"'{s}'.lastIndexOf('{ch}')", str(s.rfind(ch)), f"the last '{ch}' sits at index {s.rfind(ch)}"),
        (f"'{s}'.replaceAll('{ch}', '').length", str(len(s) - s.count(ch)), f"removing every '{ch}' ({s.count(ch)} of them) leaves {len(s) - s.count(ch)} characters"),
        (f"'{s}'.split('{ch}').length", str(len(s.split(ch))), f"splitting at '{ch}' cuts the text into {len(s.split(ch))} pieces"),
        (f"'{s}'.substring({len(s) - 3}).length", "3", "substring(n) keeps everything from index n on: the last 3 characters"),
        (f"'{s}'.codeUnitAt(0)", str(ord(s[0])), f"'{s[0]}' has the code {ord(s[0])}"),
    ]
    code, ans, why = rng.choice(forms)
    return mk(ASK, shown_text(code), ans, f"{why[0].upper() + why[1:]}: {ans}.", SHOWN)


@template(TEMPLATES)
def list_facts(rng):
    xs = [rng.randint(1, 9) for _ in range(rng.randint(4, 5))]
    lst = "[" + ", ".join(map(str, xs)) + "]"
    k = rng.randint(2, 6)
    v = rng.choice(xs)
    forms = [
        (f"{lst}.where((x) => x > {k}).length", sum(1 for x in xs if x > k), f"{sum(1 for x in xs if x > k)} items are greater than {k}"),
        (f"{lst}.reduce((a, b) => a + b)", sum(xs), "reduce adds the items one by one"),
        (f"{lst}.reduce((a, b) => a > b ? a : b)", max(xs), "reduce keeps the bigger of each pair"),
        (f"{lst}.first + {lst}.last", xs[0] + xs[-1], "the first item plus the last"),
        (f"{lst}.indexOf({v})", xs.index(v), f"{v} is first found at index {xs.index(v)}"),
        (f"{lst}.map((x) => x * 2).last", xs[-1] * 2, "the last item, doubled"),
        (f"{lst}.toSet().length", len(set(xs)), "a Set keeps each value once"),
        (f"{lst}.where((x) => x.isEven).length", sum(1 for x in xs if x % 2 == 0), "the even items are counted"),
        (f"{lst}.skip(2).first", xs[2], "skip(2) drops two items, so first is item 2"),
    ]
    code, ans, why = rng.choice(forms)
    return mk(ASK, shown_text(code), ans, f"{why[0].upper() + why[1:]}: {ans}.", SHOWN)


@template(TEMPLATES)
def map_lookup(rng):
    vals = rng.sample(range(1, 10), 3)
    m = {"a": vals[0], "b": vals[1], "c": vals[2]}
    lit = "{" + ", ".join(f"'{k}': {v}" for k, v in m.items()) + "}"
    key = rng.choice(("a", "b", "c", "z"))
    form = rng.choice(("get", "default", "sum", "len"))
    if form == "get":
        key = rng.choice("abc")
        code, ans, why = f"{lit}['{key}']", m[key], f"the value stored under '{key}'"
    elif form == "default":
        code, ans, why = f"{lit}['{key}'] ?? 0", m.get(key, 0), ("the key is missing, so ?? falls back to 0" if key == "z" else f"the key is there: {m[key]}")
    elif form == "sum":
        code, ans, why = f"{lit}.values.reduce((a, b) => a + b)", sum(vals), "the values added up"
    else:
        code, ans, why = f"{lit}.keys.length", 3, "three keys"
    return mk(ASK, shown_text(code), ans, f"{why[0].upper() + why[1:]}: {ans}.", SHOWN)


@template(TEMPLATES)
def ternary_difference(rng):
    a, b = rng.sample(range(1, 10), 2)
    op = rng.choice((">", "<"))
    holds = (a > b) if op == ">" else (a < b)
    first, second = ((a, b), (b, a)) if op == ">" else ((b, a), (a, b))
    code = f"{a} {op} {b} ? '${{{first[0]} - {first[1]}}}' : '${{{second[0]} - {second[1]}}}'"
    pick = first if holds else second
    ans = pick[0] - pick[1]
    return mk(ASK, G("Text", code), ans, f"{a} {op} {b} is {'true' if holds else 'false'}, so the "
              f"{'first' if holds else 'second'} text is used: {pick[0]} - {pick[1]} = {ans}.", SHOWN)


@template(TEMPLATES)
def nested_ternary(rng):
    n = rng.randint(1, 9)
    t1, t2 = rng.randint(2, 4), rng.randint(5, 8)
    a, b, c = rng.sample(range(1, 10), 3)
    code = f"{n} < {t1} ? '{a}' : {n} < {t2} ? '{b}' : '{c}'"
    ans = a if n < t1 else (b if n < t2 else c)
    return mk(ASK, G("Text", code), ans, f"{n} is {'below' if n < t1 else 'not below'} {t1}"
              + ("" if n < t1 else f" and {'below' if n < t2 else 'not below'} {t2}") + f": the Text shows {ans}.", SHOWN)


@template(TEMPLATES)
def switch_expression(rng):
    n = rng.randint(0, 5)
    if rng.random() < 0.5:
        vals = rng.sample(range(1, 10), 3)
        code = f"switch ({n}) {{ 1 => '{vals[0]}', 2 => '{vals[1]}', 3 => '{vals[2]}', _ => '0' }}"
        ans = {1: vals[0], 2: vals[1], 3: vals[2]}.get(n, 0)
        why = f"the case matching {n}" if n in (1, 2, 3) else f"{n} matches no case, so the _ case gives 0"
    else:
        t1, t2 = rng.randint(1, 2), rng.randint(3, 4)
        vals = rng.sample(range(1, 10), 3)
        code = f"switch ({n}) {{ < {t1} => '{vals[0]}', < {t2} => '{vals[1]}', _ => '{vals[2]}' }}"
        ans = vals[0] if n < t1 else (vals[1] if n < t2 else vals[2])
        why = f"cases are tried in order and the first match wins: {n} is {'< ' + str(t1) if n < t1 else ('< ' + str(t2) if n < t2 else 'neither')}"
    return mk(ASK, G("Text", code), ans, f"{why[0].upper() + why[1:]}, so the Text shows {ans}.", SHOWN)


# ── statements in a Builder ─────────────────────────────────────────────

@template(TEMPLATES)
def builder_for(rng):
    start = rng.randint(1, 3)
    k = rng.randint(3, 5)
    op = rng.choice(("n += i", "n *= 2", "n = n * 2 + 1", "n += i * i", "n = n + 2"))
    n = start
    for i in range(k):
        if op == "n += i":
            n += i
        elif op == "n *= 2":
            n *= 2
        elif op == "n = n * 2 + 1":
            n = n * 2 + 1
        elif op == "n += i * i":
            n += i * i
        else:
            n = n + 2
    code = block([f"var n = {start};", f"for (var i = 0; i < {k}; i++) {{", f"  {op};", "}", "return Text('$n');"])
    return mk(ASK, code, n, f"The loop body runs for i = 0 to {k - 1}, starting from {start}; it ends with n = {n}.", SHOWN)


@template(TEMPLATES)
def builder_conditional_sum(rng):
    k = rng.randint(6, 10)
    m = rng.randint(2, 4)
    use_continue = rng.random() < 0.5
    n = 0
    for i in range(1, k + 1):
        if i % m == 0:
            n += i
    if use_continue:
        lines = ["var n = 0;", f"for (var i = 1; i <= {k}; i++) {{", f"  if (i % {m} != 0) continue;", "  n += i;", "}", "return Text('$n');"]
    else:
        lines = ["var n = 0;", f"for (var i = 1; i <= {k}; i++) {{", f"  if (i % {m} == 0) n += i;", "}", "return Text('$n');"]
    return mk(ASK, block(lines), n, f"Only the multiples of {m} up to {k} are added: {n}.", SHOWN)


@template(TEMPLATES)
def builder_while(rng):
    start = rng.randint(20, 60)
    step = rng.choice((3, 4, 5, 6, 7))
    limit = rng.choice((0, 5, 10))
    n, steps = start, 0
    while n > limit:
        n -= step
        steps += 1
    show_steps = rng.random() < 0.5
    lines = [f"var n = {start};", "var steps = 0;", f"while (n > {limit}) {{", f"  n -= {step};", "  steps++;", "}",
             "return Text('$steps');" if show_steps else "return Text('$n');"]
    ans = steps if show_steps else n
    return mk(ASK, block(lines), ans, f"n starts at {start} and drops by {step} while it is above {limit}; it stops at {n} after {steps} steps, "
              f"and the Text shows {'steps' if show_steps else 'n'}.", SHOWN)


@template(TEMPLATES)
def builder_if_chain(rng):
    start = rng.randint(1, 9)
    t1, t2 = rng.randint(2, 4), rng.randint(5, 7)
    a, b, c = rng.randint(1, 4), rng.randint(1, 4), rng.randint(2, 3)
    n = start
    if n > t2:
        n -= a
    elif n > t1:
        n += b
    else:
        n = 0
    n *= c
    lines = [f"var n = {start};", f"if (n > {t2}) n -= {a};", f"else if (n > {t1}) n += {b};", "else n = 0;", f"return Text('${{n * {c}}}');"]
    return mk(ASK, block(lines), n, f"Start {start}: exactly one branch runs, then n is multiplied by {c}: {n}.", SHOWN)


@template(TEMPLATES)
def closure_capture(rng):
    a, b = rng.randint(1, 5), rng.randint(1, 5)
    kind = rng.choice(("late", "loop"))
    if kind == "late":
        # a closure reads the VARIABLE, not the value it had when the closure was made
        lines = [f"var x = {a};", "int f() => x + 1;", f"x = {b};", "return Text('${f()}');"]
        ans = b + 1
        why = f"f reads x when it is called, and by then x is {b}: {b} + 1 = {ans}."
    else:
        k = rng.randint(3, 4)
        j = rng.randint(0, k - 1)
        lines = ["final fs = <int Function()>[];", f"for (var i = 0; i < {k}; i++) {{", f"  fs.add(() => i * {a});", "}",
                 f"return Text('${{fs[{j}]()}}');"]
        ans = j * a
        why = f"each pass of a for loop has its own i, so fs[{j}] remembers i = {j}: {j} * {a} = {ans}."
    return mk(ASK, block(lines), ans, why, SHOWN)


# ── helper functions (declared above the widget) ────────────────────────

@template(TEMPLATES)
def helper_branches(rng):
    t = rng.randint(3, 6)
    a, b = rng.randint(2, 4), rng.randint(2, 5)
    n = rng.randint(1, 9)
    decl = f"int f(int n) {{\n  if (n > {t}) {{\n    return n - {a};\n  }}\n  return n * {b};\n}}"
    ans = n - a if n > t else n * b
    return mk(ASK, shown_text(f"f({n})"), ans, f"f({n}): {n} is {'above' if n > t else 'not above'} {t}, so it returns "
              f"{n} {'-' if n > t else '*'} {a if n > t else b} = {ans}.", SHOWN, decls=decl)


@template(TEMPLATES)
def helper_recursion(rng):
    kind = rng.choice(("fact", "fib", "sumto", "pow", "digits"))
    if kind == "fact":
        n = rng.randint(3, 5)
        decl = "int f(int n) {\n  return n <= 1 ? 1 : n * f(n - 1);\n}"
        ans, why = 1, ""
        for i in range(2, n + 1):
            ans *= i
        why = f"f({n}) multiplies {n} * {n - 1} * ... * 1"
    elif kind == "fib":
        n = rng.randint(4, 7)
        decl = "int f(int n) {\n  return n < 2 ? n : f(n - 1) + f(n - 2);\n}"
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        ans, why = a, f"f({n}) is the {n}th Fibonacci number (0, 1, 1, 2, 3, 5, 8, ...)"
    elif kind == "sumto":
        n = rng.randint(4, 8)
        decl = "int f(int n) {\n  if (n == 0) return 0;\n  return n + f(n - 1);\n}"
        ans = sum(range(n + 1))
        why = f"f({n}) adds {n} + {n - 1} + ... + 1"
    elif kind == "pow":
        base, n = rng.randint(2, 3), rng.randint(2, 4)
        decl = f"int f(int n) {{\n  return n == 0 ? 1 : {base} * f(n - 1);\n}}"
        ans = base ** n
        why = f"f({n}) multiplies {base} together {n} times"
    else:
        n = rng.choice((123, 405, 98, 7531, 666))
        decl = "int f(int n) {\n  return n < 10 ? n : n % 10 + f(n ~/ 10);\n}"
        ans = sum(int(c) for c in str(n))
        why = f"f({n}) adds the digits of {n}"
    return mk(ASK, shown_text(f"f({n})"), ans, f"{why} = {ans}.", SHOWN, decls=decl)


@template(TEMPLATES)
def helper_default_argument(rng):
    by, n = rng.randint(2, 4), rng.randint(2, 6)
    given = rng.random() < 0.5
    other = rng.choice([x for x in range(2, 7) if x != by])
    decl = f"int scale(int n, {{int by = {by}}}) {{\n  return n * by;\n}}"
    call = f"scale({n}, by: {other})" if given else f"scale({n})"
    ans = n * (other if given else by)
    return mk(ASK, shown_text(call), ans, ("The named argument by: replaces the default" if given else f"by was not given, so it is the default {by}")
              + f": {n} * {other if given else by} = {ans}.", SHOWN, decls=decl)


# ── which Text is on stage ──────────────────────────────────────────────

@template(TEMPLATES)
def indexed_stack_shown(rng):
    d = rng.sample(range(1, 10), rng.randint(3, 4))
    i = rng.randrange(len(d))
    w = G("IndexedStack", index=str(i), children=[text(str(x)) for x in d])
    return mk(ASK, w, d[i], f"IndexedStack builds every child but shows only the one at index {i}; find.byType skips the offstage "
              f"ones, leaving {d[i]}.", SHOWN)


@template(TEMPLATES)
def hidden_wrappers(rng):
    d = rng.sample(range(1, 10), 4)
    kinds = [rng.choice(("off_true", "off_false", "vis_false", "vis_keep", "vis_true", "opacity0", "plain")) for _ in range(rng.randint(3, 4))]
    kids, found = [], []
    for k, x in zip(kinds, d):
        t = text(str(x))
        if k == "off_true":
            kids.append(G("Offstage", child=t))
        elif k == "off_false":
            kids.append(G("Offstage", offstage="false", child=t))
            found.append(x)
        elif k == "vis_false":
            kids.append(G("Visibility", visible="false", child=t))
        elif k == "vis_keep":
            kids.append(G("Visibility", visible="false", maintainState="true", child=t))
        elif k == "vis_true":
            kids.append(G("Visibility", visible="true", child=t))
            found.append(x)
        elif k == "opacity0":
            kids.append(G("Opacity", opacity="0", child=t))
            found.append(x)
        else:
            kids.append(t)
            found.append(x)
    if not found:
        raise_retry()
    ans = "".join(map(str, found))
    return mk(ASK_ALL, col(*kids), ans, "Offstage(offstage: true), an invisible Visibility (with or without maintainState) are skipped; "
              f"Opacity 0, a visible Visibility and plain Texts are found, in order: {ans}.", JOINED)


@template(TEMPLATES)
def visibility_replacement(rng):
    a, b, c = rng.sample(range(1, 10), 3)
    vis = rng.random() < 0.5
    keep = rng.random() < 0.3
    kw = {"visible": "true" if vis else "false"}
    if keep:
        kw["maintainState"] = "true"
    w = col(G("Visibility", **kw, replacement=text(str(a)), child=text(str(b))), text(str(c)))
    if vis:
        found, why = [b, c], "visible: the child is shown and the replacement is not built"
    elif keep:
        found, why = [c], "maintainState keeps the child offstage (skipped) and no replacement is used"
    else:
        found, why = [a, c], "invisible without maintainState: the replacement stands in for the child"
    ans = "".join(map(str, found))
    return mk(ASK_ALL, w, ans, f"{why[0].upper() + why[1:]}. Found in order: {ans}.", JOINED)


@template(TEMPLATES)
def pageview_initial(rng):
    kind = rng.choice(("children", "builder"))
    if kind == "children":
        d = rng.sample(range(1, 10), 3)
        i = rng.randint(0, 2)
        w = G("PageView", controller=f"PageController(initialPage: {i})", children=[text(str(x)) for x in d])
        ans = d[i]
    else:
        n, mul = rng.randint(4, 6), rng.randint(2, 4)
        i = rng.randint(0, n - 1)
        w = G("PageView.builder", controller=f"PageController(initialPage: {i})", itemCount=str(n),
              itemBuilder="(c, i) => Text('${i * %d}')" % mul)
        ans = i * mul
    return mk(ASK_ALL, w, ans, f"A PageView shows one page at a time and builds only that one (no cache area); initialPage is {i}: {ans}.", JOINED)


@template(TEMPLATES)
def loop_last_text(rng):
    n = rng.randint(4, 8)
    m = rng.randint(2, 3)
    expr = rng.choice(("i * i", "i + 10", "i * 2"))
    cond = rng.choice((f"i % {m} == 0", f"i % {m} == 1", f"i > {n // 2}"))
    use = {f"i % {m} == 0": lambda i: i % m == 0, f"i % {m} == 1": lambda i: i % m == 1, f"i > {n // 2}": lambda i: i > n // 2}[cond]
    fn = {"i * i": lambda i: i * i, "i + 10": lambda i: i + 10, "i * 2": lambda i: i * 2}[expr]
    vals = [fn(i) for i in range(1, n + 1) if use(i)]
    if not vals:
        raise_retry()
    which = rng.choice(("first", "last"))
    w = col(f"for (var i = 1; i <= {n}; i++) if ({cond}) Text('${{{expr}}}')")
    ans = vals[0] if which == "first" else vals[-1]
    check = f"tester.widgetList<Text>(find.byType(Text)).{which}.data"
    return mk(f"the {which} Text the list builds", w, ans, f"The loop makes a Text for i = {', '.join(str(i) for i in range(1, n + 1) if use(i))}"
              f" (texts {', '.join(map(str, vals))}); the {which} one is {ans}.", check)


# ── what the constraints make of a LayoutBuilder ───────────────────────

def _lb(dim: str, scale: int) -> G:
    attr = "maxWidth" if dim == "w" else "maxHeight"
    return G("LayoutBuilder", builder="(c, bc) => Text('${bc.%s ~/ %d}')" % (attr, scale))


@template(TEMPLATES)
def layout_builder_beside(rng):
    horizontal = rng.random() < 0.5
    p = rng.choice((0, 10, 20))
    s = rng.choice((50, 80, 100))
    total = (400 if horizontal else 300) - 2 * p - s
    scale = rng.choice((5, 10))
    inner = row(G("SizedBox", width=str(s)), G("Expanded", child=_lb("w", scale))) if horizontal else \
        col(G("SizedBox", height=str(s)), G("Expanded", child=_lb("h", scale)))
    w = G("Padding", padding=f"EdgeInsets.all({p})", child=inner) if p else inner
    ans = total // scale
    return mk(ASK, w, ans, f"The {'width' if horizontal else 'height'} left for the Expanded is "
              f"{400 if horizontal else 300}{f' - 2 * {p}' if p else ''} - {s} = {total}; ~/ {scale} gives {ans}.", SHOWN)


@template(TEMPLATES)
def layout_builder_shares(rng):
    f1, f2 = rng.choice(((1, 1), (1, 3), (2, 3), (1, 4), (3, 2)))
    total = 400
    pad_ = rng.choice((0, 10, 20, 30))
    space = total - 2 * pad_
    if space % (f1 + f2):
        raise_retry()
    which = rng.choice((0, 1))
    flexes = (f1, f2)
    widths = [space // (f1 + f2) * f for f in flexes]
    kids = [G("Expanded", flex=str(f), child=G("LayoutBuilder", builder="(c, bc) => Text('${bc.maxWidth ~/ 10}')")) if i == which
            else G("Expanded", flex=str(f), child=G("Placeholder")) for i, f in enumerate(flexes)]
    inner = row(*kids)
    w = G("Padding", padding=f"EdgeInsets.all({pad_})", child=inner) if pad_ else inner
    ans = widths[which] // 10
    return mk(ASK, w, ans, f"The Row hands out {space} pixels in the ratio {f1}:{f2}: {widths[0]} and {widths[1]}. The LayoutBuilder is in the "
              f"{'first' if which == 0 else 'second'} Expanded, {widths[which]} wide; ~/ 10 gives {ans}.", SHOWN)


# ── counting a text on screen ───────────────────────────────────────────

@template(TEMPLATES)
def find_text_mod(rng):
    n = rng.randint(5, 8)
    m = rng.randint(2, 4)
    target = rng.randrange(m)
    w = col(f"for (var i = 0; i < {n}; i++) Text('${{i % {m}}}')")
    ans = sum(1 for i in range(n) if i % m == target)
    return mk(f"find.text('{target}') matches how many?", w, ans, f"i % {m} runs through 0..{m - 1} again and again for i = 0..{n - 1}; "
              f"{ans} of the {n} Texts say {target}.", f"count(find.text('{target}'))")


@template(TEMPLATES)
def find_text_in_list(rng):
    xs = [rng.randint(1, 4) for _ in range(rng.randint(5, 7))]
    target = rng.randint(1, 4)
    w = col(f"for (final x in {xs}) Text('$x')")
    ans = xs.count(target)
    return mk(f"find.text('{target}') matches how many?", w, ans, f"{ans} of the numbers in the list are {target}, and each makes its own Text.",
              f"count(find.text('{target}'))")


@template(TEMPLATES)
def text_rich_plain(rng):
    d = rng.sample(range(1, 10), 5)
    shape = rng.choice(("flat", "nested", "parent"))
    t = lambda x: f"TextSpan(text: '{x}')"  # noqa: E731
    if shape == "flat":
        span = f"TextSpan(children: [{t(d[0])}, {t(d[1])}, {t(d[2])}])"
        ans = f"{d[0]}{d[1]}{d[2]}"
    elif shape == "nested":
        span = f"TextSpan(children: [{t(d[0])}, TextSpan(children: [{t(d[1])}, {t(d[2])}]), {t(d[3])}])"
        ans = f"{d[0]}{d[1]}{d[2]}{d[3]}"
    else:
        span = f"TextSpan(text: '{d[0]}', children: [{t(d[1])}, TextSpan(text: '{d[2]}', children: [{t(d[3])}])])"
        ans = f"{d[0]}{d[1]}{d[2]}{d[3]}"
    why = {"flat": "the spans' texts are joined in order", "nested": "a span without text of its own just passes its children's through",
           "parent": "a span's own text comes first, then its children's"}[shape]
    return mk("the plain text of the span", G("Text.rich", span), ans, f"{why[0].upper() + why[1:]}: {ans}.",
              "tester.widget<Text>(find.byType(Text)).textSpan!.toPlainText()")
