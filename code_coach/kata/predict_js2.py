"""More JavaScript to predict: throwing, and numbers on screen.

Two families the set was missing.

Throwing and catching, because try/catch is the first thing a beginner
is told to reach for and almost none of what it does is guessable. It
does not see into a promise unless you await. finally runs after the
return has been decided and can overrule it. A thrown string is not an
Error and has no message. Each of those is a thing you find out once,
usually at the worst moment.

Numbers on screen, because turning a number into text is where a
program meets a person, and every one of these is a rule rather than a
calculation: where parseInt stops reading, what toFixed hands back,
which way Math.round takes a negative half.

Every expected output here was checked against Node, and the suite
keeps checking — same way round as the rest of predict.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


# ── Throwing and catching ────────────────────────────────────

THROWING: tuple[Puzzle, ...] = (
    _p(
        id="predict-js-finally-runs",
        level=2,
        language="javascript",
        name="finally, after the return",
        family="Throwing and catching",
        code=(
            "function risky() {\n"
            "  try {\n"
            '    return "try";\n'
            "  } finally {\n"
            '    console.log("finally");\n'
            "  }\n"
            "}\n"
            "console.log(risky());"
        ),
        expect="finally\ntry",
        why=(
            "The return value is worked out first, then finally runs, "
            "then the function actually returns — so the log inside "
            "finally happens before the value reaches the caller. That "
            "is what finally is for: it runs on the way out however you "
            "leave, including on the way out of a return."
        ),
    ),
    _p(
        id="predict-js-throw-a-string",
        level=3,
        language="javascript",
        name="Throwing something that is not an Error",
        family="Throwing and catching",
        code=(
            "try {\n"
            '  throw "just a string";\n'
            "} catch (err) {\n"
            "  console.log(typeof err, err.message);\n"
            "}"
        ),
        expect="string undefined",
        why=(
            "JavaScript lets you throw anything, and what you catch is "
            "exactly what was thrown. A string has no .message, so the "
            "usual `err.message` prints undefined — which is why "
            "catch blocks that assume an Error quietly report nothing, "
            "and why you throw `new Error(...)` rather than text."
        ),
    ),
    _p(
        id="predict-js-await-lets-catch-see-it",
        level=3,
        language="javascript",
        name="What await lets catch see",
        family="Throwing and catching",
        code=(
            "async function boom() {\n"
            '  throw new Error("nope");\n'
            "}\n"
            "async function main() {\n"
            "  try {\n"
            "    await boom();\n"
            "  } catch (err) {\n"
            '    console.log("caught", err.message);\n'
            "  }\n"
            "}\n"
            "main();"
        ),
        expect="caught nope",
        why=(
            "A throw inside an async function becomes a rejected "
            "promise, and a try/catch only sees it because of the "
            "await — without that word the call returns a rejected "
            "promise, the try block finishes happily, and the catch is "
            "never reached. The most common version of this bug is a "
            "missing await, not a missing catch."
        ),
    ),
    _p(
        id="predict-js-then-skipped",
        level=4,
        language="javascript",
        name="The then that never runs",
        family="Throwing and catching",
        code=(
            "Promise.resolve(1)\n"
            "  .then(() => {\n"
            '    throw new Error("in then");\n'
            "  })\n"
            '  .then(() => console.log("second then"))\n'
            '  .catch((e) => console.log("caught:", e.message));'
        ),
        expect="caught: in then",
        why=(
            "Once something throws, the chain skips every then between "
            "there and the next catch. The second then is not run and "
            "not reported — it is simply stepped over. That is why a "
            "catch belongs at the end of a chain rather than in the "
            "middle of one."
        ),
    ),
    _p(
        id="predict-js-catch-recovers",
        level=5,
        language="javascript",
        name="Carrying on after a catch",
        family="Throwing and catching",
        code=(
            'Promise.reject(new Error("x"))\n'
            "  .catch(() => 2)\n"
            "  .then((v) => console.log(v * 21));"
        ),
        expect="42",
        why=(
            "A catch that returns a value hands the chain back to "
            "normal, so the then after it runs with that value. The "
            "chain is only still broken if the catch itself throws or "
            "returns a rejected promise. This is how retries and "
            "fallbacks are written — and also how a swallowed error "
            "turns into a program that carries on with nonsense."
        ),
    ),
)


# ── Numbers on screen ────────────────────────────────────────

NUMBERS_OUT: tuple[Puzzle, ...] = (
    _p(
        id="predict-js-parseint-stops",
        level=2,
        language="javascript",
        name="Where parseInt gives up",
        family="Numbers on screen",
        code=(
            'console.log(parseInt("12px"));\n'
            'console.log(Number("12px"));\n'
            'console.log(parseInt(""));'
        ),
        expect="12\nNaN\nNaN",
        why=(
            "parseInt reads from the front and stops at the first thing "
            "that is not a digit, so it is happy with trailing rubbish. "
            "Number wants the whole string to be a number and gives NaN "
            "otherwise. Which you want depends on whether '12px' should "
            "be 12 or should be an error — and picking the wrong one is "
            "how a form accepts '3 bananas' as a quantity."
        ),
    ),
    _p(
        id="predict-js-tofixed-is-text",
        level=3,
        language="javascript",
        name="What toFixed hands back",
        family="Numbers on screen",
        code=(
            "const price = 5;\n"
            "const shown = price.toFixed(2);\n"
            "console.log(shown);\n"
            "console.log(typeof shown);\n"
            "console.log(shown + 1);"
        ),
        expect="5.00\nstring\n5.001",
        why=(
            "toFixed returns text, not a number — it is for showing, "
            "and the moment you do arithmetic on the result you get "
            "string joining instead. Format at the very end, once, and "
            "keep numbers as numbers everywhere else."
        ),
    ),
    _p(
        id="predict-js-round-negative-half",
        level=4,
        language="javascript",
        name="Rounding a negative half",
        family="Numbers on screen",
        code="console.log(Math.round(2.5), Math.round(-2.5), Math.round(-2.6));",
        expect="3 -2 -3",
        why=(
            "Math.round always goes up on a tie, and up from -2.5 is "
            "-2, not -3. So rounding is not symmetric about zero, and "
            "a total built from rounded positives and negatives drifts "
            "in one direction. Math.trunc, Math.floor and Math.ceil all "
            "treat negatives differently again."
        ),
    ),
    _p(
        id="predict-js-padstart",
        level=2,
        language="javascript",
        name="Padding a number out",
        family="Numbers on screen",
        code=(
            'console.log(String(7).padStart(3, "0"));\n'
            'console.log(String(1234).padStart(3, "0"));\n'
            'console.log("7".padStart(3));'
        ),
        expect="007\n1234\n  7",
        why=(
            "padStart only adds when it is short, so it never truncates "
            "— a number already longer than the width comes back whole. "
            "The pad defaults to a space. This is the whole of clock "
            "and invoice formatting, and it needs a string first, which "
            "is what String(7) is doing."
        ),
    ),
    _p(
        id="predict-js-big-integers",
        level=5,
        language="javascript",
        name="Where whole numbers stop being exact",
        family="Numbers on screen",
        code=(
            "console.log(9007199254740992 === 9007199254740993);\n"
            "console.log(Number.isSafeInteger(9007199254740993));"
        ),
        expect="true\nfalse",
        why=(
            "Every number in JavaScript is a float, and past about nine "
            "quadrillion the gaps between the ones it can hold are "
            "bigger than one — so two different whole numbers become "
            "the same value and compare as equal. Ids from a database "
            "live in exactly this range, which is why they are so often "
            "sent as strings."
        ),
    ),
)


JS_PUZZLES_2: tuple[Puzzle, ...] = THROWING + NUMBERS_OUT
