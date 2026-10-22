"""Errors and debugging, Python side: eight activities about what goes wrong and why.

Which Error, Which Line, Read the Message, Try Flow, Fix It, Crash or Print,
Off by One Bug, Typo Hunt. Every answer is modelled by hand (a tiny
interpreter for try/except/else/finally, hand-made ranges, the line a failing
statement sits on) and tests/test_brain_packs.py runs every template through
the real interpreter. The runtime is only ever the judge: each item carries a
`check` program that RUNS the shown code and works out the answer from what
really happened (the exception's name, the line of its traceback, what was
printed, which of two fixes passes), and the test compares that with the answer
written here.

The JavaScript side (`_errors_js.py`) imports the shared pieces from here.
"""

from __future__ import annotations

import random
import re
from string import Template
from typing import Callable

from ._model import Maker, fdiv, ints, isort, params, py_div, py_show, row, upper
from .items import Item

# ── Oracle programs: they run the shown code and report what really happened ─

_GO = (
    "import contextlib, io\n"
    "def _go(src):\n"
    "    buf = io.StringIO()\n"
    "    err = None\n"
    "    try:\n"
    "        with contextlib.redirect_stdout(buf):\n"
    "            exec(compile(src, '<s>', 'exec'), {})\n"
    "    except Exception as e:\n"
    "        err = e\n"
    "    return buf.getvalue(), err\n"
)


def check_exc_name(code: str) -> str:
    """Runs `code`; gives the name of the exception it raises."""
    return _GO + "def _answer():\n    _, e = _go(" + repr(code) + ")\n    return type(e).__name__ if e else 'none'\n_answer()"


def check_exc_line(code: str) -> str:
    """Runs `code`; gives the line (of the code) the exception was raised on: the innermost one."""
    return (_GO + "def _answer():\n    _, e = _go(" + repr(code) + ")\n    if e is None:\n        return 'none'\n"
            "    tb, n = e.__traceback__, 'none'\n    while tb:\n"
            "        if tb.tb_frame.f_code.co_filename == '<s>':\n            n = tb.tb_lineno\n"
            "        tb = tb.tb_next\n    return str(n)\n_answer()")


def check_last_print(code: str) -> str:
    """Runs `code`; gives the last line it printed ('nothing' if none)."""
    return (_GO + "def _answer():\n    out, _ = _go(" + repr(code) + ")\n"
            "    lines = [x for x in out.split('\\n') if x]\n    return lines[-1] if lines else 'nothing'\n_answer()")


def check_joined_prints(code: str) -> str:
    """Runs `code`; gives everything it printed, the lines joined with nothing between."""
    return (_GO + "def _answer():\n    out, _ = _go(" + repr(code) + ")\n"
            "    return ''.join(out.split('\\n')) or 'nothing'\n_answer()")


def check_message(code: str, shown: str, answer: str) -> str:
    """Runs `code`; gives `answer` only if the exception really reads `shown` (else what it read)."""
    return (_GO + "def _answer():\n    _, e = _go(" + repr(code) + ")\n"
            "    msg = type(e).__name__ + ': ' + str(e) if e else 'none'\n"
            "    return " + repr(answer) + " if msg == " + repr(shown) + " else 'MISMATCH ' + msg\n_answer()")


def check_two_programs(first: str, second: str, want: str) -> str:
    """Runs both programs: '1' or '2' for the only one that prints exactly `want` and does not raise."""
    return (_GO + "def _answer():\n    a, b = _go(" + repr(first) + "), _go(" + repr(second) + ")\n"
            "    w = " + repr(want) + "\n"
            "    ok1 = a[1] is None and a[0].strip() == w\n    ok2 = b[1] is None and b[0].strip() == w\n"
            "    if ok1 and not ok2:\n        return '1'\n    if ok2 and not ok1:\n        return '2'\n"
            "    return 'both' if ok1 else 'neither'\n_answer()")


def check_two_loops(first: str, second: str, want: str) -> str:
    """Like check_two_programs, but the output is compared with its lines joined by one space."""
    return (_GO + "def _answer():\n    a, b = _go(" + repr(first) + "), _go(" + repr(second) + ")\n"
            "    w = " + repr(want) + "\n"
            "    ok1 = a[1] is None and ' '.join(a[0].split()) == w\n"
            "    ok2 = b[1] is None and ' '.join(b[0].split()) == w\n"
            "    if ok1 and not ok2:\n        return '1'\n    if ok2 and not ok1:\n        return '2'\n"
            "    return 'both' if ok1 else 'neither'\n_answer()")


def check_typo(code: str, typo: str, fixed: str) -> str:
    """Runs the code and its repaired form: gives the misspelled word the runtime itself complains about
    (a NameError's or AttributeError's name) or, for a syntax error, the typo - but only if the repair runs clean."""
    return (_GO + "def _answer():\n    _, e = _go(" + repr(code) + ")\n    _, f = _go(" + repr(fixed) + ")\n"
            "    if f is not None:\n        return 'REPAIR FAILS ' + repr(f)\n"
            "    if e is None:\n        return 'NO ERROR'\n"
            "    if isinstance(e, (NameError, AttributeError)):\n        return e.name\n"
            "    if isinstance(e, SyntaxError):\n        return " + repr(typo) + "\n"
            "    return 'OTHER ' + type(e).__name__\n_answer()")


# ── Small hand models ───────────────────────────────────────────────────

def hrange(start: int, stop: int, step: int = 1) -> list[int]:
    """The numbers range(start, stop, step) gives, by counting."""
    out, v = [], start
    if step > 0:
        while v < stop:
            out.append(v)
            v += step
    else:
        while v > stop:
            out.append(v)
            v += step
    return out


def spaced(values) -> str:
    return " ".join(str(v) for v in values)


def _fill(rng: random.Random, fmt: str) -> tuple[dict, str]:
    p = params(rng)
    return p, Template(fmt).substitute(p)


# ── The try/except/else/finally model, shared with the JavaScript side ──────
#
# Statements are tuples: ("p", "A") prints A; ("pi",) prints the loop number; ("raise", "ValueError");
# ("reraise",) inside a handler; ("ret", "A"); ("break",); ("continue",); ("if", k, [..]) is `if i == k`;
# ("loop", n, [..]) runs i = 1..n; ("call", shown) calls g() (and prints what it returns when shown);
# ("try", body, [(exception or None, handler)], else, finally). Run it and you have what the program prints.

P = lambda x: ("p", x)  # noqa: E731
RAISE = lambda e: ("raise", e)  # noqa: E731
RET = lambda x: ("ret", x)  # noqa: E731


def T(body, handlers=(), els=(), fin=()):
    return ("try", list(body), [(e, list(b)) for e, b in handlers], list(els), list(fin))


class Flow:
    """Runs a statement list by the language's rules and records what it prints."""

    def __init__(self, g=()):
        self.g = list(g)
        self.out: list[str] = []

    def run(self, stmts, cur=None, i=0):
        for s in stmts:
            sig = self.step(s, cur, i)
            if sig is not None:
                return sig
        return None

    def step(self, s, cur, i):
        k = s[0]
        if k == "p":
            self.out.append(s[1])
        elif k == "pi":
            self.out.append(str(i))
        elif k == "raise":
            return ("exc", s[1])
        elif k == "reraise":
            return ("exc", cur)
        elif k == "ret":
            return ("ret", s[1])
        elif k == "break":
            return ("break",)
        elif k == "continue":
            return ("continue",)
        elif k == "if":
            return self.run(s[2], cur, i) if i == s[1] else None
        elif k == "call":
            sig = self.run(self.g)
            if sig is not None and sig[0] == "exc":
                return sig
            if s[1]:
                self.out.append(sig[1])
        elif k == "loop":
            j = 1
            while j <= s[1]:
                sig = self.run(s[2], cur, j)
                if sig is not None and sig[0] in ("exc", "ret"):
                    return sig
                if sig is not None and sig[0] == "break":
                    break
                j += 1
        elif k == "try":
            _, body, handlers, els, fin = s
            sig = self.run(body, cur, i)
            if sig is not None and sig[0] == "exc":
                for exc, hb in handlers:
                    if exc is None or exc == "Exception" or exc == sig[1]:
                        sig = self.run(hb, sig[1], i)
                        break
            elif sig is None and els:
                sig = self.run(els, cur, i)
            fsig = self.run(fin, cur, i)
            return fsig if fsig is not None else sig
        return None

    def program(self, main, as_func: bool) -> str:
        """What the whole program prints. A function body is called and its result printed."""
        if as_func:
            sig = self.run(main)
            if sig is not None and sig[0] == "ret":
                self.out.append(sig[1])
        else:
            self.run(main)
        return "".join(self.out)


def py_lines(stmts, ind: int = 0) -> list[str]:
    pad = "    " * ind
    out: list[str] = []
    for s in stmts:
        k = s[0]
        if k == "p":
            out.append(f'{pad}print("{s[1]}")')
        elif k == "pi":
            out.append(f"{pad}print(i)")
        elif k == "raise":
            out.append(f'{pad}raise {s[1]}("x")')
        elif k == "reraise":
            out.append(f"{pad}raise")
        elif k == "ret":
            out.append(f'{pad}return "{s[1]}"')
        elif k in ("break", "continue"):
            out.append(pad + k)
        elif k == "if":
            out.append(f"{pad}if i == {s[1]}:")
            out += py_lines(s[2], ind + 1)
        elif k == "call":
            out.append(f"{pad}print(g())" if s[1] else f"{pad}g()")
        elif k == "loop":
            out.append(f"{pad}for i in range(1, {s[1] + 1}):")
            out += py_lines(s[2], ind + 1)
        elif k == "try":
            _, body, handlers, els, fin = s
            out.append(f"{pad}try:")
            out += py_lines(body, ind + 1)
            for exc, hb in handlers:
                out.append(f"{pad}except {exc or 'Exception'}:")
                out += py_lines(hb, ind + 1)
            if els:
                out.append(f"{pad}else:")
                out += py_lines(els, ind + 1)
            if fin:
                out.append(f"{pad}finally:")
                out += py_lines(fin, ind + 1)
    return out


