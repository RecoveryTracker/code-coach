"""JavaScript: the planets.

Ten pages of space arithmetic, each one a short program that runs in plain
node with no DOM: weight on other worlds, conversions and scale models, how
long light takes, an age in other planets' years, Kepler's third law, where
a planet is in its orbit, escape velocity and orbital speed, and then the
planets as an array of objects to filter, sort and print as a lined-up
table.

The facts arrive in the arguments: the content module keeps NASA's numbers
and every prompt states the ones it needs, so this module only does the
arithmetic. The few constants that every page shares are kept here as the
text the program types, so the prompt, the program and the oracle all read
the very same digits.

The oracle never runs the JavaScript. It works each answer out in Python,
doing the same operations in the same order so the doubles come out
identical, and the tests then hold node to it. Anything that is not a whole
number is printed with toFixed, which emit_jsgame._fixed models exactly. A
learner may well divide before multiplying, which can move the last bit of
a double; that only changes what prints when the answer sits right on a
rounding edge, so rows that do are refused here, and every exercise prints
the same whichever order its arithmetic is done in.
"""

from __future__ import annotations

import math
from decimal import Decimal

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines
from code_coach.workbook.emit_jsgame import _bool, _fixed, _lit, _num

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_planets_weight", "weight as mass times a world's gravity"),
    Shape("js_planets_units", "converting units and shrinking to a scale model"),
    Shape("js_planets_light", "how long light takes, in minutes and seconds"),
    Shape("js_planets_age", "an age counted in another planet's years"),
    Shape("js_planets_kepler", "a year worked out from a distance, by Kepler's third law"),
    Shape("js_planets_orbit", "how far round its orbit a planet is, and when two line up"),
    Shape("js_planets_escape", "escape velocity and orbital speed"),
    Shape("js_planets_filter", "filtering an array of planets and joining what is left"),
    Shape("js_planets_sort", "sorting planets, and reducing them to one value"),
    Shape("js_planets_table", "a table of planets lined up with padEnd and padStart"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── The constants, as the program writes them ────────────────

#: Earth's surface gravity in m/s², as NASA's fact sheet gives it.
EARTH_G = "9.8"
#: An Earth year in days, leap days included. (The fact sheet rounds
#: Earth's orbit to 365.2.)
EARTH_YEAR = "365.25"
#: One AU in millions of km: the fact sheet's distance from Earth to the Sun.
AU_MILLION_KM = "149.6"
#: One AU in km, exact by definition since 2012.
AU_KM = "149597870.7"
#: The speed of light in km per second, exact by definition.
LIGHT_KM_S = "299792.458"
#: A mile in km, exact by definition.
MILE_KM = "1.609344"
#: The Sun's diameter in km, twice NASA's mean radius of 695700 km.
SUN_KM = "1391400"
#: The Sun's mass in kg, from NASA's Sun fact sheet.
SUN_MASS = "1.9884e30"
#: The gravitational constant, in m³ per kg per s².
G = "6.674e-11"

#: The unit printed after a value in a label.
UNITS: dict[str, str] = {"au": "AU", "km": "km", "day": "h"}

#: What reduce keeps when it looks for the top or the bottom of a field,
#: and so what the answer's variable is called.
BEST: dict[tuple[str, str], str] = {
    ("max", "km"): "biggest", ("min", "km"): "smallest",
    ("max", "day"): "longest", ("min", "day"): "shortest",
    ("max", "gravity"): "strongest", ("min", "gravity"): "weakest",
    ("max", "temp"): "hottest", ("min", "temp"): "coldest",
    ("max", "au"): "farthest", ("min", "au"): "closest",
    ("max", "mass"): "heaviest", ("min", "mass"): "lightest",
}


# ── Writing numbers and names ────────────────────────────────


def _code(x) -> str:
    """A number literal. A whole float such as 228.0 is written 228."""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return _lit(x)


def _sci(mass) -> str:
    """A mass given as (digits, power of ten), written as 6.42e23."""
    digits, power = mass
    if not 1 <= digits < 10 or isinstance(power, bool) or not isinstance(power, int):
        raise ValueError(f"{mass}: masses are written like 6.42e23")
    return f"{_code(digits)}e{power}"


def _name(s: str) -> str:
    """A planet's name as a string literal."""
    if not s.replace(" ", "").isalpha():
        raise ValueError(f"{s!r}: names are plain words")
    return f'"{s}"'


def _word(s: str) -> str:
    """A lowercase word used to start a variable name: rover, probe."""
    if not (s.isalpha() and s.islower()):
        raise ValueError(f"{s!r}: one lowercase word")
    return s


def _stem(body: str) -> str:
    """The start of a variable name for a body: Mars is mars, the Moon is moon."""
    word = body.removeprefix("the ").split()[0].removesuffix("'s")
    if not word.isalpha():
        raise ValueError(f"{body!r} makes no variable name")
    return word[0].lower() + word[1:]


def _val(v) -> str:
    return _bool(v) if isinstance(v, bool) else _code(v)


def _items(rows, size: int) -> list[tuple]:
    """The planets of a data page: (name, value, ...), checked."""
    items = [tuple(r) for r in rows]
    names = [r[0] for r in items]
    if len(items) < 3:
        raise ValueError("three planets at least, or it is hardly data")
    if len(set(names)) != len(names):
        raise ValueError("names must be unique, or the output is ambiguous")
    if any(len(r) != size for r in items):
        raise ValueError("every planet needs every field")
    return items


def _data(rows, *fields: str) -> list[str]:
    """const planets = [ { name: "Mars", au: 1.524 }, ... ];"""
    lines = []
    for name, *values in _items(rows, len(fields) + 1):
        body = ", ".join(f"{f}: {_val(v)}" for f, v in zip(fields, values))
        lines.append(f"  {{ name: {_name(name)}, {body} }},")
    return ["const planets = [", *lines, "];"]


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


def _floor(x: float) -> int:
    """Math.floor of a computed value, refused a hair from a whole number."""
    near = round(x)
    if abs(x - near) < _TOO_CLOSE * max(1.0, abs(x)):
        raise ValueError(f"{x} is too near {near} to round down safely")
    return math.floor(x)


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


# ── 1. Weight ────────────────────────────────────────────────


def _weight(a: dict) -> str:
    want = a["want"]
    if want == "newtons":
        return _lines(
            f"const mass = {_code(a['mass'])};",
            f"const gravity = {_code(a['g'])};",
            "const weight = mass * gravity;",
            "console.log(weight.toFixed(1));",
        )
    if want == "heavier":
        (t1, m1, _, g1), (t2, m2, _, g2) = a["one"], a["two"]
        w1, w2 = f"{_word(t1)}Weight", f"{_word(t2)}Weight"
        return _lines(
            f"const {w1} = {_code(m1)} * {_code(g1)};",
            f"const {w2} = {_code(m2)} * {_code(g2)};",
            f"console.log({w1}.toFixed(1));",
            f"console.log({w2}.toFixed(1));",
            f"console.log({w1} > {w2});",
        )
    s = _stem(a["body"])
    if s == "earth":
        raise ValueError("compare Earth with somewhere else")
    if want == "scale":
        return _lines(
            f"const earthReading = {_code(a['reading'])};",
            f"const earthGravity = {EARTH_G};",
            f"const {s}Gravity = {_code(a['g'])};",
            f"const {s}Reading = earthReading * {s}Gravity / earthGravity;",
            f"console.log({s}Reading.toFixed(1));",
        )
    if want == "jump":
        return _lines(
            f"const earthJump = {_code(a['height'])};",
            f"const earthGravity = {EARTH_G};",
            f"const {s}Gravity = {_code(a['g'])};",
            f"const {s}Jump = earthJump * earthGravity / {s}Gravity;",
            f"console.log({s}Jump.toFixed(2));",
        )
    raise ValueError(want)


def _weight_out(a: dict) -> str:
    want = a["want"]
    if want == "newtons":
        return _shown(a["mass"] * a["g"], 1)
    if want == "scale":
        return _shown(a["reading"] * a["g"] / float(EARTH_G), 1)
    if want == "jump":
        return _shown(a["height"] * float(EARTH_G) / a["g"], 2)
    if want == "heavier":
        (t1, m1, _, g1), (t2, m2, _, g2) = a["one"], a["two"]
        if t1 == t2:
            raise ValueError("two different things, or the names clash")
        w1, w2 = m1 * g1, m2 * g2
        if abs(w1 - w2) < _TOO_CLOSE * max(w1, w2):
            raise ValueError("too close to call which weighs more")
        return NL.join([_shown(w1, 1), _shown(w2, 1), _bool(w1 > w2)])
    raise ValueError(want)


# ── 2. Conversions and scale models ──────────────────────────


def _km(million) -> int:
    """Millions of km as a whole number of km: 149.6 is 149600000."""
    km = Decimal(repr(million)) * 1_000_000
    if km != km.to_integral_value():
        raise ValueError(f"{million} million km is not a whole number of km")
    return int(km)


def _units(a: dict) -> str:
    want = a["want"]
    if want == "miles":
        return _lines(
            f"const kmPerMile = {MILE_KM};",
            f"const millionKm = {_code(a['d'])};",
            "const millionMiles = millionKm / kmPerMile;",
            "console.log(millionMiles.toFixed(1));",
        )
    if want == "au":
        return _lines(
            f"const millionKm = {_code(a['d'])};",
            f"const au = millionKm / {AU_MILLION_KM};",
            "console.log(au.toFixed(2));",
        )
    if want == "model":
        return _lines(
            f"const sunKm = {SUN_KM};",
            f"const ballCm = {_code(a['ball'])};",
            f"const distanceKm = {_km(a['d'])};",
            "const metres = distanceKm * ballCm / sunKm / 100;",
            "console.log(metres.toFixed(1));",
        )
    if want == "temp":
        return _lines(
            f"const celsius = {_code(a['c'])};",
            "const fahrenheit = celsius * 9 / 5 + 32;",
            "console.log(fahrenheit.toFixed(1));",
        )
    raise ValueError(want)


def _units_out(a: dict) -> str:
    want = a["want"]
    if want == "miles":
        return _shown(a["d"] / float(MILE_KM), 1)
    if want == "au":
        return _shown(a["d"] / float(AU_MILLION_KM), 2)
    if want == "model":
        return _shown(_km(a["d"]) * a["ball"] / int(SUN_KM) / 100, 1)
    if want == "temp":
        return _shown(a["c"] * 9 / 5 + 32, 1)
    raise ValueError(want)


# ── 3. How long light takes ──────────────────────────────────


def _trip(a: dict) -> str:
    km = _code(a["km"])
    return f"2 * {km}" if a.get("both") else km


def _light(a: dict) -> str:
    want = a["want"]
    if want == "seconds":
        return _lines(
            f"const km = {_trip(a)};",
            f"const seconds = km / {LIGHT_KM_S};",
            "console.log(seconds.toFixed(1));",
        )
    if want == "minsec":
        return _lines(
            f"const km = {_trip(a)};",
            f"const total = Math.floor(km / {LIGHT_KM_S});",
            "const minutes = Math.floor(total / 60);",
            "console.log(`${minutes} min ${total % 60} s`);",
        )
    if want == "au":
        return _lines(
            f"const au = {_code(a['au'])};",
            f"const km = au * {AU_KM};",
            f"const total = Math.floor(km / {LIGHT_KM_S});",
            "console.log(`${Math.floor(total / 60)} min ${total % 60} s`);",
        )
    if want == "hms":
        return _lines(
            f"const km = {_trip(a)};",
            f"const total = Math.floor(km / {LIGHT_KM_S});",
            "const hours = Math.floor(total / 3600);",
            "const minutes = Math.floor((total % 3600) / 60);",
            "console.log(`${hours} h ${minutes} min ${total % 60} s`);",
        )
    raise ValueError(want)


def _light_out(a: dict) -> str:
    want = a["want"]
    if want == "au":
        seconds = a["au"] * float(AU_KM) / float(LIGHT_KM_S)
    else:
        if not isinstance(a["km"], int):
            raise ValueError("a distance in whole km")
        seconds = a["km"] * (2 if a.get("both") else 1) / float(LIGHT_KM_S)
    if want == "seconds":
        return _shown(seconds, 1)
    total = _floor(seconds)
    if want in ("minsec", "au"):
        if total >= 3600:
            raise ValueError("an hour or more belongs on the hours rows")
        return f"{total // 60} min {total % 60} s"
    if want == "hms":
        if total < 3600:
            raise ValueError("under an hour belongs on the minutes rows")
        return f"{total // 3600} h {total % 3600 // 60} min {total % 60} s"
    raise ValueError(want)


# ── 4. An age in another planet's years ──────────────────────


def _age(a: dict) -> str:
    want = a["want"]
    s = _stem(a["body"])
    if s == "earth":
        raise ValueError("an age in Earth years is just the age")
    year = f"const {s}Year = {_code(a['year'])};"
    if want == "age":
        return _lines(
            f"const age = {_code(a['age'])};",
            f"const days = age * {EARTH_YEAR};",
            year,
            f"const {s}Age = days / {s}Year;",
            f"console.log({s}Age.toFixed(2));",
        )
    if want == "birthdays":
        return _lines(
            f"const age = {_code(a['age'])};",
            f"const days = age * {EARTH_YEAR};",
            year,
            f"console.log(Math.floor(days / {s}Year));",
        )
    if want == "next":
        return _lines(
            f"const daysAlive = {_code(a['days'])};",
            year,
            f"console.log(Math.floor(daysAlive / {s}Year));",
            f"console.log({s}Year - (daysAlive % {s}Year));",
        )
    if want == "back":
        return _lines(
            f"const {s}Age = {_code(a['n'])};",
            year,
            f"const earthAge = {s}Age * {s}Year / {EARTH_YEAR};",
            "console.log(earthAge.toFixed(2));",
        )
    raise ValueError(want)


def _age_out(a: dict) -> str:
    want, year = a["want"], a["year"]
    if want == "age":
        return _shown(a["age"] * float(EARTH_YEAR) / year, 2)
    if want == "birthdays":
        return str(_floor(a["age"] * float(EARTH_YEAR) / year))
    if want == "next":
        days = a["days"]
        if not (isinstance(days, int) and isinstance(year, int)):
            raise ValueError("whole days only, so the remainder is exact")
        left = days % year
        if left == 0:
            raise ValueError("today is the birthday, so 'until the next' is unclear")
        return NL.join([str(days // year), str(year - left)])
    if want == "back":
        return _shown(a["n"] * year / float(EARTH_YEAR), 2)
    raise ValueError(want)


# ── 5. Kepler's third law ────────────────────────────────────


def _kepler(a: dict) -> str:
    want = a["want"]
    if want == "ratio":
        (b1, a1), (b2, a2) = a["one"], a["two"]
        x1, x2 = _code(a1), _code(a2)
        y1, y2 = f"{_stem(b1)}Year", f"{_stem(b2)}Year"
        return _lines(
            f"const {y1} = Math.sqrt({x1} * {x1} * {x1});",
            f"const {y2} = Math.sqrt({x2} * {x2} * {x2});",
            f"console.log(({y1} / {y2}).toFixed(2));",
        )
    if want == "km":
        first = f"const a = {_code(a['d'])} / {AU_MILLION_KM};"
    elif want in ("years", "days"):
        first = f"const a = {_code(a['au'])};"
    else:
        raise ValueError(want)
    shown = (f"Math.round(years * {EARTH_YEAR})" if want == "days"
             else "years.toFixed(2)")
    return _lines(
        first,
        "const years = Math.sqrt(a * a * a);",
        f"console.log({shown});",
    )


def _kepler_year(au: float) -> float:
    return math.sqrt(au * au * au)


def _kepler_out(a: dict) -> str:
    want = a["want"]
    if want == "ratio":
        (b1, a1), (b2, a2) = a["one"], a["two"]
        if a1 <= a2 or b1 == b2:
            raise ValueError("the farther body first, so its year is the longer")
        return _shown(_kepler_year(a1) / _kepler_year(a2), 2)
    if want == "km":
        years = _kepler_year(a["d"] / float(AU_MILLION_KM))
    elif want in ("years", "days"):
        years = _kepler_year(a["au"])
    else:
        raise ValueError(want)
    if want == "days":
        return str(_round(years * float(EARTH_YEAR)))
    return _shown(years, 2)


# ── 6. Where in the orbit ────────────────────────────────────


def _orbit(a: dict) -> str:
    want = a["want"]
    if want == "synodic":
        (b1, t1), (b2, t2) = a["one"], a["two"]
        y1, y2 = f"{_stem(b1)}Year", f"{_stem(b2)}Year"
        return _lines(
            f"const {y1} = {_code(t1)};",
            f"const {y2} = {_code(t2)};",
            f"const synodic = 1 / Math.abs(1 / {y1} - 1 / {y2});",
            "console.log(Math.round(synodic));",
        )
    year = f"{_stem(a['body'])}Year"
    head = [f"const {year} = {_code(a['year'])};",
            f"const days = {_code(a['days'])};"]
    if want == "angle":
        return _lines(
            *head,
            f"const angle = (360 * days / {year}) % 360;",
            "console.log(angle.toFixed(1));",
        )
    if want == "laps":
        return _lines(
            *head,
            f"console.log(Math.floor(days / {year}));",
            f"console.log(((360 * days / {year}) % 360).toFixed(1));",
        )
    raise ValueError(want)


def _orbit_out(a: dict) -> str:
    want = a["want"]
    if want == "synodic":
        (b1, t1), (b2, t2) = a["one"], a["two"]
        if t1 == t2 or b1 == b2:
            raise ValueError("two different years, or they never line up")
        return str(_round(1 / abs(1 / t1 - 1 / t2)))
    if want not in ("angle", "laps"):
        raise ValueError(want)
    days, year = a["days"], a["year"]
    whole = 360 * days / year
    angle = math.fmod(whole, 360)  # JavaScript's % on doubles, exactly
    if min(angle, 360 - angle) < _TOO_CLOSE * max(1.0, whole):
        raise ValueError("too near a whole number of orbits")
    shown = _shown(angle, 1)
    if shown in ("0.0", "360.0"):
        raise ValueError("an angle that prints as a whole lap")
    if want == "angle":
        return shown
    laps = _floor(days / year)
    if laps < 1:
        raise ValueError("one whole orbit at least")
    return NL.join([str(laps), shown])


# ── 7. Escape velocity and orbital speed ─────────────────────


def _escape(a: dict) -> str:
    want = a["want"]
    if want == "escape":
        return _lines(
            f"const G = {G};",
            f"const mass = {_sci(a['mass'])};",
            f"const radius = ({_code(a['km'])} / 2) * 1000;",
            "const escapeSpeed = Math.sqrt(2 * G * mass / radius);",
            "console.log((escapeSpeed / 1000).toFixed(2));",
        )
    if want == "sun":
        return _lines(
            f"const G = {G};",
            f"const sunMass = {SUN_MASS};",
            f"const r = {_code(a['d'])}e9;",
            "const speed = Math.sqrt(G * sunMass / r);",
            "console.log((speed / 1000).toFixed(1));",
        )
    if want == "satellite":
        return _lines(
            f"const G = {G};",
            f"const mass = {_sci(a['mass'])};",
            f"const r = ({_code(a['km'])} / 2 + {_code(a['height'])}) * 1000;",
            "const speed = Math.sqrt(G * mass / r);",
            "console.log((speed / 1000).toFixed(2));",
            "console.log((2 * Math.PI * r / speed / 60).toFixed(1));",
        )
    raise ValueError(want)


def _escape_out(a: dict) -> str:
    want, g = a["want"], float(G)
    if want == "escape":
        mass = float(_sci(a["mass"]))
        radius = (a["km"] / 2) * 1000
        return _shown(math.sqrt(2 * g * mass / radius) / 1000, 2)
    if want == "sun":
        r = float(f"{_code(a['d'])}e9")
        return _shown(math.sqrt(g * float(SUN_MASS) / r) / 1000, 1)
    if want == "satellite":
        mass = float(_sci(a["mass"]))
        r = (a["km"] / 2 + a["height"]) * 1000
        speed = math.sqrt(g * mass / r)
        return NL.join([_shown(speed / 1000, 2),
                        _shown(2 * math.pi * r / speed / 60, 1)])
    raise ValueError(want)


# ── 8. Filter, map and join ──────────────────────────────────


def _test(field: str, op: str, limit) -> str:
    """The arrow function's body: p.au > 5, or p.rings."""
    if field == "rings":
        if op not in ("is", "not"):
            raise ValueError(op)
        return "p.rings" if op == "is" else "!p.rings"
    if op not in (">", "<"):
        raise ValueError(op)
    return f"p.{field} {op} {_code(limit)}"


def _filter(a: dict) -> str:
    want, f = a["want"], a["field"]
    test = _test(f, a["op"], a.get("limit"))
    data = _data(a["items"], f)
    if want == "names":
        return _lines(
            *data,
            f"const names = planets.filter((p) => {test}).map((p) => p.name);",
            'console.log(names.join(", "));',
        )
    if want == "count":
        return _lines(
            *data,
            f"const count = planets.filter((p) => {test}).length;",
            "console.log(count);",
        )
    if want == "label":
        label = f"`${{p.name}} ${{p.{f}}} {UNITS[f]}`"
        return _lines(
            *data,
            f"const labels = planets.filter((p) => {test}).map((p) => {label});",
            'console.log(labels.join(", "));',
        )
    if want in ("some", "every"):
        return _lines(*data, f"console.log(planets.{want}((p) => {test}));")
    raise ValueError(want)


def _keep(value, field: str, op: str, limit) -> bool:
    if field == "rings":
        if not isinstance(value, bool):
            raise ValueError("rings is true or false")
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
        raise ValueError("the filter has to keep some planets and drop some")
    if want == "names":
        return ", ".join(n for n, _ in kept)
    if want == "count":
        return str(len(kept))
    if want == "label":
        return ", ".join(f"{n} {_num(v)} {UNITS[f]}" for n, v in kept)
    raise ValueError(want)


# ── 9. Sort and reduce ───────────────────────────────────────


def _sort(a: dict) -> str:
    want, f = a["want"], a["field"]
    data = _data(a["items"], f)
    if want in ("up", "down"):
        compare = f"a.{f} - b.{f}" if want == "up" else f"b.{f} - a.{f}"
        return _lines(
            *data,
            f"const sorted = [...planets].sort((a, b) => {compare});",
            'console.log(sorted.map((p) => p.name).join(", "));',
        )
    if want in ("max", "min"):
        best = BEST[(want, f)]
        op = ">" if want == "max" else "<"
        return _lines(
            *data,
            f"const {best} = planets.reduce((best, p) => (p.{f} {op} best.{f} ? p : best));",
            f"console.log(`${{{best}.name}} ${{{best}.{f}}}`);",
        )
    if want in ("total", "average"):
        shown = "total" if want == "total" else "(total / planets.length)"
        return _lines(
            *data,
            f"const total = planets.reduce((sum, p) => sum + p.{f}, 0);",
            f"console.log({shown}.toFixed({a['digits']}));",
        )
    raise ValueError(want)


def _sort_out(a: dict) -> str:
    want = a["want"]
    items = _items(a["items"], 2)
    values = [v for _, v in items]
    if want in ("up", "down", "max", "min") and len(set(values)) != len(values):
        raise ValueError("a tie makes the order depend on how the compare is written")
    if want in ("up", "down"):
        ordered = sorted(items, key=lambda item: item[1], reverse=want == "down")
        if ordered == items:
            raise ValueError("already in order, so sorting would show nothing")
        return ", ".join(n for n, _ in ordered)
    if want in ("max", "min"):
        name, value = (max if want == "max" else min)(items, key=lambda item: item[1])
        return f"{name} {_num(value)}"
    if want in ("total", "average"):
        # Added one at a time, left to right, as reduce does. Not sum():
        # since Python 3.12 that compensates for rounding, and JavaScript
        # does not.
        total = 0
        for v in values:
            total = total + v
        if want == "average":
            total = total / len(values)
        return _shown(total, a["digits"])
    raise ValueError(want)


# ── 10. A table that lines up ────────────────────────────────


def _cell(field: str, digits: int) -> str:
    """A number as a string: whole ones with String(), the rest with toFixed."""
    return f"String(p.{field})" if digits == 0 else f"p.{field}.toFixed({digits})"


def _table(a: dict) -> str:
    want, nw = a["want"], a["name_width"]
    if want == "three":
        (f1, d1, w1), (f2, d2, w2) = a["columns"]
        row = (f"`${{p.name.padEnd({nw})}} | ${{{_cell(f1, d1)}.padStart({w1})}}"
               f" | ${{{_cell(f2, d2)}.padStart({w2})}}`")
        return _lines(
            *_data(a["items"], f1, f2),
            "for (const p of planets) {",
            f"  console.log({row});",
            "}",
        )
    f, d, w = a["field"], a["digits"], a["width"]
    cell = f"${{{_cell(f, d)}.padStart({w})}}"
    if want == "numbered":
        return _lines(
            *_data(a["items"], f),
            "planets.forEach((p, i) => {",
            f"  console.log(`${{i + 1}}. ${{p.name.padEnd({nw})}}{cell}`);",
            "});",
        )
    head = []
    if want == "header":
        title = a["title"]
        if not title.isalpha():
            raise ValueError(f"{title!r}: one plain word")
        head = [f'console.log(`${{"Planet".padEnd({nw})}} | ${{"{title}".padStart({w})}}`);']
    elif want != "two":
        raise ValueError(want)
    return _lines(
        *_data(a["items"], f),
        *head,
        "for (const p of planets) {",
        f"  console.log(`${{p.name.padEnd({nw})}} | {cell}`);",
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


def _table_out(a: dict) -> str:
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
        rows.insert(0, f"{_name_out('Planet', nw)} | {title.rjust(w)}")
    elif want != "two":
        raise ValueError(want)
    return NL.join(rows)


_BUILDERS = {
    "js_planets_weight": _weight,
    "js_planets_units": _units,
    "js_planets_light": _light,
    "js_planets_age": _age,
    "js_planets_kepler": _kepler,
    "js_planets_orbit": _orbit,
    "js_planets_escape": _escape,
    "js_planets_filter": _filter,
    "js_planets_sort": _sort,
    "js_planets_table": _table,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "js_planets_weight": _weight_out,
    "js_planets_units": _units_out,
    "js_planets_light": _light_out,
    "js_planets_age": _age_out,
    "js_planets_kepler": _kepler_out,
    "js_planets_orbit": _orbit_out,
    "js_planets_escape": _escape_out,
    "js_planets_filter": _filter_out,
    "js_planets_sort": _sort_out,
    "js_planets_table": _table_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_planets_weight": Cost(
        "O(1)",
        "Constant: a multiply, or a multiply and a divide, whichever world it "
        "is. A heavier rover or a stronger pull is a bigger number, not more "
        "work."),
    "js_planets_units": Cost(
        "O(1)",
        "Constant: one or two multiplies and divides per conversion. "
        "Converting a whole list of distances would be linear in its length, "
        "one conversion each."),
    "js_planets_light": Cost(
        "O(1)",
        "Constant: one division, a floor or two and a couple of remainders, "
        "however far the light goes. Counting the seconds off a minute at a "
        "time would take longer the farther away the planet is; % finds what "
        "is left over in one step."),
    "js_planets_age": Cost(
        "O(1)",
        "Constant: a multiply, a divide and a floor. Counting birthdays by "
        "adding one planet-year at a time until you pass your age would grow "
        "with the age; dividing jumps straight to the answer."),
    "js_planets_kepler": Cost(
        "O(1)",
        "Constant: two multiplies and one Math.sqrt, the same for Mercury as "
        "for a comet far beyond Neptune."),
    "js_planets_orbit": Cost(
        "O(1)",
        "Constant: a few multiplies and divides and one %. Taking 360 off the "
        "angle again and again until it fits would cost a step per lap; % "
        "does it in one step, however many laps there have been."),
    "js_planets_escape": Cost(
        "O(1)",
        "Constant: a handful of multiplies and divides and one square root. "
        "The enormous and tiny numbers cost nothing extra: a double holds "
        "6.674e-11 and 1.9884e30 in the same 8 bytes."),
    "js_planets_filter": Cost(
        "O(n)",
        "Linear in the number of planets, n: filter runs its test once per "
        "planet, map once per planet kept and join once per name. some stops "
        "at the first yes and every at the first no, so they can finish "
        "early, but at worst they look at all n."),
    "js_planets_sort": Cost(
        "O(n log n)",
        "Sorting n planets takes about n log n comparisons, a little more "
        "than one pass. reduce is a single pass of n steps, which is why the "
        "biggest is found with reduce rather than by sorting everything and "
        "taking the first."),
    "js_planets_table": Cost(
        "O(n)",
        "Linear in the number of planets, n: one line each. Padding a cell "
        "adds at most its width in spaces, a fixed amount per line, so twice "
        "the planets is twice the work."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
