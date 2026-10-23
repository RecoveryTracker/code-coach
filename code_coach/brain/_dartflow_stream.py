"""Dart flow pack, part 6: Stream Sum - what does the stream pipeline, generator or controller print?

Every template is a complete program (`main(`) that prints exactly ONE line (oracle `value`). The model treats a
stream as the Python list of the events it delivers: `map`/`where`/`take`/`skip`/`takeWhile`/`skipWhile`/`expand`/
`distinct` are list operations, a terminal (`toList`, `length`, `first`, `fold`, `join`...) is a function of that
list, an `async*` function is a generator that does its work LAZILY, one step per listener pull (nothing runs until
somebody listens; `await for` + `break` cancels it and runs its `finally`), `yield*` splices in another stream, a
single-subscription controller buffers events until somebody listens, a broadcast one drops them, and an ordinary
controller delivers asynchronously (a `sync: true` one at once).
"""

from __future__ import annotations

from ._dart_model import DSet
from ._dartflow_model import F
from ._model import Maker

XS = "Stream.fromIterable([$a, $b, $c, $d])"


def xs(p) -> list[int]:
    return [p["a"], p["b"], p["c"], p["d"]]


def SP(expr: str, solve, why: str, decls: str = "", pre=None) -> Maker:
    """`print(await <expr>);` in an async main, after `decls` (imports, generator functions)."""
    return F(decls + "Future<void> main() async {\n  print(await " + expr + ");\n}", solve, why, pre)


def SB(body: str, solve, why: str, decls: str = "", pre=None) -> Maker:
    """A complete async main with the given statements."""
    lines = "\n".join("  " + ln for ln in body.split("\n"))
    return F(decls + "Future<void> main() async {\n" + lines + "\n}", solve, why, pre)


def pre_k(p, rng):
    p["k"] = rng.randint(2, 3)


def pre_k4(p, rng):
    p["k"] = rng.randint(3, 5)


def pre_dups(p, rng):
    p["a"], p["b"], p["c"] = rng.sample(range(2, 9), 3)


IMP = "import 'dart:async';\n"
MAXF = "reduce((s, x) => s > x ? s : x)"

