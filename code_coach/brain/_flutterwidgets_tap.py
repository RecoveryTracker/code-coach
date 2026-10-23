"""Flutter widgets pack, activity 5: Tap Target.

Which handler fires when the test taps (or long-presses, drags, hovers) at a place? Every example keeps a counter
`n` that the handlers bump through `add(k)` - the digits of n then say WHICH handlers ran (1, 10, 100 are different
handlers) - and the answer is n at the end. (A global counter plus a function that bumps it is the smallest
declaration a prompt can carry: it must end with a column-0 `}` line, so the oracle treats it as the item's library.)

The rules written out below, and held to real Flutter by the oracle:

* HIT TESTING. A render object adds itself to the hit path if the point is inside it and (a child was hit, or its
  behavior is `opaque`); a `translucent` one is added even when nothing under it was hit but lets the widgets below
  it be tested too; `deferToChild` (the GestureDetector default) is added only if a child was hit. An empty `Box`
  (a SizedBox) or an uncoloured `Container` has nothing to hit; `ColoredBox`, `Container(color:)` and a
  `DecoratedBox` do. InkWell is opaque. In a Stack the last child is tested first, and an opaque hit stops the search.
* THE ARENA. Among the gesture detectors on the path only ONE tap wins: the deepest / topmost one. A Listener is not
  in the arena: it gets every pointer event of the path.
* IgnorePointer is never hit; AbsorbPointer swallows the tap without any handler; Opacity 0 still takes taps, an
  Offstage child does not.
* A GestureDetector with onDoubleTap delays onTap until the double-tap window (300 ms) is over.
"""

from __future__ import annotations


from ._flutterwidgets_kit import G, col, mk, q, row, template, text

TEMPLATES: list = []

ADD = "int n = 0;\nvoid add(int k) {\n  n += k;\n}"
RET = "\nreturn n;"
OPAQUE = "HitTestBehavior.opaque"
TRANSLUCENT = "HitTestBehavior.translucent"
PUMP = "await tester.pump(Duration(milliseconds: 500));"


def hit(k: int) -> str:
    return f"() => add({k})"


def hit1(k: int) -> str:
    return f"(_) => add({k})"


def box(id_: str = "a", w: int = 50, h: int = 50) -> G:
    kw = {}
    if w != 50:
        kw["w"] = str(w)
    if h != 50:
        kw["h"] = str(h)
    return G("Box", q(id_), **kw)


def red(**kw) -> G:
    return G("Container", **kw, color="Colors.red")


def gd(k: int, behavior: str | None = None, child=None, **kw) -> G:
    args: dict = {}
    if behavior:
        args["behavior"] = behavior
    args["onTap"] = hit(k)
    args.update(kw)
    if child is not None:
        args["child"] = child
    return G("GestureDetector", **args)


def ink(k: int, child) -> G:
    return G("InkWell", onTap=hit(k), child=child)


def mat(child) -> G:
    return G("Material", child=child)


def tap_at(x: float, y: float) -> str:
    return f"await tester.tapAt(Offset({x:g}, {y:g}));\n{PUMP}"


def ask_at(x: float, y: float) -> str:
    return f"n after a tap at {x:g}, {y:g}"


# ── what can be hit ─────────────────────────────────────────────────────

#: (code, can a tap in its middle hit it?) - a child that draws or paints something is hit; empty boxes are not.
CHILDREN = {
    "an empty Box": (lambda: box(), False),
    "an uncoloured Container": (lambda: G("Container"), False),
    "a coloured Container": (lambda: red(), True),
    "a transparent Container": (lambda: G("Container", color="Colors.transparent"), True),
    "a Container holding a Text": (lambda: G("Container", child=text("x")), True),
    "a Text": (lambda: text("tap me"), True),
    "a DecoratedBox with only a border": (lambda: G("DecoratedBox", decoration="BoxDecoration(border: Border.all())", child=box()), True),
    "a Padding around an empty Box": (lambda: G("Padding", padding="EdgeInsets.all(20)", child=box()), False),
    "a Padding around a ColoredBox": (lambda: G("Padding", padding="EdgeInsets.all(20)", child=G("ColoredBox", color="Colors.red", child=box())), True),
    "a Center around an empty Box": (lambda: G("Center", child=box()), False),
}


@template(TEMPLATES)
def what_can_be_hit(rng):
    name = rng.choice(list(CHILDREN))
    make, child_hit = CHILDREN[name]
    behavior = rng.choice((None, None, OPAQUE, TRANSLUCENT))
    got = 1 if (child_hit or behavior in (OPAQUE, TRANSLUCENT)) else 0
    why = (f"The tap lands in the middle of {name}. " + ("That child can be hit" if child_hit else "That child has nothing to hit")
           + (f", and behavior {behavior.split('.')[1]} makes the detector itself take the tap" if behavior else ", and the default behavior (deferToChild) needs a child that is hit")
           + f": n = {got}.")
    return mk("n after tapping the middle", gd(1, behavior, make()), got, why,
              "await tester.tap(find.byType(GestureDetector));\n" + PUMP + RET, decls=ADD)


# ── layers and the arena ────────────────────────────────────────────────