LETTERS = "ABCDEFGHJKMNPQRSTUVWXYZ"
EXCS = ("ValueError", "KeyError", "ZeroDivisionError", "TypeError")


# ── 1. Which Error ──────────────────────────────────────────────────────

def _we(code: str, answer: str, why: str) -> Maker:
    return row(code, answer, why, check=check_exc_name)


WHICH_ERROR = [
    _we('nums = [$a, $b, $c]\nprint(nums[3])', "IndexError",
        "A list of three items has positions 0, 1 and 2, so position 3 is past the end."),
    _we('word = "$w"\nprint(word[$n])', "IndexError", "The string is far shorter than that position."),
    _we('ages = {"$w": $a}\nprint(ages["$v"])', "KeyError", "The dict has no key named $v."),
    _we("print($a / 0)", "ZeroDivisionError", "Nothing can be divided by zero."),
    _we("total = $a\ncount = 0\nprint(total / count)", "ZeroDivisionError", "count is 0, and dividing by it fails."),
    _we("n = $a\nprint(n // 0)", "ZeroDivisionError", "// refuses a zero divisor too."),
    _we("print(len($a))", "TypeError", "A number has no length: len wants a string, list or the like."),
    _we('print("$w" + $a)', "TypeError", "Text and a number do not add: one has to be converted."),
    _we('print("Age: " + $a)', "TypeError", "A string and an int cannot be joined with +."),
    _we('print(int("$w"))', "ValueError", "int() got text that is not a number."),
    _we('print(int("$a.5"))', "ValueError", "int() cannot read a decimal point in text."),
    _we('print(float("$w"))', "ValueError", "float() got text that is not a number."),
    _we("print($w)", "NameError", "$w was never given a value, so Python does not know the name."),
    _we("count = $a\nprint(cont)", "NameError", "cont is a typo: no such name exists."),
    _we("def show():\n    print(x)\n    x = $a\nshow()", "UnboundLocalError",
        "x is assigned inside the function, so it is local, and it is read before it has a value."),
    _we("x = $a\ndef bump():\n    x += 1\nbump()", "UnboundLocalError",
        "x += 1 makes x local to the function, where it has no value yet."),
    _we("x = None\nx.append($a)", "AttributeError", "None has no append: the value is not a list."),
    _we("nums = [$a]\nnums.push($b)", "AttributeError", "Python lists have append, not push."),
    _we('name = "$w"\nprint(name.size())', "AttributeError", "Strings have no size method."),
    _we("import ${w}_tools", "ModuleNotFoundError", "There is no module with that name."),
    _we("nums = [$a, $b]\nnums.remove($c + 10)", "ValueError", "remove() raises when the value is not in the list."),
    _we("a, b = [$a, $b, $c]", "ValueError", "Three values do not fit into two names."),
    _we("x = $a\nx()", "TypeError", "A number is not a function, so it cannot be called."),
    _we("t = ($a, $b)\nt[0] = $c", "TypeError", "Tuples cannot be changed after they are made."),
    _we('s = "$w"\ns[0] = "x"', "TypeError", "Strings cannot be changed one letter at a time."),
    _we("d = {[$a]: $b}", "TypeError", "A list cannot be a dict key because it can change."),
    _we('[$a, "$w"].sort()', "TypeError", "A number and a string cannot be put in order."),
    _we("nothing = None\nprint(nothing + $a)", "TypeError", "None cannot be added to a number."),
    _we("x = None\nprint(x[0])", "TypeError", "None cannot be indexed."),
    _we("def add(a, b):\n    return a + b\nprint(add($a))", "TypeError", "add needs two arguments and got one."),
    _we("def add(a, b):\n    return a + b\nprint(add($a, $b, $c))", "TypeError", "add takes two arguments and got three."),
    _we("assert $a > $b + 10", "AssertionError", "The assert's condition is false, so it raises."),
    _we('def check(n):\n    if n < 0:\n        raise ValueError("negative")\ncheck(-$a)', "ValueError",
        "The function raises ValueError on purpose for a negative number."),
    _we("print(next(iter([])))", "StopIteration", "next() on an empty iterator has nothing to give."),
    _we('open("missing_$a.txt")', "FileNotFoundError", "There is no file with that name to open."),
    _we("import math\nprint(math.sqrt(-$a))", "ValueError", "The square root of a negative number is outside math.sqrt's domain."),
    _we("print(int(None))", "TypeError", "int() cannot turn None into a number."),
    _we("for i in $a:\n    print(i)", "TypeError", "A number cannot be looped over."),
    _we("print([$a, $b][$c])", "IndexError", "The list has two items, so that position is past the end."),
    _we("nums = []\nprint(nums[0])", "IndexError", "An empty list has no first item."),
    _we("print(max([]))", "ValueError", "max() of nothing has no answer."),
    _we("class Dog:\n    pass\nDog().bark()", "AttributeError", "The class has no bark method."),
    _we('d = {}\nd["a"]["b"] = $a', "KeyError", 'd["a"] is read first, and the key "a" is missing.'),
    _we('print({"a": $a}.a)', "AttributeError", "Dict keys are read with [], not with a dot."),
    _we('print("$a" * "$b")', "TypeError", "Two strings cannot be multiplied."),
    _we('print(int("3.5"))', "ValueError", "int() will not read text with a decimal point."),
    _we('print("$w".index("z"))', "ValueError", "index() raises when the text is missing (find would give -1)."),
    _we("[].pop()", "IndexError", "pop() on an empty list has nothing to remove."),
    _we('{}.pop("$w")', "KeyError", "pop() with no default raises when the key is missing."),
    _we("{$a, $b}.remove($c + 10)", "KeyError", "A set's remove() raises KeyError when the value is missing."),
    _we("def f(n):\n    return f(n + 1)\nf(0)", "RecursionError", "A function that calls itself forever hits Python's recursion limit."),
    _we("print(2.0 ** 10000)", "OverflowError", "The float is far too big to store."),
    _we('items = [$a, $b, $c]\nprint(items["1"])', "TypeError", "A list is indexed with whole numbers, not text."),
    _we("print(chr(-$a))", "ValueError", "chr() has no character for a negative number."),
    _we('print("%d" % "$w")', "TypeError", "%d wants a number and got text."),
    _we("print((lambda a: a)())", "TypeError", "The lambda needs one argument and got none."),
    _we("nums = [$a, $b, $c]\nfor i in range(4):\n    print(nums[i])", "IndexError", "The fourth turn asks for position 3 of a three-item list."),
]


# ── 2. Which Line ───────────────────────────────────────────────────────

