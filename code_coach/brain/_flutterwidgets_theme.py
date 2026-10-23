"""Flutter widgets pack, activity 7: Theme Says.

What number does a descendant read from the widgets above it? The nearest ancestor of each kind wins:
DefaultTextStyle (replaced by a plain DefaultTextStyle, only added to by `.merge`), TextStyle on the Text itself,
MediaQuery's textScaler, IconTheme and Theme(iconTheme), Directionality (and the Start/End versions of
EdgeInsets and Alignment), MediaQuery (size, padding, SafeArea), Theme and MaterialApp's themeMode.

The test font makes text measurable: every glyph is a square as wide as the font size (Ahem), so a Text of 3
characters at font size 20 is 60 wide; the default font size is 14. An Icon is a box as wide as its size (24 unless a
theme or the Icon says otherwise). Directions: rtl starts at the right edge.
"""

from __future__ import annotations

import random

from ._flutterwidgets_kit import G, center, mk, row, template, text

TEMPLATES: list = []

DEFAULT_FONT = 14
ICON_DEFAULT = 24
KEY = "Key('t')"


def label(rng: random.Random, n: int | None = None) -> str:
    return "".join(rng.choice("abcdefgh") for _ in range(n or rng.randint(2, 4)))


def keyed_text(s: str, **kw) -> G:
    return G("Text", f"'{s}'", key=KEY, **kw)


def keyed_icon(**kw) -> G:
    return G("Icon", "Icons.add", key="Key('i')", **kw)


def box(id_: str, w: int = 50, h: int = 50) -> G:
    kw = {}
    if w != 50:
        kw["w"] = str(w)
    if h != 50:
        kw["h"] = str(h)
    return G("Box", f"'{id_}'", **kw)


def ts(**kw) -> str:
    return "TextStyle(" + ", ".join(f"{k}: {v}" for k, v in kw.items()) + ")"


def num(v: float) -> str:
    return str(int(v)) if float(v) == int(v) else str(v)


# ── text ────────────────────────────────────────────────────────────────

@template(TEMPLATES)
def default_text_style_levels(rng):
    n = label(rng)
    a = rng.choice((10, 20, 30))
    b = rng.choice([x for x in (10, 20, 30, 40) if x != a])
    kind = rng.choice(("replace_color", "replace_size", "merge_color", "merge_size"))
    if kind == "replace_color":
        inner = G("DefaultTextStyle", style=ts(color="Colors.red"), child=center(keyed_text(n)))
        size, why = DEFAULT_FONT, "A plain DefaultTextStyle REPLACES the one above; its style has no fontSize, so the text falls back to the default 14"
    elif kind == "replace_size":
        inner = G("DefaultTextStyle", style=ts(fontSize=b), child=center(keyed_text(n)))
        size, why = b, f"The inner DefaultTextStyle replaces the outer one and says {b}"
    elif kind == "merge_color":
        inner = G("DefaultTextStyle.merge", style=ts(color="Colors.red"), child=center(keyed_text(n)))
        size, why = a, f"DefaultTextStyle.merge adds its colour to the style above and keeps the outer fontSize {a}"
    else:
        inner = G("DefaultTextStyle.merge", style=ts(fontSize=b), child=center(keyed_text(n)))
        size, why = b, f"DefaultTextStyle.merge lets its own fontSize {b} win over the outer {a}"
    w = G("DefaultTextStyle", style=ts(fontSize=a), child=inner)
    return mk("width of t", w, len(n) * size, f"Each glyph is as wide as the font size: {len(n)} x {size}. {why}.", "w('t')")


@template(TEMPLATES)
def text_style_over_default(rng):
    n = label(rng)
    a, b = rng.sample((10, 20, 30, 40), 2)
    kind = rng.choice(("size", "color", "inherit_false", "inherit_false_size", "height", "bold"))
    if kind == "size":
        style, size, why = ts(fontSize=b), b, f"The Text's own fontSize {b} beats the DefaultTextStyle's {a}"
    elif kind == "color":
        style, size, why = ts(color="Colors.red"), a, f"A style without fontSize leaves the inherited {a} alone"
    elif kind == "inherit_false":
        style, size, why = ts(inherit="false", color="Colors.red"), DEFAULT_FONT, "inherit: false ignores the DefaultTextStyle completely, so the size is the default 14"
    elif kind == "inherit_false_size":
        style, size, why = ts(inherit="false", fontSize=b), b, f"inherit: false keeps only this style, which says {b}"
    elif kind == "height":
        style, size, why = ts(height=2), a, f"height changes the line height, not the glyph width; the inherited {a} stays"
    else:
        style, size, why = ts(fontWeight="FontWeight.bold"), a, f"A weight does not change the size; the inherited {a} stays"
    w = G("DefaultTextStyle", style=ts(fontSize=a), child=center(keyed_text(n, style=style)))
    return mk("width of t", w, len(n) * size, f"{len(n)} glyphs x {size}. {why}.", "w('t')")


