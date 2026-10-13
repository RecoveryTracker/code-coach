"""Python for handling data: collections, itertools, functools and friends.

The lines are the ones a data-wrangling script is made of: Counter,
defaultdict, deque and namedtuple from collections; groupby, chain, islice,
product and accumulate from itertools; lru_cache, partial and reduce from
functools; dataclasses; csv and json read from and written to io.StringIO;
sorted with a key; comprehensions; zip and enumerate; statistics; decimal
and fractions for exact arithmetic; type hints in the Python 3.12 spelling;
and pathlib for the files the data comes from.

The blocks are whole little programs that print their result, and the
tests run every one in the real interpreter and hold what it prints to an
answer worked out by hand. They touch no files - the CSV and JSON live in
io.StringIO - read no clock and roll no dice, and every fractional result
goes through round or a format spec, so the last digit never depends on how
floating point happens to land.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYDATA_LINES: tuple[Passage, ...] = (
    # collections
    _s("from collections import Counter, defaultdict, deque",
       "the three containers a data script reaches for"),
    _s("counts = Counter(text.lower().split())", "how often each word appears"),
    _s("rare = [w for w, n in counts.items() if n == 1]", "the words seen only once"),
    _s("groups = defaultdict(list)", "a missing key starts as an empty list"),
    _s("groups[len(word)].append(word)", "words grouped by their length"),
    _s("totals[name] += amount", "a running total per name"),
    _s("window = deque(maxlen=3)", "keeps only the last three, dropping the oldest"),
    _s("window.append(price)", "the newest in; the oldest falls out if full"),
    _s("first = queue.popleft()", "take from the front in constant time"),
    _s("Point = namedtuple(\"Point\", [\"x\", \"y\"])", "a tuple whose fields have names"),
    _s("moved = point._replace(x=10)", "a copy with one field changed"),

    # itertools
    _s("from itertools import accumulate, chain, groupby, islice, product",
       "the iterator tools most scripts need"),
    _s("for key, group in groupby(rows, key=lambda r: r[\"team\"]):",
       "runs of equal keys; sort by the key first"),
    _s("merged = list(chain(first, second))", "two iterables, end to end"),
    _s("flat = list(chain.from_iterable(nested))", "flatten one level of nesting"),
    _s("first_five = list(islice(numbers, 5))", "take the first five without slicing"),
    _s("pairs = list(product(\"ab\", range(3)))", "every pairing: six of them"),
    _s("running = list(accumulate(values))", "running totals"),
    _s("highest = list(accumulate(values, max))", "the highest value so far"),
    _s("combos = list(combinations(items, 2))", "every unordered pair, once each"),
    _s("for before, after in pairwise(readings):", "each reading with the next one"),
    _s("batches = list(batched(items, 3))", "chunks of three; new in Python 3.12"),
    _s("padded = list(zip_longest(a, b, fillvalue=0))", "zip that does not stop early"),

    # functools
    _s("from functools import lru_cache, partial, reduce", "caching, pre-filling and folding"),
    _s("@lru_cache(maxsize=None)", "remember every answer the function gives"),
    _s("@functools.cache", "the same, with no limit, in one word"),
    _s("total = reduce(lambda a, b: a * b, numbers, 1)", "fold a list into one value"),
    _s("to_int = partial(int, base=2)", "int with its second argument filled in"),

    # dataclasses
    _s("@dataclass(frozen=True, slots=True)", "an immutable record that is cheap to hold"),
    _s("tags: list[str] = field(default_factory=list)",
       "a mutable default needs a factory"),
    _s("record = asdict(item)", "a dataclass as a plain dict"),
    _s("discounted = replace(item, price=item.price * 0.9)",
       "a copy with one field changed"),

    # csv and json
    _s("reader = csv.DictReader(io.StringIO(text))", "rows as dicts, keyed by the header"),
    _s("rows = list(csv.reader(io.StringIO(text)))", "rows as lists of strings"),
    _s("writer = csv.writer(out, lineterminator=\"\\n\")",
       "csv writes carriage returns unless told otherwise"),
    _s("writer = csv.DictWriter(out, fieldnames=[\"name\", \"score\"])",
       "write dicts, in this column order"),
    _s("writer.writerows(rows)", "every row at once"),
    _s("text = out.getvalue()", "everything written so far, as a string"),
    _s("data = json.loads('{\"a\": 1, \"b\": [true, null]}')",
       "JSON text into Python: true is True, null is None"),
    _s("payload = json.dumps(data, indent=2, sort_keys=True)",
       "readable JSON with the keys in order"),
    _s("json.dump(data, out, separators=(\",\", \":\"))", "compact JSON, with no spaces"),
    _s("print(json.dumps(record, default=str))", "anything JSON cannot hold becomes text"),

    # Sorting and comprehensions
    _s("ranked = sorted(rows, key=lambda r: r[\"score\"], reverse=True)",
       "highest score first"),
    _s("ranked = sorted(people, key=attrgetter(\"age\", \"name\"))",
       "sort by age, then by name"),
    _s("names = sorted(words, key=str.lower)", "alphabetical, ignoring case"),
    _s("by_length = sorted(words, key=lambda w: (len(w), w))",
       "shortest first, then alphabetical"),
    _s("best = max(rows, key=lambda r: r[\"score\"])", "the row with the top score"),
    _s("squares = {n: n * n for n in range(1, 6)}", "a dict built in one line"),
    _s("unique = {w.lower() for w in words}", "a set comprehension drops repeats"),
    _s("total = sum(r[\"qty\"] * r[\"price\"] for r in rows)", "a generator, so no list is built"),
    _s("transposed = [list(col) for col in zip(*matrix)]", "rows become columns"),

    # zip and enumerate
    _s("for i, (name, score) in enumerate(zip(names, scores), start=1):",
       "a counter and a pair, both at once"),
    _s("lookup = dict(zip(keys, values))", "two lists become one dict"),
    _s("for a, b in zip(xs, xs[1:]):", "each item beside the next"),

    # statistics, decimal and fractions
    _s("mean = statistics.mean(scores)", "the average"),
    _s("middle = statistics.median(scores)", "the middle value, unmoved by outliers"),
    _s("spread = statistics.stdev(scores)", "sample standard deviation"),
    _s("common = statistics.mode(grades)", "the most frequent value"),
    _s("q1, q2, q3 = statistics.quantiles(values, n=4)", "the three quartile cut points"),
    _s("from decimal import ROUND_HALF_UP, Decimal", "exact decimal arithmetic"),
    _s("price = Decimal(\"19.99\")", "build it from a string, never a float"),
    _s("cents = amount.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)",
       "round to the cent the way a shop does"),
    _s("share = Fraction(1, 3) + Fraction(1, 6)", "exact: one half, with no rounding"),

    # Type hints
    _s("def mean(values: list[float]) -> float:", "built-in types work as hints now"),
    _s("Row = dict[str, str | int]", "a type alias, with a union written as a pipe"),
    _s("type Matrix = list[list[float]]", "the type statement, from Python 3.12"),
    _s("def first[T](items: list[T]) -> T | None:",
       "a generic function in 3.12's own syntax"),

    # pathlib
    _s("rows = Path(\"data.csv\").read_text().splitlines()", "a file's lines in one call"),
    _s("for path in Path(\"data\").glob(\"*.json\"):", "every JSON file in a folder"),
    _s("with path.open(newline=\"\") as f:", "csv wants the file opened this way"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYDATA_BLOCKS: tuple[Passage, ...] = (
    _b(r"""from collections import Counter

