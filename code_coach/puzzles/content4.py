"""Six more two-part puzzles, in Python, JavaScript and Dart.

The Dart answers live in puzzles/dart3.py. Same rule as the rest: part one's
answer is nearly - not quite - what part two needs, and the suite runs it
against part two to prove it. Between them part two asks for a comparison
with the day before, a running peak, the biggest step between neighbours,
the item behind a total, only the digits that rise, and what is
left after a whole log has been replayed.
"""

from __future__ import annotations

from code_coach.puzzles import Part, Puzzle

# ── Step counter ─────────────────────────────────────────────


def _total_steps(days):
    return sum(days)


def _better_days(days):
    return sum(1 for i in range(1, len(days)) if days[i] > days[i - 1])


STEP_CASES = (([],), ([5000],), ([3000, 4000, 3500, 6000],), ([100, 100, 100],),
              ([9000, 8000, 7000, 10000, 12000],))

STEPS = Puzzle(
    id="pz-step-counter",
    title="Step counter",
    level=1,
    story="A step counter keeps one number a day: how many steps you walked.",
    one=Part(
        brief="How many steps were walked altogether?",
        params=("days",),
        cases=STEP_CASES,
        solve=_total_steps,
        example="[3000, 4000, 3500, 6000] → 16500",
        py_answer="def part_one(days):\n    return sum(days)\n",
        js_answer="function partOne(days) {\n  return days.reduce((a, b) => a + b, 0);\n}\n",
        checks=((([3000, 4000, 3500, 6000],), 16500), (([],), 0)),
    ),
    two=Part(
        brief="The app gives a star for every day you beat the day before. "
              "How many stars? (The first day has nothing to beat.)",
        params=("days",),
        cases=STEP_CASES,
        solve=_better_days,
        example="[3000, 4000, 3500, 6000] → 2",
        py_answer=(
            "def part_two(days):\n"
            "    return sum(1 for i in range(1, len(days)) if days[i] > days[i - 1])\n"
        ),
        js_answer=(
            "function partTwo(days) {\n"
            "  let stars = 0;\n"
            "  for (let i = 1; i < days.length; i++) {\n"
            "    if (days[i] > days[i - 1]) stars++;\n"
            "  }\n"
            "  return stars;\n"
            "}\n"
        ),
        checks=((([3000, 4000, 3500, 6000],), 2), (([100, 100, 100],), 0),
                (([9000, 8000, 7000, 10000, 12000],), 2)),
    ),
    lesson="Part one looks at each day alone. Part two compares each day with "
           "its neighbour, so the loop starts at the SECOND day and looks back "
           "- start at the first and days[i - 1] is days[-1], the last day.",
)


# ── Car park ─────────────────────────────────────────────────


def _cars_in(log):
    return sum(1 for e in log if e == "in")


def _busiest(log):
    now = best = 0
    for e in log:
        now += 1 if e == "in" else -1
        best = max(best, now)
    return best


PARK_CASES = (([],), (["in"],), (["in", "in", "out", "in"],), (["in", "out", "in", "out"],),
              (["in", "in", "in", "out", "out", "in", "in"],))

