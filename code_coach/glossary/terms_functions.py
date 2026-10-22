"""Words about functions and the things built from them: calls, arguments, closures, classes, generators."""

from __future__ import annotations

from .entry import Entry, both

_PY_NOT_CALLS = r"if|elif|while|for|def|return|and|or|not|in|is|lambda|class|with|assert|yield|await|print"
_JS_NOT_CALLS = r"if|while|for|switch|function|catch|return|typeof|new|await|void|delete"

TERMS: list[Entry] = [
    *both(
        "function",
        "Function",
        "A named, reusable piece of code. You write it once and run it, with different inputs, as often as you like.",
        see=("parameter", "argument", "return", "call"),
        priority=45,
        aka=("functions", "def", "subroutine", "procedure"),
        python=dict(
            rules=(
                "def name(parameters): followed by an indented body defines a function.",
                "Defining a function does not run it; you have to call it.",
                "Functions are values: you can store one in a variable or pass it to another function.",
            ),
            detect=(r"\bdef\s+\w+",),
            example="""
                def double(n):
                    return n * 2
                print(double(4))
            """,
            out="8",
        ),
        javascript=dict(
            rules=(
                "function name(parameters) { ... } defines one; (x) => x * 2 is the short arrow form.",
                "Defining a function does not run it; you have to call it.",
                "Functions are values: you can store one in a variable or pass it to another function.",
            ),
            detect=(r"\bfunction\b",),
            example="""
                function double(n) {
                  return n * 2;
                }
                console.log(double(4));
            """,
            out="8",
        ),
    ),
    *both(
        "parameter",
        "Parameter",
        "A name in a function's definition that receives a value when the function is called. In def f(x), x is a parameter.",
        see=("argument", "function", "local"),
        priority=40,
        aka=("parameters", "param", "params", "formal parameter"),
        python=dict(
            rules=(
                "A parameter is a local variable that exists only while the function runs.",
                "A default value (def f(x, y=10)) is used when the caller leaves that argument out.",
                "*args collects extra positional arguments into a tuple.",
            ),
            detect=(r"\bdef\s+\w+\s*\([^)]*\w[^)]*\)",),
            example="""
                def greet(name, punctuation="!"):
                    return "hi " + name + punctuation
                print(greet("Ana"), greet("Bo", "?"))
            """,
            out="hi Ana! hi Bo?",
        ),
        javascript=dict(
            rules=(
                "A parameter is a local variable that exists only while the function runs.",
                "A default value (function f(x, y = 10)) is used when the argument is missing or undefined.",
                "A parameter with no matching argument is undefined - JavaScript does not complain.",
            ),
            detect=(r"\bfunction\s*[\w$]*\s*\([^)]*\w[^)]*\)", r"\(\s*[\w$][\w$\s,=]*\)\s*=>|\b[\w$]+\s*=>"),
            example="""
                function greet(name, punctuation = "!") {
                  return "hi " + name + punctuation;
                }
                console.log(greet("Ana"), greet("Bo", "?"), greet());
            """,
            out="hi Ana! hi Bo? hi undefined!",
        ),
    ),
    *both(
        "argument",
        "Argument",
        "The actual value you hand to a function when you call it. In double(4), 4 is the argument.",
        see=("parameter", "call", "function"),
        priority=30,
        aka=("arguments", "arg", "args"),
        python=dict(
            rules=(
                "Each argument fills one parameter. By position: area(3, 4). By name: area(h=2, w=5).",
                "Too few or too many arguments is a TypeError.",
                "Numbers and strings are passed by value (the function cannot change yours); a list or dict can be changed by the function.",
            ),
            detect=(rf"(?<!\bdef )\b(?!(?:{_PY_NOT_CALLS})\b)[A-Za-z_]\w*\(\s*[^()\s]",),
            example="""
                def area(w, h):
                    return w * h
                print(area(3, 4), area(h=2, w=5))
            """,
            out="12 10",
        ),
        javascript=dict(
            rules=(
                "Each argument fills one parameter, by position only: area(3, 4).",
                "Missing arguments are undefined and extra ones are ignored - no error either way.",
                "Numbers and strings are passed by value; an array or object can be changed by the function.",
            ),
            detect=(rf"\b(?!(?:{_JS_NOT_CALLS})\b)[A-Za-z_$][\w$]*\(\s*[^()\s]",),
            example="""
                function area(w, h) {
                  return w * h;
                }
                console.log(area(3, 4), area(3));
            """,
            out="12 NaN",
        ),
    ),
    *both(
        "return",
        "Return value",
        "The value a function hands back to the code that called it. The call is replaced by that value.",
        see=("function", "call", "argument"),
        priority=45,
        aka=("return", "returns", "returned", "returning", "output of a function"),
        python=dict(
            rules=(
                "The function ends the moment it reaches return; lines after it do not run.",
                "A function with no return gives back None.",
                "Returning is not printing: print shows a value to the person, return hands it to the program.",
            ),
            detect=(r"\breturn\b",),
            example="""
                def f():
                    pass
                def g():
                    return 5
                print(f(), g())
            """,
            out="None 5",
        ),
        javascript=dict(
            rules=(
                "The function ends the moment it reaches return; lines after it do not run.",
                "A function with no return gives back undefined.",
                "Returning is not printing: console.log shows a value to the person, return hands it to the program.",
            ),
            detect=(r"\breturn\b",),
            example="""
                function f() {}
                function g() {
                  return 5;
                }
                console.log(f(), g());
            """,
            out="undefined 5",
        ),
    ),
    *both(
        "call",
        "Function call",
        "Running a function by writing its name followed by parentheses, with any arguments inside.",
        see=("function", "argument", "return"),
        priority=30,
        aka=("calling", "called", "invoke", "invocation", "function call"),
        python=dict(
            rules=(
                "double(4) runs the function; double on its own is just the function itself, not a run of it.",
                "A call is an expression: its value is whatever the function returns.",
                "Every call needs the parentheses, even with no arguments: f().",
            ),
            detect=(rf"\b(?!(?:{_PY_NOT_CALLS.replace('|print', '')})\b)[A-Za-z_]\w*\s*\(",),
            example="""
                def hi():
                    return "hi"
                print(type(hi).__name__, hi())
            """,
            out="function hi",
        ),
        javascript=dict(
            rules=(
                "double(4) runs the function; double on its own is just the function itself, not a run of it.",
                "A call is an expression: its value is whatever the function returns.",
                "Every call needs the parentheses, even with no arguments: f().",
            ),
            detect=(rf"\b(?!(?:{_JS_NOT_CALLS})\b)[A-Za-z_$][\w$]*\s*\(",),
            example="""
                function hi() {
                  return "hi";
                }
                console.log(typeof hi, hi());
            """,
            out="function hi",
        ),
    ),
    *both(
        "method",
        "Method",
        "A function that belongs to a value or a class and is called with a dot: text.upper() or list.append(3).",
        see=("function", "class", "call"),
        priority=30,
        aka=("methods",),
        python=dict(
            rules=(
                "In a class, a method's first parameter is self, the object it was called on.",
                "Different types have different methods: str has upper(), list has append().",
                "dir(x) lists an object's methods.",
            ),
            detect=(r"[\w)\]]\.[A-Za-z_]\w*\(",),
            example="""
                print("hi".upper(), [3, 1, 2].index(1))
            """,
            out="HI 1",
        ),
        javascript=dict(
            rules=(
                "In a class, a method can reach the object it was called on as this.",
                "Different types have different methods: strings have toUpperCase(), arrays have push().",
                "console.log is itself a method: log belongs to console.",
            ),
            detect=(r"[\w$)\]](?<!console)\.[A-Za-z_$][\w$]*\(",),
            example="""
                console.log("hi".toUpperCase(), [3, 1, 2].indexOf(1));
            """,
            out="HI 1",
        ),
    ),
    *both(
        "class",
        "Class",
        "A blueprint for making objects that bundle data with the functions that work on it.",
        see=("method", "function"),
        priority=50,
        aka=("classes", "object-oriented", "oop", "constructor"),
        python=dict(
            see=("method", "function", "instance", "self"),
            rules=(
                "class Name: starts one; __init__ runs when you make an object, and sets up its data.",
                "Calling the class, Dog('Rex'), makes a new object (an instance).",
                "Class names start with a capital letter by convention.",
            ),
            detect=(r"\bclass\b",),
            example="""
                class Dog:
                    def __init__(self, name):
                        self.name = name
                    def speak(self):
                        return self.name + " says woof"
                print(Dog("Rex").speak())
            """,
            out="Rex says woof",
        ),
        javascript=dict(
            see=("method", "function", "this", "object"),
            rules=(
                "class Name { constructor(...) { ... } } starts one; the constructor runs when you make an object.",
                "new Dog('Rex') makes a new object from the class.",
                "Class names start with a capital letter by convention.",
            ),
            detect=(r"\bclass\b", r"\bnew\s+[A-Z]"),
            example="""
                class Dog {
                  constructor(name) {
                    this.name = name;
                  }
                  speak() {
                    return this.name + " says woof";
                  }
                }
                console.log(new Dog("Rex").speak());
            """,
            out="Rex says woof",
        ),
    ),
    *both(
        "closure",
        "Closure",
        "A function that remembers the variables from the place where it was written, even after that surrounding code has finished.",
        see=("scope", "function", "local"),
        priority=75,
        aka=("closures", "nonlocal", "enclosing scope"),
        python=dict(
            rules=(
                "The inner function keeps using the outer function's variables after the outer one has returned.",
                "To CHANGE such a variable (not just read it) the inner function needs nonlocal.",
                "Each call to the outer function makes a fresh set of remembered variables.",
            ),
            detect=(r"\bnonlocal\b", r"\bdef\b[^\n]*\n(?:[ \t]+[^\n]*\n)*?[ \t]+def\b"),
            example="""
                def counter():
                    n = 0
                    def step():
                        nonlocal n
                        n += 1
                        return n
                    return step
                next_one = counter()
                print(next_one(), next_one())
            """,
            out="1 2",
        ),
        javascript=dict(
            rules=(
                "The inner function keeps using the outer function's variables after the outer one has returned.",
                "It can read and change them (unless they are const).",
                "Each call to the outer function makes a fresh set of remembered variables.",
            ),
            detect=(r"\breturn\s+(?:function\b|\([^)]*\)\s*=>|[\w$]+\s*=>)",),
            example="""
                function counter() {
                  let n = 0;
                  return () => ++n;
                }
                const next = counter();
                console.log(next(), next());
            """,
            out="1 2",
        ),
    ),
    *both(
        "callback",
        "Callback",
        "A function you hand to another function so that it can call it later, at the right moment.",
        see=("function", "argument", "call"),
        priority=60,
        aka=("callbacks", "higher-order function", "handler"),
        python=dict(
            see=("function", "lambda", "argument"),
            rules=(
                "Pass the function itself, without parentheses: key=len, not key=len().",
                "sorted, map, filter, min and max all accept one (often as key=).",
            ),
            detect=(r"\b(?:key|func|callback)\s*=\s*[A-Za-z_]", r"\b(?:map|filter)\(",),
            example="""
                print(sorted(["bb", "a", "ccc"], key=len))
            """,
            out="['a', 'bb', 'ccc']",
        ),
        javascript=dict(
            see=("function", "arrow-function", "argument"),
            rules=(
                "Pass the function itself, without parentheses: arr.map(fn), not arr.map(fn()).",
                "Array methods (map, filter, sort, forEach), setTimeout and event listeners all take one.",
                "Callbacks are how JavaScript says 'do this when it is ready'.",
            ),
            detect=(r"\.(?:map|filter|forEach|reduce|sort|find|some|every)\(", r"\bsetTimeout\(|\bsetInterval\(|\baddEventListener\("),
            example="""
                console.log(["bb", "a", "ccc"].sort((x, y) => x.length - y.length));
            """,
            out="[ 'a', 'bb', 'ccc' ]",
        ),
    ),
    *both(
        "generator",
        "Generator",
        "A function that hands back its results one at a time, pausing between them, instead of building the whole list first.",
        see=("iterable", "function", "loop"),
        priority=60,
        aka=("generators", "yield", "lazy"),
        python=dict(
            rules=(
                "A function with yield in it is a generator function; calling it gives a generator, not the values.",
                "Each pass of a for loop (or each next()) resumes it until the next yield.",
                "It can be used only once; run it again by calling the function again.",
            ),
            detect=(r"\byield\b",),
            example="""
                def count_up(n):
                    for i in range(n):
                        yield i
                print(list(count_up(3)))
            """,
            out="[0, 1, 2]",
        ),
        javascript=dict(
            rules=(
                "function* with yield makes a generator function; calling it gives a generator, not the values.",
                "Each pass of a for...of loop (or each .next()) resumes it until the next yield.",
                "It can be used only once; run it again by calling the function again.",
            ),
            detect=(r"\bfunction\s*\*|\byield\b",),
            example="""
                function* countUp(n) {
                  for (let i = 0; i < n; i++) yield i;
                }
                console.log([...countUp(3)]);
            """,
            out="[ 0, 1, 2 ]",
        ),
    ),
    *both(
        "unpacking",
        "Unpacking",
        "Splitting a list or object into separate variables in one step.",
        see=("assignment", "variable", "iterable"),
        priority=65,
        aka=("destructuring", "destructure", "unpack", "tuple unpacking"),
        python=dict(
            aka=("destructuring", "destructure", "unpack", "tuple unpacking", "star unpacking", "rest"),
            rules=(
                "a, b = [1, 2] sets a to 1 and b to 2; the counts must match or it is a ValueError.",
                "a, b = b, a swaps two variables, with no temporary.",
                "first, *rest = items puts the first item in first and all the others in rest.",
            ),
            detect=(
                r"^\s*[A-Za-z_]\w*\s*,\s*\*?[A-Za-z_][\w\s,*]*=(?!=)",
                r"\bfor\s+\w+\s*,\s*\w+\s+in\b",
            ),
            example="""
                a, b = 1, 2
                a, b = b, a
                first, *rest = [1, 2, 3]
                print(a, b, first, rest)
            """,
            out="2 1 1 [2, 3]",
        ),
        javascript=dict(
            term="Destructuring",
            definition="Pulling values out of an array or object into separate variables in one step.",
            rules=(
                "const [a, b] = [1, 2] takes by position; const { x, y } = obj takes by property name.",
                "[a, b] = [b, a] swaps two variables, with no temporary.",
                "const [first, ...rest] = items puts the first item in first and the others in rest.",
            ),
            detect=(
                r"\b(?:const|let|var)\s*[\[{][^\]}]*[\]}]\s*=",
                r"^\s*\[[^\]\n]*\]\s*=(?!=)",
                r"\(\s*[{\[][^)]*[}\]]\s*\)\s*=>",
            ),
            example="""
                let [a, b] = [1, 2];
                [a, b] = [b, a];
                const { x, y } = { x: 5, y: 6 };
                console.log(a, b, x, y);
            """,
            out="2 1 5 6",
        ),
    ),
    *both(
        "async-await",
        "async / await",
        "A way to write code that waits for something slow (a download, a timer) without freezing everything else.",
        see=("function", "callback"),
        priority=60,
        aka=("async", "await", "asynchronous", "asyncio", "coroutine"),
        python=dict(
            rules=(
                "async def makes a coroutine function: calling it does not run the body, it gives a coroutine.",
                "await pauses the current coroutine until another one finishes, letting others run meanwhile.",
                "asyncio.run(coroutine) starts the top-level one.",
            ),
            detect=(r"\b(?:async|await)\b|\basyncio\b",),
            example="""
                import asyncio
                async def double(n):
                    await asyncio.sleep(0)
                    return n * 2
                print(asyncio.run(double(4)))
            """,
            out="8",
        ),
        javascript=dict(
            see=("function", "callback", "promise", "event-loop"),
            rules=(
                "An async function always returns a promise, whatever it returns.",
                "await pauses THAT function until a promise settles; the rest of the program keeps running.",
                "await works inside async functions (and at the top level of a module).",
            ),
            detect=(r"\b(?:async|await)\b",),
            example="""
                async function f() {
                  const v = await Promise.resolve(7);
                  return v * 2;
                }
                f().then((v) => console.log(v));
                console.log("first");
            """,
            out="first\n14",
        ),
    ),
]
