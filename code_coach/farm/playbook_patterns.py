"""Playbook tips on scanning, search, drones and speed (see playbook.py).

Seven groups: how to walk the field (scan orders), what to write down while
you do (remembering the field), searching a maze, working with drones,
measuring what a program costs, how to lay a program out, and the habits of a
fast run. Every snippet is a few helper functions and one example call, and is
run for real in tests/test_farm_playbook_patterns.py.

Two things are true of this clone and are written into the snippets:

* Every position is a number. A maze square is `x * n + y` (n = the field's
  size), so a set or a dictionary can be keyed by it in all four languages -
  JavaScript's objects turn a tuple key into text, and a Map would not match
  a list.
* Nothing a function does to a plain variable reaches the outside (the game's
  language has no `global`), so a counter that several functions add to is a
  list with one number in it.
"""

from __future__ import annotations

from code_coach.farm.playbook import (
    _HARVEST_COLUMN_DART,
    _HARVEST_COLUMN_JS,
    _HARVEST_COLUMN_PY,
    Entry,
    _entry,
)

# ── Pieces used by more than one entry ──────────────────────────────────

_GO_TO_PY = """
def go_to(x, y):
    n = get_world_size()
    for i in range((x - get_pos_x()) % n):
        move(East)
    for i in range((y - get_pos_y()) % n):
        move(North)
"""

_GO_TO_JS = """
function goTo(x, y) {
  const n = getWorldSize();
  for (const i of range((((x - getPosX()) % n) + n) % n)) move(East);
  for (const i of range((((y - getPosY()) % n) + n) % n)) move(North);
}
"""

_GO_TO_DART = """
void goTo(int x, int y) {
  final n = getWorldSize();
  for (final i in range((x - getPosX()) % n)) move(east);
  for (final i in range((y - getPosY()) % n)) move(north);
}
"""

#: The maze's squares are numbered x * n + y; a step North is +1, East +n.
_EXPLORE_PY = """
def cell():
    return get_pos_x() * get_world_size() + get_pos_y()

def explore(links):
    dirs = [North, East, South, West]
    here = cell()
    links[here] = []
    for i in range(4):
        if can_move(dirs[i]):
            links[here].append(i)
            move(dirs[i])
            if cell() not in links:
                explore(links)
            move(dirs[(i + 2) % 4])
"""

_EXPLORE_JS = """
const cell = () => getPosX() * getWorldSize() + getPosY();

function explore(links) {
  const dirs = [North, East, South, West];
  const here = cell();
  links.set(here, []);
  for (const i of range(4)) {
    if (!canMove(dirs[i])) continue;
    links.get(here).push(i);
    move(dirs[i]);
    if (!links.has(cell())) explore(links);
    move(dirs[(i + 2) % 4]);
  }
}
"""

_EXPLORE_DART = """
int cell() => getPosX() * getWorldSize() + getPosY();

void explore(Map<int, List<int>> links) {
  const dirs = [north, east, south, west];
  final here = cell();
  links[here] = [];
  for (final i in range(4)) {
    if (!canMove(dirs[i])) continue;
    links[here]!.add(i);
    move(dirs[i]);
    if (!links.containsKey(cell())) explore(links);
    move(dirs[(i + 2) % 4]);
  }
}
"""

# ── The entries ─────────────────────────────────────────────────────────

