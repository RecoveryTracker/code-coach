"""A fifth batch: splitting text, joining it, and looking things up by key.

These are the first shapes that cannot be written in C. Not because C is
awkward — the earlier batches lean on C being awkward on purpose, and a fixed
array with a count beside it teaches something real — but because there is no
honest C answer to "split this sentence on spaces" that is one exercise
rather than a lesson in memory management. Same for a map: writing one is a
week's work and a fine thing to do, and it is not this page.

So these pages name six languages and leave C out, which is what
`Page.languages` is for.

C++ and Rust are in. Splitting a string in C++ is a stringstream and a
getline loop, and that IS what splitting a string in C++ involves — the same
argument that put C in the earlier batches keeps C++ in this one.

The determinism rule needs one extra care here: a map is never iterated.
Rust's HashMap has a deliberately unpredictable order and the others differ
from each other, so every exercise looks up keys it names rather than walking
the map. Print what you asked for, not what the container felt like giving.
"""

from __future__ import annotations

from typing import Callable

from code_coach.workbook.emit import NL, Shape, _lines, _q

# Everything but C.
LANGUAGES: tuple[str, ...] = (
    "python",
    "javascript",
    "typescript",
    "dart",
    "cpp",
    "rust",
)

SHAPES: tuple[Shape, ...] = (
    Shape("split_words", "cutting a sentence into its words"),
    Shape("count_words", "how many pieces a sentence came apart into"),
    Shape("join_list", "putting a list back together as one line"),
    Shape("map_lookup", "a value found by its key"),
    Shape("map_build", "filling a map in a loop, then asking it"),
    Shape("str_contains", "whether one piece of text is inside another"),
    Shape("str_slice", "taking a run of characters out of the middle"),
    Shape("str_find", "where a piece of text starts"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _pairs_py(pairs) -> str:
    return "{" + ", ".join(f'"{k}": {v}' for k, v in pairs) + "}"


# ── Python ───────────────────────────────────────────────────

def _python(shape: str, a: dict) -> str:
    if shape == "split_words":
        return _lines(
            f"words = {_q(a['sentence'])}.split(\" \")",
            "for w in words:",
            "    print(w)",
        )
    if shape == "count_words":
        return _lines(
            f"words = {_q(a['sentence'])}.split(\" \")",
            "print(len(words))",
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"words = [{items}]",
            f'print({_q(a["sep"])}.join(words))',
        )
    if shape == "map_lookup":
        looks = [f'print(ages[{_q(k)}])' for k in a["keys"]]
        return _lines(f"ages = {_pairs_py(a['pairs'])}", *looks)
    if shape == "map_build":
        looks = [f"print(squares[{k}])" for k in a["keys"]]
        return _lines(
            "squares = {}",
            f"for i in range(1, {a['upto']} + 1):",
            f"    squares[i] = {a['expr']}",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"if {_q(a['piece'])} in {_q(a['word'])}:",
            f"    print({_q(a['yes'])})",
            "else:",
            f"    print({_q(a['no'])})",
        )
    if shape == "str_slice":
        return f"print({_q(a['word'])}[{a['start']}:{a['end']}])"
    if shape == "str_find":
        return f"print({_q(a['word'])}.find({_q(a['piece'])}))"
    raise KeyError(shape)


# ── JavaScript ───────────────────────────────────────────────

def _js(shape: str, a: dict) -> str:
    if shape == "split_words":
        return _lines(
            f'const words = {_q(a["sentence"])}.split(" ");',
            "for (const w of words) {",
            "  console.log(w);",
            "}",
        )
    if shape == "count_words":
        return _lines(
            f'const words = {_q(a["sentence"])}.split(" ");',
            "console.log(words.length);",
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"const words = [{items}];",
            f'console.log(words.join({_q(a["sep"])}));',
        )
    if shape == "map_lookup":
        pairs = ", ".join(f'{_q(k)}: {v}' for k, v in a["pairs"])
        looks = [f"console.log(ages[{_q(k)}]);" for k in a["keys"]]
        return _lines(f"const ages = {{{pairs}}};", *looks)
    if shape == "map_build":
        looks = [f"console.log(squares[{k}]);" for k in a["keys"]]
        return _lines(
            "const squares = {};",
            f"for (let i = 1; i <= {a['upto']}; i++) {{",
            f"  squares[i] = {a['expr']};",
            "}",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"if ({_q(a['word'])}.includes({_q(a['piece'])})) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "str_slice":
        return f"console.log({_q(a['word'])}.slice({a['start']}, {a['end']}));"
    if shape == "str_find":
        return f"console.log({_q(a['word'])}.indexOf({_q(a['piece'])}));"
    raise KeyError(shape)


# ── TypeScript ───────────────────────────────────────────────

def _ts(shape: str, a: dict) -> str:
    if shape == "split_words":
        return _lines(
            f'const words: string[] = {_q(a["sentence"])}.split(" ");',
            "for (const w of words) {",
            "  console.log(w);",
            "}",
        )
    if shape == "count_words":
        return _lines(
            f'const words: string[] = {_q(a["sentence"])}.split(" ");',
            "console.log(words.length);",
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"const words: string[] = [{items}];",
            f'console.log(words.join({_q(a["sep"])}));',
        )
    if shape == "map_lookup":
        pairs = ", ".join(f'{_q(k)}: {v}' for k, v in a["pairs"])
        looks = [f"console.log(ages[{_q(k)}]);" for k in a["keys"]]
        return _lines(
            f"const ages: Record<string, number> = {{{pairs}}};", *looks
        )
    if shape == "map_build":
        looks = [f"console.log(squares[{k}]);" for k in a["keys"]]
        return _lines(
            "const squares: Record<number, number> = {};",
            f"for (let i = 1; i <= {a['upto']}; i++) {{",
            f"  squares[i] = {a['expr']};",
            "}",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"if ({_q(a['word'])}.includes({_q(a['piece'])})) {{",
            f"  console.log({_q(a['yes'])});",
            "} else {",
            f"  console.log({_q(a['no'])});",
            "}",
        )
    if shape == "str_slice":
        return f"console.log({_q(a['word'])}.slice({a['start']}, {a['end']}));"
    if shape == "str_find":
        return f"console.log({_q(a['word'])}.indexOf({_q(a['piece'])}));"
    raise KeyError(shape)


# ── Dart ─────────────────────────────────────────────────────

def _dart_body(shape: str, a: dict) -> str:
    if shape == "split_words":
        return _lines(
            f'var words = {_q(a["sentence"])}.split(" ");',
            "  for (var w in words) {",
            "    print(w);",
            "  }",
        )
    if shape == "count_words":
        return _lines(
            f'var words = {_q(a["sentence"])}.split(" ");',
            "  print(words.length);",
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"var words = [{items}];",
            f'  print(words.join({_q(a["sep"])}));',
        )
    if shape == "map_lookup":
        pairs = ", ".join(f"{_q(k)}: {v}" for k, v in a["pairs"])
        looks = [f"  print(ages[{_q(k)}]);" for k in a["keys"]]
        return _lines(f"var ages = {{{pairs}}};", *looks)
    if shape == "map_build":
        looks = [f"  print(squares[{k}]);" for k in a["keys"]]
        return _lines(
            "var squares = {};",
            f"  for (var i = 1; i <= {a['upto']}; i++) {{",
            f"    squares[i] = {a['expr']};",
            "  }",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"if ({_q(a['word'])}.contains({_q(a['piece'])})) {{",
            f"    print({_q(a['yes'])});",
            "  } else {",
            f"    print({_q(a['no'])});",
            "  }",
        )
    if shape == "str_slice":
        return f"print({_q(a['word'])}.substring({a['start']}, {a['end']}));"
    if shape == "str_find":
        return f"print({_q(a['word'])}.indexOf({_q(a['piece'])}));"
    raise KeyError(shape)


def _dart(shape: str, a: dict) -> str:
    return "void main() {" + NL + "  " + _dart_body(shape, a) + NL + "}"


# ── C++ ──────────────────────────────────────────────────────

_CPP_HEAD = _lines(
    "#include <iostream>",
    "#include <map>",
    "#include <sstream>",
    "#include <string>",
    "#include <vector>",
    "",
)


def _cpp_body(shape: str, a: dict) -> str:
    if shape in ("split_words", "count_words"):
        # A stringstream and a getline loop. This is the whole reason C++ is
        # on these pages and C is not: it is long, and it is honest.
        head = _lines(
            f"std::string line = {_q(a['sentence'])};",
            "  std::stringstream stream(line);",
            "  std::vector<std::string> words;",
            "  std::string w;",
            "  while (std::getline(stream, w, ' ')) {",
            "    words.push_back(w);",
            "  }",
        )
        if shape == "count_words":
            return head + NL + '  std::cout << words.size() << "\\n";'
        return _lines(
            head,
            "  for (const std::string &word : words) {",
            '    std::cout << word << "\\n";',
            "  }",
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"std::vector<std::string> words = {{{items}}};",
            "  std::string line;",
            "  for (size_t k = 0; k < words.size(); k++) {",
            f"    if (k > 0) line += {_q(a['sep'])};",
            "    line += words[k];",
            "  }",
            '  std::cout << line << "\\n";',
        )
    if shape == "map_lookup":
        pairs = ", ".join("{" + _q(k) + ", " + str(v) + "}" for k, v in a["pairs"])
        looks = [
            f'  std::cout << ages[{_q(k)}] << "\\n";' for k in a["keys"]
        ]
        return _lines(
            f"std::map<std::string, int> ages = {{{pairs}}};", *looks
        )
    if shape == "map_build":
        looks = [f'  std::cout << squares[{k}] << "\\n";' for k in a["keys"]]
        return _lines(
            "std::map<int, int> squares;",
            f"  for (int i = 1; i <= {a['upto']}; i++) {{",
            f"    squares[i] = {a['expr']};",
            "  }",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"std::string w = {_q(a['word'])};",
            f"  if (w.find({_q(a['piece'])}) != std::string::npos) {{",
            f'    std::cout << {_q(a["yes"])} << "\\n";',
            "  } else {",
            f'    std::cout << {_q(a["no"])} << "\\n";',
            "  }",
        )
    if shape == "str_slice":
        length = a["end"] - a["start"]
        return _lines(
            f"std::string w = {_q(a['word'])};",
            f'  std::cout << w.substr({a["start"]}, {length}) << "\\n";',
        )
    if shape == "str_find":
        return _lines(
            f"std::string w = {_q(a['word'])};",
            f'  std::cout << (int)w.find({_q(a["piece"])}) << "\\n";',
        )
    raise KeyError(shape)


def _cpp(shape: str, a: dict) -> str:
    return _lines(
        _CPP_HEAD, "int main() {", "  " + _cpp_body(shape, a), "  return 0;", "}"
    )


# ── Rust ─────────────────────────────────────────────────────

def _rust_body(shape: str, a: dict) -> str:
    if shape == "split_words":
        return _lines(
            f"let words: Vec<&str> = {_q(a['sentence'])}.split(' ').collect();",
            "    for w in words {",
            '        println!("{}", w);',
            "    }",
        )
    if shape == "count_words":
        return _lines(
            f"let words: Vec<&str> = {_q(a['sentence'])}.split(' ').collect();",
            '    println!("{}", words.len());',
        )
    if shape == "join_list":
        items = ", ".join(_q(w) for w in a["words"])
        return _lines(
            f"let words = vec![{items}];",
            f'    println!("{{}}", words.join({_q(a["sep"])}));',
        )
    if shape == "map_lookup":
        inserts = [
            f"    ages.insert({_q(k)}, {v});" for k, v in a["pairs"]
        ]
        looks = [f'    println!("{{}}", ages[{_q(k)}]);' for k in a["keys"]]
        return _lines(
            "let mut ages = HashMap::new();", *inserts, *looks
        )
    if shape == "map_build":
        looks = [f'    println!("{{}}", squares[&{k}]);' for k in a["keys"]]
        return _lines(
            "let mut squares = HashMap::new();",
            f"    for i in 1..={a['upto']} {{",
            f"        squares.insert(i, {a['expr']});",
            "    }",
            *looks,
        )
    if shape == "str_contains":
        return _lines(
            f"if {_q(a['word'])}.contains({_q(a['piece'])}) {{",
            f'        println!("{{}}", {_q(a["yes"])});',
            "    } else {",
            f'        println!("{{}}", {_q(a["no"])});',
            "    }",
        )
    if shape == "str_slice":
        return (
            'println!("{}", &'
            + _q(a["word"])
            + f"[{a['start']}..{a['end']}]);"
        )
    if shape == "str_find":
        return (
            'println!("{}", '
            + _q(a["word"])
            + f".find({_q(a['piece'])}).unwrap());"
        )
    raise KeyError(shape)


def _rust(shape: str, a: dict) -> str:
    head = ""
    if shape in ("map_lookup", "map_build"):
        head = "use std::collections::HashMap;" + NL + NL
    return head + "fn main() {" + NL + "    " + _rust_body(shape, a) + NL + "}"


_EMITTERS: dict[str, Callable[[str, dict], str]] = {
    "python": _python,
    "javascript": _js,
    "typescript": _ts,
    "dart": _dart,
    "cpp": _cpp,
    "rust": _rust,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    emit = _EMITTERS.get(language)
    if emit is None:
        return None
    return emit(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "split_words":
        lines = a["sentence"].split(" ")
    elif shape == "count_words":
        lines = [str(len(a["sentence"].split(" ")))]
    elif shape == "join_list":
        lines = [a["sep"].join(a["words"])]
    elif shape == "map_lookup":
        table = dict(a["pairs"])
        lines = [str(table[k]) for k in a["keys"]]
    elif shape == "map_build":
        table = {i: value(a["expr"], {"i": i}) for i in range(1, a["upto"] + 1)}
        lines = [str(table[k]) for k in a["keys"]]
    elif shape == "str_contains":
        lines = [a["yes"] if a["piece"] in a["word"] else a["no"]]
    elif shape == "str_slice":
        lines = [a["word"][a["start"] : a["end"]]]
    elif shape == "str_find":
        lines = [str(a["word"].find(a["piece"]))]
    else:
        raise KeyError(shape)
    return NL.join(lines)
