"""Flutter state pack, Key Keeps and State Survives: which State goes with which widget after a rebuild.

Both use a FormField as the stateful widget (it copies `initialValue` into its State once and shows it, so the text on
screen tells WHICH State a widget ended up with) and the reconciliation model of `_flutterstate_tree.py`, which writes
out Flutter's own rules: the same runtimeType and key means the element (and its State) is reused; a different one
means a fresh State; a multi-child widget matches children from the top, from the bottom, then by key in the middle;
a GlobalKey carries its State across parents.

The snippet has a global flag `f`; the check sets it to true (once, or true then false) and lets the parent rebuild,
which is what a `setState` that flips `f` higher up would do. The code is written once, with a ternary exactly where
the tree changes.
"""

from __future__ import annotations

import random

from ._flutterstate_common import REBUILD, item, template
from ._flutterstate_tree import FF, MULTI, W, Tree, ff, key_code
from ._model import Maker

ORD = ("1st", "2nd", "3rd", "4th", "5th")
FIELD_BODY = "FormField(%sinitialValue: %s, builder: (s) => Text('${s.value}'))"
ALL_TEXTS = "tester.widgetList<Text>(find.byType(Text, skipOffstage: false))"


# ── Printing a tree, or two trees merged into one with a ternary where they differ ──────────────────────────

def _put(w: W, key_txt: str, arg_txt: str, kids_txt: str) -> str:
    parts = []
    if key_txt:
        parts.append(f"key: {key_txt}")
    if arg_txt:
        parts.append(arg_txt)
    if kids_txt:
        parts.append(("children: " if w.t in MULTI else "child: ") + kids_txt)
    return f"{w.t}({', '.join(parts)})"


def render(w: W, leaf) -> str:
    """The Dart code of a widget tree (`leaf(w, key_text)` writes a FormField)."""
    if w.t == FF:
        return leaf(w, key_code(w.key) if w.key else "")
    kids = [render(k, leaf) for k in w.kids]
    kids_txt = "[" + ", ".join(kids) + "]" if w.t in MULTI else "".join(kids)
    return _put(w, key_code(w.key) if w.key else "", w.arg.replace("{}", w.argv), kids_txt)


def _key_text(b: tuple, a: tuple) -> str:
    if b == a:
        return key_code(b)
    if b[0] == a[0] == "v":
        return f"Key(f ? '{a[1]}' : '{b[1]}')"
    return f"f ? {key_code(a)} : {key_code(b)}"


def merged(b: W, a: W, leaf) -> str:
    """One piece of code for the tree before (f false) and after (f true): `f ? ... : ...` only where they differ."""
    whole = f"f ? {render(a, leaf)} : {render(b, leaf)}"
    if b == a:
        return render(b, leaf)
    if b.t != a.t or (b.key is None) != (a.key is None):
        return whole
    key_txt = _key_text(b.key, a.key) if b.key else ""
    if b.t == FF:
        return leaf(b, key_txt)
    if b.arg != a.arg:
        return whole
    arg_txt = b.arg.replace("{}", b.argv if b.argv == a.argv else f"f ? {a.argv} : {b.argv}")
    if b.t in MULTI:
        if len(b.kids) == len(a.kids):
            kids_txt = "[" + ", ".join(merged(x, y, leaf) for x, y in zip(b.kids, a.kids)) + "]"
        else:
            kids_txt = f"f ? [{', '.join(render(k, leaf) for k in a.kids)}] : [{', '.join(render(k, leaf) for k in b.kids)}]"
    elif len(b.kids) == len(a.kids) == 1:
        kids_txt = merged(b.kids[0], a.kids[0], leaf)
    elif len(b.kids) == len(a.kids) == 0:
        kids_txt = ""
    else:
        return whole
    return _put(b, key_txt, arg_txt, kids_txt)


def _flip(*flags: bool) -> str:
    out = ""
    for flag in flags:
        out += f"f = {str(flag).lower()};\n{REBUILD}"
    return out


# ── Key Keeps ───────────────────────────────────────────────────────────

