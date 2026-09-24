"""More hunts, each a different kind of bug from the first eight.

Added because eight was too few to practise on, and chosen so that each
teaches a mistake the others do not - a second off-by-one would be more
practice at one thing, not practice at hunting. Between them:

  Python      a helper that is right and never called; numbers compared
              as text; a slice that means "everything" when n is 0; a
              line one indent too deep
  JavaScript  sort() sorting numbers as text; != deciding 0 is blank;
              fill() handing every slot the same array; parseInt reading
              "1,000" as 1

The same rules hold as for the first set, and the suite checks all of
them: the bug is real, it hides on some inputs, the report's own input
shows it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

PYTHON = "Python"
JAVASCRIPT = "JavaScript"


# ── Python ───────────────────────────────────────────────────


def _cart_total(items: list) -> int:
    return sum(item["price"] * item["qty"] for item in items)


def _oldest(text: str):
    ages = [int(part) for part in text.split(",") if part.strip()]
    return max(ages) if ages else None


def _recent(events: list, n: int) -> list:
    n = max(0, min(n, 50))
    return events[max(0, len(events) - n):]


def _final_balances(accounts: list) -> list:
    return [sum(changes) for changes in accounts]


PYTHON_HUNTS_2: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-cart-quantity",
        title="Two coffees cost 3",
        family=PYTHON,
        language="python",
        level=1,
        report="Two coffees at 3 each: the cart says the total is 3, not 6. "
               "Buying one of something always looks fine.",
        name="cart_total",
        params=("items",),
        start=(
            "def line_total(item):\n"
            "    return item[\"price\"] * item[\"qty\"]\n"
            "\n"
            "\n"
            "def subtotal(items):\n"
            "    total = 0\n"
            "    for item in items:\n"
            "        total += item[\"price\"]\n"
            "    return total\n"
            "\n"
            "\n"
            "def cart_total(items):\n"
            "    return subtotal(items)\n"
        ),
        fixed=(
            "def line_total(item):\n"
            "    return item[\"price\"] * item[\"qty\"]\n"
            "\n"
            "\n"
            "def subtotal(items):\n"
            "    total = 0\n"
            "    for item in items:\n"
            "        total += line_total(item)\n"
            "    return total\n"
            "\n"
            "\n"
            "def cart_total(items):\n"
            "    return subtotal(items)\n"
        ),
        solve=_cart_total,
        reported=([{"price": 3, "qty": 2}],),
        cases=(([],), ([{"price": 3, "qty": 2}],), ([{"price": 5, "qty": 1}],),
               ([{"price": 2, "qty": 1}, {"price": 4, "qty": 3}],),
               ([{"price": 10, "qty": 1}, {"price": 1, "qty": 1}],)),
        cause="subtotal adds each item's price once and ignores how many "
              "were bought.",
        decoys=(
            "line_total multiplies when it should add.",
            "total should start at 1, not 0.",
            "cart_total returns before the loop has finished.",
        ),
        lesson="A helper that does exactly the right thing, sitting unused, "
               "is a clue. A bug is often the right code, already written, "
               "and never called.",
        hint="Buy two of something: cart_total([{\"price\": 3, \"qty\": 2}]).",
        checks=((([{"price": 3, "qty": 2}],), 6), (([],), 0),
                (([{"price": 2, "qty": 1}, {"price": 4, "qty": 3}],), 14)),
    ),
    Hunt(
        id="hunt-oldest-age",
        title="The oldest is 9",
        family=PYTHON,
        language="python",
        level=2,
        report="For the ages 9, 10 and 25, the app says the oldest person is "
               "9.",
        name="oldest",
        params=("text",),
        start=(
            "def parse_ages(text):\n"
            "    return [part.strip() for part in text.split(\",\") if part.strip()]\n"
            "\n"
            "\n"
            "def oldest(text):\n"
            "    ages = parse_ages(text)\n"
            "    if not ages:\n"
            "        return None\n"
            "    return int(max(ages))\n"
        ),
        fixed=(
            "def parse_ages(text):\n"
            "    return [int(part) for part in text.split(\",\") if part.strip()]\n"
            "\n"
            "\n"
            "def oldest(text):\n"
            "    ages = parse_ages(text)\n"
            "    if not ages:\n"
            "        return None\n"
            "    return int(max(ages))\n"
        ),
        solve=_oldest,
        reported=("9, 10, 25",),
        cases=(("",), ("5, 7",), ("9, 10, 25",), ("12, 30",), ("100, 99",)),
        cause="The ages are compared as text, and as text '9' comes after "
              "'25', because 9 is bigger than 2.",
        decoys=(
            "max() gives back the first item when the list is short.",
            "split(',') leaves spaces in that confuse max().",
            "int() rounds the answer down.",
        ),
        lesson="Text is compared letter by letter, so '9' beats '10'. Turn "
               "numbers that arrive as text into numbers where they come "
               "in, not where they are used.",
        hint="The ages from the report: oldest(\"9, 10, 25\"). Then try two "
             "ages with the same number of digits.",
        checks=((("9, 10, 25",), 25), (("",), None), (("5, 7",), 7)),
    ),
    Hunt(
        id="hunt-recent-zero",
        title="Zero recent means everything",
        family=PYTHON,
        language="python",
        level=2,
        report="Asking for the 0 most recent events shows every event there "
               "is. Asking for 2 shows the last 2, as it should.",
        name="recent",
        params=("events", "n"),
        start=(
            "MAX_SHOWN = 50\n"
            "\n"
            "\n"
            "def clamp(n):\n"
            "    return max(0, min(n, MAX_SHOWN))\n"
            "\n"
            "\n"
            "def recent(events, n):\n"
            "    n = clamp(n)\n"
            "    return events[-n:]\n"
        ),
        fixed=(
            "MAX_SHOWN = 50\n"
            "\n"
            "\n"
            "def clamp(n):\n"
            "    return max(0, min(n, MAX_SHOWN))\n"
            "\n"
            "\n"
            "def recent(events, n):\n"
            "    n = clamp(n)\n"
            "    return events[max(0, len(events) - n):]\n"
        ),
        solve=_recent,
        reported=([1, 2, 3], 0),
        cases=(([1, 2, 3], 2), ([1, 2, 3], 0), ([], 3), ([1, 2, 3], 5),
               ([1, 2, 3, 4], 1)),
        cause="When n is 0, events[-0:] is events[0:] - the whole list, "
              "because -0 is just 0.",
        decoys=(
            "clamp lets n go above the number of events.",
            "MAX_SHOWN cuts the list short.",
            "Slicing from the end reverses the order.",
        ),
        lesson="Negative indexes count from the end, but -0 is 0, which is "
               "the start. Any slice written [-n:] needs a thought about n "
               "being 0.",
        hint="The report's input: recent([1, 2, 3], 0). What should zero "
             "events look like?",
        checks=((([1, 2, 3], 0), []), (([1, 2, 3], 2), [2, 3]), (([], 3), [])),
    ),
    Hunt(
        id="hunt-balances-indent",
        title="Too many balances",
        family=PYTHON,
        language="python",
        level=3,
        report="Two accounts, with changes [10, -5] and [3], should end on "
               "[5, 3]. We get [10, 5, 3]. Accounts with one change each are "
               "fine.",
        name="final_balances",
        params=("accounts",),
        start=(
            "def apply(balance, change):\n"
            "    return balance + change\n"
            "\n"
            "\n"
            "def final_balances(accounts):\n"
            "    results = []\n"
            "    for changes in accounts:\n"
            "        balance = 0\n"
            "        for change in changes:\n"
            "            balance = apply(balance, change)\n"
            "            results.append(balance)\n"
            "    return results\n"
        ),
        fixed=(
            "def apply(balance, change):\n"
            "    return balance + change\n"
            "\n"
            "\n"
            "def final_balances(accounts):\n"
            "    results = []\n"
            "    for changes in accounts:\n"
            "        balance = 0\n"
            "        for change in changes:\n"
            "            balance = apply(balance, change)\n"
            "        results.append(balance)\n"
            "    return results\n"
        ),
        solve=_final_balances,
        reported=([[10, -5], [3]],),
        cases=(([],), ([[10], [3]],), ([[10, -5], [3]],), ([[1, 1, 1]],),
               ([[]],)),
        cause="results.append is inside the inner loop, so it records every "
              "step instead of each account's final balance.",
        decoys=(
            "balance should be set to 0 outside the outer loop.",
            "apply adds the change the wrong way round.",
            "The accounts are processed in the wrong order.",
        ),
        lesson="In Python the indentation is the logic. A line one level too "
               "deep runs once for every inner step instead of once for each "
               "outer item.",
        hint="The report's accounts: final_balances([[10, -5], [3]]). Then "
             "give every account just one change.",
        checks=((([[10, -5], [3]],), [5, 3]), (([],), []), (([[]],), [0])),
    ),
)


# ── JavaScript ───────────────────────────────────────────────


def _high_scores(scores: list) -> list:
    return sorted(scores, reverse=True)[:3]


def _missing_fields(form: dict, required: list) -> list:
    return [name for name in required if form.get(name) in (None, "")]


def _bucket_by_length(words: list, count: int) -> list:
    buckets: list[list] = [[] for _ in range(count)]
    for word in words:
        buckets[len(word) % count].append(word)
    return buckets


def _total_donations(entries: list) -> int:
    return sum(int(text.replace(",", "")) for text in entries)


JAVASCRIPT_HUNTS_2: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-js-high-scores",
        title="100 is not the high score",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        report="Scores of 9, 10 and 100 show on the board as 9, 100, 10. "
               "Small scores always look right.",
        name="highScores",
        params=("scores",),
        start=(
            "const TOP = 3;\n"
            "\n"
            "function ranked(scores) {\n"
            "  return [...scores].sort().reverse();\n"
            "}\n"
            "\n"
            "function highScores(scores) {\n"
            "  return ranked(scores).slice(0, TOP);\n"
            "}\n"
        ),
        fixed=(
            "const TOP = 3;\n"
            "\n"
            "function ranked(scores) {\n"
            "  return [...scores].sort((a, b) => a - b).reverse();\n"
            "}\n"
            "\n"
            "function highScores(scores) {\n"
            "  return ranked(scores).slice(0, TOP);\n"
            "}\n"
        ),
        solve=_high_scores,
        reported=([9, 10, 100],),
        cases=(([],), ([3, 1, 2],), ([9, 10, 100],), ([50, 5, 500, 55],),
               ([7],)),
        cause="sort() with no function compares the numbers as text, so 9 "
              "sorts after 100.",
        decoys=(
            "reverse() runs before the sort has finished.",
            "slice(0, TOP) drops the highest score.",
            "Spreading into [...scores] changes the numbers.",
        ),
        lesson="JavaScript's sort() is alphabetical unless you give it a "
               "comparison. For numbers, always pass (a, b) => a - b.",
        hint="The report's scores: highScores([9, 10, 100]). Then try three "
             "single-digit scores.",
        checks=((([9, 10, 100],), [100, 10, 9]), (([],), []),
                (([3, 1, 2],), [3, 2, 1])),
    ),
    Hunt(
        id="hunt-js-zero-missing",
        title="Zero counts as blank",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="Someone ordering a quantity of 0 is told the quantity is "
               "missing. 0 is a real answer.",
        name="missingFields",
        params=("form", "required"),
        start=(
            "const EMPTY = \"\";\n"
            "\n"
            "function isFilled(value) {\n"
            "  return value != EMPTY && value != null;\n"
            "}\n"
            "\n"
            "function missingFields(form, required) {\n"
            "  return required.filter((name) => !isFilled(form[name]));\n"
            "}\n"
        ),
        fixed=(
            "const EMPTY = \"\";\n"
            "\n"
            "function isFilled(value) {\n"
            "  return value !== EMPTY && value != null;\n"
            "}\n"
            "\n"
            "function missingFields(form, required) {\n"
            "  return required.filter((name) => !isFilled(form[name]));\n"
            "}\n"
        ),
        solve=_missing_fields,
        reported=({"qty": 0}, ["qty"]),
        cases=(({"qty": 0}, ["qty"]), ({"name": "Ada"}, ["name"]),
               ({}, ["name"]), ({"name": ""}, ["name"]),
               ({"name": "Ada", "qty": 0}, ["name", "qty"]),
               ({"qty": 3}, ["qty"])),
        cause="!= converts before comparing, and 0 converted to text equals "
              "the empty string - so 0 counts as blank.",
        decoys=(
            "form[name] reads the wrong field.",
            "filter keeps the fields it should drop.",
            "null and undefined are treated differently.",
        ),
        lesson="!= and == convert types first, which is how 0 ends up equal "
               "to \"\". Use !== and === unless you have a reason not to.",
        hint="The report's form: missingFields({\"qty\": 0}, [\"qty\"]). Then "
             "try a quantity of 3.",
        checks=((({"qty": 0}, ["qty"]), []), (({}, ["name"]), ["name"]),
                (({"name": ""}, ["name"]), ["name"])),
    ),
    Hunt(
        id="hunt-js-shared-buckets",
        title="Every word in every bucket",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="Sorting ['a', 'bb'] into 2 buckets by length puts both words "
               "in both buckets. With a single bucket it looks fine.",
        name="bucketByLength",
        params=("words", "count"),
        start=(
            "function makeBuckets(count) {\n"
            "  return new Array(count).fill([]);\n"
            "}\n"
            "\n"
            "function bucketByLength(words, count) {\n"
            "  const buckets = makeBuckets(count);\n"
            "  for (const word of words) {\n"
            "    buckets[word.length % count].push(word);\n"
            "  }\n"
            "  return buckets;\n"
            "}\n"
        ),
        fixed=(
            "function makeBuckets(count) {\n"
            "  return Array.from({ length: count }, () => []);\n"
            "}\n"
            "\n"
            "function bucketByLength(words, count) {\n"
            "  const buckets = makeBuckets(count);\n"
            "  for (const word of words) {\n"
            "    buckets[word.length % count].push(word);\n"
            "  }\n"
            "  return buckets;\n"
            "}\n"
        ),
        solve=_bucket_by_length,
        reported=(["a", "bb"], 2),
        cases=(([], 2), (["a"], 1), (["a", "bb"], 2), (["cat", "dog"], 1),
               (["a", "bb", "ccc"], 3)),
        cause="fill([]) puts the very same array in every bucket, so pushing "
              "into one pushes into all of them.",
        decoys=(
            "word.length % count picks the wrong bucket.",
            "new Array(count) makes one bucket too few.",
            "push adds each word twice.",
        ),
        lesson="fill() copies the value you give it - and for an array or "
               "object, the value is a reference. Every slot points at the "
               "same thing.",
        hint="The report's words: bucketByLength([\"a\", \"bb\"], 2). Then "
             "try just one bucket.",
        checks=(((["a", "bb"], 2), [["bb"], ["a"]]), (([], 2), [[], []]),
                ((["a"], 1), [["a"]])),
    ),
    Hunt(
        id="hunt-js-donations-comma",
        title="1,000 plus 50 is 51",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        report="Donations of '1,000' and '50' add up to 51 on the total. "
               "Donations under a thousand add up fine.",
        name="totalDonations",
        params=("entries",),
        start=(
            "function toNumber(text) {\n"
            "  return parseInt(text, 10);\n"
            "}\n"
            "\n"
            "function totalDonations(entries) {\n"
            "  let total = 0;\n"
            "  for (const entry of entries) {\n"
            "    total += toNumber(entry);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        fixed=(
            "function toNumber(text) {\n"
            "  return parseInt(text.replace(/,/g, \"\"), 10);\n"
            "}\n"
            "\n"
            "function totalDonations(entries) {\n"
            "  let total = 0;\n"
            "  for (const entry of entries) {\n"
            "    total += toNumber(entry);\n"
            "  }\n"
            "  return total;\n"
            "}\n"
        ),
        solve=_total_donations,
        reported=(["1,000", "50"],),
        cases=(([],), (["50"],), (["1,000", "50"],), (["20", "30"],),
               (["2,500"],)),
        cause="parseInt stops reading at the first character that is not a "
              "digit, so '1,000' becomes 1.",
        decoys=(
            "The 10 in parseInt should be 1000.",
            "total starts at the wrong number.",
            "+= joins the numbers together as text.",
        ),
        lesson="parseInt does not fail on odd input - it quietly reads as "
               "much as it can. Numbers people type have commas, spaces and "
               "currency signs; clean them first.",
        hint="The report's donations: totalDonations([\"1,000\", \"50\"]). "
             "What does parseInt make of the first one on its own?",
        checks=(((["1,000", "50"],), 1050), (([],), 0), ((["2,500"],), 2500)),
    ),
)
