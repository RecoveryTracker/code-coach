"""Dart: null safety, and the collections the pages never opened.

The audit found Dart the emptiest of the seven relative to what its
solutions use. Across sixteen hundred Dart answers the workbook had never
written `Map<`, never written `Set<`, never called `.sort`, `.map` or
`.where`, and never once used `??`, `?.` or `late`.

The null-safety gap is the serious one. Dart is null-safe by default, so
`int` and `int?` are different types and the compiler enforces the
difference, exactly as Rust does with Option. The Dart solutions lean on it
constantly: `Node?` for a child that might not be there, `??=` to fill a
parameter that arrived null, `!` to promise the compiler something it
cannot prove. A student who had done every Dart page in the book had never
seen any of it.

Ten pages. Null safety first because it is the type system, then the
collections, then the node object those two combine into.

Dart only. Nothing prints a list directly: Dart renders one as `[1, 2, 3]`
and these answers are compared as text.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("dart",)

SHAPES: tuple[Shape, ...] = (
    Shape("dart_null", "the question mark that changes the type"),
    Shape("dart_map", "a keyed store, and the key that is not there"),
    Shape("dart_set", "membership without repeats"),
    Shape("dart_list_make", "building a list of a known length"),
    Shape("dart_list_ops", "adding and taking away"),
    Shape("dart_iter", "map, where, and what makes them run"),
    Shape("dart_sort", "sorting in place, with a comparison"),
    Shape("dart_string", "splitting, joining, padding"),
    Shape("dart_node", "a class that points at itself"),
    Shape("dart_tree", "two children, either of which might be missing"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(f"'{s}'" for s in items) + "]"


def _main(*body: str) -> str:
    return _lines("void main() {", *(f"  {line}" if line else "" for line in body), "}")


# ── 81. Null safety ──────────────────────────────────────────


def _null(a: dict) -> str:
    values, over = a["values"], a["over"]
    return _main(
        f"final items = {_nums(values)};",
        "// firstWhere with orElse would throw on no match, so this looks",
        "// for the index instead and lets it be -1.",
        f"final at = items.indexWhere((n) => n > {over});",
        "int? found = at == -1 ? null : items[at];",
        f"print(found ?? {a['fallback']});",
        "print(found == null);",
        "// ??= only assigns when the left side is null.",
        f"found ??= {a['fallback']};",
        "print(found);",
    )


# ── 82. Map ──────────────────────────────────────────────────


def _map(a: dict) -> str:
    pairs, look = a["pairs"], a["look"]
    sets = [f"ages['{k}'] = {v};" for k, v in pairs]
    return _main(
        "final ages = <String, int>{};",
        *sets,
        f"final found = ages['{look}'];",
        "print(found ?? 'missing');",
        f"print(ages.containsKey('{look}'));",
        "print(ages.length);",
        "final keys = ages.keys.toList()..sort();",
        "print(keys.join(' '));",
    )


# ── 83. Set ──────────────────────────────────────────────────


def _set(a: dict) -> str:
    return _main(
        f"final items = {_nums(a['values'])};",
        "final seen = items.toSet();",
        f"seen.remove({a['dropped']});",
        "final kept = seen.toList()..sort();",
        "print(kept.join(' '));",
        "print(seen.length);",
        f"print(seen.contains({a['probe']}));",
    )


# ── 84. Building a list ──────────────────────────────────────


def _list_make(a: dict) -> str:
    n, step = a["n"], a["step"]
    if a["want"] == "filled":
        return _main(
            f"final filled = List<int>.filled({n}, {step});",
            "print(filled.join(' '));",
            "print(filled.length);",
        )
    return _main(
        f"final made = List<int>.generate({n}, (i) => i * {step});",
        "print(made.join(' '));",
        "print(made.length);",
    )


# ── 85. Adding and taking away ───────────────────────────────


def _list_ops(a: dict) -> str:
    return _main(
        f"final items = {_nums(a['values'])}.toList();",
        f"items.add({a['added']});",
        "final last = items.removeLast();",
        "print(last);",
        f"final gone = items.removeAt({a['at']});",
        "print(gone);",
        f"items.insert(0, {a['front']});",
        "print(items.join(' '));",
    )


# ── 86. map and where ────────────────────────────────────────


def _iter(a: dict) -> str:
    values, want = a["values"], a["want"]
    if want == "doubled":
        return _main(
            f"final items = {_nums(values)};",
            "final doubled = items.map((n) => n * 2).toList();",
            "print(doubled.join(' '));",
        )
    if want == "kept":
        return _main(
            f"final items = {_nums(values)};",
            f"final kept = items.where((n) => n > {a['over']}).toList();",
            "print(kept.join(' '));",
            "print(kept.length);",
        )
    return _main(
        f"final items = {_nums(values)};",
        "final total = items.reduce((a, b) => a + b);",
        "print(total);",
        "final biggest = items.reduce((a, b) => a > b ? a : b);",
        "print(biggest);",
    )


# ── 87. Sorting ──────────────────────────────────────────────


def _sort(a: dict) -> str:
    if a["want"] == "numbers":
        return _main(
            f"final items = {_nums(a['values'])}.toList();",
            "// sort returns nothing: it reorders in place, which is why",
            "// the cascade is used to sort and keep the list.",
            "items.sort((x, y) => x - y);",
            "print(items.join(' '));",
            f"final down = {_nums(a['values'])}.toList()"
            "..sort((x, y) => y - x);",
            "print(down.join(' '));",
        )
    return _main(
        f"final words = {_strs(a['words'])}.toList();",
        "words.sort((x, y) {",
        "  final byLength = x.length.compareTo(y.length);",
        "  return byLength != 0 ? byLength : x.compareTo(y);",
        "});",
        "print(words.join(' '));",
    )


# ── 88. Strings ──────────────────────────────────────────────


def _string(a: dict) -> str:
    if a["want"] == "repeat":
        return _main(
            f"final unit = '{a['unit']}';",
            f"print(unit * {a['times']});",
            f"print('{a['word']}'.padLeft({a['width']}, '.'));",
        )
    return _main(
        f"final text = '{a['text']}';",
        f"final parts = text.split('{a['sep']}');",
        "print(parts.join('-'));",
        "print(parts.length);",
        f"print(text.substring(0, {a['cut']}));",
    )


# ── 89-90. Node objects ──────────────────────────────────────

_LIST_NODE = (
    "class ListNode {",
    "  int val;",
    "  ListNode? next;",
    "  ListNode(this.val, [this.next]);",
    "}",
    "",
)

_TREE_NODE = (
    "class TreeNode {",
    "  int val;",
    "  TreeNode? left;",
    "  TreeNode? right;",
    "  TreeNode(this.val, [this.left, this.right]);",
    "}",
    "",
    "int depth(TreeNode? node) {",
    "  if (node == null) return 0;",
    "  final a = depth(node.left);",
    "  final b = depth(node.right);",
    "  return 1 + (a > b ? a : b);",
    "}",
    "",
    "int total(TreeNode? node) {",
    "  if (node == null) return 0;",
    "  return node.val + total(node.left) + total(node.right);",
    "}",
    "",
)


def _node(a: dict) -> str:
    values = a["values"]
    return _lines(
        *_LIST_NODE,
        "void main() {",
        f"  final values = {_nums(values)};",
        "  ListNode? head;",
        "  for (final v in values.reversed) {",
        "    head = ListNode(v, head);",
        "  }",
        "  final out = <String>[];",
        "  // node is ListNode? so the loop has to prove it is not null",
        "  // before reaching through it. That is the type doing its job.",
        "  var node = head;",
        "  while (node != null) {",
        "    out.add(node.val.toString());",
        "    node = node.next;",
        "  }",
        "  print(out.join(' -> '));",
        "  print(out.length);",
        "}",
    )


def _tree(a: dict) -> str:
    values = a["values"]
    lines = [f"  final n{i} = TreeNode({v});" for i, v in enumerate(values)]
    for i in range(len(values)):
        left, right = 2 * i + 1, 2 * i + 2
        if left < len(values):
            lines.append(f"  n{i}.left = n{left};")
        if right < len(values):
            lines.append(f"  n{i}.right = n{right};")
    return _lines(
        *_TREE_NODE,
        "void main() {",
        *lines,
        "  print(n0.val);",
        "  print(depth(n0));",
        "  print(total(n0));",
        "}",
    )


_BUILDERS = {
    "dart_null": _null,
    "dart_map": _map,
    "dart_set": _set,
    "dart_list_make": _list_make,
    "dart_list_ops": _list_ops,
    "dart_iter": _iter,
    "dart_sort": _sort,
    "dart_string": _string,
    "dart_node": _node,
    "dart_tree": _tree,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, from the data rather than the Dart."""
    a = args
    if shape == "dart_null":
        values, over, fallback = list(a["values"]), a["over"], a["fallback"]
        found = next((n for n in values if n > over), None)
        if found is not None and found == fallback:
            raise ValueError(
                "the fallback must differ from the value found, or the two "
                "branches print the same thing"
            )
        first = found if found is not None else fallback
        return NL.join([
            str(first),
            "true" if found is None else "false",
            str(first),
        ])
    if shape == "dart_map":
        pairs = [tuple(p) for p in a["pairs"]]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the writes")
        if len(table) < 2:
            raise ValueError("one entry does not need a Map")
        look = a["look"]
        found = table.get(look)
        return NL.join([
            "missing" if found is None else str(found),
            "true" if look in table else "false",
            str(len(table)),
            " ".join(sorted(table)),
        ])
    if shape == "dart_set":
        values, dropped, probe = list(a["values"]), a["dropped"], a["probe"]
        if len(set(values)) == len(values):
            raise ValueError(
                "the input must repeat something, or toSet is doing nothing"
            )
        if dropped not in set(values):
            raise ValueError("the removed value must have been there")
        kept = sorted(set(values) - {dropped})
        return NL.join([
            " ".join(str(n) for n in kept), str(len(kept)),
            "true" if probe in kept else "false",
        ])
    if shape == "dart_list_make":
        n, step = a["n"], a["step"]
        if n < 2:
            raise ValueError("a length of one shows no pattern")
        if a["want"] == "filled":
            return NL.join([" ".join([str(step)] * n), str(n)])
        if step == 0:
            raise ValueError("a step of zero makes every element the same")
        return NL.join([" ".join(str(i * step) for i in range(n)), str(n)])
    if shape == "dart_list_ops":
        values = list(a["values"])
        added, at, front = a["added"], a["at"], a["front"]
        after = values + [added]
        last = after.pop()
        if not 0 <= at < len(after):
            raise ValueError("the index removed must be inside the list")
        gone = after.pop(at)
        after.insert(0, front)
        return NL.join([
            str(last), str(gone), " ".join(str(n) for n in after),
        ])
    if shape == "dart_iter":
        values, want = list(a["values"]), a["want"]
        if not values:
            raise ValueError("reduce on an empty list throws")
        if want == "doubled":
            return " ".join(str(n * 2) for n in values)
        if want == "kept":
            over = a["over"]
            kept = [n for n in values if n > over]
            if not kept or len(kept) == len(values):
                raise ValueError("where must keep some and drop some")
            return NL.join([
                " ".join(str(n) for n in kept), str(len(kept)),
            ])
        return NL.join([str(sum(values)), str(max(values))])
    if shape == "dart_sort":
        if a["want"] == "numbers":
            values = list(a["values"])
            if values == sorted(values):
                raise ValueError("the data must not already be sorted")
            return NL.join([
                " ".join(str(n) for n in sorted(values)),
                " ".join(str(n) for n in sorted(values, reverse=True)),
            ])
        words = list(a["words"])
        order = sorted(words, key=lambda w: (len(w), w))
        if order == words:
            raise ValueError("the words must not already be in order")
        if len({len(w) for w in words}) < 2:
            raise ValueError("the words must differ in length")
        return " ".join(order)
    if shape == "dart_string":
        if a["want"] == "repeat":
            unit, times = a["unit"], a["times"]
            word, width = a["word"], a["width"]
            if times < 2:
                raise ValueError("repeating once is not repeating")
            if width <= len(word):
                raise ValueError("the width must exceed the word")
            return NL.join([unit * times, word.rjust(width, ".")])
        text, sep, cut = a["text"], a["sep"], a["cut"]
        if sep not in text:
            raise ValueError("the separator must be in the text")
        if not 0 < cut < len(text):
            raise ValueError("the substring must take part of the text")
        parts = text.split(sep)
        return NL.join(["-".join(parts), str(len(parts)), text[:cut]])
    if shape == "dart_node":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("a chain needs more than one node")
        return NL.join([
            " -> ".join(str(v) for v in values), str(len(values)),
        ])
    if shape == "dart_tree":
        values = list(a["values"])
        if len(values) < 4:
            raise ValueError("a tree this small has nothing to recurse into")
        depth = 0
        while (1 << depth) - 1 < len(values):
            depth += 1
        return NL.join([str(values[0]), str(depth), str(sum(values))])
    raise KeyError(shape)
