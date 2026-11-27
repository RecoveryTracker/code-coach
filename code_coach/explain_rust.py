"""Plain-English walkthrough of Rust, a statement at a time.

Like the C and Dart readers it works piece by piece (a piece = one statement, header, match arm or argument that starts
on a physical line), but Rust has its own tokenizer (lifetimes, raw strings, nested comments), its own splitter (a `{`
may open a block, a match, an impl or a struct literal), its own expression, pattern and type readers, and a format-string
reader for `println!`. A piece nobody reads gets the honest row "A line this reader does not break down yet.".

Every sentence that states a checkable fact lives in `FACTS`. A claim is written ```EXPR` gives `VALUE``: the test puts
EXPR in `println!("{}", EXPR)` and runs it with the real rustc. A fact that is not one expression (a move, a borrow,
shadowing, `?`, an overflow panic) is a whole program in tests/test_explain_rust.py's `EXTRA`.
"""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field

from . import explain_common as C
from .explain_programs import rust_program

FACTS: dict[str, str] = {
    "div": "Dividing two whole numbers throws the fraction away (it cuts toward zero): `7 / 2` gives `3` and `-7 / 2` gives `-3`. A float keeps it: `7.0 / 2.0` gives `3.5`.",
    "rem": "`%` takes the sign of the left side: `-7 % 3` gives `-1`.",
    "floatshow": "`{}` shows a whole float without the `.0`: `2.0_f64` gives `2`; `{:?}` keeps it: `format!(\"{:?}\", 2.0_f64)` gives `2.0`.",
    "debugquotes": "`{:?}` is the Debug form, and it puts quotes round text: `format!(\"{:?}\", \"hi\")` gives `\"hi\"`, where `{}` would give `hi`.",
    "debugvec": "A Vec has no plain `{}` form, so it is shown with `{:?}`: `format!(\"{:?}\", vec![1, 2])` gives `[1, 2]`.",
    "width": "`{:>5}` pads on the left to 5 wide: `format!(\"[{:>5}]\", 42)` gives `[   42]`; `<` pads on the right: `format!(\"[{:<5}]\", 42)` gives `[42   ]`; `^` centres: `format!(\"[{:^5}]\", 42)` gives `[ 42  ]`.",
    "defalign": "With no `<`, `>` or `^`, numbers sit on the right and text on the left: `format!(\"[{:5}]\", 42)` gives `[   42]` and `format!(\"[{:5}]\", \"ab\")` gives `[ab   ]`.",
    "zeropad": "`{:05}` pads with zeros: `format!(\"{:05}\", 42)` gives `00042`.",
    "prec": "`{:.2}` rounds to 2 digits after the point: `format!(\"{:.2}\", 3.14159)` gives `3.14`. On text it cuts the text short: `format!(\"{:.2}\", \"hello\")` gives `he`.",
    "hex": "`{:x}` is hexadecimal: `format!(\"{:x}\", 255)` gives `ff`; `{:#x}` adds the `0x`: `format!(\"{:#x}\", 255)` gives `0xff`; `{:X}` is upper case: `format!(\"{:X}\", 255)` gives `FF`.",
    "bin": "`{:b}` is binary: `format!(\"{:b}\", 5)` gives `101`, and `{:08b}` pads it with zeros to 8 digits: `format!(\"{:08b}\", 5)` gives `00000101`.",
    "oct": "`{:o}` is octal: `format!(\"{:o}\", 8)` gives `10`.",
    "exp": "`{:e}` is scientific notation: `format!(\"{:e}\", 1500.0)` gives `1.5e3`.",
    "plus": "`{:+}` always shows the sign: `format!(\"{:+}\", 5)` gives `+5`.",
    "inline": "`{name}` reads a variable called `name` straight from the code around it: `{ let w = 3; format!(\"{w}\") }` gives `3`.",
    "position": "`{1}` and `{0}` pick an argument by its position: `format!(\"{1}{0}\", \"a\", \"b\")` gives `ba`.",
    "braces": "`{{` and `}}` print one brace each: `format!(\"{{}}\")` gives `{}`.",
    "lenbytes": "`len()` of text counts bytes, not letters: `\"héllo\".len()` gives `6`, while `\"héllo\".chars().count()` gives `5`.",
    "astrunc": "`as` between whole-number types keeps only the low bits that fit and never panics: `300i32 as u8` gives `44` and `-1i32 as u32` gives `4294967295`.",
    "asfloat": "`as` from a float to a whole number cuts the fraction toward zero and stops at the biggest or smallest value that fits: `3.99_f64 as i32` gives `3`, `-5.7_f64 as i32` gives `-5` and `1e10_f64 as i32` gives `2147483647`.",
    "aschar": "`u8 as char` turns a code into a character: `65u8 as char` gives `A`; going back, `'a' as u8` gives `97`.",
    "wrapping": "`wrapping_add` goes round to the other end instead of overflowing: `250u8.wrapping_add(10)` gives `4`. `saturating_add` stops at the limit: `250u8.saturating_add(10)` gives `255`. `checked_add` gives an Option that is `None` when it would overflow: `250u8.checked_add(10).is_none()` gives `true`.",
    "rangeex": "`0..3` stops before 3 (it holds 0, 1, 2) and `0..=3` includes it: `(0..3).sum::<i32>()` gives `3` and `(0..=3).sum::<i32>()` gives `6`.",
    "i32default": "A whole number with nothing to say what type it is becomes an i32, which is 4 bytes: `std::mem::size_of_val(&5)` gives `4`.",
    "unwrapor": "`unwrap_or(d)` gives the value inside, or `d` when there is none: `None::<i32>.unwrap_or(7)` gives `7` and `Some(3).unwrap_or(7)` gives `3`.",
    "parse": "`parse` turns text into a value and gives a Result, because the text may not fit: `\"7\".parse::<i32>().unwrap() + 1` gives `8` and `\"x\".parse::<i32>().is_err()` gives `true`.",
    "asbytes": "`as_bytes()` gives the bytes of the text: `\"a\".as_bytes()[0]` gives `97`.",
    "shadow": "A second `let` with a name already in use makes a NEW variable that hides the old one for the rest of the block. The old value is not changed (and the new one may even have another type).",
    "immut": "A variable made with plain `let` can never be given a new value: the compiler refuses `x = 6`. Add `mut` to allow it.",
    "move": "Giving a String (or Vec, Box...) to another variable or to a function MOVES it: the old name can no longer be used. Numbers, `char` and `bool` are copied instead, so both names keep working.",
    "clonefact": "`clone()` makes a second, separate copy, so both names stay usable.",
    "borrow": "`&x` lends x without moving it, so the owner can still be used afterwards.",
    "mutborrow": "A `&mut` borrow is exclusive: while it is alive nothing else may use the value (two `&mut` of the same value at once is a compile error).",
    "deref": "`*r` is the value the reference `r` points at, so `*r += 1` changes that value, not the reference.",
    "exhaustive": "A `match` must cover every possible value or it does not compile; `_` catches whatever is left.",
    "qmark": "`?` on a Result (or Option): if it holds an `Err` (or `None`), the function returns early with that; otherwise `?` gives the value inside.",
    "overflow": "In a debug build, a `+` that goes past the number type's limit panics with `attempt to add with overflow` (a release build wraps instead).",
    "tail": "The last expression of a block, with no `;` after it, is the value of the block. Adding a `;` throws the value away.",
    "unwrapnone": "`unwrap()` on a `None` (or an `Err`) panics: the program stops with an error.",
    "indexpanic": "An index past the end of a Vec or array panics while the program runs.",
    "movecl": "`move` makes a closure take ownership of the variables it uses: a String used inside it cannot be used outside afterwards.",
    "rc": "`Rc::clone(&a)` does not copy the value, it makes one more owner of the same value; `Rc::strong_count` says how many owners there are.",
    "refcell": "`borrow_mut()` on a RefCell checks the borrowing rules while the program runs: a second `borrow_mut()` while the first is alive panics.",
    "labeled": "`break 'outer` leaves the loop labeled `'outer`, even from inside an inner loop.",
    "loopvalue": "`break value` ends a `loop` and makes the value the result of the whole loop.",
    "lazy": "Iterator steps such as `map` and `filter` do nothing by themselves: nothing runs until something (`sum`, `collect`, a `for` loop...) asks for the items.",
    "needsmut": "Calling a method that changes a value (such as `push`) needs the variable to be `mut`.",
    "formove": "`for x in v` takes the items out of `v` (a Vec cannot be used afterwards); `for x in &v` only borrows them.",
    "ifexpr": "`if` can give a value: both branches must have the same type, and the value is the last expression of the branch (no `;`).",
    "unsafe": "An `unsafe` block lets you do a few things the compiler cannot check (such as using a raw pointer); keeping them correct is then your job.",
}


# ── tokenizer ───────────────────────────────────────────────

@dataclass
class T:
    kind: str  # id num str char life op
    text: str
    start: int
    end: int


_IDENT = re.compile(r"[^\W\d]\w*")
_NUMBER = re.compile(
    r"0[xX][0-9a-fA-F_]+(?:[iu](?:8|16|32|64|128|size))?|0[bB][01_]+\w*|0[oO][0-7_]+\w*"
    r"|\d[\d_]*(?:\.(?!\.)(?![^\W\d])(?:\d[\d_]*)?)?(?:[eE][+-]?\d[\d_]*)?(?:_?(?:[iu](?:8|16|32|64|128|size)|f32|f64))?"
)
_RAW = re.compile(r"(?:b|c)?r(#*)\"")
_OPS = sorted(["..=", "...", "<<=", ">>=", "::", "->", "=>", "==", "!=", "<=", ">=", "&&", "||", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=", "<<", ">>", ".."], key=len, reverse=True)


def tokenize(s: str) -> list[T]:
    """Never raises: an unterminated string or comment runs to the end."""
    toks: list[T] = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch.isspace():
            i += 1
            continue
        if s.startswith("//", i):
            j = s.find("\n", i)
            i = n if j < 0 else j
            continue
        if s.startswith("/*", i):
            depth, j = 1, i + 2
            while j < n and depth:
                if s.startswith("/*", j):
                    depth += 1
                    j += 2
                elif s.startswith("*/", j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            i = j
            continue
        m = _RAW.match(s, i)
        if m and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] == "_")):
            close = '"' + m.group(1)
            j = s.find(close, m.end())
            j = n if j < 0 else j + len(close)
            toks.append(T("str", s[i:j], i, j))
            i = j
            continue
        if ch in "bc" and i + 1 < n and s[i + 1] == '"' or ch == '"':
            j = i + (2 if ch != '"' else 1)
            while j < n and s[j] != '"':
                j += 2 if s[j] == "\\" else 1
            j = min(j + 1, n)
            toks.append(T("str", s[i:j], i, j))
            i = j
            continue
        if ch == "b" and s.startswith("b'", i) or ch == "'":
            q = i + (1 if ch == "'" else 2)
            if q < n and s[q] == "\\":
                j = s.find("'", q + 2)
                j = n if j < 0 else j + 1
                toks.append(T("char", s[i:j], i, j))
                i = j
                continue
            if q + 1 < n and s[q + 1] == "'" and s[q] != "'":
                toks.append(T("char", s[i : q + 2], i, q + 2))
                i = q + 2
                continue
            if ch == "'":
                m = _IDENT.match(s, q)
                if m:
                    toks.append(T("life", s[i : m.end()], i, m.end()))
                    i = m.end()
                    continue
        if ch.isdigit():
            if toks and toks[-1].kind == "op" and toks[-1].text == ".":
                m = re.compile(r"\d+").match(s, i)
            else:
                m = _NUMBER.match(s, i)
            toks.append(T("num", m.group(0), i, m.end()))
            i = m.end()
            continue
        m = _IDENT.match(s, i)
        if m:
            toks.append(T("id", m.group(0), i, m.end()))
            i = m.end()
            continue
        for op in _OPS:
            if s.startswith(op, i):
                toks.append(T("op", op, i, i + len(op)))
                i += len(op)
                break
        else:
            toks.append(T("op", ch, i, i + 1))
            i += 1
    return toks


# ── splitting code into pieces ──────────────────────────────

ARGK = ("paren", "brack", "lit")
BLOCKISH = ("block", "match", "impl", "trait", "mod", "struct", "enum")
CONTROL = {"if", "else", "while", "loop", "for", "match", "unsafe"}
_QUAL = {"pub", "const", "async", "unsafe", "extern", "default", "crate", "safe"}
_ITEM_FRAME = {"struct": "struct", "union": "struct", "enum": "enum", "trait": "trait", "impl": "impl", "mod": "mod"}
_CONT_START = {".", "?", "+", "-", "*", "/", "%", "&&", "||", "==", "!=", "<", ">", "<=", ">=", "&", "|", "^", "<<", ">>", "=", "..", "..="}


@dataclass
class Frame:
    kind: str
    name: str = ""
    value: bool = False


@dataclass
class Piece:
    line: int
    toks: list
    mode: str  # stmt | arg | cont
    frame: str  # file block match impl trait mod struct enum: the block this piece sits in
    fname: str = ""
    opens: str = ""  # what the `{` that follows opens: block match impl trait mod struct enum
    end: str = "eol"  # ; { } , eol or a closing bracket
    sdepth: int = 0
    value: bool = False  # inside a match whose result is used
    tail: bool = False  # the last expression of a block (no `;`)


@dataclass
class Info:
    line: int
    raw: str
    depth: int = 0
    pieces: list = field(default_factory=list)
    structural: bool = False


def _skip_attr(cur: list, i: int) -> int:
    while i + 1 < len(cur) and cur[i].text == "#" and cur[i + 1].text in ("[", "!"):
        depth, j = 0, i + 1
        while j < len(cur):
            if cur[j].text == "[":
                depth += 1
            elif cur[j].text == "]":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        i = j + 1
    return i


def _brace_kind(cur: list) -> str:
    """What the `{` after these tokens opens: block, match, impl, trait, mod, struct, enum, or lit (a struct literal)."""
    i = _skip_attr(cur, 0)
    j = i
    if i < len(cur) and cur[i].text == "use":
        return "lit"
    if i < len(cur) and cur[i].text == "macro_rules":
        return "mod"
    while j < len(cur) and cur[j].kind == "id" and cur[j].text in _QUAL:
        j += 1
        if j < len(cur) and cur[j].text == "(" and cur[j - 1].text in ("pub", "crate"):
            while j < len(cur) and cur[j].text != ")":
                j += 1
            j += 1
        if j < len(cur) and cur[j].kind == "str":
            j += 1
    if j < len(cur) and cur[j].kind == "id":
        w = cur[j].text
        if w in _ITEM_FRAME:
            return _ITEM_FRAME[w]
        if w == "fn":
            return "block"
    last_kw = ""
    for k in range(len(cur) - 1, i - 1, -1):
        if cur[k].kind == "id" and cur[k].text in CONTROL and not (k > 0 and cur[k - 1].text == "."):
            last_kw = cur[k].text
            break
    if last_kw:
        return "match" if last_kw == "match" else "block"
    if not cur:
        return "block"
    last = cur[-1]
    if last.kind == "op" and last.text in ("|", "||", "=>", "="):
        return "block"
    if last.kind == "id" and (last.text[:1].isupper() or last.text == "Self"):
        return "lit"
    return "block"


