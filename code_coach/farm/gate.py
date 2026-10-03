"""The language gate: stop code that uses a part of the language you have not bought.

In The Farmer Was Replaced the language itself is research. You start able
only to call functions - harvest(), do_a_flip() - and buy the rest a piece
at a time: while with Loops, if with the first Speed, for with the second
Expand, then operators, variables, functions, lists and dictionaries.

Here programs are real Python, JavaScript or Dart, run as real processes,
and nothing in those languages stops a `while` before you own Loops. This
does, before the program starts: check() reads the code and names every
use of a feature that is still locked, with its line and the unlock that
brings it.

Two rules shape everything below.

* A syntax error is not the gate's business. Code that does not parse
  passes straight through (check() returns []), and the run reports the
  error in the language's own words, which say it better than we could.
* A false positive is worse than a miss. Refusing a program that is legal
  for you is a bug you cannot get round; letting a clever one through
  costs nothing. So where a reading is ambiguous - a[i] could be a list
  or a dictionary, `<` could open List<int> - the program gets the
  benefit of the doubt.

Python is read with its own ast module and JavaScript with the TypeScript
compiler's parser (gate_js.js, using the copy in web/node_modules). Dart
has no parser here, so it is read token by token, by the company each
token keeps; the notes in that section say where that reading stops.
"""

from __future__ import annotations

import ast
import bisect
import json
import re
import shutil
import subprocess
import warnings
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable

from code_coach.farm.data import LANGUAGE_FEATURES, UNLOCKS

HERE = Path(__file__).resolve().parent
GATE_JS = HERE / "gate_js.js"
#: The TypeScript compiler the web app installs; its parser reads JavaScript too.
TYPESCRIPT = HERE.parent.parent / "web" / "node_modules" / "typescript"
#: Loading TypeScript takes a third of a second; this is room for a busy machine.
JS_TIMEOUT_SECONDS = 20
#: A snippet longer than this is cut short.
SNIPPET_CHARS = 40


@dataclass(frozen=True)
class Violation:
    feature: str  # one of LANGUAGE_FEATURES
    line: int  # 1-based line in the user's code
    snippet: str  # the offending source text, short
    message: str  # plain words: "`while` needs Loops - buy it in the research tree."


@dataclass(frozen=True)
class _Use:
    """One use of a feature, found before anyone asks whether it is unlocked."""

    line: int
    #: Only for putting a line's uses in order.
    col: int
    feature: str
    snippet: str
    #: How the message names it: "`while`", "`+`", "A list".
    what: str
    #: a[i]: a list's index or a dictionary's key - the code cannot say which.
    index: bool = False


def check(code: str, language: str, unlocked: set[str]) -> list[Violation]:
    """Every use of a language feature not in `unlocked`, in source order, at most one per (feature, line)."""
    finder = _FINDERS.get(language.lower())
    if finder is None:
        raise ValueError(f"No language gate for {language!r}: it reads python, javascript and dart.")
    unlocked = set(unlocked)
    if unlocked.issuperset(LANGUAGE_FEATURES):
        return []  # everything bought: nothing to look for, and no node to start
    uses = finder(code)
    if uses is None:
        return []  # does not parse: the run will say so
    found: list[Violation] = []
    seen: set[tuple[str, int]] = set()
    for use in sorted(uses, key=lambda u: (u.line, u.col)):
        if use.feature in unlocked:
            continue
        # With dictionaries bought, a[i] may well be one: let it through.
        if use.index and "dicts" in unlocked:
            continue
        if (use.feature, use.line) in seen:
            continue
        seen.add((use.feature, use.line))
        found.append(Violation(use.feature, use.line, _short(use.snippet), _message(use)))
    return found


def _unlock_table() -> dict[str, tuple[str, int]]:
    table: dict[str, tuple[str, int]] = {}
    for unlock in UNLOCKS.values():
        for level, features in sorted(unlock.features.items()):
            for feature in features:
                table.setdefault(feature, (unlock.name, level))
    return table


_UNLOCK_FOR = _unlock_table()


def unlock_for(feature: str) -> tuple[str, int]:
    """The research that brings a language feature, and the level: ("Expand", 2) for `for`."""
    try:
        return _UNLOCK_FOR[feature]
    except KeyError:
        raise KeyError(f"No unlock gives the language feature {feature!r}.") from None


def _message(use: _Use) -> str:
    if use.index:
        return f"{use.what} needs Lists or Dictionaries - buy one in the research tree."
    name, level = unlock_for(use.feature)
    title = name.replace("_", " ") + (f" level {level}" if level > 1 else "")
    if UNLOCKS[name].missing:
        return f"{use.what} needs {title}, which Code Coach does not have yet."
    return f"{use.what} needs {title} - buy it in the research tree."


def _short(text: str) -> str:
    """The first line of the source, cut to SNIPPET_CHARS."""
    lines = text.strip().splitlines()
    first = lines[0].strip() if lines else ""
    if len(first) > SNIPPET_CHARS:
        first = first[: SNIPPET_CHARS - 3].rstrip() + "..."
    return first


