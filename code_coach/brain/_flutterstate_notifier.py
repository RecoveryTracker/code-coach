"""Flutter state pack, Notifier Says: what a ValueNotifier / ChangeNotifier and its builders show.

The rules written out by hand below:

* a ValueNotifier notifies only when `value` becomes something NOT `==` to the old value (ints, strings, bools and
  records compare by value; a list literal is a new object every time, a `const` list is one shared object);
* changing what is INSIDE the value (`v.value.add(1)`) does not notify, so nothing rebuilds and the screen is stale;
* a ChangeNotifier subclass notifies only when its method calls notifyListeners();
* a builder that listens (ValueListenableBuilder, ListenableBuilder, AnimatedBuilder) rebuilds on a notification, once
  per frame however many notifications came; code that merely READS `v.value` inside a plain Builder never rebuilds;
* a notification schedules the rebuild, so a value changed right AFTER notifyListeners() is still what the frame shows.

Counting: `Text('${++b}')` shows how many times its builder ran, so the answer is what is on the screen.
"""

from __future__ import annotations

from ._flutterstate_common import READ, iife, item, taps, template
from ._model import Maker

VLB = "ValueListenableBuilder(valueListenable: v, builder: (c, n, _) => Text('%s'))"


def _tap(op: str, inner: str, decl: str) -> str:
    arrow = "() " if op.startswith("{") else "() => "
    return iife(decl, f"GestureDetector(onTap: {arrow}{op}, child: {inner})")


def _ask(n: int) -> str:
    return f"shown after {n} taps?"


# ── What the Text shows ─────────────────────────────────────────────────

def n_incr(rng):
    n, i, k = rng.choice((2, 3, 4, 5)), rng.choice((0, 1, 2)), rng.choice((1, 1, 2, 3))
    op = "v.value++" if k == 1 else f"v.value += {k}"
    return item(_ask(n), _tap(op, VLB % "$n", f"var v = ValueNotifier({i});"), i + n * k,
                f"Every tap changes the value and ValueListenableBuilder rebuilds with it: {i} + {n} x {k} = {i + n * k}.",
                taps(n) + READ)


def n_same(rng):
    n, i, k = rng.choice((2, 3, 4)), rng.choice((0, 1)), rng.choice((5, 7, 9))
    return item(_ask(n), _tap(f"v.value = {k}", VLB % "$n", f"var v = ValueNotifier({i});"), k,
                f"The first tap sets {k}; the later taps set {k} again. Either way the Text shows {k}.", taps(n) + READ)


def n_toggle(rng):
    n, a, b = rng.choice((2, 3, 4, 5)), *rng.sample((3, 4, 7, 8, 9), 2)
    code = _tap("v.value = !v.value", VLB % f"${{n ? {a} : {b}}}", "var v = ValueNotifier(false);")
    on = n % 2 == 1
    return item(_ask(n), code, a if on else b, f"The bool flips {n} times from false, ending {str(on).lower()}: the Text shows {a if on else b}.",
                taps(n) + READ)


