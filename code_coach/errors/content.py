"""The crashes.

Every message and line number here was copied out of what the engine
actually printed, and the suite runs each program and holds it to that.
The plain-words readings are written by hand, and so are the wrong
options — each of those is a misreading somebody really makes, usually
by blaming something the message does not mention.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c


# -- Nothing there --------------------------------------------

MISSING: tuple[Crash, ...] = (
    _c(
        id="err-prop-of-undefined",
        level=1,
        name="Reading a field off nothing",
        family="Nothing there",
        code=(
            "const users = [];\n"
            "const first = users[0];\n"
            "console.log(first.name);"
        ),
        message=(
            "TypeError: Cannot read properties of undefined (reading 'name')"
        ),
        line=3,
        meaning="The value in front of .name was undefined",
        decoys=(
            "The array users was empty when it was built",
            "There is no field called name on any user",
            "users[0] was never declared as a variable",
        ),
        fix=(
            "The message names the thing immediately before the dot, and "
            "nothing else. `first` was undefined, because taking [0] of "
            "an empty array gives undefined rather than complaining. The "
            "array being empty is why, but it is not what the message "
            "says — and chasing what the message says is faster than "
            "chasing why. Guard it: `if (first) ...`, or `first?.name`."
        ),
    ),
    _c(
        id="err-prop-of-null",
        level=2,
        name="null is not the same as undefined",
        family="Nothing there",
        code=(
            "const found = null;\n"
            "console.log(found.title);"
        ),
        message=(
            "TypeError: Cannot read properties of null (reading 'title')"
        ),
        line=2,
        meaning="The value in front of .title was null",
        decoys=(
            "The value in front of .title was undefined",
            "The field title is spelled wrong here",
            "found was never declared in this scope",
        ),
        fix=(
            "Same shape of message, different word in the middle, and "
            "the difference is worth keeping: undefined usually means "
            "nobody set it, null usually means somebody set it to "
            "nothing on purpose. Which of the two words is in the "
            "message tells you which kind of bug you have — a value that "
            "never arrived, or a value that arrived empty."
        ),
    ),
    _c(
        id="err-method-of-undefined",
        level=3,
        name="Calling something that is not there",
        family="Nothing there",
        code=(
            "const settings = { theme: 'dark' };\n"
            "console.log(settings.getTheme());"
        ),
        message="TypeError: settings.getTheme is not a function",
        line=2,
        meaning="settings.getTheme exists as a lookup but is not callable",
        decoys=(
            "settings is undefined at the point it is used",
            "getTheme was called with the wrong number of arguments",
            "The getTheme function ran and threw an error inside itself",
        ),
        fix=(
            "Read it as two steps, because that is what it did: it "
            "looked up `settings.getTheme`, got undefined, and then "
            "tried to call it. The message blames the calling, not the "
            "lookup — which is why this is the message you get for a "
            "method you spelled wrong, one that does not exist, and one "
            "you forgot to define, all three."
        ),
    ),
    _c(
        id="err-undefined-from-function",
        level=4,
        name="A function that quietly returned nothing",
        family="Nothing there",
        code=(
            "function findUser(id) {\n"
            "  const users = [{ id: 1, name: 'Ada' }];\n"
            "  users.find((u) => u.id === id);\n"
            "}\n"
            "const user = findUser(1);\n"
            "console.log(user.name);"
        ),
        message=(
            "TypeError: Cannot read properties of undefined (reading 'name')"
        ),
        line=6,
        meaning="findUser returned undefined, so user was undefined",
        decoys=(
            "There is no user with id 1 in the users array",
            "find does not work on an array of objects like this",
            "name is not a field on the user that was found",
        ),
        fix=(
            "The crash is on line 6 and the bug is on line 3: the find "
            "runs, works perfectly, and its result is thrown away "
            "because there is no `return` in front of it. A function "
            "with no return gives undefined. This is the gap worth "
            "learning — where it broke and where it went wrong are "
            "different lines, and the message can only ever tell you the "
            "first."
        ),
    ),
)


# -- Names ----------------------------------------------------

NAMES: tuple[Crash, ...] = (
    _c(
        id="err-not-defined",
        level=1,
        name="A name nothing knows",
        family="Names",
        code=(
            "const price = 10;\n"
            "console.log(prcie);"
        ),
        message="ReferenceError: prcie is not defined",
        line=2,
        meaning="Nothing in scope is called prcie",
        decoys=(
            "The variable price has no value yet",
            "The value in price is of the wrong type",
            "console.log cannot print a plain number",
        ),
        fix=(
            "ReferenceError is always about the name, never about the "
            "value — the name was looked up and nothing anywhere "
            "answered to it. Nine times in ten it is a typo, and the "
            "message hands you the misspelling to compare against what "
            "you meant. Read the name in the message, not the line."
        ),
    ),
    _c(
        id="err-before-declared",
        level=3,
        name="Used one line too early",
        family="Names",
        code=(
            "console.log(total);\n"
            "const total = 5;"
        ),
        message=(
            "ReferenceError: Cannot access 'total' before initialization"
        ),
        line=1,
        meaning="total exists here but has not been given its value yet",
        decoys=(
            "There is no variable called total anywhere in scope",
            "A const declaration cannot be printed with console.log at all",
            "total was declared twice and the second one won",
        ),
        fix=(
            "A different message from 'is not defined', and the "
            "difference is the whole lesson: this name is known, it is "
            "just not usable yet. `let` and `const` exist from the top "
            "of their block but cannot be touched until the line that "
            "declares them runs. Move the declaration above the use. "
            "(`var` would have printed undefined instead of crashing, "
            "which is worse.)"
        ),
    ),
    _c(
        id="err-out-of-block",
        level=4,
        name="Gone when the block ended",
        family="Names",
        code=(
            "if (true) {\n"
            "  const message = 'hello';\n"
            "}\n"
            "console.log(message);"
        ),
        message="ReferenceError: message is not defined",
        line=4,
        meaning="message only existed inside the braces above",
        decoys=(
            "The if statement never ran, so nothing was set",
            "message was set to nothing inside the block",
            "console.log cannot print a string constant",
        ),
        fix=(
            "`const` and `let` live and die with their braces. The if "
            "definitely ran — that is what makes this confusing, because "
            "you watched the line execute. Declare it before the block "
            "and assign inside, or return it out."
        ),
    ),
)


# -- The wrong kind of thing ----------------------------------

WRONG_KIND: tuple[Crash, ...] = (
    _c(
        id="err-not-a-function",
        level=2,
        name="A method the value does not have",
        family="The wrong kind of thing",
        code=(
            "const total = 5;\n"
            "console.log(total.toUpperCase());"
        ),
        message="TypeError: total.toUpperCase is not a function",
        line=2,
        meaning="total is a number, and numbers have no toUpperCase",
        decoys=(
            "The method toUpperCase is spelled wrong here",
            "total is undefined at the point it is used",
            "toUpperCase needs an argument that it was not given",
        ),
        fix=(
            "The message tells you the call failed; it does not tell you "
            "the value was a number. That part you get by looking at "
            "what `total` is. This is the everyday version of the "
            "commonest bug in JavaScript — a value is not the type you "
            "assumed, and nothing said so until you used it."
        ),
    ),
    _c(
        id="err-const-assign",
        level=1,
        name="Changing something declared const",
        family="The wrong kind of thing",
        code=(
            "const count = 1;\n"
            "count = 2;\n"
            "console.log(count);"
        ),
        message="TypeError: Assignment to constant variable.",
        line=2,
        meaning="count was declared const, so it cannot be reassigned",
        decoys=(
            "The variable count cannot hold the number 2",
            "count is used on line 2 before it is declared",
            "The contents of what count points at cannot be changed",
        ),
        fix=(
            "const stops the name being pointed at something else. It "
            "does not freeze what it points at — `const list = []` then "
            "`list.push(1)` is fine, and that distinction is the one "
            "people get backwards. If the name genuinely needs to "
            "change, it should have been `let`."
        ),
    ),
    _c(
        id="err-not-iterable",
        level=3,
        name="Looping over something that is not a list",
        family="The wrong kind of thing",
        code=(
            "const counts = { apples: 2, pears: 5 };\n"
            "for (const item of counts) {\n"
            "  console.log(item);\n"
            "}"
        ),
        message="TypeError: counts is not iterable",
        line=2,
        meaning="A plain object cannot be walked with for...of",
        decoys=(
            "The object counts is empty so there is nothing to loop",
            "The variable item was not defined before the loop",
            "The object has the wrong kind of keys for a loop",
        ),
        fix=(
            "for...of walks things that know how to hand out items one "
            "at a time — arrays, strings, Maps, Sets. A plain object "
            "does not. Use Object.keys, Object.values or Object.entries "
            "to turn it into something that does, which is why "
            "`for (const [k, v] of Object.entries(obj))` is the phrase "
            "worth memorising."
        ),
    ),
    _c(
        id="err-json-parse",
        level=4,
        name="Parsing something that is not JSON",
        family="The wrong kind of thing",
        code=(
            "const raw = \"{ name: 'Ada' }\";\n"
            "const data = JSON.parse(raw);\n"
            "console.log(data.name);"
        ),
        message=(
            "SyntaxError: Expected property name or '}' in JSON at "
            "position 2 (line 1 column 3)"
        ),
        line=2,
        meaning="The text is not valid JSON, so parsing stopped at position 2",
        decoys=(
            "The file itself has a syntax error on line 2",
            "data has no field called name after parsing",
            "JSON.parse needs a second argument that was not supplied here",
        ),
        fix=(
            "A SyntaxError that is not about your program — it is about "
            "the text you handed to JSON.parse, and the line and column "
            "in the message count through that text, not your file. JSON "
            "requires double quotes around keys as well as values, so "
            "this needs `{\"name\": \"Ada\"}`. Anything that came off a "
            "network or out of a file deserves a try/catch around the "
            "parse."
        ),
    ),
)
