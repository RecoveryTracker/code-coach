"""Keep the tests out of the real student's progress file.

The default ProgressStore path is ~/.code_coach/student_progress.json — the
actual saved progress of whoever is running the suite. Several tests read it
without meaning to, which makes them depend on state nobody controls: a run
would pass or fail according to which language the developer last chose in
the app, and the failure had nothing to do with the change under test.

That is exactly how the lesson deep-link bug hid. `batch_holding` was told a
language while the drill builder read this file, and for as long as those two
happened to agree the offsets lined up. They stopped agreeing when a bank
whose solutions run to more lines was added, and the link started landing on
the next problem along.

So the whole session gets a throwaway store. Nothing here can read the real
one, and nothing here can write to it either.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def _isolated_progress_store():
    """Point the app at a temporary store for the whole run."""
    from code_coach.progress.store import ProgressStore, use_store

    folder = tempfile.mkdtemp(prefix="code-coach-tests-")
    previous = use_store(ProgressStore(Path(folder) / "progress.json"))
    try:
        yield
    finally:
        use_store(previous)


@pytest.fixture(autouse=True)
def _fresh_progress_per_test():
    """And a clean one per test, so order cannot matter.

    Swapping the store rather than clearing it means a test that keeps its own
    reference to the old one is not quietly writing somewhere shared.
    """
    from code_coach.api import server
    from code_coach.progress.store import ProgressStore, active_store, use_store

    folder = tempfile.mkdtemp(prefix="code-coach-test-")
    previous = use_store(ProgressStore(Path(folder) / "progress.json"))
    was = server._store
    server._store = active_store()
    try:
        yield
    finally:
        use_store(previous)
        server._store = was
