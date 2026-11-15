"""What the Dart, C and SQL explainers share: reading code a piece at a time, and saying what running it printed.

A "piece" is one statement, one header, or one argument that starts on a physical line. Splitting code into pieces
needs to know where it is nested (is this line inside `Column(children: [`, or inside a `{` block?), so `read_pieces`
walks the tokens once with a stack of open brackets and hands each language's describer the pieces in order, with the
mode they were found in. Every explainer returns the same dict as `explain_js`:
`{ok, summary, lines: [{line, depth, source, text}], output_notes, error_note}`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from .explain_expr import Tok, tokenize

#: Shown for a line no rule covers. Tests count these.
FALLBACK = "A line this reader does not break down yet."


@dataclass
class Frame:
    kind: str  # paren brack lit block class switch swexpr
    name: str = ""
    ckind: str = ""  # class | enum | struct | union | mixin | extension


@dataclass
class Piece:
    line: int
    text: str  # the source of the piece (closing brackets still to come are not included)
    toks: list[Tok]
    mode: str  # stmt (a statement or header) | arg (an argument or element inside brackets) | cont (continues a statement)
    frame: str  # the block this piece sits in: file block class switch swexpr
    class_name: str = ""
    class_kind: str = ""
    opens_block: bool = False  # a header: its `{` follows
    lambda_block: bool = False  # the `{` is the body of a lambda inside a call: `setState(() {`
    closers: str = ""  # what auto-closes the piece's own open brackets
    depth: int = 0
    first_on_line: bool = True

    @property
    def closed_text(self) -> str:
        """The piece with its open brackets closed (and an empty body where a `{` follows), so it can be parsed."""
        body = self.text
        if self.lambda_block:
            body += " {}"
        return body + self.closers


@dataclass
class LineInfo:
    line: int
    raw: str
    depth: int
    pieces: list[Piece] = field(default_factory=list)
    structural: bool = False  # nothing but closing brackets / a comment / blank
    extra: str = ""


_CLOSE = {"(": ")", "[": "]", "{": "}"}
_LITERAL_PREV = {"=", ",", "(", "[", ":", "=>", "return", "?", "??", "??=", "+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>=", "..", "{", "+", "-", "&&", "||", "!", "await", "yield", "throw"}


def _line_starts(code: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(code):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def _line_of(starts: list[int], pos: int) -> int:
    lo, hi = 0, len(starts) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if starts[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo + 1


def _unclosed(toks: list[Tok]) -> str:
    stack: list[str] = []
    for t in toks:
        if t.kind == "str":
            continue
        if t.text in _CLOSE:
            stack.append(t.text)
        elif t.text in (")", "]", "}") and stack:
            stack.pop()
    return "".join(_CLOSE[o] for o in reversed(stack))


def read_pieces(code: str, dart: bool) -> list[LineInfo]:
    """Every physical line with the pieces that start on it. Never raises."""
    # preprocessor lines (#include, #define ...) are one piece each and are not tokenised
    raw_lines = code.split("\n")
    pp_lines: set[int] = set()
    masked_chars = list(code)
    starts = _line_starts(code)
    if not dart:
        i = 0
        while i < len(raw_lines):
            if raw_lines[i].lstrip().startswith("#"):
                j = i
                while raw_lines[j].rstrip().endswith("\\") and j + 1 < len(raw_lines):
                    j += 1
                for k in range(i, j + 1):
                    pp_lines.add(k + 1)
                    for p in range(starts[k], starts[k] + len(raw_lines[k])):
                        masked_chars[p] = " "
                i = j + 1
            else:
                i += 1
    toks = tokenize("".join(masked_chars), dart)
    infos = [LineInfo(n + 1, raw_lines[n], 0) for n in range(len(raw_lines))]
    by_line: dict[int, list[Tok]] = {}
    for t in toks:
        by_line.setdefault(_line_of(starts, t.start), []).append(t)

    stack: list[Frame] = []
    prev_tok: Tok | None = None
    stmt_open = False  # the previous statement did not end (no `;`, `{` or `}` yet) at block level

    def top() -> Frame | None:
        return stack[-1] if stack else None

    def block_frame() -> tuple[str, str, str]:
        for f in reversed(stack):
            if f.kind in ("block", "class", "switch", "swexpr"):
                return f.kind, f.name, f.ckind
        return "file", "", ""

    def in_arg_mode() -> bool:
        t = top()
        return t is not None and t.kind in ("paren", "brack", "lit")

    for n, info in enumerate(infos, start=1):
        if n in pp_lines:
            info.pieces.append(Piece(n, raw_lines[n - 1].strip(), [], "pp", "file"))
            continue
        ltoks = by_line.get(n, [])
        if not ltoks:
            info.structural = True
            continue
        # leading closers
        idx = 0
        while idx < len(ltoks) and ltoks[idx].kind != "str" and ltoks[idx].text in (")", "]", "}"):
            if stack:
                stack.pop()
            idx += 1
        rest = ltoks[idx:]
        info.depth = min(len(stack), 10)
        if not rest or all(t.text in (";", ",") and t.kind != "str" for t in rest):
            info.structural = True
            prev_tok = ltoks[-1]
            if any(t.text == ";" for t in rest):
                stmt_open = False
            continue
        cur: list[Tok] = []
        local = 0
        mode = "arg" if in_arg_mode() else "stmt"
        if mode == "stmt" and stmt_open and not (top() is not None and top().kind in ("swexpr", "switch")) and rest[0].text in (".", "?.", "..", "?..", "+", "-", "*", "/", "&&", "||", "?", ":", "=>", "??", "==", "!=", "<", ">", "<=", ">=", "%", "=", "|", "&", "^"):
            mode = "cont"
        piece_start_mode = mode
        first = True

        def emit(opens: bool = False, lam: bool = False) -> None:
            nonlocal cur, first, piece_start_mode
            if not cur:
                return
            fk, fname, fck = block_frame()
            text = code[cur[0].start : cur[-1].end]
            info.pieces.append(Piece(n, text, cur, piece_start_mode, fk, fname, fck, opens, lam, _unclosed(cur), info.depth, first))
            first = False
            cur = []

        for k, t in enumerate(rest):
            s = t.text if t.kind != "str" else "\0str"
            prev = rest[k - 1] if k else prev_tok
            if s in ("(", "["):
                stack.append(Frame("paren" if s == "(" else "brack"))
                cur.append(t)
                local += 1
            elif s == "{":
                pv = prev.text if prev is not None and prev.kind != "str" else ""
                head = cur[0].text if cur else ""
                pk = prev.kind if prev is not None else ""
                pv2 = rest[k - 2].text if k >= 2 else (prev_tok.text if k == 1 and prev_tok is not None else "")
                literal = (pv in _LITERAL_PREV or (pk == "op" and pv not in (">", ">>", "++", "--"))) and not (head in ("case", "default") and local == 0)
                if pv == "*" and pv2 in ("async", "sync"):
                    literal = False
                elif pv in (">", ">>") and not literal:
                    # `<String, int>{...}` is a typed literal; `State<A> {` is a class body
                    depth_a, j = 0, len(cur) - 1
                    while j >= 0:
                        tx = cur[j].text if cur[j].kind != "str" else ""
                        depth_a += (tx == ">") + 2 * (tx == ">>") - (tx == "<")
                        if depth_a <= 0:
                            break
                        j -= 1
                    before = cur[j - 1] if j >= 1 else None
                    if j >= 0 and (before is None and (prev_tok is not None and (prev_tok.text in _LITERAL_PREV or prev_tok.kind == "op")) or (before is not None and (before.text in _LITERAL_PREV or before.kind == "op" or before.text in ("const", "final", "return")))):
                        literal = True
                    elif j == 0 and not cur[:j]:
                        literal = True
                if local > 0 and pv not in (")", "async", "*") and not literal:
                    literal = True
                if not dart and pv == ")" and not literal:
                    # `(struct P){...}` and `(int[]){...}` are compound literals, not blocks
                    depth_p, j = 0, len(cur) - 1
                    while j >= 0:
                        tx = cur[j].text if cur[j].kind != "str" else ""
                        depth_p += (tx == ")") - (tx == "(")
                        if depth_p <= 0:
                            break
                        j -= 1
                    inside = cur[j + 1 : -1] if j >= 0 else []
                    before = cur[j - 1] if j >= 1 else None
                    typeish = bool(inside) and inside[0].kind == "id" and (inside[0].text in ("struct", "union", "enum", "int", "char", "unsigned", "long", "short", "double", "float", "const", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t", "size_t") or inside[0].text.endswith("_t") or inside[0].text[:1].isupper())
                    if j >= 0 and typeish and (before is None and False or (before is not None and (before.text in _LITERAL_PREV or before.kind == "op" or before.text == "return"))):
                        literal = True
                if literal:
                    stack.append(Frame("lit"))
                    cur.append(t)
                    local += 1
                else:
                    kind, name, ckind = "block", "", ""
                    ctext = [x.text for x in cur if x.kind != "str"]
                    if "class" in ctext[:4] or "mixin" in ctext[:3] or "extension" in ctext[:2] or "enum" in ctext[:3] or "struct" in ctext[:2] or "union" in ctext[:2]:
                        kind = "class"
                        ckind = next((w for w in ctext if w in ("class", "enum", "struct", "union", "mixin", "extension")), "class")
                        for j, w in enumerate(ctext):
                            if w in ("class", "mixin", "enum", "extension", "struct", "union") and j + 1 < len(ctext) and re.match(r"[A-Za-z_]", ctext[j + 1]):
                                name = ctext[j + 1]
                                if ctext[j + 1] in ("class", "on", "type") and j + 2 < len(ctext):
                                    name = ctext[j + 2]
                                break
                    elif ctext[:1] == ["switch"]:
                        kind = "switch"
                    elif "switch" in ctext and ctext[0] != "switch" and ctext[-1:] == [")"] and ctext[len(ctext) - 1 - ctext[::-1].index("switch") + 1 : len(ctext) - 1 - ctext[::-1].index("switch") + 2] == ["("]:
                        kind = "swexpr"
                    emit(opens=local == 0 and not in_arg_mode(), lam=local > 0 or in_arg_mode())
                    stack.append(Frame(kind, name, ckind))
                    local = 0
                    mode = "stmt"
                    piece_start_mode = "stmt"
                    first = False if info.pieces else True
            elif s in (")", "]", "}"):
                if local > 0:
                    local -= 1
                    if stack:
                        stack.pop()
                    cur.append(t)
                else:
                    emit()
                    if stack:
                        stack.pop()
                    piece_start_mode = "arg" if in_arg_mode() else "stmt"
            elif s == ";" and local == 0:
                emit()
                piece_start_mode = "arg" if in_arg_mode() else "stmt"
                stmt_open = False
            elif s == "," and local == 0 and (in_arg_mode() or (top() is not None and top().kind == "swexpr")):
                emit()
                piece_start_mode = "arg" if in_arg_mode() else "stmt"
            else:
                cur.append(t)
            if s in ("{", "}", ";") and local == 0:
                stmt_open = False
        emit()
        last = rest[-1]
        prev_tok = last
        if last.kind != "str" and last.text in ("{", "}", ";"):
            stmt_open = False
        elif not in_arg_mode():
            stmt_open = True
        # a piece that ends here but whose brackets stay open is closed for parsing by `closers`
    return infos


def depth_note(info: LineInfo) -> int:
    return info.depth


# ── Running it ──────────────────────────────────────────────

_PATH = re.compile(r"(?:[A-Za-z]:)?[^\s\"'(]*?[\\/](snippet\.\w+)")


def first_lines(text: str, limit: int = 6) -> list[str]:
    lines = [ln for ln in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def printed_notes(stdout: str, limit: int = 6) -> list[str]:
    lines = first_lines(stdout)
    notes = [f"It printed: {ln}" if ln.strip() else "It printed a blank line." for ln in lines[:limit]]
    if len(lines) > limit:
        notes.append(f"...and {len(lines) - limit} more line{'s' if len(lines) - limit != 1 else ''}.")
    return notes


def shift_line_numbers(message: str, offset: int, name: str) -> str:
    """`snippet.dart:7:3: Error: ...` becomes `line 4: Error: ...` once the lines the wrapper added are taken off."""

    def fix(m: re.Match) -> str:
        n = int(m.group(1)) - offset
        return f"line {n}:" if n >= 1 else "the wrapper:"

    out = re.sub(rf"{re.escape(name)}:(\d+)(?::\d+)?:?", fix, message)
    return out.strip()


Runner = Callable[[str], object]


def run_notes(language: str, program: str, offset: int, filename: str, *, timeout: float = 3.0) -> tuple[list[str], str | None]:
    """Run the program for real: (notes about what it printed, an error note or None). Never raises."""
    from code_coach.gotchas.runner import run_program

    try:
        result = run_program(language, program, timeout=timeout)
    except Exception as exc:  # the runner is missing, a temp folder failed...
        return [f"It was not run here ({str(exc).strip() or 'no toolchain found'}), so there is no output to show."], None
    if result.compile_error:
        words = shift_line_numbers(_first_error(language, result.stderr), offset, filename)
        return [], f"It does not compile: {words}"
    notes = printed_notes(result.stdout)
    if result.timed_out:
        notes.append(f"It was still running after {timeout:g} seconds, so it was stopped (an endless loop?).")
        return notes, None
    if not result.ok:
        return notes, _runtime_error(language, result, offset, filename)
    return notes, None


def _first_error(language: str, stderr: str) -> str:
    lines = [ln.strip() for ln in stderr.replace("\r\n", "\n").split("\n") if ln.strip()]
    for ln in lines:
        if re.search(r"\berror\b", ln, re.I):
            return re.sub(r"^.*?(snippet\.\w+)", r"\1", ln)
    return lines[0] if lines else "the compiler gave no reason"


def _runtime_error(language: str, result, offset: int, filename: str) -> str:
    err = result.stderr.replace("\r\n", "\n").strip()
    if language == "dart":
        lines = [ln for ln in err.split("\n") if ln.strip()]
        for i, ln in enumerate(lines):
            if ln.startswith("Unhandled exception"):
                body = lines[i + 1] if i + 1 < len(lines) else ""
                return f"It stopped with an error: {shift_line_numbers(body, offset, filename)}"
        return "It stopped with an error: " + (shift_line_numbers(lines[0], offset, filename) if lines else f"exit code {result.returncode}")
    if language == "sql":
        first = err.split("\n")[0] if err else "the database refused it"
        return "SQLite stopped with an error: " + re.sub(r"^SQLError:\s*", "", first)
    first = err.split("\n")[0] if err else ""
    return f"The program stopped early (exit code {result.returncode})" + (f": {first}" if first else ".")


def finish(summary: str, rows: list[dict], notes: list[str], error_note: str | None) -> dict:
    return {"ok": True, "summary": summary, "lines": rows, "output_notes": notes, "error_note": error_note}


def empty() -> dict:
    return {"ok": False, "summary": "There's nothing in the editor yet.", "lines": [], "output_notes": []}


def join_names(names: list[str]) -> str:
    unique = list(dict.fromkeys(names))
    if not unique:
        return ""
    if len(unique) == 1:
        return unique[0]
    return ", ".join(unique[:-1]) + f" and {unique[-1]}"


def sentence(parts: list[str]) -> str:
    """Join clause texts into one row of prose; each clause already ends sensibly."""
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        p = p[0].upper() + p[1:]
        if p[-1] not in ".!?`":
            p += "."
        out.append(p)
    return " ".join(out)


# ── Small text helpers both C-family readers use ────────────

def balanced(text: str, start: int) -> int:
    """Index of the bracket that closes the one at `start` (strings skipped), or -1."""
    depth, i, quote = 0, start, ""
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def head_of(s: str, kw: str) -> tuple[str, str] | None:
    """`kw (inner) rest` -> (inner, rest), matching the parentheses properly."""
    m = re.match(rf"^{kw}\s*\(", s)
    if not m:
        return None
    end = balanced(s, m.end() - 1)
    if end < 0:
        return None
    return s[m.end() : end], s[end + 1 :].strip()


def split_top(text: str, sep: str = ",") -> list[str]:
    """Split at `sep` outside any brackets or strings."""
    out, depth, cur, quote, i = [], 0, "", "", 0
    while i < len(text):
        ch = text[i]
        if quote:
            cur += ch
            if ch == "\\":
                cur += text[i + 1 : i + 2]
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
            cur += ch
        elif ch in "([{":
            depth += 1
            cur += ch
        elif ch in ")]}":
            depth -= 1
            cur += ch
        elif ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip():
        out.append(cur)
    return out


def capital(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def lower_first(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s
