"""Flutter state pack, the element tree model: which State survives a rebuild.

This is Flutter's reconciliation written out by hand (framework.dart: `Element.updateChild`, `Widget.canUpdate` and
`RenderObjectElement.updateChildren`), on a tiny tree of widgets that only has what the examples need:

* an element is REUSED for a new widget when the new widget has the same runtimeType AND the same key, otherwise the
  old subtree is deactivated and a new one is inflated (a new State, built from the new widget's initialValue);
* a multi-child widget (Column, Row, IndexedStack) matches its children by walking in from the top while they can be
  updated, then in from the bottom, then keyed children in the middle through a map; an unkeyed old child left in the
  middle is thrown away;
* a GlobalKey can take its element, and so its State, out of a subtree that was just deactivated and put it somewhere
  else in the same frame.

The stateful leaf is a FormField: its State copies `initialValue` once and keeps it, so the text it shows tells which
State a widget got (a kept State shows its first value, a new one shows the new widget's).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class W:
    """A widget. `t` is its runtimeType, `key` is None, ('v', value) for a ValueKey, ('u',) for a UniqueKey made at
    every build, ('g', name) for a GlobalKey; `arg` is printed code that does not change identity (padding: ...)."""
    t: str
    key: tuple | None = None
    kids: tuple = ()
    arg: str = ""
    argv: str = ""  # the value that fills the `{}` of `arg` (it does not change identity either)
    val: int | None = None  # a FormField's initialValue (None: the running counter)


FF = "FormField"
MULTI = {"Column", "Row", "IndexedStack", "Stack"}


def ff(val: int | None = None, key: tuple | None = None) -> W:
    return W(FF, key=key, val=val)


def key_code(key: tuple) -> str:
    kind = key[0]
    if kind == "v":
        return f"Key('{key[1]}')"
    if kind == "u":
        return "UniqueKey()"
    return str(key[1])


def can_update(old: W, new: W) -> bool:
    return old.t == new.t and old.key == new.key


class Elem:
    __slots__ = ("w", "kids", "state")

    def __init__(self, w: W, kids: list, state: int | None) -> None:
        self.w, self.kids, self.state = w, kids, state


class Tree:
    """One running app: build trees with `build`, keep the element tree between builds."""

    def __init__(self) -> None:
        self.counter = 0  # `++n` of the FormFields' initialValue
        self.unique = 0
        self.root: Elem | None = None
        self.inactive: dict[tuple, Elem] = {}

    # a widget tree as the build function makes it: fresh unique keys, counted initial values
    def materialize(self, w: W) -> W:
        key = w.key
        if key == ("u",):
            self.unique += 1
            key = ("u", self.unique)
        val = w.val
        kids = tuple(self.materialize(k) for k in w.kids)
        if w.t == FF and val is None:
            self.counter += 1
            val = self.counter
        return W(w.t, key, kids, w.arg, w.argv, val)

    def pump(self, w: W) -> None:
        new = self.materialize(w)
        self.inactive = {}
        self.root = self.update_child(self.root, new)
        self.inactive = {}

    # ── Element.updateChild / inflateWidget ─────────────────────────────
    def update_child(self, old: Elem | None, new: W) -> Elem:
        if old is not None:
            if can_update(old.w, new):
                return self.update(old, new)
            self.deactivate(old)
        return self.inflate(new)

    def inflate(self, w: W) -> Elem:
        if w.key is not None and w.key[0] == "g" and w.key in self.inactive:
            retaken = self.inactive.pop(w.key)
            if can_update(retaken.w, w):
                return self.update(retaken, w)
        return Elem(w, [self.inflate(k) for k in w.kids], w.val if w.t == FF else None)

    def deactivate(self, e: Elem) -> None:
        if e.w.key is not None and e.w.key[0] == "g":
            self.inactive[e.w.key] = e
        for k in e.kids:
            self.deactivate(k)

    def update(self, e: Elem, new: W) -> Elem:
        e.w = new
        if new.t == FF:
            return e
        if new.t in MULTI:
            e.kids = self.update_children(e.kids, list(new.kids))
        else:
            old_kid = e.kids[0] if e.kids else None
            if not new.kids:
                if old_kid is not None:
                    self.deactivate(old_kid)
                e.kids = []
            else:
                e.kids = [self.update_child(old_kid, new.kids[0])]
        return e

    # ── RenderObjectElement.updateChildren ──────────────────────────────
    def update_children(self, old: list, new_ws: list) -> list:
        new_top, old_top = 0, 0
        new_bot, old_bot = len(new_ws) - 1, len(old) - 1
        out: list = [None] * len(new_ws)
        while old_top <= old_bot and new_top <= new_bot:  # the top of the list
            if not can_update(old[old_top].w, new_ws[new_top]):
                break
            out[new_top] = self.update(old[old_top], new_ws[new_top])
            old_top += 1
            new_top += 1
        while old_top <= old_bot and new_top <= new_bot:  # the bottom (only counted here)
            if not can_update(old[old_bot].w, new_ws[new_bot]):
                break
            old_bot -= 1
            new_bot -= 1
        have_old = old_top <= old_bot
        keyed: dict[tuple, Elem] = {}
        if have_old:
            while old_top <= old_bot:
                o = old[old_top]
                if o.w.key is not None:
                    keyed[o.w.key] = o
                else:
                    self.deactivate(o)
                old_top += 1
        while new_top <= new_bot:  # the middle
            nw = new_ws[new_top]
            o = None
            if have_old and nw.key is not None:
                o = keyed.get(nw.key)
                if o is not None:
                    if can_update(o.w, nw):
                        del keyed[nw.key]
                    else:
                        o = None
            out[new_top] = self.update_child(o, nw)
            new_top += 1
        new_bot = len(new_ws) - 1  # the bottom, now paired in order
        old_bot = len(old) - 1
        while old_top <= old_bot and new_top <= new_bot:
            out[new_top] = self.update_child(old[old_top], new_ws[new_top])
            old_top += 1
            new_top += 1
        for o in keyed.values():
            self.deactivate(o)
        return out

    # ── what is on screen ───────────────────────────────────────────────
    def states(self) -> list[int]:
        """The State of every FormField, in tree order."""
        out: list[int] = []

        def walk(e: Elem) -> None:
            if e.w.t == FF:
                out.append(e.state)
            for k in e.kids:
                walk(k)
        if self.root is not None:
            walk(self.root)
        return out
