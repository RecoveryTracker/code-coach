"""Flutter layout pack, part 1: Flex Share, Main Axis and Cross Axis (Row and Column).

Every template builds a widget tree out of the nodes of `_flutter_model.py`; that same tree is printed as the code the
learner reads and laid out by Flutter's own flex algorithm (written out by hand there), and tests/test_brain_packs.py
then builds every tree in real Flutter and measures it (tests/flutter_oracle.py). A template is a (structure, axis)
pair - `Row` and `Column` are different templates, since they work on a different 400 vs 300 - with random sizes and
flex factors from small clean sets.
"""

from __future__ import annotations

import random

from ._flutter_model import (AlignN, BoxN, FlexN, Node, PadN, Retry, SizedN, Expanded, Flexible, Spacer, fit,
                             item, named)
from ._model import Maker

AXES = ("row", "column")
LETTERS = "abcdefgh"
SIZES = (30, 40, 50, 60, 70, 80, 90, 100, 120)
ALIGNS = ("start", "end", "center", "spaceBetween", "spaceAround", "spaceEvenly")


def avail(axis: str) -> int:
    """The screen along a Row (400) or a Column (300)."""
    return 400 if axis == "row" else 300


def mbox(axis: str, id_: str, main: float, cross: float = 50) -> BoxN:
    """A Box with the given size ALONG the axis (and `cross` across it)."""
    return BoxN(id_, w=main, h=cross) if axis == "row" else BoxN(id_, w=cross, h=main)


def along(axis: str) -> dict[str, str]:
    """The measurement letters along an axis: start (x or y), size (w or h), far edge (r or b)."""
    return {"start": "x", "size": "w", "end": "r"} if axis == "row" else {"start": "y", "size": "h", "end": "b"}


def across(axis: str) -> dict[str, str]:
    return along("column" if axis == "row" else "row")


def flex(axis: str, kids: list[Node], **kw) -> FlexN:
    return FlexN(axis, kids, **kw)


def template(name: str, fn, *args) -> Maker:
    """A template: `fn(rng, *args)` with a name, re-rolled until the prompt is short and the answer whole."""
    def make(rng: random.Random):
        return fn(rng, *args)
    return fit(named(name, make))


# ── 1. Flex Share ───────────────────────────────────────────────────────

def _pattern(rng: random.Random, axis: str, pattern: str, outer: str, inner: str):
    """A row/column of the kinds in `pattern`: F a fixed Box, E an Expanded Box, L a Flexible Box smaller than its
    share, G a Flexible Box bigger than its share, S a Spacer. `outer`: none | pad | sized; `inner`: none | pad | center
    (what each Expanded Box sits in)."""
    row = axis == "row"
    total_len = avail(axis)
    wrap_pad = wrap_len = 0
    if outer == "pad":
        wrap_pad = rng.choice((10, 20, 25, 50))
        total_len -= 2 * wrap_pad
    elif outer == "sized":
        wrap_len = rng.choice((200, 240, 300, 360)) if row else rng.choice((150, 180, 240))
        total_len = wrap_len
    kinds = list(pattern)
    flexes = [rng.choice((1, 1, 2, 3)) if k in "ELGS" else 0 for k in kinds]
    fixed = [rng.choice(SIZES) if k == "F" else 0 for k in kinds]
    free = total_len - sum(fixed)
    total_flex = sum(flexes)
    if free <= 0 or free % total_flex:
        raise Retry
    per = free // total_flex
    pad_in = rng.choice((10, 20)) if inner == "pad" else 0
    kids: list[Node] = []
    meta: list[tuple[str, str]] = []  # (id, kind) of the Boxes
    next_id = iter(LETTERS)
    for k, f, fx in zip(kinds, flexes, fixed):
        if k == "S":
            kids.append(Spacer(f))
            continue
        id_ = next(next_id)
        if k == "F":
            kids.append(mbox(axis, id_, fx))
        elif k == "E":
            box = mbox(axis, id_, rng.choice((50, 50, 100)))
            if inner == "pad":
                box = PadN(pad_in, pad_in, pad_in, pad_in, box)
            elif inner == "center":
                box = AlignN(0, 0, box, center=True)
            kids.append(Expanded(box, f))
        elif k == "L":
            small = [s for s in SIZES if s < per * f]
            if not small:
                raise Retry
            kids.append(Flexible(mbox(axis, id_, rng.choice(small)), f))
        else:  # G
            kids.append(Flexible(mbox(axis, id_, per * f + rng.choice((50, 100, 150))), f))
        meta.append((id_, k))
    root: Node = flex(axis, kids)
    if outer == "pad":
        root = PadN(wrap_pad, wrap_pad, wrap_pad, wrap_pad, root)
    elif outer == "sized":
        root = AlignN(0, 0, SizedN(wrap_len if row else None, None if row else wrap_len, root), center=True)
    # what to ask: a flexible Box's size, or a fixed Box's place after a flexible child
    a = along(axis)
    kind_of = dict(meta)
    sizes = [i for i, k in meta if k in "EG"] or [i for i, k in meta if k == "L"]
    after: list[str] = []
    seen_flex = False
    ids = iter(i for i, _ in meta)
    for k in kinds:
        if k == "S":
            seen_flex = True
            continue
        id_ = next(ids)
        if k == "F" and seen_flex:
            after.append(id_)
        elif k != "F":
            seen_flex = True
    if inner == "center":
        target, prop = rng.choice([i for i, k in meta if k == "E"] or sizes), a["start"]
    elif inner == "pad":
        target, prop = rng.choice([i for i, k in meta if k == "E"]), a["size"]
    elif after and (not sizes or rng.random() < 0.45):
        target, prop = rng.choice(after), a["start"]
    else:
        target, prop = rng.choice(sizes), a["size"]
    topics = ["flex", "tight", "pad", "align", "pos"] if prop == a["start"] else ["flex", "tight", "pad"]
    tail = ""
    if kind_of.get(target) == "G":
        tail = "A Flexible child may be smaller than its share but never bigger, so the big Box is cut down to it."
    if kind_of.get(target) == "L":
        tail = "A loose Flexible child keeps its own size when it fits in the share."
    return item(root, target, prop, topics, tail)


