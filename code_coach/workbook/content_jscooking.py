"""Pages 258-267: JavaScript, cooking and recipes.

Kitchen arithmetic, with the recipe as the flavour and the JavaScript as the
lesson. The first eight pages are sums, each a step harder than the one
before: scaling a recipe to more or fewer servings, converting cups and
spoons and ounces, oven temperatures and gas marks, a roasting time as hours
and minutes, an array of recipes to filter and join, shopping lists merged
with reduce, the cost of a serving, and nutrition worked out from the
macros. The last two count a timeline backwards from the time dinner is
served, with padStart and a wrap past midnight, and print a recipe card that
lines up.

Every prompt states the numbers it needs, the conversion factors, the gas
mark table and the daily values included, so nobody has to look anything up.
The recipes and ingredients are kept in the tables below so that every page
agrees with every other.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.emit_jscooking import (
    CUP_ML,
    DAILY_KCAL,
    GAS,
    KCAL_FAT,
    KCAL_PROTEIN,
    OZ_G,
    TBSP_ML,
    TSP_ML,
)

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


# ── The recipes and ingredients ──────────────────────────────

#: A recipe: minutes to cook, vegetarian or not, people it serves.
RECIPES = {
    "Pancakes": (20, True, 4),
    "Beef stew": (150, False, 6),
    "Omelette": (10, True, 1),
    "Lasagne": (90, False, 8),
    "Veg curry": (35, True, 4),
    "Roast chicken": (105, False, 5),
    "Pasta bake": (45, True, 6),
    "Fish pie": (60, False, 4),
    "Tomato soup": (30, True, 4),
    "Chilli": (70, False, 6),
    "Salad": (15, True, 2),
    "Risotto": (40, True, 3),
}

#: What a prompt calls each recipe field, and which slot of RECIPES it is.
RECIPE_FIELDS = {
    "minutes": (0, "its cooking time in minutes", "cooking time"),
    "veg": (1, "whether it is vegetarian, true or false,", "vegetarian"),
    "serves": (2, "how many people it serves", "servings"),
}

#: An ingredient on a recipe card: grams, price in dollars, kcal.
INGREDIENTS = {
    "Flour": (250, 0.4, 910),
    "Butter": (125, 1.1, 896),
    "Sugar": (100, 0.55, 387),
    "Eggs": (180, 1.8, 258),
    "Milk": (300, 0.45, 150),
    "Cheese": (200, 3.25, 800),
    "Rice": (150, 0.3, 520),
    "Onion": (120, 0.2, 48),
    "Tomato": (400, 1.5, 72),
    "Oil": (60, 0.25, 530),
}

#: A field of the card: its slot of INGREDIENTS, how a prompt describes it,
#: and what one value of it is called.
CARD_FIELDS = {
    "grams": (0, "its weight in grams", "weight"),
    "price": (1, "its price in dollars", "price"),
    "kcal": (2, "its energy in kcal", "calories"),
}


# ── Saying things ────────────────────────────────────────────


def _say(x) -> str:
    """A value as a prompt writes it: 0.25, 250, 3, true."""
    if isinstance(x, bool):
        return "true" if x else "false"
    return repr(x) if isinstance(x, float) else str(x)


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _places(digits: int) -> str:
    return {0: "as a whole number", 1: "to one decimal place",
            2: "to two decimal places"}[digits]


def _money(x) -> str:
    return f"${x:.2f}"


# ── 258. Scaling a recipe ────────────────────────────────────

_SCALES = (
    ("amount", "flour", "g", 250, 4, 6),
    ("amount", "cream", "ml", 150, 4, 5),
    ("amount", "cheese", "g", 100, 3, 5),
    ("amount", "lentils", "g", 200, 6, 4),
    ("amount", "vanilla", "ml", 5, 8, 3),
    ("amount", "oats", "g", 90, 4, 7),
    ("factor", "rice", "g", 200, 4, 6),
    ("factor", "butter", "g", 60, 6, 4),
    ("factor", "milk", "ml", 250, 4, 10),
    ("factor", "sugar", "g", 80, 5, 2),
    ("factor", "stock", "ml", 500, 3, 8),
    ("two", (("flour", "g", 250), ("milk", "ml", 300)), 4, 10),
    ("two", (("rice", "g", 300), ("stock", "ml", 750)), 6, 9),
    ("two", (("pasta", "g", 320), ("tomatoes", "g", 400)), 4, 6),
    ("two", (("oats", "g", 100), ("milk", "ml", 250)), 3, 5),
    ("two", (("flour", "g", 500), ("milk", "ml", 300)), 8, 3),
    ("whole", "eggs", 3, 4, 10),
    ("whole", "eggs", 2, 4, 9),
    ("whole", "onions", 1, 4, 10),
    ("whole", "lemons", 1, 6, 4),
)


def _scale_row(row):
    want = row[0]
    if want == "two":
        _, ((t1, u1, q1), (t2, u2, q2)), orig, wanted = row
        return (f"A recipe for {orig} people uses {q1} {u1} of {t1} and {q2} "
                f"{u2} of {t2}. Print how much of each {wanted} people need, "
                f"{t1} first, to one decimal place each.",
                {"want": want, "orig": orig, "wanted": wanted,
                 "items": ((t1, q1), (t2, q2))})
    if want == "whole":
        _, thing, qty, orig, wanted = row
        return (f"A recipe for {orig} people uses {qty} {thing}. You cannot "
                f"buy part of one, so round up: print how many {thing} "
                f"{wanted} people need.",
                {"want": want, "thing": thing, "qty": qty, "orig": orig,
                 "wanted": wanted})
    _, thing, unit, qty, orig, wanted = row
    args = {"want": want, "thing": thing, "qty": qty, "orig": orig,
            "wanted": wanted}
    start = f"A recipe for {orig} people uses {qty} {unit} of {thing}."
    if want == "amount":
        return (f"{start} Print how many {unit} of {thing} {wanted} people "
                f"need, to one decimal place.", args)
    return (f"{start} The scale factor for {wanted} people is {wanted} divided "
            f"by {orig}: print that factor to two decimal places, then the "
            f"amount of {thing} needed for {wanted} people, to one decimal "
            f"place.", args)


SCALE_PAGE = _page(
    "js-cook-scale", 258, "Cooking: scaling a recipe",
    "A recipe is written for a number of servings, and cooking for more or "
    "fewer people means scaling every amount by the same fraction: the "
    "servings you want over the servings it was written for. Multiply the "
    "ingredient by wanted, then divide by original, and the amount comes "
    "out in proportion whichever way you are going; that fraction, "
    "wanted / original, is the scale factor, which is above 1 when you "
    "cook for more and below 1 when you cook for fewer. Divisions such as "
    "250 * 7 / 4 do not always come out even, so toFixed(1) rounds the "
    "result to one decimal place for printing and hands back a string. "
    "Some things cannot be split, like an egg. Math.ceil rounds up to the "
    "next whole number, which is the safe way to buy: 7.5 eggs means 8.",
    "250 g of flour for 4 people, scaled to 6: 250 * 6 / 4 is 375, so "
    "(250 * 6 / 4).toFixed(1) prints 375.0; the factor 6 / 4 is 1.5; and "
    "Math.ceil(3 * 10 / 4) is 8, the eggs for 10 people when 4 need 3",
    "js_cook_scale",
    tuple(_scale_row(row) for row in _SCALES),
)


# ── 259. Unit conversions ────────────────────────────────────

_FACT = {
    "cup": f"1 cup is {CUP_ML} ml",
    "tbsp": f"1 tbsp (a tablespoon) is {TBSP_ML} ml",
    "tsp": f"1 tsp (a teaspoon) is {TSP_ML} ml",
}
_WORD = {"cup": "cups", "tbsp": "tablespoons", "tsp": "teaspoons"}

_UNITS = (
    ("to_ml", "cup", 2.5),
    ("to_ml", "cup", 0.75),
    ("to_ml", "tbsp", 4),
    ("to_ml", "tbsp", 2.5),
    ("to_ml", "tsp", 1.5),
    ("from_ml", "cup", 350, 2),
    ("from_ml", "cup", 500, 2),
    ("from_ml", "tbsp", 100, 1),
    ("from_ml", "tbsp", 40, 1),
    ("from_ml", "tsp", 22, 1),
    ("oz_g", "butter", 8),
    ("oz_g", "cheese", 2.5),
    ("oz_g", "chocolate", 12),
    ("oz_g", "flour", 6),
    ("g_oz", "butter", 250),
    ("g_oz", "pasta", 500),
    ("g_oz", "sugar", 100),
    ("g_oz", "cheese", 75),
    ("cup_tbsp", "milk", 1.5),
    ("cup_tbsp", "flour", 0.25),
)


def _units_row(row):
    want = row[0]
    if want == "to_ml":
        _, unit, qty = row
        return (f"{_FACT[unit].capitalize()}. A recipe needs {qty} {_WORD[unit]}: "
                f"print how many millilitres that is.",
                {"want": want, "unit": unit, "qty": qty})
    if want == "from_ml":
        _, unit, ml, digits = row
        return (f"{_FACT[unit].capitalize()}. A bottle holds {ml} ml: print how "
                f"many {_WORD[unit]} that is, {_places(digits)}.",
                {"want": want, "unit": unit, "qty": ml, "digits": digits})
    if want == "oz_g":
        _, thing, oz = row
        return (f"1 oz is {OZ_G} g. A recipe needs {oz} oz of {thing}: print how "
                f"many grams that is, to one decimal place.",
                {"want": want, "thing": thing, "qty": oz})
    if want == "g_oz":
        _, thing, grams = row
        return (f"1 oz is {OZ_G} g. A recipe needs {grams} g of {thing}: print "
                f"how many ounces that is, to two decimal places.",
                {"want": want, "thing": thing, "qty": grams})
    _, thing, cups = row
    return (f"1 cup is {CUP_ML} ml and 1 tbsp is {TBSP_ML} ml. A recipe needs "
            f"{cups} cups of {thing}: print how many tablespoons that is.",
            {"want": want, "thing": thing, "qty": cups})


UNITS_PAGE = _page(
    "js-cook-units", 259, "Cooking: unit conversions",
    "Recipes mix cups, spoons, millilitres, ounces and grams, and changing "
    "one for another is a single multiply or divide by a fixed number. To "
    "know which, ask whether the answer should come out bigger or smaller: "
    "a cup is a lot of millilitres, so cups to millilitres multiplies by "
    "240, and millilitres to cups divides by it. Put the factor in a "
    "variable with a name that says what it is, such as mlPerCup, so the "
    "line reads like the sum. To go through a middle unit, convert to it "
    "first and out again: cups * mlPerCup gives millilitres, and dividing "
    "that by mlPerTbsp gives tablespoons. When the answer is not a whole "
    "number, toFixed(2) rounds it to two decimal places for printing.",
    "with const mlPerCup = 240, 2.5 cups is 2.5 * mlPerCup, 600 ml; 350 ml "
    "is 350 / mlPerCup, about 1.458 cups, and (350 / mlPerCup).toFixed(2) "
    "prints 1.46",
    "js_cook_units",
    tuple(_units_row(row) for row in _UNITS),
)


# ── 260. Oven temperatures ───────────────────────────────────

_GAS_TEXT = ("Gas marks 1 to 9 are " + ", ".join(str(v) for v in GAS.values())
             + " °C, in that order.")

_TEMPS = (
    ("c2f", "The oven is set to", 180),
    ("c2f", "The fridge should be at", 4),
    ("c2f", "Chicken is safe to eat once its middle reaches", 74),
    ("c2f", "The freezer is kept at", -18),
    ("c2f", "Caramel is made at", 170),
    ("f2c", "A recipe says to bake at", 350),
    ("f2c", "A bread recipe says to bake at", 400),
    ("f2c", "A cake recipe says to bake at", 325),
    ("f2c", "A freezer is kept at", 0),
    ("round", "A recipe says to bake at", 350),
    ("round", "A pizza recipe says to bake at", 425),
    ("round", "A slow roast recipe says to cook at", 300),
    ("gas2c", 6),
    ("gas2c", 3),
    ("gas2c", 8),
    ("gas2f", 4),
    ("gas2f", 9),
    ("c2gas", 180),
    ("c2gas", 200),
    ("c2gas", 230),
)


def _temp_row(row):
    want = row[0]
    if want == "c2f":
        _, what, c = row
        return (f"{what} {c} °C. Fahrenheit is Celsius times 9, divided by 5, "
                f"plus 32: print it in °F to one decimal place.",
                {"want": want, "c": c})
    if want == "f2c":
        _, what, f = row
        return (f"{what} {f} °F. Celsius is Fahrenheit minus 32, times 5, "
                f"divided by 9: print it in °C to one decimal place.",
                {"want": want, "f": f})
    if want == "round":
        _, what, f = row
        return (f"{what} {f} °F. Celsius is Fahrenheit minus 32, times 5, "
                f"divided by 9: print it in °C, rounded to the nearest whole "
                f"degree.",
                {"want": want, "f": f})
    if want == "gas2c":
        return (f"{_GAS_TEXT} A recipe says to bake at gas mark {row[1]}: print "
                f"the temperature in °C.",
                {"want": want, "mark": row[1]})
    if want == "gas2f":
        return (f"{_GAS_TEXT} A recipe says to bake at gas mark {row[1]}. "
                f"Fahrenheit is Celsius times 9, divided by 5, plus 32: print "
                f"the temperature in °F to one decimal place.",
                {"want": want, "mark": row[1]})
    return (f"{_GAS_TEXT} A recipe says to bake at {row[1]} °C: print which gas "
            f"mark that is.",
            {"want": want, "c": row[1]})


TEMP_PAGE = _page(
    "js-cook-temp", 260, "Cooking: oven temperatures",
    "Ovens are marked in Celsius, Fahrenheit or gas marks depending on the "
    "country and the age of the cooker. The two degree scales start from "
    "different places, so Celsius to Fahrenheit needs a multiply and an "
    "add: Celsius times 9, divided by 5, plus 32. Going back undoes it in "
    "reverse order: take the 32 off first, then times 5 and divide by 9. "
    "Math.round gives the nearest whole degree, and toFixed(1) keeps one "
    "decimal place, including the minus sign when a result drops below "
    "zero. Gas marks are not a formula at all, only a table, and a table "
    "is an object: { 4: 180 } maps the key 4 to 180, and marks[4] looks it "
    "up. The other way round, Object.keys(marks) lists the keys and find "
    "returns the first key whose value matches. Keys come back as text, "
    "which prints the same.",
    "350 °F is (350 - 32) * 5 / 9, about 176.7 °C, and Math.round of that "
    "is 177; with const marks = { 4: 180, 5: 190 }, marks[4] is 180, and "
    "Object.keys(marks).find((key) => marks[key] === 190) is \"5\"",
    "js_cook_temp",
    tuple(_temp_row(row) for row in _TEMPS),
)


# ── 261. Cooking time from the weight ────────────────────────

_TIMES = (
    ("min", "chicken", 20, 45, 2.3),
    ("min", "turkey", 30, 35, 5.5),
    ("min", "beef", 25, 50, 1.75),
    ("min", "pork", 35, 45, 2.1),
    ("hm", "turkey", 30, 35, 4.3),
    ("hm", "chicken", 20, 45, 2.3),
    ("hm", "beef", 25, 50, 1.75),
    ("hm", "pork", 35, 45, 2.1),
    ("hm", "ham", 40, 32, 3.7),
    ("hm", "goose", 30, 42, 4.6),
    ("rest", "chicken", 20, 45, 2.3, 15),
    ("rest", "turkey", 30, 35, 4.3, 30),
    ("rest", "beef", 25, 50, 1.75, 20),
    ("rest", "lamb", 25, 55, 1.9, 10),
    ("rest", "ham", 40, 32, 3.7, 45),
    ("longer", ("chicken", 20, 45, 2.3), ("lamb", 25, 55, 1.9)),
    ("longer", ("turkey", 30, 35, 4.3), ("chicken", 20, 45, 2.3)),
    ("longer", ("beef", 25, 50, 1.75), ("pork", 35, 45, 2.1)),
    ("longer", ("ham", 40, 32, 3.7), ("beef", 25, 50, 1.75)),
    ("longer", ("goose", 30, 42, 4.6), ("pork", 35, 45, 2.1)),
)


def _roasts(thing, base, per, kg) -> str:
    return (f"A {thing} needs {base} minutes in the oven plus {per} minutes "
            f"for every kg, and this one weighs {kg} kg.")


def _time_row(row):
    want = row[0]
    if want == "longer":
        (t1, b1, p1, k1), (t2, b2, p2, k2) = row[1], row[2]
        return (f"A {t1} needs {b1} minutes in the oven plus {p1} minutes for "
                f"every kg and weighs {k1} kg; a {t2} needs {b2} minutes plus "
                f"{p2} for every kg and weighs {k2} kg. For each, print the "
                f"minutes, dropping any fraction, the {t1} first, then "
                f"whether the {t1} takes longer.",
                {"want": want, "one": row[1], "two": row[2]})
    _, thing, base, per, kg, *more = row
    args = {"want": want, "base": base, "per": per, "kg": kg}
    start = _roasts(thing, base, per, kg)
    if want == "min":
        return (f"{start} Print the total minutes it needs, dropping any "
                f"fraction of a minute.", args)
    if want == "hm":
        return (f"{start} Drop any fraction of a minute and print the total "
                f"time in the form 1 h 25 min.", args)
    args["rest"] = more[0]
    return (f"{start} After it comes out it rests for {more[0]} minutes. Drop "
            f"any fraction of a minute from the cooking and print the time "
            f"from putting it in to carving it, in the form 1 h 25 min.", args)


TIME_PAGE = _page(
    "js-cook-time", 261, "Cooking: time from the weight",
    "Roasting times are usually given as a fixed amount plus so many "
    "minutes for every kilogram, so the total is base + perKg * kg. Ovens "
    "are not that exact and a stray fraction of a minute means nothing, so "
    "Math.floor drops it. A hundred and twenty-three minutes reads better "
    "as hours and minutes. Math.floor(total / 60) is how many whole hours "
    "fit in it, and total % 60 is the remainder: the minutes left over once "
    "every full hour has been taken out. A template literal puts them "
    "together, and a remainder of zero still prints, as 0 min. To add a "
    "resting time, add it to the whole minutes before splitting, not to "
    "the hours and the minutes after.",
    "20 + 45 * 2.3 is 123.5, so with total = Math.floor(20 + 45 * 2.3), "
    "which is 123, Math.floor(total / 60) is 2 and total % 60 is 3, and "
    "`${Math.floor(total / 60)} h ${total % 60} min` prints 2 h 3 min",
    "js_cook_time",
    tuple(_time_row(row) for row in _TIMES),
)


# ── 262. Filter, map and join ────────────────────────────────

_FILTERS = (
    ("names", "minutes", ">", 60, ("Pancakes", "Beef stew", "Omelette", "Lasagne", "Chilli")),
    ("names", "minutes", "<", 30, ("Pancakes", "Lasagne", "Omelette", "Chilli", "Salad")),
    ("names", "veg", "is", None, ("Pancakes", "Beef stew", "Veg curry", "Fish pie", "Risotto")),
    ("names", "veg", "not", None, ("Omelette", "Lasagne", "Roast chicken", "Pasta bake", "Chilli")),
    ("names", "serves", ">", 4, ("Omelette", "Lasagne", "Salad", "Pasta bake", "Chilli", "Risotto")),
    ("names", "serves", "<", 4, ("Omelette", "Beef stew", "Risotto", "Salad", "Roast chicken")),
    ("names", "minutes", "<", 50, ("Veg curry", "Fish pie", "Pasta bake", "Tomato soup", "Risotto")),
    ("names", "minutes", ">", 100, ("Beef stew", "Roast chicken", "Omelette", "Salad", "Fish pie")),
    ("count", "minutes", ">", 40, ("Pancakes", "Lasagne", "Veg curry", "Roast chicken", "Pasta bake")),
    ("count", "veg", "is", None, ("Pancakes", "Beef stew", "Omelette", "Fish pie", "Salad")),
    ("count", "serves", ">", 5, ("Beef stew", "Lasagne", "Salad", "Chilli", "Pancakes")),
    ("count", "veg", "not", None, ("Lasagne", "Veg curry", "Roast chicken", "Chilli", "Risotto")),
    ("label", "minutes", "<", 40, ("Pancakes", "Beef stew", "Omelette", "Lasagne", "Veg curry", "Salad")),
    ("label", "serves", ">", 4, ("Omelette", "Lasagne", "Pasta bake", "Salad", "Chilli")),
    ("label", "minutes", ">", 50, ("Pancakes", "Beef stew", "Fish pie", "Omelette", "Chilli")),
    ("label", "serves", "<", 3, ("Omelette", "Lasagne", "Salad", "Pancakes")),
    ("some", "minutes", ">", 140, ("Pancakes", "Omelette", "Beef stew")),
    ("some", "serves", ">", 10, ("Pancakes", "Lasagne", "Chilli")),
    ("every", "veg", "is", None, ("Pancakes", "Omelette", "Veg curry", "Salad")),
    ("every", "minutes", "<", 60, ("Pancakes", "Omelette", "Lasagne")),
)

#: How a label is written, shown with a recipe that is never in the data.
_LABEL_LIKE = {"minutes": "Bread 75 min", "serves": "Bread for 8"}

#: What a test keeps, as the plural verb ("recipes that ...") and the
#: singular ("any recipe in the array ...").
_PLURAL = {
    ("minutes", ">"): "that take longer than {x} minutes",
    ("minutes", "<"): "that take less than {x} minutes",
    ("serves", ">"): "that serve more than {x} people",
    ("serves", "<"): "that serve fewer than {x} people",
    ("veg", "is"): "that are vegetarian",
    ("veg", "not"): "that are not vegetarian",
}
_SINGULAR = {
    ("minutes", ">"): "takes longer than {x} minutes",
    ("minutes", "<"): "takes less than {x} minutes",
    ("serves", ">"): "serves more than {x} people",
    ("serves", "<"): "serves fewer than {x} people",
    ("veg", "is"): "is vegetarian",
    ("veg", "not"): "is not vegetarian",
}


def _array(field: str, names) -> tuple[str, tuple]:
    """The prompt's description of a one-field array, and the items."""
    slot, describe, _ = RECIPE_FIELDS[field]
    items = tuple((n, RECIPES[n][slot]) for n in names)
    listing = _and(f"{n} {_say(v)}" for n, v in items)
    return (f"Make an array of recipe objects, each with a name and "
            f"{describe} as {field}: {listing}.", items)


