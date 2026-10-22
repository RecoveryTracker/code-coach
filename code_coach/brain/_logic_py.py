"""Logic and flow pack, Python side - and the hand models both languages share.

This module is the first half of the pack (the JavaScript templates are in
`_logic_js.py`, which imports the models from here). Nothing here asks a
runtime anything: truthiness is a table, `and`/`or`/`??` are written out as
"keep the left or go to the right", a branch chain is "the first condition
that is true", a bit operation is a loop over bits, and a boolean expression
is a small tree that is both printed as source (with the minimum brackets the
language needs) and evaluated by hand. tests/test_brain_packs.py then runs
every template through the real interpreter and the real node.

Eight activities: Which Value, Which Branch, Same Logic, Truth Table Row,
Ternary Pick, Bit Ops, In Range, Leap & Fizz.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from ._model import (UNDEF, NULL, Maker, _Const, fdiv, find, fmod, ints, ipow, js_show, lit, py_show, tmod, yes_no_js, yes_no_py)
from .items import Item

NAN = _Const("NaN")


def named(name: str, fn: Maker) -> Maker:
    """The template under a name (the tests print it when it fails)."""
    fn.__name__ = name
    return fn


# ── Truthiness, by table ────────────────────────────────────────────────

def py_truthy(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, (str, list, tuple, dict)):
        return len(v) > 0
    return True


def js_truthy(v: Any) -> bool:
    if v is UNDEF or v is NULL or v is NAN:
        return False
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        return len(v) > 0
    return True  # every array and object


def truthy_for(lang: str) -> Callable[[Any], bool]:
    return py_truthy if lang == "py" else js_truthy


def show(lang: str, v: Any, nested: bool = False) -> str:
    """How the language prints a value (nested: as inside a list, strings quoted)."""
    return py_show(v, nested) if lang == "py" else js_show(v, nested)


def tf(lang: str, b: bool) -> str:
    """True/False in the language's spelling."""
    return show(lang, bool(b))


def say(truthy: bool) -> str:
    return "truthy" if truthy else "falsy"


# ── Value trees: and / or / not / ?? over literal values ────────────────
#
# A node is ("v", source, value) | ("p", node) [brackets] | ("not", node) |
# ("and" | "or" | "nn", left, right). Built from a spec of class letters.

_PREC = {"or": 1, "nn": 1, "and": 2}
_WORDS = {"py": {"and": " and ", "or": " or ", "not": "not "},
          "js": {"and": " && ", "or": " || ", "nn": " ?? ", "not": "!"}}


def _needs(child: str, parent: str) -> bool:
    if child in ("v", "not", "p"):
        return False
    if parent == "not":
        return True
    if child == parent:
        return False
    if "nn" in (child, parent):  # JavaScript refuses ?? mixed with || or && without brackets
        return True
    return _PREC[child] < _PREC[parent]


def vsrc(node: tuple, lang: str) -> str:
    """The node as source, with only the brackets the language needs (plus any ("p", ...) the template asked for)."""
    k = node[0]
    if k == "v":
        return node[1]
    if k == "p":
        return "(" + vsrc(node[1], lang) + ")"
    if k == "not":
        inner = vsrc(node[1], lang)
        return _WORDS[lang]["not"] + ("(" + inner + ")" if _needs(node[1][0], "not") else inner)
    parts = []
    for child in node[1:]:
        s = vsrc(child, lang)
        parts.append("(" + s + ")" if _needs(child[0], k) else s)
    return _WORDS[lang][k].join(parts)


def veval(node: tuple, truthy: Callable[[Any], bool]) -> Any:
    k = node[0]
    if k == "v":
        return node[2]
    if k == "p":
        return veval(node[1], truthy)
    if k == "not":
        return not truthy(veval(node[1], truthy))
    left = veval(node[1], truthy)
    if k == "and":
        return veval(node[2], truthy) if truthy(left) else left
    if k == "or":
        return left if truthy(left) else veval(node[2], truthy)
    return left if (left is not UNDEF and left is not NULL) else veval(node[2], truthy)


def vwhy(node: tuple, lang: str) -> str:
    """One sentence on the top operator of the node (after the inside is worked out)."""
    truthy = truthy_for(lang)
    while node[0] == "p":
        node = node[1]
    k = node[0]
    if k == "v":
        return "That is just the value itself."
    lead = "Work out the inside first. " if any(c[0] not in ("v",) for c in node[1:]) else ""
    if k == "not":
        v = veval(node[1], truthy)
        return f"{lead}{show(lang, v, True)} is {say(truthy(v))}, so not gives {tf(lang, not truthy(v))}."
    left = veval(node[1], truthy)
    sl = show(lang, left, True)
    if k == "and":
        if truthy(left):
            return f"{lead}{sl} is truthy, so and goes on and gives the right side."
        return f"{lead}{sl} is falsy, so and stops there and gives it: the right side never runs."
    if k == "or":
        if truthy(left):
            return f"{lead}{sl} is truthy, so or stops there and gives it: the right side never runs."
        return f"{lead}{sl} is falsy, so or goes on and gives the right side."
    if left is UNDEF or left is NULL:
        return f"{lead}{sl} is nullish, so ?? goes on and gives the right side."
    return f"{lead}{sl} is not null or undefined, so ?? keeps it - even if it is falsy."


def build(spec: Any, rng: random.Random, pools: dict[str, list], used: set[str]) -> tuple:
    """A node from a spec: a class letter ('T' truthy, 'F' falsy, 'X' any...) or (op, spec...)."""
    if isinstance(spec, str):
        options = [p for p in pools[spec] if p[0] not in used] or pools[spec]
        src, val = rng.choice(options)
        used.add(src)
        return ("v", src, val)
    return (spec[0],) + tuple(build(s, rng, pools, used) for s in spec[1:])


def finish(lang: str, src: str, result: Any) -> tuple[str, str]:
    """(source, answer): an empty string would print as nothing, so it is shown through repr / JSON.stringify."""
    if isinstance(result, str) and result == "":
        if lang == "py":
            return f"repr({src})", "''"
        return f"JSON.stringify({src})", '""'
    return src, show(lang, result)


def value_item(node: tuple, lang: str, prefix: str = "", why: str = "") -> Item:
    result = veval(node, truthy_for(lang))
    src, answer = finish(lang, vsrc(node, lang), result)
    if src != vsrc(node, lang):
        why = (why or vwhy(node, lang)) + " (The empty string is wrapped so that it shows.)"
    return Item(prefix + src, answer, why or vwhy(node, lang))


def value_template(tag: str, spec: Any, pools: dict[str, list], lang: str) -> Maker:
    def make(rng: random.Random) -> Item:
        return value_item(build(spec, rng, pools, set()), lang)
    return named("value_" + tag, make)


# ── Boolean trees over named variables ──────────────────────────────────
#
# ("var", name) | ("cmp", name, op, k) | ("mod", name, m, r) [name % m == r] | ("in", name, values)
# | ("notin", name, values) | ("not", node) | ("p", node) | ("and" | "or", left, right).
# A variable is a True/False or a whole number, as the environment says.

def B_VAR(n: str) -> tuple:
    return ("var", n)


def B_CMP(n: str, op: str, k: int) -> tuple:
    return ("cmp", n, op, k)


def B_MOD(n: str, m: int, r: int) -> tuple:
    return ("mod", n, m, r)


def B_IN(n: str, values: tuple[int, ...]) -> tuple:
    return ("in", n, values)


def B_RAW(py: str, js: str, fn: Callable[[dict], Any], names: tuple[str, ...]) -> tuple:
    """A test written out in each language, with the hand model `fn(env)` of what it says."""
    return ("raw", py, js, fn, names)


def B_NOT(x: tuple) -> tuple:
    return ("not", x)


def B_AND(x: tuple, y: tuple) -> tuple:
    return ("and", x, y)


def B_OR(x: tuple, y: tuple) -> tuple:
    return ("or", x, y)


def B_P(x: tuple) -> tuple:
    return ("p", x)


def beval(node: tuple, env: dict[str, Any]) -> bool:
    k = node[0]
    if k == "var":
        return bool(env[node[1]])
    if k == "p":
        return beval(node[1], env)
    if k == "not":
        return not beval(node[1], env)
    if k == "and":
        return beval(node[1], env) and beval(node[2], env)
    if k == "or":
        return beval(node[1], env) or beval(node[2], env)
    if k == "raw":
        return bool(node[3](env))
    x = env[node[1]]
    if k == "cmp":
        op, n = node[2], node[3]
        return {">": x > n, ">=": x >= n, "<": x < n, "<=": x <= n, "==": x == n, "!=": x != n}[op]
    if k == "mod":
        return fmod(x, node[2]) == node[3]
    if k == "in":
        return x in node[2]
    if k == "notin":
        return x not in node[2]
    raise ValueError(k)


def bvars(node: tuple) -> list[str]:
    """The variable names a tree uses, in order of first appearance."""
    out: list[str] = []

    def walk(n: tuple) -> None:
        if n[0] == "raw":
            out.extend(v for v in n[4] if v not in out)
            return
        if n[0] in ("var", "cmp", "mod", "in", "notin"):
            if n[1] not in out:
                out.append(n[1])
            return
        for c in n[1:]:
            walk(c)
    walk(node)
    return out


_BPREC = {"or": 1, "and": 2}


def _bneeds(child: str, parent: str) -> bool:
    if child in ("var", "not", "p", "in", "notin"):
        return False
    if parent == "not":
        return True
    if child in ("cmp", "mod", "raw"):
        return False
    if child == parent:
        return False
    return _BPREC[child] < _BPREC[parent]


def bsrc(node: tuple, lang: str) -> str:
    k = node[0]
    if k == "var":
        return node[1]
    if k == "p":
        return "(" + bsrc(node[1], lang) + ")"
    if k == "raw":
        return node[1] if lang == "py" else node[2]
    if k == "cmp":
        op = node[2]
        if lang == "js":
            op = {"==": "===", "!=": "!=="}.get(op, op)
        return f"{node[1]} {op} {node[3]}"
    if k == "mod":
        return f"{node[1]} % {node[2]} {'===' if lang == 'js' else '=='} {node[3]}"
    if k in ("in", "notin"):
        items = ", ".join(str(v) for v in node[2])
        if lang == "py":
            return f"{node[1]} {'in' if k == 'in' else 'not in'} ({items}{',' if len(node[2]) == 1 else ''})"
        return ("" if k == "in" else "!") + f"[{items}].includes({node[1]})"
    if k == "not":
        inner = bsrc(node[1], lang)
        word = "not " if lang == "py" else "!"
        wrapped = _bneeds(node[1][0], "not") or node[1][0] in ("cmp", "mod", "raw")
        return word + ("(" + inner + ")" if wrapped else inner)
    word = " and " if lang == "py" else " && "
    if k == "or":
        word = " or " if lang == "py" else " || "
    parts = []
    for child in node[1:]:
        s = bsrc(child, lang)
        parts.append("(" + s + ")" if _bneeds(child[0], k) else s)
    return word.join(parts)


def decls(lang: str, env: dict[str, Any]) -> list[str]:
    """`a = True` lines (or `const a = true;`) for an environment."""
    out = []
    for name, v in env.items():
        text = tf(lang, v) if isinstance(v, bool) else lit(v) if isinstance(v, (str, list)) else str(v)
        out.append(f"{name} = {text}" if lang == "py" else f"const {name} = {text};")
    return out


def env_text(lang: str, env: dict[str, Any]) -> str:
    return ", ".join(f"{n} = {tf(lang, v) if isinstance(v, bool) else lit(v) if isinstance(v, (str, list)) else v}"
                     for n, v in env.items())


# ── 1. Which Value ──────────────────────────────────────────────────────

PY_VALUES: dict[str, list] = {
    "T": [("1", 1), ("2", 2), ("5", 5), ("9", 9), ("-1", -1), ('"hi"', "hi"), ('"ab"', "ab"), ('"0"', "0"),
          ('"yes"', "yes"), ("[0]", [0]), ("[1, 2]", [1, 2]), ("(1,)", (1,)), ("True", True)],
    "F": [("0", 0), ('""', ""), ("None", None), ("False", False), ("[]", []), ("{}", {}), ("()", ()),
          ("0.0", 0.0)],
}
PY_VALUES["X"] = PY_VALUES["T"] + PY_VALUES["F"]

#: (tag, spec): every shape of and/or/not worth a reflex.
PY_VALUE_SPECS: list[tuple[str, Any]] = [
    ("or_t_x", ("or", "T", "X")), ("or_f_t", ("or", "F", "T")), ("or_f_f", ("or", "F", "F")),
    ("or_x_x", ("or", "X", "X")), ("and_f_x", ("and", "F", "X")), ("and_t_t", ("and", "T", "T")),
    ("and_t_f", ("and", "T", "F")), ("and_x_x", ("and", "X", "X")),
    ("not_x", ("not", "X")), ("not_not_x", ("not", ("not", "X"))),
    ("or3_ffx", ("or", ("or", "F", "F"), "X")), ("or3_ftx", ("or", ("or", "F", "T"), "X")),
    ("or3_fff", ("or", ("or", "F", "F"), "F")), ("or3_txx", ("or", ("or", "T", "X"), "X")),
    ("and3_ttt", ("and", ("and", "T", "T"), "T")), ("and3_ttf", ("and", ("and", "T", "T"), "F")),
    ("and3_tfx", ("and", ("and", "T", "F"), "X")), ("and3_fxx", ("and", ("and", "F", "X"), "X")),
    ("or_and_f", ("or", "F", ("and", "T", "T"))), ("or_and_t", ("or", "T", ("and", "X", "X"))),
    ("and_or_pf", ("and", ("p", ("or", "F", "T")), "X")), ("and_or_pt", ("and", ("p", ("or", "T", "X")), "F")),
    ("and_or_ff", ("or", ("and", "F", "X"), "T")), ("and_or_tt", ("or", ("and", "T", "T"), "X")),
    ("and_or_tf", ("or", ("and", "T", "F"), "X")),
    ("not_or", ("not", ("p", ("or", "F", "F")))), ("not_and", ("not", ("p", ("and", "T", "X")))),
    ("not_then_and", ("and", ("not", "X"), "X")), ("not_then_or", ("or", ("not", "X"), "X")),
    ("or_not", ("or", "X", ("not", "X"))), ("and_not", ("and", "X", ("not", "X"))),
    ("two_ands", ("or", ("p", ("and", "T", "X")), ("p", ("and", "F", "X")))),
    ("or_or_and", ("or", ("or", "F", "F"), ("and", "T", "X"))),
]


def v_guard(rng: random.Random) -> Item:
    xs = ints(rng, rng.randint(2, 3)) if rng.random() < 0.6 else []
    prompt = f"items = {lit(xs)}\nitems and items[0]"
    got = xs[0] if xs else xs
    why = ("A non-empty list is truthy, so and goes on to items[0]." if xs
           else "An empty list is falsy, so and stops there and gives it - items[0] would have crashed.")
    return Item(prompt, py_show(got), why)


def v_default_name(rng: random.Random) -> Item:
    name, shown = rng.choice([("", '""'), ("ana", '"ana"'), ("", '""'), ("bo", '"bo"')])
    got = name or "guest"
    return Item(f'name = {shown}\nname or "guest"', got,
                "A name is kept if it has any text; an empty one is falsy, so the default after or is used.")


def v_default_count(rng: random.Random) -> Item:
    n = rng.choice([0, 0, 3, 7, 12])
    got = n if n else 10
    return Item(f"count = {n}\ncount or 10", str(got),
                "or keeps a truthy count; 0 is falsy, so the default 10 replaces it - a classic bug when 0 is a real value.")


def v_zero_div_or(rng: random.Random) -> Item:
    a = rng.randint(1, 9)
    return Item(f"{a} or 1 / 0", str(a), f"{a} is truthy, so or stops there: the 1 / 0 never runs, and so never crashes.")


def v_zero_div_and(rng: random.Random) -> Item:
    src, v = rng.choice([("0", 0), ('""', ""), ("None", None), ("False", False), ("[]", [])])
    out = finish("py", f"{src} and 1 / 0", v)
    return Item(out[0], out[1], f"{show('py', v, True)} is falsy, so and stops there: the 1 / 0 never runs.")


def v_cmp_and_str(rng: random.Random) -> Item:
    a, b = ints(rng, 2)
    got = "yes" if a > b else False
    return Item(f'{a} > {b} and "yes"', py_show(got),
                f"{a} > {b} is {tf('py', a > b)}: " + ("and goes on and gives \"yes\"." if a > b else "and stops and gives that False."))


def v_cmp_idiom(rng: random.Random) -> Item:
    a, b = ints(rng, 2)
    got = "big" if a > b else "small"
    return Item(f'{a} > {b} and "big" or "small"', got,
                "The old and/or idiom for a choice: " + ("true, so and gives \"big\", which or keeps." if a > b
                                                         else "false, so and gives False, which or throws away for \"small\"."))


def v_eq_or(rng: random.Random) -> Item:
    a, b, c = ints(rng, 3)
    if rng.random() < 0.5:
        b = a
    got = True if a == b else c
    return Item(f"{a} == {b} or {c}", py_show(got),
                f"{a} == {b} is {tf('py', a == b)}: " + ("or stops and gives that True." if a == b else f"or goes on and gives {c}."))


def v_len_or(rng: random.Random) -> Item:
    s = rng.choice(["", "hi", "code", ""])
    got = len(s) if s else "empty"
    return Item(f's = "{s}"\nlen(s) or "empty"', py_show(got),
                "len is 0 for an empty string, and 0 is falsy, so or moves on." if not s else "len is not 0, so or keeps it.")


def v_bool_or(rng: random.Random) -> Item:
    node = build(("or", "X", "X"), rng, PY_VALUES, set())
    r = veval(node, py_truthy)
    return Item(f"bool({vsrc(node, 'py')})", tf("py", py_truthy(r)),
                f"{vwhy(node, 'py')} bool() then turns the result into True or False.")


def v_bool_and(rng: random.Random) -> Item:
    node = build(("and", "X", "X"), rng, PY_VALUES, set())
    r = veval(node, py_truthy)
    return Item(f"bool({vsrc(node, 'py')})", tf("py", py_truthy(r)),
                f"{vwhy(node, 'py')} bool() then turns the result into True or False.")


def v_any_list(rng: random.Random) -> Item:
    nodes = [build("X", rng, PY_VALUES, set()) for _ in range(rng.randint(3, 4))]
    got = any(py_truthy(n[2]) for n in nodes)
    return Item("any([" + ", ".join(n[1] for n in nodes) + "])", tf("py", got),
                "any is True if at least one item is truthy." if got else "any is False when every item is falsy.")


def v_all_list(rng: random.Random) -> Item:
    pool = "T" if rng.random() < 0.5 else "X"
    nodes = [build(pool, rng, PY_VALUES, set()) for _ in range(rng.randint(3, 4))]
    got = all(py_truthy(n[2]) for n in nodes)
    return Item("all([" + ", ".join(n[1] for n in nodes) + "])", tf("py", got),
                "all is True only when every item is truthy." if got else "all is False as soon as one item is falsy.")


