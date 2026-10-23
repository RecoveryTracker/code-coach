"""Flutter widgets pack, activity 3: List Build.

A scrolling list builds only what it needs: the items on screen plus a cache area (250 pixels by default) beyond the
viewport. The root of every example is the 400 x 300 screen, so a plain vertical list has a 300 pixel viewport and builds
every item that starts before 300 + 250 = 550 pixels. The checks ask for two different things:

* "visible" - `find.byType(Text)` skips what is outside the viewport (it is offstage), so it counts the items on screen;
* "built" - `find.byType(Text, skipOffstage: false)` also counts the cache area.

Items are fixed-size `SizedBox(height: h, child: Text('$i'))` (or width for a horizontal list), so every count is a few
lines of arithmetic. The model loops over the items (`items_in`) instead of using one clever formula.
"""

from __future__ import annotations


from ._flutter_model import Retry
from ._flutterwidgets_kit import G, center, col, mk, template

TEMPLATES: list = []

CACHE = 250.0
VIEW_H, VIEW_W = 300.0, 400.0
HEIGHTS = (40, 50, 60, 75, 80, 100, 120, 150)

VISIBLE = "count(find.byType(Text))"
BUILT = "count(find.byType(Text, skipOffstage: false))"
ASK_VISIBLE = "items on screen: find.byType(Text)"
ASK_BUILT = "items built: find.byType(Text, skipOffstage: false)"
FIRST = "tester.widgetList<Text>(find.byType(Text)).first.data"
LAST = "tester.widgetList<Text>(find.byType(Text)).last.data"


def items_in(n: int, size: float, pitch: float, first: float, low: float, high: float, inclusive: bool = False) -> list[int]:
    """The indexes of the items (extent `size`, one every `pitch`, the first at `first`) that overlap [low, high):
    visible ones use strict edges, the built (cache) range keeps an item that ends exactly at `low`."""
    out = []
    for i in range(n):
        start = first + i * pitch
        end = start + size
        if (end >= low if inclusive else end > low) and start < high:
            out.append(i)
    return out


def visible(n, size, pitch=None, first=0.0, off=0.0, view=VIEW_H):
    return items_in(n, size, pitch or size, first, off, off + view)


def built(n, size, pitch=None, first=0.0, off=0.0, view=VIEW_H, cache=CACHE):
    return items_in(n, size, pitch or size, first, off - min(cache, off), off + view + cache, inclusive=True)


def tile(h: int, horizontal: bool = False) -> str:
    return f"SizedBox({'width' if horizontal else 'height'}: {h}, child: Text('$i'))"


def builder(n: int, h: int, **kw) -> G:
    """ListView.builder(itemCount: n, itemBuilder: (c, i) => SizedBox(height: h, child: Text('$i')))"""
    return G("ListView.builder", **kw, itemCount=str(n), itemBuilder=f"(c, i) => {tile(h, kw.get('scrollDirection') == 'Axis.horizontal')}")


def jump_check(off: int, tail: str) -> str:
    return ("tester.state<ScrollableState>(find.byType(Scrollable)).position.jumpTo(%d);\nawait tester.pump();\nreturn %s;"
            % (off, tail))


# ── at the top of a plain vertical list ─────────────────────────────────

@template(TEMPLATES)
def builder_built(rng):
    h = rng.choice(HEIGHTS)
    n = rng.choice((3, 4, 5, 8, 12, 40, 60, 99, 100))
    got = len(built(n, h))
    return mk(ASK_BUILT, builder(n, h), got, f"The viewport is 300 tall and the cache adds 250 below it: items starting before 550 are built, "
              f"{h} apart" + (f", but there are only {n}" if got == n else "") + f": {got}.", BUILT)


@template(TEMPLATES)
def builder_visible(rng):
    h = rng.choice(HEIGHTS)
    n = rng.choice((3, 4, 5, 8, 40, 60, 99))
    got = len(visible(n, h))
    return mk(ASK_VISIBLE, builder(n, h), got, f"find.byType skips the offstage cache area, so only items starting above the bottom "
              f"edge (300) count: items {h} tall" + (f", but there are only {n}" if got == n else "") + f": {got}.", VISIBLE)


