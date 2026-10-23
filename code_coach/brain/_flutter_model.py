"""Hand-built models of Flutter's box layout, for the Flutter packs (the sibling of `_dart_model.py`).

Nothing here asks Flutter anything. A widget tree is built from the small node classes below, and the SAME tree
does two jobs: `dart()` prints it as the Flutter code the learner reads, and `layout()` works out its sizes and
positions by Flutter's own rules (constraints go down, sizes go up, the parent sets the position). The rules are the
ones of the render objects - RenderFlex, RenderPadding, RenderPositionedBox, RenderConstrainedBox, RenderStack,
RenderWrap, RenderAspectRatio... - written out by hand. tests/flutter_oracle.py then builds every item in a real
Flutter test (the oracle rule), so a wrong rule here is a failing test.

THE HOST every item sits in: the app's view is 400 x 300 logical pixels, and the root widget is given TIGHT 400 x 300
constraints, as a real app's root is (`host()`).

Numbers: sizes are Python floats; `fnum` prints a whole one as an integer (`120`) and any other the Dart way (`96.5`),
which is exactly what the Flutter oracle's `emit` prints.

Notes: while it lays out, a node may leave a plain-English `note` under a TOPIC ("flex", "main", "cross", "pad",
"tight", "stack", "wrap", "aspect", "overflow", "host"); `explain(root, id, topics)` joins the notes of the nodes on the
path from the root to the widget with that id, which is how each item explains its own numbers.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from .items import Item
from ._model import Maker

INF = float("inf")
SCREEN_W, SCREEN_H = 400.0, 300.0
EPS = 1e-10


def fnum(v: float) -> str:
    """How the Flutter oracle prints a measurement: 120 for a whole number, else Dart's shortest form (96.5)."""
    v = float(v)
    if v == INF:
        return "unlimited"
    if v == int(v):
        return str(int(v))
    return repr(v)


def dnum(v: float) -> str:
    """A number as Dart source: ints stay ints, 62.5 stays 62.5."""
    return fnum(v)


# ── Constraints ─────────────────────────────────────────────────────────

def _clamp(x: float, lo: float, hi: float) -> float:
    return min(max(x, lo), hi)


@dataclass(frozen=True)
class BC:
    """BoxConstraints."""
    minw: float = 0.0
    maxw: float = INF
    minh: float = 0.0
    maxh: float = INF

    @staticmethod
    def tight(w: float, h: float) -> "BC":
        return BC(w, w, h, h)

    @staticmethod
    def tight_for(w: float | None = None, h: float | None = None) -> "BC":
        return BC(0.0 if w is None else w, INF if w is None else w, 0.0 if h is None else h, INF if h is None else h)

    @staticmethod
    def expand() -> "BC":
        return BC(INF, INF, INF, INF)

    @property
    def is_tight(self) -> bool:
        return self.minw >= self.maxw and self.minh >= self.maxh

    @property
    def bounded_w(self) -> bool:
        return self.maxw < INF

    @property
    def bounded_h(self) -> bool:
        return self.maxh < INF

    def constrain(self, w: float, h: float) -> tuple[float, float]:
        return _clamp(w, self.minw, self.maxw), _clamp(h, self.minh, self.maxh)

    def loosen(self) -> "BC":
        return BC(0.0, self.maxw, 0.0, self.maxh)

    def deflate(self, l: float, t: float, r: float, b: float) -> "BC":
        hor, ver = l + r, t + b
        minw, minh = max(0.0, self.minw - hor), max(0.0, self.minh - ver)
        return BC(minw, max(minw, self.maxw - hor), minh, max(minh, self.maxh - ver))

    def enforce(self, outer: "BC") -> "BC":
        """self squeezed into outer's range (BoxConstraints.enforce)."""
        return BC(_clamp(self.minw, outer.minw, outer.maxw), _clamp(self.maxw, outer.minw, outer.maxw),
                  _clamp(self.minh, outer.minh, outer.maxh), _clamp(self.maxh, outer.minh, outer.maxh))

    def tighten(self, w: float | None = None, h: float | None = None) -> "BC":
        return BC(self.minw if w is None else _clamp(w, self.minw, self.maxw),
                  self.maxw if w is None else _clamp(w, self.minw, self.maxw),
                  self.minh if h is None else _clamp(h, self.minh, self.maxh),
                  self.maxh if h is None else _clamp(h, self.minh, self.maxh))


@dataclass
class Ctx:
    """What a layout leaves behind: the rectangle of every keyed widget, and whether a RenderFlex overflowed."""
    rects: dict[str, tuple[float, float, float, float]] = field(default_factory=dict)
    overflow: bool = False


# ── The nodes ───────────────────────────────────────────────────────────

class Node:
    """A widget. `call()` is how it is written in Dart; `layout(c)` returns its size; `kids()` its child widgets."""
    id: str | None = None
    #: How a keyed widget is spelled in the code: Box('a') has the id inside, the others get `key: Key('a')`.
    boxy = False

    def __init__(self) -> None:
        self.size: tuple[float, float] = (0.0, 0.0)
        self.notes: list[tuple[str, str]] = []
        self.placed: list[tuple["Node", float, float]] = []

    # printing
    def call(self) -> tuple[str, list[Any], list[tuple[str, Any]]]:
        raise NotImplementedError

    def kids(self) -> list["Node"]:
        return []

    # layout
    def layout(self, c: BC) -> tuple[float, float]:
        raise NotImplementedError

    def note(self, topic: str, text: str) -> None:
        self.notes.append((topic, text))

    def paint(self, x: float, y: float, ctx: Ctx) -> None:
        if self.id:
            ctx.rects[self.id] = (x, y, self.size[0], self.size[1])
        for child, dx, dy in self.placed:
            child.paint(x + dx, y + dy, ctx)

    def reset(self) -> None:
        self.notes = []
        self.placed = []
        for k in self.kids():
            k.reset()

    def key_named(self, id_: str) -> "Node":
        self.id = id_
        return self