FLEX_PATTERNS = ("EE", "EEE", "FE", "EF", "FEE", "EFE", "EEF", "FFE", "FEF", "EFF", "FEFE", "FSF", "FSFSF", "SFE",
                 "FSE", "LE", "GE", "LEE", "GEE", "ELE", "FG", "FL")
FLEX_PAD = ("EE", "FE", "EFE", "FEE")
FLEX_SIZED = ("EE", "FE", "EFE")
FLEX_INNER = ("EE", "FE", "EFE")


def _nested(rng: random.Random, axis: str, ask_inner: bool):
    """A Column of two Expanded areas, the second holding a Row of two Expanded Boxes (or the other way round)."""
    inner_axis = "column" if axis == "row" else "row"
    f1, f2 = rng.choice(((1, 1), (1, 2), (2, 1), (1, 3), (3, 1)))
    g1, g2 = rng.choice(((1, 1), (1, 2), (2, 1), (1, 3), (3, 1)))
    outer_total = avail(axis)
    if outer_total % (f1 + f2):
        raise Retry
    first = Expanded(mbox(axis, "a", 50), f1)
    inner = flex(inner_axis, [Expanded(mbox(inner_axis, "b", 50), g1), Expanded(mbox(inner_axis, "c", 50), g2)])
    root = flex(axis, [first, Expanded(inner, f2)])
    if ask_inner:
        target, prop = rng.choice(("b", "c")), along(inner_axis)["size"]
    else:
        target, prop = "a", along(axis)["size"]
    return item(root, target, prop, ["flex", "tight"])


def _in_padded_expanded(rng: random.Random, axis: str):
    return _pattern(rng, axis, rng.choice(FLEX_INNER), "none", "pad")


FLEX_TEMPLATES: list[Maker] = []
for _axis in AXES:
    for _p in FLEX_PATTERNS:
        FLEX_TEMPLATES.append(template(f"flex_{_p}_{_axis}", _pattern, _axis, _p, "none", "none"))
    for _p in FLEX_PAD:
        FLEX_TEMPLATES.append(template(f"flex_pad_{_p}_{_axis}", _pattern, _axis, _p, "pad", "none"))
    for _p in FLEX_SIZED:
        FLEX_TEMPLATES.append(template(f"flex_sized_{_p}_{_axis}", _pattern, _axis, _p, "sized", "none"))
    for _p in FLEX_INNER:
        FLEX_TEMPLATES.append(template(f"flex_inpad_{_p}_{_axis}", _pattern, _axis, _p, "none", "pad"))
        FLEX_TEMPLATES.append(template(f"flex_incenter_{_p}_{_axis}", _pattern, _axis, _p, "none", "center"))
    for _inner in (False, True):
        FLEX_TEMPLATES.append(template(f"flex_nested_{_inner}_{_axis}", _nested, _axis, _inner))


