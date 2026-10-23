"""Flutter widgets pack, activity 1: Widget Count.

How many widgets does a finder match in a small tree? The answer is counted by hand from what the tree builds:
`Text`/`Icon` and the containers you write, the hidden widgets that `Container`, `Card`, `Spacer`, `Icon` and `Scaffold`
build for you, the collection syntax (`for`, `if`, `...`, `map`), what `Visibility`/`Offstage`/`IndexedStack` take out of
sight (`find.byType` skips offstage widgets unless it says `skipOffstage: false`), and what a scroll view keeps.
"""

from __future__ import annotations

import operator
import random

from ._flutterwidgets_kit import G, center, col, icon, mk, pad, q, row, template, text, walk_names

TEMPLATES: list = []

LETTERS = "abcdefgh"
ICONS = ("add", "home", "star", "edit", "delete", "search", "menu", "check")


def leaf(rng: random.Random, kind: str | None = None) -> G:
    kind = kind or rng.choice("TI")
    return text(rng.choice(LETTERS)) if kind == "T" else icon(rng.choice(ICONS))


def tally(widget, name: str) -> int:
    return list(walk_names(widget)).count(name)


def by_type(name: str, off: bool = False) -> str:
    return f"find.byType({name}{', skipOffstage: false' if off else ''})"


def ask(finder: str) -> str:
    return f"{finder} matches how many?"


def count_of(finder: str) -> str:
    return f"count({finder})"


# ── plain trees ─────────────────────────────────────────────────────────

@template(TEMPLATES)
def row_mix(rng):
    kids = [leaf(rng) for _ in range(rng.randint(4, 6))]
    w = rng.choice((row, col))(*kids)
    t = rng.choice(("Text", "Icon"))
    n = tally(w, t)
    return mk(ask(by_type(t)), w, n, f"The {w.name} has {len(kids)} children and {n} of them are {t} widgets, so the "
              f"finder matches {n}.", count_of(by_type(t)))


@template(TEMPLATES)
def nested_rows(rng):
    inner = row(*[leaf(rng) for _ in range(rng.randint(2, 3))])
    kids = [leaf(rng), inner, leaf(rng)]
    if rng.random() < 0.5:
        kids.append(row(leaf(rng), leaf(rng)))
    w = col(*kids)
    t = rng.choice(("Text", "Icon", "Row", "Text", "Icon"))
    n = tally(w, t)
    return mk(ask(by_type(t)), w, n, f"The finder looks at the whole tree, children of children included: {n} {t} "
              f"widgets.", count_of(by_type(t)))


@template(TEMPLATES)
def wrapper_chain(rng):
    layers = [rng.choice(("Padding", "Center")) for _ in range(rng.randint(3, 5))]
    w: G = text(rng.choice(LETTERS))
    for kind in layers:
        w = pad(w) if kind == "Padding" else center(w)
    t = rng.choice(("Padding", "Center"))
    n = layers.count(t)
    return mk(ask(by_type(t)), w, n, f"Each wrapper is one widget in the chain: {n} of them are {t}.", count_of(by_type(t)))


@template(TEMPLATES)
def nested_loops(rng):
    rows = [[rng.randint(1, 9) for _ in range(rng.randint(1, 3))] for _ in range(rng.randint(2, 3))]
    lists = ", ".join("[" + ", ".join(map(str, r)) + "]" for r in rows)
    w = col(f"for (final r in [{lists}]) Row(children: [for (final x in r) Text('$x')])")
    t = rng.choice(("Row", "Text", "Text"))
    n = len(rows) if t == "Row" else sum(len(r) for r in rows)
    return mk(ask(by_type(t)), w, n, f"The outer loop makes one Row per inner list ({len(rows)}) and the inner loop one Text "
              f"per number ({sum(len(r) for r in rows)}).", count_of(by_type(t)))


# ── widgets that build other widgets ────────────────────────────────────

