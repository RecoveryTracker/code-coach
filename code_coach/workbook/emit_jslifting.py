"""JavaScript: bodybuilding and strength training.

A training log is arithmetic from the first set to the last: volume is sets
times reps times weight, calories come from grams of food, a rest timer
turns seconds into minutes, a one-rep max is estimated with a formula,
working weights are percentages rounded to what a bar can carry, a program
climbs by a fixed step with a lighter week every so often, records live in a
Map, a week of training is an array to ask questions of, and the plates on
each side come from a greedy loop. These pages drill that arithmetic as
short programs in plain node. The gym is the flavour; the numbers are the
point.

The answers are worked out here in Python, and node has to print the same
text. Weights are whole numbers or multiples of 0.25, which a double holds
exactly and both languages print the same short way. Anything else goes
through toFixed or Math.round, each modelled on the exact value of the
double: emit_jsgame._fixed for toFixed, and floor(x + 1/2) for Math.round,
whose halves go up where Python's round() goes to the even neighbour.

A row whose answer sits on a rounding edge - a toFixed whose next digit is
a 5, a Math.round of a half - is refused rather than guessed. There the last
bit of the double decides, and a learner who writes the same formula in a
different, equally right order could land on the other side of the edge.
"""

from __future__ import annotations

import math
from fractions import Fraction

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines
from code_coach.workbook.emit_jsgame import _bool, _fixed, _lit, _num

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_lift_volume", "training volume: sets times reps times weight"),
    Shape("js_lift_macros", "calories and shares from grams of food"),
    Shape("js_lift_timer", "seconds as minutes and seconds, and a session's length"),
    Shape("js_lift_onerm", "estimating a one-rep max from a heavy set"),
    Shape("js_lift_bodycomp", "lean mass and FFMI from weight, body fat and height"),
    Shape("js_lift_percent", "a percentage of a max, rounded to what a bar can carry"),
    Shape("js_lift_overload", "a plan that climbs every week, with deload weeks"),
    Shape("js_lift_records", "personal records kept in a Map"),
    Shape("js_lift_split", "questions about a weekly split, asked of an array"),
    Shape("js_lift_plates", "loading the bar greedily, plate by plate"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: Plates for one side, heaviest first, and the bar they go on.
KG_PLATES = (25, 20, 15, 10, 5, 2.5, 1.25)
KG_BAR = 20
LB_PLATES = (45, 35, 25, 10, 5, 2.5)
LB_BAR = 45

#: The seven days of a split, in the order every split page writes them.
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Values, as JavaScript writes and prints them ─────────────


def _str(s: str) -> str:
    """A plain name as a string literal: no quotes or escapes to get wrong."""
    if not isinstance(s, str) or not s or any(c in s for c in "\"'\\`$"):
        raise ValueError(f"{s!r}: keep names plain")
    return f'"{s}"'


def _word(s: str) -> str:
    """A lift or muscle group: one lowercase word.

    Object.entries puts keys that look like numbers first, whatever order
    they were added in, so a key that is a plain word is what keeps the
    printed order the order things first appeared.
    """
    if not isinstance(s, str) or not s.isalpha() or not s.islower():
        raise ValueError(f"{s!r}: one lowercase word")
    return s


def _kg(x) -> str:
    """A weight as console.log shows it: whole, or a multiple of 0.25.

    A double holds those exactly, and Python and JavaScript both print them
    the same short way (102.5, 61.25), so anything else is refused.
    """
    if isinstance(x, bool) or (Fraction(x) * 4).denominator != 1:
        raise ValueError(f"{x} is not a multiple of 0.25")
    return _num(float(x) if isinstance(x, Fraction) else x)


#: How close to a rounding edge counts as on it. A formula written in a
#: different order moves a double by a few units in the last place, around
#: 1e-14 here, so a millionth is far wider than any of that and far
#: narrower than the gaps between the answers.
_EDGE = Fraction(1, 10**6)


def _js_round(x: float) -> int:
    """Math.round: the nearest whole number, a half going up toward +infinity.

    Python's round() sends a half to the even neighbour instead, so this
    works on the exact value of the double: floor(x + 1/2). A value within
    a hair of a half is refused, because there how the learner wrote the
    formula decides which way it goes.
    """
    exact = Fraction(x)
    if abs(exact - math.floor(exact) - Fraction(1, 2)) < _EDGE:
        raise ValueError(f"{x} is a halfway case for Math.round")
    return math.floor(exact + Fraction(1, 2))


def _to_fixed(x: float, digits: int) -> str:
    """toFixed(digits), refusing a value that sits on a rounding edge.

    emit_jsgame._fixed rounds exactly as toFixed does; this adds the
    refusal, for a next digit of 5 (or a hair either side of one), and for
    a small negative number that would print as -0.0.
    """
    scaled = Fraction(x) * 10**digits
    if abs(scaled - math.floor(scaled) - Fraction(1, 2)) < _EDGE:
        raise ValueError(f"{x} sits on a rounding edge at {digits} places")
    shown = _fixed(x, digits)
    if x < 0 and Fraction(shown) == 0:
        raise ValueError(f"{x} would print as {shown}")
    return shown


def _round_to(x: float, step) -> str:
    """Math.round(x / step) * step, as console.log shows it."""
    return _kg(_js_round(x / step) * step)


def _int(x) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: a whole number here")
    return x


# ── 1. Training volume ───────────────────────────────────────


def _pairs(rows) -> str:
    """[[8, 60], [6, 80]]: an array of [reps, kg] pairs."""
    return "[" + ", ".join(f"[{_lit(r)}, {_lit(k)}]" for r, k in rows) + "]"


def _volume(a: dict) -> str:
    want = a["want"]
    if want == "straight":
        return _lines(
            f"const sets = {_lit(a['sets'])};",
            f"const reps = {_lit(a['reps'])};",
            f"const kg = {_lit(a['kg'])};",
            "console.log(sets * reps * kg);",
        )
    if want == "session":
        return _lines(
            f"const sets = {_pairs(a['sets'])};",
            "const volume = sets.reduce((total, [reps, kg]) => total + reps * kg, 0);",
            "console.log(volume);",
        )
    (s1, r1, k1), (s2, r2, k2) = a["a"], a["b"]
    return _lines(
        "const volume = (sets, reps, kg) => sets * reps * kg;",
        f"const a = volume({_lit(s1)}, {_lit(r1)}, {_lit(k1)});",
        f"const b = volume({_lit(s2)}, {_lit(r2)}, {_lit(k2)});",
        "console.log(a);",
        "console.log(b);",
        "console.log(b > a);",
    )


# ── 2. Calories from macros ──────────────────────────────────


def _macros(a: dict) -> str:
    want = a["want"]
    if want in ("total", "share"):
        head = [f"const protein = {_lit(a['protein'])};",
                f"const carbs = {_lit(a['carbs'])};",
                f"const fat = {_lit(a['fat'])};"]
        if want == "total":
            return _lines(*head, "console.log(protein * 4 + carbs * 4 + fat * 9);")
        return _lines(
            *head,
            "const total = protein * 4 + carbs * 4 + fat * 9;",
            "console.log(total);",
            "console.log(Math.round(protein * 4 / total * 100));",
        )
    if want == "target":
        return _lines(
            f"const bodyweight = {_lit(a['bodyweight'])};",
            f"const gramsPerKg = {_lit(a['per_kg'])};",
            "const grams = Math.round(bodyweight * gramsPerKg);",
            "console.log(grams);",
            "console.log(grams * 4);",
        )
    p, c, f = (_lit(x) for x in a["split"])
    return _lines(
        f"const calories = {_lit(a['calories'])};",
        f"const protein = Math.round(calories * {p} / 100 / 4);",
        f"const carbs = Math.round(calories * {c} / 100 / 4);",
        f"const fat = Math.round(calories * {f} / 100 / 9);",
        "console.log(protein, carbs, fat);",
    )


# ── 3. Rest timers and session time ──────────────────────────

_CLOCK = ('const clock = (s) => '
          '`${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;')


def _timer(a: dict) -> str:
    want = a["want"]
    if want == "clock":
        return _lines(
            f"const seconds = {_lit(a['seconds'])};",
            "const minutes = Math.floor(seconds / 60);",
            'const secs = String(seconds % 60).padStart(2, "0");',
            "console.log(`${minutes}:${secs}`);",
        )
    if want == "session":
        return _lines(
            f"const sets = {_lit(a['sets'])};",
            f"const work = {_lit(a['work'])};",
            f"const rest = {_lit(a['rest'])};",
            "const total = sets * work + (sets - 1) * rest;",
            "console.log(`${Math.floor(total / 60)}:"
            '${String(total % 60).padStart(2, "0")}`);',
        )
    return _lines(
        _CLOCK,
        f"for (let left = {_lit(a['rest'])}; left >= 0; left -= {_lit(a['step'])}) {{",
        "  console.log(clock(left));",
        "}",
    )


# ── 4. One-rep max ───────────────────────────────────────────

_EPLEY = "kg * (1 + reps / 30)"
_BRZYCKI = "kg * 36 / (37 - reps)"


def _onerm(a: dict) -> str:
    want = a["want"]
    if want in ("epley", "brzycki"):
        return _lines(
            f"const kg = {_lit(a['kg'])};",
            f"const reps = {_lit(a['reps'])};",
            f"const oneRepMax = {_EPLEY if want == 'epley' else _BRZYCKI};",
            "console.log(oneRepMax.toFixed(1));",
        )
    if want == "both":
        kg, reps = _lit(a["kg"]), _lit(a["reps"])
        return _lines(
            f"const epley = (kg, reps) => {_EPLEY};",
            f"const brzycki = (kg, reps) => {_BRZYCKI};",
            f"console.log(epley({kg}, {reps}).toFixed(1), "
            f"brzycki({kg}, {reps}).toFixed(1));",
        )
    return _lines(
        "function oneRepMax(kg, reps) {",
        "  if (reps === 1) return kg.toFixed(1);",
        '  if (reps > 10) return "too many reps";',
        f"  return ({_EPLEY}).toFixed(1);",
        "}",
        *(f"console.log(oneRepMax({_lit(kg)}, {_lit(reps)}));"
          for kg, reps in a["sets"]),
    )


# ── 5. Body composition ──────────────────────────────────────


def _bodycomp(a: dict) -> str:
    want = a["want"]
    head = [f"const weight = {_lit(a['weight'])};",
            f"const bodyFat = {_lit(a['fat'])};"]
    if want == "lean":
        return _lines(
            *head,
            "console.log((weight * bodyFat / 100).toFixed(1));",
            "console.log((weight * (1 - bodyFat / 100)).toFixed(1));",
        )
    if want == "cm":
        head.append(f"const height = {_lit(a['cm'])} / 100;")
    else:
        head.append(f"const height = {_lit(a['height'])};")
    if want == "normal":
        return _lines(
            *head,
            "const ffmi = weight * (1 - bodyFat / 100) / (height * height);",
            "console.log(ffmi.toFixed(1));",
            "console.log((ffmi + 6.1 * (1.8 - height)).toFixed(1));",
        )
    return _lines(
        *head,
        "const lean = weight * (1 - bodyFat / 100);",
        "console.log((lean / (height * height)).toFixed(1));",
    )


# ── 6. Working weights from percentages ──────────────────────

_ROUND_TO = "const roundTo = (kg) => Math.round(kg / 2.5) * 2.5;"


def _percent(a: dict) -> str:
    want, best = a["want"], _lit(a["max"])
    if want == "one":
        return _lines(
            f"const oneRepMax = {best};",
            f"const percent = {_lit(a['percent'])};",
            "const weight = oneRepMax * percent / 100;",
            "console.log(Math.round(weight / 2.5) * 2.5);",
        )
    if want == "raw":
        return _lines(
            f"const oneRepMax = {best};",
            f"const weight = oneRepMax * {_lit(a['percent'])} / 100;",
            "console.log(weight.toFixed(2));",
            "console.log(Math.round(weight / 2.5) * 2.5);",
        )
    if want == "ramp":
        return _lines(
            f"const oneRepMax = {best};",
            _ROUND_TO,
            f"for (const percent of [{', '.join(_lit(p) for p in a['percents'])}]) {{",
            "  console.log(`${percent}% ${roundTo(oneRepMax * percent / 100)}`);",
            "}",
        )
    return _lines(
        f"const oneRepMax = {best};",
        f"const weight = oneRepMax * {_lit(a['percent'])} / 100;",
        "console.log(Math.round(weight / 5) * 5);",
    )


# ── 7. Progressive overload ──────────────────────────────────


def _overload(a: dict) -> str:
    want = a["want"]
    deload = f"roundTo(plan * {_lit(a['percent'] / 100)})"
    test = f"week % {_lit(a['every'])} === 0"
    start, step = _lit(a["start"]), _lit(a["step"])
    if want == "weeks":
        return _lines(
            _ROUND_TO,
            f"let plan = {start};",
            f"for (let week = 1; week <= {_lit(a['weeks'])}; week++) {{",
            f"  if ({test}) {{",
            f"    console.log({deload});",
            "  } else {",
            "    console.log(plan);",
            "  }",
            f"  plan += {step};",
            "}",
        )
    if want == "final":
        return _lines(
            _ROUND_TO,
            f"let plan = {start};",
            "let lifted = 0;",
            f"for (let week = 1; week <= {_lit(a['weeks'])}; week++) {{",
            f"  lifted = {test} ? {deload} : plan;",
            f"  plan += {step};",
            "}",
            "console.log(lifted);",
        )
    return _lines(
        _ROUND_TO,
        "let week = 1;",
        f"let plan = {start};",
        f"while (({test} ? {deload} : plan) < {_lit(a['goal'])}) {{",
        "  week++;",
        f"  plan += {step};",
        "}",
        "console.log(week);",
    )


# ── 8. Personal records ──────────────────────────────────────


def _log(rows) -> str:
    """[["squat", 100], ["bench", 70]]: an array of [lift, kg] pairs."""
    return "[" + ", ".join(f"[{_str(_word(n))}, {_lit(kg)}]" for n, kg in rows) + "]"


_BEST = (
    "const best = new Map();",
    "for (const [lift, kg] of log) {",
    "  if (!best.has(lift) || kg > best.get(lift)) best.set(lift, kg);",
    "}",
)


def _records(a: dict) -> str:
    want = a["want"]
    if want == "best":
        return _lines(
            f"const log = {_log(a['log'])};",
            *_BEST,
            "for (const [lift, kg] of best) console.log(`${lift} ${kg}`);",
        )
    if want == "order":
        ask = ", ".join(_str(_word(n)) for n in a["ask"])
        return _lines(
            f"const log = {_log(a['log'])};",
            *_BEST,
            f"for (const lift of [{ask}]) {{",
            '  console.log(`${lift} ${best.get(lift) ?? "none"}`);',
            "}",
        )
    return _lines(
        f"const best = new Map({_log(a['records'])});",
        f"const today = {_log(a['today'])};",
        "let broken = 0;",
        "for (const [lift, kg] of today) {",
        "  if (kg <= best.get(lift)) continue;",
        "  best.set(lift, kg);",
        "  broken++;",
        "  console.log(`${lift} ${kg}`);",
        "}",
        "console.log(`records broken: ${broken}`);",
    )


# ── 9. The weekly split ──────────────────────────────────────


def _week(days) -> str:
    """The split as one array literal of [day, groups] pairs."""
    return "[" + ", ".join(
        f"[{_str(day)}, [{', '.join(_str(_word(g)) for g in groups)}]]"
        for day, groups in days) + "]"


def _split(a: dict) -> str:
    want = a["want"]
    data = f"const split = {_week(a['days'])};"
    if want == "count":
        return _lines(
            data,
            "const counts = split.reduce((acc, [day, groups]) => {",
            "  for (const group of groups) acc[group] = (acc[group] ?? 0) + 1;",
            "  return acc;",
            "}, {});",
            "for (const [group, n] of Object.entries(counts)) "
            "console.log(`${group} ${n}`);",
        )
    if want == "rest":
        return _lines(
            data,
            "const rest = split.filter(([day, groups]) => groups.length === 0)"
            ".map(([day]) => day);",
            'console.log(rest.join(", "));',
            "console.log(split.length - rest.length);",
        )
    return _lines(
        data,
        "let twice = false;",
        "for (let i = 0; i < split.length; i++) {",
        "  const next = split[(i + 1) % split.length][1];",
        "  if (split[i][1].some((group) => next.includes(group))) twice = true;",
        "}",
        "console.log(twice);",
    )


# ── 10. Plate math ───────────────────────────────────────────


def _plates(a: dict) -> str:
    want = a["want"]
    bar, plates = (LB_BAR, LB_PLATES) if want == "lb" else (KG_BAR, KG_PLATES)
    lines = [
        f"const plates = [{', '.join(_lit(p) for p in plates)}];",
        f"let side = ({_lit(a['target'])} - {bar}) / 2;",
        "const load = [];",
        "for (const plate of plates) {",
        "  while (side >= plate) { load.push(plate); side -= plate; }",
        "}",
        'console.log(load.join(" "));',
    ]
    if want != "kg":
        lines.append('console.log(side === 0 ? "exact" : `${side} left over`);')
    return _lines(*lines)


_BUILDERS = {
    "js_lift_volume": _volume,
    "js_lift_macros": _macros,
    "js_lift_timer": _timer,
    "js_lift_onerm": _onerm,
    "js_lift_bodycomp": _bodycomp,
    "js_lift_percent": _percent,
    "js_lift_overload": _overload,
    "js_lift_records": _records,
    "js_lift_split": _split,
    "js_lift_plates": _plates,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────
#
# Each function below works the answer out from the arguments alone, in
# the same order of operations the formula is written in, so every double
# is the one node makes; the tests then run the reference program in node
# and hold it to this.


def _volume_out(a: dict) -> str:
    want = a["want"]
    if want == "straight":
        return _kg(a["sets"] * a["reps"] * a["kg"])
    if want == "session":
        if len(a["sets"]) < 2:
            raise ValueError("a session has two sets at least")
        total = 0
        for reps, kg in a["sets"]:
            total += reps * kg
        return _kg(total)
    (s1, r1, k1), (s2, r2, k2) = a["a"], a["b"]
    one, two = s1 * r1 * k1, s2 * r2 * k2
    return NL.join([_kg(one), _kg(two), _bool(two > one)])


def _macros_out(a: dict) -> str:
    want = a["want"]
    if want in ("total", "share"):
        p, c, f = _int(a["protein"]), _int(a["carbs"]), _int(a["fat"])
        total = p * 4 + c * 4 + f * 9
        if want == "total":
            return str(total)
        return NL.join([str(total), str(_js_round(p * 4 / total * 100))])
    if want == "target":
        if not 1 <= a["per_kg"] <= 2.5:
            raise ValueError("keep the protein target an ordinary one")
        grams = _js_round(_int(a["bodyweight"]) * a["per_kg"])
        return NL.join([str(grams), str(grams * 4)])
    p, c, f = (_int(x) for x in a["split"])
    if p + c + f != 100:
        raise ValueError("the three shares make 100 percent")
    kcal = _int(a["calories"])
    grams = (_js_round(kcal * p / 100 / 4), _js_round(kcal * c / 100 / 4),
             _js_round(kcal * f / 100 / 9))
    return " ".join(str(g) for g in grams)


def _clock(seconds: int) -> str:
    return f"{_int(seconds) // 60}:{seconds % 60:02d}"


def _timer_out(a: dict) -> str:
    want = a["want"]
    if want == "clock":
        return _clock(a["seconds"])
    if want == "session":
        sets = _int(a["sets"])
        if sets < 2:
            raise ValueError("one set has no rest to count")
        return _clock(sets * _int(a["work"]) + (sets - 1) * _int(a["rest"]))
    rest, step = _int(a["rest"]), _int(a["step"])
    if step <= 0 or rest % step or rest // step < 2:
        raise ValueError("the countdown lands on 0 after a few steps")
    return NL.join(_clock(left) for left in range(rest, -1, -step))


def _epley(kg, reps) -> float:
    return kg * (1 + reps / 30)


def _brzycki(kg, reps) -> float:
    return kg * 36 / (37 - reps)


def _onerm_out(a: dict) -> str:
    want = a["want"]
    if want != "guard":
        kg, reps = a["kg"], _int(a["reps"])
        if not 2 <= reps <= 10:
            raise ValueError(f"{reps} reps: the formulas are for 2 to 10")
        if want == "epley":
            return _to_fixed(_epley(kg, reps), 1)
        if want == "brzycki":
            return _to_fixed(_brzycki(kg, reps), 1)
        return (f"{_to_fixed(_epley(kg, reps), 1)} "
                f"{_to_fixed(_brzycki(kg, reps), 1)}")
    out = []
    for kg, reps in a["sets"]:
        if _int(reps) < 1:
            raise ValueError("a set has one rep at least")
        if reps == 1:
            out.append(_to_fixed(kg, 1))
        elif reps > 10:
            out.append("too many reps")
        else:
            out.append(_to_fixed(_epley(kg, reps), 1))
    if len(out) < 2:
        raise ValueError("two calls at least")
    return NL.join(out)


def _bodycomp_out(a: dict) -> str:
    want, w, bf = a["want"], a["weight"], a["fat"]
    if not 5 <= bf <= 35:
        raise ValueError("an everyday body-fat percentage")
    if want == "lean":
        return NL.join([_to_fixed(w * bf / 100, 1),
                        _to_fixed(w * (1 - bf / 100), 1)])
    h = a["cm"] / 100 if want == "cm" else a["height"]
    if not 1.5 <= h <= 2.1:
        raise ValueError("a height in metres")
    if want == "normal":
        ffmi = w * (1 - bf / 100) / (h * h)
        return NL.join([_to_fixed(ffmi, 1),
                        _to_fixed(ffmi + 6.1 * (1.8 - h), 1)])
    lean = w * (1 - bf / 100)
    return _to_fixed(lean / (h * h), 1)


def _percent_out(a: dict) -> str:
    want, best = a["want"], a["max"]
    if want == "ramp":
        return NL.join(f"{_int(p)}% {_round_to(best * p / 100, 2.5)}"
                       for p in a["percents"])
    weight = best * _int(a["percent"]) / 100
    if want == "one":
        return _round_to(weight, 2.5)
    if want == "raw":
        return NL.join([_to_fixed(weight, 2), _round_to(weight, 2.5)])
    return _round_to(weight, 5)


def _lifted(a: dict, week: int, plan) -> float:
    """What a week lifts: the plan, or a deload rounded to 2.5 kg."""
    if week % a["every"] == 0:
        return _js_round(plan * (a["percent"] / 100) / 2.5) * 2.5
    return plan


def _overload_out(a: dict) -> str:
    want = a["want"]
    if not 2 <= _int(a["every"]) or not 50 < _int(a["percent"]) < 100:
        raise ValueError("a deload every few weeks, lighter but not empty")
    if a["step"] <= 0:
        raise ValueError("the plan climbs")
    if want in ("weeks", "final"):
        weeks = _int(a["weeks"])
        if weeks < a["every"]:
            raise ValueError("the plan reaches a deload week at least once")
        plan, lifted = a["start"], []
        for week in range(1, weeks + 1):
            lifted.append(_lifted(a, week, plan))
            plan += a["step"]
        if want == "final":
            return _kg(lifted[-1])
        return NL.join(_kg(x) for x in lifted)
    if a["goal"] <= a["start"]:
        raise ValueError("a goal above where the plan starts")
    week, plan = 1, a["start"]
    while _lifted(a, week, plan) < a["goal"]:
        week += 1
        plan += a["step"]
        if week > 100:
            raise ValueError("a goal the plan reaches")
    return str(week)


def _records_out(a: dict) -> str:
    want = a["want"]
    if want == "new":
        best = {_word(lift): kg for lift, kg in a["records"]}
        if len(best) != len(a["records"]):
            raise ValueError("one record per lift")
        out = []
        for lift, kg in a["today"]:
            if lift not in best:
                raise ValueError(f"{lift} has no record to beat")
            if kg > best[lift]:
                best[lift] = kg
                out.append(f"{lift} {_kg(kg)}")
        return NL.join(out + [f"records broken: {len(out)}"])
    best = {}
    for lift, kg in a["log"]:
        if _word(lift) not in best or kg > best[lift]:
            best[lift] = kg
    if want == "best":
        return NL.join(f"{lift} {_kg(kg)}" for lift, kg in best.items())
    return NL.join(f"{lift} {_kg(best[lift]) if lift in best else 'none'}"
                   for lift in a["ask"])


def _split_out(a: dict) -> str:
    days = a["days"]
    if tuple(day for day, _ in days) != DAYS:
        raise ValueError("a split is the seven days, Mon to Sun, in order")
    for day, groups in days:
        if len(set(groups)) != len(groups):
            raise ValueError(f"{day} lists a group twice")
        for group in groups:
            _word(group)
    want = a["want"]
    if want == "count":
        counts: dict[str, int] = {}
        for _, groups in days:
            for group in groups:
                counts[group] = counts.get(group, 0) + 1
        return NL.join(f"{group} {n}" for group, n in counts.items())
    if want == "rest":
        rest = [day for day, groups in days if not groups]
        if not rest or len(rest) == len(days):
            raise ValueError("some rest days and some training days")
        return NL.join([", ".join(rest), str(len(days) - len(rest))])
    twice = any(set(days[i][1]) & set(days[(i + 1) % len(days)][1])
                for i in range(len(days)))
    return _bool(twice)


def _plates_out(a: dict) -> str:
    want, target = a["want"], a["target"]
    bar, plates = (LB_BAR, LB_PLATES) if want == "lb" else (KG_BAR, KG_PLATES)
    if (Fraction(target) * 2).denominator != 1:
        raise ValueError("a target in whole or half units")
    side = (Fraction(target) - bar) / 2
    load = []
    for plate in plates:
        while side >= plate:
            load.append(plate)
            side -= Fraction(plate)
    if not load:
        raise ValueError("no plate fits, and an empty line teaches nothing")
    shown = " ".join(_kg(p) for p in load)
    if want == "kg":
        if side:
            raise ValueError("the plain rows load exactly")
        return shown
    return NL.join([shown, "exact" if side == 0 else f"{_kg(side)} left over"])


_ORACLES = {
    "js_lift_volume": _volume_out,
    "js_lift_macros": _macros_out,
    "js_lift_timer": _timer_out,
    "js_lift_onerm": _onerm_out,
    "js_lift_bodycomp": _bodycomp_out,
    "js_lift_percent": _percent_out,
    "js_lift_overload": _overload_out,
    "js_lift_records": _records_out,
    "js_lift_split": _split_out,
    "js_lift_plates": _plates_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    if shape not in _ORACLES:
        raise KeyError(shape)
    return _ORACLES[shape](args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_lift_volume": Cost(
        "O(n)",
        "Straight sets are constant: two multiplications, however heavy. A "
        "whole session is linear in its number of sets, n: reduce visits "
        "each [reps, kg] pair once and carries a single running total."),
    "js_lift_macros": Cost(
        "O(1)",
        "Constant: three multiplications, two additions and a division, "
        "whatever the numbers are. Math.round runs once, at the end, which "
        "is also where it does the least harm."),
    "js_lift_timer": Cost(
        "O(n)",
        "Formatting one time is constant: a division, a remainder and a "
        "pad. A countdown prints one line per beep, rest / step of them, so "
        "it is linear in that count, with constant work per line."),
    "js_lift_onerm": Cost(
        "O(1)",
        "Constant: a division, an addition and a multiplication per "
        "estimate. The guard clauses cost one comparison each and return "
        "before any arithmetic is done for the cases they turn away."),
    "js_lift_bodycomp": Cost(
        "O(1)",
        "Constant: a handful of multiplications and divisions. Squaring the "
        "height as height * height costs one multiplication, the same as "
        "any other step."),
    "js_lift_percent": Cost(
        "O(k)",
        "Constant per weight: a multiply, a divide, one Math.round and a "
        "multiply back. A ramp of k percentages is k of those, one per "
        "line."),
    "js_lift_overload": Cost(
        "O(n)",
        "Linear in the number of weeks, n: one addition, one remainder test "
        "and at most one rounding per week. Any single week's plan could "
        "be worked out directly as start + (week - 1) * step; the loop is "
        "for when every week is wanted, or the first week that reaches a "
        "goal."),
    "js_lift_records": Cost(
        "O(n)",
        "Linear in the length of the log, n. A Map's has, get and set take "
        "about the same time however many lifts it holds, so each set costs "
        "a constant amount. Searching an array of records for every set "
        "would cost n times the number of lifts instead."),
    "js_lift_split": Cost(
        "O(n)",
        "Linear in the entries, every group on every day: reduce and filter "
        "each visit them once. The two-days-running check compares each day "
        "with the next, a few groups against a few with includes - tiny for "
        "a week, and a Set per day would make each lookup constant."),
    "js_lift_plates": Cost(
        "O(p + k)",
        "Linear in the plate sizes, p, plus the plates loaded, k: the for "
        "visits each size once and every turn of the while puts one plate "
        "on. Greedy never takes a plate back off, which is why it is quick, "
        "and with these plates it still finds an exact load whenever there "
        "is one, because every size is a whole number of the smallest."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
