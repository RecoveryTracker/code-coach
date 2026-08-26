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
        _s(
            "function greet(name: string): string {\n"
            "  return `Hello, ${name}!`;\n"
            "}\n"
            "\n"
            "console.log(greet('Alex'));",
            "Annotations go after the name, and after the parentheses for the return.",
            5,
        ),
        _s(
            "function average(nums: number[]): number {\n"
            "  const total = nums.reduce((sum, n) => sum + n, 0);\n"
            "  return total / nums.length;\n"
            "}\n"
            "\n"
            "console.log(average([2, 4, 6]));",
            "number[] and Array<number> mean the same thing.",
            5,
        ),
        _s(
            "const area = (w: number, h: number): number => w * h;\n"
            "\n"
            "console.log(area(3, 4));",
            "An arrow function annotates the same way a named one does.",
            5,
        ),
        _s(
            "interface Person {\n"
            "  name: string;\n"
            "  age: number;\n"
            "}\n"
            "\n"
            "function describe(p: Person): string {\n"
            "  return `${p.name} is ${p.age}`;\n"
            "}\n"
            "\n"
            "console.log(describe({ name: 'Sam', age: 30 }));",
            "An interface names a shape, and any object with that shape fits.",
            5,
        ),
        _s(
            "function first<T>(items: T[]): T | undefined {\n"
            "  return items[0];\n"
            "}\n"
            "\n"
            "console.log(first([10, 20]));",
            "A generic keeps the caller's type instead of losing it to any.",
            5,
        ),
        _s(
            "type Point = { x: number; y: number };\n"
            "\n"
            "function shift(p: Point): Point {\n"
            "  return { x: p.x + 1, y: p.y };\n"
            "}\n"
            "\n"
            "console.log(shift({ x: 1, y: 2 }));",
            "A type alias does the same job as an interface for object shapes.",
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
            "  return id.toFixed(2);\n}\n\n"
            "console.log(describe('abc'));",
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
        _s(
            "function grade(score: number): string {\n"
            "  if (score >= 90) return 'A';\n"
            "  if (score >= 80) return 'B';\n"
            "  return 'C';\n"
            "}\n"
            "\n"
            "console.log(grade(85));",
            "Every path returns a string, which is what the annotation promises.",
            5,
        ),
        _s(
            "function sign(n: number): string {\n"
            "  if (n > 0) return 'positive';\n"
            "  if (n < 0) return 'negative';\n"
            "  return 'zero';\n"
            "}\n"
            "\n"
            "console.log(sign(-4));",
            "Three cases, three returns, no else needed.",
            5,
        ),
        _s(
            "function canVote(age: number, citizen: boolean): boolean {\n"
            "  return age >= 18 && citizen;\n"
            "}\n"
            "\n"
            "console.log(canVote(20, true));",
            "The comparison is already a boolean; return it directly.",
            5,
        ),
        _s(
            "type Shape = 'circle' | 'square';\n"
            "\n"
            "function sides(shape: Shape): number {\n"
            "  return shape === 'circle' ? 0 : 4;\n"
            "}\n"
            "\n"
            "console.log(sides('square'));",
            "A union of literals is a type with exactly those values in it.",
            5,
        ),
        _s(
            "function lengthOf(value: string | number): number {\n"
            "  if (typeof value === 'string') return value.length;\n"
            "  return String(value).length;\n"
            "}\n"
            "\n"
            "console.log(lengthOf('hello'));",
            "typeof narrows the union, so .length is allowed inside the if.",
            5,
        ),
        _s(
            "function label(name?: string): string {\n"
            "  return name === undefined ? 'unnamed' : name;\n"
            "}\n"
            "\n"
            "console.log(label());",
            "A ? on a parameter makes it optional, and possibly undefined.",
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
            "  for (const n of nums) {\n    total += n;\n  }\n  return total;\n}\n\n"
            "console.log(sum([1, 2, 3, 4]));",
            "The accumulator pattern, typed.",
            5,
        ),
        _s(
            "function biggest(nums: number[]): number {\n  let best = nums[0];\n"
            "  for (const n of nums) {\n    if (n > best) {\n      best = n;\n"
            "    }\n  }\n  return best;\n}\n\n"
            "console.log(biggest([3, 9, 4]));",
            "Loop plus decision — most algorithms are this shape.",
            5,
        ),
        _s(
            "function total(nums: number[]): number {\n"
            "  let sum = 0;\n"
            "  for (const n of nums) {\n"
            "    sum += n;\n"
            "  }\n"
            "  return sum;\n"
            "}\n"
            "\n"
            "console.log(total([1, 2, 3, 4]));",
            "The loop variable takes its type from the array.",
            5,
        ),
        _s(
            "function countdown(from: number): number[] {\n"
            "  const out: number[] = [];\n"
            "  for (let i = from; i > 0; i--) {\n"
            "    out.push(i);\n"
            "  }\n"
            "  return out;\n"
            "}\n"
            "\n"
            "console.log(countdown(3));",
            "An empty array needs its annotation, or it is any[].",
            5,
        ),
        _s(
            "function firstNegative(nums: number[]): number | null {\n"
            "  for (const n of nums) {\n"
            "    if (n < 0) return n;\n"
            "  }\n"
            "  return null;\n"
            "}\n"
            "\n"
            "console.log(firstNegative([3, 1, -2, 5]));",
            "Saying | null in the return type is how the caller knows to check.",
            5,
        ),
        _s(
            "function doubled(nums: number[]): number[] {\n"
            "  return nums.map((n) => n * 2);\n"
            "}\n"
            "\n"
            "console.log(doubled([1, 2, 3]));",
            "map keeps the element type unless the callback changes it.",
            5,
        ),
        _s(
            "function tally(words: string[]): number {\n"
            "  const counts = new Map<string, number>();\n"
            "  for (const word of words) {\n"
            "    counts.set(word, (counts.get(word) || 0) + 1);\n"
            "  }\n"
            "  return counts.get('a') || 0;\n"
            "}\n"
            "\n"
            "console.log(tally(['a', 'b', 'a']));",
            "A Map takes two type arguments: key, then value.",
            5,
        ),
        _s(
            "function longest(words: string[]): string {\n"
            "  let best = '';\n"
            "  for (const word of words) {\n"
            "    if (word.length > best.length) best = word;\n"
            "  }\n"
            "  return best;\n"
            "}\n"
            "\n"
            "console.log(longest(['a', 'abc', 'ab']));",
            "Keep-the-best-so-far, the shape behind most single-pass loops.",
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
