"""The saved editor buffer belongs to one exercise, and only shows up there.

This started as a bug report: "the code I've typed into the editor doesn't
match the problem... it seems like the files are getting mixed up." It was
real. A draft was addressed purely by position — drill, language, difficulty,
window, index — and two compatibility fallbacks read a neighbouring slot when
the current one was empty. Position is not identity: window 0 exercise 3 and
window 5 exercise 3 are different problems.

The reason this is a Python test running JavaScript, rather than a browser
check, is that a browser check could not see it. Monaco does not lay out in a
headless pane, so reading the editor returns nothing and every assertion about
it passes or fails for reasons that have nothing to do with the code. So the
draft logic lives in its own module, and here it is compiled and run for real
against a stub store — the same discipline the solution banks get.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_coach.engine import _find_tsc

ROOT = Path(__file__).resolve().parent.parent
MODULE = ROOT / "web" / "src" / "lib" / "drafts.ts"
CHECK = ROOT / "web" / "src" / "lib" / "__checks__" / "drafts.check.cjs"


def _tooling() -> tuple[Path, str] | None:
    tsc, node = _find_tsc(), shutil.which("node")
    return (tsc, node) if tsc and node else None


class DraftTests(unittest.TestCase):
    def test_the_module_is_where_the_check_expects_it(self) -> None:
        """Fails loudly if the module moves, rather than skipping quietly."""
        self.assertTrue(MODULE.exists(), MODULE)
        self.assertTrue(CHECK.exists(), CHECK)

    def test_the_component_does_not_keep_its_own_copy(self) -> None:
        """A second implementation in App.tsx would go unchecked."""
        app = (ROOT / "web" / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn('from "./lib/drafts"', app)
        self.assertNotIn("function loadDraft", app)
        # The fallbacks that caused the report. They must not come back.
        self.assertNotIn("preWindowDraftKey", app)
        self.assertNotIn("legacyDraftKey", app)

    def test_a_draft_only_returns_under_its_own_exercise(self) -> None:
        tools = _tooling()
        if tools is None:
            self.skipTest("needs Node and tsc (npm install in web/)")
        tsc, node = tools
        with tempfile.TemporaryDirectory() as out:
            build = subprocess.run(
                [
                    node, str(tsc), str(MODULE),
                    "--outDir", out,
                    "--module", "commonjs",
                    "--target", "es2020",
                    "--lib", "es2020,dom",
                    "--skipLibCheck",
                ],
                capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            ran = subprocess.run(
                [node, str(CHECK)],
                capture_output=True, text=True, timeout=60,
                env={**os.environ, "DRAFTS_OUT": out},
            )
        self.assertEqual(ran.returncode, 0, ran.stdout + ran.stderr)


if __name__ == "__main__":
    unittest.main()
