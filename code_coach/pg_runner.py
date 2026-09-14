"""Run PostgreSQL against the practice database.

Same contract as the SQLite runner — (stdout, stderr, exit_code) — and
the same table formatting, so one set of exercises can be read in
either dialect and the difference on screen is the SQL rather than the
furniture.

Two things are different, and both are about it being a real server.

Everything runs inside a transaction that is rolled back. SQLite's
runner rebuilds the whole database per run, which is free for a file
and would be seconds per query for a server. A transaction gets the
same guarantee for nothing: an UPDATE without a WHERE does exactly what
it really does, you see exactly what it really did, and the next
exercise starts from the same place anyway. The cost is that the few
statements PostgreSQL refuses to run in a transaction — CREATE
DATABASE, VACUUM — cannot be practised here, and say so plainly when
tried.

And the whole script runs in one psql session rather than a process per
statement, because an INSERT followed by a SELECT is one thought and
has to see its own work. The statements are separated in the output by
asking psql to echo a marker between them, which is the only way to
know which result belongs to which statement without parsing SQL.
"""

from __future__ import annotations

import csv
import io
import subprocess

from code_coach import pg_server
from code_coach.sql_runner import MAX_ROWS, _as_table

#: Printed between statements so their results can be told apart. Long
#: and ugly on purpose: it has to be something no query would produce.
MARKER = "<<<CODE_COACH_PG_NEXT>>>"

#: Put every sequence back where the data ends, so the next id an
#: INSERT is handed is the same one on every go. Asked of
#: pg_get_serial_sequence rather than named, so adding a table to the
#: practice data does not mean editing this too.
RESET_SEQUENCES = """
DO $$
DECLARE
    seq text;
    tbl text;
BEGIN
    FOREACH tbl IN ARRAY ARRAY['users', 'orders'] LOOP
        seq := pg_get_serial_sequence(tbl, 'id');
        IF seq IS NOT NULL THEN
            EXECUTE format(
                'SELECT setval(%L, COALESCE((SELECT max(id) FROM %I), 1))',
                seq, tbl);
        END IF;
    END LOOP;
END $$;
"""

#: How long any one script gets. Generous next to the three seconds a
#: program gets — a first connection to a cold server is most of it —
#: and still far short of forever.
TIMEOUT = 20.0


def _split(script: str) -> list[str]:
    """The statements, keeping strings and dollar quotes intact.

    Splitting on semicolons is wrong the moment one appears inside a
    string, and $$ bodies are full of them. This is not a SQL parser
    and does not need to be: it only has to know when a semicolon is
    inside quotes.
    """
    out: list[str] = []
    current: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(script):
        ch = script[i]
        if quote:
            current.append(ch)
            if ch == quote:
                # '' inside a string is an escaped quote, not the end.
                if quote == "'" and script[i + 1: i + 2] == "'":
                    current.append("'")
                    i += 1
                else:
                    quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            current.append(ch)
            i += 1
            continue
        if script.startswith("$$", i):
            end = script.find("$$", i + 2)
            end = len(script) if end == -1 else end + 2
            current.append(script[i:end])
            i = end
            continue
        if ch == ";":
            statement = "".join(current).strip()
            if statement:
                out.append(statement)
            current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    tail = "".join(current).strip()
    if tail:
        out.append(tail)
    return out


def _table_from_csv(chunk: str) -> str:
    """One statement's psql --csv output, as the table the app draws."""
    text = chunk.strip("\n")
    if not text.strip():
        return ""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return ""
    header, body = rows[0], rows[1:]
    # A statement that changes rows prints its tag rather than a table:
    # "UPDATE 3", "INSERT 0 1". One cell, and not a column list anybody
    # would write.
    if len(header) == 1 and not body and " " in header[0]:
        return header[0]
    if not body:
        return "(no rows)"
    return _as_table(header, [tuple(r) for r in body])


def run_postgres(script: str) -> tuple[str, str, int]:
    """(stdout, stderr, exit_code), matching the shape of run_code."""
    statements = _split(script)
    if not statements:
        return "", "Nothing to run — write a query first.", 0

    ok, why = pg_server.start()
    if not ok:
        return "", why, 1

    psql = pg_server._binary("psql")
    if psql is None:
        return "", "psql is missing from the PostgreSQL install.", 1

    # BEGIN and ROLLBACK around the lot: practice cannot outlive its go.
    #
    # The sequence needs saying separately, because a sequence is the
    # one thing a rollback does not undo. That is deliberate in
    # PostgreSQL — two sessions inserting at once must never be handed
    # the same id, so nextval stands outside the transaction — and it
    # means an INSERT practised twenty times hands back a different id
    # every go while the table itself never changes. An exercise cannot
    # have an answer under those conditions.
    #
    # So every go starts by putting the sequences back where the data
    # ends, which makes the database identical at the start of each run
    # rather than nearly identical. Its own statement, and its output is
    # dropped below, so nobody has to look at the plumbing.
    lines = ["BEGIN;", RESET_SEQUENCES, f"\\echo {MARKER}"]
    for i, statement in enumerate(statements):
        if i:
            lines.append(f"\\echo {MARKER}")
        lines.append(statement.rstrip(";") + ";")
    lines.append("ROLLBACK;")

    argv = [
        str(psql),
        "-h", pg_server.HOST,
        "-p", str(pg_server.PORT),
        "-U", pg_server.USER,
        "-d", pg_server.DATABASE,
        "--csv",
        "-q",                      # no "BEGIN"/"ROLLBACK" chatter
        "-v", "ON_ERROR_STOP=1",
        "-P", "null=NULL",         # tell an empty string from a NULL
        "-f", "-",
    ]
    try:
        done = subprocess.run(
            argv,
            input="\n".join(lines),
            capture_output=True,
            timeout=TIMEOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=pg_server.env(),
        )
    except subprocess.TimeoutExpired:
        return "", f"The query took longer than {TIMEOUT:g}s and was stopped.", 1
    except OSError as exc:
        return "", f"Could not run psql: {exc}", 1

    if done.returncode != 0:
        return "", _tidy_error(done.stderr), 1

    # The first chunk is the sequence reset above, which is plumbing.
    chunks = (done.stdout or "").split(MARKER)[1:]
    tables = [_table_from_csv(chunk) for chunk in chunks]
    shown = [t for t in tables if t]
    if not shown:
        return "(no rows)\n", "", 0
    return "\n\n".join(shown) + "\n", "", 0


def _tidy_error(detail: str) -> str:
    """PostgreSQL's error, without the bits about our plumbing.

    psql names the script it was reading, which is stdin here and reads
    as "stdin:3: ERROR". True and confusing: the line number counts the
    BEGIN this runner added, so it is one past what the student wrote.
    The message and its hint are the useful parts, and they are what is
    kept.
    """
    keep: list[str] = []
    for raw in (detail or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        for prefix in ("psql:<stdin>:", "psql:stdin:"):
            if line.startswith(prefix):
                rest = line.split(":", 3)
                line = rest[3].strip() if len(rest) > 3 else line
                break
        keep.append(line)
    return "\n".join(keep[:8]) or "The query failed."


__all__ = ["run_postgres", "MAX_ROWS"]