def _key_arg(n: Node) -> list[tuple[str, Any]]:
    return [("key", f"Key('{n.id}')")] if n.id else []


class BoxN(Node):
    """`Box('a', w: 100, h: 40)`: a SizedBox with that size (50 x 50 unless said), measured by its id."""
    boxy = True

    def __init__(self, id_: str, w: float = 50.0, h: float = 50.0) -> None:
        super().__init__()
        self.id, self.w, self.h = id_, float(w), float(h)

    def call(self):
        named = []
        if self.w != 50:
            named.append(("w", dnum(self.w)))
        if self.h != 50:
            named.append(("h", dnum(self.h)))
        return "Box", [f"'{self.id}'"], named

    def layout(self, c: BC):
        self.size = c.constrain(self.w, self.h)
        if self.size != (self.w, self.h):
            self.note("tight", f"{self.id} wants {fnum(self.w)} x {fnum(self.h)} but its parent only allows "
                               f"{_range(c.minw, c.maxw)} wide and {_range(c.minh, c.maxh)} tall, so it becomes "
                               f"{fnum(self.size[0])} x {fnum(self.size[1])}.")
        return self.size


def _range(lo: float, hi: float) -> str:
    if lo == hi:
        return f"exactly {fnum(lo)}"
    return f"{fnum(lo)} to {'any size' if hi == INF else fnum(hi)}"


class SizedN(Node):
    """`SizedBox(width: 200, height: 100, child: x)`."""

    def __init__(self, w: float | None, h: float | None, child: Node | None, square: bool = False) -> None:
        super().__init__()
        self.w, self.h, self.child, self.square = w, h, child, square

    def call(self):
        if self.square:
            return "SizedBox.square", [], [("dimension", dnum(self.w))] + ([("child", self.child)] if self.child else [])
        named = []
        if self.w is not None:
            named.append(("width", dnum(self.w)))
        if self.h is not None:
            named.append(("height", dnum(self.h)))
        if self.child:
            named.append(("child", self.child))
        return "SizedBox", [], named + _key_arg(self)

    def kids(self):
        return [self.child] if self.child else []

    def layout(self, c: BC):
        cc = BC.tight_for(self.w, self.h).enforce(c)
        if self.child is None:
            self.size = cc.constrain(0.0, 0.0)
            return self.size
        self.size = self.child.layout(cc)
        self.placed = [(self.child, 0.0, 0.0)]
        want = f"{fnum(self.w) if self.w is not None else 'any'} x {fnum(self.h) if self.h is not None else 'any'}"
        self.note("tight", f"The SizedBox ({want}) gives its child tight "
                           f"{_dims(cc)}.")
        return self.size


def _dims(c: BC) -> str:
    """A constraint's width and height, in words."""
    return f"{_range(c.minw, c.maxw)} wide and {_range(c.minh, c.maxh)} tall" if not c.is_tight else \
        f"{fnum(c.minw)} x {fnum(c.minh)}"


class PadN(Node):
    """`Padding(padding: EdgeInsets..., child: x)`."""

    def __init__(self, l: float, t: float, r: float, b: float, child: Node, style: str = "auto") -> None:
        super().__init__()
        self.l, self.t, self.r, self.b, self.child, self.style = float(l), float(t), float(r), float(b), child, style

    def insets(self) -> str:
        l, t, r, b = self.l, self.t, self.r, self.b
        style = self.style
        if style == "auto":
            style = "all" if l == t == r == b else "sym" if (l == r and t == b) else "only"
        if style == "all":
            return f"EdgeInsets.all({dnum(l)})"
        if style == "sym":
            parts = [(k, v) for k, v in (("horizontal", l), ("vertical", t)) if v]
            return "EdgeInsets.symmetric(" + ", ".join(f"{k}: {dnum(v)}" for k, v in parts) + ")"
        if style == "ltrb":
            return f"EdgeInsets.fromLTRB({dnum(l)}, {dnum(t)}, {dnum(r)}, {dnum(b)})"
        parts = [(k, v) for k, v in (("left", l), ("top", t), ("right", r), ("bottom", b)) if v]
        return "EdgeInsets.only(" + ", ".join(f"{k}: {dnum(v)}" for k, v in parts) + ")"

    def call(self):
        return "Padding", [], [("padding", self.insets()), ("child", self.child)] + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        cw, ch = self.child.layout(c.deflate(self.l, self.t, self.r, self.b))
        self.size = c.constrain(self.l + self.r + cw, self.t + self.b + ch)
        self.placed = [(self.child, self.l, self.t)]
        self.note("pad", f"Padding takes {fnum(self.l + self.r)} off the width and {fnum(self.t + self.b)} off the "
                         f"height, and puts its child {fnum(self.l)} from the left and {fnum(self.t)} from the top.")
        return self.size


ALIGNMENTS = {
    (-1.0, -1.0): "topLeft", (0.0, -1.0): "topCenter", (1.0, -1.0): "topRight",
    (-1.0, 0.0): "centerLeft", (0.0, 0.0): "center", (1.0, 0.0): "centerRight",
    (-1.0, 1.0): "bottomLeft", (0.0, 1.0): "bottomCenter", (1.0, 1.0): "bottomRight",
}


def alignment_dart(ax: float, ay: float) -> str:
    name = ALIGNMENTS.get((float(ax), float(ay)))
    return f"Alignment.{name}" if name else f"Alignment({dnum(ax)}, {dnum(ay)})"


