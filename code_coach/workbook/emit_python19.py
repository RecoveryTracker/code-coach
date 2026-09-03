"""Python-only shapes, nineteenth batch: the last corners.

A metaclass, which is the older and heavier answer to page 246. weakref,
for holding on to something without keeping it alive. struct, for bytes
with a layout. uuid5, which is the same every time for the same name.
Reading an exception without its traceback, and catching a warning
rather than printing it. shutil. cmp_to_key for an old-style comparison
function, methodcaller, and the dataclass fields that stay out of the
repr and out of the comparison.

Determinism: uuid5 is derived from a namespace and a name rather than
from the clock or the machine, warnings are captured rather than
printed, and the traceback page prints only the exception line, never
file paths or line numbers.
"""

from __future__ import annotations

import struct
import uuid
from functools import cmp_to_key

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("metaclass_use", "a class that makes classes"),
    Shape("weakref_use", "a reference that does not keep it alive"),
    Shape("struct_use", "numbers packed into bytes with a layout"),
    Shape("uuid5_use", "an id derived from a name"),
    Shape("traceback_only", "the exception line without the traceback"),
    Shape("warnings_use", "a warning caught instead of printed"),
    Shape("shutil_copy", "copying a file"),
    Shape("cmp_to_key_use", "an old comparison function, made into a key"),
    Shape("methodcaller_use", "calling the same method on each of them"),
    Shape("dataclass_field_flags", "a field kept out of the repr"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _python(shape: str, a: dict) -> str:
    if shape == "metaclass_use":
        children = []
        for name in a["children"]:
            children.append(f"class {name}(metaclass={a['meta']}):")
            children.append("    pass")
            children.append("")
            children.append("")
        return _lines(
            f"class {a['meta']}(type):",
            "    made = []",
            "",
            "    def __new__(mcls, name, bases, namespace):",
            "        cls = super().__new__(mcls, name, bases, namespace)",
            f"        {a['meta']}.made.append(name)",
            "        return cls",
            "",
            "",
            *children,
            f"print({a['meta']}.made)",
        )
    if shape == "weakref_use":
        return _lines(
            "import weakref",
            "",
            "",
            f"class {a['cls']}:",
            "    pass",
            "",
            "",
            f"thing = {a['cls']}()",
            "link = weakref.ref(thing)",
            "",
            "print(link() is thing)",
            "del thing",
            "print(link() is None)",
        )
    if shape == "struct_use":
        values = ", ".join(str(n) for n in a["values"])
        return _lines(
            "import struct",
            "",
            f"packed = struct.pack({_q(a['layout'])}, {values})",
            "",
            "print(len(packed))",
            "print(packed.hex())",
            f"print(struct.unpack({_q(a['layout'])}, packed))",
        )
    if shape == "uuid5_use":
        return _lines(
            "import uuid",
            "",
            f"first = uuid.uuid5(uuid.NAMESPACE_DNS, {_q(a['name'])})",
            f"second = uuid.uuid5(uuid.NAMESPACE_DNS, {_q(a['name'])})",
            "",
            "print(first == second)",
            "print(str(first))",
            "print(first.version)",
        )
    if shape == "traceback_only":
        return _lines(
            "import traceback",
            "",
            "try:",
            f"    int({_q(a['bad'])})",
            "except ValueError as problem:",
            "    lines = traceback.format_exception_only(",
            "        type(problem), problem",
            "    )",
            "    print(lines[0].strip())",
            "    print(len(lines))",
        )
    if shape == "warnings_use":
        return _lines(
            "import warnings",
            "",
            "with warnings.catch_warnings(record=True) as caught:",
            '    warnings.simplefilter("always")',
            f"    warnings.warn({_q(a['message'])}, {a['category']})",
            "",
            "print(len(caught))",
            "print(caught[0].category.__name__)",
            "print(str(caught[0].message))",
        )
    if shape == "shutil_copy":
        return _lines(
            "import shutil",
            "import tempfile",
            "from pathlib import Path",
            "",
            "with tempfile.TemporaryDirectory() as folder:",
            "    root = Path(folder)",
            f"    first = root / {_q(a['first'])}",
            f"    first.write_text({_q(a['text'])})",
            f"    second = root / {_q(a['second'])}",
            "    shutil.copy(first, second)",
            "",
            "    print(second.read_text())",
            "    print(sorted(p.name for p in root.iterdir()))",
        )
    if shape == "cmp_to_key_use":
        return _lines(
            "from functools import cmp_to_key",
            "",
            "",
            "def compare(a, b):",
            "    return len(a) - len(b)",
            "",
            "",
            "words = [" + _words(a["words"]) + "]",
            "",
            "print(sorted(words, key=cmp_to_key(compare)))",
        )
    if shape == "methodcaller_use":
        return _lines(
            "from operator import methodcaller",
            "",
            "words = [" + _words(a["words"]) + "]",
            'lower = methodcaller("lower")',
            "",
            "print([lower(word) for word in words])",
            f"print(methodcaller(\"replace\", {_q(a['from_'])}, "
            f"{_q(a['to'])})({_q(a['subject'])}))",
        )
    if shape == "dataclass_field_flags":
        return _lines(
            "from dataclasses import dataclass, field",
            "",
            "",
            "@dataclass",
            f"class {a['cls']}:",
            "    name: str",
            f"    {a['hidden']}: str = field(repr=False, compare=False)",
            "",
            "",
            f"first = {a['cls']}({_q(a['name'])}, {_q(a['secrets'][0])})",
            f"second = {a['cls']}({_q(a['name'])}, {_q(a['secrets'][1])})",
            "",
            "print(first)",
            "print(first == second)",
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
    if shape == "metaclass_use":
        lines = [repr(list(a["children"]))]
    elif shape == "weakref_use":
        # CPython frees it the moment the last strong reference goes.
        lines = ["True", "True"]
    elif shape == "struct_use":
        packed = struct.pack(a["layout"], *a["values"])
        lines = [
            str(len(packed)),
            packed.hex(),
            repr(struct.unpack(a["layout"], packed)),
        ]
    elif shape == "uuid5_use":
        made = uuid.uuid5(uuid.NAMESPACE_DNS, a["name"])
        lines = ["True", str(made), "5"]
    elif shape == "traceback_only":
        try:
            int(a["bad"])
        except ValueError as problem:
            import traceback

            found = traceback.format_exception_only(type(problem), problem)
            lines = [found[0].strip(), str(len(found))]
        else:
            raise ValueError(f"{a['bad']!r} is a number, so nothing raises")
    elif shape == "warnings_use":
        lines = ["1", a["category"], a["message"]]
    elif shape == "shutil_copy":
        names = sorted((a["first"], a["second"]))
        lines = [a["text"], repr(names)]
    elif shape == "cmp_to_key_use":
        ordered = sorted(a["words"], key=cmp_to_key(lambda x, y: len(x) - len(y)))
        if len(ordered) != len({len(w) for w in a["words"]}):
            raise ValueError("the words must all be different lengths")
        lines = [repr(ordered)]
    elif shape == "methodcaller_use":
        lines = [
            repr([w.lower() for w in a["words"]]),
            a["subject"].replace(a["from_"], a["to"]),
        ]
    elif shape == "dataclass_field_flags":
        # The hidden field is out of the repr and out of the comparison,
        # so two objects differing only in it come out equal.
        lines = [f"{a['cls']}(name={a['name']!r})", "True"]
    else:
        raise KeyError(shape)
    return NL.join(lines)
