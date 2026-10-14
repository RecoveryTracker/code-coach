"""Data practice in Python.

Ten pages of small programs that do the everyday jobs of working with data:
counting with Counter, grouping with defaultdict and groupby, a table of
records, the statistics module, csv text, JSON round trips, dates, money with
Decimal and Fraction, a grid of lists, and a block of text.

Everything is deterministic:

- dates are always fixed dates, never today;
- csv and JSON live in strings and io.StringIO, never in files, and a csv
  writer is always given lineterminator="\\n";
- numbers that are printed to a fixed number of decimals are held away from
  rounding ties (a tie in binary floating point can go either way), and the
  money page asks for ROUND_HALF_UP, which is exact and so allowed to tie;
- where Python promises an order (a Counter ties in the order the keys were
  first seen, a stable sort keeps equal keys in their input order, a dict
  remembers insertion order) the oracle follows the promise and says so.

The oracle never runs the Python it describes. Every answer is worked out
by small models written here, with nothing from the standard library but
re: a tally, a stable grouper, an exact decimal, a fraction reduced by
Euclid, a calendar from day numbers, a JSON writer and reader, a csv writer
and reader. The tests then hold python to it. A row that could print two
ways is refused with ValueError.
"""

from __future__ import annotations

import re

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("py_data_counter",
          "collections.Counter: counts, most_common and its ties, total, update and subtract"),
    Shape("py_data_group",
          "grouping with defaultdict, and with itertools.groupby after sorting"),
    Shape("py_data_records",
          "a table of records as a list of dicts: filter, sort on two keys, top N, totals"),
    Shape("py_data_stats",
          "the statistics module, printed to a fixed number of decimals"),
    Shape("py_data_csv",
          "csv text in io.StringIO: reader, DictReader and writer with lineterminator"),
    Shape("py_data_json",
          "json.dumps and json.loads: sort_keys, indent, separators and what a round trip changes"),
    Shape("py_data_dates",
          "fixed dates: differences, weekday names, month ends, ages and timedelta"),
    Shape("py_data_money",
          "Decimal with ROUND_HALF_UP for money, and Fraction for exact arithmetic"),
    Shape("py_data_grid",
          "a grid of lists: transpose with zip, row and column sums, flatten, diagonals"),
    Shape("py_data_text",
          "a text block: splitlines, strip, split, partition and an f-string table"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: How long a program may be: a small program, not a project.
LIMIT = 10


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Writing things the program types ─────────────────────────

#: Text that sits safely inside a double-quoted Python string.
_PLAIN = re.compile(r"[A-Za-z0-9 _.,:;/=@%+!?#()\-]+")
_WORD = re.compile(r"[a-z][a-z0-9_]*")
_LOWER = re.compile(r"[a-z]+")
_ALPHA = re.compile(r"[A-Za-z]+")


def _s(x) -> str:
    """A string literal. Quotes, backslashes and the like are refused."""
    if not isinstance(x, str) or not _PLAIN.fullmatch(x):
        raise ValueError(f"{x!r}: plain text only")
    return _q(x)


def _int(x) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: a whole number")
    return x


def _word(x) -> str:
    if not isinstance(x, str) or not _WORD.fullmatch(x):
        raise ValueError(f"{x!r}: one lowercase word")
    return x


def _fit(lines, limit: int = LIMIT) -> str:
    """The program, with blank lines dropped one by one if it runs long."""
    lines = list(lines)
    while len(lines) > limit and "" in lines:
        lines.remove("")
    if len(lines) > limit:
        raise ValueError(f"{len(lines)} lines is too many")
    return NL.join(lines)


def _lit(v) -> str:
    """A Python literal for a plain value."""
    if isinstance(v, bool) or v is None:
        return repr(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return _s(v)
    if isinstance(v, tuple):
        return "(" + ", ".join(_lit(i) for i in v) + ("," if len(v) == 1 else "") + ")"
    if isinstance(v, list):
        return "[" + ", ".join(_lit(i) for i in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{_lit(k)}: {_lit(x)}" for k, x in v.items()) + "}"
    raise ValueError(f"{v!r}: not a plain value")


def _repr(v) -> str:
    """What print shows for plain data, written out by hand."""
    if isinstance(v, bool) or v is None:
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        _s(v)
        return "'" + v + "'"
    if isinstance(v, tuple):
        return "(" + ", ".join(_repr(i) for i in v) + ("," if len(v) == 1 else "") + ")"
    if isinstance(v, list):
        return "[" + ", ".join(_repr(i) for i in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{_repr(k)}: {_repr(x)}" for k, x in v.items()) + "}"
    raise ValueError(f"{v!r}: not a plain value")


def _say(v) -> str:
    """What print shows for a single value."""
    if isinstance(v, (bool, int)) or v is None:
        return str(v)
    if isinstance(v, str):
        return v
    raise ValueError(f"{v!r}: not a single value")


def _words(items, minimum: int = 4) -> list[str]:
    items = list(items)
    if len(items) < minimum or any(
            not isinstance(w, str) or not _LOWER.fullmatch(w) for w in items):
        raise ValueError(f"lowercase words, {minimum} at least")
    return items


def _nums(items, minimum: int = 3, lo: int = 0, hi: int = 999) -> list[int]:
    items = list(items)
    if len(items) < minimum or any(
            isinstance(x, bool) or not isinstance(x, int) or not lo <= x <= hi
            for x in items):
        raise ValueError(f"whole numbers {lo} to {hi}, {minimum} at least")
    return items


def _pairs(pairs, numbers: bool = False, minimum: int = 4) -> list[tuple]:
    """Pairs of (word, word) or (word, whole number)."""
    pairs = [tuple(p) for p in pairs]
    if len(pairs) < minimum:
        raise ValueError(f"{minimum} pairs at least")
    for first, second in pairs:
        _words([first], 1)
        if numbers:
            _nums([second], 1)
        else:
            _words([second], 1)
    return pairs


def _tally(items) -> dict:
    """Counts in the order each item was first seen (a dict remembers it)."""
    out: dict = {}
    for x in items:
        out[x] = out.get(x, 0) + 1
    return out


def _fixed(num: int, den: int, digits: int) -> str:
    """num/den to `digits` places, half up, refusing a tie or near-tie.

    A tie rounds one way on paper and either way in binary floating point,
    so a row that lands on one would have two right answers.
    """
    if den <= 0 or num < 0:
        raise ValueError("a positive amount")
    q, r = divmod(num * 10 ** digits, den)
    if abs(2 * r - den) * 10 ** 6 < den:
        raise ValueError("a rounding tie")
    q += 1 if 2 * r > den else 0
    text = str(q).rjust(digits + 1, "0")
    return text[:-digits] + "." + text[-digits:] if digits else text


def _isqrt(n: int) -> int:
    """Integer square root by Newton's method."""
    if n < 2:
        return n
    x, y = n, (n + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x


def _unique(items, what: str = "values") -> list:
    items = list(items)
    if len(set(items)) != len(items):
        raise ValueError(f"{what} must be different")
    return items


# ── 1. Counter ───────────────────────────────────────────────

_CI = ["from collections import Counter", ""]


def _most_common(counts: dict) -> list[tuple]:
    """Counter.most_common: highest count first.

    Equal counts stay in the order they were first seen. Python promises
    that: a Counter is a dict, which remembers insertion order, and the sort
    behind most_common is stable.
    """
    return sorted(counts.items(), key=lambda kv: -kv[1])


def _counter(a: dict) -> str:
    want = a["want"]
    if want == "letters":
        return _fit([*_CI, f"text = {_s(a['text'])}",
                     "for letter, n in sorted(Counter(text).items()):",
                     "    print(letter, n)"])
    if want == "normalised":
        return _fit([*_CI, f"text = {_s(a['text'])}",
                     "counts = Counter(word.lower() for word in text.split())",
                     f"print(counts[{_s(a['word'])}])"])
    if want == "anagram":
        return _fit([*_CI, f"first = Counter({_s(a['a'])})",
                     f"second = Counter({_s(a['b'])})", "print(first == second)"])
    head = [*_CI, f"words = {_lit(_words(a['words']))}"]
    if want == "count":
        return _fit([*head, "counts = Counter(words)", f"print(counts[{_s(a['word'])}])"])
    if want == "missing":
        return _fit([*head, "counts = Counter(words)", f"print(counts[{_s(a['word'])}])",
                     "print(len(counts))"])
    if want == "top":
        return _fit([*head, "counts = Counter(words)",
                     f"for word, n in counts.most_common({_int(a['n'])}):",
                     "    print(word, n)"])
    if want == "best":
        return _fit([*head, "word, n = Counter(words).most_common(1)[0]", "print(word, n)"])
    if want == "least":
        return _fit([*head, "word, n = Counter(words).most_common()[-1]", "print(word, n)"])
    if want == "total":
        return _fit([*head, "counts = Counter(words)", "print(counts.total())",
                     "print(len(counts))"])
    if want == "repeated":
        return _fit([*head, "counts = Counter(words)",
                     'print(", ".join(sorted(word for word, n in counts.items() if n > 1)))'])
    if want == "update":
        return _fit([*head, f"more = {_lit(_words(a['more'], 2))}", "counts = Counter(words)",
                     "counts.update(more)", f"print(counts[{_s(a['word'])}])"])
    if want == "subtract":
        return _fit([*head, f"sold = {_lit(_words(a['sold'], 2))}", "stock = Counter(words)",
                     "stock.subtract(sold)", "print(sorted(stock.items()))"])
    raise ValueError(want)


def _counter_out(a: dict) -> str:
    want = a["want"]
    if want == "letters":
        text = a["text"]
        if not _LOWER.fullmatch(text) or not 5 <= len(text) <= 12:
            raise ValueError("five to twelve lowercase letters")
        t = _tally(text)
        if len(t) == len(text):
            raise ValueError("a letter that repeats")
        return NL.join(f"{k} {t[k]}" for k in sorted(t))
    if want == "normalised":
        words = a["text"].split(" ")
        if any(not _ALPHA.fullmatch(w) for w in words) or len(words) < 5:
            raise ValueError("five words or more, single spaces, letters only")
        target = _words([a["word"]], 1)[0]
        t = _tally(w.lower() for w in words)
        if t.get(target, 0) < 2 or sum(1 for w in words if w == target) == t[target]:
            raise ValueError("a word that the case changes the count of")
        return str(t[target])
    if want == "anagram":
        x, y = _words([a["a"], a["b"]], 2)
        if len(x) < 4 or len(x) != len(y) or x == y:
            raise ValueError("two different words of the same length, four letters or more")
        return str(_tally(x) == _tally(y))
    words = _words(a["words"])
    t = _tally(words)
    if want == "count":
        word = _words([a["word"]], 1)[0]
        if t.get(word, 0) < 2:
            raise ValueError("a word that is there more than once")
        return str(t[word])
    if want == "missing":
        word = _words([a["word"]], 1)[0]
        if word in t:
            raise ValueError("a word that is not there")
        return NL.join(["0", str(len(t))])
    if want == "top":
        n = _int(a["n"])
        if not 1 <= n < len(t) or len(words) == len(t):
            raise ValueError("fewer than all of the words, and some repeat")
        return NL.join(f"{w} {c}" for w, c in _most_common(t)[:n])
    if want == "best":
        if len(words) == len(t):
            raise ValueError("a word that repeats")
        w, c = _most_common(t)[0]
        return f"{w} {c}"
    if want == "least":
        ranked = _most_common(t)
        if len(t) < 3 or sum(1 for _, c in ranked if c == ranked[-1][1]) != 1:
            raise ValueError("one word that is rarest, and three words or more")
        return f"{ranked[-1][0]} {ranked[-1][1]}"
    if want == "total":
        if len(words) == len(t):
            raise ValueError("a word that repeats")
        return NL.join([str(len(words)), str(len(t))])
    if want == "repeated":
        found = sorted(w for w, c in t.items() if c > 1)
        if not found or len(found) == len(t):
            raise ValueError("some words repeat and some do not")
        return ", ".join(found)
    if want == "update":
        more = _words(a["more"], 2)
        word = _words([a["word"]], 1)[0]
        both = _tally([*words, *more])
        if word not in t or word not in more:
            raise ValueError("a word that is in both lists")
        return str(both[word])
    if want == "subtract":
        sold = _words(a["sold"], 2)
        stock = dict(t)
        for w in sold:
            stock[w] = stock.get(w, 0) - 1
        if not any(c == 0 for c in stock.values()) or not any(c < 0 for c in stock.values()):
            raise ValueError("one item sold out and one sold that was never in stock")
        return _repr(sorted(stock.items()))
    raise ValueError(want)


# ── 2. defaultdict and groupby ───────────────────────────────

_DD = ["from collections import defaultdict", ""]
_GB = ["from itertools import groupby", ""]
_KEY = "key=lambda row: row[0]"


def _group_by_hand(rows) -> list[tuple]:
    """groupby by hand: a new group wherever the key changes."""
    out: list[tuple] = []
    for row in rows:
        if out and out[-1][0] == row[0]:
            out[-1][1].append(row[1])
        else:
            out.append((row[0], [row[1]]))
    return out


def _sorted_rows(rows) -> list[tuple]:
    """Sorted on the first item only. The sort is stable, so equal keys
    keep the order they had."""
    return sorted(rows, key=lambda row: row[0])


def _dd_fill(pairs, kind: str) -> list[str]:
    body = {"list": "groups[team].append(name)", "int": "totals[item] += amount"}
    if kind == "list":
        return ["groups = defaultdict(list)", "for name, team in pairs:",
                f"    {body[kind]}"]
    return ["totals = defaultdict(int)", "for item, amount in pairs:", f"    {body[kind]}"]


def _group(a: dict) -> str:
    want = a["want"]
    if want in ("members", "sizes", "peek"):
        pairs = f"pairs = {_lit(_pairs(a['pairs']))}"
        fill = _dd_fill(a["pairs"], "list")
        if want == "peek":
            return _fit([*_DD, pairs, *fill, f"print(groups[{_s(a['team'])}])",
                         "print(len(groups))"])
        show = ('print(team + ":", ", ".join(groups[team]))' if want == "members"
                else "print(team, len(groups[team]))")
        return _fit([*_DD, pairs, *fill, "for team in sorted(groups):", f"    {show}"])
    if want == "totals":
        return _fit([*_DD, f"pairs = {_lit(_pairs(a['pairs'], numbers=True))}",
                     *_dd_fill(a["pairs"], "int"),
                     "for item in sorted(totals):", "    print(item, totals[item])"])
    if want == "by_length":
        return _fit([*_DD, f"words = {_lit(_words(a['words']))}", "groups = defaultdict(list)",
                     "for word in words:", "    groups[len(word)].append(word)",
                     "for size in sorted(groups):", '    print(size, " ".join(groups[size]))'])
    if want == "unique":
        return _fit([*_DD, f"pairs = {_lit(_pairs(a['pairs']))}", "tags = defaultdict(set)",
                     "for user, tag in pairs:", "    tags[user].add(tag)",
                     "for user in sorted(tags):",
                     '    print(user, ", ".join(sorted(tags[user])))'])
    if want == "invert":
        return _fit([*_DD, f"skills = {_lit(a['skills'])}", "by_skill = defaultdict(list)",
                     "for person, known in skills.items():", "    for skill in known:",
                     "        by_skill[skill].append(person)",
                     "for skill in sorted(by_skill):",
                     '    print(skill, ", ".join(by_skill[skill]))'])
    if want == "default":
        return _fit([*_DD, f"stock = defaultdict(int, {_lit(a['stock'])})",
                     f"print(stock[{_s(a['have'])}], stock[{_s(a['miss'])}])",
                     "print(len(stock))"])
    # groupby
    if want == "runs":
        text = a["text"]
        return _fit([*_GB, f"text = {_s(text)}",
                     'print("".join(f"{ch}{len(list(run))}" for ch, run in groupby(text)))'])
    if want == "buckets":
        return _fit([*_GB, f"numbers = {_lit(_nums(a['numbers'], 5, 0, 99))}",
                     "for tens, group in groupby(sorted(numbers), key=lambda n: n // 10):",
                     "    print(tens * 10, list(group))"])
    rows = f"rows = {_lit(_pairs(a['rows'], numbers=want != 'names'))}"
    if want == "dict_of_lists":
        return _fit([*_GB, rows, "groups = groupby(sorted(rows), key=lambda row: row[0])",
                     "print({key: [amount for _, amount in group] for key, group in groups})"])
    sort = [f"rows.sort({_KEY})"]
    loop = f"for key, group in groupby(rows, {_KEY}):"
    shows = {
        "sums": ["    print(key, sum(amount for _, amount in group))"],
        "counts": ["    print(key, len(list(group)))"],
        "biggest": ["    print(key, max(amount for _, amount in group))"],
        "unsorted": ["    print(key, sum(amount for _, amount in group))"],
        "averages": ["    amounts = [amount for _, amount in group]",
                     '    print(key, f"{sum(amounts) / len(amounts):.1f}")'],
        "names": ['    print(key + ":", ", ".join(name for _, name in group))'],
    }
    if want not in shows:
        raise ValueError(want)
    return _fit([*_GB, rows, *([] if want == "unsorted" else sort), loop, *shows[want]])


def _group_out(a: dict) -> str:
    want = a["want"]
    if want in ("members", "sizes", "peek"):
        pairs = _pairs(a["pairs"])
        groups: dict = {}
        for name, team in pairs:
            groups.setdefault(team, []).append(name)
        if len(groups) == len(pairs) or len(groups) < 2:
            raise ValueError("two groups at least, and one with more than one member")
        if want == "peek":
            team = _words([a["team"]], 1)[0]
            if team in groups:
                raise ValueError("a team that is not there")
            return NL.join(["[]", str(len(groups) + 1)])
        if want == "members":
            return NL.join(f"{t}: {', '.join(groups[t])}" for t in sorted(groups))
        return NL.join(f"{t} {len(groups[t])}" for t in sorted(groups))
    if want == "totals":
        pairs = _pairs(a["pairs"], numbers=True)
        totals: dict = {}
        for item, amount in pairs:
            totals[item] = totals.get(item, 0) + amount
        if len(totals) == len(pairs):
            raise ValueError("an item that repeats")
        return NL.join(f"{k} {totals[k]}" for k in sorted(totals))
    if want == "by_length":
        words = _words(a["words"])
        groups = {}
        for w in words:
            groups.setdefault(len(w), []).append(w)
        if len(groups) == len(words) or len(groups) < 2:
            raise ValueError("two lengths at least, and one shared")
        return NL.join(f"{k} {' '.join(groups[k])}" for k in sorted(groups))
    if want == "unique":
        pairs = _pairs(a["pairs"])
        tags: dict = {}
        for user, tag in pairs:
            tags.setdefault(user, set()).add(tag)
        if sum(len(v) for v in tags.values()) == len(pairs):
            raise ValueError("a tag given twice to the same user")
        return NL.join(f"{u} {', '.join(sorted(tags[u]))}" for u in sorted(tags))
    if want == "invert":
        skills = dict(a["skills"])
        inverted: dict = {}
        for person, known in skills.items():
            _words([person], 1)
            for skill in _words(known, 1):
                inverted.setdefault(skill, []).append(person)
        if len(skills) < 2 or len(inverted) < 2:
            raise ValueError("two people and two skills at least")
        return NL.join(f"{k} {', '.join(inverted[k])}" for k in sorted(inverted))
    if want == "default":
        stock = dict(a["stock"])
        _nums(stock.values(), 2, 0, 99)
        have, miss = _words([a["have"], a["miss"]], 2)
        if have not in stock or miss in stock:
            raise ValueError("one name that is there and one that is not")
        for k in stock:
            _words([k], 1)
        return NL.join([f"{stock[have]} 0", str(len(stock) + 1)])
    if want == "runs":
        text = a["text"]
        if not _LOWER.fullmatch(text) or len(text) < 6:
            raise ValueError("six lowercase letters or more")
        runs = _group_by_hand((ch, 1) for ch in text)
        if len(runs) == len(text):
            raise ValueError("a letter that repeats")
        return "".join(f"{k}{len(v)}" for k, v in runs)
    if want == "buckets":
        numbers = _nums(a["numbers"], 5, 0, 99)
        tens = _group_by_hand((n // 10, n) for n in sorted(numbers))
        if len(tens) < 2 or len(tens) == len(numbers):
            raise ValueError("two groups at least, one with several numbers")
        return NL.join(f"{k * 10} {_repr(v)}" for k, v in tens)
    names = want == "names"
    rows = _pairs(a["rows"], numbers=not names)
    if want == "unsorted":
        runs = _group_by_hand(rows)
        if len({k for k, _ in runs}) == len(runs):
            raise ValueError("a key that comes back, or sorting is not the point")
        return NL.join(f"{k} {sum(v)}" for k, v in runs)
    grouped = _group_by_hand(_sorted_rows(rows))
    if len(grouped) < 2 or len(grouped) == len(rows):
        raise ValueError("two groups at least, and one with several rows")
    if want == "sums":
        return NL.join(f"{k} {sum(v)}" for k, v in grouped)
    if want == "counts":
        return NL.join(f"{k} {len(v)}" for k, v in grouped)
    if want == "biggest":
        return NL.join(f"{k} {max(v)}" for k, v in grouped)
    if want == "averages":
        return NL.join(f"{k} {_fixed(sum(v), len(v), 1)}" for k, v in grouped)
    if want == "names":
        return NL.join(f"{k}: {', '.join(v)}" for k, v in grouped)
    if want == "dict_of_lists":
        sortedrows = sorted(rows)
        return _repr(dict(_group_by_hand(sortedrows)))
    raise ValueError(want)


# ── 3. A table of records ────────────────────────────────────


def _table(rows, minimum: int = 4) -> list[dict]:
    rows = [dict(r) for r in rows]
    if len(rows) < minimum:
        raise ValueError(f"{minimum} records at least")
    keys = list(rows[0])
    if len(keys) < 3:
        raise ValueError("three fields at least")
    for k in keys:
        _word(k)
    for r in rows:
        if list(r) != keys:
            raise ValueError("every record has the same fields, in the same order")
        for v in r.values():
            if isinstance(v, bool) or not isinstance(v, (int, str)):
                raise ValueError("text or a whole number")
            if isinstance(v, str):
                _s(v)
            elif v < 0:
                raise ValueError("no negative numbers")
    if len({r[keys[0]] for r in rows}) != len(rows):
        raise ValueError("the first field names the record: all different")
    return rows


def _field(rows, key, number: bool) -> str:
    _word(key)
    if key not in rows[0]:
        raise ValueError(f"{key!r}: not a field")
    if number != isinstance(rows[0][key], int):
        raise ValueError(f"{key!r}: wrong kind of field")
    return key


def _rec(key: str) -> str:
    return f'row["{key}"]'


def _records(a: dict) -> str:
    want = a["want"]
    rows = _table(a["rows"])
    label = _rec(next(iter(rows[0])))
    head = f"rows = {_lit(rows)}"
    if want == "filter":
        return _fit([head,
                     f"names = [{label} for row in rows if {_rec(a['key'])} > {_int(a['limit'])}]",
                     'print(", ".join(names))'])
    if want == "match":
        return _fit([head,
                     f"names = [{label} for row in rows if {_rec(a['key'])} == {_s(a['value'])}]",
                     'print(", ".join(names))'])
    if want == "two_filter":
        return _fit([head,
                     f"names = [{label} for row in rows if {_rec(a['key'])} == {_s(a['value'])} "
                     f"and {_rec(a['key2'])} >= {_int(a['limit'])}]",
                     'print(", ".join(names))'])
    if want == "sort1":
        rev = ", reverse=True" if a["reverse"] else ""
        return _fit([head, f"ranked = sorted(rows, key=lambda row: {_rec(a['key'])}{rev})",
                     f'print(", ".join({label} for row in ranked))'])
    if want == "sort2":
        second = ("-" if a["desc"] else "") + _rec(a["second"])
        return _fit([head,
                     f"ranked = sorted(rows, key=lambda row: ({_rec(a['first'])}, {second}))",
                     "for row in ranked:",
                     f"    print({label}, {_rec(a['first'])}, {_rec(a['second'])})"])
    if want == "top":
        return _fit([head,
                     f"best = sorted(rows, key=lambda row: {_rec(a['key'])}, "
                     f"reverse=True)[:{_int(a['n'])}]",
                     f'print(", ".join({label} for row in best))'])
    if want == "best":
        fn = "max" if a["how"] == "max" else "min"
        return _fit([head, f"pick = {fn}(rows, key=lambda row: {_rec(a['key'])})",
                     f'print(pick["{next(iter(rows[0]))}"])'])
    if want in ("total_of", "average_of"):
        cond = f"if {_rec(a['by'])} == {_s(a['value'])}"
        if want == "total_of":
            return _fit([head, f"values = [{_rec(a['key'])} for row in rows {cond}]",
                         "print(sum(values))"])
        return _fit([head, f"values = [{_rec(a['key'])} for row in rows {cond}]",
                     'print(f"{sum(values) / len(values):.1f}")'])
    if want == "count_of":
        return _fit([head,
                     f"found = [row for row in rows if {_rec(a['key'])} > {_int(a['limit'])}]",
                     "print(len(found))"])
    if want == "lookup":
        first = next(iter(rows[0]))
        return _fit([head, f'by_{first} = {{{label}: row for row in rows}}',
                     f"print(by_{first}[{_s(a['name'])}][{_s(a['field'])}])"])
    if want == "raise":
        return _fit([head, "for row in rows:",
                     f"    if {_rec(a['by'])} == {_s(a['value'])}:",
                     f"        {_rec(a['key'])} += {_int(a['step'])}",
                     f"print(sum({_rec(a['key'])} for row in rows))"])
    if want == "column":
        return _fit([head, f"values = [{_rec(a['key'])} for row in rows]", "print(values)",
                     "print(max(values) - min(values))"])
    if want == "unique":
        return _fit([head, f"kinds = sorted({{{_rec(a['key'])} for row in rows}})",
                     'print(", ".join(kinds))', "print(len(kinds))"])
    raise ValueError(want)


def _records_out(a: dict) -> str:
    want = a["want"]
    rows = _table(a["rows"])
    label = next(iter(rows[0]))

    def names(kept) -> str:
        return ", ".join(r[label] for r in kept)

    if want == "filter":
        key, limit = _field(rows, a["key"], True), _int(a["limit"])
        kept = [r for r in rows if r[key] > limit]
        if not kept or len(kept) == len(rows):
            raise ValueError("a limit that keeps some and drops some")
        return names(kept)
    if want in ("match", "two_filter"):
        key = _field(rows, a["key"], False)
        value = a["value"]
        kept = [r for r in rows if r[key] == value]
        if want == "match":
            if not kept or len(kept) == len(rows):
                raise ValueError("a value that keeps some and drops some")
            return names(kept)
        key2, limit = _field(rows, a["key2"], True), _int(a["limit"])
        both = [r for r in kept if r[key2] >= limit]
        if not both or len(both) == len(kept) or len(kept) == len(rows):
            raise ValueError("the second test has to drop one of the first test's rows")
        return names(both)
    if want == "sort1":
        key = _field(rows, a["key"], True)
        if len({r[key] for r in rows}) != len(rows):
            raise ValueError("all different, or the order of ties is a puzzle")
        ranked = sorted(rows, key=lambda r: r[key], reverse=bool(a["reverse"]))
        return names(ranked)
    if want == "sort2":
        first = _field(rows, a["first"], isinstance(rows[0][a["first"]], int))
        second = _field(rows, a["second"], True)
        pairs = [(r[first], r[second]) for r in rows]
        if len(set(pairs)) != len(pairs) or len({p[0] for p in pairs}) == len(pairs):
            raise ValueError("no tie on both keys, and a first key that repeats")
        sign = -1 if a["desc"] else 1
        ranked = sorted(rows, key=lambda r: (r[first], sign * r[second]))
        return NL.join(f"{r[label]} {r[first]} {r[second]}" for r in ranked)
    if want == "top":
        key, n = _field(rows, a["key"], True), _int(a["n"])
        if not 1 <= n < len(rows) or len({r[key] for r in rows}) != len(rows):
            raise ValueError("all different, and fewer than all of them")
        return names(sorted(rows, key=lambda r: r[key], reverse=True)[:n])
    if want == "best":
        key = _field(rows, a["key"], True)
        hi = max(r[key] for r in rows) if a["how"] == "max" else min(r[key] for r in rows)
        found = [r for r in rows if r[key] == hi]
        if a["how"] not in ("max", "min") or len(found) != 1:
            raise ValueError("one record at the extreme")
        return found[0][label]
    if want in ("total_of", "average_of", "raise"):
        key, by = _field(rows, a["key"], True), _field(rows, a["by"], False)
        chosen = [r[key] for r in rows if r[by] == a["value"]]
        if want == "total_of":
            if len(chosen) < 2 or len(chosen) == len(rows):
                raise ValueError("a group of several, not the whole table")
            return str(sum(chosen))
        if want == "average_of":
            if len(chosen) < 2 or len(chosen) == len(rows):
                raise ValueError("a group of several, not the whole table")
            return _fixed(sum(chosen), len(chosen), 1)
        step = _int(a["step"])
        if not chosen or not step:
            raise ValueError("a group that is there, and a raise that does something")
        return str(sum(r[key] for r in rows) + step * len(chosen))
    if want == "count_of":
        key, limit = _field(rows, a["key"], True), _int(a["limit"])
        found = [r for r in rows if r[key] > limit]
        if not found or len(found) == len(rows):
            raise ValueError("a limit that keeps some and drops some")
        return str(len(found))
    if want == "lookup":
        by_label = {r[label]: r for r in rows}
        if a["name"] not in by_label or a["field"] not in rows[0]:
            raise ValueError("a record and a field that are there")
        return _say(by_label[a["name"]][a["field"]])
    if want == "column":
        key = _field(rows, a["key"], True)
        values = [r[key] for r in rows]
        if max(values) == min(values):
            raise ValueError("values that differ")
        return NL.join([_repr(values), str(max(values) - min(values))])
    if want == "unique":
        key = _field(rows, a["key"], False)
        kinds = sorted({r[key] for r in rows})
        if len(kinds) == len(rows) or len(kinds) < 2:
            raise ValueError("a field that repeats")
        return NL.join([", ".join(kinds), str(len(kinds))])
    raise ValueError(want)


# ── 4. statistics ────────────────────────────────────────────

_SI = ["import statistics", ""]


def _spread(data: list[int]) -> tuple[int, int, int]:
    """n, the sum, and n * sum of squares - sum squared (n² times the
    population variance), all whole numbers, so nothing is rounded."""
    n, s = len(data), sum(data)
    return n, s, n * sum(x * x for x in data) - s * s


def _root_fixed(N: int, M: int, digits: int) -> str:
    """sqrt(N / M) to `digits` places, from whole numbers only."""
    t = _isqrt(N * M * 10 ** 24)
    return _fixed(t, M * 10 ** 12, digits)


def _digits(a: dict) -> int:
    d = _int(a["digits"])
    if d not in (1, 2):
        raise ValueError("one or two decimals")
    return d


def _stats(a: dict) -> str:
    want = a["want"]
    if want == "mode_words":
        return _fit([*_SI, f"words = {_lit(_words(a['words']))}", "print(statistics.mode(words))"])
    data = f"data = {_lit(_nums(a['data']))}"
    if want in ("mean", "median", "pstdev", "stdev", "pvariance", "variance"):
        shown = "{statistics." + want + "(data):." + str(_digits(a)) + "f}"
        return _fit([*_SI, data, 'print(f"' + shown + '")'])
    if want == "mode":
        return _fit([*_SI, data, "print(statistics.mode(data))"])
    if want == "multimode":
        return _fit([*_SI, data, "print(statistics.multimode(data))"])
    if want == "low_high":
        return _fit([*_SI, data, "print(statistics.median_low(data), statistics.median_high(data))"])
    if want == "quantiles":
        return _fit([*_SI, data, 'print(" ".join(f"{q:.2f}" for q in statistics.quantiles(data)))'])
    if want == "trimmed":
        return _fit([*_SI, data, "middle = sorted(data)[1:-1]",
                     'print(f"{statistics.mean(middle):.' + str(_digits(a)) + 'f}")'])
    if want == "above":
        return _fit([*_SI, data, "mean = statistics.mean(data)",
                     "print(sum(1 for x in data if x > mean))"])
    if want == "outliers":
        return _fit([*_SI, data, "mean = statistics.mean(data)", "sd = statistics.pstdev(data)",
                     f'print([x for x in data if abs(x - mean) > {_int(a["k"])} * sd] or "none")'])
    raise ValueError(want)


def _stats_out(a: dict) -> str:
    want = a["want"]
    if want == "mode_words":
        words = _words(a["words"])
        t = _tally(words)
        top = max(t.values())
        best = [w for w, c in t.items() if c == top]
        if len(best) != 1 or top < 2:
            raise ValueError("one word that is the most common")
        return best[0]
    data = _nums(a["data"])
    n, s, N = _spread(data)
    ordered = sorted(data)
    if want == "mean":
        return _fixed(s, n, _digits(a))
    if want == "median":
        mid = n // 2
        top = ordered[mid] * 2 if n % 2 else ordered[mid - 1] + ordered[mid]
        if _digits(a) != 1:
            raise ValueError("one decimal for a median")
        return _fixed(top, 2, 1)
    if want in ("pstdev", "stdev", "pvariance", "variance"):
        sample = want in ("stdev", "variance")
        if n < 2 or (sample and n < 3):
            raise ValueError("more data")
        if len(set(data)) < 2:
            raise ValueError("data that varies")
        M = n * (n - 1) if sample else n * n
        if want.endswith("stdev"):
            return _root_fixed(N, M, _digits(a))
        return _fixed(N, M, _digits(a))
    tally = _tally(data)
    top = max(tally.values())
    modes = [x for x, c in tally.items() if c == top]
    if want == "mode":
        if len(modes) != 1 or top < 2:
            raise ValueError("one value that is the most common")
        return str(modes[0])
    if want == "multimode":
        if len(modes) < 2 or top < 2:
            raise ValueError("a tie, which multimode lists in the order first seen")
        return _repr(modes)
    if want == "low_high":
        if n % 2 or ordered[n // 2 - 1] == ordered[n // 2]:
            raise ValueError("an even count with different middles")
        return f"{ordered[n // 2 - 1]} {ordered[n // 2]}"
    if want == "quantiles":
        if n < 5:
            raise ValueError("five values at least")
        out = []
        for i in (1, 2, 3):
            scaled = i * (n + 1)
            j, delta = scaled // 4, scaled % 4
            if not 1 <= j < n:
                raise ValueError("a quartile inside the data")
            out.append(_fixed(ordered[j - 1] * (4 - delta) + ordered[j] * delta, 4, 2))
        return " ".join(out)
    if want == "trimmed":
        if n < 4:
            raise ValueError("four values at least")
        return _fixed(sum(ordered[1:-1]), n - 2, _digits(a))
    if want == "above":
        found = sum(1 for x in data if n * x > s)
        if found in (0, n) or any(n * x == s for x in data):
            raise ValueError("some above, some below, none exactly on it")
        return str(found)
    if want == "outliers":
        k = _int(a["k"])
        if k not in (1, 2) or len(set(data)) < 2:
            raise ValueError("k of 1 or 2, and data that varies")
        out = []
        for x in data:
            lhs, rhs = (n * x - s) ** 2, k * k * N
            if abs(lhs - rhs) * 10 ** 9 < max(rhs, 1):
                raise ValueError("a value right on the line")
            if lhs > rhs:
                out.append(x)
        return _repr(out) if out else "none"
    raise ValueError(want)


# ── 5. csv ───────────────────────────────────────────────────

_CSVH = ["import csv", "import io", ""]


def _cfield(x, quoted_ok: bool = False) -> str:
    if not isinstance(x, str) or not x:
        raise ValueError(f"{x!r}: text, not empty")
    if not _PLAIN.fullmatch(x.replace('"', "") if quoted_ok else x):
        raise ValueError(f"{x!r}: plain text")
    return x


def _csv_rows(rows, quoted_ok: bool = False, minimum: int = 4) -> list[list[str]]:
    rows = [list(r) for r in rows]
    if len(rows) < minimum or len({len(r) for r in rows}) != 1 or len(rows[0]) < 2:
        raise ValueError("a header and three rows at least, all the same width")
    for r in rows:
        for f in r:
            _cfield(f, quoted_ok)
    return rows


def _csv_text(rows, delim: str = ",") -> str:
    """The rows written as a csv writer writes them: a field is quoted only
    when it holds the delimiter, a quote or a line break."""
    def one(f: str) -> str:
        if any(c in f for c in (delim, '"', "\n", "\r")):
            return '"' + f.replace('"', '""') + '"'
        return f
    return "".join(delim.join(one(f) for f in r) + "\n" for r in rows)


def _csv_read(text: str, delim: str = ",") -> list[list[str]]:
    """A csv reader by hand: quoted fields, doubled quotes."""
    rows, row, field, i, quoted = [], [], "", 0, False
    while i < len(text):
        ch = text[i]
        if quoted:
            if ch == '"':
                if text[i + 1:i + 2] == '"':
                    field += '"'
                    i += 1
                else:
                    quoted = False
            else:
                field += ch
        elif ch == '"' and not field:
            quoted = True
        elif ch == delim:
            row.append(field)
            field = ""
        elif ch == "\n":
            row.append(field)
            rows.append(row)
            row, field = [], ""
        else:
            field += ch
        i += 1
    if field or row:
        row.append(field)
        rows.append(row)
    return rows


def _csv_load(rows, quoted_ok: bool = False, delim: str = ","):
    rows = _csv_rows(rows, quoted_ok)
    if _csv_read(_csv_text(rows, delim), delim) != rows:
        raise ValueError("the table does not survive being written and read")
    return rows


def _col(rows, name, number: bool) -> int:
    if name not in rows[0]:
        raise ValueError(f"{name!r}: not a column")
    i = rows[0].index(name)
    if number != all(re.fullmatch(r"\d+", r[i]) for r in rows[1:]):
        raise ValueError(f"{name!r}: wrong kind of column")
    return i


def _reader() -> str:
    return "csv.DictReader(io.StringIO(text))"


def _csv(a: dict) -> str:
    want = a["want"]
    delim = ";" if want == "semicolon" else ","
    rows = _csv_rows(a["rows"], want == "quoted" or want == "semicolon")
    text = f"text = {_text_lit(_csv_text(rows, delim))}"
    head = [*_CSVH, text]
    out = ["out = io.StringIO()"]
    show = 'print(out.getvalue(), end="")'
    writer = 'csv.writer(out, lineterminator="\\n")'
    col = a.get("col")
    if want == "fieldnames":
        return _fit([*head, f"reader = {_reader()}", "print(reader.fieldnames)"])
    if want == "first_row":
        return _fit([*head, f"reader = {_reader()}", "print(next(reader))"])
    if want == "header_body":
        return _fit([*head, "header, *body = csv.reader(io.StringIO(text))", "print(header)",
                     "print(len(body))"])
    if want == "count_where":
        return _fit([*head, f"rows = list({_reader()})",
                     f'print(sum(1 for row in rows if int(row["{col}"]) > {_int(a["limit"])}))'])
    if want == "unique":
        return _fit([*head, f"rows = list({_reader()})",
                     f'print(", ".join(sorted({{row["{col}"] for row in rows}})))'])
    if want == "average":
        return _fit([*head, f"rows = list({_reader()})",
                     f'values = [int(row["{col}"]) for row in rows]',
                     f'print(f"{{sum(values) / len(values):.{_digits(a)}f}}")'])
    if want == "max_row":
        return _fit([*head, f"rows = list({_reader()})",
                     f'best = max(rows, key=lambda row: int(row["{col}"]))',
                     f'print(best["{a["show"]}"])'])
    if want == "string_max":
        return _fit([*head, f"rows = list({_reader()})",
                     f'print(max(row["{col}"] for row in rows))'])
    if want == "filter_write":
        return _fit([*head, f"reader = {_reader()}", *out,
                     'writer = csv.DictWriter(out, fieldnames=reader.fieldnames, '
                     'lineterminator="\\n")',
                     "writer.writeheader()",
                     f'writer.writerows(row for row in reader if int(row["{col}"]) '
                     f'> {_int(a["limit"])})', show])
    if want == "computed":
        x, y = a["cols"]
        return _fit([*head, *out, f"writer = {writer}",
                     f"for row in {_reader()}:",
                     f'    writer.writerow([row["{a["show"]}"], int(row["{x}"]) * int(row["{y}"])])',
                     show])
    if want == "sorted_write":
        return _fit([*head,
                     f'rows = sorted({_reader()}, key=lambda row: int(row["{col}"]), '
                     "reverse=True)",
                     *out, f"writer = {writer}",
                     f'writer.writerows([row["{a["show"]}"], row["{col}"]] for row in rows)',
                     show])
    if want == "group_write":
        key = a["key"]
        return _fit([*head, "totals = {}", f"for row in {_reader()}:",
                     f'    totals[row["{key}"]] = totals.get(row["{key}"], 0) + int(row["{col}"])',
                     *out, f"{writer}.writerows(sorted(totals.items()))", show])
    if want == "quoted":
        return _fit([*head, "rows = list(csv.reader(io.StringIO(text)))",
                     f"print(len(rows[{_int(a['row'])}]))",
                     f"print(rows[{a['row']}][{_int(a['col'])}])"])
    if want == "semicolon":
        return _fit([*head, 'rows = list(csv.reader(io.StringIO(text), delimiter=";"))',
                     f"print(len(rows[{_int(a['row'])}]))",
                     f"print(rows[{a['row']}][{_int(a['col'])}])"])
    raise ValueError(want)


def _text_lit(text: str) -> str:
    """A program's string literal for a block of text: lines end in \\n."""
    quote = '"' if '"' not in text else "'"
    if quote == "'" and "'" in text:
        raise ValueError("one kind of quote")
    return quote + text.replace("\n", "\\n") + quote


def _csv_out(a: dict) -> str:
    want = a["want"]
    delim = ";" if want == "semicolon" else ","
    rows = _csv_load(a["rows"], want in ("quoted", "semicolon"), delim)
    header, body = rows[0], rows[1:]
    records = [dict(zip(header, r)) for r in body]
    if want == "fieldnames":
        return _repr(header)
    if want == "first_row":
        return _repr(records[0])
    if want == "header_body":
        return NL.join([_repr(header), str(len(body))])
    if want in ("quoted", "semicolon"):
        r, c = _int(a["row"]), _int(a["col"])
        if not 1 <= r < len(rows) or not 0 <= c < len(header):
            raise ValueError("a cell that is there")
        special = (",", '"') if want == "quoted" else (",",)
        if not any(ch in rows[r][c] for ch in special):
            raise ValueError("a cell that needs the quoting, or the delimiter, to be right")
        if want == "semicolon" and any(";" in f for row in rows for f in row):
            raise ValueError("no semicolon inside a field")
        return NL.join([str(len(rows[r])), rows[r][c]])
    if any("," in f or '"' in f for r in rows for f in r):
        raise ValueError("plain fields on the dictionary rows")
    col = a.get("col")
    if want == "unique":
        i = _col(rows, col, False)
        kinds = sorted({r[i] for r in body})
        if len(kinds) == len(body):
            raise ValueError("a column that repeats")
        return ", ".join(kinds)
    if want == "group_write":
        i, k = _col(rows, col, True), _col(rows, a["key"], False)
        totals: dict = {}
        for r in body:
            totals[r[k]] = totals.get(r[k], 0) + int(r[i])
        if len(totals) == len(body):
            raise ValueError("a key that repeats")
        return NL.join(f"{key},{totals[key]}" for key in sorted(totals))
    if want == "computed":
        x, y = (_col(rows, c, True) for c in a["cols"])
        s = _col(rows, a["show"], False)
        return NL.join(f"{r[s]},{int(r[x]) * int(r[y])}" for r in body)
    i = _col(rows, col, want != "unique")
    values = [int(r[i]) for r in body] if want != "string_max" else [r[i] for r in body]
    if want == "count_where":
        limit = _int(a["limit"])
        found = sum(1 for v in values if v > limit)
        if not 0 < found < len(values):
            raise ValueError("a limit that keeps some and drops some")
        return str(found)
    if want == "average":
        return _fixed(sum(values), len(values), _digits(a))
    if want == "max_row":
        hi = max(values)
        if values.count(hi) != 1:
            raise ValueError("one row with the most")
        return body[values.index(hi)][_col(rows, a["show"], False)]
    if want == "string_max":
        top = values[0]
        for v in values[1:]:
            if _lex_after(v, top):
                top = v
        if int(top) == max(int(v) for v in values):
            raise ValueError("the longest number is not the biggest: that is the point")
        return top
    if want == "filter_write":
        limit = _int(a["limit"])
        kept = [r for r, v in zip(body, values) if v > limit]
        if not 0 < len(kept) < len(body):
            raise ValueError("a limit that keeps some and drops some")
        return _csv_text([header, *kept]).rstrip("\n")
    if want == "sorted_write":
        if len(set(values)) != len(values):
            raise ValueError("all different, so the order has no ties")
        s = _col(rows, a["show"], False)
        order = sorted(range(len(body)), key=lambda j: -values[j])
        return _csv_text([[body[j][s], body[j][i]] for j in order]).rstrip("\n")
    raise ValueError(want)


def _lex_after(x: str, y: str) -> bool:
    """x sorts after y, character by character, as strings compare."""
    for p, q in zip(x, y):
        if p != q:
            return ord(p) > ord(q)
    return len(x) > len(y)


# ── 6. JSON ──────────────────────────────────────────────────


def _check_json(v) -> None:
    """Refuse what the hand-written writer and the library might split on."""
    if v is None or isinstance(v, bool):
        return
    if isinstance(v, str):
        _s(v)
        return
    if isinstance(v, int):
        if abs(v) >= 2 ** 31:
            raise ValueError("a modest number")
        return
    if isinstance(v, (list, tuple)):
        for x in v:
            _check_json(x)
        return
    if isinstance(v, dict):
        for k, x in v.items():
            if not isinstance(k, (str, int)) or isinstance(k, bool):
                raise ValueError(f"{k!r}: a text or number key")
            if isinstance(k, str):
                _s(k)
            _check_json(x)
        return
    raise ValueError(f"{v!r}: no floats here")


def _jsonify(v):
    """What JSON keeps of a value: tuples become lists, keys become text."""
    if isinstance(v, (list, tuple)):
        return [_jsonify(x) for x in v]
    if isinstance(v, dict):
        out = {str(k): _jsonify(x) for k, x in v.items()}
        if len(out) != len(v):
            raise ValueError("keys that stay different as text")
        return out
    return v


def _dump(v, indent: int | None = None, sort: bool = False, level: int = 0,
          sep: tuple[str, str] = (", ", ": ")) -> str:
    """json.dumps by hand. A value must already be JSON (see _jsonify)."""
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, list):
        if not v:
            return "[]"
        items = [_dump(x, indent, sort, level + 1, sep) for x in v]
        open_, close = "[", "]"
    else:
        if not v:
            return "{}"
        keys = sorted(v) if sort else list(v)
        items = [f'"{k}"{sep[1]}' + _dump(v[k], indent, sort, level + 1, sep) for k in keys]
        open_, close = "{", "}"
    if indent is None:
        return open_ + sep[0].join(items) + close
    pad = " " * (indent * (level + 1))
    return open_ + "\n" + ",\n".join(pad + i for i in items) + "\n" + " " * (indent * level) + close


class _Bad(ValueError):
    """Text a strict JSON reader refuses."""


def _parse(text: str):
    """A strict JSON reader: no trailing commas, double quotes only."""
    pos = 0

    def skip() -> None:
        nonlocal pos
        while pos < len(text) and text[pos] in " \t\n\r":
            pos += 1

    def string() -> str:
        nonlocal pos
        if text[pos:pos + 1] != '"':
            raise _Bad("a string")
        end = text.find('"', pos + 1)
        if end < 0:
            raise _Bad("unterminated")
        out = text[pos + 1:end]
        pos = end + 1
        return out

    def value():
        nonlocal pos
        skip()
        ch = text[pos:pos + 1]
        if ch == "{":
            pos += 1
            out: dict = {}
            skip()
            if text[pos:pos + 1] == "}":
                pos += 1
                return out
            while True:
                skip()
                key = string()
                skip()
                if text[pos:pos + 1] != ":":
                    raise _Bad(":")
                pos += 1
                if key in out:
                    raise ValueError("a repeated key")
                out[key] = value()
                skip()
                nxt = text[pos:pos + 1]
                pos += 1
                if nxt == "}":
                    return out
                if nxt != ",":
                    raise _Bad(", or }")
        if ch == "[":
            pos += 1
            items: list = []
            skip()
            if text[pos:pos + 1] == "]":
                pos += 1
                return items
            while True:
                items.append(value())
                skip()
                nxt = text[pos:pos + 1]
                pos += 1
                if nxt == "]":
                    return items
                if nxt != ",":
                    raise _Bad(", or ]")
        if ch == '"':
            return string()
        for word, val in (("true", True), ("false", False), ("null", None)):
            if text.startswith(word, pos):
                pos += len(word)
                return val
        m = re.compile(r"-?(0|[1-9][0-9]*)").match(text, pos)
        if not m:
            raise _Bad("a value")
        pos = m.end()
        if text[pos:pos + 1] in (".", "e", "E"):
            raise ValueError("no floats here")
        return int(m.group())

    result = value()
    skip()
    if pos != len(text):
        raise _Bad("extra text")
    return result


def _json_lit(text: str) -> str:
    """JSON text as a Python literal, in whichever quote it does not hold."""
    if not re.fullmatch(r"[A-Za-z0-9 _.,:{}\[\]\"'-]+", text) or ("'" in text and '"' in text):
        raise ValueError(f"{text!r}: plain JSON-ish text, one kind of quote")
    return repr(text)


def _rows_text(rows) -> str:
    """The records of the total and filter exercises, as compact-ish JSON."""
    rows = [dict(r) for r in rows]
    if len(rows) < 3:
        raise ValueError("three records at least")
    for r in rows:
        if list(r) != ["item", "price", "qty"]:
            raise ValueError("item, price, qty")
        _check_json(r)
    return _dump(rows)


def _json(a: dict) -> str:
    want = a["want"]
    head = ["import json", ""]
    if want in ("dumps_sorted", "dumps_indent", "compact"):
        obj = f"data = {_lit(a['obj'])}"
        option = {"dumps_sorted": "sort_keys=True",
                  "dumps_indent": f"indent={_int(a.get('indent', 2))}, sort_keys=True",
                  "compact": 'separators=(",", ":")'}[want]
        return _fit([*head, obj, f"print(json.dumps(data, {option}))"])
    if want == "loads_path":
        path = "".join(f"[{_lit(p)}]" for p in a["path"])
        return _fit([*head, f"text = {_json_lit(_dump(a['obj']))}", "data = json.loads(text)",
                     f"print(data{path})"])
    if want == "types":
        keys = list(a["keys"])
        return _fit([*head, f"text = {_json_lit(_dump(a['obj']))}", "data = json.loads(text)",
                     "print(" + ", ".join(f"data[{_s(k)}]" for k in keys) + ")"])
    if want == "round_trip":
        return _fit([*head, f"original = {_lit(a['obj'])}",
                     "back = json.loads(json.dumps(original))", "print(back)",
                     "print(back == original)"])
    if want == "total":
        return _fit([*head, f"text = {_json_lit(_rows_text(a['rows']))}", "rows = json.loads(text)",
                     'print(sum(row["price"] * row["qty"] for row in rows))'])
    if want == "filter_dump":
        return _fit([*head, f"text = {_json_lit(_rows_text(a['rows']))}", "rows = json.loads(text)",
                     f'print(json.dumps([row for row in rows if row["qty"] > {_int(a["limit"])}]))'])
    if want == "update_dump":
        return _fit([*head, f"text = {_json_lit(_dump(a['obj']))}", "data = json.loads(text)",
                     f'data[{_s(a["key"])}] += {_int(a["step"])}',
                     f"data[{_s(a['new'])}] = {_lit(a['value'])}",
                     "print(json.dumps(data, sort_keys=True))"])
    if want == "valid":
        return _fit([*head, f"text = {_json_lit(a['text'])}", "try:",
                     "    print(json.loads(text))", "except json.JSONDecodeError:",
                     '    print("bad")'])
    raise ValueError(want)


def _json_out(a: dict) -> str:
    want = a["want"]
    if want in ("dumps_sorted", "dumps_indent", "compact"):
        obj = dict(a["obj"])
        _check_json(obj)
        if want == "compact":
            return _dump(obj, sep=(",", ":"))
        if list(obj) == sorted(obj) or len(obj) < 3:
            raise ValueError("three keys, out of order")
        if want == "dumps_sorted":
            return _dump(obj, sort=True)
        indent = _int(a.get("indent", 2))
        if indent not in (2, 4) or not any(isinstance(v, (list, dict)) and v
                                           for v in obj.values()):
            raise ValueError("an indent of 2 or 4, and something nested")
        return _dump(obj, indent=indent, sort=True)
    if want in ("loads_path", "types"):
        obj = a["obj"]
        _check_json(obj)
        if any(isinstance(k, int) for k in obj):
            raise ValueError("text keys")
        if want == "types":
            keys = list(a["keys"])
            vals = [obj[k] for k in keys]
            if not any(v is None or isinstance(v, bool) for v in vals) or len(keys) < 2:
                raise ValueError("a true, false or null among two values")
            return " ".join(_say(v) for v in vals)
        v = obj
        for p in a["path"]:
            v = v[p]
        if isinstance(v, (list, dict)):
            raise ValueError("one value at the end of the path")
        if len(a["path"]) < 2:
            raise ValueError("a path of two steps at least")
        return _say(v)
    if want == "round_trip":
        obj = a["obj"]
        _check_json(obj)
        back = _jsonify(obj)
        return NL.join([_repr(back), str(_same(obj, back))])
    if want in ("total", "filter_dump"):
        rows = [dict(r) for r in a["rows"]]
        _rows_text(rows)
        if want == "total":
            return str(sum(r["price"] * r["qty"] for r in rows))
        limit = _int(a["limit"])
        kept = [r for r in rows if r["qty"] > limit]
        if not 0 < len(kept) < len(rows):
            raise ValueError("a limit that keeps some and drops some")
        return _dump(kept)
    if want == "update_dump":
        obj = dict(a["obj"])
        _check_json(obj)
        key, step = a["key"], _int(a["step"])
        new = _word(a["new"])
        if not isinstance(obj.get(key), int) or isinstance(obj[key], bool) or not step:
            raise ValueError("a number to add to, and a step that does something")
        if new in obj:
            raise ValueError("a new key")
        _check_json(a["value"])
        obj[key] += step
        obj[new] = a["value"]
        return _dump(obj, sort=True)
    if want == "valid":
        text = a["text"]
        try:
            return _repr(_parse(text))
        except _Bad:
            return "bad"
    raise ValueError(want)


def _same(a, b) -> bool:
    """Equal and the same kinds all the way down: a tuple is not a list and
    1 is not "1"."""
    if type(a) is not type(b):
        return False
    if isinstance(a, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return (len(a) == len(b) and all(
            any(type(k) is type(j) and k == j for j in b) and _same(x, b[k])
            for k, x in a.items()))
    return a == b


# ── 7. Dates ─────────────────────────────────────────────────

_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _leap(y: int) -> bool:
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def _month_days(y: int, m: int) -> int:
    return 29 if m == 2 and _leap(y) else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]


def _ymd(t) -> tuple[int, int, int]:
    y, m, d = (_int(x) for x in t)
    if not (1950 <= y <= 2100 and 1 <= m <= 12 and 1 <= d <= _month_days(y, m)):
        raise ValueError(f"{t!r}: not a date")
    return y, m, d


def _days(t) -> int:
    """Days since 1970-01-01 (the civil calendar, from day numbers)."""
    y, m, d = _ymd(t)
    y -= m <= 2
    era = y // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _civil(n: int) -> tuple[int, int, int]:
    n += 719468
    era = n // 146097
    doe = n - era * 146097
    yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
    doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
    mp = (5 * doy + 2) // 153
    d = doy - (153 * mp + 2) // 5 + 1
    m = mp + (3 if mp < 10 else -9)
    return yoe + era * 400 + (m <= 2), m, d


def _weekday(t) -> int:
    """Monday is 0. 1970-01-01 was a Thursday."""
    return (_days(t) + 3) % 7


def _iso(t) -> str:
    y, m, d = t
    return f"{y:04d}-{m:02d}-{d:02d}"


def _strftime(t, fmt: str) -> str:
    y, m, d = _ymd(t)
    table = {
        "%Y": f"{y:04d}", "%y": f"{y % 100:02d}", "%m": f"{m:02d}", "%d": f"{d:02d}",
        "%B": _MONTHS[m - 1], "%b": _MONTHS[m - 1][:3], "%A": _DAYS[_weekday(t)],
        "%a": _DAYS[_weekday(t)][:3],
        "%j": f"{_days(t) - _days((y, 1, 1)) + 1:03d}",
    }
    out = ""
    for part in re.split(r"(%.)", fmt):
        out += table[part] if part.startswith("%") else part
    return out


_FORMATS = {"%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d", "%d %b %Y", "%B %d, %Y",
            "%A %d %B %Y", "%a %d %b", "%d.%m.%y", "%A", "%B", "%j"}


def _dt(t) -> str:
    y, m, d = _ymd(t)
    return f"date({y}, {m}, {d})"


def _date_text(y, m, d, fmt: str) -> str:
    return _strftime((y, m, d), fmt)


def _time(t) -> tuple[int, int]:
    h, mi = _int(t[0]), _int(t[1])
    if not (0 <= h < 24 and 0 <= mi < 60):
        raise ValueError(f"{t!r}: not a time")
    return h, mi


def _dates(a: dict) -> str:
    want = a["want"]
    D = "from datetime import date"
    DT = "from datetime import date, timedelta"
    if want == "diff":
        return _fit([D, "", f"start = {_dt(a['start'])}", f"end = {_dt(a['end'])}",
                     "print((end - start).days)"])
    if want == "weekday":
        return _fit([D, "", f"day = {_dt(a['day'])}",
                     f'print(day.strftime({_s(a.get("fmt", "%A"))}))'])
    if want == "add":
        return _fit([DT, "", f"start = {_dt(a['start'])}",
                     f"print(start + timedelta(days={_int(a['n'])}))"])
    if want == "month_end":
        y, m = _int(a["year"]), _int(a["month"])
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        return _fit([DT, "", f"after = date({ny}, {nm}, 1)",
                     "print(after - timedelta(days=1))"])
    if want == "parse":
        fmt = a["fmt"]
        first = _s(_date_text(*a["start"], fmt))
        second = _s(_date_text(*a["end"], fmt))
        return _fit(["from datetime import datetime", "",
                     f"start = datetime.strptime({first}, {_s(fmt)})",
                     f"end = datetime.strptime({second}, {_s(fmt)})",
                     "print((end - start).days)"])
    if want == "format":
        return _fit([D, "", f"day = {_dt(a['day'])}", f"print(day.strftime({_s(a['fmt'])}))"])
    if want == "weekends":
        return _fit([DT, "", f"start, end = {_dt(a['start'])}, {_dt(a['end'])}",
                     "days = [start + timedelta(days=i) for i in range((end - start).days + 1)]",
                     "print(sum(day.weekday() >= 5 for day in days))"])
    if want == "age":
        return _fit([D, "", f"born = {_dt(a['born'])}", f"on = {_dt(a['on'])}",
                     "years = on.year - born.year - ((on.month, on.day) < (born.month, born.day))",
                     "print(years)"])
    if want == "delta":
        x, y = a["start"], a["end"]
        return _fit(["from datetime import datetime", "",
                     f"start = datetime({x[0]}, {x[1]}, {x[2]}, {x[3]}, {x[4]})",
                     f"end = datetime({y[0]}, {y[1]}, {y[2]}, {y[3]}, {y[4]})",
                     "print(end - start)"])
    if want == "span":
        days = ", ".join(_dt(d) for d in a["days"])
        return _fit([D, "", f"days = [{days}]", "print(min(days), max(days))",
                     "print((max(days) - min(days)).days)"])
    if want == "next_weekday":
        return _fit([DT, "", f"day = {_dt(a['day'])}", f"target = {_int(a['target'])}",
                     "print(day + timedelta(days=(target - day.weekday() - 1) % 7 + 1))"])
    raise ValueError(want)


def _dates_out(a: dict) -> str:
    want = a["want"]
    if want == "diff":
        gap = _days(a["end"]) - _days(a["start"])
        if gap < 10:
            raise ValueError("a gap of ten days or more")
        return str(gap)
    if want == "weekday":
        fmt = a.get("fmt", "%A")
        if fmt not in ("%A", "%a"):
            raise ValueError(fmt)
        return _strftime(a["day"], fmt)
    if want == "add":
        n = _int(a["n"])
        if n == 0:
            raise ValueError("a move of some days")
        return _iso(_civil(_days(a["start"]) + n))
    if want == "month_end":
        y, m = _ymd((a["year"], a["month"], 1))[:2]
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        return _iso(_civil(_days((ny, nm, 1)) - 1))
    if want == "parse":
        fmt = a["fmt"]
        if fmt not in _FORMATS or fmt in ("%A", "%B", "%j", "%a %d %b", "%A %d %B %Y"):
            raise ValueError(f"{fmt!r}: a format that parses back")
        if "%y" in fmt:
            raise ValueError("four-digit years only")
        gap = _days(a["end"]) - _days(a["start"])
        if gap < 10:
            raise ValueError("a gap of ten days or more")
        return str(gap)
    if want == "format":
        fmt = a["fmt"]
        if fmt not in _FORMATS:
            raise ValueError(f"{fmt!r}: a format the model knows")
        return _strftime(a["day"], fmt)
    if want == "weekends":
        start, end = _days(a["start"]), _days(a["end"])
        if end - start < 14:
            raise ValueError("two weeks or more")
        return str(sum(1 for n in range(start, end + 1) if (n + 3) % 7 >= 5))
    if want == "age":
        born, on = _ymd(a["born"]), _ymd(a["on"])
        if _days(on) <= _days(born):
            raise ValueError("a birthday before the day")
        years = on[0] - born[0] - ((on[1], on[2]) < (born[1], born[2]))
        if years < 1:
            raise ValueError("at least a year")
        return str(years)
    if want == "delta":
        x, y = a["start"], a["end"]
        (h1, m1), (h2, m2) = _time(x[3:]), _time(y[3:])
        minutes = (_days(y[:3]) - _days(x[:3])) * 1440 + (h2 * 60 + m2) - (h1 * 60 + m1)
        if minutes <= 0:
            raise ValueError("a later time")
        days, rest = divmod(minutes, 1440)
        clock = f"{rest // 60}:{rest % 60:02d}:00"
        if days == 0:
            return clock
        return f"{days} day{'s' if days != 1 else ''}, {clock}"
    if want == "span":
        stamps = [_days(d) for d in a["days"]]
        if len(stamps) < 3 or stamps == sorted(stamps) or len(set(stamps)) != len(stamps):
            raise ValueError("three different dates, out of order")
        lo, hi = min(stamps), max(stamps)
        return NL.join([f"{_iso(_civil(lo))} {_iso(_civil(hi))}", str(hi - lo)])
    if want == "next_weekday":
        target = _int(a["target"])
        if not 0 <= target <= 6:
            raise ValueError("a weekday number, 0 to 6")
        n = _days(a["day"])
        step = 1
        while (n + step + 3) % 7 != target:
            step += 1
        return _iso(_civil(n + step))
    raise ValueError(want)


# ── 8. Decimal and Fraction ──────────────────────────────────

_DECIMAL = "from decimal import Decimal"
_HALF_UP = "from decimal import ROUND_HALF_UP, Decimal"
_FRACTION = "from fractions import Fraction"


def _dec(text: str) -> tuple[int, int]:
    """A Decimal as whole numbers: the digits, and how many are after the point."""
    if not isinstance(text, str) or not re.fullmatch(r"\d+(\.\d+)?", text):
        raise ValueError(f"{text!r}: a decimal such as 12.50")
    whole, _, frac = text.partition(".")
    return int(whole + frac), len(frac)


def _dec_str(u: int, s: int) -> str:
    sign = "-" if u < 0 else ""
    digits = str(abs(u)).rjust(s + 1, "0")
    return sign + (digits[:-s] + "." + digits[-s:] if s else digits)


def _dec_add(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    s = max(x[1], y[1])
    return x[0] * 10 ** (s - x[1]) + y[0] * 10 ** (s - y[1]), s


def _dec_sum(items) -> tuple[int, int]:
    total = (0, 0)
    for x in items:
        total = _dec_add(total, x)
    return total


def _cents_half_up(num: int, den: int) -> int:
    """num/den rounded to a whole number, ties away from zero (ROUND_HALF_UP)."""
    q, r = divmod(num, den)
    return q + (1 if 2 * r >= den else 0)


def _quantize(x: tuple[int, int], places: int = 2) -> tuple[int, int]:
    """Decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), for x >= 0."""
    u, s = x
    if s <= places:
        return u * 10 ** (places - s), places
    return _cents_half_up(u, 10 ** (s - places)), places


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def _frac(text: str) -> tuple[int, int]:
    """A Fraction from "3/4" or "5", reduced."""
    if not isinstance(text, str) or not re.fullmatch(r"\d+(/[1-9]\d*)?", text):
        raise ValueError(f"{text!r}: a fraction such as 3/4")
    n, _, d = text.partition("/")
    return _reduce(int(n), int(d) if d else 1)


def _reduce(n: int, d: int) -> tuple[int, int]:
    g = _gcd(n, d) or 1
    n, d = n // g, d // g
    return (n, d) if d > 0 else (-n, -d)


def _frac_str(f: tuple[int, int]) -> str:
    return str(f[0]) if f[1] == 1 else f"{f[0]}/{f[1]}"


def _frac_op(x, op: str, y) -> tuple[int, int]:
    if op == "+":
        return _reduce(x[0] * y[1] + y[0] * x[1], x[1] * y[1])
    if op == "-":
        return _reduce(x[0] * y[1] - y[0] * x[1], x[1] * y[1])
    if op == "*":
        return _reduce(x[0] * y[0], x[1] * y[1])
    if op == "/":
        if y[0] == 0:
            raise ValueError("no dividing by zero")
        return _reduce(x[0] * y[1], x[1] * y[0])
    raise ValueError(op)


def _money(a: dict) -> str:
    want = a["want"]
    if want == "sum_prices":
        return _fit([_DECIMAL, "", f"prices = {_lit(a['prices'])}",
                     "print(sum(Decimal(price) for price in prices))"])
    if want == "line_total":
        return _fit([_DECIMAL, "", f"items = {_lit(a['items'])}",
                     "print(sum(Decimal(price) * qty for price, qty in items))"])
    if want == "tax":
        return _fit([_HALF_UP, "", f"prices = {_lit(a['prices'])}",
                     "subtotal = sum(Decimal(price) for price in prices)",
                     f"tax = (subtotal * Decimal({_s(a['rate'])})).quantize("
                     'Decimal("0.01"), rounding=ROUND_HALF_UP)',
                     "print(subtotal, tax, subtotal + tax)"])
    if want == "split":
        return _fit([_HALF_UP, "", f"total = Decimal({_s(a['total'])})", f"people = {_int(a['people'])}",
                     'share = (total / people).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)',
                     "print(share, total - share * people)"])
    if want == "cents":
        return _fit([_DECIMAL, "", f"price = Decimal({_s(a['price'])})", "cents = int(price * 100)",
                     f"print(cents, cents * {_int(a['qty'])})"])
    if want == "same_value":
        return _fit([_DECIMAL, "", f"x = Decimal({_s(a['x'])})", f"y = Decimal({_s(a['y'])})",
                     "print(x == y)", "print(x, y)"])
    if want == "fraction_sum":
        return _fit([_FRACTION, "", f"parts = {_lit(a['parts'])}",
                     "print(sum(Fraction(part) for part in parts))"])
    if want == "fraction_ops":
        return _fit([_FRACTION, "", f"a = Fraction({_s(a['x'])})", f"b = Fraction({_s(a['y'])})",
                     f"print(a {a['op']} b)"])
    if want == "fraction_parts":
        return _fit([_FRACTION, "", f"parts = {_lit(a['parts'])}",
                     "total = sum(Fraction(part) for part in parts)",
                     "print(total.numerator, total.denominator)"])
    if want == "largest":
        return _fit([_FRACTION, "", f"parts = {_lit(a['parts'])}",
                     "print(max(Fraction(part) for part in parts))"])
    raise ValueError(want)


def _money_out(a: dict) -> str:
    want = a["want"]
    if want == "sum_prices":
        prices = list(a["prices"])
        if len(prices) < 3:
            raise ValueError("three prices at least")
        parsed = [_dec(p) for p in prices]
        if len({s for _, s in parsed}) < 2:
            raise ValueError("prices with different numbers of decimals")
        return _dec_str(*_dec_sum(parsed))
    if want == "line_total":
        items = [tuple(i) for i in a["items"]]
        if len(items) < 3:
            raise ValueError("three lines at least")
        total = _dec_sum([(_dec(p)[0] * _int(q), _dec(p)[1]) for p, q in items])
        return _dec_str(*total)
    if want == "tax":
        prices = list(a["prices"])
        if len(prices) < 3:
            raise ValueError("three prices at least")
        sub = _dec_sum([_dec(p) for p in prices])
        ru, rs = _dec(a["rate"])
        product = (sub[0] * ru, sub[1] + rs)
        tax = _quantize(product)
        if product[1] <= 2 or product[0] % 10 ** (product[1] - 2) == 0:
            raise ValueError("a tax that needed no rounding")
        return " ".join([_dec_str(*sub), _dec_str(*tax), _dec_str(*_dec_add(sub, tax))])
    if want == "split":
        people = _int(a["people"])
        u, s = _dec(a["total"])
        if s != 2 or not 2 <= people <= 9:
            raise ValueError("a total in cents, shared by two to nine")
        share = _cents_half_up(u * 100, 10 ** s * people)
        rest = u - share * people
        if rest == 0:
            raise ValueError("a total that does not split evenly")
        return f"{_dec_str(share, 2)} {_dec_str(rest, 2)}"
    if want == "cents":
        u, s = _dec(a["price"])
        qty = _int(a["qty"])
        if s != 2 or (u * 100) % 10 ** s:
            raise ValueError("a price in cents")
        cents = u * 100 // 10 ** s
        return f"{cents} {cents * qty}"
    if want == "same_value":
        x, y = _dec(a["x"]), _dec(a["y"])
        same = x[0] * 10 ** y[1] == y[0] * 10 ** x[1]
        if a["x"] == a["y"]:
            raise ValueError("written differently")
        return NL.join([str(same), f"{_dec_str(*x)} {_dec_str(*y)}"])
    if want in ("fraction_sum", "fraction_parts", "largest"):
        parts = list(a["parts"])
        if len(parts) < 3:
            raise ValueError("three fractions at least")
        fr = [_frac(p) for p in parts]
        if want == "largest":
            best = fr[0]
            for f in fr[1:]:
                if f[0] * best[1] > best[0] * f[1]:
                    best = f
            if sum(1 for f in fr if f[0] * best[1] == best[0] * f[1]) != 1:
                raise ValueError("one fraction that is largest")
            return _frac_str(best)
        total = (0, 1)
        for f in fr:
            total = _frac_op(total, "+", f)
        if want == "fraction_sum":
            return _frac_str(total)
        if total[1] == 1:
            raise ValueError("a total that is not a whole number")
        return f"{total[0]} {total[1]}"
    if want == "fraction_ops":
        x, y, op = _frac(a["x"]), _frac(a["y"]), a["op"]
        if x == y or (op == "-" and x[0] * y[1] < y[0] * x[1]):
            raise ValueError("two different fractions, and a difference above zero")
        return _frac_str(_frac_op(x, op, y))
    raise ValueError(want)


# ── 9. A grid of lists ───────────────────────────────────────


def _grid(rows, square: bool = False, minimum: int = 2) -> list[list[int]]:
    rows = [list(r) for r in rows]
    if len(rows) < minimum or len({len(r) for r in rows}) != 1 or len(rows[0]) < 2:
        raise ValueError("a grid two rows by two columns or more, every row the same length")
    _nums([x for r in rows for x in r], 4, 0, 99)
    if square and len(rows) != len(rows[0]):
        raise ValueError("a square grid")
    return rows


def _columns(rows) -> list[list[int]]:
    return [[r[c] for r in rows] for c in range(len(rows[0]))]


def _grid_prog(a: dict) -> str:
    want = a["want"]
    if want == "build_table":
        h, w = _int(a["h"]), _int(a["w"])
        return _fit([f"for r in range(1, {h + 1}):",
                     f"    row = [r * c for c in range(1, {w + 1})]", "    print(*row)"])
    if want in ("set_cell", "alias"):
        h, w, r, c, v = (_int(a[k]) for k in ("h", "w", "r", "c", "value"))
        make = (f"grid = [[0] * {w} for _ in range({h})]" if want == "set_cell"
                else f"grid = [[0] * {w}] * {h}")
        return _fit([make, f"grid[{r}][{c}] = {v}", "print(grid)"])
    head = f"rows = {_lit(_grid(a['rows']))}"
    if want == "transpose":
        return _fit([head, "flipped = [list(column) for column in zip(*rows)]", "print(flipped)"])
    if want == "row_sums":
        return _fit([head, "print([sum(row) for row in rows])", "print(sum(map(sum, rows)))"])
    if want == "col_sums":
        return _fit([head, "print([sum(column) for column in zip(*rows)])",
                     "print(len(rows[0]))"])
    if want == "flatten":
        if a["how"] == "chain":
            return _fit(["from itertools import chain", "", head,
                         "print(list(chain.from_iterable(rows)))"])
        return _fit([head, "flat = [x for row in rows for x in row]", "print(flat)"])
    if want == "diagonal":
        idx = "rows[i][i]" if a["which"] == "main" else "rows[i][-1 - i]"
        return _fit([head, f"cells = [{idx} for i in range(len(rows))]", "print(cells)",
                     "print(sum(cells))"])
    if want == "biggest":
        return _fit([head, "best = max(x for row in rows for x in row)", "for r, row in enumerate(rows):",
                     "    if best in row:", "        print(best, r, row.index(best))"])
    if want == "best_row":
        return _fit([head, "totals = [sum(row) for row in rows]",
                     "print(totals.index(max(totals)))", "print(max(totals))"])
    if want == "rotate":
        return _fit([head, "for row in zip(*rows[::-1]):", "    print(*row)"])
    if want == "mirror":
        return _fit([head, "for row in rows:", "    print(*row[::-1])"])
    if want == "count_over":
        return _fit([head, f"count = sum(x > {_int(a['limit'])} for row in rows for x in row)",
                     "print(count)"])
    if want == "neighbors":
        r, c = _int(a["r"]), _int(a["c"])
        return _fit([head, f"r, c = {r}, {c}", "total = 0",
                     "for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):",
                     "    if 0 <= r + dr < len(rows) and 0 <= c + dc < len(rows[0]):",
                     "        total += rows[r + dr][c + dc]", "print(total)"])
    raise ValueError(want)


def _show_rows(rows) -> str:
    return NL.join(" ".join(str(x) for x in r) for r in rows)


def _grid_out(a: dict) -> str:
    want = a["want"]
    if want == "build_table":
        h, w = _int(a["h"]), _int(a["w"])
        if not 2 <= h <= 6 or not 2 <= w <= 6:
            raise ValueError("two to six rows and columns")
        return _show_rows([[r * c for c in range(1, w + 1)] for r in range(1, h + 1)])
    if want in ("set_cell", "alias"):
        h, w, r, c, v = (_int(a[k]) for k in ("h", "w", "r", "c", "value"))
        if h < 2 or w < 2 or not (0 <= r < h and 0 <= c < w) or v == 0:
            raise ValueError("a grid of two by two or more, and a cell that is there")
        grid = [[0] * w for _ in range(h)]
        if want == "set_cell":
            grid[r][c] = v
        else:
            for row in grid:
                row[c] = v
        return _repr(grid)
    square = want == "diagonal"
    rows = _grid(a["rows"], square=square)
    h, w = len(rows), len(rows[0])
    if want == "transpose":
        return _repr(_columns(rows))
    if want == "row_sums":
        return NL.join([_repr([sum(r) for r in rows]), str(sum(sum(r) for r in rows))])
    if want == "col_sums":
        return NL.join([_repr([sum(c) for c in _columns(rows)]), str(w)])
    if want == "flatten":
        if a["how"] not in ("comp", "chain"):
            raise ValueError(a["how"])
        return _repr([x for r in rows for x in r])
    if want == "diagonal":
        if a["which"] not in ("main", "anti"):
            raise ValueError(a["which"])
        cells = [rows[i][i if a["which"] == "main" else -1 - i] for i in range(h)]
        if h < 3 or len(set(cells)) < 3:
            raise ValueError("a 3 by 3 grid or bigger, with different cells on the line")
        return NL.join([_repr(cells), str(sum(cells))])
    if want == "biggest":
        flat = [x for r in rows for x in r]
        top = max(flat)
        if flat.count(top) != 1:
            raise ValueError("one biggest cell")
        r = next(i for i, row in enumerate(rows) if top in row)
        return f"{top} {r} {rows[r].index(top)}"
    if want == "best_row":
        totals = [sum(r) for r in rows]
        if totals.count(max(totals)) != 1 or h < 3:
            raise ValueError("one row with the most, and three rows")
        return NL.join([str(totals.index(max(totals))), str(max(totals))])
    if want == "rotate":
        if h == w:
            raise ValueError("a grid that is not square, so the shape changes")
        return _show_rows([[rows[h - 1 - k][c] for k in range(h)] for c in range(w)])
    if want == "mirror":
        return _show_rows([r[::-1] for r in rows])
    if want == "count_over":
        limit = _int(a["limit"])
        found = sum(1 for r in rows for x in r if x > limit)
        if not 0 < found < h * w:
            raise ValueError("a limit that counts some and not others")
        return str(found)
    if want == "neighbors":
        r, c = _int(a["r"]), _int(a["c"])
        if not (0 <= r < h and 0 <= c < w):
            raise ValueError("a cell that is there")
        total = 0
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= r + dr < h and 0 <= c + dc < w:
                total += rows[r + dr][c + dc]
        return str(total)
    raise ValueError(want)


# ── 10. A block of text ──────────────────────────────────────


def _block(lines, blank_ok: bool = False) -> str:
    """The text of a block as the program writes it: lines joined by \\n."""
    lines = list(lines)
    if len(lines) < 3:
        raise ValueError("three lines at least")
    for line in lines:
        if not isinstance(line, str) or (line == "" and not blank_ok):
            raise ValueError("no blank lines")
        if line:
            _s(line)
    return '"' + "\\n".join(lines) + '"'


def _pad(text: str, width: int, align: str) -> str:
    gap = width - len(text)
    if gap < 1:
        raise ValueError(f"{text!r} does not fit in {width}")
    if align == "<":
        return text + " " * gap
    if align == ">":
        return " " * gap + text
    if align == "^":
        return " " * (gap // 2) + text + " " * (gap - gap // 2)
    raise ValueError(align)


def _commas(n: int) -> str:
    text, out = str(n), ""
    while len(text) > 3:
        out = "," + text[-3:] + out
        text = text[:-3]
    return text + out


def _log_lines(lines) -> list[list[str]]:
    """Log lines of date, level and message, single spaces."""
    parsed = []
    for line in lines:
        parts = line.split(" ", 2)
        if len(parts) != 3 or not re.fullmatch(r"\d{4}-\d\d-\d\d", parts[0]) or parts[1] not in (
                "INFO", "WARN", "ERROR"):
            raise ValueError(f"{line!r}: a date, a level and a message")
        parsed.append(parts)
    return parsed


def _text(a: dict) -> str:
    want = a["want"]
    if want == "levels":
        _log_lines(a["lines"])
        return _fit([f"text = {_block(a['lines'])}",
                     "levels = [line.split()[1] for line in text.splitlines()]",
                     f"print(levels.count({_s(a['level'])}))"])
    if want == "messages":
        _log_lines(a["lines"])
        return _fit([f"text = {_block(a['lines'])}", "for line in text.splitlines():",
                     '    date, _, rest = line.partition(" ")',
                     '    level, _, message = rest.partition(" ")',
                     f"    if level == {_s(a['level'])}:", "        print(message)"])
    if want == "settings":
        return _fit([f"text = {_block(a['lines'], True)}", "settings = {}",
                     "for line in text.splitlines():", "    if line.strip():",
                     '        key, _, value = line.partition("=")',
                     "        settings[key.strip()] = value.strip()", "print(settings)"])
    if want == "table":
        widths = a["widths"]
        al = a["align"]
        comma = a.get("comma", False)
        number = "int(qty)" if comma else "qty"
        second = f"{{{number}:{al[1]}{widths[1]}{',' if comma else ''}}}"
        row = f'    print(f"{{name:{al[0]}{widths[0]}}}{second}")'
        lines = ["text = " + _block(a["lines"]), "for line in text.splitlines():",
                 '    name, qty = line.split(",")', row]
        if a.get("header"):
            names = "{'name':" + al[0] + str(widths[0]) + "}"
            qtys = "{'qty':" + al[1] + str(widths[1]) + "}"
            lines.insert(1, 'print(f"' + names + qtys + '")')
        return _fit(lines)
    if want == "header_body":
        return _fit([f"text = {_block(a['lines'])}", "header, *rows = text.splitlines()",
                     "print(header.upper())", "print(len(rows))", "print(rows[-1])"])
    if want == "longest":
        return _fit([f"text = {_block(a['lines'])}", "lines = text.splitlines()",
                     "longest = max(lines, key=len)", "print(longest, len(longest))"])
    if want == "clean":
        return _fit([f"text = {_s(a['text'])}", "words = text.split()",
                     'print(" ".join(words))', 'print(len(text), len(" ".join(words)))'])
    if want == "sum_csv":
        return _fit([f"text = {_block(a['lines'])}", "lines = text.splitlines()[1:]",
                     'print(sum(int(line.partition(",")[2]) for line in lines))'])
    if want == "rpartition":
        return _fit([f"names = {_lit(a['names'])}", "for name in names:",
                     '    stem, _, ext = name.rpartition(".")', "    print(ext, stem)"])
    if want == "comments":
        return _fit([f"text = {_block(a['lines'], True)}",
                     "lines = [line.strip() for line in text.splitlines()]",
                     'kept = [line for line in lines if line and not line.startswith("#")]',
                     "print(len(kept), kept)"])
    raise ValueError(want)


def _text_out(a: dict) -> str:
    want = a["want"]
    lines = a.get("lines")
    if want in ("levels", "messages"):
        parsed = _log_lines(lines)
        level = a["level"]
        found = [p for p in parsed if p[1] == level]
        if not found or len(found) == len(parsed):
            raise ValueError("a level that is some of the lines")
        if want == "levels":
            return str(len(found))
        if any(not p[2] or p[2] != p[2].strip() for p in parsed):
            raise ValueError("plain messages")
        return NL.join(p[2] for p in found)
    if want == "settings":
        out: dict = {}
        for line in lines:
            if line.strip():
                key, eq, value = line.partition("=")
                if not eq or "=" in value:
                    raise ValueError("one = on a line")
                if not key.strip() or not value.strip():
                    raise ValueError("a key and a value")
                if key.strip() in out:
                    raise ValueError("every key once")
                out[key.strip()] = value.strip()
        _block(lines, True)
        if not any(line != line.strip() for line in lines) or "" not in lines:
            raise ValueError("untidy lines, and a blank one, or strip proves nothing")
        return _repr(out)
    if want == "table":
        widths, al, comma = a["widths"], a["align"], a.get("comma", False)
        rows = []
        for line in lines:
            name, c, qty = line.partition(",")
            if not c or "," in qty or not re.fullmatch(r"[a-z]+", name) or not re.fullmatch(
                    r"\d+", qty):
                raise ValueError(f"{line!r}: a name, a comma and a whole number")
            rows.append((name, _commas(int(qty)) if comma else qty))
        if al[0] not in "<>^" or al[1] not in "<>^":
            raise ValueError(al)
        if a.get("header"):
            rows.insert(0, ("name", "qty"))
        _block(lines)
        return NL.join(_pad(n, widths[0], al[0]) + _pad(q, widths[1], al[1]) for n, q in rows)
    if want == "header_body":
        _block(lines)
        header, rows = lines[0], lines[1:]
        if header != header.lower() or len(rows) < 2:
            raise ValueError("a lowercase header and two rows or more")
        return NL.join([header.upper(), str(len(rows)), rows[-1]])
    if want == "longest":
        _block(lines)
        top = max(len(x) for x in lines)
        found = [x for x in lines if len(x) == top]
        if len(found) != 1:
            raise ValueError("a tie for the longest line")
        return f"{found[0]} {top}"
    if want == "clean":
        text = a["text"]
        _s(text)
        words = [w for w in text.split(" ") if w]
        if len(words) < 3 or text == " ".join(words):
            raise ValueError("three words, and spaces to tidy")
        return NL.join([" ".join(words), f"{len(text)} {len(' '.join(words))}"])
    if want == "sum_csv":
        _block(lines)
        total = 0
        for line in lines[1:]:
            name, c, cost = line.partition(",")
            if not c or not re.fullmatch(r"\d+", cost) or not re.fullmatch(r"[a-z]+", name):
                raise ValueError(f"{line!r}: a name, a comma and a whole number")
            total += int(cost)
        if not re.fullmatch(r"[a-z]+,[a-z]+", lines[0]):
            raise ValueError("a header of two words")
        return str(total)
    if want == "rpartition":
        names = list(a["names"])
        out_lines = []
        for name in names:
            _s(name)
            stem, dot, ext = name.rpartition(".")
            if not dot or not stem or not ext:
                raise ValueError("every name has an extension")
            out_lines.append(f"{ext} {stem}")
        if len(names) < 3 or not any("." in n.rpartition(".")[0] for n in names):
            raise ValueError("three names, one with two dots")
        return NL.join(out_lines)
    if want == "comments":
        _block(lines, True)
        stripped = [x.strip() for x in lines]
        kept = [x for x in stripped if x and not x.startswith("#")]
        if not kept or len(kept) == len(lines) or "" not in lines:
            raise ValueError("comments and a blank line among the settings")
        return f"{len(kept)} {_repr(kept)}"
    raise ValueError(want)


# ── Dispatch ─────────────────────────────────────────────────

_BUILDERS = {
    "py_data_counter": _counter,
    "py_data_group": _group,
    "py_data_records": _records,
    "py_data_stats": _stats,
    "py_data_csv": _csv,
    "py_data_json": _json,
    "py_data_dates": _dates,
    "py_data_money": _money,
    "py_data_grid": _grid_prog,
    "py_data_text": _text,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "py_data_counter": _counter_out,
    "py_data_group": _group_out,
    "py_data_records": _records_out,
    "py_data_stats": _stats_out,
    "py_data_csv": _csv_out,
    "py_data_json": _json_out,
    "py_data_dates": _dates_out,
    "py_data_money": _money_out,
    "py_data_grid": _grid_out,
    "py_data_text": _text_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "py_data_counter": Cost(
        "O(n)",
        "Linear in the number of items, n: Counter makes one pass, and each "
        "item is a dictionary hit, constant on average. most_common(k) then "
        "sorts the distinct keys, which for few distinct words is much less "
        "than n. A lookup of a missing key costs nothing and adds nothing."),
    "py_data_group": Cost(
        "O(n log n)",
        "Building the groups is one pass, a dictionary hit for each item "
        "(constant on average), and groupby is one pass over sorted data. "
        "The sorting, of the rows or of the group names for printing, is what "
        "makes it n log n. groupby only joins neighbours, so without the "
        "sort a key that comes back starts a second group."),
    "py_data_records": Cost(
        "O(n log n)",
        "Filtering, summing and looking for the largest are one pass over n "
        "records. Sorting is about n log n, and a sort on two keys is still "
        "one sort, because the key is the pair. Building a dictionary by "
        "name makes every later lookup constant instead of a pass."),
    "py_data_stats": Cost(
        "O(n log n)",
        "mean, pstdev and mode pass over the n values once or twice. median "
        "and quantiles sort them first, which is n log n, and that is the "
        "price of asking for the middle."),
    "py_data_csv": Cost(
        "O(n)",
        "Linear in the size of the text: the reader looks at each character "
        "once to find the commas and the quotes, DictReader builds one "
        "dictionary per row, and the writer quotes each field as it goes. "
        "Sorting rows before writing them adds a sort on top, n log n."),
    "py_data_json": Cost(
        "O(n)",
        "Linear in the size of the data: dumps and loads visit every value "
        "once, and sort_keys adds a sort of each object's keys, which are few. "
        "A round trip allocates a whole new copy, which is why it is a way to "
        "make a deep copy and also why a tuple does not come back as one."),
    "py_data_dates": Cost(
        "O(n)",
        "Date arithmetic is constant: a date is stored as a day number, so a "
        "difference is a subtraction however far apart the days are. Only "
        "counting weekends walks the days one at a time, linear in the length "
        "of the span."),
    "py_data_money": Cost(
        "O(n)",
        "Linear in the number of amounts, n, with each addition or product a "
        "constant amount of work on numbers of this size. Decimal holds "
        "digits, so it is slower than a float for the same job, and Fraction "
        "keeps two whole numbers and reduces them with Euclid's algorithm, "
        "whose cost grows with the number of digits, not the value."),
    "py_data_grid": Cost(
        "O(r × c)",
        "Proportional to the number of cells, rows times columns: every "
        "cell is read a fixed number of times. Transposing with zip(*rows) "
        "makes a new grid the same size. Nested comprehensions look like a "
        "square, but the two loops cover rows and columns, not one list twice."),
    "py_data_text": Cost(
        "O(n)",
        "Linear in the length of the text: splitlines, split, strip and "
        "partition each pass over the characters once, and a loop over the "
        "lines does a fixed amount of work for each. The f-string table does "
        "the padding as it prints."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
