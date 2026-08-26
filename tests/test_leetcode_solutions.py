"""
Every solution in the LeetCode bank is executed against real cases.

This bank is typed verbatim as muscle memory, so a wrong line here would be
drilled in rather than caught. These tests run the exact source string the
student is asked to type — not a copy — so the two can never drift apart.
"""

from __future__ import annotations

import ast
import pathlib
import unittest

from code_coach.leetcode.problems import (
    PATTERNS,
    PATTERNS_BY_ID,
    all_problems,
    problem_count,
)


def load(pattern_id: str, number: int) -> dict:
    """Exec one solution (plus its pattern preamble) and return its namespace."""
    pattern = PATTERNS_BY_ID[pattern_id]
    problem = next(p for p in pattern.problems if p.number == number)
    ns: dict = {}
    for block in pattern.preamble:
        exec(block, ns)
    exec(problem.code, ns)
    return ns


# ── Helpers for linked-list / tree shaped inputs ────────────


def make_list(values, node_cls):
    head = None
    for v in reversed(values):
        head = node_cls(v, head)
    return head


def read_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def make_tree(values, node_cls):
    """Level-order build; None means 'no child'."""
    if not values:
        return None
    root = node_cls(values[0])
    queue = [root]
    i = 1
    while queue and i < len(values):
        node = queue.pop(0)
        if i < len(values):
            if values[i] is not None:
                node.left = node_cls(values[i])
                queue.append(node.left)
            i += 1
        if i < len(values):
            if values[i] is not None:
                node.right = node_cls(values[i])
                queue.append(node.right)
            i += 1
    return root


class TestHashMap(unittest.TestCase):
    def test_two_sum(self):
        f = load("lc-hashmap", 1)["two_sum"]
        self.assertEqual(f([2, 7, 11, 15], 9), [0, 1])
        self.assertEqual(f([3, 2, 4], 6), [1, 2])
        self.assertEqual(f([3, 3], 6), [0, 1])
        self.assertEqual(f([1, 2], 99), [])

    def test_contains_duplicate(self):
        f = load("lc-hashmap", 217)["contains_duplicate"]
        self.assertTrue(f([1, 2, 3, 1]))
        self.assertFalse(f([1, 2, 3, 4]))
        self.assertFalse(f([]))

    def test_is_anagram(self):
        f = load("lc-hashmap", 242)["is_anagram"]
        self.assertTrue(f("anagram", "nagaram"))
        self.assertFalse(f("rat", "car"))
        self.assertFalse(f("a", "ab"))
        self.assertTrue(f("", ""))

    def test_group_anagrams(self):
        f = load("lc-hashmap", 49)["group_anagrams"]
        got = f(["eat", "tea", "tan", "ate", "nat", "bat"])
        norm = sorted(sorted(g) for g in got)
        self.assertEqual(norm, [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]])


class TestTwoPointers(unittest.TestCase):
    def test_is_palindrome(self):
        f = load("lc-two-pointers", 125)["is_palindrome"]
        self.assertTrue(f("A man, a plan, a canal: Panama"))
        self.assertFalse(f("race a car"))
        self.assertTrue(f(" "))
        self.assertTrue(f("aa"))

    def test_two_sum_sorted(self):
        f = load("lc-two-pointers", 167)["two_sum_sorted"]
        self.assertEqual(f([2, 7, 11, 15], 9), [1, 2])
        self.assertEqual(f([2, 3, 4], 6), [1, 3])
        self.assertEqual(f([-1, 0], -1), [1, 2])

    def test_max_area(self):
        f = load("lc-two-pointers", 11)["max_area"]
        self.assertEqual(f([1, 8, 6, 2, 5, 4, 8, 3, 7]), 49)
        self.assertEqual(f([1, 1]), 1)

    def test_three_sum(self):
        f = load("lc-two-pointers", 15)["three_sum"]
        got = sorted(sorted(t) for t in f([-1, 0, 1, 2, -1, -4]))
        self.assertEqual(got, [[-1, -1, 2], [-1, 0, 1]])
        self.assertEqual(f([0, 1, 1]), [])
        self.assertEqual(f([0, 0, 0]), [[0, 0, 0]])


