"""Pages 208-217: Async JavaScript, from zero.

The book already touches async in single pages (waiting for something that
is not ready, promise chains, awaiting in turn, what runs before what).
These ten go back to the start and take it slowly, one idea per page:
setTimeout, callbacks, new Promise, then chains, async functions, await,
try and catch around a rejection, a sleep helper, Promise.all, and one by
one against all at once.

Every exercise prints an order, never a time it measured, so the answers
are the same on any machine. Numbered after the game-building pages
(198-207, content_jsbuild), so this tuple is registered after JSBUILD_PAGES.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


_OP_WORDS = {"+": "plus", "-": "minus", "*": "times"}


# ── 208. setTimeout runs later ───────────────────────────────

_LATERS = (
    (("wake", None), ("toast", 0), ("shower", None)),
    (("one", 0), ("two", None)),
    (("a", None), ("b", 10), ("c", None), ("d", None)),
    (("red", 20), ("green", 10), ("blue", None)),
    (("start", None), ("late", 30), ("early", 10), ("end", None)),
    (("x", 0), ("y", 0), ("z", None)),
    (("hello", None), ("world", 0), ("again", None)),
    (("tick", 10), ("tock", 10), ("now", None)),
    (("first", None), ("third", 20), ("second", None)),
    (("ping", 0), ("pong", None), ("pang", None)),
    (("cat", 30), ("dog", 20), ("cow", 10), ("owl", None)),
    (("up", None), ("down", 0), ("left", None), ("right", 0)),
    (("sun", 40), ("moon", None), ("star", 0)),
    (("ready", None), ("go", 10), ("set", None)),
    (("apple", 0), ("pear", 10), ("plum", None), ("fig", None)),
    (("nine", 20), ("eight", None), ("seven", 20)),
    (("load", None), ("show", 0), ("save", None), ("quit", 50)),
    (("north", 10), ("south", None), ("east", 0), ("west", None)),
    (("alpha", None), ("beta", 20), ("gamma", None), ("delta", 0)),
    (("in", 0), ("out", None)),
)


def _later_step(word, ms) -> str:
    if ms is None:
        return f"print {word} straight away"
    return f"set a {ms} ms timer that prints {word}"


LATER_PAGE = _page(
    "js-async-later", 208, "Async JavaScript: setTimeout runs later",
    "JavaScript runs one thing at a time. The lines of your program run top "
    "to bottom, and while they are running nothing else can. setTimeout "
    "does not run its function — it hands it to node with a note saying "
    "\"not before this many milliseconds\", and carries straight on with "
    "the next line. Only when every line of the program has finished, and "
    "the call stack (the list of functions running right now) is empty, "
    "does node look at its queue of timers and run the ones that are due, "
    "soonest first. Two timers with the same delay run in the order they "
    "were set. So even a 0 ms timer runs after every plain line below it: "
    "zero means \"as soon as you are free\", and node is not free until "
    "the program is done.",
    "console.log(\"A\"); setTimeout(() => console.log(\"B\"), 0); "
    "console.log(\"C\"); prints A, C, B — the timer waits for the rest of "
    "the program, however short its delay",
    "jsa_later",
    tuple(
        ("Write these in this order: "
         + _and(_later_step(w, ms) for w, ms in steps)
         + ". Each word goes on its own line, and every timer uses "
         "setTimeout.",
         {"steps": steps})
        for steps in _LATERS
    ),
)


# ── 209. Callbacks ───────────────────────────────────────────

_CALLBACKS = (
    ("add", ((3, 4),), False, "asked"),
    ("add", ((3, 4),), True, "asked"),
    ("multiply", ((6, 7),), False, "done"),
    ("multiply", ((6, 7),), True, "done"),
    ("subtract", ((10, 4), (5, 9)), False, "both asked"),
    ("subtract", ((10, 4), (5, 9)), True, "both asked"),
    ("add", ((1, 1), (2, 2), (3, 3)), True, "three calls made"),
    ("multiply", ((2, 5), (3, 3)), False, "finished"),
    ("add", ((100, -1),), True, "waiting"),
    ("subtract", ((0, 8),), False, "after"),
    ("multiply", ((12, 12), (0, 99)), True, "queued"),
    ("add", ((7, 8), (9, 10)), False, "end"),
    ("subtract", ((50, 25),), True, "later is later"),
    ("multiply", ((4, 4), (5, 5), (6, 6)), True, "squares asked"),
    ("add", ((-3, 3),), False, "zero"),
    ("subtract", ((1, 2), (3, 4)), True, "two asked"),
    ("multiply", ((9, 9),), False, "last"),
    ("add", ((20, 22),), True, "not yet"),
    ("subtract", ((100, 1), (100, 99)), False, "hundreds"),
    ("multiply", ((3, -2),), True, "sign"),
)

_CALLBACK_DOES = {"add": "a + b", "subtract": "a - b", "multiply": "a * b"}

CALLBACK_PAGE = _page(
    "js-async-callback", 209, "Async JavaScript: callbacks",
    "A callback is a function you pass to another function, for it to call "
    "when it has an answer. Instead of return a + b, the function takes one "
    "more parameter, usually called done or cb, and calls done(a + b). "
    "Whoever called it says what happens to the answer by passing an arrow "
    "function: add(3, 4, (result) => ...). On its own that changes nothing "
    "about the order — done is called straight away, before add returns. "
    "It matters when the answer is not ready yet: wrap the call in "
    "setTimeout and done runs later, after the rest of the program. That "
    "is how all of node's slow work used to report back — reading a file, "
    "asking a server — and it is still underneath promises today.",
    "function add(a, b, done) { setTimeout(() => done(a + b), 0); } then "
    "add(3, 4, (r) => console.log(r)); console.log(\"asked\"); prints "
    "asked first and 7 after it",
    "jsa_callback",
    tuple(
        (f"Write a function {fn}(a, b, done) that calls done with "
         f"{_CALLBACK_DOES[fn]}"
         + (" from inside a 0 ms timer" if later else " straight away")
         + ". Call it with "
         + _and(f"{x} and {y}" for x, y in calls)
         + f", each time passing a callback that prints the result as "
         f"{fn} gave 7, and then print {word} on the last line of the "
         f"program.",
         {"fn": fn, "calls": calls, "later": later, "word": word})
        for fn, calls, later, word in _CALLBACKS
    ),
)


# ── 210. new Promise and resolve ─────────────────────────────

_PROMISES = (
    ("order", 6, "*", 7, None, None, "executor runs now", "after new Promise"),
    ("order", 6, "*", 7, 10, None, "executor runs now", "after new Promise"),
    ("pizza", 2, "+", 3, None, None, "baking", "ordered"),
    ("pizza", 2, "+", 3, None, 99, "baking", "ordered"),
    ("ticket", 100, "-", 1, None, None, "printing", "queued"),
    ("ticket", 100, "-", 1, 20, None, "printing", "queued"),
    ("score", 9, "*", 9, None, 0, "counting", "asked"),
    ("mail", 40, "+", 2, 0, None, "sending", "sent off"),
    ("parcel", 7, "*", 3, None, None, "packing", "posted"),
    ("reply", 50, "-", 8, 10, None, "thinking", "waiting"),
    ("dice", 1, "+", 5, None, 6, "rolling", "thrown"),
    ("coffee", 3, "*", 4, 30, None, "brewing", "cup out"),
    ("answer", 84, "-", 42, None, None, "working", "asked"),
    ("level", 5, "+", 5, None, 1, "loading", "menu shown"),
    ("file", 8, "*", 8, 0, None, "reading", "opened"),
    ("total", 11, "+", 12, 20, None, "adding", "sum asked"),
    ("stock", 30, "-", 45, None, None, "checking", "listed"),
    ("key", 2, "*", 21, None, 7, "cutting", "locked"),
    ("page", 12, "+", 0, 10, None, "fetching", "clicked"),
    ("gift", 15, "*", 2, None, None, "wrapping", "given"),
)

PROMISE_PAGE = _page(
    "js-async-promise", 210, "Async JavaScript: making a promise",
    "A promise is an object standing in for a value that may not exist "
    "yet. new Promise takes one function, the executor, and runs it "
    "immediately — right there, before new Promise even returns — handing "
    "it a function called resolve. Calling resolve(value) fills the "
    "promise in. A promise is filled in once: a second resolve is simply "
    "ignored. To use the value, call .then with a function; it gets the "
    "value as its argument. The rule that trips everyone up: a then "
    "callback never runs straight away, even if the promise is already "
    "resolved. It is queued, and runs once the code that is running now "
    "has finished. So the executor's own line prints first, then the "
    "lines after new Promise, and only then the then.",
    "const p = new Promise((resolve) => { console.log(\"in\"); "
    "resolve(42); }); p.then((v) => console.log(v)); "
    "console.log(\"out\"); prints in, out, 42",
    "jsa_promise",
    tuple(
        (f"Make a promise named {v} whose executor prints {inside} and then "
         f"resolves with {a} {_OP_WORDS[op]} {b}"
         + (f" from inside a {delay} ms timer" if delay is not None else "")
         + (f", then calls resolve a second time with {again}"
            if again is not None else "")
         + f". Give it a then that prints the value as {v} resolved with "
         f"42, and after all that print {after}.",
         {"var": v, "a": a, "op": op, "b": b, "delay": delay,
          "again": again, "inside": inside, "after": after})
        for v, a, op, b, delay, again, inside, after in _PROMISES
    ),
)


# ── 211. then passes a value along ───────────────────────────

_THENS = (
    (3, (("+", 4), ("*", 2)), None, "result", "chain built"),
    (10, (("-", 3),), None, "left", "chain built"),
    (2, (("*", 5), ("+", 1), ("*", 3)), None, "value", "waiting"),
    (7, (("+", 1),), ("*", 2), "result", "chain built"),
    (1, (("*", 100), ("-", 1)), None, "total", "set up"),
    (0, (("+", 5), ("+", 5)), None, "sum", "queued"),
    (6, (("*", 6),), ("+", 1), "got", "before"),
    (50, (("-", 25), ("*", 4)), None, "result", "first"),
    (9, (("*", 9), ("-", 1)), None, "square minus one", "sync done"),
    (4, (("+", 4), ("*", 4), ("-", 4)), None, "n", "ready"),
    (12, (("-", 12),), ("+", 3), "left", "chain built"),
    (5, (("*", -2),), None, "flipped", "above"),
    (100, (("-", 1), ("-", 1), ("-", 1)), None, "count", "counting"),
    (8, (("*", 2), ("*", 2)), None, "doubled twice", "go"),
    (3, (("-", 1),), ("*", 10), "value", "later"),
    (21, (("*", 2),), None, "answer", "asking"),
    (15, (("+", 5), ("*", 5)), None, "result", "made"),
    (2, (("*", 2), ("*", 2), ("*", 2)), None, "power", "built"),
    (40, (("+", 2),), ("-", 2), "result", "before the result"),
    (-5, (("*", -1), ("+", 10)), None, "result", "negative start"),
)


def _step_words(op, k) -> str:
    return {"+": f"add {k}", "-": f"subtract {k}", "*": f"multiply by {k}"}[op]


THEN_PAGE = _page(
    "js-async-then", 211, "Async JavaScript: then passes the value along",
    "Every .then returns a brand new promise, and that new promise is "
    "resolved with whatever your then function returns. That is what lets "
    "you chain them: .then((n) => n + 4) receives the value, and the "
    "number it returns is what the next .then receives. An arrow function "
    "without braces returns its expression by itself. With braces it "
    "returns nothing unless you write return — so .then((n) => { n * 2; }) "
    "works the sum out and throws it away, and the next step gets "
    "undefined. That missing return is the most common promise bug there "
    "is. And as always, none of the then functions run until the "
    "synchronous code has finished, so a line written after the whole "
    "chain still prints first.",
    "Promise.resolve(3).then((n) => n + 4).then((n) => n * 2).then((n) => "
    "console.log(n)); console.log(\"built\"); prints built, then 14",
    "jsa_then",
    tuple(
        (f"Start from a promise resolved with {start}, then "
         + _and(_step_words(op, k) for op, k in steps)
         + ", one then for each"
         + (f", then add a then with braces that works out n "
            f"{_OP_WORDS[forget[0]]} {forget[1]} but forgets to return it"
            if forget else "")
         + f". Finish with a then that prints the value as {label} 14, and "
         f"on the line after the chain print {word}.",
         {"start": start, "steps": steps, "forget": forget, "label": label,
          "word": word})
        for start, steps, forget, label, word in _THENS
    ),
)


# ── 212. Async functions return promises ─────────────────────

_ASYNCS = (
    ("total", (2, 3)),
    ("total", (10, -4)),
    ("total", (100, 250)),
    ("total", (7, 7)),
    ("area", (4, 5)),
    ("area", (3, 3)),
    ("area", (12, 10)),
    ("area", (1, 99)),
    ("area", (6, 7)),
    ("double", (21,)),
    ("double", (-8,)),
    ("double", (0,)),
    ("double", (1000,)),
    ("greet", ("ana",)),
    ("greet", ("world",)),
    ("greet", ("bo",)),
    ("shout", ("hey",)),
    ("shout", ("stop",)),
    ("shout", ("go",)),
    ("shout", ("async",)),
)

_ASYNC_DOES = {
    "total": ("total(a, b)", "a + b"),
    "area": ("area(w, h)", "w * h"),
    "double": ("double(n)", "n * 2"),
    "greet": ("greet(name)", "hello followed by a space and the name"),
    "shout": ("shout(word)", "the word in capital letters"),
}


def _args_words(args) -> str:
    return _and(str(x) for x in args)


ASYNCFN_PAGE = _page(
    "js-async-asyncfn", 212, "Async JavaScript: an async function returns a promise",
    "Put async in front of a function and it always returns a promise, "
    "whatever the return statement says. async function total(a, b) { "
    "return a + b; } does add the numbers — but total(2, 3) hands back a "
    "promise holding 5, not 5 itself. Printing result instanceof Promise "
    "shows true. To get at the 5 you need .then (or, next page, await), and "
    "that then waits in the queue like any other, so the line after the "
    "call prints before the value does. The body of an async function "
    "still starts running the moment you call it; it is only the answer "
    "that is delivered later.",
    "async function total(a, b) { return a + b; } const r = total(2, 3); "
    "console.log(r instanceof Promise); prints true, and r.then((v) => "
    "console.log(v)) prints 5 once the program's own lines are done",
    "jsa_asyncfn",
    tuple(
        (f"Write an async function {_ASYNC_DOES[fn][0]} that returns "
         f"{_ASYNC_DOES[fn][1]}. Call it with {_args_words(args)} and keep "
         f"what comes back as result, print whether result is a Promise, "
         f"give result a then that prints the value as {fn} is 5, and "
         f"after that print called {fn}.",
         {"fn": fn, "args": args})
        for fn, args in _ASYNCS
    ),
)


# ── 213. await pauses only this function ─────────────────────

_AWAITS = (
    ((), "A", 5, "B", ("C",)),
    ((), "start", 1, "resumed with", ("outside",)),
    (("first",), "in main", 42, "got", ("after the call",)),
    ((), "one", 3, "three", ("two",)),
    ((), "asking", 10, "answer", ("carrying on", "still going")),
    (("setup",), "main begins", 7, "main ends with", ("free",)),
    ((), "open", 0, "closed after", ("meanwhile",)),
    ((), "before await", 99, "after await", ("outside main",)),
    (("boot",), "loading", 2, "loaded", ("menu",)),
    ((), "hi", 8, "bye", ("in between",)),
    ((), "knock", 4, "come in", ("who is there", "a pause")),
    (("ready",), "set", 1, "go", ("wait",)),
    ((), "tea on", 3, "tea ready", ("read a page",)),
    ((), "ask", 6, "reply", ("look away",)),
    (("x",), "y", 11, "z", ("w",)),
    ((), "call", 20, "answered", ("ring", "ring again")),
    ((), "red", 1, "green", ("amber",)),
    (("dawn",), "morning", 12, "noon", ("tea",)),
    ((), "left", 5, "right", ("middle",)),
    (("a1",), "b2", 3, "c", ("d4", "e5")),
)

AWAIT_PAGE = _page(
    "js-async-await", 213, "Async JavaScript: await pauses only this function",
    "Inside an async function, await promise stops that function until the "
    "promise has a value, and then gives you the value: const n = await "
    "p. It reads like ordinary top-to-bottom code, which is the whole point. "
    "But await does not freeze the program. It pauses this one function, "
    "puts the rest of it in the queue, and returns to whoever called it — "
    "so the lines after main() carry on and print first. Only when they "
    "are finished does main pick up where it left off. Everything in main "
    "before the await runs straight away, as part of the call. Even "
    "awaiting a promise that is already resolved pauses like this.",
    "async function main() { console.log(\"A\"); const n = await "
    "Promise.resolve(5); console.log(`B ${n}`); } main(); "
    "console.log(\"C\"); prints A, C, B 5",
    "jsa_await",
    tuple(
        ((f"Print {_and(pre)}, then c" if pre else "C")
         + f"all an async function main that prints {before}, awaits a "
         f"promise resolved with {value} and prints the value as {after} "
         f"5. After calling main, print {_and(post)}, each on its own line.",
         {"pre": pre, "before": before, "value": value, "after": after,
          "post": post})
        for pre, before, value, after, post in _AWAITS
    ),
)


# ── 214. try and catch around await ──────────────────────────

_TRIES = (
    ((3, -1, 2), "min", 1, 10),
    ((5, 0, 7), "min", 1, 2),
    ((1, 2, 3, 4), "even", 0, 5),
    ((10, 4, 20), "min", 5, 1),
    ((2, 3), "even", 0, 10),
    ((-2, -1, 0), "min", 0, 3),
    ((8, 7, 6), "even", 0, 2),
    ((100, 50, 99), "min", 60, 1),
    ((1, 1, 2), "even", 0, 7),
    ((0, 1), "min", 1, 100),
    ((4, 9, 16, 25), "even", 0, 1),
    ((6, 5, 4, 3), "min", 5, 6),
    ((12, 11), "even", 0, 3),
    ((3, 30, 300), "min", 10, 2),
    ((-4, -3), "even", 0, 5),
    ((1, 2), "min", 2, 9),
    ((20, 21, 22), "even", 0, 4),
    ((9, 8, 7), "min", 8, 11),
    ((2, 4, 5), "even", 0, 8),
    ((15, -15), "min", 0, 2),
)

TRY_PAGE = _page(
    "js-async-trycatch", 214, "Async JavaScript: catching a rejected promise",
    "A promise can fail instead of succeed: it is rejected, usually with an "
    "Error. Promise.reject(new Error(\"nope\")) makes one that has already "
    "failed, and throw inside an async function does the same thing. When "
    "you await a rejected promise, the await throws that error right "
    "there, as if the line itself had failed — so the ordinary try and "
    "catch you would use for any error catches it. The error's text is "
    "err.message. Put the try inside the loop and one failure is dealt "
    "with and the loop carries on to the next value; put it outside and "
    "the first failure ends the loop. A rejection nobody catches stops "
    "node with an error.",
    "try { console.log(await check(-1)); } catch (err) { "
    "console.log(err.message); } prints the rejection's message instead "
    "of crashing, and the code after the catch carries on",
    "jsa_trycatch",
    tuple(
        ((f"Write check(n), which returns a promise rejected with an Error "
          f"saying 5 is too small when n is below {m}, and otherwise one "
          f"resolved with n times {t}."
          if rule == "min" else
          f"Write check(n), which returns a promise rejected with an Error "
          f"saying 3 is odd when n is odd, and otherwise one resolved with "
          f"n times {t}.")
         + f" In an async function, await check for each of "
         f"{_and(str(n) for n in inputs)} in turn inside try and catch, "
         f"printing ok and the value, or caught and the error's message, "
         f"as ok 30 or caught 5 is too small.",
         {"inputs": inputs, "rule": rule, "min": m, "times": t})
        for inputs, rule, m, t in _TRIES
    ),
)


# ── 215. A sleep helper ──────────────────────────────────────

_SLEEPS = (
    ((("boil", 20), ("steep", 10)), "kettle on"),
    ((("wash", 10), ("rinse", 10), ("dry", 20)), "started"),
    ((("red", 30), ("green", 20)), "lights on"),
    ((("one", 10), ("two", 10)), "counting"),
    ((("mix", 10), ("bake", 40), ("cool", 20)), "oven on"),
    ((("ready", 10), ("set", 10), ("go", 10)), "race"),
    ((("warm up", 20), ("run", 50)), "shoes on"),
    ((("load", 30), ("play", 10)), "booting"),
    ((("a", 0), ("b", 10), ("c", 0)), "letters"),
    ((("knock", 10), ("wait", 30)), "at the door"),
    ((("ping", 20), ("pong", 20)), "table set"),
    ((("seed", 10), ("water", 20), ("grow", 40)), "garden"),
    ((("draft", 40), ("edit", 20), ("send", 10)), "writing"),
    ((("up", 10), ("down", 10), ("up again", 10), ("down again", 10)), "stairs"),
    ((("north", 50), ("south", 30)), "compass"),
    ((("dial", 10), ("ring", 20), ("answer", 0)), "phone"),
    ((("fetch", 30), ("parse", 10), ("show", 10)), "page open"),
    ((("inhale", 20), ("hold", 20), ("exhale", 20)), "breathing"),
    ((("sand", 10), ("paint", 40)), "workshop"),
    ((("check", 0), ("mate", 10)), "chess"),
)

SLEEP_PAGE = _page(
    "js-async-sleep", 215, "Async JavaScript: a sleep helper, one wait after another",
    "setTimeout takes a callback, and await wants a promise, so the two "
    "are joined with one line you will see everywhere: const sleep = (ms) "
    "=> new Promise((resolve) => setTimeout(resolve, ms)). It makes a "
    "promise and hands its resolve to the timer, so the promise is "
    "fulfilled when the time is up. Now await sleep(20) inside an async "
    "function waits 20 ms and carries on — and in a for...of loop each "
    "await finishes before the next sleep even starts, so the waits add "
    "up. Keep your own running total rather than reading the clock: the "
    "program then prints the same numbers every time. Meanwhile, the line "
    "after main() prints first, because main pauses at its first await.",
    "const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, "
    "ms)); then await sleep(20); await sleep(10); inside an async function "
    "waits 30 ms in all, one wait after the other",
    "jsa_sleep",
    tuple(
        ("Write a sleep(ms) helper that returns a promise resolved by "
         "setTimeout. In an async function main, go through the steps "
         + _and(f"{n} for {ms} ms" for n, ms in steps)
         + f" in turn, awaiting sleep for each and adding up the time "
         f"waited, and print each as "
         f"{steps[0][0]} after {steps[0][1]} ms. Call main, and on the "
         f"next line of the program print {word}.",
         {"steps": steps, "word": word})
        for steps, word in _SLEEPS
    ),
)


# ── 216. Promise.all ─────────────────────────────────────────

_ALLS = (
    ((("ana", 30), ("bo", 10), ("cy", 20)), "fetchUser", "upper"),
    ((("ana", 30), ("bo", 10), ("cy", 20)), "fetchUser", "length"),
    ((("red", 20), ("blue", 10)), "loadColor", "upper"),
    ((("north", 40), ("south", 20), ("east", 30), ("west", 10)), "ask", "upper"),
    ((("apple", 10), ("kiwi", 30), ("fig", 20)), "fetchFruit", "length"),
    ((("slow", 50), ("fast", 10)), "race", "upper"),
    ((("x", 20), ("y", 30), ("z", 10)), "getLetter", "upper"),
    ((("mon", 30), ("tue", 20), ("wed", 10)), "loadDay", "upper"),
    ((("hello", 20), ("hi", 10)), "greet", "length"),
    ((("pizza", 40), ("soup", 10), ("salad", 20)), "order", "upper"),
    ((("one", 10), ("three", 30), ("two", 20)), "count", "length"),
    ((("gold", 30), ("silver", 20), ("bronze", 10)), "medal", "upper"),
    ((("cat", 20), ("mouse", 10)), "chase", "length"),
    ((("alpha", 40), ("beta", 30), ("gamma", 20), ("delta", 10)), "fetchWord", "length"),
    ((("tea", 10), ("coffee", 50), ("water", 30)), "pour", "upper"),
    ((("left", 30), ("right", 10)), "turn", "upper"),
    ((("sun", 20), ("moon", 40), ("star", 10)), "shine", "length"),
    ((("bob", 30), ("amy", 20), ("cal", 40), ("dan", 10)), "fetchUser", "upper"),
    ((("zip", 10), ("ab", 30), ("longest", 20)), "measure", "length"),
    ((("rock", 20), ("paper", 30), ("scissors", 10)), "play", "upper"),
)

_GIVES = {"upper": "the name in capital letters",
          "length": "the number of letters in the name"}

ALL_PAGE = _page(
    "js-async-all", 216, "Async JavaScript: Promise.all keeps your order",
    "Calling an async function starts it; it does not wait for it. So "
    "jobs.map((j) => fetchUser(j)) starts every job at once and gives you "
    "an array of promises. Promise.all takes that array and returns one "
    "promise that resolves when all of them have — with an array of their "
    "results in the same order as the array you gave it, not the order "
    "they finished in. Watch the two orders side by side: each job prints "
    "when it arrives, so the quick ones print first, but the results "
    "still line up with the input. If any one of them rejects, "
    "Promise.all rejects too, straight away.",
    "Promise.all([slow(), fast()]) — fast prints first when it arrives, "
    "but the results array is still [slow's result, fast's result]",
    "jsa_all",
    tuple(
        (f"Write a sleep helper and an async function {fn}(name, ms) that "
         f"sleeps for ms, prints the name followed by arrived, and returns "
         f"{_GIVES[give]}. Start it for "
         + _and(f"{n} with {ms} ms" for n, ms in jobs)
         + " all at once with Promise.all, and when that resolves print "
         "the results joined by a comma and a space.",
         {"jobs": jobs, "fn": fn, "give": give})
        for jobs, fn, give in _ALLS
    ),
)


# ── 217. One by one, or all at once ──────────────────────────

_DISHES = (
    (("soup", 30), ("bread", 10), ("salad", 20)),
    (("rice", 20), ("fish", 40)),
    (("eggs", 10), ("toast", 20), ("juice", 30)),
    (("tea", 50), ("cake", 10)),
    (("pasta", 30), ("sauce", 20), ("cheese", 10)),
    (("steak", 40), ("fries", 30), ("peas", 10)),
    (("pie", 20), ("cream", 10)),
    (("noodles", 10), ("broth", 40), ("egg", 20)),
    (("tacos", 30), ("salsa", 10), ("beans", 20), ("rice", 40)),
    (("bagel", 20), ("coffee", 30)),
)
_PARALLELS = tuple((want, d) for d in _DISHES for want in ("one", "all"))


def _dish_words(dishes) -> str:
    return _and(f"{n} for {ms} ms" for n, ms in dishes)


PARALLEL_PAGE = _page(
    "js-async-parallel", 217, "Async JavaScript: one by one, or all at once",
    "Three things to cook, 30, 10 and 20 ms each. Awaited one by one in a "
    "loop, each waits for the one before, so the total is the sum: 60 ms, "
    "and they finish in the order you wrote them. Started all at once — "
    "call the async function for each and hand the promises to "
    "Promise.all — they wait side by side, so the total is only the "
    "longest one, 30 ms, and they finish shortest first. Same work, half "
    "the time. The loop is still right when each step needs the one before "
    "it (you cannot fetch a user's orders before you have the user); when "
    "the jobs do not depend on each other, start them together. The clock "
    "here is counted by the program itself, never read, so it prints the "
    "same every time.",
    "for (const [name, ms] of dishes) { await sleep(ms); clock += ms; } "
    "takes 30 + 10 + 20 = 60 ms; Promise.all(dishes.map(([name, ms]) => "
    "cook(name, ms))) takes the longest, 30 ms",
    "jsa_parallel",
    tuple(
        ((f"Write a sleep helper, then in an async function main cook "
          f"{_dish_words(dishes)} one after another, awaiting each before "
          f"the next. Keep a clock of the time waited so far, print each "
          f"dish as soup ready at 30, and at the end print the total as "
          f"one by one: 60 ms."
          if want == "one" else
          f"Write a sleep helper and an async function cook(name, ms) that "
          f"sleeps for ms, prints the dish as soup ready at 30 and returns "
          f"ms. Start cooking {_dish_words(dishes)} all at once with "
          f"Promise.all, then print the longest time as all at once: 30 "
          f"ms."),
         {"want": want, "dishes": dishes})
        for want, dishes in _PARALLELS
    ),
)


JSASYNC_PAGES: tuple[Page, ...] = (
    LATER_PAGE,
    CALLBACK_PAGE,
    PROMISE_PAGE,
    THEN_PAGE,
    ASYNCFN_PAGE,
    AWAIT_PAGE,
    TRY_PAGE,
    SLEEP_PAGE,
    ALL_PAGE,
    PARALLEL_PAGE,
)
