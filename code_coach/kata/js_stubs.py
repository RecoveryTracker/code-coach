"""Finish the program: a stub with the rest of the code around it.

The third shape, after writing a function from nothing and fixing one
that is wrong. Here the program is already there — its constants, its
helpers, the comment saying how the page calls it — and one function is
empty. You fill that in.

It is the shape boot.dev uses and it is worth stealing, because it is
the one that looks like work. A kata on its own is a puzzle with no
surroundings; real code always has surroundings, and half of writing a
function is noticing that the thing you were about to write by hand is
already sitting three lines above you. Every stub here has a helper or
a constant in scope that the answer should use.

The machinery is the machinery. A stub is a kata whose `start` holds the
whole program instead of a broken function, so the driver, the marker,
the mutation check and the screen are the ones already in use. What
changes is that the code in the box is not wrong — it is unfinished.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Finish the program"


def _total_with_tax(items: list) -> int:
    total = sum(round(item["price"] * 100) for item in items)
    return round(total * 1.2)


def _render_row(item: dict) -> str:
    name = (
        str(item["name"])
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f'<li class="row">{name}</li>'


def _parse_query(search: str) -> dict:
    out: dict = {}
    text = search[1:] if search.startswith("?") else search
    if not text:
        return out
    for pair in text.split("&"):
        if not pair:
            continue
        key, _, value = pair.partition("=")
        if key:
            out[key] = value
    return out


def _next_state(state: dict, action: dict) -> dict:
    kind = action["type"]
    if kind == "add":
        return {**state, "count": state["count"] + 1}
    if kind == "reset":
        return {**state, "count": 0}
    if kind == "rename":
        return {**state, "name": action["value"]}
    return state


def _visible_items(items: list, which: str) -> list:
    if which == "all":
        return list(items)
    if which == "done":
        return [i for i in items if i["done"]]
    if which == "todo":
        return [i for i in items if not i["done"]]
    return []


STUBS: tuple[Kata, ...] = (
    Kata(
        id="js-stub-total",
        js_answer=(
            "// The rate the shop charges, and the helper the rest of the\n"
            "// program already uses for money.\n"
            "const TAX_RATE = 0.2;\n"
            "\n"
            "function pence(pounds) {\n"
            "  return Math.round(pounds * 100);\n"
            "}\n"
            "\n"
            "// The checkout calls this and prints what comes back:\n"
            "//   show(`Total: ${totalWithTax(cart)}p`);\n"
            "function totalWithTax(items) {\n"
            "  const total = items.reduce((sum, item) => sum + pence(item.price), 0);\n"
            "  return Math.round(total * (1 + TAX_RATE));\n"
            "}"
        ),
        level=2,
        language="javascript",
        name="totalWithTax",
        family=FAMILY,
        brief=(
            "Add up the prices and put the tax on. Return whole pence. "
            "The program above you has a pence() helper and the tax rate "
            "already — use them rather than writing the arithmetic again."
        ),
        params=("items",),
        example="totalWithTax([{ price: 1.0 }]) is 120",
        hint=(
            "Convert each price to pence before adding, not after: "
            "adding the pounds first leaves you rounding a number binary "
            "cannot hold exactly."
        ),
        cases=(
            ([{"price": 1.0}],),
            ([],),
            ([{"price": 0.0}],),
            ([{"price": 0.01}],),
            ([{"price": 1.0}, {"price": 2.0}],),
            ([{"price": 19.99}],),
            ([{"price": 0.1}, {"price": 0.2}],),
            ([{"price": 100.0}],),
            ([{"price": 2.5}, {"price": 2.5}],),
            ([{"price": 0.05}],),
        ),
        solve=_total_with_tax,
        checks=(
            ((([{"price": 1.0}],)), 120),
            ((([],)), 0),
            ((([{"price": 0.0}],)), 0),
            # A tenth and two tenths: thirty pence, then tax.
            ((([{"price": 0.1}, {"price": 0.2}],)), 36),
            ((([{"price": 19.99}],)), 2399),
        ),
        start=(
            "// The rate the shop charges, and the helper the rest of the\n"
            "// program already uses for money.\n"
            "const TAX_RATE = 0.2;\n"
            "\n"
            "function pence(pounds) {\n"
            "  return Math.round(pounds * 100);\n"
            "}\n"
            "\n"
            "// The checkout calls this and prints what comes back:\n"
            "//   show(`Total: ${totalWithTax(cart)}p`);\n"
            "function totalWithTax(items) {\n"
            "  // your code here\n"
            "}"
        ),
        bug=(
            "The two things already in scope are the two things worth "
            "using: pence() so the rounding happens once per price, and "
            "TAX_RATE so the number lives in one place. Writing "
            "`* 100` and `* 1.2` by hand works and puts the same two "
            "facts in a second place."
        ),
    ),
    Kata(
        id="js-stub-render-row",
        js_answer=(
            "// Anything that came from a person gets escaped before it\n"
            "// goes anywhere near innerHTML. This is why.\n"
            "function escapeHtml(text) {\n"
            "  return String(text)\n"
            "    .replaceAll(\"&\", \"&amp;\")\n"
            "    .replaceAll(\"<\", \"&lt;\")\n"
            "    .replaceAll(\">\", \"&gt;\");\n"
            "}\n"
            "\n"
            "// The list is built by joining these together:\n"
            "//   list.innerHTML = items.map(renderRow).join(\"\");\n"
            "function renderRow(item) {\n"
            "  return `<li class=\"row\">${escapeHtml(item.name)}</li>`;\n"
            "}"
        ),
        level=3,
        language="javascript",
        name="renderRow",
        family=FAMILY,
        brief=(
            "Return the markup for one row: an li with class 'row' "
            "holding the item's name. The name comes from the user, so "
            "escape it with the helper above rather than dropping it in."
        ),
        params=("item",),
        example='renderRow({ name: "Tea" }) is \'<li class="row">Tea</li>\'',
        hint=(
            "escapeHtml is already written. The whole point of this "
            "exercise is that you call it instead of not calling it."
        ),
        cases=(
            ({"name": "Tea"},),
            ({"name": ""},),
            ({"name": "a"},),
            ({"name": "Fish & Chips"},),
            ({"name": "<script>"},),
            ({"name": "1 < 2"},),
            ({"name": "a > b"},),
            ({"name": "plain"},),
            ({"name": "&amp;"},),
            ({"name": "<b>bold</b>"},),
        ),
        solve=_render_row,
        checks=(
            (({"name": "Tea"},), '<li class="row">Tea</li>'),
            (({"name": ""},), '<li class="row"></li>'),
            (({"name": "a"},), '<li class="row">a</li>'),
            (({"name": "<script>"},),
             '<li class="row">&lt;script&gt;</li>'),
            (({"name": "Fish & Chips"},),
             '<li class="row">Fish &amp; Chips</li>'),
        ),
        start=(
            "// Anything that came from a person gets escaped before it\n"
            "// goes anywhere near innerHTML. This is why.\n"
            "function escapeHtml(text) {\n"
            "  return String(text)\n"
            '    .replaceAll("&", "&amp;")\n'
            '    .replaceAll("<", "&lt;")\n'
            '    .replaceAll(">", "&gt;");\n'
            "}\n"
            "\n"
            "// The list is built by joining these together:\n"
            '//   list.innerHTML = items.map(renderRow).join("");\n'
            "function renderRow(item) {\n"
            "  // your code here\n"
            "}"
        ),
        bug=(
            "The ampersand has to be replaced first. Doing the angle "
            "brackets first turns < into &lt; and then the ampersand "
            "pass turns that into &amp;lt;, which shows the escape on "
            "the page instead of the character — which is why the helper "
            "is written once and called, rather than rewritten per row."
        ),
    ),
    Kata(
        id="js-stub-parse-query",
        js_answer=(
            "// Called on load, with whatever is after the question mark\n"
            "// in the address bar:\n"
            "//   const filters = parseQuery(window.location.search);\n"
            "//\n"
            "// Every value is a string — there are no numbers in a URL.\n"
            "function parseQuery(search) {\n"
            "  return Object.fromEntries(new URLSearchParams(search));\n"
            "}"
        ),
        level=3,
        language="javascript",
        name="parseQuery",
        family=FAMILY,
        brief=(
            "Turn a query string into an object of strings. It may or "
            "may not start with a question mark. An empty one gives an "
            "empty object, and a key with nothing after the equals gives "
            "an empty string."
        ),
        params=("search",),
        example='parseQuery("?a=1&b=2") is { a: "1", b: "2" }',
        hint=(
            "URLSearchParams does the splitting and the question mark "
            "for you, and Object.fromEntries turns it into an object — "
            "but doing it by hand with split is a fair answer too."
        ),
        cases=(
            ("?a=1&b=2",), ("",), ("?",), ("a=1",), ("?a=",),
            ("?a=1&a=2",), ("?one=hello",), ("?x=1&y=2&z=3",),
            ("?flag=",), ("k=v",),
        ),
        solve=_parse_query,
        checks=(
            (("?a=1&b=2",), {"a": "1", "b": "2"}),
            (("",), {}),
            (("?",), {}),
            (("a=1",), {"a": "1"}),
            (("?a=",), {"a": ""}),
            # The last one wins, which is what both the hand-written
            # loop and URLSearchParams.get do.
            (("?a=1&a=2",), {"a": "2"}),
        ),
        start=(
            "// Called on load, with whatever is after the question mark\n"
            "// in the address bar:\n"
            "//   const filters = parseQuery(window.location.search);\n"
            "//\n"
            "// Every value is a string — there are no numbers in a URL.\n"
            "function parseQuery(search) {\n"
            "  // your code here\n"
            "}"
        ),
        bug=(
            "Everything out of a query string is text. The page that "
            "treats `?page=2` as the number two works until it compares "
            "it with a number and gets false, which is the bug this "
            "shape of function usually causes rather than has."
        ),
    ),
    Kata(
        id="js-stub-next-state",
        js_answer=(
            "// The whole app's state lives in one object, and every\n"
            "// change goes through here. Nothing else writes to it.\n"
            "//\n"
            "//   state = nextState(state, { type: \"add\" });\n"
            "//   render(state);\n"
            "//\n"
            "// Which only works if this returns a new object — render\n"
            "// compares the old one with the new one to decide whether\n"
            "// there is anything to redraw.\n"
            "function nextState(state, action) {\n"
            "  switch (action.type) {\n"
            "    case \"add\":\n"
            "      return { ...state, count: state.count + 1 };\n"
            "    case \"reset\":\n"
            "      return { ...state, count: 0 };\n"
            "    case \"rename\":\n"
            "      return { ...state, name: action.value };\n"
            "    default:\n"
            "      return state;\n"
            "  }\n"
            "}"
        ),
        level=4,
        language="javascript",
        name="nextState",
        family=FAMILY,
        brief=(
            "Return the new state for an action, without changing the "
            "one you were given. 'add' raises the count by one, 'reset' "
            "puts it back to zero, 'rename' sets the name from the "
            "action's value, and anything else returns the state as it "
            "was."
        ),
        params=("state", "action"),
        example='nextState({ count: 0 }, { type: "add" }) is { count: 1 }',
        hint=(
            "Spread the old state into a new object and change the one "
            "field. Assigning into the state you were handed is the bug "
            "this is here to prevent."
        ),
        cases=(
            ({"count": 0, "name": "a"}, {"type": "add"}),
            ({"count": 0, "name": "a"}, {"type": "reset"}),
            ({"count": 3, "name": "a"}, {"type": "reset"}),
            ({"count": 0, "name": "a"}, {"type": "rename", "value": "b"}),
            ({"count": 0, "name": "a"}, {"type": "nonsense"}),
            ({"count": -1, "name": "a"}, {"type": "add"}),
            ({"count": 9, "name": "x"}, {"type": "add"}),
            ({"count": 0, "name": ""}, {"type": "rename", "value": ""}),
            ({"count": 1, "name": "a"}, {"type": "rename", "value": "z"}),
            ({"count": 0, "name": "a"}, {"type": "add"}),
        ),
        solve=_next_state,
        checks=(
            (({"count": 0, "name": "a"}, {"type": "add"}),
             {"count": 1, "name": "a"}),
            (({"count": 3, "name": "a"}, {"type": "reset"}),
             {"count": 0, "name": "a"}),
            (({"count": 0, "name": "a"}, {"type": "nonsense"}),
             {"count": 0, "name": "a"}),
            (({"count": -1, "name": "a"}, {"type": "add"}),
             {"count": 0, "name": "a"}),
            (({"count": 0, "name": "a"}, {"type": "rename", "value": "b"}),
             {"count": 0, "name": "b"}),
        ),
        start=(
            "// The whole app's state lives in one object, and every\n"
            "// change goes through here. Nothing else writes to it.\n"
            "//\n"
            "//   state = nextState(state, { type: \"add\" });\n"
            "//   render(state);\n"
            "//\n"
            "// Which only works if this returns a new object — render\n"
            "// compares the old one with the new one to decide whether\n"
            "// there is anything to redraw.\n"
            "function nextState(state, action) {\n"
            "  // your code here\n"
            "}"
        ),
        bug=(
            "Returning a changed copy rather than the same object is the "
            "whole discipline. A render that asks `state === previous` "
            "sees no difference when you edited in place, so the screen "
            "keeps showing the old numbers and the data is right — which "
            "is the hardest version of this bug to find."
        ),
    ),
    Kata(
        id="js-stub-visible",
        js_answer=(
            "// The three buttons above the list set this, and the list\n"
            "// is redrawn from whatever comes back:\n"
            "//   render(visibleItems(TODOS, currentFilter));\n"
            "//\n"
            "// TODOS is the real array the app keeps, so whatever this\n"
            "// returns must not be it.\n"
            "function visibleItems(items, which) {\n"
            "  if (which === \"all\") return [...items];\n"
            "  if (which === \"done\") return items.filter((i) => i.done);\n"
            "  if (which === \"todo\") return items.filter((i) => !i.done);\n"
            "  return [];\n"
            "}"
        ),
        level=1,
        language="javascript",
        name="visibleItems",
        family=FAMILY,
        brief=(
            "Return the items the current filter should show: 'all' is "
            "everything, 'done' is the finished ones, 'todo' is the "
            "rest. Anything else shows nothing. The list you were given "
            "must not change."
        ),
        params=("items", "which"),
        example='visibleItems([{ done: true }], "done") keeps the one item',
        hint=(
            "filter already returns a new array, so the no-changing rule "
            "comes free — but 'all' has to make a copy rather than hand "
            "back the same array."
        ),
        cases=(
            ([{"done": True}, {"done": False}], "all"),
            ([], "all"),
            ([], "done"),
            ([{"done": True}], "done"),
            ([{"done": True}], "todo"),
            ([{"done": False}], "todo"),
            ([{"done": False}], "done"),
            ([{"done": True}, {"done": True}], "todo"),
            ([{"done": True}], "nonsense"),
            ([{"done": False}, {"done": True}], "done"),
        ),
        solve=_visible_items,
        checks=(
            ((([], "all")), []),
            ((([{"done": True}], "done")), [{"done": True}]),
            ((([{"done": True}], "todo")), []),
            ((([{"done": False}], "todo")), [{"done": False}]),
            ((([{"done": True}], "nonsense")), []),
        ),
        start=(
            "// The three buttons above the list set this, and the list\n"
            "// is redrawn from whatever comes back:\n"
            "//   render(visibleItems(TODOS, currentFilter));\n"
            "//\n"
            "// TODOS is the real array the app keeps, so whatever this\n"
            "// returns must not be it.\n"
            "function visibleItems(items, which) {\n"
            "  // your code here\n"
            "}"
        ),
        bug=(
            "Returning `items` for 'all' hands back the app's own array. "
            "Anything the caller then does to the visible list — a sort "
            "for display, say — happens to the real one. `[...items]` "
            "costs nothing and closes it."
        ),
    ),
)
