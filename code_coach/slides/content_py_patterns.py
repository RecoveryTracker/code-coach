"""Python Patterns: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 30

DECK = Deck(
    id="py-patterns",
    title="Python Patterns",
    language="python",
    blurb="Small moves you will use again and again: accumulating, counting, searching, pairing, stacks, queues, windows and caching.",
    slides=(
        Slide(
            title="Accumulator",
            text="Start a variable at zero, then add to it as you loop. When the loop ends it holds the running total.",
            code=r"""total = 0
for n in [4, 8, 15]:
    total += n
print(total)""",
            output="27",
            point="Start with a neutral value, update it each round.",
        ),
        Slide(
            title="Counting with a dict",
            text="Use each item as a key and its count as the value. .get(key, 0) gives 0 the first time you see something new.",
            code=r"""counts = {}
for ch in "banana":
    counts[ch] = counts.get(ch, 0) + 1
print(counts)""",
            output="{'b': 1, 'a': 3, 'n': 2}",
            point="counts[x] = counts.get(x, 0) + 1",
        ),
        Slide(
            title="Counting with Counter",
            text="collections.Counter does that counting for you. It also knows how to list the most common items.",
            code=r"""from collections import Counter
counts = Counter("banana")
print(counts["a"])
print(counts.most_common(1))""",
            output="3\n[('a', 3)]",
            point="Counter(items) is the counting pattern in one call.",
        ),
        Slide(
            title="Finding the biggest",
            text="By hand: keep the best so far and replace it when you see something better. Or let max() do it, with key= saying what 'bigger' means.",
            code=r"""words = ["fig", "banana", "kiwi"]
best = words[0]
for w in words:
    if len(w) > len(best):
        best = w
print(best)
print(max(words, key=len))""",
            output="banana\nbanana",
            point="max(items, key=...) replaces the hand-written loop.",
        ),
        Slide(
            title="Filter and map in one line",
            text="A comprehension can keep only some items (filter) and change each one (map) at the same time.",
            code=r"""nums = [1, 2, 3, 4, 5, 6]
print([n * n for n in nums if n % 2 == 0])""",
            output="[4, 16, 36]",
            point="[change(x) for x in items if keep(x)]",
        ),
        Slide(
            title="enumerate and zip",
            text="enumerate gives each item with its position. zip walks two lists side by side, pairing up items at the same position.",
            code=r"""names = ["ann", "bo"]
ages = [30, 25]
for i, name in enumerate(names):
    print(i, name)
for name, age in zip(names, ages):
    print(name, age)""",
            output="0 ann\n1 bo\nann 30\nbo 25",
            point="Never write range(len(x)) just to get an index.",
        ),
        Slide(
            title="Guard clause",
            text="Handle the odd or empty case first and return straight away. The rest of the function can then assume the normal case.",
            code=r"""def first_word(text):
    if not text:
        return "(empty)"
    return text.split()[0]

print(first_word(""))
print(first_word("hello world"))""",
            output="(empty)\nhello",
            point="Return early instead of nesting deeper.",
        ),
        Slide(
            title="Dict dispatch",
            text="Instead of a long if/elif chain, put the choices in a dict that maps a key to a function, then look the function up and call it.",
            code=r"""ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b}
print(ops["+"](5, 3))
print(ops["-"](5, 3))""",
            output="8\n2",
            point="A dict of functions beats an if-chain.",
        ),
        Slide(
            title="Stack with a list",
            text="A stack is last in, first out, like a pile of plates. append puts on top and pop takes the top one off.",
            code=r"""stack = []
stack.append("a")
stack.append("b")
print(stack.pop())
print(stack)""",
            output="b\n['a']",
            point="append + pop = a stack.",
        ),
        Slide(
            title="Queue with deque",
            text="A queue is first in, first out, like a line at a shop. A list is slow at removing from the front, so use collections.deque and popleft.",
            code=r"""from collections import deque
queue = deque(["a", "b", "c"])
queue.append("d")
print(queue.popleft())
print(list(queue))""",
            output="a\n['b', 'c', 'd']",
            point="deque: append at the back, popleft from the front.",
        ),
        Slide(
            title="Two pointers",
            text="On a sorted list, put one marker at each end and move them toward each other. Here we look for two numbers adding to 7 (we know a pair exists): too small moves left up, too big moves right down.",
            code=r"""nums = [1, 3, 4, 6, 9]
left, right = 0, 4
while nums[left] + nums[right] != 7:
    if nums[left] + nums[right] < 7:
        left += 1
    else:
        right -= 1
print(nums[left], nums[right])""",
            output="1 6",
            point="Sorted order tells you which pointer to move.",
        ),
        Slide(
            title="Sliding window sum",
            text="To get the best sum of 3 neighbours, do not re-add each group. Slide the window: add the new item that enters and subtract the one that leaves.",
            code=r"""nums = [2, 1, 5, 1, 3, 2]
k = 3
window = sum(nums[:k])
best = window
for i in range(k, len(nums)):
    window += nums[i] - nums[i - k]
    best = max(best, window)
print(best)""",
            output="9",
            point="Add the newcomer, subtract the leaver.",
        ),
        Slide(
            title="Memoization with lru_cache",
            text="A function that calls itself with the same inputs again and again wastes work. @lru_cache remembers each answer, so every input is worked out only once.",
            code=r"""from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(30))""",
            output="832040",
            point="One decorator turns a slow recursion into a fast one.",
        ),
        Slide(
            title="Sorting with key= and reverse=",
            text="sorted() returns a new sorted list. key= says what to sort by, and reverse=True flips the order.",
            code=r"""words = ["pear", "fig", "banana"]
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))
print(sorted(words))""",
            output="['fig', 'pear', 'banana']\n['banana', 'pear', 'fig']\n['banana', 'fig', 'pear']",
            point="key= picks the thing to compare; the items stay as they are.",
        ),
        Slide(
            title="Building a string with join",
            text="Gluing strings together with + in a loop is clumsy and slow. Collect the pieces in a list, then join them once with the separator you want.",
            code=r"""parts = []
for n in range(4):
    parts.append(str(n))
print(", ".join(parts))
print("-".join(["a", "b", "c"]))""",
            output="0, 1, 2, 3\na-b-c",
            point="separator.join(list_of_strings)",
        ),
    ),
)
