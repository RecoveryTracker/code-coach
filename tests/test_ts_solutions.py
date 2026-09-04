"""Every TypeScript solution is type-checked and executed against real cases.

TypeScript is a superset of JavaScript, and these assertions are plain
expressions, so the checks are the JavaScript ones rather than a second copy
that could drift from them. What differs is the run: tsc goes first with
--noEmitOnError, so a solution whose annotations don't hold up fails here
before node ever sees it. That is the reason to write TypeScript at all, and
it is worth having under test.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code, typescript_available
from code_coach.leetcode.problems_ts import PATTERNS as TS_PATTERNS

from test_js_solutions import CHECKS, HARNESS, REPORT

PATTERNS_BY_ID = {p.id: p for p in TS_PATTERNS}

# The helpers are typed here; everything else carries over unchanged.
LIST_HELPERS = """
function makeList(vals: number[]): ListNode | null {
  let head: ListNode | null = null;
  for (let i = vals.length - 1; i >= 0; i--) head = new ListNode(vals[i], head);
  return head;
}
function readList(head: ListNode | null): number[] {
  const out: number[] = [];
  while (head) { out.push(head.val); head = head.next; }
  return out;
}
"""

TREE_HELPERS = """
function makeTree(vals: (number | null)[]): TreeNode | null {
  if (!vals.length || vals[0] === null) return null;
  const root = new TreeNode(vals[0]);
  const queue: TreeNode[] = [root];
  let i = 1;
  while (queue.length && i < vals.length) {
    const node = queue.shift()!;
    if (i < vals.length) {
      if (vals[i] !== null) { node.left = new TreeNode(vals[i]!); queue.push(node.left); }
      i++;
    }
    if (i < vals.length) {
      if (vals[i] !== null) { node.right = new TreeNode(vals[i]!); queue.push(node.right); }
      i++;
    }
  }
  return root;
}
"""

TYPED_HARNESS = """
const failed: string[] = [];
function eq(label: string, got: unknown, want: unknown): void {
  const a = JSON.stringify(got);
  const b = JSON.stringify(want);
  if (a !== b) failed.push(label + ': got ' + a + ', want ' + b);
}
function ok(label: string, value: unknown): void { eq(label, !!value, true); }
"""

# No `process.exit` here: that needs @types/node, which this deliberately
# minimal tsc invocation doesn't have. Printing is enough — a green run has
# empty stdout, and _run asserts exactly that.
TYPED_REPORT = """
if (failed.length) { console.log(failed.join('\\n')); }
"""

HELPERS = {"lc-linked-list": LIST_HELPERS, "lc-tree-dfs": TREE_HELPERS,
           "lc-tree-bfs": TREE_HELPERS}


# ── Where the shared checks need a TypeScript-only nudge ─────
#
# The checks are shared with JavaScript deliberately, so that one copy
# cannot drift from the other. But three of them dereference a value whose
# declared type is nullable — middleNode returns ListNode | null, invertTree
# returns TreeNode | null, makeTree returns TreeNode | null — which
# JavaScript does not mind and strict TypeScript does. The solutions are
# right; it is the assertion that needs to say "I know this one is there".
#
# Rather than fork the checks, each fixup below is applied to the shared
# text and asserted to match exactly once. Change the JavaScript check and
# this raises rather than quietly testing something else.
NULLABLE_FIXUPS: dict[str, tuple[tuple[str, str], ...]] = {
    "lc-graph": (
        (
            "cloneGraph(new GraphNode(1, [new GraphNode(2)])).val",
            "cloneGraph(new GraphNode(1, [new GraphNode(2)]))!.val",
        ),
    ),
    "lc-linked-list": (
        (
            "middleNode(makeList([1, 2, 3, 4, 5])).val",
            "middleNode(makeList([1, 2, 3, 4, 5]))!.val",
        ),
        (
            "middleNode(makeList([1, 2, 3, 4])).val",
            "middleNode(makeList([1, 2, 3, 4]))!.val",
        ),
    ),
    "lc-tree-dfs": (
        (
            "invertTree(makeTree([2, 1, 3])).left.val",
            "invertTree(makeTree([2, 1, 3]))!.left!.val",
        ),
        (
            "const lca = makeTree([3, 5, 1, 6, 2, 0, 8]);",
            "const lca = makeTree([3, 5, 1, 6, 2, 0, 8])!;",
        ),
        ("lca.left.right", "lca.left!.right"),
    ),
}


def _typed_checks(pattern_id: str, checks: str) -> str:
    """The shared checks, with the nullable dereferences asserted."""
    for before, after in NULLABLE_FIXUPS.get(pattern_id, ()):
        found = checks.count(before)
        if found != 1:
            raise AssertionError(
                f"{pattern_id}: expected exactly one {before!r} to fix up "
                f"for TypeScript, found {found}. The shared JavaScript "
                f"check has changed and this fixup needs revisiting."
            )
        checks = checks.replace(before, after)
    return checks


@unittest.skipUnless(typescript_available(), "needs node and tsc")
class TypeScriptSolutionTests(unittest.TestCase):
    def _run(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        _, checks = CHECKS[pattern_id]
        src = "\n\n".join(
            list(pattern.preamble) + [p.code for p in pattern.problems]
        )
        src = (
            f"{src}\n{HELPERS.get(pattern_id, '')}\n"
            f"{TYPED_HARNESS}\n{_typed_checks(pattern_id, checks)}\n"
            f"{TYPED_REPORT}"
        )
        out, err, code = run_code(src, language="typescript")
        self.assertEqual(code, 0, f"{pattern_id}\n{out[:900]}\n{err[:600]}")
        self.assertEqual(out.strip(), "", f"{pattern_id}: {out}")

    def test_the_same_checks_cover_every_pattern(self) -> None:
        """Sharing the JavaScript checks only works while the two banks hold
        the same problems under the same names."""
        self.assertEqual(sorted(CHECKS), sorted(PATTERNS_BY_ID))


def _make(pattern_id: str):
    def test(self):
        self._run(pattern_id)

    test.__doc__ = f"Every solution in {pattern_id} type-checks, runs, answers."
    return test


for _pid in CHECKS:
    setattr(TypeScriptSolutionTests, f"test_{_pid.replace('-', '_')}", _make(_pid))

# Referenced so linters keep the imports that the generated tests rely on.
_UNUSED = (HARNESS, REPORT)


if __name__ == "__main__":
    unittest.main()
