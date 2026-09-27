"""The third Canvas track: Farm, after The Farmer Was Replaced.

Dodge and Breakout had you write the game. Here the game is written - a
drone on a grid of soil - and you write the program that plays it. That
turns the practice round: not "make this move on screen" but "make this
happen, in as few steps as you can", which is where loops, conditions,
functions and a little arithmetic stop being exercises and start being
the only sensible way to get the job done.

The farm is `WORLD`, loaded before your code. Your commands run straight
away, all of them, before anything is drawn; time on the farm is counted
in ticks, one per action, and crops ripen after so many ticks. The canvas
then replays what the drone did. A check reads `__farm` afterwards - what
was harvested, what was cut down unripe, how many ticks it took - and can
call your functions itself, the way step 6 calls goTo.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

WORLD = r"""// The farm. Everything you can call is a plain function; everything a
// check reads is on __farm. Commands happen at once; the picture replays
// them afterwards, so the program is finished before the drone moves.
var __farm = (function () {
  "use strict";
  const f = {
    w: 5, h: 5, x: 0, y: 0, grow: 20,
    ticks: 0, calls: 0, moves: 0, harvested: 0, wasted: 0, planted: 0,
    tiles: [], log: [],
  };

  function ripe(t) {
    return f.ticks - t.at >= t.grow;
  }
  function here() {
    return f.y * f.w + f.x;
  }
  function snap() {
    f.log.push({
      x: f.x, y: f.y, t: f.ticks, h: f.harvested,
      tiles: f.tiles.map((t) => (t ? (ripe(t) ? 2 : 1) : 0)).join(""),
    });
  }

  const api = {
    setup(o) {
      f.w = o.w || o.size || 5;
      f.h = o.h || o.size || 5;
      f.grow = o.grow || 20;
      f.tiles = [];
      for (let y = 0; y < f.h; y++) {
        for (let x = 0; x < f.w; x++) {
          const kind = o.tile ? o.tile(x, y) : "empty";
          if (kind === "ripe") f.tiles.push({ at: -f.grow, grow: f.grow });
          else if (kind === "young") f.tiles.push({ at: 0, grow: 1e9 });
          else f.tiles.push(null);
        }
      }
      snap();
    },
    get x() { return f.x; },
    get y() { return f.y; },
    get ticks() { return f.ticks; },
    get moves() { return f.moves; },
    get harvested() { return f.harvested; },
    get wasted() { return f.wasted; },
    get planted() { return f.planted; },
    get width() { return f.w; },
    get height() { return f.h; },
    /** 'empty', 'young' or 'ripe'. */
    at(x, y) {
      const t = f.tiles[y * f.w + x];
      return !t ? "empty" : ripe(t) ? "ripe" : "young";
    },
    count(kind) {
      let n = 0;
      for (let y = 0; y < f.h; y++) for (let x = 0; x < f.w; x++) if (api.at(x, y) === kind) n++;
      return n;
    },
    _raw: f,
  };
  return api;
})();

const __DIRS = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };

function move(direction) {
  const d = __DIRS[direction];
  if (!d) {
    throw new Error("move(" + JSON.stringify(direction) + ")? The directions are 'up', 'down', 'left' and 'right'.");
  }
  const f = __farm._raw;
  f.x = (f.x + d[0] + f.w) % f.w;
  f.y = (f.y + d[1] + f.h) % f.h;
  f.moves += 1;
  __farmTick();
}
function harvest() {
  const f = __farm._raw;
  const i = f.y * f.w + f.x;
  const t = f.tiles[i];
  if (t) {
    if (f.ticks - t.at >= t.grow) f.harvested += 1;
    else f.wasted += 1;
    f.tiles[i] = null;
  }
  __farmTick();
}
function plant() {
  const f = __farm._raw;
  const i = f.y * f.w + f.x;
  if (!f.tiles[i]) {
    f.tiles[i] = { at: f.ticks, grow: f.grow };
    f.planted += 1;
  }
  __farmTick();
}
function wait() {
  __farmTick();
}
function canHarvest() {
  __farmCount();
  return __farm.at(getX(), getY()) === "ripe";
}
function isEmpty() {
  __farmCount();
  return __farm.at(getX(), getY()) === "empty";
}
function getX() {
  __farmCount();
  return __farm._raw.x;
}
function getY() {
  __farmCount();
  return __farm._raw.y;
}
function getSize() {
  __farmCount();
  return __farm._raw.w;
}
function numHarvested() {
  __farmCount();
  return __farm._raw.harvested;
}

