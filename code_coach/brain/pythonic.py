"""Brain Drills in Python: the same seven activities, with Python's rules.

Each answer is worked out here by modelling what Python does - spelled out
by hand (floor division as a counting loop, a string repeated by joining,
round() as round-half-to-even) rather than by asking Python - and
tests/test_brain_python.py then runs every template through the real
interpreter to hold the model to the real thing (the oracle rule).
"""

from __future__ import annotations

import math
import random
from string import Template

from .items import Item

_WORDS = ("farm", "drone", "carrot", "loop", "code", "pumpkin", "array", "key", "grid", "tree")


def _floor_div(a: int, b: int) -> int:
    """a // b for positive a and b, by counting."""
    q = 0
    while (q + 1) * b <= a:
        q += 1
    return q


def _repeat(text: str, n: int) -> str:
    return "".join(text for _ in range(n))


def _reverse(text: str) -> str:
    return "".join(text[len(text) - 1 - i] for i in range(len(text)))


def _upper(text: str) -> str:
    return "".join(chr(ord(ch) - 32) if "a" <= ch <= "z" else ch for ch in text)


def _contains(text: str, sub: str) -> bool:
    return any(text[i:i + len(sub)] == sub for i in range(len(text) - len(sub) + 1))


def _round_half_even(k: int) -> int:
    """round(k + 0.5): halves go to the even neighbour."""
    return k if k % 2 == 0 else k + 1


def _tf(x: bool) -> str:
    return "True" if x else "False"


# ── 1. Quick Eval ───────────────────────────────────────────────────────

#: (expression, what print shows, why) for bool(...) of a value.
_BOOLS = (
    ('""', False, "The empty string is falsy."),
    ('"0"', True, "A non-empty string is truthy - even \"0\"."),
    ("[]", False, "An empty list is falsy (unlike JavaScript)."),
    ("[0]", True, "A list with anything in it is truthy."),
    ("0.0", False, "0.0 is zero: falsy."),
    ("None", False, "None is falsy."),
    ("{}", False, "An empty dict is falsy."),
    ("()", False, "An empty tuple is falsy."),
    ('" "', True, "A space is still a character: truthy."),
    ('"False"', True, "A non-empty string, whatever it says: truthy."),
)

_TYPES = (
    ("{a}", "int"), ('"{word}"', "str"), ("{a}.5", "float"), ("True", "bool"),
    ("None", "NoneType"), ("[{a}]", "list"), ("{{}}", "dict"), ("({a}, {a})", "tuple"),
)