def _filter_row(row):
    want, field, op, limit, names = row
    make, items = _array(field, names)
    args = {"want": want, "field": field, "op": op, "limit": limit,
            "items": items}
    x = _say(limit)
    if want == "names":
        which = _PLURAL[(field, op)].format(x=x)
        ask = (f"Print the names of the recipes {which}, in the same order, "
               f"joined by a comma and a space.")
    elif want == "count":
        ask = f"Print how many recipes {_PLURAL[(field, op)].format(x=x)}."
    elif want == "label":
        which = _PLURAL[(field, op)].format(x=x)
        ask = (f"Take the recipes {which} and print them on one line, each "
               f"written like {_LABEL_LIKE[field]}, joined by a comma and a "
               f"space.")
    else:
        whom = "any recipe" if want == "some" else "every recipe"
        ask = (f"Print whether {whom} in the array "
               f"{_SINGULAR[(field, op)].format(x=x)}.")
    return f"{make} {ask}", args


FILTER_PAGE = _page(
    "js-cook-filter", 262, "Cooking: filter, map and join",
    "Give each recipe an object, { name: \"Pancakes\", minutes: 20 }, and a "
    "cookbook becomes one array you can ask questions of. "
    "filter((r) => r.minutes < 30) goes through the array and keeps the "
    "recipes the arrow function says true for, in their original order, "
    "leaving the array itself alone. For a yes-or-no field such as veg the "
    "test is just r.veg, or !r.veg for the ones that are not. map((r) => "
    "r.name) turns each recipe into something else: here its name, or a "
    "label built with a template literal. join(\", \") glues the results "
    "into one string with a comma and a space between them. Chained, the "
    "three read like the question: which recipes, what about them, and how "
    "to print it. For a count, take the filtered array's length. some and "
    "every answer yes or no directly: some is true as soon as one recipe "
    "passes, every only when all of them do.",
    "recipes.filter((r) => r.veg).map((r) => r.name).join(\", \") gives the "
    "names of the vegetarian recipes, in order, with a comma and a space "
    "between; recipes.some((r) => r.minutes > 100) is true as soon as one "
    "recipe takes longer than 100 minutes",
    "js_cook_filter",
    tuple(_filter_row(row) for row in _FILTERS),
)