// Shared by the commands above: every command counts toward the limit -
// so a loop that never ends stops with a message instead of a frozen tab -
// and the ones that take time also move the clock on.
function __farmCount() {
  const f = __farm._raw;
  f.calls += 1;
  if (f.calls > 20000) {
    throw new Error("The drone has been given 20000 commands without the program finishing - is there a loop that never ends?");
  }
}
function __farmTick() {
  const f = __farm._raw;
  __farmCount();
  f.ticks += 1;
  f.log.push({
    x: f.x, y: f.y, t: f.ticks, h: f.harvested,
    tiles: f.tiles.map((t) => (t ? (f.ticks - t.at >= t.grow ? 2 : 1) : 0)).join(""),
  });
}

// The replay: the log, drawn at a pace that fits any program into ten
// seconds or so, and never faster than you can follow a short one.
(function () {
  const canvas = document.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  let shown = 0;
  let before = null;
  function draw(now) {
    const f = __farm._raw;
    const log = f.log;
    if (before === null) before = now;
    const perSecond = Math.max(6, log.length / 9);
    shown = Math.min(log.length - 1, shown + ((now - before) / 1000) * perSecond);
    before = now;
    const s = log[Math.floor(shown)] || log[log.length - 1];
    ctx.fillStyle = "#10141f";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (s) {
      const top = 30;
      const cell = Math.floor(Math.min(canvas.width / f.w, (canvas.height - top - 6) / f.h));
      const left = Math.floor((canvas.width - cell * f.w) / 2);
      for (let y = 0; y < f.h; y++) {
        for (let x = 0; x < f.w; x++) {
          const px = left + x * cell;
          const py = top + y * cell;
          ctx.fillStyle = "#4a3728";
          ctx.fillRect(px + 1, py + 1, cell - 2, cell - 2);
          const kind = s.tiles[y * f.w + x];
          if (kind !== "0") {
            ctx.fillStyle = kind === "2" ? "#f6ad55" : "#68d391";
            ctx.beginPath();
            ctx.arc(px + cell / 2, py + cell / 2, kind === "2" ? cell * 0.32 : cell * 0.14, 0, Math.PI * 2);
            ctx.fill();
          }
        }
      }
      ctx.strokeStyle = "#63b3ed";
      ctx.lineWidth = 3;
      ctx.strokeRect(left + s.x * cell + 3, top + s.y * cell + 3, cell - 6, cell - 6);
      ctx.fillStyle = "white";
      ctx.font = "14px monospace";
      const done = Math.floor(shown) >= log.length - 1 ? "   done" : "";
      ctx.fillText("Harvested " + s.h + "   Time " + s.t + done, 10, 20);
    }
    requestAnimationFrame(draw);
  }
  requestAnimationFrame(draw);
})();
"""


def _world(setup: str) -> str:
    return WORLD + "\n__farm.setup(" + setup + ");\n"


_API_1 = """// The drone starts on the top-left square.
// Commands: harvest()   move('right')   move('left')   move('up')   move('down')
"""

_F1 = """harvest();
move('right');
harvest();
move('right');
harvest();
"""

_F2 = """for (let i = 0; i < 12; i++) {
  harvest();
  move('right');
}
"""

_F3 = """for (let row = 0; row < 6; row++) {
  for (let col = 0; col < 6; col++) {
    harvest();
    move('right');
  }
  move('down');
}
"""

_F4 = """for (let row = 0; row < 5; row++) {
  for (let col = 0; col < 5; col++) {
    plant();
    move('right');
  }
  move('down');
}

for (let row = 0; row < 5; row++) {
  for (let col = 0; col < 5; col++) {
    harvest();
    move('right');
  }
  move('down');
}
"""

_F5 = """for (let row = 0; row < 6; row++) {
  for (let col = 0; col < 6; col++) {
    if (canHarvest()) harvest();
    move('right');
  }
  move('down');
}
"""

_F6 = """function goTo(x, y) {
  while (getX() < x) move('right');
  while (getX() > x) move('left');
  while (getY() < y) move('down');
  while (getY() > y) move('up');
}

