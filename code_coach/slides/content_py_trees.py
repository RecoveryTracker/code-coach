"""Trees: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 122

TN = """class TreeNode:
    def __init__(self, val, left=None, right=None): self.val, self.left, self.right = val, left, right
"""
BIG = "root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, None, TreeNode(6)))\n"
BST = "root = TreeNode(5, TreeNode(2, None, TreeNode(4)), TreeNode(9, TreeNode(7)))\n"
INO = "def ino(n): return ino(n.left) + [n.val] + ino(n.right) if n else []\n"

DECK = Deck(
    id="py-trees",
    title="Trees",
    language="python",
    blurb="Binary trees and search trees: traversals, depth, validation, ancestors and paths, all by recursion.",
    slides=(
        Slide(
            title="A TreeNode: value, left, right",
            text="A binary tree node holds a value and up to two children. A missing child is None, and a node with no children is called a leaf.",
            code=TN + r"""root = TreeNode(1, TreeNode(2), TreeNode(3))
print(root.val, root.left.val, root.right.val)
print(root.left.left)""",
            output="1 2 3\nNone",
            point="A tree is just its root node; every child is itself the root of a smaller tree.",
        ),
        Slide(
            title="Building a small tree by hand",
            text="Nest the constructors to draw the tree in code. Here 1 has children 2 and 3, and 2 has children 4 and 5; node 3 has no children at all.",
            code=TN + r"""root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
print(root.left.right.val)
print(root.right.left)
print(root.left.left.left)""",
            output="5\nNone\nNone",
            point="Read a path with dots: root.left.right means 'go left, then right'.",
        ),
        Slide(
            title="Depth with recursion",
            text="The depth of a tree is one more than the deeper of its two subtrees. An empty tree has depth 0, and that base case ends the recursion.",
            code=TN + BIG + r"""def depth(n): return 0 if n is None else 1 + max(depth(n.left), depth(n.right))
print(depth(root))
print(depth(root.right))""",
            output="3\n2",
            point="Tree recursion: answer for None, then combine the answers for left and right.",
        ),
        Slide(
            title="Counting nodes",
            text="A node counts as one, plus everything in its left subtree, plus everything in its right subtree. The same shape of recursion solves sums, leaf counts and more.",
            code=TN + BIG + r"""def count(n): return 0 if not n else 1 + count(n.left) + count(n.right)
def leaves(n): return 0 if not n else 1 if not n.left and not n.right else leaves(n.left) + leaves(n.right)
print(count(root), count(root.left))
print(leaves(root))""",
            output="6 3\n3",
            point="Change what you do at the node and what you do for None; the walk stays the same.",
        ),
        Slide(
            title="Preorder, inorder, postorder",
            text="All three visit every node, but they differ in when the node itself is read: before its children (pre), between them (in), or after them (post).",
            code=TN + BIG + INO + r"""def pre(n): return [n.val] + pre(n.left) + pre(n.right) if n else []
def post(n): return post(n.left) + post(n.right) + [n.val] if n else []
print(pre(root))
print(ino(root))
print(post(root))""",
            output="[1, 2, 4, 5, 3, 6]\n[4, 2, 5, 1, 3, 6]\n[4, 5, 2, 6, 3, 1]",
            point="Pre = root first, in = root in the middle, post = root last. Left always comes before right.",
        ),
        Slide(
            title="Level order with a deque",
            text="To go row by row, keep the current row in a queue. Record its values, then build the next row from the children of every node in it.",
            code=r"""from collections import deque
""" + TN + BIG + r"""q, out = deque([root]), []
while q:
    out.append([n.val for n in q])
    q = deque(c for n in q for c in (n.left, n.right) if c)
print(out)""",
            output="[[1], [2, 3], [4, 5, 6]]",
            point="Level order (breadth first) uses a queue; the other orders use recursion, which is a stack.",
        ),
        Slide(
            title="Binary search tree: insert",
            text="In a binary search tree everything left of a node is smaller and everything right is bigger. To insert, go left or right by comparison until you find an empty spot.",
            code=TN + r"""def insert(n, v):
    if not n: return TreeNode(v)
    if v < n.val: n.left = insert(n.left, v)
    else: n.right = insert(n.right, v)
    return n
root = None
for v in (5, 3, 8, 1, 4): root = insert(root, v)
print(root.val, root.left.val, root.right.val, root.left.left.val)""",
            output="5 3 8 1",
            point="The first value becomes the root; each later value walks down and becomes a leaf.",
        ),
        Slide(
            title="BST search",
            text="Searching follows the same rule as inserting: smaller goes left, bigger goes right. Each step throws away a whole subtree, so a balanced tree needs only about log n steps.",
            code=TN + r"""root = TreeNode(5, TreeNode(3, TreeNode(1), TreeNode(4)), TreeNode(8))