@template(TEMPLATES)
def cache_extent(rng):
    h = rng.choice((50, 60, 75, 100))
    ce = rng.choice((0, 50, 100, 150, 200, 400, 600))
    got = len(built(60, h, cache=ce))
    return mk(ASK_BUILT, builder(60, h, cacheExtent=str(ce)), got, f"With cacheExtent {ce} the list builds items starting before "
              f"300 + {ce} = {300 + ce}, {h} apart: {got}.", BUILT)


@template(TEMPLATES)
def item_extent(rng):
    h = rng.choice((40, 50, 80, 100, 120))
    n = rng.choice((30, 40, 80))
    ask_built = rng.random() < 0.5
    w = G("ListView.builder", itemExtent=str(h), itemCount=str(n), itemBuilder="(c, i) => Text('$i')")
    got = len(built(n, h)) if ask_built else len(visible(n, h))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"itemExtent forces every item to be {h} tall, whatever the Text needs; "
              + (f"the built range ends at 550: {got}." if ask_built else f"{got} start above 300."), BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def children_are_lazy(rng):
    h = rng.choice(HEIGHTS)
    n = rng.choice((20, 30, 40, 50))
    w = G("ListView", children=[f"for (var i = 0; i < {n}; i++) {tile(h)}"])
    ask_built = rng.random() < 0.6
    got = len(built(n, h)) if ask_built else len(visible(n, h))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, "ListView(children: ...) has all the widgets ready but still builds elements "
              "lazily, like ListView.builder: " + (f"{got} built (items before 550 pixels)." if ask_built else f"{got} on screen."),
              BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def short_list(rng):
    h = rng.choice(HEIGHTS)
    n = rng.randint(1, 3)
    ask_built = rng.random() < 0.5
    got = len(built(n, h)) if ask_built else len(visible(n, h))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, builder(n, h), got, f"itemCount is {n}, so the builder is never asked for more "
              f"items than that: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def sized_viewport(rng):
    vh = rng.choice((100, 150, 200, 250))
    h = rng.choice((40, 50, 60, 75))
    ask_built = rng.random() < 0.5
    w = center(G("SizedBox", height=str(vh), child=builder(50, h)))
    got = len(built(50, h, view=vh)) if ask_built else len(visible(50, h, view=vh))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"The SizedBox makes the viewport {vh} tall"
              + (f", so the cache reaches {vh} + 250 = {vh + 250}" if ask_built else "") + f"; items are {h} tall: {got}.",
              BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def header_above_list(rng):
    hh = rng.choice((50, 60, 100, 150))
    h = rng.choice((40, 50, 60, 75))
    ask_built = rng.random() < 0.5
    w = col(G("SizedBox", height=str(hh)), G("Expanded", child=builder(60, h)))
    vh = 300 - hh
    got = len(built(60, h, view=vh)) if ask_built else len(visible(60, h, view=vh))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"The header takes {hh}, so the Expanded list is {vh} tall"
              + (f" and the cache reaches {vh + 250}" if ask_built else "") + f"; items are {h} tall: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def top_padding(rng):
    p = rng.choice((20, 50, 100))
    h = rng.choice((40, 50, 60, 75))
    ask_built = rng.random() < 0.5
    w = builder(60, h, padding=f"EdgeInsets.only(top: {p})")
    got = len(built(60, h, first=p)) if ask_built else len(visible(60, h, first=p))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"The padding pushes the first item down to {p}, so each item starts {p} "
              f"lower than without it: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def reverse_list(rng):
    h = rng.choice(HEIGHTS)
    ask_built = rng.random() < 0.5
    w = builder(60, h, reverse="true")
    got = len(built(60, h)) if ask_built else len(visible(60, h))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, "reverse: true starts at the bottom and grows upward, but the same "
              f"number of items fit: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def plain_texts_in_list(rng):
    n = rng.choice((10, 15, 30, 50, 60))
    ask_built = rng.random() < 0.5
    w = G("ListView", children=[f"for (var i = 0; i < {n}; i++) Text('$i')"])
    got = len(built(n, 14)) if ask_built else len(visible(n, 14))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, "A one-line Text is 14 tall in the test font; "
              + (f"the built range ends at 550, {got} items fit before it (or all {n})." if ask_built else f"{got} fit in 300 (or all {n})."),
              BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def shrink_wrap_all(rng):
    h = rng.choice((30, 40, 50, 60))
    n = rng.randint(3, 300 // h)
    w = col(builder(n, h, shrinkWrap="true"))
    return mk(ASK_BUILT, w, n, f"shrinkWrap makes the list as tall as all its items ({n} x {h} = {n * h}), so nothing is left to build lazily: {n}.",
              BUILT)


@template(TEMPLATES)
def custom_scroll_view(rng):
    hh = rng.choice((50, 100, 150))
    h = rng.choice((40, 50, 60, 75))
    ask_built = rng.random() < 0.5
    w = G("CustomScrollView", slivers=[G("SliverToBoxAdapter", child=G("SizedBox", height=str(hh))),
                                      G("SliverFixedExtentList.builder", itemExtent=str(h), itemBuilder="(c, i) => Text('$i')")])
    got = len(built(1000, h, first=hh)) if ask_built else len(visible(1000, h, first=hh))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"The {hh} pixel header sliver scrolls with the list and pushes the first "
              f"item down to {hh}: {got}.", BUILT if ask_built else VISIBLE)