PARK = Puzzle(
    id="pz-car-park",
    title="Car park",
    level=2,
    story="The barrier of a car park logs every car: 'in' when one drives in, "
          "'out' when one leaves. It opens empty.",
    one=Part(
        brief="How many cars came in during the day?",
        params=("log",),
        cases=PARK_CASES,
        solve=_cars_in,
        example="['in', 'in', 'out', 'in'] → 3",
        py_answer="def part_one(log):\n    return log.count(\"in\")\n",
        js_answer="function partOne(log) {\n  return log.filter((e) => e === \"in\").length;\n}\n",
        checks=(((["in", "in", "out", "in"],), 3), (([],), 0)),
    ),
    two=Part(
        brief="The owner wants to know if the car park is big enough. What is "
              "the most cars that were ever inside at the same time?",
        params=("log",),
        cases=PARK_CASES,
        solve=_busiest,
        example="['in', 'in', 'in', 'out', 'out', 'in', 'in'] → 3",
        py_answer=(
            "def part_two(log):\n"
            "    now = best = 0\n"
            "    for e in log:\n"
            "        now += 1 if e == \"in\" else -1\n"
            "        best = max(best, now)\n"
            "    return best\n"
        ),
        js_answer=(
            "function partTwo(log) {\n"
            "  let now = 0;\n"
            "  let best = 0;\n"
            "  for (const e of log) {\n"
            "    now += e === \"in\" ? 1 : -1;\n"
            "    best = Math.max(best, now);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=(((["in", "in", "in", "out", "out", "in", "in"],), 3),
                ((["in", "out", "in", "out"],), 1), (([],), 0)),
    ),
    lesson="A running total answers 'how many now'; keeping the biggest value it "
           "ever reached answers 'how many at most'. Part one's count of ins is "
           "the peak only if nobody ever leaves.",
)


# ── Temperatures ─────────────────────────────────────────────


def _hottest(readings):
    return max(readings)


def _biggest_rise(readings):
    rises = [b - a for a, b in zip(readings, readings[1:])]
    return max([0] + rises)


TEMP_CASES = (([12],), ([12, 15, 11, 20],), ([30, 25, 20],), ([-5, 0, -2, 4],), ([7, 7, 7],))

TEMPS = Puzzle(
    id="pz-temperatures",
    title="Temperatures",
    level=2,
    story="A weather station writes down the temperature every hour, in whole "
          "degrees. There is always at least one reading.",
    one=Part(
        brief="What was the hottest reading?",
        params=("readings",),
        cases=TEMP_CASES,
        solve=_hottest,
        example="[12, 15, 11, 20] → 20",
        py_answer="def part_one(readings):\n    return max(readings)\n",
        js_answer="function partOne(readings) {\n  return Math.max(...readings);\n}\n",
        checks=((([12, 15, 11, 20],), 20), (([-5, 0, -2, 4],), 4)),
    ),
    two=Part(
        brief="What was the biggest rise from one hour to the next? If it never "
              "got warmer, the answer is 0.",
        params=("readings",),
        cases=TEMP_CASES,
        solve=_biggest_rise,
        example="[12, 15, 11, 20] → 9",
        py_answer=(
            "def part_two(readings):\n"
            "    best = 0\n"
            "    for a, b in zip(readings, readings[1:]):\n"
            "        best = max(best, b - a)\n"
            "    return best\n"
        ),
        js_answer=(
            "function partTwo(readings) {\n"
            "  let best = 0;\n"
            "  for (let i = 1; i < readings.length; i++) {\n"
            "    best = Math.max(best, readings[i] - readings[i - 1]);\n"
            "  }\n"
            "  return best;\n"
            "}\n"
        ),
        checks=((([12, 15, 11, 20],), 9), (([30, 25, 20],), 0), (([-5, 0, -2, 4],), 6)),
    ),
    lesson="The hottest minus the coldest is not the biggest rise: the coldest "
           "reading may come AFTER the hottest. A rise is between neighbours, so "
           "zip(readings, readings[1:]) - each reading with the next - is the shape.",
)


# ── Receipts ─────────────────────────────────────────────────


def _receipt_total(lines):
    return sum(int(line.split(":")[1]) for line in lines)


def _priciest(lines):
    best_name, best = "", -1
    for line in lines:
        name, price = line.split(":")
        if int(price) > best:
            best_name, best = name, int(price)
    return best_name


RECEIPT_CASES = ((["tea:3"],), (["tea:3", "cake:5", "jam:2"],), (["a:1", "b:1"],),
                 (["bread:4", "milk:2", "cheese:9", "eggs:9"],), ([],))

