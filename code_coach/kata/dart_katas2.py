"""More katas in Dart: the second pass over what sits behind a screen.

The first set was about lists and maps in general. These lean further
into the shapes a Flutter app meets every day: a page of results, a
label for an avatar, a status turned into words by a `switch`
expression, a form field checked with a RegExp, a grid cut into rows,
a set of selected ids compared before and after, a `copyWith` that
keeps what was not changed, and a decoded JSON map that has to be cast,
piece by piece, into something a widget can show.

The rules are the same as in dart_katas.py. The oracle is Python, the
worked answer is Dart and is compiled and run against it, every
parameter and the result are typed, and nothing may modify what it was
handed.

`Map<String, dynamic>` is what jsonDecode gives back, and it is new
here. Every value in it is dynamic, so the compiler will let anything
through - which is why the answers read them with `as` and a `?` and a
`??`, saying at each step what type is expected and what to do when it
is missing.
"""

from __future__ import annotations

import re

from code_coach.kata import Kata

FAMILY = "Dart"

# ── Small shapes ─────────────────────────────────────────────


def _initials_of(full_name: str) -> str:
    words = full_name.split()
    if not words:
        return ""
    if len(words) == 1:
        return words[0][0].upper()
    return (words[0][0] + words[-1][0]).upper()


def _status_label(status: str) -> str:
    return {
        "loading": "Loading...",
        "done": "Done",
        "empty": "Nothing here yet",
        "error": "Something went wrong",
    }.get(status.strip().lower(), "Unknown")


def _page_of(items: list, page: int, per_page: int) -> list:
    start = (page - 1) * per_page
    return items[start:start + per_page]


def _drop_repeats(values: list) -> list:
    out: list = []
    for value in values:
        if not out or out[-1] != value:
            out.append(value)
    return out