CHANGES = {
    "swap2": ([0, 1], [1, 0]),
    "rm_first2": ([0, 1], [1]),
    "rm_first3": ([0, 1, 2], [1, 2]),
    "ins_front2": ([0, 1], [2, 0, 1]),
    "rot_left3": ([0, 1, 2], [1, 2, 0]),
    "rot_right3": ([0, 1, 2], [2, 0, 1]),
    "reverse3": ([0, 1, 2], [2, 1, 0]),
    "rm_mid3": ([0, 1, 2], [0, 2]),
    "replace_first": ([0, 1], [2, 1]),
    "replace_last": ([0, 1], [0, 2]),
    "swap_ends4": ([0, 1, 2, 3], [3, 1, 2, 0]),
    "rm_last3": ([0, 1, 2], [0, 1]),
    "ins_end": ([0, 1], [0, 1, 2]),
    "ins_mid": ([0, 2], [0, 1, 2]),
    "swap_mid4": ([0, 1, 2, 3], [0, 2, 1, 3]),
    "rm_two4": ([0, 1, 2, 3], [2, 3]),
}
WHY = {
    "swap2": "the two children trade places",
    "rm_first2": "the first child is removed",
    "rm_first3": "the first child is removed",
    "ins_front2": "a new child is added in front",
    "rot_left3": "the first child moves to the end",
    "rot_right3": "the last child moves to the front",
    "reverse3": "the order is reversed",
    "rm_mid3": "the middle child is removed",
    "replace_first": "the first child is replaced by a different one",
    "replace_last": "the last child is replaced by a different one",
    "swap_ends4": "the first and last children trade places",
    "rm_last3": "the last child is removed",
    "ins_end": "a new child is added at the end",
    "ins_mid": "a new child is added in the middle",
    "swap_mid4": "the two middle children trade places",
    "rm_two4": "the first two children are removed",
}


def _states(keyed: bool, old: list[int], new: list[int], digits: list[int]) -> list[int]:
    tree = Tree()

    def column(labels: list[int]) -> W:
        return W("Column", kids=tuple(ff(digits[i], ("v", digits[i]) if keyed else None) for i in labels))
    tree.pump(column(old))
    tree.pump(column(new))
    return tree.states()


def key_item(rng: random.Random, change: str, keyed: bool):
    old, new = CHANGES[change]
    digits = rng.sample(range(1, 10), 4)
    got = _states(keyed, old, new, digits)
    other = _states(not keyed, old, new, digits)
    spots = [i for i in range(len(new)) if got[i] != other[i]] or list(range(len(new)))
    pos = rng.choice(spots)
    answer = got[pos]

    def call(labels: list[int]) -> str:
        return "[" + ", ".join(f"n({digits[i]})" for i in labels) + "]"
    row = rng.choice(("Column", "Row"))
    key = "key: Key('$v'), " if keyed else ""
    code = ("var f = false;\nWidget n(int v) {\n  return " + FIELD_BODY % (key, "v") + ";\n}\n"
            f"{row}(children: f ? {call(new)} : {call(old)})")
    if keyed:
        why = (f"{WHY[change].capitalize()}. Each child has a key, so its State follows the key: "
               f"the {ORD[pos]} child ends up showing {answer}.")
    else:
        why = (f"{WHY[change].capitalize()}. With no keys the States stay where they were by position "
               f"(a new child past the old end gets a new State), so the {ORD[pos]} text is {answer}.")
    check = "f = true;\n" + REBUILD + f"return {ALL_TEXTS}.elementAt({pos}).data;"
    return item(f"{ORD[pos]} text after f = true?", code, answer, why, check)


# ── State Survives ──────────────────────────────────────────────────────

def _kept(before: W, after: W, flips: tuple[bool, ...]) -> bool:
    tree = Tree()
    tree.pump(before)
    for flag in flips:
        tree.pump(after if flag else before)
    return tree.states()[0] == 1


def _wrap(t: str, kid: W, key: tuple | None = None, arg: str = "", argv: str = "") -> W:
    return W(t, key=key, kids=(kid,), arg=arg, argv=argv)


