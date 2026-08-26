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
            f"{TYPED_HARNESS}\n{checks}\n{TYPED_REPORT}"
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
