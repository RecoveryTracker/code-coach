"""JavaScript: cooking and recipes.

Ten pages of kitchen arithmetic, each one a short program that runs in plain
node with no DOM: scaling a recipe to a new number of servings, converting
cups and spoons and ounces, oven temperatures and gas marks, a roasting time
worked out from the weight, filtering an array of recipes, merging shopping
lists, cost per serving, nutrition from macros, a timeline counted backwards
from the time dinner is served, and a recipe card lined up with padEnd and
padStart.

The numbers arrive in the arguments, and every prompt states the ones it
needs: the conversion factors, the gas mark table, the daily values. The few
constants that several rows share are kept here as the text the program
types, so the prompt, the program and the oracle all read the very same
digits.

The oracle never runs the JavaScript. It works each answer out in Python,
doing the same operations in the same order so the doubles come out
identical, and the tests then hold node to it. Anything that is not a whole
number is printed with toFixed, which emit_jsgame._fixed models exactly. A
learner may well multiply and divide in another order, which can move the
last bit of a double; that only changes what prints when the answer sits
right on a rounding edge, so rows that do are refused here (halves for
toFixed and Math.round, whole numbers for Math.floor and Math.ceil), and
every exercise prints the same whichever order its arithmetic is done in.
"""

from __future__ import annotations

