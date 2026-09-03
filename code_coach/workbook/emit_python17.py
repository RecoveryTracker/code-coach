"""Python-only shapes, seventeenth batch: sets, types written down, and
the newer corners.

A set comprehension and the frozen set that can live inside another set.
Counter doing arithmetic. TypedDict and Literal, which describe a shape
of data rather than a class. cached_property, which computes once.
base64. Time zones, and the difference between a datetime that knows
where it is and one that does not.

Then three things most people never meet: except*, which catches from a
group of errors raised together; __init_subclass__, which lets a base
class notice that someone inherited from it; and inspect.signature,
which reads a function's own shape back out.

Determinism: every set is printed sorted, and the datetimes use fixed
offsets rather than named zones, which would need a tz database that is
not installed everywhere.
"""

from __future__ import annotations

import base64
import inspect
from collections import Counter
from datetime import datetime, timedelta, timezone

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("set_comp_frozen", "a set built in one line, and a frozen one"),
    Shape("counter_math", "counters added, subtracted and overlapped"),
    Shape("typed_dict", "a dict whose keys are written down"),
    Shape("cached_property", "worked out once, then remembered"),
    Shape("base64_use", "bytes written as safe characters"),
    Shape("aware_datetime", "a time that knows where it is"),
    Shape("exception_group", "several errors at once"),
    Shape("init_subclass", "a base class that notices its children"),
    Shape("signature_use", "reading a function's own shape"),
    Shape("pickle_round", "an object saved and brought back"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "set_comp_frozen":
        return _lines(
            "words = [" + _words(a["words"]) + "]",
            "firsts = {word[0] for word in words}",
            "",
            "print(sorted(firsts))",
            "frozen = frozenset(firsts)",
            "print(sorted(frozen))",
            "print(len({frozen}))",
        )
    if shape == "counter_math":
        return _lines(
            "from collections import Counter",
            "",
            f"first = Counter({_q(a['first'])})",
            f"second = Counter({_q(a['second'])})",
            "",
            "print(sorted((first + second).items()))",
            "print(sorted((first - second).items()))",
            "print(sorted((first & second).items()))",
        )
    if shape == "typed_dict":
        return _lines(
            "from typing import Literal, TypedDict",
            "",
            "",
            f"class {a['cls']}(TypedDict):",
            "    name: str",
            f"    {a['field']}: int",
            "",
            "",
            f"mode: Literal[{_q(a['modes'][0])}, {_q(a['modes'][1])}] = "
            f"{_q(a['modes'][0])}",
            f"person: {a['cls']} = {{\"name\": {_q(a['name'])}, "
            f"{_q(a['field'])}: {a['value']!r}}}",
            "",
            'print(person["name"])',
            f"print(person[{_q(a['field'])}])",
            "print(mode)",
        )
    if shape == "cached_property":
        return _lines(
            "from functools import cached_property",
            "",
            "",
            f"class {a['cls']}:",
            "    def __init__(self, rows):",
            "        self.rows = rows",
            "        self.calls = 0",
            "",
            "    @cached_property",
            f"    def {a['name']}(self):",
            "        self.calls += 1",
            "        return sum(self.rows)",
            "",
            "",
            f"table = {a['cls']}([" + _nums(a["rows"]) + "])",
            f"print(table.{a['name']})",
            f"print(table.{a['name']})",
            "print(table.calls)",
        )
    if shape == "base64_use":
        return _lines(
            "import base64",
            "",
            f"text = {_q(a['text'])}",
            'encoded = base64.b64encode(text.encode("utf-8"))',
            "",
            'print(encoded.decode("ascii"))',
            'print(base64.b64decode(encoded).decode("utf-8"))',
            "print(len(encoded) % 4)",
        )
    if shape == "aware_datetime":
        y, m, d, hour = a["when"]
        return _lines(
            "from datetime import datetime, timedelta, timezone",
            "",
            f"naive = datetime({y}, {m}, {d}, {hour}, 0)",
            "utc = naive.replace(tzinfo=timezone.utc)",
            f"far = utc.astimezone(timezone(timedelta(hours={a['offset']})))",
            "",
            "print(utc.isoformat())",
            "print(far.isoformat())",
            "print(naive.tzinfo)",
        )
    if shape == "exception_group":
        return _lines(
            "def work():",
            f"    raise ExceptionGroup({_q(a['label'])}, [",
            f"        ValueError({_q(a['value_message'])}),",
            f"        KeyError({_q(a['key_message'])}),",
            "    ])",
            "",
            "",
            "try:",
            "    work()",
            "except* ValueError as group:",
            f"    print({_q(a['value_label'])}, len(group.exceptions))",
            "except* KeyError as group:",
            f"    print({_q(a['key_label'])}, len(group.exceptions))",
        )
    if shape == "init_subclass":
        children = []
        for name in a["children"]:
            children.append(f"class {name}({a['base']}):")
            children.append("    pass")
            children.append("")
            children.append("")
        return _lines(
            f"class {a['base']}:",
            "    registry = []",
            "",
            "    def __init_subclass__(cls, **kwargs):",
            "        super().__init_subclass__(**kwargs)",
            f"        {a['base']}.registry.append(cls.__name__)",
            "",
            "",
            *children,
            f"print({a['base']}.registry)",
        )
    if shape == "signature_use":
        params = ", ".join(a["params"])
        return _lines(
            "import inspect",
            "",
            "",
            f"def {a['name']}({params}):",
            f"    return {a['first']}",
            "",
            "",
            f"print(str(inspect.signature({a['name']})))",
            f"print(list(inspect.signature({a['name']}).parameters))",
        )
    if shape == "pickle_round":
        return _lines(
            "import pickle",
            "",
            f"data = {{\"name\": {_q(a['name'])}, "
            f"\"scores\": [{_nums(a['scores'])}]}}",
            "raw = pickle.dumps(data)",
            "back = pickle.loads(raw)",
            "",
            'print(back["name"])',
            'print(back["scores"])',
            "print(back == data)",
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
    if shape == "set_comp_frozen":
        firsts = sorted({word[0] for word in a["words"]})
        if len(firsts) == len(a["words"]):
            # Nothing collapsed, so the set did no visible work.
            raise ValueError("two words must share a first letter")
        lines = [repr(firsts), repr(firsts), "1"]
    elif shape == "counter_math":
        first, second = Counter(a["first"]), Counter(a["second"])
        lines = [
            repr(sorted((first + second).items())),
            repr(sorted((first - second).items())),
            repr(sorted((first & second).items())),
        ]
    elif shape == "typed_dict":
        lines = [a["name"], str(a["value"]), a["modes"][0]]
    elif shape == "cached_property":
        total = sum(a["rows"])
        # Read twice, computed once: that last 1 is the page.
        lines = [str(total), str(total), "1"]
    elif shape == "base64_use":
        encoded = base64.b64encode(a["text"].encode("utf-8"))
        lines = [
            encoded.decode("ascii"),
            a["text"],
            str(len(encoded) % 4),
        ]
    elif shape == "aware_datetime":
        y, m, d, hour = a["when"]
        naive = datetime(y, m, d, hour, 0)
        utc = naive.replace(tzinfo=timezone.utc)
        far = utc.astimezone(timezone(timedelta(hours=a["offset"])))
        lines = [utc.isoformat(), far.isoformat(), "None"]
    elif shape == "exception_group":
        lines = [f"{a['value_label']} 1", f"{a['key_label']} 1"]
    elif shape == "init_subclass":
        lines = [repr(list(a["children"]))]
    elif shape == "signature_use":
        # Built with the real inspect rather than by string work, so the
        # expected text cannot drift from what Python actually prints.
        made: dict = {}
        exec(f"def {a['name']}({', '.join(a['params'])}): pass", made)  # noqa: S102
        found = inspect.signature(made[a["name"]])
        lines = [str(found), repr(list(found.parameters))]
    elif shape == "pickle_round":
        lines = [a["name"], repr(list(a["scores"])), "True"]
    else:
        raise KeyError(shape)
    return NL.join(lines)
