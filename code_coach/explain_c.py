"""Plain-English walkthrough of C, a statement at a time.

Like the Dart reader: `explain_common.read_pieces` splits the code into statements and headers, `explain_expr` reads one
expression, and each piece gets a sentence. A piece it cannot follow gets an honest fallback row, never a guess.

Every sentence that states a checkable fact lives in `FACTS`; a claim written ```printf(...)` prints `OUT``` is
compiled and run for real by tests/test_explain_c.py, so a rule here cannot say something C does not do.
"""

from __future__ import annotations

import re

from . import explain_common as C
from .explain_expr import N, Say, code, say, try_expr, walk
from .explain_programs import c_program

FACTS: dict[str, str] = {
    "div": "Dividing two integers throws the fraction away: `printf(\"%d\", 7 / 2)` prints `3`. If either side is a float the fraction stays: `printf(\"%.1f\", 7 / 2.0)` prints `3.5`.",
    "mod": "`%` takes the sign of the left side: `printf(\"%d\", -7 % 3)` prints `-1`.",
    "uwrap": "An unsigned type never goes negative: past its top it wraps around to 0, so `printf(\"%u\", (uint8_t)(255 + 1))` prints `0`.",
    "promo": "Small integer types are widened to int before arithmetic, so the sum is not cut short: `printf(\"%d\", (uint8_t)200 + (uint8_t)100)` prints `300`.",
    "strcmp": "`strcmp` gives 0 when the strings are equal and a negative or positive number otherwise (not always -1 or 1): `printf(\"%d\", strcmp(\"a\", \"a\"))` prints `0`.",
    "strlen": "`strlen` counts the characters before the ending `\\0`, not including it: `printf(\"%zu\", strlen(\"seed\"))` prints `4`.",
    "terminator": "A string literal has one extra byte for its ending `\\0`: `printf(\"%zu\", sizeof(\"abc\"))` prints `4`.",
    "sizeof": "`sizeof` gives a size in bytes, worked out at compile time: `printf(\"%zu\", sizeof(int[5]))` prints `20`.",
    "width": "`%5d` pads to at least 5 characters, on the left: `printf(\"[%5d]\", 42)` prints `[   42]`.",
    "left": "A `-` flag pads on the right instead: `printf(\"[%-5d]\", 42)` prints `[42   ]`.",
    "zero": "A `0` flag pads with zeros: `printf(\"[%05d]\", 42)` prints `[00042]`.",
    "hex": "`%x` writes a number in hexadecimal, lower case: `printf(\"%x\", 255)` prints `ff`; `%X` is upper case: `printf(\"%X\", 255)` prints `FF`.",
    "octal": "`%o` writes a number in octal: `printf(\"%o\", 8)` prints `10`.",
    "char": "`%c` writes a number as the character with that code: `printf(\"%c\", 65)` prints `A`.",
    "prec": "`%.2f` rounds to 2 digits after the point, and `%5.2f` also pads to width 5: `printf(\"[%5.2f]\", 3.14159)` prints `[ 3.14]`.",
    "zu": "`%zu` is the specifier for a `size_t` such as the result of `sizeof`: `printf(\"%zu\", sizeof(int))` prints `4`.",
    "unsigned": "`%u` writes an unsigned number: `printf(\"%u\", 4000000000u)` prints `4000000000`.",
    "pct": "`%%` prints one percent sign: `printf(\"100%%\")` prints `100%`.",
    "macro": "A macro is plain text pasted in before compiling, so an operator in its body is not protected: with `#define SQ(x) x * x`, `SQ(1 + 2)` becomes `1 + 2 * 1 + 2`, which is 5, not 9. Wrapping the body and each parameter in parentheses fixes it.",
    "fallthrough": "A `case` with no `break` runs straight on into the next case.",
    "ptrarith": "Adding 1 to a pointer moves it by one whole element, not one byte.",
    "postinc": "`*p++` reads what p points at and then moves p on one element; `i++` gives the old value and then adds one.",
    "assignif": "`if (x = 5)` assigns 5 and then tests the 5 (which is true); `==` is the comparison.",
    "bitops": "`&`, `|`, `^`, `<<` and `>>` work on the bits of a number; `printf(\"%d\", 6 & 3)` prints `2`.",
}

_TYPE_WORDS = {"int", "char", "short", "long", "unsigned", "signed", "float", "double", "void", "_Bool", "bool", "size_t", "ptrdiff_t", "intptr_t", "uintptr_t", "FILE", "wchar_t"}
_STORAGE = {"static", "extern", "const", "volatile", "register", "auto", "inline", "typedef", "restrict"}
_CONTROL = {"if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue", "return", "goto", "sizeof"}
_TYPE_RE = re.compile(r"^(?:u?int(?:8|16|32|64)_t|u?int_(?:fast|least)\d+_t)$")


def _is_type_word(w: str, typedefs: set[str]) -> bool:
    return w in _TYPE_WORDS or w in typedefs or bool(_TYPE_RE.match(w)) or w in ("struct", "union", "enum")


