"""JavaScript for a training log: sets, volume, maxes, plates and macros.

The lines are what a lifting tracker is made of: a session kept as data,
volume load added up with reduce, one-rep-max estimates, rounding to a
weight that can actually be loaded and working out the plates for it,
progressive overload, calories and macros, personal records in a Map, a
rest timer's mm:ss, and a weekly split.

The formulas are the standard published ones - Epley's and Brzycki's
one-rep-max estimates, the Atwater factors of 4, 4 and 9 kcal a gram, the
Mifflin-St Jeor equation - and the numbers are kilograms, with a 20 kg bar
and the usual plates from 25 down to 1.25. It is arithmetic, not advice:
a target such as protein per kilogram is a parameter the caller chooses,
never a recommendation written into the code.

The blocks are whole little programs that print their result, and the
tests run every one in Node and hold what it prints to an answer worked
out by hand - so nothing in them reads the clock or rolls a random
number.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSLIFTING_LINES: tuple[Passage, ...] = (
    # The log as data
    _s("const set = { exercise: 'squat', weightKg: 100, reps: 5, rpe: 8 };",
       "one set: the lift, the load, the reps and how hard it felt"),
    _s("const session = { date: '2026-10-06', sets: [] };",
       "a training day: an ISO date and the sets to come"),
    _s("session.sets.push({ exercise: 'deadlift', weightKg: 140, reps: 3 });",
       "log a set as soon as it is done"),
    _s("const squats = log.filter((s) => s.exercise === 'squat');",
       "every squat set and nothing else"),
    _s("const exercises = [...new Set(log.map((s) => s.exercise))];",
       "each exercise once, in the order it was first done"),
    _s("const topSquat = Math.max(...squats.map((s) => s.weightKg));",
       "the heaviest squat in the log"),
    _s("const lastSet = session.sets.at(-1);", "the set just finished"),
    _s("const { exercise, weightKg, reps } = set;", "a set unpacked into three names"),
    _s("const allHit = sets.every((s) => s.reps >= s.targetReps);",
       "true only if every set reached its target"),
    _s("const firstMiss = sets.findIndex((s) => s.reps < s.targetReps);",
       "the first set that fell short, or -1"),
    _s("const allSets = sessions.flatMap((s) => s.sets);",
       "every set from every session, in one flat list"),

    # Volume
    _s("const volume = sets.reduce((sum, s) => sum + s.weightKg * s.reps, 0);",
       "volume load: weight times reps, summed"),
    _s("const totalReps = sets.reduce((sum, s) => sum + s.reps, 0);",
       "every rep in the session"),
    _s("const byExercise = Object.groupBy(log, (s) => s.exercise);",
       "ES2024: one list of sets per exercise"),
    _s("const tonnes = (volume / 1000).toFixed(1);", "kilograms into tonnes, one decimal"),
    _s("const hardSets = sets.filter((s) => s.rpe >= 8).length;",
       "how many sets were RPE 8 or harder"),

    # One-rep maxes
    _s("const epley = (w, r) => w * (1 + r / 30);", "Epley's estimate of a one-rep max"),
    _s("const brzycki = (w, r) => (w * 36) / (37 - r);",
       "Brzycki's estimate; it matches Epley's at ten reps"),
    _s("const e1rm = reps === 1 ? weight : epley(weight, reps);",
       "a single is already a max, so leave it alone"),
    _s("const pct = Math.round((weight / oneRepMax) * 100);",
       "this set as a percentage of the max"),
    _s("const trainingMax = Math.round(oneRepMax * 0.9);",
       "a training max: ninety percent of the real one"),
    _s("const repsAt = Math.floor(30 * (oneRepMax / weight - 1));",
       "Epley turned round: the reps on offer at a weight"),
    _s("const bestE1rm = Math.max(...sets.map((s) => epley(s.weightKg, s.reps)));",
       "the best estimated max of the day"),

    # Plates
    _s("const BAR_KG = 20;", "a men's Olympic barbell weighs 20 kg"),
    _s("const PLATES_KG = [25, 20, 15, 10, 5, 2.5, 1.25];", "kilo plates, heaviest first"),
    _s("const loadable = Math.round(target / 2.5) * 2.5;",
       "to the nearest 2.5 kg, a pair of 1.25s"),
    _s("const capped = Math.floor(target / 5) * 5;", "down to a 5 kg step, never up"),
    _s("let perSide = (total - BAR_KG) / 2;", "what goes on each sleeve"),
    _s("for (const plate of PLATES_KG) {", "heaviest plates first: the greedy way"),
    _s("const count = Math.floor(perSide / plate);", "how many of this plate fit"),
    _s("perSide -= count * plate;", "what is left to load"),
    _s("const loaded = BAR_KG + 2 * oneSide.reduce((a, p) => a + p, 0);",
       "the bar plus both sides"),
    _s("const lb = Math.round(kg * 2.20462);", "kilograms to pounds, to the pound"),
    _s("const kg = Math.round((lb / 2.20462) * 10) / 10;",
       "pounds to kilograms, to a tenth"),

    # Progressive overload
    _s("const nextKg = hitAllReps ? weightKg + 2.5 : weightKg;",
       "add load only when every rep was made"),
    _s("const nextWeek = sets.map((s) => ({ ...s, weightKg: s.weightKg + 2.5 }));",
       "a new plan, every set 2.5 kg heavier; the old one untouched"),
    _s("const nextReps = Math.min(lastReps + 1, 12);",
       "double progression: one more rep, up to twelve"),
    _s("const reset = Math.round((weightKg * 0.9) / 2.5) * 2.5;",
       "ten percent off after a stall, back onto a 2.5 kg step"),
    _s("const stalled = history.slice(-3).every((s) => !s.hitAllReps);",
       "three missed sessions in a row"),

    # Calories and macros
    _s("const kcal = protein * 4 + carbs * 4 + fat * 9;",
       "Atwater: 4 kcal a gram for protein and carbs, 9 for fat"),
    _s("const proteinG = Math.round(bodyKg * gramsPerKg);",
       "a protein target from body weight and a chosen rate"),
    _s("const fatG = Math.round((kcalTarget * fatShare) / 9);",
       "the fat share of the calories, in grams"),
    _s("const carbsG = Math.round((kcalTarget - proteinG * 4 - fatG * 9) / 4);",
       "carbs fill whatever calories are left"),
    _s("const bmr = 10 * kg + 6.25 * cm - 5 * age + 5;",
       "Mifflin-St Jeor resting calories; the female form ends - 161"),
    _s("const tdee = Math.round(bmr * activityFactor);",
       "times an activity factor: a whole day's energy"),
    _s("const proteinPct = Math.round(((proteinG * 4) / kcal) * 100);",
       "protein's share of the calories, as a percent"),
    _s("const left = target - meals.reduce((sum, m) => sum + m.kcal, 0);",
       "what remains of the day's calories"),

    # Personal records
    _s("const prs = new Map();", "best lift per exercise; a Map keeps insertion order"),
    _s("if (kg > (prs.get(lift) ?? 0)) prs.set(lift, kg);",
       "a heavier lift becomes the record"),
    _s("for (const [lift, kg] of prs) console.log(`${lift}: ${kg} kg`);",
       "a Map iterates as [key, value] pairs"),
    _s("const total = ['squat', 'bench', 'deadlift'].reduce((t, l) => t + prs.get(l), 0);",
       "a powerlifting total: the best of the three lifts"),
    _s("const saved = JSON.stringify([...prs]);",
       "a Map has no JSON form of its own, so save its pairs"),
    _s("const restored = new Map(JSON.parse(saved));", "and the pairs back into a Map"),

    # The rest timer
    _s("const mm = String(Math.floor(secs / 60)).padStart(2, '0');",
       "minutes, always two digits"),
    _s("const ss = String(secs % 60).padStart(2, '0');", "seconds: 5 becomes '05'"),
    _s("console.log(`Rest ${mm}:${ss}`);", "'Rest 01:30'"),
    _s("const timer = setInterval(() => tick(--remaining), 1000);",
       "count down once a second"),
    _s("if (remaining <= 0) clearInterval(timer);", "stop at zero"),
    _s("const restS = reps <= 5 ? 180 : 90;",
       "a longer rest when the reps are low and the load heavy"),

    # The week
    _s("const split = { mon: 'push', tue: 'pull', wed: 'legs', thu: 'rest' };",
       "push, pull and legs as an object"),
    _s("const DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];",
       "the order getDay() counts in, Sunday first"),
    _s("const today = split[DAYS[new Date().getDay()]] ?? 'rest';",
       "today's session, or rest when nothing is planned"),
    _s("const trainingDays = Object.values(split).filter((f) => f !== 'rest').length;",
       "how many days have a session"),
    _s("for (const [day, focus] of Object.entries(split)) {",
       "every day with its session, in order"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSLIFTING_BLOCKS: tuple[Passage, ...] = (
    _b("const sets = [\n"
       "  { exercise: 'squat', weightKg: 100, reps: 5 },\n"
       "  { exercise: 'squat', weightKg: 100, reps: 5 },\n"
       "  { exercise: 'bench', weightKg: 70, reps: 8 },\n"
       "];\n"
       "\n"
       "const volumeOf = (list) => list.reduce((sum, s) => sum + s.weightKg * s.reps, 0);\n"
       "const byExercise = Object.groupBy(sets, (s) => s.exercise);\n"
       "\n"
       "for (const [exercise, list] of Object.entries(byExercise)) {\n"
       "  console.log(`${exercise}: ${volumeOf(list)} kg`);\n"
       "}\n"
       "console.log(`total: ${volumeOf(sets)} kg`);",
       "a session's volume, per exercise and in all"),
    _b("const epley = (weight, reps) => weight * (1 + reps / 30);\n"
       "const brzycki = (weight, reps) => (weight * 36) / (37 - reps);\n"
       "\n"
       "for (const reps of [3, 10]) {\n"
       "  const e = epley(100, reps).toFixed(1);\n"
       "  const b = brzycki(100, reps).toFixed(1);\n"
       "  console.log(`${reps} reps at 100 kg: Epley ${e}, Brzycki ${b}`);\n"
       "}",
       "Epley and Brzycki side by side"),
    _b("function platesPerSide(totalKg, barKg = 20) {\n"
       "  let left = (totalKg - barKg) / 2;\n"
       "  return [25, 20, 15, 10, 5, 2.5, 1.25].flatMap((plate) => {\n"
       "    const count = Math.floor(left / plate);\n"
       "    left -= count * plate;\n"
       "    return Array(count).fill(plate);\n"
       "  });\n"
       "}\n"
       "\n"
       "console.log(platesPerSide(100).join(' + '));\n"
       "console.log(platesPerSide(142.5).join(' + '));",
       "the plates for each side of the bar"),
    _b("const log = [\n"
       "  ['squat', 140], ['bench', 100], ['squat', 150], ['deadlift', 180], ['bench', 95],\n"
       "];\n"
       "\n"
       "const prs = new Map();\n"
       "for (const [lift, kg] of log) {\n"
       "  if (kg > (prs.get(lift) ?? 0)) prs.set(lift, kg);\n"
       "}\n"
       "\n"
       "console.log(prs);\n"
       "console.log('total', [...prs.values()].reduce((a, b) => a + b, 0));",
       "personal records kept in a Map"),
    _b("function clock(totalSeconds) {\n"
       "  const m = Math.floor(totalSeconds / 60);\n"
       "  const s = totalSeconds % 60;\n"
       "  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;\n"
       "}\n"
       "\n"
       "for (const rest of [90, 180, 45, 605]) {\n"
       "  console.log(`rest ${clock(rest)}`);\n"
       "}",
       "a rest timer's mm:ss, padded with padStart"),
    _b("function macroPlan({ kcal, bodyKg, proteinPerKg, fatShare }) {\n"
       "  const protein = Math.round(bodyKg * proteinPerKg);\n"
       "  const fat = Math.round((kcal * fatShare) / 9);\n"
       "  const carbs = Math.round((kcal - protein * 4 - fat * 9) / 4);\n"
       "  return { protein, carbs, fat };\n"
       "}\n"
       "\n"
       "const plan = macroPlan({ kcal: 2800, bodyKg: 80, proteinPerKg: 2, fatShare: 0.25 });\n"
       "console.log(plan);\n"
       "console.log(plan.protein * 4 + plan.carbs * 4 + plan.fat * 9, 'kcal');",
       "macros from a calorie target, and what rounding does to it"),
    _b("function nextSession({ weightKg, reps }, hitAllReps) {\n"
       "  if (!hitAllReps) return { weightKg, reps };\n"
       "  if (reps < 12) return { weightKg, reps: reps + 1 };\n"
       "  return { weightKg: weightKg + 2.5, reps: 8 };\n"
       "}\n"
       "\n"
       "let plan = { weightKg: 60, reps: 11 };\n"
       "for (const hit of [true, true, false, true]) {\n"
       "  plan = nextSession(plan, hit);\n"
       "  console.log(`${plan.weightKg} kg x ${plan.reps}`);\n"
       "}",
       "double progression: reps first, then weight"),
    _b("const split = {\n"
       "  mon: 'push', tue: 'pull', wed: 'legs', thu: 'rest',\n"
       "  fri: 'push', sat: 'pull', sun: 'legs',\n"
       "};\n"
       "\n"
       "const counts = {};\n"
       "for (const focus of Object.values(split)) {\n"
       "  counts[focus] = (counts[focus] ?? 0) + 1;\n"
       "}\n"
       "\n"
       "const days = Object.keys(split).filter((d) => split[d] !== 'rest');\n"
       "console.log(counts, `${days.length} training days`);",
       "a weekly split, counted"),
    _b("const roundTo = (kg, step) => Math.round(kg / step) * step;\n"
       "\n"
       "const trainingMax = 140;\n"
       "for (const pct of [65, 75, 85]) {\n"
       "  const exact = (trainingMax * pct) / 100;\n"
       "  console.log(`${pct}%: ${exact} -> ${roundTo(exact, 2.5)} kg`);\n"
       "}",
       "working sets from a training max, rounded to 2.5 kg"),
    _b("const LB_PER_KG = 2.20462;\n"
       "\n"
       "const toLb = (kg) => Math.round(kg * LB_PER_KG);\n"
       "const toKg = (lb) => Math.round((lb / LB_PER_KG) * 10) / 10;\n"
       "\n"
       "for (const kg of [60, 100, 140]) {\n"
       "  console.log(`${kg} kg = ${toLb(kg)} lb`);\n"
       "}\n"
       "console.log(`315 lb = ${toKg(315)} kg`);",
       "kilograms and pounds, both ways"),
)
