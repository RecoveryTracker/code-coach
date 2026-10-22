"""Words the Brain Drills function, scope and loop packs teach: default and keyword arguments, mutable defaults, side
effects, the call stack, late binding, block scope, shadowing, loop variables, nested loops, termination, for-else,
counters, flags and control flow."""

from __future__ import annotations

from .entry import Entry, both, js, py

TERMS: list[Entry] = [
    *both(
        "default-parameter",
        "Default parameter",
        "A parameter that already has a value, used when the caller leaves that argument out.",
        see=("parameter", "argument", "default-value"),
        priority=45,
        aka=("default argument", "default parameters", "optional parameter", "default arguments"),
        python=dict(
            see=("parameter", "argument", "default-value", "mutable-default"),
            rules=(
                "def greet(name, greeting='Hello') - leave greeting out and it is 'Hello'.",
                "Parameters with defaults must come after the ones without.",
                "The default is worked out ONCE, when def runs, not on every call. That is harmless for numbers and text and a trap for lists.",
            ),
            detect=(r"\bdef\s+\w+\s*\([^)]*\w\s*=[^=][^)]*\)",),
            example="""
                def greet(name, greeting="Hello"):
                    return greeting + ", " + name
                print(greet("Ann"), greet("Bo", "Hi"))
            """,
            out="Hello, Ann Hi, Bo",
        ),
        javascript=dict(
            see=("parameter", "argument", "default-value"),
            rules=(
                "function greet(name, greeting = 'Hello') - leave greeting out and it is 'Hello'.",
                "The default is worked out on every call, so a default like [] is a fresh array each time.",
                "Only undefined triggers the default: passing undefined uses it, passing null does not.",
            ),
            detect=(
                r"\bfunction\b[^(\n]*\([^()\n]*\b[\w$]+\s*=[^=>][^()\n]*\)",
                r"\([^()\n]*\b[\w$]+\s*=[^=>][^()\n]*\)\s*=>",
                r"^\s*(?:async\s+|static\s+)*(?!(?:if|while|for|switch|catch|function)\b)[\w$]+\s*\([^()\n]*\b[\w$]+\s*=[^=>][^()\n]*\)\s*\{",
            ),
            example="""
                const greet = (name, greeting = "Hello") => greeting + ", " + name;
                console.log(greet("Ann"), greet("Bo", "Hi"), greet("Cy", undefined), greet("Di", null));
            """,
            out="Hello, Ann Hi, Bo Hello, Cy null, Di",
        ),
    ),
    *py(
        "mutable-default",
        "Mutable default argument",
        "A default like [] or {} is made once, when the function is defined, so every call that uses it shares the same list.",
        see=("default-parameter", "mutable", "reference"),
        priority=70,
        aka=("mutable default argument", "default list", "shared default"),
        detect=(r"\bdef\s+\w+\s*\([^)]*=\s*(?:\[\s*\]|\{\s*\}|set\(\s*\)|list\(\s*\)|dict\(\s*\))",),
        rules=(
            "def add(x, items=[]) keeps adding to the SAME list across calls that do not pass their own.",
            "The usual fix: items=None, then 'if items is None: items = []' inside the function.",
            "Numbers, text and tuples are safe as defaults because they cannot be changed.",
        ),
        example="""
            def add(x, items=[]):
                items.append(x)
                return items
            print(add(1), add(2))
        """,
        out="[1, 2] [1, 2]",
    ),
    *py(
        "keyword-argument",
        "Keyword argument",
        "An argument passed by name, such as f(w=5), instead of by position. The order then does not matter.",
        see=("argument", "parameter", "default-parameter", "star-args"),
        priority=50,
        aka=("keyword arguments", "named argument", "named arguments", "kwarg", "by name"),
        detect=(r"(?<!def )(?<![=!<>])\b[A-Za-z_]\w*\s*\(\s*(?:[^()\n]*,\s*)?[A-Za-z_]\w*\s*=(?!=)[^()\n]*\)",),
        rules=(
            "area(h=2, w=5) and area(w=5, h=2) are the same call.",
            "Positional arguments must come first: area(3, h=4) is fine, area(w=3, 4) is a SyntaxError.",
            "A name the function does not have is a TypeError, as is giving the same parameter twice.",
            "print(..., sep=' ', end='\\n') takes its options this way.",
        ),
        example="""
            def area(w, h):
                return w * h
            print(area(h=2, w=5), area(3, h=4), sep=" / ")
        """,
        out="10 / 12",
    ),
    *js(
        "options-object",
        "Options object (named arguments)",
        "JavaScript has no keyword arguments, so a function takes one object and picks the values out by name.",
        see=("unpacking", "default-parameter", "object", "parameter"),
        priority=45,
        aka=("keyword argument", "keyword arguments", "named argument", "named arguments", "named parameters", "options"),
        detect=(r"\(\s*\{\s*[\w$]+(?:\s*=[^,}]+)?(?:\s*,\s*[\w$]+(?:\s*=[^,}]+)?)*\s*\}\s*\)\s*(?:=>|\{)",),
        rules=(
            "function area({ w, h = 1 }) takes the values out of the object it is given.",
            "The call names them, in any order: area({ h: 2, w: 5 }) and area({ w: 5, h: 2 }) are the same.",
            "A name that is left out is undefined, or its default if it has one.",
        ),
        example="""
            const area = ({ w, h = 1 }) => w * h;
            console.log(area({ w: 5, h: 2 }), area({ h: 3, w: 2 }), area({ w: 4 }));
        """,
        out="10 6 4",
    ),
    *both(
        "side-effect",
        "Side effect",
        "Anything a function does besides giving back a value: printing, changing a list it was given, changing a variable outside itself.",
        see=("function", "return", "mutable"),
        priority=50,
        aka=("side effects", "pure function", "impure", "pure"),
        python=dict(
            rules=(
                "A function with no side effects and the same answer for the same arguments is called pure.",
                "Changing a list or dict you were passed (items.append(x)) is a side effect the caller can see.",
                "A side effect only happens if the code runs: 'False and f()' never calls f, so f's side effects never happen.",
            ),
            example="""
                log = []
                def add(a, b):
                    log.append("called")
                    return a + b
                print(add(1, 2), log)
            """,
            out="3 ['called']",
        ),
        javascript=dict(
            rules=(
                "A function with no side effects and the same answer for the same arguments is called pure.",
                "Changing an array or object you were passed (items.push(x)) is a side effect the caller can see.",
                "A side effect only happens if the code runs: 'false && f()' never calls f, so f's side effects never happen.",
            ),
            example="""
                const log = [];
                function add(a, b) {
                  log.push("called");
                  return a + b;
                }
                console.log(add(1, 2), log);
            """,
            out="3 [ 'called' ]",
        ),
    ),
    *both(
        "call-stack",
        "Call stack",
        "The list of functions that are running right now, each waiting for the one it called. When a function returns, it is taken off the top.",
        see=("recursion", "function", "return", "traceback"),
        priority=55,
        aka=("stack", "stack frame", "stack overflow", "recursion limit", "call stack"),
        python=dict(
            see=("recursion", "function", "return", "traceback"),
            rules=(
                "Every call adds a frame; a recursive function with no base case keeps adding until Python raises a RecursionError (the limit is 1000 deep by default).",
                "A traceback is a print-out of the call stack at the moment of an error, oldest call first.",
                "The innermost call finishes first: the last function called is the first to return.",
            ),
            example="""
                def depth(n):
                    return 0 if n == 0 else 1 + depth(n - 1)
                def forever():
                    forever()
                print(depth(5))
                try:
                    forever()
                except RecursionError as e:
                    print(type(e).__name__)
            """,
            out="5\nRecursionError",
        ),
        javascript=dict(
            see=("recursion", "function", "return", "traceback", "event-loop"),
            rules=(
                "Every call adds a frame; a recursive function with no base case keeps adding until JavaScript throws a RangeError ('Maximum call stack size exceeded').",
                "An error's stack property is a print-out of the call stack at the moment of the error, newest call first.",
                "The innermost call finishes first: the last function called is the first to return.",
            ),
            example="""
                function depth(n) {
                  return n === 0 ? 0 : 1 + depth(n - 1);
                }
                console.log(depth(5));
                try {
                  (function forever() { forever(); })();
                } catch (e) {
                  console.log(e.name + ": " + e.message);
                }
            """,
            out="5\nRangeError: Maximum call stack size exceeded",
        ),
    ),
    *both(
        "late-binding",
        "Late binding in closures",
        "A function made inside a loop remembers the variable, not the value it had at the time, so it sees the value the variable has when the function is finally called.",
        see=("closure", "scope", "loop-variable"),
        priority=60,
        aka=("late binding", "closure in a loop", "loop closure", "closures in loops"),
        python=dict(
            detect=(r"\[\s*lambda\b[^\]\n]*\bfor\b", r"\blambda\s+(\w+)\s*=\s*\1\s*:"),
            rules=(
                "[lambda: i for i in range(3)] makes three functions that all read the same i, which ends as 2: they all give 2.",
                "To capture the value now, make it a default: lambda i=i: i.",
                "The same happens with def inside a loop.",
            ),
            example="""
                fns = [lambda: i for i in range(3)]
                print([f() for f in fns])
                fixed = [lambda i=i: i for i in range(3)]
                print([f() for f in fixed])
            """,
            out="[2, 2, 2]\n[0, 1, 2]",
        ),
        javascript=dict(
            detect=(r"\bfor\s*\(\s*var\b[^{\n]*\{[^}]*(?:=>|\bfunction\b)",),
            rules=(
                "With var there is one i for the whole loop, so every function made in it sees its final value.",
                "With let in the loop header, each pass gets its own fresh i, so each function keeps its own value.",
                "That is why let (or const) is preferred over var.",
            ),
            example="""
                const a = [], b = [];
                for (var i = 0; i < 3; i++) a.push(() => i);
                for (let j = 0; j < 3; j++) b.push(() => j);
                console.log(a.map((f) => f()), b.map((f) => f()));
            """,
            out="[ 3, 3, 3 ] [ 0, 1, 2 ]",
        ),
    ),
    *both(
        "block-scope",
        "Block scope",
        "Whether a name made inside a pair of curly braces or an indented block stops existing when the block ends.",
        priority=60,
        aka=("block scoped", "block-scoped", "block scoping", "function scope", "scope of a block"),
        python=dict(
            see=("scope", "loop-variable", "shadowing"),
            rules=(
                "Python has NO block scope: names made inside an if, for or while block are still there after it.",
                "Only a function (and a class, module, or comprehension) has its own scope.",
                "A comprehension's variable stays inside the comprehension: after [j for j in range(2)], j is a NameError.",
            ),
            example="""
                for i in range(3):
                    sq = i * i
                print(i, sq)
            """,
            out="2 4",
        ),
        javascript=dict(
            see=("scope", "let-const-var", "shadowing", "hoisting"),
            rules=(
                "let and const belong to the nearest pair of braces and are gone after the closing brace.",
                "var ignores blocks: it belongs to the whole function, so it is still there after the braces.",
                "That is why a loop's let i is not visible after the loop, but a var i is.",
            ),
            example="""
                {
                  let a = 1;
                  var b = 2;
                }
                console.log(typeof a, b);
            """,
            out="undefined 2",
        ),
    ),
    *both(
        "shadowing",
        "Shadowing",
        "Making a new name that hides another name of the same spelling from an outer scope. The outer one is not changed; it is just out of sight.",
        see=("scope", "local", "global"),
        priority=55,
        aka=("shadow", "shadowed", "hides", "name hiding"),
        python=dict(
            rules=(
                "Assigning to a name inside a function makes a new local that hides a global of the same name.",
                "The global keeps its value: after the function, the outer name is as it was.",
                "On an object, assigning self.n = 5 makes an instance attribute that hides the class attribute n for that object only.",
            ),
            example="""
                x = 1
                def f():
                    x = 2
                    return x
                print(f(), x)
            """,
            out="2 1",
        ),
        javascript=dict(
            rules=(
                "A let or const inside a function or block hides an outer name of the same spelling for that block.",
                "The outer variable keeps its value: after the block, the outer name is as it was.",
                "An object's own property hides a property of the same name further along its prototype chain.",
            ),
            example="""
                let x = 1;
                function f() {
                  const x = 2;
                  return x;
                }
                console.log(f(), x);
            """,
            out="2 1",
        ),
    ),
    *both(
        "loop-variable",
        "Loop variable",
        "The variable a for loop sets to each item in turn: the i in 'for i in ...'.",
        see=("loop", "scope", "block-scope"),
        priority=45,
        aka=("loop variables", "loop counter", "loop index", "iteration variable", "loop var"),
        python=dict(
            rules=(
                "It is a normal variable: it is still there after the loop, holding the LAST item.",
                "If the loop never runs (an empty list), the variable is never made at all.",
                "Changing it inside the body does not change the loop: the next pass sets it again.",
            ),
            example="""
                for i in range(3):
                    pass
                print(i)
                for k in []:
                    pass
                try:
                    print(k)
                except NameError:
                    print("no k")
            """,
            out="2\nno k",
        ),
        javascript=dict(
            rules=(
                "With let or const in the loop header, the variable exists only inside the loop.",
                "With var it leaks out, and holds the value that ended the loop (3 after for (var k = 0; k < 3; k++)).",
                "Changing it inside the body changes the loop, for a counting loop: i++ in the body skips a pass.",
            ),
            example="""
                for (let i = 0; i < 3; i++) {}
                for (var k = 0; k < 3; k++) {}
                console.log(typeof i, k);
            """,
            out="undefined 3",
        ),
    ),
    *both(
        "nested-loop",
        "Nested loop",
        "A loop inside another loop. The inner one runs completely, from start to finish, for every single pass of the outer one.",
        see=("loop", "nesting", "break-continue"),
        priority=60,
        aka=("nested loops", "loop in a loop", "inner loop", "outer loop", "double loop"),
        python=dict(
            rules=(
                "Passes: outer passes times inner passes, so range(3) outside and range(2) inside is 6 passes of the inner body.",
                "The inner variable starts again on every outer pass.",
                "break leaves only the inner loop; the outer loop carries on.",
            ),
            detect=(r"^[ \t]*for\b[^\n]*:[ \t]*\n(?:[ \t]+\S[^\n]*\n)*?[ \t]+for\b",),
            example="""
                rows = []
                for i in range(2):
                    for j in range(3):
                        rows.append(f"{i}{j}")
                print(" ".join(rows))
            """,
            out="00 01 02 10 11 12",
        ),
        javascript=dict(
            rules=(
                "Passes: outer passes times inner passes, so 3 outside and 2 inside is 6 passes of the inner body.",
                "The inner variable starts again on every outer pass.",
                "break leaves only the inner loop; the outer loop carries on.",
            ),
            detect=(r"\bfor\s*\([^\n]*\{[^\n]*\n(?:[^\n]*\n)*?[^\n]*\bfor\s*\(",),
            example="""
                const rows = [];
                for (let i = 0; i < 2; i++) {
                  for (let j = 0; j < 3; j++) {
                    rows.push(`${i}${j}`);
                  }
                }
                console.log(rows.join(" "));
            """,
            out="00 01 02 10 11 12",
        ),
    ),
    *both(
        "termination",
        "Termination",
        "A loop terminates when it eventually stops. A while loop only does if something inside it moves the condition toward false.",
        see=("while-loop", "condition", "loop"),
        priority=50,
        aka=("terminate", "terminates", "infinite loop", "stop condition", "stopping condition", "forever", "never ends"),
        python=dict(
            rules=(
                "A for loop over a list or range always terminates, because the collection runs out.",
                "A while loop needs its condition to change: 'while n > 1' must change n, or it never ends.",
                "'while True:' is meant to run until a break (or return) inside it.",
            ),
            example="""
                n = 10
                steps = 0
                while n > 1:
                    n //= 2
                    steps += 1
                print(n, steps)
            """,
            out="1 3",
        ),
        javascript=dict(
            rules=(
                "A for...of loop over an array always terminates, because the array runs out.",
                "A while loop needs its condition to change: 'while (n > 1)' must change n, or it never ends.",
                "'while (true)' is meant to run until a break (or return) inside it.",
            ),
            example="""
                let n = 10;
                let steps = 0;
                while (n > 1) {
                  n = Math.floor(n / 2);
                  steps++;
                }
                console.log(n, steps);
            """,
            out="1 3",
        ),
    ),
    *py(
        "for-else",
        "for ... else",
        "An else on a loop. Its block runs when the loop finished normally, without hitting a break.",
        see=("for-loop", "break-continue", "branch"),
        priority=60,
        aka=("loop else", "while else", "else on a loop", "for/else", "for else"),
        detect=(r"^[ \t]*else\s*:",),
        rules=(
            "The else runs when the loop ends because it ran out of items, and is skipped if a break ended it.",
            "So it answers 'did the loop finish without finding what it was looking for?'.",
            "It does NOT mean 'else, when the loop did not run': an empty loop still runs the else.",
        ),
        example="""
            for n in [1, 3, 5]:
                if n % 2 == 0:
                    print("even found")
                    break
            else:
                print("no even")
            for n in [1, 2, 5]:
                if n % 2 == 0:
                    print("even found")
                    break
            else:
                print("no even")
        """,
        out="no even\neven found",
    ),
    *both(
        "counter",
        "Counter",
        "A variable that counts how many times something happened: it starts at 0 and goes up by 1 each time.",
        see=("accumulator", "augmented-assignment", "loop"),
        priority=45,
        aka=("counting", "count", "tally", "counters"),
        python=dict(
            rules=(
                "count = 0 before the loop, count += 1 inside an if, and the answer is count after the loop.",
                "To count each kind separately use a dict: counts[ch] = counts.get(ch, 0) + 1.",
                "The standard library has collections.Counter for exactly this.",
            ),
            example="""
                count = 0
                counts = {}
                for ch in "banana":
                    if ch == "a":
                        count += 1
                    counts[ch] = counts.get(ch, 0) + 1
                print(count, counts)
            """,
            out="3 {'b': 1, 'a': 3, 'n': 2}",
        ),
        javascript=dict(
            rules=(
                "let count = 0 before the loop, count++ inside an if, and the answer is count after the loop.",
                "To count each kind separately use an object: counts[ch] = (counts[ch] ?? 0) + 1.",
                "A Map works too, and keeps its keys in the order they were first seen.",
            ),
            example="""
                let count = 0;
                const counts = {};
                for (const ch of "banana") {
                  if (ch === "a") count++;
                  counts[ch] = (counts[ch] ?? 0) + 1;
                }
                console.log(count, counts);
            """,
            out="3 { b: 1, a: 3, n: 2 }",
        ),
    ),
    *both(
        "flag",
        "Flag",
        "A true-or-false variable that remembers whether something has happened yet, so code after a loop can act on it.",
        see=("boolean", "loop", "break-continue"),
        priority=40,
        aka=("flags", "boolean flag", "found flag", "sentinel"),
        python=dict(
            rules=(
                "Set it to False before the loop, to True inside the loop when the thing happens, and read it after.",
                "Set it to False INSIDE the loop and it is reset on every pass; it must be set once, before the loop.",
                "for ... else does the same job without a flag.",
            ),
            example="""
                found = False
                for n in [1, 2, 3]:
                    if n == 2:
                        found = True
                print(found)
            """,
            out="True",
        ),
        javascript=dict(
            rules=(
                "Set it to false before the loop, to true inside the loop when the thing happens, and read it after.",
                "Set it to false INSIDE the loop and it is reset on every pass; it must be set once, before the loop.",
                "Array methods such as includes and some answer the same question without a flag.",
            ),
            example="""
                let found = false;
                for (const n of [1, 2, 3]) {
                  if (n === 2) found = true;
                }
                console.log(found);
            """,
            out="true",
        ),
    ),
    *both(
        "control-flow",
        "Control flow",
        "The order in which a program's lines run. Normally top to bottom; branches, loops, function calls and errors change it.",
        see=("branch", "loop", "break-continue", "exception"),
        priority=50,
        aka=("flow of control", "program flow", "execution order", "order of execution", "jump"),
        python=dict(
            rules=(
                "if/elif/else choose which block runs; for and while repeat a block.",
                "break leaves a loop, continue skips to the next pass, return leaves a function.",
                "An uncaught exception stops the whole flow; try/except catches it and carries on after the except block.",
            ),
            example="""
                for n in range(4):
                    if n == 1:
                        continue
                    if n == 3:
                        break
                    print(n)
            """,
            out="0\n2",
        ),
        javascript=dict(
            rules=(
                "if/else choose which block runs; for and while repeat a block.",
                "break leaves a loop, continue skips to the next pass, return leaves a function.",
                "An uncaught error stops the whole flow; try/catch catches it and carries on after the catch block.",
            ),
            example="""
                for (let n = 0; n < 4; n++) {
                  if (n === 1) continue;
                  if (n === 3) break;
                  console.log(n);
                }
            """,
            out="0\n2",
        ),
    ),
]
