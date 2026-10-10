"""Predict the output, in JavaScript, for code about music and sound.

Studio arithmetic runs straight into the language's number traps. A note
number transposed below zero meets the remainder operator's sign. Beat
times are built from fractions like 0.1 that have no exact binary form.
A quantizer meets Math.round on exact halves, in both directions. Tempos
sort as text unless told otherwise. A frequency formula is only right if
the exponent is parenthesised the way it was written. A tempo typed
into a box is a string with units on the end. And a step sequencer built
with fill shares one row between every step.

Every snippet runs in plain Node with no page and no audio. Every
expected output was worked out by hand first and then checked against
what Node printed, and tests/test_predict_jsnode_music_cooking.py keeps
checking. Results that depend on how floating point rounds in the last
digit are shown with toFixed, except where the last digit is the lesson
and is a well-known one (0.1 + 0.2).
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

MUSIC = "Music"


JS_MUSIC_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsms-transpose-negative",
        level=1,
        name="Transposing below zero",
        family=MUSIC,
        language="javascript",
        code=(
            "const pitchClass = (n) => n % 12;\n"
            "console.log(pitchClass(61), pitchClass(-1), pitchClass(-13));\n"
            "const fixed = (n) => ((n % 12) + 12) % 12;\n"
            "console.log(fixed(61), fixed(-1), fixed(-13));"
        ),
        expect="1 -1 -1\n1 11 11",
        why=(
            "`%` is a remainder, not a true modulo, and its sign "
            "follows the number on the left. A note transposed down "
            "past zero is negative, and -1 % 12 is -1, so an index "
            "into a list of twelve note names finds nothing: "
            "NAMES[-1] is undefined. Adding 12 and taking the "
            "remainder again lands everything in 0 to 11: -1 becomes "
            "11 (B), and -13, a whole octave and one semitone further "
            "down, also becomes 11."
        ),
    ),
    _p(
        id="predict-jsms-beat-times",
        level=1,
        name="Beats at a tenth of a second",
        family=MUSIC,
        language="javascript",
        code=(
            "const beat = 0.1 + 0.2;\n"
            "console.log(beat, beat === 0.3);\n"
            "console.log(Math.abs(beat - 0.3) < 1e-9, (beat * 1000).toFixed(0));"
        ),
        expect="0.30000000000000004 false\ntrue 300",
        why=(
            "0.1 and 0.2 have no exact form in binary, as one third has "
            "none in decimal, and their sum lands a hair above 0.3. "
            "Comparing with === asks for exact equality and says false; "
            "a scheduler comparing event times that way will miss "
            "notes. Compare with a small tolerance instead, or count "
            "in whole units - milliseconds, samples or ticks - and "
            "only convert at the end."
        ),
    ),
    _p(
        id="predict-jsms-bpm-text",
        level=1,
        name="A tempo typed into a box",
        family=MUSIC,
        language="javascript",
        code=(
            "const text = '120bpm';\n"
            "console.log(Number(text), parseInt(text), parseFloat('92.5 bpm'));\n"
            "console.log(Number(''), Number(' 128 '), parseInt(''));"
        ),
        expect="NaN 120 92.5\n0 128 NaN",
        why=(
            "Number is strict: the whole string must be a number, so the "
            "'bpm' on the end makes it NaN. parseInt and parseFloat read "
            "as far as the number goes and stop, so they take the 120 "
            "and the 92.5. The empty string is the odd one: Number('') "
            "is 0 - a blank tempo box quietly becomes a tempo of zero - "
            "while parseInt('') finds no digits and gives NaN. Spaces "
            "around a number are ignored by both."
        ),
    ),
    _p(
        id="predict-jsms-sort-bpms",
        level=2,
        name="Sorting tempos",
        family=MUSIC,
        language="javascript",
        code=(
            "const bpms = [90, 128, 100, 75, 140];\n"
            "console.log(bpms.sort());\n"
            "console.log(bpms.sort((a, b) => a - b));\n"
            "console.log(bpms.map(String).sort().join(' '));"
        ),
        expect=(
            "[ 100, 128, 140, 75, 90 ]\n"
            "[ 75, 90, 100, 128, 140 ]\n"
            "100 128 140 75 90"
        ),
        why=(
            "With no compare function, sort converts every item to a "
            "string and orders them as text, a character at a time. "
            "'100' comes before '75' because '1' comes before '7', so "
            "the slowest tempo lands in the middle. A compare function "
            "that subtracts sorts numerically. The last line shows the "
            "text order again, even on tempos that are already in "
            "order - it is the same trap a track list sorted by BPM "
            "falls into."
        ),
    ),
    _p(
        id="predict-jsms-round-halves",
        level=2,
        name="Quantizing exactly between two lines",
        family=MUSIC,
        language="javascript",
        code=(
            "const grid = 0.5;\n"
            "const times = [0.25, 0.75, 1.25, -0.25];\n"
            "console.log(times.map((t) => Math.round(t / grid)));\n"
            "console.log(times.map((t) => Math.round(t / grid) * grid));\n"
            "console.log(Math.round(-0.5), Math.round(-1.5));"
        ),
        expect=(
            "[ 1, 2, 3, -0 ]\n"
            "[ 0.5, 1, 1.5, -0 ]\n"
            "-0 -1"
        ),
        why=(
            "A note exactly halfway between two grid lines is a tie, "
            "and Math.round settles ties upwards - towards positive "
            "infinity - not to the nearest even number and not away "
            "from zero. So 0.5, 1.5 and 2.5 become 1, 2 and 3, and "
            "-1.5 becomes -1 where a symmetrical rule would give -2. "
            "Rounding -0.25 / 0.5 = -0.5 produces negative zero, which "
            "console.log prints as -0; it equals 0 in every comparison "
            "but turns up in output."
        ),
    ),
    _p(
        id="predict-jsms-semitone-precedence",
        level=2,
        name="Where the bracket goes",
        family=MUSIC,
        language="javascript",
        code=(
            "const m = 61;\n"
            "console.log((440 * 2 ** (m - 69) / 12).toFixed(4));\n"
            "console.log((440 * 2 ** ((m - 69) / 12)).toFixed(2));\n"
            "console.log(2 ** 1 / 12 === 1 / 6, (2 ** (1 / 12)).toFixed(4));"
        ),
        expect="0.1432\n277.18\ntrue 1.0595",
        why=(
            "** binds tighter than * and /, so the first formula "
            "raises 2 to the power of -8 - a whole number of octaves - "
            "gets 1/256, multiplies by 440 and then divides by 12. "
            "That is a tiny number, not a pitch. The right formula puts "
            "the division inside the exponent, 2 ** ((m - 69) / 12), so "
            "each semitone is a twelfth of an octave, and middle C's "
            "neighbour C#4 comes out at 277.18 Hz. The last line shows "
            "the same trap in miniature: 2 ** 1 / 12 is 2 / 12, while "
            "the semitone ratio is 2 ** (1 / 12), about 1.0595."
        ),
    ),
    _p(
        id="predict-jsms-tap-tempo",
        level=2,
        name="Tapping a tempo",
        family=MUSIC,
        language="javascript",
        code=(
            "const taps = [0, 500, 1000, 1500];\n"
            "const gaps = taps.slice(1).map((t, i) => t - taps[i]);\n"
            "const avg = gaps.reduce((a, b) => a + b) / gaps.length;\n"
            "console.log(gaps, avg, 60000 / avg);\n"
            "try {\n"
            "  console.log([1000].slice(1).reduce((a, b) => a + b));\n"
            "} catch (e) {\n"
            "  console.log(e.name);\n"
            "}"
        ),
        expect="[ 500, 500, 500 ] 500 120\nTypeError",
        why=(
            "Four taps make three gaps, always one fewer than the taps: "
            "map's index i reaches back to the previous tap. Three "
            "gaps of 500 ms average 500, which is 120 beats a minute. "
            "The second half shows reduce with no starting value: on "
            "an empty list it has nothing to start from and throws a "
            "TypeError. A single tap makes an empty list of gaps, so "
            "the first tap of a tap-tempo button crashes unless reduce "
            "is given a starting 0 or the length is checked first."
        ),
    ),
    _p(
        id="predict-jsms-log-of-zero",
        level=3,
        name="Silence in decibels",
        family=MUSIC,
        language="javascript",
        code=(
            "const db = (x) => 20 * Math.log10(x);\n"
            "console.log(db(1), db(0), db(-0.5));\n"
            "console.log(db(0.5).toFixed(1), Math.round(db(0.5)));\n"
            "console.log([0.5, 1, 2].map((x) => db(x).toFixed(1)).join(' '));"
        ),
        expect="0 -Infinity NaN\n-6.0 -6\n-6.0 0.0 6.0",
        why=(
            "Full scale is a ratio of 1, which is 0 dB. Half the "
            "amplitude is about -6.02 dB, and double is +6.02. "
            "But the logarithm of zero is minus infinity, so a "
            "silent sample gives -Infinity, which will wreck any "
            "meter that averages or draws it - clamp it to a floor "
            "such as -100 first. The logarithm of a negative number is "
            "NaN, which is why a decibel meter takes the absolute "
            "value of a sample before the log. toFixed(1) turns "
            "-6.02 into the string '-6.0', where Math.round gives the "
            "number -6."
        ),
    ),
    _p(
        id="predict-jsms-fill-shared-row",
        level=3,
        name="A grid where every step shares a row",
        family=MUSIC,
        language="javascript",
        code=(
            "const grid = new Array(3).fill([]);\n"
            "grid[0].push('kick');\n"
            "console.log(grid);\n"
            "const grid2 = Array.from({ length: 3 }, () => []);\n"
            "grid2[0].push('kick');\n"
            "console.log(grid2);\n"
            "console.log(new Array(4).map((_, i) => i), Array(4).fill(0).map((_, i) => i));"
        ),
        expect=(
            "[ [ 'kick' ], [ 'kick' ], [ 'kick' ] ]\n"
            "[ [ 'kick' ], [], [] ]\n"
            "[ <4 empty items> ] [ 0, 1, 2, 3 ]"
        ),
        why=(
            "fill puts the very same value in every slot. With a "
            "number that is harmless, but with an array it is one "
            "array in three places, so a kick added to step 0 appears "
            "at every step. Array.from with a function builds a new "
            "array for each slot. The last line shows the other trap "
            "of new Array(n): its slots are empty, not undefined, and "
            "map skips empty slots entirely, so the result is still "
            "four holes. Fill it first, or use Array.from."
        ),
    ),
    _p(
        id="predict-jsms-accumulated-time",
        level=3,
        name="Adding a tenth four times",
        family=MUSIC,
        language="javascript",
        code=(
            "let t = 0;\n"
            "const times = [];\n"
            "for (let i = 0; i < 4; i++) {\n"
            "  times.push(t);\n"
            "  t += 0.1;\n"
            "}\n"
            "console.log(times);\n"
            "console.log(times.map((x) => Math.round(x * 1000)));\n"
            "console.log(times.at(-1) === 0.3, times.at(-1).toFixed(2) === '0.30');"
        ),
        expect=(
            "[ 0, 0.1, 0.2, 0.30000000000000004 ]\n"
            "[ 0, 100, 200, 300 ]\n"
            "false true"
        ),
        why=(
            "Each addition of 0.1 carries a tiny error, and the "
            "errors pile up: 0.1 and 0.2 happen to survive, but the "
            "fourth note lands at 0.30000000000000004, which is not "
            "equal to 0.3. A sequencer that steps its clock by adding "
            "a fraction every tick drifts further over a long song. "
            "Count whole steps in an integer and multiply - or work in "
            "milliseconds - and rounding to a unit, as the second line "
            "does, hides the error from anything that compares."
        ),
    ),
)