# ── 2. Main Axis ────────────────────────────────────────────────────────

MAIN_TEXT = {
    "start": "start", "end": "end", "center": "center",
    "spaceBetween": "spaceBetween", "spaceAround": "spaceAround", "spaceEvenly": "spaceEvenly",
}


def _main_n(rng: random.Random, axis: str, align: str, n: int, ask_last: bool):
    """`n` fixed Boxes under one MainAxisAlignment; ask where one of them starts (or ends)."""
    ids = LETTERS[:n]
    total = 0
    kids = []
    for i in ids:
        s = rng.choice((30, 40, 50, 60, 70, 80, 100))
        total += s
        kids.append(mbox(axis, i, s))
    if total >= avail(axis):
        raise Retry
    root = flex(axis, kids, main=align, mark_main=True)
    a = along(axis)
    target = ids[-1] if ask_last else ids[1]
    prop = a["start"] if rng.random() < 0.7 else a["end"]
    return item(root, target, prop, ["flex", "main", "pos"])


def _main_min(rng: random.Random, axis: str):
    """Center(Row(mainAxisSize: min ...)): no free space inside the Row, so the alignment changes nothing."""
    sizes = [rng.choice((40, 50, 60, 80, 100)) for _ in range(3)]
    kids = [mbox(axis, i, s) for i, s in zip("abc", sizes)]
    align = rng.choice(ALIGNS)
    root = AlignN(0, 0, flex(axis, kids, main=align, main_size="min", mark_main=True), center=True)
    return item(root, rng.choice("bc"), along(axis)["start"], ["flex", "main", "pos", "align", "tight"])


def _main_expanded(rng: random.Random, axis: str):
    """An Expanded child eats all the free space, so the alignment changes nothing."""
    f = rng.choice((40, 60, 80, 100))
    align = rng.choice(ALIGNS[1:])
    kids = [mbox(axis, "a", f), Expanded(mbox(axis, "b", 50)), mbox(axis, "c", rng.choice((40, 60, 80)))]
    root = flex(axis, kids, main=align, mark_main=True)
    return item(root, "c", along(axis)["start"], ["flex", "main", "pos"])


def _main_padded(rng: random.Random, axis: str, align: str):
    p = rng.choice((10, 20, 25, 50))
    sizes = [rng.choice((40, 60, 80)) for _ in range(3)]
    if sum(sizes) > avail(axis) - 2 * p:  # no overflow stripes in a question about positions
        raise Retry
    kids = [mbox(axis, i, s) for i, s in zip("abc", sizes)]
    root = PadN(p, p, p, p, flex(axis, kids, main=align, mark_main=True))
    return item(root, rng.choice("ac"), along(axis)["start"], ["pad", "flex", "main", "pos"])


def _main_single(rng: random.Random, axis: str, align: str):
    root = flex(axis, [mbox(axis, "a", rng.choice((40, 50, 60, 100)))], main=align, mark_main=True)
    return item(root, "a", along(axis)["start"], ["flex", "main", "pos"])


MAIN_TEMPLATES: list[Maker] = []
for _axis in AXES:
    for _align in ALIGNS:
        MAIN_TEMPLATES.append(template(f"main_three_{_align}_{_axis}", _main_n, _axis, _align, 3, False))
        MAIN_TEMPLATES.append(template(f"main_four_{_align}_{_axis}", _main_n, _axis, _align, 4, True))
    MAIN_TEMPLATES.append(template(f"main_min_{_axis}", _main_min, _axis))
    MAIN_TEMPLATES.append(template(f"main_expanded_{_axis}", _main_expanded, _axis))
    MAIN_TEMPLATES.append(template(f"main_padded_{_axis}", lambda rng, axis: _main_padded(rng, axis, rng.choice(ALIGNS)), _axis))
    for _align in ("spaceBetween", "spaceAround", "spaceEvenly"):
        MAIN_TEMPLATES.append(template(f"main_single_{_align}_{_axis}", _main_single, _axis, _align))


# ── 3. Cross Axis ───────────────────────────────────────────────────────

CROSS = ("start", "end", "center", "stretch")


def _cbox(axis: str, id_: str, main: float, cross: float) -> BoxN:
    return mbox(axis, id_, main, cross)


