"""Two requests saving progress at the same time.

This is not hypothetical. The UI fires several calls the moment it loads, the
server answers them on a thread pool, and on Windows replacing a file that
another handle has open is a permission error rather than a wait — so a save
landing while another thread was reading raised, and the browser got a 500 on
startup every time.

Retrying the replace was tried first and was not enough: under sustained
contention the destination is open often enough that a bounded retry still
loses. What fixes it is not letting two threads touch the file at once.

The check has to actually race. Removing the lock makes this fail within a
second, which is what makes it worth having.
"""

from __future__ import annotations

import tempfile
import threading
import time
import unittest
from pathlib import Path

from code_coach.progress.store import ProgressStore, default_progress

# Long enough to lose the race several times over without the lock, short
# enough not to be felt in the suite.
SECONDS = 1.5
WORKERS = 3


class ConcurrentAccessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path(tempfile.mkdtemp()) / "student_progress.json"
        self.store = ProgressStore(self.path)
        self.store.save(default_progress())

    def _hammer(self, work) -> list[str]:
        failures: list[str] = []
        stop = threading.Event()

        def run() -> None:
            while not stop.is_set():
                try:
                    work()
                except Exception as exc:  # noqa: BLE001 - any of them is a bug
                    failures.append(f"{type(exc).__name__}: {exc}")
                    return

        threads = [threading.Thread(target=run) for _ in range(WORKERS)]
        for t in threads:
            t.start()
        time.sleep(SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)
        return failures

    def test_saving_from_several_threads_at_once_does_not_raise(self) -> None:
        def work() -> None:
            self.store.save(self.store.load())

        self.assertEqual(self._hammer(work), [])

    def test_saving_while_another_thread_reads_does_not_raise(self) -> None:
        """The one that was actually happening: the reader holds the file open
        for the moment the writer wants to replace it."""
        stop = threading.Event()
        read_failures: list[str] = []

        def reader() -> None:
            while not stop.is_set():
                try:
                    self.store.load()
                except Exception as exc:  # noqa: BLE001
                    read_failures.append(f"{type(exc).__name__}: {exc}")
                    return

        readers = [threading.Thread(target=reader) for _ in range(WORKERS)]
        for t in readers:
            t.start()
        try:
            write_failures = self._hammer(
                lambda: self.store.save(self.store.load())
            )
        finally:
            stop.set()
            for t in readers:
                t.join(timeout=5)
        self.assertEqual(write_failures, [])
        self.assertEqual(read_failures, [])

    def test_the_file_is_never_left_half_written(self) -> None:
        """Whatever a reader sees has to be a whole document. The write goes
        to a temporary file and is moved into place for exactly this reason,
        so a torn read would mean the move had stopped being atomic."""
        stop = threading.Event()
        torn: list[str] = []

        def reader() -> None:
            while not stop.is_set():
                loaded = self.store.load()
                # A partial file parses as nothing and comes back as the
                # defaults, which would show up as a language that was never
                # stored.
                if loaded.language not in ("python", "rust"):
                    torn.append(loaded.language)
                    return

        def writer() -> None:
            while not stop.is_set():
                progress = self.store.load()
                progress.language = (
                    "rust" if progress.language == "python" else "python"
                )
                self.store.save(progress)

        threads = [threading.Thread(target=reader) for _ in range(2)]
        threads += [threading.Thread(target=writer) for _ in range(2)]
        for t in threads:
            t.start()
        time.sleep(SECONDS)
        stop.set()
        for t in threads:
            t.join(timeout=5)
        self.assertEqual(torn, [])

    def test_the_last_write_is_the_one_on_disk(self) -> None:
        """Serialising must not mean losing writes."""
        for n in range(1, 6):
            progress = self.store.load()
            progress.total_completes = n
            self.store.save(progress)
        self.assertEqual(self.store.load().total_completes, 5)

    def test_no_temporary_files_are_left_behind(self) -> None:
        def work() -> None:
            self.store.save(self.store.load())

        self.assertEqual(self._hammer(work), [])
        leftovers = list(self.path.parent.glob("*.tmp"))
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
