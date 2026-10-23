"""Flutter state pack, Build Count: how many times a build (or a builder) runs.

Flutter calls `build` again when (1) the widget's own State calls setState, (2) the parent builds and hands down a
NEW widget instance, or (3) an InheritedWidget it depends on changes. It does NOT call it again when the parent hands
down the very same instance (a `const` widget, or one kept in a variable), when a tap changes a variable without
setState, or when a frame passes with nothing dirty. Several setStates before one frame are ONE rebuild.
Each count is the number shown by a Text that counts its own builds (`++b`), simulated below by hand.
"""

from __future__ import annotations

from ._flutterstate_common import READ, iife, item, rebuilds, taps, template
from ._model import Maker

BUILD = "Builder(builder: (c) => Text('${++b}'))"
K_FN = "Widget k(BuildContext c) {\n  b++;\n  return Text('$b');\n}"
GLOBAL_B = "return b;"


def _tap_scaffold(inner: str, ontap: str = "() => setState(() {})", decl: str = "var b = 0;", params: str = "c, setState") -> str:
    return iife(decl, f"StatefulBuilder(builder: ({params}) => GestureDetector(\n      onTap: {ontap}, child: {inner}))")


def _taps_ask(n: int, what: str = "shown") -> str:
    return f"{what} after {n} taps?"


# ── Rebuilt by a tap (setState in a StatefulBuilder) ───────────────────

def tb_basic(rng):
    n = rng.choice((2, 3, 4, 5))
    return item(_taps_ask(n), _tap_scaffold(BUILD), 1 + n,
                f"Each setState builds the StatefulBuilder again, which makes a NEW Builder, so it runs once at the start and once per tap: {1 + n}.",
                taps(n) + READ)


def tb_stored(rng):
    n = rng.choice((2, 3, 4, 5))
    code = _tap_scaffold("k", decl=f"var b = 0, k = {BUILD};")
    return item(_taps_ask(n), code, 1,
                "k was made once and the very same Builder is handed back at every rebuild, so Flutter skips it: it ran once.",
                taps(n) + READ)


def tb_direct(rng):
    n = rng.choice((2, 3, 4, 5))
    code = iife("var b = 0;", "StatefulBuilder(builder: (c, setState) {\n    b++;\n    return GestureDetector(\n        onTap: () => setState(() {}), child: Text('$b'));\n  })")
    return item(_taps_ask(n), code, 1 + n,
                f"The StatefulBuilder's own builder runs at the start and again after each setState: {1 + n}.", taps(n) + READ)


def tb_nothing(rng):
    n = rng.choice((2, 3, 4, 5))
    code = _tap_scaffold(BUILD, ontap="() => n++", decl="var b = 0, n = 0;")
    return item(_taps_ask(n), code, 1,
                "The tap changes n but never calls setState, so nothing is marked dirty and the Builder ran only once.",
                taps(n) + READ)


def tb_twice(rng):
    n, r = rng.choice((2, 3, 4)), rng.choice((2, 3))
    ontap = "() { setState(() {}); setState(() {}); }" if r == 2 else "() { for (var i = 0; i < 3; i++) setState(() {}); }"
    return item(_taps_ask(n), _tap_scaffold(BUILD, ontap=ontap), 1 + n,
                f"{r} setStates in one tap only mark the same widget dirty {r} times: ONE rebuild per frame, so {1 + n}.",
                taps(n) + READ)


def tb_one_frame(rng):
    n = rng.choice((3, 4, 5))
    return item(f"shown after {n} taps and 1 frame?", _tap_scaffold(BUILD), 2,
                f"The {n} setStates all land before the next frame, which builds the widget just once: 1 + 1 = 2.",
                taps(n, pump=False) + "await tester.pump();\n" + READ)


