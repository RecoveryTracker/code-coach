"""Plain-English walkthrough of SQL (SQLite's), one statement and one clause at a time.

SQL is read differently from Dart and C: a statement is a few clauses (`SELECT ... FROM ... WHERE ...`), each worth
a sentence, and a clause can sit on several lines. So this splits the script into statements, a statement into its
clauses, and a small precedence parser reads the expressions inside them. A row is written on the line where its
clause (or its list item) starts. Anything the reader does not know becomes an honest fallback row.

Every sentence that states a checkable fact lives in `FACTS`; a claim written ```SELECT ...` gives `ROWS``` is run
in the real SQLite by tests/test_explain_sql.py, so a rule here cannot say something SQLite does not do.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from . import explain_common as C
from .explain_programs import sql_program

FACTS: dict[str, str] = {
    "intdiv": "Dividing two integers gives an integer: `SELECT 7 / 2` gives `3`. Make one side a decimal to keep the fraction: `SELECT 7 / 2.0` gives `3.5`.",
    "div0": "Dividing by zero is not an error in SQLite, it gives NULL: `SELECT 1 / 0` gives `NULL`.",
    "nulleq": "Comparing with NULL gives NULL (unknown), never true: `SELECT NULL = NULL` gives `NULL`. Use IS NULL instead: `SELECT NULL IS NULL` gives `1`.",
    "notin": "`NOT IN` against a list or subquery that contains a NULL matches nothing: `SELECT 5 NOT IN (1, NULL)` gives `NULL`.",
    "count": "`COUNT(*)` counts rows, but `COUNT(col)` skips the NULLs: `SELECT COUNT(*), COUNT(a) FROM (SELECT NULL AS a UNION ALL SELECT 1)` gives `2|1`.",
    "nullsfirst": "SQLite sorts NULL before every other value when ascending: `SELECT a FROM (SELECT 1 AS a UNION ALL SELECT NULL) ORDER BY a LIMIT 1` gives `NULL`.",
    "wherehaving": "WHERE filters rows before they are grouped; HAVING filters the groups afterwards, so only HAVING can test an aggregate such as COUNT(*).",
    "leftwhere": "A WHERE test on the right-hand table of a LEFT JOIN throws away the rows that found no match (their column is NULL), which quietly turns it into an inner join. Put the test in the ON clause to keep them.",
    "like": "LIKE ignores upper and lower case for plain letters: `SELECT 'A' LIKE 'a'` gives `1`.",
    "concatnull": "`||` glues text together, and NULL poisons it: `SELECT 'a' || NULL` gives `NULL`.",
    "substr": "SUBSTR counts from 1, not 0: `SELECT SUBSTR('hello', 1, 2)` gives `he`.",
    "avg": "AVG gives a decimal even for whole numbers: `SELECT AVG(v) FROM (SELECT 1 AS v UNION ALL SELECT 2)` gives `1.5`.",
    "round": "ROUND gives a decimal number: `SELECT ROUND(2.5)` gives `3.0`.",
    "between": "BETWEEN includes both ends: `SELECT 5 BETWEEN 5 AND 6` gives `1`.",
    "bool": "SQLite has no separate true and false: a comparison gives 1 or 0, as in `SELECT 2 > 1` gives `1`.",
    "union": "UNION drops duplicate rows, UNION ALL keeps them: `SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 1)` gives `1`, and `SELECT COUNT(*) FROM (SELECT 1 UNION ALL SELECT 1)` gives `2`.",
    "nowhere": "With no WHERE, an UPDATE or DELETE touches every row of the table.",
    "ignore": "OR IGNORE skips a row that would break a PRIMARY KEY or UNIQUE rule instead of stopping with an error.",
    "rownum": "ROW_NUMBER gives every row its own number, even when values tie, but RANK gives tied rows the same number and then skips ahead.",
    "distinct": "DISTINCT keeps one copy of each different row: `SELECT COUNT(*) FROM (SELECT DISTINCT 1 UNION ALL SELECT 1)` gives `2`, but `SELECT COUNT(*) FROM (SELECT DISTINCT a FROM (SELECT 1 AS a UNION ALL SELECT 1))` gives `1`.",
    "coalesce": "COALESCE gives its first argument that is not NULL: `SELECT COALESCE(NULL, 5)` gives `5`.",
    "limit": "LIMIT counts rows after sorting, so it is only predictable together with ORDER BY.",
    "typeof": "SQLite keeps the type of each value, not of the column: `SELECT TYPEOF(1), TYPEOF(1.0), TYPEOF('1')` gives `integer|real|text`.",
}


# ── Tokens ──────────────────────────────────────────────────

@dataclass
class T:
    kind: str  # word num str qid punct op
    text: str
    line: int
    start: int
    end: int

    @property
    def up(self) -> str:
        return self.text.upper() if self.kind == "word" else self.text


_OPS = ["<>", "!=", "<=", ">=", "==", "||", "<<", ">>", "->>", "->"]


def tokenize(src: str) -> list[T]:
    toks: list[T] = []
    i, n, line = 0, len(src), 1
    while i < n:
        c = src[i]
        if c == "\n":
            line += 1
            i += 1
        elif c.isspace():
            i += 1
        elif src.startswith("--", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            line += src.count("\n", i, j)
            i = j
        elif c == "'":
            j = i + 1
            while j < n:
                if src[j] == "'":
                    if src[j + 1 : j + 2] == "'":
                        j += 2
                        continue
                    break
                j += 1
            j = min(j + 1, n)
            toks.append(T("str", src[i:j], line, i, j))
            line += src.count("\n", i, j)
            i = j
        elif c in '"`' or c == "[":
            close = "]" if c == "[" else c
            j = src.find(close, i + 1)
            j = n if j < 0 else j + 1
            toks.append(T("qid", src[i:j], line, i, j))
            i = j
        elif c.isdigit() or (c == "." and src[i + 1 : i + 2].isdigit()):
            m = re.compile(r"0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?").match(src, i)
            j = m.end() if m else i + 1
            toks.append(T("num", src[i:j], line, i, j))
            i = j
        elif c.isalpha() or c == "_":
            j = i + 1
            while j < n and (src[j].isalnum() or src[j] in "_$"):
                j += 1
            if src[i] in "xX" and src[j : j + 1] == "'":  # a blob literal x'ff'
                k = src.find("'", j + 1)
                j = n if k < 0 else k + 1
                toks.append(T("str", src[i:j], line, i, j))
            else:
                toks.append(T("word", src[i:j], line, i, j))
            i = j
        else:
            for op in _OPS:
                if src.startswith(op, i):
                    toks.append(T("op", op, line, i, i + len(op)))
                    i += len(op)
                    break
            else:
                kind = "punct" if c in "(),;." else "op"
                toks.append(T(kind, c, line, i, i + 1))
                i += 1
    return toks


def split_statements(toks: list[T]) -> list[list[T]]:
    out: list[list[T]] = []
    cur: list[T] = []
    depth = 0
    in_trigger = False
    i = 0
    while i < len(toks):
        t = toks[i]
        cur.append(t)
        if t.kind == "punct" and t.text == "(":
            depth += 1
        elif t.kind == "punct" and t.text == ")":
            depth -= 1
        elif t.kind == "word" and t.up == "TRIGGER" and len(cur) <= 4 and cur[0].up == "CREATE":
            in_trigger = True
        elif in_trigger and t.up == "END":
            in_trigger = False
        elif t.kind == "punct" and t.text == ";" and depth <= 0 and not in_trigger:
            out.append(cur[:-1])
            cur = []
            depth = 0
        i += 1
    if cur:
        out.append(cur)
    return [s for s in out if s]


# ── Expressions ─────────────────────────────────────────────

@dataclass
class E:
    kind: str
    a: list
    text: str = ""


class ReadError(Exception):
    pass


_BP = {"OR": 1, "AND": 2, "=": 4, "==": 4, "!=": 4, "<>": 4, "IS": 4, "IN": 4, "LIKE": 4, "GLOB": 4, "BETWEEN": 4, "NOT": 4, "ISNULL": 4, "NOTNULL": 4, "MATCH": 4, "REGEXP": 4,
       "<": 5, ">": 5, "<=": 5, ">=": 5, "&": 6, "|": 6, "<<": 6, ">>": 6, "+": 7, "-": 7, "*": 8, "/": 8, "%": 8, "||": 9, "->": 9, "->>": 9}


class P:
    def __init__(self, toks: list[T], src: str):
        self.t = toks
        self.i = 0
        self.src = src

    def peek(self, k: int = 0) -> T | None:
        return self.t[self.i + k] if self.i + k < len(self.t) else None

    def up(self, k: int = 0) -> str:
        t = self.peek(k)
        return t.up if t is not None and t.kind in ("word", "punct", "op") else ""

    def next(self) -> T:
        t = self.peek()
        if t is None:
            raise ReadError("end")
        self.i += 1
        return t

    def eat(self, w: str) -> bool:
        if self.up() == w:
            self.i += 1
            return True
        return False

    def expect(self, w: str) -> None:
        if not self.eat(w):
            raise ReadError(w)

    def text_from(self, a: int) -> str:
        if self.i <= a:
            return ""
        return self.src[self.t[a].start : self.t[self.i - 1].end]

    def expr(self, min_bp: int = 0) -> E:
        first = self.i
        left = self.prefix()
        while True:
            u = self.up()
            nt = self.peek()
            if nt is None:
                break
            if nt.kind == "punct" and nt.text in (",", ")", ";"):
                break
            if u == "COLLATE":
                self.i += 1
                self.next()
                left = E("collate", [left], self.text_from(first))
                continue
            neg = False
            op = u
            if u == "NOT" and self.up(1) in ("IN", "LIKE", "GLOB", "BETWEEN", "MATCH", "REGEXP"):
                neg = True
                op = self.up(1)
            if op in ("ISNULL", "NOTNULL"):
                if 4 < min_bp:
                    break
                self.i += 1
                left = E("isnull", [left, op == "NOTNULL"], self.text_from(first))
                continue
            bp = _BP.get(op)
            if bp is None or (nt.kind not in ("word", "op") and nt.text not in ("<", ">")):
                break
            if nt.kind == "word" and op not in ("AND", "OR", "IS", "IN", "LIKE", "GLOB", "BETWEEN", "NOT", "MATCH", "REGEXP"):
                break
            if bp < min_bp:
                break
            self.i += 1
            if neg:
                self.i += 1
            if op == "IS":
                neg_is = self.eat("NOT")
                if self.up() == "DISTINCT":
                    self.i += 1
                    self.expect("FROM")
                    right = self.expr(5)
                    left = E("isdistinct", [left, right, neg_is], self.text_from(first))
                    continue
                if self.up() == "NULL":
                    self.i += 1
                    left = E("isnull", [left, neg_is], self.text_from(first))
                    continue
                right = self.expr(5)
                left = E("is", [left, right, neg_is], self.text_from(first))
            elif op == "IN":
                self.expect("(")
                if self.up() in ("SELECT", "WITH", "VALUES"):
                    sub = self.sub_tokens()
                    left = E("in_sub", [left, sub, neg], self.text_from(first))
                else:
                    items = []
                    while self.up() != ")":
                        items.append(self.expr(1))
                        if not self.eat(","):
                            break
                    self.expect(")")
                    left = E("in_list", [left, items, neg], self.text_from(first))
            elif op == "BETWEEN":
                lo = self.expr(5)
                self.expect("AND")
                hi = self.expr(5)
                left = E("between", [left, lo, hi, neg], self.text_from(first))
            elif op in ("LIKE", "GLOB", "MATCH", "REGEXP"):
                pat = self.expr(5)
                if self.eat("ESCAPE"):
                    self.expr(9)
                left = E("like", [left, pat, neg, op], self.text_from(first))
            else:
                right = self.expr(bp + 1)
                left = E("bin", [t_text(nt), left, right], self.text_from(first))
        return left

    def sub_tokens(self) -> list[T]:
        """At the first token inside a `(`: take everything up to the matching `)` and consume it."""
        depth, start = 1, self.i
        while self.i < len(self.t):
            t = self.t[self.i]
            if t.kind == "punct" and t.text == "(":
                depth += 1
            elif t.kind == "punct" and t.text == ")":
                depth -= 1
                if depth == 0:
                    toks = self.t[start : self.i]
                    self.i += 1
                    return toks
            self.i += 1
        raise ReadError("paren")

    def prefix(self) -> E:
        t = self.next()
        first = self.i - 1
        if t.kind == "num":
            return E("num", [t.text], t.text)
        if t.kind == "str":
            return E("str", [t.text], t.text)
        if t.kind == "op" and t.text in ("-", "+", "~"):
            return E("un", [t.text, self.expr(10)], self.text_from(first))
        if t.kind == "op" and t.text == "*":
            return E("star", [], "*")
        if t.kind == "punct" and t.text == "(":
            if self.up() in ("SELECT", "WITH", "VALUES"):
                return E("sub", [self.sub_tokens()], self.text_from(first))
            items = [self.expr(0)]
            while self.eat(","):
                items.append(self.expr(0))
            self.expect(")")
            return E("paren", [items[0]], self.text_from(first)) if len(items) == 1 else E("row", [items], self.text_from(first))
        if t.kind == "qid":
            return self.after_name(t, first)
        if t.kind != "word":
            raise ReadError("unexpected")
        u = t.up
        if u == "NULL":
            return E("null", [], "NULL")
        if u in ("TRUE", "FALSE"):
            return E("bool", [u], u)
        if u in ("CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP"):
            return E("current", [u], u)
        if u == "NOT":
            if self.up() == "EXISTS":
                self.i += 1
                self.expect("(")
                return E("exists", [self.sub_tokens(), True], self.text_from(first))
            return E("not", [self.expr(3)], self.text_from(first))
        if u == "EXISTS" and self.up() == "(":
            self.i += 1
            return E("exists", [self.sub_tokens(), False], self.text_from(first))
        if u == "CASE":
            return self.case(first)
        if u == "CAST" and self.up() == "(":
            self.i += 1
            x = self.expr(0)
            self.expect("AS")
            ty = []
            while self.up() != ")":
                ty.append(self.next().text)
            self.expect(")")
            return E("cast", [x, " ".join(ty)], self.text_from(first))
        return self.after_name(t, first)

    def after_name(self, t: T, first: int) -> E:
        name = t.text
        while self.up() == "." and self.peek(1) is not None:
            self.i += 1
            nxt = self.next()
            name += "." + nxt.text
        if self.up() == "(" and t.kind == "word":
            self.i += 1
            distinct = self.eat("DISTINCT")
            args: list[E] = []
            star = False
            while self.up() != ")":
                if self.up() == "*":
                    self.i += 1
                    star = True
                else:
                    args.append(self.expr(0))
                    if self.up() == "ORDER":  # aggregate ORDER BY
                        while self.up() != ")":
                            self.i += 1
                if not self.eat(","):
                    break
            self.expect(")")
            node = E("call", [name, args, distinct, star], self.text_from(first))
            if self.up() == "FILTER":
                self.i += 1
                self.expect("(")
                self.expect("WHERE")
                node.a.append(self.expr(0))
                self.expect(")")
            else:
                node.a.append(None)
            if self.up() == "OVER":
                self.i += 1
                if self.up() == "(":
                    self.i += 1
                    spec = self.sub_tokens()
                    node = E("over", [node, spec], self.text_from(first))
                else:
                    node = E("over", [node, [self.next()]], self.text_from(first))
            return node
        if name.endswith(".*"):
            return E("star", [name], name)
        return E("id", [name], name)

    def case(self, first: int) -> E:
        operand = None
        if self.up() != "WHEN":
            operand = self.expr(0)
        whens = []
        while self.eat("WHEN"):
            c = self.expr(0)
            self.expect("THEN")
            whens.append((c, self.expr(0)))
        other = self.expr(0) if self.eat("ELSE") else None
        self.expect("END")
        return E("case", [operand, whens, other], self.text_from(first))


def t_text(t: T) -> str:
    return t.up


def parse_expr(toks: list[T], src: str) -> E | None:
    try:
        p = P(toks, src)
        if not toks:
            return None
        e = p.expr(0)
        return e if p.i >= len(toks) else None
    except (ReadError, IndexError, RecursionError):
        return None


def walk(e):
    if isinstance(e, E):
        yield e
        for x in e.a:
            yield from walk(x)
    elif isinstance(e, (list, tuple)):
        for x in e:
            yield from walk(x)


_AGG = {
    "SUM": "the total of {a} (NULLs are ignored; NULL if there is nothing to add)", "AVG": "the average of {a} (NULLs are ignored)", "MIN": "the smallest {a}", "MAX": "the largest {a}",
    "TOTAL": "the total of {a} as a decimal (0.0 if there is nothing to add)", "GROUP_CONCAT": "all the {a} values glued into one text",
}
_SCALAR = {
    "ROUND": "{a} rounded", "ABS": "the size of {a}, ignoring the sign", "LENGTH": "the length of {a}", "UPPER": "{a} in capitals", "LOWER": "{a} in small letters", "TRIM": "{a} with spaces cut off both ends",
    "LTRIM": "{a} with spaces cut off the left", "RTRIM": "{a} with spaces cut off the right", "SUBSTR": "part of {a}, counting positions from 1", "SUBSTRING": "part of {a}, counting positions from 1",
    "INSTR": "the position of the second value inside {a} (0 if it is not there)", "REPLACE": "{a} with every match swapped", "COALESCE": "the first of {a} that is not NULL", "IFNULL": "{a0}, or {a1} if that is NULL",
    "NULLIF": "NULL if {a0} equals {a1}, otherwise {a0}", "IIF": "{a1} if {a0} is true, otherwise {a2}", "TYPEOF": "the type name of {a}", "RANDOM": "a random number", "DATE": "the date {a}",
    "STRFTIME": "{a} written as a formatted date or time", "DATETIME": "the date and time {a}", "TIME": "the time {a}", "JULIANDAY": "{a} as a day number", "CHANGES": "how many rows the last statement changed",
    "LAST_INSERT_ROWID": "the row id of the last insert", "MAX": "the larger of {a}", "MIN": "the smaller of {a}", "HEX": "{a} in hexadecimal", "QUOTE": "{a} written as a SQL literal", "PRINTF": "text formatted by {a0}",
    "FORMAT": "text formatted by {a0}", "CHAR": "the character(s) with code {a}", "UNICODE": "the code of the first character of {a}", "LIKE": "whether {a1} matches {a0}", "ZEROBLOB": "{a} zero bytes",
    "SIGN": "the sign of {a}", "CEIL": "{a} rounded up", "FLOOR": "{a} rounded down", "POWER": "{a0} to the power {a1}", "SQRT": "the square root of {a}", "JSON_EXTRACT": "a value pulled out of the JSON {a0}",
}
_WINDOW = {
    "ROW_NUMBER": "the row's position number (1, 2, 3, ...)", "RANK": "the rank (tied rows share a rank, and the next rank skips ahead)", "DENSE_RANK": "the rank with no gaps after ties",
    "NTILE": "which of {a} equal buckets the row falls into", "LAG": "the {a0} of the previous row", "LEAD": "the {a0} of the next row", "FIRST_VALUE": "the {a0} of the first row of the window",
    "LAST_VALUE": "the {a0} of the last row of the frame", "NTH_VALUE": "the {a0} of row number {a1}", "PERCENT_RANK": "the row's rank as a fraction", "CUME_DIST": "the share of rows up to this one",
}
_BIN = {"+": "plus", "-": "minus", "*": "times", "/": "divided by", "%": "remainder after dividing by", "||": "joined (as text) to", "=": "equals", "==": "equals", "!=": "is not equal to", "<>": "is not equal to",
        "<": "is less than", ">": "is greater than", "<=": "is at most", ">=": "is at least", "AND": "and", "OR": "or", "&": "bitwise AND", "|": "bitwise OR", "<<": "shifted left by", ">>": "shifted right by"}


def code(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text if len(text) <= 70 else text[:67] + "..."


class Reader:
    """One script: collects rows and the notes about what it used."""

    def __init__(self, src: str):
        self.src = src
        self.rows: list[dict] = []
        self.seen: set[str] = set()
        self.bad_lines: set[int] = set()
        self.lines = src.split("\n")
        self.has_select_clauses = 0
        self.right_names: set[str] = set()
        self.order_steps: list[str] = []

    # -- rows
    def row(self, line: int, depth: int, text: str) -> None:
        raw = self.lines[line - 1].strip() if 0 < line <= len(self.lines) else ""
        self.rows.append({"line": line, "depth": depth, "source": raw, "text": C.sentence([text]).replace("..", ".").replace(".`.", ".`")})

    def fact(self, key: str) -> str:
        if key in self.seen:
            return ""
        self.seen.add(key)
        return FACTS[key]

    # -- expression words
    def say(self, e: E | None, level: int = 0, src: str = "") -> str:
        if e is None:
            return code(src)
        k = e.kind
        if k in ("num", "id"):
            return e.a[0]
        if k == "str":
            return e.a[0]
        if k == "null":
            return "NULL"
        if k == "bool":
            return e.a[0].lower()
        if k == "current":
            return {"CURRENT_DATE": "today's date", "CURRENT_TIME": "the current time", "CURRENT_TIMESTAMP": "the current date and time"}[e.a[0]]
        if k == "star":
            return "every column" if not e.a else f"every column of {e.a[0][:-2]}"
        if k == "paren":
            return self.say(e.a[0], level, src)
        if k == "row":
            return "(" + ", ".join(self.say(x, level + 1) for x in e.a[0]) + ")"
        if level >= 3 and k in ("bin", "case", "call"):
            return code(e.text)
        if k == "un":
            return f"minus {self.say(e.a[1], level + 1)}" if e.a[0] == "-" else self.say(e.a[1], level + 1)
        if k == "not":
            return f"not ({self.say(e.a[0], level + 1)})"
        if k == "bin":
            return f"{self.say(e.a[1], level + 1)} {_BIN.get(e.a[0], e.a[0])} {self.say(e.a[2], level + 1)}"
        if k == "isnull":
            return f"{self.say(e.a[0], level + 1)} is {'not ' if e.a[1] else ''}NULL"
        if k == "is":
            return f"{self.say(e.a[0], level + 1)} is {'not ' if e.a[2] else ''}{self.say(e.a[1], level + 1)}"
        if k == "isdistinct":
            return f"{self.say(e.a[0], level + 1)} is {'the same as' if e.a[2] else 'different from'} {self.say(e.a[1], level + 1)} (NULLs count as equal)"
        if k == "in_list":
            return f"{self.say(e.a[0], level + 1)} is {'not ' if e.a[2] else ''}one of ({', '.join(self.say(x, level + 1) for x in e.a[1])})"
        if k == "in_sub":
            return f"{self.say(e.a[0], level + 1)} is {'not ' if e.a[2] else ''}one of the values the subquery returns"
        if k == "between":
            return f"{self.say(e.a[0], level + 1)} is {'not ' if e.a[3] else ''}between {self.say(e.a[1], level + 1)} and {self.say(e.a[2], level + 1)} (both ends included)"
        if k == "like":
            word = {"LIKE": "matches the pattern", "GLOB": "matches the glob pattern", "MATCH": "matches", "REGEXP": "matches the regular expression"}[e.a[3]]
            return f"{self.say(e.a[0], level + 1)} does {'not ' if e.a[2] else ''}{word.replace('matches', 'match')} {self.say(e.a[1], level + 1)}"
        if k == "sub":
            return "the value from a subquery"
        if k == "exists":
            return f"{'no row' if e.a[1] else 'at least one row'} comes back from a subquery"
        if k == "collate":
            return f"{self.say(e.a[0], level + 1)} compared by a special collation"
        if k == "cast":
            return f"{self.say(e.a[0], level + 1)} converted to {e.a[1]}"
        if k == "case":
            operand, whens, other = e.a
            parts = [f"if {self.say(c, level + 1)} then {self.say(v, level + 1)}" if operand is None else f"if it is {self.say(c, level + 1)} then {self.say(v, level + 1)}" for c, v in whens]
            if operand is not None:
                parts = [f"if {self.say(operand, level + 1)} equals {self.say(c, level + 1)} then {self.say(v, level + 1)}" for c, v in whens]
            return "a CASE: " + ", ".join(parts) + (f", otherwise {self.say(other, level + 1)}" if other is not None else ", otherwise NULL")
        if k == "over":
            return self.over(e)
        if k == "call":
            return self.call(e, level)
        return code(e.text)

    def call(self, e: E, level: int) -> str:
        name, args, distinct, star, filt = e.a
        up = name.upper()
        argv = [self.say(a, level + 1) for a in args]
        a = ", ".join(argv)
        slots = {f"a{i}": (argv[i] if i < len(argv) else "it") for i in range(4)}
        slots["a"] = a
        extra = f", counting only rows where {self.say(filt, level + 1)}" if filt is not None else ""
        if up == "COUNT":
            if star:
                return "the number of rows (every row counts, NULLs or not)" + extra
            if distinct:
                return f"how many different non-NULL values {a} has" + extra
            return f"how many rows have a value (not NULL) in {a}" + extra
        if up in _AGG and (len(args) == 1 or up in ("GROUP_CONCAT",)) and up not in ("MIN", "MAX") or (up in ("MIN", "MAX") and len(args) == 1):
            return _AGG[up].format(**slots) + extra
        if up in _WINDOW:
            return _WINDOW[up].format(**slots)
        if up in _SCALAR:
            return _SCALAR[up].format(**slots)
        return f"{name}({a})" if not args else f"the result of {name} on {a}"

    def over(self, e: E) -> str:
        call, spec = e.a
        base = self.call(call, 1)
        text = " ".join(t.text for t in spec) if spec and isinstance(spec[0], T) else ""
        up = text.upper()
        bits = []
        if isinstance(spec, list) and spec and isinstance(spec[0], T) and len(spec) == 1 and spec[0].kind == "word":
            return f"{base}, computed over the window named {spec[0].text}"
        m = re.search(r"PARTITION\s+BY\s+(.*?)(?=\s+ORDER\s+BY|\s+ROWS|\s+RANGE|\s+GROUPS|$)", text, re.I)
        if m:
            bits.append(f"inside each group of rows with the same {code(m.group(1))} (PARTITION BY)")
        m = re.search(r"ORDER\s+BY\s+(.*?)(?=\s+ROWS|\s+RANGE|\s+GROUPS|$)", text, re.I)
        if m:
            bits.append(f"going in the order of {code(m.group(1))}")
        if re.search(r"\b(ROWS|RANGE|GROUPS)\b", up):
            bits.append(f"over the frame `{code(re.search(r'(ROWS|RANGE|GROUPS).*$', text, re.I).group(0))}`")
        if not bits:
            bits.append("over all the rows")
        return f"{base}, worked out for every row separately ({', '.join(bits)}) without collapsing rows into groups"

    # -- facts triggered by an expression
    def facts_for(self, es: list[E | None], extra_text: str = "") -> str:
        out: list[str] = []
        for root in es:
            for n in walk(root):
                if n.kind == "bin" and n.a[0] == "/":
                    out.append(self.fact("intdiv"))
                    out.append(self.fact("div0"))
                if n.kind == "bin" and n.a[0] in ("=", "==", "!=", "<>") and any(isinstance(x, E) and x.kind == "null" for x in n.a[1:]):
                    out.append(self.fact("nulleq"))
                if n.kind in ("in_list", "in_sub") and n.a[2]:
                    out.append(self.fact("notin"))
                if n.kind == "call":
                    nm = n.a[0].upper()
                    if nm == "COUNT":
                        out.append(self.fact("count"))
                    elif nm == "AVG":
                        out.append(self.fact("avg"))
                    elif nm == "ROUND":
                        out.append(self.fact("round"))
                    elif nm in ("SUBSTR", "SUBSTRING"):
                        out.append(self.fact("substr"))
                    elif nm == "COALESCE":
                        out.append(self.fact("coalesce"))
                    elif nm == "TYPEOF":
                        out.append(self.fact("typeof"))
                    elif nm in ("ROW_NUMBER", "RANK", "DENSE_RANK"):
                        out.append(self.fact("rownum"))
                if n.kind == "like" and n.a[3] == "LIKE":
                    out.append(self.fact("like"))
                if n.kind == "bin" and n.a[0] == "||":
                    out.append(self.fact("concatnull"))
                if n.kind == "between":
                    out.append(self.fact("between"))
        out = [x for x in out if x]
        return " ".join(out[:2])

    # -- statements
    def statement(self, toks: list[T], depth: int = 0) -> None:
        if not toks:
            return
        w = toks[0].up
        w2 = toks[1].up if len(toks) > 1 else ""
        first_line = toks[0].line
        try:
            if w in ("SELECT", "WITH", "VALUES") or (w == "(" and w2 == "SELECT"):
                self.select(toks, depth)
            elif w in ("INSERT", "REPLACE"):
                self.insert(toks, depth)
            elif w == "UPDATE":
                self.update(toks, depth)
            elif w == "DELETE":
                self.delete(toks, depth)
            elif w == "CREATE":
                self.create(toks, depth)
            elif w == "DROP":
                kind = w2
                rest = [t for t in toks[2:] if t.up not in ("IF", "EXISTS")]
                name = rest[0].text if rest else "it"
                self.row(first_line, depth, f"deletes the {kind.lower()} {name} for good" + (" (and its rows)" if kind == "TABLE" else "") + (" - IF EXISTS makes it harmless when it is already gone" if any(t.up == "IF" for t in toks) else "") + ".")
            elif w == "ALTER":
                self.alter(toks, depth)
            elif w == "BEGIN":
                self.row(first_line, depth, "starts a transaction: the changes that follow are held back until COMMIT, and ROLLBACK would undo them all.")
            elif w in ("COMMIT", "END"):
                self.row(first_line, depth, "commits the transaction: every change since BEGIN is made permanent together.")
            elif w == "ROLLBACK":
                if w2 == "TO" or (w2 == "TRANSACTION" and len(toks) > 3 and toks[2].up == "TO"):
                    name = toks[-1].text
                    self.row(first_line, depth, f"undoes everything since the savepoint {name} was made, but the transaction stays open.")
                else:
                    self.row(first_line, depth, "rolls the transaction back: every change since BEGIN is undone.")
            elif w == "SAVEPOINT":
                self.row(first_line, depth, f"marks a point named {toks[1].text if len(toks) > 1 else ''} inside the transaction that ROLLBACK TO can come back to.")
            elif w == "RELEASE":
                self.row(first_line, depth, f"forgets the savepoint {toks[-1].text}, keeping its changes.")
            elif w == "PRAGMA":
                self.row(first_line, depth, f"asks SQLite to read or change the setting `{code(' '.join(t.text for t in toks[1:]))}`.")
            elif w in ("VACUUM", "ANALYZE", "REINDEX"):
                self.row(first_line, depth, {"VACUUM": "rebuilds the database file to reclaim space.", "ANALYZE": "gathers statistics so queries can be planned better.", "REINDEX": "rebuilds indexes."}[w])
            elif w == "EXPLAIN":
                self.row(first_line, depth, "shows how SQLite plans to run the statement instead of running it.")
                self.statement(toks[2:] if w2 == "QUERY" else toks[1:], depth)
            elif w == "ATTACH":
                self.row(first_line, depth, "attaches another database file under a name.")
            else:
                raise ReadError("unknown statement")
        except (ReadError, IndexError, KeyError, RecursionError):
            self.bad_lines.update(range(first_line, toks[-1].line + 1))
            self.row(first_line, depth, C.FALLBACK)

    # -- SELECT
    _CLAUSES = ("WITH", "SELECT", "FROM", "WHERE", "GROUP", "HAVING", "WINDOW", "ORDER", "LIMIT", "OFFSET", "UNION", "INTERSECT", "EXCEPT", "VALUES")

    def segments(self, toks: list[T]) -> list[tuple[str, list[T]]]:
        segs: list[tuple[str, list[T]]] = []
        depth = 0
        cur_kw, cur = "", []
        case_depth = 0
        for i, t in enumerate(toks):
            if t.kind == "punct" and t.text == "(":
                depth += 1
            elif t.kind == "punct" and t.text == ")":
                depth -= 1
            elif t.up == "CASE":
                case_depth += 1
            elif t.up == "END" and case_depth:
                case_depth -= 1
            is_kw = depth == 0 and case_depth == 0 and t.kind == "word" and t.up in self._CLAUSES
            if is_kw and t.up == "ORDER" and i + 1 < len(toks) and toks[i + 1].up != "BY":
                is_kw = False
            if is_kw and t.up == "GROUP" and not (i + 1 < len(toks) and toks[i + 1].up == "BY"):
                is_kw = False
            if is_kw and t.up in ("WITH",) and i > 0:
                is_kw = False
            if is_kw and t.up == "VALUES" and cur_kw not in ("", "UNION", "INTERSECT", "EXCEPT"):
                is_kw = False
            if is_kw and t.up == "EXCEPT" and False:
                is_kw = False
            if is_kw:
                if cur_kw or cur:
                    segs.append((cur_kw, cur))
                cur_kw, cur = t.up, []
            else:
                cur.append(t)
        if cur_kw or cur:
            segs.append((cur_kw, cur))
        return segs

    def items(self, toks: list[T]) -> list[list[T]]:
        out, cur, depth, case_depth = [], [], 0, 0
        for t in toks:
            if t.kind == "punct" and t.text == "(":
                depth += 1
            elif t.kind == "punct" and t.text == ")":
                depth -= 1
            elif t.up == "CASE":
                case_depth += 1
            elif t.up == "END" and case_depth:
                case_depth -= 1
            if t.kind == "punct" and t.text == "," and depth == 0 and case_depth == 0:
                out.append(cur)
                cur = []
            else:
                cur.append(t)
        if cur:
            out.append(cur)
        return out

    def subqueries(self, e: E | None, depth: int, shown: set[int]) -> None:
        for n in walk(e):
            sub = None
            if n.kind in ("sub", "exists"):
                sub = n.a[0]
            elif n.kind == "in_sub":
                sub = n.a[1]
            if sub and id(sub) not in shown:
                shown.add(id(sub))
                self.select(sub, depth + 1, label="the subquery")

    def select(self, toks: list[T], depth: int, label: str = "") -> None:
        segs = self.segments(toks)
        if not segs:
            raise ReadError("empty")
        shown: set[int] = set()
        present: list[str] = []
        where_text = ""
        has_left_join = False
        grouped = False
        left_alias: list[str] = []
        for kw, seg in segs:
            line = seg[0].line if seg else toks[0].line
            if kw:
                kline = self._kw_line(toks, seg, kw)
            else:
                kline = line
            if kw == "WITH":
                self.with_clause(seg, depth, kline)
            elif kw == "SELECT":
                present.append("SELECT")
                self.select_list(seg, depth, kline, label, shown)
            elif kw == "VALUES":
                rows = self.items(seg)
                self.row(kline, depth, f"{label + ': ' if label else ''}makes a table of {len(rows)} row{'s' if len(rows) != 1 else ''} straight from the values written here.")
                for r in rows[1:]:
                    if r and r[0].line != kline:
                        self.row(r[0].line, depth, f"another row: {code(' '.join(t.text for t in r))}.")
            elif kw == "FROM":
                present.append("FROM")
                has_left_join = self.from_clause(seg, depth, kline, shown) or has_left_join
            elif kw == "WHERE":
                present.append("WHERE")
                where_text = " ".join(t.text for t in seg)
                self.cond_clause("WHERE", seg, depth, kline, shown)
                if self.right_names:
                    for j, t in enumerate(seg):
                        if t.text.lower() in self.right_names and j + 1 < len(seg) and seg[j + 1].text == "." and not (
                                j + 3 < len(seg) and seg[j + 3].up == "IS" and seg[j + 4 : j + 6] and (seg[j + 4].up == "NULL" or (seg[j + 4].up == "NOT" and False))):
                            self.row(kline, depth, "Watch out: this WHERE tests a column of the LEFT JOIN's right-hand table. " + self.fact("leftwhere"))
                            break
            elif kw == "GROUP":
                present.append("GROUP BY")
                grouped = True
                body = seg[1:] if seg and seg[0].up == "BY" else seg
                es = [parse_expr(x, self.src) for x in self.items(body)]
                self.row(kline, depth, "GROUP BY: puts the rows that share " + (", ".join(self.say(e, 1, "") for e in es if e) or code(" ".join(t.text for t in body))) + " into one group each, so aggregates like COUNT work per group, and the query gives one row per group.")
            elif kw == "HAVING":
                present.append("HAVING")
                self.cond_clause("HAVING", seg, depth, kline, shown, extra=self.fact("wherehaving") if "WHERE" in present else "")
            elif kw == "WINDOW":
                self.row(kline, depth, "WINDOW: gives a name to a window specification that OVER can reuse.")
            elif kw == "ORDER":
                present.append("ORDER BY")
                body = seg[1:] if seg and seg[0].up == "BY" else seg
                bits = []
                for it in self.items(body):
                    desc = bool(it) and it[-1].up == "DESC"
                    core = [t for t in it if t.up not in ("ASC", "DESC")]
                    if len(core) >= 2 and core[-2].up == "NULLS":
                        core = core[:-2]
                    e = parse_expr(core, self.src)
                    bits.append(f"{self.say(e, 1, ' '.join(t.text for t in core))} ({'biggest first' if desc else 'smallest first'})")
                nulls = "" if any(t.up == "NULLS" for t in body) else " " + self.fact("nullsfirst")
                self.row(kline, depth, "ORDER BY: sorts the result by " + ", then ".join(bits) + "." + nulls)
            elif kw == "LIMIT":
                present.append("LIMIT")
                texts = [t for t in seg]
                comma = [i for i, t in enumerate(texts) if t.text == ","]
                if comma:
                    a, b = texts[: comma[0]], texts[comma[0] + 1 :]
                    self.row(kline, depth, f"LIMIT: skips the first {code(' '.join(t.text for t in a))} rows and then keeps at most {code(' '.join(t.text for t in b))}.")
                else:
                    self.row(kline, depth, f"LIMIT: keeps at most {code(' '.join(t.text for t in texts))} row{'' if ' '.join(t.text for t in texts) == '1' else 's'}." + (" " + self.fact("limit") if "ORDER BY" not in present else ""))
            elif kw == "OFFSET":
                self.row(kline, depth, f"OFFSET: skips the first {code(' '.join(t.text for t in seg))} rows before LIMIT starts counting.")
            elif kw in ("UNION", "INTERSECT", "EXCEPT"):
                al = bool(seg) and seg[0].up == "ALL"
                what = {"UNION": "puts the rows of both queries together" + (" and keeps duplicates" if al else " and drops duplicates"),
                        "INTERSECT": "keeps only the rows that both queries give", "EXCEPT": "keeps the rows of the first query that the second does not give"}[kw]
                self.row(kline, depth, f"{kw}{' ALL' if al else ''}: {what}." + (" " + self.fact("union") if kw == "UNION" else ""))
                inner = seg[1:] if al else seg
                if inner:
                    self.select(inner, depth, label)
            elif not kw and seg:
                raise ReadError("stray tokens")
        if has_left_join and where_text:
            self.left_join_note(where_text, left_alias, depth, shown)
        order = [c for c in ("FROM", "WHERE", "GROUP BY", "HAVING", "SELECT", "ORDER BY", "LIMIT") if c in present]
        joined = any(t.up == "JOIN" for _kw, seg in segs for t in seg)
        if (len(order) >= 3 or (joined and len(order) >= 2)) and depth == 0:
            self.order_steps = order + (["(JOINs happen as part of FROM)"] if joined else [])
        _ = grouped

    def _kw_line(self, toks: list[T], seg: list[T], kw: str) -> int:
        """The line of the keyword that starts a segment: the token just before the segment's first token."""
        if seg:
            idx = toks.index(seg[0])
            if idx > 0:
                prev = toks[idx - 1]
                return prev.line
        for i, t in enumerate(toks):
            if t.up == kw:
                return t.line
        return toks[0].line

    def left_join_note(self, where_text: str, aliases: list[str], depth: int, shown: set[int]) -> None:
        return

    def with_clause(self, seg: list[T], depth: int, line: int) -> None:
        recursive = bool(seg) and seg[0].up == "RECURSIVE"
        body = seg[1:] if recursive else seg
        self.row(line, depth, "WITH: names the helper queries below so the main query can use them as if they were tables." + (" RECURSIVE lets a helper query call itself, adding rows until nothing new comes out." if recursive else ""))
        for it in self.items(body):
            m = [i for i, t in enumerate(it) if t.up == "AS"]
            if not m:
                continue
            name = it[0].text
            j = m[0] + 1
            while j < len(it) and it[j].up in ("NOT", "MATERIALIZED"):
                j += 1
            sub = it[j + 1 : -1] if j < len(it) and it[j].text == "(" else []
            self.row(it[0].line, depth, f"{name} is a helper query:")
            if sub:
                self.select(sub, depth + 1, label=f"the body of {name}")

    def select_list(self, seg: list[T], depth: int, line: int, label: str, shown: set[int]) -> None:
        body = list(seg)
        mods = ""
        if body and body[0].up in ("DISTINCT", "ALL"):
            mods = " DISTINCT keeps one copy of each different row. " + (self.fact("distinct") if body[0].up == "DISTINCT" else "")
            body = body[1:]
        items = self.items(body)
        descs: list[tuple[int, str]] = []
        for it in items:
            alias = ""
            core = it
            if len(it) >= 2 and it[-2].up == "AS":
                alias, core = it[-1].text, it[:-2]
            elif len(it) >= 2 and it[-1].kind in ("word", "qid") and it[-2].kind != "op" and it[-2].text not in (".", "(", ",") and it[-1].up not in ("END", "NULL", "ASC", "DESC") and it[-2].up not in ("DISTINCT",):
                if parse_expr(it, self.src) is None:
                    alias, core = it[-1].text, it[:-1]
            e = parse_expr(core, self.src)
            if e is None:
                raise ReadError("select item")
            self.subqueries(e, depth, shown)
            text = self.say(e, 0)
            fct = self.facts_for([e])
            descs.append((it[0].line, f"{text}" + (f" (called {alias})" if alias else "") + (f". {fct}" if fct else "")))
        head = f"{label + ': ' if label else ''}SELECT: picks what each row of the result shows: " if len(descs) == 1 or True else ""
        same_line = [d for ln, d in descs if ln == line]
        first = "; ".join(same_line[:4]) if same_line else ""
        if not same_line:
            self.row(line, depth, f"{label + ': ' if label else ''}SELECT: starts the list of what each result row shows (one item per line below)." + mods)
        else:
            self.row(line, depth, head + first + (f" ... and {len(same_line) - 4} more" if len(same_line) > 4 else "") + "." + mods)
        for ln, d in descs:
            if ln != line:
                self.row(ln, depth, f"shows {d}.")
        if len(items) == 1 and items[0] and items[0][0].text == "*":
            pass

    def from_clause(self, seg: list[T], depth: int, line: int, shown: set[int]) -> bool:
        """Rows for the table, then one per JOIN. Returns whether a LEFT JOIN was seen."""
        pieces: list[tuple[str, list[T]]] = []
        cur: list[T] = []
        kind = "FROM"
        d = 0
        i = 0
        joins = {"JOIN", "INNER", "LEFT", "RIGHT", "FULL", "CROSS", "NATURAL"}
        while i < len(seg):
            t = seg[i]
            if t.kind == "punct" and t.text == "(":
                d += 1
            elif t.kind == "punct" and t.text == ")":
                d -= 1
            if d == 0 and t.kind == "word" and t.up in joins and (t.up != "JOIN" or not (cur and cur[-1].up in joins) ) and not (cur and cur[-1].up in joins and t.up != "JOIN" and False):
                if not (t.up in ("INNER", "LEFT", "RIGHT", "FULL", "CROSS", "NATURAL") and False):
                    if cur and not (cur[-1].up in joins or cur[-1].up == "OUTER"):
                        pieces.append((kind, cur))
                        cur = []
                        j = i
                        words = []
                        while j < len(seg) and seg[j].up in joins | {"OUTER"}:
                            words.append(seg[j].up)
                            j += 1
                        kind = " ".join(words)
                        i = j
                        continue
            if d == 0 and t.kind == "punct" and t.text == ",":
                pieces.append((kind, cur))
                cur = []
                kind = "COMMA"
                i += 1
                continue
            cur.append(t)
            i += 1
        if cur:
            pieces.append((kind, cur))
        left = False
        first_line = line
        for idx, (kd, ptoks) in enumerate(pieces):
            if not ptoks:
                raise ReadError("from")
            pline = first_line if idx == 0 else self._kw_line_before(seg, ptoks[0])
            on_i = next((j for j, t in enumerate(ptoks) if t.up in ("ON", "USING") and self._top_level(ptoks, j)), None)
            src_toks = ptoks[:on_i] if on_i is not None else ptoks
            cond = ptoks[on_i:] if on_i is not None else []
            what = self.table_ref(src_toks, depth, shown)
            if idx == 0:
                self.row(pline, depth, f"FROM: reads rows from {what}.")
                continue
            if kd == "COMMA":
                self.row(pline, depth, f"also reads {what}, pairing every row with every row above (a cross join) unless WHERE ties them together.")
                continue
            jk = kd
            if "LEFT" in jk:
                left = True
                meaning = "keeps every row from the left side; where the right side has no match its columns are NULL"
            elif "RIGHT" in jk:
                meaning = "keeps every row from the right side; where the left side has no match its columns are NULL"
            elif "FULL" in jk:
                meaning = "keeps every row from both sides, filling NULLs where there is no match"
            elif "CROSS" in jk:
                meaning = "pairs every row on the left with every row on the right"
            elif "NATURAL" in jk:
                meaning = "joins on the columns that have the same name on both sides"
            else:
                meaning = "keeps only the pairs of rows that match; a row with no match is dropped"
            word = jk.replace("JOIN", "").strip().title() + " join" if jk.replace("JOIN", "").strip() else "Inner join"
            text = f"{word} with {what}: {meaning}."
            if cond:
                if cond[0].up == "ON":
                    e = parse_expr(cond[1:], self.src)
                    self.subqueries(e, depth, shown)
                    text += f" ON says which rows pair up: {self.say(e, 0, ' '.join(t.text for t in cond[1:]))}."
                else:
                    text += f" USING joins on the column(s) {code(' '.join(t.text for t in cond[1:]))} that both sides share."
            if "LEFT" in jk:
                names = {src_toks[0].text.split(".")[-1]} if src_toks and src_toks[0].text != "(" else set()
                alias = src_toks[-1].text if len(src_toks) > 1 and src_toks[-1].kind in ("word", "qid") and src_toks[-1].up not in ("AS",) else ""
                if alias:
                    names.add(alias)
                self.right_names |= {n.lower() for n in names}
            self.row(pline, depth, text)
        return left

    def _top_level(self, toks: list[T], idx: int) -> bool:
        d = 0
        for t in toks[:idx]:
            if t.kind == "punct" and t.text == "(":
                d += 1
            elif t.kind == "punct" and t.text == ")":
                d -= 1
        return d == 0

    def _kw_line_before(self, seg: list[T], first: T) -> int:
        idx = seg.index(first)
        j = idx - 1
        while j >= 0 and seg[j].up in ("JOIN", "INNER", "LEFT", "RIGHT", "FULL", "CROSS", "NATURAL", "OUTER", ","):
            j -= 1
        return seg[j + 1].line if j + 1 < idx else first.line

    def table_ref(self, toks: list[T], depth: int, shown: set[int]) -> str:
        if not toks:
            raise ReadError("table")
        if toks[0].text == "(":
            end = len(toks) - 1
            while end > 0 and toks[end].text != ")":
                end -= 1
            inner = toks[1:end]
            alias = ""
            rest = toks[end + 1 :]
            if rest:
                alias = rest[-1].text
            if inner and inner[0].up in ("SELECT", "WITH", "VALUES"):
                self.select(inner, depth + 1, label="the subquery" + (f" {alias}" if alias else ""))
                return f"a subquery{' called ' + alias if alias else ''} (explained below)"
            return f"`{code(' '.join(t.text for t in toks))}`"
        name = toks[0].text
        k = 1
        while k + 1 < len(toks) and toks[k].text == "." and True:
            name += "." + toks[k + 1].text
            k += 2
        rest = toks[k:]
        alias = ""
        if rest and rest[0].up == "AS" and len(rest) > 1:
            alias = rest[1].text
        elif rest and rest[0].kind in ("word", "qid") and rest[0].up not in ("INDEXED", "NOT"):
            alias = rest[0].text
        if len(toks) > k and toks[k].text == "(":
            return f"the table function `{code(' '.join(t.text for t in toks))}`"
        return f"the table {name}" + (f" (nicknamed {alias} so the rest of the query can say {alias}.column)" if alias else "")

    def cond_clause(self, name: str, seg: list[T], depth: int, line: int, shown: set[int], extra: str = "") -> None:
        e = parse_expr(seg, self.src)
        if e is None:
            raise ReadError("condition")
        self.subqueries(e, depth, shown)
        meaning = {"WHERE": "keeps only the rows where", "HAVING": "keeps only the groups where"}[name]
        fct = self.facts_for([e])
        text = f"{name}: {meaning} {self.say(e, 0, '')}."
        # a condition spread over several lines: one row per extra AND/OR line
        conj = []
        top = e
        while top.kind in ("paren",):
            top = top.a[0]
        if top.kind == "bin" and top.a[0] in ("AND", "OR") and seg[0].line != seg[-1].line:
            parts = self.split_conj(seg)
            if len(parts) > 1 and any(ptoks and ptoks[0].line != line for _w, ptoks in parts):
                first = True
                for word, ptoks in parts:
                    pe = parse_expr(ptoks, self.src)
                    if pe is None:
                        conj = []
                        break
                    conj.append((word, ptoks[0].line, self.say(pe, 0, "")))
                if conj:
                    for word, ln, tx in conj:
                        if first:
                            self.row(line, depth, f"{name}: {meaning} {tx}." if ln == line else f"{name}: {meaning} the conditions below all hold." if parts[0][0] == "" and top.a[0] == "AND" else f"{name}: {meaning} {tx}.")
                            if ln != line:
                                self.row(ln, depth, f"{tx}.")
                            first = False
                        else:
                            self.row(ln, depth, f"{word.lower()} {tx}.")
                    if fct or extra:
                        self.rows[-1]["text"] += " " + " ".join(x for x in (fct, extra) if x)
                    return
        self.row(line, depth, text + (" " + fct if fct else "") + (" " + extra if extra else ""))

    def split_conj(self, seg: list[T]) -> list[tuple[str, list[T]]]:
        parts: list[tuple[str, list[T]]] = []
        cur: list[T] = []
        word = ""
        d = 0
        case_d = 0
        between = 0
        for t in seg:
            if t.kind == "punct" and t.text == "(":
                d += 1
            elif t.kind == "punct" and t.text == ")":
                d -= 1
            elif t.up == "CASE":
                case_d += 1
            elif t.up == "END" and case_d:
                case_d -= 1
            elif t.up == "BETWEEN" and d == 0:
                between += 1
            if d == 0 and case_d == 0 and t.kind == "word" and t.up in ("AND", "OR"):
                if t.up == "AND" and between:
                    between -= 1
                    cur.append(t)
                    continue
                if word and t.up != word and word != "":
                    return [("", seg)]  # mixed AND / OR: do not split
                parts.append((word, cur))
                cur, word = [], t.up
                continue
            cur.append(t)
        parts.append((word, cur))
        # the first part carries no word; remaining parts carry the word that came before them
        fixed = []
        for i, (w, tk) in enumerate(parts):
            fixed.append(("" if i == 0 else parts[i][0], tk))
        return [(w if i else "", tk) for i, (w, tk) in enumerate(fixed)] if len(parts) > 1 else [("", seg)]

    # -- INSERT / UPDATE / DELETE
    def insert(self, toks: list[T], depth: int) -> None:
        line = toks[0].line
        i = 0
        verb = toks[0].up
        mode = ""
        if verb == "REPLACE":
            mode = "REPLACE"
            i = 1
        else:
            i = 1
            if toks[i].up == "OR":
                mode = toks[i + 1].up
                i += 2
        if toks[i].up != "INTO":
            raise ReadError("into")
        i += 1
        name = toks[i].text
        i += 1
        while i + 1 < len(toks) and toks[i].text == ".":
            name += "." + toks[i + 1].text
            i += 2
        cols: list[str] = []
        if i < len(toks) and toks[i].text == "(":
            j = i + 1
            while j < len(toks) and toks[j].text != ")":
                if toks[j].text != ",":
                    cols.append(toks[j].text)
                j += 1
            i = j + 1
        rest = toks[i:]
        how = ""
        if mode == "IGNORE":
            how = " " + self.fact("ignore") + " Rows that are skipped are not an error."
        elif mode == "REPLACE":
            how = " OR REPLACE (or REPLACE INTO) deletes the old row that clashes and puts the new one in its place."
        where = f"into {name}" + (f", filling the columns {', '.join(cols)}" if cols else ", filling the columns in the order the table was made")
        if rest and rest[0].up == "VALUES":
            rows = self.items(rest[1:])
            n = len(rows)
            self.row(line, depth, f"INSERT: adds {n} row{'s' if n != 1 else ''} {where}.{how}")
            for r in rows[1:]:
                if r and r[0].line != line:
                    self.row(r[0].line, depth, f"adds the row {code(' '.join(t.text for t in r))}.")
            # facts about NULL in the values are about the data, not the statement
        elif rest and rest[0].up in ("SELECT", "WITH"):
            on = next((j for j, t in enumerate(rest) if t.up == "ON" and j + 1 < len(rest) and rest[j + 1].up == "CONFLICT"), None)
            sel = rest[:on] if on is not None else rest
            self.row(line, depth, f"INSERT: adds every row that the query below gives {where}.{how}")
            self.select(sel, depth + 1, label="the query that supplies the rows")
            if on is not None:
                self.upsert(rest[on:], depth, line)
            return
        elif rest and rest[0].up == "DEFAULT":
            self.row(line, depth, f"INSERT: adds one row {where} using every column's DEFAULT.")
        else:
            raise ReadError("insert body")
        on = next((j for j, t in enumerate(rest) if t.up == "ON" and j + 1 < len(rest) and rest[j + 1].up == "CONFLICT"), None)
        if on is not None:
            self.upsert(rest[on:], depth, rest[on].line)
        ret = next((j for j, t in enumerate(rest) if t.up == "RETURNING"), None)
        if ret is not None:
            self.row(rest[ret].line, depth, "RETURNING: gives back the rows that were added.")

    def upsert(self, toks: list[T], depth: int, line: int) -> None:
        text = " ".join(t.text for t in toks)
        target = re.search(r"\((.*?)\)", text)
        t = f" on {target.group(1)}" if target else ""
        if re.search(r"DO\s+NOTHING", text, re.I):
            self.row(toks[0].line, depth, f"ON CONFLICT{t} DO NOTHING: if that value already exists, the row is skipped quietly.")
        else:
            m = re.search(r"SET\s+(.*?)(?:\s+WHERE|$)", text, re.I)
            self.row(toks[0].line, depth, f"ON CONFLICT{t} DO UPDATE: if that value already exists, the old row is changed instead ({code(m.group(1)) if m else 'see SET'}); `excluded.col` means the value that was being inserted. This is an upsert.")

    def update(self, toks: list[T], depth: int) -> None:
        line = toks[0].line
        i = 1
        if toks[i].up == "OR":
            mode = toks[i + 1].up
            i += 2
        else:
            mode = ""
        name = toks[i].text
        i += 1
        segs = []
        cur_kw, cur = "", []
        d = 0
        for t in toks[i:]:
            if t.kind == "punct" and t.text == "(":
                d += 1
            elif t.kind == "punct" and t.text == ")":
                d -= 1
            if d == 0 and t.kind == "word" and t.up in ("SET", "FROM", "WHERE", "RETURNING", "ORDER", "LIMIT") and not (t.up == "ORDER" and False):
                segs.append((cur_kw, cur))
                cur_kw, cur = t.up, []
            else:
                cur.append(t)
        segs.append((cur_kw, cur))
        has_where = any(k == "WHERE" for k, _ in segs)
        ign = " " + self.fact("ignore") if mode == "IGNORE" else ""
        for k, seg in segs:
            ln = line if k == "" else self._seg_line(toks, seg, k)
            if k == "SET":
                parts = []
                for it in self.items(seg):
                    eq = next((j for j, t in enumerate(it) if t.text == "="), None)
                    if eq is None:
                        raise ReadError("set")
                    e = parse_expr(it[eq + 1 :], self.src)
                    if e is None:
                        raise ReadError("set value")
                    self.subqueries(e, depth, set())
                    parts.append(f"{' '.join(t.text for t in it[:eq])} becomes {self.say(e, 0)}")
                    fct = self.facts_for([e])
                    if fct:
                        parts[-1] += f". {fct}"
                self.row(line, depth, f"UPDATE: changes the table {name}: " + "; ".join(parts) + "." + ign + ("" if has_where else " There is no WHERE, so EVERY row is changed. " + self.fact("nowhere")))
            elif k == "WHERE":
                self.cond_clause("WHERE", seg, depth, ln, set())
            elif k == "FROM":
                self.from_clause(seg, depth, ln, set())
            elif k == "RETURNING":
                self.row(ln, depth, "RETURNING: gives back the rows that were changed.")
            elif k in ("ORDER", "LIMIT"):
                self.row(ln, depth, f"{k}: limits which rows are changed.")

    def _seg_line(self, toks: list[T], seg: list[T], kw: str) -> int:
        if seg:
            idx = toks.index(seg[0])
            return toks[idx - 1].line if idx > 0 else seg[0].line
        return toks[0].line

    def delete(self, toks: list[T], depth: int) -> None:
        line = toks[0].line
        if len(toks) < 3 or toks[1].up != "FROM":
            raise ReadError("delete")
        name = toks[2].text
        w = next((i for i, t in enumerate(toks) if t.up == "WHERE"), None)
        ret = next((i for i, t in enumerate(toks) if t.up == "RETURNING"), None)
        if w is None:
            self.row(line, depth, f"DELETE: removes rows from {name}. There is no WHERE, so EVERY row goes (the table itself stays). " + self.fact("nowhere"))
        else:
            self.row(line, depth, f"DELETE: removes rows from {name}, the ones the WHERE below picks.")
            end = ret if ret is not None and ret > w else len(toks)
            self.cond_clause("WHERE", toks[w + 1 : end], depth, toks[w].line, set())
        if ret is not None:
            self.row(toks[ret].line, depth, "RETURNING: gives back the rows that were removed.")

    # -- CREATE / ALTER
    def create(self, toks: list[T], depth: int) -> None:
        line = toks[0].line
        i = 1
        temp = False
        unique = False
        while toks[i].up in ("TEMP", "TEMPORARY", "UNIQUE", "VIRTUAL"):
            temp = temp or toks[i].up in ("TEMP", "TEMPORARY")
            unique = unique or toks[i].up == "UNIQUE"
            i += 1
        kind = toks[i].up
        i += 1
        if toks[i].up == "IF":
            i += 3
        name = toks[i].text
        i += 1
        while i + 1 < len(toks) and toks[i].text == ".":
            name += "." + toks[i + 1].text
            i += 2
        if kind == "TABLE":
            self.create_table(toks, i, name, depth, line)
        elif kind == "INDEX":
            on = next((j for j, t in enumerate(toks) if t.up == "ON"), None)
            tbl = toks[on + 1].text if on is not None else "a table"
            cols = re.search(r"\((.*)\)", " ".join(t.text for t in toks[on:])) if on is not None else None
            self.row(line, depth, f"creates {'a unique ' if unique else 'an '}index {name} on {tbl}({cols.group(1) if cols else ''}): a sorted lookup structure that makes searches on those columns faster" + ("; it also refuses two rows with the same value there" if unique else "") + ".")
        elif kind == "VIEW":
            self.row(line, depth, f"creates the view {name}: a saved query that behaves like a table, and runs again each time it is read.")
            a = next((j for j, t in enumerate(toks) if t.up == "AS"), None)
            if a is not None:
                self.select(toks[a + 1 :], depth + 1, label=f"the query behind {name}")
        elif kind == "TRIGGER":
            self.trigger(toks, i, name, depth, line)
        else:
            raise ReadError("create")

    def create_table(self, toks: list[T], i: int, name: str, depth: int, line: int) -> None:
        if i < len(toks) and toks[i].up == "AS":
            self.row(line, depth, f"creates the table {name} from the rows a query gives.")
            self.select(toks[i + 1 :], depth + 1, label="the query that fills it")
            return
        if i >= len(toks) or toks[i].text != "(":
            raise ReadError("create table")
        end = len(toks) - 1
        while end > i and toks[end].text != ")":
            end -= 1
        defs = self.items(toks[i + 1 : end])
        tail = " ".join(t.up for t in toks[end + 1 :])
        cols = [d for d in defs if d and d[0].up not in ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT")]
        self.row(line, depth, f"creates the table {name} with {len(cols)} column{'s' if len(cols) != 1 else ''}. A table starts empty; each INSERT adds rows. SQLite column types are hints, not strict checks." + (" WITHOUT ROWID stores it as a plain primary-key tree." if "WITHOUT ROWID" in tail else ""))
        for d in defs:
            if not d:
                continue
            first = d[0].up
            if first in ("PRIMARY", "UNIQUE", "CHECK", "FOREIGN", "CONSTRAINT"):
                self.row(d[0].line, depth + 1, {"PRIMARY": "a table rule: the columns named form the primary key (each row's unique name).", "UNIQUE": "a table rule: no two rows may share these values.",
                         "CHECK": f"a table rule: every row must satisfy `{code(' '.join(t.text for t in d[1:]))}`.", "FOREIGN": "a table rule: these columns must match a row in another table.",
                         "CONSTRAINT": f"a named table rule: {code(' '.join(t.text for t in d[2:]))}."}[first])
                continue
            cname = d[0].text
            ctype_toks = []
            j = 1
            while j < len(d) and d[j].up not in ("PRIMARY", "NOT", "NULL", "UNIQUE", "CHECK", "DEFAULT", "REFERENCES", "COLLATE", "GENERATED", "AS", "CONSTRAINT"):
                ctype_toks.append(d[j].text)
                j += 1
            ctype = " ".join(ctype_toks)
            bits = []
            rest = " ".join(t.up for t in d[j:])
            if "PRIMARY KEY" in rest:
                bits.append("the primary key (each row's unique name" + (", and an INTEGER one fills itself in when left out" if ctype.upper() == "INTEGER" else "") + ")")
            if "AUTOINCREMENT" in rest:
                bits.append("AUTOINCREMENT never reuses an old number")
            if "NOT NULL" in rest:
                bits.append("NOT NULL: it must always have a value")
            if "UNIQUE" in rest:
                bits.append("UNIQUE: no two rows may share it")
            m = re.search(r"DEFAULT\s+(\S+)", " ".join(t.text for t in d[j:]), re.I)
            if m:
                bits.append(f"DEFAULT {m.group(1)}: used when an INSERT leaves it out")
            if "CHECK" in rest:
                bits.append("CHECK: every row must pass the test written")
            if "REFERENCES" in rest:
                bits.append("REFERENCES: it must match a row in another table")
            self.row(d[0].line, depth + 1, f"the column {cname}" + (f", type {ctype}" if ctype else ", with no declared type (SQLite then accepts any kind of value)") + (": " + "; ".join(bits) if bits else "") + ".")

    def trigger(self, toks: list[T], i: int, name: str, depth: int, line: int) -> None:
        text = " ".join(t.up for t in toks[i:])
        m = re.match(r"(BEFORE|AFTER|INSTEAD OF)?\s*(INSERT|UPDATE|DELETE)(?: OF [\w, ]+)? ON (\w+)", text)
        if not m:
            raise ReadError("trigger")
        when, ev, tbl = m.groups()
        self.row(line, depth, f"creates the trigger {name}: {(when or 'AFTER').lower()} every {ev} on {tbl.lower()}, it runs the statements between BEGIN and END by itself (NEW is the new row, OLD the old one).")
        b = next((j for j, t in enumerate(toks) if t.up == "BEGIN"), None)
        if b is not None:
            inner = toks[b + 1 :]
            if inner and inner[-1].up == "END":
                inner = inner[:-1]
            if inner and inner[-1].text == ";":
                inner = inner[:-1]
            for st in split_statements(inner + [T("punct", ";", 0, 0, 0)]):
                self.statement(st, depth + 1)

    def alter(self, toks: list[T], depth: int) -> None:
        line = toks[0].line
        if toks[1].up != "TABLE":
            raise ReadError("alter")
        name = toks[2].text
        rest = " ".join(t.up for t in toks[3:])
        if rest.startswith("RENAME TO"):
            self.row(line, depth, f"ALTER TABLE: renames the table {name} to {toks[-1].text}.")
        elif rest.startswith("RENAME COLUMN") or rest.startswith("RENAME "):
            self.row(line, depth, f"ALTER TABLE: renames a column of {name}: `{code(' '.join(t.text for t in toks[3:]))}`.")
        elif rest.startswith("ADD"):
            col = [t for t in toks[3:] if t.up not in ("ADD", "COLUMN")]
            nn = " ADDing a NOT NULL column needs a DEFAULT unless the table is empty." if "NOT NULL" in rest and "DEFAULT" not in rest else ""
            self.row(line, depth, f"ALTER TABLE: adds the column {col[0].text if col else ''} to {name}; existing rows get its DEFAULT (or NULL).{nn}")
        elif rest.startswith("DROP"):
            self.row(line, depth, f"ALTER TABLE: removes the column {toks[-1].text} from {name}, along with its data.")
        else:
            raise ReadError("alter")


def _read_rows(code_text: str) -> tuple[list[dict], int, list[str]]:
    toks = tokenize(code_text)
    reader = Reader(code_text)
    for st in split_statements(toks):
        try:
            reader.statement(st)
        except Exception:
            reader.bad_lines.update(range(st[0].line, st[-1].line + 1))
            reader.row(st[0].line, 0, C.FALLBACK)
    lines_with_tokens = {t.line for t in toks}
    rows = sorted(reader.rows, key=lambda r: r["line"])
    bad = sorted(reader.bad_lines & lines_with_tokens)
    # every line with tokens counts once; a line is specific unless it lies in a statement that fell back
    return rows, len(lines_with_tokens), [str(b) for b in bad]


def explain_sql(code_text: str, *, run: bool = True, context: str = "") -> dict:
    """Walk SQL statement by statement, clause by clause, and (when `run`) say what the last query returned."""
    if not code_text.strip():
        return C.empty()
    reader = Reader(code_text)
    try:
        toks = tokenize(code_text)
        for st in split_statements(toks):
            try:
                reader.statement(st)
            except Exception:
                reader.row(st[0].line, 0, C.FALLBACK)
    except Exception:
        pass
    rows = sorted(reader.rows, key=lambda r: r["line"])
    kinds = []
    for m in re.finditer(r"^\s*(CREATE\s+(?:TEMP\s+|TEMPORARY\s+|UNIQUE\s+)?(?:TABLE|VIEW|INDEX|TRIGGER)|INSERT|UPDATE|DELETE|SELECT|WITH|ALTER|DROP|BEGIN|COMMIT|ROLLBACK)", code_text, re.I | re.M):
        kinds.append(m.group(1).split()[0].upper())
    summary = "Here's what each statement and clause does:" if len(kinds) > 1 or reader.order_steps else "Here's what this statement does:"
    notes: list[str] = []
    error_note = None
    if reader.order_steps:
        notes.append("How the database works a query out is not the order it is written in: " + " -> ".join(s for s in reader.order_steps if not s.startswith("(")) + "." + ("".join(" " + s for s in reader.order_steps if s.startswith("("))))
    if run:
        prog = sql_program(code_text)
        from code_coach.gotchas.runner import run_program

        try:
            res = run_program("sql", prog.text, timeout=3.0)
        except Exception as exc:
            notes.append(f"It was not run here ({str(exc).strip() or 'no SQLite found'}), so there is no result to show.")
        else:
            if res.timed_out:
                notes.append("It was still running after 3 seconds, so it was stopped.")
            elif not res.ok:
                first = (res.stderr.strip().split("\n")[0] if res.stderr.strip() else "the database refused it")
                error_note = "SQLite stopped with an error: " + re.sub(r"^SQLError:\s*", "", first)
            else:
                out = res.stdout.strip()
                if out:
                    shown = out if len(out) <= 300 else out[:297] + "..."
                    notes.append(f"The last query returned: {shown} (columns are joined with |, rows with ;, and NULL is written NULL).")
                else:
                    notes.append("It ran without error, but no statement returned rows, so there is nothing to show.")
    return C.finish(summary, rows, notes, error_note)