import math
from decimal import Decimal

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines
from code_coach.workbook.emit_jsgame import _bool, _fixed, _lit, _num

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_cook_scale", "scaling a recipe's amounts to a new number of servings"),
    Shape("js_cook_units", "converting cups, spoons, millilitres, ounces and grams"),
    Shape("js_cook_temp", "oven temperatures in Celsius, Fahrenheit and gas marks"),
    Shape("js_cook_time", "a cooking time from the weight, as hours and minutes"),
    Shape("js_cook_filter", "filtering an array of recipes and joining what is left"),
    Shape("js_cook_shop", "merging shopping lists by adding up repeated items"),
    Shape("js_cook_cost", "cost per serving and per portion from prices"),
    Shape("js_cook_nutrition", "calories from macros, per serving and as a percent of daily value"),
    Shape("js_cook_timeline", "start times counted back from the serving time, as HH:MM"),
    Shape("js_cook_card", "a recipe card lined up with padEnd and padStart"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── The constants, as the program writes them ────────────────

#: Millilitres in a cup, a tablespoon and a teaspoon, as the prompts say them.
CUP_ML = "240"
TBSP_ML = "15"
TSP_ML = "5"
#: Grams in an ounce, the rounded figure kitchens use.
OZ_G = "28.35"
#: Minutes in a day.
DAY_MIN = 1440
#: The daily energy a nutrition label is worked against, in kcal.
DAILY_KCAL = "2000"

#: Gas mark to °C, as the prompts print the table.
GAS: dict[int, int] = {
    1: 140, 2: 150, 3: 170, 4: 180, 5: 190, 6: 200, 7: 220, 8: 230, 9: 240,
}

#: What a gram of each macronutrient is worth, in kcal.
KCAL_PROTEIN, KCAL_CARBS, KCAL_FAT = 4, 4, 9


# ── Writing numbers and names ────────────────────────────────


def _code(x) -> str:
    """A number literal. A whole float such as 250.0 is written 250."""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return _lit(x)


def _name(s: str) -> str:
    """A name or word as a string literal."""
    if not s.replace(" ", "").isalpha():
        raise ValueError(f"{s!r}: names are plain words")
    return f'"{s}"'


def _word(s: str, *avoid: str) -> str:
    """A lowercase word used as a variable name: flour, chicken."""
    if not (s.isalpha() and s.islower()):
        raise ValueError(f"{s!r}: one lowercase word")
    if s in avoid:
        raise ValueError(f"{s!r} clashes with another name in the program")
    return s


def _val(v) -> str:
    return _bool(v) if isinstance(v, bool) else _code(v)


def _items(rows, size: int) -> list[tuple]:
    """The rows of a data page: (name, value, ...), checked."""
    items = [tuple(r) for r in rows]
    names = [r[0] for r in items]
    if len(items) < 3:
        raise ValueError("three rows at least, or it is hardly data")
    if len(set(names)) != len(names):
        raise ValueError("names must be unique, or the output is ambiguous")
    if any(len(r) != size for r in items):
        raise ValueError("every row needs every field")
    return items


def _data(rows, *fields: str) -> list[str]:
    """const items = [ { name: "Flour", grams: 250 }, ... ];"""
    lines = []
    for name, *values in _items(rows, len(fields) + 1):
        body = ", ".join(f"{f}: {_val(v)}" for f, v in zip(fields, values))
        lines.append(f"  {{ name: {_name(name)}, {body} }},")
    return ["const items = [", *lines, "];"]


# ── Refusing anything that could print two ways ──────────────

#: How close, relative to its size, a value may come to an edge.
_TOO_CLOSE = 1e-9


def _edge(x, digits: int) -> None:
    scaled = abs(x) * 10 ** digits
    if abs(scaled - math.floor(scaled) - 0.5) < _TOO_CLOSE * max(1.0, scaled):
        raise ValueError(f"{x} sits on a rounding edge at {digits} places")


def _shown(x, digits: int) -> str:
    """toFixed(digits), for a value no order of operations can tip over.

    Halfway between two printable values, the last bit of the double decides
    which way toFixed goes, and that bit depends on the order the arithmetic
    was done in. Such values are refused rather than guessed.
    """
    _edge(x, digits)
    return _fixed(x, digits)


def _near_whole(x: float) -> None:
    near = round(x)
    if abs(x - near) < _TOO_CLOSE * max(1.0, abs(x)):
        raise ValueError(f"{x} is too near {near} to round it a fixed way")


def _floor(x: float) -> int:
    """Math.floor of a computed value, refused a hair from a whole number."""
    _near_whole(x)
    return math.floor(x)


def _ceil(x: float) -> int:
    """Math.ceil of a computed value, refused a hair from a whole number."""
    _near_whole(x)
    return math.ceil(x)


def _round(x: float) -> int:
    """Math.round: the nearest whole number, with halves going up.

    It rounds the exact value of the double, as the spec says, rather than
    adding 0.5 in floating point, which can round on its own. Kept to
    positive values: Math.round of a small negative is -0, which prints -0.
    """
    if x <= 0:
        raise ValueError("Math.round is only used on positive values here")
    _edge(x, 0)
    return math.floor(Decimal(x) + Decimal("0.5"))


# ── 1. Scaling a recipe ──────────────────────────────────────

_SCALE_NAMES = ("original", "wanted", "needed", "factor")


def _scale(a: dict) -> str:
    want = a["want"]
    head = [f"const original = {_code(a['orig'])};",
            f"const wanted = {_code(a['wanted'])};"]
    if want == "amount":
        t = _word(a["thing"], *_SCALE_NAMES)
        return _lines(
            *head,
            f"const {t} = {_code(a['qty'])};",
            f"const needed = {t} * wanted / original;",
            "console.log(needed.toFixed(1));",
        )
    if want == "factor":
        return _lines(
            *head,
            "const factor = wanted / original;",
            "console.log(factor.toFixed(2));",
            f"console.log(({_code(a['qty'])} * factor).toFixed(1));",
        )
    if want == "two":
        (t1, q1), (t2, q2) = a["items"]
        n1, n2 = _word(t1, *_SCALE_NAMES), _word(t2, *_SCALE_NAMES, t1)
        return _lines(
            *head,
            f"const {n1} = {_code(q1)} * wanted / original;",
            f"const {n2} = {_code(q2)} * wanted / original;",
            f"console.log({n1}.toFixed(1));",
            f"console.log({n2}.toFixed(1));",
        )
    if want == "whole":
        t = _word(a["thing"], *_SCALE_NAMES)
        return _lines(
            *head,
            f"const {t} = Math.ceil({_code(a['qty'])} * wanted / original);",
            f"console.log({t});",
        )
    raise ValueError(want)


def _scale_out(a: dict) -> str:
    want = a["want"]
    orig, wanted = a["orig"], a["wanted"]
    if orig == wanted:
        raise ValueError("scaling to the same number of servings shows nothing")
    if want == "amount":
        return _shown(a["qty"] * wanted / orig, 1)
    if want == "factor":
        factor = wanted / orig
        return NL.join([_shown(factor, 2), _shown(a["qty"] * factor, 1)])
    if want == "two":
        (_, q1), (_, q2) = a["items"]
        return NL.join([_shown(q1 * wanted / orig, 1),
                        _shown(q2 * wanted / orig, 1)])
    if want == "whole":
        return str(_ceil(a["qty"] * wanted / orig))
    raise ValueError(want)


# ── 2. Unit conversions ──────────────────────────────────────

_UNIT_VAR = {"cup": "cups", "tbsp": "tbsp", "tsp": "tsp"}
_UNIT_ML = {
    "cup": ("mlPerCup", CUP_ML),
    "tbsp": ("mlPerTbsp", TBSP_ML),
    "tsp": ("mlPerTsp", TSP_ML),
}


def _quarters(x) -> None:
    if not (x * 4).is_integer():
        raise ValueError(f"{x}: quarters only, so the product is exact")


def _units(a: dict) -> str:
    want = a["want"]
    if want == "cup_tbsp":
        return _lines(
            f"const mlPerCup = {CUP_ML};",
            f"const mlPerTbsp = {TBSP_ML};",
            f"const cups = {_code(a['qty'])};",
            "const tbsp = cups * mlPerCup / mlPerTbsp;",
            "console.log(tbsp);",
        )
    if want == "oz_g":
        return _lines(
            f"const gramsPerOz = {OZ_G};",
            f"const oz = {_code(a['qty'])};",
            "const grams = oz * gramsPerOz;",
            "console.log(grams.toFixed(1));",
        )
    if want == "g_oz":
        return _lines(
            f"const gramsPerOz = {OZ_G};",
            f"const grams = {_code(a['qty'])};",
            "const oz = grams / gramsPerOz;",
            "console.log(oz.toFixed(2));",
        )
    factor, ml = _UNIT_ML[a["unit"]]
    var = _UNIT_VAR[a["unit"]]
    if want == "to_ml":
        return _lines(
            f"const {factor} = {ml};",
            f"const {var} = {_code(a['qty'])};",
            f"const ml = {var} * {factor};",
            "console.log(ml);",
        )
    if want == "from_ml":
        return _lines(
            f"const {factor} = {ml};",
            f"const ml = {_code(a['qty'])};",
            f"const {var} = ml / {factor};",
            f"console.log({var}.toFixed({a['digits']}));",
        )
    raise ValueError(want)


def _units_out(a: dict) -> str:
    want, q = a["want"], a["qty"]
    if want == "cup_tbsp":
        _quarters(q)
        return _num(q * int(CUP_ML) / int(TBSP_ML))
    if want == "oz_g":
        return _shown(q * float(OZ_G), 1)
    if want == "g_oz":
        return _shown(q / float(OZ_G), 2)
    ml = int(_UNIT_ML[a["unit"]][1])
    if want == "to_ml":
        _quarters(q)
        return _num(q * ml)
    if want == "from_ml":
        return _shown(q / ml, a["digits"])
    raise ValueError(want)


# ── 3. Temperatures and gas marks ────────────────────────────


def _marks() -> str:
    body = ", ".join(f"{k}: {v}" for k, v in GAS.items())
    return f"const marks = {{ {body} }};"


def _temp(a: dict) -> str:
    want = a["want"]
    if want == "c2f":
        return _lines(
            f"const celsius = {_code(a['c'])};",
            "const fahrenheit = celsius * 9 / 5 + 32;",
            "console.log(fahrenheit.toFixed(1));",
        )
    if want == "f2c":
        return _lines(
            f"const fahrenheit = {_code(a['f'])};",
            "const celsius = (fahrenheit - 32) * 5 / 9;",
            "console.log(celsius.toFixed(1));",
        )
    if want == "round":
        return _lines(
            f"const fahrenheit = {_code(a['f'])};",
            "const celsius = (fahrenheit - 32) * 5 / 9;",
            "console.log(Math.round(celsius));",
        )
    if want == "gas2c":
        return _lines(
            _marks(),
            f"const mark = {_code(a['mark'])};",
            "console.log(marks[mark]);",
        )
    if want == "gas2f":
        return _lines(
            _marks(),
            f"const mark = {_code(a['mark'])};",
            "const celsius = marks[mark];",
            "const fahrenheit = celsius * 9 / 5 + 32;",
            "console.log(fahrenheit.toFixed(1));",
        )
    if want == "c2gas":
        return _lines(
            _marks(),
            f"const celsius = {_code(a['c'])};",
            "const mark = Object.keys(marks).find((key) => marks[key] === celsius);",
            "console.log(mark);",
        )
    raise ValueError(want)


def _temp_out(a: dict) -> str:
    want = a["want"]
    if want == "c2f":
        return _shown(a["c"] * 9 / 5 + 32, 1)
    if want == "f2c":
        return _shown((a["f"] - 32) * 5 / 9, 1)
    if want == "round":
        return str(_round((a["f"] - 32) * 5 / 9))
    if want == "gas2c":
        return str(GAS[a["mark"]])
    if want == "gas2f":
        return _shown(GAS[a["mark"]] * 9 / 5 + 32, 1)
    if want == "c2gas":
        marks = [k for k, v in GAS.items() if v == a["c"]]
        if len(marks) != 1:
            raise ValueError(f"{a['c']} is not exactly one gas mark")
        return str(marks[0])
    raise ValueError(want)


# ── 4. A cooking time from the weight ────────────────────────

_TIME_NAMES = ("base", "perKg", "kg", "total", "rest", "minutes")


def _time_head(a: dict) -> list[str]:
    return [f"const base = {_code(a['base'])};",
            f"const perKg = {_code(a['per'])};",
            f"const kg = {_code(a['kg'])};"]


def _time(a: dict) -> str:
    want = a["want"]
    if want == "min":
        return _lines(
            *_time_head(a),
            "const minutes = Math.floor(base + perKg * kg);",
            "console.log(minutes);",
        )
    if want == "hm":
        return _lines(
            *_time_head(a),
            "const total = Math.floor(base + perKg * kg);",
            "console.log(`${Math.floor(total / 60)} h ${total % 60} min`);",
        )
    if want == "rest":
        return _lines(
            *_time_head(a),
            f"const rest = {_code(a['rest'])};",
            "const total = Math.floor(base + perKg * kg) + rest;",
            "console.log(`${Math.floor(total / 60)} h ${total % 60} min`);",
        )
    if want == "longer":
        (t1, b1, p1, k1), (t2, b2, p2, k2) = a["one"], a["two"]
        n1, n2 = _word(t1, *_TIME_NAMES), _word(t2, *_TIME_NAMES, t1)
        return _lines(
            f"const {n1} = Math.floor({_code(b1)} + {_code(p1)} * {_code(k1)});",
            f"const {n2} = Math.floor({_code(b2)} + {_code(p2)} * {_code(k2)});",
            f"console.log({n1});",
            f"console.log({n2});",
            f"console.log({n1} > {n2});",
        )
    raise ValueError(want)


def _roast(base, per, kg) -> int:
    return _floor(base + per * kg)


def _hm(total: int) -> str:
    if total < 60:
        raise ValueError("under an hour belongs on the minutes rows")
    return f"{total // 60} h {total % 60} min"


def _time_out(a: dict) -> str:
    want = a["want"]
    if want == "min":
        return str(_roast(a["base"], a["per"], a["kg"]))
    if want == "hm":
        return _hm(_roast(a["base"], a["per"], a["kg"]))
    if want == "rest":
        return _hm(_roast(a["base"], a["per"], a["kg"]) + a["rest"])
    if want == "longer":
        (_, b1, p1, k1), (_, b2, p2, k2) = a["one"], a["two"]
        m1, m2 = _roast(b1, p1, k1), _roast(b2, p2, k2)
        if m1 == m2:
            raise ValueError("a tie: neither takes longer")
        return NL.join([str(m1), str(m2), _bool(m1 > m2)])
    raise ValueError(want)


# ── 5. Filter, map and join ──────────────────────────────────


def _test(field: str, op: str, limit) -> str:
    """The arrow function's body: r.minutes < 30, or r.veg."""
    if field == "veg":
        if op not in ("is", "not"):
            raise ValueError(op)
        return "r.veg" if op == "is" else "!r.veg"
    if op not in (">", "<"):
        raise ValueError(op)
    return f"r.{field} {op} {_code(limit)}"


def _filter(a: dict) -> str:
    want, f = a["want"], a["field"]
    test = _test(f, a["op"], a.get("limit"))
    data = _data(a["items"], f)
    if want == "names":
        return _lines(
            *data,
            f"const names = items.filter((r) => {test}).map((r) => r.name);",
            'console.log(names.join(", "));',
        )
    if want == "count":
        return _lines(
            *data,
            f"const count = items.filter((r) => {test}).length;",
            "console.log(count);",
        )
    if want == "label":
        tail = " min" if f == "minutes" else ""
        mid = "" if f == "minutes" else "for "
        label = f"`${{r.name}} {mid}${{r.{f}}}{tail}`"
        return _lines(
            *data,
            f"const labels = items.filter((r) => {test}).map((r) => {label});",
            'console.log(labels.join(", "));',
        )
    if want in ("some", "every"):
        return _lines(*data, f"console.log(items.{want}((r) => {test}));")
    raise ValueError(want)


def _keep(value, field: str, op: str, limit) -> bool:
    if field == "veg":
        if not isinstance(value, bool):
            raise ValueError("veg is true or false")
        return value if op == "is" else not value
    if isinstance(value, bool) or value == limit:
        raise ValueError(f"{value} equals the limit, so < and <= would disagree")
    return value > limit if op == ">" else value < limit


def _filter_out(a: dict) -> str:
    want, f = a["want"], a["field"]
    items = _items(a["items"], 2)
    kept = [(n, v) for n, v in items if _keep(v, f, a["op"], a.get("limit"))]
    if want == "some":
        return _bool(bool(kept))
    if want == "every":
        return _bool(len(kept) == len(items))
    if not kept or len(kept) == len(items):
        raise ValueError("the filter has to keep some recipes and drop some")
    if want == "names":
        return ", ".join(n for n, _ in kept)
    if want == "count":
        return str(len(kept))
    if want == "label":
        if f == "minutes":
            return ", ".join(f"{n} {_num(v)} min" for n, v in kept)
        return ", ".join(f"{n} for {_num(v)}" for n, v in kept)
    raise ValueError(want)


# ── 6. Merging shopping lists ────────────────────────────────

_MERGE = (
    "const totals = lines.reduce((sum, [item, qty]) => {",
    "  sum[item] = (sum[item] || 0) + qty;",
    "  return sum;",
    "}, {});",
)


def _pairs(lines) -> list[tuple]:
    pairs = [tuple(p) for p in lines]
    if any(len(p) != 2 or not isinstance(p[1], int) or p[1] < 1 for p in pairs):
        raise ValueError("each line is an item and a whole number of packs")
    items = [p[0] for p in pairs]
    if len(set(items)) < 3 or len(set(items)) == len(items):
        raise ValueError("three items at least, and some of them repeated")
    return pairs


def _totals(lines) -> dict:
    totals: dict = {}
    for item, qty in _pairs(lines):
        totals[item] = totals.get(item, 0) + qty
    return totals


def _shop(a: dict) -> str:
    want = a["want"]
    pairs = _pairs(a["lines"])
    body = ", ".join(f"[{_name(i)}, {q}]" for i, q in pairs)
    first = f"const lines = [{body}];"
    if want == "sorted":
        return _lines(
            first, *_MERGE,
            "for (const item of Object.keys(totals).sort()) {",
            "  console.log(`${item}: ${totals[item]}`);",
            "}",
        )
    if want == "oneline":
        return _lines(
            first, *_MERGE,
            "const text = Object.keys(totals).sort()"
            ".map((item) => `${item} ${totals[item]}`).join(\", \");",
            "console.log(text);",
        )
    if want == "count":
        return _lines(
            first, *_MERGE,
            "console.log(Object.keys(totals).length);",
            "console.log(Object.values(totals).reduce((a, b) => a + b, 0));",
        )
    if want == "most":
        return _lines(
            first, *_MERGE,
            "const [item, qty] = Object.entries(totals).sort((a, b) => b[1] - a[1])[0];",
            "console.log(`${item} ${qty}`);",
        )
    if want == "map":
        return _lines(
            first,
            "const totals = new Map();",
            "for (const [item, qty] of lines) {",
            "  totals.set(item, (totals.get(item) || 0) + qty);",
            "}",
            "for (const item of [...totals.keys()].sort()) {",
            "  console.log(`${item}: ${totals.get(item)}`);",
            "}",
        )
    raise ValueError(want)


def _shop_out(a: dict) -> str:
    want = a["want"]
    totals = _totals(a["lines"])
    names = sorted(totals)
    if want in ("sorted", "map"):
        return NL.join(f"{n}: {totals[n]}" for n in names)
    if want == "oneline":
        return ", ".join(f"{n} {totals[n]}" for n in names)
    if want == "count":
        return NL.join([str(len(totals)), str(sum(totals.values()))])
    if want == "most":
        ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        if ranked[0][1] == ranked[1][1]:
            raise ValueError("a tie for the biggest total")
        return f"{ranked[0][0]} {ranked[0][1]}"
    raise ValueError(want)


# ── 7. Cost per serving and per portion ──────────────────────

_COST_NAMES = ("total", "perServing", "perPortion")


def _cost_lines(items) -> tuple[list[str], str]:
    """One const per ingredient, and the sum of them."""
    if not 2 <= len(items) <= 4:
        raise ValueError("two to four ingredients")
    names: list[str] = []
    lines = []
    for name, qty, price in items:
        n = _word(name, *_COST_NAMES, *names)
        names.append(n)
        lines.append(f"const {n} = {_code(qty)} * {_code(price)};")
    return lines, f"const total = {' + '.join(names)};"


def _cost_total(items) -> float:
    total = items[0][1] * items[0][2]
    for _, qty, price in items[1:]:
        total = total + qty * price
    return total


def _cost(a: dict) -> str:
    want = a["want"]
    if want == "cheaper":
        (n1, t1, s1), (n2, t2, s2) = a["one"], a["two"]
        w1, w2 = _word(n1, *_COST_NAMES), _word(n2, *_COST_NAMES, n1)
        return _lines(
            f"const {w1} = {_code(t1)} / {_code(s1)};",
            f"const {w2} = {_code(t2)} / {_code(s2)};",
            f"console.log({w1}.toFixed(2));",
            f"console.log({w2}.toFixed(2));",
            f"console.log({w1} < {w2});",
        )
    lines, total = _cost_lines(a["items"])
    servings = _code(a["servings"])
    if want == "serving":
        return _lines(*lines, total, f"console.log((total / {servings}).toFixed(2));")
    if want == "both":
        return _lines(
            *lines, total,
            "console.log(total.toFixed(2));",
            f"console.log((total / {servings}).toFixed(2));",
        )
    if want == "portion":
        return _lines(
            *lines, total,
            f"const perServing = total / {servings};",
            "console.log(perServing.toFixed(2));",
            f"console.log((perServing * {_code(a['per'])}).toFixed(2));",
        )
    if want == "afford":
        return _lines(
            *lines, total,
            f"const perServing = total / {servings};",
            f"console.log(Math.floor({_code(a['budget'])} / perServing));",
        )
    raise ValueError(want)


def _cost_out(a: dict) -> str:
    want = a["want"]
    if want == "cheaper":
        (_, t1, s1), (_, t2, s2) = a["one"], a["two"]
        c1, c2 = t1 / s1, t2 / s2
        if abs(c1 - c2) < _TOO_CLOSE:
            raise ValueError("the same cost per serving: neither is cheaper")
        return NL.join([_shown(c1, 2), _shown(c2, 2), _bool(c1 < c2)])
    total = _cost_total(a["items"])
    servings = a["servings"]
    if want == "serving":
        return _shown(total / servings, 2)
    if want == "both":
        return NL.join([_shown(total, 2), _shown(total / servings, 2)])
    if want == "portion":
        per_serving = total / servings
        return NL.join([_shown(per_serving, 2), _shown(per_serving * a["per"], 2)])
    if want == "afford":
        return str(_floor(a["budget"] / (total / servings)))
    raise ValueError(want)


# ── 8. Nutrition ─────────────────────────────────────────────


def _macros(a: dict) -> list[str]:
    return [f"const protein = {_code(a['protein'])};",
            f"const carbs = {_code(a['carbs'])};",
            f"const fat = {_code(a['fat'])};"]


_KCAL = (f"const calories = protein * {KCAL_PROTEIN} + carbs * {KCAL_CARBS}"
         f" + fat * {KCAL_FAT};")


def _kcal(a: dict) -> int:
    return (a["protein"] * KCAL_PROTEIN + a["carbs"] * KCAL_CARBS
            + a["fat"] * KCAL_FAT)


def _nutrition(a: dict) -> str:
    want = a["want"]
    if want == "dvof":
        n = _word(a["nutrient"], "dailyValue")
        return _lines(
            f"const {n} = {_code(a['amount'])};",
            f"const dailyValue = {_code(a['dv'])};",
            f"console.log(Math.round({n} / dailyValue * 100));",
        )
    head = [*_macros(a), _KCAL]
    if want == "cal":
        return _lines(*head, "console.log(calories);")
    if want == "fatpct":
        return _lines(*head, "console.log(Math.round(fat * 9 / calories * 100));")
    servings = _code(a["servings"])
    if want == "per":
        return _lines(*head, f"console.log((calories / {servings}).toFixed(1));")
    if want == "dv":
        return _lines(
            *head,
            f"const perServing = calories / {servings};",
            f"console.log(Math.round(perServing / {DAILY_KCAL} * 100));",
        )
    raise ValueError(want)


def _nutrition_out(a: dict) -> str:
    want = a["want"]
    if want == "dvof":
        return str(_round(a["amount"] / a["dv"] * 100))
    kcal = _kcal(a)
    if want == "cal":
        return str(kcal)
    if want == "fatpct":
        return str(_round(a["fat"] * 9 / kcal * 100))
    if want == "per":
        return _shown(kcal / a["servings"], 1)
    if want == "dv":
        return str(_round(kcal / a["servings"] / int(DAILY_KCAL) * 100))
    raise ValueError(want)


# ── 9. A timeline counted backwards ──────────────────────────

_FMT = (
    "const fmt = (t) => {",
    "  const m = ((t % 1440) + 1440) % 1440;",
    '  return `${String(Math.floor(m / 60)).padStart(2, "0")}:'
    '${String(m % 60).padStart(2, "0")}`;',
    "};",
)


def _clock(hm) -> str:
    h, m = hm
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"{hm} is not a time of day")
    return f"{h} * 60 + {m}"


