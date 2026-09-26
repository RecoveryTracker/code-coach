"""The two projects and their tickets.

Each project is written out as a series of whole files, V0 to V6: V0 is
the codebase on the day you join, and each ticket turns one version into
the next. A ticket's `start` is the version before it and its `after` the
version after, so the story is continuous by construction - and the
suite checks that anyway, since an edit to one ticket's answer that is
not carried into the next ticket's start would otherwise go unnoticed.

The oracles are Python for both projects, like every kata oracle: the
values are numbers, strings, lists and dicts, which mean the same thing
in both languages.
"""

from __future__ import annotations

from code_coach.tickets import Check, Project, Ticket

# ═════════════════════════════════════════════════════════════
# Python: Corner shop orders
# ═════════════════════════════════════════════════════════════

SHOP_V0 = '''\
# Corner shop orders: the module behind the till.
# Prices are in pence, so every sum stays a whole number.

PRICES = {
    "apple": 40,
    "bread": 145,
    "milk": 95,
    "eggs": 210,
    "tea": 250,
}


def line_total(item):
    return PRICES[item["sku"]] * item["qty"]


def order_total(order):
    total = 0
    for item in order:
        total += line_total(item)
    return total


def pounds(pence):
    return "£" + str(pence // 100) + "." + str(pence % 100)


def receipt_lines(order):
    lines = []
    for item in order:
        lines.append(f"{item['qty']} x {item['sku']}  {pounds(line_total(item))}")
    lines.append(f"TOTAL  {pounds(order_total(order))}")
    return lines
'''

SHOP_V1 = SHOP_V0.replace(
    '    return "£" + str(pence // 100) + "." + str(pence % 100)\n',
    '    return f"£{pence // 100}.{pence % 100:02d}"\n',
)

SHOP_V2 = SHOP_V1.replace(
    '''    "tea": 250,
}
''',
    '''    "tea": 250,
}

# Percent off, by code.
DISCOUNTS = {"TENOFF": 10, "STAFF": 25}
''',
).replace(
    '''        total += line_total(item)
    return total
''',
    '''        total += line_total(item)
    return total


def discounted_total(order, code):
    total = order_total(order)
    percent = DISCOUNTS.get(code, 0)
    return total - total * percent // 100
''',
)

SHOP_V3 = SHOP_V2.replace(
    '''    total = order_total(order)
    percent = DISCOUNTS.get(code, 0)
''',
    '''    total = order_total(order)
    if code == "TENOFF" and total < 1000:
        return total
    percent = DISCOUNTS.get(code, 0)
''',
)

SHOP_V4 = SHOP_V3.replace(
    '''    return total - total * percent // 100
''',
    '''    return total - total * percent // 100


def missing_items(order, stock):
    missing = []
    for item in order:
        if item["qty"] > stock.get(item["sku"], 0):
            missing.append(item["sku"])
    return missing
''',
)

SHOP_V5 = SHOP_V4.replace(
    '''def missing_items(order, stock):
    missing = []
    for item in order:
        if item["qty"] > stock.get(item["sku"], 0):
            missing.append(item["sku"])
    return missing
''',
    '''def missing_items(order, stock):
    wanted = {}
    for item in order:
        wanted[item["sku"]] = wanted.get(item["sku"], 0) + item["qty"]
    missing = []
    for sku, qty in wanted.items():
        if qty > stock.get(sku, 0):
            missing.append(sku)
    return missing
''',
)

SHOP_V6 = SHOP_V5.replace(
    '''def receipt_lines(order):
    lines = []
    for item in order:
        lines.append(f"{item['qty']} x {item['sku']}  {pounds(line_total(item))}")
    lines.append''',
    '''def receipt_line(item):
    return f"{item['qty']} x {item['sku']}  {pounds(line_total(item))}"


def receipt_lines(order):
    lines = [receipt_line(item) for item in order]
    lines.append''',
)

# ── Oracles ──────────────────────────────────────────────────

