"""Shared helpers of the Flutter widgets pack (`pack_flutterwidgets.py`): print widget trees, build Items.

The layout pack (`_flutter_model.py`) lays boxes out; this pack asks about the widget TREE and what happens in it
(counts, shown text, lazy lists, typing, taps, routes, inherited values, forms). There is nothing to lay out here, so
the helpers are small: `G` is a generic printable widget (it reuses `_flutter_model.render`, so long trees break
into lines the same way), `mk` builds an Item whose `check` is what the Flutter oracle (tests/flutter_oracle.py)
evaluates, and `template` registers a template function of one activity.

Every template does its own sums in plain Python from Flutter's rules; none of this asks Flutter anything. The
oracle test builds each item in a real `flutter test` and compares.

THE ITEM, as the oracle sees it: `prompt` = `// question` line, optional top-level declarations (classes, a global
counter and the function that bumps it, ending with a column-0 `}` line), then ONE widget expression; `check` = a Dart
expression, or (it mentions `await`/`return`) a statement body that may tap, enter text and pump.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from ._flutter_model import Node, Retry, fit, named, render
from ._model import Maker
from .items import Item


class G(Node):
    """A widget written as Dart: `G('Row', children=[...])`. Strings are code as written; Nodes and lists of them nest."""

    def __init__(self, name: str, *pos: Any, **kw: Any) -> None:
        super().__init__()
        self.name, self.pos, self.kw = name, list(pos), list(kw.items())

    def call(self):
        return self.name, self.pos, self.kw

    def kids(self) -> list[Node]:
        out: list[Node] = []
        for v in self.pos + [x for _, x in self.kw]:
            if isinstance(v, Node):
                out.append(v)
            elif isinstance(v, list):
                out.extend(x for x in v if isinstance(x, Node))
        return out


def q(s: str) -> str:
    """A Dart string literal."""
    return "'" + s.replace("'", "\\'") + "'"


def text(s: str, **kw: Any) -> G:
    return G("Text", q(s), **kw)


def icon(name: str = "add", **kw: Any) -> G:
    return G("Icon", f"Icons.{name}", **kw)


def row(*kids: Any) -> G:
    return G("Row", children=list(kids))


def col(*kids: Any) -> G:
    return G("Column", children=list(kids))


def pad(child: Any, n: int = 8) -> G:
    return G("Padding", padding=f"EdgeInsets.all({n})", child=child)


def center(child: Any) -> G:
    return G("Center", child=child)


def walk_names(v: Any):
    """Every G node's name under (and including) v, in order."""
    if isinstance(v, G):
        yield v.name
        for k in v.kids():
            yield from walk_names(k)


def mk(ask: str, widget: Any, answer: Any, why: str, check: str, decls: str = "", width: int = 78) -> Item:
    """An item: `// ask`, the declarations (if any), then the widget expression."""
    code = widget if isinstance(widget, str) else render(widget, width=width)
    prompt = f"// {ask}\n" + (decls.rstrip() + "\n" if decls else "") + code
    assert "$" not in why, why
    return Item(prompt, str(answer), why, check=check)


def template(bucket: list[Maker]) -> Callable[[Callable[[random.Random], Item]], Callable[[random.Random], Item]]:
    """Decorator: register a template function in `bucket`, re-rolled by `fit` until the prompt fits the drill."""
    def deco(fn):
        bucket.append(fit(named(fn.__name__, fn), whole=False))
        return fn
    return deco


def maybe(rng: random.Random, p: float = 0.5) -> bool:
    return rng.random() < p


def shuffled(rng: random.Random, xs: list) -> list:
    out = list(xs)
    rng.shuffle(out)
    return out


__all__ = ["G", "q", "text", "icon", "row", "col", "pad", "center", "walk_names", "mk", "template", "maybe", "shuffled",
           "Retry"]