#: (props of a Container, the hidden widgets it builds) - Container.build wraps the child in Align, Padding (padding),
#: ColoredBox (color), DecoratedBox (decoration), ConstrainedBox (width/height/constraints), Padding (margin).
CONTAINERS = [
    (dict(padding="EdgeInsets.all(8)"), {"Padding": 1}),
    (dict(margin="EdgeInsets.all(8)"), {"Padding": 1}),
    (dict(margin="EdgeInsets.all(4)", padding="EdgeInsets.all(8)"), {"Padding": 2}),
    (dict(color="Colors.red"), {"ColoredBox": 1}),
    (dict(decoration="BoxDecoration(color: Colors.red)"), {"DecoratedBox": 1}),
    (dict(width="40"), {"ConstrainedBox": 1}),
    (dict(width="40", height="40"), {"ConstrainedBox": 1}),
    (dict(height="30"), {"ConstrainedBox": 1}),
    (dict(alignment="Alignment.center"), {"Align": 1}),
    (dict(width="40", color="Colors.red"), {"ConstrainedBox": 1, "ColoredBox": 1}),
    (dict(padding="EdgeInsets.all(8)", color="Colors.red"), {"Padding": 1, "ColoredBox": 1}),
    (dict(padding="EdgeInsets.all(8)", decoration="BoxDecoration(color: Colors.red)"), {"Padding": 1, "DecoratedBox": 1}),
    (dict(alignment="Alignment.center", padding="EdgeInsets.all(8)"), {"Align": 1, "Padding": 1}),
]
HIDDEN = ("Padding", "ColoredBox", "DecoratedBox", "ConstrainedBox", "Align")
WHY_HIDDEN = {
    "Padding": "padding and margin each become a Padding",
    "ColoredBox": "color becomes a ColoredBox",
    "DecoratedBox": "decoration becomes a DecoratedBox",
    "ConstrainedBox": "width, height or constraints become one ConstrainedBox",
    "Align": "alignment becomes an Align",
}


@template(TEMPLATES)
def container_siblings(rng):
    t = rng.choice(HIDDEN)
    picks = rng.sample([c for c in CONTAINERS if t in c[1]], 1) + rng.sample(CONTAINERS, 1)
    rng.shuffle(picks)
    kids = [G("Container", **props, child=text(rng.choice(LETTERS))) for props, _ in picks]
    n = sum(h.get(t, 0) for _, h in picks)
    w = row(*kids)
    return mk(ask(by_type(t)), w, n, f"Container is only a recipe: {WHY_HIDDEN[t]}, so the two Containers build {n} "
              f"{t} in all.", count_of(by_type(t)))


@template(TEMPLATES)
def container_nested(rng):
    picks = [rng.choice(CONTAINERS) for _ in range(rng.randint(2, 3))]
    t = rng.choice(("Container",) + HIDDEN[:4])
    w: G = text(rng.choice(LETTERS))
    for props, _ in reversed(picks):
        w = G("Container", **props, child=w)
    n = len(picks) if t == "Container" else sum(h.get(t, 0) for _, h in picks)
    why = ("each Container written is one Container" if t == "Container" else f"{WHY_HIDDEN[t]}")
    return mk(ask(by_type(t)), w, n, f"{why[0].upper() + why[1:]}; the chain gives {n}.", count_of(by_type(t)))


@template(TEMPLATES)
def card_and_padding(rng):
    k, m = rng.randint(1, 3), rng.randint(0, 2)
    kids = [G("Card", child=text(rng.choice(LETTERS))) for _ in range(k)] + [pad(text(rng.choice(LETTERS))) for _ in range(m)]
    kids = [kids[i] for i in rng.sample(range(len(kids)), len(kids))]
    w = G("Material", child=col(*kids))
    n = k + m
    return mk(ask(by_type("Padding")), w, n, f"A Card builds its margin as a Padding ({k}), and {m} Padding written out: {n}.",
              count_of(by_type("Padding")))