def quick_eval(rng: random.Random) -> Item:
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
    word = rng.choice(_WORDS)
    kind = rng.randrange(30)
    if kind == 0:
        return Item(f"{a} + {b} * {c}", str(a + b * c), "* happens before +.")
    if kind == 1:
        return Item(f"({a} + {b}) * {c}", str((a + b) * c), "The brackets go first.")
    if kind == 2:
        big = rng.randint(10, 40)
        return Item(f"{big} % {b}", str(big - b * _floor_div(big, b)),
                    f"% is the remainder after dividing by {b}.")
    if kind == 3:
        p = rng.choice((2, 3))
        value = 1
        for _ in range(p):
            value *= a
        return Item(f"{a} ** {p}", str(value), "** is a power: a times itself.")
    if kind == 4:
        big = rng.randint(10, 60)
        return Item(f"{big} // {b}", str(_floor_div(big, b)), "// divides and rounds down to a whole number.")
    if kind == 5:
        return Item(f"{a * b} / {b}", f"{a}.0", "/ always gives a float in Python, even when it divides exactly.")
    if kind == 6:
        k = rng.randint(1, 9)
        return Item(f"{2 * k + 1} / 2", f"{k}.5", "/ is true division: it keeps the fraction.")
    if kind == 7:
        big = b * rng.randint(1, 6) + rng.randint(1, b - 1)
        return Item(f"-{big} // {b}", str(-(_floor_div(big, b) + 1)),
                    "// rounds down toward minus infinity, so a negative result goes further from 0.")
    if kind == 8:
        big = b * rng.randint(1, 6) + rng.randint(1, b - 1)
        return Item(f"-{big} % {b}", str(b - (big - b * _floor_div(big, b))),
                    f"A % result takes the sign of the right side: it lands from 0 to {b - 1}.")
    if kind == 9:
        return Item(f'"{a}" * {b}', _repeat(str(a), b), "A string times a number repeats it; nothing is multiplied.")
    if kind == 10:
        n = rng.randint(2, 3)
        return Item(f'"{word}" * {n}', _repeat(word, n), "Repeats the string.")
    if kind == 11:
        return Item(f'"{word}" + str({a})', f"{word}{a}", "str() turns the number into text, and + joins.")
    if kind == 12:
        return Item(f"str({a}) + str({b})", f"{a}{b}", "Both are strings by then: + joins them.")
    if kind == 13:
        n = rng.randint(2, 3)
        shown = ", ".join([str(a)] * n + [str(b)])
        return Item(f"[{a}] * {n} + [{b}]", f"[{shown}]", "A list times a number repeats it; + joins two lists.")
    if kind == 14:
        n = rng.randint(2, 6)
        items = ", ".join(str(rng.randint(0, 9)) for _ in range(n))
        return Item(f"len([{items}])", str(n), "len counts the items.")
    if kind == 15:
        return Item(f'len("{word}")', str(len(word)), "len counts the characters.")
    if kind == 16:
        return Item(f"max({a}, {b}, {c})", str(max(a, b, c)), "The largest.")
    if kind == 17:
        return Item(f"min({a}, {b}, {c})", str(min(a, b, c)), "The smallest.")
    if kind == 18:
        return Item(f'{a} == "{a}"', "False", "Python never converts: a number does not equal a string.")
    if kind == 19:
        return Item(f"{a} == {a}.0", "True", "An int and a float compare by value.")
    if kind == 20:
        return Item(f"[{a}, {b}, {c}][-1]", str(c), "-1 counts from the end: the last item.")
    if kind == 21:
        i = rng.choice((0, -1))
        return Item(f'"{word}"[{i}]', word[i], "Index 0 is the first character; -1 is the last.")
    if kind == 22:
        return Item(f'"{word}"[::-1]', _reverse(word), "A step of -1 walks the string backwards.")
    if kind == 23:
        value, answer = rng.choice(_TYPES)
        return Item(f"type({value.format(a=a, word=word)}).__name__", answer, "")
    if kind == 24:
        value, truthy, why = rng.choice(_BOOLS)
        return Item(f"bool({value})", _tf(truthy), why)
    if kind == 25:
        k = rng.randint(0, 9)
        return Item(f"round({k}.5)", str(_round_half_even(k)),
                    "round() sends an exact half to the even neighbour, not always up.")
    if kind == 26:
        sub = rng.choice((word[:2], word[1:3], word[-2:], rng.choice("xyzq"), word[0]))
        text = word if rng.random() < 0.5 else rng.choice(_WORDS)
        return Item(f'"{sub}" in "{text}"', _tf(_contains(text, sub)), "in on strings looks for that run of characters.")
    if kind == 27:
        big = rng.randint(10, 60)
        return Item(f"{big} // {b}.0", f"{_floor_div(big, b)}.0", "// with a float still rounds down, but the result is a float.")
    if kind == 28:
        return Item(f"True + {a}", str(a + 1), "True is 1 when you do arithmetic.")
    if kind == 29:
        if rng.random() < 0.5:
            return Item(f"{a} < {b} < {c}", _tf(a < b and b < c), "A chain means both comparisons: a < b and b < c.")
        return Item(f'"{word}".upper()', _upper(word), "upper() makes capitals.")
    raise AssertionError(kind)


# ── 2. Truthy or Falsy ──────────────────────────────────────────────────

#: (Python value, truthy?, why).
TRUTHY = (
    ("0", False, "0 is falsy."),
    ("1", True, "Every number but 0 is truthy."),
    ("-1", True, "Negative numbers are truthy."),
    ("0.0", False, "0.0 is zero: falsy."),
    ("-0.0", False, "-0.0 is still zero: falsy."),
    ('""', False, "The empty string is falsy."),
    ('" "', True, "A space is still a character: truthy."),
    ('"0"', True, "A non-empty string is truthy - even \"0\"."),
    ('"False"', True, "It's a non-empty string, so truthy."),
    ('"None"', True, "A non-empty string - truthy."),
    ("[]", False, "An empty list is falsy (not like JavaScript)."),
    ("[0]", True, "A list with anything in it is truthy."),
    ("[[]]", True, "One item, even if that item is empty: truthy."),
    ("{}", False, "An empty dict is falsy."),
    ("{0: 0}", True, "A dict with an entry is truthy."),
    ("()", False, "An empty tuple is falsy."),
    ("(0,)", True, "A tuple with one item is truthy."),
    ("set()", False, "An empty set is falsy."),
    ("None", False, "None is falsy."),
    ("False", False, "False is falsy."),
    ("True", True, "True is truthy."),
    ("0.5", True, "Not 0: truthy."),
    ("range(0)", False, "An empty range is falsy."),
    ('float("nan")', True, "nan is not zero, so truthy (JavaScript's NaN is falsy; Python's is not)."),
    ("lambda: 0", True, "Functions are truthy."),
)