def hit_layers(layers: list[dict]) -> tuple[int, str]:
    """Simulate a tap through Stack layers given TOP FIRST. Returns (n, what happened).

    ink / det_opaque / det_colored: added, the search stops. det_translucent: added, the search goes on. det_empty,
    box, ignore, listener_empty: not hit. absorb: stops the search, nothing added. listener_opaque: added, stops.
    The winner among tap detectors is the first one added; every Listener added gets its event."""
    winner, listeners, story = None, [], []
    for L in layers:
        k, label = L["kind"], L["label"]
        if k in ("det_empty", "box", "ignore", "listener_empty"):
            story.append(f"{label} is not hit")
            continue
        if k == "absorb":
            story.append(f"{label} swallows the tap")
            break
        if k in ("ink", "det_colored", "det_translucent"):
            if winner is None:
                winner = L["value"]
                story.append(f"{label} is hit and wins the tap")
            else:
                story.append(f"{label} is on the path but loses the arena")
            if k != "det_translucent":
                break
            continue
        listeners.append(L["value"])  # listener_opaque
        story.append(f"{label} hears the pointer")
        break
    return (winner or 0) + sum(listeners), "; ".join(story)


def layer(kind: str, value: int, i: int):
    """(widget, dict for hit_layers) of one Stack layer: 50 x 50 at the top left, keyed 'a', 'b', 'c'."""
    b = box("abc"[i])
    if kind == "ink":
        return ink(value, b), dict(kind=kind, value=value, label=f"the InkWell (adds {value}; always opaque)")
    if kind == "det_translucent":
        return gd(value, TRANSLUCENT, b), dict(kind=kind, value=value, label=f"the translucent GestureDetector (adds {value})")
    if kind == "det_empty":
        return gd(value, None, b), dict(kind=kind, value=value, label=f"the GestureDetector over an empty Box (adds {value})")
    if kind == "det_colored":
        return gd(value, None, G("ColoredBox", color="Colors.red", child=b)), dict(kind=kind, value=value, label=f"the GestureDetector over a ColoredBox (adds {value})")
    if kind == "listener_opaque":
        return (G("Listener", behavior=OPAQUE, onPointerDown=hit1(value), child=b), dict(kind=kind, value=value, label=f"the opaque Listener (adds {value})"))
    if kind == "listener_empty":
        return G("Listener", onPointerDown=hit1(value), child=b), dict(kind=kind, value=value, label=f"the Listener over an empty Box (adds {value})")
    if kind == "ignore":
        return G("IgnorePointer", child=ink(value, b)), dict(kind=kind, value=value, label=f"the InkWell inside an IgnorePointer (adds {value})")
    if kind == "absorb":
        return G("AbsorbPointer", child=b), dict(kind=kind, value=value, label="the AbsorbPointer")
    return b, dict(kind="box", value=value, label="the plain Box")


STACK_KINDS = ("ink", "det_translucent", "det_empty", "det_colored", "ignore", "absorb", "box", "listener_opaque", "listener_empty")


@template(TEMPLATES)
def stack_layers(rng):
    kinds = [rng.choice(STACK_KINDS) for _ in range(rng.choice((2, 2, 3)))]
    built = [layer(kind, 10 ** i, i) for i, kind in enumerate(kinds)]  # bottom first, as written
    n, story = hit_layers([d for _, d in reversed(built)])
    w = G("Stack", children=[x for x, _ in built])
    if any(d["kind"] in ("ink", "ignore") for _, d in built):
        w = mat(w)
    return mk(ask_at(25, 25), w, n, f"The Stack tests its last child first: {story}. n = {n}.", tap_at(25, 25) + RET, decls=ADD)


@template(TEMPLATES)
def covering_layer(rng):
    top = rng.choice([
        ("a plain Box", box("b"), False, "an empty Box has nothing to hit, so the tap goes on to the InkWell below"),
        ("a transparent ColoredBox", G("ColoredBox", color="Colors.transparent", child=box("b")), True, "a ColoredBox is hit even when it is transparent, so it covers the InkWell"),
        ("a red ColoredBox inside an IgnorePointer", G("IgnorePointer", child=G("ColoredBox", color="Colors.red", child=box("b"))), False,
         "IgnorePointer is never hit, whatever is inside it"),
        ("a red ColoredBox inside an Opacity of 0", G("Opacity", opacity="0", child=G("ColoredBox", color="Colors.red", child=box("b"))), True,
         "an invisible Opacity is still there for hit testing"),
        ("a red ColoredBox inside an invisible Visibility", G("Visibility", visible="false", child=G("ColoredBox", color="Colors.red", child=box("b"))), False,
         "an invisible Visibility builds nothing"),
        ("a red ColoredBox inside an Offstage", G("Offstage", child=G("ColoredBox", color="Colors.red", child=box("b"))), False, "an Offstage child cannot be hit"),
        ("a red Container", red(width="50", height="50"), True, "Container(color:) builds a ColoredBox, which is hit"),
    ])
    name, widget, covers, why = top
    n = 0 if covers else 1
    w = mat(G("Stack", children=[ink(1, box("a")), widget]))
    return mk(ask_at(25, 25), w, n, f"The tap is inside both layers and {name} is on top: {why}. n = {n}.", tap_at(25, 25) + RET, decls=ADD)


