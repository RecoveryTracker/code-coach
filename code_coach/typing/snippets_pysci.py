"""Python for science and the things people measure: planets, lifting, music, food.

The lines are the ones a small calculating script is made of, drawn from
four places a person keeps numbers: the planets (weight and gravity, light
travel time, Kepler's third law, escape velocity), a training log (one-rep
max estimates, plate math, calories from macros), music (beats per minute
as milliseconds, MIDI notes as frequencies, transposing with a remainder)
and the kitchen (scaling a recipe exactly with Fraction, converting units).
The last group is the tables: padding and aligning with f-strings.

The planetary figures are NASA's Planetary Fact Sheet, rounded as the sheet
rounds them: gravity in m/s^2, mass, diameter, distance from the Sun. Moon
counts are left out on purpose - they change as new moons are found, and a
line to type should not go out of date. The constants are the defined or
standard ones: the astronomical unit and the speed of light are exact by
definition, standard gravity is 9.80665 m/s^2, and the Sun's GM is known far
better than G or the Sun's mass on their own. For music, MIDI note 69 is A4
at 440 Hz and middle C is 60 (C4); sharps only.

The blocks are whole little programs that print their result, and the
tests run every one in the real interpreter and hold what it prints to an
answer worked out by hand - so they read no clock and roll no dice, and every
fractional result goes through a format spec or round, with the figures
chosen so that none sits on a rounding tie.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYSCI_LINES: tuple[Passage, ...] = (
    # Gravity and weight
    _s("GRAVITY = {\"Mercury\": 3.7, \"Venus\": 8.9, \"Earth\": 9.8, \"Mars\": 3.7}",
       "surface gravity in m/s^2, from NASA's fact sheet"),
    _s("EARTH_G = 9.80665", "standard gravity, exact by definition"),
    _s("weight_n = mass_kg * GRAVITY[\"Mars\"]", "weight is mass times gravity, in newtons"),
    _s("on_mars = weight_kg * GRAVITY[\"Mars\"] / GRAVITY[\"Earth\"]",
       "what an Earth scale would read there"),
    _s("moon_ratio = 1.62 / EARTH_G", "the Moon pulls about a sixth as hard as Earth"),
    _s("G_CONST = 6.6743e-11", "the gravitational constant, in SI units"),
    _s("radius_m = diameter_km * 1000 / 2", "half the diameter, in metres"),
    _s("surface_g = G_CONST * mass_kg / radius_m**2",
       "gravity: G times the mass over the radius squared"),
    _s("v_escape = math.sqrt(2 * G_CONST * mass_kg / radius_m)",
       "escape velocity, in metres per second"),
    _s("v_orbit = math.sqrt(G_CONST * mass_kg / (radius_m + altitude_m))",
       "the speed of a circular orbit at that height"),
    _s("fall_time = math.sqrt(2 * height_m / g)", "seconds to fall, with no air"),
    _s("jump_height = speed * speed / (2 * g)", "how high a take-off speed gets you"),
    _s("density = mass_kg / (4 / 3 * math.pi * radius_m**3)",
       "mass over the volume of a sphere"),

    # Light and distance
    _s("AU_KM = 149_597_870.7", "the astronomical unit in km, exact since 2012"),
    _s("C_KM_S = 299_792.458", "the speed of light in km/s, exact by definition"),
    _s("light_seconds = distance_km / C_KM_S", "how long light takes to cross it"),
    _s("minutes, seconds = divmod(round(light_seconds), 60)", "seconds as minutes and seconds"),
    _s("print(f\"{minutes} min {seconds:02d} s\")", "8 min 19 s, with the seconds padded"),
    _s("round_trip = 2 * distance_km / C_KM_S", "a signal out and the reply back"),
    _s("LIGHT_YEAR_KM = C_KM_S * 365.25 * 86_400", "light's speed times a Julian year"),
    _s("au = distance_km / AU_KM", "a distance in astronomical units"),
    _s("print(f\"{name:<8}{au:6.2f} AU {light_min:6.1f} min\")",
       "name left, numbers lined up on the right"),

    # Kepler
    _s("years = au ** 1.5", "Kepler's third law: the period squared is the distance cubed"),
    _s("au = years ** (2 / 3)", "and backwards, from the period to the distance"),
    _s("ratio = period_days**2 / distance_au**3", "the same for every planet, in these units"),
    _s("GM_SUN = 1.32712440018e20", "the Sun's G times M, known far better than G alone"),
    _s("period_s = 2 * math.pi * math.sqrt(a_m**3 / GM_SUN)",
       "the full law: a period in seconds from metres"),
    _s("speed = 2 * math.pi * radius_km / (period_days * 86_400)",
       "average orbital speed in km/s"),

    # Lifting
    _s("one_rm = weight * (1 + reps / 30)", "the Epley estimate of a one-rep max"),
    _s("one_rm = weight * 36 / (37 - reps)", "the Brzycki estimate; poor above ten reps"),
    _s("def epley(weight: float, reps: int) -> float:", "an estimate as a function"),
    _s("percent = round(weight / one_rm * 100)", "a working weight as a percentage"),
    _s("working = round(one_rm * 0.85 / 5) * 5", "85 percent, to the nearest 5"),
    _s("PLATES = [45, 35, 25, 10, 5, 2.5]", "the plates in a gym, heaviest first"),
    _s("per_side = (target - bar) / 2", "the plates are loaded in pairs"),
    _s("for plate in PLATES:", "greedy: use the biggest plate that fits"),
    _s("count, per_side = divmod(per_side, plate)", "how many fit, and what is left"),
    _s("loaded.extend([plate] * int(count))", "that many of this plate"),
    _s("volume = sum(w * r for w, r in sets)", "weight times reps, over all sets"),
    _s("calories = protein * 4 + carbs * 4 + fat * 9", "4, 4 and 9 calories per gram"),
    _s("print(f\"{fat * 9 / calories:.0%} from fat\")", "a share, printed as a percentage"),
    _s("kg = lbs * 0.45359237", "pounds to kilograms; the factor is exact"),
    _s("bmr = 10 * kg + 6.25 * cm - 5 * age + 5", "Mifflin-St Jeor, the male version"),
    _s("tdee = bmr * 1.55", "a moderately active day"),

    # Music
    _s("beat_ms = 60_000 / bpm", "milliseconds in one beat"),
    _s("sixteenth_ms = 60_000 / bpm / 4", "a sixteenth is a quarter of a beat"),
    _s("bpm = round(60_000 / beat_ms)", "tempo from the gap between beats"),
    _s("hz = 440 * 2 ** ((midi - 69) / 12)", "equal temperament: note 69 is A4 at 440 Hz"),
    _s("midi = round(69 + 12 * math.log2(hz / 440))", "the nearest note to a frequency"),
    _s("NAMES = [\"C\", \"C#\", \"D\", \"D#\", \"E\", \"F\", \"F#\", \"G\", \"G#\", \"A\", \"A#\", \"B\"]",
       "the twelve pitch classes, sharps only"),
    _s("name = NAMES[midi % 12] + str(midi // 12 - 1)", "69 becomes A4"),
    _s("transposed = [(n + 5) % 12 for n in notes]", "up a fourth, wrapped round the octave"),
    _s("MAJOR = (0, 2, 4, 5, 7, 9, 11)", "the major scale, in semitones"),
    _s("scale = [(root + step) % 12 for step in MAJOR]", "that scale in any key"),
    _s("cents = 1200 * math.log2(played / target)", "how far out of tune; 100 is a semitone"),
    _s("gain = 10 ** (db / 20)", "decibels back to an amplitude ratio"),
    _s("samples = round(seconds * 44_100)", "a length in samples at CD rate"),

    # Recipes and units
    _s("from fractions import Fraction", "exact fractions, so a third stays a third"),
    _s("scale = Fraction(servings, 4)", "a recipe for four, scaled to the guests"),
    _s("amount = Fraction(3, 4) * scale", "three quarters of a cup, times the scale"),
    _s("print(f\"{amount} cups\")", "a Fraction prints as 9/8"),
    _s("total = sum(parts, Fraction(0))", "adding fractions: start from a Fraction zero"),
    _s("ML_PER = {\"cup\": 236.588, \"tbsp\": 14.787, \"tsp\": 4.929}", "US kitchen measures in ml"),
    _s("celsius = (fahrenheit - 32) / 1.8", "an oven temperature in degrees C"),
    _s("fahrenheit = celsius * 9 / 5 + 32", "and back again"),
    _s("grams = ounces * 28.3495", "ounces to grams"),
    _s("UNITS = {\"km\": 1000.0, \"m\": 1.0, \"cm\": 0.01, \"mi\": 1609.344}",
       "each unit's length in metres"),
    _s("value_m = amount * UNITS[unit]", "convert to the base unit first"),

    # Tables with f-strings
    _s("header = f\"{'Planet':<10}{'g':>6}{'km':>9}\"", "column titles with the same widths"),
    _s("print(\"-\" * 25)", "a rule as wide as the table"),
    _s("for name, g, km in rows:", "one row at a time"),
    _s("print(f\"{name:<10}{g:>6.1f}{km:>9,}\")", "text left, numbers right, thousands commas"),
    _s("rows.sort(key=lambda row: row[1], reverse=True)", "strongest gravity first"),
    _s("print(f\"{unit:>4} {amount:>10.2f}\")", "right-aligned, two decimal places"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYSCI_BLOCKS: tuple[Passage, ...] = (
    _b(r"""GRAVITY = {"Venus": 8.9, "Earth": 9.8, "Mars": 3.7, "Jupiter": 23.1}