_PRICES = {"apple": 40, "bread": 145, "milk": 95, "eggs": 210, "tea": 250}
_DISCOUNTS = {"TENOFF": 10, "STAFF": 25}


def _line_total(item):
    return _PRICES[item["sku"]] * item["qty"]


def _order_total(order):
    return sum(_line_total(item) for item in order)


def _pounds(pence):
    return "£%d.%02d" % (pence // 100, pence % 100)


def _receipt_line(item):
    return f"{item['qty']} x {item['sku']}  {_pounds(_line_total(item))}"


def _receipt_lines(order):
    return [_receipt_line(i) for i in order] + [
        "TOTAL  " + _pounds(_order_total(order))]


def _discounted_v2(order, code):
    total = _order_total(order)
    return total - total * _DISCOUNTS.get(code, 0) // 100


def _discounted_v3(order, code):
    total = _order_total(order)
    if code == "TENOFF" and total < 1000:
        return total
    return _discounted_v2(order, code)


def _missing_v4(order, stock):
    return [i["sku"] for i in order if i["qty"] > stock.get(i["sku"], 0)]


def _missing_v5(order, stock):
    wanted: dict[str, int] = {}
    for i in order:
        wanted[i["sku"]] = wanted.get(i["sku"], 0) + i["qty"]
    return [sku for sku, qty in wanted.items() if qty > stock.get(sku, 0)]


# ── Cases ────────────────────────────────────────────────────


def _i(sku, qty):
    return {"sku": sku, "qty": qty}


_ITEMS = ((_i("apple", 3),), (_i("tea", 1),), (_i("bread", 2),),
          (_i("eggs", 0),), (_i("milk", 7),))

_ORDERS = (
    ([],),
    ([_i("apple", 3)],),
    ([_i("apple", 2), _i("milk", 1)],),
    ([_i("bread", 1), _i("eggs", 2), _i("tea", 4)],),
    ([_i("milk", 1), _i("apple", 1)],),
    ([_i("eggs", 1), _i("milk", 1)],),
)

LINE_TOTAL = Check(
    "line_total", ("item",), _ITEMS, _line_total,
    checks=(((_i("apple", 3),), 120), ((_i("eggs", 0),), 0)))

ORDER_TOTAL = Check(
    "order_total", ("order",), _ORDERS, _order_total,
    checks=((([],), 0), (([_i("apple", 2), _i("milk", 1)],), 175)))

POUNDS = Check(
    "pounds", ("pence",),
    ((0,), (5,), (40,), (105,), (150,), (1000,), (1234,), (99,)),
    _pounds,
    checks=(((105,), "£1.05"), ((0,), "£0.00"), ((1234,), "£12.34")))

RECEIPT_LINES = Check(
    "receipt_lines", ("order",), _ORDERS, _receipt_lines,
    checks=((([_i("milk", 1), _i("apple", 1)],),
             ["1 x milk  £0.95", "1 x apple  £0.40", "TOTAL  £1.35"]),
            (([],), ["TOTAL  £0.00"])))

_DISCOUNT_CASES_V2 = (
    ([_i("apple", 3)], "TENOFF"),
    ([_i("tea", 4), _i("eggs", 1)], "TENOFF"),
    ([_i("tea", 4), _i("eggs", 1)], "STAFF"),
    ([_i("milk", 1)], "STAFF"),
    ([_i("bread", 2)], "FREEBIE"),
    ([_i("bread", 2)], ""),
    ([], "STAFF"),
)

DISCOUNTED_V2 = Check(
    "discounted_total", ("order", "code"), _DISCOUNT_CASES_V2, _discounted_v2,
    checks=((([_i("apple", 3)], "TENOFF"), 108),
            (([_i("milk", 1)], "STAFF"), 72),
            (([_i("bread", 2)], "FREEBIE"), 290)))

DISCOUNTED_V3 = Check(
    "discounted_total", ("order", "code"),
    _DISCOUNT_CASES_V2 + (
        ([_i("tea", 4)], "TENOFF"),         # exactly £10.00: counts
        ([_i("apple", 24)], "TENOFF"),       # £9.60: too little
        ([_i("tea", 3), _i("milk", 1)], "TENOFF"),   # £8.45
    ),
    _discounted_v3,
    checks=((([_i("apple", 3)], "TENOFF"), 120),
            (([_i("tea", 4)], "TENOFF"), 900),
            (([_i("milk", 1)], "STAFF"), 72)))

_STOCK = {"apple": 5, "bread": 2, "milk": 0, "tea": 10}

MISSING_V4 = Check(
    "missing_items", ("order", "stock"),
    (
        ([], _STOCK),
        ([_i("apple", 3)], _STOCK),
        ([_i("apple", 6)], _STOCK),
        ([_i("milk", 1), _i("bread", 2)], _STOCK),
        ([_i("eggs", 1), _i("tea", 10), _i("bread", 3)], _STOCK),
        ([_i("apple", 1)], {}),
    ),
    _missing_v4,
    checks=((([_i("eggs", 1), _i("tea", 10), _i("bread", 3)], _STOCK),
             ["eggs", "bread"]),
            (([_i("apple", 5)], _STOCK), [])))

MISSING_V5 = Check(
    "missing_items", ("order", "stock"),
    MISSING_V4.cases + (
        ([_i("apple", 3), _i("apple", 3)], _STOCK),
        ([_i("apple", 2), _i("bread", 1), _i("apple", 3)], _STOCK),
        ([_i("bread", 2), _i("milk", 1), _i("bread", 1), _i("milk", 1)], _STOCK),
    ),
    _missing_v5,
    checks=((([_i("apple", 3), _i("apple", 3)], _STOCK), ["apple"]),
            (([_i("bread", 2), _i("milk", 1), _i("bread", 1), _i("milk", 1)],
              _STOCK), ["bread", "milk"])))

RECEIPT_LINE = Check(
    "receipt_line", ("item",), _ITEMS, _receipt_line,
    checks=(((_i("apple", 3),), "3 x apple  £1.20"),
            ((_i("eggs", 0),), "0 x eggs  £0.00")))


SHOP = Project(
    id="corner-shop",
    title="Corner shop orders",
    language="python",
    story="You have joined the two-person team that keeps the till at "
          "Patel's corner shop running. This module prices an order and "
          "prints the receipt. Priya owns the shop and files the tickets; "
          "Sam wrote most of the code and reviews yours.",
    tickets=(
        Ticket(
            id="shop-1",
            title="Receipt says £3.5 for £3.05",
            kind="bug",
            report="A customer came back with her receipt: eggs and a pint "
                   "of milk, £3.05, and the receipt said £3.5. She thought "
                   "we had overcharged her by 45p. Anything with fewer than "
                   "ten pence after the point comes out wrong - an empty "
                   "order even says £0.0. Can you fix the receipts? - Priya",
            start=SHOP_V0, after=SHOP_V1,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES),
            new=("pounds", "receipt_lines"),
            hint="The pence are printed with str(), which does not know "
                 "they are always two digits. Only one function formats "
                 "money - fix it there and the receipt follows.",
            lesson="The bug was in one small helper and showed up in "
                   "another function. Fixing it at the source rather than "
                   "patching receipt_lines means every caller of pounds is "
                   "right at once - and the totals, which never touched "
                   "pounds, still add up exactly as before.",
        ),
        Ticket(
            id="shop-2",
            title="Discount codes at the till",
            kind="feature",
            report="We are printing flyers with codes on. TENOFF is 10% off "
                   "the order and STAFF is 25% off. Can we get a "
                   "discounted_total(order, code) that gives the price to "
                   "charge in pence? Round the discount down to the penny, "
                   "and a code we do not recognise just means no discount. "
                   "Keep the list of codes somewhere I can find it - I will "
                   "want to add more. - Priya",
            start=SHOP_V1, after=SHOP_V2,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES,
                    DISCOUNTED_V2),
            new=("discounted_total",),
            hint="order_total already exists - call it rather than adding "
                 "up the order again. A dict of code to percent next to "
                 "PRICES keeps the codes in one place; .get(code, 0) covers "
                 "the unknown ones. Integer division rounds the discount "
                 "down: total * percent // 100.",
            lesson="A new feature built on the functions already there, "
                   "not beside them. Nothing old changed, so everything old "
                   "still passes - that is what a feature should look like "
                   "from the outside.",
        ),
        Ticket(
            id="shop-3",
            title="TENOFF needs a £10 minimum spend",
            kind="change",
            report="Bad news on the flyers: people are using TENOFF on a "
                   "single apple. From today TENOFF only works on orders of "
                   "£10.00 or more (before the discount). Under that, they "
                   "pay full price. STAFF stays as it is - that one is for "
                   "Sam and me and we buy milk. - Priya",
            start=SHOP_V2, after=SHOP_V3,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES,
                    DISCOUNTED_V3),
            new=("discounted_total",),
            hint="The rule is about one code and one threshold. Check it "
                 "before the discount is worked out, and let every other "
                 "code carry on down the line it already took. Exactly "
                 "£10.00 counts.",
            lesson="A change of rules touches one branch of one function. "
                   "The cases that did not change - STAFF, unknown codes, "
                   "big TENOFF orders - are the ones a rushed edit breaks, "
                   "which is why they are still being checked.",
        ),
        Ticket(
            id="shop-4",
            title="Warn when we cannot fill an order",
            kind="feature",
            report="Phone orders keep coming in for things we have run out "
                   "of. I need missing_items(order, stock): stock is a dict "
                   "of how many of each thing we have, and it should give "
                   "back the skus we do not have enough of, in the order "
                   "they appear on the order. Something not in the stock "
                   "dict at all means we have none. - Priya",
            start=SHOP_V3, after=SHOP_V4,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES,
                    DISCOUNTED_V3, MISSING_V4),
            new=("missing_items",),
            hint="Walk the order and compare each line's qty with "
                 "stock.get(sku, 0). The order of the result is the order "
                 "of the lines. Do not change the stock dict - it belongs "
                 "to whoever called you.",
            lesson="stock.get(sku, 0) makes 'not listed' and 'none left' "
                   "the same thing, which is what Priya asked for. And the "
                   "stock is only read, never changed - a check that edits "
                   "what it was handed is a bug waiting to happen somewhere "
                   "else.",
        ),
        Ticket(
            id="shop-5",
            title="Stock check misses repeated lines",
            kind="bug",
            report="Sam put through a phone order as 'apple x3' and then "
                   "added another 'apple x3' when they rang back. We only "
                   "had 5 apples and missing_items said everything was "
                   "fine. It needs to add up all the lines for the same "
                   "thing before comparing. Each sku once in the answer, "
                   "please, where it first appears. - Priya",
            start=SHOP_V4, after=SHOP_V5,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES,
                    DISCOUNTED_V3, MISSING_V5),
            new=("missing_items",),
            hint="Two passes: first total the qty per sku in a dict, then "
                 "compare each total with the stock. A dict keeps keys in "
                 "the order they were first added, which is the order the "
                 "ticket wants. A set would lose it.",
            lesson="The first version compared lines; the real question was "
                   "about products. Totalling first and comparing second "
                   "fixes it, and every case the old version got right - "
                   "orders with no repeats - still comes out the same.",
        ),
        Ticket(
            id="shop-6",
            title="Pull out receipt_line for the website",
            kind="refactor",
            report="We are putting orders on the website and I want the "
                   "same line format there as on paper. Can you pull the "
                   "one-line formatting out of receipt_lines into its own "
                   "receipt_line(item), and have receipt_lines use it? "
                   "Nothing on the receipt should change - not a space. "
                   "- Sam",
            start=SHOP_V5, after=SHOP_V6,
            checks=(LINE_TOTAL, ORDER_TOTAL, POUNDS, RECEIPT_LINES,
                    DISCOUNTED_V3, MISSING_V5, RECEIPT_LINE),
            new=("receipt_line",),
            hint="Move the f-string into a function of its own that takes "
                 "one item and returns the string, then call it from the "
                 "loop. The only new behaviour is that receipt_line can be "
                 "called by itself.",
            lesson="A refactor changes the shape of the code and nothing "
                   "it does. Every other check here was a regression check, "
                   "and they were the real test: if one of them had moved, "
                   "it would not have been a refactor any more.",
        ),
    ),
)


