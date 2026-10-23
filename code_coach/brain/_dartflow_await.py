"""Dart flow pack, part 4: Await Order - in what order do the prints happen? (the deeper cases)

The answer is the printed letters (and the odd digit) glued together; the oracle is `lines`. Every template is a
complete program (`main(`). Dart Core's Async Order has the basics (sync, microtask, event). The model here adds
these rules, all checked against the real event loop:

* an `async` function runs SYNCHRONOUSLY up to its first `await`; one with no `await` runs entirely at the call;
* an `await` always gives other queued work a turn: the code after it runs in a MICROTASK queued at that moment
  (even for `await null` or an already finished Future), or when the awaited event or Future completes;
* callbacks attached to ONE Future (several `then`s, the awaiter) run one after the other in the same microtask,
  and a `then` whose callback returns a plain value hands it to the next `then` in that same microtask - so a
  chain `a.then(x).then(y)` runs x and y back to back (not like JavaScript, where each hop is its own turn);
* a callback that returns a Future (an `async` closure that awaits) makes the next `then` wait for that Future;
* `Future.value(f())` calls `f` NOW; `Future(() => f())` calls it in an event; `Future.microtask(() => f())` in a
  microtask; `Future.sync(f)` now; `Future.delayed(Duration.zero, f)` and `Future(f)` are events in queue order;
* when several microtasks are waiting they run in the order queued, and microtasks queued by microtasks go to the back;
* an error in an `async` function is delivered to its returned Future, never thrown at the call.
"""

from __future__ import annotations

from ._dartflow_model import L
from ._model import Maker

IMP = "import 'dart:async';\n"
W2 = "Future<void> w(String s) async {\n  print(s);\n  await null;\n  print(s);\n}\n"
AWAIT_TURN = "Every await lets the queued microtasks run before the code after it continues."


def pre_ab(p, rng):
    p["a"], p["b"] = rng.sample(range(2, 9), 2)


def pre_n(p, rng):
    p["k"] = rng.randint(2, 4)


