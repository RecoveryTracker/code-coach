"""SQL case files: a small mystery, solved by querying real PostgreSQL.

The shape is SQL Murder Mystery's. You are handed a story and some
tables, and every step asks one question whose answer is in the data:
a name, a count, a date. You explore with any queries you like, then
type the answer. The next step only makes sense once you have it, so a
case is a chain of queries where each one is aimed by the last - which
is what querying is for, and what a list of unrelated exercises never
shows.

Where the data lives
--------------------
In temporary tables, made at the start of every run and gone at the
end. A case's setup is put in front of your query and the whole lot
goes through the ordinary PostgreSQL runner, inside its BEGIN and
ROLLBACK. So a case never touches the practice tables, two cases can
both have a table called people, and a DELETE in the middle of an
investigation costs nothing: the next run starts from the same data.

Where the answers come from
---------------------------
Each step has an answer written by hand and a reference query, and the
suite runs the query on the real server and insists it returns that
answer and only that answer. Each step also has a decoy - the query
someone plausibly writes first, such as = NULL instead of IS NULL - and
the suite insists the decoy does not return the answer. That is what
proves the step tests the idea it is about.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    """One question in a case."""

    question: str
    #: The answer as a person would type it. Compared loosely - see same().
    answer: str
    #: A query that returns exactly the answer, one row, one column.
    reference: str
    #: The tempting wrong query. Must not return the answer.
    decoy: str
    hint: str
    #: What the step taught, shown once it is solved.
    lesson: str


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    level: int
    story: str
    #: CREATE TEMP TABLE and INSERT statements, nothing else.
    setup: str
    steps: tuple[Step, ...]
    #: Shown when the last step is solved.
    ending: str


def normal(text: str) -> str:
    """An answer as compared: case, outer quotes and spacing ignored."""
    text = " ".join(str(text).split()).lower()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        text = text[1:-1].strip()
    return text


def same(given: str, answer: str) -> bool:
    return bool(normal(given)) and normal(given) == normal(answer)


_TABLE = re.compile(
    r"CREATE\s+TEMP\s+TABLE\s+(\w+)\s*\((.*?)\);", re.IGNORECASE | re.DOTALL)


def tables(case: Case) -> list[dict]:
    """The tables a case has, with their columns, for the screen.

    Read from the setup rather than written out again, so the list
    cannot drift from the data. The suite checks it against what the
    server itself says the tables are.
    """
    out = []
    for name, body in _TABLE.findall(case.setup):
        columns = []
        for raw in body.split(","):
            words = raw.split()
            # Whole first word: a column called check_in is not a CHECK.
            if len(words) >= 2 and words[0].upper() not in (
                    "PRIMARY", "FOREIGN", "UNIQUE", "CHECK", "CONSTRAINT"):
                columns.append({"name": words[0], "type": words[1].lower()})
        out.append({"name": name, "columns": columns})
    return out


def run_query(case: Case, sql: str) -> tuple[str, str, int]:
    """Your query against the case's data. Same contract as run_postgres."""
    from code_coach.pg_runner import _split, run_postgres

    if not _split(sql or ""):
        return "", "Nothing to run — write a query first.", 0
    return run_postgres(case.setup + "\n" + sql)


def values(out: str) -> list[str]:
    """The rows of a one-column result, as the runner prints them.

    The runner draws a header, a line of dashes and then one row per
    line, or says "(no rows)". Only used on the reference and decoy
    queries, which are written to return a single column.
    """
    lines = out.strip("\n").splitlines()
    if len(lines) < 2 or not set(lines[1].strip()) <= {"-", " "}:
        return []
    return [line.strip() for line in lines[2:] if line.strip()]


def cases() -> tuple[Case, ...]:
    from code_coach.casefiles.content import CASES

    return CASES


def case(case_id: str) -> Case | None:
    return next((c for c in cases() if c.id == case_id), None)
