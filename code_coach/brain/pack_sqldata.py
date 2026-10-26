"""The SQL Data Pack: eight SQL-only activities about CHANGING data and the rules around it - UPDATE, DELETE, INSERT ... SELECT
and defaults, upserts, constraints, ALTER TABLE, views and transactions.

After Update, After Delete, Insert & Default, Upsert, Constraint Quiet, Alter & Default, View Says, Transaction Rollback
(ids `sd_*`, group "SQL data and DDL"). Each has only a SQL generator (`make_sql`), built from 40+ templates, so it is played
under the SQL language of the app's picker (SQLite semantics). The templates are in `_sqldata_update.py`,
`_sqldata_insert.py`, `_sqldata_rules.py` and `_sqldata_state.py`; every answer is modelled by hand with
`_sqldata_model.py` (the relational model of `_sql_model.py` extended with writes: rows that obey NOT NULL, CHECK, UNIQUE and
DEFAULT, upserts, ALTER TABLE, snapshots for transactions) and tests/test_brain_packs.py runs every script in a fresh in-memory
SQLite (tests/sql_oracle.py). This file only wires the templates into Activities.

THE ITEM CONVENTION is the SQL core pack's (see `_sql_model.py`): the prompt is the whole script ending in the query asked
about, the answer is what the LAST row-returning statement prints, ONE value. Two rules of this pack: a statement that would
fail aborts the driver's script, so no item depends on an error (the constraint items use OR IGNORE, ON CONFLICT and
friends); and a script that uses BEGIN has a `COMMIT;` after its setup (the runner's Python opens a transaction at the first
INSERT by itself).
"""

from __future__ import annotations

from . import _sqldata_delete as delete
from . import _sqldata_insert as insert
from . import _sqldata_rules as rules
from . import _sqldata_state as state
from . import _sqldata_update as update
from . import _sqldata_upsert as upsert
from ._model import Pool
from .items import Activity

GROUP = "SQL data and DDL"

#: What every SQL blurb says about the answer.
NOTE = " The answer is one value: a number, a word or NULL."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("sd_update", "After Update", "UPDATE with and without WHERE, with NULLs, CASE and subqueries: what does the table hold afterwards?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(update.UPDATES), group=GROUP,
             concepts=("update", "set-clause", "where-clause", "null", "case-expression", "subquery", "changes"), oracle="value"),
    Activity("sd_delete", "After Delete", "DELETE with WHERE, subqueries, NULL traps and cascades: what is left in the table?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(delete.DELETES), group=GROUP,
             concepts=("delete", "where-clause", "not-in", "null", "subquery", "foreign-key", "autoincrement", "changes"),
             oracle="value"),
    Activity("sd_insert", "Insert & Default", "Multi-row INSERT, INSERT ... SELECT, omitted columns and DEFAULT values: what ends up in the table?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(insert.INSERTS), group=GROUP,
             concepts=("insert", "default", "insert-select", "primary-key", "null", "type-affinity", "typeof", "changes"),
             oracle="value"),
    Activity("sd_upsert", "Upsert", "INSERT OR REPLACE, OR IGNORE and ON CONFLICT DO UPDATE: which row and which value is left?" + NOTE,
             "What does the last SELECT return?", 10, "type", 8.0, 32.0, make_sql=Pool(upsert.UPSERTS), group=GROUP,
             concepts=("upsert", "insert", "on-conflict", "unique", "primary-key", "replace", "excluded", "changes"),
             oracle="value"),
    Activity("sd_constraint", "Constraint Quiet", "UNIQUE, PRIMARY KEY, NOT NULL and CHECK with OR IGNORE: which rows survive?" + NOTE,
             "What does the last SELECT return?", 10, "type", 8.0, 32.0, make_sql=Pool(rules.CONSTRAINTS), group=GROUP,
             concepts=("constraint", "unique", "primary-key", "not-null", "check-constraint", "or-ignore", "null", "autoincrement"),
             oracle="value"),
    Activity("sd_alter", "Alter & Default", "ALTER TABLE, DEFAULT values, RENAME and DROP: what do the old rows show now?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(rules.ALTERS), group=GROUP,
             concepts=("alter-table", "default", "add-column", "rename", "drop-column", "ddl", "null", "typeof"),
             oracle="value"),
    Activity("sd_view", "View Says", "A VIEW is a saved query: after the table changes, what does the view show?" + NOTE,
             "What does the last SELECT return?", 10, "type", 8.0, 32.0, make_sql=Pool(state.VIEWS), group=GROUP,
             concepts=("view", "cte", "subquery", "create-view", "live-view", "union", "join", "ddl"), oracle="value"),
    Activity("sd_txn", "Transaction Rollback", "BEGIN, COMMIT, ROLLBACK and SAVEPOINT: what is left once the transaction is over?" + NOTE,
             "What does the last SELECT return?", 10, "type", 8.0, 32.0, make_sql=Pool(state.TXNS), group=GROUP,
             concepts=("transaction", "rollback", "commit", "savepoint", "begin", "atomicity", "ddl", "autoincrement"),
             oracle="value"),
)
