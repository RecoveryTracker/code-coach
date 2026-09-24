"""The puzzles, easiest first. Stories and twists are this project's own.

Each part-two twist was chosen so that the natural part-one solution is
nearly - but not quite - reusable: the running total that becomes a
running maximum, the count that becomes a grouping, the rule that gains
a clause. That "nearly" is where the thinking is.
"""

from __future__ import annotations

import re

from code_coach.puzzles import Part, Puzzle


# ── The night shift ──────────────────────────────────────────


def _inside(log):
    inside = 0
    for line in log:
        kind, count = line.split()
        inside += int(count) if kind == "IN" else -int(count)
    return inside


def _peak(log):
    inside = most = 0
    for line in log:
        kind, count = line.split()
        inside += int(count) if kind == "IN" else -int(count)
        most = max(most, inside)
    return most


NIGHT_CASES = ((["IN 3"],), ([],), (["IN 3", "OUT 2"],),
               (["IN 2", "IN 5", "OUT 6", "IN 1"],), (["IN 1", "OUT 1", "IN 1"],))

NIGHT = Puzzle(
    id="pz-night-shift",
    title="The night shift",
    level=1,
    story="The museum's door counter logs every group that passes: "
          "'IN 3' means three people came in, 'OUT 2' that two left. "
          "Nobody was inside when the log began.",
    one=Part(
        brief="How many people are inside when the log ends?",
        params=("log",),
        cases=NIGHT_CASES,
        solve=_inside,
        example="['IN 3', 'OUT 2'] → 1",
        py_answer=(
            "def part_one(log):\n"
            "    inside = 0\n"
            "    for line in log:\n"
            "        kind, count = line.split()\n"
            "        inside += int(count) if kind == \"IN\" else -int(count)\n"
            "    return inside\n"
        ),
        js_answer=(
            "function partOne(log) {\n"
            "  let inside = 0;\n"
            "  for (const line of log) {\n"
            "    const [kind, count] = line.split(\" \");\n"
            "    inside += kind === \"IN\" ? Number(count) : -Number(count);\n"
            "  }\n"
            "  return inside;\n"
            "}\n"
        ),
        checks=(((["IN 3", "OUT 2"],), 1), (([],), 0),
                ((["IN 2", "IN 5", "OUT 6", "IN 1"],), 2)),
    ),
    two=Part(
        brief="The fire marshal wants something else: what was the most "
              "people inside at any one time?",
        params=("log",),
        cases=NIGHT_CASES,
        solve=_peak,
        example="['IN 2', 'IN 5', 'OUT 6', 'IN 1'] → 7",
        py_answer=(
            "def part_two(log):\n"
            "    inside = most = 0\n"
            "    for line in log:\n"
            "        kind, count = line.split()\n"
            "        inside += int(count) if kind == \"IN\" else -int(count)\n"
            "        most = max(most, inside)\n"
            "    return most\n"
        ),
        js_answer=(
            "function partTwo(log) {\n"
            "  let inside = 0;\n"
            "  let most = 0;\n"
            "  for (const line of log) {\n"
            "    const [kind, count] = line.split(\" \");\n"
            "    inside += kind === \"IN\" ? Number(count) : -Number(count);\n"
            "    most = Math.max(most, inside);\n"
            "  }\n"
            "  return most;\n"
            "}\n"
        ),
        checks=(((["IN 2", "IN 5", "OUT 6", "IN 1"],), 7), (([],), 0),
                ((["IN 3", "OUT 2"],), 3)),
    ),
    lesson="The loop was right; what it remembered was not. Part one "
           "only needed where the count ended up, part two needed the "
           "count at every step - one more variable, updated inside.",
)


# ── Sorting station ──────────────────────────────────────────


def _heavy(parcels):
    return sum(1 for p in parcels if int(p[1:]) > 10)


def _busiest_zone(parcels):
    totals: dict[str, int] = {}
    for p in parcels:
        totals[p[0]] = totals.get(p[0], 0) + int(p[1:])
    if not totals:
        return ""
    return max(sorted(totals), key=totals.get)