# ═════════════════════════════════════════════════════════════
# JavaScript: Team task board
# ═════════════════════════════════════════════════════════════

BOARD_V0 = '''\
// Team task board: the functions behind the board view.
// A task is { id, title, status, assignee, due }.
// status is "todo", "doing" or "done"; due is "YYYY-MM-DD" or null.
// Dates in that shape sort the same as text, so < compares them.

const STATUSES = ["todo", "doing", "done"];

function byStatus(tasks, status) {
  return tasks.filter((t) => t.status === status);
}

function isOverdue(task, today) {
  return task.due < today;
}

function overdue(tasks, today) {
  return tasks.filter((t) => isOverdue(t, today)).map((t) => t.id);
}

function assigneeCounts(tasks) {
  const counts = {};
  for (const t of tasks) {
    counts[t.assignee] = (counts[t.assignee] || 0) + 1;
  }
  return counts;
}

function columns(tasks) {
  const board = {};
  for (const s of STATUSES) {
    board[s] = byStatus(tasks, s).map((t) => t.title);
  }
  return board;
}
'''

BOARD_V1 = BOARD_V0.replace(
    '  return task.due < today;\n',
    '  return task.status !== "done" && task.due < today;\n',
)

BOARD_V2 = BOARD_V1 + '''
function search(tasks, query) {
  const q = query.toLowerCase();
  return tasks.filter((t) => t.title.toLowerCase().includes(q)).map((t) => t.id);
}
'''

