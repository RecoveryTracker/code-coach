"""The session queue.

Most of this is arithmetic and could be checked by reading it. The two
that could not are `test_every_source_asks_progress_for_something_real`
— the sources name progress methods as strings, which is a rename away
from an AttributeError nobody sees until they open the screen — and
`test_a_practice_running_out_does_not_shorten_the_session`, which is
the edge the round-robin gets wrong if written the obvious way.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_coach.progress.store import ProgressStore, StudentProgress
from code_coach.session import SOURCES, queue


class SourceTests(unittest.TestCase):
    def test_every_source_asks_progress_for_something_real(self) -> None:
        """The counts and dates are named as strings, so a rename in the
        store leaves this pointing at nothing — and the failure lands on
        the person opening the screen rather than here."""
        progress = StudentProgress()
        for source in SOURCES:
            with self.subTest(source=source.key):
                counts = getattr(progress, source.counts_attr, None)
                last = getattr(progress, source.last_attr, None)
                self.assertTrue(
                    callable(counts),
                    f"{source.key}: no {source.counts_attr} on progress")
                self.assertTrue(
                    callable(last),
                    f"{source.key}: no {source.last_attr} on progress")
                self.assertIsInstance(counts(), dict)
                self.assertIsInstance(last(), dict)

    def test_every_source_has_items(self) -> None:
        for source in SOURCES:
            with self.subTest(source=source.key):
                items = source.items()
                self.assertTrue(items, f"{source.key} offers nothing")
                for item_id, name in items:
                    self.assertTrue(item_id)
                    self.assertTrue(name)

    def test_the_keys_are_unique(self) -> None:
        keys = [s.key for s in SOURCES]
        self.assertEqual(len(keys), len(set(keys)))

    def test_no_source_hands_out_the_same_id_twice(self) -> None:
        for source in SOURCES:
            with self.subTest(source=source.key):
                ids = [i for i, _ in source.items()]
                self.assertEqual(len(ids), len(set(ids)))


class QueueTests(unittest.TestCase):
    def setUp(self) -> None:
        self.progress = StudentProgress()

    def test_it_is_the_length_asked_for(self) -> None:
        self.assertEqual(len(queue(self.progress, 20)), 20)
        self.assertEqual(len(queue(self.progress, 3)), 3)

    def test_it_mixes_the_practices(self) -> None:
        """A queue of twenty katas is a worse session than a mixed one,
        and on a fresh profile a pure sort gives exactly that — nothing
        has been done, so the tie breaks on source order."""
        # One round of the deal is one item per practice. It was written
        # as a literal 7, which was the number of practices at the time;
        # adding the eighth broke the test without breaking the rule.
        first_round = queue(self.progress, len(SOURCES))
        self.assertEqual(
            len({item["practice"] for item in first_round}), len(SOURCES))

    def test_nothing_is_offered_twice(self) -> None:
        picked = [(i["practice"], i["id"]) for i in queue(self.progress, 40)]
        self.assertEqual(len(picked), len(set(picked)))

    def test_the_coldest_comes_first(self) -> None:
        """Something done twice should not be offered ahead of something
        never done."""
        forms = next(s for s in SOURCES if s.key == "forms")
        first_id = forms.items()[0][0]
        self.progress.record_kata(first_id)
        self.progress.record_kata(first_id)

        offered = [i["id"] for i in queue(self.progress, 40)
                   if i["practice"] == "forms"]
        self.assertTrue(offered)
        self.assertNotEqual(
            offered[0], first_id,
            "an item done twice is still being offered first")

    def test_a_practice_running_out_does_not_shorten_the_session(self) -> None:
        """The smallest practice has far fewer items than the largest.
        Dealing round-robin without noticing would stop the whole queue
        when the shortest pile empties."""
        smallest = min(len(s.items()) for s in SOURCES)
        total = sum(len(s.items()) for s in SOURCES)
        self.assertLess(smallest * len(SOURCES), total,
                        "the piles are all the same size, so this proves "
                        "nothing — pick a different check")
        wanted = smallest * len(SOURCES) + 5
        self.assertEqual(len(queue(self.progress, wanted)), wanted)

    def test_asking_for_more_than_exists_gives_everything_once(self) -> None:
        total = sum(len(s.items()) for s in SOURCES)
        everything = queue(self.progress, total + 50)
        self.assertEqual(len(everything), total)
        picked = [(i["practice"], i["id"]) for i in everything]
        self.assertEqual(len(picked), len(set(picked)))

    def test_every_item_says_where_it_goes(self) -> None:
        keys = {s.key for s in SOURCES}
        for item in queue(self.progress, 20):
            with self.subTest(item=item["id"]):
                self.assertIn(item["practice"], keys)
                self.assertTrue(item["label"])
                self.assertTrue(item["name"])


class RouteTests(unittest.TestCase):
    def test_the_route_serves_a_queue(self) -> None:
        from code_coach.api import server

        got = server.session_queue(size=10)
        self.assertEqual(len(got["items"]), 10)
        self.assertEqual(
            [p["key"] for p in got["practices"]], [s.key for s in SOURCES])

    def test_the_size_is_capped(self) -> None:
        """A stray query string should not be able to ask for the whole
        app in one response."""
        from code_coach.api import server

        self.assertLessEqual(len(server.session_queue(size=9999)["items"]), 60)
        self.assertGreaterEqual(len(server.session_queue(size=0)["items"]), 1)

    def test_it_follows_the_saved_progress(self) -> None:
        """The queue is only worth anything if it reads what you have
        actually done, so this goes through the store rather than a
        progress object made up here."""
        from code_coach.api import server
        from code_coach.progress.store import active_store, use_store

        folder = tempfile.mkdtemp(prefix="session-test-")
        previous = use_store(ProgressStore(Path(folder) / "progress.json"))
        was = server._store
        server._store = active_store()
        try:
            forms = next(s for s in SOURCES if s.key == "forms")
            first_id = forms.items()[0][0]
            progress = server._store.load()
            for _ in range(3):
                progress.record_kata(first_id)
            server._store.save(progress)

            offered = [i["id"] for i in server.session_queue(size=40)["items"]
                       if i["practice"] == "forms"]
            self.assertTrue(offered)
            self.assertNotEqual(offered[0], first_id)
        finally:
            use_store(previous)
            server._store = was


if __name__ == "__main__":
    unittest.main()


class BrowserAgreesTests(unittest.TestCase):
    """The server deals the queue; the browser has to know every kind.

    Each card names a practice, and the browser turns that into the key
    the screen reads on the way in and the screen to open. Those live in
    web/src/lastKeys.ts, whose own comment says the two sides must agree
    - and until this test nothing checked that they did. A source the
    server deals and the browser does not know is a card that opens the
    wrong screen, or nothing, with no error anywhere.
    """

    def _block(self, name: str) -> str:
        from pathlib import Path
        import re

        text = (Path(__file__).resolve().parent.parent
                / "web" / "src" / "lastKeys.ts").read_text(encoding="utf-8")
        m = re.search(rf"{name}[^=]*=\s*\{{(.*?)\}}", text, flags=re.S)
        self.assertIsNotNone(m, f"no {name} in lastKeys.ts")
        return m.group(1)

    def test_every_source_has_a_last_key(self) -> None:
        import re

        known = set(re.findall(r"^\s*(\w+):", self._block("LAST_KEYS"), re.M))
        for source in SOURCES:
            with self.subTest(source=source.key):
                self.assertIn(source.key, known)

    def test_every_source_has_a_screen(self) -> None:
        import re

        known = set(re.findall(r"^\s*(\w+):", self._block("MODE_FOR"), re.M))
        for source in SOURCES:
            with self.subTest(source=source.key):
                self.assertIn(source.key, known)