SORTING_CASES = ((["A5"],), ([],), (["A12", "B3", "A11"],),
                 (["B20", "A10", "A10", "C1"],), (["C11", "C1", "B12"],))

SORTING = Puzzle(
    id="pz-sorting-station",
    title="Sorting station",
    level=1,
    story="Parcels arrive labelled with a zone letter and a weight in "
          "kilos: 'A12' is twelve kilos bound for zone A.",
    one=Part(
        brief="How many parcels weigh more than 10 kilos?",
        params=("parcels",),
        cases=SORTING_CASES,
        solve=_heavy,
        example="['A12', 'B3', 'A11'] → 2",
        py_answer=(
            "def part_one(parcels):\n"
            "    return sum(1 for p in parcels if int(p[1:]) > 10)\n"
        ),
        js_answer=(
            "function partOne(parcels) {\n"
            "  return parcels.filter((p) => Number(p.slice(1)) > 10).length;\n"
            "}\n"
        ),
        checks=(((["A12", "B3", "A11"],), 2), (([],), 0),
                ((["B20", "A10", "A10", "C1"],), 1)),
    ),
    two=Part(
        brief="Which zone gets the most weight in total? If two zones tie, "
              "the one earlier in the alphabet. No parcels means ''.",
        params=("parcels",),
        cases=SORTING_CASES,
        solve=_busiest_zone,
        example="['C11', 'C1', 'B12'] → 'B' (a tie at 12, and B comes first)",
        py_answer=(
            "def part_two(parcels):\n"
            "    totals = {}\n"
            "    for p in parcels:\n"
            "        totals[p[0]] = totals.get(p[0], 0) + int(p[1:])\n"
            "    if not totals:\n"
            "        return \"\"\n"
            "    return max(sorted(totals), key=totals.get)\n"
        ),
        js_answer=(
            "function partTwo(parcels) {\n"
            "  const totals = {};\n"
            "  for (const p of parcels) {\n"
            "    totals[p[0]] = (totals[p[0]] || 0) + Number(p.slice(1));\n"
            "  }\n"
            "  let best = \"\";\n"
            "  for (const zone of Object.keys(totals).sort()) {\n"
            "    if (best === \"\" || totals[zone] > totals[best]) best = zone;\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=(((["C11", "C1", "B12"],), "B"), (([],), ""),
                ((["B20", "A10", "A10", "C1"],), "A")),
    ),
    lesson="Counting became grouping: part two needs a total per zone, "
           "which is a dictionary. And a tie rule is part of the answer - "
           "sorting the zones first is what makes 'the first maximum' mean "
           "'alphabetically first'.",
)


# ── New password rules ───────────────────────────────────────


def _valid_one(passwords):
    return sum(1 for p in passwords if len(p) >= 8 and any(c.isdigit() for c in p))


def _valid_two(passwords):
    return sum(
        1 for p in passwords
        if len(p) >= 8 and any(c.isdigit() for c in p)
        and not re.search(r"(.)\1\1", p)
    )


PASSWORD_CASES = ((["password1"],), ([],), (["abc"],), (["passsword1"],),
                  (["short1", "longenough2", "aaaaaaaa1"],),
                  (["abcdefg1", "12345678"],))