def _type_phrase(words: list[str], stars: int = 0, dims: list[str] | None = None) -> str:
    ws = [w for w in words if w not in _STORAGE]
    base = " ".join(ws)
    nice = {
        "int": "an int (a whole number)", "unsigned": "an unsigned int (a whole number, never negative)", "unsigned int": "an unsigned int (a whole number, never negative)",
        "char": "a char (one character, stored as a small number)", "unsigned char": "an unsigned char (a small number 0 to 255)", "short": "a short (a smaller whole number)",
        "long": "a long (a larger whole number)", "long long": "a long long (a 64-bit whole number)", "float": "a float (a decimal number)", "double": "a double (a more precise decimal number)",
        "size_t": "a size_t (an unsigned size or count)", "bool": "a bool (true or false)", "_Bool": "a _Bool (0 or 1)", "void": "void",
    }
    m = re.match(r"^(u?)int(\d+)_t$", base)
    if m:
        bits = int(m.group(2))
        if m.group(1):
            nice[base] = f"a {base} (a {bits}-bit number that is never negative: 0 to {2 ** bits - 1})"
        else:
            nice[base] = f"a {base} (a {bits}-bit whole number: {-2 ** (bits - 1)} to {2 ** (bits - 1) - 1})"
    phrase = nice.get(base, f"a {base}" if base else "a value")
    if base.startswith(("struct ", "union ", "enum ")):
        phrase = f"a {base}"
    const = "const" in words
    if stars:
        target = phrase.split(" (")[0].replace("a ", "", 1) if phrase.startswith("a ") else phrase
        out = "a pointer to " + ("a read-only " if const else "") + (target if stars == 1 else "a pointer to " * (stars - 1) + target)
        if "char" in ws and stars == 1:
            out += " (usually text)"
        phrase = out
    if dims:
        n = [x for x in dims if x]
        size = " x ".join(n) if n else "an unspecified number of"
        elem = base + ("s" if not base.endswith("s") else "")
        if "char" in ws and not stars:
            phrase = f"an array of {size} chars (room for text)"
        elif stars:
            phrase = f"an array of {size} pointers"
        else:
            phrase = f"an array of {size} {elem}"
    elif const and not stars:
        phrase += ", read-only"
    return phrase


# ── printf ──────────────────────────────────────────────────

_SPEC = re.compile(r"%([-+ 0#]*)(\*|\d+)?(?:\.(\*|\d+))?(hh|h|ll|l|z|j|t|L)?([diuoxXfFeEgGcspn%])")
_CONV = {
    "d": "as a signed whole number", "i": "as a signed whole number", "u": "as an unsigned whole number", "o": "in octal", "x": "in hexadecimal (lower case)",
    "X": "in hexadecimal (upper case)", "f": "as a decimal number", "F": "as a decimal number",
    "e": "in scientific notation", "E": "in scientific notation", "g": "in the shorter of decimal or scientific form", "G": "in the shorter of decimal or scientific form",
    "c": "as one character", "s": "as text", "p": "as an address", "n": "(stores the count so far)",
}


def _printf_phrase(fmt_raw: str, args: list[N], ctx: Say, name: str) -> tuple[str, list[str]]:
    inner = fmt_raw[1:-1] if len(fmt_raw) >= 2 else fmt_raw
    specs = list(_SPEC.finditer(inner))
    facts: list[str] = []
    parts: list[str] = []
    ai = 0
    for m in specs:
        flags, width, prec, length, conv = m.groups()
        if conv == "%":
            facts.append(FACTS["pct"])
            parts.append("a literal `%`")
            continue
        if width == "*":
            ai += 1
        if prec == "*":
            ai += 1
        arg = say(args[ai], ctx, 1) if ai < len(args) else "(a missing argument)"
        ai += 1
        what = _CONV.get(conv, "")
        if length == "z" and conv in "du":
            what = "as a size_t (an unsigned size)"
            facts.append(FACTS["zu"])
        extras = []
        if width and width != "*":
            extras.append(f"padded to at least {width} wide" + (" on the right (left-aligned)" if "-" in flags else " on the left"))
            facts.append(FACTS["left"] if "-" in flags else FACTS["width"])
        if "0" in flags and "-" not in flags and width:
            extras.append("with zeros as the padding")
            facts.append(FACTS["zero"])
        if "+" in flags:
            extras.append("with its sign always shown")
        if prec and prec != "*":
            extras.append(f"{prec} digit{'s' if prec != '1' else ''} after the point" if conv in "fFeE" else f"at most {prec} characters" if conv == "s" else f"at least {prec} digits")
            if conv in "fF":
                facts.append(FACTS["prec"])
        if conv in "fF" and not prec:
            extras.append("6 digits after the point (the default)")
        if conv in "xX":
            facts.append(FACTS["hex"])
        if conv == "o":
            facts.append(FACTS["octal"])
        if conv == "c":
            facts.append(FACTS["char"])
        if conv == "u" and not length:
            facts.append(FACTS["unsigned"])
        parts.append(f"`{m.group(0)}` shows {arg} {what}" + (", " + ", ".join(extras) if extras else ""))
    ends = inner.endswith("\\n")
    shown = re.sub(r"\\n", "", inner)
    head = "writes" + (f" the text \"{shown}\"" if not specs else f" \"{shown}\"")
    if specs:
        head += ", where " + "; ".join(parts)
    if ends:
        head += ", then ends the line"
    return head, facts


# ── vocabulary ──────────────────────────────────────────────

