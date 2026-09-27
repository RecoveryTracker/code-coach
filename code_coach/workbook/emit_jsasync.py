"""JavaScript: async, from zero.

Node runs one piece of JavaScript at a time. Whatever is running now runs to
the end; anything that has to wait — a timer, a promise's then, the rest of
an async function after an await — is put in a queue and run afterwards.
Every page here is about that one rule, seen from a different side:
setTimeout, callbacks, new Promise, then chains, async functions, await,
rejections, a sleep helper, Promise.all, and one-by-one against all-at-once.

The oracle does not run anything. It works out the order from the rules —
synchronous lines first, in the order they are written; then promise
callbacks; then timers, soonest first, ties in the order they were set —
and the tests check that node agrees.

No answer prints a time it measured. Timers are a few milliseconds and only
ever decide an order, and every total printed is added up by the program
itself, so the output is the same on a fast machine and a busy one. That
works because node reads the clock once per turn of its loop: timers set in
the same turn with different delays always fire soonest first, and timers
with the same delay fire in the order they were set.
"""

from __future__ import annotations

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("jsa_later", "setTimeout runs after everything written below it"),
    Shape("jsa_callback", "passing a function to be called with the result"),
    Shape("jsa_promise", "making a promise with new Promise and resolve"),
    Shape("jsa_then", "a then chain that passes a value along"),
    Shape("jsa_asyncfn", "an async function returns a promise"),
    Shape("jsa_await", "await pauses only the function it is in"),
    Shape("jsa_trycatch", "catching a rejected promise with try and catch"),
    Shape("jsa_sleep", "a sleep helper and awaits one after another"),
    Shape("jsa_all", "Promise.all keeps the order it was given"),
    Shape("jsa_parallel", "one by one against all at once"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: The one line every timer page starts with.
SLEEP = "const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));"

#: The functions the callback page passes a result from, as (JS, Python).
CALLBACK_OPS: dict[str, tuple[str, object]] = {
    "add": ("a + b", lambda a, b: a + b),
    "subtract": ("a - b", lambda a, b: a - b),
    "multiply": ("a * b", lambda a, b: a * b),
}

#: The async functions of page 212: (params, returned expression, oracle).
ASYNC_FNS: dict[str, tuple[str, str, object]] = {
    "total": ("a, b", "a + b", lambda a, b: str(a + b)),
    "area": ("w, h", "w * h", lambda w, h: str(w * h)),
    "double": ("n", "n * 2", lambda n: str(n * 2)),
    "greet": ("name", "`hello ${name}`", lambda name: f"hello {name}"),
    "shout": ("word", "word.toUpperCase()", lambda word: word.upper()),
}

_OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
        "*": lambda a, b: a * b}


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Rendering values ─────────────────────────────────────────


def _int(x) -> str:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: whole numbers only on these pages")
    return str(x)


def _str(s: str) -> str:
    if not isinstance(s, str) or '"' in s or "\\" in s or "`" in s or "${" in s:
        raise ValueError(f"{s!r}: keep strings plain")
    return f'"{s}"'


def _delay(ms) -> str:
    """A timer delay: 0, or a multiple of ten up to fifty.

    Node treats 0 as 1, so 0 and 1 would tie; keeping to tens means two
    different delays always mean two different times.
    """
    _int(ms)
    if ms and (ms % 10 or not 0 < ms <= 50):
        raise ValueError(f"{ms}: delays are 0 or 10, 20 ... 50 ms")
    return str(ms)


def _pairs(rows) -> str:
    return "[" + ", ".join(f"[{_str(n)}, {_delay(ms)}]" for n, ms in rows) + "]"


# ── 1. setTimeout runs later ─────────────────────────────────


def _later(a: dict) -> str:
    return _lines(*(
        f"console.log({_str(word)});" if ms is None
        else f"setTimeout(() => console.log({_str(word)}), {_delay(ms)});"
        for word, ms in a["steps"]
    ))


# ── 2. Callbacks ─────────────────────────────────────────────


def _callback(a: dict) -> str:
    fn = a["fn"]
    body = CALLBACK_OPS[fn][0]
    call = (f"  setTimeout(() => done({body}), 0);" if a["later"]
            else f"  done({body});")
    return _lines(
        f"function {fn}(a, b, done) {{",
        call,
        "}",
        *(f"{fn}({_int(x)}, {_int(y)}, (result) => "
          f"console.log(`{fn} gave ${{result}}`));"
          for x, y in a["calls"]),
        f"console.log({_str(a['word'])});",
    )


