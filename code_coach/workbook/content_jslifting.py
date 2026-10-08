"""Pages 228-237: JavaScript, bodybuilding and strength training.

A training log is arithmetic from the first set to the last: the volume
lifted, calories from grams of food, a rest timer, a one-rep max from a
formula, lean mass and FFMI, working weights rounded to what a bar can
carry, a plan that climbs week by week, personal records, a weekly split,
and the plates on each side of the bar. These ten pages drill each one as a
short program, easiest first, with the numbers changing from exercise to
exercise. The gym is the flavour; the arithmetic is the lesson.

Numbered after the planets pages (218-227, content_jsplanets), so this tuple
has to be registered after that set's pages for the book to stay in order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

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


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


_ORDINALS = {2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth"}


def _a(n: int) -> str:
    """A or An, by how the number sounds: an 8-week plan, an 11-week plan."""
    return "An" if str(n).startswith("8") or n in (11, 18) else "A"


# ── 228. Training volume ─────────────────────────────────────

_STRAIGHT = (
    # lift, sets, reps, kg
    ("squat", 5, 5, 100),
    ("bench press", 4, 8, 62.5),
    ("deadlift", 3, 5, 140),
    ("overhead press", 5, 5, 42.5),
    ("barbell row", 4, 10, 60),
    ("front squat", 3, 6, 72.5),
    ("leg press", 4, 12, 150),
)

_SESSIONS = (
    # lift, (reps, kg) for every set
    ("squat", ((8, 60), (8, 70), (6, 80), (5, 85))),
    ("bench press", ((10, 40), (8, 50), (6, 60), (4, 67.5))),
    ("deadlift", ((5, 100), (3, 130), (1, 160))),
    ("overhead press", ((8, 30), (6, 37.5), (5, 42.5))),
    ("Romanian deadlift", ((10, 60), (10, 70), (8, 80))),
    ("incline press", ((12, 40), (10, 45), (8, 50), (6, 52.5))),
    ("hack squat", ((15, 60), (12, 80), (10, 100), (8, 110))),
)

_PLANS = (
    # plan A, plan B, each (sets, reps, kg)
    ((5, 5, 100), (3, 10, 80)),
    ((5, 3, 120), (4, 8, 80)),
    ((3, 8, 70), (4, 6, 70)),
    ((10, 3, 90), (3, 10, 85)),
    ((3, 5, 110), (5, 5, 80)),
    ((6, 2, 140), (4, 6, 72.5)),
)


def _set_words(sets) -> str:
    (reps, kg), *rest = sets
    first = f"{reps} {'rep' if reps == 1 else 'reps'} at {kg} kg"
    return _and([first] + [f"{r} at {k} kg" for r, k in rest])


def _volume_rows():
    for lift, sets, reps, kg in _STRAIGHT:
        yield (f"Today's {lift} was {sets} sets of {reps} reps at {kg} kg. "
               f"Print the volume, sets times reps times the weight.",
               {"want": "straight", "sets": sets, "reps": reps, "kg": kg})
    for lift, sets in _SESSIONS:
        yield (f"Today's {lift} sets were {_set_words(sets)}. Keep them as an "
               f"array of [reps, kg] pairs, add up reps times kg over every "
               f"set with reduce, and print the total.",
               {"want": "session", "sets": sets})
    for one, two in _PLANS:
        yield (f"Plan A is {one[0]} sets of {one[1]} at {one[2]} kg and plan B "
               f"is {two[0]} sets of {two[1]} at {two[2]} kg. Write "
               f"volume(sets, reps, kg), then print plan A's volume, plan B's "
               f"volume, and whether plan B's volume is higher than plan A's, "
               f"one per line.",
               {"want": "compare", "a": one, "b": two})


VOLUME_PAGE = _page(
    "js-lift-volume", 228, "Bodybuilding: training volume",
    "Volume is the number most training logs are built around: how much "
    "weight you moved in total. For straight sets, the same reps at the "
    "same weight every set, it is sets times reps times weight, so 5 sets of "
    "5 at 100 kg is 2500 kg. A real session is rarely that tidy, because the "
    "weight climbs as you warm up, so keep each set as a [reps, kg] pair in "
    "an array and let reduce add reps * kg for every set. Destructuring the "
    "pair right in the parameter list, ([reps, kg]), names both numbers at "
    "once. Give reduce its starting total of 0: without it, reduce starts "
    "from the first pair itself, and an array plus a number makes a string, "
    "not a sum.",
    "const sets = [[8, 60], [6, 80], [5, 85]]; sets.reduce((total, [reps, "
    "kg]) => total + reps * kg, 0) is 480 + 480 + 425 = 1385; 5 sets of 5 "
    "at 100 kg is 5 * 5 * 100 = 2500",
    "js_lift_volume",
    tuple(_volume_rows()),
)


# ── 229. Calories from macros ────────────────────────────────

_TOTALS = (
    # protein, carbs, fat, in grams
    (150, 250, 70),
    (180, 300, 80),
    (120, 200, 60),
    (200, 350, 90),
    (140, 180, 75),
)

_SHARES = (
    (160, 220, 65),
    (130, 260, 70),
    (190, 240, 60),
    (110, 300, 85),
    (220, 200, 50),
)

_TARGETS = (
    # bodyweight in kg, grams of protein per kg
    (72, 1.6),
    (85, 1.8),
    (68, 2.2),
    (94, 1.7),
    (61, 2),
)

_SPLITS = (
    # calories, percent from (protein, carbs, fat)
    (2400, (30, 45, 25)),
    (2000, (25, 50, 25)),
    (2800, (30, 40, 30)),
    (3200, (25, 55, 20)),
    (3600, (30, 45, 25)),
)


def _macro_rows():
    for p, c, f in _TOTALS:
        yield (f"A day's food comes to {p} g of protein, {c} g of carbohydrate "
               f"and {f} g of fat. At 4 kcal per gram of protein, 4 per gram "
               f"of carbohydrate and 9 per gram of fat, print the day's total "
               f"calories.",
               {"want": "total", "protein": p, "carbs": c, "fat": f})
    for p, c, f in _SHARES:
        yield (f"A day's food comes to {p} g of protein, {c} g of carbohydrate "
               f"and {f} g of fat, at 4, 4 and 9 kcal per gram. Print the "
               f"total calories, then the percentage of them that comes from "
               f"protein, rounded to the nearest whole number, one per line.",
               {"want": "share", "protein": p, "carbs": c, "fat": f})
    for weight, per_kg in _TARGETS:
        yield (f"A lifter weighing {weight} kg aims for {per_kg} g of protein "
               f"per kilogram of bodyweight each day. Print the grams of "
               f"protein that comes to, rounded to the nearest gram, then the "
               f"calories in that many grams at 4 kcal per gram, one per line.",
               {"want": "target", "bodyweight": weight, "per_kg": per_kg})
    for kcal, (p, c, f) in _SPLITS:
        yield (f"A plan of {kcal} kcal a day takes {p}% of it from protein, "
               f"{c}% from carbohydrate and {f}% from fat. At 4, 4 and 9 kcal "
               f"per gram, print the grams of protein, carbohydrate and fat, "
               f"each rounded to the nearest gram, on one line with a space "
               f"between.",
               {"want": "split", "calories": kcal, "split": (p, c, f)})


MACROS_PAGE = _page(
    "js-lift-macros", 229, "Bodybuilding: calories from macros",
    "Food labels give protein, carbohydrate and fat in grams, and each gram "
    "carries a fixed amount of energy: 4 kcal for protein, 4 for "
    "carbohydrate, 9 for fat. A day's calories are grams times energy per "
    "gram, added up: protein * 4 + carbs * 4 + fat * 9. A share is a part "
    "over the whole, protein's calories divided by the total, and times 100 "
    "makes it a percentage. Divisions rarely come out whole, so round for "
    "display, and round once, at the end: rounding in the middle throws a "
    "little away every time. Run backwards, the same arithmetic plans a "
    "day: a percentage of a calorie target, divided by the kcal per gram, "
    "is grams.",
    "150 g protein, 250 g carbs and 70 g fat is 150 * 4 + 250 * 4 + 70 * 9 "
    "= 2230 kcal, and protein's share is Math.round(150 * 4 / 2230 * 100), "
    "27 percent",
    "js_lift_macros",
    tuple(_macro_rows()),
)


# ── 230. Rest timers and session time ────────────────────────

_CLOCKS = (90, 45, 125, 180, 61, 600, 247)

_LENGTHS = (
    # exercise, sets, seconds of work per set, seconds of rest between
    ("squats", 5, 40, 90),
    ("bench press", 4, 30, 120),
    ("curls", 3, 35, 60),
    ("deadlifts", 3, 25, 180),
    ("dips", 3, 23, 90),
    ("rows", 4, 33, 90),
    ("lunges", 2, 50, 75),
)

_COUNTDOWNS = (
    # rest in seconds, shown every this many seconds
    (90, 30),
    (120, 40),
    (60, 15),
    (150, 50),
    (45, 9),
    (100, 20),
)

_TWO_DIGITS = "as minutes and seconds with a colon between and the seconds always two digits"


def _timer_rows():
    for seconds in _CLOCKS:
        yield (f"The rest timer reads {seconds} seconds. Print it "
               f"{_TWO_DIGITS}, so 65 seconds would be 1:05.",
               {"want": "clock", "seconds": seconds})
    for name, sets, work, rest in _LENGTHS:
        yield (f"{sets} sets of {name}, each about {work} seconds of work, "
               f"with {rest} seconds of rest between sets and none after the "
               f"last. Work out the total time in seconds, then print it "
               f"{_TWO_DIGITS}.",
               {"want": "session", "sets": sets, "work": work, "rest": rest})
    for rest, step in _COUNTDOWNS:
        yield (f"{_a(rest)} {rest}-second rest timer shows the time left every {step} "
               f"seconds. Print what it shows, from the full {rest} seconds "
               f"down to 0, one per line, {_TWO_DIGITS}.",
               {"want": "countdown", "rest": rest, "step": step})


TIMER_PAGE = _page(
    "js-lift-timer", 230, "Bodybuilding: rest timers and session time",
    "A rest timer counts seconds; people read minutes and seconds. "
    "Math.floor(seconds / 60) is the whole minutes, and seconds % 60 is the "
    "remainder, what is left once every full minute is taken out. The "
    "seconds always need two digits, or 125 seconds would read 2:5: "
    "String(n).padStart(2, \"0\") adds zeros at the front until the text is "
    "two characters long. For a whole exercise, count the gaps with care: "
    "5 sets have only 4 rests between them, because nobody times the rest "
    "after the last set, so the total is sets * work + (sets - 1) * rest. "
    "Forgetting that - 1 is the fencepost mistake: five fence posts have "
    "four gaps between them.",
    "Math.floor(125 / 60) is 2 and 125 % 60 is 5, and String(5).padStart(2, "
    "\"0\") is \"05\", so the timer shows 2:05; 5 sets of 40 seconds with 90 "
    "seconds of rest take 5 * 40 + 4 * 90 = 560 seconds, 9:20",
    "js_lift_timer",
    tuple(_timer_rows()),
)


# ── 231. One-rep max ─────────────────────────────────────────

_EPLEY = "the weight times (1 + reps / 30)"
_BRZYCKI = "the weight times 36 / (37 - reps)"

_EPLEYS = ((100, 5), (80, 8), (140, 3), (62.5, 10), (185, 2))
_BRZYCKIS = ((100, 5), (90, 8), (120, 3), (60, 10), (152.5, 6))
_BOTHS = ((100, 6), (70, 9), (130, 4), (47.5, 8), (200, 2))
_GUARDS = (
    # (kg, reps) for each call
    ((100, 5), (100, 1), (80, 12)),
    ((60, 1), (60, 8), (60, 15)),
    ((120, 10), (120, 11), (125, 1)),
    ((82.5, 4), (90, 2), (40, 20)),
    ((142.5, 1), (130, 3), (110, 6)),
)


def _call_words(kg, reps) -> str:
    return f"{kg} kg for {reps} {'rep' if reps == 1 else 'reps'}"


def _onerm_rows():
    for kg, reps in _EPLEYS:
        yield (f"You lifted {kg} kg for {reps} reps. Estimate your one-rep "
               f"max with Epley's formula, {_EPLEY}, and print it to one "
               f"decimal place.",
               {"want": "epley", "kg": kg, "reps": reps})
    for kg, reps in _BRZYCKIS:
        yield (f"You lifted {kg} kg for {reps} reps. Estimate your one-rep "
               f"max with Brzycki's formula, {_BRZYCKI}, and print it to one "
               f"decimal place.",
               {"want": "brzycki", "kg": kg, "reps": reps})
    for kg, reps in _BOTHS:
        yield (f"You lifted {kg} kg for {reps} reps. Print the one-rep max "
               f"from Epley's formula, {_EPLEY}, then from Brzycki's, "
               f"{_BRZYCKI}, each to one decimal place, on one line with a "
               f"space between.",
               {"want": "both", "kg": kg, "reps": reps})
    for sets in _GUARDS:
        yield (f"Write oneRepMax(kg, reps) with Epley's formula, {_EPLEY}, "
               f"that returns the weight itself for a single rep and too many "
               f"reps for more than 10. Print it for "
               f"{_and(_call_words(k, r) for k, r in sets)}, one per line, "
               f"every number to one decimal place.",
               {"want": "guard", "sets": sets})


ONERM_PAGE = _page(
    "js-lift-onerm", 231, "Bodybuilding: estimating a one-rep max",
    "Your one-rep max, or 1RM, is the most you can lift for a single rep, "
    "and most strength programs are written as percentages of it. A true "
    "max attempt is tiring and needs a spotter, so lifters often estimate "
    "it from a set of a few reps instead. Two well-known formulas do it: "
    "Epley's, weight * (1 + reps / 30), and Brzycki's, weight * 36 / (37 - "
    "reps). They are fitted to real lifters rather than derived, so they "
    "disagree a little, and both are trusted only for about 2 to 10 reps: "
    "one rep already is the max, and past ten the guess drifts. A function "
    "handles that with guard clauses, returning early for the cases the "
    "formula does not cover. The results are rarely whole, so toFixed(1) "
    "prints one decimal place, and always shows it, even for 160.0.",
    "100 kg for 5 reps: Epley gives 100 * (1 + 5 / 30) = 116.666..., which "
    "toFixed(1) prints as 116.7, and Brzycki gives 100 * 36 / (37 - 5) = "
    "112.5",
    "js_lift_onerm",
    tuple(_onerm_rows()),
)


# ── 232. Body composition ────────────────────────────────────

_LEANS = ((80, 15), (72, 18), (95, 22), (68, 12), (88, 20))
_FFMIS = ((78, 15, 1.8), (75, 12, 1.75), (90, 16, 1.85), (62, 14, 1.68), (100, 20, 1.9))
_NORMALS = ((80, 15, 1.8), (95, 14, 1.9), (70, 12, 1.7), (66, 10, 1.65), (102, 16, 1.88))
_CMS = ((75, 18, 172), (84, 15, 180), (68, 20, 165), (92, 12, 186), (58, 22, 160))


def _bodycomp_rows():
    for weight, fat in _LEANS:
        yield (f"You weigh {weight} kg at {fat}% body fat. Print your fat "
               f"mass, the weight times the percentage over 100, then your "
               f"lean mass, everything else, each to one decimal place, one "
               f"per line.",
               {"want": "lean", "weight": weight, "fat": fat})
    for weight, fat, height in _FFMIS:
        yield (f"You weigh {weight} kg at {fat}% body fat and are {height} m "
               f"tall. Work out your lean mass, then your FFMI, lean mass "
               f"divided by height squared, and print the FFMI to one decimal "
               f"place.",
               {"want": "ffmi", "weight": weight, "fat": fat, "height": height})
    for weight, fat, height in _NORMALS:
        yield (f"You weigh {weight} kg at {fat}% body fat and are {height} m "
               f"tall. Print your FFMI, lean mass over height squared, then "
               f"the normalised FFMI, the FFMI plus 6.1 times (1.8 minus the "
               f"height), each to one decimal place, one per line.",
               {"want": "normal", "weight": weight, "fat": fat,
                "height": height})
    for weight, fat, cm in _CMS:
        yield (f"You weigh {weight} kg at {fat}% body fat and are {cm} cm "
               f"tall. Turn the height into metres, then print your FFMI, "
               f"lean mass divided by height in metres squared, to one "
               f"decimal place.",
               {"want": "cm", "weight": weight, "fat": fat, "cm": cm})


BODYCOMP_PAGE = _page(
    "js-lift-bodycomp", 232, "Bodybuilding: lean mass and FFMI",
    "Bodyweight alone does not say how much of it is muscle, so a body-fat "
    "percentage splits it in two. Fat mass is weight * bodyFat / 100, and "
    "lean mass, everything else, is weight * (1 - bodyFat / 100): dividing "
    "by 100 turns 15 percent into the fraction 0.15 that the formula needs. "
    "FFMI, the fat-free mass index, divides lean mass by height in metres "
    "squared. It is BMI with lean mass in place of weight, so lifters of "
    "different heights can be compared. Taller people tend to score a "
    "little higher, and the normalised FFMI corrects for that by adding "
    "6.1 * (1.8 - height), which lowers a tall lifter's score and raises a "
    "short one's toward what it would be at 1.8 m. A height in centimetres "
    "must be divided by 100 first, or the answer comes out ten thousand "
    "times too small.",
    "80 kg at 15% body fat is 80 * (1 - 15 / 100) = 68 kg lean; at 1.8 m, "
    "68 / (1.8 * 1.8) is 20.98..., so the FFMI prints as 21.0 with "
    "toFixed(1)",
    "js_lift_bodycomp",
    tuple(_bodycomp_rows()),
)


# ── 233. Working weights from percentages ────────────────────

_ONES = ((140, 75), (135, 85), (160, 65), (100, 70), (185, 80), (92.5, 75))
_RAWS = ((150, 72), (118, 85), (205, 65), (87.5, 80), (172, 77))
_RAMPS = (
    (150, (65, 75, 85)),
    (120, (50, 60, 70, 80)),
    (210, (40, 60, 80)),
    (96, (65, 75, 85)),
    (132.5, (60, 70, 80, 90)),
)
_POUNDS = ((315, 80), (225, 72), (405, 65), (185, 85))


def _percent_rows():
    for best, percent in _ONES:
        yield (f"Your one-rep max is {best} kg and today's sets are at "
               f"{percent}% of it. Work out that weight, round it to the "
               f"nearest 2.5 kg, and print it.",
               {"want": "one", "max": best, "percent": percent})
    for best, percent in _RAWS:
        yield (f"Your one-rep max is {best} kg. Print {percent}% of it to two "
               f"decimal places, then the same weight rounded to the nearest "
               f"2.5 kg, one per line.",
               {"want": "raw", "max": best, "percent": percent})
    for best, percents in _RAMPS:
        yield (f"Your one-rep max is {best} kg. For sets at "
               f"{_and(f'{p}%' for p in percents)} of it, print each "
               f"percentage and its weight rounded to the nearest 2.5 kg, as "
               f"65% 97.5, one per line.",
               {"want": "ramp", "max": best, "percents": percents})
    for best, percent in _POUNDS:
        yield (f"In a gym that loads in 5 lb steps, your one-rep max is {best} "
               f"lb and today's sets are at {percent}% of it. Print that "
               f"weight rounded to the nearest 5 lb.",
               {"want": "lb", "max": best, "percent": percent})


PERCENT_PAGE = _page(
    "js-lift-percent", 233, "Bodybuilding: working weights from percentages",
    "Strength programs are written in percentages of your one-rep max: "
    "three sets at 75 percent, a top set at 85. 75 percent of 140 kg is 105 "
    "kg, easy, but 85 percent of 135 kg is 114.75, and a bar cannot be "
    "loaded to that: the smallest jump most gyms can make is 2.5 kg, a 1.25 "
    "kg plate on each side. So round to the nearest 2.5. Dividing by 2.5 "
    "counts how many 2.5 kg steps the weight is, Math.round makes that a "
    "whole number of steps, and multiplying by 2.5 turns the steps back into "
    "kilograms: 114.75 / 2.5 is 45.9 steps, which rounds to 46, and 46 * 2.5 "
    "is 115. The same three moves round to any step, such as 5 lb in a gym "
    "that uses pounds.",
    "const roundTo = (kg) => Math.round(kg / 2.5) * 2.5; roundTo(135 * 85 / "
    "100) is Math.round(45.9) * 2.5 = 115, and roundTo(150 * 65 / 100) stays "
    "97.5, already a whole number of steps",
    "js_lift_percent",
    tuple(_percent_rows()),
)


# ── 234. Progressive overload ────────────────────────────────

_BLOCKS = (
    # start kg, kg added a week, weeks, deload every, deload percent
    (60, 2.5, 8, 4, 90),
    (100, 5, 6, 3, 80),
    (40, 2.5, 5, 4, 90),
    (80, 5, 9, 4, 90),
    (120, 2.5, 7, 4, 85),
    (50, 2.5, 10, 5, 90),
    (140, 5, 6, 3, 90),
    (30, 2.5, 8, 4, 80),
)

_FINALS = (
    (65, 2.5, 12, 4, 90),
    (100, 5, 10, 4, 90),
    (80, 2.5, 16, 4, 85),
    (45, 2.5, 9, 3, 90),
    (120, 5, 11, 4, 90),
    (70, 2.5, 15, 5, 80),
)

_GOALS = (
    # start kg, kg added a week, deload every, deload percent, goal kg
    (60, 2.5, 4, 90, 67.5),
    (60, 2.5, 4, 90, 65),
    (100, 5, 4, 90, 140),
    (80, 2.5, 3, 85, 87.5),
    (40, 5, 4, 80, 55),
    (150, 2.5, 5, 90, 160),
)


def _deload_words(every, percent) -> str:
    return (f"every {_ORDINALS[every]} week is a deload that lifts {percent}% "
            f"of that week's planned weight, rounded to the nearest 2.5 kg, "
            f"while the plan keeps climbing")


def _overload_rows():
    for start, step, weeks, every, percent in _BLOCKS:
        yield (f"{_a(weeks)} {weeks}-week plan starts at {start} kg and adds {step} kg "
               f"every week; {_deload_words(every, percent)}. Print the "
               f"weight lifted each week, one per line.",
               {"want": "weeks", "start": start, "step": step, "weeks": weeks,
                "every": every, "percent": percent})
    for start, step, weeks, every, percent in _FINALS:
        yield (f"{_a(weeks)} {weeks}-week plan starts at {start} kg and adds {step} kg "
               f"every week; {_deload_words(every, percent)}. Print only the "
               f"weight lifted in week {weeks}.",
               {"want": "final", "start": start, "step": step, "weeks": weeks,
                "every": every, "percent": percent})
    for start, step, every, percent, goal in _GOALS:
        yield (f"A plan starts at {start} kg and adds {step} kg every week; "
               f"{_deload_words(every, percent)}. Print the number of the "
               f"first week in which the weight lifted is at least {goal} kg.",
               {"want": "goal", "start": start, "step": step, "every": every,
                "percent": percent, "goal": goal})


OVERLOAD_PAGE = _page(
    "js-lift-overload", 234, "Bodybuilding: progressive overload, week by week",
    "Muscles adapt to what they are asked to do, so a program asks for a "
    "little more each week: progressive overload. The simplest plan adds a "
    "fixed step, say 2.5 kg, every week. Recovery matters too, so every few "
    "weeks comes a lighter deload week. Here every fourth week lifts 90 "
    "percent of that week's planned weight, rounded to the nearest 2.5 kg, "
    "and the plan carries on climbing behind it. In code that is a loop "
    "over the weeks with an if inside, and week % 4 === 0 is the test: the "
    "remainder is 0 exactly on weeks 4, 8 and 12. Keep two numbers apart, "
    "the plan, which only ever goes up, and what is lifted, which dips on a "
    "deload.",
    "starting at 60 kg and adding 2.5 a week, week 4's plan is 67.5, and as "
    "a deload it lifts Math.round(67.5 * 0.9 / 2.5) * 2.5 = 60; week 5 is "
    "back on the plan at 70",
    "js_lift_overload",
    tuple(_overload_rows()),
)


# ── 235. Personal records ────────────────────────────────────

_LOGS = (
    (("squat", 100), ("bench", 70), ("squat", 105), ("deadlift", 140),
     ("bench", 72.5)),
    (("deadlift", 160), ("deadlift", 150), ("squat", 120), ("deadlift", 165)),
    (("bench", 80), ("press", 50), ("bench", 77.5), ("press", 52.5),
     ("bench", 82.5)),
    (("row", 70), ("curl", 30), ("row", 75), ("curl", 30), ("row", 72.5)),
    (("squat", 90), ("squat", 95), ("squat", 100), ("squat", 97.5)),
    (("press", 40), ("bench", 60), ("squat", 80), ("deadlift", 100),
     ("press", 42.5), ("squat", 85)),
    (("deadlift", 180), ("squat", 140), ("bench", 100), ("deadlift", 175),
     ("bench", 102.5), ("squat", 140)),
)

_ASKS = (
    # the log, then the lifts to print in order
    ((("squat", 100), ("bench", 70), ("squat", 105)),
     ("deadlift", "squat", "bench")),
    ((("press", 45), ("press", 47.5), ("row", 60)),
     ("row", "press")),
    ((("deadlift", 150), ("squat", 110), ("deadlift", 155), ("squat", 107.5)),
     ("squat", "bench", "deadlift")),
    ((("curl", 25), ("curl", 27.5), ("curl", 25)),
     ("curl", "row", "press")),
    ((("bench", 90), ("squat", 120), ("bench", 92.5), ("press", 55)),
     ("press", "bench", "squat")),
    ((("row", 80), ("deadlift", 170), ("row", 82.5), ("deadlift", 170)),
     ("deadlift", "row", "squat")),
)

_RECORD_DAYS = (
    # records so far, then today's sets in order
    ((("squat", 120), ("bench", 85), ("deadlift", 160)),
     (("squat", 115), ("squat", 122.5), ("bench", 85), ("deadlift", 165))),
    ((("bench", 100), ("press", 60)),
     (("bench", 100), ("press", 57.5), ("bench", 97.5))),
    ((("squat", 140), ("deadlift", 180)),
     (("squat", 142.5), ("squat", 145), ("deadlift", 180))),
    ((("row", 70), ("curl", 35), ("press", 50)),
     (("press", 52.5), ("row", 70), ("curl", 37.5), ("press", 50))),
    ((("deadlift", 200),),
     (("deadlift", 190), ("deadlift", 200), ("deadlift", 202.5))),
    ((("squat", 100), ("bench", 75)),
     (("squat", 102.5), ("bench", 77.5), ("squat", 105), ("bench", 80))),
    ((("press", 65), ("bench", 110), ("squat", 150)),
     (("squat", 150), ("bench", 112.5), ("press", 65))),
)


def _lifts(rows) -> str:
    return _and(f"{lift} {kg} kg" for lift, kg in rows)


def _records_rows():
    for log in _LOGS:
        yield (f"Your training log, in order: {_lifts(log)}. Keep each lift's "
               f"best weight in a Map, then print each lift with its best as "
               f"squat 105, one per line, in the order the lifts first appear.",
               {"want": "best", "log": log})
    for log, ask in _ASKS:
        yield (f"Your training log, in order: {_lifts(log)}. Keep each lift's "
               f"best weight in a Map, then print the records for "
               f"{_and(ask)}, in that order, as squat 105, one per line, with "
               f"none in place of the weight for a lift that is not in the log.",
               {"want": "order", "log": log, "ask": ask})
    for records, today in _RECORD_DAYS:
        yield (f"Your records stand at {_lifts(records)}, kept in a Map. Today "
               f"you lifted {_lifts(today)}, in that order. Each time a set is "
               f"heavier than the record, update the Map and print the set as "
               f"squat 122.5; equalling a record does not count. Finish with "
               f"the count, as records broken: 2.",
               {"want": "new", "records": records, "today": today})


RECORDS_PAGE = _page(
    "js-lift-records", 235, "Bodybuilding: personal records in a Map",
    "A personal record, a PR, is the heaviest you have ever lifted on one "
    "exercise, and keeping them is a perfect job for a Map: the lift's name "
    "is the key and the best weight so far is the value. For each set in "
    "the log, if the Map has no entry for that lift yet, or the set is "
    "heavier than the entry, set it. Heavier means strictly heavier: "
    "equalling a record is good work but not a new record, so the test is > "
    "and not >=. A Map keeps its keys in the order they were first added, "
    "and setting a new value for a key does not move it, so looping over "
    "the Map lists the lifts in the order they first turned up. Asking for "
    "a key it does not have gives undefined, and ?? swaps that for "
    "something printable.",
    "if (!best.has(lift) || kg > best.get(lift)) best.set(lift, kg); after "
    "squat 100, bench 70 and squat 105 the Map holds squat 105 and bench 70, "
    "in that order, and best.get(\"deadlift\") ?? \"none\" is none",
    "js_lift_records",
    tuple(_records_rows()),
)


# ── 236. The weekly split ────────────────────────────────────

_PPL = (("Mon", ("chest", "shoulders", "triceps")), ("Tue", ("back", "biceps")),
        ("Wed", ("legs",)), ("Thu", ("chest", "shoulders", "triceps")),
        ("Fri", ("back", "biceps")), ("Sat", ("legs",)), ("Sun", ()))
_UPPER_LOWER = (("Mon", ("chest", "back", "shoulders")),
                ("Tue", ("quads", "hamstrings", "calves")), ("Wed", ()),
                ("Thu", ("chest", "back", "arms")),
                ("Fri", ("quads", "hamstrings", "glutes")), ("Sat", ()),
                ("Sun", ()))
_FULL_BODY = (("Mon", ("legs", "chest", "back")), ("Tue", ()),
              ("Wed", ("legs", "chest", "back")), ("Thu", ()),
              ("Fri", ("legs", "chest", "back")), ("Sat", ()), ("Sun", ()))

_COUNTS = (
    _PPL,
    _UPPER_LOWER,
    (("Mon", ("chest", "triceps")), ("Tue", ("back", "biceps")), ("Wed", ()),
     ("Thu", ("legs",)), ("Fri", ("shoulders", "arms")), ("Sat", ("chest",)),
     ("Sun", ())),
    _FULL_BODY,
    (("Mon", ("legs",)), ("Tue", ("chest", "back")), ("Wed", ("arms",)),
     ("Thu", ()), ("Fri", ("legs",)), ("Sat", ("chest", "shoulders")),
     ("Sun", ())),
    (("Mon", ("back",)), ("Tue", ("chest", "biceps")), ("Wed", ("legs", "abs")),
     ("Thu", ()), ("Fri", ("back", "chest")), ("Sat", ("abs", "legs")),
     ("Sun", ())),
    (("Mon", ("glutes", "hamstrings")), ("Tue", ("chest", "triceps")),
     ("Wed", ()), ("Thu", ("quads", "glutes")), ("Fri", ("back", "biceps")),
     ("Sat", ("shoulders",)), ("Sun", ())),
)

_RESTS = (
    _PPL,
    _UPPER_LOWER,
    _FULL_BODY,
    (("Mon", ("chest",)), ("Tue", ("back",)), ("Wed", ("legs",)), ("Thu", ()),
     ("Fri", ("shoulders",)), ("Sat", ("arms",)), ("Sun", ())),
    (("Mon", ()), ("Tue", ("legs",)), ("Wed", ("chest", "back")), ("Thu", ()),
     ("Fri", ("legs",)), ("Sat", ("shoulders", "arms")), ("Sun", ())),
    (("Mon", ("legs", "back")), ("Tue", ("chest",)), ("Wed", ("legs",)),
     ("Thu", ("back",)), ("Fri", ("chest",)), ("Sat", ()), ("Sun", ("legs",))),
)

_ROWS = (
    _PPL,
    (("Mon", ("chest", "triceps")), ("Tue", ("triceps", "shoulders")),
     ("Wed", ()), ("Thu", ("legs",)), ("Fri", ("back", "biceps")), ("Sat", ()),
     ("Sun", ())),
    (("Mon", ("legs",)), ("Tue", ("chest",)), ("Wed", ("back",)), ("Thu", ()),
     ("Fri", ("shoulders",)), ("Sat", ("arms",)), ("Sun", ("legs",))),
    _FULL_BODY,
    (("Mon", ("chest", "back")), ("Tue", ("legs",)), ("Wed", ("chest", "back")),
     ("Thu", ("legs",)), ("Fri", ()), ("Sat", ()), ("Sun", ())),
    (("Mon", ("back", "biceps")), ("Tue", ("chest",)), ("Wed", ("legs",)),
     ("Thu", ("shoulders",)), ("Fri", ("back", "biceps")),
     ("Sat", ("biceps", "abs")), ("Sun", ())),
    (("Mon", ("abs", "chest")), ("Tue", ("back",)), ("Wed", ("abs", "legs")),
     ("Thu", ()), ("Fri", ("abs", "shoulders")), ("Sat", ()), ("Sun", ("abs",))),
)


def _week_words(days) -> str:
    return "; ".join(f"{day} {_and(groups) if groups else 'rest'}"
                     for day, groups in days)


def _split_rows():
    base = ("Your week, as [day, groups] pairs with an empty array on a rest "
            "day: {}. ")
    for days in _COUNTS:
        yield (base.format(_week_words(days))
               + "Count the days each muscle group is trained by reducing into "
               "an object, then print each group and its count as chest 2, "
               "one per line, in the order the groups first appear.",
               {"want": "count", "days": days})
    for days in _RESTS:
        yield (base.format(_week_words(days))
               + "Print the rest days joined by a comma and a space, then on "
               "the next line the number of training days.",
               {"want": "rest", "days": days})
    for days in _ROWS:
        yield (base.format(_week_words(days))
               + "The week repeats, so Sunday runs into Monday. Print whether "
               "any muscle group is trained on two days in a row.",
               {"want": "row", "days": days})


SPLIT_PAGE = _page(
    "js-lift-split", 236, "Bodybuilding: the weekly split",
    "A split is how a week of training is divided up: chest and triceps on "
    "Monday, back and biceps on Tuesday, and so on. Written as an array of "
    "[day, groups] pairs, with an empty array on a rest day, every question "
    "about the week is an array method. How often is each muscle trained? "
    "Reduce into an object, adding one to each group's count, with ?? 0 for "
    "a group seen for the first time. Which days are rest days? filter the "
    "days whose groups are empty, then map each to its name. Is any muscle "
    "trained two days running, before it has had a day to recover? Compare "
    "each day with the next using some and includes, and because the week "
    "repeats, Sunday's next day is Monday: (i + 1) % 7 wraps index 6 round "
    "to 0.",
    "split.reduce((counts, [day, groups]) => { for (const g of groups) "
    "counts[g] = (counts[g] ?? 0) + 1; return counts; }, {}) counts every "
    "group, and split[(6 + 1) % 7] is Monday again",
    "js_lift_split",
    tuple(_split_rows()),
)


# ── 237. Plate math ──────────────────────────────────────────

_KG_PLATES = "25, 20, 15, 10, 5, 2.5 and 1.25 kg"
_LB_PLATES = "45, 35, 25, 10, 5 and 2.5 lb"

_EXACT_LOADS = (100, 60, 140, 82.5, 185, 47.5, 220, 127.5)
_KG_TRIES = (101, 90, 103, 75, 66, 157)
_LB_TRIES = (225, 315, 185, 200, 152, 99)


def _plates_rows():
    for target in _EXACT_LOADS:
        yield (f"Load {target} kg on a 20 kg bar: take off the bar, halve what "
               f"is left for each side, and fill one side greedily from plates "
               f"of {_KG_PLATES}, heaviest first and as many of each as fit. "
               f"Print the plates for one side, separated by spaces.",
               {"want": "kg", "target": target})
    for target in _KG_TRIES:
        yield (f"Load {target} kg on a 20 kg bar, filling one side greedily "
               f"from plates of {_KG_PLATES}, heaviest first. Print the plates "
               f"for one side separated by spaces, then on the next line exact "
               f"if nothing is left over, or the amount still missing on each "
               f"side as 0.5 left over.",
               {"want": "check", "target": target})
    for target in _LB_TRIES:
        yield (f"Load {target} lb on a 45 lb bar, filling one side greedily "
               f"from plates of {_LB_PLATES}, heaviest first. Print the plates "
               f"for one side separated by spaces, then on the next line exact "
               f"if nothing is left over, or the pounds still missing on each "
               f"side as 1 left over.",
               {"want": "lb", "target": target})


PLATES_PAGE = _page(
    "js-lift-plates", 237, "Bodybuilding: plate math",
    "Loading a bar is a small algorithm. Take the bar off the target, 20 kg "
    "for a standard barbell, and halve what is left, since both sides must "
    "match. Then go greedily: start at the heaviest plate, put it on while "
    "it still fits, and move to the next size down when it does not. For "
    "100 kg that is 40 kg a side: a 25 fits, a second would not; a 20 does "
    "not fit in the 15 left; a 15 does, and the side is done. A for...of "
    "over the plate sizes with a while inside does exactly that. Some "
    "targets cannot be made exactly, and then something is left over when "
    "the sizes run out, so check for it rather than print a load that is "
    "wrong. With these plates greedy finds an exact load whenever there is "
    "one, because every size is a whole number of the smallest plates.",
    "(100 - 20) / 2 is 40 a side: 25 fits and leaves 15, 20 does not fit, 15 "
    "fits and leaves 0, so the side is 25 15; for 101 kg, 40.5 a side ends "
    "with 0.5 left over",
    "js_lift_plates",
    tuple(_plates_rows()),
)


JSLIFTING_PAGES: tuple[Page, ...] = (
    VOLUME_PAGE,
    MACROS_PAGE,
    TIMER_PAGE,
    ONERM_PAGE,
    BODYCOMP_PAGE,
    PERCENT_PAGE,
    OVERLOAD_PAGE,
    RECORDS_PAGE,
    SPLIT_PAGE,
    PLATES_PAGE,
)
