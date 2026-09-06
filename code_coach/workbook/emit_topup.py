"""The last few library calls, one page per language.

A re-measure after the C, C++, Rust and Dart tiers landed showed each had
gone from almost nothing to most of the way, and named what was left. Small
lists, but every entry is a call the solution bank actually makes, so
leaving them is leaving a known gap.

C wants realloc, memcmp and atoi. C++ wants insert, clear and the string
comparisons. Rust wants into_iter against iter, is_none, get and take.
Dart wants the null-assertion operator, which is the awkward one: the null
safety pages taught ?? and ??= and never taught !, which is the operator
for the case where you know something the compiler cannot.

One shape per language, one page each. Nothing here is deep; it is the
difference between a language you have been shown and one you can write.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("c", "cpp", "rust", "dart")

SHAPES: tuple[Shape, ...] = (
    Shape("c_more", "growing memory, comparing it, reading a number"),
    Shape("cpp_more", "inserting, clearing, and comparing strings"),
    Shape("rust_more", "consuming an iterator, and asking politely"),
    Shape("dart_more", "the operator for knowing better than the compiler"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

_OWNER = {"c_more": "c", "cpp_more": "cpp",
          "rust_more": "rust", "dart_more": "dart"}


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


# ── C ────────────────────────────────────────────────────────


def _c_more(a: dict) -> str:
    values, extra, text = a["values"], a["extra"], a["text"]
    n = len(values)
    return _lines(
        "#include <stdio.h>",
        "#include <stdlib.h>",
        "#include <string.h>",
        "",
        "int main(void) {",
        f"  int n = {n};",
        "  int *items = malloc(n * sizeof(int));",
        "  if (items == NULL) return 1;",
        f"  int source[] = {{{_ints(values)}}};",
        "  memcpy(items, source, n * sizeof(int));",
        "",
        "  /* realloc may move the block, so the answer replaces the old",
        "     pointer. Assigning it to a different variable and keeping",
        "     the old one is the classic way to end up with a dangling",
        "     pointer that still looks fine. */",
        f"  int grown = n + {extra};",
        "  items = realloc(items, grown * sizeof(int));",
        "  if (items == NULL) return 1;",
        "  for (int i = n; i < grown; i++) items[i] = 0;",
        "  for (int i = 0; i < grown; i++) {",
        '    if (i > 0) printf(" ");',
        '    printf("%d", items[i]);',
        "  }",
        '  printf("\\n");',
        "",
        "  printf(\"%d\\n\", memcmp(items, source, n * sizeof(int)) == 0);",
        f'  printf("%d\\n", atoi("{text}"));',
        "  free(items);",
        "  return 0;",
        "}",
    )


# ── C++ ──────────────────────────────────────────────────────


def _cpp_more(a: dict) -> str:
    values, at, value = a["values"], a["at"], a["value"]
    head, tail = a["head"], a["tail"]
    return _lines(
        "#include <iostream>",
        "#include <vector>",
        "#include <string>",
        "using namespace std;",
        "",
        "int main() {",
        f"  vector<int> items = {{{_ints(values)}}};",
        f"  items.insert(items.begin() + {at}, {value});",
        "  for (size_t i = 0; i < items.size(); i++) {",
        '    if (i > 0) cout << " ";',
        "    cout << items[i];",
        "  }",
        '  cout << "\\n";',
        f'  string word = "{head}";',
        f'  word.append("{tail}");',
        '  cout << word << "\\n";',
        f'  cout << (word.compare("{head}{tail}") == 0 ? 1 : 0) << "\\n";',
        "  items.clear();",
        '  cout << items.size() << "\\n";',
        "  return 0;",
        "}",
    )


# ── Rust ─────────────────────────────────────────────────────


def _rust_more(a: dict) -> str:
    values, at, take = a["values"], a["at"], a["take"]
    return _lines(
        "fn main() {",
        f"    let items = vec![{_ints(values)}];",
        "    // into_iter hands over the values themselves and consumes the",
        "    // vector, so this one is cloned first. iter would borrow and",
        "    // leave items usable, which is why it is the usual choice.",
        "    let doubled: Vec<i32> = items.clone()",
        "        .into_iter()",
        "        .map(|n| n * 2)",
        "        .collect();",
        "    let shown: Vec<String> = doubled.iter()",
        "        .map(|n| n.to_string())",
        "        .collect();",
        '    println!("{}", shown.join(" "));',
        f"    println!(\"{{}}\", items.get({at}).is_none());",
        f"    println!(\"{{}}\", items.iter().take({take}).sum::<i32>());",
        '    println!("{}", items.len());',
        "}",
    )


# ── Dart ─────────────────────────────────────────────────────


def _dart_more(a: dict) -> str:
    pairs, key, take = a["pairs"], a["key"], a["take"]
    sets = [f"  ages['{k}'] = {v};" for k, v in pairs]
    return _lines(
        "void main() {",
        "  final ages = <String, int>{};",
        *sets,
        "  // The lookup is int? and this one is known to be there, so ! is",
        "  // the way to say so. It is a promise, not a check: wrong, and it",
        "  // throws at exactly the point you claimed it could not.",
        f"  print(ages['{key}']!);",
        f"  final items = List<int>.from({[v for _, v in pairs]});",
        f"  print(items.take({take}).join(' '));",
        "  print(items.length);",
        "}",
    )


_BUILDERS = {
    "c_more": _c_more,
    "cpp_more": _cpp_more,
    "rust_more": _rust_more,
    "dart_more": _dart_more,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if _OWNER.get(shape) != language:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python from the arguments."""
    a = args
    if shape == "c_more":
        values, extra, text = list(a["values"]), a["extra"], a["text"]
        if extra < 1:
            raise ValueError("realloc must actually grow the block")
        if not values:
            raise ValueError("there must be something to copy and compare")
        if not text.lstrip("-").isdigit():
            raise ValueError("atoi is given something it can read")
        grown = values + [0] * extra
        return NL.join([
            " ".join(str(n) for n in grown), "1", str(int(text)),
        ])
    if shape == "cpp_more":
        values, at, val = list(a["values"]), a["at"], a["value"]
        if not 0 <= at <= len(values):
            raise ValueError("the insert position must be inside the vector")
        if at in (0, len(values)):
            raise ValueError(
                "inserting at an end is push_front or push_back, and insert "
                "is worth a page only where it goes in the middle"
            )
        after = values[:at] + [val] + values[at:]
        head, tail = a["head"], a["tail"]
        if not head or not tail:
            raise ValueError("both halves of the string must be there")
        return NL.join([
            " ".join(str(n) for n in after), head + tail, "1", "0",
        ])
    if shape == "rust_more":
        values, at, take = list(a["values"]), a["at"], a["take"]
        if at < len(values):
            raise ValueError(
                "the index must be past the end, or get returns Some and "
                "is_none is false on every row of the page"
            )
        if not 0 < take < len(values):
            raise ValueError("take must leave something behind")
        return NL.join([
            " ".join(str(n * 2) for n in values),
            "true",
            str(sum(values[:take])),
            str(len(values)),
        ])
    if shape == "dart_more":
        pairs = [tuple(p) for p in a["pairs"]]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the writes")
        key, take = a["key"], a["take"]
        if key not in table:
            raise ValueError(
                "the asserted key must be present, or ! throws and the page "
                "teaches the failure rather than the operator"
            )
        values = [v for _, v in pairs]
        if not 0 < take < len(values):
            raise ValueError("take must leave something behind")
        return NL.join([
            str(table[key]),
            " ".join(str(v) for v in values[:take]),
            str(len(values)),
        ])
    raise KeyError(shape)
