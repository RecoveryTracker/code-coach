"""Pages 21-30: SQL past the second set of fundamentals.

Ten more, and they are the ones that turn up in real queries and rarely in
tutorials. The other two set operators. The three ranking functions and
what separates them, which is only visible when there is a tie. The two
that read a neighbouring row. An aggregate with its own filter. String
aggregation. Casting. The two NULL helpers, one that supplies a value and
one that makes a null on purpose. Pagination. And a query that calls
itself.

The table is five users and six orders and does not grow, so the variety
comes from the predicates — and on the ranking pages from ordering by a
remainder, because five rows contain a tie in only two columns and a page
needs twenty distinct exercises.
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
        tier="intermediate",
    )


# ── 21. INTERSECT and EXCEPT ─────────────────────────────────
#
# Every age here leaves the older half a proper subset of the cities, so
# INTERSECT is not simply the left half and EXCEPT is not empty.

_AGES = (17, 20, 22, 24, 25, 28, 30, 32, 35, 38)

SETOPS_PAGE = _page(
    "sql-setops", 21, "What both have, and what only one has",
    "UNION was the first of three. INTERSECT keeps a row only when it "
    "appears on both sides, EXCEPT keeps it only when it appears on the "
    "left and not the right. All three remove duplicates, and all three "
    "need the two halves to have the same columns.",
    "SELECT city FROM users EXCEPT SELECT city FROM users WHERE age > 30 "
    "— the cities with nobody over thirty in them",
    "sql_setops",
    tuple(
        (f"List the cities that appear both in the whole table and among "
         f"users over {age}. Order by city.",
         {"op": "INTERSECT", "age": age})
        for age in _AGES
    ) + tuple(
        (f"List the cities that appear in the whole table but not among "
         f"users over {age}. Order by city.",
         {"op": "EXCEPT", "age": age})
        for age in _AGES
    ),
)


# ── 22. The three ranking functions ──────────────────────────
#
# Ordering by a remainder is what makes ties. Five rows tie only on city
# and on active, which is two exercises rather than twenty.

_RANK_BY = ("city", "active", "age % 2", "age % 3", "age % 4",
            "age % 5", "age % 6", "age % 7", "age % 8", "age % 9")

RANKS_PAGE = _page(
    "sql-ranks", 22, "Three ways to number, and what a tie does",
    "ROW_NUMBER always counts one two three, even when two rows are "
    "equal, so it has to pick one arbitrarily. RANK gives equal rows the "
    "same number and then skips: two firsts are followed by a third. "
    "DENSE_RANK gives them the same number and does not skip. They are "
    "identical until there is a tie, which is why this page orders by a "
    "remainder rather than by age. Note that ROW_NUMBER is given a "
    "second ordering column and the other two are not: without one it "
    "would have to break the tie arbitrarily, and the same query could "
    "answer differently twice.",
    "Two rows tied at the top: ROW_NUMBER says 1 and 2, RANK says 1 and 1 "
    "then 3, DENSE_RANK says 1 and 1 then 2",
    "sql_ranks",
    tuple(
        (f"Number the users by {by}, {'largest' if desc else 'smallest'} "
         f"first, three ways at once: ROW_NUMBER, RANK and DENSE_RANK. "
         f"Print the name and all three.",
         {"by": by, "desc": desc})
        for by in _RANK_BY
        for desc in (False, True)
    ),
)


# ── 23. The row before and the row after ─────────────────────

# Any column can be read, including the one that is sometimes null. The
# window can only be ordered by a column whose values are all different:
# city has two Denvers, and a tie makes which row is "before" a matter of
# what the database felt like, which is not something to ask for an exact
# answer to. Never a column against itself, either — LAG(age) over an age
# ordering shows the neighbour of a value already on the row. Twelve pairs
# and two directions.
_READ = ("age", "id", "name", "city", "email")
_ORDER = ("id", "age", "name")

_NEIGHBOUR = tuple(
    (col, over, desc)
    for desc in (False, True)
    for over in _ORDER
    for col in _READ
    if col != over
)

NEIGHBOUR_PAGE = _page(
    "sql-neighbour", 23, "The row before and the row after",
    "LAG reads a column from the previous row and LEAD from the next, in "
    "whatever order the window says. The first row has nothing before it "
    "and the last has nothing after, so both return NULL at the ends — "
    "which is the thing to handle rather than be surprised by. This is how "
    "you compute a difference between consecutive rows without joining the "
    "table to itself.",
    "LAG(age) OVER (ORDER BY id) — the previous row's age, and NULL on "
    "the first row",
    "sql_neighbour",
    tuple(
        (f"For every user print the name, the {col} of the row before and "
         f"the {col} of the row after, walking in {over} order, "
         f"{'largest' if desc else 'smallest'} first.",
         {"col": col, "over": over, "desc": desc})
        for col, over, desc in _NEIGHBOUR
    ),
)


# ── 24. Equal groups ─────────────────────────────────────────

# Five rows into five buckets is one row each, which demonstrates nothing
# about the uneven split this page is for, so the parts stop at four.
_NTILE = tuple(
    (by, parts)
    for by in ("age", "id", "name", "city", "age % 5", "age % 3", "age % 2")
    for parts in (2, 3, 4)
)

NTILE_PAGE = _page(
    "sql-ntile", 24, "Cutting the rows into equal groups",
    "NTILE splits the ordered rows into that many buckets and tells each "
    "row which one it landed in. When the rows do not divide evenly the "
    "earlier buckets take the extra, so five rows in two buckets is three "
    "and two rather than two and three. That rule is worth knowing before "
    "you use it to build quartiles.",
    "NTILE(2) OVER (ORDER BY age) on five rows gives three ones and two "
    "twos, not the other way round",
    "sql_ntile",
    tuple(
        (f"Split the users into {parts} equal groups ordered by {by}, and "
         f"print each name with the group it fell into.",
         {"by": by, "parts": parts})
        for by, parts in _NTILE
    ),
)


# ── 25. An aggregate with its own filter ─────────────────────

_FILTERS = tuple(
    (age, city)
    for age in (17, 20, 24, 25, 28, 30, 32, 35, 38, 40)
    for city in ("Denver", "Austin")
)

FILTER_PAGE = _page(
    "sql-filter", 25, "Counting only some of what you counted",
    "FILTER puts a condition on one aggregate without touching the rest of "
    "the query, so a single pass can count everything and count a subset "
    "beside it. The alternative is a CASE inside the aggregate, which does "
    "the same thing and reads worse, or two queries and a join, which does "
    "the same thing and costs more.",
    "COUNT(*) FILTER (WHERE age > 30) beside a plain COUNT(*) — one scan, "
    "two answers",
    "sql_filter",
    tuple(
        (f"In one row print how many users there are, how many are over "
         f"{age}, and the total age of everyone in {city}.",
         {"age": age, "city": city})
        for age, city in _FILTERS
    ),
)


# ── 26. Many rows into one string ────────────────────────────

# No semicolon in a separator: the runner splits a script into statements
# on semicolons, and one inside a string literal is indistinguishable from
# the end of the query as far as that split is concerned.
_SEPS = (", ", " and ", " | ", " . ", " / ", " + ", " -> ", " then ",
         " & ", " with ")

CONCAT_PAGE = _page(
    "sql-concat", 26, "Many rows into one string",
    "GROUP_CONCAT collapses a group into a single piece of text with a "
    "separator between the parts. It is the aggregate people forget "
    "exists and then write a loop in the application for. The order "
    "inside the string is not guaranteed unless you ask for one, which is "
    "the usual surprise.",
    "GROUP_CONCAT(name, ', ') per city — one row per city, the names "
    "joined into one column",
    "sql_concat",
    tuple(
        (f"For each {group}, print it beside the names of everyone in it, "
         f"joined with {sep!r}.",
         {"group": group, "sep": sep})
        for group in ("city", "active")
        for sep in _SEPS
    ),
)


# ── 27. A number treated as text ─────────────────────────────

_CASTS = tuple(
    (age, tail)
    for age in (17, 20, 24, 28, 30)
    for tail in (" years", " yrs", "!", " old", "y")
)

CAST_PAGE = _page(
    "sql-cast", 27, "A number treated as text",
    "CAST changes the type of a value for the rest of the expression. The "
    "double pipe is the standard way to join two strings, and it needs "
    "both sides to be text — SQLite is loose enough to convert for you, "
    "which is convenient until you move the query to a database that is "
    "not.",
    "CAST(age AS TEXT) || ' years' — the cast is what makes the join a "
    "string join rather than an addition",
    "sql_cast",
    tuple(
        (f"For every user over {age}, print the name and their age with "
         f"{tail!r} on the end. Order by name.",
         {"age": age, "tail": tail})
        for age, tail in _CASTS
    ),
)


# ── 28. Supplying a null, and making one ─────────────────────

_FALLBACKS = ("none", "no email", "unknown", "-", "missing",
              "not given", "blank", "absent", "n/a", "unset")

NULLS_PAGE = _page(
    "sql-nulls", 28, "Supplying one, and making one",
    "IFNULL hands back the second value when the first is null, which is "
    "COALESCE with exactly two arguments. NULLIF goes the other way: it "
    "returns null when the two arguments are equal, which is how you turn "
    "a placeholder into a real absence before an aggregate counts it. "
    "Together they are how a column that means nothing gets said as "
    "nothing.",
    "NULLIF(city, 'Denver') turns Denver into null and leaves every other "
    "city alone",
    "sql_nulls",
    tuple(
        (f"For every user print the name, their email or {fallback!r} "
         f"where there is none, and their city with {blank!r} turned into "
         f"a null. Order by name.",
         {"fallback": fallback, "blank": blank})
        for blank in ("Denver", "Austin")
        for fallback in _FALLBACKS
    ),
)


# ── 29. The second page of results ───────────────────────────

# Five rows, so skipping five leaves nothing to take and the exercise is
# a page number past the end of the book.
_PAGES = tuple(
    (size, skip)
    for size in (1, 2, 3, 4, 5)
    for skip in (1, 2, 3, 4)
)

PAGE_PAGE = _page(
    "sql-page", 29, "The second page of results",
    "OFFSET skips rows before LIMIT takes them, which is how pagination is "
    "usually written and why the tenth page of a large table is slow: the "
    "database still has to walk everything it skipped. Keyset pagination — "
    "asking for rows after the last id you saw — is the answer once the "
    "table is big, and it is a different query rather than a bigger "
    "offset.",
    "LIMIT 2 OFFSET 2 is the second page of two, and the database read "
    "four rows to give you the last two",
    "sql_page",
    tuple(
        (f"Order the users by age, oldest first, then skip {skip} and take "
         f"{size}. Print the name and age.",
         {"size": size, "skip": skip})
        for size, skip in _PAGES
    ),
)


# ── 30. A query that calls itself ────────────────────────────

_RECURSIVE = (
    (1, 1, 5), (1, 1, 8), (1, 2, 9), (2, 2, 10), (1, 3, 13),
    (0, 1, 4), (5, 5, 30), (1, 4, 17), (3, 3, 18), (10, 10, 50),
    (1, 1, 6), (2, 1, 7), (1, 5, 21), (4, 4, 24), (0, 2, 8),
    (1, 6, 25), (5, 1, 9), (2, 3, 14), (6, 6, 36), (1, 7, 29),
)

RECURSIVE_PAGE = _page(
    "sql-recursive", 30, "A query that calls itself",
    "A recursive CTE has two halves joined by UNION ALL: a first row, and "
    "a rule for making the next one from the last. It stops when the rule "
    "produces nothing. This is how you generate a series without a table "
    "to select from, and how you walk a tree stored as rows pointing at "
    "their parents — which is the reason it exists.",
    "WITH RECURSIVE counted(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM "
    "counted WHERE x < 5) — the WHERE is what stops it",
    "sql_recursive",
    tuple(
        (f"Using a recursive CTE, count from {start} in steps of {step} "
         f"until you reach {stop}, and print each number.",
         {"start": start, "step": step, "stop": stop})
        for start, step, stop in _RECURSIVE
    ),
)


SQL3_PAGES: tuple[Page, ...] = (
    SETOPS_PAGE, RANKS_PAGE, NEIGHBOUR_PAGE, NTILE_PAGE, FILTER_PAGE,
    CONCAT_PAGE, CAST_PAGE, NULLS_PAGE, PAGE_PAGE, RECURSIVE_PAGE,
)