RECEIPTS = Puzzle(
    id="pz-receipts",
    title="Receipts",
    level=3,
    story="A till prints one line per item, the name and the price in whole "
          "pounds joined by a colon: 'tea:3'.",
    one=Part(
        brief="What does the receipt come to?",
        params=("lines",),
        cases=RECEIPT_CASES,
        solve=_receipt_total,
        example="['tea:3', 'cake:5', 'jam:2'] → 10",
        py_answer=(
            "def part_one(lines):\n"
            "    return sum(int(line.split(\":\")[1]) for line in lines)\n"
        ),
        js_answer=(
            "function partOne(lines) {\n"
            "  return lines.reduce((sum, line) => sum + Number(line.split(\":\")[1]), 0);\n"
            "}\n"
        ),
        checks=(((["tea:3", "cake:5", "jam:2"],), 10), (([],), 0)),
    ),
    two=Part(
        brief="Which item cost the most? Give its name - the first one if two "
              "cost the same - or an empty string for an empty receipt.",
        params=("lines",),
        cases=RECEIPT_CASES,
        solve=_priciest,
        example="['bread:4', 'milk:2', 'cheese:9', 'eggs:9'] → 'cheese'",
        py_answer=(
            "def part_two(lines):\n"
            "    best_name, best = \"\", -1\n"
            "    for line in lines:\n"
            "        name, price = line.split(\":\")\n"
            "        if int(price) > best:\n"
            "            best_name, best = name, int(price)\n"
            "    return best_name\n"
        ),
        js_answer=(
            "function partTwo(lines) {\n"
            "  let bestName = \"\";\n"
            "  let best = -1;\n"
            "  for (const line of lines) {\n"
            "    const [name, price] = line.split(\":\");\n"
            "    if (Number(price) > best) {\n"
            "      bestName = name;\n"
            "      best = Number(price);\n"
            "    }\n"
            "  }\n"
            "  return bestName;\n"
            "}\n"
        ),
        checks=(((["bread:4", "milk:2", "cheese:9", "eggs:9"],), "cheese"), (([],), ""),
                ((["a:1", "b:1"],), "a")),
    ),
    lesson="A total can forget each item as soon as it is added. 'Which one' "
           "cannot: it has to carry the best name along with the best price, and "
           "a strict > is what keeps the FIRST of two equal prices.",
)


# ── Digit string ─────────────────────────────────────────


def _digit_sum(text):
    return sum(int(ch) for ch in text)


def _rising_sum(text):
    return sum(int(b) for a, b in zip(text, text[1:]) if b > a)


DIGIT_CASES = (("",), ("7",), ("31415",), ("1111",), ("123",), ("9081726354",))