def truthy(rng: random.Random) -> Item:
    value, ok, why = rng.choice(TRUTHY)
    return Item(value, "truthy" if ok else "falsy", why, check=f"bool({value})")


# ── 3. Loop Count ───────────────────────────────────────────────────────

def _ceil_div(a: int, b: int) -> int:
    return math.ceil(a / b)


def loop_count(rng: random.Random) -> Item:
    kind = rng.randrange(10)
    setup = ""
    while_body = ""
    if kind == 0:
        a, b, s = rng.randint(0, 5), rng.randint(6, 20), rng.randint(2, 4)
        head, n = f"for i in range({a}, {b}, {s}):", _ceil_div(b - a, s)
        why = f"i takes {n} values: {a}, {a + s}, ... stopping before {b}."
    elif kind == 1:
        b = rng.randint(3, 12)
        head, n = f"for i in range({b}):", b
        why = f"range({b}) is 0 up to {b - 1}: {b} values."
    elif kind == 2:
        a, b = rng.randint(1, 5), rng.randint(7, 15)
        head, n = f"for i in range({a}, {b}):", b - a
        why = f"i runs from {a} up to {b - 1}, and {b} is left out."
    elif kind == 3:
        a, b, s = rng.randint(0, 5), rng.randint(8, 20), rng.randint(1, 4)
        head, n = f"for i in range({b}, {a}, -{s}):", _ceil_div(b - a, s)
        why = f"Counting down from {b} in steps of {s}, stopping before {a}."
    elif kind == 4:
        n0 = rng.choice((8, 16, 20, 32, 50, 64, 100))
        steps, v = 0, n0
        while v > 1:
            v = _floor_div(v, 2)
            steps += 1
        setup, head, n = f"n = {n0}\n", "while n > 1:", steps
        while_body = "    n //= 2"
        why = "Each turn halves n; count the halvings until it reaches 1."
    elif kind == 5:
        limit = rng.choice((10, 20, 50, 100, 64))
        n, i = 0, 1
        while i < limit:
            n += 1
            i *= 2
        setup, head = "i = 1\n", f"while i < {limit}:"
        while_body = "    i *= 2"
        why = "i doubles: 1, 2, 4, 8 ... count the ones below the limit."
    elif kind == 6:
        a = rng.randint(3, 9)
        head, n = f"for i in range({a}, {a}):", 0
        why = "i starts where it must stop, so the body never runs."
    elif kind == 7:
        word = rng.choice(_WORDS)
        head, n = f'for ch in "{word}":', len(word)
        why = "One turn per character."
    elif kind == 8:
        b = rng.randint(3, 12)
        head, n = f"for i in range(1, {b} + 1):", b
        why = f"The stop is {b + 1}, which is left out: 1 to {b}."
    else:
        b, s = rng.randint(8, 30), rng.randint(2, 5)
        setup, head, n = "i = 0\n", f"while i < {b}:", _ceil_div(b, s)
        while_body = f"    i += {s}"
        why = f"i goes 0, {s}, {2 * s} ... count the values below {b}."
    if while_body:
        shown = setup + head + "\n" + while_body
        check_body = while_body + "\n    count += 1"
    else:
        shown = setup + head + "\n    count += 1"
        check_body = "    count += 1"
    check = "count = 0\n" + setup + head + "\n" + check_body + "\ncount"
    return Item(shown, str(n), why, check=check)


# ── 4. Final Value ──────────────────────────────────────────────────────

