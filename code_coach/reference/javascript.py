"""The JavaScript cheat sheet."""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="javascript",
    sections=(
        Section(
            "The first minute",
            "What you write before you have written anything.",
            (
                _e("console.log(value);", "print anything"),
                _e("const name = 'Alex';", "can't be reassigned — start here"),
                _e("let count = 0;", "for values that change"),
                _e("function add(a, b) {\n  return a + b;\n}", "a named function"),
                _e("const add = (a, b) => a + b;", "the same, as an arrow"),
                _e("`Hi, ${name}!`", "backticks interpolate; quotes do not"),
                _e("if (a === b) {", "always ===, never =="),
                _e("for (const n of nums) {", "walk values"),
                _e("return;", "leaves the function now"),
                _e("// a note to your later self", "line comment"),
            ),
        ),
        Section(
            "Arrays",
            "Ordered, growable, and where most of the work happens.",
            (
                _e("const nums = [1, 2, 3];", "a literal"),
                _e("nums.length", "a property, no parentheses"),
                _e("nums[0]", "first; nums[nums.length - 1] is last"),
                _e("nums.push(4);", "append"),
                _e("nums.pop();", "remove and return the last"),
                _e("nums.shift();", "remove the first — slow on big arrays"),
                _e("nums.unshift(0);", "insert at the front"),
                _e("nums.includes(2)", "is it in there?"),
                _e("nums.indexOf(2)", "where? -1 if absent"),
                _e("nums.slice(1, 3)", "a copy of part; leaves the original"),
                _e("nums.splice(1, 2);", "cuts out of the original"),
                _e("[...nums]", "a shallow copy"),
                _e("nums.join('-')", "to a string"),
                _e("Array.from({ length: 5 }, (_, i) => i)", "0..4"),
            ),
        ),
        Section(
            "Walking an array",
            "The four you reach for, and what each hands back.",
            (
                _e("nums.map((n) => n * 2)", "same length, new values"),
                _e("nums.filter((n) => n > 2)", "fewer, same values"),
                _e("nums.reduce((sum, n) => sum + n, 0)", "one value out"),
                _e("nums.forEach((n) => console.log(n));", "no value out"),
                _e("nums.find((n) => n > 2)", "first match, or undefined"),
                _e("nums.findIndex((n) => n > 2)", "its index, or -1"),
                _e("nums.some((n) => n > 2)", "any?"),
                _e("nums.every((n) => n > 2)", "all?"),
                _e("nums.sort((a, b) => a - b);", "numbers — the default is text"),
                _e("nums.reverse();", "in place"),
                _e("nums.flat()", "one level of nesting out"),
            ),
        ),
        Section(
            "Strings",
            "Immutable — every one of these returns a new string.",
            (
                _e("text.length", "characters"),
                _e("text.toUpperCase()", "and toLowerCase()"),
                _e("text.trim()", "whitespace off both ends"),
                _e("text.includes('ab')", "substring present?"),
                _e("text.startsWith('a')", "and endsWith"),
                _e("text.indexOf('a')", "-1 if absent"),
                _e("text.slice(0, 3)", "a piece of it"),
                _e("text.split(',')", "to an array"),
                _e("text.replace('a', 'b')", "first only; replaceAll for all"),
                _e("text.repeat(3)", "concatenate with itself"),
                _e("text.padStart(2, '0')", "'7' becomes '07'"),
                _e("[...text]", "to an array of characters"),
            ),
        ),
        Section(
            "Objects, Maps and Sets",
            "Three ways to look something up, for three different jobs.",
            (
                _e("const user = { name: 'Alex', age: 30 };", "an object"),
                _e("user.name", "or user['name'] when the key is a variable"),
                _e("user.city ?? 'unknown'", "default only for null/undefined"),
                _e("Object.keys(user)", "and .values(), .entries()"),
                _e("const { name, age } = user;", "destructure by key"),
                _e("{ ...user, age: 31 }", "a copy with one field changed"),
                _e("'name' in user", "key present?"),
                _e("delete user.age;", "remove a key"),
                _e("const seen = new Set();", "no duplicates"),
                _e("seen.add(x); seen.has(x);", "and seen.delete(x)"),
                _e("const counts = new Map();", "any key type, keeps order"),
                _e("counts.set(k, v); counts.get(k);", "and counts.has(k)"),
                _e("counts.get(k) ?? 0", "the counting idiom"),
                _e("[...counts.entries()]", "to an array of pairs"),
            ),
        ),
        Section(
            "Deciding",
            "Comparisons, and the operators that stand in for an if.",
            (
                _e("a === b", "equal, without converting types"),
                _e("a !== b", "the matching not-equal"),
                _e("a && b", "both; stops early if a is falsy"),
                _e("a || b", "either; stops early if a is truthy"),
                _e("!a", "flip it"),
                _e("a ?? b", "b only if a is null or undefined"),
                _e("cond ? x : y", "an if that is an expression"),
                _e("user?.address?.city", "stops at null instead of throwing"),
                _e("Array.isArray(x)", "typeof [] is 'object', so use this"),
                _e("Number.isNaN(x)", "NaN is not equal to itself"),
                _e(
                    "if (!items.length) return;",
                    "the early exit that saves a nesting level",
                ),
            ),
        ),
        Section(
            "Loops",
            "Four shapes, and when each is the right one.",
            (
                _e("for (const n of nums) {", "values — the usual one"),
                _e("for (const key in obj) {", "keys, and inherited ones too"),
                _e("for (let i = 0; i < n; i++) {", "when you need the index"),
                _e("for (let i = n - 1; i >= 0; i--) {", "backwards"),
                _e("while (cond) {", "when the end is a condition"),
                _e("break;", "leave the loop"),
                _e("continue;", "skip to the next turn"),
                _e("for (const [k, v] of Object.entries(obj)) {", "key and value"),
                _e("for (const [i, n] of nums.entries()) {", "index and value"),
            ),
        ),
        Section(
            "Async",
            "Promises, and the two ways to wait for one.",
            (
                _e("async function load() {", "returns a Promise, always"),
                _e("const data = await fetch(url);", "only inside async"),
                _e("await Promise.all([a, b]);", "together, not one after another"),
                _e("await Promise.allSettled([a, b]);", "all of them, results and all"),
                _e("try {\n  await job();\n} catch (err) {\n  console.error(err);\n}", "catching an await"),
                _e("setTimeout(() => fn(), 1000);", "later, not blocking"),
                _e(".then((v) => ...)", "the callback form"),
                _e(".catch((e) => ...)", "and its error half"),
            ),
        ),
        Section(
            "Errors",
            "Throwing, catching, and the shape of a guard.",
            (
                _e("throw new Error('message');", "always an Error, not a string"),
                _e("try {\n  risky();\n} catch (err) {\n  handle(err);\n}", "the shape"),
                _e("} finally {", "runs either way"),
                _e("err.message", "and err.stack"),
                _e(
                    "if (!input) throw new Error('input required');",
                    "guard at the top, not a nested if",
                ),
            ),
        ),
        Section(
            "Modules",
            "Getting things in and out of a file.",
            (
                _e("export function add(a, b) {", "a named export"),
                _e("export default thing;", "the one unnamed export"),
                _e("import { add } from './math.js';", "named"),
                _e("import thing from './thing.js';", "default"),
                _e("import * as math from './math.js';", "everything, namespaced"),
            ),
        ),
    ),
)

register(SHEET)