def _minutes(hm) -> int:
    _clock(hm)
    return hm[0] * 60 + hm[1]


def _timeline(a: dict) -> str:
    want = a["want"]
    if want == "ready":
        return _lines(
            *_FMT,
            f"const begin = {_clock(a['begin'])};",
            f"const duration = {_code(a['hours'])} * 60 + {_code(a['mins'])};",
            "console.log(fmt(begin + duration));",
        )
    head = [*_FMT, f"const serve = {_clock(a['serve'])};",
            f"const prep = {_code(a['prep'])};",
            f"const cook = {_code(a['cook'])};"]
    if want == "start":
        return _lines(*head, "console.log(fmt(serve - prep - cook));")
    if want == "steps":
        return _lines(
            *head,
            "console.log(fmt(serve - cook - prep));",
            "console.log(fmt(serve - cook));",
        )
    raise ValueError(want)


def _fmt_out(t: int) -> str:
    m = t % DAY_MIN
    return f"{m // 60:02d}:{m % 60:02d}"


def _timeline_out(a: dict) -> str:
    want = a["want"]
    if want == "ready":
        return _fmt_out(_minutes(a["begin"]) + a["hours"] * 60 + a["mins"])
    serve = _minutes(a["serve"])
    if a["prep"] + a["cook"] >= DAY_MIN:
        raise ValueError("a day or more of cooking")
    if want == "start":
        return _fmt_out(serve - a["prep"] - a["cook"])
    if want == "steps":
        return NL.join([_fmt_out(serve - a["cook"] - a["prep"]),
                        _fmt_out(serve - a["cook"])])
    raise ValueError(want)


