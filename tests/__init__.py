"""Tests, and the one thing that must be true before any of them run.

The suite must never touch the real progress file. Several tests record
a correct answer as part of checking that recording works, and the
default store is ~/.code_coach/student_progress.json — somebody's actual
practice history.

This used to be handled entirely by conftest.py, which works and is
loaded only by pytest. Running the same tests the way the README told
people to —

    python -m unittest discover -s tests

— skipped it silently and wrote sixteen magnet puzzles and eight
workbook exercises into a real progress file that had just been reset on
purpose. Nothing failed. Nothing warned. The counts simply appeared.

So the redirect lives here, in the package every runner imports before
it can import a test. conftest.py still gives each test a fresh store on
top of this; what this guarantees is that the store was never the real
one in the first place, whichever way the suite was started.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from code_coach.progress.store import ProgressStore, use_store

#: Kept on the module so it is not garbage collected mid-run, and so a
#: test that wants to know where it landed can ask.
SANDBOX = Path(tempfile.mkdtemp(prefix="code-coach-suite-"))

use_store(ProgressStore(SANDBOX / "progress.json"))
