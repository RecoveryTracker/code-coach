"""Lessons: how to arrive at a solution, not just what the solution is.

The rest of this package tells you what a pattern is, gives you a template,
and hands you finished code. None of that shows the part that actually has to
be learned — the move from reading a question to knowing which shape it wants,
and then building the code a line at a time.

So each pattern has one problem taken the whole way. The obvious approach
first, because that is what anyone thinks of; what is wrong with it, stated as
a cost rather than as a scolding; the one observation that fixes it; and then
the solution assembled in stages, each stage a sentence and the code as it
stands after it.

The code here is written in the same neutral, Python-leaning style as the
pattern templates, so it reads the same whichever language you are practising
in. The finished, runnable version in your language is the problem's own
solution, a pane away.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Stage:
    """One move in the reasoning, and the code as it stands after it."""

    explain: str
    code: str = ""


@dataclass(frozen=True)
class Worked:
    """One problem taken from the question to a finished solution."""

    problem: int
    naive: str
    why_not: str
    insight: str
    stages: tuple[Stage, ...] = field(default_factory=tuple)


def _s(explain: str, code: str = "") -> Stage:
    return Stage(explain=explain, code=code)


WORKED: dict[str, Worked] = {
    "lc-hashmap": Worked(
        problem=1,
        naive=(
            "Try every pair. For each number, walk the rest of the list "
            "looking for one that completes the target."
        ),
        why_not=(
            "Two nested loops over n numbers is n squared comparisons. At a "
            "thousand numbers that is a million, and it grows faster than the "
            "input does."
        ),
        insight=(
            "You are not really searching. You know exactly which number you "
            "want — target minus the one in your hand — so the question is "
            "'have I seen this specific value?', and a dict answers that in "
            "one step."
        ),
        stages=(
            _s(
                "Walk the list once, and keep a dict of what you have passed. "
                "The value is the key, because the value is what you will "
                "look up.",
                "seen = {}\nfor i, n in enumerate(nums):\n    ...",
            ),
            _s(
                "At each number, name the one that would finish the pair.",
                "seen = {}\nfor i, n in enumerate(nums):\n    need = target - n",
            ),
            _s(
                "If you have already passed that number, you are done. Look "
                "before you store, or a number will pair with itself.",
                "seen = {}\nfor i, n in enumerate(nums):\n    need = target - n\n"
                "    if need in seen:\n        return [seen[need], i]",
            ),
            _s(
                "Otherwise remember this one and carry on. Storing the index, "
                "not just the value, because the answer is indexes.",
                "seen = {}\nfor i, n in enumerate(nums):\n    need = target - n\n"
                "    if need in seen:\n        return [seen[need], i]\n"
                "    seen[n] = i\nreturn []",
            ),
        ),
    ),
    "lc-two-pointers": Worked(
        problem=167,
        naive=(
            "Try every pair again, the same way you would if the list were "
            "unsorted."
        ),
        why_not=(
            "It works, and it throws away the one fact the question went out "
            "of its way to give you: the list is sorted. Any solution that "
            "would work just as well shuffled is ignoring the hint."
        ),
        insight=(
            "Start at both ends. The sum of the outermost pair is the largest "
            "small number plus the largest — so if it is too big, only the "
            "right end can move, and if it is too small, only the left can. "
            "Each comparison discards a whole column of pairs."
        ),
        stages=(
            _s(
                "Put one finger at each end.",
                "left = 0\nright = len(nums) - 1",
            ),
            _s(
                "While they have not met, look at the pair they name.",
                "left = 0\nright = len(nums) - 1\nwhile left < right:\n"
                "    total = nums[left] + nums[right]",
            ),
            _s(
                "Too small means the left number is the problem: every pair "
                "using it is at most this, so move left inward.",
                "left = 0\nright = len(nums) - 1\nwhile left < right:\n"
                "    total = nums[left] + nums[right]\n"
                "    if total < target:\n        left += 1",
            ),
            _s(
                "Too big means the right number is the problem, by the same "
                "argument in reverse. Equal means you are finished.",
                "left = 0\nright = len(nums) - 1\nwhile left < right:\n"
                "    total = nums[left] + nums[right]\n"
                "    if total == target:\n        return [left + 1, right + 1]\n"
                "    if total < target:\n        left += 1\n    else:\n"
                "        right -= 1",
            ),
        ),
    ),
    "lc-sliding-window": Worked(
        problem=3,
        naive=(
            "Take every substring and check each one for a repeated "
            "character."
        ),
        why_not=(
            "There are about n squared substrings and checking one costs "
            "another pass, so it is n cubed. It also re-examines the same "
            "characters over and over."
        ),
        insight=(
            "Neighbouring substrings overlap almost entirely. Keep one window "
            "and edit it: the right edge always moves forward, and the left "
            "edge only moves when the window has broken the rule."
        ),
        stages=(
            _s(
                "Track the window's left edge and what is inside it.",
                "left = 0\nseen = set()\nbest = 0",
            ),
            _s(
                "March the right edge along, one character per turn, always.",
                "for right, ch in enumerate(text):\n    ...",
            ),
            _s(
                "Before the character can join, the window has to be legal "
                "with it in. While it is not, drop from the left.",
                "for right, ch in enumerate(text):\n    while ch in seen:\n"
                "        seen.remove(text[left])\n        left += 1",
            ),
            _s(
                "Now add it, and measure. The answer is recorded after the "
                "window is legal again, never during the repair.",
                "for right, ch in enumerate(text):\n    while ch in seen:\n"
                "        seen.remove(text[left])\n        left += 1\n"
                "    seen.add(ch)\n    best = max(best, right - left + 1)",
            ),
        ),
    ),
    "lc-stack": Worked(
        problem=20,
        naive=(
            "Count the brackets. If there are as many closers as openers, "
            "call it balanced."
        ),
        why_not=(
            "Counting cannot tell '([)]' from '()[]'. Order matters, and a "
            "count has thrown the order away."
        ),
        insight=(
            "A closing bracket has to match the most recent unclosed opener — "
            "not any opener, the last one. 'Most recent' is exactly what a "
            "stack gives you."
        ),
        stages=(
            _s(
                "Keep the openers you have not closed yet.",
                "stack = []\npairs = {')': '(', ']': '[', '}': '{'}",
            ),
            _s(
                "An opener is just remembered.",
                "for ch in text:\n    if ch not in pairs:\n        stack.append(ch)",
            ),
            _s(
                "A closer has to match the top. Nothing on top means a closer "
                "with no opener at all.",
                "for ch in text:\n    if ch not in pairs:\n        stack.append(ch)\n"
                "    else:\n        if not stack or stack.pop() != pairs[ch]:\n"
                "            return False",
            ),
            _s(
                "At the end the stack has to be empty, or something was "
                "opened and never closed.",
                "return not stack",
            ),
        ),
    ),
    "lc-linked-list": Worked(
        problem=206,
        naive=(
            "Read the values into a list, reverse it, and build a new chain "
            "from them."
        ),
        why_not=(
            "It works, and it uses memory proportional to the list to solve a "
            "problem that only needs to change the direction of each arrow. "
            "The interesting version is in place."
        ),
        insight=(
            "Reversing a chain is flipping each link one at a time. The only "
            "difficulty is that overwriting a node's next loses the rest of "
            "the list — so grab it first."
        ),
        stages=(
            _s(
                "Two pointers: what came before, and where you are.",
                "prev = None\ncur = head",
            ),
            _s(
                "Before touching anything, save the rest of the list. This is "
                "the line the whole problem is about.",
                "while cur:\n    nxt = cur.next",
            ),
            _s(
                "Now the link can be turned around safely.",
                "while cur:\n    nxt = cur.next\n    cur.next = prev",
            ),
            _s(
                "Shuffle both pointers forward. When cur runs off the end, "
                "prev is standing on the new head.",
                "while cur:\n    nxt = cur.next\n    cur.next = prev\n"
                "    prev = cur\n    cur = nxt\nreturn prev",
            ),
        ),
    ),
    "lc-binary-search": Worked(
        problem=704,
        naive="Look at every element until you find the target.",
        why_not=(
            "Linear is fine for a small list and ignores the sorting, which "
            "is the only reason the question mentions it. Sorted means you "
            "can rule out half the list with one comparison."
        ),
        insight=(
            "Keep a range that the answer must be inside, and halve it every "
            "turn. The whole difficulty is being exact about whether the ends "
            "are included, and staying consistent about it."
        ),
        stages=(
            _s(
                "The answer is somewhere in this range, both ends included.",
                "low = 0\nhigh = len(nums) - 1",
            ),
            _s(
                "While the range still holds something, look at its middle.",
                "while low <= high:\n    mid = (low + high) // 2",
            ),
            _s(
                "Found it, or the target is bigger, so nothing at mid or "
                "below can be it.",
                "while low <= high:\n    mid = (low + high) // 2\n"
                "    if nums[mid] == target:\n        return mid\n"
                "    if nums[mid] < target:\n        low = mid + 1",
            ),
            _s(
                "Otherwise it is smaller. Note that mid is always excluded "
                "from the next range — that is what stops it looping forever.",
                "low = 0\nhigh = len(nums) - 1\nwhile low <= high:\n"
                "    mid = (low + high) // 2\n"
                "    if nums[mid] == target:\n        return mid\n"
                "    if nums[mid] < target:\n        low = mid + 1\n"
                "    else:\n        high = mid - 1\nreturn -1",
            ),
        ),
    ),
    "lc-tree-dfs": Worked(
        problem=104,
        naive=(
            "Walk the tree keeping a running depth and a best-so-far in a "
            "variable outside the walk."
        ),
        why_not=(
            "It works, but it is more bookkeeping than the problem needs, and "
            "the state outside the recursion is where the bugs live."
        ),
        insight=(
            "Ask the question of the children instead. The depth of a tree is "
            "one more than the depth of its deeper side — which is the same "
            "question, on something smaller."
        ),
        stages=(
            _s(
                "Say what the answer is for the smallest possible tree. An "
                "empty tree has depth zero, and that is the base case.",
                "def max_depth(node):\n    if not node:\n        return 0",
            ),
            _s(
                "Assume the function already works, and ask it about each "
                "child. This is the leap: you do not trace it, you trust it.",
                "def max_depth(node):\n    if not node:\n        return 0\n"
                "    left = max_depth(node.left)\n    right = max_depth(node.right)",
            ),
            _s(
                "Combine the two answers into this node's answer.",
                "def max_depth(node):\n    if not node:\n        return 0\n"
                "    left = max_depth(node.left)\n    right = max_depth(node.right)\n"
                "    return 1 + max(left, right)",
            ),
            _s(
                "Every DFS on a tree is these three parts: the base case, the "
                "calls on the children, and the line that combines them.",
            ),
        ),
    ),
    "lc-tree-bfs": Worked(
        problem=102,
        naive=(
            "Walk the tree with recursion, and tag each value with its depth "
            "so you can group them afterwards."
        ),
        why_not=(
            "That works and it fights the traversal. Recursion goes down one "
            "branch at a time, so you get the values in the wrong order and "
            "then sort them back."
        ),
        insight=(
            "A queue visits in the order things arrive, which is level by "
            "level. The only trick is knowing where a level ends — and the "
            "queue's length at the top of a turn is exactly one level."
        ),
        stages=(
            _s(
                "Start the queue with the root.",
                "queue = deque([root])\nlevels = []",
            ),
            _s(
                "Take a snapshot of the size FIRST. It will grow as you add "
                "children, so reading it later would run into the next level.",
                "while queue:\n    size = len(queue)",
            ),
            _s(
                "Take exactly that many, and they are one level.",
                "while queue:\n    size = len(queue)\n    level = []\n"
                "    for _ in range(size):\n        node = queue.popleft()\n"
                "        level.append(node.val)",
            ),
            _s(
                "Their children queue up behind, ready to be the next level.",
                "while queue:\n    size = len(queue)\n    level = []\n"
                "    for _ in range(size):\n        node = queue.popleft()\n"
                "        level.append(node.val)\n"
                "        if node.left:\n            queue.append(node.left)\n"
                "        if node.right:\n            queue.append(node.right)\n"
                "    levels.append(level)",
            ),
        ),
    ),
    "lc-graph": Worked(
        problem=200,
        naive=(
            "Count the cells that hold land, or try to spot the shapes by "
            "scanning row by row."
        ),
        why_not=(
            "Counting cells counts cells, not islands. Row-by-row shape "
            "spotting founders as soon as one island is U-shaped."
        ),
        insight=(
            "Every walk you start from a piece of land you have not seen "
            "before consumes exactly one whole island. So the answer is the "
            "number of times you had to start a walk."
        ),
        stages=(
            _s(
                "Visit every cell, and only act on unvisited land.",
                "count = 0\nfor r in range(rows):\n    for c in range(cols):\n"
                "        if grid[r][c] == '1':\n            ...",
            ),
            _s(
                "When you find some, that is a new island, so count it and "
                "then go and consume the whole thing.",
                "count = 0\nfor r in range(rows):\n    for c in range(cols):\n"
                "        if grid[r][c] == '1':\n            count += 1\n"
                "            sink(r, c)",
            ),
            _s(
                "The walk marks as it goes. Marking is what stops it "
                "revisiting — a graph has cycles, and without this it never "
                "terminates.",
                "def sink(r, c):\n    if out of bounds or grid[r][c] != '1':\n"
                "        return\n    grid[r][c] = '0'",
            ),
            _s(
                "Then spread to the four neighbours, each of which stops "
                "itself the same way.",
                "def sink(r, c):\n    if out of bounds or grid[r][c] != '1':\n"
                "        return\n    grid[r][c] = '0'\n    sink(r + 1, c)\n"
                "    sink(r - 1, c)\n    sink(r, c + 1)\n    sink(r, c - 1)",
            ),
        ),
    ),
    "lc-backtracking": Worked(
        problem=78,
        naive=(
            "Write nested loops — one for each element you might include."
        ),
        why_not=(
            "You cannot: the number of loops would have to depend on the "
            "length of the input, and you have to write them before you know "
            "it. Recursion is how you get a loop nest whose depth is decided "
            "at run time."
        ),
        insight=(
            "At each element there are exactly two choices: take it or leave "
            "it. Explore one, undo it, explore the other. Every subset is one "
            "path down that tree of choices."
        ),
        stages=(
            _s(
                "Carry the choices made so far, and record a copy whenever "
                "you arrive somewhere. A copy, because the list keeps "
                "changing underneath you.",
                "out = []\npicked = []\n\ndef walk(start):\n"
                "    out.append(list(picked))",
            ),
            _s(
                "From here, try each remaining element in turn.",
                "def walk(start):\n    out.append(list(picked))\n"
                "    for i in range(start, len(nums)):\n        ...",
            ),
            _s(
                "Take it, and go deeper. Passing i + 1 is what stops you "
                "picking the same element twice, and stops the same set being "
                "built in a different order.",
                "def walk(start):\n    out.append(list(picked))\n"
                "    for i in range(start, len(nums)):\n"
                "        picked.append(nums[i])\n        walk(i + 1)",
            ),
            _s(
                "Then put it back. This line is the 'backtracking': without "
                "it the choices from one branch leak into the next.",
                "def walk(start):\n    out.append(list(picked))\n"
                "    for i in range(start, len(nums)):\n"
                "        picked.append(nums[i])\n        walk(i + 1)\n"
                "        picked.pop()",
            ),
        ),
    ),
    "lc-heap": Worked(
        problem=215,
        naive="Sort the list and take the kth from the end.",
        why_not=(
            "Nothing at all, for one query on a list that fits in memory — it "
            "is n log n and perfectly clear. It is the wrong answer only when "
            "n is huge and k is small, because you have ordered a million "
            "things to learn about five of them."
        ),
        insight=(
            "You never need the whole order. Keep only the best k seen so "
            "far, and the worst of those is the one to evict — which is the "
            "smallest, so a min-heap puts it exactly where you can reach it."
        ),
        stages=(
            _s(
                "Hold a heap of the k largest so far. It is a MIN-heap, which "
                "feels backwards until you see why.",
                "heap = []",
            ),
            _s(
                "Offer every number to it.",
                "heap = []\nfor n in nums:\n    heappush(heap, n)",
            ),
            _s(
                "If that made k + 1, drop the smallest — and the smallest is "
                "the root, which is the whole reason the heap is a min-heap.",
                "for n in nums:\n    heappush(heap, n)\n    if len(heap) > k:\n"
                "        heappop(heap)",
            ),
            _s(
                "At the end the heap holds the k largest, and its root is the "
                "smallest of those: the kth largest overall.",
                "return heap[0]",
            ),
        ),
    ),
    "lc-topological": Worked(
        problem=207,
        naive=(
            "Follow the prerequisites from each course and see whether you "
            "ever come back to where you started."
        ),
        why_not=(
            "Doing that from every course re-walks the same paths again and "
            "again, and getting the 'currently on the stack' bookkeeping "
            "right is fiddlier than it looks."
        ),
        insight=(
            "Turn it around. Instead of hunting for a cycle, repeatedly take "
            "whatever has no prerequisites left. If you get stuck before "
            "taking everything, what remains is a cycle — you never have to "
            "look for one."
        ),
        stages=(
            _s(
                "Build who-unlocks-what, and how many prerequisites each "
                "course is still waiting on.",
                "graph = {i: [] for i in range(n)}\nindegree = [0] * n\n"
                "for course, prereq in prerequisites:\n"
                "    graph[prereq].append(course)\n    indegree[course] += 1",
            ),
            _s(
                "Start with everything that is already available.",
                "queue = deque([i for i in range(n) if indegree[i] == 0])\ntaken = 0",
            ),
            _s(
                "Take one, and tell everything it unlocks that one of its "
                "prerequisites is done.",
                "while queue:\n    node = queue.popleft()\n    taken += 1\n"
                "    for nxt in graph[node]:\n        indegree[nxt] -= 1",
            ),
            _s(
                "Anything that hits zero has just become available. If you "
                "took them all, there was no cycle.",
                "while queue:\n    node = queue.popleft()\n    taken += 1\n"
                "    for nxt in graph[node]:\n        indegree[nxt] -= 1\n"
                "        if indegree[nxt] == 0:\n            queue.append(nxt)\n"
                "return taken == n",
            ),
        ),
    ),
    "lc-dp": Worked(
        problem=70,
        naive=(
            "Recurse: the ways to reach step n are the ways to reach n - 1 "
            "plus the ways to reach n - 2."
        ),
        why_not=(
            "The recurrence is right and the implementation is exponential. "
            "Reaching step 40 recomputes step 30 over and over — millions of "
            "times, all with the same answer."
        ),
        insight=(
            "Every one of those repeats has the same answer, so compute each "
            "step once and keep it. And once you notice you only ever look "
            "back two steps, you do not even need the table."
        ),
        stages=(
            _s(
                "Say the recurrence out loud first. Almost every DP problem "
                "is won or lost here rather than in the code.",
                "ways(n) = ways(n - 1) + ways(n - 2)",
            ),
            _s(
                "Anchor it. There is one way to stand still, and one way to "
                "climb a single step.",
                "ways(0) = 1\nways(1) = 1",
            ),
            _s(
                "Now build upwards instead of recursing downwards, and each "
                "step is computed exactly once.",
                "table = [1, 1]\nfor i in range(2, n + 1):\n"
                "    table.append(table[i - 1] + table[i - 2])\nreturn table[n]",
            ),
            _s(
                "The table only ever reads its last two entries, so keep two "
                "variables and let the rest go.",
                "a, b = 1, 1\nfor _ in range(n - 1):\n    a, b = b, a + b\nreturn b",
            ),
        ),
    ),
}


def worked_for(pattern_id: str | None) -> Worked | None:
    """The lesson for a pattern, or None where there isn't one yet."""
    if pattern_id is None:
        return None
    return WORKED.get(pattern_id)