_FUNCS: dict[str, str] = {
    "strlen": "the number of characters in {a0}, not counting the ending `\\0`", "strcpy": "copies the text {a1} into {a0}, including its ending `\\0`",
    "strncpy": "copies at most {a2} characters of {a1} into {a0} (it does not add a `\\0` if {a1} is that long)", "strcat": "sticks {a1} onto the end of {a0}",
    "strncat": "sticks at most {a2} characters of {a1} onto the end of {a0}", "strcmp": "compares {a0} with {a1}: 0 means equal, negative means {a0} comes first, positive means {a0} comes after",
    "strncmp": "compares the first {a2} characters of {a0} and {a1} (0 means equal)", "strchr": "finds the first {a1} in {a0} (or NULL)", "strrchr": "finds the last {a1} in {a0} (or NULL)",
    "strstr": "finds the first {a1} inside {a0} (or NULL)", "memcpy": "copies {a2} bytes from {a1} to {a0}", "memset": "fills {a2} bytes of {a0} with the value {a1}",
    "memcmp": "compares {a2} bytes of {a0} and {a1} (0 means equal)", "memmove": "copies {a2} bytes from {a1} to {a0}, safely even if they overlap", "puts": "writes {a0} and a newline",
    "putchar": "writes the single character {a0}", "abs": "the size of {a0}, ignoring the sign", "atoi": "reads the digits of {a0} as an int", "strtol": "reads the number at the start of {a0}",
    "strtok": "cuts the next piece out of {a0} at any of the separators {a1} (it changes the text in place)", "toupper": "{a0} as an upper-case letter", "tolower": "{a0} as a lower-case letter",
    "isalpha": "whether {a0} is a letter (non-zero if so)", "isdigit": "whether {a0} is a digit (non-zero if so)", "isspace": "whether {a0} is white space (non-zero if so)",
    "malloc": "asks for {a0} bytes of memory (and may fail with NULL)", "free": "gives the memory at {a0} back", "realloc": "resizes the memory at {a0} to {a1} bytes", "calloc": "asks for {a0} zeroed items of {a1} bytes",
    "qsort": "sorts the {a1} items at {a0} using the comparison function {a3}", "snprintf": "writes formatted text into {a0}, at most {a1} bytes", "sscanf": "reads values out of the text {a0} using the format {a1}",
    "sqrt": "the square root of {a0}", "pow": "{a0} raised to the power {a1}", "floor": "{a0} rounded down", "ceil": "{a0} rounded up", "round": "{a0} rounded to the nearest whole number", "fabs": "the size of {a0}, ignoring the sign",
    "exit": "ends the program with the status {a0}", "rand": "a pseudo-random number", "getchar": "reads one character",
}
_VERBS = {"copies", "sticks", "compares", "finds", "fills", "writes", "reads", "cuts", "asks", "gives", "ends", "sorts", "resizes"}


def _c_call(node: N, ctx: Say) -> str | None:
    fn, args = node.a
    if fn.kind != "id":
        if fn.kind in ("paren", "mem", "un", "idx"):
            return f"calls the function that {code(fn.text)} stands for" + (f" with {', '.join(say(a, ctx, 1) for a in args)}" if args else "")
        return None
    name = fn.a[0]
    argv = [say(a, ctx, 1) for a in args]
    if name in _FUNCS:
        slots = {f"a{i}": (argv[i] if i < len(argv) else "it") for i in range(4)}
        return _FUNCS[name].format(**slots)
    if name == "printf":
        return None
    return f"calls {name}" + (f" with {', '.join(argv)}" if argv else " with no arguments")


def _c_hook(node: N, ctx: Say, level: int) -> str | None:
    k = node.kind
    if k == "call":
        fn = node.a[0]
        if fn.kind == "id" and fn.a[0] == "printf" and node.a[1] and node.a[1][0].kind == "str":
            return None
        phrase = _c_call(node, ctx)
        if phrase:
            first = phrase.split(" ", 1)[0]
            if first in _VERBS or first == "calls":
                gerund = {"copies": "copying", "sticks": "sticking", "compares": "comparing", "finds": "finding", "fills": "filling", "writes": "writing", "reads": "reading", "cuts": "cutting", "asks": "asking",
                          "gives": "giving", "ends": "ending", "sorts": "sorting", "resizes": "resizing", "calls": "calling"}[first]
                return f"the result of {gerund} {phrase.split(' ', 1)[1]}" if " " in phrase else phrase
        return phrase
    if k == "mem":
        obj, op, name = node.a
        if op == "->":
            return f"the {name} of what {say(obj, ctx, level + 1)} points to"
        return f"the {name} of {say(obj, ctx, level + 1)}"
    if k == "str":
        raw = node.a[0]
        if raw.startswith("'"):
            return f"the character {raw}"
        return f'the text {raw}' if len(raw) < 40 else code(raw)
    if k == "init":
        items = node.a[0]
        return "a list of " + ", ".join(say(x, ctx, level + 1) for x in items[:6]) + (f" and {len(items) - 6} more" if len(items) > 6 else "") if items else "an empty initializer list"
    if k == "designated":
        return f"{code(node.a[0].text)} set to {say(node.a[1], ctx, level + 1)}"
    if k == "compound":
        return f"a temporary {node.a[0].strip()} built from {say(node.a[1], ctx, level + 1)}"
    if k == "comma":
        return "the last of: " + ", ".join(say(x, ctx, level + 1) for x in node.a[0])
    if k == "post":
        return f"{say(node.a[1], ctx, level + 1)} ({'then adds' if node.a[0] == '++' else 'then subtracts'} one)"
    if k == "un" and node.a[0] in ("++", "--"):
        return f"{say(node.a[1], ctx, level + 1)} after {'adding' if node.a[0] == '++' else 'subtracting'} one"
    if k == "bin" and node.a[0] == "%":
        return f"{say(node.a[1], ctx, level + 1)} remainder {say(node.a[2], ctx, level + 1)}"
    return None