def read_pieces(code: str) -> list[Info]:
    """Every physical line with the pieces that start on it. Never raises."""
    raw_lines = code.split("\n")
    toks = tokenize(code)
    starts = [0]
    for k, ch in enumerate(code):
        if ch == "\n":
            starts.append(k + 1)
    infos = [Info(n + 1, raw_lines[n]) for n in range(len(raw_lines))]
    idx_of = {t.start: k for k, t in enumerate(toks)}
    by_line: dict[int, list[T]] = {}
    for t in toks:
        by_line.setdefault(bisect.bisect_right(starts, t.start), []).append(t)
    stack: list[Frame] = []
    prev_tok: T | None = None
    stmt_open = False

    def block_frame() -> Frame | None:
        for f in reversed(stack):
            if f.kind not in ARGK:
                return f
        return None

    def in_arg() -> bool:
        return bool(stack) and stack[-1].kind in ARGK

    for n, info in enumerate(infos, start=1):
        ltoks = by_line.get(n, [])
        if not ltoks:
            info.structural = True
            continue
        idx = 0
        while idx < len(ltoks) and ltoks[idx].kind == "op" and ltoks[idx].text in (")", "]", "}"):
            if stack:
                stack.pop()
            idx += 1
        rest = ltoks[idx:]
        info.depth = min(len(stack), 10)
        if not rest or all(t.kind == "op" and t.text in (";", ",") for t in rest):
            info.structural = True
            prev_tok = ltoks[-1]
            if any(t.text == ";" for t in rest):
                stmt_open = False
            continue
        top = stack[-1] if stack else None
        mode = "arg" if in_arg() else "stmt"
        if mode == "stmt" and stmt_open and not (top is not None and top.kind in ("match", "struct", "enum")) and rest[0].kind == "op" and rest[0].text in _CONT_START:
            mode = "cont"
        cur: list[T] = []
        local = 0
        cur_depth = len(stack)
        cur_mode = mode

        def emit(end: str, opens: str = "") -> None:
            nonlocal cur, cur_depth, cur_mode
            if not cur:
                return
            bf = block_frame()
            kind = bf.kind if bf else "file"
            ni = idx_of.get(cur[-1].start, -1) + 1
            nxt = toks[ni] if 0 < ni < len(toks) else None
            tail = (end == "}" or (end == "eol" and nxt is not None and nxt.kind == "op" and nxt.text == "}")) and bool(stack) and stack[-1].kind == "block" and cur_mode == "stmt"
            info.pieces.append(Piece(n, cur, cur_mode, kind, bf.name if bf else "", opens, end, cur_depth, bool(bf and bf.value), tail))
            cur = []

        for k, t in enumerate(rest):
            s = t.text if t.kind == "op" else None
            if not cur:
                cur_depth = len(stack)
                cur_mode = mode
            if s in ("(", "["):
                stack.append(Frame("paren" if s == "(" else "brack"))
                cur.append(t)
                local += 1
            elif s == "{":
                kind = _brace_kind(cur)
                if kind == "lit":
                    stack.append(Frame("lit"))
                    cur.append(t)
                    local += 1
                else:
                    value = kind == "match" and (any(x.kind == "op" and x.text == "=" for x in cur) or (bool(cur) and cur[0].text in ("return", "break")) or in_arg() or any(x.text == "let" for x in cur))
                    emit("{", kind)
                    name = " ".join(x.text for x in cur[:6]) if cur else ""
                    stack.append(Frame(kind, name, value))
                    local = 0
                    mode = "stmt"
            elif s in (")", "]", "}"):
                if local > 0:
                    local -= 1
                    if stack:
                        stack.pop()
                    cur.append(t)
                else:
                    emit(s)
                    if stack:
                        stack.pop()
                    mode = "arg" if in_arg() else "stmt"
            elif s == ";" and local == 0:
                emit(";")
                mode = "arg" if in_arg() else "stmt"
                stmt_open = False
            elif s == "," and local == 0 and stack and stack[-1].kind in ARGK + ("match", "struct", "enum"):
                emit(",")
                mode = "arg" if in_arg() else "stmt"
            else:
                cur.append(t)
            if s in ("{", "}", ";") and local == 0:
                stmt_open = False
        emit("eol")
        last = rest[-1]
        prev_tok = last
        if last.kind == "op" and last.text in ("{", "}", ";"):
            stmt_open = False
        elif not in_arg():
            stmt_open = True
    del prev_tok
    return infos


# ── reading one expression, pattern or type ─────────────────

class Unreadable(Exception):
    """The piece is not one this reader can follow."""


@dataclass
class N:
    kind: str
    a: tuple = ()
    src: str = ""
    open: bool = False  # its closing bracket is not in this piece (the rest is on the next lines)


_BIN = {"*": 11, "/": 11, "%": 11, "+": 10, "-": 10, "<<": 9, ">>": 9, "&": 8, "^": 7, "|": 6,
        "==": 5, "!=": 5, "<": 5, ">": 5, "<=": 5, ">=": 5, "&&": 4, "||": 3}
