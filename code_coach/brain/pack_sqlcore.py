"""The SQL Core Pack: eight SQL-only activities about the language itself - counting rows, NULL logic, groups, joins,
ordering and limiting, scalar arithmetic and text functions, CASE and subqueries, window functions.

SQL Row Count, NULL Logic, Group Result, Join Count, Order & Limit, Scalar Math, Case & Subquery, Window Row. Each has only
a SQL generator (`make_sql`), built from 40-80 templates, so they are played under the SQL language of the app's picker
(SQLite semantics) and never listed under another one. The templates are in `_sqlcore_rows.py`, `_sqlcore_joins.py` and
`_sqlcore_funcs.py`; every answer is modelled by hand with `_sql_model.py` (a tiny relational model: tables are lists of
tuples, NULL is None, conditions are three-valued), and tests/test_brain_packs.py runs every script in a fresh in-memory
SQLite (tests/sql_oracle.py). This file only wires the templates into Activities.

THE ITEM CONVENTION (see `_sql_model.py`): the prompt is a complete SQL script - `CREATE TABLE`, `INSERT INTO t VALUES (...),
(...);`, then the query asked about - and the answer is what the LAST statement that returns rows prints, as the Gotchas SQL
driver prints it: one value (a number, a word, NULL; a real keeps its decimal point). `oracle`: "value".
"""

from __future__ import annotations

from . import _sqlcore_funcs as funcs
from . import _sqlcore_joins as joins
from . import _sqlcore_rows as rows
from ._model import Pool
from .items import Activity

GROUP = "SQL core"

#: What every SQL blurb says about the answer.
NOTE = " The answer is one value: a number, a word or NULL."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("sql_count", "Row Count", "WHERE, BETWEEN, IN, LIKE and NULLs: how many rows does the query count?" + NOTE,
             "What does the last SELECT return?", 10, "type", 6.0, 24.0, make_sql=Pool(rows.COUNT), group=GROUP,
             concepts=("where-clause", "null", "like-operator", "in-operator", "between", "count", "three-valued-logic"),
             oracle="value"),
    Activity("sql_null", "NULL Logic", "NULL is not a value: unknown in, unknown out. What does it return?" + NOTE,
             "What does the last SELECT return?", 12, "type", 5.0, 20.0, make_sql=Pool(rows.NULLS), group=GROUP,
             concepts=("null", "three-valued-logic", "coalesce", "aggregate-function", "count", "null-handling"),
             oracle="value"),
    Activity("sql_group", "Group Result", "GROUP BY and HAVING: what value does the query give?" + NOTE,
             "What does the last SELECT return?", 8, "type", 8.0, 30.0, make_sql=Pool(rows.GROUPS), group=GROUP,
             concepts=("group-by", "having", "aggregate-function", "count", "sum", "subquery"), oracle="value"),
    Activity("sql_join", "Join Count", "Inner, left and cross joins, duplicates and set operations: how many rows?" + NOTE,
             "What does the last SELECT return?", 8, "type", 8.0, 30.0, make_sql=Pool(joins.JOINS), group=GROUP,
             concepts=("join", "inner-join", "left-join", "cross-join", "union", "duplicate"), oracle="value"),
    Activity("sql_order", "Order & Limit", "ORDER BY with NULLs, LIMIT, OFFSET and DISTINCT: which value comes out?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(joins.ORDERS), group=GROUP,
             concepts=("order-by", "limit", "offset", "distinct", "sorting", "null"), oracle="value"),
    Activity("sql_scalar", "Scalar Math", "Integer or real division, remainders, ROUND and text functions: what does it return?" + NOTE,
             "What does the last SELECT return?", 14, "type", 4.0, 16.0, make_sql=Pool(funcs.SCALAR), group=GROUP,
             concepts=("integer-division", "modulo", "round", "string-function", "concatenation", "type-conversion", "typeof"),
             oracle="value"),
    Activity("sql_case", "Case & Subquery", "CASE, scalar subqueries, IN and EXISTS, correlated counts: what does it return?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(funcs.CASES), group=GROUP,
             concepts=("case-expression", "subquery", "exists", "correlated-subquery", "in-operator", "aggregate-function"),
             oracle="value"),
    Activity("sql_window", "Window Row", "ROW_NUMBER, RANK, running totals, LAG and LEAD: what value does that row get?" + NOTE,
             "What does the last SELECT return?", 8, "type", 9.0, 36.0, make_sql=Pool(funcs.WINDOWS), group=GROUP,
             concepts=("window-function", "row-number", "rank", "partition", "running-total", "lag", "lead"),
             oracle="value"),
)
