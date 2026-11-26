"""The code magnet puzzles in TypeScript.

The same puzzle as the other languages: the lines of a working program,
jumbled, to be put back in an order that prints the right thing. In
TypeScript the order is also held to the type checker - the engine runs
`tsc --strict` first and refuses a program with a type error - so a type
used before it is declared is fine (types are hoisted) but a `const` read
above its line, or a narrowing check placed after the line that needed it,
fails.

The expected output beside each was typed by a person and is held to what
the program prints by tests/test_magnets_ts.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "TypeScript"

TS_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-ts-typed-function",
        plan=(
            ("A function with typed inputs and output", 3),
            ("Use it on two prices", 2),
            ("Show the total", 1),
        ),
        level=1,
        name="A function with types",
        family=FAMILY,
        language="typescript",
        note=(
            "`(price: number, rate: number): number` says what goes in and "
            "what comes out; the compiler checks every call against it. The "
            "function is declared with `function`, so it could sit below its "
            "calls, but the consts are read in order: `total` needs both "
            "`a` and `b` made first."
        ),
        code=(
            "function withTax(price: number, rate: number): number {\n"
            "  return Math.round(price * (1 + rate));\n"
            "}\n"
            "const a = withTax(100, 0.2);\n"
            "const b = withTax(50, 0.2);\n"
            "console.log(\"total\", a + b);"
        ),
        expect="total 180",
    ),
    _m(
        id="magnet-ts-interface",
        plan=(
            ("Describe a user", 4),
            ("A function that greets one", 3),
            ("Make a user and greet them", 2),
        ),
        level=1,
        name="An interface and an object that fits it",
        family=FAMILY,
        language="typescript",
        note=(
            "An interface describes a shape: which properties, of which "
            "types. `age?` means it may be left out, so the object does not "
            "need one. Types are erased before the program runs and can be "
            "declared anywhere in the file, but the object itself is a const "
            "and has to exist before `greet` is called with it."
        ),
        code=(
            "interface User {\n"
            "  name: string;\n"
            "  age?: number;\n"
            "}\n"
            "function greet(user: User): string {\n"
            "  return `Hello, ${user.name}` + (user.age ? ` (${user.age})` : \"\");\n"
            "}\n"
            "const ada: User = { name: \"Ada\" };\n"
            "console.log(greet(ada), greet({ name: \"Bo\", age: 9 }));"
        ),
        expect="Hello, Ada Hello, Bo (9)",
    ),
    _m(
        id="magnet-ts-union-narrowing",
        plan=(
            ("A function that takes two kinds of thing", 1),
            ("Handle text", 3),
            ("Handle a list", 2),
            ("Try both", 1),
        ),
        level=2,
        name="Narrowing a union with typeof",
        family=FAMILY,
        language="typescript",
        note=(
            "`string | string[]` is either one. Inside the if, typeof has "
            "proved it is a string, so `.toUpperCase()` compiles; after the "
            "if has returned, only the array is left, so `.join` compiles. "
            "Swap the two returns and the compiler refuses: it would be "
            "calling join on something that might be a string."
        ),
        code=(
            "function shout(x: string | string[]): string {\n"
            "  if (typeof x === \"string\") {\n"
            "    return x.toUpperCase();\n"
            "  }\n"
            "  return x.map((s) => s.toUpperCase()).join(\" \");\n"
            "}\n"
            "console.log(shout(\"hi\"), \"/\", shout([\"a\", \"b\"]));"
        ),
        expect="HI / A B",
    ),
    _m(
        id="magnet-ts-class",
        plan=(
            ("A class with a private balance", 3),
            ("Put money in and say what is there", 4),
            ("Close the class", 1),
            ("Open an account and use it", 2),
        ),
        level=2,
        name="A class with private state",
        family=FAMILY,
        language="typescript",
        note=(
            "`private balance` can only be touched by the class's own "
            "methods, so the outside world goes through `deposit`. "
            "`constructor(readonly owner: string)` makes owner a field in one "
            "line. A class is not hoisted the way a function is: `new "
            "Account` above the class line fails at runtime."
        ),
        code=(
            "class Account {\n"
            "  private balance = 0;\n"
            "  constructor(readonly owner: string) {}\n"
            "  deposit(amount: number): string {\n"
            "    this.balance += amount;\n"
            "    return `${this.owner} has ${this.balance}`;\n"
            "  }\n"
            "}\n"
            "const acct = new Account(\"Ada\");\n"
            "console.log(acct.deposit(5), \"/\", acct.deposit(10));"
        ),
        expect="Ada has 5 / Ada has 15",
    ),
    _m(
        id="magnet-ts-generic",
        plan=(
            ("A function that works for any type", 3),
            ("Use it on numbers and on words", 2),
            ("Show both", 1),
        ),
        level=3,
        name="A generic function",
        family=FAMILY,
        language="typescript",
        note=(
            "`<T>` is a type parameter: whatever kind of array you hand "
            "`last`, it hands back that kind of item, or undefined. So `n` "
            "is a number | undefined and `w` a string | undefined, and the "
            "compiler knows which. One function, checked separately for each "
            "use."
        ),
        code=(
            "function last<T>(items: T[]): T | undefined {\n"
            "  return items[items.length - 1];\n"
            "}\n"
            "const n = last([3, 1, 4]);\n"
            "const w = last([\"x\", \"y\"]);\n"
            "console.log(n, w, last([]));"
        ),
        expect="4 y undefined",
    ),
    _m(
        id="magnet-ts-discriminated-union",
        plan=(
            ("Two kinds of shape, told apart by kind", 3),
            ("Work out the area of either", 8),
            ("Measure one of each", 1),
        ),
        level=3,
        name="A discriminated union",
        family=FAMILY,
        language="typescript",
        note=(
            "Each shape carries a `kind` with a fixed value, and switching on "
            "it narrows the shape: inside `case \"circle\"` the compiler knows "
            "there is a radius. The type lines can go anywhere, since types "
            "are hoisted, but each case's return has to sit under its own "
            "case or it measures the wrong shape."
        ),
        code=(
            "type Circle = { kind: \"circle\"; r: number };\n"
            "type Square = { kind: \"square\"; side: number };\n"
            "type Shape = Circle | Square;\n"
            "function area(s: Shape): number {\n"
            "  switch (s.kind) {\n"
            "    case \"circle\":\n"
            "      return Math.round(Math.PI * s.r * s.r);\n"
            "    case \"square\":\n"
            "      return s.side * s.side;\n"
            "  }\n"
            "}\n"
            "console.log(area({ kind: \"circle\", r: 2 }), area({ kind: \"square\", side: 3 }));"
        ),
        expect="13 9",
    ),
    _m(
        id="magnet-ts-record-count",
        plan=(
            ("Some words and an empty tally", 2),
            ("Count each word", 3),
            ("Show the tally", 1),
        ),
        level=3,
        name="Counting into a Record",
        family=FAMILY,
        language="typescript",
        note=(
            "`Record<string, number>` is an object whose keys are strings and "
            "values numbers. `(counts[w] ?? 0) + 1` starts a new word at 0: "
            "`??` replaces the undefined a missing key gives. The tally has "
            "to exist before the loop writes to it, and the print has to wait "
            "until the loop is done."
        ),
        code=(
            "const words = [\"to\", \"be\", \"or\", \"not\", \"to\", \"be\"];\n"
            "const counts: Record<string, number> = {};\n"
            "for (const w of words) {\n"
            "  counts[w] = (counts[w] ?? 0) + 1;\n"
            "}\n"
            "console.log(JSON.stringify(counts));"
        ),
        expect='{"to":2,"be":2,"or":1,"not":1}',
    ),
    _m(
        id="magnet-ts-async",
        plan=(
            ("A pause that resolves later", 2),
            ("An async task that waits for it", 5),
            ("Start it and say so", 2),
        ),
        level=4,
        name="async and await",
        family=FAMILY,
        language="typescript",
        note=(
            "`await` pauses `run` until the promise settles, but it does not "
            "pause anything else: `main` carries on, so \"started\" prints "
            "while run is waiting. `Promise<void>` is the type of a promise "
            "that settles with nothing. The const `wait` has to be defined "
            "before run is called, because consts are not hoisted."
        ),
        code=(
            "const wait = (ms: number): Promise<void> =>\n"
            "  new Promise((done) => setTimeout(done, ms));\n"
            "async function run(): Promise<void> {\n"
            "  console.log(\"one\");\n"
            "  await wait(10);\n"
            "  console.log(\"two\");\n"
            "}\n"
            "run();\n"
            "console.log(\"started\");"
        ),
        expect="one\nstarted\ntwo",
    ),
    _m(
        id="magnet-ts-readonly-map",
        plan=(
            ("A list of prices that cannot be changed", 1),
            ("Make new lists from it", 2),
            ("Show the old and the new", 2),
        ),
        level=4,
        name="readonly arrays and map",
        family=FAMILY,
        language="typescript",
        note=(
            "`readonly number[]` forbids push, sort and anything else that "
            "would change the array, so the only way forward is methods that "
            "make a new one: map, filter, a spread. Each new list needs the "
            "old one to exist first; the two new lists do not depend on each "
            "other."
        ),
        code=(
            "const prices: readonly number[] = [5, 20, 12];\n"
            "const doubled = prices.map((p) => p * 2);\n"
            "const sorted = [...prices].sort((a, b) => a - b);\n"
            "console.log(prices.join(\",\"), doubled.join(\",\"));\n"
            "console.log(sorted.join(\",\"));"
        ),
        expect="5,20,12 10,40,24\n5,12,20",
    ),
    _m(
        id="magnet-ts-error-result",
        plan=(
            ("A result that is either a value or an error", 3),
            ("Parse a number without throwing", 4),
            ("Use the result safely", 4),
        ),
        level=5,
        name="A Result type instead of throwing",
        family=FAMILY,
        language="typescript",
        note=(
            "`ok: true` and `ok: false` are literal types, so checking "
            "`r.ok` narrows `r` to one side: only then does `r.value` "
            "compile. It forces every caller to handle the failure, which a "
            "thrown error does not. The check has to come before the line "
            "that reads value, or the compiler refuses."
        ),
        code=(
            "type Result =\n"
            "  | { ok: true; value: number }\n"
            "  | { ok: false; error: string };\n"
            "function parse(text: string): Result {\n"
            "  const n = Number(text);\n"
            "  return Number.isNaN(n) ? { ok: false, error: `bad: ${text}` } : { ok: true, value: n };\n"
            "}\n"
            "for (const t of [\"7\", \"x\"]) {\n"
            "  const r = parse(t);\n"
            "  console.log(r.ok ? r.value * 2 : r.error);\n"
            "}"
        ),
        expect="14\nbad: x",
    ),
)