@template(TEMPLATES)
def text_scaler_from_media_query(rng):
    n = label(rng)
    a = rng.choice((10, 20))
    k = rng.choice((2, 3, 0.5))
    kind = rng.choice(("plain", "noscale", "own", "nested"))
    inner_text = keyed_text(n)
    size, why = a * k, f"The MediaQuery's textScaler multiplies the font size: {a} x {num(k)}"
    child = center(inner_text)
    if kind == "noscale":
        child = center(keyed_text(n, textScaler="TextScaler.noScaling"))
        size, why = a, "The Text says textScaler: noScaling, which beats the MediaQuery"
    elif kind == "own":
        j = rng.choice((1, 3))
        child = center(keyed_text(n, textScaler=f"TextScaler.linear({j})"))
        size, why = a * j, f"The Text's own textScaler ({j}) beats the MediaQuery's"
    elif kind == "nested":
        j = rng.choice((1, 3))
        child = G("MediaQuery", data=f"MediaQueryData(textScaler: TextScaler.linear({j}))", child=center(inner_text))
        size, why = a * j, f"The nearest MediaQuery wins: its textScaler is {j}"
    w = G("MediaQuery", data=f"MediaQueryData(textScaler: TextScaler.linear({num(k)}))",
          child=G("DefaultTextStyle", style=ts(fontSize=a), child=child))
    width = len(n) * size
    return mk("width of t", w, num(width), f"{why}; {len(n)} glyphs of width {num(size)} = {num(width)}.", "w('t')")


# ── icons ───────────────────────────────────────────────────────────────

@template(TEMPLATES)
def icon_theme_levels(rng):
    a = rng.choice((16, 30, 40))
    b = rng.choice([x for x in (16, 32, 48) if x != a])
    kind = rng.choice(("plain", "replace_color", "merge_color", "replace_size", "own", "none"))
    icon = keyed_icon()
    if kind == "plain":
        inner, size, why = icon, a, f"The nearest IconTheme says {a}"
    elif kind == "replace_color":
        inner, size, why = G("IconTheme", data="IconThemeData(color: Colors.red)", child=icon), ICON_DEFAULT, "A plain IconTheme replaces the one above; without a size the Icon falls back to 24"
    elif kind == "merge_color":
        inner, size, why = G("IconTheme.merge", data="IconThemeData(color: Colors.red)", child=icon), a, f"IconTheme.merge keeps the size {a} from above"
    elif kind == "replace_size":
        inner, size, why = G("IconTheme", data=f"IconThemeData(size: {b})", child=icon), b, f"The inner IconTheme replaces the outer and says {b}"
    elif kind == "own":
        inner, size, why = keyed_icon(size=str(b)), b, f"The Icon's own size {b} beats every IconTheme"
    else:
        return mk("width of i", center(keyed_icon()), ICON_DEFAULT, "No IconTheme anywhere: an Icon is 24 wide.", "w('i')")
    w = G("IconTheme", data=f"IconThemeData(size: {a})", child=center(inner))
    return mk("width of i", w, size, f"{why}: {size}.", "w('i')")


@template(TEMPLATES)
def theme_icon_size(rng):
    a = rng.choice((16, 32, 48))
    b = rng.choice([x for x in (20, 36, 52) if x != a])
    kind = rng.choice(("outer", "inner", "inner_default", "icon_theme_inside"))
    icon = keyed_icon()
    theme = lambda size, child: G("Theme", data=f"ThemeData(iconTheme: IconThemeData(size: {size}))", child=child)  # noqa: E731
    if kind == "outer":
        w, size, why = theme(a, center(icon)), a, f"Theme(iconTheme) reaches the Icon: {a}"
    elif kind == "inner":
        w, size, why = theme(a, theme(b, center(icon))), b, f"The nearer Theme wins: {b}"
    elif kind == "inner_default":
        w, size, why = theme(a, G("Theme", data="ThemeData()", child=center(icon))), ICON_DEFAULT, "A fresh ThemeData() does not inherit anything: no icon size, so 24"
    else:
        w, size, why = theme(a, G("IconTheme", data=f"IconThemeData(size: {b})", child=center(icon))), b, f"An IconTheme below the Theme is nearer: {b}"
    return mk("width of i", w, size, f"{why}.", "w('i')")


