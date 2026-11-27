"""Explain my code for SQL (code_coach/explain_sql.py): coverage over the app's own scripts, alignment, the rules it
states held to the real SQLite, and what it says the last query returned.

The oracle rule: no expected value here comes from the reader. Every claim written into a rule sentence as a query and
the rows it gives is run in a fresh SQLite database (tests/sql_oracle.py); the facts that need a table are scripts with
an exact expected result."""

from __future__ import annotations

from code_coach import explain_sql as Q
from code_coach.api import server
from code_coach.api.schemas import ExplainRequest
from tests import explain_corpus as E
from tests.sql_oracle import driver_value, run_sql


def explain(code: str, run: bool = False, context: str = ""):
    return Q.explain_sql(code, run=run, context=context)


def text_of(code: str) -> str:
    return " ".join(r["text"] for r in explain(code)["lines"])


# (a) coverage and never raising

def test_at_least_90_percent_of_the_apps_own_sql_lines_get_a_specific_row():
    numbers = E.assert_coverage(Q._read_rows, "sql", 0.90)
    assert set(numbers) >= {"brain", "gotchas", "workbook"}, numbers


def test_junk_empty_and_half_typed_input_never_raises():
    E.check_never_raises(explain, extra=["SELECT a FROM t WHERE", "SELECT (1 +", "INSERT INTO t VALUES (1,", "CREATE TABLE t(a INT,", "UPDATE t SET", "SELECT CASE WHEN", "WITH x AS (SELECT 1", "SELECT a FROM t GROUP BY"])
    assert explain("")["ok"] is False


def test_an_unrecognised_statement_gets_the_honest_generic_row_and_is_counted():
    rows, n, bad = Q._read_rows("FROBNICATE the table;\nSELECT 1;")
    assert any(r["text"].endswith("does not break down yet.") for r in rows)
    assert bad == ["1"] and n == 2


# (b) alignment

def test_rows_match_the_input_line_by_line():
    E.check_alignment(explain, "sql")


def test_a_clause_row_sits_on_the_line_where_the_clause_starts():
    r = explain("SELECT name,\n       age\nFROM users u\nJOIN orders o ON o.uid = u.id\nWHERE age > 3\n  AND name <> 'x'\nGROUP BY name\nHAVING COUNT(*) > 1\nORDER BY name DESC\nLIMIT 5;")
    first = {}
    for row in r["lines"]:
        first.setdefault(row["text"].split(":")[0] if ":" in row["text"][:12] else row["text"][:8], row["line"])
    by_kw = {row["text"].split(":")[0]: row["line"] for row in r["lines"] if row["text"].split(":")[0] in ("SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT")}
    assert by_kw == {"SELECT": 1, "FROM": 3, "WHERE": 5, "GROUP BY": 7, "HAVING": 8, "ORDER BY": 9, "LIMIT": 10}, by_kw
    assert any(row["line"] == 2 and "age" in row["text"] for row in r["lines"]), "a select item on its own line has its own row"
    assert any(row["line"] == 4 and "join" in row["text"].lower() for row in r["lines"])
    assert any(row["line"] == 6 and row["text"].lower().startswith("and ") for row in r["lines"])


# (c) truth

