"""Two things the whole suite needs: an isolated progress file, and room
to breathe on the clock.

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

The second is the run timeout. The app gives a student's program three
seconds, which is right in front of a person: a `while True` should stop
the screen for three seconds, not thirty. It is wrong for a suite that
starts thousands of processes back to back, where process startup alone
can eat the budget and a program that finishes in 0.3s is reported as a
possible infinite loop. That happened twice in hour-long runs, to code
that runs in well under a second when asked on its own.

So the suite raises the ceiling for its own duration. This is not
loosening the guard - a real infinite loop still dies, fifteen seconds
later instead of three, and the suite has all the patience in the world
where a person has none. What it stops is the suite crying wolf, which
is worth more than the twelve seconds: a suite that fails at random is
one you stop believing.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def _room_on_the_clock():
    """Raise the run timeout for the length of the run, and put it back.

    Set here rather than in the shell so that running one test file gets
    the same ceiling as running all of them - a flake that only appears
    in the full suite is the hardest kind to chase.
    """
    from code_coach.engine import TIMEOUT_ENV

    previous = os.environ.get(TIMEOUT_ENV)
    os.environ[TIMEOUT_ENV] = "15"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(TIMEOUT_ENV, None)
        else:
            os.environ[TIMEOUT_ENV] = previous


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