@template(TEMPLATES)
def icon_inside(rng):
    # An Icon builds a SizedBox holding a RichText; a Text builds a RichText; Spacer is an Expanded around a SizedBox.shrink.
    icons, texts, boxes, spacers = rng.randint(1, 3), rng.randint(0, 2), rng.randint(0, 2), rng.randint(0, 2)
    kids: list = [icon(rng.choice(ICONS)) for _ in range(icons)] + [text(rng.choice(LETTERS)) for _ in range(texts)]
    kids += [G("SizedBox", width="8") for _ in range(boxes)] + [G("Spacer") for _ in range(spacers)]
    kids = [kids[i] for i in rng.sample(range(len(kids)), len(kids))]
    w = row(*kids)
    t = rng.choice(("SizedBox", "SizedBox", "RichText"))
    if t == "SizedBox":
        n, why = icons + boxes + spacers, (f"Each Icon ({icons}) builds a SizedBox, each Spacer ({spacers}) builds a SizedBox.shrink, "
                                           f"and {boxes} are written out")
    else:
        n, why = icons + texts, f"Text builds a RichText ({texts}) and so does Icon ({icons})"
    return mk(ask(by_type(t)), w, n, f"{why}: {n}.", count_of(by_type(t)))


@template(TEMPLATES)
def spacer_is_expanded(rng):
    kinds = [rng.choice(("Expanded", "Flexible", "Spacer", "Spacer")) for _ in range(rng.randint(3, 5))]
    kids = []
    for k in kinds:
        if k == "Spacer":
            kids.append(G("Spacer", flex=str(rng.randint(1, 2))) if rng.random() < 0.3 else G("Spacer"))
        else:
            kids.append(G(k, child=text(rng.choice(LETTERS))))
    t = rng.choice(("Expanded", "Flexible", "Spacer"))
    n = kinds.count("Expanded") + kinds.count("Spacer") if t == "Expanded" else kinds.count(t)
    why = ("Spacer is an Expanded with an empty box inside, so it counts as an Expanded too" if t == "Expanded"
           else f"find.byType matches the exact class {t} only: Expanded is a different class from Flexible" if t == "Flexible"
           else "Spacer is its own widget")
    return mk(ask(by_type(t)), row(*kids), n, f"{why}: {n}.", count_of(by_type(t)))


@template(TEMPLATES)
def scaffold_parts(rng):
    drawer, end = rng.random() < 0.6, rng.random() < 0.3
    lead = rng.choice(("none", "none", "icon", "no_imply"))
    acts = rng.random() < 0.3
    fab = rng.random() < 0.5
    bar_kw: dict = {}
    n_icons = 0
    if lead == "icon":
        bar_kw["leading"] = icon("menu")
        n_icons += 1
    elif lead == "no_imply":
        bar_kw["automaticallyImplyLeading"] = "false"
    elif drawer:
        n_icons += 1  # the DrawerButton
    if acts:
        bar_kw["actions"] = [icon("search")]
        n_icons += 1
    elif end:
        n_icons += 1  # the EndDrawerButton
    bar_kw["title"] = text("t")
    kw: dict = {"appBar": G("AppBar", **bar_kw)}
    if drawer:
        kw["drawer"] = G("Drawer")
    if end:
        kw["endDrawer"] = G("Drawer")
    kw["body"] = text("b")
    if fab:
        kw["floatingActionButton"] = G("FloatingActionButton", onPressed="null", child=icon("add"))
        n_icons += 1
    w = G("MaterialApp", home=G("Scaffold", **kw))
    return mk(ask(by_type("Icon")), w, n_icons,
              "An AppBar adds a menu button for a drawer (leading) and for an endDrawer (actions) unless you give "
              f"that slot yourself or switch it off. All Icons: {n_icons}.", count_of(by_type("Icon")))


