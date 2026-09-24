"""SQL case files: every answer really is in the data, and only there.

The answers are written by hand and the server is the check on them.
Each step's reference query has to return that answer and nothing
else - one row - on real PostgreSQL. And each step's decoy, the query
someone plausibly writes first, must not: a step whose careless query
also finds the answer is a step that does not test what it says.

The parts that need no server - the loose answer comparison, the table
listing - are tested without one.
"""

from __future__ import annotations

import re
import unittest

from code_coach import pg_server
from code_coach.casefiles import case, cases, normal, run_query, same, tables, values
from code_coach.pg_runner import _split

HAS_SERVER = pg_server.available() and pg_server.initialised()
WHY_NOT = "no local PostgreSQL — run tools/get_postgres.py"


class CollectionTests(unittest.TestCase):

    def test_ids_are_unique_and_findable(self) -> None:
        ids = [c.id for c in cases()]
        self.assertEqual(len(ids), len(set(ids)))
        for c in cases():
            self.assertIs(case(c.id), c)

    def test_they_read_easiest_first(self) -> None:
        levels = [c.level for c in cases()]
        self.assertEqual(levels, sorted(levels))

    def test_every_case_says_what_it_needs_to(self) -> None:
        for c in cases():
            with self.subTest(case=c.id):
                self.assertGreaterEqual(len(c.steps), 2)
                for text in (c.title, c.story, c.ending):
                    self.assertTrue(text.strip())
                for s in c.steps:
                    for text in (s.question, s.answer, s.hint, s.lesson):
                        self.assertTrue(text.strip())

    def test_the_answer_is_not_given_away_in_the_text(self) -> None:
        """Only the data holds it. A question that names its own answer
        is a reading test."""
        for c in cases():
            for n, s in enumerate(c.steps):
                shown = " ".join([c.story, s.question, s.hint] + [
                    t.question for t in c.steps[:n + 1]])
                with self.subTest(case=c.id, step=n + 1):
                    # As a whole word: the answer 2 is not given away by 2026.
                    word = r"(?<!\w)" + re.escape(normal(s.answer)) + r"(?!\w)"
                    self.assertIsNone(re.search(word, normal(shown)))

    def test_setup_only_makes_temporary_tables(self) -> None:
        """Nothing a case does may outlive it or touch the practice data.
        Temporary tables are both: private to the run, and gone at the
        rollback."""
        for c in cases():
            made = {t["name"] for t in tables(c)}
            for statement in _split(c.setup):
                with self.subTest(case=c.id, statement=statement[:40]):
                    head = " ".join(statement.split()[:3]).upper()
                    if head.startswith("CREATE"):
                        self.assertEqual(head, "CREATE TEMP TABLE")
                    else:
                        match = re.match(r"INSERT\s+INTO\s+(\w+)", statement, re.I)
                        self.assertIsNotNone(match, statement[:60])
                        self.assertIn(match.group(1), made)


class LooseAnswerTests(unittest.TestCase):

    def test_case_spacing_and_quotes_do_not_matter(self) -> None:
        for given in ("eve lund", "  Eve   Lund ", "'Eve Lund'", '"EVE LUND"'):
            with self.subTest(given=given):
                self.assertTrue(same(given, "Eve Lund"))

    def test_a_different_answer_is_still_wrong(self) -> None:
        for given in ("Eve", "Eve Lunds", "", "  ", "''"):
            with self.subTest(given=given):
                self.assertFalse(same(given, "Eve Lund"))


class ValuesTests(unittest.TestCase):

    def test_reads_the_rows_under_the_dashes(self) -> None:
        self.assertEqual(values("name\n------\nAda\nBen\n"), ["Ada", "Ben"])

    def test_no_rows_is_no_values(self) -> None:
        self.assertEqual(values("(no rows)\n"), [])