# ── 10. A recipe card that lines up ──────────────────────────


def _cell(field: str, digits: int) -> str:
    """A number as a string: whole ones with String(), the rest with toFixed."""
    return f"String(item.{field})" if digits == 0 else f"item.{field}.toFixed({digits})"


def _card(a: dict) -> str:
    want, nw = a["want"], a["name_width"]
    if want == "three":
        (f1, d1, w1), (f2, d2, w2) = a["columns"]
        row = (f"`${{item.name.padEnd({nw})}} | ${{{_cell(f1, d1)}.padStart({w1})}}"
               f" | ${{{_cell(f2, d2)}.padStart({w2})}}`")
        return _lines(
            *_data(a["items"], f1, f2),
            "for (const item of items) {",
            f"  console.log({row});",
            "}",
        )
    f, d, w = a["field"], a["digits"], a["width"]
    cell = f"${{{_cell(f, d)}.padStart({w})}}"
    if want == "numbered":
        return _lines(
            *_data(a["items"], f),
            "items.forEach((item, i) => {",
            f"  console.log(`${{i + 1}}. ${{item.name.padEnd({nw})}}{cell}`);",
            "});",
        )
    head = []
    if want == "header":
        title = a["title"]
        if not title.isalpha():
            raise ValueError(f"{title!r}: one plain word")
        head = [f'console.log(`${{"Item".padEnd({nw})}} | ${{"{title}".padStart({w})}}`);']
    elif want != "two":
        raise ValueError(want)
    return _lines(
        *_data(a["items"], f),
        *head,
        "for (const item of items) {",
        f"  console.log(`${{item.name.padEnd({nw})}} | {cell}`);",
        "}",
    )