def scale_reading(kg, planet):
    return kg * GRAVITY[planet] / GRAVITY["Earth"]


for planet in ("Venus", "Mars", "Jupiter"):
    print(f"{planet}: {scale_reading(70, planet):.1f} kg")""",
       "weight elsewhere, as a scale set for Earth would show it"),
    _b(r"""C_KM_S = 299_792.458


def light_time(distance_km):
    minutes, seconds = divmod(round(distance_km / C_KM_S), 60)
    return f"{minutes} min {seconds} s"


print("Sun to Earth:", light_time(149_597_870.7))
print("Sun to Mars:", light_time(228.0e6))
print("Moon to Earth:", light_time(384_400))""",
       "how long light takes to arrive"),
    _b(r"""AU_KM = 149_597_870.7
distance_km = {"Earth": 149.6e6, "Mars": 228.0e6, "Jupiter": 778.5e6}

for name, km in distance_km.items():
    au = km / AU_KM
    years = au**1.5
    print(f"{name}: {au:.2f} AU, {years:.2f} years")""",
       "Kepler's third law: the year from the distance"),
    _b(r"""import math

G = 6.674e-11
BODIES = {
    "Earth": (5.97e24, 12756),
    "Mars": (0.642e24, 6792),
    "Moon": (7.35e22, 3475),
}

