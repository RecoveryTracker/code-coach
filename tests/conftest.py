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

import faulthandler
import os
import tempfile
from pathlib import Path

import pytest


#: How long one test may take before the run is treated as hung.
#:
#: Generous, because it has to clear the slowest honest test in here:
#: running every workbook exercise in one language is a single test and
#: takes about a quarter of an hour. Anything past half an hour is not
#: slow, it is stuck.
WATCHDOG_SECONDS = float(os.environ.get("CODE_COACH_WATCHDOG", "1800"))

#: Where a hang leaves its evidence. Rewritten at the start of every
#: test, so afterwards it either holds a traceback and the name of the
#: test that hung, or just the line saying nothing did.
HANG_REPORT = Path(tempfile.gettempdir()) / "code-coach-hang.txt"


@pytest.fixture(autouse=True)
def _never_hang_silently(request):
    """Turn a hang into a traceback instead of a wait.

    A test that blocks forever is the worst failure this suite can
    have, because it does not look like a failure. The run simply stops
    printing, and whoever started it keeps waiting — an hour, in the
    case that prompted this.

    It happened three times, always in the same place, and was
    diagnosed only by attaching faulthandler by hand. So faulthandler
    is attached always: if a single test outlives the budget, the
    process dumps every thread's stack, naming the file and line that
    is stuck, and exits. A dead run with a traceback can be read. A
    live run with nothing in it cannot.

    The dump goes to a file rather than to stderr, which is the part
    that had to be learned by getting it wrong. faulthandler exits the
    process the instant it fires; pytest is capturing output at the
    time; the captured buffer dies with the process. So the run ended —
    good — with nothing whatsoever to read, which is most of the value
    gone. A file survives.

    Set CODE_COACH_WATCHDOG to change the budget, or to something small
    to check the watchdog itself still works.
    """
    HANG_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with HANG_REPORT.open("w", encoding="utf-8") as report:
        report.write(
            f"A traceback below means a test outlived "
            f"{WATCHDOG_SECONDS:.0f}s and the run was stopped.\n"
            f"The test was: {request.node.nodeid}\n\n"
        )
        report.flush()
        faulthandler.dump_traceback_later(
            WATCHDOG_SECONDS, exit=True, file=report)
        try:
            yield
        finally:
            faulthandler.cancel_dump_traceback_later()


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
