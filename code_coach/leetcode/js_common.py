"""Pieces shared by the JavaScript pattern files."""

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
      constructor(val = 0, next = null) {
        this.val = val;
        this.next = next;
      }
    }
    """
)

TREE_NODE = _src(
    """
    class TreeNode {
      constructor(val = 0, left = null, right = null) {
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
      constructor(val = 0, neighbors = []) {
        this.val = val;
        this.neighbors = neighbors;
      }
    }
    """
)
