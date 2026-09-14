"""PostgreSQL workbook shapes: the things SQLite cannot do.

The SQL pages already teach SELECT, WHERE, JOIN and GROUP BY, and those
are the same in both dialects. Repeating them here in a second dialect
would be twenty more pages of the same ideas. So these pages are only
the places PostgreSQL differs — which is also the list of things that
come up in a job: casts, ILIKE, RETURNING, upserts, generate_series,
arrays, JSONB, and window functions done properly.

Where the expected output comes from
------------------------------------
The same way round as the SQL pages, and for the same reason. The
answer is computed in Python from a hand-written mirror of the rows,
and then drawn with the runner's table formatter. Running the query to
find out what it returns would compare the query against itself and
pass just as happily if it were wrong.

Filtering a list of dicts in Python and asking PostgreSQL to execute a
query are genuinely different implementations, so agreeing means
something. The cost is that this file has to reproduce PostgreSQL's own
way of writing values down — `t` for true, `{admin,beta}` for an array,
`{"plan": "pro"}` with the space after the colon, a numeric that keeps
its trailing zero. Every one of those was read off a real result rather
than guessed, and the suite runs each reference query and holds this
file to what came back.

Timestamps are printed in UTC because the runner pins the session to
it. Without that the same query answers differently on a machine in
another timezone, and every exercise with a time in it becomes a test
of where you live.
"""

from __future__ import annotations

from code_coach.sql_runner import _as_table
from code_coach.workbook.emit import Shape

LANGUAGES: tuple[str, ...] = ("postgresql",)