ENTRIES: tuple[Entry, ...] = (
    # ── Scan orders ─────────────────────────────────────────────────────
    _entry(
        "scan-loop", "Scan orders", "Sweep, and finish where you began",
        "A zig-zag sweep ends in a corner, but the farm wraps: one more step East lands you "
        "in column 0 and, on a field of odd size (where the sweep ends on the top row), one "
        "step North in row 0. That is n*n moves in all on an even field and n*n + 1 on an odd "
        "one, and the next pass starts from (0, 0). Walking back along every row instead "
        "would cost n*n + n.",
        ("Expand", "Speed", "Senses", "Debug", "Operators", "Variables", "Functions"),
        python="""
def work():
    quick_print(get_pos_x(), get_pos_y())

def sweep_and_home():
    n = get_world_size()
    for x in range(n):
        d = North if x % 2 == 0 else South
        for y in range(n - 1):
            work()
            move(d)
        work()
        if x < n - 1:
            move(East)
    move(East)            # off the last column: the wrap puts you in column 0
    if get_pos_y() > 0:
        move(North)       # off the top row (odd sizes): back on row 0

sweep_and_home()
""",
        javascript="""
function work() {
  quickPrint(getPosX(), getPosY());
}

function sweepAndHome() {
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
  move(East); // off the last column: the wrap puts you in column 0
  if (getPosY() > 0) move(North); // off the top row (odd sizes): back on row 0
}

sweepAndHome();
""",
        dart="""
void work() {
  quickPrint('${getPosX()},${getPosY()}');
}

void sweepAndHome() {
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
  move(east); // off the last column: the wrap puts you in column 0
  if (getPosY() > 0) {
    move(north); // off the top row (odd sizes): back on row 0
  }
}

void main() {
  sweepAndHome();
}
""",
    ),
    _entry(
        "scan-spiral", "Scan orders", "Spiral in from the corner",
        "Walk the outside of the field first and finish in the middle: sides of n-1, n-1, "
        "n-1, then n-2 twice, n-3 twice, and so on down to 1. It costs the same n*n - 1 moves "
        "as a zig-zag, so choose it for where it ends (the centre) and for doing the outer "
        "ring first - not to save moves.",
        ("Loops", "Expand", "Senses", "Debug", "Operators", "Variables", "Functions", "Lists"),
        python="""
def work():
    quick_print(get_pos_x(), get_pos_y())

def spiral():
    n = get_world_size()
    dirs = [North, East, South, West]
    d = 0
    length = n - 1    # three sides this long, then two of n - 2, two of n - 3 ...
    sides = 3
    work()
    while length > 0:
        for side in range(sides):
            for step in range(length):
                move(dirs[d])
                work()
            d = (d + 1) % 4
        length -= 1
        sides = 2

spiral()
""",
        javascript="""
function work() {
  quickPrint(getPosX(), getPosY());
}

function spiral() {
  const n = getWorldSize();
  const dirs = [North, East, South, West];
  let d = 0;
  let length = n - 1; // three sides this long, then two of n - 2, two of n - 3 ...
  let sides = 3;
  work();
  while (length > 0) {
    for (const side of range(sides)) {
      for (const step of range(length)) {
        move(dirs[d]);
        work();
      }
      d = (d + 1) % 4;
    }
    length -= 1;
    sides = 2;
  }
}

spiral();
""",
        dart="""
void work() {
  quickPrint('${getPosX()},${getPosY()}');
}

void spiral() {
  final n = getWorldSize();
  const dirs = [north, east, south, west];
  var d = 0;
  var length = n - 1; // three sides this long, then two of n - 2, two of n - 3 ...
  var sides = 3;
  work();
  while (length > 0) {
    for (final side in range(sides)) {
      for (final step in range(length)) {
        move(dirs[d]);
        work();
      }
      d = (d + 1) % 4;
    }
    length -= 1;
    sides = 2;
  }
}

void main() {
  spiral();
}
""",
    ),
    _entry(
        "scan-distance", "Scan orders", "How many moves away is a tile?",
        "On a wrapping field the way to a tile is never more than half the field on each "
        "axis: go East or West, whichever is shorter, and the same for North and South. Add "
        "the two and you know what a trip costs (200 ticks a move) before you take it - so "
        "you can walk to the nearest of several targets first.",
        ("Expand", "Speed", "Senses", "Debug", "Operators", "Variables", "Functions", "Lists"),
        python="""
def distance(x, y):
    n = get_world_size()
    dx = (x - get_pos_x()) % n
    dy = (y - get_pos_y()) % n
    if dx > n - dx:
        dx = n - dx         # shorter to go West
    if dy > n - dy:
        dy = n - dy         # shorter to go South
    return dx + dy

def nearest(spots):
    bx, by = spots[0]
    for sx, sy in spots:
        if distance(sx, sy) < distance(bx, by):
            bx = sx
            by = sy
    return (bx, by)

quick_print("moves to (5, 5):", distance(5, 5))
quick_print("nearest:", nearest([(5, 5), (2, 1), (4, 4)]))
""",
        javascript="""
function distance(x, y) {
  const n = getWorldSize();
  let dx = (((x - getPosX()) % n) + n) % n;
  let dy = (((y - getPosY()) % n) + n) % n;
  if (dx > n - dx) dx = n - dx; // shorter to go West
  if (dy > n - dy) dy = n - dy; // shorter to go South
  return dx + dy;
}

function nearest(spots) {
  let [bx, by] = spots[0];
  for (const [sx, sy] of spots) {
    if (distance(sx, sy) < distance(bx, by)) {
      bx = sx;
      by = sy;
    }
  }
  return [bx, by];
}

quickPrint("moves to (5, 5):", distance(5, 5));
quickPrint("nearest:", nearest([[5, 5], [2, 1], [4, 4]]));
""",
        dart="""
int distance(int x, int y) {
  final n = getWorldSize();
  var dx = (x - getPosX()) % n;
  var dy = (y - getPosY()) % n;
  if (dx > n - dx) dx = n - dx; // shorter to go West
  if (dy > n - dy) dy = n - dy; // shorter to go South
  return dx + dy;
}

(int, int) nearest(List<(int, int)> spots) {
  var (bx, by) = spots[0];
  for (final (sx, sy) in spots) {
    if (distance(sx, sy) < distance(bx, by)) {
      bx = sx;
      by = sy;
    }
  }
  return (bx, by);
}

void main() {
  quickPrint('moves to (5, 5): ${distance(5, 5)}');
  quickPrint('nearest: ${nearest([(5, 5), (2, 1), (4, 4)])}');
}
""",
    ),
    # ── Remembering the field ───────────────────────────────────────────
    _entry(
        "remember-spots", "Remembering the field", "Write down where, then go straight there",
        "Looking at a tile costs a move to reach it, so look once and keep the answer. This "
        "scans for dead pumpkins and puts each tile's (x, y) in a list; replanting then "
        "walks only between those tiles instead of sweeping the whole field again. A list of "
        "positions is the simplest map there is.",
        ("Expand", "Speed", "Plant", "Pumpkins", "Senses", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def find_dead():
    spots = []
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if get_entity_type() == Entities.Dead_Pumpkin:
                spots.append((x, y))
            move(North)
        move(East)
    return spots
""" + _GO_TO_PY + """
def replant(spots):
    for x, y in spots:
        go_to(x, y)
        plant(Entities.Pumpkin)

replant(find_dead())
""",
        javascript="""
function findDead() {
  const spots = [];
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (getEntityType() === Entities.DeadPumpkin) spots.push([x, y]);
      move(North);
    }
    move(East);
  }
  return spots;
}
""" + _GO_TO_JS + """
function replant(spots) {
  for (const [x, y] of spots) {
    goTo(x, y);
    plant(Entities.Pumpkin);
  }
}

replant(findDead());
""",
        dart="""
List<(int, int)> findDead() {
  final spots = <(int, int)>[];
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (getEntityType() == Entities.deadPumpkin) {
        spots.add((x, y));
      }
      move(north);
    }
    move(east);
  }
  return spots;
}
""" + _GO_TO_DART + """
void replant(List<(int, int)> spots) {
  for (final (x, y) in spots) {
    goTo(x, y);
    plant(Entities.pumpkin);
  }
}

void main() {
  replant(findDead());
}
""",
    ),
    _entry(
        "remember-petals", "Remembering the field", "Sort the sunflowers by petals once",
        "The slow way to harvest sunflowers biggest-first sweeps the field nine times, once "
        "for each petal count. Instead scan once, file every flower's position under its "
        "petal count in a dictionary of lists, then walk 15 down to 7 and visit only the "
        "tiles filed there. Keep at least 10 flowers standing as you go, or the biggest "
        "stops paying 8 times the power.",
        ("Expand", "Speed", "Sunflowers", "Senses", "Operators", "Variables", "Functions",
         "Lists", "Dictionaries"),
        python="""
def scan_petals():
    by_petals = {}
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            p = measure()
            if p != None:
                if p not in by_petals:
                    by_petals[p] = []
                by_petals[p].append((x, y))
            move(North)
        move(East)
    return by_petals
""" + _GO_TO_PY + """
def harvest_biggest_first(by_petals):
    for petals in range(15, 6, -1):
        if petals in by_petals:
            for x, y in by_petals[petals]:
                go_to(x, y)
                if can_harvest():
                    harvest()

harvest_biggest_first(scan_petals())
""",
        javascript="""
function scanPetals() {
  const byPetals = new Map();
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const p = measure();
      if (p !== null) {
        if (!byPetals.has(p)) byPetals.set(p, []);
        byPetals.get(p).push([x, y]);
      }
      move(North);
    }
    move(East);
  }
  return byPetals;
}
""" + _GO_TO_JS + """
function harvestBiggestFirst(byPetals) {
  for (const petals of range(15, 6, -1)) {
    if (byPetals.has(petals)) {
      for (const [x, y] of byPetals.get(petals)) {
        goTo(x, y);
        if (canHarvest()) harvest();
      }
    }
  }
}

harvestBiggestFirst(scanPetals());
""",
        dart="""
Map<int, List<(int, int)>> scanPetals() {
  final byPetals = <int, List<(int, int)>>{};
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final int? p = measure();
      if (p != null) {
        byPetals.putIfAbsent(p, () => []).add((x, y));
      }
      move(north);
    }
    move(east);
  }
  return byPetals;
}
""" + _GO_TO_DART + """
void harvestBiggestFirst(Map<int, List<(int, int)>> byPetals) {
  for (final petals in range(15, 6, -1)) {
    if (byPetals.containsKey(petals)) {
      for (final (x, y) in byPetals[petals]!) {
        goTo(x, y);
        if (canHarvest()) {
          harvest();
        }
      }
    }
  }
}

