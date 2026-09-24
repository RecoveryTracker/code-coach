"""Six more two-part puzzles, two at each level.

Same rule as the first six: the natural part-one answer is nearly - but
not quite - reusable for part two, and the suite proves it by running
part one's answer against part two's cases.
"""

from __future__ import annotations

from code_coach.puzzles import Part, Puzzle

# ── The lift ─────────────────────────────────────────────────


def _floor(moves):
    floor = 0
    for move in moves:
        floor += int(move[1:]) if move[0] == "U" else -int(move[1:])
    return floor


def _first_basement(moves):
    floor = 0
    for i, move in enumerate(moves, 1):
        floor += int(move[1:]) if move[0] == "U" else -int(move[1:])
        if floor < 0:
            return i
    return 0


LIFT_CASES = ((["U3", "D2"],), ([],), (["D1"],), (["U2", "D3", "U5"],),
              (["U1", "D1", "D2", "U4"],), (["U10", "D4", "D4"],))

LIFT = Puzzle(
    id="pz-the-lift",
    title="The lift",
    level=1,
    story="An old lift keeps a log of every trip: 'U3' is up three floors, "
          "'D2' down two. It starts on the ground floor, floor 0. Floors "
          "below that are the basement.",
    one=Part(
        brief="Which floor is the lift on when the log ends?",
        params=("moves",),
        cases=LIFT_CASES,
        solve=_floor,
        example="['U2', 'D3', 'U5'] → 4",
        py_answer=(
            "def part_one(moves):\n"
            "    floor = 0\n"
            "    for move in moves:\n"
            "        amount = int(move[1:])\n"
            "        floor += amount if move[0] == \"U\" else -amount\n"
            "    return floor\n"
        ),
        js_answer=(
            "function partOne(moves) {\n"
            "  let floor = 0;\n"
            "  for (const move of moves) {\n"
            "    const amount = Number(move.slice(1));\n"
            "    floor += move[0] === \"U\" ? amount : -amount;\n"
            "  }\n"
            "  return floor;\n"
            "}\n"
        ),
        checks=(((["U2", "D3", "U5"],), 4), (([],), 0), ((["D1"],), -1)),
    ),
    two=Part(
        brief="The basement is flooded. Which move first took the lift below "
              "ground? Count moves from 1, and answer 0 if it never went down there.",
        params=("moves",),
        cases=LIFT_CASES,
        solve=_first_basement,
        example="['U1', 'D1', 'D2', 'U4'] → 3",
        py_answer=(
            "def part_two(moves):\n"
            "    floor = 0\n"
            "    for number, move in enumerate(moves, 1):\n"
            "        amount = int(move[1:])\n"
            "        floor += amount if move[0] == \"U\" else -amount\n"
            "        if floor < 0:\n"
            "            return number\n"
            "    return 0\n"
        ),
        js_answer=(
            "function partTwo(moves) {\n"
            "  let floor = 0;\n"
            "  for (let i = 0; i < moves.length; i++) {\n"
            "    const amount = Number(moves[i].slice(1));\n"
            "    floor += moves[i][0] === \"U\" ? amount : -amount;\n"
            "    if (floor < 0) return i + 1;\n"
            "  }\n"
            "  return 0;\n"
            "}\n"
        ),
        checks=(((["U1", "D1", "D2", "U4"],), 3), ((["U3", "D2"],), 0),
                ((["D1"],), 1)),
    ),
    lesson="Part two asks when, not where, so the answer comes from inside "
           "the loop - return the moment it happens, and fall through to 0 "
           "only when the whole log is done.",
)


# ── The class vote ───────────────────────────────────────────


def _top_votes(votes):
    counts: dict[str, int] = {}
    for name in votes:
        counts[name] = counts.get(name, 0) + 1
    return max(counts.values(), default=0)


def _winner(votes):
    most = _top_votes(votes)
    counts: dict[str, int] = {}
    for name in votes:
        counts[name] = counts.get(name, 0) + 1
        if counts[name] == most:
            return name
    return ""


VOTE_CASES = ((["ann", "bo", "ann"],), (["bo"],), (["cy", "ann", "ann", "cy"],),
              (["dee", "eve", "eve", "dee", "dee"],), (["x", "y"],), ([],))