# ── 263. Merging shopping lists ──────────────────────────────

_SHOPS = (
    ("sorted", (("eggs", 2), ("flour", 1), ("milk", 2), ("eggs", 1),
                ("butter", 1), ("flour", 2))),
    ("sorted", (("onions", 3), ("rice", 1), ("tomatoes", 4), ("onions", 2),
                ("garlic", 1), ("tomatoes", 2), ("rice", 2))),
    ("sorted", (("pasta", 2), ("cheese", 1), ("cream", 1), ("pasta", 1),
                ("basil", 1), ("cheese", 2))),
    ("sorted", (("lemons", 4), ("sugar", 1), ("butter", 2), ("lemons", 3),
                ("flour", 1), ("sugar", 2), ("eggs", 6))),
    ("sorted", (("carrots", 3), ("potatoes", 5), ("onions", 2), ("carrots", 4),
                ("potatoes", 3), ("stock", 2))),
    ("oneline", (("milk", 1), ("eggs", 3), ("milk", 2), ("butter", 1),
                 ("eggs", 2))),
    ("oneline", (("rice", 2), ("beans", 1), ("onions", 3), ("beans", 2),
                 ("rice", 1), ("garlic", 1))),
    ("oneline", (("apples", 6), ("sugar", 1), ("flour", 2), ("apples", 4),
                 ("butter", 1), ("flour", 1))),
    ("oneline", (("peppers", 2), ("pasta", 1), ("tomatoes", 3), ("peppers", 1),
                 ("cheese", 1), ("tomatoes", 2))),
    ("count", (("eggs", 2), ("flour", 1), ("eggs", 3), ("milk", 1),
               ("flour", 1))),
    ("count", (("onions", 2), ("carrots", 3), ("celery", 1), ("onions", 1),
               ("carrots", 2), ("stock", 2), ("celery", 2))),
    ("count", (("lemons", 3), ("sugar", 2), ("lemons", 1), ("honey", 1),
               ("ginger", 1), ("honey", 1))),
    ("most", (("eggs", 2), ("flour", 3), ("milk", 1), ("eggs", 4),
              ("sugar", 1))),
    ("most", (("rice", 1), ("beans", 2), ("rice", 4), ("onions", 3),
              ("beans", 1), ("garlic", 1))),
    ("most", (("pasta", 2), ("cheese", 3), ("cream", 1), ("pasta", 2),
              ("basil", 1), ("cream", 1))),
    ("most", (("butter", 1), ("apples", 5), ("flour", 2), ("apples", 2),
              ("butter", 2), ("sugar", 3))),
    ("map", (("tea", 1), ("milk", 2), ("sugar", 1), ("tea", 2), ("milk", 1))),
    ("map", (("peas", 2), ("rice", 1), ("peas", 3), ("fish", 2), ("lemons", 1),
             ("rice", 1))),
    ("map", (("bread", 2), ("ham", 1), ("cheese", 2), ("bread", 1), ("ham", 2),
             ("pickles", 1))),
    ("map", (("oats", 1), ("honey", 1), ("milk", 3), ("oats", 2), ("bananas", 4),
             ("milk", 1))),
)