void main() {
  harvestBiggestFirst(scanPetals());
}
""",
    ),
    _entry(
        "remember-giants", "Remembering the field", "Count the giants with a set",
        "A set keeps each value once. Add every pumpkin's measure() id and what is left has "
        "one id per separate pumpkin or giant: 1 means the whole field has grown into a "
        "single giant, 9 means nine lone pumpkins. An unripe pumpkin counts as its own, a "
        "dead one gives None and is skipped.",
        ("Expand", "Speed", "Pumpkins", "Debug", "Operators", "Variables", "Functions",
         "Dictionaries"),
        python="""
def count_pumpkins():
    ids = set()
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            p = measure()
            if p != None:
                ids.add(p)
            move(North)
        move(East)
    return len(ids)

quick_print(count_pumpkins(), "separate pumpkins")
""",
        javascript="""
function countPumpkins() {
  const ids = new Set();
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const p = measure();
      if (p !== null) ids.add(p);
      move(North);
    }
    move(East);
  }
  return ids.size;
}

quickPrint(countPumpkins(), "separate pumpkins");
""",
        dart="""
int countPumpkins() {
  final ids = <int>{};
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final int? p = measure();
      if (p != null) {
        ids.add(p);
      }
      move(north);
    }
    move(east);
  }
  return ids.length;
}

void main() {
  quickPrint('${countPumpkins()} separate pumpkins');
}
""",
    ),
    _entry(
        "remember-census", "Remembering the field", "Take a census with a dictionary",
        "A dictionary maps a key to a count: here each kind of thing on the field to how many "
        "tiles hold it. Entities.Grass, Entities.Bush and the rest make good keys, and an "
        "empty tile's key is None. Ask `kind in counts` before reading a count that may not "
        "be there.",
        ("Expand", "Speed", "Senses", "Debug", "Operators", "Variables", "Functions",
         "Dictionaries"),
        python="""
def census():
    counts = {}
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            kind = get_entity_type()
            if kind in counts:
                counts[kind] += 1
            else:
                counts[kind] = 1
            move(North)
        move(East)
    return counts

def how_many(counts, kind):
    if kind in counts:
        return counts[kind]
    return 0

counts = census()
quick_print("grass:", how_many(counts, Entities.Grass))
quick_print("bushes:", how_many(counts, Entities.Bush))
""",
        javascript="""
function census() {
  const counts = new Map();
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      const kind = getEntityType();
      if (counts.has(kind)) {
        counts.set(kind, counts.get(kind) + 1);
      } else {
        counts.set(kind, 1);
      }
      move(North);
    }
    move(East);
  }
  return counts;
}

function howMany(counts, kind) {
  return counts.has(kind) ? counts.get(kind) : 0;
}

const counts = census();
quickPrint("grass:", howMany(counts, Entities.Grass));
quickPrint("bushes:", howMany(counts, Entities.Bush));
""",
        dart="""
Map<Entities?, int> census() {
  final counts = <Entities?, int>{};
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      final kind = getEntityType();
      if (counts.containsKey(kind)) {
        counts[kind] = counts[kind]! + 1;
      } else {
        counts[kind] = 1;
      }
      move(north);
    }
    move(east);
  }
  return counts;
}

int howMany(Map<Entities?, int> counts, Entities? kind) {
  return counts.containsKey(kind) ? counts[kind]! : 0;
}

void main() {
  final counts = census();
  final grass = howMany(counts, Entities.grass);
  final bushes = howMany(counts, Entities.bush);
  quickPrint('grass: $grass');
  quickPrint('bushes: $bushes');
}
""",
    ),
    # ── Maze search ─────────────────────────────────────────────────────
    _entry(
        "maze-dfs", "Maze search", "Depth-first search with a stack and a visited set",
        "The right-hand rule can circle for ever in a reused maze; this cannot. Keep a set "
        "of the squares you have stood on and a stack of the directions you took. Step to a "
        "neighbour you have not seen; when there is none, pop the stack and take the last "
        "step back. A square is numbered x * n + y, which is its own key in the set. Nothing "
        "is recursive, so even a big maze is safe. The two lines before the call grow the "
        "maze from a bush, as in Grow a maze from a bush; where a maze already stands they "
        "do nothing.",
        ("Loops", "Expand", "Plant", "Senses", "Speed", "Mazes", "Fertilizer", "Operators",
         "Variables", "Functions", "Lists", "Dictionaries"),
        python="""
def dfs_to_treasure():
    n = get_world_size()
    tx, ty = measure()
    dirs = [North, East, South, West]
    dx = [0, 1, 0, -1]
    dy = [1, 0, -1, 0]
    seen = set()
    path = []              # the way back: the direction numbers we took
    while get_pos_x() != tx or get_pos_y() != ty:
        x = get_pos_x()
        y = get_pos_y()
        seen.add(x * n + y)
        moved = False
        for i in range(4):
            if can_move(dirs[i]) and (x + dx[i]) * n + y + dy[i] not in seen:
                path.append(i)
                move(dirs[i])
                moved = True
                break
        if not moved:
            move(dirs[(path.pop() + 2) % 4])   # dead end: undo the last step

plant(Entities.Bush)
use_item(Items.Weird_Substance, get_world_size())   # grow a maze around you
dfs_to_treasure()
harvest()
""",
        javascript="""
function dfsToTreasure() {
  const n = getWorldSize();
  const [tx, ty] = measure();
  const dirs = [North, East, South, West];
  const dx = [0, 1, 0, -1];
  const dy = [1, 0, -1, 0];
  const seen = new Set();
  const path = []; // the way back: the direction numbers we took
  while (getPosX() !== tx || getPosY() !== ty) {
    const x = getPosX();
    const y = getPosY();
    seen.add(x * n + y);
    let moved = false;
    for (const i of range(4)) {
      if (canMove(dirs[i]) && !seen.has((x + dx[i]) * n + y + dy[i])) {
        path.push(i);
        move(dirs[i]);
        moved = true;
        break;
      }
    }
    if (!moved) move(dirs[(path.pop() + 2) % 4]); // dead end: undo the last step
  }
}

plant(Entities.Bush);
useItem(Items.WeirdSubstance, getWorldSize()); // grow a maze around you
dfsToTreasure();
harvest();
""",
        dart="""
void dfsToTreasure() {
  final n = getWorldSize();
  final (tx, ty) = measure() as (int, int);
  const dirs = [north, east, south, west];
  const dx = [0, 1, 0, -1];
  const dy = [1, 0, -1, 0];
  final seen = <int>{};
  final path = <int>[]; // the way back: the direction numbers we took
  while (getPosX() != tx || getPosY() != ty) {
    final x = getPosX();
    final y = getPosY();
    seen.add(x * n + y);
    var moved = false;
    for (final i in range(4)) {
      if (canMove(dirs[i]) && !seen.contains((x + dx[i]) * n + y + dy[i])) {
        path.add(i);
        move(dirs[i]);
        moved = true;
        break;
      }
    }
    if (!moved) {
      move(dirs[(path.removeLast() + 2) % 4]); // dead end: undo the last step
    }
  }
}

