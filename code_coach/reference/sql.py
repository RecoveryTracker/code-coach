"""The SQL cheat sheet.

SQL's dialects differ more than most languages', so this sticks to what is
portable and flags the places where it is not. Where the app runs your query
it is SQLite, and the entries that only work there say so.

The other thing this card tries to fix is the order. SQL is written
SELECT-first but executed FROM-first, and almost every early confusion —
why an alias is not visible, why WHERE cannot see a COUNT — comes from that.
"""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="sql",
    sections=(
        Section(
            "The first minute",
            "What you write before you have written anything.",
            (
                _e("SELECT * FROM users;", "everything, to see what is there"),
                _e("SELECT name, email FROM users;", "name the columns once you know them"),
                _e("SELECT * FROM users WHERE age > 21;", "filter rows"),
                _e("SELECT * FROM users ORDER BY name;", "add DESC to reverse"),
                _e("SELECT * FROM users LIMIT 10;", "always, while exploring"),
                _e("SELECT COUNT(*) FROM users;", "how many rows"),
                _e("SELECT DISTINCT city FROM users;", "one row per different value"),
                _e("-- a note to your later self", "and /* ... */ for a block"),
            ),
        ),
        Section(
            "The order it really runs in",
            "Written SELECT-first, executed FROM-first. This explains most errors.",
            (
                _e("FROM", "1. pick the tables and join them"),
                _e("WHERE", "2. drop rows; no aggregates visible yet"),
                _e("GROUP BY", "3. collapse rows into groups"),
                _e("HAVING", "4. drop groups; aggregates ARE visible"),
                _e("SELECT", "5. choose columns; aliases are born here"),
                _e("ORDER BY", "6. sort; can use the aliases from SELECT"),
                _e("LIMIT", "7. take the first n of the sorted result"),
                _e("SELECT total AS t FROM sales WHERE t > 10;", "fails: WHERE runs before the alias exists"),
                _e("SELECT total AS t FROM sales ORDER BY t;", "works: ORDER BY runs after SELECT"),
            ),
        ),
        Section(
            "WHERE",
            "Filtering rows, and the operators worth knowing by heart.",
            (
                _e("WHERE age >= 18 AND city = 'Leeds'", "single quotes for text, always"),
                _e("WHERE age < 18 OR age > 65", "mind the precedence; bracket when mixed"),
                _e("WHERE NOT active", "or use != / <> for inequality"),
                _e("WHERE city IN ('Leeds', 'York')", "shorter than a chain of ORs"),
                _e("WHERE age BETWEEN 18 AND 65", "inclusive at both ends"),
                _e("WHERE name LIKE 'A%'", "% is any run, _ is one character"),
                _e("WHERE email IS NULL", "= NULL is never true, not even for NULL"),
                _e("WHERE email IS NOT NULL", "the only way to test for a value"),
                _e("WHERE deleted_at IS NULL", "the usual shape of a soft delete"),
            ),
        ),
        Section(
            "NULL",
            "Not zero, not empty text. It means unknown, and it is contagious.",
            (
                _e("NULL = NULL", "not true — unknown equals unknown is unknown"),
                _e("1 + NULL", "NULL; arithmetic with unknown is unknown"),
                _e("COALESCE(nickname, name)", "first value that is not NULL"),
                _e("COALESCE(total, 0)", "the standard way to default a sum"),
                _e("COUNT(*)", "counts rows, NULLs included"),
                _e("COUNT(email)", "counts rows where email is not NULL"),
                _e("SUM(bonus)", "ignores NULLs; NULL, not 0, when every row is"),
                _e("NULLIF(a, b)", "NULL when a = b; guards a divide by zero"),
                _e("ORDER BY name", "NULLs sort together, but which end varies"),
            ),
        ),
        Section(
            "JOIN",
            "Combining tables. The type is about what happens when there is no match.",
            (
                _e("FROM orders o\nJOIN users u ON u.id = o.user_id", "only rows that match both sides"),
                _e("LEFT JOIN users u ON u.id = o.user_id", "keeps every left row; NULLs on the right"),
                _e("RIGHT JOIN", "the mirror image; rarer, and not in every engine"),
                _e("FULL OUTER JOIN", "keeps unmatched rows from both sides"),
                _e("CROSS JOIN", "every pair; usually a mistake"),
                _e("FROM users a JOIN users b ON a.boss_id = b.id", "a table joined to itself needs aliases"),
                _e("LEFT JOIN orders o ON o.user_id = u.id\nWHERE o.id IS NULL", "the rows with NO match"),
                _e("ON u.id = o.user_id AND o.paid", "in ON, filters BEFORE the join"),
                _e("WHERE o.paid", "in WHERE, filters after — turns a LEFT JOIN into a JOIN"),
            ),
        ),
        Section(
            "GROUP BY",
            "Collapsing many rows into one per group.",
            (
                _e("SELECT city, COUNT(*)\nFROM users\nGROUP BY city;", "one row per city"),
                _e("SELECT city, AVG(age) FROM users GROUP BY city;", "the aggregate applies within a group"),
                _e("GROUP BY city, country", "one row per combination"),
                _e("HAVING COUNT(*) > 5", "filters groups; WHERE cannot"),
                _e("WHERE active\nGROUP BY city\nHAVING COUNT(*) > 5", "WHERE trims rows, HAVING trims groups"),
                _e("SUM(amount)", "add them up"),
                _e("MIN(created_at)\nMAX(created_at)", "earliest and latest"),
                _e("AVG(score)", "ignores NULLs, which may not be what you want"),
                _e("GROUP_CONCAT(name)", "SQLite and MySQL; STRING_AGG elsewhere"),
            ),
        ),
        Section(
            "Subqueries and CTEs",
            "A query used as a value, a table, or a name.",
            (
                _e("WHERE id IN (SELECT user_id FROM orders)", "a list of values"),
                _e("WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id)", "often faster than IN"),
                _e("WHERE amount > (SELECT AVG(amount) FROM orders)", "one value, compared against"),
                _e("FROM (SELECT city, COUNT(*) AS n FROM users GROUP BY city) t", "a query as a table; it needs an alias"),
                _e("WITH recent AS (\n    SELECT * FROM orders WHERE paid\n)\nSELECT * FROM recent;", "a CTE: the same thing, readable"),
                _e("WITH a AS (...), b AS (...)", "chain them; b can use a"),
                _e("NOT IN (SELECT user_id FROM orders)", "beware: one NULL makes it match nothing"),
            ),
        ),
        Section(
            "Changing data",
            "Write these with a WHERE before you write the verb.",
            (
                _e("INSERT INTO users (name, age) VALUES ('Ada', 36);", "name the columns; order is not a contract"),
                _e("INSERT INTO users (name) VALUES ('Ada'), ('Bob');", "several rows in one statement"),
                _e("UPDATE users SET age = 37 WHERE id = 1;", "no WHERE updates every row"),
                _e("UPDATE users SET seen = seen + 1 WHERE id = 1;", "a column can read itself"),
                _e("DELETE FROM users WHERE id = 1;", "no WHERE empties the table"),
                _e("SELECT * FROM users WHERE id = 1;", "run the SELECT first, every time"),
                _e("BEGIN;\nUPDATE ...;\nCOMMIT;", "ROLLBACK; instead if it looks wrong"),
                _e("INSERT INTO t SELECT * FROM other;", "insert the result of a query"),
            ),
        ),
        Section(
            "Tables and keys",
            "Enough to create something and know why it is shaped that way.",
            (
                _e("CREATE TABLE users (\n    id INTEGER PRIMARY KEY,\n    name TEXT NOT NULL\n);", "SQLite types; others differ"),
                _e("PRIMARY KEY", "unique, not null, one per table"),
                _e("FOREIGN KEY (user_id) REFERENCES users(id)", "the id must exist over there"),
                _e("NOT NULL", "the cheapest bug prevention there is"),
                _e("UNIQUE", "no two rows may share it"),
                _e("DEFAULT 0", "used when the insert omits the column"),
                _e("CREATE INDEX idx_users_email ON users(email);", "speeds reads, slows writes"),
                _e("ALTER TABLE users ADD COLUMN city TEXT;", "adding is portable; dropping is not"),
                _e("DROP TABLE users;", "gone, with the data"),
            ),
        ),
        Section(
            "Shaping the output",
            "Text, numbers, dates and conditionals.",
            (
                _e("SELECT name AS full_name", "AS is optional and worth writing"),
                _e("SELECT first || ' ' || last", "standard concatenation; MySQL wants CONCAT"),
                _e("UPPER(name)\nLOWER(name)", "case, for display or comparison"),
                _e("LENGTH(name)", "characters"),
                _e("TRIM(name)", "strips the spaces users type"),
                _e("ROUND(amount, 2)", "two decimal places"),
                _e("CAST(price AS INTEGER)", "portable conversion"),
                _e("CASE WHEN age < 18 THEN 'minor'\n     ELSE 'adult' END", "SQL's if; ELSE gives NULL when omitted"),
                _e("DATE('now')", "SQLite; CURRENT_DATE is the portable one"),
                _e("ORDER BY created_at DESC", "newest first"),
            ),
        ),
        Section(
            "Window functions",
            "A calculation across other rows, without collapsing them.",
            (
                _e("ROW_NUMBER() OVER (ORDER BY score DESC)", "1, 2, 3 with no ties"),
                _e("RANK() OVER (ORDER BY score DESC)", "ties share a rank, then it skips"),
                _e("DENSE_RANK() OVER (ORDER BY score DESC)", "ties share a rank, no gap after"),
                _e("PARTITION BY city", "restart the numbering per group"),
                _e("ROW_NUMBER() OVER (\n    PARTITION BY city ORDER BY score DESC\n)", "best per city: keep where it equals 1"),
                _e("SUM(amount) OVER (ORDER BY day)", "a running total"),
                _e("LAG(score) OVER (ORDER BY day)", "the previous row's value"),
                _e("LEAD(score) OVER (ORDER BY day)", "the next row's value"),
            ),
        ),
    ),
)

register(SHEET)