BOARD_V3 = BOARD_V2.replace(
    '''  const q = query.toLowerCase();
''',
    '''  const q = query.trim().toLowerCase();
  if (q === "") return [];
''',
)

BOARD_V4 = BOARD_V3 + '''
function sortedByDue(tasks) {
  return [...tasks]
    .sort((a, b) => {
      if (a.due === b.due) return a.id - b.id;
      if (a.due === null) return 1;
      if (b.due === null) return -1;
      return a.due < b.due ? -1 : 1;
    })
    .map((t) => t.id);
}
'''

BOARD_V5 = BOARD_V4.replace(
    '''  for (const t of tasks) {
    counts[t.assignee] = (counts[t.assignee] || 0) + 1;
  }
''',
    '''  for (const t of tasks) {
    if (t.status === "done") continue;
    const who = t.assignee || "unassigned";
    counts[who] = (counts[who] || 0) + 1;
  }
''',
)

BOARD_V6 = BOARD_V5.replace(
    '''function isOverdue(task, today) {
  return task.status !== "done" && task.due < today;
}
''',
    '''function isOpen(task) {
  return task.status !== "done";
}

function isOverdue(task, today) {
  return isOpen(task) && task.due < today;
}
''',
).replace(
    '    if (t.status === "done") continue;\n',
    '    if (!isOpen(t)) continue;\n',
)

