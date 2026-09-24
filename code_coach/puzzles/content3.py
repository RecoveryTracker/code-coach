"""Three more two-part puzzles, in Python, JavaScript and Dart.

The Dart answers live in puzzles/dart2.py, next to the types they need.
Same rule as the rest: part one's answer is nearly - not quite - what
part two needs, and the suite runs it against part two to prove it.
"""

from __future__ import annotations

from code_coach.puzzles import Part, Puzzle

# ── Traffic light ────────────────────────────────────────────


def _green_seconds(log):
    return sum(1 for colour in log if colour == "green")


def _longest_run(log):
    best = run = 0
    for i, colour in enumerate(log):
        run = run + 1 if i and log[i - 1] == colour else 1
        best = max(best, run)
    return best


LIGHT_CASES = ((["red"],), ([],), (["green", "green", "red"],),
               (["red", "red", "green", "amber", "red"],),
               (["amber", "green", "green", "green", "red", "red"],))

LIGHT = Puzzle(
    id="pz-traffic-light",
    title="Traffic light",
    level=2,
    story="A camera logs the colour of a traffic light once a second: "
          "'red', 'amber' or 'green'.",
    one=Part(
        brief="How many seconds was the light green?",
        params=("log",),
        cases=LIGHT_CASES,
        solve=_green_seconds,
        example="['red', 'red', 'green', 'amber', 'red'] → 1",
        py_answer=(
            "def part_one(log):\n"
            "    return sum(1 for colour in log if colour == \"green\")\n"
        ),
        js_answer=(
            "function partOne(log) {\n"
            "  return log.filter((colour) => colour === \"green\").length;\n"
            "}\n"
        ),
        checks=(((["green", "green", "red"],), 2), (([],), 0),
                ((["amber", "green", "green", "green", "red", "red"],), 3)),
    ),
    two=Part(
        brief="The council suspects the light gets stuck. What is the longest "
              "run of seconds it stayed on one colour, whichever colour?",
        params=("log",),
        cases=LIGHT_CASES,
        solve=_longest_run,
        example="['amber', 'green', 'green', 'green', 'red', 'red'] → 3",
        py_answer=(
            "def part_two(log):\n"
            "    best = run = 0\n"
            "    for i, colour in enumerate(log):\n"
            "        run = run + 1 if i and log[i - 1] == colour else 1\n"
            "        best = max(best, run)\n"
            "    return best\n"
        ),
        js_answer=(
            "function partTwo(log) {\n"
            "  let best = 0;\n"
            "  let run = 0;\n"
            "  for (let i = 0; i < log.length; i++) {\n"
            "    run = i > 0 && log[i - 1] === log[i] ? run + 1 : 1;\n"
            "    best = Math.max(best, run);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=(((["red"],), 1), (([],), 0),
                ((["red", "red", "green", "amber", "red"],), 2)),
    ),
    lesson="Part one looks at each second alone; part two has to compare "
           "each second with the one before, and remember a running streak "
           "that resets whenever the colour changes.",
)


# ── The shopping list ────────────────────────────────────────


def _parse(line):
    name, count = line.split(" x")
    return name, int(count)


def _item_total(lines):
    return sum(_parse(line)[1] for line in lines)


def _merged(lines):
    totals: dict[str, int] = {}
    for line in lines:
        name, count = _parse(line)
        totals[name] = totals.get(name, 0) + count
    return [f"{name} x{totals[name]}" for name in sorted(totals)]


SHOP_CASES = ((["apple x2"],), ([],), (["pear x1", "apple x3"],),
              (["egg x6", "milk x1", "egg x6"],), (["tea x1", "tea x1", "tea x1"],))

