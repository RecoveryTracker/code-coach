"""Node objects in JavaScript and TypeScript.

The gap these close was found in Python, fixed there, then fixed in C, C++,
Rust and Dart. It was never applied to the two web languages. A re-measure
after all of that found `new ListNode` still missing from both, which is
the same omission repeated five times and then not noticed in the two
languages most people reach for.

Two pages each, deliberately the same two: build a chain and walk it, then
reverse it and merge two of them onto a dummy head. The JavaScript and the
TypeScript print identical output and are compared against one expectation,
so if they ever stopped agreeing something would say so.

The interesting difference is the annotation. Under strict, `next` is
`ListNode | null`, so the walk cannot reach `cur.next` until the loop
condition has proved `cur` is not null, and every pointer variable has to
say it might be null before it can be one. The JavaScript is the same
program with those proofs deleted. Doing both is the clearest available
statement of what the types are actually buying.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page


def _page(page_id, number, name, teaches, example, shape, rows,
          language) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=(language,),
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


_CHAIN_ROWS = (
    ((3, 1, 4), "sum"), ((2, 7, 1, 8), "count"), ((1, 9, 3), "max"),
    ((5, 2, 8), "sum"), ((6, 6, 2, 7), "count"), ((2, 5, 9), "max"),
    ((4, 1, 7), "sum"), ((9, 1, 8, 2), "count"), ((3, 8, 5), "max"),
    ((7, 3, 6), "sum"), ((1, 2, 3, 4), "count"), ((2, 9, 4), "max"),
    ((5, 1, 3), "sum"), ((8, 2, 6, 1), "count"), ((1, 4, 9), "max"),
    ((6, 2, 8), "sum"), ((3, 6, 1, 5), "count"), ((4, 7, 2), "max"),
    ((9, 4, 7), "sum"), ((2, 2, 6, 3), "count"),
)

_WORDS = {
    "sum": "add every value up",
    "count": "count the nodes",
    "max": "find the largest value",
}

_REVERSES = (
    (1, 2, 3), (3, 1, 4), (5, 2, 9), (2, 8, 5, 1), (9, 4, 6),
    (1, 2, 3, 4), (6, 1, 8), (4, 9, 2), (8, 3, 7), (2, 7, 1, 8),
)

_MERGES = (
    ((1, 4, 7), (2, 3, 9)), ((1, 3, 5), (2, 4, 6)), ((2, 6), (1, 5, 8)),
    ((1, 2, 9), (3, 4, 5)), ((4, 8), (1, 6, 9)), ((3, 7), (2, 5, 8)),
    ((1, 5), (2, 3, 4)), ((2, 4, 9), (1, 6, 7)), ((5, 6), (1, 3, 8)),
    ((1, 7), (4, 5, 9)),
)

_NODE_TEACHES = {
    "javascript": (
        "A node is an object holding a value and a reference to another "
        "one. The class is three lines and the defaults are what let a "
        "node be made already pointing at the rest of the chain, which is "
        "why building backwards through the array works in one pass."
    ),
    "typescript": (
        "The same three-line class with the types written down, and the "
        "types are the lesson. next is ListNode | null, so the walk cannot "
        "reach through node.next until the loop condition has proved node "
        "is not null — and the compiler tracks that proof, which is why "
        "the variable must be declared as the union rather than inferred "
        "from head."
    ),
}

_NODE_EXAMPLE = {
    "javascript": (
        "class ListNode { constructor(val = 0, next = null) { this.val = "
        "val; this.next = next; } } — the defaults do the work"
    ),
    "typescript": (
        "let node: ListNode | null = head; and then while (node !== null) "
        "— without the annotation the type is narrowed too early to "
        "reassign"
    ),
}

_OPS_TEACHES = {
    "javascript": (
        "Reversing is three references and no new nodes, so the memory "
        "does not move. Merging builds onto a dummy you throw away, which "
        "is what removes the is-the-list-empty check from every append and "
        "with it the place the bugs live."
    ),
    "typescript": (
        "The same two moves with the nulls accounted for. nxt has to be "
        "declared as ListNode | null because it holds cur.next before cur "
        "is repointed, and the merge tail is a plain ListNode because the "
        "dummy guarantees there is always one."
    ),
}

_OPS_EXAMPLE = {
    "javascript": (
        "const dummy = new ListNode(0); let tail = dummy; and at the end "
        "the answer is dummy.next, never dummy"
    ),
    "typescript": (
        "const nxt: ListNode | null = cur.next; — the annotation is what "
        "lets it hold null on the last node without the compiler objecting"
    ),
}


def _pages_for(language: str, first: int) -> tuple[Page, ...]:
    tag = "js" if language == "javascript" else "ts"
    return (
        _page(
            f"{tag}-list-node", first,
            "A class that points at another of itself",
            _NODE_TEACHES[language], _NODE_EXAMPLE[language],
            "web_list_node",
            tuple(
                (f"Build a chain of ListNode from [{_seq(v)}], walking the "
                 f"array backwards so each node is made already pointing at "
                 f"the rest. Print it with arrows, then {_WORDS[w]}.",
                 {"values": list(v), "want": w})
                for v, w in _CHAIN_ROWS
            ),
            language,
        ),
        _page(
            f"{tag}-list-ops", first + 1,
            "Reversing, and the dummy head",
            _OPS_TEACHES[language], _OPS_EXAMPLE[language],
            "web_list_ops",
            tuple(
                (f"Reverse a chain built from [{_seq(v)}] in place, then "
                 f"print it with arrows.",
                 {"values": list(v), "want": "reverse"})
                for v in _REVERSES
            ) + tuple(
                (f"Merge the sorted chains [{_seq(a)}] and [{_seq(b)}] onto "
                 f"a dummy head and print the result with arrows.",
                 {"left": list(a), "right": list(b), "want": "merge"})
                for a, b in _MERGES
            ),
            language,
        ),
    )


WEBNODE_PAGES: tuple[Page, ...] = (
    _pages_for("javascript", 166) + _pages_for("typescript", 151)
)
