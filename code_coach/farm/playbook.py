"""The Farm playbook: short tips and paste-able snippets, in all four languages.

Each entry is a tip and the same small piece of code four times - the game's
own language (Original), Python, JavaScript and Dart - written the way each
is written. A snippet is a helper function and one example call, so pasting
it into the editor and pressing Run does something you can see.

`needs` names the research (keys of data.UNLOCKS) a snippet cannot run
without: the functions it calls, and the parts of the language it uses -
loops, if, operators, variables, functions, lists - which the research
tree sells as well. `levels` says when one level is not enough: every
snippet that moves needs Expand level 2, the square farm, which is also
where get_world_size() and `for` arrive. tests/test_farm_playbook.py holds
each snippet to its `needs` with the real language gate and the real farm.

Everything here is true of this clone, not only of the game: where the two
differ (what wraps, what the maze does when you reuse it) the clone wins.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

LANGUAGES = ("original", "python", "javascript", "dart")

#: Expand level 2 is the first square farm - and where `for` and
#: get_world_size() come from.
SQUARE_FARM = {"Expand": 2}


@dataclass(frozen=True)
class Entry:
    id: str
    group: str
    title: str
    tip: str
    #: Research that must be bought first (keys of data.UNLOCKS).
    needs: tuple[str, ...]
    #: Language -> code.
    snippets: dict[str, str] = field(default_factory=dict)

    @property
    def levels(self) -> dict[str, int]:
        """The level of a need when level 1 is not enough."""
        return {name: level for name, level in SQUARE_FARM.items() if name in self.needs}

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "group": self.group,
            "title": self.title,
            "tip": self.tip,
            "needs": list(self.needs),
            "levels": self.levels,
            "snippets": dict(self.snippets),
        }


def _entry(
    id: str,
    group: str,
    title: str,
    tip: str,
    needs: tuple[str, ...],
    python: str,
    javascript: str,
    dart: str,
    original: str | None = None,
) -> Entry:
    """An entry. Original is Python's syntax, so it takes Python's snippet unless given its own."""
    snippets = {
        "original": (python if original is None else original).strip("\n") + "\n",
        "python": python.strip("\n") + "\n",
        "javascript": javascript.strip("\n") + "\n",
        "dart": dart.strip("\n") + "\n",
    }
    return Entry(id, group, title, tip, needs, snippets)


# ── Pieces used by more than one entry ──────────────────────────────────

_FULLY_MERGED_PY = """
def fully_merged():
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)
    first = measure()   # the pumpkin's id at (0, 0)
    move(West)          # off the West edge: wraps to x = size - 1
    move(South)         # off the South edge: wraps to y = size - 1
    last = measure()
    return first != None and first == last
"""

_FULLY_MERGED_JS = """
function fullyMerged() {
  while (getPosX() > 0) move(West);
  while (getPosY() > 0) move(South);
  const first = measure(); // the pumpkin's id at (0, 0)
  move(West); // off the West edge: wraps to x = size - 1
  move(South); // off the South edge: wraps to y = size - 1
  const last = measure();
  return first !== null && first === last;
}
"""

_FULLY_MERGED_DART = """
bool fullyMerged() {
  while (getPosX() > 0) {
    move(west);
  }
  while (getPosY() > 0) {
    move(south);
  }
  final first = measure(); // the pumpkin's id at (0, 0)
  move(west); // off the West edge: wraps to x = size - 1
  move(south); // off the South edge: wraps to y = size - 1
  final last = measure();
  return first != null && first == last;
}
"""

_HARVEST_COLUMN_PY = """
def harvest_column():
    for i in range(get_world_size()):
        if can_harvest():
            harvest()
        move(North)
"""

_HARVEST_COLUMN_JS = """
function harvestColumn() {
  for (const i of range(getWorldSize())) {
    if (canHarvest()) harvest();
    move(North);
  }
}
"""

_HARVEST_COLUMN_DART = """
void harvestColumn() {
  for (final i in range(getWorldSize())) {
    if (canHarvest()) {
      harvest();
    }
    move(north);
  }
}
"""

# ── The entries ─────────────────────────────────────────────────────────

ENTRIES: tuple[Entry, ...] = (
    # ── Moving ──────────────────────────────────────────────────────────
    _entry(
        "move-go-to", "Moving", "Go to a tile the short way round",
        "The farm wraps: walk off one edge and you arrive on the opposite one, so no tile "
        "is ever more than half the field away. This works out the short way on each axis "
        "(East or West, North or South) and walks it. x grows to the East, y to the North, "
        "and (0, 0) is the bottom-left corner.",
        ("Expand", "Speed", "Senses", "Operators", "Variables", "Functions"),
        python="""