# ── Oracles ──────────────────────────────────────────────────

_STATUSES = ("todo", "doing", "done")


def _by_status(tasks, status):
    return [t for t in tasks if t["status"] == status]


def _is_overdue(task, today):
    # null < "2026-..." is false in JavaScript, so no due date is never late.
    return (task["status"] != "done" and task["due"] is not None
            and task["due"] < today)


def _overdue(tasks, today):
    return [t["id"] for t in tasks if _is_overdue(t, today)]


def _counts_v0(tasks):
    counts: dict[str, int] = {}
    for t in tasks:
        counts[t["assignee"]] = counts.get(t["assignee"], 0) + 1
    return counts


def _counts_v5(tasks):
    counts: dict[str, int] = {}
    for t in tasks:
        if t["status"] == "done":
            continue
        who = t["assignee"] or "unassigned"
        counts[who] = counts.get(who, 0) + 1
    return counts


def _columns(tasks):
    return {s: [t["title"] for t in _by_status(tasks, s)] for s in _STATUSES}


def _search_v2(tasks, query):
    q = query.lower()
    return [t["id"] for t in tasks if q in t["title"].lower()]


def _search_v3(tasks, query):
    q = query.strip().lower()
    if not q:
        return []
    return [t["id"] for t in tasks if q in t["title"].lower()]


