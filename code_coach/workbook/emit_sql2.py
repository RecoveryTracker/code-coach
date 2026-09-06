"""SQL past the fundamentals.

The first ten SQL pages covered SELECT through JOIN, which is the shape of
every introduction, and stopped exactly where SQL starts being the reason
people reach for SQL. No CASE, no subquery, no EXISTS, no UNION, no CTE,
and no window functions, which is most of the second half of the language.

Ten more pages, in the order the ideas need each other: pattern and range
predicates, CASE, how NULL behaves, a subquery, EXISTS, a table joined to
itself, UNION, a CTE to give a subquery a name, and then the two window
pages, which are the payoff — they answer a question about a group without
collapsing the group, which nothing before them can do.

The rule from the first ten holds and is the whole game. The expected table
is worked out in Python from a hand-written mirror of the same rows, never
by running the query. Running it would compare the query against itself and
pass just as happily if it were wrong.

Every shape takes arguments that change the rows it returns. That is not
decoration: a page whose twenty exercises are one query repeated twenty
times is not repetition, it is a single exercise with a copy-paste problem.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape
from code_coach.workbook.emit_sql import (
    ORDERS,
    USERS,
    _order,
    _render,
    _table,
    _user,
)

LANGUAGES: tuple[str, ...] = ("sql",)

SHAPES: tuple[Shape, ...] = (
    Shape("sql_like", "matching a shape, and falling in a range"),
    Shape("sql_case", "a column that depends on the row"),
    Shape("sql_null", "the value that is not a value"),
    Shape("sql_subquery", "a query inside a query"),
    Shape("sql_exists", "asking whether anything matches"),
    Shape("sql_self_join", "a table joined to itself"),
    Shape("sql_union", "two results stacked into one"),
    Shape("sql_cte", "naming a query so the next one can read"),
    Shape("sql_window", "a number per row, worked out over a group"),
    Shape("sql_running", "a total that grows as the rows go by"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

NEWLINE = "\n"


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _q(*lines: str) -> str:
    return NEWLINE.join(lines)


# ── 11. LIKE and BETWEEN ─────────────────────────────────────


def _like(a: dict) -> str:
    if a["want"] == "like":
        return _q(
            "SELECT name, city FROM users",
            f"WHERE name LIKE '{a['pattern']}'",
            "ORDER BY name;",
        )
    return _q(
        "SELECT name, age FROM users",
        f"WHERE age BETWEEN {a['low']} AND {a['high']}",
        "ORDER BY age;",
    )


# ── 12. CASE ─────────────────────────────────────────────────


def _case(a: dict) -> str:
    return _q(
        "SELECT name,",
        f"       CASE WHEN age < {a['cut']} THEN '{a['low']}'",
        f"            ELSE '{a['high']}' END AS band",
        "FROM users",
        "ORDER BY name;",
    )


# ── 13. NULL ─────────────────────────────────────────────────


def _null(a: dict) -> str:
    if a["want"] == "coalesce":
        return _q(
            f"SELECT name, COALESCE(email, '{a['fallback']}') AS email",
            "FROM users",
            "ORDER BY name;",
        )
    keep = "IS NULL" if a["want"] == "is_null" else "IS NOT NULL"
    return _q(
        f"SELECT {', '.join(a['cols'])} FROM users",
        f"WHERE email {keep}",
        "ORDER BY name;",
    )


# ── 14. Subquery ─────────────────────────────────────────────


def _subquery(a: dict) -> str:
    shift = ""
    if a["offset"]:
        sign = "+" if a["offset"] > 0 else "-"
        shift = f" {sign} {abs(a['offset'])}"
    return _q(
        "SELECT name, age FROM users",
        f"WHERE age {a['op']} (SELECT {a['agg']}(age) FROM users){shift}",
        "ORDER BY age;",
    )


# ── 15. EXISTS ───────────────────────────────────────────────


def _exists(a: dict) -> str:
    negate = "NOT " if a["want"] == "without" else ""
    floor = f" AND o.price > {a['over']}" if a["over"] is not None else ""
    return _q(
        "SELECT name FROM users u",
        f"WHERE {negate}EXISTS (",
        f"  SELECT 1 FROM orders o WHERE o.user_id = u.id{floor}",
        ")",
        "ORDER BY u.name;",
    )


# ── 16. Self join ────────────────────────────────────────────


def _self_join(a: dict) -> str:
    on = a["on"]
    lines = [
        f"SELECT a.name AS one, b.name AS two, a.{on}",
        "FROM users a",
        f"JOIN users b ON a.{on} = b.{on} AND a.id < b.id",
    ]
    if a["floor"]:
        lines.append(f"WHERE a.{a['floor_col']} > {a['floor']}")
    lines.append("ORDER BY a.name, b.name;")
    return _q(*lines)


# ── 17. UNION ────────────────────────────────────────────────


def _union(a: dict) -> str:
    kind = "UNION ALL" if a["want"] == "all" else "UNION"
    return _q(
        f"SELECT name FROM users WHERE city = '{a['city']}'",
        kind,
        f"SELECT name FROM users WHERE age > {a['age']}",
        "ORDER BY name;",
    )


# ── 18. CTE ──────────────────────────────────────────────────


def _cte(a: dict) -> str:
    return _q(
        "WITH spend AS (",
        "  SELECT user_id, SUM(price) AS total",
        "  FROM orders",
        "  GROUP BY user_id",
        ")",
        "SELECT u.name, s.total",
        "FROM spend s",
        "JOIN users u ON u.id = s.user_id",
        f"WHERE s.total {a['op']} {a['amount']}",
        "ORDER BY s.total DESC;",
    )


# ── 19. Window ───────────────────────────────────────────────


def _window(a: dict) -> str:
    direction = "DESC" if a["desc"] else "ASC"
    part = a["part"]
    lines = [
        f"SELECT name, {part},",
        "       ROW_NUMBER() OVER (",
        f"         PARTITION BY {part} ORDER BY {a['by']} {direction}",
        "       ) AS rn",
        "FROM users",
    ]
    if a["over"]:
        # The filter runs before the window, so the numbering is over what
        # survived it rather than over the whole table. That ordering is
        # the point of the row, not a detail of it.
        lines.append(f"WHERE age > {a['over']}")
    lines.append(f"ORDER BY {part}, rn;")
    return _q(*lines)


# ── 20. Running total ────────────────────────────────────────


def _running(a: dict) -> str:
    return _q(
        "SELECT item, price,",
        "       SUM(price) OVER (ORDER BY id) AS running",
        "FROM orders",
        f"WHERE price {a['op']} {a['amount']}",
        "ORDER BY id;",
    )


_BUILDERS = {
    "sql_like": _like,
    "sql_case": _case,
    "sql_null": _null,
    "sql_subquery": _subquery,
    "sql_exists": _exists,
    "sql_self_join": _self_join,
    "sql_union": _union,
    "sql_cte": _cte,
    "sql_window": _window,
    "sql_running": _running,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def _like_matches(name: str, pattern: str) -> bool:
    """SQL LIKE, for the two wildcards these pages use.

    Written out rather than handed to a regex, because the point of this
    file is that the expected answer comes from somewhere other than the
    engine under test.
    """
    low = name.lower()
    pat = pattern.lower()
    if pat.startswith("%") and pat.endswith("%") and len(pat) > 2:
        return pat[1:-1] in low
    if pat.startswith("%"):
        return low.endswith(pat[1:])
    if pat.endswith("%"):
        return low.startswith(pat[:-1])
    return low == pat


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out from the Python mirror of the rows, never by querying.

    The guards ask whether a query can be told apart from a simpler one. A
    LIKE that matches everybody is a SELECT. A UNION whose halves do not
    overlap prints what UNION ALL prints. A partition holding one row each
    makes ROW_NUMBER a column of ones.
    """
    a = args
    users = [_user(r) for r in USERS]
    orders = [_order(r) for r in ORDERS]

    if shape == "sql_like":
        if a["want"] == "like":
            kept = [u for u in users if _like_matches(u["name"], a["pattern"])]
            if not kept or len(kept) == len(users):
                raise ValueError(
                    "the pattern must match some and miss some, or it does "
                    "nothing a bare SELECT would not do"
                )
            kept.sort(key=lambda u: u["name"])
            return _render(("name", "city"), kept)
        low, high = a["low"], a["high"]
        if low >= high:
            raise ValueError("the range must have something in it")
        kept = [u for u in users if low <= u["age"] <= high]
        if not kept or len(kept) == len(users):
            raise ValueError("the range must keep some and drop some")
        kept.sort(key=lambda u: u["age"])
        return _render(("name", "age"), kept)

    if shape == "sql_case":
        cut, low, high = a["cut"], a["low"], a["high"]
        bands = [(u["name"], low if u["age"] < cut else high) for u in users]
        if len({b for _, b in bands}) < 2:
            raise ValueError(
                "the cut must put rows on both sides, or CASE is a constant"
            )
        bands.sort()
        return _table(("name", "band"), bands)

    if shape == "sql_null":
        if a["want"] == "coalesce":
            if all(u["email"] is not None for u in users):
                raise ValueError("nothing is null, so COALESCE does nothing")
            rows = [
                (u["name"],
                 u["email"] if u["email"] is not None else a["fallback"])
                for u in users
            ]
            rows.sort()
            return _table(("name", "email"), rows)
        want_null = a["want"] == "is_null"
        cols = tuple(a["cols"])
        if "name" not in cols:
            raise ValueError("the ordering column must be selected")
        kept = [u for u in users if (u["email"] is None) == want_null]
        if not kept or len(kept) == len(users):
            raise ValueError("the test must keep some and drop some")
        kept.sort(key=lambda u: u["name"])
        return _render(cols, kept)

    if shape == "sql_subquery":
        ages = [u["age"] for u in users]
        base = {"AVG": sum(ages) / len(ages), "MIN": min(ages),
                "MAX": max(ages)}[a["agg"]]
        mark = base + a["offset"]
        kept = [u for u in users
                if (u["age"] > mark if a["op"] == ">" else u["age"] < mark)]
        if not kept or len(kept) == len(users):
            raise ValueError("the comparison must split the rows")
        kept.sort(key=lambda u: u["age"])
        return _render(("name", "age"), kept)

    if shape == "sql_exists":
        over = a["over"]
        with_orders = {o["user_id"] for o in orders
                       if over is None or o["price"] > over}
        kept = [u for u in users
                if (u["id"] in with_orders) == (a["want"] == "with")]
        if not kept or len(kept) == len(users):
            raise ValueError(
                "both sides must be non-empty, or EXISTS decides nothing"
            )
        kept.sort(key=lambda u: u["name"])
        return _render(("name",), kept)

    if shape == "sql_self_join":
        on, floor, col = a["on"], a["floor"], a["floor_col"]
        rows = []
        for one in users:
            if floor and not one[col] > floor:
                continue
            for two in users:
                if one[on] == two[on] and one["id"] < two["id"]:
                    rows.append((one["name"], two["name"], one[on]))
        if not rows:
            raise ValueError(
                "no two remaining rows share the column, so the self join "
                "finds nothing and the page prints an empty table"
            )
        rows.sort(key=lambda r: (r[0], r[1]))
        return _table(("one", "two", on), rows)

    if shape == "sql_union":
        city, age = a["city"], a["age"]
        left = [u["name"] for u in users if u["city"] == city]
        right = [u["name"] for u in users if u["age"] > age]
        if not left or not right:
            raise ValueError("both halves must return something")
        if not set(left) & set(right):
            raise ValueError(
                "the halves must overlap, or UNION and UNION ALL print the "
                "same thing and the page shows nothing"
            )
        names = left + right if a["want"] == "all" else sorted(set(left + right))
        return _table(("name",), [(n,) for n in sorted(names)])

    if shape == "sql_cte":
        totals: dict = {}
        for o in orders:
            totals[o["user_id"]] = totals.get(o["user_id"], 0) + o["price"]
        op, amount = a["op"], a["amount"]
        by_id = {u["id"]: u["name"] for u in users}
        rows = [(by_id[uid], total) for uid, total in totals.items()
                if (total > amount if op == ">" else total < amount)]
        if not rows or len(rows) == len(totals):
            raise ValueError("the threshold must keep some and drop some")
        rows.sort(key=lambda r: -r[1])
        return _table(("name", "total"), rows)

    if shape == "sql_window":
        by, desc, part, over = a["by"], a["desc"], a["part"], a["over"]
        kept = [u for u in users if not over or u["age"] > over]
        if not kept:
            raise ValueError("the filter must leave rows to number")
        groups: dict = {}
        for u in kept:
            groups.setdefault(u[part], []).append(u)
        if max(len(v) for v in groups.values()) < 2:
            raise ValueError(
                "some partition must hold more than one row, or every row "
                "number is 1 and the window is decoration"
            )
        rows = []
        for key in sorted(groups):
            ranked = sorted(groups[key], key=lambda u: u[by], reverse=desc)
            for i, u in enumerate(ranked, start=1):
                rows.append((u["name"], u[part], i))
        return _table(("name", part, "rn"), rows)

    if shape == "sql_running":
        op, amount = a["op"], a["amount"]
        kept = [o for o in sorted(orders, key=lambda o: o["id"])
                if (o["price"] > amount if op == ">" else o["price"] < amount)]
        if len(kept) < 2:
            raise ValueError("a running total needs two rows to run over")
        if len(kept) == len(orders):
            raise ValueError("the filter must drop something")
        rows = []
        running = 0.0
        for o in kept:
            running += o["price"]
            rows.append((o["item"], o["price"], running))
        return _table(("item", "price", "running"), rows)

    raise KeyError(shape)


__all__ = [
    "NL", "SHAPES", "SHAPE_IDS", "expected_output", "handles", "solution",
]