SMALL: tuple[Kata, ...] = (
    Kata(
        id="dart-initials-of",
        level=1,
        language="dart",
        name="initialsOf",
        brief=(
            "Make the initials for an avatar from a full name: the first "
            "letter of the first word and of the last word, in capitals. "
            "One word gives one letter, and a name that is empty or only "
            "spaces gives an empty string. Words may be separated by more "
            "than one space."
        ),
        params=("fullName",),
        types=("String",),
        returns="String",
        family=FAMILY,
        example="initialsOf('ada  king lovelace') is 'AL'",
        hint=(
            "split(' ') on 'a  b' gives an empty string between the two "
            "spaces. Split on RegExp(r'\\s+') after trim(), or drop the "
            "empty pieces with where. Then first and last are properties "
            "of the list, and one word is both of them."
        ),
        cases=(
            ("ada  king lovelace",), ("",), ("   ",), ("cher",),
            ("Grace Hopper",), (" alan turing ",), ("x y",),
            ("mary ann evans",), ("bob",), ("jean-luc picard",),
        ),
        solve=_initials_of,
        checks=(
            (("ada  king lovelace",), "AL"),
            (("",), ""),
            (("   ",), ""),
            (("cher",), "C"),
            ((" alan turing ",), "AT"),
        ),
        dart_answer=(
            "String initialsOf(String fullName) {\n"
            "  final trimmed = fullName.trim();\n"
            "  if (trimmed.isEmpty) return '';\n"
            "  final words = trimmed.split(RegExp(r'\\s+'));\n"
            "  if (words.length == 1) return words.first[0].toUpperCase();\n"
            "  return (words.first[0] + words.last[0]).toUpperCase();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-status-label",
        level=2,
        language="dart",
        name="statusLabel",
        brief=(
            "Turn a status from the server into the words a screen shows. "
            "'loading' is 'Loading...', 'done' is 'Done', 'empty' is "
            "'Nothing here yet' and 'error' is 'Something went wrong'. "
            "Ignore case and surrounding spaces. Anything else is 'Unknown'."
        ),
        params=("status",),
        types=("String",),
        returns="String",
        family=FAMILY,
        example="statusLabel(' Done ') is 'Done'",
        hint=(
            "A switch expression is a value, so it can be returned "
            "directly: return switch (x) { 'a' => ..., _ => ... }; with "
            "_ catching everything else. Tidy the string before you "
            "switch on it, not in every branch."
        ),
        cases=(
            ("loading",), ("done",), ("empty",), ("error",), ("",),
            (" Done ",), ("ERROR",), ("pending",), ("load",), ("Empty",),
        ),
        solve=_status_label,
        checks=(
            (("loading",), "Loading..."),
            (("",), "Unknown"),
            ((" Done ",), "Done"),
            (("ERROR",), "Something went wrong"),
            (("load",), "Unknown"),
        ),
        dart_answer=(
            "String statusLabel(String status) {\n"
            "  return switch (status.trim().toLowerCase()) {\n"
            "    'loading' => 'Loading...',\n"
            "    'done' => 'Done',\n"
            "    'empty' => 'Nothing here yet',\n"
            "    'error' => 'Something went wrong',\n"
            "    _ => 'Unknown',\n"
            "  };\n"
            "}"
        ),
    ),
    Kata(
        id="dart-page-of",
        level=2,
        language="dart",
        name="pageOf",
        brief=(
            "Return one page of a list, the way an infinite scroll asks for "
            "the next batch. Pages are numbered from 1 and hold perPage "
            "items each. The last page may be short, and a page past the "
            "end is empty."
        ),
        params=("items", "page", "perPage"),
        types=("List<String>", "int", "int"),
        returns="List<String>",
        family=FAMILY,
        example="pageOf(['a', 'b', 'c', 'd', 'e'], 2, 2) is ['c', 'd']",
        hint=(
            "skip() and take() never go out of range: skipping past the "
            "end gives nothing, and taking more than is left takes what "
            "is left. sublist() would throw on both. Page 1 skips none."
        ),
        cases=(
            (["a", "b", "c", "d", "e"], 2, 2), ([], 1, 10),
            (["a", "b", "c", "d", "e"], 3, 2), (["a", "b", "c"], 5, 2),
            (["only"], 1, 1), (["a", "b", "c"], 1, 10),
            (["a", "b", "c", "d"], 2, 3), (["a", "b"], 2, 1),
            (["x", "y", "z"], 1, 2), (["a", "b", "c", "d", "e", "f"], 2, 3),
        ),
        solve=_page_of,
        checks=(
            ((["a", "b", "c", "d", "e"], 2, 2), ["c", "d"]),
            (([], 1, 10), []),
            # The last page is short rather than an error.
            ((["a", "b", "c", "d", "e"], 3, 2), ["e"]),
            ((["a", "b", "c"], 5, 2), []),
            ((["a", "b", "c"], 1, 10), ["a", "b", "c"]),
        ),
        dart_answer=(
            "List<String> pageOf(List<String> items, int page, int perPage) {\n"
            "  return items.skip((page - 1) * perPage).take(perPage).toList();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-drop-repeats",
        level=2,
        language="dart",
        name="dropRepeats",
        brief=(
            "A sensor reports the same reading many times in a row, and "
            "the screen should only redraw when it changes. Drop each value "
            "that equals the one just before it. A value that comes back "
            "later, after a different one, is kept."
        ),
        params=("values",),
        types=("List<int>",),
        returns="List<int>",
        family=FAMILY,
        example="dropRepeats([1, 1, 2, 2, 2, 1]) is [1, 2, 1]",
        hint=(
            "This is not toSet(): a set would lose the second 1. Compare "
            "each value with the last one you kept - result.last - and "
            "remember that an empty list has no last."
        ),
        cases=(
            ([1, 1, 2, 2, 2, 1],), ([],), ([7],), ([3, 3, 3],),
            ([1, 2, 3],), ([-1, -1, 0, -1],), ([5, 5, 6, 6, 5, 5],),
            ([0, 0],), ([2, 1, 2, 1],), ([4, 4, 4, 9],),
        ),
        solve=_drop_repeats,
        checks=(
            (([1, 1, 2, 2, 2, 1],), [1, 2, 1]),
            (([],), []),
            (([3, 3, 3],), [3]),
            (([-1, -1, 0, -1],), [-1, 0, -1]),
            (([2, 1, 2, 1],), [2, 1, 2, 1]),
        ),
        dart_answer=(
            "List<int> dropRepeats(List<int> values) {\n"
            "  final kept = <int>[];\n"
            "  for (final value in values) {\n"
            "    if (kept.isEmpty || kept.last != value) kept.add(value);\n"
            "  }\n"
            "  return kept;\n"
            "}"
        ),
    ),
)

# ── Shaping ──────────────────────────────────────────────────


def _running_total(amounts: list) -> list:
    out: list = []
    total = 0
    for amount in amounts:
        total += amount
        out.append(total)
    return out


_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _looks_like_email(text: str) -> bool:
    return _EMAIL.fullmatch(text.strip()) is not None


def _in_rows(items: list, per_row: int) -> list:
    return [items[i:i + per_row] for i in range(0, len(items), per_row)]


SHAPING: tuple[Kata, ...] = (
    Kata(
        id="dart-running-total",
        level=3,
        language="dart",
        name="runningTotal",
        brief=(
            "Given the amounts on a statement, oldest first, return the "
            "balance after each one, starting from zero - the numbers down "
            "the right-hand side of a bank app."
        ),
        params=("amounts",),
        types=("List<int>",),
        returns="List<int>",
        family=FAMILY,
        example="runningTotal([10, -3, 5]) is [10, 7, 12]",
        hint=(
            "fold carries one value through the whole list, and that value "
            "can be the list you are building. Give the start a type - "
            "<int>[] - or Dart cannot tell what the list holds. Inside, "
            "the last balance is the list's last, or 0 when it is empty."
        ),
        cases=(
            ([10, -3, 5],), ([],), ([4],), ([-2],), ([1, 1, 1, 1],),
            ([5, -5, 5, -5],), ([100, -30, -80],), ([0, 0, 3],),
            ([2, 4, 8, 16],), ([-1, -2, -3],),
        ),
        solve=_running_total,
        checks=(
            (([10, -3, 5],), [10, 7, 12]),
            (([],), []),
            (([-2],), [-2]),
            (([5, -5, 5, -5],), [5, 0, 5, 0]),
            # The balance can go below zero; nothing stops it.
            (([100, -30, -80],), [100, 70, -10]),
        ),
        dart_answer=(
            "List<int> runningTotal(List<int> amounts) {\n"
            "  return amounts.fold(<int>[], (totals, amount) {\n"
            "    final before = totals.isEmpty ? 0 : totals.last;\n"
            "    return totals..add(before + amount);\n"
            "  });\n"
            "}"
        ),
    ),
    Kata(
        id="dart-looks-like-email",
        level=3,
        language="dart",
        name="looksLikeEmail",
        brief=(
            "Decide whether a form field looks enough like an email address "
            "to enable the Sign up button. Ignore spaces around it. Then it "
            "must be: some characters, one @, some characters, a dot, some "
            "characters - where none of those characters is an @ or a space."
        ),
        params=("text",),
        types=("String",),
        returns="bool",
        family=FAMILY,
        example="looksLikeEmail(' ada@example.com ') is true",
        hint=(
            "[^@\\s] is one character that is neither an @ nor a space, and "
            "+ makes it one or more. Anchor the pattern with ^ and $, or "
            "hasMatch is happy to find an address hiding in the middle of "
            "rubbish. Use a raw string, r'...', so the backslash survives."
        ),
        cases=(
            (" ada@example.com ",), ("",), ("@",), ("ada@example",),
            ("ada@@example.com",), ("a@b.c",), ("ada lovelace@example.com",),
            ("ada@mail.example.co.uk",), ("@example.com",), ("ada@.com",),
        ),
        solve=_looks_like_email,
        checks=(
            ((" ada@example.com ",), True),
            (("",), False),
            (("ada@example",), False),
            (("ada@@example.com",), False),
            (("ada lovelace@example.com",), False),
            # More than one dot after the @ is fine: the last one counts.
            (("ada@mail.example.co.uk",), True),
        ),
        dart_answer=(
            "bool looksLikeEmail(String text) {\n"
            "  final pattern = RegExp(r'^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$');\n"
            "  return pattern.hasMatch(text.trim());\n"
            "}"
        ),
    ),
    Kata(
        id="dart-in-rows",
        level=3,
        language="dart",
        name="inRows",
        brief=(
            "Cut a list of photo ids into rows of perRow for a grid. Every "
            "row is full except perhaps the last, which holds what is left. "
            "No photos means no rows."
        ),
        params=("items", "perRow"),
        types=("List<int>", "int"),
        returns="List<List<int>>",
        family=FAMILY,
        example="inRows([1, 2, 3, 4, 5], 2) is [[1, 2], [3, 4], [5]]",
        hint=(
            "Step i by perRow: for (var i = 0; i < items.length; i += perRow). "
            "sublist(i, end) throws if end is past the list, so the end is "
            "the smaller of i + perRow and the length - min() from "
            "dart:math, or a comparison of your own."
        ),
        cases=(
            ([1, 2, 3, 4, 5], 2), ([], 3), ([9], 4), ([1, 2, 3], 1),
            ([1, 2, 3, 4], 2), ([1, 2, 3], 3), ([1, 2, 3, 4, 5, 6, 7], 3),
            ([-1, -2], 5), ([4, 5, 6, 7], 3), ([8, 9], 1),
        ),
        solve=_in_rows,
        checks=(
            (([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]),
            (([], 3), []),
            (([9], 4), [[9]]),
            (([1, 2, 3], 1), [[1], [2], [3]]),
            (([1, 2, 3], 3), [[1, 2, 3]]),
        ),
        dart_answer=(
            "List<List<int>> inRows(List<int> items, int perRow) {\n"
            "  final rows = <List<int>>[];\n"
            "  for (var i = 0; i < items.length; i += perRow) {\n"
            "    final end = i + perRow < items.length ? i + perRow : items.length;\n"
            "    rows.add(items.sublist(i, end));\n"
            "  }\n"
            "  return rows;\n"
            "}"
        ),
    ),
)

# ── State and JSON ───────────────────────────────────────────


def _with_changes(current: dict, changes: dict) -> dict:
    merged = dict(current)
    for key, value in changes.items():
        if value is not None:
            merged[key] = value
    return merged


def _selection_diff(before: list, after: list) -> dict:
    was, now = set(before), set(after)
    return {"added": sorted(now - was), "removed": sorted(was - now)}


def _user_summary(json: dict) -> str:
    profile = json.get("profile") or {}
    name = (profile.get("name") or "").strip() or "Anonymous"
    age = profile.get("age")
    tags = json.get("tags") or []
    label = name if age is None else f"{name} ({age})"
    noun = "tag" if len(tags) == 1 else "tags"
    return f"{label}, {len(tags)} {noun}"


STATE: tuple[Kata, ...] = (
    Kata(
        id="dart-with-changes",
        level=4,
        language="dart",
        name="withChanges",
        brief=(
            "Merge an edit into the current settings the way copyWith "
            "does: every key in changes replaces the current value, keys "
            "not mentioned keep theirs, and a change whose value is null "
            "means 'leave it alone', not 'clear it'. Return a new map; "
            "neither map you were given may change."
        ),
        params=("current", "changes"),
        types=("Map<String, dynamic>", "Map<String, dynamic>"),
        returns="Map<String, dynamic>",
        family=FAMILY,
        example=(
            "withChanges({'theme': 'dark', 'size': 14}, "
            "{'size': 16, 'theme': null}) is {'theme': 'dark', 'size': 16}"
        ),
        hint=(
            "A map literal can spread one map and then add entries with a "
            "collection for and a collection if: {...current, for (final e "
            "in changes.entries) if (e.value != null) e.key: e.value}. "
            "Later keys win, and the originals are only read."
        ),
        cases=(
            ({"theme": "dark", "size": 14}, {"size": 16, "theme": None}),
            ({}, {}),
            ({"a": 1}, {}),
            ({}, {"lang": "en"}),
            ({"a": 1}, {"a": None}),
            ({"name": "Ada", "age": 36}, {"age": 37}),
            ({"x": 1, "y": 2}, {"z": 3, "x": None}),
            ({"volume": 5}, {"volume": 0}),
            ({"mode": "list"}, {"mode": "grid", "sort": "name"}),
            ({"k": "v"}, {"k": ""}),
        ),
        solve=_with_changes,
        checks=(
            (({"theme": "dark", "size": 14}, {"size": 16, "theme": None}),
             {"theme": "dark", "size": 16}),
            (({}, {}), {}),
            (({"a": 1}, {"a": None}), {"a": 1}),
            # Zero and the empty string are values, not "no change".
            (({"volume": 5}, {"volume": 0}), {"volume": 0}),
            (({"k": "v"}, {"k": ""}), {"k": ""}),
            (({"mode": "list"}, {"mode": "grid", "sort": "name"}),
             {"mode": "grid", "sort": "name"}),
        ),
        dart_answer=(
            "Map<String, dynamic> withChanges(\n"
            "    Map<String, dynamic> current, Map<String, dynamic> changes) {\n"
            "  return {\n"
            "    ...current,\n"
            "    for (final e in changes.entries)\n"
            "      if (e.value != null) e.key: e.value,\n"
            "  };\n"
            "}"
        ),
    ),
    Kata(
        id="dart-selection-diff",
        level=4,
        language="dart",
        name="selectionDiff",
        brief=(
            "A list screen lets the user tick items, and on Save the app "
            "sends only what changed. Given the ids ticked before and the "
            "ids ticked now, return {'added': [...], 'removed': [...]}, "
            "each sorted smallest first with no id twice. Either list may "
            "hold repeats."
        ),
        params=("before", "after"),
        types=("List<int>", "List<int>"),
        returns="Map<String, List<int>>",
        family=FAMILY,
        example=(
            "selectionDiff([1, 2, 3], [2, 3, 4]) is "
            "{'added': [4], 'removed': [1]}"
        ),
        hint=(
            "toSet() drops the repeats, and a Set has difference(): "
            "now.difference(was) is what is in now and not in was. A set "
            "has no order, so turn it into a list and sort that - "
            "..sort() on the new list hands the list back."
        ),
        cases=(
            ([1, 2, 3], [2, 3, 4]), ([], []), ([5], []), ([], [5]),
            ([1, 2], [1, 2]), ([3, 1, 3], [1, 1]), ([9, 2], [7, 2, 4]),
            ([10, 20], [30, 40]), ([4, 4, 4], [4]), ([6, 5], [5, 8, 7]),
        ),
        solve=_selection_diff,
        checks=(
            (([1, 2, 3], [2, 3, 4]), {"added": [4], "removed": [1]}),
            (([], []), {"added": [], "removed": []}),
            (([1, 2], [1, 2]), {"added": [], "removed": []}),
            (([3, 1, 3], [1, 1]), {"added": [], "removed": [3]}),
            (([9, 2], [7, 2, 4]), {"added": [4, 7], "removed": [9]}),
        ),
        dart_answer=(
            "Map<String, List<int>> selectionDiff(List<int> before, List<int> after) {\n"
            "  final was = before.toSet();\n"
            "  final now = after.toSet();\n"
            "  return {\n"
            "    'added': now.difference(was).toList()..sort(),\n"
            "    'removed': was.difference(now).toList()..sort(),\n"
            "  };\n"
            "}"
        ),
    ),
    Kata(
        id="dart-user-summary",
        level=5,
        language="dart",
        name="userSummary",
        brief=(
            "An API sends a user as decoded JSON: a 'profile' map holding "
            "a 'name' and an 'age', and a 'tags' list. Any of them may be "
            "missing or null. Return a line for a list tile: the name (or "
            "'Anonymous' when it is missing or blank), then the age in "
            "brackets only when there is one, then ', ' and the number of "
            "tags - '1 tag', otherwise 'N tags'."
        ),
        params=("json",),
        types=("Map<String, dynamic>",),
        returns="String",
        family=FAMILY,
        example=(
            "userSummary({'profile': {'name': 'Ada', 'age': 36}, "
            "'tags': ['math', 'code']}) is 'Ada (36), 2 tags'"
        ),
        hint=(
            "Each read says what it expects: json['profile'] as Map? gives "
            "a map or null, and ?? const {} turns null into an empty one. "
            "Then profile['name'] as String?, profile['age'] as int?, "
            "json['tags'] as List?. The casts are checked when the code "
            "runs, so they are the place a wrong guess about the JSON shows."
        ),
        cases=(
            ({"profile": {"name": "Ada", "age": 36}, "tags": ["math", "code"]},),
            ({},),
            ({"profile": None, "tags": None},),
            ({"profile": {"name": "  "}, "tags": ["x"]},),
            ({"profile": {"name": "Linus"}},),
            ({"tags": []},),
            ({"profile": {"age": 0}, "tags": ["a", "b", "c"]},),
            ({"profile": {"name": " Grace ", "age": None}, "tags": ["navy"]},),
            ({"profile": {"name": "Bo", "age": 7}, "tags": []},),
            ({"profile": {"name": None, "age": 50}},),
        ),
        solve=_user_summary,
        checks=(
            (({"profile": {"name": "Ada", "age": 36},
               "tags": ["math", "code"]},), "Ada (36), 2 tags"),
            (({},), "Anonymous, 0 tags"),
            (({"profile": {"name": "  "}, "tags": ["x"]},), "Anonymous, 1 tag"),
            # An age of 0 is still an age - only a missing one is left out.
            (({"profile": {"age": 0}, "tags": ["a", "b", "c"]},),
             "Anonymous (0), 3 tags"),
            (({"profile": {"name": " Grace ", "age": None},
               "tags": ["navy"]},), "Grace, 1 tag"),
        ),
        dart_answer=(
            "String userSummary(Map<String, dynamic> json) {\n"
            "  final profile = json['profile'] as Map? ?? const {};\n"
            "  final name = (profile['name'] as String? ?? '').trim();\n"
            "  final age = profile['age'] as int?;\n"
            "  final tags = json['tags'] as List? ?? const [];\n"
            "  final shown = name.isEmpty ? 'Anonymous' : name;\n"
            "  final label = age == null ? shown : '$shown ($age)';\n"
            "  final noun = tags.length == 1 ? 'tag' : 'tags';\n"
            "  return '$label, ${tags.length} $noun';\n"
            "}"
        ),
    ),
)

DART_KATAS_2: tuple[Kata, ...] = SMALL + SHAPING + STATE