@template(TEMPLATES)
def listtile_slots(rng):
    tiles = []
    nt = ni = 0
    for _ in range(rng.randint(2, 3)):
        slots: dict = {}
        if rng.random() < 0.6:
            slots["leading"] = icon(rng.choice(ICONS))
            ni += 1
        slots["title"] = text(rng.choice(LETTERS))
        nt += 1
        if rng.random() < 0.5:
            slots["subtitle"] = text(rng.choice(LETTERS))
            nt += 1
        if rng.random() < 0.3:
            slots["trailing"] = icon(rng.choice(ICONS))
            ni += 1
        tiles.append(G("ListTile", **slots))
    w = G("Material", child=col(*tiles))
    t = rng.choice(("Text", "Icon", "ListTile"))
    n = {"Text": nt, "Icon": ni, "ListTile": len(tiles)}[t]
    return mk(ask(by_type(t)), w, n, f"Only the slots that are filled build anything: {n} {t}.", count_of(by_type(t)))


# ── collection syntax ───────────────────────────────────────────────────

@template(TEMPLATES)
def for_loop(rng):
    n = rng.randint(3, 8)
    k = rng.randint(1, n - 2)
    cond, keep = rng.choice([
        ("", lambda i: True), ("if (i.isEven) ", lambda i: i % 2 == 0), ("if (i.isOdd) ", lambda i: i % 2 == 1),
        (f"if (i > {k}) ", lambda i: i > k), (f"if (i < {k}) ", lambda i: i < k), ("if (i % 3 == 0) ", lambda i: i % 3 == 0)])
    leaf_code, t = rng.choice((("Text('$i')", "Text"), ("Icon(Icons.star)", "Icon")))
    w = rng.choice((row, col))(f"for (var i = 0; i < {n}; i++) {cond}{leaf_code}")
    got = sum(1 for i in range(n) if keep(i))
    return mk(ask(by_type(t)), w, got, f"The loop runs i = 0 to {n - 1}; {'every' if not cond else 'the ones passing the if'} "
              f"make a {t}: {got}.", count_of(by_type(t)))


@template(TEMPLATES)
def for_in(rng):
    words = rng.sample(["a", "bb", "c", "dd", "e", "fff", "gg"], rng.randint(3, 5))
    cond, keep = rng.choice([("", lambda s: True), ("if (s.length > 1) ", lambda s: len(s) > 1),
                             ("if (s.length == 1) ", lambda s: len(s) == 1), ("if (s != 'a') ", lambda s: s != "a")])
    lst = "[" + ", ".join(q(s) for s in words) + "]"
    w = col(f"for (final s in {lst}) {cond}Text(s)")
    got = sum(1 for s in words if keep(s))
    return mk(ask(by_type("Text")), w, got, f"One Text per word that passes the test: {got} of {len(words)}.", count_of(by_type("Text")))


@template(TEMPLATES)
def spread_generate(rng):
    n = rng.randint(2, 5)
    form = rng.choice(("generate", "filled"))
    lead = rng.randint(0, 2)
    t = rng.choice(("Text", "Icon"))
    if form == "generate":
        spread = f"...List.generate({n}, (i) => Icon(Icons.star))"
    else:
        spread = f"...List.filled({n}, Icon(Icons.star))"
    kids: list = [text(rng.choice(LETTERS)) for _ in range(lead)] + [spread]
    w = col(*kids)
    got = n if t == "Icon" else lead
    return mk(ask(by_type(t)), w, got, f"The spread adds {n} Icons to the list; the {lead} written Texts are all the Text there is: "
              f"{t} = {got}.", count_of(by_type(t)))


@template(TEMPLATES)
def map_to_list(rng):
    words = rng.sample(["a", "bb", "c", "dd", "e", "fff", "gg"], rng.randint(3, 5))
    where, keep = rng.choice([("", lambda s: True), (".where((s) => s.length > 1)", lambda s: len(s) > 1),
                              (".where((s) => s.length < 2)", lambda s: len(s) < 2)])
    lst = "[" + ", ".join(q(s) for s in words) + "]"
    lead = rng.random() < 0.5
    got = sum(1 for s in words if keep(s))
    if lead:
        w = col(icon("add"), f"...{lst}{where}.map((s) => Text(s))")
    else:
        w = col(f"...{lst}{where}.map((s) => Text(s))")
    return mk(ask(by_type("Text")), w, got, f"map makes a Text for each word that survives the filter: {got}.", count_of(by_type("Text")))


