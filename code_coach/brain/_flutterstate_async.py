"""Flutter state pack, Async Setter: the number a Text shows once async work has called setState.

Everything is deterministic: a Flutter test runs on a fake clock, so a `Future.delayed(30 ms)` finishes exactly when the
test has pumped 30 ms. The rules written out by hand below (a tap starts the handler at time 0):

* a tap alone draws no frame, so the Text still shows the old number;
* work that waits only on MICROTASKS (`await null`, `await Future.value()`, `Future.microtask`, `.then` on a finished
  future) has finished by the time the tap returns, but the screen changes at the next frame: `pump()`;
* work behind a TIMER (`Future(...)`, `Future.delayed(Duration.zero)`) needs time to pass: `pump(Duration.zero)` runs
  the timers that are due now (a chain of zero-delay timers included); `pump()` does not;
* `Future.delayed(30 ms)` needs the clock to reach 30 ms: `pump(Duration(milliseconds: 40))`; `pumpAndSettle()` keeps
  pumping 100 ms steps until nothing is scheduled, so every delay used here has finished;
* when several callbacks write the same number, the one that RUNS last wins: synchronous code first, then microtasks in
  the order they were scheduled, then timers by time and then by the order they were scheduled;
* a handler that reads `n` BEFORE an await and writes `old + 1` AFTER it loses updates when taps overlap (timers),
  but not when each tap's work finishes before the next tap (microtasks);
* FutureBuilder / StreamBuilder show 'waiting' (no data) on the first frame; the data arrives with the next frame.
"""

from __future__ import annotations

import random

from ._flutterstate_common import READ, item, template
from ._model import Maker

TAP = "await tester.tap(find.byType(GestureDetector));\n"
#: When the Text is read: name -> (code that moves the clock and draws, ask words, ms elapsed or None for 'no frame', micro-only frame)
WHEN = {
    "tap": ("", "", None),
    "pump": ("await tester.pump();\n", "pump()", -1),
    "pump0": ("await tester.pump(Duration.zero);\n", "pump(Duration.zero)", 0),
    "settle": ("await tester.pumpAndSettle();\n", "pumpAndSettle()", 100),
}


def _when(name: str, ms: int | None = None):
    if name == "sec":
        return f"await tester.pump(Duration(seconds: {ms}));\n", f"pump({ms} s)", ms * 1000
    if name == "ms":
        return f"await tester.pump(Duration(milliseconds: {ms}));\n", f"pump({ms} ms)", ms
    return WHEN[name]


def _sb(handler: str, params: str = "c, s", decl: str = "var n = 0;") -> str:
    return "() {\n  " + decl + f"\n  return StatefulBuilder(builder: ({params}) => GestureDetector(\n      onTap: {handler}, child: Text('$n')));\n}}()"


# ── A handler that awaits something, read at different moments ──────────

#: await kind -> (code, delay in ms: -1 microtask, 0 zero timer, d a timer of d ms)
AWAITS = {
    "null": ("await null", -1),
    "value": ("await Future.value()", -1),
    "timer": ("await Future(() {})", 0),
    "zero": ("await Future.delayed(Duration.zero)", 0),
    "d1": ("await Future.delayed(Duration(seconds: 1))", 1000),
}


def await_item(rng: random.Random, kind: str, when: str, ms: int | None = None):
    code_await, delay = AWAITS[kind]
    n, inc, init = rng.choice((1, 2, 3)), rng.choice((1, 2, 3)), rng.choice((0, 0, 1, 2))
    wcode, wwords, elapsed = _when(when, ms)
    done = elapsed is not None and elapsed >= delay
    answer = init + n * inc if done else init
    bump = "n++" if inc == 1 else f"n += {inc}"
    handler = f"() async {{ {code_await}; s(() => {bump}); }}"
    code = _sb(handler, decl=f"var n = {init};")
    ask = f"after {n} tap{'s' if n > 1 else ''}" + (f", {wwords}?" if wwords else "?")
    if elapsed is None:
        why = f"A tap alone draws no frame, so the Text has not been rebuilt: still {init}."
    elif done and delay == -1:
        why = f"Only microtasks are involved: they finish right after the tap, and the frame from {wwords} shows it: {answer}."
    elif done:
        why = f"The wait is {'a zero-delay timer' if delay == 0 else str(delay // 1000) + ' s'} and {wwords} lets that much time pass, so the setState ran: {answer}."
    elif delay == 0:
        why = f"A timer is still waiting: pump() draws a frame but does not run timers, so the Text still shows {init}."
    else:
        why = (f"The wait is {delay // 1000} s but {wwords} only moves the clock {max(elapsed, 0)} ms"
               + (" (pumpAndSettle stops after 100 ms because no frame is scheduled while a timer is merely waiting)" if when == "settle" else "")
               + f", so the setState has not run: {init}.")
    return item(ask, code, answer, why, TAP * n + wcode + READ)