def _sorted_by_due(tasks):
    ordered = sorted(tasks, key=lambda t: (t["due"] is None, t["due"] or "", t["id"]))
    return [t["id"] for t in ordered]


def _is_open(task):
    return task["status"] != "done"


# ── Cases ────────────────────────────────────────────────────

TODAY = "2026-09-26"


def _t(id_, title, status, assignee, due):
    return {"id": id_, "title": title, "status": status,
            "assignee": assignee, "due": due}


# Everyone assigned, for the checks written before unassigned tasks
# were a thing anyone had asked about.
_TEAM = [
    _t(1, "Fix login redirect", "doing", "ana", "2026-09-20"),
    _t(2, "Write release notes", "todo", "ben", "2026-10-01"),
    _t(3, "Login page copy", "done", "ana", "2026-09-10"),
    _t(4, "Update logo", "todo", "cy", None),
    _t(5, "Audit LOGIN errors", "todo", "ben", "2026-09-26"),
    _t(6, "Ship dark mode", "done", "cy", "2026-09-30"),
]

_SMALL = [
    _t(7, "Backup the database", "doing", "ana", "2026-09-25"),
    _t(8, "Rename repo", "todo", "dev", "2026-09-29"),
]

_WITH_NOBODY = _TEAM + [
    _t(9, "Triage inbox", "todo", None, "2026-09-12"),
    _t(10, "Old spike", "done", None, None),
]

BY_STATUS = Check(
    "byStatus", ("tasks", "status"),
    ((_TEAM, "todo"), (_TEAM, "done"), (_SMALL, "done"), ([], "doing")),
    _by_status,
    checks=(((_SMALL, "done"), []), (([], "doing"), [])))

IS_OVERDUE = Check(
    "isOverdue", ("task", "today"),
    tuple((t, TODAY) for t in _TEAM) + ((_SMALL[0], TODAY),),
    _is_overdue,
    checks=(((_TEAM[0], TODAY), True), ((_TEAM[2], TODAY), False),
            ((_TEAM[4], TODAY), False)))

OVERDUE = Check(
    "overdue", ("tasks", "today"),
    ((_TEAM, TODAY), (_SMALL, TODAY), ([], TODAY), (_TEAM, "2026-12-31")),
    _overdue,
    checks=(((_TEAM, TODAY), [1]), ((_TEAM, "2026-12-31"), [1, 2, 5])))

COUNTS_V0 = Check(
    "assigneeCounts", ("tasks",),
    ((_TEAM,), (_SMALL,), ([],)),
    _counts_v0,
    checks=(((_TEAM,), {"ana": 2, "ben": 2, "cy": 2}),))

COUNTS_V5 = Check(
    "assigneeCounts", ("tasks",),
    ((_TEAM,), (_SMALL,), ([],), (_WITH_NOBODY,)),
    _counts_v5,
    checks=(((_TEAM,), {"ana": 1, "ben": 2, "cy": 1}),
            ((_WITH_NOBODY,), {"ana": 1, "ben": 2, "cy": 1, "unassigned": 1})))