@unittest.skipUnless(HAS_SERVER, WHY_NOT)
class AgainstTheServerTests(unittest.TestCase):

    def test_each_reference_query_returns_the_answer_and_only_it(self) -> None:
        for c in cases():
            for n, s in enumerate(c.steps, 1):
                with self.subTest(case=c.id, step=n):
                    out, err, code = run_query(c, s.reference)
                    self.assertEqual((err, code), ("", 0))
                    got = values(out)
                    self.assertEqual(len(got), 1, out)
                    self.assertTrue(same(got[0], s.answer), f"{got[0]!r} vs {s.answer!r}")

    def test_each_decoy_misses(self) -> None:
        for c in cases():
            for n, s in enumerate(c.steps, 1):
                with self.subTest(case=c.id, step=n):
                    out, err, code = run_query(c, s.decoy)
                    # It has to run - a decoy that errors proves nothing.
                    self.assertEqual((err, code), ("", 0))
                    got = values(out)
                    self.assertFalse(
                        len(got) == 1 and same(got[0], s.answer),
                        f"the careless query also finds {s.answer!r}")

    def test_the_listed_tables_are_the_ones_the_server_makes(self) -> None:
        for c in cases():
            with self.subTest(case=c.id):
                out, err, code = run_query(c, (
                    "SELECT table_name || '.' || column_name FROM "
                    "information_schema.columns WHERE table_schema LIKE 'pg_temp%' "
                    "ORDER BY 1"))
                self.assertEqual((err, code), ("", 0))
                listed = sorted(f"{t['name']}.{col['name']}"
                                for t in tables(c) for col in t["columns"])
                self.assertEqual(values(out), listed)

    def test_a_change_does_not_outlive_the_run(self) -> None:
        c = cases()[0]
        first = c.steps[0]
        out, err, _ = run_query(c, "DELETE FROM loans; SELECT count(*) FROM loans")
        self.assertEqual(err, "")
        out, err, _ = run_query(c, first.reference)
        self.assertTrue(same(values(out)[0], first.answer))

    def test_nothing_to_run_says_so(self) -> None:
        out, err, code = run_query(cases()[0], "  ;  ")
        self.assertEqual(out, "")
        self.assertIn("Nothing to run", err)


class RouteTests(unittest.TestCase):

    def test_the_list_carries_no_answers_or_queries(self) -> None:
        from code_coach.api.server import case_list

        # Each step sends its question and hint and nothing else. Whether
        # those give the answer away is test_the_answer_is_not_given_away;
        # searching the whole entry instead trips on "level: 2" when the
        # answer is 2.
        listed = case_list()["cases"]
        self.assertEqual([e["id"] for e in listed], [c.id for c in cases()])
        for entry, c in zip(listed, cases()):
            text = repr(entry)
            for n, (sent, s) in enumerate(zip(entry["steps"], c.steps), 1):
                with self.subTest(case=c.id, step=n):
                    self.assertEqual(sent, {"question": s.question, "hint": s.hint})
                    self.assertNotIn(s.reference, text)
                    self.assertNotIn(s.decoy, text)

    def test_only_the_last_step_counts_the_case(self) -> None:
        from code_coach.api.schemas import CaseAnswerRequest
        from code_coach.api.server import _store, case_answer

        c = cases()[0]
        wrong = case_answer(CaseAnswerRequest(case_id=c.id, step=0, answer="nope"))
        self.assertFalse(wrong.right)
        self.assertEqual(wrong.lesson, "", "a wrong answer must not get the lesson")
        for n, s in enumerate(c.steps):
            got = case_answer(CaseAnswerRequest(case_id=c.id, step=n, answer=s.answer.upper()))
            self.assertTrue(got.right)
            last = n == len(c.steps) - 1
            self.assertEqual(bool(got.ending), last)
        self.assertEqual(_store.load().case_counts()[c.id], 1)

    def test_a_step_that_does_not_exist_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.server import case_reveal

        with self.assertRaises(HTTPException):
            case_reveal(case_id=cases()[0].id, step=99)


if __name__ == "__main__":
    unittest.main()
