"""Brain Drills: short, timed coding reflex drills, scored as a "code age".

After the Nintendo DS brain-training games: a few activities of about a
minute each, answered as fast as you can, and a score that says how old
your coding reflexes act - 20 at their sharpest, 80 at their slowest -
which you try to bring down day by day. A daily stamp for training at all,
and a Code age check (three activities in a row) whose result is charted.

Every activity is generated fresh each time from templates, so there is
nothing to memorise but the language - JavaScript or Python, switched on
the screen (the Python templates are in pythonic.py). Each answer is worked
out here, in Python, by modelling what the language does; tests/test_brain.py
(JavaScript, through node) and tests/test_brain_python.py (Python, through
the real interpreter) then run every template to hold the model to the real
thing (the oracle rule: the expected answer comes from somewhere other than
the code under test). Code age is kept per language.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable

from . import pythonic
from .items import Item

# ── Items and activities ────────────────────────────────────────────────


@dataclass(frozen=True)
class Activity:
    id: str
    title: str
    blurb: str
    #: The question every item asks.
    question: str
    count: int
    #: "type" (type the answer) or "pick" (one of two keys).
    kind: str
    #: Seconds per item at the sharpest (age 20) and at the slowest (age 80).
    par: float
    slow: float
    make: Callable[[random.Random], Item]
    #: For "pick": the two answers, left key first.
    choices: tuple[str, str] = ("", "")
    #: Variable Recall shows something first, for this many seconds.
    show_seconds: float = 0.0
    #: The Python version: its generator, and its wording where it differs.
    make_py: Callable[[random.Random], Item] | None = None
    question_py: str = ""
    blurb_py: str = ""


LANGUAGES = ("javascript", "python")


def _num(x: float) -> str:
    """A number as console.log writes it."""
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def _b(x: bool) -> str:
    return "true" if x else "false"


# ── 1. Quick Eval ───────────────────────────────────────────────────────

_WORDS = ("farm", "drone", "carrot", "loop", "code", "pumpkin", "array", "key", "grid", "tree")


def _quick_eval(rng: random.Random) -> Item:
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
    word = rng.choice(_WORDS)
    kind = rng.randrange(22)
    if kind == 0:
        return Item(f"{a} + {b} * {c}", _num(a + b * c), "* happens before +.")
    if kind == 1:
        return Item(f"({a} + {b}) * {c}", _num((a + b) * c), "The brackets go first.")
    if kind == 2:
        big = rng.randint(10, 40)
        return Item(f"{big} % {b}", _num(big % b), f"% is the remainder after dividing by {b}.")
    if kind == 3:
        return Item(f"{a} ** 2", _num(a ** 2), "** is a power: a times itself.")
    if kind == 4:
        big = rng.randint(10, 60)
        return Item(f"Math.floor({big} / {b})", _num(big // b), "/ gives a fraction; Math.floor rounds it down.")
    if kind == 5:
        return Item(f"{a * b} / {b}", _num(a), "This one divides exactly.")
    if kind == 6:
        return Item(f'"{a}" + {b}', f"{a}{b}", "A string + a number joins them into a string.")
    if kind == 7:
        return Item(f'{a} + "{b}"', f"{a}{b}", "A string on either side of + makes it join, not add.")
    if kind == 8:
        return Item(f'"{a}" * {b}', _num(a * b), "* only means multiply, so the string becomes a number.")
    if kind == 9:
        return Item(f'"{a + b}" - {b}', _num(a), "- only means subtract, so the string becomes a number.")
    if kind == 10:
        n = rng.randint(2, 6)
        items = ", ".join(str(rng.randint(0, 9)) for _ in range(n))
        return Item(f"[{items}].length", _num(n), "length counts the items.")
    if kind == 11:
        return Item(f'"{word}".length', _num(len(word)), "length counts the characters.")
    if kind == 12:
        return Item(f"Math.max({a}, {b}, {c})", _num(max(a, b, c)), "The largest.")
    if kind == 13:
        return Item(f"Math.min({a}, {b}, {c})", _num(min(a, b, c)), "The smallest.")
    if kind == 14:
        return Item(f'{a} === "{a}"', "false", "=== also compares types: a number is never a string.")
    if kind == 15:
        return Item(f'{a} == "{a}"', "true", "== converts first, so the string becomes a number.")
    if kind == 16:
        value, answer = rng.choice([
            (str(a), "number"), (f'"{word}"', "string"), ("true", "boolean"),
            ("null", "object"), ("undefined", "undefined"), (f"[{a}]", "object"),
        ])
        why = {"null": "typeof null is \"object\" - a famous mistake in JavaScript itself.",
               f"[{a}]": "Arrays are objects to typeof."}.get(value, "")
        return Item(f"typeof {value}", answer, why)
    if kind == 17:
        return Item(f"[{a}, {b}, {c}][1]", _num(b), "Indexes start at 0, so [1] is the second.")
    if kind == 18:
        return Item(f'"{word}"[0]', word[0], "Index 0 is the first character.")
    if kind == 19:
        return Item(f'{a} + {b} + "{c}"', f"{a + b}{c}", "Left to right: the numbers add, then the string joins.")
    if kind == 20:
        return Item(f'"{c}" + {a} + {b}', f"{c}{a}{b}", "Left to right: it is a string from the start, so both join.")
    return Item(f"!{a}", "false", f"{a} is truthy, so !{a} is false.") if rng.random() < 0.5 else Item(
        "!0", "true", "0 is falsy, so !0 is true.")


# ── 2. Truthy or Falsy ──────────────────────────────────────────────────

#: (JavaScript value, truthy?, why).
_TRUTHY = (
    ("0", False, "0 is falsy."),
    ("1", True, "Every number but 0 and NaN is truthy."),
    ("-1", True, "Negative numbers are truthy."),
    ('""', False, "The empty string is falsy."),
    ('" "', True, "A space is still a character: truthy."),
    ('"0"', True, "A non-empty string is truthy - even \"0\"."),
    ('"false"', True, "It's a non-empty string, so truthy."),
    ("[]", True, "Every array is truthy, even an empty one."),
    ("{}", True, "Every object is truthy, even an empty one."),
    ("null", False, "null is falsy."),
    ("undefined", False, "undefined is falsy."),
    ("NaN", False, "NaN is falsy."),
    ("Infinity", True, "Infinity is a number other than 0: truthy."),
    ("-0", False, "-0 is still 0: falsy."),
    ('"null"', True, "A non-empty string - truthy."),
    ("[0]", True, "An array, whatever is in it: truthy."),
    ("false", False, "false is falsy."),
    ("true", True, "true is truthy."),
    ("0.5", True, "Not 0: truthy."),
    ("() => {}", True, "Functions are truthy."),
    ('"undefined"', True, "A non-empty string - truthy."),
    ("[[]]", True, "An array: truthy."),
)


def _truthy(rng: random.Random) -> Item:
    value, truthy, why = rng.choice(_TRUTHY)
    return Item(value, "truthy" if truthy else "falsy", why, check=f"Boolean({value})")


# ── 3. Loop Count ───────────────────────────────────────────────────────

def _loop_count(rng: random.Random) -> Item:
    kind = rng.randrange(6)
    if kind == 0:
        a, b, s = rng.randint(0, 5), rng.randint(6, 20), rng.randint(1, 4)
        n = max(0, math.ceil((b - a) / s))
        code = f"for (let i = {a}; i < {b}; i += {s})"
        why = f"i takes {n} values below {b}."
    elif kind == 1:
        a, b, s = rng.randint(0, 5), rng.randint(6, 20), rng.randint(1, 4)
        n = max(0, (b - a) // s + 1)
        code = f"for (let i = {a}; i <= {b}; i += {s})"
        why = f"<= includes {b} itself if i lands on it."
    elif kind == 2:
        a, b, s = rng.randint(0, 5), rng.randint(8, 20), rng.randint(1, 4)
        n = max(0, math.ceil((b - a) / s))
        code = f"for (let i = {b}; i > {a}; i -= {s})"
        why = "Counting down works the same way, the other way round."
    elif kind == 3:
        n0 = rng.choice((8, 16, 20, 32, 50, 64, 100))
        steps, v = 0, n0
        while v > 1:
            v //= 2
            steps += 1
        n = steps
        code = f"let n = {n0};\nwhile (n > 1) n = Math.floor(n / 2);"
        why = "Each turn halves n; count the halvings until it reaches 1."
    elif kind == 4:
        limit = rng.choice((10, 20, 50, 100, 64))
        n, i = 0, 1
        while i < limit:
            n += 1
            i *= 2
        code = f"for (let i = 1; i < {limit}; i *= 2)"
        why = "i doubles: 1, 2, 4, 8 ... count the ones below the limit."
    else:
        a = rng.randint(3, 9)
        n = 0
        code = f"for (let i = {a}; i < {a}; i++)"
        why = "i starts where it must stop, so the body never runs."
    body = "\n  count++;" if "while" not in code else ""
    shown = code + (" {" + body + "\n}" if "while" not in code else "")
    check = "let count = 0;\n" + (
        code.replace("n = Math.floor(n / 2);", "{ n = Math.floor(n / 2); count++; }")
        if "while" in code else code + " { count++; }"
    ) + "\ncount"
    return Item(shown, _num(n), why, check=check)


# ── 4. Final Value ──────────────────────────────────────────────────────

def _final_value(rng: random.Random) -> Item:
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 5)
    kind = rng.randrange(8)
    if kind == 0:
        code = f"let x = {a};\nx += {b};\nx *= {c};"
        return Item(code, _num((a + b) * c), "Step by step: add, then multiply.", check=code + "\nx")
    if kind == 1:
        code = f"let x = {a};\nlet y = x;\nx = {b};"
        return Item(code + "\n// y?", _num(a), "y got a copy of the number; changing x later doesn't touch it.",
                    check=code + "\ny")
    if kind == 2:
        n = rng.randint(3, 8)
        code = f"let x = 0;\nfor (let i = 1; i <= {n}; i++) x += i;"
        return Item(code, _num(n * (n + 1) // 2), f"1 + 2 + ... + {n}.", check=code + "\nx")
    if kind == 3:
        code = f"let x = {a};\nx++;\nx *= 2;"
        return Item(code, _num((a + 1) * 2), "x++ adds one first.", check=code + "\nx")
    if kind == 4:
        code = f"const x = [{a}, {b}];\nx.push({c});\nx.length;"
        return Item(code.replace("\nx.length;", "\n// x.length?"), "3", "push adds one: three items.",
                    check=code.replace("\nx.length;", "") + "\nx.length")
    if kind == 5:
        code = f"let x = {a};\nif (x > {b}) {{\n  x = x - {b};\n}} else {{\n  x = x + {b};\n}}"
        answer = a - b if a > b else a + b
        return Item(code, _num(answer), f"{a} > {b} is {_b(a > b)}.", check=code + "\nx")
    if kind == 6:
        code = 'let x = "ab";\nx = x + x;\nx = x.length;'
        return Item(code, "4", "\"abab\" has four characters.", check=code + "\nx")
    code = f"let x = {a};\nlet y = {b};\n[x, y] = [y, x];"
    return Item(code, _num(b), "The swap trades the two values.", check=code + "\nx")


# ── 5. Bracket Check ────────────────────────────────────────────────────

_PAIRS = {"(": ")", "[": "]", "{": "}"}


def balanced(text: str) -> bool:
    stack: list[str] = []
    for ch in text:
        if ch in _PAIRS:
            stack.append(_PAIRS[ch])
        elif not stack or stack.pop() != ch:
            return False
    return not stack


def _bracket_check(rng: random.Random) -> Item:
    def build(depth: int) -> str:
        out = ""
        while len(out) < 2 or rng.random() < 0.4:
            o = rng.choice("([{")
            inner = build(depth + 1) if depth < 2 and rng.random() < 0.6 else ""
            out += o + inner + _PAIRS[o]
            if len(out) > 8:
                break
        return out

    text = build(0)
    if rng.random() < 0.5:
        chars = list(text)
        how = rng.randrange(3)
        if how == 0:  # one closer becomes the wrong kind
            i = rng.choice([k for k, ch in enumerate(chars) if ch in ")]}"])
            chars[i] = rng.choice([c for c in ")]}" if c != chars[i]])
        elif how == 1:  # one bracket goes missing
            del chars[rng.randrange(len(chars))]
        else:  # two neighbours swap
            i = rng.randrange(len(chars) - 1)
            chars[i], chars[i + 1] = chars[i + 1], chars[i]
        text = "".join(chars)
    ok = balanced(text)
    return Item(text, "yes" if ok else "no",
                "Every opener closes, innermost first." if ok else "Something closes the wrong one, or never closes.")


# ── 6. Variable Recall ──────────────────────────────────────────────────

def _recall(rng: random.Random) -> Item:
    n = rng.randint(3, 5)
    names = rng.sample("abcdefghkmnpqrstwxyz", n)
    values = [rng.randint(0, 20) for _ in names]
    shown = "\n".join(f"let {k} = {v};" for k, v in zip(names, values))
    ask = rng.randrange(n)
    return Item(f"{names[ask]}?", str(values[ask]), shown.replace("\n", "  "), show=shown)


# ── 7. Syntax Snap ──────────────────────────────────────────────────────

#: (line, valid JavaScript?, why). Every line is held to node by the tests.
_SYNTAX = (
    ("const x = 5;", True, ""),
    ("cosnt x = 5;", False, "cosnt is a typo for const."),
    ("let 2x = 1;", False, "A name can't start with a digit."),
    ("let x2 = 1;", True, "Digits are fine after the first character."),
    ("if (x > 3) { x--; }", True, ""),
    ("if x > 3 { x--; }", False, "JavaScript's if needs brackets round the condition."),
    ("for (let i = 0; i < 3; i++) {}", True, ""),
    ("for (let i = 0, i < 3, i++) {}", False, "The parts of a for are separated by ;, not ,."),
    ("const add = (a, b) => a + b;", True, ""),
    ("const add = (a, b) -> a + b;", False, "The arrow is =>, not ->."),
    ("function greet(name) { return 'hi ' + name; }", True, ""),
    ("function greet(name) { return 'hi ' + name; ", False, "The function's { never closes."),
    ("const a;", False, "A const needs a value when it's made."),
    ("let a;", True, "let can start empty."),
    ("let let = 1;", False, "let is a keyword, not a name."),
    ("const list = [1, 2, 3,];", True, "A trailing comma in an array is allowed."),
    ("const o = { a: 1, b: 2 };", True, ""),
    ("const o = { a = 1, b = 2 };", False, "Object properties use :, not =."),
    ("console.log(`total: ${3 + 4}`);", True, ""),
    ("console.log('total: ${3 + 4}');", True, "Valid - but ${} only works in backticks, so it prints the braces."),
    ("x => x * 2;", True, ""),
    ("const f = function() {};", True, ""),
    ("else { x = 1; }", False, "An else needs an if before it."),
    ("while (true) break;", True, ""),
    ("return 5;", False, "return only works inside a function."),
    ("const [a, b] = [1, 2];", True, ""),
    ("const {a, b} = {a: 1, b: 2};", True, ""),
    ("let x = 5\nlet y = 6", True, "Semicolons are optional here."),
    ("x === = 3;", False, "=== is one operator; there's a stray =."),
    ("const s = 'it's';", False, "The ' inside ends the string early."),
    ("const s = \"it's\";", True, "Double quotes can hold a '."),
    ("import x from;", False, "from needs a module after it."),
    ("const n = 0xFF;", True, "0x starts a hexadecimal number."),
    ("const n = 1_000_000;", True, "Underscores can separate digits."),
    ("switch (x) { case 1: break; default: }", True, ""),
    ("try { x(); } finally {}", True, "try needs a catch or a finally - this has one."),
    ("try { x(); }", False, "try needs a catch or a finally."),
)


def _syntax_snap(rng: random.Random) -> Item:
    line, ok, why = rng.choice(_SYNTAX)
    return Item(line, "valid" if ok else "invalid", why or ("Valid JavaScript." if ok else ""))


ACTIVITIES: tuple[Activity, ...] = (
    Activity("eval", "Quick Eval", "What does it print? Twenty quick ones.",
             "What does console.log print?", 20, "type", 2.0, 9.0, _quick_eval,
             make_py=pythonic.quick_eval, question_py="What does print() show?"),
    Activity("truthy", "Truthy or Falsy", "In an if, is it true or false? Left for falsy, right for truthy.",
             "Truthy or falsy?", 20, "pick", 0.9, 3.5, _truthy, ("falsy", "truthy"),
             make_py=pythonic.truthy),
    Activity("loops", "Loop Count", "How many times does the loop run?",
             "How many times does the body run?", 10, "type", 3.0, 13.0, _loop_count,
             make_py=pythonic.loop_count),
    Activity("trace", "Final Value", "Follow a few lines in your head.",
             "What is x at the end?", 8, "type", 4.0, 16.0, _final_value,
             make_py=pythonic.final_value),
    Activity("brackets", "Bracket Check", "Balanced or not? Left for no, right for yes.",
             "Balanced?", 16, "pick", 1.0, 4.5, _bracket_check, ("no", "yes"),
             make_py=pythonic.bracket_check),
    Activity("recall", "Variable Recall", "Remember the variables, then answer from memory.",
             "What was it?", 6, "type", 2.5, 9.0, _recall, show_seconds=3.5,
             make_py=pythonic.recall),
    Activity("syntax", "Syntax Snap", "Would JavaScript accept this line? Left for no, right for yes.",
             "Valid JavaScript?", 16, "pick", 1.4, 6.0, _syntax_snap, ("invalid", "valid"),
             make_py=pythonic.syntax_snap, question_py="Valid Python?",
             blurb_py="Would Python accept this line? Left for no, right for yes."),
)

ACTIVITIES_BY_ID = {a.id: a for a in ACTIVITIES}
#: The Code age check: three activities, as the DS check was three tests.
CHECK = ("eval", "truthy", "brackets")


def activity_for(activity_id: str, language: str = "javascript") -> Activity:
    """The activity as played in a language (KeyError for an unknown one)."""
    activity = ACTIVITIES_BY_ID[activity_id]
    if language == "javascript":
        return activity
    if language == "python":
        assert activity.make_py is not None
        return replace(activity, make=activity.make_py, question=activity.question_py or activity.question,
                       blurb=activity.blurb_py or activity.blurb)
    raise KeyError(language)


def make_round(activity_id: str, seed: int | None = None, language: str = "javascript") -> list[Item]:
    """A fresh round of an activity. The same seed gives the same round."""
    activity = activity_for(activity_id, language)
    rng = random.Random(seed)
    items: list[Item] = []
    seen: set[str] = set()
    tries = 0
    while len(items) < activity.count and tries < activity.count * 50:
        tries += 1
        item = activity.make(rng)
        # No repeats in a round, unless the pool is too small to avoid them.
        key = item.prompt + "|" + item.show
        if key in seen and tries < activity.count * 25:
            continue
        seen.add(key)
        items.append(item)
    return items


# ── Scoring: the code age ───────────────────────────────────────────────

def code_age(activity_id: str, seconds: float, errors: int, total: int, language: str = "javascript") -> int:
    """How old your reflexes acted, 20 to 80. Speed per item between the
    activity's par (20) and slow (80) times, and five years for each mistake;
    Variable Recall is about memory, so it is scored on mistakes alone.
    Both languages are held to the same par and slow times."""
    activity = activity_for(activity_id, language)
    total = max(1, total)
    if activity_id == "recall":
        age = 20 + 60 * (errors / total)
    else:
        per = seconds / total
        speed = (per - activity.par) / (activity.slow - activity.par)
        age = 20 + 60 * min(1.0, max(0.0, speed)) + 5 * errors
    return int(round(min(80, max(20, age))))


# ── Keeping results ─────────────────────────────────────────────────────

def save_path() -> Path:
    from code_coach.progress.store import active_store

    return active_store().path.with_name("brain_drills.json")


def _load() -> dict[str, Any]:
    path = save_path()
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and isinstance(raw.get("results"), list):
                return raw
        except (OSError, ValueError):
            pass
    return {"results": []}


def _save(state: dict[str, Any]) -> None:
    path = save_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    tmp.replace(path)


@dataclass
class Result:
    day: str
    activity: str
    seconds: float
    errors: int
    total: int
    age: int
    #: Part of a Code age check (check_id groups the three).
    check_id: str = ""
    #: Which language was played. Rounds saved before Python existed have no
    #: such field in the file and count as JavaScript.
    language: str = "javascript"


def record(activity_id: str, seconds: float, errors: int, total: int, check_id: str = "",
           today: date | None = None, language: str = "javascript") -> Result:
    if activity_id not in ACTIVITIES_BY_ID:
        raise KeyError(activity_id)
    if language not in LANGUAGES:
        raise KeyError(language)
    seconds = max(0.0, float(seconds))
    errors = max(0, int(errors))
    total = max(1, int(total))
    result = Result((today or date.today()).isoformat(), activity_id, round(seconds, 2), errors, total,
                    code_age(activity_id, seconds, errors, total, language), check_id, language)
    state = _load()
    state["results"].append(asdict(result))
    state["results"] = state["results"][-2000:]
    _save(state)
    return result


def summary(today: date | None = None, language: str = "javascript") -> dict[str, Any]:
    """Everything the home screen shows: each activity's best and last and
    the check ages by day (for one language), and the days trained (for the
    stamps and the streak - training in either language counts)."""
    if language not in LANGUAGES:
        raise KeyError(language)
    today = today or date.today()
    all_results = _load()["results"]
    results = [r for r in all_results if r.get("language", "javascript") == language]
    best: dict[str, dict[str, Any]] = {}
    last: dict[str, dict[str, Any]] = {}
    checks: dict[str, list[int]] = {}
    days = {r["day"] for r in all_results}
    for r in results:
        a = r["activity"]
        last[a] = r
        if a not in best or (r["age"], r["seconds"]) < (best[a]["age"], best[a]["seconds"]):
            best[a] = r
        if r.get("check_id"):
            checks.setdefault(r["check_id"], []).append(r["age"])
    # A check's age is the average of its three; a day keeps its best check.
    check_by_day: dict[str, int] = {}
    for check_id, ages in checks.items():
        if len(ages) < len(CHECK):
            continue
        day = check_id.split("/")[0]
        age = int(round(sum(ages) / len(ages)))
        check_by_day[day] = min(age, check_by_day.get(day, 99))
    streak = 0
    d = today
    while d.isoformat() in days:
        streak += 1
        d -= timedelta(days=1)
    recent = [(today - timedelta(days=k)).isoformat() for k in range(27, -1, -1)]
    return {
        "today": today.isoformat(),
        "language": language,
        "languages": list(LANGUAGES),
        "activities": [
            {"id": a.id, "title": a.title, "blurb": a.blurb, "question": a.question, "count": a.count,
             "kind": a.kind, "choices": list(a.choices), "showSeconds": a.show_seconds,
             "best": best.get(a.id), "last": last.get(a.id)}
            for a in (activity_for(x.id, language) for x in ACTIVITIES)
        ],
        "check": list(CHECK),
        "stamps": [{"day": d, "trained": d in days} for d in recent],
        "streak": streak,
        "checkAges": [{"day": d, "age": check_by_day[d]} for d in sorted(check_by_day)][-60:],
        "trainedToday": today.isoformat() in days,
    }


def round_payload(activity_id: str, seed: int | None = None, language: str = "javascript") -> dict[str, Any]:
    items = make_round(activity_id, seed, language)
    return {
        "activity": activity_id,
        "language": language,
        "items": [{"prompt": i.prompt, "answer": i.answer, "explain": i.explain, "show": i.show}
                  for i in items],
    }


def all_items_for_tests(seeds: range, language: str = "javascript") -> list[tuple[str, Item]]:
    """Every activity's items over many seeds - what the oracle tests run."""
    out = []
    for activity in ACTIVITIES:
        for seed in seeds:
            out.extend((activity.id, item) for item in make_round(activity.id, seed, language))
    return out