@template(TEMPLATES)
def pointer_flags(rng):
    conds = [("true", True), ("false", False), ("1 > 2", False), ("2 > 1", True), ("'a'.isEmpty", False), ("'ab'.length == 2", True)]
    code, val = rng.choice(conds)
    bottom = ink(1, box("a"))
    if rng.random() < 0.5:
        top = G("IgnorePointer", ignoring=code, child=ink(10, box("b")))
        n = 1 if val else 10
        why = f"IgnorePointer(ignoring: {code}) is {'invisible to taps, so the lower InkWell wins' if val else 'not ignoring anything, so its InkWell is on top and wins'}"
    else:
        top = G("AbsorbPointer", absorbing=code, child=box("b"))
        n = 0 if val else 1
        why = (f"AbsorbPointer(absorbing: {code}) " + ("swallows the tap: nothing under it hears it" if val
                                                        else "does not absorb, and its empty child is not hit, so the lower InkWell wins"))
    return mk(ask_at(25, 25), mat(G("Stack", children=[bottom, top])), n, f"{why}: n = {n}.", tap_at(25, 25) + RET, decls=ADD)


@template(TEMPLATES)
def nested_detectors(rng):
    outer_kind = rng.choice(("ink", "gd"))
    inner_kind = rng.choice(("ink", "gd_empty", "gd_translucent"))
    spot = rng.choice(("the middle", "the corner"))
    b = box()
    inner = {"ink": ink(1, b), "gd_empty": gd(1, None, b), "gd_translucent": gd(1, TRANSLUCENT, b)}[inner_kind]
    padded = G("Center", child=inner)
    outer = ink(10, padded) if outer_kind == "ink" else gd(10, None, padded)
    inner_added, inner_blocks = inner_kind in ("ink", "gd_translucent"), inner_kind == "ink"
    outer_added = inner_blocks or outer_kind == "ink"
    if spot == "the middle":
        n = 1 if inner_added else (10 if outer_added else 0)
        x, y = 200, 150
        why = ("The inner detector is hit and wins the arena" if inner_added else
               "The inner GestureDetector has an empty Box and the default behavior, so it is not hit"
               + (", and the outer one takes the tap" if outer_added else ", and the outer one is not hit either"))
    else:
        n = 10 if outer_kind == "ink" else 0
        x, y = 20, 20
        why = ("The space around the centred box belongs to the outer InkWell, which is opaque" if n else
               "The space around the centred box has nothing to hit, and the outer GestureDetector uses the default behavior")
    root = mat(outer) if "ink" in (outer_kind, inner_kind) else outer
    return mk(f"n after tapping {spot}", root, n, f"The tap lands in {spot}. {why}: n = {n}.", tap_at(x, y) + RET, decls=ADD)


# ── gestures in time ────────────────────────────────────────────────────

def pressable(**handlers) -> G:
    return G("GestureDetector", **handlers, child=red())


