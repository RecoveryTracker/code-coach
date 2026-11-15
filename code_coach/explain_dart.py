"""Plain-English walkthrough of Dart (and Flutter widget code), a statement at a time.

Dart ships no parser we can import, so this reads the way the JavaScript explainer does - shape by shape - with a
little more help: `explain_common.read_pieces` splits the code into statements, headers and arguments that know what
they are nested in, and `explain_expr` reads one expression into a tree. A piece it cannot follow gets an honest
"this reader does not break down yet" row instead of a guess.

Every sentence that states a fact about the language lives in `FACTS` below. A fact that can be shown by evaluating an
expression is written ```EXPR` gives `VALUE``` and tests/test_explain_dart.py runs each such claim in the real
`dart`, so a rule here cannot say something Dart does not do. Flutter code is described, never run.
"""

from __future__ import annotations

import re

from . import explain_common as C
from .explain_expr import N, Say, code, say, try_expr, walk
from .explain_programs import dart_program, is_flutter

# ── The rules that state a checkable fact ──────────────────

FACTS: dict[str, str] = {
    "mod": "`%` never gives a negative answer in Dart: `-7 % 3` gives `2`.",
    "tdiv": "`~/` divides and drops the fraction, rounding toward zero: `-7 ~/ 2` gives `-3`.",
    "div": "`/` always gives a double, even for whole numbers: `6 / 3` gives `2.0`.",
    "coalesce": "`a ?? b` is `b` only when `a` is null: `(null as int?) ?? 5` gives `5`.",
    "nullaware": "`a?.b` is null (and does not throw) when `a` is null: `(null as String?)?.length` gives `null`.",
    "bang": "`x!` promises x is not null and throws if it is.",
    "nullassign": "`a ??= b` stores b only when a is currently null.",
    "final": "A `final` variable is set once; assigning it again is a compile error.",
    "const": "A `const` value is fixed when the program is compiled and can never change.",
    "late": "A `late` variable is set later; reading it before that throws an error.",
    "listeq": "`==` on two lists asks whether they are the same list, not whether they hold the same items: `[1] == [1]` gives `false`.",
    "streq": "`==` on strings compares the letters: `'a' + 'b' == 'ab'` gives `true`.",
    "cascade": "`a..b()` runs b() on a and the whole expression is still a, not b()'s result: `(StringBuffer()..write('x')).toString()` gives `x`.",
    "nofall": "A Dart `switch` case does not run on into the next one, so a `break` is not needed.",
    "async": "An `async` function always returns a Future: `(() async => 1)() is Future` gives `true`.",
    "interp": "`${...}` inside a string is replaced by the value of the expression: `'${1 + 2}'` gives `3`.",
    "isop": "`x is T` asks whether x is a T at run time: `5 is int` gives `true`.",
    "rethrow": "`rethrow` throws the caught error again, with its original stack trace.",
    "records": "A record is a small fixed group of values; two records with equal parts are equal: `(1, 2) == (1, 2)` gives `true`.",
    "spread": "`...xs` pours the items of xs into the list being built: `[0, ...[1, 2]]` gives `[0, 1, 2]`.",
    "collif": "`if` inside a list literal adds an item only when the condition is true: `[if (1 > 2) 9]` gives `[]`.",
    "round": "`.round()` rounds halves away from zero: `(-2.5).round()` gives `-3`.",
}

_NUM_WORDS = {"int": "a whole number", "double": "a decimal number", "num": "a number", "String": "text", "bool": "true or false"}


