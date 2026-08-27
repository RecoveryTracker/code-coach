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


WORKED: dict[int, Worked] = {
    1: Worked(
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
    167: Worked(
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
    3: Worked(
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
    20: Worked(
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
    206: Worked(
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
    704: Worked(
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
    104: Worked(
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
    102: Worked(
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
    200: Worked(
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
    78: Worked(
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
    215: Worked(
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
    207: Worked(
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
    70: Worked(
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
    # ── Hash maps ──────────────────────────────────────────
    217: Worked(
        problem=217,
        naive=(
            "Compare every number against every other one and stop the "
            "moment two match."
        ),
        why_not=(
            "It is n squared, and on a list with no duplicates at all it does "
            "every single one of those comparisons before answering no."
        ),
        insight=(
            "You never need to compare anything. The only question is whether "
            "a number has turned up before, and a set answers that as you go."
        ),
        stages=(
            _s(
                "Keep what you have passed.",
                "seen = set()",
            ),
            _s(
                "Each number either finishes the job or joins the set.",
                "seen = set()\nfor n in nums:\n    if n in seen:\n"
                "        return True\n    seen.add(n)",
            ),
            _s(
                "Getting to the end means every value was distinct.",
                "seen = set()\nfor n in nums:\n    if n in seen:\n"
                "        return True\n    seen.add(n)\nreturn False",
            ),
        ),
    ),
    242: Worked(
        problem=242,
        naive="Sort both strings and compare them.",
        why_not=(
            "Nothing much — it is n log n, short, and obviously correct. It is "
            "just doing more than the question needs: you do not care what "
            "the order is, only that the letters match."
        ),
        insight=(
            "An anagram is two strings with the same letter counts. Count the "
            "first, spend the second against it, and anything left over means "
            "no."
        ),
        stages=(
            _s(
                "Different lengths cannot be anagrams, and checking first "
                "saves the rest of the work.",
                "if len(s) != len(t):\n    return False",
            ),
            _s(
                "Count the letters of the first.",
                "counts = {}\nfor ch in s:\n    counts[ch] = counts.get(ch, 0) + 1",
            ),
            _s(
                "Spend the second against those counts. Going below zero "
                "means the second string has a letter the first did not.",
                "for ch in t:\n    if counts.get(ch, 0) == 0:\n        return False\n"
                "    counts[ch] -= 1\nreturn True",
            ),
        ),
    ),
    49: Worked(
        problem=49,
        naive=(
            "Compare every word with every other one, testing each pair for "
            "being anagrams."
        ),
        why_not=(
            "That is n squared pair tests, each costing the length of a word. "
            "It also gives you pairs when what you wanted was groups."
        ),
        insight=(
            "Anagrams need a name they all share. Sort the letters of a word "
            "and every anagram of it produces the same string — so use that "
            "as a dict key and the groups build themselves."
        ),
        stages=(
            _s(
                "A dict from the shared name to the words that have it.",
                "groups = {}",
            ),
            _s(
                "The sorted letters are the name. Any two anagrams agree on "
                "it, and nothing else does.",
                "groups = {}\nfor word in words:\n    key = ''.join(sorted(word))",
            ),
            _s(
                "File each word under its name, and the values are the answer.",
                "groups = {}\nfor word in words:\n    key = ''.join(sorted(word))\n"
                "    groups.setdefault(key, []).append(word)\nreturn list(groups.values())",
            ),
        ),
    ),
    454: Worked(
        problem=454,
        naive="Four nested loops, one per list.",
        why_not=(
            "n to the fourth. At two hundred elements each that is 1.6 "
            "billion combinations, which is not a constant factor away from "
            "workable."
        ),
        insight=(
            "Split it down the middle. Every sum from the first two lists can "
            "be counted in n squared, and then each pair from the other two "
            "asks one question: how many times have I seen its negation?"
        ),
        stages=(
            _s(
                "Count every sum the first half can make.",
                "pairs = {}\nfor x in a:\n    for y in b:\n"
                "        pairs[x + y] = pairs.get(x + y, 0) + 1",
            ),
            _s(
                "Now each pair from the second half is a lookup, not a search.",
                "found = 0\nfor z in c:\n    for w in d:\n"
                "        found += pairs.get(-(z + w), 0)",
            ),
            _s(
                "Adding the count rather than one, because every earlier pair "
                "that made that sum is a separate answer.",
                "return found",
            ),
        ),
    ),
    560: Worked(
        problem=560,
        naive=(
            "Take every start, extend to every end, and add up each run as "
            "you go."
        ),
        why_not=(
            "n squared, and it is the version most people write. It is also "
            "the version a sliding window cannot rescue, because negative "
            "numbers mean a longer run is not necessarily a bigger sum."
        ),
        insight=(
            "A run from i to j sums to total(j) minus total(i). So keep the "
            "running total, and ask how many earlier totals were exactly k "
            "less than the one you are standing on."
        ),
        stages=(
            _s(
                "Count the running totals seen so far. Zero has been seen "
                "once — that is the empty prefix, and it is what lets a run "
                "starting at index 0 count.",
                "seen = {0: 1}\nrunning = 0\nfound = 0",
            ),
            _s(
                "Extend the running total by one number.",
                "seen = {0: 1}\nrunning = 0\nfound = 0\nfor n in nums:\n"
                "    running += n",
            ),
            _s(
                "Any earlier total of running minus k ends a qualifying run "
                "here, and there may be several.",
                "for n in nums:\n    running += n\n"
                "    found += seen.get(running - k, 0)",
            ),
            _s(
                "Then record this total for the runs that end later.",
                "for n in nums:\n    running += n\n"
                "    found += seen.get(running - k, 0)\n"
                "    seen[running] = seen.get(running, 0) + 1\nreturn found",
            ),
        ),
    ),
    128: Worked(
        problem=128,
        naive="Sort the list, then walk it counting consecutive runs.",
        why_not=(
            "It is n log n and perfectly readable, and the question asks for "
            "linear — which is the only reason to look further."
        ),
        insight=(
            "Only start counting from a number with no left-hand neighbour. "
            "Every run is then walked exactly once, from its own beginning, "
            "so the whole thing is linear despite the inner loop."
        ),
        stages=(
            _s(
                "A set, so 'is this number present?' costs nothing.",
                "pool = set(nums)\nbest = 0",
            ),
            _s(
                "Skip anything that is not the start of a run. This one line "
                "is what stops the inner loop being quadratic.",
                "pool = set(nums)\nbest = 0\nfor n in pool:\n"
                "    if n - 1 in pool:\n        continue",
            ),
            _s(
                "From a genuine start, walk upwards as far as the run goes.",
                "    length = 1\n    while n + length in pool:\n        length += 1\n"
                "    best = max(best, length)",
            ),
        ),
    ),
    36: Worked(
        problem=36,
        naive=(
            "Check the nine rows, then the nine columns, then the nine boxes "
            "— twenty-seven passes over the board."
        ),
        why_not=(
            "It works and it is fine. The board is a fixed 81 cells, so this "
            "is not about speed; it is that three separate passes is three "
            "places to get the indexing wrong, and the box index is the one "
            "everyone gets wrong."
        ),
        insight=(
            "Every cell belongs to exactly one row, one column and one box, "
            "so one pass can check all three at once. The box is identified "
            "by (row // 3, column // 3)."
        ),
        stages=(
            _s(
                "One set of seen digits per row, per column, and per box.",
                "rows, cols, boxes = {}, {}, {}",
            ),
            _s(
                "Walk every cell once. Empty cells break no rules.",
                "for r in range(9):\n    for c in range(9):\n"
                "        value = board[r][c]\n        if value == '.':\n"
                "            continue",
            ),
            _s(
                "Name the box, and fail if the digit is already in any of the "
                "three groups this cell belongs to.",
                "        box = (r // 3, c // 3)\n"
                "        if value in rows.setdefault(r, set()):\n"
                "            return False\n"
                "        if value in cols.setdefault(c, set()):\n"
                "            return False\n"
                "        if value in boxes.setdefault(box, set()):\n"
                "            return False",
            ),
            _s(
                "Otherwise record it in all three and carry on.",
                "        rows[r].add(value)\n        cols[c].add(value)\n"
                "        boxes[box].add(value)\nreturn True",
            ),
        ),
    ),
    # ── Two pointers ───────────────────────────────────────
    125: Worked(
        problem=125,
        naive=(
            "Strip out everything that is not a letter or digit, lowercase "
            "what is left, and compare the result with its reverse."
        ),
        why_not=(
            "Genuinely nothing, and it is the version to write if someone "
            "asks you to be clear. It builds two extra strings, which is the "
            "only thing the two-pointer version saves."
        ),
        insight=(
            "You do not need the cleaned string, only the comparison. Walk "
            "inwards from both ends, skipping anything that does not count, "
            "and compare in place."
        ),
        stages=(
            _s(
                "One finger at each end.",
                "left = 0\nright = len(text) - 1",
            ),
            _s(
                "Skip anything that is not part of the comparison. The bound "
                "check has to be inside the skip, or an all-punctuation string "
                "runs off the end.",
                "while left < right:\n"
                "    while left < right and not text[left].isalnum():\n"
                "        left += 1\n"
                "    while left < right and not text[right].isalnum():\n"
                "        right -= 1",
            ),
            _s(
                "Now both fingers are on real characters, so compare them.",
                "    if text[left].lower() != text[right].lower():\n"
                "        return False\n    left += 1\n    right -= 1\nreturn True",
            ),
        ),
    ),
    11: Worked(
        problem=11,
        naive="Try every pair of lines and keep the largest area.",
        why_not=(
            "n squared. With a hundred thousand lines that is five billion "
            "pairs, and most of them are obviously worse than ones you have "
            "already seen."
        ),
        insight=(
            "Start at the widest pair. Moving either edge inward loses width, "
            "so it is only worth moving the SHORTER one — the taller line can "
            "never be the reason a narrower pair is better."
        ),
        stages=(
            _s(
                "The widest possible container first.",
                "left = 0\nright = len(height) - 1\nbest = 0",
            ),
            _s(
                "Its area is the width times the shorter of the two walls.",
                "while left < right:\n"
                "    area = (right - left) * min(height[left], height[right])\n"
                "    best = max(best, area)",
            ),
            _s(
                "Then discard the shorter wall. Keeping it could only ever "
                "give a narrower container of the same height or less.",
                "    if height[left] < height[right]:\n        left += 1\n"
                "    else:\n        right -= 1\nreturn best",
            ),
        ),
    ),
    15: Worked(
        problem=15,
        naive="Three nested loops over every triple.",
        why_not=(
            "n cubed, and then you still have to remove the duplicate "
            "triples, which is its own problem."
        ),
        insight=(
            "Sort first. Then fix one number and the rest is Two Sum on a "
            "sorted list, which two pointers solve in one pass — and sorting "
            "also puts duplicates next to each other so they are easy to skip."
        ),
        stages=(
            _s(
                "Sorting is what makes both halves of this work.",
                "nums.sort()\nout = []",
            ),
            _s(
                "Fix the first number. Once it is positive no triple can sum "
                "to zero, and repeats of it would give repeated answers.",
                "for i, first in enumerate(nums):\n    if first > 0:\n        break\n"
                "    if i > 0 and first == nums[i - 1]:\n        continue",
            ),
            _s(
                "The rest is two pointers looking for the negation of it.",
                "    left, right = i + 1, len(nums) - 1\n    while left < right:\n"
                "        total = first + nums[left] + nums[right]\n"
                "        if total < 0:\n            left += 1\n"
                "        elif total > 0:\n            right -= 1",
            ),
            _s(
                "On a hit, record it and then step past any repeat of the "
                "middle number, or the same triple comes out twice.",
                "        else:\n            out.append([first, nums[left], nums[right]])\n"
                "            left += 1\n"
                "            while left < right and nums[left] == nums[left - 1]:\n"
                "                left += 1\nreturn out",
            ),
        ),
    ),
    26: Worked(
        problem=26,
        naive=(
            "Build a new list of the distinct values, then copy it back over "
            "the original."
        ),
        why_not=(
            "The extra list is the whole thing the question is asking you to "
            "avoid, and copying back is a second pass for no gain."
        ),
        insight=(
            "Use two indexes into the same list: one reading ahead, one "
            "writing behind. The writer only moves when it has something new "
            "to write, so it is never ahead of the reader."
        ),
        stages=(
            _s(
                "The first element is always kept, so writing starts at one.",
                "if not nums:\n    return 0\nwrite = 1",
            ),
            _s(
                "Read across the rest, comparing against the last thing "
                "written rather than the previous element read.",
                "for read in range(1, len(nums)):\n"
                "    if nums[read] != nums[write - 1]:",
            ),
            _s(
                "A new value gets written and the writer advances. The count "
                "of distinct values is where the writer ended up.",
                "for read in range(1, len(nums)):\n"
                "    if nums[read] != nums[write - 1]:\n"
                "        nums[write] = nums[read]\n        write += 1\nreturn write",
            ),
        ),
    ),
    283: Worked(
        problem=283,
        naive=(
            "Whenever you find a zero, shift everything after it left by one."
        ),
        why_not=(
            "Each shift is a pass, so a list of all zeros does n passes: n "
            "squared work to move nothing anywhere useful."
        ),
        insight=(
            "Same read/write pair as removing duplicates. Write every "
            "non-zero forward in order, and then fill whatever is left with "
            "zeros — you never shift, you overwrite."
        ),
        stages=(
            _s(
                "The writer marks where the next non-zero belongs.",
                "write = 0",
            ),
            _s(
                "Every non-zero moves forward, keeping its relative order.",
                "write = 0\nfor read in range(len(nums)):\n"
                "    if nums[read] != 0:\n        nums[write] = nums[read]\n"
                "        write += 1",
            ),
            _s(
                "Everything from the writer on has already been copied "
                "forward, so it can be zeroed.",
                "for i in range(write, len(nums)):\n    nums[i] = 0\nreturn nums",
            ),
        ),
    ),
    42: Worked(
        problem=42,
        naive=(
            "For each column, scan left for the tallest wall and right for "
            "the tallest, and take the smaller of the two."
        ),
        why_not=(
            "Two scans per column is n squared, and it recomputes the same "
            "maxima again and again as it moves one step along."
        ),
        insight=(
            "Walk in from both ends carrying the tallest wall seen from that "
            "side. Whichever side has the SHORTER running maximum is the side "
            "whose answer is already decided — the other side has something "
            "at least that tall, so it cannot be the limit."
        ),
        stages=(
            _s(
                "A pointer and a running maximum from each end.",
                "left, right = 0, len(height) - 1\n"
                "left_max, right_max = height[left], height[right]\nwater = 0",
            ),
            _s(
                "Move whichever side has the lower wall. That is the side "
                "you can safely settle, and it is the whole argument.",
                "while left < right:\n    if left_max < right_max:",
            ),
            _s(
                "Step in, update that side's maximum, and the water above the "
                "new column is the maximum minus the column itself.",
                "        left += 1\n        left_max = max(left_max, height[left])\n"
                "        water += left_max - height[left]",
            ),
            _s(
                "The other side is the mirror image.",
                "    else:\n        right -= 1\n"
                "        right_max = max(right_max, height[right])\n"
                "        water += right_max - height[right]\nreturn water",
            ),
        ),
    ),
    977: Worked(
        problem=977,
        naive="Square every number and sort the result.",
        why_not=(
            "n log n, and the question hands you a sorted list, which usually "
            "means a linear answer exists."
        ),
        insight=(
            "Squaring makes the list V-shaped: smallest in the middle, "
            "largest at whichever end is furthest from zero. So the LARGEST "
            "square is always at one end or the other — fill the answer "
            "backwards."
        ),
        stages=(
            _s(
                "Room for the answer, and a pointer at each end of the input.",
                "out = [0] * len(nums)\nleft, right = 0, len(nums) - 1",
            ),
            _s(
                "Fill from the back, because the biggest is what you can "
                "identify with certainty.",
                "for slot in range(len(nums) - 1, -1, -1):",
            ),
            _s(
                "Whichever end is further from zero has the bigger square.",
                "    if abs(nums[left]) > abs(nums[right]):\n"
                "        out[slot] = nums[left] * nums[left]\n        left += 1\n"
                "    else:\n        out[slot] = nums[right] * nums[right]\n"
                "        right -= 1\nreturn out",
            ),
        ),
    ),
    # ── Sliding window ─────────────────────────────────────
    121: Worked(
        problem=121,
        naive="Try every buy day against every later sell day.",
        why_not=(
            "n squared, and every one of those comparisons is asking the same "
            "small question: what is the cheapest day so far?"
        ),
        insight=(
            "Selling today is only ever worth the cheapest price you have "
            "seen before today. Carry that one number and the second loop "
            "disappears."
        ),
        stages=(
            _s(
                "The cheapest day so far, and the best profit so far.",
                "cheapest = prices[0]\nbest = 0",
            ),
            _s(
                "For each day, the best you could do selling here.",
                "for price in prices[1:]:\n    best = max(best, price - cheapest)",
            ),
            _s(
                "Then update the cheapest for the days after. Best is seeded "
                "at zero because doing nothing is allowed.",
                "for price in prices[1:]:\n    best = max(best, price - cheapest)\n"
                "    cheapest = min(cheapest, price)\nreturn best",
            ),
        ),
    ),
    209: Worked(
        problem=209,
        naive="Try every start, extending until the sum reaches the target.",
        why_not=(
            "n squared in the worst case, and each restart throws away a sum "
            "that was almost entirely correct."
        ),
        insight=(
            "All the numbers are positive, so a longer window always sums to "
            "more. That means once the window qualifies you should shrink it "
            "from the left while it still qualifies — the answer is the "
            "smallest window you can shrink to."
        ),
        stages=(
            _s(
                "A left edge, a running sum, and an answer that starts "
                "impossible so any real one beats it.",
                "left = 0\ntotal = 0\nbest = len(nums) + 1",
            ),
            _s(
                "The right edge always advances, one number per turn.",
                "for right, n in enumerate(nums):\n    total += n",
            ),
            _s(
                "While the window is big enough, record it and shrink. A "
                "while, not an if: several shrinks may be possible at once.",
                "    while total >= target:\n"
                "        best = min(best, right - left + 1)\n"
                "        total -= nums[left]\n        left += 1",
            ),
            _s(
                "An untouched best means no window ever reached the target.",
                "return best if best <= len(nums) else 0",
            ),
        ),
    ),
    424: Worked(
        problem=424,
        naive=(
            "For each letter of the alphabet, find the longest window that "
            "becomes all that letter with at most k changes."
        ),
        why_not=(
            "Twenty-six passes is not the end of the world, and it is more "
            "work than one pass. It also hides the simpler statement of the "
            "problem."
        ),
        insight=(
            "A window is legal when its length minus its most common letter's "
            "count is at most k — that difference is exactly how many "
            "characters you would have to replace."
        ),
        stages=(
            _s(
                "Counts inside the window, and the left edge.",
                "counts = {}\nleft = 0\nbest = 0",
            ),
            _s(
                "Grow right and count the new character.",
                "for right, ch in enumerate(text):\n"
                "    counts[ch] = counts.get(ch, 0) + 1",
            ),
            _s(
                "Replacements needed is the window minus its commonest "
                "letter. While that is too many, shrink from the left.",
                "    while (right - left + 1) - max(counts.values()) > k:\n"
                "        counts[text[left]] -= 1\n        left += 1",
            ),
            _s(
                "Whatever survives is legal, so measure it.",
                "    best = max(best, right - left + 1)\nreturn best",
            ),
        ),
    ),
    643: Worked(
        problem=643,
        naive="Add up each window of k numbers from scratch.",
        why_not=(
            "Every window re-adds k numbers, so it is n times k. Neighbouring "
            "windows differ by exactly two numbers."
        ),
        insight=(
            "The window never changes size, so each step adds one number and "
            "drops one. And since the divisor is always k, the biggest "
            "average is just the biggest sum."
        ),
        stages=(
            _s(
                "Add the first window the slow way, once.",
                "window = sum(nums[:k])\nbest = window",
            ),
            _s(
                "Then slide: one number in at the right, one out at the left.",
                "for i in range(k, len(nums)):\n    window += nums[i] - nums[i - k]",
            ),
            _s(
                "Compare sums, and divide only at the end.",
                "for i in range(k, len(nums)):\n    window += nums[i] - nums[i - k]\n"
                "    best = max(best, window)\nreturn best / k",
            ),
        ),
    ),
    567: Worked(
        problem=567,
        naive=(
            "Generate every permutation of the pattern and search the text "
            "for each one."
        ),
        why_not=(
            "There are k factorial permutations. At ten characters that is "
            "three and a half million strings to search for."
        ),
        insight=(
            "You never need the permutations. A window is a permutation "
            "exactly when its letter counts match the pattern's — so slide a "
            "fixed-size window and compare counts."
        ),
        stages=(
            _s(
                "What the pattern needs.",
                "need = {}\nfor ch in pattern:\n    need[ch] = need.get(ch, 0) + 1",
            ),
            _s(
                "Slide a window of exactly the pattern's length.",
                "window = {}\nfor i, ch in enumerate(text):\n"
                "    window[ch] = window.get(ch, 0) + 1",
            ),
            _s(
                "Once it is too wide, drop the character falling off the "
                "left. Deleting at zero keeps the dicts comparable.",
                "    if i >= len(pattern):\n        out = text[i - len(pattern)]\n"
                "        window[out] -= 1\n        if window[out] == 0:\n"
                "            del window[out]",
            ),
            _s(
                "Matching counts is a permutation.",
                "    if window == need:\n        return True\nreturn False",
            ),
        ),
    ),
    1004: Worked(
        problem=1004,
        naive=(
            "Try every combination of k zeros to flip and measure the runs "
            "that result."
        ),
        why_not=(
            "The number of combinations explodes, and it treats the flips as "
            "the thing being chosen when really they are a consequence."
        ),
        insight=(
            "Restate it: the longest run of ones after k flips is the longest "
            "window containing at most k zeros. Nothing is flipped at all — "
            "you are just allowed that many."
        ),
        stages=(
            _s(
                "Count the zeros inside the window rather than flipping "
                "anything.",
                "left = 0\nzeros = 0\nbest = 0",
            ),
            _s(
                "Grow right, counting a zero as it comes in.",
                "for right in range(len(nums)):\n    if nums[right] == 0:\n"
                "        zeros += 1",
            ),
            _s(
                "Too many zeros means shrink from the left until it is legal.",
                "    while zeros > k:\n        if nums[left] == 0:\n"
                "            zeros -= 1\n        left += 1",
            ),
            _s(
                "Whatever survives the shrink is a legal window, so measure "
                "it before growing again.",
                "    best = max(best, right - left + 1)\nreturn best",
            ),
        ),
    ),
    76: Worked(
        problem=76,
        naive="Check every substring for containing all the needed letters.",
        why_not=(
            "There are n squared substrings and checking one costs its own "
            "length, so it is n cubed on a problem where n can be a hundred "
            "thousand."
        ),
        insight=(
            "Grow until the window is valid, then shrink while it stays "
            "valid, and repeat. To know 'valid' cheaply, count how many "
            "distinct required letters are fully satisfied rather than "
            "re-checking the whole dict."
        ),
        stages=(
            _s(
                "What is needed, and how many of those letters are still "
                "unsatisfied.",
                "need = {}\nfor ch in pattern:\n    need[ch] = need.get(ch, 0) + 1\n"
                "missing = len(need)",
            ),
            _s(
                "Grow right. A letter satisfies its requirement at the exact "
                "moment its count reaches what was needed — equality, not "
                "greater, or it counts twice.",
                "window = {}\nleft = 0\nbest = ''\n"
                "for right, ch in enumerate(text):\n"
                "    window[ch] = window.get(ch, 0) + 1\n"
                "    if ch in need and window[ch] == need[ch]:\n        missing -= 1",
            ),
            _s(
                "While nothing is missing, this window is an answer. Record "
                "it if it is the shortest so far, then shrink.",
                "    while missing == 0:\n"
                "        if not best or right - left + 1 < len(best):\n"
                "            best = text[left:right + 1]",
            ),
            _s(
                "Dropping a letter only breaks the window if it takes the "
                "count BELOW what was needed.",
                "        out = text[left]\n        window[out] -= 1\n"
                "        if out in need and window[out] < need[out]:\n"
                "            missing += 1\n        left += 1\nreturn best",
            ),
        ),
    ),
}


# The problem a pattern opens with. Every problem has its own lesson; this is
# the one that teaches the pattern itself rather than a variation on it, and
# it is what the Lessons screen shows first.
CANONICAL: dict[str, int] = {
    "lc-hashmap": 1,
    "lc-two-pointers": 167,
    "lc-sliding-window": 3,
    "lc-stack": 20,
    "lc-linked-list": 206,
    "lc-binary-search": 704,
    "lc-tree-dfs": 104,
    "lc-tree-bfs": 102,
    "lc-graph": 200,
    "lc-backtracking": 78,
    "lc-heap": 215,
    "lc-topological": 207,
    "lc-dp": 70,
}


def worked_for_problem(number: int | None) -> Worked | None:
    """The lesson for one problem."""
    if number is None:
        return None
    return WORKED.get(number)


def worked_for(pattern_id: str | None) -> Worked | None:
    """The lesson a pattern opens with."""
    if pattern_id is None:
        return None
    return WORKED.get(CANONICAL.get(pattern_id, -1))
