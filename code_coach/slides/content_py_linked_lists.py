"""Linked Lists: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 121

NODE = """class Node:
    def __init__(self, val, next=None): self.val, self.next = val, next
"""
BUILD = "def build(v): return Node(v[0], build(v[1:])) if v else None\n"
SHOW = "def show(n): return [] if n is None else [n.val] + show(n.next)\n"

DECK = Deck(
    id="py-linked-lists",
    title="Linked Lists",
    language="python",
    blurb="Nodes and next pointers: build, walk, reverse, merge, and the slow/fast tricks interviewers love.",
    slides=(
        Slide(
            title="A Node: a value and a next pointer",
            text="A linked list is a chain of small objects. Each Node holds one value and a reference to the next Node; the last one points to None.",
            code=NODE + r"""a = Node(1, Node(2, Node(3)))
print(a.val)
print(a.next.val)
print(a.next.next.next)""",
            output="1\n2\nNone",
            point="A list is just a head Node; everything else is reached by following .next.",
        ),
        Slide(
            title="Building a list from values",
            text="Real problems give you a list of numbers and expect a chain. Building from the back is easy: start with None and put each new Node in front.",
            code=NODE + r"""def build(vals):
    head = None
    for v in reversed(vals): head = Node(v, head)
    return head
h = build([4, 5, 6])
print(h.val, h.next.val, h.next.next.val)""",
            output="4 5 6",
            point="Walk the values backwards, and each new Node points at what you had so far.",
        ),
        Slide(
            title="Walking a list",
            text="To visit every Node, keep a current pointer and move it along with cur = cur.next. Stop when it becomes None.",
            code=NODE + BUILD + r"""cur = build([1, 2, 3])
while cur:
    print(cur.val)
    cur = cur.next""",
            output="1\n2\n3",
            point="while cur: ... cur = cur.next is the loop behind almost every linked-list problem.",
        ),
        Slide(
            title="Printing a list with a helper",
            text="While debugging, a helper that turns the chain into text saves a lot of squinting. Collect the values, then join them with arrows.",
            code=NODE + BUILD + r"""def show(head):
    parts = []
    while head:
        parts.append(str(head.val))
        head = head.next
    return " -> ".join(parts)
print(show(build([1, 2, 3])))""",
            output="1 -> 2 -> 3",
            point="Write show() first; you will use it to check every other answer.",
        ),
        Slide(
            title="Inserting at the head",
            text="Adding to the front is one step: make a Node whose next is the old head. Adding after a node you already hold is just as cheap.",
            code=NODE + BUILD + SHOW + r"""h = build([2, 3])
h = Node(1, h)
print(show(h))
h.next = Node(9, h.next)
print(show(h))""",
            output="[1, 2, 3]\n[1, 9, 2, 3]",
            point="Insert at the head or after a known node in O(1): no shifting, just two pointers.",
        ),
        Slide(
            title="Appending at the tail",
            text="You only have the head, so you must walk to the last Node (the one whose next is None) and hang the new Node there. That walk makes append O(n). An empty list needs a special case.",
            code=NODE + BUILD + SHOW + r"""h = build([1, 2])
cur = h
while cur.next: cur = cur.next
cur.next = Node(3)
print(show(h))""",
            output="[1, 2, 3]",
            point="Stop at cur.next being None, not at cur being None, or you walk off the end.",
        ),
        Slide(
            title="Deleting a node",
            text="To remove a node, stop on the one before it and point around it: cur.next = cur.next.next. Python then frees the skipped Node by itself.",
            code=NODE + BUILD + SHOW + r"""cur = h = build([1, 2, 3, 4])
while cur.next.val != 3: cur = cur.next
cur.next = cur.next.next
print(show(h))""",
            output="[1, 2, 4]",
            point="You cannot unlink a node from itself; you must hold the node before it.",
        ),
        Slide(
            title="Reversing a list, pointer by pointer",
            text="Walk once and flip each arrow. Save the rest first (nxt), point the current Node backwards at prev, then step both pointers forward.",
            code=NODE + r"""h = Node(1, Node(2, Node(3)))
prev = None
while h:
    nxt = h.next    # remember the rest
    h.next = prev   # flip the arrow
    prev = h        # prev steps forward
    h = nxt         # h steps forward
