"""Python-only shapes, eighth batch: patterns in text, and work not done twice.

Four pages of regular expressions - matching, capturing, finding every
one, replacing - which is the tool everybody eventually needs and most
people only half learn.

Then recursion into nested data, and the two ways to stop a recursive
function redoing work it has already done: a dict you manage yourself,
and the one-line decorator that replaces it. **kwargs, which is the half
of page 93 that page 93 left out. Numbers in other bases. And reduce,
which is where the fold hiding inside sum and max comes from.

Everything deterministic: kwargs are printed in sorted order rather than
the order they were passed, and nothing prints a dict or a set raw.
"""

from __future__ import annotations

import functools
import re

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("regex_search", "finding the first match, and where it was"),
    Shape("regex_groups", "capturing the pieces you actually wanted"),
    Shape("regex_findall", "every match, not just the first"),
    Shape("regex_sub", "replacing by pattern rather than by text"),
    Shape("recurse_nested", "a function that calls itself on the inside"),
    Shape("memo_dict", "remembering answers in a dict you keep"),
    Shape("lru_cache_use", "the same idea, as one line above the def"),
    Shape("kwargs_use", "as many named arguments as you like"),
    Shape("number_bases", "the same number written three ways"),
    Shape("reduce_use", "folding a list down to one value"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _pattern(text: str) -> str:
    """A raw-string literal, which is how a pattern should always be written."""
    return 'r"' + text + '"'


def _as_list(item):
    if isinstance(item, tuple):
        return [_as_list(x) for x in item]
    return item


def _deep_sum(item) -> int:
    if isinstance(item, tuple):
        return sum(_deep_sum(x) for x in item)
    return item


def _fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _python(shape: str, a: dict) -> str:
    if shape == "regex_search":
        return _lines(
            "import re",
            "",
            "text = " + _q(a["text"]),
            f"found = re.search({_pattern(a['pattern'])}, text)",
            "",
            "print(found.group())",
            "print(found.start())",
        )
    if shape == "regex_groups":
        shows = [f"print(found.group({i}))" for i in (1, 2)]
        return _lines(
            "import re",
            "",
            "text = " + _q(a["text"]),
            f"found = re.search({_pattern(a['pattern'])}, text)",
            "",
            *shows,
        )
    if shape == "regex_findall":
        return _lines(
            "import re",
            "",
            "text = " + _q(a["text"]),
            "",
            f"print(re.findall({_pattern(a['pattern'])}, text))",
        )
    if shape == "regex_sub":
        return _lines(
            "import re",
            "",
            "text = " + _q(a["text"]),
            "",
            f"print(re.sub({_pattern(a['pattern'])}, {_q(a['into'])}, text))",
        )
    if shape == "recurse_nested":
        return _lines(
            f"def {a['name']}(items):",
            "    answer = 0",
            "    for item in items:",
            "        if isinstance(item, list):",
            f"            answer += {a['name']}(item)",
            "        else:",
            "            answer += item",
            "    return answer",
            "",
            "",
            f"print({a['name']}({_as_list(a['nested'])!r}))",
        )
    if shape == "memo_dict":
        shows = [f"print(fib({n}))" for n in a["values"]]
        return _lines(
            "cache = {}",
            "",
            "",
            "def fib(n):",
            "    if n < 2:",
            "        return n",
            "    if n not in cache:",
            "        cache[n] = fib(n - 1) + fib(n - 2)",
            "    return cache[n]",
            "",
            "",
            *shows,
        )
    if shape == "lru_cache_use":
        shows = [f"print(fib({n}))" for n in a["values"]]
        return _lines(
            "from functools import lru_cache",
            "",
            "",
            "@lru_cache",
            "def fib(n):",
            "    if n < 2:",
            "        return n",
            "    return fib(n - 1) + fib(n - 2)",
            "",
            "",
            *shows,
        )
    if shape == "kwargs_use":
        call = ", ".join(f"{k}={v!r}" for k, v in a["pairs"])
        return _lines(
            f"def {a['name']}(**details):",
            "    for key in sorted(details):",
            "        print(key, details[key])",
            "",
            "",
            f"{a['name']}({call})",
        )
    if shape == "number_bases":
        return _lines(
            "value = " + repr(a["value"]),
            "",
            "print(bin(value))",
            "print(hex(value))",
            'print(f"{value:0' + str(a["width"]) + 'b}")',
        )
    if shape == "reduce_use":
        items = ", ".join(repr(n) for n in a["items"])
        return _lines(
            "from functools import reduce",
            "",
            "numbers = [" + items + "]",
            "",
            f"print(reduce(lambda a, b: {a['expr']}, numbers))",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "regex_search":
        found = re.search(a["pattern"], a["text"])
        if found is None:
            raise ValueError(f"pattern never matches: {a['pattern']}")
        lines = [found.group(), str(found.start())]
    elif shape == "regex_groups":
        found = re.search(a["pattern"], a["text"])
        if found is None:
            raise ValueError(f"pattern never matches: {a['pattern']}")
        lines = [found.group(1), found.group(2)]
    elif shape == "regex_findall":
        lines = [repr(re.findall(a["pattern"], a["text"]))]
    elif shape == "regex_sub":
        lines = [re.sub(a["pattern"], a["into"], a["text"])]
    elif shape == "recurse_nested":
        lines = [str(_deep_sum(a["nested"]))]
    elif shape in ("memo_dict", "lru_cache_use"):
        lines = [str(_fib(n)) for n in a["values"]]
    elif shape == "kwargs_use":
        held = dict(a["pairs"])
        lines = [f"{k} {held[k]}" for k in sorted(held)]
    elif shape == "number_bases":
        n = a["value"]
        lines = [bin(n), hex(n), format(n, "0" + str(a["width"]) + "b")]
    elif shape == "reduce_use":
        folded = functools.reduce(
            lambda x, y: value(a["expr"], {"a": x, "b": y}), a["items"]
        )
        lines = [str(folded)]
    else:
        raise KeyError(shape)
    return NL.join(lines)