class AlignN(Node):
    """`Center(child: x)` or `Align(alignment: ..., child: x)`, with optional width/height factors."""

    def __init__(self, ax: float, ay: float, child: Node, center: bool = False, wf: float | None = None,
                 hf: float | None = None) -> None:
        super().__init__()
        self.ax, self.ay, self.child, self.center, self.wf, self.hf = float(ax), float(ay), child, center, wf, hf

    def call(self):
        named: list[tuple[str, Any]] = []
        name = "Center" if self.center else "Align"
        if not self.center:
            named.append(("alignment", alignment_dart(self.ax, self.ay)))
        if self.wf is not None:
            named.append(("widthFactor", dnum(self.wf)))
        if self.hf is not None:
            named.append(("heightFactor", dnum(self.hf)))
        named.append(("child", self.child))
        return name, [], named + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        cw, ch = self.child.layout(c.loosen())
        shrink_w = self.wf is not None or not c.bounded_w
        shrink_h = self.hf is not None or not c.bounded_h
        w = cw * (1.0 if self.wf is None else self.wf) if shrink_w else INF
        h = ch * (1.0 if self.hf is None else self.hf) if shrink_h else INF
        self.size = c.constrain(w, h)
        dx = (self.size[0] - cw) * (self.ax + 1) / 2
        dy = (self.size[1] - ch) * (self.ay + 1) / 2
        self.placed = [(self.child, dx, dy)]
        self.note("tight", f"Center/Align hands its child a LOOSE version of its own constraints (anything from 0 up to "
                           f"{fnum(c.maxw)} x {fnum(c.maxh)}), then grows to fill the space.")
        self.note("align", f"The child is {fnum(cw)} x {fnum(ch)} in a space of {fnum(self.size[0])} x "
                           f"{fnum(self.size[1])}, so the left over is {fnum(self.size[0] - cw)} x "
                           f"{fnum(self.size[1] - ch)}, split by the alignment: {fnum(dx)} from the left, "
                           f"{fnum(dy)} from the top.")
        return self.size


class ConstrainedN(Node):
    """`ConstrainedBox(constraints: BoxConstraints(...), child: x)`."""

    def __init__(self, bc: BC, child: Node, style: str = "plain") -> None:
        super().__init__()
        self.bc, self.child, self.style = bc, child, style

    def bc_dart(self) -> str:
        bc = self.bc
        if self.style == "tightFor":
            parts = []
            if bc.minw == bc.maxw:
                parts.append(f"width: {dnum(bc.minw)}")
            if bc.minh == bc.maxh:
                parts.append(f"height: {dnum(bc.minh)}")
            return "BoxConstraints.tightFor(" + ", ".join(parts) + ")"
        if self.style == "tight":
            return f"BoxConstraints.tight(Size({dnum(bc.minw)}, {dnum(bc.minh)}))"
        if self.style == "loose":
            return f"BoxConstraints.loose(Size({dnum(bc.maxw)}, {dnum(bc.maxh)}))"
        parts = []
        for name, v, default in (("minWidth", bc.minw, 0.0), ("maxWidth", bc.maxw, INF),
                                 ("minHeight", bc.minh, 0.0), ("maxHeight", bc.maxh, INF)):
            if v != default:
                parts.append(f"{name}: {dnum(v)}")
        return "BoxConstraints(" + ", ".join(parts) + ")"

    def call(self):
        return "ConstrainedBox", [], [("constraints", self.bc_dart()), ("child", self.child)] + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        cc = self.bc.enforce(c)
        self.size = self.child.layout(cc)
        self.placed = [(self.child, 0.0, 0.0)]
        self.note("tight", f"ConstrainedBox adds its own limits to the ones it was given; the child may be "
                           f"{_dims(cc)}.")
        return self.size


class UnconstrainedN(Node):
    """`UnconstrainedBox(child: x)`: the child may be any size; the box itself obeys its parent and centres the child."""

    def __init__(self, child: Node) -> None:
        super().__init__()
        self.child = child

    def call(self):
        return "UnconstrainedBox", [], [("child", self.child)] + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        cw, ch = self.child.layout(BC())
        self.size = c.constrain(cw, ch)
        self.placed = [(self.child, (self.size[0] - cw) / 2, (self.size[1] - ch) / 2)]
        self.note("tight", "UnconstrainedBox lets the child be any size it likes (no limits at all), then "
                           "shrinks itself to fit its own parent and centres the child.")
        return self.size


class AspectN(Node):
    """`AspectRatio(aspectRatio: 2, child: x)`."""

    def __init__(self, ratio: float, child: Node) -> None:
        super().__init__()
        self.ratio, self.child = float(ratio), child

    def call(self):
        return "AspectRatio", [], [("aspectRatio", dnum(self.ratio)), ("child", self.child)] + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        if c.is_tight:
            w, h = c.minw, c.minh
            self.note("aspect", "Tight constraints leave AspectRatio no choice: it takes exactly that size.")
        else:
            width = c.maxw
            if width < INF:
                height = width / self.ratio
            else:
                height = c.maxh
                width = height * self.ratio
            if width > c.maxw:
                width, height = c.maxw, c.maxw / self.ratio
            if width < c.minw:
                width, height = c.minw, c.minw / self.ratio
            if height > c.maxh:
                height, width = c.maxh, c.maxh * self.ratio
            if height < c.minh:
                height, width = c.minh, c.minh * self.ratio
            w, h = c.constrain(width, height)
            self.note("aspect", f"AspectRatio takes the widest width it may ({fnum(c.maxw)}), makes the height "
                                f"width / ratio, and if that is too tall it takes the tallest height instead "
                                f"({fnum(c.maxh)}) and derives the width: {fnum(w)} x {fnum(h)}.")
        self.size = (w, h)
        self.child.layout(BC.tight(w, h))
        self.placed = [(self.child, 0.0, 0.0)]
        return self.size


