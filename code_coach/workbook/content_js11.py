"""Pages 178-187: JavaScript, working with data.

The JavaScript book taught find, some, reduce, sort and the rest on bare
numbers and words. Real JavaScript spends its day on something else: an
array of small objects, the shape every API hands back. These ten pages
drill the everyday moves on exactly that shape, so the method is no longer
the new part and the data is.

Numbered after the regex pages (168-177, content_js10), so this tuple has
to be registered after JS10_PAGES for the book to stay in order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


def _objs(fields, rows) -> list[dict]:
    return [dict(zip(fields, row)) for row in rows]


def _desc(items) -> str:
    """ann (age 25), bob (age 34) - the data, readably, for a prompt."""
    out = []
    for item in items:
        rest = ", ".join(
            f"{k} {str(v).lower() if isinstance(v, bool) else v}"
            for k, v in item.items() if k != "name")
        out.append(f"{item['name']} ({rest})")
    return ", ".join(out)


def _ids(field, values) -> list[dict]:
    return [{"id": i + 1, field: v} for i, v in enumerate(values)]


# ── 178. find and findIndex ──────────────────────────────────

_FINDS = (
    ("users", "age", (("ann", 25), ("bob", 34), ("cy", 41), ("dee", 19)), 30, "zed"),
    ("users", "age", (("eve", 52), ("fay", 28), ("gus", 61)), 50, "ann"),
    ("products", "price", (("pen", 3), ("mug", 12), ("hat", 20), ("cap", 9)), 10, "sock"),
    ("players", "score", (("kim", 70), ("lee", 95), ("max", 88), ("ned", 60)), 80, "ola"),
    ("books", "pages", (("dune", 412), ("emma", 380), ("ulysses", 730), ("it", 1138)), 500, "odyssey"),
    ("products", "stock", (("tea", 0), ("jam", 5), ("oil", 14), ("rice", 22)), 10, "salt"),
    ("users", "age", (("tom", 17), ("uma", 16), ("val", 18), ("wes", 21)), 17, "xia"),
    ("cities", "pop", (("rome", 28), ("oslo", 7), ("lima", 97), ("kyiv", 29)), 25, "paris"),
    ("players", "score", (("ada", 12), ("ben", 9), ("cal", 15), ("dan", 30), ("eli", 22)), 20, "fox"),
    ("orders", "total", (("ord1", 40), ("ord2", 15), ("ord3", 90), ("ord4", 75)), 50, "ord9"),
    ("tasks", "hours", (("plan", 2), ("code", 8), ("test", 5), ("ship", 1), ("fix", 6)), 4, "demo"),
    ("users", "age", (("ivy", 8), ("jo", 12), ("kai", 40), ("lu", 33)), 30, "mo"),
    ("products", "price", (("fig", 2), ("kiwi", 1), ("lime", 3), ("mango", 4), ("pear", 5)), 3, "plum"),
    ("players", "goals", (("ana", 0), ("bo", 3), ("cleo", 1), ("dex", 7), ("emi", 4)), 2, "finn"),
    ("books", "year", (("emma", 1815), ("dune", 1965), ("it", 1986), ("beloved", 1987)), 1900, "odyssey"),
    ("cities", "temp", (("cairo", 35), ("oslo", 12), ("lima", 22), ("delhi", 38), ("rome", 30)), 32, "quito"),
    ("tasks", "points", (("login", 3), ("search", 8), ("cart", 5), ("pay", 13)), 6, "chat"),
    ("users", "visits", (("sam", 3), ("pat", 0), ("jan", 9), ("ray", 11), ("liz", 2)), 8, "ted"),
    ("products", "weight", (("bag", 700), ("box", 250), ("crate", 1200), ("tub", 900)), 800, "tin"),
    ("players", "level", (("rio", 4), ("sky", 9), ("ash", 2), ("bay", 7), ("cruz", 10)), 6, "dot"),
)

FIND_PAGE = _page(
    "js-data-find", 178, "Working with data: find the first match, and where",
    "An API hands you an array of objects, and the first question is "
    "usually 'which one?'. find walks the array from the front and gives "
    "back the first object your test says yes to — the whole object, so "
    "you can read any field off it. findIndex asks the same question and "
    "gives back the position instead, and -1 when nothing matched. find "
    "gives undefined when nothing matched, which is why these exercises "
    "only read .name off a find that is sure to succeed.",
    "users.find((u) => u.age > 30) is the first user over 30, the object "
    "itself; users.findIndex((u) => u.name === \"zed\") is -1 when there "
    "is no zed",
    "js_data_find",
    tuple(
        (f"Given {v} {_desc(_objs(('name', f), rows))}, print the name of "
         f"the first with {f} over {over}, then its position, then the "
         f"position of {absent!r}, who is not there.",
         {"var": v, "field": f, "items": _objs(("name", f), rows),
          "over": over, "absent": absent})
        for v, f, rows, over, absent in _FINDS
    ),
)


# ── 179. some and every ──────────────────────────────────────

_T, _F = True, False
_QUESTIONS = (
    ("users", "age", "active", (("ann", 25, _T), ("bob", 34, _T), ("cy", 41, _T)), 40, "bob"),
    ("users", "age", "active", (("dee", 19, _F), ("eve", 52, _T), ("fay", 28, _T)), 60, "zed"),
    ("products", "price", "inStock", (("pen", 3, _T), ("mug", 12, _F), ("hat", 20, _T)), 20, "cap"),
    ("products", "price", "inStock", (("tea", 4, _T), ("jam", 5, _T), ("oil", 9, _T)), 10, "jam"),
    ("tasks", "hours", "done", (("plan", 2, _T), ("code", 8, _F), ("test", 5, _F)), 8, "test"),
    ("tasks", "hours", "done", (("fix", 1, _T), ("ship", 2, _T), ("demo", 3, _T)), 5, "plan"),
    ("orders", "total", "paid", (("ord1", 40, _T), ("ord2", 15, _F), ("ord3", 90, _T), ("ord4", 75, _T)), 100, "ord4"),
    ("players", "score", "online", (("kim", 70, _T), ("lee", 95, _T), ("max", 88, _T), ("ned", 60, _T)), 95, "zoe"),
    ("users", "visits", "verified", (("sam", 3, _F), ("pat", 0, _F), ("jan", 9, _F)), 1, "pat"),
    ("books", "pages", "read", (("dune", 412, _T), ("emma", 380, _T), ("it", 1138, _F)), 1000, "ulysses"),
    ("cities", "temp", "sunny", (("cairo", 35, _T), ("oslo", 12, _F), ("lima", 22, _T), ("rome", 30, _T)), 40, "lima"),
    ("products", "stock", "onSale", (("rice", 22, _T), ("salt", 7, _T), ("oil", 14, _T)), 20, "salt"),
    ("tasks", "points", "done", (("login", 3, _T), ("cart", 5, _T), ("pay", 13, _T), ("search", 8, _T)), 20, "chat"),
    ("players", "goals", "fit", (("ana", 0, _T), ("bo", 3, _F), ("cleo", 1, _T)), 3, "dex"),
    ("users", "age", "admin", (("tom", 17, _F), ("uma", 16, _F), ("val", 18, _F)), 18, "uma"),
    ("orders", "total", "shipped", (("ord5", 12, _T), ("ord6", 8, _T), ("ord7", 30, _T)), 31, "ord8"),
    ("products", "weight", "fragile", (("bag", 700, _F), ("box", 250, _T), ("tub", 900, _F)), 900, "crate"),
    ("players", "level", "ready", (("rio", 4, _T), ("sky", 9, _T), ("ash", 2, _T), ("bay", 7, _T)), 10, "ash"),
    ("books", "year", "owned", (("emma", 1815, _T), ("it", 1986, _F), ("beloved", 1987, _T)), 1987, "dune"),
    ("users", "visits", "active", (("liz", 2, _T), ("ray", 11, _T), ("ted", 5, _T), ("una", 6, _T)), 12, "ray"),
)

SOME_EVERY_PAGE = _page(
    "js-data-some-every", 179, "Working with data: yes-no questions about a list",
    "Often you do not want an object back, only an answer: is anything "
    "over budget, has everyone paid, is this name in the list. some says "
    "true if at least one object passes the test, every says true only if "
    "all of them do, and both stop looking the moment they know. Test a "
    "true-or-false field directly — (u) => u.active — rather than writing "
    "=== true, because the field already is the answer.",
    "orders.some((o) => o.total >= 100) asks 'is any order 100 or more?'; "
    "orders.every((o) => o.paid) asks 'has every order been paid?'",
    "js_data_some_every",
    tuple(
        (f"Given {v} {_desc(_objs(('name', f, flag), rows))}, print whether "
         f"any has {f} of at least {limit}, then whether every one is "
         f"{flag}, then whether any is named {target!r}.",
         {"var": v, "field": f, "flag": flag,
          "items": _objs(("name", f, flag), rows),
          "limit": limit, "target": target})
        for v, f, flag, rows, limit, target in _QUESTIONS
    ),
)


# ── 180. Summing one field ───────────────────────────────────

_SUMS = (
    ("plain", "cart", (("pen", 3), ("mug", 12), ("hat", 20))),
    ("plain", "cart", (("tea", 4), ("jam", 5), ("oil", 9), ("rice", 2))),
    ("plain", "basket", (("fig", 2), ("kiwi", 1), ("lime", 3), ("pear", 5))),
    ("plain", "products", (("bag", 70), ("box", 25), ("tub", 90))),
    ("plain", "cart", (("book", 15), ("pen", 2), ("ink", 6), ("pad", 4))),
    ("plain", "basket", (("egg", 3), ("milk", 2), ("bread", 4), ("cheese", 9))),
    ("plain", "products", (("lamp", 40), ("desk", 120), ("chair", 85))),
    ("qty", "cart", (("pen", 3, 4), ("mug", 12, 1), ("hat", 20, 2))),
    ("qty", "basket", (("fig", 2, 6), ("lime", 3, 3), ("pear", 5, 2))),
    ("qty", "cart", (("tea", 4, 2), ("jam", 5, 3), ("oil", 9, 1))),
    ("qty", "products", (("bolt", 1, 50), ("nut", 1, 40), ("gear", 7, 3))),
    ("qty", "basket", (("egg", 3, 12), ("milk", 2, 2), ("bread", 4, 1))),
    ("qty", "cart", (("sock", 5, 3), ("shoe", 60, 1), ("lace", 2, 2))),
    ("qty", "products", (("cup", 6, 4), ("plate", 9, 4), ("bowl", 7, 2))),
    ("money", "cart", (("pen", 1.5), ("mug", 12.99), ("hat", 20.25))),
    ("money", "basket", (("fig", 0.4), ("kiwi", 0.35), ("lime", 0.3))),
    ("money", "cart", (("tea", 3.99), ("jam", 4.49), ("oil", 8.75), ("rice", 2.1))),
    ("money", "products", (("book", 12.5), ("pen", 0.99), ("ink", 5.25))),
    ("money", "basket", (("egg", 0.1), ("milk", 0.2), ("bread", 0.3))),
    ("money", "cart", (("lamp", 39.99), ("desk", 119.99), ("chair", 84.5))),
)


def _sum_prompt(want, v, items) -> str:
    base = f"Given {v} {_desc(items)}, "
    if want == "plain":
        return base + "print the total of the prices."
    if want == "qty":
        return base + "print the total of price times qty for each."
    return base + "print the total of the prices to two decimal places."


SUM_PAGE = _page(
    "js-data-sum", 180, "Working with data: adding up one field",
    "A cart total is the same reduce as adding up numbers, except each "
    "step reaches into an object for the number: sum + item.price. The 0 "
    "at the end is the starting total and matters more here than on bare "
    "numbers — without it, reduce starts from the first object itself and "
    "you get '[object Object]12' instead of a sum. Money in dollars and "
    "cents does not add exactly in floating point, so a total is rounded "
    "for display with toFixed(2), which also always shows both cents.",
    "cart.reduce((sum, c) => sum + c.price * c.qty, 0) is the order total; "
    "0.1 + 0.2 + 0.3 prints as 0.6000000000000001 until toFixed(2) makes "
    "it 0.60",
    "js_data_sum",
    tuple(
        (_sum_prompt(want, v, _objs(
            ("name", "price", "qty") if want == "qty" else ("name", "price"),
            rows)),
         {"want": want, "var": v, "items": _objs(
             ("name", "price", "qty") if want == "qty" else ("name", "price"),
             rows)})
        for want, v, rows in _SUMS
    ),
)


# ── 181. The biggest ─────────────────────────────────────────

_BESTS = (
    ("max", "players", "score", (("kim", 70), ("lee", 95), ("max", 88))),
    ("max", "users", "age", (("ann", 25), ("bob", 34), ("cy", 41), ("dee", 19))),
    ("max", "products", "price", (("pen", 3), ("mug", 12), ("hat", 20), ("cap", 9))),
    ("max", "books", "pages", (("dune", 412), ("emma", 380), ("ulysses", 730), ("it", 1138))),
    ("max", "cities", "pop", (("rome", 28), ("oslo", 7), ("lima", 97), ("kyiv", 29))),
    ("max", "tasks", "hours", (("plan", 2), ("code", 8), ("test", 5), ("ship", 1))),
    ("max", "players", "goals", (("ana", 0), ("bo", 3), ("cleo", 1), ("dex", 7), ("emi", 4))),
    ("max", "products", "rating", (("lamp", 4.2), ("desk", 4.8), ("chair", 3.9))),
    ("max", "users", "visits", (("sam", 3), ("pat", 0), ("jan", 9), ("ray", 11), ("liz", 2))),
    ("max", "cities", "temp", (("oslo", 12), ("cairo", 35), ("lima", 22), ("delhi", 38))),
    ("max", "orders", "total", (("ord1", 40), ("ord2", 15), ("ord3", 90), ("ord4", 75))),
    ("max", "products", "weight", (("box", 250), ("bag", 700), ("crate", 1200), ("tub", 900))),
    ("min", "products", "price", (("mug", 12), ("pen", 3), ("hat", 20))),
    ("min", "players", "score", (("kim", 70), ("lee", 95), ("ned", 60), ("max", 88))),
    ("min", "users", "age", (("bob", 34), ("ann", 25), ("dee", 19), ("cy", 41))),
    ("min", "cities", "temp", (("cairo", 35), ("oslo", 12), ("lima", 22))),
    ("min", "tasks", "hours", (("plan", 2), ("code", 8), ("ship", 1), ("test", 5))),
    ("min", "books", "year", (("dune", 1965), ("emma", 1815), ("it", 1986))),
    ("min", "products", "price", (("desk", 119.99), ("lamp", 39.99), ("chair", 84.5))),
    ("min", "orders", "total", (("ord1", 40), ("ord2", 15), ("ord3", 90), ("ord5", 12))),
)

MAX_PAGE = _page(
    "js-data-max", 181, "Working with data: the one with the biggest field",
    "Math.max gives you the biggest number but not the object it came "
    "from, and 'which product is dearest' wants the product. So carry the "
    "best object so far and swap it whenever the next one beats it: that "
    "is one pass, where sorting the whole list to take the first would do "
    "far more work and scramble a copy for nothing. With no starting value "
    "reduce begins from the first object, which is exactly the right "
    "starting champion. Flip > to < and the same code finds the smallest.",
    "players.reduce((top, p) => (p.score > top.score ? p : top)) is the "
    "top player, object and all",
    "js_data_max",
    tuple(
        (f"Given {v} {_desc(_objs(('name', f), rows))}, print the name and "
         f"{f} of the one with the {'highest' if want == 'max' else 'lowest'} "
         f"{f}, separated by a space.",
         {"want": want, "var": v, "field": f,
          "items": _objs(("name", f), rows)})
        for want, v, f, rows in _BESTS
    ),
)


# ── 182. Counting ────────────────────────────────────────────

_TALLIES = (
    ("orders", "status", ("paid", "sent", "paid"), ("paid", "sent", "lost")),
    ("tasks", "state", ("done", "todo", "todo", "todo"), ("todo", "done", "blocked")),
    ("users", "role", ("admin", "user", "user", "user", "admin"), ("user", "admin", "guest")),
    ("products", "color", ("red", "blue", "red", "red"), ("red", "blue", "green")),
    ("players", "team", ("red", "blue", "blue", "red", "blue"), ("blue", "red", "gold")),
    ("books", "genre", ("scifi", "romance", "horror", "horror"), ("horror", "scifi", "poetry")),
    ("cities", "country", ("france", "france", "italy", "italy", "france"), ("france", "italy", "spain")),
    ("orders", "status", ("sent", "sent", "lost", "sent", "paid"), ("sent", "paid", "open")),
    ("users", "country", ("uk", "us", "us", "uk", "us", "fr"), ("us", "uk", "de")),
    ("tasks", "owner", ("kim", "lee", "kim", "kim"), ("kim", "lee", "max")),
    ("products", "size", ("s", "m", "m", "l", "m"), ("m", "s", "xl")),
    ("players", "pos", ("gk", "df", "df", "fw", "df", "fw"), ("df", "fw", "mf")),
    ("books", "author", ("austen", "austen", "herbert", "king", "king", "king"), ("king", "austen", "tolkien")),
    ("orders", "city", ("oslo", "rome", "oslo", "oslo"), ("oslo", "rome", "lima")),
    ("users", "plan", ("free", "pro", "free", "free", "pro"), ("free", "pro", "team")),
    ("tasks", "tag", ("bug", "feature", "bug", "bug", "feature"), ("bug", "feature", "docs")),
    ("products", "brand", ("acme", "zest", "acme", "acme", "zest"), ("acme", "zest", "nova")),
    ("cities", "continent", ("africa", "america", "europe", "europe", "africa", "europe"), ("europe", "africa", "america", "asia")),
    ("players", "hand", ("left", "right", "right", "right"), ("right", "left", "both")),
    ("users", "lang", ("js", "py", "js", "go", "js", "py"), ("js", "py", "go", "rust")),
)

TALLY_PAGE = _page(
    "js-data-tally", 182, "Working with data: how many of each",
    "'How many orders are paid, how many sent?' is a tally: an empty "
    "object, and for each item add one to the count under its value. The "
    "first time a value turns up its count does not exist yet, so "
    "counts[key] is undefined and undefined + 1 is NaN — the ?? 0 turns "
    "that missing count into a zero before the one is added. Asking for a "
    "value that never appeared needs the same ?? 0, or it prints "
    "undefined.",
    "counts[o.status] = (counts[o.status] ?? 0) + 1; inside a for...of "
    "loop counts every status in one pass",
    "js_data_tally",
    tuple(
        (f"Given {v} whose {f} values are {', '.join(vals)}, count how many "
         f"have each {f}, then print the counts for "
         f"{', '.join(repr(k) for k in ask)}, one per line, with 0 for one "
         f"that never appears.",
         {"var": v, "field": f, "items": _ids(f, vals), "ask": list(ask)})
        for v, f, vals, ask in _TALLIES
    ),
)


# ── 183. Grouping ────────────────────────────────────────────

_GROUPS = (
    ("players", "team", (("kim", "red"), ("lee", "blue"), ("max", "red"))),
    ("users", "role", (("ann", "admin"), ("bob", "user"), ("cy", "user"), ("dee", "admin"))),
    ("products", "color", (("pen", "red"), ("mug", "blue"), ("hat", "red"), ("cap", "green"))),
    ("tasks", "state", (("plan", "done"), ("code", "todo"), ("test", "todo"), ("ship", "todo"))),
    ("books", "genre", (("dune", "scifi"), ("emma", "romance"), ("it", "horror"), ("carrie", "horror"))),
    ("cities", "country", (("lyon", "france"), ("rome", "italy"), ("nice", "france"), ("milan", "italy"))),
    ("orders", "status", (("ord1", "paid"), ("ord2", "sent"), ("ord3", "paid"), ("ord4", "lost"), ("ord5", "sent"))),
    ("users", "country", (("ann", "uk"), ("bob", "us"), ("cy", "us"), ("dee", "uk"), ("eve", "fr"))),
    ("players", "pos", (("ana", "gk"), ("bo", "df"), ("cleo", "df"), ("dex", "fw"), ("emi", "df"), ("finn", "fw"))),
    ("products", "size", (("tee", "s"), ("polo", "m"), ("vest", "m"), ("coat", "l"), ("cap", "m"))),
    ("tasks", "owner", (("plan", "kim"), ("code", "lee"), ("test", "kim"), ("ship", "max"), ("fix", "lee"))),
    ("books", "author", (("emma", "austen"), ("dune", "herbert"), ("it", "king"), ("carrie", "king"), ("persuasion", "austen"))),
    ("cities", "continent", (("cairo", "africa"), ("lima", "america"), ("oslo", "europe"), ("rome", "europe"), ("lagos", "africa"))),
    ("orders", "city", (("ord1", "oslo"), ("ord2", "rome"), ("ord3", "oslo"), ("ord4", "lima"), ("ord5", "rome"), ("ord6", "oslo"))),
    ("users", "plan", (("ann", "free"), ("bob", "pro"), ("cy", "free"), ("dee", "team"), ("eve", "pro"))),
    ("tasks", "tag", (("login", "bug"), ("cart", "feature"), ("pay", "bug"), ("search", "bug"), ("chat", "feature"))),
    ("products", "brand", (("fig", "acme"), ("kiwi", "zest"), ("lime", "acme"), ("pear", "nova"), ("plum", "zest"))),
    ("players", "hand", (("rio", "left"), ("sky", "right"), ("ash", "right"), ("bay", "left"), ("cruz", "right"))),
    ("users", "lang", (("ann", "js"), ("bob", "py"), ("cy", "js"), ("dee", "go"), ("eve", "js"), ("fay", "py"))),
    ("books", "decade", (("dune", "1960s"), ("it", "1980s"), ("carrie", "1970s"), ("misery", "1980s"), ("shining", "1970s"))),
)

GROUP_PAGE = _page(
    "js-data-group", 183, "Working with data: grouping by a field",
    "A tally keeps a number under each key; a group keeps a list. Same "
    "loop, but the first time a key turns up it gets an empty array, and "
    "every item is then pushed onto the array for its key — so you end up "
    "with 'team red: kim, max'. Object keys come back in the order they "
    "were first added, so sort them before printing if the order should "
    "not depend on the data.",
    "if (!groups[p.team]) groups[p.team] = []; then groups[p.team]"
    ".push(p.name); — create the list once, add to it every time",
    "js_data_group",
    tuple(
        (f"Given {v} {_desc(_objs(('name', f), rows))}, group the names by "
         f"{f} and print one line per {f} in alphabetical order, as the "
         f"{f}, a colon, then its names joined with a comma and a space.",
         {"var": v, "field": f, "items": _objs(("name", f), rows)})
        for v, f, rows in _GROUPS
    ),
)


# ── 184. Sorting ─────────────────────────────────────────────

_SORTS = (
    ("text", "users", ("name", "age"), (("cy", 41), ("ann", 25), ("bob", 34)), None, None),
    ("text", "products", ("name", "price"), (("pen", 3), ("mug", 12), ("hat", 20), ("cap", 9)), None, None),
    ("text", "players", ("name", "score"), (("lee", 95), ("kim", 70), ("ned", 60), ("max", 88)), None, None),
    ("text", "books", ("name", "pages"), (("dune", 412), ("emma", 380), ("it", 1138), ("beloved", 324)), None, None),
    ("text", "cities", ("name", "pop"), (("rome", 28), ("oslo", 7), ("lima", 97), ("kyiv", 29)), None, None),
    ("text", "tasks", ("name", "hours"), (("test", 5), ("plan", 2), ("code", 8), ("ship", 1)), None, None),
    ("text", "users", ("name", "age"), (("zoe", 22), ("amy", 30), ("mia", 27), ("eva", 35), ("ivy", 19)), None, None),
    ("number", "players", ("name", "score"), (("kim", 70), ("lee", 95), ("max", 88)), "score", None),
    ("number", "users", ("name", "age"), (("ann", 25), ("bob", 34), ("cy", 41), ("dee", 19)), "age", None),
    ("number", "products", ("name", "price"), (("pen", 3), ("mug", 12), ("hat", 20), ("cap", 9)), "price", None),
    ("number", "books", ("name", "pages"), (("dune", 412), ("emma", 380), ("it", 1138), ("beloved", 324)), "pages", None),
    ("number", "cities", ("name", "pop"), (("rome", 28), ("oslo", 7), ("lima", 97), ("kyiv", 29)), "pop", None),
    ("number", "tasks", ("name", "hours"), (("plan", 2), ("code", 8), ("test", 5), ("ship", 1), ("fix", 6)), "hours", None),
    ("number", "products", ("name", "price"), (("lamp", 39.99), ("desk", 119.99), ("chair", 84.5), ("rug", 64.25)), "price", None),
    ("two", "players", ("name", "team", "score"), (("kim", "red", 70), ("lee", "blue", 95), ("max", "red", 88), ("ned", "blue", 60)), "score", "team"),
    ("two", "users", ("name", "role", "age"), (("ann", "user", 25), ("bob", "admin", 34), ("cy", "user", 41), ("dee", "admin", 19)), "age", "role"),
    ("two", "products", ("name", "color", "price"), (("pen", "red", 3), ("mug", "blue", 12), ("hat", "red", 20), ("cap", "blue", 9), ("bag", "red", 15)), "price", "color"),
    ("two", "books", ("name", "genre", "pages"), (("dune", "scifi", 412), ("it", "horror", 1138), ("carrie", "horror", 199), ("emma", "romance", 380), ("solaris", "scifi", 204)), "pages", "genre"),
    ("two", "tasks", ("name", "state", "hours"), (("plan", "done", 2), ("code", "todo", 8), ("test", "todo", 5), ("ship", "done", 1), ("fix", "todo", 6)), "hours", "state"),
    ("two", "cities", ("name", "country", "pop"), (("lyon", "france", 5), ("rome", "italy", 28), ("nice", "france", 3), ("milan", "italy", 14), ("paris", "france", 21)), "pop", "country"),
)


def _sort_prompt(want, v, items, f, by) -> str:
    base = f"Given {v} {_desc(items)}, sort a copy "
    if want == "text":
        how = "by name alphabetically"
    elif want == "number":
        how = f"by {f}, highest first"
    else:
        how = f"by {by} alphabetically, and by {f} highest first within a {by}"
    return (base + how + ", print the sorted names joined with a comma and a "
            f"space, then print the first name in the original {v} to show "
            "it did not change.")


SORT_PAGE = _page(
    "js-data-sort", 184, "Working with data: sorting by text, by number, by both",
    "sort changes the array it is called on, and the array from an API is "
    "usually something else still needs in its original order, so spread "
    "a copy first. For text, a.name.localeCompare(b.name) returns the "
    "negative, zero or positive number sort wants. For numbers, b.score - "
    "a.score puts the highest first. For two fields, compare the first "
    "and, only when it says 0, fall through to the second: || does "
    "exactly that, because 0 is falsy.",
    "[...players].sort((a, b) => a.team.localeCompare(b.team) || b.score "
    "- a.score) sorts by team, then best score first inside each team",
    "js_data_sort",
    tuple(
        (_sort_prompt(want, v, _objs(fields, rows), f, by),
         {"want": want, "var": v, "items": _objs(fields, rows),
          **({"field": f} if f else {}), **({"by": by} if by else {})})
        for want, v, fields, rows, f, by in _SORTS
    ),
)


# ── 185. Formatting ──────────────────────────────────────────

_FORMATS = (
    ("plain", "products", (("pen", 3), ("mug", 12.5), ("hat", 20))),
    ("plain", "cart", (("tea", 3.99), ("jam", 4.49), ("oil", 8.75))),
    ("plain", "products", (("lamp", 39.99), ("desk", 119), ("chair", 84.5))),
    ("plain", "menu", (("soup", 6.5), ("salad", 8.25), ("bread", 2))),
    ("plain", "cart", (("fig", 0.4), ("kiwi", 0.35), ("lime", 0.3))),
    ("plain", "products", (("book", 12.5), ("pen", 0.99), ("ink", 5.25), ("pad", 3))),
    ("plain", "menu", (("tea", 2.2), ("coffee", 2.75), ("cake", 4.1))),
    ("plain", "cart", (("sock", 5), ("shoe", 59.9), ("lace", 1.25))),
    ("plain", "products", (("cup", 6.45), ("plate", 9.1), ("bowl", 7))),
    ("plain", "menu", (("pie", 3.3), ("tart", 3.45), ("bun", 1.05))),
    ("plain", "cart", (("egg", 0.25), ("milk", 1.19), ("bread", 2.49), ("cheese", 6.8))),
    ("plain", "products", (("rug", 64.25), ("vase", 18), ("clock", 42.75))),
    ("qty", "cart", (("pen", 1.5, 4), ("mug", 12.99, 1), ("hat", 20.25, 2))),
    ("qty", "cart", (("tea", 3.99, 2), ("jam", 4.49, 3), ("rice", 2.1, 5))),
    ("qty", "basket", (("fig", 0.4, 6), ("lime", 0.3, 3), ("kiwi", 0.35, 4))),
    ("qty", "cart", (("egg", 0.25, 12), ("milk", 1.19, 2), ("bread", 2.49, 1))),
    ("qty", "basket", (("sock", 5, 3), ("lace", 1.25, 2), ("shoe", 59.9, 1))),
    ("qty", "cart", (("cup", 6.45, 4), ("plate", 9.1, 4), ("bowl", 7, 2))),
    ("qty", "basket", (("pie", 3.3, 3), ("tart", 3.45, 2), ("bun", 1.05, 6))),
    ("qty", "cart", (("book", 12.5, 2), ("ink", 5.25, 3), ("pad", 3, 5))),
)


def _format_prompt(want, v, items) -> str:
    base = f"Given {v} {_desc(items)}, "
    if want == "plain":
        return (base + "print one line per item as its name, a colon, a "
                "space, then the price with a dollar sign and two decimal "
                "places.")
    return (base + "print one line per item as the qty, ' x ', the name, a "
            "colon, a space, then price times qty with a dollar sign and two "
            "decimal places.")


FORMAT_PAGE = _page(
    "js-data-format", 185, "Working with data: every object as a line of text",
    "Before data reaches a screen it becomes text, and map is how: one "
    "object in, one formatted string out, and the new array is exactly as "
    "long as the old one. Inside a template literal, $$ before the brace "
    "is a real dollar sign followed by the ${...} hole. toFixed(2) is what "
    "turns 3 into 3.00 and 12.5 into 12.50, and it hands back a string, "
    "which is fine because a string is what the line wants. join(\"\\n\") "
    "then puts one per line.",
    "products.map((p) => `${p.name}: $${p.price.toFixed(2)}`).join(\"\\n\") "
    "prints pen: $3.00 on its own line, and so on",
    "js_data_format",
    tuple(
        (_format_prompt(want, v, _objs(
            ("name", "price", "qty") if want == "qty" else ("name", "price"),
            rows)),
         {"want": want, "var": v, "items": _objs(
             ("name", "price", "qty") if want == "qty" else ("name", "price"),
             rows)})
        for want, v, rows in _FORMATS
    ),
)


# ── 186. A tally, printed in order ───────────────────────────

_ENTRIES = (
    ("keys", "orders", "status", ("paid", "sent", "paid", "lost")),
    ("keys", "tasks", "state", ("todo", "done", "todo", "todo", "blocked")),
    ("keys", "users", "role", ("user", "admin", "user", "guest")),
    ("keys", "products", "color", ("red", "blue", "red", "green", "blue", "red")),
    ("keys", "players", "team", ("red", "blue", "blue", "gold")),
    ("keys", "books", "genre", ("scifi", "romance", "horror", "horror")),
    ("keys", "cities", "country", ("italy", "france", "italy", "spain", "france")),
    ("keys", "users", "lang", ("py", "js", "go", "js", "py", "js")),
    ("count", "orders", "status", ("sent", "paid", "sent", "lost", "sent")),
    ("count", "products", "color", ("blue", "red", "red", "green", "red")),
    ("count", "users", "role", ("user", "user", "admin", "user", "guest", "admin")),
    ("count", "players", "team", ("red", "blue", "red", "gold", "red", "blue")),
    ("count", "tasks", "tag", ("feature", "bug", "feature", "docs", "feature")),
    ("count", "cities", "continent", ("europe", "africa", "europe", "asia", "europe", "africa")),
    ("count", "books", "author", ("king", "austen", "king", "herbert", "austen", "king")),
    ("count", "users", "plan", ("team", "free", "team", "pro", "team", "pro")),
    ("count", "orders", "city", ("rome", "oslo", "rome", "lima", "rome", "oslo", "lima", "rome")),
    ("count", "products", "size", ("m", "s", "l", "m", "m", "s")),
    ("count", "players", "pos", ("fw", "df", "fw", "gk", "fw", "df", "mf")),
    ("count", "users", "country", ("us", "uk", "fr", "us", "uk", "us", "de", "us")),
)


def _entries_prompt(want, v, f, vals) -> str:
    base = (f"Given {v} whose {f} values are {', '.join(vals)}, count how "
            f"many have each {f}, then print every {f} and its count as "
            f"'{f}: count', one per line, ")
    if want == "keys":
        return base + f"in alphabetical order of {f}."
    return base + "most common first, alphabetically where counts tie."


ENTRIES_PAGE = _page(
    "js-data-entries", 186, "Working with data: printing a tally in order",
    "A tally object answers 'how many paid?' but cannot be sorted, because "
    "an object has no order you control. Object.entries turns it into an "
    "array of [key, count] pairs, and an array can be sorted: pair[0] is "
    "the key and pair[1] the count. Sort by pair[1] for most common first, "
    "with || and localeCompare on pair[0] to settle ties the same way "
    "every time, then destructure each pair straight into two names in "
    "the for...of.",
    "Object.entries(counts).sort((a, b) => b[1] - a[1] || a[0]"
    ".localeCompare(b[0])) is most common first; for (const [key, n] of "
    "rows) reads each pair",
    "js_data_entries",
    tuple(
        (_entries_prompt(want, v, f, vals),
         {"want": want, "var": v, "field": f, "items": _ids(f, vals)})
        for want, v, f, vals in _ENTRIES
    ),
)


# ── 187. Chaining into a report ──────────────────────────────

_TOPS = (
    ("products", "score", 50, 3, (("lamp", 40, 81), ("desk", 120, 95), ("chair", 85, 77), ("rug", 30, 64), ("vase", 18, 70), ("mug", 9, 58))),
    ("hotels", "score", 100, 3, (("ritz", 450, 98), ("inn", 80, 71), ("lodge", 95, 84), ("hostel", 30, 62), ("motel", 60, 55))),
    ("games", "score", 20, 2, (("chess", 15, 90), ("tetris", 10, 85), ("doom", 25, 95), ("pong", 5, 60))),
    ("books", "likes", 15, 3, (("dune", 12, 540), ("emma", 8, 310), ("it", 18, 700), ("carrie", 9, 420), ("misery", 11, 380))),
    ("phones", "score", 500, 3, (("pixel", 499, 88), ("iphone", 999, 93), ("moto", 199, 71), ("nokia", 99, 60), ("galaxy", 450, 85))),
    ("products", "votes", 30, 2, (("pen", 3, 12), ("mug", 12, 40), ("hat", 20, 33), ("cap", 9, 27), ("bag", 45, 80))),
    ("hotels", "score", 200, 3, (("plaza", 350, 97), ("dorm", 40, 60), ("suite", 180, 90), ("cabin", 120, 82), ("hut", 50, 66))),
    ("games", "votes", 30, 3, (("zelda", 60, 980), ("mario", 50, 950), ("tetris", 10, 700), ("pong", 5, 300), ("snake", 3, 450), ("doom", 25, 820))),
    ("books", "score", 10, 2, (("odyssey", 9, 88), ("iliad", 11, 91), ("emma", 8, 79), ("dune", 12, 94), ("it", 7, 70))),
    ("products", "score", 25, 3, (("tea", 4, 61), ("jam", 5, 72), ("oil", 9, 68), ("rice", 2, 55), ("honey", 30, 90))),
    ("phones", "likes", 300, 2, (("moto", 199, 410), ("nokia", 99, 380), ("pixel", 499, 900), ("oppo", 250, 450))),
    ("hotels", "votes", 90, 3, (("inn", 80, 310), ("hostel", 30, 150), ("motel", 60, 220), ("ritz", 450, 990), ("bnb", 70, 260))),
    ("games", "score", 40, 3, (("catan", 35, 88), ("risk", 30, 70), ("go", 20, 92), ("chess", 15, 85), ("bridge", 5, 60), ("gloom", 90, 99))),
    ("books", "votes", 20, 3, (("dune", 12, 540), ("it", 18, 700), ("emma", 8, 310), ("ulysses", 25, 800), ("carrie", 9, 420))),
    ("products", "likes", 100, 2, (("lamp", 40, 81), ("desk", 120, 95), ("chair", 85, 77), ("rug", 30, 64))),
    ("phones", "score", 400, 3, (("moto", 199, 71), ("nokia", 99, 60), ("oppo", 250, 74), ("galaxy", 450, 85), ("xperia", 380, 79))),
    ("hotels", "likes", 150, 2, (("cabin", 120, 82), ("hut", 50, 66), ("dorm", 40, 60), ("plaza", 350, 97))),
    ("games", "likes", 15, 3, (("pong", 5, 300), ("snake", 3, 450), ("tetris", 10, 700), ("chess", 15, 650), ("zelda", 60, 980))),
    ("products", "score", 12, 3, (("pen", 3, 12), ("cap", 9, 27), ("mug", 12, 40), ("tee", 11, 35), ("bag", 45, 80))),
    ("books", "likes", 12, 3, (("dune", 12, 540), ("emma", 8, 310), ("carrie", 9, 420), ("misery", 11, 380), ("it", 18, 700), ("odyssey", 10, 600))),
)

TOP_PAGE = _page(
    "js-data-top", 187, "Working with data: filter, sort, slice, map",
    "Most reports are four steps in a row: keep the rows that qualify, put "
    "them in order, take the first few, and turn each into a line. Each "
    "array method returns a new array, so the next method can be called "
    "straight on it, one step per line. Order matters: filtering first "
    "means the sort has less to do, and slicing after the sort is what "
    "makes the first three the best three. filter already made a copy, so "
    "sorting it in place damages nothing. map's second argument is the "
    "position, which is where the 1. 2. 3. comes from.",
    "products.filter((p) => p.price <= 50).sort((a, b) => b.score - "
    "a.score).slice(0, 3).map((p, i) => `${i + 1}. ${p.name}`)",
    "js_data_top",
    tuple(
        (f"Given {v} {_desc(_objs(('name', 'price', f), rows))}, keep those "
         f"with price at most {budget}, sort by {f} highest first, take the "
         f"top {n}, and print each on its own line as its rank, a dot, a "
         f"space, the name, then the {f} in parentheses.",
         {"var": v, "field": f, "budget": budget, "n": n,
          "items": _objs(("name", "price", f), rows)})
        for v, f, budget, n, rows in _TOPS
    ),
)


JS11_PAGES: tuple[Page, ...] = (
    FIND_PAGE,
    SOME_EVERY_PAGE,
    SUM_PAGE,
    MAX_PAGE,
    TALLY_PAGE,
    GROUP_PAGE,
    SORT_PAGE,
    FORMAT_PAGE,
    ENTRIES_PAGE,
    TOP_PAGE,
)