void main() {
  plant(Entities.bush);
  useItem(Items.weirdSubstance, getWorldSize()); // grow a maze around you
  dfsToTreasure();
  harvest();
}
""",
    ),
    _entry(
        "maze-map", "Maze search", "Map the whole maze into a dictionary",
        "Go down every open passage, step back out, and write down for each square which of "
        "the four directions are open (numbered 0 to 3 as North, East, South, West). It costs "
        "4 moves a passage, since both ends look at it, but then the map answers any question "
        "about the maze without moving: shortest routes, dead ends, where the treasure is. A "
        "reused maze only ever gains passages, so an old map still shows a way, if not always "
        "the shortest.",
        ("Expand", "Plant", "Senses", "Speed", "Debug", "Mazes", "Fertilizer", "Operators",
         "Variables", "Functions", "Lists", "Dictionaries"),
        python=_EXPLORE_PY + """
plant(Entities.Bush)
use_item(Items.Weird_Substance, get_world_size())   # grow a maze around you
links = {}
explore(links)
quick_print(len(links), "squares mapped")
""",
        javascript=_EXPLORE_JS + """
plant(Entities.Bush);
useItem(Items.WeirdSubstance, getWorldSize()); // grow a maze around you
const links = new Map();
explore(links);
quickPrint(links.size, "squares mapped");
""",
        dart=_EXPLORE_DART + """
void main() {
  plant(Entities.bush);
  useItem(Items.weirdSubstance, getWorldSize()); // grow a maze around you
  final links = <int, List<int>>{};
  explore(links);
  quickPrint('${links.length} squares mapped');
}
""",
    ),
    _entry(
        "maze-shortest", "Maze search", "Shortest way to the treasure: breadth-first search",
        "Depth-first finds a way; breadth-first finds the shortest. With the maze mapped, "
        "search outwards from the treasure with a queue - first every square one step away, "
        "then two, and so on - and note at each square the direction that leads back towards "
        "the treasure. Then just follow those notes from where you stand, and harvest() on "
        "arrival. A square's neighbours are +1 (North), +n (East), -1 (South) and -n (West) "
        "in its number. The two lines before the mapping grow the maze from a bush, and do "
        "nothing where one already stands.",
        ("Loops", "Expand", "Plant", "Senses", "Speed", "Mazes", "Fertilizer", "Operators",
         "Variables", "Functions", "Lists", "Dictionaries"),
        python=_EXPLORE_PY + """
def way_to(links, goal):
    n = get_world_size()
    steps = [1, n, -1, -n]       # North, East, South, West as a change of square number
    toward = {goal: 0}           # square -> the direction that leads towards the goal
    queue = [goal]
    while len(queue) > 0:
        here = queue.pop(0)
        for i in links[here]:
            if here + steps[i] not in toward:
                toward[here + steps[i]] = (i + 2) % 4
                queue.append(here + steps[i])
    return toward

plant(Entities.Bush)
use_item(Items.Weird_Substance, get_world_size())   # grow a maze around you
links = {}
explore(links)
tx, ty = measure()
goal = tx * get_world_size() + ty
toward = way_to(links, goal)
while cell() != goal:
    move([North, East, South, West][toward[cell()]])
""",
        javascript=_EXPLORE_JS + """
function wayTo(links, goal) {
  const steps = [1, getWorldSize(), -1, -getWorldSize()]; // North, East, South, West as a change of square number
  const toward = new Map([[goal, 0]]); // square -> the direction that leads towards the goal
  const queue = [goal];
  while (queue.length > 0) {
    const here = queue.shift();
    for (const i of links.get(here)) {
      if (toward.has(here + steps[i])) continue;
      toward.set(here + steps[i], (i + 2) % 4);
      queue.push(here + steps[i]);
    }
  }
  return toward;
}

plant(Entities.Bush);
useItem(Items.WeirdSubstance, getWorldSize()); // grow a maze around you
const links = new Map();
explore(links);
const [tx, ty] = measure();
const goal = tx * getWorldSize() + ty;
const toward = wayTo(links, goal);
while (cell() !== goal) {
  move([North, East, South, West][toward.get(cell())]);
}
""",
        dart=_EXPLORE_DART + """
Map<int, int> wayTo(Map<int, List<int>> links, int goal) {
  final steps = [1, getWorldSize(), -1, -getWorldSize()]; // North, East, South, West as a change of square number
  final toward = <int, int>{goal: 0}; // square -> the direction that leads towards the goal
  final queue = [goal];
  while (queue.isNotEmpty) {
    final here = queue.removeAt(0);
    for (final i in links[here]!) {
      if (toward.containsKey(here + steps[i])) continue;
      toward[here + steps[i]] = (i + 2) % 4;
      queue.add(here + steps[i]);
    }
  }
  return toward;
}

void main() {
  plant(Entities.bush);
  useItem(Items.weirdSubstance, getWorldSize()); // grow a maze around you
  final links = <int, List<int>>{};
  explore(links);
  final (tx, ty) = measure() as (int, int);
  final goal = tx * getWorldSize() + ty;
  final toward = wayTo(links, goal);
  while (cell() != goal) move([north, east, south, west][toward[cell()]!]);
}
""",
    ),
    # ── Drone teams ─────────────────────────────────────────────────────
    _entry(
        "drones-stripes", "Drone teams", "Split the field into stripes, one drone each",
        "Cut the field into stripes of whole columns, as many as max_drones() allows. Spawn "
        "a drone standing at each stripe's first column - it starts where you stand and "
        "works the columns from there - and do the last stripe yourself. With 4 drones on "
        "6 columns the field takes the time of 2 columns, not 6. If spawn_drone() answers "
        "None there is no drone free, so do that stripe yourself.",
        ("Loops", "Expand", "Speed", "Senses", "Megafarm", "Operators", "Variables",
         "Functions"),
        python="""
def stripe_width():                       # columns per drone, rounded up
    drones = max_drones()
    return (get_world_size() + drones - 1) // drones

def work_stripe():                        # from the column you stand in
    count = stripe_width()
    if get_pos_x() + count > get_world_size():
        count = get_world_size() - get_pos_x()
    for c in range(count):
        for y in range(get_world_size()):
            if can_harvest():
                harvest()
            move(North)
        move(East)

def split_field():
    width = stripe_width()
    x = 0
    while x < get_world_size():
        helper = None
        if x + width < get_world_size():
            helper = spawn_drone(work_stripe)      # every stripe but the last
        if helper == None:
            work_stripe()       # the last one, or no drone free: do it yourself
        else:
            for c in range(width):
                move(East)
        x += width

