"""More JavaScript crashes.

The second set, same rules as `content.py`: every message and line was
copied from what Node printed through `engine_report`, and
tests/test_js_errors_predict.py holds them to it. They go in the three
families the first set opened.

These lean toward what a page meets once it talks to a server — a
field the response did not include, an object where an array was
expected — plus a few that come from the language itself: a var
function called too early, a length that is not a length, a class
called like a function.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c


JS_CRASHES_2: tuple[Crash, ...] = (
    _c(
        id="err-js-nested-missing-field",
        level=2,
        name="A field the response left out",
        family="Nothing there",
        code=(
            "const res = { id: 7, customer: { name: 'Ada' } };\n"
            "const name = res.customer.name;\n"
            "const city = res.customer.address.city;\n"
            "console.log(name, city);"
        ),
        message=(
            "TypeError: Cannot read properties of undefined (reading 'city')"
        ),
        line=3,
        meaning="res.customer.address was undefined",
        decoys=(
            "res.customer was undefined when line 3 ran",
            "The address has no field called city",
            "The response had not finished loading",
        ),
        fix=(
            "Read the message against the chain: it was reading 'city', "
            "so the thing just before .city — res.customer.address — was "
            "undefined. customer was fine, or line 2 would have failed "
            "first. The server simply did not send an address, and a "
            "missing key on an object gives undefined rather than an "
            "error, one step before the crash. For a field that may be "
            "absent, `res.customer.address?.city` answers undefined "
            "instead of throwing; then decide what to show for it."
        ),
    ),
    _c(
        id="err-js-map-on-object",
        level=2,
        name="An object where the array should be",
        family="The wrong kind of thing",
        code=(
            "const res = { results: [1, 2, 3], page: 1 };\n"
            "const doubled = res.map(n => n * 2);\n"
            "console.log(doubled);"
        ),
        message="TypeError: res.map is not a function",
        line=2,
        meaning="res is an object, and objects have no map",
        decoys=(
            "map was given an arrow instead of a function",
            "The results array inside res was empty",
            "map is spelled differently in this version of JavaScript",
        ),
        fix=(
            "'x.map is not a function' almost always means x is not an "
            "array. Here the list is one level down, in res.results — "
            "the envelope a lot of APIs wrap their data in. Log the "
            "response once and look at its shape before mapping it: "
            "`res.results.map(...)`. When the shape is unsure, "
            "`Array.isArray(x)` is the question to ask first."
        ),
    ),
    _c(
        id="err-js-var-function-early",
        level=3,
        name="A function stored in a var, called too soon",
        family="Names",
        code=(
            "greet('Ada');\n"
            "\n"
            "var greet = function (name) {\n"
            "  console.log('Hello, ' + name);\n"
            "};"
        ),
        message="TypeError: greet is not a function",
        line=1,
        meaning="greet exists but is still undefined on line 1",
        decoys=(
            "greet is not declared anywhere in the program",
            "Functions cannot take a string as their argument",
            "The function body on line 4 has an error in it",
        ),
        fix=(
            "It is not a ReferenceError, which is the clue: the name "
            "greet exists. A var is created at the top of the file "
            "holding undefined, and only gets the function when line 3 "
            "runs — so line 1 calls undefined. A `function greet(name) "
            "{...}` declaration is hoisted whole and would have worked. "
            "Either use a declaration, or call it after the assignment."
        ),
    ),
    _c(
        id="err-js-invalid-array-length",
        level=3,
        name="A length below zero",
        family="The wrong kind of thing",
        code=(
            "const count = 5 - 7;\n"
            "const slots = new Array(count);\n"
            "console.log(slots.length);"
        ),
        message="RangeError: Invalid array length",
        line=2,
        meaning="count is -2, and a length cannot be negative",
        decoys=(
            "new Array cannot be given a variable, only a number",
            "Arrays must have at least one item in them",
            "count was a string, not a number",
        ),
        fix=(
            "A RangeError means the value was the right type but outside "
            "what is allowed: a number, but not one that can be a length. "
            "Lengths are whole numbers from 0 up, so a negative or a "
            "fraction (2.5) fails the same way. Clamp it first — "
            "`Math.max(0, count)` — or find why the subtraction went the "
            "wrong way round, which is usually the real bug."
        ),
    ),
    _c(
        id="err-js-class-without-new",
        level=4,
        name="A class called like a function",
        family="The wrong kind of thing",
        code=(
            "class Cart {\n"
            "  constructor() { this.items = []; }\n"
            "}\n"
            "const cart = Cart();\n"
            "console.log(cart.items);"
        ),
        message=(
            "TypeError: Class constructor Cart cannot be invoked without 'new'"
        ),
        line=4,
        meaning="Cart is a class, so it has to be called with new",
        decoys=(
            "The constructor on line 2 is missing a return",
            "cart.items was read before it was set",
            "Classes must be declared below the code using them",
        ),
        fix=(
            "The message says exactly this: a class constructor, invoked "
            "without new. `new Cart()` makes a fresh object, runs the "
            "constructor with this pointing at it, and hands it back; a "
            "class refuses to run any other way. Older code used plain "
            "functions as constructors and forgetting new silently set "
            "things on the global object — classes made it an error."
        ),
    ),
    _c(
        id="err-js-set-on-undefined",
        level=4,
        name="Setting a field on nothing",
        family="Nothing there",
        code=(
            "const totals = {};\n"
            "totals.march.sales = 10;\n"
            "console.log(totals);"
        ),
        message="TypeError: Cannot set properties of undefined (setting 'sales')",
        line=2,
        meaning="totals.march did not exist yet",
        decoys=(
            "totals was declared const, so it cannot change",
            "sales must be declared before it can be set",
            "An empty object cannot be given new fields",
        ),
        fix=(
            "Setting, not reading — but the same rule: the value in "
            "front of .sales was undefined. JavaScript will make a "
            "missing field for you on assignment, but only one level: "
            "totals.march = ... works, totals.march.sales = ... has "
            "nothing to put sales on. Make the middle object first, "
            "`totals.march ??= {}`, then set the field on it."
        ),
    ),
)