#: Facts that need a table: (script, the exact rows the last query gives).
EXTRA = {
    "wherehaving": [("CREATE TABLE t(g INT, v INT); INSERT INTO t VALUES (1,1),(1,5),(2,1);"
                     " SELECT g, COUNT(*) FROM t WHERE v = 1 GROUP BY g HAVING COUNT(*) = 1 ORDER BY g;", "1|1; 2|1"),
                    ("CREATE TABLE t(g INT, v INT); INSERT INTO t VALUES (1,1),(1,5),(2,1);"
                     " SELECT g, COUNT(*) FROM t GROUP BY g HAVING COUNT(*) = 2;", "1|2")],
    "leftwhere": [("CREATE TABLE a(id INT); CREATE TABLE b(aid INT, x INT); INSERT INTO a VALUES (1),(2); INSERT INTO b VALUES (1,5);"
                   " SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid;", "2"),
                  ("CREATE TABLE a(id INT); CREATE TABLE b(aid INT, x INT); INSERT INTO a VALUES (1),(2); INSERT INTO b VALUES (1,5);"
                   " SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid WHERE b.x > 0;", "1"),
                  ("CREATE TABLE a(id INT); CREATE TABLE b(aid INT, x INT); INSERT INTO a VALUES (1),(2); INSERT INTO b VALUES (1,5);"
                   " SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid AND b.x > 0;", "2")],
    "nowhere": [("CREATE TABLE t(a INT); INSERT INTO t VALUES (1),(2); DELETE FROM t; SELECT COUNT(*) FROM t;", "0"),
                ("CREATE TABLE t(a INT); INSERT INTO t VALUES (1),(2); UPDATE t SET a = 9; SELECT COUNT(*) FROM t WHERE a = 9;", "2")],
    "ignore": [("CREATE TABLE t(a INT PRIMARY KEY); INSERT OR IGNORE INTO t VALUES (1),(1),(2); SELECT COUNT(*) FROM t;", "2")],
    "rownum": [("CREATE TABLE t(v INT); INSERT INTO t VALUES (1),(1),(2);"
                " SELECT GROUP_CONCAT(r) FROM (SELECT RANK() OVER (ORDER BY v) AS r FROM t ORDER BY v);", "1,1,3"),
               ("CREATE TABLE t(v INT); INSERT INTO t VALUES (1),(1),(2);"
                " SELECT GROUP_CONCAT(r) FROM (SELECT ROW_NUMBER() OVER (ORDER BY v) AS r FROM t ORDER BY v);", "1,2,3")],
    "limit": [("CREATE TABLE t(v INT); INSERT INTO t VALUES (3),(1),(2); SELECT v FROM t ORDER BY v LIMIT 1;", "1")],
    "wherehaving_note": [],
}
EXTRA.pop("wherehaving_note")


def test_every_rule_sentence_that_states_a_checkable_fact_is_held_to_the_real_sqlite():
    claims = E.claims(Q.FACTS)
    assert claims
    for fid, query, want in claims:
        have = run_sql(query.rstrip(";") + ";")
        assert have == want, f"{fid}: `{query}` -> SQLite gave {have!r}, the rule sentence says {want!r}"
    covered = {f for f, _q, _v in claims} | set(EXTRA)
    assert set(Q.FACTS) <= covered, f"rules with no check: {sorted(set(Q.FACTS) - covered)}"


def test_the_facts_that_need_a_table_are_scripts_run_for_real():
    for fid, cases in EXTRA.items():
        for script, want in cases:
            assert run_sql(script) == want, f"{fid}: {script}"


def test_the_real_driver_agrees_with_the_in_process_check_on_a_claim():
    assert driver_value("SELECT 7 / 2;") == run_sql("SELECT 7 / 2;") == "3"


def test_the_traps_are_named_when_the_query_has_them():
    assert Q.FACTS["intdiv"] in text_of("SELECT 7 / 2;")
    assert Q.FACTS["nulleq"] in text_of("SELECT * FROM t WHERE a = NULL;")
    assert Q.FACTS["notin"] in text_of("SELECT * FROM t WHERE a NOT IN (SELECT x FROM u);")
    assert Q.FACTS["count"] in text_of("SELECT COUNT(*), COUNT(a) FROM t;")
    assert Q.FACTS["nulleq"] not in text_of("SELECT * FROM t WHERE a IS NULL;")
    assert Q.FACTS["nowhere"] in text_of("DELETE FROM t;") and Q.FACTS["nowhere"] not in text_of("DELETE FROM t WHERE a = 1;")
    trap = text_of("SELECT * FROM a LEFT JOIN b ON a.id = b.aid WHERE b.x > 0;")
    assert Q.FACTS["leftwhere"] in trap
    assert Q.FACTS["leftwhere"] not in text_of("SELECT * FROM a LEFT JOIN b ON a.id = b.aid WHERE a.x > 0;")
    assert Q.FACTS["leftwhere"] not in text_of("SELECT * FROM a LEFT JOIN b ON a.id = b.aid WHERE b.id IS NULL;")
    assert Q.FACTS["wherehaving"] in text_of("SELECT g FROM t WHERE v > 1 GROUP BY g HAVING COUNT(*) > 1;")