def go_to(x, y):
    n = get_world_size()
    dx = (x - get_pos_x()) % n   # steps East; the other way round is n - dx
    dy = (y - get_pos_y()) % n
    if dx > n // 2:
        for i in range(n - dx):
            move(West)
    else:
        for i in range(dx):
            move(East)
    if dy > n // 2:
        for i in range(n - dy):
            move(South)
    else:
        for i in range(dy):
            move(North)

go_to(2, 1)
""",
        javascript="""
function goTo(x, y) {
  const n = getWorldSize();
  const dx = (((x - getPosX()) % n) + n) % n; // steps East (JavaScript's % can be negative)
  const dy = (((y - getPosY()) % n) + n) % n;
  if (dx > n / 2) {
    for (const i of range(n - dx)) move(West);
  } else {
    for (const i of range(dx)) move(East);
  }
  if (dy > n / 2) {
    for (const i of range(n - dy)) move(South);
  } else {
    for (const i of range(dy)) move(North);
  }
}

goTo(2, 1);
""",
        dart="""
void goTo(int x, int y) {
  final n = getWorldSize();
  final dx = (x - getPosX()) % n; // steps East; Dart's % is never negative
  final dy = (y - getPosY()) % n;
  if (dx > n / 2) {
    for (final i in range(n - dx)) {
      move(west);
    }
  } else {
    for (final i in range(dx)) {
      move(east);
    }
  }
  if (dy > n / 2) {
    for (final i in range(n - dy)) {
      move(south);
    }
  } else {
    for (final i in range(dy)) {
      move(north);
    }
  }
}

void main() {
  goTo(2, 1);
}
""",
    ),
    _entry(
        "move-sweep", "Moving", "Sweep the whole field without a wasted move",
        "A field of n by n tiles needs only n*n - 1 moves: up one column, a step East, down "
        "the next, and so on. Put what you do on each tile in work(); this one just says "
        "where it is. Moving costs 200 ticks, so a zig-zag beats walking back to the start "
        "of every row.",
        ("Expand", "Speed", "Senses", "Debug", "Operators", "Variables", "Functions"),
        python="""
def work():
    quick_print(get_pos_x(), get_pos_y())

def sweep():
    n = get_world_size()
    for x in range(n):
        d = North if x % 2 == 0 else South
        for y in range(n - 1):
            work()
            move(d)
        work()
        if x < n - 1:
            move(East)

sweep()
""",
        javascript="""
function work() {
  quickPrint(getPosX(), getPosY());
}

function sweep() {
  const n = getWorldSize();
  for (const x of range(n)) {
    const d = x % 2 === 0 ? North : South;
    for (const y of range(n - 1)) {
      work();
      move(d);
    }
    work();
    if (x < n - 1) move(East);
  }
}

sweep();
""",
        dart="""
void work() {
  quickPrint('${getPosX()},${getPosY()}');
}

void sweep() {
  final n = getWorldSize();
  for (final x in range(n)) {
    final d = x % 2 == 0 ? north : south;
    for (final y in range(n - 1)) {
      work();
      move(d);
    }
    work();
    if (x < n - 1) {
      move(east);
    }
  }
}

void main() {
  sweep();
}
""",
    ),
    _entry(
        "move-wrap", "Moving", "Wrap round to the far corner",
        "Moving off an edge wraps round, so from (0, 0) one step West and one step South "
        "lands on the far corner, (size - 1, size - 1): two moves instead of walking all "
        "the way. Handy for checking both ends of the field.",
        ("Loops", "Expand", "Senses", "Operators", "Functions"),
        python="""
def far_corner():
    while get_pos_x() > 0:
        move(West)
    while get_pos_y() > 0:
        move(South)
    move(West)    # off the West edge: wraps to x = size - 1
    move(South)   # off the South edge: wraps to y = size - 1

far_corner()
""",
        javascript="""