class FractionalN(Node):
    """`FractionallySizedBox(widthFactor: .5, child: x)`: tight fractions of the parent's maximum, child centred."""

    def __init__(self, wf: float | None, hf: float | None, child: Node) -> None:
        super().__init__()
        self.wf, self.hf, self.child = wf, hf, child

    def call(self):
        named = []
        if self.wf is not None:
            named.append(("widthFactor", dnum(self.wf)))
        if self.hf is not None:
            named.append(("heightFactor", dnum(self.hf)))
        return "FractionallySizedBox", [], named + [("child", self.child)] + _key_arg(self)

    def kids(self):
        return [self.child]

    def layout(self, c: BC):
        minw, maxw, minh, maxh = c.minw, c.maxw, c.minh, c.maxh
        if self.wf is not None:
            minw = maxw = maxw * self.wf
        if self.hf is not None:
            minh = maxh = maxh * self.hf
        cw, ch = self.child.layout(BC(minw, maxw, minh, maxh))
        self.size = c.constrain(cw, ch)
        self.placed = [(self.child, (self.size[0] - cw) / 2, (self.size[1] - ch) / 2)]
        self.note("tight", f"FractionallySizedBox gives its child tight constraints of {fnum(minw) if self.wf is not None else 'the parent range'}"
                           f" wide and {fnum(minh) if self.hf is not None else 'the parent range'} tall: that fraction of the "
                           f"parent's maximum.")
        return self.size


class FillN(Node):
    """What a Container with no child and no tight size becomes: LimitedBox(0) around ConstrainedBox.expand()."""

    def __init__(self) -> None:
        super().__init__()

    def call(self):
        return "SizedBox.expand", [], []

    def layout(self, c: BC):
        lim = BC(c.minw, c.maxw if c.bounded_w else _clamp(0.0, c.minw, INF), c.minh,
                 c.maxh if c.bounded_h else _clamp(0.0, c.minh, INF))
        cc = BC.expand().enforce(lim)
        self.size = c.constrain(*cc.constrain(0.0, 0.0))
        return self.size