@template(TEMPLATES)
def icon_button_size(rng):
    a = rng.choice((16, 40, 56))
    b = rng.choice((20, 32))
    kind = rng.choice(("iconSize", "own", "default", "outer"))
    ikw = {}
    bkw: dict = {}
    if kind == "iconSize":
        bkw["iconSize"] = str(a)
        size, why = a, f"IconButton(iconSize: {a}) gives its icon that size"
    elif kind == "own":
        bkw["iconSize"] = str(a)
        ikw["size"] = str(b)
        size, why = b, f"The Icon's own size {b} beats the IconButton's iconSize"
    elif kind == "default":
        size, why = ICON_DEFAULT, "IconButton's iconSize defaults to 24"
    else:
        size, why = 48, "IconButton takes its default iconSize from the IconTheme above it (24 only when there is none)"
    btn = G("IconButton", **bkw, onPressed="null", icon=keyed_icon(**ikw))
    inner = center(btn)
    if kind == "outer":
        inner = G("IconTheme", data="IconThemeData(size: 48)", child=inner)
    return mk("width of i", G("MaterialApp", home=G("Material", child=inner)), size, f"{why}: {size}.", "w('i')")


# ── directions ──────────────────────────────────────────────────────────

def row_x(widths: list[int], align: str, rtl: bool) -> list[int]:
    total = sum(widths)
    free = 400 - total
    if rtl:
        block = {"start": free, "end": 0, "center": free / 2}[align]
        out, cum = [], 0
        for w in widths:
            out.append(block + total - cum - w)
            cum += w
        return out
    block = {"start": 0, "end": free, "center": free / 2}[align]
    out, cum = [], 0
    for w in widths:
        out.append(block + cum)
        cum += w
    return out


def direction_wrap(rtl: bool, child) -> G:
    return G("Directionality", textDirection="TextDirection.rtl" if rtl else "TextDirection.ltr", child=child)


@template(TEMPLATES)
def rtl_row_positions(rng):
    widths = [rng.choice((50, 100, 150)) for _ in range(rng.randint(2, 3))]
    ids = "abc"[:len(widths)]
    align = rng.choice(("start", "start", "end", "center"))
    rtl = rng.random() < 0.65
    via_row = rng.random() < 0.3
    kw = {}
    if align != "start":
        kw["mainAxisAlignment"] = f"MainAxisAlignment.{align}"
    kids = [box(i, w) for i, w in zip(ids, widths)]
    if via_row:
        r = G("Row", **kw, textDirection="TextDirection.rtl" if rtl else "TextDirection.ltr", children=kids)
        w = r
    else:
        r = G("Row", **kw, children=kids)
        w = direction_wrap(rtl, r) if rtl or rng.random() < 0.3 else r
    k = rng.randrange(len(widths))
    xs = row_x(widths, align, rtl)
    return mk(f"left edge of {ids[k]}", w, num(xs[k]), f"The row is laid out {'right to left' if rtl else 'left to right'}; "
              f"{'start is the right edge and end the left' if rtl else 'start is the left edge'}; the widths are {widths}, so {ids[k]} starts at {num(xs[k])}.", f"x('{ids[k]}')")


@template(TEMPLATES)
def directional_padding_and_align(rng):
    s = rng.choice((20, 40, 60))
    rtl = rng.random() < 0.6
    al = rng.choice(("Alignment.topLeft", "AlignmentDirectional.topStart", "AlignmentDirectional.topEnd", "Alignment.topRight"))
    pd = rng.choice((f"EdgeInsets.only(left: {s})", f"EdgeInsetsDirectional.only(start: {s})", f"EdgeInsets.only(right: {s})", f"EdgeInsetsDirectional.only(end: {s})"))
    block = 50 + s
    # which side of the block the padding is on, and where the block sits
    pad_left = (pd.startswith("EdgeInsets.only(left") or (pd.startswith("EdgeInsetsDirectional.only(start") and not rtl) or (pd.startswith("EdgeInsetsDirectional.only(end") and rtl))
    left_aligned = al in ("Alignment.topLeft",) or (al == "AlignmentDirectional.topStart" and not rtl) or (al == "AlignmentDirectional.topEnd" and rtl)
    block_x = 0 if left_aligned else 400 - block
    x = block_x + (s if pad_left else 0)
    w = direction_wrap(rtl, G("Align", alignment=al, child=G("Padding", padding=pd, child=box("a"))))
    return mk("left edge of a", w, x, f"Under {'rtl' if rtl else 'ltr'}: the padded block is {block} wide and sits at the {'left' if left_aligned else 'right'} edge "
              f"(x = {block_x}); the padding is on its {'left' if pad_left else 'right'}, so a starts at {x}.", "x('a')")