CTX = Say(call=_c_call, hook=_c_hook, limit=3)
_SEEN: set[str] = set()
_TYPEDEFS: set[str] = set()


def d(node: N | None) -> str:
    return say(node, CTX) if node is not None else ""


def _facts(nodes: list[N], text: str = "") -> list[str]:
    ops: set[str] = set()
    kinds: set[str] = set()
    out: list[str] = []
    for root in nodes:
        for n in walk(root):
            if n.kind in ("bin", "asg"):
                ops.add(n.a[0])
            kinds.add(n.kind)
            if n.kind == "post" or (n.kind == "un" and n.a[0] in ("++", "--")):
                ops.add("++")
            if n.kind == "cast" and re.search(r"u?int\d+_t|unsigned", n.a[0]):
                out.append(FACTS["uwrap"])
            if n.kind == "call" and n.a[0].kind == "id":
                nm = n.a[0].a[0]
                if nm in ("strcmp", "strncmp"):
                    out.append(FACTS["strcmp"])
                if nm == "strlen":
                    out.append(FACTS["strlen"])
            if n.kind in ("sizeof", "sizeof_t"):
                out.append(FACTS["sizeof"])
    if "/" in ops or "/=" in ops:
        out.append(FACTS["div"])
    if "%" in ops or "%=" in ops:
        out.append(FACTS["mod"])
    if ops & {"&", "|", "^", "<<", ">>"}:
        out.append(FACTS["bitops"])
    if re.search(r"\buint(?:8|16)_t\b", text) and ops & {"+", "*", "+=", "-", "*="}:
        out.append(FACTS["promo"])
    if re.search(r"\bunsigned\b|\buint\d+_t\b", text) and ops & {"+", "+=", "-", "-=", "++"} and FACTS["uwrap"] not in out:
        out.append(FACTS["uwrap"])
    fresh = []
    for f in out:
        if f not in _SEEN and f not in fresh:
            fresh.append(f)
    _SEEN.update(fresh)
    return fresh[:2]


def _sub(p: C.Piece, text: str) -> C.Piece:
    from .explain_expr import tokenize

    return C.Piece(p.line, text, tokenize(text, False), p.mode, p.frame, p.class_name, p.class_kind, p.opens_block, p.lambda_block, p.closers, p.depth)


def _expr(src: str) -> N | None:
    return try_expr(src, False, _TYPEDEFS)


# ── preprocessor ────────────────────────────────────────────

def _pp(text: str) -> str | None:
    s = re.sub(r"\\\s*$", "", text.strip())
    m = re.match(r"^#\s*include\s*[<\"]([^>\"]+)[>\"]", s)
    if m:
        h = m.group(1)
        what = {"stdio.h": "printf, scanf and friends", "string.h": "strlen, strcpy, memcpy and the other text and memory functions", "stdint.h": "fixed-size types such as uint8_t",
                "stdlib.h": "malloc, free, qsort, atoi", "stddef.h": "size_t and NULL", "math.h": "sqrt, pow, floor", "ctype.h": "isalpha, toupper and friends", "limits.h": "INT_MAX and the other limits",
                "stdbool.h": "bool, true and false", "assert.h": "assert"}.get(h)
        return f"pastes in the header {h}" + (f", which declares {what}" if what else "") + " (the preprocessor does this before compiling)."
    m = re.match(r"^#\s*define\s+(\w+)(\(([^)]*)\))?\s*(.*)$", s, re.S)
    if m:
        name, params, args, body = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        if params is None:
            return f"defines {name} as a constant: the preprocessor swaps the name for `{code(body)}` everywhere before compiling." if body else f"defines the name {name} with no value (used with #ifdef)."
        base = f"defines the macro {name}({args}): the preprocessor pastes `{code(body)}` in place of every call, as plain text."
        stripped = body
        wrapped = stripped.startswith("(") and C.balanced(stripped, 0) == len(stripped) - 1
        has_op = bool(re.search(r"[-+*/%<>=&|^?]", re.sub(r"\([^()]*\)", "", stripped))) or bool(re.search(r"\b" + re.escape(args.split(",")[0].strip() or "_") + r"\b[^()]*[-+*/%]", stripped))
        unparen_param = any(re.search(rf"(?<![\w(]){re.escape(a.strip())}(?![\w)])", stripped) and not re.search(rf"\({re.escape(a.strip())}\)", stripped) for a in args.split(",") if a.strip())
        if body and ((has_op and not wrapped) or (unparen_param and re.search(r"[-+*/%<>=&|^]", stripped))):
            _SEEN.add(FACTS["macro"])
            return base + " Careful: " + FACTS["macro"]
        return base
    m = re.match(r"^#\s*(ifdef|ifndef|if|elif|else|endif|undef|pragma|error|line)\b\s*(.*)$", s)
    if m:
        kw, rest = m.groups()
        return {"ifdef": f"compiles what follows only if {rest} has been #defined.", "ifndef": f"compiles what follows only if {rest} has NOT been #defined.",
                "if": f"compiles what follows only if `{code(rest)}` is true at preprocessing time.", "elif": f"otherwise, compiles what follows only if `{code(rest)}` is true.",
                "else": "otherwise, compiles what follows instead.", "endif": "ends the conditional compilation above.", "undef": f"forgets the definition of {rest}.",
                "pragma": f"a compiler instruction: `{code(rest)}`.", "error": "stops compiling with this message.", "line": "sets the line number the compiler reports."}[kw]
    return None


