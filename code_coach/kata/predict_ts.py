"""Predict the output, in TypeScript.

TypeScript's types are checked and then thrown away: what runs is the
JavaScript underneath. So most of what surprises people is the gap between
the two - `as` that converts nothing, an interface that does not trim
extra properties, `private` that is still there at runtime - plus the few
things TypeScript adds that DO exist at runtime, which is mostly enums and
parameter properties.

Every program here passes `tsc --strict` with no errors (the engine refuses
to run one that does not), and every expected output was typed out first
and then checked against Node by tests/test_predict_ts.py.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

FAMILY = "TypeScript"


TS_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-ts-or-vs-nullish",
        level=1,
        language="typescript",
        name="|| and ?? with a zero",
        family=FAMILY,
        code=(
            "const count: number = 0;\n"
            "const label: string = \"\";\n"
            "console.log(count || 10, count ?? 10);\n"
            "console.log(`[${label || \"none\"}] [${label ?? \"none\"}]`);"
        ),
        expect="10 0\n[none] []",
        why=(
            "`||` falls back on anything falsy, and 0 and \"\" are both falsy, "
            "so it replaces real values. `??` falls back only on null and "
            "undefined. The type says count is a number either way; which "
            "operator you pick decides whether 0 counts as an answer."
        ),
    ),
    _p(
        id="predict-ts-void-return",
        level=1,
        language="typescript",
        name="What a void function hands back",
        family=FAMILY,
        code=(
            "function log(msg: string): void {\n"
            "  console.log(\"log:\", msg);\n"
            "}\n"
            "const got = log(\"hi\");\n"
            "console.log(got, typeof got);"
        ),
        expect="log: hi\nundefined undefined",
        why=(
            "`void` is a promise not to return anything useful, and at "
            "runtime a function that returns nothing returns undefined. The "
            "log line prints first because it runs inside the call, before "
            "`got` is printed."
        ),
    ),
    _p(
        id="predict-ts-enum-numbers",
        level=1,
        language="typescript",
        name="An enum counts from where you start it",
        family=FAMILY,
        code=(
            "enum Size { Small = 1, Medium, Large }\n"
            "enum Color { Red, Green, Blue }\n"
            "console.log(Size.Large, Color.Blue);\n"
            "console.log(Color[1]);"
        ),
        expect="3 2\nGreen",
        why=(
            "A numeric enum counts up by one from the last value given: Small "
            "is 1, so Large is 3. Color starts at 0 by default, so Blue is 2. "
            "Numeric enums also map BACK from number to name, which is why "
            "`Color[1]` is the string \"Green\"."
        ),
    ),
    _p(
        id="predict-ts-tuple",
        level=1,
        language="typescript",
        name="A tuple at runtime",
        family=FAMILY,
        code=(
            "const pair: [string, number] = [\"age\", 36];\n"
            "const [key, value] = pair;\n"
            "console.log(typeof pair, Array.isArray(pair), pair.length);\n"
            "console.log(key.toUpperCase(), value + 1);"
        ),
        expect="object true 2\nAGE 37",
        why=(
            "A tuple type is only a description of an array: two items, a "
            "string then a number. At runtime it is a plain array, so typeof "
            "says object and Array.isArray says true. The type is what lets "
            "`key.toUpperCase()` compile - TypeScript knows the first item is "
            "a string."
        ),
    ),
    _p(
        id="predict-ts-as-converts-nothing",
        level=2,
        language="typescript",
        name="as does not convert",
        family=FAMILY,
        code=(
            "const raw: unknown = \"42\";\n"
            "const n = raw as number;\n"
            "console.log(typeof n, n + 1);\n"
            "const real = Number(raw);\n"
            "console.log(typeof real, real + 1);"
        ),
        expect="string 421\nnumber 43",
        why=(
            "`as number` tells the compiler to treat the value as a number; it "
            "does nothing to the value. It is still the string \"42\", and "
            "\"42\" + 1 joins to \"421\". Number(raw) actually converts. An `as` "
            "is you vouching for a type, and the compiler takes your word for "
            "it."
        ),
    ),
    _p(
        id="predict-ts-nullish-empty",
        level=2,
        language="typescript",
        name="An optional parameter left out",
        family=FAMILY,
        code=(
            "function greet(name?: string): string {\n"
            "  return `[hi ${name ?? \"you\"}]`;\n"
            "}\n"
            "console.log(greet(), greet(\"\"), greet(\"Bo\"));"
        ),
        expect="[hi you] [hi ] [hi Bo]",
        why=(
            "Leaving out an optional parameter makes it undefined, and `??` "
            "replaces undefined with \"you\". An empty string is a real value, "
            "not a missing one, so `??` leaves it alone - hence \"hi \" with "
            "nothing after it. With `||` all three of the first two would say "
            "you."
        ),
    ),
    _p(
        id="predict-ts-structural",
        level=2,
        language="typescript",
        name="An interface does not trim",
        family=FAMILY,
        code=(
            "interface Point { x: number }\n"
            "const full = { x: 1, y: 2, label: \"A\" };\n"
            "const p: Point = full;\n"
            "console.log(JSON.stringify(p));\n"
            "console.log(Object.keys(p).length);"
        ),
        expect='{"x":1,"y":2,"label":"A"}\n3',
        why=(
            "TypeScript checks shape, not exact contents: anything with an x "
            "that is a number fits Point, extra properties and all. And the "
            "type changes nothing at runtime - p is the same object as full, "
            "so it still has all three properties. The type only limits what "
            "you may write, `p.y` being an error."
        ),
    ),
    _p(
        id="predict-ts-sort-numbers",
        level=2,
        language="typescript",
        name="Sorting a number[]",
        family=FAMILY,
        code=(
            "const scores: number[] = [10, 9, 100, 1];\n"
            "const asText = [...scores].sort();\n"
            "const asNumbers = [...scores].sort((a, b) => a - b);\n"
            "console.log(asText.join(\" \"));\n"
            "console.log(asNumbers.join(\" \"));"
        ),
        expect="1 10 100 9\n1 9 10 100",
        why=(
            "The type says number[], but sort() with no comparison still "
            "sorts by turning each item into text, where \"10\" comes before "
            "\"9\". Types do not change what built-in methods do. Pass a "
            "comparison - (a, b) => a - b - to sort numbers as numbers."
        ),
    ),
    _p(
        id="predict-ts-getter",
        level=2,
        language="typescript",
        name="A getter runs every time",
        family=FAMILY,
        code=(
            "class Counter {\n"
            "  private n = 0;\n"
            "  get next(): number {\n"
            "    this.n += 1;\n"
            "    return this.n;\n"
            "  }\n"
            "}\n"
            "const c = new Counter();\n"
            "console.log(c.next, c.next, c.next);"
        ),
        expect="1 2 3",
        why=(
            "`c.next` looks like reading a field, but a getter is a method "
            "that runs on every read. Three reads, three calls, three "
            "different answers. A getter with side effects like this one is "
            "legal but surprising, which is exactly why it is worth knowing."
        ),
    ),
    _p(
        id="predict-ts-private-is-there",
        level=3,
        language="typescript",
        name="private is still in the object",
        family=FAMILY,
        code=(
            "class Account {\n"
            "  private balance = 100;\n"
            "  #pin = 1234;\n"
            "  owner = \"Ada\";\n"
            "}\n"
            "const a = new Account();\n"
            "console.log(JSON.stringify(a));\n"
            "console.log(Object.keys(a).join(\",\"));"
        ),
        expect='{"balance":100,"owner":"Ada"}\nbalance,owner',
        why=(
            "TypeScript's `private` is a compile-time rule only: the property "
            "is an ordinary one at runtime, so JSON and Object.keys see it. "
            "`#pin` is JavaScript's own private field, which really is hidden "
            "- it does not show up in either. Use # when it has to stay "
            "secret."
        ),
    ),
    _p(
        id="predict-ts-parameter-properties",
        level=3,
        language="typescript",
        name="Fields made in the constructor's brackets",
        family=FAMILY,
        code=(
            "class User {\n"
            "  constructor(public name: string, readonly id: number, age: number) {\n"
            "    console.log(\"made\", name, age);\n"
            "  }\n"
            "}\n"
            "const u = new User(\"Bo\", 7, 30);\n"
            "console.log(JSON.stringify(u));"
        ),
        expect='made Bo 30\n{"name":"Bo","id":7}',
        why=(
            "A parameter marked public, private, protected or readonly becomes "
            "a field automatically - one of the few TypeScript features that "
            "writes real code. `age` has no marker, so it is just a parameter: "
            "usable inside the constructor and then gone, which is why the "
            "JSON has name and id but no age."
        ),
    ),
    _p(
        id="predict-ts-map-vs-record",
        level=3,
        language="typescript",
        name="Number keys in a Map and in an object",
        family=FAMILY,
        code=(
            "const m = new Map<number, string>();\n"
            "m.set(1, \"one\");\n"
            "const o: Record<number, string> = {};\n"
            "o[1] = \"one\";\n"
            "console.log(m.has(1), [...m.keys()].map((k) => typeof k).join());\n"
            "console.log(Object.keys(o).map((k) => typeof k).join());"
        ),
        expect="true number\nstring",
        why=(
            "A Map keeps keys exactly as given, so the number 1 stays a "
            "number. An object's keys are always strings: `o[1]` stores the "
            "key \"1\". Record<number, string> lets you WRITE number keys, but "
            "the object underneath turns them into text all the same."
        ),
    ),
    _p(
        id="predict-ts-narrowing",
        level=3,
        language="typescript",
        name="Narrowing a union",
        family=FAMILY,
        code=(
            "function size(x: string | number[] | null): number {\n"
            "  if (x === null) return -1;\n"
            "  if (typeof x === \"string\") return x.trim().length;\n"
            "  return x.length;\n"
            "}\n"
            "console.log(size(\"  hi  \"), size([1, 2, 3]), size(null));"
        ),
        expect="2 3 -1",
        why=(
            "Each check narrows the type for the lines after it: past the "
            "null test x cannot be null, past the typeof test it must be an "
            "array. The checks are ordinary JavaScript and really run; "
            "TypeScript just follows them. `trim()` drops the spaces, so the "
            "string's length is 2."
        ),
    ),
    _p(
        id="predict-ts-enum-keys",
        level=4,
        language="typescript",
        name="Looping over an enum",
        family=FAMILY,
        code=(
            "enum Level { Low, High }\n"
            "enum Mode { On = \"ON\", Off = \"OFF\" }\n"
            "console.log(Object.keys(Level).join(\",\"));\n"
            "console.log(Object.keys(Mode).join(\",\"));"
        ),
        expect="0,1,Low,High\nOn,Off",
        why=(
            "A numeric enum is compiled to an object that maps both ways - "
            "Low to 0 AND 0 to \"Low\" - so its keys include the numbers. A "
            "string enum maps one way only, so its keys are just the names. "
            "Looping over a numeric enum without knowing this gives you "
            "everything twice."
        ),
    ),
    _p(
        id="predict-ts-key-order",
        level=4,
        language="typescript",
        name="The order of an object's keys",
        family=FAMILY,
        code=(
            "const stock: Record<string, number> = { b: 1, 20: 2, a: 3, 3: 4 };\n"
            "console.log(Object.keys(stock).join(\",\"));"
        ),
        expect="3,20,b,a",
        why=(
            "Object keys come out in a fixed order that is not the order "
            "written: keys that look like whole numbers first, smallest "
            "first, then every other key in the order it was added. The type "
            "says nothing about order. When order matters, use a Map, which "
            "keeps exactly the order things were set."
        ),
    ),
    _p(
        id="predict-ts-async-order",
        level=4,
        language="typescript",
        name="When an async function's answer arrives",
        family=FAMILY,
        code=(
            "async function load(): Promise<number> {\n"
            "  console.log(\"loading\");\n"
            "  return 7;\n"
            "}\n"
            "load().then((v) => console.log(\"got\", v));\n"
            "console.log(\"asked\");"
        ),
        expect="loading\nasked\ngot 7",
        why=(
            "An async function runs straight away, up to its first await - so "
            "\"loading\" prints during the call. But its answer always arrives "
            "later, as a promise, so `.then` waits until the current code has "
            "finished: \"asked\" comes before \"got 7\" even with nothing slow "
            "in between."
        ),
    ),
    _p(
        id="predict-ts-readonly-array",
        level=5,
        language="typescript",
        name="readonly stops you, not the array",
        family=FAMILY,
        code=(
            "const nums: number[] = [3, 1, 2];\n"
            "const view: readonly number[] = nums;\n"
            "nums.push(4);\n"
            "console.log(view.length, view.join(\"\"));\n"
            "const copy = [...view].sort();\n"
            "console.log(nums.join(\"\"), copy.join(\"\"));"
        ),
        expect="4 3124\n3124 1234",
        why=(
            "`readonly number[]` means YOU may not change the array through "
            "that name - view.push would not compile. It does not freeze the "
            "array, and view is the same array as nums, so a push through "
            "nums shows up in view. Sorting a spread copy leaves the original "
            "alone."
        ),
    ),
)
