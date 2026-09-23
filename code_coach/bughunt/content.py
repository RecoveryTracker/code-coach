"""The hunts themselves.

Each program is written the way the real thing would be - helpers,
constants, a function that calls another - because a bug in a
four-line function has nowhere to hide and locating it teaches nothing.

Several put the symptom and the cause in different places on purpose:
the last page is wrong but the counting is what broke, the most common
word is wrong but the words were read in wrong. Following a wrong value
back to where it was made is the skill.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

PYTHON = "Python"
JAVASCRIPT = "JavaScript"


# ── Python ───────────────────────────────────────────────────


def _order_total(prices: list) -> int:
    total = sum(prices)
    return total + (0 if total >= 100 else 7)


def _average(scores: list):
    if not scores:
        return 0
    return sum(scores) / len(scores)


def _most_common(text: str) -> str:
    counts: dict[str, int] = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    if not counts:
        return ""
    return max(counts, key=counts.get)


def _last_page(items: list) -> list:
    if not items:
        return []
    pages = (len(items) + 2) // 3
    start = (pages - 1) * 3
    return items[start:start + 3]


PYTHON_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-free-shipping",
        title="Free shipping from 100",
        family=PYTHON,
        language="python",
        level=1,
        report="A customer spent exactly 100 and was still charged 7 for "
               "shipping. The site says shipping is free from 100.",
        name="order_total",
        params=("prices",),
        start=(
            "FREE_SHIPPING_FROM = 100\n"
            "SHIPPING = 7\n"
            "\n"
            "\n"
            "def subtotal(prices):\n"
            "    return sum(prices)\n"
            "\n"
            "\n"
            "def shipping_for(total):\n"
            "    if total > FREE_SHIPPING_FROM:\n"
            "        return 0\n"
            "    return SHIPPING\n"
            "\n"
            "\n"
            "def order_total(prices):\n"
            "    total = subtotal(prices)\n"
            "    return total + shipping_for(total)\n"
        ),
        fixed=(
            "FREE_SHIPPING_FROM = 100\n"
            "SHIPPING = 7\n"
            "\n"
            "\n"
            "def subtotal(prices):\n"
            "    return sum(prices)\n"
            "\n"
            "\n"
            "def shipping_for(total):\n"
            "    if total >= FREE_SHIPPING_FROM:\n"
            "        return 0\n"
            "    return SHIPPING\n"
            "\n"
            "\n"
            "def order_total(prices):\n"
            "    total = subtotal(prices)\n"
            "    return total + shipping_for(total)\n"
        ),
        solve=_order_total,
        reported=([100],),
        cases=(([],), ([50],), ([100],), ([60, 40],), ([150],), ([99],)),
        cause="Free shipping should start at 100, but the test only lets "
              "totals above 100 through.",
        decoys=(
            "subtotal adds the prices up wrong.",
            "SHIPPING is set to the wrong amount.",
            "order_total adds the shipping to the wrong total.",
        ),
        lesson="Boundaries are where bugs live. When a report names an "
               "exact number, check first whether the code says > where "
               "it means >=.",
        hint="Try the exact amount the customer spent: order_total([100]).",
        checks=((([100],), 100), (([],), 7), (([99],), 106)),
    ),
    Hunt(
        id="hunt-class-average",
        title="The class average",
        family=PYTHON,
        language="python",
        level=1,
        report="The class average is wrong. Three students scored 90, 80 "
               "and 70, and the average came out as 50 instead of 80.",
        name="average",
        params=("scores",),
        start=(
            "def total_of(scores):\n"
            "    total = 0\n"
            "    for i in range(1, len(scores)):\n"
            "        total += scores[i]\n"
            "    return total\n"
            "\n"
            "\n"
            "def average(scores):\n"
            "    if not scores:\n"
            "        return 0\n"
            "    return total_of(scores) / len(scores)\n"
        ),
        fixed=(
            "def total_of(scores):\n"
            "    total = 0\n"
            "    for i in range(len(scores)):\n"
            "        total += scores[i]\n"
            "    return total\n"
            "\n"
            "\n"
            "def average(scores):\n"
            "    if not scores:\n"
            "        return 0\n"
            "    return total_of(scores) / len(scores)\n"
        ),
        solve=_average,
        reported=([90, 80, 70],),
        cases=(([],), ([90, 80, 70],), ([100],), ([0, 50],),
               ([10, 10, 10, 10],)),
        cause="The loop starts at index 1, so the first score is never "
              "added.",
        decoys=(
            "Dividing by len(scores) counts one student too many.",
            "The empty-list check returns before the loop can run.",
            "Adding with += loses the decimals.",
        ),
        lesson="When a total is too low, find where it starts counting. A "
               "range that starts at 1 is the commonest way to lose the "
               "first item.",
        hint="Use the scores from the report: average([90, 80, 70]).",
        checks=((([90, 80, 70],), 80.0), (([],), 0), (([0, 50],), 25.0)),
    ),
    Hunt(
        id="hunt-common-word",
        title="The most common word",
        family=PYTHON,
        language="python",
        level=2,
        report="In 'The dog and the cat and the bird', 'the' appears three "
               "times, so it should be the most common word. Our tool "
               "says 'and'.",
        name="most_common",
        params=("text",),
        start=(
            "def words_in(text):\n"
            "    return text.split()\n"
            "\n"
            "\n"
            "def count_words(text):\n"
            "    counts = {}\n"
            "    for word in words_in(text):\n"
            "        counts[word] = counts.get(word, 0) + 1\n"
            "    return counts\n"
            "\n"
            "\n"
            "def most_common(text):\n"
            "    counts = count_words(text)\n"
            "    if not counts:\n"
            "        return \"\"\n"
            "    return max(counts, key=counts.get)\n"
        ),
        fixed=(
            "def words_in(text):\n"
            "    return text.lower().split()\n"
            "\n"
            "\n"
            "def count_words(text):\n"
            "    counts = {}\n"
            "    for word in words_in(text):\n"
            "        counts[word] = counts.get(word, 0) + 1\n"
            "    return counts\n"
            "\n"
            "\n"
            "def most_common(text):\n"
            "    counts = count_words(text)\n"
            "    if not counts:\n"
            "        return \"\"\n"
            "    return max(counts, key=counts.get)\n"
        ),
        solve=_most_common,
        reported=("The dog and the cat and the bird",),
        cases=(("",), ("a b a",), ("The dog and the cat and the bird",),
               ("Go go GO",), ("one",)),
        cause="Words are counted exactly as typed, so 'The' and 'the' are "
              "counted as two different words.",
        decoys=(
            "max picks the wrong word when two are tied.",
            "split() cuts the text in the wrong places.",
            "counts.get starts each new word at the wrong number.",
        ),
        lesson="When two things that should be equal are counted apart, "
               "look at where the data comes in. One lower() at the source "
               "fixes every place that uses it.",
        hint="Use the sentence from the report, and count 'the' yourself.",
        checks=((("The dog and the cat and the bird",), "the"), (("",), ""),
                (("Go go GO",), "go")),
    ),
    Hunt(
        id="hunt-last-page",
        title="The missing last result",
        family=PYTHON,
        language="python",
        level=3,
        report="With 7 results the last page shows results 4, 5 and 6. "
               "Result 7 is never shown anywhere.",
        name="last_page",
        params=("items",),
        start=(
            "PAGE_SIZE = 3\n"
            "\n"
            "\n"
            "def page_count(items):\n"
            "    return len(items) // PAGE_SIZE\n"
            "\n"
            "\n"
            "def page(items, number):\n"
            "    start = (number - 1) * PAGE_SIZE\n"
            "    return items[start:start + PAGE_SIZE]\n"
            "\n"
            "\n"
            "def last_page(items):\n"
            "    if not items:\n"
            "        return []\n"
            "    return page(items, page_count(items))\n"
        ),
        fixed=(
            "PAGE_SIZE = 3\n"
            "\n"
            "\n"
            "def page_count(items):\n"
            "    return (len(items) + PAGE_SIZE - 1) // PAGE_SIZE\n"
            "\n"
            "\n"
            "def page(items, number):\n"
            "    start = (number - 1) * PAGE_SIZE\n"
            "    return items[start:start + PAGE_SIZE]\n"
            "\n"
            "\n"
            "def last_page(items):\n"
            "    if not items:\n"
            "        return []\n"
            "    return page(items, page_count(items))\n"
        ),
        solve=_last_page,
        reported=([1, 2, 3, 4, 5, 6, 7],),
        cases=(([],), ([1, 2, 3],), ([1, 2, 3, 4, 5, 6],),
               ([1, 2, 3, 4, 5, 6, 7],), ([1, 2],),
               ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10],)),
        cause="page_count rounds down, so a last page that is only partly "
              "full is never counted.",
        decoys=(
            "page() starts each page one item too late.",
            "PAGE_SIZE should be 4.",
            "last_page asks for the wrong page number.",
        ),
        lesson="The bug showed up in last_page, but it lived in page_count. "
               "Following a wrong value back to where it was worked out is "
               "most of debugging.",
        hint="Seven results, as in the report: last_page([1, 2, 3, 4, 5, 6, 7]). "
             "Then try six.",
        checks=((([1, 2, 3, 4, 5, 6, 7],), [7]), (([],), []),
                (([1, 2],), [1, 2])),
    ),
)


# ── JavaScript ───────────────────────────────────────────────


def _label(day: int) -> str:
    return "weekend" if day in (0, 6) else "weekday"


def _item_count(quantities: list) -> int:
    return sum(int(text.strip()) for text in quantities)


def _safe_for(ingredients: list, allergies: list) -> bool:
    return not any(allergy in ingredients for allergy in allergies)


def _final_price(price, is_member: bool):
    discount = price * 10 / 100 if is_member else 0
    return round(price - discount, 2)


JAVASCRIPT_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-js-weekend",
        title="Sunday is a weekday",
        family=JAVASCRIPT,
        language="javascript",
        level=1,
        report="Sunday - day 0 - shows up as a weekday. Saturday is fine.",
        name="label",
        params=("day",),
        start=(
            "const SATURDAY = 6;\n"
            "const SUNDAY = 7;\n"
            "\n"
            "function isWeekend(day) {\n"
            "  return day === SATURDAY || day === SUNDAY;\n"
            "}\n"
            "\n"
            "function label(day) {\n"
            "  return isWeekend(day) ? \"weekend\" : \"weekday\";\n"
            "}\n"
        ),
        fixed=(
            "const SATURDAY = 6;\n"
            "const SUNDAY = 0;\n"
            "\n"
            "function isWeekend(day) {\n"
            "  return day === SATURDAY || day === SUNDAY;\n"
            "}\n"
            "\n"
            "function label(day) {\n"
            "  return isWeekend(day) ? \"weekend\" : \"weekday\";\n"
            "}\n"
        ),
        solve=_label,
        reported=(0,),
        cases=((0,), (1,), (3,), (5,), (6,)),
        cause="SUNDAY is set to 7, but the days are numbered 0 to 6 and "
              "Sunday is 0.",
        decoys=(
            "=== is too strict and should be ==.",
            "The || should be &&.",
            "label has weekend and weekday the wrong way round.",
        ),
        lesson="When a comparison looks right and still fails, check the "
               "values it compares against. A wrong constant fails quietly "
               "everywhere it is used.",
        hint="The report names the day: label(0).",
        checks=(((0,), "weekend"), ((6,), "weekend"), ((1,), "weekday")),
    ),
    Hunt(
        id="hunt-js-item-count",
        title="023 items in the cart",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="Ordering 2 of one thing and 3 of another shows '023 items' "
               "in the cart instead of 5.",
        name="itemCount",
        params=("quantities",),
        start=(
            "function parseQuantity(text) {\n"
            "  return text.trim();\n"
            "}\n"
            "\n"
            "function itemCount(quantities) {\n"
            "  let count = 0;\n"
            "  for (const text of quantities) {\n"
            "    count += parseQuantity(text);\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        fixed=(
            "function parseQuantity(text) {\n"
            "  return Number(text.trim());\n"
            "}\n"
            "\n"
            "function itemCount(quantities) {\n"
            "  let count = 0;\n"
            "  for (const text of quantities) {\n"
            "    count += parseQuantity(text);\n"
            "  }\n"
            "  return count;\n"
            "}\n"
        ),
        solve=_item_count,
        reported=(["2", "3"],),
        cases=(([],), (["2", "3"],), ([" 4 "],), (["1", "1", "1"],)),
        cause="The quantities are text, so += joins them together as "
              "strings instead of adding them as numbers.",
        decoys=(
            "trim() removes the digits along with the spaces.",
            "count should start at 1, not 0.",
            "The loop visits each quantity twice.",
        ),
        lesson="Anything that came from a form is text until you make it a "
               "number. A sum that looks like numbers glued together is "
               "exactly that.",
        hint="The quantities come from a form, so they are text: "
             "itemCount([\"2\", \"3\"]).",
        checks=(((["2", "3"],), 5), (([],), 0), (([" 4 "],), 4)),
    ),
    Hunt(
        id="hunt-js-allergens",
        title="Marked safe with nuts in it",
        family=JAVASCRIPT,
        language="javascript",
        level=2,
        report="A recipe of flour, sugar and nuts was marked safe for "
               "someone allergic to nuts.",
        name="safeFor",
        params=("ingredients", "allergies"),
        start=(
            "function hasAllergen(ingredients, allergen) {\n"
            "  for (const item of ingredients) {\n"
            "    return item === allergen;\n"
            "  }\n"
            "  return false;\n"
            "}\n"
            "\n"
            "function safeFor(ingredients, allergies) {\n"
            "  return allergies.every((allergy) => !hasAllergen(ingredients, allergy));\n"
            "}\n"
        ),
        fixed=(
            "function hasAllergen(ingredients, allergen) {\n"
            "  for (const item of ingredients) {\n"
            "    if (item === allergen) return true;\n"
            "  }\n"
            "  return false;\n"
            "}\n"
            "\n"
            "function safeFor(ingredients, allergies) {\n"
            "  return allergies.every((allergy) => !hasAllergen(ingredients, allergy));\n"
            "}\n"
        ),
        solve=_safe_for,
        reported=(["flour", "sugar", "nuts"], ["nuts"]),
        cases=(([], ["nuts"]), (["nuts"], ["nuts"]),
               (["flour", "sugar", "nuts"], ["nuts"]), (["flour"], ["nuts"]),
               (["nuts", "flour"], ["nuts"]), (["flour"], [])),
        cause="hasAllergen returns after looking at the first ingredient, "
              "so anything later in the list is never checked.",
        decoys=(
            "every() should be some().",
            "=== fails because the words have different capitals.",
            "An empty ingredient list should count as unsafe.",
        ),
        lesson="A return inside a loop ends the whole function, not just "
               "that turn of the loop. If a search only ever finds things "
               "at the front of a list, look for one.",
        hint="Try the recipe from the report, then the same ingredients "
             "with nuts first.",
        checks=(((["flour", "sugar", "nuts"], ["nuts"]), False),
                ((["nuts"], ["nuts"]), False), (([], ["nuts"]), True)),
    ),
    Hunt(
        id="hunt-js-member-price",
        title="Members pay -180",
        family=JAVASCRIPT,
        language="javascript",
        level=3,
        report="Members are being charged a negative amount: a 20 dollar "
               "item comes out at -180. Non-members are fine.",
        name="finalPrice",
        params=("price", "isMember"),
        start=(
            "const MEMBER_DISCOUNT_PERCENT = 10;\n"
            "\n"
            "function roundCents(amount) {\n"
            "  return Math.round(amount * 100) / 100;\n"
            "}\n"
            "\n"
            "function discountFor(price, isMember) {\n"
            "  if (!isMember) return 0;\n"
            "  return price * MEMBER_DISCOUNT_PERCENT;\n"
            "}\n"
            "\n"
            "function finalPrice(price, isMember) {\n"
            "  return roundCents(price - discountFor(price, isMember));\n"
            "}\n"
        ),
        fixed=(
            "const MEMBER_DISCOUNT_PERCENT = 10;\n"
            "\n"
            "function roundCents(amount) {\n"
            "  return Math.round(amount * 100) / 100;\n"
            "}\n"
            "\n"
            "function discountFor(price, isMember) {\n"
            "  if (!isMember) return 0;\n"
            "  return price * MEMBER_DISCOUNT_PERCENT / 100;\n"
            "}\n"
            "\n"
            "function finalPrice(price, isMember) {\n"
            "  return roundCents(price - discountFor(price, isMember));\n"
            "}\n"
        ),
        solve=_final_price,
        reported=(20, True),
        cases=((20, True), (20, False), (19.99, True), (0, True), (50, True)),
        cause="The discount multiplies by 10 instead of taking 10 percent - "
              "nothing ever divides by 100.",
        decoys=(
            "roundCents rounds to the wrong number of places.",
            "isMember is checked the wrong way round.",
            "The discount is subtracted when it should be added.",
        ),
        lesson="A number that is wildly wrong - negative, or ten times too "
               "big - usually means a unit is wrong rather than the logic. "
               "A percent needs dividing by 100 somewhere.",
        hint="The report's item: finalPrice(20, true). What should a 10% "
             "discount on 20 be?",
        checks=(((20, True), 18), ((0, True), 0), ((20, False), 20)),
    ),
)
