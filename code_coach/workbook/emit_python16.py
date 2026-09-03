"""Python-only shapes, sixteenth batch: the standard library you reach for at work.

Logging instead of print. argparse instead of reading sys.argv by hand.
__slots__ for the class you make a million of. singledispatch, so one
name can do different work for different types without a chain of
isinstance. attrgetter and methodcaller. Then statistics, Fraction,
hashlib, urllib.parse and textwrap - five modules that already contain
the thing you were about to write.

Determinism: logging is pointed at stdout with a bare format, argparse
is handed its arguments explicitly rather than reading the command line,
and every hash is printed as a hex digest, which is fixed for a given
input forever.
"""

from __future__ import annotations

import hashlib
import statistics
import textwrap
import urllib.parse
from fractions import Fraction

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("logging_use", "saying it properly instead of printing it"),
    Shape("argparse_use", "arguments read for you"),
    Shape("slots_use", "a class told exactly what it may hold"),
    Shape("singledispatch_use", "one name, different work per type"),
    Shape("attrgetter_use", "sorting by an attribute, plainly"),
    Shape("statistics_use", "mean, median and the middle of things"),
    Shape("fraction_use", "thirds that stay thirds"),
    Shape("hashlib_use", "a fingerprint of some text"),
    Shape("urlparse_use", "a web address taken apart"),
    Shape("textwrap_use", "text laid out to a width"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "logging_use":
        return _lines(
            "import logging",
            "import sys",
            "",
            "logging.basicConfig(",
            "    stream=sys.stdout,",
            "    level=logging.INFO,",
            '    format="%(levelname)s %(message)s",',
            ")",
            "",
            f"logging.info({_q(a['info'])})",
            f"logging.warning({_q(a['warning'])})",
            f"logging.debug({_q(a['debug'])})",
        )
    if shape == "argparse_use":
        return _lines(
            "import argparse",
            "",
            "parser = argparse.ArgumentParser()",
            f'parser.add_argument("--{a["flag"]}", type=int, '
            f"default={a['fallback']!r})",
            f'parser.add_argument("--{a["word"]}", default={_q(a["default"])})',
            "",
            f'args = parser.parse_args(["--{a["flag"]}", "{a["given"]}"])',
            "",
            f"print(args.{a['flag']})",
            f"print(args.{a['word']})",
        )
    if shape == "slots_use":
        names = ", ".join(_q(n) for n in a["fields"])
        made = ", ".join(repr(v) for v in a["values"])
        return _lines(
            f"class {a['cls']}:",
            f"    __slots__ = ({names},)",
            "",
            f"    def __init__(self, {', '.join(a['fields'])}):",
            *[f"        self.{n} = {n}" for n in a["fields"]],
            "",
            "",
            f"thing = {a['cls']}({made})",
            f"print(thing.{a['fields'][0]})",
            "",
            "try:",
            f"    thing.{a['extra']} = 1",
            "except AttributeError:",
            f"    print({_q(a['refused'])})",
        )
    if shape == "singledispatch_use":
        return _lines(
            "from functools import singledispatch",
            "",
            "",
            "@singledispatch",
            f"def {a['name']}(value):",
            f"    return {_q(a['fallback'])}",
            "",
            "",
            f"@{a['name']}.register",
            "def _(value: int):",
            f'    return f"{a["int_word"]} {{value}}"',
            "",
            "",
            f"@{a['name']}.register",
            "def _(value: str):",
            f'    return f"{a["str_word"]} {{value}}"',
            "",
            "",
            f"print({a['name']}({a['number']!r}))",
            f"print({a['name']}({_q(a['word'])}))",
            f"print({a['name']}({a['other']!r}))",
        )
    if shape == "attrgetter_use":
        made = ", ".join(
            f"{a['cls']}({_q(n)}, {v!r})" for n, v in a["rows"]
        )
        return _lines(
            "from operator import attrgetter",
            "",
            "",
            f"class {a['cls']}:",
            f"    def __init__(self, name, {a['field']}):",
            "        self.name = name",
            f"        self.{a['field']} = {a['field']}",
            "",
            "",
            f"things = [{made}]",
            "",
            f'for thing in sorted(things, key=attrgetter("{a["field"]}")):',
            f"    print(thing.name, thing.{a['field']})",
        )
    if shape == "statistics_use":
        return _lines(
            "import statistics",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            "print(statistics.mean(numbers))",
            "print(statistics.median(numbers))",
            "print(statistics.mode(numbers))",
        )
    if shape == "fraction_use":
        return _lines(
            "from fractions import Fraction",
            "",
            f"third = Fraction({a['top']}, {a['bottom']})",
            "",
            f"print(third * {a['bottom']})",
            f"print(third + Fraction({a['top']}, {a['bottom']}))",
            f"print(float(third) * {a['bottom']} == {a['top']})",
        )
    if shape == "hashlib_use":
        return _lines(
            "import hashlib",
            "",
            f"text = {_q(a['text'])}",
            'digest = hashlib.sha256(text.encode("utf-8")).hexdigest()',
            "",
            "print(len(digest))",
            f"print(digest[:{a['show']}])",
            'print(digest == hashlib.sha256(text.encode("utf-8")).hexdigest())',
        )
    if shape == "urlparse_use":
        return _lines(
            "from urllib.parse import urlparse",
            "",
            f"address = {_q(a['url'])}",
            "parts = urlparse(address)",
            "",
            "print(parts.scheme)",
            "print(parts.netloc)",
            "print(parts.path)",
        )
    if shape == "textwrap_use":
        return _lines(
            "import textwrap",
            "",
            f"text = {_q(a['text'])}",
            "",
            f"for line in textwrap.wrap(text, width={a['width']}):",
            "    print(line)",
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
    if shape == "logging_use":
        # level=INFO, so debug never appears. That is the page.
        lines = [f"INFO {a['info']}", f"WARNING {a['warning']}"]
    elif shape == "argparse_use":
        lines = [a["given"], a["default"]]
    elif shape == "slots_use":
        lines = [str(a["values"][0]), a["refused"]]
    elif shape == "singledispatch_use":
        lines = [
            f"{a['int_word']} {a['number']}",
            f"{a['str_word']} {a['word']}",
            a["fallback"],
        ]
    elif shape == "attrgetter_use":
        ordered = sorted(a["rows"], key=lambda row: row[1])
        lines = [f"{n} {v}" for n, v in ordered]
    elif shape == "statistics_use":
        items = list(a["items"])
        lines = [
            str(statistics.mean(items)),
            str(statistics.median(items)),
            str(statistics.mode(items)),
        ]
    elif shape == "fraction_use":
        third = Fraction(a["top"], a["bottom"])
        if float(a["top"] / a["bottom"]) * a["bottom"] == a["top"]:
            # Then the float round trip survived and the page's third
            # line would say True, which is the opposite of its point.
            raise ValueError(
                f"{a['top']}/{a['bottom']} survives the float round trip"
            )
        lines = [
            str(third * a["bottom"]),
            str(third + Fraction(a["top"], a["bottom"])),
            str(float(third) * a["bottom"] == a["top"]),
        ]
    elif shape == "hashlib_use":
        digest = hashlib.sha256(a["text"].encode("utf-8")).hexdigest()
        lines = [str(len(digest)), digest[: a["show"]], "True"]
    elif shape == "urlparse_use":
        parts = urllib.parse.urlparse(a["url"])
        lines = [parts.scheme, parts.netloc, parts.path]
    elif shape == "textwrap_use":
        wrapped = textwrap.wrap(a["text"], width=a["width"])
        if len(wrapped) < 2:
            # A single line shows nothing about wrapping.
            raise ValueError("the text must wrap onto at least two lines")
        lines = wrapped
    else:
        raise KeyError(shape)
    return NL.join(lines)
