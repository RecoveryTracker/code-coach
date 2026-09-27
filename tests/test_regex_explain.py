"""The Regex screen's pattern explainer, run for real.

It lives in the browser (web/src/lib/regexExplain.ts) so it can explain a
pattern as it is typed. This compiles it with tsc and runs a Node check
against hand-written readings, and against every answer and pitfall in
the Regex tasks, none of which may come back "not understood".
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_coach.engine import _find_tsc
from code_coach.regex import tasks

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "web" / "src" / "lib" / "regexExplain.ts"
CHECK = ROOT / "web" / "src" / "lib" / "__checks__" / "regexExplain.check.cjs"


class ExplainTests(unittest.TestCase):

    def test_it_reads_patterns_as_written_by_hand(self) -> None:
        tsc, node = _find_tsc(), shutil.which("node")
        if not (tsc and node):
            self.skipTest("needs Node and tsc (npm install in web/)")
        patterns = sorted({p for t in tasks() for p in (t.answer, *t.pitfalls)})
        with tempfile.TemporaryDirectory() as out:
            build = subprocess.run(
                [node, str(tsc), str(MODULE), "--outDir", out, "--module", "commonjs",
                 "--target", "es2020", "--skipLibCheck"],
                capture_output=True, text=True, timeout=120)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            ran = subprocess.run(
                [node, str(CHECK)], capture_output=True, text=True, timeout=60,
                env={**os.environ, "EXPLAIN_OUT": out, "PATTERNS": json.dumps(patterns)})
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)


if __name__ == "__main__":
    unittest.main()