def _wl(lines: list[str], bad: int, why: str) -> Maker:
    """A Which Line template: `lines` is the program, `bad` the (1-based) line the exception is raised on.
    Half the time a harmless first line is added, which moves every line down by one."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = [Template(line).substitute(p) for line in lines]
        at = bad
        if rng.random() < 0.5:
            src.insert(0, 'note = "ok"')
            at += 1
        code = "\n".join(src)
        return Item(code, str(at), Template(why).safe_substitute(p), check=check_exc_line(code))
    make.__name__ = "line_" + lines[bad - 1].strip()[:20]
    return make


WHICH_LINE = [
    _wl(["nums = [$a, $b, $c]", "total = 0", "for n in nums:", "    total += n", "print(nums[3])", "print(total)"], 5,
        "Only three items, so nums[3] fails; the loop above ran fine."),
    _wl(["price = $a", "qty = 0", "cost = price * qty", "avg = cost / qty", "print(avg)"], 4,
        "Multiplying by 0 is fine; dividing by 0 is the line that fails."),
    _wl(['name = "$w"', "print(name.upper())", "print(name.shout())", 'print("done")'], 3,
        "Strings have upper but no shout."),
    _wl(['stock = {"$w": $a}', 'print(stock["$w"])', 'total = stock["$w"] + 1', 'print(stock["$v"])', "print(total)"], 4,
        "The key \"$v\" was never added."),
    _wl(["def bump(n):", "    return n + 1", "print(bump($a))", 'print(bump("$w"))', 'print("end")'], 2,
        "The error is raised inside the function, on the line that adds, not on the call line."),
    _wl(["def first(items):", "    return items[0]", "print(first([$a, $b]))", "print(first([]))", 'print("end")'], 2,
        "The index is read inside first, so that is the line the error comes from."),
    _wl(["nums = [$a, $b, $c]", "for i in range(4):", "    print(nums[i])", 'print("done")'], 3,
        "On the fourth turn i is 3, and nums[3] does not exist."),
    _wl(["x = $a", "y = x + 1", "z = y / (x - $a)", "print(z)"], 3, "x - $a is 0, so the division fails."),
    _wl(["count = $a", "def bump():", "    count = count + 1", "bump()", "print(count)"], 3,
        "count is assigned in the function, so it is local, and it is read before it has a value."),
    _wl(["total = 0", "for n in [$a, $b]:", "    total = total + n", "print(totl)", "print(total)"], 4,
        "totl is a typo, so the name does not exist."),
    _wl(['text = "$a"', "num = int(text)", 'word = "$w"', "bad = int(word)", "print(num + bad)"], 4,
        "int(\"$a\") is fine; int of a word fails."),
    _wl(["pair = ($a, $b)", "first, second = pair", "print(first + second)", "x, y, z = pair", "print(x)"], 4,
        "Two values cannot fill three names."),
    _wl(["import math", "print(math.sqrt($a))", "import ${w}_tools", 'print("ready")'], 3,
        "math exists; ${w}_tools does not."),
    _wl(['label = "Total: "', "amount = $a", "line = label + amount", "print(line)"], 3,
        "A string and a number cannot be joined with +."),
    _wl(['stock = {"a": $a, "b": $b}', 'for k in ["a", "b", "c"]:', "    print(stock[k])", 'print("done")'], 3,
        "The loop reaches the key \"c\", which the dict does not have: the error is on the line that looks it up."),
    _wl(["def a():", "    return b()", "def b():", "    return 1 / 0", "print(a())"], 4,
        "The traceback ends at the line that really failed: the division inside b."),
    _wl(["def find(xs, t):", "    for x in xs:", "        if x == t:", "            return x",
         "r = find([$a, $b], 99)", "print(r + 1)"], 6,
        "find gives back None when nothing matches, and adding to None fails on the last line."),
    _wl(["items = []", "items.append($a)", "items.pop()", "items.pop()", "print(items)"], 4,
        "The first pop empties the list; the second has nothing to remove."),
    _wl(["n = 3", "while n >= 0:", "    print(12 // n)", "    n -= 1", 'print("done")'], 3,
        "n counts down to 0, and the division on line 3 fails then."),
    _wl(["def check(age):", "    if age < 0:", '        raise ValueError("negative")', "    return age",
         "print(check($a))", "print(check(-$b))"], 3, "The error is raised by the raise line inside check."),
    _wl(["class Dog:", "    def __init__(self, name):", "        self.name = name", 'd = Dog("$w")', "print(d.name)",
         "print(d.age)"], 6, "Dog sets name but never age."),
    _wl(["a = [$a, $b]", "b = a + [$c]", "c = b + $d", "print(c)"], 3, "A list and a number cannot be added."),
    _wl(['d = {"x": $a}', 'del d["x"]', 'del d["x"]', "print(d)"], 3, "The key was already removed by the line above."),
    _wl(['print("start")', "half = $a / 2", "for i in range(half):", "    print(i)"], 3,
        "$a / 2 is a float, and range wants a whole number."),
    _wl(['print("go")', "pair = ($a, $b, $c)", "first, second = pair", "print(first)"], 3,
        "Three values do not fit into two names."),
    _wl(['words = ["$w", "$v"]', "for w in words:", "    print(w.upper())", "    print(w.size())"], 4,
        "upper works, size does not exist, and the first turn already fails."),
    _wl(["scores = [$a, $b, $c]", "best = max(scores)", "low = min(scores)", "avg = sum(scores) / len([])", "print(avg)"], 4,
        "len([]) is 0, so the division fails."),
    _wl(["def area(w, h):", "    return w * h", "print(area($a, $b))", "print(area($a))", 'print("end")'], 4,
        "area needs two arguments: the call line is where Python notices it got one."),
    _wl(['names = ["$w", "$v"]', "print(names[0])", "print(names[1])", "print(names[2])", "print(names[3])"], 4,
        "Positions 0 and 1 exist; position 2 is the first one past the end."),
    _wl(["x = $a", "if x > 1:", '    print("big")', "    print(y)", "print(x)"], 4,
        "y was never given a value."),
    _wl(["total = 0", "for n in [$a, $b, $c]:", "    total += n", 'print("total", total)', 'print("avg", total / 0)'], 5,
        "The first print works; dividing by 0 breaks the second."),
    _wl(['value = "$a"', "number = int(value)", "half = number / 2", "result = value + half", "print(result)"], 4,
        "value is still the string; adding a number to it fails."),
    _wl(['data = {"a": [$a, $b]}', 'print(data["a"][0])', 'print(data["a"][2])', 'print(data["b"])'], 3,
        "The list under \"a\" has two items, so position 2 is too far."),
    _wl(["def risky(n):", "    if n > 5:", '        raise RuntimeError("too big")', "    return n",
         "for n in [1, $k, 10]:", "    print(risky(n))"], 3, "The error comes from the raise inside risky, when n is 10."),
    _wl(["a = [1, 2, 3]", "b = a[1]", "c = a[b + 2]", "print(c)"], 3, "b is 2, so a[4] is far past the end."),
    _wl(['text = "$w"', "print(len(text))", 'print(text.count("o"))', "print(text + len(text))"], 4,
        "A string and a number cannot be joined with +."),
    _wl(["def f(n):", "    return n / (n - $a)", "print(f($b))", "print(f($a))", "print(f($c))"], 2,
        "f($a) divides by zero inside f."),
    _wl(["ok = True", "if ok:", '    print("fine")', "    print(nothing)", 'print("end")'], 4, "nothing was never given a value."),
    _wl(["total = 0", "for i in range(1, 4):", "    total += i", "print(total)", "print(total[0])"], 5,
        "total is a number, and a number cannot be indexed."),
    _wl(["age = $a", "print(age)", 'age = age + "1"', "print(age)"], 3, "A number and a string cannot be added."),
    _wl(['names = ["$w", "$v"]', "upper = [n.upper() for n in names]", "lens = [len(n) for n in names + [$a]]",
         "print(upper)"], 3, "len of the number fails on line 3, inside the comprehension."),
    _wl(["def get(d, k):", "    return d[k]", 'stock = {"a": $a}', 'print(get(stock, "a"))', 'print(get(stock, "b"))'], 2,
        "The lookup d[k] is inside get, so that is the line the error is raised on."),
    _wl(["items = [$a, $b, $c]", "items[0] = 0", "t = tuple(items)", "t[1] = 5", "print(t)"], 4,
        "A list can be assigned into; a tuple cannot."),
    _wl(["import math", "r = $a", "print(math.pi * r * r)", "print(math.sqrt(-r))"], 4,
        "The square root of a negative number is an error."),
    _wl(["x = 10", "y = 0", "while y < 3:", "    y += 1", "    print(x / (y - 2))"], 5,
        "The division is fine for y = 1, then fails when y reaches 2."),
]


# ── 3. Read the Message ─────────────────────────────────────────────────

CHOICES_MSG = ("missing", "wrong")


def _msg(code: str, shown: str, answer: str, why: str) -> Maker:
    """An error message to classify: `shown` is exactly what the real exception reads when `code` runs."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src, text = Template(code).substitute(p), Template(shown).substitute(p)
        return Item(text, answer, Template(why).safe_substitute(p), check=check_message(src, text, answer))
    make.__name__ = "msg_" + shown[:24]
    return make


def _gone(code: str, shown: str, why: str) -> Maker:
    return _msg(code, shown, "missing", why)


def _bad(code: str, shown: str, why: str) -> Maker:
    return _msg(code, shown, "wrong", why)


