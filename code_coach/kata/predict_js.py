"""Predict the output, in JavaScript.

The same question as the Python set and a better fit for this language.
JavaScript has more traps, they bite harder, and one whole family of
them — the order an async program prints in — cannot be worked out by
reading carefully. You either know the rule about microtasks and timers
or you guess, and guessing is wrong about as often as it is right.

That family is the reason this exists. A vanilla app is mostly events
and fetch, which is to say mostly callbacks resolving in an order nobody
wrote down, and the bugs it produces look like the code is haunted until
the rule is in your hands.

Every answer below came from running the snippet through the same runner
the app uses, not from memory. Two of them would have been wrong
otherwise: `this` inside a plain callback is nought here rather than the
TypeError it is in strict mode, and a probe that captured output before
the microtask queue drained reported half an answer for every async one.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

# ── Async ────────────────────────────────────────────────────
#
# The order is always: everything synchronous, then every microtask
# (promises), then the timers. Knowing those three words in that order
# answers all five of these.

ASYNC: tuple[Puzzle, ...] = (
    _p(
        id="js-async-order",
        level=3,
        language="javascript",
        name="Sync, promise, timer",
        family="Async",
        code=(
            'console.log("one");\n'
            'setTimeout(() => console.log("two"), 0);\n'
            'Promise.resolve().then(() => console.log("three"));\n'
            'console.log("four");'
        ),
        expect="one\nfour\nthree\ntwo",
        why=(
            "All the synchronous code runs first, to the end. Then the "
            "microtask queue, which is where a resolved promise's then "
            "goes. Then the timers, and a timeout of zero is still a "
            "timer. That order never changes, so the zero in setTimeout "
            "buys nothing except a place at the back of the queue."
        ),
    ),
    _p(
        id="js-await-order",
        level=3,
        language="javascript",
        name="What await really does",
        family="Async",
        code=(
            "async function go() {\n"
            '  console.log("a");\n'
            "  await null;\n"
            '  console.log("b");\n'
            "}\n"
            "go();\n"
            'console.log("c");'
        ),
        expect="a\nc\nb",
        why=(
            "An async function runs normally until its first await, so "
            "`a` prints straight away. The await then hands control back "
            "to the caller — even awaiting null — and the rest of the "
            "function becomes a microtask. So the line after the call "
            "runs before the line after the await."
        ),
    ),
    _p(
        id="js-promise-chain",
        level=2,
        language="javascript",
        name="Two thens and a timer",
        family="Async",
        code=(
            'Promise.resolve().then(() => console.log("first then"));\n'
            'Promise.resolve().then(() => console.log("second then"));\n'
            'setTimeout(() => console.log("timer"), 0);\n'
            'console.log("sync");'
        ),
        expect="sync\nfirst then\nsecond then\ntimer",
        why=(
            "The same three-stage order, with the microtasks running in "
            "the order they were queued. Every promise callback in the "
            "queue runs before any timer does, however many there are."
        ),
    ),
    _p(
        id="js-await-loop",
        level=4,
        language="javascript",
        name="Awaiting inside a loop",
        family="Async",
        code=(
            "async function go() {\n"
            "  for (const n of [1, 2]) {\n"
            "    await null;\n"
            "    console.log(n);\n"
            "  }\n"
            "}\n"
            "go();\n"
            'console.log("after");'
        ),
        expect="after\n1\n2",
        why=(
            "The first await suspends before anything is printed, so the "
            "caller finishes first. The loop then resumes one turn at a "
            "time through the microtask queue, in order. This is why a "
            "loop full of awaits is sequential rather than parallel — "
            "Promise.all is what runs them together."
        ),
    ),
)


# ── Coercion ─────────────────────────────────────────────────

COERCION: tuple[Puzzle, ...] = (
    _p(
        id="js-plus-minus",
        level=1,
        language="javascript",
        name="Plus is not minus",
        family="Coercion",
        code='console.log("5" + 2, "5" - 2, "5" * "2", [] + {});',
        expect="52 3 10 [object Object]",
        why=(
            "Plus means concatenation as soon as either side is a string, "
            "so it turns the number into text. Minus and times have no "
            "string meaning, so they turn the text into numbers instead. "
            "The last one is both rules at once: an empty array becomes "
            "an empty string and an object becomes [object Object]."
        ),
    ),
    _p(
        id="js-loose-equality",
        level=3,
        language="javascript",
        name="Double equals",
        family="Coercion",
        code='console.log([] == false, "0" == false, null == undefined, NaN == NaN);',
        expect="true true true false",
        why=(
            "Double equals converts before comparing, and the rules are "
            "not transitive or obvious: an empty array becomes an empty "
            "string becomes nought, which equals false. null and "
            "undefined equal each other and nothing else. NaN equals "
            "nothing at all, itself included — Number.isNaN is how you "
            "ask. Triple equals avoids the lot."
        ),
    ),
    _p(
        id="js-typeof",
        level=2,
        language="javascript",
        name="What typeof says",
        family="Coercion",
        code="console.log(typeof null, typeof NaN, typeof [], typeof function () {});",
        expect="object number object function",
        why=(
            "typeof null being object is a bug from 1995 that can never "
            "be fixed without breaking the web. NaN is a number, which is "
            "consistent if unhelpful — it is the numeric value meaning "
            "not a number. And an array is an object: Array.isArray is "
            "the question worth asking."
        ),
    ),
    _p(
        id="js-sort-strings",
        level=2,
        language="javascript",
        name="Sorting numbers",
        family="Coercion",
        code=(
            "console.log([1, 10, 2, 20].sort().join(\",\"));\n"
            "console.log([1, 10, 2, 20].sort((a, b) => a - b).join(\",\"));"
        ),
        expect="1,10,2,20\n1,2,10,20",
        why=(
            "sort with no comparator converts everything to strings and "
            "sorts those, so 10 comes before 2 the way 'ab' comes before "
            "'b'. It is the default because sort predates thinking about "
            "it, and it is why every numeric sort needs the comparator."
        ),
    ),
    _p(
        id="js-float",
        level=1,
        language="javascript",
        name="A tenth plus two tenths",
        family="Coercion",
        code="console.log(0.1 + 0.2 === 0.3, 0.1 + 0.2);",
        expect="false 0.30000000000000004",
        why=(
            "The same binary floating point every language has. "
            "JavaScript has only this one number type, so there is no "
            "integer arithmetic to fall back on and money is usually "
            "held in whole pence for exactly this reason."
        ),
    ),
)


# ── Scope and this ───────────────────────────────────────────

SCOPE: tuple[Puzzle, ...] = (
    _p(
        id="js-var-loop",
        level=3,
        language="javascript",
        name="var in a loop",
        family="Scope and this",
        code=(
            "const out = [];\n"
            "for (var i = 0; i < 3; i++) out.push(() => i);\n"
            'console.log(out.map(f => f()).join(","));'
        ),
        expect="3,3,3",
        why=(
            "var has one binding for the whole function, so all three "
            "closures see the same i — and by the time they run the loop "
            "has finished and left it at 3. This is the single most "
            "common bug in pre-2015 JavaScript and the reason let exists."
        ),
    ),
    _p(
        id="js-let-loop",
        level=1,
        language="javascript",
        name="let in the same loop",
        family="Scope and this",
        code=(
            "const out = [];\n"
            "for (let i = 0; i < 3; i++) out.push(() => i);\n"
            'console.log(out.map(f => f()).join(","));'
        ),
        expect="0,1,2",
        why=(
            "let makes a fresh binding for each turn of the loop, so each "
            "closure captures its own. The same code with one word "
            "changed gives the answer everyone expected from the other "
            "one, which is the whole argument for let."
        ),
    ),
    _p(
        id="js-this-callback",
        level=4,
        language="javascript",
        name="this inside a callback",
        family="Scope and this",
        code=(
            "const counter = {\n"
            "  n: 0,\n"
            "  bump() {\n"
            "    [1, 2].forEach(function () { this.n += 1; });\n"
            "    return this.n;\n"
            "  },\n"
            "};\n"
            "console.log(counter.bump());"
        ),
        expect="0",
        why=(
            "A plain function gets its own this, decided by how it is "
            "called rather than where it was written — and forEach calls "
            "it with none, so outside strict mode this is the global "
            "object. The increments happen, to a global n nobody wanted, "
            "and counter.n never moves. In strict mode the same code "
            "throws instead, which is friendlier."
        ),
    ),
    _p(
        id="js-this-arrow",
        level=2,
        language="javascript",
        name="The same, with an arrow",
        family="Scope and this",
        code=(
            "const counter = {\n"
            "  n: 0,\n"
            "  bump() {\n"
            "    [1, 2].forEach(() => { this.n += 1; });\n"
            "    return this.n;\n"
            "  },\n"
            "};\n"
            "console.log(counter.bump());"
        ),
        expect="2",
        why=(
            "An arrow function has no this of its own and uses the one "
            "from where it was written, which is the method. That is the "
            "whole difference between the two and the reason arrows took "
            "over for callbacks."
        ),
    ),
    _p(
        id="js-hoisting",
        level=3,
        language="javascript",
        name="Before the line that makes it",
        family="Scope and this",
        code=(
            "console.log(typeof later, typeof soon);\n"
            "var later = 1;\n"
            "function soon() {}"
        ),
        expect="undefined function",
        why=(
            "A var is created at the top of its scope and only assigned "
            "where you wrote it, so it exists and holds undefined. A "
            "function declaration is moved up whole and is already "
            "callable. A let or const would have thrown instead, which "
            "is the improvement."
        ),
    ),
)


# ── Objects and arrays ───────────────────────────────────────

SHAPES: tuple[Puzzle, ...] = (
    _p(
        id="js-const-object",
        level=1,
        language="javascript",
        name="What const protects",
        family="Objects and arrays",
        code=(
            "const o = { a: 1 };\n"
            "o.a = 2;\n"
            "o.b = 3;\n"
            "console.log(JSON.stringify(o));"
        ),
        expect='{"a":2,"b":3}',
        why=(
            "const stops the name being pointed at something else. It "
            "says nothing at all about the object it points to, which "
            "can be changed as freely as any other. Object.freeze is the "
            "one that stops that."
        ),
    ),
    _p(
        id="js-spread-shallow",
        level=3,
        language="javascript",
        name="How deep a copy goes",
        family="Objects and arrays",
        code=(
            "const first = { inner: { n: 1 } };\n"
            "const copy = { ...first };\n"
            "copy.inner.n = 9;\n"
            "console.log(first.inner.n, copy.inner.n);"
        ),
        expect="9 9",
        why=(
            "Spread copies one level. The new object has its own inner "
            "property holding the same nested object, so changing "
            "through either is visible through both. structuredClone "
            "copies all the way down."
        ),
    ),
    _p(
        id="js-array-holes",
        level=4,
        language="javascript",
        name="The comma with nothing in it",
        family="Objects and arrays",
        code=(
            "const a = [1, , 3];\n"
            'console.log(a.length, a.map(x => x * 2).join(","), JSON.stringify(a));'
        ),
        expect="3 2,,6 [1,null,3]",
        why=(
            "A hole is not undefined — it is nothing at all. The length "
            "counts it, map skips it and leaves a hole behind, join "
            "writes nothing for it, and JSON has no way to say hole so "
            "it writes null. Four behaviours for one missing value."
        ),
    ),
    _p(
        id="js-json-drops",
        level=3,
        language="javascript",
        name="What JSON leaves out",
        family="Objects and arrays",
        code="console.log(JSON.stringify({ a: undefined, b: () => 1, c: NaN, d: 1 }));",
        expect='{"c":null,"d":1}',
        why=(
            "JSON has no undefined and no functions, so those properties "
            "vanish entirely rather than being written as anything. It "
            "has no NaN either, but a number has to be written, so that "
            "one becomes null. Round-tripping an object through JSON "
            "quietly changes its shape."
        ),
    ),
    _p(
        id="js-string-immutable",
        level=2,
        language="javascript",
        name="Writing into a string",
        family="Objects and arrays",
        code=(
            'const s = "abc";\n'
            's[0] = "z";\n'
            'console.log(s, s.length, [...s].join("-"));'
        ),
        expect="abc 3 a-b-c",
        why=(
            "Strings cannot be changed, and outside strict mode the "
            "assignment is ignored rather than refused — no error, no "
            "effect. They can still be read by index and spread into an "
            "array of characters, which is what to do instead."
        ),
    ),
)


JS_PUZZLES: tuple[Puzzle, ...] = ASYNC + COERCION + SCOPE + SHAPES