def find(n, v):
    while n and n.val != v: n = n.left if v < n.val else n.right
    return n is not None
print(find(root, 4), find(root, 7))""",
            output="True False",
            point="BST search is binary search on a tree: compare, then discard half.",
        ),
        Slide(
            title="Inorder of a BST is sorted",
            text="Visiting left, node, right in a search tree gives the values in increasing order. That is a handy check, and it is how you read a BST back as a sorted list.",
            code=TN + BST + INO + r"""print(ino(root))
print(ino(root) == sorted(ino(root)))""",
            output="[2, 4, 5, 7, 9]\nTrue",
            point="BST + inorder = sorted. If inorder is not increasing, it is not a BST.",
        ),
        Slide(
            title="Min and max of a BST",
            text="The smallest value is as far left as you can go; the biggest is as far right. No comparing is needed, just follow one side to the end.",
            code=TN + BST + r"""def lo(n):
    while n.left: n = n.left
    return n.val
def hi(n):
    while n.right: n = n.right
    return n.val
print(lo(root), hi(root))""",
            output="2 9",
            point="Min = keep going left. Max = keep going right. O(height).",
        ),
        Slide(
            title="Validating a BST",
            text="Checking only each parent against its children is not enough: a deep node can break a rule set by a far ancestor. Pass down a (low, high) window that every value must fit inside.",
            code=TN + r"""def valid(n, lo=float("-inf"), hi=float("inf")):
    if not n: return True
    return lo < n.val < hi and valid(n.left, lo, n.val) and valid(n.right, n.val, hi)
bad = TreeNode(5, TreeNode(3, None, TreeNode(6)), TreeNode(8))
print(valid(bad))
print(valid(TreeNode(5, TreeNode(3), TreeNode(8))))""",
            output="False\nTrue",
            point="In 'bad', 6 is a fine child of 3 but sits left of 5: only the window catches it.",
        ),
        Slide(
            title="Lowest common ancestor in a BST",
            text="Start at the root. If both values are smaller, go left; if both are bigger, go right. The first node where they split apart (or that equals one of them) is the answer.",
            code=TN + r"""root = TreeNode(6, TreeNode(2, TreeNode(0), TreeNode(4)), TreeNode(8, TreeNode(7), TreeNode(9)))
def lca(n, a, b):
    while n:
        if a < n.val and b < n.val: n = n.left
        elif a > n.val and b > n.val: n = n.right
        else: return n.val
print(lca(root, 0, 4), lca(root, 0, 9), lca(root, 7, 9))""",
            output="2 6 8",
            point="The order property lets you find the split point without searching the whole tree.",
        ),
        Slide(
            title="Path sums",
            text="Does some root-to-leaf path add up to a target? Subtract each node's value as you go down, and at a leaf check whether exactly zero is left, which is when the value equals the target.",
            code=TN + r"""root = TreeNode(5, TreeNode(4, TreeNode(11)), TreeNode(8, TreeNode(13), TreeNode(4)))
def has_sum(n, t):
    if not n: return False
    if not n.left and not n.right: return n.val == t
    return has_sum(n.left, t - n.val) or has_sum(n.right, t - n.val)
print(has_sum(root, 20), has_sum(root, 22))""",
            output="True False",
            point="Carry the remaining target down; test it only at a leaf (5+4+11 = 20).",
        ),
        Slide(
            title="Height versus balance",
            text="Height is how far down the tree goes. A tree is balanced when every node's two subtrees differ in height by at most 1; a chain has height n and makes search O(n).",
            code=TN + r"""def height(n): return 0 if not n else 1 + max(height(n.left), height(n.right))
def balanced(n): return not n or (abs(height(n.left) - height(n.right)) <= 1 and balanced(n.left) and balanced(n.right))
chain = TreeNode(1, TreeNode(2, TreeNode(3)))
tree = TreeNode(1, TreeNode(2), TreeNode(3))
print(height(chain), balanced(chain))
print(height(tree), balanced(tree))""",
            output="3 False\n2 True",
            point="Balanced trees keep height near log n; that is why BST operations stay fast.",
        ),
        Slide(
            title="Serialising a tree to a list",
            text="To save a tree, write it in preorder and put None for every missing child. To rebuild it, read the same list back in the same order with an iterator.",
            code=TN + r"""def ser(n): return [None] if not n else [n.val] + ser(n.left) + ser(n.right)
def de(it): v = next(it); return None if v is None else TreeNode(v, de(it), de(it))
root = TreeNode(1, TreeNode(2), TreeNode(3))
data = ser(root)
print(data)
copy = de(iter(data))
print(copy.right.val, ser(copy) == data)""",
            output="[1, 2, None, None, 3, None, None]\n3 True",
            point="The None markers make the list unambiguous, so one pass can rebuild the exact shape.",
        ),
    ),
)
