"""Short reminders about code that will not run.

Free mode turns the coach off, which is the point of it — nobody wants to be
marked while they are playing. But there is a difference between "you did not
solve it the way I wanted" and "this line has one quote", and the second is
worth saying even when the first is not.

So these are reminders rather than marking. They fire on things that are
simply wrong — an unclosed string, a bracket that never closes, a Python block
header with no colon — and they say what and where, in one line.

Python gets the real parser, because it ships with one: a SyntaxError knows
exactly what is wrong and on which line, and no heuristic will beat it. The
other languages get text checks, for the same reason brace_checks does: there
is no parser in the standard library and shelling out to one on a debounce
would be far too slow.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# What the C-family and friends use to start a comment. Everything after this
# on a line is prose and must not be counted as structure.
_LINE_COMMENT = {
    "python": "#",
    "sql": "--",
    "javascript": "//",
    "typescript": "//",
    "dart": "//",
    "c": "//",
    "cpp": "//",
    "rust": "//",
}

_PAIRS = {")": "(", "]": "[", "}": "{"}
_OPENERS = {"(": ")", "[": "]", "{": "}"}

# Python block headers: these must end in a colon.
_BLOCK = re.compile(
    r"^\s*(if|elif|else|for|while|def|class|try|except|finally|with|match|case)\b"
)


@dataclass(frozen=True)
class Hint:
    """One reminder: what, and which line it is on."""

    line: int
    message: str


def _comment_marker(language: str) -> str:
    return _LINE_COMMENT.get(language, "#")


def _strip_comment(line: str, marker: str) -> str:
    """Drop a trailing comment, without being fooled by one inside a string."""
    out: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                out.append(ch)
                if i + 1 < len(line):
                    out.append(line[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            out.append(ch)
        elif ch in "'\"`":
            quote = ch
            out.append(ch)
        elif line.startswith(marker, i):
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def _unclosed_quote(line: str) -> str | None:
    """The quote character left open at the end of a line, if any."""
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "'\"`":
            quote = ch
        i += 1
    return quote


def _python_hints(code: str) -> list[Hint]:
    """What the parser says, said kindly."""
    try:
        compile(code, "<free>", "exec")
        return []
    except SyntaxError as err:
        line = err.lineno or 1
        raw = (err.msg or "invalid syntax").strip()
        # The parser's own wording is usually good. These three come up often
        # enough to be worth turning into the thing to actually do.
        lowered = raw.lower()
        if "expected ':'" in lowered:
            message = "This line opens a block, so it needs a colon at the end."
        elif "unterminated string" in lowered:
            message = "A quote is opened here and never closed."
        elif "was never closed" in lowered:
            message = raw[0].upper() + raw[1:] + "."
        elif "unexpected indent" in lowered:
            message = "This line is indented further than the one above it."
        elif "expected an indented block" in lowered:
            message = "The line above opens a block, so this one has to indent."
        else:
            message = raw[0].upper() + raw[1:] + "."
        return [Hint(line=line, message=message)]
    except (ValueError, MemoryError):
        # compile() raises ValueError on a source with null bytes.
        return []


def _text_hints(code: str, language: str) -> list[Hint]:
    """Quotes and brackets, for the languages with no parser to hand."""
    marker = _comment_marker(language)
    hints: list[Hint] = []
    stack: list[tuple[str, int]] = []

    for number, raw in enumerate(code.splitlines(), start=1):
        line = _strip_comment(raw, marker)

        left = _unclosed_quote(line)
        if left is not None:
            hints.append(
                Hint(
                    line=number,
                    message=f"A {left} is opened on this line and never closed.",
                )
            )
            # The rest of this line is inside a string as far as anyone can
            # tell, so its brackets are not structure.
            continue

        in_string: str | None = None
        i = 0
        while i < len(line):
            ch = line[i]
            if in_string:
                if ch == "\\":
                    i += 2
                    continue
                if ch == in_string:
                    in_string = None
            elif ch in "'\"`":
                in_string = ch
            elif ch in _OPENERS:
                stack.append((ch, number))
            elif ch in _PAIRS:
                if not stack:
                    hints.append(
                        Hint(
                            line=number,
                            message=f"A {ch} here closes something that was "
                            "never opened.",
                        )
                    )
                elif stack[-1][0] != _PAIRS[ch]:
                    opener, opened_on = stack.pop()
                    hints.append(
                        Hint(
                            line=number,
                            message=f"This {ch} does not match the {opener} "
                            f"opened on line {opened_on}.",
                        )
                    )
                else:
                    stack.pop()
            i += 1

    for opener, opened_on in stack:
        hints.append(
            Hint(
                line=opened_on,
                message=f"This {opener} is never closed by a "
                f"{_OPENERS[opener]}.",
            )
        )
    return hints


def _python_extra(code: str) -> list[Hint]:
    """Things the parser cannot see, because they are style not syntax."""
    hints: list[Hint] = []
    for number, raw in enumerate(code.splitlines(), start=1):
        indent = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in indent and " " in indent:
            hints.append(
                Hint(
                    line=number,
                    message="This line is indented with both tabs and spaces.",
                )
            )
    return hints


def hints_for(code: str, language: str = "python") -> list[Hint]:
    """Reminders about code that will not run, soonest line first.

    Empty when there is nothing to say, which is most of the time — a hint
    that fires on working code is worse than no hint at all.
    """
    if not code.strip():
        return []
    if language == "python":
        found = _python_hints(code) + _python_extra(code)
    else:
        found = _text_hints(code, language)
    # One per line is plenty; a cascade of them from a single missing bracket
    # is noise, and the first one is the one to fix.
    seen: set[int] = set()
    out: list[Hint] = []
    for hint in sorted(found, key=lambda h: h.line):
        if hint.line in seen:
            continue
        seen.add(hint.line)
        out.append(hint)
    return out[:3]
