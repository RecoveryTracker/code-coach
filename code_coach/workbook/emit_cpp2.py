"""C++: the standard library the pages stopped short of.

The audit found the C++ pages had taught vector, push_back and size, and
then stopped. Across sixteen hundred C++ answers the workbook had never
written unordered_map, never called std::sort, never used begin or end,
never touched stack or queue, and never called empty — which the solutions
use thirty-five times.

That is a particular kind of half-covered: the container was taught and
the library that makes containers worth having was not. Every C++ solution
in the bank is built out of the parts that were missing.

Ten pages: the vector calls in full, the two hash containers, sort with a
lambda, iterators, the adapters, the algorithms, strings, and then the node
structs, which in C++ carry the same new-and-delete duty they had in C.

C++ only. Nothing prints a container directly; each is walked and joined,
because there is no built-in rendering to rely on.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("cpp",)

SHAPES: tuple[Shape, ...] = (
    Shape("cpp_vector", "the calls a vector answers to"),
    Shape("cpp_map", "an unordered map, and the key that is not there"),
    Shape("cpp_set", "membership without repeats"),
    Shape("cpp_sort", "sorting a range with a lambda"),
    Shape("cpp_iterators", "begin, end, and what sits between them"),
    Shape("cpp_adapters", "a stack and a queue, made of something else"),
    Shape("cpp_algorithms", "the header that does the work for you"),
    Shape("cpp_string", "the string calls worth knowing"),
    Shape("cpp_node", "a struct, a pointer, and the arrow"),
    Shape("cpp_tree", "two pointers per node"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


def _quoted(items) -> str:
    return ", ".join(f'"{s}"' for s in items)


_HEAD = (
    "#include <iostream>",
    "#include <vector>",
    "#include <string>",
    "#include <unordered_map>",
    "#include <unordered_set>",
    "#include <algorithm>",
    "#include <numeric>",
    "#include <stack>",
    "#include <queue>",
    "using namespace std;",
    "",
)

_JOIN_INTS = (
    "void show(const vector<int>& items) {",
    "  for (size_t i = 0; i < items.size(); i++) {",
    '    if (i > 0) cout << " ";',
    "    cout << items[i];",
    "  }",
    '  cout << "\\n";',
    "}",
    "",
)


def _prog(*body: str) -> str:
    return _lines(*_HEAD, "int main() {", *body, "  return 0;", "}")


def _prog_show(*body: str) -> str:
    return _lines(*_HEAD, *_JOIN_INTS, "int main() {", *body,
                  "  return 0;", "}")


# ── 81. vector ───────────────────────────────────────────────


def _vector(a: dict) -> str:
    return _prog_show(
        f"  vector<int> items = {{{_ints(a['values'])}}};",
        '  cout << (items.empty() ? "yes" : "no") << "\\n";',
        f"  items.push_back({a['pushed']});",
        '  cout << items.front() << "\\n";',
        '  cout << items.back() << "\\n";',
        "  items.pop_back();",
        "  show(items);",
        '  cout << items.size() << "\\n";',
    )


# ── 82. unordered_map ────────────────────────────────────────


def _map(a: dict) -> str:
    pairs, look = a["pairs"], a["look"]
    sets = [f'  seen["{k}"] = {v};' for k, v in pairs]
    return _prog(
        "  unordered_map<string, int> seen;",
        *sets,
        f'  if (seen.count("{look}")) cout << seen["{look}"] << "\\n";',
        '  else cout << "missing" << "\\n";',
        f'  cout << seen.count("{look}") << "\\n";',
        '  cout << seen.size() << "\\n";',
        "  vector<string> keys;",
        "  for (const auto& entry : seen) keys.push_back(entry.first);",
        "  sort(keys.begin(), keys.end());",
        "  for (size_t i = 0; i < keys.size(); i++) {",
        '    if (i > 0) cout << " ";',
        "    cout << keys[i];",
        "  }",
        '  cout << "\\n";',
    )


# ── 83. unordered_set ────────────────────────────────────────


def _set(a: dict) -> str:
    return _prog_show(
        f"  vector<int> items = {{{_ints(a['values'])}}};",
        "  unordered_set<int> seen(items.begin(), items.end());",
        f"  seen.erase({a['dropped']});",
        "  vector<int> kept(seen.begin(), seen.end());",
        "  sort(kept.begin(), kept.end());",
        "  show(kept);",
        '  cout << seen.size() << "\\n";',
        f'  cout << seen.count({a["probe"]}) << "\\n";',
    )


# ── 84. sort ─────────────────────────────────────────────────


def _sort(a: dict) -> str:
    if a["want"] == "numbers":
        return _prog_show(
            f"  vector<int> items = {{{_ints(a['values'])}}};",
            "  sort(items.begin(), items.end());",
            "  show(items);",
            "  sort(items.begin(), items.end(),",
            "       [](int x, int y) { return x > y; });",
            "  show(items);",
        )
    return _prog(
        f"  vector<string> words = {{{_quoted(a['words'])}}};",
        "  sort(words.begin(), words.end(),",
        "       [](const string& x, const string& y) {",
        "         if (x.size() != y.size()) return x.size() < y.size();",
        "         return x < y;",
        "       });",
        "  for (size_t i = 0; i < words.size(); i++) {",
        '    if (i > 0) cout << " ";',
        "    cout << words[i];",
        "  }",
        '  cout << "\\n";',
    )


# ── 85. Iterators ────────────────────────────────────────────


def _iterators(a: dict) -> str:
    return _prog(
        f"  vector<int> items = {{{_ints(a['values'])}}};",
        "  int total = 0;",
        "  for (auto it = items.begin(); it != items.end(); ++it) {",
        "    total += *it;",
        "  }",
        '  cout << total << "\\n";',
        f"  auto found = find(items.begin(), items.end(), {a['target']});",
        '  cout << (found == items.end() ? -1 : (int)(found - items.begin()))',
        '       << "\\n";',
        '  cout << *items.begin() << "\\n";',
        '  cout << *(items.end() - 1) << "\\n";',
    )


# ── 86. stack and queue ──────────────────────────────────────


def _adapters(a: dict) -> str:
    return _prog(
        f"  vector<int> items = {{{_ints(a['values'])}}};",
        "  stack<int> pile;",
        "  for (int n : items) pile.push(n);",
        "  string out;",
        "  while (!pile.empty()) {",
        '    if (!out.empty()) out += " ";',
        "    out += to_string(pile.top());",
        "    pile.pop();",
        "  }",
        '  cout << out << "\\n";',
        "  queue<int> line;",
        "  for (int n : items) line.push(n);",
        "  string order;",
        "  while (!line.empty()) {",
        '    if (!order.empty()) order += " ";',
        "    order += to_string(line.front());",
        "    line.pop();",
        "  }",
        '  cout << order << "\\n";',
    )


# ── 87. Algorithms ───────────────────────────────────────────


def _algorithms(a: dict) -> str:
    return _prog_show(
        f"  vector<int> items = {{{_ints(a['values'])}}};",
        '  cout << *max_element(items.begin(), items.end()) << "\\n";',
        '  cout << *min_element(items.begin(), items.end()) << "\\n";',
        '  cout << accumulate(items.begin(), items.end(), 0) << "\\n";',
        "  reverse(items.begin(), items.end());",
        "  show(items);",
    )


# ── 88. Strings ──────────────────────────────────────────────


def _string(a: dict) -> str:
    return _prog(
        f'  string text = "{a["text"]}";',
        f'  cout << text.substr(0, {a["cut"]}) << "\\n";',
        '  cout << text.size() << "\\n";',
        f'  size_t at = text.find("{a["needle"]}");',
        '  cout << (at == string::npos ? -1 : (int)at) << "\\n";',
        "  string built;",
        f"  for (int i = 0; i < {a['times']}; i++) built += \"{a['unit']}\";",
        '  cout << built << "\\n";',
    )


# ── 89-90. Node structs ──────────────────────────────────────


def _node(a: dict) -> str:
    return _lines(
        *_HEAD,
        "struct ListNode {",
        "  int val;",
        "  ListNode* next;",
        "  ListNode(int v) : val(v), next(nullptr) {}",
        "};",
        "",
        "int main() {",
        f"  vector<int> values = {{{_ints(a['values'])}}};",
        "  ListNode* head = nullptr;",
        "  ListNode* tail = nullptr;",
        "  for (int v : values) {",
        "    ListNode* node = new ListNode(v);",
        "    if (head == nullptr) head = node;",
        "    else tail->next = node;",
        "    tail = node;",
        "  }",
        "  string out;",
        "  for (ListNode* n = head; n != nullptr; n = n->next) {",
        '    if (!out.empty()) out += " -> ";',
        "    out += to_string(n->val);",
        "  }",
        '  cout << out << "\\n";',
        "  int total = 0;",
        "  for (ListNode* n = head; n != nullptr; n = n->next) total += n->val;",
        '  cout << total << "\\n";',
        "  while (head != nullptr) {",
        "    ListNode* next = head->next;",
        "    delete head;",
        "    head = next;",
        "  }",
        "  return 0;",
        "}",
    )


def _tree(a: dict) -> str:
    values = a["values"]
    lines = [f"  TreeNode* n{i} = new TreeNode({v});"
             for i, v in enumerate(values)]
    for i in range(len(values)):
        left, right = 2 * i + 1, 2 * i + 2
        if left < len(values):
            lines.append(f"  n{i}->left = n{left};")
        if right < len(values):
            lines.append(f"  n{i}->right = n{right};")
    return _lines(
        *_HEAD,
        "struct TreeNode {",
        "  int val;",
        "  TreeNode* left;",
        "  TreeNode* right;",
        "  TreeNode(int v) : val(v), left(nullptr), right(nullptr) {}",
        "};",
        "",
        "int depth(TreeNode* node) {",
        "  if (node == nullptr) return 0;",
        "  return 1 + max(depth(node->left), depth(node->right));",
        "}",
        "",
        "int total(TreeNode* node) {",
        "  if (node == nullptr) return 0;",
        "  return node->val + total(node->left) + total(node->right);",
        "}",
        "",
        "void freeTree(TreeNode* node) {",
        "  if (node == nullptr) return;",
        "  freeTree(node->left);",
        "  freeTree(node->right);",
        "  delete node;",
        "}",
        "",
        "int main() {",
        *lines,
        '  cout << n0->val << "\\n";',
        '  cout << depth(n0) << "\\n";',
        '  cout << total(n0) << "\\n";',
        "  freeTree(n0);",
        "  return 0;",
        "}",
    )


_BUILDERS = {
    "cpp_vector": _vector,
    "cpp_map": _map,
    "cpp_set": _set,
    "cpp_sort": _sort,
    "cpp_iterators": _iterators,
    "cpp_adapters": _adapters,
    "cpp_algorithms": _algorithms,
    "cpp_string": _string,
    "cpp_node": _node,
    "cpp_tree": _tree,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, from the data rather than the C++."""
    a = args
    if shape == "cpp_vector":
        values, pushed = list(a["values"]), a["pushed"]
        if not values:
            raise ValueError("an empty vector has no front or back")
        after = values + [pushed]
        return NL.join([
            "no", str(after[0]), str(after[-1]),
            " ".join(str(n) for n in after[:-1]), str(len(after) - 1),
        ])
    if shape == "cpp_map":
        pairs = [tuple(p) for p in a["pairs"]]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the writes")
        if len(table) < 2:
            raise ValueError("one entry does not need a map")
        look = a["look"]
        found = table.get(look)
        return NL.join([
            "missing" if found is None else str(found),
            "1" if look in table else "0",
            str(len(table)), " ".join(sorted(table)),
        ])
    if shape == "cpp_set":
        values, dropped, probe = list(a["values"]), a["dropped"], a["probe"]
        if len(set(values)) == len(values):
            raise ValueError("the input must repeat something")
        if dropped not in set(values):
            raise ValueError("the erased value must have been there")
        kept = sorted(set(values) - {dropped})
        return NL.join([
            " ".join(str(n) for n in kept), str(len(kept)),
            "1" if probe in kept else "0",
        ])
    if shape == "cpp_sort":
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
    if shape == "cpp_iterators":
        values, target = list(a["values"]), a["target"]
        if len(values) < 2:
            raise ValueError("begin and end are the same on one element")
        at = values.index(target) if target in values else -1
        return NL.join([
            str(sum(values)), str(at), str(values[0]), str(values[-1]),
        ])
    if shape == "cpp_adapters":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("one element leaves the two orders identical")
        if values == values[::-1]:
            raise ValueError(
                "the values must not read the same backwards, or the stack "
                "and the queue print the same line and the page shows "
                "nothing about the difference"
            )
        return NL.join([
            " ".join(str(n) for n in reversed(values)),
            " ".join(str(n) for n in values),
        ])
    if shape == "cpp_algorithms":
        values = list(a["values"])
        if not values:
            raise ValueError("max_element of nothing is the end iterator")
        if values == values[::-1]:
            raise ValueError("reversing must visibly change the order")
        return NL.join([
            str(max(values)), str(min(values)), str(sum(values)),
            " ".join(str(n) for n in reversed(values)),
        ])
    if shape == "cpp_string":
        text, cut, needle = a["text"], a["cut"], a["needle"]
        unit, times = a["unit"], a["times"]
        if not 0 < cut < len(text):
            raise ValueError("the substring must take part of the text")
        if times < 2:
            raise ValueError("building once is not building")
        at = text.find(needle)
        return NL.join([
            text[:cut], str(len(text)), str(at), unit * times,
        ])
    if shape == "cpp_node":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("a chain needs more than one node")
        return NL.join([
            " -> ".join(str(v) for v in values), str(sum(values)),
        ])
    if shape == "cpp_tree":
        values = list(a["values"])
        if len(values) < 4:
            raise ValueError("a tree this small has nothing to recurse into")
        depth = 0
        while (1 << depth) - 1 < len(values):
            depth += 1
        return NL.join([str(values[0]), str(depth), str(sum(values))])
    raise KeyError(shape)