class TestSlidingWindow(unittest.TestCase):
    def test_max_profit(self):
        f = load("lc-sliding-window", 121)["max_profit"]
        self.assertEqual(f([7, 1, 5, 3, 6, 4]), 5)
        self.assertEqual(f([7, 6, 4, 3, 1]), 0)

    def test_longest_substring(self):
        f = load("lc-sliding-window", 3)["length_of_longest_substring"]
        self.assertEqual(f("abcabcbb"), 3)
        self.assertEqual(f("bbbbb"), 1)
        self.assertEqual(f("pwwkew"), 3)
        self.assertEqual(f(""), 0)
        self.assertEqual(f("tmmzuxt"), 5)

    def test_min_sub_array_len(self):
        f = load("lc-sliding-window", 209)["min_sub_array_len"]
        self.assertEqual(f(7, [2, 3, 1, 2, 4, 3]), 2)
        self.assertEqual(f(4, [1, 4, 4]), 1)
        self.assertEqual(f(11, [1, 1, 1, 1, 1, 1, 1, 1]), 0)

    def test_character_replacement(self):
        f = load("lc-sliding-window", 424)["character_replacement"]
        self.assertEqual(f("ABAB", 2), 4)
        self.assertEqual(f("AABABBA", 1), 4)


class TestStack(unittest.TestCase):
    def test_is_valid(self):
        f = load("lc-stack", 20)["is_valid"]
        self.assertTrue(f("()"))
        self.assertTrue(f("()[]{}"))
        self.assertFalse(f("(]"))
        self.assertFalse(f("("))
        self.assertFalse(f(")"))
        self.assertTrue(f(""))

    def test_min_stack(self):
        cls = load("lc-stack", 155)["MinStack"]
        s = cls()
        s.push(-2)
        s.push(0)
        s.push(-3)
        self.assertEqual(s.get_min(), -3)
        s.pop()
        self.assertEqual(s.top(), 0)
        self.assertEqual(s.get_min(), -2)

    def test_eval_rpn(self):
        f = load("lc-stack", 150)["eval_rpn"]
        self.assertEqual(f(["2", "1", "+", "3", "*"]), 9)
        self.assertEqual(f(["4", "13", "5", "/", "+"]), 6)
        # Division truncates toward zero, not floor.
        self.assertEqual(f(["-7", "2", "/"]), -3)

    def test_daily_temperatures(self):
        f = load("lc-stack", 739)["daily_temperatures"]
        self.assertEqual(
            f([73, 74, 75, 71, 69, 72, 76, 73]), [1, 1, 4, 2, 1, 1, 0, 0]
        )
        self.assertEqual(f([30, 40, 50, 60]), [1, 1, 1, 0])


class TestLinkedList(unittest.TestCase):
    def test_reverse_list(self):
        ns = load("lc-linked-list", 206)
        head = make_list([1, 2, 3, 4, 5], ns["ListNode"])
        self.assertEqual(read_list(ns["reverse_list"](head)), [5, 4, 3, 2, 1])
        self.assertEqual(read_list(ns["reverse_list"](None)), [])

    def test_merge_two_lists(self):
        ns = load("lc-linked-list", 21)
        node = ns["ListNode"]
        merged = ns["merge_two_lists"](
            make_list([1, 2, 4], node), make_list([1, 3, 4], node)
        )
        self.assertEqual(read_list(merged), [1, 1, 2, 3, 4, 4])
        self.assertEqual(read_list(ns["merge_two_lists"](None, None)), [])

    def test_has_cycle(self):
        ns = load("lc-linked-list", 141)
        node = ns["ListNode"]
        head = make_list([3, 2, 0, -4], node)
        self.assertFalse(ns["has_cycle"](head))
        # Point the tail back at the second node.
        tail = head
        while tail.next:
            tail = tail.next
        tail.next = head.next
        self.assertTrue(ns["has_cycle"](head))

    def test_remove_nth_from_end(self):
        ns = load("lc-linked-list", 19)
        node = ns["ListNode"]
        out = ns["remove_nth_from_end"](make_list([1, 2, 3, 4, 5], node), 2)
        self.assertEqual(read_list(out), [1, 2, 3, 5])
        out = ns["remove_nth_from_end"](make_list([1], node), 1)
        self.assertEqual(read_list(out), [])
        out = ns["remove_nth_from_end"](make_list([1, 2], node), 2)
        self.assertEqual(read_list(out), [2])


