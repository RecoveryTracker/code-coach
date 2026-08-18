"""Structural checks for the C-family languages — Dart, JavaScript, and any
other build lessons written with braces and parentheses.

Python's build lessons parse the student's code with `ast`, which won't help
here: there is no parser for these languages in the standard library, and
shelling out to a real one for every keystroke would be far too slow for a
check that runs on a debounce.

So these are text checks, written to be hard to satisfy by accident: comments
and string literals are stripped first, so the word `while` inside a comment
or a message doesn't count as a loop. They're looser than an AST — that's the
honest trade for not having a parser — but they still require real code.
"""

from __future__ import annotations

import re

_LINE_COMMENT = re.compile(r"//[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
# Dart strings: '...', "...", and their raw/interpolated forms. Good enough to
# stop keywords inside message text from counting as structure.
_STRINGS = re.compile(
    r"""(?:r?'(?:\\.|[^'\\])*'|r?"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)"""
)


def strip_noise(code: str) -> str:
    """Code with comments and string bodies removed."""
    out = _BLOCK_COMMENT.sub(" ", code)
    out = _LINE_COMMENT.sub(" ", out)
    return _STRINGS.sub("''", out)


def _has_keyword(code: str, word: str) -> bool:
    return re.search(rf"\b{word}\b\s*\(", strip_noise(code)) is not None


def uses_for(code: str) -> bool:
    return _has_keyword(code, "for")


def uses_while(code: str) -> bool:
    return _has_keyword(code, "while")


def uses_if(code: str) -> bool:
    return _has_keyword(code, "if")


def returns_value(code: str) -> bool:
    """A `return` that actually hands something back, not a bare `return;`."""
    return re.search(r"\breturn\s+[^;\s]", strip_noise(code)) is not None


def defines_function(code: str, name: str) -> bool:
    """`name(` preceded by something that isn't a call — a return type, or a
    modifier like `void`. A plain call `foo(1)` must not count as defining it.
    """
    clean = strip_noise(code)

    # JavaScript's other shape: `const twoSum = (a, b) => ...` or
    # `const twoSum = function (a, b) {`. The name is bound, not declared.
    assigned = rf"\b(?:const|let|var)\s+{re.escape(name)}\s*=\s*(?:async\s*)?(?:function\b|\(|[A-Za-z_$]\w*\s*=>)"
    if re.search(assigned, clean):
        return True

    # A definition is followed by a parameter list, optionally a return-type
    # annotation, and then `{` or `=>`. Without allowing the annotation,
    # `function twoSum(...): number[] {` reads as a call rather than a
    # definition, and the build lesson stops asking for the function at all.
    pattern = (
        rf"\b{re.escape(name)}\s*\([^)]*\)\s*(?::\s*[^;{{=]+)?"
        r"\s*(?:async\s*)?(?:\{|=>)"
    )
    for match in re.finditer(pattern, clean):
        before = clean[: match.start()].rstrip()
        # A call sits after `=`, `(`, `,`, `return`, or an operator; a
        # definition sits after a type, `void`, `function`, or a line start.
        if before.endswith(("=", "(", ",", "return", "+", "-", "*", "&&", "||", "!")):
            continue
        return True
    return False


def defines_class(code: str, name: str) -> bool:
    return re.search(rf"\bclass\s+{re.escape(name)}\b", strip_noise(code)) is not None


def top_level_names(code: str) -> tuple[list[str], list[str]]:
    """(function names, class names) declared in this source.

    Mirrors the Python helper's contract so the requirement builder can treat
    both languages the same way.
    """
    clean = strip_noise(code)
    classes = re.findall(r"\bclass\s+([A-Za-z_]\w*)", clean)
    funcs: list[str] = []
    keywords = {"if", "for", "while", "switch", "catch", "return", "function"}

    # `<type> name(params) {`, `function name(params) {`, or `... => ...`.
    decl = re.compile(
        r"(?:^|\n)\s*(?:(?:export|async)\s+)*(?:function\s+|[A-Za-z_][\w<>,?\s\[\]]*\s+)?"
        r"([a-zA-Z_$]\w*)\s*\([^;{}]*\)\s*(?::\s*[^;{=]+)?\s*(?:async\s*)?(?:\{|=>)"
    )
    for match in decl.finditer(clean):
        name = match.group(1)
        if name in keywords or name in funcs:
            continue
        funcs.append(name)

    # `const name = (…) => …` — declared by binding rather than by keyword.
    arrow = re.compile(
        r"(?:^|\n)\s*(?:const|let|var)\s+([a-zA-Z_$]\w*)\s*=\s*"
        r"(?:async\s*)?(?:function\b|\(|[A-Za-z_$]\w*\s*=>)"
    )
    for match in arrow.finditer(clean):
        name = match.group(1)
        if name not in funcs:
            funcs.append(name)
    return funcs, classes
