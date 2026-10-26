"""The SQL Deeper Queries Pack: eight SQL-only activities that go past the core pack - aggregates with NULLs and filters, set
operations, self joins, subqueries, CTEs and recursion, LIKE / GLOB patterns, date functions on fixed dates, and multi-key
ordering.

Aggregate Mix, Set Operation, Self Join, Subquery Value, CTE Chain, Pattern Match, Date Math, Multi-key Order. Each has only a SQL
generator (`make_sql`), built from 40+ templates, so they are played under the SQL language of the app's picker (SQLite semantics).
The templates are in `_sqlquery_*.py`; every answer is modelled by hand with `_sql_model.py` and `_sqlquery_model.py`, and
tests/test_brain_packs.py runs every script in a fresh in-memory SQLite (tests/sql_oracle.py). This file only wires the templates
into Activities. The item convention is the SQL core pack's (see `_sql_model.py`): the prompt is the whole script and the answer
is what the LAST statement that returns rows prints.
"""

from __future__ import annotations

from . import _sqlquery_agg as agg
from . import _sqlquery_cte as cte
from . import _sqlquery_date as date
from . import _sqlquery_order as order
from . import _sqlquery_pat as pat
from . import _sqlquery_self as selfjoin
from . import _sqlquery_sub as sub
from . import _sqlquery_sets as sets
from ._model import Pool
from .items import Activity

GROUP = "SQL deeper queries"

#: What every SQL blurb says about the answer.
NOTE = " The answer is one value: a number, a word or NULL."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("sq_agg", "Aggregate Mix", "COUNT(DISTINCT), SUM and AVG with NULLs, CASE and FILTER inside aggregates: what does it return?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(agg.AGG), group=GROUP,
             concepts=("aggregate", "distinct", "null", "filter", "case-expression", "group-concat", "sum", "average"),
             oracle="value"),
    Activity("sq_set", "Set Operation", "UNION, UNION ALL, INTERSECT and EXCEPT with repeats and NULLs: how many rows, or which value?" + NOTE,
             "What does the last SELECT return?", 10, "type", 7.0, 28.0, make_sql=Pool(sets.SETS), group=GROUP,
             concepts=("union", "union-all", "intersect", "except", "set-operation", "duplicate", "null"),
             oracle="value"),
    Activity("sq_self", "Self Join", "A table joined to itself: bosses, neighbouring rows, pairs and friends of friends. How many, or which?" + NOTE,
             "What does the last SELECT return?", 8, "type", 9.0, 36.0, make_sql=Pool(selfjoin.SELF), group=GROUP,
             concepts=("self-join", "join", "alias", "left-join", "inner-join", "pair", "hierarchy"),
             oracle="value"),
    Activity("sq_sub", "Subquery Value", "Subqueries in SELECT, FROM and WHERE, IN against EXISTS, correlated 'above its own group': what value comes out?" + NOTE,
             "What does the last SELECT return?", 9, "type", 9.0, 36.0, make_sql=Pool(sub.SUB), group=GROUP,
             concepts=("subquery", "correlated-subquery", "exists", "in-operator", "derived-table", "scalar-subquery", "null"),
             oracle="value"),
    Activity("sq_cte", "CTE Chain", "WITH queries that build on each other, and WITH RECURSIVE series, factorials and tree walks: what is the final value?" + NOTE,
             "What does the last SELECT return?", 9, "type", 10.0, 40.0, make_sql=Pool(cte.CTE), group=GROUP,
             concepts=("cte", "recursion", "recursive-cte", "subquery", "with-clause", "series", "tree"),
             oracle="value"),
    Activity("sq_pat", "Pattern Match", "LIKE, GLOB, ESCAPE and the order of text: which rows match, and what does it return?" + NOTE,
             "What does the last SELECT return?", 12, "type", 6.0, 24.0, make_sql=Pool(pat.PAT), group=GROUP,
             concepts=("like-operator", "glob", "wildcard", "escape", "pattern-matching", "case-sensitivity", "collation", "between"),
             oracle="value"),
    Activity("sq_date", "Date Math", "date(), strftime() and julianday() on fixed dates: month overflow, weekdays, day counts. What does it return?" + NOTE,
             "What does the last SELECT return?", 10, "type", 8.0, 32.0, make_sql=Pool(date.DATE), group=GROUP,
             concepts=("date-function", "strftime", "julian-day", "date-arithmetic", "iso-date", "text-comparison"),
             oracle="value"),
    Activity("sq_order", "Multi-key Order", "ORDER BY two keys with ties and NULLs, LIMIT and OFFSET, ranks and the top rows per group: which value comes out?" + NOTE,
             "What does the last SELECT return?", 10, "type", 9.0, 36.0, make_sql=Pool(order.ORDER), group=GROUP,
             concepts=("order-by", "tie", "null", "limit", "offset", "rank", "dense-rank", "window-function", "partition"),
             oracle="value"),
)
