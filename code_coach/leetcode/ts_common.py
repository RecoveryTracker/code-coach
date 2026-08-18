"""Pieces shared by the TypeScript pattern files."""

from __future__ import annotations

from code_coach.leetcode.problems import Problem, _src


def _p(
    number: int,
    title: str,
    difficulty: str,
    idea: str,
    complexity: str,
    code: str,
) -> Problem:
    return Problem(number, title, difficulty, idea, complexity, _src(code))


LIST_NODE = _src(
    """
    class ListNode {
      val: number;
      next: ListNode | null;
      constructor(val: number = 0, next: ListNode | null = null) {
        this.val = val;
        this.next = next;
      }
    }
    """
)

TREE_NODE = _src(
    """
    class TreeNode {
      val: number;
      left: TreeNode | null;
      right: TreeNode | null;
      constructor(
        val: number = 0,
        left: TreeNode | null = null,
        right: TreeNode | null = null,
      ) {
        this.val = val;
        this.left = left;
        this.right = right;
      }
    }
    """
)

GRAPH_NODE = _src(
    """
    class GraphNode {
      val: number;
      neighbors: GraphNode[];
      constructor(val: number = 0, neighbors: GraphNode[] = []) {
        this.val = val;
        this.neighbors = neighbors;
      }
    }
    """
)
