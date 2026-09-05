"""SQL workbook shapes.

SQL does not print, it returns rows — so the reference "program" is a query
and the expected output is the table the runner draws from the result. The
runner already exists for the SQL lessons; this reuses it, and reuses its
schema, so the workbook queries the same two tables the rest of the app
does.

The expected output is worked out *in Python*, from a hand-written mirror of
the same rows, and then rendered with the runner's own table formatter. That
matters. Computing it by running the query would make every test tautological
— the query compared against itself — and would pass just as happily if the
query were wrong. Filtering a list of tuples in Python and asking SQLite to
execute a SELECT are genuinely different implementations, so agreeing means
something.

The dataset is small and fixed, so the variety across twenty exercises comes
from the predicates rather than the data: cities, ages, the inactive row, the
two users with no email, the price bands.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape
from code_coach.sql_runner import _as_table

LANGUAGES: tuple[str, ...] = ("sql",)

SHAPES: tuple[Shape, ...] = (
    Shape("sql_select", "choosing columns rather than taking them all"),
    Shape("sql_where", "keeping only the rows that qualify"),
    Shape("sql_order", "putting the answer in an order you chose"),
    Shape("sql_limit", "asking for only the first few"),
    Shape("sql_aggregate", "one number out of many rows"),
    Shape("sql_group", "one row out per group in"),
    Shape("sql_having", "filtering the groups, not the rows"),
    Shape("sql_join", "two tables matched on a shared column"),
    Shape("sql_left_join", "keeping the rows with nothing to match"),
    Shape("sql_distinct_in", "no repeats, and a list of allowed values"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── The same rows the runner loads, as Python ────────────────
#
# Written out rather than read back from SQLite on purpose: this is the
# independent half of the check. If these ever drift from the runner's
# SCHEMA the tests fail, which is the point.

USERS: tuple[tuple, ...] = (
    (1, "Alex", "Denver", 30, "alex@example.com", 1),
    (2, "Bailey", "Austin", 24, None, 1),
    (3, "Casey", "Denver", 41, "casey@example.com", 0),
    (4, "Devon", "Boston", 17, "devon@example.com", 1),
    (5, "Erin", "Austin", 35, None, 1),
)
USER_COLS = ("id", "name", "city", "age", "email", "active")

ORDERS: tuple[tuple, ...] = (
    (1, 1, "keyboard", 45.00),
    (2, 1, "mouse", 18.50),
    (3, 2, "monitor", 180.00),
    (4, 3, "cable", 7.25),
    (5, 5, "desk", 220.00),
    (6, 5, "lamp", 32.00),
)
ORDER_COLS = ("id", "user_id", "item", "price")


def _user(row: tuple) -> dict:
    return dict(zip(USER_COLS, row))


def _order(row: tuple) -> dict:
    return dict(zip(ORDER_COLS, row))


def _keep(rows, where: str):
    """Apply one of the page's predicates, written as Python rather than
    handed to SQLite — the whole point of the independent side."""
    return [r for r in rows if _TESTS[where](r)]


#: Every predicate a page may use, by the name the content refers to. Adding
#: a page means adding its test here, which is deliberate: a predicate that
#: exists only as a SQL string could never be checked against anything.
_TESTS = {
    "city_denver": lambda r: r["city"] == "Denver",
    "city_austin": lambda r: r["city"] == "Austin",
    "city_boston": lambda r: r["city"] == "Boston",
    "age_over_25": lambda r: r["age"] > 25,
    "age_over_30": lambda r: r["age"] > 30,
    "age_under_25": lambda r: r["age"] < 25,
    "age_at_least_35": lambda r: r["age"] >= 35,
    "active": lambda r: r["active"] == 1,
    "inactive": lambda r: r["active"] == 0,
    "no_email": lambda r: r["email"] is None,
    "has_email": lambda r: r["email"] is not None,
    "price_over_40": lambda r: r["price"] > 40,
    "price_under_50": lambda r: r["price"] < 50,
    "price_over_100": lambda r: r["price"] > 100,
    "price_under_20": lambda r: r["price"] < 20,
}

#: The SQL each predicate becomes.
_WHERE_SQL = {
    "city_denver": "city = 'Denver'",
    "city_austin": "city = 'Austin'",
    "city_boston": "city = 'Boston'",
    "age_over_25": "age > 25",
    "age_over_30": "age > 30",
    "age_under_25": "age < 25",
    "age_at_least_35": "age >= 35",
    "active": "active = 1",
    "inactive": "active = 0",
    "no_email": "email IS NULL",
    "has_email": "email IS NOT NULL",
    "price_over_40": "price > 40",
    "price_under_50": "price < 50",
    "price_over_100": "price > 100",
    "price_under_20": "price < 20",
}

#: What each predicate reads as in a prompt.
WHERE_WORDS = {
    "city_denver": "live in Denver",
    "city_austin": "live in Austin",
    "city_boston": "live in Boston",
    "age_over_25": "are over 25",
    "age_over_30": "are over 30",
    "age_under_25": "are under 25",
    "age_at_least_35": "are 35 or older",
    "active": "are active",
    "inactive": "are not active",
    "no_email": "have no email",
    "has_email": "have an email",
    "price_over_40": "cost more than 40",
    "price_under_50": "cost less than 50",
    "price_over_100": "cost more than 100",
    "price_under_20": "cost less than 20",
}


def _table(columns, rows) -> str:
    return _as_table(list(columns), [tuple(r) for r in rows])


def _render(columns, dicts) -> str:
    return _table(columns, [[d[c] for c in columns] for d in dicts])


# ── The queries ──────────────────────────────────────────────


def _select(a: dict) -> str:
    return f"SELECT {', '.join(a['columns'])} FROM users;"


def _where(a: dict) -> str:
    return (
        f"SELECT {', '.join(a['columns'])} FROM users\n"
        f"WHERE {_WHERE_SQL[a['where']]};"
    )


def _order_by(a: dict) -> str:
    # Not _order: that name is already the orders-row helper above, and
    # defining it twice silently replaced the helper — every page then
    # failed with a tuple being indexed by a column name.
    return (
        f"SELECT {', '.join(a['columns'])} FROM users\n"
        f"ORDER BY {a['by']}{' DESC' if a['desc'] else ''};"
    )


def _limit(a: dict) -> str:
    return (
        f"SELECT {', '.join(a['columns'])} FROM users\n"
        f"ORDER BY {a['by']}{' DESC' if a['desc'] else ''}\n"
        f"LIMIT {a['count']};"
    )


def _aggregate(a: dict) -> str:
    where = _WHERE_SQL.get(a["where"])
    tail = f"\nWHERE {where}" if where else ""
    return f"SELECT {a['agg']}({a['column']}) FROM {a['table']}{tail};"


def _group(a: dict) -> str:
    return (
        f"SELECT {a['by']}, {a['agg']}({a['column']})\n"
        f"FROM {a['table']}\n"
        f"GROUP BY {a['by']}\n"
        f"ORDER BY {a['by']};"
    )


def _having(a: dict) -> str:
    return (
        f"SELECT {a['by']}, COUNT(*)\n"
        f"FROM {a['table']}\n"
        f"GROUP BY {a['by']}\n"
        f"HAVING COUNT(*) {a['test']}\n"
        f"ORDER BY {a['by']};"
    )


def _join(a: dict) -> str:
    return (
        "SELECT users.name, orders.item, orders.price\n"
        "FROM users\n"
        "JOIN orders ON orders.user_id = users.id\n"
        + (f"WHERE {_WHERE_SQL[a['where']]}\n" if a["where"] else "")
        + f"ORDER BY {a['by']};"
    )


def _left_join(a: dict) -> str:
    return (
        f"SELECT {a['by']}, {a['shown']}\n"
        "FROM users\n"
        "LEFT JOIN orders ON orders.user_id = users.id\n"
        f"GROUP BY {a['by']}\n"
        f"ORDER BY {a['by']}{' DESC' if a['desc'] else ''};"
    )


def _distinct_in(a: dict) -> str:
    values = ", ".join(f"'{v}'" for v in a["values"])
    return (
        f"SELECT DISTINCT {a['column']} FROM {a['table']}\n"
        f"WHERE {a['column']} IN ({values})\n"
        f"ORDER BY {a['column']};"
    )


_BUILDERS = {
    "sql_select": _select,
    "sql_where": _where,
    "sql_order": _order_by,
    "sql_limit": _limit,
    "sql_aggregate": _aggregate,
    "sql_group": _group,
    "sql_having": _having,
    "sql_join": _join,
    "sql_left_join": _left_join,
    "sql_distinct_in": _distinct_in,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def _sorted_by(dicts, by: str, desc: bool):
    """SQLite's ORDER BY, close enough for this data: no NULLs are ordered
    on any of these pages, so the NULLs-first rule never comes up."""
    return sorted(dicts, key=lambda d: d[by], reverse=desc)


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    users = [_user(r) for r in USERS]
    orders = [_order(r) for r in ORDERS]

    if shape == "sql_select":
        body = _render(a["columns"], users)
    elif shape == "sql_where":
        kept = _keep(users, a["where"])
        if not kept:
            raise ValueError("the filter must keep at least one row")
        if len(kept) == len(users):
            raise ValueError("the filter must leave something out")
        body = _render(a["columns"], kept)
    elif shape == "sql_order":
        ordered = _sorted_by(users, a["by"], a["desc"])
        if [d["id"] for d in ordered] == [d["id"] for d in users]:
            raise ValueError("the order must differ from the stored order")
        body = _render(a["columns"], ordered)
    elif shape == "sql_limit":
        ordered = _sorted_by(users, a["by"], a["desc"])[: a["count"]]
        if a["count"] >= len(users):
            raise ValueError("the limit must cut something off")
        body = _render(a["columns"], ordered)
    elif shape == "sql_aggregate":
        rows = users if a["table"] == "users" else orders
        if a["where"]:
            rows = _keep(rows, a["where"])
        if not rows:
            raise ValueError("the aggregate must have rows to work on")
        # if/elif rather than a dict of the five answers: a dict literal
        # evaluates every branch before picking one, so COUNT(*) tried to
        # sum a list of rows and died.
        agg = a["agg"]
        if agg == "COUNT":
            answer = len(rows)
        else:
            values = [r[a["column"]] for r in rows]
            if agg == "SUM":
                answer = sum(values)
            elif agg == "AVG":
                answer = sum(values) / len(values)
            elif agg == "MIN":
                answer = min(values)
            else:
                answer = max(values)
        label = f"{a['agg']}({a['column']})"
        body = _table([label], [(answer,)])
    elif shape == "sql_group":
        rows = users if a["table"] == "users" else orders
        groups: dict = {}
        for r in rows:
            groups.setdefault(r[a["by"]], []).append(r)
        if len(groups) < 2:
            raise ValueError("grouping needs more than one group")
        if len(groups) == len(rows):
            raise ValueError("every group of one shows nothing about grouping")
        out = []
        for key in sorted(groups):
            members = groups[key]
            agg = a["agg"]
            if agg == "COUNT":
                answer = len(members)
            else:
                vals = [m[a["column"]] for m in members]
                answer = {"SUM": sum, "MIN": min, "MAX": max}[agg](vals)
            out.append((key, answer))
        body = _table([a["by"], f"{a['agg']}({a['column']})"], out)
    elif shape == "sql_having":
        rows = users if a["table"] == "users" else orders
        groups = {}
        for r in rows:
            groups.setdefault(r[a["by"]], []).append(r)
        keep = [(k, len(v)) for k, v in sorted(groups.items())
                if _HAVING[a["test"]](len(v))]
        if not keep:
            raise ValueError("HAVING must keep at least one group")
        if len(keep) == len(groups):
            raise ValueError("HAVING must drop at least one group")
        body = _table([a["by"], "COUNT(*)"], keep)
    elif shape == "sql_join":
        joined = [
            {"name": u["name"], "item": o["item"], "price": o["price"],
             **{k: u[k] for k in USER_COLS}}
            for o in orders for u in users if u["id"] == o["user_id"]
        ]
        if a["where"]:
            joined = _keep(joined, a["where"])
        if not joined:
            raise ValueError("the join must match something")
        by = a["by"].split(".")[-1]
        joined = sorted(joined, key=lambda d: d[by])
        body = _table(["name", "item", "price"],
                      [(d["name"], d["item"], d["price"]) for d in joined])
    elif shape == "sql_left_join":
        key = a["by"].split(".")[-1]
        groups: dict = {}
        for u in users:
            groups.setdefault(u[key], []).extend(
                o for o in orders if o["user_id"] == u["id"]
            )
        agg = a["shown"].split("(")[0]
        out = []
        for value in sorted(groups, reverse=a["desc"]):
            prices = [o["price"] for o in groups[value]]
            if agg == "COUNT":
                answer = len(prices)
            elif not prices:
                # SUM, MIN, MAX and AVG of nothing are all NULL. COUNT of
                # nothing is 0, and that difference is the page.
                answer = None
            elif agg == "SUM":
                answer = sum(prices)
            elif agg == "MIN":
                answer = min(prices)
            elif agg == "MAX":
                answer = max(prices)
            else:
                answer = sum(prices) / len(prices)
            out.append((value, answer))
        if all(v for _, v in out):
            raise ValueError(
                "someone must have no orders, or the left join is a plain join"
            )
        body = _table([key, a["shown"]], out)
    elif shape == "sql_distinct_in":
        rows = users if a["table"] == "users" else orders
        vals = sorted({r[a["column"]] for r in rows
                       if r[a["column"]] in a["values"]})
        if not vals:
            raise ValueError("the IN list must match something")
        if len(vals) == len(a["values"]):
            raise ValueError("the IN list must name something that is absent")
        body = _table([a["column"]], [(v,) for v in vals])
    else:
        raise KeyError(shape)
    return body + NL


_HAVING = {
    "> 1": lambda n: n > 1,
    ">= 2": lambda n: n >= 2,
    ">= 3": lambda n: n >= 3,
    "= 1": lambda n: n == 1,
    "!= 1": lambda n: n != 1,
    "< 2": lambda n: n < 2,
    "<= 1": lambda n: n <= 1,
    "> 2": lambda n: n > 2,
}