split_field()
""",
        javascript="""
function stripeWidth() { // columns per drone, rounded up
  const drones = maxDrones();
  return Math.floor((getWorldSize() + drones - 1) / drones);
}

function workStripe() { // from the column you stand in
  let count = stripeWidth();
  if (getPosX() + count > getWorldSize()) count = getWorldSize() - getPosX();
  for (const c of range(count)) {
    for (const y of range(getWorldSize())) {
      if (canHarvest()) harvest();
      move(North);
    }
    move(East);
  }
}

function splitField() {
  const width = stripeWidth();
  let x = 0;
  while (x < getWorldSize()) {
    let helper = null;
    if (x + width < getWorldSize()) helper = spawnDrone(workStripe); // every stripe but the last
    if (helper === null) {
      workStripe(); // the last one, or no drone free: do it yourself
    } else {
      for (const c of range(width)) move(East);
    }
    x += width;
  }
}

splitField();
""",
        dart="""
int stripeWidth() { // columns per drone, rounded up
  final drones = maxDrones();
  return (getWorldSize() + drones - 1) ~/ drones;
}

void workStripe() { // from the column you stand in
  var count = stripeWidth();
  if (getPosX() + count > getWorldSize()) count = getWorldSize() - getPosX();
  for (final c in range(count)) {
    for (final y in range(getWorldSize())) {
      if (canHarvest()) harvest();
      move(north);
    }
    move(east);
  }
}

void splitField() {
  final width = stripeWidth();
  var x = 0;
  while (x < getWorldSize()) {
    int? helper;
    if (x + width < getWorldSize()) helper = spawnDrone(workStripe); // every stripe but the last
    if (helper == null) {
      workStripe(); // the last one, or no drone free: do it yourself
    } else {
      for (final c in range(width)) move(east);
    }
    x += width;
  }
}

void main() {
  splitField();
}
""",
    ),
    _entry(
        "drones-crops", "Drone teams", "A different crop for each drone",
        "A drone can be handed anything a function takes, game values included, so one "
        "function can grow whatever you pass it. This sends a helper to each column with "
        "its own crop - carrots here, bushes there - and does the column itself when no "
        "drone is free. Each helper starts where you stood when you spawned it; wait_for() "
        "lets them all finish.",
        ("Expand", "Plant", "Carrots", "Senses", "Speed", "Megafarm", "Operators", "Variables",
         "Functions", "Lists"),
        python="""
def grow_column(crop):
    for y in range(get_world_size()):
        if crop == Entities.Carrot and get_ground_type() != Grounds.Soil:
            till()
        plant(crop)
        move(North)

crops = [Entities.Carrot, Entities.Bush]      # a column of each
helpers = []
for crop in crops:
    helper = spawn_drone(grow_column, crop)
    if helper == None:
        grow_column(crop)       # no drone free: this column is yours
    else:
        helpers.append(helper)
    move(East)
for helper in helpers:
    wait_for(helper)
""",
        javascript="""
function growColumn(crop) {
  for (const y of range(getWorldSize())) {
    if (crop === Entities.Carrot && getGroundType() !== Grounds.Soil) till();
    plant(crop);
    move(North);
  }
}

const crops = [Entities.Carrot, Entities.Bush]; // a column of each
const helpers = [];
for (const crop of crops) {
  const helper = spawnDrone(growColumn, crop);
  if (helper === null) {
    growColumn(crop); // no drone free: this column is yours
  } else {
    helpers.push(helper);
  }
  move(East);
}
for (const helper of helpers) {
  waitFor(helper);
}
""",
        dart="""
void growColumn(Entities crop) {
  for (final y in range(getWorldSize())) {
    if (crop == Entities.carrot && getGroundType() != Grounds.soil) {
      till();
    }
    plant(crop);
    move(north);
  }
}

void main() {
  final crops = [Entities.carrot, Entities.bush]; // a column of each
  final helpers = <int>[];
  for (final crop in crops) {
    final helper = spawnDrone(growColumn, [crop]);
    if (helper == null) {
      growColumn(crop); // no drone free: this column is yours
    } else {
      helpers.add(helper);
    }
    move(east);
  }
  for (final helper in helpers) {
    waitFor(helper);
  }
}
""",
    ),
    _entry(
        "drones-return", "Drone teams", "Drones that report back",
        "Whatever a spawned function returns is what wait_for() hands you, so a drone can be "
        "sent to look at a column and come back with the answer. Keep the handles in a list, "
        "do any column nobody is free for yourself, then add up the answers. Drones share no "
        "variables, so returning a value is how they tell you anything.",
        ("Expand", "Speed", "Megafarm", "Debug", "Operators", "Variables", "Functions",
         "Lists"),
        python="""
def count_ripe():
    total = 0
    for y in range(get_world_size()):
        if can_harvest():
            total += 1
        move(North)
    return total

def ripe_tiles():
    total = 0
    helpers = []
    for x in range(get_world_size()):
        helper = spawn_drone(count_ripe)
        if helper == None:
            total += count_ripe()      # nobody free: count this column yourself
        else:
            helpers.append(helper)
        move(East)
    for helper in helpers:
        total += wait_for(helper)      # each helper hands back its column's count
    return total

quick_print(ripe_tiles(), "ripe tiles")
""",
        javascript="""
function countRipe() {
  let total = 0;
  for (const y of range(getWorldSize())) {
    if (canHarvest()) total += 1;
    move(North);
  }
  return total;
}

function ripeTiles() {
  let total = 0;
  const helpers = [];
  for (const x of range(getWorldSize())) {
    const helper = spawnDrone(countRipe);
    if (helper === null) {
      total += countRipe(); // nobody free: count this column yourself
    } else {
      helpers.push(helper);
    }
    move(East);
  }
  for (const helper of helpers) {
    total += waitFor(helper); // each helper hands back its column's count
  }
  return total;
}

quickPrint(ripeTiles(), "ripe tiles");
""",
        dart="""
int countRipe() {
  var total = 0;
  for (final y in range(getWorldSize())) {
    if (canHarvest()) {
      total += 1;
    }
    move(north);
  }
  return total;
}

int ripeTiles() {
  var total = 0;
  final helpers = <int>[];
  for (final x in range(getWorldSize())) {
    final helper = spawnDrone(countRipe);
    if (helper == null) {
      total += countRipe(); // nobody free: count this column yourself
    } else {
      helpers.add(helper);
    }
    move(east);
  }
  for (final helper in helpers) {
    total += waitFor(helper) as int; // each helper hands back its column's count
  }
  return total;
}

void main() {
  quickPrint('${ripeTiles()} ripe tiles');
}
""",
    ),
    _entry(
        "drones-poll", "Drone teams", "Keep one helper busy with has_finished",
        "has_finished(handle) answers at once whether a drone has returned, where wait_for() "
        "would stop you until it had. Check it as you pass each column: while the helper is "
        "still busy the column is yours, and the moment it is free you hand it the next one. "
        "You count as a drone yourself, so with max_drones() of 2 there is one helper.",
        ("Expand", "Speed", "Megafarm", "Operators", "Variables", "Functions"),
        python=_HARVEST_COLUMN_PY + """
