"""Words about how a program decides and repeats: conditions, branches, loops, indexes, errors."""

from __future__ import annotations

from .entry import Entry, both, js, py

TERMS: list[Entry] = [
    *both(
        "condition",
        "Condition",
        "The yes-or-no test an if or a while looks at to decide whether to run its code.",
        see=("truthy", "comparison", "branch"),
        priority=45,
        aka=("conditional", "test"),
        python=dict(
            rules=(
                "Any value works as a condition, not only True and False: it is judged by the truthy and falsy rules.",
                "Use == to compare. A single = is assignment, and 'if x = 3:' is a syntax error.",
                "A while loop re-checks its condition before every pass.",
            ),
            detect=(r"\b(?:if|elif|while)\b",),
            example="""
                n = 3
                if n > 2:
                    print("yes")
            """,
            out="yes",
        ),
        javascript=dict(
            rules=(
                "Any value works as a condition, not only true and false: it is judged by the truthy and falsy rules.",
                "Use === to compare. A single = assigns, and 'if (x = 3)' assigns 3 and then tests it - a classic bug.",
                "A while loop re-checks its condition before every pass.",
            ),
            detect=(r"\b(?:if|while)\s*\(",),
            example="""
                const n = 3;
                if (n > 2) {
                  console.log("yes");
                }
            """,
            out="yes",
        ),
    ),
    *both(
        "comparison",
        "Comparison",
        "Asking how two values relate: equal, different, smaller, larger. The answer is true or false.",
        see=("boolean", "condition", "float-precision"),
        priority=45,
        aka=("compare", "relational operator", "less than", "greater than", "<", ">", "<=", ">="),
        python=dict(
            rules=(
                "The comparisons are == != < > <= >=.",
                "They can be chained: 1 < x < 5 means 1 < x and x < 5.",
                "Strings compare character by character, capitals before lowercase: 'Z' < 'a' is True.",
                "Comparing unlike types with < (such as 'a' < 1) is a TypeError.",
            ),
            detect=(r"[\w)\]\"']\s*(?:==|!=|<=|>=|<|>)\s*[\w(\[\"'\-]",),
            example="""
                x = 3
                print(x > 2, x == 3, 1 < x < 5, "Z" < "a")
            """,
            out="True True True True",
        ),
        javascript=dict(
            rules=(
                "The comparisons are === !== < > <= >= (and the looser == and !=).",
                "Strings compare as text: '10' < '9' is true. If one side is a number, the other becomes a number: '10' < 9 is false.",
                "They cannot be chained: 1 < 5 < 3 is true, because 1 < 5 is true, and true counts as 1, which is < 3.",
            ),
            detect=(r"[\w)\]\"'`]\s*(?:===|!==|==|!=|<=|>=|<|>)\s*[\w(\[\"'`\-]",),
            example="""
                console.log(3 > 2, "10" < "9", "10" < 9, 1 < 5 < 3);
            """,
            out="true true false true",
        ),
    ),
    *both(
        "short-circuit",
        "Short-circuit",
        "How and / or (&& and || in JavaScript) stop as soon as the answer is known, and hand back one of the actual values, "
        "not just true or false.",
        see=("truthy", "falsy", "boolean", "condition"),
        priority=80,
        aka=("short circuit", "short-circuiting", "shortcircuit", "and", "or", "&&", "||", "lazy evaluation"),
        python=dict(
            rules=(
                "a or b gives a if a is truthy, otherwise b. So name or 'guest' is a default.",
                "a and b gives a if a is falsy, otherwise b.",
                "The right side is not run at all when the left already decides: x and x.name is safe when x is None.",
                "The result is one of the two values, not necessarily True or False.",
            ),
            detect=(r"\b(?:and|or)\b",),
            example="""
                print("" or "default", 0 and 5, "x" and "y", [] or None)
            """,
            out="default 0 y None",
        ),
        javascript=dict(
            rules=(
                "a || b gives a if a is truthy, otherwise b. So name || 'guest' is a default.",
                "a && b gives a if a is falsy, otherwise b.",
                "a ?? b gives b only when a is null or undefined: 0 ?? 5 is 0, but 0 || 5 is 5.",
                "The right side is not run at all when the left already decides: user && user.name is safe when user is null.",
            ),
            detect=(r"&&|\|\||\?\?",),
            example="""
                console.log("" || "default", 0 && 5, "x" && "y", 0 ?? 5, 0 || 5);
            """,
            out="default 0 y 0 5",
        ),
    ),
    *both(
        "ternary",
        "Conditional expression",
        "A one-line if that picks one of two values: a short way to say 'this value if the test is true, otherwise that one'.",
        see=("condition", "branch", "expression"),
        priority=55,
        aka=("ternary", "ternary operator", "inline if", "conditional operator", "?:"),
        python=dict(
            rules=(
                "The shape is value_if_true if condition else value_if_false.",
                "Only the chosen side is worked out.",
                "It is an expression, so it can sit inside a print, an assignment or a return.",
            ),
            detect=(r"(?m)^(?!\s*(?:if|elif)\b).*\S\s+if\s.+\selse\b",),
            example="""
                age = 20
                print("adult" if age >= 18 else "minor")
            """,
            out="adult",
        ),
        javascript=dict(
            rules=(
                "The shape is condition ? value_if_true : value_if_false.",
                "Only the chosen side is worked out.",
                "It is an expression, so it can sit inside a console.log, an assignment or a return.",
            ),
            detect=(r"[\w$.\])]\s*\?(?![?.])[^:\n]*:",),
            example="""
                const age = 20;
                console.log(age >= 18 ? "adult" : "minor");
            """,
            out="adult",
        ),
    ),
    *both(
        "branch",
        "Branch",
        "One of the different paths a program can take, chosen by an if. Code in a branch runs only when its test passes.",
        see=("condition", "ternary", "indentation"),
        priority=50,
        aka=("if", "else", "elif", "else if", "if statement", "conditional", "if/else"),
        python=dict(
            rules=(
                "if checks first, each elif checks next, and else catches whatever is left (it has no condition).",
                "Only the FIRST branch whose condition is truthy runs; the rest are skipped.",
                "elif and else are optional, and the program carries on below the whole if.",
            ),
            detect=(r"\b(?:if|elif|else)\b",),
            example="""
                n = 7
                if n < 5:
                    print("small")
                elif n < 10:
                    print("medium")
                else:
                    print("large")
            """,
            out="medium",
        ),
        javascript=dict(
            rules=(
                "if checks first, each else if checks next, and else catches whatever is left (it has no condition).",
                "Only the FIRST branch whose condition is truthy runs; the rest are skipped.",
                "switch picks a branch by comparing one value against several cases (with ===); each case needs a break or it falls through.",
            ),
            detect=(r"\b(?:if|else|switch)\b",),
            example="""
                const n = 7;
                if (n < 5) {
                  console.log("small");
                } else if (n < 10) {
                  console.log("medium");
                } else {
                  console.log("large");
                }
            """,
            out="medium",
        ),
    ),
    *both(
        "loop",
        "Loop",
        "Code that repeats. A for loop goes through a set of things, and a while loop goes on as long as a condition holds.",
        see=("iteration", "for-loop", "while-loop", "off-by-one"),
        priority=60,
        aka=("loops", "looping", "repeat"),
        python=dict(
            rules=(
                "for repeats once per item of something; while repeats as long as its condition is truthy.",
                "A while loop whose condition never becomes falsy runs forever (an infinite loop).",
                "break leaves the loop early; continue skips to the next pass.",
            ),
            detect=(r"\b(?:for|while)\b",),
            example="""
                for i in range(3):
                    print(i)
            """,
            out="0\n1\n2",
        ),
        javascript=dict(
            rules=(
                "for (start; test; step) runs while the test is truthy; for...of goes through values; while repeats on a condition.",
                "A loop whose test never becomes falsy runs forever (an infinite loop).",
                "break leaves the loop early; continue skips to the next pass.",
            ),
            detect=(r"\b(?:for|while)\b|\.forEach\(",),
            example="""
                for (let i = 0; i < 3; i++) {
                  console.log(i);
                }
            """,
            out="0\n1\n2",
        ),
    ),
    *both(
        "iteration",
        "Iteration",
        "One pass through the body of a loop. A loop that repeats five times has five iterations.",
        see=("loop", "iterable", "off-by-one"),
        priority=45,
        aka=("iterate", "iterating", "iterations", "pass", "trip"),
        rules=(
            "The loop variable has a new value on each iteration.",
            "Count iterations by listing the values the loop variable takes: 0, 1, 2, 3 is four iterations.",
            "If the condition is false the first time, there are zero iterations and the body never runs.",
        ),
        python=dict(
            detect=(r"\b(?:for|while)\b",),
            example="""
                count = 0
                for i in range(4):
                    count += 1
                print(count)
            """,
            out="4",
        ),
        javascript=dict(
            detect=(r"\b(?:for|while)\b",),
            example="""
                let count = 0;
                for (let i = 0; i < 4; i++) {
                  count++;
                }
                console.log(count);
            """,
            out="4",
        ),
    ),
    *both(
        "iterable",
        "Iterable",
        "Anything a loop can go through one item at a time.",
        see=("loop", "for-loop", "generator"),
        priority=40,
        aka=("iterate over", "iterables"),
        python=dict(
            rules=(
                "Lists, tuples, strings, dicts (their keys), sets, ranges and files are iterable.",
                "A number is not: for x in 5 is a TypeError - use range(5).",
                "list(x) collects any iterable into a list.",
            ),
            detect=(r"\bfor\s+\w+(?:\s*,\s*\w+)*\s+in\b",),
            example="""
                for ch in "abc":
                    print(ch, end="-")
                print()
                print(list(range(3)), list("ab"))
            """,
            out="a-b-c-\n[0, 1, 2] ['a', 'b']",
        ),
        javascript=dict(
            rules=(
                "Arrays, strings, Maps, Sets and generators are iterable: for...of goes through them.",
                "A plain object is not: for (x of {a: 1}) is a TypeError - use Object.keys, Object.values or Object.entries.",
                "[...x] collects any iterable into an array.",
            ),
            detect=(r"\bfor\s*\(\s*(?:const|let|var)\s+[\w$]+\s+of\b",),
            example="""
                let out = "";
                for (const ch of "abc") out += ch + "-";
                console.log(out);
                console.log([..."ab"], Object.keys({ a: 1 }));
            """,
            out="a-b-c-\n[ 'a', 'b' ] [ 'a' ]",
        ),
    ),
    *both(
        "while-loop",
        "While loop",
        "A loop that keeps going as long as its condition is truthy, checked before every pass.",
        see=("loop", "condition", "break-continue"),
        priority=45,
        aka=("while",),
        rules=(
            "If the condition is false at the start, the body never runs.",
            "Something inside the loop must change what the condition sees, or it never stops.",
            "Use while when you do not know in advance how many passes it takes.",
        ),
        python=dict(
            detect=(r"\bwhile\b",),
            example="""
                n = 1
                while n < 20:
                    n *= 2
                print(n)
            """,
            out="32",
        ),
        javascript=dict(
            detect=(r"\bwhile\b",),
            example="""
                let n = 1;
                while (n < 20) {
                  n *= 2;
                }
                console.log(n);
            """,
            out="32",
        ),
    ),
    *both(
        "for-loop",
        "For loop",
        "A loop that goes through a set of things, once each, or counts through a series of numbers.",
        see=("loop", "iterable", "break-continue"),
        priority=45,
        aka=("for", "for each", "foreach"),
        python=dict(
            rules=(
                "for item in things: runs the body once per item, with item set to each in turn.",
                "for i in range(n): counts i = 0, 1, ... n - 1.",
                "enumerate(things) gives index and item together: for i, item in enumerate(things).",
            ),
            detect=(r"\bfor\b",),
            example="""
                total = 0
                for n in [1, 2, 3]:
                    total += n
                print(total)
            """,
            out="6",
        ),
        javascript=dict(
            rules=(
                "for (let i = 0; i < n; i++) is the counting form: start; test before each pass; step after each pass.",
                "for (const x of things) goes through the values; for (const k in obj) goes through the KEYS, which are always strings.",
                "things.forEach(fn) is a method alternative, but break does not work in it.",
            ),
            detect=(r"\bfor\s*\(",),
            example="""
                let total = 0;
                for (const n of [1, 2, 3]) total += n;
                for (const k in ["a", "b"]) console.log(typeof k);
                console.log(total);
            """,
            out="string\nstring\n6",
        ),
    ),
    *both(
        "break-continue",
        "break and continue",
        "break leaves a loop immediately. continue skips the rest of this pass and goes to the next one.",
        see=("loop", "condition"),
        priority=45,
        aka=("break", "continue", "pass"),
        rules=(
            "Both only affect the innermost loop they sit in.",
            "break is for 'I found it, stop looking'; continue is for 'skip this one'.",
        ),
        python=dict(
            detect=(r"\b(?:break|continue)\b",),
            example="""
                for i in range(6):
                    if i == 2:
                        continue
                    if i == 4:
                        break
                    print(i)
            """,
            out="0\n1\n3",
        ),
        javascript=dict(
            detect=(r"\b(?:break|continue)\b",),
            example="""
                for (let i = 0; i < 6; i++) {
                  if (i === 2) continue;
                  if (i === 4) break;
                  console.log(i);
                }
            """,
            out="0\n1\n3",
        ),
    ),
    *both(
        "off-by-one",
        "Off-by-one error",
        "A bug where a count or position is wrong by exactly one: one pass too many, one item missed, one step past the end.",
        see=("index", "loop", "iteration"),
        priority=70,
        aka=("off by one", "fencepost", "fence post", "obo"),
        python=dict(
            rules=(
                "Items are numbered from 0, so a list of 3 has indexes 0, 1, 2 - the last index is len(x) - 1.",
                "range(n) stops BEFORE n, so range(3) gives 0, 1, 2 (three numbers, not four).",
                "< stops before a limit and <= includes it; choosing the wrong one adds or drops a pass.",
            ),
            detect=(
                r"\brange\(\s*len\(",
                r"\blen\([^)]*\)\s*[-+]\s*1\b",
                r"\b(?:for|while)\b[^\n]*<=",
                r"\brange\(",
            ),
            example="""
                items = [10, 20, 30]
                for i in range(len(items) + 1):
                    try:
                        print(items[i])
                    except IndexError:
                        print("one too far")
            """,
            out="10\n20\n30\none too far",
        ),
        javascript=dict(
            rules=(
                "Items are numbered from 0, so an array of 3 has indexes 0, 1, 2 - the last index is length - 1.",
                "i < n stops before n and i <= n includes it; choosing the wrong one adds or drops a pass.",
                "Reading past the end gives undefined instead of an error, so the bug can go unnoticed.",
            ),
            detect=(
                r"<=\s*[\w$.]*\.length\b",
                r"\.length\s*[-+]\s*1\b",
                r"\b(?:for|while)\b[^\n]*<=",
            ),
            example="""
                const items = [10, 20, 30];
                for (let i = 0; i <= items.length; i++) {
                  console.log(items[i]);
                }
            """,
            out="10\n20\n30\nundefined",
        ),
    ),
    *both(
        "index",
        "Index",
        "A number saying which item you want, counted from 0: the first item is index 0, the second is 1.",
        see=("off-by-one", "slice", "string"),
        priority=50,
        aka=("indexes", "indices", "indexing", "subscript"),
        python=dict(
            rules=(
                "Counting starts at 0: items[0] is the first.",
                "Negative numbers count from the end: items[-1] is the last.",
                "An index that does not exist raises IndexError (a missing dict key is a KeyError).",
            ),
            detect=(r"[\w)\]]\[(?:-?\d+|[A-Za-z_]\w*)\]",),
            example="""
                letters = ["a", "b", "c"]
                print(letters[0], letters[-1], len(letters))
            """,
            out="a c 3",
        ),
        javascript=dict(
            rules=(
                "Counting starts at 0: items[0] is the first.",
                "A negative index does not count from the end: items[-1] is undefined. Use items.at(-1).",
                "An index that does not exist gives undefined, not an error.",
            ),
            detect=(r"[\w$)\]]\[(?:-?\d+|[A-Za-z_$][\w$]*)\]", r"\.at\("),
            example="""
                const letters = ["a", "b", "c"];
                console.log(letters[0], letters.at(-1), letters[-1], letters[9]);
            """,
            out="a c undefined undefined",
        ),
    ),
    *both(
        "slice",
        "Slice",
        "A piece cut out of a string or list: from a start position up to, but not including, an end position.",
        see=("index", "string", "off-by-one"),
        priority=60,
        aka=("slicing", "substring"),
        python=dict(
            rules=(
                "x[1:4] gives positions 1, 2 and 3: the start is included and the end is not.",
                "Leave a side out to go to the edge: x[:3] is the first three, x[3:] is the rest, x[-3:] is the last three.",
                "x[::2] takes every second item, and x[::-1] reverses.",
                "A slice never raises an error for going too far; it just stops at the end.",
            ),
            detect=(r"[\w)\]]\[[^\[\]{}\n]*:[^\[\]{}\n]*\]",),
            example="""
                word = "farmland"
                print(word[0:4], word[4:], word[-3:], word[::-1])
            """,
            out="farm land and dnalmraf",
        ),
        javascript=dict(
            rules=(
                "x.slice(1, 4) gives positions 1, 2 and 3: the start is included and the end is not.",
                "Leave the end out to go to the edge: x.slice(3) is the rest, x.slice(-3) is the last three.",
                "slice makes a copy and leaves the original unchanged (splice, by contrast, changes the array).",
            ),
            detect=(r"\.slice\(", r"\.substring\(|\.substr\("),
            example="""
                const word = "farmland";
                console.log(word.slice(0, 4), word.slice(4), word.slice(-3));
            """,
            out="farm land and",
        ),
    ),
    *both(
        "exception",
        "Exception",
        "An error that happens while the program is running. If nothing handles it, the program stops and shows a message.",
        see=("finally", "syntax-error"),
        priority=55,
        aka=("error", "errors", "exceptions", "raise", "throw", "traceback", "crash"),
        python=dict(
            rules=(
                "Common ones: ValueError (right type, wrong value), TypeError, IndexError, KeyError, ZeroDivisionError, NameError.",
                "An unhandled exception prints a traceback: the chain of calls that led to the error, with the error last.",
                "raise ValueError('message') makes one on purpose.",
            ),
            see=("try-except", "finally", "syntax-error"),
            detect=(r"\b(?:raise|except|try)\b", r"\b\w+Error\b"),
            example="""
                try:
                    print(1 / 0)
                except ZeroDivisionError:
                    print("cannot divide by zero")
            """,
            out="cannot divide by zero",
        ),
        javascript=dict(
            rules=(
                "Common ones: TypeError (such as null.name), ReferenceError (a name that does not exist), RangeError, SyntaxError.",
                "An uncaught error stops the script and prints a message with the line.",
                "throw new Error('message') makes one on purpose. Note 1 / 0 is Infinity, not an error.",
            ),
            see=("try-catch", "finally", "syntax-error"),
            detect=(r"\b(?:throw|catch|try)\b", r"\bnew\s+\w*Error\b"),
            example="""
                try {
                  null.name;
                } catch (e) {
                  console.log(e.name, 1 / 0);
                }
            """,
            out="TypeError Infinity",
        ),
    ),
    *both(
        "finally",
        "finally",
        "A block that runs after a try no matter what happened: it finished, it hit an error, or it returned.",
        see=("exception",),
        priority=40,
        aka=("cleanup",),
        rules=(
            "Use it for clean-up that must always happen, such as closing a file.",
            "It runs even when the try block returns early.",
        ),
        python=dict(
            see=("exception", "try-except"),
            detect=(r"\bfinally\b",),
            example="""
                def f():
                    try:
                        return "try"
                    finally:
                        print("cleanup")
                print(f())
            """,
            out="cleanup\ntry",
        ),
        javascript=dict(
            see=("exception", "try-catch"),
            detect=(r"\bfinally\b",),
            example="""
                function f() {
                  try {
                    return "try";
                  } finally {
                    console.log("cleanup");
                  }
                }
                console.log(f());
            """,
            out="cleanup\ntry",
        ),
    ),
    *both(
        "recursion",
        "Recursion",
        "A function that calls itself to solve a smaller piece of the same problem.",
        see=("function", "call", "exception"),
        priority=65,
        aka=("recursive", "base case"),
        python=dict(
            rules=(
                "Every recursive function needs a base case: an answer that needs no further call, or it never stops.",
                "Each call waits for the one below it, so deep recursion uses memory; Python gives up with a RecursionError at about 1000 levels.",
            ),
            detect=(r"\bdef\s+(\w+)\s*\([^)]*\)[^\n]*:\s*\n(?:[ \t]+\S[^\n]*\n)*?[ \t]+[^\n]*\b\1\s*\(",),
            example="""
                def fact(n):
                    if n <= 1:
                        return 1
                    return n * fact(n - 1)
                print(fact(5))
            """,
            out="120",
        ),
        javascript=dict(
            rules=(
                "Every recursive function needs a base case: an answer that needs no further call, or it never stops.",
                "Each call waits for the one below it, so deep recursion uses memory; JavaScript gives up with a RangeError (call stack size exceeded).",
            ),
            detect=(r"\bfunction\s+([\w$]+)\s*\([^)]*\)\s*\{[\s\S]*?\b\1\s*\(",),
            example="""
                function fact(n) {
                  if (n <= 1) return 1;
                  return n * fact(n - 1);
                }
                console.log(fact(5));
            """,
            out="120",
        ),
    ),
    *py(
        "try-except",
        "try / except",
        "Python's way to handle an exception: run the risky code in try, and put what to do about an error in except.",
        see=("exception", "finally"),
        priority=50,
        aka=("try", "except", "try/except", "catch"),
        detect=(r"\btry\b",),
        rules=(
            "Only the code inside try is guarded; if it raises, Python jumps straight to a matching except.",
            "except ValueError: catches only that kind. A bare except: catches everything, hiding real bugs.",
            "else: runs only if nothing went wrong, and finally: always runs.",
        ),
        example="""
            try:
                n = int("abc")
            except ValueError:
                n = 0
            print(n)
        """,
        out="0",
    ),
    *js(
        "try-catch",
        "try / catch",
        "JavaScript's way to handle an error: run the risky code in try, and put what to do about an error in catch.",
        see=("exception", "finally"),
        priority=50,
        aka=("try", "catch", "try/catch", "except"),
        detect=(r"\btry\b",),
        rules=(
            "Only the code inside try is guarded; if it throws, JavaScript jumps straight to catch with the error.",
            "The error object has a name (such as TypeError) and a message.",
            "A try/catch does not catch errors in code that runs later, such as a setTimeout callback or an un-awaited promise.",
        ),
        example="""
            try {
              JSON.parse("{bad");
            } catch (e) {
              console.log("bad JSON:", e.name);
            }
        """,
        out="bad JSON: SyntaxError",
    ),
]
