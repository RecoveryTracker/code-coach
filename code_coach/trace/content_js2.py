"""More JavaScript moments.

The second JavaScript set, same rule as `content.py`: every expected
value was read off the tracer rather than reasoned about, and
tests/test_trace_js2.py keeps reading it.

Most go into the existing families. Four are about what array and
object operations hand back and share, which is none of aliasing,
loops or scope exactly, so they get a family of their own.

The tracer quirks that shaped them:

- The first statement of a callback is stopped on twice per call, so
  the reduce moment gives the callback two statements and asks about
  the first, which is then stopped on exactly once per call.
- Functions render as strings, so the closure moments ask about the
  number a call returned rather than the function holding it.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t

OBJECTS = "Objects and arrays"
LOOPS = "Going round"
SCOPE = "What is in scope"


JS_TRACES_2: tuple[Trace, ...] = (
    _t(
        id="trace-js-push-returns-length",
        level=1,
        name="What push hands back",
        family=OBJECTS,
        code=(
            "const tags = ['a', 'b'];\n"
            "const n = tags.push('c');\n"
            "console.log(n);"
        ),
        at_line=3,
        occurrence=1,
        variable="n",
        expect="3",
        decoys=("['a', 'b', 'c']", "'c'", "2"),
        why=(
            "push changes the array in place and returns the new length, "
            "not the array and not the item added. So n is 3, a plain "
            "number. People reach for `const bigger = list.push(x)` "
            "expecting a list and get a count instead — then "
            "`bigger.map` blows up two lines later. concat or a spread "
            "returns an array; push returns how long it now is."
        ),
    ),
    _t(
        id="trace-js-destructure-swap",
        level=2,
        name="Swapping with destructuring",
        family=OBJECTS,
        code=(
            "let a = 1;\n"
            "let b = 2;\n"
            "[a, b] = [b, a];\n"
            "console.log(a, b);"
        ),
        at_line=4,
        occurrence=1,
        variable="a",
        expect="2",
        decoys=("1", "[2, 1]", "[1, 2]"),
        why=(
            "The right-hand side is built first: `[b, a]` is a brand new "
            "array holding 2 and 1 before anything is assigned. Then it "
            "is unpacked into a and b, so a gets 2 and b gets 1. No temp "
            "variable needed, and no risk of the classic `a = b; b = a` "
            "mistake where both end up 2. a is a number, not an array — "
            "the brackets on the left are a pattern, not a value."
        ),
    ),
    _t(
        id="trace-js-while-continue",
        level=2,
        name="Skipping with continue",
        family=LOOPS,
        code=(
            "const out = [];\n"
            "let i = 0;\n"
            "while (i < 6) {\n"
            "  i++;\n"
            "  if (i % 2 === 1) continue;\n"
            "  out.push(i);\n"
            "}\n"
            "console.log(out);"
        ),
        at_line=6,
        occurrence=3,
        variable="out",
        expect="[2, 4]",
        decoys=("[2, 4, 6]", "[1, 3]", "[2]"),
        why=(
            "continue jumps back to the loop test and skips the push, so "
            "odd numbers never go in. Line 6 is only reached for 2, 4 "
            "and 6 — the third arrival is for 6, and the question stops "
            "before it runs, so out holds 2 and 4. The increment is "
            "above the continue on purpose: put it below and the loop "
            "never gets past 1."
        ),
    ),
    _t(
        id="trace-js-assign-order",
        level=3,
        name="Merging objects",
        family=OBJECTS,
        code=(
            "const defaults = { theme: 'light', size: 12 };\n"
            "const prefs = { theme: 'dark' };\n"
            "const opts = Object.assign({}, defaults, prefs);\n"
            "console.log(opts);"
        ),
        at_line=4,
        occurrence=1,
        variable="opts",
        expect="{ theme: 'dark', size: 12 }",
        decoys=(
            "{ theme: 'light', size: 12 }",
            "{ theme: 'dark' }",
            "{ size: 12, theme: 'dark' }",
        ),
        why=(
            "Object.assign copies each source into the target left to "
            "right, so a key that appears twice ends up with the last "
            "value written: prefs comes after defaults and its theme "
            "wins. size is only in defaults, so it survives. And the key "
            "keeps the position it was first written in, which is why "
            "theme still comes first. `{ ...defaults, ...prefs }` "
            "follows exactly the same rule."
        ),
    ),
    _t(
        id="trace-js-reduce-midway",
        level=3,
        name="Inside reduce, part way through",
        family=LOOPS,
        code=(
            "const nums = [4, 1, 3, 2];\n"
            "const total = nums.reduce((acc, n) => {\n"
            "  const sum = acc + n;\n"
            "  return sum;\n"
            "}, 10);\n"
            "console.log(total);"
        ),
        at_line=3,
        occurrence=3,
        variable="acc",
        expect="15",
        decoys=("18", "8", "5", "14"),
        why=(
            "acc starts at the 10 passed as reduce's second argument, "
            "not at 0 and not at the first item. Each call's return "
            "becomes the next call's acc: 10, then 14, then 15. The "
            "third time line 3 is about to run, n is 3 and acc is still "
            "15 — the 3 has not been added yet. 8 is what you get if you "
            "forget the starting 10; 18 is one step too far."
        ),
    ),
    _t(
        id="trace-js-closure-counter",
        level=3,
        name="A counter that remembers",
        family=SCOPE,
        code=(
            "function makeCounter() {\n"
            "  let count = 0;\n"
            "  return () => ++count;\n"
            "}\n"
            "const next = makeCounter();\n"
            "next();\n"
            "const seen = next();\n"
            "console.log(seen);"
        ),
        at_line=8,
        occurrence=1,
        variable="seen",
        expect="2",
        decoys=("1", "0", "3"),
        why=(
            "makeCounter has returned, but its count did not disappear: "
            "the arrow function closes over it and keeps it alive. Every "
            "call to next bumps the same count. The first call made it "
            "1 and its result was thrown away; the second made it 2 and "
            "that is what seen holds. Call makeCounter again and you get "
            "a separate count starting from 0."
        ),
    ),
    _t(
        id="trace-js-spread-nested",
        level=4,
        name="A copy with an array inside",
        family=OBJECTS,
        code=(
            "const a = [1, [2, 3]];\n"
            "const b = [...a];\n"
            "b[0] = 9;\n"
            "b[1].push(4);\n"
            "console.log(a);"
        ),
        at_line=5,
        occurrence=1,
        variable="a",
        expect="[1, [2, 3, 4]]",
        decoys=("[1, [2, 3]]", "[9, [2, 3, 4]]", "[9, [2, 3]]"),
        why=(
            "The spread copies one level deep. b is a new outer array, so "
            "putting 9 in b[0] leaves a[0] alone. But its second slot "
            "holds the very same inner array a does — the copy copied "
            "the reference, not the contents — so pushing 4 through b "
            "shows up in a too. Half changed, half not: that is a "
            "shallow copy. structuredClone copies all the way down."
        ),
    ),
    _t(
        id="trace-js-var-in-closures",
        level=5,
        name="Closures made in a var loop",
        family=SCOPE,
        code=(
            "const fns = [];\n"
            "for (var i = 0; i < 3; i++) {\n"
            "  fns.push(() => i);\n"
            "}\n"
            "const got = fns[0]();\n"
            "console.log(got);"
        ),
        at_line=6,
        occurrence=1,
        variable="got",
        expect="3",
        decoys=("0", "2", "1"),
        why=(
            "var gives the whole function one i, not one per time round. "
            "All three arrow functions close over that same i, and they "
            "are called after the loop has finished and left it at 3 — "
            "so the first one says 3, not 0. Change var to let and each "
            "iteration gets its own i, and fns[0]() says 0. This is the "
            "reason let was added."
        ),
    ),
)
