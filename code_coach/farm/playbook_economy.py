"""Playbook tips on crops, items and the economy (see playbook.py).

Grass and hay, trees and bushes, carrots, water and fertilizer, companions,
sunflowers, cactus sorting, the dinosaur, gold from the maze, and the barn.
Every number here is what this clone does (world.py, data.py); where the
game differs, the clone wins. Every snippet also has to run on a bare field
of grass, because that is what tests/test_farm_playbook.py gives it, so the
ones that read a plant's size or petals look first.
"""

from __future__ import annotations

from code_coach.farm.playbook import Entry, _entry

# ── Pieces used by more than one entry ──────────────────────────────────

#: Walk straight to (tx, ty) - across the field, never over an edge.
_WALK_PY = """
def walk_to(tx, ty):
    while get_pos_x() < tx:
        move(East)
    while get_pos_x() > tx:
        move(West)
    while get_pos_y() < ty:
        move(North)
    while get_pos_y() > ty:
        move(South)
"""

_WALK_JS = """
function walkTo(tx, ty) {
  while (getPosX() < tx) move(East);
  while (getPosX() > tx) move(West);
  while (getPosY() < ty) move(North);
  while (getPosY() > ty) move(South);
}
"""

_WALK_DART = """
void walkTo(int tx, int ty) {
  while (getPosX() < tx) move(east);
  while (getPosX() > tx) move(west);
  while (getPosY() < ty) move(north);
  while (getPosY() > ty) move(south);
}
"""

# ── The entries ─────────────────────────────────────────────────────────

