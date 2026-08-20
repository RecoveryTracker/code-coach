"""Plain-English walkthrough of JavaScript, line by line.

The Python explainer walks a real syntax tree, because Python ships one. There
is no JavaScript parser in the standard library, and pulling in a whole parser
to describe twenty statement forms would be a poor trade — so this reads the
code the way a person skimming it does: one line at a time, recognising the
shape of each statement.

That has an honest limit. It describes statements, not expressions nested
three deep, and a line it doesn't recognise is quoted rather than guessed at.
Saying nothing about a line is fine; saying something wrong about it is not.

It's paired with a real traced run (see `_js_trace_runner.js`), so the summary
can talk about what actually happened rather than only what the code says.
"""

from __future__ import annotations

import re
from typing import Any

# ── Statement shapes ────────────────────────────────────────
# Ordered: the first pattern that matches a line wins, so the more specific
# forms come first.

_DECL = re.compile(
    r"^(const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(.+?);?$"
)
_DESTRUCTURE = re.compile(
    r"^(const|let|var)\s*([\[{])(.+?)[\]}]\s*=\s*(.+?);?$"
)
_FUNCTION = re.compile(
    r"^(?:export\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)?\s*\((.*?)\)"
)
_ARROW_DECL = re.compile(
    r"^(const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
    r"\(?([^)=]*?)\)?\s*=>"
)
_CLASS = re.compile(r"^class\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+([A-Za-z_$][\w$]*))?")
_FOR_CLASSIC = re.compile(
    r"^for\s*\(\s*(?:let|var|const)?\s*([A-Za-z_$][\w$]*)\s*=\s*(.+?)\s*;"
    r"\s*(.+?)\s*;\s*(.+?)\s*\)"
)
_FOR_OF = re.compile(
    r"^for\s*\(\s*(?:const|let|var)\s+(.+?)\s+of\s+(.+?)\s*\)"
)
_FOR_IN = re.compile(
    r"^for\s*\(\s*(?:const|let|var)\s+(.+?)\s+in\s+(.+?)\s*\)"
)
_WHILE = re.compile(r"^while\s*\((.+)\)")
_IF_HEAD = re.compile(r"^(?:\}\s*)?(else\s+if|if)\s*\(")


def _split_if(line: str) -> tuple[str, str, str] | None:
    """Break `if (cond) tail` into its parts, counting parens.

    A regex can't do this: non-greedy stops at the first `)` and cuts
    `seen.has(need)` in half, greedy runs to the last one and swallows the
    body. Nested calls in conditions are far too common to get either wrong.
    """
    head = _IF_HEAD.match(line)
    if not head:
        return None
    start = line.index("(", head.end() - 1)
    depth = 0
    for i in range(start, len(line)):
        if line[i] == "(":
            depth += 1
        elif line[i] == ")":
            depth -= 1
            if depth == 0:
                return head.group(1), line[start + 1 : i], line[i + 1 :].strip()
    return None
_ELSE = re.compile(r"^(?:\}\s*)?else\s*\{?\s*$")
_RETURN = re.compile(r"^return\b\s*(.*?);?$")
_ASSIGN = re.compile(r"^([A-Za-z_$][\w$.\[\]'\"]*)\s*(\+=|-=|\*=|/=|=)\s*(.+?);?$")
_INCREMENT = re.compile(r"^([A-Za-z_$][\w$.\[\]]*)\s*(\+\+|--)\s*;?$")
_CALL = re.compile(r"^([A-Za-z_$][\w$.]*)\((.*)\)\s*;?$")

# Comparisons and operators, in the order they must be tried: === before ==.
_OPERATORS: tuple[tuple[str, str], ...] = (
    ("===", "is exactly equal to"),
    ("!==", "is not exactly equal to"),
    ("==", "is equal to"),
    ("!=", "is not equal to"),
    (">=", "is at least"),
    ("<=", "is at most"),
    ("&&", "and"),
    ("||", "or"),
    ("??", "or, if that's null,"),
    (">", "is greater than"),
    ("<", "is less than"),
)

