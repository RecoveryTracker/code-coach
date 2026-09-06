"""Node objects for JavaScript and TypeScript.

The node-object gap was found in Python and fixed there, then in C, C++,
Rust and Dart. It was never applied to the two web languages, and a
re-measure after all that work found `new ListNode` still missing from
both. Five languages deep into the same omission and neither of the two
most-used ones had been done.

One emitter for both, because the algorithm is identical and only the types
differ. That is also the pedagogically interesting part: under strict,
TypeScript's `next` is `ListNode | null`, so the walk cannot touch
`cur.next` until the loop condition has proved `cur` is not null. The
JavaScript version is the same program with the proofs removed, and reading
them side by side is the clearest statement of what the types are buying.

Both print exactly the same characters, which is checked the same way
everything else here is.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript", "typescript")

SHAPES: tuple[Shape, ...] = (
    Shape("web_list_node", "a class that points at another of itself"),
    Shape("web_list_ops", "reversing, and the dummy head"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _class(ts: bool) -> tuple[str, ...]:
    if ts:
        return (
            "class ListNode {",
            "  val: number;",
            "  next: ListNode | null;",
            "  constructor(val: number = 0, next: ListNode | null = null) {",
            "    this.val = val;",
            "    this.next = next;",
            "  }",
            "}",
            "",
        )
    return (
        "class ListNode {",
        "  constructor(val = 0, next = null) {",
        "    this.val = val;",
        "    this.next = next;",
        "  }",
        "}",
        "",
    )


def _build(ts: bool, values) -> tuple[str, ...]:
    decl = "let head: ListNode | null = null;" if ts else "let head = null;"
    return (
        f"const values = {_nums(values)};",
        decl,
        "for (let i = values.length - 1; i >= 0; i--) {",
        "  head = new ListNode(values[i], head);",
        "}",
    )


def _show(ts: bool) -> tuple[str, ...]:
    """Walk and join. The annotation is the whole difference between the
    two languages, so it is on its own line in both."""
    cur = "let node: ListNode | null = head;" if ts else "let node = head;"
    return (
        "const out = [];",
        cur,
        "while (node !== null) {",
        "  out.push(String(node.val));",
        "  node = node.next;",
        "}",
    )


def _list_node(language: str, a: dict) -> str:
    ts = language == "typescript"
    want = a["want"]
    tail: tuple[str, ...]
    if want == "sum":
        tail = (
            "let total = 0;",
            "for (const n of out) total += Number(n);",
            "console.log(total);",
        )
    elif want == "count":
        tail = ("console.log(out.length);",)
    else:
        tail = (
            "let best = Number(out[0]);",
            "for (const n of out) best = Math.max(best, Number(n));",
            "console.log(best);",
        )
    return _lines(
        *_class(ts),
        *_build(ts, a["values"]),
        *_show(ts),
        'console.log(out.join(" -> "));',
        *tail,
    )


def _list_ops(language: str, a: dict) -> str:
    ts = language == "typescript"
    if a["want"] == "reverse":
        prev = "let prev: ListNode | null = null;" if ts else "let prev = null;"
        cur = "let cur: ListNode | null = head;" if ts else "let cur = head;"
        nxt = ("  const nxt: ListNode | null = cur.next;" if ts
               else "  const nxt = cur.next;")
        walk = ("let node: ListNode | null = prev;" if ts
                else "let node = prev;")
        return _lines(
            *_class(ts),
            *_build(ts, a["values"]),
            prev,
            cur,
            "while (cur !== null) {",
            nxt,
            "  cur.next = prev;",
            "  prev = cur;",
            "  cur = nxt;",
            "}",
            "const out = [];",
            walk,
            "while (node !== null) {",
            "  out.push(String(node.val));",
            "  node = node.next;",
            "}",
            'console.log(out.join(" -> "));',
        )
    left, right = a["left"], a["right"]
    decl_a = "let a: ListNode | null = left;" if ts else "let a = left;"
    decl_b = "let b: ListNode | null = right;" if ts else "let b = right;"
    tail_d = "let tail: ListNode = dummy;" if ts else "let tail = dummy;"
    walk = ("let node: ListNode | null = dummy.next;" if ts
            else "let node = dummy.next;")
    build_left = (
        f"const leftValues = {_nums(left)};",
        ("let left: ListNode | null = null;" if ts else "let left = null;"),
        "for (let i = leftValues.length - 1; i >= 0; i--) {",
        "  left = new ListNode(leftValues[i], left);",
        "}",
        f"const rightValues = {_nums(right)};",
        ("let right: ListNode | null = null;" if ts else "let right = null;"),
        "for (let i = rightValues.length - 1; i >= 0; i--) {",
        "  right = new ListNode(rightValues[i], right);",
        "}",
    )
    return _lines(
        *_class(ts),
        *build_left,
        "const dummy = new ListNode(0);",
        tail_d,
        decl_a,
        decl_b,
        "while (a !== null && b !== null) {",
        "  if (a.val <= b.val) {",
        "    tail.next = a;",
        "    a = a.next;",
        "  } else {",
        "    tail.next = b;",
        "    b = b.next;",
        "  }",
        "  tail = tail.next;",
        "}",
        "tail.next = a !== null ? a : b;",
        "const out = [];",
        walk,
        "while (node !== null) {",
        "  out.push(String(node.val));",
        "  node = node.next;",
        "}",
        'console.log(out.join(" -> "));',
    )


_BUILDERS = {
    "web_list_node": _list_node,
    "web_list_ops": _list_ops,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(language, args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """One expectation for both languages, which is the point.

    If the JavaScript and the TypeScript ever stopped agreeing, this is
    what would notice, because there is only one answer and both are
    compared against it.
    """
    a = args
    if shape == "web_list_node":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("a chain needs more than one node")
        want = a["want"]
        if want == "max" and values[0] == max(values):
            raise ValueError("the largest must not be the head")
        chain = " -> ".join(str(v) for v in values)
        got = {"sum": sum(values), "count": len(values),
               "max": max(values)}[want]
        return NL.join([chain, str(got)])
    if shape == "web_list_ops":
        if a["want"] == "reverse":
            values = list(a["values"])
            if values == values[::-1]:
                raise ValueError(
                    "the chain must not read the same backwards, or "
                    "reversing it proves nothing"
                )
            return " -> ".join(str(v) for v in reversed(values))
        left, right = list(a["left"]), list(a["right"])
        for side in (left, right):
            if side != sorted(side):
                raise ValueError("each chain must already be sorted")
        merged = sorted(left + right)
        if merged in (left + right, right + left):
            raise ValueError(
                "the two chains must interleave, or the merge is a join and "
                "the comparison never runs"
            )
        return " -> ".join(str(v) for v in merged)
    raise KeyError(shape)
