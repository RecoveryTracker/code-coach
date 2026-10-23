"""Flutter state pack, shared helpers: how a state/rebuild item is built, and the checks that drive it.

Every item of this pack is a tiny widget snippet (its classes included) plus a `// question` line, held to <= 220
characters and 10 lines, so the snippets lean on a few compact idioms:

* an IIFE `() { var n = 0; return StatefulBuilder(...); }()` keeps a local variable alive across rebuilds without a
  class (the variable lives in the closure, setState is the builder's);
* a counting `Builder(builder: (c) => Text('${++b}'))` shows how many times it was built, so the ANSWER IS ON THE
  SCREEN and the check only reads the Text;
* `bool f = false;` plus a function `g()` ending in a lone `}` line makes the snippet its own library, and the check may
  then flip `f` and "rebuild the parent" by pumping `build()` (the generated root) again - a parent that rebuilds with
  new widgets, which is exactly how the framework sees a `setState` higher up.

Nothing here asks Flutter anything: the answer of each template is worked out by hand in Python from the framework's rules
(setState marks dirty, a frame builds once, a widget that is `identical` is not rebuilt, state follows type and key...),
and tests/test_brain_packs.py then holds every answer to a real `flutter test` (tests/flutter_oracle.py).
"""

from __future__ import annotations

import random

from ._flutter_model import fit, named
from ._model import Maker
from .items import Item

#: Reads the one Text on screen.
READ = "return tester.widget<Text>(find.byType(Text)).data;"
#: The same read, for the LAST Text when there are two.
READ_LAST = "return tester.widgetList<Text>(find.byType(Text)).last.data;"
READ_FIRST = "return tester.widgetList<Text>(find.byType(Text)).first.data;"

#: Pump the generated root again: the parent rebuilds with fresh widgets from `build()`.
REBUILD = "await tester.pumpWidget(Directionality(textDirection: TextDirection.ltr, child: build()));\n"


def taps(n: int, finder: str = "find.byType(GestureDetector)", pump: bool = True) -> str:
    """Tap `n` times (a frame after each tap unless `pump` is False)."""
    after = " await tester.pump();" if pump else ""
    return f"for (var i = 0; i < {n}; i++) {{ await tester.tap({finder});{after} }}\n"


def rebuilds(n: int) -> str:
    return f"for (var i = 0; i < {n}; i++) {{ {REBUILD.strip()} }}\n"


def flip(flag: str = "f") -> str:
    """Set the global flag, then let the parent rebuild."""
    return f"{flag} = true;\n{REBUILD}"


def item(ask: str, code: str, answer: object, why: str, check: str) -> Item:
    """`// ask`, then the code; `why` is a sentence or two (no dollar sign: Dart's interpolation stays out of it)."""
    return Item(f"// {ask}\n{code}", str(answer), why, check=check)


def template(name: str, fn, *args) -> Maker:
    """A template that re-rolls until the prompt fits the drill (220 characters, 10 lines)."""
    def make(rng: random.Random) -> Item:
        return fn(rng, *args)
    return fit(named(name, make))


def once(rng: random.Random, *choices):
    return rng.choice(choices)


def iife(decl: str, body: str) -> str:
    """`() { <decl> return <body>; }()`: a closure that owns the variables of the example."""
    return "() {\n  " + decl + "\n  return " + body + ";\n}()"


def sb_tap(ontap: str, text: str, wrap: str = "@", params: str = "c, setState") -> str:
    """A StatefulBuilder whose builder returns a tappable Text (`wrap` puts a widget around the GestureDetector)."""
    gd = f"GestureDetector(\n      onTap: {ontap}, child: Text('{text}'))"
    return f"StatefulBuilder(builder: ({params}) => " + wrap.replace("@", gd) + ")"