@template(TEMPLATES)
def collection_if(rng):
    ops = {">": operator.gt, "<": operator.lt, "==": operator.eq, "!=": operator.ne}
    items: list = [leaf(rng, "T")]
    n_text = 1
    n_icon = 0
    for _ in range(rng.randint(2, 3)):
        a, b = rng.randint(1, 5), rng.randint(1, 5)
        op = rng.choice(list(ops))
        holds = ops[op](a, b)
        kind = rng.choice("TI")
        w = leaf(rng, kind)
        if rng.random() < 0.35:  # if ... else ...
            other = leaf(rng, "I" if kind == "T" else "T")
            items.append(f"if ({a} {op} {b}) {_flat(w)} else {_flat(other)}")
            shown = w if holds else other
        else:
            items.append(f"if ({a} {op} {b}) {_flat(w)}")
            shown = w if holds else None
        if shown is not None:
            if shown.name == "Text":
                n_text += 1
            else:
                n_icon += 1
    t = rng.choice(("Text", "Icon"))
    n = n_text if t == "Text" else n_icon
    return mk(ask(by_type(t)), col(*items), n, f"An if in a list adds its widget only when the condition holds (else branch "
              f"otherwise): {n} {t}.", count_of(by_type(t)))


def _flat(w) -> str:
    from ._flutter_model import render
    return render(w, width=500)


@template(TEMPLATES)
def ternary_children(rng):
    n_text = 0
    n_icon = 0
    items: list = []
    for _ in range(rng.randint(2, 3)):
        a, b = rng.randint(1, 9), rng.randint(1, 9)
        op = rng.choice((">", "<"))
        holds = (a > b) if op == ">" else (a < b)
        first, second = (leaf(rng, "T"), leaf(rng, "I")) if rng.random() < 0.5 else (leaf(rng, "I"), leaf(rng, "T"))
        items.append(f"{a} {op} {b} ? {_flat(first)} : {_flat(second)}")
        shown = first if holds else second
        if shown.name == "Text":
            n_text += 1
        else:
            n_icon += 1
    t = rng.choice(("Text", "Icon"))
    n = n_text if t == "Text" else n_icon
    return mk(ask(by_type(t)), col(*items), n, f"Each ternary picks exactly one of its two widgets: {n} {t}.", count_of(by_type(t)))


# ── out of sight, still in the tree? ────────────────────────────────────

@template(TEMPLATES)
def visibility_and_friends(rng):
    # (code, found by default, found with skipOffstage: false)
    hidden = rng.random() < 0.7
    v = "false" if hidden else "true"
    opts = [
        (lambda c: G("Visibility", visible=v, child=c), 0 if hidden else 1, 0 if hidden else 1,
         "Visibility swaps its child for an empty box when invisible (maintainState is false)"),
        (lambda c: G("Visibility", visible=v, maintainState="true", child=c), 0 if hidden else 1, 1,
         "maintainState keeps the child alive but offstage, and find.byType skips offstage widgets by default"),
        (lambda c: G("Visibility.maintain", visible=v, child=c), 1, 1,
         "Visibility.maintain keeps the child in place, just not painted: it is not offstage"),
        (lambda c: G("Offstage", offstage="true" if hidden else "false", child=c), 0 if hidden else 1, 1,
         "Offstage keeps its child in the tree but find.byType skips what is offstage by default"),
        (lambda c: G("Opacity", opacity="0" if hidden else "1", child=c), 1, 1,
         "Opacity only changes how it is painted; the child is always in the tree"),
        (lambda c: G("SizedBox.shrink", child=c), 1, 1, "SizedBox.shrink still builds its child"),
    ]
    picks = rng.sample(opts, 2)
    off = rng.random() < 0.5
    kids = [p[0](text(rng.choice(LETTERS))) for p in picks]
    if rng.random() < 0.5:
        kids.append(text(rng.choice(LETTERS)))
    plain = 1 if len(kids) == 3 else 0
    n = sum(p[2] if off else p[1] for p in picks) + plain
    reasons = "; ".join(p[3] for p in picks)
    return mk(ask(by_type("Text", off)), col(*kids), n, f"{reasons[0].upper() + reasons[1:]}. Total {n}.", count_of(by_type("Text", off)))


