"""Flutter state pack, Inherited Value: what a descendant reads from an InheritedWidget, and whether it rebuilds.

The framework's own inherited widgets stand in for a custom one (DefaultTextStyle, IconTheme, MediaQuery, TickerMode,
Theme): they are InheritedWidgets with the same machinery. The rules written out by hand below:

* `X.of(context)` (dependOnInheritedWidgetOfExactType) registers a DEPENDENCY: when the inherited widget is rebuilt with
  a value its `updateShouldNotify` calls different, every dependent is rebuilt - even a child that is the very same
  instance, which Flutter would otherwise skip;
* `context.getInheritedWidgetOfExactType` reads the value but does NOT register a dependency, so an identical child
  never hears about the change and keeps showing the old value;
* a child made fresh at every parent build (`Builder(builder: r)`) is rebuilt anyway, dependency or not;
* when the inherited value did not change, nothing is notified;
* MediaQuery.of depends on every part of MediaQueryData, MediaQuery.sizeOf only on the size;
* the NEAREST inherited widget of a type wins.

The snippet has a global `f`; the check sets it to true and lets the parent rebuild. (`Widget r(c)` leaves the type of
`c` out to keep the example short.)
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from ._flutterstate_common import READ, REBUILD, item, template
from ._model import Maker


@dataclass(frozen=True)
class Kind:
    name: str
    wrap: str                      # the inherited widget around the child K ({} is the value)
    read: str                      # a dependOn read that is an int
    values: tuple                  # ((old code, new code, old shown, new shown), ...)
    what: str                      # words for the explanation
    get: str = ""                  # the same read WITHOUT a dependency ("" if the type cannot be named)
    touch: str = ""                # a dependOn call as a statement (default: the read)


DTS = Kind("DefaultTextStyle", "DefaultTextStyle.merge(maxLines: {}, child: K)", "DefaultTextStyle.of(c).maxLines",
           (("1", "2", 1, 2), ("2", "3", 2, 3), ("1", "3", 1, 3), ("3", "1", 3, 1)), "maxLines",
           get="c.getInheritedWidgetOfExactType<DefaultTextStyle>()!.maxLines")
ICON = Kind("IconTheme", "IconTheme(data: IconThemeData(size: {}), child: K)", "IconTheme.of(c).size!.round()",
            (("20", "40", 20, 40), ("10", "30", 10, 30), ("24", "48", 24, 48), ("40", "20", 40, 20)), "icon size")
MQ = Kind("MediaQuery", "MediaQuery(data: MediaQueryData(devicePixelRatio: {}), child: K)",
          "MediaQuery.of(c).devicePixelRatio.round()",
          (("1", "2", 1, 2), ("2", "3", 2, 3), ("1", "3", 1, 3), ("3", "1", 3, 1)), "pixel ratio")
TICKER = Kind("TickerMode", "TickerMode(enabled: {}, child: K)", "TickerMode.of(c) ? 1 : 0",
              (("false", "true", 0, 1),), "enabled flag", touch="TickerMode.of(c)")
THEME = Kind("Theme", "Theme(data: ThemeData(useMaterial3: {}), child: K)", "Theme.of(c).useMaterial3 ? 1 : 0",
             (("false", "true", 0, 1),), "useMaterial3 flag", touch="Theme.of(c)")


def _root(kind: Kind, value: str, child: str) -> str:
    return kind.wrap.replace("{}", value).replace("K", child)


def _cond(old: str, new: str) -> str:
    return "f" if (old, new) == ("false", "true") else f"f ? {new} : {old}"


def read_item(rng: random.Random, kind: Kind, identical: bool, depend: bool):
    old, new, old_shown, new_shown = rng.choice(kind.values)
    rebuilt = (not identical) or depend
    answer = new_shown if rebuilt else old_shown
    reading = kind.read if depend else kind.get
    fn = f"Widget r(c) {{\n  return Text('${{{reading}}}');\n}}"
    head, child = ("var f = false, k = Builder(builder: r);", "k") if identical else ("var f = false;", "Builder(builder: r)")
    code = f"{head}\n{fn}\n{_root(kind, _cond(old, new), child)}"
    if identical and depend:
        why = f"The child is the same instance, but .of registered a dependency, so the changed {kind.what} rebuilds it: {answer}."
    elif identical:
        why = f"The child is the same instance and getInheritedWidgetOfExactType registers no dependency, so it is not rebuilt and still shows {answer}."
    elif depend:
        why = f"A new Builder is made at every parent build and it reads the new {kind.what}: {answer}."
    else:
        why = f"A new Builder is made at every parent build, so it is built again and reads the new {kind.what}, dependency or not: {answer}."
    return item("after f = true?", code, answer, why, "f = true;\n" + REBUILD + READ)


def builds_item(rng: random.Random, kind: Kind, identical: bool, depend: bool, changes: bool = True):
    old, new, _, _ = rng.choice(kind.values)
    rebuilt = (not identical) or (depend and changes)
    answer = 2 if rebuilt else 1
    touch = (kind.touch or kind.read) if depend else kind.get.replace("!.maxLines", "")
    fn = f"Widget r(c) {{\n  {touch};\n  return Text('${{++b}}');\n}}"
    head, child = (("var f = false, b = 0, k = Builder(builder: r);", "k") if identical
                   else ("var f = false, b = 0;", "Builder(builder: r)"))
    value = _cond(old, new) if changes else old
    code = f"{head}\n{fn}\n{_root(kind, value, child)}"
    if not identical:
        why = "A new Builder is made at every parent build, so r runs again whatever it reads: 2."
    elif not depend:
        why = "The child is the same instance and r registered no dependency, so Flutter never rebuilds it: 1."
    elif not changes:
        why = f"r depends on the {kind.name}, but its {kind.what} never changes, so nobody is notified: 1."
    else:
        why = f"The child is the same instance, but r depends on the {kind.name} and its {kind.what} changed: r runs again, 2."
    return item("after f = true?", code, answer, why, "f = true;\n" + REBUILD + READ)


def nearest_item(rng: random.Random, kind: Kind):
    old, new, _, _ = rng.choice(kind.values)
    inner = rng.choice([v for v in kind.values if v[0] not in (old, new) and v[1] not in (old, new)] or [kind.values[0]])
    shown = inner[2]
    inner_code = inner[0]
    fn = f"Widget r(c) {{\n  return Text('${{{kind.read}}}');\n}}"
    code = f"var f = false;\n{fn}\n" + _root(kind, _cond(old, new), _root(kind, inner_code, "Builder(builder: r)"))
    return item("after f = true?", code, shown,
                f"There are two {kind.name}s above; the nearest one decides, and it says {shown} whatever the outer one does.",
                "f = true;\n" + REBUILD + READ)


def sizeof_item(rng: random.Random, aspect: bool):
    """MediaQuery.of vs MediaQuery.sizeOf: only the pixel ratio changes."""
    old, new = rng.choice(((1, 2), (2, 3), (1, 3)))
    read = "MediaQuery.sizeOf(c)" if aspect else "MediaQuery.of(c)"
    fn = f"Widget r(c) {{\n  {read};\n  return Text('${{++b}}');\n}}"
    code = (f"var f = false, b = 0, k = Builder(builder: r);\n{fn}\n"
            f"MediaQuery(data: MediaQueryData(size: Size(9, 9), devicePixelRatio: f ? {new} : {old}), child: k)")
    why = ("sizeOf depends on the size only, and only the pixel ratio changed: r is not run again, 1." if aspect
           else "MediaQuery.of depends on all of MediaQueryData, so any change rebuilds the dependents: 2.")
    return item("after f = true?", code, 1 if aspect else 2, why, "f = true;\n" + REBUILD + READ)


def _spec_templates() -> list[Maker]:
    out: list[Maker] = []
    for kind in (DTS, ICON, MQ, TICKER, THEME):
        n = kind.name
        out.append(template(f"{n}_value_identical_depend", read_item, kind, True, True))
        out.append(template(f"{n}_value_fresh", read_item, kind, False, True))
        if kind is not MQ:  # (mq_of_all below is this one, with a size added)
            out.append(template(f"{n}_builds_identical_depend", builds_item, kind, True, True))
        out.append(template(f"{n}_builds_unchanged", builds_item, kind, True, True, False))
        out.append(template(f"{n}_builds_fresh", builds_item, kind, False, True))
        if kind.get:
            out.append(template(f"{n}_value_identical_get", read_item, kind, True, False))
            out.append(template(f"{n}_value_fresh_get", read_item, kind, False, False))
            out.append(template(f"{n}_builds_identical_get", builds_item, kind, True, False))
            out.append(template(f"{n}_builds_fresh_get", builds_item, kind, False, False))
    out.append(template("mq_of_all", sizeof_item, False))
    out.append(template("mq_size_only", sizeof_item, True))
    out.append(template("DefaultTextStyle_nearest", nearest_item, DTS))
    return out


TEMPLATES: tuple[Maker, ...] = tuple(_spec_templates())