class TestBinarySearch(unittest.TestCase):
    def test_search(self):
        f = load("lc-binary-search", 704)["search"]
        self.assertEqual(f([-1, 0, 3, 5, 9, 12], 9), 4)
        self.assertEqual(f([-1, 0, 3, 5, 9, 12], 2), -1)
        self.assertEqual(f([5], 5), 0)

    def test_search_insert(self):
        f = load("lc-binary-search", 35)["search_insert"]
        self.assertEqual(f([1, 3, 5, 6], 5), 2)
        self.assertEqual(f([1, 3, 5, 6], 2), 1)
        self.assertEqual(f([1, 3, 5, 6], 7), 4)
        self.assertEqual(f([1, 3, 5, 6], 0), 0)

    def test_find_min(self):
        f = load("lc-binary-search", 153)["find_min"]
        self.assertEqual(f([3, 4, 5, 1, 2]), 1)
        self.assertEqual(f([4, 5, 6, 7, 0, 1, 2]), 0)
        self.assertEqual(f([11, 13, 15, 17]), 11)

    def test_search_rotated(self):
        f = load("lc-binary-search", 33)["search_rotated"]
        self.assertEqual(f([4, 5, 6, 7, 0, 1, 2], 0), 4)
        self.assertEqual(f([4, 5, 6, 7, 0, 1, 2], 3), -1)
        self.assertEqual(f([1], 0), -1)
        self.assertEqual(f([5, 1, 3], 3), 2)

    def test_min_eating_speed(self):
        f = load("lc-binary-search", 875)["min_eating_speed"]
        self.assertEqual(f([3, 6, 7, 11], 8), 4)
        self.assertEqual(f([30, 11, 23, 4, 20], 5), 30)
        self.assertEqual(f([30, 11, 23, 4, 20], 6), 23)


class TestTreeDFS(unittest.TestCase):
    def test_max_depth(self):
        ns = load("lc-tree-dfs", 104)
        root = make_tree([3, 9, 20, None, None, 15, 7], ns["TreeNode"])
        self.assertEqual(ns["max_depth"](root), 3)
        self.assertEqual(ns["max_depth"](None), 0)

    def test_invert_tree(self):
        ns = load("lc-tree-dfs", 226)
        root = make_tree([4, 2, 7, 1, 3, 6, 9], ns["TreeNode"])
        out = ns["invert_tree"](root)
        self.assertEqual(out.left.val, 7)
        self.assertEqual(out.right.val, 2)
        self.assertEqual(out.left.left.val, 9)

    def test_has_path_sum(self):
        ns = load("lc-tree-dfs", 112)
        root = make_tree(
            [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], ns["TreeNode"]
        )
        self.assertTrue(ns["has_path_sum"](root, 22))
        self.assertFalse(ns["has_path_sum"](root, 100))
        self.assertFalse(ns["has_path_sum"](None, 0))

    def test_diameter(self):
        ns = load("lc-tree-dfs", 543)
        root = make_tree([1, 2, 3, 4, 5], ns["TreeNode"])
        self.assertEqual(ns["diameter_of_binary_tree"](root), 3)
        self.assertEqual(ns["diameter_of_binary_tree"](None), 0)

    def test_is_valid_bst(self):
        ns = load("lc-tree-dfs", 98)
        good = make_tree([2, 1, 3], ns["TreeNode"])
        self.assertTrue(ns["is_valid_bst"](good))
        bad = make_tree([5, 1, 4, None, None, 3, 6], ns["TreeNode"])
        self.assertFalse(ns["is_valid_bst"](bad))
        # A deep violator that a naive parent-only check would miss.
        sneaky = make_tree([5, 4, 6, None, None, 3, 7], ns["TreeNode"])
        self.assertFalse(ns["is_valid_bst"](sneaky))