@template(TEMPLATES)
def indexed_stack(rng):
    n = rng.randint(3, 4)
    idx = rng.randint(0, n - 1)
    letters = rng.sample(LETTERS, n)
    w = G("IndexedStack", index=str(idx), children=[text(c) for c in letters])
    mode = rng.choice(("type", "type_off", "text", "text_off"))
    if mode == "type":
        finder, got, why = by_type("Text"), 1, "Only the child at index is onstage; the others are offstage and skipped"
    elif mode == "type_off":
        finder, got, why = by_type("Text", True), n, "skipOffstage: false also matches the hidden children, and IndexedStack builds all of them"
    else:
        c = rng.choice(letters)
        off = mode == "text_off"
        finder = f"find.text({q(c)}{', skipOffstage: false' if off else ''})"
        got = 1 if (off or letters.index(c) == idx) else 0
        why = (f"{c} is child {letters.index(c)} and index is {idx}" +
               (": hidden, but skipOffstage: false still finds it" if off and letters.index(c) != idx else
                ": it is the shown one" if letters.index(c) == idx else ": hidden, so the default finder skips it"))
    return mk(ask(finder), w, got, f"{why}: {got}.", count_of(finder))


@template(TEMPLATES)
def stack_positioned(rng):
    kids = []
    kinds = [rng.choice(("pos_t", "pos_i", "plain_t")) for _ in range(rng.randint(3, 4))]
    for k in kinds:
        if k == "pos_t":
            kids.append(G("Positioned", **{rng.choice(("left", "top")): str(rng.choice((0, 20, 40)))}, child=text(rng.choice(LETTERS))))
        elif k == "pos_i":
            kids.append(G("Positioned", **{rng.choice(("right", "bottom")): "0"}, child=icon(rng.choice(ICONS))))
        else:
            kids.append(text(rng.choice(LETTERS)))
    w = G("Stack", children=kids)
    t = rng.choice(("Positioned", "Text", "Icon"))
    n = {"Positioned": sum(1 for k in kinds if k.startswith("pos")), "Text": sum(1 for k in kinds if k.endswith("_t")),
         "Icon": kinds.count("pos_i")}[t]
    return mk(ask(by_type(t)), w, n, f"Every child of a Stack is in the tree, covered or not: {n} {t}.", count_of(by_type(t)))


@template(TEMPLATES)
def scroll_view_keeps_all(rng):
    n = rng.randint(15, 40)
    w = G("SingleChildScrollView", child=col(f"for (var i = 0; i < {n}; i++) Text('$i')"))
    mode = rng.choice(("count", "last"))
    if mode == "count":
        finder, got = by_type("Text"), n
    else:
        finder, got = f"find.text('{n - 1}')", 1
    return mk(ask(finder), w, got, "SingleChildScrollView builds its whole child, however far it scrolls: all "
              f"{n} Texts exist and are found.", count_of(finder))


# ── your own widgets, and finders that look around ─────────────────────