VOTE = Puzzle(
    id="pz-class-vote",
    title="The class vote",
    level=1,
    story="The class is voting for a new name for the hamster. Each vote "
          "is written on a slip, and the slips are read out in the order "
          "they were cast.",
    one=Part(
        brief="How many votes did the most popular name get?",
        params=("votes",),
        cases=VOTE_CASES,
        solve=_top_votes,
        example="['ann', 'bo', 'ann'] → 2",
        py_answer=(
            "def part_one(votes):\n"
            "    counts = {}\n"
            "    for name in votes:\n"
            "        counts[name] = counts.get(name, 0) + 1\n"
            "    return max(counts.values(), default=0)\n"
        ),
        js_answer=(
            "function partOne(votes) {\n"
            "  const counts = new Map();\n"
            "  for (const name of votes) counts.set(name, (counts.get(name) || 0) + 1);\n"
            "  return counts.size ? Math.max(...counts.values()) : 0;\n"
            "}\n"
        ),
        checks=(((["dee", "eve", "eve", "dee", "dee"],), 3), (([],), 0),
                ((["x", "y"],), 1)),
    ),
    two=Part(
        brief="Now name the winner. If names tie, the winner is the one that "
              "reached the top count first as the slips were read. No votes "
              "means no winner: answer an empty string.",
        params=("votes",),
        cases=VOTE_CASES,
        solve=_winner,
        example="['cy', 'ann', 'ann', 'cy'] → 'ann'",
        py_answer=(
            "def part_two(votes):\n"
            "    counts = {}\n"
            "    for name in votes:\n"
            "        counts[name] = counts.get(name, 0) + 1\n"
            "    most = max(counts.values(), default=0)\n"
            "    seen = {}\n"
            "    for name in votes:\n"
            "        seen[name] = seen.get(name, 0) + 1\n"
            "        if seen[name] == most:\n"
            "            return name\n"
            "    return \"\"\n"
        ),
        js_answer=(
            "function partTwo(votes) {\n"
            "  const counts = new Map();\n"
            "  for (const name of votes) counts.set(name, (counts.get(name) || 0) + 1);\n"
            "  const most = counts.size ? Math.max(...counts.values()) : 0;\n"
            "  const seen = new Map();\n"
            "  for (const name of votes) {\n"
            "    seen.set(name, (seen.get(name) || 0) + 1);\n"
            "    if (seen.get(name) === most) return name;\n"
            "  }\n"
            "  return \"\";\n"
            "}\n"
        ),
        checks=(((["cy", "ann", "ann", "cy"],), "ann"), ((["x", "y"],), "x"),
                (([],), "")),
    ),
    lesson="Part one's tally gives you the top count; it cannot say who got "
           "there first, because a dictionary of totals has forgotten the "
           "order. So read the slips a second time, counting again, and stop "
           "at the first name to reach it.",
)


# ── Brackets ─────────────────────────────────────────────────

PAIRS = {")": "(", "]": "[", "}": "{"}


def _balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != PAIRS[ch]:
            return False
    return not stack