# ── Which write wins? ───────────────────────────────────────────────────

#: mechanism -> (code with a value hole, phase: 0 now, 1 microtask, 2 timer)
MECH = {
    "sync": ("s(() => n = %d)", 0),
    "micro": ("Future.microtask(() => s(() => n = %d))", 1),
    "then": ("Future.value().then((_) => s(() => n = %d))", 1),
    "timer": ("Future(() => s(() => n = %d))", 2),
    "zero": ("Future.delayed(Duration.zero, () => s(() => n = %d))", 2),
}


def order_item(rng: random.Random, kinds: tuple[str, ...]):
    values = rng.sample(range(1, 10), len(kinds))
    stmts = [MECH[k][0] % v for k, v in zip(kinds, values)]
    ranked = sorted(range(len(kinds)), key=lambda i: (MECH[kinds[i]][1], i))
    answer = values[ranked[-1]]
    handler = "() { " + "; ".join(stmts) + "; }"
    code = _sb(handler, params="c, s")
    names = {"sync": "directly", "micro": "as a microtask", "then": "in a then on a finished future", "timer": "as a Future timer",
             "zero": "as a zero-delay Future.delayed"}
    order = ", ".join(f"{values[i]} ({names[kinds[i]]})" for i in ranked)
    return item("after the tap settles?", code, answer, f"They run in this order: {order}. The last one to run wins: {answer}.",
                TAP + "await tester.pumpAndSettle();\n" + READ)


# ── Loops of awaits, overlapping taps ───────────────────────────────────

