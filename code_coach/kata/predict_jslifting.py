"""Predict the output, in JavaScript, for a lifting log.

A training tracker is small, friendly arithmetic, and most of what goes
wrong in one is JavaScript being itself in the middle of it: reps that
arrive from a form as the string '5', a plate total formatted with
toFixed and then added to, a personal-records Map whose order is not the
order you expected, a rest day whose volume crashes reduce, and a
"copy" of Monday's workout that is still Monday's workout.

Every snippet runs in plain Node, with no page and no clock. The numbers
are kilograms on a 20 kg bar. Every expected output was worked out by
hand first and then checked against what Node printed, and
tests/test_predict_jsplanets_lifting.py keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

LIFTING = "Bodybuilding"


JS_LIFTING_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsbb-rest-clock",
        level=1,
        name="The rest timer's clock",
        family=LIFTING,
        language="javascript",
        code=(
            "const clock = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;\n"
            "console.log(clock(90), clock(65), clock(600));\n"
            "console.log('rest'.padStart(2, '-'), 'go'.padStart(4, '-'));"
        ),
        expect="1:30 1:05 10:00\nrest --go",
        why=(
            "padStart's number is the length the string should end up, "
            "not how many characters to add. '5' padded to 2 is '05', "
            "and '30' is already 2 long, so it is left alone. A string "
            "that is already long enough comes back unchanged and is "
            "never cut down, so 'rest' stays 'rest' - which is also why "
            "padStart is safe to call on every number, however big."
        ),
    ),
    _p(
        id="predict-jsbb-plate-label",
        level=1,
        name="The label on the bar",
        family=LIFTING,
        language="javascript",
        code=(
            "const perSide = ((100 - 20) / 2).toFixed(1);\n"
            "const total = perSide * 2 + 20;\n"
            "const shown = perSide + perSide;\n"
            "console.log(perSide, total, shown);"
        ),
        expect="40.0 100 40.040.0",
        why=(
            "toFixed gives back a string, ready to display. `*` only "
            "works on numbers, so '40.0' * 2 turns the string back into "
            "a number and the total comes out right. `+` is different: "
            "if either side is a string it joins them, so the label "
            "added to itself is '40.040.0'. Keep the number for the "
            "arithmetic and call toFixed when you print."
        ),
    ),
    _p(
        id="predict-jsbb-sets-of-eight",
        level=1,
        name="Fifty reps in sets of eight",
        family=LIFTING,
        language="javascript",
        code=(
            "const totalReps = 50;\n"
            "const perSet = 8;\n"
            "console.log(totalReps / perSet);\n"
            "console.log(Math.floor(totalReps / perSet), totalReps % perSet);"
        ),
        expect="6.25\n6 2",
        why=(
            "JavaScript has no integer division: `/` always gives the "
            "exact answer, so 50 reps in sets of 8 is 6.25 sets. "
            "Math.floor turns that into the 6 full sets, and `%` gives "
            "the remainder - 2 reps left over for a short seventh set. "
            "Together they do what Python writes as // and %."
        ),
    ),
    _p(
        id="predict-jsbb-form-reps",
        level=2,
        name="Reps from an input box",
        family=LIFTING,
        language="javascript",
        code=(
            "const form = { reps: '5', kg: '100' };\n"
            "console.log(form.reps == 5, form.reps === 5);\n"
            "console.log(form.reps + 1, form.reps - 1, form.kg * 2);"
        ),
        expect="true false\n51 4 200",
        why=(
            "Whatever is typed into a form arrives as a string. `==` "
            "converts before comparing, so '5' == 5 is true; `===` "
            "compares without converting, and a string is never equal "
            "to a number. The arithmetic splits the same way: `+` with "
            "a string glues, giving '51', while `-` and `*` only work on "
            "numbers, so they convert first. Convert input with Number() "
            "once, as soon as it arrives."
        ),
    ),
    _p(
        id="predict-jsbb-plates-and-tenths",
        level=2,
        name="Plates add up, tenths do not",
        family=LIFTING,
        language="javascript",
        code=(
            "const loaded = 20 + 2 * (1.25 + 2.5);\n"
            "const gained = 0.1 + 0.2;\n"
            "console.log(loaded === 27.5, gained === 0.3);\n"
            "console.log(loaded, gained);"
        ),
        expect="true false\n27.5 0.30000000000000004",
        why=(
            "Plates come in halves and quarters, like 2.5 and 1.25, and "
            "those have exact binary forms, so a loaded bar adds up to "
            "exactly 27.5. Tenths do not: 0.1 and 0.2 are each a hair "
            "off in binary, and the error shows when they are added, as "
            "in two weigh-ins of 0.1 and 0.2 kg gained. Round for "
            "display - Math.round(x * 10) / 10 - and never compare "
            "tenths with ===."
        ),
    ),
    _p(
        id="predict-jsbb-pr-map-order",
        level=2,
        name="Personal records in a Map",
        family=LIFTING,
        language="javascript",
        code=(
            "const prs = new Map([['squat', 140], ['bench', 100], ['deadlift', 180]]);\n"
            "prs.set('bench', 105);\n"
            "prs.delete('squat');\n"
            "prs.set('squat', 150);\n"
            "console.log([...prs.keys()].join(', '));\n"
            "console.log(prs.get('bench'), prs.size);"
        ),
        expect="bench, deadlift, squat\n105 3",
        why=(
            "A Map remembers the order its keys were first set. Setting "
            "bench again changes its value but not its place. Deleting "
            "squat and setting it again adds it as a new key, so it "
            "goes to the end. There are still three records, and bench "
            "holds the new one."
        ),
    ),
    _p(
        id="predict-jsbb-rest-day-volume",
        level=2,
        name="The volume of a rest day",
        family=LIFTING,
        language="javascript",
        code=(
            "const today = [];\n"
            "console.log(today.reduce((sum, s) => sum + s.kg * s.reps, 0));\n"
            "try {\n"
            "  console.log(today.reduce((sum, s) => sum + s.kg * s.reps));\n"
            "} catch (e) {\n"
            "  console.log(e.name);\n"
            "}"
        ),
        expect="0\nTypeError",
        why=(
            "With a starting value, reduce over an empty array simply "
            "hands the starting value back: 0 kg on a rest day. Without "
            "one, reduce has nothing to start from - no first element "
            "to borrow - and throws a TypeError. A log that can be "
            "empty needs the 0 every time."
        ),
    ),
    _p(
        id="predict-jsbb-ranked-in-place",
        level=2,
        name="Ranking the lifts",
        family=LIFTING,
        language="javascript",
        code=(
            "const lifts = [140, 100, 180];\n"
            "const ranked = lifts.sort((a, b) => b - a);\n"
            "console.log(lifts, ranked === lifts);\n"
            "const ascending = lifts.toSorted((a, b) => a - b);\n"
            "console.log(lifts, ascending);"
        ),
        expect="[ 180, 140, 100 ] true\n[ 180, 140, 100 ] [ 100, 140, 180 ]",
        why=(
            "sort rearranges the array it is called on and returns that "
            "same array, so ranked and lifts are two names for one list "
            "and the original order is gone. toSorted, from ES2023, "
            "returns a sorted copy and leaves the array alone, which is "
            "why lifts still reads heaviest first after it."
        ),
    ),
    _p(
        id="predict-jsbb-max-of-nothing",
        level=3,
        name="The best deadlift never lifted",
        family=LIFTING,
        language="javascript",
        code=(
            "const log = [{ lift: 'squat', kg: 140 }, { lift: 'bench', kg: 100 }];\n"
            "const best = (lift) => {\n"
            "  const weights = log.filter((s) => s.lift === lift).map((s) => s.kg);\n"
            "  return Math.max(...weights);\n"
            "};\n"
            "console.log(best('squat'), best('deadlift'));\n"
            "console.log(Math.max(log.map((s) => s.kg)));"
        ),
        expect="140 -Infinity\nNaN",
        why=(
            "Math.max with nothing to compare returns -Infinity - the "
            "starting point every number beats - so a lift with no sets "
            "reports -Infinity rather than an error. And Math.max does "
            "not look inside an array: handed the array itself, it turns "
            "it into the text '140,100', which is not a number, so the "
            "answer is NaN. Spread the array with ..., and check for an "
            "empty list first."
        ),
    ),
    _p(
        id="predict-jsbb-copied-workout",
        level=3,
        name="Copying Monday's workout",
        family=LIFTING,
        language="javascript",
        code=(
            "const monday = { name: 'Push', sets: [{ lift: 'bench', kg: 100 }] };\n"
            "const thursday = { ...monday, name: 'Push B' };\n"
            "thursday.sets[0].kg = 90;\n"
            "thursday.sets.push({ lift: 'dips', kg: 0 });\n"
            "console.log(monday.name, monday.sets[0].kg, monday.sets.length);\n"
            "const friday = structuredClone(monday);\n"
            "friday.sets[0].kg = 110;\n"
            "console.log(monday.sets[0].kg, friday.sets === monday.sets);"
        ),
        expect="Push 90 2\n90 false",
        why=(
            "The spread copies the top level only. thursday gets its own "
            "name, but its sets is the very same array as monday's, so "
            "lightening a set or adding one through thursday changes "
            "Monday's workout too. structuredClone copies all the way "
            "down: friday's sets is a new array of new objects, and "
            "changing it leaves Monday alone."
        ),
    ),
    _p(
        id="predict-jsbb-filled-week",
        level=3,
        name="Three training days, one list",
        family=LIFTING,
        language="javascript",
        code=(
            "const week = Array(3).fill([]);\n"
            "week[0].push('squat');\n"
            "console.log(week);\n"
            "const fixed = Array.from({ length: 3 }, () => []);\n"
            "fixed[0].push('squat');\n"
            "console.log(fixed);"
        ),
        expect="[ [ 'squat' ], [ 'squat' ], [ 'squat' ] ]\n[ [ 'squat' ], [], [] ]",
        why=(
            "fill puts the same value into every slot, and the value "
            "here is one array, so all three days hold the very same "
            "list: push onto Monday's and every day has squats. "
            "Array.from with a function calls it once per slot, and "
            "each call makes a fresh empty list."
        ),
    ),
)