def feed_the_helper():
    helper = None
    for x in range(get_world_size()):
        if helper != None and not has_finished(helper):
            harvest_column()           # the helper is still busy: this one is mine
        else:
            helper = spawn_drone(harvest_column)   # it is free again: hand it a column
            if helper == None:
                harvest_column()       # no drone to hand it to
        move(East)
    if helper != None:
        wait_for(helper)

feed_the_helper()
""",
        javascript=_HARVEST_COLUMN_JS + """
function feedTheHelper() {
  let helper = null;
  for (const x of range(getWorldSize())) {
    if (helper !== null && !hasFinished(helper)) {
      harvestColumn(); // the helper is still busy: this one is mine
    } else {
      helper = spawnDrone(harvestColumn); // it is free again: hand it a column
      if (helper === null) harvestColumn(); // no drone to hand it to
    }
    move(East);
  }
  if (helper !== null) waitFor(helper);
}

feedTheHelper();
""",
        dart=_HARVEST_COLUMN_DART + """
void feedTheHelper() {
  int? helper;
  for (final x in range(getWorldSize())) {
    if (helper != null && !hasFinished(helper)) {
      harvestColumn(); // the helper is still busy: this one is mine
    } else {
      helper = spawnDrone(harvestColumn); // it is free again: hand it a column
      if (helper == null) {
        harvestColumn(); // no drone to hand it to
      }
    }
    move(east);
  }
  if (helper != null) {
    waitFor(helper);
  }
}

void main() {
  feedTheHelper();
}
""",
    ),
    # ── Measuring your program ──────────────────────────────────────────
    _entry(
        "measure-ticks", "Measuring your program", "Time a block in ticks",
        "get_tick_count() counts the ticks your program has used so far, so the difference "
        "across a block is exactly what the block cost: 200 for each move, plant, harvest or "
        "till, and 1 for each question or failed action. Hand the block to a helper as a "
        "function and time anything with the same few lines. In Original your own sums and "
        "loops add a few ticks too.",
        ("Expand", "Timing", "Debug", "Operators", "Variables", "Functions"),
        python="""
def ticks_of(job):
    start = get_tick_count()
    job()
    return get_tick_count() - start

def three_moves():
    move(North)
    move(North)
    move(East)

quick_print("ticks:", ticks_of(three_moves))
""",
        javascript="""
function ticksOf(job) {
  const start = getTickCount();
  job();
  return getTickCount() - start;
}

function threeMoves() {
  move(North);
  move(North);
  move(East);
}

quickPrint("ticks:", ticksOf(threeMoves));
""",
        dart="""
int ticksOf(void Function() job) {
  final start = getTickCount();
  job();
  return getTickCount() - start;
}

void threeMoves() {
  move(north);
  move(north);
  move(east);
}

void main() {
  quickPrint('ticks: ${ticksOf(threeMoves)}');
}
""",
    ),
    _entry(
        "measure-seconds", "Measuring your program", "Time a block in game seconds",
        "get_time() is game seconds since the farm began, so the difference across a block is "
        "how long it really took - and each Speed level shortens it, where the tick count "
        "stays the same. A flip is always exactly 1 second whatever your speed, a move is "
        "200 ticks: 0.5 seconds with no upgrades, a third of a second at Speed 1.",
        ("Expand", "Timing", "Debug", "Operators", "Variables", "Functions"),
        python="""
def seconds_of(job):
    start = get_time()
    job()
    return get_time() - start

def flip_and_step():
    do_a_flip()
    move(North)

quick_print("seconds:", seconds_of(flip_and_step))
""",
        javascript="""
function secondsOf(job) {
  const start = getTime();
  job();
  return getTime() - start;
}

function flipAndStep() {
  doAFlip();
  move(North);
}

quickPrint("seconds:", secondsOf(flipAndStep));
""",
        dart="""
double secondsOf(void Function() job) {
  final start = getTime();
  job();
  return getTime() - start;
}

void flipAndStep() {
  doAFlip();
  move(north);
}

void main() {
  quickPrint('seconds: ${secondsOf(flipAndStep)}');
}
""",
    ),
    _entry(
        "measure-counter", "Measuring your program", "Count your moves in a list",
        "A function cannot change a plain variable that lives outside it - assigning makes a "
        "new one - but it can change what is inside a list. So a counter is a list holding "
        "one number: moves = [0], and moves[0] += 1 anywhere adds to it. Count only the "
        "moves that happened (move() answers False when it is blocked).",
        ("Expand", "Speed", "Debug", "Operators", "Variables", "Functions", "Lists"),
        python="""
moves = [0]

def step(direction):
    if move(direction):
        moves[0] += 1

def zig_zag():
    n = get_world_size()
    for x in range(n):
        for y in range(n - 1):
            step(North if x % 2 == 0 else South)
        if x < n - 1:
            step(East)

zig_zag()
quick_print("moves:", moves[0])
""",
        javascript="""
const moves = [0];

function step(direction) {
  if (move(direction)) moves[0] += 1;
}

function zigZag() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n - 1)) {
      step(x % 2 === 0 ? North : South);
    }
    if (x < n - 1) step(East);
  }
}

zigZag();
quickPrint("moves:", moves[0]);
""",
        dart="""
final moves = [0];

void step(Direction direction) {
  if (move(direction)) {
    moves[0] += 1;
  }
}

void zigZag() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n - 1)) {
      step(x % 2 == 0 ? north : south);
    }
    if (x < n - 1) {
      step(east);
    }
  }
}

void main() {
  zigZag();
  quickPrint('moves: ${moves[0]}');
}
""",
    ),
    _entry(
        "measure-simulate", "Measuring your program", "Race two ways of doing it with simulate()",
        "simulate(file, research, items, globals, seed, speedup) runs one of your files on a "
        "fresh farm of its own and answers with the game seconds it took, leaving your real "
        "farm exactly as it was. Here the file races itself: it is the real program when it "
        "owns Simulation, and a trial when it does not, doing whichever of two ways its "
        "`trial` global names. Speedup 0 means as fast as it goes. In this example the file is "
        "called main.",
        ("Expand", "Speed", "Senses", "Debug", "Simulation", "Operators", "Variables",
         "Functions", "Dictionaries"),
        python="""
def naive():
    for x in range(get_world_size()):
        for y in range(get_world_size()):
            move(North)
        move(East)

def zig_zag():
    for x in range(get_world_size()):
        for y in range(get_world_size() - 1):
            move(North if x % 2 == 0 else South)
        move(East)

if num_unlocked(Unlocks.Simulation) == 0:   # in a trial you own only what you were given
    if trial == 1:
        naive()
    else:
        zig_zag()