def final_value(rng: random.Random) -> Item:
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 5)
    kind = rng.randrange(13)
    if kind == 0:
        code = f"x = {a}\nx += {b}\nx *= {c}"
        return Item(code, str((a + b) * c), "Step by step: add, then multiply.", check=code + "\nx")
    if kind == 1:
        code = f"x = {a}\ny = x\nx = {b}"
        return Item(code + "\n# y?", str(a), "y got a copy of the number; changing x later doesn't touch it.",
                    check=code + "\ny")
    if kind == 2:
        n = rng.randint(3, 8)
        code = f"x = 0\nfor i in range(1, {n + 1}):\n    x += i"
        return Item(code, str(n * (n + 1) // 2), f"1 + 2 + ... + {n}.", check=code + "\nx")
    if kind == 3:
        code = f"x = {a * b}\nx //= {c}\nx += 1"
        return Item(code, str(_floor_div(a * b, c) + 1), "// rounds down, then one is added.", check=code + "\nx")
    if kind == 4:
        code = f"x = [{a}, {b}]\nx.append({c})\nx = len(x)"
        return Item(code, "3", "append adds one: three items.", check=code + "\nx")
    if kind == 5:
        code = f"x = {a}\nif x > {b}:\n    x = x - {b}\nelse:\n    x = x + {b}"
        answer = a - b if a > b else a + b
        return Item(code, str(answer), f"{a} > {b} is {_tf(a > b)}.", check=code + "\nx")
    if kind == 6:
        code = 'x = "ab"\nx = x + x\nx = len(x)'
        return Item(code, "4", "\"abab\" has four characters.", check=code + "\nx")
    if kind == 7:
        code = f"x = {a}\ny = {b}\nx, y = y, x"
        return Item(code, str(b), "The swap trades the two values.", check=code + "\nx")
    if kind == 8:
        code = f"y = [{a}]\nx = y\ny.append({b})\nx = len(x)"
        return Item(code, "2", "x and y are the same list, so the append shows through x.", check=code + "\nx")
    if kind == 9:
        code = f"x = {a}\nx **= 2\nx -= {b}"
        return Item(code, str(a * a - b), "Square it, then take away.", check=code + "\nx")
    if kind == 10:
        n = rng.randint(4, 10)
        code = f"x = 0\nfor i in range({n}):\n    if i % 2 == 0:\n        x += i"
        return Item(code, str(sum(i for i in range(n) if i - 2 * _floor_div(i, 2) == 0)),
                    f"Only the even i below {n} are added.", check=code + "\nx")
    if kind == 11:
        code = f'x = "ab" * {c}\nx = len(x)'
        return Item(code, str(2 * c), "The string repeats, then len counts it.", check=code + "\nx")
    code = f"x = {a}\nx = -x // 2"
    return Item(code, str(-(_floor_div(a, 2) + (a % 2))), "-x is negative first, and // rounds down.", check=code + "\nx")


# ── 5. Bracket Check ────────────────────────────────────────────────────

_PAIRS = {"(": ")", "[": "]", "{": "}"}

_NAMES = ("x", "y", "z", "data", "pts", "d", "total", "names", "grid", "box")

#: Real Python lines whose only brackets are syntax (or an f-string's {}).
_BRACKET_TEMPLATES = (
    "$x = {$n: [$m, ($n, $m)]}",
    'print(f"{$x}: {len($y)}")',
    "$x = {$n, $m, ($n + $m)}",
    "$x = [$y[$n] for $y in ($z, ($m,))]",
    "$x = dict([($n, [$m]), ($m, {$n})])",
    "$x = {k: ($n * k) for k in range($m)}",
    "print(len({$n: [$m]}) + sum([$n, ($m)]))",
    'print(f"{($n + $m) * $n}")',
    "$x = [($n, {$m}), ($m, {$n})]",
    "$x = {$n: {$m: [$n]}}",
    "$x = sorted({$n, $m})[$n]",
    'print(f"{$x[0]} and {$y[($n)]}")',
)


def balanced(text: str) -> bool:
    stack: list[str] = []
    for ch in text:
        if ch in _PAIRS:
            stack.append(_PAIRS[ch])
        elif ch in ")]}":
            if not stack or stack.pop() != ch:
                return False
    return not stack


def bracket_check(rng: random.Random) -> Item:
    names = rng.sample(_NAMES, 3)
    text = Template(rng.choice(_BRACKET_TEMPLATES)).substitute(
        x=names[0], y=names[1], z=names[2], n=rng.randint(1, 9), m=rng.randint(1, 9))
    if rng.random() < 0.5:
        for _ in range(8):
            chars = list(text)
            spots = [k for k, ch in enumerate(chars) if ch in "([{)]}"]
            how = rng.randrange(3)
            if how == 0:  # one closer becomes the wrong kind
                i = rng.choice([k for k in spots if chars[k] in ")]}"])
                chars[i] = rng.choice([c for c in ")]}" if c != chars[i]])
            elif how == 1:  # one bracket goes missing
                del chars[rng.choice(spots)]
            else:  # two neighbouring brackets swap
                pairs = [k for k in spots if k + 1 in spots]
                if not pairs:
                    continue
                i = rng.choice(pairs)
                chars[i], chars[i + 1] = chars[i + 1], chars[i]
            if not balanced("".join(chars)):
                text = "".join(chars)
                break
        else:
            text = text.replace("(", "", 1) if "(" in text else text[:-1]
    ok = balanced(text)
    return Item(text, "yes" if ok else "no",
                "Every opener closes, innermost first." if ok else "Something closes the wrong one, or never closes.")


# ── 6. Variable Recall ──────────────────────────────────────────────────

def recall(rng: random.Random) -> Item:
    n = rng.randint(3, 5)
    names = rng.sample("abcdefghkmnpqrstwxyz", n)
    values = [rng.randint(0, 20) for _ in names]
    shown = "\n".join(f"{k} = {v}" for k, v in zip(names, values))
    ask = rng.randrange(n)
    return Item(f"{names[ask]}?", str(values[ask]), shown.replace("\n", "  "), show=shown)


# ── 7. Syntax Snap ──────────────────────────────────────────────────────

#: (line, valid Python?, why). Every line is held to compile() by the tests.
SYNTAX = (
    ("x = 5", True, ""),
    ("x == = 3", False, "== is one operator; there's a stray =."),
    ("2x = 1", False, "A name can't start with a digit."),
    ("x2 = 1", True, "Digits are fine after the first character."),
    ("if x > 3: x -= 1", True, ""),
    ("if x > 3 x -= 1", False, "An if needs a : after its condition."),
    ("if (x > 3) { x -= 1 }", False, "Python uses : and indentation, not braces."),
    ("if x = 3: pass", False, "A condition compares with ==; a single = assigns."),
    ("for i in range(3): pass", True, ""),
    ("for i in range(3) pass", False, "A for needs a : before its body."),
    ("def add(a, b): return a + b", True, ""),
    ("def add(a, b) return a + b", False, "A def needs a : before its body."),
    ("add = lambda a, b: a + b", True, ""),
    ("add = lambda a, b -> a + b", False, "A lambda uses :, not an arrow."),
    ('print(f"total: {3 + 4}")', True, ""),
    ('print(f"total: {3 + 4")', False, "The { in the f-string never closes."),
    ("x = [1, 2, 3,]", True, "A trailing comma in a list is allowed."),
    ('d = {"a": 1, "b": 2}', True, ""),
    ("d = {1: 2, 3}", False, "A dict needs a value for every key."),
    ("s = {1, 2, 3}", True, "Braces with no colons make a set."),
    ("a, b = 1, 2", True, ""),
    ("a, b = 1, 2,,", False, "Two commas in a row."),
    ("while True: break", True, ""),
    ("while True do: pass", False, "Python has no do."),
    ("x = 1 if y else 2", True, "A conditional expression."),
    ("x = y ? 1 : 2", False, "Python has no ?: - it's 1 if y else 2."),
    ('print("it\'s")', True, "Double quotes can hold a '."),
    ("x = 'it's'", False, "The ' inside ends the string early."),
    ('print "hi"', False, "print is a function in Python 3: it needs brackets."),
    ("x++", False, "Python has no ++; write x += 1."),
    ("let x = 5", False, "Python has no let - just write x = 5."),
    ("x = 0xFF", True, "0x starts a hexadecimal number."),
    ("x = 08", False, "A number can't have a leading zero."),
    ("x = 1_000_000", True, "Underscores can separate digits."),
    ("try:\n    pass\nfinally:\n    pass", True, "try needs an except or a finally - this has one."),
    ("try:\n    pass", False, "try needs an except or a finally."),
    ("else: x = 1", False, "An else needs an if before it."),
    ("else if x: pass", False, "Python's word is elif."),
    ("return 5", False, "return only works inside a function."),
    ("break", False, "break only works inside a loop."),
    ("yield 5", False, "yield only works inside a function."),
    ("def f(a, a): pass", False, "Two parameters can't share a name."),
    ("def f():", False, "A def needs an indented body."),
    ("def f(a, b=2, *args, **kw): pass", True, ""),
    ("class A: pass", True, ""),
    ("class: pass", False, "A class needs a name."),
    ("x: int = 5", True, "A type hint is allowed."),
    ("True = 1", False, "True is a keyword, not a name."),
    ("None = 1", False, "None is a keyword, not a name."),
    ("x = [i for i in range(3)]", True, ""),
    ("x = [i for i in range(3)", False, "The list's [ never closes."),
    ("x = y = 0", True, "Chained assignment."),
    ("assert x > 0, 'no'", True, ""),
    ("del x", True, ""),
    ("import os", True, ""),
    ("import x from y", False, "It's from y import x."),
    ("from os import path", True, ""),
    ("with open('f') as f: pass", True, ""),
    ("x = 'a' 'b'", True, "Two string literals side by side join up."),
    ("print(x, end='')", True, ""),
    ("if x == 1: pass\nelif x == 2: pass\nelse: pass", True, ""),
)


def syntax_snap(rng: random.Random) -> Item:
    line, ok, why = rng.choice(SYNTAX)
    return Item(line, "valid" if ok else "invalid", why or ("Valid Python." if ok else ""))
