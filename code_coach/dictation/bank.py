"""
Dictation line bank for Class 1 (type-along).

- Large pre-made pool
- On-the-fly variants from templates
- Keyboard / procedural tips
- Simple chatbot answers (local FAQ — no API key required)
"""

from __future__ import annotations

import hashlib
import random
import re
from dataclasses import dataclass
from typing import Callable


# ── Line completeness checks (same spirit as day01) ─────────


def _lines(code: str) -> list[str]:
    return [
        ln.strip()
        for ln in code.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def _quoted_ok(s: str) -> bool:
    s = s.strip()
    if len(s) < 3 or s[0] not in "\"'" or s[-1] != s[0]:
        return False
    return bool(s[1:-1])


def check_print_string(code: str) -> bool:
    for s in _lines(code):
        m = re.fullmatch(r"print\s*\((.*)\)\s*", s)
        if m and _quoted_ok(m.group(1)):
            return True
    return False


def check_str_assign(code: str, var: str) -> bool:
    for s in _lines(code):
        m = re.fullmatch(rf"{re.escape(var)}\s*=\s*(.+)", s)
        if m and _quoted_ok(m.group(1)):
            return True
    return False


def check_int_assign(code: str, var: str) -> bool:
    for s in _lines(code):
        if re.fullmatch(rf"{re.escape(var)}\s*=\s*(-?\d+)\s*", s):
            return True
    return False


def check_print_var(code: str, var: str) -> bool:
    for s in _lines(code):
        if re.fullmatch(rf"print\s*\(\s*{re.escape(var)}\s*\)\s*", s):
            return True
    return False


def check_print_two_args(code: str) -> bool:
    """print("age:", 30) style."""
    for s in _lines(code):
        if re.fullmatch(r'print\s*\(\s*["\'].*["\']\s*,\s*-?\d+\s*\)\s*', s):
            return True
    return False


def check_comment_then_print(code: str) -> bool:
    # any complete print string is enough; tip teaches comments separately
    return check_print_string(code)


def _code_lines(code: str) -> list[str]:
    """Non-empty, non-comment lines, stripped of trailing whitespace."""
    out: list[str] = []
    for ln in code.splitlines():
        s = ln.rstrip()
        if not s.strip() or s.strip().startswith("#"):
            continue
        out.append(s)
    return out


def check_block(code: str, expected: str) -> bool:
    """True when the expected block appears as consecutive typed lines."""
    exp = _code_lines(expected)
    if not exp:
        return False
    got = _code_lines(code)
    n = len(exp)
    for i in range(0, max(0, len(got) - n + 1)):
        window = got[i : i + n]
        if len(window) != n:
            continue
        if all(a.strip() == b.strip() for a, b in zip(window, exp)):
            return True
    return False


def make_block_check(expected: str) -> Callable[[str], bool]:
    def _check(code: str, exp: str = expected) -> bool:
        return check_block(code, exp)

    return _check


# Dictation difficulty (user-controlled; stay in endless mode):
#   1 = single easy lines
#   2 = single lines (broader)
#   3 = 2-line snippets
#   4 = short multi-line blocks
#   5 = functions / larger snippets
DICTATION_LEVEL_MIN = 1
DICTATION_LEVEL_MAX = 5
DICTATION_LEVEL_LABELS = {
    1: "Single lines",
    2: "Lines+",
    3: "Two-liners",
    4: "Blocks",
    5: "Functions",
}
# Small regenerable window — more batches load endlessly (not a fixed lesson size).
WINDOW_SIZE = 8


@dataclass
class LineSpec:
    """One dictation exercise (single line or multi-line block)."""

    id: str
    example: str  # may contain newlines
    check: Callable[[str], bool]
    tip: str  # procedural / concept tip
    keyboard_tip: str
    family: str  # print | assign_str | … | multi | function
    level: int = 1  # minimum dictation difficulty that includes this


# ── Keyboard tips (Mac — user is on MacBook / big TV) ───────

KEYBOARD_TIPS = [
    "End of line: ⌘ →  (Command + Right Arrow)",
    "Start of line: ⌘ ←  (Command + Left Arrow)",
    "Move down a line: ↓  (Down Arrow)",
    "Move up a line: ↑  (Up Arrow)",
    "Next word: ⌥ →  (Option + Right Arrow)",
    "Previous word: ⌥ ←  (Option + Left Arrow)",
    "New line: Return ⏎",
    "Delete left: Delete ⌫",
    "Select whole line: ⌘ ← then ⇧ ⌘ →",
    "Undo: ⌘ Z",
    "Run code: ⌘ ⏎  (Command + Enter)",
    "Jump to top of file: ⌘ ↑",
    "Jump to bottom of file: ⌘ ↓",
]


def _kb(i: int) -> str:
    return KEYBOARD_TIPS[i % len(KEYBOARD_TIPS)]


# ── Pre-made + template material ────────────────────────────

_PRINT_MSGS = [
    "Hello, world!",
    "hi",
    "Code Coach",
    "I am learning Python",
    "Day 01",
    "print shows text",
    "Hello from Omak",
    "ready",
    "typing practice",
    "keep going",
    "almost there",
    "nice work",
    "Python is fun",
    "variables store values",
    "quotes mean text",
]

_NAMES = ["Ada", "Sam", "Alex", "Jordan", "Riley", "Casey", "Morgan", "Quinn"]
_CITIES = ["Seattle", "Portland", "Spokane", "Tacoma", "Boise", "Bend", "Omak", "Yakima"]
_WORDS = ["score", "level", "lives", "points", "count", "total", "age", "year"]
_NUMS = [0, 1, 2, 3, 5, 7, 10, 12, 20, 42, 99]


def _pool_seed() -> list[LineSpec]:
    """Large static + combinatorial pool."""
    out: list[LineSpec] = []
    n = 0

    def add(
        family: str,
        example: str,
        tip: str,
    ) -> None:
        nonlocal n
        n += 1
        # Exact line match — so prior typed work does not auto-complete new targets
        out.append(
            LineSpec(
                id=f"c1-{family}-{n}",
                example=example,
                check=make_block_check(example),
                tip=tip,
                keyboard_tip=_kb(n),
                family=family,
            )
        )

    for msg in _PRINT_MSGS:
        add(
            "print",
            f'print("{msg}")',
            "print(...) shows text in the terminal. Text goes in quotes.",
        )

    for name in _NAMES:
        add(
            "assign_str",
            f'name = "{name}"',
            'name = "..." stores text. The name on the left is the variable.',
        )
        add(
            "print_var",
            "print(name)",
            "print(name) prints the value — no quotes around the variable name.",
        )

    for city in _CITIES:
        add(
            "assign_str",
            f'city = "{city}"',
            "Same idea as name: city holds a text value.",
        )
        add(
            "print_var",
            "print(city)",
            "print(city) — quotes would print the word city, not the value.",
        )

    for w, num in zip(_WORDS, _NUMS):
        add(
            "assign_int",
            f"{w} = {num}",
            f"Numbers usually have no quotes: {w} = {num}",
        )
        add(
            "print_var",
            f"print({w})",
            f"print({w}) shows the number stored in {w}.",
        )

    for msg, num in zip(_PRINT_MSGS[::2], _NUMS):
        add(
            "print_multi",
            f'print("{msg}", {num})',
            "print can take several things, separated by commas.",
        )

    # Classic day-01 spine first (always available) — exact match
    spine_lines = [
        ("spine-1", 'print("Hello, world!")', "print(...) shows text. Quotes mark a string.", "print"),
        ("spine-2", 'name = "Ada"', "A variable is a name that holds a value.", "assign_str"),
        ("spine-3", "print(name)", "No quotes around the variable when you want its value.", "print_var"),
        ("spine-4", 'city = "Seattle"', "You can have many variables at once.", "assign_str"),
        ("spine-5", "favorite_number = 7", "Whole numbers usually have no quotes.", "assign_int"),
        ("spine-6", "print(city)", "Same pattern as print(name).", "print_var"),
        ("spine-7", "print(favorite_number)", "print works for numbers too.", "print_var"),
    ]
    spine = [
        LineSpec(
            sid,
            ex,
            make_block_check(ex),
            tip,
            _kb(i),
            fam,
        )
        for i, (sid, ex, tip, fam) in enumerate(spine_lines)
    ]
    return spine + out


_POOL = _pool_seed()


def _rng(seed: str) -> random.Random:
    h = hashlib.sha256(seed.encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def generate_variant(rng: random.Random, level: int = 1) -> LineSpec:
    """On-the-fly exercise for the given dictation difficulty."""
    level = max(DICTATION_LEVEL_MIN, min(DICTATION_LEVEL_MAX, int(level)))
    kb = rng.choice(KEYBOARD_TIPS)
    rid = rng.randint(0, 1_000_000)

    # Level 1–2: single lines
    if level <= 2:
        kinds = ["print", "name", "city", "num"]
        if level >= 2:
            kinds.extend(["print_var_num", "multi", "print"])
        kind = rng.choice(kinds)
        if kind == "print":
            msg = rng.choice(_PRINT_MSGS + [f"line {rng.randint(1, 99)}"])
            ex = f'print("{msg}")'
            return LineSpec(
                id=f"gen-print-{rid}",
                example=ex,
                check=make_block_check(ex),
                tip="print(...) with text in quotes.",
                keyboard_tip=kb,
                family="print",
                level=1,
            )
        if kind == "name":
            name = rng.choice(_NAMES)
            ex = f'name = "{name}"'
            return LineSpec(
                id=f"gen-name-{rid}",
                example=ex,
                check=make_block_check(ex),
                tip='Store text: name = "..."',
                keyboard_tip=kb,
                family="assign_str",
                level=1,
            )
        if kind == "city":
            city = rng.choice(_CITIES)
            ex = f'city = "{city}"'
            return LineSpec(
                id=f"gen-city-{rid}",
                example=ex,
                check=make_block_check(ex),
                tip='city = "..." is another string variable.',
                keyboard_tip=kb,
                family="assign_str",
                level=1,
            )
        if kind == "num":
            w = rng.choice(_WORDS)
            num = rng.choice(_NUMS)
            ex = f"{w} = {num}"
            return LineSpec(
                id=f"gen-num-{rid}",
                example=ex,
                check=make_block_check(ex),
                tip=f"Number variable: {w} = {num} (no quotes).",
                keyboard_tip=kb,
                family="assign_int",
                level=1,
            )
        if kind == "print_var_num":
            w = rng.choice(_WORDS)
            ex = f"print({w})"
            return LineSpec(
                id=f"gen-pv-{rid}",
                example=ex,
                check=make_block_check(ex),
                tip=f"print({w}) prints whatever is stored in {w}.",
                keyboard_tip=kb,
                family="print_var",
                level=2,
            )
        msg = rng.choice(_PRINT_MSGS)
        num = rng.choice(_NUMS)
        ex = f'print("{msg}", {num})'
        return LineSpec(
            id=f"gen-multi-{rid}",
            example=ex,
            check=make_block_check(ex),
            tip="Comma separates multiple things in print.",
            keyboard_tip=kb,
            family="print_multi",
            level=2,
        )

    # Level 3: two-liners
    if level == 3:
        name = rng.choice(_NAMES)
        city = rng.choice(_CITIES)
        w = rng.choice(_WORDS)
        num = rng.choice(_NUMS)
        msg = rng.choice(_PRINT_MSGS)
        pick = rng.choice(["name_print", "city_print", "num_print", "two_print"])
        if pick == "name_print":
            ex = f'name = "{name}"\nprint(name)'
        elif pick == "city_print":
            ex = f'city = "{city}"\nprint(city)'
        elif pick == "num_print":
            ex = f"{w} = {num}\nprint({w})"
        else:
            ex = f'print("{msg}")\nprint({num})'
        return LineSpec(
            id=f"gen-2line-{rid}",
            example=ex,
            check=make_block_check(ex),
            tip="Two lines in a row — finish line 1, then ↓ for line 2.",
            keyboard_tip="↓ next line · ⌘ → end of line",
            family="multi",
            level=3,
        )

    # Level 4: short blocks (3–4 lines)
    if level == 4:
        name = rng.choice(_NAMES)
        w = rng.choice(_WORDS)
        num = rng.choice(_NUMS)
        n = rng.randint(2, 4)
        pick = rng.choice(["intro", "if_block", "for_block", "while_block"])
        if pick == "intro":
            ex = (
                f'name = "{name}"\n'
                f"{w} = {num}\n"
                f"print(name)\n"
                f"print({w})"
            )
            tip = "Type the whole short program. Use ↓ between lines."
        elif pick == "if_block":
            ex = (
                f"{w} = {num}\n"
                f"if {w} > 0:\n"
                f'    print("ok")'
            )
            tip = "Indent the body under if with spaces (Tab or 4 spaces)."
        elif pick == "for_block":
            ex = (
                f"for i in range({n}):\n"
                f"    print(i)"
            )
            tip = "for + range, then an indented body."
        else:
            ex = (
                f"{w} = {n}\n"
                f"while {w} > 0:\n"
                f"    print({w})\n"
                f"    {w} = {w} - 1"
            )
            tip = "while needs a condition and something that eventually ends the loop."
        return LineSpec(
            id=f"gen-block-{rid}",
            example=ex,
            check=make_block_check(ex),
            tip=tip,
            keyboard_tip="↓ new line · Tab indent · ⌘ → end of line",
            family="block",
            level=4,
        )

    # Level 5: functions / larger snippets
    name = rng.choice(_NAMES)
    w = rng.choice(_WORDS)
    num = rng.choice(_NUMS)
    pick = rng.choice(["greet", "add", "double", "countdown", "hello_fn"])
    if pick == "greet":
        ex = (
            f"def greet():\n"
            f'    print("Hello, {name}!")\n'
            f"\n"
            f"greet()"
        )
        tip = "def names a function. Call it with greet()."
    elif pick == "add":
        a, b = num, rng.choice(_NUMS)
        ex = (
            f"def add(a, b):\n"
            f"    return a + b\n"
            f"\n"
            f"print(add({a}, {b}))"
        )
        tip = "Parameters go in the parentheses; return sends a value back."
    elif pick == "double":
        ex = (
            f"def double(n):\n"
            f"    return n * 2\n"
            f"\n"
            f"print(double({num}))"
        )
        tip = "A tiny function: take n, return n * 2."
    elif pick == "countdown":
        n = rng.randint(2, 4)
        ex = (
            f"def countdown(n):\n"
            f"    while n > 0:\n"
            f"        print(n)\n"
            f"        n = n - 1\n"
            f"\n"
            f"countdown({n})"
        )
        tip = "Function body can hold a whole loop."
    else:
        ex = (
            "def hello():\n"
            '    print("hi")\n'
            '    print("bye")\n'
            "\n"
            "hello()"
        )
        tip = "Multiple lines inside the function — keep them indented."
    return LineSpec(
        id=f"gen-fn-{rid}",
        example=ex,
        check=make_block_check(ex),
        tip=tip,
        keyboard_tip="Tab indent · ↓ next line · ⌘ → end of line",
        family="function",
        level=5,
    )


def build_dictation_steps(
    *,
    seed: str,
    count: int = 10,
    include_spine: bool = True,
    level: int = 1,
) -> list[LineSpec]:
    """
    Build a window of dictation exercises for Class 1 (endless mode).
    Difficulty (1–5) controls single lines → multi-line → functions.
    Batches keep coming; this is not a fixed 14-exercise lesson.
    """
    level = max(DICTATION_LEVEL_MIN, min(DICTATION_LEVEL_MAX, int(level)))
    rng = _rng(seed)
    chosen: list[LineSpec] = []

    # Spine only on first batch at easy levels (warm-up single lines)
    if include_spine and level <= 2:
        spine = [s for s in _POOL if s.id.startswith("spine-")]
        chosen.extend(spine)

    if level <= 2:
        rest = [s for s in _POOL if not s.id.startswith("spine-")]
        rng.shuffle(rest)
        for s in rest:
            if len(chosen) >= count:
                break
            if any(c.example == s.example for c in chosen):
                continue
            chosen.append(s)

    # Fill / full content from generators (unique examples)
    safety = 0
    while len(chosen) < count and safety < count * 40:
        safety += 1
        v = generate_variant(rng, level=level)
        if any(c.example == v.example for c in chosen):
            continue
        chosen.append(v)

    return chosen[:count]


def tip_for_step(spec: LineSpec) -> dict[str, str]:
    return {
        "tip": spec.tip,
        "keyboard_tip": spec.keyboard_tip,
    }


# ── Per-class endless dictation (Decisions, Loops) ──────────
# Every class's Lesson 1 is an infinite verbatim type-along drilling the
# EXACT syntax that class's build lessons will need — parentheses, quotes,
# colons, comparison signs — so the fingers learn each detail first.

_CMP_OPS = [">", "<", ">=", "<=", "==", "!="]
_CMP_WORDS = {
    ">": "greater than",
    "<": "less than",
    ">=": "at least",
    "<=": "at most",
    "==": "equal to",
    "!=": "not equal to",
}
_INT_VARS = ["x", "n", "age", "score", "count", "limit", "temp"]
_BOOL_VARS = ["has_ticket", "is_ready", "is_open", "done", "passed"]
_SHORT_MSGS = ["ok", "yes", "no", "ready", "go", "win", "high", "low", "stop"]


def _spec(sid: str, ex: str, tip: str, family: str, level: int, kb: str) -> LineSpec:
    return LineSpec(
        id=sid,
        example=ex,
        check=make_block_check(ex),
        tip=tip,
        keyboard_tip=kb,
        family=family,
        level=level,
    )


# Curated warm-up window (batch 0, easy levels) — the class's core sequence.
_DECISIONS_SPINE: list[tuple[str, str, str]] = [
    ("x = 5", "Set up a number to test.", "assign_int"),
    ('if x > 0:\n    print("ok")', "if runs a block only when the condition is true. Indent the body.", "if"),
    ("n = 7", "Another number for even/odd.", "assign_int"),
    ('if n % 2 == 0:\n    print("even")\nelse:\n    print("odd")', "else covers the other case. % is remainder.", "if_else"),
    ("age = 20", "age for a compound check.", "assign_int"),
    ("has_ticket = True", "True / False are booleans (no quotes).", "bool"),
    ('if age >= 18 and has_ticket:\n    print("ready")', "and requires both sides true.", "and"),
]

_LOOPS_SPINE: list[tuple[str, str, str]] = [
    ("for i in range(3):\n    print(i)", "for repeats for each item in range.", "for"),
    ("n = 3", "Countdown start value.", "assign_int"),
    ("while n > 0:\n    print(n)\n    n = n - 1", "while repeats until the condition is false.", "while"),
    ("total = 0", "Running total starts at 0.", "assign_int"),
    ("for i in range(1, 6):\n    total = total + i\nprint(total)", "Accumulate pattern: update total each loop.", "accumulate"),
]


def _gen_decisions(rng: random.Random, level: int) -> LineSpec:
    """Endless Decisions material: comparisons, booleans, if / elif / else."""
    level = max(DICTATION_LEVEL_MIN, min(DICTATION_LEVEL_MAX, int(level)))
    kb = rng.choice(KEYBOARD_TIPS)
    rid = rng.randint(0, 1_000_000)
    v = rng.choice(_INT_VARS)
    b = rng.choice(_BOOL_VARS)
    op = rng.choice(_CMP_OPS)
    num = rng.choice(_NUMS)
    msg = rng.choice(_SHORT_MSGS)

    # Levels 1–2: single lines — assigns, booleans, comparison prints
    if level <= 2:
        kinds = ["assign", "bool", "cmp_print"]
        if level >= 2:
            kinds.extend(["cmp_assign", "not_print"])
        kind = rng.choice(kinds)
        if kind == "assign":
            ex = f"{v} = {num}"
            return _spec(f"gen-dec-a-{rid}", ex, f"A number to test: {ex}", "assign_int", 1, kb)
        if kind == "bool":
            ex = f"{b} = {rng.choice(['True', 'False'])}"
            return _spec(f"gen-dec-b-{rid}", ex, "Booleans are True or False — capital letter, no quotes.", "bool", 1, kb)
        if kind == "cmp_print":
            ex = f"print({v} {op} {num})"
            return _spec(
                f"gen-dec-c-{rid}", ex,
                f"{op} asks: is {v} {_CMP_WORDS[op]} {num}? Prints True or False.",
                "compare", 1, kb,
            )
        if kind == "cmp_assign":
            ex = f"{b} = {v} {op} {num}"
            return _spec(
                f"gen-dec-d-{rid}", ex,
                "A comparison's True/False answer can be stored in a variable.",
                "compare", 2, kb,
            )
        ex = f"print(not {b})"
        return _spec(f"gen-dec-e-{rid}", ex, "not flips True to False and back.", "bool", 2, kb)

    # Level 3: two-line if blocks
    if level == 3:
        ex = f'if {v} {op} {num}:\n    print("{msg}")'
        return _spec(
            f"gen-dec-if-{rid}", ex,
            "Colon ends the if line; the body is indented 4 spaces.",
            "if", 3, "↓ next line · Tab indent",
        )

    # Level 4: if/else blocks and compound conditions
    if level == 4:
        pick = rng.choice(["if_else", "and_block", "or_block"])
        if pick == "if_else":
            m2 = rng.choice([m for m in _SHORT_MSGS if m != msg] or _SHORT_MSGS)
            ex = (
                f"if {v} {op} {num}:\n"
                f'    print("{msg}")\n'
                f"else:\n"
                f'    print("{m2}")'
            )
            tip = "else lines up with if — no condition, just a colon."
        elif pick == "and_block":
            n2 = rng.choice(_NUMS)
            ex = (
                f"if {v} >= {min(num, n2)} and {b}:\n"
                f'    print("{msg}")'
            )
            tip = "and requires both sides true."
        else:
            ex = (
                f"if {v} < {num} or {b}:\n"
                f'    print("{msg}")'
            )
            tip = "or needs just one side true."
        return _spec(f"gen-dec-blk-{rid}", ex, tip, "if_else", 4, "↓ · Tab indent")

    # Level 5: elif chains
    lo, hi = sorted((rng.choice(_NUMS), rng.choice(_NUMS) + 1))
    ex = (
        f"if {v} > {hi}:\n"
        f'    print("high")\n'
        f"elif {v} > {lo}:\n"
        f'    print("mid")\n'
        f"else:\n"
        f'    print("low")'
    )
    return _spec(
        f"gen-dec-elif-{rid}", ex,
        "elif = another check, only tried when the ones above were false.",
        "elif", 5, "↓ · Tab indent · ⌘ → end of line",
    )


def _gen_loops(rng: random.Random, level: int) -> LineSpec:
    """Endless Loops material: for, while, range, accumulate, loop functions."""
    level = max(DICTATION_LEVEL_MIN, min(DICTATION_LEVEL_MAX, int(level)))
    kb = rng.choice(KEYBOARD_TIPS)
    rid = rng.randint(0, 1_000_000)
    v = rng.choice(_INT_VARS)
    n = rng.randint(2, 6)
    msg = rng.choice(_SHORT_MSGS)

    # Levels 1–2: single lines — loop setup values and one-line loops
    if level <= 2:
        kinds = ["seed_var", "oneline_for"]
        if level >= 2:
            kinds.extend(["oneline_msg", "range_two"])
        kind = rng.choice(kinds)
        if kind == "seed_var":
            ex = f"{v} = {n}"
            return _spec(f"gen-lp-a-{rid}", ex, "A starting value the loop will use.", "assign_int", 1, kb)
        if kind == "oneline_for":
            ex = f"for i in range({n}): print(i)"
            return _spec(
                f"gen-lp-b-{rid}", ex,
                f"One-line loop: prints 0 up to {n - 1}.",
                "for", 1, kb,
            )
        if kind == "oneline_msg":
            ex = f'for i in range({n}): print("{msg}")'
            return _spec(
                f"gen-lp-c-{rid}", ex,
                f"Repeats the same message {n} times.",
                "for", 2, kb,
            )
        a = rng.randint(1, 3)
        ex = f"for i in range({a}, {a + n}): print(i)"
        return _spec(
            f"gen-lp-d-{rid}", ex,
            f"range({a}, {a + n}) starts at {a} and stops before {a + n}.",
            "for", 2, kb,
        )

    # Level 3: two-line for blocks
    if level == 3:
        pick = rng.choice(["print_i", "print_msg"])
        body = "print(i)" if pick == "print_i" else f'print("{msg}", i)'
        ex = f"for i in range({n}):\n    {body}"
        return _spec(
            f"gen-lp-for-{rid}", ex,
            "for + range, then an indented body.",
            "for", 3, "↓ next line · Tab indent",
        )

    # Level 4: while countdown / accumulate blocks
    if level == 4:
        pick = rng.choice(["countdown", "accumulate", "step_range"])
        if pick == "countdown":
            ex = (
                f"{v} = {n}\n"
                f"while {v} > 0:\n"
                f"    print({v})\n"
                f"    {v} = {v} - 1"
            )
            tip = "The loop needs a line that moves it toward the end."
        elif pick == "accumulate":
            ex = (
                f"total = 0\n"
                f"for i in range(1, {n + 1}):\n"
                f"    total = total + i\n"
                f"print(total)"
            )
            tip = "Accumulate: update total inside, print once after."
        else:
            ex = (
                f"for i in range(0, {2 * n}, 2):\n"
                f"    print(i)"
            )
            tip = "The third range number is the step — count by 2s."
        return _spec(f"gen-lp-blk-{rid}", ex, tip, "while", 4, "↓ · Tab indent")

    # Level 5: functions that loop / nested loops
    pick = rng.choice(["sum_fn", "countdown_fn", "grid"])
    if pick == "sum_fn":
        ex = (
            "def sum_list(xs):\n"
            "    total = 0\n"
            "    for x in xs:\n"
            "        total = total + x\n"
            "    return total\n"
            "\n"
            f"print(sum_list([1, 2, {n}]))"
        )
        tip = "A function that loops: accumulate inside, return the result."
    elif pick == "countdown_fn":
        ex = (
            "def countdown(n):\n"
            "    while n > 0:\n"
            "        print(n)\n"
            "        n = n - 1\n"
            "\n"
            f"countdown({n})"
        )
        tip = "Function body can hold a whole loop."
    else:
        m = rng.randint(2, 3)
        ex = (
            f"for r in range({m}):\n"
            f"    for c in range({m}):\n"
            f"        print(r, c)"
        )
        tip = "Nested: the inner loop runs fully for each outer pass."
    return _spec(
        f"gen-lp-fn-{rid}", ex, tip, "function", 5,
        "Tab indent · ↓ next line · ⌘ → end of line",
    )


_CLASS_GENERATORS = {
    "decisions": _gen_decisions,
    "loops": _gen_loops,
}

_CLASS_SPINES = {
    "decisions": _DECISIONS_SPINE,
    "loops": _LOOPS_SPINE,
}


def build_class_dictation_steps(
    class_id: str,
    *,
    seed: str,
    count: int = WINDOW_SIZE,
    include_spine: bool = True,
    level: int = 1,
) -> list[LineSpec]:
    """Endless dictation window for any class. Foundations keeps its original
    pool; other classes use their own generators + curated spine."""
    if class_id not in _CLASS_GENERATORS:
        return build_dictation_steps(
            seed=seed, count=count, include_spine=include_spine, level=level
        )

    level = max(DICTATION_LEVEL_MIN, min(DICTATION_LEVEL_MAX, int(level)))
    rng = _rng(f"{class_id}:{seed}")
    gen = _CLASS_GENERATORS[class_id]
    chosen: list[LineSpec] = []

    if include_spine and level <= 2:
        spine = _CLASS_SPINES.get(class_id, [])
        for i, (ex, tip, family) in enumerate(spine):
            chosen.append(
                _spec(f"{class_id}-spine-{i + 1}", ex, tip, family, 1, _kb(i))
            )

    safety = 0
    while len(chosen) < count and safety < count * 40:
        safety += 1
        v = gen(rng, level)
        if any(c.example == v.example for c in chosen):
            continue
        chosen.append(v)

    return chosen[:count]


# ── Simple chatbot (FAQ + keyboard) ─────────────────────────

_FAQ: list[tuple[list[str], str]] = [
    (
        [
            "end of line",
            "end of the line",
            "end of a line",
            "to the end",
            "go to end",
            "move to end",
            "eol",
            "cursor to end",
        ],
        "On a Mac: press ⌘ → (Command + Right Arrow) to jump to the end of the line. "
        "Start of line: ⌘ ←.",
    ),
    (
        ["start of line", "beginning of line", "home", "start of the line"],
        "Jump to the start of the line with ⌘ ← (Command + Left Arrow).",
    ),
    (
        ["move down", "down a line", "go down", "down arrow"],
        "Press the Down Arrow ↓ to move the cursor down one line. "
        "Up Arrow ↑ moves up. Return ⏎ makes a new line.",
    ),
    (
        ["move up", "previous line", "go up"],
        "Press the Up Arrow ↑ to move up one line.",
    ),
    (
        ["how do i run", "run code", "execute"],
        "Press ⌘ ⏎ (Command + Enter), or click Run. Output shows in the Terminal below.",
    ),
    (
        ["what is a variable", "variable"],
        'A variable is a name that holds a value, e.g. name = "Ada". '
        "Later print(name) shows what you stored.",
    ),
    (
        ["what is print", "how does print"],
        'print(...) shows values in the terminal. Text uses quotes: print("hi").',
    ),
    (
        ["quotes", "string"],
        'Text (a string) goes in quotes: "hello" or \'hello\'. Numbers usually do not: 7 not "7".',
    ),
    (
        ["undo"],
        "Undo with ⌘ Z. Redo is ⇧ ⌘ Z.",
    ),
    (
        ["help", "what do i do", "stuck"],
        "Type the exact line in the blue/cyan box into the editor under it. "
        "When it says Got it, press Enter or Next line. Ask me keyboard tips anytime.",
    ),
]


def chat_reply(message: str) -> str:
    q = message.strip().lower()
    if not q:
        return "Ask me anything about the editor keys or this Python line."
    for keys, answer in _FAQ:
        if any(k in q for k in keys):
            return answer
    # fuzzy keyboard
    if "keyboard" in q or "key" in q or "shortcut" in q:
        return "Useful keys: ⌘ → end of line · ⌘ ← start · ↓ next line · ⌘ ⏎ run · ⌘ Z undo."
    if "line" in q and ("move" in q or "go" in q or "how" in q):
        return "↓ moves down a line. ⌘ → jumps to the end of the current line."
    return (
        "I’m the tips bot (no cloud AI required yet). Try asking:\n"
        "• how do I move to the end of a line?\n"
        "• how do I move down a line?\n"
        "• what is a variable?\n"
        "• how do I run?"
    )
