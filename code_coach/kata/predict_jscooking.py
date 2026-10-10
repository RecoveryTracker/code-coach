"""Predict the output, in JavaScript, for code about cooking and recipes.

Kitchen arithmetic is full of the numbers JavaScript is worst at: prices
that need exactly two decimals, quantities scaled by a fraction, halves
that have to round one way or the other, lists of amounts that arrive as
text, and shopping lists kept in a Map. A recipe card also formats times
and money, and each of those has an edge: a minute below ten needs a
zero, a number that has been through toFixed is a string, and a currency
formatter and toFixed do not always agree about a tie.

Every snippet runs in plain Node with no page and no network. Every
expected output was worked out by hand first and then checked against
what Node printed, and tests/test_predict_jsnode_music_cooking.py keeps
checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

COOKING = "Cooking"


JS_COOKING_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsck-tofixed-string",
        level=1,
        name="A price with two decimals",
        family=COOKING,
        language="javascript",
        code=(
            "const price = (4.5).toFixed(2);\n"
            "console.log(price, typeof price, price + 1, price * 2);\n"
            "console.log((1.005).toFixed(2), (2.5).toFixed(0), (1.45).toFixed(1));"
        ),
        expect="4.50 string 4.501 9\n1.00 3 1.4",
        why=(
            "toFixed is for showing a number, and what it hands back is "
            "a string. Adding 1 to the string '4.50' glues, giving "
            "'4.501', while multiplying converts it back to a number, "
            "so * 2 gives 9. The second line shows that toFixed rounds "
            "the number's exact stored value, not the decimal you "
            "typed: 1.005 is really a hair under 1.005, so it rounds "
            "down to '1.00', and 1.45 is a hair under 1.45, so it gives "
            "'1.4'. Only the exact tie 2.5 goes up. Keep prices in "
            "whole cents and format at the very end."
        ),
    ),
    _p(
        id="predict-jsck-round-half",
        level=1,
        name="Rounding a half",
        family=COOKING,
        language="javascript",
        code=(
            "const grams = [2.5, 3.5, -2.5, 0.5];\n"
            "console.log(grams.map(Math.round));\n"
            "console.log(Math.round(1.005 * 100) / 100, Math.round(1.5 * 100) / 100);"
        ),
        expect="[ 3, 4, -2, 1 ]\n1 1.5",
        why=(
            "Math.round sends an exact half upwards, towards positive "
            "infinity: 2.5 becomes 3, 3.5 becomes 4, but -2.5 becomes "
            "-2, not -3. The trick of multiplying by 100, rounding and "
            "dividing to get two decimals does not fix the problem "
            "with prices: 1.005 * 100 is really 100.49999999999999, "
            "which rounds down to 100, so the answer is 1 and not "
            "1.01, while 1.5 * 100 is exactly 150 and survives. "
            "The number you typed is not always the number stored."
        ),
    ),
    _p(
        id="predict-jsck-scaling-division",
        level=1,
        name="Eggs for six",
        family=COOKING,
        language="javascript",
        code=(
            "const eggs = 5;\n"
            "const perServing = eggs / 4;\n"
            "console.log(perServing, perServing * 6, eggs / 4 | 0);\n"
            "console.log(Math.floor(eggs / 4), Math.ceil(eggs / 4), eggs % 4);"
        ),
        expect="1.25 7.5 1\n1 2 1",
        why=(
            "JavaScript has no integer division: / always gives a "
            "fraction, so 5 eggs for 4 servings is 1.25 per person, "
            "and 7.5 eggs for six. If you want whole eggs you must "
            "choose how to round. `| 0` cuts off the fraction, as "
            "Math.trunc does, and so does Math.floor for positive "
            "numbers; Math.ceil rounds up, which is the right choice "
            "when buying eggs. The remainder, `%`, is 1: what is left "
            "when you hand out four at a time."
        ),
    ),
    _p(
        id="predict-jsck-sort-amounts",
        level=2,
        name="Sorting the amounts",
        family=COOKING,
        language="javascript",
        code=(
            "const amounts = ['250', '1000', '75', '30'];\n"
            "console.log(amounts.sort());\n"
            "console.log(amounts.sort((a, b) => a - b));\n"
            "console.log([250, 1000, 75, 30].sort());"
        ),
        expect=(
            "[ '1000', '250', '30', '75' ]\n"
            "[ '30', '75', '250', '1000' ]\n"
            "[ 1000, 250, 30, 75 ]"
        ),
        why=(
            "The default sort compares as text, even for numbers: "
            "'1000' is first because '1' comes before '2', '250' before "
            "'30' because '2' comes before '3', and so on. This is true "
            "for the plain numbers on the last line as well, which "
            "are turned into strings for the comparison and keep "
            "their type in the output. A compare function that "
            "subtracts forces a numeric comparison - the minus "
            "converts the strings to numbers - and the strings keep "
            "their quotes but sort in the right order."
        ),
    ),
    _p(
        id="predict-jsck-reduce-strings",
        level=2,
        name="Adding up prices that are text",
        family=COOKING,
        language="javascript",
        code=(
            "const prices = ['2.50', '3.00', '1.25'];\n"
            "console.log(prices.reduce((sum, p) => sum + p, 0));\n"
            "console.log(prices.reduce((sum, p) => sum + Number(p), 0));\n"
            "console.log(prices.reduce((sum, p) => sum + p));\n"
            "try { [].reduce((a, b) => a + b); } catch (e) { console.log(e.name); }"
        ),
        expect="02.503.001.25\n6.75\n2.503.001.25\nTypeError",
        why=(
            "`+` joins when either side is a string. With a starting "
            "value of 0, the first step is 0 + '2.50', which is the text "
            "'02.50', and every step after that just glues more text on "
            "- so the 'total' is a string of digits. Converting each "
            "price with Number first gives the real sum, 6.75. Without "
            "a starting value reduce starts from the first element "
            "itself, which gives the same kind of text without the "
            "leading 0. And with no starting value on an empty list, "
            "there is nothing to start from, so it throws."
        ),
    ),
    _p(
        id="predict-jsck-map-order",
        level=2,
        name="The shopping list's order",
        family=COOKING,
        language="javascript",
        code=(
            "const list = new Map();\n"
            "list.set('flour', 1);\n"
            "list.set('eggs', 6);\n"
            "list.set('milk', 2);\n"
            "list.set('flour', 3);\n"
            "list.delete('eggs');\n"
            "list.set('eggs', 12);\n"
            "console.log([...list.keys()].join(' '), list.size);\n"
            "console.log([...list.values()]);"
        ),
        expect="flour milk eggs 3\n[ 3, 2, 12 ]",
        why=(
            "A Map keeps its keys in the order they were first added. "
            "Setting a key that is already there changes its value but "
            "not its place, so flour stays first and becomes 3. "
            "Deleting a key and adding it again puts it at the end, as "
            "if it were new, so eggs moves behind milk. The size is "
            "three: flour, milk, eggs. This is why a Map is a good "
            "shopping list - but a list that must be sorted still "
            "has to be sorted."
        ),
    ),
    _p(
        id="predict-jsck-padstart-clock",
        level=2,
        name="Dinner at seven",
        family=COOKING,
        language="javascript",
        code=(
            "const h = 7;\n"
            "const m = 5;\n"
            "console.log(`${h}:${m}`);\n"
            "console.log(`${h}:${String(m).padStart(2, '0')}`);\n"
            "console.log(m.toString().padStart(3, 'ab'), `${m}`.padStart(1, '0'), '12345'.padStart(3, '0'));\n"
            "console.log(h + ':' + m + 5, h + m + ':00');"
        ),
        expect="7:5\n7:05\nab5 5 12345\n7:55 12:00",
        why=(
            "A number has no padStart: it belongs to strings, so the "
            "minute has to become one first. String(m).padStart(2, "
            "'0') adds as many leading zeros as are needed to reach a "
            "width of 2 - and only that: it never shortens a longer "
            "string, so '12345' stays as it is, and the fill text "
            "repeats and is cut to fit, giving 'ab5'. The last line "
            "is about + again. Left to right, h + ':' makes text, so "
            "5 is glued on, then another 5: '7:55'. But h + m comes "
            "first when both are numbers, and 7 + 5 is 12."
        ),
    ),
    _p(
        id="predict-jsck-currency-vs-tofixed",
        level=3,
        name="Two ways to show a price",
        family=COOKING,
        language="javascript",
        code=(
            "const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });\n"
            "console.log(usd.format(4.5), usd.format(1234.567), usd.format(-3));\n"
            "console.log(usd.format('2.5'), usd.format('abc'));\n"
            "console.log((1.005).toFixed(2), usd.format(1.005));"
        ),
        expect=(
            "$4.50 $1,234.57 -$3.00\n"
            "$2.50 $NaN\n"
            "1.00 $1.01"
        ),
        why=(
            "Intl.NumberFormat is the right tool for money: it adds the "
            "symbol, the thousands separators, the right number of "
            "decimals, and places the minus sign before the dollar "
            "sign. It also accepts a numeric string and turns it into "
            "a number first, while text that is no number comes out "
            "as '$NaN' rather than an error. The last line is a "
            "surprise: the formatter rounds the number as written, in "
            "decimal, so 1.005 becomes $1.01, while toFixed rounds "
            "the exact stored value, which is just under, and gives "
            "'1.00'. The two are not interchangeable."
        ),
    ),
    _p(
        id="predict-jsck-sort-case",
        level=3,
        name="Alphabetical, or nearly",
        family=COOKING,
        language="javascript",
        code=(
            "const items = ['eggs', 'Flour', 'apples', 'Butter'];\n"
            "console.log([...items].sort());\n"
            "console.log([...items].sort((a, b) => a.localeCompare(b)));\n"
            "const sorted = items.sort();\n"
            "console.log(sorted === items, items[0]);"
        ),
        expect=(
            "[ 'Butter', 'Flour', 'apples', 'eggs' ]\n"
            "[ 'apples', 'Butter', 'eggs', 'Flour' ]\n"
            "true Butter"
        ),
        why=(
            "The default sort orders by character code, and every "
            "capital letter has a smaller code than every lowercase "
            "one, so 'Butter' and 'Flour' come before 'apples' and "
            "'eggs'. localeCompare knows alphabets: it ignores the case "
            "when it can and gives the order a person expects. The "
            "copies made with [...items] left the array alone; the "
            "last sort did not, and it returns the same array, not "
            "a new one, so `sorted === items` is true and the "
            "original now begins 'Butter'."
        ),
    ),
    _p(
        id="predict-jsck-shallow-copy",
        level=3,
        name="A copy of the recipe",
        family=COOKING,
        language="javascript",
        code=(
            "const recipe = { name: 'bread', items: ['flour', 'water'] };\n"
            "const copy = { ...recipe };\n"
            "copy.name = 'rolls';\n"
            "copy.items.push('salt');\n"
            "console.log(recipe.name, recipe.items.length);\n"
            "const deep = structuredClone(recipe);\n"
            "deep.items.push('yeast');\n"
            "console.log(recipe.items.length, deep.items.length);"
        ),
        expect="bread 3\n3 4",
        why=(
            "The spread copies the top level only. The name is a plain "
            "value, so the copy has its own and renaming it leaves the "
            "original as 'bread'. But items is an array, and what is "
            "copied is the reference to it, so both recipes share one "
            "list, and pushing 'salt' through the copy changes the "
            "original. structuredClone makes a deep copy: the "
            "ingredients of `deep` are separate, so adding yeast "
            "changes nothing else."
        ),
    ),
)