function farCorner() {
  while (getPosX() > 0) move(West);
  while (getPosY() > 0) move(South);
  move(West); // off the West edge: wraps to x = size - 1
  move(South); // off the South edge: wraps to y = size - 1
}

farCorner();
""",
        dart="""
void farCorner() {
  while (getPosX() > 0) {
    move(west);
  }
  while (getPosY() > 0) {
    move(south);
  }
  move(west); // off the West edge: wraps to x = size - 1
  move(south); // off the South edge: wraps to y = size - 1
}

void main() {
  farCorner();
}
""",
    ),
    # ── Planting ────────────────────────────────────────────────────────
    _entry(
        "plant-harvest-replant", "Planting", "Harvest only what is ripe, then replant",
        "harvest() on something unripe destroys it, so ask can_harvest() first: a question "
        "costs 1 tick, a harvest 200. Plant again straight after harvesting so no tile sits "
        "empty. Grass is ripe after half a second, so this also turns a field of grass into "
        "bushes.",
        ("Expand", "Speed", "Plant", "Functions"),
        python="""
def tend_column(crop):
    for i in range(get_world_size()):
        if can_harvest():
            harvest()
            plant(crop)
        move(North)

tend_column(Entities.Bush)
""",
        javascript="""
function tendColumn(crop) {
  for (const i of range(getWorldSize())) {
    if (canHarvest()) {
      harvest();
      plant(crop);
    }
    move(North);
  }
}

tendColumn(Entities.Bush);
""",
        dart="""
void tendColumn(Entities crop) {
  for (final i in range(getWorldSize())) {
    if (canHarvest()) {
      harvest();
      plant(crop);
    }
    move(north);
  }
}

void main() {
  tendColumn(Entities.bush);
}
""",
    ),
    _entry(
        "plant-till", "Planting", "Till first, then plant",
        "Carrots, pumpkins, sunflowers and cacti only grow in soil. till() turns grassland "
        "into soil - and soil back into grassland, so look at get_ground_type() before you "
        "call it.",
        ("Plant", "Carrots", "Senses", "Speed", "Operators", "Functions"),
        python="""
def plant_crop(crop):
    if get_ground_type() != Grounds.Soil:
        till()
    plant(crop)

plant_crop(Entities.Carrot)
""",
        javascript="""
function plantCrop(crop) {
  if (getGroundType() !== Grounds.Soil) till();
  plant(crop);
}

plantCrop(Entities.Carrot);
""",
        dart="""
void plantCrop(Entities crop) {
  if (getGroundType() != Grounds.soil) {
    till();
  }
  plant(crop);
}

void main() {
  plantCrop(Entities.carrot);
}
""",
    ),
    _entry(
        "plant-water", "Planting", "Water only when it is dry",
        "Each use_item(Items.Water) adds a quarter tank to the ground under you, up to 1, "
        "and wet ground grows plants up to five times as fast. The water drains away slowly, "
        "so top up when the level falls below a threshold instead of on every visit. The "
        "barn gets fresh water every 10 seconds.",
        ("Loops", "Watering", "Senses", "Operators", "Functions"),
        python="""
def top_up(level):
    while get_water() < level and num_items(Items.Water) > 0:
        use_item(Items.Water)

top_up(0.75)
""",
        javascript="""
function topUp(level) {
  while (getWater() < level && numItems(Items.Water) > 0) {
    useItem(Items.Water);
  }
}

topUp(0.75);
""",
        dart="""
void topUp(double level) {
  while (getWater() < level && numItems(Items.water) > 0) {
    useItem(Items.water);
  }
}

void main() {
  topUp(0.75);
}
""",
    ),
    _entry(
        "plant-companion", "Planting", "Plant what the plant next door wants",
        "Grass, bushes, trees and carrots each want a particular neighbour, on one particular "
        "tile within three steps. get_companion() says which plant and where, or None if it "
        "wants nothing. Plant exactly that there and the harvest comes out five times "
        "bigger.",
        ("Polyculture", "Debug", "Speed", "Operators", "Variables", "Functions"),
        python="""
def show_companion():
    companion = get_companion()
    if companion == None:
        quick_print("nothing wanted here")
    else:
        kind, spot = companion
        quick_print("wants", kind, "at", spot)

show_companion()
""",
        javascript="""
