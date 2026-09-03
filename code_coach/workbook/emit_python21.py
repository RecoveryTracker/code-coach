"""Python-only shapes, twenty-first batch: precision, parsing and the rest
of the toolkit.

Named groups and a lookahead, which are the two regex features worth
knowing beyond page 149. strptime, for text that has to become a date.
calendar. Decimal's quantize, which is the only honest way to round
money. json with a default for types it does not know. Writing csv.
More of pathlib. Four more itertools. And the dataclass that makes you
name your arguments.

Determinism: the rounding page is built from values where half-even and
half-up genuinely disagree, and the emitter raises if a value is chosen
where they do not.
"""

from __future__ import annotations

import calendar
import csv
import io
import json
import re
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from itertools import compress, count, filterfalse, islice
from pathlib import Path

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("regex_named", "capture groups with names"),
    Shape("regex_lookahead", "matching only when something follows"),
    Shape("strptime_use", "text turned into a date"),
    Shape("calendar_use", "how long a month is"),
    Shape("decimal_quantize", "rounding money the way you meant"),
    Shape("json_default", "encoding a type json does not know"),
    Shape("csv_write", "writing a table out"),
    Shape("path_parts_more", "a path's pieces, suffix and relative form"),
    Shape("itertools_more", "count, compress and filterfalse"),
    Shape("dataclass_kwonly", "arguments that must be named"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "regex_named":
        pattern = (
            r"(?P<" + a["first"] + r">\w+)" + a["gap"] + r"(?P<" + a["second"] + r">\d+)"
        )
        return _lines(
            "import re",
            "",
            f'pattern = re.compile(r"{pattern}")',
            f"found = pattern.search({_q(a['text'])})",
            "",
            f"print(found.group({_q(a['first'])}))",
            f"print(found.group({_q(a['second'])}))",
            "print(found.groupdict())",
        )
    if shape == "regex_lookahead":
        return _lines(
            "import re",
            "",
            f'pattern = re.compile(r"\\d+(?= {a["unit"]})")',
            "",
            f"print(pattern.findall({_q(a['text'])}))",
        )
    if shape == "strptime_use":
        return _lines(
            "from datetime import datetime",
            "",
            f"text = {_q(a['text'])}",
            f"when = datetime.strptime(text, {_q(a['reads'])})",
            "",
            "print(when.year)",
            f"print(when.strftime({_q(a['shows'])}))",
            "print(when.date().isoformat())",
        )
    if shape == "calendar_use":
        return _lines(
            "import calendar",
            "",
            f"print(calendar.monthrange({a['year']}, {a['month']}))",
            f"print(calendar.isleap({a['leap_year']}))",
            f"print(calendar.weekday({a['year']}, {a['month']}, {a['day']}))",
        )
    if shape == "decimal_quantize":
        return _lines(
            "from decimal import ROUND_HALF_UP, Decimal",
            "",
            f"value = Decimal({_q(a['value'])})",
            "",
            'print(value.quantize(Decimal("0.01")))',
            'print(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))',
            f"print(round({a['value']}, 2))",
        )
    if shape == "json_default":
        y, m, d = a["when"]
        return _lines(
            "import json",
            "from datetime import date",
            "",
            "",
            "def encode(value):",
            "    if isinstance(value, date):",
            "        return value.isoformat()",
            f"    raise TypeError({_q(a['complaint'])})",
            "",
            "",
            f'data = {{"when": date({y}, {m}, {d}), '
            f'"{a["key"]}": {_q(a["name"])}}}',
            "print(json.dumps(data, default=encode, sort_keys=True))",
        )
    if shape == "csv_write":
        row = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["row"])
        names = ", ".join(_q(k) for k, _ in a["row"])
        return _lines(
            "import csv",
            "import io",
            "",
            "buffer = io.StringIO()",
            "writer = csv.DictWriter(",
            f"    buffer, fieldnames=[{names}], lineterminator=\"\\n\"",
            ")",
            "writer.writeheader()",
            "writer.writerow({" + row + "})",
            "",
            "print(buffer.getvalue().strip())",
        )
    if shape == "path_parts_more":
        return _lines(
            "from pathlib import Path",
            "",
            f"path = Path({_q(a['path'])})",
            "",
            f"print(path.with_suffix({_q(a['suffix'])}).name)",
            "print(path.parts)",
            f"print(path.relative_to({_q(a['root'])}))",
        )
    if shape == "itertools_more":
        picks = ", ".join(str(n) for n in a["picks"])
        return _lines(
            "from itertools import compress, count, filterfalse, islice",
            "",
            f"print(list(islice(count({a['start']}, {a['step']}), "
            f"{a['take']})))",
            f"print(list(compress({_q(a['letters'])}, [{picks}])))",
            f"print(list(filterfalse(lambda n: {a['test']}, "
            f"[{_nums(a['numbers'])}])))",
        )
    if shape == "dataclass_kwonly":
        return _lines(
            "from dataclasses import KW_ONLY, dataclass",
            "",
            "",
            "@dataclass(slots=True)",
            f"class {a['cls']}:",
            f"    {a['first']}: int",
            "    _: KW_ONLY",
            f"    {a['second']}: int = {a['fallback']!r}",
            "",
            "",
            f"thing = {a['cls']}({a['given']!r}, {a['second']}={a['named']!r})",
            "print(thing)",
            "",
            "try:",
            f"    {a['cls']}({a['given']!r}, {a['named']!r})",
            "except TypeError:",
            f"    print({_q(a['complaint'])})",
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
    if shape == "regex_named":
        pattern = (
            r"(?P<" + a["first"] + r">\w+)" + a["gap"] + r"(?P<" + a["second"] + r">\d+)"
        )
        found = re.search(pattern, a["text"])
        if found is None:
            raise ValueError(f"pattern never matches {a['text']!r}")
        lines = [
            found.group(a["first"]),
            found.group(a["second"]),
            repr(found.groupdict()),
        ]
    elif shape == "regex_lookahead":
        found = re.findall(r"\d+(?= " + a["unit"] + ")", a["text"])
        if len(found) != 1:
            # One match, so the lookahead is visibly doing the choosing.
            raise ValueError("the lookahead must pick exactly one number")
        lines = [repr(found)]
    elif shape == "strptime_use":
        when = datetime.strptime(a["text"], a["reads"])
        lines = [
            str(when.year),
            when.strftime(a["shows"]),
            when.date().isoformat(),
        ]
    elif shape == "calendar_use":
        lines = [
            repr(calendar.monthrange(a["year"], a["month"])),
            str(calendar.isleap(a["leap_year"])),
            str(calendar.weekday(a["year"], a["month"], a["day"])),
        ]
    elif shape == "decimal_quantize":
        made = Decimal(a["value"])
        even = made.quantize(Decimal("0.01"))
        up = made.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if even == up:
            # The page exists to show the two rules disagreeing.
            raise ValueError(f"{a['value']} rounds the same either way")
        lines = [str(even), str(up), repr(round(float(a["value"]), 2))]
    elif shape == "json_default":
        y, m, d = a["when"]
        data = {"when": date(y, m, d), a["key"]: a["name"]}
        lines = [
            json.dumps(
                data,
                default=lambda v: v.isoformat(),
                sort_keys=True,
            )
        ]
    elif shape == "csv_write":
        buffer = io.StringIO()
        names = [k for k, _ in a["row"]]
        writer = csv.DictWriter(buffer, fieldnames=names, lineterminator="\n")
        writer.writeheader()
        writer.writerow(dict(a["row"]))
        lines = buffer.getvalue().strip().split("\n")
    elif shape == "path_parts_more":
        path = Path(a["path"])
        lines = [
            path.with_suffix(a["suffix"]).name,
            repr(path.parts),
            str(path.relative_to(a["root"])),
        ]
    elif shape == "itertools_more":
        counted = list(islice(count(a["start"], a["step"]), a["take"]))
        picked = list(compress(a["letters"], a["picks"]))
        rest = list(
            filterfalse(
                lambda n: value(a["test"], {"n": n}), list(a["numbers"])
            )
        )
        lines = [repr(counted), repr(picked), repr(rest)]
    elif shape == "dataclass_kwonly":
        lines = [
            f"{a['cls']}({a['first']}={a['given']!r}, "
            f"{a['second']}={a['named']!r})",
            a["complaint"],
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