# ── statements ──────────────────────────────────────────────

def _decl(p: C.Piece, text: str) -> str | None:
    toks = p.toks
    if not toks or toks[0].text in _CONTROL or toks[0].kind == "str":
        return None
    words: list[str] = []
    i = 0
    typedef = False
    while i < len(toks) and toks[i].kind == "id" and (_is_type_word(toks[i].text, _TYPEDEFS) or toks[i].text in _STORAGE):
        if toks[i].text == "typedef":
            typedef = True
        words.append(toks[i].text)
        if toks[i].text in ("struct", "union", "enum") and i + 1 < len(toks) and toks[i + 1].kind == "id":
            i += 1
            words.append(toks[i].text)
        i += 1
    core_words = [w for w in words if w not in _STORAGE]
    if not core_words and i < len(toks) and toks[i].kind == "id" and i + 1 < len(toks):
        # a typedef name used as the type: `Node *p`, `fn f = dbl`
        nxt = toks[i + 1]
        if (nxt.kind == "id" or nxt.text == "*") and toks[i].text not in _CONTROL and not (nxt.text == "*" and i + 2 < len(toks) and toks[i + 2].text in ("=", ";") and False):
            if nxt.kind == "id" or (nxt.text == "*" and i + 2 < len(toks) and toks[i + 2].kind in ("id", "op")):
                words.append(toks[i].text)
                core_words = [toks[i].text]
                i += 1
    if not core_words:
        return None
    if typedef:
        fm = re.search(r"\(\s*\*\s*(\w+)\s*\)", text)
        name = fm.group(1) if fm else (re.findall(r"[A-Za-z_]\w*", re.sub(r"\[[^\]]*\]|\([^()]*\)\s*$", "", text))[-1:] or [""])[0]
        if name:
            _TYPEDEFS.add(name)
        return f"gives a type a new name, {name}: `{code(text[len('typedef'):])}`, so later code can write {name} instead." if name else None
    rest_toks = toks[i:]
    if not rest_toks:
        # `struct P { ... }` header handled elsewhere; a bare type is nothing
        return None
    if p.opens_block and core_words and core_words[0] in ("struct", "union", "enum") and len(rest_toks) == 0:
        return None
    rest_text = text[rest_toks[0].start - toks[0].start :]
    segments = C.split_top(rest_text)
    out = []
    member = p.frame == "class"
    for seg in segments:
        seg = seg.strip()
        m = re.match(r"^\(\s*\*\s*(\w+)\s*((?:\[[^\]]*\]\s*)*)\)\s*\((.*?)\)\s*(?:=\s*(.*))?$", seg, re.S)
        if m:
            name, arr, params, init = m.groups()
            s = f"creates {name}, " + ("an array of pointers" if arr else "a pointer") + f" to a function taking ({code(params)}) and giving back {_type_phrase(core_words)}"
            s += f", set to {d(_expr(init)) if init and _expr(init) else code(init)}" if init else ""
            out.append(s)
            continue
        m = re.match(r"^((?:\*\s*(?:const\s+)?)*)\s*(\w+)\s*((?:\[[^\]]*\]\s*)*)\s*(?::\s*(\d+))?\s*(?:=\s*(.*))?$", seg, re.S)
        if not m:
            return None
        stars_txt, name, dims_txt, bits, init = m.groups()
        stars = stars_txt.count("*")
        dims = re.findall(r"\[([^\]]*)\]", dims_txt or "")
        typ = _type_phrase(words, stars, dims)
        if "const" in stars_txt:
            typ += ", and the pointer itself can never be pointed anywhere else"
        verb = "declares the member" if member else "creates"
        s = f"{verb} {name}, {typ}"
        if bits:
            s += f", {bits} bits wide"
        if init is not None:
            init = init.strip()
            e = _expr(init)
            if dims and not dims[0] and init.startswith('"'):
                s += " (sized to fit the text plus its ending `\0`)"
            if dims and not dims[0] and e is not None and e.kind == "init":
                s += f" (its size comes from the {len(e.a[0])} items in the list)"
            if init.startswith('"') and dims and "char" in core_words:
                s += f", filled with {init}"
                if dims[0].isdigit() and len(init) - 2 >= int(dims[0]) and "\\" not in init:
                    s += " (careful: no room is left for the ending `\\0`)"
                _SEEN.add(FACTS["terminator"])
            elif e is not None:
                s += f", set to {d(e)}"
                fs = _facts([e], text)
                if fs:
                    s += ". " + " ".join(fs)
            else:
                s += f", set to `{code(init)}`"
        else:
            s += ", with no value yet" + ("" if member or "static" in words else " (it holds whatever was in memory: do not read it before setting it)")
            if "static" in words:
                s = s.replace("with no value yet", "starting at zero")
        out.append(s)
    return ". ".join(C.capital(x) if k else x for k, x in enumerate(out))