function showCompanion() {
  const companion = getCompanion();
  if (companion === null) {
    quickPrint("nothing wanted here");
  } else {
    const [kind, spot] = companion;
    quickPrint("wants", kind, "at", spot);
  }
}

showCompanion();
""",
        dart="""
void showCompanion() {
  final companion = getCompanion();
  if (companion == null) {
    quickPrint('nothing wanted here');
  } else {
    final (kind, spot) = companion;
    quickPrint('wants $kind at $spot');
  }
}

void main() {
  showCompanion();
}
""",
    ),
    # ── Pumpkins ────────────────────────────────────────────────────────
    _entry(
        "pumpkin-square", "Pumpkins", "Plant a pumpkin on every tile",
        "Ripe pumpkins that make a solid square grow into one giant pumpkin, so plant the "
        "whole field: the bigger the square, the bigger the giant. Pumpkins need soil and "
        "cost carrots, and about one in five dies as it ripens.",
        ("Expand", "Plant", "Carrots", "Pumpkins", "Senses", "Speed", "Operators",
         "Variables", "Functions"),
        python="""
def plant_pumpkins():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Pumpkin)
            move(North)
        move(East)

plant_pumpkins()
""",
        javascript="""
function plantPumpkins() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getGroundType() !== Grounds.Soil) till();
      plant(Entities.Pumpkin);
      move(North);
    }
    move(East);
  }
}

plantPumpkins();
""",
        dart="""
void plantPumpkins() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getGroundType() != Grounds.soil) {
        till();
      }
      plant(Entities.pumpkin);
      move(north);
    }
    move(east);
  }
}

void main() {
  plantPumpkins();
}
""",
    ),
    _entry(
        "pumpkin-merged", "Pumpkins", "Is the whole field one giant pumpkin?",
        "Every pumpkin in a giant reports the same id from measure(). When the whole field "
        "is one giant, (0, 0) and the far corner report the same id - two looks instead of "
        "checking every tile. An unripe pumpkin reports an id of its own and a dead one "
        "reports None, so a yes cannot be wrong. Harvest only then: a giant is worth far "
        "more than the same pumpkins one by one (3 by 3 gives 27, not 9). A cheap first "
        "look: if can_harvest() is false on the tile you are standing on, there is nothing "
        "to check yet - but a yes there proves nothing about the rest.",
        ("Loops", "Expand", "Senses", "Speed", "Pumpkins", "Operators", "Variables",
         "Functions"),
        python=_FULLY_MERGED_PY + """
if fully_merged():
    harvest()
""",
        javascript=_FULLY_MERGED_JS + """
if (fullyMerged()) harvest();
""",
        dart=_FULLY_MERGED_DART + """
void main() {
  if (fullyMerged()) {
    harvest();
  }
}
""",
    ),
    _entry(
        "pumpkin-loop", "Pumpkins", "Grow one giant, replace the dead, harvest once",
        "The whole routine: sweep the field, plant (or replant) every tile that is not a "
        "living pumpkin, and go round again until the two corners agree. Planting over a "
        "dead pumpkin is allowed, so there is nothing to clear. Then one harvest() takes "
        "the lot.",
        ("Loops", "Expand", "Plant", "Carrots", "Pumpkins", "Senses", "Speed", "Operators",
         "Variables", "Functions"),
        python=_FULLY_MERGED_PY + """
def tend_pumpkins():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_entity_type() != Entities.Pumpkin:   # empty, or dead
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
            move(North)
        move(East)

while not fully_merged():
    tend_pumpkins()
harvest()
""",
        javascript=_FULLY_MERGED_JS + """
function tendPumpkins() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getEntityType() !== Entities.Pumpkin) { // empty, or dead
        if (getGroundType() !== Grounds.Soil) till();
        plant(Entities.Pumpkin);
      }
      move(North);
    }
    move(East);
  }
}

while (!fullyMerged()) tendPumpkins();
harvest();
""",
        dart=_FULLY_MERGED_DART + """