def n_list_inplace(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((1, 2))
    code = _tap("v.value.add(1)", VLB % "${n.length}", f"var v = ValueNotifier({[0] * i});")
    return item(_ask(n), code, i,
                f"add changes the list but the value is still the SAME list, so the notifier never notifies and the Text is not rebuilt: {i}.",
                taps(n) + READ)


def n_list_copy(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((1, 2))
    code = _tap("v.value += [1]", VLB % "${n.length}", f"var v = ValueNotifier({[0] * i});")
    return item(_ask(n), code, i + n, f"A new list each time is a different value, so every tap notifies and the length grows to {i + n}.",
                taps(n) + READ)


def n_read_only(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = _tap("v.value++", "Builder(builder: (c) => Text('${v.value}'))", f"var v = ValueNotifier({i});")
    return item(_ask(n), code, i,
                f"The Builder only READS v.value; it does not listen, so nothing rebuilds it and it still shows {i}.", taps(n) + READ)


def n_merge(rng):
    n, a, b = rng.choice((2, 3)), rng.choice((1, 2)), rng.choice((2, 3))
    code = iife("var p = ValueNotifier(0), q = ValueNotifier(0);",
                f"GestureDetector(onTap: () {{ p.value += {a}; q.value += {b}; }},\n      child: ListenableBuilder(listenable: Listenable.merge([p, q]),\n          builder: (c, _) => Text('${{p.value + q.value}}')))")
    return item(_ask(n), code, n * (a + b), f"The merged listenable fires for either, and the Text adds both: {n} x ({a} + {b}) = {n * (a + b)}.",
                taps(n) + READ)


def n_double(rng):
    n = rng.choice((2, 3, 4))
    code = _tap("v.value *= 2", VLB % "$n", "var v = ValueNotifier(1);")
    return item(_ask(n), code, 2 ** n, f"The value doubles at each tap: {2 ** n}.", taps(n) + READ)


def n_derived(rng):
    n, k = rng.choice((2, 3, 4)), rng.choice((2, 3, 5))
    code = _tap("v.value++", VLB % f"${{n * {k}}}", "var v = ValueNotifier(0);")
    return item(_ask(n), code, n * k, f"The builder shows the value times {k}: {n} x {k} = {n * k}.", taps(n) + READ)


# ── How many times the builder ran ──────────────────────────────────────

VLB_B = "ValueListenableBuilder(valueListenable: v, builder: (c, n, _) => Text('${++b}'))"


def _builds(op: str, decl: str, n: int, answer: int, why: str, inner: str = VLB_B):
    return item(_ask(n), _tap(op, inner, decl), answer, why, taps(n) + READ)


def b_incr(rng):
    n = rng.choice((2, 3, 4, 5))
    return _builds("v.value++", "var v = ValueNotifier(0), b = 0;", n, 1 + n,
                   f"Each tap changes the value, so the builder runs once at the start and once per tap: {1 + n}.")


def b_same_value(rng):
    n, k = rng.choice((2, 3, 4)), rng.choice((3, 5, 8))
    return _builds(f"v.value = {k}", "var v = ValueNotifier(0), b = 0;", n, 2,
                   f"Only the first tap changes the value (0 to {k}); the other taps set an equal value, which does not notify: 1 + 1 = 2.")


def b_already_equal(rng):
    n, k = rng.choice((2, 3, 4)), rng.choice((3, 5, 8))
    return _builds(f"v.value = {k}", f"var v = ValueNotifier({k}), b = 0;", n, 1,
                   f"The value is already {k}, so setting it again never notifies: the builder ran only once.")


def b_two_changes(rng):
    n = rng.choice((2, 3, 4))
    return _builds("{ v.value++; v.value++; }", "var v = ValueNotifier(0), b = 0;", n, 1 + n,
                   f"Two notifications in one tap still make ONE rebuild before the next frame: 1 + {n} = {1 + n}.")


def b_new_list(rng):
    n = rng.choice((2, 3, 4))
    return _builds("v.value = [1]", "var v = ValueNotifier([1]), b = 0;", n, 1 + n,
                   f"Every [1] is a new list, never == the old one, so each tap notifies: {1 + n}.", VLB_B)


def b_const_list(rng):
    n = rng.choice((2, 3, 4))
    return _builds("v.value = const [1]", "var v = ValueNotifier([1]), b = 0;", n, 2,
                   "The const list is one shared object: the first tap swaps in a different list (notifies), later taps set the very same one (silent): 2.")


def b_string(rng):
    n = rng.choice((2, 3, 4))
    return _builds("v.value = 'ab'", "var v = ValueNotifier('ab'), b = 0;", n, 1,
                   "Strings with the same characters are ==, so nothing changes and nothing notifies: 1.")


def b_record(rng):
    n = rng.choice((2, 3, 4))
    return _builds("v.value = (1, 2)", "var v = ValueNotifier((1, 2)), b = 0;", n, 1,
                   "Records compare by value, so (1, 2) is == (1, 2): no notification, one build.")


def b_merge(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var p = ValueNotifier(0), q = ValueNotifier(0), b = 0;",
                "GestureDetector(onTap: () { p.value++; q.value++; },\n      child: ListenableBuilder(listenable: Listenable.merge([p, q]),\n          builder: (c, _) => Text('${++b}')))")
    return item(_ask(n), code, 1 + n, f"Both notifiers fire, but the builder is rebuilt once per frame: 1 + {n} = {1 + n}.", taps(n) + READ)


def b_animated(rng):
    n = rng.choice((2, 3, 4))
    inner = "AnimatedBuilder(animation: v, builder: (c, _) => Text('${++b}'))"
    return _builds("v.value++", "var v = ValueNotifier(0), b = 0;", n, 1 + n,
                   f"AnimatedBuilder listens to any Listenable, a ValueNotifier included: {1 + n}.", inner)


LISTEN_K = "ListenableBuilder(listenable: v, builder: (c, _) => Text('$k'))"


def b_listener_count(rng):
    n = rng.choice((2, 3, 4))
    code = _tap("v.value++", LISTEN_K, "var v = ValueNotifier(0), k = 0;\n  v.addListener(() => k++);")
    return item(_ask(n), code, n, f"The listener runs once per change, and ours is added first, so k is {n} when the builder reads it.",
                taps(n) + READ)


def b_listener_same(rng):
    n = rng.choice((2, 3, 4))
    code = _tap("v.value = 4", LISTEN_K, "var v = ValueNotifier(0), k = 0;\n  v.addListener(() => k++);")
    return item(_ask(n), code, 1, "Only the first tap changes the value, so the listener runs once: 1.", taps(n) + READ)


def b_listenable(rng):
    n = rng.choice((2, 3, 4))
    inner = "ListenableBuilder(listenable: v, builder: (c, _) => Text('${++b}'))"
    return _builds("v.value++", "var v = ValueNotifier(0), b = 0;", n, 1 + n,
                   f"ListenableBuilder reruns its builder on each notification: {1 + n}.", inner)


def n_string_len(rng):
    n, i = rng.choice((2, 3, 4)), rng.choice((0, 1, 2))
    code = _tap("v.value += 'a'", VLB % "${n.length}", f"var v = ValueNotifier('{'z' * i}');")
    return item(_ask(n), code, i + n, f"Each tap makes a longer, different string, so it notifies: {i} + {n} = {i + n}.", taps(n) + READ)


# ── A ChangeNotifier subclass ───────────────────────────────────────────

def _cls(body: str, builder: str) -> str:
    return f"var m = C();\nclass C extends ChangeNotifier {{\n  var n = 0;\n  {body}\n}}\n{builder}"


LISTEN = "ListenableBuilder(listenable: m, builder: (c, _) => Text('%s'))"


def _calls(n: int) -> str:
    return f"for (var i = 0; i < {n}; i++) {{ m.up(); await tester.pump(); }}\n"


def c_notify(rng):
    n = rng.choice((2, 3, 4))
    code = _cls("up() { n++; notifyListeners(); }", LISTEN % "${m.n}")
    return item(f"shown after m.up() {n} times?", code, n, f"up changes n and notifies, so each call rebuilds with the new n: {n}.", _calls(n) + READ)


def c_silent(rng):
    n = rng.choice((2, 3, 4))
    code = _cls("up() { n++; }", LISTEN % "${m.n}")
    return item(f"shown after m.up() {n} times?", code, 0, "up never calls notifyListeners, so the ListenableBuilder is never told: it still shows 0.",
                _calls(n) + READ)


def c_notify_first(rng):
    n = rng.choice((2, 3, 4))
    code = _cls("up() { notifyListeners(); n++; }", LISTEN % "${m.n}")
    return item(f"shown after m.up() {n} times?", code, n,
                f"notifyListeners only schedules the rebuild; the frame is built after up has finished, with n already bumped: {n}.",
                _calls(n) + READ)


def c_builds_twice(rng):
    n = rng.choice((2, 3, 4))
    code = _cls("up() { notifyListeners(); notifyListeners(); }", LISTEN % "${++b}").replace("var m = C();", "var m = C(), b = 0;")
    return item(f"shown after m.up() {n} times?", code, 1 + n,
                f"Two notifications in one call still give one rebuild per frame: 1 + {n} = {1 + n}.", _calls(n) + READ)


def c_step(rng):
    n, k = rng.choice((2, 3)), rng.choice((2, 3, 5))
    code = _cls(f"up() {{ n += {k}; notifyListeners(); }}", LISTEN % "${m.n}")
    return item(f"shown after m.up() {n} times?", code, n * k, f"Each call adds {k} and notifies: {n} x {k} = {n * k}.", _calls(n) + READ)


def c_no_listener(rng):
    n = rng.choice((2, 3, 4))
    code = _cls("up() { n++; notifyListeners(); }", "Builder(builder: (c) => Text('${m.n}'))")
    return item(f"shown after m.up() {n} times?", code, 0,
                "m notifies, but nobody is listening: a plain Builder is not rebuilt and still shows 0.", _calls(n) + READ)


def _t(name, fn):
    return template(name, fn)


TEMPLATES: tuple[Maker, ...] = (
    _t("n_incr", n_incr), _t("n_same", n_same), _t("n_toggle", n_toggle), _t("n_list_inplace", n_list_inplace),
    _t("n_list_copy", n_list_copy), _t("n_read_only", n_read_only),
    _t("n_double", n_double), _t("n_derived", n_derived),
    _t("b_incr", b_incr), _t("b_same_value", b_same_value), _t("b_already_equal", b_already_equal),
    _t("b_two_changes", b_two_changes), _t("b_new_list", b_new_list), _t("b_const_list", b_const_list),
    _t("b_string", b_string), _t("b_record", b_record), _t("b_animated", b_animated),
    _t("b_listener_count", b_listener_count), _t("b_listener_same", b_listener_same), _t("b_listenable", b_listenable), _t("n_string_len", n_string_len),
    _t("c_notify", c_notify), _t("c_silent", c_silent), _t("c_notify_first", c_notify_first), _t("c_builds_twice", c_builds_twice),
    _t("c_step", c_step), _t("c_no_listener", c_no_listener),
)