class ContainerN(Node):
    """`Container(width:, height:, margin:, padding:, alignment:, constraints:, child:)`, built the way Flutter builds
    it: child -> Align -> Padding -> ConstrainedBox -> margin Padding. A Container with no child is a box that fills."""

    def __init__(self, child: Node | None = None, width: float | None = None, height: float | None = None,
                 margin: tuple[float, float, float, float] | None = None,
                 padding: tuple[float, float, float, float] | None = None,
                 alignment: tuple[float, float] | None = None, constraints: BC | None = None,
                 color: bool = False) -> None:
        super().__init__()
        self.child, self.width, self.height = child, width, height
        self.margin, self.padding, self.alignment, self.constraints, self.color = margin, padding, alignment, constraints, color
        self.chain: Node | None = None

    def _constraints(self) -> BC | None:
        if self.width is not None or self.height is not None:
            return (self.constraints or BC()).tighten(self.width, self.height)
        return self.constraints

    def build(self) -> Node:
        """The widgets Container is made of (the same objects are reused, so positions can be read back)."""
        current: Node | None = self.child
        cons = self._constraints()
        if self.child is None and (cons is None or not cons.is_tight):
            current = FillN()
        elif self.alignment is not None:
            current = AlignN(self.alignment[0], self.alignment[1], current)
        if self.padding is not None:
            current = PadN(*self.padding, current)
        if cons is not None:
            current = _ConstrainedMaybeChild(cons, current)
        if self.margin is not None:
            current = PadN(*self.margin, current)
        assert current is not None
        return current

    def call(self):
        named: list[tuple[str, Any]] = []
        if self.width is not None:
            named.append(("width", dnum(self.width)))
        if self.height is not None:
            named.append(("height", dnum(self.height)))
        if self.constraints is not None:
            named.append(("constraints", ConstrainedN(self.constraints, BoxN("x")).bc_dart()))
        if self.margin is not None:
            named.append(("margin", PadN(*self.margin, BoxN("x")).insets()))
        if self.padding is not None:
            named.append(("padding", PadN(*self.padding, BoxN("x")).insets()))
        if self.alignment is not None:
            named.append(("alignment", alignment_dart(*self.alignment)))
        if self.color:
            named.append(("color", "Colors.blue"))
        if self.child is not None:
            named.append(("child", self.child))
        return "Container", [], named + _key_arg(self)

    def kids(self):
        return [self.child] if self.child else []

    def layout(self, c: BC):
        self.chain = self.build()
        self.size = self.chain.layout(c)
        self.placed = [(self.chain, 0.0, 0.0)]
        return self.size

    def paint(self, x: float, y: float, ctx: Ctx) -> None:
        if self.id:
            ctx.rects[self.id] = (x, y, self.size[0], self.size[1])
        if self.chain is not None:
            self.chain.paint(x, y, ctx)

    def reset(self) -> None:
        super().reset()
        self.chain = None

    def inner_notes(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []

        def walk(n: Node) -> None:
            if n is self.child:
                return
            out.extend(n.notes)
            for child, _, _ in n.placed:
                walk(child)

        if self.chain is not None:
            walk(self.chain)
        return out


class _ConstrainedMaybeChild(Node):
    """ConstrainedBox(constraints, child) where the child may be absent (a Container of exactly width x height)."""

    def __init__(self, bc: BC, child: Node | None) -> None:
        super().__init__()
        self.bc, self.child = bc, child

    def call(self):
        raise AssertionError("never printed")

    def layout(self, c: BC):
        cc = self.bc.enforce(c)
        if self.child is None:
            self.size = cc.constrain(0.0, 0.0)
            return self.size
        self.size = self.child.layout(cc)
        self.placed = [(self.child, 0.0, 0.0)]
        self.note("tight", f"Container's width and height become tight constraints on its child: {_dims(cc)}.")
        return self.size


# ── Flex: Row and Column ────────────────────────────────────────────────

MAIN_ALIGN = ("start", "end", "center", "spaceBetween", "spaceAround", "spaceEvenly")
CROSS_ALIGN = ("start", "end", "center", "stretch")


class FlexKid(Node):
    """`Expanded(flex: 2, child: x)`, `Flexible(flex:, fit: FlexFit.loose, child: x)` or `Spacer(flex: 2)`."""

    def __init__(self, child: Node | None, flex: int = 1, loose: bool = False, spacer: bool = False) -> None:
        super().__init__()
        self.child, self.flex, self.loose, self.spacer = child, flex, loose, spacer

    def call(self):
        named: list[tuple[str, Any]] = []
        if self.flex != 1:
            named.append(("flex", str(self.flex)))
        if self.spacer:
            return "Spacer", [], named
        if self.loose:
            named.append(("fit", "FlexFit.loose"))
            return "Flexible", [], named + [("child", self.child)]
        return "Expanded", [], named + [("child", self.child)]

    def kids(self):
        return [self.child] if self.child else []

    def layout(self, c: BC):
        if self.child is None:
            self.size = c.constrain(0.0, 0.0)
            return self.size
        self.size = self.child.layout(c)
        self.placed = [(self.child, 0.0, 0.0)]
        return self.size


def Expanded(child: Node, flex: int = 1) -> FlexKid:
    return FlexKid(child, flex)


def Flexible(child: Node, flex: int = 1) -> FlexKid:
    return FlexKid(child, flex, loose=True)


def Spacer(flex: int = 1) -> FlexKid:
    return FlexKid(None, flex, spacer=True)


class FlexN(Node):
    """`Row` / `Column`, as RenderFlex lays them out (left-to-right, top-to-bottom)."""

    def __init__(self, axis: str, kids: list[Node], main: str = "start", cross: str = "center",
                 main_size: str = "max", mark_main: bool = False, mark_cross: bool = False) -> None:
        super().__init__()
        assert axis in ("row", "column")
        self.axis, self.items, self.main, self.cross, self.main_size = axis, kids, main, cross, main_size
        #: Whether the code spells out the alignment even when it is the default.
        self.mark_main, self.mark_cross = mark_main, mark_cross
        self.overflowed = 0.0
        self.allocated = self.actual_main = 0.0

    def call(self):
        named: list[tuple[str, Any]] = []
        if self.main != "start" or self.mark_main:
            named.append(("mainAxisAlignment", f"MainAxisAlignment.{self.main}"))
        if self.cross != "center" or self.mark_cross:
            named.append(("crossAxisAlignment", f"CrossAxisAlignment.{self.cross}"))
        if self.main_size != "max":
            named.append(("mainAxisSize", "MainAxisSize.min"))
        named.append(("children", self.items))
        return ("Row" if self.axis == "row" else "Column"), [], named + _key_arg(self)

    def kids(self):
        return list(self.items)

    def layout(self, c: BC):
        row = self.axis == "row"
        name = "Row" if row else "Column"
        mw = (lambda w, h: w) if row else (lambda w, h: h)  # main extent of a size
        cr = (lambda w, h: h) if row else (lambda w, h: w)  # cross extent
        max_main = c.maxw if row else c.maxh
        max_cross = c.maxh if row else c.maxw
        can_flex = max_main < INF
        stretch = self.cross == "stretch"
        sizes: list[tuple[float, float]] = [(0.0, 0.0)] * len(self.items)

        def cons(min_main: float, max_main_: float) -> BC:
            cmin = max_cross if stretch else 0.0
            if row:
                return BC(min_main, max_main_, cmin, max_cross)
            return BC(cmin, max_cross, min_main, max_main_)

        total_flex = 0
        allocated = 0.0
        cross_size = 0.0
        last_flex = None
        for i, k in enumerate(self.items):
            flex = k.flex if isinstance(k, FlexKid) else 0
            if flex > 0:
                total_flex += flex
                last_flex = i
            else:
                s = k.layout(cons(0.0, INF))
                sizes[i] = s
                allocated += mw(*s)
                cross_size = max(cross_size, cr(*s))
        inflexible = allocated
        free = max(0.0, (max_main if can_flex else 0.0) - allocated)
        per = free / total_flex if (can_flex and total_flex > 0) else float("nan")
        allocated_flex = 0.0
        for i, k in enumerate(self.items):
            flex = k.flex if isinstance(k, FlexKid) else 0
            if flex <= 0:
                continue
            assert can_flex, "an Expanded in an unbounded Row or Column is an error in Flutter"
            max_extent = (free - allocated_flex) if i == last_flex else per * flex
            min_extent = 0.0 if k.loose else max_extent
            s = k.layout(cons(min_extent, max_extent))
            sizes[i] = s
            allocated += mw(*s)
            allocated_flex += max_extent
            cross_size = max(cross_size, cr(*s))
        ideal = max_main if (can_flex and self.main_size == "max") else allocated
        if row:
            self.size = c.constrain(ideal, cross_size)
        else:
            self.size = c.constrain(cross_size, ideal)
        actual_main = mw(*self.size)
        cross_size = cr(*self.size)
        delta = actual_main - allocated
        self.allocated, self.actual_main = allocated, actual_main
        self.overflowed = max(0.0, -delta)
        remaining = max(0.0, delta)
        n = len(self.items)
        leading = between = 0.0
        if self.main == "end":
            leading = remaining
        elif self.main == "center":
            leading = remaining / 2
        elif self.main == "spaceBetween":
            between = remaining / (n - 1) if n > 1 else 0.0
        elif self.main == "spaceAround":
            between = remaining / n if n > 0 else 0.0
            leading = between / 2
        elif self.main == "spaceEvenly":
            between = remaining / (n + 1)
            leading = between
        pos = leading
        self.placed = []
        for k, s in zip(self.items, sizes):
            ch = cr(*s)
            if self.cross == "end":
                cpos = cross_size - ch
            elif self.cross == "center":
                cpos = (cross_size - ch) / 2
            else:
                cpos = 0.0
            self.placed.append((k, pos, cpos) if row else (k, cpos, pos))
            pos += mw(*s) + between
        # the words
        fixed = inflexible
        if total_flex:
            self.note("flex", f"The {name} has {fnum(max_main)} to share. The children without flex take {fnum(fixed)}, "
                              f"which leaves {fnum(free)}; that is cut into {total_flex} equal part"
                              f"{'s' if total_flex != 1 else ''} of {fnum(per)}, and a child with flex f gets f parts.")
        else:
            self.note("flex", f"No child has a flex factor, so each keeps its own size on the {name}'s main axis.")
        if remaining or self.main != "start":
            self.note("main", f"The children use {fnum(allocated)} of the {fnum(actual_main)} along the main axis, "
                              f"so {fnum(remaining)} is left over; MainAxisAlignment.{self.main} puts "
                              f"{fnum(leading)} before the first child and {fnum(between)} between neighbours.")
        where = [f"{first_id(k)} at {fnum(dx if row else dy)}" for k, dx, dy in self.placed if first_id(k)]
        self.note("pos", f"Along the {'width' if row else 'height'} the children sit one after another, each starting "
                         f"where the last one ended: " + ", ".join(where) + ".")
        self.note("cross", f"The {name} is {fnum(cross_size)} across, and CrossAxisAlignment.{self.cross} "
                           + {"start": "puts every child at the start of that.",
                              "end": "puts every child's far edge at the far edge.",
                              "center": "centres every child across it.",
                              "stretch": "forces every child to the full size across."}[self.cross])
        if self.overflowed > EPS:
            self.note("overflow", f"The children need {fnum(allocated)} but the {name} is only {fnum(actual_main)}: "
                                  f"it overflows by {fnum(self.overflowed)}.")
        return self.size

    def has_overflow(self) -> bool:
        return self.overflowed > EPS


# ── Stack ───────────────────────────────────────────────────────────────

class PositionedN(Node):
    """`Positioned(left: 10, top: 20, child: x)` (a Stack's child)."""

    def __init__(self, child: Node, left: float | None = None, top: float | None = None, right: float | None = None,
                 bottom: float | None = None, width: float | None = None, height: float | None = None) -> None:
        super().__init__()
        self.child, self.left, self.top, self.right, self.bottom = child, left, top, right, bottom
        self.width, self.height = width, height

    def call(self):
        named = [(k, dnum(v)) for k, v in (("left", self.left), ("top", self.top), ("right", self.right),
                                           ("bottom", self.bottom), ("width", self.width), ("height", self.height))
                 if v is not None]
        return "Positioned", [], named + [("child", self.child)]

    def kids(self):
        return [self.child]

    def layout(self, c: BC):  # the Stack lays positioned children out itself
        raise AssertionError("a Positioned is laid out by its Stack")


class StackN(Node):
    """`Stack(alignment:, children: [...])`."""

    def __init__(self, kids: list[Node], ax: float = -1.0, ay: float = -1.0, mark_alignment: bool = False) -> None:
        super().__init__()
        self.items, self.ax, self.ay, self.mark_alignment = kids, float(ax), float(ay), mark_alignment

    def call(self):
        named: list[tuple[str, Any]] = []
        if (self.ax, self.ay) != (-1.0, -1.0) or self.mark_alignment:
            named.append(("alignment", alignment_dart(self.ax, self.ay)))
        named.append(("children", self.items))
        return "Stack", [], named + _key_arg(self)

    def kids(self):
        return list(self.items)

    def layout(self, c: BC):
        loose = c.loosen()
        plain = [k for k in self.items if not isinstance(k, PositionedN)]
        sizes: dict[int, tuple[float, float]] = {}
        w = h = 0.0
        for k in plain:
            s = k.layout(loose)
            sizes[id(k)] = s
            w, h = max(w, s[0]), max(h, s[1])
        if plain:
            self.size = c.constrain(w, h)
        else:
            self.size = (c.maxw, c.maxh)
        sw, sh = self.size
        self.placed = []
        for k in self.items:
            if isinstance(k, PositionedN):
                cc = BC()
                if k.left is not None and k.right is not None:
                    cc = cc.tighten(w=max(0.0, sw - k.right - k.left))
                elif k.width is not None:
                    cc = cc.tighten(w=k.width)
                if k.top is not None and k.bottom is not None:
                    cc = cc.tighten(h=max(0.0, sh - k.bottom - k.top))
                elif k.height is not None:
                    cc = cc.tighten(h=k.height)
                cw, ch = k.child.layout(cc)
                k.size = (cw, ch)
                if k.left is not None:
                    x = k.left
                elif k.right is not None:
                    x = sw - k.right - cw
                else:
                    x = (sw - cw) * (self.ax + 1) / 2
                if k.top is not None:
                    y = k.top
                elif k.bottom is not None:
                    y = sh - k.bottom - ch
                else:
                    y = (sh - ch) * (self.ay + 1) / 2
                k.placed = [(k.child, 0.0, 0.0)]
                self.placed.append((k, x, y))
            else:
                cw, ch = sizes[id(k)]
                self.placed.append((k, (sw - cw) * (self.ax + 1) / 2, (sh - ch) * (self.ay + 1) / 2))
        self.note("stack", f"The Stack is {fnum(sw)} x {fnum(sh)}. A Positioned child sits where left/top/right/bottom "
                           f"say, measured from the Stack's own edges; a child without Positioned goes where the "
                           f"Stack's alignment says.")
        return self.size


# ── Wrap ────────────────────────────────────────────────────────────────

WRAP_ALIGN = ("start", "end", "center", "spaceBetween", "spaceAround", "spaceEvenly")


def _lead_between(kind: str, free: float, n: int) -> tuple[float, float]:
    """WrapAlignment: (space before the first, space between neighbours) for `n` items and `free` left over."""
    free = max(0.0, free)
    if kind == "start":
        return 0.0, 0.0
    if kind == "end":
        return free, 0.0
    if kind == "center":
        return free / 2, 0.0
    if kind == "spaceBetween":
        return 0.0, (free / (n - 1) if n > 1 else 0.0)
    if kind == "spaceAround":
        between = free / n if n else 0.0
        return between / 2, between
    between = free / (n + 1)
    return between, between


class WrapN(Node):
    """`Wrap(spacing:, runSpacing:, children: [...])` (horizontal, or vertical when `vertical`)."""

    def __init__(self, kids: list[Node], spacing: float = 0.0, run_spacing: float = 0.0, align: str = "start",
                 run_align: str = "start", cross_align: str = "start", vertical: bool = False) -> None:
        super().__init__()
        self.items, self.spacing, self.run_spacing = kids, float(spacing), float(run_spacing)
        self.align, self.run_align, self.cross_align, self.vertical = align, run_align, cross_align, vertical
        self.runs: list[list[int]] = []

    def call(self):
        named: list[tuple[str, Any]] = []
        if self.vertical:
            named.append(("direction", "Axis.vertical"))
        if self.spacing:
            named.append(("spacing", dnum(self.spacing)))
        if self.run_spacing:
            named.append(("runSpacing", dnum(self.run_spacing)))
        if self.align != "start":
            named.append(("alignment", f"WrapAlignment.{self.align}"))
        if self.run_align != "start":
            named.append(("runAlignment", f"WrapAlignment.{self.run_align}"))
        if self.cross_align != "start":
            named.append(("crossAxisAlignment", f"WrapCrossAlignment.{self.cross_align}"))
        named.append(("children", self.items))
        return "Wrap", [], named + _key_arg(self)

    def kids(self):
        return list(self.items)

    def layout(self, c: BC):
        v = self.vertical
        limit = c.maxh if v else c.maxw
        child_c = BC(0.0, INF, 0.0, c.maxh) if v else BC(0.0, c.maxw, 0.0, INF)
        main = (lambda s: s[1]) if v else (lambda s: s[0])
        cross = (lambda s: s[0]) if v else (lambda s: s[1])
        sizes = [k.layout(child_c) for k in self.items]
        runs: list[list[int]] = []
        run_main: list[float] = []
        run_cross: list[float] = []
        cur: list[int] = []
        cur_main = cur_cross = 0.0
        for i, s in enumerate(sizes):
            if cur and cur_main + self.spacing + main(s) > limit + 1e-10:
                runs.append(cur)
                run_main.append(cur_main)
                run_cross.append(cur_cross)
                cur, cur_main, cur_cross = [], 0.0, 0.0
            cur_main += main(s) + (self.spacing if cur else 0.0)
            cur_cross = max(cur_cross, cross(s))
            cur.append(i)
        if cur:
            runs.append(cur)
            run_main.append(cur_main)
            run_cross.append(cur_cross)
        self.runs = runs
        main_extent = max(run_main, default=0.0)
        cross_extent = sum(run_cross) + self.run_spacing * max(0, len(runs) - 1)
        self.size = c.constrain(cross_extent, main_extent) if v else c.constrain(main_extent, cross_extent)
        cont_main, cont_cross = (self.size[1], self.size[0]) if v else (self.size[0], self.size[1])
        run_lead, run_between = _lead_between(self.run_align, cont_cross - cross_extent, len(runs))
        self.placed = []
        pos_cross = run_lead
        for r, idxs in enumerate(runs):
            lead, between = _lead_between(self.align, cont_main - run_main[r], len(idxs))
            pos_main = lead
            for i in idxs:
                s = sizes[i]
                if self.cross_align == "end":
                    off = run_cross[r] - cross(s)
                elif self.cross_align == "center":
                    off = (run_cross[r] - cross(s)) / 2
                else:
                    off = 0.0
                x, y = ((pos_cross + off, pos_main) if v else (pos_main, pos_cross + off))
                self.placed.append((self.items[i], x, y))
                pos_main += main(s) + self.spacing + between
            pos_cross += run_cross[r] + self.run_spacing + run_between
        line, step = ("column", "to the right") if v else ("row", "lower")
        n = len(runs)
        self.note("wrap", f"A Wrap fills a {line} until the next box would not fit in {fnum(limit)} (boxes plus "
                          f"{fnum(self.spacing)} gaps), then starts a new {line} {fnum(self.run_spacing)} {step}. "
                          f"Here that makes {n} {line}{'s' if n != 1 else ''} "
                          f"({' + '.join(str(len(r)) for r in runs)} boxes), together {fnum(cross_extent)} "
                          f"{'wide' if v else 'tall'}.")
        return self.size


# ── Printing ────────────────────────────────────────────────────────────

WIDTH = 78


def _call(v: Node):
    """(name, positional args, named args) with `key:` first, as it is usually written."""
    name, pos, named = v.call()
    return name, pos, sorted(named, key=lambda kv: kv[0] != "key")


def _flat(v: Any) -> str:
    if isinstance(v, Node):
        name, pos, named = _call(v)
        args = [_flat(p) if not isinstance(p, str) else p for p in pos]
        args += [f"{k}: {_flat(x)}" if not isinstance(x, str) else f"{k}: {x}" for k, x in named]
        return f"{name}({', '.join(args)})"
    if isinstance(v, list):
        return "[" + ", ".join(_flat(x) for x in v) + "]"
    return str(v)


def render(v: Any, indent: int = 0, width: int = WIDTH) -> str:
    """Dart source for a node: on one line when it fits in `width` columns, else one argument per line."""
    flat = _flat(v)
    if indent + len(flat) <= width:
        return flat
    pad = " " * (indent + 2)
    if isinstance(v, Node):
        name, pos, named = _call(v)
        if not pos and len(named) == 1 and named[0][0] == "child" and isinstance(named[0][1], Node):
            inner = render(named[0][1], indent, width)
            if indent + len(name) + 8 + len(inner.splitlines()[0]) <= width + 6:  # Center(child: Row(
                return f"{name}(child: " + inner + ")"
        if named and isinstance(named[-1][1], list) and not pos:  # hug the list: `Row(children: [` ... `]),`
            earlier = "".join(f"{k}: {_flat(x)}, " for k, x in named[:-1])
            head = f"{name}({earlier}{named[-1][0]}: ["
            if indent + len(head) <= width:
                body = _render_list(named[-1][1], indent, width)  # "[" ... "]" at this indent
                return head + body[1:] + ")"
        lines = [f"{name}("]
        for p in pos:
            lines.append(pad + (p if isinstance(p, str) else render(p, indent + 2, width)) + ",")
        for k, x in named:
            body = x if isinstance(x, str) else render(x, indent + 2, width)
            lines.append(pad + f"{k}: {body},")
        lines.append(" " * indent + ")")
        return "\n".join(lines)
    if isinstance(v, list):
        return _render_list(v, indent, width)
    return str(v)


def _render_list(v: list, indent: int, width: int) -> str:
    """A list over several lines (several small items to a line when there are many of them)."""
    pad = " " * (indent + 2)
    flats = [_flat(x) for x in v]
    lines = ["["]
    if len(v) >= 3 and all(len(f) <= 30 for f in flats):  # many small items: several to a line
        row = ""
        for f in flats:
            piece = f + ","
            if row and len(pad) + len(row) + 1 + len(piece) > width:
                lines.append(pad + row)
                row = piece
            else:
                row = (row + " " + piece) if row else piece
        lines.append(pad + row)
    else:
        for x in v:
            lines.append(pad + render(x, indent + 2, width) + ",")
    lines.append(" " * indent + "]")
    return "\n".join(lines)


# ── Hosting, finding, explaining ────────────────────────────────────────

def host(root: Node) -> Ctx:
    """Lay the tree out as the app's root widget: tight 400 x 300 constraints. Returns every keyed rectangle."""
    root.reset()
    root.layout(BC.tight(SCREEN_W, SCREEN_H))
    ctx = Ctx()
    root.paint(0.0, 0.0, ctx)
    ctx.overflow = any(isinstance(n, FlexN) and n.has_overflow() for n in walk(root))
    return ctx


def first_id(n: Node) -> str | None:
    """The id of the widget itself, or of the first keyed widget below it."""
    if n.id:
        return n.id
    for k in n.kids():
        found = first_id(k)
        if found:
            return found
    return None


def walk(n: Node) -> Iterable[Node]:
    yield n
    for k in n.kids():
        yield from walk(k)


def path_to(root: Node, id_: str) -> list[Node]:
    """The nodes from the root down to the widget keyed `id_` (empty if there is none)."""
    if root.id == id_:
        return [root]
    for k in root.kids():
        sub = path_to(k, id_)
        if sub:
            return [root] + sub
    return []


def explain(root: Node, id_: str | None, topics: Iterable[str], host_note: bool = True) -> str:
    """The notes (under `topics`) of the nodes on the way down to `id_`, root first, as one paragraph."""
    want = set(topics)
    nodes = path_to(root, id_) if id_ else list(walk(root))
    out: list[str] = []
    if host_note:
        out.append("The screen is 400 x 300 and forces its root widget to exactly that size.")
    for n in nodes:
        notes = list(n.notes)
        if isinstance(n, ContainerN):
            notes += n.inner_notes()
        out.extend(text for topic, text in notes if topic in want)
    return " ".join(out)


# ── Items ───────────────────────────────────────────────────────────────

PROPS = {"w": "width", "h": "height", "x": "left", "y": "top", "r": "right edge", "b": "bottom edge"}


def measure(ctx: Ctx, id_: str, prop: str) -> float:
    x, y, w, h = ctx.rects[id_]
    return {"w": w, "h": h, "x": x, "y": y, "r": x + w, "b": y + h}[prop]


def item(root: Node, id_: str, prop: str, topics: Iterable[str], tail: str = "", comment: str | None = None,
         host_note: bool = True) -> Item:
    """An item asking for one measurement of the widget keyed `id_`: `// width of b`, then the code."""
    ctx = host(root)
    answer = fnum(measure(ctx, id_, prop))
    ask = comment if comment is not None else f"// {PROPS[prop]} of {id_}"
    prompt = ask + "\n" + render(root)
    why = (explain(root, id_, topics, host_note) + (" " + tail if tail else "")).strip()
    return Item(prompt, answer, f"{why} So the {PROPS[prop]} of {id_} is {answer}." if comment is None else f"{why} So the answer is {answer}.",
                check=f"{prop}('{id_}')")


def fit(maker: Maker, tries: int = 300, whole: bool = True) -> Maker:
    """A template that re-rolls its random choices until the prompt is short enough for the drill (<= 200 characters,
    <= 9 lines - the shape tests hold every prompt to that) and, by default, the answer is a whole number."""
    def make(rng: random.Random) -> Item:
        last = None
        for _ in range(tries):
            try:
                last = maker(rng)
            except Retry:
                continue
            if len(last.prompt) <= 220 and last.prompt.count("\n") <= 9 and (not whole or "." not in last.answer):
                return last
        assert last is not None, f"{getattr(maker, '__name__', maker)} always asked for a re-roll"
        raise AssertionError(f"{getattr(maker, '__name__', maker)} never made a short prompt; last was:\n{last.prompt}")
    make.__name__ = getattr(maker, "__name__", "template")
    return make


class Retry(Exception):
    """A template's random choices did not make a good item (a fraction, a prompt too long): `fit` rolls again."""


def named(name: str, maker: Callable[[random.Random], Item]) -> Maker:
    maker.__name__ = name
    return maker
