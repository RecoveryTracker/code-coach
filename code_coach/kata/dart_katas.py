"""Katas in Dart: the small functions a Flutter app is actually made of.

Chosen against the code that sits behind a screen rather than against a
list of famous problems. A widget shows data, and most of the Dart
around it turns one shape of data into another: filtering a list,
counting things into a map, grouping names under a header, making a
label out of a number, checking a form before the button is enabled.
None of it is hard, and all of it has a Dart way of being written that
reads better than the way you would bring over from another language.

The oracle is still Python, as for every kata. The answers are numbers,
strings, lists, maps and booleans, which mean the same in both, so one
implementation of the truth is guarded by the same hand-written checks
as everything else. What is Dart is the worked answer, which the suite
compiles and runs against that oracle through the same driver a
student's code goes through.

Two things are new because Dart is typed. Each kata declares the Dart
type of every parameter and of the result, and the driver converts the
JSON inputs into exactly those types before the call - so the function
really is handed a List<String>, and has to give back what its
signature promises. And null safety is part of the lesson rather than a
nuisance: looking up a key in a Map gives a value that might be null,
and several of these are about saying, in the code, what should happen
when it is.

The rule about arguments carries over unchanged. Nothing here may modify
what it was handed. In Dart that bites on `sort`, which works in place
and returns nothing, so the list has to be copied first.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Dart"

# ── Lists and maps ───────────────────────────────────────────


def _words_at_least(words: list, min_length: int) -> list:
    return [word for word in words if len(word) >= min_length]


def _form_complete(fields: dict, needed: list) -> bool:
    return all((fields.get(key) or "").strip() != "" for key in needed)


def _tally_votes(votes: list) -> dict:
    counts: dict = {}
    for vote in votes:
        name = vote.strip().lower()
        if name:
            counts[name] = counts.get(name, 0) + 1
    return counts


COLLECTIONS: tuple[Kata, ...] = (
    Kata(
        id="dart-words-at-least",
        level=1,
        language="dart",
        name="wordsAtLeast",
        brief=(
            "Return the words that are at least minLength characters "
            "long, in the order they came. The list you were given must "
            "not change."
        ),
        params=("words", "minLength"),
        types=("List<String>", "int"),
        returns="List<String>",
        family=FAMILY,
        example="wordsAtLeast(['hi', 'hello', 'hey'], 3) is ['hello', 'hey']",
        hint=(
            "where() keeps the ones that pass, but it hands back a lazy "
            "Iterable rather than a List. The return type says "
            "List<String>, so something has to turn one into the other."
        ),
        cases=(
            (["hi", "hello", "hey"], 3), ([], 3), (["a"], 1), (["a"], 2),
            (["one", "three", "five"], 0), (["", "x", ""], 1),
            (["flutter", "dart", "widget"], 5), (["same", "size", "four"], 4),
            (["tiny"], 10), (["ab", "abc", "abcd"], 3),
        ),
        solve=_words_at_least,
        checks=(
            ((["hi", "hello", "hey"], 3), ["hello", "hey"]),
            (([], 3), []),
            ((["a"], 2), []),
            ((["", "x", ""], 1), ["x"]),
            ((["flutter", "dart", "widget"], 5), ["flutter", "widget"]),
        ),
        dart_answer=(
            "List<String> wordsAtLeast(List<String> words, int minLength) {\n"
            "  return words.where((word) => word.length >= minLength).toList();\n"
            "}"
        ),
    ),
    Kata(
        id="dart-form-complete",
        level=2,
        language="dart",
        name="formComplete",
        brief=(
            "Say whether every needed field of a form has been filled in. "
            "A field is filled when it is in the map and holds something "
            "other than spaces. Fields that are not needed do not matter."
        ),
        params=("fields", "needed"),
        types=("Map<String, String>", "List<String>"),
        returns="bool",
        family=FAMILY,
        example=(
            "formComplete({'name': 'Ada', 'email': ''}, ['name', 'email']) "
            "is false"
        ),
        hint=(
            "fields[key] is a String? - a key that is not there gives null, "
            "not an empty string - and null has no trim(). `??` swaps the "
            "null for something that has. And every() on an empty list is "
            "true, which is right here: nothing needed, nothing missing."
        ),
        cases=(
            ({"name": "Ada", "email": ""}, ["name", "email"]),
            ({"name": "Ada", "email": "ada@example.com"}, ["name", "email"]),
            ({}, []),
            ({}, ["name"]),
            ({"name": "   "}, ["name"]),
            ({"name": "Ada"}, ["name", "phone"]),
            ({"name": "Ada", "phone": ""}, ["name"]),
            ({"a": "1"}, []),
            ({"city": " Leeds "}, ["city"]),
            ({"x": "y", "z": "w"}, ["z"]),
        ),
        solve=_form_complete,
        checks=(
            (({"name": "Ada", "email": ""}, ["name", "email"]), False),
            (({"name": "Ada", "email": "ada@example.com"}, ["name", "email"]),
             True),
            (({}, []), True),
            # Only spaces is not filled in, however it looks on screen.
            (({"name": "   "}, ["name"]), False),
            # The empty phone is not needed, so it does not count against.
            (({"name": "Ada", "phone": ""}, ["name"]), True),
        ),
        dart_answer=(
            "bool formComplete(Map<String, String> fields, List<String> needed) {\n"
            "  return needed.every((key) => (fields[key] ?? '').trim().isNotEmpty);\n"
            "}"
        ),
    ),
    Kata(
        id="dart-tally-votes",
        level=2,
        language="dart",
        name="tallyVotes",
        brief=(
            "Count the votes for each name. Case and the spaces around a "
            "name do not matter - ' Ada' and 'ada' are both a vote for "
            "'ada' - and a vote that is blank once trimmed is not counted "
            "at all. The keys are the tidied names."
        ),
        params=("votes",),
        types=("List<String>",),
        returns="Map<String, int>",
        family=FAMILY,
        example="tallyVotes(['Ada', ' ada', 'Bob']) is {'ada': 2, 'bob': 1}",
        hint=(
            "Tidy each vote before counting it, and skip the blank ones "
            "before they reach the map. update() with ifAbsent adds a key "
            "the first time and changes it every time after, in one call."
        ),
        cases=(
            (["Ada", " ada", "Bob"],), ([],), (["x"],), (["", "  "],),
            (["ADA", "Ada", "ada"],), (["bob ", "", "Bob"],),
            (["a", "b", "c"],),
            (["Linus", "Grace", "linus", " GRACE ", "linus"],),
            (["  "],), (["Zed", "amy"],),
        ),
        solve=_tally_votes,
        checks=(
            ((["Ada", " ada", "Bob"],), {"ada": 2, "bob": 1}),
            (([],), {}),
            ((["", "  "],), {}),
            ((["bob ", "", "Bob"],), {"bob": 2}),
            ((["Linus", "Grace", "linus", " GRACE ", "linus"],),
             {"linus": 3, "grace": 2}),
        ),
        dart_answer=(
            "Map<String, int> tallyVotes(List<String> votes) {\n"
            "  final counts = <String, int>{};\n"
            "  for (final vote in votes) {\n"
            "    final name = vote.trim().toLowerCase();\n"
            "    if (name.isEmpty) continue;\n"
            "    counts.update(name, (n) => n + 1, ifAbsent: () => 1);\n"
            "  }\n"
            "  return counts;\n"
            "}"
        ),
    ),
)


# ── Labels, order and groups ─────────────────────────────────


def _track_time(seconds: int) -> str:
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _shortest_first(words: list) -> list:
    return sorted(words, key=lambda word: (len(word), word))


def _group_by_initial(names: list) -> dict:
    groups: dict = {}
    for name in names:
        if name:
            groups.setdefault(name[0].upper(), []).append(name)
    return groups


SHAPING: tuple[Kata, ...] = (
    Kata(
        id="dart-track-time",
        level=3,
        language="dart",
        name="trackTime",
        brief=(
            "Turn a number of seconds into the label a media player shows: "
            "m:ss under an hour, h:mm:ss from an hour up. The first number "
            "is never padded; the ones after it always have two digits."
        ),
        params=("seconds",),
        types=("int",),
        returns="String",
        family=FAMILY,
        example="trackTime(75) is '1:15', and trackTime(3661) is '1:01:01'",
        hint=(
            "~/ is whole-number division and % is what is left over: "
            "3661 ~/ 3600 is one hour, and 3661 % 3600 is the 61 seconds "
            "still to share out. padLeft(2, '0') turns '5' into '05'."
        ),
        cases=(
            (0,), (1,), (59,), (60,), (75,), (599,), (3599,), (3600,),
            (3661,), (45296,),
        ),
        solve=_track_time,
        checks=(
            ((0,), "0:00"),
            ((75,), "1:15"),
            ((3599,), "59:59"),
            # The first second of the second hour, where the shape changes.
            ((3600,), "1:00:00"),
            ((45296,), "12:34:56"),
        ),
        dart_answer=(
            "String trackTime(int seconds) {\n"
            "  final hours = seconds ~/ 3600;\n"
            "  final minutes = (seconds % 3600) ~/ 60;\n"
            "  final secs = (seconds % 60).toString().padLeft(2, '0');\n"
            "  if (hours == 0) return '$minutes:$secs';\n"
            "  return '$hours:${minutes.toString().padLeft(2, '0')}:$secs';\n"
            "}"
        ),
    ),
    Kata(
        id="dart-shortest-first",
        level=3,
        language="dart",
        name="shortestFirst",
        brief=(
            "Return a new list of the words, shortest first, with words of "
            "the same length in alphabetical order. The list you were "
            "given must not change."
        ),
        params=("words",),
        types=("List<String>",),
        returns="List<String>",
        family=FAMILY,
        example=(
            "shortestFirst(['pear', 'fig', 'apple', 'kiwi']) is "
            "['fig', 'kiwi', 'pear', 'apple']"
        ),
        hint=(
            "sort() works in place and returns void, so copy first - "
            "[...words]..sort(...) does both, because the two dots hand "
            "back the list rather than what sort returned. The comparator "
            "wants a negative, zero or positive int, which is exactly what "
            "compareTo gives for both lengths and strings."
        ),
        cases=(
            (["pear", "fig", "apple", "kiwi"],), ([],), (["solo"],),
            (["bb", "a", "ccc"],), (["dog", "cat", "ant"],),
            (["zz", "a", "yy", "b"],), (["same", "same"],),
            (["", "x", ""],), (["widget", "row", "column", "text"],),
            (["cc", "b", "aa"],),
        ),
        solve=_shortest_first,
        checks=(
            ((["pear", "fig", "apple", "kiwi"],),
             ["fig", "kiwi", "pear", "apple"]),
            (([],), []),
            ((["zz", "a", "yy", "b"],), ["a", "b", "yy", "zz"]),
            ((["", "x", ""],), ["", "", "x"]),
            ((["widget", "row", "column", "text"],),
             ["row", "text", "column", "widget"]),
        ),
        dart_answer=(
            "List<String> shortestFirst(List<String> words) {\n"
            "  return [...words]..sort((a, b) {\n"
            "    final byLength = a.length.compareTo(b.length);\n"
            "    return byLength != 0 ? byLength : a.compareTo(b);\n"
            "  });\n"
            "}"
        ),
    ),
    Kata(
        id="dart-group-by-initial",
        level=3,
        language="dart",
        name="groupByInitial",
        brief=(
            "Group the names under their first letter in capitals, the way "
            "a contacts list has a header for each letter. Each group keeps "
            "its names as they were written and in the order they came. An "
            "empty name has no first letter and is left out."
        ),
        params=("names",),
        types=("List<String>",),
        returns="Map<String, List<String>>",
        family=FAMILY,
        example=(
            "groupByInitial(['ada', 'Bob', 'alan']) is "
            "{'A': ['ada', 'alan'], 'B': ['Bob']}"
        ),
        hint=(
            "putIfAbsent(key, () => []) returns the list already under that "
            "key, or puts an empty one there and returns that. Either way "
            "you can add() to what comes back, and there is no if."
        ),
        cases=(
            (["ada", "Bob", "alan"],), ([],), (["zoe"],), ([""],),
            (["Ann", "ann", "ANN"],), (["", "bea", ""],),
            (["cy", "di", "cal", "dot"],), (["a", "b", "c"],),
            (["Max", "mia", "Leo", "liv", "max"],),
            (["1st", "2nd", "1up"],),
        ),
        solve=_group_by_initial,
        checks=(
            ((["ada", "Bob", "alan"],), {"A": ["ada", "alan"], "B": ["Bob"]}),
            (([],), {}),
            (([""],), {}),
            ((["cy", "di", "cal", "dot"],),
             {"C": ["cy", "cal"], "D": ["di", "dot"]}),
            ((["Max", "mia", "Leo", "liv", "max"],),
             {"M": ["Max", "mia", "max"], "L": ["Leo", "liv"]}),
        ),
        dart_answer=(
            "Map<String, List<String>> groupByInitial(List<String> names) {\n"
            "  final groups = <String, List<String>>{};\n"
            "  for (final name in names) {\n"
            "    if (name.isEmpty) continue;\n"
            "    groups.putIfAbsent(name[0].toUpperCase(), () => []).add(name);\n"
            "  }\n"
            "  return groups;\n"
            "}"
        ),
    ),
)


# ── Putting them together ────────────────────────────────────


def _cart_summary(items: list) -> list:
    count = 0
    total = 0
    for item in items:
        qty = item.get("qty", 1)
        count += qty
        total += item["price"] * qty
    return [count, total]


def _top_tags(tags: list, n: int) -> list:
    counts: dict = {}
    for tag in tags:
        counts[tag] = counts.get(tag, 0) + 1
    ranked = sorted(counts, key=lambda tag: (-counts[tag], tag))
    return ranked[:n]


COMBINED: tuple[Kata, ...] = (
    Kata(
        id="dart-cart-summary",
        level=4,
        language="dart",
        name="cartSummary",
        brief=(
            "Each item in a cart is a map with a 'price' in cents and, "
            "sometimes, a 'qty'. An item with no 'qty' is one of that "
            "thing. Return [how many things, total in cents] - the two "
            "numbers a cart badge and a checkout button need."
        ),
        params=("items",),
        types=("List<Map<String, int>>",),
        returns="List<int>",
        family=FAMILY,
        example=(
            "cartSummary([{'price': 250, 'qty': 2}, {'price': 100}]) "
            "is [3, 600]"
        ),
        hint=(
            "item['qty'] is an int? because it might not be there, so it "
            "needs ?? before you can multiply by it. The price is always "
            "there, which is what ! is for: it tells the compiler so, and "
            "throws if you were wrong. A record like (int, int) would be "
            "the natural Dart shape for the answer, but JSON has no "
            "records, so the pair comes back as a list."
        ),
        cases=(
            ([{"price": 250, "qty": 2}, {"price": 100}],),
            ([],),
            ([{"price": 999}],),
            ([{"price": 500, "qty": 0}],),
            ([{"price": 0, "qty": 3}],),
            ([{"price": 150, "qty": 4}, {"price": 75, "qty": 2}],),
            ([{"price": 100}, {"price": 100}, {"price": 100}],),
            ([{"price": 1200, "qty": 1}, {"price": 350}],),
            ([{"price": 99, "qty": 10}],),
        ),
        solve=_cart_summary,
        checks=(
            (([{"price": 250, "qty": 2}, {"price": 100}],), [3, 600]),
            (([],), [0, 0]),
            # A qty of nought is there and is nought - not a missing one.
            (([{"price": 500, "qty": 0}],), [0, 0]),
            (([{"price": 150, "qty": 4}, {"price": 75, "qty": 2}],), [6, 750]),
            (([{"price": 1200, "qty": 1}, {"price": 350}],), [2, 1550]),
        ),
        dart_answer=(
            "List<int> cartSummary(List<Map<String, int>> items) {\n"
            "  var count = 0;\n"
            "  var total = 0;\n"
            "  for (final item in items) {\n"
            "    final qty = item['qty'] ?? 1;\n"
            "    count += qty;\n"
            "    total += item['price']! * qty;\n"
            "  }\n"
            "  return [count, total];\n"
            "}"
        ),
    ),
    Kata(
        id="dart-top-tags",
        level=5,
        language="dart",
        name="topTags",
        brief=(
            "Return the n most used tags, most used first, with tags used "
            "equally often in alphabetical order. Fewer than n different "
            "tags gives all of them; an n of nought gives an empty list."
        ),
        params=("tags", "n"),
        types=("List<String>", "int"),
        returns="List<String>",
        family=FAMILY,
        example=(
            "topTags(['dart', 'ui', 'dart', 'web', 'ui', 'dart'], 2) is "
            "['dart', 'ui']"
        ),
        hint=(
            "Two steps you have already done: count into a Map, then sort "
            "a copy. The map's entries.toList() gives you something to "
            "sort, and comparing b's count to a's puts the biggest first. "
            "take(n) does not mind n being more than there are; sublist "
            "does."
        ),
        cases=(
            (["dart", "ui", "dart", "web", "ui", "dart"], 2),
            ([], 3),
            (["solo"], 1),
            (["a", "b"], 0),
            (["b", "a", "c"], 2),
            (["x", "y", "y"], 5),
            (["web", "web", "app", "app", "cli"], 2),
            (["flutter", "dart", "flutter", "riverpod", "dart", "flutter"], 1),
            (["m", "n", "m", "n", "o", "o", "o"], 3),
            (["z"], 0),
        ),
        solve=_top_tags,
        checks=(
            ((["dart", "ui", "dart", "web", "ui", "dart"], 2), ["dart", "ui"]),
            (([], 3), []),
            ((["a", "b"], 0), []),
            # A tie on two apiece: alphabetical decides, not first seen.
            ((["web", "web", "app", "app", "cli"], 2), ["app", "web"]),
            ((["m", "n", "m", "n", "o", "o", "o"], 3), ["o", "m", "n"]),
        ),
        dart_answer=(
            "List<String> topTags(List<String> tags, int n) {\n"
            "  final counts = <String, int>{};\n"
            "  for (final tag in tags) {\n"
            "    counts.update(tag, (c) => c + 1, ifAbsent: () => 1);\n"
            "  }\n"
            "  final ranked = counts.entries.toList();\n"
            "  ranked.sort((a, b) {\n"
            "    final byCount = b.value.compareTo(a.value);\n"
            "    return byCount != 0 ? byCount : a.key.compareTo(b.key);\n"
            "  });\n"
            "  return ranked.take(n).map((entry) => entry.key).toList();\n"
            "}"
        ),
    ),
)


DART_KATAS: tuple[Kata, ...] = COLLECTIONS + SHAPING + COMBINED
