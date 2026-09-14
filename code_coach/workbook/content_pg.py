"""PostgreSQL pages: the seven places it is not SQLite.

The SQL pages already teach SELECT, WHERE, ORDER BY, GROUP BY and JOIN,
and every one of those is the same here. Doing them again in a second
dialect would be twenty more pages of things you already know.

So these are only the differences, which turn out to be the same list
as "what a job expects you to know about PostgreSQL": casting with ::,
case-insensitive matching, making rows out of nothing, a column that
holds a list, a column that holds a document, getting back what a write
just did, and calculating across rows without collapsing them.

The tables are the ones the runner loads — the same five people and six
orders as the SQLite database, so nothing new has to be learned to
start, plus the columns SQLite has no answer for:

    users(id, name, city, age, email, active, joined, tags, profile)
    orders(id, user_id, item, price, placed)

Every go runs inside a transaction that is rolled back, so the pages
that write can be done twenty times and the sixth order is still the
sixth order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PG = ("postgresql",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=PG,
        tier="intermediate",
    )


def _cast(label, expression, answer):
    return {"label": label, "expression": expression, "answer": answer}


CAST = _page(
    "pg-cast", 1,
    "Turning one type into another",
    "PostgreSQL will not quietly treat text as a number the way some "
    "databases do. `::` is how you say you meant it — and where the "
    "answer changes depending on which type you land on.",
    "SELECT '42'::int + 8 AS answer;   →   50, because the text was "
    "turned into a number before the adding rather than after it.",
    "pg_cast",
    [
        ("Cast the text '42' to an integer and add 8, as answer.",
         _cast("answer", "'42'::int + 8", 50)),
        ("Cast the text '7' to an integer and multiply by 6, as answer.",
         _cast("answer", "'7'::int * 6", 42)),
        ("Divide 10 by 4 as plain integers, as answer.",
         _cast("answer", "10 / 4", 2)),
        ("Divide 10 by 4 with the 10 cast to numeric, as answer.",
         _cast("answer", "10::numeric / 4", "2.5000000000000000")),
        ("Cast 9.99 to an integer, as answer.",
         _cast("answer", "9.99::int", 10)),
        ("Cast 9.49 to an integer, as answer.",
         _cast("answer", "9.49::int", 9)),
        ("Cast the number 42 to text and join '!' on the end, as answer.",
         _cast("answer", "42::text || '!'", "42!")),
        ("Cast the text 'true' to a boolean, as answer.",
         _cast("answer", "'true'::boolean", True)),
        ("Cast the text 'f' to a boolean, as answer.",
         _cast("answer", "'f'::boolean", False)),
        ("Round 2.675 to two decimal places as numeric, as answer.",
         _cast("answer", "round(2.675::numeric, 2)", "2.68")),
        ("Cast the text '2024-01-15' to a date, as answer.",
         _cast("answer", "'2024-01-15'::date", "2024-01-15")),
        ("Cast 100 to numeric(10, 2), as answer.",
         _cast("answer", "100::numeric(10, 2)", "100.00")),
        ("Cast the text '3.7' to numeric and add 0.3, as answer.",
         _cast("answer", "'3.7'::numeric + 0.3", "4.0")),
        ("Cast the text '08' to an integer, as answer.",
         _cast("answer", "'08'::int", 8)),
        ("Cast the integer 5 to numeric and divide by 2, as answer.",
         _cast("answer", "5::numeric / 2", "2.5000000000000000")),
        ("Cast -9.5 to an integer, as answer.",
         _cast("answer", "-9.5::int", -10)),
    ],
)


def _ilike(pattern):
    return {"pattern": pattern}


ILIKE = _page(
    "pg-ilike", 2,
    "Matching text without caring about case",
    "LIKE is case-sensitive, so 'a%' finds nobody in a table of "
    "capitalised names. ILIKE is the same thing with the case ignored, "
    "and it is PostgreSQL's alone — no other major database spells it "
    "this way.",
    "SELECT name FROM users WHERE name ILIKE 'a%' ORDER BY name;   "
    "→   Alex, where LIKE 'a%' would have found nobody at all.",
    "pg_ilike",
    [
        ("Names starting with a, either case. Ordered by name.", _ilike("a%")),
        ("Names starting with b, either case. Ordered by name.", _ilike("b%")),
        ("Names starting with c, either case. Ordered by name.", _ilike("c%")),
        ("Names starting with d, either case. Ordered by name.", _ilike("d%")),
        ("Names starting with e, either case. Ordered by name.", _ilike("e%")),
        ("Names ending in n, either case. Ordered by name.", _ilike("%n")),
        ("Names ending in y, either case. Ordered by name.", _ilike("%y")),
        ("Names containing le, either case. Ordered by name.", _ilike("%le%")),
        ("Names containing ai, either case. Ordered by name.", _ilike("%ai%")),
        ("Names containing as, either case. Ordered by name.", _ilike("%as%")),
        ("Names of exactly four letters. Ordered by name.", _ilike("____")),
        ("Names of exactly five letters. Ordered by name.", _ilike("_____")),
        ("Names whose second letter is l. Ordered by name.", _ilike("_l%")),
        ("Names whose second letter is a. Ordered by name.", _ilike("_a%")),
        ("Names spelled ALEX, in any case at all.", _ilike("ALEX")),
        ("Names spelled erin, in any case at all.", _ilike("erin")),
    ],
)


def _series(start, stop, label, expression, answers):
    return {
        "start": start, "stop": stop, "label": label,
        "expression": expression, "answers": answers,
    }


SERIES = _page(
    "pg-series", 3,
    "Rows made out of nothing",
    "generate_series invents rows. It is how you make a calendar to "
    "join against, fill the gaps in a report, or produce test data — "
    "and it is a table, so everything you know about FROM still works.",
    "SELECT n, n * n AS squared FROM generate_series(1, 4) AS n;   "
    "→   four rows, from a table that was never stored anywhere.",
    "pg_series",
    [
        ("The numbers 1 to 4, with each one squared as squared.",
         _series(1, 4, "squared", "n * n", [1, 4, 9, 16])),
        ("The numbers 1 to 5, with each one doubled as doubled.",
         _series(1, 5, "doubled", "n * 2", [2, 4, 6, 8, 10])),
        ("The numbers 1 to 6, with each one tripled as tripled.",
         _series(1, 6, "tripled", "n * 3", [3, 6, 9, 12, 15, 18])),
        ("The numbers 1 to 5, with ten times each as tens.",
         _series(1, 5, "tens", "n * 10", [10, 20, 30, 40, 50])),
        ("The numbers 1 to 4, with one more than each as next_one.",
         _series(1, 4, "next_one", "n + 1", [2, 3, 4, 5])),
        ("The numbers 3 to 7, with each one squared as squared.",
         _series(3, 7, "squared", "n * n", [9, 16, 25, 36, 49])),
        ("The numbers 1 to 5, with each one cubed as cubed.",
         _series(1, 5, "cubed", "n * n * n", [1, 8, 27, 64, 125])),
        ("The numbers 1 to 4, each as text with an x on the end, as tag.",
         _series(1, 4, "tag", "n::text || 'x'", ["1x", "2x", "3x", "4x"])),
        ("The numbers 1 to 6, with the remainder of each divided by 3 as left_over.",
         _series(1, 6, "left_over", "n % 3", [1, 2, 0, 1, 2, 0])),
        ("The numbers 1 to 5, with each one less one as before_it.",
         _series(1, 5, "before_it", "n - 1", [0, 1, 2, 3, 4])),
        # Rounded rather than raw: the scale PostgreSQL gives a numeric
        # division depends on both operands, so 2/2 comes back with
        # twenty decimal places and 3/2 with sixteen. Reproducing that
        # rule in the mirror would be re-implementing PostgreSQL's
        # arithmetic to check PostgreSQL's arithmetic, which is not what
        # an independent answer means. round() makes the question about
        # division rather than about scale.
        ("The numbers 2 to 6, each halved as numeric and rounded to two places, as half.",
         _series(2, 6, "half", "round(n::numeric / 2, 2)",
                 ["1.00", "1.50", "2.00", "2.50", "3.00"])),
        ("The numbers 1 to 4, with each one negated as flipped.",
         _series(1, 4, "flipped", "-n", [-1, -2, -3, -4])),
        ("The numbers 1 to 5, with whether each is even as even.",
         _series(1, 5, "even", "n % 2 = 0",
                 [False, True, False, True, False])),
        ("The numbers 1 to 4, with each one hundred times bigger as hundreds.",
         _series(1, 4, "hundreds", "n * 100", [100, 200, 300, 400])),
        ("The numbers 5 to 9, with each one squared as squared.",
         _series(5, 9, "squared", "n * n", [25, 36, 49, 64, 81])),
        ("The numbers 1 to 6, with each one as text, as spelled.",
         _series(1, 6, "spelled", "n::text",
                 ["1", "2", "3", "4", "5", "6"])),
    ],
)


def _col(header, name=None, kind="column", key=None):
    out = {"header": header, "kind": kind}
    if kind == "column":
        out["name"] = name or header
    if key:
        out["key"] = key
    return out


def _array(columns, select, where, rule):
    return {
        "columns": columns, "select": select, "where": where, "filter": rule,
    }


ARRAY = _page(
    "pg-array", 4,
    "A column that holds a list",
    "A text[] is a real column holding several values, and it needs its "
    "own operators: ANY to ask whether something is in it, and "
    "array_length to count it — which answers NULL rather than 0 for an "
    "empty one, and catches everybody once.",
    "SELECT name, tags FROM users WHERE 'admin' = ANY(tags) ORDER BY id;",
    "pg_array",
    [
        ("Name and tags of everyone tagged admin. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "'admin' = ANY(tags)", {"kind": "has_tag", "tag": "admin"})),
        ("Name and tags of everyone tagged beta. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "'beta' = ANY(tags)", {"kind": "has_tag", "tag": "beta"})),
        ("Name and tags of everyone tagged student. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "'student' = ANY(tags)",
                {"kind": "has_tag", "tag": "student"})),
        ("Just the names of everyone tagged admin. By id.",
         _array("name", [_col("name")],
                "'admin' = ANY(tags)", {"kind": "has_tag", "tag": "admin"})),
        ("Name and city of everyone tagged beta. By id.",
         _array("name, city", [_col("name"), _col("city")],
                "'beta' = ANY(tags)", {"kind": "has_tag", "tag": "beta"})),
        ("Name and tags of everyone with no tags at all. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "cardinality(tags) = 0", {"kind": "no_tags"})),
        ("Name and tags of everyone with at least one tag. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "cardinality(tags) > 0", {"kind": "any_tags"})),
        ("Name and how many tags each has, as n, for everyone tagged admin. By id.",
         _array("name, array_length(tags, 1) AS n",
                [_col("name"), _col("n", kind="array_length")],
                "'admin' = ANY(tags)", {"kind": "has_tag", "tag": "admin"})),
        ("Name and how many tags each has, as n, for everyone with tags. By id.",
         _array("name, array_length(tags, 1) AS n",
                [_col("name"), _col("n", kind="array_length")],
                "cardinality(tags) > 0", {"kind": "any_tags"})),
        ("Name and how many tags each has, as n, for everyone with none. By id.",
         _array("name, array_length(tags, 1) AS n",
                [_col("name"), _col("n", kind="array_length")],
                "cardinality(tags) = 0", {"kind": "no_tags"})),
        ("Name, city and tags of everyone tagged admin. By id.",
         _array("name, city, tags",
                [_col("name"), _col("city"), _col("tags")],
                "'admin' = ANY(tags)", {"kind": "has_tag", "tag": "admin"})),
        ("Name and age of everyone tagged beta. By id.",
         _array("name, age", [_col("name"), _col("age")],
                "'beta' = ANY(tags)", {"kind": "has_tag", "tag": "beta"})),
        ("Name and email of everyone tagged admin. By id.",
         _array("name, email", [_col("name"), _col("email")],
                "'admin' = ANY(tags)", {"kind": "has_tag", "tag": "admin"})),
        ("Name and tags of everyone tagged admin, using the ANY form. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "tags @> ARRAY['admin']",
                {"kind": "has_tag", "tag": "admin"})),
        ("Name and tags of everyone tagged student, using the contains form. By id.",
         _array("name, tags", [_col("name"), _col("tags")],
                "tags @> ARRAY['student']",
                {"kind": "has_tag", "tag": "student"})),
        ("Name, tags and how many, as n, for everyone tagged beta. By id.",
         _array("name, tags, array_length(tags, 1) AS n",
                [_col("name"), _col("tags"),
                 _col("n", kind="array_length")],
                "'beta' = ANY(tags)", {"kind": "has_tag", "tag": "beta"})),
    ],
)


JSONB = _page(
    "pg-jsonb", 5,
    "A column that holds a document",
    "jsonb keeps a whole document in one column. `->` gives you JSON "
    "back and `->>` gives you text, which is the distinction that "
    "catches people: compare with ->> or you are comparing a JSON "
    "string to a text one. A missing key is NULL rather than an error.",
    "SELECT name, profile->>'plan' AS plan FROM users "
    "WHERE profile->>'plan' = 'pro' ORDER BY id;",
    "pg_jsonb",
    [
        ("Name and plan, as plan, for everyone on the pro plan. By id.",
         _array("name, profile->>'plan' AS plan",
                [_col("name"), _col("plan", kind="json_text", key="plan")],
                "profile->>'plan' = 'pro'",
                {"kind": "json_equals", "key": "plan", "value": "pro"})),
        ("Name and plan, as plan, for everyone on the free plan. By id.",
         _array("name, profile->>'plan' AS plan",
                [_col("name"), _col("plan", kind="json_text", key="plan")],
                "profile->>'plan' = 'free'",
                {"kind": "json_equals", "key": "plan", "value": "free"})),
        ("Name and plan, as plan, for everyone on the team plan. By id.",
         _array("name, profile->>'plan' AS plan",
                [_col("name"), _col("plan", kind="json_text", key="plan")],
                "profile->>'plan' = 'team'",
                {"kind": "json_equals", "key": "plan", "value": "team"})),
        ("Just the names of everyone on the pro plan. By id.",
         _array("name", [_col("name")], "profile->>'plan' = 'pro'",
                {"kind": "json_equals", "key": "plan", "value": "pro"})),
        ("Name and seats, as seats, for everyone who has a seats key. By id.",
         _array("name, profile->>'seats' AS seats",
                [_col("name"), _col("seats", kind="json_text", key="seats")],
                "profile ? 'seats'",
                {"kind": "json_has_key", "key": "seats"})),
        ("Name and seats, as seats, for everyone with no seats key. By id.",
         _array("name, profile->>'seats' AS seats",
                [_col("name"), _col("seats", kind="json_text", key="seats")],
                "NOT (profile ? 'seats')",
                {"kind": "json_missing_key", "key": "seats"})),
        ("Name and the whole profile for everyone on the pro plan. By id.",
         _array("name, profile", [_col("name"), _col("profile")],
                "profile->>'plan' = 'pro'",
                {"kind": "json_equals", "key": "plan", "value": "pro"})),
        ("Name and the whole profile for everyone on the free plan. By id.",
         _array("name, profile", [_col("name"), _col("profile")],
                "profile->>'plan' = 'free'",
                {"kind": "json_equals", "key": "plan", "value": "free"})),
        ("Name and seats, as seats, for everyone with five seats or more. By id.",
         _array("name, profile->>'seats' AS seats",
                [_col("name"), _col("seats", kind="json_text", key="seats")],
                "(profile->>'seats')::int >= 5",
                {"kind": "json_at_least", "key": "seats", "value": 5})),
        ("Name and seats, as seats, for everyone with ten seats or more. By id.",
         _array("name, profile->>'seats' AS seats",
                [_col("name"), _col("seats", kind="json_text", key="seats")],
                "(profile->>'seats')::int >= 10",
                {"kind": "json_at_least", "key": "seats", "value": 10})),
        ("Name and who referred them, as referred_by, for anyone with that key. By id.",
         _array("name, profile->>'referred_by' AS referred_by",
                [_col("name"),
                 _col("referred_by", kind="json_text", key="referred_by")],
                "profile ? 'referred_by'",
                {"kind": "json_has_key", "key": "referred_by"})),
        ("Name, city and plan, as plan, for everyone on the pro plan. By id.",
         _array("name, city, profile->>'plan' AS plan",
                [_col("name"), _col("city"),
                 _col("plan", kind="json_text", key="plan")],
                "profile->>'plan' = 'pro'",
                {"kind": "json_equals", "key": "plan", "value": "pro"})),
        ("Name and plan, as plan, for the pro plan, using containment. By id.",
         _array("name, profile->>'plan' AS plan",
                [_col("name"), _col("plan", kind="json_text", key="plan")],
                """profile @> '{"plan": "pro"}'""",
                {"kind": "json_equals", "key": "plan", "value": "pro"})),
        ("Name and plan, as plan, for the team plan, using containment. By id.",
         _array("name, profile->>'plan' AS plan",
                [_col("name"), _col("plan", kind="json_text", key="plan")],
                """profile @> '{"plan": "team"}'""",
                {"kind": "json_equals", "key": "plan", "value": "team"})),
        ("Name, plan and seats for everyone with a seats key. By id.",
         _array("name, profile->>'plan' AS plan, profile->>'seats' AS seats",
                [_col("name"), _col("plan", kind="json_text", key="plan"),
                 _col("seats", kind="json_text", key="seats")],
                "profile ? 'seats'",
                {"kind": "json_has_key", "key": "seats"})),
        ("Name and age of everyone on the free plan. By id.",
         _array("name, age", [_col("name"), _col("age")],
                "profile->>'plan' = 'free'",
                {"kind": "json_equals", "key": "plan", "value": "free"})),
    ],
)


def _returning(user_id, item, price, headers, returning):
    """One INSERT ... RETURNING exercise.

    There used to be a price_shown argument beside price, for what the
    returned row would print. Two of sixteen call sites passed the item
    name into it and the mistake was invisible on the fourteen where
    price was not among the returned columns. A price prints as a price;
    there was never a second value to supply, only a second chance to
    get one wrong.
    """
    return {
        "user_id": user_id, "item": item, "price": price,
        "headers": headers, "returning": returning,
    }


RETURNING = _page(
    "pg-returning", 6,
    "Getting back what a write just did",
    "RETURNING turns an INSERT into a query. You get the row that was "
    "written, including the id the database chose — which otherwise "
    "takes a second round trip and a guess. It works on UPDATE and "
    "DELETE too.",
    "INSERT INTO orders (user_id, item, price) VALUES (2, 'Cable', 9.99) "
    "RETURNING id, item;",
    "pg_returning",
    [
        ("Add a Cable at 9.99 for user 2. Return id and item.",
         _returning(2, "Cable", "9.99",
                    ["id", "item"], "id, item")),
        ("Add a Stand at 25.00 for user 1. Return id and item.",
         _returning(1, "Stand", "25.00",
                    ["id", "item"], "id, item")),
        ("Add a Hub at 42.50 for user 3. Return id and item.",
         _returning(3, "Hub", "42.50",
                    ["id", "item"], "id, item")),
        ("Add a Dock at 99.00 for user 5. Return id and item.",
         _returning(5, "Dock", "99.00",
                    ["id", "item"], "id, item")),
        ("Add a Cable at 9.99 for user 2. Return just the id.",
         _returning(2, "Cable", "9.99",
                    ["id"], "id")),
        ("Add a Stand at 25.00 for user 1. Return just the id.",
         _returning(1, "Stand", "25.00",
                    ["id"], "id")),
        ("Add a Mat at 15.25 for user 4. Return id, item and price.",
         _returning(4, "Mat", "15.25",
                    ["id", "item", "price"], "id, item, price")),
        ("Add a Lamp at 34.25 for user 2. Return id, item and price.",
         _returning(2, "Lamp", "34.25",
                    ["id", "item", "price"], "id, item, price")),
        ("Add a Chair at 150.00 for user 3. Return id and price.",
         _returning(3, "Chair", "150.00",
                    ["id", "price"], "id, price")),
        ("Add a Riser at 30.00 for user 1. Return id and price.",
         _returning(1, "Riser", "30.00",
                    ["id", "price"], "id, price")),
        ("Add a Pad at 5.00 for user 5. Return id, user_id and item.",
         _returning(5, "Pad", "5.00",
                    ["id", "user_id", "item"], "id, user_id, item")),
        ("Add a Tray at 12.00 for user 4. Return id, user_id and item.",
         _returning(4, "Tray", "12.00",
                    ["id", "user_id", "item"], "id, user_id, item")),
        ("Add a Case at 60.00 for user 2. Return item and price.",
         _returning(2, "Case", "60.00",
                    ["item", "price"], "item, price")),
        ("Add a Strap at 7.75 for user 3. Return item and price.",
         _returning(3, "Strap", "7.75",
                    ["item", "price"], "item, price")),
        ("Add a Cover at 18.40 for user 1. Return id, item and user_id.",
         _returning(1, "Cover", "18.40",
                    ["id", "item", "user_id"], "id, item, user_id")),
        ("Add a Clip at 3.20 for user 5. Return just the item.",
         _returning(5, "Clip", "3.20",
                    ["item"], "item")),
    ],
)


def _window(call, over, label, answers):
    return {"call": call, "over": over, "label": label, "answers": answers}


WINDOW = _page(
    "pg-window", 7,
    "Calculating across rows without collapsing them",
    "GROUP BY gives one row per group and throws the rest away. A "
    "window function does the same arithmetic and keeps every row, so "
    "you can show somebody their number and the total on the same line. "
    "OVER () is what says which rows to look at.",
    "SELECT name, rank() OVER (ORDER BY age DESC) AS r FROM users "
    "ORDER BY id;",
    "pg_window",
    [
        ("Each name with its rank by age, oldest first, as r. By id.",
         _window("rank()", "ORDER BY age DESC", "r", [3, 4, 1, 5, 2])),
        ("Each name with its rank by age, youngest first, as r. By id.",
         _window("rank()", "ORDER BY age", "r", [3, 2, 5, 1, 4])),
        ("Each name with its row number by id, as n. By id.",
         _window("row_number()", "ORDER BY id", "n", [1, 2, 3, 4, 5])),
        ("Each name with its row number by name, as n. By id.",
         _window("row_number()", "ORDER BY name", "n", [1, 2, 3, 4, 5])),
        ("Each name with the total of everyone's ages, as total. By id.",
         _window("sum(age)", "", "total", [147, 147, 147, 147, 147])),
        ("Each name with how many users there are, as everyone. By id.",
         _window("count(*)", "", "everyone", [5, 5, 5, 5, 5])),
        ("Each name with the oldest age of all, as oldest. By id.",
         _window("max(age)", "", "oldest", [41, 41, 41, 41, 41])),
        ("Each name with the youngest age of all, as youngest. By id.",
         _window("min(age)", "", "youngest", [17, 17, 17, 17, 17])),
        ("Each name with the total age of their city, as city_total. By id.",
         _window("sum(age)", "PARTITION BY city", "city_total",
                 [71, 59, 71, 17, 59])),
        ("Each name with how many people share their city, as in_city. By id.",
         _window("count(*)", "PARTITION BY city", "in_city",
                 [2, 2, 2, 1, 2])),
        ("Each name with the oldest age in their city, as city_oldest. By id.",
         _window("max(age)", "PARTITION BY city", "city_oldest",
                 [41, 35, 41, 17, 35])),
        ("Each name with the youngest age in their city, as city_youngest. By id.",
         _window("min(age)", "PARTITION BY city", "city_youngest",
                 [30, 24, 30, 17, 24])),
        ("Each name with its rank by age within its city, oldest first, as r. By id.",
         _window("rank()", "PARTITION BY city ORDER BY age DESC", "r",
                 [2, 2, 1, 1, 1])),
        ("Each name with its row number within its city by id, as n. By id.",
         _window("row_number()", "PARTITION BY city ORDER BY id", "n",
                 [1, 1, 2, 1, 2])),
        ("Each name with how many users there are in their city, by name order, as n. By id.",
         _window("count(*)", "PARTITION BY city", "n", [2, 2, 2, 1, 2])),
        ("Each name with its dense rank by age, oldest first, as r. By id.",
         _window("dense_rank()", "ORDER BY age DESC", "r", [3, 4, 1, 5, 2])),
    ],
)


PG_PAGES: tuple[Page, ...] = (
    CAST, ILIKE, SERIES, ARRAY, JSONB, RETURNING, WINDOW,
)
