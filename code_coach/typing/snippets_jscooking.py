"""JavaScript about cooking and recipes.

The lines are the ones a kitchen helper is made of: scaling a recipe to a
different number of servings, converting cups and spoons and ounces,
oven temperatures, a cooking time as hours and minutes, a clock time
counted back from when dinner is served, shopping lists merged with Map
and reduce, the cost of a serving, and money shown with Intl.NumberFormat.

The conversion factors are the usual kitchen ones: a US cup is 236.588 ml,
a tablespoon 14.787 ml and a teaspoon 4.929 ml, an ounce is 28.3495 g, and
a stick of butter is 113 g. UK gas marks run from 140 C (mark 1) to 240 C
(mark 9). Chicken is safe at an internal 74 C (165 F).

The blocks are whole little programs that print their result, and the
tests run every one in Node and hold what it prints to an answer worked
out by hand - so they read no clock and roll no dice, and every
fractional result goes through toFixed or Math.round so that the last
digit does not depend on how floating point happens to round.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSCOOKING_LINES: tuple[Passage, ...] = (
    # Scaling a recipe
    _s("const factor = wantedServings / recipe.servings;", "how many times bigger the batch is"),
    _s("const scaled = recipe.items.map((i) => ({ ...i, qty: i.qty * factor }));",
       "a new list; the original recipe is untouched"),
    _s("const eggs = Math.ceil(2 * factor);", "you can't use half an egg, so round up"),
    _s("const nearestQuarter = Math.round(qty * 4) / 4;",
       "tidy 0.3333 cups into something a measuring cup shows"),
    _s("const perServing = recipe.items.map((i) => i.qty / recipe.servings);",
       "the amount for one person"),
    _s("const half = qty / 2;", "halving is the easy case"),
    _s("const text = `${qty} ${unit}${qty === 1 ? '' : 's'} ${name}`;",
       "'1 cup flour', but '2 cups flour'"),
    _s("const label = qty === 1 ? 'egg' : 'eggs';", "the singular and the plural"),
    _s("const price = (4.5).toFixed(2);", "'4.50': toFixed gives a string, not a number"),

    # Units
    _s("const ML_PER_CUP = 236.588;", "a US cup in millilitres"),
    _s("const ml = cups * ML_PER_CUP;", "cups to millilitres"),
    _s("const cups = ml / ML_PER_CUP;", "and back"),
    _s("const tsp = tbsp * 3;", "three teaspoons to a tablespoon"),
    _s("const tbspMl = tbsp * 14.787;", "a tablespoon in millilitres"),
    _s("const grams = ounces * 28.3495;", "ounces to grams"),
    _s("const ounces = (grams / 28.3495).toFixed(1);", "grams to ounces, one decimal"),
    _s("const pounds = grams / 453.592;", "grams to pounds"),
    _s("const flourG = cups * 120;", "a cup of plain flour weighs about 120 g"),
    _s("const butterG = sticks * 113;", "a US stick of butter is 113 g"),
    _s("const litres = (ml / 1000).toFixed(2);", "millilitres to litres"),
    _s("const toMl = (qty, unit) => qty * ML[unit];", "one lookup table for every unit"),

    # Temperature
    _s("const celsius = ((fahrenheit - 32) * 5) / 9;", "oven degrees, Fahrenheit to Celsius"),
    _s("const fahrenheit = (celsius * 9) / 5 + 32;", "and the other way"),
    _s("const fan = celsius - 20;", "a fan oven runs about 20 degrees cooler"),
    _s("const nearest5 = Math.round(celsius / 5) * 5;", "ovens are set in steps of five"),
    _s("const GAS = [140, 150, 170, 180, 190, 200, 220, 230, 240];",
       "gas marks 1 to 9, in Celsius"),
    _s("const gasMark = GAS.indexOf(180) + 1;", "180 C is gas mark 4"),
    _s("const done = internalC >= 74;", "chicken is safe at 74 C inside"),
    _s("const hot = `${Math.round(celsius)} C / ${Math.round(fahrenheit)} F`;",
       "both scales in one string"),

    # Time
    _s("const hours = Math.floor(minutes / 60);", "whole hours"),
    _s("const mins = minutes % 60;", "what is left over"),
    _s("const label = `${hours} h ${mins} min`;", "'1 h 32 min'"),
    _s("const total = prepMin + cookMin + restMin;", "the whole job, start to finish"),
    _s("const cookMin = Math.round(weightKg * 45 + 20);",
       "a roast's time: so many minutes a kilo, plus a bit"),
    _s("const startAt = serveAt - cookMin - restMin;", "count backwards from dinner"),
    _s("const hh = String(Math.floor(t / 60)).padStart(2, '0');", "7 becomes '07'"),
    _s("const mm = String(t % 60).padStart(2, '0');", "5 becomes '05'"),
    _s("const clock = `${hh}:${mm}`;", "HH:MM"),
    _s("const wrapped = ((t % 1440) + 1440) % 1440;",
       "1440 minutes in a day; this stays in range even when t is negative"),
    _s("const timer = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;",
       "a countdown reads 04:05"),
    _s("const secs = minutes * 60;", "minutes to seconds for a timer"),

    # Lists, Maps and reduce
    _s("const pantry = new Map([['flour', 500], ['sugar', 200]]);",
       "what is in the cupboard, in grams"),
    _s("pantry.set('flour', (pantry.get('flour') ?? 0) + 250);",
       "add to a total, starting from zero if it is new"),
    _s("const tally = (m, i) => m.set(i.name, (m.get(i.name) ?? 0) + i.qty);",
       "add to an item's total, starting from zero if it is new"),
    _s("const merged = items.reduce(tally, new Map());",
       "one shopping list from many recipes"),
    _s("const need = [...list].filter(([item, qty]) => (pantry.get(item) ?? 0) < qty);",
       "everything the cupboard can't cover"),
    _s("const sorted = [...merged].sort(([a], [b]) => a.localeCompare(b));",
       "alphabetical by item, the way a shop is laid out"),
    _s("const lines = [...merged].map(([n, q]) => `${q} x ${n}`);", "'600 x milk'"),
    _s("const unique = [...new Set(recipes.flatMap((r) => r.items.map((i) => i.name)))];",
       "each ingredient once, in the order first seen"),
    _s("const grouped = Object.groupBy(items, (i) => i.aisle);",
       "the list split up by aisle"),
    _s("const total = items.reduce((sum, i) => sum + i.qty, 0);",
       "the 0 is the starting value, and it matters"),
    _s("const hasNuts = recipe.items.some((i) => i.name === 'peanut');",
       "does any ingredient match?"),
    _s("const vegetarian = recipes.filter((r) => r.vegetarian);", "keep the meat-free ones"),
    _s("const byTime = recipes.toSorted((a, b) => a.minutes - b.minutes);",
       "quickest first; a sorted copy"),
    _s("const quickest = recipes.reduce((a, b) => (b.minutes < a.minutes ? b : a));",
       "the recipe that takes the least time"),

    # Money and nutrition
    _s("const cost = (price * used) / packSize;", "the price of just the part you use"),
    _s("const perPortion = totalCost / servings;", "cost per serving"),
    _s("const cents = Math.round(price * 100);", "money counted in whole cents"),
    _s("const rounded = Math.round(perPortion * 100) / 100;", "to the nearest cent"),
    _s("const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });",
       "one formatter, reused"),
    _s("const shown = usd.format(1234.5);", "'$1,234.50'"),
    _s("const eur = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });",
       "the same number as 1.234,50 EUR in Germany"),
    _s("const kcal = 4 * (protein + carbs) + 9 * fat;", "calories from the macros"),
    _s("const fatShare = Math.round(((fat * 9) / kcal) * 100);",
       "the percentage of calories from fat"),
    _s("const row = `${name.padEnd(10)}${qty.toString().padStart(6)}`;",
       "a recipe card that lines up"),
    _s("console.log(`${name}: ${qty.toFixed(1)} ${unit}`);", "one ingredient per line"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSCOOKING_BLOCKS: tuple[Passage, ...] = (
    _b(r"""const recipe = { servings: 4, flourG: 250, milkMl: 300, eggs: 2, saltTsp: 0.5 };

