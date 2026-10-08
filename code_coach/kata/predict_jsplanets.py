"""Predict the output, in JavaScript, for code about the planets.

Astronomy data is a good place to meet JavaScript's sharp edges, because
it is exactly the data they cut: numbers too big for an integer's habits
(a diameter of 142,984 km sorted as text), negative ones where code
assumed positive (Venus turns backwards, so its rotation is listed as a
negative number of hours), figures that arrive as strings from an API or
a form, and a list of eight things where the first one is at position 0.

Every snippet runs in plain Node, with no page and no network. The
figures are NASA's Planetary Fact Sheet where a real one is used. Every
expected output was worked out by hand first and then checked against
what Node printed, and tests/test_predict_jsplanets_lifting.py keeps
checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

PLANETS = "Planets"


JS_PLANETS_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jspl-missing-jupiter",
        level=1,
        name="The planet that was skipped",
        family=PLANETS,
        language="javascript",
        code=(
            "const planets = ['Mercury', 'Venus', 'Earth', 'Mars'];\n"
            "planets[5] = 'Saturn';\n"
            "console.log(planets.length, planets[4]);"
        ),
        expect="6 undefined",
        why=(
            "Writing to index 5 of a four-item array is not an error: "
            "Saturn goes in at 5, and the length becomes 6, one more "
            "than the highest index. Index 4 - where Jupiter belonged - "
            "was never written, so it is a hole, and reading a hole "
            "gives undefined, just as reading past the end does. "
            "console.log(planets) would show it as <1 empty item>. Use "
            "push to add to the end, so nothing can be skipped."
        ),
    ),
    _p(
        id="predict-jspl-const-array",
        level=1,
        name="A const list of planets",
        family=PLANETS,
        language="javascript",
        code=(
            "const planets = ['Mercury', 'Venus'];\n"
            "planets.push('Earth');\n"
            "try {\n"
            "  planets = ['Pluto'];\n"
            "} catch (e) {\n"
            "  console.log(e.name);\n"
            "}\n"
            "console.log(planets.join(', '));"
        ),
        expect="TypeError\nMercury, Venus, Earth",
        why=(
            "`const` stops the name `planets` from being pointed at a "
            "different array. It does not stop the array it points at "
            "from changing, so push works and Earth goes in. Pointing "
            "the name at a whole new array is the one thing const "
            "forbids, and it throws a TypeError at the moment it runs. "
            "If the contents must not change either, that is a job for "
            "Object.freeze."
        ),
    ),
    _p(
        id="predict-jspl-sort-diameters",
        level=2,
        name="Sorting the diameters",
        family=PLANETS,
        language="javascript",
        code=(
            "const diametersKm = [12756, 6792, 142984, 4879];\n"
            "console.log(diametersKm.sort());\n"
            "console.log(diametersKm.sort((a, b) => a - b));"
        ),
        expect="[ 12756, 142984, 4879, 6792 ]\n[ 4879, 6792, 12756, 142984 ]",
        why=(
            "With no compare function, sort turns every element into a "
            "string and puts them in text order, a character at a time. "
            "As text, '12756' comes before '142984' because 2 comes "
            "before 4, and both come before anything starting with 4 or "
            "6. Numbers need a compare function: `(a, b) => a - b` is "
            "negative when a belongs first, which sorts smallest to "
            "largest. Both calls change the array itself and return it."
        ),
    ),
    _p(
        id="predict-jspl-tofixed-compare",
        level=2,
        name="Which planet pulls harder",
        family=PLANETS,
        language="javascript",
        code=(
            "const earthG = (9.8).toFixed(1);\n"
            "const jupiterG = (23.1).toFixed(1);\n"
            "console.log(earthG > jupiterG, typeof earthG);\n"
            "console.log(Number(earthG) > Number(jupiterG));"
        ),
        expect="true string\nfalse",
        why=(
            "toFixed is for showing a number, and what it hands back is "
            "a string. Two strings compared with `>` are compared as "
            "text, one character at a time, so '9.8' beats '23.1' "
            "because 9 comes after 2. Turn them back into numbers "
            "before comparing - or better, keep the numbers and only "
            "call toFixed at the moment you print."
        ),
    ),
    _p(
        id="predict-jspl-venus-days",
        level=2,
        name="Venus turns the other way",
        family=PLANETS,
        language="javascript",
        code=(
            "const venusRotationHours = -5832.5;\n"
            "const days = venusRotationHours / 24;\n"
            "console.log(Math.trunc(days), Math.floor(days));\n"
            "console.log(Math.round(days), Math.ceil(days));"
        ),
        expect="-243 -244\n-243 -243",
        why=(
            "NASA lists Venus's rotation as a negative number of hours "
            "because it spins backwards, and divided by 24 it is about "
            "-243.02 days. Math.trunc drops the fraction, moving towards "
            "zero: -243. Math.floor always moves down, and down from "
            "-243.02 is -244. For positive numbers the two agree, which "
            "is why the difference hides until a negative turns up. "
            "Math.round goes to the nearest, and Math.ceil goes up, "
            "which for a negative is towards zero."
        ),
    ),
    _p(
        id="predict-jspl-index-zero",
        level=2,
        name="Mercury is at position zero",
        family=PLANETS,
        language="javascript",
        code=(
            "const planets = ['Mercury', 'Venus', 'Earth', 'Mars'];\n"
            "if (planets.indexOf('Mercury')) console.log('found Mercury');\n"
            "else console.log('no Mercury');\n"
            "console.log(planets.indexOf('Pluto') ? 'found Pluto' : 'no Pluto');"
        ),
        expect="no Mercury\nfound Pluto",
        why=(
            "indexOf answers with a position, not a yes or a no. Mercury "
            "is first, at position 0, and 0 is falsy, so the if takes the "
            "else. Pluto is not in the list, and indexOf's way of saying "
            "so is -1, which is truthy. Both answers are backwards. "
            "Compare with `!== -1`, or ask the question you mean: "
            "includes returns true or false."
        ),
    ),
    _p(
        id="predict-jspl-parse-mass",
        level=2,
        name="Reading a mass from text",
        family=PLANETS,
        language="javascript",
        code=(
            "const massText = '1.898e27';\n"
            "console.log(parseInt(massText), parseFloat(massText));\n"
            "console.log(Number(massText) === 1.898e27, Number('1,898'));"
        ),
        expect="1 1.898e+27\ntrue NaN",
        why=(
            "parseInt reads digits until it meets something that cannot "
            "be part of a whole number, then stops without complaint, so "
            "Jupiter's mass in kilograms comes out as 1. parseFloat "
            "understands the decimal point and the exponent. Number is "
            "stricter than both: the whole string has to be a number, so "
            "'1,898' with its comma is NaN rather than 1. Very large "
            "numbers print in exponent form, with a + sign."
        ),
    ),
    _p(
        id="predict-jspl-angle-wrap",
        level=2,
        name="Stepping an angle backwards",
        family=PLANETS,
        language="javascript",
        code=(
            "const normalize = (deg) => deg % 360;\n"
            "console.log(normalize(400), normalize(-30));\n"
            "const wrap = (deg) => ((deg % 360) + 360) % 360;\n"
            "console.log(wrap(400), wrap(-30), wrap(-720));"
        ),
        expect="40 -30\n40 330 0",
        why=(
            "`%` is a remainder, and its sign follows the number on the "
            "left, so -30 % 360 is -30, not 330. An orbit's angle stepped "
            "back past zero comes out negative instead of wrapping round "
            "the circle. Adding 360 and taking the remainder again lands "
            "any angle, however negative, in 0 to 359 - and -720, two "
            "whole turns back, lands on 0."
        ),
    ),
    _p(
        id="predict-jspl-numbered-keys",
        level=3,
        name="Planets numbered from the Sun",
        family=PLANETS,
        language="javascript",
        code=(
            "const fromSun = { 4: 'Mars', 1: 'Mercury', 3: 'Earth' };\n"
            "console.log(Object.values(fromSun).join(' '));\n"
            "const visited = new Map([[4, 'Mars'], [1, 'Mercury'], [3, 'Earth']]);\n"
            "console.log([...visited.values()].join(' '));"
        ),
        expect="Mercury Earth Mars\nMars Mercury Earth",
        why=(
            "A plain object does not keep keys that look like whole "
            "numbers in the order they were added. It lists them first, "
            "in ascending order, and only then any other keys in the "
            "order they arrived - so the planets come out sorted by "
            "their number, not as written. A Map keeps every key in the "
            "order it was set, numbers included, which is what a list of "
            "places visited needs."
        ),
    ),
    _p(
        id="predict-jspl-reduce-no-start",
        level=3,
        name="Adding up diameters",
        family=PLANETS,
        language="javascript",
        code=(
            "const planets = [{ name: 'Mars', km: 6792 }, { name: 'Venus', km: 12104 }];\n"
            "console.log(planets.reduce((sum, p) => sum + p.km));\n"
            "console.log(planets.reduce((sum, p) => sum + p.km, 0));"
        ),
        expect="[object Object]12104\n18896",
        why=(
            "Without a starting value, reduce uses the first element as "
            "the starting total and begins at the second. Here the first "
            "element is the whole Mars object, so the first sum is an "
            "object plus a number: the object becomes the text "
            "'[object Object]' and 12104 is glued on the end. Give reduce "
            "a starting 0 and the total starts as a number, and every "
            "planet's diameter is added."
        ),
    ),
    _p(
        id="predict-jspl-round-negative-half",
        level=3,
        name="Rounding a reading from Mars",
        family=PLANETS,
        language="javascript",
        code=(
            "const readingsC = [-62.5, -63.5, 2.5];\n"
            "console.log(readingsC.map((c) => Math.round(c)));\n"
            "console.log(readingsC.map((c) => c.toFixed(0)));"
        ),
        expect="[ -62, -63, 3 ]\n[ '-63', '-64', '3' ]",
        why=(
            "Math.round sends a half up, towards positive infinity, so "
            "-62.5 becomes -62, while 2.5 becomes 3 as expected. toFixed "
            "rounds a half away from zero instead, so -62.5 becomes "
            "'-63' - and it hands back strings, which is why the second "
            "array is in quotes. The two only disagree on negative "
            "halves, which is exactly why the difference gets past "
            "tests that use positive numbers."
        ),
    ),
    _p(
        id="predict-jspl-shallow-freeze",
        level=3,
        name="Freezing the list of planets",
        family=PLANETS,
        language="javascript",
        code=(
            "const planets = Object.freeze([{ name: 'Pluto', isPlanet: true }]);\n"
            "planets[0].isPlanet = false;\n"
            "try {\n"
            "  planets.push({ name: 'Eris' });\n"
            "} catch (e) {\n"
            "  console.log(e.name);\n"
            "}\n"
            "console.log(planets.length, planets[0].isPlanet);"
        ),
        expect="TypeError\n1 false",
        why=(
            "Object.freeze locks the array: it cannot grow, so push "
            "throws a TypeError. But the freeze is shallow. The object "
            "inside the array was never frozen, so its isPlanet field "
            "can still be changed - which is how Pluto, reclassified as "
            "a dwarf planet in 2006, loses its status in a list that "
            "was supposedly locked. To lock the objects too, freeze "
            "each of them as well."
        ),
    ),
)
