"""Flutter state pack, Lifecycle Order: the digits a State's hooks write, in the order Flutter runs them.

Each hook of a tiny State writes its own digit into a global log `s` (the digits are random and the hooks are listed
in a shuffled order, so the order of the lines in the code is NOT the order they run). The answer is the log after a
scene: the first frame, a parent that rebuilds, the widget being removed, its key changing, its own setState, or being
removed and shown again. Flutter's rules, written out by hand below:

* a widget's constructor runs whenever the widget is made (a `const` widget is made once, at compile time);
* a NEW State is made by createState, then initState, then didChangeDependencies, then build;
* when a parent hands a new widget to the same State (same type and key): didUpdateWidget, then build;
* a const widget handed down again is the same instance, so nothing runs at all;
* setState only runs build; a rebuild by the parent does NOT call createState, initState or didChangeDependencies;
* when a widget leaves the tree its State gets deactivate, and dispose when the frame is done;
* when the key changes, the old State is deactivated first, the new one is created and built, and only then is
  the old one disposed.

The 220-character limit is the reason for the terse style (types left to inference, super calls left out except where
dispose needs one): a State with three hooks is about all that fits.
"""

from __future__ import annotations

import random

from ._flutter_model import Retry
from ._flutterstate_common import REBUILD, item, rebuilds, template
from ._model import Maker

#: How each hook of the State is written (`@` is its digit).
LINES = {
    "initState": "initState() => s+='@';",
    "deps": "didChangeDependencies() => s+='@';",
    "update": "didUpdateWidget(o) => s+='@';",
    "deactivate": "deactivate() => s+='@';",
    "dispose": "dispose() { super.dispose(); s+='@'; }",
}
WORDS = {"ctor": "the constructor", "create": "createState", "initState": "initState", "deps": "didChangeDependencies",
         "build": "build", "update": "didUpdateWidget", "deactivate": "deactivate", "dispose": "dispose"}

FIRST = ["ctor", "create", "initState", "deps", "build"]
REPUMP = ["ctor", "update", "build"]
GONE = ["deactivate", "dispose"]

PUMP = "await tester.pumpWidget(Directionality(textDirection: TextDirection.ltr, child: %s));\n"
REMOVE_CHECK = PUMP % "SizedBox()"
SETSTATE_CHECK = "(tester.state(find.byType(A)) as dynamic).setState(() {});\nawait tester.pump();\n"


def _events(scene: str, n: int = 1) -> list[str]:
    """Every hook that runs in the scene, in order (the code only logs the ones it writes)."""
    if scene == "first":
        return list(FIRST)
    if scene == "rebuild":
        return FIRST + REPUMP * n
    if scene == "rebuild_const":
        return list(FIRST[1:])  # a const constructor has no body, and the same instance is handed down again
    if scene == "remove":
        return FIRST + GONE
    if scene == "key":
        return FIRST + ["ctor", "deactivate", "create", "initState", "deps", "build", "dispose"]
    if scene == "setstate":
        return FIRST + ["build"] * n
    if scene == "readd":
        return FIRST + GONE + FIRST
    raise AssertionError(scene)


def _code(rng: random.Random, hooks: list[str], digits: dict[str, str], *, key: bool = False, const: bool = False) -> str:
    a_lines = []
    if "ctor" in hooks:
        a_lines.append(f"A({{super.key}}) {{ s+='{digits['ctor']}'; }}" if key else f"A() {{ s+='{digits['ctor']}'; }}")
    elif key:
        a_lines.append("A({super.key});")
    elif const:
        a_lines.append("const A();")
    if "create" in hooks:
        a_lines.append(f"createState() {{ s+='{digits['create']}'; return S(); }}")
    else:
        a_lines.append("createState() => S();")
    s_lines = [LINES[h].replace("@", digits[h]) for h in hooks if h in LINES]
    s_lines.append(f"build(c) => Text(s+='{digits['build']}');" if "build" in hooks else "build(c) => Text('');")
    rng.shuffle(s_lines)
    root = "const A()" if const else ("A(key: Key('1'))" if key else "A()")
    return ("var s = '';\nclass A extends StatefulWidget { " + " ".join(a_lines) + " }\nclass S extends State<A> {\n  "
            + "\n  ".join(s_lines) + "\n}\n" + root)