text = "the cat and the hat and the bat"
counts = Counter(text.split())
print(counts.most_common(2))
print(counts["cat"], counts["dog"], len(counts))
counts.update(["cat", "cat"])
print(counts.most_common(1), sum(counts.values()))""",
       "Counter: tally, rank and update"),
    _b(r"""from collections import defaultdict

words = ["apple", "bob", "cat", "avocado", "banana", "cherry"]
groups = defaultdict(list)
for word in words:
    groups[word[0]].append(word)
print(dict(groups))
print({k: len(v) for k, v in groups.items()})
print(groups["z"], len(groups))""",
       "defaultdict: words grouped by first letter"),
    _b(r"""from collections import deque

window = deque(maxlen=3)
averages = []
for price in [10, 20, 30, 40, 50]:
    window.append(price)
    averages.append(sum(window) / len(window))
print(window, averages)
window.rotate(1)
print(list(window), window.popleft())""",
       "deque: a moving average over the last three"),
    _b(r"""from collections import namedtuple

Point = namedtuple("Point", "x y")
a = Point(3, 4)
b = a._replace(x=10)
x, y = b
print(a, b, x + y)
print(a._asdict(), Point._fields)
print(abs(complex(*a)), a == (3, 4))""",
       "namedtuple: names on a tuple"),
    _b(r"""from itertools import accumulate, chain, groupby, islice, product

