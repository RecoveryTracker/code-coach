"""
Study material: what each problem actually asks, and a lesson per pattern.

The problem text on leetcode.com is theirs, so nothing here is copied from it.
Every brief is an original restatement — what the problem asks, in plain words,
with a worked example. Each one links out to the real problem for the full
statement and the judge.

Kept separate from problems.py so the solution bank stays code + tests and this
stays prose. Briefs are keyed by LeetCode number (unique across the bank).
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field


def _t(text: str) -> str:
    return textwrap.dedent(text).strip("\n")


@dataclass(frozen=True)
class ProblemBrief:
    """What the question asks, in our own words."""

    slug: str
    statement: str
    examples: tuple[str, ...] = ()
    note: str = ""

    @property
    def url(self) -> str:
        return f"https://leetcode.com/problems/{self.slug}/"


@dataclass(frozen=True)
class PatternLesson:
    """The reading that makes a pattern's problems make sense."""

    summary: str
    when: str
    template: str
    steps: tuple[str, ...] = ()
    pitfalls: tuple[str, ...] = field(default_factory=tuple)


# ── Pattern lessons ─────────────────────────────────────────

LESSONS: dict[str, PatternLesson] = {
    "lc-hashmap": PatternLesson(
        summary=(
            "A dict or set remembers what you have already seen, so a question "
            "that looks like it needs a second loop becomes one lookup."
        ),
        when=(
            "You are about to write a nested loop to ask 'does a matching thing "
            "exist?' or 'how many times does this appear?'"
        ),
        template=_t(
            """
            seen = {}
            for i, item in enumerate(items):
                if <the thing I need> in seen:
                    return ...
                seen[item] = i
            """
        ),
        steps=(
            "Decide what question you keep asking inside the loop.",
            "Store whatever makes that question a single lookup.",
            "Check BEFORE you store, or an item can match itself.",
        ),
        pitfalls=(
            "Storing before checking — item pairs with itself.",
            "Using a list instead of a set: `in` on a list is O(n), which "
            "throws away the whole point.",
            "counts[ch] += 1 on a missing key raises KeyError. Use "
            "counts.get(ch, 0) + 1.",
        ),
    ),
    "lc-two-pointers": PatternLesson(
        summary=(
            "Two indexes move through the data instead of one, usually from "
            "opposite ends, turning an O(n^2) pair search into O(n)."
        ),
        when=(
            "The input is sorted, or the answer involves a pair, or you care "
            "about both ends of a range at once."
        ),
        template=_t(
            """
            left, right = 0, len(items) - 1
            while left < right:
                if <found it>:
                    return ...
                if <need a bigger value>:
                    left += 1
                else:
                    right -= 1
            """
        ),
        steps=(
            "Sort first if the problem does not hand you sorted data.",
            "Work out which pointer to move — that decision IS the algorithm.",
            "Make sure every branch moves a pointer, or you loop forever.",
        ),
        pitfalls=(
            "A branch that moves neither pointer — infinite loop.",
            "`while left <= right` when the two must not be the same item.",
            "Forgetting to skip duplicates when the answer must be unique.",
        ),
    ),
    "lc-sliding-window": PatternLesson(
        summary=(
            "Two pointers where the gap between them is the thing you are "
            "measuring. The right edge always advances; the left edge catches "
            "up only when the window breaks a rule."
        ),
        when=(
            "'Longest', 'shortest', or 'best' run of ADJACENT items that "
            "satisfies some condition."
        ),
        template=_t(
            """
            left = 0
            for right, item in enumerate(items):
                add item to the window
                while <window breaks the rule>:
                    remove items[left]
                    left += 1
                best = max(best, right - left + 1)
            """
        ),
        steps=(
            "Grow right unconditionally, once per loop.",
            "Shrink from the left only while the window is illegal.",
            "Record the answer after the window is legal again.",
        ),
        pitfalls=(
            "Recording `best` before shrinking, so an illegal window counts.",
            "Using `if` instead of `while` to shrink — one removal may not be "
            "enough.",
            "Contiguous vs not: subsequence problems are NOT sliding window.",
        ),
    ),
    "lc-stack": PatternLesson(
        summary=(
            "A list you only push to and pop from the end of. It remembers "
            "things in the reverse of the order they arrived."
        ),
        when=(
            "Matching pairs, undo, or 'the next bigger/smaller thing to the "
            "right' (a monotonic stack)."
        ),
        template=_t(
            """
            stack = []
            for item in items:
                while stack and <top of stack loses to item>:
                    resolved = stack.pop()
                    ...
                stack.append(item)
            """
        ),
        steps=(
            "Decide what goes on the stack — often an index, not a value.",
            "Decide what makes the top 'resolved' by the current item.",
            "Anything still on the stack at the end never got resolved.",
        ),
        pitfalls=(
            "Calling .pop() on an empty stack — always guard with `if stack`.",
            "Storing values when you need indexes to compute a distance.",
            "Forgetting to check the stack is empty at the end (unclosed "
            "brackets).",
        ),
    ),
    "lc-linked-list": PatternLesson(
        summary=(
            "Nodes joined by .next. You can only walk forward, and you only "
            "ever hold one node, so save anything you are about to overwrite."
        ),
        when="Reversing, merging, or finding a position relative to the end.",
        template=_t(
            """
            dummy = ListNode(0, head)
            prev, cur = dummy, head
            while cur:
                nxt = cur.next        # save before you break anything
                ...
                prev, cur = cur, nxt
            return dummy.next
            """
        ),
        steps=(
            "A dummy node in front means the first node needs no special case.",
            "Save .next BEFORE reassigning it, or you lose the rest.",
            "Two pointers at different speeds solve 'from the end' and cycles.",
        ),
        pitfalls=(
            "Overwriting cur.next before saving it — the tail is gone.",
            "Returning head instead of dummy.next when the head was removed.",
            "`while fast.next` without checking `fast` first — AttributeError.",
        ),
    ),
    "lc-binary-search": PatternLesson(
        summary=(
            "Halve the search space each step by asking one yes/no question. "
            "The hard part is never the halving — it is the boundaries."
        ),
        when=(
            "Sorted input, or 'smallest/largest value that works' over a range "
            "of numbers (binary search the answer, not the array)."
        ),
        template=_t(
            """
            low, high = 0, len(nums) - 1
            while low <= high:
                mid = (low + high) // 2
                if nums[mid] == target:
                    return mid
                if nums[mid] < target:
                    low = mid + 1
                else:
                    high = mid - 1
            return -1
            """
        ),
        steps=(
            "Pick your range style and keep it: closed [low, high] with "
            "`while low <= high`, or half-open [low, high) with `while low < high`.",
            "Every branch must exclude mid, or the loop never ends.",
            "When searching for a boundary, return `low` — not mid.",
        ),
        pitfalls=(
            "Mixing the two range styles in one function.",
            "`high = mid` in a closed-range loop — infinite when high == low + 1.",
            "Assuming the answer is at mid when you wanted the first/last match.",
        ),
    ),
    "lc-tree-dfs": PatternLesson(
        summary=(
            "Recursion that solves the children first, then combines their "
            "answers into this node's answer."
        ),
        when=(
            "The answer for a node can be built from the answers for its two "
            "subtrees."
        ),
        template=_t(
            """
            def solve(node):
                if not node:
                    return <base case>
                left = solve(node.left)
                right = solve(node.right)
                return <combine left, right, node.val>
            """
        ),
        steps=(
            "Write the base case first — usually `if not node`.",
            "Trust the recursion: assume the children return correct answers.",
            "When you need to return one thing but track another, use a "
            "`nonlocal` variable (see Diameter).",
        ),
        pitfalls=(
            "Missing the `if not node` guard — AttributeError on None.",
            "Checking only parent vs child for BSTs; you must carry a range "
            "down (see Validate BST).",
            "Confusing what you RETURN with what you RECORD.",
        ),
    ),
    "lc-tree-bfs": PatternLesson(
        summary=(
            "A queue visits the tree level by level instead of branch by "
            "branch."
        ),
        when="The question mentions levels, rows, depth order, or 'nearest'.",
        template=_t(
            """
            queue = deque([root])
            while queue:
                for _ in range(len(queue)):     # snapshot = one level
                    node = queue.popleft()
                    ...
                    if node.left:
                        queue.append(node.left)
                    if node.right:
                        queue.append(node.right)
            """
        ),
        steps=(
            "Guard the empty tree before you start.",
            "Take len(queue) BEFORE the inner loop — that count is one level.",
            "Everything you append lands in the next level, not this one.",
        ),
        pitfalls=(
            "Calling len(queue) inside the loop condition — it changes as you "
            "append, and levels smear together.",
            "Using a list with .pop(0) instead of deque.popleft() — O(n) each.",
            "Forgetting `if not root: return []`.",
        ),
    ),
    "lc-graph": PatternLesson(
        summary=(
            "The same DFS/BFS as trees, but graphs have cycles, so you must "
            "mark things visited or you loop forever."
        ),
        when="A grid of cells, or nodes with edges/neighbours.",
        template=_t(
            """
            def dfs(r, c):
                if r < 0 or r >= rows or c < 0 or c >= cols:
                    return
                if <not the thing we are filling>:
                    return
                mark grid[r][c] as visited
                dfs(r + 1, c)
                dfs(r - 1, c)
                dfs(r, c + 1)
                dfs(r, c - 1)
            """
        ),
        steps=(
            "Bounds check first, then the 'is this a match' check.",
            "Mark visited BEFORE recursing, not after.",
            "DFS for 'how big / is it connected', BFS for 'how many steps'.",
        ),
        pitfalls=(
            "No visited marking — infinite recursion.",
            "Marking after the recursive calls, which is too late.",
            "Comparing to 1 when the grid holds the string \"1\".",
        ),
    ),
    "lc-backtracking": PatternLesson(
        summary=(
            "Choose, recurse, un-choose. You walk a tree of decisions, and "
            "undoing each choice on the way out is what makes it correct."
        ),
        when="'All subsets / permutations / combinations that ...'",
        template=_t(
            """
            def backtrack(start):
                if <this branch is complete>:
                    result.append(current[:])
                    return
                for i in range(start, len(items)):
                    current.append(items[i])
                    backtrack(i + 1)
                    current.pop()          # un-choose
            """
        ),
        steps=(
            "Append a COPY (current[:]) — otherwise every result is the same "
            "list, and it ends up empty.",
            "`i + 1` means each item is used once; `i` means reuse allowed.",
            "Sort first when the input has duplicates, then skip repeats at "
            "the same level with `if i > start and items[i] == items[i - 1]`.",
        ),
        pitfalls=(
            "result.append(current) without [:] — all entries alias one list.",
            "Forgetting current.pop(), so choices leak into sibling branches.",
            "Skipping duplicates with `i > 0` instead of `i > start`, which "
            "wrongly drops valid picks.",
        ),
    ),
    "lc-heap": PatternLesson(
        summary=(
            "A heap keeps the smallest item instantly reachable. Holding only "
            "k items answers 'top k' without sorting everything."
        ),
        when="'K largest', 'K closest', 'K most frequent'.",
        template=_t(
            """
            heap = []
            for item in items:
                heapq.heappush(heap, key(item))
                if len(heap) > k:
                    heapq.heappop(heap)     # drop the worst survivor
            """
        ),
        steps=(
            "For the k LARGEST, keep a MIN-heap of size k — the root is your "
            "answer and the weakest to evict.",
            "Push a tuple to sort by something other than the value itself; "
            "the first element decides order.",
            "Negate the key when you need max-heap behaviour.",
        ),
        pitfalls=(
            "Using a max-heap for 'k largest' — then you cannot cheaply evict.",
            "Tuples whose later fields are not comparable, e.g. a dict as a "
            "tiebreaker: TypeError when counts tie.",
            "Popping before the size check, which can empty the heap.",
        ),
    ),
    "lc-topological": PatternLesson(
        summary=(
            "Repeatedly take whatever has no unmet prerequisites. If you get "
            "stuck before taking everything, there is a cycle."
        ),
        when="Dependencies, ordering, 'can this schedule be completed?'",
        template=_t(
            """
            graph = {i: [] for i in range(n)}
            indegree = [0] * n
            for after, before in pairs:
                graph[before].append(after)
                indegree[after] += 1

            queue = deque([i for i in range(n) if indegree[i] == 0])
            order = []
            while queue:
                node = queue.popleft()
                order.append(node)
                for nxt in graph[node]:
                    indegree[nxt] -= 1
                    if indegree[nxt] == 0:
                        queue.append(nxt)
            """
        ),
        steps=(
            "Build the graph edge-direction FIRST — getting it backwards is "
            "the usual bug.",
            "Seed the queue with every indegree-0 node, not just one.",
            "len(order) < n means a cycle: impossible schedule.",
        ),
        pitfalls=(
            "Reversing the edge direction — the pair order is easy to misread.",
            "Only queueing one starting node.",
            "Forgetting the final length check, so a cycle returns a partial "
            "order as if it succeeded.",
        ),
    ),
    "lc-dp": PatternLesson(
        summary=(
            "Solve each small case once, store it, and build the big answer "
            "from stored answers instead of recomputing them."
        ),
        when=(
            "The obvious recursion recomputes the same subproblem over and "
            "over — 'overlapping subproblems'."
        ),
        template=_t(
            """
            best = [<worst value>] * (n + 1)
            best[0] = <base case>
            for i in range(1, n + 1):
                for choice in choices:
                    if choice fits in i:
                        best[i] = min(best[i], best[i - choice] + 1)
            return best[n]
            """
        ),
        steps=(
            "Say out loud what best[i] MEANS. Every bug starts here.",
            "Write the base case, then the rule linking i to smaller i.",
            "If you only ever look back one or two slots, drop the array and "
            "keep two variables (see Climbing Stairs).",
        ),
        pitfalls=(
            "A sentinel like `amount + 1` that you forget to convert back to "
            "-1 at the end.",
            "Off-by-one in the array size — you usually need n + 1 slots.",
            "Looping in an order where best[i - choice] is not computed yet.",
        ),
    ),
}


