"""Dart core pack, part 5: Async Order - in what order do the prints happen?

The answer is the printed letters in order, typed together (`ADCB`). The oracle for this activity is `lines`: the
printed lines of the real program are glued together with nothing between them.

The model is Dart's event loop in three rules: first the synchronous code runs to its end (an `async` function runs
synchronously up to its first `await`); then every MICROTASK runs (`Future.microtask`, a `then` on a finished future,
the code after an `await` on something already done), in the order it was queued, including microtasks queued by
microtasks; then ONE EVENT runs (`Future(...)`, `Future.delayed(Duration.zero, ...)`), and the microtasks it queued
run before the next event. The generated templates below use the first two parts of the rule directly; the written
ones spell out their own order. Only `Duration.zero` delays are used, so nothing depends on a clock.
"""

from __future__ import annotations

import itertools
import random
from string import Template

from ._dart_model import P
from ._model import Maker
from .items import Item


def AO(fmt: str, order: list[int], why: str) -> Maker:
    """An Async Order template. `order` lists which letters print and in what order, as numbers 1-5 for $s1..$s5."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        prompt = Template(fmt).substitute(p)
        answer = "".join(p[f"s{i}"] for i in order)
        return Item(prompt, answer, Template(why).safe_substitute(p))
    make.__name__ = "ao_" + fmt[:24].replace("\n", " ")
    return make


def AOD(fmt: str, order: list[int | str], why: str) -> Maker:
    """Like AO, but `order` may also hold literal strings (digits printed by a loop) that go into the answer as they are."""
    def make(rng: random.Random) -> Item:
        p = P(rng)
        prompt = Template(fmt).substitute(p)
        answer = "".join(x if isinstance(x, str) else p[f"s{x}"] for x in order)
        return Item(prompt, answer, Template(why).safe_substitute(p))
    make.__name__ = "aod_" + fmt[:24].replace("\n", " ")
    return make


SYNC = "Synchronous code always finishes before any queued work starts."
MICRO = "Microtasks run after the synchronous code and before any event."
EVENT = "An event (Future, Future.delayed) runs after the microtasks."

# ── Generated: every order of three of four kinds of statement ──────────

#: kind -> (what it looks like with the letter in `{}`, which queue it lands in)
KINDS = {
    "sync": ("print('{}');", 0),
    "micro": ("Future.microtask(() => print('{}'));", 1),
    "event": ("Future(() => print('{}'));", 2),
    "zero": ("Future.delayed(Duration.zero, () => print('{}'));", 2),
}
KIND_WHY = {
    "sync": "A plain print happens at once.",
    "micro": "Future.microtask waits for the microtask turn.",
    "event": "Future(...) waits for an event turn.",
    "zero": "Future.delayed(Duration.zero, ...) is an event, queued behind earlier events.",
}


def _triple(kinds: tuple[str, str, str]) -> Maker:
    def make(rng: random.Random) -> Item:
        p = P(rng)
        letters = [p["s1"], p["s2"], p["s3"]]
        lines = "\n".join("  " + KINDS[k][0].format(ch) for k, ch in zip(kinds, letters))
        prompt = "void main() {\n" + lines + "\n}"
        queue = {0: [], 1: [], 2: []}
        for k, ch in zip(kinds, letters):
            queue[KINDS[k][1]].append(ch)
        answer = "".join(queue[0] + queue[1] + queue[2])
        why = "Sync first, then microtasks, then events. " + " ".join(KIND_WHY[k] for k in dict.fromkeys(kinds))
        return Item(prompt, answer, why)
    make.__name__ = "triple_" + "_".join(kinds)
    return make


GENERATED: list[Maker] = [_triple(k) for k in itertools.permutations(KINDS, 3)]

# ── Written one by one ──────────────────────────────────────────────────

WRITTEN: list[Maker] = [
    AO("Future<void> main() async {\n  print('$s1');\n  Future(() => print('$s2'));\n  print('$s3');\n}", [1, 3, 2], SYNC),
    AO("Future<void> main() async {\n  Future(() => print('$s1'));\n  Future.microtask(() => print('$s2'));\n  print('$s3');\n}", [3, 2, 1], "Sync, then the microtask, then the event."),
    AO("void main() {\n  Future(() => print('$s1'));\n  Future(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "Events run in the order they were queued, after the sync code."),
    AO("void main() {\n  Future.microtask(() => print('$s1'));\n  Future.microtask(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "Microtasks keep their queue order, after the sync code."),
    AO("void main() {\n  Future(() => print('$s1')).then((_) => print('$s2'));\n  Future(() => print('$s3'));\n  print('$s4');\n}", [4, 1, 2, 3],
       "The then runs right after its own Future, as a microtask, before the next event."),
    AO("void main() {\n  Future.value(1).then((_) => print('$s1'));\n  print('$s2');\n}", [2, 1], "A then always runs later, even on a Future that is already done."),
    AO("Future<void> f() async {\n  print('$s1');\n  await null;\n  print('$s2');\n}\nvoid main() {\n  f();\n  print('$s3');\n}", [1, 3, 2],
       "An async function runs until its first await, then main carries on."),
    AO("Future<void> f() async {\n  print('$s1');\n  await Future.delayed(Duration.zero);\n  print('$s2');\n}\nvoid main() {\n  f();\n  Future.microtask(() => print('$s3'));\n  print('$s4');\n}", [1, 4, 3, 2],
       "f stops at the await; the sync print, the microtask, then f's event."),
    AO("Future<void> a() async { print('$s1'); await null; print('$s2'); }\nFuture<void> b() async { print('$s3'); await null; print('$s4'); }\nvoid main() { a(); b(); print('$s5'); }", [1, 3, 5, 2, 4],
       "Both functions run to their await first, then main finishes, then the awaited parts continue in order."),
    AO("Future<void> main() async {\n  try {\n    await Future.error('x');\n    print('$s1');\n  } catch (e) {\n    print('$s2');\n  } finally { print('$s3'); }\n  print('$s4');\n}", [2, 3, 4],
       "The error skips the line after the await, lands in catch, then finally runs."),
    AO("void main() {\n  Future.error('x').catchError((e) => print('$s1'));\n  Future.value(1).then((_) => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "The two callbacks are microtasks queued in order, after the sync print."),
    AO("void main() {\n  Future(() => print('$s1')).whenComplete(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "whenComplete runs after its Future, once the sync code is done."),
    AO("Future<void> main() async {\n  await Future.wait([\n    Future(() => print('$s1')),\n    Future(() => print('$s2')),\n  ]);\n  print('$s3');\n}", [1, 2, 3], "Future.wait finishes when both are done; main continues after."),
    AOD("Future<void> main() async {\n  for (var i = 1; i <= 3; i++) {\n    await null;\n    print(i);\n  }\n  print('$s1');\n}", ["1", "2", "3", 1], "Each await pauses for a microtask turn, but nothing else is running."),
    AO("Future<void> f() async {\n  await Future.delayed(Duration.zero);\n  print('$s1');\n}\nFuture<void> main() async {\n  f();\n  print('$s2');\n}", [2, 1], "main does not wait for f, so main's print comes first."),
    AO("Future<void> f() async {\n  await Future.delayed(Duration.zero);\n  print('$s1');\n}\nFuture<void> main() async {\n  await f();\n  print('$s2');\n}", [1, 2], "await f() makes main wait until f is finished."),
    AO("void main() {\n  Future(() => 1).then((_) => print('$s1')).then((_) => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "Each then runs after the one before it, all after the sync code."),
    AO("void main() {\n  Future.microtask(() {\n    print('$s1');\n    Future.microtask(() => print('$s2'));\n  });\n  Future.microtask(() => print('$s3'));\n}", [1, 3, 2], "A microtask queued by a microtask goes to the back of the queue."),
    AO("void main() {\n  Future(() {\n    print('$s1');\n    Future.microtask(() => print('$s2'));\n  });\n  Future(() => print('$s3'));\n}", [1, 2, 3], "Microtasks run between two events, so $s2 comes before the next event."),
    AO("void main() {\n  Future(() {\n    print('$s1');\n    Future(() => print('$s2'));\n  });\n  Future(() => print('$s3'));\n}", [1, 3, 2], "An event queued by an event goes behind the events already waiting."),
    AO("Future<int> f() async => 1;\nvoid main() {\n  f().then((v) => print('$s1'));\n  print('$s2');\n}", [2, 1], "An async function gives a Future, and its then runs later."),
    AO("void main() {\n  Future.sync(() => print('$s1'));\n  print('$s2');\n}", [1, 2], "Future.sync runs its function at once."),
    AO("void main() {\n  Future(() => print('$s1'));\n  Future.delayed(Duration.zero, () => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "Both are events, queued in order, after the sync code."),
    AO("void main() {\n  Future.delayed(Duration.zero, () => print('$s1'));\n  Future(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "Both are events, queued in order, so the delayed one is first."),
    AOD("Future<void> main() async {\n  await for (final x in Stream.fromIterable([1, 2, 3])) {\n    print(x);\n  }\n  print('$s1');\n}", ["1", "2", "3", 1], "await for takes the stream's items one by one, then the loop ends."),
    AO("import 'dart:async';\nvoid main() {\n  scheduleMicrotask(() => print('$s1'));\n  Future(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "scheduleMicrotask is a microtask, so it beats the Future's event."),
    AO("import 'dart:async';\nFuture<void> main() async {\n  var c = Completer<void>();\n  c.future.then((_) => print('$s1'));\n  print('$s2');\n  c.complete();\n  print('$s3');\n}", [2, 3, 1],
       "complete() does not run the then at once: it runs after the sync code."),
    AO("import 'dart:async';\nFuture<void> main() async {\n  var c = Completer<int>();\n  Future(() => c.complete(1));\n  print('$s1');\n  await c.future;\n  print('$s2');\n}", [1, 2], "main waits at the await until the event completes it."),
    AO("Future<void> main() async {\n  print('$s1');\n  await Future.microtask(() => print('$s2'));\n  print('$s3');\n}", [1, 2, 3], "Every step is awaited, so the order is the order written."),
    AO("Future<void> main() async {\n  Future.microtask(() => print('$s1'));\n  await null;\n  print('$s2');\n}", [1, 2], "The microtask was queued first, and the await resumes after it."),
    AO("Future<void> main() async {\n  Future(() => print('$s1'));\n  await null;\n  print('$s2');\n}", [2, 1], "The await resumes in a microtask, before the event."),
    AO("Future<void> main() async {\n  Future(() => print('$s1'));\n  await Future.delayed(Duration.zero);\n  print('$s2');\n}", [1, 2], "The delayed Future is queued behind the first event, so the event runs first."),
    AO("void main() {\n  print('$s1');\n  Future.microtask(() => print('$s2'));\n  Future(() => print('$s3'));\n  print('$s4');\n}", [1, 4, 2, 3], "Both prints first, then the microtask, then the event."),
    AO("void main() {\n  Future(() => print('$s1'));\n  Future.microtask(() => print('$s2'));\n  Future(() => print('$s3'));\n  Future.microtask(() => print('$s4'));\n}", [2, 4, 1, 3], "Both microtasks run before either event."),
    AO("Future<void> f(String s) async {\n  print(s);\n  await null;\n  print(s);\n}\nvoid main() {\n  f('$s1');\n  f('$s2');\n}", [1, 2, 1, 2], "Each call runs to its await; then each continues in order."),
    AO("void main() {\n  Future.value('$s1').then(print);\n  Future(() => print('$s2'));\n  print('$s3');\n}", [3, 1, 2], "then(print) runs as a microtask, before the event."),
    AO("Future<String> get() async => '$s1';\nFuture<void> main() async {\n  print('$s2');\n  print(await get());\n  print('$s3');\n}", [2, 1, 3], "await get() waits for the value, then prints it."),
    AO("void main() {\n  Future<void>(() => throw 'x').catchError((e) => print('$s1'));\n  print('$s2');\n}", [2, 1], "The error handler runs after the event, once the sync code is done."),
    AO("void main() {\n  print('$s1');\n  Future(() => print('$s2')).then((_) => print('$s3'));\n  Future.microtask(() => print('$s4'));\n}", [1, 4, 2, 3], "Sync, then the microtask, then the event and its then."),
]

ORDERS: list[Maker] = GENERATED + WRITTEN