for name, (mass, diameter_km) in BODIES.items():
    radius_m = diameter_km * 1000 / 2
    v_escape = math.sqrt(2 * G * mass / radius_m)
    print(f"{name}: {v_escape / 1000:.1f} km/s")""",
       "escape velocity from mass and size"),
    _b(r"""def epley(weight, reps):
    return weight * (1 + reps / 30)


def brzycki(weight, reps):
    return weight * 36 / (37 - reps)


for weight, reps in ((100, 6), (200, 3), (60, 10)):
    print(weight, reps, round(epley(weight, reps)), round(brzycki(weight, reps)))""",
       "two one-rep max estimates side by side"),
    _b(r"""PLATES = [45, 25, 10, 5, 2.5]


def plates_per_side(target, bar=45):
    left = (target - bar) / 2
    loaded = []
    for plate in PLATES:
        count, left = divmod(left, plate)
        loaded += [plate] * int(count)
    return loaded, left


print(plates_per_side(225))
print(plates_per_side(185))
print(plates_per_side(137.5))""",
       "plate math: the plates for each side of the bar"),
    _b(r"""def calories(protein, carbs, fat):
    return protein * 4 + carbs * 4 + fat * 9


meals = {"breakfast": (30, 50, 12), "lunch": (45, 60, 20), "dinner": (40, 40, 25)}
total = 0
for name, (p, c, f) in meals.items():
    kcal = calories(p, c, f)
    total += kcal
    print(f"{name:<10}{kcal:>5} kcal {f * 9 / kcal:4.0%} fat")
print("total", total)""",
       "calories from the macros of three meals"),
    _b(r"""NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def hz(midi):
    return 440 * 2 ** ((midi - 69) / 12)


def name(midi):
    return NAMES[midi % 12] + str(midi // 12 - 1)


for midi in (60, 69, 72, 81):
    print(name(midi), f"{hz(midi):.2f}")""",
       "MIDI numbers as note names and frequencies"),
    _b(r"""NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR = (0, 2, 4, 5, 7, 9, 11)


def scale(root):
    return [NAMES[(NAMES.index(root) + step) % 12] for step in MAJOR]


def transpose(notes, semitones):
    return [NAMES[(NAMES.index(n) + semitones) % 12] for n in notes]


print(" ".join(scale("G")))
print(transpose(["C", "E", "G"], -5), transpose(["A", "B"], 14))""",
       "a major scale and transposing with a remainder"),
    _b(r"""print(f"{'BPM':>4}{'beat ms':>10}{'bar ms':>9}")
for bpm in (60, 90, 100, 120, 174):
    beat = 60_000 / bpm
    print(f"{bpm:>4}{beat:>10.1f}{beat * 4:>9.0f}")""",
       "a tempo table in fixed columns"),
    _b(r"""from fractions import Fraction

RECIPE = {"flour": Fraction(3, 4), "sugar": Fraction(1, 3), "milk": Fraction(1, 2)}


def scaled(servings, base=4):
    k = Fraction(servings, base)
    return {name: cups * k for name, cups in RECIPE.items()}


for name, cups in scaled(6).items():
    print(f"{name:<6}{cups!s:>5} cups {float(cups):.3f}")
print(sum(scaled(2).values()))""",
       "scaling a recipe exactly with Fraction"),
    _b(r"""UNITS = {"km": 1000.0, "m": 1.0, "cm": 0.01, "mi": 1609.344, "ft": 0.3048}


def convert(value, source, target):
    return value * UNITS[source] / UNITS[target]


for target in ("m", "mi", "ft"):
    print(f"{target:>3} {convert(5, 'km', target):>10.3f}")
print(round(convert(26.2, "mi", "km"), 1), convert(100, "cm", "m"))""",
       "unit conversion from one table"),
)
