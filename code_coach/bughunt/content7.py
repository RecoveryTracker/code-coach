"""A third set of Python hunts, so Python has as many to practise on as
JavaScript does, each a kind of bug the first sixteen do not cover:

  `or` taking 0 for "missing"; `in` on a string finding part of a word;
  split(" ") counting the gap between two spaces as a word; removing from
  the list being looped over; round() rounding half to even; ids read as
  text looked up under number keys; sorted() putting every capital first;
  and a default list that every call shares.

The same rules hold as for the other sets, and tests/test_bughunt.py checks
them all: the bug is real, it hides on some inputs, the report's own input
shows it, and the fix changes one or two lines in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

PYTHON = "Python"


def _order_cost(items: list) -> int:
    return sum(item["price"] * (item["qty"] if "qty" in item else 1) for item in items)


def _posts_tagged(posts: list, tag: str) -> list:
    return [post["title"] for post in posts if tag in post["tags"].split(",")]


def _word_count(text: str) -> int:
    return len(text.split())


def _basket_total(ids_text: str) -> int:
    prices = {1: 250, 2: 400, 3: 125}
    return sum(prices.get(int(part), 0) for part in ids_text.split(","))


def _roster(names: list) -> list:
    return sorted((n.strip() for n in names), key=str.lower)


def _drop_refunds(amounts: list) -> list:
    return [a for a in amounts if a >= 0]


def _till_total(prices: list) -> int:
    return sum(int(p * 1.25 + 0.5) for p in prices)


def _tag_lists(words: list) -> list:
    return [[w] for w in words]


PYTHON_HUNTS_3: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-zero-quantity",
        title="Charged for cheese I removed",
        family=PYTHON,
        language="python",
        level=1,
        report="I set the cheese to 0 in my order and I'm still charged for "
               "one. Items where I left the quantity out are right - they "
               "count as one, like they should.",
        name="order_cost",
        params=("items",),
        start=(
            "def quantity(item):\n"
            "    return item.get(\"qty\") or 1\n"
            "\n"
            "\n"
            "def line_cost(item):\n"
            "    return item[\"price\"] * quantity(item)\n"
            "\n"
            "\n"
            "def order_cost(items):\n"
            "    return sum(line_cost(item) for item in items)\n"
        ),
        fixed=(
            "def quantity(item):\n"
            "    return item[\"qty\"] if \"qty\" in item else 1\n"
            "\n"
            "\n"
            "def line_cost(item):\n"
            "    return item[\"price\"] * quantity(item)\n"
            "\n"
            "\n"
            "def order_cost(items):\n"
            "    return sum(line_cost(item) for item in items)\n"
        ),
        solve=_order_cost,
        reported=([{"price": 4, "qty": 0}],),
        cases=(([],), ([{"price": 4, "qty": 2}],), ([{"price": 5}],),
               ([{"price": 4, "qty": 0}],),
               ([{"price": 4, "qty": 0}, {"price": 3, "qty": 1}],)),
        cause="`or 1` replaces every falsy quantity with 1, and 0 is falsy - "
              "so a quantity of 0 is treated as if it were missing.",
        decoys=(
            "get() returns 0 for a key that is there, so every quantity is 0.",
            "line_cost multiplies before checking the quantity.",
            "sum() skips items whose cost is 0.",
        ),
        lesson="`x or default` means 'x unless x is falsy', and 0, '', [] "
               "and None are all falsy. When 0 is a real answer, test for "
               "the thing that actually means missing.",
        hint="Order something with a quantity of 0: order_cost([{\"price\": 4, \"qty\": 0}]).",
        checks=((([{"price": 4, "qty": 0}],), 0), (([{"price": 5}],), 5),
                (([{"price": 4, "qty": 0}, {"price": 3, "qty": 1}],), 3)),
    ),
    Hunt(
        id="hunt-tag-substring",
        title="Searching java finds JavaScript",
        family=PYTHON,
        language="python",
        level=1,
        report="When I search for posts tagged java, my JavaScript posts come "
               "up too. Searching for web or for a tag nobody used is fine.",
        name="posts_tagged",
        params=("posts", "tag"),
        start=(
            "def tags_of(post):\n"
            "    return post[\"tags\"]\n"
            "\n"
            "\n"
            "def has_tag(post, tag):\n"
            "    return tag in tags_of(post)\n"
            "\n"
            "\n"
            "def posts_tagged(posts, tag):\n"
            "    return [post[\"title\"] for post in posts if has_tag(post, tag)]\n"
        ),
        fixed=(
            "def tags_of(post):\n"
            "    return post[\"tags\"].split(\",\")\n"
            "\n"
            "\n"
            "def has_tag(post, tag):\n"
            "    return tag in tags_of(post)\n"
            "\n"
            "\n"
            "def posts_tagged(posts, tag):\n"
            "    return [post[\"title\"] for post in posts if has_tag(post, tag)]\n"
        ),
        solve=_posts_tagged,
        reported=([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "java"),
        cases=(([], "java"),
               ([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "web"),
               ([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "go"),
               ([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "java"),
               ([{"title": "C", "tags": "cat,catalog"}], "cat")),
        cause="The tags are one string, and `in` on a string looks for the "
              "letters anywhere in it - so 'java' is found inside "
              "'javascript'.",
        decoys=(
            "The search ignores case, so java and Java are the same tag.",
            "posts_tagged returns every post when one of them matches.",
            "has_tag compares the tag with the post's title.",
        ),
        lesson="`in` means 'is part of' for a string but 'is one of' for a "
               "list. Split a comma-separated string into a list before "
               "asking whether something is one of its items.",
        hint="Tag one post javascript and one java, then search for java.",
        checks=((([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "java"), ["B"]),
                (([{"title": "A", "tags": "javascript,web"}, {"title": "B", "tags": "java"}], "web"), ["A"]),
                (([{"title": "C", "tags": "cat,catalog"}], "cat"), ["C"])),
    ),
    Hunt(
        id="hunt-double-space",
        title="Two spaces make three words",
        family=PYTHON,
        language="python",
        level=2,
        report="'hello  world' - with two spaces between the words - is "
               "counted as 3 words. One space between each word is always "
               "right.",
        name="word_count",
        params=("text",),
        start=(
            "def words(text):\n"
            "    return text.strip().split(\" \")\n"
            "\n"
            "\n"
            "def word_count(text):\n"
            "    cleaned = text.strip()\n"
            "    if not cleaned:\n"
            "        return 0\n"
            "    return len(words(cleaned))\n"
        ),
        fixed=(
            "def words(text):\n"
            "    return text.strip().split()\n"
            "\n"
            "\n"
            "def word_count(text):\n"
            "    cleaned = text.strip()\n"
            "    if not cleaned:\n"
            "        return 0\n"
            "    return len(words(cleaned))\n"
        ),
        solve=_word_count,
        reported=("hello  world",),
        cases=(("",), ("one",), ("a b c",), ("   ",), ("  padded  ",),
               ("hello  world",), ("a   b",)),
        cause="split(\" \") splits at every single space, so two spaces in a "
              "row leave an empty string between them, and it is counted.",
        decoys=(
            "strip() removes the spaces between the words as well as the ends.",
            "len() counts the characters rather than the words.",
            "word_count returns 0 for anything with more than one space.",
        ),
        lesson="split() with no argument splits on any run of whitespace and "
               "never hands back empty strings. split(\" \") splits on each "
               "single space, gaps and all - right for fixed formats, wrong "
               "for text people type.",
        hint="Put two spaces between two words.",
        checks=((("hello  world",), 2), (("a b c",), 3), (("",), 0)),
    ),
    Hunt(
        id="hunt-string-ids",
        title="My basket comes to 0",
        family=PYTHON,
        language="python",
        level=2,
        report="I add products 1 and 3 to my basket and the total is 0. It "
               "is 0 whatever I add.",
        name="basket_total",
        params=("ids_text",),
        start=(
            "PRICES = {1: 250, 2: 400, 3: 125}\n"
            "\n"
            "\n"
            "def price_of(product_id):\n"
            "    return PRICES.get(product_id, 0)\n"
            "\n"
            "\n"
            "def basket_total(ids_text):\n"
            "    ids = ids_text.split(\",\")\n"
            "    return sum(price_of(i) for i in ids)\n"
        ),
        fixed=(
            "PRICES = {1: 250, 2: 400, 3: 125}\n"
            "\n"
            "\n"
            "def price_of(product_id):\n"
            "    return PRICES.get(product_id, 0)\n"
            "\n"
            "\n"
            "def basket_total(ids_text):\n"
            "    ids = [int(part) for part in ids_text.split(\",\")]\n"
            "    return sum(price_of(i) for i in ids)\n"
        ),
        solve=_basket_total,
        reported=("1,3",),
        cases=(("9",), ("7,8",), ("1,3",), ("2",), ("1,1,2",)),
        cause="The ids come out of split() as text, '1' and '3', and the "
              "prices are kept under the numbers 1 and 3 - so no lookup "
              "matches and get() falls back to 0 every time.",
        decoys=(
            "sum() cannot add up the values from a generator.",
            "PRICES is defined outside the function, so price_of cannot see it.",
            "split(\",\") drops the first id in the text.",
        ),
        lesson="'1' and 1 are different keys. Anything read from text - a "
               "form, a file, a URL - is a string until you turn it into a "
               "number, and a dict will not do that for you.",
        hint="Add two real products: basket_total(\"1,3\").",
        checks=((("1,3",), 375), (("9",), 0), (("1,1,2",), 900)),
    ),
    Hunt(
        id="hunt-capitals-first",
        title="adam comes after Zed",
        family=PYTHON,
        language="python",
        level=2,
        report="The class list puts 'adam' after 'Zed'. When everyone types "
               "their name with a capital it is in the right order.",
        name="roster",
        params=("names",),
        start=(
            "def clean(name):\n"
            "    return name.strip()\n"
            "\n"
            "\n"
            "def roster(names):\n"
            "    cleaned = [clean(n) for n in names]\n"
            "    ordered = sorted(cleaned)\n"
            "    return ordered\n"
        ),
        fixed=(
            "def clean(name):\n"
            "    return name.strip()\n"
            "\n"
            "\n"
            "def roster(names):\n"
            "    cleaned = [clean(n) for n in names]\n"
            "    ordered = sorted(cleaned, key=str.lower)\n"
            "    return ordered\n"
        ),
        solve=_roster,
        reported=(["Zed", "adam"],),
        cases=(([],), (["Bea", "Al"],), ([" Cy ", "Ann"],), (["Zed", "adam"],),
               (["bo", "Al", "cara"],)),
        cause="sorted() compares letters by their code, and every capital "
              "letter comes before every small one - so Z sorts before a.",
        decoys=(
            "clean() changes the names to capitals before they are sorted.",
            "sorted() sorts the names by length first.",
            "The spaces around a name push it to the end of the list.",
        ),
        lesson="Text sorts by character code, not by the alphabet as people "
               "use it: 'Z' (90) comes before 'a' (97). Give sorted a key - "
               "key=str.lower - to sort the way a person reads.",
        hint="Mix a capital and a small first letter: roster([\"Zed\", \"adam\"]).",
        checks=(((["Zed", "adam"],), ["adam", "Zed"]), (([" Cy ", "Ann"],), ["Ann", "Cy"]),
                ((["bo", "Al", "cara"],), ["Al", "bo", "cara"])),
    ),
    Hunt(
        id="hunt-remove-while-looping",
        title="One refund too many",
        family=PYTHON,
        language="python",
        level=3,
        report="Refunds should be dropped from the list. For -5, -3 and 10, "
               "the -3 is still there afterwards. A single refund on its own "
               "is always dropped.",
        name="drop_refunds",
        params=("amounts",),
        start=(
            "def is_refund(amount):\n"
            "    return amount < 0\n"
            "\n"
            "\n"
            "def drop_refunds(amounts):\n"
            "    kept = list(amounts)\n"
            "    for amount in kept:\n"
            "        if is_refund(amount):\n"
            "            kept.remove(amount)\n"
            "    return kept\n"
        ),
        fixed=(
            "def is_refund(amount):\n"
            "    return amount < 0\n"
            "\n"
            "\n"
            "def drop_refunds(amounts):\n"
            "    kept = list(amounts)\n"
            "    for amount in amounts:\n"
            "        if is_refund(amount):\n"
            "            kept.remove(amount)\n"
            "    return kept\n"
        ),
        solve=_drop_refunds,
        reported=([-5, -3, 10],),
        cases=(([],), ([1, 2],), ([-1, 4],), ([5, -2],), ([-5, -3, 10],),
               ([-1, -1],)),
        cause="The loop walks kept while removing from kept. Removing -5 "
              "moves everything left one place, so the loop's next step "
              "lands past -3 and never looks at it.",
        decoys=(
            "is_refund treats -3 as a sale because it is closer to zero.",
            "list(amounts) only copies the first item.",
            "remove() takes away every refund with the same value at once.",
        ),
        lesson="Never add to or remove from a list while a for loop is "
               "walking it: the loop keeps its place by position, and the "
               "positions move. Loop over one list and change another, or "
               "build the result: [a for a in amounts if a >= 0].",
        hint="Put two refunds next to each other: drop_refunds([-5, -3, 10]).",
        checks=((([-5, -3, 10],), [10]), (([-1, 4],), [4]), (([-1, -1],), [])),
    ),
    Hunt(
        id="hunt-round-half-even",
        title="2.50 rounds down to 2",
        family=PYTHON,
        language="python",
        level=3,
        report="An item costing 2 is 2.50 with tax, and the till rounds it to "
               "2 - halves should round up, to 3. Most prices come out right; "
               "6 is 7.50 and correctly becomes 8.",
        name="till_total",
        params=("prices",),
        start=(
            "def with_tax(price):\n"
            "    return price * 1.25\n"
            "\n"
            "\n"
            "def rounded(value):\n"
            "    return round(value)\n"
            "\n"
            "\n"
            "def till_total(prices):\n"
            "    return sum(rounded(with_tax(p)) for p in prices)\n"
        ),
        fixed=(
            "def with_tax(price):\n"
            "    return price * 1.25\n"
            "\n"
            "\n"
            "def rounded(value):\n"
            "    return int(value + 0.5)\n"
            "\n"
            "\n"
            "def till_total(prices):\n"
            "    return sum(rounded(with_tax(p)) for p in prices)\n"
        ),
        solve=_till_total,
        reported=([2],),
        cases=(([],), ([4],), ([6],), ([1],), ([3],), ([2],), ([10],)),
        cause="round() rounds a half to the nearest EVEN number, so 2.5 "
              "becomes 2 while 7.5 becomes 8. The till wants every half "
              "rounded up.",
        decoys=(
            "1.25 cannot be stored exactly, so 2 * 1.25 comes out a little under 2.5.",
            "sum() turns the rounded prices back into floats and drops the half.",
            "with_tax adds the tax twice for small prices.",
        ),
        lesson="Python's round() is 'round half to even' (banker's rounding): "
               "round(2.5) is 2 and round(3.5) is 4. It is fair over many "
               "sums but not what a receipt expects; for money, use "
               "decimal.Decimal with ROUND_HALF_UP.",
        hint="Find a price whose taxed amount ends in exactly .5: till_total([2]).",
        checks=((([2],), 3), (([6],), 8), (([1],), 1), (([10],), 13)),
    ),
    Hunt(
        id="hunt-shared-default",
        title="Every word gets every tag",
        family=PYTHON,
        language="python",
        level=4,
        report="Each word should get its own list with just itself in it. "
               "For ['a', 'b'] I get [['a', 'b'], ['a', 'b']]. An empty list "
               "of words is fine.",
        name="tag_lists",
        params=("words",),
        start=(
            "def add_tag(tag, tags=[]):\n"
            "    tags.append(tag)\n"
            "    return tags\n"
            "\n"
            "\n"
            "def tag_lists(words):\n"
            "    result = []\n"
            "    for word in words:\n"
            "        result.append(add_tag(word))\n"
            "    return result\n"
        ),
        fixed=(
            "def add_tag(tag, tags=None):\n"
            "    tags = (tags or []) + [tag]\n"
            "    return tags\n"
            "\n"
            "\n"
            "def tag_lists(words):\n"
            "    result = []\n"
            "    for word in words:\n"
            "        result.append(add_tag(word))\n"
            "    return result\n"
        ),
        solve=_tag_lists,
        reported=(["a", "b"],),
        cases=(([],), (["a", "b"],), (["x"],), (["p", "q", "r"],)),
        cause="The default list is made once, when the def runs, and every "
              "call that leaves tags out appends to that same list - so "
              "every word's list is one shared list holding all of them.",
        decoys=(
            "result.append adds the whole result to itself on each turn.",
            "tag_lists passes the words to add_tag in reverse order.",
            "add_tag returns the list before the tag has been added.",
        ),
        lesson="Default values are worked out once, at def time. A mutable "
               "default - [] or {} - is shared by every call that uses it. "
               "Default to None and make the new list inside the function.",
        hint="Tag two words: tag_lists([\"a\", \"b\"]).",
        checks=(((["a", "b"],), [["a"], ["b"]]), (([],), []), ((["x"],), [["x"]])),
    ),
)
