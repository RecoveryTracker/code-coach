"""Recursion: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 110

DECK = Deck(
    id="py-recursion",
    title="Recursion",
    language="python",
    blurb="Functions that call themselves: base cases, the call stack, memoising, backtracking, trees, and turning recursion back into a loop.",
    slides=(
        Slide(
            title="Base case and recursive case",
            text="A recursive function solves a big problem by calling itself on a smaller one. It needs a base case, where it stops, and a recursive case that moves closer to it.",
            code=r"""def countdown(n):
    if n == 0:
        print("liftoff")
        return
    print(n)
    countdown(n - 1)
countdown(3)""",
            output="3\n2\n1\nliftoff",
            point="Every recursive function needs a base case that stops it.",
        ),
        Slide(
            title="Factorial",
            text="n! is n times (n-1)!, and the chain ends at 1. The function returns a value up the chain, so each call waits for the smaller call to finish.",
            code=r"""def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
print(fact(5), fact(0))""",
            output="120 1",
            point="fact(5) = 5 * fact(4) = 5 * 4 * fact(3) ... down to 1.",
        ),
        Slide(
            title="The call stack",
            text="Each call waits on a pile of unfinished calls. The prints show it: we enter 2, 1, 0 going down, then leave 0, 1, 2 coming back up, like a stack of plates.",
            code=r"""def f(n):
    print("enter", n)
    if n > 0:
        f(n - 1)
    print("leave", n)
f(2)""",
            output="enter 2\nenter 1\nenter 0\nleave 0\nleave 1\nleave 2",
            point="The last call to start is the first to finish.",
        ),
        Slide(
            title="Sum of a list",
            text="The sum of a list is its first item plus the sum of the rest. An empty list sums to 0, which is the base case.",
            code=r"""def total(xs):
    if not xs:
        return 0
    return xs[0] + total(xs[1:])
print(total([3, 4, 5]))
print(total([]))""",
            output="12\n0",
            point="Think: first item + the answer for everything else.",
        ),
        Slide(
            title="Reversing a string",
            text="To reverse a string, reverse everything after the first letter and put that letter at the end. The empty string is the base case.",
            code=r"""def rev(s):
    if s == "":
        return ""
    return rev(s[1:]) + s[0]
print(rev("abc"))""",
            output="cba",
            point="rev('abc') = rev('bc') + 'a' = ('c' + 'b') + 'a'.",
        ),
        Slide(
            title="Fibonacci, naive: count the calls",
            text="Each fib call makes two more, and the same values get recomputed again and again. Counting the calls shows the waste: finding fib(10) takes 177 calls.",
            code=r"""calls = 0
def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
print(fib(10), calls)""",
            output="55 177",
            point="Naive fib roughly doubles its work for every step up.",
        ),
        Slide(
            title="Fibonacci, memoized",
            text="Store each answer in a dict the first time you work it out. The same fib(10) now takes only 19 calls, because repeats return straight from the memo.",
            code=r"""memo = {0: 0, 1: 1}
calls = []
def fib(n):
    calls.append(n)
    if n not in memo:
        memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]
print(fib(10), len(calls))""",
            output="55 19",
            point="Memoizing turns repeated work into a quick lookup.",
        ),
        Slide(
            title="Power by squaring",
            text="Instead of multiplying b by itself e times, compute b to the half power and square it, adding one more b if e is odd. The number of steps drops from e to about log e.",
            code=r"""def power(b, e):
    if e == 0:
        return 1
    half = power(b, e // 2)
    if e % 2 == 0:
        return half * half
    return half * half * b
print(power(2, 10), power(3, 5))""",
            output="1024 243",
            point="Halving the problem each call makes recursion very fast.",
        ),
        Slide(
            title="Flattening nested lists",
            text="If the item is not a list, return it in a one-item list. If it is a list, flatten each element and join the pieces. The nesting can be any depth.",
            code=r"""def flatten(x):
    if not isinstance(x, list):
        return [x]
    out = []
    for item in x:
        out += flatten(item)
    return out
print(flatten([1, [2, [3, 4]], 5]))""",
            output="[1, 2, 3, 4, 5]",
            point="Nested data of unknown depth is a job for recursion.",
        ),
        Slide(
            title="Generating subsets",
            text="The subsets of a list are the subsets without its first item, plus those same subsets with the first item added. An empty list has just one subset: the empty one.",
            code=r"""def subsets(items):
    if not items:
        return [[]]
    rest = subsets(items[1:])
    return rest + [[items[0]] + r for r in rest]
print(subsets([1, 2, 3]))""",
            output="[[], [3], [2], [2, 3], [1], [1, 3], [1, 2], [1, 2, 3]]",
            point="n items give 2**n subsets: each item is in or out.",
        ),
        Slide(
            title="Permutations by backtracking",
            text="Choose a letter, recurse on what is left, then go back and choose the next letter. When nothing is left, the chosen letters are one finished ordering.",
            code=r"""def perms(chosen, left):
    if not left:
        print(chosen)
        return
    for i in range(len(left)):
        perms(chosen + left[i], left[:i] + left[i + 1:])
perms("", "abc")""",
            output="abc\nacb\nbac\nbca\ncab\ncba",
            point="Backtracking = choose, explore, then undo and try the next.",
        ),
        Slide(
            title="Tree depth on a nested tuple",
            text="Here a tree is (value, left, right) with None for nothing. A tree's depth is 1 plus the deeper of its two sides, and an empty tree has depth 0.",
            code=r"""def depth(t):
    if t is None:
        return 0
    value, left, right = t
    return 1 + max(depth(left), depth(right))
tree = (1, (2, (4, None, None), None), (3, None, None))
print(depth(tree), depth(None))""",
            output="3 0",
            point="Trees are recursive by nature: a node's children are trees.",
        ),
        Slide(
            title="Binary search, recursively",
            text="Look at the middle. If it is too small, search the right half; if too big, the left half. lo > hi means the range is empty, so the item is missing and we return -1.",
            code=r"""def find(xs, target, lo, hi):
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if xs[mid] == target:
        return mid
    if xs[mid] < target:
        return find(xs, target, mid + 1, hi)
    return find(xs, target, lo, mid - 1)
print(find([1, 3, 5, 7, 9], 7, 0, 4), find([1, 3, 5, 7, 9], 4, 0, 4))""",
            output="3 -1",
            point="Each call throws away half of what is left.",
        ),
        Slide(
            title="The recursion limit",
            text="Python stops a runaway recursion after about a thousand nested calls by raising RecursionError, so a missing base case is caught instead of crashing. Very deep problems need a loop.",
            code=r"""def forever(n):
    return forever(n + 1)
try:
    forever(0)
except RecursionError:
    print("too deep")""",
            output="too deep",
            point="No base case, or too deep a chain, ends in RecursionError.",
        ),
        Slide(
            title="Recursion into a loop with a stack",
            text="Any recursion can become a loop with your own stack. Pop an item; if it is a list, push its parts back, otherwise use it. It never hits the recursion limit.",
            code=r"""def flat_sum(x):
    stack, total = [x], 0
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(item)
        else:
            total += item
    return total
print(flat_sum([1, [2, [3, 4]], 5]))""",
            output="15",
            point="Your own stack replaces the call stack.",
        ),
    ),
)
