"""Pages 11-20: SQL past the fundamentals.

The first ten pages went SELECT to JOIN and stopped, which is where most
introductions stop and where SQL starts being the reason anyone reaches for
SQL. No CASE, no subquery, no EXISTS, no UNION, no CTE, no window
functions.

Ten more, in the order the ideas need each other. The two window pages come
last because they are the payoff: they answer a question about a group
without collapsing the group, which nothing before them can do.

The dataset is five users and six orders and does not change, so the
variety across twenty exercises comes from the predicates. That is
deliberate rather than a shortcut: the same small table seen twenty ways is
how the shape of a query becomes readable.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

SQL_ONLY = ("sql",)


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
        languages=SQL_ONLY,
        tier="advanced",
    )


# ── 11. LIKE and BETWEEN ─────────────────────────────────────

_PATTERNS = ("A%", "B%", "C%", "D%", "E%", "%n", "%y", "%x", "%s%", "%v%")
_RANGES = ((20, 35), (18, 40), (25, 45), (17, 30), (30, 45),
           (20, 30), (35, 45), (17, 25), (24, 35), (28, 42))

LIKE_PAGE = _page(
    "sql-like", 11, "Matching a shape, and falling in a range",
    "LIKE compares against a pattern where % stands for any run of "
    "characters, including none. BETWEEN is inclusive at both ends, which "
    "is the part worth remembering, because the equivalent written with "
    "two comparisons is easy to get wrong by one at either edge.",
    "WHERE age BETWEEN 20 AND 35 includes both 20 and 35, unlike almost "
    "every range in every other language here",
    "sql_like",
    tuple(
        (f"List name and city for every user whose name matches "
         f"'{pat}'. Order by name.",
         {"want": "like", "pattern": pat})
        for pat in _PATTERNS
    ) + tuple(
        (f"List name and age for every user aged between {low} and {high}. "
         f"Order by age.",
         {"want": "between", "low": low, "high": high})
        for low, high in _RANGES
    ),
)


# ── 12. CASE ─────────────────────────────────────────────────

_CUTS = (18, 20, 24, 25, 28, 30, 31, 35, 36, 40)
_LABELS = (("minor", "adult"), ("young", "older"))

CASE_PAGE = _page(
    "sql-case", 12, "A column that depends on the row",
    "CASE is the closest SQL comes to an if, and it produces a value rather "
    "than choosing a statement, so it belongs wherever a column belongs. "
    "The arms are tried in order and the first true one wins, which means "
    "an ELSE is what stops a row that matches nothing from coming out null.",
    "CASE WHEN age < 18 THEN 'minor' ELSE 'adult' END AS band — the AS "
    "names the column, and without it the header is the whole expression",
    "sql_case",
    tuple(
        (f"For every user print the name and a band column: '{low}' when "
         f"the age is under {cut}, otherwise '{high}'. Order by name.",
         {"cut": cut, "low": low, "high": high})
        for low, high in _LABELS
        for cut in _CUTS
    ),
)


# ── 13. NULL ─────────────────────────────────────────────────

_FALLBACKS = ("none", "n/a", "missing", "unknown", "-", "(blank)",
              "no email", "tbd", "absent", "void", "nil", "empty")

# Four different projections rather than the same query four times: the
# suite forbids two identical exercises on a page, and it is right to.
_NULL_COLS = (("name",), ("name", "city"), ("name", "age"),
              ("name", "city", "age"))

NULL_PAGE = _page(
    "sql-null", 13, "The value that is not a value",
    "NULL is not a value and does not compare like one: equals NULL is "
    "never true, not even against another NULL, which is why IS NULL exists "
    "as its own operator. COALESCE takes the first argument that is not "
    "null, so it is how a missing value becomes a printable one.",
    "WHERE email = NULL returns nothing, ever. WHERE email IS NULL is what "
    "you meant.",
    "sql_null",
    tuple(
        (f"List every user's name alongside their email, showing "
         f"'{fallback}' where there is none. Order by name.",
         {"want": "coalesce", "fallback": fallback})
        for fallback in _FALLBACKS
    ) + tuple(
        (f"List {' and '.join(cols)} for users who have no email at all. "
         f"Order by name.",
         {"want": "is_null", "cols": list(cols)})
        for cols in _NULL_COLS
    ) + tuple(
        (f"List {' and '.join(cols)} for users who do have an email. "
         f"Order by name.",
         {"want": "is_not_null", "cols": list(cols)})
        for cols in _NULL_COLS
    ),
)


# ── 14. Subquery ─────────────────────────────────────────────

_SUBQUERIES = (
    (">", "AVG", 0), ("<", "AVG", 0), (">", "AVG", 5), ("<", "AVG", 5),
    (">", "AVG", -5), ("<", "AVG", -5), (">", "AVG", 10), ("<", "AVG", 10),
    (">", "AVG", -10), ("<", "AVG", -10),
    (">", "MIN", 0), (">", "MIN", 3), (">", "MIN", 7), (">", "MIN", 13),
    (">", "MIN", 18),
    ("<", "MAX", 0), ("<", "MAX", -3), ("<", "MAX", -6), ("<", "MAX", -11),
    ("<", "MAX", -17),
)

_WORDS = {">": "above", "<": "below"}

SUBQUERY_PAGE = _page(
    "sql-subquery", 14, "A query inside a query",
    "A subquery returning one row and one column can stand anywhere a value "
    "can, which is what lets a WHERE compare against something the same "
    "query computed. It runs once here, not once per row, because nothing "
    "inside it refers to the outer query — that difference is the whole gap "
    "between a fast query and a slow one.",
    "WHERE age > (SELECT AVG(age) FROM users) — the inner query has no idea "
    "the outer one exists, so it runs once",
    "sql_subquery",
    tuple(
        (f"List name and age for users whose age is {_WORDS[op]} the "
         f"{agg.lower()} age"
         + ("" if not off else
            f" {'plus' if off > 0 else 'minus'} {abs(off)}")
         + ". Work the threshold out with a subquery. Order by age.",
         {"op": op, "agg": agg, "offset": off})
        for op, agg, off in _SUBQUERIES
    ),
)


# ── 15. EXISTS ───────────────────────────────────────────────

_OVERS = (None, 5, 10, 20, 30, 40, 50, 100, 150, 200)

EXISTS_PAGE = _page(
    "sql-exists", 15, "Asking whether anything matches",
    "EXISTS asks whether the inner query returns any row at all and stops "
    "at the first one, so what it selects does not matter and SELECT 1 is "
    "the convention. It refers to the outer row, which makes it a "
    "correlated subquery: it runs once per row rather than once, and that "
    "is the trade for being able to ask about each row separately.",
    "WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id) — the "
    "mention of u.id is what makes it run per row",
    "sql_exists",
    tuple(
        (("List the names of users who have at least one order"
          + ("" if over is None else f" costing more than {over}")
          + ". Use EXISTS. Order by name."),
         {"want": "with", "over": over})
        for over in _OVERS
    ) + tuple(
        (("List the names of users with no order"
          + ("" if over is None else f" costing more than {over}")
          + " at all. Use NOT EXISTS. Order by name."),
         {"want": "without", "over": over})
        for over in _OVERS
    ),
)


# ── 16. Self join ────────────────────────────────────────────

_FLOORS = (0, 15, 18, 20, 22, 24, 25, 26, 28, 29)

SELF_JOIN_PAGE = _page(
    "sql-self-join", 16, "A table joined to itself",
    "Nothing about JOIN says the two sides are different tables. Aliasing "
    "the same one twice is how you compare rows to other rows, and the "
    "a.id < b.id is what stops every pair appearing twice and every row "
    "pairing with itself. Without it you get every ordered pair including "
    "the diagonal, which is a classic way to be surprised by a row count.",
    "JOIN users b ON a.city = b.city AND a.id < b.id — the second half is "
    "what makes it pairs rather than every combination",
    "sql_self_join",
    tuple(
        (("List every pair of users sharing a city, as one, two and the "
          "city"
          + ("" if not floor else f", where the first is older than {floor}")
          + ". Order by both names."),
         {"on": "city", "floor": floor, "floor_col": "age"})
        for floor in _FLOORS
    ) + tuple(
        (("List every pair of users with the same active flag, as one, two "
          "and the flag"
          + ("" if not floor else f", where the first is older than {floor}")
          + ". Order by both names."),
         {"on": "active", "floor": floor, "floor_col": "age"})
        for floor in _FLOORS
    ),
)


# ── 17. UNION ────────────────────────────────────────────────

_UNIONS = (
    ("Denver", 20), ("Denver", 29), ("Denver", 34), ("Denver", 39),
    ("Austin", 20), ("Austin", 24), ("Austin", 30), ("Austin", 34),
    ("Boston", 10), ("Boston", 16),
)

UNION_PAGE = _page(
    "sql-union", 17, "Two results stacked into one",
    "UNION stacks two results and removes the duplicates, which costs a "
    "sort or a hash. UNION ALL keeps everything and costs nothing extra, so "
    "it is the right one whenever you know there is no overlap or do not "
    "care. Both halves must have the same number of columns, and one ORDER "
    "BY at the end orders the whole thing rather than either half.",
    "UNION removes duplicates and UNION ALL does not — on these rows the "
    "two halves overlap, so the answers differ",
    "sql_union",
    tuple(
        (f"List the names of users in {city}, stacked with the names of "
         f"users older than {age}, with duplicates removed. Order by name.",
         {"want": "plain", "city": city, "age": age})
        for city, age in _UNIONS
    ) + tuple(
        (f"The same two halves, users in {city} and users older than "
         f"{age}, but keep every row with UNION ALL. Order by name.",
         {"want": "all", "city": city, "age": age})
        for city, age in _UNIONS
    ),
)


# ── 18. CTE ──────────────────────────────────────────────────

_CTES = (
    (">", 10), ("<", 10), (">", 50), ("<", 50), (">", 60), ("<", 60),
    (">", 70), ("<", 70), (">", 100), ("<", 100), (">", 150), ("<", 150),
    (">", 175), ("<", 175), (">", 200), ("<", 200), (">", 225), ("<", 225),
    (">", 250), ("<", 250),
)

CTE_PAGE = _page(
    "sql-cte", 18, "Naming a query so the next one can read",
    "WITH gives a subquery a name and lets the query after it be about one "
    "thing. Nothing else changes: the same query written with the subquery "
    "inline computes the same rows. What it buys is that a reader meets the "
    "pieces in the order they are used rather than inside out, which on a "
    "query of any size is most of whether it can be understood at all.",
    "WITH spend AS (SELECT user_id, SUM(price) AS total FROM orders GROUP "
    "BY user_id) — and afterwards spend is a table you can join to",
    "sql_cte",
    tuple(
        (f"Total each user's orders in a CTE named spend, then list the "
         f"names and totals where the total is {_WORDS[op]} {amount}. "
         f"Order by total, largest first.",
         {"op": op, "amount": amount})
        for op, amount in _CTES
    ),
)


# ── 19. Window ───────────────────────────────────────────────
#
# Only age, name and id are used to order within a partition. The other
# columns tie inside at least one city, and the order among tied rows is
# not defined, so a page built on one would have no fixed answer.

_WINDOWS = tuple(
    (by, desc, part, over)
    for part in ("city", "active")
    for by in ("age", "name", "id")
    for desc in (True, False)
    for over in (0, 18)
)[:20]

_ORDER_WORDS = {True: "highest first", False: "lowest first"}
_PART_WORDS = {"city": "city", "active": "active flag"}

WINDOW_PAGE = _page(
    "sql-window", 19, "A number per row, worked out over a group",
    "A window function computes across a set of rows and still returns one "
    "row per row, which is the thing GROUP BY cannot do. PARTITION BY says "
    "which rows count as the group, ORDER BY inside the OVER decides the "
    "numbering, and neither has anything to do with the ORDER BY at the end "
    "of the query.",
    "ROW_NUMBER() OVER (PARTITION BY city ORDER BY age DESC) — the "
    "numbering restarts in every city",
    "sql_window",
    tuple(
        (f"Number the users within each {_PART_WORDS[part]} by {by}, "
         f"{_ORDER_WORDS[desc]}, using ROW_NUMBER with a window"
         + ("" if not over else f", counting only users older than {over}")
         + f". Print name, {part} and the number, ordered by {part} then "
         f"number.",
         {"by": by, "desc": desc, "part": part, "over": over})
        for by, desc, part, over in _WINDOWS
    ),
)


# ── 20. Running total ────────────────────────────────────────

_RUNNING = (
    (">", 10), (">", 15), (">", 20), (">", 25), (">", 30), (">", 35),
    (">", 40), (">", 50), (">", 60), (">", 100), (">", 150),
    ("<", 20), ("<", 25), ("<", 30), ("<", 40), ("<", 50), ("<", 60),
    ("<", 100), ("<", 150), ("<", 200),
)

RUNNING_PAGE = _page(
    "sql-running", 20, "A total that grows as the rows go by",
    "The same window machinery with an aggregate in front of it. SUM with "
    "an OVER that has an ORDER BY totals everything up to and including the "
    "current row, which is a running total. Take the ORDER BY out of the "
    "OVER and it totals the whole partition instead and prints the same "
    "number on every row, which is a different and also useful thing.",
    "SUM(price) OVER (ORDER BY id) AS running — the ORDER BY inside is "
    "what makes it accumulate rather than repeat",
    "sql_running",
    tuple(
        (f"List item, price and a running total of price for the orders "
         f"costing {_WORDS[op]} {amount}, in id order.",
         {"op": op, "amount": amount})
        for op, amount in _RUNNING
    ),
)


SQL2_PAGES: tuple[Page, ...] = (
    LIKE_PAGE, CASE_PAGE, NULL_PAGE, SUBQUERY_PAGE, EXISTS_PAGE,
    SELF_JOIN_PAGE, UNION_PAGE, CTE_PAGE, WINDOW_PAGE, RUNNING_PAGE,
)
