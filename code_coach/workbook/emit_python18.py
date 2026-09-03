"""Python-only shapes, eighteenth batch: the machinery under the machinery.

A descriptor, which is what @property is made of. ChainMap, for defaults
under choices. ExitStack, for a number of context managers you do not
know in advance. Path.glob and a real temporary directory. os.environ.
Then math.prod and the counting functions, batched and starmap, a
NamedTuple with defaults, a generator you can send values into, and
casefold - which is lower() for people who have met a language other
than English.

Determinism: every glob and every set is sorted, environment variables
are set by the exercise rather than read from the machine, and the
ExitStack page prints its opens and closes in the order they happen,
which is fixed.
"""

from __future__ import annotations

import math
from itertools import batched, starmap

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("descriptor_use", "what a property is made of"),
    Shape("chainmap_use", "choices in front of defaults"),
    Shape("exitstack_use", "however many context managers there turn out to be"),
    Shape("path_glob", "finding files by pattern"),
    Shape("environ_use", "settings from outside the program"),
    Shape("math_prod", "multiplying a list, and counting arrangements"),
    Shape("batched_starmap", "fixed-size chunks, and arguments already in tuples"),
    Shape("namedtuple_defaults", "a record with a default and a replace"),
    Shape("generator_send", "a generator you can hand values back to"),
    Shape("casefold_compare", "comparing text from more than one language"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "descriptor_use":
        return _lines(
            f"class {a['guard']}:",
            "    def __set_name__(self, owner, name):",
            '        self.store = "_" + name',
            "",
            "    def __get__(self, obj, owner=None):",
            "        return getattr(obj, self.store)",
            "",
            "    def __set__(self, obj, value):",
            f"        if value < {a['floor']!r}:",
            f"            raise ValueError({_q(a['complaint'])})",
            "        setattr(obj, self.store, value)",
            "",
            "",
            f"class {a['cls']}:",
            f"    {a['field']} = {a['guard']}()",
            "",
            f"    def __init__(self, {a['field']}):",
            f"        self.{a['field']} = {a['field']}",
            "",
            "",
            f"thing = {a['cls']}({a['good']!r})",
            f"print(thing.{a['field']})",
            "",
            "try:",
            f"    thing.{a['field']} = {a['bad']!r}",
            "except ValueError as problem:",
            "    print(problem)",
        )
    if shape == "chainmap_use":
        defaults = ", ".join(f"{_q(k)}: {_q(v)}" for k, v in a["defaults"])
        chosen = ", ".join(f"{_q(k)}: {_q(v)}" for k, v in a["chosen"])
        return _lines(
            "from collections import ChainMap",
            "",
            "defaults = {" + defaults + "}",
            "chosen = {" + chosen + "}",
            "settings = ChainMap(chosen, defaults)",
            "",
            f"print(settings[{_q(a['chosen'][0][0])}])",
            f"print(settings[{_q(a['only_default'])}])",
            "print(len(settings))",
        )
    if shape == "exitstack_use":
        return _lines(
            "from contextlib import ExitStack, contextmanager",
            "",
            "",
            "@contextmanager",
            "def step(name):",
            '    print("open " + name)',
            "    try:",
            "        yield name",
            "    finally:",
            '        print("close " + name)',
            "",
            "",
            "with ExitStack() as stack:",
            "    names = [",
            "        stack.enter_context(step(name))",
            "        for name in [" + _words(a["names"]) + "]",
            "    ]",
            "",
            "print(names)",
        )
    if shape == "path_glob":
        made = _words(a["files"])
        return _lines(
            "import tempfile",
            "from pathlib import Path",
            "",
            "with tempfile.TemporaryDirectory() as folder:",
            "    root = Path(folder)",
            f"    for name in [{made}]:",
            '        (root / name).write_text("x")',
            "",
            f"    found = sorted(p.name for p in root.glob({_q(a['pattern'])}))",
            "    print(found)",
            '    print(len(list(root.glob("*"))))',
        )
    if shape == "environ_use":
        return _lines(
            "import os",
            "",
            f"os.environ[{_q(a['name'])}] = {_q(a['value'])}",
            "",
            f"print(os.environ[{_q(a['name'])}])",
            f"print(os.environ.get({_q(a['missing'])}, {_q(a['fallback'])}))",
            f"print({_q(a['missing'])} in os.environ)",
        )
    if shape == "math_prod":
        return _lines(
            "import math",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            "print(math.prod(numbers))",
            f"print(math.comb({a['total']}, {a['take']}))",
            f"print(math.perm({a['total']}, {a['take']}))",
        )
    if shape == "batched_starmap":
        pairs = ", ".join(f"({x}, {y})" for x, y in a["pairs"])
        return _lines(
            "from itertools import batched, starmap",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            f"print([list(chunk) for chunk in batched(numbers, {a['size']})])",
            f"print(list(starmap(pow, [{pairs}])))",
        )
    if shape == "namedtuple_defaults":
        return _lines(
            "from typing import NamedTuple",
            "",
            "",
            f"class {a['cls']}(NamedTuple):",
            f"    {a['first']}: int",
            f"    {a['second']}: int = {a['fallback']!r}",
            "",
            "",
            f"thing = {a['cls']}({a['given']!r})",
            f"moved = thing._replace({a['second']}={a['changed']!r})",
            "",
            "print(thing)",
            "print(moved)",
            "print(thing._asdict())",
        )
    if shape == "generator_send":
        sends = [f"print(machine.send({n!r}))" for n in a["sends"]]
        return _lines(
            "def totaller():",
            "    total = 0",
            "    while True:",
            "        n = yield total",
            "        total += n",
            "",
            "",
            "machine = totaller()",
            "print(next(machine))",
            *sends,
            "machine.close()",
            f"print({_q(a['done'])})",
        )
    if shape == "casefold_compare":
        return _lines(
            f"first = {_q(a['upper'])}",
            f"second = {_q(a['plain'])}",
            f"third = {_q(a['special'])}",
            "",
            "print(first.lower() == second)",
            "print(third.lower() == second)",
            "print(third.casefold() == second.casefold())",
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
    if shape == "descriptor_use":
        if a["bad"] >= a["floor"]:
            raise ValueError("the bad value must be refused")
        lines = [str(a["good"]), a["complaint"]]
    elif shape == "chainmap_use":
        merged = {**dict(a["defaults"]), **dict(a["chosen"])}
        # The front map wins; length counts the keys once.
        lines = [
            dict(a["chosen"])[a["chosen"][0][0]],
            dict(a["defaults"])[a["only_default"]],
            str(len(merged)),
        ]
    elif shape == "exitstack_use":
        names = list(a["names"])
        lines = [f"open {n}" for n in names]
        # Unwound in reverse, the way nested with blocks would.
        lines += [f"close {n}" for n in reversed(names)]
        lines.append(repr(names))
    elif shape == "path_glob":
        matched = sorted(
            name for name in a["files"] if name.endswith(a["pattern"][1:])
        )
        if len(matched) == len(a["files"]):
            raise ValueError("the pattern must leave at least one file out")
        lines = [repr(matched), str(len(a["files"]))]
    elif shape == "environ_use":
        lines = [a["value"], a["fallback"], "False"]
    elif shape == "math_prod":
        lines = [
            str(math.prod(a["items"])),
            str(math.comb(a["total"], a["take"])),
            str(math.perm(a["total"], a["take"])),
        ]
    elif shape == "batched_starmap":
        chunks = [list(chunk) for chunk in batched(a["items"], a["size"])]
        powers = list(starmap(pow, a["pairs"]))
        lines = [repr(chunks), repr(powers)]
    elif shape == "namedtuple_defaults":
        first, second = a["first"], a["second"]
        made = {first: a["given"], second: a["fallback"]}
        moved = {first: a["given"], second: a["changed"]}
        lines = [
            f"{a['cls']}({first}={made[first]!r}, {second}={made[second]!r})",
            f"{a['cls']}({first}={moved[first]!r}, {second}={moved[second]!r})",
            repr(made),
        ]
    elif shape == "generator_send":
        total = 0
        lines = ["0"]
        for n in a["sends"]:
            total += n
            lines.append(str(total))
        lines.append(a["done"])
    elif shape == "casefold_compare":
        upper, plain, special = a["upper"], a["plain"], a["special"]
        lines = [
            str(upper.lower() == plain),
            str(special.lower() == plain),
            str(special.casefold() == plain.casefold()),
        ]
        if lines[1] != "False" or lines[2] != "True":
            # The page only says something when lower fails and casefold
            # succeeds on the same pair.
            raise ValueError("casefold must succeed where lower fails")
    else:
        raise KeyError(shape)
    return NL.join(lines)