_SHOP_ASK = {
    "sorted": ("with an object built by reduce, add up the packs for each item "
               "and print one line per item in alphabetical order, written "
               "like eggs: 3."),
    "oneline": ("with an object built by reduce, add up the packs for each item "
                "and print them on one line in alphabetical order, each "
                "written like eggs 3, joined by a comma and a space."),
    "count": ("with an object built by reduce, add up the packs for each item. "
              "Print how many different items there are, then how many packs "
              "there are in all."),
    "most": ("with an object built by reduce, add up the packs for each item. "
             "Print the item with the most packs in all, then a space and its "
             "total."),
    "map": ("with a Map, add up the packs for each item and print one line per "
            "item in alphabetical order, written like eggs: 3."),
}


def _shop_row(row):
    want, pairs = row
    listing = _and(f"{i} {q}" for i, q in pairs)
    return (f"A shopping list has these lines, each an item and a number of "
            f"packs, some items on it more than once: {listing}. Now, "
            f"{_SHOP_ASK[want]}",
            {"want": want, "lines": pairs})


SHOP_PAGE = _page(
    "js-cook-shop", 263, "Cooking: merging shopping lists",
    "Two recipes both want eggs, and the shopping list should say eggs once, "
    "with the amounts added. That is a job for reduce, carrying one object "
    "along: for each line, look the item up, start from 0 when it is not "
    "there yet, and add: sum[item] = (sum[item] || 0) + qty. The || 0 does "
    "the starting: a missing key gives undefined, which is falsy, so 0 "
    "takes its place. A Map does the same with set and get, and keeps "
    "its keys in the order they first arrived. Neither is in alphabetical "
    "order, so Object.keys(totals).sort() puts the names in order before "
    "printing; sort on plain text goes by letters, which is what a shopping "
    "list wants. Object.values lists the amounts, Object.keys the names, and "
    "Object.entries gives pairs, which sort can compare by the second "
    "element, b[1] - a[1], biggest first.",
    "reducing [[\"eggs\", 2], [\"milk\", 1], [\"eggs\", 3]] into an object "
    "gives { eggs: 5, milk: 1 }, and looping over Object.keys(totals).sort() "
    "prints eggs: 5 then milk: 1",
    "js_cook_shop",
    tuple(_shop_row(row) for row in _SHOPS),
)