MESSAGE = [
    _gone("print($w)", "NameError: name '$w' is not defined", "The code uses a name that was never created: something is missing."),
    _gone("count = $a\nprint(cont)", "NameError: name 'cont' is not defined", "A typo in a name leaves a name that does not exist."),
    _gone("print(math.sqrt($a))", "NameError: name 'math' is not defined", "math was never imported, so the name is missing."),
    _gone("Print('$w')", "NameError: name 'Print' is not defined", "Python is case sensitive: only print exists."),
    _gone("print(items)\nitems = [$a]", "NameError: name 'items' is not defined", "The name is used before the line that creates it."),
    _gone("count = $a\nprint(Count)", "NameError: name 'Count' is not defined", "Count and count are different names."),
    _gone("nums = [$a, $b]\nnums.push($c)", "AttributeError: 'list' object has no attribute 'push'",
          "The list has no method called push: the attribute is missing."),
    _gone("x = None\nx.upper()", "AttributeError: 'NoneType' object has no attribute 'upper'",
          "None has no upper method: the thing that should have been text is not there."),
    _gone('print("$w".size())', "AttributeError: 'str' object has no attribute 'size'", "Strings have no size method."),
    _gone("t = ($a, $b)\nt.append($c)", "AttributeError: 'tuple' object has no attribute 'append'", "Tuples cannot grow, so they have no append."),
    _gone('d = {"a": $a}\nd.a', "AttributeError: 'dict' object has no attribute 'a'", "A dict's keys are read with [], not as attributes."),
    _gone("class Dog:\n    pass\nDog().bark()", "AttributeError: 'Dog' object has no attribute 'bark'", "The class never defined bark."),
    _gone("x = None\nx.length", "AttributeError: 'NoneType' object has no attribute 'length'", "None has no length attribute."),
    _gone('"$w".foo', "AttributeError: 'str' object has no attribute 'foo'", "A string has no attribute named foo."),
    _gone("nums = [$a]\nnums.add($b)", "AttributeError: 'list' object has no attribute 'add'", "Lists have append; add belongs to sets."),
    _gone("s = {$a}\ns.append($b)", "AttributeError: 'set' object has no attribute 'append'", "Sets have add; append belongs to lists."),
    _gone("str.shout('x')", "AttributeError: type object 'str' has no attribute 'shout'", "The str type has no shout."),
    _gone("nums = [$a, $b, $c]\nnums[3]", "IndexError: list index out of range", "There is no item at that position."),
    _gone("nums = [$a, $b, $c]\nnums[-4]", "IndexError: list index out of range", "Counting back from the end runs out of items."),
    _gone('"$w"[$n]', "IndexError: string index out of range", "The string has no character at that position."),
    _gone("[].pop()", "IndexError: pop from empty list", "An empty list has nothing to pop."),
    _gone('d = {"a": $a}\nd["$w"]', "KeyError: '$w'", "The dict has no key '$w'."),
    _gone('{}.pop("$w")', "KeyError: '$w'", "pop cannot remove a key that is not there."),
    _gone('d = {}\nd["$w"]["$v"]', "KeyError: '$w'", "The first lookup already fails: the key is missing."),
    _gone("s = {$a, $b}\ns.remove(99)", "KeyError: 99", "A set's remove raises for a value it does not hold."),
    _gone("import ${w}_tools", "ModuleNotFoundError: No module named '${w}_tools'", "No module has that name."),
    _gone("import mathh", "ModuleNotFoundError: No module named 'mathh'", "A typo in a module name finds no module."),
    _gone("def add(a, b):\n    return a + b\nadd($a)", "TypeError: add() missing 1 required positional argument: 'b'",
          "The call left out an argument add needs: something is missing."),
    _gone("def add(a, b):\n    return a + b\nadd()", "TypeError: add() missing 2 required positional arguments: 'a' and 'b'",
          "Both arguments were left out."),
    _gone("[$a, $b].index(99)", "ValueError: 99 is not in list", "index cannot find a value that is not there."),
    _gone('"$w".index("z")', "ValueError: substring not found", "index fails when the text is not there (find would give -1)."),
    _gone("open('nofile.txt')", "FileNotFoundError: [Errno 2] No such file or directory: 'nofile.txt'", "There is no such file to open."),
    _bad('"$w" + $a', 'TypeError: can only concatenate str (not "int") to str', "A string and a number cannot be joined: the number is the wrong kind."),
    _bad('"$w" + None', 'TypeError: can only concatenate str (not "NoneType") to str', "None is not text, so it cannot be joined on."),
    _bad("[$a, $b] + $c", 'TypeError: can only concatenate list (not "int") to list', "Only a list can be added to a list."),
    _bad('$a + "$w"', "TypeError: unsupported operand type(s) for +: 'int' and 'str'", "The operator does not work on an int and a str."),
    _bad("None + $a", "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'", "None cannot be added to: the value is wrong."),
    _bad('"$w" - "$v"', "TypeError: unsupported operand type(s) for -: 'str' and 'str'", "Strings cannot be subtracted."),
    _bad('sum(["$w"])', "TypeError: unsupported operand type(s) for +: 'int' and 'str'", "sum starts from 0 and cannot add text to it."),
    _bad("x = None\nx += $a", "TypeError: unsupported operand type(s) for +=: 'NoneType' and 'int'", "None cannot be added to."),
    _bad('"$w" * "$v"', "TypeError: can't multiply sequence by non-int of type 'str'", "A string can only be repeated by a whole number."),
    _bad("$a / 0", "ZeroDivisionError: division by zero", "Zero is the wrong value to divide by."),
    _bad('int("$w")', "ValueError: invalid literal for int() with base 10: '$w'", "The text is the wrong value for int()."),
    _bad('int("3.5")', "ValueError: invalid literal for int() with base 10: '3.5'", "int() will not read a decimal point."),
    _bad('float("$w")', "ValueError: could not convert string to float: '$w'", "The text cannot be read as a number."),
    _bad("len($a)", "TypeError: object of type 'int' has no len()", "A number is the wrong kind of thing to measure."),
    _bad("x = $a\nx()", "TypeError: 'int' object is not callable", "A number is not a function."),
    _bad('x = "$w"\nx()', "TypeError: 'str' object is not callable", "A string is not a function."),
    _bad("x = $a\nx[0]", "TypeError: 'int' object is not subscriptable", "A number cannot be indexed."),
    _bad("x = None\nx[0]", "TypeError: 'NoneType' object is not subscriptable", "None cannot be indexed."),
    _bad("t = ($a, $b)\nt[0] = $c", "TypeError: 'tuple' object does not support item assignment", "Tuples cannot be changed."),
    _bad('s = "$w"\ns[0] = "z"', "TypeError: 'str' object does not support item assignment", "Strings cannot be changed in place."),
    _bad("for i in $a:\n    pass", "TypeError: 'int' object is not iterable", "A number cannot be looped over."),
    _bad("max($a)", "TypeError: 'int' object is not iterable", "max wants a collection, not one number."),
    _bad("{[$a]: $b}", "TypeError: unhashable type: 'list'", "A list is the wrong kind of thing for a dict key."),
    _bad('[$a, $b]["x"]', "TypeError: list indices must be integers or slices, not str", "A list is indexed with whole numbers."),
    _bad("a, b = [$a, $b, $c]", "ValueError: too many values to unpack (expected 2)", "The number of values is wrong for the names."),
    _bad('[$a, "$w"].sort()', "TypeError: '<' not supported between instances of 'str' and 'int'", "A number and a string cannot be compared."),
    _bad('print("$a" < $b)', "TypeError: '<' not supported between instances of 'str' and 'int'", "Text and a number cannot be ordered."),
    _bad("range(1.5)", "TypeError: 'float' object cannot be interpreted as an integer", "range wants whole numbers."),
    _bad("import math\nmath.sqrt(-$a)", "ValueError: math domain error", "A negative number is the wrong value for a square root."),
    _bad('abs("$w")', "TypeError: bad operand type for abs(): 'str'", "abs works on numbers, not text."),
    _bad("int(None)", "TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'",
         "None is not something int() can read."),
    _bad('"$w".join([$a])', "TypeError: sequence item 0: expected str instance, int found", "join only takes text."),
]


# ── 4. Try Flow ─────────────────────────────────────────────────────────

def flow_item(code: str, as_func: bool, main, g, why: str, check: Callable[[str], str]) -> Item:
    answer = Flow(g).program(main, as_func)
    return Item(code, answer, why, check=check(code))


def _flow(shape, why: str) -> Maker:
    """A Try Flow template: `shape(letters, X, Y, boom)` gives (as_func, main statements, g statements)."""
    def make(rng: random.Random) -> Item:
        letters = rng.sample(LETTERS, 7)
        x, y = rng.sample(EXCS, 2)
        as_func, main, g = shape(*letters, x, y, rng.random() < 0.5)
        lines: list[str] = []
        if g:
            lines += ["def g():"] + py_lines(g, 1)
        if as_func:
            lines += ["def f():"] + py_lines(main, 1) + ["print(f())"]
        else:
            lines += py_lines(main)
        return flow_item("\n".join(lines), as_func, main, g, why, check_joined_prints)
    make.__name__ = "flow_" + why[:20]
    return make


def _ifi(k, *body):
    return ("if", k, list(body))


_CONT, _BRK, _RERAISE = ("continue",), ("break",), ("reraise",)
_CALL, _CALLP = ("call", False), ("call", True)


def _loop(n, *body):
    return ("loop", n, list(body))


_FIN = "finally always runs, whatever happened in the try."
_ELSE = "else runs only when the try finished without an error."