def _cell_out(value, digits: int, width: int) -> str:
    if digits == 0:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("String() is for whole numbers here; use toFixed")
        text = str(value)
    else:
        text = _shown(value, digits)
    if len(text) >= width:
        raise ValueError(f"{text} does not fit in {width} with a space to spare")
    return text.rjust(width)


def _name_out(name: str, width: int) -> str:
    if len(name) >= width:
        raise ValueError(f"{name} does not fit in {width} with a space to spare")
    return name.ljust(width)


def _card_out(a: dict) -> str:
    want, nw = a["want"], a["name_width"]
    if want == "three":
        (_, d1, w1), (_, d2, w2) = a["columns"]
        return NL.join(
            f"{_name_out(n, nw)} | {_cell_out(v1, d1, w1)} | {_cell_out(v2, d2, w2)}"
            for n, v1, v2 in _items(a["items"], 3))
    d, w = a["digits"], a["width"]
    items = _items(a["items"], 2)
    if want == "numbered":
        return NL.join(
            f"{i}. {_name_out(n, nw)}{_cell_out(v, d, w)}"
            for i, (n, v) in enumerate(items, start=1))
    rows = [f"{_name_out(n, nw)} | {_cell_out(v, d, w)}" for n, v in items]
    if want == "header":
        title = a["title"]
        if len(title) >= w:
            raise ValueError("the title has to fit its column")
        rows.insert(0, f"{_name_out('Item', nw)} | {title.rjust(w)}")
    elif want != "two":
        raise ValueError(want)
    return NL.join(rows)