# ── 264. Cost per serving and per portion ────────────────────

FLOUR = ("flour", 0.25, 1.6, "kg")
EGGS = ("eggs", 3, 0.35, "each")
MILK = ("milk", 0.5, 0.9, "litre")
BUTTER = ("butter", 0.2, 8, "kg")
SUGAR = ("sugar", 0.1, 1.5, "kg")
RICE = ("rice", 0.3, 2.2, "kg")
ONIONS = ("onions", 2, 0.4, "each")
TOMATOES = ("tomatoes", 0.5, 3.2, "kg")
CHEESE = ("cheese", 0.15, 9, "kg")
CREAM = ("cream", 0.25, 3.6, "litre")
OIL = ("oil", 0.05, 6, "litre")
CHICKEN = ("chicken", 1.2, 7.5, "kg")
BEANS = ("beans", 0.4, 2.5, "kg")
PASTA = ("pasta", 0.5, 1.8, "kg")

_COSTS = (
    ("serving", (FLOUR, EGGS, MILK), 6),
    ("serving", (RICE, ONIONS, TOMATOES), 5),
    ("serving", (BUTTER, SUGAR, FLOUR, EGGS), 8),
    ("serving", (PASTA, TOMATOES, CHEESE), 3),
    ("both", (CHICKEN, RICE, OIL), 5),
    ("both", (BEANS, ONIONS, TOMATOES, OIL), 6),
    ("both", (CREAM, BUTTER, SUGAR), 7),
    ("both", (CHEESE, PASTA, CREAM), 4),
    ("portion", (FLOUR, EGGS, MILK), 10, 4),
    ("portion", (CHICKEN, RICE, OIL), 6, 2),
    ("portion", (BUTTER, SUGAR, FLOUR, EGGS), 16, 4),
    ("portion", (BEANS, ONIONS, TOMATOES), 6, 2),
    ("afford", (RICE, ONIONS, TOMATOES), 4, 15),
    ("afford", (FLOUR, EGGS, MILK), 6, 10),
    ("afford", (PASTA, TOMATOES, CHEESE), 3, 12),
    ("afford", (CHICKEN, RICE, OIL), 5, 20),
    ("cheaper", ("soup", 9.6, 6), ("stew", 14.4, 8)),
    ("cheaper", ("curry", 18, 6), ("chilli", 14, 5)),
    ("cheaper", ("pie", 12.6, 6), ("bake", 9.2, 4)),
    ("cheaper", ("risotto", 7.5, 3), ("paella", 21, 6)),
)