SHAPES: tuple[Shape, ...] = (
    Shape("pg_cast", "turning one type into another with ::"),
    Shape("pg_ilike", "matching text without caring about case"),
    Shape("pg_series", "rows made out of nothing with generate_series"),
    Shape("pg_array", "a column that holds a list"),
    Shape("pg_jsonb", "a column that holds a document"),
    Shape("pg_returning", "getting back what a write just did"),
    Shape("pg_window", "a calculation across rows without collapsing them"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── The rows, as Python ──────────────────────────────────────
#
# A hand-written mirror of what tools/get_postgres.py loads. Written out
# rather than read back from the database on purpose: this is the
# independent half of the check, and reading it back would make the
# check circular. If these drift from the schema the tests fail, which
# is exactly what they are for.

USERS: tuple[dict, ...] = (
    {
        "id": 1, "name": "Alex", "city": "Denver", "age": 30,
        "email": "alex@example.com", "active": True,
        "joined": "2024-01-15 09:30:00+00",
        "tags": ["admin", "beta"],
        "profile": {"plan": "pro", "seats": 3},
    },
    {
        "id": 2, "name": "Bailey", "city": "Austin", "age": 24,
        "email": None, "active": True,
        "joined": "2024-03-02 14:05:00+00",
        "tags": ["beta"],
        "profile": {"plan": "free"},
    },
    {
        "id": 3, "name": "Casey", "city": "Denver", "age": 41,
        "email": "casey@example.com", "active": False,
        "joined": "2023-11-20 08:00:00+00",
        "tags": [],
        "profile": {"plan": "pro", "seats": 12},
    },
    {
        "id": 4, "name": "Devon", "city": "Boston", "age": 17,
        "email": "devon@example.com", "active": True,
        "joined": "2024-05-30 17:45:00+00",
        "tags": ["student"],
        "profile": {"plan": "free", "referred_by": 1},
    },
    {
        "id": 5, "name": "Erin", "city": "Austin", "age": 35,
        "email": None, "active": True,
        "joined": "2024-02-11 11:15:00+00",
        "tags": ["admin"],
        "profile": {"plan": "team", "seats": 5},
    },
)

ORDERS: tuple[dict, ...] = (
    {"id": 1, "user_id": 1, "item": "Keyboard", "price": "49.99"},
    {"id": 2, "user_id": 1, "item": "Monitor", "price": "219.00"},
    {"id": 3, "user_id": 2, "item": "Mouse", "price": "19.50"},
    {"id": 4, "user_id": 3, "item": "Desk", "price": "315.75"},
    {"id": 5, "user_id": 5, "item": "Lamp", "price": "34.25"},
    {"id": 6, "user_id": 5, "item": "Keyboard", "price": "49.99"},
)

#: The next id an INSERT without one will get. The sequence is set to
#: the highest hand-written id when the data is loaded, so the first
#: new row is one past it — and because every go is rolled back, it is
#: this same number every time rather than climbing.
NEXT_ORDER_ID = len(ORDERS) + 1


# ── Writing values down the way PostgreSQL does ──────────────


def pg_text(value) -> str:
    """One value, as psql prints it.

    Each of these was read off a real result. They are easy to guess
    wrong — a Python bool is True and PostgreSQL's is t, a Python list
    is [1, 2] and an array is {1,2}, and json.dumps puts no space after
    a colon where PostgreSQL does.
    """
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "t" if value else "f"
    if isinstance(value, list):
        return "{" + ",".join(_array_item(v) for v in value) + "}"
    if isinstance(value, dict):
        inner = ", ".join(
            f'"{k}": {_json_item(v)}' for k, v in value.items())
        return "{" + inner + "}"
    return str(value)


def _array_item(value) -> str:
    """Inside an array literal, where strings are bare unless they need
    quoting — which none of this data does."""
    return "NULL" if value is None else str(value)


def _json_item(value) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def table(columns: list[str], rows: list[list]) -> str:
    """The rows as the runner draws them, values written PostgreSQL's way."""
    return _as_table(columns, [tuple(pg_text(c) for c in row) for row in rows])


def _sorted_users(by: str = "id") -> list[dict]:
    return sorted(USERS, key=lambda u: u[by])



# ── Reading the mirror, from arguments that are data ─────────
#
# Not from a lambda in the arguments. An exercise carries a shape and
# its arguments and never code — that rule is what lets the same
# argument dict be printed, compared, stored and reasoned about, and a
# function hidden in there would be the one that could not.


def _keeps(user: dict, rule: dict) -> bool:
    kind = rule["kind"]
    if kind == "has_tag":
        return rule["tag"] in user["tags"]
    if kind == "no_tags":
        return not user["tags"]
    if kind == "any_tags":
        return bool(user["tags"])
    if kind == "json_equals":
        return user["profile"].get(rule["key"]) == rule["value"]
    if kind == "json_has_key":
        return rule["key"] in user["profile"]
    if kind == "json_missing_key":
        return rule["key"] not in user["profile"]
    if kind == "json_at_least":
        seats = user["profile"].get(rule["key"])
        return isinstance(seats, int) and seats >= rule["value"]
    raise ValueError(f"no filter called {kind}")


def _cell(user: dict, col: dict):
    kind = col["kind"]
    if kind == "column":
        return user[col["name"]]
    if kind == "array_length":
        # PostgreSQL gives NULL rather than 0 for an empty array, which
        # is the trap the page about it is built on.
        return len(user["tags"]) or None
    if kind == "json_text":
        # ->> gives text, and a missing key gives NULL rather than an
        # error — the other half of the same lesson.
        found = user["profile"].get(col["key"])
        if found is None:
            return None
        return "true" if found is True else str(found)
    raise ValueError(f"no column called {kind}")

# ── The reference query for each shape ───────────────────────


def _cast(a: dict) -> str:
    return (
        f"SELECT {a['expression']} AS {a['label']};"
    )


def _ilike(a: dict) -> str:
    return (
        f"SELECT name FROM users WHERE name ILIKE '{a['pattern']}' "
        "ORDER BY name;"
    )


def _series(a: dict) -> str:
    return (
        f"SELECT n, {a['expression']} AS {a['label']} "
        f"FROM generate_series({a['start']}, {a['stop']}) AS n;"
    )


def _array(a: dict) -> str:
    return f"SELECT {a['columns']} FROM users WHERE {a['where']} ORDER BY id;"


def _jsonb(a: dict) -> str:
    return f"SELECT {a['columns']} FROM users WHERE {a['where']} ORDER BY id;"


def _returning(a: dict) -> str:
    return (
        f"INSERT INTO orders (user_id, item, price) "
        f"VALUES ({a['user_id']}, '{a['item']}', {a['price']}) "
        f"RETURNING {a['returning']};"
    )


def _window(a: dict) -> str:
    return (
        f"SELECT name, {a['call']} OVER ({a['over']}) AS {a['label']} "
        "FROM users ORDER BY id;"
    )


_BUILDERS = {
    "pg_cast": _cast,
    "pg_ilike": _ilike,
    "pg_series": _series,
    "pg_array": _array,
    "pg_jsonb": _jsonb,
    "pg_returning": _returning,
    "pg_window": _window,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES or shape not in _BUILDERS:
        return None
    return _BUILDERS[shape](args)


# ── What each one should come back with ──────────────────────


def expected_output(shape: str, args: dict, value=None) -> str:
    a = args

    if shape == "pg_cast":
        return table([a["label"]], [[a["answer"]]])

    if shape == "pg_ilike":
        kept = [u["name"] for u in USERS if _ilike_match(u["name"], a["pattern"])]
        if not kept:
            raise ValueError("the pattern must match at least one name")
        if len(kept) == len(USERS):
            raise ValueError("the pattern must leave someone out")
        return table(["name"], [[n] for n in sorted(kept)])

    if shape == "pg_series":
        rows = [[n, a["answers"][i]]
                for i, n in enumerate(range(a["start"], a["stop"] + 1))]
        if len(rows) != len(a["answers"]):
            raise ValueError("one answer per row in the series")
        return table(["n", a["label"]], rows)

    if shape in ("pg_array", "pg_jsonb"):
        kept = [u for u in _sorted_users() if _keeps(u, a["filter"])]
        if not kept:
            raise ValueError("the filter must keep at least one row")
        if len(kept) == len(USERS):
            raise ValueError("the filter must leave something out")
        headers = [col["header"] for col in a["select"]]
        return table(
            headers,
            [[_cell(u, col) for col in a["select"]] for u in kept],
        )

    if shape == "pg_returning":
        made = {
            "id": NEXT_ORDER_ID,
            "user_id": a["user_id"],
            "item": a["item"],
            "price": a["price"],
        }
        return table(a["headers"], [[made[c] for c in a["headers"]]])

    if shape == "pg_window":
        rows = [[u["name"], a["answers"][u["id"] - 1]] for u in _sorted_users()]
        return table(["name", a["label"]], rows)

    raise ValueError(f"no expected output for {shape}")


def _ilike_match(text: str, pattern: str) -> bool:
    """LIKE matching, case-insensitively, for % and _ only.

    Enough for these patterns and no more — a general LIKE engine would
    be a second implementation of something PostgreSQL already does,
    and the point of this file is to be a different implementation of
    the *answer*, not of the database.
    """
    import re

    escaped = []
    for ch in pattern:
        if ch == "%":
            escaped.append(".*")
        elif ch == "_":
            escaped.append(".")
        else:
            escaped.append(re.escape(ch))
    return re.fullmatch("".join(escaped), text, re.IGNORECASE) is not None


__all__ = [
    "LANGUAGES", "SHAPES", "SHAPE_IDS",
    "expected_output", "handles", "solution",
    "USERS", "ORDERS", "NEXT_ORDER_ID", "pg_text", "table",
]