_BUILDERS = {
    "js_cook_scale": _scale,
    "js_cook_units": _units,
    "js_cook_temp": _temp,
    "js_cook_time": _time,
    "js_cook_filter": _filter,
    "js_cook_shop": _shop,
    "js_cook_cost": _cost,
    "js_cook_nutrition": _nutrition,
    "js_cook_timeline": _timeline,
    "js_cook_card": _card,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "js_cook_scale": _scale_out,
    "js_cook_units": _units_out,
    "js_cook_temp": _temp_out,
    "js_cook_time": _time_out,
    "js_cook_filter": _filter_out,
    "js_cook_shop": _shop_out,
    "js_cook_cost": _cost_out,
    "js_cook_nutrition": _nutrition_out,
    "js_cook_timeline": _timeline_out,
    "js_cook_card": _card_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_cook_scale": Cost(
        "O(1)",
        "Constant: a multiply and a divide per ingredient. Scaling a whole "
        "recipe of n ingredients would be n of them, one each, but doubling "
        "the servings does not make any single sum harder."),
    "js_cook_units": Cost(
        "O(1)",
        "Constant: one multiply or divide by a fixed factor, whatever the "
        "amount. Converting a whole shopping list would be linear in its "
        "length, one conversion each."),
    "js_cook_temp": Cost(
        "O(1)",
        "Constant: a multiply and an add, or a lookup in a table of nine "
        "gas marks. The reverse lookup with find looks at each mark in turn, "
        "but the table never grows, so it is still a fixed few steps."),
    "js_cook_time": Cost(
        "O(1)",
        "Constant: a multiply, an add, a floor and a remainder, however big "
        "the bird is. Counting the minutes off an hour at a time would take "
        "longer for a bigger roast; floor and % find the hours in one step."),
    "js_cook_filter": Cost(
        "O(n)",
        "Linear in the number of recipes, n: filter runs its test once per "
        "recipe, map once per recipe kept and join once per name. some stops "
        "at the first yes and every at the first no, so they can finish "
        "early, but at worst they look at all n."),
    "js_cook_shop": Cost(
        "O(n log n)",
        "Merging is one pass over the n lines, each an object or Map lookup "
        "and an add, so linear. Printing in alphabetical order sorts the k "
        "distinct items, about k log k comparisons, which is what sets the "
        "bound. Searching the totals for a repeat on every line instead "
        "would cost a pass per line."),
    "js_cook_cost": Cost(
        "O(n)",
        "Linear in the number of ingredients, n: one multiply and one add "
        "each. Dividing by the servings and rounding for print are single "
        "steps, however many people are fed."),
    "js_cook_nutrition": Cost(
        "O(1)",
        "Constant: a few multiplies, an add, a divide and a round. Each "
        "macronutrient is one term, whatever the amount; a recipe with n "
        "ingredients to add up would be linear in n."),
    "js_cook_timeline": Cost(
        "O(1)",
        "Constant: a subtraction, a remainder to wrap past midnight and a "
        "floor to split hours from minutes. Stepping back one minute at a "
        "time until the clock came out right would grow with the duration; "
        "% 1440 wraps it in one step."),
    "js_cook_card": Cost(
        "O(n)",
        "Linear in the number of ingredients, n: one line each. Padding a "
        "cell adds at most its width in spaces, a fixed amount per line, so "
        "twice the ingredients is twice the work."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