# The methods that carry the meaning in most JavaScript worth explaining.
_METHODS: dict[str, str] = {
    "push": "adds {args} to the end of {target}",
    "pop": "takes the last item off {target}",
    "shift": "takes the first item off {target}",
    "unshift": "puts {args} on the front of {target}",
    "slice": "takes a copy of part of {target}",
    "splice": "cuts items out of {target}",
    "map": "makes a new array by transforming every item of {target}",
    "filter": "keeps only the items of {target} that pass a test",
    "reduce": "folds {target} down to a single value",
    "forEach": "runs something for each item of {target}",
    "sort": "puts {target} in order",
    "reverse": "flips {target} back to front",
    "join": "glues {target} together into one string",
    "split": "breaks {target} apart into an array",
    "includes": "checks whether {target} contains {args}",
    "indexOf": "finds where {args} sits in {target}",
    "has": "checks whether {target} already contains {args}",
    "get": "looks up {args} in {target}",
    "set": "stores {args} in {target}",
    "add": "puts {args} into {target}",
    "delete": "removes {args} from {target}",
    "keys": "lists the keys of {target}",
    "values": "lists the values of {target}",
    "entries": "lists {target} as key-and-value pairs",
    "charCodeAt": "gets the character code from {target}",
    "toString": "turns {target} into text",
    "concat": "joins {args} onto {target}",
    "find": "finds the first item of {target} that passes a test",
    "some": "checks whether any item of {target} passes a test",
    "every": "checks whether every item of {target} passes a test",
}

_METHOD_CALL = re.compile(r"^([A-Za-z_$][\w$.\[\]]*)\.([A-Za-z_$][\w$]*)\((.*)\)\s*;?$")


def _readable(expr: str) -> str:
    """Turn an expression into something closer to English.

    Deliberately shallow: it swaps operators for words and leaves the rest
    alone. Rewriting a nested expression into prose usually reads worse than
    the code did.
    """
    text = expr.strip().rstrip(";")
    for symbol, word in _OPERATORS:
        if symbol in text:
            text = text.replace(symbol, f" {word} ")
    return re.sub(r"\s+", " ", text).strip()


def _describe_new(value: str) -> str | None:
    match = re.match(r"^new\s+([A-Za-z_$][\w$]*)\s*\((.*)\)", value.strip())
    if not match:
        return None
    kind, args = match.group(1), match.group(2).strip()
    known = {
        "Map": "an empty lookup table (a Map: keys to values)",
        "Set": "an empty Set, which keeps only one of each value",
        "Array": "a new array",
        "Date": "the current date and time",
    }
    if kind in known and not args:
        return known[kind]
    if kind == "Map":
        return "a lookup table built from " + args
    if kind == "Set":
        return "a Set built from " + args + ", dropping any duplicates"
    if kind == "Array":
        return f"an array of {args} slots"
    return f"a new {kind}" + (f", built from {args}" if args else "")


def _describe_value(value: str) -> str:
    """What a right-hand side produces."""
    value = value.strip().rstrip(";")

    made = _describe_new(value)
    if made:
        return made
    if value in ("[]",):
        return "an empty array"
    if value in ("{}",):
        return "an empty object"
    if value in ("0", "1", "-1"):
        return value
    if value in ("Infinity", "-Infinity"):
        return f"{value} — a starting value that any real number beats"
    if value in ("true", "false", "null", "undefined"):
        return value
    spread = re.match(r"^\[\s*\.\.\.new\s+Set\((.+)\)\s*\]$", value)
    if spread:
        return f"a copy of {spread.group(1)} with the duplicates removed"
    if value.startswith("[...") and value.endswith("]"):
        return f"a copy of {value[4:-1]} as an array"
    if value.startswith("[") and value.endswith("]"):
        return f"the array {value}"

    method = _METHOD_CALL.match(value)
    if method:
        return _describe_method(method.group(1), method.group(2), method.group(3))
    return _readable(value)


