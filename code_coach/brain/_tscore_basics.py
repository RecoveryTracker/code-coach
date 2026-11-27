"""TypeScript core pack, part 1: TS Eval and Null & Undefined.

Every answer is worked out by hand in Python (arithmetic, string building, Fractions for division and rounding); the
real `tsc --strict` and node only check the model afterwards (tests/brain_check.py tscore).
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, getcontext
from fractions import Fraction
from math import floor

from ._model import Maker, decimal_div, tmod
from ._ts_model import NULL, UNDEF, TS, js_show

getcontext().prec = 60


def K(fn):
    """A model function of the parameters: `K(lambda a, b, **_: a + b)`."""
    return lambda p: fn(**p)


def jsround(x: Fraction) -> int:
    """Math.round: halves go up."""
    return floor(x + Fraction(1, 2))


def fixed(x: Fraction, digits: int) -> str:
    """x.toFixed(digits) for a non-negative exact value: halves go up."""
    d = Decimal(x.numerator) / Decimal(x.denominator)
    return format(d.quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP), "f")


def jsb(v: bool) -> str:
    return "true" if v else "false"


def bits(*vs) -> str:
    return " ".join(jsb(v) if isinstance(v, bool) else js_show(v) for v in vs)


def tr(x: Fraction) -> int:
    """Math.trunc."""
    return int(x)


# -- 1. TS Eval -----------------------------------------------------------

EVAL: list[Maker] = [
    TS("console.log($a + $b * $c);", K(lambda a, b, c, **_: a + b * c), "Multiplication binds tighter than addition."),
    TS("console.log(($a + $b) * $c);", K(lambda a, b, c, **_: (a + b) * c), "The brackets are worked out first."),
    TS("console.log($m % $a, $m % $b);", K(lambda m, a, b, **_: f"{m % a} {m % b}"), "The percent sign gives the remainder of the division."),
    TS('console.log("$w" + $a + $b);', K(lambda w, a, b, **_: f"{w}{a}{b}"),
       "Once a string is on the left, each plus glues the number on as text."),
    TS('console.log($a + $b + "$w");', K(lambda w, a, b, **_: f"{a + b}{w}"),
       "The two numbers are added first, and only then does the string join in."),
    TS('const n = $a;\nconsole.log("$w x" + n + ", " + n * $b);', K(lambda w, a, b, **_: f"{w} x{a}, {a * b}"),
       "Each plus glues the next piece on as text, and the product is worked out first."),
    TS('console.log(typeof $a, typeof "$w");', "number string", "typeof names the kind of a value."),
    TS("console.log(typeof null, typeof undefined, typeof []);", "object undefined object",
       "typeof null and typeof an array are both the old, odd answer object."),
    TS("console.log(typeof (() => $a), typeof NaN, typeof ($a).toString());", "function number string",
       "NaN is still a number, and toString gives a string."),
    TS("console.log(Math.max($a, $b, $c));", K(lambda a, b, c, **_: max(a, b, c)), "Math.max returns the biggest argument."),
    TS("console.log(Math.min($a, $b, $c), Math.max($a, $b, $c));", K(lambda a, b, c, **_: f"{min(a, b, c)} {max(a, b, c)}"),
       "Math.min and Math.max pick the smallest and the biggest."),
    TS("console.log(Math.floor($m / $a));", K(lambda m, a, **_: m // a), "Math.floor rounds the quotient down."),
    TS("console.log(Math.round($a / $h));", K(lambda a, h, **_: jsround(Fraction(a, h))), "Math.round rounds halves up."),
    TS("console.log(($a / $h).toFixed(1));", K(lambda a, h, **_: fixed(Fraction(a, h), 1)),
       "toFixed returns a string with exactly that many decimals, rounding halves up."),
    TS("console.log(($m / $h).toFixed(2));", K(lambda m, h, **_: fixed(Fraction(m, h), 2)),
       "toFixed(2) always shows two decimals, padding with zeros."),
    TS('console.log(Number("$n") + $a);', K(lambda n, a, **_: n + a), "Number turns the text into a number, so plus adds."),
    TS('console.log("$n" + $a);', K(lambda n, a, **_: f"{n}{a}"), "A string plus a number glues the digits together."),
    TS('console.log(+"$n" + $a);', K(lambda n, a, **_: n + a), "The unary plus turns the string into a number first."),
    TS('console.log(parseInt("$n px") + $a);', K(lambda n, a, **_: n + a),
       "parseInt reads the leading digits and stops at the first other character."),
    TS("let i = $a;\nconsole.log(i++, ++i, i);", K(lambda a, **_: f"{a} {a + 2} {a + 2}"),
       "i++ gives the old value then adds one, ++i adds one then gives the new value."),
    TS("let x = $a;\nlet y = $b;\nconsole.log(x < y, x === y, x !== y);", K(lambda a, b, **_: bits(a < b, a == b, a != b)),
       "Each comparison is a boolean about the two numbers."),
    TS('console.log("$w" < "$z", "$w".length < "$z".length);', K(lambda w, z, **_: bits(w < z, len(w) < len(z))),
       "Strings compare letter by letter in dictionary order, lengths compare as numbers."),
    TS('console.log("$a" + "$b", +"$a" + +"$b");', K(lambda a, b, **_: f"{a}{b} {a + b}"),
       "Two strings are glued; with a unary plus on each they become numbers and add."),
    TS('let n = Number("$w");\nconsole.log(n === n, Number.isNaN(n));', "false true",
       "A word is not a number, and NaN is the one value that is not equal to itself."),
    TS("console.log($a / 0, -$a / 0, 0 / 0);", "Infinity -Infinity NaN", "Dividing by zero gives Infinity, and zero over zero is NaN."),
    TS("console.log(0.1 + 0.2 === 0.3, 0.1 + 0.2);", "false 0.30000000000000004", "Binary floating point cannot store 0.1 or 0.2 exactly."),
    TS("console.log(2 ** $a, 2 ** $k, $a ** 2);", K(lambda a, k, **_: f"{2 ** a} {2 ** k} {a * a}"), "Two stars is exponentiation."),
    TS("console.log($a % -$b, -$a % $b);", K(lambda a, b, **_: f"{tmod(a, -b)} {tmod(-a, b)}"),
       "The remainder takes the sign of the left number."),
    TS("console.log(Math.trunc(-$m / $a), Math.floor(-$m / $a), Math.round(-$m / $a));",
       K(lambda m, a, **_: f"{tr(Fraction(-m, a))} {floor(Fraction(-m, a))} {jsround(Fraction(-m, a))}"),
       "trunc cuts toward zero, floor goes down, round sends halves up."),
    TS('const t = (x: unknown) => !!x;\nconsole.log(t(""), t("$w"), t(0), t([]));', "false true false true", "Empty string and 0 are falsy, any non-empty string and any array are truthy."),
    TS('console.log("$w".length, "$w"[$j], "$w".indexOf("$f"));',
       K(lambda w, j, f, **_: f"{len(w)} {w[j]} {w.find(f)}"), "length counts letters, [j] reads one, indexOf finds the first match."),
    TS('console.log("$w".toUpperCase().slice(0, $i), "$z".slice(-$k));',
       K(lambda w, z, i, k, **_: f"{w.upper()[:i]} {z[-k:]}"), "slice(0, i) keeps the first i letters, a negative start counts from the end."),
    TS('console.log([..."$w"].reverse().join(""));', K(lambda w, **_: w[::-1]), "Spread splits into letters, reverse flips them, join glues them back."),
    TS('console.log("$w".repeat($k) + $a);', K(lambda w, k, a, **_: w * k + str(a)), "repeat copies the text, then the number is glued on."),
    TS('console.log("$w".replace("$f", "-"), "$w".split("$f").length);',
       K(lambda w, f, **_: f"{w.replace(f, '-', 1)} {w.count(f) + 1}"),
       "replace changes only the first match, and split gives one more piece than there are matches."),
    TS('console.log($a + " + " + $b + " = " + ($a + $b));', K(lambda a, b, **_: f"{a} + {b} = {a + b}"),
       "The brackets make the sum a number first, the other plus signs glue text."),
    TS("let x = $n;\nx %= $a;\nx *= $b;\nconsole.log(x);", K(lambda n, a, b, **_: (n % a) * b), "Each compound assignment updates x in turn."),
    TS("console.log($m / $h);", K(lambda m, h, **_: decimal_div(m, h)), "Slash is true division, so the answer can have decimals."),
    TS("console.log(Number.isInteger($m / $a), $m % $a === 0);", K(lambda m, a, **_: bits(m % a == 0, m % a == 0)),
       "A quotient is a whole number exactly when the remainder is zero."),
    TS("console.log(Math.abs($a - $m), Math.sign($a - $m), Math.sqrt($a * $a));", K(lambda a, m, **_: f"{m - a} -1 {a}"),
       "abs drops the sign, sign gives -1, 0 or 1, and sqrt undoes the square."),
    TS('console.log(($n).toString(2), parseInt("$hx", 16));', K(lambda n, hx, hxv, **_: f"{bin(n)[2:]} {hxv}"),
       "toString(2) writes binary, and parseInt with 16 reads hexadecimal."),
    TS("const v: number | undefined = $a > $b ? undefined : $c;\nconsole.log(v ?? $d);",
       K(lambda a, b, c, d, **_: d if a > b else c), "The double question mark falls back only when the left side is undefined or null."),
    TS("const o: { n?: { v: number } } = { n: { v: $a } };\nconsole.log(o.n?.v);", K(lambda a, **_: a),
       "Optional chaining reads the property when the object exists."),
    TS('console.log(Number(""), Number(" $a "), Number("$a px"));', K(lambda a, **_: f"0 {a} NaN"),
       "An empty string is 0, spaces around digits are ignored, other text is NaN."),
    TS("console.log(String($a) + String(true) + String(null));", K(lambda a, **_: f"{a}truenull"), "String turns any value into its text."),
    TS('console.log(typeof ($a + "$b"), typeof ($a * $b), typeof (typeof $a));', "string number string",
       "A number plus a string is a string, a product is a number, and typeof always returns a string."),
    TS("console.log(Math.min($a, $b) * Math.max($c, $d));", K(lambda a, b, c, d, **_: min(a, b) * max(c, d)), "Each Math call runs first, then the product."),
    TS("console.log(($a * 1.5).toFixed(0), ($b * 0.25).toFixed(1));",
       K(lambda a, b, **_: f"{fixed(Fraction(a * 3, 2), 0)} {fixed(Fraction(b, 4), 1)}"), "toFixed rounds an exact half up."),
    TS("console.log(Math.ceil($a / $b), Math.floor($a / $b));",
       K(lambda a, b, **_: f"{-((-a) // b)} {a // b}"), "ceil rounds the quotient up and floor rounds it down."),
]

# -- 8. Null & Undefined --------------------------------------------------

NULLS: list[Maker] = [
    TS("function f(x?: number) { return x ?? $a; }\nconsole.log(f(), f(0), f($b));", K(lambda a, b, **_: f"{a} 0 {b}"),
       "The double question mark replaces only undefined or null, so 0 stays."),
    TS("function f(x: number) { return x || $a; }\nconsole.log(f(0), f($b));", K(lambda a, b, **_: f"{a} {b}"),
       "The double bar replaces every falsy value, and 0 is falsy."),
    TS('function f(s: string) { return (s || "$w").length; }\nconsole.log(f(""), f("$z"));',
       K(lambda w, z, **_: f"{len(w)} {len(z)}"), "The empty string is falsy, so the double bar swaps in the default."),
    TS('function f(s: string) { return (s ?? "$w").length; }\nconsole.log(f(""), f("$z"));',
       K(lambda w, z, **_: f"0 {len(z)}"), "The empty string is not nullish, so the double question mark keeps it."),
    TS("const o: { a?: { b: number } } = {};\nconsole.log(o.a?.b);", "undefined", "Optional chaining stops at the missing a and gives undefined."),
    TS("const o: { a?: { b: number } } = { a: { b: $a } };\nconsole.log(o.a?.b ?? $b);", K(lambda a, **_: a),
       "The chain succeeds, so the fallback is not used."),
    TS("const o: { a?: { b: number } } = {};\nconsole.log(o.a?.b ?? $b);", K(lambda b, **_: b),
       "The chain gives undefined, so the fallback is supplied."),
    TS('const m = new Map<string, number>([["$w", $a]]);\nconsole.log(m.get("$w")! + $b);', K(lambda a, b, **_: a + b),
       "The exclamation mark only silences the compiler, the value is really there."),
    TS("function f(a: number, b = $a) { return a + b; }\nconsole.log(f($b), f($b, $c));", K(lambda a, b, c, **_: f"{b + a} {b + c}"),
       "The default is used only when the argument is left out."),
    TS("function f(b = $a) { return b; }\nconsole.log(f(undefined), f());", K(lambda a, **_: f"{a} {a}"),
       "Passing undefined counts as leaving the argument out."),
    TS("function f(n: number | null = $a) { return n; }\nconsole.log(f(null), f(undefined), f());", K(lambda a, **_: f"null {a} {a}"),
       "A default replaces undefined but not null."),
    TS("function f(x: number | null | undefined) { return x == null; }\nconsole.log(f(null), f(undefined), f(0));", "true true false",
       "Loose equality with null is true for both null and undefined, and for nothing else."),
    TS("function f(x: number | null | undefined) { return x === null; }\nconsole.log(f(null), f(undefined), f(0));", "true false false",
       "Strict equality with null matches only null."),
    TS("console.log(typeof null, typeof undefined);", "object undefined", "typeof null is the famous quirk: object."),
    TS('interface O { a?: number }\nconst o: O = {};\nconsole.log(o.a, "a" in o);', "undefined false", "The property was never set, so in says false."),
    TS('interface O { a?: number }\nconst o: O = { a: undefined };\nconsole.log(o.a, "a" in o);', "undefined true",
       "The property exists and holds undefined, so in says true."),
    TS("console.log(Object.keys({ a: undefined, b: $a }).length);", "2", "A property holding undefined is still a key."),
    TS("console.log(JSON.stringify({ a: undefined, b: $a }));", K(lambda a, **_: '{"b":%d}' % a),
       "JSON.stringify drops properties whose value is undefined."),
    TS("console.log(JSON.stringify({ a: null, b: $a }));", K(lambda a, **_: '{"a":null,"b":%d}' % a), "JSON keeps null."),
    TS("function g(f?: () => number) { return f?.() ?? $a; }\nconsole.log(g(), g(() => $b));", K(lambda a, b, **_: f"{a} {b}"),
       "The optional call runs the function only if it exists."),
    TS("function f(xs?: number[]) { return xs?.[0]; }\nconsole.log(f(), f([]), f([$a]));", K(lambda a, **_: f"undefined undefined {a}"),
       "An undefined array and an empty array both give undefined for index 0."),
    TS("function f(x?: number) { x ??= $a; return x; }\nconsole.log(f(), f(0), f($b));", K(lambda a, b, **_: f"{a} 0 {b}"),
       "The nullish assignment assigns only when the value is undefined or null."),
    TS("function f(x?: number) { x ||= $a; return x; }\nconsole.log(f(), f(0), f($b));", K(lambda a, b, **_: f"{a} {a} {b}"),
       "The logical-or assignment assigns whenever the value is falsy, and 0 is falsy."),
    TS("function f(a?: number, b?: number) { return a ?? b ?? $c; }\nconsole.log(f(), f(undefined, $a), f($b, $a));",
       K(lambda a, b, c, **_: f"{c} {a} {b}"), "The chain picks the first value that is not undefined or null."),
    TS("console.log(Number(null), Number(undefined));", "0 NaN", "null becomes 0 but undefined becomes NaN."),
    TS("console.log(String(null) + String(undefined));", "nullundefined", "String turns them into the words null and undefined."),
    TS('console.log([null, undefined].join("-"), [$a, null, $b].join("-"));', K(lambda a, b, **_: f"- {a}--{b}"), "join turns null and undefined into empty text."),
    TS("console.log([null, undefined].map(x => x ?? $a));", K(lambda a, **_: [a, a]), "Both items are nullish, so each becomes the fallback."),
    TS('console.log([0, $a, "", "$w", null].filter(Boolean));', K(lambda a, w, **_: [a, w]), "Boolean drops 0, the empty string and null."),
    TS("let n = 0;\nfunction next() { return ++n; }\nfunction f(o?: number[]) { return o?.[next()]; }\nf(); f([$a, $b, $c]); f();\nconsole.log(n);",
       "1", "When o is undefined the whole chain is skipped, so next() does not run."),
    TS('function f(s: string | null) { return s?.length; }\nconsole.log(f(null), f("$w"));', K(lambda w, **_: f"undefined {len(w)}"),
       "Optional chaining gives undefined for null."),
    TS("function f(...xs: number[]) { return xs.length; }\nconsole.log(f(), f($a, $b));", "0 2",
       "Rest parameters collect the arguments into an array, empty if none."),
    TS("function pick(a: number, b: number | null) { return a || b; }\nconsole.log(pick(0, null), pick(0, $a), pick($b, $a));",
       K(lambda a, b, **_: f"null {a} {b}"), "The double bar returns the first truthy operand, or the last one."),
    TS("console.log([undefined, null, $a]);", K(lambda a, **_: [UNDEF, NULL, a]), "console.log shows undefined and null by name inside an array."),
    TS("console.log({ a: undefined, b: null, c: $a });", K(lambda a, **_: {"a": UNDEF, "b": NULL, "c": a}),
       "console.log shows both nothings inside an object."),
    TS("function f({ x = $a, y = $b }: { x?: number; y?: number | null }) { return [x, y]; }\nconsole.log(f({ x: undefined, y: null }));",
       K(lambda a, **_: [a, NULL]), "A destructuring default applies to undefined but not to null."),
    TS("function f({ x = $a, y = $b }: { x?: number; y?: number | null }) { return [x, y]; }\nconsole.log(f({}));",
       K(lambda a, b, **_: [a, b]), "Both properties are missing, so both defaults are used."),
    TS('console.log([$a, $b].find(n => n > $m)?.toFixed(1) ?? "none");', "none",
       "find gives undefined, the optional call is skipped, and the fallback word is shown."),
    TS('const m = new Map<string, number>();\nconsole.log(m.get("$w"), m.has("$w"));', "undefined false",
       "A missing key gives undefined from get and false from has."),
    TS('const m = new Map<string, number>();\nm.set("$w", 0);\nconsole.log(m.get("$w") || $a, m.get("$w") ?? $a);', K(lambda a, **_: f"{a} 0"),
       "The stored 0 is falsy so the double bar replaces it, but it is not nullish so the double question mark keeps it."),
    TS("function f() {}\nconsole.log(f(), typeof f());", "undefined undefined", "A function that returns nothing gives undefined."),
    TS("function f(n: number) { if (n > $a) return n; }\nconsole.log(f($b), f($c));",
       K(lambda a, b, c, **_: f"{b if b > a else 'undefined'} {c if c > a else 'undefined'}"),
       "Without a return that runs, the call gives undefined."),
    TS("function f(n: number) { return n ?? $a; }\nconsole.log(f(NaN), f(0));", "NaN 0", "NaN is not nullish, so it is kept."),
    TS("function f(o?: { x: number }) { return { ...o, a: $a }; }\nconsole.log(f(), f({ x: $b }));", K(lambda a, b, **_: f"{{ a: {a} }} {{ x: {b}, a: {a} }}"),
       "Spreading undefined adds nothing."),
    TS('console.log(Boolean(null), Boolean(undefined), Boolean("null"));', "false false true",
       "The word null in quotes is a non-empty string, so it is truthy."),
    TS("function f(o: { n?: number }) { return o.n === undefined; }\nconsole.log(f({}), f({ n: 0 }));", "true false",
       "0 is a real value, not undefined."),
]