FLOW_SHAPES = [
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X) if B else P(b)], [(X, [P(c)])], [P(d)], [P(e)])], ()),
     "The handler runs only if the try raised, else only if it did not; finally runs either way."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X)], [(X, [P(b)])], [], [P(c)]), P(d)], ()),
     "After the error is handled and finally has run, the program carries on below the try."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X), P(b)], [(Y, [P(c)])], [], [P(d)])], ()),
     "The except names a different error, so nothing catches this one: finally still runs, then the program stops."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X), P(b)], [("Exception", [P(c)])], [], [P(d)])], ()),
     "Nothing after the raise in the try runs; except Exception catches it, and finally runs last."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [("Exception", [P(a)]), (X, [P(b)])], [], [P(c)])], ()),
     "The first except that fits wins, and Exception fits everything, so the second one never runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(Y)], [(X, [P(b)]), (Y, [P(c)])], [], [P(d)])], ()),
     "Python tries the excepts in order and uses the one that matches the error."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(X, [P(a), RAISE(Y)])], [], [P(b)])], [(Y, [P(c)])])], ()),
     "An error raised inside an except still lets that try's finally run before the outer except sees it."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([P(a)], [(X, [P(b)])], [RAISE(X)])], [(X, [P(d)])])], ()),
     "An error raised in else is not caught by that try's own excepts, so it goes to the outer one."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RET(a)], [], [], [P(b)]), RET(c)], ()),
     "finally runs before the function really returns, so B prints before the returned A."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RAISE(X)], [(X, [RET(a)])], [], [P(b)]), RET(c)], ()),
     "A return inside except still runs finally first, and then the caller prints the returned value."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([RET(a)], [(X, [P(b)])], [P(c)], [P(d)])], ()),
     "A return in the try skips else, but finally still runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, _CONT), P(a)], [], [], [P(b)]), P(c))], ()),
     "continue skips the rest of that turn, but finally still runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, _BRK), P(a)], [], [], [P(b)])), P(c)], ()),
     "break leaves the loop, but finally runs first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, RAISE(X)), P(a)], [(X, [P(b), _CONT])], [], []), P(c))], ()),
     "continue in the except jumps to the next turn, skipping the line after the try."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, RAISE(X))], [(X, [P(a)])], [P(b)], [P(c)]))], ()),
     "Each turn runs else when nothing was raised, the except when it was, and finally either way."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, ("pi",), T([_ifi(2, RAISE(X))], [(X, [P(a)])], [], []))], ()),
     "Turn 2 prints its number, then the error is caught and A is printed; the loop goes on."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([P(a)], [], [], [P(b)])], [], [], [P(c)])], ()),
     "Inner finally first, then the outer one."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [], [], [P(a)])], [(X, [P(b)])], [], [P(c)])], ()),
     "The error passes through the inner finally on its way out to the outer except."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(X, [P(a), _RERAISE])], [], [P(b)])], [(X, [P(c)])])], ()),
     "A bare raise in an except sends the same error on, after the inner finally."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [(X, [P(a)])]), P(b)], ()),
     "Once handled, the error is over and the next line runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a)], [(X, [P(b)])], [P(c)], [P(d)])], ()),
     "No error: the except is skipped, else runs, then finally."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X), P(a)], [(X, [P(b)])], [], [P(c)])], ()),
     "The raise comes first, so the try's print never happens."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(X)], [(X, [P(a)])]), T([P(b)], [(X, [P(c)])], [P(d)])], ()),
     "Two separate tries run one after the other; the second has no error, so its else runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALL, P(c)], [(X, [P(d)])], [], [P(e)])], [P(a), RAISE(X)]),
     "The error is raised inside g, so the rest of g and the line after the call are skipped."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALL], [(X, [P(d)])])], [T([P(a), RAISE(X)], [], [], [P(b)])]),
     "g's own finally runs while the error leaves g, before the caller's except."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALLP], [(X, [P(e)])], [P(c)], [P(d)])], [RET(a)]),
     "g returns normally, so the try has no error: its else runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP, P(c)], [T([RAISE(X)], [(X, [RET(a)])], [], [P(b)])]),
     "g's finally runs before its return value gets back to the caller."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, P(a), _CONT), P(b)], [], [], [P(c)]))], ()),
     "continue skips B on turn 2, and finally still runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, _CONT)], [(X, [P(d)])], [P(b)], [P(c)]))], ()),
     "A continue in the try also skips else, but not finally."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(2, RAISE(X)), P(a)], [(X, [_BRK])], [], [P(b)])), P(c)], ()),
     "break in the except ends the loop, but finally runs first."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP], [_loop(3, T([_ifi(2, RET(a))], [], [], [P(b)])), RET(c)]),
     "Turn 2 returns, but finally still prints B before the function leaves."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a), RAISE(X), P(b)], [], [], [P(c)])], ()),
     "No except at all: the error stops the program after finally has run."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(Y, [P(a)])], [], [P(b)])], [(X, [P(c)])])], ()),
     "The inner except does not match, so only its finally runs; the outer except then catches the error."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a)], [(X, [P(b)])], [P(c), RAISE(X)], [P(d)])], ()),
     "The error raised in else is not caught by the same try: finally runs and the program stops."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([T([RAISE(X)], [(X, [RAISE(Y)])], [], [P(a)])], [(Y, [P(b)])])], ()),
     "A new error from an except travels outward after the inner finally, and the outer except catches it."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([P(a), RAISE(X)], [(X, [P(b)])], [], [P(c)]), RET(d)], ()),
     "The function carries on after the handled error, and finally runs before it returns."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([_CALL], [(Y, [P(c)])])], [T([RAISE(X)], [(X, [P(a), RAISE(Y)])])]),
     "g's except raises a new error that leaves g, and the caller's except catches it."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP, P(d)], [T([P(a), RET(b)], [], [], [P(c)])]),
     "The finally prints C before the return value B reaches the caller's print."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([P(a)], [(Y, [P(g)])], [P(b)]), T([RAISE(X)], [(X, [P(d)])])], ()),
     "The first try has no error, so it runs else; the second raises, so its handler runs."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(3, T([_ifi(3, RAISE(X)), ("pi",)], [], [], [P(a)]))], ()),
     "Turn 3 raises with no except: finally runs, then the program stops."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(4, T([_ifi(2, _CONT), _ifi(3, _BRK), ("pi",)], [], [], [P(a)]))], ()),
     "Turn 2 continues, turn 3 breaks; finally runs on every turn, even those."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_CALLP], [P(a), T([P(b)], [], [], [P(c)]), RET(d)]),
     "The function prints A, B and C, and then the caller prints what it returned."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([P(a), RAISE(X)], [(X, [P(b), RET(c)])], [], [P(d)])], ()),
     "The return in the except waits for finally, so D prints before the returned C."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [_loop(2, T([RAISE(X)], [(X, [P(a)])], [], [P(b)]), ("pi",))], ()),
     "Each turn handles its own error, runs finally, and then prints its number."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (False, [T([RAISE(Y)], [(X, [P(d)]), ("Exception", [P(e)])], [], [P(f)])], ()),
     "The second try raises Y: X does not fit it, Exception does."),
    (lambda a, b, c, d, e, f, g, X, Y, B: (True, [T([T([RET(a)], [], [], [P(b)])], [], [], [P(c)]), RET(d)], ()),
     "A return passes through both finallys, inner first, on its way out."),
]


WHICH_FLOW = [_flow(shape, why) for shape, why in FLOW_SHAPES]


# ── 6. Crash or Print ───────────────────────────────────────────────────

def _count(text: str) -> int:
    n = 0
    for _ in text:
        n += 1
    return n


