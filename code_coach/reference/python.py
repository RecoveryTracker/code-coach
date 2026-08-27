"""The Python cheat sheet."""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="python",
    sections=(
        Section(
            "The first minute",
            "What you write before you have written anything.",
            (
                _e("print(value)", "print anything"),
                _e("name = 'Alex'", "no keyword, no type"),
                _e("count = 0", "same for numbers"),
                _e("def add(a, b):\n    return a + b", "a function"),
                _e("f'Hi, {name}!'", "an f-string interpolates"),
                _e("if a == b:", "one equals compares, two assigns... the other way"),
                _e("for n in nums:", "walk values"),
                _e("return", "leaves the function, handing back None"),
                _e("# a note to your later self", "there is no block comment"),
                _e('"""A docstring."""', "the first line of a function or module"),
            ),
        ),
        Section(
            "Lists",
            "Ordered, growable, and where most of the work happens.",
            (
                _e("nums = [1, 2, 3]", "a literal"),
                _e("len(nums)", "a function, not a method"),
                _e("nums[0]", "and nums[-1] for the last"),
                _e("nums[1:3]", "a slice — a copy, not a view"),
                _e("nums[::-1]", "reversed copy"),
                _e("nums.append(4)", "add one"),
                _e("nums.extend(more)", "add several"),
                _e("nums.pop()", "remove and return the last"),
                _e("nums.insert(0, x)", "at a position — slow at the front"),
                _e("nums.remove(x)", "first match by value"),
                _e("x in nums", "present? linear for a list"),
                _e("nums.index(x)", "where? raises if absent"),
                _e("sorted(nums)", "a new list; nums.sort() is in place"),
                _e("list(nums)", "a shallow copy"),
                _e("','.join(words)", "list of strings to one string"),
            ),
        ),
        Section(
            "Comprehensions",
            "The loop that is an expression. Reach for these first.",
            (
                _e("[n * 2 for n in nums]", "map"),
                _e("[n for n in nums if n > 2]", "filter"),
                _e("[n * 2 for n in nums if n > 2]", "both, filter first"),
                _e("{n for n in nums}", "a set"),
                _e("{k: v for k, v in pairs}", "a dict"),
                _e("(n * 2 for n in nums)", "lazy — a generator, not a tuple"),
                _e("sum(n for n in nums)", "no brackets needed inside a call"),
                _e("[x for row in grid for x in row]", "flatten; outer loop first"),
            ),
        ),
        Section(
            "Strings",
            "Immutable — every one of these returns a new string.",
            (
                _e("len(text)", "characters"),
                _e("text.upper()", "and .lower()"),
                _e("text.strip()", "whitespace off both ends"),
                _e("'ab' in text", "substring present?"),
                _e("text.startswith('a')", "and .endswith"),
                _e("text.find('a')", "-1 if absent; .index raises"),
                _e("text.split(',')", "to a list; no argument splits whitespace"),
                _e("text.replace('a', 'b')", "all of them, unlike JavaScript"),
                _e("text.zfill(2)", "'7' becomes '07'"),
                _e("text.isdigit()", "and .isalpha(), .isalnum()"),
                _e("f'{value:.2f}'", "two decimal places"),
                _e("f'{value:>8}'", "right-aligned in eight columns"),
            ),
        ),
        Section(
            "Dicts and sets",
            "Lookup by key, and membership without duplicates.",
            (
                _e("user = {'name': 'Alex'}", "a literal"),
                _e("user['name']", "raises if the key is missing"),
                _e("user.get('city')", "None if missing"),
                _e("user.get('city', 'unknown')", "with a default"),
                _e("counts[k] = counts.get(k, 0) + 1", "the counting idiom"),
                _e("user.setdefault(k, []).append(v)", "grouping into lists"),
                _e("'name' in user", "checks keys"),
                _e("for k, v in user.items():", "and .keys(), .values()"),
                _e("del user['name']", "or .pop(k) to get it back"),
                _e("{**user, 'age': 31}", "a copy with one field changed"),
                _e("seen = set()", "not {} — that is an empty dict"),
                _e("seen.add(x)", "and .discard(x), which never raises"),
                _e("a & b, a | b, a - b", "intersection, union, difference"),
            ),
        ),
        Section(
            "Deciding",
            "Comparisons, and the bits of syntax that stand in for an if.",
            (
                _e("a == b", "value equality; `is` compares identity"),
                _e("a is None", "always `is` for None"),
                _e("a and b", "returns one of the operands, not a bool"),
                _e("a or b", "the usual way to write a default"),
                _e("not a", "flip it"),
                _e("x if cond else y", "the conditional expression"),
                _e("0 < n < 10", "chained comparison, and it means what it says"),
                _e("if not items:", "empty list, string, dict, all falsy"),
                _e("isinstance(x, int)", "type check that respects subclasses"),
                _e("match value:\n    case 1:", "structural match, 3.10 and up"),
            ),
        ),
        Section(
            "Loops",
            "The shapes, and the built-ins that usually replace them.",
            (
                _e("for n in nums:", "values"),
                _e("for i, n in enumerate(nums):", "index and value"),
                _e("for a, b in zip(xs, ys):", "two at once, stops at the shorter"),
                _e("for i in range(5):", "0 to 4"),
                _e("for i in range(len(nums) - 1, -1, -1):", "backwards"),
                _e("while cond:", "when the end is a condition"),
                _e("break", "leave; continue skips a turn"),
                _e("else:", "on a loop: runs if you never broke out"),
                _e("sum(nums), min(nums), max(nums)", "usually beat a loop"),
                _e("any(...), all(...)", "and they stop early"),
            ),
        ),
        Section(
            "Functions",
            "Arguments, defaults, and the trap in the middle of them.",
            (
                _e("def f(a, b=2):", "a default"),
                _e("def f(*args, **kwargs):", "any positional, any named"),
                _e("def f(a, *, b):", "b must be passed by name"),
                _e("lambda n: n * 2", "one expression, no statements"),
                _e("f(*items)", "spread a list into arguments"),
                _e("f(**opts)", "spread a dict into named arguments"),
                _e("def f(items=None):\n    items = items or []", "never default to []"),
                _e("def f(a: int) -> str:", "type hints; not enforced at runtime"),
                _e("yield value", "makes it a generator"),
            ),
        ),
        Section(
            "Errors and files",
            "Failing on purpose, and the block that always tidies up.",
            (
                _e("raise ValueError('message')", "the specific type, not Exception"),
                _e("try:\n    risky()\nexcept ValueError as err:\n    handle(err)", "the shape"),
                _e("except (A, B):", "several types at once"),
                _e("finally:", "runs either way"),
                _e("with open(path) as f:", "closes even if it throws"),
                _e("f.read()", "and .readlines(), or iterate the file"),
                _e("from pathlib import Path", "the modern way to touch files"),
                _e("Path(p).read_text(encoding='utf-8')", "one line, closed for you"),
            ),
        ),
        Section(
            "Imports and structure",
            "Getting at the standard library, and running a file.",
            (
                _e("import math", "then math.sqrt(x)"),
                _e("from collections import Counter, defaultdict, deque", "the useful three"),
                _e("Counter(items).most_common(3)", "counting, done for you"),
                _e("defaultdict(list)", "no setdefault needed"),
                _e("deque()", "fast at both ends; a list is not"),
                _e("import heapq", "heappush, heappop — a min-heap"),
                _e("if __name__ == '__main__':", "runs only when executed directly"),
            ),
        ),
    ),
)

register(SHEET)