AWAIT: list[Maker] = [
    # ── what runs at the call, what waits ──
    L("Future<void> f() async {\n  print('$s1');\n}\nvoid main() {\n  f();\n  print('$s2');\n}",
      [1, 2], "An async function with no await runs completely at the call; only the Future it returns is 'later'."),
    L("Future<void> f() async => print('$s1');\nFuture<void> main() async {\n  print('$s2');\n  Future.microtask(() => print('$s3'));\n  await f();\n  print('$s4');\n}",
      [2, 1, 3, 4], "f prints at the call. The await then takes a turn, so the microtask goes before the code after it."),
    L("Future<void> f() async {\n  print('$s1');\n  await null;\n  print('$s2');\n}\nFuture<void> main() async {\n  Future.microtask(() => print('$s3'));\n  await f();\n  print('$s4');\n}",
      [1, 3, 2, 4], "f runs to its await at the call. The earlier microtask goes first, then f resumes, then main."),
    L(W2 + "Future<void> main() async {\n  w('$s1');\n  w('$s2');\n  print('$s3');\n}",
      [1, 2, 3, 1, 2], "Both calls run to their await, then main finishes, then each resumes in turn."),
    L(W2 + "Future<void> main() async {\n  w('$s1');\n  w('$s2');\n  w('$s3');\n}",
      [1, 2, 3, 1, 2, 3], "All three run to their await first; then they resume in the order they paused."),
    L("Future<void> a() async {\n  print('$s1');\n  await null;\n  print('$s2');\n  await null;\n  print('$s3');\n}\nFuture<void> b() async {\n  print('$s4');\n  await null;\n  print('$s5');\n}\nvoid main() {\n  a();\n  b();\n}",
      [1, 4, 2, 5, 3], "The two take turns, one step per await: a, b, a, b, and a is left with its last step."),
    L("Future<void> main() async {\n  [1, 2].forEach((x) async {\n    await null;\n    print(x);\n  });\n  print('$s1');\n}",
      lambda p: [1, "1", "2"], "forEach does not wait for async closures: main's print comes first, then each closure resumes."),
    L("Future<void> main() async {\n  for (var x in [1, 2]) {\n    await null;\n    print(x);\n  }\n  print('$s1');\n}",
      lambda p: ["1", "2", 1], "A for loop does wait at its own await, so the loop finishes before the print."),
    L("Future<void> main() async {\n  for (var i = 0; i < $k; i++) {\n    Future.microtask(() => print(i));\n  }\n  await null;\n  print('$s1');\n}",
      lambda p: [str(i) for i in range(p["k"])] + [1], "Each turn of the loop has its own i; the microtasks print 0, 1, ... before main resumes.", pre_n),
    # ── Future.value(f()) versus Future(() => f()) ──
    L("String f(String s) {\n  print(s);\n  return s;\n}\nvoid main() {\n  Future(() => f('$s1'));\n  Future.value(f('$s2'));\n  Future.microtask(() => f('$s3'));\n  print('$s4');\n}",
      [2, 4, 3, 1], "Future.value(f(...)) calls f right now; the microtask comes next; the event comes last."),
    L("String f(String s) {\n  print(s);\n  return s;\n}\nvoid main() {\n  Future.sync(() => f('$s1'));\n  Future.microtask(() => f('$s2'));\n  print('$s3');\n}",
      [1, 3, 2], "Future.sync runs its function at once."),
    L("Future<void> main() async {\n  Future.sync(() => print('$s1')).then((_) => print('$s2'));\n  print('$s3');\n}",
      [1, 3, 2], "Future.sync runs now, but its then still waits for a microtask."),
    # ── then chains ──
    L("void main() {\n  var f = Future.value(1);\n  f.then((_) => print('$s1'));\n  f.then((_) => print('$s2'));\n  print('$s3');\n}",
      [3, 1, 2], "Two thens on one Future run in the order they were attached, after the sync print."),
    L("void main() {\n  Future.value(1).then((_) => print('$s1')).then((_) => print('$s2'));\n  Future.microtask(() => print('$s3'));\n}",
      [1, 2, 3], "The two thens run back to back in the first microtask, before the microtask queued after it."),
    L("void main() {\n  Future.microtask(() => print('$s1'));\n  Future.value(1).then((_) => print('$s2')).then((_) => print('$s3'));\n}",
      [1, 2, 3], "The microtask was queued first; then both thens run together."),
    L("void main() {\n  Future.value(1).then((_) => print('$s1'));\n  Future.value(2).then((_) => print('$s2')).then((_) => print('$s3'));\n  Future.value(3).then((_) => print('$s4'));\n}",
      [1, 2, 3, 4], "Each Future.value is its own microtask, in order; a chain runs all its steps in its turn."),
    L(IMP + "void main() {\n  Future.value(1).then((_) {\n    print('$s1');\n    scheduleMicrotask(() => print('$s2'));\n  }).then((_) => print('$s3'));\n}",
      [1, 3, 2], "The next then runs right away in the same turn; the new microtask waits for its turn."),
    L("void main() {\n  Future.value(1).whenComplete(() => print('$s1')).then((_) => print('$s2'));\n  Future.microtask(() => print('$s3'));\n}",
      [1, 2, 3], "whenComplete and the then after it run together in the first microtask."),
    L("void main() {\n  Future.error('x').catchError((e) => print('$s1')).then((_) => print('$s2'));\n  Future.microtask(() => print('$s3'));\n}",
      [1, 2, 3], "catchError hands on to the next then in the same turn."),
    L("void main() {\n  Future.value(1).then((_) => Future.value(2)).then((_) => print('$s1'));\n  Future.microtask(() => print('$s2'));\n}",
      [2, 1], "The first then returns a Future, so the next then must wait for it: the microtask gets in first."),
    L("void main() {\n  Future.value(1).then((_) => 2).then((_) => print('$s1'));\n  Future.microtask(() => print('$s2'));\n}",
      [1, 2], "The first then returns a plain value, so the next then runs at once in the same turn."),
    L("void main() {\n  Future.value(1).then((_) async {\n    print('$s1');\n    await null;\n    print('$s2');\n  }).then((_) => print('$s3'));\n  Future.microtask(() => print('$s4'));\n}",
      [1, 4, 2, 3], "The async closure pauses at its await, so the next then waits until the closure is done."),
    L("void main() {\n  Future.value(1).then((_) async {\n    print('$s1');\n  }).then((_) => print('$s2'));\n  Future.microtask(() => print('$s3'));\n}",
      [1, 2, 3], "The async closure has no await, so its Future is already done and the next then follows at once."),
    L("Future<int> f() async => 1;\nvoid main() {\n  f().then((_) => print('$s1'));\n  Future.microtask(() => print('$s2'));\n  print('$s3');\n}",
      [3, 1, 2], "f is already finished at the call; its then is queued first, as a microtask."),
    L("Future<void> main() async {\n  Future.wait([Future.value(1), Future.value(2)]).then((_) => print('$s1'));\n  Future.microtask(() => print('$s2'));\n  print('$s3');\n}",
      [3, 1, 2], "Future.wait is done as soon as the second Future.value is, which is before the later microtask."),
    L("void main() {\n  Future.sync(() => 1).then((_) => print('$s1'));\n  Future.value(2).then((_) => print('$s2'));\n  print('$s3');\n}",
      [3, 1, 2], "Both thens wait for a microtask, in the order they were queued, behind the sync print."),
    # ── completers and events ──
    L(IMP + "Future<void> main() async {\n  var c = Completer<void>();\n  Future.microtask(() => print('$s1'));\n  c.future.then((_) => print('$s2'));\n  c.complete();\n  print('$s3');\n}",
      [3, 1, 2], "complete() queues the then after the microtask that was already waiting."),
    L("void main() {\n  Future.delayed(Duration.zero, () => print('$s1'));\n  Future.delayed(Duration.zero).then((_) => print('$s2'));\n  Future(() => print('$s3'));\n  print('$s4');\n}",
      [4, 1, 2, 3], "Three events in the order queued; the then rides along with the delayed Future it belongs to."),
    L("Future<void> main() async {\n  Future(() => print('$s1'));\n  await Future.delayed(Duration.zero);\n  print('$s2');\n  Future(() => print('$s3'));\n  await null;\n  print('$s4');\n}",
      [1, 2, 4, 3], "The first event goes before the delayed one; after it, the await's microtask beats the new event."),
    L("Future<void> main() async {\n  Future(() => print('$s1'));\n  await null;\n  print('$s2');\n  await Future(() {});\n  print('$s3');\n}",
      [2, 1, 3], "The await null resumes before the event; the second await waits behind the first event."),
    L("Future<void> main() async {\n  var f = Future.delayed(Duration.zero, () => $a);\n  Future.microtask(() => print('$s1'));\n  print(await f);\n  print('$s2');\n}",
      lambda p: [1, str(p["a"]), 2], "The microtask runs now; main waits for the event, prints its value, then goes on.", pre_ab),
    # ── interleaving of awaits ──
    L("Future<void> main() async {\n  Future.microtask(() => print('$s1'));\n  await null;\n  print('$s2');\n  Future.microtask(() => print('$s3'));\n  await null;\n  print('$s4');\n}",
      [1, 2, 3, 4], AWAIT_TURN + " Each microtask was queued before the await that follows it."),
    L("Future<void> main() async {\n  await null;\n  Future.microtask(() => print('$s1'));\n  print('$s2');\n  await null;\n  print('$s3');\n}",
      [2, 1, 3], "The microtask is queued before the second await, so it runs first, then main resumes."),
    L("Future<void> main() async {\n  var f = Future.value(1);\n  await f;\n  print('$s1');\n  Future.microtask(() => print('$s2'));\n  await f;\n  print('$s3');\n}",
      [1, 2, 3], "Awaiting a finished Future still takes one turn, so the microtask queued before it goes first."),
    L("Future<void> main() async {\n  Future.value(1).then((_) => print('$s1'));\n  await Future.value(2);\n  print('$s2');\n}",
      [1, 2], "Both Futures finish in order; the then was attached first, so it runs first."),
    L("Future<void> main() async {\n  Future.microtask(() => print('$s1'));\n  await for (var x in Stream.fromIterable([1, 2])) {\n    print(x);\n  }\n  print('$s2');\n}",
      lambda p: [1, "1", "2", 2], "The microtask is queued before the stream starts delivering; the loop ends before the last print."),
    L("Future<void> f() async {\n  await null;\n  print('$s1');\n}\nFuture<void> main() async {\n  f();\n  f();\n  print('$s2');\n  await f();\n  print('$s3');\n}",
      [2, 1, 1, 1, 3], "Three calls pause; main prints, then each resumes in order; main's await ends with the third call."),
    # ── nesting and errors ──
    L("Future<void> inner() async {\n  print('$s1');\n  await null;\n  print('$s2');\n}\nFuture<void> outer() async {\n  print('$s3');\n  await inner();\n  print('$s4');\n}\nvoid main() {\n  outer();\n  print('$s5');\n}",
      [3, 1, 5, 2, 4], "outer calls inner, which pauses; main prints; inner resumes and ends; then outer resumes."),
    L("Future<void> f() async {\n  try {\n    print('$s1');\n    await null;\n    print('$s2');\n  } finally {\n    print('$s3');\n  }\n}\nvoid main() {\n  f();\n  print('$s4');\n}",
      [1, 4, 2, 3], "The finally belongs to the code after the await, so it waits too."),
    L("Future<void> f() async => throw 'x';\nFuture<void> main() async {\n  try {\n    f().catchError((e) => print('$s1'));\n    print('$s2');\n  } catch (e) {\n    print('$s3');\n  }\n  print('$s4');\n}",
      [2, 4, 1], "The async error does not throw at the call: the catch is never used; catchError runs later."),
    L("Future<void> f() async => throw 'x';\nFuture<void> main() async {\n  try {\n    await f();\n    print('$s1');\n  } catch (e) {\n    print('$s2');\n  }\n  print('$s3');\n}",
      [2, 3], "await turns the Future's error into a throw, so the catch runs and the print after the await is skipped."),
    L("Future<void> f() async {\n  print('$s1');\n  throw 'x';\n}\nFuture<void> main() async {\n  f().catchError((e) => print('$s2'));\n  print('$s3');\n}",
      [1, 3, 2], "f runs at the call up to its throw; the error is handed to the Future, and catchError runs later."),
    L("Future<int> a() async {\n  print('$s1');\n  return $a;\n}\nFuture<int> b() async {\n  print('$s2');\n  return $b;\n}\nFuture<void> main() async {\n  var x = a();\n  var y = b();\n  print('$s3');\n  print(await x + await y);\n}",
      lambda p: [1, 2, 3, str(p["a"] + p["b"])], "Both calls start before anything is awaited; the sum is printed last.", pre_ab),
    L(W2 + "Future<void> main() async {\n  await w('$s1');\n  await w('$s2');\n  print('$s3');\n}",
      [1, 1, 2, 2, 3], "Awaited one after the other, the second call does not even start until the first is done."),
    L(W2 + "Future<void> main() async {\n  await Future.wait([w('$s1'), w('$s2')]);\n  print('$s3');\n}",
      [1, 2, 1, 2, 3], "Future.wait starts both at once, so they take turns."),
]
