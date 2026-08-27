"""Pieces shared by the Rust pattern files.

A separate module so `problems_rust` and `problems_rust2` can both use the
node types without importing each other — the same split the Dart bank uses.
"""

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


COLLECTIONS = "use std::collections::HashMap;\nuse std::collections::HashSet;"
HASH_MAP = "use std::collections::HashMap;"
VEC_DEQUE = "use std::collections::VecDeque;"
BINARY_HEAP = "use std::collections::BinaryHeap;"
