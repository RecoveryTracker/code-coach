"""TypeScript hunts: bugs the type checker lets through.

Every program here passes `tsc --strict`, which is the point. Types catch a
whole class of mistakes, and these are the ones they cannot: an `as` that
vouches for data it never checked, `||` treating a real 0 as missing, an
enum whose first value is falsy, object keys that are strings whatever the
type says, `includes` comparing objects by identity, and `map(parseInt)`
handing parseInt an index it reads as a radix.

The same rules hold as for every hunt, checked by tests/test_bughunt_ts.py:
the bug is real, it hides on some inputs, the report's own input shows it,
and the fix changes one or two lines in place.
"""

from __future__ import annotations

import json

from code_coach.bughunt import Hunt

TS = "TypeScript"


def _total_text(text: str) -> int:
    return sum(int(x) for x in json.loads(text))


def _price_after(price: int, discount):
    pct = 10 if discount is None else discount
    return price - price * pct // 100


def _labels(levels: list) -> list:
    names = {0: "low", 1: "high"}
    return [names.get(level, "unset") for level in levels]


def _next_ids(stock: dict) -> list:
    return [int(k) + 1 for k in stock]


def _picked_count(items: list, ids: list) -> int:
    return sum(1 for item in items if item["id"] in ids)


def _parse_all(texts: list) -> list:
    return [int(t) if t.strip().lstrip("-").isdigit() else None for t in texts]