# ── Problem briefs ──────────────────────────────────────────


def _b(
    slug: str,
    statement: str,
    *examples: str,
    note: str = "",
) -> ProblemBrief:
    return ProblemBrief(
        slug=slug, statement=_t(statement), examples=examples, note=note
    )


BRIEFS: dict[int, ProblemBrief] = {
    # Hash maps
    1: _b(
        "two-sum",
        "Given a list of numbers and a target, return the indexes of the two "
        "numbers that add up to the target. Exactly one pair works, and you "
        "cannot use the same element twice.",
        "nums = [2, 7, 11, 15], target = 9  ->  [0, 1]",
        "nums = [3, 2, 4], target = 6  ->  [1, 2]",
        note="The answer is indexes, not the values themselves.",
    ),
    217: _b(
        "contains-duplicate",
        "Return True if any value appears at least twice in the list, and "
        "False if every value is distinct.",
        "nums = [1, 2, 3, 1]  ->  True",
        "nums = [1, 2, 3, 4]  ->  False",
    ),
    242: _b(
        "valid-anagram",
        "Given two strings, return True if one is a rearrangement of the "
        "other — same letters, same counts, different order.",
        's = "anagram", t = "nagaram"  ->  True',
        's = "rat", t = "car"  ->  False',
        note="Different lengths can never be anagrams — check that first.",
    ),
    49: _b(
        "group-anagrams",
        "Given a list of words, group together the ones that are "
        "rearrangements of each other. Return the groups in any order.",
        '["eat","tea","tan","ate","nat","bat"]  ->  '
        '[["eat","tea","ate"], ["tan","nat"], ["bat"]]',
        note="You need a key that all anagrams share — sorted letters works.",
    ),
    # Two pointers
    125: _b(
        "valid-palindrome",
        "Return True if the string reads the same forwards and backwards, "
        "counting only letters and digits and ignoring case.",
        's = "A man, a plan, a canal: Panama"  ->  True',
        's = "race a car"  ->  False',
        note="Punctuation and spaces are skipped, not treated as mismatches.",
    ),
    167: _b(
        "two-sum-ii-input-array-is-sorted",
        "Same as Two Sum, but the list is already sorted and the answer is "
        "1-based indexes rather than 0-based.",
        "numbers = [2, 7, 11, 15], target = 9  ->  [1, 2]",
        note="Sorted input is the hint: two pointers, no dict needed.",
    ),
    11: _b(
        "container-with-most-water",
        "Each number is the height of a vertical line. Pick two lines so that "
        "the container they form holds the most water. Area is the shorter "
        "line times the distance between them.",
        "height = [1,8,6,2,5,4,8,3,7]  ->  49",
        note="Moving the taller wall can never help — the short one caps you.",
    ),
    15: _b(
        "3sum",
        "Find every unique triple in the list that sums to zero. No triple "
        "may be repeated in the output.",
        "nums = [-1, 0, 1, 2, -1, -4]  ->  [[-1, -1, 2], [-1, 0, 1]]",
        note="Uniqueness is the whole difficulty — sort, then skip duplicates.",
    ),
    # Sliding window
    121: _b(
        "best-time-to-buy-and-sell-stock",
        "Each number is the stock price on that day. Buy on one day and sell "
        "on a later day for the largest profit. If no profit is possible, "
        "return 0.",
        "prices = [7, 1, 5, 3, 6, 4]  ->  5   (buy at 1, sell at 6)",
        "prices = [7, 6, 4, 3, 1]  ->  0",
        note="You must sell AFTER you buy — order matters.",
    ),
    3: _b(
        "longest-substring-without-repeating-characters",
        "Find the length of the longest run of consecutive characters that "
        "contains no repeats.",
        's = "abcabcbb"  ->  3   ("abc")',
        's = "pwwkew"  ->  3   ("wke")',
        note="Substring means contiguous. \"pwke\" is a subsequence, not valid.",
    ),
    209: _b(
        "minimum-size-subarray-sum",
        "Find the length of the shortest run of consecutive numbers whose sum "
        "is at least the target. Return 0 if no run qualifies.",
        "target = 7, nums = [2, 3, 1, 2, 4, 3]  ->  2   ([4, 3])",
        note="Shortest, not longest — you shrink whenever the window qualifies.",
    ),
    424: _b(
        "longest-repeating-character-replacement",
        "You may change at most k characters in the string. Find the longest "
        "run of consecutive identical characters you can produce.",
        's = "AABABBA", k = 1  ->  4',
        note=(
            "A window is legal when (its size - the most common letter in it) "
            "<= k."
        ),
    ),
    # Stack
    20: _b(
        "valid-parentheses",
        "Given a string of brackets — (), [], {} — return True if every one is "
        "closed by the matching type in the right order.",
        's = "()[]{}"  ->  True',
        's = "(]"  ->  False',
        note="\"([)]\" is False: correct counts, wrong nesting.",
    ),
    155: _b(
        "min-stack",
        "Build a stack supporting push, pop, top, and getMin — where getMin "
        "returns the smallest value currently on the stack in constant time.",
        "push(-2), push(0), push(-3), getMin() -> -3, pop(), getMin() -> -2",
        note="Scanning for the min would be O(n). Track it as you push.",
    ),
    150: _b(
        "evaluate-reverse-polish-notation",
        "Evaluate an expression in postfix notation, where each operator "
        "follows its two operands.",
        '["2","1","+","3","*"]  ->  9   ((2 + 1) * 3)',
        note=(
            "Division truncates toward zero, so -7 / 2 is -3, not -4. That is "
            "int(a / b), not a // b."
        ),
    ),
    739: _b(
        "daily-temperatures",
        "For each day, how many days until a warmer one? Put 0 where no "
        "warmer day ever comes.",
        "[73,74,75,71,69,72,76,73]  ->  [1,1,4,2,1,1,0,0]",
        note="Stack holds INDEXES — you need them to compute the gap.",
    ),
    # Linked list
    206: _b(
        "reverse-linked-list",
        "Reverse a singly linked list and return the new head.",
        "1 -> 2 -> 3 -> 4 -> 5   becomes   5 -> 4 -> 3 -> 2 -> 1",
        note="Three cursors: previous, current, and the saved next.",
    ),
    21: _b(
        "merge-two-sorted-lists",
        "Given two sorted linked lists, splice them into one sorted list and "
        "return its head.",
        "[1,2,4] and [1,3,4]  ->  [1,1,2,3,4,4]",
        note="A dummy head removes the 'which list starts it' special case.",
    ),
    141: _b(
        "linked-list-cycle",
        "Return True if the linked list loops back on itself, False if it "
        "ends normally.",
        "3 -> 2 -> 0 -> -4, with -4 pointing back at 2  ->  True",
        note="Slow and fast pointers meet inside a loop. O(1) memory.",
    ),
    19: _b(
        "remove-nth-node-from-end-of-list",
        "Remove the nth node counting from the END of the list, and return "
        "the head.",
        "[1,2,3,4,5], n = 2  ->  [1,2,3,5]",
        note="Start fast n ahead; when it hits the end, slow is in position.",
    ),
    # Binary search
    704: _b(
        "binary-search",
        "Find the index of a target in a sorted list, or -1 if it is absent.",
        "nums = [-1,0,3,5,9,12], target = 9  ->  4",
        note="The plain version — get the boundaries right here first.",
    ),
    35: _b(
        "search-insert-position",
        "Return the index of the target in a sorted list, or the index where "
        "it would be inserted to keep the list sorted.",
        "nums = [1,3,5,6], target = 2  ->  1",
        "nums = [1,3,5,6], target = 7  ->  4",
        note="A boundary search: return low, and never return mid.",
    ),
    153: _b(
        "find-minimum-in-rotated-sorted-array",
        "A sorted list was rotated at some unknown point. Find its smallest "
        "value in O(log n).",
        "nums = [4,5,6,7,0,1,2]  ->  0",
        note="Compare mid against the RIGHT end to learn which half has the dip.",
    ),
    33: _b(
        "search-in-rotated-sorted-array",
        "A sorted list was rotated at an unknown point. Find a target's index "
        "in O(log n), or -1.",
        "nums = [4,5,6,7,0,1,2], target = 0  ->  4",
        note="One half is always properly sorted — identify it, then decide.",
    ),
    875: _b(
        "koko-eating-bananas",
        "Given piles of bananas and h hours, find the slowest eating speed "
        "(bananas per hour) that still finishes every pile in time. A pile is "
        "never shared across hours.",
        "piles = [3,6,7,11], h = 8  ->  4",
        note=(
            "You binary search the ANSWER (a speed from 1 to max(piles)), not "
            "the array."
        ),
    ),
    # Tree DFS
    104: _b(
        "maximum-depth-of-binary-tree",
        "Return the number of nodes on the longest path from the root down to "
        "a leaf.",
        "[3,9,20,null,null,15,7]  ->  3",
        note="The gentlest possible recursion — start here.",
    ),
    226: _b(
        "invert-binary-tree",
        "Mirror the tree: every node's left and right children swap.",
        "[4,2,7,1,3,6,9]  ->  [4,7,2,9,6,3,1]",
    ),
    112: _b(
        "path-sum",
        "Return True if some root-to-leaf path has values adding up exactly "
        "to the target.",
        "[5,4,8,11,null,13,4,7,2], target = 22  ->  True",
        note="Must end at a LEAF — stopping halfway does not count.",
    ),
    543: _b(
        "diameter-of-binary-tree",
        "Return the number of edges on the longest path between any two "
        "nodes. That path does not have to pass through the root.",
        "[1,2,3,4,5]  ->  3",
        note=(
            "The classic 'return one thing, record another': return depth "
            "upward while recording left + right."
        ),
    ),
    98: _b(
        "validate-binary-search-tree",
        "Return True if the tree is a valid BST: everything in a node's left "
        "subtree is smaller, everything right is larger, all the way down.",
        "[2,1,3]  ->  True",
        "[5,1,4,null,null,3,6]  ->  False",
        note=(
            "Comparing only parent and child is the classic wrong answer — a "
            "deep node can violate an ancestor. Carry a (low, high) range down."
        ),
    ),
    # Tree BFS
    102: _b(
        "binary-tree-level-order-traversal",
        "Return the node values level by level, top to bottom, each level as "
        "its own list.",
        "[3,9,20,null,null,15,7]  ->  [[3], [9,20], [15,7]]",
        note="len(queue) before the inner loop is exactly one level.",
    ),
    199: _b(
        "binary-tree-right-side-view",
        "Standing to the right of the tree, return the values you can see — "
        "the last node of each level, top to bottom.",
        "[1,2,3,null,5,null,4]  ->  [1, 3, 4]",
        note="Not the same as 'all right children' — a left child can be visible.",
    ),
    103: _b(
        "binary-tree-zigzag-level-order-traversal",
        "Level order, but alternating direction: first level left to right, "
        "the next right to left, and so on.",
        "[3,9,20,null,null,15,7]  ->  [[3], [20,9], [15,7]]",
        note="Walk normally and reverse every other row — do not reverse the queue.",
    ),
    # Graph
    733: _b(
        "flood-fill",
        "Starting at one pixel, repaint it and every connected pixel of the "
        "same original colour (up/down/left/right) with a new colour.",
        "image = [[1,1,1],[1,1,0],[1,0,1]], start (1,1), colour 2  ->  "
        "[[2,2,2],[2,2,0],[2,0,1]]",
        note=(
            "If the new colour equals the old one, return immediately or you "
            "recurse forever."
        ),
    ),
    200: _b(
        "number-of-islands",
        "A grid of '1' (land) and '0' (water). Count the islands — groups of "
        "land connected horizontally or vertically.",
        '[["1","1","0"],["1","1","0"],["0","0","1"]]  ->  2',
        note="The cells are STRINGS \"1\"/\"0\", not integers.",
    ),
    994: _b(
        "rotting-oranges",
        "In a grid, 2 is a rotten orange, 1 is fresh, 0 is empty. Each minute "
        "rot spreads to adjacent fresh oranges. Return the minutes until none "
        "are fresh, or -1 if some can never rot.",
        "[[2,1,1],[1,1,0],[0,1,1]]  ->  4",
        note=(
            "Multi-source BFS: every rotten orange starts in the queue at "
            "minute zero."
        ),
    ),
    133: _b(
        "clone-graph",
        "Return a deep copy of a connected undirected graph — every node and "
        "edge duplicated, sharing nothing with the original.",
        "1—2, 2—1  ->  an identical but entirely separate pair",
        note="A dict from original node to copy doubles as the visited set.",
    ),
    # Backtracking
    78: _b(
        "subsets",
        "Return every possible subset of a list of distinct numbers, "
        "including the empty one. Any order.",
        "[1,2,3]  ->  [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]",
        note="n items produce 2^n subsets — include or exclude each one.",
    ),
    90: _b(
        "subsets-ii",
        "Same as Subsets, but the input may contain duplicates and the output "
        "must not repeat a subset.",
        "[1,2,2]  ->  [[], [1], [1,2], [1,2,2], [2], [2,2]]",
        note="Sort first, then skip a repeat unless it is the first pick here.",
    ),
    46: _b(
        "permutations",
        "Return every ordering of a list of distinct numbers.",
        "[1,2,3]  ->  6 orderings, from [1,2,3] to [3,2,1]",
        note="Order matters here, so you track which items are already used.",
    ),
    39: _b(
        "combination-sum",
        "Given distinct candidates and a target, find every combination that "
        "sums to the target. Each candidate may be reused any number of times.",
        "candidates = [2,3,6,7], target = 7  ->  [[2,2,3], [7]]",
        note="Reuse allowed means you recurse with i, not i + 1.",
    ),
    79: _b(
        "word-search",
        "Given a grid of letters, return True if a word can be spelled by "
        "walking to adjacent cells. A cell cannot be reused within one word.",
        '[["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], '
        '"ABCCED"  ->  True',
        note=(
            "Blank the cell out before recursing and restore it after — that "
            "restore is the backtracking."
        ),
    ),
    # Heap
    215: _b(
        "kth-largest-element-in-an-array",
        "Return the kth largest value in the list — by rank, not the kth "
        "distinct value.",
        "nums = [3,2,1,5,6,4], k = 2  ->  5",
        note="Duplicates still occupy a rank each.",
    ),
    347: _b(
        "top-k-frequent-elements",
        "Return the k values that appear most often, in any order.",
        "nums = [1,1,1,2,2,3], k = 2  ->  [1, 2]",
        note="Count first, then heap the counts — two distinct phases.",
    ),
    973: _b(
        "k-closest-points-to-origin",
        "Given points on a plane, return the k nearest to (0, 0).",
        "[[1,3],[-2,2]], k = 1  ->  [[-2,2]]",
        note="Compare x*x + y*y — no need for the square root.",
    ),
    # Topological sort
    207: _b(
        "course-schedule",
        "Given a number of courses and a list of prerequisite pairs, return "
        "True if you can finish all of them.",
        "2 courses, [[1,0]]  ->  True   (take 0, then 1)",
        "2 courses, [[1,0],[0,1]]  ->  False   (circular)",
        note=(
            "The pair [a, b] means: to take a you must first take b. Getting "
            "this backwards is the usual bug."
        ),
    ),
    210: _b(
        "course-schedule-ii",
        "Same setup, but return an actual valid order to take the courses, or "
        "an empty list if it is impossible.",
        "4 courses, [[1,0],[2,0],[3,1],[3,2]]  ->  [0,1,2,3]",
        note="Any valid order is accepted, not one specific answer.",
    ),
    310: _b(
        "minimum-height-trees",
        "Given a tree as edges, find every node that would give the shortest "
        "tree if you rooted it there. There are always one or two.",
        "n = 4, edges = [[1,0],[1,2],[1,3]]  ->  [1]",
        note=(
            "Peel leaves layer by layer, like indegree peeling. Whatever "
            "survives is the centre."
        ),
    ),
    # DP
    70: _b(
        "climbing-stairs",
        "You climb 1 or 2 steps at a time. How many distinct ways can you "
        "reach step n?",
        "n = 2  ->  2   (1+1, 2)",
        "n = 3  ->  3   (1+1+1, 1+2, 2+1)",
        note="Ways(n) = ways(n-1) + ways(n-2). It is Fibonacci in disguise.",
    ),
    198: _b(
        "house-robber",
        "Each number is the money in a house along a street. You cannot rob "
        "two adjacent houses. Return the most you can take.",
        "[1,2,3,1]  ->  4   (houses 1 and 3)",
        "[2,7,9,3,1]  ->  12   (2 + 9 + 1)",
        note="Greedy fails — [2,7,9] shows why taking the biggest first loses.",
    ),
    322: _b(
        "coin-change",
        "Given coin denominations and an amount, return the fewest coins that "
        "make that amount, or -1 if it cannot be made. Unlimited coins.",
        "coins = [1,2,5], amount = 11  ->  3   (5 + 5 + 1)",
        "coins = [2], amount = 3  ->  -1",
        note="Taking the largest coin first is wrong: coins=[1,3,4], amount=6.",
    ),
    300: _b(
        "longest-increasing-subsequence",
        "Return the length of the longest strictly increasing subsequence. "
        "Items need not be adjacent, but must keep their order.",
        "[10,9,2,5,3,7,101,18]  ->  4   ([2,3,7,101])",
        note=(
            "Subsequence, not substring — gaps are fine. The O(n log n) "
            "version binary searches a 'tails' list."
        ),
    ),
}