def _function(p: C.Piece, text: str) -> str | None:
    if p.mode != "stmt" or p.frame == "class":
        return None
    for cand in [i for i, ch in enumerate(text) if ch == "("]:
        close = C.balanced(text, cand)
        if close < 0:
            continue
        before = text[:cand].strip()
        after = text[close + 1 :].strip()
        m = re.match(r"^(?P<pre>.*?)(?P<stars>[\s*]*)(?P<name>[A-Za-z_]\w*)$", before, re.S)
        if not m or after:
            continue
        pre_words = m.group("pre").split()
        if not pre_words or pre_words[-1] in _CONTROL or pre_words[0] in ("return", "else", "typedef"):
            continue
        if not (p.opens_block or p.mode == "stmt"):
            continue
        name = m.group("name")
        if name in _CONTROL or name in ("sizeof",):
            continue
        # a prototype ends with `;` (not part of the piece); a definition opens a block - an expression statement would not have a type first
        if not _is_type_word(pre_words[-1], _TYPEDEFS) and not (len(pre_words) >= 1 and (pre_words[0] in _STORAGE or _is_type_word(pre_words[0], _TYPEDEFS) or pre_words[-1] in _TYPEDEFS)) and not m.group("stars").strip():
            if not (len(pre_words) >= 1 and re.match(r"^[A-Za-z_]\w*$", pre_words[-1]) and p.opens_block):
                continue
        params = text[cand + 1 : close].strip()
        if params in ("", "void"):
            pw = "taking nothing"
        else:
            names = []
            for chunk in C.split_top(params):
                chunk = chunk.strip()
                if chunk == "...":
                    names.append("any number of extra arguments (...)")
                    continue
                mm = re.search(r"(\*+)?\s*(\w+)\s*(\[[^\]]*\])?\s*$", chunk)
                names.append(f"{mm.group(2) if mm else chunk}" + (" (a pointer)" if mm and mm.group(1) else " (an array, really a pointer)" if mm and mm.group(3) else ""))
            pw = "taking " + ", ".join(names)
        stars = m.group("stars").count("*")
        ret_words = [w for w in pre_words if w not in _STORAGE]
        ret = _type_phrase(ret_words, stars)
        stat = " It is static: only this file can call it." if "static" in pre_words else ""
        if name == "main":
            return f"defines main, {pw}: the function C runs first. Its return value is the program's exit status (0 means success)."
        if ret_words == ["void"] and not stars:
            r = "giving back nothing"
        else:
            r = f"giving back {ret}"
        kind = "defines" if p.opens_block else "declares (a prototype: it promises the function exists and says how to call it)"
        return f"{kind} the function {name}, {pw}, {r}.{stat}"
    return None


def _struct_header(p: C.Piece, text: str) -> str | None:
    m = re.match(r"^(typedef\s+)?(struct|union|enum)\s*(\w+)?\s*$", text.strip())
    if m and p.opens_block:
        kind, name = m.group(2), m.group(3)
        what = {"struct": "a struct: a bundle of named fields kept together", "union": "a union: several fields sharing the same memory", "enum": "an enum: a set of named whole-number constants"}[kind]
        label = f" {name}" if name else ""
        return f"defines the {kind}{label}: {what.split(': ', 1)[1] if ': ' in what else what}" + (", and `typedef` will give it a shorter name after the closing brace" if m.group(1) else "") + "."
    return None


def _case_text(p: C.Piece, text: str) -> str | None:
    s = text.strip()
    m = re.match(r"^case\s+(.*?)\s*:\s*(.*)$", s, re.S)
    if m:
        tail = m.group(2).strip()
        e = _expr(m.group(1))
        base = f"when the value is {d(e) if e else code(m.group(1))}:"
        if tail:
            inner = _stmt(_sub(p, tail), tail)
            return f"{base} {C.lower_first(inner) if inner else '`' + code(tail) + '`'}"
        extra = ""
        if p.__dict__.get("fall") == "share":
            extra = " (this case has no code of its own, so it shares the next case's code)"
        elif p.__dict__.get("fall") == "through":
            extra = " Careful: this case has no `break`, so it runs on into the next one. " + FACTS["fallthrough"]
            _SEEN.add(FACTS["fallthrough"])
        return base.rstrip(":") + ", runs the code below." + extra
    m = re.match(r"^default\s*:\s*(.*)$", s, re.S)
    if m:
        tail = m.group(1).strip()
        inner = _stmt(_sub(p, tail), tail) if tail else ""
        return "when no case matched: " + (C.lower_first(inner) if inner else "runs the code below.")
    return None


