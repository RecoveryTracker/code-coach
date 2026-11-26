"""TypeScript errors: the type checker's refusals.

TypeScript's errors arrive before anything runs. The engine runs
`tsc --strict` and stops on the first error, which reads:

    file.ts(2,1): error TS2322: Type 'string' is not assignable to type 'number'.

the line and column in brackets, then the error's number and its sentence.
The sentence is recorded here and the line is its own question. Runtime
crashes are left to the JavaScript set: they are JavaScript's, and the line
Node reports is a line of the compiled .js, not of the program you wrote.

Every message and line was copied from what tsc printed, and
tests/test_errors_ts.py holds them to a real compile.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

TS = "TypeScript"


TS_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-ts-wrong-type",
        level=1,
        name="Text into a number",
        family=TS,
        language="typescript",
        code=(
            "let count: number = 5;\n"
            "count = \"five\";\n"
            "console.log(count);"
        ),
        message="error TS2322: Type 'string' is not assignable to type 'number'.",
        line=2,
        meaning="count was declared a number, and \"five\" is a string",
        decoys=(
            "let variables cannot be given a second value",
            "console.log cannot print a variable that has a type",
            "Numbers must be written in words in TypeScript",
        ),
        fix=(
            "'X is not assignable to type Y' is TypeScript's most common "
            "sentence: you tried to put an X where only a Y may go. The "
            "declared type wins - count is a number for good. Assign a "
            "number, `count = 5;`, or if it really can be either, say so: "
            "`let count: number | string`."
        ),
    ),
    _c(
        id="err-ts-property-typo",
        level=1,
        name="A property spelled wrong",
        family=TS,
        language="typescript",
        code=(
            "const names: string[] = [\"ann\", \"bo\"];\n"
            "console.log(names.lenght);"
        ),
        message=("error TS2551: Property 'lenght' does not exist on type 'string[]'. "
                 "Did you mean 'length'?"),
        line=2,
        meaning="Arrays have no property called lenght; the compiler suggests length",
        decoys=(
            "names is empty, so it has no properties yet",
            "Properties cannot be read inside console.log",
            "A string[] has to be turned into a list first",
        ),
        fix=(
            "In plain JavaScript names.lenght is just undefined and the bug "
            "hides; TypeScript knows every property a string[] has and "
            "refuses the one that is not there. The 'Did you mean' is the "
            "fix: names.length."
        ),
    ),
    _c(
        id="err-ts-const",
        level=1,
        name="Changing a const",
        family=TS,
        language="typescript",
        code=(
            "const limit = 10;\n"
            "limit = 20;\n"
            "console.log(limit);"
        ),
        message="error TS2588: Cannot assign to 'limit' because it is a constant.",
        line=2,
        meaning="limit was declared with const, so it can never be given a new value",
        decoys=(
            "20 is larger than the limit that was set",
            "limit has no type written next to it, so TypeScript does not know what it may be changed to",
            "A number cannot be assigned after it has been printed",
        ),
        fix=(
            "const means the NAME can never point at anything else. JavaScript "
            "would throw a TypeError when the line ran; TypeScript stops it "
            "before. If it has to change, declare it with let. If it should "
            "not, the mistake is the second line."
        ),
    ),
    _c(
        id="err-ts-wrong-argument",
        level=1,
        name="The wrong kind of argument",
        family=TS,
        language="typescript",
        code=(
            "function double(n: number): number {\n"
            "  return n * 2;\n"
            "}\n"
            "console.log(double(\"4\"));"
        ),
        message="error TS2345: Argument of type 'string' is not assignable to parameter of type 'number'.",
        line=4,
        meaning="double expects a number, and \"4\" in quotes is a string",
        decoys=(
            "double returns a number, which console.log cannot print",
            "n * 2 is not allowed on a parameter",
            "A function has to be declared after it is called",
        ),
        fix=(
            "The error is on the CALL, not in the function: the function is "
            "fine and was given the wrong thing. JavaScript would quietly "
            "work out \"4\" * 2 as 8 here, and the same mistake with + would "
            "give \"44\". Pass a number: double(4), or Number(text) if it "
            "came from input."
        ),
    ),
    _c(
        id="err-ts-arity",
        level=2,
        name="A call one argument short",
        family=TS,
        language="typescript",
        code=(
            "function area(w: number, h: number): number {\n"
            "  return w * h;\n"
            "}\n"
            "console.log(area(3));"
        ),
        message="error TS2554: Expected 2 arguments, but got 1.",
        line=4,
        meaning="area needs both a width and a height, and the call gave only one",
        decoys=(
            "area returns its answer before it multiplies",
            "3 is not a valid width",
            "Two parameters cannot both be numbers, so the second one is ignored and the call looks short",
        ),
        fix=(
            "In JavaScript the missing h is undefined and 3 * undefined is "
            "NaN - no error, just a wrong answer later. TypeScript counts. "
            "Pass both, or make the second optional with a default: "
            "`h: number = w` makes area(3) a square."
        ),
    ),
    _c(
        id="err-ts-implicit-any",
        level=2,
        name="A parameter with no type",
        family=TS,
        language="typescript",
        code=(
            "function shout(word) {\n"
            "  return word.toUpperCase();\n"
            "}\n"
            "console.log(shout(\"hi\"));"
        ),
        message="error TS7006: Parameter 'word' implicitly has an 'any' type.",
        line=1,
        meaning="word has no type written, and strict mode will not assume any",
        decoys=(
            "toUpperCase does not exist on strings in TypeScript",
            "A function that returns something must say what type it returns",
            "shout is a reserved word",
        ),
        fix=(
            "Without a type, a parameter would be `any`: anything goes and "
            "nothing is checked, which is JavaScript with extra steps. Strict "
            "mode refuses to guess. Say what it is: `function shout(word: "
            "string)`. Return types can usually be left for TypeScript to "
            "work out; parameter types cannot."
        ),
    ),
    _c(
        id="err-ts-possibly-undefined",
        level=2,
        name="An optional property used as if it were there",
        family=TS,
        language="typescript",
        code=(
            "interface User {\n"
            "  name: string;\n"
            "  age?: number;\n"
            "}\n"
            "const u: User = { name: \"Ada\" };\n"
            "console.log(u.age + 1);"
        ),
        message="error TS18048: 'u.age' is possibly 'undefined'.",
        line=6,
        meaning="age is optional, so it may be undefined, and undefined + 1 is not a number",
        decoys=(
            "u was made without an age, so it is not a User at all",
            "name has to come after age in the interface",
            "console.log cannot do arithmetic inside its brackets",
        ),
        fix=(
            "`age?: number` means number OR undefined, and TypeScript makes "
            "you deal with the undefined. Check first - `if (u.age !== "
            "undefined) ...` - or give a fallback: `(u.age ?? 0) + 1`. "
            "In JavaScript this prints NaN."
        ),
    ),
    _c(
        id="err-ts-find-undefined",
        level=2,
        name="Using what find found",
        family=TS,
        language="typescript",
        code=(
            "const users = [{ name: \"Ada\" }, { name: \"Bo\" }];\n"
            "const found = users.find((u) => u.name === \"Cy\");\n"
            "console.log(found.name);"
        ),
        message="error TS18048: 'found' is possibly 'undefined'.",
        line=3,
        meaning="find returns undefined when nothing matches, and there is no Cy",
        decoys=(
            "find can only search arrays of numbers",
            "users has no type, so its items have no name",
            "An arrow function cannot be passed to find",
        ),
        fix=(
            "find's type is 'the item, or undefined', because it might not "
            "find one - and here it really does not. In JavaScript this is "
            "the 'Cannot read properties of undefined' crash; TypeScript "
            "catches it at compile time. Check: `if (found) console.log("
            "found.name);`, or `found?.name`."
        ),
    ),
    _c(
        id="err-ts-missing-property",
        level=2,
        name="An object missing a field",
        family=TS,
        language="typescript",
        code=(
            "interface User {\n"
            "  id: number;\n"
            "  name: string;\n"
            "}\n"
            "const u: User = { name: \"Ada\" };\n"
            "console.log(u);"
        ),
        message=("error TS2741: Property 'id' is missing in type '{ name: string; }' "
                 "but required in type 'User'."),
        line=5,
        meaning="User requires an id, and the object only has a name",
        decoys=(
            "name must be written before id in the object",
            "An interface cannot be used as the type of a const",
            "console.log cannot print an object that has an interface",
        ),
        fix=(
            "Read it as: the thing on the right has type { name: string }, "
            "and that is not enough to be a User, because a User must have "
            "an id. Add it - `{ id: 1, name: \"Ada\" }` - or mark it optional "
            "in the interface, `id?: number`, if a user can exist without one."
        ),
    ),
    _c(
        id="err-ts-excess-property",
        level=3,
        name="A field spelled wrong in an object",
        family=TS,
        language="typescript",
        code=(
            "interface User {\n"
            "  id: number;\n"
            "  name: string;\n"
            "}\n"
            "const u: User = { id: 1, nmae: \"Ada\" };\n"
            "console.log(u);"
        ),
        message=("error TS2353: Object literal may only specify known properties, "
                 "and 'nmae' does not exist in type 'User'."),
        line=5,
        meaning="nmae is not one of User's properties; the name was misspelled",
        decoys=(
            "id has to be a string because name is",
            "Objects with two properties need a class, not an interface",
            "User is declared after u, so it is not known yet",
        ),
        fix=(
            "TypeScript reports the first problem it finds: the unknown nmae. "
            "Fix the spelling and the missing name goes away with it. This "
            "check only applies to an object written out right there - a "
            "literal - which is exactly where a typo in a key is most likely."
        ),
    ),
    _c(
        id="err-ts-no-overlap",
        level=3,
        name="Comparing a string with a number",
        family=TS,
        language="typescript",
        code=(
            "const code: string = \"200\";\n"
            "if (code === 200) {\n"
            "  console.log(\"ok\");\n"
            "}"
        ),
        message=("error TS2367: This comparison appears to be unintentional because "
                 "the types 'string' and 'number' have no overlap."),
        line=2,
        meaning="code is a string and 200 is a number, so === can never be true",
        decoys=(
            "=== cannot be used inside an if",
            "\"200\" is too long to be a status code",
            "console.log needs a type before it can print",
        ),
        fix=(
            "=== never converts, so a string and a number are never equal - "
            "the if could never run, which is almost certainly a bug. "
            "TypeScript notices the types can never match. Compare like with "
            "like: `code === \"200\"`, or convert first: `Number(code) === "
            "200`."
        ),
    ),
    _c(
        id="err-ts-readonly",
        level=3,
        name="Changing a readonly property",
        family=TS,
        language="typescript",
        code=(
            "interface Point {\n"
            "  readonly x: number;\n"
            "}\n"
            "const p: Point = { x: 1 };\n"
            "p.x = 2;\n"
            "console.log(p.x);"
        ),
        message="error TS2540: Cannot assign to 'x' because it is a read-only property.",
        line=5,
        meaning="x is marked readonly in Point, so it can be set when made but never changed",
        decoys=(
            "p is a const, so nothing inside it can ever change, including x and any other property it has",
            "2 is not a valid value for a Point",
            "Interfaces cannot have number properties",
        ),
        fix=(
            "The const is NOT the reason - a const object's properties can "
            "normally change. readonly on the property is. It is a compile-"
            "time promise only: at runtime the object is ordinary. Make a "
            "new point instead: `const q = { ...p, x: 2 };`."
        ),
    ),
    _c(
        id="err-ts-before-declaration",
        level=3,
        name="Using a const above its line",
        family=TS,
        language="typescript",
        code=(
            "console.log(total);\n"
            "const total = 3;"
        ),
        message="error TS2448: Block-scoped variable 'total' used before its declaration.",
        line=1,
        meaning="total is read on line 1 but not declared until line 2",
        decoys=(
            "total has no type written next to it, so TypeScript will not let console.log print it",
            "A const has to be given a value of at least 10",
            "console.log has to be the last line of a program",
        ),
        fix=(
            "let and const exist only from their line onwards; reading one "
            "earlier is a ReferenceError in JavaScript, and TypeScript "
            "reports it before running. Functions declared with `function` "
            "are different - they can be called above their line. Move the "
            "const up."
        ),
    ),
    _c(
        id="err-ts-missing-return",
        level=4,
        name="A function that does not always return",
        family=TS,
        language="typescript",
        code=(
            "function grade(score: number): string {\n"
            "  if (score >= 50) {\n"
            "    return \"pass\";\n"
            "  }\n"
            "}\n"
            "console.log(grade(70));"
        ),
        message=("error TS2366: Function lacks ending return statement and return type "
                 "does not include 'undefined'."),
        line=1,
        meaning="A score under 50 reaches the end with no return, but the type promises a string",
        decoys=(
            "grade(70) is over 50, so the function is never called properly",
            "if blocks cannot contain a return",
            "The return type has to be written as String with a capital S",
        ),
        fix=(
            "The call with 70 would work - TypeScript is not looking at the "
            "call, it is looking at every path through the function. Under "
            "50 there is no return, so it would hand back undefined, which is "
            "not a string. Add the missing case: `return \"fail\";` at the end."
        ),
    ),
    _c(
        id="err-ts-uninitialized-field",
        level=4,
        name="A class field never set",
        family=TS,
        language="typescript",
        code=(
            "class Box {\n"
            "  label: string;\n"
            "  size = 1;\n"
            "}\n"
            "console.log(new Box().size);"
        ),
        message=("error TS2564: Property 'label' has no initializer and is not "
                 "definitely assigned in the constructor."),
        line=2,
        meaning="label promises to be a string, but nothing ever gives it a value",
        decoys=(
            "size has to be declared before label",
            "A class needs at least one method",
            "new Box() needs an argument for every field the class has, and it was called with none",
        ),
        fix=(
            "label: string says every Box has a string label, but a new Box "
            "would have undefined there. Give it a starting value (`label = "
            "\"\"`), set it in a constructor, or admit it can be missing "
            "(`label?: string`)."
        ),
    ),
)
