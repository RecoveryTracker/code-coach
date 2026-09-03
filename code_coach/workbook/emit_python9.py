"""Python-only shapes, ninth batch: files, dates, and the itertools shelf.

Four pages where the program finally touches something outside itself -
paths taken apart and built up, then a file written and read back. The
file pages do their work inside a TemporaryDirectory, which is not a
teaching dodge: it is what you should reach for whenever a program needs
a scratch file, because it cleans up even when something raises.

Then dates, which are their own small world of traps, and four of the
tools that already exist so you stop writing loops for them.

Determinism: the dates are fixed and every format is numeric - no %A or
%B, which read differently under a different locale. Counter data has no
ties, so most_common cannot wobble.
"""

from __future__ import annotations

import itertools
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("path_parts", "a path taken apart by name, stem and suffix"),
    Shape("path_build", "a path built with a slash"),
    Shape("file_write_read", "writing a file and reading it back"),
    Shape("file_lines", "a file's lines, one at a time"),
    Shape("date_format", "a date, and the ways to print it"),
    Shape("date_delta", "days between, and days ahead"),
    Shape("chain_use", "several lists walked as one"),
    Shape("accumulate_use", "the running total, already written"),
    Shape("combinations_use", "every pair, without the nested loop"),
    Shape("most_common_use", "the top few, in order"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _text_of(lines) -> str:
    """The file's contents: every line ended, the way a text file is."""
    return "".join(line + "\n" for line in lines)


def _python(shape: str, a: dict) -> str:
    if shape == "path_parts":
        return _lines(
            "from pathlib import Path",
            "",
            "path = Path(" + _q(a["path"]) + ")",
            "",
            "print(path.name)",
            "print(path.suffix)",
            "print(path.stem)",
            "print(path.parent)",
        )
    if shape == "path_build":
        pieces = " / ".join(_q(p) for p in a["pieces"][1:])
        return _lines(
            "from pathlib import Path",
            "",
            f"path = Path({_q(a['pieces'][0])}) / {pieces}",
            "",
            "print(path)",
            "print(path.name)",
            "print(path.parent)",
        )
    if shape == "file_write_read":
        return _lines(
            "import tempfile",
            "from pathlib import Path",
            "",
            "with tempfile.TemporaryDirectory() as folder:",
            f"    path = Path(folder) / {_q(a['name'])}",
            f"    path.write_text({_text_of(a['lines'])!r})",
            "",
            "    print(path.read_text().strip())",
            "    print(path.exists())",
        )
    if shape == "file_lines":
        return _lines(
            "import tempfile",
            "from pathlib import Path",
            "",
            "with tempfile.TemporaryDirectory() as folder:",
            f"    path = Path(folder) / {_q(a['name'])}",
            f"    path.write_text({_text_of(a['lines'])!r})",
            "",
            "    for line in path.read_text().splitlines():",
            f"        print(line.{a['method']}())",
        )
    if shape == "date_format":
        y, m, d = a["day"]
        return _lines(
            "from datetime import date",
            "",
            f"day = date({y}, {m}, {d})",
            "",
            "print(day.isoformat())",
            f"print(day.strftime({_q(a['spec'])}))",
            "print(day.year)",
        )
    if shape == "date_delta":
        y1, m1, d1 = a["start"]
        y2, m2, d2 = a["end"]
        return _lines(
            "from datetime import date, timedelta",
            "",
            f"start = date({y1}, {m1}, {d1})",
            f"end = date({y2}, {m2}, {d2})",
            "",
            "print((end - start).days)",
            f"print((start + timedelta(days={a['ahead']})).isoformat())",
        )
    if shape == "chain_use":
        return _lines(
            "from itertools import chain",
            "",
            "first = [" + _nums(a["first"]) + "]",
            "second = [" + _nums(a["second"]) + "]",
            "",
            "print(list(chain(first, second)))",
        )
    if shape == "accumulate_use":
        return _lines(
            "from itertools import accumulate",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            "print(list(accumulate(numbers)))",
        )
    if shape == "combinations_use":
        return _lines(
            "from itertools import combinations",
            "",
            "items = [" + _nums(a["items"]) + "]",
            "",
            f"print(list(combinations(items, {a['take']})))",
        )
    if shape == "most_common_use":
        return _lines(
            "from collections import Counter",
            "",
            "words = [" + _words(a["words"]) + "]",
            "counts = Counter(words)",
            "",
            f"for word, many in counts.most_common({a['top']}):",
            "    print(word, many)",
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
    if shape == "path_parts":
        # Built with the same pathlib the exercise runs, so the separator
        # in `parent` is this machine's either way.
        path = Path(a["path"])
        lines = [path.name, path.suffix, path.stem, str(path.parent)]
    elif shape == "path_build":
        path = Path(*a["pieces"])
        lines = [str(path), path.name, str(path.parent)]
    elif shape == "file_write_read":
        lines = [_text_of(a["lines"]).strip(), "True"]
    elif shape == "file_lines":
        lines = [
            getattr(line, a["method"])() for line in a["lines"]
        ]
    elif shape == "date_format":
        day = date(*a["day"])
        lines = [day.isoformat(), day.strftime(a["spec"]), str(day.year)]
    elif shape == "date_delta":
        start, end = date(*a["start"]), date(*a["end"])
        lines = [
            str((end - start).days),
            (start + timedelta(days=a["ahead"])).isoformat(),
        ]
    elif shape == "chain_use":
        lines = [repr(list(a["first"]) + list(a["second"]))]
    elif shape == "accumulate_use":
        lines = [repr(list(itertools.accumulate(a["items"])))]
    elif shape == "combinations_use":
        lines = [repr(list(itertools.combinations(a["items"], a["take"])))]
    elif shape == "most_common_use":
        counts = Counter(a["words"])
        ties = [n for _, n in counts.most_common()]
        if len(set(ties)) != len(ties):
            raise ValueError("most_common data has a tie; order would wobble")
        lines = [f"{w} {n}" for w, n in counts.most_common(a["top"])]
    else:
        raise KeyError(shape)
    return NL.join(lines)
