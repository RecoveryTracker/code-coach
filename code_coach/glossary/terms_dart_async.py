"""Dart words, part 3: Futures and Streams, the event loop, errors, text, collections' methods, libraries.

Examples with `main(` are whole programs; the others are the body of main (see terms_dart_core.py).
The test run drains the event loop after each example, so the order of async output is the real one."""

from __future__ import annotations

from .entry import Entry, dart

TERMS: list[Entry] = [
    # ── Async ───────────────────────────────────────────────────────────
    *dart(
        "future",
        "Future",
        "An object standing for a value that is not ready yet. It later completes with a value, or with an error.",
        see=("async-await", "then", "event-loop"),
        priority=70,
        aka=("futures", "future<t>", "future.delayed", "future.wait", "promise", "completer", "pending"),
        detect=(r"\bFuture\b",),
        rules=(
            "await future waits for it and gives the value; inside a function marked async.",
            "Future.value(3) is already done; Future.delayed(Duration(seconds: 1), () => 3) completes later.",
            "Future.wait([a, b]) gives a list of the results once all are done.",
            "A function marked async always returns a Future, even if you return a plain value.",
        ),
        example="""
            Future<int> slowDouble(int n) async => n * 2;
            Future<void> main() async {
              print('before');
              final r = await slowDouble(4);
              print(r);
              print(await Future.wait([slowDouble(1), slowDouble(2)]));
            }
        """,
        out="before\n8\n[2, 4]",
    ),
    *dart(
        "async-await",
        "async and await",
        "A function marked async can use await, which pauses just that function until a Future finishes while the rest of the program carries on.",
        see=("future", "event-loop", "try-catch"),
        priority=75,
        aka=("async", "await", "asynchronous", "async function", "async/await", "waiting", "execution order", "order of execution"),
        detect=(r"\bawait\b", r"\basync\b(?!\*)"),
        rules=(
            "An async function runs normally until its first await; then it hands control back to the caller and returns a Future.",
            "Even awaiting an already finished Future lets other waiting code run first.",
            "Errors from an awaited Future are thrown at the await, so ordinary try/catch works.",
            "await only works inside an async function (main can be Future<void> main() async).",
        ),
        example="""
            Future<void> task() async {
              print('task start');
              await Future<void>.value();
              print('task end');
            }
            Future<void> main() async {
              var f = task();
              print('after call');
              await f;
              print('done');
            }
        """,
        out="task start\nafter call\ntask end\ndone",
    ),
    *dart(
        "then",
        "then",
        "future.then(callback) runs the callback when the Future completes, and gives a new Future for what the callback returns.",
        see=("future", "catch-error", "callback"),
        priority=65,
        aka=("future.then", ".then", "whencomplete", "chaining", "promise chain", "then callback"),
        detect=(r"\.then\s*[(<]",),
        rules=(
            "The callback does not run at the line where you write it; it runs later, as a microtask.",
            "Chains read top to bottom: f.then(a).then(b) gives a's result to b.",
            "await is usually easier to read than a long chain of then.",
        ),
        example="""
            Future<void> main() {
              return Future.value(2)
                  .then((v) => v * 10)
                  .then((v) => print(v));
            }
        """,
        out="20",
    ),
    *dart(
        "catch-error",
        "catchError",
        "future.catchError(handler) handles an error from a Future, like catch does for await. whenComplete runs at the end either way.",
        see=("future", "try-catch", "finally"),
        priority=65,
        aka=("catcherror", "future error", "whencomplete", "handle future error", "onerror"),
        detect=(r"\.catchError\s*\(|\.whenComplete\s*\(",),
        rules=(
            "The handler must give back a value of the Future's type (or throw again).",
            "With await, plain try/catch does the same job and is clearer.",
            "An error in a Future nobody handles is reported as uncaught and can stop the program.",
        ),
        example="""
            Future<void> main() {
              return Future<int>.error('boom')
                  .then((v) => v + 1)
                  .catchError((e) {
                    print('caught $e');
                    return 0;
                  })
                  .whenComplete(() => print('cleanup'));
            }
        """,
        out="caught boom\ncleanup",
    ),
    *dart(
        "stream",
        "Stream",
        "A sequence of values that arrive over time, one after another: keystrokes, messages, ticks. A Future is one value later; a Stream is many.",
        see=("future", "async-generator", "iterable"),
        priority=70,
        aka=("streams", "stream<t>", "await for", "listen", "streamcontroller", "event stream", "broadcast stream"),
        detect=(r"\bStream\b|\bawait\s+for\b|\.listen\s*\(",),
        rules=(
            "await for (final v in stream) { ... } handles each value as it comes; stream.listen(callback) does the same with a callback.",
            "A stream has map, where and toList like a list, but they work on values as they arrive.",
            "A plain stream (such as a StreamController's) can be listened to only once; a broadcast stream can have many listeners.",
            "stream.toList() gives a Future of the list.",
        ),
        example="""
            Future<void> main() async {
              final s = Stream.fromIterable([1, 2, 3, 4]).where((n) => n.isEven).map((n) => n * 10);
              await for (final v in s) {
                print(v);
              }
            }
        """,
        out="20\n40",
    ),
    *dart(
        "async-generator",
        "async* and yield",
        "A function marked async* makes a Stream. Each yield sends one value out, and the function can wait between them.",
        see=("stream", "generator", "async-await"),
        priority=75,
        aka=("async*", "yield", "yield*", "stream generator", "async generator"),
        detect=(r"\basync\s*\*", r"\byield\*?\b"),
        rules=(
            "The function returns at once with a Stream; its body runs as the stream is listened to.",
            "yield value sends a value; yield* other sends all of another stream's values.",
            "The body only runs while someone is listening.",
        ),
        example="""
            Stream<int> count(int n) async* {
              for (var i = 1; i <= n; i++) {
                yield i;
              }
            }
            Future<void> main() async {
              print(await count(3).toList());
            }
        """,
        out="[1, 2, 3]",
    ),
    *dart(
        "generator",
        "sync* generator",
        "A function marked sync* that produces an Iterable one value at a time with yield, working out each value only when asked for it.",
        see=("lazy", "async-generator", "iterable"),
        priority=70,
        aka=("sync*", "generators", "iterator block", "sync generator"),
        detect=(r"\bsync\s*\*",),
        rules=(
            "Calling it does not run the body; the body runs as far as the next yield each time a value is requested.",
            "it.first only runs until the first yield.",
            "yield* other produces every value of another iterable.",
        ),
        example="""
            Iterable<int> evens(int max) sync* {
              for (var i = 0; i <= max; i += 2) {
                print('making $i');
                yield i;
              }
            }
            var it = evens(4);
            print('created');
            print(it.first);
        """,
        out="created\nmaking 0\n0",
    ),
    *dart(
        "event-loop",
        "Event loop",
        "How Dart runs one thing at a time: first the main code to its end, then all waiting microtasks, then one event (a timer, a Future callback) at a time, clearing the microtasks after each.",
        see=("microtask", "future", "async-await"),
        priority=60,
        aka=("event queue", "event loop", "queue", "single threaded", "run to completion", "timer", "settimeout"),
        detect=(r"\bscheduleMicrotask\b|\bTimer\b|Future\.delayed|Future\.microtask",),
        rules=(
            "Dart code never runs two pieces at once in one isolate: a callback waits until the current code finishes.",
            "Order: all code now, then microtasks (scheduleMicrotask, then-callbacks of finished Futures), then the next event (Future(() => ...), Timer, Future.delayed).",
            "Future(() => x) and Future.delayed(Duration.zero, ...) go in the event queue, so they run after every microtask.",
            "A long loop in main blocks everything, including screen updates in Flutter.",
        ),
        example="""
            import 'dart:async';
            void main() {
              Future(() => print('event'));
              scheduleMicrotask(() => print('microtask'));
              print('sync');
            }
        """,
        out="sync\nmicrotask\nevent",
    ),
    *dart(
        "microtask",
        "Microtask",
        "A tiny job that runs as soon as the current code finishes, before any timer or other event. Futures that are already done run their then-callbacks this way.",
        see=("event-loop", "then", "future"),
        priority=60,
        aka=("microtasks", "scheduleMicrotask", "microtask queue", "future.microtask"),
        detect=(r"\bscheduleMicrotask\b|Future\.microtask",),
        rules=(
            "All microtasks run before the next event, including ones added by microtasks.",
            "A then-callback of a Future that completes runs as a microtask, so it runs before the next event.",
            "Too many microtasks starve events (and, in Flutter, drawing).",
        ),
        example="""
            Future(() => print('E1')).then((_) => print('after E1'));
            Future.microtask(() => print('M'));
            Future.delayed(Duration.zero, () => print('E2'));
            print('S');
        """,
        out="S\nM\nE1\nafter E1\nE2",
    ),
    *dart(
        "isolate",
        "Isolate",
        "Dart's version of a thread: separate code with its own memory that runs at the same time as the main code. Isolates share nothing and talk by sending messages.",
        see=("event-loop", "future", "async-await"),
        priority=55,
        aka=("isolates", "isolate.run", "thread", "threads", "compute", "parallel", "concurrency", "background work"),
        detect=(r"\bIsolate\b|\bcompute\s*\(",),
        rules=(
            "async/await does not make code run in parallel; an isolate does.",
            "Isolate.run(() => work()) runs work in a new isolate and gives a Future of the result.",
            "Use one for heavy computing so the screen (the main isolate) stays smooth.",
        ),
        example="""
            import 'dart:isolate';
            Future<void> main() async {
              final r = await Isolate.run(() => [1, 2, 3, 4].fold<int>(0, (a, b) => a + b * b));
              print(r);
            }
        """,
        out="30",
    ),
    # ── Errors ──────────────────────────────────────────────────────────
    *dart(
        "try-catch",
        "try, on and catch",
        "try { ... } runs code that might fail. on Type catch (e) { ... } handles one kind of failure; a plain catch handles any.",
        see=("finally", "throw", "exception"),
        priority=65,
        aka=("try", "catch", "on", "try-except", "try-catch", "try catch", "except", "error handling", "on catch"),
        detect=(r"\btry\s*\{", r"\bcatch\s*\(", r"\bon\s+[A-Z]\w*\s*(?:catch\b|\{)"),
        rules=(
            "on FormatException catch (e) handles only that type (and its subtypes); catch (e, st) also gives the stack trace.",
            "The first matching clause runs, top to bottom, so put specific types before a general catch.",
            "If nothing matches, the error keeps going up to the caller.",
            "finally { ... } runs at the end whether or not anything failed.",
        ),
        example="""
            try {
              int.parse('x');
            } on FormatException catch (e) {
              print('bad number');
            } catch (e) {
              print('other');
            } finally {
              print('done');
            }
        """,
        out="bad number\ndone",
    ),
    *dart(
        "finally",
        "finally",
        "A block after try/catch that always runs at the end: after success, after a handled error, even after a return.",
        see=("try-catch", "return", "throw"),
        priority=55,
        aka=("cleanup", "always runs", "whencomplete"),
        detect=(r"\bfinally\b",),
        rules=(
            "Use it for cleanup that must happen: closing a file, stopping a spinner.",
            "If try has a return, finally still runs first.",
            "An error not caught anywhere still runs the finally blocks while it travels up.",
        ),
        example="""
            int f() {
              try {
                return 1;
              } finally {
                print('cleanup');
              }
            }
            print(f());
        """,
        out="cleanup\n1",
    ),
    *dart(
        "throw",
        "throw",
        "Stops the normal flow and raises an error: throw Exception('bad input'). The error travels up to the nearest matching catch.",
        see=("try-catch", "exception", "rethrow"),
        priority=60,
        aka=("raise", "throws", "thrown", "throwing", "throw an error"),
        detect=(r"\bthrow\b",),
        rules=(
            "You can throw any object, but throw an Exception or Error subtype.",
            "throw is an expression: int f(int x) => x > 0 ? x : throw ArgumentError('positive only');",
            "An error nobody catches ends the program with a message and a stack trace.",
        ),
        example="""
            int positive(int x) => x > 0 ? x : throw ArgumentError('positive only');
            print(positive(3));
            try {
              positive(-1);
            } catch (e) {
              print(e);
            }
        """,
        out="3\nInvalid argument(s): positive only",
    ),
    *dart(
        "rethrow",
        "rethrow",
        "Inside a catch, rethrow throws the same error again, so the caller sees it (with the original stack trace) after you have done your own part.",
        see=("throw", "try-catch", "stack-trace"),
        priority=70,
        aka=("rethrows", "re-throw", "pass the error on"),
        detect=(r"\brethrow\b",),
        rules=(
            "Log or clean up in the catch, then rethrow so nothing is silently swallowed.",
            "rethrow keeps the original stack trace; throw e starts a new one.",
            "It is only allowed inside a catch clause.",
        ),
        example="""
            void run() {
              try {
                throw StateError('broken');
              } catch (e) {
                print('logging: $e');
                rethrow;
              }
            }
            try {
              run();
            } catch (e) {
              print('caller got: $e');
            }
        """,
        out="logging: Bad state: broken\ncaller got: Bad state: broken",
    ),
    *dart(
        "exception",
        "Exception and Error",
        "Dart splits failures in two. An Exception is something a program may expect and handle (bad input, a missing file). An Error is a mistake in the code itself (bad index, wrong state) that you normally fix instead of catching.",
        see=("try-catch", "format-exception", "index-error"),
        priority=50,
        aka=("exceptions", "error", "errors", "error class", "exception class", "custom exception", "implements exception"),
        detect=(r"\bException\b|\bError\b",),
        rules=(
            "FormatException and IOException are Exceptions; RangeError, StateError, ArgumentError and TypeError are Errors.",
            "catch (e) catches both; on Exception catch (e) catches only Exceptions.",
            "Make your own: class MyError implements Exception { ... }.",
            "print(e) shows 'Exception: message' for Exception('message').",
        ),
        example="""
            try {
              [1][5];
            } catch (e) {
              print(e is Error);
            }
            try {
              int.parse('x');
            } catch (e) {
              print(e is Exception);
            }
            print(Exception('oops'));
        """,
        out="true\ntrue\nException: oops",
    ),
    *dart(
        "format-exception",
        "FormatException",
        "The error thrown when text is not in the shape expected, such as int.parse('abc') or a broken date or JSON.",
        see=("type-conversion", "exception", "try-catch"),
        priority=60,
        aka=("formatexception", "invalid format", "parse error"),
        detect=(r"\bFormatException\b",),
        rules=(
            "int.parse and double.parse throw it on text that is not a number.",
            "int.tryParse(text) gives null instead, with no error to catch.",
            "It is an Exception, meant to be caught.",
        ),
        example="""
            try {
              int.parse('12a');
            } on FormatException {
              print('not a number');
            }
            print(int.tryParse('12a'));
            print(int.tryParse('12'));
        """,
        out="not a number\nnull\n12",
    ),
    *dart(
        "index-error",
        "RangeError (index error)",
        "The error thrown when you ask for an item at a position that does not exist, like [1, 2][5].",
        see=("index", "exception", "state-error"),
        priority=60,
        aka=("rangeerror", "range error", "index out of range", "out of range", "out of bounds", "index error", "invalid value"),
        detect=(r"\bRangeError\b",),
        rules=(
            "Valid positions of a list with n items are 0 to n - 1; xs[n] and xs[-1] both throw.",
            "It is an Error (a bug to fix), not an Exception.",
            "Check xs.length first, or use xs.elementAtOrNull(i) for null instead of an error.",
        ),
        example="""
            var xs = [10, 20];
            try {
              print(xs[2]);
            } on RangeError {
              print('no item 2');
            }
            print(xs.elementAtOrNull(2));
        """,
        out="no item 2\nnull",
    ),
    *dart(
        "state-error",
        "StateError",
        "The error thrown when a call does not make sense in the object's current state, most often asking for an item of an empty collection.",
        see=("exception", "index-error", "reduce"),
        priority=55,
        aka=("stateerror", "bad state", "no element", "too many elements", "stateerror"),
        detect=(r"\bStateError\b",),
        rules=(
            "[].first, [].last and [].reduce(...) throw StateError: Bad state: No element.",
            "Use firstOrNull or a default: xs.isEmpty ? 0 : xs.first.",
            "It is an Error, a bug to fix.",
        ),
        example="""
            try {
              print(<int>[].first);
            } on StateError catch (e) {
              print(e);
            }
            print(<int>[].firstOrNull);
        """,
        out="Bad state: No element\nnull",
    ),
    *dart(
        "type-error",
        "TypeError",
        "The error thrown when a value is not the type the code needed: a failed as cast, or ! on a value that is null.",
        see=("type-check", "null-assertion", "exception"),
        priority=60,
        aka=("typeerror", "type error", "cast error", "bad cast", "is not a subtype", "type mismatch"),
        detect=(r"\bTypeError\b",),
        rules=(
            "Object o = 'a'; o as int throws a TypeError.",
            "Many type mistakes never reach run time: the compiler rejects int x = 'a' before the program starts.",
            "Test with is first when the type is not certain.",
        ),
        example="""
            Object o = 'text';
            try {
              print(o as int);
            } on TypeError {
              print('not an int');
            }
        """,
        out="not an int",
    ),
    *dart(
        "stack-trace",
        "Stack trace",
        "The list of function calls that were active when an error happened, newest first. It shows how the program got to the failing line.",
        see=("call-stack", "try-catch", "rethrow"),
        priority=50,
        aka=("stacktrace", "traceback", "stack trace", "trace", "stacktrace.current", "line number"),
        detect=(r"\bStackTrace\b|\bcatch\s*\(\s*\w+\s*,\s*\w+\s*\)",),
        rules=(
            "catch (e, st) gives the trace as the second name.",
            "StackTrace.current is the trace right now, without any error.",
            "Each line names a function and a place in a file, such as #0 main (file.dart:5:3).",
        ),
        example="""
            try {
              throw Exception('x');
            } catch (e, st) {
              print(st is StackTrace);
              print(st.toString().isNotEmpty);
            }
        """,
        out="true\ntrue",
    ),
    *dart(
        "error-message",
        "Error message",
        "The text describing what went wrong. Printing the caught error in a catch shows it, with a prefix for the kind of error.",
        see=("exception", "string-representation", "try-catch"),
        priority=45,
        aka=("message", "error text", "e.message", "e.tostring", "error output"),
        rules=(
            "Exception('x') prints as Exception: x; StateError('x') as Bad state: x; ArgumentError('x') as Invalid argument(s): x.",
            "FormatException has a .message you can read: e.message.",
            "Use messages to tell the reader what to fix, not only what failed.",
        ),
        example="""
            print(Exception('x'));
            print(StateError('x'));
            print(ArgumentError('x'));
            try {
              int.parse('q');
            } on FormatException catch (e) {
              print(e.message);
            }
        """,
        out="Exception: x\nBad state: x\nInvalid argument(s): x\nInvalid radix-10 number",
    ),
    *dart(
        "runtime-error",
        "Runtime error",
        "A problem that only appears while the program runs, such as a bad index or a null where a value was needed. It throws an error at that moment.",
        see=("syntax-error", "exception", "stack-trace"),
        priority=40,
        aka=("runtime errors", "runtime exception", "crash", "bug", "uncaught exception", "unhandled exception", "run time error"),
        rules=(
            "Dart catches many mistakes earlier, as compile errors, so fewer problems are left for run time than in Python or JavaScript.",
            "Typical ones: RangeError, StateError, FormatException, TypeError (failed as or !).",
            "An uncaught error ends the program (or, in a Future, is reported as uncaught).",
        ),
        example="""
            try {
              var xs = <int>[];
              print(xs.first);
            } catch (e) {
              print('crashed: ${e.runtimeType}');
            }
        """,
        out="crashed: StateError",
    ),
    *dart(
        "syntax-error",
        "Compile error (syntax error)",
        "A mistake Dart finds before the program runs: broken grammar, a missing semicolon, or a type that cannot work. The program does not start at all.",
        see=("runtime-error", "null-safety", "type"),
        priority=40,
        aka=("syntax error", "compile error", "compile-time error", "compilation error", "does not compile", "analyzer error", "analysis error", "compile time"),
        rules=(
            "Dart is checked before running: int x = 'a'; and calling a method that does not exist are compile errors.",
            "Null safety adds more: using an int? where an int is needed is a compile error.",
            "Because the whole program is checked first, nothing prints if a single line has a compile error.",
        ),
    ),
    # ── Strings and text ────────────────────────────────────────────────
    *dart(
        "string-interpolation",
        "String interpolation ($)",
        "Putting a value inside a string: '$name' inserts the variable, and '${expression}' inserts any expression.",
        see=("string", "string-representation", "format"),
        priority=60,
        aka=("interpolation", "$", "${}", "template string", "template literal", "template-literal", "f-string", "fstring", "string template", "concatenation"),
        detect=(r"raw:'[^'\n]*\$[\w{][^'\n]*'|\"[^\"\n]*\$[\w{][^\"\n]*\"",),
        rules=(
            "'$name' takes just the name; use braces for anything longer: '${name.length}', '${a + b}'.",
            "'$name.length' is the name followed by the text .length, not the length!",
            "Write \\$ for a real dollar sign: 'cost \\$5'.",
            "The value is turned into text with toString().",
        ),
        example="""
            var name = 'Ann';
            var n = 3;
            print('Hi $name, ${n * 2} items, ${name.length} letters');
            print('$name.length');
            print('cost: \\$5');
        """,
        out="Hi Ann, 6 items, 3 letters\nAnn.length\ncost: $5",
    ),
    *dart(
        "raw-string",
        "Raw string (r'...')",
        "A string with r in front, in which backslashes and $ mean themselves. Handy for patterns and file paths.",
        see=("string", "regexp", "string-interpolation"),
        priority=60,
        aka=("raw string", "r''", "raw strings", "multiline string", "triple quote", "triple-quoted string", "escape sequence", "escape"),
        detect=(r"raw:\br['\"]", r"raw:'''|\"\"\""),
        rules=(
            "'a\\nb' has a line break (3 characters); r'a\\nb' is the 4 characters a \\ n b.",
            "Triple quotes ''' ... ''' (or \"\"\" ... \"\"\") make a string that can span several lines.",
            "In a raw string, '$x' is not interpolated.",
        ),
        example="""
            print('a\\nb'.length);
            print(r'a\\nb'.length);
            print(r'C:\\temp');
            var x = 1;
            print(r'$x');
        """,
        out="3\n4\nC:\\temp\n$x",
    ),
    *dart(
        "string-buffer",
        "StringBuffer",
        "An object for building a long string piece by piece without making a new string at every step.",
        see=("string", "cascade", "join"),
        priority=60,
        aka=("stringbuffer", "string builder", "stringbuilder", "build a string", "write", "writeln"),
        detect=(r"\bStringBuffer\b",),
        rules=(
            "sb.write('a') adds text, sb.writeln('a') adds text and a line break, sb.writeAll(items, ', ') adds many.",
            "sb.toString() (or printing it) gives the finished string.",
            "Much faster than text += piece in a long loop.",
        ),
        example="""
            final sb = StringBuffer();
            for (var i = 1; i <= 3; i++) {
              sb.write(i);
              if (i < 3) sb.write(', ');
            }
            print(sb);
            print(sb.length);
        """,
        out="1, 2, 3\n7",
    ),
    *dart(
        "regexp",
        "RegExp (regular expression)",
        "A pattern describing text to find, like \\d+ for 'one or more digits'. RegExp(r'\\d+') builds one.",
        see=("raw-string", "string-search", "replace"),
        priority=60,
        aka=("regex", "regular expression", "regexes", "regular expressions", "capture group", "group"),
        detect=(r"\bRegExp\b",),
        rules=(
            "Write the pattern as a raw string so backslashes survive: RegExp(r'\\d+').",
            "hasMatch(text) says whether there is a match; firstMatch gives the first Match (or null); allMatches gives all of them.",
            "match.group(0) is the whole matched text; group(1) is the first (...) part.",
            "text.replaceAll(re, 'x') replaces every match.",
        ),
        example="""
            var re = RegExp(r'\\d+');
            print(re.hasMatch('abc 42'));
            print(re.firstMatch('abc 42 and 7')!.group(0));
            print(re.allMatches('a1b22c333').map((m) => m.group(0)).toList());
            print('a1b22'.replaceAll(re, '#'));
        """,
        out="true\n42\n[1, 22, 333]\na#b#",
    ),
    *dart(
        "string-search",
        "Searching in a string",
        "Finding text inside text: contains, indexOf, startsWith, endsWith, firstMatch.",
        see=("regexp", "index", "string"),
        priority=40,
        aka=("search", "find", "contains", "indexof", "startswith", "endswith", "substring search", "lastindexof"),
        detect=(r"\.(?:contains|indexOf|lastIndexOf|startsWith|endsWith)\(",),
        rules=(
            "'hello'.indexOf('l') is 2, the first place; it is -1 when the text is not there.",
            "contains, startsWith and endsWith give true or false.",
            "All of them are case-sensitive: 'Hello'.contains('h') is false.",
        ),
        example="""
            var s = 'hello';
            print(s.indexOf('l'));
            print(s.indexOf('z'));
            print(s.contains('ell'));
            print(s.startsWith('he') && s.endsWith('lo'));
            print(s.contains('H'));
        """,
        out="2\n-1\ntrue\ntrue\nfalse",
    ),
    *dart(
        "split",
        "split",
        "text.split(separator) cuts a string at each separator and gives a list of the pieces.",
        see=("join", "string", "regexp"),
        priority=45,
        aka=("splits", "tokenize", "cut a string", "split by"),
        detect=(r"\.split\s*\(",),
        rules=(
            "'a,b,c'.split(',') is [a, b, c]; 'a,,b'.split(',') keeps the empty piece: [a, , b].",
            "split('') cuts into single characters.",
            "To split on any whitespace: text.split(RegExp(r'\\s+')) (trim first).",
        ),
        example="""
            print('a,b,c'.split(','));
            print('a,,b'.split(','));
            print('abc'.split(''));
            print('  x   y '.trim().split(RegExp(r'\\s+')));
        """,
        out="[a, b, c]\n[a, , b]\n[a, b, c]\n[x, y]",
    ),
    *dart(
        "join",
        "join",
        "list.join(glue) puts the items of a list into one string, with the glue between them.",
        see=("split", "string-buffer", "iterable"),
        priority=45,
        aka=("joins", "concatenate", "glue", "concat", "stitch together"),
        detect=(r"\.join\s*\(",),
        rules=(
            "['a', 'b'].join('-') is 'a-b'; join() with nothing glues with no gap.",
            "Items that are not strings are turned into text first: [1, 2].join('+') is '1+2'.",
            "Works on any Iterable: xs.map(f).join(', ').",
        ),
        example="""
            print(['a', 'b', 'c'].join('-'));
            print([1, 2, 3].join());
            print([1, 2, 3].map((n) => n * n).join(' + '));
        """,
        out="a-b-c\n123\n1 + 4 + 9",
    ),
    *dart(
        "padding",
        "Padding",
        "Extra filler added around something. For text, padLeft and padRight add characters to reach a width. In Flutter, the Padding widget adds empty space around a widget.",
        see=("string", "format", "layout"),
        priority=40,
        aka=("pad", "padleft", "padright", "pad left", "pad right", "zero pad", "pad a string", "padding widget", "edgeinsets"),
        detect=(r"\.pad(?:Left|Right)\s*\(", r"\bPadding\s*\(|\bEdgeInsets\b"),
        rules=(
            "'7'.padLeft(3, '0') is '007'; 'ab'.padRight(4, '.') is 'ab..'.",
            "If the text is already as wide, nothing is added. The default filler is a space.",
            "Flutter: Padding(padding: EdgeInsets.all(8), child: x) makes x 16 wider and 16 taller than it would be (8 on every side).",
        ),
        example="""
            print('7'.padLeft(3, '0'));
            print('ab'.padRight(4, '.') + '|');
            print('abcd'.padLeft(2));
        """,
        out="007\nab..|\nabcd",
    ),
    *dart(
        "replace",
        "replace",
        "replaceAll(from, to) gives a new string with every match of from changed to to; replaceFirst changes only the first.",
        see=("regexp", "string", "string-search"),
        priority=45,
        aka=("replaceall", "replacefirst", "substitute", "swap text", "replace text"),
        detect=(r"\.replace(?:All|First|AllMapped|Range)\s*\(",),
        rules=(
            "Strings cannot change, so the original is untouched and a new string comes back.",
            "'aaa'.replaceAll('a', 'b') is 'bbb'; 'aaa'.replaceFirst('a', 'b') is 'baa'.",
            "from can be a RegExp: 'a1b2'.replaceAll(RegExp(r'\\d'), '#') is 'a#b#'.",
        ),
        example="""
            var s = 'banana';
            print(s.replaceAll('a', 'o'));
            print(s.replaceFirst('a', 'o'));
            print(s);
        """,
        out="bonono\nbonana\nbanana",
    ),
    *dart(
        "letter-case",
        "Letter case",
        "toUpperCase() and toLowerCase() change the case of every letter. Dart has no built-in 'capitalize'.",
        see=("string", "string-comparison", "character"),
        priority=40,
        aka=("uppercase", "lowercase", "touppercase", "tolowercase", "capitalize", "title case", "upper", "lower", "case insensitive"),
        detect=(r"\.to(?:Upper|Lower)Case\s*\(",),
        rules=(
            "They return a new string; the original does not change.",
            "To capitalise the first letter: s[0].toUpperCase() + s.substring(1) (check s is not empty first).",
            "For a case-insensitive comparison, lower both sides first.",
        ),
        example="""
            var s = 'dart';
            print(s.toUpperCase());
            print(s[0].toUpperCase() + s.substring(1));
            print('Dart'.toLowerCase() == 'DART'.toLowerCase());
        """,
        out="DART\nDart\ntrue",
    ),
    *dart(
        "format",
        "Formatting values as text",
        "Making a value look the way you want: fixed decimals with toStringAsFixed, a width with padLeft, or a whole line with interpolation.",
        see=("float-precision", "padding", "string-interpolation"),
        priority=40,
        aka=("formatting", "number formatting", "display", "printf", "string format", "tostringasfixed", "toStringAsPrecision"),
        detect=(r"\.toStringAs(?:Fixed|Precision|Exponential)\s*\(",),
        rules=(
            "3.14159.toStringAsFixed(2) is '3.14'; 5.toStringAsFixed(1) is '5.0'.",
            "For a table column: value.toString().padLeft(6).",
            "Dart has no printf; the intl package adds number and date formats.",
        ),
        example="""
            var price = 4.5;
            print('Total: ${price.toStringAsFixed(2)}');
            print('x'.padLeft(4) + '|');
            print(1234.5678.toStringAsFixed(1));
        """,
        out="Total: 4.50\n   x|\n1234.6",
    ),
    *dart(
        "string-comparison",
        "String comparison",
        "Strings are compared with == for equality and compareTo for order. Order goes by the character codes, so capital letters come before lowercase ones.",
        see=("equality", "letter-case", "sorting"),
        priority=40,
        aka=("compare strings", "string equality", "lexicographic", "alphabetical order", "compareto", "dictionary order", "alphabetical"),
        detect=(r"\.compareTo\s*\(",),
        rules=(
            "a.compareTo(b) is negative if a comes first, 0 if equal, positive if b comes first (only the sign is promised).",
            "'Z'.compareTo('a') is negative: 'Z' is code 90, 'a' is 97.",
            "'apple' < 'banana' does not compile; use compareTo.",
        ),
        example="""
            print('a'.compareTo('b') < 0);
            print('Z'.compareTo('a') < 0);
            print('abc'.compareTo('abc'));
            print(['b', 'B', 'a']..sort());
        """,
        out="true\ntrue\n0\n[B, a, b]",
    ),
    # ── Collections: methods and the words around them ──────────────────
    *dart(
        "iterable",
        "Iterable",
        "Anything you can go through one item at a time. Lists and sets are Iterables, and so is what map and where give back.",
        see=("lazy", "map", "list"),
        priority=55,
        aka=("iterables", "iterator", "sequence", "iterate", "collection", "traversable"),
        detect=(r"\bIterable\b",),
        rules=(
            "for (final x in iterable) { ... } goes through all the items.",
            "Printing a map/where result shows round brackets: (2, 4). Add .toList() to get [2, 4].",
            "Common methods: map, where, fold, reduce, any, every, first, last, length, contains, take, skip, toList.",
        ),
        example="""
            var it = [1, 2, 3].map((x) => x * 2);
            print(it);
            print(it.toList());
            print(it.contains(4));
            print({1, 2}.length);
        """,
        out="(2, 4, 6)\n[2, 4, 6]\ntrue\n2",
    ),
    *dart(
        "lazy",
        "Lazy evaluation",
        "Not doing work until the result is needed. map and where on a list do nothing until you read the results.",
        see=("iterable", "generator", "map"),
        priority=50,
        aka=("lazy iterable", "lazily", "deferred", "on demand", "lazy sequence"),
        rules=(
            "xs.map(f) only builds a recipe; f runs when the result is read (first, toList, a for loop...).",
            "Reading it again runs f again: every read recomputes (call toList() once to keep the results).",
            "Hence side effects inside map callbacks happen late, or more than once.",
        ),
        example="""
            var calls = 0;
            var squares = [1, 2, 3].map((n) {
              calls++;
              return n * n;
            });
            print(calls);
            print(squares.first);
            print(calls);
            squares.toList();
            print(calls);
        """,
        out="0\n1\n1\n4",
    ),
    *dart(
        "map",
        "map",
        "iterable.map(f) gives a new sequence where each item is replaced by f(item). It is lazy: call toList() to get a list.",
        see=("filter", "reduce", "lazy"),
        priority=45,
        aka=("map method", "map function", "transform", "mapping", "map over a list", ".map"),
        detect=(r"\.map\s*[(<]",),
        rules=(
            "[1, 2, 3].map((n) => n * 2) is the sequence (2, 4, 6), shown in round brackets.",
            "The result has the same number of items as the input.",
            "Don't confuse it with the Map type (key-value pairs).",
        ),
        example="""
            var names = ['ann', 'bo'];
            print(names.map((s) => s.toUpperCase()).toList());
            print(names.map((s) => s.length));
        """,
        out="[ANN, BO]\n(3, 2)",
    ),
    *dart(
        "filter",
        "where (filter)",
        "iterable.where(test) keeps only the items for which test returns true. Dart calls filtering where.",
        see=("map", "reduce", "iterable"),
        priority=45,
        aka=("where", "filtering", "filter function", "keep", "select", "whereType", "takewhile", "removewhere", "retainwhere"),
        detect=(r"\.where\s*[(<]|\.whereType\s*<",),
        rules=(
            "[1, 2, 3, 4].where((n) => n.isEven) is (2, 4).",
            "Like map it is lazy and gives an Iterable: add .toList().",
            "xs.removeWhere(test) changes the list in place; where makes a new sequence.",
            "xs.whereType<int>() keeps only the items of one type.",
        ),
        example="""
            var xs = [1, 2, 3, 4, 5];
            print(xs.where((n) => n.isOdd).toList());
            print(xs.where((n) => n > 9).isEmpty);
            print(<Object>[1, 'a', 2].whereType<int>().toList());
        """,
        out="[1, 3, 5]\ntrue\n[1, 2]",
    ),
    *dart(
        "reduce",
        "fold and reduce",
        "Both squash a whole sequence into one value by combining items two at a time. fold starts from a value you give; reduce starts from the first item.",
        see=("accumulator", "sum", "map"),
        priority=50,
        aka=("fold", "reducer", "reduce method", "aggregate", "accumulate", "combine"),
        detect=(r"\.(?:fold|reduce)\s*[(<]",),
        rules=(
            "[1, 2, 3].fold(10, (a, b) => a + b) is 16; [1, 2, 3].reduce((a, b) => a + b) is 6.",
            "reduce on an empty list throws a StateError; fold just returns the start value.",
            "fold can change the type: fold<String>('', (s, n) => s + n.toString()).",
            "If Dart can't work out the type, write it: fold<int>(0, ...).",
        ),
        example="""
            var xs = [1, 2, 3];
            print(xs.fold<int>(10, (a, b) => a + b));
            print(xs.reduce((a, b) => a * b));
            print(<int>[].fold<int>(7, (a, b) => a + b));
            print(xs.fold<String>('', (s, n) => s + n.toString()));
        """,
        out="16\n6\n7\n123",
    ),
    *dart(
        "sum",
        "Sum",
        "Adding up all the numbers in a collection. Dart has no sum() built in: use fold or reduce.",
        see=("reduce", "accumulator", "iterable"),
        priority=40,
        aka=("add up", "sum of", "summation", "average", "mean"),
        rules=(
            "xs.fold<int>(0, (a, b) => a + b) is the sum, and 0 for an empty list.",
            "For doubles start from 0.0 (xs.fold<double>(0.0, ...)).",
            "The average is the sum divided by xs.length (and xs.length can be 0).",
        ),
        example="""
            var xs = [4, 5, 6];
            var total = xs.fold<int>(0, (a, b) => a + b);
            print(total);
            print(total / xs.length);
        """,
        out="15\n5.0",
    ),
    *dart(
        "sorting",
        "Sorting",
        "Putting items in order. list.sort() sorts the list itself (and returns nothing); sort(compare) uses your own rule.",
        see=("comparator", "reverse", "string-comparison"),
        priority=45,
        aka=("sort", "sorted", "ascending", "descending", "sort a list", "sorting a list", "sort list", "orderby"),
        detect=(r"\.sort\s*\(",),
        rules=(
            "xs.sort() changes xs in place and returns void: print(xs.sort()) does not compile.",
            "To keep the original: var copy = [...xs]..sort();",
            "Numbers sort by value, strings by character code ('B' before 'a').",
            "The sort is not guaranteed to keep equal items in their old order.",
        ),
        example="""
            var xs = [3, 1, 2];
            xs.sort();
            print(xs);
            var words = ['pear', 'fig', 'apple'];
            var sorted = [...words]..sort();
            print(sorted);
            print(words);
        """,
        out="[1, 2, 3]\n[apple, fig, pear]\n[pear, fig, apple]",
    ),
    *dart(
        "comparator",
        "Comparator (compare function)",
        "A function that takes two items and says which comes first: a negative number, 0, or a positive number. sort uses it.",
        see=("sorting", "string-comparison", "anonymous-function"),
        priority=45,
        aka=("compare function", "key-function", "key function", "custom sort", "sort by", "sort key", "compareto"),
        rules=(
            "(a, b) => a.length - b.length puts shorter words first.",
            "(a, b) => b.compareTo(a) sorts from largest to smallest (swap a and b to reverse).",
            "To sort by several things, compare the first and fall back to the next when it returns 0.",
        ),
        example="""
            var words = ['pear', 'fig', 'apple', 'kiwi'];
            words.sort((a, b) {
              var c = a.length - b.length;
              return c != 0 ? c : a.compareTo(b);
            });
            print(words);
            words.sort((a, b) => b.compareTo(a));
            print(words);
        """,
        out="[fig, kiwi, pear, apple]\n[pear, kiwi, fig, apple]",
    ),
    *dart(
        "reverse",
        "Reversing",
        "xs.reversed gives the items back to front, as a lazy Iterable (use .toList() for a list). Strings have no reverse; go through a list of characters.",
        see=("sorting", "iterable", "lazy"),
        priority=40,
        aka=("reversed", "backwards", "backward", "reverse a string", "reverse order"),
        detect=(r"\.reversed\b",),
        rules=(
            "[1, 2, 3].reversed prints as (3, 2, 1); it does not change the list.",
            "Reverse a string: s.split('').reversed.join().",
            "For a sort from largest to smallest, sort with a flipped comparator.",
        ),
        example="""
            var xs = [1, 2, 3];
            print(xs.reversed);
            print(xs.reversed.toList());
            print(xs);
            print('stressed'.split('').reversed.join());
        """,
        out="(3, 2, 1)\n[3, 2, 1]\n[1, 2, 3]\ndesserts",
    ),
    *dart(
        "to-list",
        "toList",
        "Turns any Iterable (the result of map, where, a Set...) into a real List you can print, index and change.",
        see=("iterable", "lazy", "map"),
        priority=50,
        aka=("toset", "convert to list", "list.of", "list.from"),
        detect=(r"\.toList\s*\(|\.toSet\s*\(",),
        rules=(
            "It does the waiting work now: the callbacks of map and where run once, while the list is built.",
            "toList() makes a growable list unless you say toList(growable: false).",
            "toSet() makes a Set, which also removes duplicates.",
        ),
        example="""
            var xs = [3, 1, 3];
            print(xs.map((n) => n + 1).toList());
            print(xs.toSet());
            print(xs.toSet().toList());
        """,
        out="[4, 2, 4]\n{3, 1}\n[3, 1]",
    ),
    # ── Libraries ───────────────────────────────────────────────────────
    *dart(
        "import",
        "import (libraries)",
        "import 'dart:math'; brings in code from another library: one of Dart's own (dart:math, dart:async, dart:convert), a package, or one of your files.",
        see=("main-function", "private-member", "future"),
        priority=50,
        aka=("imports", "library", "libraries", "package", "dart:core", "dart:math", "dart:async", "dart:convert", "dart:io", "module", "export", "as prefix", "show", "hide"),
        detect=(r"^\s*import\s+['\"]",),
        rules=(
            "dart:core (String, List, print, int...) is imported for you; others need an import line.",
            "import 'dart:math' as math; then math.max(2, 3) keeps names apart; show and hide pick names.",
            "Imports go at the top of the file, before any other code.",
            "package:flutter/material.dart brings in Flutter's widgets.",
        ),
        example="""
            import 'dart:math' as math;
            void main() {
              print(math.max(3, 8));
              print(math.sqrt(16));
              print(math.pi > 3.14);
            }
        """,
        out="8\n4.0\ntrue",
    ),
]
