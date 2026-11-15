"""A small expression reader shared by the Dart and C explainers.

Neither language has a parser in the standard library, and a full one would be far more than a plain-English
walkthrough needs. So this reads one *expression* the way the JavaScript explainer reads a line: a tokenizer and a
precedence-climbing parser that understand the shapes beginners actually write (calls, members, indexing, casts,
ternaries, collection literals, lambdas, cascades, string interpolation) and turn them into a tree. `say()` then
puts a tree into plain words. Anything the parser cannot follow raises `ReadError`, and the caller falls back to
quoting the code: saying nothing about a piece is fine, saying something wrong about it is not.

The tree is `N(kind, ...)`; every node keeps `text`, the source it came from, so a complicated piece can be quoted
instead of paraphrased.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable


class ReadError(Exception):
    """The expression is not one this reader can follow."""


@dataclass
class Tok:
    kind: str  # id num str op p
    text: str
    start: int
    end: int


@dataclass
class N:
    kind: str
    a: list[Any] = field(default_factory=list)
    text: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


# ── Tokenizer ───────────────────────────────────────────────

_OPS = [
    ">>>=", "<<=", ">>=", "...?", "?..", "??=", "~/=", ">>>", "...", "->", "++", "--", "&&", "||", "==", "!=", "<=", ">=",
    "<<", ">>", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "=>", "..", "??", "?.", "~/",
    "+", "-", "*", "/", "%", "<", ">", "=", "!", "~", "&", "|", "^", "?", ":", ".", ",", ";", "(", ")", "[", "]", "{", "}", "#", "@",
]
_NUM = re.compile(r"0[xX][0-9a-fA-F_]+[uUlL]*|0[bB][01_]+[uUlL]*|(?:\d[\d_]*(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?[fFuUlL]*")
_ID = re.compile(r"[A-Za-z_$][\w$]*")


def _skip_dart_string(src: str, i: int) -> int:
    """`i` is at a quote (or at an `r` before one). Returns the index just past the string, interpolation included."""
    raw = False
    if src[i] in "rR" and i + 1 < len(src) and src[i + 1] in "'\"":
        raw = True
        i += 1
    q = src[i]
    triple = src.startswith(q * 3, i)
    i += 3 if triple else 1
    close = q * 3 if triple else q
    while i < len(src):
        c = src[i]
        if c == "\\" and not raw:
            i += 2
            continue
        if src.startswith(close, i):
            return i + len(close)
        if c == "$" and not raw and i + 1 < len(src) and src[i + 1] == "{":
            depth, i = 1, i + 2
            while i < len(src) and depth:
                if src[i] in "'\"":
                    i = _skip_dart_string(src, i)
                    continue
                depth += (src[i] == "{") - (src[i] == "}")
                i += 1
            continue
        if c == "\n" and not triple:
            return i  # an unterminated string stops at the end of its line
        i += 1
    return len(src)


def _skip_c_string(src: str, i: int) -> int:
    q = src[i]
    i += 1
    while i < len(src):
        if src[i] == "\\":
            i += 2
            continue
        if src[i] == q:
            return i + 1
        if src[i] == "\n":
            return i
        i += 1
    return len(src)


def tokenize(src: str, dart: bool) -> list[Tok]:
    """Tokens of `src` with comments dropped. Never raises: a character nobody knows is skipped."""
    toks: list[Tok] = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c.isspace():
            i += 1
        elif src.startswith("//", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
        elif c in "'\"" or (dart and c in "rR" and i + 1 < n and src[i + 1] in "'\"" and not (toks and toks[-1].end == i and toks[-1].kind == "id")):
            j = _skip_dart_string(src, i) if dart else _skip_c_string(src, i)
            toks.append(Tok("str", src[i:j], i, j))
            i = j
        elif c.isdigit() or (c == "." and i + 1 < n and src[i + 1].isdigit()):
            m = _NUM.match(src, i)
            j = m.end() if m else i + 1
            toks.append(Tok("num", src[i:j], i, j))
            i = j
        elif c.isalpha() or c in "_$":
            m = _ID.match(src, i)
            j = m.end() if m else i + 1
            toks.append(Tok("id", src[i:j], i, j))
            i = j
        else:
            for op in _OPS:
                if src.startswith(op, i):
                    toks.append(Tok("p" if op in "()[]{},;:.#@?" or op == "=>" else "op", op, i, i + len(op)))
                    i += len(op)
                    break
            else:
                i += 1
    return toks


# ── Precedence ──────────────────────────────────────────────

_ASSIGN = {"=", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", ">>>=", "&=", "^=", "|=", "??=", "~/="}
# op -> (left binding power, right binding power)
_BIN: dict[str, tuple[int, int]] = {}
for _bp, _ops, _right in [
    (1, _ASSIGN, True), (3, {"??"}, True), (4, {"||"}, False), (5, {"&&"}, False), (6, {"|"}, False),
    (7, {"^"}, False), (8, {"&"}, False), (9, {"==", "!="}, False), (10, {"<", ">", "<=", ">="}, False),
    (11, {"<<", ">>", ">>>"}, False), (12, {"+", "-"}, False), (13, {"*", "/", "%", "~/"}, False),
]:
    for _o in _ops:
        _BIN[_o] = (_bp, _bp if _right else _bp + 1)
_UNARY_BP = 14
_C_TYPE_WORDS = {
    "int", "char", "short", "long", "unsigned", "signed", "float", "double", "void", "const", "volatile", "struct", "union",
    "enum", "size_t", "ptrdiff_t", "bool", "_Bool", "intptr_t", "uintptr_t",
}


def _is_c_type_name(name: str, typedefs: set[str]) -> bool:
    return name in _C_TYPE_WORDS or name in typedefs or bool(re.fullmatch(r"u?int(?:8|16|32|64)_t|u?int_(?:fast|least)\d+_t", name))


class Parser:
    def __init__(self, src: str, dart: bool, typedefs: set[str] | None = None):
        self.src = src
        self.toks = tokenize(src, dart)
        self.i = 0
        self.dart = dart
        self.typedefs = typedefs or set()
        self.depth = 0

    # -- helpers
    def peek(self, k: int = 0) -> Tok | None:
        j = self.i + k
        return self.toks[j] if j < len(self.toks) else None

    def at(self, text: str, k: int = 0) -> bool:
        t = self.peek(k)
        return t is not None and t.text == text and t.kind != "str"

    def next(self) -> Tok:
        t = self.peek()
        if t is None:
            raise ReadError("unexpected end")
        self.i += 1
        return t

    def eat(self, text: str) -> bool:
        if self.at(text):
            self.i += 1
            return True
        return False

    def expect(self, text: str) -> Tok:
        if not self.at(text):
            raise ReadError(f"expected {text}")
        return self.next()

    def text_from(self, first: int) -> str:
        """The source from token index `first` up to the current position."""
        if self.i <= first or first >= len(self.toks):
            return ""
        return self.src[self.toks[first].start : self.toks[self.i - 1].end]

    def done(self) -> bool:
        return self.i >= len(self.toks)

    # -- entry
    def parse(self, min_bp: int = 0) -> N:
        self.depth += 1
        if self.depth > 60:
            raise ReadError("too deep")
        try:
            first = self.i
            left = self.prefix()
            left = self.postfix(left, first)
            while True:
                t = self.peek()
                if t is None:
                    break
                if t.kind == "op" and t.text in _BIN:
                    lbp, rbp = _BIN[t.text]
                    if lbp < min_bp:
                        break
                    self.i += 1
                    right = self.parse(rbp)
                    kind = "asg" if t.text in _ASSIGN else "bin"
                    left = N(kind, [t.text, left, right], self.text_from(first))
                elif t.text == "?" and not self.at("?.") and 2 >= min_bp:
                    self.i += 1
                    a = self.parse(1)
                    self.expect(":")
                    b = self.parse(2)
                    left = N("tern", [left, a, b], self.text_from(first))
                elif self.dart and t.kind == "id" and t.text in ("is", "as") and 10 >= min_bp:
                    self.i += 1
                    neg = self.eat("!") if t.text == "is" else False
                    ty = self.parse_type()
                    left = N("is" if t.text == "is" else "as", [left, ty, neg], self.text_from(first))
                else:
                    break
            return left
        finally:
            self.depth -= 1

    def parse_type(self) -> str:
        first = self.i
        t = self.next()
        if t.kind != "id" and t.text != "(":
            raise ReadError("type")
        if t.text == "(":  # record type
            depth = 1
            while depth and not self.done():
                tt = self.next()
                depth += (tt.text == "(") - (tt.text == ")")
        while self.at("."):
            self.i += 1
            self.next()
        if self.at("<"):
            self.skip_angles()
        nxt = self.peek(1)
        if self.at("?") and (nxt is None or nxt.text in (")", ",", ";", "]", "}", "=", "&&", "||", "==", "!=", ":")):
            self.i += 1
        return self.text_from(first)

    def skip_angles(self) -> None:
        depth = 0
        while not self.done():
            t = self.next()
            if t.text == "<":
                depth += 1
            elif t.text == ">":
                depth -= 1
            elif t.text == ">>":
                depth -= 2
            elif t.kind not in ("id",) and t.text not in (",", ".", "?", "(", ")", "Function"):
                raise ReadError("type args")
            if depth <= 0:
                return

    def type_args_ahead(self) -> bool:
        """At a `<`: is this `<T, U>` followed by `(`, `[`, `{` or `.` (type arguments) rather than a comparison?"""
        j, depth = self.i, 0
        while j < len(self.toks):
            t = self.toks[j]
            if t.text == "<":
                depth += 1
            elif t.text == ">":
                depth -= 1
            elif t.text == ">>":
                depth -= 2
            elif not (t.kind == "id" or t.text in (",", ".", "?")):
                return False
            j += 1
            if depth <= 0:
                nxt = self.toks[j] if j < len(self.toks) else None
                return nxt is not None and nxt.text in ("(", "[", "{", ".")
        return False

    # -- prefix
    def prefix(self) -> N:
        t = self.next()
        first = self.i - 1
        if t.kind == "num":
            return N("num", [t.text], t.text)
        if t.kind == "str":
            return N("str", [t.text], t.text)
        if t.kind == "id":
            return self.prefix_id(t, first)
        s = t.text
        if s == "(":
            return self.paren(first)
        if s == "[" and self.dart:
            return self.collection("list", "]", first)
        if s == "{":
            return self.collection("brace" if self.dart else "init", "}", first)
        if s == "<" and self.dart:
            self.i -= 1
            tstart = self.i
            self.skip_angles()
            targs = self.text_from(tstart)
            if self.eat("["):
                node = self.collection("list", "]", tstart)
            elif self.eat("{"):
                node = self.collection("brace", "}", tstart)
            else:
                raise ReadError("typed literal")
            node.extra["targs"] = targs
            return node
        if s == "." and not self.dart and self.peek() is not None and self.peek().kind == "id":  # designator .x
            name = self.next().text
            return N("designator", [name], "." + name)
        if s == "[" and not self.dart:  # designator [2]
            idx = self.parse(0)
            self.expect("]")
            return N("designator_idx", [idx], self.text_from(first))
        if t.kind == "op" and s in ("!", "~", "-", "+", "++", "--", "&", "*"):
            operand = self.parse(_UNARY_BP)
            return N("un", [s, operand], self.text_from(first))
        if s == "..." or s == "...?":
            operand = self.parse(1)
            return N("spread", [operand, s == "...?"], self.text_from(first))
        raise ReadError(f"unexpected {s}")

    def prefix_id(self, t: Tok, first: int) -> N:
        s = t.text
        if self.dart:
            if s in ("await", "throw"):
                return N(s, [self.parse(_UNARY_BP if s == "await" else 1)], "")
            if s in ("new", "const") and not self.at("(") :
                node = self.parse(_UNARY_BP)
                node.extra["const" if s == "const" else "new"] = True
                node.text = self.text_from(first)
                return node
            if s == "switch" and self.at("("):
                return self.switch_expr(first)
            if self.at("=>") :
                body = self.parse_lambda_body()
                return N("lam", [[N("id", [s], s)], body], self.text_from(first))
            if s in ("true", "false", "null", "this", "super"):
                return N("id", [s], s)
            if self.at("<") and s[:1].isupper() and self.type_args_ahead():
                tstart = self.i
                self.skip_angles()
                node = N("id", [s], s)
                node.extra["targs"] = self.text_from(tstart)
                return node
        else:
            if s == "sizeof":
                if self.at("(") and self.looks_like_c_type(1):
                    self.i += 1
                    ty = self.c_type_text()
                    self.expect(")")
                    return N("sizeof_t", [ty], self.text_from(first))
                return N("sizeof", [self.parse(_UNARY_BP)], self.text_from(first))
        return N("id", [s], s)

    def parse_lambda_body(self) -> N:
        self.expect("=>")
        return self.parse(1)

    def looks_like_c_type(self, k: int) -> bool:
        t = self.peek(k)
        if t is None or t.kind != "id":
            return False
        return _is_c_type_name(t.text, self.typedefs)

    def c_type_text(self) -> str:
        first = self.i
        while not self.done() and not self.at(")"):
            self.next()
        return self.text_from(first)

    def paren(self, first: int) -> N:
        if self.dart:
            if self.lambda_ahead():
                params = self.params_until_close()
                if self.at("=>"):
                    body = self.parse_lambda_body()
                    return N("lam", [params, body], self.text_from(first))
                if self.at("{"):
                    end = self.skip_block()
                    return N("lam", [params, None], self.src[self.toks[first].start : self.toks[end].end])
                raise ReadError("lambda")
            if self.eat(")"):
                return N("rec", [[]], "()")
            items = [self.parse(0)] if not self.named_ahead() else [self.named_arg()]
            if self.at(")") and items[0].kind != "named":
                self.i += 1
                return N("paren", [items[0]], self.text_from(first))
            while self.eat(","):
                if self.at(")"):
                    break
                items.append(self.named_arg() if self.named_ahead() else self.parse(0))
            self.expect(")")
            return N("rec", [items], self.text_from(first))
        # C: a cast, a compound literal, or just parentheses
        if self.looks_like_c_type(0):
            save = self.i
            ty = self.c_type_text()
            if self.eat(")"):
                nxt = self.peek()
                if nxt is not None and nxt.text == "{":
                    self.i += 1
                    init = self.collection("init", "}", self.i - 1)
                    return N("compound", [ty, init], self.text_from(first))
                if nxt is not None and (nxt.kind in ("id", "num", "str") or nxt.text in ("(", "-", "+", "!", "~", "*", "&", "++", "--")):
                    operand = self.parse(_UNARY_BP)
                    return N("cast", [ty, operand], self.text_from(first))
            self.i = save
        inner = self.parse(0)
        if self.at(","):  # comma operator
            items = [inner]
            while self.eat(","):
                items.append(self.parse(1))
            self.expect(")")
            return N("comma", [items], self.text_from(first))
        self.expect(")")
        return N("paren", [inner], self.text_from(first))

    def skip_block(self) -> int:
        """At a `{`: step to just past its matching `}`; returns the index of that `}` token."""
        depth = 0
        while not self.done():
            t = self.next()
            if t.kind == "str":
                continue
            if t.text == "{":
                depth += 1
            elif t.text == "}":
                depth -= 1
                if depth == 0:
                    return self.i - 1
        raise ReadError("block")

    def lambda_ahead(self) -> bool:
        """Just after a `(`: is this a parameter list followed by `=>` or `{`?"""
        j, depth = self.i, 1
        while j < len(self.toks) and depth:
            t = self.toks[j]
            if t.kind != "str":
                depth += (t.text in "([{") - (t.text in ")]}")
            j += 1
        nxt = self.toks[j] if j < len(self.toks) else None
        if nxt is None:
            return False
        if nxt.text == "=>":
            return True
        if nxt.text == "async" and j + 1 < len(self.toks) and self.toks[j + 1].text in ("{", "=>"):
            return True
        if nxt.text == "{":
            inside = self.toks[self.i : j - 1]
            return all(x.kind == "id" or x.text in (",", "<", ">", "?", ".", "[", "]", "(", ")", "{", "}", "=", ":") or x.kind in ("num", "str", "op") for x in inside)
        return False

    def params_until_close(self) -> list[N]:
        params: list[N] = []
        depth = 1
        cur: list[Tok] = []
        while not self.done() and depth:
            t = self.next()
            if t.kind != "str":
                depth += (t.text in "([{") - (t.text in ")]}")
            if depth == 0:
                break
            if t.text == "," and depth == 1:
                params.append(self._param(cur))
                cur = []
            else:
                cur.append(t)
        if cur:
            params.append(self._param(cur))
        if self.at("async"):
            self.i += 1
        return params

    def _param(self, toks: list[Tok]) -> N:
        names = [t.text for t in toks if t.kind == "id" and t.text not in ("final", "required", "var", "const")]
        name = names[-1] if names else "_"
        return N("id", [name], " ".join(t.text for t in toks))

    def named_ahead(self) -> bool:
        t, u = self.peek(), self.peek(1)
        return t is not None and u is not None and t.kind == "id" and u.text == ":" and u.kind == "p"

    def named_arg(self) -> N:
        name = self.next().text
        self.expect(":")
        value = self.parse(1)
        return N("named", [name, value], f"{name}: {value.text}")

    # -- collections
    def collection(self, kind: str, close: str, first: int) -> N:
        items: list[N] = []
        while not self.at(close):
            if self.done():
                raise ReadError("unclosed")
            items.append(self.element())
            if not self.eat(","):
                break
        self.expect(close)
        node = N(kind, [items], self.text_from(first))
        if kind == "brace":
            pairs = [x for x in items if x.kind == "pair"]
            node.extra["map"] = bool(pairs) or (not items and False)
        return node

    def element(self) -> N:
        first = self.i
        if self.dart and self.at("if") and self.at("(", 1):
            self.i += 1
            self.expect("(")
            cond = self.parse(0)
            self.expect(")")
            then = self.element()
            other = None
            if self.eat("else"):
                other = self.element()
            return N("if_el", [cond, then, other], self.text_from(first))
        if self.dart and (self.at("for") or (self.at("await") and self.at("for", 1))) and self.at("(", 1 if self.at("for") else 2):
            while not self.at("("):
                self.i += 1
            self.i += 1
            depth, hs = 1, self.i
            while depth and not self.done():
                t = self.next()
                if t.kind != "str":
                    depth += (t.text == "(") - (t.text == ")")
            header = self.src[self.toks[hs].start : self.toks[self.i - 2].end] if self.i - 2 >= hs else ""
            body = self.element()
            return N("for_el", [header, body], self.text_from(first))
        key = self.parse(1)
        if self.dart and self.at(":"):
            self.i += 1
            val = self.parse(1)
            return N("pair", [key, val], self.text_from(first))
        if not self.dart and self.at("=") and key.kind in ("designator", "designator_idx"):
            self.i += 1
            val = self.parse(1)
            return N("designated", [key, val], self.text_from(first))
        return key

    def switch_expr(self, first: int) -> N:
        self.expect("(")
        subj = self.parse(0)
        self.expect(")")
        self.expect("{")
        arms: list[tuple[str, N]] = []
        while not self.at("}"):
            if self.done():
                raise ReadError("switch")
            ps = self.i
            depth = 0
            while not self.done():
                t = self.peek()
                if t.kind != "str":
                    if t.text in "([{":
                        depth += 1
                    elif t.text in ")]}":
                        depth -= 1
                    elif t.text == "=>" and depth == 0:
                        break
                self.i += 1
            pattern = self.text_from(ps)
            self.expect("=>")
            arms.append((pattern, self.parse(1)))
            if not self.eat(","):
                break
        self.expect("}")
        return N("switch", [subj, arms], self.text_from(first))

    # -- postfix
    def postfix(self, left: N, first: int) -> N:
        while True:
            t = self.peek()
            if t is None:
                return left
            s = t.text
            if t.kind == "str":
                return left
            if s == "(" and left.kind in ("id", "mem", "call", "idx", "paren", "post", "lam", "num", "str") and self._call_ok(left):
                self.i += 1
                args = self.args()
                left = N("call", [left, args], self.text_from(first))
            elif s == "[" and (left.kind != "num" or not self.dart):
                self.i += 1
                idx = self.parse(0)
                self.expect("]")
                left = N("idx", [left, idx], self.text_from(first))
            elif s == "<" and t.kind == "op" and self.dart and left.kind in ("mem", "id") and self.type_args_ahead():
                targ_start = self.i
                self.skip_angles()
                left.extra["targs"] = self.text_from(targ_start)
            elif s in (".", "?.", "->") and self.peek(1) is not None and self.peek(1).kind == "id":
                self.i += 1
                name = self.next().text
                left = N("mem", [left, s, name], self.text_from(first))
            elif s in ("++", "--") and t.kind == "op":
                self.i += 1
                left = N("post", [s, left], self.text_from(first))
            elif self.dart and s == "!" and t.kind == "op" and not self.at("=", 1):
                self.i += 1
                left = N("bang", [left], self.text_from(first))
            elif self.dart and s in ("..", "?.."):
                left = self.cascade(left, first)
            else:
                return left

    def _call_ok(self, left: N) -> bool:
        return True

    def args(self) -> list[N]:
        out: list[N] = []
        while not self.at(")"):
            if self.done():
                raise ReadError("args")
            if self.dart and self.named_ahead():
                out.append(self.named_arg())
            else:
                out.append(self.element() if self.dart else self.parse(1))
            if not self.eat(","):
                break
        self.expect(")")
        return out

    def cascade(self, target: N, first: int) -> N:
        sections: list[N] = []
        while self.at("..") or self.at("?.."):
            self.i += 1
            sfirst = self.i
            if self.at("["):
                self.i += 1
                idx = self.parse(0)
                self.expect("]")
                sec = N("idx", [N("id", ["_"], "_"), idx], self.text_from(sfirst))
            else:
                name = self.next().text
                sec = N("id", [name], name)
            sec = self.postfix(sec, sfirst)
            if self.peek() is not None and self.peek().kind == "op" and self.peek().text in _ASSIGN:
                op = self.next().text
                sec = N("asg", [op, sec, self.parse(2)], self.text_from(sfirst))
            sections.append(sec)
        return N("cascade", [target, sections], self.text_from(first))


def parse_expr(src: str, dart: bool, typedefs: set[str] | None = None) -> N:
    """The whole of `src` as one expression, or ReadError."""
    p = Parser(src.strip().rstrip(";"), dart, typedefs)
    if p.done():
        raise ReadError("empty")
    node = p.parse(0)
    if not p.done():
        raise ReadError("trailing")
    node.text = p.src
    return node


def try_expr(src: str, dart: bool, typedefs: set[str] | None = None) -> N | None:
    try:
        return parse_expr(src, dart, typedefs)
    except (ReadError, RecursionError, IndexError):
        return None


# ── Words ───────────────────────────────────────────────────

BIN_WORDS = {
    "+": "plus", "-": "minus", "*": "times", "/": "divided by", "%": "remainder after dividing by", "~/": "divided by (dropping the fraction)",
    "==": "is equal to", "!=": "is not equal to", "<": "is less than", ">": "is greater than", "<=": "is at most", ">=": "is at least",
    "&&": "and", "||": "or", "??": "or, if that is null,", "&": "bitwise AND", "|": "bitwise OR", "^": "bitwise XOR",
    "<<": "shifted left by", ">>": "shifted right by", ">>>": "shifted right (unsigned) by",
}
ASSIGN_VERBS = {
    "+=": ("adds", "to"), "-=": ("subtracts", "from"), "*=": ("multiplies", "by"), "/=": ("divides", "by"), "%=": ("takes", "%="),
    "<<=": ("shifts", "left by"), ">>=": ("shifts", "right by"), "&=": ("ANDs", "into"), "|=": ("ORs", "into"), "^=": ("XORs", "into"),
    "~/=": ("divides (dropping the fraction)", "by"), "??=": ("sets", "if it is null"), ">>>=": ("shifts", "right (unsigned) by"),
}


def walk(node: Any):
    """Every N under (and including) `node`."""
    if isinstance(node, N):
        yield node
        for x in node.a:
            yield from walk(x)
    elif isinstance(node, (list, tuple)):
        for x in node:
            yield from walk(x)


def is_simple(node: N) -> bool:
    return node.kind in ("num", "str", "id") or (node.kind == "mem" and is_simple(node.a[0])) or (
        node.kind == "paren" and is_simple(node.a[0]))


@dataclass
class Say:
    """How to put a node into words; a language plugs in how it names a call or a string."""

    call: Callable[[N, "Say"], str | None] = lambda n, s: None
    string: Callable[[N], str | None] = lambda n: None
    # tried first for every node: a language's own kinds (lists, lambdas, widgets...)
    hook: Callable[[N, "Say", int], str | None] = lambda n, s, level: None
    # how many levels of operators to spell out before quoting the code instead
    limit: int = 2

    def __call__(self, node: N, level: int = 0) -> str:
        return say(node, self, level)


def code(text: str) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    return text if len(text) <= 70 else text[:67] + "..."


def say(node: N, ctx: Say, level: int = 0) -> str:
    """One expression in words, spelling out the first couple of operators and quoting what is deeper."""
    k = node.kind
    hooked = ctx.hook(node, ctx, level)
    if hooked:
        return hooked
    if k == "num":
        return node.a[0]
    if k == "str":
        return ctx.string(node) or node.a[0]
    if k == "id":
        return node.a[0]
    if k == "paren":
        return say(node.a[0], ctx, level)
    if level >= ctx.limit and k in ("bin", "tern", "call", "cast", "idx"):
        return code(node.text)
    if k == "bin":
        op, left, right = node.a
        return f"{say(left, ctx, level + 1)} {BIN_WORDS.get(op, op)} {say(right, ctx, level + 1)}"
    if k == "un":
        op, x = node.a
        inner = say(x, ctx, level + 1)
        return {"!": f"not {inner}", "-": f"minus {inner}", "+": inner, "~": f"{inner} with every bit flipped",
                "&": f"the address of {inner}", "*": f"what {inner} points to", "++": f"{inner} plus one", "--": f"{inner} minus one"}.get(op, code(node.text))
    if k == "post":
        return f"{say(node.a[1], ctx, level + 1)} (then adds one)" if node.a[0] == "++" else f"{say(node.a[1], ctx, level + 1)} (then subtracts one)"
    if k == "bang":
        return f"{say(node.a[0], ctx, level + 1)} (asserted not null)"
    if k == "tern":
        c, a, b = node.a
        return f"{say(a, ctx, level + 1)} if {say(c, ctx, level + 1)}, otherwise {say(b, ctx, level + 1)}"
    if k == "call":
        return ctx.call(node, ctx) or code(node.text)
    if k == "idx":
        return f"item {say(node.a[1], ctx, level + 1)} of {say(node.a[0], ctx, level + 1)}"
    if k == "mem":
        return code(node.text)
    if k == "cast":
        return f"{say(node.a[1], ctx, level + 1)} converted to {node.a[0].strip()}"
    if k in ("sizeof", "sizeof_t"):
        what = node.a[0] if k == "sizeof_t" else code(node.a[0].text)
        return f"the size in bytes of {what}"
    if k == "await":
        return f"the result of waiting for {say(node.a[0], ctx, level + 1)}"
    return code(node.text)