function scale(r, servings) {
  const k = servings / r.servings;
  const out = { servings };
  for (const key of ['flourG', 'milkMl', 'eggs', 'saltTsp']) out[key] = r[key] * k;
  return out;
}

console.log(scale(recipe, 6));
console.log(scale(recipe, 3).eggs, Math.ceil(scale(recipe, 3).eggs));""",
       "scaling a recipe to a different number of servings"),
    _b(r"""const ML = { cup: 236.588, tbsp: 14.787, tsp: 4.929 };
const G_PER_OZ = 28.3495;

const toMl = (qty, unit) => qty * ML[unit];
const ozToG = (oz) => oz * G_PER_OZ;

console.log(toMl(1.5, 'cup').toFixed(0), toMl(3, 'tsp').toFixed(1));
console.log(Math.round(ozToG(8)), (500 / G_PER_OZ).toFixed(2));""",
       "kitchen unit conversions from one table"),
    _b(r"""const toC = (f) => ((f - 32) * 5) / 9;
const toF = (c) => (c * 9) / 5 + 32;

for (const f of [250, 350, 425, 475]) {
  console.log(`${f}F = ${Math.round(toC(f))}C`);
}
console.log(toF(180), toF(-40), toC(212));""",
       "oven temperatures in both scales"),
    _b(r"""function hm(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m} min`;
  return m === 0 ? `${h} h` : `${h} h ${m} min`;
}

const roastMin = (kg) => Math.round(kg * 40 + 20);
for (const kg of [1, 1.8, 2.5, 4.2]) console.log(kg, 'kg', hm(roastMin(kg)));""",
       "a roasting time as hours and minutes"),
    _b(r"""function clock(totalMin) {
  const t = ((totalMin % 1440) + 1440) % 1440;
  const h = String(Math.floor(t / 60)).padStart(2, '0');
  return `${h}:${String(t % 60).padStart(2, '0')}`;
}

const dinner = 19 * 60 + 30;
const steps = [['serve', 0], ['rest', 15], ['roast', 105], ['preheat', 135]];
for (const [what, before] of steps) console.log(clock(dinner - before), what);
console.log(clock(30 - 90));""",
       "a timeline counted back from dinner, with a wrap past midnight"),
    _b(r"""const recipes = [
  { name: 'pancakes', items: [['flour', 200], ['milk', 300], ['egg', 2]] },
  { name: 'omelette', items: [['egg', 3], ['milk', 50]] },
  { name: 'crepes', items: [['flour', 125], ['milk', 250], ['egg', 1]] },
];

const list = recipes
  .flatMap((r) => r.items)
  .reduce((m, [item, qty]) => m.set(item, (m.get(item) ?? 0) + qty), new Map());
console.log(list);
console.log([...list.keys()].join(', '), list.get('egg'));""",
       "one shopping list merged from three recipes"),
    _b(r"""const ingredients = [
  { name: 'rice', price: 2.4, perPack: 1000, used: 300 },
  { name: 'chicken', price: 7.4, perPack: 1000, used: 450 },
  { name: 'peas', price: 1.8, perPack: 500, used: 100 },
];

const cost = (i) => (i.price * i.used) / i.perPack;
const total = ingredients.reduce((s, i) => s + cost(i), 0);
console.log(ingredients.map((i) => cost(i).toFixed(2)).join(' '));
console.log(total.toFixed(2), (total / 4).toFixed(2));""",
       "what a dish costs, and what one serving costs"),
    _b(r"""const usd = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const items = [['flour', 2.49, 2], ['eggs', 3.99, 1], ['butter', 4.75, 3]];

let total = 0;
for (const [name, price, qty] of items) {
  const line = price * qty;
  total += line;
  console.log(`${name.padEnd(8)}${qty}x ${usd.format(line).padStart(8)}`);
}
console.log(`${'total'.padEnd(8)}   ${usd.format(total).padStart(8)}`);""",
       "a receipt with Intl.NumberFormat currency"),
    _b(r"""const recipes = [
  { name: 'Ragu', mins: 180, vegetarian: false },
  { name: 'Salad', mins: 10, vegetarian: true },
  { name: 'Curry', mins: 45, vegetarian: true },
  { name: 'Risotto', mins: 35, vegetarian: true },
];

const quick = recipes.filter((r) => r.vegetarian && r.mins <= 45);
console.log(quick.map((r) => r.name).join(', '));
const byTime = recipes.toSorted((a, b) => a.mins - b.mins);
console.log(byTime.map((r) => `${r.name} ${r.mins}m`).join(' < '));
console.log(recipes.some((r) => r.mins > 120), recipes.every((r) => r.mins > 10));""",
       "filtering, sorting and testing a list of recipes"),
    _b(r"""const KCAL = { protein: 4, carbs: 4, fat: 9 };
const meal = { protein: 32, carbs: 45, fat: 14 };

const kcal = Object.entries(meal).reduce((sum, [k, g]) => sum + g * KCAL[k], 0);
console.log(kcal, `${Math.round(((meal.fat * 9) / kcal) * 100)}% from fat`);
const perServing = (total, servings) => Math.round(total / servings);
console.log(perServing(kcal * 6, 4), perServing(2000, 3));""",
       "calories from the macros, and a big batch shared out"),
)