class TestTreeBFS(unittest.TestCase):
    def test_level_order(self):
        ns = load("lc-tree-bfs", 102)
        root = make_tree([3, 9, 20, None, None, 15, 7], ns["TreeNode"])
        self.assertEqual(ns["level_order"](root), [[3], [9, 20], [15, 7]])
        self.assertEqual(ns["level_order"](None), [])

    def test_right_side_view(self):
        ns = load("lc-tree-bfs", 199)
        root = make_tree([1, 2, 3, None, 5, None, 4], ns["TreeNode"])
        self.assertEqual(ns["right_side_view"](root), [1, 3, 4])
        self.assertEqual(ns["right_side_view"](None), [])

    def test_zigzag(self):
        ns = load("lc-tree-bfs", 103)
        root = make_tree([3, 9, 20, None, None, 15, 7], ns["TreeNode"])
        self.assertEqual(
            ns["zigzag_level_order"](root), [[3], [20, 9], [15, 7]]
        )

    def test_min_depth(self):
        ns = load("lc-tree-bfs", 111)
        root = make_tree([3, 9, 20, None, None, 15, 7], ns["TreeNode"])
        self.assertEqual(ns["min_depth"](root), 2)
        # A single left-leaning spine: the shallowest leaf is at the bottom.
        spine = make_tree([2, None, 3, None, 4, None, 5], ns["TreeNode"])
        self.assertEqual(ns["min_depth"](spine), 4)
        self.assertEqual(ns["min_depth"](None), 0)

    def test_average_of_levels(self):
        ns = load("lc-tree-bfs", 637)
        root = make_tree([3, 9, 20, None, None, 15, 7], ns["TreeNode"])
        self.assertEqual(ns["average_of_levels"](root), [3.0, 14.5, 11.0])
        self.assertEqual(ns["average_of_levels"](None), [])

    def test_largest_values(self):
        ns = load("lc-tree-bfs", 515)
        root = make_tree([1, 3, 2, 5, 3, None, 9], ns["TreeNode"])
        self.assertEqual(ns["largest_values"](root), [1, 3, 9])
        # Negatives, because a running max seeded with 0 would report 0 here.
        negative = make_tree([-1, -2, -3], ns["TreeNode"])
        self.assertEqual(ns["largest_values"](negative), [-1, -2])
        self.assertEqual(ns["largest_values"](None), [])

    def test_max_level_sum(self):
        ns = load("lc-tree-bfs", 1161)
        root = make_tree([1, 7, 0, 7, -8, None, None], ns["TreeNode"])
        self.assertEqual(ns["max_level_sum"](root), 2)
        # Every level negative: -100, then -500, then -85. The shallowest
        # level only wins if a best-sum seeded at 0 rejected all three.
        negative = make_tree([-100, -200, -300, -20, -5, -10, -50], ns["TreeNode"])
        self.assertEqual(ns["max_level_sum"](negative), 3)
        self.assertEqual(ns["max_level_sum"](None), 0)

    def test_width_of_binary_tree(self):
        ns = load("lc-tree-bfs", 662)
        root = make_tree([1, 3, 2, 5, 3, None, 9], ns["TreeNode"])
        self.assertEqual(ns["width_of_binary_tree"](root), 4)
        # The gap counts: two grandchildren at the outer edges are width 4.
        sparse = make_tree([1, 3, 2, 5, None, None, 9], ns["TreeNode"])
        self.assertEqual(ns["width_of_binary_tree"](sparse), 4)
        self.assertEqual(ns["width_of_binary_tree"](None), 0)