def _cp(lines: list[str], answer, why: str) -> Maker:
    """A Crash or Print template: the answer is the last line printed before the program crashes."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        code = "\n".join(Template(line).substitute(p) for line in lines)
        got = answer(p) if callable(answer) else Template(answer).substitute(p)
        return Item(code, got, Template(why).safe_substitute(p), check=check_last_print(code))
    make.__name__ = "crash_" + lines[0][:20]
    return make


_CRASH_WHY = "Output printed before the error stays on screen; the crash stops everything after it."

CRASH = [
    _cp(['print("start")', "nums = [$a, $b, $c]", "print(nums[2])", "print(nums[3])", 'print("done")'], "$c",
        "nums[2] is printed; nums[3] fails before it can print."),
    _cp(["total = 0", "for n in [$a, $b]:", "    total += n", "    print(total)", "print(total / 0)", 'print("done")'],
        lambda p: str(p["a"] + p["b"]), "The loop prints its last total, then the division crashes before it prints anything."),
    _cp(['print("Hello")', 'name = "$w"', "print(name.upper())", "print(name.shout())", 'print("bye")'],
        lambda p: upper(p["w"]), "The upper-case word prints; the missing method crashes the next line."),
    _cp(['d = {"a": $a}', 'print(d["a"])', 'print(d["b"])', 'print("end")'], "$a", "The missing key crashes the second print before it prints."),
    _cp(["print(1)", "print(2)", 'print(int("x"))', "print(3)"], "2", "int() fails while print's argument is still being worked out."),
    _cp(["n = $a", 'print("n is", n)', 'print("n is " + n)', 'print("done")'], "n is $a",
        "The second print never gets its text: the + fails first."),
    _cp(["for i in range(4):", "    print(($a * 6) // (3 - i))", 'print("done")'], lambda p: str(6 * p["a"]),
        "On the fourth turn i is 3, and dividing by 3 - 3 crashes; the third turn printed last."),
    _cp(['words = ["$w", "$v"]', "for i in range(3):", "    print(words[i])", 'print("end")'], "$v",
        "The third turn asks for words[2], which does not exist."),
    _cp(["def show(n):", '    print("n:", n)', "    print(10 / n)", "show($a)", "show(0)"], "n: 0",
        "show(0) prints its first line, then 10 / 0 crashes."),
    _cp(["x = $a", "print(x)", 'x = x + "1"', "print(x)"], "$a", "Adding text to a number crashes before the second print."),
    _cp(["nums = []", 'print("empty")', "print(nums[0])"], "empty", "An empty list has no first item."),
    _cp(['print("a")', "import ${w}_tools", 'print("b")'], "a", "The import fails, so the last print is never reached."),
    _cp(['text = "$w"', "print(len(text))", "print(text[10])", 'print("end")'], lambda p: str(_count(p["w"])),
        "The length prints; position 10 is past the end of the word."),
    _cp(["def f(n):", "    return 100 // n", "print(f($a))", "print(f(0))", 'print("done")'], lambda p: str(fdiv(100, p["a"])),
        "f(0) divides by zero before its print can happen."),
    _cp(["scores = [$a, $b, $c]", "print(max(scores))", "print(min(scores))", "print(scores[5])"],
        lambda p: str(isort([p["a"], p["b"], p["c"]])[0]), "min is printed; scores[5] crashes."),
    _cp(["i = 3", "while i >= 0:", "    print(12 // i)", "    i -= 1"], "12", "When i reaches 0 the division crashes; the turn before printed 12."),
    _cp(['print("one")', 'print("two" + 3)', 'print("three")'], "one", "A string and a number do not add."),
    _cp(["a = $a", "b = $b", "print(a + b)", "print(a / (b - b))", 'print("ok")'], lambda p: str(p["a"] + p["b"]),
        "The sum prints; b - b is 0, so the next line crashes."),
    _cp(["name = None", 'print("hi")', "print(name.upper())"], "hi", "None has no upper method."),
    _cp(["items = [$a, $b]", "items.pop()", "print(items)", "items.pop()", "items.pop()", "print(items)"],
        lambda p: py_show([p["a"]]), "The third pop finds nothing left, so the last print never runs."),
    _cp(['d = {"x": $a}', 'print(d.get("y"))', 'print(d["y"])'], "None", "get gives None for a missing key; [] raises."),
    _cp(['print("A")', 'x = int("12")', "print(x + 1)", 'y = int("1 2")', "print(y)"], "13", "int(\"1 2\") has a space in the middle: it cannot be read."),
    _cp(["nums = [$a, $b, $c]", "for n in nums:", "    print(n)", "    nums[5] = 0"], "$a",
        "The first turn prints, then assigning to position 5 of a short list crashes."),
    _cp(["x = $a", "y = $b", "print(x * y)", "print(x / 0, y)", 'print("done")'], lambda p: str(p["a"] * p["b"]),
        "The arguments are worked out first, so the division crashes before print runs."),
    _cp(["import math", "print(math.floor(7.5))", "print(math.sqrt(-1))", 'print("ok")'], "7", "floor gives 7; the square root of -1 is an error."),
    _cp(["def risky(n):", "    if n > 2:", '        raise ValueError("big")', "    return n", "for n in [1, 2, 3]:", "    print(risky(n))"], "2",
        "risky(3) raises, so 3 is never printed."),
    _cp(["a = [1, 2, 3]", "print(a[-1])", "print(a[-3])", "print(a[-4])"], "1", "-3 is the first item; -4 is past the start."),
    _cp(['s = "$w"', "print(s[0])", "print(s[-1])", "print(s[$n])"], lambda p: p["w"][_count(p["w"]) - 1],
        "s[-1] is the last letter; the position $n is far past the end."),
    _cp(["t = ($a, $b)", "print(t[0])", "print(t[1])", "t[0] = 0", 'print("done")'], "$b", "Tuples cannot be assigned into."),
    _cp(["count = 0", "for i in range(5):", "    count += i", "    print(count)", "    if i == 2:", "        print(count / 0)"], "3",
        "After i = 2 the count is 3; the division then crashes."),
    _cp(["x = $a", "print(x)", "print(y)", "y = 2", "print(y)"], "$a", "y is used before the line that creates it."),
    _cp(['print("opening")', 'f = open("missing.txt")', 'print("opened")'], "opening", "There is no such file."),
    _cp(['letters = ["a", "b"]', "for ch in letters:", "    print(ch)", "print(letters[2])"], "b", "Positions 0 and 1 exist; 2 does not."),
    _cp(['print("loading")', "def go():", "    return stop", "print(go())", 'print("done")'], "loading",
        "stop is not a name that exists, and the call fails before print runs."),
    _cp(["a = $a", "def half(n):", "    return n / 2", "print(half(a))", 'print(half("$w"))', 'print("end")'],
        lambda p: py_div(p["a"], 2), "Halving the number prints; halving text crashes."),
    _cp(["nums = [$a, $b, $c]", "nums.sort()", "print(nums)", "nums.sort(1)", 'print("sorted")'],
        lambda p: py_show(isort([p["a"], p["b"], p["c"]])), "sort() takes no positional argument."),
    _cp(['print("one")', "assert 1 > 2", 'print("two")'], "one", "A false assert raises an error."),
    _cp(["x = $a", "print(x)", "print(x.upper())", 'print("done")'], "$a", "A number has no upper method."),
    _cp(["pairs = [($a, $b), ($c, $d)]", "for x, y in pairs:", "    print(x + y)", "for x, y, z in pairs:", "    print(z)"],
        lambda p: str(p["c"] + p["d"]), "The first loop prints both sums; the second cannot unpack two values into three names."),
    _cp(['data = {"n": $a}', 'data["n"] += 1', 'print(data["n"])', 'data["m"] += 1', "print(data)"], lambda p: str(p["a"] + 1),
        "data[\"m\"] does not exist yet, so += fails."),
    _cp(["print(1 / 1)", "print(1 / 0)"], "1.0", "1 / 1 prints as 1.0 in Python; the next line crashes."),
    _cp(['name = "$w"', 'print("Hello " + name)', 'print("Hello " + len(name))'], lambda p: "Hello " + p["w"],
        "Joining a number onto text fails."),
    _cp(['x = int("a")', 'print("done")'], "nothing", "int(\"a\") crashes first, so nothing is ever printed."),
    _cp(['n = int("$w")', "print(n)"], "nothing", "The word is not a number, so the program stops before printing."),
    _cp(['print("x" * $a)', 'print("x" * "$b")'], lambda p: "".join("x" for _ in range(p["a"])),
        "A string can be repeated by a number, but not by a string."),
]


# ── 5. Fix It ───────────────────────────────────────────────────────────

CHOICES_PICK = ("1", "2")


def fix_item(lines: list[str], bad: int, want: str, good: str, wrong: str, why: str, rng: random.Random,
             comment: str, check: Callable[[str, str, str], str]) -> Item:
    """One Fix It item: the program with the buggy line (index `bad`) marked, the wanted output, and two
    replacement lines in a random order. The check runs both repaired programs."""
    indent = lines[bad][:len(lines[bad]) - len(lines[bad].lstrip())]
    first, second = (good, wrong) if rng.random() < 0.5 else (wrong, good)
    marked = list(lines)
    marked[bad] = lines[bad] + f"  {comment} bug"

    def program(fix: str) -> str:
        fixed = list(lines)
        fixed[bad] = indent + fix
        return "\n".join(fixed)

    prompt = "\n".join(marked + [f"{comment} want: {want}", f"{comment} 1) {first}", f"{comment} 2) {second}"])
    return Item(prompt, "1" if first == good else "2", why, check=check(program(first), program(second), want))


def _fix(lines: list[str], bad: int, want, good: str, wrong: str, why: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = [Template(x).substitute(p) for x in lines]
        w = want(p) if callable(want) else Template(want).substitute(p)
        return fix_item(src, bad, w, Template(good).substitute(p), Template(wrong).substitute(p),
                        Template(why).safe_substitute(p), rng, "#", check_two_programs)
    make.__name__ = "fix_" + lines[bad].strip()[:20]
    return make


def _sum_to(n: int) -> int:
    total = 0
    for k in range(1, n + 1):
        total += k
    return total


FIX = [
    _fix(["nums = [$a, $b, $c]", "print(nums[len(nums)])"], 1, "$c", "print(nums[len(nums) - 1])", "print(nums[len(nums) - 2])",
         "The last item sits at position len - 1."),
    _fix(["total = $a + $b", 'print("Total: " + total)'], 1, lambda p: f"Total: {p['a'] + p['b']}", 'print("Total: " + str(total))',
         'print("Total: " + int(total))', "str() turns the number into text so it can be joined."),
    _fix(['prices = {"apple": $a}', 'print(prices["pear"])'], 1, "0", 'print(prices.get("pear", 0))', 'print(prices.get("pear"))',
         "get with a default gives 0; without one it gives None."),
    _fix(["nums = []", "total = sum(nums)", "avg = total / len(nums)", "print(avg)"], 2, "0", "avg = total / len(nums) if nums else 0",
         "avg = total // len(nums)", "Check for the empty list first: // divides by zero too."),
    _fix(["total = 0", "for i in range(1, $a):", "    total += i", "print(total)"], 1, lambda p: str(_sum_to(p["a"])),
         "for i in range(1, $a + 1):", "for i in range(0, $a):", "range stops before its second number, so $a itself needs + 1."),
    _fix(["x = $a", "if x = $a:", '    print("yes")'], 1, "yes", "if x == $a:", "if x != $a:", "A single = assigns; == compares."),
    _fix(["def add(a, b):", "    a + b", "print(add($a, $b))"], 1, lambda p: str(p["a"] + p["b"]), "return a + b", "print(a + b)",
         "Without return the function gives None; printing inside it prints the sum and then None."),
    _fix(["nums = [$a, $b, $c]", "nums = nums.append($d)", "print(len(nums))"], 1, "4", "nums.append($d)", "nums = nums + $d",
         "append changes the list and returns None, so do not assign its result."),
    _fix(['word = "$w"', "word.upper()", "print(word)"], 1, lambda p: upper(p["w"]), "word = word.upper()", "word.upper().strip()",
         "Strings cannot change: upper() returns a new one that must be kept."),
    _fix(['age = "$a"', "print(age + 1)"], 1, lambda p: str(p["a"] + 1), "print(int(age) + 1)", "print(str(age) + 1)",
         "age is text; int() makes it a number."),
    _fix(["items = [$a, $b, $c, $d, 1]", "print(len(items) / 2)"], 1, lambda p: "2", "print(len(items) // 2)", "print(len(items) % 2)",
         "/ gives a decimal; // rounds down to a whole number."),
    _fix(["count = $a", "count = count + 1", "print(cont)"], 2, lambda p: str(p["a"] + 1), "print(count)", "print(Count)",
         "cont and Count are not names that exist."),
    _fix(['a = "10"', 'b = "9"', "print(a < b)"], 2, "False", "print(int(a) < int(b))", "print(str(a) < str(b))",
         "Text is compared letter by letter; int() compares the numbers."),
    _fix(["grid = [[0] * 2] * 2", "grid[0][0] = 1", "print(grid[1][0])"], 0, "0", "grid = [[0] * 2 for _ in range(2)]",
         "grid = [[0, 0]] * 2", "The * copies the same inner list twice; a comprehension makes two lists."),
    _fix(["nums = [$a, $b, $c]", 'print(",".join(nums))'], 1, lambda p: f"{p['a']},{p['b']},{p['c']}",
         'print(",".join(str(n) for n in nums))', 'print(",".join(map(int, nums)))', "join only takes text, so each number becomes a string."),
    _fix(["nums = [$c, $a, $b]", "ordered = nums.sort()", "print(ordered)"], 1, lambda p: py_show(isort([p["c"], p["a"], p["b"]])),
         "ordered = sorted(nums)", "ordered = list(nums.sort())", "sort() works in place and gives None; sorted() gives the new list."),
    _fix(["n = $a * 2", "total = 0", "for i in range(n / 2):", "    total += 1", "print(total)"], 2, "$a", "for i in range(n // 2):",
         "for i in range(int(n) / 2):", "range needs a whole number, and / always gives a decimal."),
    _fix(["a, b = 1, 2, 3", "print(a + b)"], 0, "3", "a, b, c = 1, 2, 3", "a, b = (1, 2, 3)[1:]", "Three values need three names."),
    _fix(["counts = {}", 'for w in ["a", "b", "a"]:', "    counts[w] += 1", "print(counts)"], 2, "{'a': 2, 'b': 1}",
         "counts[w] = counts.get(w, 0) + 1", "counts[w] = counts[w] + 1", "A new key has no count yet, so start from get(w, 0)."),
    _fix(["x = $a", "if x > 1:", '    print("big")', "else", '    print("small")'], 3, "big", "else:", "else if x:", "else needs a colon."),
    _fix(["def greet(name):", '    return "Hi " + name', 'print(greet("$w")'], 2, lambda p: "Hi " + p["w"], 'print(greet("$w"))',
         'print(greet("$w")))', "The brackets must pair up."),
    _fix(["def total(xs):", "    s = sum(xs)", "    s", "print(total([$a, $b]))"], 2, lambda p: str(p["a"] + p["b"]), "return s", "print(s)",
         "The function must return the value for print to show it once."),
    _fix(["nums = [$a, $b, $c]", "total = 0", "i = 0", "while i <= len(nums):", "    total += nums[i]", "    i += 1", "print(total)"], 3,
         lambda p: str(p["a"] + p["b"] + p["c"]), "while i < len(nums):", "while i < len(nums) + 1:",
         "The last position is len - 1, so the loop must stop before len."),
    _fix(['text = "$w"', "print(text[len(text)])"], 1, lambda p: p["w"][_count(p["w"]) - 1], "print(text[-1])", "print(text[1])",
         "-1 is the last character; len(text) is one past it."),
    _fix(["scores = [$a, $b, $c]", "best = scores[0]", "for s in scores:", "    if s > best", "        best = s", "print(best)"], 3,
         lambda p: str(max(p["a"], p["b"], p["c"])), "if s > best:", "if s < best:", "An if line ends with a colon."),
    _fix(["name = '$w'", "print('Hello, ' + nam)"], 1, lambda p: "Hello, " + p["w"], "print('Hello, ' + name)", "print('Hello, ' + 'name')",
         "nam is a typo for the variable name."),
    _fix(["nums = [$a, $b, $c]", "print(nums.sum())"], 1, lambda p: str(p["a"] + p["b"] + p["c"]), "print(sum(nums))", "print(len(nums))",
         "sum is a function, not a list method."),
    _fix(["items = [$a, $b]", "items.add($c)", "print(len(items))"], 1, "3", "items.append($c)", "items.insert($c)",
         "Lists use append; add belongs to sets."),
    _fix(["x = $a", "y = '$b'", "print(x + y)"], 1, lambda p: str(p["a"] + p["b"]), "y = $b", "y = str($b)", "Both must be numbers to add."),
    _fix(["d = {'a': $a, 'b': $b}", "total = 0", "for k in d:", "    total += k", "print(total)"], 3, lambda p: str(p["a"] + p["b"]),
         "total += d[k]", "total += len(k)", "Looping a dict gives the keys; d[k] is the value."),
    _fix(["nums = [$a, $b, $c]", "first = nums.first()", "print(first)"], 1, "$a", "first = nums[0]", "first = nums[1]",
         "Lists have no first(); the first item is nums[0]."),
    _fix(["total = 0", "for i in range(1, $a + 1):", "    total = i", "print(total)"], 2, lambda p: str(_sum_to(p["a"])), "total += i",
         "total = total + 1", "total = i throws the old total away; += adds."),
    _fix(['word = "$w"', 'print(word * "2")'], 1, lambda p: p["w"] + p["w"], "print(word * 2)", "print(word + 2)", "A string is repeated by a whole number."),
    _fix(["nums = [$a, $b, $c]", "nums.pop(3)", "print(nums)"], 1, lambda p: py_show([p["a"], p["b"]]), "nums.pop()", "nums.pop(0)",
         "pop() removes the last item; pop(3) has no position 3."),
    _fix(["x = $a", "print('x is x')"], 1, lambda p: f"x is {p['a']}", "print(f'x is {x}')", "print('x is {x}')",
         "Only an f-string fills in the {x}."),
    _fix(["def square(n):", "    return n * n", "print(square($a, $b))"], 2, lambda p: str(p["a"] * p["a"]), "print(square($a))",
         "print(square($b))", "square takes one argument."),
    _fix(["words = ['$w', '$v']", "print(words.join(' '))"], 1, lambda p: p["w"] + " " + p["v"], "print(' '.join(words))",
         "print(''.join(words))", "join is a string method: the separator comes first."),
    _fix(["total = 0", "for n in [$a, $b, $c]:", "    total + n", "print(total)"], 2, lambda p: str(p["a"] + p["b"] + p["c"]), "total += n",
         "total = n", "total + n works out a sum and throws it away."),
    _fix(["items = ['$w', '$v']", "print(items[2])"], 1, lambda p: p["v"], "print(items[1])", "print(items[0])",
         "Two items sit at positions 0 and 1."),
    _fix(["a = $a", "b = $b", "print(a + b / 2)"], 2, lambda p: py_div(p["a"] + p["b"], 2), "print((a + b) / 2)", "print(a + b // 2)",
         "/ happens before +, so the sum needs brackets."),
    _fix(["name = '$w'", "print(name.capitalize)"], 1, lambda p: upper(p["w"][0]) + p["w"][1:], "print(name.capitalize())", "print(name.upper())",
         "Without () the method is not called."),
    _fix(["nums = [$a, $b, $c]", "total = 0", "for i in range(len(nums)):", "    total += nums[i + 1]", "print(total)"], 3,
         lambda p: str(p["a"] + p["b"] + p["c"]), "total += nums[i]", "total += nums[i] * 2", "nums[i + 1] runs off the end on the last turn."),
    _fix(["price = '$a'", "tax = 2", "print(price * tax)"], 2, lambda p: str(p["a"] * 2), "print(int(price) * tax)", "print(float(price) * tax)",
         "price is text, and text times a number repeats it."),
    _fix(["def is_even(n):", "    return n % 2 == 1", "print(is_even($a))"], 1, lambda p: "True" if p["a"] % 2 == 0 else "False",
         "return n % 2 == 0", "return n % 2 != 0", "An even number leaves remainder 0."),
    _fix(["lo = $a", "hi = $b", "mid = (lo + hi) / 2", "print(mid)"], 2, lambda p: str((p["a"] + p["b"]) // 2), "mid = (lo + hi) // 2",
         "mid = int((lo + hi) / 2) + 1", "// gives a whole number."),
    _fix(["items = [$a, $b, $c]", "print(items[1:2])"], 1, lambda p: py_show([p["b"], p["c"]]), "print(items[1:])", "print(items[:2])",
         "A slice stops before its end index, so [1:2] has one item."),
    _fix(["total = $a", "total =+ $b", "print(total)"], 1, lambda p: str(p["a"] + p["b"]), "total += $b", "total =- $b",
         "=+ is an assignment of +$b; += adds."),
]


# ── 7. Off by One Bug ───────────────────────────────────────────────────

BODIES = (("$v", lambda v: v), ("$v * 2", lambda v: v * 2), ("$v + 10", lambda v: v + 10))


R_STOP = "range stops before its second number."

OB_SPECS = [
    (lambda p: ([], "for i in range(1, $a + 1):", [], "for i in range(1, $a):", [], "i", hrange(1, p["a"] + 1), hrange(1, p["a"]), R_STOP)),
    (lambda p: ([], "for i in range($a):", [], "for i in range(1, $a):", [], "i", hrange(0, p["a"]), hrange(1, p["a"]),
                "range with one number starts at 0.")),
    (lambda p: ([], "for i in range($a):", [], "for i in range($a - 1):", [], "i", hrange(0, p["a"]), hrange(0, p["a"] - 1),
                "range($a) gives $a numbers, 0 to $a - 1.")),
    (lambda p: ([], "for i in range($a + 1):", [], "for i in range($a):", [], "i", hrange(0, p["a"] + 1), hrange(0, p["a"]), R_STOP)),
    (lambda p: ([], "for i in range($lo, $hi + 1):", [], "for i in range($lo, $hi):", [], "i", hrange(p["lo"], p["hi"] + 1),
                hrange(p["lo"], p["hi"]), R_STOP)),
    (lambda p: ([], "for i in range($lo, $hi):", [], "for i in range($lo, $hi + 1):", [], "i", hrange(p["lo"], p["hi"]),
                hrange(p["lo"], p["hi"] + 1), "The end number is not included.")),
    (lambda p: ([], "for i in range($a, 0, -1):", [], "for i in range($a, 1, -1):", [], "i", hrange(p["a"], 0, -1), hrange(p["a"], 1, -1),
                "Counting down also stops before the end number, so 0 is needed to reach 1.")),
    (lambda p: ([], "for i in range($a, 0, -1):", [], "for i in range($a - 1, 0, -1):", [], "i", hrange(p["a"], 0, -1),
                hrange(p["a"] - 1, 0, -1), "The start number is included, so it must be $a.")),
    (lambda p: ([], "for i in range($a, -1, -1):", [], "for i in range($a, 0, -1):", [], "i", hrange(p["a"], -1, -1), hrange(p["a"], 0, -1),
                "To count down to 0 the end number must be -1.")),
    (lambda p: ([], "for i in range(0, $b * 2, 2):", [], "for i in range(1, $b * 2, 2):", [], "i", hrange(0, p["b"] * 2, 2),
                hrange(1, p["b"] * 2, 2), "Starting at 0 with a step of 2 gives the even numbers.")),
    (lambda p: ([], "for i in range(0, $b * 3 + 1, 3):", [], "for i in range(0, $b * 3, 3):", [], "i", hrange(0, p["b"] * 3 + 1, 3),
                hrange(0, p["b"] * 3, 3), "$b * 3 itself needs the end to be one more.")),
    (lambda p: ([], "for i in range($a):", [], "for i in range(1, $a + 1):", [], "i", hrange(0, p["a"]), hrange(1, p["a"] + 1),
                "range($a) starts at 0, not 1.")),
    (lambda p: ([], "for i in range($lo, $hi):", [], "for i in range($lo - 1, $hi - 1):", [], "i", hrange(p["lo"], p["hi"]),
                hrange(p["lo"] - 1, p["hi"] - 1), "Both ends are given directly: the loop starts at $lo.")),
    (lambda p: (["xs = $xs"], "for i in range(len(xs)):", [], "for i in range(len(xs) - 1):", [], "xs[i]", p["xs"], p["xs"][:-1],
                "len(xs) numbers start at 0 and end at len - 1: that already covers every item.")),
    (lambda p: (["xs = $xs"], "for x in xs[:$k]:", [], "for x in xs[:$k - 1]:", [], "x", p["xs"][:p["k"]], p["xs"][:p["k"] - 1],
                "A slice stops before its end, so xs[:$k] has $k items.")),
    (lambda p: (["xs = $xs"], "for x in xs[$k:]:", [], "for x in xs[$k + 1:]:", [], "x", p["xs"][p["k"]:], p["xs"][p["k"] + 1:],
                "xs[$k:] starts at position $k and goes to the end.")),
    (lambda p: (["xs = $xs"], "for x in xs[-$k:]:", [], "for x in xs[-$k - 1:]:", [], "x", p["xs"][len(p["xs"]) - p["k"]:],
                p["xs"][len(p["xs"]) - p["k"] - 1:], "xs[-$k:] is exactly the last $k items.")),
    (lambda p: (["i = 1"], "while i <= $a:", ["i += 1"], "while i < $a:", ["i += 1"], "i", hrange(1, p["a"] + 1), hrange(1, p["a"]),
                "<= includes $a; < stops one short.")),
    (lambda p: (["n = $a"], "while n > 0:", ["n -= 1"], "while n > 1:", ["n -= 1"], "n", hrange(p["a"], 0, -1), hrange(p["a"], 1, -1),
                "n > 0 still runs when n is 1.")),
    (lambda p: (["n = $a"], "while n >= 0:", ["n -= 1"], "while n > 0:", ["n -= 1"], "n", hrange(p["a"], -1, -1), hrange(p["a"], 0, -1),
                ">= 0 includes 0.")),
    (lambda p: (["xs = $xs3"], "for i, x in enumerate(xs, 1):", [], "for i, x in enumerate(xs):", [], "i", [1, 2, 3], [0, 1, 2],
                "enumerate counts from 0 unless you give it a start.")),
    (lambda p: (["xs = $xs3"], "for i in range(1, len(xs) + 1):", [], "for i in range(1, len(xs)):", [], "i", [1, 2, 3], [1, 2],
                "To reach len(xs) the range must end at len(xs) + 1.")),
    (lambda p: (["xs = $xs"], "for i in range(len(xs) - 1, -1, -1):", [], "for i in range(len(xs) - 1, 0, -1):", [], "xs[i]",
                [p["xs"][len(p["xs"]) - 1 - j] for j in range(len(p["xs"]))],
                [p["xs"][len(p["xs"]) - 1 - j] for j in range(len(p["xs"]) - 1)], "To include position 0 the end must be -1.")),
]


def _ob_make(spec, body) -> Maker:
    fmt, fn = body

    def make(rng: random.Random) -> Item:
        for _ in range(50):
            p = params(rng)
            xs = ints(rng, 5, 1, 9)
            p.update(lo=min(p["a"], p["b"]), hi=max(p["a"], p["b"]), xs=xs, xs3=xs[:3], k=rng.randint(1, 3))
            pre, g_head, g_tail, b_head, b_tail, var, g_seq, b_seq, why = spec(p)
            g_out, b_out = [fn(v) for v in g_seq], [fn(v) for v in b_seq]
            if g_out and b_out and g_out != b_out:
                break
        else:
            raise AssertionError("no distinct pair")
        text = dict(p, xs=str(xs), xs3=str(xs[:3]))
        shown = Template(fmt).substitute(v=var)

        def code(head: str, tail: list[str]) -> list[str]:
            return [Template(head).substitute(text), "    print(" + shown + ")"] + ["    " + t for t in tail]

        pre_lines = [Template(x).substitute(text) for x in pre]
        good, bad = code(g_head, g_tail), code(b_head, b_tail)
        first, second = (good, bad) if rng.random() < 0.5 else (bad, good)
        want = spaced(g_out)
        prompt = "\n".join(pre_lines + [f"# want: {want}", "# 1)"] + first + ["# 2)"] + second)
        prog1, prog2 = "\n".join(pre_lines + first), "\n".join(pre_lines + second)
        return Item(prompt, "1" if first is good else "2", Template(why).safe_substitute(text),
                    check=check_two_loops(prog1, prog2, want))
    make.__name__ = "ob_" + str(id(spec))
    return make


OFF_BY_ONE = [_ob_make(spec, body) for spec in OB_SPECS for body in BODIES]


# ── 8. Typo Hunt ────────────────────────────────────────────────────────

def _typo(code: str, typo: str, fix: str) -> Maker:
    def make(rng: random.Random) -> Item:
        p = params(rng)
        src = Template(code).substitute(p)
        fixed = re.sub(rf"\b{typo}\b", fix, src)
        assert fixed != src
        return Item(src, typo, f"{typo} is a misspelling of {fix}.", check=check_typo(src, typo, fixed))
    make.__name__ = "typo_" + typo
    return make


TYPO_ROWS = [
    ("total = 0\nfor n in [$a, $b]:\n    total = totl + n", "totl", "total"),
    ('name = "$w"\nprint(name)\nprint(nmae)', "nmae", "name"),
    ("count = $a\ncount = count + 1\nprint(cont)", "cont", "count"),
    ("price = $a\ntax = price * 2\nprint(prcie + tax)", "prcie", "price"),
    ("score = $a\nbonus = $b\nprint(scroe + bonus)", "scroe", "score"),
    ("items = [$a, $b]\nfor item in items:\n    print(itme)", "itme", "item"),
    ('word = "$w"\nprint(word.upper())\nprint(wrod)', "wrod", "word"),
    ("x = $a\ny = x + 1\npritn(y)", "pritn", "print"),
    ('x = $a\nprnt(x)\nprint("done")', "prnt", "print"),
    ('print("start")\nprin("$w")', "prin", "print"),
    ("nums = [$a, $b]\nprint(lenght(nums))", "lenght", "len"),
    ("nums = [$a, $b]\nprint(lne(nums))", "lne", "len"),
    ("nums = [$a, $b, $c]\nprint(smu(nums))", "smu", "sum"),
    ("nums = [$a, $b, $c]\nprint(mxa(nums))", "mxa", "max"),
    ("nums = [$a, $b, $c]\nprint(mni(nums))", "mni", "min"),
    ("nums = [$c, $a, $b]\nprint(sroted(nums))", "sroted", "sorted"),
    ('n = "$a"\nprint(itn(n) + 1)', "itn", "int"),
    ("x = $a\ntext = srt(x)\nprint(text)", "srt", "str"),
    ("nums = [$a, $b]\nprint(lsit(nums))", "lsit", "list"),
    ("for i in rnage($a):\n    print(i)", "rnage", "range"),
    ("for i in rang($a):\n    print(i)", "rang", "range"),
    ("for i in ragne($a):\n    print(i)\nprint(i)", "ragne", "range"),
    ('for i, w in enumarate(["$w", "$v"]):\n    print(i, w)', "enumarate", "enumerate"),
    ("print(abs(-$a))\nprint(asb(-$b))", "asb", "abs"),
    ("print(round(2.567, 2))\nprint(rond(3.14159, 2))", "rond", "round"),
    ("nums = [$a]\nnums.apend($b)\nprint(nums)", "apend", "append"),
    ("nums = [$a]\nnums.appnd($b)\nprint(nums)", "appnd", "append"),
    ("nums = [$a]\nnums.extned([$b])\nprint(nums)", "extned", "extend"),
    ("nums = [$b, $a]\nnums.sor()\nprint(nums)", "sor", "sort"),
    ("nums = [$a, $b]\nnums.revers()\nprint(nums)", "revers", "reverse"),
    ("nums = [$a, $b]\nnums.popp()\nprint(nums)", "popp", "pop"),
    ('word = "$w"\nprint(word.uper())\nprint(word)', "uper", "upper"),
    ('word = "$w"\nprint(word.lowr())', "lowr", "lower"),
    ('word = "$w "\nprint(word.strp())', "strp", "strip"),
    ('word = "$w $v"\nprint(word.splitt())', "splitt", "split"),
    ('word = "$w"\nprint(word.replce("o", "0"))', "replce", "replace"),
    ('word = "$w"\nprint(word.startwith("f"))', "startwith", "startswith"),
    ('word = "$w"\nprint(word.endwith("e"))', "endwith", "endswith"),
    ('word = "$w"\nprint(word.captalize())', "captalize", "capitalize"),
    ('d = {"a": $a}\nprint(d.gett("a"))', "gett", "get"),
    ('d = {"a": $a}\nfor k, v in d.itmes():\n    print(k, v)', "itmes", "items"),
    ('d = {"a": $a}\nprint(list(d.keyss()))', "keyss", "keys"),
    ('d = {"a": $a}\nprint(list(d.valus()))', "valus", "values"),
    ('class Dog:\n    def __init__(self, name):\n        slef.name = name\nd = Dog("$w")', "slef", "self"),
    ('class Dog:\n    def bark(self):\n        print("woof")\nDog().bakr()', "bakr", "bark"),
    ("ok = Ture\nprint(ok)", "Ture", "True"),
    ("ok = Flase\nprint(ok)", "Flase", "False"),
    ("ok = $a > 1 and Fasle\nprint(ok)", "Fasle", "False"),
    ("x = none\nprint(x)", "none", "None"),
    ("x = Nnoe\nprint(x)", "Nnoe", "None"),
    ("fro i in range($a):\n    print(i)", "fro", "for"),
    ("whlie True:\n    break", "whlie", "while"),
    ("def f(n):\n    retrun n * 2\nprint(f($a))", "retrun", "return"),
    ("x = $a\nif x > 1:\n    print(1)\nesle:\n    print(2)", "esle", "else"),
    ("x = $a\nif x > 1:\n    print(1)\neilf x > 0:\n    print(2)", "eilf", "elif"),
    ("improt math\nprint(math.pi)", "improt", "import"),
    ("dfe f():\n    pass\nf()", "dfe", "def"),
    ("from math improt sqrt\nprint(sqrt($a))", "improt", "import"),
    ("try:\n    print($a)\nexcpet:\n    print(0)", "excpet", "except"),
    ("while True:\n    print($a)\n    braek", "braek", "break"),
    ("for i in range($a):\n    contiue", "contiue", "continue"),
]

TYPO = [_typo(*r) for r in TYPO_ROWS]


# <<END>>