_ASG = {"=", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=", "<<=", ">>="}
_MAXDEPTH = 40
_END = {")", "]", "}", ",", ";", "{", "=>"}


class Parser:
    def __init__(self, toks: list, code: str):
        self.t = list(toks)
        self.i = 0
        self.code = code
        self.depth = 0
        self.split_end: dict[int, int] = {}
        self.hit_eof = False

    # basics
    def peek(self, k: int = 0):
        j = self.i + k
        return self.t[j] if 0 <= j < len(self.t) else None

    def at(self, text: str, k: int = 0) -> bool:
        t = self.peek(k)
        return t is not None and t.text == text and t.kind in ("op", "id")

    def eof(self) -> bool:
        return self.i >= len(self.t)

    def take(self):
        if self.eof():
            raise Unreadable
        self.i += 1
        return self.t[self.i - 1]

    def expect(self, text: str) -> None:
        if self.at(text):
            self.i += 1
        elif text == ">" and self.at(">>"):
            t = self.t[self.i]
            self.split_end[self.i] = t.start + 1
            self.t[self.i] = T("op", ">", t.start + 1, t.end)
        elif text == ">" and self.at(">="):
            t = self.t[self.i]
            self.split_end[self.i] = t.start + 1
            self.t[self.i] = T("op", "=", t.start + 1, t.end)
        elif not self.eof():
            raise Unreadable
        else:
            self.hit_eof = True

    def src(self, i0: int, i1: int) -> str:
        if i1 <= i0 or i0 >= len(self.t):
            return ""
        end = self.t[min(i1, len(self.t)) - 1].end
        if i1 in self.split_end:
            end = self.split_end[i1]
        return self.code[self.t[i0].start : end]

    def enter(self) -> None:
        self.depth += 1
        if self.depth > _MAXDEPTH:
            raise Unreadable

    def leave(self) -> None:
        self.depth -= 1

    def ends(self) -> bool:
        t = self.peek()
        return t is None or (t.kind == "op" and t.text in _END)

    # expressions
    def expr(self, min_prec: int = 0) -> N:
        self.enter()
        try:
            i0 = self.i
            lhs = self.unary()
            while True:
                t = self.peek()
                if t is None:
                    break
                if t.kind == "id" and t.text == "as":
                    self.i += 1
                    ty = self.ty()
                    lhs = N("cast", (lhs, ty), self.src(i0, self.i))
                    continue
                if t.kind != "op":
                    break
                op = t.text
                if op in _BIN:
                    prec = _BIN[op]
                    if prec < min_prec:
                        break
                    self.i += 1
                    rhs = self.expr(prec + 1)
                    lhs = N("bin", (op, lhs, rhs), self.src(i0, self.i))
                elif op in _ASG:
                    if min_prec > 1:
                        break
                    self.i += 1
                    rhs = self.expr(1)
                    lhs = N("asg", (op, lhs, rhs), self.src(i0, self.i))
                elif op in ("..", "..="):
                    if min_prec > 2:
                        break
                    self.i += 1
                    hi = None if self.ends() else self.expr(3)
                    lhs = N("range", (lhs, hi, op == "..="), self.src(i0, self.i))
                else:
                    break
            return lhs
        finally:
            self.leave()

    def unary(self) -> N:
        self.enter()
        try:
            i0 = self.i
            t = self.peek()
            if t is None:
                raise Unreadable
            if t.kind == "op":
                if t.text in ("-", "!", "*"):
                    self.i += 1
                    e = self.unary()
                    return N("un", (t.text, e), self.src(i0, self.i))
                if t.text in ("&", "&&"):
                    self.i += 1
                    mut = False
                    if self.at("mut"):
                        self.i += 1
                        mut = True
                    e = self.unary()
                    n = N("un", ("&mut" if mut else "&", e), self.src(i0, self.i))
                    return N("un", ("&", n), n.src) if t.text == "&&" else n
                if t.text in ("..", "..="):
                    self.i += 1
                    hi = None if self.ends() else self.expr(3)
                    return N("range", (None, hi, t.text == "..="), self.src(i0, self.i))
            return self.postfix(self.primary(), i0)
        finally:
            self.leave()

    def args(self, close: str) -> list:
        out = []
        while not self.eof() and not self.at(close):
            out.append(self.expr())
            if self.at(","):
                self.i += 1
            elif not self.at(close) and not self.eof():
                raise Unreadable
        self.expect(close)
        return out

    def postfix(self, e: N, i0: int) -> N:
        while True:
            t = self.peek()
            if t is None or t.kind != "op":
                return e
            if t.text == ".":
                nxt = self.peek(1)
                if nxt is None:
                    raise Unreadable
                if nxt.kind == "num":
                    self.i += 2
                    e = N("field", (e, nxt.text), self.src(i0, self.i))
                elif nxt.kind == "id":
                    self.i += 2
                    targs = ""
                    if self.at("::") and self.at("<", 1):
                        j0 = self.i
                        self.i += 1
                        self.generic_args()
                        targs = self.src(j0 + 1, self.i)
                    if nxt.text == "await":
                        e = N("await", (e,), self.src(i0, self.i))
                    elif self.at("("):
                        self.i += 1
                        e = N("mcall", (e, nxt.text, targs, self.args(")")), self.src(i0, self.i))
                        e.open = self.hit_eof
                    else:
                        e = N("field", (e, nxt.text), self.src(i0, self.i))
                else:
                    raise Unreadable
            elif t.text == "(":
                self.i += 1
                e = N("call", (e, self.args(")")), self.src(i0, self.i))
                e.open = self.hit_eof
            elif t.text == "[":
                self.i += 1
                ix = self.expr()
                self.expect("]")
                e = N("idx", (e, ix), self.src(i0, self.i))
            elif t.text == "?":
                self.i += 1
                e = N("try", (e,), self.src(i0, self.i))
            else:
                return e

    def path(self) -> tuple[str, str]:
        """a::b::<T>::c -> (source of the path, last segment)."""
        i0 = self.i
        last = ""
        while True:
            t = self.peek()
            if t is not None and t.kind == "id":
                last = t.text
                self.i += 1
            else:
                raise Unreadable
            if self.at("::"):
                self.i += 1
                if self.at("<"):
                    self.generic_args()
                    if self.at("::"):
                        self.i += 1
                        continue
                    break
                continue
            break
        return self.src(i0, self.i), last

    def primary(self) -> N:
        i0 = self.i
        t = self.take()
        k, x = t.kind, t.text
        if k in ("num", "str", "char"):
            return N(k, (x,), x)
        if k == "life":
            if self.at(":"):
                self.i += 1
                return N("blockhead", ("labeled",), x)
            raise Unreadable
        if k == "op":
            if x == "(":
                items = []
                comma = False
                while not self.eof() and not self.at(")"):
                    items.append(self.expr())
                    if self.at(","):
                        self.i += 1
                        comma = True
                    elif not self.at(")") and not self.eof():
                        raise Unreadable
                self.expect(")")
                s = self.src(i0, self.i)
                if not items:
                    return N("unit", (), s)
                if len(items) == 1 and not comma:
                    return N("paren", (items[0],), s)
                tn = N("tuple", (items,), s)
                tn.open = self.hit_eof
                return tn
            if x == "[":
                if self.at("]"):
                    self.i += 1
                    return N("array", ([],), self.src(i0, self.i))
                first = self.expr()
                if self.at(";"):
                    self.i += 1
                    cnt = self.expr()
                    self.expect("]")
                    return N("repeat", (first, cnt), self.src(i0, self.i))
                items = [first]
                while self.at(","):
                    self.i += 1
                    if self.at("]") or self.eof():
                        break
                    items.append(self.expr())
                self.expect("]")
                an = N("array", (items,), self.src(i0, self.i))
                an.open = self.hit_eof
                return an
            if x in ("|", "||"):
                return self.closure(i0, False)
            raise Unreadable
        # identifiers and keywords
        if x in ("true", "false"):
            return N("bool", (x,), x)
        if x == "move":
            if not (self.at("|") or self.at("||")):
                raise Unreadable
            self.i += 1
            return self.closure(i0, True, self.t[self.i - 1].text)
        if x == "if":
            if self.at("let"):
                self.i += 1
                pat = self.pattern()
                self.expect("=")
                return N("iflet", (pat, self.expr(2)), self.src(i0, self.i))
            return N("ifhead", (self.expr(),), self.src(i0, self.i))
        if x == "match":
            return N("matchhead", (self.expr(),), self.src(i0, self.i))
        if x in ("loop", "unsafe", "async"):
            return N("blockhead", (x,), x)
        if x == "while":
            return N("whilehead", (self.expr(),), self.src(i0, self.i))
        if x == "let":
            pat = self.pattern()
            self.expect("=")
            return N("letcond", (pat, self.expr(5)), self.src(i0, self.i))
        if x == "return":
            e = None if self.ends() else self.expr()
            return N("return", (e,), self.src(i0, self.i))
        if x == "break":
            label = ""
            if self.peek() is not None and self.peek().kind == "life":
                label = self.take().text
            e = None if self.ends() else self.expr()
            return N("break", (label, e), self.src(i0, self.i))
        if x == "continue":
            label = self.take().text if self.peek() is not None and self.peek().kind == "life" else ""
            return N("continue", (label,), self.src(i0, self.i))
        if x == "else":
            raise Unreadable
        self.i -= 1
        psrc, last = self.path()
        if self.at("!") and self.peek(1) is not None and self.peek(1).text in ("(", "[", "{"):
            return self.macro(psrc, i0)
        if self.at("{") and last[:1].isupper() and self.struct_ok():
            return self.struct_lit(psrc, i0)
        return N("path", (psrc,), psrc)

    def struct_ok(self) -> bool:
        return True

    def struct_lit(self, psrc: str, i0: int) -> N:
        self.expect("{")
        fields, base = [], None
        while not self.eof() and not self.at("}"):
            if self.at(".."):
                self.i += 1
                base = self.expr()
            else:
                name = self.take()
                if name.kind not in ("id", "num"):
                    raise Unreadable
                if self.at(":"):
                    self.i += 1
                    fields.append((name.text, self.expr()))
                else:
                    fields.append((name.text, None))
            if self.at(","):
                self.i += 1
            elif not self.at("}") and not self.eof():
                raise Unreadable
        self.expect("}")
        sn = N("struct", (psrc, fields, base), self.src(i0, self.i))
        sn.open = self.hit_eof
        return sn

    def macro(self, name: str, i0: int) -> N:
        self.i += 1  # the !
        opener = self.take().text
        close = {"(": ")", "[": "]", "{": "}"}[opener]
        depth, j0 = 0, self.i
        j = self.i
        while j < len(self.t):
            tx = self.t[j]
            if tx.kind == "op":
                if tx.text in "([{":
                    depth += 1
                elif tx.text in ")]}":
                    if depth == 0:
                        break
                    depth -= 1
            j += 1
        inner = self.t[j0:j]
        unclosed = j >= len(self.t)
        self.i = min(j + 1, len(self.t))
        parts: list[list] = [[]]
        seps: list[str] = []
        d = 0
        for tx in inner:
            if tx.kind == "op":
                if tx.text in "([{":
                    d += 1
                elif tx.text in ")]}":
                    d -= 1
                elif d == 0 and tx.text in (",", ";"):
                    seps.append(tx.text)
                    parts.append([])
                    continue
            parts[-1].append(tx)
        if parts and not parts[-1]:
            parts.pop()
        nodes = []
        for p in parts:
            try:
                sub = Parser(p, self.code)
                sub.depth = self.depth
                nd = sub.expr()
                if not sub.eof():
                    raise Unreadable
                nodes.append(nd)
            except (Unreadable, RecursionError):
                nodes.append(N("raw", (self.code[p[0].start : p[-1].end],), self.code[p[0].start : p[-1].end]))
        short = name.split("::")[-1]
        mn = N("macro", (short, nodes, opener, ";" in seps), self.src(i0, self.i))
        mn.open = unclosed
        return mn

    def closure(self, i0: int, mv: bool, first: str = "") -> N:
        params = []
        first = first or self.t[self.i - 1].text
        if first == "|":
            while not self.eof() and not self.at("|"):
                pat = self.pat1()
                ty = None
                if self.at(":"):
                    self.i += 1
                    ty = self.ty()
                params.append((pat, ty))
                if self.at(","):
                    self.i += 1
            self.expect("|")
        ret = None
        if self.at("->"):
            self.i += 1
            ret = self.ty()
        body = None if self.eof() else self.expr(1)
        return N("closure", (params, body, mv, ret), self.src(i0, self.i))

    # types
    def generic_args(self) -> list:
        self.expect("<")
        out = []
        while not self.eof() and not (self.at(">") or self.at(">>") or self.at(">=")):
            t = self.peek()
            if t.kind == "life":
                self.i += 1
            elif t.kind == "id" and self.at("=", 1):
                self.i += 2
                out.append(self.ty())
            elif t.kind == "num" or t.text == "{":
                self.i += 1
            else:
                out.append(self.ty())
            if self.at(","):
                self.i += 1
        self.expect(">")
        return out

    def ty(self) -> tuple:
        self.enter()
        try:
            t = self.peek()
            if t is None:
                raise Unreadable
            if t.kind == "op" and t.text in ("&", "&&"):
                self.i += 1
                if self.peek() is not None and self.peek().kind == "life":
                    self.i += 1
                mut = False
                if self.at("mut"):
                    self.i += 1
                    mut = True
                inner = self.ty()
                r = ("ref", mut, inner)
                return ("ref", False, r) if t.text == "&&" else r
            if t.kind == "op" and t.text == "*":
                self.i += 1
                if self.at("const") or self.at("mut"):
                    self.i += 1
                return ("ptr", self.ty())
            if t.kind == "op" and t.text == "(":
                self.i += 1
                items = []
                while not self.eof() and not self.at(")"):
                    items.append(self.ty())
                    if self.at(","):
                        self.i += 1
                self.expect(")")
                return ("tuple", items) if items else ("unit",)
            if t.kind == "op" and t.text == "[":
                self.i += 1
                inner = self.ty()
                if self.at(";"):
                    self.i += 1
                    j0 = self.i
                    self.expr()
                    n = self.src(j0, self.i)
                    self.expect("]")
                    return ("array", inner, n)
                self.expect("]")
                return ("slice", inner)
            if t.kind == "op" and t.text == "!":
                self.i += 1
                return ("never",)
            if t.kind == "id" and t.text in ("dyn", "impl"):
                self.i += 1
                bounds = [self.bound()]
                while self.at("+"):
                    self.i += 1
                    bounds.append(self.bound())
                return (t.text, bounds)
            if t.kind == "id" and t.text in ("fn", "unsafe", "extern"):
                while self.at("unsafe") or self.at("extern"):
                    self.i += 1
                    if self.peek() is not None and self.peek().kind == "str":
                        self.i += 1
                self.expect("fn")
                self.expect("(")
                params = []
                while not self.eof() and not self.at(")"):
                    if self.peek().kind == "id" and self.at(":", 1):
                        self.i += 2
                    params.append(self.ty())
                    if self.at(","):
                        self.i += 1
                self.expect(")")
                ret = None
                if self.at("->"):
                    self.i += 1
                    ret = self.ty()
                return ("fn", params, ret)
            if t.kind == "id":
                psrc, last, targs = self.type_path()
                return ("path", psrc, targs)
            raise Unreadable
        finally:
            self.leave()

    def type_path(self) -> tuple[str, str, list]:
        i0 = self.i
        last, targs = "", []
        while True:
            t = self.peek()
            if t is None or t.kind != "id":
                raise Unreadable
            last = t.text
            self.i += 1
            if self.at("<"):
                targs = self.generic_args()
            elif self.at("(") and last in ("Fn", "FnMut", "FnOnce"):
                self.i += 1
                ps = []
                while not self.eof() and not self.at(")"):
                    ps.append(self.ty())
                    if self.at(","):
                        self.i += 1
                self.expect(")")
                ret = None
                if self.at("->"):
                    self.i += 1
                    ret = self.ty()
                targs = [("fn", ps, ret)]
            if self.at("::") and not self.at("<", 1):
                self.i += 1
                continue
            if self.at("::") and self.at("<", 1):
                self.i += 1
                targs = self.generic_args()
            break
        return self.src(i0, self.i), last, targs

    def bound(self) -> tuple:
        t = self.peek()
        if t is not None and t.kind == "life":
            self.i += 1
            return ("life", t.text)
        if self.at("?"):
            self.i += 1
        psrc, last, targs = self.type_path()
        return ("path", psrc, targs)

    # patterns
    def pattern(self) -> tuple:
        self.enter()
        try:
            if self.at("|"):
                self.i += 1
            first = self.pat1()
            alts = [first]
            while self.at("|"):
                self.i += 1
                alts.append(self.pat1())
            return ("or", alts) if len(alts) > 1 else first
        finally:
            self.leave()

    def pat_lit(self):
        t = self.peek()
        if t is None:
            raise Unreadable
        neg = ""
        if t.kind == "op" and t.text == "-":
            self.i += 1
            neg = "-"
            t = self.peek()
            if t is None or t.kind != "num":
                raise Unreadable
        if t.kind in ("num", "char", "str") or (t.kind == "id" and t.text in ("true", "false")):
            self.i += 1
            return neg + t.text
        if t.kind == "id":
            psrc, last, _ = self.type_path()
            return psrc
        raise Unreadable

    def pat1(self) -> tuple:
        t = self.peek()
        if t is None:
            raise Unreadable
        if t.kind == "op":
            if t.text in ("&", "&&"):
                self.i += 1
                if self.at("mut"):
                    self.i += 1
                return ("ref", self.pat1())
            if t.text == "(":
                self.i += 1
                items = []
                while not self.eof() and not self.at(")"):
                    items.append(self.pattern())
                    if self.at(","):
                        self.i += 1
                self.expect(")")
                return ("tuple", items)
            if t.text == "[":
                self.i += 1
                items = []
                while not self.eof() and not self.at("]"):
                    items.append(self.pattern())
                    if self.at(","):
                        self.i += 1
                self.expect("]")
                return ("slice", items)
            if t.text in ("..", "..="):
                self.i += 1
                if t.text == "..=" or (self.peek() is not None and (self.peek().kind in ("num", "char") or self.at("-"))):
                    return ("range", None, self.pat_lit(), t.text == "..=")
                return ("rest",)
            if t.text == "-":
                lo = self.pat_lit()
                return self.range_tail(lo)
            raise Unreadable
        if t.kind in ("num", "char", "str"):
            lo = self.pat_lit()
            return self.range_tail(lo)
        if t.kind == "id":
            if t.text == "_":
                self.i += 1
                return ("wild",)
            if t.text in ("true", "false"):
                self.i += 1
                return ("lit", t.text)
            if t.text in ("ref", "mut", "box"):
                self.i += 1
                mut = t.text == "mut" or (t.text == "ref" and self.at("mut"))
                if t.text == "ref" and self.at("mut"):
                    self.i += 1
                name = self.take()
                return self.bind_tail(name.text, mut)
            nxt = self.peek(1)
            nt = nxt.text if nxt is not None else ""
            if (t.text[:1].islower() or t.text[:1] == "_") and nt not in ("::", "(", "{", "..=", "..", "..."):
                self.i += 1
                return self.bind_tail(t.text, False)
            psrc, last, _ = self.type_path_expr()
            if self.at("("):
                self.i += 1
                items = []
                while not self.eof() and not self.at(")"):
                    items.append(self.pattern())
                    if self.at(","):
                        self.i += 1
                self.expect(")")
                return ("tstruct", psrc, items)
            if self.at("{"):
                self.i += 1
                fields, rest = [], False
                while not self.eof() and not self.at("}"):
                    if self.at(".."):
                        self.i += 1
                        rest = True
                    else:
                        mut = False
                        if self.at("ref") or self.at("mut"):
                            self.i += 1
                            mut = True
                        nm = self.take().text
                        if self.at(":"):
                            self.i += 1
                            fields.append((nm, self.pattern()))
                        else:
                            fields.append((nm, None))
                    if self.at(","):
                        self.i += 1
                self.expect("}")
                return ("struct", psrc, fields, rest)
            if self.at("..=") or self.at("..") or self.at("..."):
                return self.range_tail(psrc)
            return ("path", psrc)
        raise Unreadable

    def type_path_expr(self) -> tuple[str, str, list]:
        i0 = self.i
        last = ""
        while True:
            t = self.peek()
            if t is None or t.kind != "id":
                raise Unreadable
            last = t.text
            self.i += 1
            if self.at("::"):
                self.i += 1
                if self.at("<"):
                    self.generic_args()
                    if self.at("::"):
                        self.i += 1
                        continue
                    break
                continue
            break
        return self.src(i0, self.i), last, []

    def bind_tail(self, name: str, mut: bool) -> tuple:
        if self.at("@"):
            self.i += 1
            return ("bind", name, mut, self.pat1())
        return ("bind", name, mut, None)

    def range_tail(self, lo: str) -> tuple:
        if self.at("..=") or self.at("..") or self.at("..."):
            incl = self.peek().text != ".."
            self.i += 1
            hi = None
            t = self.peek()
            if t is not None and (t.kind in ("num", "char") or (t.kind == "op" and t.text == "-") or (t.kind == "id" and t.text[:1].isupper())):
                hi = self.pat_lit()
            return ("range", lo, hi, incl)
        return ("lit", lo)


def parse_expr(toks: list, code: str) -> N | None:
    """One whole expression, or None when it is not one this reader can follow."""
    if not toks:
        return None
    try:
        p = Parser(toks, code)
        e = p.expr()
        return e if p.eof() else None
    except (Unreadable, RecursionError, IndexError, KeyError):
        return None


# ── saying things in plain English ──────────────────────────

_SEEN: set[str] = set()
_PEND: list[tuple[str, str]] = []
_GEN: set[str] = set()
_OWNED: set[str] = set()  # variables known to own a String, Vec, Box...: using one by value MOVES it
_SCOPES: dict[int, set] = {}
_CODE = ""


def want(key: str) -> bool:
    """A rule sentence for this row, unless this explanation already showed it. True when it was added now."""
    if key not in _SEEN and key not in [k for k, _t in _PEND]:
        _PEND.append((key, FACTS[key]))
        return True
    return False


def code(s: str, limit: int = 60) -> str:
    s = re.sub(r"\s+", " ", s.strip()).replace("`", "'")
    return s if len(s) <= limit else s[: limit - 3] + "..."


_INTS = {"i8": 8, "i16": 16, "i32": 32, "i64": 64, "i128": 128, "isize": 64, "u8": 8, "u16": 16, "u32": 32, "u64": 64, "u128": 128, "usize": 64}


def ty_src(t: tuple, lvl: int = 0) -> str:
    k = t[0]
    if lvl > 6:
        return "..."
    if k == "path":
        name = t[1]
        return name.split("::")[-1] + ("<" + ", ".join(ty_src(x, lvl + 1) for x in t[2]) + ">" if t[2] else "") if "::" in name and not t[2] else name + ("<" + ", ".join(ty_src(x, lvl + 1) for x in t[2]) + ">" if t[2] and "<" not in name else "")
    if k == "ref":
        return "&" + ("mut " if t[1] else "") + ty_src(t[2], lvl + 1)
    if k == "ptr":
        return "*" + ty_src(t[1], lvl + 1)
    if k == "tuple":
        return "(" + ", ".join(ty_src(x, lvl + 1) for x in t[1]) + ")"
    if k == "unit":
        return "()"
    if k == "array":
        return f"[{ty_src(t[1], lvl + 1)}; {t[2]}]"
    if k == "slice":
        return f"[{ty_src(t[1], lvl + 1)}]"
    if k in ("dyn", "impl"):
        return k + " " + " + ".join(b[1] if b[0] == "life" else ty_src(b, lvl + 1) for b in t[1])
    if k == "fn":
        return "fn(" + ", ".join(ty_src(x, lvl + 1) for x in t[1]) + ")" + (" -> " + ty_src(t[2], lvl + 1) if t[2] else "")
    if k == "never":
        return "!"
    return "?"


def art(word: str) -> str:
    """'a' or 'an' for a type or variant name."""
    w = word.split("::")[0]
    if len(w) == 1:
        return "an" if w.upper() in "AEFHILMNORSX" else "a"
    return "an" if w[:1].lower() in "aeiou" else "a"


def ty_phrase(t: tuple) -> str:
    """A type in words (the outer layer explained, what is inside quoted as source)."""
    k = t[0]
    if k == "path":
        full = t[1]
        name = full.split("::")[-1] if "<" not in full else re.split(r"<", full)[0].split("::")[-1]
        name = name.strip()
        args = t[2]
        inner = ", ".join(ty_src(x) for x in args)
        if name in _INTS:
            bits = _INTS[name]
            artic = "an " if name[0] in "iu" else "a "
            if name == "usize":
                return "a usize (a whole number used for sizes and positions, never negative)"
            if name == "isize":
                return "an isize (a whole number that can be negative, as wide as a pointer)"
            if name[0] == "u":
                return f"a {name} (a whole number from 0 to {2 ** bits - 1})" if bits <= 32 else f"a {name} (a {bits}-bit whole number, never negative)"
            return f"{artic}{name} (a {bits}-bit whole number, can be negative)"
        simple = {
            "f64": "an f64 (a 64-bit decimal number)", "f32": "an f32 (a 32-bit decimal number)", "bool": "a bool (true or false)", "char": "a char (one character)",
            "str": "a str (text)", "String": "a String (text it owns and can grow)", "Self": "the type this block is about (Self)", "Ordering": "an Ordering (Less, Equal or Greater)",
        }
        if name in simple and not args:
            return simple[name]
        if name == "Vec":
            return f"a Vec of {inner or 'items'} (a growable list)"
        if name == "VecDeque":
            return f"a VecDeque of {inner} (a list you can add to and take from at both ends)"
        if name == "Option":
            return f"an Option of {inner} (either Some value or None)"
        if name == "Result":
            return f"a Result (either Ok holding {ty_src(args[0]) if args else 'a value'}, or Err holding {ty_src(args[1]) if len(args) > 1 else 'an error'})"
        if name == "Box":
            return f"a Box holding {inner} (kept on the heap)"
        if name in ("Rc", "Arc"):
            return f"an {name} holding {inner} (a value with several owners)"
        if name == "RefCell":
            return f"a RefCell holding {inner} (borrowing is checked while the program runs)"
        if name == "Cell":
            return f"a Cell holding {inner} (a value you can change through a shared reference)"
        if name in ("HashMap", "BTreeMap"):
            return f"a {name} from {ty_src(args[0]) if args else '?'} to {ty_src(args[1]) if len(args) > 1 else '?'} (key and value pairs)"
        if name in ("HashSet", "BTreeSet"):
            return f"a {name} of {inner} (each item once)"
        if name in _GEN:
            return f"a value of the generic type {name}"
        return f"{art(name)} {name}" + (f" of {inner}" if inner else "")
    if k == "ref":
        inner = t[2]
        if inner[0] == "path" and inner[1] == "str" and not t[1]:
            return "a &str (borrowed text)"
        return ("a mutable reference to " if t[1] else "a reference to ") + ty_src(inner)
    if k == "ptr":
        return f"a raw pointer to {ty_src(t[1])}"
    if k == "tuple":
        return f"a tuple of {ty_src(t)[1:-1]}"
    if k == "unit":
        return "nothing (the unit type `()`)"
    if k == "array":
        return f"an array of {t[2]} {ty_src(t[1])} (a fixed length)"
    if k == "slice":
        return f"a slice of {ty_src(t[1])} (a view of part of a list)"
    if k == "dyn":
        return f"any value that implements {ty_src(t)[4:]}"
    if k == "impl":
        return f"some type that implements {ty_src(t)[5:]}"
    if k == "fn":
        return "a function " + ty_src(t)
    if k == "never":
        return "never (the function does not come back)"
    return "a type"


def pat_names(p: tuple, out: list | None = None) -> list:
    out = [] if out is None else out
    k = p[0]
    if k == "bind":
        out.append(p[1])
        if p[3]:
            pat_names(p[3], out)
    elif k in ("tuple", "slice", "or"):
        for x in p[1]:
            pat_names(x, out)
    elif k == "tstruct":
        for x in p[2]:
            pat_names(x, out)
    elif k == "struct":
        for nm, sub in p[2]:
            if sub is None:
                out.append(nm)
            else:
                pat_names(sub, out)
    elif k == "ref":
        pat_names(p[1], out)
    return out


def pat_say(p: tuple, lvl: int = 0) -> str:
    k = p[0]
    if lvl > 5:
        return "something"
    if k == "wild":
        return "anything (`_` ignores the value)"
    if k == "rest":
        return "the rest"
    if k == "lit":
        return p[1]
    if k == "path":
        return {"None": "None (no value)"}.get(p[1], p[1])
    if k == "bind":
        s = p[1] if lvl else f"any value, which it calls {p[1]}"
        if p[3]:
            s = f"{p[1]}, as long as it is {pat_say(p[3], lvl + 1)}"
        return s
    if k == "range":
        lo, hi, incl = p[1], p[2], p[3]
        if lo is None:
            return f"{hi} or less" if incl else f"anything below {hi}"
        if hi is None:
            return f"{lo} or more"
        return f"a value from {lo} to {hi} (both included)" if incl else f"a value from {lo} up to but not including {hi}"
    if k == "tstruct":
        name = p[1].split("::")[-1] if p[1] in ("Some", "Ok", "Err") or "::" not in p[1] else p[1]
        inner = ", ".join(pat_say(x, lvl + 1) for x in p[2])
        return f"{art(name)} {name} holding {inner}" if inner else f"{art(name)} {name}"
    if k == "struct":
        parts = [f"{nm} as {pat_say(sub, lvl + 1) if sub is not None else nm}" for nm, sub in p[2]]
        return f"{art(p[1])} {p[1]} with " + ", ".join(parts) + (" and ignoring the other fields" if p[3] else "")
    if k == "tuple":
        return "a tuple of " + ", ".join(pat_say(x, lvl + 1) for x in p[1]) if p[1] else "the empty tuple"
    if k == "ref":
        return "a reference to " + pat_say(p[1], lvl + 1)
    if k == "or":
        return ", or ".join(pat_say(x, lvl + 1) for x in p[1])
    if k == "slice":
        return "a list shaped like [" + ", ".join(pat_say(x, lvl + 1) if x[0] != "rest" else ".." for x in p[1]) + "]"
    return "something"


_OPW = {"+": "plus", "-": "minus", "*": "times", "/": "divided by", "==": "equals", "!=": "is not equal to", "<": "is less than", ">": "is greater than", "<=": "is at most", ">=": "is at least",
        "&&": "and", "||": "or", "&": "bitwise-AND", "|": "bitwise-OR", "^": "bitwise-XOR", "<<": "shifted left by", ">>": "shifted right by"}


def _is_float(n: N) -> bool:
    return n.kind == "num" and bool(re.search(r"\.|f32|f64|e", n.a[0].lower())) and not n.a[0].lower().startswith("0x")


def _atomic(n: N) -> bool:
    return n.kind in ("num", "str", "char", "bool", "path", "unit")


# method vocabulary: name -> (a noun phrase for a single call, the same as a step in a chain)
_M: dict[str, tuple[str, str]] = {
    "len": ("the length of {r}", "taking its length"), "is_empty": ("whether {r} is empty", "checking whether it is empty"),
    "clone": ("a separate copy of {r}", "making a separate copy"), "to_string": ("{r} turned into a String", "turning it into a String"),
    "to_owned": ("an owned copy of {r}", "making an owned copy"), "into": ("{r} converted to the type needed here", "converting it to the type needed here"),
    "as_str": ("{r} viewed as a &str", "viewing it as a &str"), "as_bytes": ("the bytes of {r}", "taking its bytes"), "bytes": ("the bytes of {r}, one at a time", "going through its bytes"),
    "chars": ("the characters of {r}, one at a time", "going through its characters one at a time"), "char_indices": ("the characters of {r} with their positions", "going through its characters with their positions"),
    "lines": ("the lines of {r}", "going through its lines"), "split": ("{r} cut into pieces at {a0}", "cutting it into pieces at {a0}"),
    "split_whitespace": ("{r} cut into words", "cutting it into words"), "trim": ("{r} without the spaces at both ends", "cutting off the spaces at both ends"),
    "to_uppercase": ("{r} in capitals", "making it capitals"), "to_lowercase": ("{r} in small letters", "making it small letters"),
    "to_ascii_uppercase": ("{r} in capitals", "making it capitals"), "to_ascii_lowercase": ("{r} in small letters", "making it small letters"),
    "starts_with": ("whether {r} starts with {a0}", "checking whether it starts with {a0}"), "ends_with": ("whether {r} ends with {a0}", "checking whether it ends with {a0}"),
    "contains": ("whether {r} contains {a0}", "checking whether it contains {a0}"), "contains_key": ("whether {r} has the key {a0}", "checking whether it has the key {a0}"),
    "replace": ("{r} with {a0} replaced by {a1}", "replacing {a0} with {a1}"), "repeat": ("{r} repeated {a0} times", "repeating it {a0} times"),
    "parse": ("{r} read as a value of the wanted type (a Result, since the text may not fit)", "reading it as a value of the wanted type (gives a Result)"),
    "push": ("adds {a0} to the end of {r}", "adding {a0} on the end"), "push_str": ("adds the text {a0} to the end of {r}", "adding the text {a0} on the end"),
    "pop": ("removes the last item of {r} and gives it back (an Option)", "removing the last item"), "insert": ("puts {all} into {r}", "putting {all} in"),
    "remove": ("takes {a0} out of {r}", "taking {a0} out"), "clear": ("empties {r}", "emptying it"), "extend": ("adds all of {a0} to {r}", "adding all of {a0}"),
    "extend_from_slice": ("adds all of {a0} to {r}", "adding all of {a0}"), "retain": ("keeps only the items of {r} for which {b0}", "keeping only the items for which {b0}"),
    "truncate": ("cuts {r} down to {a0} items", "cutting it down to {a0} items"), "drain": ("takes the items {a0} out of {r}", "taking those items out"),
    "sort": ("sorts {r} from smallest to largest", "sorting it from smallest to largest"), "sort_unstable": ("sorts {r} from smallest to largest", "sorting it from smallest to largest"),
    "sort_by": ("sorts {r} using {c0}", "sorting it using {c0}"), "sort_by_key": ("sorts {r} by {b0}", "sorting it by {b0}"), "dedup": ("removes repeated neighbours from {r}", "removing repeated neighbours"),
    "reverse": ("reverses {r} in place", "reversing it in place"), "swap": ("swaps items {a0} and {a1} of {r}", "swapping items {a0} and {a1}"),
    "join": ("the items of {r} joined into one text with {a0} between them", "joining the items into one text with {a0} between them"), "concat": ("the items of {r} joined end to end", "joining the items end to end"),
    "to_vec": ("{r} copied into a new Vec", "copying it into a new Vec"), "first": ("the first item of {r} (an Option: None if there is none)", "taking the first item (an Option)"),
    "last": ("the last item of {r} (an Option)", "taking the last item (an Option)"), "get": ("the item of {r} at {a0} (an Option: None if it is not there)", "getting the item at {a0} (an Option)"),
    "get_mut": ("a changeable view of the item of {r} at {a0} (an Option)", "getting a changeable view of the item at {a0}"), "iter": ("{r} as something to go through one item at a time (the items are borrowed)", "going through its items one at a time (borrowed)"),
    "iter_mut": ("{r} as something to go through, with each item changeable", "going through its items so each can be changed"), "into_iter": ("{r} as something to go through, taking the items out of it", "going through its items, taking them out"),
    "map": ("each item of {r} changed by {c0}", "changing each item {p0} into {b0}"), "filter": ("the items of {r} that pass {c0}", "keeping only the items {p0} for which {b0}"),
    "filter_map": ("the items of {r} changed by {c0}, dropping the ones that give None", "changing each item {p0} into {b0} and dropping the Nones"),
    "flat_map": ("each item of {r} changed into a list by {c0}, all joined up", "changing each item {p0} into a list ({b0}) and joining the lists"),
    "flatten": ("{r} with one level of nesting removed", "removing one level of nesting"), "enumerate": ("the items of {r} paired with their positions (from 0)", "pairing each item with its position (from 0)"),
    "zip": ("the items of {r} paired up with the items of {a0}", "pairing each item with the item of {a0} at the same place"), "rev": ("the items of {r} backwards", "going backwards"),
    "skip": ("the items of {r} after the first {a0}", "skipping the first {a0}"), "take": ("the first {a0} items of {r}", "taking only the first {a0}"),
    "take0": ("the value taken out of {r}, leaving None behind", "taking the value out, leaving None behind"), "step_by": ("every {a0}th item of {r}", "taking every {a0}th item"),
    "chain": ("the items of {r} followed by those of {a0}", "adding the items of {a0} on the end"), "windows": ("overlapping runs of {a0} items of {r}", "sliding a window of {a0} items along"),
    "chunks": ("{r} cut into chunks of {a0} items", "cutting it into chunks of {a0} items"), "peekable": ("{r} that lets you look at the next item without taking it", "making it able to look ahead"),
    "cloned": ("copies of the items of {r}", "copying each item"), "copied": ("copies of the items of {r}", "copying each item"), "take_while": ("the items of {r} up to the first one that fails {c0}", "taking items until one fails {b0}"),
    "skip_while": ("the items of {r} after the leading ones that pass {c0}", "skipping the items that pass {b0}"), "sum": ("the sum of the items of {r}", "adding them all up"),
    "product": ("the product of the items of {r}", "multiplying them all together"), "count": ("how many items {r} has", "counting them"), "min": ("the smallest item of {r} (an Option)", "finding the smallest (an Option)"),
    "max": ("the largest item of {r} (an Option)", "finding the largest (an Option)"), "min1": ("the smaller of {r} and {a0}", "taking the smaller of it and {a0}"), "max1": ("the larger of {r} and {a0}", "taking the larger of it and {a0}"),
    "min_by_key": ("the item of {r} with the smallest {b0}", "finding the item with the smallest {b0}"), "max_by_key": ("the item of {r} with the largest {b0}", "finding the item with the largest {b0}"),
    "fold": ("{a0} combined with each item of {r} by {c1}", "folding the items into one value, starting from {a0} and combining with {c1}"), "any": ("whether any item of {r} passes {c0}", "checking whether any item passes {b0}"),
    "all": ("whether every item of {r} passes {c0}", "checking whether every item passes {b0}"), "find": ("the first item of {r} that passes {c0} (an Option)", "finding the first item for which {b0} (an Option)"),
    "position": ("the position of the first item of {r} that passes {c0} (an Option)", "finding the position of the first item for which {b0} (an Option)"),
    "collect": ("the items of {r} gathered into a collection of the wanted type", "gathering them into a collection of the wanted type"), "for_each": ("runs {c0} for each item of {r}", "running {c0} on each item"),
    "next": ("the next item of {r} (an Option: None when it has run out)", "taking the next item (an Option)"), "nth": ("the item of {r} at position {a0}, using up the ones before it", "taking item {a0}, using up the ones before it"),
    "peek": ("a look at the next item of {r} without taking it", "looking at the next item without taking it"),
    "unwrap": ("the value inside {r} (stops the program with an error if there is none)", "unwrapping it (stops the program with an error if there is no value)"),
    "expect": ("the value inside {r} (stops with the message {a0} if there is none)", "unwrapping it (stops with the message {a0} if there is no value)"),
    "unwrap_or": ("the value inside {r}, or {a0} if there is none", "unwrapping it, or using {a0} if there is no value"), "unwrap_or_else": ("the value inside {r}, or what {c0} gives if there is none", "unwrapping it, or using what {b0} gives if there is no value"),
    "unwrap_or_default": ("the value inside {r}, or the type's default if there is none", "unwrapping it, or using the default if there is no value"), "unwrap_err": ("the error inside {r}", "taking the error out"),
    "is_some": ("whether {r} holds a value", "checking whether it holds a value"), "is_none": ("whether {r} is None", "checking whether it is None"), "is_ok": ("whether {r} is Ok", "checking whether it is Ok"),
    "is_err": ("whether {r} is an Err", "checking whether it is an Err"), "ok": ("{r} as an Option (Ok becomes Some, Err becomes None)", "turning it into an Option"), "err": ("the error of {r} as an Option", "taking the error as an Option"),
    "ok_or": ("{r} as a Result: Ok of the value, or Err of {a0} if there is none", "turning it into a Result with {a0} as the error"), "map_err": ("{r} with its error changed by {c0}", "changing the error with {c0}"),
    "and_then": ("{r} followed by {c0} if it holds a value", "continuing with {c0} if there is a value"), "or_else": ("{r}, or what {c0} gives if it failed", "trying {c0} if it failed"),
    "as_ref": ("a borrowed view of what is inside {r}", "borrowing what is inside"), "as_mut": ("a changeable view of what is inside {r}", "borrowing what is inside so it can change"),
    "borrow": ("a shared borrow of what is inside {r}", "borrowing what is inside"), "borrow_mut": ("a changeable borrow of what is inside {r}, checked while the program runs", "borrowing what is inside so it can change"),
    "get0": ("the value held in {r}", "reading the value held in it"), "set": ("sets {r} to {a0}", "setting it to {a0}"), "lock": ("the lock on {r}", "locking it"), "abs": ("the size of {r} without its sign", "dropping the sign"), "pow": ("{r} to the power {a0}", "raising it to the power {a0}"),
    "powi": ("{r} to the power {a0}", "raising it to the power {a0}"), "powf": ("{r} to the power {a0}", "raising it to the power {a0}"), "sqrt": ("the square root of {r}", "taking the square root"),
    "floor": ("{r} rounded down", "rounding down"), "ceil": ("{r} rounded up", "rounding up"), "round": ("{r} rounded to the nearest whole number", "rounding to the nearest whole number"),
    "rem_euclid": ("the remainder of {r} divided by {a0}, never negative", "taking the remainder after dividing by {a0}, never negative"), "div_euclid": ("{r} divided by {a0}, rounded down", "dividing by {a0}, rounding down"),
    "signum": ("the sign of {r} (-1, 0 or 1)", "taking its sign"), "is_alphabetic": ("whether {r} is a letter", "checking whether it is a letter"), "is_numeric": ("whether {r} is a number character", "checking whether it is a number character"),
    "is_ascii_digit": ("whether {r} is a digit 0 to 9", "checking whether it is a digit 0 to 9"), "is_alphanumeric": ("whether {r} is a letter or a digit", "checking whether it is a letter or a digit"),
    "is_whitespace": ("whether {r} is a space or similar", "checking whether it is a space or similar"), "is_uppercase": ("whether {r} is a capital", "checking whether it is a capital"), "to_digit": ("{r} as a number in base {a0} (an Option)", "reading it as a digit in base {a0} (an Option)"),
    "cmp": ("how {r} compares with {a0} (Less, Equal or Greater)", "comparing it with {a0}"), "partial_cmp": ("how {r} compares with {a0} (an Option, None if they cannot be ordered)", "comparing it with {a0} (an Option)"),
    "entry": ("the slot of {r} for the key {a0}", "looking up the slot for the key {a0}"), "or_insert": ("the value in {r}, putting {a0} there first if the slot was empty", "using the value, putting {a0} there first if the slot was empty"),
    "keys": ("the keys of {r}", "going through the keys"), "values": ("the values of {r}", "going through the values"), "push_back": ("adds {a0} to the back of {r}", "adding {a0} at the back"),
    "push_front": ("adds {a0} to the front of {r}", "adding {a0} at the front"), "pop_front": ("removes the first item of {r}", "removing the first item"), "pop_back": ("removes the last item of {r}", "removing the last item"),
    "binary_search": ("looks for {a0} in the sorted {r}", "looking for {a0} (it must be sorted)"), "split_at": ("{r} cut in two at {a0}", "cutting it in two at {a0}"), "abs_diff": ("the distance between {r} and {a0}", "taking its distance from {a0}"),
    "eq": ("whether {r} equals {a0}", "checking whether it equals {a0}"), "capacity": ("how much room {r} has reserved", "taking its reserved room"), "len_utf8": ("how many bytes {r} takes as text", "counting its bytes as text"),
    "as_slice": ("{r} as a slice", "viewing it as a slice"), "to_le_bytes": ("the bytes of {r}, smallest first", "taking its bytes"), "drop": ("drops {r}", "dropping it"), "get_or_insert_with": ("the value in {r}, creating it with {c0} if empty", "using the value, creating it first if it is empty"),
    "replace_with": ("{r} replaced", "replacing it"), "last_mut": ("a changeable view of the last item of {r}", "getting a changeable view of the last item"), "first_mut": ("a changeable view of the first item of {r}", "getting a changeable view of the first item"),
}
_ARITH = {"wrapping": "going round to the other end when it overflows", "checked": "giving None when it overflows (an Option)", "saturating": "stopping at the limit when it overflows", "overflowing": "giving the result and whether it overflowed"}
_ARITH_OP = {"add": "plus", "sub": "minus", "mul": "times", "div": "divided by", "pow": "to the power", "neg": "negated", "rem": "remainder"}
_FACT_METHODS = {"clone": "clonefact", "len": "lenbytes", "parse": "parse", "unwrap_or": "unwrapor", "as_bytes": "asbytes", "unwrap": "unwrapnone", "expect": "unwrapnone", "borrow_mut": "refcell", "push": "needsmut", "push_str": "needsmut"}
_LAZY = {"map", "filter", "filter_map", "flat_map", "enumerate", "zip", "rev", "skip", "take", "step_by", "chain", "windows", "chunks", "peekable", "cloned", "copied", "take_while", "skip_while", "inspect"}
_MUT_STMT = {"push", "push_str", "pop", "insert", "remove", "clear", "extend", "retain", "truncate", "sort", "sort_by", "sort_by_key", "dedup", "reverse", "swap", "set", "push_back", "push_front", "pop_front", "pop_back", "drain", "extend_from_slice", "sort_unstable"}


def _closure_bits(n: N) -> tuple[str, str, str]:
    """(parameter names, what it gives, the whole closure as words) for a closure argument; a plain function is described too."""
    if n.kind == "closure":
        names = []
        for pat, _ty in n.a[0]:
            names.extend(pat_names(pat))
        params = " and ".join(names) if names else "nothing"
        body = n.a[1]
        b = say(body, 2) if body is not None else "what the lines below work out"
        return params or "x", b, f"a closure taking {params} that gives {b}"
    s = code(n.src, 40)
    return "x", f"{s} is applied to it", f"the function {s}"


def _args_say(args: list, lvl: int) -> list[str]:
    return [say(a, lvl + 1) for a in args]


def _flatten(n: N) -> tuple[N, list]:
    """A chain `base.a().b()?.c` -> (base, [steps]); a step is ('m', node) or ('?', node) or ('f', node)."""
    steps = []
    cur = n
    while cur.kind in ("mcall", "try", "field", "await"):
        steps.append(({"mcall": "m"}.get(cur.kind, cur.kind), cur))
        cur = cur.a[0]
    steps.reverse()
    return cur, steps


def _method_texts(node: N, recv: str, lvl: int, step: bool) -> str:
    name, targs, args = node.a[1], node.a[2], node.a[3]
    argv = _args_say(args, lvl)
    slots = {f"a{i}": (argv[i] if i < len(argv) else "it") for i in range(3)}
    slots["all"] = ", ".join(argv) if argv else "nothing"
    slots["r"] = recv
    clos = [a for a in args if a.kind == "closure"]
    p0 = b0 = c0 = c1 = "it"
    if args:
        p0, b0, c0 = _closure_bits(args[0])
    if len(args) > 1:
        _p, _b, c1 = _closure_bits(args[1])
    if args and args[0].kind != "closure":
        # a plain function as the argument: say so, with a0 as the name
        pass
    slots.update(p0=p0, b0=b0, c0=c0, c1=c1)
    key = name
    if name in ("min", "max") and args:
        key = name + "1"
    if name == "take" and not args:
        key = "take0"
    if name == "get" and not args:
        key = "get0"
    m = re.match(r"^(wrapping|checked|saturating|overflowing)_(\w+)$", name)
    if key in _M:
        noun, stp = _M[key]
        out = (stp if step else noun).format(**slots)
        if name == "collect" and targs:
            out += f" (as {code(targs, 30)})"
        if name == "sum" and targs:
            out += f" (as {code(targs, 20)})"
        if name == "iter" or name == "len":
            pass
    elif m:
        how = _ARITH[m.group(1)]
        op = _ARITH_OP.get(m.group(2), m.group(2))
        if m.group(2) in ("abs", "neg", "unsigned_abs"):
            out = f"taking its {'size without the sign' if 'abs' in m.group(2) else 'negative'}, {how}" if step else f"the {'size of {r} without the sign' if 'abs' in m.group(2) else 'negative of {r}'}, {how}".format(r=recv)
        else:
            out = f"taking it {op} {slots['a0']}, {how}" if step else f"{recv} {op} {slots['a0']}, {how}"
        want("wrapping")
    else:
        a = f" with {', '.join(argv)}" if argv else ""
        out = f"calling {name}{a}" if step else f"the result of calling {name} on {recv}{a}"
    out += _moved_note(args)
    k = _FACT_METHODS.get(name)
    if k:
        want(k)
    if name in _LAZY:
        pass
    del clos
    return out


_OWNING_CALLS = {"String::from", "String::new", "Vec::new", "Box::new", "HashMap::new", "HashSet::new", "Vec::with_capacity", "String::with_capacity", "BTreeMap::new", "BTreeSet::new", "VecDeque::new", "Rc::new", "RefCell::new"}


def _owned_expr(e: N | None) -> bool:
    if e is None:
        return False
    k = e.kind
    if k == "macro":
        return e.a[0] in ("vec", "format")
    if k == "call" and e.a[0].kind == "path":
        return e.a[0].a[0] in _OWNING_CALLS
    if k == "mcall":
        if e.a[1] in ("to_string", "to_owned", "collect", "to_vec"):
            return True
        return e.a[1] == "clone" and _owned_expr(e.a[0])
    if k == "path":
        return e.a[0] in _OWNED
    return False


def _moved_note(args: list) -> str:
    names = [a.a[0] for a in args if a.kind == "path" and a.a[0] in _OWNED]
    if not names:
        return ""
    want("move")
    return f" (this moves {', '.join(names)} in: it cannot be used again afterwards)"


def _chain_say(n: N, lvl: int, statement: bool = False) -> str:
    base, steps = _flatten(n)
    while steps and steps[0][0] == "field":
        base = steps[0][1]
        steps = steps[1:]
    names = [s[1].a[1] for s in steps if s[0] == "m"]
    b = say(base, lvl + 1)
    if len(steps) == 1 and steps[0][0] == "m" and not statement:
        return _method_texts(steps[0][1], b, lvl, False)
    parts = []
    for kind, node in steps:
        if kind == "m":
            parts.append(_method_texts(node, "it", lvl, True))
        elif kind == "try":
            parts.append("applying `?` (an Err or None makes this function stop and return it)")
            want("qmark")
        elif kind == "field":
            nm = node.a[1]
            parts.append(f"taking its field {nm}" if not nm.isdigit() else f"taking item {nm} of it")
        else:
            parts.append("waiting for it to finish")
    if names and names[-1] in _LAZY:
        want("lazy")
    if len(steps) == 1 and steps[0][0] == "m":
        return f"works on {b}: {parts[0]}" if statement else parts[0]
    return (f"works on {b}: " if statement else f"the result of taking {b}, then ") + ", then ".join(parts)


_PATHCALL = {
    "String::from": "a String made from {a0}", "String::new": "an empty String", "Vec::new": "an empty Vec", "Vec::with_capacity": "an empty Vec with room reserved for {a0} items",
    "HashMap::new": "an empty HashMap", "HashSet::new": "an empty HashSet", "BTreeMap::new": "an empty BTreeMap", "VecDeque::new": "an empty VecDeque", "BTreeSet::new": "an empty BTreeSet",
    "Box::new": "{a0} put in a Box (kept on the heap)", "Rc::new": "{a0} wrapped in an Rc (a value with several owners)", "Arc::new": "{a0} wrapped in an Arc (a value with several owners)",
    "RefCell::new": "{a0} wrapped in a RefCell (borrowing checked while the program runs)", "Cell::new": "{a0} wrapped in a Cell", "Some": "a Some holding {a0}", "Ok": "an Ok holding {a0}", "Err": "an Err holding {a0}",
    "Default::default": "the default value of the type needed", "drop": "drops {a0} (frees it right now)", "std::mem::swap": "swaps the values of {a0} and {a1}", "mem::swap": "swaps the values of {a0} and {a1}",
    "std::mem::replace": "what {a0} held, after {a1} is put in its place", "mem::replace": "what {a0} held, after {a1} is put in its place", "std::mem::take": "the value taken out of {a0}, which is left holding the default",
    "mem::take": "the value taken out of {a0}, which is left holding the default", "Rc::clone": "another owner of {a0} (it shares the value, it does not copy it)", "Arc::clone": "another owner of {a0} (it shares the value, it does not copy it)",
    "Rc::strong_count": "how many owners {a0} has", "Rc::ptr_eq": "whether {a0} and {a1} are the same value", "String::with_capacity": "an empty String with room for {a0} bytes", "char::from_digit": "the digit character for {a0} in base {a1}",
    "char::from_u32": "the character with code {a0} (an Option)", "std::process::exit": "ends the program with the status {a0}", "std::mem::size_of_val": "the size of {a0} in bytes", "std::mem::size_of": "the size of a type in bytes",
    "Rc::try_unwrap": "the value out of {a0} if it has no other owners (a Result)", "thread::spawn": "starts {a0} on a new thread", "std::thread::spawn": "starts {a0} on a new thread",
}
_CONSTS = {"MAX": "the largest value", "MIN": "the smallest value", "EPSILON": "the tiny gap between 1 and the next float", "INFINITY": "infinity", "NAN": "not-a-number", "PI": "pi"}


def _fmt_phrase(args: list, lvl: int, first_is_dest: bool = False) -> tuple[str, str]:
    """(what is built from the format string, '' ) - reads the string's placeholders one by one."""
    if not args or args[0].kind != "str":
        return ("", "")
    raw = args[0].a[0]
    parts = fmt_parts(raw)
    rest = args[1:]
    named = {}
    pos = []
    for a in rest:
        if a.kind == "asg" and a.a[0] == "=" and a.a[1].kind == "path":
            named[a.a[1].a[0]] = a.a[2]
        else:
            pos.append(a)
    nxt = 0
    texts = []
    for ph in parts:
        if ph[0] == "lit":
            continue
        _k, argspec, spec = ph
        if argspec == "":
            arg = pos[nxt] if nxt < len(pos) else None
            nxt += 1
            shown = say(arg, lvl + 1) if arg is not None else "an argument given on the next line"
            argnode = arg
        elif argspec.isdigit():
            idx = int(argspec)
            argnode = pos[idx] if idx < len(pos) else None
            shown = say(argnode, lvl + 1) if argnode is not None else "an argument given on the next line"
            want("position")
        else:
            argnode = named.get(argspec)
            shown = say(argnode, lvl + 1) if argnode is not None else f"the variable {argspec}"
            if argnode is None:
                want("inline")
        texts.append(_spec_phrase(f"{{{argspec}{':' + spec if spec else ''}}}", shown, spec, argnode))
    if "{{" in raw or "}}" in raw:
        want("braces")
    return raw, "; ".join(texts)


_SPEC = re.compile(r"^(?:(.)?([<^>]))?([+-])?(#)?(0)?(\d+\$?|\w+\$)?(?:\.(\d+\$?|\*|\w+\$))?(\?|x\?|X\?|x|X|o|b|e|E|p)?$", re.S)


def fmt_parts(raw: str) -> list:
    """The placeholders of a format string: ('lit', text) or ('ph', argument, spec)."""
    inner = raw
    m = re.match(r'^(?:b|c)?r?#*"', inner)
    if m:
        inner = inner[m.end() :]
        inner = re.sub(r'"#*$', "", inner)
    parts, i, n, lit = [], 0, len(inner), ""
    while i < n:
        ch = inner[i]
        if ch == "{" and inner[i : i + 2] == "{{":
            lit += "{"
            i += 2
        elif ch == "}" and inner[i : i + 2] == "}}":
            lit += "}"
            i += 2
        elif ch == "{":
            j = inner.find("}", i)
            if j < 0:
                lit += inner[i:]
                break
            if lit:
                parts.append(("lit", lit))
                lit = ""
            body = inner[i + 1 : j]
            arg, _, spec = body.partition(":")
            parts.append(("ph", arg.strip(), spec))
            i = j + 1
        else:
            lit += ch
            i += 1
    if lit:
        parts.append(("lit", lit))
    return parts


def _spec_phrase(ph: str, shown: str, spec: str, argnode: N | None) -> str:
    m = _SPEC.match(spec) if spec else None
    if not spec:
        if argnode is not None and _is_float(argnode):
            want("floatshow")
        return f"`{ph}` shows {shown}"
    if not m:
        return f"`{ph}` shows {shown}, formatted as `{spec}`"
    fill, align, sign, alt, zero, width, prec, ty = m.groups()
    what = {"": "", "?": "in Debug form", "x?": "in Debug form", "X?": "in Debug form", "x": "in hexadecimal (base 16, lower case)", "X": "in hexadecimal (base 16, upper case)",
            "o": "in octal (base 8)", "b": "in binary (base 2)", "e": "in scientific notation", "E": "in scientific notation", "p": "as an address"}.get(ty or "", "")
    if ty == "?":
        want("debugquotes")
        if alt:
            what = "in a pretty, multi-line Debug form"
    if ty in ("x", "X"):
        want("hex")
        if alt:
            what += ", starting with 0x"
    if ty == "b":
        want("bin")
    if ty == "o":
        want("oct")
    if ty in ("e", "E"):
        want("exp")
    out = f"`{ph}` shows {shown}" + (f" {what}" if what else "")
    extras = []
    if width:
        w = width if not width.endswith("$") else f"the width held in {width[:-1]}"
        al = {"<": "left-aligned (padding on the right)", ">": "right-aligned (padding on the left)", "^": "centred"}.get(align or "", "")
        if zero:
            extras.append(f"padded with zeros to at least {w} wide")
            want("zeropad")
        else:
            extras.append(f"padded to at least {w} wide" + (f", {al}" if al else " (numbers go on the right, text on the left)"))
            want("width" if align else "defalign")
            if fill:
                extras.append(f"with `{fill}` as the padding")
    elif zero:
        extras.append("padded with zeros")
    if prec:
        extras.append("with the number of digits taken from an argument" if prec in ("*",) or prec.endswith("$") else f"with {prec} digit{'s' if prec != '1' else ''} after the point (or {prec} characters of text)")
        want("prec")
    if sign == "+":
        extras.append("always showing its sign")
        want("plus")
    if extras:
        out += ", " + ", ".join(extras)
    return out


_FMT_MACROS = {"println", "print", "eprintln", "eprint", "format", "panic", "write", "writeln", "unreachable", "todo", "unimplemented", "assert", "assert_eq", "assert_ne", "debug_assert", "debug_assert_eq", "expect"}


def _macro_say(n: N, lvl: int, stmt: bool) -> str | None:
    name, args = n.a[0], n.a[1]
    if name in ("println", "print", "eprintln", "eprint"):
        nl = name.endswith("ln")
        err = name.startswith("e")
        where = "the error output (not the normal output)" if err else "the screen"
        if not args:
            return f"writes an empty line to {where}" if nl else f"writes nothing to {where}"
        if args[0].kind != "str":
            return f"writes {', '.join(_args_say(args, lvl))} to {where}"
        raw, specs = _fmt_phrase(args, lvl)
        txt = f"writes {code(raw, 70)} to {where}" if not specs else f"writes {code(raw, 70)} to {where}, where {specs}"
        return txt + (", then ends the line" if nl else ", without ending the line")
    if name == "format":
        if args and args[0].kind == "str":
            raw, specs = _fmt_phrase(args, lvl)
            return f"a String built from {code(raw, 70)}" + (f", where {specs}" if specs else "")
        return "a String built from a format"
    if name in ("write", "writeln") and args:
        dest = say(args[0], lvl + 1)
        if len(args) > 1 and args[1].kind == "str":
            raw, specs = _fmt_phrase(args[1:], lvl)
            return f"writes {code(raw, 70)} into {dest}" + (f", where {specs}" if specs else "") + (", then ends the line" if name == "writeln" else "")
        return f"writes into {dest}"
    if name == "panic":
        if args and args[0].kind == "str":
            raw, specs = _fmt_phrase(args, lvl)
            return f"stops the program at once (a panic) with the message {code(raw, 70)}" + (f", where {specs}" if specs else "")
        return "stops the program at once (a panic)"
    if name in ("unreachable", "todo", "unimplemented"):
        return {"unreachable": "marks a spot the program should never reach (it panics if it does)", "todo": "marks code not written yet (it panics if reached)", "unimplemented": "marks code not written yet (it panics if reached)"}[name]
    if name in ("assert", "debug_assert") and args:
        return f"checks that {say(args[0], lvl + 1)} (the program panics if it does not)"
    if name in ("assert_eq", "assert_ne", "debug_assert_eq") and len(args) >= 2:
        w = "equals" if name != "assert_ne" else "is different from"
        return f"checks that {say(args[0], lvl + 1)} {w} {say(args[1], lvl + 1)} (the program panics and shows both values if not)"
    if name == "vec" and n.open and not args:
        return "a Vec (a growable list) whose items are on the next lines"
    if name == "vec":
        if n.a[3] and len(args) == 2:
            return f"a Vec (a growable list) of {say(args[1], lvl + 1)} copies of {say(args[0], lvl + 1)}"
        if not args:
            return "an empty Vec (a growable list)"
        shown = ", ".join(_args_say(args[:6], lvl)) + (f" and {len(args) - 6} more" if len(args) > 6 else "")
        return f"a Vec (a growable list) holding {shown}"
    if name == "matches" and len(args) >= 2:
        return f"whether {say(args[0], lvl + 1)} fits the pattern {code(args[1].src, 40)}"
    if name == "dbg":
        return "prints the expression and its value to the error output, and gives the value back"
    if name in ("include_str", "concat", "stringify", "env", "line", "file", "cfg"):
        return f"the compiler macro {name}!"
    return f"the macro {name}! applied to {', '.join(_args_say(args, lvl)) or 'nothing'}"


def say(n: N | None, lvl: int = 0) -> str:
    """One expression as a noun phrase (or, for a call that does something, a verb phrase)."""
    out = _say(n, lvl)
    if n is not None and n.open and n.kind in ("call", "mcall", "macro", "array", "tuple", "struct") and not out.endswith("next lines"):
        out += " (the rest of it is on the next lines)"
    return out


def _say(n: N | None, lvl: int = 0) -> str:
    if n is None:
        return "nothing"
    if lvl > 4:
        return "`" + code(n.src, 40) + "`"
    k = n.kind
    if k == "num":
        return n.a[0]
    if k == "bool":
        return n.a[0]
    if k == "str":
        return "the text " + code(n.a[0], 50) if lvl or True else n.a[0]
    if k == "char":
        return "the character " + n.a[0]
    if k == "unit":
        return "nothing (`()`)"
    if k == "path":
        p = n.a[0]
        last = p.split("::")[-1]
        if "::" in p and last in _CONSTS:
            return f"{_CONSTS[last]} of {p.rsplit('::', 1)[0].split('::')[-1]} ({code(p, 30)})"
        return p
    if k == "paren":
        return say(n.a[0], lvl)
    if k == "field":
        obj, f = n.a
        o = say(obj, lvl + 1)
        return f"item {f} of {o}" if f.isdigit() else f"the {f} of {o}"
    if k == "idx":
        obj, ix = n.a
        o = say(obj, lvl + 1)
        if ix.kind == "range":
            lo, hi, incl = ix.a
            want("indexpanic")
            return f"the slice of {o} from position {say(lo, lvl + 1) if lo else 'the start'} " + ("up to the end" if hi is None else f"{'up to and including' if incl else 'up to but not including'} {say(hi, lvl + 1)}")
        want("indexpanic")
        return f"item {say(ix, lvl + 1)} of {o}"
    if k == "un":
        op, e = n.a
        if op == "-":
            return "-" + say(e, lvl + 1) if e.kind == "num" else f"minus {say(e, lvl + 1)}"
        if op == "!":
            return f"not {say(e, lvl + 1)}"
        if op == "*":
            want("deref")
            return f"what {say(e, lvl + 1)} points to"
        if op == "&":
            if e.kind == "idx" and e.a[1].kind == "range":
                return say(e, lvl)
            want("borrow")
            return f"a reference to {say(e, lvl + 1)}"
        want("mutborrow")
        return f"a mutable reference to {say(e, lvl + 1)}"
    if k == "bin":
        op, l, r = n.a
        ls = say(l, lvl + 1)
        rs = say(r, lvl + 1)
        if l.kind == "bin" and _BIN[l.a[0]] < _BIN[op]:
            ls = f"({ls})"
        if r.kind == "bin" and _BIN[r.a[0]] <= _BIN[op]:
            rs = f"({rs})"
        if op == "/":
            if not (_is_float(l) or _is_float(r)):
                want("div")
        if op == "%":
            want("rem")
            return f"the remainder of {ls} divided by {rs}"
        return f"{ls} {_OPW[op]} {rs}"
    if k == "cast":
        e, ty = n.a
        tname = ty_src(ty)
        if tname in _INTS:
            want("asfloat" if _is_float(e) else "astrunc")
            if e.kind == "char":
                want("aschar")
        elif tname == "char":
            want("aschar")
        return f"{say(e, lvl + 1)} converted to {ty_phrase(ty)} with `as`"
    if k == "range":
        lo, hi, incl = n.a
        want("rangeex")
        if lo is None and hi is None:
            return "the whole range (`..`)"
        if lo is None:
            return f"everything up to {'and including ' if incl else 'but not including '}{say(hi, lvl + 1)}"
        if hi is None:
            return f"everything from {say(lo, lvl + 1)} on"
        return f"the numbers from {say(lo, lvl + 1)} up to {'and including ' if incl else 'but not including '}{say(hi, lvl + 1)}"
    if k == "tuple":
        return "a tuple of " + ", ".join(_args_say(n.a[0][:6], lvl))
    if k == "array":
        items = n.a[0]
        return "an array of " + (", ".join(_args_say(items[:6], lvl)) + (f" and {len(items) - 6} more" if len(items) > 6 else "")) if items else "an empty array"
    if k == "repeat":
        return f"an array of {say(n.a[1], lvl + 1)} copies of {say(n.a[0], lvl + 1)}"
    if k == "struct":
        name, fields, base = n.a
        parts = [f"{f} set to {say(v, lvl + 1) if v is not None else 'the variable ' + f}" for f, v in fields]
        s = f"{art(name)} {name}" + (" with " + ", ".join(parts[:6]) if parts else "")
        return s + (f", and the other fields copied from {say(base, lvl + 1)}" if base is not None else "")
    if k == "closure":
        params, body, mv, _ret = n.a
        names = []
        for pat, _t in params:
            names.extend(pat_names(pat))
        s = ("a `move` closure (it takes ownership of the variables it uses)" if mv else "a closure (a small function written inline)")
        if mv:
            want("movecl")
        s += f" taking {' and '.join(names)}" if names else " taking nothing"
        return s + (f" that gives {say(body, lvl + 1)}" if body is not None else " (its body is on the lines below)")
    if k == "try":
        want("qmark")
        return f"{say(n.a[0], lvl + 1)}, and if that is an Err (or None) this function stops here and returns it (`?`)"
    if k == "await":
        return f"{say(n.a[0], lvl + 1)}, waiting for it to finish"
    if k == "macro":
        return _macro_say(n, lvl, False) or "`" + code(n.src, 40) + "`"
    if k == "call":
        return _call_say(n, lvl)
    if k in ("mcall",):
        return _chain_say(n, lvl)
    if k == "asg":
        op, l, r = n.a
        return f"sets {say(l, lvl + 1)} to {say(r, lvl + 1)}" if op == "=" else f"{_ASG_WORD[op].format(l=say(l, lvl + 1), r=say(r, lvl + 1))}"
    if k == "ifhead":
        return f"whichever of two values the `if` picks (the first when {say(n.a[0], lvl + 1)})"
    if k == "iflet":
        return f"the result of: if {say(n.a[1], lvl + 1)} fits {pat_say(n.a[0], 1)}"
    if k == "matchhead":
        return f"the result of matching {say(n.a[0], lvl + 1)} against the arms below"
    if k == "later":
        return "the expression on the next line"
    if k == "blockhead":
        return {"labeled": "the value of the labeled block below (`break` with its label leaves it early, with a value)", "block": "the value of the block below", "loop": "the result of the loop below", "unsafe": "the result of the unsafe block below", "async": "an async block"}[n.a[0]]
    if k == "return":
        return "returning " + say(n.a[0], lvl + 1) if n.a[0] is not None else "returning nothing"
    if k in ("raw",):
        return "`" + code(n.a[0], 40) + "`"
    return "`" + code(n.src, 40) + "`"


_ASG_WORD = {"+=": "adds {r} to {l}", "-=": "subtracts {r} from {l}", "*=": "multiplies {l} by {r}", "/=": "divides {l} by {r}", "%=": "sets {l} to the remainder of {l} divided by {r}",
             "&=": "ANDs the bits of {r} into {l}", "|=": "ORs the bits of {r} into {l}", "^=": "XORs the bits of {r} into {l}", "<<=": "shifts {l} left by {r} bits", ">>=": "shifts {l} right by {r} bits"}


def _call_say(n: N, lvl: int) -> str:
    fn, args = n.a
    argv = _args_say(args, lvl)
    if fn.kind == "path":
        p = fn.a[0]
        key = re.sub(r"::<[^>]*>", "", p)
        if key.split("::")[-1] in ("swap", "replace", "take") and "mem" in key:
            argv = [say(a.a[1], lvl + 1) if a.kind == "un" and a.a[0] in ("&", "&mut") else say(a, lvl + 1) for a in args]
    slots = {f"a{i}": (argv[i] if i < len(argv) else "it") for i in range(3)}
    if fn.kind == "path":
        if key == "Rc::clone" or key == "Arc::clone":
            want("rc")
        if key in ("std::mem::size_of_val", "mem::size_of_val"):
            want("i32default")
        if key in _PATHCALL:
            return _PATHCALL[key].format(**slots)
        last = key.split("::")[-1]
        if last[:1].islower() and "::" not in key and _moved_note(args):
            return f"the result of calling {key} with {', '.join(argv)}" + _moved_note(args)
        if last[:1].isupper():
            return f"{art(key)} {key} holding {', '.join(argv)}" if argv else f"{art(key)} {key}"
        if "::" in key:
            return f"the result of calling {key}" + (f" with {', '.join(argv)}" if argv else "")
        return f"the result of calling {key}" + (f" with {', '.join(argv)}" if argv else "")
    return f"the result of calling {say(fn, lvl + 1)}" + (f" with {', '.join(argv)}" if argv else "")


# ── pieces: items, lets, control flow, arms, statements ─────

_BOUNDS = {
    "Display": "can be shown with `{}`", "Debug": "can be shown with `{:?}`", "Clone": "can be copied with `.clone()`", "Copy": "is copied instead of moved", "PartialOrd": "can be compared with `<` and `>`",
    "PartialEq": "can be compared with `==`", "Ord": "can be put in a full order", "Eq": "can be compared with `==` (and always equals itself)", "Default": "has a default value", "Add": "can be added with `+`",
    "Sub": "can be subtracted with `-`", "Mul": "can be multiplied with `*`", "Hash": "can be hashed (used as a map key)", "Iterator": "can be gone through one item at a time", "ToString": "can be turned into a String",
    "Sized": "has a size known at compile time", "Send": "is safe to send to another thread", "Sync": "is safe to share between threads", "From": "can be made from another type", "Into": "can be converted into another type",
    "AsRef": "can be borrowed as another type", "Fn": "is a function that may be called many times", "FnMut": "is a function that may change what it captured", "FnOnce": "is a function that can be called once",
}
_DERIVE = {
    "Debug": "Debug (so `{:?}` can show it)", "Clone": "Clone (so `.clone()` works)", "Copy": "Copy (assigning it copies instead of moving)", "PartialEq": "PartialEq (so `==` works)", "Eq": "Eq (equality that is always sensible)",
    "PartialOrd": "PartialOrd (so `<` and `>` work)", "Ord": "Ord (a full ordering, so it can be sorted)", "Hash": "Hash (so it can be a map key)", "Default": "Default (a ready-made default value)",
}


def _bound_phrase(b: tuple) -> str:
    if b[0] == "life":
        return f"lives at least as long as {b[1]}"
    name = b[1].split("::")[-1]
    return _BOUNDS.get(name, f"implements {b[1]}")


def _generics(ps: Parser) -> list:
    out = []
    ps.expect("<")
    while not ps.eof() and not (ps.at(">") or ps.at(">>") or ps.at(">=")):
        t = ps.take()
        if t.kind == "life":
            bounds = []
            if ps.at(":"):
                ps.i += 1
                while True:
                    bounds.append(ps.bound())
                    if ps.at("+"):
                        ps.i += 1
                    else:
                        break
            out.append((t.text, bounds, True))
        elif t.kind == "id":
            if t.text == "const":
                nm = ps.take().text
                ps.expect(":")
                ps.ty()
                out.append((nm, [], False))
            else:
                bounds = []
                if ps.at(":"):
                    ps.i += 1
                    while not ps.eof() and not ps.at(",") and not ps.at(">"):
                        bounds.append(ps.bound())
                        if ps.at("+"):
                            ps.i += 1
                        else:
                            break
                if ps.at("="):
                    ps.i += 1
                    ps.ty()
                out.append((t.text, bounds, False))
        else:
            raise Unreadable
        if ps.at(","):
            ps.i += 1
    ps.expect(">")
    return out


def _generics_phrase(gs: list) -> str:
    _GEN.update(n for n, _b, il in gs if not il)
    bits, life = [], False
    for name, bounds, is_life in gs:
        if is_life:
            life = True
            continue
        if bounds:
            bits.append(f"{name} stands for any type that " + " and ".join(_bound_phrase(b) for b in bounds[:3]))
        else:
            bits.append(f"{name} stands for any type")
    s = ""
    if bits:
        s += " It is generic: " + "; ".join(bits) + "."
    if life:
        names = ", ".join(n for n, _b, il in gs if il)
        s += f" `{names}` is a lifetime name: it ties the references that carry it together, so the compiler knows how long each one stays valid."
    return s


def _vis_note(vis: bool) -> str:
    return " It is `pub`, so code outside this module can use it." if vis else ""


def _strip_vis(toks: list) -> tuple[bool, list]:
    if toks and toks[0].text == "pub":
        i = 1
        if i < len(toks) and toks[i].text == "(":
            while i < len(toks) and toks[i].text != ")":
                i += 1
            i += 1
        return True, toks[i:]
    return False, toks


def _attr(toks: list) -> str:
    inner = [t.text for t in toks if t.text not in ("#", "!", "[", "]")]
    if inner and inner[0] == "derive":
        names = [x for x in inner[1:] if x not in ("(", ")", ",")]
        if names:
            return "asks the compiler to write the standard code for " + ", ".join(_DERIVE.get(n, n) for n in names[:6]) + " on the type below."
    if inner and inner[0] == "test":
        return "marks the function below as a test."
    return f"is an attribute: a note to the compiler about the item below (`{code(' '.join(inner), 50)}`)."


def _param(ps: Parser):
    i0 = ps.i
    if ps.at("&"):
        ps.i += 1
        if ps.peek() is not None and ps.peek().kind == "life":
            ps.i += 1
        mut = False
        if ps.at("mut"):
            ps.i += 1
            mut = True
        if ps.at("self"):
            ps.i += 1
            return ("self", "mutref" if mut else "ref")
        ps.i = i0
    if ps.at("self") or (ps.at("mut") and ps.at("self", 1)):
        if ps.at("mut"):
            ps.i += 1
        ps.i += 1
        if ps.at(":"):
            ps.i += 1
            ps.ty()
        return ("self", "own")
    pat = ps.pattern()
    ps.expect(":")
    return ("param", pat, ps.ty())


def _fn(p: Piece, t: list, vis: bool) -> str | None:
    i = 0
    unsafe = False
    while i < len(t) and t[i].text in ("const", "async", "unsafe", "extern", "default") or (i < len(t) and t[i].kind == "str"):
        unsafe = unsafe or t[i].text == "unsafe"
        i += 1
    if i >= len(t) or t[i].text != "fn" or i + 1 >= len(t):
        return None
    name = t[i + 1].text
    ps = Parser(t[i + 2 :], _CODE)
    gs = _generics(ps) if ps.at("<") else []
    ps.expect("(")
    params = []
    while not ps.eof() and not ps.at(")"):
        params.append(_param(ps))
        if ps.at(","):
            ps.i += 1
    ps.expect(")")
    ret = None
    if ps.at("->"):
        ps.i += 1
        ret = ps.ty()
    where = ""
    if ps.at("where"):
        where = code(ps.src(ps.i + 1, len(ps.t)), 60)
        ps.i = len(ps.t)
    if not ps.eof():
        return None
    # scopes: a new function starts fresh
    _SCOPES.clear()
    _OWNED.clear()
    names = []
    for pr in params:
        if pr[0] == "param":
            names.extend(pat_names(pr[1]))
            if pr[2][0] == "path" and pr[2][1].split("::")[-1] in ("String", "Vec", "Box", "HashMap", "HashSet"):
                _OWNED.update(pat_names(pr[1]))
    names.append("self") if any(pr[0] == "self" for pr in params) else None
    _SCOPES[p.sdepth + 1] = set(names)
    has_self = any(pr[0] == "self" for pr in params)
    in_impl = p.frame in ("impl", "trait")
    if name == "main" and p.frame == "file":
        kind = "main, the function where the program starts"
        head = f"defines {kind}"
    else:
        what = ("method" if has_self else "associated function") if in_impl else "function"
        head = f"defines the {what} {name}" + (f" (called as Type::{name}, with no `self`)" if in_impl and not has_self else "") if p.opens else (f"declares the {what} {name} with no body (a type that implements the trait supplies it)" if p.frame == "trait" else f"declares the {what} {name} (no body here)")
    ps_txt = []
    selfs = ""
    for pr in params:
        if pr[0] == "self":
            selfs = {"ref": " It borrows the value it is called on (`&self`): it can read it, and the value is still usable afterwards.",
                     "mutref": " It borrows the value it is called on so it can change it (`&mut self`); nothing else may use the value meanwhile.",
                     "own": " It takes ownership of the value it is called on (`self`): the caller cannot use that value afterwards."}[pr[1]]
            if pr[1] == "own":
                want("move")
            if pr[1] == "mutref":
                want("mutborrow")
            if pr[1] == "ref":
                want("borrow")
        else:
            ps_txt.append(f"{', '.join(pat_names(pr[1])) or 'a value'} ({ty_phrase(pr[2]).split(' (')[0]})")
    taking = "taking " + ", ".join(ps_txt) if ps_txt else "taking no arguments"
    giving = "" if ret is None or ret[0] == "unit" else f", giving back {ty_phrase(ret)}"
    if ret is None or ret[0] == "unit":
        giving = ", giving back nothing"
    out = f"{head}, {taking}{giving}." + selfs + _generics_phrase(gs)
    if where:
        out += f" Extra requirements: `{where}`."
    if unsafe:
        out += " It is `unsafe`: calling it is a promise that the caller has checked what the compiler cannot."
    if ret is not None and ret[0] == "path" and ret[1] in ("Result",) or (ret is not None and ret[0] == "path" and ret[1].startswith("Result")):
        out += " (A function that gives back a Result can use `?` inside.)"
    return out + _vis_note(vis)


def _struct(p: Piece, t: list, vis: bool) -> str | None:
    ps = Parser(t[1:], _CODE)
    name = ps.take().text
    gs = _generics(ps) if ps.at("<") else []
    if ps.at("("):
        ps.i += 1
        tys = []
        while not ps.eof() and not ps.at(")"):
            if ps.at("pub"):
                ps.i += 1
            tys.append(ty_phrase(ps.ty()).split(" (")[0])
            if ps.at(","):
                ps.i += 1
        ps.expect(")")
        out = f"defines the tuple struct {name}: a bundle of {len(tys)} unnamed field{'s' if len(tys) != 1 else ''} ({'; '.join(tys)}), reached as `.0`, `.1`..."
    elif p.opens:
        out = f"defines the struct {name}: a bundle of named fields, listed below."
    else:
        out = f"defines the struct {name}, which holds no data."
    return out + _generics_phrase(gs) + _vis_note(vis)


def _enum(p: Piece, t: list, vis: bool) -> str | None:
    ps = Parser(t[1:], _CODE)
    name = ps.take().text
    gs = _generics(ps) if ps.at("<") else []
    return f"defines the enum {name}: a value that is exactly one of the variants listed below." + _generics_phrase(gs) + _vis_note(vis)


def _trait(p: Piece, t: list, vis: bool) -> str | None:
    ps = Parser(t[1:], _CODE)
    name = ps.take().text
    gs = _generics(ps) if ps.at("<") else []
    sup = ""
    if ps.at(":"):
        ps.i += 1
        bs = []
        while not ps.eof():
            bs.append(_bound_phrase(ps.bound()))
            if ps.at("+"):
                ps.i += 1
            else:
                break
        sup = " Any type that implements it must also be one that " + " and ".join(bs) + "."
    return f"defines the trait {name}: a list of functions a type can promise to provide." + sup + _generics_phrase(gs) + _vis_note(vis)


def _impl(p: Piece, t: list, vis: bool) -> str | None:
    ps = Parser(t[1:], _CODE)
    gs = _generics(ps) if ps.at("<") else []
    if ps.at("!"):
        ps.i += 1
    first = ps.ty()
    if ps.at("for"):
        ps.i += 1
        second = ps.ty()
        out = f"says that {ty_src(second)} implements the trait {ty_src(first)}: the functions inside are the ones the trait asks for."
    else:
        out = f"starts the methods of {ty_src(first)}: the functions inside belong to it (called as `{ty_src(first).split('<')[0]}::name` or `value.name`)."
    if ps.at("where"):
        out += f" Extra requirements: `{code(ps.src(ps.i + 1, len(ps.t)), 60)}`."
    return out + _generics_phrase(gs)


def _use(p: Piece, t: list, vis: bool) -> str | None:
    texts = [x.text for x in t[1:]]
    if not texts:
        return None
    s = "".join(("::" if x == "::" else " as " if x == "as" else (", " if x == "," else x)) for x in texts)
    s = s.replace("::{", "::{").replace("{", "{").strip()
    if "*" in texts:
        return f"brings everything public from `{s.rsplit('::', 1)[0]}` into scope, so the names can be used without the path."
    if "{" in texts:
        head, _, tail = s.partition("::{")
        return f"brings {tail.rstrip('}')} (from {head}) into scope, so they can be written without the full path."
    if "as" in texts:
        path, _, alias = s.partition(" as ")
        return f"brings `{path}` into scope under the new name {alias}."
    last = texts[-1]
    if len(texts) == 1:
        return f"brings the crate or module {last} into scope."
    return f"brings {last} (from {'::'.join(x for x in texts[:-2] if x != '::')}) into scope, so it can be written without the full path."


def _const(p: Piece, t: list, vis: bool) -> str | None:
    kw = t[0].text
    i = 1
    mut = False
    if kw == "static" and t[i].text == "mut":
        mut = True
        i += 1
    ps = Parser(t[i:], _CODE)
    name = ps.take().text
    ty = None
    if ps.at(":"):
        ps.i += 1
        ty = ps.ty()
    val = None
    if ps.at("="):
        ps.i += 1
        val = ps.expr()
    if not ps.eof():
        return None
    what = "the constant" if kw == "const" else "the static variable"
    s = f"defines {what} {name}" if val is not None or kw != "const" else f"declares the constant {name} (each type that implements the trait supplies the value)"
    if ty:
        s += f", {ty_phrase(ty)}"
    if val is not None:
        s += f", set to {say(val)}"
    if kw == "const" and val is None:
        pass
    elif kw == "const":
        s += ". A constant can never change and is worked out while compiling"
    elif mut:
        s += ". It is `static mut`: one place in memory for the whole program that can change, so touching it needs `unsafe`"
    else:
        s += ". It lives for the whole program, in one fixed place in memory"
    return s + "." + _vis_note(vis)


def _type_alias(p: Piece, t: list, vis: bool) -> str | None:
    ps = Parser(t[1:], _CODE)
    name = ps.take().text
    if ps.at("<"):
        _generics(ps)
    if not ps.at("="):
        return f"declares the associated type {name}: each type that implements the trait picks its own."
    ps.i += 1
    ty = ps.ty()
    if not ps.eof():
        return None
    extra = " (inside an `impl` this fills in the type the trait asked for)" if p.frame == "impl" else ""
    return f"gives the type {ty_src(ty)} the extra name {name}{extra}."


def _mod(p: Piece, t: list, vis: bool) -> str | None:
    if t[0].text == "macro_rules":
        return f"defines the macro {t[2].text if len(t) > 2 else '?'}: a rule that writes code for you wherever it is called with a name ending in `!`."
    name = t[1].text if len(t) > 1 else "?"
    return f"defines the module {name}: a named group of items. Names inside are private unless they are `pub`." + _vis_note(vis)


def _field(t: list, vis: bool) -> str | None:
    ps = Parser(t, _CODE)
    name = ps.take().text
    ps.expect(":")
    ty = ps.ty()
    if not ps.eof():
        return None
    return f"has a field {name}: {ty_phrase(ty)}." + (" It is `pub`, so code outside the module can read it." if vis else "")


def _variant(t: list) -> str | None:
    if not t or t[0].kind != "id":
        return None
    name = t[0].text
    ps = Parser(t[1:], _CODE)
    if ps.eof():
        return f"is the variant {name}, which carries no data."
    if ps.at("("):
        ps.i += 1
        tys = []
        while not ps.eof() and not ps.at(")"):
            tys.append(ty_phrase(ps.ty()))
            if ps.at(","):
                ps.i += 1
        ps.expect(")")
        return f"is the variant {name}, which carries {'; '.join(tys)}."
    if ps.at("{"):
        ps.i += 1
        fs = []
        while not ps.eof() and not ps.at("}"):
            fn = ps.take().text
            ps.expect(":")
            fs.append(f"{fn} ({ty_phrase(ps.ty())})")
            if ps.at(","):
                ps.i += 1
        ps.expect("}")
        return f"is the variant {name}, which carries the named fields {', '.join(fs)}."
    if ps.at("="):
        ps.i += 1
        return f"is the variant {name}, numbered {say(ps.expr())}."
    return None


def _declare(names: list, depth: int) -> None:
    _SCOPES.setdefault(depth, set()).update(names)


def _shadows(name: str, depth: int) -> bool:
    return any(name in s for d, s in _SCOPES.items() if d <= depth)


def _let(p: Piece, t: list) -> str | None:
    ps = Parser(t[1:], _CODE)
    pat = ps.pattern()
    ty = init = None
    els = False
    if ps.at(":"):
        ps.i += 1
        ty = ps.ty()
    if ps.at("="):
        ps.i += 1
        init = ps.expr() if not ps.eof() else N("blockhead" if p.opens else "later", ("block",), "{")
    if ps.at("else"):
        ps.i += 1
        els = True
    if not ps.eof():
        return None
    names = pat_names(pat)
    sd = p.sdepth
    s = ""
    tail = ""
    moved = ""
    if pat[0] == "bind" and init is not None and init.kind == "path" and init.a[0] in _OWNED:
        moved = f" (this MOVES {init.a[0]} into {pat[1]}: {init.a[0]} cannot be used again afterwards)"
        want("move")
    if pat[0] == "bind" and _owned_expr(init):
        _OWNED.add(pat[1])
    if pat[0] == "bind" and pat[3] is None:
        name, mut = pat[1], pat[2]
        if _shadows(name, sd):
            s = f"creates a new {name} that shadows the earlier {name}"
            if not want("shadow"):
                tail = f" From here on, `{name}` means the new one; the old one is hidden, not changed."
        else:
            s = f"creates {name}"
        if mut:
            s += " (changeable: it has `mut`)"
        elif init is not None:
            s += " (fixed: no `mut`)"
        if name.startswith("_") and len(name) > 1:
            s += " (the leading underscore says it is unused on purpose)"
        if ty is not None:
            s += f", {ty_phrase(ty)}"
        if init is not None:
            s += f", set to {say(init)}{moved}"
        else:
            s += ", with no value yet (it must get one before it is used)"
    elif pat[0] == "wild":
        s = f"works out {say(init)} and throws the result away" if init is not None else "does nothing"
    else:
        shadow = [n for n in names if _shadows(n, sd)]
        s = f"unpacks {say(init) if init is not None else 'a value'} into {', '.join(names) or 'nothing'}"
        if len(names) > 1 and pat[0] == "tuple":
            s += ": the first name gets the first part, the second name the second part, and so on"
        elif pat[0] == "struct":
            s += ": each name gets the field of the same name"
        elif pat[0] == "tstruct":
            s += f" (this only works if it really is a {pat[1]})"
        if shadow:
            s += f". {', '.join(shadow)} shadow{'s' if len(shadow) == 1 else ''} the earlier name{'s' if len(shadow) != 1 else ''} of the same spelling"
            want("shadow")
        if ty is not None:
            s += f". The type is {ty_phrase(ty)}"
    if els:
        s = f"tries to unpack {say(init)} as {pat_say(pat, 1)}: if it fits, {', '.join(names) or 'the names'} can be used below; if not, the `else` block runs, and it must leave (return, break, panic...)"
        _declare(names, sd)
        return s + "."
    _declare(names, sd)
    return s + "." + tail


def _cond_phrase(e: N | None) -> str | None:
    if e is None:
        return None
    if e.kind == "letcond":
        return f"{say(e.a[1])} fits the pattern {pat_say(e.a[0], 1)}"
    return say(e)


def _expr_of(t: list) -> N | None:
    return parse_expr(t, _CODE)


def _for(p: Piece, t: list) -> str | None:
    ps = Parser(t[1:], _CODE)
    pat = ps.pattern()
    ps.expect("in")
    e = ps.expr()
    if not ps.eof():
        return None
    names = pat_names(pat)
    _declare(names, p.sdepth + 1)
    nm = ", ".join(names) or "the item"
    inner = e
    while inner.kind == "paren":
        inner = inner.a[0]
    if inner.kind == "range":
        lo, hi, incl = inner.a
        want("rangeex")
        if lo is not None and hi is not None:
            return f"repeats once for each number from {say(lo, 1)} up to {'and including ' if incl else 'but not including '}{say(hi, 1)}, calling the current one {nm}."
    if inner.kind == "un" and inner.a[0] in ("&", "&mut"):
        want("formove")
        return f"repeats once for each item of {say(inner.a[1], 1)}, {'borrowing them' if inner.a[0] == '&' else 'borrowing them so each can be changed'} (it is still usable afterwards). The current item is called {nm}."
    base, steps = _flatten(inner)
    if steps and steps[-1][0] == "m" and steps[-1][1].a[1] == "enumerate" and pat[0] == "tuple" and len(names) == 2:
        only_iter = len(steps) == 2 and steps[0][0] == "m" and steps[0][1].a[1] in ("iter", "into_iter", "iter_mut")
        src = say(_rebuild(steps[:-1], base), 1) if len(steps) > 1 and not only_iter else say(base, 1)
        return f"repeats once for each item of {src}, with its position: {names[0]} is the position (counting from 0) and {names[1]} is the item."
    if inner.kind == "path":
        want("formove")
        return f"repeats once for each item of {inner.a[0]}, taking the items out of it (a Vec cannot be used again afterwards). The current item is called {nm}."
    return f"repeats once for each item of {say(e, 1)}, calling the current one {nm}."


def _rebuild(steps: list, base: N) -> N:
    cur = base
    for kind, node in steps:
        if kind == "m":
            cur = N("mcall", (cur, node.a[1], node.a[2], node.a[3]), "")
        elif kind == "try":
            cur = N("try", (cur,), "")
        elif kind == "field":
            cur = N("field", (cur, node.a[1]), "")
        else:
            cur = N("await", (cur,), "")
    return cur


def _control(p: Piece, t: list) -> str | None:
    w = t[0].text
    if w == "else":
        rest = t[1:]
        if not rest:
            return "otherwise, does what follows."
        if rest[0].text == "if":
            inner = _control(p, rest)
            return "otherwise, " + inner if inner else None
        return None
    if w == "if":
        e = _expr_of(t[1:])
        c = _cond_phrase(e)
        if c is None:
            return None
        extra = ""
        if e is not None and e.kind == "letcond":
            names = pat_names(e.a[0])
            _declare(names, p.sdepth + 1)
            extra = f" The name{'s' if len(names) != 1 else ''} {', '.join(names)} can be used inside." if names else ""
        return f"if {c}, does what follows.{extra}"
    if w == "while":
        e = _expr_of(t[1:])
        if e is None:
            return None
        if e.kind == "letcond":
            names = pat_names(e.a[0])
            _declare(names, p.sdepth + 1)
            return f"keeps repeating as long as {say(e.a[1])} fits the pattern {pat_say(e.a[0], 1)}, using the names {', '.join(names) or 'none'}, and stops the first time it does not."
        return f"keeps repeating while {say(e)}."
    if w == "loop":
        return "repeats forever, until something inside leaves with `break` (or `return`)." if len(t) == 1 else None
    if w == "for":
        return _for(p, t)
    if w == "match":
        e = _expr_of(t[1:])
        if e is None:
            return None
        want("exhaustive")
        return f"compares {say(e)} against the arms below, top to bottom, and runs the first one that fits."
    if w == "unsafe" and len(t) == 1:
        want("unsafe")
        return "starts an unsafe block."
    if w == "async" and len(t) <= 2:
        return "starts an async block."
    return None


def _arm(p: Piece, t: list) -> str | None:
    depth = 0
    idx = -1
    for k, x in enumerate(t):
        if x.kind == "op":
            if x.text in "([{":
                depth += 1
            elif x.text in ")]}":
                depth -= 1
            elif x.text == "=>" and depth == 0:
                idx = k
                break
    if idx < 1:
        return None
    ps = Parser(t[:idx], _CODE)
    pat = ps.pattern()
    guard = None
    if ps.at("if"):
        ps.i += 1
        guard = ps.expr()
    if not ps.eof():
        return None
    if pat[0] == "wild" and guard is None:
        head = "in every other case (`_` matches anything that is left)"
    elif pat[0] == "bind" and pat[3] is None and guard is None:
        head = f"for any value, calling it {pat[1]}"
    else:
        head = f"when it is {pat_say(pat, 1)}"
        if pat[0] == "bind" and pat[3] is None:
            head = f"for any value, calling it {pat[1]}"
    if guard is not None:
        head += f", but only if {say(guard)}"
    body_toks = t[idx + 1 :]
    names = pat_names(pat)
    _declare(names, p.sdepth + 1)
    if not body_toks:
        return head + ", runs the block below."
    e = _expr_of(body_toks)
    if e is None:
        return None
    return head + ": " + _arm_body(e, p.value)


def _is_action(e: N) -> bool:
    k = e.kind
    if k in ("asg", "return", "break", "continue"):
        return True
    if k == "macro":
        return e.a[0] in _FMT_MACROS - {"format"} or e.a[0] in ("dbg",)
    if k == "mcall":
        return e.a[1] in _MUT_STMT or e.a[1] in ("for_each",)
    if k == "call" and e.a[0].kind == "path":
        return e.a[0].a[0] in ("drop", "std::mem::swap", "mem::swap", "std::process::exit")
    return False


def _arm_body(e: N, value: bool) -> str:
    if _is_action(e) or (not value and e.kind in ("call", "mcall") and e.kind != "path"):
        return _stmt_text(e, False)
    if e.kind in ("ifhead", "matchhead", "blockhead", "iflet"):
        return "gives " + say(e) + "."
    return "gives " + say(e) + "."


def _tail_text(what: str) -> str:
    if want("tail"):
        return f"gives {what} as the value of this block (the last expression, with no `;`)."
    return f"gives {what} as the value of this block (no `;`)."


def _stmt_text(e: N, tail: bool) -> str:
    k = e.kind
    if k == "asg":
        op, l, r = e.a
        left, right = say(l, 1), say(r, 1)
        if l.kind == "un" and l.a[0] == "*":
            want("deref")
        if op == "=":
            if l.kind == "idx":
                return f"stores {right} at position {say(l.a[1], 1)} of {say(l.a[0], 1)}."
            if l.kind == "un" and l.a[0] == "*":
                return f"stores {right} where {say(l.a[1], 1)} points."
            if l.kind == "field":
                return f"sets {left} to {right}."
            want("immut")
            return f"sets {left} to {right} (replacing what it held; {left} must have been made with `mut`)."
        if op == "/=" and not _is_float(r):
            want("div")
        if op == "%=":
            want("rem")
        return _ASG_WORD[op].format(l=left, r=right) + "."
    if k == "macro":
        s = _macro_say(e, 0, True)
        return (s or "does a macro call") + "."
    if k == "return":
        v = e.a[0]
        return f"leaves this function now, giving back {say(v, 1)}." if v is not None else "leaves this function now, giving back nothing."
    if k == "break":
        label, v = e.a
        if label:
            want("labeled")
        if v is not None:
            want("loopvalue")
        return "leaves " + (f"the loop labeled {label}" if label else "the loop") + (f", and the loop's value is {say(v, 1)}" if v is not None else "") + " right here."
    if k == "continue":
        label = e.a[0]
        return ("skips the rest of this round of the loop labeled " + label + " and starts its next round." if label else "skips the rest of this round of the loop and starts the next.")
    if k in ("mcall", "try", "await"):
        base, steps = _flatten(e)
        if len(steps) == 1 and steps[0][0] == "m":
            phrase = _chain_say(e, 0)
            name = steps[0][1].a[1]
            if name in _MUT_STMT or name in ("for_each", "clear", "push", "set", "drop"):
                return C.capital(phrase) + "."
            if phrase.startswith("the result of calling "):
                return ("Calls " + phrase[len("the result of calling ") :] + ".") if not tail else _tail_text(phrase)
            return f"works out {phrase} (and does nothing with the answer)." if not tail else _tail_text(phrase)
        text = _chain_say(e, 0, statement=not tail)
        if tail:
            return _tail_text(text)
        return C.capital(text) + "."
    if k == "call":
        phrase = say(e)
        if phrase.startswith("the result of calling "):
            phrase = "calls " + phrase[len("the result of calling ") :]
            return (C.capital(phrase) + ".") if not tail else _tail_text(say(e))
        if tail:
            return _tail_text(phrase)
        return C.capital(phrase) + "."
    if k in ("ifhead", "matchhead", "blockhead", "iflet"):
        return "gives " + say(e) + "."
    if tail:
        return _tail_text(say(e))
    if k == "path":
        return f"just names {e.a[0]} (nothing happens)."
    return f"works out {say(e)} (and does nothing with the answer)."


def _stmt(p: Piece, t: list) -> str | None:
    e = _expr_of(t)
    if e is None:
        return None
    tail = p.tail and not _is_action(e)
    return _stmt_text(e, tail)


def _cont(p: Piece, t: list) -> str | None:
    if t[0].text == ".":
        e = parse_expr([T("id", "_", 0, 0)] + list(t), _CODE.replace("", "")) if False else None
        try:
            ps = Parser([T("id", "_", t[0].start, t[0].start)] + list(t), _CODE)
            e = ps.expr()
            if not ps.eof():
                return None
        except (Unreadable, RecursionError):
            return None
        base, steps = _flatten(e)
        parts = []
        for kind, node in steps:
            if kind == "m":
                parts.append(_method_texts(node, "it", 0, True))
            elif kind == "try":
                parts.append("applying `?` (an Err or None makes this function stop and return it)")
                want("qmark")
            elif kind == "field":
                parts.append(f"taking its field {node.a[1]}")
        names = [s[1].a[1] for s in steps if s[0] == "m"]
        if names and names[-1] in _LAZY:
            want("lazy")
        return "carries on the chain above: " + ", then ".join(parts) + "."
    return f"carries on the expression above with `{code(' '.join(x.text for x in t), 50)}`."


def _arg(p: Piece, t: list) -> str | None:
    if len(t) >= 3 and t[0].kind in ("id", "num") and t[1].text == ":" and t[1].kind == "op":
        e = _expr_of(t[2:])
        if e is not None:
            return f"sets the field {t[0].text} to {say(e)}."
        try:
            ps = Parser(t[2:], _CODE)
            ty = ps.ty()
            if ps.eof():
                return f"is {t[0].text}, {ty_phrase(ty)}."
        except (Unreadable, RecursionError):
            pass
        return None
    e = _expr_of(t)
    if e is None:
        return None
    return f"is one of the items or arguments: {say(e)}."


def _describe(p: Piece, toks: list) -> str | None:
    vis, t = _strip_vis(toks)
    if not t:
        return None
    if any(x.text == "$" for x in t) or p.fname.startswith("macro_rules"):
        return f"is part of a macro rule: `{code(' '.join(x.text for x in t), 50)}` (`$x:expr` names a piece of code the caller passes in)."
    if p.mode == "cont" or t[0].text == ".":
        return _cont(p, t)
    if p.mode == "arg" and t[0].text in CONTROL and t[0].kind == "id":
        return _control(p, t)
    if p.mode == "arg":
        return _arg(p, t)
    if p.frame == "match" and any(x.kind == "op" and x.text == "=>" for x in t):
        return _arm(p, t)
    if p.frame == "struct":
        return _field(t, vis)
    if p.frame == "enum":
        return _variant(t)
    label = ""
    if t[0].kind == "life" and len(t) > 2 and t[1].text == ":":
        label = t[0].text
        t = t[2:]
    i = 0
    while i < len(t) - 1 and t[i].text in ("const", "async", "unsafe", "extern", "default") and (t[i + 1].text in ("fn", "impl", "trait", "unsafe") or t[i + 1].kind == "str"):
        i += 1
    w = t[i].text if t[i].kind == "id" else ""
    q = t[i:]
    if w == "fn":
        return _fn(p, t, vis)
    if w == "let":
        return _let(p, q)
    if w in ("struct", "union"):
        return _struct(p, q, vis)
    if w == "enum":
        return _enum(p, q, vis)
    if w == "trait":
        return _trait(p, q, vis)
    if w == "impl":
        return _impl(p, q, vis)
    if w == "use":
        return _use(p, q, vis)
    if w in ("const", "static") and len(q) > 1 and q[1].text != "fn":
        return _const(p, q, vis)
    if w == "type":
        return _type_alias(p, q, vis)
    if w in ("mod", "macro_rules"):
        return _mod(p, q, vis)
    if w in ("if", "else", "while", "loop", "for", "match", "unsafe", "async") and not (len(q) > 1 and q[1].text in ("=", ".", "?")):
        out = _control(p, q)
        if out is not None and label:
            want("labeled")
            out += f" It is labeled {label}, so `break {label}` or `continue {label}` can aim at this loop from inside an inner one."
        return out
    return _stmt(p, t)


def describe_piece(p: Piece) -> str | None:
    toks = p.toks
    if not toks or len(toks) > 800:
        return None
    _PEND.clear()
    for d in [d for d in _SCOPES if d > p.sdepth + (1 if p.mode == "arg" else 0)]:
        del _SCOPES[d]
    lead = ""
    if toks[0].text == "#" and len(toks) > 1 and toks[0].kind == "op":
        j = _skip_attr(toks, 0)
        lead = _attr(toks[:j])
        toks = toks[j:]
        if not toks:
            return C.capital(lead)
    try:
        body = _describe(p, toks)
    except (Unreadable, RecursionError, IndexError, KeyError, ValueError):
        body = None
    if body is None:
        return None
    text = (C.capital(lead) + " " + C.capital(body)) if lead else body
    if _PEND:
        shown = _PEND[:2]
        _SEEN.update(k for k, _t in shown)
        text = text.rstrip() + " " + " ".join(t for _k, t in shown)
    return text


# ── rows ────────────────────────────────────────────────────

def _read_rows(code_text: str) -> tuple[list[dict], int, list[str]]:
    global _CODE
    _CODE = code_text
    infos = read_pieces(code_text)
    _SEEN.clear()
    _SCOPES.clear()
    _GEN.clear()
    _OWNED.clear()
    rows: list[dict] = []
    bad: list[int] = []
    for info in infos:
        if info.structural or not info.pieces:
            continue
        texts: list[str] = []
        failed = False
        for piece in info.pieces:
            try:
                t = describe_piece(piece)
            except Exception:
                t = None
            if t is None:
                failed = True
            else:
                texts.append(t)
        if failed and not texts:
            text = C.FALLBACK
            bad.append(info.line)
        elif failed:
            text = C.sentence(texts) + " " + C.FALLBACK
            bad.append(info.line)
        else:
            text = C.sentence(texts)
        rows.append({"line": info.line, "depth": info.depth, "source": info.raw.strip(), "text": text})
    return rows, len(rows), [str(n) for n in bad]


# ── running it ──────────────────────────────────────────────

_DIAG = re.compile(r"^(error(?:\[E\d+\])?: .*)\n\s*--> [^\n]*?snippet\.rs:(\d+):\d+", re.M)
_PANIC = re.compile(r"panicked at [^\n]*?snippet\.rs:(\d+):\d+:?\s*\n?(.*?)(?:\nnote:|\Z)", re.S)


def _rust_notes(program, timeout: float = 3.0) -> tuple[list[str], str | None]:
    from code_coach.gotchas.runner import run_program

    try:
        result = run_program("rust", program.text, timeout=timeout)
    except Exception as exc:  # no toolchain, a temp folder that failed...
        return [f"It was not run here ({str(exc).strip() or 'no Rust compiler found'}), so there is no output to show."], None
    err = result.stderr.replace("\r\n", "\n")

    def line_of(n: int) -> str:
        k = n - program.offset
        return f"line {k}" if k >= 1 else "the wrapper"

    if result.compile_error:
        m = _DIAG.search(err)
        if m:
            return [], f"It does not compile: {line_of(int(m.group(2)))}: {m.group(1).strip()}"
        first = next((ln.strip() for ln in err.split("\n") if "error" in ln), "") or "the compiler gave no reason"
        return [], "It does not compile: " + re.sub(r"snippet\.rs:\d+:\d+", "", first).strip()
    notes = C.printed_notes(result.stdout)
    if result.timed_out:
        notes.append(f"It was still running after {timeout:g} seconds, so it was stopped (an endless loop?).")
        return notes, None
    if not result.ok:
        m = _PANIC.search(err)
        if m:
            msg = m.group(2).strip().split("\n")[0]
            return notes, f"It stopped with an error: {msg} ({line_of(int(m.group(1)))}). A panic stops the program at once."
        first = next((ln.strip() for ln in err.split("\n") if ln.strip()), "")
        return notes, f"It stopped with an error (exit code {result.returncode})" + (f": {first}" if first else ".")
    return notes, None


def explain_rust(code_text: str, run: bool = True, context: str = "") -> dict:
    """Walk Rust line by line, and (when `run`) say what running it printed."""
    if not code_text.strip():
        return C.empty()
    try:
        rows, _n, _bad = _read_rows(code_text)
    except Exception:
        rows = []
    funcs = [m for m in re.findall(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:const\s+|async\s+|unsafe\s+)*fn\s+(\w+)", code_text, re.M) if m != "main"][:8]
    summary = f"This defines {C.join_names(funcs)}. Here's what each line does:" if funcs else "Here's what each line does:"
    notes: list[str] = []
    error_note = None
    if run:
        prog = rust_program(code_text)
        notes, error_note = _rust_notes(prog)
    return C.finish(summary, rows, notes, error_note)