void tendPumpkins() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getEntityType() != Entities.pumpkin) { // empty, or dead
        if (getGroundType() != Grounds.soil) {
          till();
        }
        plant(Entities.pumpkin);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  while (!fullyMerged()) {
    tendPumpkins();
  }
  harvest();
}
""",
    ),
    # ── Sunflowers ──────────────────────────────────────────────────────
    _entry(
        "sunflower-biggest-first", "Sunflowers", "Harvest the biggest sunflowers first",
        "measure() gives a sunflower's petals, 7 to 15. The flower with the most petals pays "
        "8 times the power - but only while 10 or more sunflowers are on the field, and "
        "harvesting a smaller one while a bigger one still stands spoils the next bonus. So "
        "go round once for each petal count, from 15 down to 7. (A faster way: scan once, "
        "remember where the flowers are in a list, and go straight to the biggest.)",
        ("Expand", "Speed", "Sunflowers", "Operators", "Variables", "Functions"),
        python="""
def harvest_biggest_first():
    n = get_world_size()
    for petals in range(15, 6, -1):
        for x in range(n):
            for y in range(n):
                if measure() == petals and can_harvest():
                    harvest()
                move(North)
            move(East)

harvest_biggest_first()
""",
        javascript="""
function harvestBiggestFirst() {
  const n = getWorldSize();
  for (let petals = 15; petals >= 7; petals--) {
    for (const x of range(n)) {
      for (const y of range(n)) {
        if (measure() === petals && canHarvest()) harvest();
        move(North);
      }
      move(East);
    }
  }
}

harvestBiggestFirst();
""",
        dart="""
void harvestBiggestFirst() {
  final n = getWorldSize();
  for (var petals = 15; petals >= 7; petals--) {
    for (final x in range(n)) {
      for (final y in range(n)) {
        if (measure() == petals && canHarvest()) {
          harvest();
        }
        move(north);
      }
      move(east);
    }
  }
}

void main() {
  harvestBiggestFirst();
}
""",
    ),
    # ── Cactus ──────────────────────────────────────────────────────────
    _entry(
        "cactus-sort", "Cactus", "Sort the cacti with swap()",
        "Cacti have a size from 0 to 9 (measure()). A patch counts as sorted when every "
        "neighbour to the North and East is at least as big as the tile, and every one to "
        "the South and West at most as big. Compare each tile with its North and East "
        "neighbours, swap when they are the wrong way round, and repeat until a whole pass "
        "swaps nothing. One harvest() then takes the whole sorted patch: n cacti pay n "
        "squared. Never compare across the edge - the field wraps, the sorting does not. "
        "Start from a field of planted cacti (soil, Entities.Cactus on every tile).",
        ("Loops", "Expand", "Speed", "Cactus", "Operators", "Variables", "Functions"),
        python="""
def sort_pass():
    n = get_world_size()
    swapped = False
    for x in range(n):
        for y in range(n):
            if y < n - 1 and measure(North) < measure():
                swap(North)
                swapped = True
            if x < n - 1 and measure(East) < measure():
                swap(East)
                swapped = True
            move(North)
        move(East)
    return swapped

while sort_pass():
    pass
harvest()
""",
        javascript="""
function sortPass() {
  const n = getWorldSize();
  let swapped = false;
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (y < n - 1 && measure(North) < measure()) {
        swap(North);
        swapped = true;
      }
      if (x < n - 1 && measure(East) < measure()) {
        swap(East);
        swapped = true;
      }
      move(North);
    }
    move(East);
  }
  return swapped;
}

while (sortPass()) {}
harvest();
""",
        dart="""
bool sortPass() {
  final n = getWorldSize();
  var swapped = false;
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (y < n - 1 && measure(north) < measure()) {
        swap(north);
        swapped = true;
      }
      if (x < n - 1 && measure(east) < measure()) {
        swap(east);
        swapped = true;
      }
      move(north);
    }
    move(east);
  }
  return swapped;
}

void main() {
  while (sortPass()) {}
  harvest();
}
""",
    ),
    # ── Maze ────────────────────────────────────────────────────────────
    _entry(
        "maze-grow", "Maze", "Grow a maze from a bush",
        "Plant a bush and use Weird Substance on it: the bush becomes a hedge maze with a "
        "treasure inside, and you are standing in it. Give the field size times 2 for each "
        "Mazes level past the first - that fills the whole field; less makes a smaller "
        "maze. Weird Substance comes from fertilized plants. Harvest on the treasure and "
        "you get gold equal to the maze's area (doubling with each Mazes level).",
        ("Expand", "Plant", "Senses", "Mazes", "Fertilizer", "Operators", "Variables",
         "Functions"),
        python="""