COLUMNS = Check(
    "columns", ("tasks",),
    ((_TEAM,), (_SMALL,), ([],)),
    _columns,
    checks=((([],), {"todo": [], "doing": [], "done": []}),
            ((_SMALL,), {"todo": ["Rename repo"],
                         "doing": ["Backup the database"], "done": []})))

_SEARCHES = ((_TEAM, "login"), (_TEAM, "LOGIN"), (_TEAM, "logo"),
             (_TEAM, "notes"), (_TEAM, "zebra"), ([], "login"))

SEARCH_V2 = Check(
    "search", ("tasks", "query"), _SEARCHES, _search_v2,
    checks=(((_TEAM, "login"), [1, 3, 5]), ((_TEAM, "zebra"), [])))

SEARCH_V3 = Check(
    "search", ("tasks", "query"),
    _SEARCHES + ((_TEAM, ""), (_TEAM, "   "), (_TEAM, " logo "),
                 (_TEAM, "Login ")),
    _search_v3,
    checks=(((_TEAM, ""), []), ((_TEAM, " logo "), [4]),
            ((_TEAM, "Login "), [1, 3, 5])))

SORTED = Check(
    "sortedByDue", ("tasks",),
    ((_TEAM,), (_SMALL,), ([],), (_WITH_NOBODY,),
     ([_t(12, "b", "todo", "x", "2026-10-01"),
       _t(11, "a", "todo", "x", "2026-10-01")],)),
    _sorted_by_due,
    checks=(((_TEAM,), [3, 1, 5, 6, 2, 4]),
            (([_t(12, "b", "todo", "x", "2026-10-01"),
               _t(11, "a", "todo", "x", "2026-10-01")],), [11, 12])))

IS_OPEN = Check(
    "isOpen", ("task",),
    tuple((t,) for t in _TEAM),
    _is_open,
    checks=(((_TEAM[0],), True), ((_TEAM[2],), False)))

_BOARD_BASE = (BY_STATUS, IS_OVERDUE, OVERDUE)