STREAM: list[Maker] = [
    # ── operators and terminals on Stream.fromIterable([a, b, c, d]) ──
    SP(XS + ".map((x) => x * $k).toList()", lambda p: [x * p["k"] for x in xs(p)], "map changes each event; toList collects them in order."),
    SP(XS + ".where((x) => x.isEven).toList()", lambda p: [x for x in xs(p) if x % 2 == 0], "where keeps the events that pass the test."),
    SP(XS + ".map((x) => x * 2).where((x) => x > 8).toList()", lambda p: [x for x in (2 * y for y in xs(p)) if x > 8],
       "Each event is doubled first, then the test is applied to the doubled number."),
    SP(XS + ".take(2).toList()", lambda p: xs(p)[:2], "take(2) keeps the first two events and ends the stream."),
    SP(XS + ".skip(1).toList()", lambda p: xs(p)[1:], "skip(1) drops the first event."),
    SP(XS + ".skip(1).take(2).toList()", lambda p: xs(p)[1:3], "Skip one, then keep two."),
    SP(XS + ".takeWhile((x) => x < 6).toList()", lambda p: _take_while(xs(p), lambda x: x < 6),
       "takeWhile stops at the FIRST event that fails the test, even if later ones would pass."),
    SP(XS + ".skipWhile((x) => x < 6).toList()", lambda p: _skip_while(xs(p), lambda x: x < 6),
       "skipWhile drops events only while the test holds; from the first failure on, everything stays."),
    SP(XS + ".expand((x) => [x, x * 10]).toList()", lambda p: [y for x in xs(p) for y in (x, x * 10)], "expand turns each event into several."),
    SP(XS + ".fold<int>(0, (s, x) => s + x)", lambda p: sum(xs(p)), "fold adds the events up from 0."),
    SP(XS + ".map((x) => x * x).fold<int>(0, (s, x) => s + x)", lambda p: sum(x * x for x in xs(p)), "Square each event, then add them up."),
    SP(XS + "." + MAXF, lambda p: max(xs(p)), "reduce keeps the larger of the two each time: the maximum."),
    SP(XS + ".reduce((s, x) => s - x)", lambda p: xs(p)[0] - sum(xs(p)[1:]), "reduce starts with the first event, then subtracts each of the others."),
    SP(XS + ".join('-')", lambda p: "-".join(str(x) for x in xs(p)), "join glues the events with the separator."),
    SP(XS + ".map((x) => x.isEven ? 'E' : 'O').join()", lambda p: "".join("E" if x % 2 == 0 else "O" for x in xs(p)),
       "Each number becomes E or O; join with no separator glues them."),
    SP(XS + ".where((x) => x > 5).length", lambda p: len([x for x in xs(p) if x > 5]), "length counts the events that got through where."),
    SP(XS + ".first", lambda p: xs(p)[0], "first is the first event."),
    SP(XS + ".last", lambda p: xs(p)[-1], "last waits for the end and gives the final event."),
    SP(XS + ".elementAt(2)", lambda p: xs(p)[2], "elementAt counts from 0."),
    SP(XS + ".skip(1).first", lambda p: xs(p)[1], "After skipping one, the first is the second event."),
    SP(XS + ".take(3).last", lambda p: xs(p)[2], "take(3) ends the stream after three events, so last is the third."),
    SP(XS + ".any((x) => x > 7)", lambda p: any(x > 7 for x in xs(p)), "any is true if at least one event passes."),
    SP(XS + ".every((x) => x.isOdd)", lambda p: all(x % 2 == 1 for x in xs(p)), "every is true only if all events pass."),
    SP(XS + ".contains($b)", lambda p: True, "contains looks for an equal event."),
    SP(XS + ".where((x) => x > 100).isEmpty", lambda p: True, "Nothing gets through where, so the stream is empty."),
    SP(XS + ".firstWhere((x) => x > 5, orElse: () => -1)", lambda p: next((x for x in xs(p) if x > 5), -1),
       "firstWhere gives the first event that passes, or the orElse value."),
    SP(XS + ".map((x) => x % 3).toSet()", lambda p: DSet(x % 3 for x in xs(p)), "A set keeps each value once, in the order first seen."),
    SP("Stream.fromIterable([$a, $a, $b, $b, $c]).distinct().length", lambda p: len(_distinct([p["a"], p["a"], p["b"], p["b"], p["c"]])),
       "distinct drops an event equal to the one just before it.", pre=pre_dups),
    SP("Stream.fromIterable([$a, $b, $a]).distinct().length", lambda p: 3, "distinct only compares neighbours; a, b, a are all different neighbours."),
    SP(XS + ".asyncMap((x) async => x + 1).toList()", lambda p: [x + 1 for x in xs(p)], "asyncMap waits for each async function and passes on its result."),
    SP("Stream.fromIterable([$a, $b]).asyncExpand((x) => Stream.fromIterable([x, -x])).toList()",
       lambda p: [y for x in (p["a"], p["b"]) for y in (x, -x)], "asyncExpand replaces each event with all the events of a stream."),
    SP("Stream.periodic(Duration.zero, (i) => i * $a).take(3).toList()", lambda p: [0, p["a"], 2 * p["a"]], "periodic counts i = 0, 1, 2, ...; take(3) stops it."),
    SP("Stream.value($a).toList()", lambda p: [p["a"]], "Stream.value is a stream of one event."),
    SP("Stream.fromFuture(Future.value($a)).map((x) => x * 2).toList()", lambda p: [p["a"] * 2], "A stream from a Future has one event."),
    # ── async* generators ──
    SP("gen($k).toList()", lambda p: [i * i for i in range(1, p["k"] + 1)], "The generator yields i times i for i = 1 up to n.",
       decls="Stream<int> gen(int n) async* {\n  for (var i = 1; i <= n; i++) {\n    yield i * i;\n  }\n}\n", pre=pre_k4),
    SP("gen(7).toList()", lambda p: [i for i in range(1, 8) if i % 2], "Only the odd numbers are yielded.",
       decls="Stream<int> gen(int n) async* {\n  for (var i = 1; i <= n; i++) {\n    if (i.isOdd) yield i;\n  }\n}\n"),
    SP("outer().toList()", lambda p: [p["a"], p["b"], p["c"], p["d"]], "yield* hands over all the events of the inner stream at that point.",
       decls="Stream<int> inner() async* {\n  yield $b;\n  yield $c;\n}\nStream<int> outer() async* {\n  yield $a;\n  yield* inner();\n  yield $d;\n}\n"),
    SP("nat().take($k).toList()", lambda p: list(range(p["k"])), "The generator never ends, but take stops listening after k events.",
       decls="Stream<int> nat() async* {\n  var i = 0;\n  while (true) yield i++;\n}\n", pre=pre_k4),
    SP("nat().where((x) => x.isOdd).take(3).toList()", lambda p: [1, 3, 5], "The odd numbers from an endless stream, three of them.",
       decls="Stream<int> nat() async* {\n  var i = 0;\n  while (true) yield i++;\n}\n"),
    SP("nat().map((x) => x * x).take($k).last", lambda p: (p["k"] - 1) ** 2, "The k-th square of 0, 1, 4, 9, ...", pre=pre_k4,
       decls="Stream<int> nat() async* {\n  var i = 0;\n  while (true) yield i++;\n}\n"),
    SP("words().join(' ')", lambda p: p["w"] + " " + p["v"], "Two yields, two events, joined with a space.",
       decls="Stream<String> words() async* {\n  yield '$w';\n  await Future.delayed(Duration.zero);\n  yield '$v';\n}\n"),
    SB("var total = 0;\nawait for (var x in Stream.fromIterable([$a, $b, $c, $d])) {\n  if (x.isOdd) continue;\n  total += x;\n}\nprint(total);",
       lambda p: sum(x for x in xs(p) if x % 2 == 0), "continue skips the odd ones; the even ones are added."),
    SB("var total = 0;\nawait for (var x in Stream.fromIterable([$a, $b, $c, $d])) {\n  if (x > 5) break;\n  total += x;\n}\nprint(total);",
       lambda p: sum(_take_while(xs(p), lambda x: x <= 5)), "break leaves the loop (and the stream) at the first x above 5."),
    SB("await for (var x in gen()) {\n  log += 'c$$x';\n}\nprint(log);",
       lambda p: "".join(f"g{i}c{i}" for i in range(1, p["k"] + 1)), "A generator works lazily: it makes one event, the loop body runs, then it goes on.",
       decls="String log = '';\nStream<int> gen() async* {\n  for (var i = 1; i <= $k; i++) {\n    log += 'g$$i';\n    yield i;\n  }\n}\n", pre=pre_k),
    SB("var s = gen();\nprint(log);", lambda p: "x", "Nothing in the generator runs until somebody listens.",
       decls="String log = 'x';\nStream<int> gen() async* {\n  log += 'g';\n  yield 1;\n}\n"),
    SB("await gen().toList();\nprint(log);", lambda p: "xgh", "Listening starts the generator, and toList runs it to the end.",
       decls="String log = 'x';\nStream<int> gen() async* {\n  log += 'g';\n  yield 1;\n  log += 'h';\n}\n"),
    SB("await for (var x in g()) {\n  s += '$$x';\n  if (x == 2) break;\n}\nprint(s);", lambda p: "12F",
       "break cancels the stream: the generator stops at its yield and its finally runs. 3 is never produced.",
       decls="var s = '';\nStream<int> g() async* {\n  try {\n    yield 1;\n    yield 2;\n    yield 3;\n  } finally {\n    s += 'F';\n  }\n}\n"),
    SB("await for (var x in g()) {\n  s += '$$x';\n}\nprint(s);", lambda p: "123F", "Read to the end, the generator finishes normally and then the finally runs.",
       decls="var s = '';\nStream<int> g() async* {\n  try {\n    yield 1;\n    yield 2;\n    yield 3;\n  } finally {\n    s += 'F';\n  }\n}\n"),
    SB("print(gen());", lambda p: "(1, 2, 3)", "A sync* function gives an Iterable, which print shows in round brackets.",
       decls="Iterable<int> gen() sync* {\n  yield 1;\n  yield 2;\n  yield 3;\n}\n"),
    SB("print(gen($k).toList());", lambda p: [i * 2 for i in range(1, p["k"] + 1)], "toList of a sync* Iterable is a plain list.", pre=pre_k,
       decls="Iterable<int> gen(int n) sync* {\n  for (var i = 1; i <= n; i++) {\n    yield i * 2;\n  }\n}\n"),
    # ── StreamController ──
    SB("var c = StreamController<int>();\nc.add($a);\nc.add($b);\nc.close();\nprint(await c.stream.toList());", lambda p: [p["a"], p["b"]],
       "A single-subscription controller keeps the events until somebody listens.", decls=IMP),
    SB("var c = StreamController<int>.broadcast();\nc.add($a);\nvar f = c.stream.toList();\nc.add($b);\nc.close();\nprint(await f);", lambda p: [p["b"]],
       "A broadcast stream drops events nobody is listening to: the first one came too early.", decls=IMP),
    SB("var c = StreamController<int>();\nc.add($a);\nvar f = c.stream.toList();\nc.add($b);\nc.close();\nprint(await f);", lambda p: [p["a"], p["b"]],
       "The same code with an ordinary controller: the early event was kept for the listener.", decls=IMP),
    SB("var c = StreamController<int>();\nvar s = 0;\nc.stream.listen((x) => s += x);\nc.add($a);\nprint(s);", lambda p: 0,
       "Events are delivered later, not inside add, so s is still 0.", decls=IMP),
    SB("var c = StreamController<int>(sync: true);\nvar s = 0;\nc.stream.listen((x) => s += x);\nc.add($a);\nprint(s);", lambda p: p["a"],
       "A sync controller calls the listener inside add.", decls=IMP),
    SB("var c = StreamController<int>();\nvar s = 0;\nc.stream.listen((x) => s += x);\nc.add($a);\nc.add($b);\nawait c.close();\nprint(s);", lambda p: p["a"] + p["b"],
       "await c.close() waits until the done event is delivered, after the data events.", decls=IMP),
    SB("var c = StreamController<int>.broadcast(), r = [];\nc.stream.listen(r.add);\nc.stream.listen((x) => r.add(x * 10));\nc.add($a);\nawait c.close();\nprint(r);",
       lambda p: [p["a"], p["a"] * 10], "A broadcast stream sends every event to every listener, one listener after the other.", decls=IMP),
    SB("var c = StreamController<int>();\nc.stream.listen((_) {});\ntry {\n  c.stream.listen((_) {});\n} catch (e) {\n  print(e.runtimeType);\n}", lambda p: "StateError",
       "A single-subscription stream can have only one listener: the second listen throws a StateError.", decls=IMP),
    SB("var c = StreamController<int>();\nc.add($a);\nc.addError('x');\nc.add($b);\nc.close();\nprint(await c.stream.handleError((e) {}).toList());",
       lambda p: [p["a"], p["b"]], "handleError swallows the error event; the data events go on.", decls=IMP),
    SB("var c = StreamController<int>();\nc.add($a);\nc.addError('$w');\nc.add($b);\nc.close();\ntry {\n  await c.stream.toList();\n} catch (e) {\n  print(e);\n}",
       lambda p: p["w"], "toList stops at the first error event and fails with it.", decls=IMP),
    SB("var c = StreamController<int>();\nprint(c.hasListener);", lambda p: False, "Nobody has listened yet.", decls=IMP),
    SB("var c = StreamController<int>();\nc.stream.listen((_) {});\nprint(c.hasListener);", lambda p: True, "Now somebody listens.", decls=IMP),
    SB("var c = StreamController<int>();\nc.close();\nprint(c.isClosed);", lambda p: True, "close() marks the controller closed at once.", decls=IMP),
    SB("var log = '';\nStream.fromIterable([$a, $b]).listen((x) => log += '$$x', onDone: () => log += 'D');\nawait Future.delayed(Duration.zero);\nprint(log);",
       lambda p: f"{p['a']}{p['b']}D", "The data events come first, then the done callback."),
    SB("var s = Stream.fromIterable([$a, $b, $c]).map((x) => x == $b ? throw 'bad' : x).handleError((e) {});\nprint(await s.toList());",
       lambda p: [p["a"], p["c"]], "The map throws for b, that becomes an error event, and handleError drops it."),
    SB("var s = Stream.fromIterable([$a, $b, $c]).map((x) => x == $b ? throw '$w' : x);\ntry {\n  await s.toList();\n} catch (e) {\n  print(e);\n}",
       lambda p: p["w"], "Without handleError, toList fails with the thrown value."),
    SB("var sub = Stream.fromIterable([$a, $b, $c]).listen(null);\nawait sub.cancel();\nprint('done');", lambda p: "done", "cancel just stops listening; nothing fails."),
]


def _take_while(xs_: list[int], test) -> list[int]:
    out = []
    for x in xs_:
        if not test(x):
            break
        out.append(x)
    return out


def _skip_while(xs_: list[int], test) -> list[int]:
    i = 0
    while i < len(xs_) and test(xs_[i]):
        i += 1
    return xs_[i:]


def _distinct(xs_: list[int]) -> list[int]:
    out: list[int] = []
    for x in xs_:
        if not out or out[-1] != x:
            out.append(x)
    return out
