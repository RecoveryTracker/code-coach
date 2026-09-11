"""SQL pages 21-30: the parts people reach for once the basics are in.

Pages 1 to 10 were SELECT through JOIN. Pages 11 to 20 added CASE,
subqueries, EXISTS, UNION, CTEs and the two window pages. What is left is
the set of things that turn up in real queries and almost never in
tutorials: the other two set operators, the three ranking functions and
why they differ, the two that look at a neighbouring row, an aggregate
with a filter on it, string aggregation, casting, the two NULL helpers,
pagination, and a recursive CTE.

Every feature here was run against the database before a page was written
for it, because a page whose SQL the engine cannot execute is worse than
no page. The expected table is worked out in Python from the same
hand-written mirror of the rows the earlier SQL pages use, never by
running the query, which would compare it against itself.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape
from code_coach.workbook.emit_sql import ORDERS, USERS, _order, _table, _user

LANGUAGES: tuple[str, ...] = ("sql",)

SHAPES: tuple[Shape, ...] = (
    Shape("sql_setops", "what both have, and what only one has"),
    Shape("sql_ranks", "three ways to number, and what a tie does"),
    Shape("sql_neighbour", "the row before and the row after"),
    Shape("sql_ntile", "cutting the rows into equal groups"),
    Shape("sql_filter", "counting only some of what you counted"),
    Shape("sql_concat", "many rows into one string"),
    Shape("sql_cast", "a number treated as text"),
    Shape("sql_nulls", "supplying one, and making one"),
    Shape("sql_page", "the second page of results"),
    Shape("sql_recursive", "a query that calls itself"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _q(*lines: str) -> str:
    return NL.join(lines)


def _reader(column: str):
    """Read a column, or a remainder of one.

    The table has five rows and only `city` and `active` contain a tie,
    which is not enough to fill a page. `age % 5` makes as many ties as
    the page needs and is still a column expression SQLite can order by.
    """
    if "%" in column:
        name, _, divisor = column.partition("%")
        name, divisor = name.strip(), int(divisor)
        return lambda u: u[name] % divisor
    return lambda u: u[column]


# ── The queries ──────────────────────────────────────────────


def _setops(a: dict) -> str:
    return _q(
        "SELECT city FROM users",
        a["op"],
        f"SELECT city FROM users WHERE age > {a['age']}",
        "ORDER BY city;",
    )


def _ranks(a: dict) -> str:
    # ROW_NUMBER gets the name as a tiebreak and the other two do not, on
    # purpose. RANK and DENSE_RANK need the tie to still be a tie, or the
    # page shows nothing. ROW_NUMBER over a tie has to pick one of the two
    # arbitrarily, and which one is up to the database — so asking for an
    # exact answer without a tiebreak is asking for a guess.
    d = "DESC" if a["desc"] else "ASC"
    by = a["by"]
    return _q(
        "SELECT name,",
        f"       ROW_NUMBER() OVER (ORDER BY {by} {d}, name) AS rn,",
        f"       RANK() OVER (ORDER BY {by} {d}) AS rk,",
        f"       DENSE_RANK() OVER (ORDER BY {by} {d}) AS dr",
        "FROM users",
        f"ORDER BY {by} {d}, name;",
    )


def _neighbour(a: dict) -> str:
    over = a["over"]
    d = " DESC" if a["desc"] else ""
    return _q(
        "SELECT name,",
        f"       LAG({a['col']}) OVER (ORDER BY {over}{d}) AS before,",
        f"       LEAD({a['col']}) OVER (ORDER BY {over}{d}) AS after",
        "FROM users",
        f"ORDER BY {over}{d};",
    )


def _ntile(a: dict) -> str:
    # The name is a tiebreak, not part of the lesson: without one, which of
    # two equal rows lands in the earlier bucket is up to the database.
    by = a["by"]
    return _q(
        "SELECT name,",
        f"       NTILE({a['parts']}) OVER (ORDER BY {by}, name) AS part",
        "FROM users",
        f"ORDER BY {by}, name;",
    )


def _filter(a: dict) -> str:
    return _q(
        "SELECT COUNT(*) AS everyone,",
        f"       COUNT(*) FILTER (WHERE age > {a['age']}) AS older,",
        f"       SUM(age) FILTER (WHERE city = '{a['city']}') AS there",
        "FROM users;",
    )


def _concat(a: dict) -> str:
    return _q(
        f"SELECT {a['group']}, GROUP_CONCAT(name, '{a['sep']}') AS who",
        "FROM users",
        f"GROUP BY {a['group']}",
        f"ORDER BY {a['group']};",
    )


def _cast(a: dict) -> str:
    return _q(
        f"SELECT name, CAST(age AS TEXT) || '{a['tail']}' AS shown",
        "FROM users",
        f"WHERE age > {a['age']}",
        "ORDER BY name;",
    )


def _nulls(a: dict) -> str:
    return _q(
        "SELECT name,",
        f"       IFNULL(email, '{a['fallback']}') AS mail,",
        f"       NULLIF(city, '{a['blank']}') AS town",
        "FROM users",
        "ORDER BY name;",
    )


def _page(a: dict) -> str:
    return _q(
        "SELECT name, age FROM users",
        "ORDER BY age DESC",
        f"LIMIT {a['size']} OFFSET {a['skip']};",
    )


def _recursive(a: dict) -> str:
    return _q(
        "WITH RECURSIVE counted(x) AS (",
        f"  SELECT {a['start']}",
        "  UNION ALL",
        f"  SELECT x + {a['step']} FROM counted WHERE x < {a['stop']}",
        ")",
        "SELECT x FROM counted;",
    )


_BUILDERS = {
    "sql_setops": _setops,
    "sql_ranks": _ranks,
    "sql_neighbour": _neighbour,
    "sql_ntile": _ntile,
    "sql_filter": _filter,
    "sql_concat": _concat,
    "sql_cast": _cast,
    "sql_nulls": _nulls,
    "sql_page": _page,
    "sql_recursive": _recursive,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out from the Python mirror of the rows, never by querying.

    The guards ask the same question as the earlier SQL pages: could this
    data pass while showing nothing. A ranking page whose order column has
    no ties makes all three functions agree. A set operation whose halves
    do not overlap makes INTERSECT empty and EXCEPT the whole thing.
    """
    a = args
    users = [_user(r) for r in USERS]
    orders = [_order(r) for r in ORDERS]  # noqa: F841 - parity with emit_sql

    if shape == "sql_setops":
        age = a["age"]
        left = {u["city"] for u in users}
        right = {u["city"] for u in users if u["age"] > age}
        if not right or right == left:
            raise ValueError(
                "the right half must be a proper subset, or INTERSECT is "
                "the left half and EXCEPT is empty"
            )
        kept = sorted(left & right) if a["op"] == "INTERSECT" else sorted(left - right)
        if not kept:
            raise ValueError("the result must not be empty")
        return _table(("city",), [(c,) for c in kept])

    if shape == "sql_ranks":
        by, desc = a["by"], a["desc"]
        key = _reader(by)
        values = [key(u) for u in users]
        if len(set(values)) == len(values):
            raise ValueError(
                "the ordering column must contain a tie, or row_number, "
                "rank and dense_rank all agree and the page shows nothing"
            )
        # Sorted twice rather than negated: a text column cannot be
        # negated, and `by` may be city. Name ascending breaks ties in
        # both directions, which is what the query's ORDER BY does.
        ordered = sorted(users, key=lambda u: u["name"])
        ordered.sort(key=key, reverse=desc)
        rows = []
        for i, u in enumerate(ordered, start=1):
            mine = key(u)
            rank = next(
                j for j, other in enumerate(ordered, start=1)
                if key(other) == mine)
            ahead = {key(o) for o in ordered
                     if (key(o) > mine if desc else key(o) < mine)}
            rows.append((u["name"], i, rank, len(ahead) + 1))
        return _table(("name", "rn", "rk", "dr"), rows)

    if shape == "sql_neighbour":
        col, over, desc = a["col"], a["over"], a["desc"]
        if col == over:
            raise ValueError(
                "reading the column the window is ordered by shows the "
                "neighbour of a value you can already see"
            )
        seen = [u[over] for u in users]
        if None in seen or len(set(seen)) != len(seen):
            raise ValueError(
                "the window must be ordered by a column with no ties and "
                "no nulls, or which row is before which is up to the "
                "database and the expected answer is a guess"
            )
        ordered = sorted(users, key=_reader(over), reverse=desc)
        rows = []
        for i, u in enumerate(ordered):
            before = ordered[i - 1][col] if i > 0 else None
            after = ordered[i + 1][col] if i + 1 < len(ordered) else None
            rows.append((u["name"], before, after))
        return _table(("name", "before", "after"), rows)

    if shape == "sql_ntile":
        by, parts = a["by"], a["parts"]
        if not 1 < parts < len(users):
            raise ValueError("the parts must divide the rows into several")
        ordered = sorted(users, key=lambda u: (_reader(by)(u), u["name"]))
        n = len(ordered)
        big, rest = divmod(n, parts)
        rows = []
        at = 0
        for group in range(1, parts + 1):
            size = big + (1 if group <= rest else 0)
            for u in ordered[at:at + size]:
                rows.append((u["name"], group))
            at += size
        return _table(("name", "part"), rows)

    if shape == "sql_filter":
        age, city = a["age"], a["city"]
        older = [u for u in users if u["age"] > age]
        there = [u for u in users if u["city"] == city]
        if not older or len(older) == len(users):
            raise ValueError("the filter must keep some and drop some")
        if not there:
            raise ValueError("the city must have someone in it")
        return _table(
            ("everyone", "older", "there"),
            [(len(users), len(older), sum(u["age"] for u in there))],
        )

    if shape == "sql_concat":
        group, sep = a["group"], a["sep"]
        buckets: dict = {}
        for u in sorted(users, key=lambda u: u["id"]):
            buckets.setdefault(u[group], []).append(u["name"])
        if max(len(v) for v in buckets.values()) < 2:
            raise ValueError(
                "some group must hold more than one, or the separator "
                "never appears and the page is a SELECT"
            )
        rows = [(k, sep.join(buckets[k])) for k in sorted(buckets)]
        return _table((group, "who"), rows)

    if shape == "sql_cast":
        age, tail = a["age"], a["tail"]
        kept = [u for u in users if u["age"] > age]
        if not kept or len(kept) == len(users):
            raise ValueError("the filter must keep some and drop some")
        kept.sort(key=lambda u: u["name"])
        return _table(
            ("name", "shown"),
            [(u["name"], f"{u['age']}{tail}") for u in kept],
        )

    if shape == "sql_nulls":
        fallback, blank = a["fallback"], a["blank"]
        if all(u["email"] is not None for u in users):
            raise ValueError("nothing is null, so IFNULL does nothing")
        if not any(u["city"] == blank for u in users):
            raise ValueError(
                "the city NULLIF blanks must be one somebody has, or it "
                "never turns anything into null"
            )
        rows = [
            (u["name"],
             u["email"] if u["email"] is not None else fallback,
             None if u["city"] == blank else u["city"])
            for u in sorted(users, key=lambda u: u["name"])
        ]
        return _table(("name", "mail", "town"), rows)

    if shape == "sql_page":
        size, skip = a["size"], a["skip"]
        if skip == 0:
            raise ValueError(
                "an offset of zero is the first page, which LIMIT alone "
                "already showed on page four"
            )
        ordered = sorted(users, key=lambda u: -u["age"])
        window = ordered[skip:skip + size]
        if not window:
            raise ValueError("the page asked for must have rows on it")
        return _table(("name", "age"), [(u["name"], u["age"]) for u in window])

    if shape == "sql_recursive":
        start, step, stop = a["start"], a["step"], a["stop"]
        if step < 1 or start > stop:
            raise ValueError("the count must move forward and terminate")
        values = []
        x = start
        while True:
            values.append(x)
            if x >= stop:
                break
            x += step
        if len(values) < 3:
            raise ValueError("a count this short does not show recursion")
        if values[-1] != stop:
            raise ValueError(
                "the last step must land on the number the prompt names, "
                "or the prompt says reach and the answer overshoots"
            )
        return _table(("x",), [(v,) for v in values])

    raise KeyError(shape)