def _control(p: C.Piece, text: str) -> str | None:
    s = text.strip()
    toks = p.toks
    if not toks:
        return None
    w = toks[0].text
    if w == "else":
        rest = s[4:].strip()
        if rest.startswith("if"):
            inner = _control(_sub(p, rest), rest)
            return "otherwise, " + inner if inner else None
        if rest:
            inner = _stmt(_sub(p, rest), rest)
            return "otherwise, " + C.lower_first(inner) if inner else None
        return "otherwise, does what follows."
    if w == "if":
        hd = C.head_of(s, "if")
        if not hd:
            return None
        cond_src, tail = hd
        e = _expr(cond_src)
        base = f"if {_cond(e, cond_src)}, does what follows."
        if e is not None and any(n.kind == "asg" and n.a[0] == "=" for n in walk(e)):
            base += " " + FACTS["assignif"]
            _SEEN.add(FACTS["assignif"])
        if tail:
            inner = _stmt(_sub(p, tail), tail)
            if inner:
                base = f"if {_cond(e, cond_src)}, then {C.lower_first(inner)}"
        fs = _facts([e] if e else [], cond_src)
        return base + (" " + " ".join(fs) if fs else "")
    if w == "for":
        hd = C.head_of(s, "for")
        if not hd:
            return None
        head, tail = hd
        parts = head.split(";")
        if len(parts) == 3:
            init, cond, step = (x.strip() for x in parts)
            if not init and not cond and not step:
                return "loops forever until something inside breaks out." + _tail(p, tail)
            e = _expr(cond) if cond else None
            init_txt = f"starting with `{code(init)}`" if init else "with no setup"
            cond_txt = f"keeps going while {_cond(e, cond)}" if cond else "keeps going with no condition"
            step_txt = f"and does `{code(step)}` after each time round" if step else "and changes nothing between rounds"
            fs = _facts([e] if e else [], cond)
            return f"loops {init_txt}, {cond_txt}, {step_txt}." + (" " + " ".join(fs) if fs else "") + _tail(p, tail)
        return None
    if w == "while":
        hd = C.head_of(s, "while")
        if not hd:
            return None
        e = _expr(hd[0])
        fs = _facts([e] if e else [], hd[0])
        return f"keeps looping while {_cond(e, hd[0])}." + (" " + " ".join(fs) if fs else "") + _tail(p, hd[1])
    if w == "do":
        return "does what follows once, then checks the while condition after it and repeats."
    if w == "switch":
        hd = C.head_of(s, "switch")
        e = _expr(hd[0]) if hd else None
        return f"jumps to the case that matches {d(e) if e else code(s[6:])}; a case with no `break` runs on into the next."
    if w in ("case", "default"):
        return _case_text(p, s)
    if w == "break":
        return "leaves the loop (or the switch) right here."
    if w == "continue":
        return "skips the rest of this round of the loop and starts the next."
    if w == "goto":
        return f"jumps to the label {s[4:].strip()}."
    if w == "return":
        v = s[6:].strip()
        if not v:
            return "leaves this function and gives back nothing."
        e = _expr(v)
        fs = _facts([e] if e else [], v)
        return f"gives back {d(e) if e else '`' + code(v) + '`'} and leaves this function." + (" " + " ".join(fs) if fs else "")
    if re.match(r"^[A-Za-z_]\w*\s*:$", s):
        return f"a label named {w}, a place `goto {w}` can jump to."
    return None


def _cond(e: N | None, src: str) -> str:
    """A condition in words; a bare value (not a comparison) is true when it is not zero."""
    if e is None:
        return code(src)
    inner = e
    while inner.kind == "paren":
        inner = inner.a[0]
    text = d(e)
    if inner.kind == "bin" and inner.a[0] in ("==", "!=", "<", ">", "<=", ">=", "&&", "||"):
        return text
    if inner.kind == "un" and inner.a[0] == "!":
        return text
    if inner.kind == "asg":
        return text
    return f"{text} is not zero (C treats any non-zero value as true)"


def _tail(p: C.Piece, tail: str) -> str:
    tail = tail.strip().rstrip(";")
    if not tail:
        return ""
    inner = _stmt(_sub(p, tail), tail)
    return f" Each time: {C.lower_first(inner)}" if inner else ""


def _stmt(p: C.Piece, text: str) -> str:
    text = text.strip().rstrip(";")
    return _control(p, text) or _decl(p, text) or _expr_statement(p, text) or ""


_ASSIGN_VERB = {"+=": "adds {r} to {l}", "-=": "subtracts {r} from {l}", "*=": "multiplies {l} by {r}", "/=": "divides {l} by {r}", "%=": "sets {l} to the remainder of {l} divided by {r}",
                "<<=": "shifts {l} left by {r} bits", ">>=": "shifts {l} right by {r} bits", "&=": "ANDs the bits of {r} into {l}", "|=": "ORs the bits of {r} into {l}", "^=": "XORs the bits of {r} into {l}"}


def _expr_statement(p: C.Piece, text: str) -> str | None:
    src = p.closed_text if text == p.text else text
    node = _expr(src)
    if node is None:
        parts = C.split_top(src.rstrip(";"))
        nodes = [_expr(x) for x in parts]
        if len(parts) > 1 and all(nodes):
            return "does these in order: " + "; ".join(C.lower_first(_expr_statement(_sub(p, x.strip()), x.strip()) or x.strip()).rstrip(".") for x in parts) + "."
        return None
    k = node.kind
    if k == "call" and node.a[0].kind == "id" and node.a[0].a[0] in _CONTROL:
        return None  # a statement the control-flow rules failed to read is not a call
    fs = _facts([node], src)
    tail = (" " + " ".join(fs)) if fs else ""
    if k == "asg":
        op, lhs, rhs = node.a
        left, right = d(lhs), d(rhs)
        if op == "=":
            if lhs.kind == "idx":
                return f"stores {right} at position {d(lhs.a[1])} of {d(lhs.a[0])}." + tail
            if lhs.kind == "un" and lhs.a[0] == "*":
                return f"stores {right} where {d(lhs.a[1])} points." + tail
            return f"sets {left} to {right}." + tail
        return _ASSIGN_VERB.get(op, "updates {l} with {r}").format(l=left, r=right) + "." + tail
    if k in ("post", "un") and node.a[0] in ("++", "--"):
        target = node.a[1]
        return f"{'adds' if node.a[0] == '++' else 'subtracts'} one {'to' if node.a[0] == '++' else 'from'} {d(target)}."
    if k == "un" and node.a[0] == "*" and node.a[1].kind == "post":
        _SEEN.add(FACTS["postinc"])
        return f"reads what {d(node.a[1].a[1])} points to, then moves {d(node.a[1].a[1])} on by one element. " + FACTS["postinc"]
    if k == "call":
        fn, args = node.a
        if fn.kind == "id" and fn.a[0] in ("printf", "fprintf", "sprintf", "snprintf") and fn.a[0] == "printf":
            if args and args[0].kind == "str":
                phrase, ff = _printf_phrase(args[0].a[0], args[1:], CTX, "prints")
                fresh = []
                for f in ff:
                    if f not in _SEEN and f not in fresh:
                        fresh.append(f)
                _SEEN.update(fresh)
                more = _facts(list(args[1:]), src)
                return C.capital(phrase) + "." + (" " + " ".join(fresh[:2] + more[:1]) if (fresh or more) else "")
            return f"prints {', '.join(d(a) for a in args)} (the first argument is the format)." + tail
        phrase = _c_call(node, CTX) or d(node)
        return C.capital(phrase) + "." + tail
    if k == "id" and p.frame != "class":
        return f"just names {node.a[0]}." if node.a[0] not in _CONTROL else None
    return f"evaluates {d(node)}." + tail