SHOP = Puzzle(
    id="pz-shopping-list",
    title="The shopping list",
    level=3,
    story="Everyone in the house adds to one shopping list. Each line is an "
          "item and how many: 'egg x6' is six eggs. The same item can be "
          "added more than once.",
    one=Part(
        brief="How many things are on the list altogether?",
        params=("lines",),
        cases=SHOP_CASES,
        solve=_item_total,
        example="['egg x6', 'milk x1', 'egg x6'] → 13",
        py_answer=(
            "def part_one(lines):\n"
            "    total = 0\n"
            "    for line in lines:\n"
            "        name, count = line.split(\" x\")\n"
            "        total += int(count)\n"
            "    return total\n"
        ),
        js_answer=(
            "function partOne(lines) {\n"
            "  let total = 0;\n"
            "  for (const line of lines) {\n"
            "    const [, count] = line.split(\" x\");\n"
            "    total += Number(count);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=(((["egg x6", "milk x1", "egg x6"],), 13), (([],), 0),
                ((["pear x1", "apple x3"],), 4)),
    ),
    two=Part(
        brief="Tidy the list for the shop: one line per item with the "
              "amounts added up, written the same way, in alphabetical order.",
        params=("lines",),
        cases=SHOP_CASES,
        solve=_merged,
        example="['egg x6', 'milk x1', 'egg x6'] → ['egg x12', 'milk x1']",
        py_answer=(
            "def part_two(lines):\n"
            "    totals = {}\n"
            "    for line in lines:\n"
            "        name, count = line.split(\" x\")\n"
            "        totals[name] = totals.get(name, 0) + int(count)\n"
            "    return [f\"{name} x{totals[name]}\" for name in sorted(totals)]\n"
        ),
        js_answer=(
            "function partTwo(lines) {\n"
            "  const totals = new Map();\n"
            "  for (const line of lines) {\n"
            "    const [name, count] = line.split(\" x\");\n"
            "    totals.set(name, (totals.get(name) || 0) + Number(count));\n"
            "  }\n"
            "  return [...totals.keys()].sort().map((name) => `${name} x${totals.get(name)}`);\n"
            "}\n"
        ),
        checks=(((["egg x6", "milk x1", "egg x6"],), ["egg x12", "milk x1"]),
                (([],), []), ((["pear x1", "apple x3"],), ["apple x3", "pear x1"])),
    ),
    lesson="A total only needs one number; merging needs one number per "
           "name, which is a map. Part one's split is reusable - what it "
           "fed into was not.",
)


# ── Warming up ───────────────────────────────────────────────


def _biggest_rise(readings):
    rises = [b - a for a, b in zip(readings, readings[1:])]
    return max([0] + rises)


def _longest_climb(readings):
    best = run = 0
    for i, value in enumerate(readings):
        run = run + 1 if i and readings[i - 1] < value else 1
        best = max(best, run)
    return best


WARM_CASES = (([5],), ([],), ([1, 3, 2, 6],), ([3, 2, 1],), ([1, 2, 3, 1, 2],),
              ([-2, -1, 4],))

WARM = Puzzle(
    id="pz-warming-up",
    title="Warming up",
    level=4,
    story="A greenhouse sensor records the temperature every hour, in whole "
          "degrees. Readings can go below zero.",
    one=Part(
        brief="What is the biggest rise from one reading to the next? If it "
              "never rises, 0.",
        params=("readings",),
        cases=WARM_CASES,
        solve=_biggest_rise,
        example="[1, 3, 2, 6] → 4",
        py_answer=(
            "def part_one(readings):\n"
            "    best = 0\n"
            "    for i in range(1, len(readings)):\n"
            "        best = max(best, readings[i] - readings[i - 1])\n"
            "    return best\n"
        ),
        js_answer=(
            "function partOne(readings) {\n"
            "  let best = 0;\n"
            "  for (let i = 1; i < readings.length; i++) {\n"
            "    best = Math.max(best, readings[i] - readings[i - 1]);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=((([1, 3, 2, 6],), 4), (([3, 2, 1],), 0), (([-2, -1, 4],), 5)),
    ),
    two=Part(
        brief="How many readings long is the longest stretch where every "
              "reading is warmer than the one before it? One reading on its "
              "own is a stretch of 1; no readings is 0.",
        params=("readings",),
        cases=WARM_CASES,
        solve=_longest_climb,
        example="[1, 2, 3, 1, 2] → 3",
        py_answer=(
            "def part_two(readings):\n"
            "    best = run = 0\n"
            "    for i, value in enumerate(readings):\n"
            "        run = run + 1 if i and readings[i - 1] < value else 1\n"
            "        best = max(best, run)\n"
            "    return best\n"
        ),
        js_answer=(
            "function partTwo(readings) {\n"
            "  let best = 0;\n"
            "  let run = 0;\n"
            "  for (let i = 0; i < readings.length; i++) {\n"
            "    run = i > 0 && readings[i - 1] < readings[i] ? run + 1 : 1;\n"
            "    best = Math.max(best, run);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=((([5],), 1), (([1, 2, 3, 1, 2],), 3), (([1, 3, 2, 6],), 2)),
    ),
    lesson="Both parts compare neighbours, but part one keeps the biggest "
           "difference and part two keeps a streak. Counting readings rather "
           "than rises is the off-by-one to watch: three rising readings is "
           "two rises.",
)


MORE_PUZZLES_2: tuple[Puzzle, ...] = (LIGHT, SHOP, WARM)