@template(TEMPLATES)
def own_widget(rng):
    name = rng.choice(("Tag", "Cell", "Pair", "Slot", "Mark"))
    body_kind = rng.choice(("row_tt", "col_ti", "pad_t", "row_ti"))
    body = {"row_tt": row(text("a"), text("b")), "col_ti": col(text("a"), icon("add"), text("b")),
            "pad_t": pad(text("a")), "row_ti": row(text("a"), icon("add"))}[body_kind]
    k = rng.randint(2, 4)
    extra = rng.random() < 0.4
    kids: list = [G(name) for _ in range(k)] + ([text("z")] if extra else [])
    outer = col(*kids)
    flat_body = _flat(body)
    decl = (f"class {name} extends StatelessWidget {{\n  @override\n  Widget build(BuildContext c) =>\n      {flat_body};\n}}")
    t = rng.choice((name, "Text", "Icon", body.name))
    n = tally(body, t) * k + tally(outer, t)
    return mk(ask(by_type(t)), outer, n, f"Each {name} builds its own {body.name} with {tally(body, 'Text')} Text and {tally(body, 'Icon')} "
              f"Icon, and the tree has {k} of them" + (", plus the lone Text" if extra and t == "Text" else "") + f": {n}.",
              count_of(by_type(t)), decls=decl)


@template(TEMPLATES)
def layout_builder_root(rng):
    dim = rng.choice(("maxWidth", "maxHeight"))
    real = 400 if dim == "maxWidth" else 300
    t = rng.choice((150, 250, 350, 450) if dim == "maxWidth" else (100, 200, 250, 350))
    big, small = rng.randint(2, 4), rng.randint(1, 2)
    w = G("LayoutBuilder", builder=f"(c, bc) => bc.{dim} > {t} ? {_flat(row(*[text(LETTERS[i]) for i in range(big)]))} : "
                                   f"{_flat(row(*[text(LETTERS[i]) for i in range(small)]))}")
    got = big if real > t else small
    return mk(ask(by_type("Text")), w, got, f"The screen gives its root exactly 400 x 300, so {dim} is {real}; {real} > {t} is "
              f"{'true' if real > t else 'false'}, so the {'first' if real > t else 'second'} branch with {got} Texts is built.",
              count_of(by_type("Text")))


@template(TEMPLATES)
def layout_builder_sized(rng):
    dim = rng.choice(("width", "height"))
    size = rng.choice((100, 200, 300))
    t = rng.choice((150, 250))
    big, small = rng.randint(2, 4), rng.randint(1, 2)
    attr = "maxWidth" if dim == "width" else "maxHeight"
    lb = G("LayoutBuilder", builder=f"(c, bc) => bc.{attr} > {t} ? {_flat(row(*[text(LETTERS[i]) for i in range(big)]))} : "
                                    f"{_flat(row(*[text(LETTERS[i]) for i in range(small)]))}")
    w = center(G("SizedBox", **{dim: str(size)}, child=lb))
    got = big if size > t else small
    return mk(ask(by_type("Text")), w, got, f"Center lets the SizedBox be {size} {dim}, so the LayoutBuilder sees {attr} = {size} "
              f"(not the screen's); {size} > {t} is {'true' if size > t else 'false'}: {got} Texts.", count_of(by_type("Text")))


@template(TEMPLATES)
def media_query_branch(rng):
    exprs = [("size.width", 400), ("size.height", 300), ("size.shortestSide", 300), ("size.longestSide", 400),
             ("size.width / 2", 200)]
    e, real = rng.choice(exprs)
    t = rng.choice((100, 250, 350, 450))
    if real == t:
        t += 1
    big, small = rng.randint(2, 4), rng.randint(1, 2)
    branch = (f"{_flat(row(*[text(LETTERS[i]) for i in range(big)]))} : {_flat(row(*[text(LETTERS[i]) for i in range(small)]))}")
    w = G("MaterialApp", home=G("Builder", builder=f"(c) => MediaQuery.of(c).{e} > {t} ? {branch}"))
    got = big if real > t else small
    return mk(ask(by_type("Text")), w, got, f"The test screen is 400 x 300 logical pixels, so {e} is {real}; {real} > {t} is "
              f"{'true' if real > t else 'false'}: {got} Texts.", count_of(by_type("Text")))


