"""Flutter layout pack, part 2: Padding Math and Tight or Loose (one box inside wrappers).

The widget tree is built from `_flutter_model.py` nodes, printed as the code the learner reads and laid out by the
hand-written constraint rules (constraints go down, sizes go up, the parent positions); tests/flutter_oracle.py
builds the same tree in real Flutter. The host is the 400 x 300 screen, whose root widget is forced to that size, so
the same Box is 50 x 50 inside a Center and 400 x 300 when it is the root: that difference is the lesson.
"""

from __future__ import annotations

import random

from ._flutter_model import (AlignN, AspectN, BC, BoxN, ConstrainedN, ContainerN, FlexN, FractionalN, Node, PadN,
                             SizedN, StackN, UnconstrainedN, WrapN, Expanded, Retry, fit, item, named)
from ._model import Maker

PADS = (10, 20, 25, 30, 40, 50)
EVEN = (10, 20, 30, 40, 50, 60)


def template(name: str, fn, *args) -> Maker:
    def make(rng: random.Random):
        return fn(rng, *args)
    return fit(named(name, make))


def box(id_: str = "a", w: float = 50, h: float = 50) -> BoxN:
    return BoxN(id_, w=w, h=h)


def center(child: Node) -> AlignN:
    return AlignN(0, 0, child, center=True)


def pick(rng: random.Random, props: str) -> str:
    return rng.choice(props)


# ── 1. Padding Math ─────────────────────────────────────────────────────

def _pad_root(rng: random.Random, style: str, props: str):
    """Padding is the root: the screen forces it to 400 x 300, and the Box inside gets what is left."""
    if style == "all":
        l = t = r = b = rng.choice(PADS)
    elif style == "sym":
        l = r = rng.choice(PADS)
        t = b = rng.choice(PADS)
        if l == t:
            raise Retry
    elif style == "only":
        l, t, r, b = rng.choice(((rng.choice(PADS), 0, 0, 0), (0, rng.choice(PADS), 0, 0), (rng.choice(PADS), rng.choice(PADS), 0, 0),
                                 (0, 0, rng.choice(PADS), rng.choice(PADS))))
    else:
        l, t, r, b = (rng.choice(PADS) for _ in range(4))
    root = PadN(l, t, r, b, box(), style="ltrb" if style == "ltrb" else "auto")
    return item(root, "a", pick(rng, props), ["pad", "tight"])


def _pad_nested(rng: random.Random, props: str):
    p, q = rng.sample(PADS, 2)
    root = PadN(p, p, p, p, PadN(q, q, q, q, box()))
    return item(root, "a", pick(rng, props), ["pad", "tight"])


def _container_root(rng: random.Random, kind: str, props: str):
    """Container(margin / padding) as the root: with a child and no size it just passes the screen's tightness on."""
    m = rng.choice(PADS)
    p = rng.choice(PADS)
    if kind == "margin":
        c = ContainerN(box(), margin=(m, m, m, m))
    elif kind == "padding":
        c = ContainerN(box(), padding=(p, p, p, p))
    else:
        c = ContainerN(box(), margin=(m, m, m, m), padding=(p, p, p, p))
    return item(c, "a", pick(rng, props), ["pad", "tight"])


def _center_padded(rng: random.Random, kind: str, props: str):
    """Center(Padding(...)): the Padding is only as big as Box + padding, centred; padding moves the Box only if it
    is lopsided."""
    p = rng.choice(PADS)
    if kind == "all":
        pad = PadN(p, p, p, p, box())
    elif kind == "left":
        pad = PadN(p, 0, 0, 0, box())
    elif kind == "top":
        pad = PadN(0, p, 0, 0, box())
    elif kind == "right":
        pad = PadN(0, 0, p, 0, box())
    else:
        pad = PadN(p, rng.choice(PADS), 0, 0, box())
    return item(center(pad), "a", pick(rng, props), ["pad", "tight", "align"])


