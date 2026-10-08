"""JavaScript about the planets: their data, their gravity and their orbits.

The lines are the ones a small astronomy program is made of: the eight
planets as an array of objects, weight and surface gravity, distances in
astronomical units and the time light takes to cross them, Kepler's
third law, sorting and filtering the planets, a table printed in fixed
columns, one step of an orbit simulation, and a fetch from NASA's API.

The figures are NASA's Planetary Fact Sheet, rounded as the sheet rounds
them: gravity in m/s^2, distance from the Sun, orbital period, length of
day, diameter, mass and mean temperature. Moon counts are left out on
purpose - they change as new moons are found, and a line to type should
not go out of date. The constants are the defined or standard ones: the
astronomical unit and the speed of light are exact by definition, and
the Sun's GM is known far better than G or the Sun's mass on their own.

The blocks are whole little programs that print their result, and the
tests run every one in Node and hold what it prints to an answer worked
out by hand - so they read no clock and roll no dice. The fetch is a
line only: a block that needs the network is a block that fails offline.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSPLANETS_LINES: tuple[Passage, ...] = (
    # The planets as data
    _s("const earth = { name: 'Earth', gravity: 9.8, diameterKm: 12756, dayHours: 24 };",
       "one planet as an object, with NASA's rounded figures"),
    _s("const planets = [mercury, venus, earth, mars, jupiter, saturn, uranus, neptune];",
       "all eight, in order out from the Sun"),
    _s("const names = planets.map((p) => p.name);", "just the names, in the same order"),
    _s("const { name, gravity, diameterKm } = planet;",
       "three fields out of one planet in a single line"),
    _s("const [first, second, ...others] = planets;",
       "the first two by position, the other six in an array"),
    _s("const byName = Object.fromEntries(planets.map((p) => [p.name, p]));",
       "a lookup object keyed by planet name"),
    _s("const mars = planets.find((p) => p.name === 'Mars');",
       "the Mars object, or undefined if it is not there"),
    _s("const position = planets.findIndex((p) => p.name === 'Mars') + 1;",
       "4: Mars is the fourth planet out"),
    _s("const outermost = planets.at(-1);", "Neptune: at(-1) counts from the end"),
    _s("const rocky = planets.slice(0, 4);", "Mercury to Mars, the rocky inner four"),
    _s("const giants = planets.filter((p) => p.diameterKm > 40000);",
       "the four giants, every one over 40,000 km across"),
    _s("const ringed = new Set(['Jupiter', 'Saturn', 'Uranus', 'Neptune']);",
       "every giant planet has a ring system"),
    _s("const retrograde = planets.filter((p) => p.rotationHours < 0);",
       "Venus and Uranus, which NASA lists with a negative rotation"),
    _s("Object.freeze(planets);", "lock the array; the objects inside stay editable"),

    # Gravity and weight
    _s("const weightN = massKg * planet.gravity;",
       "weight is mass times gravity, in newtons"),
    _s("const scaleKg = massKg * (planet.gravity / earth.gravity);",
       "what a bathroom scale set for Earth would show there"),
    _s("const G = 6.674e-11;", "the gravitational constant, in SI units"),
    _s("const radiusM = (planet.diameterKm / 2) * 1000;", "half the diameter, in metres"),
    _s("const surfaceG = (G * planet.massKg) / radiusM ** 2;",
       "surface gravity: G times the mass over the radius squared"),
    _s("const escapeMs = Math.sqrt((2 * G * planet.massKg) / radiusM);",
       "escape velocity, in metres per second"),
    _s("const jumpM = (speed * speed) / (2 * planet.gravity);",
       "how high a jump goes at a given take-off speed"),
    _s("const fallS = Math.sqrt((2 * heightM) / planet.gravity);",
       "seconds to fall a height, with no air in the way"),
    _s("const strongest = planets.reduce((a, b) => (b.gravity > a.gravity ? b : a));",
       "Jupiter: reduce keeps whichever pull is stronger"),
    _s("const relative = (planet.gravity / earth.gravity).toFixed(2);",
       "gravity as a fraction of Earth's, as a string"),

    # Distance and light
    _s("const AU_KM = 149_597_870.7;",
       "the astronomical unit in km, as the IAU fixed it in 2012"),
    _s("const C_KM_S = 299_792.458;", "the speed of light in km/s, exact by definition"),
    _s("const au = planet.distanceKm / AU_KM;",
       "distance from the Sun in astronomical units"),
    _s("const lightS = planet.distanceKm / C_KM_S;", "seconds for sunlight to get there"),
    _s("const lightMin = (AU_KM / C_KM_S / 60).toFixed(1);",
       "'8.3': minutes for light from the Sun to reach Earth"),
    _s("const delayMin = probeKm / C_KM_S / 60;",
       "the one-way radio delay to a probe, in minutes"),
    _s("const roundTripS = (2 * probeKm) / C_KM_S;",
       "a command out and the reply back, in seconds"),
    _s("const LY_KM = C_KM_S * 365.25 * 86_400;",
       "a light year: light speed times a Julian year"),

    # Kepler and the orbits
    _s("const years = Math.sqrt(au ** 3);",
       "Kepler's third law: the period squared equals the distance cubed"),
    _s("const periodYears = au ** 1.5;", "the same law, as a single power"),
    _s("const auFromYears = Math.cbrt(years ** 2);",
       "and backwards: the distance from the period"),
    _s("const GM_SUN = 1.32712440018e20;",
       "the Sun's G times M in SI units, known far better than G alone"),
    _s("const periodS = 2 * Math.PI * Math.sqrt(aM ** 3 / GM_SUN);",
       "the full law: a period in seconds from a distance in metres"),
    _s("const orbitMs = Math.sqrt(GM_SUN / rM);", "the speed on a circular orbit, in m/s"),
    _s("const ageThere = (ageYears * 365.25) / planet.periodDays;",
       "your age, counted in that planet's years"),
    _s("const laps = Math.floor(days / planet.periodDays);",
       "complete orbits in that many Earth days"),
    _s("const sols = missionHours / 24.7;", "Mars days, called sols, last about 24.7 hours"),

    # Sorting and filtering
    _s("planets.sort((a, b) => a.distanceKm - b.distanceKm);",
       "nearest the Sun first; sort changes the array itself"),
    _s("const bySize = planets.toSorted((a, b) => b.diameterKm - a.diameterKm);",
       "a sorted copy, biggest first; the original stays put"),
    _s("const alphabetical = names.toSorted((a, b) => a.localeCompare(b));",
       "the names from A to Z"),
    _s("const belowZero = planets.filter((p) => p.meanTempC < 0);",
       "every planet colder than freezing on average"),
    _s("const shortestDay = planets.reduce((a, b) => (b.dayHours < a.dayHours ? b : a));",
       "Jupiter, whose day is under ten hours"),
    _s("const allLarge = planets.every((p) => p.diameterKm > 4000);",
       "true: even Mercury is 4,879 km across"),
    _s("const sides = Object.groupBy(planets, (p) => (p.au < 2 ? 'inner' : 'outer'));",
       "ES2024: the planets split into lists by a key"),
    _s("const totalKg = planets.reduce((sum, p) => sum + p.massKg, 0);",
       "the mass of all eight, added up"),
    _s("const jupiterShare = jupiter.massKg / totalKg;",
       "about 0.71: Jupiter outweighs the other seven put together"),

    # Printing a table
    _s("console.table(planets, ['name', 'gravity', 'dayHours']);",
       "a quick table in the console, chosen columns only"),
    _s("const row = `${p.name.padEnd(8)}${p.gravity.toFixed(1).padStart(6)}`;",
       "names to the left, numbers lined up on the right"),
    _s("const size = p.diameterKm.toLocaleString('en-US');", "12756 becomes '12,756'"),
    _s("const mass = p.massKg.toExponential(2);",
       "'5.97e+24': scientific notation for a huge number"),
    _s("console.log(`${p.name}: ${au.toFixed(2)} AU`);",
       "two decimal places, inside a template"),
    _s("const fmt = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1 });",
       "one formatter, made once and reused for every number"),
    _s("const kelvin = p.meanTempC + 273.15;", "Celsius to kelvin"),

    # One step of an orbit
    _s("const r = Math.hypot(body.x, body.y);",
       "the distance from the Sun, which sits at the origin"),
    _s("const accel = GM / (r * r);", "gravity weakens with the square of the distance"),
    _s("body.vx -= ((accel * body.x) / r) * dt;", "a pull towards the Sun: the x part"),
    _s("body.vy -= ((accel * body.y) / r) * dt;", "and the y part"),
    _s("body.x += body.vx * dt;",
       "then move with the new velocity: semi-implicit Euler"),
    _s("const angle = (2 * Math.PI * t) / planet.periodDays;",
       "how far round a circular orbit after t days"),
    _s("const pos = { x: au * Math.cos(angle), y: au * Math.sin(angle) };",
       "the point on that circle"),

    # From the network
    _s("const res = await fetch(`https://api.nasa.gov/planetary/apod?api_key=${apiKey}`);",
       "NASA's Astronomy Picture of the Day API"),
    _s("const { title, url, explanation } = await res.json();",
       "the picture's title, its address and NASA's caption"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSPLANETS_BLOCKS: tuple[Passage, ...] = (
    _b("const gravity = { Mercury: 3.7, Venus: 8.9, Earth: 9.8, Mars: 3.7, Jupiter: 23.1 };\n"
       "\n"
       "function scaleReading(kg, planet) {\n"
       "  return (kg * gravity[planet]) / gravity.Earth;\n"
       "}\n"
       "\n"
       "for (const planet of ['Venus', 'Mars', 'Jupiter']) {\n"
       "  console.log(`${planet}: ${scaleReading(70, planet).toFixed(1)} kg`);\n"
       "}",
       "weight elsewhere, as a scale set for Earth would show it"),
    _b("const C_KM_S = 299_792.458;\n"
       "\n"
       "function lightTime(distanceKm) {\n"
       "  const total = Math.round(distanceKm / C_KM_S);\n"
       "  const m = Math.floor(total / 60);\n"
       "  const s = total % 60;\n"
       "  return `${m} min ${s} s`;\n"
       "}\n"
       "\n"
       "console.log('Sun to Earth:', lightTime(149_597_870.7));\n"
       "console.log('Sun to Mars:', lightTime(228.0e6));",
       "how long sunlight takes to arrive"),
    _b("const AU_KM = 149_597_870.7;\n"
       "const distanceKm = { Earth: 149.6e6, Mars: 228.0e6, Jupiter: 778.5e6 };\n"
       "\n"
       "for (const [name, km] of Object.entries(distanceKm)) {\n"
       "  const au = km / AU_KM;\n"
       "  const years = Math.sqrt(au ** 3);\n"
       "  console.log(`${name}: ${au.toFixed(2)} AU, ${years.toFixed(2)} years`);\n"
       "}",
       "Kepler's third law: the year from the distance"),
    _b("const planets = [\n"
       "  { name: 'Mars', diameterKm: 6792 },\n"
       "  { name: 'Jupiter', diameterKm: 142984 },\n"
       "  { name: 'Mercury', diameterKm: 4879 },\n"
       "  { name: 'Earth', diameterKm: 12756 },\n"
       "];\n"
       "\n"
       "const bySize = planets.toSorted((a, b) => b.diameterKm - a.diameterKm);\n"
       "console.log(bySize.map((p) => p.name).join(' > '));\n"
       "console.log(planets[0].name, bySize.at(-1).name);",
       "a sorted copy, with the original left alone"),
    _b("const rows = [\n"
       "  ['Mercury', 3.7, 4879],\n"
       "  ['Venus', 8.9, 12104],\n"
       "  ['Earth', 9.8, 12756],\n"
       "  ['Mars', 3.7, 6792],\n"
       "];\n"
       "\n"
       "console.log('Planet'.padEnd(8) + 'g'.padStart(6) + 'km'.padStart(9));\n"
       "for (const [name, g, km] of rows) {\n"
       "  const size = km.toLocaleString('en-US');\n"
       "  console.log(name.padEnd(8) + g.toFixed(1).padStart(6) + size.padStart(9));\n"
       "}",
       "a table in fixed columns with padEnd and padStart"),
    _b("function step(body, GM, dt) {\n"
       "  const r = Math.hypot(body.x, body.y);\n"
       "  const a = GM / (r * r);\n"
       "  body.vx -= ((a * body.x) / r) * dt;\n"
       "  body.vy -= ((a * body.y) / r) * dt;\n"
       "  body.x += body.vx * dt;\n"
       "  body.y += body.vy * dt;\n"
       "}\n"
       "\n"
       "const probe = { x: 1, y: 0, vx: 0, vy: 1 };\n"
       "for (let i = 0; i < 2; i++) step(probe, 1, 0.1);\n"
       "console.log(probe.x.toFixed(3), probe.y.toFixed(3));",
       "two steps of an orbit, by semi-implicit Euler"),
    _b("const G = 6.674e-11;\n"
       "\n"
       "function surfaceGravity(massKg, diameterKm) {\n"
       "  const r = (diameterKm / 2) * 1000;\n"
       "  return (G * massKg) / r ** 2;\n"
       "}\n"
       "\n"
       "console.log('Earth', surfaceGravity(5.97e24, 12756).toFixed(2));\n"
       "console.log('Mars', surfaceGravity(0.642e24, 6792).toFixed(2));",
       "surface gravity from a planet's mass and size"),
    _b("const meanTempC = { Mercury: 167, Venus: 464, Earth: 15, Mars: -65, Jupiter: -110 };\n"
       "\n"
       "const belowFreezing = Object.entries(meanTempC)\n"
       "  .filter(([, c]) => c < 0)\n"
       "  .map(([name, c]) => `${name} ${Math.round(c + 273.15)} K`);\n"
       "\n"
       "console.log(belowFreezing.join(', '));\n"
       "console.log(Object.keys(meanTempC).find((name) => meanTempC[name] > 400));",
       "filter, map and find over mean temperatures"),
    _b("const periodDays = { Mercury: 88.0, Venus: 224.7, Mars: 687.0, Jupiter: 4331 };\n"
       "\n"
       "function ageOn(planet, earthYears) {\n"
       "  return (earthYears * 365.25) / periodDays[planet];\n"
       "}\n"
       "\n"
       "for (const planet of Object.keys(periodDays)) {\n"
       "  console.log(`${planet}: ${ageOn(planet, 30).toFixed(1)}`);\n"
       "}",
       "a thirty-year-old's age in other planets' years"),
    _b("const gravity = { Mercury: 3.7, Venus: 8.9, Earth: 9.8, Mars: 3.7, Saturn: 9.0 };\n"
       "\n"
       "const byGravity = new Map();\n"
       "for (const [name, g] of Object.entries(gravity)) {\n"
       "  byGravity.set(g, [...(byGravity.get(g) ?? []), name]);\n"
       "}\n"
       "\n"
       "for (const [g, names] of byGravity) {\n"
       "  if (names.length > 1) console.log(`${names.join(' and ')}: ${g} m/s^2`);\n"
       "}\n"
       "console.log(byGravity.size, 'different values');",
       "planets that share a gravity, grouped in a Map"),
)
