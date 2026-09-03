"""Python-only shapes, twentieth batch: formats, archives, and text that
looks the same.

difflib for how alike two pieces of text are. graphlib, which works out
what has to happen before what. heapq used as a real heap rather than
through nsmallest. Then three formats Python ships whole - zip, gzip and
ini - plus capturing print, string.Template, unicode normalisation, and
the enums that are also numbers or strings.

Determinism: gzip's compressed bytes carry a timestamp, so nothing here
prints them or their length - only the round trip. Every archive listing
is sorted.
"""

from __future__ import annotations

import configparser
import difflib
import gzip
import heapq
import unicodedata
from graphlib import TopologicalSorter
from string import Template

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("difflib_use", "how alike two pieces of text are"),
    Shape("graphlib_use", "what has to happen before what"),
    Shape("heapq_real", "a heap you push and pop yourself"),
    Shape("zipfile_use", "several files in one"),
    Shape("gzip_use", "the same bytes, smaller"),
    Shape("configparser_use", "an ini file read properly"),
    Shape("stringio_redirect", "catching what print would have shown"),
    Shape("template_use", "filling in a template safely"),
    Shape("normalize_use", "two spellings of the same letter"),
    Shape("int_str_enum", "an enum that is also a number or a string"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "difflib_use":
        return _lines(
            "import difflib",
            "",
            f"first = {_q(a['first'])}",
            f"second = {_q(a['second'])}",
            "",
            "matcher = difflib.SequenceMatcher(None, first, second)",
            "print(round(matcher.ratio(), 2))",
            f"print(difflib.get_close_matches({_q(a['typo'])}, "
            f"[{_words(a['options'])}]))",
        )
    if shape == "graphlib_use":
        inside = ", ".join(
            f"{_q(k)}: [" + _words(v) + "]" for k, v in a["graph"]
        )
        return _lines(
            "from graphlib import TopologicalSorter",
            "",
            "graph = {" + inside + "}",
            "order = list(TopologicalSorter(graph).static_order())",
            "",
            "print(order)",
            f"print(order.index({_q(a['before'])}) < "
            f"order.index({_q(a['after'])}))",
        )
    if shape == "heapq_real":
        return _lines(
            "import heapq",
            "",
            "heap = []",
            "for n in [" + _nums(a["items"]) + "]:",
            "    heapq.heappush(heap, n)",
            "",
            "print(heapq.heappop(heap))",
            "print(heapq.heappop(heap))",
            "print(sorted(heap))",
        )
    if shape == "zipfile_use":
        writes = [
            f"        zf.writestr({_q(name)}, {_q(text)})"
            for name, text in a["files"]
        ]
        return _lines(
            "import tempfile",
            "import zipfile",
            "from pathlib import Path",
            "",
            "with tempfile.TemporaryDirectory() as folder:",
            f"    archive = Path(folder) / {_q(a['archive'])}",
            '    with zipfile.ZipFile(archive, "w") as zf:',
            *writes,
            "",
            "    with zipfile.ZipFile(archive) as zf:",
            "        print(sorted(zf.namelist()))",
            f"        print(zf.read({_q(a['files'][0][0])})"
            f'.decode("utf-8"))',
        )
    if shape == "gzip_use":
        return _lines(
            "import gzip",
            "",
            f"text = {_q(a['text'])}",
            'raw = text.encode("utf-8")',
            "squeezed = gzip.compress(raw)",
            "",
            "print(len(raw))",
            'print(gzip.decompress(squeezed).decode("utf-8"))',
            "print(gzip.decompress(squeezed) == raw)",
        )
    if shape == "configparser_use":
        body = f"[{a['section']}]\\n{a['key']} = {a['value']}\\n{a['number_key']} = {a['number']}\\n"
        return _lines(
            "import configparser",
            "",
            f'text = "{body}"',
            "parser = configparser.ConfigParser()",
            "parser.read_string(text)",
            "",
            f"print(parser[{_q(a['section'])}][{_q(a['key'])}])",
            f"print(parser.getint({_q(a['section'])}, "
            f"{_q(a['number_key'])}))",
            "print(parser.sections())",
        )
    if shape == "stringio_redirect":
        return _lines(
            "import contextlib",
            "import io",
            "",
            "buffer = io.StringIO()",
            "with contextlib.redirect_stdout(buffer):",
            f"    print({_q(a['hidden'])})",
            "",
            "print(buffer.getvalue().strip())",
            f"print({_q(a['after'])})",
        )
    if shape == "template_use":
        return _lines(
            "from string import Template",
            "",
            f"greeting = Template({_q(a['template'])})",
            "",
            f"print(greeting.substitute({a['first']}={_q(a['first_value'])}, "
            f"{a['second']}={a['second_value']!r}))",
            f"print(greeting.safe_substitute("
            f"{a['first']}={_q(a['first_value'])}))",
        )
    if shape == "normalize_use":
        return _lines(
            "import unicodedata",
            "",
            f"composed = {_q(a['word'])}",
            'decomposed = unicodedata.normalize("NFD", composed)',
            "",
            "print(len(composed))",
            "print(len(decomposed))",
            "print(composed == decomposed)",
            'print(unicodedata.normalize("NFC", decomposed) == composed)',
        )
    if shape == "int_str_enum":
        return _lines(
            "from enum import IntEnum, StrEnum",
            "",
            "",
            f"class {a['number_cls']}(IntEnum):",
            f"    {a['low']} = 1",
            f"    {a['high']} = 2",
            "",
            "",
            f"class {a['text_cls']}(StrEnum):",
            f"    {a['first']} = {_q(a['first_value'])}",
            f"    {a['second']} = {_q(a['second_value'])}",
            "",
            "",
            f"print({a['number_cls']}.{a['high']} > "
            f"{a['number_cls']}.{a['low']})",
            f"print({a['number_cls']}.{a['high']} + 1)",
            f"print({a['text_cls']}.{a['first']} == "
            f"{_q(a['first_value'])})",
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
    if shape == "difflib_use":
        ratio = difflib.SequenceMatcher(None, a["first"], a["second"]).ratio()
        close = difflib.get_close_matches(a["typo"], list(a["options"]))
        if not close:
            raise ValueError("the typo must be close to something")
        lines = [repr(round(ratio, 2)), repr(close)]
    elif shape == "graphlib_use":
        graph = {k: list(v) for k, v in a["graph"]}
        order = list(TopologicalSorter(graph).static_order())
        lines = [
            repr(order),
            str(order.index(a["before"]) < order.index(a["after"])),
        ]
    elif shape == "heapq_real":
        heap: list[int] = []
        for n in a["items"]:
            heapq.heappush(heap, n)
        lines = [str(heapq.heappop(heap)), str(heapq.heappop(heap))]
        lines.append(repr(sorted(heap)))
    elif shape == "zipfile_use":
        names = sorted(name for name, _ in a["files"])
        lines = [repr(names), a["files"][0][1]]
    elif shape == "gzip_use":
        raw = a["text"].encode("utf-8")
        # Never the compressed bytes: gzip stores a timestamp in them.
        if gzip.decompress(gzip.compress(raw)) != raw:
            raise ValueError("the round trip must come back the same")
        lines = [str(len(raw)), a["text"], "True"]
    elif shape == "configparser_use":
        text = (
            f"[{a['section']}]\n{a['key']} = {a['value']}\n"
            f"{a['number_key']} = {a['number']}\n"
        )
        parser = configparser.ConfigParser()
        parser.read_string(text)
        lines = [
            parser[a["section"]][a["key"]],
            str(parser.getint(a["section"], a["number_key"])),
            repr(parser.sections()),
        ]
    elif shape == "stringio_redirect":
        # The first print went into the buffer, so only these two show.
        lines = [a["hidden"], a["after"]]
    elif shape == "template_use":
        made = Template(a["template"])
        filled = made.substitute(
            **{a["first"]: a["first_value"], a["second"]: a["second_value"]}
        )
        partial = made.safe_substitute(**{a["first"]: a["first_value"]})
        if partial == filled:
            raise ValueError("safe_substitute must leave something behind")
        lines = [filled, partial]
    elif shape == "normalize_use":
        word = a["word"]
        apart = unicodedata.normalize("NFD", word)
        if len(apart) == len(word):
            raise ValueError(f"{word!r} has nothing to decompose")
        lines = [str(len(word)), str(len(apart)), "False", "True"]
    elif shape == "int_str_enum":
        lines = ["True", "3", "True"]
    else:
        raise KeyError(shape)
    return NL.join(lines)
