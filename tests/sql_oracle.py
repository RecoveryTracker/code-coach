"""The SQL oracle for Brain Drills: hold a SQL script to the real SQLite, in-process.

Each item is a complete script (`CREATE TABLE ...; INSERT ...; SELECT ...;`) that is run in a FRESH in-memory database
through Python's own `sqlite3` - one `sqlite3.connect(":memory:")` per item, so nothing leaks from one item to the next - and
its value is what the Gotchas SQL driver (code_coach/gotchas/toolchains.py, `SQL_DRIVER`, which "Run it" uses) prints:
the rows of the LAST statement that returns rows, each row's columns joined with `|`, the rows joined with `; `, NULL
written `NULL`, a real the way Python's `repr` writes it (`2.0`, `0.30000000000000004`), text bare. No rows: the empty
string. An error: `ERROR: <message>` (so a bad template fails the oracle test and names the message).

It is fast (a script takes a fraction of a millisecond), so there is no batching: a loop. `sql_values(programs)` is the
whole API; `driver_value(program)` runs the real driver (a subprocess, ~0.2 s) for the test that holds this module to it.

What a SQL item is (written up in code_coach/brain/_sql_model.py): the program is `item.check`, or the prompt when `check`
is empty; statements end with `;`, and the answer is the value above.
"""

from __future__ import annotations

import sqlite3


def _split(text: str) -> list[str]:
    """The driver's splitting: a statement ends at a `;` where SQLite says the statement is complete."""
    statements, start = [], 0
    for i, ch in enumerate(text):
        if ch == ";" and sqlite3.complete_statement(text[start:i + 1]):
            statements.append(text[start:i + 1].strip())
            start = i + 1
    if text[start:].strip():
        statements.append(text[start:].strip())
    return statements


def _show(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, bytes):
        return "x'" + value.hex() + "'"
    return str(value)


def run_sql(program: str) -> str:
    """The value of one script, as the driver prints it (see the module docstring)."""
    db = sqlite3.connect(":memory:")
    rows = None
    try:
        for statement in _split(program):
            cursor = db.execute(statement)
            if cursor.description is not None:
                rows = cursor.fetchall()
    except sqlite3.Error as exc:
        return f"ERROR: {exc}"
    finally:
        db.close()
    if rows is None:
        return ""
    return "; ".join("|".join(_show(v) for v in row) for row in rows)


def sql_values(programs: list[str]) -> list[str]:
    """The value of each program, each in its own fresh in-memory database."""
    return [run_sql(p) for p in programs]


def driver_value(program: str) -> str:
    """What the real runner (the one "Run it" uses) prints for the program: its stdout, or `ERROR: <stderr>`."""
    from code_coach.gotchas.runner import run_program

    got = run_program("sql", program)
    return got.stdout.strip() if got.ok else "ERROR: " + got.stderr.strip()