PASSWORDS = Puzzle(
    id="pz-password-rules",
    title="New password rules",
    level=2,
    story="IT is auditing old passwords against the company's rules.",
    one=Part(
        brief="A valid password is at least 8 characters and contains at "
              "least one digit. How many are valid?",
        params=("passwords",),
        cases=PASSWORD_CASES,
        solve=_valid_one,
        example="['short1', 'longenough2', 'aaaaaaaa1'] → 2",
        py_answer=(
            "def part_one(passwords):\n"
            "    return sum(\n"
            "        1 for p in passwords\n"
            "        if len(p) >= 8 and any(c.isdigit() for c in p)\n"
            "    )\n"
        ),
        js_answer=(
            "function partOne(passwords) {\n"
            "  return passwords.filter((p) => p.length >= 8 && /\\d/.test(p)).length;\n"
            "}\n"
        ),
        checks=(((["short1", "longenough2", "aaaaaaaa1"],), 2), (([],), 0),
                ((["passsword1"],), 1)),
    ),
    two=Part(
        brief="A new rule: no character may appear three times in a row. "
              "Keep the old rules too. How many are valid now?",
        params=("passwords",),
        cases=PASSWORD_CASES,
        solve=_valid_two,
        example="['passsword1'] → 0 (sss)",
        py_answer=(
            "import re\n"
            "\n"
            "\n"
            "def part_two(passwords):\n"
            "    return sum(\n"
            "        1 for p in passwords\n"
            "        if len(p) >= 8 and any(c.isdigit() for c in p)\n"
            "        and not re.search(r\"(.)\\1\\1\", p)\n"
            "    )\n"
        ),
        js_answer=(
            "function partTwo(passwords) {\n"
            "  return passwords.filter(\n"
            "    (p) => p.length >= 8 && /\\d/.test(p) && !/(.)\\1\\1/.test(p),\n"
            "  ).length;\n"
            "}\n"
        ),
        checks=(((["passsword1"],), 0), (([],), 0),
                ((["short1", "longenough2", "aaaaaaaa1"],), 1)),
    ),
    lesson="A rule that gains a clause is the commonest change there is. "
           "If part one's check lived in one place, part two was one more "
           "'and' - which is the argument for keeping rules in one place.",
)


# ── The garden grid ──────────────────────────────────────────


def _trees(grid):
    return sum(row.count("#") for row in grid)


def _neighboured(grid):
    count = 0
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell != "#":
                continue
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < len(grid) and 0 <= cc < len(grid[rr]) \
                        and grid[rr][cc] == "#":
                    count += 1
                    break
    return count


GARDEN_CASES = ((["#."],), ([],), (["."],), (["#"],), (["##"],), (["#.", ".#"],),
                (["#.#", "###", "..."],))