def v_any_empty(rng: random.Random) -> Item:
    if rng.random() < 0.5:
        return Item("any([])", "False", "any of nothing is False: there is no truthy item.")
    return Item("all([])", "True", "all of nothing is True: no item is falsy.")


def v_any_gen(rng: random.Random) -> Item:
    xs = ints(rng, 4)
    t = rng.randint(3, 8)
    if rng.random() < 0.5:
        got = any(x > t for x in xs)
        return Item(f"any(x > {t} for x in {lit(xs)})", tf("py", got), f"Is some item bigger than {t}?")
    got = all(x > t for x in xs)
    return Item(f"all(x > {t} for x in {lit(xs)})", tf("py", got), f"Is every item bigger than {t}?")


def v_chain_var(rng: random.Random) -> Item:
    a = build("F", rng, PY_VALUES, set())
    used = {a[1]}
    b = build("X", rng, PY_VALUES, used)
    c = build("X", rng, PY_VALUES, used)
    r = veval(("or", ("or", a, b), c), py_truthy)
    src, ans = finish("py", "x", r)
    return Item(f"x = {a[1]} or {b[1]} or {c[1]}\n{src}", ans, "or gives the first truthy value, or the last one if none is.")


def v_max_or(rng: random.Random) -> Item:
    a = rng.randint(-3, 3)
    got = max(a, 0) or "zero"
    return Item(f'max({a}, 0) or "zero"', py_show(got),
                f"max({a}, 0) is {max(a, 0)}: " + ("falsy, so or goes on." if not max(a, 0) else "truthy, so or keeps it."))


def v_not_eq(rng: random.Random) -> Item:
    a, b = ints(rng, 2)
    if rng.random() < 0.5:
        b = a
    return Item(f"not {a} == {b}", tf("py", not (a == b)),
                "not binds looser than ==, so this is not ({0} == {1}).".format(a, b))


def v_strip_or(rng: random.Random) -> Item:
    s = rng.choice(["   ", "  ", "  ok  ", " hi"])
    got = s.strip() if s.strip() else "blank"
    src, ans = finish("py", 's.strip() or "blank"', got)
    return Item(f's = "{s}"\n{src}', ans,
                "strip removes the spaces; if nothing is left it is empty, falsy, and or uses the default." if got == "blank"
                else "strip leaves text, which is truthy, so or keeps it.")


def v_none_default(rng: random.Random) -> Item:
    if rng.random() < 0.5:
        return Item("x = None\nx = x or []\nx", "[]", "None is falsy, so x becomes an empty list.")
    n = rng.randint(2, 9)
    return Item(f"x = [{n}]\nx = x or []\nx", f"[{n}]", "A non-empty list is truthy, so or keeps it.")


def v_dict_get(rng: random.Random) -> Item:
    k = rng.choice(["a", "k", "n"])
    v = rng.choice([0, 0, 5, 8])
    got = v or "none"
    return Item(f'd = {{"{k}": {v}}}\nd.get("{k}") or "none"', py_show(got),
                "The key is there, but 0 is falsy, so or still replaces it." if not v else "5 is truthy, so or keeps it."
                if v == 5 else "The value is truthy, so or keeps it.")


def v_in_and(rng: random.Random) -> Item:
    w = rng.choice(["cat", "farm", "tree", "loop"])
    c1, c2 = rng.choice(w), rng.choice("xyzq")
    got = (c1 in w) and (c2 in w)
    op = rng.random() < 0.5
    got2 = (c1 in w) or (c2 in w)
    if op:
        return Item(f'"{c1}" in "{w}" and "{c2}" in "{w}"', tf("py", got), "in is checked on each side; and needs both True.")
    return Item(f'"{c1}" in "{w}" or "{c2}" in "{w}"', tf("py", got2), "in is checked on each side; or needs one True.")


PY_VALUE_CUSTOM: list[Maker] = [v_guard, v_default_name, v_default_count, v_zero_div_or, v_zero_div_and,
                                v_cmp_and_str, v_cmp_idiom, v_eq_or, v_len_or, v_bool_or, v_bool_and, v_any_list,
                                v_all_list, v_any_empty, v_any_gen, v_chain_var, v_max_or, v_not_eq, v_strip_or,
                                v_none_default, v_dict_get, v_in_and]

PY_VALUE = [value_template(tag, spec, PY_VALUES, "py") for tag, spec in PY_VALUE_SPECS] + PY_VALUE_CUSTOM

# ── 2. Which Branch ─────────────────────────────────────────────────────
#
# A template is `f(rng, lang)`; `bind` makes it the Maker of one language.

def bind(fn: Callable[[random.Random, str], Item], lang: str) -> Maker:
    def make(rng: random.Random) -> Item:
        return fn(rng, lang)
    make.__name__ = fn.__name__
    return make


L2 = [("small", "big"), ("low", "high"), ("cold", "hot"), ("short", "tall"), ("weak", "strong"), ("slow", "fast"),
      ("night", "day"), ("cheap", "dear")]
L3 = [("low", "mid", "high"), ("cold", "warm", "hot"), ("small", "medium", "large"), ("child", "teen", "adult"),
      ("red", "amber", "green"), ("bronze", "silver", "gold"), ("easy", "fair", "hard")]
L4 = [("F", "C", "B", "A"), ("tiny", "small", "medium", "large"), ("winter", "spring", "summer", "autumn"),
      ("mild", "warm", "hot", "scorching")]
_OPNAME = {">": "gt", ">=": "ge", "<": "lt", "<=": "le", "==": "eq", "!=": "ne"}


def render_chain(lang: str, branches: list[tuple[tuple, str]], else_label: str | None, style: str,
                 init: str | None) -> list[str]:
    """The if / elif / else lines (style "elif") or separate ifs with an else on the last (style "ifs")."""
    out: list[str] = []
    need_init = style == "ifs" or else_label is None
    if need_init:
        assert init is not None
    if lang == "py":
        if need_init:
            out.append(f'label = "{init}"')
        for i, (cond, lab) in enumerate(branches):
            out.append(f"{'if' if i == 0 or style == 'ifs' else 'elif'} {bsrc(cond, 'py')}:")
            out.append(f'    label = "{lab}"')
        if else_label is not None:
            out.append("else:")
            out.append(f'    label = "{else_label}"')
        return out
    out.append(f'let label = "{init}";' if need_init else "let label;")
    for i, (cond, lab) in enumerate(branches):
        out.append(f"{'if' if i == 0 or style == 'ifs' else 'else if'} ({bsrc(cond, 'js')}) label = \"{lab}\";")
    if else_label is not None:
        out.append(f'else label = "{else_label}";')
    return out


def run_chain(branches: list[tuple[tuple, str]], else_label: str | None, style: str, init: str | None,
              env: dict[str, Any]) -> tuple[str, int]:
    """(the label at the end, the index of the last branch that set it or -1)."""
    label, last = init, -1
    if style == "elif":
        for i, (cond, lab) in enumerate(branches):
            if beval(cond, env):
                return lab, i
        return (else_label if else_label is not None else init), -1  # type: ignore[return-value]
    for i, (cond, lab) in enumerate(branches):
        if beval(cond, env):
            label, last = lab, i
        elif i == len(branches) - 1 and else_label is not None:
            label, last = else_label, -1
    return label, last  # type: ignore[return-value]


def chain_why(lang: str, branches: list[tuple[tuple, str]], else_label: str | None, style: str,
              init: str | None, env: dict[str, Any], got: str) -> str:
    if style == "elif":
        for cond, lab in branches:
            if beval(cond, env):
                return f"Conditions are tried in order and the first true one wins: {bsrc(cond, lang)} is true, so label is {lab}."
        return "No condition is true, so the else runs." if else_label is not None else "No condition is true, so label keeps its start."
    true = [bsrc(c, lang) for c, _ in branches if beval(c, env)]
    last_else = else_label is not None and not beval(branches[-1][0], env)
    if last_else:
        return "Each if is checked on its own; the else belongs only to the last if, and that is false, so the else runs."
    if not true:
        return "No if is true, so label keeps its start."
    return "Each if is checked on its own, so a later true one overwrites an earlier one: " + ", then ".join(true) + "."


def chain_item(lang: str, env: dict[str, Any], branches: list[tuple[tuple, str]], else_label: str | None = None,
               style: str = "elif", init: str | None = None, why: str = "") -> Item:
    lines = decls(lang, env) + render_chain(lang, branches, else_label, style, init)
    prompt = "\n".join(lines)
    got, _ = run_chain(branches, else_label, style, init, env)
    return Item(prompt, got, why or chain_why(lang, branches, else_label, style, init, env, got), check=prompt + "\nlabel")


def _cmp(op: str, k: int, name: str = "n") -> tuple:
    return B_CMP(name, op, k)