# ── Python ──────────────────────────────────────────────────────────────

_PY_BINARY = {
    ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.FloorDiv: "//",
    ast.Mod: "%", ast.Pow: "**", ast.MatMult: "@", ast.LShift: "<<", ast.RShift: ">>",
    ast.BitOr: "|", ast.BitXor: "^", ast.BitAnd: "&",
}
_PY_COMPARE = {
    ast.Eq: "==", ast.NotEq: "!=", ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
    ast.Is: "is", ast.IsNot: "is not", ast.In: "in", ast.NotIn: "not in",
}
_PY_UNARY = {ast.Not: "not", ast.Invert: "~", ast.USub: "-", ast.UAdd: "+"}
#: Calling these builds the collection as surely as writing one out does.
_PY_MAKERS = {
    "list": ("lists", "`list()`"),
    "dict": ("dicts", "`dict()`"),
    "set": ("dicts", "`set()`"),
    "frozenset": ("dicts", "`frozenset()`"),
}
#: Type annotations are not code that runs: `-> tuple[int, int]` is no index,
#: and `int | None` no operator. The walk does not go into them.
_PY_TYPE_FIELDS = frozenset(("annotation", "returns", "type_params"))
_PY_TYPE_ALIAS = getattr(ast, "TypeAlias", None)  # `type X = ...`, Python 3.12+


def _python_uses(code: str) -> list[_Use] | None:
    try:
        with warnings.catch_warnings():
            # "\d" and friends warn as they parse. The run will show that
            # warning where it belongs; the gate should not print it as well.
            warnings.simplefilter("ignore")
            tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    uses: list[_Use] = []

    def add(node: ast.AST, feature: str, what: str, at: ast.AST | None = None, index: bool = False) -> None:
        where = node if at is None else at
        snippet = ast.get_source_segment(code, node) or ""
        uses.append(_Use(where.lineno, where.col_offset, feature, snippet, what, index))

    todo: list[ast.AST] = [tree]
    while todo:
        node = todo.pop()
        if _PY_TYPE_ALIAS is not None and isinstance(node, _PY_TYPE_ALIAS):
            continue
        _python_node(node, add)
        for name, value in ast.iter_fields(node):
            if name in _PY_TYPE_FIELDS:
                continue
            if isinstance(value, ast.AST):
                todo.append(value)
            elif isinstance(value, list):
                todo.extend(v for v in value if isinstance(v, ast.AST))
    return uses


