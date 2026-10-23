"""Flutter state pack, Tap Count: the number a Text shows after some taps.

The lesson is what setState does and does not do: it runs its callback at once and marks the widget dirty, the NEXT
frame builds it again; changing a variable with no setState changes nothing on screen; a variable declared inside the
builder starts again at every build; a widget made once and reused is not made again; and a tap that never arrives
(IgnorePointer, AbsorbPointer, a null onTap) changes nothing. Each answer is simulated by hand below.
"""

from __future__ import annotations

import random

from ._flutterstate_common import READ, iife, item, sb_tap, taps, template
from ._model import Maker

INITS = (0, 0, 0, 1, 2, 3, 5)


def _ask(n: int) -> str:
    return f"shown after {n} taps?"


def _bump(rng: random.Random) -> str:
    return rng.choice(("n++", "n += 1", "n = n + 1", "++n"))


# ── Plain counters ─────────────────────────────────────────────────────

def plain(rng):
    n, i = rng.choice((2, 3, 4, 5)), rng.choice(INITS)
    ontap = rng.choice((f"() => setState(() => {_bump(rng)})", f"() => setState(() {{ {_bump(rng)}; }})"))
    code = iife(f"var n = {i};", sb_tap(ontap, "$n"))
    return item(_ask(n), code, i + n, f"Each tap runs setState, which adds 1 and rebuilds, so {n} taps from {i} show {i + n}.",
                taps(n) + READ)


def no_setstate(rng):
    n, i = rng.choice((2, 3, 4, 5)), rng.choice(INITS)
    code = iife(f"var n = {i};", sb_tap(f"() => {_bump(rng)}", "$n"))
    return item(_ask(n), code, i, f"n changes, but nothing calls setState, so the Text is never rebuilt and still shows {i}.",
                taps(n) + READ)