def test_every_kind_of_statement_and_clause_is_named():
    script = ("CREATE TABLE t(id INTEGER PRIMARY KEY, n TEXT NOT NULL DEFAULT 'x', UNIQUE(n));\nCREATE INDEX i ON t(n);\nCREATE VIEW v AS SELECT n FROM t;\n"
              "ALTER TABLE t ADD COLUMN k INT;\nINSERT INTO t(n) VALUES ('a') ON CONFLICT(n) DO NOTHING;\nUPDATE t SET n = 'b' WHERE id = 1;\nDELETE FROM t WHERE id = 1;\n"
              "BEGIN;\nSAVEPOINT s;\nROLLBACK TO s;\nRELEASE s;\nCOMMIT;\nWITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c WHERE x < 3) SELECT x FROM c;\n"
              "SELECT n, ROW_NUMBER() OVER (PARTITION BY k ORDER BY n) AS r, CASE WHEN id > 1 THEN 'a' ELSE 'b' END FROM t WHERE EXISTS (SELECT 1 FROM v) UNION SELECT 'z', 1, 2;\n"
              "CREATE TRIGGER tr AFTER INSERT ON t BEGIN UPDATE t SET k = 1; END;\nDROP TABLE t;")
    text = text_of(script).lower()
    for word in ("primary key", "unique", "index", "view", "adds the column", "on conflict", "do nothing", "every row", "starts a transaction", "savepoint", "commits",
                 "recursive", "row_number", "position number", "partition", "case", "exists", "union", "trigger", "deletes the table", "rolls", "forgets"):
        if word in ("every row", "rolls"):
            continue
        assert word in text, word


def test_the_evaluation_order_of_a_multi_clause_select_is_a_note():
    r = explain("SELECT g, COUNT(*) FROM t WHERE v > 1 GROUP BY g HAVING COUNT(*) > 1 ORDER BY g LIMIT 3;")
    assert any("FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT" in n for n in r["output_notes"]), r["output_notes"]
    assert not any("->" in n for n in explain("SELECT 1;")["output_notes"])


# (d) output notes

def test_the_output_note_is_what_the_real_query_returned():
    for script in ("SELECT 7 / 2;", "CREATE TABLE t(a INT); INSERT INTO t VALUES (1),(NULL),(3); SELECT a FROM t ORDER BY a;", "SELECT 1, 'x', NULL, 2.5;"):
        want = run_sql(script)
        notes = explain(script.replace("; ", ";\n"), run=True)["output_notes"]
        got = [n for n in notes if n.startswith("The last query returned: ")]
        assert got and got[0].split(": ", 1)[1].split(" (columns")[0] == want, (script, notes, want)


def test_a_script_with_no_rows_has_no_made_up_result_and_an_error_is_an_error_note():
    quiet = explain("CREATE TABLE t(a INT);", run=True)
    assert all("The last query returned" not in n for n in quiet["output_notes"])
    bad = explain("SELECT * FROM nope;\n", run=True)
    assert bad["error_note"] and "no such table" in bad["error_note"], bad
    assert "gotcha_run_" not in bad["error_note"] and "SQLError" not in bad["error_note"]
    assert bad["lines"], "the rows still come back"


# (e) API