def _buy(item) -> str:
    name, qty, price, unit = item
    cost = _money(price)
    if unit == "each":
        return f"{qty} {name} at {cost} each"
    if unit == "kg":
        return f"{qty} kg of {name} at {cost} a kg"
    word = "litre" if qty == 1 else "litres"
    return f"{qty} {word} of {name} at {cost} a litre"


def _cost_row(row):
    want = row[0]
    if want == "cheaper":
        (n1, t1, s1), (n2, t2, s2) = row[1], row[2]
        return (f"A pot of {n1} costs {_money(t1)} in all and makes {s1} "
                f"servings; a pot of {n2} costs {_money(t2)} and makes {s2}. "
                f"Print the cost of one serving of each to two decimal "
                f"places, the {n1} first, then whether the {n1} is the "
                f"cheaper serving.",
                {"want": want, "one": row[1], "two": row[2]})
    items, servings = row[1], row[2]
    args = {"want": want, "servings": servings,
            "items": tuple((n, q, p) for n, q, p, _ in items)}
    start = (f"A recipe uses {_and(_buy(i) for i in items)}, and makes "
             f"{servings} servings.")
    if want == "serving":
        return (f"{start} Print the cost of one serving, to two decimal "
                f"places.", args)
    if want == "both":
        return (f"{start} Print the cost of the whole recipe, then the cost of "
                f"one serving, each to two decimal places.", args)
    if want == "portion":
        args["per"] = row[3]
        return (f"{start} A portion is {row[3]} servings. Print the cost of one "
                f"serving, then the cost of one portion, each to two decimal "
                f"places.", args)
    args["budget"] = row[3]
    return (f"{start} You have {_money(row[3])} to spend on servings. Print how "
            f"many whole servings you could afford at that price per serving.",
            args)


COST_PAGE = _page(
    "js-cook-cost", 264, "Cooking: cost per serving",
    "The price of a dish is the quantity of each ingredient times its price "
    "per unit, added together. Give each ingredient a const, flour = 0.25 * "
    "1.6, so a long sum reads like the shopping list. Dividing the total "
    "by the servings gives the cost of one serving, and multiplying that "
    "by how many servings go in a portion gives the cost of a portion. "
    "Prices are decimals, which a computer stores as near misses, so print "
    "money with toFixed(2), which rounds to two decimal places and keeps "
    "a trailing zero: 1.6 prints as 1.60. To ask how many servings a "
    "budget buys, divide the budget by the cost of one and use Math.floor: "
    "you can buy 5 servings, never 5.7. Comparing two costs is a "
    "comparison like any other, and prints true or false.",
    "with flour = 0.25 * 1.6, eggs = 3 * 0.35 and milk = 0.5 * 0.9, the "
    "total is 1.9, and (total / 6).toFixed(2) prints 0.32; "
    "Math.floor(10 / 0.32) would be 31 servings",
    "js_cook_cost",
    tuple(_cost_row(row) for row in _COSTS),
)


# ── 265. Nutrition ───────────────────────────────────────────

_MACROS = f"protein and carbohydrate are {KCAL_PROTEIN} kcal a gram, fat is {KCAL_FAT}"

_NUTRIENTS = {
    "sodium": "mg", "fibre": "g", "fat": "g", "protein": "g", "calcium": "mg",
}

_NUTRITION = (
    ("cal", 25, 40, 12),
    ("cal", 30, 10, 20),
    ("cal", 8, 55, 3),
    ("cal", 40, 0, 15),
    ("cal", 12, 30, 25),
    ("per", 90, 210, 55, 7),
    ("per", 120, 300, 80, 6),
    ("per", 60, 150, 40, 5),
    ("per", 45, 260, 30, 3),
    ("per", 80, 180, 70, 6),
    ("dv", 90, 210, 55, 4),
    ("dv", 120, 300, 80, 6),
    ("dv", 60, 150, 40, 5),
    ("dv", 45, 260, 30, 3),
    ("dvof", "sodium", 940, 2300),
    ("dvof", "fibre", 9, 28),
    ("dvof", "fat", 22, 78),
    ("fatpct", 25, 40, 12),
    ("fatpct", 30, 10, 20),
    ("fatpct", 12, 30, 25),
)