def scene_item(rng: random.Random, scene: str, hooks: tuple[str, ...], n: int = 1):
    """One item: a scene, the hooks the State writes, and (for rebuilds and setStates) how many times."""
    use = list(hooks)
    digits = dict(zip(use, rng.sample("123456789", len(use))))
    events = _events(scene, n)
    answer = "".join(digits[e] for e in events if e in digits)
    if not answer:
        raise Retry
    code = _code(rng, use, digits, key=scene == "key", const=scene == "rebuild_const")
    order = ", ".join(WORDS[e] for e in events if e in digits)
    why = f"Flutter runs them in this order: {order}. As digits that is {answer}."
    if scene == "first":
        ask, check = "s once built?", "return s;"
    elif scene in ("rebuild", "rebuild_const"):
        ask = "s after rebuild?" if n == 1 else f"s after {n} rebuilds?"
        check = rebuilds(n) + "return s;"
    elif scene == "remove":
        ask, check = "s after removal?", REMOVE_CHECK + "return s;"
    elif scene == "key":
        ask, check = "s after key 1 -> 2?", PUMP % "A(key: Key('2'))" + "return s;"
    elif scene == "setstate":
        ask = "s after setState?" if n == 1 else f"s after {n} setStates?"
        check = SETSTATE_CHECK * n + "return s;"
    else:
        ask, check = "s after remove and add?", REMOVE_CHECK + REBUILD + "return s;"
    return item(ask, code, answer, why, check)


#: (name, scene, hooks, n)
SPECS = (
    ("first_init", "first", ("initState", "build"), 1),
    ("first_init_deps", "first", ("initState", "deps", "build"), 1),
    ("first_deps", "first", ("deps", "build"), 1),
    ("first_create", "first", ("create", "initState", "build"), 1),
    ("first_ctor", "first", ("ctor", "create", "build"), 1),
    ("rebuild_update", "rebuild", ("initState", "update", "build"), 1),
    ("rebuild_update_deps", "rebuild", ("deps", "update", "build"), 1),
    ("rebuild_twice", "rebuild", ("update", "build"), 2),
    ("rebuild_create", "rebuild", ("create", "build"), 2),
    ("rebuild_ctor", "rebuild", ("ctor", "build"), 1),
    ("rebuild_deps", "rebuild", ("deps", "build"), 2),
    ("rebuild_const", "rebuild_const", ("initState", "build"), 2),
    ("remove_init", "remove", ("initState", "dispose"), 1),
    ("remove_build", "remove", ("build", "dispose"), 1),
    ("remove_deactivate", "remove", ("build", "deactivate", "dispose"), 1),
    ("remove_create", "remove", ("create", "dispose"), 1),
    ("key_init", "key", ("initState", "build"), 1),
    ("key_build", "key", ("build", "deactivate"), 1),
    ("key_create", "key", ("create", "initState"), 1),
    ("setstate_init", "setstate", ("initState", "build"), 1),
    ("setstate_update", "setstate", ("initState", "update", "build"), 1),
    ("setstate_deps", "setstate", ("deps", "build"), 1),
    ("setstate_twice", "setstate", ("initState", "build"), 2),
    ("readd_init", "readd", ("initState", "dispose"), 1),
    ("readd_build", "readd", ("build", "dispose"), 1),
    ("readd_deactivate", "readd", ("build", "deactivate"), 1),
)


TEMPLATES: tuple[Maker, ...] = tuple(template(name, scene_item, scene, hooks, n) for name, scene, hooks, n in SPECS)
