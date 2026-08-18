"""SQL fundamentals.

The three class slots are shared with every other language, but SQL doesn't
loop — it describes a set and lets the engine do the walking. So the third
class is named "Grouping" here and covers the set-based equivalent:
aggregates, GROUP BY, and joins. Class names come from the bank, so this
reads correctly in the picker.

Queries run against a small sample database (see `sql_runner`), so you can
actually execute what you type.
"""

from __future__ import annotations

from code_coach.fundamentals.base import (
    FundamentalsBank,
    FundamentalsClass,
    Snippet,
    register,
)


def _s(code: str, tip: str, level: int = 1) -> Snippet:
    return Snippet(code=code, tip=tip, level=level)


_FOUNDATIONS = FundamentalsClass(
    id="foundations",
    name="Queries",
    description="Asking for rows: SELECT, FROM, ORDER BY, LIMIT.",
    snippets=(
        _s("SELECT * FROM users;", "Every column, every row. Fine while exploring."),
        _s("SELECT name FROM users;", "Name the columns you actually want."),
        _s("SELECT name, city FROM users;", "Several columns, comma separated."),
        _s("SELECT DISTINCT city FROM users;", "Drop repeats from the result."),
        _s("SELECT COUNT(*) FROM users;", "How many rows came back."),
        _s("SELECT name AS customer FROM users;", "`AS` renames a column in the output."),
        _s("SELECT * FROM users LIMIT 5;", "Cap the rows — always do this while exploring."),
        _s("SELECT * FROM users ORDER BY name;", "Sorted ascending unless you say otherwise.", 2),
        _s("SELECT * FROM users ORDER BY age DESC;", "`DESC` for largest first.", 2),
        _s("SELECT name FROM users ORDER BY age DESC LIMIT 3;",
           "Sort then cut — that's a 'top 3'.", 2),
        _s("SELECT price * 2 AS doubled FROM orders;", "You can compute new columns.", 2),
        _s("SELECT MIN(age), MAX(age) FROM users;", "Aggregates collapse many rows to one.", 2),
        _s(
            "SELECT name, city\nFROM users\nORDER BY name;",
            "One clause per line — SQL gets long, and this stays readable.",
            3,
        ),
        _s(
            "SELECT name, age\nFROM users\nORDER BY age DESC\nLIMIT 3;",
            "The clause order is fixed: SELECT, FROM, ORDER BY, LIMIT.",
            4,
        ),
        _s(
            "SELECT city, COUNT(*) AS people\nFROM users\nGROUP BY city\n"
            "ORDER BY people DESC;",
            "Count per city, biggest first — the shape of most reports.",
            5,
        ),
        _s(
            "SELECT name, age\nFROM users\nWHERE age >= 30\nORDER BY age\nLIMIT 5;",
            "A complete query with every common clause.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Filtering",
    description="WHERE, boolean logic, NULL, and CASE.",
    snippets=(
        _s("WHERE age > 18", "Keeps only the rows that match."),
        _s("WHERE city = 'Denver'", "One `=` for comparison. Strings in single quotes."),
        _s("WHERE city != 'Denver'", "`!=` or `<>`, both work."),
        _s("WHERE age BETWEEN 18 AND 30", "Inclusive at both ends."),
        _s("WHERE city IN ('Denver', 'Austin')", "Matches any value in the list."),
        _s("WHERE name LIKE 'A%'", "`%` matches any run of characters."),
        _s("WHERE email IS NULL", "Never `= NULL` — nothing equals NULL, not even NULL."),
        _s("WHERE email IS NOT NULL", "The matching test for 'has a value'.", 2),
        _s("WHERE age > 18 AND city = 'Denver'", "Both must hold.", 2),
        _s("WHERE city = 'Denver' OR city = 'Austin'", "Either will do.", 2),
        _s("WHERE NOT active", "Flips the condition.", 2),
        _s("HAVING COUNT(*) > 1", "HAVING filters groups; WHERE filters rows.", 2),
        _s(
            "SELECT name\nFROM users\nWHERE age > 18;",
            "WHERE comes after FROM, before ORDER BY.",
            3,
        ),
        _s(
            "SELECT name, age\nFROM users\nWHERE age >= 18 AND city = 'Denver'\n"
            "ORDER BY age;",
            "Two conditions, then a sort.",
            4,
        ),
        _s(
            "SELECT name,\n       CASE\n         WHEN age < 18 THEN 'minor'\n"
            "         ELSE 'adult'\n       END AS bracket\nFROM users;",
            "CASE is SQL's if/else, and it lives in the SELECT list.",
            5,
        ),
        _s(
            "SELECT city, COUNT(*) AS people\nFROM users\nWHERE age >= 18\n"
            "GROUP BY city\nHAVING COUNT(*) > 1\nORDER BY people DESC;",
            "WHERE filters rows first, then HAVING filters the groups.",
            5,
        ),
    ),
)


_GROUPING = FundamentalsClass(
    id="loops",
    name="Grouping & Joins",
    description="Summarising many rows, and combining tables.",
    snippets=(
        _s("SELECT COUNT(*) FROM orders;", "The simplest aggregate."),
        _s("SELECT SUM(price) FROM orders;", "Adds a column up."),
        _s("SELECT AVG(price) FROM orders;", "The mean, ignoring NULLs."),
        _s("GROUP BY city", "Collapses rows that share a value into one."),
        _s("GROUP BY user_id", "Group by whatever you're summarising per."),
        _s("ORDER BY total DESC", "Sort the summary, not the raw rows."),
        _s("JOIN orders ON orders.user_id = users.id",
           "The ON clause says how the tables line up.", 2),
        _s("LEFT JOIN orders ON orders.user_id = users.id",
           "Keeps every user, even those with no orders.", 2),
        _s("SELECT u.name, o.price", "Alias tables and the query gets much shorter.", 2),
        _s("FROM users u", "`u` is now the alias for users.", 2),
        _s(
            "SELECT city, COUNT(*)\nFROM users\nGROUP BY city;",
            "Anything not aggregated must be in the GROUP BY.",
            3,
        ),
        _s(
            "SELECT user_id, SUM(price) AS total\nFROM orders\nGROUP BY user_id\n"
            "ORDER BY total DESC;",
            "Spend per customer, biggest first.",
            4,
        ),
        _s(
            "SELECT u.name, o.price\nFROM users u\nJOIN orders o ON o.user_id = u.id;",
            "An inner join keeps only rows that match on both sides.",
            5,
        ),
        _s(
            "SELECT u.name, COUNT(o.id) AS orders\nFROM users u\n"
            "LEFT JOIN orders o ON o.user_id = u.id\nGROUP BY u.name\n"
            "ORDER BY orders DESC;",
            "LEFT JOIN plus COUNT gives zero for users who ordered nothing.",
            5,
        ),
        _s(
            "SELECT u.city, SUM(o.price) AS revenue\nFROM users u\n"
            "JOIN orders o ON o.user_id = u.id\nGROUP BY u.city\n"
            "HAVING SUM(o.price) > 10\nORDER BY revenue DESC;",
            "Join, group, filter the groups, sort — the full reporting shape.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(
        language="sql",
        classes=(_FOUNDATIONS, _DECISIONS, _GROUPING),
    )
)