# ── 3. new Promise ───────────────────────────────────────────


def _promise(a: dict) -> str:
    v = a["var"]
    value = f"{_int(a['a'])} {a['op']} {_int(a['b'])}"
    if a["op"] not in _OPS:
        raise ValueError(a["op"])
    resolve = (f"  setTimeout(() => resolve({value}), {_delay(a['delay'])});"
               if a.get("delay") is not None else f"  resolve({value});")
    return _lines(
        f"const {v} = new Promise((resolve) => {{",
        f"  console.log({_str(a['inside'])});",
        resolve,
        *([f"  resolve({_int(a['again'])});"] if a.get("again") is not None
          else []),
        "});",
        f"{v}.then((value) => console.log(`{v} resolved with ${{value}}`));",
        f"console.log({_str(a['after'])});",
    )


# ── 4. then chains ───────────────────────────────────────────


def _then(a: dict) -> str:
    steps = [f"  .then((n) => n {op} {_int(k)})" for op, k in a["steps"]]
    for op, _ in a["steps"]:
        if op not in _OPS:
            raise ValueError(op)
    if a.get("forget"):
        op, k = a["forget"]
        steps.append(f"  .then((n) => {{ n {op} {_int(k)}; }})")
    return _lines(
        f"Promise.resolve({_int(a['start'])})",
        *steps,
        f"  .then((n) => console.log(`{_str(a['label'])[1:-1]} ${{n}}`));",
        f"console.log({_str(a['word'])});",
    )


# ── 5. Async functions return promises ───────────────────────


def _asyncfn(a: dict) -> str:
    fn = a["fn"]
    params, body, _ = ASYNC_FNS[fn]
    args = ", ".join(_str(x) if isinstance(x, str) else _int(x)
                     for x in a["args"])
    return _lines(
        f"async function {fn}({params}) {{",
        f"  return {body};",
        "}",
        f"const result = {fn}({args});",
        "console.log(result instanceof Promise);",
        f"result.then((value) => console.log(`{fn} is ${{value}}`));",
        f"console.log(\"called {fn}\");",
    )


# ── 6. await pauses only this function ───────────────────────


def _await(a: dict) -> str:
    return _lines(
        "async function main() {",
        f"  console.log({_str(a['before'])});",
        f"  const n = await Promise.resolve({_int(a['value'])});",
        f"  console.log(`{a['after']} ${{n}}`);",
        "}",
        *(f"console.log({_str(w)});" for w in a["pre"]),
        "main();",
        *(f"console.log({_str(w)});" for w in a["post"]),
    )


# ── 7. try / catch around await ──────────────────────────────


def _trycatch(a: dict) -> str:
    if a["rule"] == "min":
        bad, why = f"n < {_int(a['min'])}", "is too small"
    else:
        bad, why = "n % 2 !== 0", "is odd"
    return _lines(
        f"const inputs = [{', '.join(_int(n) for n in a['inputs'])}];",
        "function check(n) {",
        f"  if ({bad}) return Promise.reject(new Error(`${{n}} {why}`));",
        f"  return Promise.resolve(n * {_int(a['times'])});",
        "}",
        "async function main() {",
        "  for (const n of inputs) {",
        "    try { console.log(`ok ${await check(n)}`); }",
        "    catch (err) { console.log(`caught ${err.message}`); }",
        "  }",
        "}",
        "main();",
    )


# ── 8. A sleep helper, awaited in turn ───────────────────────


def _sleep(a: dict) -> str:
    return _lines(
        f"const steps = {_pairs(a['steps'])};",
        SLEEP,
        "async function main() {",
        "  let waited = 0;",
        "  for (const [name, ms] of steps) {",
        "    await sleep(ms);",
        "    waited += ms;",
        "    console.log(`${name} after ${waited} ms`);",
        "  }",
        "}",
        "main();",
        f"console.log({_str(a['word'])});",
    )


# ── 9. Promise.all ───────────────────────────────────────────


def _all(a: dict) -> str:
    fn = a["fn"]
    give = "name.toUpperCase()" if a["give"] == "upper" else "name.length"
    return _lines(
        f"const jobs = {_pairs(a['jobs'])};",
        SLEEP,
        f"async function {fn}(name, ms) {{",
        "  await sleep(ms);",
        "  console.log(`${name} arrived`);",
        f"  return {give};",
        "}",
        f"const all = Promise.all(jobs.map(([name, ms]) => {fn}(name, ms)));",
        'all.then((results) => console.log(results.join(", ")));',
    )


