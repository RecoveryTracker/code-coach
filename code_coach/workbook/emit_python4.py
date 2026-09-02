"""Python-only shapes, fourth batch: sharp edges, and the lazy half.

Two kinds of page here. The sharp edges are the handful of behaviours that
are perfectly reasonable once you know them and produce baffling bugs until
you do — a default argument that is the same object every call, `is` against
`==`, a copy that copies one level. Every one of them is best met on purpose
in a page that shows the surprise, rather than at eleven at night in code
that matters.

The rest is the lazy half: generators, context managers, decorators,
closures. Those are what separate Python that works from Python written by
someone who knows the language.

Determinism is easy here — everything prints numbers or plain lines — with
one exception. `defaultdict` and `Counter` both iterate in insertion order,
which is stable, but nothing here iterates one anyway: every exercise asks
for keys it names.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("mutable_default", "the default argument that is not fresh"),
    Shape("is_vs_equals", "the same value against the same object"),
    Shape("copy_depth", "a copy that only went one level down"),
    Shape("generator", "a function that hands values back one at a time"),
    Shape("generator_take", "stopping a generator before it runs out"),
    Shape("context_manager", "with, and the cleanup that happens anyway"),
    Shape("decorator", "wrapping a function in another one"),
    Shape("closure", "a function that remembers where it was made"),
    Shape("counter_use", "counting occurrences without writing the loop"),
    Shape("sort_tuple_key", "ordering by one thing, then another"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(repr(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(_q(w) for w in items) + "]"


def _python(shape: str, a: dict) -> str:
    if shape == "mutable_default":
        calls = [f"print({a['name']}({v}))" for v in a["calls"]]
        return _lines(
            f"def {a['name']}(item, box=[]):",
            "    box.append(item)",
            "    return box",
            "",
            *calls,
        )
    if shape == "is_vs_equals":
        return _lines(
            f"first = {a['left']}",
            f"second = {a['right']}",
            "print(first == second)",
            "print(first is second)",
        )
    if shape == "copy_depth":
        return _lines(
            f"inner = {_nums(a['inner'])}",
            "outer = [inner]",
            "shallow = list(outer)",
            f"inner.append({a['added']})",
            "print(len(outer[0]))",
            "print(len(shallow[0]))",
        )
    if shape == "generator":
        return _lines(
            f"def {a['name']}(n):",
            "    for i in range(1, n + 1):",
            f"        yield {a['expr']}",
            "",
            f"for value in {a['name']}({a['upto']}):",
            "    print(value)",
        )
    if shape == "generator_take":
        return _lines(
            f"def {a['name']}():",
            "    i = 1",
            "    while True:",
            f"        yield {a['expr']}",
            "        i += 1",
            "",
            f"maker = {a['name']}()",
            f"for _ in range({a['take']}):",
            "    print(next(maker))",
        )
    if shape == "context_manager":
        return _lines(
            f"class {a['cls']}:",
            "    def __enter__(self):",
            f"        print({_q(a['opening'])})",
            "        return self",
            "",
            "    def __exit__(self, *details):",
            f"        print({_q(a['closing'])})",
            "",
            "",
            f"with {a['cls']}():",
            f"    print({_q(a['inside'])})",
        )
    if shape == "decorator":
        return _lines(
            "def loud(func):",
            "    def wrapper(n):",
            f"        return {a['wrap']}",
            "    return wrapper",
            "",
            "",
            "@loud",
            f"def {a['name']}(n):",
            f"    return {a['expr']}",
            "",
            "",
            *[f"print({a['name']}({v}))" for v in a["calls"]],
        )
    if shape == "closure":
        return _lines(
            "def make(n):",
            "    def inner(m):",
            f"        return {a['expr']}",
            "    return inner",
            "",
            "",
            f"first = make({a['outer'][0]})",
            f"second = make({a['outer'][1]})",
            f"print(first({a['inner']}))",
            f"print(second({a['inner']}))",
        )
    if shape == "counter_use":
        looks = [f"print(counts[{_q(k)}])" for k in a["keys"]]
        return _lines(
            "from collections import Counter",
            "",
            f"words = {_strs(a['words'])}",
            "counts = Counter(words)",
            *looks,
        )
    if shape == "sort_tuple_key":
        return _lines(
            f"words = {_strs(a['words'])}",
            "for word in sorted(words, key=lambda w: (len(w), w)):",
            "    print(word)",
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
    if shape == "mutable_default":
        # The whole point: one list, made once, kept between calls.
        box: list = []
        for v in a["calls"]:
            box.append(v)
            lines.append(repr(list(box)))
    elif shape == "is_vs_equals":
        lines = [str(a["equal"]), str(a["identical"])]
    elif shape == "copy_depth":
        grown = len(a["inner"]) + 1
        # Both, because the shallow copy shares the inner list.
        lines = [str(grown), str(grown)]
    elif shape == "generator":
        lines = [
            str(value(a["expr"], {"i": i}))
            for i in range(1, a["upto"] + 1)
        ]
    elif shape == "generator_take":
        lines = [
            str(value(a["expr"], {"i": i})) for i in range(1, a["take"] + 1)
        ]
    elif shape == "context_manager":
        lines = [a["opening"], a["inside"], a["closing"]]
    elif shape == "decorator":
        lines = [
            str(
                value(
                    a["wrap"],
                    {"func": lambda n: value(a["expr"], {"n": n}), "n": v},
                )
            )
            for v in a["calls"]
        ]
    elif shape == "closure":
        lines = [
            str(value(a["expr"], {"n": outer, "m": a["inner"]}))
            for outer in a["outer"]
        ]
    elif shape == "counter_use":
        from collections import Counter

        counts = Counter(a["words"])
        lines = [str(counts[k]) for k in a["keys"]]
    elif shape == "sort_tuple_key":
        lines = list(sorted(a["words"], key=lambda w: (len(w), w)))
    else:
        raise KeyError(shape)
    return NL.join(lines)