else:
    research = {Unlocks.Expand: 3, Unlocks.Senses: 1}
    quick_print("naive:", simulate("main", research, {}, {"trial": 1}, 0, 0), "seconds")
    quick_print("zig-zag:", simulate("main", research, {}, {"trial": 2}, 0, 0), "seconds")
""",
        javascript="""
function naive() {
  for (const x of range(getWorldSize())) {
    for (const y of range(getWorldSize())) move(North);
    move(East);
  }
}

function zigZag() {
  for (const x of range(getWorldSize())) {
    for (const y of range(getWorldSize() - 1)) move(x % 2 === 0 ? North : South);
    move(East);
  }
}

if (numUnlocked(Unlocks.Simulation) === 0) { // in a trial you own only what you were given
  if (trial === 1) {
    naive();
  } else {
    zigZag();
  }
} else {
  const research = { [Unlocks.Expand]: 3, [Unlocks.Senses]: 1 };
  quickPrint("naive:", simulate("main", research, {}, { trial: 1 }, 0, 0), "seconds");
  quickPrint("zig-zag:", simulate("main", research, {}, { trial: 2 }, 0, 0), "seconds");
}
""",
        dart="""
void naive() {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize())) {
      move(north);
    }
    move(east);
  }
}

void zigZag() {
  for (final x in range(getWorldSize())) {
    for (final y in range(getWorldSize() - 1)) {
      move(x % 2 == 0 ? north : south);
    }
    move(east);
  }
}

void main() {
  if (numUnlocked(Unlocks.simulation) == 0) { // in a trial you own only what you were given
    if (simGlobals['trial'] == 1) {
      naive();
    } else {
      zigZag();
    }
  } else {
    final research = {Unlocks.expand: 3, Unlocks.senses: 1};
    quickPrint('naive: ${simulate('main', research, {}, {'trial': 1}, 0, 0)} seconds');
    quickPrint('zig-zag: ${simulate('main', research, {}, {'trial': 2}, 0, 0)} seconds');
  }
}
""",
    ),
    # ── Structure ───────────────────────────────────────────────────────
    _entry(
        "structure-machine", "Structure", "A tiny state machine for the main loop",
        "A program that never ends is easiest to keep straight as a state and a function that "
        "does one step and says which state comes next: plant, wait, harvest, plant... Add "
        "states without tangling the loop. This one stops after two harvests so it can be "
        "tried; change the loop to `while True:` to run for ever.",
        ("Loops", "Speed", "Plant", "Operators", "Variables", "Functions"),
        python="""
PLANT = 0
WAIT = 1
HARVEST = 2

def step(state):
    if state == PLANT:
        plant(Entities.Bush)
        return WAIT
    if state == WAIT:
        if can_harvest():
            return HARVEST
        return WAIT
    harvest()
    return PLANT

state = PLANT
harvests = 0
while harvests < 2:         # `while True:` to run for ever
    state = step(state)
    if state == PLANT:
        harvests += 1
""",
        javascript="""
const PLANT = 0;
const WAIT = 1;
const HARVEST = 2;

function step(state) {
  if (state === PLANT) {
    plant(Entities.Bush);
    return WAIT;
  }
  if (state === WAIT) {
    if (canHarvest()) return HARVEST;
    return WAIT;
  }
  harvest();
  return PLANT;
}

let state = PLANT;
let harvests = 0;
while (harvests < 2) { // `while (true)` to run for ever
  state = step(state);
  if (state === PLANT) harvests += 1;
}
""",
        dart="""
const plantState = 0;
const waitState = 1;
const harvestState = 2;

int step(int state) {
  if (state == plantState) {
    plant(Entities.bush);
    return waitState;
  }
  if (state == waitState) {
    if (canHarvest()) {
      return harvestState;
    }
    return waitState;
  }
  harvest();
  return plantState;
}

void main() {
  var state = plantState;
  var harvests = 0;
  while (harvests < 2) { // `while (true)` to run for ever
    state = step(state);
    if (state == plantState) {
      harvests += 1;
    }
  }
}
""",
    ),
    _entry(
        "structure-constants", "Structure", "Settings at the top, no numbers in the code",
        "Put what you will want to change - the crop, how many columns - in CAPITALS at the "
        "top, and read the field's size with get_world_size() instead of typing 3 or 6. "
        "Then one edit changes the program, and the same code still works after you buy "
        "Expand.",
        ("Expand", "Plant", "Variables", "Functions"),
        python="""
CROP = Entities.Bush      # what to grow
COLUMNS = 2               # how many columns of it

def plant_column(crop):
    for y in range(get_world_size()):
        plant(crop)
        move(North)

def plant_columns(crop, columns):
    for c in range(columns):
        plant_column(crop)
        move(East)

plant_columns(CROP, COLUMNS)
""",
        javascript="""
const CROP = Entities.Bush; // what to grow
const COLUMNS = 2; // how many columns of it

function plantColumn(crop) {
  for (const y of range(getWorldSize())) {
    plant(crop);
    move(North);
  }
}

function plantColumns(crop, columns) {
  for (const c of range(columns)) {
    plantColumn(crop);
    move(East);
  }
}

plantColumns(CROP, COLUMNS);
""",
        dart="""
const crop = Entities.bush; // what to grow
const columns = 2; // how many columns of it

void plantColumn(Entities kind) {
  for (final y in range(getWorldSize())) {
    plant(kind);
    move(north);
  }
}

void plantColumns(Entities kind, int count) {
  for (final c in range(count)) {
    plantColumn(kind);
    move(east);
  }
}

void main() {
  plantColumns(crop, columns);
}
""",
    ),
    _entry(
        "structure-import", "Structure", "Helpers in a second file",
        "Press the + beside the file tabs and add a file called tools. This is what goes in "
        "it: a setting and a helper that runs any job on every tile in a zig-zag. In main "
        "(this needs the Import research) write `import tools` and then "
        "`tools.for_each_tile(tools.plant_it)`. Run always runs the file you have open, and "
        "every file sees the farm's own names without importing them.",
        ("Expand", "Speed", "Plant", "Operators", "Variables", "Functions"),
        python="""
# The file "tools". In main:  import tools
#                             tools.for_each_tile(tools.plant_it)
CROP = Entities.Bush

def plant_it():
    plant(CROP)

def for_each_tile(job):
    n = get_world_size()
    for x in range(n):
        d = North if x % 2 == 0 else South
        for y in range(n - 1):
            job()
            move(d)
        job()
        if x < n - 1:
            move(East)
""",
        javascript="""
// The file "tools". In main:  import { forEachTile, plantIt } from "./tools.js";
//                             forEachTile(plantIt);
export const CROP = Entities.Bush;

export function plantIt() {
  plant(CROP);
}

export function forEachTile(job) {
  const n = getWorldSize();
  for (const x of range(n)) {
    const d = x % 2 === 0 ? North : South;
    for (const y of range(n - 1)) {
      job();
      move(d);
    }
    job();
    if (x < n - 1) move(East);
  }
}
""",
        dart="""
