"""Run SQL against a small in-memory sample database.

SQL doesn't print — it returns rows — so Run means "execute this query and
show the result as a table". sqlite3 ships with Python, so this needs nothing
installed, unlike the C/C++/Rust toolchains.

The database is rebuilt for every run, so a stray UPDATE or DELETE can't wreck
the next exercise.
"""

from __future__ import annotations

import sqlite3

MAX_ROWS = 50

SCHEMA = """
CREATE TABLE users (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    city    TEXT,
    age     INTEGER,
    email   TEXT,
    active  INTEGER DEFAULT 1
);

CREATE TABLE orders (
    id       INTEGER PRIMARY KEY,
    user_id  INTEGER REFERENCES users(id),
    item     TEXT NOT NULL,
    price    REAL NOT NULL
);

INSERT INTO users (id, name, city, age, email, active) VALUES
    (1, 'Alex',  'Denver', 30, 'alex@example.com',  1),
    (2, 'Bailey','Austin', 24, NULL,                1),
    (3, 'Casey', 'Denver', 41, 'casey@example.com', 0),
    (4, 'Devon', 'Boston', 17, 'devon@example.com', 1),
    (5, 'Erin',  'Austin', 35, NULL,                1);

INSERT INTO orders (id, user_id, item, price) VALUES
    (1, 1, 'keyboard', 45.00),
    (2, 1, 'mouse',    18.50),
    (3, 2, 'monitor',  180.00),
    (4, 3, 'cable',     7.25),
    (5, 5, 'desk',     220.00),
    (6, 5, 'lamp',      32.00);
"""

# Shown in the coach so you know what you're querying.
TABLES_SUMMARY = (
    "users(id, name, city, age, email, active) — 5 rows\n"
    "orders(id, user_id, item, price) — 6 rows"
)


def _as_table(columns: list[str], rows: list[tuple]) -> str:
    """Fixed-width text table — the terminal shows plain text."""
    if not columns:
        return ""
    widths = [len(c) for c in columns]
    shown = rows[:MAX_ROWS]
    for row in shown:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len("NULL" if cell is None else str(cell)))

    def line(cells: list[str]) -> str:
        return "  ".join(c.ljust(widths[i]) for i, c in enumerate(cells)).rstrip()

    out = [line(list(columns)), line(["-" * w for w in widths])]
    for row in shown:
        out.append(
            line(["NULL" if cell is None else str(cell) for cell in row])
        )
    if len(rows) > MAX_ROWS:
        out.append(f"… {len(rows) - MAX_ROWS} more rows")
    return "\n".join(out)


def run_sql(script: str) -> tuple[str, str, int]:
    """(stdout, stderr, exit_code), matching the shape of run_code."""
    statements = [s.strip() for s in script.split(";") if s.strip()]
    if not statements:
        return "", "Nothing to run — write a query first.", 0

    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(SCHEMA)
        out: list[str] = []
        for statement in statements:
            try:
                cursor = conn.execute(statement)
            except sqlite3.Error as exc:
                return "\n\n".join(out), f"SQL error: {exc}", 1
            if cursor.description is None:
                # INSERT/UPDATE/DELETE — report what it touched.
                out.append(f"{cursor.rowcount} row(s) affected.")
                continue
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            if not rows:
                out.append("(no rows)")
            else:
                out.append(_as_table(columns, rows))
        return "\n\n".join(out) + "\n", "", 0
    finally:
        conn.close()