def _py_number(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and type(node.value) in (int, float, complex)


def _python_node(node: ast.AST, add: Callable[..., None]) -> None:
    if isinstance(node, ast.While):
        add(node, "while", "`while`")
    elif isinstance(node, ast.If):  # elif too: it is an if of its own, on its own line
        add(node, "if", "`if`")
    elif isinstance(node, ast.IfExp):
        add(node, "if", "`if`")
    elif isinstance(node, ast.Match):  # an if by another name
        add(node, "if", "`match`")
    elif isinstance(node, (ast.For, ast.AsyncFor)):
        # Not the loop variable: `for i in range(3)` is free of Variables,
        # as it is in the game.
        add(node, "for", "`for`")
    elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        for loop in node.generators:
            add(node, "for", "`for`", at=loop.target)
            for condition in loop.ifs:
                add(node, "if", "`if`", at=condition)
        if isinstance(node, ast.ListComp):
            add(node, "lists", "A list")
        elif isinstance(node, ast.SetComp):
            add(node, "dicts", "A set")
        elif isinstance(node, ast.DictComp):
            add(node, "dicts", "A dictionary")
    elif isinstance(node, ast.BinOp):
        add(node, "operators", f"`{_PY_BINARY[type(node.op)]}`")
    elif isinstance(node, ast.BoolOp):
        add(node, "operators", "`and`" if isinstance(node.op, ast.And) else "`or`")
    elif isinstance(node, ast.Compare):
        add(node, "operators", f"`{_PY_COMPARE[type(node.ops[0])]}`")
    elif isinstance(node, ast.UnaryOp):
        # -1 is a number, not the minus operator applied to one: free, as in the game.
        if not (isinstance(node.op, (ast.USub, ast.UAdd)) and _py_number(node.operand)):
            add(node, "operators", f"`{_PY_UNARY[type(node.op)]}`")
    elif isinstance(node, ast.AugAssign):
        add(node, "operators", f"`{_PY_BINARY[type(node.op)]}=`")
        add(node, "variables", "A variable")
    elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
        add(node, "variables", "A variable")
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        # Parameters are the function's, not variables of yours.
        add(node, "functions", "A function of your own")
    elif isinstance(node, ast.ClassDef):
        add(node, "functions", "A class of your own")
    elif isinstance(node, ast.List):
        add(node, "lists", "A list")
    elif isinstance(node, ast.Subscript):
        add(node, "lists", "Indexing with `[ ]`", index=True)
    elif isinstance(node, ast.Dict):
        add(node, "dicts", "A dictionary")
    elif isinstance(node, ast.Set):
        add(node, "dicts", "A set")
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        add(node, "import", "`import`")
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _PY_MAKERS:
        feature, what = _PY_MAKERS[node.func.id]
        add(node, feature, what)
    # Everything else is free: calls, names, attributes (Entities.Bush),
    # constants, tuples, strings and f-strings (their {...} are walked).


# ── JavaScript ──────────────────────────────────────────────────────────


def _javascript_uses(code: str) -> list[_Use] | None:
    node = shutil.which("node")
    if node is None or not TYPESCRIPT.is_dir():
        return None  # nothing to read it with: let it run rather than block it
    found = _ask_node(node, code)
    return None if found is None else list(found)


@lru_cache(maxsize=64)
def _ask_node(node: str, code: str) -> tuple[_Use, ...] | None:
    """gate_js.js's reading of the code. Remembered: pressing Run twice asks once."""
    try:
        done = subprocess.run(
            [node, str(GATE_JS), str(TYPESCRIPT)],
            input=code.encode("utf-8"),
            capture_output=True,
            timeout=JS_TIMEOUT_SECONDS,
        )
        found = json.loads(done.stdout.decode("utf-8"))
    except (OSError, subprocess.TimeoutExpired, UnicodeDecodeError, ValueError):
        return None
    if not isinstance(found, list):
        return None
    try:
        return tuple(
            _Use(int(f["line"]), int(f["col"]), str(f["feature"]), str(f["snippet"]),
                 str(f["what"]), bool(f.get("index")))
            for f in found
        )
    except (KeyError, TypeError, ValueError):
        return None


# ── Dart ────────────────────────────────────────────────────────────────
#
# No Dart parser is installed, so Dart is read in two steps. A tokenizer
# drops comments and strings (keeping what is inside each ${...}, which is
# code) and splits the rest into names, numbers and symbols. Then each
# token is judged by the company it keeps:
#
#   <  >   type arguments in List<int> and Map<Items, num> - a name, then
#          only names, commas, dots and ? up to the matching > - are not
#          comparisons. `count < 3` has a number in it and is.
#   {      after ) else do try or a name it opens a block; after = ( , [ :
#          return => ?? or a bare <K, V> it opens a map or set literal.
#   [      after a value (a name, ), ]) it indexes; otherwise it is a list.
#   !      after a value it asserts non-null, otherwise it is `not`.
#   -      before a number, with no value in front, it is part of the number.
#   ( ){   a parameter list followed by a body is a function, unless it is
#          the program's own main().
#
# Where that reading cannot decide, it lets the program through. The gaps
# it knows of: the ?: conditional is not flagged at all (`int? x` makes `?`
# too ambiguous); `f(a < b, c > d)` reads as type arguments, so neither
# comparison is flagged; a declaration with no `var` and no `=` is only
# seen at the start of a statement (`int x;`), so `static int x;` in a
# class is missed; and code that does not tokenize - an unclosed string
# or comment, unmatched brackets - counts as not parsing, so passes
# straight to the run that reports it.

#: Dart's reserved words, and the words it reserves only in places, none of
#: which is ever the name of a type or a value where the reading looks for one.
_DART_KEYWORDS = frozenset((
    "assert break case catch class const continue default do else enum extends false final "
    "finally for if in is new null rethrow return super switch this throw true try var void "
    "while with abstract as async await augment base covariant deferred export extension "
    "external factory hide implements import interface late library mixin of on operator "
    "part required sealed show static sync typedef when yield"
).split())
#: Keywords that are values: `this[0]` indexes, `true == x` compares.
_DART_VALUES = frozenset(("this", "super", "true", "false", "null"))
#: A '(' after these is a header or a call, never a parameter list.
_DART_HEADS = frozenset(("if", "while", "for", "switch", "catch", "when", "assert", "super", "this"))
#: After these a '{' opens a literal (`return {...}`), not a block.
_DART_LITERAL_AFTER = frozenset(("return", "const", "in", "yield", "await", "throw", "case"))
#: After `List<int>` these mean the < > were a comparison after all.
_DART_NOT_AFTER_TYPE = frozenset(("-", "+", "*", "/", "%", "~/", "[", "<", "<<", "~", "++", "--"))
_DART_BINARY = frozenset((
    "+", "/", "%", "~/", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "??", "&", "|", "^",
    "<<", ">>", ">>>",
))
_DART_COMPOUND = frozenset((
    "+=", "-=", "*=", "/=", "~/=", "%=", "<<=", ">>=", ">>>=", "&=", "|=", "^=", "??=",
))
#: Building a collection by its constructor - Map(), List.filled(3, 0) - uses it
#: as much as writing one out.
_DART_MAKERS = {
    "List": ("lists", "A `List`"),
    **{name: ("dicts", f"A `{name}`") for name in (
        "Map", "HashMap", "LinkedHashMap", "SplayTreeMap",
        "Set", "HashSet", "LinkedHashSet", "SplayTreeSet",
    )},
}
_DART_OPS = (
    ">>>=", "...?", "~/=", ">>>", ">>=", "<<=", "??=", "?..", "...",
    "==", "!=", "<=", ">=", "&&", "||", "??", "?.", "..", "=>", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "~/", "<<", ">>",
    "+", "-", "*", "/", "%", "<", ">", "=", "!", "?", ":", ";", ",", ".",
    "(", ")", "[", "]", "{", "}", "&", "|", "^", "~", "@", "#",
)
_DART_OP = re.compile("|".join(re.escape(op) for op in sorted(_DART_OPS, key=len, reverse=True)))
_DART_NAME = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
_DART_NUMBER = re.compile(
    r"0[xX][0-9A-Fa-f_]+|(?:[0-9][0-9_]*(?:\.[0-9][0-9_]*)?|\.[0-9][0-9_]*)(?:[eE][+-]?[0-9][0-9_]*)?"
)
_OPENER = {")": "(", "]": "[", "}": "{"}


@dataclass(slots=True)
class _Tok:
    kind: str  # "name", "number", "string" or "op"
    text: str
    pos: int
    line: int
    #: For a string: the tokens inside each ${...} - which are code.
    parts: tuple[tuple[_Tok, ...], ...] = ()


class _Unparsable(Exception):
    """The code does not tokenize: an unclosed string or comment, a stray character."""


def _digit(c: str) -> bool:
    return c != "" and "0" <= c <= "9"  # not str.isdigit, which says yes to "²"


class _DartLexer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.starts = [0] + [m.end() for m in re.finditer("\n", code)]

    def line(self, pos: int) -> int:
        return bisect.bisect_right(self.starts, pos)

    def tokens(self, i: int, interpolation: bool = False) -> tuple[list[_Tok], int]:
        """Tokens from i to the end - or, inside ${...}, to its closing brace."""
        code, n = self.code, len(self.code)
        out: list[_Tok] = []
        depth = 0
        while i < n:
            c = code[i]
            if c.isspace():
                i += 1
            elif code.startswith("//", i):
                end = code.find("\n", i)
                i = n if end < 0 else end
            elif code.startswith("/*", i):
                i = self.comment(i)
            elif c in "'\"" or (c == "r" and code[i + 1:i + 2] in ("'", '"')):
                token, i = self.string(i)
                out.append(token)
            elif _digit(c) or (c == "." and _digit(code[i + 1:i + 2])):
                m = _DART_NUMBER.match(code, i)
                assert m is not None
                out.append(_Tok("number", m.group(), i, self.line(i)))
                i = m.end()
            elif m := _DART_NAME.match(code, i):
                out.append(_Tok("name", m.group(), i, self.line(i)))
                i = m.end()
            elif m := _DART_OP.match(code, i):
                text = m.group()
                if interpolation and text == "}":
                    if depth == 0:
                        return out, i + 1
                    depth -= 1
                elif interpolation and text == "{":
                    depth += 1
                out.append(_Tok("op", text, i, self.line(i)))
                i = m.end()
            else:
                raise _Unparsable(c)
        if interpolation:
            raise _Unparsable("${ never closed")
        return out, i

    def comment(self, i: int) -> int:
        """Past a /* */ comment. Dart lets them nest."""
        code, n = self.code, len(self.code)
        depth = 0
        while i < n:
            if code.startswith("/*", i):
                depth += 1
                i += 2
            elif code.startswith("*/", i):
                depth -= 1
                i += 2
                if depth == 0:
                    return i
            else:
                i += 1
        raise _Unparsable("comment never closed")

    def string(self, start: int) -> tuple[_Tok, int]:
        """One string literal: '...', "...", '''...''', r'...'; ${...} inside is lexed as code."""
        code, n = self.code, len(self.code)
        raw = code[start] == "r"
        q = start + 1 if raw else start
        quote = code[q]
        delim = quote * 3 if code.startswith(quote * 3, q) else quote
        i = q + len(delim)
        parts: list[tuple[_Tok, ...]] = []
        while True:
            if i >= n:
                raise _Unparsable("string never closed")
            if code.startswith(delim, i):
                i += len(delim)
                break
            c = code[i]
            if c == "\n" and len(delim) == 1:
                raise _Unparsable("string never closed")
            if c == "\\" and not raw:
                i += 2
            elif c == "$" and not raw and code.startswith("{", i + 1):
                inner, i = self.tokens(i + 2, interpolation=True)
                parts.append(tuple(inner))
            else:
                i += 1  # $name reads a variable, which is free
        return _Tok("string", code[start:i], start, self.line(start), tuple(parts)), i


def _dart_uses(code: str) -> list[_Use] | None:
    code = code.removeprefix("﻿").replace("\r\n", "\n").replace("\r", "\n")
    if code.startswith("#!"):  # a script tag, `#!/usr/bin/env dart`: keep its line, not its text
        end = code.find("\n")
        code = "" if end < 0 else code[end:]
    try:
        tokens, _ = _DartLexer(code).tokens(0)
    except (_Unparsable, RecursionError):
        return None
    lines = code.split("\n")

    def line_text(line: int) -> str:
        return lines[line - 1].strip() if 0 < line <= len(lines) else ""

    scan = _DartScan(tokens, line_text)
    return scan.uses if scan.ok else None


class _DartScan:
    """The features one run of Dart tokens uses: a whole file, or one ${...}."""

    def __init__(self, tokens: list[_Tok], line_text: Callable[[int], str]) -> None:
        self.t = tokens
        self.n = len(tokens)
        self.line_text = line_text
        self.uses: list[_Use] = []
        self.ok = self._brackets()
        if not self.ok:
            return
        self._type_arguments()
        self._bodies()
        self._parameters()
        self._loops()
        self._walk()

    # ── what the tokens are ──

    def _brackets(self) -> bool:
        """Pair up ( ) [ ] { }, and note the innermost bracket around each token."""
        t = self.t
        self.match = [-1] * self.n
        self.encl = [-1] * self.n
        stack: list[int] = []
        for i, tok in enumerate(t):
            x = tok.text if tok.kind == "op" else ""
            if x in _OPENER:
                if not stack or t[stack[-1]].text != _OPENER[x]:
                    return False
                j = stack.pop()
                self.match[i], self.match[j] = j, i
            self.encl[i] = stack[-1] if stack else -1
            if x in ("(", "[", "{"):
                stack.append(i)
        return not stack

    def _type_arguments(self) -> None:
        """Find the types, which are not code: the < > of List<int> and <int>[], record types."""
        self.span: dict[int, int] = {}  # '<' -> the '>' (or '>>') that closes it
        self.span_from: dict[int, int] = {}  # and back
        self.named: dict[int, bool] = {}  # '<' -> follows a name (List<int>), not a bare <int>[]
        self.typed = [False] * self.n
        i = 0
        while i < self.n:
            tok = self.t[i]
            found = self._type_arguments_at(i) if tok.kind == "op" and tok.text == "<" else None
            if found is None:
                i += 1
                continue
            end, named = found
            self.span[i], self.span_from[end], self.named[i] = end, i, named
            for k in range(i, end + 1):
                self.typed[k] = True
            i = end + 1
        # `(int, int) p;`, `({int x, int y}) p;`: brackets followed by a name
        # are a record type - an expression is never followed by a name - so
        # the { } in one is no map. Not after `if` or `while`, whose
        # (condition) can be followed by the statement it guards.
        self.records: set[int] = set()
        t, n = self.t, self.n
        for p, tok in enumerate(t):
            if self.typed[p] or tok.kind != "op" or tok.text != "(":
                continue
            if p and t[p - 1].kind == "name" and t[p - 1].text in _DART_HEADS:
                continue
            k = self.match[p] + 1
            if k < n and t[k].text == "?":
                k += 1
            if k < n and t[k].kind == "name" and t[k].text not in _DART_KEYWORDS:
                self.records.add(p)
                for m in range(p, self.match[p] + 1):
                    self.typed[m] = True

    def _type_arguments_at(self, i: int) -> tuple[int, bool] | None:
        t, n = self.t, self.n
        before = t[i - 1] if i else None
        if before is not None and before.kind == "name" and before.text not in _DART_KEYWORDS:
            named = True
        elif self._value_end(i - 1):
            return None  # `f() < g`, `2 < x`: a comparison
        else:
            named = False  # `= <int>[]`, `return <String, int>{}`
        depth, parens, j = 1, 0, i + 1
        while j < n:
            tok = t[j]
            x = tok.text
            if tok.kind == "name":
                pass
            elif tok.kind != "op":
                return None  # a number or a string: not a type
            elif x == "<":
                depth += 1
            elif x in (">", ">>", ">>>"):
                depth -= len(x)  # List<List<int>> closes two at once
                if depth <= 0:
                    break
            elif x in (",", ".", "?"):
                pass
            elif x == "(":  # record and function types: <(int, int)>, <void Function(int)>
                parens += 1
            elif x == ")":
                parens -= 1
                if parens < 0:
                    return None  # `if (i < n)`
            elif x in ("{", "}") and parens:
                pass
            else:
                return None  # `&&`, `+`, `;` ...: an expression, so a comparison
            j += 1
        else:
            return None
        if depth != 0 or parens != 0:
            return None
        after = t[j + 1] if j + 1 < n else None
        if named:
            if after is not None and (after.kind in ("number", "string") or after.text in _DART_NOT_AFTER_TYPE):
                return None
        elif after is None or after.text not in ("[", "{", "("):
            return None
        return j, named

    def _bodies(self) -> None:
        """The braces of switch and class bodies: blocks, whatever comes before them."""
        t, n = self.t, self.n
        self.switch_body: set[int] = set()
        self.class_body: set[int] = set()
        for i, tok in enumerate(t):
            if tok.kind != "name" or self.typed[i]:
                continue
            if tok.text == "switch" and i + 1 < n and t[i + 1].text == "(":
                after = self.match[i + 1] + 1
                if after < n and t[after].text == "{":
                    self.switch_body.add(after)
            elif self._declares_type(i):
                j = i + 1
                while j < n and t[j].text not in ("{", ";", "}", ")", "]", "="):
                    j = self.match[j] + 1 if t[j].text in ("(", "[") and t[j].kind == "op" else j + 1
                if j < n and t[j].text == "{":
                    self.class_body.add(j)

    def _declares_type(self, i: int) -> bool:
        """`class`, `enum`, `mixin M`, `extension on X`: a type of your own."""
        word = self.t[i].text
        if word in ("class", "enum"):
            return True
        after = self.t[i + 1] if i + 1 < self.n else None
        return word in ("mixin", "extension") and after is not None and after.kind == "name"

    def _parameters(self) -> None:
        """Find parameter lists, and the function definitions they belong to."""
        t, n = self.t, self.n
        self.params: set[int] = set()  # '(' of every parameter list
        self.defs: list[int] = []  # where to report each function definition
        for p in range(n):
            if t[p].kind != "op" or t[p].text != "(" or self.typed[p]:
                continue
            q = self.match[p]
            name = p - 1
            if name in self.span_from:  # f<T>(...)
                name = self.span_from[name] - 1
            head = t[name] if name >= 0 else None
            named = head is not None and head.kind == "name"
            if named and head.text == "Function":  # a function type: parameters, no body
                self.params.add(p)
                continue
            if named and head.text in _DART_HEADS:
                continue
            body = self._body_after(q)
            # `int add(` - a type, then a name: only a declaration looks like that.
            declared = named and head.text not in _DART_KEYWORDS and self._type_end(name - 1)
            # `Point(this.x);` - a constructor, at the start of a class member.
            member = named and self.encl[p] in self.class_body and self._member_start(name)
            if body is None and not declared and not member:
                continue  # a call, or brackets round an expression
            if body is not None and not declared and self.encl[p] in self.switch_body:
                continue  # `(0, 0) => 'corner'`: a pattern in a switch, not a function
            self.params.add(p)
            after = t[q + 1].text if q + 1 < n else ""
            if body is None and after != ";" and not (member and after == ":"):
                continue  # a function-typed parameter: `void f(int g(int x))`
            if named and head.text == "main" and self.encl[p] == -1:
                continue  # main() is the program itself, not a function of yours
            self.defs.append(name if named else p)

    def _body_after(self, q: int) -> int | None:
        """After a ')': the '{' or '=>' of a function body, or None."""
        t, n = self.t, self.n
        k = q + 1
        if k < n and t[k].kind == "name" and t[k].text in ("async", "sync"):
            k += 1
            if k < n and t[k].text == "*":
                k += 1
        if k < n and t[k].kind == "op" and t[k].text in ("{", "=>"):
            return k
        return None

    def _type_end(self, k: int) -> bool:
        """Could token k end a type - the `int` of `int f(`, the `>` of `List<int> f(`?"""
        if k < 0:
            return False
        tok = self.t[k]
        if tok.kind == "name":
            return tok.text not in _DART_KEYWORDS or tok.text == "void"
        if k in self.span_from:
            return self.named[self.span_from[k]]
        if tok.text == "?":  # int? f(
            return self._type_end(k - 1)
        return False

    def _member_start(self, k: int) -> bool:
        """Is the name at k the first word of a class member: `Point(`, `const Point.origin(`?"""
        t = self.t
        j = k - 1
        if j >= 1 and t[j].text == "." and t[j - 1].kind == "name":
            j -= 2
        while j >= 0 and t[j].kind == "name" and t[j].text in ("const", "factory", "external"):
            j -= 1
        return j < 0 or t[j].text in ("{", "}", ";")

    def _loops(self) -> None:
        """For-in loop variables, and the `while` that ends a do { } while."""
        t, n = self.t, self.n
        self.binding = [False] * n
        self.trailer: set[int] = set()
        for i, tok in enumerate(t):
            if tok.kind != "name" or i + 1 >= n or t[i + 1].kind != "op":
                continue
            if tok.text == "for" and t[i + 1].text == "(":
                # `for (final x in xs)` names x for the loop - the loop's, as
                # `i` is in Python's `for i in range(3)` - not a variable of yours.
                o = i + 1
                for k in range(o + 1, self.match[o]):
                    if self.encl[k] == o and t[k].kind == "name" and t[k].text == "in":
                        for m in range(o + 1, k):
                            self.binding[m] = True
                        break
            elif tok.text == "do" and t[i + 1].text == "{":
                after = self.match[i + 1] + 1
                if after < n and t[after].text == "while":
                    self.trailer.add(after)  # one loop, already counted at `do`

    def _value_end(self, k: int) -> bool:
        """Does token k end a value? Then a '-' after it subtracts, '[' indexes, '!' asserts."""
        if k < 0:
            return False
        tok = self.t[k]
        if tok.kind in ("number", "string"):
            return True
        if tok.kind == "name":
            return tok.text in _DART_VALUES or tok.text not in _DART_KEYWORDS
        if tok.text == ")":
            return not self._header_close(k)  # `if (x) -1` is no subtraction
        if tok.text == "]":
            return True
        if tok.text in ("!", "++", "--"):  # x! and x++ are still values; !x was not one
            return self._value_end(k - 1)
        return False

    def _header_close(self, k: int) -> bool:
        """Is the ')' at k the end of an if/while/for/switch/catch header?"""
        o = self.match[k]
        return o >= 1 and self.t[o - 1].kind == "name" and self.t[o - 1].text in (
            "if", "while", "for", "switch", "catch")

    def _in_params(self, i: int) -> bool:
        """Inside a parameter list - `{int x = 0}` - where = gives a default, not a variable."""
        e = self.encl[i]
        if e < 0:
            return False
        if e in self.params:
            return True
        return self.t[e].text in ("{", "[") and self.encl[e] in self.params

    def _group(self, i: int) -> bool:
        """The { } or [ ] that hold named or optional parameters, not a literal."""
        return self.encl[i] in self.params

    # ── what they are used for ──

    def _walk(self) -> None:
        t = self.t
        self.block: set[int] = set()  # '{' that open blocks and bodies, not literals
        labels: set[int] = set()  # the ':' of `case 1:`, `default:`, `outer:`
        # One frame per open bracket: [the bracket, holds statements, first token of the statement so far]
        frames: list[list] = [[-1, True, None]]
        fresh = True  # the next token starts a statement
        for i, tok in enumerate(t):
            frame = frames[-1]
            if frame[1] and fresh:
                frame[2] = i
                fresh = False
                self._declaration(i)
            x = tok.text if tok.kind == "op" else None
            if x == "{" and self._is_block(i, labels):
                self.block.add(i)
            if not self.typed[i]:
                self._token(i, frame[2] if frame[1] else None)
            if x in ("(", "["):
                frames.append([i, False, None])
            elif x == "{":
                frames.append([i, i in self.block, None])
                fresh = True
            elif x in (")", "]", "}"):
                frames.pop()
                if x == "}" or (x == ")" and self._header_close(i)):
                    fresh = True
            elif x == ";":
                fresh = True
            elif x == ":" and frame[1] and self._is_label(frame[2], i):
                labels.add(i)
                fresh = True
            elif tok.kind == "name" and tok.text in ("else", "do", "try", "finally"):
                fresh = True
        for k in self.defs:
            self._add(k, "functions", "A function of your own")

    def _is_block(self, i: int, labels: set[int]) -> bool:
        """Does the '{' at i open a block (or a body), rather than a map or set literal?"""
        if i in self.class_body or i in self.switch_body:
            return True
        if i == 0 or self._group(i):
            return i == 0
        t = self.t
        before = t[i - 1]
        x = before.text
        if before.kind == "name":
            return x not in _DART_LITERAL_AFTER  # `class A {`, `else {`, `get x {`, `async {`
        if before.kind != "op":
            return True  # after a string or number: not Dart, so not ours to flag
        if x == ")":
            o = self.match[i - 1]
            if o >= 1 and t[o - 1].kind == "name" and t[o - 1].text in ("if", "for") and self._in_collection(o - 1):
                return False  # `[if (c) {1}]`: an element of a list, not a block
            return True
        if x in (";", "}"):
            return True
        if x == "{":
            return i - 1 in self.block  # `{ {` nests blocks, `{{1}}` a set in a set
        if x == "*":
            return i >= 2 and t[i - 2].text in ("async", "sync")
        if x == ":":
            return i - 1 in labels  # `case 1: {` is a block; `{'a': {}}` a map
        if i - 1 in self.span_from:
            return self.named[self.span_from[i - 1]]  # `class Box<T> {` - but `<int, int>{}` is a map
        return False  # after = ( , [ => ?? ... : a value goes here, so a literal

    def _in_collection(self, k: int) -> bool:
        """Is the `if`/`for` at k an element of a list, map or set literal?"""
        e = self.encl[k]
        return e >= 0 and (self.t[e].text == "[" or (self.t[e].text == "{" and e not in self.block))

    def _is_label(self, first: int | None, colon: int) -> bool:
        if first is None:
            return False
        word = self.t[first]
        if word.kind == "name" and word.text in ("case", "default"):
            return True
        return first == colon - 1 and word.kind == "name" and word.text not in _DART_KEYWORDS

    def _declaration(self, i: int) -> None:
        """`int x;`, `Entities? e = ...`, `List<int> xs;`: a variable with a type and no `var`."""
        t, n = self.t, self.n
        if i in self.records:  # (int, int) p;
            j = self.match[i] + 1
        elif t[i].kind != "name" or t[i].text in _DART_KEYWORDS or self.binding[i]:
            return
        else:
            j = i + 1
        while j + 1 < n and t[j].text == "." and t[j + 1].kind == "name":
            j += 2
        if j < n and j in self.span:
            j = self.span[j] + 1
        if j < n and t[j].text == "?":
            j += 1
        if (j + 1 < n and t[j].kind == "name" and t[j].text not in _DART_KEYWORDS
                and t[j + 1].text in (";", ",", "=")):
            self._add(j, "variables", "A variable")

    def _token(self, i: int, first: int | None) -> None:
        t, n = self.t, self.n
        tok = t[i]
        x = tok.text
        if tok.kind == "string":
            for part in tok.parts:
                self._interpolation(part)
        elif tok.kind == "name":
            self._word(i)
        elif tok.kind != "op":
            pass
        elif x == "=":
            # Not a parameter's default, not `typedef F = ...`.
            if not self._in_params(i) and not (first is not None and t[first].text == "typedef"):
                self._add(i, "variables", "A variable")
        elif x in _DART_COMPOUND or x in ("++", "--"):
            self._add(i, "operators", f"`{x}`")
            self._add(i, "variables", "A variable")
        elif x == "-":
            # -1 is a number, not the minus operator applied to one: free, as in the game.
            if self._value_end(i - 1) or not (i + 1 < n and t[i + 1].kind == "number"):
                self._add(i, "operators", "`-`")
        elif x == "*":
            if not (i and t[i - 1].kind == "name" and t[i - 1].text in ("async", "sync", "yield")):
                self._add(i, "operators", "`*`")
        elif x == "!":
            if not self._value_end(i - 1):  # x! asserts non-null: not an operator of the game's
                self._add(i, "operators", "`!`")
        elif x in _DART_BINARY or x == "~":
            self._add(i, "operators", f"`{x}`")
        elif x == "[":
            if self._group(i):
                return
            if self._value_end(i - 1) or self._null_aware_index(i):
                self._add(i, "lists", "Indexing with `[ ]`", index=True)
            else:
                self._add(i, "lists", "A list")
        elif x == "{":
            if i not in self.block and not self._group(i):
                self._add(i, "dicts", "A map or set")
        elif x == "=>":
            self._arrow(i)

    def _word(self, i: int) -> None:
        t, n = self.t, self.n
        x = t[i].text
        after = t[i + 1] if i + 1 < n else None
        if x == "while":
            if i not in self.trailer:
                self._add(i, "while", "`while`")
        elif x == "do":
            self._add(i, "while", "`do ... while`")
        elif x == "if":
            self._add(i, "if", "`if`")
        elif x == "switch":  # an if by another name
            self._add(i, "if", "`switch`")
        elif x == "for":
            self._add(i, "for", "`for`")
        elif x in ("var", "final", "late"):
            if not self.binding[i] and not self._in_params(i):
                self._add(i, "variables", "A variable")
        elif x == "is":
            self._add(i, "operators", "`is`")
        elif x in ("import", "export", "part"):
            if after is not None and (after.kind == "string" or after.text == "of"):
                self._add(i, "import", f"`{x}`")
        elif self._declares_type(i):
            self._add(i, "functions", "An enum of your own" if x == "enum" else "A class of your own")
        elif x == "get":
            if after is not None and after.kind == "name" and i + 2 < n and t[i + 2].text in ("{", "=>"):
                self._add(i, "functions", "A function of your own")
        elif x in _DART_MAKERS and self._constructs(i):
            self._add(i, *_DART_MAKERS[x])

    def _constructs(self, i: int) -> bool:
        """`Map()`, `Set<int>()`, `List.filled(3, 0)`: building one, not naming the type."""
        t, n = self.t, self.n
        if i and t[i - 1].text == ".":
            return False
        j = i + 1
        if j < n and j in self.span:
            j = self.span[j] + 1
        return j < n and t[j].kind == "op" and t[j].text in ("(", ".")

    def _arrow(self, i: int) -> None:
        """`=>` makes a function - unless its definition is already counted, or it is a switch arm."""
        t = self.t
        k = i - 1
        if k >= 0 and t[k].text == "*":
            k -= 1
        if k >= 0 and t[k].kind == "name" and t[k].text in ("async", "sync"):
            k -= 1
        if k >= 0 and t[k].kind == "op" and t[k].text == ")" and self.match[k] in self.params:
            return  # counted with its parameter list
        if k >= 1 and t[k].kind == "name" and t[k - 1].kind == "name" and t[k - 1].text == "get":
            return  # a getter, counted at `get`
        if self.encl[i] in self.switch_body:
            return  # `Entities.bush => 1,`
        self._add(i, "functions", "A function of your own")

    def _null_aware_index(self, i: int) -> bool:
        """`m?[key]`: the ? is part of the index, not the start of a conditional."""
        t = self.t
        return i >= 2 and t[i - 1].text == "?" and t[i - 1].pos + 1 == t[i].pos and self._value_end(i - 2)

    def _interpolation(self, part: tuple[_Tok, ...]) -> None:
        """The code in one ${...}, read as the expression it is."""
        if not part:
            self.ok = False  # `${}` is not Dart
            return
        open_, close = _Tok("op", "(", part[0].pos, part[0].line), _Tok("op", ")", part[-1].pos, part[-1].line)
        inner = _DartScan([open_, *part, close], self.line_text)
        self.ok = self.ok and inner.ok
        self.uses.extend(inner.uses)

    def _add(self, k: int, feature: str, what: str, index: bool = False) -> None:
        tok = self.t[k]
        self.uses.append(_Use(tok.line, tok.pos, feature, self.line_text(tok.line), what, index))


_FINDERS: dict[str, Callable[[str], list[_Use] | None]] = {
    "python": _python_uses,
    "py": _python_uses,
    "javascript": _javascript_uses,
    "js": _javascript_uses,
    "dart": _dart_uses,
}