goTo(4, 3);
harvest();
"""

_F7 = """function goTo(x, y) {
  const size = getSize();
  const right = (x - getX() + size) % size;
  if (right <= size / 2) {
    for (let i = 0; i < right; i++) move('right');
  } else {
    for (let i = 0; i < size - right; i++) move('left');
  }
  const down = (y - getY() + size) % size;
  if (down <= size / 2) {
    for (let i = 0; i < down; i++) move('down');
  } else {
    for (let i = 0; i < size - down; i++) move('up');
  }
}

goTo(4, 3);
harvest();
"""

_F8 = """while (numHarvested() < 50) {
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4; col++) {
      if (isEmpty()) plant();
      move('right');
    }
    move('down');
  }
  for (let row = 0; row < 4; row++) {
    for (let col = 0; col < 4; col++) {
      if (canHarvest()) harvest();
      move('right');
    }
    move('down');
  }
}
"""

_F9 = """function tend() {
  if (canHarvest()) harvest();
  if (isEmpty()) plant();
}

while (numHarvested() < 100) {
  for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 5; col++) {
      tend();
      move('right');
    }
    move('down');
  }
}
"""

_MIXED = (
    "{ size: 6, tile: (x, y) => ((x * 7 + y * 3) % 5 === 0 ? 'empty'"
    " : (x + 2 * y) % 3 === 0 ? 'young' : 'ripe') }"
)

FARM_STEPS: tuple[Step, ...] = (
    Step(
        id="farm-01-commands",
        track="Farm",
        title="Your first commands",
        teaches=(
            "This time the game is already written: a drone over a field. "
            "You write the program that flies it. harvest() picks the crop "
            "under the drone; move('right') - or 'left', 'up', 'down' - "
            "moves it one square. Your whole program runs first, then the "
            "canvas replays what the drone did. Ripe crops are orange; "
            "little green ones are still growing. x counts squares from "
            "the left and y from the TOP, like the canvas."
        ),
        goal="Harvest the three squares of the top row.",
        starter=_API_1,
        solution=_F1,
        check="""
const left = [0, 1, 2].filter((x) => __farm.at(x, 0) !== "empty");
expect(left.length === 0, `The top row still has crops at x ${left.join(", ")}. harvest() takes the square the drone is on, and move('right') goes one to the right.`);
expect(__farm.wasted === 0, "Something was cut down before it was ripe.");
""",
        hint="harvest(); move('right'); and again, and again.",
        world=_world("{ size: 3, tile: () => 'ripe' }"),
    ),
    Step(
        id="farm-02-loop",
        track="Farm",
        title="A loop does the repeating",
        teaches=(
            "Twelve squares is twenty-four lines written out, and you would "
            "get one wrong. A for loop runs its body again and again: for "
            "(let i = 0; i < 12; i++) { ... } runs it twelve times, with i "
            "counting 0 to 11. Put in the loop only what repeats. The field "
            "wraps around: move right off the edge and the drone comes back "
            "in on the left."
        ),
        goal="The top row is 12 squares long now. Harvest all of it, using a loop.",
        starter=_F1,
        solution=_F2,
        check="""
const left = [];
for (let x = 0; x < __farm.width; x++) if (__farm.at(x, 0) !== "empty") left.push(x);
expect(left.length === 0, `${left.length} squares of the top row still have crops. Harvest, move right - twelve times: for (let i = 0; i < 12; i++) { ... }`);
expect(__farm.wasted === 0, "Something was cut down before it was ripe.");
""",
        hint="for (let i = 0; i < 12; i++) { harvest(); move('right'); }",
        world=_world("{ w: 12, h: 3, tile: () => 'ripe' }"),
    ),
    Step(
        id="farm-03-nested",
        track="Farm",
        title="A loop inside a loop",
        teaches=(
            "A whole field is rows of squares. The loop you have does one "
            "row; wrap it in a second loop that does it once per row, "
            "moving down between rows. The inner loop runs all the way "
            "round for every single turn of the outer one - 6 rows of 6 is "
            "36 harvests from a handful of lines."
        ),
        goal="Harvest every square of the 6 by 6 field.",
        starter=_F2,
        solution=_F3,
        check="""