# ── scrolled lists ──────────────────────────────────────────────────────

@template(TEMPLATES)
def start_offset_first(rng):
    h = rng.choice(HEIGHTS)
    off = rng.choice(range(100, 700, 50))
    w = builder(100, h, controller=f"ScrollController(initialScrollOffset: {off})")
    vis = visible(100, h, off=off)
    which = rng.choice(("first", "last"))
    got = vis[0] if which == "first" else vis[-1]
    return mk(f"the {which} item on screen", w, got, f"The list starts {off} pixels down; items are {h} tall, so the {which} one touching the "
              f"viewport ({off} to {off + 300}) is number {got}.", FIRST if which == "first" else LAST)


@template(TEMPLATES)
def start_offset_counts(rng):
    h = rng.choice((50, 60, 75, 100))
    off = rng.choice((120, 170, 230, 340, 410, 515))
    ask_built = rng.random() < 0.5
    w = builder(100, h, controller=f"ScrollController(initialScrollOffset: {off})")
    got = len(built(100, h, off=off)) if ask_built else len(visible(100, h, off=off))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"The viewport covers {off} to {off + 300}"
              + (f"; the cache adds up to 250 on each side (starting at {off - min(250, off)}, ending at {off + 550})" if ask_built else "")
              + f". Items are {h} tall: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def jump_then_first(rng):
    h = rng.choice(HEIGHTS)
    off = rng.choice(range(100, 800, 50))
    vis = visible(100, h, off=off)
    which = rng.choice(("first", "last"))
    got = vis[0] if which == "first" else vis[-1]
    return mk(f"the {which} item on screen after jumpTo({off})", builder(100, h), got, f"jumpTo({off}) scrolls {off} pixels; items are {h} tall, "
              f"so the {which} one touching {off} to {off + 300} is number {got}.",
              jump_check(off, FIRST if which == "first" else LAST))


@template(TEMPLATES)
def jump_then_built(rng):
    h = rng.choice((50, 60, 75, 100))
    off = rng.choice((90, 130, 180, 260, 330, 470))
    got = len(built(100, h, off=off))
    return mk(f"items built after jumpTo({off})", builder(100, h), got, f"After jumpTo({off}) the viewport is {off} to {off + 300}; the cache "
              f"reaches {off - min(250, off)} to {off + 550}. Items are {h} tall: {got}.", jump_check(off, BUILT))


