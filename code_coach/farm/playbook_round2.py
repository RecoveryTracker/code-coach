"""Playbook tips on the rest of the research tree: dictionaries, utilities, timing, costs, hats, imports, simulation, layouts, dinosaurs, mazes (see playbook.py).

Nine groups, for the parts of the tree the first tips barely touch: dictionaries
as memory, min/max/random and the clocks, get_cost and unlock(), hats, files
that import each other, simulate() as a way to choose, planting layouts for
companions, long dinosaur runs, and reusing a maze. Every snippet is a helper
and one example call, and is run for real in tests/test_farm_playbook_round2.py.

What is said here is what this clone does, and in a few places that is not the
whole game:

* Only the dinosaur hat does anything; the other hats are costumes.
* A plant's wish (get_companion) is chosen at random when it is planted, so a
  layout can only improve the odds; the tips count the lucky ones.
* A reused maze only ever gains passages, and its treasure moves at most 300
  times.
* A file snippet (the Imports group) is the helper file; the comment on top
  says what main writes. Import is not in `needs`, because the helper file
  itself imports nothing and has to run on its own.
"""

from __future__ import annotations

from code_coach.farm.playbook import Entry, _entry

ENTRIES: tuple[Entry, ...] = (
    # ── Dictionaries ────────────────────────────────────────────────────
    _entry(
        "dict-tally", "Dictionaries", "Tally the harvest by crop and name the busiest",
        "A dictionary keeps a count for each key you meet. This harvests what is ripe and adds "
        "one to the count under the kind of thing that stood there, and busiest() walks the "
        "dictionary for the biggest count. Ask `kind in tally` before you read a count that "
        "may not be there yet.",
        ("Expand", "Speed", "Senses", "Debug", "Dictionaries", "Operators", "Variables",
         "Functions"),
        python="""
def harvest_field():
    tally = {}
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            kind = get_entity_type()
            if can_harvest():
                harvest()
                if kind in tally:
                    tally[kind] += 1
                else:
                    tally[kind] = 1
            move(North)
        move(East)
    return tally

def busiest(tally):
    best = None
    for kind in tally:
        if best == None or tally[kind] > tally[best]:
            best = kind
    return best

tally = harvest_field()
best = busiest(tally)
if best == None:
    quick_print("nothing was ripe")
else:
    quick_print("busiest:", best, tally[best])
""",
        javascript="""
function harvestField() {
  const tally = new Map();
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const kind = getEntityType();
      if (canHarvest()) {
        harvest();
        tally.set(kind, tally.has(kind) ? tally.get(kind) + 1 : 1);
      }
      move(North);
    }
    move(East);
  }
  return tally;
}

function busiest(tally) {
  let best = null;
  for (const kind of tally.keys()) {
    if (best === null || tally.get(kind) > tally.get(best)) best = kind;
  }
  return best;
}

const tally = harvestField();
const best = busiest(tally);
if (best === null) {
  quickPrint("nothing was ripe");
} else {
  quickPrint("busiest:", best, tally.get(best));
}
""",
        dart="""
Map<Entities?, int> harvestField() {
  final tally = <Entities?, int>{};
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final kind = getEntityType();
      if (canHarvest()) {
        harvest();
        tally[kind] = tally.containsKey(kind) ? tally[kind]! + 1 : 1;
      }
      move(north);
    }
    move(east);
  }
  return tally;
}

Entities? busiest(Map<Entities?, int> tally) {
  Entities? best;
  for (final kind in tally.keys) {
    if (best == null || tally[kind]! > tally[best]!) {
      best = kind;
    }
  }
  return best;
}

void main() {
  final tally = harvestField();
  final best = busiest(tally);
  if (best == null) {
    quickPrint('nothing was ripe');
  } else {
    quickPrint('busiest: $best ${tally[best]}');
  }
}
""",
    ),
    _entry(
        "dict-blueprint", "Dictionaries", "Keep a blueprint and repair the field from it",
        "A dictionary can remember what belongs where. Number each square x * n + y, store "
        "the crop that should stand there, and repair() sweeps the field and plants again "
        "wherever the plan and the field disagree - after a harvest, or after a pumpkin dies. "
        "A square that already holds the right crop costs one question, not a planting.",
        ("Expand", "Speed", "Plant", "Senses", "Dictionaries", "Operators", "Variables",
         "Functions"),
        python="""
def make_plan(crop):
    plan = {}
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if (x + y) % 2 == 0:          # a checkerboard: every other square
                plan[x * n + y] = crop
    return plan

def repair(plan):
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            spot = x * n + y
            if spot in plan and get_entity_type() != plan[spot]:
                plant(plan[spot])
            move(North)
        move(East)

plan = make_plan(Entities.Bush)
repair(plan)
""",
        javascript="""
function makePlan(crop) {
  const plan = new Map();
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if ((x + y) % 2 === 0) plan.set(x * n + y, crop); // a checkerboard: every other square
    }
  }
  return plan;
}

function repair(plan) {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const spot = x * n + y;
      if (plan.has(spot) && getEntityType() !== plan.get(spot)) plant(plan.get(spot));
      move(North);
    }
    move(East);
  }
}

const plan = makePlan(Entities.Bush);
repair(plan);
""",
        dart="""
Map<int, Entities> makePlan(Entities crop) {
  final plan = <int, Entities>{};
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if ((x + y) % 2 == 0) { // a checkerboard: every other square
        plan[x * n + y] = crop;
      }
    }
  }
  return plan;
}

void repair(Map<int, Entities> plan) {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final spot = x * n + y;
      if (plan.containsKey(spot) && getEntityType() != plan[spot]) {
        plant(plan[spot]!);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  final plan = makePlan(Entities.bush);
  repair(plan);
}
""",
    ),
    _entry(
        "dict-barn-diff", "Dictionaries", "What did that pass bring in? Compare two snapshots",
        "num_items() reads one item. To see what a pass earned, copy the barn into a "
        "dictionary before and again after, and subtract. The list says which items to "
        "watch; this mows a field of grass and bushes and prints the change in hay and wood.",
        ("Expand", "Speed", "Senses", "Debug", "Dictionaries", "Lists", "Operators",
         "Variables", "Functions"),
        python="""
WATCH = [Items.Hay, Items.Wood]

def snapshot():
    barn = {}
    for item in WATCH:
        barn[item] = num_items(item)
    return barn

def mow():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if can_harvest():
                harvest()
            move(North)
        move(East)

before = snapshot()
mow()
after = snapshot()
for item in WATCH:
    quick_print(item, "+", after[item] - before[item])
""",
        javascript="""
const WATCH = [Items.Hay, Items.Wood];

function snapshot() {
  const barn = new Map();
  for (const item of WATCH) barn.set(item, numItems(item));
  return barn;
}

function mow() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (canHarvest()) harvest();
      move(North);
    }
    move(East);
  }
}

const before = snapshot();
mow();
const after = snapshot();
for (const item of WATCH) {
  quickPrint(item, "+", after.get(item) - before.get(item));
}
""",
        dart="""
const watch = [Items.hay, Items.wood];

Map<Items, num> snapshot() {
  final barn = <Items, num>{};
  for (final item in watch) {
    barn[item] = numItems(item);
  }
  return barn;
}

void mow() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (canHarvest()) {
        harvest();
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  final before = snapshot();
  mow();
  final after = snapshot();
  for (final item in watch) {
    quickPrint('$item + ${after[item]! - before[item]!}');
  }
}
""",
    ),
    # ── Utilities and Timing ────────────────────────────────────────────
    _entry(
        "util-extremes", "Utilities and Timing", "The biggest and smallest flower with max() and min()",
        "min() and max() take several values or one whole list, so there is no loop to write: "
        "scan the field, collect each flower's petals in a list, and ask for the extremes. "
        "Each call costs one tick for every value after the first. abs(x) drops a minus sign, "
        "and random() comes with them.",
        ("Expand", "Speed", "Sunflowers", "Utilities", "Debug", "Lists", "Operators",
         "Variables", "Functions"),
        python="""
def all_petals():
    petals = []
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            p = measure()
            if p != None:
                petals.append(p)
            move(North)
        move(East)
    return petals

petals = all_petals()
if len(petals) > 0:
    most = max(petals)
    fewest = min(petals)
    quick_print("most:", most, "fewest:", fewest, "spread:", most - fewest)
""",
        javascript="""
function allPetals() {
  const petals = [];
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const p = measure();
      if (p !== null) petals.push(p);
      move(North);
    }
    move(East);
  }
  return petals;
}

const petals = allPetals();
if (petals.length > 0) {
  const most = max(petals);
  const fewest = min(petals);
  quickPrint("most:", most, "fewest:", fewest, "spread:", most - fewest);
}
""",
        dart="""
List<int> allPetals() {
  final petals = <int>[];
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final int? p = measure();
      if (p != null) {
        petals.add(p);
      }
      move(north);
    }
    move(east);
  }
  return petals;
}

void main() {
  final petals = allPetals();
  if (petals.isNotEmpty) {
    final most = max(petals);
    final fewest = min(petals);
    quickPrint('most: $most fewest: $fewest spread: ${most - fewest}');
  }
}
""",
    ),
    _entry(
        "util-random-share", "Utilities and Timing", "Plant a random share of the field",
        "random() gives a number from 0 up to, but not including, 1, and asking costs a tick. "
        "`random() < 0.25` is true about a quarter of the time, so this plants roughly a "
        "quarter of the squares with bushes and leaves the rest as grass. Share 0 plants "
        "nothing and anything above 1 plants every square.",
        ("Expand", "Speed", "Plant", "Utilities", "Operators", "Variables", "Functions"),
        python="""
def plant_share(share):
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if random() < share:
                plant(Entities.Bush)
            move(North)
        move(East)

plant_share(0.25)
""",
        javascript="""
function plantShare(share) {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (random() < share) plant(Entities.Bush);
      move(North);
    }
    move(East);
  }
}

plantShare(0.25);
""",
        dart="""
void plantShare(double share) {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (random() < share) {
        plant(Entities.bush);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  plantShare(0.25);
}
""",
    ),
    _entry(
        "timing-rate", "Utilities and Timing", "How fast is it? Hay a second, from the clocks",
        "get_time() is the game seconds since the farm began and get_tick_count() the ticks "
        "since your program started; neither costs anything to ask. Read both and the hay "
        "before a few laps and after, and the difference is a rate you can compare between "
        "versions of your code. Use quick_print for the report: print() would add a second.",
        ("Expand", "Speed", "Senses", "Timing", "Debug", "Operators", "Variables", "Functions"),
        python="""
def mow():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if can_harvest():
                harvest()
            move(North)
        move(East)

def measure_laps(laps):
    start = get_time()
    first_tick = get_tick_count()
    hay = num_items(Items.Hay)
    for i in range(laps):
        mow()
    seconds = get_time() - start
    gained = num_items(Items.Hay) - hay
    quick_print(gained, "hay in", seconds, "seconds and", get_tick_count() - first_tick, "ticks")
    quick_print("hay a second:", gained / seconds)

measure_laps(3)
""",
        javascript="""
function mow() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (canHarvest()) harvest();
      move(North);
    }
    move(East);
  }
}

function measureLaps(laps) {
  const start = getTime();
  const firstTick = getTickCount();
  const hay = numItems(Items.Hay);
  for (const i of range(laps)) mow();
  const seconds = getTime() - start;
  const gained = numItems(Items.Hay) - hay;
  quickPrint(gained, "hay in", seconds, "seconds and", getTickCount() - firstTick, "ticks");
  quickPrint("hay a second:", gained / seconds);
}

measureLaps(3);
""",
        dart="""
void mow() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (canHarvest()) {
        harvest();
      }
      move(north);
    }
    move(east);
  }
}

void measureLaps(int laps) {
  final start = getTime();
  final firstTick = getTickCount();
  final hay = numItems(Items.hay);
  for (final i in range(laps)) {
    mow();
  }
  final seconds = getTime() - start;
  final gained = numItems(Items.hay) - hay;
  quickPrint('$gained hay in $seconds seconds and ${getTickCount() - firstTick} ticks');
  quickPrint('hay a second: ${gained / seconds}');
}

void main() {
  measureLaps(3);
}
""",
    ),
    _entry(
        "timing-deadline", "Utilities and Timing", "Work until a deadline with get_time()",
        "A loop can stop on the clock instead of on a count: note the time to stop at, then "
        "keep working while get_time() is earlier. The check is free, so the loop ends within "
        "one move of the deadline. Here the drone patrols its column for ten game seconds, "
        "harvesting what is ripe, and reports how many harvests it made.",
        ("Loops", "Expand", "Speed", "Timing", "Debug", "Operators", "Variables", "Functions"),
        python="""
def work_for(seconds):
    stop = get_time() + seconds
    harvests = 0
    while get_time() < stop:
        if can_harvest():
            harvest()
            harvests += 1
        move(North)
    return harvests

quick_print("harvested", work_for(10), "times in ten seconds")
""",
        javascript="""
function workFor(seconds) {
  const stop = getTime() + seconds;
  let harvests = 0;
  while (getTime() < stop) {
    if (canHarvest()) {
      harvest();
      harvests += 1;
    }
    move(North);
  }
  return harvests;
}

quickPrint("harvested", workFor(10), "times in ten seconds");
""",
        dart="""
int workFor(int seconds) {
  final stop = getTime() + seconds;
  var harvests = 0;
  while (getTime() < stop) {
    if (canHarvest()) {
      harvest();
      harvests += 1;
    }
    move(north);
  }
  return harvests;
}

void main() {
  quickPrint('harvested ${workFor(10)} times in ten seconds');
}
""",
    ),
    # ── Costs ───────────────────────────────────────────────────────────
    _entry(
        "costs-shortfall", "Costs", "What is missing for the next upgrade?",
        "get_cost(Unlocks.Speed) is a dictionary of what the next level costs, from item to "
        "amount, and it follows your upgrades. Compare each item with num_items() and keep "
        "only the ones that fall short: an empty answer means you can afford it - or, for an "
        "unlock at its top level, whose cost is an empty dictionary, that nothing is left to "
        "buy.",
        ("Expand", "Speed", "Senses", "Costs", "Debug", "Dictionaries", "Operators",
         "Variables", "Functions"),
        python="""
def shortfall(thing):
    cost = get_cost(thing)
    missing = {}
    for item in cost:
        if num_items(item) < cost[item]:
            missing[item] = cost[item] - num_items(item)
    return missing

missing = shortfall(Unlocks.Speed)
if len(missing) == 0:
    quick_print("you can afford it")
else:
    for item in missing:
        quick_print("short of", missing[item], item)
""",
        javascript="""
function shortfall(thing) {
  const cost = getCost(thing);
  const missing = new Map();
  for (const item in cost) {
    if (numItems(item) < cost[item]) missing.set(item, cost[item] - numItems(item));
  }
  return missing;
}

const missing = shortfall(Unlocks.Speed);
if (missing.size === 0) {
  quickPrint("you can afford it");
} else {
  for (const [item, short] of missing) {
    quickPrint("short of", short, item);
  }
}
""",
        dart="""
Map<Items, num> shortfall(Object thing) {
  final cost = getCost(thing)!;
  final missing = <Items, num>{};
  for (final item in cost.keys) {
    if (numItems(item) < cost[item]!) {
      missing[item] = cost[item]! - numItems(item);
    }
  }
  return missing;
}

void main() {
  final missing = shortfall(Unlocks.speed);
  if (missing.isEmpty) {
    quickPrint('you can afford it');
  } else {
    for (final item in missing.keys) {
      quickPrint('short of ${missing[item]} $item');
    }
  }
}
""",
    ),
    _entry(
        "costs-safe-buy", "Costs", "A safe buy: unlock() only what the barn can pay for",
        "unlock(Unlocks.Speed) buys research from code, as the button would, and gives back "
        "True if it was bought. can_afford() reads the price first and also refuses an unlock "
        "already at its top level, whose cost comes back empty. A failed unlock() costs a "
        "tick; a real one 200. This really spends the barn: it buys every Speed level it can.",
        ("Loops", "Expand", "Speed", "Senses", "Costs", "Auto_Unlock", "Debug", "Lists",
         "Operators", "Variables", "Functions"),
        python="""
def can_afford(thing):
    cost = get_cost(thing)
    if len(cost) == 0:
        return False            # at the top level: nothing left to buy
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True

def buy_all(thing):
    bought = 0
    while can_afford(thing) and unlock(thing):
        bought += 1
    return bought

quick_print("bought", buy_all(Unlocks.Speed), "Speed levels")
""",
        javascript="""
function canAfford(thing) {
  const cost = getCost(thing);
  if (Object.keys(cost).length === 0) return false; // at the top level: nothing left to buy
  for (const item in cost) {
    if (numItems(item) < cost[item]) return false;
  }
  return true;
}

function buyAll(thing) {
  let bought = 0;
  while (canAfford(thing) && unlock(thing)) bought += 1;
  return bought;
}

quickPrint("bought", buyAll(Unlocks.Speed), "Speed levels");
""",
        dart="""
bool canAfford(Object thing) {
  final cost = getCost(thing)!;
  if (cost.isEmpty) return false; // at the top level: nothing left to buy
  for (final item in cost.keys) {
    if (numItems(item) < cost[item]!) {
      return false;
    }
  }
  return true;
}

int buyAll(Unlocks thing) {
  var bought = 0;
  while (canAfford(thing) && unlock(thing)) {
    bought += 1;
  }
  return bought;
}

void main() {
  final bought = buyAll(Unlocks.speed);
  quickPrint('bought $bought Speed levels');
}
""",
    ),
    _entry(
        "costs-how-many", "Costs", "How many can the barn pay for?",
        "A plant's price depends on its upgrade level - a carrot costs 1 hay and 1 wood, "
        "double after each Carrots upgrade - so ask get_cost(Entities.Carrot) instead of "
        "remembering it. The barn pays for num_items(item) // cost[item] of them, and the "
        "least of those over all the items is how many in all. A free plant has an empty "
        "cost, so the starting number stands for no limit.",
        ("Expand", "Speed", "Plant", "Carrots", "Senses", "Costs", "Utilities", "Debug",
         "Lists", "Operators", "Variables", "Functions"),
        python="""
def how_many(thing):
    cost = get_cost(thing)
    most = 999999                # a free plant has no limit
    for item in cost:
        most = min(most, num_items(item) // cost[item])
    return most

def plant_up_to(crop, limit):
    count = min(limit, how_many(crop))
    for i in range(count):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(crop)
        move(North)
    return count

quick_print("planted", plant_up_to(Entities.Carrot, 3))
""",
        javascript="""
function howMany(thing) {
  const cost = getCost(thing);
  let most = 999999; // a free plant has no limit
  for (const item in cost) {
    most = min(most, Math.floor(numItems(item) / cost[item]));
  }
  return most;
}

function plantUpTo(crop, limit) {
  const count = min(limit, howMany(crop));
  for (const i of range(count)) {
    if (getGroundType() !== Grounds.Soil) till();
    plant(crop);
    move(North);
  }
  return count;
}

quickPrint("planted", plantUpTo(Entities.Carrot, 3));
""",
        dart="""
int howMany(Entities thing) {
  final cost = getCost(thing)!;
  num most = 999999; // a free plant has no limit
  for (final item in cost.keys) {
    most = min(most, numItems(item) ~/ cost[item]!);
  }
  return most.toInt();
}

int plantUpTo(Entities crop, int limit) {
  final count = min(limit, howMany(crop)).toInt();
  for (final i in range(count)) {
    if (getGroundType() != Grounds.soil) {
      till();
    }
    plant(crop);
    move(north);
  }
  return count;
}

void main() {
  final planted = plantUpTo(Entities.carrot, 3);
  quickPrint('planted $planted');
}
""",
    ),
    # ── Hats ────────────────────────────────────────────────────────────
    _entry(
        "hats-try-each", "Hats", "Try every hat: only the picture changes",
        "change_hat(Hats.Wizard_Hat) puts a hat on the drone and takes 200 ticks, like any "
        "action. Apart from the dinosaur hat, which has its own rules (see Dinosaurs), every "
        "hat is a costume: this puts each one on in turn and times a move, and it takes the "
        "same 200 ticks in all of them.",
        ("Expand", "Hats", "Timing", "Debug", "Lists", "Operators", "Variables", "Functions"),
        python="""
HATS = [Hats.Straw_Hat, Hats.Brown_Hat, Hats.Gray_Hat, Hats.Green_Hat,
        Hats.Purple_Hat, Hats.Traffic_Cone, Hats.Wizard_Hat]

def try_hat(hat):
    change_hat(hat)
    start = get_tick_count()
    move(North)
    return get_tick_count() - start

for hat in HATS:
    quick_print(hat, "- a move takes", try_hat(hat), "ticks")
change_hat(Hats.Straw_Hat)
""",
        javascript="""
const HATS = [Hats.StrawHat, Hats.BrownHat, Hats.GrayHat, Hats.GreenHat,
              Hats.PurpleHat, Hats.TrafficCone, Hats.WizardHat];

function tryHat(hat) {
  changeHat(hat);
  const start = getTickCount();
  move(North);
  return getTickCount() - start;
}

for (const hat of HATS) {
  quickPrint(hat, "- a move takes", tryHat(hat), "ticks");
}
changeHat(Hats.StrawHat);
""",
        dart="""
const hats = [Hats.strawHat, Hats.brownHat, Hats.grayHat, Hats.greenHat,
              Hats.purpleHat, Hats.trafficCone, Hats.wizardHat];

int tryHat(Hats hat) {
  changeHat(hat);
  final start = getTickCount();
  move(north);
  return getTickCount() - start;
}

void main() {
  for (final hat in hats) {
    quickPrint('$hat - a move takes ${tryHat(hat)} ticks');
  }
  changeHat(Hats.strawHat);
}
""",
    ),
    _entry(
        "hats-job-colours", "Hats", "Wear a colour for each job",
        "The hat is drawn on the drone, so it is a free status light - except that every "
        "change_hat() takes 200 ticks, the price of a move. Change it once per job, not once "
        "per square: a green hat for the harvesting lap, a purple one for the planting lap, "
        "and the straw hat back at the end.",
        ("Expand", "Speed", "Plant", "Hats", "Functions"),
        python="""
def sweep(hat, job):
    change_hat(hat)             # once per lap: a change takes 200 ticks
    for y in range(get_world_size()):
        job()
        move(North)

def cut():
    if can_harvest():
        harvest()

def sow():
    plant(Entities.Bush)

sweep(Hats.Green_Hat, cut)
sweep(Hats.Purple_Hat, sow)
change_hat(Hats.Straw_Hat)
""",
        javascript="""
function sweep(hat, job) {
  changeHat(hat); // once per lap: a change takes 200 ticks
  for (const y of range(getWorldSize())) {
    job();
    move(North);
  }
}

function cut() {
  if (canHarvest()) harvest();
}

function sow() {
  plant(Entities.Bush);
}

sweep(Hats.GreenHat, cut);
sweep(Hats.PurpleHat, sow);
changeHat(Hats.StrawHat);
""",
        dart="""
void sweep(Hats hat, void Function() job) {
  changeHat(hat); // once per lap: a change takes 200 ticks
  for (final y in range(getWorldSize())) {
    job();
    move(north);
  }
}

void cut() {
  if (canHarvest()) {
    harvest();
  }
}

void sow() {
  plant(Entities.bush);
}

void main() {
  sweep(Hats.greenHat, cut);
  sweep(Hats.purpleHat, sow);
  changeHat(Hats.strawHat);
}
""",
    ),
    # ── Imports and files ───────────────────────────────────────────────
    _entry(
        "import-config", "Imports and files", "A config file every other file can read",
        "Press the + beside the file tabs and add a file called config. This is what goes in "
        "it: the settings you keep changing and a check built on them. In main (this needs "
        "the Import research) write `import config` and then `config.CROP` and "
        "`config.rich_enough()`. One edit to config changes every file that reads it, and "
        "the file is harmless to Run on its own.",
        ("Senses", "Operators", "Variables", "Functions"),
        python="""
# The file "config". In main:  import config
#                              if config.rich_enough(): plant(config.CROP)
CROP = Entities.Bush
HAY_MIN = 50            # keep this much hay in the barn

def rich_enough():
    return num_items(Items.Hay) >= HAY_MIN
""",
        javascript="""
// The file "config". In main:  import { CROP, richEnough } from "./config.js";
//                              if (richEnough()) plant(CROP);
export const CROP = Entities.Bush;
export const HAY_MIN = 50; // keep this much hay in the barn

export function richEnough() {
  return numItems(Items.Hay) >= HAY_MIN;
}
""",
        dart="""
// The file "config". In main:  import 'config.dart';
//                              if (richEnough()) plant(crop);
const crop = Entities.bush;
const hayMin = 50; // keep this much hay in the barn

bool richEnough() {
  return numItems(Items.hay) >= hayMin;
}

void main() {} // Run starts main(), so a file you may Run needs one; main.dart's own wins
""",
    ),
    _entry(
        "import-names", "Imports and files", "Import only the names you use",
        "Name what you want from a file and the rest stays out of main's way, so main can "
        "keep its own cut(). In Python that is `from farmlib import cut_all`, in JavaScript "
        "`import { cutAll } from \"./farmlib.js\"` (only what the file exports can be "
        "imported), in Dart `import 'farmlib.dart' show cutAll;`. This is the file farmlib; "
        "it needs the Import research in main, not here.",
        ("Expand", "Speed", "Variables", "Functions"),
        python="""
# The file "farmlib". In main:  from farmlib import cut_all
#                               cut_all()
def cut():
    if can_harvest():
        harvest()

def cut_all():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            cut()
            move(North)
        move(East)
""",
        javascript="""
// The file "farmlib". In main:  import { cutAll } from "./farmlib.js";
//                               cutAll();
function cut() {
  if (canHarvest()) harvest();
}

export function cutAll() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      cut();
      move(North);
    }
    move(East);
  }
}
""",
        dart="""
// The file "farmlib". In main:  import 'farmlib.dart' show cutAll;
//                               cutAll();
void cut() {
  if (canHarvest()) {
    harvest();
  }
}

void cutAll() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      cut();
      move(north);
    }
    move(east);
  }
}

void main() {} // Run starts main(), so a file you may Run needs one; main.dart's own wins
""",
    ),
    # ── Simulation ──────────────────────────────────────────────────────
    _entry(
        "sim-next-speed", "Simulation", "What would the next Speed level save?",
        "simulate() lets you choose the research the trial owns, so you can ask for an "
        "upgrade you have not bought. This file races itself at your Speed level and at one "
        "more on a 4 by 4 field, and prints both times in game seconds. Your real farm is "
        "left exactly as it was. The trial must be handed num_unlocked()'s own research, "
        "Senses, or it cannot tell it is a trial.",
        ("Expand", "Speed", "Senses", "Simulation", "Debug", "Dictionaries", "Operators",
         "Variables", "Functions"),
        python="""
def sweep():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if can_harvest():
                harvest()
            move(North)
        move(East)

if num_unlocked(Unlocks.Simulation) == 0:    # a trial owns only what it was handed
    sweep()
else:
    level = num_unlocked(Unlocks.Speed)
    now = simulate("main", {Unlocks.Expand: 3, Unlocks.Senses: 1, Unlocks.Speed: level}, {}, {}, 0, 0)
    later = simulate("main", {Unlocks.Expand: 3, Unlocks.Senses: 1, Unlocks.Speed: level + 1}, {}, {}, 0, 0)
    quick_print("Speed", level, ":", now, "seconds. Speed", level + 1, ":", later, "seconds")
""",
        javascript="""
function sweep() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (canHarvest()) harvest();
      move(North);
    }
    move(East);
  }
}

if (numUnlocked(Unlocks.Simulation) === 0) { // a trial owns only what it was handed
  sweep();
} else {
  const level = numUnlocked(Unlocks.Speed);
  const now = simulate("main", { [Unlocks.Expand]: 3, [Unlocks.Senses]: 1, [Unlocks.Speed]: level }, {}, {}, 0, 0);
  const later = simulate("main", { [Unlocks.Expand]: 3, [Unlocks.Senses]: 1, [Unlocks.Speed]: level + 1 }, {}, {}, 0, 0);
  quickPrint("Speed", level, ":", now, "seconds. Speed", level + 1, ":", later, "seconds");
}
""",
        dart="""
void sweep() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (canHarvest()) {
        harvest();
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  if (numUnlocked(Unlocks.simulation) == 0) { // a trial owns only what it was handed
    sweep();
  } else {
    final level = numUnlocked(Unlocks.speed);
    final now = simulate('main', {Unlocks.expand: 3, Unlocks.senses: 1, Unlocks.speed: level}, {}, {}, 0, 0);
    final later = simulate('main', {Unlocks.expand: 3, Unlocks.senses: 1, Unlocks.speed: level + 1}, {}, {}, 0, 0);
    quickPrint('Speed $level : $now seconds. Speed ${level + 1} : $later seconds');
  }
}
""",
    ),
    _entry(
        "sim-best-tanks", "Simulation", "Try a setting from 0 to 4 and keep the winner",
        "Pass a setting to simulate() as a global, run the same file once for each value, and "
        "keep the value with the fewest game seconds: the program picks its own best. Here "
        "the setting is how many tanks of water to give a bush before waiting for it, and "
        "every trial starts with 4 tanks and the same random seed, so the only difference is "
        "the setting. The real run then grows its bush with the winner.",
        ("Loops", "Expand", "Plant", "Speed", "Senses", "Watering", "Simulation", "Debug",
         "Dictionaries", "Operators", "Variables", "Functions"),
        python="""
def grow_bush(tanks):
    plant(Entities.Bush)
    if tanks > 0:
        use_item(Items.Water, tanks)
    while not can_harvest():
        pass
    harvest()

if num_unlocked(Unlocks.Simulation) == 0:     # a trial: `tanks` was handed in
    grow_bush(tanks)
else:
    research = {Unlocks.Plant: 1, Unlocks.Speed: 1, Unlocks.Watering: 1, Unlocks.Senses: 1}
    best = 0
    best_time = 999999
    for water in range(5):
        seconds = simulate("main", research, {Items.Water: 4}, {"tanks": water}, 0, 0)
        quick_print(water, "tanks:", seconds, "seconds")
        if seconds < best_time:
            best_time = seconds
            best = water
    grow_bush(best)
""",
        javascript="""
function growBush(tanks) {
  plant(Entities.Bush);
  if (tanks > 0) useItem(Items.Water, tanks);
  while (!canHarvest()) {}
  harvest();
}

if (numUnlocked(Unlocks.Simulation) === 0) { // a trial: `tanks` was handed in
  growBush(tanks);
} else {
  const research = { [Unlocks.Plant]: 1, [Unlocks.Speed]: 1, [Unlocks.Watering]: 1, [Unlocks.Senses]: 1 };
  let best = 0;
  let bestTime = 999999;
  for (const water of range(5)) {
    const seconds = simulate("main", research, { [Items.Water]: 4 }, { tanks: water }, 0, 0);
    quickPrint(water, "tanks:", seconds, "seconds");
    if (seconds < bestTime) {
      bestTime = seconds;
      best = water;
    }
  }
  growBush(best);
}
""",
        dart="""
void growBush(int tanks) {
  plant(Entities.bush);
  if (tanks > 0) {
    useItem(Items.water, tanks);
  }
  while (!canHarvest()) {}
  harvest();
}

void main() {
  if (numUnlocked(Unlocks.simulation) == 0) { // a trial: simGlobals holds what was handed in
    growBush(simGlobals['tanks'] as int);
    return;
  }
  final research = {Unlocks.plant: 1, Unlocks.speed: 1, Unlocks.watering: 1, Unlocks.senses: 1};
  var best = 0;
  var bestTime = 999999.0;
  for (final water in range(5)) {
    final seconds = simulate('main', research, {Items.water: 4}, {'tanks': water}, 0, 0);
    quickPrint('$water tanks: $seconds seconds');
    if (seconds < bestTime) {
      bestTime = seconds;
      best = water;
    }
  }
  growBush(best);
}
""",
    ),
    # ── Polyculture layouts ─────────────────────────────────────────────
    _entry(
        "poly-grass-rows", "Polyculture layouts", "Bush rows with grass rows between",
        "A plant's wish is drawn at random when you plant it - one of the other three kinds, "
        "on one square within three steps - so a layout only improves the odds. Grass counts "
        "as a kind and grows by itself on any square you leave alone, so bushes on every other "
        "row make each grass row a friend a bush wants about one time in six. crop_at() is the "
        "layout; this plants it and counts the bushes whose wish it already meets. Half the "
        "field stays grass, so unless you grant more wishes it harvests less than a solid field.",
        ("Expand", "Speed", "Plant", "Polyculture", "Debug", "Operators", "Variables",
         "Functions"),
        python="""
def crop_at(x, y):      # the layout: bushes on the even rows, the rest left to grow grass
    return Entities.Bush if y % 2 == 0 else Entities.Grass

def plant_rows():
    n = get_world_size()
    bushes = 0
    happy = 0
    for y in range(n):
        for x in range(n):
            if crop_at(x, y) == Entities.Bush:
                plant(Entities.Bush)
                bushes += 1
                kind, (sx, sy) = get_companion()   # the wish, drawn when it was planted
                if kind == crop_at(sx, sy):         # the layout puts that kind there
                    happy += 1
            move(East)
        move(North)
    quick_print(happy, "of", bushes, "bushes have their wish")

plant_rows()
""",
        javascript="""
function cropAt(x, y) { // the layout: bushes on the even rows, the rest left to grow grass
  return y % 2 === 0 ? Entities.Bush : Entities.Grass;
}

function plantRows() {
  const n = getWorldSize();
  let bushes = 0;
  let happy = 0;
  for (const y of range(n)) {
    for (const x of range(n)) {
      if (cropAt(x, y) === Entities.Bush) {
        plant(Entities.Bush);
        bushes += 1;
        const [kind, [sx, sy]] = getCompanion(); // the wish, drawn when it was planted
        if (kind === cropAt(sx, sy)) happy += 1; // the layout puts that kind there
      }
      move(East);
    }
    move(North);
  }
  quickPrint(happy, "of", bushes, "bushes have their wish");
}

plantRows();
""",
        dart="""
Entities cropAt(int x, int y) { // the layout: bushes on the even rows, the rest left to grow grass
  return y % 2 == 0 ? Entities.bush : Entities.grass;
}

void plantRows() {
  final n = getWorldSize();
  var bushes = 0;
  var happy = 0;
  for (final y in range(n)) {
    for (final x in range(n)) {
      if (cropAt(x, y) == Entities.bush) {
        plant(Entities.bush);
        bushes += 1;
        final (kind, (sx, sy)) = getCompanion()!; // the wish, drawn when it was planted
        if (kind == cropAt(sx, sy)) { // the layout puts that kind there
          happy += 1;
        }
      }
      move(east);
    }
    move(north);
  }
  quickPrint('$happy of $bushes bushes have their wish');
}

void main() {
  plantRows();
}
""",
    ),
    _entry(
        "poly-checkerboard", "Polyculture layouts", "A checkerboard of trees and bushes",
        "Trees on the dark squares and bushes on the light ones: no tree has a tree beside it "
        "(a tree grows half as fast for each one), and every plant has the other kind close "
        "by. Because crop_at() says what stands on every square, a plant can tell the moment "
        "it is planted whether its wish will be met. About one plant in six is lucky.",
        ("Expand", "Speed", "Plant", "Trees", "Polyculture", "Debug", "Operators",
         "Variables", "Functions"),
        python="""
def crop_at(x, y):      # the layout: trees on the dark squares, bushes on the light ones
    return Entities.Tree if (x + y) % 2 == 0 else Entities.Bush

def plant_board():
    n = get_world_size()
    happy = 0
    for y in range(n):
        for x in range(n):
            plant(crop_at(x, y))
            kind, (sx, sy) = get_companion()   # the wish, drawn when it was planted
            if kind == crop_at(sx, sy):         # the layout puts that kind there
                happy += 1
            move(East)
        move(North)
    quick_print(happy, "of", n * n, "plants have their wish")

plant_board()
""",
        javascript="""
function cropAt(x, y) { // the layout: trees on the dark squares, bushes on the light ones
  return (x + y) % 2 === 0 ? Entities.Tree : Entities.Bush;
}

function plantBoard() {
  const n = getWorldSize();
  let happy = 0;
  for (const y of range(n)) {
    for (const x of range(n)) {
      plant(cropAt(x, y));
      const [kind, [sx, sy]] = getCompanion(); // the wish, drawn when it was planted
      if (kind === cropAt(sx, sy)) happy += 1; // the layout puts that kind there
      move(East);
    }
    move(North);
  }
  quickPrint(happy, "of", n * n, "plants have their wish");
}

plantBoard();
""",
        dart="""
Entities cropAt(int x, int y) { // the layout: trees on the dark squares, bushes on the light ones
  return (x + y) % 2 == 0 ? Entities.tree : Entities.bush;
}

void plantBoard() {
  final n = getWorldSize();
  var happy = 0;
  for (final y in range(n)) {
    for (final x in range(n)) {
      plant(cropAt(x, y));
      final (kind, (sx, sy)) = getCompanion()!; // the wish, drawn when it was planted
      if (kind == cropAt(sx, sy)) { // the layout puts that kind there
        happy += 1;
      }
      move(east);
    }
    move(north);
  }
  quickPrint('$happy of ${n * n} plants have their wish');
}

void main() {
  plantBoard();
}
""",
    ),
    # ── Dinosaur: longer runs ───────────────────────────────────────────
    _entry(
        "dino-cycle", "Dinosaur: longer runs", "A loop through every square: the tail can never trap you",
        "With the dinosaur hat on, the field does not wrap and your tail blocks you, so a "
        "chase can corner itself. On a field with an even side there is a closed loop through "
        "every square: along the bottom row, a snake through the rows above, and back down "
        "the left column. Follow it and the square ahead is always free, and every apple "
        "lies on it. It needs an even side (4 by 4 after Expand 3) and cactus for apples.",
        ("Expand", "Speed", "Senses", "Dinosaurs", "Operators", "Variables", "Functions"),
        python="""
def cycle_direction(n):
    x = get_pos_x()
    y = get_pos_y()
    if x == 0:
        return East if y == 0 else South
    if y % 2 == 0:
        return North if x == n - 1 else East
    return North if x == 1 and y < n - 1 else West

def ride(laps):
    n = get_world_size()
    change_hat(Hats.Dinosaur_Hat)
    for i in range(laps * n * n):
        move(cycle_direction(n))
    change_hat(Hats.Straw_Hat)    # bones: the tail's length squared

ride(2)
""",
        javascript="""
function cycleDirection(n) {
  const x = getPosX();
  const y = getPosY();
  if (x === 0) return y === 0 ? East : South;
  if (y % 2 === 0) return x === n - 1 ? North : East;
  return x === 1 && y < n - 1 ? North : West;
}

function ride(laps) {
  const n = getWorldSize();
  changeHat(Hats.DinosaurHat);
  for (const i of range(laps * n * n)) {
    move(cycleDirection(n));
  }
  changeHat(Hats.StrawHat); // bones: the tail's length squared
}

ride(2);
""",
        dart="""
Direction cycleDirection(int n) {
  final x = getPosX();
  final y = getPosY();
  if (x == 0) return y == 0 ? east : south;
  if (y % 2 == 0) return x == n - 1 ? north : east;
  return x == 1 && y < n - 1 ? north : west;
}

void ride(int laps) {
  final n = getWorldSize();
  changeHat(Hats.dinosaurHat);
  for (final i in range(laps * n * n)) {
    move(cycleDirection(n));
  }
  changeHat(Hats.strawHat); // bones: the tail's length squared
}

void main() {
  ride(2);
}
""",
    ),
    _entry(
        "dino-bank", "Dinosaur: longer runs", "Ride until the tail is long enough, then bank it",
        "Taking the hat off pays the tail's length squared in bones, while every apple costs "
        "the same cactus, so a longer tail pays more per apple: 4 apples give 16 bones, 8 give "
        "64. Standing on an apple, get_entity_type() says Apple, and the step off eats it, so "
        "counting those gives the length. The loop of the last tip keeps the run safe; the "
        "step budget ends it if the cactus runs out before the tail is long enough.",
        ("Loops", "Expand", "Speed", "Senses", "Dinosaurs", "Debug", "Operators", "Variables",
         "Functions"),
        python="""
def cycle_direction(n):
    x = get_pos_x()
    y = get_pos_y()
    if x == 0:
        return East if y == 0 else South
    if y % 2 == 0:
        return North if x == n - 1 else East
    return North if x == 1 and y < n - 1 else West

def ride_until(target):
    n = get_world_size()
    eaten = 0
    steps = 0
    change_hat(Hats.Dinosaur_Hat)
    while eaten < target and steps < 20 * n * n:
        if get_entity_type() == Entities.Apple:
            eaten += 1                # the step off this square eats it
        move(cycle_direction(n))
        steps += 1
    change_hat(Hats.Straw_Hat)        # bank it: eaten * eaten bones
    return eaten

quick_print("tail of", ride_until(4))
""",
        javascript="""
function cycleDirection(n) {
  const x = getPosX();
  const y = getPosY();
  if (x === 0) return y === 0 ? East : South;
  if (y % 2 === 0) return x === n - 1 ? North : East;
  return x === 1 && y < n - 1 ? North : West;
}

function rideUntil(target) {
  const n = getWorldSize();
  let eaten = 0;
  let steps = 0;
  changeHat(Hats.DinosaurHat);
  while (eaten < target && steps < 20 * n * n) {
    if (getEntityType() === Entities.Apple) eaten += 1; // the step off this square eats it
    move(cycleDirection(n));
    steps += 1;
  }
  changeHat(Hats.StrawHat); // bank it: eaten * eaten bones
  return eaten;
}

quickPrint("tail of", rideUntil(4));
""",
        dart="""
Direction cycleDirection(int n) {
  final x = getPosX();
  final y = getPosY();
  if (x == 0) return y == 0 ? east : south;
  if (y % 2 == 0) return x == n - 1 ? north : east;
  return x == 1 && y < n - 1 ? north : west;
}

int rideUntil(int target) {
  final n = getWorldSize();
  var eaten = 0;
  var steps = 0;
  changeHat(Hats.dinosaurHat);
  while (eaten < target && steps < 20 * n * n) {
    if (getEntityType() == Entities.apple) {
      eaten += 1; // the step off this square eats it
    }
    move(cycleDirection(n));
    steps += 1;
  }
  changeHat(Hats.strawHat); // bank it: eaten * eaten bones
  return eaten;
}

void main() {
  quickPrint('tail of ${rideUntil(4)}');
}
""",
    ),
    # ── Maze: reuse and speed ───────────────────────────────────────────
    _entry(
        "maze-toward", "Maze: reuse and speed", "Try the way towards the treasure first",
        "measure() tells you where the treasure is, so a depth-first search need not try the "
        "directions in a fixed order: try the ones that close the gap first, and only then "
        "the others. It still never circles in a reused maze, since it remembers where it "
        "has been, but it usually reaches the treasure in fewer moves. The two lines before "
        "the search grow the maze from a bush, and do nothing where one already stands.",
        ("Expand", "Plant", "Senses", "Speed", "Mazes", "Fertilizer", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def cell():
    return get_pos_x() * 32 + get_pos_y()

def dfs(tx, ty, seen):
    if get_pos_x() == tx and get_pos_y() == ty:
        return True
    seen.append(cell())
    dirs = [North, East, South, West]
    toward = [ty > get_pos_y(), tx > get_pos_x(), ty < get_pos_y(), tx < get_pos_x()]
    for round in range(2):                      # first the ways that close the gap
        for i in range(4):
            if toward[i] == (round == 0) and can_move(dirs[i]):
                move(dirs[i])
                if cell() not in seen and dfs(tx, ty, seen):
                    return True
                move(dirs[(i + 2) % 4])         # dead end or seen before: step back
    return False

plant(Entities.Bush)
use_item(Items.Weird_Substance, get_world_size())   # grow a maze around you
tx, ty = measure()
dfs(tx, ty, [])
harvest()
""",
        javascript="""
function cell() {
  return getPosX() * 32 + getPosY();
}

function dfs(tx, ty, seen) {
  if (getPosX() === tx && getPosY() === ty) return true;
  seen.push(cell());
  const dirs = [North, East, South, West];
  const toward = [ty > getPosY(), tx > getPosX(), ty < getPosY(), tx < getPosX()];
  for (const round of range(2)) { // first the ways that close the gap
    for (const i of range(4)) {
      if (toward[i] === (round === 0) && canMove(dirs[i])) {
        move(dirs[i]);
        if (!seen.includes(cell()) && dfs(tx, ty, seen)) return true;
        move(dirs[(i + 2) % 4]); // dead end or seen before: step back
      }
    }
  }
  return false;
}

plant(Entities.Bush);
useItem(Items.WeirdSubstance, getWorldSize()); // grow a maze around you
const [tx, ty] = measure();
dfs(tx, ty, []);
harvest();
""",
        dart="""
int cell() => getPosX() * 32 + getPosY();

bool dfs(int tx, int ty, List<int> seen) {
  if (getPosX() == tx && getPosY() == ty) return true;
  seen.add(cell());
  const dirs = [north, east, south, west];
  final toward = [ty > getPosY(), tx > getPosX(), ty < getPosY(), tx < getPosX()];
  for (final round in range(2)) { // first the ways that close the gap
    for (final i in range(4)) {
      if (toward[i] == (round == 0) && canMove(dirs[i])) {
        move(dirs[i]);
        if (!seen.contains(cell()) && dfs(tx, ty, seen)) return true;
        move(dirs[(i + 2) % 4]); // dead end or seen before: step back
      }
    }
  }
  return false;
}

void main() {
  plant(Entities.bush);
  useItem(Items.weirdSubstance, getWorldSize()); // grow a maze around you
  final (tx, ty) = measure() as (int, int);
  dfs(tx, ty, <int>[]);
  harvest();
}
""",
    ),
    _entry(
        "maze-hop-plan", "Maze: reuse and speed", "How many hops is a maze worth?",
        "Growing a maze and every hop of its treasure cost the same Weird Substance: the "
        "field's size times 2 for each Mazes level past the first. Each hop, and the last "
        "harvest, pays the field's size times that cost in gold. The treasure moves at most "
        "300 times, after which use_item does nothing, so the barn, the first maze and that "
        "limit decide how many hops to plan.",
        ("Expand", "Speed", "Senses", "Mazes", "Utilities", "Debug", "Operators", "Variables",
         "Functions"),
        python="""
def plan_maze():
    n = get_world_size()
    amount = n * 2 ** (num_unlocked(Unlocks.Mazes) - 1)   # a maze, and each hop, costs this
    batches = num_items(Items.Weird_Substance) // amount
    if batches == 0:
        quick_print("not enough Weird Substance for a maze")
        return
    hops = min(batches - 1, 300)          # the maze itself takes the first batch
    quick_print("grow, then", hops, "hops for about", (hops + 1) * n * amount, "gold")

plan_maze()
""",
        javascript="""
function planMaze() {
  const n = getWorldSize();
  const amount = n * 2 ** (numUnlocked(Unlocks.Mazes) - 1); // a maze, and each hop, costs this
  const batches = Math.floor(numItems(Items.WeirdSubstance) / amount);
  if (batches === 0) {
    quickPrint("not enough Weird Substance for a maze");
    return;
  }
  const hops = min(batches - 1, 300); // the maze itself takes the first batch
  quickPrint("grow, then", hops, "hops for about", (hops + 1) * n * amount, "gold");
}

planMaze();
""",
        dart="""
void planMaze() {
  final n = getWorldSize();
  var amount = n; // a maze, and each hop, costs this
  for (final i in range(numUnlocked(Unlocks.mazes) - 1)) {
    amount *= 2;
  }
  final batches = numItems(Items.weirdSubstance) ~/ amount;
  if (batches == 0) {
    quickPrint('not enough Weird Substance for a maze');
    return;
  }
  final hops = min(batches - 1, 300).toInt(); // the maze itself takes the first batch
  quickPrint('grow, then $hops hops for about ${(hops + 1) * n * amount} gold');
}

void main() {
  planMaze();
}
""",
    ),
)