def _cross_direct(rng: random.Random, axis: str, cross: str):
    """The Row/Column fills the screen across; ask where a Box sits across it."""
    crosses = [rng.choice((30, 50, 60, 80, 100, 120)) for _ in range(3)]
    kids = [_cbox(axis, i, rng.choice((40, 50, 60)), c) for i, c in zip("abc", crosses)]
    root = flex(axis, kids, cross=cross, mark_cross=True)
    t = rng.choice("abc")
    c = across(axis)
    prop = c["size"] if cross == "stretch" else rng.choice((c["start"], c["start"], c["end"]))
    return item(root, t, prop, ["flex", "cross", "tight"])


def _cross_loose(rng: random.Random, axis: str, cross: str):
    """Center(Row(...)): the Row is only as tall as its tallest child, and sits in the middle of the screen."""
    crosses = [rng.choice((40, 60, 80, 100)) for _ in range(3)]
    kids = [_cbox(axis, i, rng.choice((40, 50, 60)), c) for i, c in zip("abc", crosses)]
    root = AlignN(0, 0, flex(axis, kids, cross=cross, mark_cross=True), center=True)
    c = across(axis)
    prop = c["size"] if cross == "stretch" else rng.choice((c["start"], c["start"], c["end"]))
    return item(root, rng.choice("abc"), prop, ["flex", "cross", "tight", "align"])


def _cross_sized(rng: random.Random, axis: str, cross: str):
    """Center(SizedBox(height: H, child: Row(...))): the SizedBox fixes how tall the Row is."""
    big = rng.choice((100, 120, 160, 200)) if axis == "row" else rng.choice((120, 160, 200, 300))
    kids = [_cbox(axis, i, rng.choice((40, 50, 60)), rng.choice((30, 50, 60, 80))) for i in "ab"]
    row = flex(axis, kids, cross=cross, mark_cross=True)
    sized = SizedN(None, big, row) if axis == "row" else SizedN(big, None, row)
    c = across(axis)
    prop = c["size"] if cross == "stretch" else rng.choice((c["start"], c["end"]))
    return item(AlignN(0, 0, sized, center=True), rng.choice("ab"), prop, ["flex", "cross", "tight", "align"])


def _cross_nested(rng: random.Random, axis: str, cross: str):
    """A Box next to a shrink-wrapped Column of two Boxes: the Column's height decides the Row's."""
    other = "column" if axis == "row" else "row"
    inner = flex(other, [_cbox(other, "b", 50, 50), _cbox(other, "c", rng.choice((50, 50, 30, 60)), 50)], main_size="min")
    a = _cbox(axis, "a", 50, rng.choice((30, 40, 60)))
    root = AlignN(0, 0, flex(axis, [a, inner], cross=cross, mark_cross=cross != "center"), center=True)
    c = across(axis)
    prop = c["size"] if cross == "stretch" else c["start"]
    return item(root, "a", prop, ["flex", "cross", "tight", "align"])


def _cross_size_of_flex(rng: random.Random, axis: str, main_size: str):
    """Ask how big the Row itself is: as tall as its tallest child, and wide as the screen unless mainAxisSize.min."""
    kids = [_cbox(axis, i, rng.choice((40, 50, 60, 80)), rng.choice((30, 50, 70, 90))) for i in "abc"]
    row = flex(axis, kids, main_size=main_size)
    row.id = "r"
    root = AlignN(0, 0, row, center=True)
    c = across(axis)
    a = along(axis)
    prop = rng.choice((c["size"], a["size"]))
    return item(root, "r", prop, ["flex", "cross", "tight", "align"], comment=f"// {'width' if prop == 'w' else 'height'} of r")


CROSS_TEMPLATES: list[Maker] = []
for _axis in AXES:
    for _cross in CROSS:
        CROSS_TEMPLATES.append(template(f"cross_direct_{_cross}_{_axis}", _cross_direct, _axis, _cross))
        CROSS_TEMPLATES.append(template(f"cross_loose_{_cross}_{_axis}", _cross_loose, _axis, _cross))
        CROSS_TEMPLATES.append(template(f"cross_sized_{_cross}_{_axis}", _cross_sized, _axis, _cross))
        CROSS_TEMPLATES.append(template(f"cross_nested_{_cross}_{_axis}", _cross_nested, _axis, _cross))
    for _ms in ("max", "min"):
        CROSS_TEMPLATES.append(template(f"cross_size_{_ms}_{_axis}", _cross_size_of_flex, _axis, _ms))
