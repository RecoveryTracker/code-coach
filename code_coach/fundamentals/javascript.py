"""JavaScript fundamentals.

No LeetCode bank yet — this class set stands on its own, and the pattern
lessons appear as soon as the solutions are written.
"""

from __future__ import annotations

from code_coach.fundamentals.base import (
    FundamentalsBank,
    FundamentalsClass,
    Snippet,
    register,
)


def _s(code: str, tip: str, level: int = 1) -> Snippet:
    return Snippet(code=code, tip=tip, level=level)


_FOUNDATIONS = FundamentalsClass(
    id="foundations",
    name="Foundations",
    description="Values, names, printing, and your first functions.",
    snippets=(
        _s("console.log('Hello, world!');", "The everyday way to print."),
        _s("const name = 'Alex';", "`const` can't be reassigned. Reach for it first."),
        _s("let count = 0;", "`let` is for values that change."),
        _s("let total = 0;", "Same idea — a running number."),
        _s("const isReady = true;", "Booleans are `true` / `false`."),
        _s("const price = 4.99;", "One number type; no separate int and double."),
        _s("console.log(name);", "Print a variable by naming it."),
        _s("console.log(`Hi, \\${name}!`);",
           "Backticks make a template literal; ${...} inserts a value."),
        _s("const nums = [1, 2, 3];", "An array."),
        _s("const seen = new Set();", "A Set: no duplicates.", 2),
        _s("const counts = new Map();", "A Map keeps insertion order.", 2),
        _s("const scores = {};", "A plain object also works as a lookup.", 2),
        _s("nums.push(4);", "Append to an array.", 2),
        _s("console.log(nums.length);", "`length` is a property, no parentheses.", 2),
        _s("console.log(nums[0]);", "Index from zero.", 2),
        _s("scores.alex = 10;", "Set a property on an object.", 2),
        _s("counts.set('a', 1);", "A Map uses set/get rather than brackets.", 2),
        _s(
            "const name = 'Alex';\nconsole.log(`Hello, \\${name}!`);",
            "Declare, then use.",
            3,
        ),
        _s(
            "const nums = [1, 2, 3];\nconsole.log(nums.length);",
            "Build a collection, then ask it something.",
            3,
        ),
        _s(
            "function double(n) {\n  return n * 2;\n}",
            "The classic function declaration.",
            4,
        ),
        _s(
            "function add(a, b) {\n  return a + b;\n}",
            "Two parameters, separated by a comma.",
            4,
        ),
        _s(
            "const triple = (n) => n * 3;",
            "An arrow function returns its expression with no `return`.",
            4,
        ),
        _s(
            "function greet(name) {\n  console.log(`Hello, \\${name}!`);\n}",
            "No return: it does something rather than hands something back.",
            4,
        ),
        _s(
            "function add(a, b) {\n  return a + b;\n}\n\nconsole.log(add(7, 12));",
            "Define, then call — no main() needed.",
            5,
        ),
        _s(
            "function shout(words) {\n  return words.toUpperCase();\n}\n\n"
            "console.log(shout('hello'));",
            "Strings carry their own methods.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Decisions",
    description="Comparing values and branching on the answer.",
    snippets=(
        _s("if (age > 18) {", "The condition goes in parentheses."),
        _s("if (count === 0) {",
           "Use `===`, not `==` — it compares without converting types."),
        _s("if (name !== 'Alex') {", "`!==` is the matching 'not equal'."),
        _s("} else {", "The other branch."),
        _s("} else if (score > 50) {", "Chain another test on."),
        _s("if (isReady && count > 0) {", "`&&` needs both sides true.", 2),
        _s("if (isDone || isEmpty) {", "`||` needs only one.", 2),
        _s("if (!isReady) {", "`!` flips a boolean.", 2),
        _s("const label = age >= 18 ? 'adult' : 'minor';",
           "The ternary: condition ? this : that.", 2),
        _s("const shown = name ?? 'guest';",
           "`??` falls back only on null or undefined.", 2),
        _s(
            "if (score > 50) {\n  console.log('pass');\n}",
            "Braces hold everything that runs when it's true.",
            3,
        ),
        _s(
            "if (score > 50) {\n  console.log('pass');\n} else {\n"
            "  console.log('fail');\n}",
            "One branch or the other, never both.",
            4,
        ),
        _s(
            "if (n > 0) {\n  console.log('positive');\n} else if (n < 0) {\n"
            "  console.log('negative');\n} else {\n  console.log('zero');\n}",
            "Tested in order; the first true one wins.",
            4,
        ),
        _s(
            "function grade(score) {\n  if (score >= 90) {\n    return 'A';\n  }\n"
            "  if (score >= 80) {\n    return 'B';\n  }\n  return 'C';\n}",
            "An early return ends the function then and there.",
            5,
        ),
        _s(
            "function isEven(n) {\n  return n % 2 === 0;\n}\n\n"
            "console.log(isEven(4));",
            "`%` is the remainder — the usual evenness test.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Repeating work, and stopping at the right moment.",
    snippets=(
        _s("for (let i = 0; i < 5; i++) {", "Start, keep-going test, step."),
        _s("for (const n of nums) {", "`of` walks values; `in` walks keys."),
        _s("while (count > 0) {", "Repeat while the condition holds."),
        _s("count++;", "Add one. `count--` takes one away."),
        _s("total += n;", "Shorthand for total = total + n.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn of the loop.", 2),
        _s("for (let i = nums.length - 1; i >= 0; i--) {",
           "Counting down: start at the end, step back.", 2),
        _s("nums.forEach((n) => console.log(n));", "Arrays can walk themselves.", 2),
        _s(
            "for (const n of nums) {\n  console.log(n);\n}",
            "The most common loop you'll write.",
            3,
        ),
        _s(
            "let total = 0;\nfor (const n of nums) {\n  total += n;\n}",
            "An accumulator: start empty, add as you go.",
            4,
        ),
        _s(
            "let count = 3;\nwhile (count > 0) {\n  console.log(count);\n  count--;\n}",
            "Something inside must change, or it never ends.",
            4,
        ),
        _s(
            "for (let i = 0; i < nums.length; i++) {\n"
            "  console.log(`\\${i}: \\${nums[i]}`);\n}",
            "Use the index form when you need the position too.",
            4,
        ),
        _s(
            "function sum(nums) {\n  let total = 0;\n  for (const n of nums) {\n"
            "    total += n;\n  }\n  return total;\n}",
            "The accumulator pattern, wrapped up as a function.",
            5,
        ),
        _s(
            "function biggest(nums) {\n  let best = nums[0];\n"
            "  for (const n of nums) {\n    if (n > best) {\n      best = n;\n"
            "    }\n  }\n  return best;\n}",
            "Loop plus decision — most algorithms are this shape.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(
        language="javascript",
        classes=(_FOUNDATIONS, _DECISIONS, _LOOPS),
    )
)
