"""SQL words, part 3: storing and changing data - tables, INSERT / UPDATE / DELETE, upsert, constraints, ALTER TABLE,
views, transactions, triggers and indexes. SQLite semantics (see terms_sql_query.py for how an example's output is
written)."""

from __future__ import annotations

from .entry import Entry, sql

TERMS: list[Entry] = [
    *sql(
        "table",
        "Table, row and column",
        "A table stores data in rows (one record each) and columns (one named kind of value each). A database is a collection of tables.",
        see=("create-table", "primary-key", "select", "query"),
        priority=25,
        aka=("tables", "row", "rows", "column", "columns", "record", "records", "field", "fields", "database", "relation", "schema", "cell", "relational"),
        rules=(
            r"Every row of a table has the same columns, in the same order.",
            r"A table is a set of rows with no built-in order: ask for one with ORDER BY.",
            r"A column has a name and a declared type (INTEGER, TEXT, REAL).",
        ),
        example=r"""
            CREATE TABLE pet (id INTEGER, name TEXT);
            INSERT INTO pet VALUES (1, 'rex'), (2, 'tom');
            SELECT COUNT(*) FROM pet;
        """,
        out=r"2",
    ),
    *sql(
        "query",
        "Query",
        "A request to the database, written in SQL. A SELECT is a query that reads; INSERT, UPDATE and DELETE are statements that change data. Each statement ends with a semicolon.",
        see=("select", "table", "create-table", "subquery"),
        priority=20,
        aka=("queries", "statement", "sql", "sql statement", "command", "sql query", "script", "clause", "keyword", "syntax", "syntax error"),
        rules=(
            r"Keywords (SELECT, FROM, WHERE) are not case-sensitive; text values ('ann') are case-sensitive in comparisons with = in SQLite.",
            r"Text values use single quotes: 'ann'. Double quotes are for names of tables and columns.",
            r"The clauses come in a fixed order: SELECT, FROM, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT.",
        ),
        example=r"""
            SELECT 1 + 2, 'a' = 'A', 'a' IS NOT NULL;
        """,
        out=r"3|0|1",
    ),
    *sql(
        "create-table",
        "CREATE TABLE",
        "CREATE TABLE name (column type constraints, ...) makes a new empty table. IF NOT EXISTS skips it when the table is already there; DROP TABLE deletes the table and its rows.",
        see=("constraint", "primary-key", "alter-table", "type-affinity"),
        priority=50,
        aka=("create", "make a table", "define a table", "drop table", "drop", "schema definition", "ddl", "table definition"),
        detect=(r"(?i)\bcreate\s+(?:temp(?:orary)?\s+)?table\b|\bdrop\s+table\b",),
        rules=(
            r"Each column: a name, a type (INTEGER, REAL, TEXT, BLOB) and optional constraints: id INTEGER PRIMARY KEY, name TEXT NOT NULL.",
            r"CREATE TABLE fails if the name exists, unless you add IF NOT EXISTS.",
            r"DROP TABLE removes the table for good; DELETE FROM removes only the rows.",
        ),
        example=r"""
            CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS t (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            INSERT INTO t (name) VALUES ('a');
            SELECT COUNT(*) FROM t;
        """,
        out=r"1",
    ),
    *sql(
        "insert",
        "INSERT",
        "INSERT INTO table (columns) VALUES (values) adds rows. List several value groups to add several rows at once, or add rows from a query with INSERT INTO ... SELECT.",
        see=("update", "delete", "default-value", "upsert"),
        priority=55,
        aka=("insert into", "add a row", "add rows", "add data", "insert row", "insert values", "bulk insert", "values", "insert select", "insert-select", "insert from select"),
        detect=(r"(?i)\binsert\s+(?:or\s+\w+\s+)?into\b",),
        rules=(
            r"Name the columns: INSERT INTO t (name, age) VALUES ('ann', 30). Leaving the list out means 'all columns, in table order'.",
            r"A column you leave out gets its DEFAULT, or NULL when it has none (an error if it is NOT NULL).",
            r"INSERT INTO t2 SELECT * FROM t copies rows between tables.",
            r"If a constraint is broken the whole INSERT statement fails and adds nothing.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER, name TEXT, age INTEGER DEFAULT 18);
            INSERT INTO t (id, name) VALUES (1, 'ann'), (2, 'bob');
            SELECT id, name, age FROM t ORDER BY id;
        """,
        out=r"1|ann|18; 2|bob|18",
    ),
    *sql(
        "update",
        "UPDATE",
        "UPDATE table SET column = value WHERE condition changes existing rows. Without a WHERE it changes EVERY row.",
        see=("insert", "delete", "where-clause", "transaction"),
        priority=55,
        aka=("update set", "change rows", "modify rows", "change data", "set column", "update statement", "edit rows", "set clause", "set-clause", "set"),
        detect=(r"(?i)\bupdate\s+\w+\s+set\b",),
        rules=(
            r"Always check the WHERE first: UPDATE t SET price = 0; zeroes the whole table.",
            r"All the SET expressions see the OLD row, so SET a = b, b = a swaps the two values.",
            r"Several columns: SET a = 1, b = 2. A calculation is fine: SET qty = qty + 1.",
        ),
        example=r"""
            CREATE TABLE t (a INTEGER, b INTEGER);
            INSERT INTO t VALUES (1, 2);
            UPDATE t SET a = b, b = a;
            SELECT a, b FROM t;
        """,
        out=r"2|1",
    ),
    *sql(
        "delete",
        "DELETE",
        "DELETE FROM table WHERE condition removes the rows that match. Without a WHERE it removes every row, but the (empty) table remains.",
        see=("update", "insert", "create-table", "transaction"),
        priority=55,
        aka=("delete from", "remove rows", "remove row", "delete rows", "truncate", "erase"),
        detect=(r"(?i)\bdelete\s+from\b",),
        rules=(
            r"Test the condition with SELECT first, then change the word to DELETE.",
            r"DELETE removes rows; DROP TABLE removes the table itself.",
            r"A foreign key may refuse the delete, or delete child rows too (ON DELETE CASCADE), when foreign keys are enabled.",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER);
            INSERT INTO t VALUES (1), (2), (3), (4);
            DELETE FROM t WHERE n % 2 = 0;
            SELECT COUNT(*), SUM(n) FROM t;
        """,
        out=r"2|4",
    ),
    *sql(
        "upsert",
        "UPSERT (ON CONFLICT)",
        "INSERT ... ON CONFLICT (column) DO UPDATE SET ... inserts a row, or if one with the same key already exists, updates it instead. 'excluded' is the row you tried to insert.",
        see=("insert", "or-replace", "primary-key", "unique"),
        priority=55,
        aka=("on conflict", "insert or update", "do update", "merge", "update or insert", "on duplicate key", "excluded"),
        detect=(r"(?i)\bon\s+conflict\b",),
        rules=(
            r"The conflict target must be a column (or columns) with a PRIMARY KEY or UNIQUE constraint.",
            r"DO NOTHING ignores the new row; DO UPDATE SET n = n + excluded.n adds to the old value.",
            r"Needs SQLite 3.24 or newer.",
        ),
        example=r"""
            CREATE TABLE hits (page TEXT PRIMARY KEY, n INTEGER);
            INSERT INTO hits VALUES ('home', 1);
            INSERT INTO hits VALUES ('home', 1) ON CONFLICT (page) DO UPDATE SET n = n + excluded.n;
            INSERT INTO hits VALUES ('about', 1) ON CONFLICT (page) DO UPDATE SET n = n + excluded.n;
            SELECT page, n FROM hits ORDER BY page;
        """,
        out=r"about|1; home|2",
    ),
    *sql(
        "or-replace",
        "INSERT OR REPLACE / IGNORE",
        "A conflict clause on INSERT says what to do when a row breaks a UNIQUE or PRIMARY KEY rule. OR IGNORE skips the new row quietly; OR REPLACE deletes the old row and inserts the new one.",
        see=("upsert", "primary-key", "unique", "insert"),
        priority=50,
        aka=("insert or replace", "insert or ignore", "or ignore", "replace into", "or replace", "conflict clause", "on conflict replace", "replace", "replace row"),
        detect=(r"(?i)\binsert\s+or\s+(?:replace|ignore)\b|\breplace\s+into\b",),
        rules=(
            r"OR REPLACE removes the whole old row, so columns you did not mention go back to their defaults (it is not an UPDATE).",
            r"OR IGNORE hides the problem: nothing tells you the row was skipped.",
            r"Without a clause, the default is to fail the statement with an error.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT);
            INSERT INTO t VALUES (1, 'a');
            INSERT OR IGNORE INTO t VALUES (1, 'b');
            INSERT OR REPLACE INTO t VALUES (1, 'c');
            SELECT id, v FROM t;
        """,
        out=r"1|c",
    ),
    *sql(
        "constraint",
        "Constraint",
        "A rule the database enforces on a column or table: PRIMARY KEY, UNIQUE, NOT NULL, CHECK, DEFAULT, FOREIGN KEY. A statement that breaks one fails as a whole and changes nothing.",
        see=("primary-key", "unique", "not-null", "check-constraint", "foreign-key"),
        priority=45,
        aka=("constraints", "integrity", "data integrity", "rules", "validation", "integrity constraint", "table constraint", "column constraint"),
        detect=(r"(?i)\bconstraint\s+\w+",),
        rules=(
            r"The error names the rule, for example 'UNIQUE constraint failed: t.email'.",
            r"Constraints guard the data no matter which program writes to it, unlike checks in application code.",
            r"Name one with CONSTRAINT name ... when you want a clearer message or to drop it later.",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER CHECK (n > 0));
            INSERT INTO t VALUES (5);
            SELECT COUNT(*) FROM t;
        """,
        out=r"1",
    ),
    *sql(
        "primary-key",
        "PRIMARY KEY",
        "The column (or columns) that identify each row uniquely. In SQLite a column declared INTEGER PRIMARY KEY is filled in automatically with the next number when you leave it out.",
        see=("unique", "rowid", "autoincrement", "foreign-key", "constraint"),
        priority=55,
        aka=("primary key", "pk", "key", "unique id", "id column", "identifier column", "surrogate key", "composite key", "natural key"),
        detect=(r"(?i)\bprimary\s+key\b",),
        rules=(
            r"No two rows may have the same key: inserting a duplicate fails with 'UNIQUE constraint failed'.",
            r"INTEGER PRIMARY KEY is an alias of the hidden rowid, so it is automatic and cannot be NULL.",
            r"A key spanning two columns is written PRIMARY KEY (a, b).",
            r"Quirk: a non-integer PRIMARY KEY in SQLite still allows NULL unless you add NOT NULL.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT);
            INSERT INTO t (v) VALUES ('a'), ('b');
            SELECT id FROM t ORDER BY id;
        """,
        out=r"1; 2",
    ),
    *sql(
        "unique",
        "UNIQUE",
        "UNIQUE on a column means no two rows may hold the same value there. NULLs do not count as equal, so a UNIQUE column may hold several NULLs.",
        see=("primary-key", "constraint", "or-replace", "index"),
        priority=50,
        aka=("unique constraint", "unique column", "no duplicates allowed", "unique index", "must be different", "uniqueness"),
        detect=(r"(?i)\bunique\b",),
        rules=(
            r"Inserting a duplicate fails: 'UNIQUE constraint failed: t.email'.",
            r"Two NULLs are allowed in a UNIQUE column (they are 'not equal').",
            r"A table has one primary key but may have many UNIQUE columns.",
        ),
        example=r"""
            CREATE TABLE t (email TEXT UNIQUE);
            INSERT INTO t VALUES ('a'), (NULL), (NULL);
            SELECT COUNT(*) FROM t;
        """,
        out=r"3",
    ),
    *sql(
        "not-null",
        "NOT NULL",
        "NOT NULL on a column forbids missing values: an INSERT or UPDATE that would leave it NULL fails.",
        see=("null", "default-value", "constraint", "primary-key"),
        priority=50,
        aka=("not null constraint", "required column", "mandatory", "no nulls", "non-null", "required", "nullable"),
        detect=(r"(?i)\bnot\s+null\b",),
        rules=(
            r"The error reads 'NOT NULL constraint failed: t.name'.",
            r"Leaving the column out of an INSERT counts as NULL unless it has a DEFAULT.",
            r"NOT NULL DEFAULT 0 is the usual pair for flags and counters.",
        ),
        example=r"""
            CREATE TABLE t (name TEXT NOT NULL DEFAULT 'none');
            INSERT INTO t DEFAULT VALUES;
            SELECT name FROM t;
        """,
        out=r"none",
    ),
    *sql(
        "check-constraint",
        "CHECK",
        "CHECK (condition) on a column or table rejects any row where the condition is FALSE. A row whose condition is NULL (unknown) passes.",
        see=("constraint", "null", "boolean", "type-affinity"),
        priority=50,
        aka=("check", "check constraint", "validation rule", "valid range", "allowed values", "value check"),
        detect=(r"(?i)\bcheck\s*\(",),
        rules=(
            r"CHECK (age >= 0) refuses -1 but accepts NULL, because NULL >= 0 is unknown, not false. Add NOT NULL to refuse missing values too.",
            r"The error reads 'CHECK constraint failed'.",
            r"It can look at other columns of the same row: CHECK (end_date >= start_date).",
        ),
        example=r"""
            CREATE TABLE t (age INTEGER CHECK (age >= 0));
            INSERT INTO t VALUES (5), (NULL);
            SELECT COUNT(*) FROM t;
        """,
        out=r"2",
    ),
    *sql(
        "default-value",
        "DEFAULT",
        "DEFAULT value on a column is what a new row gets when the INSERT does not mention that column.",
        see=("not-null", "insert", "create-table", "null"),
        priority=45,
        aka=("default", "default column value", "defaults", "initial value", "current_timestamp", "default null"),
        detect=(r"(?i)\bdefault\s+(?:[-\w'(]|current_)",),
        rules=(
            r"DEFAULT is used only when the column is left out; inserting NULL on purpose stores NULL.",
            r"The default can be a constant ('new', 0) or CURRENT_TIMESTAMP, which is the time of the insert.",
            r"Without a DEFAULT the missing value is NULL.",
        ),
        example=r"""
            CREATE TABLE t (a INTEGER, b INTEGER DEFAULT 7);
            INSERT INTO t (a) VALUES (1);
            INSERT INTO t (a, b) VALUES (2, NULL);
            SELECT a, b FROM t ORDER BY a;
        """,
        out=r"1|7; 2|NULL",
    ),
    *sql(
        "foreign-key",
        "FOREIGN KEY",
        "A column that must hold a key that exists in another table: orders.user_id REFERENCES users(id). It stops rows pointing at something that is not there. In SQLite it is only enforced after PRAGMA foreign_keys = ON.",
        see=("primary-key", "join", "constraint", "delete"),
        priority=50,
        aka=("references", "foreign key constraint", "referential integrity", "fk", "pragma foreign_keys", "on delete cascade", "cascade", "relationship", "one to many"),
        detect=(r"(?i)\bforeign\s+key\b|\breferences\s+\w+",),
        rules=(
            r"SQLite ignores foreign keys by default: you must run PRAGMA foreign_keys = ON on each connection.",
            r"When enforced, inserting an order for a missing user fails with 'FOREIGN KEY constraint failed'.",
            r"ON DELETE CASCADE deletes the child rows when the parent is deleted.",
            r"The referenced column should be a PRIMARY KEY or UNIQUE.",
        ),
        example=r"""
            PRAGMA foreign_keys = ON;
            CREATE TABLE u (id INTEGER PRIMARY KEY);
            CREATE TABLE o (uid INTEGER REFERENCES u(id));
            INSERT INTO u VALUES (1);
            INSERT INTO o VALUES (1);
            SELECT COUNT(*) FROM o;
        """,
        out=r"1",
    ),
    *sql(
        "alter-table",
        "ALTER TABLE",
        "ALTER TABLE changes a table that already exists: ADD COLUMN, RENAME TO, RENAME COLUMN, DROP COLUMN. Existing rows get the new column's DEFAULT, or NULL.",
        see=("create-table", "default-value", "not-null", "view"),
        priority=50,
        aka=("add column", "drop column", "rename column", "rename table", "rename", "change table", "modify table", "alter", "add a column"),
        detect=(r"(?i)\balter\s+table\b",),
        rules=(
            r"ALTER TABLE t ADD COLUMN c INTEGER DEFAULT 0; fills every old row with 0.",
            r"A NOT NULL column can only be added if it has a non-NULL DEFAULT.",
            r"SQLite cannot change a column's type or constraints in place: make a new table, copy, drop, rename.",
        ),
        example=r"""
            CREATE TABLE t (a INTEGER);
            INSERT INTO t VALUES (1), (2);
            ALTER TABLE t ADD COLUMN b INTEGER DEFAULT 5;
            SELECT a, b FROM t ORDER BY a;
        """,
        out=r"1|5; 2|5",
    ),
    *sql(
        "view",
        "VIEW",
        "A view is a saved SELECT with a name. You query it like a table, but it stores no data of its own and always shows the current rows.",
        see=("select", "cte", "create-table", "subquery"),
        priority=50,
        aka=("views", "create view", "saved query", "virtual table", "stored query", "named query", "live view", "live-view"),
        detect=(r"(?i)\bcreate\s+(?:temp(?:orary)?\s+)?view\b",),
        rules=(
            r"CREATE VIEW v AS SELECT ...; then SELECT * FROM v;",
            r"If the underlying table changes, the view's answer changes at once.",
            r"In SQLite a view is read-only (unless you add INSTEAD OF triggers); DROP VIEW removes it.",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER);
            CREATE VIEW big AS SELECT n FROM t WHERE n > 5;
            INSERT INTO t VALUES (3), (8), (10);
            SELECT COUNT(*) FROM big;
        """,
        out=r"2",
    ),
    *sql(
        "transaction",
        "Transaction",
        "A group of statements that succeed or fail together. BEGIN starts one, COMMIT makes all its changes permanent, ROLLBACK throws them all away.",
        see=("rollback", "savepoint", "update", "constraint"),
        priority=50,
        aka=("transactions", "begin", "commit", "atomic", "atomicity", "acid", "begin transaction", "all or nothing", "end transaction"),
        detect=(r"(?i)\b(?:begin(?:\s+transaction)?|commit)\s*;",),
        rules=(
            r"Without BEGIN, each statement is its own transaction, committed at once.",
            r"Moving money is the classic case: take from A and add to B must both happen or neither.",
            r"If the program stops mid-transaction, the changes are not kept.",
            r"In SQLite even CREATE TABLE and ALTER TABLE take part in a transaction.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            BEGIN;
            INSERT INTO t VALUES (1);
            COMMIT;
            BEGIN;
            INSERT INTO t VALUES (2);
            ROLLBACK;
            SELECT COUNT(*) FROM t;
        """,
        out=r"1",
    ),
    *sql(
        "rollback",
        "ROLLBACK",
        "ROLLBACK undoes every change made since BEGIN and ends the transaction, as if none of those statements had run.",
        see=("transaction", "savepoint", "delete", "update"),
        priority=50,
        aka=("undo", "roll back", "revert", "cancel changes", "abort", "undo changes"),
        detect=(r"(?i)\brollback\b",),
        rules=(
            r"Only changes after BEGIN are undone; anything committed earlier stays.",
            r"A failed statement (constraint error) is undone by itself; the rest of an open transaction continues unless you roll back.",
            r"Once committed, ROLLBACK can no longer help.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1);
            COMMIT;
            BEGIN;
            DELETE FROM t;
            ROLLBACK;
            SELECT COUNT(*) FROM t;
        """,
        out=r"1",
    ),
    *sql(
        "savepoint",
        "SAVEPOINT",
        "A named bookmark inside a transaction. ROLLBACK TO name undoes only the work after the bookmark; RELEASE name forgets the bookmark and keeps the work.",
        see=("transaction", "rollback"),
        priority=50,
        aka=("save point", "rollback to", "release", "nested transaction", "partial rollback", "release savepoint"),
        detect=(r"(?i)\bsavepoint\b",),
        rules=(
            r"SAVEPOINT s; ... ROLLBACK TO s; undoes back to s but the transaction stays open.",
            r"The earlier work is still pending until COMMIT.",
            r"Savepoints nest, giving finer control than one all-or-nothing ROLLBACK.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            BEGIN;
            INSERT INTO t VALUES (1);
            SAVEPOINT s;
            INSERT INTO t VALUES (2);
            ROLLBACK TO s;
            COMMIT;
            SELECT COUNT(*) FROM t;
        """,
        out=r"1",
    ),
    *sql(
        "trigger",
        "Trigger",
        "A trigger runs some SQL by itself when a row is inserted, updated or deleted. Inside it NEW holds the incoming row and OLD the previous one.",
        see=("insert", "update", "delete", "view"),
        priority=50,
        aka=("triggers", "create trigger", "after insert", "before update", "event", "new and old", "automatic action"),
        detect=(r"(?i)\bcreate\s+trigger\b",),
        rules=(
            r"CREATE TRIGGER name AFTER INSERT ON t BEGIN ... END; (also BEFORE, UPDATE, DELETE, and INSTEAD OF on views).",
            r"NEW.col is available for INSERT and UPDATE, OLD.col for UPDATE and DELETE.",
            r"Triggers fire for every affected row, even when the change comes from another program: use them sparingly, as they are easy to forget.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            CREATE TABLE log (n INTEGER);
            CREATE TRIGGER t_ins AFTER INSERT ON t BEGIN INSERT INTO log VALUES (NEW.v * 2); END;
            INSERT INTO t VALUES (5), (7);
            SELECT n FROM log ORDER BY n;
        """,
        out=r"10; 14",
    ),
    *sql(
        "index",
        "Index",
        "A sorted lookup structure on one or more columns that lets the database find rows quickly instead of reading the whole table. It speeds up WHERE, JOIN and ORDER BY and never changes an answer.",
        see=("unique", "primary-key", "where-clause", "order-by"),
        priority=50,
        aka=("indexes", "indices", "create index", "indexing", "performance", "query plan", "explain", "fast lookup", "speed up queries"),
        detect=(r"(?i)\bcreate\s+(?:unique\s+)?index\b",),
        rules=(
            r"CREATE INDEX i ON t (col); then queries filtering on col can use it. A UNIQUE index also enforces no duplicates.",
            r"It costs space and slows INSERT, UPDATE and DELETE a little, so index the columns you search by, not all of them.",
            r"EXPLAIN QUERY PLAN SELECT ... shows whether an index is used.",
            r"LIKE '%x' (a leading wildcard) cannot use an ordinary index.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (2), (2), (3);
            CREATE INDEX i ON t (v);
            SELECT COUNT(*) FROM t WHERE v = 2;
        """,
        out=r"2",
    ),
    *sql(
        "rowid",
        "rowid",
        "Every ordinary SQLite table has a hidden integer column called rowid that numbers its rows 1, 2, 3... A column declared INTEGER PRIMARY KEY is that same number under another name.",
        see=("primary-key", "autoincrement", "table"),
        priority=45,
        aka=("row id", "_rowid_", "oid", "hidden column", "row number", "last_insert_rowid", "last insert id"),
        detect=(r"(?i)\browid\b",),
        rules=(
            r"SELECT rowid, * FROM t shows it; it is not included by SELECT *.",
            r"last_insert_rowid() is the rowid of the most recent INSERT.",
            r"VACUUM may renumber rows of a table that has no INTEGER PRIMARY KEY, so do not use a bare rowid as a permanent id.",
        ),
        example=r"""
            CREATE TABLE t (name TEXT);
            INSERT INTO t VALUES ('a'), ('b');
            SELECT rowid, name FROM t;
        """,
        out=r"1|a; 2|b",
    ),
    *sql(
        "autoincrement",
        "AUTOINCREMENT",
        "INTEGER PRIMARY KEY AUTOINCREMENT promises that a new row never gets an id that was used before, even after the biggest row is deleted. Plain INTEGER PRIMARY KEY may reuse it.",
        see=("primary-key", "rowid", "delete"),
        priority=45,
        aka=("auto increment", "auto_increment", "serial", "identity column", "next id", "generated id", "sequence"),
        detect=(r"(?i)\bautoincrement\b",),
        rules=(
            r"Without AUTOINCREMENT the next id is max(id) + 1, so deleting the last row lets its id come back.",
            r"With AUTOINCREMENT SQLite remembers the highest id ever used (in sqlite_sequence).",
            r"Ids are not guaranteed gap-free either way.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, v TEXT);
            INSERT INTO t (v) VALUES ('a'), ('b');
            DELETE FROM t WHERE id = 2;
            INSERT INTO t (v) VALUES ('c');
            SELECT id FROM t ORDER BY id;
        """,
        out=r"1; 3",
    ),
]
