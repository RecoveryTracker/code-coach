"""The TypeScript cheat sheet.

Everything on the JavaScript sheet is true here too, so this one covers the
part that is different: the types.
"""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="typescript",
    sections=(
        Section(
            "The first minute",
            "Annotations go after the name, behind a colon.",
            (
                _e("const name: string = 'Alex';", "explicit"),
                _e("const name = 'Alex';", "inferred, and usually better"),
                _e("let count: number = 0;", "one number type, as in JavaScript"),
                _e("const ready: boolean = true;", "spelled out in full"),
                _e("const nums: number[] = [];", "an empty array needs its type"),
                _e("function add(a: number, b: number): number {", "return type last"),
                _e("const add = (a: number, b: number): number => a + b;", "as an arrow"),
                _e("function log(msg: string): void {", "returns nothing"),
                _e("console.log(value);", "the same as JavaScript, all of it"),
            ),
        ),
        Section(
            "Shapes",
            "Naming the form of an object, two ways.",
            (
                _e("interface Point {\n  x: number;\n  y: number;\n}", "an interface"),
                _e("type Point = { x: number; y: number };", "a type alias — same job"),
                _e("interface P { readonly id: string }", "cannot be reassigned"),
                _e("interface P { name?: string }", "optional: string | undefined"),
                _e("interface Dog extends Animal {", "interfaces extend"),
                _e("type Both = A & B;", "aliases intersect"),
                _e("Record<string, number>", "an object used as a lookup"),
                _e("Array<number>", "the same as number[]"),
            ),
        ),
        Section(
            "Unions and narrowing",
            "One type or another, and how to prove which.",
            (
                _e("let id: string | number;", "a union"),
                _e("type Shape = 'circle' | 'square';", "a union of literals"),
                _e("if (typeof id === 'string') {", "narrows inside the block"),
                _e("if (Array.isArray(x)) {", "narrows to an array"),
                _e("if (x === null) return;", "narrows by elimination"),
                _e("if ('wings' in animal) {", "narrows by property"),
                _e("value as string", "an assertion — you are overruling it"),
                _e("value!", "'this is not null', and you had better be right"),
                _e("x satisfies Shape", "check without widening the type"),
            ),
        ),
        Section(
            "Generics",
            "Keeping the caller's type instead of losing it to any.",
            (
                _e("function first<T>(items: T[]): T | undefined {", "one type parameter"),
                _e("const box = <T,>(v: T) => ({ v });", "the comma is for .tsx files"),
                _e("interface Box<T> { value: T }", "a generic shape"),
                _e("function longest<T extends { length: number }>(", "a constraint"),
                _e("Promise<string>", "what it resolves to"),
                _e("Map<string, number>", "key type, then value type"),
                _e("Partial<T>", "every field optional"),
                _e("Pick<T, 'a' | 'b'>", "and Omit<T, 'c'>"),
                _e("ReturnType<typeof fn>", "the type a function gives back"),
            ),
        ),
        Section(
            "Strictness",
            "The settings that decide how much the compiler helps.",
            (
                _e('"strict": true', "turn it on; the rest of these come with it"),
                _e("strictNullChecks", "null stops being assignable to everything"),
                _e("noImplicitAny", "an unannotated parameter becomes an error"),
                _e("unknown", "any, but you have to narrow before using it"),
                _e("never", "the type of a value that cannot happen"),
                _e("as const", "freezes a literal to its exact value"),
                _e("// @ts-expect-error", "asserts the next line DOES fail"),
            ),
        ),
        Section(
            "Enums and modules",
            "Named constants, and getting types across files.",
            (
                _e("enum Colour { Red, Green }", "numeric by default"),
                _e("enum Colour { Red = 'red' }", "string values are usually clearer"),
                _e("const enum Colour {", "inlined; no object at runtime"),
                _e("export type { Point };", "a type-only export"),
                _e("import type { Point } from './point';", "erased at compile time"),
                _e("export interface Point {", "types and values export alike"),
            ),
        ),
    ),
)

register(SHEET)