print(list(accumulate([1, 2, 3, 4])), list(accumulate([3, 1, 4, 1, 5], max)))
print(list(chain("ab", [1, 2])), list(islice(range(100), 2, 8, 2)))
print(list(product("ab", [0, 1])))
data = sorted(["pear", "fig", "plum", "kiwi", "apple"], key=len)
print([(n, list(g)) for n, g in groupby(data, key=len)])""",
       "itertools: accumulate, chain, islice, product and groupby"),
    _b(r"""from functools import lru_cache

calls = 0


@lru_cache(maxsize=None)
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(30), calls)
print(fib.cache_info().hits, fib.cache_info().misses)
fib.cache_clear()
print(fib.cache_info().currsize)""",
       "lru_cache: each Fibonacci number worked out once"),
    _b(r"""from functools import partial, reduce

numbers = [2, 3, 4]
product = reduce(lambda a, b: a * b, numbers, 1)
from_binary = partial(int, base=2)
square = partial(pow, exp=2)
print(product, from_binary("1011"), square(7))
print(reduce(lambda acc, ch: acc * 10 + int(ch), "2024", 0))
print(from_binary.func.__name__, from_binary.keywords)""",
       "reduce and partial"),
    _b(r"""from dataclasses import asdict, dataclass, field, replace


@dataclass(frozen=True, order=True)
class Item:
    price: float
    name: str = field(compare=False)
    tags: tuple[str, ...] = ()


items = [Item(3.5, "tea"), Item(1.25, "gum", ("candy",)), Item(2.0, "pen")]
print(sorted(items)[0].name, max(items).name)
cheap = replace(items[0], price=0.99)
print(cheap, asdict(cheap)["tags"])""",
       "a frozen, ordered dataclass, copied with replace"),
    _b(r"""import csv
import io
import json

text = "name,score\nana,90\nbo,72\ncy,85\n"
rows = list(csv.DictReader(io.StringIO(text)))
best = max(rows, key=lambda r: int(r["score"]))
print(best, len(rows))
out = io.StringIO()
writer = csv.writer(out, lineterminator="\n")
writer.writerows([["a", 1], ["b", "x,y"]])
print(repr(out.getvalue()))
print(json.dumps({"b": [1, None], "a": True}, sort_keys=True))""",
       "CSV and JSON through io.StringIO"),
    _b(r"""import statistics
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction

scores = [70, 80, 80, 90, 100]
print(statistics.mean(scores), statistics.median(scores), statistics.mode(scores))
print(round(statistics.pstdev(scores), 2), statistics.quantiles(scores, n=4))
print(0.1 + 0.2 == 0.3, Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
print(Fraction(1, 3) + Fraction(1, 6), Fraction("0.75"), float(Fraction(3, 8)))""",
       "statistics, then exact arithmetic with Decimal and Fraction"),
    _b(r"""names = ["ana", "bo", "cy"]
scores = [90, 72, 85]
ranked = sorted(zip(scores, names), reverse=True)
print(ranked)
print({n: s for n, s in zip(names, scores) if s > 80})
matrix = [[1, 2, 3], [4, 5, 6]]
print([list(col) for col in zip(*matrix)])
print([f"{i}:{n}" for i, n in enumerate(names, 1)])""",
       "zip, enumerate and comprehensions"),
    _b(r"""type Pair[T] = tuple[T, T]


def first[T](items: list[T]) -> T | None:
    return items[0] if items else None


def swap[T](pair: Pair[T]) -> Pair[T]:
    a, b = pair
    return b, a


print(first([3, 4]), first([]), swap(("x", "y")))""",
       "generic functions and a type alias, in 3.12 syntax"),
)