@template(TEMPLATES)
def align_left_or_start(rng):
    rtl = rng.random() < 0.6
    al, ax = rng.choice([("Alignment.centerLeft", -1), ("Alignment.centerRight", 1), ("Alignment.center", 0),
                         ("AlignmentDirectional.centerStart", "start"), ("AlignmentDirectional.centerEnd", "end"), ("AlignmentDirectional(1, 0)", "end")])
    if ax == "start":
        ax = 1 if rtl else -1
    elif ax == "end":
        ax = -1 if rtl else 1
    x = {-1: 0, 0: 175, 1: 350}[ax]
    w = direction_wrap(rtl, G("Align", alignment=al, child=box("a")))
    return mk("left edge of a", w, x, f"{al} is {'fixed to a side' if 'Directional' not in al else 'relative to the text direction'}; here "
              f"({'rtl' if rtl else 'ltr'}) it puts the 50 wide box {'at the left edge' if x == 0 else 'in the middle' if x == 175 else 'at the right edge'}: {x}.", "x('a')")


@template(TEMPLATES)
def nested_directionality_x(rng):
    layers = [rng.random() < 0.5 for _ in range(rng.randint(2, 3))]
    w = row(box("a"), box("b"))
    for rtl in reversed(layers):
        w = direction_wrap(rtl, w)
    rtl_now = layers[-1]
    k = rng.choice("ab")
    x = (400 - 50 if k == "a" else 400 - 100) if rtl_now else (0 if k == "a" else 50)
    return mk(f"left edge of {k}", w, x, f"The nearest Directionality is {'rtl' if rtl_now else 'ltr'}: the row starts at the {'right' if rtl_now else 'left'}, "
              f"so {k} is at {x}.", f"x('{k}')")


@template(TEMPLATES)
def stack_alignment_directional(rng):
    rtl = rng.random() < 0.6
    al = rng.choice(["AlignmentDirectional.topEnd", "AlignmentDirectional.topStart", "Alignment.topRight", "AlignmentDirectional.bottomEnd", "Alignment.bottomLeft"])
    horiz = "end" if "End" in al else "start" if "Start" in al else ("right" if "Right" in al else "left")
    right = (not rtl) if horiz == "end" else rtl if horiz == "start" else horiz == "right"
    x = 350 if right else 0
    y = 250 if "bottom" in al else 0
    prop = rng.choice(("x", "y"))
    w = direction_wrap(rtl, G("Stack", alignment=al, children=[box("a")]))
    return mk(f"{'left edge' if prop == 'x' else 'top'} of a", w, x if prop == "x" else y, f"The Stack puts its 50 x 50 child at the {'right' if right else 'left'} "
              f"{'bottom' if y else 'top'} corner ({'rtl' if rtl else 'ltr'}): x = {x}, y = {y}.", f"{prop}('a')")


@template(TEMPLATES)
def column_cross_axis_rtl(rng):
    rtl = rng.random() < 0.6
    ca = rng.choice(("start", "end", "center"))
    wd = rng.choice((100, 150))
    free = 400 - wd
    if ca == "center":
        x = free / 2
    else:
        left = (ca == "start") != rtl
        x = 0 if left else free
    w = direction_wrap(rtl, G("Column", crossAxisAlignment=f"CrossAxisAlignment.{ca}", children=[box("a", wd)]))
    return mk("left edge of a", w, num(x), f"In a Column, crossAxisAlignment.{ca} means the {'leading' if ca == 'start' else 'trailing' if ca == 'end' else 'middle'} side, "
              f"which is {'the right' if rtl else 'the left'} edge for 'start' under {'rtl' if rtl else 'ltr'}: x = {num(x)}.", "x('a')")


