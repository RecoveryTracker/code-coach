"""Dart flow pack, part 5: Future Result - what value (or error) comes out of the chain?

Every template is a complete program, `Future<void> main() async { ... }`, that prints exactly ONE line (oracle
`value`). The model is plain value-passing: `then` passes the callback's result on, a thrown error skips the
`then`s until a `catchError` (or a `try`/`catch` around the `await`), `whenComplete` passes the original value or
error through unless it throws itself, `Future.wait` gives its results in LIST order whatever order they finish in,
an `await` turns a Future's error into a throw, and a Future never holds another Future (it is flattened).
"""

from __future__ import annotations

from ._dartflow_model import F
from ._model import Maker


def FR(body: str, solve, why: str, pre=None, decls: str = "") -> Maker:
    """A complete program: `decls` (top-level code) and `Future<void> main() async { body }` (body lines indented)."""
    lines = "\n".join("  " + ln for ln in body.split("\n"))
    return F(decls + "Future<void> main() async {\n" + lines + "\n}", solve, why, pre)


def pre_k(p, rng):
    p["k"] = rng.randint(2, 4)


FUTURE: list[Maker] = [
    # ── then chains ──
    FR("print(await Future.value($a).then((x) => x * $b));", lambda p: p["a"] * p["b"], "then passes the callback's result on: a times b."),
    FR("print(await Future.value($a).then((x) => x + $b).then((x) => x * 2));", lambda p: (p["a"] + p["b"]) * 2,
       "Each then gets the result of the one before: (a + b), then doubled."),
    FR("var f = Future.value($a);\nf.then((x) => x * $b);\nprint(await f);", lambda p: p["a"],
       "then makes a NEW Future; f itself still holds the first value."),
    FR("var f = Future.value($a);\nvar g = f.then((x) => x * $b);\nprint(await g);", lambda p: p["a"] * p["b"],
       "g is the Future made by then, so it holds the result of the callback."),
    FR("print(await Future.value($a).then((x) => Future.value(x + $b)));", lambda p: p["a"] + p["b"],
       "A then that returns a Future is flattened: the result is the number, not a Future."),
    FR("var r = await Future.value($a).then((x) {\n  var y = x * 2;\n});\nprint(r);", lambda p: None,
       "A block callback that returns nothing gives null."),
    FR("print(await Future.value($a).then((x) => x.isEven));", lambda p: p["a"] % 2 == 0, "then can change the type: here an int becomes a bool."),
    FR("print(await Future.value('$w').then((s) => s.length));", lambda p: p["L"], "The String becomes its length."),
    FR("print(await Future.value($a).then((x) => x * x).then((x) => x.toString()).then((s) => s.length));",
       lambda p: len(str(p["a"] * p["a"])), "Square, then text, then the length of the text."),
    FR("print(await Future.value(Future.value($a)));", lambda p: p["a"], "A Future never holds another Future; it is flattened."),
    FR("print(await Future.value($a) > $b ? '$w' : '$v');", lambda p: p["w"] if p["a"] > p["b"] else p["v"],
       "await gives the number, and the comparison picks a word."),
    FR("var f = Future.value($a);\nprint(await f + await f);", lambda p: 2 * p["a"], "Awaiting the same Future twice gives the same value twice."),
    # ── errors ──
    FR("print(await Future<int>.error('x').catchError((e) => $a));", lambda p: p["a"], "catchError's callback replaces the error with a value."),
    FR("print(await Future.value($a).catchError((e) => $b));", lambda p: p["a"], "No error, so catchError is skipped and the value goes through."),
    FR("print(await Future.value($a).then<int>((x) => throw 'boom').catchError((e) => $b));", lambda p: p["b"],
       "The throw in the then becomes an error; catchError turns it into b."),
    FR("print(await Future.value(1).then<String>((x) => throw '$w').catchError((e) => 'got $$e'));", lambda p: "got " + p["w"],
       "catchError receives the thrown value."),
    FR("print(await Future<int>.error('x').then((v) => v + 1, onError: (e) => $a));", lambda p: p["a"],
       "then(onError:) handles the error of this Future, so the result is a."),
    FR("print(await Future<int>.error('x').then((v) => v + 1).catchError((e) => $a));", lambda p: p["a"],
       "The then is skipped because of the error; catchError answers."),
    FR("print(await Future.value($a).whenComplete(() => $b));", lambda p: p["a"], "whenComplete ignores what its callback returns: the original value goes on."),
    FR("try {\n  await Future.value(1).whenComplete(() => throw '$w');\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "An error thrown in whenComplete replaces the result."),
    FR("try {\n  await Future<int>.error('$w').whenComplete(() {});\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "whenComplete does not handle the error; it goes on to the await."),
    FR("try {\n  await Future<int>.error('x').catchError((e) => 1, test: (e) => e is FormatException);\n} catch (e) {\n  print(e);\n}", lambda p: "x",
       "The test says no, so catchError does not handle it and the await throws the original error."),
    FR("print(await Future<int>.error(FormatException('x')).catchError((e) => $a, test: (e) => e is FormatException));", lambda p: p["a"],
       "The test says yes for a FormatException, so the handler's value is the result."),
    FR("try {\n  await Future.delayed(Duration.zero, () => throw '$w');\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "An error inside the delayed callback becomes an error of the Future, and await throws it."),
    FR("try {\n  await Future.error(StateError('$w'));\n} on StateError catch (e) {\n  print(e.message);\n}", lambda p: p["w"],
       "await throws the StateError, and the on clause takes it; message is the text."),
    FR("try {\n  await Future.sync(() => throw '$w');\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "Future.sync catches the throw and turns it into an error of the Future."),
    # ── Future.wait, any, forEach, records ──
    FR("print(await Future.wait([Future.value($a), Future.value($b), Future.value($c)]));", lambda p: [p["a"], p["b"], p["c"]],
       "Future.wait gives a list in the order of the list you gave."),
    FR("print(await Future.wait([Future.delayed(Duration.zero, () => $a), Future.value($b)]));", lambda p: [p["a"], p["b"]],
       "The results are in list order, even though the second one finishes first."),
    FR("var r = await Future.wait([Future.value($a), Future.value($b), Future.value($c)]);\nprint(r.reduce((x, y) => x + y));",
       lambda p: p["a"] + p["b"] + p["c"], "Future.wait gives a List<int>, which can be summed."),
    FR("print(await Future.wait([for (var i = 1; i <= $k; i++) Future.value(i * i)]));", lambda p: [i * i for i in range(1, p["k"] + 1)],
       "A collection-for builds the Futures; the squares come out in order.", pre_k),
    FR("try {\n  await Future.wait([Future.value(1), Future.error('$w')]);\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "If any Future fails, Future.wait fails with that error."),
    FR("try {\n  await Future.wait([Future<int>.error('$w'), Future<int>.error('$v')]);\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "Both fail; the first one to fail (here the first in the list) is the error you get."),
    FR("print(await Future.any([Future.delayed(Duration.zero, () => '$w'), Future.value('$v')]));", lambda p: p["v"],
       "Future.any takes the first to finish: a Future.value finishes before a delayed event."),
    FR("print(await Future.any([Future.value('$w'), Future.delayed(Duration.zero, () => '$v')]));", lambda p: p["w"],
       "The same race with the list the other way round: the value still wins."),
    FR("var s = 0;\nawait Future.forEach([$a, $b, $c], (x) async {\n  s += x;\n});\nprint(s);", lambda p: p["a"] + p["b"] + p["c"],
       "forEach waits for each async call, so s is complete afterwards."),
    FR("var (x, y) = await (Future.value($a), Future.value($b)).wait;\nprint(x + y);", lambda p: p["a"] + p["b"],
       "A record of Futures has .wait, and the results come back as a record."),
    # ── async functions ──
    FR("print(await f($a) + await f($b));", lambda p: 2 * (p["a"] + p["b"]), "Each call gives a Future<int>; await takes the number out.",
       decls="Future<int> f(int n) async => n * 2;\n"),
    FR("print(await f() * $b);", lambda p: p["a"] * p["b"], "f gives $a after one pause; the await takes it out.",
       decls="Future<int> f() async {\n  await null;\n  return $a;\n}\n"),
    FR("print(await f() ?? $b);", lambda p: p["b"], "f gives null, so ?? supplies the fallback.", decls="Future<int?> f() async => null;\n"),
    FR("print(await f());", lambda p: -1, "g throws, so f's catch returns -1.",
       decls="Future<int> g() async => throw 'x';\nFuture<int> f() async {\n  try {\n    return await g();\n  } catch (e) {\n    return -1;\n  }\n}\n"),
    FR("print(await f());", lambda p: p["a"], "g works, so f returns its value and the catch is skipped.",
       decls="Future<int> g() async => $a;\nFuture<int> f() async {\n  try {\n    return await g();\n  } catch (e) {\n    return -1;\n  }\n}\n"),
    FR("print(await f());", lambda p: p["b"], "A return in finally wins over the catch's return.",
       decls="Future<int> f() async {\n  try {\n    throw 'x';\n  } catch (e) {\n    return $a;\n  } finally {\n    return $b;\n  }\n}\n"),
    FR("var total = 0;\nfor (var i = 1; i <= $k; i++) {\n  total += await Future.value(i);\n}\nprint(total);", lambda p: sum(range(1, p["k"] + 1)),
       "Each await gives the number, and the loop adds them up.", pre_k),
    # ── Completer ──
    FR("var c = Completer<int>();\ntry {\n  c.complete($a);\n  c.complete($b);\n} catch (e) {}\nprint(await c.future);", lambda p: p["a"],
       "A Completer can be completed only once; the second complete throws, and the first value stays.", decls="import 'dart:async';\n"),
    FR("var c = Completer<int>();\nc.completeError('$w');\ntry {\n  await c.future;\n} catch (e) {\n  print(e);\n}", lambda p: p["w"],
       "completeError makes the Future fail, and await throws it.", decls="import 'dart:async';\n"),
    # ── side effects and the order they happen in ──
    FR("var x = 0;\nFuture.microtask(() => x = $a);\nawait null;\nprint(x);", lambda p: p["a"],
       "The microtask was queued before the await resumed, so it has run."),
    FR("var x = 0;\nFuture(() => x = $a);\nawait null;\nprint(x);", lambda p: 0, "The Future(...) is an event; await null resumes before any event, so x is still 0."),
    FR("var x = 0;\nFuture(() => x = $a);\nawait Future.delayed(Duration.zero);\nprint(x);", lambda p: p["a"],
       "The delayed Future is queued behind the first event, so x is set by then."),
    FR("var x = 0;\nFuture.value($a).then((v) => x = v);\nprint(x);", lambda p: 0, "The print comes first: the then runs later."),
    FR("var x = 0;\nFuture.value($a).then((v) => x = v);\nawait null;\nprint(x);", lambda p: p["a"],
       "The then was queued before the await resumed, so x is set."),
    FR("var x = 0;\nawait Future.value($a).then((v) => x = v);\nprint(x);", lambda p: p["a"], "await waits for the whole then, so x is set."),
]