def _first_wrong(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != PAIRS[ch]:
            return ch
    return ""


BRACKET_CASES = (("()",), ("([)]",), ("",), ("(()",), ("{[]}()",), ("]",),
                 ("(]",), ("{[(])}",))

BRACKETS = Puzzle(
    id="pz-brackets",
    title="Brackets",
    level=2,
    story="A code editor wants to warn you about brackets. The text is only "
          "brackets: ( ) [ ] { }. Each closer has to close the most recent "
          "opener that is still open, and be the same kind.",
    one=Part(
        brief="Is every bracket closed, in the right order, by the right kind?",
        params=("text",),
        cases=BRACKET_CASES,
        solve=_balanced,
        example="'{[]}()' → True    '([)]' → False",
        py_answer=(
            "def part_one(text):\n"
            "    pairs = {\")\": \"(\", \"]\": \"[\", \"}\": \"{\"}\n"
            "    stack = []\n"
            "    for ch in text:\n"
            "        if ch in \"([{\":\n"
            "            stack.append(ch)\n"
            "        elif not stack or stack.pop() != pairs[ch]:\n"
            "            return False\n"
            "    return not stack\n"
        ),
        js_answer=(
            "function partOne(text) {\n"
            "  const pairs = { \")\": \"(\", \"]\": \"[\", \"}\": \"{\" };\n"
            "  const stack = [];\n"
            "  for (const ch of text) {\n"
            "    if (\"([{\".includes(ch)) stack.push(ch);\n"
            "    else if (stack.length === 0 || stack.pop() !== pairs[ch]) return false;\n"
            "  }\n"
            "  return stack.length === 0;\n"
            "}\n"
        ),
        checks=((("([)]",), False), (("(()",), False), (("",), True),
                (("{[]}()",), True)),
    ),
    two=Part(
        brief="The editor wants to underline the mistake. Return the first "
              "closing bracket that is wrong - nothing open to close, or the "
              "wrong kind. If none is wrong (even if some are left open), "
              "return an empty string.",
        params=("text",),
        cases=BRACKET_CASES,
        solve=_first_wrong,
        example="'{[(])}' → ']'    '(()' → ''",
        py_answer=(
            "def part_two(text):\n"
            "    pairs = {\")\": \"(\", \"]\": \"[\", \"}\": \"{\"}\n"
            "    stack = []\n"
            "    for ch in text:\n"
            "        if ch in \"([{\":\n"
            "            stack.append(ch)\n"
            "        elif not stack or stack.pop() != pairs[ch]:\n"
            "            return ch\n"
            "    return \"\"\n"
        ),
        js_answer=(
            "function partTwo(text) {\n"
            "  const pairs = { \")\": \"(\", \"]\": \"[\", \"}\": \"{\" };\n"
            "  const stack = [];\n"
            "  for (const ch of text) {\n"
            "    if (\"([{\".includes(ch)) stack.push(ch);\n"
            "    else if (stack.length === 0 || stack.pop() !== pairs[ch]) return ch;\n"
            "  }\n"
            "  return \"\";\n"
            "}\n"
        ),
        checks=((("{[(])}",), "]"), (("(()",), ""), (("([)]",), ")")),
    ),
    lesson="A stack remembers what is still open, most recent on top - "
           "exactly the order brackets close in. Part two keeps the same "
           "stack and only changes what is reported: which bracket broke it, "
           "and that being left open is not the same mistake.",
)


# ── The seat map ─────────────────────────────────────────────


def _free(rows):
    return sum(row.count(".") for row in rows)


def _roomy(rows):
    total = 0
    for row in rows:
        for i, seat in enumerate(row):
            left = row[i - 1] if i > 0 else "."
            right = row[i + 1] if i + 1 < len(row) else "."
            if seat == "." and left == "." and right == ".":
                total += 1
    return total


SEAT_CASES = ((["..#", "..."],), ([],), (["#.#"],), ([".", "#"],),
              (["....", "#..#"],), (["#.."],))

SEATS = Puzzle(
    id="pz-seat-map",
    title="The seat map",
    level=2,
    story="A small theatre sends its seat map as rows of text: '.' is a "
          "free seat and '#' is taken.",
    one=Part(
        brief="How many seats are free?",
        params=("rows",),
        cases=SEAT_CASES,
        solve=_free,
        example="['..#', '...'] → 5",
        py_answer=(
            "def part_one(rows):\n"
            "    return sum(row.count(\".\") for row in rows)\n"
        ),
        js_answer=(
            "function partOne(rows) {\n"
            "  let free = 0;\n"
            "  for (const row of rows) {\n"
            "    for (const seat of row) if (seat === \".\") free++;\n"
            "  }\n"
            "  return free;\n"
            "}\n"
        ),
        checks=(((["..#", "..."],), 5), (([],), 0), ((["....", "#..#"],), 6)),
    ),
    two=Part(
        brief="Some people want elbow room. How many free seats have no "
              "taken seat directly to their left or right in the same row? "
              "The end of a row counts as free.",
        params=("rows",),
        cases=SEAT_CASES,
        solve=_roomy,
        example="['..#', '...'] → 4",
        py_answer=(
            "def part_two(rows):\n"
            "    total = 0\n"
            "    for row in rows:\n"
            "        for i, seat in enumerate(row):\n"
            "            left = row[i - 1] if i > 0 else \".\"\n"
            "            right = row[i + 1] if i + 1 < len(row) else \".\"\n"
            "            if seat == \".\" and left == \".\" and right == \".\":\n"
            "                total += 1\n"
            "    return total\n"
        ),
        js_answer=(
            "function partTwo(rows) {\n"
            "  let total = 0;\n"
            "  for (const row of rows) {\n"
            "    for (let i = 0; i < row.length; i++) {\n"
            "      const left = i > 0 ? row[i - 1] : \".\";\n"
            "      const right = i + 1 < row.length ? row[i + 1] : \".\";\n"
            "      if (row[i] === \".\" && left === \".\" && right === \".\") total++;\n"
            "    }\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=(((["..#", "..."],), 4), ((["#.#"],), 0), ((["....", "#..#"],), 4)),
    ),
    lesson="Part one looks at each seat alone; part two needs each seat's "
           "neighbours, so the loop needs the position, not just the seat. "
           "And the edges need a decision - here, off the end counts as free "
           "- or row[i - 1] quietly reads the other end of the row in Python.",
)


# ── Meeting rooms ────────────────────────────────────────────


def _parse(slot):
    start, end = slot.split("-")
    return int(start), int(end)


def _hours(meetings):
    return sum(end - start for start, end in map(_parse, meetings))


def _rooms(meetings):
    slots = [_parse(m) for m in meetings]
    most = 0
    for hour in range(0, 24):
        busy = sum(1 for start, end in slots if start <= hour < end)
        most = max(most, busy)
    return most


ROOM_CASES = ((["9-11"],), ([],), (["9-11", "10-12"],), (["9-11", "11-12"],),
              (["9-12", "10-11", "10-13", "12-14"],), (["13-14", "8-9", "13-15"],))

ROOMS = Puzzle(
    id="pz-meeting-rooms",
    title="Meeting rooms",
    level=3,
    story="The office books meetings by the whole hour on a 24-hour clock: "
          "'9-11' starts at 9 and ends at 11. A meeting that ends at 11 has "
          "left the room by the time one starting at 11 walks in.",
    one=Part(
        brief="How many hours of meetings are booked altogether?",
        params=("meetings",),
        cases=ROOM_CASES,
        solve=_hours,
        example="['9-11', '10-12'] → 4",
        py_answer=(
            "def part_one(meetings):\n"
            "    total = 0\n"
            "    for slot in meetings:\n"
            "        start, end = slot.split(\"-\")\n"
            "        total += int(end) - int(start)\n"
            "    return total\n"
        ),
        js_answer=(
            "function partOne(meetings) {\n"
            "  let total = 0;\n"
            "  for (const slot of meetings) {\n"
            "    const [start, end] = slot.split(\"-\").map(Number);\n"
            "    total += end - start;\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=(((["9-12", "10-11", "10-13", "12-14"],), 9), (([],), 0),
                ((["9-11", "11-12"],), 3)),
    ),
    two=Part(
        brief="How many rooms does the office need, so that every meeting "
              "has one? That is the most meetings going on at the same time.",
        params=("meetings",),
        cases=ROOM_CASES,
        solve=_rooms,
        example="['9-12', '10-11', '10-13', '12-14'] → 3",
        py_answer=(
            "def part_two(meetings):\n"
            "    slots = []\n"
            "    for slot in meetings:\n"
            "        start, end = slot.split(\"-\")\n"
            "        slots.append((int(start), int(end)))\n"
            "    most = 0\n"
            "    for hour in range(24):\n"
            "        busy = sum(1 for start, end in slots if start <= hour < end)\n"
            "        most = max(most, busy)\n"
            "    return most\n"
        ),
        js_answer=(
            "function partTwo(meetings) {\n"
            "  const slots = meetings.map((slot) => slot.split(\"-\").map(Number));\n"
            "  let most = 0;\n"
            "  for (let hour = 0; hour < 24; hour++) {\n"
            "    let busy = 0;\n"
            "    for (const [start, end] of slots) if (start <= hour && hour < end) busy++;\n"
            "    most = Math.max(most, busy);\n"
            "  }\n"
            "  return most;\n"
            "}\n"
        ),
        checks=(((["9-12", "10-11", "10-13", "12-14"],), 3),
                ((["9-11", "11-12"],), 1), (([],), 0)),
    ),
    lesson="Adding up lengths never asks when meetings happen; counting "
           "rooms is only about when. Checking every hour works because "
           "hours are whole - and start <= hour < end is where 'ends at 11' "
           "and 'starts at 11' stop clashing.",
)


# ── The walking robot ────────────────────────────────────────

#: North, east, south, west, as (dx, dy). Turning right steps forward
#: through this list, turning left steps back.
HEADINGS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def _walk(commands):
    x = y = facing = 0
    path = [(0, 0)]
    for c in commands:
        if c == "R":
            facing = (facing + 1) % 4
        elif c == "L":
            facing = (facing + 3) % 4
        else:
            dx, dy = HEADINGS[facing]
            x, y = x + dx, y + dy
            path.append((x, y))
    return path


def _distance(commands):
    x, y = _walk(commands)[-1]
    return abs(x) + abs(y)


def _first_revisit(commands):
    seen = set()
    for x, y in _walk(commands):
        if (x, y) in seen:
            return abs(x) + abs(y)
        seen.add((x, y))
    return -1


ROBOT_CASES = (("FF",), ("",), ("FRFRFRF",), ("FFRFFRFFRFF",), ("FLFLFLFLF",),
               ("RFF",), ("FFRFRFRFF",))

ROBOT = Puzzle(
    id="pz-walking-robot",
    title="The walking robot",
    level=3,
    story="A robot starts at the charging dock, facing north. Its commands "
          "are letters: 'F' moves one square forward, 'L' and 'R' turn it a "
          "quarter turn left or right without moving. Distance is counted in "
          "squares along the grid - across plus up - not as the crow flies.",
    one=Part(
        brief="How far from the dock does the robot finish?",
        params=("commands",),
        cases=ROBOT_CASES,
        solve=_distance,
        example="'RFF' → 2",
        py_answer=(
            "def part_one(commands):\n"
            "    steps = [(0, 1), (1, 0), (0, -1), (-1, 0)]\n"
            "    x = y = facing = 0\n"
            "    for c in commands:\n"
            "        if c == \"R\":\n"
            "            facing = (facing + 1) % 4\n"
            "        elif c == \"L\":\n"
            "            facing = (facing + 3) % 4\n"
            "        else:\n"
            "            dx, dy = steps[facing]\n"
            "            x, y = x + dx, y + dy\n"
            "    return abs(x) + abs(y)\n"
        ),
        js_answer=(
            "function partOne(commands) {\n"
            "  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];\n"
            "  let x = 0, y = 0, facing = 0;\n"
            "  for (const c of commands) {\n"
            "    if (c === \"R\") facing = (facing + 1) % 4;\n"
            "    else if (c === \"L\") facing = (facing + 3) % 4;\n"
            "    else {\n"
            "      x += steps[facing][0];\n"
            "      y += steps[facing][1];\n"
            "    }\n"
            "  }\n"
            "  return Math.abs(x) + Math.abs(y);\n"
            "}\n"
        ),
        checks=((("RFF",), 2), (("FRFRFRF",), 0), (("FLFLFLFLF",), 1)),
    ),
    two=Part(
        brief="The robot is meant to never cross its own path. How far from "
              "the dock is the first square it stands on for a second time? "
              "The dock itself counts as visited. Answer -1 if it never "
              "repeats a square.",
        params=("commands",),
        cases=ROBOT_CASES,
        solve=_first_revisit,
        example="'FFRFRFRFF' → 1",
        py_answer=(
            "def part_two(commands):\n"
            "    steps = [(0, 1), (1, 0), (0, -1), (-1, 0)]\n"
            "    x = y = facing = 0\n"
            "    seen = {(0, 0)}\n"
            "    for c in commands:\n"
            "        if c == \"R\":\n"
            "            facing = (facing + 1) % 4\n"
            "        elif c == \"L\":\n"
            "            facing = (facing + 3) % 4\n"
            "        else:\n"
            "            dx, dy = steps[facing]\n"
            "            x, y = x + dx, y + dy\n"
            "            if (x, y) in seen:\n"
            "                return abs(x) + abs(y)\n"
            "            seen.add((x, y))\n"
            "    return -1\n"
        ),
        js_answer=(
            "function partTwo(commands) {\n"
            "  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];\n"
            "  let x = 0, y = 0, facing = 0;\n"
            "  const seen = new Set([\"0,0\"]);\n"
            "  for (const c of commands) {\n"
            "    if (c === \"R\") facing = (facing + 1) % 4;\n"
            "    else if (c === \"L\") facing = (facing + 3) % 4;\n"
            "    else {\n"
            "      x += steps[facing][0];\n"
            "      y += steps[facing][1];\n"
            "      const key = x + \",\" + y;\n"
            "      if (seen.has(key)) return Math.abs(x) + Math.abs(y);\n"
            "      seen.add(key);\n"
            "    }\n"
            "  }\n"
            "  return -1;\n"
            "}\n"
        ),
        checks=((("FFRFRFRFF",), 1), (("FF",), -1), (("FRFRFRF",), 0)),
    ),
    lesson="Part one only needs where the robot is; part two needs "
           "everywhere it has been, so the walk has to leave a trail - a "
           "set of squares. In JavaScript a Set compares arrays by identity, "
           "which is why the square is stored as the string 'x,y'.",
)


MORE_PUZZLES: tuple[Puzzle, ...] = (LIFT, VOTE, BRACKETS, SEATS, ROOMS, ROBOT)