@template(TEMPLATES)
def wrap_direction(rng):
    rtl = rng.random() < 0.6
    ws = [rng.choice((50, 100)) for _ in range(3)]
    align = rng.choice(("start", "end"))
    kw = {} if align == "start" else {"alignment": "WrapAlignment.end"}
    k = rng.randrange(3)
    xs = row_x(ws, align, rtl)
    w = direction_wrap(rtl, G("Wrap", **kw, children=[box("abc"[i], ws[i]) for i in range(3)]))
    return mk(f"left edge of {'abc'[k]}", w, num(xs[k]), f"A Wrap follows the text direction like a Row ({'right to left' if rtl else 'left to right'}), all three fit on one run: "
              f"{'abc'[k]} starts at {num(xs[k])}.", f"x('{'abc'[k]}')")


@template(TEMPLATES)
def direction_read_by_a_builder(rng):
    layers = [rng.random() < 0.5 for _ in range(rng.randint(1, 3))]
    via_row = rng.random() < 0.3
    reader = G("Builder", builder="(c) => Text('${Directionality.of(c).index}')")
    if via_row:
        inner = G("Row", textDirection="TextDirection.rtl", children=[reader])
        now = layers[-1] if layers else True
    else:
        inner, now = reader, layers[-1]
    w = inner
    for rtl in reversed(layers):
        w = direction_wrap(rtl, w)
    ans = 0 if now else 1  # TextDirection.rtl.index is 0, ltr is 1; `now` is True when the nearest layer is rtl
    return mk("the number the Text shows (TextDirection.rtl.index is 0, ltr is 1)", w, ans, ("Row(textDirection:) only changes how the Row lays out; it does not change the Directionality its children read, so the nearest Directionality "
                                                                                             "answers" if via_row else "The nearest Directionality wins")
              + f": {'rtl' if ans == 0 else 'ltr'}, index {ans}.", "tester.widget<Text>(find.byType(Text)).data")


# ── media query and safe area ───────────────────────────────────────────

MQ_VALUES = [("size.width.toInt()", 400), ("size.height.toInt()", 300), ("size.shortestSide.toInt()", 300), ("size.longestSide.toInt()", 400),
             ("devicePixelRatio.toInt()", 1), ("orientation.index", 1), ("padding.top.toInt()", 0), ("textScaler.scale(10).toInt()", 10),
             ("platformBrightness.index", 1), ("size.width ~/ 100", 4), ("size.height ~/ 100", 3)]


@template(TEMPLATES)
def media_query_of_the_test_screen(rng):
    expr, val = rng.choice(MQ_VALUES)
    w = G("MaterialApp", home=G("Builder", builder="(c) => Text('${MediaQuery.of(c).%s}')" % expr))
    return mk("the number the Text shows", w, val, "The test screen is 400 x 300 logical pixels at devicePixelRatio 1, with no insets, "
              "text scale 1 and a light platform (Orientation.landscape has index 1, Brightness.light index 1)"
              f"; so MediaQuery.of(c).{expr} is {val}.", "tester.widget<Text>(find.byType(Text)).data")


@template(TEMPLATES)
def media_query_vs_layout_builder(rng):
    s1, s2 = rng.choice((100, 200, 300)), rng.choice((100, 150))
    wd = rng.choice((120, 160, 240))
    form = rng.choice(("mq", "lb", "diff"))
    if form == "mq":
        expr, val, why = "MediaQuery.of(c).size.width.toInt()", s1, f"MediaQuery says how big the MediaQuery widget above claims the screen is: {s1}"
        inner = G("Builder", builder=f"(c) => Text('${{{expr}}}')")
    elif form == "lb":
        expr, val, why = "bc.maxWidth.toInt()", wd, f"LayoutBuilder reports the space its own parent gives it, the {wd} wide SizedBox, not the screen"
        inner = G("LayoutBuilder", builder=f"(c, bc) => Text('${{{expr}}}')")
    else:
        expr = "MediaQuery.of(c).size.width.toInt() - bc.maxWidth.toInt()"
        val, why = s1 - wd, f"MediaQuery says {s1} and the box is {wd}, so the difference is {s1 - wd}"
        inner = G("LayoutBuilder", builder=f"(c, bc) => Text('${{{expr}}}')")
    w = G("MediaQuery", data=f"MediaQueryData(size: Size({s1}, {s2}))", child=center(G("SizedBox", width=str(wd), child=inner)))
    return mk("the number the Text shows", w, val, f"{why}.", "tester.widget<Text>(find.byType(Text)).data", width=110)