def _two_way(op: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        t = rng.randint(3, 12)
        n = max(0, t + rng.choice((-2, -1, 0, 0, 1, 2)))
        l1, l2 = rng.choice(L2)
        return chain_item(lang, {"n": n}, [(_cmp(op, t), l2)], l1)
    f.__name__ = "branch_two_" + _OPNAME[op]
    return f


def _three(kind: str, op: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        lo = rng.randint(3, 8)
        hi = lo + rng.randint(3, 8)
        n = rng.choice((lo - 1, lo, lo + 1, hi - 1, hi, hi + 1, hi + 3))
        a, b, c = rng.choice(L3)
        if kind == "desc":
            branches, other = [(_cmp(op, hi), c), (_cmp(op, lo), b)], a
        elif kind == "asc":
            branches, other = [(_cmp(op, lo), a), (_cmp(op, hi), b)], c
        elif kind == "trap":   # the broad test is first, so the narrow one never gets a turn
            n = rng.choice((lo + 1, hi, hi + 1, hi + 3, lo - 1))
            branches, other = [(_cmp(">", lo), b), (_cmp(">", hi), c)], a
        else:
            n = rng.choice((lo - 1, lo, hi - 1, lo + 1, hi + 2))
            branches, other = [(_cmp("<", hi), b), (_cmp("<", lo), a)], c
        return chain_item(lang, {"n": n}, branches, other)
    f.__name__ = f"branch_three_{kind}_{_OPNAME[op]}"
    return f


def _four(kind: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        t1 = rng.randint(2, 5)
        t2 = t1 + rng.randint(2, 5)
        t3 = t2 + rng.randint(2, 5)
        n = rng.choice((t1 - 1, t1, t2 - 1, t2, t3 - 1, t3, t3 + 2, t1 + 1))
        a, b, c, d = rng.choice(L4)
        if kind == "desc_ge":
            branches, other = [(_cmp(">=", t3), d), (_cmp(">=", t2), c), (_cmp(">=", t1), b)], a
        elif kind == "desc_gt":
            branches, other = [(_cmp(">", t3), d), (_cmp(">", t2), c), (_cmp(">", t1), b)], a
        elif kind == "asc_lt":
            branches, other = [(_cmp("<", t1), a), (_cmp("<", t2), b), (_cmp("<", t3), c)], d
        else:
            branches, other = [(_cmp(">", t1), b), (_cmp(">", t2), c), (_cmp(">", t3), d)], a
        return chain_item(lang, {"n": n}, branches, other)
    f.__name__ = "branch_four_" + kind
    return f


def branch_ifs_override(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(3, 8)
    hi = lo + rng.randint(2, 6)
    a, b, c, _ = rng.choice(L4)
    n = rng.choice((lo, lo + 1, hi, hi + 1, lo - 1))
    return chain_item(lang, {"n": n}, [(_cmp(">", lo), b), (_cmp(">", hi), c)], None, "ifs", a)


def branch_ifs_else_last(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(3, 8)
    hi = lo + rng.randint(2, 6)
    a, b, c, d = rng.choice(L4)
    n = rng.choice((lo - 1, lo + 1, hi + 1, hi, lo))
    return chain_item(lang, {"n": n}, [(_cmp(">", lo), b), (_cmp(">", hi), c)], d, "ifs", a)


def branch_ifs_three(rng: random.Random, lang: str) -> Item:
    t1 = rng.randint(2, 5)
    t2 = t1 + rng.randint(2, 4)
    t3 = t2 + rng.randint(2, 4)
    a, b, c, d = rng.choice(L4)
    n = rng.choice((t1, t1 + 1, t2 + 1, t3 + 1, t3, 0))
    return chain_item(lang, {"n": n}, [(_cmp(">", t1), b), (_cmp(">", t2), c), (_cmp(">", t3), d)], None, "ifs", a)


def branch_ifs_mixed(rng: random.Random, lang: str) -> Item:
    t = rng.randint(4, 9)
    n = rng.randint(1, 14)
    return chain_item(lang, {"n": n}, [(B_MOD("n", 2, 0), "even"), (_cmp(">", t), "big")], None, "ifs", "plain")


def branch_eq_two(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2, 1, 9)
    n = rng.choice((a, b, a + b + 1))
    la, lb, lc, _ = rng.choice(L4)
    return chain_item(lang, {"n": n}, [(_cmp("==", a), la), (_cmp("==", b), lb)], lc)


def branch_eq_three(rng: random.Random, lang: str) -> Item:
    a, b, c = ints(rng, 3, 1, 9)
    n = rng.choice((a, b, c, 0, 10))
    w = rng.choice(L4)
    return chain_item(lang, {"n": n}, [(_cmp("==", a), w[0]), (_cmp("==", b), w[1]), (_cmp("==", c), w[2])], w[3])


def branch_and_range(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(3, 6)
    hi = lo + rng.randint(2, 6)
    n = rng.choice((lo - 1, lo, hi, hi + 1, lo + 1))
    cond = B_AND(_cmp(">=", lo), _cmp("<=", hi))
    return chain_item(lang, {"n": n}, [(cond, "inside")], "outside")


def branch_or_outside(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(3, 6)
    hi = lo + rng.randint(2, 6)
    n = rng.choice((lo - 1, lo, hi, hi + 1, lo + 1))
    cond = B_OR(_cmp("<", lo), _cmp(">", hi))
    return chain_item(lang, {"n": n}, [(cond, "outside")], "inside")


def branch_not_gt(rng: random.Random, lang: str) -> Item:
    t = rng.randint(3, 9)
    n = rng.choice((t - 1, t, t + 1))
    l1, l2 = rng.choice(L2)
    return chain_item(lang, {"n": n}, [(B_NOT(_cmp(">", t)), l1)], l2)


def branch_and_or_prec(rng: random.Random, lang: str) -> Item:
    k1 = rng.randint(2, 4)
    k2 = rng.randint(5, 8)
    n = rng.randint(0, 12)
    cond = B_OR(_cmp("<", k1), B_AND(_cmp(">", k2), B_MOD("n", 2, 0)))
    return chain_item(lang, {"n": n}, [(cond, "yes")], "no",
                      why=f"and binds tighter than or, so the test is n < {k1} or (n > {k2} and n % 2 == 0).")


def branch_and_three(rng: random.Random, lang: str) -> Item:
    n = rng.randint(-3, 9)
    return chain_item(lang, {"n": n}, [(B_AND(_cmp(">", 0), B_MOD("n", 2, 0)), "even"), (_cmp(">", 0), "odd")], "nonpositive")


def branch_not_either(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2, 1, 9)
    n = rng.choice((a, b, 0, 10))
    cond = B_AND(_cmp("!=", a), _cmp("!=", b))
    return chain_item(lang, {"n": n}, [(cond, "other")], "chosen")


def branch_even_odd(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 30)
    return chain_item(lang, {"n": n}, [(B_MOD("n", 2, 0), "even")], "odd")


def branch_div35(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 30)
    return chain_item(lang, {"n": n}, [(B_MOD("n", 3, 0), "fizz"), (B_MOD("n", 5, 0), "buzz")], "plain")


def branch_div15_first(rng: random.Random, lang: str) -> Item:
    n = rng.choice((15, 30, 45, 3, 5, 6, 10, 9, 7, 8, 60, 20))
    return chain_item(lang, {"n": n}, [(B_MOD("n", 15, 0), "fizzbuzz"), (B_MOD("n", 3, 0), "fizz"),
                                       (B_MOD("n", 5, 0), "buzz")], "plain")


def branch_div15_last(rng: random.Random, lang: str) -> Item:
    n = rng.choice((15, 30, 45, 3, 5, 6, 10, 9, 7, 8, 60, 20))
    return chain_item(lang, {"n": n}, [(B_MOD("n", 3, 0), "fizz"), (B_MOD("n", 5, 0), "buzz"),
                                       (B_MOD("n", 15, 0), "fizzbuzz")], "plain",
                      why="The test for 15 comes last, but 3 or 5 catches the number first.")


def branch_mod_pair(rng: random.Random, lang: str) -> Item:
    m1, m2 = rng.choice([(2, 3), (2, 5), (3, 4), (4, 6), (3, 6)])
    n = rng.randint(1, 24)
    return chain_item(lang, {"n": n}, [(B_MOD("n", m1, 0), f"by{m1}"), (B_MOD("n", m2, 0), f"by{m2}")], "neither")


def _str_env(rng: random.Random) -> str:
    return rng.choice(["farm", "drone", "carrot", "loop", "code", "pumpkin", "array", "key", "grid", "tree"])


def branch_str_eq(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["yes", "no", "maybe", "yes"])
    c1 = B_RAW('w == "yes"', 'w === "yes"', lambda e: e["w"] == "yes", ("w",))
    c2 = B_RAW('w == "no"', 'w === "no"', lambda e: e["w"] == "no", ("w",))
    return chain_item(lang, {"w": w}, [(c1, "agree"), (c2, "refuse")], "unsure")


def branch_str_start(rng: random.Random, lang: str) -> Item:
    w = _str_env(rng)
    ch = rng.choice([w[0], w[0], "a", "c", "t"])
    cond = B_RAW(f'w.startswith("{ch}")', f'w.startsWith("{ch}")', lambda e: e["w"][:1] == ch, ("w",))
    l1, l2 = rng.choice(L2)
    return chain_item(lang, {"w": w}, [(cond, l2)], l1)


def branch_str_len(rng: random.Random, lang: str) -> Item:
    w = _str_env(rng)
    t1, t2 = 3, 5
    c1 = B_RAW(f"len(w) <= {t1}", f"w.length <= {t1}", lambda e: len(e["w"]) <= t1, ("w",))
    c2 = B_RAW(f"len(w) <= {t2}", f"w.length <= {t2}", lambda e: len(e["w"]) <= t2, ("w",))
    return chain_item(lang, {"w": w}, [(c1, "short"), (c2, "medium")], "long")


def branch_str_vowel(rng: random.Random, lang: str) -> Item:
    ch = rng.choice("abcdeiopuxyz")
    cond = B_RAW('ch in "aeiou"', '"aeiou".includes(ch)', lambda e: find("aeiou", e["ch"]) != -1, ("ch",))
    return chain_item(lang, {"ch": ch}, [(cond, "vowel")], "consonant")


def branch_str_has(rng: random.Random, lang: str) -> Item:
    w = _str_env(rng)
    ch = rng.choice("oaerk")
    cond = B_RAW(f'"{ch}" in w', f'w.includes("{ch}")', lambda e: find(e["w"], ch) != -1, ("w",))
    return chain_item(lang, {"w": w}, [(cond, "found")], "missing")


def branch_truth_list(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(1, 3)) if rng.random() < 0.5 else []
    py_c = B_RAW("items", "items.length", lambda e: len(e["items"]) > 0, ("items",))
    return chain_item(lang, {"items": xs}, [(py_c, "full")], "empty")


def branch_truth_num(rng: random.Random, lang: str) -> Item:
    n = rng.choice([0, 0, 1, 2, 5])
    cond = B_RAW("n", "n", lambda e: e["n"] != 0, ("n",))
    return chain_item(lang, {"n": n}, [(cond, "nonzero")], "zero")


def branch_truth_str(rng: random.Random, lang: str) -> Item:
    name = rng.choice(["", "ana", "", "0", "bo"])
    cond = B_RAW("name", "name", lambda e: len(e["name"]) > 0, ("name",))
    return chain_item(lang, {"name": name}, [(cond, "named")], "anonymous")


def _nested(kind: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        a = rng.randint(3, 6)
        b = a + rng.randint(2, 5)
        n = rng.choice((a - 1, a + 1, b, b + 1, a))
        x, y, z, w = rng.choice(L4)
        c1, c2 = f"n > {a}", f"n > {b}"
        if kind == "else":
            got = (x if n > b else y) if n > a else z
            if lang == "py":
                lines = [f"n = {n}", f"if {c1}:", f"    if {c2}:", f'        label = "{x}"', "    else:",
                         f'        label = "{y}"', "else:", f'    label = "{z}"']
            else:
                lines = [f"const n = {n};", "let label;", f"if ({c1}) {{", f'  if ({c2}) label = "{x}";',
                         f'  else label = "{y}";', f'}} else label = "{z}";']
            why = "The outer test picks the group; only then does the inner one decide."
        else:
            got = (x if n > b else w) if n > a else z
            if lang == "py":
                lines = [f"n = {n}", f'label = "{w}"', f"if {c1}:", f"    if {c2}:", f'        label = "{x}"',
                         "else:", f'    label = "{z}"']
            else:
                lines = [f"const n = {n};", f'let label = "{w}";', f"if ({c1}) {{", f'  if ({c2}) label = "{x}";',
                         f'}} else label = "{z}";']
            why = "The else belongs to the outer if: when the inner test fails, nothing changes label."
        prompt = "\n".join(lines)
        return Item(prompt, got, why, check=prompt + "\nlabel")
    f.__name__ = "branch_nested_" + kind
    return f


def branch_two_vars(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    return chain_item(lang, {"a": a, "b": b}, [(B_RAW("a > b", "a > b", lambda e: e["a"] > e["b"], ("a", "b")), "first"),
                                              (B_RAW("a == b", "a === b", lambda e: e["a"] == e["b"], ("a", "b")), "tie")],
                      "second")


def branch_sum(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    t = rng.randint(8, 12)
    cond = B_RAW(f"a + b > {t}", f"a + b > {t}", lambda e: e["a"] + e["b"] > t, ("a", "b"))
    cond2 = B_RAW(f"a + b == {t}", f"a + b === {t}", lambda e: e["a"] + e["b"] == t, ("a", "b"))
    return chain_item(lang, {"a": a, "b": b}, [(cond, "over"), (cond2, "exact")], "under")


def branch_max3(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 10), 3)
    c1 = B_RAW("a > b and a > c", "a > b && a > c", lambda e: e["a"] > e["b"] and e["a"] > e["c"], ("a", "b", "c"))
    c2 = B_RAW("b > c", "b > c", lambda e: e["b"] > e["c"], ("b", "c"))
    return chain_item(lang, {"a": a, "b": b, "c": c}, [(c1, "a"), (c2, "b")], "c")


def branch_in_weekend(rng: random.Random, lang: str) -> Item:
    day = rng.randint(1, 7)
    return chain_item(lang, {"day": day}, [(B_IN("day", (6, 7)), "weekend")], "weekday")


def branch_in_two(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 8)
    a, b, c, _ = rng.choice(L4)
    return chain_item(lang, {"n": n}, [(B_IN("n", (1, 2, 3)), a), (B_IN("n", (4, 5, 6)), b)], c)


def branch_bool_and(rng: random.Random, lang: str) -> Item:
    p, q = rng.choice([(True, False), (False, True), (True, True), (False, False)])
    return chain_item(lang, {"raining": p, "cold": q},
                      [(B_AND(B_VAR("raining"), B_VAR("cold")), "coat"), (B_VAR("raining"), "umbrella")], "nothing")


def branch_bool_not(rng: random.Random, lang: str) -> Item:
    p, q = rng.choice([(True, False), (False, True), (True, True), (False, False)])
    return chain_item(lang, {"ready": p, "late": q},
                      [(B_AND(B_VAR("ready"), B_NOT(B_VAR("late"))), "go"), (B_VAR("ready"), "hurry")], "wait")


def branch_bool_or(rng: random.Random, lang: str) -> Item:
    p, q, r = (rng.random() < 0.5 for _ in range(3))
    cond = B_OR(B_VAR("a"), B_AND(B_VAR("b"), B_VAR("c")))
    return chain_item(lang, {"a": p, "b": q, "c": r}, [(cond, "open")], "closed")


def branch_zero_str(rng: random.Random, lang: str) -> Item:
    cond = B_RAW("s", "s", lambda e: len(e["s"]) > 0, ("s",))
    return chain_item(lang, {"s": "0"}, [(cond, "truthy")], "falsy",
                      why='The string "0" has a character in it, so it is truthy in both Python and JavaScript.')


#: Written for both languages; `bind` makes each a Maker.
BRANCH_SHARED: list[Callable] = (
    [_two_way(op) for op in (">", ">=", "<", "<=", "==", "!=")]
    + [_three("desc", ">"), _three("desc", ">="), _three("asc", "<"), _three("asc", "<="), _three("trap", ">"),
       _three("traplt", "<")]
    + [_four("desc_ge"), _four("desc_gt"), _four("asc_lt"), _four("trap")]
    + [branch_ifs_override, branch_ifs_else_last, branch_ifs_three, branch_ifs_mixed, branch_eq_two, branch_eq_three,
       branch_and_range, branch_or_outside, branch_not_gt, branch_and_or_prec, branch_and_three, branch_not_either,
       branch_even_odd, branch_div35, branch_div15_first, branch_div15_last, branch_mod_pair, branch_str_eq,
       branch_str_start, branch_str_len, branch_str_vowel, branch_str_has, branch_truth_list, branch_truth_num,
       branch_truth_str, _nested("else"), _nested("dangling"), branch_two_vars, branch_sum, branch_max3,
       branch_in_weekend, branch_in_two, branch_bool_and, branch_bool_not, branch_bool_or, branch_zero_str]
)


def branch_chained(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(3, 6)
    n = rng.choice((lo - 1, lo, hi - 1, hi, lo + 1))
    cond = B_RAW(f"{lo} <= n < {hi}", "", lambda e: lo <= e["n"] < hi, ("n",))
    return chain_item("py", {"n": n}, [(cond, "inside")], "outside",
                      why=f"{lo} <= n < {hi} means n is {lo} or more and less than {hi}.")


def branch_in_range(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(3, 6)
    n = rng.choice((lo - 1, lo, hi - 1, hi, lo + 1))
    cond = B_RAW(f"n in range({lo}, {hi})", "", lambda e: lo <= e["n"] < hi, ("n",))
    return chain_item("py", {"n": n}, [(cond, "inside")], "outside",
                      why=f"range({lo}, {hi}) stops before {hi}, so {hi} is outside.")


def branch_chained_three(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(2, 5), rng.randint(8, 12)
    n = rng.choice((a - 1, a, a + 1, b - 1, b, b + 1))
    c1 = B_RAW(f"n < {a}", "", lambda e: e["n"] < a, ("n",))
    c2 = B_RAW(f"{a} <= n <= {b}", "", lambda e: a <= e["n"] <= b, ("n",))
    return chain_item("py", {"n": n}, [(c1, "low"), (c2, "mid")], "high")


PY_BRANCH = [bind(f, "py") for f in BRANCH_SHARED] + [bind(f, "py") for f in
                                                      (branch_chained, branch_in_range, branch_chained_three)]

# ── 3. Same Logic ───────────────────────────────────────────────────────
#
# Two conditions; are they the same for every a, b, c (True/False) and every whole x from 0 to 11? The answer is
# worked out by hand over that whole table (`beval` on both trees); the oracle brute-forces it in the real runtime.

XS = tuple(range(12))


def _domain(names: list[str]):
    """Every environment over the names: a, b, c are False/True, x is 0..11."""
    envs: list[dict[str, Any]] = [{}]
    for name in names:
        values = XS if name == "x" else (False, True)
        envs = [{**e, name: v} for e in envs for v in values]
    return envs


def same_check(lang: str, e1: tuple, e2: tuple) -> str:
    """The program the real runtime runs: brute force over the same table, 'yes' or 'no'."""
    names = bvars(B_AND(e1, e2))
    s1, s2 = bsrc(e1, lang), bsrc(e2, lang)
    if lang == "py":
        loops = " ".join(f"for {n} in {'range(12)' if n == 'x' else '(False, True)'}" for n in names)
        return f'"yes" if all(({s1}) == ({s2}) {loops}) else "no"'
    body = f"({s1}) === ({s2})"
    for n in reversed(names):
        values = "Array.from({ length: 12 }, (_, i) => i)" if n == "x" else "[false, true]"
        body = f"{values}.every({n} => {body})"
    return f'{body} ? "yes" : "no"'


def same_item(lang: str, e1: tuple, e2: tuple, intended: bool, rule: str) -> Item:
    names = bvars(B_AND(e1, e2))
    differ = None
    for env in _domain(names):
        if beval(e1, env) != beval(e2, env):
            differ = env
            break
    same = differ is None
    if differ is not None:
        v1, v2 = beval(e1, differ), beval(e2, differ)
        counter = f" For {env_text(lang, differ)} the first is {tf(lang, v1)} and the second {tf(lang, v2)}."
        why = (rule + counter) if not intended else ("They differ." + counter)
    else:
        why = rule if intended else "Here the two happen to agree for every value."
    return Item(bsrc(e1, lang) + "\n" + bsrc(e2, lang), "yes" if same else "no", why, check=same_check(lang, e1, e2))


def _atoms(rng: random.Random, n: int) -> list[tuple]:
    """n different atoms: True/False variables, or tests on the whole number x."""
    mode = rng.random()
    pool_vars = ["a", "b", "c"]
    out: list[tuple] = []
    seen: set[str] = set()
    tries = 0
    while len(out) < n and tries < 60:
        tries += 1
        use_var = mode < 0.6 or (mode < 0.85 and len(out) < n - 1)
        if use_var and pool_vars:
            node: tuple = B_VAR(pool_vars.pop(0))
        else:
            node = B_CMP("x", rng.choice((">", ">=", "<", "<=")), rng.randint(2, 9))
        key = bsrc(node, "py")
        if key not in seen:
            seen.add(key)
            out.append(node)
    while len(out) < n:  # cannot happen for n <= 3, but never leave short
        out.append(B_VAR("abc"[len(out)]))
    return out


def _same_atoms(tag: str, n: int, fn: Callable) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        e1, e2, intended, rule = fn(*_atoms(rng, n))
        return same_item(lang, e1, e2, intended, rule)
    f.__name__ = "same_" + tag
    return f


def _same_rng(tag: str, fn: Callable) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        e1, e2, intended, rule = fn(rng)
        return same_item(lang, e1, e2, intended, rule)
    f.__name__ = "same_" + tag
    return f


def _n(x: tuple) -> tuple:
    return B_NOT(x)


_P = B_P
_A = B_AND
_O = B_OR

#: (tag, how many atoms, builder -> (first, second, are they the same?, the rule in words))
SAME_ATOM_SPECS: list[tuple[str, int, Callable]] = [
    ("demorgan_and", 2, lambda X, Y: (_n(_P(_A(X, Y))), _O(_n(X), _n(Y)), True,
                                      "De Morgan: not (A and B) is (not A) or (not B).")),
    ("demorgan_or", 2, lambda X, Y: (_n(_P(_O(X, Y))), _A(_n(X), _n(Y)), True,
                                     "De Morgan: not (A or B) is (not A) and (not B).")),
    ("double_not", 1, lambda X: (_n(_n(X)), X, True, "Two nots cancel out.")),
    ("comm_and", 2, lambda X, Y: (_A(X, Y), _A(Y, X), True, "and does not care about the order.")),
    ("comm_or", 2, lambda X, Y: (_O(X, Y), _O(Y, X), True, "or does not care about the order.")),
    ("absorb_or", 2, lambda X, Y: (_O(X, _P(_A(X, Y))), X, True, "If A is true the whole is true; if A is false, A and B is false too.")),
    ("absorb_and", 2, lambda X, Y: (_A(X, _P(_O(X, Y))), X, True, "A must be true anyway, and then (A or B) is true.")),
    ("distribute_and", 3, lambda X, Y, Z: (_A(X, _P(_O(Y, Z))), _O(_P(_A(X, Y)), _P(_A(X, Z))), True,
                                           "and spreads over or, like multiplying over a sum.")),
    ("distribute_or", 3, lambda X, Y, Z: (_O(X, _P(_A(Y, Z))), _A(_P(_O(X, Y)), _P(_O(X, Z))), True,
                                          "or spreads over and as well.")),
    ("factor", 3, lambda X, Y, Z: (_O(_P(_A(X, Y)), _P(_A(X, Z))), _A(X, _P(_O(Y, Z))), True,
                                   "A is needed in both, so it can be factored out.")),
    ("implication", 2, lambda X, Y: (_O(_n(X), Y), _n(_P(_A(X, _n(Y)))), True,
                                     "(not A) or B is false only when A is true and B is false.")),
    ("mux", 2, lambda X, Y: (_O(_P(_A(X, Y)), _P(_A(_n(X), Y))), Y, True, "Whatever A is, the answer is just B.")),
    ("not_not_and", 2, lambda X, Y: (_A(_n(_n(X)), Y), _A(X, Y), True, "The double not cancels.")),
    ("swap_not_and", 2, lambda X, Y: (_A(_n(X), _n(Y)), _n(_P(_O(X, Y))), True, "Neither A nor B is the same as not (A or B).")),
    ("swap_not_or", 2, lambda X, Y: (_O(_n(X), _n(Y)), _n(_P(_A(X, Y))), True, "Not both is the same as not-A or not-B.")),
    ("bad_demorgan_and", 2, lambda X, Y: (_n(_P(_A(X, Y))), _A(_n(X), _n(Y)), False,
                                          "Flipping the not without flipping and to or is not De Morgan.")),
    ("bad_demorgan_or", 2, lambda X, Y: (_n(_P(_O(X, Y))), _O(_n(X), _n(Y)), False,
                                         "Flipping the not without flipping or to and is not De Morgan.")),
    ("bad_not_and", 2, lambda X, Y: (_A(_n(X), Y), _n(_P(_A(X, Y))), False, "not A and B is not the same as not (A and B).")),
    ("bad_not_or", 2, lambda X, Y: (_O(_n(X), Y), _n(_P(_O(X, Y))), False, "not A or B is not the same as not (A or B).")),
    ("prec_and_or", 3, lambda X, Y, Z: (_O(_A(X, Y), Z), _A(X, _P(_O(Y, Z))), False,
                                        "and binds tighter than or, so the brackets move the meaning.")),
    ("prec_or_and", 3, lambda X, Y, Z: (_O(X, _A(Y, Z)), _A(_P(_O(X, Y)), Z), False,
                                        "and binds tighter than or, so the brackets move the meaning.")),
    ("bad_absorb", 3, lambda X, Y, Z: (_O(X, _P(_A(Y, Z))), X, False, "B and C can make it true even when A is false.")),
    ("and_vs_or", 2, lambda X, Y: (_A(X, Y), _O(X, Y), False, "and needs both; or needs one.")),
    ("not_and_not", 2, lambda X, Y: (_A(X, _n(Y)), _n(_P(_A(X, Y))), False, "A and not B is narrower than not (A and B).")),
    ("bad_dist", 3, lambda X, Y, Z: (_O(X, _P(_A(Y, Z))), _A(_P(_O(X, Y)), Z), False, "or does not spread over and like that.")),
    ("bad_mux", 2, lambda X, Y: (_O(_P(_A(X, Y)), _P(_A(_n(X), Y))), X, False, "The answer depends on B, not on A.")),
    ("bad_implication", 2, lambda X, Y: (_O(_n(X), Y), _O(X, _n(Y)), False, "Swapping A and B does not keep (not A) or B.")),
]


def _x_not(op: str, flip: str) -> Callable:
    def fn(rng: random.Random):
        k = rng.randint(2, 9)
        return (_n(_P(B_CMP("x", op, k))), B_CMP("x", flip, k), True,
                f"The opposite of x {op} {k} is x {flip} {k}, boundary included.")
    return fn


def _x_rng_flip(rng: random.Random):
    k = rng.randint(2, 9)
    return (B_CMP("x", ">", k), B_RAW(f"{k} < x", f"{k} < x", lambda e: k < e["x"], ("x",)), True, "Reading the test from the other side changes nothing.")


def _x_ge_minus(rng: random.Random):
    k = rng.randint(3, 9)
    return (B_CMP("x", ">=", k), B_CMP("x", ">", k - 1), True, "For whole numbers, k or more is the same as more than k - 1.")


def _x_range_out(rng: random.Random):
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    return (_O(B_CMP("x", "<", lo), B_CMP("x", ">", hi)), _n(_P(_A(B_CMP("x", ">=", lo), B_CMP("x", "<=", hi)))), True,
            "Outside the range is the opposite of inside it.")


def _x_range_in(rng: random.Random):
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    return (_A(B_CMP("x", ">=", lo), B_CMP("x", "<=", hi)), _n(_P(_O(B_CMP("x", "<", lo), B_CMP("x", ">", hi)))), True,
            "Inside the range is the opposite of outside it.")


def _x_two_lt(rng: random.Random):
    k1, k2 = rng.sample(range(2, 10), 2)
    return (_O(B_CMP("x", "<", k1), B_CMP("x", "<", k2)), B_CMP("x", "<", max(k1, k2)), True, "The bigger limit already covers the smaller one.")


def _x_two_gt(rng: random.Random):
    k1, k2 = rng.sample(range(2, 10), 2)
    return (_A(B_CMP("x", ">", k1), B_CMP("x", ">", k2)), B_CMP("x", ">", max(k1, k2)), True, "Beating the bigger limit beats both.")


def _x_ne_split(rng: random.Random):
    k = rng.randint(2, 9)
    return (B_CMP("x", "!=", k), _O(B_CMP("x", "<", k), B_CMP("x", ">", k)), True, "Not equal means below or above.")


def _x_mod_even(rng: random.Random):
    return (B_MOD("x", 2, 0), _n(_P(B_MOD("x", 2, 1))), True, "A whole number from 0 up is even or odd, never both.")


def _x_mod_odd(rng: random.Random):
    return (B_MOD("x", 2, 1), _n(_P(B_MOD("x", 2, 0))), True, "A whole number from 0 up is even or odd, never both.")


def _x_bad(op1: str, op2: str) -> Callable:
    def fn(rng: random.Random):
        k = rng.randint(2, 9)
        return (_n(_P(B_CMP("x", op1, k))), B_CMP("x", op2, k), False, f"x == {k} is on one side of this and not the other.")
    return fn


def _x_gt_ge(rng: random.Random):
    k = rng.randint(2, 9)
    return B_CMP("x", ">", k), B_CMP("x", ">=", k), False, f"x == {k} is the difference."


def _x_between(rng: random.Random):
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    return (_A(B_CMP("x", ">=", lo), B_CMP("x", "<=", hi)), _A(B_CMP("x", ">", lo), B_CMP("x", "<", hi)), False,
            "One includes the ends, the other leaves them out.")


def _x_or_and_range(rng: random.Random):
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    return (_O(B_CMP("x", "<", lo), B_CMP("x", ">", hi)), _A(B_CMP("x", "<", lo), B_CMP("x", ">", hi)), False,
            "Nothing is both below the low end and above the high end.")


def _x_and_or_range(rng: random.Random):
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    return (_A(B_CMP("x", ">", lo), B_CMP("x", "<", hi)), _O(B_CMP("x", ">", lo), B_CMP("x", "<", hi)), False,
            "or lets almost every number through.")


def _x_mod_ks(rng: random.Random):
    return B_MOD("x", 3, 0), B_MOD("x", 6, 0), False, "Every multiple of 6 is a multiple of 3, but not the other way round."


def _x_xor(rng: random.Random):
    return (_A(_P(_O(B_VAR("a"), B_VAR("b"))), _n(_P(_A(B_VAR("a"), B_VAR("b"))))),
            B_RAW("a != b", "a !== b", lambda e: e["a"] != e["b"], ("a", "b")), True,
            "Exactly one of the two is true: that is what != says for two booleans.")


SAME_X_SPECS: list[tuple[str, Callable]] = [
    ("not_gt", _x_not(">", "<=")), ("not_ge", _x_not(">=", "<")), ("not_lt", _x_not("<", ">=")),
    ("not_le", _x_not("<=", ">")), ("not_eq", _x_not("==", "!=")), ("not_ne", _x_not("!=", "==")),
    ("flip_sides", _x_rng_flip), ("ge_minus", _x_ge_minus), ("range_out", _x_range_out), ("range_in", _x_range_in),
    ("two_lt", _x_two_lt), ("two_gt", _x_two_gt), ("ne_split", _x_ne_split), ("mod_even", _x_mod_even),
    ("mod_odd", _x_mod_odd), ("xor", _x_xor),
    ("bad_not_gt", _x_bad(">", "<")), ("bad_not_ge", _x_bad(">=", "<=")), ("bad_not_lt", _x_bad("<", ">")),
    ("gt_ge", _x_gt_ge), ("between", _x_between), ("or_and_range", _x_or_and_range),
    ("and_or_range", _x_and_or_range), ("mod_ks", _x_mod_ks),
]

SAME_SHARED: list[Callable] = ([_same_atoms(t, n, fn) for t, n, fn in SAME_ATOM_SPECS]
                               + [_same_rng(t, fn) for t, fn in SAME_X_SPECS])
PY_SAME = [bind(f, "py") for f in SAME_SHARED]

# ── 4. Truth Table Row ──────────────────────────────────────────────────

_NEG = {0: lambda x: x, 1: B_NOT}


def _tt_atoms(rng: random.Random, n: int) -> tuple[list[tuple], dict[str, Any]]:
    """n atoms - True/False variables, or tests on a whole number n - and the values they are given."""
    env: dict[str, Any] = {}
    atoms: list[tuple] = []
    names = ["a", "b", "c"]
    used_cmp: set[str] = set()
    for i in range(n):
        if rng.random() < 0.72 or i == 0:
            name = names[sum(1 for a in atoms if a[0] == "var")]
            env[name] = rng.random() < 0.5
            atoms.append(B_VAR(name))
        else:
            op, k = rng.choice((">", ">=", "<", "<=", "==")), rng.randint(2, 8)
            if "n" not in env:
                env["n"] = rng.randint(1, 9)
            node = B_CMP("n", op, k)
            if bsrc(node, "py") in used_cmp:
                node = B_MOD("n", 2, 0)
            used_cmp.add(bsrc(node, "py"))
            atoms.append(node)
    return atoms, env


def tt_item(lang: str, node: tuple, env: dict[str, Any]) -> Item:
    prompt = "\n".join(decls(lang, env) + [bsrc(node, lang)])
    got = beval(node, env)
    why = f"With {env_text(lang, env)}, the whole thing works out to {tf(lang, got)}."
    check = yes_no_py(prompt) if lang == "py" else yes_no_js(prompt)
    return Item(prompt, "yes" if got else "no", why, check=check)


def _tt(tag: str, n: int, fn: Callable) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        atoms, env = _tt_atoms(rng, n)
        return tt_item(lang, fn(*atoms), env)
    f.__name__ = "table_" + tag
    return f


TABLE_SKELETONS: list[tuple[str, int, Callable]] = []
for _op, _fn in (("and", _A), ("or", _O)):
    for _na in (0, 1):
        for _nb in (0, 1):
            for _outer in (0, 1):
                def _make(op=_op, fn=_fn, na=_na, nb=_nb, outer=_outer):
                    def build2(X, Y):
                        core = fn(_NEG[na](X), _NEG[nb](Y))
                        return B_NOT(B_P(core)) if outer else core
                    return build2
                TABLE_SKELETONS.append((f"{_op}_{_na}{_nb}{_outer}", 2, _make()))
for _o1, _f1 in (("and", _A), ("or", _O)):
    for _o2, _f2 in (("and", _A), ("or", _O)):
        for _shape in ("left", "right", "flat"):
            if _shape == "flat" and (_o1, _o2) == ("or", "and"):
                continue  # it prints exactly like "left" (and is bracketed anyway)
            for _neg in (0, 1):
                def _make3(f1=_f1, f2=_f2, shape=_shape, neg=_neg):
                    def build3(X, Y, Z):
                        X = _NEG[neg](X)
                        if shape == "left":
                            return f2(B_P(f1(X, Y)), Z)
                        if shape == "right":
                            return f1(X, B_P(f2(Y, Z)))
                        return f2(f1(X, Y), Z)
                    return build3
                TABLE_SKELETONS.append((f"{_o1}_{_o2}_{_shape}{_neg}", 3, _make3()))
TABLE_SKELETONS += [
    ("xor", 2, lambda X, Y: _A(_P(_O(X, Y)), _n(_P(_A(X, Y))))),
    ("xnor", 2, lambda X, Y: _O(_P(_A(X, Y)), _P(_A(_n(X), _n(Y))))),
    ("majority", 3, lambda X, Y, Z: _O(_O(_P(_A(X, Y)), _P(_A(X, Z))), _P(_A(Y, Z)))),
    ("not_double", 1, lambda X: _n(_n(X))),
    ("not_or_and", 3, lambda X, Y, Z: _n(_P(_O(_P(_A(X, Y)), Z)))),
    ("two_nots", 2, lambda X, Y: _A(_n(X), _n(Y))),
]

TABLE_SHARED: list[Callable] = [_tt(t, n, fn) for t, n, fn in TABLE_SKELETONS]
PY_TABLE = [bind(f, "py") for f in TABLE_SHARED]

# ── 5. Ternary Pick ─────────────────────────────────────────────────────

def tern(lang: str, cond: tuple | str, x: str, y: str) -> str:
    """`x if c else y` / `c ? x : y` (a nested one in the else slot needs no brackets in either language)."""
    c = cond if isinstance(cond, str) else bsrc(cond, lang)
    return f"{x} if {c} else {y}" if lang == "py" else f"{c} ? {x} : {y}"


def tp(lang: str, s: str) -> str:
    return "(" + s + ")"


def tern_item(lang: str, env: dict[str, Any], expr: str, got: Any, why: str, extra: list[str] | None = None) -> Item:
    prompt = "\n".join(decls(lang, env) + (extra or []) + [expr])
    return Item(prompt, show(lang, got), why)


def _why_cond(lang: str, cond: tuple, env: dict[str, Any]) -> str:
    true = beval(cond, env)
    return (f"The condition {bsrc(cond, lang)} is {tf(lang, true)}, so the " +
            ("first value is used." if true else "value after the else is used." if lang == "py" else "second value is used."))


def t_label(rng: random.Random, lang: str) -> Item:
    t = rng.randint(3, 12)
    n = max(0, t + rng.choice((-3, -1, 0, 1, 3)))
    l1, l2 = rng.choice(L2)
    c = B_CMP("n", ">", t)
    return tern_item(lang, {"n": n}, tern(lang, c, f'"{l2}"', f'"{l1}"'), l2 if n > t else l1, _why_cond(lang, c, {"n": n}))


def t_calc(rng: random.Random, lang: str) -> Item:
    t, k = rng.randint(3, 8), rng.randint(2, 4)
    n = rng.randint(1, 12)
    c = B_CMP("n", ">", t)
    got = n * k if n > t else n + 10
    return tern_item(lang, {"n": n}, tern(lang, c, f"n * {k}", "n + 10"), got, _why_cond(lang, c, {"n": n}))


def t_max(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    c = B_RAW("a > b", "a > b", lambda e: e["a"] > e["b"], ("a", "b"))
    return tern_item(lang, {"a": a, "b": b}, tern(lang, c, "a", "b"), a if a > b else b, "It picks the bigger of the two.")


def t_min(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    c = B_RAW("a < b", "a < b", lambda e: e["a"] < e["b"], ("a", "b"))
    return tern_item(lang, {"a": a, "b": b}, tern(lang, c, "a", "b"), a if a < b else b, "It picks the smaller of the two.")


def t_abs(rng: random.Random, lang: str) -> Item:
    n = rng.randint(-7, 7)
    c = B_CMP("n", ">=", 0)
    return tern_item(lang, {"n": n}, tern(lang, c, "n", "-n"), n if n >= 0 else -n, "Negative numbers are flipped: this is the absolute value.")


def t_sign(rng: random.Random, lang: str) -> Item:
    n = rng.randint(-4, 4)
    inner = tern(lang, B_CMP("n", "<", 0), "-1", "0")
    got = 1 if n > 0 else (-1 if n < 0 else 0)
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", ">", 0), "1", inner), got, "The tests run left to right until one is true.")


def t_grade(rng: random.Random, lang: str) -> Item:
    s = rng.choice((72, 79, 80, 85, 89, 90, 95, 60))
    inner = tern(lang, B_CMP("s", ">=", 80), '"B"', '"C"')
    got = "A" if s >= 90 else ("B" if s >= 80 else "C")
    return tern_item(lang, {"s": s}, tern(lang, B_CMP("s", ">=", 90), '"A"', inner), got, "The first true test wins: 90 or more, else 80 or more, else C.")


def t_clamp_hi(rng: random.Random, lang: str) -> Item:
    t = rng.randint(4, 9)
    n = rng.randint(1, 14)
    c = B_CMP("n", "<", t)
    return tern_item(lang, {"n": n}, tern(lang, c, "n", str(t)), n if n < t else t, f"It caps n at {t}.")


def t_clamp_both(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(2, 4)
    hi = lo + rng.randint(3, 6)
    n = rng.randint(0, 12)
    inner = tern(lang, B_CMP("n", ">", hi), str(hi), "n")
    got = lo if n < lo else (hi if n > hi else n)
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", "<", lo), str(lo), inner), got, f"It keeps n between {lo} and {hi}.")


def t_evenodd(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 30)
    c = B_MOD("n", 2, 0)
    return tern_item(lang, {"n": n}, tern(lang, c, '"even"', '"odd"'), "even" if n % 2 == 0 else "odd", _why_cond(lang, c, {"n": n}))


def t_fizz(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    c = B_MOD("n", 3, 0)
    return tern_item(lang, {"n": n}, tern(lang, c, '"fizz"', "n"), "fizz" if n % 3 == 0 else n, _why_cond(lang, c, {"n": n}))


def t_fizzbuzz(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    inner = tern(lang, B_MOD("n", 5, 0), '"buzz"', "n")
    got = "fizz" if n % 3 == 0 else ("buzz" if n % 5 == 0 else n)
    return tern_item(lang, {"n": n}, tern(lang, B_MOD("n", 3, 0), '"fizz"', inner), got, "3 is tried first, then 5, otherwise the number itself.")


def t_collatz(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    half = "n // 2" if lang == "py" else "n / 2"
    got = n // 2 if n % 2 == 0 else 3 * n + 1
    return tern_item(lang, {"n": n}, tern(lang, B_MOD("n", 2, 0), half, "3 * n + 1"), got, "The Collatz step: halve an even number, otherwise triple it and add 1.")


def t_absdiff(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    c = B_RAW("a > b", "a > b", lambda e: e["a"] > e["b"], ("a", "b"))
    return tern_item(lang, {"a": a, "b": b}, tern(lang, c, "a - b", "b - a"), abs(a - b), "The bigger minus the smaller.")


def t_eq_chain(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 4)
    inner = tern(lang, B_CMP("n", "==", 2), "20", "30")
    got = 10 if n == 1 else (20 if n == 2 else 30)
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", "==", 1), "10", inner), got, "Each == test is tried in turn; 30 is the fallback.")


def t_prec_outer(rng: random.Random, lang: str) -> Item:
    a, b, d = ints(rng, 3)
    flag = rng.random() < 0.5
    got = a + b if flag else d
    return tern_item(lang, {"flag": flag}, tern(lang, B_VAR("flag"), f"{a} + {b}", str(d)), got,
                     "The whole sum is the first value: the + happens inside that branch.")


def t_prec_both(rng: random.Random, lang: str) -> Item:
    a, b, d, e = ints(rng, 4)
    flag = rng.random() < 0.5
    got = a + b if flag else d + e
    return tern_item(lang, {"flag": flag}, tern(lang, B_VAR("flag"), f"{a} + {b}", f"{d} + {e}"), got,
                     "Each branch is a whole sum; only one of them is worked out.")


def t_prec_inner(rng: random.Random, lang: str) -> Item:
    k, a, b = ints(rng, 3)
    flag = rng.random() < 0.5
    got = k + (a if flag else b)
    return tern_item(lang, {"flag": flag}, f"{k} + " + tp(lang, tern(lang, B_VAR("flag"), str(a), str(b))), got,
                     "The brackets make the choice happen first; then the number is added.")


def t_paren_after(rng: random.Random, lang: str) -> Item:
    a, b, k = ints(rng, 3)
    flag = rng.random() < 0.5
    got = (a if flag else b) + k
    return tern_item(lang, {"flag": flag}, tp(lang, tern(lang, B_VAR("flag"), str(a), str(b))) + f" + {k}", got,
                     "Choose first (the brackets), then add.")


def t_len_clamp(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["farm", "drone", "carrot", "loop", "tree", "pumpkin"])
    t = rng.randint(3, 6)
    ln = "len(w)" if lang == "py" else "w.length"
    c = B_RAW(f"len(w) > {t}", f"w.length > {t}", lambda e: len(e["w"]) > t, ("w",))
    return tern_item(lang, {"w": w}, tern(lang, c, ln, str(t)), len(w) if len(w) > t else t, f"It is the length, but never less than {t}.")


def t_nested_else_paren(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 9)
    a, b = 3, 6
    inner = tp(lang, tern(lang, B_CMP("n", "<", b), '"mid"', '"high"'))
    got = "low" if n < a else ("mid" if n < b else "high")
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", "<", a), '"low"', inner), got, "Brackets round the second choice change nothing here: it sits in the else part.")


def t_nested_true(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 12)
    a, b = 4, 8
    inner = tp(lang, tern(lang, B_CMP("n", ">", b), '"huge"', '"big"'))
    got = ("huge" if n > b else "big") if n > a else "small"
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", ">", a), inner, '"small"'), got, "The inner choice only matters once the outer test passes.")


def t_comp(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(3, 5))
    t = rng.randint(3, 6)
    got = [x if x > t else 0 for x in xs]
    if lang == "py":
        expr = f"[x if x > {t} else 0 for x in {lit(xs)}]"
    else:
        expr = f"{lit(xs)}.map(x => x > {t} ? x : 0)"
    return Item(expr, show(lang, got), f"Each item is kept if it is over {t}, otherwise it becomes 0.")


def t_comp_str(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 6)
    vals = [a, a + 1, a + 2]
    got = ["odd" if v % 2 else "even" for v in vals]
    if lang == "py":
        expr = f'["odd" if x % 2 else "even" for x in {lit(vals)}]'
    else:
        expr = f'{lit(vals)}.map(x => x % 2 ? "odd" : "even")'
    return Item(expr, show(lang, got), "x % 2 is 1 for an odd number, which counts as true.")


def t_and(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    n = rng.randint(0, 12)
    c = B_AND(B_CMP("n", ">", lo), B_CMP("n", "<", hi))
    return tern_item(lang, {"n": n}, tern(lang, c, '"in"', '"out"'), "in" if lo < n < hi else "out", _why_cond(lang, c, {"n": n}))


def t_or(rng: random.Random, lang: str) -> Item:
    lo = rng.randint(2, 5)
    hi = lo + rng.randint(2, 5)
    n = rng.randint(0, 12)
    c = B_OR(B_CMP("n", "<", lo), B_CMP("n", ">", hi))
    return tern_item(lang, {"n": n}, tern(lang, c, '"out"', '"in"'), "out" if (n < lo or n > hi) else "in", _why_cond(lang, c, {"n": n}))


def t_not(rng: random.Random, lang: str) -> Item:
    flag = rng.random() < 0.5
    a, b = ints(rng, 2)
    c = B_NOT(B_VAR("flag"))
    return tern_item(lang, {"flag": flag}, tern(lang, c, str(a), str(b)), b if flag else a, _why_cond(lang, c, {"flag": flag}))


def t_assign(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    n = rng.randint(1, 9)
    c = B_CMP("n", ">", 5)
    pick = a if n > 5 else b
    x = tern(lang, c, str(a), str(b))
    lines = decls(lang, {"n": n}) + [f"x = {x}" if lang == "py" else f"const x = {x};", "x * 2"]
    return Item("\n".join(lines), str(pick * 2), "x is chosen first, then doubled.")


def t_streq(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["word", "word", "other", "farm"])
    c = B_RAW('w == "word"', 'w === "word"', lambda e: e["w"] == "word", ("w",))
    return tern_item(lang, {"w": w}, tern(lang, c, '"yes"', '"no"'), "yes" if w == "word" else "no", _why_cond(lang, c, {"w": w}))


def t_vowel(rng: random.Random, lang: str) -> Item:
    ch = rng.choice("abcdeiopuxyz")
    c = B_RAW('ch in "aeiou"', '"aeiou".includes(ch)', lambda e: find("aeiou", e["ch"]) != -1, ("ch",))
    return tern_item(lang, {"ch": ch}, tern(lang, c, '"vowel"', '"other"'), "vowel" if find("aeiou", ch) != -1 else "other", _why_cond(lang, c, {"ch": ch}))


def t_first(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(2, 3)) if rng.random() < 0.5 else []
    if lang == "py":
        expr, empty = "xs[0] if xs else None", None
    else:
        expr, empty = "xs.length ? xs[0] : undefined", UNDEF
    return tern_item(lang, {"xs": xs}, expr, xs[0] if xs else empty,
                     "An empty list is falsy in Python, so the else is used." if lang == "py"
                     else "An empty array has length 0, which is falsy, so the else is used.")


def t_dict(rng: random.Random, lang: str) -> Item:
    k = rng.choice(["a", "k", "n"])
    present = rng.random() < 0.5
    key = k if present else "z"
    v = rng.randint(2, 9)
    if lang == "py":
        lines = [f'd = {{"{k}": {v}}}', f'd["{key}"] if "{key}" in d else 0']
    else:
        lines = [f"const d = {{ {k}: {v} }};", f'"{key}" in d ? d.{key} : 0']
    return Item("\n".join(lines), str(v if present else 0), "The in test asks whether the key is there before using it.")


def t_pair(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    lo, hi = (a, b) if a < b else (b, a)
    c = B_RAW("a < b", "a < b", lambda e: e["a"] < e["b"], ("a", "b"))
    if lang == "py":
        expr = tern(lang, c, "(a, b)", "(b, a)")
        got: Any = (lo, hi)
    else:
        expr = tern(lang, c, "[a, b]", "[b, a]")
        got = [lo, hi]
    return tern_item(lang, {"a": a, "b": b}, expr, got, "It puts the smaller one first.")


def t_list_pick(rng: random.Random, lang: str) -> Item:
    a, b, c = ints(rng, 3)
    flag = rng.random() < 0.5
    got = [a, b] if flag else [c]
    return tern_item(lang, {"flag": flag}, tern(lang, B_VAR("flag"), f"[{a}, {b}]", f"[{c}]"), got, "The whole list on the chosen side is the result.")


def t_odd_inc(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    return tern_item(lang, {"n": n}, tern(lang, B_RAW("n % 2", "n % 2", lambda e: e["n"] % 2 != 0, ("n",)), "n + 1", "n"),
                     n + 1 if n % 2 else n, "n % 2 is 1 for an odd n, which counts as true: odd numbers go up by one.")


def t_relu(rng: random.Random, lang: str) -> Item:
    n = rng.randint(-6, 6)
    if lang == "py":
        expr = "(lambda v: v if v > 0 else 0)(n)"
    else:
        expr = "((v) => v > 0 ? v : 0)(n)"
    return tern_item(lang, {"n": n}, expr, n if n > 0 else 0, "Negative numbers become 0.")


def t_concat(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    c = B_MOD("n", 2, 0)
    word = tp(lang, tern(lang, c, '"even"', '"odd"'))
    expr = f'str(n) + " is " + {word}' if lang == "py" else f'n + " is " + {word}'
    return tern_item(lang, {"n": n}, expr, f"{n} is " + ("even" if n % 2 == 0 else "odd"), "The brackets pick the word, then the pieces join.")


def t_max3(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 10), 3)
    cond1 = B_RAW("a > b and a > c", "a > b && a > c", lambda e: e["a"] > e["b"] and e["a"] > e["c"], ("a", "b", "c"))
    cond2 = B_RAW("b > c", "b > c", lambda e: e["b"] > e["c"], ("b", "c"))
    inner = tern(lang, cond2, "b", "c")
    return tern_item(lang, {"a": a, "b": b, "c": c}, tern(lang, cond1, "a", inner), max(a, b, c), "It finds the biggest of three.")


def t_redundant(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 9)
    t = rng.randint(3, 7)
    c = B_CMP("n", ">", t)
    return tern_item(lang, {"n": n}, tern(lang, c, tf(lang, True), tf(lang, False)), n > t,
                     "A ternary that returns True or False is just the comparison itself.")


def t_str_len(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["farm", "drone", "carrot", "loop", "tree", "pumpkin", "key"])
    ln = "len(w) > 4" if lang == "py" else "w.length > 4"
    c = B_RAW(ln, ln, lambda e: len(e["w"]) > 4, ("w",))
    return tern_item(lang, {"w": w}, tern(lang, c, '"long"', '"short"'), "long" if len(w) > 4 else "short", _why_cond(lang, c, {"w": w}))


def t_mult_choice(rng: random.Random, lang: str) -> Item:
    a, b = ints(rng, 2)
    c = B_RAW("a > b", "a > b", lambda e: e["a"] > e["b"], ("a", "b"))
    return tern_item(lang, {"a": a, "b": b}, tern(lang, c, "a * b", "a + b"), a * b if a > b else a + b, _why_cond(lang, c, {"a": a, "b": b}))


def t_three_way(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 4)
    inner = tern(lang, B_CMP("n", "==", 2), '"two"', '"many"')
    got = "one" if n == 1 else ("two" if n == 2 else "many")
    return tern_item(lang, {"n": n}, tern(lang, B_CMP("n", "==", 1), '"one"', inner), got, "== tests in order, with many as the fallback.")


def t_in_arg(rng: random.Random, lang: str) -> Item:
    a, b, k = ints(rng, 3)
    flag = rng.random() < 0.5
    pick = a if flag else b
    t = tern(lang, B_VAR("flag"), str(a), str(b))
    expr = f"max({t}, {k})" if lang == "py" else f"Math.max({t}, {k})"
    return tern_item(lang, {"flag": flag}, expr, max(pick, k), "The choice is made inside the call, then max picks the bigger.")


def t_eq_zero(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(1, 4), rng.randint(1, 4)
    c = B_RAW("a == b", "a === b", lambda e: e["a"] == e["b"], ("a", "b"))
    return tern_item(lang, {"a": a, "b": b}, tern(lang, c, "a", "0"), a if a == b else 0, _why_cond(lang, c, {"a": a, "b": b}))


def t_step(rng: random.Random, lang: str) -> Item:
    n = rng.randint(2, 14)
    t = rng.randint(4, 9)
    half = "n // 2" if lang == "py" else "Math.floor(n / 2)"
    c = B_CMP("n", ">", t)
    return tern_item(lang, {"n": n}, tern(lang, c, half, "n * 2"), n // 2 if n > t else n * 2, _why_cond(lang, c, {"n": n}))


def t_truthy_list(rng: random.Random, lang: str) -> Item:
    xs = [] if rng.random() < 0.5 else ints(rng, 2)
    truthy = truthy_for(lang)(xs)
    cond = "xs"
    return tern_item(lang, {"xs": xs}, tern(lang, cond, '"yes"', '"no"'), "yes" if truthy else "no",
                     "Python treats an empty list as false." if lang == "py" else "JavaScript treats every array as true, even an empty one.")


def t_truthy_value(rng: random.Random, lang: str) -> Item:
    pool = PY_VALUES["X"] if lang == "py" else JS_VALUES_FOR_TERNARY
    src, v = rng.choice([p for p in pool if p[0] not in ("{}",)])
    truthy = truthy_for(lang)(v)
    return Item(tern(lang, src, '"yes"', '"no"'), "yes" if truthy else "no", f"{src} is {say(truthy)}, so the " + ("first" if truthy else "second") + " value is used.")


#: The JavaScript values `t_truthy_value` may test (kept here so the shared template needs no import of _logic_js).
JS_VALUES_FOR_TERNARY: list = [("0", 0), ("1", 1), ('""', ""), ('"0"', "0"), ("[]", []), ("null", NULL), ("undefined", UNDEF),
                               ("NaN", NAN), ("-1", -1), ('"hi"', "hi"), ("false", False), ("true", True), ("[0]", [0])]

TERNARY_SHARED: list[Callable] = [
    t_label, t_calc, t_max, t_min, t_abs, t_sign, t_grade, t_clamp_hi, t_clamp_both, t_evenodd, t_fizz, t_fizzbuzz,
    t_collatz, t_absdiff, t_eq_chain, t_prec_outer, t_prec_both, t_prec_inner, t_paren_after, t_len_clamp,
    t_nested_else_paren, t_nested_true, t_comp, t_comp_str, t_and, t_or, t_not, t_assign, t_streq, t_vowel, t_first,
    t_dict, t_pair, t_list_pick, t_odd_inc, t_relu, t_concat, t_max3, t_redundant, t_str_len, t_mult_choice,
    t_three_way, t_in_arg, t_eq_zero, t_step, t_truthy_list, t_truthy_value,
]


def t_fstring(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 20)
    return tern_item("py", {"n": n}, "f\"{n} is {'even' if n % 2 == 0 else 'odd'}\"", f"{n} is " + ("even" if n % 2 == 0 else "odd"),
                     "The ternary sits inside the braces of the f-string.")


def t_none_default(rng: random.Random, lang: str) -> Item:
    v = rng.choice([None, None, 0, 4, 7])
    got = v if v is not None else -1
    return Item(f"x = {py_show(v)}\nx if x is not None else -1", str(got),
                "Only None is replaced: 0 is a real value, so it is kept.")


def t_neg_last(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(2, 4)) if rng.random() < 0.6 else []
    return Item(f"xs = {lit(xs)}\nxs[-1] if xs else None", py_show(xs[-1] if xs else None),
                "An empty list is falsy, so the else gives None instead of an IndexError.")


def t_chain_cmp(rng: random.Random, lang: str) -> Item:
    n = rng.randint(0, 12)
    return Item(f'n = {n}\n"mid" if 3 < n < 8 else "edge"', "mid" if 3 < n < 8 else "edge",
                "3 < n < 8 is a chained comparison: n is between 3 and 8, not counting the ends.")


PY_TERNARY = [bind(f, "py") for f in TERNARY_SHARED] + [bind(f, "py") for f in (t_fstring, t_none_default, t_neg_last, t_chain_cmp)]

# ── 6. Bit Ops ──────────────────────────────────────────────────────────
#
# Python's ints are unbounded (two's complement with endless sign bits: 64 bits is plenty for these small
# numbers); JavaScript's bit operators work on 32-bit signed ints. Both are modelled as loops over bits.

def _bits(n: int, w: int) -> list[int]:
    """Two's complement, least significant bit first, w bits."""
    m = n % ipow(2, w)
    out = []
    for _ in range(w):
        out.append(m % 2)
        m = m // 2
    return out


def _from_bits(bits: list[int], signed: bool) -> int:
    v = 0
    for i, b in enumerate(bits):
        v += b * ipow(2, i)
    if signed and bits[-1] == 1:
        v -= ipow(2, len(bits))
    return v


def bitwise(op: str, x: int, y: int, w: int) -> int:
    bx, by = _bits(x, w), _bits(y, w)
    if op == "&":
        out = [1 if (p == 1 and q == 1) else 0 for p, q in zip(bx, by)]
    elif op == "|":
        out = [1 if (p == 1 or q == 1) else 0 for p, q in zip(bx, by)]
    else:
        out = [1 if p != q else 0 for p, q in zip(bx, by)]
    return _from_bits(out, True)


def bit_not(x: int, w: int) -> int:
    return _from_bits([1 - b for b in _bits(x, w)], True)


def i32(x: int | float) -> int:
    """JavaScript's ToInt32: cut off the fraction (toward zero), then wrap to 32 bits."""
    return _from_bits(_bits(int(x), 32), True)


def js_shl(x: int, k: int) -> int:
    return i32(i32(x) * ipow(2, k % 32))


def js_shr(x: int, k: int) -> int:
    return i32(x) // ipow(2, k % 32)


def js_ushr(x: int, k: int) -> int:
    return (i32(x) % ipow(2, 32)) // ipow(2, k % 32)


def binstr(n: int, width: int = 1) -> str:
    """n >= 0 in binary, padded with zeros to at least width digits."""
    out = ""
    m = n
    while m > 0:
        out = str(m % 2) + out
        m = m // 2
    out = out or "0"
    while len(out) < width:
        out = "0" + out
    return out


def hexstr(n: int) -> str:
    digits = "0123456789abcdef"
    out = ""
    m = n
    while m > 0:
        out = digits[m % 16] + out
        m = m // 16
    return out or "0"


def popcount(n: int) -> int:
    return sum(1 for ch in binstr(n) if ch == "1")


W = {"py": 64, "js": 32}


def b_op(lang: str, op: str, x: int, y: int) -> int:
    return bitwise(op, i32(x) if lang == "js" else x, i32(y) if lang == "js" else y, W[lang])


def b_shl(lang: str, x: int, k: int) -> int:
    return x * ipow(2, k) if lang == "py" else js_shl(x, k)


def b_shr(lang: str, x: int, k: int) -> int:
    return x // ipow(2, k) if lang == "py" else js_shr(x, k)


_BITNAME = {"&": "and", "|": "or", "^": "xor"}
_BITRULE = {"&": "& keeps a bit only where both numbers have it.",
            "|": "| keeps a bit where either number has it.",
            "^": "^ keeps a bit where exactly one of the numbers has it."}


def _bits_why(op: str, a: int, b: int, res: int) -> str:
    wd = max(len(binstr(a)), len(binstr(b)), 4)
    return f"{a} is {binstr(a, wd)} and {b} is {binstr(b, wd)}, so {_BITRULE[op]} That gives {binstr(res, wd)}, which is {res}."


def _bit_item(prompt: str, got: int | str, why: str) -> Item:
    return Item(prompt, str(got), why)


def _op_dec(op: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        a, b = rng.sample(range(1, 16), 2)
        res = b_op(lang, op, a, b)
        return _bit_item(f"{a} {op} {b}", res, _bits_why(op, a, b, res))
    f.__name__ = "bits_dec_" + _BITNAME[op]
    return f


def _op_bin(op: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        a, b = rng.sample(range(1, 16), 2)
        res = b_op(lang, op, a, b)
        return _bit_item(f"0b{binstr(a, 4)} {op} 0b{binstr(b, 4)}", res, _bits_why(op, a, b, res))
    f.__name__ = "bits_bin_" + _BITNAME[op]
    return f


def _op_hex(op: str) -> Callable:
    def f(rng: random.Random, lang: str) -> Item:
        a, b = rng.sample(range(16, 256), 2)
        res = b_op(lang, op, a, b)
        return _bit_item(f"0x{hexstr(a)} {op} 0x{hexstr(b)}", res,
                         f"0x{hexstr(a)} is {a} and 0x{hexstr(b)} is {b}; as bits that is {binstr(a, 8)} {op} {binstr(b, 8)} = {binstr(res, 8)}, so {res}.")
    f.__name__ = "bits_hex_" + _BITNAME[op]
    return f


def bits_shl(rng: random.Random, lang: str) -> Item:
    a, k = rng.randint(1, 9), rng.randint(1, 4)
    return _bit_item(f"{a} << {k}", b_shl(lang, a, k), f"<< {k} moves every bit {k} places left: it multiplies by 2 to the power {k}.")


def bits_shr(rng: random.Random, lang: str) -> Item:
    a, k = rng.randint(8, 99), rng.randint(1, 3)
    return _bit_item(f"{a} >> {k}", b_shr(lang, a, k), f">> {k} drops the lowest {k} bits: it divides by 2 to the power {k}, rounding down.")


def bits_one_shl(rng: random.Random, lang: str) -> Item:
    k = rng.randint(1, 8)
    return _bit_item(f"1 << {k}", b_shl(lang, 1, k), f"1 << {k} is a single 1 bit moved {k} places: 2 to the power {k}.")


def bits_double(rng: random.Random, lang: str) -> Item:
    n = rng.randint(3, 40)
    return _bit_item(f"{n} << 1", b_shl(lang, n, 1), "Shifting left by one doubles it.")


def bits_halve(rng: random.Random, lang: str) -> Item:
    n = rng.randint(3, 60)
    return _bit_item(f"{n} >> 1", b_shr(lang, n, 1), "Shifting right by one halves it, dropping the remainder.")


def bits_not(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 20)
    return _bit_item(f"~{a}", bit_not(a, W[lang]), f"~ flips every bit; for whole numbers ~n is -n - 1, so ~{a} is {-a - 1}.")


def bits_not_special(rng: random.Random, lang: str) -> Item:
    a = rng.choice((0, -1, -2, -5, -9))
    return _bit_item(f"~{a}" if a >= 0 else f"~({a})", bit_not(a, W[lang]), f"~n is -n - 1, so ~{a} is {-a - 1}.")


def bits_not_not(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 20)
    return _bit_item(f"~~{a}", bit_not(bit_not(a, W[lang]), W[lang]), "Flipping all the bits twice gives the number back.")


def bits_odd(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 40)
    return _bit_item(f"{n} & 1", b_op(lang, "&", n, 1), "& 1 keeps only the lowest bit: 1 for an odd number, 0 for an even one.")


def bits_clear_low(rng: random.Random, lang: str) -> Item:
    n = rng.randint(2, 40)
    res = b_op(lang, "&", n, n - 1)
    return _bit_item(f"{n} & ({n} - 1)", res, f"n & (n - 1) clears the lowest 1 bit: {binstr(n)} & {binstr(n - 1)} = {binstr(res)}.")


def bits_xor_self(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 30)
    return _bit_item(f"{a} ^ {a}", 0, "Every bit is the same on both sides, so xor gives 0.")


def bits_identity(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 30)
    op, other = rng.choice([("^", 0), ("|", 0), ("&", 0)])
    return _bit_item(f"{a} {op} {other}", b_op(lang, op, a, other),
                     {"^": "xor with 0 changes nothing.", "|": "or with 0 changes nothing.", "&": "and with 0 clears every bit."}[op])


def bits_xor_twice(rng: random.Random, lang: str) -> Item:
    a, b = rng.sample(range(1, 30), 2)
    return _bit_item(f"({a} ^ {b}) ^ {b}", a, "xor with the same number twice undoes itself.")


def bits_flags(rng: random.Random, lang: str) -> Item:
    flags = {"READ": 1, "WRITE": 2, "EXEC": 4}
    names = list(flags)
    have = rng.sample(names, rng.randint(1, 2))
    test = rng.choice(names)
    perm = 0
    for nm in have:
        perm = b_op(lang, "|", perm, flags[nm])
    got = b_op(lang, "&", perm, flags[test])
    setup = "READ, WRITE, EXEC = 1, 2, 4" if lang == "py" else "const READ = 1, WRITE = 2, EXEC = 4;"
    perm_line = "perm = " + " | ".join(have) if lang == "py" else "const perm = " + " | ".join(have) + ";"
    return _bit_item(f"{setup}\n{perm_line}\nperm & {test}", got,
                     f"perm is {perm}. & {test} keeps the {test} bit: it is {'there' if got else 'missing'}.")


def bits_flag_clear(rng: random.Random, lang: str) -> Item:
    flags = {"READ": 1, "WRITE": 2, "EXEC": 4}
    drop = rng.choice(list(flags))
    perm = rng.randint(3, 7)
    got = b_op(lang, "&", perm, bit_not(flags[drop], W[lang]))
    setup = "READ, WRITE, EXEC = 1, 2, 4" if lang == "py" else "const READ = 1, WRITE = 2, EXEC = 4;"
    return _bit_item(f"{setup}\n{perm} & ~{drop}", got, f"~{drop} flips every bit, so & ~{drop} clears just the {drop} bit.")


def bits_prec_shift(rng: random.Random, lang: str) -> Item:
    a, b, k = rng.randint(1, 5), rng.randint(1, 5), rng.randint(1, 3)
    return _bit_item(f"{a} + {b} << {k}", b_shl(lang, a + b, k), f"+ binds tighter than <<, so this is ({a} + {b}) << {k}.")


def bits_prec_shift_add(rng: random.Random, lang: str) -> Item:
    a, c = rng.randint(1, 6), rng.randint(1, 2)
    return _bit_item(f"{a} << 1 + {c}", b_shl(lang, a, 1 + c), f"+ binds tighter than <<, so this is {a} << (1 + {c}).")


def bits_prec_and_or(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 16), 3)
    return _bit_item(f"{a} | {b} & {c}", b_op(lang, "|", a, b_op(lang, "&", b, c)), f"& binds tighter than |, so this is {a} | ({b} & {c}).")


def bits_prec_or_xor(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 16), 3)
    return _bit_item(f"{a} | {b} ^ {c}", b_op(lang, "|", a, b_op(lang, "^", b, c)), f"^ binds tighter than |, so this is {a} | ({b} ^ {c}).")


def bits_prec_xor_and(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 16), 3)
    return _bit_item(f"{a} ^ {b} & {c}", b_op(lang, "^", a, b_op(lang, "&", b, c)), f"& binds tighter than ^, so this is {a} ^ ({b} & {c}).")


def bits_neg_and(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 9)
    mask = rng.choice((15, 255))
    return _bit_item(f"-{a} & {mask}", b_op(lang, "&", -a, mask), f"-{a} is all 1s up to the last few bits; & {mask} keeps the low {len(binstr(mask))} of them: {mask + 1 - a}.")


def bits_neg_shr(rng: random.Random, lang: str) -> Item:
    a = rng.choice((-1, -3, -7, -8, -9, -12))
    k = rng.randint(1, 2)
    return _bit_item(f"({a}) >> {k}", b_shr(lang, a, k), "A right shift rounds down (toward minus infinity), so a negative number stays negative.")


def bits_neg_shl(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 6)
    k = rng.randint(1, 3)
    return _bit_item(f"-{a} << {k}", b_shl(lang, -a, k), f"A left shift still multiplies by 2 to the power {k}, sign and all.")


def bits_lowbit(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 40)
    return _bit_item(f"{n} & -{n}", b_op(lang, "&", n, -n), "n & -n keeps only the lowest 1 bit of n.")


def bits_mask_low(rng: random.Random, lang: str) -> Item:
    n = rng.randint(8, 99)
    k = rng.choice((3, 7, 15))
    return _bit_item(f"{n} & {k}", b_op(lang, "&", n, k), f"& {k} keeps only the lowest {len(binstr(k))} bits: the remainder after dividing by {k + 1}.")


def bits_test_bit(rng: random.Random, lang: str) -> Item:
    n = rng.randint(8, 99)
    k = rng.randint(1, 4)
    return _bit_item(f"({n} >> {k}) & 1", b_op(lang, "&", b_shr(lang, n, k), 1), f"Shift bit {k} down to the bottom, then & 1 reads it.")


def bits_set_bit(rng: random.Random, lang: str) -> Item:
    n, k = rng.randint(1, 30), rng.randint(0, 4)
    return _bit_item(f"{n} | (1 << {k})", b_op(lang, "|", n, b_shl(lang, 1, k)), f"1 << {k} is a mask with only bit {k}; | turns that bit on.")


def bits_toggle(rng: random.Random, lang: str) -> Item:
    n, k = rng.randint(1, 30), rng.randint(0, 4)
    return _bit_item(f"{n} ^ (1 << {k})", b_op(lang, "^", n, b_shl(lang, 1, k)), f"1 << {k} is a mask with only bit {k}; ^ flips that bit.")


def bits_pack(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(1, 15), rng.randint(1, 15)
    return _bit_item(f"({a} << 4) | {b}", b_op(lang, "|", b_shl(lang, a, 4), b), f"{a} moves up into the high nibble, then {b} fills the low one: {a * 16 + b}.")


def bits_unpack(rng: random.Random, lang: str) -> Item:
    n = rng.randint(17, 255)
    if rng.random() < 0.5:
        return _bit_item(f"0x{hexstr(n)} >> 4", b_shr(lang, n, 4), "Shifting right by 4 drops the low hex digit.")
    return _bit_item(f"0x{hexstr(n)} & 0xF", b_op(lang, "&", n, 15), "& 0xF keeps only the low hex digit.")


def bits_shl_or(rng: random.Random, lang: str) -> Item:
    a, b = rng.randint(1, 7), rng.randint(0, 3)
    return _bit_item(f"{a} << 2 | {b}", b_op(lang, "|", b_shl(lang, a, 2), b), f"<< binds tighter than |, so this is ({a} << 2) | {b}.")


def bits_pow2(rng: random.Random, lang: str) -> Item:
    n = rng.choice((1, 2, 3, 4, 6, 8, 12, 16, 20, 32, 33, 64))
    zero = b_op(lang, "&", n, n - 1) == 0
    return _bit_item(f"({n} & ({n} - 1)) == 0", tf(lang, zero), "A power of two has a single 1 bit, which n & (n - 1) clears to 0.")


def bits_compound(rng: random.Random, lang: str) -> Item:
    x, k, m = rng.randint(1, 6), rng.randint(1, 3), rng.randint(1, 3)
    got = b_op(lang, "|", b_shl(lang, x, k), m)
    lines = [f"x = {x}", f"x <<= {k}", f"x |= {m}", "x"] if lang == "py" else [f"let x = {x};", f"x <<= {k};", f"x |= {m};", "x"]
    return _bit_item("\n".join(lines), got, "x <<= k and x |= m are shorthand for x = x << k and x = x | m.")


def bits_xor_swap(rng: random.Random, lang: str) -> Item:
    a, b = rng.sample(range(1, 30), 2)
    lines = ([f"a, b = {a}, {b}", "a ^= b", "b ^= a", "a ^= b", "(a, b)"] if lang == "py"
             else [f"let a = {a}, b = {b};", "a ^= b;", "b ^= a;", "a ^= b;", "[a, b]"])
    return _bit_item("\n".join(lines), show(lang, (b, a) if lang == "py" else [b, a]), "Three xors swap the two numbers without a spare variable.")


BITS_SHARED: list[Callable] = (
    [_op_dec(o) for o in "&|^"] + [_op_bin(o) for o in "&|^"] + [_op_hex(o) for o in "&^"]
    + [bits_shl, bits_shr, bits_one_shl, bits_double, bits_halve, bits_not, bits_not_special, bits_not_not, bits_odd,
       bits_clear_low, bits_xor_self, bits_identity, bits_xor_twice, bits_flags, bits_flag_clear, bits_prec_shift,
       bits_prec_shift_add, bits_prec_and_or, bits_prec_or_xor, bits_prec_xor_and, bits_neg_and, bits_neg_shr,
       bits_neg_shl, bits_lowbit, bits_mask_low, bits_test_bit, bits_set_bit, bits_toggle, bits_pack, bits_unpack,
       bits_shl_or, bits_pow2, bits_compound, bits_xor_swap]
)


def bits_py_bin(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 40)
    return _bit_item(f"bin({n})", "0b" + binstr(n), "bin() writes the binary digits after the 0b prefix, as text.")


def bits_py_bin_op(rng: random.Random, lang: str) -> Item:
    a, b = rng.sample(range(1, 16), 2)
    op = rng.choice("&|^")
    return _bit_item(f"bin({a} {op} {b})", "0b" + binstr(b_op("py", op, a, b)), "Work out the bit operation, then write the result in binary.")


def bits_py_length(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 255)
    return _bit_item(f"({n}).bit_length()", len(binstr(n)), f"{n} needs {len(binstr(n))} binary digits.")


def bits_py_popcount(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 255)
    return _bit_item(f'bin({n}).count("1")', popcount(n), f"{n} is {binstr(n)} in binary: count the 1s.")


def bits_py_int2(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 31)
    return _bit_item(f'int("{binstr(n)}", 2)', n, "int(text, 2) reads the text as binary digits.")


def bits_py_format(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 100)
    return _bit_item(f'format({n}, "08b")', binstr(n, 8), "format with 08b writes 8 binary digits, padded with zeros.")


def bits_py_hex(rng: random.Random, lang: str) -> Item:
    n = rng.randint(10, 255)
    return _bit_item(f"hex({n})", "0x" + hexstr(n), "hex() writes the hexadecimal digits after 0x, as text.")


def bits_py_bool(rng: random.Random, lang: str) -> Item:
    a, b = rng.random() < 0.5, rng.random() < 0.5
    op = rng.choice("&|^")
    got = {"&": a and b, "|": a or b, "^": a != b}[op]
    return _bit_item(f"{tf('py', a)} {op} {tf('py', b)}", tf("py", got),
                     "On two bools, & | ^ give a bool back (not 0 or 1).")


def bits_py_bool_not(rng: random.Random, lang: str) -> Item:
    if rng.random() < 0.5:
        return _bit_item("~True", -2, "True counts as 1, and ~1 is -2.")
    return _bit_item("~False", -1, "False counts as 0, and ~0 is -1.")


def bits_py_cmp(rng: random.Random, lang: str) -> Item:
    a, b = rng.sample(range(1, 16), 2)
    res = b_op("py", "&", a, b)
    c = res if rng.random() < 0.5 else res + 1
    return _bit_item(f"{a} & {b} == {c}", tf("py", res == c), f"In Python & binds tighter than ==, so this is ({a} & {b}) == {c}.")


def bits_py_cmp_odd(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 30)
    return _bit_item(f"{n} & 1 == 0", tf("py", n % 2 == 0), f"In Python & binds tighter than ==, so this is ({n} & 1) == 0: is it even?")


def bits_py_neg_big(rng: random.Random, lang: str) -> Item:
    k = rng.randint(40, 70)
    return _bit_item(f"1 << {k} > 2 ** {k - 1}", "True", "Python ints do not overflow: 1 << k is 2 to the power k, always bigger than half of it.")


PY_BITS = [bind(f, "py") for f in BITS_SHARED] + [bind(f, "py") for f in (
    bits_py_bin, bits_py_bin_op, bits_py_length, bits_py_popcount, bits_py_int2, bits_py_format, bits_py_hex,
    bits_py_bool, bits_py_bool_not, bits_py_cmp, bits_py_cmp_odd, bits_py_neg_big)]

# ── 7. In Range ─────────────────────────────────────────────────────────

def yn_item(lang: str, setup: list[str], expr: str, truth: bool, why: str) -> Item:
    prompt = "\n".join(setup + [expr])
    return Item(prompt, "yes" if truth else "no", why, check=yes_no_py(prompt) if lang == "py" else yes_no_js(prompt))


def _edge_x(rng: random.Random, lo: int, hi: int) -> int:
    return rng.choice((lo - 1, lo, lo, lo + 1, hi - 1, hi, hi, hi + 1, rng.randint(lo, hi)))


def _lohi(rng: random.Random) -> tuple[int, int]:
    lo = rng.randint(1, 5)
    return lo, lo + rng.randint(2, 6)


def _between(kind: str) -> Callable:
    lo_incl, hi_incl = {"open": (False, False), "closed": (True, True), "half_lo": (True, False), "half_hi": (False, True)}[kind]

    def f(rng: random.Random, lang: str) -> Item:
        lo, hi = _lohi(rng)
        x = _edge_x(rng, lo, hi)
        ok = (x >= lo if lo_incl else x > lo) and (x <= hi if hi_incl else x < hi)
        op1, op2 = ("<=" if lo_incl else "<"), ("<=" if hi_incl else "<")
        if lang == "py":
            expr = f"{lo} {op1} x {op2} {hi}"
        else:
            expr = f"x {'>=' if lo_incl else '>'} {lo} && x {op2} {hi}"
        edge = "The ends count" if kind == "closed" else "Neither end counts" if kind == "open" else "Only the low end counts" if kind == "half_lo" else "Only the high end counts"
        return yn_item(lang, decls(lang, {"x": x}), expr, ok, f"x is {x}, the limits are {lo} and {hi}. {edge}.")
    f.__name__ = "range_between_" + kind
    return f


def range_out(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    ok = x < lo or x > hi
    return yn_item(lang, decls(lang, {"x": x}), f"x < {lo} {'or' if lang == 'py' else '||'} x > {hi}", ok,
                   f"It says yes for anything outside {lo} to {hi}; x is {x}.")


def range_not_between(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    ok = not (lo <= x <= hi)
    expr = f"not ({lo} <= x <= {hi})" if lang == "py" else f"!(x >= {lo} && x <= {hi})"
    return yn_item(lang, decls(lang, {"x": x}), expr, ok, f"The inside test is {'true' if not ok else 'false'} for x = {x}, and not flips it.")


def _lst(rng: random.Random, n: int = 4) -> list[int]:
    return ints(rng, n, 1, 12)


def range_in_list(rng: random.Random, lang: str) -> Item:
    xs = _lst(rng)
    x = rng.choice(xs) if rng.random() < 0.5 else rng.choice([v for v in range(1, 13) if v not in xs])
    expr = f"x in {lit(xs)}" if lang == "py" else f"{lit(xs)}.includes(x)"
    return yn_item(lang, decls(lang, {"x": x}), expr, x in xs, f"{x} is {'one of' if x in xs else 'not in'} the list.")


def range_not_in_list(rng: random.Random, lang: str) -> Item:
    xs = _lst(rng)
    x = rng.choice(xs) if rng.random() < 0.5 else rng.choice([v for v in range(1, 13) if v not in xs])
    expr = f"x not in {lit(xs)}" if lang == "py" else f"!{lit(xs)}.includes(x)"
    return yn_item(lang, decls(lang, {"x": x}), expr, x not in xs, f"{x} is {'one of' if x in xs else 'not in'} the list, so the answer is {'no' if x in xs else 'yes'}.")


def range_in_set(rng: random.Random, lang: str) -> Item:
    xs = _lst(rng, 3)
    x = rng.choice(xs) if rng.random() < 0.5 else rng.choice([v for v in range(1, 13) if v not in xs])
    expr = "x in {" + ", ".join(map(str, xs)) + "}" if lang == "py" else "new Set(" + lit(xs) + ").has(x)"
    return yn_item(lang, decls(lang, {"x": x}), expr, x in xs, f"{x} is {'in' if x in xs else 'not in'} the set.")


def range_char_in(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["word", "farm", "tree", "code"])
    ch = rng.choice(w) if rng.random() < 0.5 else rng.choice("xyzqj")
    expr = f'"{ch}" in "{w}"' if lang == "py" else f'"{w}".includes("{ch}")'
    return yn_item(lang, [], expr, find(w, ch) != -1, f'"{ch}" is {"a letter of" if find(w, ch) != -1 else "not in"} "{w}".')


def range_substr(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["pumpkin", "carrot", "drone", "maple"])
    i = rng.randint(0, len(w) - 3)
    sub = w[i:i + 2] if rng.random() < 0.5 else w[i] + w[i + 2]
    expr = f'"{sub}" in "{w}"' if lang == "py" else f'"{w}".includes("{sub}")'
    ok = find(w, sub) != -1
    return yn_item(lang, [], expr, ok, f'A run of letters has to appear together: "{sub}" is {"inside" if ok else "not inside"} "{w}".')


def range_empty_str(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["abc", "farm", "x"])
    expr = f'"" in "{w}"' if lang == "py" else f'"{w}".includes("")'
    return yn_item(lang, [], expr, True, "The empty string is inside every string.")


def range_dict_key(rng: random.Random, lang: str) -> Item:
    ks = rng.sample(["a", "b", "c", "k", "name"], 2)
    k = rng.choice(ks + ["z"])
    setup = [f'd = {{"{ks[0]}": 1, "{ks[1]}": 2}}'] if lang == "py" else [f"const d = {{ {ks[0]}: 1, {ks[1]}: 2 }};"]
    return yn_item(lang, setup, f'"{k}" in d', k in ks, f'"{k}" is {"a" if k in ks else "not a"} key of d.')


def range_dict_value(rng: random.Random, lang: str) -> Item:
    ks = rng.sample(["a", "b", "c", "k"], 2)
    vs = ints(rng, 2, 1, 9)
    v = rng.choice(vs + [10])
    setup = ([f'd = {{"{ks[0]}": {vs[0]}, "{ks[1]}": {vs[1]}}}'] if lang == "py"
             else [f"const d = {{ {ks[0]}: {vs[0]}, {ks[1]}: {vs[1]} }};"])
    expr = f"{v} in d.values()" if lang == "py" else f"Object.values(d).includes({v})"
    return yn_item(lang, setup, expr, v in vs, f"{v} is {'one of' if v in vs else 'not one of'} the values.")


def range_dict_value_trap(rng: random.Random, lang: str) -> Item:
    ks = rng.sample(["a", "b", "c", "k"], 2)
    vs = ints(rng, 2, 1, 9)
    v = rng.choice(vs)
    setup = ([f'd = {{"{ks[0]}": {vs[0]}, "{ks[1]}": {vs[1]}}}'] if lang == "py"
             else [f"const d = {{ {ks[0]}: {vs[0]}, {ks[1]}: {vs[1]} }};"])
    return yn_item(lang, setup, f"{v} in d", False, f"in looks at the keys, and the keys here are names, not {v}.")


def range_order3(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.choice([(2, 5, 9), (3, 3, 8), (1, 6, 4), (5, 2, 7), (4, 9, 9), (1, 2, 3)]) if rng.random() < 0.6 else rng.sample(range(1, 10), 3)
    expr = "a < b < c" if lang == "py" else "a < b && b < c"
    return yn_item(lang, decls(lang, {"a": a, "b": b, "c": c}), expr, a < b < c, f"Is {a} < {b} and {b} < {c}?")


def range_mixed_chain(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.sample(range(1, 10), 3)
    expr = "a < b > c" if lang == "py" else "a < b && b > c"
    return yn_item(lang, decls(lang, {"a": a, "b": b, "c": c}), expr, a < b and b > c, f"b has to be bigger than both: {a} < {b} and {b} > {c}.")


def range_eq_chain(rng: random.Random, lang: str) -> Item:
    a, b, c = rng.choice([(2, 2, 2), (2, 2, 3), (3, 2, 2), (4, 4, 4), (5, 4, 5)])
    expr = "a == b == c" if lang == "py" else "a === b && b === c"
    return yn_item(lang, decls(lang, {"a": a, "b": b, "c": c}), expr, a == b == c, "All three must be equal.")


def range_index_valid(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(3, 5))
    i = rng.choice((-1, 0, len(xs) - 1, len(xs), len(xs) + 1, 1))
    expr = "0 <= i < len(xs)" if lang == "py" else "i >= 0 && i < xs.length"
    return yn_item(lang, decls(lang, {"xs": xs, "i": i}), expr, 0 <= i < len(xs),
                   f"Valid positions are 0 to {len(xs) - 1}; i is {i}.")


def range_even_in(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    expr = f"x % 2 == 0 and {lo} <= x <= {hi}" if lang == "py" else f"x % 2 === 0 && x >= {lo} && x <= {hi}"
    return yn_item(lang, decls(lang, {"x": x}), expr, x % 2 == 0 and lo <= x <= hi, f"x must be even and from {lo} to {hi}; x is {x}.")


def range_lower_letter(rng: random.Random, lang: str) -> Item:
    ch = rng.choice("amzAMZ05_")
    expr = '"a" <= ch <= "z"' if lang == "py" else 'ch >= "a" && ch <= "z"'
    return yn_item(lang, decls(lang, {"ch": ch}), expr, "a" <= ch <= "z", "Letters compare by their character codes: lowercase a-z sit together, after the capitals and digits.")


def range_digit(rng: random.Random, lang: str) -> Item:
    ch = rng.choice("0159a/:x")
    expr = '"0" <= ch <= "9"' if lang == "py" else 'ch >= "0" && ch <= "9"'
    return yn_item(lang, decls(lang, {"ch": ch}), expr, "0" <= ch <= "9", "Digits sit together in the character codes, from 0 to 9.")


def range_len_between(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["key", "farm", "drone", "pumpkin", "tree"])
    lo, hi = 3, rng.randint(4, 6)
    expr = f"{lo} <= len(w) <= {hi}" if lang == "py" else f"w.length >= {lo} && w.length <= {hi}"
    return yn_item(lang, decls(lang, {"w": w}), expr, lo <= len(w) <= hi, f'"{w}" has {len(w)} letters; the range is {lo} to {hi}.')


def range_abs(rng: random.Random, lang: str) -> Item:
    x = rng.randint(-6, 6)
    k = rng.randint(2, 4)
    expr = f"abs(x) < {k}" if lang == "py" else f"Math.abs(x) < {k}"
    return yn_item(lang, decls(lang, {"x": x}), expr, abs(x) < k, f"abs(x) is {abs(x)}: the distance from 0 has to be under {k}.")


def range_str_vs_num(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 9)
    if rng.random() < 0.5:
        expr = f'{n} in ["{n}", "{n + 1}"]' if lang == "py" else f'["{n}", "{n + 1}"].includes({n})'
        return yn_item(lang, [], expr, False, f'The number {n} is not the string "{n}": it is not in the list.')
    expr = f'"{n}" in ["{n}", "{n + 1}"]' if lang == "py" else f'["{n}", "{n + 1}"].includes("{n}")'
    return yn_item(lang, [], expr, True, f'"{n}" is in the list: same type, same text.')


def range_str_in_list(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["farm", "drone", "carrot"])
    part = w[:2]
    expr = f'"{part}" in ["{w}", "tree"]' if lang == "py" else f'["{w}", "tree"].includes("{part}")'
    return yn_item(lang, [], expr, False, f'In a list, in needs a whole item: "{part}" is only part of "{w}".')


def range_empty_list(rng: random.Random, lang: str) -> Item:
    x = rng.randint(0, 9)
    expr = f"{x} in []" if lang == "py" else f"[].includes({x})"
    return yn_item(lang, [], expr, False, "Nothing is in an empty list.")


def range_two_in(rng: random.Random, lang: str) -> Item:
    xs = _lst(rng)
    a = rng.choice(xs)
    b = rng.choice(xs + [rng.choice([v for v in range(1, 13) if v not in xs])])
    if lang == "py":
        expr = f"{a} in {lit(xs)} and {b} not in {lit(xs)}"
    else:
        expr = f"{lit(xs)}.includes({a}) && !{lit(xs)}.includes({b})"
    return yn_item(lang, [], expr, a in xs and b not in xs, f"{a} is in the list; is {b} left out?")


def range_chain4(rng: random.Random, lang: str) -> Item:
    vals = rng.choice([(1, 2, 3, 4), (1, 3, 2, 4), (1, 2, 2, 4), (4, 3, 2, 1), (2, 5, 7, 9), (2, 5, 4, 9)])
    a, b, c, d = vals
    expr = f"{a} < {b} < {c} < {d}" if lang == "py" else f"{a} < {b} && {b} < {c} && {c} < {d}"
    return yn_item(lang, [], expr, a < b < c < d, "Every neighbouring pair has to be in order.")


def range_first_vowel(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["apple", "farm", "umbra", "tree", "owl", "drone"])
    expr = 'w[0] in "aeiou"' if lang == "py" else '"aeiou".includes(w[0])'
    return yn_item(lang, decls(lang, {"w": w}), expr, w[0] in "aeiou", f'"{w}" starts with "{w[0]}".')


def range_found(rng: random.Random, lang: str) -> Item:
    xs = _lst(rng)
    x = rng.choice(xs) if rng.random() < 0.5 else rng.choice([v for v in range(1, 13) if v not in xs])
    expr = "xs.count(x) > 0" if lang == "py" else "xs.indexOf(x) !== -1"
    return yn_item(lang, decls(lang, {"xs": xs, "x": x}), expr, x in xs, f"Is {x} somewhere in the list?")


def range_str_cmp(rng: random.Random, lang: str) -> Item:
    a, b = rng.choice([("apple", "banana"), ("Zebra", "apple"), ("10", "9"), ("abc", "abd"), ("a", "B"), ("cat", "cats"), ("2", "10")])
    return yn_item(lang, [], f'"{a}" < "{b}"', a < b,
                   "Strings compare character by character by their codes (capitals before lowercase, '1' before '9'): "
                   + f'"{a}" is {"before" if a < b else "not before"} "{b}".')


RANGE_SHARED: list[Callable] = (
    [_between(k) for k in ("open", "closed", "half_lo", "half_hi")]
    + [range_out, range_not_between, range_in_list, range_not_in_list, range_in_set, range_char_in, range_substr,
       range_empty_str, range_dict_key, range_dict_value, range_dict_value_trap, range_order3, range_mixed_chain,
       range_eq_chain, range_index_valid, range_even_in, range_lower_letter, range_digit, range_len_between,
       range_abs, range_str_vs_num, range_str_in_list, range_empty_list, range_two_in, range_chain4,
       range_first_vowel, range_found, range_str_cmp]
)


def range_py_range(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("py", decls("py", {"x": x}), f"x in range({lo}, {hi})", lo <= x < hi,
                   f"range({lo}, {hi}) stops before {hi}, so {hi} is not in it; x is {x}.")


def range_py_range_incl(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("py", decls("py", {"x": x}), f"x in range({lo}, {hi} + 1)", lo <= x < hi + 1,
                   f"The + 1 lets {hi} in: the numbers are {lo} to {hi}; x is {x}.")


def range_py_step(rng: random.Random, lang: str) -> Item:
    x = rng.randint(0, 11)
    return yn_item("py", decls("py", {"x": x}), "x in range(0, 10, 2)", x in (0, 2, 4, 6, 8), "range(0, 10, 2) is 0, 2, 4, 6, 8.")


def range_py_down(rng: random.Random, lang: str) -> Item:
    x = rng.randint(0, 11)
    return yn_item("py", decls("py", {"x": x}), "x in range(10, 0, -2)", x in (10, 8, 6, 4, 2), "range(10, 0, -2) is 10, 8, 6, 4, 2: it stops before 0.")


def range_py_index(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(3, 5))
    i = rng.choice((-1, 0, len(xs) - 1, len(xs), len(xs) + 1))
    return yn_item("py", decls("py", {"xs": xs, "i": i}), "i in range(len(xs))", 0 <= i < len(xs),
                   f"range(len(xs)) is the valid positions 0 to {len(xs) - 1}; -1 is not in it.")


def range_py_neg(rng: random.Random, lang: str) -> Item:
    n = rng.randint(3, 9)
    return yn_item("py", [], f"-1 in range({n})", False, "range counts up from 0, so -1 is never in it.")


def range_py_eq_lt(rng: random.Random, lang: str) -> Item:
    x = rng.randint(2, 6)
    b = rng.randint(2, 6)
    c = rng.randint(3, 7)
    return yn_item("py", decls("py", {"x": x}), f"{b} == x < {c}", b == x and x < c,
                   f"A chain: {b} == x and x < {c}; both have to hold.")


def range_py_list_in_list(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 5)
    return yn_item("py", [], f"[{a}] in [[{a}], [{a + 1}]]", True, "Lists compare by content, so [x] equals the [x] inside.")


def range_py_nested(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 5)
    return yn_item("py", [], f"{a} in [[{a}, {a + 1}], [{a + 2}]]", False, f"The items of the outer list are lists, and none of them equals {a}.")


def range_py_tuple(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, 3, 1, 9)
    x = rng.choice(xs + [10])
    return yn_item("py", decls("py", {"x": x}), f"x in ({xs[0]}, {xs[1]}, {xs[2]})", x in xs,
                   f"x is {x}, which is {'one of' if x in xs else 'not one of'} the tuple's items.")


def range_py_chain_cmp_len(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, rng.randint(2, 6))
    return yn_item("py", decls("py", {"xs": xs}), "1 < len(xs) < 5", 1 < len(xs) < 5, f"len(xs) is {len(xs)}.")


def range_py_not_chain(rng: random.Random, lang: str) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("py", decls("py", {"x": x}), f"not {lo} < x < {hi}", not (lo < x < hi), f"not flips the whole chain: is x outside ({lo}, {hi})? x is {x}.")


def range_py_dict_get(rng: random.Random, lang: str) -> Item:
    k = rng.choice(["a", "b", "z"])
    return yn_item("py", ['d = {"a": 1, "b": 2}'], f'd.get("{k}") is not None', k in ("a", "b"), "get gives None for a missing key.")


def range_py_str_slice(rng: random.Random, lang: str) -> Item:
    w = rng.choice(["pumpkin", "carrot", "maple"])
    sub = rng.choice([w[1:4], w[:2], w[2] + w[0]])
    return yn_item("py", [], f'"{sub}" in "{w}"', find(w, sub) != -1, f'"{sub}" is {"inside" if find(w, sub) != -1 else "not inside"} "{w}" as one run.')


def range_py_any(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, 4, 1, 12)
    lo, hi = _lohi(rng)
    return yn_item("py", decls("py", {"xs": xs}), f"any({lo} <= x <= {hi} for x in xs)", any(lo <= x <= hi for x in xs),
                   f"Is at least one item from {lo} to {hi}?")


PY_RANGE = [bind(f, "py") for f in RANGE_SHARED] + [bind(f, "py") for f in (
    range_py_range, range_py_range_incl, range_py_step, range_py_down, range_py_index, range_py_neg, range_py_eq_lt,
    range_py_list_in_list, range_py_nested, range_py_tuple, range_py_chain_cmp_len, range_py_not_chain,
    range_py_dict_get, range_py_str_slice, range_py_any)]

# ── 8. Leap & Fizz ──────────────────────────────────────────────────────

YEARS = (1700, 1800, 1900, 2000, 2100, 2200, 2400, 1996, 2004, 2012, 2016, 2020, 2023, 2024, 2025, 1999, 2028, 2019)


def divides(n: int, d: int) -> bool:
    return fmod(n, d) == 0


def leap(y: int) -> bool:
    return divides(y, 4) and (not divides(y, 100) or divides(y, 400))


def prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, n):
        if divides(n, d):
            return False
    return True


def code(lang: str, py_lines: list[str], js_lines: list[str]) -> str:
    return "\n".join(py_lines if lang == "py" else js_lines)


def classic(prompt: str, got: Any, lang: str, why: str) -> Item:
    return Item(prompt, show(lang, got), why)


def _leap_why(y: int) -> str:
    r4, r100, r400 = fmod(y, 4), fmod(y, 100), fmod(y, 400)
    return (f"{y} % 4 is {r4}, % 100 is {r100}, % 400 is {r400}: a leap year is divisible by 4, except centuries, "
            "unless the century is divisible by 400.")


def _year(rng: random.Random) -> int:
    return rng.choice(YEARS)


def leap_std(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    p = code(lang, ["def is_leap(y):", "    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)", f"is_leap({y})"],
             ["function isLeap(y) {", "  return y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);", "}", f"isLeap({y})"])
    return classic(p, leap(y), lang, _leap_why(y))


def leap_nested(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    p = code(lang, ["def is_leap(y):", "    if y % 400 == 0:", "        return True", "    if y % 100 == 0:",
                    "        return False", "    return y % 4 == 0", f"is_leap({y})"],
             ["function isLeap(y) {", "  if (y % 400 === 0) return true;", "  if (y % 100 === 0) return false;",
              "  return y % 4 === 0;", "}", f"isLeap({y})"])
    return classic(p, leap(y), lang, "Checked in order: divisible by 400 is leap, other centuries are not, otherwise every 4th year is.")


def leap_alt(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    expr = "y % 400 == 0 or (y % 4 == 0 and y % 100 != 0)" if lang == "py" else "y % 400 === 0 || (y % 4 === 0 && y % 100 !== 0)"
    p = "\n".join(decls(lang, {"y": y}) + [expr])
    return classic(p, leap(y), lang, _leap_why(y))


def leap_only4(rng: random.Random, lang: str) -> Item:
    y = rng.choice((1900, 2000, 2100, 2024, 2023, 2200, 1996))
    p = code(lang, ["def is_leap(y):", "    return y % 4 == 0", f"is_leap({y})"],
             ["function isLeap(y) {", "  return y % 4 === 0;", "}", f"isLeap({y})"])
    return classic(p, divides(y, 4), lang, f"This version only tests divisibility by 4, so it says {tf(lang, divides(y, 4))} for {y} (centuries need more care).")


def leap_no400(rng: random.Random, lang: str) -> Item:
    y = rng.choice((1900, 2000, 2100, 2400, 2024, 2023, 1600))
    p = code(lang, ["def is_leap(y):", "    return y % 4 == 0 and y % 100 != 0", f"is_leap({y})"],
             ["function isLeap(y) {", "  return y % 4 === 0 && y % 100 !== 0;", "}", f"isLeap({y})"])
    got = divides(y, 4) and not divides(y, 100)
    return classic(p, got, lang, "This version forgets the exception to the exception: years divisible by 400 are leap years, but it says no.")


def leap_remainders(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    got = [fmod(y, 4), fmod(y, 100), fmod(y, 400)]
    expr = "(y % 4, y % 100, y % 400)" if lang == "py" else "[y % 4, y % 100, y % 400]"
    p = "\n".join(decls(lang, {"y": y}) + [expr])
    return classic(p, tuple(got) if lang == "py" else got, lang, "The three remainders are what the leap-year rule looks at.")


def leap_feb(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    cond = "(y % 4 == 0 and (y % 100 != 0 or y % 400 == 0))" if lang == "py" else "(y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0))"
    expr = f"29 if {cond} else 28" if lang == "py" else f"{cond} ? 29 : 28"
    p = "\n".join(decls(lang, {"y": y}) + [expr])
    return classic(p, 29 if leap(y) else 28, lang, "February has 29 days in a leap year, 28 otherwise. " + _leap_why(y))


def leap_days(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    expr = "366 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 365" if lang == "py" else \
        "y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0) ? 366 : 365"
    p = "\n".join(decls(lang, {"y": y}) + [expr])
    return classic(p, 366 if leap(y) else 365, lang, "A leap year has 366 days. " + _leap_why(y))


def leap_century(rng: random.Random, lang: str) -> Item:
    y = rng.choice((1700, 1800, 1900, 2000, 2100, 2200, 2400, 2024, 1996))
    expr = "y % 100 == 0 and y % 400 != 0" if lang == "py" else "y % 100 === 0 && y % 400 !== 0"
    p = "\n".join(decls(lang, {"y": y}) + [expr])
    return classic(p, divides(y, 100) and not divides(y, 400), lang, "True only for a century that is not divisible by 400 - the one kind of 4th year that is not leap.")


def leap_list(rng: random.Random, lang: str) -> Item:
    ys = rng.sample(YEARS, 5)
    got = [y for y in ys if leap(y)]
    if lang == "py":
        expr = f"[y for y in {lit(ys)} if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)]"
    else:
        expr = f"{lit(ys)}.filter(y => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0))"
    return classic(expr, got, lang, "Keeps only the years that pass the leap-year rule, in the same order.")


def leap_count(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1995, 2096)
    k = rng.randint(6, 14)
    got = sum(1 for y in range(a, a + k) if divides(y, 4))
    if lang == "py":
        p = f"len([y for y in range({a}, {a + k}) if y % 4 == 0])"
    else:
        p = f"let c = 0;\nfor (let y = {a}; y < {a + k}; y++) {{\n  if (y % 4 === 0) c++;\n}}\nc"
    return classic(p, got, lang, f"Counts the multiples of 4 from {a} up to {a + k - 1}.")


def leap_next(rng: random.Random, lang: str) -> Item:
    y = rng.choice((1897, 1999, 2021, 2097, 2023, 1895, 2101))
    got = y
    while not leap(got):
        got += 1
    p = code(lang, [f"y = {y}", "while not (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)):", "    y += 1", "y"],
             [f"let y = {y};", "while (!(y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0))) y++;", "y"])
    return classic(p, got, lang, f"y goes up one at a time until it passes the leap-year rule: {got}.")


def _fz(n: int, a: int, b: int, wa: str, wb: str):
    if divides(n, a) and divides(n, b):
        return wa + wb
    if divides(n, a):
        return wa
    if divides(n, b):
        return wb
    return n


_PAIRS = [(3, 5, "Fizz", "Buzz"), (2, 3, "Tick", "Tock"), (3, 4, "Fizz", "Buzz"), (2, 5, "Ping", "Pong")]


def _fz_n(rng: random.Random, a: int, b: int) -> int:
    return rng.choice((a * b, a * b * 2, a, a * 2, b, b * 3, rng.randint(1, 30), rng.randint(1, 30), a * 3 + 1))


def fizz_classic(rng: random.Random, lang: str) -> Item:
    a, b, wa, wb = rng.choice(_PAIRS)
    n = _fz_n(rng, a, b)
    p = code(lang, ["def fizz(n):", f"    if n % {a} == 0 and n % {b} == 0:", f'        return "{wa}{wb}"',
                    f"    if n % {a} == 0:", f'        return "{wa}"', f"    if n % {b} == 0:", f'        return "{wb}"',
                    "    return n", f"fizz({n})"],
             ["function fizz(n) {", f'  if (n % {a} === 0 && n % {b} === 0) return "{wa}{wb}";',
              f'  if (n % {a} === 0) return "{wa}";', f'  if (n % {b} === 0) return "{wb}";', "  return n;", "}", f"fizz({n})"])
    return classic(p, _fz(n, a, b, wa, wb), lang, f"Divisible by both {a} and {b} comes first; then {a}, then {b}; otherwise the number itself.")


def fizz_bad_order(rng: random.Random, lang: str) -> Item:
    a, b, wa, wb = rng.choice(_PAIRS)
    n = rng.choice((a * b, a * b * 2, a, b, a * b * 3, rng.randint(1, 30)))
    p = code(lang, ["def fizz(n):", f"    if n % {a} == 0:", f'        return "{wa}"', f"    if n % {b} == 0:",
                    f'        return "{wb}"', f"    if n % {a * b} == 0:", f'        return "{wa}{wb}"', "    return n", f"fizz({n})"],
             ["function fizz(n) {", f'  if (n % {a} === 0) return "{wa}";', f'  if (n % {b} === 0) return "{wb}";',
              f'  if (n % {a * b} === 0) return "{wa}{wb}";', "  return n;", "}", f"fizz({n})"])
    got = wa if divides(n, a) else wb if divides(n, b) else wa + wb if divides(n, a * b) else n
    return classic(p, got, lang, f"The test for {a * b} is last, so {a} or {b} catches the number first - it can never be reached.")


def fizz_concat(rng: random.Random, lang: str) -> Item:
    a, b, wa, wb = rng.choice(_PAIRS)
    n = _fz_n(rng, a, b)
    p = code(lang, ["def fizz(n):", '    s = ""', f"    if n % {a} == 0:", f'        s += "{wa}"', f"    if n % {b} == 0:",
                    f'        s += "{wb}"', "    return s or n", f"fizz({n})"],
             ["function fizz(n) {", '  let s = "";', f'  if (n % {a} === 0) s += "{wa}";', f'  if (n % {b} === 0) s += "{wb}";',
              "  return s || n;", "}", f"fizz({n})"])
    return classic(p, _fz(n, a, b, wa, wb), lang, "Each test adds its word; if nothing was added, the empty string is falsy and the number is returned.")


def fizz_oneliner(rng: random.Random, lang: str) -> Item:
    a, b, wa, wb = rng.choice(_PAIRS)
    n = _fz_n(rng, a, b)
    if lang == "py":
        p = f'n = {n}\n("" if n % {a} else "{wa}") + ("" if n % {b} else "{wb}") or n'
    else:
        p = f'const n = {n};\n(n % {a} ? "" : "{wa}") + (n % {b} ? "" : "{wb}") || n'
    return classic(p, _fz(n, a, b, wa, wb), lang, "A remainder of 0 is falsy, so n % a picks the word exactly when it divides; empty text falls back to n.")


def fizz_list4(rng: random.Random, lang: str) -> Item:
    s = rng.randint(1, 26)
    got = [_fz(n, 3, 5, "Fizz", "Buzz") for n in range(s, s + 4)]
    if lang == "py":
        p = ('def fizz(n):\n    return "FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else n\n'
             f"[fizz(n) for n in range({s}, {s + 4})]")
    else:
        p = ('const fizz = (n) => n % 15 === 0 ? "FizzBuzz" : n % 3 === 0 ? "Fizz" : n % 5 === 0 ? "Buzz" : n;\n'
             f"[{', '.join(str(s + i) for i in range(4))}].map(fizz)")
    return classic(p, got, lang, "Four in a row through the classic test, each one a word or itself.")


def _count_loop(lang: str, cond_py: str, cond_js: str, hi: int, start: int = 1, total: bool = False) -> str:
    if lang == "py":
        if total:
            return f"sum(n for n in range({start}, {hi}) if {cond_py})"
        return f"sum(1 for n in range({start}, {hi}) if {cond_py})"
    acc = "s" if total else "c"
    step = "s += n" if total else "c++"
    return f"let {acc} = 0;\nfor (let n = {start}; n < {hi}; n++) {{\n  if ({cond_js}) {step};\n}}\n{acc}"


def fizz_count3(rng: random.Random, lang: str) -> Item:
    top = rng.randint(10, 40)
    k = rng.choice((3, 4, 5, 7))
    got = sum(1 for n in range(1, top + 1) if divides(n, k))
    return classic(_count_loop(lang, f"n % {k} == 0", f"n % {k} === 0", top + 1), got, lang, f"How many numbers from 1 to {top} divide by {k}.")


def fizz_count_both(rng: random.Random, lang: str) -> Item:
    top = rng.randint(30, 80)
    got = sum(1 for n in range(1, top + 1) if divides(n, 3) and divides(n, 5))
    return classic(_count_loop(lang, "n % 3 == 0 and n % 5 == 0", "n % 3 === 0 && n % 5 === 0", top + 1), got, lang,
                   f"The multiples of 15 up to {top}.")


def fizz_count_either(rng: random.Random, lang: str) -> Item:
    top = rng.randint(10, 30)
    got = sum(1 for n in range(1, top + 1) if divides(n, 3) or divides(n, 5))
    return classic(_count_loop(lang, "n % 3 == 0 or n % 5 == 0", "n % 3 === 0 || n % 5 === 0", top + 1), got, lang,
                   f"Numbers up to {top} that are a multiple of 3 or of 5 (or both, counted once).")


def fizz_euler(rng: random.Random, lang: str) -> Item:
    top = rng.randint(10, 30)
    got = sum(n for n in range(top) if divides(n, 3) or divides(n, 5))
    return classic(_count_loop(lang, "n % 3 == 0 or n % 5 == 0", "n % 3 === 0 || n % 5 === 0", top, 0, True), got, lang,
                   f"Adds up the multiples of 3 or 5 below {top}.")


def fizz_next_multiple(rng: random.Random, lang: str) -> Item:
    a = rng.randint(10, 60)
    k = rng.choice((3, 4, 5, 6, 7))
    got = a
    while not divides(got, k):
        got += 1
    p = code(lang, [f"n = {a}", f"while n % {k} != 0:", "    n += 1", "n"], [f"let n = {a};", f"while (n % {k} !== 0) n++;", "n"])
    return classic(p, got, lang, f"Counts up from {a} to the first multiple of {k}.")


def fizz_words(rng: random.Random, lang: str) -> Item:
    n = rng.choice((14, 6, 7, 2, 21, 28, 9, 15, 4))
    got = "Pop" * (1 if divides(n, 2) else 0) + "Bang" * (1 if divides(n, 7) else 0)
    got = got or n
    if lang == "py":
        p = f'def f(n):\n    return "Pop" * (n % 2 == 0) + "Bang" * (n % 7 == 0) or n\nf({n})'
    else:
        p = f'const f = (n) => (n % 2 === 0 ? "Pop" : "") + (n % 7 === 0 ? "Bang" : "") || n;\nf({n})'
    return classic(p, got, lang, "Each part adds its word when it divides, and empty text falls back to the number.")


def div_and(rng: random.Random, lang: str) -> Item:
    a, b = rng.choice([(3, 5), (2, 3), (4, 6), (3, 9), (2, 7)])
    n = rng.choice((a * b, a * b * 2, a, b, a * b + 1, a * 3, b * 4, 30, 12, 18))
    expr = f"n % {a} == 0 and n % {b} == 0" if lang == "py" else f"n % {a} === 0 && n % {b} === 0"
    return classic("\n".join(decls(lang, {"n": n}) + [expr]), divides(n, a) and divides(n, b), lang, f"Is {n} a multiple of both {a} and {b}?")


def div_or(rng: random.Random, lang: str) -> Item:
    a, b = rng.choice([(3, 5), (2, 3), (4, 6), (2, 7)])
    n = rng.randint(1, 40)
    expr = f"n % {a} == 0 or n % {b} == 0" if lang == "py" else f"n % {a} === 0 || n % {b} === 0"
    return classic("\n".join(decls(lang, {"n": n}) + [expr]), divides(n, a) or divides(n, b), lang, f"Is {n} a multiple of {a} or of {b}?")


def div_not(rng: random.Random, lang: str) -> Item:
    k = rng.choice((2, 3, 5, 7))
    n = rng.randint(1, 40)
    expr = f"not n % {k}" if lang == "py" else f"!(n % {k})"
    return classic("\n".join(decls(lang, {"n": n}) + [expr]), divides(n, k), lang, f"n % {k} is 0 when it divides, and 0 is falsy, so not turns it into True.")


def div_filter(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, 6, 1, 20)
    k = rng.choice((2, 3, 4))
    got = [x for x in xs if divides(x, k)]
    expr = f"[x for x in {lit(xs)} if x % {k} == 0]" if lang == "py" else f"{lit(xs)}.filter(x => x % {k} === 0)"
    return classic(expr, got, lang, f"Keeps the multiples of {k}.")


def div_count_even(rng: random.Random, lang: str) -> Item:
    xs = ints(rng, 6, 1, 20)
    got = sum(1 for x in xs if divides(x, 2))
    expr = f"sum(1 for x in {lit(xs)} if x % 2 == 0)" if lang == "py" else f"{lit(xs)}.filter(x => x % 2 === 0).length"
    return classic(expr, got, lang, "Counts the even numbers.")


def div_all(rng: random.Random, lang: str) -> Item:
    k = rng.choice((2, 3, 5))
    xs = [k * rng.randint(1, 6) for _ in range(4)]
    if rng.random() < 0.5:
        xs[rng.randrange(4)] += 1
    got = all(divides(x, k) for x in xs)
    expr = f"all(x % {k} == 0 for x in {lit(xs)})" if lang == "py" else f"{lit(xs)}.every(x => x % {k} === 0)"
    return classic(expr, got, lang, f"Is every item a multiple of {k}?")


def div_any(rng: random.Random, lang: str) -> Item:
    k = rng.choice((3, 4, 5, 7))
    xs = ints(rng, 4, 1, 12)
    got = any(divides(x, k) for x in xs)
    expr = f"any(x % {k} == 0 for x in {lit(xs)})" if lang == "py" else f"{lit(xs)}.some(x => x % {k} === 0)"
    return classic(expr, got, lang, f"Is at least one item a multiple of {k}?")


def div_digit(rng: random.Random, lang: str) -> Item:
    n = rng.randint(100, 9999)
    if rng.random() < 0.5:
        return classic("\n".join(decls(lang, {"n": n}) + ["n % 10"]), fmod(n, 10), lang, "The remainder after dividing by 10 is the last digit.")
    tens = fmod(fdiv(n, 10), 10)
    expr = "n // 10 % 10" if lang == "py" else "Math.floor(n / 10) % 10"
    return classic("\n".join(decls(lang, {"n": n}) + [expr]), tens, lang, "Drop the last digit, then take the new last digit: the tens digit.")


def div_label(rng: random.Random, lang: str) -> Item:
    k = rng.choice((3, 4, 5, 6))
    n = rng.randint(1, 30)
    got = "div" if divides(n, k) else fmod(n, k)
    expr = f'"div" if n % {k} == 0 else n % {k}' if lang == "py" else f'n % {k} === 0 ? "div" : n % {k}'
    return classic("\n".join(decls(lang, {"n": n}) + [expr]), got, lang, f"{n} % {k} is {fmod(n, k)}.")


def div_chain(rng: random.Random, lang: str) -> Item:
    n = rng.randint(10, 60)
    a = rng.randint(4, 9)
    b = rng.randint(2, 4)
    got = fmod(fmod(n, a), b)
    return classic(f"{n} % {a} % {b}", got, lang, f"% goes left to right: {n} % {a} is {fmod(n, a)}, then % {b}.")


def div_neg(rng: random.Random, lang: str) -> Item:
    k = rng.choice((3, 4, 5, 7))
    n = rng.choice([v for v in range(2, 21) if v % k != 0])
    if lang == "py":
        got = fmod(-n, k)
        why = f"Python's % takes the sign of the right side, so -{n} % {k} is {got}, not negative."
    else:
        got = tmod(-n, k)
        why = f"JavaScript's % takes the sign of the left side, so -{n} % {k} is {got}, negative."
    return classic(f"-{n} % {k}", got, lang, why)


def prime_range(rng: random.Random, lang: str) -> Item:
    n = rng.choice((0, 1, 2, 3, 4, 9, 13, 15, 17, 21, 25, 29, 7, 11, 27))
    p = code(lang, ["def is_prime(n):", "    for d in range(2, n):", "        if n % d == 0:", "            return False",
                    "    return n > 1", f"is_prime({n})"],
             ["function isPrime(n) {", "  for (let d = 2; d < n; d++) {", "    if (n % d === 0) return false;", "  }",
              "  return n > 1;", "}", f"isPrime({n})"])
    return classic(p, prime(n), lang, "Looks for a divisor from 2 up to n - 1; 0 and 1 are not prime.")


def prime_bug(rng: random.Random, lang: str) -> Item:
    n = rng.choice((0, 1, 2, 4, 9, 13, 1, 0))
    p = code(lang, ["def is_prime(n):", "    for d in range(2, n):", "        if n % d == 0:", "            return False",
                    "    return True", f"is_prime({n})"],
             ["function isPrime(n) {", "  for (let d = 2; d < n; d++) {", "    if (n % d === 0) return false;", "  }",
              "  return true;", "}", f"isPrime({n})"])
    got = True if n < 2 else prime(n)
    return classic(p, got, lang, "With no check for n < 2 the loop never runs for 0 or 1, and the function falls through to True - a bug.")


def prime_while(rng: random.Random, lang: str) -> Item:
    n = rng.choice((1, 2, 9, 25, 49, 47, 53, 35, 31, 91, 97, 51))
    p = code(lang, ["def is_prime(n):", "    d = 2", "    while d * d <= n:", "        if n % d == 0:", "            return False",
                    "        d += 1", "    return n > 1", f"is_prime({n})"],
             ["function isPrime(n) {", "  let d = 2;", "  while (d * d <= n) {", "    if (n % d === 0) return false;",
              "    d++;", "  }", "  return n > 1;", "}", f"isPrime({n})"])
    return classic(p, prime(n), lang, "Only divisors up to the square root need checking.")


def prime_count_below(rng: random.Random, lang: str) -> Item:
    top = rng.randint(8, 30)
    got = sum(1 for n in range(2, top) if prime(n))
    if lang == "py":
        p = f"sum(1 for n in range(2, {top}) if all(n % d for d in range(2, n)))"
    else:
        p = (f"let c = 0;\nfor (let n = 2; n < {top}; n++) {{\n  let p = true;\n  for (let d = 2; d < n; d++) if (n % d === 0) p = false;\n"
             "  if (p) c++;\n}\nc")
    return classic(p, got, lang, f"Counts the primes below {top}.")


def prime_list(rng: random.Random, lang: str) -> Item:
    a = rng.randint(1, 20)
    got = [n for n in range(a, a + 8) if prime(n)]
    if lang == "py":
        p = f"[n for n in range({a}, {a + 8}) if n > 1 and all(n % d for d in range(2, n))]"
    else:
        p = (f"const out = [];\nfor (let n = {a}; n < {a + 8}; n++) {{\n  let p = n > 1;\n  for (let d = 2; d < n; d++) if (n % d === 0) p = false;\n"
             "  if (p) out.push(n);\n}\nout")
    return classic(p, got, lang, f"The primes from {a} to {a + 7}, in order.")


def prime_smallest_factor(rng: random.Random, lang: str) -> Item:
    n = rng.choice((15, 21, 35, 49, 77, 91, 51, 55, 33, 25, 39, 85, 87, 95))
    got = 2
    while not divides(n, got):
        got += 1
    p = code(lang, [f"n = {n}", "d = 2", "while n % d != 0:", "    d += 1", "d"], [f"const n = {n};", "let d = 2;", "while (n % d !== 0) d++;", "d"])
    return classic(p, got, lang, f"The first d that divides {n} is its smallest factor.")


def prime_count_divisors(rng: random.Random, lang: str) -> Item:
    n = rng.randint(2, 40)
    got = sum(1 for d in range(1, n + 1) if divides(n, d))
    if lang == "py":
        p = f"sum(1 for d in range(1, {n + 1}) if {n} % d == 0)"
    else:
        p = f"let c = 0;\nfor (let d = 1; d <= {n}; d++) {{\n  if ({n} % d === 0) c++;\n}}\nc"
    return classic(p, got, lang, f"How many numbers from 1 to {n} divide {n}.")


def prime_perfect(rng: random.Random, lang: str) -> Item:
    n = rng.choice((6, 28, 12, 8, 10, 496, 20, 6, 28, 18))
    got = sum(d for d in range(1, n) if divides(n, d)) == n
    if lang == "py":
        p = f"sum(d for d in range(1, {n}) if {n} % d == 0) == {n}"
    else:
        p = f"let s = 0;\nfor (let d = 1; d < {n}; d++) {{\n  if ({n} % d === 0) s += d;\n}}\ns === {n}"
    return classic(p, got, lang, f"A perfect number equals the sum of its divisors below itself ({n}).")


def prime_largest_proper(rng: random.Random, lang: str) -> Item:
    n = rng.choice((12, 15, 18, 20, 21, 24, 25, 28, 30, 35, 36, 45, 49, 14))
    got = max(d for d in range(1, n) if divides(n, d))
    if lang == "py":
        p = f"max(d for d in range(1, {n}) if {n} % d == 0)"
    else:
        p = f"let m = 1;\nfor (let d = 1; d < {n}; d++) {{\n  if ({n} % d === 0) m = d;\n}}\nm"
    return classic(p, got, lang, f"The biggest divisor of {n} that is smaller than {n}.")


CLASSIC_SHARED: list[Callable] = [
    leap_std, leap_nested, leap_alt, leap_only4, leap_no400, leap_remainders, leap_feb, leap_days, leap_century,
    leap_list, leap_count, leap_next,
    fizz_classic, fizz_bad_order, fizz_concat, fizz_oneliner, fizz_list4, fizz_count3, fizz_count_both,
    fizz_count_either, fizz_euler, fizz_next_multiple, fizz_words,
    div_and, div_or, div_not, div_filter, div_count_even, div_all, div_any, div_digit, div_label, div_chain, div_neg,
    prime_range, prime_bug, prime_while, prime_count_below, prime_list, prime_smallest_factor, prime_count_divisors,
    prime_perfect, prime_largest_proper,
]


def py_prime_all(rng: random.Random, lang: str) -> Item:
    n = rng.choice((0, 1, 2, 9, 13, 21, 29, 4))
    return classic(f"n = {n}\nn > 1 and all(n % d for d in range(2, n))", prime(n), "py", "all() is True when no d divides n; n > 1 rules out 0 and 1.")


def py_prime_any(rng: random.Random, lang: str) -> Item:
    n = rng.choice((9, 13, 21, 29, 15, 7, 25))
    return classic(f"n = {n}\nnot any(n % d == 0 for d in range(2, n))", prime(n), "py", "True when no number from 2 to n - 1 divides n.")


def py_fizz_dict(rng: random.Random, lang: str) -> Item:
    n = rng.randint(1, 30)
    got = _fz(n, 3, 5, "Fizz", "Buzz")
    p = (f"n = {n}\n" 'out = ""\nif n % 3 == 0:\n    out += "Fizz"\nif n % 5 == 0:\n    out += "Buzz"\nout or n')
    return classic(p, got, "py", "Each if adds its word; an empty out is falsy, so n is the answer.")


def py_leap_words(rng: random.Random, lang: str) -> Item:
    y = _year(rng)
    p = f'y = {y}\n"leap" if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else "common"'
    return classic(p, "leap" if leap(y) else "common", "py", _leap_why(y))


def py_divmod(rng: random.Random, lang: str) -> Item:
    a = rng.randint(10, 99)
    b = rng.randint(3, 9)
    return classic(f"divmod({a}, {b})", (fdiv(a, b), fmod(a, b)), "py", "divmod gives the quotient and the remainder together.")


def py_neg_floor(rng: random.Random, lang: str) -> Item:
    n = rng.randint(2, 20)
    k = rng.choice((3, 4, 5))
    return classic(f"-{n} // {k}", fdiv(-n, k), "py", f"// rounds down toward minus infinity, so -{n} // {k} is {fdiv(-n, k)}.")


PY_CLASSIC = [bind(f, "py") for f in CLASSIC_SHARED] + [bind(f, "py") for f in (
    py_prime_all, py_prime_any, py_fizz_dict, py_leap_words, py_divmod, py_neg_floor)]

# --END--