ENTRIES: tuple[Entry, ...] = (
    # ── Grass and hay ───────────────────────────────────────────────────
    _entry(
        "grass-mow", "Grass and hay", "Cut the whole field for hay",
        "Grass grows by itself, is ripe half a second after it is cut, and needs no soil and "
        "no planting. A cut gives 1 hay, and every Grass upgrade doubles that. Sweep the field "
        "and cut only what is ripe: can_harvest() costs 1 tick, harvest() 200.",
        ("Expand", "Speed"),
        python="""
for x in range(get_world_size()):
    for y in range(get_world_size()):
        if can_harvest():
            harvest()
        move(North)
    move(East)
""",
        javascript="""
for (const x of range(getWorldSize())) {
  for (const y of range(getWorldSize())) {
    if (canHarvest()) harvest();
    move(North);
  }
  move(East);
}
""",
        dart="""
void main() {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize())) {
      if (canHarvest()) {
        harvest();
      }
      move(north);
    }
    move(east);
  }
}
""",
    ),
    _entry(
        "grass-hay-per-cut", "Grass and hay", "What is one cut of grass worth?",
        "Ask num_items(Items.Hay) before and after a harvest: 1 hay at the start, 2 after one "
        "Grass upgrade, 4 after two. Harvesting grass that is not ripe yet throws it away, so "
        "wait for can_harvest(); do_a_flip() is a wait of exactly one second.",
        ("Loops", "Speed", "Senses", "Debug", "Operators", "Variables", "Functions"),
        python="""
def hay_per_cut():
    while not can_harvest():
        do_a_flip()
    before = num_items(Items.Hay)
    harvest()
    return num_items(Items.Hay) - before

quick_print("hay per cut:", hay_per_cut())
""",
        javascript="""
function hayPerCut() {
  while (!canHarvest()) doAFlip();
  const before = numItems(Items.Hay);
  harvest();
  return numItems(Items.Hay) - before;
}

quickPrint("hay per cut:", hayPerCut());
""",
        dart="""
num hayPerCut() {
  while (!canHarvest()) {
    doAFlip();
  }
  final before = numItems(Items.hay);
  harvest();
  return numItems(Items.hay) - before;
}

void main() {
  quickPrint('hay per cut: ${hayPerCut()}');
}
""",
    ),
    # ── Trees and bushes ────────────────────────────────────────────────
    _entry(
        "trees-checkerboard", "Trees and bushes", "Plant trees on a checkerboard",
        "A tree gives 5 wood where a bush gives 1, but it grows twice as slowly for every tree "
        "right beside it (North, South, East or West; diagonals do not count). Trees where "
        "x + y is even and bushes in between means no tree ever has a tree beside it: ripe in "
        "5 to 8 seconds, where two tree neighbours make it four times slower than that, which "
        "is worse than a bush.",
        ("Expand", "Speed", "Plant", "Trees", "Operators", "Variables", "Functions"),
        python="""
def plant_checkerboard():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if (x + y) % 2 == 0:
                plant(Entities.Tree)
            else:
                plant(Entities.Bush)
            move(North)
        move(East)

plant_checkerboard()
""",
        javascript="""
function plantCheckerboard() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if ((x + y) % 2 === 0) plant(Entities.Tree);
      else plant(Entities.Bush);
      move(North);
    }
    move(East);
  }
}

plantCheckerboard();
""",
        dart="""
void plantCheckerboard() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if ((x + y) % 2 == 0) {
        plant(Entities.tree);
      } else {
        plant(Entities.bush);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  plantCheckerboard();
}
""",
    ),
    _entry(
        "trees-wood-loop", "Trees and bushes", "Keep the wood coming",
        "Visit every tile; where something is ripe, harvest it and plant the same kind again "
        "at once, so the checkerboard never changes. The first pass over plain grass cuts the "
        "hay and sets the checkerboard up; after that, each pass takes the wood that is ready. "
        "A tree gives 5 wood and a bush 1, and every Trees upgrade doubles both.",
        ("Expand", "Speed", "Plant", "Trees", "Operators", "Variables", "Functions"),
        python="""
def tend_wood():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if can_harvest():
                harvest()
                if (x + y) % 2 == 0:
                    plant(Entities.Tree)
                else:
                    plant(Entities.Bush)
            move(North)
        move(East)

tend_wood()
""",
        javascript="""
function tendWood() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (canHarvest()) {
        harvest();
        if ((x + y) % 2 === 0) plant(Entities.Tree);
        else plant(Entities.Bush);
      }
      move(North);
    }
    move(East);
  }
}

tendWood();
""",
        dart="""
void tendWood() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (canHarvest()) {
        harvest();
        if ((x + y) % 2 == 0) {
          plant(Entities.tree);
        } else {
          plant(Entities.bush);
        }
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  tendWood();
}
""",
    ),
    # ── Carrots ─────────────────────────────────────────────────────────
    _entry(
        "carrots-first-plot", "Carrots", "Till and plant a carrot field",
        "Carrots grow only in soil, so till() any tile that is not soil yet. Each carrot costs "
        "1 hay and 1 wood (twice that after each Carrots upgrade, which also doubles the "
        "harvest), and plant() answers False for 1 tick when the barn is short, so count the "
        "ones that went in. A carrot is ripe in 5 to 7 seconds.",
        ("Expand", "Speed", "Plant", "Carrots", "Senses", "Debug", "Operators", "Variables",
         "Functions"),
        python="""
def plant_carrots():
    planted = 0
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_ground_type() != Grounds.Soil:
                till()
            if plant(Entities.Carrot):
                planted += 1
            move(North)
        move(East)
    return planted

quick_print("planted", plant_carrots())
""",
        javascript="""
function plantCarrots() {
  let planted = 0;
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getGroundType() !== Grounds.Soil) till();
      if (plant(Entities.Carrot)) planted++;
      move(North);
    }
    move(East);
  }
  return planted;
}

quickPrint("planted", plantCarrots());
""",
        dart="""
int plantCarrots() {
  var planted = 0;
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getGroundType() != Grounds.soil) {
        till();
      }
      if (plant(Entities.carrot)) {
        planted++;
      }
      move(north);
    }
    move(east);
  }
  return planted;
}

void main() {
  quickPrint('planted ${plantCarrots()}');
}
""",
    ),
    _entry(
        "carrots-tend-loop", "Carrots", "Farm carrots until you have enough",
        "Soil stays soil when a carrot is harvested, so only till() the first time round: one "
        "function can take any tile - bare grass, empty soil, a ripe carrot or a growing one - "
        "and do the right thing. Loop it over the field until num_items(Items.Carrot) reaches "
        "the goal; most of the research is paid in carrots.",
        ("Loops", "Expand", "Speed", "Plant", "Carrots", "Senses", "Operators", "Variables",
         "Functions"),
        python="""
def tend_tile():
    if get_ground_type() != Grounds.Soil:
        till()
    if can_harvest():
        harvest()
    if get_entity_type() == None:
        plant(Entities.Carrot)

def tend_field():
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            tend_tile()
            move(North)
        move(East)

goal = num_items(Items.Carrot) + 20
while num_items(Items.Carrot) < goal:
    tend_field()
""",
        javascript="""
function tendTile() {
  if (getGroundType() !== Grounds.Soil) till();
  if (canHarvest()) harvest();
  if (getEntityType() === null) plant(Entities.Carrot);
}

function tendField() {
  for (const x of range(getWorldSize())) {
    for (const y of range(getWorldSize())) {
      tendTile();
      move(North);
    }
    move(East);
  }
}

const goal = numItems(Items.Carrot) + 20;
while (numItems(Items.Carrot) < goal) tendField();
""",
        dart="""
void tendTile() {
  if (getGroundType() != Grounds.soil) {
    till();
  }
  if (canHarvest()) {
    harvest();
  }
  if (getEntityType() == null) {
    plant(Entities.carrot);
  }
}

void tendField() {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize())) {
      tendTile();
      move(north);
    }
    move(east);
  }
}

void main() {
  final goal = numItems(Items.carrot) + 20;
  while (numItems(Items.carrot) < goal) {
    tendField();
  }
}
""",
    ),
    # ── Water and fertilizer ────────────────────────────────────────────
    _entry(
        "water-field", "Water and fertilizer", "Water the whole field in one sweep",
        "Each tank adds a quarter to the water level of the tile you stand on (the level stops "
        "at 1), and wet ground grows plants up to five times as fast. The ground loses 1 percent "
        "of its water every second, so a full tile is still above one half after a minute. Top "
        "each tile up to the level you want while the barn has water; it gets a tank every 10 "
        "seconds, and twice as many per Watering upgrade.",
        ("Loops", "Expand", "Watering", "Senses", "Operators", "Variables", "Functions"),
        python="""
def water_field(level):
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            while get_water() < level and num_items(Items.Water) > 0:
                use_item(Items.Water)
            move(North)
        move(East)

water_field(0.5)
""",
        javascript="""
function waterField(level) {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      while (getWater() < level && numItems(Items.Water) > 0) {
        useItem(Items.Water);
      }
      move(North);
    }
    move(East);
  }
}

waterField(0.5);
""",
        dart="""
void waterField(double level) {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      while (getWater() < level && numItems(Items.water) > 0) {
        useItem(Items.water);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  waterField(0.5);
}
""",
    ),
    _entry(
        "water-only-growing", "Water and fertilizer", "Water only what is growing",
        "Water only speeds up a plant that is still growing. On an empty tile, on a ripe plant "
        "or on grass (ripe again half a second after every cut) a tank is wasted. Look at "
        "get_entity_type() and can_harvest() first, and water only the rest.",
        ("Loops", "Expand", "Speed", "Watering", "Senses", "Operators", "Variables",
         "Functions"),
        python="""
def water_growing(level):
    crop = get_entity_type()
    if crop == None or crop == Entities.Grass or can_harvest():
        return
    while get_water() < level and num_items(Items.Water) > 0:
        use_item(Items.Water)

for x in range(get_world_size()):
    for y in range(get_world_size()):
        water_growing(0.75)
        move(North)
    move(East)
""",
        javascript="""
function waterGrowing(level) {
  const crop = getEntityType();
  if (crop === null || crop === Entities.Grass || canHarvest()) return;
  while (getWater() < level && numItems(Items.Water) > 0) {
    useItem(Items.Water);
  }
}

for (const x of range(getWorldSize())) {
  for (const y of range(getWorldSize())) {
    waterGrowing(0.75);
    move(North);
  }
  move(East);
}
""",
        dart="""
void waterGrowing(double level) {
  final crop = getEntityType();
  if (crop == null || crop == Entities.grass || canHarvest()) {
    return;
  }
  while (getWater() < level && numItems(Items.water) > 0) {
    useItem(Items.water);
  }
}

void main() {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize())) {
      waterGrowing(0.75);
      move(north);
    }
    move(east);
  }
}
""",
    ),
    _entry(
        "fertilizer-weird", "Water and fertilizer", "Make Weird Substance from grass",
        "use_item(Items.Fertilizer) takes 2 seconds off a plant's growing and infects it: when "
        "it is harvested, half of what it gives (rounded down, but at least 1) comes out as "
        "Weird Substance instead. Grass gives 1, so fertilized grass is ripe at once and pays "
        "1 Weird Substance and no hay - one fertilizer each, and the Weird Substance a maze "
        "needs. It fails on a ripe plant, so cut the grass first.",
        ("Expand", "Speed", "Fertilizer", "Operators", "Functions"),
        python="""
def make_weird(count):
    for i in range(count):
        if can_harvest():
            harvest()
        if not use_item(Items.Fertilizer):
            return
        harvest()

make_weird(5)
""",
        javascript="""
function makeWeird(count) {
  for (const i of range(count)) {
    if (canHarvest()) harvest();
    if (!useItem(Items.Fertilizer)) return;
    harvest();
  }
}

makeWeird(5);
""",
        dart="""
void makeWeird(int count) {
  for (final i in range(count)) {
    if (canHarvest()) {
      harvest();
    }
    if (!useItem(Items.fertilizer)) {
      return;
    }
    harvest();
  }
}

void main() {
  makeWeird(5);
}
""",
    ),
    _entry(
        "fertilizer-pass", "Water and fertilizer", "A fertilize-and-harvest pass",
        "One sweep that harvests what is ripe and fertilizes what is still growing (grass "
        "excepted, it is ripe again in half a second). Each dose takes 2 seconds off the wait, "
        "but half the harvest of an infected plant turns into Weird Substance: a tree then pays "
        "3 wood and 2 Weird Substance instead of 5 wood. Use it when you want the Weird "
        "Substance or the time, not for the wood. The barn gets a fertilizer every 10 seconds.",
        ("Expand", "Speed", "Senses", "Fertilizer", "Operators", "Variables", "Functions"),
        python="""
def fertilize_pass():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            crop = get_entity_type()
            if can_harvest():
                harvest()
            elif crop != None and crop != Entities.Grass and num_items(Items.Fertilizer) > 0:
                use_item(Items.Fertilizer)
            move(North)
        move(East)

fertilize_pass()
""",
        javascript="""
function fertilizePass() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const crop = getEntityType();
      if (canHarvest()) {
        harvest();
      } else if (crop !== null && crop !== Entities.Grass && numItems(Items.Fertilizer) > 0) {
        useItem(Items.Fertilizer);
      }
      move(North);
    }
    move(East);
  }
}

fertilizePass();
""",
        dart="""
void fertilizePass() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final crop = getEntityType();
      if (canHarvest()) {
        harvest();
      } else if (crop != null && crop != Entities.grass && numItems(Items.fertilizer) > 0) {
        useItem(Items.fertilizer);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  fertilizePass();
}
""",
    ),
    # ── Companions ──────────────────────────────────────────────────────
    _entry(
        "companion-plant-wish", "Companions", "Plant the neighbour a plant wants",
        "get_companion() gives the plant a grass, bush, tree or carrot wants beside it, and "
        "the tile, up to three steps away and on the field. Plant that there and the harvest "
        "of the plant here is multiplied by five, doubling with each Polyculture upgrade. "
        "This walks over, plants a wished-for bush or tree and walks back; a carrot wish "
        "needs till() first, and grass that is already there needs nothing.",
        ("Loops", "Expand", "Speed", "Plant", "Trees", "Senses", "Polyculture", "Operators",
         "Variables", "Functions"),
        python=_WALK_PY + """
def plant_wish():
    wish = get_companion()
    if wish == None:
        return
    kind, spot = wish
    if kind != Entities.Bush and kind != Entities.Tree:
        return
    tx, ty = spot
    x = get_pos_x()
    y = get_pos_y()
    walk_to(tx, ty)
    plant(kind)
    walk_to(x, y)

plant_wish()
""",
        javascript=_WALK_JS + """
function plantWish() {
  const wish = getCompanion();
  if (wish === null) return;
  const [kind, [tx, ty]] = wish;
  if (kind !== Entities.Bush && kind !== Entities.Tree) return;
  const x = getPosX();
  const y = getPosY();
  walkTo(tx, ty);
  plant(kind);
  walkTo(x, y);
}

plantWish();
""",
        dart=_WALK_DART + """
void plantWish() {
  final wish = getCompanion();
  if (wish == null) return;
  final (kind, (tx, ty)) = wish;
  if (kind != Entities.bush && kind != Entities.tree) return;
  final x = getPosX();
  final y = getPosY();
  walkTo(tx, ty);
  plant(kind);
  walkTo(x, y);
}

void main() {
  plantWish();
}
""",
    ),
    _entry(
        "companion-check-friend", "Companions", "Harvest only when the friend is there",
        "The bonus counts only if the wished-for plant is standing on its tile at the moment "
        "you harvest - ripe or not, but not cut, dead or replaced. So walk over, look with "
        "get_entity_type(), walk back, and cash in only on a yes. Harvest the plant before "
        "its friend, never the other way round.",
        ("Loops", "Expand", "Speed", "Senses", "Polyculture", "Operators", "Variables",
         "Functions"),
        python=_WALK_PY + """
def friend_is_there():
    wish = get_companion()
    if wish == None:
        return True
    kind, spot = wish
    tx, ty = spot
    x = get_pos_x()
    y = get_pos_y()
    walk_to(tx, ty)
    there = get_entity_type() == kind
    walk_to(x, y)
    return there

if can_harvest() and friend_is_there():
    harvest()
""",
        javascript=_WALK_JS + """
function friendIsThere() {
  const wish = getCompanion();
  if (wish === null) return true;
  const [kind, [tx, ty]] = wish;
  const x = getPosX();
  const y = getPosY();
  walkTo(tx, ty);
  const there = getEntityType() === kind;
  walkTo(x, y);
  return there;
}

if (canHarvest() && friendIsThere()) harvest();
""",
        dart=_WALK_DART + """
bool friendIsThere() {
  final wish = getCompanion();
  if (wish == null) return true;
  final (kind, (tx, ty)) = wish;
  final x = getPosX();
  final y = getPosY();
  walkTo(tx, ty);
  final there = getEntityType() == kind;
  walkTo(x, y);
  return there;
}

void main() {
  if (canHarvest() && friendIsThere()) {
    harvest();
  }
}
""",
    ),
    # ── Sunflower power ─────────────────────────────────────────────────
    _entry(
        "sunflower-field", "Sunflower power", "Plant enough sunflowers for the bonus",
        "The bonus of 8 times the power needs at least 10 sunflowers standing on the field, so "
        "the 3 by 3 farm (9 tiles) can never earn it and the 4 by 4 one (16) can. A sunflower "
        "costs 1 carrot, grows in soil in 6 to 8 seconds and has 7 to 15 petals. Plant every "
        "tile and count what went in.",
        ("Expand", "Speed", "Plant", "Carrots", "Sunflowers", "Senses", "Debug", "Operators",
         "Variables", "Functions"),
        python="""
def plant_sunflowers():
    planted = 0
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_ground_type() != Grounds.Soil:
                till()
            if plant(Entities.Sunflower):
                planted += 1
            move(North)
        move(East)
    return planted

count = plant_sunflowers()
if count >= 10:
    quick_print(count, "sunflowers: the bonus is possible")
else:
    quick_print(count, "sunflowers: too few for the bonus")
""",
        javascript="""
function plantSunflowers() {
  let planted = 0;
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getGroundType() !== Grounds.Soil) till();
      if (plant(Entities.Sunflower)) planted++;
      move(North);
    }
    move(East);
  }
  return planted;
}

const count = plantSunflowers();
if (count >= 10) quickPrint(count, "sunflowers: the bonus is possible");
else quickPrint(count, "sunflowers: too few for the bonus");
""",
        dart="""
int plantSunflowers() {
  var planted = 0;
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getGroundType() != Grounds.soil) {
        till();
      }
      if (plant(Entities.sunflower)) {
        planted++;
      }
      move(north);
    }
    move(east);
  }
  return planted;
}

void main() {
  final count = plantSunflowers();
  if (count >= 10) {
    quickPrint('$count sunflowers: the bonus is possible');
  } else {
    quickPrint('$count sunflowers: too few for the bonus');
  }
}
""",
    ),
    _entry(
        "sunflower-scan-harvest", "Sunflower power", "Scan once, then go to the biggest",
        "Instead of one pass of the field for every petal count, sweep it once and write every "
        "sunflower down as [petals, x, y] in a list. Then keep picking the biggest, walking to "
        "it and harvesting: biggest first is what the bonus asks for, and the walks are far "
        "shorter than nine full passes. Power doubles the drone's speed while any is left.",
        ("Loops", "Expand", "Speed", "Senses", "Sunflowers", "Operators", "Variables",
         "Functions", "Lists"),
        python=_WALK_PY + """
def scan():
    flowers = []
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            petals = measure()
            if petals != None:
                flowers.append([petals, get_pos_x(), get_pos_y()])
            move(North)
        move(East)
    return flowers

def harvest_biggest_first():
    flowers = scan()
    while len(flowers) > 0:
        best = 0
        for i in range(len(flowers)):
            if flowers[i][0] > flowers[best][0]:
                best = i
        petals, x, y = flowers.pop(best)
        walk_to(x, y)
        if can_harvest():
            harvest()

harvest_biggest_first()
""",
        javascript=_WALK_JS + """
function scan() {
  const flowers = [];
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const petals = measure();
      if (petals !== null) flowers.push([petals, getPosX(), getPosY()]);
      move(North);
    }
    move(East);
  }
  return flowers;
}

function harvestBiggestFirst() {
  const flowers = scan();
  while (flowers.length > 0) {
    let best = 0;
    for (let i = 0; i < flowers.length; i++) {
      if (flowers[i][0] > flowers[best][0]) best = i;
    }
    const [petals, x, y] = flowers.splice(best, 1)[0];
    walkTo(x, y);
    if (canHarvest()) harvest();
  }
}

harvestBiggestFirst();
""",
        dart=_WALK_DART + """
List<List<int>> scan() {
  final flowers = <List<int>>[];
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final petals = measure();
      if (petals != null) flowers.add([petals as int, getPosX(), getPosY()]);
      move(north);
    }
    move(east);
  }
  return flowers;
}

void harvestBiggestFirst() {
  final flowers = scan();
  while (flowers.isNotEmpty) {
    var best = 0;
    for (var i = 0; i < flowers.length; i++) {
      if (flowers[i][0] > flowers[best][0]) best = i;
    }
    final flower = flowers.removeAt(best);
    walkTo(flower[1], flower[2]);
    if (canHarvest()) harvest();
  }
}

void main() {
  harvestBiggestFirst();
}
""",
    ),
    # ── Cactus: faster sorting ──────────────────────────────────────────
    _entry(
        "cactus-plant-field", "Cactus: faster sorting", "Plant a cactus field",
        "A cactus costs 2 pumpkins, needs soil, gets a random size from 0 to 9 and is ripe one "
        "second after planting. Plant every tile, then wait that second - do_a_flip() is "
        "exactly one - before you sort, because a cactus that is not ripe never counts as "
        "sorted.",
        ("Expand", "Speed", "Plant", "Carrots", "Cactus", "Senses", "Operators", "Variables",
         "Functions"),
        python="""
def plant_cacti():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
            move(North)
        move(East)
    do_a_flip()

plant_cacti()
""",
        javascript="""
function plantCacti() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getGroundType() !== Grounds.Soil) till();
      plant(Entities.Cactus);
      move(North);
    }
    move(East);
  }
  doAFlip();
}

plantCacti();
""",
        dart="""
void plantCacti() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getGroundType() != Grounds.soil) {
        till();
      }
      plant(Entities.cactus);
      move(north);
    }
    move(east);
  }
  doAFlip();
}

void main() {
  plantCacti();
}
""",
    ),
    _entry(
        "cactus-row-sort", "Cactus: faster sorting", "A row of cacti pays its length squared",
        "A patch pays the square of its size, and a row of cacti with nothing planted above or "
        "below it is a patch by itself once it is sorted small (West) to big (East): 6 cacti "
        "pay 36. Bubble sort needs only measure(East) and swap(East), and each pass can stop "
        "one tile sooner because the biggest has reached the end. Start on the West end.",
        ("Expand", "Speed", "Plant", "Carrots", "Cactus", "Senses", "Operators", "Variables",
         "Functions"),
        python="""
def plant_row():
    for i in range(get_world_size()):
        if get_ground_type() != Grounds.Soil:
            till()
        plant(Entities.Cactus)
        move(East)
    do_a_flip()

def sort_row():
    n = get_world_size()
    for end in range(n - 1, 0, -1):
        for i in range(end):
            if measure(East) < measure():
                swap(East)
            move(East)
        for i in range(end):
            move(West)

plant_row()
sort_row()
harvest()
""",
        javascript="""
function plantRow() {
  for (const i of range(getWorldSize())) {
    if (getGroundType() !== Grounds.Soil) till();
    plant(Entities.Cactus);
    move(East);
  }
  doAFlip();
}

function sortRow() {
  const n = getWorldSize();
  for (const end of range(n - 1, 0, -1)) {
    for (const i of range(end)) {
      if (measure(East) < measure()) swap(East);
      move(East);
    }
    for (const i of range(end)) move(West);
  }
}

plantRow();
sortRow();
harvest();
""",
        dart="""
void plantRow() {
  for (final i in range(getWorldSize())) {
    if (getGroundType() != Grounds.soil) {
      till();
    }
    plant(Entities.cactus);
    move(east);
  }
  doAFlip();
}

void sortRow() {
  final n = getWorldSize();
  for (final end in range(n - 1, 0, -1)) {
    for (final i in range(end)) {
      if (measure(east) < measure()) {
        swap(east);
      }
      move(east);
    }
    for (final i in range(end)) {
      move(west);
    }
  }
}

void main() {
  plantRow();
  sortRow();
  harvest();
}
""",
    ),
    _entry(
        "cactus-rows-then-columns", "Cactus: faster sorting", "Sort the whole field: columns, then rows",
        "A whole field of n by n sorted cacti is one patch and pays (n*n) squared: on a 6 by 6 "
        "farm 1296, against 36 for a single sorted row - 36 times as much for roughly ten times "
        "the time. Sort every column (small to the South), then every row (small to the West); "
        "sorting the rows afterwards leaves the columns sorted. Each line is shaken forth and "
        "back until a round swaps nothing. Plant the field first, as in the tip above.",
        ("Loops", "Expand", "Speed", "Cactus", "Senses", "Operators", "Variables", "Functions"),
        python="""
def sort_line(d, back, length):
    swapped = True
    while swapped:
        swapped = False
        for i in range(length - 1):
            if measure(d) < measure():
                swap(d)
                swapped = True
            move(d)
        for i in range(length - 1):
            if measure(back) > measure():
                swap(back)
                swapped = True
            move(back)

def sort_field():
    if get_entity_type() != Entities.Cactus:
        return
    n = get_world_size()
    for x in range(n):
        sort_line(North, South, n)
        move(East)
    for y in range(n):
        sort_line(East, West, n)
        move(North)

sort_field()
harvest()
""",
        javascript="""
function sortLine(d, back, length) {
  let swapped = true;
  while (swapped) {
    swapped = false;
    for (const i of range(length - 1)) {
      if (measure(d) < measure()) {
        swap(d);
        swapped = true;
      }
      move(d);
    }
    for (const i of range(length - 1)) {
      if (measure(back) > measure()) {
        swap(back);
        swapped = true;
      }
      move(back);
    }
  }
}

function sortField() {
  if (getEntityType() !== Entities.Cactus) return;
  const n = getWorldSize();
  for (const x of range(n)) {
    sortLine(North, South, n);
    move(East);
  }
  for (const y of range(n)) {
    sortLine(East, West, n);
    move(North);
  }
}

sortField();
harvest();
""",
        dart="""
void sortLine(Direction d, Direction back, int length) {
  var swapped = true;
  while (swapped) {
    swapped = false;
    for (final i in range(length - 1)) {
      if (measure(d) < measure()) {
        swap(d);
        swapped = true;
      }
      move(d);
    }
    for (final i in range(length - 1)) {
      if (measure(back) > measure()) {
        swap(back);
        swapped = true;
      }
      move(back);
    }
  }
}

void sortField() {
  if (getEntityType() != Entities.cactus) return;
  final n = getWorldSize();
  for (final x in range(n)) {
    sortLine(north, south, n);
    move(east);
  }
  for (final y in range(n)) {
    sortLine(east, west, n);
    move(north);
  }
}

void main() {
  sortField();
  harvest();
}
""",
    ),
    # ── Dinosaur and apples ─────────────────────────────────────────────
    _entry(
        "dino-first-apple", "Dinosaur and apples", "Put the hat on and eat an apple",
        "The dinosaur hat drags a tail behind you and buys apples with cactus, 2 each. With the "
        "hat on, an apple appears under you at once, and while you stand on an apple measure() "
        "says where the next one will be. Leave the tile and you have eaten it: the tail "
        "grows by one and the next apple appears. Careful: with the hat on the field does "
        "not wrap, your tail blocks you, and every move takes 400 ticks (3 percent less for "
        "each apple eaten).",
        ("Loops", "Expand", "Speed", "Senses", "Dinosaurs", "Operators", "Variables",
         "Functions"),
        python=_WALK_PY + """
def eat_one_apple():
    target = measure()
    if target == None:
        return
    tx, ty = target
    walk_to(tx, ty)

change_hat(Hats.Dinosaur_Hat)
eat_one_apple()
change_hat(Hats.Straw_Hat)
""",
        javascript=_WALK_JS + """
function eatOneApple() {
  const target = measure();
  if (target === null) return;
  const [tx, ty] = target;
  walkTo(tx, ty);
}

changeHat(Hats.DinosaurHat);
eatOneApple();
changeHat(Hats.StrawHat);
""",
        dart=_WALK_DART + """
void eatOneApple() {
  final target = measure();
  if (target == null) return;
  final (tx, ty) = target as (int, int);
  walkTo(tx, ty);
}

void main() {
  changeHat(Hats.dinosaurHat);
  eatOneApple();
  changeHat(Hats.strawHat);
}
""",
    ),
    _entry(
        "dino-chaser", "Dinosaur and apples", "Chase the apples with measure()",
        "The whole game in one loop: standing on an apple, ask measure() for the next one and "
        "step towards it; arrive and ask again. A step that fails (an edge, or your own tail) "
        "tries another way, and the step budget ends the loop if you ever get stuck. It also "
        "ends when no apple comes - the cactus ran out, or your tail was on the spot the next "
        "apple was meant for and the game put it elsewhere. Taking the hat off pays bones: "
        "the tail's length squared, doubling with each Dinosaurs upgrade.",
        ("Expand", "Speed", "Senses", "Dinosaurs", "Operators", "Variables", "Functions"),
        python="""
def step_toward(tx, ty):
    if get_pos_x() < tx and move(East):
        return
    if get_pos_x() > tx and move(West):
        return
    if get_pos_y() < ty and move(North):
        return
    if get_pos_y() > ty and move(South):
        return
    move(North) or move(East) or move(South) or move(West)

def chase(steps):
    target = measure()
    for i in range(steps):
        if target == None:
            return
        tx, ty = target
        if get_pos_x() == tx and get_pos_y() == ty:
            target = measure()
        else:
            step_toward(tx, ty)

change_hat(Hats.Dinosaur_Hat)
chase(300)
change_hat(Hats.Straw_Hat)
""",
        javascript="""
function stepToward(tx, ty) {
  if (getPosX() < tx && move(East)) return;
  if (getPosX() > tx && move(West)) return;
  if (getPosY() < ty && move(North)) return;
  if (getPosY() > ty && move(South)) return;
  move(North) || move(East) || move(South) || move(West);
}

function chase(steps) {
  let target = measure();
  for (const i of range(steps)) {
    if (target === null) return;
    const [tx, ty] = target;
    if (getPosX() === tx && getPosY() === ty) {
      target = measure();
    } else {
      stepToward(tx, ty);
    }
  }
}

changeHat(Hats.DinosaurHat);
chase(300);
changeHat(Hats.StrawHat);
""",
        dart="""
void stepToward(int tx, int ty) {
  if (getPosX() < tx && move(east)) return;
  if (getPosX() > tx && move(west)) return;
  if (getPosY() < ty && move(north)) return;
  if (getPosY() > ty && move(south)) return;
  move(north) || move(east) || move(south) || move(west);
}

void chase(int steps) {
  var target = measure();
  for (final i in range(steps)) {
    if (target == null) return;
    final (tx, ty) = target as (int, int);
    if (getPosX() == tx && getPosY() == ty) {
      target = measure();
    } else {
      stepToward(tx, ty);
    }
  }
}

void main() {
  changeHat(Hats.dinosaurHat);
  chase(300);
  changeHat(Hats.strawHat);
}
""",
    ),
    # ── Gold and the treasure ───────────────────────────────────────────
    _entry(
        "gold-maze-cost", "Gold and the treasure", "Price a maze before you grow it",
        "A maze of m by m squares takes m times 2^(Mazes level - 1) Weird Substance, and each "
        "treasure pays m*m times 2^(Mazes level - 1) gold - so the gold per Weird Substance is "
        "about m, and the bigger the maze the better it pays. The whole field is the best "
        "size. Check the barn with num_items() first, then plant a bush and use that much on "
        "it.",
        ("Expand", "Speed", "Plant", "Senses", "Debug", "Mazes", "Fertilizer", "Operators",
         "Variables", "Functions"),
        python="""
def per_level():
    return 2 ** (num_unlocked(Unlocks.Mazes) - 1)

def substance_for(size):
    return size * per_level()

def gold_for(size):
    return size * size * per_level()

n = get_world_size()
cost = substance_for(n)
quick_print("a", n, "by", n, "maze costs", cost, "and pays", gold_for(n), "gold")
if num_items(Items.Weird_Substance) >= cost:
    plant(Entities.Bush)
    use_item(Items.Weird_Substance, cost)
""",
        javascript="""
function perLevel() {
  return 2 ** (numUnlocked(Unlocks.Mazes) - 1);
}

function substanceFor(size) {
  return size * perLevel();
}

function goldFor(size) {
  return size * size * perLevel();
}

const n = getWorldSize();
const cost = substanceFor(n);
quickPrint("a", n, "by", n, "maze costs", cost, "and pays", goldFor(n), "gold");
if (numItems(Items.WeirdSubstance) >= cost) {
  plant(Entities.Bush);
  useItem(Items.WeirdSubstance, cost);
}
""",
        dart="""
int perLevel() {
  var result = 1;
  for (final i in range(numUnlocked(Unlocks.mazes) - 1)) {
    result *= 2;
  }
  return result;
}

int substanceFor(int size) => size * perLevel();

int goldFor(int size) => size * size * perLevel();

void main() {
  final n = getWorldSize();
  final cost = substanceFor(n);
  quickPrint('a $n by $n maze costs $cost and pays ${goldFor(n)} gold');
  if (numItems(Items.weirdSubstance) >= cost) {
    plant(Entities.bush);
    useItem(Items.weirdSubstance, cost);
  }
}
""",
    ),
    _entry(
        "gold-cash-in", "Gold and the treasure", "Only cash in on the treasure",
        "Inside a maze, can_harvest() is true on the treasure and nowhere else, so it is the "
        "test to run before harvest(): a harvest on any other square of the maze pulls the "
        "whole maze down and pays nothing. This follows the right-hand wall, asks that "
        "question on every square, and has a step budget in case the walls loop.",
        ("Expand", "Speed", "Mazes", "Operators", "Variables", "Functions", "Lists"),
        python="""
def find_treasure(budget):
    dirs = [North, East, South, West]
    facing = 0
    for i in range(budget):
        if can_harvest():
            return True
        for turn in [1, 0, 3, 2]:
            heading = (facing + turn) % 4
            if can_move(dirs[heading]):
                facing = heading
                move(dirs[facing])
                break
    return False

if find_treasure(1000):
    harvest()
""",
        javascript="""
function findTreasure(budget) {
  const dirs = [North, East, South, West];
  let facing = 0;
  for (const i of range(budget)) {
    if (canHarvest()) return true;
    for (const turn of [1, 0, 3, 2]) {
      const heading = (facing + turn) % 4;
      if (canMove(dirs[heading])) {
        facing = heading;
        move(dirs[facing]);
        break;
      }
    }
  }
  return false;
}

if (findTreasure(1000)) harvest();
""",
        dart="""
bool findTreasure(int budget) {
  const dirs = [north, east, south, west];
  var facing = 0;
  for (final i in range(budget)) {
    if (canHarvest()) return true;
    for (final turn in [1, 0, 3, 2]) {
      final heading = (facing + turn) % 4;
      if (canMove(dirs[heading])) {
        facing = heading;
        move(dirs[facing]);
        break;
      }
    }
  }
  return false;
}

void main() {
  if (findTreasure(1000)) {
    harvest();
  }
}
""",
    ),
    # ── Items ───────────────────────────────────────────────────────────
    _entry(
        "items-reserve", "Items", "Keep a reserve in the barn",
        "num_items(Items.Hay) and friends let a program look in the barn before it spends. "
        "Carrots cost 1 hay and 1 wood each, so this plants only while more than `reserve` of "
        "both is left: the 50 hay you are saving for the next research stays put.",
        ("Expand", "Speed", "Plant", "Carrots", "Senses", "Operators", "Functions"),
        python="""
def have_more_than(reserve):
    return num_items(Items.Hay) > reserve and num_items(Items.Wood) > reserve

def plant_carrots(reserve):
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            if have_more_than(reserve):
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Carrot)
            move(North)
        move(East)

plant_carrots(50)
""",
        javascript="""
function haveMoreThan(reserve) {
  return numItems(Items.Hay) > reserve && numItems(Items.Wood) > reserve;
}

function plantCarrots(reserve) {
  for (const x of range(getWorldSize())) {
    for (const y of range(getWorldSize())) {
      if (haveMoreThan(reserve)) {
        if (getGroundType() !== Grounds.Soil) till();
        plant(Entities.Carrot);
      }
      move(North);
    }
    move(East);
  }
}

plantCarrots(50);
""",
        dart="""
bool haveMoreThan(int reserve) {
  return numItems(Items.hay) > reserve && numItems(Items.wood) > reserve;
}

void plantCarrots(int reserve) {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize())) {
      if (haveMoreThan(reserve)) {
        if (getGroundType() != Grounds.soil) {
          till();
        }
        plant(Entities.carrot);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  plantCarrots(50);
}
""",
    ),
    _entry(
        "items-use-count", "Items", "Use several tanks in one go",
        "use_item(Items.Water, 3) puts three tanks in as one 200-tick action instead of three, "
        "but it uses all three even if the level stops at 1. A tank is a quarter, so "
        "(1 - get_water()) // 0.25 is how many fit exactly; cap it at what the barn has.",
        ("Speed", "Watering", "Senses", "Operators", "Variables", "Functions"),
        python="""
def fill_up():
    tanks = (1 - get_water()) // 0.25
    if tanks > num_items(Items.Water):
        tanks = num_items(Items.Water)
    if tanks >= 1:
        use_item(Items.Water, tanks)

fill_up()
""",
        javascript="""
function fillUp() {
  let tanks = Math.floor((1 - getWater()) / 0.25);
  if (tanks > numItems(Items.Water)) tanks = numItems(Items.Water);
  if (tanks >= 1) useItem(Items.Water, tanks);
}

fillUp();
""",
        dart="""
void fillUp() {
  int tanks = (1 - getWater()) ~/ 0.25;
  if (tanks > numItems(Items.water)) {
    tanks = numItems(Items.water).toInt();
  }
  if (tanks >= 1) {
    useItem(Items.water, tanks);
  }
}

void main() {
  fillUp();
}
""",
    ),
    _entry(
        "items-get-cost", "Items", "Ask what it costs before you buy",
        "get_cost(Entities.Carrot) says what a plant costs and get_cost(Unlocks.Speed) what the "
        "next level of an unlock costs, as a dictionary from item to amount, always up to date "
        "with your upgrades. Check each item against num_items() and you never plant or buy "
        "short.",
        ("Expand", "Speed", "Plant", "Carrots", "Costs", "Senses", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def can_afford(thing):
    cost = get_cost(thing)
    for item in cost:
        if num_items(item) < cost[item]:
            return False
    return True

if can_afford(Entities.Carrot):
    if get_ground_type() != Grounds.Soil:
        till()
    plant(Entities.Carrot)
""",
        javascript="""
function canAfford(thing) {
  const cost = getCost(thing);
  for (const item in cost) {
    if (numItems(item) < cost[item]) return false;
  }
  return true;
}

if (canAfford(Entities.Carrot)) {
  if (getGroundType() !== Grounds.Soil) till();
  plant(Entities.Carrot);
}
""",
        dart="""
bool canAfford(Object thing) {
  final cost = getCost(thing)!;
  for (final item in cost.keys) {
    if (numItems(item) < cost[item]!) {
      return false;
    }
  }
  return true;
}

void main() {
  if (canAfford(Entities.carrot)) {
    if (getGroundType() != Grounds.soil) {
      till();
    }
    plant(Entities.carrot);
  }
}
""",
    ),
)