print(prev.val, prev.next.val, prev.next.next.val)""",
            output="3 2 1",
            point="Save next, flip, advance prev, advance cur: four moves, O(n) time, O(1) space.",
        ),
        Slide(
            title="The dummy head trick",
            text="If the head itself may be deleted, you need special code. Put a fake Node in front and work from it: now every real node has a node before it, and you return dummy.next.",
            code=NODE + BUILD + SHOW + r"""dummy = Node(0, build([2, 2, 1, 2, 3]))
cur = dummy
while cur.next:
    if cur.next.val == 2: cur.next = cur.next.next
    else: cur = cur.next
print(show(dummy.next))""",
            output="[1, 3]",
            point="A dummy head removes the 'what if it is the first node' special case.",
        ),
        Slide(
            title="Finding the middle: slow and fast",
            text="Move one pointer one step and another two steps at a time. When the fast one reaches the end, the slow one is at the middle, without ever counting the length.",
            code=NODE + BUILD + r"""h = build([1, 2, 3, 4, 5])
slow = fast = h
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
print(slow.val)""",
            output="3",
            point="Two speeds turn 'find the middle' into one pass. With an even count, slow lands on the second middle.",
        ),
        Slide(
            title="Detecting a cycle (Floyd)",
            text="If a list loops back on itself, a walk never ends. Run a slow and a fast pointer: inside a loop the fast one must eventually land on the slow one.",
            code=NODE + r"""a, b, c = Node(1), Node(2), Node(3)
a.next, b.next, c.next = b, c, a
slow = fast = a
while fast and fast.next:
    slow, fast = slow.next, fast.next.next
    if slow is fast: print("cycle"); break
else: print("no cycle")""",
            output="cycle",
            point="Tortoise and hare: if they ever meet, there is a cycle; if fast hits None, there is not.",
        ),
        Slide(
            title="Merging two sorted lists",
            text="Keep a tail pointer on a dummy head. Always attach the smaller front node, move that list on, and when one list runs out hang the rest of the other.",
            code=NODE + BUILD + SHOW + r"""dummy = tail = Node(0); a, b = build([1, 4, 6]), build([2, 3, 7])
while a and b:
    if b.val < a.val: a, b = b, a
    tail.next, a = a, a.next; tail = tail.next
tail.next = a or b
print(show(dummy.next))""",
            output="[1, 2, 3, 4, 6, 7]",
            point="Merge = repeatedly take the smaller head; the leftover list is already sorted.",
        ),
        Slide(
            title="Removing the n-th node from the end",
            text="Send a fast pointer n steps ahead, then move both until fast is on the last Node. The slow pointer is now just before the one to remove, found in a single pass.",
            code=NODE + BUILD + SHOW + r"""dummy = Node(0, build([1, 2, 3, 4, 5]))
fast = slow = dummy
for _ in range(2): fast = fast.next
while fast.next: slow, fast = slow.next, fast.next
slow.next = slow.next.next
print(show(dummy.next))""",
            output="[1, 2, 3, 5]",
            point="Keep a gap of n between two pointers and the gap does the counting for you.",
        ),
        Slide(
            title="Python lists are arrays, not chains",
            text="A Python list is a dynamic array: a row of slots, so nums[i] is a direct jump, but inserting at the front shifts everything. For fast ends use collections.deque.",
            code=r"""from collections import deque
nums = [10, 20, 30]
nums.insert(0, 5)
print(nums, nums[2])
d = deque([1, 2, 3])
d.appendleft(0)
print(d)""",
            output="[5, 10, 20, 30] 20\ndeque([0, 1, 2, 3])",
            point="list: fast index, slow front insert. deque: fast at both ends, slow in the middle.",
        ),
        Slide(
            title="When is a linked list worth it?",
            text="In everyday Python, almost never: lists and deques are faster. Linked lists matter for interviews and for ideas like stacks, queues and LRU caches, where you add or cut at known spots in O(1).",
            code=NODE + r"""top = None
for x in (1, 2, 3): top = Node(x, top)
print(top.val, top.next.val)
top = top.next
print(top.val)""",
            output="3 2\n2",
            point="Use one when you hold a node and need O(1) insert or cut there; otherwise reach for list or deque.",
        ),
    ),
)