# ── Lookup ──────────────────────────────────────────────────


"""Runnable calls for problems whose examples can't be parsed into one.

The visualiser derives a call from the worked example, which works when the
example is literal data (`nums = [2, 7, 11, 15], target = 9`). It can't work
when the input is a *structure* — a tree written as `[3,9,20,null,null,15,7]`,
a linked list written as `[1,2,4]`, or a class you're meant to poke at. Those
need building, so they're written out here.

Without these the visualiser either showed nothing or, worse, guessed a call
like `reverse_list(1)` that crashed. Each one uses the classes that problem's
pattern already defines in its preamble.
"""

_LIST_3 = "ListNode(1, ListNode(2, ListNode(3)))"
# 4 / 2 7 / 1 3 6 9 — a full, balanced tree that's also a valid BST.
_TREE_7 = (
    "TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), "
    "TreeNode(7, TreeNode(6), TreeNode(9)))"
)

DEMO_CALLS: dict[int, str] = {
    # Linked lists — the example shows values, not nodes.
    206: f"reverse_list({_LIST_3})",
    21: "merge_two_lists(ListNode(1, ListNode(2, ListNode(4))), "
        "ListNode(1, ListNode(3, ListNode(4))))",
    141: "has_cycle(ListNode(3, ListNode(2, ListNode(0))))",
    19: f"remove_nth_from_end({_LIST_3}, 2)",
    876: f"middle_node({_LIST_3})",
    83: "delete_duplicates(ListNode(1, ListNode(1, ListNode(2))))",
    234: "is_palindrome_list(ListNode(1, ListNode(2, ListNode(1))))",
    2: (
        "add_two_numbers(ListNode(2, ListNode(4, ListNode(3))), "
        "ListNode(5, ListNode(6, ListNode(4))))"
    ),
    # Trees — the example is level-order with nulls, not constructor calls.
    104: f"max_depth({_TREE_7})",
    226: f"invert_tree({_TREE_7})",
    112: "has_path_sum(TreeNode(5, TreeNode(4, TreeNode(11)), TreeNode(8)), 20)",
    543: f"diameter_of_binary_tree({_TREE_7})",
    98: f"is_valid_bst({_TREE_7})",
    100: f"is_same_tree({_TREE_7}, {_TREE_7})",
    101: "is_symmetric(TreeNode(1, TreeNode(2, TreeNode(3)), "
        "TreeNode(2, None, TreeNode(3))))",
    236: (
        "root = " + _TREE_7 + "\n"
        "meeting = lowest_common_ancestor(root, root.left, root.right)"
    ),
    102: f"level_order({_TREE_7})",
    199: f"right_side_view({_TREE_7})",
    103: f"zigzag_level_order({_TREE_7})",
    111: f"min_depth({_TREE_7})",
    637: f"average_of_levels({_TREE_7})",
    515: f"largest_values({_TREE_7})",
    1161: f"max_level_sum({_TREE_7})",
    662: f"width_of_binary_tree({_TREE_7})",
    # Grids and graphs.
    733: "flood_fill([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2)",
    133: "clone_graph(Node(1, [Node(2)]))",
    695: "max_area_of_island([[0, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]])",
    547: "find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]])",
    542: "update_matrix([[0, 0, 0], [0, 1, 0], [1, 1, 1]])",
    417: (
        "pacific_atlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4], "
        "[2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]])"
    ),
    77: "combine(4, 2)",
    17: 'letter_combinations("23")',
    131: 'partition("aab")',
    746: "min_cost_climbing_stairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])",
    1143: 'longest_common_subsequence("abcde", "ace")',
    139: 'word_break("leetcode", ["leet", "code"])',
    152: "max_product([2, 3, -2, 4])",
    973: "k_closest([[1, 3], [-2, 2], [5, 8], [0, 1]], 2)",
    # Arrays plus a second argument the example prose can't be parsed into.
    560: "subarray_sum([1, 2, 3], 3)",
    128: "longest_consecutive([100, 4, 200, 1, 3, 2])",
    36: 'is_valid_sudoku([["." for _ in range(9)] for _ in range(9)])',
    26: "remove_duplicates([0, 0, 1, 1, 1, 2, 2, 3, 3, 4])",
    682: 'cal_points(["5", "2", "C", "D", "+"])',
    71: 'simplify_path("/a/./b/../../c/")',
    84: "largest_rectangle_area([2, 1, 5, 6, 2, 3])",
    394: 'decode_string("3[a2[c]]")',
    34: "search_range([5, 7, 7, 8, 8, 10], 8)",
    # Takes a predicate, which no example prose can be parsed into.
    278: "first_bad_version(5, lambda v: v >= 4)",
    74: "search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3)",
    454: "four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2])",
    283: "move_zeroes([0, 1, 0, 3, 12])",
    42: "trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])",
    977: "sorted_squares([-4, -1, 0, 3, 10])",
    643: "find_max_average([1, 12, -5, -6, 50, 3], 4)",
    567: 'check_inclusion("ab", "eidbaooo")',
    1004: "longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)",
    76: 'min_window("ADOBECODEBANC", "ABC")',
    # Heaps — a bare list literal reads fine, but the k has to come from
    # somewhere, and the example prose isn't parseable into one.
    1046: "last_stone_weight([2, 7, 4, 1, 8, 1])",
    692: 'top_k_frequent_words(["i", "love", "leetcode", "i", "love", "coding"], 2)',
    451: 'frequency_sort("tree")',
    378: "kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8)",
    767: 'reorganize_string("aab")',
    # Counts plus edge lists — prose in the example, not a literal.
    207: "can_finish(2, [[1, 0]])",
    210: "find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])",
    802: "eventual_safe_nodes([[1, 2], [2, 3], [5], [0], [5], [], []])",
    1462: "check_if_prerequisite(3, [[0, 1], [1, 2]], [[0, 2], [2, 0]])",
    2115: (
        'find_all_recipes(["bread", "sandwich"], '
        '[["yeast", "flour"], ["bread", "meat"]], '
        '["yeast", "flour", "meat"])'
    ),
    1136: "minimum_semesters(3, [[1, 3], [2, 3]])",
    269: 'alien_order(["wrt", "wrf", "er", "ett", "rftt"])',
    # A class, so exercise it rather than calling one function.
    155: (
        "s = MinStack()\n"
        "s.push(-2)\n"
        "s.push(0)\n"
        "s.push(-3)\n"
        "smallest = s.get_min()\n"
        "s.pop()\n"
        "smallest = s.get_min()"
    ),
}


def demo_call_for(number: int | None) -> str:
    """A hand-written call for problems the example can't produce one for."""
    if number is None:
        return ""
    return DEMO_CALLS.get(number, "")


def brief_for(number: int) -> ProblemBrief | None:
    return BRIEFS.get(number)


def lesson_for(pattern_id: str) -> PatternLesson | None:
    return LESSONS.get(pattern_id)