def _lc(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


# ── Vocabulary ──────────────────────────────────────────────

_METHODS: dict[str, str] = {
    "add": "adds {a} to the end of {t}", "addAll": "adds every item of {a} to {t}", "remove": "removes {a} from {t}",
    "removeAt": "removes the item at position {a} from {t}", "removeLast": "removes the last item of {t}",
    "removeWhere": "removes the items of {t} that pass a test", "insert": "inserts {a} into {t}", "clear": "empties {t}",
    "contains": "checks whether {t} contains {a}", "containsKey": "checks whether {t} has the key {a}",
    "containsValue": "checks whether {t} has the value {a}", "indexOf": "finds where {a} sits in {t}",
    "join": "glues the items of {t} together into one string{a2}", "map": "makes a new lazy sequence by transforming every item of {t}",
    "where": "keeps only the items of {t} that pass a test", "fold": "folds {t} down to one value, starting from {a0}",
    "reduce": "folds {t} down to one value, combining items in pairs", "toList": "turns {t} into a list",
    "toSet": "turns {t} into a set (one of each value)", "sort": "puts {t} in order, changing it in place", "take": "takes the first {a} items of {t}",
    "skip": "skips the first {a} items of {t}", "any": "checks whether any item of {t} passes a test",
    "every": "checks whether every item of {t} passes a test", "split": "breaks {t} apart at {a}",
    "substring": "takes the part of {t} from {a}", "toUpperCase": "makes {t} upper case", "toLowerCase": "makes {t} lower case",
    "trim": "cuts the spaces off both ends of {t}", "replaceAll": "replaces every {a0} in {t} with {a1}", "startsWith": "checks whether {t} starts with {a}",
    "endsWith": "checks whether {t} ends with {a}", "padLeft": "pads {t} on the left to width {a0}", "padRight": "pads {t} on the right to width {a0}",
    "toString": "turns {t} into text", "toStringAsFixed": "writes {t} with {a} digits after the point", "putIfAbsent": "adds {a0} to {t} only if the key is missing",
    "forEach": "runs a function for each item of {t}", "then": "when {t} completes, runs a function with its result", "catchError": "handles an error from {t}",
    "whenComplete": "runs a function when {t} finishes, success or error", "listen": "listens to every event of the stream {t}",
    "sublist": "takes a copy of part of {t}", "expand": "turns each item of {t} into zero or more items", "firstWhere": "finds the first item of {t} that passes a test",
    "whereType": "keeps the items of {t} that have the type {a}", "cast": "views {t} as another type", "abs": "takes the size of {t}, ignoring the sign",
    "round": "rounds {t} to the nearest whole number", "floor": "rounds {t} down", "ceil": "rounds {t} up", "clamp": "keeps {t} between {a0} and {a1}",
    "compareTo": "compares {t} with {a} (negative, zero or positive)", "update": "changes the value stored under {a0} in {t}", "codeUnitAt": "gets the character code at {a} in {t}",
    "write": "writes {a} into {t}", "writeln": "writes {a} and a newline into {t}", "isOdd": "", "complete": "completes {t} with {a}",
    "close": "closes {t}", "reversed": "", "elementAt": "gets item {a} of {t}", "replaceRange": "replaces part of {t}", "last": "",
    "lastWhere": "finds the last item of {t} that passes a test", "singleWhere": "finds the one item of {t} that passes a test", "getRange": "takes items {a0} to {a1} of {t}",
    "addEntries": "adds the entries {a} to {t}", "remainder": "the remainder of {t} divided by {a}", "toDouble": "turns {t} into a double", "toInt": "turns {t} into an int",
    "parse": "reads {a} as a number", "tryParse": "reads {a} as a number, or null if it is not one", "from": "makes a copy of {a}", "of": "makes a copy of {a}",
}
_FUNCS: dict[str, str] = {
    "print": "prints {a}", "max": "the larger of {a}", "min": "the smaller of {a}", "sqrt": "the square root of {a}", "pow": "{a0} raised to the power {a1}",
    "jsonDecode": "reads the JSON text {a} into Dart values", "jsonEncode": "turns {a} into JSON text", "identical": "checks whether {a0} and {a1} are the very same object",
    "Future.value": "a Future already completed with {a}", "Future.delayed": "a Future that completes after a delay", "Future.error": "a Future that fails with {a}",
    "Future.microtask": "queues {a} to run as a microtask", "Future.wait": "waits for all of {a}", "Future.any": "completes with whichever of {a} finishes first",
    "Stream.fromIterable": "a stream that emits each item of {a}", "Stream.periodic": "a stream that emits repeatedly", "scheduleMicrotask": "queues {a} to run as a microtask",
    "List.generate": "builds a list by calling a function for each position up to {a0}", "List.filled": "a list of {a0} copies of {a1}", "List.of": "a copy of {a}",
    "Exception": "an Exception carrying {a}", "StateError": "a StateError saying {a}", "ArgumentError": "an ArgumentError saying {a}", "FormatException": "a FormatException saying {a}",
    "Duration": "a length of time", "DateTime.now": "the current date and time", "Completer": "a Completer: a Future you finish by hand", "StringBuffer": "a StringBuffer, for building text piece by piece",
    "runApp": "starts the Flutter app with {a} as its root widget", "setState": "runs the change and tells Flutter to rebuild this widget", "Set.of": "a copy of {a} as a set",
    "Timer": "a timer that runs a function later", "Map.from": "a copy of the map {a}", "Object": "a plain object", "RegExp": "a regular expression for {a}", "int.parse": "reads {a} as a whole number",
    "double.parse": "reads {a} as a decimal number", "int.tryParse": "reads {a} as a whole number, or null if it is not one", "num.parse": "reads {a} as a number",
}
_WIDGETS = {
    "Row", "Column", "Stack", "Container", "Center", "Align", "Padding", "SizedBox", "Expanded", "Flexible", "Spacer", "Wrap", "ListView", "Text",
    "Icon", "Scaffold", "AppBar", "MaterialApp", "Placeholder", "GestureDetector", "InkWell", "Positioned", "ConstrainedBox", "AspectRatio",
    "FractionallySizedBox", "Form", "TextField", "TextFormField", "Builder", "ValueListenableBuilder", "ListenableBuilder", "FutureBuilder",
    "StreamBuilder", "LayoutBuilder", "Material", "Directionality", "DefaultTextStyle", "IconTheme", "TickerMode", "Opacity", "Card", "FlutterLogo",
    "UnconstrainedBox", "LimitedBox", "OverflowBox", "SingleChildScrollView", "GridView", "SafeArea", "Theme", "ElevatedButton", "TextButton",
    "IconButton", "FloatingActionButton", "Box", "ColoredBox", "DecoratedBox", "Draggable", "Dismissible", "Hero", "Navigator", "Visibility", "Offstage",
}
_LIFECYCLE = {
    "initState": "runs once when the State object is first created: set things up here",
    "dispose": "runs when the State is removed for good: release controllers and subscriptions here",
    "didChangeDependencies": "runs when something this widget depends on (like a Theme) changes",
    "didUpdateWidget": "runs when the parent gives this State a new configuration",
    "build": "builds the widget tree for the current state; Flutter calls it again whenever the state changes",
    "createState": "makes the State object that will hold this widget's changing data",
    "deactivate": "runs when the State is removed from the tree (it may be put back)",
}
_CONTROL = {"if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue", "return", "throw", "rethrow", "try", "catch", "on", "finally", "assert", "yield", "await"}
_DECL_MODS = {"static", "final", "const", "late", "var", "covariant", "external", "abstract"}


def _human_type(t: str) -> str:
    t = t.strip()
    base = t.rstrip("?")
    if base in _NUM_WORDS:
        return _NUM_WORDS[base] + (" or null" if t.endswith("?") else "")
    if base.startswith("List<") or base == "List":
        return "a list"
    if base.startswith("Map<") or base == "Map":
        return "a map (keys to values)"
    if base.startswith("Set<") or base == "Set":
        return "a set"
    if base.startswith("Future"):
        return "a Future (a value that arrives later)"
    if base.startswith("Stream"):
        return "a Stream (values that arrive over time)"
    if base == "dynamic":
        return "a value of any type (checked only when it runs)"
    return f"a {t}" if t else ""


def _kind_of(node: N | None) -> str:
    if node is None:
        return ""
    k = node.kind
    if k == "paren":
        return _kind_of(node.a[0])
    if k == "num":
        return "a decimal number" if re.search(r"[.eE]", node.a[0]) and not node.a[0].lower().startswith("0x") else "a whole number"
    if k == "str":
        return "text"
    if k == "id" and node.a[0] in ("true", "false"):
        return "true or false"
    if k == "id" and node.a[0] == "null":
        return "null"
    if k == "list":
        return "a list"
    if k == "brace":
        return "a map" if node.extra.get("map") else ("a set" if node.a[0] else "an empty map or set")
    if k == "rec":
        return "a record"
    if k == "lam":
        return "a function"
    return ""


# ── Reading expressions ─────────────────────────────────────

def _interp_parts(raw: str) -> list[str]:
    body = raw
    return [(m.group(1) or m.group(2)).strip() for m in re.finditer(r"(?<!\\)\$(?:\{([^{}]*)\}|([A-Za-z_]\w*))", body)]


def _quote_text(raw: str) -> str:
    m = re.match(r"^[rR]?('''|\"\"\"|'|\")(.*)\1$", raw, re.S)
    inner = m.group(2) if m else raw
    return inner


def _string(node: N) -> str | None:
    raw = node.a[0]
    if raw.startswith(("r'", 'r"', "R'", 'R"')):
        return f'the raw text "{_quote_text(raw)}"'
    parts = _interp_parts(raw)
    if parts:
        return f'the text "{_quote_text(raw)}" with {", ".join("`" + p + "`" for p in parts[:3])} filled in'
    return f'"{_quote_text(raw)}"' if len(raw) < 40 else code(raw)


def _args(args: list[N], ctx: Say) -> list[str]:
    out = []
    for a in args:
        if a.kind == "named":
            out.append(f"{a.a[0]}: {say(a.a[1], ctx, 1)}")
        else:
            out.append(say(a, ctx, 1))
    return out


def _widget_phrase(node: N, ctx: Say) -> str:
    name = node.a[0].a[0]
    named = {a.a[0]: a.a[1] for a in node.a[1] if a.kind == "named"}
    pos = [a for a in node.a[1] if a.kind != "named"]
    bits = []
    if name == "Text" and pos:
        bits.append(f"showing {say(pos[0], ctx, 1)}")
    if "children" in named and named["children"].kind == "list":
        kids = [_head(x) for x in named["children"].a[0]]
        shown = ", ".join(kids[:5]) + (f" and {len(kids) - 5} more" if len(kids) > 5 else "")
        if kids:
            bits.append(f"with these children: {shown}")
    if "child" in named:
        bits.append(f"holding {_head(named['child'])}")
    if "home" in named:
        bits.append(f"with {_head(named['home'])} as the home screen")
    props = [k for k in named if k not in ("children", "child", "home", "key")]
    if props and name not in ("Text",):
        bits.append("set with " + ", ".join(props[:4]))
    if "key" in named:
        bits.append("given a key so Flutter can tell it apart")
    return f"{_an(name)} {name} widget" + (" " + " ".join(bits) if bits else "")


def _an(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _head(node: N) -> str:
    """A short name for what an element is: `Text`, `a lambda`, `5`."""
    k = node.kind
    if k == "call" and node.a[0].kind == "id":
        return node.a[0].a[0]
    if k == "call" and node.a[0].kind == "mem":
        return code(node.a[0].text)
    if k == "named":
        return _head(node.a[1])
    if k == "str":
        return code(node.a[0])
    if k == "id" or k == "num":
        return node.a[0]
    if k == "lam":
        return "a function"
    if k in ("if_el", "for_el", "spread"):
        return code(node.text)
    return code(node.text)


def _call(node: N, ctx: Say) -> str | None:
    fn, args = node.a
    argv = _args(args, ctx)
    a = ", ".join(argv)

    def fill(template: str, target: str = "") -> str:
        slots = {"a": a, "t": target}
        for i in range(3):
            slots[f"a{i}"] = argv[i] if i < len(argv) else "it"
        slots["a2"] = f" with {argv[0]} between them" if argv else ""
        return template.format(**slots)

    if fn.kind == "id":
        name = fn.a[0]
        if name in _FUNCS:
            return fill(_FUNCS[name])
        if name in _WIDGETS:
            return _widget_phrase(node, ctx)
        if name[:1].isupper():
            return f"a new {name}" + (f" built from {a}" if a else "")
        return f"calls {name}" + (f" with {a}" if a else " with no arguments")
    if fn.kind == "mem":
        target_node, op, meth = fn.a
        target = say(target_node, ctx, 1)
        full = code(target_node.text) + "." + meth
        if full in _FUNCS:
            return fill(_FUNCS[full])
        if meth in _METHODS and _METHODS[meth]:
            return fill(_METHODS[meth], target)
        if target_node.kind == "id" and target_node.a[0][:1].isupper() and meth[:1].islower() and meth not in _METHODS:
            return f"calls {target}.{meth}" + (f" with {a}" if a else "")
        return f"calls {meth} on {target}" + (f" with {a}" if a else "")
    return None


_IRREGULAR = {"puts": "putting", "runs": "running", "cuts": "cutting", "gets": "getting", "skips": "skipping", "empties": "emptying", "pads": "padding",
              "queues": "queueing", "sets": "setting", "stores": "storing"}
_VERBS = {"adds", "removes", "inserts", "empties", "checks", "finds", "glues", "makes", "keeps", "folds", "turns", "puts", "takes", "skips", "breaks", "cuts",
          "replaces", "pads", "writes", "runs", "handles", "listens", "views", "rounds", "compares", "changes", "gets", "reads", "closes", "completes", "prints",
          "calls", "starts", "waits", "queues", "sets", "tells", "stores", "ANDs", "ORs", "XORs", "shifts", "multiplies", "divides", "subtracts", "when",
          "reads", "builds", "waits"}


def _gerund(word: str) -> str:
    if word in _IRREGULAR:
        return _IRREGULAR[word]
    base = word[:-1] if word.endswith("s") else word
    if base.endswith("e") and not base.endswith("ee"):
        base = base[:-1]
    return base + "ing"


def _value_form(phrase: str) -> str:
    """`glues the items of x` -> `the result of gluing the items of x` (a verb phrase used as a value)."""
    first, _, rest = phrase.partition(" ")
    if first in _VERBS and first != "when":
        return f"the result of {_gerund(first)} {rest}".strip()
    return phrase


def _hook(node: N, ctx: Say, level: int) -> str | None:
    k = node.kind
    if k == "call":
        phrase = _call(node, ctx)
        return _value_form(phrase) if phrase else None
    if k == "list":
        items = node.a[0]
        if not items:
            return "an empty list"
        return "a list of " + ", ".join(say(x, ctx, level + 1) for x in items[:5]) + (f" and {len(items) - 5} more" if len(items) > 5 else "")
    if k == "brace":
        items = node.a[0]
        if not items:
            return "an empty map or set"
        if node.extra.get("map"):
            return "a map of " + ", ".join(say(x, ctx, level + 1) for x in items[:4]) + (" ..." if len(items) > 4 else "")
        return "a set of " + ", ".join(say(x, ctx, level + 1) for x in items[:5])
    if k == "pair":
        return f"{say(node.a[0], ctx, level + 1)} to {say(node.a[1], ctx, level + 1)}"
    if k == "rec":
        items = node.a[0]
        return "a record (" + ", ".join(say(x, ctx, level + 1) for x in items) + ")" if items else "an empty record"
    if k == "named":
        return f"{node.a[0]}: {say(node.a[1], ctx, level + 1)}"
    if k == "spread":
        return f"every item of {say(node.a[0], ctx, level + 1)}"
    if k == "if_el":
        base = f"{say(node.a[1], ctx, level + 1)} only if {say(node.a[0], ctx, level + 1)}"
        return base + (f", otherwise {say(node.a[2], ctx, level + 1)}" if node.a[2] is not None else "")
    if k == "for_el":
        return f"{say(node.a[1], ctx, level + 1)} for each `{code(node.a[0])}`"
    if k == "lam":
        params = ", ".join(p.a[0] for p in node.a[0]) or "nothing"
        body = node.a[1]
        return f"a function taking {params} that gives {say(body, ctx, level + 1)}" if body is not None else f"a function taking {params} (its body is a block)"
    if k == "mem":
        obj, op, name = node.a
        base = say(obj, ctx, level + 1)
        props = {"length": f"the length of {base}", "isEmpty": f"whether {base} is empty", "isNotEmpty": f"whether {base} has anything in it",
                 "first": f"the first item of {base}", "last": f"the last item of {base}", "reversed": f"{base} back to front", "keys": f"the keys of {base}",
                 "values": f"the values of {base}", "entries": f"the key-and-value pairs of {base}", "isOdd": f"whether {base} is odd", "isEven": f"whether {base} is even",
                 "name": f"the name of {base}", "index": f"the position number of {base}", "future": f"the Future of {base}", "stream": f"the Stream of {base}"}
        if name in props and op == ".":
            return props[name]
        if op == "?.":
            return f"{code(node.text)} (null if {base} is null)"
        return code(node.text)
    if k == "is":
        return f"{say(node.a[0], ctx, level + 1)} {'is not' if node.a[2] else 'is'} a {node.a[1]}"
    if k == "as":
        return f"{say(node.a[0], ctx, level + 1)} treated as a {node.a[1]}"
    if k == "cascade":
        secs = ", ".join(code(s.text) for s in node.a[1])
        return f"{say(node.a[0], ctx, level + 1)}, after running {secs} on it"
    if k == "switch":
        return f"the result of matching {say(node.a[0], ctx, level + 1)} against {len(node.a[1])} patterns"
    if k == "await":
        return f"the result of waiting for {say(node.a[0], ctx, level + 1)}"
    if k == "throw":
        return f"throws {say(node.a[0], ctx, level + 1)}"
    if k == "bin" and node.a[0] == "??":
        return f"{say(node.a[1], ctx, level + 1)}, or {say(node.a[2], ctx, level + 1)} if that is null"
    return None


CTX = Say(call=_call, string=_string, hook=_hook, limit=3)


def d(node: N | None) -> str:
    return say(node, CTX) if node is not None else ""


_SEEN: set[str] = set()


def _facts_for(nodes: list[N], text: str = "") -> list[str]:
    """The rule sentences that apply to what this piece uses."""
    ops: set[str] = set()
    kinds: set[str] = set()
    for root in nodes:
        for n in walk(root):
            if n.kind in ("bin", "asg"):
                ops.add(n.a[0])
            kinds.add(n.kind)
            if n.kind == "mem" and n.a[1] == "?.":
                ops.add("?.")
            if n.kind == "mem" and n.a[2] == "round":
                ops.add("round")
    out = []
    if "%" in ops or "%=" in ops:
        out.append(FACTS["mod"])
    if "~/" in ops or "~/=" in ops:
        out.append(FACTS["tdiv"])
    if "/" in ops or "/=" in ops:
        out.append(FACTS["div"])
    if "??" in ops:
        out.append(FACTS["coalesce"])
    if "??=" in ops:
        out.append(FACTS["nullassign"])
    if "?." in ops:
        out.append(FACTS["nullaware"])
    if "bang" in kinds:
        out.append(FACTS["bang"])
    if "cascade" in kinds:
        out.append(FACTS["cascade"])
    if "round" in ops:
        out.append(FACTS["round"])
    if "if_el" in kinds:
        out.append(FACTS["collif"])
    if "spread" in kinds:
        out.append(FACTS["spread"])
    if "is" in kinds:
        out.append(FACTS["isop"])
    if re.search(r"\$\{[^}]*[-+*/%~<>=!?]", text):
        out.append(FACTS["interp"])
    fresh = [f for f in out if f not in _SEEN]
    _SEEN.update(fresh)
    return fresh[:2]


# ── Statements ──────────────────────────────────────────────

_CLASS_RE = re.compile(
    r"^((?:(?:abstract|sealed|base|final|interface|mixin)\s+)*)(class|mixin|enum|extension\s+type|extension)\b\s*(\w+)?\s*(<[^>]*(?:<[^>]*>[^>]*)*>)?\s*(?:\((.*?)\))?\s*"
    r"(?:extends\s+([\w.<>?, ]+?))?\s*(?:with\s+([\w.<>?, ]+?))?\s*(?:implements\s+([\w.<>?, ]+?))?\s*(?:on\s+([\w.<>?, ]+?))?\s*$",
    re.S,
)


def _class(text: str) -> str | None:
    m = _CLASS_RE.match(text.strip())
    if not m:
        return None
    mods, kind, name, generics, _rep, ext, with_, impl, on = m.groups()
    mods = mods or ""
    if kind == "extension" and not name and on:
        return f"adds new abilities to {on.strip()} without changing that type (an extension)."
    if kind == "extension" and name:
        return f"adds new abilities to {on.strip() if on else 'a type'} without changing that type (the extension {name})."
    if kind == "enum":
        return f"defines the enum {name}: a fixed set of named values."
    if kind == "mixin":
        s = f"defines the mixin {name}: a bundle of fields and methods other classes can borrow with `with`"
        if on:
            s += f", usable only on {on.strip()}"
        return s + "."
    if kind.startswith("extension"):
        return f"defines {name}, a new type that wraps another one at no run-time cost."
    parts = [f"defines the class {name}"]
    if "abstract" in mods:
        parts[0] = f"defines the abstract class {name} (it cannot be created directly, only extended)"
    if "sealed" in mods:
        parts[0] = f"defines the sealed class {name}: its subtypes are all in this file, so a switch over it can be checked to cover every case"
    if "mixin" in mods and "mixin class" not in parts[0]:
        parts[0] += " that is also a mixin"
    if ext:
        e = ext.strip()
        if e == "StatelessWidget":
            parts.append("which is a widget whose look depends only on what it is given and never changes by itself")
        elif e == "StatefulWidget":
            parts.append("which is a widget that owns changing data (kept in its State class)")
        elif e.startswith("State<"):
            parts.append(f"which is the State object for {e[6:-1]}: it holds the data that changes and builds the widget")
        else:
            parts.append(f"which extends {e}, so it inherits everything {e} has")
    if with_:
        parts.append(f"mixing in {with_.strip()}")
    if impl:
        parts.append(f"and promising to provide everything {impl.strip()} declares")
    return ", ".join(parts) + "."


def _split_top(text: str, sep: str = ",", angles: bool = True) -> list[str]:
    out, depth, cur, quote = [], 0, "", ""
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            cur += ch
            if ch == "\\":
                cur += text[i + 1 : i + 2]
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
            cur += ch
        elif ch in "([{" or (angles and ch == "<"):
            depth += 1
            cur += ch
        elif ch in ")]}" or (angles and ch == ">" and text[i - 1 : i] != "="):
            depth -= 1
            cur += ch
        elif ch == sep and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip():
        out.append(cur)
    return out


def _params(text: str) -> tuple[str, list[str]]:
    """The words for a parameter list, and the fields it fills directly (`this.x`)."""
    inner = text.strip()
    if not inner:
        return "taking nothing", []
    named = optional = False
    names: list[str] = []
    fields: list[str] = []
    for chunk in _split_top(inner.replace("{", "").replace("}", "").replace("[", "[").replace("]", "")):
        c = chunk.strip().strip("[]")
        if not c:
            continue
        had_default = "=" in c
        c = c.split("=")[0].strip()
        parts = c.replace("required ", "").replace("final ", "").split()
        nm = parts[-1] if parts else c
        if nm.startswith("this.") or nm.startswith("super."):
            fields.append(nm.split(".", 1)[1])
            nm = nm.split(".", 1)[1]
        names.append(nm + (" (optional)" if had_default else ""))
    if "{" in inner:
        named = True
    if "[" in inner and not named and re.search(r"\[[^\]]*\w", inner) and inner.strip().find("[") > -1 and not re.match(r"^\w+<", inner):
        optional = True
    extra = " (some are named parameters, written `name: value` when calling)" if named else " (some are optional)" if optional else ""
    return "taking " + ", ".join(names) + extra, fields


_FUNC_PRE = re.compile(r"^(?P<pre>[^=]*?)\s*(?P<name>operator\s*[^\s\w(]+|[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*(?P<gen><[^<>]*(?:<[^<>]*>[^<>]*)*>)?$", re.S)
_GETTER = re.compile(r"^(?P<pre>[^()=]*?)\b(?P<kw>get|set)\s+(?P<name>[A-Za-z_$][\w$]*)\s*(?P<tail>=>.*)?$", re.S)


def _balanced(text: str, start: int) -> int:
    """Index of the `)` that closes the `(` at `start`, or -1."""
    depth, i, quote = 0, start, ""
    while i < len(text):
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "'\"":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def _function(p: C.Piece, text: str) -> str | None:
    if p.mode != "stmt" or p.frame in ("swexpr",):
        return None
    g = _GETTER.match(text)
    if g and p.frame in ("class", "file"):
        name, pre = g.group("name"), g.group("pre").split()
        kind = g.group("kw")
        ret = [w for w in pre if w not in _DECL_MODS]
        stat = " It belongs to the class itself, not to one object (static)." if "static" in pre else ""
        body = ""
        if g.group("tail"):
            e = try_expr(g.group("tail")[2:], True)
            body = f" Its value is {d(e) if e else '`' + code(g.group('tail')[2:]) + '`'}."
        if kind == "get":
            return f"defines the getter {name}: reading `.{name}` runs this code, with no parentheses" + (f", and gives {_human_type(ret[-1])}" if ret else "") + f".{stat}{body}"
        return f"defines the setter {name}: assigning to `.{name}` runs this code.{stat}"
    m = None
    open_i = close_i = -1
    for cand in [i for i, ch in enumerate(text) if ch == "("]:
        c_close = _balanced(text, cand)
        if c_close < 0:
            continue
        mm = _FUNC_PRE.match(text[:cand].strip())
        rest = text[c_close + 1 :].strip()
        if mm and (rest.startswith(("=>", ":", "async", "sync")) or not rest) and mm.group("name") != "Function":
            m, open_i, close_i = mm, cand, c_close
            break
    if m is None:
        return None
    pre, name, params, tail = m.group("pre").strip(), m.group("name"), text[open_i + 1 : close_i], text[close_i + 1 :].strip()
    pre_words = pre.split()
    if pre_words and pre_words[0] in ("await", "throw", "new", "return", "else", "in", "yield", "case", "assert", "on", "if", "while", "for", "switch", "print"):
        return None
    if name in ("if", "for", "while", "switch", "catch", "print") or name.startswith("operator") is False and name in _CONTROL:
        return None
    after_async = re.sub(r"^(?:async\*?|sync\*)\s*", "", tail)
    arrow = after_async.startswith("=>")
    in_class = p.frame == "class"
    if not (p.opens_block or arrow or (in_class and (not tail or tail.startswith(":") or tail.startswith("async") or tail.startswith("sync")))):
        return None
    is_ctor = in_class and (name == p.class_name or name.split(".")[0] == p.class_name)
    if tail and not (arrow or tail.startswith((":", "async", "sync"))):
        return None
    if not pre_words and not is_ctor and not (p.opens_block or arrow):
        return None
    if not pre_words and not is_ctor and name[:1].isupper() and not in_class:
        return None
    pw, fields = _params(params)
    ret = " ".join(w for w in pre_words if w not in _DECL_MODS and w not in ("factory", "async", "operator"))
    if "factory" in pre_words:
        return f"defines the factory constructor {name}, {pw}: it may return an existing object or a different type instead of always making a new one."
    if is_ctor:
        label = f"the named constructor {name}" if "." in name else f"the constructor of {p.class_name}"
        extra = f" It stores {', '.join(fields)} straight into the object's own field{'s' if len(fields) > 1 else ''} (initializing formals)." if fields else ""
        if "const" in pre_words:
            extra += " It is const: an object built from constant values is made once at compile time."
        init = " Anything after the colon runs before the constructor body (the initializer list)." if tail.startswith(":") else ""
        if tail.startswith(":") and "super" in tail:
            init += " It also hands values up to the parent's constructor with super(...)."
        return f"defines {label}, {pw}.{extra}{init}"
    if name.startswith("operator"):
        return f"defines what the operator `{name[8:].strip()}` means for this class."
    if name in _LIFECYCLE and in_class:
        return f"defines {name}: {_LIFECYCLE[name]}."
    asyn = ""
    if tail.startswith("async*"):
        asyn = " It is `async*`: it returns a Stream and sends values out with yield."
    elif tail.startswith("async"):
        asyn = " It is async, so it returns a Future and may use await. " + FACTS["async"]
    elif tail.startswith("sync*"):
        asyn = " It is `sync*`: it returns an Iterable and hands values out one at a time with yield."
    stat = " It belongs to the class itself, not to one object (static)." if "static" in pre_words else ""
    arrow_txt = ""
    if arrow and p.opens_block:
        arrow_txt = " Its body is a switch expression, and the arms below pick the result." if after_async[2:].strip().startswith("switch") else " Its body continues on the lines below."
    elif arrow:
        body = after_async[2:].strip()
        e = try_expr(body, True)
        if e is not None and e.kind == "call":
            arrow_txt = f" Its whole body is one call that {_call(e, CTX) or d(e)}. " + " ".join(_facts_for([e], body))
        elif e is not None:
            arrow_txt = f" Its body is the single expression {d(e)}. " + " ".join(_facts_for([e], body))
        else:
            arrow_txt = f" Its body is the single expression `{code(body)}`."
    if name == "main":
        return f"defines main, {pw}: the function Dart runs first.{asyn}{arrow_txt}"
    r = f", giving back {_human_type(ret)}" if ret and ret != "void" else (", giving back nothing" if ret == "void" else "")
    kind = "method" if in_class else "function"
    return f"defines the {kind} {name}, {pw}{r}.{asyn}{stat}{arrow_txt}".replace("..", ".")


def _multi_decl(p: C.Piece, text: str) -> str | None:
    """`var a = 1, b = 2;` and `int x, y;`: one declaration for each name."""
    toks = p.toks
    depth, cuts = 0, []
    for i, t in enumerate(toks):
        if t.kind == "str":
            continue
        if t.text in "([{":
            depth += 1
        elif t.text in ")]}":
            depth -= 1
        elif t.text == "," and depth == 0:
            cuts.append(i)
    if not cuts or not toks or toks[0].text not in _DECL_MODS | {"int", "double", "num", "String", "bool", "dynamic", "Object"}:
        return None
    segs, prev = [], 0
    for c in cuts + [len(toks)]:
        segs.append(toks[prev:c])
        prev = c + 1
    first = segs[0]
    depth, eq = 0, len(first)
    for i, t in enumerate(first):
        if t.kind != "str" and t.text in "([{":
            depth += 1
        elif t.kind != "str" and t.text in ")]}":
            depth -= 1
        elif t.text == "=" and depth == 0 and t.kind == "op":
            eq = i
            break
    lhs = first[:eq]
    if len(lhs) < 2 or lhs[-1].kind != "id":
        return None
    prefix = p.text[lhs[0].start - toks[0].start : lhs[-2].end - toks[0].start]
    out = []
    for seg in segs:
        if not seg or not (seg[0].kind == "id"):
            return None
        seg_text = p.text[seg[0].start - toks[0].start : seg[-1].end - toks[0].start]
        full = seg_text if seg is first else prefix + " " + seg_text
        from .explain_expr import tokenize

        sub = C.Piece(p.line, full, tokenize(full, True), p.mode, p.frame, p.class_name, p.class_kind, False, False, "", p.depth)
        sub_text = _decl(sub, full)
        if not sub_text:
            return None
        out.append(sub_text.rstrip())
    return " ".join(_capital(x) for x in out)


def _decl(p: C.Piece, text: str) -> str | None:
    """var / final / const / late / typed declarations and plain assignments."""
    toks = p.toks
    if not toks or toks[0].text in _CONTROL:
        return None
    multi = _multi_decl(p, text)
    if multi:
        return multi
    # find a top-level `=`
    depth, eq = 0, -1
    for i, t in enumerate(toks):
        if t.kind == "str":
            continue
        if t.text in "([{":
            depth += 1
        elif t.text in ")]}":
            depth -= 1
        elif t.text == "=" and depth == 0 and t.kind == "op":
            eq = i
            break
        elif t.text == "<" and depth == 0 and False:
            pass
    lhs = toks[:eq] if eq >= 0 else toks
    rhs_text = ""
    if eq >= 0:
        rhs_text = (p.closed_text[toks[eq].end - toks[0].start :]).strip()
    mods = []
    j = 0
    while j < len(lhs) and lhs[j].text in _DECL_MODS:
        mods.append(lhs[j].text)
        j += 1
    core = lhs[j:]
    if not core:
        return None
    if any(t.text in (".", "[", "(") and t.kind != "str" for t in core) and not (core[0].text in ("(", "[", "{") and mods):
        # `a.b = 1`, `xs[0] = 2`: an assignment, not a declaration - unless it is `Type<..>` / `List<int?>` shaped
        if not (core[-1].kind == "id" and len(core) >= 2 and core[-2].text in (">", "?", "]") and not any(t.text == "." for t in core[-3:-1])):
            return None
    if len(core) == 1 and core[0].kind == "id":
        name, typ = core[0].text, ""
        if not mods and eq < 0:
            return None
        if not mods:
            return None  # plain assignment `x = 3`
    elif core[0].text in ("(", "[", "{") or (core[0].kind == "id" and len(core) > 1 and core[1].text == "(" and mods and mods[-1] in ("var", "final")):
        return _pattern_decl(mods, core, rhs_text)
    else:
        if core[-1].kind != "id":
            return None
        if core[-2].kind != "id" and core[-2].text not in (">", "?", "]"):
            return None
        if core[0].kind != "id":
            return None
        name = core[-1].text
        typ = p.text[core[0].start - toks[0].start : core[-2].end - toks[0].start].strip()
        if not typ:
            return None
    # `int a = 1, b = 2;` arrives as pieces split by commas only in arg mode; in stmt mode it stays one piece
    value = try_expr(rhs_text, True) if rhs_text else None
    mod = set(mods)
    if "static" in mod:
        pre = "defines the class-level "
    else:
        pre = "creates "
    kind = ""
    if "const" in mod:
        kind = " (const: fixed at compile time, can never change)"
    elif "final" in mod and p.frame == "class":
        kind = " (final: set once, in the constructor or here, and never changed after)"
    elif "final" in mod:
        kind = " (final: set once, never reassigned)"
    elif "late" in mod:
        kind = " (late: it is set later, and reading it before then throws an error)" if not rhs_text else " (late: the value is worked out only when it is first read)"
    inf = ""
    if typ:
        inf = f", {_human_type(typ)}"
        if typ.endswith("?"):
            inf += " (the ? means it may hold null)"
    elif "var" in mod or "final" in mod or "const" in mod:
        kd = _kind_of(value)
        inf = f" (Dart works out its type: {kd})" if kd else " (Dart works out its type from the value)"
    subject = f"the variable {name}" if p.frame != "class" else f"the field {name}"
    if rhs_text and value is not None:
        tail = f" and sets it to {d(value)}"
        extra = " ".join(_facts_for([value], rhs_text))
    elif rhs_text:
        tail = f" and sets it to `{code(rhs_text)}`"
        extra = ""
    else:
        tail = " with no value yet" + (" (it starts as null)" if typ.endswith("?") else "")
        extra = ""
    return f"{pre}{subject}{inf}{kind}{tail}. {extra}".strip().replace("a whole number and", "a whole number, and").replace("text and", "text, and")


def _pattern_decl(mods: list[str], core, rhs_text: str) -> str | None:
    open_t = core[0].text
    kind = {"(": "record", "[": "list", "{": "map"}.get(open_t, f"{open_t} object")
    inner = " ".join(t.text for t in core[1:-1] if t.text not in (",",))
    value = try_expr(rhs_text, True) if rhs_text else None
    src = d(value) if value is not None else code(rhs_text)
    return f"takes the {kind} {src} apart and puts its parts into {inner or 'new variables'} at once (a destructuring pattern)."


def _control(p: C.Piece, text: str) -> str | None:
    toks = p.toks
    if not toks:
        return None
    w = toks[0].text
    s = text.strip()
    inner_expr = lambda src: try_expr(src, True)  # noqa: E731
    if w == "else":
        if len(toks) > 1 and toks[1].text == "if":
            rest = _split_head(s[len("else") :].strip())
            return "otherwise, " + _control(_sub(p, rest), rest) if rest else None
        return "otherwise, does what follows."
    if w == "if":
        hd = _head_of(s, "if")
        if not hd:
            return None
        inner_c, tail = hd
        cond = inner_expr(inner_c)
        base = f"if {d(cond) if cond else code(inner_c)}, does what follows."
        if re.search(r"\bcase\b", inner_c) and cond is None:
            base = f"if the value matches the pattern in `{code(inner_c)}`, does what follows. (A pattern can test a shape and pull its parts out in one step.)"
        if tail:
            inner = _stmt_text(p, tail)
            if inner:
                base = f"if {d(cond) if cond else code(inner_c)}, then {_lc(inner)}"
        return base + " " + " ".join(_facts_for([cond] if cond else [], inner_c))
    if w in ("for", "await") and len(toks) > 1:
        aw = bool(re.match(r"^await\s+", s))
        hd = _head_of(re.sub(r"^await\s+", "", s), "for")
        if not hd:
            return None
        head, after = hd
        mi = re.match(r"^(?:final\s+|var\s+|const\s+)?(?:[\w<>?,.\[\] ]+\s+)?(\w+)\s+in\s+(.+)$", head, re.S)
        mp = re.match(r"^(?:final\s+|var\s+|const\s+)?(.+?)\s+in\s+(.+)$", head, re.S)
        if mi or mp:
            mm = mi or mp
            e = inner_expr(mm.group(2))
            what = d(e) if e else code(mm.group(2))
            item = mm.group(1) if mi else f"`{code(mm.group(1))}` pattern"
            return (f"waits for each event of the stream {what}" if aw else f"goes through {what}") + f", one {item} at a time." + _tail(p, after)
        parts = head.split(";") if head.count(";") == 2 else _split_top(head, ";", angles=False)
        if head.strip() == ";;":
            return "loops forever (there is no condition) until something inside breaks out." + _tail(p, after)
        if len(parts) == 3:
            init, cond, step = (x.strip() for x in parts)
            i_name = re.search(r"(\w+)\s*=", init)
            e = inner_expr(cond)
            return (f"counts with {i_name.group(1) if i_name else 'a counter'} starting at `{code(init)}`, keeps going while "
                    f"{d(e) if e else code(cond)}, and does `{code(step)}` after each time round." + _tail(p, after))
        return None
    if w == "while":
        hd = _head_of(s, "while")
        if not hd:
            return None
        e = inner_expr(hd[0])
        return f"keeps looping while {d(e) if e else code(hd[0])}." + _tail(p, hd[1])
    if w == "do":
        return "does what follows once, then checks the while condition after it and repeats."
    if w == "switch":
        hd = _head_of(s, "switch")
        e = inner_expr(hd[0]) if hd else None
        return f"compares {d(e) if e else code(s[6:])} against each case below and runs the first one that matches. {FACTS['nofall']}"
    if w == "case":
        m = re.match(r"^case\s+(.*?)\s*:\s*(.*)$", s, re.S)
        if m:
            pat = m.group(1)
            wh = ""
            mw = re.match(r"^(.*?)\s+when\s+(.*)$", pat, re.S)
            if mw:
                pat, wh = mw.group(1), f", but only when {code(mw.group(2))}"
            tail = m.group(2).strip()
            base = f"when the value matches {code(pat)}{wh}:"
            if tail:
                inner = _stmt_text(p, tail)
                return f"{base} {_lc(inner) if inner else '`' + code(tail) + '`'}"
            return base.rstrip(":") + ", runs the code below (an empty case like this shares the next case's code)."
        return None
    if w == "default":
        m = re.match(r"^default\s*:\s*(.*)$", s, re.S)
        tail = m.group(1).strip() if m else ""
        inner = _stmt_text(p, tail) if tail else ""
        return "when nothing above matched: " + (_lc(inner) if inner else "runs the code below.")
    if re.match(r"^[A-Za-z_]\w*\s*:$", s) and w not in ("default",):
        return f"a label: `break {w}` or `continue {w}` can now name the loop that follows."
    if w == "break":
        return "stops the loop (or leaves the switch case) right here."
    if w == "continue":
        return "skips the rest of this round of the loop and starts the next."
    if w == "return":
        v = s[6:].strip()
        if not v:
            return "stops this function and gives back nothing."
        e = inner_expr(v)
        return f"gives back {d(e) if e else '`' + code(v) + '`'} and stops this function. " + " ".join(_facts_for([e] if e else [], v))
    if w == "throw":
        e = inner_expr(s[5:].strip())
        return f"throws {d(e) if e else code(s[5:])}: the function stops and the error travels up to the nearest catch."
    if w == "rethrow":
        return f"throws the caught error again so the caller sees it. {FACTS['rethrow']}"
    if w == "try":
        return "tries what follows; if it throws, the catch below takes over."
    if w == "finally":
        return "runs what follows whether or not anything above threw."
    if w in ("catch", "on"):
        m = re.match(r"^on\s+([\w<>?.]+)(?:\s+catch\s*\(([^)]*)\))?\s*$", s)
        if m:
            who = f" and calls it {m.group(2).split(',')[0].strip()}" if m.group(2) else ""
            return f"handles an error only if it is a {m.group(1)}{who}."
        m = re.match(r"^catch\s*\(([^)]*)\)\s*$", s)
        if m:
            names = [x.strip() for x in m.group(1).split(",")]
            return f"handles any error that was thrown, calling it {names[0]}" + (f" (and its stack trace {names[1]})" if len(names) > 1 else "") + "."
        return None
    if w == "assert":
        return "checks that this is true while developing (it is ignored in a release build) and stops the program if it is not."
    if w in ("yield",):
        star = s.startswith("yield*")
        e = inner_expr(s[6 if star else 5 :].strip())
        return (f"hands out every value of {d(e) if e else code(s)}" if star else f"hands out {d(e) if e else code(s[5:])}") + " as the next value of the stream or iterable."
    return None


def _split_head(s: str) -> str:
    return s


def _head_of(s: str, kw: str) -> tuple[str, str] | None:
    """`kw (inner) rest` -> (inner, rest), matching the parentheses properly."""
    m = re.match(rf"^{kw}\s*\(", s)
    if not m:
        return None
    start = m.end() - 1
    end = _balanced(s, start)
    if end < 0:
        return None
    return s[start + 1 : end], s[end + 1 :].strip()


def _sub(p: C.Piece, text: str) -> C.Piece:
    from .explain_expr import tokenize

    return C.Piece(p.line, text, tokenize(text, True), p.mode, p.frame, p.class_name, p.class_kind, p.opens_block, p.lambda_block, p.closers, p.depth)


def _stmt_text(p: C.Piece, text: str) -> str:
    """A one-line statement that follows an `if (...)` or a `case x:` on the same line."""
    text = text.strip().rstrip(";")
    sp = _sub(p, text)
    out = _control(sp, text) or _expr_statement(sp, text)
    return out or ""


def _tail(p: C.Piece, tail: str) -> str:
    tail = tail.strip().rstrip(";")
    if not tail:
        return ""
    inner = _stmt_text(p, tail)
    return f" Each time: {_lc(inner)}" if inner else ""


def _assign_text(node: N) -> str:
    op, lhs, rhs = node.a
    left, right = d(lhs), d(rhs)
    if op == "=":
        if lhs.kind == "idx":
            return f"stores {right} at position {d(lhs.a[1])} of {d(lhs.a[0])}"
        return f"sets {left} to {right}"
    if op == "??=":
        return f"sets {left} to {right}, but only if {left} is null right now"
    verb = {"+=": f"adds {right} to {left}", "-=": f"subtracts {right} from {left}", "*=": f"multiplies {left} by {right}",
            "/=": f"divides {left} by {right}", "%=": f"sets {left} to the remainder of {left} divided by {right}",
            "~/=": f"divides {left} by {right}, dropping the fraction", "<<=": f"shifts {left} left by {right}",
            ">>=": f"shifts {left} right by {right}", "&=": f"ANDs {right} into {left}", "|=": f"ORs {right} into {left}", "^=": f"XORs {right} into {left}",
            ">>>=": f"shifts {left} right (unsigned) by {right}"}
    return verb.get(op, f"updates {left} with {right}")


def _expr_statement(p: C.Piece, text: str) -> str | None:
    src = p.closed_text if text == p.text else text
    node = try_expr(src, True)
    if node is None:
        return None
    k = node.kind
    if k == "call" and node.a[0].kind == "id" and node.a[0].a[0] in ("for", "if", "while", "switch", "catch", "do"):
        return None  # a statement the control-flow rules failed to read is not a call
    facts = " ".join(_facts_for([node], src))
    if k == "asg":
        return _assign_text(node) + ". " + facts
    if k in ("post", "un") and (node.a[0] in ("++", "--")):
        target = node.a[1]
        return f"{'adds' if node.a[0] == '++' else 'subtracts'} one {'to' if node.a[0] == '++' else 'from'} {d(target)}."
    if k == "call":
        fn = node.a[0]
        if fn.kind == "id" and fn.a[0] == "setState" and p.lambda_block:
            return "tells Flutter this widget's state is changing: it runs the function below, then rebuilds the widget."
        if fn.kind == "id" and fn.a[0] == "setState":
            return _capital(d(node)) + "."
        phrase = _call(node, CTX) or d(node)
        if p.lambda_block:
            phrase += " (the function body follows on the next lines)"
        return _capital(phrase) + ". " + facts
    if k == "await":
        return f"waits for {d(node.a[0])} to finish before moving on. " + facts
    if k == "cascade":
        return f"takes {d(node.a[0])} and runs {', '.join(code(s.text) for s in node.a[1])} on it, one after another. {FACTS['cascade']}"
    if k in ("throw",):
        return f"throws {d(node.a[0])}."
    if k == "rec" and not node.a[0]:
        return None
    if k == "mem" or k == "id" or k == "num" or k == "str":
        return f"just evaluates {d(node)} (a bare value: a drill's Run it prints it when it is the last line)."
    return f"evaluates {d(node)}. {facts}"


def _capital(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


def _annotation_or_import(text: str) -> str | None:
    s = text.strip()
    m = re.match(r"^(import|export|part)\s+['\"]([^'\"]+)['\"](.*)$", s)
    if m:
        extra = ""
        if " as " in m.group(3):
            extra = f", under the prefix {m.group(3).split(' as ')[1].split()[0].strip(';')}"
        if "show" in m.group(3) or "hide" in m.group(3):
            extra += ", limited as written"
        if m.group(1) == "import":
            return f"brings in the library `{m.group(2)}` so its names can be used here{extra}."
        return f"{m.group(1)}s `{m.group(2)}`."
    if s.startswith("@"):
        name = s.split("(")[0][1:].strip()
        return {"override": "marks the method below as replacing one from a parent class (the compiler checks there is one to replace).",
                "immutable": "promises the class below never changes after it is made.",
                "required": "marks the parameter below as required."}.get(name, f"an annotation: the note `@{name}` for tools and the compiler.")
    return None


_ARM = re.compile(r"^(?P<pat>.+?)\s*=>\s*(?P<val>.+?)\s*$", re.S)


def _arg_piece(p: C.Piece, text: str) -> str | None:
    """An argument or element inside brackets: `child: Text('a')`, `Text('b')`, `...xs`, `if (c) 1`, a map pair."""
    s = p.closed_text
    # named argument
    m = re.match(r"^([A-Za-z_]\w*)\s*:\s*(.*)$", s, re.S)
    if m and not s.startswith(("case ", "default")):
        name, value = m.group(1), m.group(2)
        e = try_expr(value, True)
        kind = ""
        if name.startswith("on") and name[2:3].isupper():
            kind = " (an event handler: it runs when that happens)"
        if name == "builder":
            kind = " (a function Flutter calls to build this part)"
        if e is not None:
            return f"`{name}` is {d(e)}{kind}. " + " ".join(_facts_for([e], value))
        m2 = re.match(r"^([A-Za-z_]\w*(?:\.\w+)?)\s*\(", value)
        if m2:
            return f"`{name}` is {_article(m2.group(1))} whose own arguments follow below.{kind}"
        return None
    # collection pieces
    e = try_expr(s, True)
    if e is not None:
        if e.kind == "pair":
            return f"the entry {d(e)}."
        if e.kind == "call" and e.a[0].kind == "id" and e.a[0].a[0] in _WIDGETS:
            return _capital(d(e)) + "."
        return _capital(d(e)) + ". " + " ".join(_facts_for([e], s))
    m2 = re.match(r"^([A-Za-z_]\w*(?:\.\w+)?)\s*\(", s)
    if m2:
        return f"starts {_article(m2.group(1))}; its arguments follow below."
    m3 = re.match(r"^\.\.\.\??", s)
    if m3:
        return f"pours in every item of `{code(s[3:])}`."
    return None


def _article(name: str) -> str:
    if name in _WIDGETS:
        return f"{_an(name)} {name} widget"
    return f"a call to {name}"


def describe_piece(p: C.Piece) -> str | None:
    text = p.text.strip()
    if not text:
        return None
    if p.mode == "arg":
        return _arg_piece(p, text)
    if p.mode == "cont":
        e = try_expr("__r" + text, True) if text[0] == "." or text[:2] in ("?.", "..") else None
        if e is not None:
            return "continues the line above: then " + _lc(_call(e, CTX) if e.kind == "call" and _call(e, CTX) else d(e)).replace("__r", "the result so far") + "."
        return f"continues the statement above with `{code(text)}`."
    out = _annotation_or_import(text)
    if out:
        return out
    if p.opens_block and re.match(r"^\(.*\)\s*(?:async\*?)?$", text, re.S):
        return "starts a function with no name, written right here; it is called as soon as its block ends."
    if text == "()" and p.mode == "stmt":
        return "calls the function that was just written, right away (the `()` after the block runs it)."
    if p.frame == "swexpr":
        m = _ARM.match(p.closed_text.rstrip().rstrip(",").rstrip())
        if m:
            e = try_expr(m.group("val"), True)
            pat = m.group("pat")
            wh = ""
            mw = re.match(r"^(.*?)\s+when\s+(.*)$", pat, re.S)
            if mw:
                pat, wh = mw.group(1), f", and only when {code(mw.group(2))}"
            return f"when the value matches {code(pat)}{wh}, the result is {d(e) if e else code(m.group('val'))}."
    c = _class(text) if p.opens_block or re.match(r"^(?:abstract|sealed|base|final|interface|mixin)?\s*(?:class|mixin|enum|extension)\b", text) else None
    if c:
        return c
    out = _control(p, p.closed_text if p.closers and not p.opens_block else text)
    if out:
        return out
    out = _function(p, p.closed_text if not p.opens_block else text)
    if out:
        return out
    if text.endswith("=>") is False and p.frame == "class" and text.startswith(("final ", "var ", "late ", "static ", "const ")) is False:
        pass
    out = _decl(p, text)
    if out:
        return out
    if p.frame == "class" and re.match(r"^[a-z_]\w*(?:\([^()]*\))?(?:\s*,\s*[a-z_]\w*(?:\([^()]*\))?)*$", text):
        names = [x.strip().split("(")[0] for x in _split_top(text)]
        return f"lists the enum values {', '.join(names)}" + (" (the arguments go to the enum's constructor)" if "(" in text else "") + "."
    if re.match(r"^(?:final|var|late|const|static)\b", text) is None and p.frame == "class":
        # a field written with a type only: `int count = 0;` is handled by _decl; `String name;` falls here
        m = re.match(r"^([\w<>?,.\[\] ]+?)\s+(\w+)$", text)
        if m and m.group(1).split()[0] not in _CONTROL:
            return f"declares the field {m.group(2)}, {_human_type(m.group(1))}, with no value yet."
    m = re.match(r"^([\w<>?,.\[\] ]+?)\s+(\w+)(?:\s*,\s*\w+)*$", text)
    if m and p.frame != "class" and m.group(1).split()[0] not in _CONTROL and not text.startswith(("return", "throw", "await", "yield")):
        return f"declares {m.group(2)}, {_human_type(m.group(1))}, with no value yet."
    if p.frame in ("class",) and re.match(r"^(?:static\s+|final\s+)*(\w+)\s+(\w+)(?:\s*[=;].*)?$", text):
        pass
    out = _expr_statement(p, text)
    if out:
        return out
    return None


# ── The whole thing ─────────────────────────────────────────

def _read_rows(code_text: str) -> tuple[list[dict], int, list[str]]:
    """Rows, how many non-structural lines there are, and the notes about unreadable lines (for tests)."""
    infos = C.read_pieces(code_text, True)
    _SEEN.clear()
    rows: list[dict] = []
    fallback_lines: list[int] = []
    for info in infos:
        if info.structural or not info.pieces:
            continue
        texts: list[str] = []
        failed = False
        for piece in info.pieces:
            try:
                t = describe_piece(piece)
            except Exception:
                t = None
            if t is None:
                failed = True
            else:
                texts.append(t)
        if failed and not texts:
            text = C.FALLBACK
            fallback_lines.append(info.line)
        elif failed:
            text = C.sentence(texts) + " " + C.FALLBACK
            fallback_lines.append(info.line)
        else:
            text = C.sentence(texts)
        rows.append({"line": info.line, "depth": info.depth, "source": info.raw.strip(), "text": text})
    return rows, len(rows), [str(n) for n in fallback_lines]


def explain_dart(code_text: str, *, run: bool = True, context: str = "") -> dict:
    """Walk Dart line by line, and (when `run`) say what running it printed."""
    if not code_text.strip():
        return C.empty()
    try:
        rows, _n, _bad = _read_rows(code_text)
    except Exception:
        rows = []
    flutter = is_flutter(code_text, context)
    classes = re.findall(r"^\s*(?:abstract\s+|sealed\s+)?class\s+(\w+)", code_text, re.M)
    if flutter:
        summary = "This is Flutter widget code" + (f" (it defines {C.join_names(classes)})" if classes else "") + ". Here's what each part is:"
    elif classes:
        summary = f"This defines {C.join_names(classes)}. Here's what each line does:"
    else:
        summary = "Here's what each line does:"
    notes: list[str] = []
    error_note = None
    if flutter:
        notes.append("Flutter widgets cannot run here: they need Flutter's own engine, not plain Dart, so there is no printed output to show. The rows above say what each widget is; they do not draw the screen.")
    elif run:
        prog = dart_program(code_text, context)
        if not prog.runnable:
            notes.append(prog.why_not)
        else:
            notes, error_note = C.run_notes("dart", prog.text, prog.offset, "snippet.dart")
            if prog.printed_last and notes and not error_note:
                notes.insert(0, "The last line is a bare value, so the program printed it for you (that is how Run it works).")
    return C.finish(summary, rows, notes, error_note)