def _nutrition_row(row):
    want = row[0]
    if want == "dvof":
        _, nutrient, amount, dv = row
        unit = _NUTRIENTS[nutrient]
        return (f"A serving has {amount} {unit} of {nutrient}. The daily value "
                f"for {nutrient} is {dv} {unit}: print the percent of the "
                f"daily value one serving gives, rounded to a whole number.",
                {"want": want, "nutrient": nutrient, "amount": amount, "dv": dv})
    p, c, f = row[1:4]
    args = {"want": want, "protein": p, "carbs": c, "fat": f}
    has = f"{p} g of protein, {c} g of carbohydrate and {f} g of fat"
    if want == "cal":
        return (f"A snack has {has}, and {_MACROS}. Print its calories in "
                f"kcal.", args)
    if want == "fatpct":
        return (f"A snack has {has}, and {_MACROS}. Print the percent of its "
                f"calories that come from fat, rounded to a whole number.",
                args)
    servings = row[4]
    args["servings"] = servings
    whole = f"A whole recipe has {has} and makes {servings} servings, and {_MACROS}."
    if want == "per":
        return (f"{whole} Print the calories in one serving, to one decimal "
                f"place.", args)
    return (f"{whole} The daily value for energy is {DAILY_KCAL} kcal: print "
            f"the percent of it that one serving gives, rounded to a whole "
            f"number.", args)


NUTRITION_PAGE = _page(
    "js-cook-nutrition", 265, "Cooking: nutrition",
    "A nutrition label can be worked out from three numbers. A gram of "
    "protein or carbohydrate carries 4 kcal and a gram of fat carries 9, so "
    "the calories are protein * 4 + carbs * 4 + fat * 9. A recipe's total "
    "divided by its servings gives one serving, and toFixed(1) prints it "
    "to one decimal place. Labels also say what percent of the daily value "
    "a serving gives: the serving's amount over the daily value, times 100. "
    "Math.round makes that a whole number, which is how labels print it. "
    "The order matters for reading more than for the answer: divide to get "
    "the fraction of a day, then multiply by 100 to turn it into a percent. "
    "The same shape finds what share of the calories is fat: the fat's "
    "calories, fat * 9, over all the calories.",
    "25 g of protein, 40 of carbohydrate and 12 of fat is 25 * 4 + 40 * 4 + "
    "12 * 9, 368 kcal; a 690 mg serving against a 2300 mg daily value is "
    "690 / 2300 * 100, about 30, and Math.round of it prints 30",
    "js_cook_nutrition",
    tuple(_nutrition_row(row) for row in _NUTRITION),
)


# ── 266. A timeline counted backwards ────────────────────────

_TIMELINES = (
    ("start", (19, 30), 25, 90),
    ("start", (18, 0), 30, 45),
    ("start", (12, 15), 20, 50),
    ("start", (0, 30), 15, 60),
    ("start", (1, 10), 25, 120),
    ("start", (9, 0), 10, 45),
    ("start", (7, 45), 15, 25),
    ("steps", (19, 0), 20, 75),
    ("steps", (13, 30), 35, 90),
    ("steps", (0, 15), 25, 40),
    ("steps", (8, 10), 15, 30),
    ("steps", (1, 0), 20, 50),
    ("steps", (20, 45), 45, 100),
    ("steps", (6, 5), 10, 20),
    ("ready", (22, 40), 3, 50),
    ("ready", (17, 15), 2, 30),
    ("ready", (9, 5), 1, 10),
    ("ready", (23, 50), 0, 25),
    ("ready", (14, 20), 4, 55),
    ("ready", (21, 0), 2, 45),
)

_WRAP = ("Clock times wrap past midnight, so 25 minutes before 00:10 is 23:45. "
         "Print times as HH:MM, with a leading zero on a single digit.")


def _hhmm(hm) -> str:
    return f"{hm[0]:02d}:{hm[1]:02d}"


def _timeline_row(row):
    want = row[0]
    if want == "ready":
        _, begin, hours, mins = row
        return (f"Something goes in the oven at {_hhmm(begin)} and takes "
                f"{hours} h {mins} min. {_WRAP} Print the time it is ready.",
                {"want": want, "begin": begin, "hours": hours, "mins": mins})
    _, serve, prep, cook = row
    args = {"want": want, "serve": serve, "prep": prep, "cook": cook}
    start = (f"Dinner is served at {_hhmm(serve)}. Prep takes {prep} minutes, "
             f"then cooking takes {cook}. {_WRAP}")
    if want == "start":
        return (f"{start} Work back from the serving time and print when to "
                f"start the prep.", args)
    return (f"{start} Work back from the serving time and print when to start "
            f"the prep, then when to put it in to cook.", args)


TIMELINE_PAGE = _page(
    "js-cook-timeline", 266, "Cooking: a timeline backwards",
    "To serve dinner at 19:30, work backwards: take the cooking time off "
    "the serving time, then the prep time off that. Times are easiest as "
    "one number, minutes since midnight: 19 * 60 + 30 is 1170, and "
    "subtracting is then plain arithmetic. To turn minutes back into a "
    "clock, Math.floor(m / 60) is the hours and m % 60 is the minutes. A "
    "clock never says 7:5, so String(n).padStart(2, \"0\") adds zeros in "
    "front until the text is 2 characters long. Dinner at 00:30 sends the "
    "start before midnight, and the number goes negative, but % 1440, the "
    "minutes in a day, wraps it back onto the clock. In JavaScript the "
    "remainder keeps the sign of the number it is taking from, so "
    "((t % 1440) + 1440) % 1440 is the wrap that is safe for negatives as "
    "well. The same wrap carries a start time forwards past midnight.",
    "const m = 17 * 60 + 5 is 1025; Math.floor(m / 60) is 17 and m % 60 is "
    "5, so `${String(17).padStart(2, \"0\")}:${String(5).padStart(2, \"0\")}` "
    "prints 17:05; at -75 minutes, ((-75 % 1440) + 1440) % 1440 is 1365, "
    "which is 22:45",
    "js_cook_timeline",
    tuple(_timeline_row(row) for row in _TIMELINES),
)