def survive_item(why_kept: str, why_reset: str, before: W, after: W, flips: tuple[bool, ...] = (True,),
                 globalkey: bool = False):
    kept = _kept(before, after, flips)
    used_key = [False]

    def leaf(w: W, key_txt: str) -> str:
        if not key_txt:
            return "x()"
        used_key[0] = True
        return f"x({key_txt})"
    root = merged(before, after, leaf)
    head = "var f = false, n = 0;" + (" var g = GlobalKey();" if globalkey else "")
    param = "[k]" if used_key[0] else ""
    key = "key: k, " if used_key[0] else ""
    code = f"{head}\nWidget x({param}) {{\n  return {FIELD_BODY % (key, '++n')};\n}}\n{root}"
    when = "f = true" if flips == (True,) else "f = true, then false"
    check = _flip(*flips) + f"return {ALL_TEXTS}.first.data == '1' ? 'kept' : 'reset';"
    return item(f"after {when}?", code, "kept" if kept else "reset", why_kept if kept else why_reset, check)


PAD = "padding: EdgeInsets.all({})"


def _s(kind: str, rng: random.Random):
    a, b = rng.sample((4, 8, 12, 16), 2)
    k1, k2 = rng.sample("abcde", 2)

    def pad(kid: W, v: int, key: tuple | None = None) -> W:
        return _wrap("Padding", kid, key=key, arg=PAD, argv=str(v))
    if kind == "padding_changes":
        return survive_item("Only the padding value changed: same type, same position, so the same State is kept.", "",
                            pad(ff(), a), pad(ff(), b))
    if kind == "col_row":
        return survive_item("", "Column and Row are different widget types, so the child under them gets a new State.",
                            W("Column", kids=(ff(),)), W("Row", kids=(ff(),)))
    if kind == "center_align":
        return survive_item("", "Center and Align are different types, even though one is built on the other: the State is reset.",
                            _wrap("Center", ff()), _wrap("Align", ff()))
    if kind == "wrapped":
        return survive_item("", "A Padding appeared around it, so the child now sits under a different widget type: new State.",
                            ff(), pad(ff(), a))
    if kind == "unwrapped":
        return survive_item("", "The Padding around it is gone, so the widget at that spot has a different type: new State.",
                            pad(ff(), a), ff())
    if kind == "key_changes":
        return survive_item("", f"The key changed from '{k1}' to '{k2}', so Flutter treats it as a different widget: new State.",
                            ff(key=("v", k1)), ff(key=("v", k2)))
    if kind == "key_same":
        return survive_item("The key is the same ValueKey, so the State is kept.", "",
                            pad(ff(key=("v", k1)), a), pad(ff(key=("v", k1)), b))
    if kind == "key_other_parent":
        return survive_item("", "A plain key only matches among siblings: with a different parent type the State is not carried over.",
                            _wrap("Center", ff(key=("v", k1))), _wrap("Align", ff(key=("v", k1))))
    if kind == "unique":
        return survive_item("", "UniqueKey() makes a brand new key at every build, so the old State never matches: reset.",
                            pad(ff(key=("u",)), a), pad(ff(key=("u",)), b))
    if kind == "global_parent":
        return survive_item("A GlobalKey carries the State to the new parent in the same frame: kept.", "",
                            _wrap("Center", ff(key=("g", "g"))), _wrap("Align", ff(key=("g", "g"))), globalkey=True)
    if kind == "global_col_row":
        return survive_item("A GlobalKey carries the State across Column and Row: kept.", "",
                            W("Column", kids=(ff(key=("g", "g")),)), W("Row", kids=(ff(key=("g", "g")),)), globalkey=True)
    if kind == "offstage":
        return survive_item("Offstage hides the child but keeps it in the tree, with its State.", "",
                            _wrap("Offstage", ff(), arg="offstage: f"), _wrap("Offstage", ff(), arg="offstage: f"))
    if kind == "offstage_twice":
        return survive_item("Offstage keeps the child (and its State) while it is hidden and when it comes back.", "",
                            _wrap("Offstage", ff(), arg="offstage: f"), _wrap("Offstage", ff(), arg="offstage: f"), flips=(True, False))
    if kind == "indexed_stack":
        return survive_item("An IndexedStack keeps every child alive and only shows one: the State is kept.", "",
                            W("IndexedStack", kids=(ff(), W("SizedBox")), arg="index: f ? 1 : 0"),
                            W("IndexedStack", kids=(ff(), W("SizedBox")), arg="index: f ? 1 : 0"), flips=(True, False))
    if kind == "removed_back":
        return survive_item("", "While f was true the widget left the tree and its State was disposed; the new one starts fresh.",
                            ff(), W("SizedBox"), flips=(True, False))
    if kind == "removed_back_key":
        return survive_item("", "A key does not save a widget that left the tree: its State was disposed, and the new one starts fresh.",
                            ff(key=("v", k1)), W("SizedBox"), flips=(True, False))
    if kind == "parent_key_changes":
        return survive_item("", "The key on the Padding changed, so the Padding is a new element and everything under it is new: reset.",
                            pad(ff(), a, ("v", k1)), pad(ff(), a, ("v", k2)))
    if kind == "parent_key_same":
        return survive_item("The Padding has the same key and type, so it is updated in place, and so is the child: kept.", "",
                            pad(ff(), a, ("v", k1)), pad(ff(), b, ("v", k1)))
    if kind == "color":
        return survive_item("Only the color changed: same Container, same child, same State.", "",
                            _wrap("Container", ff(), arg="color: {}", argv="Colors.red"), _wrap("Container", ff(), arg="color: {}", argv="Colors.blue"))
    if kind == "opacity":
        return survive_item("Opacity only changes how it paints: the child and its State are kept.", "",
                            _wrap("Opacity", ff(), arg="opacity: {}", argv="1"), _wrap("Opacity", ff(), arg="opacity: {}", argv="0"))
    if kind == "sizedbox":
        return survive_item("Same SizedBox type, only the width changed: the State is kept.", "",
                            _wrap("SizedBox", ff(), arg="width: {}", argv="20"), _wrap("SizedBox", ff(), arg="width: {}", argv="10"))
    if kind == "expanded":
        return survive_item("", "Expanded is a widget of its own, so the child now sits under a different type: new State.",
                            W("Row", kids=(ff(),)), W("Row", kids=(_wrap("Expanded", ff()),)))
    if kind == "deep":
        return survive_item("", "Two levels down a Column became a Row: that spot has a new type, so everything under it is new.",
                            _wrap("Align", _wrap("Center", W("Column", kids=(ff(),)))), _wrap("Align", _wrap("Center", W("Row", kids=(ff(),)))))
    if kind == "swap_box":
        return survive_item("", "At each position the type is different (FormField vs SizedBox) and there is no key, so nothing matches: reset.",
                            W("Column", kids=(ff(), W("SizedBox"))), W("Column", kids=(W("SizedBox"), ff())))
    if kind == "swap_box_key":
        return survive_item("The key finds the child again among its siblings, wherever it moved: kept.", "",
                            W("Column", kids=(ff(key=("v", k1)), W("SizedBox"))), W("Column", kids=(W("SizedBox"), ff(key=("v", k1)))))
    if kind == "insert_front_one":
        return survive_item("Matching from the bottom finds the same type at the same end of the list, so the State is kept.", "",
                            W("Column", kids=(ff(),)), W("Column", kids=(W("SizedBox"), ff())))
    if kind == "append":
        return survive_item("The first child still matches the first old child, so the State is kept.", "",
                            W("Column", kids=(ff(),)), W("Column", kids=(ff(), W("SizedBox"))))
    if kind == "wrapper_swap":
        w1, w2 = rng.sample(("Container", "Align", "Center", "Padding"), 2)

        def make(t: str) -> W:
            return pad(ff(), a) if t == "Padding" else _wrap(t, ff())
        return survive_item("", f"{w1} and {w2} are different widget types, so the child's State starts over.", make(w1), make(w2))
    raise AssertionError(kind)


SURVIVE_KINDS = (
    "padding_changes", "col_row", "center_align", "wrapped", "unwrapped", "key_changes", "key_same", "key_other_parent", "unique",
    "global_parent", "global_col_row", "offstage", "offstage_twice", "indexed_stack", "removed_back", "removed_back_key",
    "parent_key_changes", "parent_key_same", "color", "opacity", "sizedbox", "expanded", "deep", "swap_box", "swap_box_key",
    "insert_front_one", "append", "wrapper_swap",
)


def _survive(rng: random.Random, kind: str):
    return _s(kind, rng)


KEY_TEMPLATES: tuple[Maker, ...] = tuple(
    template(f"{change}_{'keyed' if keyed else 'plain'}", key_item, change, keyed)
    for change in CHANGES for keyed in (False, True) if not (keyed and change in ("swap_ends4", "swap_mid4")))
SURVIVE_TEMPLATES: tuple[Maker, ...] = tuple(template(kind, _survive, kind) for kind in SURVIVE_KINDS)