def mutate_then_set(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice(INITS)
    code = iife(f"var n = {i};", sb_tap("() { n++; setState(() {}); }", "$n"))
    return item(_ask(n), code, i + n, f"setState with an empty callback still rebuilds, and n was already bumped: {i + n}.",
                taps(n) + READ)


def set_then_mutate(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice(INITS)
    code = iife(f"var n = {i};", sb_tap("() { setState(() {}); n++; }", "$n"))
    return item(_ask(n), code, i + n,
                f"setState only marks the widget dirty; the rebuild comes after the handler, when n was already bumped: {i + n}.",
                taps(n) + READ)


def step(rng):
    n, k = rng.choice((2, 3, 4)), rng.choice((2, 3, 5))
    code = iife("var n = 0;", sb_tap(f"() => setState(() => n += {k})", "$n"))
    return item(_ask(n), code, n * k, f"Every tap adds {k} inside setState: {n} x {k} = {n * k}.", taps(n) + READ)


def twice(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var n = 0;", sb_tap("() { setState(() => n++); setState(() => n++); }", "$n"))
    return item(_ask(n), code, 2 * n, f"Both callbacks run at once (one rebuild shows the result): 2 per tap, {2 * n}.", taps(n) + READ)


def cap_if(rng):
    n, cap, i = rng.choice((4, 5)), rng.choice((2, 3)), rng.choice((0, 1))
    code = iife(f"var n = {i};", sb_tap(f"() {{ if (n < {cap}) setState(() => n++); }}", "$n"))
    got = i
    for _ in range(n):
        if got < cap:
            got += 1
    return item(_ask(n), code, got, f"The if lets setState run only while n < {cap}, so it stops at {got}.", taps(n) + READ)


def cap_null(rng):
    n, cap = rng.choice((4, 5)), rng.choice((2, 3))
    code = iife("var n = 0;", sb_tap(f"n < {cap} ? () => setState(() => n++) : null", "$n"))
    got = min(n, cap)
    return item(_ask(n), code, got, f"Once n reaches {cap} the onTap is null, so later taps do nothing: {got}.", taps(n) + READ)


def doubling(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var n = 1;", sb_tap("() => setState(() => n *= 2)", "$n"))
    return item(_ask(n), code, 2 ** n, f"n doubles at each tap: 1 doubled {n} times is {2 ** n}.", taps(n) + READ)


def doubling_plus(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var n = 0;", sb_tap("() => setState(() => n = n * 2 + 1)", "$n"))
    got = 0
    for _ in range(n):
        got = got * 2 + 1
    return item(_ask(n), code, got, f"0, 1, 3, 7, 15...: after {n} taps n is {got}.", taps(n) + READ)


def countdown(rng):
    n = rng.choice((2, 3, 4))
    s = n + rng.choice((1, 2, 3, 5))
    code = iife(f"var n = {s};", sb_tap("() => setState(() => n--)", "$n"))
    return item(_ask(n), code, s - n, f"Each tap subtracts 1 inside setState: {s} - {n} = {s - n}.", taps(n) + READ)


def derived_times(rng):
    n, k = rng.choice((2, 3, 4, 5)), rng.choice((2, 3, 4))
    code = iife("var n = 0;", sb_tap("() => setState(() => n++)", f"${{n * {k}}}"))
    return item(_ask(n), code, n * k, f"n is {n} after {n} taps, and the Text shows n * {k} = {n * k}.", taps(n) + READ)


def derived_mod(rng):
    k = rng.choice((2, 3, 4))
    n = rng.choice([x for x in (3, 4, 5, 6, 7) if x % k])
    code = iife("var n = 0;", sb_tap("() => setState(() => n++)", f"${{n % {k}}}"))
    return item(_ask(n), code, n % k, f"n is {n}; the Text shows the remainder of {n} divided by {k}, {n % k}.", taps(n) + READ)


def toggle(rng):
    n, a, b = rng.choice((2, 3, 4, 5)), *rng.sample((3, 4, 7, 8, 9), 2)
    start = rng.choice((True, False))
    code = iife(f"var f = {str(start).lower()};", sb_tap("() => setState(() => f = !f)", f"${{f ? {a} : {b}}}"))
    f = start
    for _ in range(n):
        f = not f
    return item(_ask(n), code, a if f else b, f"f starts {str(start).lower()} and flips {n} times, ending {str(f).lower()}: the Text shows {a if f else b}.",
                taps(n) + READ)


def list_grows(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    lst = ", ".join(["0"] * i)
    code = iife(f"var xs = [{lst}];", sb_tap("() => setState(() => xs.add(0))", "${xs.length}"))
    return item(_ask(n), code, i + n, f"Each tap adds an item inside setState and rebuilds: the length is {i + n}.", taps(n) + READ)


def list_no_set(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    lst = ", ".join(["0"] * i)
    code = iife(f"var xs = [{lst}];", sb_tap("() => xs.add(0)", "${xs.length}"))
    return item(_ask(n), code, i, f"The list grows, but without setState the Text is never rebuilt: it still shows {i}.", taps(n) + READ)


def lagging(rng):
    k = rng.choice((2, 3))
    n = rng.choice([x for x in (4, 5, 6, 7) if x % k])
    code = iife("var n = 0;", sb_tap(f"() {{ n++; if (n % {k} == 0) setState(() {{}}); }}", "$n"))
    return item(_ask(n), code, (n // k) * k,
                f"n counts every tap, but the screen is only rebuilt when n is a multiple of {k}: it last showed {(n // k) * k}.", taps(n) + READ)


def odd_even(rng):
    n = rng.choice((2, 3, 4, 5))
    code = iife("var n = 0;", sb_tap("() => setState(() => n += n.isEven ? 1 : 3)", "$n"))
    got = 0
    for _ in range(n):
        got += 1 if got % 2 == 0 else 3
    return item(_ask(n), code, got, f"Even n adds 1, odd n adds 3: 0, 1, 4, 5, 8... so after {n} taps n is {got}.", taps(n) + READ)


def two_steps(rng):
    n = rng.choice((2, 3))
    a, m = rng.choice((1, 2)), rng.choice((2, 3))
    code = iife("var n = 0;", sb_tap(f"() => setState(() {{ n += {a}; n *= {m}; }})", "$n"))
    got = 0
    for _ in range(n):
        got = (got + a) * m
    return item(_ask(n), code, got, f"One tap does n = (n + {a}) * {m}; after {n} taps that is {got}.", taps(n) + READ)


# ── Taps that never arrive, or arrive anyway ───────────────────────────

def ignored(rng):
    n, i = rng.choice((2, 3)), rng.choice((0, 1, 2))
    which = rng.choice(("IgnorePointer", "AbsorbPointer"))
    code = iife(f"var n = {i};", sb_tap("() => setState(() => n++)", "$n", wrap=f"{which}(child: @)"))
    return item(_ask(n), code, i, f"{which} stops the taps before they reach the GestureDetector, so n stays {i}.", taps(n) + READ)


def not_ignored(rng):
    n = rng.choice((2, 3, 4))
    which, flag = rng.choice((("IgnorePointer", "ignoring"), ("AbsorbPointer", "absorbing")))
    code = iife("var n = 0;", sb_tap("() => setState(() => n++)", "$n", wrap=f"{which}({flag}: false, child: @)"))
    return item(_ask(n), code, n, f"{flag}: false lets the taps through, so it counts them all: {n}.", taps(n) + READ)


def invisible(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var n = 0;", sb_tap("() => setState(() => n++)", "$n", wrap="Opacity(opacity: 0, child: @)"))
    return item(_ask(n), code, n, f"A fully transparent widget is still there and still takes taps: {n}.", taps(n) + READ)


def long_press(rng):
    a, b = rng.choice((1, 2, 3)), rng.choice((1, 2))
    k = rng.choice((5, 10))
    gd = f"GestureDetector(\n      onTap: () => s(() => n++), onLongPress: () => s(() => n += {k}),\n      child: Text('$n'))"
    code = iife("var n = 0;", f"StatefulBuilder(builder: (c, s) => {gd})")
    check = taps(a) + "for (var i = 0; i < %d; i++) { await tester.longPress(find.byType(GestureDetector)); await tester.pump(); }\n" % b + READ
    return item(f"shown after {a} tap{'s' if a > 1 else ''} and {b} long press{'es' if b > 1 else ''}?", code, a + k * b,
                f"A tap adds 1 and a long press adds {k}: {a} + {b} x {k} = {a + k * b}.", check)


# ── The same ideas with a class (terse members) ────────────────────────

CLS_HEAD = "class A extends StatefulWidget {\n  createState() => S();\n}\nclass S extends State<A> {\n"


def cls_plain(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = (CLS_HEAD + f"  int n = {i};\n  build(c) => GestureDetector(\n      onTap: () => setState(() => n++), child: Text('$n'));\n}}\nA()")
    return item(_ask(n), code, i + n, f"n lives in the State and is bumped inside setState, so every tap shows: {i + n}.",
                taps(n) + READ)


def previous(rng):
    n = rng.choice((2, 3, 4, 5))
    code = iife("var n = 0, p = 0;", sb_tap("() => setState(() { p = n; n++; })", "$p"))
    return item(_ask(n), code, n - 1, f"The Text shows p, the value n had BEFORE the last tap: after {n} taps n is {n} and p is {n - 1}.",
                taps(n) + READ)


def cls_no_set(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = (CLS_HEAD + f"  int n = {i};\n  build(c) => GestureDetector(\n      onTap: () => n++, child: Text('$n'));\n}}\nA()")
    return item(_ask(n), code, i, f"The State's n changes, but without setState build never runs again: the Text still shows {i}.",
                taps(n) + READ)


def stale_widget(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = iife(f"var n = {i}, t = Text('{i}');",
                "StatefulBuilder(builder: (c, setState) => GestureDetector(\n      onTap: () => setState(() => n++), child: t))")
    return item(_ask(n), code, i, f"n grows and the builder reruns, but t is the same old Text made once with {i}: {i}.",
                taps(n) + READ)


def fresh_widget(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = iife(f"var n = {i};",
                "StatefulBuilder(builder: (c, setState) {\n    var t = Text('$n');\n    return GestureDetector(\n        onTap: () => setState(() => n++), child: t);\n  })")
    return item(_ask(n), code, i + n, f"t is made again inside the builder at every rebuild, so it shows the new n: {i + n}.",
                taps(n) + READ)


def builder_local(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = (f"StatefulBuilder(builder: (c, setState) {{\n  var n = {i};\n  return GestureDetector(\n"
            "      onTap: () => setState(() => n++), child: Text('$n'));\n})")
    return item(_ask(n), code, i, f"n is declared inside the builder, so each rebuild starts it again at {i}: the Text always shows {i}.",
                taps(n) + READ)


def _t(name, fn):
    return template(name, fn)


TEMPLATES: tuple[Maker, ...] = (
    _t("plain", plain), _t("no_setstate", no_setstate), _t("mutate_then_set", mutate_then_set),
    _t("set_then_mutate", set_then_mutate), _t("step", step), _t("twice", twice), _t("cap_if", cap_if),
    _t("cap_null", cap_null), _t("doubling", doubling), _t("doubling_plus", doubling_plus), _t("countdown", countdown),
    _t("derived_times", derived_times), _t("derived_mod", derived_mod), _t("toggle", toggle), _t("list_grows", list_grows),
    _t("list_no_set", list_no_set), _t("lagging", lagging), _t("odd_even", odd_even), _t("two_steps", two_steps),
    _t("ignored", ignored), _t("not_ignored", not_ignored), _t("invisible", invisible), _t("long_press", long_press),
    _t("cls_plain", cls_plain), _t("previous", previous), _t("cls_no_set", cls_no_set), _t("stale_widget", stale_widget),
    _t("fresh_widget", fresh_widget), _t("builder_local", builder_local),
)