# ── 267. A recipe card ───────────────────────────────────────

_CARDS = (
    ("two", "price", 2, 8, 6, ("Flour", "Butter", "Sugar", "Milk")),
    ("two", "grams", 0, 8, 6, ("Eggs", "Cheese", "Rice", "Onion")),
    ("two", "kcal", 0, 9, 6, ("Flour", "Butter", "Cheese", "Oil")),
    ("two", "grams", 1, 8, 8, ("Tomato", "Oil", "Milk")),
    ("two", "price", 2, 10, 7, ("Cheese", "Tomato", "Eggs", "Rice")),
    ("header", "price", 2, 8, 6, ("Flour", "Butter", "Sugar"), "Price"),
    ("header", "grams", 0, 8, 6, ("Eggs", "Milk", "Rice"), "Grams"),
    ("header", "kcal", 0, 9, 6, ("Flour", "Cheese", "Oil"), "Kcal"),
    ("header", "price", 2, 8, 7, ("Cheese", "Tomato", "Onion"), "Cost"),
    ("header", "grams", 1, 9, 8, ("Butter", "Sugar", "Tomato"), "Weight"),
    ("three", (("price", 2, 6), ("kcal", 0, 5)), 8, ("Flour", "Butter", "Sugar")),
    ("three", (("grams", 0, 5), ("price", 2, 6)), 8, ("Eggs", "Milk", "Cheese")),
    ("three", (("kcal", 0, 5), ("grams", 0, 5)), 9, ("Rice", "Onion", "Tomato")),
    ("three", (("price", 2, 7), ("grams", 1, 7)), 8, ("Oil", "Flour", "Cheese")),
    ("three", (("grams", 0, 6), ("kcal", 0, 6)), 10, ("Butter", "Eggs", "Milk")),
    ("numbered", "grams", 0, 9, 6, ("Flour", "Butter", "Sugar", "Eggs")),
    ("numbered", "price", 2, 8, 6, ("Cheese", "Tomato", "Rice", "Milk")),
    ("numbered", "kcal", 0, 8, 5, ("Flour", "Butter", "Oil", "Onion")),
    ("numbered", "grams", 1, 9, 8, ("Milk", "Rice", "Tomato", "Cheese")),
    ("numbered", "price", 2, 8, 6, ("Eggs", "Flour", "Oil", "Sugar")),
)

_BAR = "a | with a space on each side"


def _column(field: str, digits: int, width: int) -> str:
    noun = CARD_FIELDS[field][2]
    return f"the {noun} {_places(digits)} padded at the start to {width} characters"


def _card_array(field: str, names) -> tuple[str, tuple]:
    slot, describe, _ = CARD_FIELDS[field]
    items = tuple((n, INGREDIENTS[n][slot]) for n in names)
    listing = _and(f"{n} {_say(v)}" for n, v in items)
    return (f"Make an array of ingredient objects, each with a name and "
            f"{describe} as {field}: {listing}.", items)


def _card_row(row):
    want = row[0]
    if want == "three":
        _, ((f1, d1, w1), (f2, d2, w2)), nw, names = row
        s1, s2 = CARD_FIELDS[f1][0], CARD_FIELDS[f2][0]
        items = tuple((n, INGREDIENTS[n][s1], INGREDIENTS[n][s2]) for n in names)
        listing = "; ".join(f"{n} {_say(v1)} and {_say(v2)}" for n, v1, v2 in items)
        return (f"Make an array of ingredient objects, each with a name, "
                f"{CARD_FIELDS[f1][1]} as {f1} and {CARD_FIELDS[f2][1]} as "
                f"{f2}: {listing}. For each ingredient print one line: the "
                f"name padded at the end to {nw} characters, {_BAR}, "
                f"{_column(f1, d1, w1)}, another such |, and "
                f"{_column(f2, d2, w2)}.",
                {"want": want, "columns": ((f1, d1, w1), (f2, d2, w2)),
                 "name_width": nw, "items": items})
    _, field, digits, nw, width, names, *title = row
    make, items = _card_array(field, names)
    args = {"want": want, "field": field, "digits": digits, "name_width": nw,
            "width": width, "items": items}
    name = f"the name padded at the end to {nw} characters"
    column = _column(field, digits, width)
    if want == "numbered":
        return (f"{make} Number the ingredients from 1 and print one line for "
                f"each: the number, a full stop and a space, then {name} and "
                f"{column}.", args)
    if want == "header":
        args["title"] = title[0]
        return (f"{make} First print a header line made the same way from "
                f"the words Item and {title[0]}, then one line for each "
                f"ingredient: {name}, then {_BAR}, then {column}.", args)
    return (f"{make} For each ingredient print one line: {name}, then {_BAR}, "
            f"then {column}.", args)


CARD_PAGE = _page(
    "js-cook-card", 267, "Cooking: a recipe card",
    "A recipe card lines up when every value in a column takes the same "
    "width. padEnd(8) adds spaces after a string until it is 8 characters "
    "long, which suits names, read from the left. padStart(6) adds the "
    "spaces in front, which suits numbers: their digits and decimal points "
    "then line up on the right. Both are string methods, so turn the number "
    "into a string first. toFixed(2) does that and fixes how many decimals "
    "it shows, so 1 and 1.1 come out as 1.00 and 1.10, and String(n) does "
    "it for whole numbers. A string already as long as the width comes back "
    "unchanged, so pick widths that fit the longest value with room to "
    "spare. A template literal puts the padded pieces together, with \" | \" "
    "between the columns.",
    "`${\"Flour\".padEnd(8)} | ${(0.4).toFixed(2).padStart(6)}` is Flour and "
    "three spaces, then \" | \", then two spaces and 0.40, and every row "
    "built the same way lines up under it",
    "js_cook_card",
    tuple(_card_row(row) for row in _CARDS),
)


JSCOOKING_PAGES: tuple[Page, ...] = (
    SCALE_PAGE,
    UNITS_PAGE,
    TEMP_PAGE,
    TIME_PAGE,
    FILTER_PAGE,
    SHOP_PAGE,
    COST_PAGE,
    NUTRITION_PAGE,
    TIMELINE_PAGE,
    CARD_PAGE,
)
