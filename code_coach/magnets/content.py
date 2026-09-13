"""The puzzles.

Every one is a program that runs and prints something definite. The
expected output beside each was typed out by a person; the suite runs
the program and holds the two together, so a puzzle that has stopped
printing what its note claims fails rather than quietly teaching the
wrong lesson.

They are short. A twenty-magnet puzzle is a jigsaw, and the thing worth
practising is which line goes before which, which you get from six
lines as well as from twenty and can then do again twice more.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


# -- Functions and scope --------------------------------------

FUNCTIONS: tuple[Magnet, ...] = (
    _m(
        id="magnet-greet",
        level=1,
        name="Say hello",
        family="Functions and scope",
        note=(
            "The smallest version of the only rule that matters here: "
            "the body goes inside the braces, the closing brace comes "
            "after it, and the call comes last. Everything else in this "
            "family is this shape with more in it."
        ),
        code=(
            "function greet(name) {\n"
            "  return `Hello, ${name}!`;\n"
            "}\n"
            'console.log(greet("Ada"));'
        ),
        expect="Hello, Ada!",
    ),
    _m(
        id="magnet-default-param",
        level=2,
        name="A parameter with a fallback",
        family="Functions and scope",
        note=(
            "A default is used when the argument is missing, not when it "
            "is falsy — passing 0 keeps the 0. That is the difference "
            "between a default parameter and the old `tax = tax || 0.2`, "
            "which would have quietly charged tax on the tax-free order."
        ),
        code=(
            "function price(amount, tax = 0.2) {\n"
            "  return Math.round(amount * (1 + tax));\n"
            "}\n"
            "console.log(price(100));\n"
            "console.log(price(100, 0));"
        ),
        expect="120\n100",
    ),
    _m(
        id="magnet-rest-spread",
        level=3,
        name="Gathering and spreading",
        family="Functions and scope",
        note=(
            "The same three dots doing opposite jobs. In the parameter "
            "list it gathers whatever was passed into an array; at the "
            "call site it spreads an array back out into arguments. The "
            "array has to be declared before the line that spreads it."
        ),
        code=(
            "function total(...amounts) {\n"
            "  return amounts.reduce((sum, n) => sum + n, 0);\n"
            "}\n"
            "const cart = [5, 10, 15];\n"
            "console.log(total(...cart));"
        ),
        expect="30",
    ),
    _m(
        id="magnet-closure-counter",
        level=4,
        name="A counter that remembers",
        family="Functions and scope",
        note=(
            "The returned function keeps the `count` that was alive when "
            "it was made — that is a closure, and it is most of what "
            "makes JavaScript worth learning. Note the two closing "
            "braces and which is which: the inner function's, then the "
            "outer one's."
        ),
        code=(
            "function makeCounter() {\n"
            "  let count = 0;\n"
            "  return function () {\n"
            "    count += 1;\n"
            "    return count;\n"
            "  };\n"
            "}\n"
            "const next = makeCounter();\n"
            "next();\n"
            "console.log(next());"
        ),
        expect="2",
    ),
)


# -- Arrays ---------------------------------------------------

ARRAYS: tuple[Magnet, ...] = (
    _m(
        id="magnet-find-some",
        level=1,
        name="Finding one, asking about all",
        family="Arrays",
        note=(
            "find gives you the item, some gives you a yes or no. "
            "Reaching for find when you wanted some is how you end up "
            "writing `if (users.find(...) !== undefined)`."
        ),
        code=(
            "const users = [\n"
            '  { name: "Ada", admin: false },\n'
            '  { name: "Bo", admin: true },\n'
            "];\n"
            "const admin = users.find((u) => u.admin);\n"
            "console.log(admin.name);\n"
            "console.log(users.some((u) => !u.admin));"
        ),
        expect="Bo\ntrue",
    ),
    _m(
        id="magnet-map-filter",
        level=2,
        name="Filter then map",
        family="Arrays",
        note=(
            "Each step makes a new array and the next step works on it, "
            "so each line has to come after the one it reads. Filtering "
            "first also means mapping over less — the order is a habit "
            "worth having, not just an ordering puzzle."
        ),
        code=(
            "const prices = [4, 12, 7, 20];\n"
            "const big = prices.filter((n) => n > 5);\n"
            "const doubled = big.map((n) => n * 2);\n"
            'console.log(doubled.join(", "));'
        ),
        expect="24, 14, 40",
    ),
    _m(
        id="magnet-sort-comparator",
        level=3,
        name="Sorting numbers properly",
        family="Arrays",
        note=(
            "Without the comparator, sort turns everything into strings "
            "first and puts 100 before 9. The comparator is the whole "
            "lesson; the ordering of the lines is that sort changes the "
            "array in place, so the log has to come after it."
        ),
        code=(
            "const scores = [10, 9, 100, 1];\n"
            "scores.sort((a, b) => a - b);\n"
            'console.log(scores.join(","));'
        ),
        expect="1,9,10,100",
    ),
    _m(
        id="magnet-reduce-longest",
        level=4,
        name="Reduce to one answer",
        family="Arrays",
        note=(
            "reduce carries a running answer through the list. The "
            "second argument to reduce is where it starts, and leaving "
            "it out is the bug: on an empty array reduce with no initial "
            "value throws rather than returning nothing."
        ),
        code=(
            'const words = ["to", "be", "or", "not"];\n'
            "const longest = words.reduce(\n"
            "  (best, word) => (word.length > best.length ? word : best),\n"
            '  "",\n'
            ");\n"
            "console.log(longest);"
        ),
        expect="not",
    ),
)


# -- Objects --------------------------------------------------

OBJECTS: tuple[Magnet, ...] = (
    _m(
        id="magnet-destructure",
        level=2,
        name="Pulling fields out",
        family="Objects",
        note=(
            "Destructuring names the fields you want, and a default "
            "covers the one that is not there. The object has to exist "
            "on an earlier line than the destructuring that reads it."
        ),
        code=(
            'const settings = { theme: "dark", size: 14 };\n'
            'const { theme, weight = "normal" } = settings;\n'
            "console.log(theme, weight);"
        ),
        expect="dark normal",
    ),
    _m(
        id="magnet-spread-merge",
        level=3,
        name="Defaults, then overrides",
        family="Objects",
        note=(
            "Later wins. Swapping the two spreads gives you the "
            "defaults overwriting the user's choices, which is the "
            "single most common way a settings merge goes wrong — and "
            "it looks completely fine in the code."
        ),
        code=(
            'const base = { colour: "red", size: 1 };\n'
            "const custom = { size: 3 };\n"
            "const merged = { ...base, ...custom };\n"
            "console.log(JSON.stringify(merged));"
        ),
        expect='{"colour":"red","size":3}',
    ),
    _m(
        id="magnet-entries",
        level=4,
        name="Walking an object",
        family="Objects",
        note=(
            "Object.entries turns an object into pairs, and destructuring "
            "in the loop header names both halves. The closing brace of "
            "the loop goes after the line inside it — which sounds "
            "obvious until the pieces are in front of you."
        ),
        code=(
            "const counts = { apples: 2, pears: 5 };\n"
            "for (const [fruit, n] of Object.entries(counts)) {\n"
            "  console.log(`${fruit}: ${n}`);\n"
            "}"
        ),
        expect="apples: 2\npears: 5",
    ),
)


# -- Async ----------------------------------------------------

ASYNC: tuple[Magnet, ...] = (
    _m(
        id="magnet-then-chain",
        level=3,
        name="A chain, and the line after it",
        family="Async",
        note=(
            "The last line prints first. Everything in a .then is "
            "queued for after the current run of code finishes, so the "
            "plain console.log below the chain goes first no matter "
            "where it sits. This is the one people do not believe until "
            "they see it."
        ),
        code=(
            "Promise.resolve(2)\n"
            "  .then((n) => n * 3)\n"
            "  .then((n) => console.log(n));\n"
            'console.log("first");'
        ),
        expect="first\n6",
    ),
    _m(
        id="magnet-async-await",
        level=4,
        name="await hands control back",
        family="Async",
        note=(
            "An async function runs like any other until it hits an "
            "await — that is why `start` prints before `after`. At the "
            "await it returns to its caller, so `after` goes next, and "
            "the value comes back last. Three lines, three stages, and "
            "none of them where people expect."
        ),
        code=(
            "async function main() {\n"
            '  console.log("start");\n'
            "  const n = await Promise.resolve(7);\n"
            "  console.log(n);\n"
            "}\n"
            "main();\n"
            'console.log("after");'
        ),
        expect="start\nafter\n7",
    ),
    _m(
        id="magnet-promise-all",
        level=4,
        name="Waiting for both",
        family="Async",
        note=(
            "Promise.all waits for every one and gives you the results "
            "in the order you asked for them, not the order they "
            "finished. Both promises have to be declared above the line "
            "that collects them."
        ),
        code=(
            "const one = Promise.resolve(1);\n"
            "const two = Promise.resolve(2);\n"
            "Promise.all([one, two]).then((both) => {\n"
            '  console.log(both.join("+"));\n'
            "});\n"
            'console.log("waiting");'
        ),
        expect="waiting\n1+2",
    ),
    _m(
        id="magnet-catch",
        level=5,
        name="Where the catch goes",
        family="Async",
        note=(
            "The .catch goes at the end of the chain and covers "
            "everything above it — the .then is skipped entirely. Put "
            "the catch before the then and it guards nothing, which is "
            "how a rejected promise ends up as an unhandled error in the "
            "console of a program that clearly has a catch in it."
        ),
        code=(
            "function risky() {\n"
            '  return Promise.reject(new Error("nope"));\n'
            "}\n"
            "risky()\n"
            '  .then(() => console.log("ok"))\n'
            '  .catch((err) => console.log("caught:", err.message));'
        ),
        expect="caught: nope",
    ),
)