@template(TEMPLATES)
def is_item_present(rng):
    h = rng.choice(HEIGHTS)
    n = 80
    off = rng.choice((0, 0, 100, 200, 400))
    k = rng.randint(0, 20)
    on_screen = k in visible(n, h, off=off)
    in_cache = k in built(n, h, off=off)
    finder_off = rng.random() < 0.5
    finder = f"find.text('{k}'{', skipOffstage: false' if finder_off else ''})"
    got = 1 if (in_cache if finder_off else on_screen) else 0
    check = f"count({finder})" if off == 0 else jump_check(off, f"count({finder})")
    ask = f"{finder} matches how many?" + ("" if off == 0 else f" (after jumpTo({off}))")
    why = (f"Item {k} sits at {k * h} to {k * h + h}; the viewport is {off} to {off + 300}, the built range {off - min(250, off)} to {off + 550}. "
           + ("skipOffstage: false also finds built items outside the viewport" if finder_off else "The default finder only finds items on screen")
           + f": {got}.")
    return mk(ask, builder(n, h), got, why, check)


# ── other kinds of scrolling widgets ────────────────────────────────────

@template(TEMPLATES)
def horizontal_list(rng):
    w_ = rng.choice((50, 80, 100, 125, 200))
    n = rng.choice((8, 20, 40))
    ask_built = rng.random() < 0.5
    w = builder(n, w_, scrollDirection="Axis.horizontal")
    got = (len(built(n, w_, view=VIEW_W)) if ask_built else len(visible(n, w_, view=VIEW_W)))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, "A horizontal list uses the screen's 400 width as its viewport"
              + (" plus 250 of cache" if ask_built else "") + f"; items are {w_} wide: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def separated_list(rng):
    h = rng.choice((40, 50, 60, 80))
    s = rng.choice((10, 20, 30))
    ask_built = rng.random() < 0.5
    w = G("ListView.separated", itemCount="60", separatorBuilder=f"(c, i) => SizedBox(height: {s})", itemBuilder=f"(c, i) => {tile(h)}")
    got = len(built(60, h, pitch=h + s)) if ask_built else len(visible(60, h, pitch=h + s))
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"Each item plus its separator takes {h} + {s} = {h + s} pixels, so item k starts at "
              f"k * {h + s}; those before {550 if ask_built else 300} count: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def grid_fixed_count(rng):
    cols = rng.choice((2, 4, 5))
    ratio = rng.choice((1, 1, 2))
    spacing = rng.choice((0, 0, 10))
    n = rng.choice((30, 100))
    tw = 400 / cols
    th = tw / ratio
    pitch = th + spacing
    ask_built = rng.random() < 0.5
    kw = {"crossAxisCount": str(cols)}
    if ratio != 1:
        kw["childAspectRatio"] = str(ratio)
    if spacing:
        kw["mainAxisSpacing"] = str(spacing)
    delegate = "SliverGridDelegateWithFixedCrossAxisCount(" + ", ".join(f"{k}: {v}" for k, v in kw.items()) + ")"
    w = G("GridView.builder", gridDelegate=delegate, itemCount=str(n), itemBuilder="(c, i) => Text('$i')")
    rows = len(items_in(1000, th, pitch, 0, 0, 550 if ask_built else 300))
    got = min(n, rows * cols)
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"{cols} columns make tiles {tw:g} wide and {th:g} tall (width divided by the "
              f"aspect ratio){f', {spacing} apart' if spacing else ''}: {rows} rows reach {550 if ask_built else 300} pixels, so {rows} x {cols}"
              f"{f', but only {n} exist' if got == n else ''}: {got}.", BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def grid_max_extent(rng):
    mx = rng.choice((50, 60, 90, 100, 130, 150, 190, 200, 250))
    cols = -(-400 // mx)  # ceil
    if 400 % cols:
        raise Retry()
    tw = 400 // cols
    n = 100
    rows = len(items_in(1000, tw, tw, 0, 0, 300))
    got = min(n, rows * cols)
    w = G("GridView.builder", gridDelegate=f"SliverGridDelegateWithMaxCrossAxisExtent(maxCrossAxisExtent: {mx})", itemCount=str(n),
          itemBuilder="(c, i) => Text('$i')")
    return mk(ASK_VISIBLE, w, got, f"Tiles may be at most {mx} wide, so a row of 400 needs ceil(400 / {mx}) = {cols} of them, each {tw} wide and "
              f"{tw} tall; {rows} rows start above 300: {rows} x {cols} = {got}.", VISIBLE)


@template(TEMPLATES)
def page_view_pages(rng):
    f = rng.choice((1, 0.8, 0.6, 0.5, 0.4, 0.25))
    n = rng.choice((3, 5, 9))
    p = rng.randint(0, n - 1)
    page_w = 400 * f
    start0 = (400 - page_w) / 2  # a page is centred in the viewport (padEnds)
    got = sum(1 for k in range(n) if start0 + (k - p) * page_w < 400 - 1e-6 and start0 + (k - p) * page_w + page_w > 1e-6)
    ctrl = "PageController(" + (f"viewportFraction: {f}" if f != 1 else "") + (", " if f != 1 and p else "") + (f"initialPage: {p}" if p else "") + ")"
    w = G("PageView.builder", controller=ctrl, itemCount=str(n), itemBuilder="(c, i) => Text('$i')")
    return mk(ASK_BUILT, w, got, f"A page is {page_w:g} wide ({f} of 400) and the current one is centred, so pages next to it peek in; a PageView has no cache "
              f"area, so exactly the pages touching the screen are built: {got}.", BUILT)


@template(TEMPLATES)
def grid_spacing(rng):
    cols, cs = rng.choice(((5, 10), (2, 20), (4, 20), (3, 50), (2, 40)))
    ms = rng.choice((0, 10, 20))
    tw = (400 - (cols - 1) * cs) // cols
    pitch = tw + ms
    ask_built = rng.random() < 0.5
    high = 550 if ask_built else 300
    rows = len(items_in(1000, tw, pitch, 0, 0, high))
    n = 80
    got = min(n, rows * cols)
    kw = f"crossAxisCount: {cols}, crossAxisSpacing: {cs}" + (f", mainAxisSpacing: {ms}" if ms else "")
    w = G("GridView.count", **{"crossAxisCount": str(cols), "crossAxisSpacing": str(cs), **({"mainAxisSpacing": str(ms)} if ms else {})},
          children=[f"for (var i = 0; i < {n}; i++) Text('$i')"])
    del kw
    return mk(ASK_BUILT if ask_built else ASK_VISIBLE, w, got, f"{cols} columns with {cs} between them leave {tw} for each tile "
              f"(square), and rows are {tw}{f' + {ms}' if ms else ''} = {pitch} apart: {rows} rows start before {high}, so {rows} x {cols} = {got}.",
              BUILT if ask_built else VISIBLE)


@template(TEMPLATES)
def last_built_item(rng):
    h = rng.choice(HEIGHTS)
    off = rng.choice((0, 0, 100, 250, 400))
    got = built(100, h, off=off)[-1]
    check_tail = "tester.widgetList<Text>(find.byType(Text, skipOffstage: false)).last.data"
    check = check_tail if off == 0 else jump_check(off, check_tail)
    ask = "the last item built" + ("" if off == 0 else f" after jumpTo({off})")
    return mk(ask, builder(100, h), got, f"The built range ends at {off} + 300 + 250 = {off + 550}; items are {h} tall, so the last one "
              f"starting before that is number {got}.", check)


@template(TEMPLATES)
def jump_to_end(rng):
    h = rng.choice((50, 60, 75, 100))
    n = rng.choice((12, 20, 30))
    total = n * h
    off = total - 300
    got = len(built(n, h, off=off))
    return mk("items built after jumping to the end", builder(n, h), got, f"{n} items of {h} make a list {total} tall; at the end the "
              f"viewport is {off} to {total} and the cache reaches back to {off - 250}: {got}.",
              jump_check_end(BUILT))


def jump_check_end(tail: str) -> str:
    return ("final p = tester.state<ScrollableState>(find.byType(Scrollable)).position;\np.jumpTo(p.maxScrollExtent);\n"
            "await tester.pump();\nreturn %s;" % tail)