@template(TEMPLATES)
def click_timing(rng):
    handlers = rng.sample([("onTap", 1), ("onDoubleTap", 10), ("onLongPress", 100)], rng.randint(2, 3))
    d = dict(handlers)
    action = rng.choice(("tap", "double", "apart", "long"))
    if action == "tap":
        n = d.get("onTap", 0)
        why = ("A single tap" + (" waits out the double-tap window (300 ms), then onTap runs" if "onDoubleTap" in d else " runs onTap right away")) if "onTap" in d \
            else "A single tap with no onTap does nothing"
    elif action == "double":
        if "onDoubleTap" in d:
            n, why = d["onDoubleTap"], "Two quick taps are a double tap: onDoubleTap runs and onTap does not"
        else:
            n, why = 2 * d.get("onTap", 0), "Without onDoubleTap two quick taps are just two taps"
    elif action == "apart":
        n, why = 2 * d.get("onTap", 0), "Taps more than 300 ms apart are two separate taps"
    elif "onLongPress" in d:
        n, why = d["onLongPress"], "Holding long enough is a long press, and a long press cancels the tap"
    else:
        n, why = d.get("onTap", 0), "Without onLongPress, holding and letting go is still a tap"
    w = pressable(**{name: hit(v) for name, v in handlers})
    f = "find.byType(GestureDetector)"
    code = {
        "tap": f"await tester.tap({f});",
        "double": f"await tester.tap({f});\nawait tester.pump(Duration(milliseconds: 50));\nawait tester.tap({f});",
        "apart": f"await tester.tap({f});\n{PUMP}\nawait tester.tap({f});",
        "long": f"await tester.longPress({f});",
    }[action]
    ask = {"tap": "n after one tap", "double": "n after two taps 50 ms apart", "apart": "n after two taps 500 ms apart", "long": "n after a long press"}[action]
    return mk(ask, w, n, f"{why}: n = {n}.", code + "\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def repeated_quick_taps(rng):
    k = rng.randint(2, 5)
    w = pressable(onTap=hit(1), onDoubleTap=hit(10))
    n = (k // 2) * 10 + (k % 2) * 1
    lines = "\n".join("await tester.tap(find.byType(GestureDetector));\nawait tester.pump(Duration(milliseconds: 50));" for _ in range(k))
    return mk(f"n after {k} taps, 50 ms apart", w, n, f"Quick taps pair up into double taps ({k // 2} of them, 10 each); a leftover single tap "
              f"{'runs onTap once the double-tap window is over (1)' if k % 2 else 'does not exist'}: n = {n}.", lines + "\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def tap_phases(rng):
    pool = [("onTapDown", "(_) => add(1)", 1), ("onTapUp", "(_) => add(10)", 10), ("onTap", "() => add(100)", 100), ("onTapCancel", "() => add(1000)", 1000)]
    hs = rng.sample(pool, 2)
    d = {name: v for name, _, v in hs}
    action = rng.choice(("tap", "slide_off"))
    if action == "tap":
        n = sum(d.get(x, 0) for x in ("onTapDown", "onTapUp", "onTap"))
        why, code, ask = "A tap is down, up, then tap (a cancel never happens)", "await tester.tap(find.byType(GestureDetector));", "n after one tap"
    else:
        n = sum(d.get(x, 0) for x in ("onTapDown", "onTapCancel"))
        why = "The finger is held long enough for onTapDown, then slides away, so the tap is cancelled: down and cancel, never up or tap"
        code = ("final g = await tester.startGesture(tester.getCenter(find.byType(GestureDetector)));\nawait tester.pump(Duration(milliseconds: 200));\n"
                "await g.moveBy(Offset(100, 0));\nawait tester.pump();\nawait g.up();")
        ask = "n after press, slide away, release"
    w = G("GestureDetector", **{name: code_ for name, code_, _ in hs}, child=red())
    return mk(ask, w, n, f"{why}: n = {n}.", code + "\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def drag_axes(rng):
    shape = rng.choice(("HV", "HT", "VT", "HVT"))
    pool = {"H": ("onHorizontalDragEnd", "(_) => add(1)", 1), "V": ("onVerticalDragEnd", "(_) => add(10)", 10), "T": ("onTap", "() => add(100)", 100)}
    hs = [pool[c] for c in shape]
    action = rng.choice(("horizontal", "vertical", "tap"))
    has = set(shape)
    if action == "horizontal":
        code, ask = "await tester.drag(find.byType(GestureDetector), Offset(80, 0));", "n after dragging 80 px sideways"
        if "H" in has:
            n, why = 1, "A sideways drag is what the horizontal recognizer waits for"
        elif "V" in has:
            n, why = 10, "Moving makes the tap give up; the vertical recognizer is the only one left and wins by default, even for a sideways drag"
        else:
            n, why = 0, "No drag recognizer, and a moving pointer is not a tap"
    elif action == "vertical":
        code, ask = "await tester.drag(find.byType(GestureDetector), Offset(0, 80));", "n after dragging 80 px down"
        if "V" in has:
            n, why = 10, "An up-or-down drag is what the vertical recognizer waits for"
        elif "H" in has:
            n, why = 1, "Moving makes the tap give up; the horizontal recognizer is the only one left and wins by default, even for a vertical drag"
        else:
            n, why = 0, "No drag recognizer, and a moving pointer is not a tap"
    else:
        code, ask = "await tester.tap(find.byType(GestureDetector));", "n after one tap"
        n, why = (100, "A tap moves nowhere, so onTap wins") if "T" in has else (0, "Without onTap a tap does nothing: the drag recognizers give up when the finger lifts")
    return mk(ask, pressable(**{name: code_ for name, code_, _ in hs}), n, f"{why}: n = {n}.", code + "\n" + PUMP + RET, decls=ADD)


# ── places ──────────────────────────────────────────────────────────────

def inside(r, x, y):
    l, t, w, h = r
    return l < x < l + w and t < y < t + h


@template(TEMPLATES)
def tap_at_a_point(rng):
    l, t = rng.choice(range(20, 200, 20)), rng.choice(range(20, 150, 10))
    w, h = 50, 50
    r = (l, t, w, h)
    x, y = rng.choice(range(5, 395, 10)), rng.choice(range(5, 295, 10))
    if rng.random() < 0.5:  # aim inside
        x, y = l + rng.choice(range(5, w, 10)), t + rng.choice(range(5, h, 10))
    n = 1 if inside(r, x, y) else 0
    wdg = mat(G("Stack", children=[G("Positioned", left=str(l), top=str(t), child=ink(1, box("a", w, h)))]))
    return mk(ask_at(x, y), wdg, n, f"The InkWell covers x from {l} to {l + w} and y from {t} to {t + h}; "
              f"({x}, {y}) is {'inside' if n else 'outside'} it: n = {n}.", tap_at(x, y) + RET, decls=ADD, width=100)


@template(TEMPLATES)
def tap_in_a_row(rng):
    a, b = rng.choice((50, 100, 150)), rng.choice((50, 100, 150))
    gap = rng.random() < 0.5
    kids = [ink(1, box("a", a, 50))] + ([box("g", 100, 50)] if gap else []) + [ink(10, box("b", b, 50))]
    g = 100 if gap else 0
    x = rng.choice(range(5, 400, 10))
    if x < a:
        n = 1
    elif x > a + g and x < a + g + b:
        n = 10
    else:
        n = 0
    spot = "the first InkWell" if n == 1 else "the second InkWell" if n == 10 else "the gap or empty space"
    return mk(ask_at(x, 150), mat(row(*kids)), n, f"The Row puts its children side by side from the left: the first InkWell covers x 0 to {a}"
              + (f", a gap {a} to {a + 100}" if gap else "") + f", the second {a + g} to {a + g + b}. x = {x} is in {spot}: n = {n}.", tap_at(x, 150) + RET, decls=ADD)


@template(TEMPLATES)
def tap_in_padding(rng):
    p = rng.choice((20, 30, 40))
    kind = rng.choice(("pad_in", "pad_opaque", "container", "margin", "outer_pad"))
    core = G("ColoredBox", color="Colors.red", child=box())
    if kind == "pad_in":
        w, ring_hit = gd(1, None, G("Padding", padding=f"EdgeInsets.all({p})", child=core)), False
        why = "Padding itself has nothing to hit, so the ring around the red box is not part of the detector's target"
    elif kind == "pad_opaque":
        w, ring_hit = gd(1, OPAQUE, G("Padding", padding=f"EdgeInsets.all({p})", child=core)), True
        why = "behavior: opaque makes the detector's whole area, padding included, a target"
    elif kind == "container":
        w, ring_hit = gd(1, None, G("Container", padding=f"EdgeInsets.all({p})", color="Colors.red", child=box())), True
        why = "Container paints its colour behind the padding, so the whole area, ring included, is red and can be hit"
    elif kind == "margin":
        w, ring_hit = gd(1, None, G("Container", margin=f"EdgeInsets.all({p})", color="Colors.red", child=box())), False
        why = "A margin is outside the colour: the ring is empty space around the red Container"
    else:
        w, ring_hit = G("Padding", padding=f"EdgeInsets.all({p})", child=gd(1, None, core)), False
        why = "The padding is outside the detector here (the detector wraps only the red box)"
    spot = rng.choice(("ring", "core"))
    x = 200 if spot == "core" else p / 2
    n = 1 if (spot == "core" or ring_hit) else 0
    return mk(f"n after tapping the {'edge of the screen, in the padding' if spot == 'ring' else 'middle'}", w, n,
              f"{why if spot == 'ring' else 'The middle of the red box is always hit'}: n = {n}.", tap_at(x, 150) + RET, decls=ADD)


@template(TEMPLATES)
def tap_list_item(rng):
    off = rng.choice((0, 0, 112, 200, 336))
    y = rng.choice(range(10, 290, 23))
    idx = int((y + off) // 56)
    w = mat(G("ListView.builder", itemBuilder="(c, i) => ListTile(onTap: () => add(i), title: Text('$i'))"))
    pre = "" if off == 0 else f"tester.state<ScrollableState>(find.byType(Scrollable)).position.jumpTo({off});\nawait tester.pump();\n"
    ask = ask_at(200, y) + ("" if off == 0 else f", list scrolled by jumpTo({off})")
    return mk(ask, w, idx, f"A one-line ListTile is 56 tall, so item k covers 56k to 56k + 56 of the list; the tap is {y}"
              f"{f' + {off}' if off else ''} = {y + off} pixels down: item {idx}.", pre + tap_at(200, y) + RET, decls=ADD)


# ── buttons, toggles and other widgets ──────────────────────────────────

@template(TEMPLATES)
def button_kinds(rng):
    kind = rng.choice(("ElevatedButton", "TextButton", "OutlinedButton", "FilledButton"))
    pressed = rng.choice((1, 1, None))
    lng = rng.choice((10, None)) if pressed else 10
    kw: dict = {"onPressed": hit(pressed) if pressed else "null"}
    if lng:
        kw["onLongPress"] = hit(lng)
    action = rng.choice(("tap", "long"))
    if action == "tap":
        n = pressed or 0
        why = "A tap calls onPressed" if pressed else "onPressed is null, so a tap does nothing (an onLongPress alone does not help)"
        code = "await tester.tap(find.byType(" + kind + "));"
    else:
        n = lng if lng else (pressed or 0)
        why = "A long press calls onLongPress" if lng else "Without onLongPress, holding and releasing is a normal press, so onPressed runs"
        code = "await tester.longPress(find.byType(" + kind + "));"
    return mk(f"n after {'a tap' if action == 'tap' else 'a long press'}", mat(G("Center", child=G(kind, **kw, child=text("go")))), n, f"{why}: n = {n}.",
              code + "\nawait tester.pump();" + RET, decls=ADD)


@template(TEMPLATES)
def tiles_in_a_column(rng):
    k = rng.randint(2, 3)
    kinds = [rng.choice(("on", "on", "off", "none")) for _ in range(k)]
    tiles = []
    for i, kind in enumerate(kinds):
        kw: dict = {"title": text("abc"[i])}
        if kind == "on":
            kw["onTap"] = hit(10 ** i)
        elif kind == "off":
            kw["enabled"] = "false"
            kw["onTap"] = hit(10 ** i)
        tiles.append(G("ListTile", **kw))
    seq = [rng.randrange(k) for _ in range(rng.randint(2, 4))]
    n = sum(10 ** i for i in seq if kinds[i] == "on")
    lines = "\n".join(f"await tester.tap(find.text('{'abc'[i]}'));" for i in seq)
    return mk("n after tapping " + ", ".join(repr("abc"[i]) for i in seq), mat(col(*tiles)), n,
              "A ListTile reacts only if it has an onTap and is enabled (enabled: false switches it off): " + ", ".join(
                  f"'{'abc'[i]}' is {'live' if kinds[i] == 'on' else 'dead'}" for i in range(k)) + f". n = {n}.", lines + "\nawait tester.pump();" + RET, decls=ADD)


@template(TEMPLATES)
def tile_and_ink(rng):
    kind = rng.choice(("ListTile", "ListTileOff", "ListTileNull", "InkWell", "InkWellDouble", "InkWellNull"))
    if kind == "ListTile":
        w, n, why = G("ListTile", onTap=hit(1), title=text("a")), 1, "A ListTile with onTap reacts to a tap"
    elif kind == "ListTileOff":
        w, n, why = G("ListTile", enabled="false", onTap=hit(1), title=text("a")), 0, "enabled: false switches the tile off even though onTap is set"
    elif kind == "ListTileNull":
        w, n, why = G("ListTile", title=text("a")), 0, "No onTap, nothing to run"
    elif kind == "InkWell":
        w, n, why = G("InkWell", onTap=hit(1), child=text("a")), 1, "InkWell reacts to taps on its child"
    elif kind == "InkWellDouble":
        w, n, why = G("InkWell", onDoubleTap=hit(1), child=text("a")), 0, "An InkWell with only onDoubleTap does nothing on a single tap"
    else:
        w, n, why = G("InkWell", child=text("a")), 0, "An InkWell without handlers does nothing"
    return mk("n after one tap on the 'a'", mat(G("Center", child=w)), n, f"{why}: n = {n}.",
              "await tester.tap(find.text('a'));\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def controlled_toggle(rng):
    kind = rng.choice(("Checkbox", "CheckboxTri", "Switch", "SwitchListTile", "FilterChip"))
    taps = rng.randint(1, 3)
    decl = "int n = 0;\nvoid pick(bool? v) {\n  n += v == true ? 1 : v == false ? 10 : 100;\n}"
    val = rng.choice(("false", "true"))
    if kind == "Checkbox":
        w, new = G("Checkbox", value=val, onChanged="pick"), val == "false"
    elif kind == "CheckboxTri":
        val = rng.choice(("false", "true", "null"))
        w = G("Checkbox", tristate="true", value=val, onChanged="pick")
        new = {"false": True, "true": None, "null": False}[val]
    elif kind == "Switch":
        w, new = G("Switch", value=val, onChanged="pick"), val == "false"
    elif kind == "SwitchListTile":
        w, new = G("SwitchListTile", value=val, onChanged="pick", title=text("a")), val == "false"
    else:
        w, new = G("FilterChip", label=text("a"), selected=val, onSelected="pick"), val == "false"
    unit = 1 if new is True else 10 if new is False else 100
    n = taps * unit
    finder = {"CheckboxTri": "Checkbox"}.get(kind, kind)
    lines = "\n".join(f"await tester.tap(find.byType({finder}));\nawait tester.pump();" for _ in range(taps))
    root = G("MaterialApp", home=mat(G("Center", child=w))) if kind == "FilterChip" else mat(G("Center", child=w))
    return mk(f"n after {taps} tap{'s' if taps > 1 else ''}", root, n,
              "The widget is controlled: it only reports what the new value would be, and since nothing rebuilds it with that value, every tap "
              f"reports the same one ({'true, +1' if new is True else 'false, +10' if new is False else 'null, +100'}): {taps} x {unit} = {n}.", lines + RET, decls=decl)


@template(TEMPLATES)
def disabled_toggle(rng):
    kind = rng.choice(("Checkbox", "Switch", "ElevatedButton", "TextButton", "IconButton"))
    on = rng.random() < 0.5
    if kind in ("Checkbox", "Switch"):
        w = G(kind, value="false", onChanged="(v) => add(1)" if on else "null")
    elif kind == "IconButton":
        w = G(kind, onPressed=hit(1) if on else "null", icon=G("Icon", "Icons.add"))
    else:
        w = G(kind, onPressed=hit(1) if on else "null", child=text("a"))
    return mk("n after one tap", mat(G("Center", child=w)), int(on), f"{kind} is disabled when its callback is null, and a disabled one ignores taps: n = {int(on)}.",
              f"await tester.tap(find.byType({kind}), warnIfMissed: false);\nawait tester.pump();" + RET, decls=ADD)


WRAPS = [
    ("Opacity(opacity: 0, ...)", lambda c: G("Opacity", opacity="0", child=c), True, "an invisible Opacity still takes taps"),
    ("IgnorePointer(...)", lambda c: G("IgnorePointer", child=c), False, "IgnorePointer lets the tap pass through"),
    ("IgnorePointer(ignoring: false, ...)", lambda c: G("IgnorePointer", ignoring="false", child=c), True, "ignoring: false ignores nothing"),
    ("AbsorbPointer(...)", lambda c: G("AbsorbPointer", child=c), False, "AbsorbPointer swallows the tap"),
    ("AbsorbPointer(absorbing: false, ...)", lambda c: G("AbsorbPointer", absorbing="false", child=c), True, "absorbing: false absorbs nothing"),
    ("Offstage(...)", lambda c: G("Offstage", child=c), False, "an Offstage child is not hit-testable"),
    ("Offstage(offstage: false, ...)", lambda c: G("Offstage", offstage="false", child=c), True, "offstage: false shows the child normally"),
    ("Visibility(visible: false, ...)", lambda c: G("Visibility", visible="false", child=c), False, "an invisible Visibility builds nothing at all"),
    ("Visibility.maintain(visible: false, ...)", lambda c: G("Visibility.maintain", visible="false", child=c), True,
     "Visibility.maintain keeps size, state and interactivity"),
    ("Visibility(visible: false, maintainSize: true, ...)",
     lambda c: G("Visibility", visible="false", maintainState="true", maintainAnimation="true", maintainSize="true", child=c), False,
     "without maintainInteractivity the kept child cannot be tapped"),
    ("ExcludeSemantics(...)", lambda c: G("ExcludeSemantics", child=c), True, "ExcludeSemantics only hides the child from screen readers"),
]


@template(TEMPLATES)
def wrapped_button(rng):
    picks = rng.sample(WRAPS, rng.randint(1, 2))
    btn: G = G("ElevatedButton", onPressed=hit(1), child=text("go"))
    for _, mkw, _, _ in reversed(picks):
        btn = mkw(btn)
    ok = all(p[2] for p in picks)
    blockers = [p for p in picks if not p[2]]
    why = (", ".join(p[3] for p in picks) + (": the tap gets through" if ok else f": {blockers[0][3]}, so the button never hears the tap"))
    return mk("n after a tap at 200, 150, the middle of the button", mat(G("Center", child=btn)), int(ok), f"{why[0].upper() + why[1:]}: n = {int(ok)}.",
              tap_at(200, 150) + RET, decls=ADD)


@template(TEMPLATES)
def ignored_inside_a_button(rng):
    inner = rng.choice((G("IgnorePointer", child=text("go")), G("AbsorbPointer", child=text("go")), G("Opacity", opacity="0", child=text("go"))))
    btn = G("ElevatedButton", onPressed=hit(1), child=inner)
    return mk("n after tapping the middle of the button", mat(G("Center", child=btn)), 1, f"{inner.name} is inside the button, so it only affects the label; the button "
              "itself takes the tap around it: n = 1.", "await tester.tap(find.byType(ElevatedButton));\nawait tester.pump();" + RET, decls=ADD)


@template(TEMPLATES)
def listener_and_detector(rng):
    arrangement = rng.choice(("nested", "top_opaque", "top_translucent", "top_defer"))
    if arrangement == "nested":
        w = G("Listener", onPointerDown=hit1(1), onPointerUp=hit1(10), child=mat(ink(100, box())))
        n, why = 111, "A Listener does not take part in the gesture arena: it hears down and up (1 + 10) and the InkWell inside still wins its tap (100)"
        ask, code = "n after one tap", "await tester.tap(find.byType(InkWell));\n" + PUMP
    else:
        beh = {"top_opaque": OPAQUE, "top_translucent": TRANSLUCENT, "top_defer": None}[arrangement]
        kw = {"behavior": beh} if beh else {}
        w = mat(G("Stack", children=[ink(100, box("a")), G("Listener", **kw, onPointerDown=hit1(1), child=box("b"))]))
        if arrangement == "top_opaque":
            n, why = 1, "The opaque Listener in front stops the hit test, so the InkWell behind never hears the pointer"
        elif arrangement == "top_translucent":
            n, why = 101, "The translucent Listener lets the hit test go on to the InkWell behind it, and both react"
        else:
            n, why = 100, "The Listener's Box child is empty and the default behavior defers to it, so the Listener is not hit; only the InkWell reacts"
        ask, code = ask_at(25, 25), tap_at(25, 25)
    return mk(ask, w, n, f"{why}: n = {n}.", code + RET, decls=ADD)


@template(TEMPLATES)
def radio_group(rng):
    value = rng.choice((1, 2))
    group = rng.choice((1, 2))
    toggle = rng.random() < 0.4
    decl = "int n = 0;\nvoid pick(int? v) {\n  n += v ?? 100;\n}"
    kw = {"value": str(value), "groupValue": str(group)}
    if toggle:
        kw["toggleable"] = "true"
    kw["onChanged"] = "pick"
    if value != group:
        n, why = value, f"The radio is not the selected one (value {value}, group value {group}), so tapping it reports its value"
    elif toggle:
        n, why = 100, "The radio is selected and toggleable: tapping it again reports null, which pick counts as 100"
    else:
        n, why = 0, "The radio is already the selected one, and an ordinary radio only reports a change"
    return mk("n after one tap", mat(G("Center", child=G("Radio<int>", **kw))), n, f"{why}: n = {n}.",
              "await tester.tap(find.byType(Radio<int>));\nawait tester.pump();" + RET, decls=decl)


@template(TEMPLATES)
def expansion_tile_taps(rng):
    initially = rng.random() < 0.5
    keep = rng.random() < 0.5
    taps = rng.randint(0, 3)
    kids = rng.randint(1, 3)
    expanded = initially if taps % 2 == 0 else not initially
    off = rng.random() < 0.5
    kw: dict = {"title": text("t")}
    if initially:
        kw["initiallyExpanded"] = "true"
    if keep:
        kw["maintainState"] = "true"
    kw["children"] = [text(chr(97 + i)) for i in range(kids)]
    if off:
        found = kids if (expanded or keep) else 0
    else:
        found = kids if expanded else 0
    finder = "find.byType(Text, skipOffstage: false)" if off else "find.byType(Text)"
    n = found + 1  # the tile's own title is one more Text
    why = (f"{taps} tap{'s' if taps != 1 else ''} on the title leave the tile {'expanded' if expanded else 'collapsed'}. "
           + ("An expanded tile shows its children" if expanded else
              ("A collapsed tile with maintainState keeps the children built, but offstage; skipOffstage: false still finds them" if keep and off else
               "A collapsed tile with maintainState keeps the children but offstage, and the default finder skips them" if keep else
               "A collapsed tile removes its children from the tree")) + f". Texts: the title + {found} = {n}.")
    pre = "".join("await tester.tap(find.text('t'));\nawait tester.pumpAndSettle();\n" for _ in range(taps))
    return mk(f"{finder} matches how many, after {taps} tap{'s' if taps != 1 else ''} on the title?", G("MaterialApp", home=mat(G("ExpansionTile", **kw))), n, why,
              pre + f"await tester.pumpAndSettle();\nreturn count({finder});")


@template(TEMPLATES)
def long_press_callbacks(rng):
    pool = [("onLongPressDown", "(_) => add(1)", 1), ("onLongPressStart", "(_) => add(10)", 10), ("onLongPress", "() => add(100)", 100),
            ("onLongPressUp", "() => add(1000)", 1000), ("onLongPressCancel", "() => add(10000)", 10000)]
    hs = rng.sample(pool, 2)
    action = rng.choice(("long", "tap"))
    fired = {"long": ("onLongPressDown", "onLongPressStart", "onLongPress", "onLongPressUp"), "tap": ("onLongPressDown", "onLongPressCancel")}[action]
    n = sum(v for name, _, v in hs if name in fired)
    why = ("Pressing for half a second is a long press: down, start, the press itself and the release all report" if action == "long"
           else "A quick tap is not a long press: the recognizer hears the pointer go down and then gives up, which is a cancel")
    code = ("await tester.longPress(find.byType(GestureDetector));" if action == "long" else "await tester.tap(find.byType(GestureDetector));")
    return mk("n after " + ("a long press" if action == "long" else "one quick tap"), pressable(**{name: c for name, c, _ in hs}), n,
              f"{why}: n = {n}.", code + "\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def finger_slop(rng):
    d = rng.choice((4, 8, 12, 15, 24, 30, 45))
    with_drag = rng.random() < 0.6
    kw = {"onTap": hit(1)}
    if with_drag:
        kw["onHorizontalDragEnd"] = hit1(10)
    if d < 18:
        n, why = 1, f"{d} pixels is within the 18 pixel touch slop, so the finger has not moved enough to cancel the tap"
    elif with_drag:
        n, why = 10, f"{d} pixels is past the 18 pixel slop: the tap gives up and the horizontal drag takes over"
    else:
        n, why = 0, f"{d} pixels is past the 18 pixel slop, so it is no longer a tap, and nothing else listens"
    code = (f"final g = await tester.startGesture(tester.getCenter(find.byType(GestureDetector)));\nawait g.moveBy(Offset({d}, 0));\n"
            "await tester.pump();\nawait g.up();")
    return mk(f"n after pressing, moving {d} px sideways, and letting go", pressable(**kw), n, f"{why}: n = {n}.", code + "\n" + PUMP + RET, decls=ADD)


@template(TEMPLATES)
def tapping_the_label(rng):
    kind = rng.choice(("SwitchListTile", "CheckboxListTile", "row_switch", "tile_checkbox"))
    pick = "(v) => add(1)"
    if kind == "SwitchListTile":
        w, n, why = G("SwitchListTile", value="false", onChanged=pick, title=text("a")), 1, "SwitchListTile makes the whole tile, label included, the switch"
    elif kind == "CheckboxListTile":
        w, n, why = G("CheckboxListTile", value="false", onChanged=pick, title=text("a")), 1, "CheckboxListTile makes the whole tile, label included, the checkbox"
    elif kind == "row_switch":
        w, n, why = row(G("Switch", value="false", onChanged=pick), text("a")), 0, "A Text next to a Switch is just a Text; only the Switch itself reacts"
    else:
        w, n, why = G("ListTile", leading=G("Checkbox", value="false", onChanged=pick), title=text("a")), 0, "The ListTile has no onTap of its own; only the Checkbox in its leading slot reacts"
    return mk("n after tapping the text 'a'", mat(G("Center", child=w)), n, f"{why}: n = {n}.", "await tester.tap(find.text('a'));\nawait tester.pump();" + RET, decls=ADD)


@template(TEMPLATES)
def button_inside_inkwell(rng):
    enabled = rng.random() < 0.6
    outer_first = rng.random() < 0.5
    btn = G("ElevatedButton", onPressed=hit(1) if enabled else "null", child=text("go"))
    if outer_first:
        w = ink(10, btn)
    else:
        w = G("Card", child=ink(10, G("Padding", padding="EdgeInsets.all(20)", child=btn)))
    n = 1 if enabled else 10
    why = ("The button is inside the InkWell and takes the tap itself: the deepest tap detector wins" if enabled
           else "A disabled button has no tap handler, so the tap goes to the InkWell around it")
    return mk("n after tapping the middle of the button", mat(G("Center", child=w)), n, f"{why}: n = {n}.",
              "await tester.tap(find.byType(ElevatedButton), warnIfMissed: false);\nawait tester.pump();" + RET, decls=ADD)