const left = __farm.count("ripe") + __farm.count("young");
expect(left === 0, `${left} squares still have crops. One loop for the squares of a row, and around it one for the rows, with move('down') after each row.`);
expect(__farm.harvested === 36, `Harvested ${__farm.harvested} of 36.`);
""",
        hint="for (let row = 0; row < 6; row++) { for (let col = 0; col < 6; col++) { ... } move('down'); }",
        world=_world("{ size: 6, tile: () => 'ripe' }"),
    ),
    Step(
        id="farm-04-plant",
        track="Farm",
        title="Plant, then harvest",
        teaches=(
            "plant() puts a seed in the square under the drone. Crops need "
            "time to ripen, and on the farm time is actions: every move, "
            "plant and harvest is one tick, and these take 30 ticks. "
            "Harvest a crop before it is ripe and it is simply lost. So: "
            "plant the whole field, then go round again to harvest - by "
            "the time the drone gets back to the first square, it has had "
            "time to grow."
        ),
        goal="The field is bare. Plant every square, then harvest every square, losing none.",
        starter=_F3,
        solution=_F4,
        check="""
expect(__farm.planted === 25, `Planted ${__farm.planted} of 25 squares. plant() on every square first.`);
expect(__farm.wasted === 0, `${__farm.wasted} crops were cut down before they were ripe. Plant the whole field first, then go round again to harvest.`);
expect(__farm.harvested === 25, `Harvested ${__farm.harvested} of 25.`);
""",
        hint="Two copies of the nested loops: the first plants, the second harvests.",
        world=_world("{ size: 5, grow: 30 }"),
    ),
    Step(
        id="farm-05-if",
        track="Farm",
        title="Only when it's ready",
        teaches=(
            "This field is a mix: ripe crops, young ones that will not be "
            "ready for ages, and bare soil. canHarvest() answers true only "
            "when the square under the drone has a ripe crop, so an if "
            "decides, square by square: if (canHarvest()) harvest(); The "
            "drone still visits every square - it just does not always do "
            "something there."
        ),
        goal="In one pass over the 6 by 6 field, harvest every ripe crop and leave every young one standing.",
        starter=_F4,
        solution=_F5,
        check="""
expect(__farm.wasted === 0, `${__farm.wasted} young crops were cut down. Ask canHarvest() first, and only harvest when it says true.`);
const ripe = __farm.count("ripe");
expect(ripe === 0, `${ripe} ripe crops are still in the field. Visit every square.`);
""",
        hint="Inside the inner loop: if (canHarvest()) harvest(); then move('right').",
        world=_world(_MIXED),
    ),
    Step(
        id="farm-06-function",
        track="Farm",
        title="A function that goes anywhere",
        teaches=(
            "getX() and getY() say where the drone is. A function wraps "
            "some steps under a name so you can use them again: function "
            "goTo(x, y) { ... } moves the drone to any square, and the "
            "check will call your goTo itself to see. A while loop is the "
            "tool: while (getX() < x) move('right'); keeps moving until "
            "the condition turns false - however far that is."
        ),
        goal="Write goTo(x, y) that moves the drone to square (x, y). Use it to fly to (4, 3) and harvest the crop there.",
        starter=_F5,
        solution=_F6,
        check="""
expect(typeof goTo === "function", "Write a function called goTo: function goTo(x, y) { ... }");
expect(__farm.harvested === 1, "Fly to (4, 3) with goTo and harvest the crop there.");
for (const [x, y] of [[1, 5], [5, 0], [0, 0], [3, 3], [0, 4]]) {
  goTo(x, y);
  expect(__farm.x === x && __farm.y === y, `goTo(${x}, ${y}) left the drone at (${__farm.x}, ${__farm.y}).`);
}
""",
        hint="while (getX() < x) move('right'); and the same for left, down and up.",
        world=_world("{ size: 6, tile: (x, y) => (x === 4 && y === 3 ? 'ripe' : 'empty') }"),
    ),
    Step(
        id="farm-07-wrap",
        track="Farm",
        title="The short way round",
        teaches=(
            "The field wraps, so from x 0 to x 5 on a field 6 wide is one "
            "move left, not five right. The distance going right is (x - "
            "getX() + size) % size - the + size keeps it from going "
            "negative, and % keeps it inside the field. If that is more "
            "than half the field, the other way is shorter: size minus it, "
            "going left. The same for up and down."
        ),
        goal="Make goTo take the short way round every time, over the edge when that is shorter.",
        starter=_F6,
        solution=_F7,
        check="""