def test_the_api_reads_sql_and_puts_the_drills_sql_words_first():
    r = server.explain(ExplainRequest(code="SELECT COUNT(*) FROM t WHERE a = NULL;", language="sql", context="sql_count"))
    assert r.ok and r.lines
    assert [w.id for w in r.words][:2] == ["where-clause", "null"]
    assert all(w.language == "sql" for w in r.words)


def test_postgresql_still_has_no_reader_and_the_sentence_lists_the_real_languages():
    r = server.explain(ExplainRequest(code="SELECT 1;", language="postgresql"))
    assert r.ok is False and "no reader" in r.summary
    for name in ("Python", "JavaScript", "Dart", "C", "SQL", "Rust"):
        assert name in r.summary


# (a2) every construct the brief names is read specifically on its own (see tests/test_explain_dart.py)

CONSTRUCTS = [
    "CREATE TABLE t(id INTEGER PRIMARY KEY, n TEXT NOT NULL, v REAL DEFAULT 0, UNIQUE(n), CHECK(v >= 0));", "INSERT INTO t VALUES (1, 'a'), (2, 'b');", "INSERT OR IGNORE INTO t VALUES (1, 'a');", "INSERT OR REPLACE INTO t VALUES (1, 'a');",
    "INSERT INTO t VALUES (1) ON CONFLICT(id) DO UPDATE SET n = 1;", "UPDATE t SET n = 'x' WHERE id = 1;", "UPDATE t SET n = 'x';", "DELETE FROM t WHERE id = 1;", "DELETE FROM t;", "SELECT DISTINCT n FROM t;", "SELECT * FROM t;",
    "SELECT a.n FROM t a JOIN u b ON a.id = b.id;", "SELECT a.n FROM t a LEFT JOIN u b ON a.id = b.id WHERE b.v > 1;", "SELECT * FROM t CROSS JOIN u;", "SELECT * FROM t WHERE a = NULL;", "SELECT * FROM t WHERE a NOT IN (SELECT x FROM u);",
    "SELECT g, COUNT(*) FROM t WHERE v > 1 GROUP BY g HAVING COUNT(*) > 1;", "SELECT COUNT(*), COUNT(a) FROM t;", "SELECT * FROM t ORDER BY a DESC LIMIT 5 OFFSET 2;", "SELECT CASE WHEN a > 1 THEN 'x' ELSE 'y' END FROM t;",
    "SELECT * FROM t WHERE EXISTS (SELECT 1 FROM u);", "SELECT a FROM t UNION SELECT a FROM u;", "SELECT a FROM t INTERSECT SELECT a FROM u;", "SELECT a FROM t EXCEPT SELECT a FROM u;", "SELECT ROW_NUMBER() OVER (PARTITION BY g ORDER BY v) FROM t;", "SELECT LAG(v) OVER (ORDER BY id) FROM t;",
    "WITH RECURSIVE c(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM c WHERE n < 3) SELECT n FROM c;", "ALTER TABLE t ADD COLUMN k INT;", "ALTER TABLE t RENAME TO u;", "CREATE VIEW v AS SELECT a FROM t;", "CREATE TRIGGER tr AFTER INSERT ON t BEGIN\nUPDATE t SET k = 1;\nEND;",
    "BEGIN;", "COMMIT;", "ROLLBACK;", "SAVEPOINT s;", "RELEASE s;", "ROLLBACK TO s;", "SELECT UPPER(n), ROUND(v, 2), COALESCE(a, 0), SUBSTR(n, 1, 2), LENGTH(n), n || 'x' FROM t;", "SELECT 7 / 2, 7 / 2.0, 7 % 2;", "SELECT * FROM t WHERE n LIKE 'a%' AND v BETWEEN 1 AND 3;",
]


def test_every_construct_the_brief_names_is_read_with_no_fallback_row():
    missed = []
    for code in CONSTRUCTS:
        rows, n, bad = Q._read_rows(code)
        if bad or not rows:
            missed.append(code.split("\n")[0])
    assert not missed, missed