def _center_container(rng: random.Random, kind: str, props: str):
    """Center(Container(...)): a Container with a child and no size is exactly as big as child + padding + margin."""
    p = rng.choice(PADS)
    if kind == "padding":
        c = ContainerN(box(), padding=(p, p, p, p))
    elif kind == "margin":
        c = ContainerN(box(), margin=(p, p, p, p))
    else:
        q = rng.choice(PADS)
        c = ContainerN(box(), margin=(p, p, p, p), padding=(q, q, q, q))
    c.id = "c"
    return item(center(c), "c", pick(rng, props), ["pad", "tight", "align"])


def _center_sized_container(rng: random.Random, kind: str, props: str):
    """Center(Container(width: 200, height: 100, ...)): the size is fixed; padding or margin eats into the Box."""
    w, h = rng.choice(((200, 100), (240, 120), (300, 150), (160, 80), (200, 160), (240, 200)))
    p = rng.choice((10, 20, 30))
    if kind == "padding":
        c = ContainerN(box(), width=w, height=h, padding=(p, p, p, p))
    elif kind == "margin":
        c = ContainerN(box(), width=w, height=h, margin=(p, p, p, p))
    elif kind == "alignment":
        ax, ay = rng.choice(((1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (1, 0)))
        c = ContainerN(box(), width=w, height=h, alignment=(ax, ay))
    else:
        ax, ay = rng.choice(((1, 1), (-1, 1), (1, -1)))
        c = ContainerN(box(), width=w, height=h, padding=(p, p, p, p), alignment=(ax, ay))
    return item(center(c), "a", pick(rng, props), ["pad", "tight", "align"])


def _align_padded(rng: random.Random, where: tuple[int, int], props: str):
    p = rng.choice(PADS)
    root = AlignN(where[0], where[1], PadN(p, p, p, p, box()))
    return item(root, "a", pick(rng, props), ["pad", "tight", "align"])


def _padded_align(rng: random.Random, where: tuple[int, int], props: str):
    p = rng.choice(PADS)
    root = PadN(p, p, p, p, AlignN(where[0], where[1], box(), center=where == (0, 0)))
    return item(root, "a", pick(rng, props), ["pad", "tight", "align"])


def _padded_center_only(rng: random.Random, edge: str, props: str):
    p = rng.choice((20, 30, 40, 60))
    ins = {"top": (0, p, 0, 0), "left": (p, 0, 0, 0), "bottom": (0, 0, 0, p), "right": (0, 0, p, 0)}[edge]
    return item(PadN(*ins, center(box())), "a", pick(rng, props), ["pad", "tight", "align"])


def _flex_padded_child(rng: random.Random, axis: str, kind: str):
    """Row/Column holding a padded Box and another Box: the padding makes the first one take more room."""
    p = rng.choice((10, 20, 30))
    ins = (p, p, p, p) if kind == "all" else ((p, 0, 0, 0) if axis == "row" else (0, p, 0, 0))
    kids = [PadN(*ins, box("a")), box("b")]
    root = FlexN(axis, kids)
    return item(root, rng.choice("ab"), "x" if axis == "row" else "y", ["pad", "flex", "pos"])


def _padded_flex(rng: random.Random, axis: str):
    p = rng.choice(PADS)
    kids = [Expanded(box("a")), Expanded(box("b"))]
    root = PadN(p, p, p, p, FlexN(axis, kids))
    return item(root, rng.choice("ab"), "w" if axis == "row" else "h", ["pad", "flex", "tight"])


def _center_sized_padded(rng: random.Random, props: str):
    w = rng.choice((200, 240, 300))
    p = rng.choice((10, 20, 30))
    root = center(SizedN(w, None, PadN(p, p, p, p, box())))
    return item(root, "a", pick(rng, props), ["pad", "tight", "align"])


PADDING_TEMPLATES: list[Maker] = []
for _style in ("all", "sym", "only", "ltrb"):
    PADDING_TEMPLATES.append(template(f"pad_root_{_style}", _pad_root, _style, "whxyrb"))
PADDING_TEMPLATES.append(template("pad_nested_size", _pad_nested, "wh"))
PADDING_TEMPLATES.append(template("pad_nested_place", _pad_nested, "xy"))
for _kind in ("margin", "padding", "both"):
    PADDING_TEMPLATES.append(template(f"pad_container_root_{_kind}", _container_root, _kind, "whxy"))
for _kind in ("all", "left", "top", "right", "mixed"):
    PADDING_TEMPLATES.append(template(f"pad_center_{_kind}", _center_padded, _kind, "xyrb"))
for _kind in ("padding", "margin", "both"):
    PADDING_TEMPLATES.append(template(f"pad_center_container_{_kind}", _center_container, _kind, "wh"))
for _kind in ("padding", "margin", "alignment", "mixed"):
    PADDING_TEMPLATES.append(template(f"pad_center_sized_container_{_kind}", _center_sized_container, _kind, "whxy"))
for _where in ((-1, -1), (1, 1), (1, -1), (-1, 1)):
    PADDING_TEMPLATES.append(template(f"pad_align_padded_{_where}", _align_padded, _where, "xy"))
    PADDING_TEMPLATES.append(template(f"pad_padded_align_{_where}", _padded_align, _where, "xy"))
for _edge in ("top", "left", "bottom", "right"):
    PADDING_TEMPLATES.append(template(f"pad_padded_center_{_edge}", _padded_center_only, _edge, "xy"))
for _axis in ("row", "column"):
    for _kind in ("all", "one"):
        PADDING_TEMPLATES.append(template(f"pad_flex_child_{_kind}_{_axis}", _flex_padded_child, _axis, _kind))
    PADDING_TEMPLATES.append(template(f"pad_padded_flex_{_axis}", _padded_flex, _axis))
PADDING_TEMPLATES.append(template("pad_center_sized_padded", _center_sized_padded, "whx"))


# ── 2. Tight or Loose ───────────────────────────────────────────────────

def _t_root_box(rng: random.Random, props: str):
    """The Box IS the root: tight constraints make it the size of the screen whatever it asks for."""
    w, h = rng.choice(((100, 60), (200, 200), (30, 80), (500, 40), (60, 400), (50, 50)))
    return item(box("a", w, h), "a", pick(rng, props), ["tight"])


def _t_center_box(rng: random.Random, props: str):
    w, h = rng.choice(((100, 60), (200, 200), (30, 80), (500, 40), (60, 400), (350, 280), (120, 90)))
    return item(center(box("a", w, h)), "a", pick(rng, props), ["tight", "align"])


def _t_align_box(rng: random.Random, props: str):
    w, h = rng.choice(((100, 60), (500, 40), (60, 400), (200, 100)))
    ax, ay = rng.choice(((1, 1), (-1, 1), (0, 1), (1, 0), (-1, -1)))
    return item(AlignN(ax, ay, box("a", w, h)), "a", pick(rng, props), ["tight", "align"])


def _t_sized_root(rng: random.Random, props: str):
    """SizedBox as the root is overruled: the screen is tight, so it cannot be 200 wide."""
    w, h = rng.choice(((200, 100), (100, 100), (300, 150), (350, 250)))
    return item(SizedN(w, h, box()), "a", pick(rng, props), ["tight"])


def _t_center_sized(rng: random.Random, kind: str, props: str):
    """Center(SizedBox(...)): now the SizedBox may have the size it says, and gives it to the Box as a tight demand."""
    w, h = rng.choice(((200, 100), (100, 120), (300, 150), (80, 80), (250, 250)))
    inner = box("a", rng.choice((30, 50, 400)), rng.choice((20, 50, 350)))
    if kind == "both":
        root = center(SizedN(w, h, inner))
    elif kind == "width":
        root = center(SizedN(w, None, inner))
    elif kind == "height":
        root = center(SizedN(None, h, inner))
    else:
        root = center(SizedN(w, None, center(inner)))
    return item(root, "a", pick(rng, props), ["tight", "align"])


def _t_constrained(rng: random.Random, kind: str, props: str):
    """Center(ConstrainedBox(...)): min forces a Box bigger, max squeezes it smaller, in-between leaves it alone."""
    if kind == "min":
        bc, style = BC(minw=rng.choice((100, 150, 200)), minh=rng.choice((80, 120))), "plain"
        inner = box("a", rng.choice((30, 50, 80)), rng.choice((20, 40, 50)))
    elif kind == "max":
        bc, style = BC(maxw=rng.choice((60, 80, 120)), maxh=rng.choice((40, 70))), "plain"
        inner = box("a", rng.choice((100, 200, 300)), rng.choice((80, 150)))
    elif kind == "range":
        lo = rng.choice((60, 100))
        hi = lo + rng.choice((40, 80))
        bc, style = BC(minw=lo, maxw=hi), "plain"
        inner = box("a", rng.choice((30, 50, 70, 120, 200)), 50)
    elif kind == "tightFor":
        v = rng.choice((100, 150, 200))
        bc, style = BC.tight_for(w=v), "tightFor"
        inner = box("a", rng.choice((30, 300)), 50)
    elif kind == "tight":
        bc, style = BC.tight(rng.choice((100, 150)), rng.choice((60, 90))), "tight"
        inner = box("a", rng.choice((30, 300)), rng.choice((20, 200)))
    else:
        bc, style = BC(maxw=rng.choice((120, 160)), maxh=rng.choice((80, 110))), "loose"
        inner = box("a", rng.choice((30, 300)), rng.choice((20, 200)))
    if style == "loose":
        bc = BC(0, bc.maxw, 0, bc.maxh)
    return item(center(ConstrainedN(bc, inner, style)), "a", pick(rng, props), ["tight", "align"])


def _t_constrained_root(rng: random.Random, props: str):
    """ConstrainedBox as the root: its limits are squeezed into the screen's tight demand, so they change nothing."""
    bc = BC(maxw=rng.choice((100, 150)), maxh=rng.choice((80, 120)))
    return item(ConstrainedN(bc, box()), "a", pick(rng, props), ["tight"])


def _t_unconstrained(rng: random.Random, root: bool, props: str):
    """UnconstrainedBox lets the Box be its own size even when the screen is tight."""
    w, h = rng.choice(((100, 60), (200, 80), (30, 120), (350, 250)))
    inner = UnconstrainedN(box("a", w, h))
    return item(inner if root else center(inner), "a", pick(rng, props), ["tight", "align"])


def _t_container(rng: random.Random, kind: str, props: str):
    w, h = rng.choice(((200, 100), (100, 100), (300, 150)))
    if kind == "root":
        c = ContainerN(box(), width=w, height=h)
        return item(c, "a", pick(rng, props), ["tight"])
    if kind == "sized":
        return item(center(ContainerN(box(), width=w, height=h)), "a", pick(rng, props), ["tight", "align"])
    if kind == "wrap":
        return item(center(ContainerN(box("a", rng.choice((70, 90, 150)), rng.choice((40, 60, 120))))), "a",
                    pick(rng, props), ["tight", "align"])
    mw = rng.choice((100, 120, 160))
    return item(center(ContainerN(box("a", rng.choice((200, 300)), 50), constraints=BC(maxw=mw))), "a",
                pick(rng, props), ["tight", "align"])


def _t_aspect(rng: random.Random, kind: str, props: str):
    ratio = rng.choice((0.5, 1, 2, 4))
    if kind == "center":
        root = center(AspectN(ratio, box()))
    elif kind == "sized":
        root = center(SizedN(rng.choice((100, 200, 160)), None, AspectN(ratio, box())))
    elif kind == "root":
        root = AspectN(ratio, box())
    else:
        root = center(SizedN(None, rng.choice((100, 150, 200)), AspectN(ratio, box())))
    return item(root, "a", pick(rng, props), ["aspect", "tight", "align"])


def _t_fractional(rng: random.Random, kind: str, props: str):
    f = rng.choice((0.25, 0.5, 0.75))
    if kind == "root":
        root = FractionalN(f, None, box())
    elif kind == "center":
        root = center(FractionalN(f, None, box()))
    elif kind == "height":
        root = center(FractionalN(None, rng.choice((0.5, 1.0)), box()))
    else:
        root = center(FractionalN(f, rng.choice((0.5, 1.0)), box()))
    return item(root, "a", pick(rng, props), ["tight", "align"])


def _t_square(rng: random.Random, root: bool, props: str):
    d = rng.choice((100, 120, 200))
    sq = SizedN(d, d, box(), square=True)
    return item(sq if root else center(sq), "a", pick(rng, props), ["tight", "align"])


def _t_flex_child(rng: random.Random, axis: str, props: str):
    """A Row hands its children loose constraints across it; a Column along the screen's height gives no limit."""
    big = rng.choice((500, 350, 600))
    root = FlexN(axis, [box("a", big if axis == "column" else 100, 400 if axis == "row" else 100)])
    return item(root, "a", pick(rng, props), ["tight", "flex"])


def _t_stack_box(rng: random.Random, props: str):
    w, h = rng.choice(((100, 60), (500, 40), (60, 400), (250, 150)))
    return item(StackN([box("a", w, h)]), "a", pick(rng, props), ["tight", "stack"])


def _t_wrap_box(rng: random.Random, props: str):
    w, h = rng.choice(((100, 60), (500, 40), (700, 90)))
    return item(WrapN([box("a", w, h)]), "a", pick(rng, props), ["tight", "wrap"])


def _t_nested_center(rng: random.Random, props: str):
    w = rng.choice((100, 150, 200))
    root = center(SizedN(w, w, center(box("a", rng.choice((50, 300)), rng.choice((20, 300))))))
    return item(root, "a", pick(rng, props), ["tight", "align"])


TIGHT_TEMPLATES: list[Maker] = []
TIGHT_TEMPLATES.append(template("tight_root_box_size", _t_root_box, "wh"))
TIGHT_TEMPLATES.append(template("tight_root_box_place", _t_root_box, "xr"))
TIGHT_TEMPLATES.append(template("tight_center_box_size", _t_center_box, "wh"))
TIGHT_TEMPLATES.append(template("tight_center_box_place", _t_center_box, "xyrb"))
TIGHT_TEMPLATES.append(template("tight_align_box_size", _t_align_box, "wh"))
TIGHT_TEMPLATES.append(template("tight_align_box_place", _t_align_box, "xy"))
TIGHT_TEMPLATES.append(template("tight_sized_root", _t_sized_root, "wh"))
for _kind in ("both", "width", "height", "width_center"):
    TIGHT_TEMPLATES.append(template(f"tight_center_sized_{_kind}", _t_center_sized, _kind, "wh"))
for _kind in ("min", "max", "range", "tightFor", "tight", "loose"):
    TIGHT_TEMPLATES.append(template(f"tight_constrained_{_kind}", _t_constrained, _kind, "wh"))
TIGHT_TEMPLATES.append(template("tight_constrained_root", _t_constrained_root, "wh"))
TIGHT_TEMPLATES.append(template("tight_unconstrained_root", _t_unconstrained, True, "wh"))
TIGHT_TEMPLATES.append(template("tight_unconstrained_center", _t_unconstrained, False, "wh"))
for _kind in ("root", "sized", "wrap", "constraints"):
    TIGHT_TEMPLATES.append(template(f"tight_container_{_kind}", _t_container, _kind, "wh"))
for _kind in ("center", "sized", "root", "height"):
    TIGHT_TEMPLATES.append(template(f"tight_aspect_{_kind}", _t_aspect, _kind, "wh"))
for _kind in ("root", "center", "height", "both"):
    TIGHT_TEMPLATES.append(template(f"tight_fractional_{_kind}", _t_fractional, _kind, "wh"))
TIGHT_TEMPLATES.append(template("tight_square_root", _t_square, True, "wh"))
TIGHT_TEMPLATES.append(template("tight_square_center", _t_square, False, "wh"))
for _axis in ("row", "column"):
    TIGHT_TEMPLATES.append(template(f"tight_flex_child_{_axis}", _t_flex_child, _axis, "wh"))
TIGHT_TEMPLATES.append(template("tight_stack_box", _t_stack_box, "wh"))
TIGHT_TEMPLATES.append(template("tight_wrap_box", _t_wrap_box, "wh"))
TIGHT_TEMPLATES.append(template("tight_nested_center", _t_nested_center, "wh"))