BOARD = Project(
    id="task-board",
    title="Team task board",
    language="javascript",
    story="Your team's in-house task board - a Kanban board with To do, "
          "Doing and Done columns. This file is the logic behind the "
          "board view. Mia leads the team and writes most tickets; Ola "
          "does code review.",
    tickets=(
        Ticket(
            id="board-1",
            title="Finished tasks show as overdue",
            kind="bug",
            report="The red 'overdue' badge is on 'Login page copy', which "
                   "we finished two weeks ago. A task that is done cannot be "
                   "late. Please fix isOverdue so done tasks are never "
                   "overdue - the overdue list uses it too. - Mia",
            start=BOARD_V0, after=BOARD_V1,
            checks=_BOARD_BASE + (COUNTS_V0, COLUMNS),
            new=("isOverdue", "overdue"),
            hint="overdue already asks isOverdue about each task, so the "
                 "fix belongs in isOverdue and overdue gets it for free. "
                 "A task is late only if it is not done AND its date has "
                 "passed.",
            lesson="Fix it where the rule lives. Patching overdue with its "
                   "own filter would have left isOverdue - which the badge "
                   "calls directly - still wrong, and two places deciding "
                   "the same thing is how they drift apart.",
        ),
        Ticket(
            id="board-2",
            title="Search box",
            kind="feature",
            report="The board is getting long. We need search(tasks, query): "
                   "the ids of tasks whose title contains the query, "
                   "ignoring case, in board order. 'login' should find "
                   "'Audit LOGIN errors' too. - Mia",
            start=BOARD_V1, after=BOARD_V2,
            checks=_BOARD_BASE + (COUNTS_V0, COLUMNS, SEARCH_V2),
            new=("search",),
            hint="Lower-case both sides and use includes. filter, then map "
                 "to the id, like overdue does.",
            lesson="A feature that adds a function and touches nothing "
                   "else. The checks on the old functions were there all "
                   "along - they pass because nothing moved.",
        ),
        Ticket(
            id="board-3",
            title="Empty search shows everything",
            kind="bug",
            report="When I clear the search box the list fills with every "
                   "task on the board, and with 800 tasks the page hangs. An "
                   "empty search should find nothing. Also, pasting ' logo ' "
                   "with spaces round it finds nothing, which confused "
                   "people. - Ola",
            start=BOARD_V2, after=BOARD_V3,
            checks=_BOARD_BASE + (COUNTS_V0, COLUMNS, SEARCH_V3),
            new=("search",),
            hint="Every string includes the empty string, so an empty "
                 "query matches everything. Trim the query first; if "
                 "nothing is left, return an empty list.",
            lesson="Two edge cases from real use: empty and padded input. "
                   "Trimming once at the top covers both, and every search "
                   "that worked before still works because an ordinary "
                   "query has nothing to trim.",
        ),
        Ticket(
            id="board-4",
            title="Sort by due date",
            kind="feature",
            report="Add sortedByDue(tasks): the task ids, soonest due first. "
                   "Tasks with no due date go at the end. If two share a "
                   "date, lower id first so the order does not jump around. "
                   "And please do not reorder the array the board is "
                   "holding - Ola lost an afternoon to that last time. - Mia",
            start=BOARD_V3, after=BOARD_V4,
            checks=_BOARD_BASE + (COUNTS_V0, COLUMNS, SEARCH_V3, SORTED),
            new=("sortedByDue",),
            hint="Array.prototype.sort sorts in place - it changes the "
                 "array it is called on. Copy first: [...tasks].sort(...). "
                 "In the comparator, deal with equal dates and nulls before "
                 "comparing the date strings.",
            lesson="sort changes the caller's array, and the checker "
                   "compares the arguments before and after each call, so "
                   "tasks.sort(...) fails even with the right order. Copying "
                   "first is the whole difference between a helper and a "
                   "side effect.",
        ),
        Ticket(
            id="board-5",
            title="Workload should count open tasks only",
            kind="change",
            report="Change of plan for the workload panel. It should show "
                   "how much each person has still to do, so done tasks do "
                   "not count any more. And tasks nobody has picked up "
                   "currently show under 'null' - count them as "
                   "'unassigned'. - Mia",
            start=BOARD_V4, after=BOARD_V5,
            checks=_BOARD_BASE + (COUNTS_V5, COLUMNS, SEARCH_V3, SORTED),
            new=("assigneeCounts",),
            hint="Skip done tasks at the top of the loop, and pick the key "
                 "with t.assignee || \"unassigned\" before counting.",
            lesson="The rule for one function changed, so that function's "
                   "old answers are now wrong on purpose - and only that "
                   "function's. The columns still show done tasks, because "
                   "the ticket was about the workload panel, not the board.",
        ),
        Ticket(
            id="board-6",
            title="Pull out isOpen",
            kind="refactor",
            report="We are adding a 'cancelled' status next sprint, and "
                   "'not done' is now decided in two places (isOverdue and "
                   "assigneeCounts). Pull it into one isOpen(task) helper "
                   "and use it in both, so the next rule change is a "
                   "one-line edit. No behaviour changes. - Ola",
            start=BOARD_V5, after=BOARD_V6,
            checks=_BOARD_BASE + (COUNTS_V5, COLUMNS, SEARCH_V3, SORTED,
                                  IS_OPEN),
            new=("isOpen",),
            hint="isOpen returns task.status !== \"done\". Then replace "
                 "the two copies of that test with calls to it.",
            lesson="A refactor is judged by what did not change: every "
                   "check except the new helper was a regression check. "
                   "Now 'cancelled' will be one edit in isOpen, and both "
                   "callers will agree about it automatically.",
        ),
    ),
)


PROJECTS: tuple[Project, ...] = (SHOP, BOARD)