class TestGraph(unittest.TestCase):
    def test_flood_fill(self):
        f = load("lc-graph", 733)["flood_fill"]
        image = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
        self.assertEqual(
            f(image, 1, 1, 2), [[2, 2, 2], [2, 2, 0], [2, 0, 1]]
        )
        # Same colour must not spin forever.
        self.assertEqual(f([[0, 0], [0, 0]], 0, 0, 0), [[0, 0], [0, 0]])

    def test_num_islands(self):
        f = load("lc-graph", 200)["num_islands"]
        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"],
        ]
        self.assertEqual(f(grid), 3)
        self.assertEqual(f([]), 0)

    def test_oranges_rotting(self):
        f = load("lc-graph", 994)["oranges_rotting"]
        self.assertEqual(f([[2, 1, 1], [1, 1, 0], [0, 1, 1]]), 4)
        self.assertEqual(f([[2, 1, 1], [0, 1, 1], [1, 0, 1]]), -1)
        self.assertEqual(f([[0, 2]]), 0)

    def test_clone_graph(self):
        ns = load("lc-graph", 133)
        node_cls = ns["Node"]
        a, b = node_cls(1), node_cls(2)
        a.neighbors.append(b)
        b.neighbors.append(a)
        clone = ns["clone_graph"](a)
        self.assertIsNot(clone, a)
        self.assertEqual(clone.val, 1)
        self.assertEqual(clone.neighbors[0].val, 2)
        self.assertIs(clone.neighbors[0].neighbors[0], clone)
        self.assertIsNone(ns["clone_graph"](None))


class TestBacktracking(unittest.TestCase):
    def test_subsets(self):
        f = load("lc-backtracking", 78)["subsets"]
        got = sorted(sorted(s) for s in f([1, 2, 3]))
        self.assertEqual(
            got, [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
        )

    def test_subsets_with_dup(self):
        f = load("lc-backtracking", 90)["subsets_with_dup"]
        got = sorted(sorted(s) for s in f([1, 2, 2]))
        self.assertEqual(got, [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]])

    def test_permute(self):
        f = load("lc-backtracking", 46)["permute"]
        got = sorted(f([1, 2, 3]))
        self.assertEqual(len(got), 6)
        self.assertEqual(got[0], [1, 2, 3])
        self.assertEqual(got[-1], [3, 2, 1])

    def test_combination_sum(self):
        f = load("lc-backtracking", 39)["combination_sum"]
        got = sorted(sorted(c) for c in f([2, 3, 6, 7], 7))
        self.assertEqual(got, [[2, 2, 3], [7]])
        self.assertEqual(f([2], 1), [])

    def test_exist(self):
        f = load("lc-backtracking", 79)["exist"]
        board = [
            ["A", "B", "C", "E"],
            ["S", "F", "C", "S"],
            ["A", "D", "E", "E"],
        ]
        self.assertTrue(f([row[:] for row in board], "ABCCED"))
        self.assertTrue(f([row[:] for row in board], "SEE"))
        self.assertFalse(f([row[:] for row in board], "ABCB"))


