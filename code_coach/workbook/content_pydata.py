"""Pages 362-371: Python data practice.

The everyday jobs of working with data, one library and one habit at a time:
counting with Counter, grouping with defaultdict and groupby, a table of
records, the statistics module, csv text, JSON round trips, fixed dates,
money with Decimal and Fraction, a grid of lists, and a block of text. It is
the Python counterpart of the JavaScript data pages (178-187): the same
jobs, done with what Python ships.

Everything is deterministic and prints the same on any machine. Dates are
fixed dates, never today. csv and JSON live in strings and io.StringIO, and
a csv writer is told lineterminator="\\n". Numbers printed to a few
decimals are chosen so that no row sits on a rounding tie. Where Python
promises an order (a Counter ties in the order the keys first appeared, a
sort is stable, a dict remembers insertion order) the prompts say so.

Counting and grouping with defaultdict share a page with groupby (the list
asked for eleven topics and ten pages), so the second page is the two ways of
grouping side by side: a dictionary that needs no sorting, and groupby, which
needs it.

Python only, numbered after the scripting pages (342-351). Registration
decides the final numbers, so only _FIRST below has to change.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PYTHON = ("python",)

#: The number of the first page; the other nine follow it.
_FIRST = 362


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
        languages=PYTHON,
        tier="intermediate",
    )


def _and(words) -> str:
    words = [str(w) for w in words]
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _py(v) -> str:
    """A value the way Python writes it, for a prompt to show."""
    return repr(v)


def _isos(dates) -> str:
    return ", ".join(_iso(d) for d in dates)


def _iso(t) -> str:
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"


# ── 362. Counter ─────────────────────────────────────────────

_COUNT_TAIL = " Words with the same count come in the order they first appear."

_COUNTER = (
    ("count", {"words": ["red", "blue", "red", "green", "red", "blue"], "word": "red"}),
    ("count", {"words": ["cat", "dog", "cat", "bird", "dog", "cat", "fish"], "word": "dog"}),
    ("missing", {"words": ["apple", "pear", "apple", "fig"], "word": "kiwi"}),
    ("total", {"words": ["one", "two", "two", "three", "three", "three"]}),
    ("letters", {"text": "banana"}),
    ("letters", {"text": "mississippi"}),
    ("top", {"words": ["ant", "bee", "ant", "cow", "bee", "ant", "dog"], "n": 2}),
    ("repeated", {"words": ["tea", "jam", "tea", "bun", "jam", "cake"]}),
    ("repeated", {"words": ["one", "two", "three", "two", "four", "one", "two"]}),
    ("best", {"words": ["red", "blue", "red", "green"]}),
    ("normalised", {"text": "The cat saw the Cat and THE dog", "word": "the"}),
    ("normalised", {"text": "Red red RED blue Blue sky", "word": "red"}),
    ("top", {"words": ["pen", "ink", "pad", "ink", "pen", "pad", "cup"], "n": 2}),
    ("best", {"words": ["fig", "plum", "fig", "plum", "kiwi"]}),
    ("update", {"words": ["red", "blue", "red", "green"], "more": ["red", "green"], "word": "red"}),
    ("top", {"words": ["sun", "rain", "sun", "snow", "rain", "wind", "sun", "snow", "rain"],
             "n": 3}),
    ("least", {"words": ["oak", "pine", "oak", "elm", "pine", "oak"]}),
    ("anagram", {"a": "listen", "b": "silent"}),
    ("anagram", {"a": "apple", "b": "paper"}),
    ("subtract", {"words": ["apple", "apple", "pear", "fig"],
                  "sold": ["apple", "apple", "kiwi"]}),
    ("subtract", {"words": ["bolt", "nut", "bolt", "nut", "nut"],
                  "sold": ["nut", "nut", "nut", "bolt", "washer"]}),
)


def _counter_row(row):
    want, a = row
    args = {"want": want, **a}
    words = _py(a.get("words"))
    count = "Count the words in " + words + " with a Counter"
    if want == "count":
        return f"{count} and print how many times {a['word']} appears.", args
    if want == "missing":
        return (f"{count}. Print the count it gives for {a['word']}, which is not in "
                f"the list, then print how many different words the Counter holds.", args)
    if want == "total":
        return (f"{count}. Print the total number of words it counted, then how many "
                f"different words it holds.", args)
    if want == "letters":
        return (f"Count the letters of the word {a['text']} with a Counter and print "
                f"each letter and its count, one pair to a line with a space between, "
                f"in alphabetical order of the letter.", args)
    if want == "top":
        return (f"{count} and print its {a['n']} most common words, one to a line, each "
                f"as the word, a space and its count.{_COUNT_TAIL}", args)
    if want == "best":
        return (f"{count} and print the most common word and its count on one line, "
                f"separated by a space. If two words are equally common, give the one "
                f"that appears first in the list.", args)
    if want == "repeated":
        return (f"{count} and print the words that appear more than once, in "
                f"alphabetical order, joined by a comma and a space.", args)
    if want == "normalised":
        return (f"Count the words of the sentence '{a['text']}' with a Counter, "
                f"ignoring capital letters, and print how many times {a['word']} "
                f"appears.", args)
    if want == "update":
        return (f"{count}, then add the words {_py(a['more'])} to the same counter and "
                f"print the count for {a['word']}.", args)
    if want == "least":
        return (f"{count} and print the least common word and its count on one line, "
                f"separated by a space.", args)
    if want == "anagram":
        return (f"Count the letters of {a['a']} and of {a['b']} with two Counters and "
                f"print whether the two counters are equal.", args)
    return (f"{count} to stand for a stock, take away the words {_py(a['sold'])}, one "
            f"for each sale, with the counter's subtract method, and print the sorted "
            f"list of the (word, count) pairs it now holds.", args)


COUNTER_PAGE = _page(
    "py-data-counter", _FIRST, "Data: counting with Counter",
    "collections.Counter counts whatever you hand it: Counter(words) is a "
    "dictionary from each item to how many times it appeared, and Counter(text) "
    "counts letters. A missing key reads as 0 without being added, so "
    "counts['kiwi'] never raises and never grows the counter. most_common(n) "
    "gives the n biggest as (item, count) pairs, and items with the same count "
    "come out in the order they were first seen (a Counter remembers insertion "
    "order, and the sort behind most_common is stable). most_common() with no "
    "argument lists everything, so its last pair is the least common. "
    "counts.total() adds the counts up, len(counts) is the number of different "
    "items, update(more) adds to the counts, and subtract(more) takes away, "
    "leaving zeros and even negatives in place. Two Counters are equal when "
    "every count is, which makes an anagram check one comparison.",
    "from collections import Counter; counts = Counter(['red', 'blue', 'red']); "
    "counts['red'] is 2, counts['green'] is 0, counts.most_common(1) is "
    "[('red', 2)], and counts.total() is 3",
    "py_data_counter",
    tuple(_counter_row(row) for row in _COUNTER),
)


# ── 363. defaultdict and groupby ─────────────────────────────

_PEOPLE = [("ada", "red"), ("sam", "blue"), ("kim", "red"), ("lee", "blue"),
           ("zoe", "green"), ("max", "red")]
_SALES = [("east", 5), ("west", 3), ("east", 7), ("north", 2), ("west", 4)]

_GROUP = (
    ("members", {"pairs": _PEOPLE}),
    ("sizes", {"pairs": [("ada", "ops"), ("sam", "dev"), ("kim", "ops"), ("lee", "dev"),
                         ("zoe", "ops")]}),
    ("totals", {"pairs": [("pen", 3), ("ink", 8), ("pen", 5), ("pad", 2), ("ink", 1)]}),
    ("by_length", {"words": ["ant", "bee", "tiger", "cat", "horse", "lion", "zebra"]}),
    ("default", {"stock": {"apple": 4, "pear": 0}, "have": "apple", "miss": "kiwi"}),
    ("peek", {"pairs": [("ada", "red"), ("sam", "blue"), ("kim", "red"), ("lee", "blue")],
              "team": "green"}),
    ("members", {"pairs": [("ann", "night"), ("bob", "day"), ("cy", "night"), ("di", "day"),
                           ("ed", "night")]}),
    ("totals", {"pairs": [("tea", 4), ("jam", 2), ("tea", 1), ("tea", 6), ("jam", 9),
                          ("bun", 3)]}),
    ("unique", {"pairs": [("ada", "py"), ("sam", "c"), ("ada", "py"), ("ada", "go"),
                          ("sam", "c"), ("sam", "js")]}),
    ("invert", {"skills": {"ada": ["py", "c"], "sam": ["py", "js"], "kim": ["c"]}}),
    ("sums", {"rows": _SALES}),
    ("counts", {"rows": [("red", 1), ("blue", 1), ("red", 2), ("red", 3), ("blue", 9)]}),
    ("averages", {"rows": [("east", 5), ("west", 3), ("east", 8), ("west", 6), ("east", 2)]}),
    ("averages", {"rows": [("tea", 3), ("jam", 4), ("tea", 4), ("jam", 5), ("tea", 6),
                           ("jam", 2)]}),
    ("biggest", {"rows": [("east", 5), ("west", 3), ("east", 9), ("west", 11),
                          ("north", 2)]}),
    ("names", {"rows": [("red", "ada"), ("blue", "sam"), ("red", "kim"), ("blue", "lee"),
                        ("green", "zoe")]}),
    ("buckets", {"numbers": [34, 12, 15, 38, 21, 17, 39]}),
    ("dict_of_lists", {"rows": [("east", 3), ("west", 1), ("east", 5), ("north", 2)]}),
    ("runs", {"text": "aaabccdd"}),
    ("unsorted", {"rows": [("east", 1), ("west", 2), ("east", 3), ("east", 4), ("west", 5)]}),
    ("sums", {"rows": [("tue", 4), ("mon", 2), ("tue", 5), ("wed", 1), ("mon", 6)]}),
)

_DD_TEXT = "with a defaultdict of lists"


def _group_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "members":
        return (f"Given the (person, team) pairs {_py(a['pairs'])}, group the people by "
                f"team {_DD_TEXT}. For each team in alphabetical order, print the team, a "
                f"colon, a space and its people joined by a comma and a space, in the "
                f"order they appear.", args)
    if want == "sizes":
        return (f"Given the (person, team) pairs {_py(a['pairs'])}, group the people by "
                f"team {_DD_TEXT}. For each team in alphabetical order, print the team, "
                f"a space and the number of people in it.", args)
    if want == "totals":
        return (f"Given the (item, amount) pairs {_py(a['pairs'])}, add up the amounts "
                f"for each item with a defaultdict of int. For each item in alphabetical "
                f"order, print the item, a space and its total.", args)
    if want == "by_length":
        return (f"Group the words in {_py(a['words'])} by their length {_DD_TEXT}. For "
                f"each length from shortest to longest, print the length, a space and "
                f"the words of that length joined by single spaces, in list order.", args)
    if want == "default":
        return (f"Make a defaultdict of int that starts from the entries "
                f"{_py(a['stock'])}. Print the entry for {a['have']} and the entry for "
                f"{a['miss']} on one line separated by a space, then print how many "
                f"entries the dictionary has.", args)
    if want == "peek":
        return (f"Given the (person, team) pairs {_py(a['pairs'])}, group the people by "
                f"team {_DD_TEXT}. Then print what looking up the team {a['team']}, "
                f"which nobody belongs to, gives, and print how many teams the "
                f"dictionary holds after that.", args)
    if want == "unique":
        return (f"Given the (user, tag) pairs {_py(a['pairs'])}, collect each user's "
                f"tags in a defaultdict of sets, so repeats vanish. For each user in "
                f"alphabetical order, print the user, a space and the tags in "
                f"alphabetical order joined by a comma and a space.", args)
    if want == "invert":
        return (f"Here is who knows which skills: {_py(a['skills'])}. Turn it round "
                f"{_DD_TEXT}, from each skill to the people who know it, in the order "
                f"they are listed. For each skill in alphabetical order, print the "
                f"skill, a space and its people joined by a comma and a space.", args)
    rows = _py(a.get("rows"))
    if want == "sums":
        return (f"The (key, amount) rows are {rows}. Sort them by key, then use groupby "
                f"to print each key and the sum of its amounts, one pair to a line with "
                f"a space between.", args)
    if want == "counts":
        return (f"The (key, amount) rows are {rows}. Sort them by key, then use groupby "
                f"to print each key and how many rows it has, one pair to a line with "
                f"a space between.", args)
    if want == "averages":
        return (f"The (key, amount) rows are {rows}. Sort them by key, then use groupby "
                f"to print each key and the average of its amounts to one decimal "
                f"place, one pair to a line with a space between.", args)
    if want == "biggest":
        return (f"The (key, amount) rows are {rows}. Sort them by key, then use groupby "
                f"to print each key and its largest amount, one pair to a line with a "
                f"space between.", args)
    if want == "names":
        return (f"The (team, person) rows are {rows}. Sort them by team, then use "
                f"groupby to print each team, a colon, a space and its people joined by "
                f"a comma and a space, in the order the sort leaves them.", args)
    if want == "buckets":
        return (f"Sort the numbers {_py(a['numbers'])}, then use groupby with the tens "
                f"as the key. For each group print the first number of its tens (10 for "
                f"12, 20 for 27, and so on), a space and the list of its numbers.", args)
    if want == "dict_of_lists":
        return (f"The (key, amount) rows are {rows}. Sort the rows, then use groupby to "
                f"build a dictionary from each key to the list of its amounts, and "
                f"print the dictionary.", args)
    if want == "runs":
        return (f"Use groupby on the text {a['text']} to print it again with every run "
                f"of the same letter written as the letter followed by the length of "
                f"the run.", args)
    return (f"The (key, amount) rows are {rows}. Do not sort them: use groupby on them "
            f"as they stand, and print each group's key and the sum of its amounts, one "
            f"pair to a line with a space between, in the order the groups come out.",
            args)


GROUP_PAGE = _page(
    "py-data-grouping", _FIRST + 1, "Data: grouping with defaultdict and groupby",
    "There are two ways to group. A defaultdict makes the entry for a new key "
    "by itself: defaultdict(list) lets groups[team].append(person) work the "
    "first time a team is seen, defaultdict(int) lets totals[item] += amount "
    "start from zero, and defaultdict(set) drops repeats. Looking up a key "
    "that is not there makes it, so len() grows, which counts.get does not do. "
    "No sorting is needed, and the keys come out in the order they were first "
    "seen. itertools.groupby is different: it only joins neighbours, so the "
    "rows must be sorted by the key first or the same key turns up in several "
    "groups. Each group is a lazy iterator that is gone once you move on, so "
    "use it at once (sum(...), list(...), len(list(...))). sort is stable, so "
    "rows with the same key keep their order inside the group.",
    "from collections import defaultdict; groups = defaultdict(list); for "
    "person, team in [('ada', 'red'), ('sam', 'blue'), ('kim', 'red')]: "
    "groups[team].append(person) gives {'red': ['ada', 'kim'], 'blue': "
    "['sam']}; and groupby(sorted(rows), key=lambda r: r[0]) gives one group "
    "per key",
    "py_data_group",
    tuple(_group_row(row) for row in _GROUP),
)


# ── 364. A table of records ──────────────────────────────────

_STAFF = [
    {"name": "Ada", "dept": "ops", "age": 31, "pay": 52},
    {"name": "Sam", "dept": "dev", "age": 28, "pay": 61},
    {"name": "Kim", "dept": "ops", "age": 45, "pay": 48},
    {"name": "Lee", "dept": "dev", "age": 39, "pay": 70},
    {"name": "Zoe", "dept": "hr", "age": 26, "pay": 44},
    {"name": "Max", "dept": "ops", "age": 34, "pay": 57},
]
_BOOKS = [
    {"title": "Dune", "genre": "scifi", "year": 1965, "pages": 412},
    {"title": "Emma", "genre": "classic", "year": 1815, "pages": 474},
    {"title": "Ilium", "genre": "scifi", "year": 2003, "pages": 752},
    {"title": "Ulysses", "genre": "classic", "year": 1922, "pages": 730},
    {"title": "Neuromancer", "genre": "scifi", "year": 1984, "pages": 271},
]
_CARS = [
    {"model": "Civic", "brand": "honda", "price": 24, "mpg": 36},
    {"model": "Golf", "brand": "vw", "price": 26, "mpg": 34},
    {"model": "Jazz", "brand": "honda", "price": 21, "mpg": 40},
    {"model": "Polo", "brand": "vw", "price": 19, "mpg": 43},
    {"model": "Accord", "brand": "honda", "price": 29, "mpg": 31},
]

_KINDS = {"name": "people", "title": "books", "model": "cars"}


def _table_text(rows) -> str:
    """The table in words: each record on its own, fields in order."""
    label = next(iter(rows[0]))
    parts = []
    for r in rows:
        rest = ", ".join(f"{k} {v}" for k, v in r.items() if k != label)
        parts.append(f"{r[label]} ({rest})")
    return "; ".join(parts)


def _records_row(row):
    want, rows, a = row
    args = {"want": want, "rows": rows, **a}
    label = next(iter(rows[0]))
    kind = _KINDS[label]
    pre = (f"Make a list of dictionaries from these {kind}, one dictionary for each, "
           f"with the fields in the order shown: {_table_text(rows)}. ")
    join = "in table order, joined by a comma and a space"
    if want == "filter":
        return (f"{pre}Print the {label}s of the {kind} whose {a['key']} is more than "
                f"{a['limit']}, {join}.", args)
    if want == "match":
        return (f"{pre}Print the {label}s of the {kind} whose {a['key']} is "
                f"{a['value']}, {join}.", args)
    if want == "count_of":
        return (f"{pre}Print how many of the {kind} have {a['key']} more than "
                f"{a['limit']}.", args)
    if want == "two_filter":
        return (f"{pre}Print the {label}s of the {kind} whose {a['key']} is "
                f"{a['value']} and whose {a['key2']} is at least {a['limit']}, {join}.", args)
    if want == "sort1":
        order = "largest first" if a["reverse"] else "smallest first"
        return (f"{pre}Print the {label}s of all the {kind} in order of {a['key']}, "
                f"{order}, joined by a comma and a space.", args)
    if want == "sort2":
        first = ("alphabetically" if isinstance(rows[0][a["first"]], str)
                 else "smallest first")
        second = "largest first" if a["desc"] else "smallest first"
        return (f"{pre}Sort the records by {a['first']} ({first}) and, within the same "
                f"{a['first']}, by {a['second']} ({second}). Print one line for each: its "
                f"{label}, its {a['first']} and its {a['second']}, separated by "
                f"spaces.", args)
    if want == "best":
        end = "highest" if a["how"] == "max" else "lowest"
        return f"{pre}Print the {label} of the record with the {end} {a['key']}.", args
    if want == "top":
        return (f"{pre}Print the {label}s of the {a['n']} records with the highest "
                f"{a['key']}, highest first, joined by a comma and a space.", args)
    if want == "total_of":
        return (f"{pre}Print the total {a['key']} of the {kind} whose {a['by']} is "
                f"{a['value']}.", args)
    if want == "average_of":
        return (f"{pre}Print the average {a['key']} of the {kind} whose {a['by']} is "
                f"{a['value']}, to one decimal place.", args)
    if want == "unique":
        return (f"{pre}Print the different values of {a['key']}, in alphabetical order "
                f"and joined by a comma and a space, then print how many different "
                f"values there are.", args)
    if want == "column":
        return (f"{pre}Make a list of every {a['key']} in table order and print it, then "
                f"print the difference between the largest and the smallest.", args)
    if want == "lookup":
        return (f"{pre}Make a dictionary from each {label} to its whole record, and use "
                f"it to print the {a['field']} of {a['name']}.", args)
    return (f"{pre}Give everyone whose {a['by']} is {a['value']} a rise of {a['step']} "
            f"in {a['key']} by changing their records, then print the total "
            f"{a['key']} of all the records.", args)


_RECORDS = (
    ("filter", _STAFF, {"key": "pay", "limit": 50}),
    ("filter", _BOOKS, {"key": "year", "limit": 1950}),
    ("match", _STAFF, {"key": "dept", "value": "ops"}),
    ("count_of", _CARS, {"key": "mpg", "limit": 35}),
    ("unique", _BOOKS, {"key": "genre"}),
    ("column", _CARS, {"key": "mpg"}),
    ("lookup", _BOOKS, {"name": "Ilium", "field": "pages"}),
    ("best", _STAFF, {"key": "pay", "how": "max"}),
    ("sort1", _STAFF, {"key": "age", "reverse": False}),
    ("sort1", _CARS, {"key": "price", "reverse": True}),
    ("two_filter", _STAFF, {"key": "dept", "value": "ops", "key2": "pay", "limit": 50}),
    ("two_filter", _BOOKS, {"key": "genre", "value": "scifi", "key2": "pages", "limit": 400}),
    ("total_of", _STAFF, {"key": "pay", "by": "dept", "value": "ops"}),
    ("average_of", _STAFF, {"key": "age", "by": "dept", "value": "dev"}),
    ("top", _STAFF, {"key": "pay", "n": 3}),
    ("top", _CARS, {"key": "mpg", "n": 2}),
    ("raise", _STAFF, {"key": "pay", "by": "dept", "value": "dev", "step": 5}),
    ("sort2", _STAFF, {"first": "dept", "second": "pay", "desc": True}),
    ("sort2", _BOOKS, {"first": "genre", "second": "year", "desc": False}),
    ("sort2", _CARS, {"first": "brand", "second": "price", "desc": False}),
    ("average_of", _CARS, {"key": "price", "by": "brand", "value": "honda"}),
)

RECORDS_PAGE = _page(
    "py-data-records", _FIRST + 2, "Data: a table of records",
    "Real data is usually a list of dictionaries, one for each record, all "
    "with the same keys. A list comprehension filters it: [row['name'] for row "
    "in rows if row['pay'] > 50]. sorted(rows, key=lambda row: row['age']) "
    "orders it, reverse=True flips it, and a tuple as the key sorts by two "
    "things at once: (row['dept'], -row['pay']) is dept A to Z and, within a "
    "dept, the highest pay first (a minus sign flips a number, not a string). "
    "sorted is stable, so rows that tie keep their table order. Slice the "
    "front for the top few, max(rows, key=...) finds the best record in one "
    "pass, sum() with a condition totals a group, and a dictionary built from "
    "the rows, {row['name']: row for row in rows}, turns a search into a "
    "lookup. The records are the same objects wherever you reach them, so "
    "changing row['pay'] in a loop changes the table itself.",
    "rows = [{'name': 'Ada', 'pay': 52}, {'name': 'Sam', 'pay': 61}]; "
    "[r['name'] for r in rows if r['pay'] > 55] is ['Sam']; "
    "sorted(rows, key=lambda r: -r['pay'])[0]['name'] is 'Sam'; "
    "sum(r['pay'] for r in rows) is 113",
    "py_data_records",
    tuple(_records_row(row) for row in _RECORDS),
)


# ── 365. statistics ──────────────────────────────────────────

_STATS = (
    ("mean", {"data": [4, 8, 15, 16, 23, 42], "digits": 2}),
    ("mean", {"data": [3, 5, 8], "digits": 2}),
    ("median", {"data": [7, 1, 5, 3, 9], "digits": 1}),
    ("median", {"data": [10, 2, 8, 4], "digits": 1}),
    ("mode", {"data": [3, 1, 3, 2, 3, 1]}),
    ("mode_words", {"words": ["red", "blue", "red", "green", "red", "blue"]}),
    ("mean", {"data": [90, 85, 77, 64, 100], "digits": 1}),
    ("median", {"data": [5, 12, 9, 20, 14, 3], "digits": 1}),
    ("above", {"data": [4, 8, 15, 16, 23, 42]}),
    ("multimode", {"data": [1, 2, 2, 3, 3, 4]}),
    ("multimode", {"data": [5, 1, 5, 2, 1, 9]}),
    ("low_high", {"data": [4, 1, 7, 9]}),
    ("pstdev", {"data": [2, 4, 4, 4, 5, 5, 7, 9], "digits": 2}),
    ("pstdev", {"data": [1, 2, 3, 4, 5], "digits": 2}),
    ("stdev", {"data": [1, 2, 3, 4, 5], "digits": 2}),
    ("stdev", {"data": [2, 4, 4, 4, 5, 5, 7, 9], "digits": 2}),
    ("pvariance", {"data": [1, 2, 3, 4, 5], "digits": 2}),
    ("variance", {"data": [2, 4, 4, 4, 5, 5, 7, 9], "digits": 2}),
    ("trimmed", {"data": [90, 12, 55, 60, 58], "digits": 1}),
    ("quantiles", {"data": [7, 1, 9, 3, 5, 11, 13, 2]}),
    ("outliers", {"data": [10, 11, 12, 10, 11, 50], "k": 2}),
    ("outliers", {"data": [10, 12, 11, 13, 12, 11, 10], "k": 2}),
)

_STAT_NAMES = {
    "mean": "mean", "median": "median", "pstdev": "population standard deviation",
    "stdev": "sample standard deviation", "pvariance": "population variance",
    "variance": "sample variance",
}


def _stats_row(row):
    want, a = row
    args = {"want": want, **a}
    data = _py(a.get("data"))
    if want in _STAT_NAMES:
        places = "one decimal place" if a["digits"] == 1 else "two decimal places"
        return f"Print the {_STAT_NAMES[want]} of {data} to {places}.", args
    if want == "mode":
        return f"Print the mode of {data}, the value that appears most often.", args
    if want == "mode_words":
        return (f"Print the mode of the words {_py(a['words'])}, the word that appears "
                f"most often.", args)
    if want == "multimode":
        return (f"Print the list of every value of {data} that is tied for most common, "
                f"in the order they first appear.", args)
    if want == "low_high":
        return (f"Print the lower middle value and then the upper middle value of "
                f"{data}, on one line separated by a space.", args)
    if want == "quantiles":
        return (f"Print the three quartile cut points of {data} that the statistics "
                f"module gives with its default settings, each to two decimal places, "
                f"separated by spaces.", args)
    if want == "trimmed":
        return (f"Drop the smallest and the largest value of {data} and print the "
                f"mean of the rest to one decimal place.", args)
    if want == "above":
        return f"Print how many values of {data} are above their mean.", args
    return (f"Print the list of values of {data} that lie more than {a['k']} population "
            f"standard deviations from the mean, or the word none when there are "
            f"none.", args)


STATS_PAGE = _page(
    "py-data-stats", _FIRST + 3, "Data: statistics",
    "The statistics module answers the usual questions about a list of "
    "numbers: mean, median (the middle value, or the mean of the two middle "
    "ones when the count is even), median_low and median_high (always one of "
    "the values), mode (the most common value; text works too) and multimode "
    "(a list of every value tied for most common, in the order first seen). "
    "pstdev and pvariance treat the data as the whole population, stdev and "
    "variance as a sample from it and divide by n - 1, which is why they are "
    "bigger. quantiles(data) cuts the sorted data into four with the "
    "'exclusive' method by default. To print a number to a fixed number of "
    "decimals use an f-string, f'{x:.2f}', which rounds the exact value of the "
    "float (a result that sits exactly between two roundings is a trap, so "
    "these exercises avoid them). statistics.mean of whole numbers can come "
    "back as a whole number, and f'{x:.1f}' prints it the same way either way.",
    "import statistics; data = [4, 8, 15, 16, 23, 42]; f'{statistics.mean(data):.2f}' "
    "is '18.00', statistics.median([5, 12, 9, 20, 14, 3]) is 10.5, and "
    "statistics.multimode([1, 2, 2, 3, 3]) is [2, 3]",
    "py_data_stats",
    tuple(_stats_row(row) for row in _STATS),
)


# ── 366. csv ─────────────────────────────────────────────────


def _csv_line(fields, delim: str = ",") -> str:
    def one(f: str) -> str:
        if delim in f or '"' in f:
            return '"' + f.replace('"', '""') + '"'
        return f
    return delim.join(one(f) for f in fields)


def _csv_pre(rows, delim: str = ",") -> str:
    lines = [_csv_line(r, delim) for r in rows]
    shown = ", ".join(f"'{x}'" for x in lines)
    how = "which separates its fields with semicolons, " if delim == ";" else ""
    return (f"Write this csv text, {how}as one string with a newline at the end of every "
            f"line: the lines {shown}. ")


_T1 = [["name", "qty"], ["ada", "3"], ["sam", "5"], ["kim", "2"], ["lee", "8"]]
_T2 = [["name", "city", "qty"], ["ada", "paris", "3"], ["sam", "rome", "5"],
       ["kim", "paris", "2"], ["lee", "rome", "8"], ["zoe", "oslo", "4"]]
_T3 = [["item", "price", "qty"], ["pen", "3", "4"], ["ink", "8", "2"], ["pad", "5", "3"],
       ["cup", "6", "1"]]
_T4 = [["id", "score"], ["a1", "9"], ["b2", "10"], ["c3", "100"], ["d4", "25"]]
_T5 = [["code", "count"], ["x", "7"], ["y", "42"], ["z", "315"], ["w", "80"]]
_T6 = [["team", "pts"], ["red", "3"], ["blue", "1"], ["red", "4"], ["blue", "2"],
       ["green", "9"]]
_Q1 = [["name", "note"], ["ada", "likes tea, jam"], ["sam", "plain"],
       ["kim", 'said "hi" twice']]
_Q2 = [["city", "country", "pop"], ["paris", "France, EU", "2"], ["rome", "Italy", "3"],
       ["oslo", "Norway", "1"]]
_S1 = [["name", "place", "qty"], ["ada", "Paris, France", "3"], ["sam", "Rome, Italy", "5"],
       ["kim", "Oslo", "2"]]

_CSV = (
    ("fieldnames", _T1, {}),
    ("first_row", _T2, {}),
    ("header_body", _T3, {}),
    ("count_where", _T1, {"col": "qty", "limit": 2}),
    ("unique", _T2, {"col": "city"}),
    ("average", _T1, {"col": "qty", "digits": 1}),
    ("count_where", _T2, {"col": "qty", "limit": 3}),
    ("average", _T2, {"col": "qty", "digits": 2}),
    ("max_row", _T2, {"col": "qty", "show": "name"}),
    ("string_max", _T4, {"col": "score"}),
    ("string_max", _T5, {"col": "count"}),
    ("filter_write", _T1, {"col": "qty", "limit": 2}),
    ("filter_write", _T3, {"col": "qty", "limit": 2}),
    ("computed", _T3, {"cols": ["price", "qty"], "show": "item"}),
    ("sorted_write", _T2, {"col": "qty", "show": "name"}),
    ("group_write", _T6, {"key": "team", "col": "pts"}),
    ("group_write", _T2, {"key": "city", "col": "qty"}),
    ("quoted", _Q1, {"row": 1, "col": 1}),
    ("quoted", _Q1, {"row": 3, "col": 1}),
    ("semicolon", _S1, {"row": 1, "col": 1}),
)


def _csv_row(row):
    want, rows, a = row
    args = {"want": want, "rows": rows, **a}
    delim = ";" if want == "semicolon" else ","
    pre = _csv_pre(rows, delim)
    col = a.get("col")
    if want == "fieldnames":
        return f"{pre}Read it with a DictReader and print the reader's fieldnames.", args
    if want == "first_row":
        return f"{pre}Read it with a DictReader and print the first row it gives.", args
    if want == "header_body":
        return (f"{pre}Read it with a csv reader, split off the first row as the header "
                f"and keep the rest as the body, then print the header and print how "
                f"many rows the body has.", args)
    if want == "count_where":
        return (f"{pre}Read it with a DictReader and print how many rows have {col} "
                f"more than {a['limit']}, comparing as numbers.", args)
    if want == "unique":
        return (f"{pre}Read it with a DictReader and print the different values of "
                f"{col}, in alphabetical order, joined by a comma and a space.", args)
    if want == "average":
        places = "one decimal place" if a["digits"] == 1 else "two decimal places"
        return (f"{pre}Read it with a DictReader and print the average {col}, as a "
                f"number, to {places}.", args)
    if want == "max_row":
        return (f"{pre}Read it with a DictReader and print the {a['show']} on the row "
                f"with the largest {col}, comparing as numbers.", args)
    if want == "string_max":
        return (f"{pre}Read it with a DictReader and print the largest {col} value "
                f"without turning the values into numbers first, so they compare as "
                f"strings do.", args)
    if want == "filter_write":
        return (f"{pre}Read it with a DictReader, and write the rows whose {col} is more "
                f"than {a['limit']} (as numbers) to a new csv text with a DictWriter "
                f"that has the same fieldnames and a newline as its lineterminator, "
                f"header included. Print the new text.", args)
    if want == "computed":
        x, y = a["cols"]
        return (f"{pre}Read it with a DictReader, and write a new csv text with a csv "
                f"writer (lineterminator a newline) holding, for each row and with no "
                f"header, its {a['show']} and the product of its {x} and {y} as "
                f"numbers. Print the new text.", args)
    if want == "sorted_write":
        return (f"{pre}Read it with a DictReader, and write a new csv text with a csv "
                f"writer (lineterminator a newline) holding, for each row and with no "
                f"header, its {a['show']} and its {col}, largest {col} first, comparing "
                f"as numbers. Print the new text.", args)
    if want == "group_write":
        return (f"{pre}Read it with a DictReader, add up {col} as numbers for each "
                f"{a['key']}, and write one row for each {a['key']}, in alphabetical "
                f"order and with no header, of the {a['key']} and its total, with a csv "
                f"writer whose lineterminator is a newline. Print the new text.", args)
    how = "a semicolon" if delim == ";" else "the default delimiter"
    return (f"{pre}Read it with a csv reader that uses {how} and print how many fields "
            f"row {a['row']} has, counting the header as row 0, then print its field "
            f"number {a['col']}, counting from 0.", args)


CSV_PAGE = _page(
    "py-data-csv", _FIRST + 4, "Data: csv tables",
    "csv.reader(io.StringIO(text)) turns csv text into lists of strings, "
    "one for each row, and csv.DictReader does the same with the first row as "
    "the keys, so row['qty'] replaces row[2]. Everything read is a string: "
    "int(row['qty']) before comparing or adding, because '9' > '10' as text "
    "(strings compare character by character). A field with a comma, a quote "
    "or a line break is wrapped in quotes in the text, and the reader takes "
    "them off again, so the comma inside it is not a gap. reader.fieldnames "
    "is the header, and next(reader) takes one row. To write, make a "
    "StringIO, hand it to csv.writer or csv.DictWriter with "
    "lineterminator='\\n' (the default is '\\r\\n', which is not what a "
    "terminal prints), call writerow or writerows, and read the text with "
    "out.getvalue(). DictWriter wants fieldnames and a writeheader() call. "
    "delimiter=';' reads the semicolon files some countries use.",
    "import csv, io; text = 'name,qty\\nada,3\\nsam,5\\n'; rows = "
    "list(csv.DictReader(io.StringIO(text))) gives [{'name': 'ada', 'qty': "
    "'3'}, {'name': 'sam', 'qty': '5'}], and sum(int(r['qty']) for r in rows) "
    "is 8",
    "py_data_csv",
    tuple(_csv_row(row) for row in _CSV),
)


# ── 367. JSON ────────────────────────────────────────────────

_ITEMS = [{"item": "pen", "price": 3, "qty": 4}, {"item": "ink", "price": 8, "qty": 2},
          {"item": "pad", "price": 5, "qty": 3}]


def _json_text(obj) -> str:
    """JSON the way json.dumps writes it, for a prompt to show."""
    if obj is True:
        return "true"
    if obj is False:
        return "false"
    if obj is None:
        return "null"
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, str):
        return f'"{obj}"'
    if isinstance(obj, list):
        return "[" + ", ".join(_json_text(x) for x in obj) + "]"
    return "{" + ", ".join(f'"{k}": {_json_text(v)}' for k, v in obj.items()) + "}"


_JSON = (
    ("dumps_sorted", {"obj": {"zoe": 1, "ann": 2, "max": 3}}),
    ("compact", {"obj": {"a": 1, "b": [1, 2], "c": None}}),
    ("types", {"obj": {"ok": True, "n": None, "name": "ada"}, "keys": ["ok", "n", "name"]}),
    ("total", {"rows": _ITEMS}),
    ("loads_path", {"obj": {"user": {"name": "ada", "langs": ["py", "c"]}},
                    "path": ["user", "name"]}),
    ("dumps_sorted", {"obj": {"name": "ada", "id": 7, "admin": True, "tags": ["x", "y"]}}),
    ("dumps_indent", {"obj": {"name": "ada", "langs": ["py", "c"], "age": 36}, "indent": 2}),
    ("filter_dump", {"rows": _ITEMS, "limit": 2}),
    ("round_trip", {"obj": {"ok": True, "tags": ["x", "y"], "n": None}}),
    ("compact", {"obj": {"id": 5, "items": [{"n": "pen", "q": 2}], "ok": False}}),
    ("loads_path", {"obj": {"user": {"name": "ada", "langs": ["py", "c"]}},
                    "path": ["user", "langs", 1]}),
    ("valid", {"text": '{"a": 1, "b": [true, null]}'}),
    ("valid", {"text": '{"a": 1,}'}),
    ("valid", {"text": "{'a': 1}"}),
    ("update_dump", {"obj": {"name": "ada", "visits": 9, "vip": False}, "key": "visits",
                     "step": 1, "new": "seen", "value": True}),
    ("dumps_indent", {"obj": {"ok": True, "items": [{"n": "pen", "q": 2}], "id": 1},
                      "indent": 4}),
    ("round_trip", {"obj": {"point": (3, 4), "name": "ada"}}),
    ("round_trip", {"obj": {1: "a", 2: "b"}}),
    ("valid", {"text": '{"ok": True}'}),
    ("update_dump", {"obj": {"count": 41, "name": "gus"}, "key": "count", "step": 1,
                     "new": "done", "value": True}),
)


def _json_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "dumps_sorted":
        return (f"Make the dictionary {_py(a['obj'])} and print it as JSON text with its "
                f"keys sorted.", args)
    if want == "dumps_indent":
        return (f"Make the dictionary {_py(a['obj'])} and print it as JSON text indented "
                f"by {a['indent']} spaces, with its keys sorted.", args)
    if want == "compact":
        return (f"Make the dictionary {_py(a['obj'])} and print it as compact JSON text: "
                f"keys in their original order and no space after any comma or colon.",
                args)
    if want == "loads_path":
        steps = " then ".join(repr(p) if isinstance(p, str) else f"position {p}"
                              for p in a["path"])
        return (f"Load the JSON text {_json_text(a['obj'])} and print the value you reach "
                f"by following {steps}.", args)
    if want == "types":
        return (f"Load the JSON text {_json_text(a['obj'])} and print the values of "
                f"{_and(a['keys'])}, in that order, on one line separated by spaces, "
                f"as Python shows them.", args)
    if want == "round_trip":
        return (f"Make the value {_py(a['obj'])}, turn it into JSON text and straight "
                f"back into data, then print what comes back and, on the next line, "
                f"whether it equals the original.", args)
    if want == "total":
        return (f"Load the JSON text {_json_text(a['rows'])}, a list of items with a "
                f"price and a quantity, and print the total of price times quantity "
                f"over all the items.", args)
    if want == "filter_dump":
        return (f"Load the JSON text {_json_text(a['rows'])} and print, as JSON text with "
                f"the default spacing, only the items with a qty of more than "
                f"{a['limit']}.", args)
    if want == "update_dump":
        return (f"Load the JSON text {_json_text(a['obj'])}, add {a['step']} to "
                f"{a['key']}, add the key {a['new']} set to true, and print the result "
                f"as JSON text with its keys sorted.", args)
    return (f"Try to load the JSON text {a['text']}. If it loads, print the Python value "
            f"it makes; if it is not valid JSON, print the word bad.", args)


JSON_PAGE = _page(
    "py-data-json", _FIRST + 5, "Data: JSON round trips",
    "json.dumps(data) turns data into JSON text and json.loads(text) turns "
    "it back. The text has its own spelling: true, false and null where "
    "Python has True, False and None, double quotes only, and \", \" and "
    "\": \" between items by default. sort_keys=True orders the keys, "
    "indent=2 lays it out over lines, and separators=(',', ':') squeezes out "
    "every space. A trip there and back does not return everything: a tuple "
    "comes back as a list, and a number used as a key comes back as text, "
    "because JSON has only lists and text keys, so the copy can be unequal to "
    "the original. Bad text raises json.JSONDecodeError: single quotes, a "
    "trailing comma, an unquoted key, True and a missing bracket are all "
    "refused. Read a number with its real type: json.loads gives ints and "
    "floats, not text.",
    "import json; json.dumps({'b': 1, 'a': [True, None]}, sort_keys=True) is "
    "'{\"a\": [true, null], \"b\": 1}'; json.loads('{\"n\": 3}')['n'] is 3; "
    "json.loads(json.dumps({'p': (3, 4)})) is {'p': [3, 4]}",
    "py_data_json",
    tuple(_json_row(row) for row in _JSON),
)


# ── 368. Dates ───────────────────────────────────────────────

_DAYNAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_FORMAT_WORDS = {
    "%d/%m/%Y": "day/month/year",
    "%m/%d/%Y": "month/day/year",
    "%Y%m%d": "the year, month and day run together",
    "%d %b %Y": "the day, a three-letter month name and the year",
}

_DATES = (
    ("diff", {"start": (2026, 1, 15), "end": (2026, 3, 1)}),
    ("diff", {"start": (2024, 2, 1), "end": (2024, 3, 1)}),
    ("weekday", {"day": (2026, 12, 25)}),
    ("weekday", {"day": (2000, 1, 1), "fmt": "%a"}),
    ("add", {"start": (2026, 1, 31), "n": 30}),
    ("add", {"start": (2024, 2, 28), "n": 2}),
    ("month_end", {"year": 2026, "month": 2}),
    ("month_end", {"year": 2024, "month": 2}),
    ("format", {"day": (2026, 3, 5), "fmt": "%d/%m/%Y"}),
    ("format", {"day": (2026, 3, 5), "fmt": "%A %d %B %Y"}),
    ("age", {"born": (1990, 7, 15), "on": (2026, 3, 1)}),
    ("age", {"born": (2000, 2, 29), "on": (2026, 2, 28)}),
    ("parse", {"start": (2026, 3, 5), "end": (2026, 4, 20), "fmt": "%d/%m/%Y"}),
    ("parse", {"start": (2025, 12, 20), "end": (2026, 1, 15), "fmt": "%d %b %Y"}),
    ("delta", {"start": (2026, 3, 1, 9, 0), "end": (2026, 3, 1, 17, 30)}),
    ("delta", {"start": (2026, 3, 1, 22, 15), "end": (2026, 3, 3, 8, 45)}),
    ("weekends", {"start": (2026, 3, 1), "end": (2026, 3, 31)}),
    ("span", {"days": [(2026, 3, 9), (2026, 1, 2), (2026, 2, 14)]}),
    ("next_weekday", {"day": (2026, 3, 5), "target": 0}),
    ("next_weekday", {"day": (2026, 3, 9), "target": 0}),
    ("format", {"day": (2026, 3, 5), "fmt": "%j"}),
    ("delta", {"start": (2026, 2, 27, 23, 0), "end": (2026, 3, 2, 1, 0)}),
)


def _dates_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "diff":
        return (f"Print the number of days from {_iso(a['start'])} to {_iso(a['end'])}, "
                f"both written as year-month-day dates.", args)
    if want == "weekday":
        how = ("abbreviated to three letters" if a.get("fmt") == "%a"
               else "written out in full")
        return (f"Print the name of the weekday of {_iso(a['day'])} ({how}, as "
                f"Monday, Tuesday and so on).", args)
    if want == "add":
        return (f"Print the date {a['n']} days after {_iso(a['start'])}, as "
                f"year-month-day.", args)
    if want == "month_end":
        return (f"Print the last day of month {a['month']} of {a['year']} as a date, by "
                f"taking the first day of the next month and going back one day.", args)
    if want == "format":
        return (f"Print the date {_iso(a['day'])} with the strftime format "
                f"'{a['fmt']}'.", args)
    if want == "age":
        return (f"Someone was born on {_iso(a['born'])}. Print their age in whole years "
                f"on {_iso(a['on'])}.", args)
    if want == "parse":
        fmt = a["fmt"]
        from_ = _text_date(a["start"], fmt)
        to = _text_date(a["end"], fmt)
        return (f"Read the two dates '{from_}' and '{to}' with strptime and the format "
                f"'{fmt}' ({_FORMAT_WORDS[fmt]}) and print the number of days from the "
                f"first to the second.", args)
    if want == "delta":
        s, e = a["start"], a["end"]
        return (f"Subtract the datetime {_stamp(s)} from the datetime {_stamp(e)} and "
                f"print the difference exactly as Python shows a timedelta.", args)
    if want == "weekends":
        return (f"Count the Saturdays and Sundays from {_iso(a['start'])} to "
                f"{_iso(a['end'])}, both days included, and print the count.", args)
    if want == "span":
        return (f"Print the earliest and the latest of the dates {_isos(a['days'])} on "
                f"one line, then on the next line the number of days between them.", args)
    day = _DAYNAMES[a["target"]]
    return (f"Print the first date strictly after {_iso(a['day'])} that falls on a {day} "
            f"(weekday number {a['target']}, where Monday is 0), as year-month-day.", args)


def _text_date(t, fmt: str) -> str:
    y, m, d = t
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct",
              "Nov", "Dec"]
    return {"%d/%m/%Y": f"{d:02d}/{m:02d}/{y}", "%m/%d/%Y": f"{m:02d}/{d:02d}/{y}",
            "%Y%m%d": f"{y}{m:02d}{d:02d}",
            "%d %b %Y": f"{d:02d} {months[m - 1]} {y}"}[fmt]


def _stamp(t) -> str:
    return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}"


DATES_PAGE = _page(
    "py-data-dates", _FIRST + 6, "Data: dates and weekdays",
    "date(2026, 3, 5) is a calendar day, and subtracting two dates gives a "
    "timedelta whose .days is the gap: (end - start).days. Adding "
    "timedelta(days=30) moves a date, and the calendar does the carrying, "
    "leap years included. day.weekday() counts Monday as 0 and Sunday as 6, "
    "and day.strftime('%A') is the name (%a short, %B the month in full, %b "
    "short, %d and %m padded with zeros, %j the day of the year). "
    "datetime.strptime(text, format) goes the other way, reading text with the "
    "same codes. The last day of a month is the day before the first of the "
    "next one. A datetime also holds hours and minutes, and printing the "
    "difference of two shows it as '1 day, 10:30:00'. An age is the difference "
    "in years, less one when the birthday has not come round yet in that "
    "year. Use fixed dates in practice: date.today() changes under you.",
    "from datetime import date, timedelta; (date(2026, 3, 1) - date(2026, 1, "
    "15)).days is 45; date(2026, 1, 31) + timedelta(days=30) is "
    "date(2026, 3, 2); date(2026, 3, 5).strftime('%A') is 'Thursday'",
    "py_data_dates",
    tuple(_dates_row(row) for row in _DATES),
)


# ── 369. Decimal and Fraction ────────────────────────────────

_MONEY = (
    ("sum_prices", {"prices": ["19.99", "5.5", "0.01"]}),
    ("sum_prices", {"prices": ["0.10", "0.2", "0.3"]}),
    ("cents", {"price": "19.99", "qty": 3}),
    ("same_value", {"x": "2.50", "y": "2.5"}),
    ("line_total", {"items": [("1.25", 4), ("0.40", 10), ("2.99", 2)]}),
    ("fraction_sum", {"parts": ["1/2", "1/3", "1/6"]}),
    ("fraction_ops", {"x": "3/4", "y": "2/3", "op": "-"}),
    ("fraction_ops", {"x": "1/2", "y": "3/5", "op": "*"}),
    ("cents", {"price": "0.05", "qty": 12}),
    ("line_total", {"items": [("2.5", 3), ("1.25", 2), ("0.10", 5)]}),
    ("same_value", {"x": "2.50", "y": "2.05"}),
    ("fraction_sum", {"parts": ["1/4", "1/4", "1/8"]}),
    ("fraction_ops", {"x": "3/4", "y": "9/8", "op": "/"}),
    ("tax", {"prices": ["19.99", "5.50", "3.25"], "rate": "0.0825"}),
    ("split", {"total": "100.00", "people": 3}),
    ("largest", {"parts": ["3/8", "2/5", "1/3"]}),
    ("fraction_parts", {"parts": ["1/6", "1/4", "1/3"]}),
    ("fraction_ops", {"x": "100", "y": "3/8", "op": "*"}),
    ("tax", {"prices": ["12.50", "7.25", "3.10"], "rate": "0.07"}),
    ("split", {"total": "100.00", "people": 6}),
    ("tax", {"prices": ["10.00", "8.00", "2.50"], "rate": "0.05"}),
    ("split", {"total": "20.50", "people": 4}),
)

_OPWORDS = {"+": "plus", "-": "minus", "*": "times", "/": "divided by"}


def _money_row(row):
    want, a = row
    args = {"want": want, **a}
    if want == "sum_prices":
        return (f"Add up the prices {_py(a['prices'])}, each made into a Decimal from its "
                f"string, and print the sum exactly as Decimal shows it.", args)
    if want == "line_total":
        return (f"The order lines are (price, quantity) pairs: {_py(a['items'])}, the "
                f"price a string for a Decimal. Print the total of price times "
                f"quantity over all the lines, as a Decimal.", args)
    if want == "tax":
        return (f"Add the prices {_py(a['prices'])} as Decimals, work out the tax at the "
                f"rate {a['rate']} rounded to the cent with ROUND_HALF_UP, and print the "
                f"subtotal, the tax and the total on one line separated by spaces.", args)
    if want == "split":
        return (f"Share {a['total']} between {a['people']} people. Print one share, the "
                f"total divided by {a['people']} and rounded to the cent with "
                f"ROUND_HALF_UP, then what is left over (the total minus the shares "
                f"added up), separated by a space.", args)
    if want == "cents":
        return (f"Make a Decimal from the string {a['price']} and print it as a whole "
                f"number of cents, then the cost of {a['qty']} of them in cents, on one "
                f"line separated by a space.", args)
    if want == "same_value":
        return (f"Make Decimals from the strings {a['x']} and {a['y']}. Print whether "
                f"they are equal, then on the next line print the two Decimals "
                f"separated by a space.", args)
    if want == "fraction_sum":
        return (f"Add the fractions {_py(a['parts'])} exactly with Fraction and print "
                f"the sum.", args)
    if want == "fraction_ops":
        return (f"Make Fractions from {a['x']} and {a['y']} and print the first "
                f"{_OPWORDS[a['op']]} the second, as a Fraction.", args)
    if want == "fraction_parts":
        return (f"Add the fractions {_py(a['parts'])} exactly with Fraction and print "
                f"the numerator and then the denominator of the sum, separated by a "
                f"space.", args)
    return f"Print the largest of the fractions {_py(a['parts'])}, as a Fraction.", args


MONEY_PAGE = _page(
    "py-data-money", _FIRST + 7, "Data: money with Decimal and Fraction",
    "Floats cannot hold 0.1 exactly, so money goes in Decimal, made from a "
    "string: Decimal('19.99'). Decimal adds and multiplies exactly and keeps "
    "the digits you gave it, so Decimal('2.50') == Decimal('2.5') is True "
    "while printing them shows 2.50 and 2.5, and a sum has as many decimals "
    "as its most precise part. To round to the cent use "
    "value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), which rounds a "
    "5 up, the way shops do (round() and the default rounding go to the even "
    "digit instead). Dividing a bill leaves a remainder: the shares added "
    "back up can be a cent short or over. int(Decimal('19.99') * 100) is the "
    "price in whole cents. Fraction is the other exact tool: Fraction('1/3') "
    "+ Fraction('1/6') is Fraction(1, 2), always reduced, printed as 1/2 (or "
    "just 2 when it is whole), with .numerator and .denominator. Both compare "
    "and sort by value.",
    "from decimal import ROUND_HALF_UP, Decimal; Decimal('19.99') + "
    "Decimal('0.01') is Decimal('20.00'); (Decimal('20.50') * "
    "Decimal('0.05')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) is "
    "Decimal('1.03'); from fractions import Fraction; Fraction('1/2') + "
    "Fraction('1/3') is Fraction(5, 6)",
    "py_data_money",
    tuple(_money_row(row) for row in _MONEY),
)


# ── 370. A grid of lists ─────────────────────────────────────

_G1 = [[1, 2, 3], [4, 5, 6]]
_G2 = [[3, 1, 4], [1, 5, 9], [2, 6, 5]]
_G3 = [[7, 2], [3, 8], [5, 1], [9, 4]]
_G4 = [[10, 20, 30], [40, 50, 60], [70, 80, 90]]
_G5 = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]

_GRID = (
    ("row_sums", {"rows": _G1}),
    ("transpose", {"rows": _G1}),
    ("col_sums", {"rows": _G2}),
    ("flatten", {"rows": _G1, "how": "comp"}),
    ("count_over", {"rows": _G2, "limit": 4}),
    ("mirror", {"rows": _G2}),
    ("build_table", {"h": 3, "w": 4}),
    ("set_cell", {"h": 2, "w": 3, "r": 1, "c": 2, "value": 5}),
    ("alias", {"h": 2, "w": 3, "r": 0, "c": 1, "value": 5}),
    ("transpose", {"rows": _G3}),
    ("col_sums", {"rows": _G3}),
    ("flatten", {"rows": _G3, "how": "chain"}),
    ("diagonal", {"rows": _G5, "which": "main"}),
    ("diagonal", {"rows": _G4, "which": "anti"}),
    ("biggest", {"rows": _G2}),
    ("best_row", {"rows": _G4}),
    ("neighbors", {"rows": _G5, "r": 0, "c": 1}),
    ("alias", {"h": 3, "w": 2, "r": 2, "c": 0, "value": 7}),
    ("rotate", {"rows": _G1}),
    ("rotate", {"rows": _G3}),
)


def _grid_row(row):
    want, a = row
    args = {"want": want, **a}
    rows = _py(a.get("rows"))
    if want == "row_sums":
        return (f"Print the list of the sums of each row of the grid {rows}, then on the "
                f"next line the sum of every number in it.", args)
    if want == "transpose":
        return (f"Print the transpose of the grid {rows}, as a list of lists, built with "
                f"zip.", args)
    if want == "col_sums":
        return (f"Print the list of the sums of each column of the grid {rows}, then on "
                f"the next line the number of columns.", args)
    if want == "flatten":
        how = ("a nested comprehension" if a["how"] == "comp"
               else "itertools.chain.from_iterable")
        return (f"Flatten the grid {rows} into one list, row by row, using {how}, and "
                f"print it.", args)
    if want == "count_over":
        return f"Print how many numbers in the grid {rows} are more than {a['limit']}.", args
    if want == "mirror":
        return (f"Print the grid {rows} with each row reversed, one row to a line, "
                f"numbers separated by spaces.", args)
    if want == "build_table":
        return (f"Print a multiplication table with {a['h']} rows and {a['w']} columns, "
                f"row r and column c holding r times c (both counted from 1), one row to "
                f"a line with spaces between the numbers.", args)
    if want == "set_cell":
        return (f"Make a grid of zeros with {a['h']} rows and {a['w']} columns, each row "
                f"its own list, set the cell in row {a['r']}, column {a['c']} (counting "
                f"from 0) to {a['value']}, and print the grid.", args)
    if want == "alias":
        return (f"Make a grid of zeros with {a['h']} rows and {a['w']} columns by "
                f"multiplying a list that holds one row of {a['w']} zeros by {a['h']}, "
                f"set the cell in row {a['r']}, column {a['c']} (counting from 0) to "
                f"{a['value']}, and print the grid.", args)
    if want == "diagonal":
        line = ("main diagonal, top left to bottom right" if a["which"] == "main"
                else "other diagonal, top right to bottom left")
        return (f"Print the list of the numbers on the {line} of the square grid "
                f"{rows}, then on the next line their sum.", args)
    if want == "biggest":
        return (f"Find the largest number in the grid {rows} and print it, its row "
                f"number and its column number (both counted from 0) on one line "
                f"separated by spaces.", args)
    if want == "best_row":
        return (f"Print the number of the row of the grid {rows} with the largest sum, "
                f"counting from 0, then on the next line that sum.", args)
    if want == "neighbors":
        return (f"In the grid {rows} add up the numbers directly above, below, left and "
                f"right of the cell in row {a['r']}, column {a['c']} (counting from 0), "
                f"leaving out any that fall off the grid, and print the total.", args)
    return (f"Turn the grid {rows} a quarter turn clockwise and print it, one row to a "
            f"line with the numbers separated by spaces.", args)


GRID_PAGE = _page(
    "py-data-grid", _FIRST + 8, "Data: grids of lists",
    "A grid is a list of rows, each a list, and rows[r][c] is row r, column "
    "c, both counted from 0. zip(*rows) hands over the columns, so "
    "[list(c) for c in zip(*rows)] is the transpose and [sum(c) for c in "
    "zip(*rows)] the column sums, where [sum(r) for r in rows] gives the row "
    "sums. [x for row in rows for x in row] flattens it (the loops read in the "
    "order you would write them out), and so does "
    "itertools.chain.from_iterable(rows). zip(*rows[::-1]) turns the grid a "
    "quarter turn clockwise. The diagonal is rows[i][i] and the other one is "
    "rows[i][-1 - i]. To make a grid use a comprehension, [[0] * w for _ in "
    "range(h)]: [[0] * w] * h repeats the same row h times, so setting one "
    "cell changes that column in every row. A neighbour may fall off the edge, "
    "so test 0 <= r < len(rows) before reading it.",
    "rows = [[1, 2, 3], [4, 5, 6]]; [list(c) for c in zip(*rows)] is "
    "[[1, 4], [2, 5], [3, 6]]; [sum(r) for r in rows] is [6, 15]; "
    "[sum(c) for c in zip(*rows)] is [5, 7, 9]; [x for r in rows for x in r] "
    "is [1, 2, 3, 4, 5, 6]",
    "py_data_grid",
    tuple(_grid_row(row) for row in _GRID),
)


# ── 371. A block of text ─────────────────────────────────────

_LOG1 = ["2026-03-01 INFO server started", "2026-03-01 WARN disk almost full",
         "2026-03-02 ERROR cannot connect", "2026-03-02 INFO retrying",
         "2026-03-03 ERROR timeout"]
_LOG2 = ["2026-04-10 INFO job queued", "2026-04-10 INFO job started",
         "2026-04-11 WARN slow response", "2026-04-11 INFO job done"]

_TEXTS = (
    ("levels", {"lines": _LOG1, "level": "ERROR"}),
    ("levels", {"lines": _LOG2, "level": "INFO"}),
    ("header_body", {"lines": ["name,qty", "ada,3", "sam,5", "kim,2"]}),
    ("messages", {"lines": _LOG1, "level": "ERROR"}),
    ("sum_csv", {"lines": ["item,cost", "pen,3", "ink,8", "pad,5"]}),
    ("rpartition", {"names": ["report.final.txt", "notes.md", "archive.tar.gz"]}),
    ("table", {"lines": ["ada,12", "sam,7", "kim,120"], "widths": [8, 5],
               "align": ["<", ">"]}),
    ("clean", {"text": "  the   quick  brown   fox  "}),
    ("longest", {"lines": ["short", "a much longer line", "medium one", "tiny"]}),
    ("messages", {"lines": _LOG2, "level": "WARN"}),
    ("settings", {"lines": ["name = ada", "  mode=fast  ", "", "limit = 10 "]}),
    ("table", {"lines": ["ada,12", "sam,7", "kim,120"], "widths": [8, 5],
               "align": ["<", ">"], "header": True}),
    ("comments", {"lines": ["# settings", "name=ada", "", "# more", "age=36"]}),
    ("sum_csv", {"lines": ["day,hours", "mon,8", "tue,6", "wed,7", "thu,9"]}),
    ("clean", {"text": "a  b   c    d "}),
    ("table", {"lines": ["ada,1200", "sam,35000", "kim,7"], "widths": [6, 8],
               "align": ["<", ">"], "comma": True}),
    ("settings", {"lines": ["host=local", "", "  port = 8080", "debug=on  "]}),
    ("rpartition", {"names": ["a.b.c.py", "readme.md", "photo.final.png", "x.tar.gz"]}),
    ("comments", {"lines": ["  # indented note", "x=1 ", "", "y=2", "# end"]}),
    ("table", {"lines": ["ada,12", "sam,7", "kim,120"], "widths": [9, 5],
               "align": ["^", ">"], "header": True}),
)


def _lines_text(lines) -> str:
    return ", ".join(repr(x) for x in lines)


def _text_row(row):
    want, a = row
    args = {"want": want, **a}
    lines = a.get("lines")
    if want == "levels":
        return (f"Put these log lines, each a date, a level and a message separated by "
                f"single spaces, in one text with a newline between them: "
                f"{_lines_text(lines)}. Print how many lines have the level "
                f"{a['level']}.", args)
    if want == "messages":
        return (f"Put these log lines, each a date, a level and a message separated by "
                f"single spaces, in one text with a newline between them: "
                f"{_lines_text(lines)}. Print the message of each line whose level is "
                f"{a['level']}, one to a line.", args)
    if want == "settings":
        return (f"Put these lines, a key = value setting on each, in one text with a "
                f"newline between them: {_lines_text(lines)}. Build a dictionary of the "
                f"settings with the stray spaces stripped off keys and values, skipping "
                f"blank lines, and print the dictionary.", args)
    if want == "table":
        w0, w1 = a["widths"]
        al = {"<": "left-aligned", ">": "right-aligned", "^": "centred"}
        extra = ", with a comma between thousands" if a.get("comma") else ""
        head = (" Put a header row first, with the words name and qty laid out the "
                "same way." if a.get("header") else "")
        return (f"Put these name,quantity lines in one text with a newline between "
                f"them: {_lines_text(lines)}. Print them as table rows: the name "
                f"{al[a['align'][0]]} in a width of {w0}, then the quantity "
                f"{al[a['align'][1]]} in a width of {w1}{extra}.{head}", args)
    if want == "header_body":
        return (f"Put these csv-like lines in one text with a newline between them: "
                f"{_lines_text(lines)}. Split off the first line as the header and keep "
                f"the rest as rows, then print the header in capitals, the number of "
                f"rows, and the last row, one to a line.", args)
    if want == "longest":
        return (f"Put these lines in one text with a newline between them: "
                f"{_lines_text(lines)}. Print the longest line and its length on one "
                f"line separated by a space.", args)
    if want == "clean":
        return (f"Take the text '{a['text']}' with its stray spaces. Print it with the "
                f"spaces tidied so that single spaces separate the words and none are "
                f"left at the ends, then on the next line print the length of the "
                f"original and the length of the tidy one separated by a space.", args)
    if want == "sum_csv":
        return (f"Put these csv-like lines in one text with a newline between them: "
                f"{_lines_text(lines)}. Skip the header line and print the sum of the "
                f"numbers after the comma on the other lines.", args)
    if want == "rpartition":
        return (f"For each file name in {_py(a['names'])}, split it at its last dot and "
                f"print the extension, a space and the name before it, one to a "
                f"line.", args)
    return (f"Put these lines in one text with a newline between them: "
            f"{_lines_text(lines)}. Strip each line, drop the blank ones and the "
            f"comments that start with #, and print how many lines are left and then "
            f"the list of them, on one line separated by a space.", args)


TEXT_PAGE = _page(
    "py-data-text", _FIRST + 9, "Data: a block of text",
    "A log or a csv file is a block of text: text.splitlines() cuts it into "
    "lines without the line breaks, line.split() cuts a line on runs of "
    "spaces and line.split(',') on one comma, and line.strip() takes the "
    "spaces off the ends. partition(sep) cuts at the first separator and "
    "always gives three pieces (before, the separator, after), so "
    "line.partition(' ') is safe even when the separator is missing, and "
    "rpartition cuts at the last one, which is how to get a file's extension. "
    "' '.join(text.split()) tidies spaces; str.upper() and len() do what they "
    "say. Unpack a head from the rest with header, *rows = lines. An f-string "
    "lays out a table: f'{name:<8}' pads on the right to a width of 8, "
    "f'{n:>5}' pads on the left, f'{name:^9}' centres, and f'{n:>8,}' adds "
    "commas between thousands. The spec is read as alignment, width, then "
    "the comma.",
    "text = 'ada,12\\nsam,7'; for line in text.splitlines(): name, qty = "
    "line.split(','); print(f'{name:<6}{qty:>4}') prints 'ada      12' and "
    "'sam       7'; 'a.b.txt'.rpartition('.') is ('a.b', '.', 'txt')",
    "py_data_text",
    tuple(_text_row(row) for row in _TEXTS),
)


PYDATA_PAGES: tuple[Page, ...] = (
    COUNTER_PAGE,
    GROUP_PAGE,
    RECORDS_PAGE,
    STATS_PAGE,
    CSV_PAGE,
    JSON_PAGE,
    DATES_PAGE,
    MONEY_PAGE,
    GRID_PAGE,
    TEXT_PAGE,
)