TS_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-ts-or-zero-discount",
        title="A 0% discount takes 10% off",
        family=TS,
        language="typescript",
        level=1,
        report="Products with no discount set should get the standard 10% off, "
               "and they do. But a product marked with a discount of 0 also "
               "comes out 10% cheaper.",
        name="priceAfter",
        params=("price", "discount"),
        start=(
            "const STANDARD = 10;\n"
            "\n"
            "function percentOff(discount: number | null): number {\n"
            "  return discount || STANDARD;\n"
            "}\n"
            "\n"
            "function priceAfter(price: number, discount: number | null): number {\n"
            "  return price - Math.floor((price * percentOff(discount)) / 100);\n"
            "}\n"
        ),
        fixed=(
            "const STANDARD = 10;\n"
            "\n"
            "function percentOff(discount: number | null): number {\n"
            "  return discount ?? STANDARD;\n"
            "}\n"
            "\n"
            "function priceAfter(price: number, discount: number | null): number {\n"
            "  return price - Math.floor((price * percentOff(discount)) / 100);\n"
            "}\n"
        ),
        solve=_price_after,
        reported=(200, 0),
        cases=((200, None), (200, 25), (200, 0), (50, 50), (90, 0)),
        cause="`||` falls back on any falsy value, and 0 is falsy, so a real "
              "discount of 0 is replaced by the standard 10.",
        decoys=(
            "Math.floor rounds the 0% discount up to 10%.",
            "null and 0 are the same value in TypeScript.",
            "STANDARD is applied to every product before the discount is read.",
        ),
        lesson="The type `number | null` is right and tsc is happy - the bug is "
               "in what `||` means. Use `??` when only null or undefined should "
               "fall back: it keeps 0, '' and false.",
        hint="Give a product an explicit discount of 0: priceAfter(200, 0).",
        checks=(((200, 0), 200), ((200, None), 180), ((200, 25), 150)),
    ),
    Hunt(
        id="hunt-ts-as-strings",
        title="5 plus 10 is 0510",
        family=TS,
        language="typescript",
        level=2,
        report="The basket total for '[\"5\", \"10\"]' comes out as 0510. When the "
               "prices arrive as plain numbers, '[5, 10]', it says 15.",
        name="totalText",
        params=("text",),
        start=(
            "function readPrices(text: string): number[] {\n"
            "  return JSON.parse(text) as number[];\n"
            "}\n"
            "\n"
            "function totalText(text: string): number {\n"
            "  const prices = readPrices(text);\n"
            "  return prices.reduce((sum, p) => sum + p, 0);\n"
            "}\n"
        ),
        fixed=(
            "function readPrices(text: string): number[] {\n"
            "  return (JSON.parse(text) as unknown[]).map(Number);\n"
            "}\n"
            "\n"
            "function totalText(text: string): number {\n"
            "  const prices = readPrices(text);\n"
            "  return prices.reduce((sum, p) => sum + p, 0);\n"
            "}\n"
        ),
        solve=_total_text,
        reported=('["5", "10"]',),
        cases=(("[]",), ("[5, 10]",), ('["5", "10"]',), ("[1, 2, 3]",), ('["7"]',)),
        cause="`as number[]` tells the compiler the parsed values are numbers "
              "without checking. They are strings, so + joins them as text.",
        decoys=(
            "reduce starts at 0, which is put in front of the total as a digit.",
            "JSON.parse cannot read numbers that are written in quotes.",
            "The prices are added in the wrong order.",
        ),
        lesson="`as` is a promise you make to the compiler, not a conversion. "
               "Data from outside - JSON, a form, a file - should be checked or "
               "converted (Number, parseInt, a schema) before it is trusted.",
        hint="Send the prices as strings: totalText('[\"5\", \"10\"]').",
        checks=((('["5", "10"]',), 15), (("[5, 10]",), 15), (("[]",), 0)),
    ),
    Hunt(
        id="hunt-ts-enum-falsy",
        title="Low priority shows as unset",
        family=TS,
        language="typescript",
        level=2,
        report="Tasks marked Low priority are labelled 'unset'. High priority "
               "tasks are labelled correctly.",
        name="labels",
        params=("levels",),
        start=(
            "enum Priority { Low, High }\n"
            "const NAMES: Record<Priority, string> = { [Priority.Low]: \"low\", [Priority.High]: \"high\" };\n"
            "\n"
            "function label(level: Priority | null): string {\n"
            "  if (!level) return \"unset\";\n"
            "  return NAMES[level];\n"
            "}\n"
            "\n"
            "function labels(levels: (Priority | null)[]): string[] {\n"
            "  return levels.map((level) => label(level));\n"
            "}\n"
        ),
        fixed=(
            "enum Priority { Low, High }\n"
            "const NAMES: Record<Priority, string> = { [Priority.Low]: \"low\", [Priority.High]: \"high\" };\n"
            "\n"
            "function label(level: Priority | null): string {\n"
            "  if (level === null) return \"unset\";\n"
            "  return NAMES[level];\n"
            "}\n"
            "\n"
            "function labels(levels: (Priority | null)[]): string[] {\n"
            "  return levels.map((level) => label(level));\n"
            "}\n"
        ),
        solve=_labels,
        reported=([0],),
        cases=(([],), ([1],), ([None],), ([0],), ([1, 0, None],)),
        cause="Priority.Low is the number 0, and `!level` is true for 0, so a "
              "Low task is treated as having no priority at all.",
        decoys=(
            "The enum starts counting at 1, so Low has no value.",
            "map passes the index as a second argument and label reads it.",
            "=== cannot compare an enum value with a number.",
        ),
        lesson="A numeric enum's first member is 0 unless you say otherwise, "
               "and 0 is falsy. Test for the missing case itself (`=== null`), "
               "or start the enum at 1 if 0 should never be a real value.",
        hint="Ask for the label of a Low task: labels([0]).",
        checks=((([0],), ["low"]), (([None],), ["unset"]), (([1, 0, None],), ["high", "low", "unset"])),
    ),
    Hunt(
        id="hunt-ts-string-keys",
        title="The next id after 1 is 11",
        family=TS,
        language="typescript",
        level=3,
        report="For each product id in stock, we work out the id that comes "
               "after it. After id 1 it says 11, and after 9 it says 91.",
        name="nextIds",
        params=("stock",),
        start=(
            "type Stock = Record<number, number>;\n"
            "\n"
            "function ids(stock: Stock): string[] {\n"
            "  return Object.keys(stock);\n"
            "}\n"
            "\n"
            "function nextIds(stock: Stock): (string | number)[] {\n"
            "  return ids(stock).map((id) => id + 1);\n"
            "}\n"
        ),
        fixed=(
            "type Stock = Record<number, number>;\n"
            "\n"
            "function ids(stock: Stock): string[] {\n"
            "  return Object.keys(stock);\n"
            "}\n"
            "\n"
            "function nextIds(stock: Stock): (string | number)[] {\n"
            "  return ids(stock).map((id) => Number(id) + 1);\n"
            "}\n"
        ),
        solve=_next_ids,
        reported=({"1": 5},),
        cases=(({},), ({"1": 5},), ({"9": 2, "20": 1},)),
        cause="Object.keys always returns strings, even for a Record<number, ...>, "
              "so id + 1 joins '1' and 1 into '11'.",
        decoys=(
            "Record<number, number> sorts the ids as text.",
            "map runs the arrow function twice for each id.",
            "The stock count is being added to the id instead of 1.",
        ),
        lesson="An object's keys are strings at runtime, whatever the Record "
               "type says, and Object.keys is honest about it: string[]. "
               "Convert with Number() - or keep number keys in a Map.",
        hint="One product with id 1: nextIds({\"1\": 5}).",
        checks=((({"1": 5},), [2]), (({},), []), (({"9": 2, "20": 1},), [10, 21])),
    ),
    Hunt(
        id="hunt-ts-includes-objects",
        title="Nothing I picked counts",
        family=TS,
        language="typescript",
        level=3,
        report="I pick items by id and the app says I picked 0, however many "
               "I choose. Picking nothing correctly says 0.",
        name="pickedCount",
        params=("items", "ids"),
        start=(
            "type Item = { id: number; name: string };\n"
            "\n"
            "function picked(items: Item[], ids: number[]): Item[] {\n"
            "  const wanted = ids.map((id) => ({ id }));\n"
            "  return items.filter((item) => wanted.includes({ id: item.id }));\n"
            "}\n"
            "\n"
            "function pickedCount(items: Item[], ids: number[]): number {\n"
            "  return picked(items, ids).length;\n"
            "}\n"
        ),
        fixed=(
            "type Item = { id: number; name: string };\n"
            "\n"
            "function picked(items: Item[], ids: number[]): Item[] {\n"
            "  const wanted = ids.map((id) => ({ id }));\n"
            "  return items.filter((item) => wanted.some((w) => w.id === item.id));\n"
            "}\n"
            "\n"
            "function pickedCount(items: Item[], ids: number[]): number {\n"
            "  return picked(items, ids).length;\n"
            "}\n"
        ),
        solve=_picked_count,
        reported=([{"id": 1, "name": "tea"}], [1]),
        cases=(([], [1]), ([{"id": 1, "name": "tea"}], []), ([{"id": 1, "name": "tea"}], [1]),
               ([{"id": 1, "name": "tea"}, {"id": 2, "name": "jam"}], [2, 3])),
        cause="includes compares objects by identity, and `{ id: item.id }` is a "
              "brand-new object each time, so it is never the same object as "
              "any in wanted.",
        decoys=(
            "filter keeps the items that do NOT match.",
            "The ids are numbers but the items store them as strings.",
            "picked returns before filter has finished.",
        ),
        lesson="Two objects with the same contents are still two objects: "
               "=== and includes compare which object, not what is inside. "
               "Compare a field with some(), or keep plain values (a Set of ids).",
        hint="Pick the only item there is: pickedCount([{\"id\": 1, \"name\": \"tea\"}], [1]).",
        checks=((([{"id": 1, "name": "tea"}], [1]), 1), (([], [1]), 0),
                (([{"id": 1, "name": "tea"}, {"id": 2, "name": "jam"}], [2, 3]), 1)),
    ),
    Hunt(
        id="hunt-ts-map-parseint",
        title="Only the first number reads",
        family=TS,
        language="typescript",
        level=4,
        report="Turning '1', '2' and '3' into numbers gives 1, then null, then "
               "null. A single value always works.",
        name="parseAll",
        params=("texts",),
        start=(
            "function toNumber(n: number): number | null {\n"
            "  return Number.isNaN(n) ? null : n;\n"
            "}\n"
            "\n"
            "function parseAll(texts: string[]): (number | null)[] {\n"
            "  const raw = texts.map(parseInt);\n"
            "  return raw.map(toNumber);\n"
            "}\n"
        ),
        fixed=(
            "function toNumber(n: number): number | null {\n"
            "  return Number.isNaN(n) ? null : n;\n"
            "}\n"
            "\n"
            "function parseAll(texts: string[]): (number | null)[] {\n"
            "  const raw = texts.map((t) => parseInt(t, 10));\n"
            "  return raw.map(toNumber);\n"
            "}\n"
        ),
        solve=_parse_all,
        reported=(["1", "2", "3"],),
        cases=(([],), (["7"],), (["1", "2", "3"],), (["10", "x"],)),
        cause="map calls parseInt with each item AND its index, and parseInt "
              "reads the index as the radix: '2' in base 1 and '3' in base 2 are "
              "not numbers.",
        decoys=(
            "parseInt cannot read a string with only one digit.",
            "toNumber turns every number after the first into null.",
            "map skips every other item when it is given a function by name.",
        ),
        lesson="map passes (item, index, array), and a function that takes a "
               "second argument will use it. parseInt(string, radix) fits the "
               "callback type, so tsc cannot object. Wrap it: map((t) => "
               "parseInt(t, 10)), or use map(Number).",
        hint="Parse more than one: parseAll([\"1\", \"2\", \"3\"]).",
        checks=(((["1", "2", "3"],), [1, 2, 3]), ((["7"],), [7]), ((["10", "x"],), [10, None])),
    ),
)