def tb_outer(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var a = 0;", "Builder(builder: (c) { a++;\n    return StatefulBuilder(builder: (c, setState) => GestureDetector(\n        onTap: () => setState(() {}), child: Text('$a'))); })")
    return item(_taps_ask(n), code, 1,
                "setState rebuilds only the StatefulBuilder inside; the outer Builder (which counts a) is not dirty and ran once.", taps(n) + READ)


def _notifier_taps(n: int) -> str:
    return ("final v = tester.widget<ValueListenableBuilder<int>>(find.byType(ValueListenableBuilder<int>)).valueListenable as ValueNotifier<int>;\n"
            f"for (var i = 0; i < {n}; i++) {{ v.value++; await tester.pump(); }}\n")


def vlb_child(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var b = 0, v = ValueNotifier(0);",
                "ValueListenableBuilder(valueListenable: v,\n      child: " + BUILD + ",\n      builder: (c, n, w) => w!)")
    return item(f"shown after v changes {n} times?", code, 1,
                "The child given to ValueListenableBuilder is built once and reused by every run of its builder: 1.",
                _notifier_taps(n) + READ)


def vlb_inside(rng):
    n = rng.choice((2, 3, 4))
    code = iife("var b = 0, v = ValueNotifier(0);",
                "ValueListenableBuilder(valueListenable: v,\n      builder: (c, n, _) => " + BUILD + ")")
    return item(f"shown after v changes {n} times?", code, 1 + n,
                f"The Builder is made inside the builder, so each of the {n} changes makes a new one that runs: {1 + n}.",
                _notifier_taps(n) + READ)


def tb_layout(rng):
    n = rng.choice((2, 3, 4))
    inner = "LayoutBuilder(builder: (c, box) => Text('${++b}'))"
    return item(_taps_ask(n), _tap_scaffold(inner), 1 + n,
                f"A new LayoutBuilder comes with every rebuild and runs its builder once: {1 + n}.", taps(n) + READ)


def tb_cls(rng):
    n = rng.choice((2, 3, 4))
    code = ("int b = 0;\nclass A extends StatefulWidget {\n  createState() => S();\n}\nclass S extends State<A> {\n"
            "  build(c) => GestureDetector(\n      onTap: () => setState(() {}), child: Text('${++b}'));\n}\nA()")
    return item(f"b after {n} taps?", code, 1 + n,
                f"The State calls setState on itself, so its build runs again for each tap: {1 + n}.", taps(n) + "return b;")


# ── Rebuilt by the parent (a new widget handed down) ───────────────────

def _parent(n: int, what: str = "b") -> str:
    return f"{what} after {n} parent rebuilds?"


def pb_new(rng):
    n = rng.choice((2, 3, 4, 5))
    code = f"int b = 0;\n{K_FN}\nBuilder(builder: k)"
    return item(_parent(n), code, 1 + n, f"Each parent build makes a new Builder, which runs k again: 1 + {n} = {1 + n}.",
                rebuilds(n) + GLOBAL_B)


def pb_stored(rng):
    n = rng.choice((2, 3, 4, 5))
    code = f"int b = 0;\nvar w = Builder(builder: k);\n{K_FN}\nw"
    return item(_parent(n), code, 1,
                "w is one Builder made once; every parent build hands back the same instance and Flutter does not rebuild it: 1.",
                rebuilds(n) + GLOBAL_B)


def pb_wrapped_stored(rng):
    n = rng.choice((2, 3, 4))
    wrap = rng.choice(("Padding(padding: EdgeInsets.all(8), child: w)", "Center(child: w)", "SizedBox(width: 90, child: w)",
                       "Align(alignment: Alignment.topLeft, child: w)", "ColoredBox(color: Colors.red, child: w)"))
    code = f"int b = 0;\nvar w = Builder(builder: k);\n{K_FN}\n{wrap}"
    return item(_parent(n), code, 1,
                "The wrapper is new each time but it passes on the same w, which is skipped: 1.", rebuilds(n) + GLOBAL_B)


def pb_wrapped_new(rng):
    n = rng.choice((2, 3, 4))
    wrap = rng.choice(("Padding(padding: EdgeInsets.all(8), child: Builder(builder: k))", "Center(child: Builder(builder: k))",
                       "SizedBox(width: 90, child: Builder(builder: k))", "ColoredBox(color: Colors.red, child: Builder(builder: k))"))
    code = f"int b = 0;\n{K_FN}\n{wrap}"
    return item(_parent(n), code, 1 + n, f"The Builder is made again inside the build each time, so k runs again: {1 + n}.",
                rebuilds(n) + GLOBAL_B)


def pb_twice_stored(rng):
    n = rng.choice((2, 3, 4))
    code = f"int b = 0;\nvar w = Builder(builder: k);\n{K_FN}\nColumn(children: [w, w])"
    return item(_parent(n), code, 2,
                "w is used in two places, so it is built twice at the start (two elements); after that it is never rebuilt: 2.",
                rebuilds(n) + GLOBAL_B)


def pb_twice_new(rng):
    n = rng.choice((2, 3))
    code = f"int b = 0;\n{K_FN}\nColumn(children: [Builder(builder: k), Builder(builder: k)])"
    return item(_parent(n), code, 2 * (1 + n), f"Two new Builders per build, each running k: 2 x {1 + n} = {2 * (1 + n)}.",
                rebuilds(n) + GLOBAL_B)


def pb_mixed(rng):
    n = rng.choice((2, 3, 4))
    code = f"int b = 0;\nvar w = Builder(builder: k);\n{K_FN}\nColumn(children: [w, Builder(builder: k)])"
    return item(_parent(n), code, 2 + n,
                f"w is built once; the new Builder runs at the start and for each of the {n} rebuilds: 1 + {1 + n} = {2 + n}.",
                rebuilds(n) + GLOBAL_B)


def pb_quiet(rng):
    n = rng.choice((3, 4, 5))
    code = f"int b = 0;\n{K_FN}\nBuilder(builder: k)"
    return item(f"b after {n} more frames?", code, 1,
                "pump only draws a frame; with nothing marked dirty no build runs, so k ran once.",
                f"for (var i = 0; i < {n}; i++) {{ await tester.pump(); }}\n" + GLOBAL_B)


def pb_layout(rng):
    n = rng.choice((2, 3, 4))
    code = "int b = 0;\nWidget k(BuildContext c, BoxConstraints x) {\n  b++;\n  return Text('$b');\n}\nLayoutBuilder(builder: k)"
    return item(_parent(n), code, 1 + n, f"A new LayoutBuilder each parent build runs its builder again: {1 + n}.",
                rebuilds(n) + GLOBAL_B)


def _cls(kind: str, const: bool) -> str:
    base = "StatelessWidget" if kind == "stateless" else "StatefulWidget"
    if kind == "stateless":
        body = f"class K extends {base} {{\n  const K();\n  build(c) => Text('${{++b}}');\n}}\n"
        root = "const K()" if const else "K()"
    else:
        body = (f"class K extends {base} {{\n  const K();\n  createState() => S();\n}}\nclass S extends State<K> {{\n"
                "  build(c) => Text('${++b}');\n}\n")
        root = "const K()" if const else "K()"
    return "int b = 0;\n" + body + root


def _cls_template(kind: str, const: bool):
    def make(rng):
        n = rng.choice((2, 3, 4))
        if const:
            why = "A const widget is one shared instance, so every parent build hands back the same K and it is never rebuilt: 1."
        elif kind == "stateless":
            why = f"Without const each parent build makes a new K, and a new instance is built again: 1 + {n} = {1 + n}."
        else:
            why = f"A new K arrives each time; the State is kept but its build runs again for the new widget: 1 + {n} = {1 + n}."
        return item(_parent(n), _cls(kind, const), 1 if const else 1 + n, why, rebuilds(n) + GLOBAL_B)
    return make


def _const_template(shape: str):
    def make(rng):
        n = rng.choice((2, 3, 4))
        head = "int b = 0;\nclass K extends StatelessWidget {\n  const K();\n  build(c) => Text('${++b}');\n}\n"
        pad = "padding: EdgeInsets.all(8)"
        if shape == "const_wrap":
            root, ans = f"const Padding({pad}, child: K())", 1
            why = "const on the Padding makes everything inside const too: one shared K, never rebuilt: 1."
        elif shape == "const_inner":
            root, ans = f"Padding({pad}, child: const K())", 1
            why = "The Padding is new each build, but the const K is one shared instance and is skipped: 1."
        elif shape == "plain_inner":
            root, ans = f"Padding({pad}, child: K())", 1 + n
            why = f"Without const there is a new K at each parent build, and it is built again: 1 + {n} = {1 + n}."
        elif shape == "const_list":
            root, ans = "Column(children: const [K(), K()])", 2
            why = "A const list shares one K, used in two places: two elements built at the start (2), then skipped."
        else:
            root, ans = "Column(children: [const K(), K()])", 2 + n
            why = f"The const K is built once; the plain K runs at the start and for each rebuild: 1 + {1 + n} = {2 + n}."
        return item(_parent(n), head + root, ans, why, rebuilds(n) + GLOBAL_B)
    return make


def _t(name, fn, *args):
    return template(name, fn, *args)


TEMPLATES: tuple[Maker, ...] = (
    _t("tb_basic", tb_basic), _t("tb_stored", tb_stored), _t("tb_direct", tb_direct), _t("tb_nothing", tb_nothing),
    _t("tb_twice", tb_twice), _t("tb_one_frame", tb_one_frame), _t("tb_outer", tb_outer),
    _t("vlb_child", vlb_child), _t("vlb_inside", vlb_inside), _t("tb_layout", tb_layout), _t("tb_cls", tb_cls),
    _t("pb_new", pb_new), _t("pb_stored", pb_stored), _t("pb_wrapped_stored", pb_wrapped_stored),
    _t("pb_wrapped_new", pb_wrapped_new), _t("pb_twice_stored", pb_twice_stored), _t("pb_twice_new", pb_twice_new),
    _t("pb_mixed", pb_mixed), _t("pb_quiet", pb_quiet), _t("pb_layout", pb_layout),
    _t("pb_const_stateless", _cls_template("stateless", True)), _t("pb_new_stateless", _cls_template("stateless", False)),
    _t("pb_const_stateful", _cls_template("stateful", True)), _t("pb_new_stateful", _cls_template("stateful", False)),
    _t("pb_const_wrap", _const_template("const_wrap")), _t("pb_const_inner", _const_template("const_inner")),
    _t("pb_plain_inner", _const_template("plain_inner")), _t("pb_const_list", _const_template("const_list")),
    _t("pb_const_mixed", _const_template("const_mixed")),
)
