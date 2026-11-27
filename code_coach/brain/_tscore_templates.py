"""TypeScript core pack, part 4: template literals for TS Eval.

`${...}` inside backticks runs the expression and puts its STRING form in the text: a number in its shortest form, an
array joined with commas (no brackets, no spaces), an object as `[object Object]`, null and undefined as their names,
a boolean as `true`/`false`. In a template below, TypeScript's own `${` is written `$${` (string.Template's escape), so
`$${n}` is TypeScript and `$a` is a hole. Every answer is worked out by hand; tests/ts_oracle.py runs each for real.
"""

from __future__ import annotations

from fractions import Fraction

from ._model import Maker
from ._ts_model import TS
from ._tscore_basics import K, fixed, jsb

TEMPLATE_LITERALS: list[Maker] = [
    TS("const n = $a;\nconsole.log(`n is $${n}`);",
       K(lambda a, **_: f"n is {a}"),
       "The value of n is put into the text where the placeholder is."),
    TS("console.log(`$${$a} + $${$b} = $${$a + $b}`);",
       K(lambda a, b, **_: f"{a} + {b} = {a + b}"),
       "Each placeholder is worked out on its own; only the last one adds."),
    TS('const w = "$w";\nconsole.log(`[$${w.length}]`);',
       K(lambda w, **_: f"[{len(w)}]"),
       "Any expression may sit inside a placeholder, here the length of the word."),
    TS('console.log(`$${"$a" + $b}`);',
       K(lambda a, b, **_: f"{a}{b}"),
       "A string plus a number joins them as text before the template sees it."),
    TS("console.log(`$${$a > $b}`);",
       K(lambda a, b, **_: jsb(a > b)),
       "A boolean becomes the word true or false in the text."),
    TS("const xs = [$a, $b, $c];\nconsole.log(`$${xs}`);",
       K(lambda a, b, c, **_: f"{a},{b},{c}"),
       "An array in a template is joined with commas, with no brackets and no spaces."),
    TS("const o = { n: $a };\nconsole.log(`got $${o}`);",
       "got [object Object]",
       "A plain object turns into the text [object Object], not its fields."),
    TS("const v: number | null = null;\nconsole.log(`$${v}-$a`);",
       K(lambda a, **_: f"null-{a}"),
       "null is written as the word null in a template."),
    TS("const v: string | undefined = undefined;\nconsole.log(`$a$${v}`);",
       K(lambda a, **_: f"{a}undefined"),
       "undefined is written as the word undefined in a template."),
    TS('const n = $n;\nconsole.log(`$${n % 2 === 0 ? "even" : "odd"}`);',
       K(lambda n, **_: "even" if n % 2 == 0 else "odd"),
       "A ternary inside the placeholder picks which text goes in."),
    TS('const w = "$w";\nconsole.log(`$${w[0].toUpperCase()}$${w.slice(1)}`);',
       K(lambda w, **_: w[0].upper() + w[1:]),
       "Two templates side by side: the first letter in capitals, then the rest."),
    TS("const n = $n;\nconsole.log(`a$${`$${n}`.length}`);",
       K(lambda n, **_: f"a{len(str(n))}"),
       "The inner template makes the text of n, and its length is the number of digits."),
    TS("console.log(`$${($a / $h).toFixed(2)}`);",
       K(lambda a, h, **_: fixed(Fraction(a, h), 2)),
       "toFixed(2) gives text with exactly two decimals, which the template puts in as it is."),
    TS("const x = $a;\nconsole.log(`$${x}` + $b);",
       K(lambda a, b, **_: f"{a}{b}"),
       "A template always makes a string, so adding a number joins it on as text."),
    TS("const x = $a;\nconsole.log(typeof `$${x}`);",
       "string",
       "Whatever goes inside, a template literal is a string."),
    TS('const w = "$w";\nconsole.log(`$${w}`.length === w.length);',
       "true",
       "Putting a string alone in a template gives the same text back."),
    TS("const a = $a, b = $b;\nconsole.log(`$${a}$${b}` === String(a) + String(b));",
       "true",
       "Two numbers side by side in a template are joined as text, not added."),
    TS("const n = $a;\nconsole.log(`$${n}` === n.toString());",
       "true",
       "A number in a template turns into the same text as toString gives."),
]
