"""Predict the output, in JavaScript, third set.

The same rules as `predict_js.py`: short, correct snippets, and every
answer below was copied from what the app's own runner printed, then
held to it by tests/test_js_errors_predict.py. They go in the families
the first set opened, and ask things neither earlier set did — two
closures from one factory, for...in against for...of, a getter, what
`?.` short-circuits, what an async function hands back, the two
equalities that are not ===, the two isNaNs, and a promise queued from
inside a timer.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


JS_PUZZLES_3: tuple[Puzzle, ...] = (
    _p(
        id="predict-js-closure-counters",
        level=1,
        name="Two counters from one factory",
        family="Scope and this",
        language="javascript",
        code=(
            "function makeCounter() {\n"
            "  let n = 0;\n"
            "  return () => ++n;\n"
            "}\n"
            "const a = makeCounter();\n"
            "const b = makeCounter();\n"
            "a();\n"
            "a();\n"
            "console.log(a(), b());"
        ),
        expect="3 1",
        why=(
            "Each call to makeCounter runs its body again, so each makes "
            "its own n and returns an arrow that keeps hold of that one. "
            "a has been called three times and b once, and they never "
            "share: a closure remembers the variables from the call that "
            "made it, not from the function in general."
        ),
    ),
    _p(
        id="predict-js-for-in-vs-of",
        level=2,
        name="in, or of",
        family="Objects and arrays",
        language="javascript",
        code=(
            "const scores = [10, 20];\n"
            "scores.bonus = 5;\n"
            "const keys = [];\n"
            "for (const k in scores) keys.push(k);\n"
            "const values = [];\n"
            "for (const v of scores) values.push(v);\n"
            "console.log(keys, values);"
        ),
        expect="[ '0', '1', 'bonus' ] [ 10, 20 ]",
        why=(
            "for...in walks an object's property names, and an array is "
            "an object: its indexes are names too — as strings — and so "
            "is anything else stuck on it. for...of asks the array for "
            "its values, which are only the items. Use of for arrays; "
            "in is for plain objects, and even there Object.keys is "
            "usually clearer."
        ),
    ),
    _p(
        id="predict-js-getter",
        level=2,
        name="A property that is worked out each time",
        family="Objects and arrays",
        language="javascript",
        code=(
            "class Box {\n"
            "  constructor(w, h) { this.w = w; this.h = h; }\n"
            "  get area() { return this.w * this.h; }\n"
            "}\n"
            "const box = new Box(2, 3);\n"
            "box.w = 10;\n"
            "console.log(box.area, typeof box.area);"
        ),
        expect="30 number",
        why=(
            "`get` makes area look like a field while running a function "
            "every time it is read — with no brackets. It was never "
            "stored as 6; it is computed from w and h at the moment you "
            "ask, so changing w changes it. And typeof sees the value "
            "the getter returned, not the getter itself."
        ),
    ),
    _p(
        id="predict-js-optional-chaining",
        level=3,
        name="Where ?. stops",
        family="Objects and arrays",
        language="javascript",
        code=(
            "const user = { profile: null };\n"
            "console.log(user.profile?.name);\n"
            "console.log(user.profile?.name.length);\n"
            'console.log(user.settings?.theme ?? "light");'
        ),
        expect="undefined\nundefined\nlight",
        why=(
            "`?.` checks the value on its left, and if that is null or "
            "undefined the whole rest of the chain is skipped and the "
            "answer is undefined — which is why the second line does not "
            "crash on .length even though there is no ?. in front of it. "
            "`??` then swaps undefined or null for a default. Neither "
            "one turns null into null: a skipped chain is undefined."
        ),
    ),
    _p(
        id="predict-js-async-returns-promise",
        level=3,
        name="What an async function returns",
        family="Async",
        language="javascript",
        code=(
            "async function load() {\n"
            "  return 42;\n"
            "}\n"
            "const result = load();\n"
            "console.log(result);\n"
            "result.then(v => console.log(v + 1));"
        ),
        expect="Promise { 42 }\n43",
        why=(
            "An async function always returns a promise, even when its "
            "body returns a plain number straight away. Logging it shows "
            "the promise (Node prints it already settled), not 42; "
            "getting 42 out takes await or then. This is the "
            "`[object Promise]` on a web page, and the `if (await "
            "isReady())` someone wrote as `if (isReady())` — a promise "
            "is always truthy."
        ),
    ),
    _p(
        id="predict-js-object-is",
        level=3,
        name="The equality that is not ===",
        family="Coercion",
        language="javascript",
        code=(
            "console.log(NaN === NaN, Object.is(NaN, NaN));\n"
            "console.log(0 === -0, Object.is(0, -0));\n"
            "console.log([NaN].indexOf(NaN), [NaN].includes(NaN));"
        ),
        expect="false true\ntrue false\n-1 true",
        why=(
            "=== has two exceptions: NaN is not equal to itself, and 0 "
            "and -0 count as equal. Object.is has neither. The array "
            "methods take sides: indexOf compares with === and so can "
            "never find NaN, while includes uses the other rule and "
            "can. If you are looking for NaN in an array, includes."
        ),
    ),
    _p(
        id="predict-js-two-isnans",
        level=4,
        name="isNaN, and Number.isNaN",
        family="Coercion",
        language="javascript",
        code=(
            'console.log(Number.isInteger(5.0), Number.isInteger("5"));\n'
            'console.log(isNaN("abc"), Number.isNaN("abc"));\n'
            'console.log(isNaN(""), Number(""));'
        ),
        expect="true false\ntrue false\nfalse 0",
        why=(
            "There is one number type, so 5.0 is the integer 5. The "
            "Number.* functions do not convert: a string is not an "
            "integer and is not NaN, it is a string. The old global "
            "isNaN converts first — 'abc' becomes NaN, so yes — and an "
            "empty string converts to 0, so an empty form field passes "
            "an isNaN check as a perfectly good number."
        ),
    ),
    _p(
        id="predict-js-microtasks-between-timers",
        level=4,
        name="A promise inside a timer",
        family="Async",
        language="javascript",
        code=(
            "setTimeout(() => {\n"
            '  console.log("timer 1");\n'
            '  Promise.resolve().then(() => console.log("promise"));\n'
            "}, 0);\n"
            'setTimeout(() => console.log("timer 2"), 0);\n'
            'console.log("start");'
        ),
        expect="start\ntimer 1\npromise\ntimer 2",
        why=(
            "The microtask queue is emptied after every task, not once "
            "per round of timers. Each timer callback is its own task, "
            "so the promise queued inside the first one runs as soon as "
            "that callback finishes — before the second timer, even "
            "though both timers were already due."
        ),
    ),
)