class TestHeap(unittest.TestCase):
    def test_find_kth_largest(self):
        f = load("lc-heap", 215)["find_kth_largest"]
        self.assertEqual(f([3, 2, 1, 5, 6, 4], 2), 5)
        self.assertEqual(f([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)

    def test_top_k_frequent(self):
        f = load("lc-heap", 347)["top_k_frequent"]
        self.assertEqual(sorted(f([1, 1, 1, 2, 2, 3], 2)), [1, 2])
        self.assertEqual(f([1], 1), [1])

    def test_k_closest(self):
        f = load("lc-heap", 973)["k_closest"]
        self.assertEqual(f([[1, 3], [-2, 2]], 1), [[-2, 2]])
        got = sorted(f([[3, 3], [5, -1], [-2, 4]], 2))
        self.assertEqual(got, [[-2, 4], [3, 3]])

    def test_last_stone_weight(self):
        f = load("lc-heap", 1046)["last_stone_weight"]
        self.assertEqual(f([2, 7, 4, 1, 8, 1]), 1)
        self.assertEqual(f([2, 2]), 0)
        self.assertEqual(f([3]), 3)
        self.assertEqual(f([]), 0)

    def test_top_k_frequent_words(self):
        f = load("lc-heap", 692)["top_k_frequent_words"]
        self.assertEqual(f(["i", "love", "leetcode", "i", "love", "coding"], 2),
                         ["i", "love"])
        # Equal counts must come back alphabetically, not in insertion order.
        self.assertEqual(f(["b", "a", "c"], 3), ["a", "b", "c"])

    def test_frequency_sort(self):
        f = load("lc-heap", 451)["frequency_sort"]
        # Ties are free to fall either way; the heap orders them by character.
        self.assertEqual(f("tree"), "eert")
        self.assertEqual(f("cccaaa"), "aaaccc")
        self.assertEqual(f(""), "")
        # Whatever the tie order, every character survives with its count.
        out = f("Aabb")
        self.assertEqual(sorted(out), sorted("Aabb"))
        self.assertEqual(out[:2], "bb")

    def test_kth_smallest(self):
        f = load("lc-heap", 378)["kth_smallest"]
        matrix = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
        self.assertEqual(f(matrix, 8), 13)
        self.assertEqual(f(matrix, 1), 1)
        self.assertEqual(f(matrix, 9), 15)
        self.assertEqual(f([[-5]], 1), -5)

    def test_reorganize_string(self):
        f = load("lc-heap", 767)["reorganize_string"]
        out = f("aab")
        self.assertEqual(sorted(out), sorted("aab"))
        self.assertTrue(all(a != b for a, b in zip(out, out[1:])))
        self.assertEqual(f("aaab"), "")
        self.assertEqual(f("a"), "a")


class TestTopological(unittest.TestCase):
    def test_can_finish(self):
        f = load("lc-topological", 207)["can_finish"]
        self.assertTrue(f(2, [[1, 0]]))
        self.assertFalse(f(2, [[1, 0], [0, 1]]))
        self.assertTrue(f(1, []))

    def test_find_order(self):
        f = load("lc-topological", 210)["find_order"]
        self.assertEqual(f(2, [[1, 0]]), [0, 1])
        self.assertEqual(f(2, [[1, 0], [0, 1]]), [])
        order = f(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
        self.assertEqual(order[0], 0)
        self.assertEqual(order[-1], 3)

    def test_find_min_height_trees(self):
        f = load("lc-topological", 310)["find_min_height_trees"]
        self.assertEqual(sorted(f(4, [[1, 0], [1, 2], [1, 3]])), [1])
        self.assertEqual(
            sorted(f(6, [[3, 0], [3, 1], [3, 2], [3, 4], [5, 4]])), [3, 4]
        )
        self.assertEqual(f(1, []), [0])

    def test_eventual_safe_nodes(self):
        f = load("lc-topological", 802)["eventual_safe_nodes"]
        self.assertEqual(
            f([[1, 2], [2, 3], [5], [0], [5], [], []]), [2, 4, 5, 6]
        )
        self.assertEqual(f([[1, 2, 3, 4], [1, 2], [3, 4], [0, 4], []]), [4])
        self.assertEqual(f([[]]), [0])

    def test_check_if_prerequisite(self):
        f = load("lc-topological", 1462)["check_if_prerequisite"]
        self.assertEqual(f(2, [[1, 0]], [[0, 1], [1, 0]]), [False, True])
        self.assertEqual(f(2, [], [[1, 0], [0, 1]]), [False, False])
        # Transitive: 0 → 1 → 2 means 0 is a prerequisite of 2.
        self.assertEqual(f(3, [[0, 1], [1, 2]], [[0, 2]]), [True])

    def test_find_all_recipes(self):
        f = load("lc-topological", 2115)["find_all_recipes"]
        self.assertEqual(
            f(["bread"], [["yeast", "flour"]], ["yeast", "flour", "corn"]),
            ["bread"],
        )
        # A recipe used as an ingredient of another.
        made = f(
            ["bread", "sandwich"],
            [["yeast", "flour"], ["bread", "meat"]],
            ["yeast", "flour", "meat"],
        )
        self.assertEqual(sorted(made), ["bread", "sandwich"])
        self.assertEqual(f(["bread"], [["yeast", "flour"]], ["yeast"]), [])

    def test_minimum_semesters(self):
        f = load("lc-topological", 1136)["minimum_semesters"]
        self.assertEqual(f(3, [[1, 3], [2, 3]]), 2)
        self.assertEqual(f(3, [[1, 2], [2, 3], [3, 1]]), -1)
        self.assertEqual(f(1, []), 1)

    def test_alien_order(self):
        f = load("lc-topological", 269)["alien_order"]
        self.assertEqual(f(["wrt", "wrf", "er", "ett", "rftt"]), "wertf")
        self.assertEqual(f(["z", "x", "z"]), "")
        # A prefix that follows its own longer form is impossible.
        self.assertEqual(f(["abc", "ab"]), "")
        self.assertEqual(f(["z", "x"]), "zx")


class TestDP(unittest.TestCase):
    def test_climb_stairs(self):
        f = load("lc-dp", 70)["climb_stairs"]
        self.assertEqual(f(1), 1)
        self.assertEqual(f(2), 2)
        self.assertEqual(f(3), 3)
        self.assertEqual(f(5), 8)

    def test_rob(self):
        f = load("lc-dp", 198)["rob"]
        self.assertEqual(f([1, 2, 3, 1]), 4)
        self.assertEqual(f([2, 7, 9, 3, 1]), 12)
        self.assertEqual(f([]), 0)

    def test_coin_change(self):
        f = load("lc-dp", 322)["coin_change"]
        self.assertEqual(f([1, 2, 5], 11), 3)
        self.assertEqual(f([2], 3), -1)
        self.assertEqual(f([1], 0), 0)

    def test_length_of_lis(self):
        f = load("lc-dp", 300)["length_of_lis"]
        self.assertEqual(f([10, 9, 2, 5, 3, 7, 101, 18]), 4)
        self.assertEqual(f([0, 1, 0, 3, 2, 3]), 4)
        self.assertEqual(f([7, 7, 7, 7]), 1)


class TestBankIntegrity(unittest.TestCase):
    def test_every_solution_parses(self):
        for problem in all_problems():
            with self.subTest(problem=problem.label):
                ast.parse(problem.code)
        self.assertEqual(problem_count(), len(all_problems()))

    def test_every_solution_has_a_test(self):
        """A solution with no case would be drilled in unverified."""
        source = pathlib.Path(__file__).read_text(encoding="utf-8")
        for pattern in PATTERNS:
            for problem in pattern.problems:
                needle = f'load("{pattern.id}", {problem.number})'
                with self.subTest(problem=problem.label):
                    self.assertIn(
                        needle,
                        source,
                        f"{problem.label} has no test — add one before shipping it.",
                    )

    def test_problem_numbers_unique_within_pattern(self):
        for pattern in PATTERNS:
            numbers = [p.number for p in pattern.problems]
            self.assertEqual(len(numbers), len(set(numbers)), pattern.id)

    def test_idea_and_complexity_present(self):
        for problem in all_problems():
            self.assertTrue(problem.idea.strip(), problem.label)
            self.assertTrue(problem.complexity.strip(), problem.label)
            self.assertIn(problem.difficulty, ("Easy", "Medium", "Hard"))


if __name__ == "__main__":
    unittest.main()
