"""Pages 218-227: JavaScript, the planets.

Space arithmetic, with the solar system as the flavour and the JavaScript as
the lesson. The first seven pages are formulas, each a step harder than the
one before: weight on other worlds, conversions and scale models, how long
light takes, an age in other planets' years, Kepler's third law, where a
planet is in its orbit, and escape velocity. The last three turn the
planets into an array of objects to filter, sort and print as a table that
lines up.

The facts are NASA's planetary fact sheet, rounded the way it rounds them,
and kept in the tables below so that every page agrees with every other.
Moon counts are left out on purpose: they change every year as new moons
are found. Every prompt states the numbers it needs, so nobody has to look
anything up.

Numbered after the async pages (208-217, content_jsasync), so this tuple has
to be registered after JSASYNC_PAGES for the book to stay in order.
"""

from __future__ import annotations

from decimal import Decimal

from code_coach.workbook import Exercise, Page
from code_coach.workbook.emit_jsplanets import (
    AU_KM,
    AU_MILLION_KM,
    EARTH_G,
    EARTH_YEAR,
    LIGHT_KM_S,
    MILE_KM,
    SUN_KM,
    SUN_MASS,
    G,
    _km,
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


# ── The facts ────────────────────────────────────────────────
#
# NASA's planetary fact sheet (nssdc.gsfc.nasa.gov/planetary/factsheet),
# rounded as it gives them. Whole numbers are written as ints, so a program
# says 228 where the sheet says 228.0.

#: Surface gravity, m/s². For the giant planets the sheet measures it where
#: the air pressure equals Earth's at sea level, near the cloud tops.
GRAVITY = {
    "Mercury": 3.7, "Venus": 8.9, "Earth": 9.8, "the Moon": 1.6, "Mars": 3.7,
    "Jupiter": 23.1, "Saturn": 9, "Uranus": 8.7, "Neptune": 11, "Pluto": 0.7,
}

#: Mean distance from the Sun, millions of km.
DISTANCE = {
    "Mercury": 57.9, "Venus": 108.2, "Earth": 149.6, "Mars": 228,
    "Jupiter": 778.5, "Saturn": 1432, "Uranus": 2867, "Neptune": 4515,
    "Pluto": 5906.4,
}

#: The same distances in AU: the sheet's figure over 149.6, to three places.
#: Ceres and Halley's Comet are not on the sheet; theirs are the usual
#: semi-major axes.
AU = {
    "Mercury": 0.387, "Venus": 0.723, "Earth": 1, "Mars": 1.524,
    "Ceres": 2.767, "Jupiter": 5.204, "Saturn": 9.572,
    "Halley's Comet": 17.834, "Uranus": 19.164, "Neptune": 30.18,
    "Pluto": 39.481,
}

#: A year, in Earth days. Earth's is the calendar year with its leap days,
#: 365.25, which the sheet rounds to 365.2.
YEAR = {
    "Mercury": 88, "Venus": 224.7, "Earth": 365.25, "Mars": 687,
    "Jupiter": 4331, "Saturn": 10747, "Uranus": 30589, "Neptune": 59800,
}

#: Diameter, km.
DIAMETER = {
    "Mercury": 4879, "Venus": 12104, "Earth": 12756, "the Moon": 3475,
    "Mars": 6792, "Jupiter": 142984, "Saturn": 120536, "Uranus": 51118,
    "Neptune": 49528,
}

#: A day, sunrise to sunrise, in hours.
DAY = {
    "Mercury": 4222.6, "Venus": 2802, "Earth": 24, "Mars": 24.7,
    "Jupiter": 9.9, "Saturn": 10.7, "Uranus": 17.2, "Neptune": 16.1,
}

#: Mean temperature, °C.
TEMP = {
    "Mercury": 167, "Venus": 464, "Earth": 15, "Mars": -65, "Jupiter": -110,
    "Saturn": -140, "Uranus": -195, "Neptune": -200,
}

#: Mass, in the sheet's units of 10²⁴ kg.
MASS = {
    "Mercury": 0.33, "Venus": 4.87, "Earth": 5.97, "the Moon": 0.073,
    "Mars": 0.642, "Jupiter": 1898, "Saturn": 568, "Uranus": 86.8,
    "Neptune": 102,
}

#: Whether it has a ring system.
RINGS = {
    "Mercury": False, "Venus": False, "Earth": False, "Mars": False,
    "Jupiter": True, "Saturn": True, "Uranus": True, "Neptune": True,
}

#: A field of the data pages: its table, how a prompt describes it, and
#: what a single value of it is called.
FIELDS = {
    "au": (AU, "its distance from the Sun in AU", "distance"),
    "km": (DIAMETER, "its diameter in km", "diameter"),
    "day": (DAY, "the length of its day in hours", "day length"),
    "gravity": (GRAVITY, "its surface gravity in m/s²", "gravity"),
    "temp": (TEMP, "its mean temperature in °C", "mean temperature"),
    "rings": (RINGS, "whether it has rings, true or false,", "rings"),
    "mass": (MASS, "its mass in units of 10²⁴ kg", "mass"),
}


# ── Saying things ────────────────────────────────────────────


def _say(x) -> str:
    """A value as a prompt writes it: 3.7, 228, -65, true."""
    if isinstance(x, bool):
        return "true" if x else "false"
    return repr(x) if isinstance(x, float) else str(x)


def _one(x) -> str:
    """One decimal place, the way the sheet prints it: 228.0, 9.0."""
    return f"{x:.1f}"


def _cap(s: str) -> str:
    return s[0].upper() + s[1:]


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _places(digits: int) -> str:
    return {0: "as a whole number", 1: "to one decimal place",
            2: "to two decimal places"}[digits]


def _fact(field: str, name: str):
    return FIELDS[field][0][name]


def _array(field: str, names) -> tuple[str, tuple]:
    """The prompt's description of a one-field array, and the items."""
    _, describe, _ = FIELDS[field]
    items = tuple((n, _fact(field, n)) for n in names)
    listing = _and(f"{n} {_say(v)}" for n, v in items)
    return (f"Make an array of planet objects, each with a name and "
            f"{describe} as {field}: {listing}.", items)


# ── 218. Weight on other worlds ──────────────────────────────

_WEIGHTS = (
    ("newtons", "astronaut", 70, "stands on", "Mars"),
    ("newtons", "astronaut", 70, "stands on", "the Moon"),
    ("newtons", "rover", 1025, "drives on", "Mars"),
    ("newtons", "lander", 120, "sits on", "Mercury"),
    ("newtons", "probe", 340, "floats in the clouds of", "Jupiter"),
    ("newtons", "camera", 15, "sits on", "Venus"),
    ("scale", 64, "the Moon"),
    ("scale", 75, "Mars"),
    ("scale", 80, "Jupiter"),
    ("scale", 45, "Pluto"),
    ("scale", 90, "Neptune"),
    ("scale", 55, "Venus"),
    ("jump", 0.4, "the Moon"),
    ("jump", 0.5, "Mars"),
    ("jump", 0.6, "Pluto"),
    ("jump", 0.45, "Mercury"),
    ("heavier", ("rover", 900, "Mars"), ("probe", 400, "Earth")),
    ("heavier", ("lander", 600, "the Moon"), ("drone", 95, "Earth")),
    ("heavier", ("crate", 200, "Jupiter"), ("sled", 480, "Earth")),
    ("heavier", ("tank", 250, "Venus"), ("cart", 220, "Earth")),
)


def _weight_row(row):
    want = row[0]
    if want == "newtons":
        _, thing, mass, verb, body = row
        g = GRAVITY[body]
        return (f"A {mass} kg {thing} {verb} {body}, where gravity is "
                f"{_one(g)} m/s². Weight is mass times gravity: print the "
                f"{thing}'s weight in newtons to one decimal place.",
                {"want": want, "mass": mass, "body": body, "g": g})
    if want == "scale":
        _, reading, body = row
        g = GRAVITY[body]
        return (f"A bathroom scale shows {reading} kg on Earth, where gravity "
                f"is {EARTH_G} m/s². On {body} gravity is {_one(g)} m/s²: "
                f"multiply the reading by {body}'s gravity divided by "
                f"Earth's, and print what the scale would show there, to one "
                f"decimal place.",
                {"want": want, "reading": reading, "body": body, "g": g})
    if want == "jump":
        _, height, body = row
        g = GRAVITY[body]
        return (f"On Earth, where gravity is {EARTH_G} m/s², you can jump "
                f"{height} m high. On {body} gravity is {_one(g)} m/s²: "
                f"multiply your jump by Earth's gravity divided by {body}'s, "
                f"and print how high you would jump there, in metres to two "
                f"decimal places.",
                {"want": want, "height": height, "body": body, "g": g})
    _, (t1, m1, b1), (t2, m2, b2) = row
    g1, g2 = GRAVITY[b1], GRAVITY[b2]
    return (f"A {m1} kg {t1} is on {b1}, where gravity is {_one(g1)} m/s², "
            f"and a {m2} kg {t2} is on {b2}, where it is {_one(g2)} m/s². "
            f"Print the {t1}'s weight in newtons to one decimal place, then "
            f"the {t2}'s, then whether the {t1} weighs more than the {t2}.",
            {"want": want, "one": (t1, m1, b1, g1), "two": (t2, m2, b2, g2)})


WEIGHT_PAGE = _page(
    "js-planets-weight", 218, "Planets: weight on other worlds",
    "Mass is how much stuff something is made of, and it is the same on "
    "every world. Weight is how hard a world pulls on that mass, and it "
    "changes from planet to planet. Physics measures weight as a force: "
    "mass in kilograms times the surface gravity in m/s², which gives "
    "newtons. A bathroom scale hides this by showing kilograms, so to find "
    "what it would show on Mars, multiply the Earth reading by Mars's "
    "gravity divided by Earth's: that fraction says how much weaker the "
    "pull is. A jump goes the other way. The weaker the pull, the higher "
    "the same legs send you, so multiply by Earth's gravity divided by the "
    "other world's. Decimals such as 23.1 are stored in binary as near "
    "misses, so 340 * 23.1 prints as 7854.000000000001; toFixed(1) rounds "
    "to one decimal place for printing and hands back the string 7854.0.",
    "const weight = 70 * 3.7; console.log(weight.toFixed(1)); prints 259.0, "
    "a 70 kg astronaut's weight on Mars in newtons; a scale that shows "
    "75 kg on Earth would show 75 * 3.7 / 9.8, about 28.3, on Mars",
    "js_planets_weight",
    tuple(_weight_row(row) for row in _WEIGHTS),
)


# ── 219. Conversions and scale models ────────────────────────

_UNITS = (
    ("miles", "Earth"),
    ("miles", "Mars"),
    ("miles", "Mercury"),
    ("miles", "Venus"),
    ("miles", "Jupiter"),
    ("au", "Mars"),
    ("au", "Saturn"),
    ("au", "Neptune"),
    ("au", "Venus"),
    ("au", "Pluto"),
    ("model", "Earth", 30),
    ("model", "Jupiter", 30),
    ("model", "Neptune", 10),
    ("model", "Mars", 20),
    ("model", "Mercury", 50),
    ("temp", "Venus"),
    ("temp", "Mars"),
    ("temp", "Earth"),
    ("temp", "Neptune"),
    ("temp", "Mercury"),
)


def _units_row(row):
    want, body = row[0], row[1]
    if want == "temp":
        c = TEMP[body]
        return (f"The mean temperature on {body} is {c} °C. Fahrenheit is "
                f"Celsius times 9, divided by 5, plus 32: print it in °F to "
                f"one decimal place.",
                {"want": want, "body": body, "c": c})
    d = DISTANCE[body]
    where = f"{body} is {_one(d)} million km from the Sun"
    if want == "miles":
        return (f"{where}, and a mile is {MILE_KM} km. Print the distance in "
                f"millions of miles to one decimal place.",
                {"want": want, "body": body, "d": d})
    if want == "au":
        return (f"{where}. One AU, the Earth's distance from the Sun, is "
                f"{AU_MILLION_KM} million km: print {body}'s distance in AU "
                f"to two decimal places.",
                {"want": want, "body": body, "d": d})
    ball = row[2]
    return (f"The Sun is {SUN_KM} km across. In a scale model it is a ball "
            f"{ball} cm across, and every distance shrinks by the same "
            f"factor. {where}: print how far from the ball it would be, in "
            f"metres to one decimal place.",
            {"want": want, "body": body, "d": d, "ball": ball})


UNITS_PAGE = _page(
    "js-planets-units", 219, "Planets: conversions and scale models",
    "Space numbers come in awkward units, and changing unit is a single "
    "multiply or divide by a fixed number. To know which, ask whether the "
    "answer should come out bigger or smaller: a mile is longer than a "
    "kilometre, so there are fewer of them, and you divide by 1.609344. "
    "Astronomers measure the solar system in AU, the Earth's distance from "
    "the Sun, 149.6 million km. Dividing by it turns Neptune's 4515 million "
    "km into about 30, which says at once that Neptune is thirty times "
    "farther out than we are. A scale model multiplies every distance by "
    "the same small factor, the model's size over the real size, which is "
    "why it keeps everything in proportion. Temperature is the odd one out "
    "because the two scales start from different places, so Fahrenheit "
    "needs a multiply and an add: Celsius times 9, divided by 5, plus 32.",
    "228 / 1.609344 is about 141.7, Mars's distance in millions of miles; "
    "228 / 149.6 is about 1.52 AU; and -65 * 9 / 5 + 32 is -85, so "
    "(-65 * 9 / 5 + 32).toFixed(1) prints -85.0",
    "js_planets_units",
    tuple(_units_row(row) for row in _UNITS),
)


# ── 220. How long light takes ────────────────────────────────

#: Trips that are not a planet's distance from the Sun: what the prompt
#: says and the km. The Mars figures are from NASA's Mars fact sheet, and
#: Pluto's farthest is the planetary fact sheet's aphelion.
_TRIPS = {
    "the Moon": ("the Moon is 384400 km from Earth", 384400),
    "Mars closest": ("at its closest, Mars is 54.6 million km from Earth",
                     54_600_000),
    "Mars farthest": ("at its farthest, Mars is 401.4 million km from Earth",
                      401_400_000),
    "Pluto farthest": ("at its farthest, Pluto is 7375.9 million km from "
                       "the Sun", 7_375_900_000),
}

_LIGHTS = (
    ("seconds", "the Moon"),
    ("laser", "the Moon"),
    ("seconds", "Earth"),
    ("seconds", "Mercury"),
    ("seconds", "Mars closest"),
    ("seconds", "Venus"),
    ("minsec", "Earth"),
    ("minsec", "Venus"),
    ("minsec", "Mars farthest"),
    ("there and back", "Mars farthest"),
    ("there and back", "Mars closest"),
    ("au", "Mercury"),
    ("au", "Mars"),
    ("au", "Ceres"),
    ("au", "Jupiter"),
    ("hms", "Saturn"),
    ("hms", "Uranus"),
    ("hms", "Neptune"),
    ("hms", "Pluto"),
    ("hms", "Pluto farthest"),
)

_LIGHT_SPEED = f"light travels {LIGHT_KM_S} km every second"


def _trip(key: str) -> tuple[str, int]:
    if key in _TRIPS:
        return _TRIPS[key]
    d = DISTANCE[key]
    return f"{key} is {_one(d)} million km from the Sun", _km(d)


def _light_row(row):
    want, key = row
    if want == "au":
        au = AU[key]
        return (f"{_cap(key)} averages {_say(au)} AU from the Sun, 1 AU is "
                f"{AU_KM} km, and {_LIGHT_SPEED}. Drop the fraction of a "
                f"second and print how long sunlight takes to reach {key}, "
                f"in the form 3 min 5 s.",
                {"want": "au", "au": au})
    where, km = _trip(key)
    if want == "laser":
        return (f"{_cap(where)}. A laser pulse fired at a mirror the Apollo "
                f"astronauts left there bounces straight back, at "
                f"{LIGHT_KM_S} km every second: print how many seconds the "
                f"round trip takes, to one decimal place.",
                {"want": "seconds", "km": km, "both": True})
    if want == "there and back":
        return (f"{_cap(where)}. A radio message to a rover there and the "
                f"rover's reply both travel at the speed of light, "
                f"{LIGHT_KM_S} km every second: drop the fraction of a "
                f"second and print how long the round trip takes, in the "
                f"form 3 min 5 s.",
                {"want": "minsec", "km": km, "both": True})
    if want == "seconds":
        return (f"{_cap(where)}, and {_LIGHT_SPEED}. Print how many seconds "
                f"light takes to cross that distance, to one decimal place.",
                {"want": want, "km": km})
    if want == "minsec":
        return (f"{_cap(where)}, and {_LIGHT_SPEED}. Drop the fraction of a "
                f"second and print how long light takes to cross that "
                f"distance, in the form 3 min 5 s.",
                {"want": want, "km": km})
    return (f"{_cap(where)}, and {_LIGHT_SPEED}. Drop the fraction of a "
            f"second and print how long sunlight takes to get there, in the "
            f"form 1 h 2 min 3 s.",
            {"want": want, "km": km})


LIGHT_PAGE = _page(
    "js-planets-light", 220, "Planets: how long light takes",
    "Light covers 299792.458 km every second, and the solar system is still "
    "big enough to keep it waiting. Time is distance divided by speed, so a "
    "distance in km divided by 299792.458 is the time in seconds. A few "
    "hundred seconds read better as minutes and seconds. Math.floor drops "
    "the fraction to leave whole seconds, total. Math.floor(total / 60) is "
    "how many whole minutes fit in it, and total % 60 is the remainder: the "
    "seconds left over once every full minute has been taken out. Hours "
    "work the same way one level up: Math.floor(total / 3600) is the hours, "
    "and the minutes come from what is left after them, total % 3600. A "
    "distance in AU becomes km by multiplying by 149597870.7, which, like "
    "the speed of light, is exact by definition.",
    "149600000 / 299792.458 is about 499.0 seconds for sunlight to reach "
    "Earth; with total = 499, Math.floor(total / 60) is 8 and total % 60 is "
    "19, so `${minutes} min ${total % 60} s` prints 8 min 19 s",
    "js_planets_light",
    tuple(_light_row(row) for row in _LIGHTS),
)


# ── 221. Your age on other worlds ────────────────────────────

_AGES = (
    ("age", 30, "Mars"),
    ("age", 12, "Mercury"),
    ("age", 40, "Jupiter"),
    ("age", 25, "Venus"),
    ("age", 60, "Saturn"),
    ("age", 8, "Mars"),
    ("birthdays", 30, "Jupiter"),
    ("birthdays", 45, "Mercury"),
    ("birthdays", 90, "Saturn"),
    ("birthdays", 21, "Mars"),
    ("birthdays", 84, "Uranus"),
    ("next", 10000, "Mars"),
    ("next", 20000, "Jupiter"),
    ("next", 12345, "Mercury"),
    ("next", 30000, "Saturn"),
    ("next", 9000, "Mars"),
    ("back", 10, "Mars"),
    ("back", 2, "Jupiter"),
    ("back", 100, "Mercury"),
    ("back", 50, "Venus"),
)


def _age_row(row):
    want, n, body = row
    year = YEAR[body]
    args = {"want": want, "body": body, "year": year}
    if want == "age":
        return (f"You are {n} Earth years old, and an Earth year is "
                f"{EARTH_YEAR} days. A year on {body} lasts {_say(year)} "
                f"Earth days: print your age in {body} years, to two decimal "
                f"places.", {**args, "age": n})
    if want == "birthdays":
        return (f"You are {n} Earth years old, an Earth year is {EARTH_YEAR} "
                f"days, and a year on {body} lasts {_say(year)} Earth days. "
                f"Print how many birthdays you would have had on {body}, "
                f"counting only whole {body} years.", {**args, "age": n})
    if want == "next":
        return (f"You have been alive {n} days, and a year on {body} lasts "
                f"{_say(year)} Earth days. Print how many {body} birthdays "
                f"you have had, then how many days are left until the next "
                f"one.", {**args, "days": n})
    return (f"Someone is {n} {body} years old, a {body} year lasts "
            f"{_say(year)} Earth days, and an Earth year is {EARTH_YEAR} "
            f"days. Print their age in Earth years, to two decimal places.",
            {**args, "n": n})


AGE_PAGE = _page(
    "js-planets-age", 221, "Planets: your age on other worlds",
    "A year is one trip round the Sun, so every planet has a year of its "
    "own: 88 Earth days on Mercury, 59800 on Neptune. To count an age in "
    "another planet's years, first turn it into days, years times 365.25 "
    "(the quarter covers the leap days), then divide by how many days that "
    "planet's year lasts. The longer the year, the smaller the age. A "
    "birthday is a whole year completed, so Math.floor of that age is how "
    "many birthdays you would have had: floor always rounds down, because "
    "a birthday you are nearly at has not happened yet. With an age in "
    "days, days % year is how far you are into the current year, and the "
    "year minus that is how long until the next birthday.",
    "30 Earth years is 30 * 365.25 = 10957.5 days; a Mars year is 687 days, "
    "so 10957.5 / 687 is about 15.95 Mars years, and "
    "Math.floor(10957.5 / 687) is 15 Martian birthdays",
    "js_planets_age",
    tuple(_age_row(row) for row in _AGES),
)


# ── 222. Kepler's third law ──────────────────────────────────

_KEPLERS = (
    ("years", "Mars"),
    ("years", "Jupiter"),
    ("years", "Saturn"),
    ("years", "Mercury"),
    ("years", "Ceres"),
    ("years", "Halley's Comet"),
    ("days", "Mars"),
    ("days", "Venus"),
    ("days", "Mercury"),
    ("days", "Jupiter"),
    ("days", "Ceres"),
    ("km", "Mars"),
    ("km", "Uranus"),
    ("km", "Neptune"),
    ("km", "Pluto"),
    ("ratio", "Saturn", "Jupiter"),
    ("ratio", "Mars", "Venus"),
    ("ratio", "Neptune", "Uranus"),
    ("ratio", "Jupiter", "Mars"),
    ("ratio", "Pluto", "Neptune"),
)


def _kepler_row(row):
    want, body = row[0], row[1]
    if want == "ratio":
        other = row[2]
        a1, a2 = AU[body], AU[other]
        return (f"{body} averages {_say(a1)} AU from the Sun and {other} "
                f"{_say(a2)} AU. Use Kepler's third law for both years, then "
                f"print how many times longer {body}'s year is than "
                f"{other}'s, to two decimal places.",
                {"want": want, "one": (body, a1), "two": (other, a2)})
    if want == "km":
        d = DISTANCE[body]
        return (f"{body} is {_one(d)} million km from the Sun, and 1 AU is "
                f"{AU_MILLION_KM} million km. Turn the distance into AU, then "
                f"use Kepler's third law to print {body}'s year in Earth "
                f"years, to two decimal places.",
                {"want": want, "body": body, "d": d})
    au = AU[body]
    if want == "years":
        return (f"{body} averages {_say(au)} AU from the Sun. By Kepler's "
                f"third law its year, in Earth years, is the square root of "
                f"that distance cubed: print it to two decimal places.",
                {"want": want, "body": body, "au": au})
    return (f"{body} averages {_say(au)} AU from the Sun. Use Kepler's third "
            f"law to find its year in Earth years, turn that into days at "
            f"{EARTH_YEAR} days a year, and print it rounded to the nearest "
            f"whole day.",
            {"want": want, "body": body, "au": au})


KEPLER_PAGE = _page(
    "js-planets-kepler", 222, "Planets: Kepler's third law",
    "In 1619 Johannes Kepler published a rule that every planet obeys: the "
    "square of its year equals the cube of its average distance from the "
    "Sun, as long as the year is in Earth years and the distance in AU. "
    "Earth checks out, 1 and 1. So for anything a AU out, the year is "
    "Math.sqrt(a * a * a): cube the distance, then take the square root. "
    "The year grows faster than the distance, because a planet farther out "
    "has a longer way round and also moves more slowly along it: Jupiter is "
    "about five times farther out than Earth, but its year is nearly twelve "
    "times as long. The law holds for anything going round the Sun, so it "
    "works for dwarf planets and comets too. Multiply by 365.25 for the "
    "year in days.",
    "Mars averages 1.524 AU from the Sun: 1.524 * 1.524 * 1.524 is about "
    "3.54, so years = Math.sqrt(1.524 * 1.524 * 1.524) is about 1.88, and "
    "Math.round(years * 365.25) is 687 days",
    "js_planets_kepler",
    tuple(_kepler_row(row) for row in _KEPLERS),
)


# ── 223. Where in the orbit ──────────────────────────────────

_ORBITS = (
    ("angle", "Mars", 1000),
    ("angle", "Earth", 100),
    ("angle", "Mercury", 200),
    ("angle", "Venus", 500),
    ("angle", "Jupiter", 10000),
    ("angle", "Mars", 2000),
    ("angle", "Saturn", 365),
    ("laps", "Mercury", 1000),
    ("laps", "Venus", 2000),
    ("laps", "Mars", 5000),
    ("laps", "Earth", 3000),
    ("laps", "Jupiter", 30000),
    ("synodic", "Earth", "Mars"),
    ("synodic", "Venus", "Earth"),
    ("synodic", "Earth", "Jupiter"),
    ("synodic", "Mercury", "Earth"),
    ("synodic", "Jupiter", "Saturn"),
    ("synodic", "Saturn", "Earth"),
    ("synodic", "Mars", "Jupiter"),
    ("synodic", "Neptune", "Uranus"),
)


def _orbit_row(row):
    want, body, x = row
    if want == "synodic":
        y1, y2 = YEAR[body], YEAR[x]
        return (f"{body} takes {_say(y1)} days to go round the Sun and {x} "
                f"takes {_say(y2)}. Print how many days pass from one "
                f"lining-up of the two to the next: 1 divided by the size of "
                f"the difference between 1 over each year, rounded to the "
                f"nearest whole day.",
                {"want": want, "one": (body, y1), "two": (x, y2)})
    year = YEAR[body]
    args = {"want": want, "body": body, "year": year, "days": x}
    if want == "angle":
        return (f"A year on {body} lasts {_say(year)} Earth days, one full "
                f"orbit of 360 degrees. Print how far round its current "
                f"orbit {body} is after {x} days, in degrees to one decimal "
                f"place.", args)
    return (f"A year on {body} lasts {_say(year)} Earth days. After {x} days, "
            f"print how many whole orbits {body} has made, then how many "
            f"degrees it is into the next one, to one decimal place.", args)


ORBIT_PAGE = _page(
    "js-planets-orbit", 223, "Planets: where in the orbit",
    "A planet goes 360 degrees round the Sun once per year, so after some "
    "days it has gone 360 * days / year degrees. Once that passes 360 it has "
    "done whole laps, and % 360 throws them away and keeps how far round "
    "the current lap it is, just as Math.floor(days / year) counts the laps "
    "themselves. Two planets line up with the Sun again and again, like "
    "runners on a track where the inner one keeps lapping the outer. Each "
    "day the faster one gains 1 / T1 - 1 / T2 of a lap on the slower, T "
    "being each one's year in days, so gaining a whole lap takes "
    "1 / (1 / T1 - 1 / T2) days, the synodic period. It is why Mars comes "
    "close to Earth only about every 780 days. Math.abs keeps the answer "
    "positive whichever planet is named first, and Math.round gives the "
    "nearest whole day.",
    "after 1000 days, Mars with its 687-day year has gone 360 * 1000 / 687, "
    "about 524 degrees, and (360 * 1000 / 687) % 360 is about 164.0; "
    "1 / Math.abs(1 / 365.25 - 1 / 687) rounds to 780 days",
    "js_planets_orbit",
    tuple(_orbit_row(row) for row in _ORBITS),
)


# ── 224. Escape velocity and orbital speed ───────────────────

_ESCAPES = (
    ("escape", "Earth"),
    ("escape", "Mars"),
    ("escape", "the Moon"),
    ("escape", "Jupiter"),
    ("escape", "Mercury"),
    ("escape", "Venus"),
    ("escape", "Saturn"),
    ("escape", "Neptune"),
    ("sun", "Venus"),
    ("sun", "Earth"),
    ("sun", "Mars"),
    ("sun", "Jupiter"),
    ("sun", "Uranus"),
    ("sun", "Neptune"),
    ("satellite", "Earth", 400, "The Space Station", "surface"),
    ("satellite", "Earth", 35786, "A geostationary weather satellite", "surface"),
    ("satellite", "Earth", 20200, "A GPS satellite", "surface"),
    ("satellite", "Mars", 400, "An orbiter", "surface"),
    ("satellite", "the Moon", 100, "A lunar orbiter", "surface"),
    ("satellite", "Jupiter", 1000, "A probe", "cloud tops"),
)


def _e(body: str) -> tuple:
    """A mass from the table as (digits, power of ten): 0.642 is (6.42, 23)."""
    d = Decimal(repr(MASS[body]))
    power = d.adjusted()
    digits = d.scaleb(-power)
    digits = int(digits) if digits == digits.to_integral_value() else float(digits)
    return digits, 24 + power


def _escape_row(row):
    want, body = row[0], row[1]
    if want == "sun":
        d = DISTANCE[body]
        return (f"{body} is {_one(d)} million km from the Sun, whose mass is "
                f"{SUN_MASS} kg, and G is {G}. Using the distance in metres, "
                f"print {body}'s orbital speed, the square root of G times "
                f"the Sun's mass over the distance, in km/s to one decimal "
                f"place.",
                {"want": want, "body": body, "d": d})
    mass, km = _e(body), DIAMETER[body]
    says = f"has a mass of {_say(mass[0])}e{mass[1]} kg and a diameter of {km} km"
    if want == "escape":
        return (f"{_cap(body)} {says}, and G is {G}. Using the radius in "
                f"metres, print {body}'s escape velocity, the square root of "
                f"2 times G times the mass over the radius, in km/s to two "
                f"decimal places.",
                {"want": want, "body": body, "mass": mass, "km": km})
    _, _, height, what, ground = row
    return (f"{what} circles {body} {height} km above the {ground}. "
            f"{_cap(body)} {says}, and G is {G}. With r measured from "
            f"{body}'s centre in metres, print the speed, the square root of "
            f"G times the mass over r, in km/s to two decimal places, then "
            f"the minutes one orbit takes, 2 times pi times r over the "
            f"speed, to one decimal place.",
            {"want": want, "body": body, "mass": mass, "km": km,
             "height": height})


ESCAPE_PAGE = _page(
    "js-planets-escape", 224, "Planets: escape velocity and orbital speed",
    "To leave a world for good, a rocket has to reach escape velocity, "
    "Math.sqrt(2 * G * M / r): G is the gravitational constant, M the "
    "world's mass in kg and r its radius in metres. Numbers this big and "
    "this small are written in e-notation: 5.97e24 is 5.97 with the point "
    "moved 24 places right, and 6.674e-11 has it moved 11 places left. The "
    "formula only works when every unit agrees, so halve the diameter to "
    "get the radius and multiply km by 1000 to get metres; the answer is "
    "then in metres per second, and dividing by 1000 gives km/s. Staying "
    "in a circular orbit takes less speed, Math.sqrt(G * M / r), with r "
    "measured from the centre: the radius plus the height above the "
    "ground, or for a planet going round the Sun, its distance from the "
    "Sun, with the Sun's mass. One orbit is the length of the circle, "
    "2 * Math.PI * r, divided by that speed.",
    "Math.sqrt(2 * 6.674e-11 * 5.97e24 / 6378000) is about 11178 m/s, so "
    "Earth's escape velocity prints as 11.18 km/s; the Space Station, "
    "400 km up, needs Math.sqrt(6.674e-11 * 5.97e24 / 6778000), about "
    "7667 m/s, or 7.67 km/s",
    "js_planets_escape",
    tuple(_escape_row(row) for row in _ESCAPES),
)


# ── 225. Filter, map and join ────────────────────────────────

_FILTERS = (
    ("names", "au", ">", 5, ("Mars", "Jupiter", "Saturn", "Uranus", "Neptune")),
    ("names", "km", "<", 10000, ("Mercury", "Venus", "Earth", "Mars")),
    ("names", "day", ">", 100, ("Mercury", "Venus", "Earth", "Mars", "Jupiter")),
    ("names", "temp", "<", 0, ("Venus", "Earth", "Mars", "Jupiter")),
    ("names", "rings", "is", None, ("Earth", "Mars", "Jupiter", "Saturn", "Uranus")),
    ("names", "gravity", ">", 10, ("Venus", "Earth", "Jupiter", "Saturn", "Neptune")),
    ("names", "au", "<", 1.5, ("Mercury", "Venus", "Earth", "Mars")),
    ("names", "day", "<", 12, ("Earth", "Jupiter", "Saturn", "Uranus", "Neptune")),
    ("count", "temp", ">", 0, ("Mercury", "Venus", "Earth", "Mars")),
    ("count", "gravity", "<", 5, ("Mercury", "Earth", "Mars", "Jupiter", "Neptune")),
    ("count", "au", ">", 2, ("Venus", "Mars", "Jupiter", "Saturn")),
    ("count", "rings", "not", None, ("Mars", "Jupiter", "Saturn", "Earth", "Venus")),
    ("label", "day", "<", 20, ("Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune")),
    ("label", "au", "<", 2, ("Mercury", "Venus", "Earth", "Mars", "Jupiter")),
    ("label", "km", ">", 100000, ("Earth", "Jupiter", "Saturn", "Uranus")),
    ("label", "day", ">", 1000, ("Mercury", "Venus", "Earth", "Mars")),
    ("some", "temp", ">", 400, ("Mercury", "Venus", "Earth")),
    ("some", "km", ">", 100000, ("Mercury", "Venus", "Earth", "Mars")),
    ("every", "rings", "is", None, ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("every", "au", ">", 1, ("Mars", "Jupiter", "Venus", "Saturn")),
)

#: How a label is written, shown with a planet that is never in the data.
_LABEL_LIKE = {"au": "Pluto 39.481 AU", "km": "Pluto 2376 km", "day": "Pluto 153.3 h"}


def _which(field: str, op: str, limit, *, after_is: bool = False) -> str:
    """The planets a test keeps: farther than 5 AU from the Sun, with rings."""
    if field == "rings":
        if op == "is":
            return "ringed" if after_is else "with rings"
        return "without rings"
    x = _say(limit)
    return {
        ("au", ">"): f"farther than {x} AU from the Sun",
        ("au", "<"): f"closer than {x} AU to the Sun",
        ("km", ">"): f"more than {x} km across",
        ("km", "<"): f"less than {x} km across",
        ("day", ">"): f"with a day longer than {x} hours",
        ("day", "<"): f"with a day shorter than {x} hours",
        ("gravity", ">"): f"with surface gravity above {x} m/s²",
        ("gravity", "<"): f"with surface gravity below {x} m/s²",
        ("temp", ">"): f"warmer than {x} °C on average",
        ("temp", "<"): f"colder than {x} °C on average",
    }[(field, op)]


def _filter_row(row):
    want, field, op, limit, names = row
    make, items = _array(field, names)
    args = {"want": want, "field": field, "op": op, "limit": limit,
            "items": items}
    if want == "names":
        ask = (f"Print the names of the planets {_which(field, op, limit)}, "
               f"in the same order, joined by a comma and a space.")
    elif want == "count":
        ask = f"Print the number of planets {_which(field, op, limit)}."
    elif want == "label":
        ask = (f"Take the planets {_which(field, op, limit)} and print them "
               f"on one line, each written like {_LABEL_LIKE[field]}, joined "
               f"by a comma and a space.")
    else:
        which = _which(field, op, limit, after_is=True)
        whom = "any planet" if want == "some" else "every planet"
        ask = f"Print whether {whom} in the array is {which}."
    return f"{make} {ask}", args


FILTER_PAGE = _page(
    "js-planets-filter", 225, "Planets: filter, map and join",
    "Give each planet an object, { name: \"Mars\", au: 1.524 }, and the "
    "solar system becomes one array you can ask questions of. "
    "filter((p) => p.au > 5) goes through the array and keeps the planets "
    "the arrow function says true for, in their original order, leaving "
    "the array itself alone. map((p) => p.name) turns each planet into "
    "something else: here its name, or a label built with a template "
    "literal. join(\", \") glues the results into one string with a comma "
    "and a space between them. Chained, the three read like the question: "
    "which planets, what about them, and how to print it. For a count, take "
    "the filtered array's length. some and every answer yes or no "
    "directly: some is true as soon as one planet passes, every only when "
    "all of them do.",
    "planets.filter((p) => p.au > 5).map((p) => p.name).join(\", \") gives "
    "Jupiter, Saturn, Uranus, Neptune; planets.some((p) => p.rings) is true "
    "as soon as one planet has rings",
    "js_planets_filter",
    tuple(_filter_row(row) for row in _FILTERS),
)


# ── 226. Sort and reduce ─────────────────────────────────────

_SORTS = (
    ("up", "km", ("Earth", "Mars", "Mercury", "Venus")),
    ("up", "day", ("Mars", "Jupiter", "Uranus", "Saturn", "Neptune")),
    ("up", "au", ("Neptune", "Mercury", "Saturn", "Earth")),
    ("up", "temp", ("Earth", "Neptune", "Mars", "Venus", "Saturn")),
    ("up", "gravity", ("Jupiter", "Mars", "Neptune", "Earth")),
    ("down", "km", ("Uranus", "Jupiter", "Neptune", "Saturn")),
    ("down", "gravity", ("Venus", "Saturn", "Uranus", "Earth")),
    ("down", "day", ("Earth", "Mercury", "Mars", "Venus")),
    ("down", "temp", ("Earth", "Mars", "Mercury", "Venus")),
    ("down", "au", ("Mars", "Venus", "Jupiter", "Mercury", "Earth")),
    ("max", "km", ("Venus", "Earth", "Mars", "Mercury")),
    ("min", "km", ("Uranus", "Neptune", "Saturn")),
    ("max", "day", ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("min", "gravity", ("Venus", "Mercury", "Uranus")),
    ("max", "temp", ("Mercury", "Venus", "Earth")),
    ("min", "temp", ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("total", "mass", ("Mercury", "Venus", "Earth", "Mars"), 2),
    ("total", "mass", ("Jupiter", "Saturn", "Uranus", "Neptune"), 1),
    ("average", "km", ("Mercury", "Venus", "Earth", "Mars"), 2),
    ("average", "day", ("Jupiter", "Saturn", "Uranus", "Neptune"), 1),
)

#: Each field's two ends, low first, for saying which way to sort.
_ENDS = {
    "km": ("smallest", "largest"),
    "day": ("shortest day", "longest day"),
    "au": ("closest to the Sun", "farthest from the Sun"),
    "temp": ("coldest", "hottest"),
    "gravity": ("weakest gravity", "strongest gravity"),
}

#: The planet reduce is to find, by what it is looking for.
_EXTREME = {
    ("max", "km"): "the largest diameter",
    ("min", "km"): "the smallest diameter",
    ("max", "day"): "the longest day",
    ("min", "gravity"): "the weakest gravity",
    ("max", "temp"): "the highest mean temperature",
    ("min", "temp"): "the lowest mean temperature",
}


def _sort_row(row):
    want, field, names = row[0], row[1], row[2]
    make, items = _array(field, names)
    args = {"want": want, "field": field, "items": items}
    noun = FIELDS[field][2]
    if want in ("up", "down"):
        low, high = _ENDS[field]
        first, last = (low, high) if want == "up" else (high, low)
        ask = (f"Sort a copy of the array from {first} to {last} and print "
               f"the names in that order, joined by a comma and a space.")
    elif want in ("max", "min"):
        ask = (f"With reduce, find the planet with {_EXTREME[(want, field)]} "
               f"and print its name and its {noun}, with a space between.")
    else:
        digits = row[3]
        args["digits"] = digits
        if want == "total":
            ask = (f"With reduce, add up their masses and print the total "
                   f"{_places(digits)}.")
        else:
            ask = (f"With reduce, add up every {noun}, divide by how many "
                   f"planets there are, and print the average "
                   f"{_places(digits)}.")
    return f"{make} {ask}", args


SORT_PAGE = _page(
    "js-planets-sort", 226, "Planets: sort and reduce",
    "sort puts an array in order, and for numbers it needs a compare "
    "function such as (a, b) => a.km - b.km. JavaScript calls it with two "
    "planets at a time and looks only at the sign of what comes back: "
    "negative puts a first, positive puts b first. So a - b sorts smallest "
    "first and b - a biggest first. Without a compare function, sort "
    "compares everything as text: plain numbers come out with 142984 before "
    "4879, because 1 comes before 4, and objects have nothing sensible to "
    "compare at all. sort also rearranges the array it is called on, so "
    "[...planets] makes a copy to sort instead. reduce walks the array "
    "carrying one value along: to find the biggest, keep whichever of the "
    "two is larger at each step, (best, p) => (p.km > best.km ? p : best); "
    "for a total, add each one on, starting from 0.",
    "[...planets].sort((a, b) => a.km - b.km) puts Mercury, Mars, Venus, "
    "Earth in size order; planets.reduce((sum, p) => sum + p.mass, 0) adds "
    "up their masses",
    "js_planets_sort",
    tuple(_sort_row(row) for row in _SORTS),
)


# ── 227. A table that lines up ───────────────────────────────

_TABLES = (
    ("two", "au", 2, 8, 6, ("Mercury", "Venus", "Earth", "Mars")),
    ("two", "gravity", 1, 8, 5, ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("two", "day", 1, 8, 7, ("Mercury", "Venus", "Earth", "Mars")),
    ("two", "temp", 0, 8, 5, ("Venus", "Earth", "Mars", "Neptune")),
    ("two", "au", 1, 10, 5, ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("two", "km", 0, 8, 7, ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("header", "au", 2, 8, 6, ("Mars", "Jupiter", "Saturn"), "AU"),
    ("header", "gravity", 1, 9, 5, ("Mercury", "Venus", "Earth"), "g"),
    ("header", "day", 1, 8, 6, ("Earth", "Mars", "Jupiter"), "Hours"),
    ("header", "temp", 0, 8, 5, ("Mercury", "Earth", "Uranus"), "Temp"),
    ("header", "mass", 2, 8, 6, ("Mercury", "Venus", "Earth"), "Mass"),
    ("three", (("au", 2, 6), ("gravity", 1, 5)), 8, ("Mercury", "Venus", "Earth")),
    ("three", (("au", 1, 5), ("day", 1, 6)), 8, ("Mars", "Jupiter", "Saturn")),
    ("three", (("km", 0, 7), ("temp", 0, 5)), 6, ("Earth", "Mars", "Venus")),
    ("three", (("gravity", 1, 5), ("temp", 0, 6)), 8, ("Uranus", "Neptune", "Earth")),
    ("three", (("au", 2, 6), ("day", 1, 8)), 9, ("Mercury", "Venus", "Earth")),
    ("numbered", "km", 0, 9, 7, ("Mercury", "Venus", "Earth", "Mars")),
    ("numbered", "km", 0, 8, 8, ("Jupiter", "Saturn", "Uranus", "Neptune")),
    ("numbered", "temp", 0, 8, 5, ("Mercury", "Venus", "Earth", "Mars")),
    ("numbered", "day", 1, 8, 7, ("Earth", "Mars", "Jupiter", "Saturn")),
)

_BAR = "a | with a space on each side"


def _column(field: str, digits: int, width: int) -> str:
    noun = FIELDS[field][2]
    return f"the {noun} {_places(digits)} padded at the start to {width} characters"


def _table_row(row):
    want = row[0]
    if want == "three":
        _, ((f1, d1, w1), (f2, d2, w2)), nw, names = row
        t1, t2 = FIELDS[f1][0], FIELDS[f2][0]
        items = tuple((n, t1[n], t2[n]) for n in names)
        listing = "; ".join(f"{n} {_say(v1)} and {_say(v2)}" for n, v1, v2 in items)
        return (f"Make an array of planet objects, each with a name, "
                f"{FIELDS[f1][1]} as {f1} and {FIELDS[f2][1]} as {f2}: "
                f"{listing}. For each planet print one line: the name padded "
                f"at the end to {nw} characters, {_BAR}, "
                f"{_column(f1, d1, w1)}, another such |, and "
                f"{_column(f2, d2, w2)}.",
                {"want": want, "columns": ((f1, d1, w1), (f2, d2, w2)),
                 "name_width": nw, "items": items})
    _, field, digits, nw, width, names, *title = row
    make, items = _array(field, names)
    args = {"want": want, "field": field, "digits": digits, "name_width": nw,
            "width": width, "items": items}
    name = f"the name padded at the end to {nw} characters"
    column = _column(field, digits, width)
    if want == "numbered":
        return (f"{make} Number the planets from 1 and print one line for "
                f"each: the number, a full stop and a space, then {name} and "
                f"{column}.", args)
    if want == "header":
        args["title"] = title[0]
        return (f"{make} First print a header line made the same way from "
                f"the words Planet and {title[0]}, then one line for each "
                f"planet: {name}, then {_BAR}, then {column}.", args)
    return (f"{make} For each planet print one line: {name}, then {_BAR}, "
            f"then {column}.", args)


TABLE_PAGE = _page(
    "js-planets-table", 227, "Planets: a table that lines up",
    "A table lines up when every value in a column takes the same width. "
    "padEnd(8) adds spaces after a string until it is 8 characters long, "
    "which suits names, read from the left. padStart(6) adds the spaces in "
    "front, which suits numbers: their digits and decimal points then line "
    "up on the right. Both are string methods, so turn the number into a "
    "string first. toFixed(2) does that and fixes how many decimals it "
    "shows, so 1 and 30.18 come out as 1.00 and 30.18, and String(n) does "
    "it for whole numbers. A string already as long as the width comes "
    "back unchanged, so pick widths that fit the longest value with room to "
    "spare. A template literal puts the padded pieces together, with "
    "\" | \" between the columns.",
    "`${\"Mars\".padEnd(8)} | ${(1.524).toFixed(2).padStart(6)}` is Mars and "
    "four spaces, then \" | \", then two spaces and 1.52, and every row "
    "built the same way lines up under it",
    "js_planets_table",
    tuple(_table_row(row) for row in _TABLES),
)


JSPLANETS_PAGES: tuple[Page, ...] = (
    WEIGHT_PAGE,
    UNITS_PAGE,
    LIGHT_PAGE,
    AGE_PAGE,
    KEPLER_PAGE,
    ORBIT_PAGE,
    ESCAPE_PAGE,
    FILTER_PAGE,
    SORT_PAGE,
    TABLE_PAGE,
)