// The file "tools". In main:  import 'tools.dart';
//                             forEachTile(plantIt);
const crop = Entities.bush;

void plantIt() {
  plant(crop);
}

void forEachTile(void Function() job) {
  final n = getWorldSize();
  for (final x in range(n)) {
    final d = x % 2 == 0 ? north : south;
    for (final y in range(n - 1)) {
      job();
      move(d);
    }
    job();
    if (x < n - 1) {
      move(east);
    }
  }
}

void main() {} // Run starts main(), so a file you may Run needs one; main.dart's own wins
""",
    ),
    _entry(
        "structure-guard", "Structure", "One program for before and after an upgrade",
        "A command you have not researched stops the run only when it is reached, so guard it "
        "with num_unlocked(): ask for a drone only when Megafarm is yours, and otherwise do "
        "the work yourself. The same file then runs before the upgrade and gets faster after "
        "it, with nothing to edit.",
        ("Expand", "Speed", "Senses", "Megafarm", "Operators", "Variables", "Functions"),
        python="""
def harvest_column():
    for y in range(get_world_size()):
        if can_harvest():
            harvest()
        move(North)

def harvest_field():
    for x in range(get_world_size()):
        helped = False
        if num_unlocked(Unlocks.Megafarm) > 0:   # only ask for a drone you may have
            helped = spawn_drone(harvest_column) != None
        if not helped:
            harvest_column()
        move(East)

harvest_field()
""",
        javascript="""
function harvestColumn() {
  for (const y of range(getWorldSize())) {
    if (canHarvest()) harvest();
    move(North);
  }
}

function harvestField() {
  for (const x of range(getWorldSize())) {
    let helped = false;
    if (numUnlocked(Unlocks.Megafarm) > 0) { // only ask for a drone you may have
      helped = spawnDrone(harvestColumn) !== null;
    }
    if (!helped) harvestColumn();
    move(East);
  }
}

harvestField();
""",
        dart="""
void harvestColumn() {
  for (final y in range(getWorldSize())) {
    if (canHarvest()) {
      harvest();
    }
    move(north);
  }
}

void harvestField() {
  for (final x in range(getWorldSize())) {
    var helped = false;
    if (numUnlocked(Unlocks.megafarm) > 0) { // only ask for a drone you may have
      helped = spawnDrone(harvestColumn) != null;
    }
    if (!helped) {
      harvestColumn();
    }
    move(east);
  }
}

void main() {
  harvestField();
}
""",
    ),
    # ── Speed runs ──────────────────────────────────────────────────────
    _entry(
        "speed-moving", "Speed runs", "Do not stand and wait: walk on",
        "The clock runs while you wait, and every tile grows at its own pace. Walk the field "
        "and harvest and replant only what is ripe as you pass; whatever is still growing "
        "gets another look on the next lap, and you lose nothing. Standing on one tile until "
        "it is ripe leaves every other tile growing with nobody to harvest it.",
        ("Expand", "Speed", "Plant", "Variables", "Functions"),
        python="""
def tend_field():
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if can_harvest():
                harvest()
                plant(Entities.Bush)
            move(North)
        move(East)

for lap in range(3):
    tend_field()
""",
        javascript="""
function tendField() {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      if (canHarvest()) {
        harvest();
        plant(Entities.Bush);
      }
      move(North);
    }
    move(East);
  }
}

for (const lap of range(3)) {
  tendField();
}
""",
        dart="""
void tendField() {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      if (canHarvest()) {
        harvest();
        plant(Entities.bush);
      }
      move(north);
    }
    move(east);
  }
}

void main() {
  for (final lap in range(3)) {
    tendField();
  }
}
""",
    ),
    _entry(
        "speed-waiting", "Speed runs", "If you must wait, wait with a question",
        "When there is truly nothing else to do, wait by asking: can_harvest() costs 1 tick, "
        "so you harvest within a tick of it being ripe. do_a_flip() as a wait always takes "
        "a whole second, so on average half a second goes to waste. Never harvest by guess: "
        "an unripe plant is destroyed.",
        ("Loops", "Speed", "Plant", "Operators", "Functions"),
        python="""
def wait_then_harvest():
    while not can_harvest():
        pass              # one tick a look
    harvest()

plant(Entities.Bush)
wait_then_harvest()
""",
        javascript="""
function waitThenHarvest() {
  while (!canHarvest()) {} // one tick a look
  harvest();
}

plant(Entities.Bush);
waitThenHarvest();
""",
        dart="""
void waitThenHarvest() {
  while (!canHarvest()) {} // one tick a look
  harvest();
}

void main() {
  plant(Entities.bush);
  waitThenHarvest();
}
""",
    ),
    _entry(
        "speed-till", "Speed runs", "Till once, plant for ever",
        "Soil stays soil when you harvest, so tilling is a job for the first lap only: 200 "
        "ticks a tile that you pay once. Do it in one sweep before the loop. (till() on soil "
        "turns it back into grass, which is why the first sweep checks the ground first.) "
        "The laps after it only harvest and plant.",
        ("Expand", "Speed", "Plant", "Carrots", "Senses", "Operators", "Variables",
         "Functions"),
        python="""
def sweep(job):
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            job()
            move(North)
        move(East)

def prepare():
    if get_ground_type() != Grounds.Soil:
        till()

def farm():
    if can_harvest():
        harvest()
    plant(Entities.Carrot)

sweep(prepare)
for lap in range(3):
    sweep(farm)
""",
        javascript="""
function sweep(job) {
  const n = getWorldSize();
  for (const x of range(n)) {
    for (const y of range(n)) {
      job();
      move(North);
    }
    move(East);
  }
}

function prepare() {
  if (getGroundType() !== Grounds.Soil) till();
}

function farm() {
  if (canHarvest()) harvest();
  plant(Entities.Carrot);
}

sweep(prepare);
for (const lap of range(3)) {
  sweep(farm);
}
""",
        dart="""
void sweep(void Function() job) {
  final n = getWorldSize();
  for (final x in range(n)) {
    for (final y in range(n)) {
      job();
      move(north);
    }
    move(east);
  }
}

void prepare() {
  if (getGroundType() != Grounds.soil) {
    till();
  }
}

void farm() {
  if (canHarvest()) {
    harvest();
  }
  plant(Entities.carrot);
}

void main() {
  sweep(prepare);
  for (final lap in range(3)) {
    sweep(farm);
  }
}
""",
    ),
    _entry(
        "speed-water", "Speed runs", "Water the field before the loop",
        "Wet ground grows plants up to 5 times as fast, and each use_item(Items.Water) adds "
        "a quarter tank. Four to the tile fills it; it then dries by about 1% a second. "
        "Do one watering sweep before you plant, so the whole first crop grows fast, and "
        "stop when the barn runs out instead of spinning. New water arrives every 10 seconds.",
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

water_field(0.75)
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

waterField(0.75);
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
  waterField(0.75);
}
""",
    ),
)
