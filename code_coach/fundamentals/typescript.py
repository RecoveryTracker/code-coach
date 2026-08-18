"""TypeScript fundamentals — JavaScript plus the type annotations."""

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
    description="Values, names, and the types that describe them.",
    snippets=(
        _s("console.log('Hello, world!');", "Same as JavaScript — TypeScript is a superset."),
        _s("const name: string = 'Alex';", "The type goes after the name, behind a colon."),
        _s("let count: number = 0;", "One number type — no separate int and float."),
        _s("const isReady: boolean = true;", "`boolean`, spelled out in full."),
        _s("const name = 'Alex';", "Leave the type off and it's inferred. Usually better."),
        _s("let total = 0;", "Inferred as number, and stays a number."),
        _s("const nums: number[] = [1, 2, 3];", "An array of numbers."),
        _s("const words: string[] = [];", "An empty array needs its type stated."),
        _s("const seen = new Set<number>();", "Generics say what's inside.", 2),
        _s("const counts = new Map<string, number>();", "Key type, then value type.", 2),
        _s("let maybe: string | null = null;", "A union: one type or the other.", 2),
        _s("let id: string | number;", "Unions aren't only for null.", 2),
        _s("nums.push(4);", "Only numbers — the type stops a stray string.", 2),
        _s("console.log(nums.length);", "`length` is a property.", 2),
        _s("console.log(`Hi, \\${name}!`);", "Template literals, same as JavaScript.", 2),
        _s(
            "const name: string = 'Alex';\nconsole.log(`Hello, \\${name}!`);",
            "Declare with a type, then use it.",
            3,
        ),
        _s(
            "interface Point {\n  x: number;\n  y: number;\n}",
            "An interface names the shape of an object.",
            4,
        ),
        _s(
            "type Grade = 'A' | 'B' | 'C';",
            "A union of literals — only those three strings are allowed.",
            4,
        ),
        _s(
            "function double(n: number): number {\n  return n * 2;\n}",
            "Parameter types, then the return type after the parentheses.",
            4,
        ),
        _s(
            "function greet(name: string): void {\n"
            "  console.log(`Hello, \\${name}!`);\n}",
            "`void` means it returns nothing.",
            4,
        ),
        _s(
            "const triple = (n: number): number => n * 3;",
            "An arrow function with types.",
            4,
        ),
        _s(
            "function add(a: number, b: number): number {\n  return a + b;\n}\n\n"
            "console.log(add(7, 12));",
            "Define, then call.",
            5,
        ),
        _s(
            "interface Point {\n  x: number;\n  y: number;\n}\n\n"
            "function show(p: Point): void {\n  console.log(`\\${p.x},\\${p.y}`);\n}\n\n"
            "show({ x: 1, y: 2 });",
            "An interface used as a parameter type.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Decisions",
    description="Comparing values, and letting types narrow the branches.",
    snippets=(
        _s("if (age > 18) {", "The condition goes in parentheses."),
        _s("if (count === 0) {", "Always `===` — it won't convert types first."),
        _s("if (name !== 'Alex') {", "The matching 'not equal'."),
        _s("} else {", "The other branch."),
        _s("} else if (score > 50) {", "Chain another test on."),
        _s("if (isReady && count > 0) {", "`&&` needs both sides true.", 2),
        _s("if (value === null) {", "Check for null before you use the value.", 2),
        _s("if (typeof id === 'string') {", "A typeof check narrows a union.", 2),
        _s("const label = age >= 18 ? 'adult' : 'minor';", "The ternary.", 2),
        _s("const shown = name ?? 'guest';", "Falls back only on null or undefined.", 2),
        _s("const len = text?.length;", "`?.` stops at null instead of throwing.", 2),
        _s(
            "if (score > 50) {\n  console.log('pass');\n}",
            "Braces hold what runs when it's true.",
            3,
        ),
        _s(
            "if (score > 50) {\n  console.log('pass');\n} else {\n"
            "  console.log('fail');\n}",
            "One branch or the other, never both.",
            4,
        ),
        _s(
            "function describe(id: string | number): string {\n"
            "  if (typeof id === 'string') {\n    return id.toUpperCase();\n  }\n"
            "  return id.toFixed(2);\n}",
            "Inside the if, TypeScript knows id is a string.",
            5,
        ),
        _s(
            "function grade(score: number): string {\n  if (score >= 90) {\n"
            "    return 'A';\n  }\n  if (score >= 80) {\n    return 'B';\n  }\n"
            "  return 'C';\n}\n\nconsole.log(grade(85));",
            "Early returns, each ending the function.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Repeating work over typed collections.",
    snippets=(
        _s("for (let i = 0; i < 5; i++) {", "Start, keep-going test, step."),
        _s("for (const n of nums) {", "`of` walks values."),
        _s("while (count > 0) {", "Repeat while the condition holds."),
        _s("count++;", "Add one."),
        _s("total += n;", "Shorthand for total = total + n.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn.", 2),
        _s("const doubled = nums.map((n) => n * 2);", "`map` keeps the types.", 2),
        _s("const big = nums.filter((n) => n > 10);", "`filter` returns the same type.", 2),
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
            "for (let i = 0; i < nums.length; i++) {\n"
            "  console.log(`\\${i}: \\${nums[i]}`);\n}",
            "Use the index form when you need the position.",
            4,
        ),
        _s(
            "function sum(nums: number[]): number {\n  let total = 0;\n"
            "  for (const n of nums) {\n    total += n;\n  }\n  return total;\n}",
            "The accumulator pattern, typed.",
            5,
        ),
        _s(
            "function biggest(nums: number[]): number {\n  let best = nums[0];\n"
            "  for (const n of nums) {\n    if (n > best) {\n      best = n;\n"
            "    }\n  }\n  return best;\n}",
            "Loop plus decision — most algorithms are this shape.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(
        language="typescript",
        classes=(_FOUNDATIONS, _DECISIONS, _LOOPS),
    )
)
