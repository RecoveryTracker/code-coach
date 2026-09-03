"""JavaScript-only shapes, sixth batch: newer methods, bigger numbers, and
the order things actually happen in.

at() with a negative index. The copying array methods that finally
arrived - toSorted, toReversed and with. The number checks, where
Number.isNaN and the global isNaN disagree. BigInt. yield* delegation.
for await...of. Object.fromEntries. matchAll. Then the event loop: a
promise callback runs before a zero-millisecond timer, always. And
finally, which runs whichever way the function left.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_at", "counting from the end"),
    Shape("js_immutable_array", "sorting and reversing without damage"),
    Shape("js_number_checks", "the two isNaNs, and the safe limit"),
    Shape("js_bigint", "numbers past what a double can hold"),
    Shape("js_yield_star", "one generator handing on to another"),
    Shape("js_for_await", "waiting on each value in turn"),
    Shape("js_from_entries", "an object taken apart and rebuilt"),
    Shape("js_matchall", "every match, with its groups"),
    Shape("js_microtask", "what runs before what"),
    Shape("js_finally", "the block that runs either way"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _at(a: dict) -> str:
    return _lines(
        "const numbers = [" + _nums(a["items"]) + "];",
        f"const word = {_q(a['word'])};",
        "",
        "console.log(numbers.at(-1));",
        f"console.log(numbers.at({a['index']}));",
        "console.log(word.at(-1));",
        "console.log(numbers[numbers.length - 1]);",
    )


def _immutable_array(a: dict) -> str:
    return _lines(
        "const numbers = [" + _nums(a["items"]) + "];",
        "const sorted = numbers.toSorted((a, b) => a - b);",
        "const reversed = numbers.toReversed();",
        f"const changed = numbers.with(0, {a['replacement']});",
        "",
        'console.log(sorted.join(", "));',
        'console.log(reversed.join(", "));',
        'console.log(changed.join(", "));',
        'console.log(numbers.join(", "));',
    )


def _number_checks(a: dict) -> str:
    return _lines(
        f"console.log(Number.isNaN({_q(a['text'])}));",
        f"console.log(isNaN({_q(a['text'])}));",
        f"console.log(Number.isInteger({a['whole']}));",
        f"console.log(Number.isInteger({a['fraction']}));",
        "console.log(",
        "  Number.MAX_SAFE_INTEGER + 1 === Number.MAX_SAFE_INTEGER + 2,",
        ");",
    )


def _bigint(a: dict) -> str:
    return _lines(
        f"const big = {a['value']}n;",
        "",
        f"console.log((big + {a['added']}n).toString());",
        "console.log(typeof big);",
        "try {",
        f"  console.log(big + {a['added']});",
        "} catch (problem) {",
        "  console.log(problem.constructor.name);",
        "}",
    )


def _yield_star(a: dict) -> str:
    return _lines(
        "function* inner() {",
        *[f"  yield {n};" for n in a["inner"]],
        "}",
        "",
        "function* outer() {",
        f"  yield {a['first']};",
        "  yield* inner();",
        f"  yield {a['last']};",
        "}",
        "",
        'console.log([...outer()].join(", "));',
    )


def _for_await(a: dict) -> str:
    return _lines(
        f"async function* {a['name']}(limit) {{",
        "  for (let n = 1; n <= limit; n += 1) {",
        f"    yield {a['expr']};",
        "  }",
        "}",
        "",
        "async function main() {",
        f"  for await (const n of {a['name']}({a['limit']})) {{",
        "    console.log(n);",
        "  }",
        "}",
        "",
        "main();",
    )


def _from_entries(a: dict) -> str:
    pairs = ", ".join(f"{k}: {v}" for k, v in a["pairs"])
    return _lines(
        "const scores = { " + pairs + " };",
        "const pairs = Object.entries(scores);",
        "const changed = Object.fromEntries(",
        f"  pairs.map(([key, value]) => [key, value * {a['times']}]),",
        ");",
        "",
        "console.log(pairs.length);",
        f"console.log(changed.{a['pairs'][0][0]});",
        'console.log(Object.keys(changed).sort().join(", "));',
    )


def _matchall(a: dict) -> str:
    return _lines(
        f"const text = {_q(a['text'])};",
        "const found = [...text.matchAll(/[a-z](\\d+)/g)];",
        "",
        "console.log(found.length);",
        'console.log(found.map((m) => m[1]).join(", "));',
        f'console.log(text.replace(/\\d+/g, {_q(a["instead"])}));',
    )


def _microtask(a: dict) -> str:
    return _lines(
        f"console.log({_q(a['first'])});",
        f"setTimeout(() => console.log({_q(a['timer'])}), 0);",
        f"Promise.resolve().then(() => console.log({_q(a['promise'])}));",
        f"console.log({_q(a['last'])});",
    )


def _finally_block(a: dict) -> str:
    return _lines(
        "function check(n) {",
        "  try {",
        f"    if ({a['test']}) {{",
        f"      throw new Error({_q(a['message'])});",
        "    }",
        f"    return {_q(a['fine'])};",
        "  } catch {",
        f"    return {_q(a['caught'])};",
        "  } finally {",
        f"    console.log({_q(a['always'])});",
        "  }",
        "}",
        "",
        f"console.log(check({a['good']}));",
        f"console.log(check({a['bad']}));",
    )


_JS = {
    "js_at": _at,
    "js_immutable_array": _immutable_array,
    "js_number_checks": _number_checks,
    "js_bigint": _bigint,
    "js_yield_star": _yield_star,
    "js_for_await": _for_await,
    "js_from_entries": _from_entries,
    "js_matchall": _matchall,
    "js_microtask": _microtask,
    "js_finally": _finally_block,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _JS[shape](args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_at":
        items = list(a["items"])
        lines = [
            str(items[-1]),
            str(items[a["index"]]),
            a["word"][-1],
            str(items[-1]),
        ]
    elif shape == "js_immutable_array":
        items = list(a["items"])
        if items == sorted(items):
            raise ValueError("the list must start unsorted")
        changed = [a["replacement"], *items[1:]]
        lines = [
            ", ".join(str(n) for n in sorted(items)),
            ", ".join(str(n) for n in reversed(items)),
            ", ".join(str(n) for n in changed),
            # None of the three touched the original.
            ", ".join(str(n) for n in items),
        ]
    elif shape == "js_number_checks":
        # Number.isNaN asks "is this the NaN value"; the global isNaN asks
        # "does this become NaN if I convert it", which is a different
        # question with a different answer.
        lines = ["false", "true", "true", "false", "true"]
    elif shape == "js_bigint":
        lines = [
            str(a["value"] + a["added"]),
            "bigint",
            "TypeError",
        ]
    elif shape == "js_yield_star":
        whole = [a["first"], *a["inner"], a["last"]]
        lines = [", ".join(str(n) for n in whole)]
    elif shape == "js_for_await":
        lines = [
            str(value(a["expr"], {"n": n, **_TOOLS}))
            for n in range(1, a["limit"] + 1)
        ]
    elif shape == "js_from_entries":
        held = dict(a["pairs"])
        lines = [
            str(len(held)),
            str(held[a["pairs"][0][0]] * a["times"]),
            ", ".join(sorted(held)),
        ]
    elif shape == "js_matchall":
        found = a["text"].split()
        digits = [word[1:] for word in found]
        lines = [
            str(len(found)),
            ", ".join(digits),
            " ".join(word[0] + a["instead"] for word in found),
        ]
    elif shape == "js_microtask":
        # Both callbacks are scheduled before either runs. The promise is a
        # microtask and goes first; the timer waits for the next turn.
        lines = [a["first"], a["last"], a["promise"], a["timer"]]
    elif shape == "js_finally":
        good = value(a["test"], {"n": a["good"], **_TOOLS})
        bad = value(a["test"], {"n": a["bad"], **_TOOLS})
        if good or not bad:
            raise ValueError("one call must throw and the other must not")
        # finally runs before the return is handed back, both times.
        lines = [a["always"], a["fine"], a["always"], a["caught"]]
    else:
        raise KeyError(shape)
    return NL.join(lines)