# ── 10. One by one, or all at once ───────────────────────────


def _parallel(a: dict) -> str:
    data = f"const dishes = {_pairs(a['dishes'])};"
    if a["want"] == "one":
        return _lines(
            data,
            SLEEP,
            "async function main() {",
            "  let clock = 0;",
            "  for (const [name, ms] of dishes) {",
            "    await sleep(ms);",
            "    clock += ms;",
            "    console.log(`${name} ready at ${clock}`);",
            "  }",
            "  console.log(`one by one: ${clock} ms`);",
            "}",
            "main();",
        )
    return _lines(
        data,
        SLEEP,
        "async function cook(name, ms) {",
        "  await sleep(ms);",
        "  console.log(`${name} ready at ${ms}`);",
        "  return ms;",
        "}",
        "Promise.all(dishes.map(([name, ms]) => cook(name, ms))).then((ends) => {",
        "  console.log(`all at once: ${Math.max(...ends)} ms`);",
        "});",
    )


_BUILDERS = {
    "jsa_later": _later,
    "jsa_callback": _callback,
    "jsa_promise": _promise,
    "jsa_then": _then,
    "jsa_asyncfn": _asyncfn,
    "jsa_await": _await,
    "jsa_trycatch": _trycatch,
    "jsa_sleep": _sleep,
    "jsa_all": _all,
    "jsa_parallel": _parallel,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────
#
# A tiny model of node's loop: `now` is what the synchronous code prints,
# in the order it is written; `micro` is what promise callbacks print once
# the synchronous code is done; `timers` fire after that, soonest first,
# ties in the order they were set.


def _timers(rows, start: int = 0) -> list[tuple[int, int, str]]:
    """(fires at, set order, word) — node counts a 0 ms timer as 1 ms."""
    return sorted((start + max(ms, 1), i, w) for i, (w, ms) in enumerate(rows))


def _unique(names) -> None:
    if len(set(names)) != len(names):
        raise ValueError("names must be unique, or the output is ambiguous")


def _distinct_delays(rows) -> None:
    delays = [ms for _, ms in rows]
    for ms in delays:
        _delay(ms)
    if len(set(delays)) != len(delays) or 0 in delays:
        raise ValueError("running at once, the delays must all differ")


def expected_output(shape: str, args: dict, value=None) -> str:
    a = args
    if shape == "jsa_later":
        steps = list(a["steps"])
        now = [w for w, ms in steps if ms is None]
        later = [(w, ms) for w, ms in steps if ms is not None]
        if not now or not later:
            raise ValueError("something now and something later")
        first_later = next(i for i, (_, ms) in enumerate(steps) if ms is not None)
        if all(ms is not None for _, ms in steps[first_later:]):
            raise ValueError("a timer must be written above a plain line")
        _unique([w for w, _ in steps])
        for _, ms in later:
            _delay(ms)
        return NL.join(now + [w for _, _, w in _timers(later)])
    if shape == "jsa_callback":
        fn = CALLBACK_OPS[a["fn"]][1]
        results = [f"{a['fn']} gave {fn(x, y)}" for x, y in a["calls"]]
        if not results:
            raise ValueError("one call at least")
        return NL.join(
            [a["word"]] + results if a["later"] else results + [a["word"]])
    if shape == "jsa_promise":
        # resolve runs once; a second call is ignored.
        got = _OPS[a["op"]](a["a"], a["b"])
        if a.get("again") is not None and a.get("delay") is not None:
            raise ValueError("a second resolve only means something "
                             "straight after the first")
        return NL.join([a["inside"], a["after"],
                        f"{a['var']} resolved with {got}"])
    if shape == "jsa_then":
        n = a["start"]
        for op, k in a["steps"]:
            n = _OPS[op](n, k)
        if not a["steps"]:
            raise ValueError("one then that returns a value at least")
        shown = "undefined" if a.get("forget") else str(n)
        return NL.join([a["word"], f"{a['label']} {shown}"])
    if shape == "jsa_asyncfn":
        fn = a["fn"]
        got = ASYNC_FNS[fn][2](*a["args"])
        return NL.join(["true", f"called {fn}", f"{fn} is {got}"])
    if shape == "jsa_await":
        pre, post = list(a["pre"]), list(a["post"])
        if not post:
            raise ValueError("something after main() shows the pause")
        _unique(pre + post + [a["before"]])
        return NL.join(pre + [a["before"]] + post
                       + [f"{a['after']} {a['value']}"])
    if shape == "jsa_trycatch":
        out = []
        for n in a["inputs"]:
            bad = n < a["min"] if a["rule"] == "min" else n % 2 != 0
            if bad:
                why = "is too small" if a["rule"] == "min" else "is odd"
                out.append(f"caught {n} {why}")
            else:
                out.append(f"ok {n * a['times']}")
        if not any(o.startswith("ok") for o in out) or not any(
                o.startswith("caught") for o in out):
            raise ValueError("some pass and some are caught")
        return NL.join(out)
    if shape == "jsa_sleep":
        steps = list(a["steps"])
        _unique([n for n, _ in steps])
        out, waited = [a["word"]], 0
        for name, ms in steps:
            _delay(ms)
            waited += ms
            out.append(f"{name} after {waited} ms")
        if len(steps) < 2 or waited > 100:
            raise ValueError("two steps at least, and under 100 ms in all")
        return NL.join(out)
    if shape == "jsa_all":
        jobs = list(a["jobs"])
        _unique([n for n, _ in jobs])
        _distinct_delays(jobs)
        finished = [w for _, _, w in _timers(jobs)]
        if finished == [n for n, _ in jobs]:
            raise ValueError("finish in a different order than asked")
        results = [n.upper() if a["give"] == "upper" else str(len(n))
                   for n, _ in jobs]
        return NL.join([f"{w} arrived" for w in finished]
                       + [", ".join(results)])
    if shape == "jsa_parallel":
        dishes = list(a["dishes"])
        _unique([n for n, _ in dishes])
        if len(dishes) < 2:
            raise ValueError("two dishes at least")
        if a["want"] == "one":
            out, clock = [], 0
            for name, ms in dishes:
                _delay(ms)
                clock += ms
                out.append(f"{name} ready at {clock}")
            if clock > 100:
                raise ValueError("under 100 ms in all")
            return NL.join(out + [f"one by one: {clock} ms"])
        _distinct_delays(dishes)
        out = [f"{w} ready at {t}" for t, _, w in _timers(dishes)]
        return NL.join(out + [f"all at once: {max(ms for _, ms in dishes)} ms"])
    raise KeyError(shape)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "jsa_later": Cost(
        "O(n)",
        "Linear in the number of lines, n: each plain line runs once and "
        "each timer fires once. Waiting is not work — while a timer is "
        "pending, node is free to run everything else."),
    "jsa_callback": Cost(
        "O(n)",
        "Linear in the number of calls, n: each call does one sum and calls "
        "its callback once. Handing the result to a function costs the "
        "same as returning it; only when it arrives changes."),
    "jsa_promise": Cost(
        "O(1)",
        "Constant: one promise, one resolve, one then. The executor runs "
        "straight away, inside new Promise, and the then callback runs "
        "once, later — never twice, however often resolve is called."),
    "jsa_then": Cost(
        "O(n)",
        "Linear in the number of then steps, n: each is one small function "
        "call, and each one returns a new promise for the next to wait on."),
    "jsa_asyncfn": Cost(
        "O(1)",
        "Constant: one call and one returned promise. The async keyword "
        "adds no loop — it only wraps whatever is returned in a promise."),
    "jsa_await": Cost(
        "O(1)",
        "Constant: a fixed handful of lines. await does not spin or poll; "
        "it parks the rest of the function in the queue and lets the code "
        "outside carry on."),
    "jsa_trycatch": Cost(
        "O(n)",
        "Linear in the number of inputs, n: one check and one await each. "
        "A rejection costs no more than a success — catch is just the "
        "other path out of the same await."),
    "jsa_sleep": Cost(
        "O(n)",
        "Linear in the number of steps, n, in work; in waiting time, the "
        "sum of all the delays, because each await sleep starts only when "
        "the one before has finished."),
    "jsa_all": Cost(
        "O(n)",
        "Linear in the number of jobs, n: map starts each one once and "
        "Promise.all collects each result once. The waiting overlaps, so "
        "it takes as long as the slowest job, not the sum."),
    "jsa_parallel": Cost(
        "O(n)",
        "Linear work either way. The difference is the waiting: one by one "
        "takes the sum of the delays, all at once takes the largest one. "
        "Same work, far less time — when the jobs do not depend on each "
        "other."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
