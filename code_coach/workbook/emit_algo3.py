"""The moves the interview patterns are made of, third batch: pointers you
rewire, and order you work out.

Linked lists are the one data structure where the move *is* the pointer
handling. There is no index to fall back on, so reversing a list, finding
its middle, and spotting a cycle are all the same skill: hold the right
number of references and let go in the right order.

Topological sort is the other half. Kahn's algorithm counts how many things
each item is waiting for, takes whatever is waiting for nothing, and repeats
- and the same code detects an impossible cycle for free, because if
anything is left over when the queue empties, it was waiting on itself.

Two more that earn their place: a monotonic stack, which turns "the next
bigger one" from a nested loop into a single pass, and merging intervals,
which is a sort followed by one comparison and comes up constantly.

Python only. The tie-breaking is deliberate throughout: the topological
queue is kept sorted so the answer is one specific order rather than any
valid one, or the page could not have an expected output at all.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("algo_list_walk", "a chain of nodes, and walking to the end"),
    Shape("algo_list_reverse", "turning every arrow round, one at a time"),
    Shape("algo_list_middle", "one pointer twice as fast as the other"),
    Shape("algo_list_cycle", "the two pointers that must meet if it loops"),
    Shape("algo_list_merge", "two sorted chains zipped into one"),
    Shape("algo_list_gap", "a fixed gap held while both pointers walk"),
    Shape("algo_topo_order", "doing things in an order that works"),
    Shape("algo_topo_cycle", "the leftovers that prove a cycle"),
    Shape("algo_monotonic", "a stack that only ever goes one way"),
    Shape("algo_merge_spans", "overlapping ranges folded together"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _pairs(items) -> str:
    """Numeric pairs, for the spans page."""
    return "[" + ", ".join(f"({a}, {b})" for a, b in items) + "]"


def _name_pairs(items) -> str:
    """Pairs of names, quoted. The spans version emits them bare, which
    for words is a NameError rather than a list of edges."""
    return "[" + ", ".join(f'("{a}", "{b}")' for a, b in items) + "]"


NODE_CLASS = (
    "class Node:",
    "    def __init__(self, value, nxt=None):",
    "        self.value = value",
    "        self.nxt = nxt",
    "",
)

BUILD_FROM = (
    "def build(values):",
    "    head = None",
    "    for value in reversed(values):",
    "        head = Node(value, head)",
    "    return head",
    "",
)


# ── 309. Walking a chain ─────────────────────────────────────


def _list_walk(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"head = build({_nums(a['items'])})",
        "",
        "values = []",
        "count = 0",
        "node = head",
        "while node is not None:",
        "    values.append(node.value)",
        "    count += 1",
        "    node = node.nxt",
        "",
        'print(", ".join(str(v) for v in values))',
        "print(count)",
        "print(values[-1])",
    )


# ── 310. Turning every arrow round ───────────────────────────


def _list_reverse(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"head = build({_nums(a['items'])})",
        "",
        "previous = None",
        "node = head",
        "while node is not None:",
        "    after = node.nxt",
        "    node.nxt = previous",
        "    previous = node",
        "    node = after",
        "",
        "values = []",
        "node = previous",
        "while node is not None:",
        "    values.append(node.value)",
        "    node = node.nxt",
        "",
        'print(", ".join(str(v) for v in values))',
        "print(previous.value)",
    )


# ── 311. Twice as fast ───────────────────────────────────────


def _list_middle(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"head = build({_nums(a['items'])})",
        "",
        "slow = head",
        "fast = head",
        "while fast is not None and fast.nxt is not None:",
        "    slow = slow.nxt",
        "    fast = fast.nxt.nxt",
        "",
        "print(slow.value)",
        f"print({len(a['items'])} // 2)",
    )


# ── 312. The two pointers that must meet ─────────────────────


def _list_cycle(a: dict) -> str:
    link = a["links_to"]
    tail_link = [
        "tail = head",
        "while tail.nxt is not None:",
        "    tail = tail.nxt",
        "target = head",
        f"for _ in range({link}):",
        "    target = target.nxt",
        "tail.nxt = target",
        "",
    ]
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"head = build({_nums(a['items'])})",
        "",
        *(tail_link if link is not None else []),
        "slow = head",
        "fast = head",
        "looped = False",
        "while fast is not None and fast.nxt is not None:",
        "    slow = slow.nxt",
        "    fast = fast.nxt.nxt",
        "    if slow is fast:",
        "        looped = True",
        "        break",
        "",
        "print(looped)",
    )


# ── 313. Two sorted chains zipped ────────────────────────────


def _list_merge(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"first = build({_nums(a['first'])})",
        f"second = build({_nums(a['second'])})",
        "",
        "front = Node(0)",
        "tail = front",
        "while first is not None and second is not None:",
        "    if first.value <= second.value:",
        "        tail.nxt = first",
        "        first = first.nxt",
        "    else:",
        "        tail.nxt = second",
        "        second = second.nxt",
        "    tail = tail.nxt",
        "tail.nxt = first if first is not None else second",
        "",
        "values = []",
        "node = front.nxt",
        "while node is not None:",
        "    values.append(node.value)",
        "    node = node.nxt",
        "",
        'print(", ".join(str(v) for v in values))',
        "print(len(values))",
    )


# ── 314. A fixed gap ─────────────────────────────────────────


def _list_gap(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        *BUILD_FROM,
        f"head = build({_nums(a['items'])})",
        f"n = {a['n']}",
        "",
        "ahead = head",
        "for _ in range(n):",
        "    ahead = ahead.nxt",
        "",
        "behind = head",
        "while ahead is not None:",
        "    ahead = ahead.nxt",
        "    behind = behind.nxt",
        "",
        "print(behind.value)",
    )


# ── 315. An order that works ─────────────────────────────────


def _topo_order(a: dict) -> str:
    return _lines(
        f"edges = {_name_pairs(a['edges'])}",
        f"names = {sorted(a['names'])!r}",
        "",
        "waiting = {name: 0 for name in names}",
        "leads_to = {name: [] for name in names}",
        "for before, after in edges:",
        "    leads_to[before].append(after)",
        "    waiting[after] += 1",
        "",
        "ready = sorted(n for n in names if waiting[n] == 0)",
        "order = []",
        "while ready:",
        "    here = ready.pop(0)",
        "    order.append(here)",
        "    for nxt in leads_to[here]:",
        "        waiting[nxt] -= 1",
        "        if waiting[nxt] == 0:",
        "            ready.append(nxt)",
        "    ready.sort()",
        "",
        'print(", ".join(order))',
        "print(len(order))",
    )


# ── 316. The leftovers that prove a cycle ────────────────────


def _topo_cycle(a: dict) -> str:
    return _lines(
        f"edges = {_name_pairs(a['edges'])}",
        f"names = {sorted(a['names'])!r}",
        "",
        "waiting = {name: 0 for name in names}",
        "leads_to = {name: [] for name in names}",
        "for before, after in edges:",
        "    leads_to[before].append(after)",
        "    waiting[after] += 1",
        "",
        "ready = sorted(n for n in names if waiting[n] == 0)",
        "done = 0",
        "while ready:",
        "    here = ready.pop(0)",
        "    done += 1",
        "    for nxt in leads_to[here]:",
        "        waiting[nxt] -= 1",
        "        if waiting[nxt] == 0:",
        "            ready.append(nxt)",
        "    ready.sort()",
        "",
        "print(done)",
        "print(len(names) - done)",
        "print(done == len(names))",
    )


# ── 317. A stack that only goes one way ──────────────────────


def _monotonic(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        "answer = [-1] * len(numbers)",
        "stack = []",
        "for i, number in enumerate(numbers):",
        "    while stack and numbers[stack[-1]] < number:",
        "        answer[stack.pop()] = number",
        "    stack.append(i)",
        "",
        'print(", ".join(str(v) for v in answer))',
        "print(len(stack))",
    )


# ── 318. Overlapping ranges folded together ──────────────────


def _merge_spans(a: dict) -> str:
    return _lines(
        f"spans = {_pairs(a['spans'])}",
        "spans.sort()",
        "merged = [spans[0]]",
        "for start, end in spans[1:]:",
        "    last_start, last_end = merged[-1]",
        "    if start <= last_end:",
        "        merged[-1] = (last_start, max(last_end, end))",
        "    else:",
        "        merged.append((start, end))",
        "",
        'print(", ".join(f"{s}-{e}" for s, e in merged))',
        "print(len(merged))",
    )


_BUILDERS = {
    "algo_list_walk": _list_walk,
    "algo_list_reverse": _list_reverse,
    "algo_list_middle": _list_middle,
    "algo_list_cycle": _list_cycle,
    "algo_list_merge": _list_merge,
    "algo_list_gap": _list_gap,
    "algo_topo_order": _topo_order,
    "algo_topo_cycle": _topo_cycle,
    "algo_monotonic": _monotonic,
    "algo_merge_spans": _merge_spans,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    if build is None:
        return None
    return build(args)


def _kahn(names, edges):
    """Kahn's algorithm, ties broken alphabetically so there is one answer."""
    waiting = {n: 0 for n in names}
    leads_to = {n: [] for n in names}
    for before, after in edges:
        leads_to[before].append(after)
        waiting[after] += 1
    ready = sorted(n for n in names if waiting[n] == 0)
    order = []
    while ready:
        here = ready.pop(0)
        order.append(here)
        for nxt in leads_to[here]:
            waiting[nxt] -= 1
            if waiting[nxt] == 0:
                ready.append(nxt)
        ready.sort()
    return order


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out here, independently of the program.

    The guards on this tier mostly police whether the move was needed at
    all: a merge where one list runs out before the other starts, a
    monotonic stack where every element has a next greater one, a
    topological sort whose answer is just the input in the order given.
    """
    a = args
    lines: list[str] = []
    if shape == "algo_list_walk":
        items = list(a["items"])
        if len(items) < 3:
            raise ValueError("a chain needs more than two links")
        lines = [
            ", ".join(str(v) for v in items),
            str(len(items)),
            str(items[-1]),
        ]
    elif shape == "algo_list_reverse":
        items = list(a["items"])
        if len(items) < 3:
            raise ValueError("reversing two nodes shows nothing")
        if items == items[::-1]:
            raise ValueError("a palindrome reversed looks unchanged")
        back = items[::-1]
        lines = [", ".join(str(v) for v in back), str(back[0])]
    elif shape == "algo_list_middle":
        items = list(a["items"])
        if len(items) < 4:
            raise ValueError("the middle of a short chain is not interesting")
        lines = [str(items[len(items) // 2]), str(len(items) // 2)]
    elif shape == "algo_list_cycle":
        link = a["links_to"]
        if link is not None and not 0 <= link < len(a["items"]):
            raise ValueError("the cycle must link back into the chain")
        lines = [str(link is not None)]
    elif shape == "algo_list_merge":
        first, second = list(a["first"]), list(a["second"])
        if first != sorted(first) or second != sorted(second):
            raise ValueError("both chains must already be sorted")
        if not first or not second:
            raise ValueError("both chains must have something in them")
        if max(first) <= min(second) or max(second) <= min(first):
            raise ValueError("the two must interleave, not just sit end to end")
        out = sorted(first + second)
        lines = [", ".join(str(v) for v in out), str(len(out))]
    elif shape == "algo_list_gap":
        items, n = list(a["items"]), a["n"]
        if not 0 < n < len(items):
            raise ValueError("the gap must be inside the chain")
        if n < 2:
            raise ValueError("a gap of one is just the last node")
        lines = [str(items[len(items) - n])]
    elif shape == "algo_topo_order":
        names, edges = list(a["names"]), list(a["edges"])
        order = _kahn(names, edges)
        if len(order) != len(names):
            raise ValueError("this graph has a cycle and cannot be ordered")
        if order == sorted(names):
            raise ValueError(
                "the answer is plain alphabetical order, so the edges "
                "changed nothing"
            )
        lines = [", ".join(order), str(len(order))]
    elif shape == "algo_topo_cycle":
        names, edges = list(a["names"]), list(a["edges"])
        order = _kahn(names, edges)
        done = len(order)
        if done == len(names):
            raise ValueError("this page needs a graph that really has a cycle")
        if done == 0:
            raise ValueError("something must come out before it gets stuck")
        lines = [str(done), str(len(names) - done), str(False)]
    elif shape == "algo_monotonic":
        items = list(a["items"])
        answer = [-1] * len(items)
        stack: list[int] = []
        for i, number in enumerate(items):
            while stack and items[stack[-1]] < number:
                answer[stack.pop()] = number
            stack.append(i)
        # Not "is -1 present" — the last element can never have a next
        # greater, so that is true of every list and guards nothing. Two or
        # more left on the stack is the real signal: it means the stack
        # actually held things up rather than emptying every step, which is
        # what a strictly rising list does.
        if len(stack) < 2:
            raise ValueError("the stack must hold more than one position")
        if answer.count(-1) == len(answer):
            raise ValueError("something must have a next greater value")
        lines = [", ".join(str(v) for v in answer), str(len(stack))]
    elif shape == "algo_merge_spans":
        spans = sorted(tuple(s) for s in a["spans"])
        merged: list[tuple[int, int]] = [spans[0]]
        for start, end in spans[1:]:
            last_start, last_end = merged[-1]
            if start <= last_end:
                merged[-1] = (last_start, max(last_end, end))
            else:
                merged.append((start, end))
        if len(merged) == len(spans):
            raise ValueError("some spans must actually overlap")
        if len(merged) == 1:
            raise ValueError("not everything may merge into one")
        lines = [
            ", ".join(f"{s}-{e}" for s, e in merged),
            str(len(merged)),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
