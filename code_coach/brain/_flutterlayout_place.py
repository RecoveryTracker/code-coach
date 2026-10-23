"""Flutter layout pack, part 3: Stack Spot, Wrap Lines and Overflow Or Fine.

As in the other parts, every template builds a tree of `_flutter_model.py` nodes; the same tree is printed as the code
the learner reads and laid out by the hand-written rules (RenderStack, RenderWrap, RenderFlex), and
tests/flutter_oracle.py builds it in real Flutter. Wrap Lines asks how many rows a Wrap makes (the check counts the
different tops), Overflow Or Fine asks whether a RenderFlex complains.
"""

from __future__ import annotations

import random

from ._flutter_model import (ALIGNMENTS, AlignN, BoxN, ContainerN, FlexN, Node, PadN, PositionedN, SizedN, StackN,
                             WrapN, Expanded, Flexible, Retry, fit, fnum, host, item, named, render, walk)
from ._model import Maker
from .items import Item

PADS = (10, 20, 30, 40)


def template(name: str, fn, *args) -> Maker:
    def make(rng: random.Random):
        return fn(rng, *args)
    return fit(named(name, make))


def box(id_: str = "a", w: float = 50, h: float = 50) -> BoxN:
    return BoxN(id_, w=w, h=h)


def center(child: Node) -> AlignN:
    return AlignN(0, 0, child, center=True)


def pos(child: Node, **kw) -> PositionedN:
    return PositionedN(child, **kw)


# ── 6. Stack Spot ───────────────────────────────────────────────────────

def _s_positioned(rng: random.Random, edges: str, props: str):
    """Stack([... Positioned(<edges>) ...]): which of left/top/right/bottom/width/height the Positioned names."""
    vals = {e: rng.choice((10, 20, 30, 40, 50, 60)) for e in "ltrb"}
    kw: dict[str, float] = {}
    names = {"l": "left", "t": "top", "r": "right", "b": "bottom", "w": "width", "h": "height"}
    for e in edges:
        kw[names[e]] = vals[e] if e in "ltrb" else rng.choice((60, 80, 100, 120))
    child = box("a", rng.choice((30, 50, 80)), rng.choice((30, 50, 60)))
    kids: list[Node] = [pos(child, **kw)]
    if rng.random() < 0.4:  # a second, plain Positioned as decoy
        kids.insert(0, pos(box("b", 40, 40), left=rng.choice((0, 10)), top=rng.choice((0, 10))))
    return item(StackN(kids), "a", rng.choice(props), ["stack", "tight"])


