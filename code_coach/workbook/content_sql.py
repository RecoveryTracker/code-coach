"""SQL pages 1-10: the workbook's first language that does not print.

SQL answers with rows rather than lines, so an exercise here is a query and
the answer is the table underneath it. Everything else is the same: one idea
a page, twenty goes at it, and the answer is checked by running it.

The two tables are the ones the SQL lessons already use, so nothing new has
to be learned to start:

    users(id, name, city, age, email, active)   5 rows
    orders(id, user_id, item, price)            6 rows

Small on purpose. You can hold five users in your head, which means you can
predict what a query should return before you run it — and predicting, then
checking, is the whole exercise.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.emit_sql import WHERE_WORDS

SQL = ("sql",)


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
        languages=SQL,
        tier="beginner",
    )


def _cols(columns) -> str:
    return ", ".join(columns)


# ── 1. Choosing columns ──────────────────────────────────────

_SELECTS = (
    ("name",), ("name", "city"), ("id", "name"), ("name", "age"),
    ("city",), ("name", "email"), ("id", "city"), ("name", "active"),
    ("age",), ("id", "age"), ("city", "age"), ("name", "city", "age"),
    ("email",), ("id", "name", "city"), ("active",), ("name", "id"),
    ("city", "name"), ("age", "name"), ("id", "email"), ("name", "age", "city"),
)

_P1 = _page(
    "sql-select",
    1,
    "Choosing columns rather than taking them all",
    "SELECT, and naming the columns you actually want.",
    "SELECT * is convenient and it is the habit worth not forming. Naming "
    "the columns says what the query is for, survives someone adding a "
    "column to the table, and moves less data. The order you name them in "
    "is the order they come back in — the table does not decide that, you "
    "do.",
    "sql_select",
    [
        (
            f"Select {_cols(columns)} from users, in that order.",
            {"columns": columns},
        )
        for columns in _SELECTS
    ],
)


# ── 2. Keeping only the rows that qualify ────────────────────

_WHERES = (
    (("name", "city"), "city_denver"),
    (("name", "city"), "city_austin"),
    (("name", "age"), "age_over_25"),
    (("name", "age"), "age_over_30"),
    (("name", "age"), "age_under_25"),
    (("name", "age"), "age_at_least_35"),
    (("name", "active"), "active"),
    (("name", "active"), "inactive"),
    (("name", "email"), "no_email"),
    (("name", "email"), "has_email"),
    (("id", "name"), "city_boston"),
    (("name", "city", "age"), "city_denver"),
    (("name", "city", "age"), "age_over_30"),
    (("id", "name", "age"), "age_under_25"),
    (("name",), "no_email"),
    (("name",), "inactive"),
    (("id", "city"), "city_austin"),
    (("name", "age", "city"), "age_at_least_35"),
    (("id", "name", "email"), "has_email"),
    (("name", "city"), "city_boston"),
)

_P2 = _page(
    "sql-where",
    2,
    "Keeping only the rows that qualify",
    "WHERE, and what IS NULL is for.",
    "WHERE runs once per row and keeps the ones it says yes to. The trap is "
    "on the email column: NULL is not a value, it is the absence of one, so "
    "`email = NULL` is neither true nor false and matches nothing at all. "
    "IS NULL is the only thing that works, and it is the first SQL surprise "
    "everyone meets.",
    "sql_where",
    [
        (
            f"Select {_cols(columns)} from users, for the ones that "
            f"{WHERE_WORDS[where]}.",
            {"columns": columns, "where": where},
        )
        for columns, where in _WHERES
    ],
)


# ── 3. Putting the answer in an order ────────────────────────

_ORDERS = (
    (('name', 'age'), 'age', False),
    (('name', 'age'), 'age', True),
    (('name', 'age'), 'city', False),
    (('name', 'age'), 'city', True),
    (('name', 'age'), 'name', True),
    (('name', 'age'), 'id', True),
    (('name', 'city'), 'age', False),
    (('name', 'city'), 'age', True),
    (('name', 'city'), 'city', False),
    (('name', 'city'), 'city', True),
    (('name', 'city'), 'name', True),
    (('name', 'city'), 'id', True),
    (('id', 'name'), 'age', False),
    (('id', 'name'), 'age', True),
    (('id', 'name'), 'city', False),
    (('id', 'name'), 'city', True),
    (('id', 'name'), 'name', True),
    (('id', 'name'), 'id', True),
    (('name',), 'age', False),
    (('name',), 'age', True),
)

_P3 = _page(
    "sql-order",
    3,
    "Putting the answer in an order you chose",
    "ORDER BY, and why you cannot skip it and hope.",
    "Rows come back in whatever order the database found convenient. It may "
    "look like insertion order today and change tomorrow when an index is "
    "added — nothing promises anything until you say ORDER BY. If the order "
    "matters, ask for it; if it does not, do not pay for it.",
    "sql_order",
    [
        (
            f"Select {_cols(columns)} from users, ordered by {by}"
            + (" from highest to lowest." if desc else " from lowest to highest."),
            {"columns": columns, "by": by, "desc": desc},
        )
        for columns, by, desc in _ORDERS
    ],
)


# ── 4. Only the first few ────────────────────────────────────

_LIMITS = (
    (("name", "age"), "age", True, 2),
    (("name", "age"), "age", False, 2),
    (("name", "age"), "age", True, 3),
    (("name", "city"), "name", False, 2),
    (("name",), "name", True, 1),
    (("id", "name"), "id", True, 3),
    (("name", "age"), "age", False, 1),
    (("name", "city"), "city", False, 3),
    (("id", "age"), "age", True, 2),
    (("name", "email"), "name", False, 4),
    (("name", "age", "city"), "age", True, 1),
    (("city", "name"), "city", True, 2),
    (("name", "active"), "name", False, 3),
    (("id", "name", "age"), "age", False, 2),
    (("name",), "name", False, 2),
    (("age", "name"), "age", True, 4),
    (("id", "city"), "id", False, 3),
    (("name", "city"), "name", True, 1),
    (("name", "age"), "name", True, 4),
    (("id", "name", "city"), "id", True, 2),
)

_P4 = _page(
    "sql-limit",
    4,
    "Asking for only the first few",
    "LIMIT, and why it only means anything after ORDER BY.",
    "LIMIT without ORDER BY gives you some rows — not the first, not the "
    "best, just some, and possibly different ones next time. The two go "
    "together: order it, then take the top few. That pair is how every "
    "top-ten list in every application is written.",
    "sql_limit",
    [
        (
            f"Select {_cols(columns)} from users ordered by {by} "
            + ("descending" if desc else "ascending")
            + f", and take only the first {count}.",
            {"columns": columns, "by": by, "desc": desc, "count": count},
        )
        for columns, by, desc, count in _LIMITS
    ],
)


# ── 5. One number out of many rows ───────────────────────────

_AGGREGATES = (
    ("users", "COUNT", "*", None),
    ("users", "AVG", "age", None),
    ("users", "MIN", "age", None),
    ("users", "MAX", "age", None),
    ("users", "SUM", "age", None),
    ("orders", "COUNT", "*", None),
    ("orders", "SUM", "price", None),
    ("orders", "MIN", "price", None),
    ("orders", "MAX", "price", None),
    ("orders", "AVG", "price", None),
    ("users", "COUNT", "*", "city_denver"),
    ("users", "COUNT", "*", "active"),
    ("users", "MAX", "age", "city_austin"),
    ("users", "MIN", "age", "active"),
    ("users", "AVG", "age", "has_email"),
    ("orders", "COUNT", "*", "price_over_40"),
    ("orders", "SUM", "price", "price_under_50"),
    ("orders", "MAX", "price", "price_over_40"),
    ("orders", "MIN", "price", "price_over_40"),
    ("orders", "AVG", "price", "price_under_50"),
)

_P5 = _page(
    "sql-aggregate",
    5,
    "One number out of many rows",
    "COUNT, SUM, MIN, MAX and AVG — many rows in, one row out.",
    "An aggregate collapses the whole result into a single value, which is "
    "why you cannot ask for a plain column beside it — there is no one row "
    "for it to come from. COUNT(*) counts rows; COUNT(column) counts rows "
    "where that column is not NULL, and the difference between those two "
    "is a question worth asking of the email column.",
    "sql_aggregate",
    [
        (
            f"From {table}, get the {agg} of {column}"
            + (f", for the rows that {WHERE_WORDS[where]}." if where else "."),
            {"table": table, "agg": agg, "column": column, "where": where},
        )
        for table, agg, column, where in _AGGREGATES
    ],
)


# ── 6. One row out per group in ──────────────────────────────

_GROUPS = (
    ('users', 'city', 'COUNT', '*'),
    ('users', 'city', 'MAX', 'age'),
    ('users', 'city', 'MAX', 'id'),
    ('users', 'city', 'MIN', 'age'),
    ('users', 'city', 'MIN', 'id'),
    ('users', 'city', 'SUM', 'age'),
    ('users', 'city', 'SUM', 'id'),
    ('users', 'active', 'COUNT', '*'),
    ('users', 'active', 'MAX', 'age'),
    ('users', 'active', 'MAX', 'id'),
    ('users', 'active', 'MIN', 'age'),
    ('users', 'active', 'MIN', 'id'),
    ('users', 'active', 'SUM', 'age'),
    ('users', 'active', 'SUM', 'id'),
    ('orders', 'user_id', 'COUNT', '*'),
    ('orders', 'user_id', 'MAX', 'id'),
    ('orders', 'user_id', 'MAX', 'price'),
    ('orders', 'user_id', 'MIN', 'id'),
    ('orders', 'user_id', 'MIN', 'price'),
    ('orders', 'user_id', 'SUM', 'id'),
)

_P6 = _page(
    "sql-group",
    6,
    "One row out per group in",
    "GROUP BY, and the rule about what may sit beside the aggregate.",
    "GROUP BY splits the rows into piles by a value, then runs the "
    "aggregate on each pile. The rule that follows from that: the only "
    "columns you may select are the ones you grouped by, and aggregates. "
    "Anything else has many possible values per pile and no reason to "
    "prefer one — SQLite will hand you an arbitrary one, and other "
    "databases refuse outright.",
    "sql_group",
    [
        (
            f"From {table}, group by {by} and give the {agg} of {column} for "
            f"each group, ordered by {by}.",
            {"table": table, "by": by, "agg": agg, "column": column},
        )
        for table, by, agg, column in _GROUPS
    ],
)


# ── 7. Filtering the groups ──────────────────────────────────

_HAVINGS = (
    ("users", "city", "> 1"),
    ("users", "city", ">= 2"),
    ("users", "city", "= 1"),
    ("users", "city", "< 2"),
    ("users", "city", "<= 1"),
    ("users", "city", "!= 1"),
    ("users", "active", "> 1"),
    ("users", "active", ">= 2"),
    ("users", "active", "= 1"),
    ("users", "active", "< 2"),
    ("users", "active", "<= 1"),
    ("users", "active", "!= 1"),
    ("users", "active", "> 2"),
    ("users", "active", ">= 3"),
    ("orders", "user_id", "> 1"),
    ("orders", "user_id", ">= 2"),
    ("orders", "user_id", "= 1"),
    ("orders", "user_id", "< 2"),
    ("orders", "user_id", "<= 1"),
    ("orders", "user_id", "!= 1"),
)

_P7 = _page(
    "sql-having",
    7,
    "Filtering the groups, not the rows",
    "HAVING, which runs after the grouping. WHERE runs before it.",
    "This is the distinction people get wrong for years. WHERE decides "
    "which rows go into the piles; HAVING decides which piles survive. So "
    "you cannot put COUNT(*) in a WHERE — at that point nothing has been "
    "counted yet — and you would not put a plain column test in a HAVING, "
    "because filtering rows after grouping them is work you did not need "
    "to do.",
    "sql_having",
    [
        (
            f"From {table}, group by {by} and keep only the groups whose "
            f"count is {test}. Show {by} and the count, ordered by {by}.",
            {"table": table, "by": by, "test": test},
        )
        for table, by, test in _HAVINGS
    ],
)


# ── 8. Two tables matched ────────────────────────────────────

_JOINS = (
    (None, 'users.name'),
    (None, 'orders.price'),
    (None, 'orders.item'),
    ('city_denver', 'users.name'),
    ('city_denver', 'orders.price'),
    ('city_denver', 'orders.item'),
    ('city_austin', 'users.name'),
    ('city_austin', 'orders.price'),
    ('city_austin', 'orders.item'),
    ('active', 'users.name'),
    ('active', 'orders.price'),
    ('active', 'orders.item'),
    ('price_over_40', 'users.name'),
    ('price_over_40', 'orders.price'),
    ('price_over_40', 'orders.item'),
    ('price_under_50', 'users.name'),
    ('price_under_50', 'orders.price'),
    ('price_under_50', 'orders.item'),
    ('price_over_100', 'users.name'),
    ('price_over_100', 'orders.price'),
)

_P8 = _page(
    "sql-join",
    8,
    "Two tables matched on a shared column",
    "JOIN ... ON, and the column that connects them.",
    "The ON is the whole join: it says which row over here belongs with "
    "which row over there. Leave it out and you get every combination of "
    "every row with every other — five users and six orders is thirty rows "
    "of nonsense, and on real tables it is how a query brings a server "
    "down. Note that a user with no orders does not appear at all, which "
    "is the next page.",
    "sql_join",
    [
        (
            "Join users to orders on the user id and show the name, item "
            "and price"
            + (f", for the ones that {WHERE_WORDS[where]}" if where else "")
            + f", ordered by {by}.",
            {"where": where, "by": by},
        )
        for where, by in _JOINS
    ],
)


# ── 9. Keeping the rows with nothing to match ────────────────

_LEFT = tuple(
    (agg, by, desc)
    for agg in (
        "COUNT(orders.id)",
        "SUM(orders.price)",
        "MIN(orders.price)",
        "MAX(orders.price)",
        "AVG(orders.price)",
    )
    for by in ("users.name", "users.city")
    for desc in (False, True)
)

_P9 = _page(
    "sql-left-join",
    9,
    "Keeping the rows with nothing to match",
    "LEFT JOIN, and what shows up for the ones with nothing on the right.",
    "A plain join silently drops anything unmatched, which is exactly the "
    "bug you do not notice — the query runs, the numbers look plausible, "
    "and two customers are missing. A LEFT JOIN keeps every row on the "
    "left and fills the right with NULLs. Notice what that does to the "
    "aggregates below: COUNT of a NULL column is 0, and SUM of nothing is "
    "NULL, not 0.",
    "sql_left_join",
    [
        (
            f"Left join users to orders and show {by} with {shown}, grouped "
            f"by {by} and ordered by it "
            + ("descending" if desc else "ascending")
            + ". Everyone should appear, including anyone with no orders.",
            {"shown": shown, "by": by, "desc": desc},
        )
        for shown, by, desc in _LEFT
    ],
)


# ── 10. No repeats, and a list of allowed values ─────────────

_DISTINCT = (
    ("users", "city", ("Denver", "Austin", "Portland")),
    ("users", "city", ("Denver", "Boston", "Seattle")),
    ("users", "city", ("Austin", "Boston", "Chicago")),
    ("orders", "item", ("keyboard", "mouse", "webcam")),
    ("orders", "item", ("desk", "lamp", "chair")),
    ("orders", "item", ("monitor", "cable", "dock")),
    ("users", "city", ("Denver", "Miami")),
    ("users", "city", ("Austin", "Dallas")),
    ("orders", "item", ("cable", "adapter")),
    ("orders", "item", ("desk", "shelf")),
    ("users", "city", ("Boston", "Denver", "Reno")),
    ("orders", "item", ("lamp", "mouse", "hub")),
    ("users", "city", ("Austin", "Denver", "Tulsa")),
    ("orders", "item", ("keyboard", "monitor", "stand")),
    ("users", "city", ("Boston", "Austin", "Fargo")),
    ("orders", "item", ("mouse", "cable", "riser")),
    ("users", "city", ("Denver", "Austin", "Boise")),
    ("orders", "item", ("desk", "monitor", "tray")),
    ("users", "city", ("Boston", "Austin", "Omaha")),
    ("orders", "item", ("lamp", "keyboard", "mat")),
)

_P10 = _page(
    "sql-distinct-in",
    10,
    "No repeats, and a list of allowed values",
    "DISTINCT, and IN as a shorter way to write several ORs.",
    "IN is a list of ORs with less typing, and it does not mind naming "
    "something that is not there — every one of these asks for a value the "
    "table does not have, and the query is perfectly happy. DISTINCT then "
    "collapses the repeats. Worth knowing that DISTINCT usually means a "
    "sort or a hash behind the scenes, so it is not free on a large table.",
    "sql_distinct_in",
    [
        (
            f"From {table}, get the distinct {column} values that are one of "
            + ", ".join(values)
            + f", ordered by {column}.",
            {"table": table, "column": column, "values": values},
        )
        for table, column, values in _DISTINCT
    ],
)


SQL_PAGES: tuple[Page, ...] = (
    _P1, _P2, _P3, _P4, _P5, _P6, _P7, _P8, _P9, _P10,
)