@template(TEMPLATES)
def safe_area_sides(rng):
    pads = [rng.choice((0, 10, 20, 30, 40)) for _ in range(4)]  # l t r b
    flags = {s: rng.random() < 0.7 for s in ("left", "top", "right", "bottom")}
    minimum = rng.choice((0, 0, 15))
    insets = [max(p if flags[s] else 0, minimum) for p, s in zip(pads, ("left", "top", "right", "bottom"))]
    kw = {s: "false" for s, on in flags.items() if not on}
    if minimum:
        kw["minimum"] = f"EdgeInsets.all({minimum})"
    prop = rng.choice(("x", "y", "w", "h"))
    val = {"x": insets[0], "y": insets[1], "w": 400 - insets[0] - insets[2], "h": 300 - insets[1] - insets[3]}[prop]
    names = {"x": "left edge", "y": "top", "w": "width", "h": "height"}
    mqd = "MediaQueryData(padding: EdgeInsets.fromLTRB(%d, %d, %d, %d))" % tuple(pads)
    w = G("MediaQuery", data=mqd, child=G("SafeArea", **kw, child=box("a")))
    return mk(f"{names[prop]} of a", w, val, f"SafeArea pads each side by the MediaQuery padding (left, top, right, bottom = {pads}) unless that side is switched off"
              + (f", but at least {minimum} (minimum)" if minimum else "") + f". Insets used: {insets}; the box fills the rest: {val}.", f"{prop}('a')")


@template(TEMPLATES)
def safe_area_consumes_padding(rng):
    t = rng.choice((20, 24, 40))
    chain = [rng.choice(("pad", "safe", "safe", "safe_no_top")) for _ in range(rng.randint(2, 3))]
    y, consumed = 0, False
    w: G = box("a")
    for kind in reversed(chain):
        w = (G("Padding", padding="EdgeInsets.all(10)", child=w) if kind == "pad" else G("SafeArea", child=w) if kind == "safe"
             else G("SafeArea", top="false", child=w))
    for kind in chain:
        if kind == "pad":
            y += 10
        elif kind == "safe" and not consumed:
            y += t
            consumed = True
    w = G("MediaQuery", data=f"MediaQueryData(padding: EdgeInsets.only(top: {t}))", child=w)
    return mk("top of a", w, y, f"The top padding is {t}. The first SafeArea that looks after the top applies it and then removes it from the MediaQuery below, so a second "
              f"SafeArea adds nothing (SafeArea(top: false) leaves it alone); each Padding adds 10: top = {y}.", "y('a')")


# ── Theme and MaterialApp ───────────────────────────────────────────────

TEXT_SIZES = {"displayLarge": 57, "displayMedium": 45, "displaySmall": 36, "headlineLarge": 32, "headlineMedium": 28, "headlineSmall": 24,
              "titleLarge": 22, "titleMedium": 16, "titleSmall": 14, "bodyLarge": 16, "bodyMedium": 14, "bodySmall": 12,
              "labelLarge": 14, "labelMedium": 12, "labelSmall": 11}


@template(TEMPLATES)
def default_text_theme_sizes(rng):
    name = rng.choice(list(TEXT_SIZES))
    w = G("MaterialApp", home=G("Builder", builder="(c) => Text('${Theme.of(c).textTheme.%s!.fontSize!.toInt()}')" % name))
    return mk("the number the Text shows", w, TEXT_SIZES[name], f"Material 3's default type scale gives {name} a font size of {TEXT_SIZES[name]}.",
              "tester.widget<Text>(find.byType(Text)).data")


@template(TEMPLATES)
def theme_text_override(rng):
    a = rng.choice((18, 20, 30))
    b = rng.choice([x for x in (12, 26, 40) if x != a])
    read = rng.choice(("bodyMedium", "bodyMedium", "bodyLarge", "titleLarge"))
    levels = rng.choice(("one", "nested", "reset"))
    reader = G("Builder", builder="(c) => Text('${Theme.of(c).textTheme.%s!.fontSize!.toInt()}')" % read)
    t1 = f"ThemeData(textTheme: TextTheme(bodyMedium: TextStyle(fontSize: {a})))"
    default = TEXT_SIZES[read]
    if levels == "one":
        w = G("Theme", data=t1, child=reader)
        val = a if read == "bodyMedium" else default
        why = f"The Theme sets bodyMedium to {a}" + ("" if read == "bodyMedium" else f"; {read} was not touched, so it keeps its default {default}")
    elif levels == "nested":
        w = G("Theme", data=t1, child=G("Theme", data=f"ThemeData(textTheme: TextTheme(bodyMedium: TextStyle(fontSize: {b})))", child=reader))
        val = b if read == "bodyMedium" else default
        why = f"The nearer Theme sets bodyMedium to {b}" + ("" if read == "bodyMedium" else f"; {read} keeps its default {default}")
    else:
        w = G("Theme", data=t1, child=G("Theme", data="ThemeData()", child=reader))
        val, why = default, f"A fresh ThemeData() starts from the defaults again, so {read} is {default}"
    return mk("the number the Text shows", w, val, f"{why}.", "tester.widget<Text>(find.byType(Text)).data", width=110)


