"""JavaScript: regular expressions from zero.

Pages 107 and 138 already use named groups and matchAll, and a learner who
"does not understand regex at all" meets them cold. These ten shapes are the
ladder up to them: one symbol per page, each a three-to-five line program
that prints true/false, a string, a count or an array.

The expected output is worked out with Python's `re`, which agrees with
JavaScript on everything used here (literal letters, the i flag, \\d, sets
and ranges, + * ? {n} {n,m}, ^ $, . and \\.). Every pattern is checked to
have no capture group, so `match(/.../g)` and `re.findall` return the same
list. The suite then runs each JavaScript answer in node and compares, which
is what actually settles it.

Arrays are printed bare, the way `console.log` shows them - `[ '3', '12' ]` -
because that is what the learner will see when they type the same line.
They are kept to six short items so node never wraps them.
"""

from __future__ import annotations

import re

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("rx_literal", "a pattern is a search for letters"),
    Shape("rx_case", "capital letters matter, and the i flag"),
    Shape("rx_digit", "\\d means one digit"),
    Shape("rx_set", "a set of allowed characters, a range, and not-these"),
    Shape("rx_repeat", "+ one or more, * zero or more, ? maybe"),
    Shape("rx_count", "{3} exactly three, {2,4} between two and four"),
    Shape("rx_anchor", "^ the start and $ the end: checking a whole string"),
    Shape("rx_dot", ". any one character, and \\. a real dot"),
    Shape("rx_replace", "replace, and /g for every match"),
    Shape("rx_match", "match with /g: every match as an array"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _js_str(text: str) -> str:
    if '"' in text or "\\" in text or "\n" in text:
        raise ValueError(f"keep the text plain: {text!r}")
    return f'"{text}"'


def _check_pattern(pattern: str) -> str:
    if "/" in pattern or "(" in pattern or "$1" in pattern:
        raise ValueError(f"no slashes or groups on these pages: {pattern!r}")
    return pattern


def _tests(pattern: str, words) -> str:
    return _lines(
        f"const pattern = /{_check_pattern(pattern)}/;",
        *(f"console.log(pattern.test({_js_str(w)}));" for w in words),
    )


# ── the programs ─────────────────────────────────────────────


def _literal(a: dict) -> str:
    return _tests(a["pattern"], a["words"])


def _case(a: dict) -> str:
    p = _check_pattern(a["pattern"])
    return _lines(
        f"const text = {_js_str(a['text'])};",
        f"console.log(/{p}/.test(text));",
        f"console.log(/{p}/i.test(text));",
    )


def _digit(a: dict) -> str:
    return _lines(
        f"const text = {_js_str(a['text'])};",
        "console.log(/\\d/.test(text));",
        "console.log(/\\d\\d/.test(text));",
    )


def _dot(a: dict) -> str:
    left, right = a["left"], a["right"]
    return _lines(
        f"const text = {_js_str(a['text'])};",
        f"console.log(/{left}.{right}/.test(text));",
        f"console.log(/{left}\\.{right}/.test(text));",
    )


def _replace(a: dict) -> str:
    p = _check_pattern(a["pattern"])
    with_ = _js_str(a["with"])
    return _lines(
        f"const text = {_js_str(a['text'])};",
        f"console.log(text.replace(/{p}/, {with_}));",
        f"console.log(text.replace(/{p}/g, {with_}));",
    )


def _match(a: dict) -> str:
    p = _check_pattern(a["pattern"])
    return _lines(
        f"const text = {_js_str(a['text'])};",
        f"const found = text.match(/{p}/g);",
        "console.log(found);",
        "console.log(found.length);",
    )


_BUILDERS = {
    "rx_literal": _literal,
    "rx_case": _case,
    "rx_digit": _digit,
    "rx_set": _literal,
    "rx_repeat": _literal,
    "rx_count": _literal,
    "rx_anchor": _literal,
    "rx_dot": _dot,
    "rx_replace": _replace,
    "rx_match": _match,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── what they print ──────────────────────────────────────────


def _bool(found) -> str:
    return "true" if found else "false"


def _both_ways(results: list[bool], what: str) -> None:
    if all(results) or not any(results):
        raise ValueError(
            f"{what}: the words must include a yes and a no, or the page "
            "never shows the pattern telling them apart"
        )


def _node_array(items: list[str]) -> str:
    """How console.log shows a short array of strings."""
    for s in items:
        if "'" in s or "\\" in s:
            raise ValueError(f"node would quote {s!r} differently")
    return "[ " + ", ".join(f"'{s}'" for s in items) + " ]"


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out with Python's re, from the data rather than the JavaScript."""
    a = args
    if shape in ("rx_literal", "rx_set", "rx_repeat", "rx_count", "rx_anchor"):
        pattern = _check_pattern(a["pattern"])
        words = list(a["words"])
        if len(words) < 2:
            raise ValueError("at least two words to compare")
        results = [re.search(pattern, w) is not None for w in words]
        _both_ways(results, pattern)
        return NL.join(_bool(r) for r in results)
    if shape == "rx_case":
        p, text = a["pattern"], a["text"]
        if re.search(p, text, re.IGNORECASE) is None:
            raise ValueError("with i it must be found, or i shows nothing")
        return NL.join([
            _bool(re.search(p, text)),
            _bool(re.search(p, text, re.IGNORECASE)),
        ])
    if shape == "rx_digit":
        text = a["text"]
        return NL.join([
            _bool(re.search(r"\d", text)), _bool(re.search(r"\d\d", text)),
        ])
    if shape == "rx_dot":
        left, right, text = a["left"], a["right"], a["text"]
        for part in (left, right):
            if not re.fullmatch(r"[A-Za-z0-9]+", part):
                raise ValueError("the two sides are plain letters and digits")
        return NL.join([
            _bool(re.search(f"{left}.{right}", text)),
            _bool(re.search(f"{left}\\.{right}", text)),
        ])
    if shape == "rx_replace":
        p, text, with_ = a["pattern"], a["text"], a["with"]
        if "$" in with_ or "\\" in with_:
            raise ValueError("a replacement with $ or \\ is a later lesson")
        if len(re.findall(p, text)) < 2:
            raise ValueError(
                "at least two matches, or /g and no /g print the same"
            )
        return NL.join([re.sub(p, with_, text, count=1), re.sub(p, with_, text)])
    if shape == "rx_match":
        p, text = a["pattern"], a["text"]
        if re.compile(p).groups:
            raise ValueError("a group changes what match returns")
        found = re.findall(p, text)
        if not found:
            raise ValueError("no match means null, and null.length throws")
        if len(found) > 6 or sum(len(s) + 4 for s in found) > 60:
            raise ValueError("node wraps long arrays onto several lines")
        return NL.join([_node_array(found), str(len(found))])
    raise KeyError(shape)
