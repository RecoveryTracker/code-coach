"""More JavaScript katas: the modern everyday parts of the language.

The first set (js.py) is the shapes a vanilla app is made of. These are
the tools written JavaScript now reaches for first - `Array.from` with a
length, `padStart`, optional chaining and `??`, `flatMap`, `Set`,
`Object.entries` and `fromEntries`, `reduce` into an object, and
destructuring with defaults inside a template literal. Each one replaces
a loop and a temporary, and each has one edge that a loop would have
handled by accident: the missing key, the null in the middle, the empty
line, the refund.

Same rules as every kata: the oracle is Python, `js_answer` is run
through the real driver against it, and nothing may change what it was
handed.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "JavaScript"


def _first_squares(n: int) -> list:
    return [(i + 1) ** 2 for i in range(n)]


def _pad_id(n: int, width: int) -> str:
    return str(n).rjust(width, "0")


def _city_of(user) -> str:
    address = user.get("address") if isinstance(user, dict) else None
    city = address.get("city") if isinstance(address, dict) else None
    return "unknown" if city is None else city


def _all_words(lines: list) -> list:
    return [word for line in lines for word in line.split(" ") if word]


def _missing_from(wanted: list, have: list) -> list:
    return [x for x in wanted if x not in have]


def _invert_object(record: dict) -> dict:
    return {value: key for key, value in record.items()}


def _totals_by(orders: list) -> dict:
    totals: dict = {}
    for order in orders:
        totals[order["name"]] = totals.get(order["name"], 0) + order["amount"]
    return totals


def _money(cents: int) -> str:
    sign = "-" if cents < 0 else ""
    return f"{sign}${abs(cents) // 100}.{abs(cents) % 100:02d}"


def _order_line(item: dict) -> str:
    qty = item.get("qty", 1)
    return (f"{qty} x {item['name']} @ {_money(item['cents'])} = "
            f"{_money(item['cents'] * qty)}")


JS_KATAS_3: tuple[Kata, ...] = (
    Kata(
        id="js-first-squares",
        level=1,
        language="javascript",
        name="firstSquares",
        brief="Return the squares of 1 to n in order. n of 0 gives an empty array.",
        params=("n",),
        family=FAMILY,
        example="firstSquares(3) is [1, 4, 9]",
        hint=(
            "Array.from({ length: n }, (_, i) => ...) makes an array of n "
            "things without a loop; the second argument gets the index."
        ),
        cases=((3,), (0,), (1,), (2,), (5,), (4,), (6,), (10,), (7,), (8,)),
        solve=_first_squares,
        checks=(((3,), [1, 4, 9]), ((0,), []), ((1,), [1]), ((5,), [1, 4, 9, 16, 25])),
        js_answer=(
            "function firstSquares(n) {\n"
            "  return Array.from({ length: n }, (_, i) => (i + 1) ** 2);\n"
            "}"
        ),
    ),
    Kata(
        id="js-pad-id",
        level=1,
        language="javascript",
        name="padId",
        brief=(
            "Write the whole number n with zeros in front until it is at "
            "least `width` characters. A longer number is left as it is."
        ),
        params=("n", "width"),
        family=FAMILY,
        example='padId(7, 3) is "007"',
        hint="padStart takes the length you want and what to pad with.",
        cases=(
            (7, 3), (0, 1), (123, 2), (0, 3), (42, 0), (5, 1), (99, 4),
            (1, 5), (1000, 4), (12, 6),
        ),
        solve=_pad_id,
        checks=(
            ((7, 3), "007"), ((0, 1), "0"), ((0, 3), "000"), ((123, 2), "123"),
            ((42, 0), "42"),
        ),
        js_answer=(
            "function padId(n, width) {\n"
            '  return String(n).padStart(width, "0");\n'
            "}"
        ),
    ),
    Kata(
        id="js-city-of",
        level=2,
        language="javascript",
        name="cityOf",
        brief=(
            "Return user.address.city, or \"unknown\" when the user, the "
            "address or the city is missing or null. An empty city is "
            "still a city."
        ),
        params=("user",),
        family=FAMILY,
        example='cityOf({ address: { city: "Leeds" } }) is "Leeds"',
        hint=(
            "?. stops at null or undefined instead of throwing, and ?? "
            "only replaces null or undefined - unlike ||, which would "
            "also throw away an empty string."
        ),
        cases=(
            ({"address": {"city": "Leeds"}},), ({},), (None,),
            ({"address": None},), ({"address": {}},),
            ({"address": {"city": ""}},), ({"address": {"city": None}},),
            ({"name": "Ada", "address": {"city": "Paris", "zip": "75"}},),
            ({"name": "Bo"},), ({"address": {"city": "Oslo"}},),
        ),
        solve=_city_of,
        checks=(
            (({"address": {"city": "Leeds"}},), "Leeds"), (({},), "unknown"),
            ((None,), "unknown"), (({"address": None},), "unknown"),
            (({"address": {"city": ""}},), ""),
            (({"address": {"city": None}},), "unknown"),
        ),
        js_answer=(
            "function cityOf(user) {\n"
            '  return user?.address?.city ?? "unknown";\n'
            "}"
        ),
    ),
    Kata(
        id="js-all-words",
        level=2,
        language="javascript",
        name="allWords",
        brief=(
            "Return every word from every line, in order, as one flat "
            "array. Words are separated by spaces, and a run of spaces "
            "gives no empty words."
        ),
        params=("lines",),
        family=FAMILY,
        example='allWords(["a b", "c"]) is ["a", "b", "c"]',
        hint=(
            "flatMap is map followed by a one-level flat, so each line can "
            "return its own array of words."
        ),
        cases=(
            (["a b", "c"],), ([],), ([""],), (["one"],),
            (["  spaced  out "],), (["hi", "there you"],), (["", "x", ""],),
            (["a  b", "c d e"],), (["same", "same"],), ([" "],),
        ),
        solve=_all_words,
        checks=(
            ((["a b", "c"],), ["a", "b", "c"]), (([],), []), (([""],), []),
            ((["  spaced  out "],), ["spaced", "out"]),
            ((["", "x", ""],), ["x"]),
        ),
        js_answer=(
            "function allWords(lines) {\n"
            '  return lines.flatMap((line) => line.split(" ").filter((w) => w !== ""));\n'
            "}"
        ),
    ),
    Kata(
        id="js-missing-from",
        level=2,
        language="javascript",
        name="missingFrom",
        brief=(
            "Return the items of `wanted` that are not in `have`, in the "
            "order they are wanted."
        ),
        params=("wanted", "have"),
        family=FAMILY,
        example="missingFrom([1, 2, 3], [2]) is [1, 3]",
        hint=(
            "Put `have` in a Set once; then has() is a quick question "
            "instead of a search through the array every time."
        ),
        cases=(
            ([1, 2, 3], [2]), ([], [1]), ([1], []), ([1, 2], [1, 2]),
            (["a", "b", "c"], ["c", "a"]), ([-1, 0, 1], [0]), ([5, 5, 6], [6]),
            ([1, 2], []), (["x"], ["x"]), ([3, 4, 5], [9]),
        ),
        solve=_missing_from,
        checks=(
            (([1, 2, 3], [2]), [1, 3]), (([], [1]), []), (([1], []), [1]),
            (([1, 2], [1, 2]), []), (([5, 5, 6], [6]), [5, 5]),
        ),
        js_answer=(
            "function missingFrom(wanted, have) {\n"
            "  const got = new Set(have);\n"
            "  return wanted.filter((x) => !got.has(x));\n"
            "}"
        ),
    ),
    Kata(
        id="js-invert-object",
        level=3,
        language="javascript",
        name="invertObject",
        brief=(
            "Swap the keys and values of an object whose values are "
            "strings. When two keys share a value, the later key wins."
        ),
        params=("record",),
        family=FAMILY,
        example='invertObject({ a: "x", b: "y" }) is { x: "a", y: "b" }',
        hint=(
            "Object.entries gives [key, value] pairs, map can swap each "
            "pair, and Object.fromEntries turns pairs back into an object."
        ),
        cases=(
            ({"a": "x", "b": "y"},), ({},), ({"a": "x"},),
            ({"a": "x", "b": "x"},), ({"red": "stop", "green": "go"},),
            ({"k": "v", "v": "k"},), ({"one": "uno", "two": "dos", "three": "tres"},),
            ({"a": ""},), ({"x": "a", "y": "b", "z": "a"},), ({"cat": "dog"},),
        ),
        solve=_invert_object,
        checks=(
            (({"a": "x", "b": "y"},), {"x": "a", "y": "b"}), (({},), {}),
            (({"a": "x"},), {"x": "a"}), (({"a": "x", "b": "x"},), {"x": "b"}),
        ),
        js_answer=(
            "function invertObject(record) {\n"
            "  return Object.fromEntries(\n"
            "    Object.entries(record).map(([key, value]) => [value, key]),\n"
            "  );\n"
            "}"
        ),
    ),
    Kata(
        id="js-totals-by",
        level=3,
        language="javascript",
        name="totalsBy",
        brief=(
            "Each order is { name, amount }. Return an object of the total "
            "amount per name, names in the order first seen. Refunds are "
            "negative amounts."
        ),
        params=("orders",),
        family=FAMILY,
        example=(
            'totalsBy([{ name: "ann", amount: 5 }, { name: "ann", amount: 2 }]) '
            "is { ann: 7 }"
        ),
        hint=(
            "reduce with {} as the starting value; the accumulator is the "
            "object you are building, and it has to be returned each time."
        ),
        cases=(
            ([{"name": "ann", "amount": 5}, {"name": "ann", "amount": 2}],),
            ([],),
            ([{"name": "bo", "amount": 3}],),
            ([{"name": "ann", "amount": 5}, {"name": "bo", "amount": 1}],),
            ([{"name": "ann", "amount": 5}, {"name": "ann", "amount": -5}],),
            ([{"name": "cy", "amount": 0}],),
            ([{"name": "b", "amount": 1}, {"name": "a", "amount": 2},
              {"name": "b", "amount": 3}],),
            ([{"name": "ann", "amount": -4}],),
            ([{"name": "x", "amount": 10}, {"name": "y", "amount": 20},
              {"name": "x", "amount": 30}, {"name": "y", "amount": 40}],),
            ([{"name": "solo", "amount": 99}],),
        ),
        solve=_totals_by,
        checks=(
            (([{"name": "ann", "amount": 5}, {"name": "ann", "amount": 2}],),
             {"ann": 7}),
            (([],), {}),
            (([{"name": "ann", "amount": 5}, {"name": "ann", "amount": -5}],),
             {"ann": 0}),
            (([{"name": "b", "amount": 1}, {"name": "a", "amount": 2},
               {"name": "b", "amount": 3}],), {"b": 4, "a": 2}),
        ),
        js_answer=(
            "function totalsBy(orders) {\n"
            "  return orders.reduce((totals, { name, amount }) => {\n"
            "    totals[name] = (totals[name] ?? 0) + amount;\n"
            "    return totals;\n"
            "  }, {});\n"
            "}"
        ),
    ),
    Kata(
        id="js-order-line",
        level=4,
        language="javascript",
        name="orderLine",
        brief=(
            "An item is { name, cents } with an optional qty that means 1 "
            "when missing. Return \"qty x name @ price = total\", money as "
            "$D.CC and a minus sign in front for a negative amount."
        ),
        params=("item",),
        family=FAMILY,
        example='orderLine({ name: "tea", cents: 150, qty: 2 }) is "2 x tea @ $1.50 = $3.00"',
        hint=(
            "const { name, cents, qty = 1 } = item; then work in whole "
            "cents and only divide by 100 for toFixed(2) at the end, with "
            "the sign kept outside the dollar sign."
        ),
        cases=(
            ({"name": "tea", "cents": 150, "qty": 2},),
            ({"name": "bun", "cents": 95},),
            ({"name": "free", "cents": 0},),
            ({"name": "refund", "cents": -250},),
            ({"name": "pen", "cents": 5, "qty": 3},),
            ({"name": "box", "cents": 1000, "qty": 0},),
            ({"name": "cake", "cents": 12345},),
            ({"name": "cup", "cents": 1, "qty": 1},),
            ({"name": "back", "cents": -99, "qty": 2},),
            ({"name": "jam", "cents": 333, "qty": 3},),
        ),
        solve=_order_line,
        checks=(
            (({"name": "tea", "cents": 150, "qty": 2},), "2 x tea @ $1.50 = $3.00"),
            (({"name": "bun", "cents": 95},), "1 x bun @ $0.95 = $0.95"),
            (({"name": "refund", "cents": -250},), "1 x refund @ -$2.50 = -$2.50"),
            (({"name": "box", "cents": 1000, "qty": 0},), "0 x box @ $10.00 = $0.00"),
            (({"name": "back", "cents": -99, "qty": 2},), "2 x back @ -$0.99 = -$1.98"),
        ),
        js_answer=(
            "function orderLine(item) {\n"
            "  const { name, cents, qty = 1 } = item;\n"
            "  const money = (c) => `${c < 0 ? \"-\" : \"\"}$${(Math.abs(c) / 100).toFixed(2)}`;\n"
            "  return `${qty} x ${name} @ ${money(cents)} = ${money(cents * qty)}`;\n"
            "}"
        ),
    ),
)