def grow_maze():
    per_cell = 1
    for i in range(num_unlocked(Unlocks.Mazes) - 1):
        per_cell *= 2
    plant(Entities.Bush)
    use_item(Items.Weird_Substance, get_world_size() * per_cell)

grow_maze()
""",
        javascript="""
function growMaze() {
  let perCell = 1;
  for (const i of range(numUnlocked(Unlocks.Mazes) - 1)) perCell *= 2;
  plant(Entities.Bush);
  useItem(Items.WeirdSubstance, getWorldSize() * perCell);
}

growMaze();
""",
        dart="""
void growMaze() {
  var perCell = 1;
  for (final i in range(numUnlocked(Unlocks.mazes) - 1)) {
    perCell *= 2;
  }
  plant(Entities.bush);
  useItem(Items.weirdSubstance, getWorldSize() * perCell);
}

void main() {
  growMaze();
}
""",
    ),
    _entry(
        "maze-right-hand", "Maze", "Follow the right-hand wall to the treasure",
        "can_move(direction) says whether a hedge is in the way. Keep your right hand on the "
        "wall: try turning right, then straight on, then left, then back. A new maze has no "
        "loops, so this reaches every square, the treasure included. measure() gives the "
        "treasure's (x, y), so you know when to stop; harvest() there for the gold.",
        ("Loops", "Expand", "Senses", "Speed", "Mazes", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def walk_to_treasure():
    dirs = [North, East, South, West]
    facing = 0
    tx, ty = measure()
    while get_pos_x() != tx or get_pos_y() != ty:
        for turn in [1, 0, 3, 2]:   # right, straight, left, back
            heading = (facing + turn) % 4
            if can_move(dirs[heading]):
                facing = heading
                move(dirs[facing])
                break

walk_to_treasure()
harvest()
""",
        javascript="""
function walkToTreasure() {
  const dirs = [North, East, South, West];
  let facing = 0;
  const [tx, ty] = measure();
  while (getPosX() !== tx || getPosY() !== ty) {
    for (const turn of [1, 0, 3, 2]) { // right, straight, left, back
      const heading = (facing + turn) % 4;
      if (canMove(dirs[heading])) {
        facing = heading;
        move(dirs[facing]);
        break;
      }
    }
  }
}

walkToTreasure();
harvest();
""",
        dart="""
void walkToTreasure() {
  const dirs = [north, east, south, west];
  var facing = 0;
  final (tx, ty) = measure() as (int, int);
  while (getPosX() != tx || getPosY() != ty) {
    for (final turn in [1, 0, 3, 2]) { // right, straight, left, back
      final heading = (facing + turn) % 4;
      if (canMove(dirs[heading])) {
        facing = heading;
        move(dirs[facing]);
        break;
      }
    }
  }
}

void main() {
  walkToTreasure();
  harvest();
}
""",
    ),
    _entry(
        "maze-reuse", "Maze", "Reuse the maze: move the treasure, keep the gold",
        "Standing on the treasure, use_item(Items.Weird_Substance, n) with the same n that "
        "grew the maze pays the gold and hides the treasure somewhere else - far cheaper "
        "than a new maze. Each time some hedges fall, so an old maze grows loops and the "
        "right-hand rule can circle for ever. Remember the squares you have been on instead "
        "(depth-first search) and back out of dead ends. harvest() on the last treasure pays "
        "once more and clears the maze; anywhere else in the maze it pays nothing.",
        ("Expand", "Senses", "Speed", "Mazes", "Fertilizer", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def cell():
    return get_pos_x() * 32 + get_pos_y()

def dfs(target, seen):
    if cell() == target:
        return True
    seen.append(cell())
    dirs = [North, East, South, West]
    for i in range(4):
        if can_move(dirs[i]):
            move(dirs[i])
            if cell() not in seen and dfs(target, seen):
                return True
            move(dirs[(i + 2) % 4])   # dead end or seen before: step back
    return False

def mine_gold(rounds, amount):
    for i in range(rounds):
        tx, ty = measure()
        dfs(tx * 32 + ty, [])
        if i < rounds - 1:
            use_item(Items.Weird_Substance, amount)   # pays, hides the treasure elsewhere
    harvest()   # the last treasure: pays, and the maze is gone

mine_gold(3, get_world_size())
""",
        javascript="""
function cell() {
  return getPosX() * 32 + getPosY();
}

function dfs(target, seen) {
  if (cell() === target) return true;
  seen.push(cell());
  const dirs = [North, East, South, West];
  for (let i = 0; i < 4; i++) {
    if (canMove(dirs[i])) {
      move(dirs[i]);
      if (!seen.includes(cell()) && dfs(target, seen)) return true;
      move(dirs[(i + 2) % 4]); // dead end or seen before: step back
    }
  }
  return false;
}

function mineGold(rounds, amount) {
  for (let i = 0; i < rounds; i++) {
    const [tx, ty] = measure();
    dfs(tx * 32 + ty, []);
    if (i < rounds - 1) useItem(Items.WeirdSubstance, amount); // pays, hides the treasure elsewhere
  }
  harvest(); // the last treasure: pays, and the maze is gone
}

mineGold(3, getWorldSize());
""",
        dart="""
int cell() => getPosX() * 32 + getPosY();

bool dfs(int target, List<int> seen) {
  if (cell() == target) return true;
  seen.add(cell());
  const dirs = [north, east, south, west];
  for (var i = 0; i < 4; i++) {
    if (canMove(dirs[i])) {
      move(dirs[i]);
      if (!seen.contains(cell()) && dfs(target, seen)) return true;
      move(dirs[(i + 2) % 4]); // dead end or seen before: step back
    }
  }
  return false;
}

void mineGold(int rounds, int amount) {
  for (var i = 0; i < rounds; i++) {
    final (tx, ty) = measure() as (int, int);
    dfs(tx * 32 + ty, <int>[]);
    if (i < rounds - 1) {
      useItem(Items.weirdSubstance, amount); // pays, hides the treasure elsewhere
    }
  }
  harvest(); // the last treasure: pays, and the maze is gone
}

void main() {
  mineGold(3, getWorldSize());
}
""",
    ),
    # ── Speed ───────────────────────────────────────────────────────────
    _entry(
        "speed-ticks", "Speed", "Count your ticks",
        "Time in the farm is counted in ticks, 400 to the second before speed upgrades. "
        "Moving, planting, harvesting and tilling take 200 each; asking a question "
        "(can_harvest, get_pos_x, measure) takes 1, and so does an action that fails. In "
        "Original, your own arithmetic and loops cost ticks too; in Python, JavaScript and "
        "Dart only the drone's commands do. get_tick_count() lets you time a change.",
        ("Expand", "Timing", "Debug", "Operators", "Variables"),
        python="""
start = get_tick_count()
for i in range(get_world_size()):
    move(North)
quick_print("ticks:", get_tick_count() - start)
""",
        javascript="""
const start = getTickCount();
for (const i of range(getWorldSize())) {
  move(North);
}
quickPrint("ticks:", getTickCount() - start);
""",
        dart="""
void main() {
  final start = getTickCount();
  for (final i in range(getWorldSize())) {
    move(north);
  }
  quickPrint('ticks: ${getTickCount() - start}');
}
""",
    ),
    _entry(
        "speed-drones", "Speed", "One drone per column",
        "spawn_drone(f) starts another drone where you stand, running f. It gives back the "
        "new drone's handle, or None when every drone is already out, so do the work "
        "yourself when it fails. f must be a function at the top level of your file, and "
        "drones share no variables - hand them what they need as arguments. max_drones() "
        "is how many you may have (each Megafarm level doubles it); num_drones() counts "
        "the ones out now.",
        ("Expand", "Megafarm", "Speed", "Operators", "Functions"),
        python=_HARVEST_COLUMN_PY + """
for i in range(get_world_size()):
    if spawn_drone(harvest_column) == None:
        harvest_column()   # no free drone: do this column yourself
    move(East)
""",
        javascript=_HARVEST_COLUMN_JS + """
for (const i of range(getWorldSize())) {
  if (spawnDrone(harvestColumn) === null) {
    harvestColumn(); // no free drone: do this column yourself
  }
  move(East);
}
""",
        dart=_HARVEST_COLUMN_DART + """
void main() {
  for (final i in range(getWorldSize())) {
    if (spawnDrone(harvestColumn) == null) {
      harvestColumn(); // no free drone: do this column yourself
    }
    move(east);
  }
}
""",
    ),
    _entry(
        "speed-wait", "Speed", "Work alongside a helper, then wait for it",
        "Spawn a helper on this column, step East and do the next one yourself - both at "
        "once. wait_for(handle) pauses you until the helper's function has returned and "
        "hands back what it returned; has_finished(handle) only peeks, so you can carry on "
        "meanwhile.",
        ("Expand", "Megafarm", "Speed", "Operators", "Variables", "Functions"),
        python=_HARVEST_COLUMN_PY + """
helper = spawn_drone(harvest_column)
if helper == None:
    harvest_column()   # no spare drone: do this column yourself
move(East)
harvest_column()
if helper != None:
    wait_for(helper)
""",
        javascript=_HARVEST_COLUMN_JS + """
const helper = spawnDrone(harvestColumn);
if (helper === null) harvestColumn(); // no spare drone: do this column yourself
move(East);
harvestColumn();
if (helper !== null) waitFor(helper);
""",
        dart=_HARVEST_COLUMN_DART + """
void main() {
  final helper = spawnDrone(harvestColumn);
  if (helper == null) {
    harvestColumn(); // no spare drone: do this column yourself
  }
  move(east);
  harvestColumn();
  if (helper != null) {
    waitFor(helper);
  }
}
""",
    ),
    # ── Tips ────────────────────────────────────────────────────────────
    _entry(
        "tip-flip", "Tips", "do_a_flip() is there from the start",
        "do_a_flip() and pet_the_piggy() need no research. Each takes exactly one second "
        "whatever your speed, which makes a flip an honest way to wait a second - or to "
        "see that your program is alive.",
        (),
        python="""
do_a_flip()
""",
        javascript="""
doAFlip();
""",
        dart="""
void main() {
  doAFlip();
}
""",
    ),
    _entry(
        "tip-unlocks", "Tips", "Ask what you have before you use it",
        "A function you have not researched stops the run with an \"isn't unlocked yet\" "
        "message that names the research. num_unlocked(Unlocks.Something) tells your code "
        "the level you have bought, so one program can run before and after an upgrade.",
        ("Senses", "Debug", "Speed", "Operators"),
        python="""
if num_unlocked(Unlocks.Pumpkins) > 0:
    quick_print("pumpkins are ready")
else:
    quick_print("research Pumpkins first")
""",
        javascript="""
if (numUnlocked(Unlocks.Pumpkins) > 0) {
  quickPrint("pumpkins are ready");
} else {
  quickPrint("research Pumpkins first");
}
""",
        dart="""
void main() {
  if (numUnlocked(Unlocks.pumpkins) > 0) {
    quickPrint('pumpkins are ready');
  } else {
    quickPrint('research Pumpkins first');
  }
}
""",
    ),
    _entry(
        "tip-quick-print", "Tips", "Debug with quick_print, not print",
        "print() writes in smoke above the drone and takes a second of game time. "
        "quick_print() writes to the output only and costs nothing, so use it to look "
        "inside a loop. Both come with Debug.",
        ("Debug",),
        python="""
quick_print("instant, in the output only")
print("one second, in smoke above the drone")
""",
        javascript="""
quickPrint("instant, in the output only");
print("one second, in smoke above the drone");
""",
        dart="""
void main() {
  quickPrint('instant, in the output only');
  print('one second, in smoke above the drone');
}
""",
    ),
    _entry(
        "tip-small-slow", "Tips", "Test small and slow",
        "set_world_size(3) shrinks (and clears) the farm for this run, so a test is quick; "
        "set_execution_speed(1) slows the drone to the speed you had before any upgrades, "
        "so you can watch it. Both are undone when the program ends. They come with "
        "Debug 2.",
        ("Debug_2",),
        python="""
set_world_size(3)
set_execution_speed(1)
""",
        javascript="""
setWorldSize(3);
setExecutionSpeed(1);
""",
        dart="""
void main() {
  setWorldSize(3);
  setExecutionSpeed(1);
}
""",
    ),
)

#: The groups, in the order the playbook shows them.
GROUPS = tuple(dict.fromkeys(entry.group for entry in ENTRIES))


def entries() -> list[dict[str, Any]]:
    """Every entry as plain data, ready to send to the screen."""
    return [entry.to_json() for entry in ENTRIES]