# Math is worth special-casing: "calls max on Math with a, b" is worse than
# no explanation at all, and these appear constantly in solutions.
_MATH: dict[str, str] = {
    "max": "the larger of {args}",
    "min": "the smaller of {args}",
    "abs": "the size of {args}, ignoring the sign",
    "floor": "{args} rounded down",
    "ceil": "{args} rounded up",
    "round": "{args} rounded",
    "sqrt": "the square root of {args}",
    "pow": "{args} raised to a power",
}


def _describe_method(target: str, method: str, args: str) -> str:
    args = args.strip()
    if target == "Math" and method in _MATH:
        return _MATH[method].format(args=args)
    if target == "Object" and method in ("keys", "values", "entries"):
        return f"the {method} of {args}"
    if target in ("Array",) and method == "from":
        return f"an array built from {args}"
    template = _METHODS.get(method)
    if template:
        return template.format(target=target, args=args or "it")
    if args:
        return f"calls {method} on {target} with {args}"
    return f"calls {method} on {target}"


def _describe_line(text: str) -> str | None:
    """One line of JavaScript in plain English, or None to leave it alone."""
    line = text.strip()
    if not line or line in ("{", "}", "});", ");", "};"):
        return None
    if line.startswith("//"):
        return None  # their own comment already says it
    if line.startswith("/*") or line.startswith("*"):
        return None

    match = _ARROW_DECL.match(line)
    if match:
        params = ", ".join(p.strip() for p in match.group(3).split(",") if p.strip())
        taking = f" taking {params}" if params else " taking nothing"
        return f"defines {match.group(2)} as a function{taking}."

    match = _DESTRUCTURE.match(line)
    if match:
        names = ", ".join(n.strip() for n in match.group(3).split(",") if n.strip())
        source = match.group(4).strip().rstrip(";")
        if match.group(2) == "[":
            return f"pulls {names} out of {source} by position."
        return f"pulls {names} out of {source} by name."

    match = _DECL.match(line)
    if match:
        keyword, name, value = match.groups()
        fixed = " (and never reassigns it)" if keyword == "const" else ""
        return f"sets {name} to {_describe_value(value)}{fixed}."

    match = _FUNCTION.match(line)
    if match:
        name = match.group(1) or "an unnamed function"
        params = ", ".join(p.strip() for p in match.group(2).split(",") if p.strip())
        taking = f", taking {params}" if params else ", taking nothing"
        return f"defines {name}{taking}."

    match = _CLASS.match(line)
    if match:
        base = f", based on {match.group(2)}" if match.group(2) else ""
        return f"defines a {match.group(1)} class{base}."

    match = _FOR_CLASSIC.match(line)
    if match:
        var, start, test, step = match.groups()
        return (
            f"counts {var} from {start.strip()} while {_readable(test)}, "
            f"doing {step.strip()} each time round."
        )

    match = _FOR_OF.match(line)
    if match:
        return f"goes through {match.group(2).strip()}, one {match.group(1).strip()} at a time."

    match = _FOR_IN.match(line)
    if match:
        return f"goes through the keys of {match.group(2).strip()}."

    match = _WHILE.match(line)
    if match:
        return f"keeps looping while {_readable(match.group(1))}."

    parts = _split_if(line)
    if parts:
        keyword, raw_condition, tail = parts
        lead = "otherwise, if" if keyword.startswith("else") else "if"
        condition = _readable(raw_condition)
        # A one-line `if (x) return y;` puts the whole story on one line, and
        # dropping the tail would lose the half that matters.
        tail = tail.lstrip("{").strip()
        if tail:
            inner = _describe_line(tail)
            if inner:
                return f"{lead} {condition}, {inner[0].lower()}{inner[1:]}"
        return f"{lead} {condition}, does what follows."

    if _ELSE.match(line):
        return "otherwise, does what follows."

    match = _RETURN.match(line)
    if match:
        value = match.group(1).strip()
        if not value:
            return "stops here and returns nothing."
        return f"hands back {_describe_value(value)}."

    match = _INCREMENT.match(line)
    if match:
        word = "up" if match.group(2) == "++" else "down"
        return f"moves {match.group(1)} {word} by one."

    match = _METHOD_CALL.match(line)
    if match:
        # Only the first letter — .capitalize() would lower-case the rest and
        # turn a variable called lastSeen into lastseen.
        described = _describe_method(*match.groups())
        return described[0].upper() + described[1:] + "."

    match = _ASSIGN.match(line)
    if match:
        name, op, value = match.groups()
        if op == "=":
            return f"sets {name} to {_describe_value(value)}."
        verb = {"+=": "adds", "-=": "subtracts", "*=": "multiplies by",
                "/=": "divides by"}[op]
        return f"{verb} {value.strip().rstrip(';')} {'to' if op == '+=' else 'from' if op == '-=' else ''} {name}.".replace(
            "  ", " "
        )

    match = _CALL.match(line)
    if match:
        name, args = match.groups()
        if name in ("console.log", "console.error"):
            return f"prints {args.strip() or 'a blank line'}."
        return f"calls {name}({args.strip()})."

    return None