expect(typeof goTo === "function", "Keep the function called goTo.");
const size = __farm.width;
const far = (a, b) => Math.min((b - a + size) % size, (a - b + size) % size);
for (const [x, y] of [[5, 0], [0, 5], [3, 3], [1, 1], [5, 5], [0, 0], [4, 1]]) {
  const fromX = __farm.x;
  const fromY = __farm.y;
  const before = __farm.moves;
  goTo(x, y);
  const used = __farm.moves - before;
  const best = far(fromX, x) + far(fromY, y);
  expect(__farm.x === x && __farm.y === y, `goTo(${x}, ${y}) left the drone at (${__farm.x}, ${__farm.y}).`);
  expect(used <= best, `From (${fromX}, ${fromY}) to (${x}, ${y}) took ${used} moves; going over the edge it is ${best}.`);
}
""",
        hint="const right = (x - getX() + size) % size; if (right <= size / 2) go right that many times, else go left size - right times.",
        world=_world("{ size: 6, tile: (x, y) => (x === 4 && y === 3 ? 'ripe' : 'empty') }"),
    ),
    Step(
        id="farm-08-keep-going",
        track="Farm",
        title="Keep the farm going",
        teaches=(
            "A farm is not harvested once. A while loop keeps going as long "
            "as its condition holds, and numHarvested() says how many you "
            "have - so while (numHarvested() < 50) { ... } runs whole rounds "
            "until the job is done, however many that takes. isEmpty() "
            "says whether the square is bare soil. Crops here ripen in 20 "
            "ticks."
        ),
        goal="On the bare 4 by 4 field, keep planting and harvesting until 50 crops are in, losing none.",
        starter=_F7,
        solution=_F8,
        check="""
expect(__farm.harvested >= 50, `Harvested ${__farm.harvested}; the goal is 50. Wrap the rounds in while (numHarvested() < 50) { ... }.`);
expect(__farm.wasted === 0, `${__farm.wasted} crops were cut down unripe - only harvest when canHarvest() says so.`);
""",
        hint="while (numHarvested() < 50) { a planting pass; a harvesting pass }",
        world=_world("{ size: 4, grow: 20 }"),
    ),
    Step(
        id="farm-09-clock",
        track="Farm",
        title="Beat the clock",
        teaches=(
            "Working code is the start. Separate planting and harvesting "
            "passes fly over every square twice a round. Doing both jobs "
            "on one visit - harvest if ripe, then plant if bare - halves the "
            "flying. A small function for the jobs, tend(), keeps the loop "
            "short enough to read. Time is ticks: every move, plant and "
            "harvest is one; the questions (canHarvest, isEmpty, getX) are "
            "free."
        ),
        goal="On the bare 5 by 5 field (crops ripen in 25 ticks), harvest 100 crops in 400 ticks or fewer, losing none.",
        starter=_F8,
        solution=_F9,
        check="""
expect(__farm.harvested >= 100, `Harvested ${__farm.harvested}; the goal is 100.`);
expect(__farm.wasted === 0, `${__farm.wasted} crops were cut down unripe.`);
expect(__farm.ticks <= 400, `That took ${__farm.ticks} ticks; the goal is 400. Visiting each square once a round - harvest if ripe, plant if empty, move on - saves a whole pass.`);
""",
        hint="function tend() { if (canHarvest()) harvest(); if (isEmpty()) plant(); } and one pass per round.",
        world=_world("{ size: 5, grow: 25 }"),
    ),
    Step(
        id="farm-10-yours",
        track="Farm",
        title="Now it's yours",
        teaches=(
            "A bigger field: 8 by 8, crops ripen in 40 ticks, and there is "
            "wait() - one tick of doing nothing. How few ticks can you take "
            "to harvest 200? Ideas: snake along the rows (right on one, "
            "left on the next) so there is no trip back; only fly to squares "
            "that need you, using goTo; keep a list of when each square was "
            "planted and plan the route around it."
        ),
        goal="No check here - farm however you like and watch the Time go down.",
        starter=_F9,
        solution=_F9.replace("< 100", "< 200").replace("< 5", "< 8"),
        check="",
        world=_world("{ size: 8, grow: 40 }"),
    ),
)
