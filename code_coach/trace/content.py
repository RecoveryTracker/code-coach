"""The moments.

Every expected value was checked against the tracer rather than
reasoned about, and the suite keeps checking. The wrong options are
mostly the value one step earlier, because "I forgot that line had
already run" is the mistake, far more than not knowing what the line
does.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t


# -- One thing, two names -------------------------------------

ALIASING: tuple[Trace, ...] = (
    _t(
        id="trace-alias-array",
        level=2,
        name="Two names, one array",
        family="One thing, two names",
        code=(
            "const a = [1, 2];\n"
            "const b = a;\n"
            "b.push(3);\n"
            "console.log(a.length);"
        ),
        at_line=4,
        occurrence=1,
        variable="a",
        expect="[1, 2, 3]",
        decoys=("[1, 2]", "[3]", "[1, 2, [3]]"),
        why=(
            "`const b = a` does not copy anything. It gives the same "
            "array a second name, so pushing through b changes what a "
            "sees — a was never touched by name and changed anyway. "
            "const stops b being pointed somewhere else; it does not "
            "stop the array being edited. A copy needs `[...a]`."
        ),
    ),
    _t(
        id="trace-copy-array",
        level=3,
        name="The same program with a copy in it",
        family="One thing, two names",
        code=(
            "const a = [1, 2];\n"
            "const b = [...a];\n"
            "b.push(3);\n"
            "console.log(a.length);"
        ),
        at_line=4,
        occurrence=1,
        variable="a",
        expect="[1, 2]",
        decoys=("[1, 2, 3]", "[]", "[1, 2, [3]]"),
        why=(
            "One character different from the one above and a different "
            "answer. The spread builds a new array with the same items "
            "in it, so b is its own thing and a is left alone. Worth "
            "holding the two side by side: the difference between them "
            "is the whole idea."
        ),
    ),
    _t(
        id="trace-object-in-function",
        level=4,
        name="Passed into a function",
        family="One thing, two names",
        code=(
            "function addTax(order) {\n"
            "  order.total = order.total * 1.2;\n"
            "  return order;\n"
            "}\n"
            "const cart = { total: 100 };\n"
            "const priced = addTax(cart);\n"
            "console.log(priced.total);"
        ),
        at_line=7,
        occurrence=1,
        variable="cart",
        expect="{ total: 120 }",
        decoys=(
            "{ total: 100 }",
            "{ total: 120, tax: 20 }",
            "{}",
        ),
        why=(
            "The function was handed the object itself, not a copy, so "
            "`cart` changed even though the code only ever mentions "
            "`order`. This is the bug behind a hundred 'why did my "
            "state change' afternoons. A function that modifies what it "
            "was given should say so in its name, or work on a copy."
        ),
    ),
)


# -- Going round ----------------------------------------------

LOOPS: tuple[Trace, ...] = (
    _t(
        id="trace-accumulator",
        level=1,
        name="Mid-way through adding up",
        family="Going round",
        code=(
            "const prices = [10, 20, 30];\n"
            "let total = 0;\n"
            "for (const p of prices) {\n"
            "  total = total + p;\n"
            "}\n"
            "console.log(total);"
        ),
        at_line=4,
        occurrence=3,
        variable="total",
        expect="30",
        decoys=("60", "0", "10"),
        why=(
            "Third time about to run the adding line, so two prices are "
            "already in: 10 and 20. The 30 has not been added yet — the "
            "line is about to run, not finished. Being one iteration out "
            "is the single commonest mistake in reading a loop, and "
            "counting from what has already happened is the fix."
        ),
    ),
    _t(
        id="trace-building-array",
        level=2,
        name="A list being built",
        family="Going round",
        code=(
            "const names = ['ada', 'bo', 'cy'];\n"
            "const shouty = [];\n"
            "for (const n of names) {\n"
            "  shouty.push(n.toUpperCase());\n"
            "}\n"
            "console.log(shouty.join());"
        ),
        at_line=4,
        occurrence=2,
        variable="shouty",
        expect="['ADA']",
        decoys=(
            "[]",
            "['ADA', 'BO']",
            "['ADA', 'BO', 'CY']",
        ),
        why=(
            "Second time about to push, so exactly one name is in "
            "already. Note that `names` is untouched — toUpperCase "
            "returns a new string rather than changing the old one, "
            "which is true of every string method in JavaScript."
        ),
    ),
    _t(
        id="trace-loop-variable-after",
        level=3,
        name="The counter, one line later",
        family="Going round",
        code=(
            "let i = 0;\n"
            "let sum = 0;\n"
            "while (i < 3) {\n"
            "  sum = sum + i;\n"
            "  i = i + 1;\n"
            "}\n"
            "console.log(sum);"
        ),
        at_line=7,
        occurrence=1,
        variable="i",
        expect="3",
        decoys=("2", "0", "4"),
        why=(
            "The loop stops when the test fails, and the test fails at "
            "3 — so i is 3 when the loop ends, one past the last value "
            "it did any work with. sum is 0 + 1 + 2, which is 3 as well, "
            "and the two being equal here is a coincidence worth "
            "noticing rather than a rule."
        ),
    ),
)


# -- What is in scope -----------------------------------------

SCOPE: tuple[Trace, ...] = (
    _t(
        id="trace-shadowed",
        level=3,
        name="The same name twice",
        family="What is in scope",
        code=(
            "let count = 1;\n"
            "function bump() {\n"
            "  let count = 10;\n"
            "  count = count + 1;\n"
            "  return count;\n"
            "}\n"
            "bump();\n"
            "console.log(count);"
        ),
        at_line=8,
        occurrence=1,
        variable="count",
        expect="1",
        decoys=("11", "10", "2"),
        why=(
            "The `let` inside the function makes a second, separate "
            "count that lives only in there. The outer one is untouched "
            "— which is what you want, and is also why a function that "
            "was supposed to update something appears to do nothing. "
            "Remove the inner `let` and the answer becomes 2."
        ),
    ),
    _t(
        id="trace-no-shadow",
        level=4,
        name="The same program without the second let",
        family="What is in scope",
        code=(
            "let count = 1;\n"
            "function bump() {\n"
            "  count = count + 1;\n"
            "  return count;\n"
            "}\n"
            "bump();\n"
            "console.log(count);"
        ),
        at_line=7,
        occurrence=1,
        variable="count",
        expect="2",
        decoys=("1", "3", "11"),
        why=(
            "One word removed and the function now reaches out and "
            "changes the count above it. Hold this against the one "
            "before: whether a function touches the outside world can "
            "come down to a single `let`, and nothing warns you either "
            "way."
        ),
    ),
    _t(
        id="trace-param-is-a-copy",
        level=5,
        name="A number passed in",
        family="What is in scope",
        code=(
            "function double(n) {\n"
            "  n = n * 2;\n"
            "  return n;\n"
            "}\n"
            "let size = 5;\n"
            "double(size);\n"
            "console.log(size);"
        ),
        at_line=7,
        occurrence=1,
        variable="size",
        expect="5",
        decoys=("10", "0", "25"),
        why=(
            "A number is handed over by value, so the function got a "
            "copy and `size` never moved. Compare it with the object "
            "one in the other family, where the function changed what "
            "it was given: the rule is not 'functions copy their "
            "arguments', it is that the value is copied — and for an "
            "object the value is the reference."
        ),
    ),
)
