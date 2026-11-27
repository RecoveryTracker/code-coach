"""A second set of TypeScript code magnets.

The first set (content_ts.py) covers a typed function, an interface, a
typeof narrowing, a class with a private field, a generic function, a
discriminated union, a Record tally, async, readonly arrays and a Result
type. These are ten shapes it lacks: a tuple returned and destructured, an
enum in a switch, a constructor parameter property, a type guard, a Map
tally, reduce with an initial value, optional chaining with a fallback, an
abstract class and its subclass, and a generic class.

The engine runs `tsc --strict` before node, so an arrangement that reads a
`const`, enum or class above its line is refused by the compiler. The
expected output beside each was worked out by hand and is held to what the
program prints by tests/test_magnets_ts2.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "TypeScript"

TS_MAGNETS_2: tuple[Magnet, ...] = (
    _m(
        id="magnet-ts2-interface-area",
        plan=(
            ("Describe a box", 4),
            ("A function for its area", 3),
            ("Make one", 1),
            ("Show the area", 1),
        ),
        level=1,
        name="An interface and a function that takes it",
        family=FAMILY,
        language="typescript",
        note=(
            "The interface says a Box has a width and a height, both numbers, "
            "and `area(b: Box)` accepts anything of that shape. Types are "
            "erased before the program runs, so the interface and the "
            "function could swap places, but `box` is a const: reading it in "
            "the console.log above its own line is a compile error."
        ),
        code=(
            "interface Box {\n"
            "  w: number;\n"
            "  h: number;\n"
            "}\n"
            "function area(b: Box): number {\n"
            "  return b.w * b.h;\n"
            "}\n"
            "const box: Box = { w: 3, h: 4 };\n"
            "console.log(\"area\", area(box));"
        ),
        expect="area 12",
    ),
    _m(
        id="magnet-ts2-tuple-destructure",
        plan=(
            ("A function that returns a pair", 3),
            ("Some numbers", 1),
            ("Split the pair into two names", 1),
            ("Show them", 1),
        ),
        level=1,
        name="A tuple returned and destructured",
        family=FAMILY,
        language="typescript",
        note=(
            "`[number, number]` is a tuple: exactly two numbers, in a fixed "
            "order, so `const [lo, hi]` knows which is which. The data has "
            "to exist before it is handed to `minMax`, and `lo` and `hi` "
            "have to exist before the print reads them; each const above its "
            "reader, or the compiler refuses."
        ),
        code=(
            "function minMax(xs: number[]): [number, number] {\n"
            "  return [Math.min(...xs), Math.max(...xs)];\n"
            "}\n"
            "const nums = [4, 9, 2, 7];\n"
            "const [lo, hi] = minMax(nums);\n"
            "console.log(lo, hi, hi - lo);"
        ),
        expect="2 9 7",
    ),
    _m(
        id="magnet-ts2-enum-switch",
        plan=(
            ("Name the two lights", 1),
            ("Open a function and switch on the light", 2),
            ("Say what each light means", 4),
            ("Close both", 2),
            ("Try it", 1),
        ),
        level=2,
        name="An enum used in a switch",
        family=FAMILY,
        language="typescript",
        note=(
            "An enum numbers its members from 0, so Red is 0 and Green is 1 "
            "(the last number printed). Unlike an interface, an enum is a "
            "real value that exists at runtime, so it has to be declared "
            "before the line that uses it. Each `return` has to sit under "
            "its own `case`, or the lights mean the wrong thing."
        ),
        code=(
            "enum Light { Red, Green }\n"
            "function act(l: Light): string {\n"
            "  switch (l) {\n"
            "    case Light.Red:\n"
            "      return \"stop\";\n"
            "    case Light.Green:\n"
            "      return \"go\";\n"
            "  }\n"
            "}\n"
            "console.log(act(Light.Green), act(Light.Red), Light.Green);"
        ),
        expect="go stop 1",
    ),
    _m(
        id="magnet-ts2-param-property",
        plan=(
            ("Open a class with a count and a step", 3),
            ("A method that steps the count", 4),
            ("Close the class", 1),
            ("Make a counter", 1),
            ("Tick, then show", 2),
        ),
        level=2,
        name="A constructor parameter property",
        family=FAMILY,
        language="typescript",
        note=(
            "`constructor(private step: number) {}` declares the field and "
            "fills it in one line. `tick` adds first and returns after, so "
            "the `return` has to be the last line of the method. In main the "
            "bare `c.tick()` has to come before the print: the print's own "
            "`c.tick()` is then the second tick, and `c.count` is read "
            "after it, left to right."
        ),
        code=(
            "class Counter {\n"
            "  count = 0;\n"
            "  constructor(private step: number) {}\n"
            "  tick(): number {\n"
            "    this.count += this.step;\n"
            "    return this.count;\n"
            "  }\n"
            "}\n"
            "const c = new Counter(5);\n"
            "c.tick();\n"
            "console.log(c.tick(), c.count);"
        ),
        expect="10 10",
    ),
    _m(
        id="magnet-ts2-type-guard",
        plan=(
            ("A check that proves a type", 3),
            ("Mixed items and a running total", 2),
            ("Add only the numbers", 5),
            ("Show the total", 1),
        ),
        level=3,
        name="A type guard function",
        family=FAMILY,
        language="typescript",
        note=(
            "`x is number` is a promise to the compiler: when `isNum` "
            "returns true, the value is a number. Only inside the `if` is "
            "`it` narrowed from unknown to number, so `total += it` has to "
            "sit under the check; above it the compiler refuses to add an "
            "unknown. The total is a `let` that must exist before the loop."
        ),
        code=(
            "function isNum(x: unknown): x is number {\n"
            "  return typeof x === \"number\";\n"
            "}\n"
            "const items: unknown[] = [1, \"two\", 3, null];\n"
            "let total = 0;\n"
            "for (const it of items) {\n"
            "  if (isNum(it)) {\n"
            "    total += it;\n"
            "  }\n"
            "}\n"
            "console.log(total);"
        ),
        expect="4",
    ),
    _m(
        id="magnet-ts2-map-tally",
        plan=(
            ("Some words and an empty tally", 2),
            ("Count each word", 3),
            ("Print the tally in order", 3),
        ),
        level=3,
        name="Counting words with a Map",
        family=FAMILY,
        language="typescript",
        note=(
            "A Map remembers the order its keys were first added, so the "
            "print goes a, b, c, not alphabetical by accident. `tally.get(w) "
            "?? 0` stands in for a missing word. The count loop has to run "
            "before the print loop: swap them and the tally is still empty "
            "when it is printed, so nothing is printed at all."
        ),
        code=(
            "const words = [\"a\", \"b\", \"a\", \"c\", \"a\", \"b\"];\n"
            "const tally = new Map<string, number>();\n"
            "for (const w of words) {\n"
            "  tally.set(w, (tally.get(w) ?? 0) + 1);\n"
            "}\n"
            "for (const [w, n] of tally) {\n"
            "  console.log(w, n);\n"
            "}"
        ),
        expect="a 3\nb 2\nc 1",
    ),
    _m(
        id="magnet-ts2-reduce",
        plan=(
            ("The digits", 1),
            ("Fold them three ways", 3),
            ("Show the results", 1),
        ),
        level=4,
        name="reduce with an initial value",
        family=FAMILY,
        language="typescript",
        note=(
            "`reduce(fn, start)` carries an accumulator through the array. "
            "The start is the value before the first item, so it has to "
            "suit the job: 0 for adding, and 1 for multiplying (start the "
            "product at 0 and the answer is 0). Building a number with "
            "`acc * 10 + d` depends on the digit order. Each const has to "
            "exist before the print reads it."
        ),
        code=(
            "const digits = [4, 2, 7];\n"
            "const value = digits.reduce((acc, d) => acc * 10 + d, 0);\n"
            "const sum = digits.reduce((acc, d) => acc + d, 0);\n"
            "const product = digits.reduce((acc, d) => acc * d, 1);\n"
            "console.log(value, sum, product);"
        ),
        expect="427 13 56",
    ),
    _m(
        id="magnet-ts2-optional-chaining",
        plan=(
            ("Describe a profile with optional parts", 4),
            ("Two people, one with no address", 4),
            ("Print each with a fallback city", 3),
        ),
        level=4,
        name="Optional chaining with a default",
        family=FAMILY,
        language="typescript",
        note=(
            "`address?` and `city?` may each be missing. `p.address?.city` "
            "stops at the first missing piece and gives undefined instead of "
            "crashing, and `?? \"unknown\"` swaps that undefined for a "
            "fallback. The people print in the order they sit in the array, "
            "and the array has to be built before the loop reads it."
        ),
        code=(
            "interface Profile {\n"
            "  name: string;\n"
            "  address?: { city?: string };\n"
            "}\n"
            "const people: Profile[] = [\n"
            "  { name: \"Ada\", address: { city: \"Rome\" } },\n"
            "  { name: \"Bo\" },\n"
            "];\n"
            "for (const p of people) {\n"
            "  console.log(p.name, p.address?.city ?? \"unknown\");\n"
            "}"
        ),
        expect="Ada Rome\nBo unknown",
    ),
    _m(
        id="magnet-ts2-abstract-class",
        plan=(
            ("An abstract base class", 5),
            ("A subclass that fills the gap", 3),
            ("Make one and speak", 2),
        ),
        level=5,
        name="An abstract class and a subclass",
        family=FAMILY,
        language="typescript",
        note=(
            "An abstract class promises a method (`sound`) without writing "
            "it, and `speak` already uses it; a subclass has to supply it. "
            "Unlike an interface, a class exists at runtime and is not "
            "hoisted: `class Dog extends Animal` placed above `Animal` is a "
            "compile error, and `new Dog` above Dog's class is too."
        ),
        code=(
            "abstract class Animal {\n"
            "  constructor(protected name: string) {}\n"
            "  abstract sound(): string;\n"
            "  speak(): string { return `${this.name} says ${this.sound()}`; }\n"
            "}\n"
            "class Dog extends Animal {\n"
            "  sound(): string { return \"woof\"; }\n"
            "}\n"
            "const d = new Dog(\"Rex\");\n"
            "console.log(d.speak());"
        ),
        expect="Rex says woof",
    ),
    _m(
        id="magnet-ts2-generic-stack",
        plan=(
            ("A stack class for any type", 5),
            ("Make a stack of words", 1),
            ("Push two words", 2),
            ("Pop three times", 1),
        ),
        level=5,
        name="A generic class",
        family=FAMILY,
        language="typescript",
        note=(
            "`Stack<T>` is written once and checked per use: `Stack<string>` "
            "only takes strings and `pop` gives back string | undefined. A "
            "stack is last in, first out, so pushing \"a\" then \"b\" pops "
            "b first, and the third pop finds it empty. Swap the two pushes "
            "and the answer swaps; push before the stack exists and it does "
            "not compile."
        ),
        code=(
            "class Stack<T> {\n"
            "  private items: T[] = [];\n"
            "  push(x: T): void { this.items.push(x); }\n"
            "  pop(): T | undefined { return this.items.pop(); }\n"
            "}\n"
            "const s = new Stack<string>();\n"
            "s.push(\"a\");\n"
            "s.push(\"b\");\n"
            "console.log(s.pop(), s.pop(), s.pop());"
        ),
        expect="b a undefined",
    ),
)