def _s_alignment(rng: random.Random, props: str, custom: bool):
    if custom:
        ax, ay = rng.choice(((0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (-0.5, -0.5), (0.5, 0), (0, 0.5)))
        root = StackN([box("a", rng.choice((40, 80, 120)), rng.choice((40, 60, 100)))], ax, ay, mark_alignment=True)
    else:
        ax, ay = rng.choice(list(ALIGNMENTS))
        root = StackN([box("a", rng.choice((40, 50, 100)), rng.choice((40, 50, 100)))], ax, ay, mark_alignment=True)
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


def _s_alignment_plus_positioned(rng: random.Random, ask: str):
    """The Stack's alignment moves the plain child but NOT a Positioned one."""
    ax, ay = rng.choice(((1, 1), (0, 0), (1, -1), (-1, 1), (0, 1)))
    plain = box("a", 50, 50)
    placed = pos(box("b", 40, 40), left=rng.choice((10, 20, 30)), top=rng.choice((10, 20, 30)))
    root = StackN([plain, placed], ax, ay, mark_alignment=True)
    return item(root, ask, rng.choice("xy"), ["stack", "tight", "align"])


def _s_half_positioned(rng: random.Random, given: str):
    """Positioned(top: 20) names only one axis: the other still follows the Stack's alignment."""
    ax, ay = rng.choice(((0, 0), (1, 1), (1, 0), (0, 1), (1, -1)))
    kw = {"top": rng.choice((10, 20, 40))} if given == "top" else (
        {"left": rng.choice((10, 20, 40))} if given == "left" else (
            {"bottom": rng.choice((10, 20, 40))} if given == "bottom" else {"right": rng.choice((10, 20, 40))}))
    root = StackN([pos(box("a"), **kw)], ax, ay, mark_alignment=True)
    return item(root, "a", "x" if given in ("top", "bottom") else "y", ["stack", "tight", "align"])


def _s_align_child(rng: random.Random, padded: bool, props: str):
    ax, ay = rng.choice(((1, 1), (-1, 1), (1, -1), (0, 1), (1, 0), (0, -1)))
    inner: Node = box("a")
    if padded:
        p = rng.choice(PADS)
        inner = PadN(p, p, p, p, inner)
    return item(StackN([AlignN(ax, ay, inner)]), "a", rng.choice(props), ["stack", "tight", "align", "pad"])


def _s_in_sized(rng: random.Random, props: str):
    w, h = rng.choice(((200, 100), (240, 160), (300, 200), (160, 120)))
    e = rng.choice((10, 20, 30))
    root = center(SizedN(w, h, StackN([pos(box("a"), right=e, bottom=e)])))
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


def _s_sized_by_child(rng: random.Random, edges: str, props: str):
    """A Stack with a plain child is as big as that child (when the parent lets it): the Positioned one is measured in that."""
    w, h = rng.choice(((200, 100), (240, 120), (100, 100), (160, 80)))
    kw = {("right" if edges == "rb" else "left"): 0, ("bottom" if edges == "rb" else "top"): 0}
    root = center(StackN([box("z", w, h), pos(box("a", 40, 40), **kw)]))
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


def _s_alignment_in_sized_child(rng: random.Random, props: str):
    w, h = rng.choice(((200, 100), (240, 120), (100, 100), (160, 80)))
    ax, ay = rng.choice(((1, 1), (-1, 1), (1, -1), (0, 0), (0, 1)))
    root = center(StackN([box("z", w, h), box("a", 40, 40)], ax, ay, mark_alignment=True))
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


def _s_nested(rng: random.Random, props: str):
    left, top = rng.choice((20, 40, 50)), rng.choice((20, 40, 50))
    w, h = rng.choice(((200, 200), (150, 100), (240, 160)))
    inner = StackN([pos(box("a"), right=10, bottom=10)])
    root = StackN([pos(inner, left=left, top=top, width=w, height=h)])
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


def _s_padded(rng: random.Random, props: str):
    p = rng.choice(PADS)
    root = PadN(p, p, p, p, StackN([pos(box("a"), left=0, top=0), pos(box("b"), right=0, bottom=0)]))
    return item(root, rng.choice("ab"), rng.choice(props), ["stack", "tight", "pad"])


def _s_two_positioned(rng: random.Random, props: str):
    l1, t1 = rng.choice((10, 20)), rng.choice((10, 20))
    l2, t2 = rng.choice((60, 80, 100)), rng.choice((60, 80))
    root = StackN([pos(box("a", 100, 80), left=l1, top=t1), pos(box("b", 80, 60), left=l2, top=t2)])
    return item(root, rng.choice("ab"), rng.choice(props), ["stack", "tight"])


def _s_negative(rng: random.Random, props: str):
    """A Positioned child can hang outside the Stack: negative left/top are allowed."""
    n = rng.choice((10, 20, 30))
    root = center(StackN([box("z", 100, 100), pos(box("a", 40, 40), left=-n, top=-n)]))
    return item(root, "a", rng.choice(props), ["stack", "tight", "align"])


STACK_TEMPLATES: list[Maker] = []
for _edges, _props in (("lt", "xyrb"), ("rb", "xyrb"), ("lb", "xyrb"), ("rt", "xyrb"), ("lr", "wxr"), ("tb", "hyb"),
                       ("ltrb", "whrb"), ("lw", "rw"), ("rw", "xw"), ("th", "bh"), ("bh", "yh"), ("ltwh", "rb"),
                       ("rbwh", "xy")):
    STACK_TEMPLATES.append(template(f"stack_positioned_{_edges}", _s_positioned, _edges, _props))
STACK_TEMPLATES.append(template("stack_alignment_x", _s_alignment, "xr", False))
STACK_TEMPLATES.append(template("stack_alignment_y", _s_alignment, "yb", False))
STACK_TEMPLATES.append(template("stack_alignment_custom", _s_alignment, "xy", True))
STACK_TEMPLATES.append(template("stack_alignment_positioned_plain", _s_alignment_plus_positioned, "a"))
STACK_TEMPLATES.append(template("stack_alignment_positioned_placed", _s_alignment_plus_positioned, "b"))
for _given in ("top", "left", "bottom", "right"):
    STACK_TEMPLATES.append(template(f"stack_half_positioned_{_given}", _s_half_positioned, _given))
STACK_TEMPLATES.append(template("stack_align_child", _s_align_child, False, "xyrb"))
STACK_TEMPLATES.append(template("stack_align_padded_child", _s_align_child, True, "xy"))
STACK_TEMPLATES.append(template("stack_in_sized", _s_in_sized, "xyrb"))
STACK_TEMPLATES.append(template("stack_sized_by_child_rb", _s_sized_by_child, "rb", "xyrb"))
STACK_TEMPLATES.append(template("stack_sized_by_child_lt", _s_sized_by_child, "lt", "xyrb"))
STACK_TEMPLATES.append(template("stack_alignment_in_sized_child", _s_alignment_in_sized_child, "xy"))
STACK_TEMPLATES.append(template("stack_nested", _s_nested, "xy"))
STACK_TEMPLATES.append(template("stack_padded", _s_padded, "xyrb"))
STACK_TEMPLATES.append(template("stack_two_positioned", _s_two_positioned, "xyrb"))
STACK_TEMPLATES.append(template("stack_negative", _s_negative, "xy"))


# ── 7. Wrap Lines ───────────────────────────────────────────────────────

def _boxes(rng: random.Random, n: int, kind: str) -> list[BoxN]:
    ids = "abcdefgh"[:n]
    if kind == "uniform":
        w = rng.choice((60, 80, 90, 100, 120))
        return [box(i, w, 50) for i in ids]
    if kind == "mixed":
        return [box(i, rng.choice((50, 80, 100, 120, 150)), 50) for i in ids]
    # tall and short: different heights
    return [box(i, rng.choice((60, 90, 110)), rng.choice((30, 50, 70, 90))) for i in ids]


def _w_core(rng: random.Random, n: int, kind: str, **kw) -> tuple[WrapN, list[BoxN]]:
    kids = _boxes(rng, n, kind)
    spacing = rng.choice((0, 5, 10, 20))
    run_spacing = rng.choice((0, 5, 10, 20))
    return WrapN(list(kids), spacing=spacing, run_spacing=run_spacing, **kw), kids


def rows_item(root: Node, ids: str, tops: bool = True, comment: str = "// how many rows?") -> Item:
    """How many rows (or columns) the Wrap made: the number of different tops (or lefts) of its boxes."""
    ctx = host(root)
    prop = "y" if tops else "x"
    answer = str(len({round(ctx.rects[i][1 if tops else 0], 6) for i in ids}))
    wrap = next(n for n in walk(root) if isinstance(n, WrapN))
    why = ("The screen is 400 x 300 and forces its root widget to exactly that size. "
           + " ".join(t for _, t in wrap.notes) + f" So the answer is {answer}.")
    check = "{" + ", ".join(f"{prop}('{i}')" for i in ids) + "}.length"
    return Item(comment + "\n" + render(root), answer, why, check=check)


def _w_rows(rng: random.Random, kind: str, n: int, wrapper: str):
    wrap, kids = _w_core(rng, n if wrapper == "none" and kind != "tallshort" else min(n, 4 if wrapper != "none" else 5), kind)
    ids = "abcdefgh"[:len(kids)]
    root: Node = wrap
    if wrapper == "padded":
        p = rng.choice((20, 40, 50))
        root = PadN(p, p, p, p, wrap)
    elif wrapper == "sized":
        root = center(SizedN(rng.choice((200, 250, 300)), None, wrap))
    return rows_item(root, ids)


def _w_exact(rng: random.Random, fits: bool):
    """Boxes that fill the row exactly (or by one pixel too much)."""
    k = rng.choice((3, 4, 5))
    spacing = rng.choice((0, 5, 10))
    w = (400 - spacing * (k - 1)) // k
    if w * k + spacing * (k - 1) != 400:
        raise Retry
    extra = 0 if fits else 1
    kids = [box(i, w + (extra if j == k - 1 else 0), 40) for j, i in enumerate("abcdefgh"[:k])]
    root = WrapN(kids, spacing=spacing, run_spacing=10)
    return rows_item(root, "abcdefgh"[:k])


def _w_place(rng: random.Random, kind: str, n: int, prop: str, which: str, wrapper: str):
    wrap, kids = _w_core(rng, n, kind)
    root: Node = wrap
    if wrapper == "padded":
        p = rng.choice((10, 20, 40))
        root = PadN(p, p, p, p, wrap)
    elif wrapper == "sized":
        root = center(SizedN(rng.choice((200, 250, 300)), None, wrap))
    ids = "abcdefgh"[:n]
    target = ids[-1] if which == "last" else rng.choice(ids[1:])
    return item(root, target, prop, ["wrap", "tight", "pad", "align"])


def _w_size(rng: random.Random, kind: str, n: int, prop: str):
    wrap, kids = _w_core(rng, n, kind)
    wrap.id = "w"
    root = AlignN(-1, -1, wrap)
    return item(root, "w", prop, ["wrap", "tight", "align"])


def _w_align(rng: random.Random, kind: str, how: str):
    """Alignment spreads the boxes of a row; runAlignment spreads the rows; crossAxisAlignment lines up unequal boxes."""
    n = rng.choice((3, 4, 5))
    if how == "main":
        wrap, kids = _w_core(rng, n, kind, align=rng.choice(("center", "end", "spaceBetween", "spaceAround", "spaceEvenly")))
        return item(wrap, rng.choice("ab"), "x", ["wrap", "tight"])
    if how == "run":
        wrap, kids = _w_core(rng, n, kind, run_align=rng.choice(("center", "end", "spaceBetween", "spaceEvenly")))
        return item(wrap, rng.choice("ab"), "y", ["wrap", "tight"])
    wrap, kids = _w_core(rng, n, "tallshort", cross_align=rng.choice(("center", "end")))
    return item(wrap, rng.choice("abc"), "y", ["wrap", "tight"])


def _w_vertical(rng: random.Random, n: int, kind: str):
    ids = "abcdefgh"[:n]
    h = rng.choice((60, 80, 100))
    kids = [box(i, 50, rng.choice((h, h + 20, 40))) if kind == "mixed" else box(i, 50, h) for i in ids]
    wrap = WrapN(kids, spacing=rng.choice((0, 10, 20)), run_spacing=rng.choice((0, 10, 20)), vertical=True)
    if kind == "count":
        return rows_item(wrap, ids, tops=False, comment="// how many columns?")
    return item(wrap, ids[-1], "x", ["wrap", "tight"])


WRAP_TEMPLATES: list[Maker] = []
for _kind in ("uniform", "mixed", "tallshort"):
    for _wrapper in ("none", "padded", "sized"):
        WRAP_TEMPLATES.append(template(f"wrap_rows_{_kind}_{_wrapper}", _w_rows, _kind, 6, _wrapper))
WRAP_TEMPLATES.append(template("wrap_rows_many", _w_rows, "uniform", 8, "none"))
WRAP_TEMPLATES.append(template("wrap_exact_fit", _w_exact, True))
WRAP_TEMPLATES.append(template("wrap_one_too_wide", _w_exact, False))
for _kind in ("uniform", "mixed"):
    for _wrapper in ("none", "padded", "sized"):
        WRAP_TEMPLATES.append(template(f"wrap_last_top_{_kind}_{_wrapper}", _w_place, _kind, 6, "y", "last", _wrapper))
        WRAP_TEMPLATES.append(template(f"wrap_left_{_kind}_{_wrapper}", _w_place, _kind, 5, "x", "other", _wrapper))
WRAP_TEMPLATES.append(template("wrap_last_left_uniform", _w_place, "uniform", 7, "x", "last", "none"))
WRAP_TEMPLATES.append(template("wrap_bottom_edge_uniform", _w_place, "uniform", 6, "b", "last", "none"))
WRAP_TEMPLATES.append(template("wrap_height", _w_size, "uniform", 6, "h"))
WRAP_TEMPLATES.append(template("wrap_height_mixed", _w_size, "tallshort", 5, "h"))
WRAP_TEMPLATES.append(template("wrap_width", _w_size, "mixed", 6, "w"))
WRAP_TEMPLATES.append(template("wrap_width_uniform", _w_size, "uniform", 5, "w"))
for _kind in ("uniform", "mixed"):
    WRAP_TEMPLATES.append(template(f"wrap_alignment_main_{_kind}", _w_align, _kind, "main"))
    WRAP_TEMPLATES.append(template(f"wrap_alignment_run_{_kind}", _w_align, _kind, "run"))
WRAP_TEMPLATES.append(template("wrap_alignment_cross", _w_align, "uniform", "cross"))
WRAP_TEMPLATES.append(template("wrap_vertical_count", _w_vertical, 6, "count"))
WRAP_TEMPLATES.append(template("wrap_vertical_count_mixed", _w_vertical, 7, "count"))
WRAP_TEMPLATES.append(template("wrap_vertical_left", _w_vertical, 6, "left"))


# ── 8. Overflow Or Fine ─────────────────────────────────────────────────

def overflow_item(root: Node) -> Item:
    ctx = host(root)
    answer = "overflow" if ctx.overflow else "fine"
    parts: list[str] = []
    flexes = [n for n in walk(root) if isinstance(n, FlexN)]
    worst = [n for n in flexes if n.has_overflow()] or flexes[:1]
    assert worst, 'an overflow item needs a Row or Column'
    for n in worst:
        row = n.axis == "row"
        sizes = [k.size[0 if row else 1] for k, _, _ in n.placed]
        need = " + ".join(fnum(s) for s in sizes)
        word = "Row" if row else "Column"
        space = fnum(n.actual_main)
        if n.has_overflow():
            parts.append(f"The {word} has {space} along its main axis, but its children need {need} = {fnum(n.allocated)}: "
                         f"it overflows by {fnum(n.overflowed)}.")
        else:
            parts.append(f"The {word} has {space} along its main axis and its children need {need} = {fnum(n.allocated)}, "
                         f"so everything fits.")
    why = "The screen is 400 x 300 and forces its root widget to exactly that size. " + " ".join(parts)
    return Item("// fine or overflow?\n" + render(root), answer, why.strip(), check="overflowed ? 'overflow' : 'fine'")


def split10(rng: random.Random, total: int, n: int, lo: int = 20, hi: int = 350) -> list[int]:
    """`n` sizes, each a multiple of 10 between lo and hi, that add up to `total`."""
    if total % 10:
        raise Retry
    parts = [lo] * n
    left = (total - lo * n) // 10
    if left < 0:
        raise Retry
    for _ in range(left):
        i = rng.randrange(n)
        parts[i] += 10
    if any(p > hi for p in parts):
        raise Retry
    return parts


def _o_fixed(rng: random.Random, axis: str, n: int):
    """A Row/Column of fixed Boxes whose total is a little under, exactly, or a little over the room."""
    room = 400 if axis == "row" else 300
    total = room + rng.choice((-60, -30, -10, 0, 10, 20, 40, 70))
    parts = split10(rng, total, n)
    kids = [box(i, p, 50) if axis == "row" else box(i, 50, p) for i, p in zip("abcd", parts)]
    return overflow_item(FlexN(axis, kids))


def _o_expanded_with_big_fixed(rng: random.Random, axis: str):
    room = 400 if axis == "row" else 300
    big = room + rng.choice((-100, -20, 0, 30, 100))
    kids = [box("a", big, 50) if axis == "row" else box("a", 50, big), Expanded(box("b"))]
    return overflow_item(FlexN(axis, kids))


def _o_expanded_big_child(rng: random.Random, axis: str):
    big = rng.choice((500, 600))
    kids = [Expanded(box("a", big, 50) if axis == "row" else box("a", 50, big)), box("b")]
    return overflow_item(FlexN(axis, kids))


def _o_flexible_big(rng: random.Random, axis: str, with_fixed: bool):
    room = 400 if axis == "row" else 300
    mk = (lambda i, s: box(i, s, 50)) if axis == "row" else (lambda i, s: box(i, 50, s))
    kids: list[Node] = [Flexible(mk("a", room)), Flexible(mk("b", room))]
    if with_fixed:
        kids.insert(0, mk("c", rng.choice((50, 100, 200))))
    return overflow_item(FlexN(axis, kids))


def _o_padded(rng: random.Random, axis: str):
    room = 400 if axis == "row" else 300
    p = rng.choice((10, 20, 30, 50))
    n = rng.choice((2, 3))
    parts = split10(rng, room - 2 * p + rng.choice((-20, -10, 0, 10, 30)), n)
    kids = [box(i, s, 50) if axis == "row" else box(i, 50, s) for i, s in zip("abc", parts)]
    return overflow_item(PadN(p, p, p, p, FlexN(axis, kids)))


def _o_sized(rng: random.Random, axis: str):
    room = rng.choice((200, 250, 300)) if axis == "row" else rng.choice((150, 200, 250))
    n = rng.choice((2, 3))
    parts = split10(rng, room + rng.choice((-30, -10, 0, 20, 50)), n)
    kids = [box(i, s, 50) if axis == "row" else box(i, 50, s) for i, s in zip("abc", parts)]
    sized = SizedN(room, None, FlexN(axis, kids)) if axis == "row" else SizedN(None, room, FlexN(axis, kids))
    return overflow_item(center(sized))


def _o_wrap(rng: random.Random, axis: str):
    """Wrap inside a Row has no width limit to wrap at, so it makes one long line and the Row overflows; inside a Column
    it wraps at the screen's width, and it is the stacked rows that may be too tall."""
    if axis == "row":
        n = rng.choice((5, 6, 7))
        return overflow_item(FlexN("row", [WrapN([box(i, 100, 50) for i in "abcdefg"[:n]], spacing=10, run_spacing=10)]))
    h = rng.choice((120, 140, 150, 160))
    kids = [box(i, 190, h) for i in "abcd"]
    return overflow_item(FlexN("column", [WrapN(kids, spacing=10, run_spacing=10)]))


def _o_container_margin(rng: random.Random, axis: str):
    """Each Container takes its size PLUS its margin along the main axis."""
    k = rng.choice((2, 3))
    size = rng.choice((120, 150, 180))
    m = rng.choice((10, 20, 30))
    kids = [ContainerN(None, width=size, height=50, margin=(m, m, m, m)) if axis == "row" else
            ContainerN(None, width=50, height=size, margin=(m, m, m, m)) for _ in range(k)]
    return overflow_item(FlexN(axis, kids))


def _o_nested_expanded(rng: random.Random, axis: str):
    """Expanded gives its child exactly half the room; a Row inside it overflows that half, not the screen."""
    share = 200 if axis == "row" else 150
    parts = split10(rng, share + rng.choice((-30, -10, 10, 30, 50)), 2, lo=30)
    inner = FlexN(axis, [box(i, s, 50) if axis == "row" else box(i, 50, s) for i, s in zip("ab", parts)])
    return overflow_item(FlexN(axis, [Expanded(inner), Expanded(box("c"))]))


def _o_cross_column_in_row(rng: random.Random):
    """A Column inside a Row is as tall as the screen allows (300), so tall Boxes overflow it."""
    sizes = [rng.choice((50, 80, 100, 120)) for _ in range(3)]
    inner = FlexN("column", [box(i, 50, s) for i, s in zip("abc", sizes)])
    return overflow_item(FlexN("row", [inner, box("d")]))


def _o_row_in_column(rng: random.Random):
    ws = [rng.choice((100, 120, 150, 200)) for _ in range(3)]
    inner = FlexN("row", [box(i, s, 50) for i, s in zip("abc", ws)])
    return overflow_item(FlexN("column", [inner, box("d")]))


def _o_stack(rng: random.Random):
    ws = [rng.choice((100, 150, 200, 250)) for _ in range(2)]
    return overflow_item(StackN([FlexN("row", [box(i, s, 50) for i, s in zip("ab", ws)])]))


def _o_spaced(rng: random.Random, align: str):
    ws = [rng.choice((100, 150, 200)) for _ in range(3)]
    return overflow_item(FlexN("row", [box(i, s, 50) for i, s in zip("abc", ws)], main=align, mark_main=True))


def _o_min(rng: random.Random):
    ws = [rng.choice((100, 150, 200)) for _ in range(3)]
    return overflow_item(center(FlexN("row", [box(i, s, 50) for i, s in zip("abc", ws)], main_size="min")))


def _o_padded_children(rng: random.Random, axis: str):
    p = rng.choice((20, 30, 40))
    k = rng.choice((3, 4, 5))
    size = rng.choice((40, 50, 60))
    kids = [PadN(p, p, p, p, box(i, size, size)) for i in "abcde"[:k]]
    return overflow_item(FlexN(axis, kids))


OVERFLOW_TEMPLATES: list[Maker] = []
for _axis in ("row", "column"):
    for _n in (2, 3, 4):
        OVERFLOW_TEMPLATES.append(template(f"overflow_fixed_{_n}_{_axis}", _o_fixed, _axis, _n))
    OVERFLOW_TEMPLATES.append(template(f"overflow_expanded_big_fixed_{_axis}", _o_expanded_with_big_fixed, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_expanded_big_child_{_axis}", _o_expanded_big_child, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_flexible_big_{_axis}", _o_flexible_big, _axis, False))
    OVERFLOW_TEMPLATES.append(template(f"overflow_flexible_big_fixed_{_axis}", _o_flexible_big, _axis, True))
    OVERFLOW_TEMPLATES.append(template(f"overflow_padded_{_axis}", _o_padded, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_sized_{_axis}", _o_sized, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_wrap_{_axis}", _o_wrap, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_container_margin_{_axis}", _o_container_margin, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_nested_expanded_{_axis}", _o_nested_expanded, _axis))
    OVERFLOW_TEMPLATES.append(template(f"overflow_padded_children_{_axis}", _o_padded_children, _axis))
OVERFLOW_TEMPLATES.append(template("overflow_column_in_row", _o_cross_column_in_row))
OVERFLOW_TEMPLATES.append(template("overflow_row_in_column", _o_row_in_column))
OVERFLOW_TEMPLATES.append(template("overflow_stack", _o_stack))
for _align in ("start", "center", "spaceBetween", "spaceEvenly"):
    OVERFLOW_TEMPLATES.append(template(f"overflow_spaced_{_align}", _o_spaced, _align))
OVERFLOW_TEMPLATES.append(template("overflow_min", _o_min))
