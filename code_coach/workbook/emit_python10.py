"""Python-only shapes, tenth batch: newer syntax, and the protocols.

Two halves. The first is syntax that did not exist in older Python and
still has not reached most tutorials - match, the walrus, dict merging
with a bar - plus partial and itemgetter, which have been there forever
and are still skipped.

The second is the protocol idea taken seriously. Pages 144 and 145
taught __eq__ and __lt__ so Python's own == and sorted would work.
Here it is __iter__, so a for loop works, and __hash__, so a set works.
The lesson underneath all four is the same: you are not writing methods
for callers to call, you are answering questions the language already
knows how to ask.
"""

from __future__ import annotations

import operator
from collections import deque

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("match_stmt", "matching a value against several cases"),
    Shape("walrus", "naming a value in the middle of a test"),
    Shape("partial_use", "a function with an argument already filled in"),
    Shape("itemgetter_sort", "sorting by a position, without a lambda"),
    Shape("deque_use", "adding and taking from both ends"),
    Shape("transpose", "rows turned into columns"),
    Shape("dict_merge", "two dicts joined, and who wins"),
    Shape("name_main", "what __name__ actually holds"),
    Shape("iter_protocol", "a class a for loop can walk"),
    Shape("hash_dunder", "objects that can live in a set"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "match_stmt":
        cases: list[str] = []
        for when, label in a["cases"]:
            cases.append(f"        case {when!r}:")
            cases.append(f"            return {_q(label)}")
        cases.append("        case _:")
        cases.append(f"            return {_q(a['otherwise'])}")
        return _lines(
            f"def {a['name']}(value):",
            "    match value:",
            *cases,
            "",
            "",
            "for n in [" + _nums(a["values"]) + "]:",
            f"    print({a['name']}(n))",
        )
    if shape == "walrus":
        return _lines(
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            "for n in numbers:",
            f"    if ({a['name']} := {a['expr']}) > {a['limit']}:",
            f"        print({a['name']})",
        )
    if shape == "partial_use":
        return _lines(
            "from functools import partial",
            "",
            "",
            f"def {a['func']}({a['first']}, {a['second']}):",
            f"    return {a['expr']}",
            "",
            "",
            f"{a['names'][0]} = partial({a['func']}, {a['fixed'][0]!r})",
            f"{a['names'][1]} = partial({a['func']}, {a['fixed'][1]!r})",
            "",
            f"print({a['names'][0]}({a['call']!r}))",
            f"print({a['names'][1]}({a['call']!r}))",
        )
    if shape == "itemgetter_sort":
        rows = ", ".join(
            "(" + _q(n) + ", " + repr(v) + ")" for n, v in a["rows"]
        )
        return _lines(
            "from operator import itemgetter",
            "",
            "rows = [" + rows + "]",
            "",
            f"for name, score in sorted(rows, key=itemgetter({a['index']})):",
            "    print(name, score)",
        )
    if shape == "deque_use":
        return _lines(
            "from collections import deque",
            "",
            "queue = deque([" + _nums(a["items"]) + "])",
            f"queue.append({a['right']!r})",
            f"queue.appendleft({a['left']!r})",
            "",
            "print(list(queue))",
            "print(queue.popleft())",
            "print(queue.pop())",
            "print(list(queue))",
        )
    if shape == "transpose":
        rows = ", ".join("[" + _nums(r) + "]" for r in a["rows"])
        return _lines(
            "rows = [" + rows + "]",
            "",
            "for column in zip(*rows):",
            "    print(column)",
        )
    if shape == "dict_merge":
        first = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["first"])
        second = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["second"])
        return _lines(
            "first = {" + first + "}",
            "second = {" + second + "}",
            "merged = first | second",
            "",
            "for key in sorted(merged):",
            "    print(key, merged[key])",
        )
    if shape == "name_main":
        return _lines(
            "def main():",
            f"    print({_q(a['message'])})",
            "",
            "",
            "print(__name__)",
            'if __name__ == "__main__":',
            "    main()",
        )
    if shape == "iter_protocol":
        return _lines(
            f"class {a['cls']}:",
            "    def __init__(self, start):",
            "        self.start = start",
            "",
            "    def __iter__(self):",
            "        n = self.start",
            "        while n > 0:",
            "            yield n",
            f"            n -= {a['step']}",
            "",
            "",
            f"for n in {a['cls']}({a['start']}):",
            "    print(n)",
        )
    if shape == "hash_dunder":
        names = [n for n, _ in a["fields"]]
        same = " and ".join(f"self.{n} == other.{n}" for n in names)
        # A one-field tuple needs the trailing comma; anything longer
        # only looks wrong with it.
        held = ", ".join(f"self.{n}" for n in names)
        if len(names) == 1:
            held += ","
        made = ", ".join(
            f"{a['cls']}(" + ", ".join(_lit(v) for v in point) + ")"
            for point in a["points"]
        )
        return _lines(
            f"class {a['cls']}:",
            f"    def __init__(self, {', '.join(names)}):",
            *[f"        self.{n} = {n}" for n in names],
            "",
            "    def __eq__(self, other):",
            f"        return {same}",
            "",
            "    def __hash__(self):",
            f"        return hash(({held}))",
            "",
            "",
            f"things = {{{made}}}",
            "print(len(things))",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "match_stmt":
        table = dict(a["cases"])
        lines = [table.get(n, a["otherwise"]) for n in a["values"]]
    elif shape == "walrus":
        for n in a["items"]:
            got = value(a["expr"], {"n": n, **_TOOLS})
            if got > a["limit"]:
                lines.append(str(got))
    elif shape == "partial_use":
        lines = [
            str(
                value(
                    a["expr"],
                    {a["first"]: fixed, a["second"]: a["call"], **_TOOLS},
                )
            )
            for fixed in a["fixed"]
        ]
    elif shape == "itemgetter_sort":
        ordered = sorted(a["rows"], key=operator.itemgetter(a["index"]))
        lines = [f"{n} {v}" for n, v in ordered]
    elif shape == "deque_use":
        queue = deque(a["items"])
        queue.append(a["right"])
        queue.appendleft(a["left"])
        lines = [repr(list(queue))]
        lines.append(str(queue.popleft()))
        lines.append(str(queue.pop()))
        lines.append(repr(list(queue)))
    elif shape == "transpose":
        lines = [repr(col) for col in zip(*a["rows"])]
    elif shape == "dict_merge":
        merged = {**dict(a["first"]), **dict(a["second"])}
        lines = [f"{k} {merged[k]}" for k in sorted(merged)]
    elif shape == "name_main":
        # Run as a script, so __name__ is __main__ and main() does run.
        lines = ["__main__", a["message"]]
    elif shape == "iter_protocol":
        n = a["start"]
        while n > 0:
            lines.append(str(n))
            n -= a["step"]
    elif shape == "hash_dunder":
        lines = [str(len({tuple(p) for p in a["points"]}))]
    else:
        raise KeyError(shape)
    return NL.join(lines)