@template(TEMPLATES)
def material_app_theme_mode(rng):
    mode = rng.choice(("system", "light", "dark"))
    has_theme = rng.random() < 0.7
    has_dark = rng.random() < 0.7
    tb = rng.choice(("light", "dark"))
    db = rng.choice(("dark", "dark", "light"))
    kw = {}
    if has_theme:
        kw["theme"] = f"ThemeData(brightness: Brightness.{tb})"
    if has_dark:
        kw["darkTheme"] = f"ThemeData(brightness: Brightness.{db})"
    if mode != "system":
        kw["themeMode"] = f"ThemeMode.{mode}"
    theme_b = tb if has_theme else "light"
    if mode == "dark":
        chosen = db if has_dark else theme_b
        why = "themeMode.dark picks darkTheme" + ("" if has_dark else " - but there is none, so the plain theme is used")
    else:
        chosen = theme_b
        why = f"themeMode.{mode} picks theme" + (" (the test platform is light, so system mode does too)" if mode == "system" else "") + ("" if has_theme else ", which defaults to a light theme")
    ans = 0 if chosen == "dark" else 1
    w = G("MaterialApp", **kw, home=G("Builder", builder="(c) => Text('${Theme.of(c).brightness.index}')"))
    return mk("the number the Text shows (Brightness.dark.index is 0, light is 1)", w, ans, f"{why[0].upper() + why[1:]}: the brightness is {chosen}, index {ans}.",
              "tester.widget<Text>(find.byType(Text)).data")


@template(TEMPLATES)
def widget_default_text_sizes(rng):
    n = label(rng, rng.randint(2, 4))
    kind = rng.choice(["appbar", "list_title", "list_sub", "text_button", "elevated", "chip", "dialog_title", "dialog_content", "scaffold_body", "material_style"])
    t = keyed_text(n)
    a = rng.choice((10, 20, 30))
    if kind == "appbar":
        w, size = G("Scaffold", appBar=G("AppBar", title=t)), 22
        why = "An AppBar title uses titleLarge, 22"
    elif kind == "list_title":
        w, size = G("Scaffold", body=G("ListTile", title=t)), 16
        why = "A ListTile's title uses bodyLarge, 16"
    elif kind == "list_sub":
        w, size = G("Scaffold", body=G("ListTile", title=text("x"), subtitle=t)), 14
        why = "A ListTile's subtitle uses bodyMedium, 14"
    elif kind == "text_button":
        w, size = G("Scaffold", body=center(G("TextButton", onPressed="null", child=t))), 14
        why = "A button's label uses labelLarge, 14"
    elif kind == "elevated":
        w, size = G("Scaffold", body=center(G("ElevatedButton", onPressed="null", child=t))), 14
        why = "A button's label uses labelLarge, 14"
    elif kind == "chip":
        w, size = G("Scaffold", body=center(G("Chip", label=t))), 14
        why = "A Chip's label uses labelLarge, 14"
    elif kind == "dialog_title":
        w, size = G("Scaffold", body=G("AlertDialog", title=t)), 24
        why = "An AlertDialog's title uses headlineSmall, 24"
    elif kind == "dialog_content":
        w, size = G("Scaffold", body=G("AlertDialog", content=t)), 14
        why = "An AlertDialog's content uses bodyMedium, 14"
    elif kind == "scaffold_body":
        w, size = G("Scaffold", body=center(t)), 14
        why = "A Scaffold's body sits on a Material whose default text style is bodyMedium, 14"
    else:
        w, size = G("Scaffold", body=G("Material", textStyle=ts(fontSize=a), child=center(t))), a
        why = f"Material(textStyle:) sets the default style for its children: {a}"
    return mk("font size around t (DefaultTextStyle)", G("MaterialApp", home=w), size, f"{why}: {size}.",
              "DefaultTextStyle.of(tester.element(find.byKey(Key('t')))).style.fontSize!.toInt()", width=100)