GARDEN = Puzzle(
    id="pz-garden-grid",
    title="The garden grid",
    level=2,
    story="A garden plan is drawn as rows of text: '#' is a tree and '.' "
          "is grass.",
    one=Part(
        brief="How many trees are in the garden?",
        params=("grid",),
        cases=GARDEN_CASES,
        solve=_trees,
        example="['#.#', '###', '...'] → 5",
        py_answer=(
            "def part_one(grid):\n"
            "    return sum(row.count(\"#\") for row in grid)\n"
        ),
        js_answer=(
            "function partOne(grid) {\n"
            "  let count = 0;\n"
            "  for (const row of grid) {\n"
            "    for (const cell of row) if (cell === \"#\") count++;\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=(((["#.#", "###", "..."],), 5), (([],), 0), ((["."],), 0)),
    ),
    two=Part(
        brief="Trees shade each other. Count only the trees with another "
              "tree directly above, below, left or right - not diagonally.",
        params=("grid",),
        cases=GARDEN_CASES,
        solve=_neighboured,
        example="['#.', '.#'] → 0 (diagonal does not count)",
        py_answer=(
            "def part_two(grid):\n"
            "    count = 0\n"
            "    for r, row in enumerate(grid):\n"
            "        for c, cell in enumerate(row):\n"
            "            if cell != \"#\":\n"
            "                continue\n"
            "            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):\n"
            "                rr, cc = r + dr, c + dc\n"
            "                if 0 <= rr < len(grid) and 0 <= cc < len(grid[rr]) \\\n"
            "                        and grid[rr][cc] == \"#\":\n"
            "                    count += 1\n"
            "                    break\n"
            "    return count\n"
        ),
        js_answer=(
            "function partTwo(grid) {\n"
            "  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];\n"
            "  let count = 0;\n"
            "  for (let r = 0; r < grid.length; r++) {\n"
            "    for (let c = 0; c < grid[r].length; c++) {\n"
            "      if (grid[r][c] !== \"#\") continue;\n"
            "      const shaded = steps.some(([dr, dc]) => {\n"
            "        const rr = r + dr;\n"
            "        const cc = c + dc;\n"
            "        return rr >= 0 && rr < grid.length && cc >= 0\n"
            "          && cc < grid[rr].length && grid[rr][cc] === \"#\";\n"
            "      });\n"
            "      if (shaded) count++;\n"
            "    }\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        checks=(((["#.", ".#"],), 0), (([],), 0), ((["##"],), 2)),
    ),
    lesson="Part one never needed to know where a tree was; part two needs "
           "its row and column, and a check that a neighbour is inside the "
           "grid before looking at it. The edge of the grid is where these "
           "go wrong.",
)


# ── Last bus ─────────────────────────────────────────────────


def _minutes(clock):
    h, m = clock.split(":")
    return int(h) * 60 + int(m)


def _wait_today(departures, now):
    later = [_minutes(d) - _minutes(now) for d in departures
             if _minutes(d) >= _minutes(now)]
    return min(later) if later else -1


def _wait_any_day(departures, now):
    if not departures:
        return -1
    return min((_minutes(d) - _minutes(now)) % 1440 for d in departures)


BUS_CASES = ((["08:00", "09:30"], "08:15"), (["08:00"], "08:00"),
             (["06:00", "23:50"], "23:55"), ([], "12:00"), (["00:10"], "23:59"))

BUS = Puzzle(
    id="pz-last-bus",
    title="Last bus",
    level=3,
    story="A stop's departures are listed as 'HH:MM' on a 24-hour clock, "
          "and so is the time now. A bus leaving right now still counts.",
    one=Part(
        brief="How many minutes until the next bus today? If there is no "
              "bus left today, -1.",
        params=("departures", "now"),
        cases=BUS_CASES,
        solve=_wait_today,
        example="(['08:00', '09:30'], '08:15') → 75",
        py_answer=(
            "def minutes(clock):\n"
            "    h, m = clock.split(\":\")\n"
            "    return int(h) * 60 + int(m)\n"
            "\n"
            "\n"
            "def part_one(departures, now):\n"
            "    later = [minutes(d) - minutes(now) for d in departures\n"
            "             if minutes(d) >= minutes(now)]\n"
            "    return min(later) if later else -1\n"
        ),
        js_answer=(
            "function minutes(clock) {\n"
            "  const [h, m] = clock.split(\":\");\n"
            "  return Number(h) * 60 + Number(m);\n"
            "}\n"
            "\n"
            "function partOne(departures, now) {\n"
            "  const later = departures\n"
            "    .map((d) => minutes(d) - minutes(now))\n"
            "    .filter((wait) => wait >= 0);\n"
            "  return later.length ? Math.min(...later) : -1;\n"
            "}\n"
        ),
        checks=(((["08:00", "09:30"], "08:15"), 75), (([], "12:00"), -1),
                ((["08:00"], "08:00"), 0)),
    ),
    two=Part(
        brief="The same timetable runs every day. How many minutes until the "
              "next bus, even if it is tomorrow? No departures at all is -1.",
        params=("departures", "now"),
        cases=BUS_CASES,
        solve=_wait_any_day,
        example="(['00:10'], '23:59') → 11",
        py_answer=(
            "def minutes(clock):\n"
            "    h, m = clock.split(\":\")\n"
            "    return int(h) * 60 + int(m)\n"
            "\n"
            "\n"
            "def part_two(departures, now):\n"
            "    if not departures:\n"
            "        return -1\n"
            "    return min((minutes(d) - minutes(now)) % 1440 for d in departures)\n"
        ),
        js_answer=(
            "function minutes(clock) {\n"
            "  const [h, m] = clock.split(\":\");\n"
            "  return Number(h) * 60 + Number(m);\n"
            "}\n"
            "\n"
            "function partTwo(departures, now) {\n"
            "  if (!departures.length) return -1;\n"
            "  const day = 24 * 60;\n"
            "  return Math.min(\n"
            "    ...departures.map((d) => (((minutes(d) - minutes(now)) % day) + day) % day),\n"
            "  );\n"
            "}\n"
        ),
        checks=(((["00:10"], "23:59"), 11), (([], "12:00"), -1),
                ((["06:00", "23:50"], "23:55"), 365)),
    ),
    lesson="Wrapping round is what % is for: (later - now) % 1440 is the "
           "wait on a clock that goes round. In JavaScript % keeps the sign "
           "of a negative number, so it needs the extra + 1440 that Python "
           "does not.",
)


# ── Word chain ───────────────────────────────────────────────


def _is_chain(words):
    return all(a[-1] == b[0] for a, b in zip(words, words[1:]))


def _longest_chain(words):
    if not words:
        return 0
    best = run = 1
    for a, b in zip(words, words[1:]):
        run = run + 1 if a[-1] == b[0] else 1
        best = max(best, run)
    return best


CHAIN_CASES = ((["apple", "egg", "goat"],), ([],), (["apple"],),
               (["apple", "egg", "tree"],),
               (["cat", "tar", "rat", "tiger", "rope"],), (["a", "b"],))

CHAIN = Puzzle(
    id="pz-word-chain",
    title="Word chain",
    level=3,
    story="In the word-chain game each word has to start with the last "
          "letter of the word before it: apple, egg, goat.",
    one=Part(
        brief="Is the whole list one valid chain? An empty list or a single "
              "word counts as valid.",
        params=("words",),
        cases=CHAIN_CASES,
        solve=_is_chain,
        example="['apple', 'egg', 'tree'] → False",
        py_answer=(
            "def part_one(words):\n"
            "    return all(a[-1] == b[0] for a, b in zip(words, words[1:]))\n"
        ),
        js_answer=(
            "function partOne(words) {\n"
            "  for (let i = 1; i < words.length; i++) {\n"
            "    const before = words[i - 1];\n"
            "    if (before[before.length - 1] !== words[i][0]) return false;\n"
            "  }\n"
            "  return true;\n"
            "}\n"
        ),
        checks=(((["apple", "egg", "tree"],), False), (([],), True),
                ((["apple"],), True)),
    ),
    two=Part(
        brief="Most lists break somewhere. How long is the longest unbroken "
              "run of chained words? No words is 0.",
        params=("words",),
        cases=CHAIN_CASES,
        solve=_longest_chain,
        example="['apple', 'egg', 'tree'] → 2",
        py_answer=(
            "def part_two(words):\n"
            "    if not words:\n"
            "        return 0\n"
            "    best = run = 1\n"
            "    for a, b in zip(words, words[1:]):\n"
            "        run = run + 1 if a[-1] == b[0] else 1\n"
            "        best = max(best, run)\n"
            "    return best\n"
        ),
        js_answer=(
            "function partTwo(words) {\n"
            "  if (!words.length) return 0;\n"
            "  let best = 1;\n"
            "  let run = 1;\n"
            "  for (let i = 1; i < words.length; i++) {\n"
            "    const before = words[i - 1];\n"
            "    run = before[before.length - 1] === words[i][0] ? run + 1 : 1;\n"
            "    best = Math.max(best, run);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=(((["apple", "egg", "tree"],), 2), (([],), 0),
                ((["a", "b"],), 1)),
    ),
    lesson="Part one could stop at the first break; part two has to carry "
           "on past it and start counting again. A yes-or-no question and a "
           "how-many question can share every comparison and still need "
           "different loops.",
)


def _all() -> tuple[Puzzle, ...]:
    # The later ones live in content2; merged by level so the list
    # still reads easiest first. sorted() is stable, so within a level
    # the first six keep their place ahead of the newer ones.
    from code_coach.puzzles.content2 import MORE_PUZZLES
    from code_coach.puzzles.content3 import MORE_PUZZLES_2

    first = (NIGHT, SORTING, PASSWORDS, GARDEN, BUS, CHAIN)
    return tuple(sorted(first + MORE_PUZZLES + MORE_PUZZLES_2, key=lambda p: p.level))


PUZZLES: tuple[Puzzle, ...] = _all()