def chain_item(rng: random.Random, kind: str, when: str, ms: int | None = None):
    k = rng.choice((2, 3, 4))
    if kind == "micro":
        step, delay = "await null", -1
    elif kind == "timer":
        step, delay = "await Future(() {})", 0
    else:
        step, delay = "await Future.delayed(Duration(seconds: 1))", 1000
    wcode, wwords, elapsed = _when(when, ms)
    if elapsed is None:
        done = 0
    elif delay == -1:
        done = k
    elif delay == 0:
        done = k if elapsed >= 0 else 0
    else:
        done = min(k, max(0, elapsed) // 1000)
    handler = f"() async {{ for (var i = 0; i < {k}; i++) {{ {step}; s(() => n++); }} }}"
    code = _sb(handler)
    if kind == "micro":
        why = f"Each await waits only for a microtask, so all {k} setStates are done after the tap; the frame shows {done}."
    elif kind == "timer":
        why = ("pump() does not run timers: none of the " + f"{k} steps has happened, so 0." if done == 0
               else f"pump(Duration.zero) runs the due timer, and the next zero-delay timer it schedules is due too, so all {k} steps happen: {k}.")
    else:
        why = f"One step per second: after {max(elapsed, 0) // 1000} s, {done} of {k} have run: {done}."
    return item(f"after tap, {wwords}?", code, done, why, TAP + wcode + READ)


def stale_item(rng: random.Random, kind: str):
    n = rng.choice((2, 3, 4))
    if kind == "stale_timer":
        handler = "() async { var o = n; await Future(() {}); s(() => n = o + 1); }"
        answer, why = 1, f"All {n} taps read n = 0 before any timer fires, so each writes 0 + 1: the updates overlap and the Text shows 1."
    elif kind == "fresh_timer":
        handler = "() async { await Future(() {}); s(() => n++); }"
        answer, why = n, f"Each continuation reads n when it runs, one after another, so every tap counts: {n}."
    else:
        handler = "() async { var o = n; await null; s(() => n = o + 1); }"
        answer, why = n, f"A microtask finishes before the next tap, so each tap sees the previous result: {n}."
    return item(f"after {n} taps, pumpAndSettle()?", _sb(handler), answer, why,
                TAP * n + "await tester.pumpAndSettle();\n" + READ)


# ── FutureBuilder / StreamBuilder ───────────────────────────────────────

def builder_item(rng: random.Random, kind: str, when: str):
    k = rng.choice((3, 4, 5, 6, 7, 8))
    init = rng.choice((1, 2, 9))
    wcode, wwords, elapsed = _when(when)
    show = "${s.data ?? 0}"
    if kind == "future":
        code, delay = f"FutureBuilder(future: Future.value({k}), builder: (c, s) => Text('{show}'))", -1
    elif kind == "timer":
        code, delay = f"FutureBuilder(future: Future(() => {k}), builder: (c, s) => Text('{show}'))", 0
    elif kind == "initial":
        code, delay = f"FutureBuilder(initialData: {init}, future: Future.value({k}), builder: (c, s) => Text('{show}'))", -1
    elif kind == "stream":
        code, delay = f"StreamBuilder(stream: Stream.value({k}), builder: (c, s) => Text('{show}'))", -1
    else:
        code, delay = f"FutureBuilder(future: Future.delayed(Duration.zero, () => {k}), builder: (c, s) => Text('{show}'))", 0
    first = init if kind == "initial" else 0
    done = elapsed is not None and elapsed >= delay and when != "tap"
    answer = k if done else first
    ask = "shown on the first frame?" if when == "tap" else f"shown after {wwords}?"
    if not done:
        why = ("The first frame is built before the data arrives: " + (f"initialData {init}." if kind == "initial" else "no data yet, so 0.")
               if when == "tap" else f"The timer has not run yet ({wwords} does not run timers), so the builder still has no data: {first}.")
    else:
        why = f"The data has arrived and the builder was rebuilt by the frame from {wwords}: {k}."
    return item(ask, code, answer, why, wcode + READ)


def _t(name, fn, *args):
    return template(name, fn, *args)


TEMPLATES: tuple[Maker, ...] = (
    _t("await_null_tap", await_item, "null", "tap"), _t("await_null_pump", await_item, "null", "pump"),
    _t("await_value_pump", await_item, "value", "pump"), _t("await_value_settle", await_item, "value", "settle"),
    _t("await_timer_tap", await_item, "timer", "tap"), _t("await_timer_pump", await_item, "timer", "pump"),
    _t("await_timer_pump0", await_item, "timer", "pump0"), _t("await_timer_settle", await_item, "timer", "settle"),
    _t("await_zero_pump", await_item, "zero", "pump"), _t("await_zero_pump0", await_item, "zero", "pump0"),
    _t("await_d1_2s", await_item, "d1", "sec", 2),
    _t("order_timer_micro", order_item, ("timer", "micro")), _t("order_micro_timer", order_item, ("micro", "timer")),
    _t("order_sync_micro", order_item, ("sync", "micro")), _t("order_timer_sync", order_item, ("timer", "sync")),
    _t("order_sync_timer", order_item, ("sync", "timer")),
    _t("chain_micro", chain_item, "micro", "pump"), _t("chain_timer_pump", chain_item, "timer", "pump"),
    _t("stale_timer", stale_item, "stale_timer"), _t("fresh_timer", stale_item, "fresh_timer"),
    _t("stale_micro", stale_item, "stale_micro"),
    _t("fb_first", builder_item, "future", "tap"), _t("fb_pump", builder_item, "future", "pump"),
    _t("fb_timer_pump", builder_item, "timer", "pump"), _t("fb_timer_pump0", builder_item, "timer", "pump0"),
    _t("fb_initial_first", builder_item, "initial", "tap"), _t("fb_initial_pump", builder_item, "initial", "pump"),
    _t("sb_first", builder_item, "stream", "tap"), _t("sb_pump", builder_item, "stream", "pump"),
)