@template(TEMPLATES)
def find_text_exact(rng):
    pool = ["a", "ab", "b", "ba", "abc", "bc"]
    words = [rng.choice(pool) for _ in range(rng.randint(5, 6))]
    target = rng.choice(["a", "b", "ab"])
    contains = rng.random() < 0.5
    finder = f"find.{'textContaining' if contains else 'text'}({q(target)})"
    n = sum(1 for s in words if (target in s if contains else s == target))
    w = col(*[text(s) for s in words])
    return mk(ask(finder), w, n, ("textContaining matches any Text whose string contains it" if contains
                                  else "find.text matches only a Text whose whole string equals it") + f": {n}.", count_of(finder))


@template(TEMPLATES)
def find_icon(rng):
    names = [rng.choice(("add", "home", "star")) for _ in range(rng.randint(4, 6))]
    target = rng.choice(("add", "home", "star"))
    w = row(*[icon(s) for s in names])
    n = names.count(target)
    return mk(ask(f"find.byIcon(Icons.{target})"), w, n, f"All Icon widgets have the type Icon, but byIcon looks at which icon: "
              f"{n} are Icons.{target}.", count_of(f"find.byIcon(Icons.{target})"))


@template(TEMPLATES)
def find_descendant(rng):
    r = row(*[leaf(rng) for _ in range(rng.randint(2, 3))])
    p = pad(leaf(rng))
    kids = [leaf(rng), r, p]
    rng.shuffle(kids)
    w = col(*kids)
    of = rng.choice(("Row", "Padding"))
    t = rng.choice(("Text", "Icon"))
    inside = r if of == "Row" else p
    n = tally(inside, t)
    finder = f"find.descendant(of: find.byType({of}), matching: find.byType({t}))"
    return mk(ask(finder), w, n, f"Only the {t} widgets below the {of} count, not the ones beside it: {n}.", count_of(finder))


@template(TEMPLATES)
def find_ancestor(rng):
    layers = [rng.choice(("Padding", "Center", "Row", "Column")) for _ in range(rng.randint(3, 5))]
    w: G = text("a")
    for kind in layers:
        w = {"Padding": lambda x: pad(x), "Center": lambda x: center(x), "Row": lambda x: row(x, text("b")),
             "Column": lambda x: col(text("b"), x)}[kind](w)
    t = rng.choice(("Padding", "Center", "Row", "Column"))
    n = layers.count(t)
    finder = f"find.ancestor(of: find.text('a'), matching: find.byType({t}))"
    return mk(ask(finder), w, n, f"Ancestors are the widgets above the Text 'a' on its way to the root; {n} of them are {t}.",
              count_of(finder))


@template(TEMPLATES)
def same_key_elsewhere(rng):
    wrappers = [lambda x: pad(x), lambda x: center(x), lambda x: row(x), lambda x: G("SizedBox", child=x)]
    picked = rng.sample(wrappers, rng.randint(3, 4))
    keys = [rng.choice("kj") for _ in picked]
    kids = [wr(text(rng.choice(LETTERS), key=f"Key('{k}')")) for wr, k in zip(picked, keys)]
    target = rng.choice("kj")
    n = keys.count(target)
    return mk(ask(f"find.byKey(Key('{target}'))"), col(*kids), n, f"A key may repeat under different parents; the finder returns "
              f"all of them: {n} carry '{target}'.", count_of(f"find.byKey(Key('{target}'))"))


@template(TEMPLATES)
def rich_text_kinds(rng):
    a, b, c = rng.randint(1, 2), rng.randint(0, 2), rng.randint(0, 2)
    kids = [text(rng.choice(LETTERS)) for _ in range(a)]
    kids += [G("Text.rich", f"TextSpan(text: {q(rng.choice(LETTERS))})") for _ in range(b)]
    kids += [icon(rng.choice(ICONS)) for _ in range(c)]
    kids = [kids[i] for i in rng.sample(range(len(kids)), len(kids))]
    t = rng.choice(("Text", "RichText"))
    n = (a + b) if t == "Text" else (a + b + c)
    why = ("Text and Text.rich are both Text widgets" if t == "Text"
           else "every Text, Text.rich and Icon draws itself with a RichText")
    return mk(ask(by_type(t)), col(*kids), n, f"{why}: {n}.", count_of(by_type(t)))