def _depth_of(raw: str) -> int:
    """Indentation as a nesting level, two spaces per step."""
    stripped = raw.expandtabs(2)
    return max(0, (len(stripped) - len(stripped.lstrip(" "))) // 2)


def explain_js(code: str, trace: dict[str, Any] | None = None) -> dict[str, Any]:
    """Walk the code line by line, and say what running it produced."""
    raw_lines = code.splitlines()
    if not code.strip():
        return {
            "ok": False,
            "summary": "There's nothing in the editor yet.",
            "lines": [],
            "output_notes": [],
        }

    explained: list[dict[str, Any]] = []
    for number, raw in enumerate(raw_lines, start=1):
        text = _describe_line(raw)
        if text is None:
            continue
        explained.append(
            {
                "line": number,
                "depth": _depth_of(raw),
                "source": raw.strip(),
                "text": text,
            }
        )

    functions = [
        m.group(1)
        for m in re.finditer(r"function\s+([A-Za-z_$][\w$]*)", code)
        if m.group(1)
    ]
    if functions:
        summary = (
            f"This defines {_join(functions)}. Here's what each line does:"
        )
    else:
        summary = "Here's what each line does:"

    notes: list[str] = []
    error_note = None
    if trace:
        error = trace.get("error")
        if isinstance(error, dict) and error.get("message"):
            where = f" on line {error['line']}" if error.get("line") else ""
            error_note = (
                f"{error.get('type', 'Error')}{where}: {error['message']}"
            )
        elif error:
            error_note = str(error)

        printed = (trace.get("stdout") or "").strip()
        if printed:
            for piece in printed.splitlines()[:6]:
                notes.append(f"It printed: {piece}")
        steps = trace.get("steps") or []
        # One step means nothing ran but the definition itself, which tells
        # the reader nothing they can't see. Only mention a real run.
        if len(steps) > 1:
            plural = "" if len(steps) == 1 else "s"
            notes.append(
                f"It ran {len(steps)} step{plural}"
                + (", stopped early — long loop" if trace.get("truncated") else "")
                + "."
            )

    return {
        "ok": True,
        "summary": summary,
        "lines": explained,
        "output_notes": notes,
        "error_note": error_note,
    }


def _join(names: list[str]) -> str:
    unique = list(dict.fromkeys(names))
    if len(unique) == 1:
        return unique[0]
    return ", ".join(unique[:-1]) + f" and {unique[-1]}"