def describe_piece(p: C.Piece) -> str | None:
    text = p.text.strip()
    if p.mode == "pp":
        return _pp(text)
    if not text:
        return None
    if p.mode == "arg":
        src = p.closed_text
        e = _expr(src)
        if e is not None:
            if e.kind == "designated":
                return f"sets {code(e.a[0].text)} to {d(e.a[1])}."
            return C.capital(d(e)) + "."
        return None
    if p.mode == "cont":
        e = _expr("__r" + text) if text[0] in ".-" else _expr("__r " + text)
        return f"continues the statement above with `{code(text)}`."
    out = _struct_header(p, text)
    if out:
        return out
    out = _control(p, p.closed_text if p.closers and not p.opens_block else text)
    if out:
        return out
    out = _function(p, text)
    if out:
        return out
    if p.frame == "class" and p.class_kind == "enum":
        names = [x.strip().split("=")[0].strip() for x in C.split_top(text)]
        return f"lists the enum constants {', '.join(names)}" + (" (counting up from 0 unless a value is given)" if "=" not in text else " (a constant without a value is one more than the one before)") + "."
    out = _decl(p, text)
    if out:
        return out
    if re.fullmatch(r"[A-Za-z_]\w*", text) and p.frame == "file":
        return f"names the type just defined above as {text} (the typedef's new name)."
    return _expr_statement(p, text)


def _mark_fallthrough(infos: list[C.LineInfo]) -> None:
    """A `case` whose code never reaches a break/return before the next case falls through; an empty one shares."""
    flat = [(info, p) for info in infos for p in info.pieces]
    for idx, (info, p) in enumerate(flat):
        if p.mode != "stmt" or not re.match(r"^(case\b|default\s*:)", p.text.strip()):
            continue
        inline = re.match(r"^(?:case\s+.*?|default)\s*:\s*(.+)$", p.text.strip(), re.S)
        body = False
        exited = bool(inline and re.match(r"^(break|return|continue|goto)\b", inline.group(1).strip()))
        body = bool(inline)
        nxt_case = False
        for _i2, q in flat[idx + 1 :]:
            qt = q.text.strip()
            if q.depth < p.depth and q.frame != p.frame:
                break
            if re.match(r"^(case\b|default\s*:)", qt) and q.depth <= p.depth:
                nxt_case = True
                break
            if q.depth < p.depth:
                break
            body = True
            if re.match(r"^(break|return|continue|goto)\b", qt):
                exited = True
                break
        if not body and nxt_case:
            p.__dict__["fall"] = "share"
        elif body and not exited and nxt_case:
            p.__dict__["fall"] = "through"


def _read_rows(code_text: str) -> tuple[list[dict], int, list[str]]:
    infos = C.read_pieces(code_text, False)
    _SEEN.clear()
    _TYPEDEFS.clear()
    _TYPEDEFS.update(re.findall(r"\btypedef\b[^;{]*?\b(\w+)\s*;", code_text))
    _TYPEDEFS.update(re.findall(r"}\s*(\w+)\s*;", code_text))
    _TYPEDEFS.update(re.findall(r"^\s*(?:struct|union)\s+(\w+)\s*\{", code_text, re.M))
    try:
        _mark_fallthrough(infos)
    except Exception:
        pass
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


def explain_c(code_text: str, *, run: bool = True, context: str = "") -> dict:
    """Walk C line by line, and (when `run`) say what running it printed."""
    if not code_text.strip():
        return C.empty()
    try:
        rows, _n, _bad = _read_rows(code_text)
    except Exception:
        rows = []
    funcs = [m for m in re.findall(r"^[A-Za-z_][\w\s\*]*?\b(\w+)\s*\([^;{}]*\)\s*\{", code_text, re.M) if m not in ("if", "for", "while", "switch")]
    summary = f"This defines {C.join_names(funcs)}. Here's what each line does:" if funcs and funcs != ["main"] else "Here's what each line does:"
    notes: list[str] = []
    error_note = None
    if run:
        prog = c_program(code_text)
        if not prog.runnable:
            notes.append(prog.why_not)
        else:
            notes, error_note = C.run_notes("c", prog.text, prog.offset, "snippet.c")
    return C.finish(summary, rows, notes, error_note)