@template(TEMPLATES)
def text_style_merge_chain(rng):
    n = label(rng)
    levels = []
    cur = None  # the font size the Text will inherit (None: the default 14)
    for _ in range(2):
        merge = rng.random() < 0.5
        sized = rng.random() < 0.5
        size = rng.choice((10, 20, 30, 40))
        levels.append((merge, sized, size))
        if merge:
            cur = size if sized else cur
        else:
            cur = size if sized else None
    code: G = center(keyed_text(n))
    for merge, sized, size in reversed(levels):
        style = ts(fontSize=size) if sized else ts(color="Colors.red")
        code = G("DefaultTextStyle.merge" if merge else "DefaultTextStyle", style=style, child=code)
    final = DEFAULT_FONT if cur is None else cur
    return mk("width of t", code, len(n) * final, f"Work from the outside in: .merge adds to the style above, a plain DefaultTextStyle replaces it. "
              f"The font size reaching the Text is {final}{' (nothing set one: the default)' if cur is None else ''}; {len(n)} x {final}.", "w('t')")


@template(TEMPLATES)
def resolve_directional(rng):
    rtl = rng.random() < 0.5
    d = "TextDirection.rtl" if rtl else "TextDirection.ltr"
    if rng.random() < 0.6:
        s, e, t, b = (rng.choice((5, 10, 20, 30)) for _ in range(4))
        side = rng.choice(("left", "right", "top", "bottom"))
        val = {"left": e if rtl else s, "right": s if rtl else e, "top": t, "bottom": b}[side]
        expr = f"EdgeInsetsDirectional.fromSTEB({s}, {t}, {e}, {b}).resolve({d}).{side}.toInt()"
        why = f"fromSTEB is start, top, end, bottom; under {'rtl' if rtl else 'ltr'} start is the {'right' if rtl else 'left'} side, so {side} is {val}"
    else:
        al, ax = rng.choice([("AlignmentDirectional.centerStart", "start"), ("AlignmentDirectional.centerEnd", "end"), ("AlignmentDirectional.center", "mid")])
        val = 0 if ax == "mid" else (-1 if (ax == "start") != rtl else 1)
        expr = f"{al}.resolve({d}).x.toInt()"
        why = f"{al} is {'the start side' if ax == 'start' else 'the end side' if ax == 'end' else 'the middle'}, which is x = {val} under {'rtl' if rtl else 'ltr'} (-1 is left, 1 is right)"
    return mk("the number the Text shows", G("Text", "'${" + expr + "}'"), val, f"{why}.", "tester.widget<Text>(find.byType(Text)).data")


@template(TEMPLATES)
def text_scaling_wrappers(rng):
    k = rng.choice((2, 3))
    kind = rng.choice(("plain", "none", "clamp_low", "clamp_high", "nested"))
    read = G("Builder", builder="(c) => Text('${MediaQuery.textScalerOf(c).scale(10).toInt()}')")
    if kind == "plain":
        inner, val, why = read, 10 * k, f"The MediaQuery's textScaler is linear({k}), so scale(10) is {10 * k}"
    elif kind == "none":
        inner, val, why = G("MediaQuery.withNoTextScaling", child=read), 10, "withNoTextScaling resets the scaler to 1"
    elif kind == "clamp_low":
        lo = k + 1
        inner, val, why = G("MediaQuery.withClampedTextScaling", minScaleFactor=str(lo), child=read), 10 * lo, f"The scale {k} is clamped up to the minimum {lo}"
    elif kind == "clamp_high":
        hi = 1
        inner, val, why = G("MediaQuery.withClampedTextScaling", maxScaleFactor=str(hi), child=read), 10 * hi, f"The scale {k} is clamped down to the maximum {hi}"
    else:
        j = k + 2
        inner, val, why = G("MediaQuery", data=f"MediaQueryData(textScaler: TextScaler.linear({j}))", child=read), 10 * j, f"The nearer MediaQuery wins: linear({j})"
    w = G("MediaQuery", data=f"MediaQueryData(textScaler: TextScaler.linear({k}))", child=inner)
    return mk("the number the Text shows", w, val, f"{why}: {val}.", "tester.widget<Text>(find.byType(Text)).data")