DIGITS = Puzzle(
    id="pz-digit-string",
    title="Digit string",
    level=3,
    story="A machine prints a long string of digits, with no spaces, such as "
          "'31415'.",
    one=Part(
        brief="What do all the digits add up to?",
        params=("text",),
        cases=DIGIT_CASES,
        solve=_digit_sum,
        example="'31415' → 14",
        py_answer="def part_one(text):\n    return sum(int(ch) for ch in text)\n",
        js_answer=(
            "function partOne(text) {\n"
            "  return [...text].reduce((sum, ch) => sum + Number(ch), 0);\n"
            "}\n"
        ),
        checks=((("31415",), 14), (("",), 0), (("9081726354",), 45)),
    ),
    two=Part(
        brief="Now add up only the digits that are bigger than the digit just "
              "before them. The first digit has nothing before it, so it never "
              "counts.",
        params=("text",),
        cases=DIGIT_CASES,
        solve=_rising_sum,
        example="'31415' → 9 (the 4 and the 5)",
        py_answer=(
            "def part_two(text):\n"
            "    total = 0\n"
            "    for i in range(1, len(text)):\n"
            "        if text[i] > text[i - 1]:\n"
            "            total += int(text[i])\n"
            "    return total\n"
        ),
        js_answer=(
            "function partTwo(text) {\n"
            "  let total = 0;\n"
            "  for (let i = 1; i < text.length; i++) {\n"
            "    if (text[i] > text[i - 1]) total += Number(text[i]);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=((("31415",), 9), (("1111",), 0), (("123",), 5), (("9081726354",), 8 + 7 + 6 + 5)),
    ),
    lesson="Part one never needs to know where a digit is. Part two compares each "
           "digit with its neighbour, so the loop starts at the second one and looks "
           "back. Comparing the characters works because '0' to '9' are in order.",
)


# ── Stock room ───────────────────────────────────────────────


def _items_left(log):
    total = 0
    for line in log:
        verb, _, count = line.split(" ")
        total += int(count) if verb == "add" else -int(count)
    return total


def _in_stock(log):
    stock = {}
    for line in log:
        verb, name, count = line.split(" ")
        stock[name] = stock.get(name, 0) + (int(count) if verb == "add" else -int(count))
    return sorted(name for name, n in stock.items() if n > 0)


STOCK_CASES = (([],), (["add tea 3"],), (["add tea 3", "take tea 1", "add jam 2"],),
               (["add pen 5", "take pen 5", "add ink 1"],),
               (["add a 2", "add b 2", "take a 1", "take b 2", "add c 4"],))

STOCK = Puzzle(
    id="pz-stock-room",
    title="Stock room",
    level=4,
    story="A stock room keeps a log of everything that goes in and out, one "
          "line each: 'add tea 3' or 'take tea 1'. It starts empty.",
    one=Part(
        brief="How many items are left in the room at the end, of all kinds "
              "together?",
        params=("log",),
        cases=STOCK_CASES,
        solve=_items_left,
        example="['add tea 3', 'take tea 1', 'add jam 2'] → 4",
        py_answer=(
            "def part_one(log):\n"
            "    total = 0\n"
            "    for line in log:\n"
            "        verb, _, count = line.split(\" \")\n"
            "        total += int(count) if verb == \"add\" else -int(count)\n"
            "    return total\n"
        ),
        js_answer=(
            "function partOne(log) {\n"
            "  let total = 0;\n"
            "  for (const line of log) {\n"
            "    const [verb, , count] = line.split(\" \");\n"
            "    total += verb === \"add\" ? Number(count) : -Number(count);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        checks=(((["add tea 3", "take tea 1", "add jam 2"],), 4),
                ((["add pen 5", "take pen 5", "add ink 1"],), 1)),
    ),
    two=Part(
        brief="Which kinds are still in stock - more than 0 left? Give their "
              "names in alphabetical order.",
        params=("log",),
        cases=STOCK_CASES,
        solve=_in_stock,
        example="['add pen 5', 'take pen 5', 'add ink 1'] → ['ink']",
        py_answer=(
            "def part_two(log):\n"
            "    stock = {}\n"
            "    for line in log:\n"
            "        verb, name, count = line.split(\" \")\n"
            "        change = int(count) if verb == \"add\" else -int(count)\n"
            "        stock[name] = stock.get(name, 0) + change\n"
            "    return sorted(name for name, n in stock.items() if n > 0)\n"
        ),
        js_answer=(
            "function partTwo(log) {\n"
            "  const stock = {};\n"
            "  for (const line of log) {\n"
            "    const [verb, name, count] = line.split(\" \");\n"
            "    const change = verb === \"add\" ? Number(count) : -Number(count);\n"
            "    stock[name] = (stock[name] ?? 0) + change;\n"
            "  }\n"
            "  return Object.keys(stock).filter((name) => stock[name] > 0).sort();\n"
            "}\n"
        ),
        checks=(((["add pen 5", "take pen 5", "add ink 1"],), ["ink"]), (([],), []),
                ((["add a 2", "add b 2", "take a 1", "take b 2", "add c 4"],), ["a", "c"])),
    ),
    lesson="One running number answers 'how many in all'. 'Which kinds' needs a "
           "number per kind - a dict keyed by name - and only once the whole log "
           "has been replayed can you tell which ones ended above zero.",
)


MORE_PUZZLES_3: tuple[Puzzle, ...] = (STEPS, PARK, TEMPS, RECEIPTS, DIGITS, STOCK)
