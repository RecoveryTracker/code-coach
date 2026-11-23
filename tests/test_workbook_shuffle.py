"""Workbook shuffle: random exercises from a range of pages.

Two halves:

- web/src/lib/workbookShuffle.ts (pure) is bundled with the esbuild already in web/node_modules and run in node: the
  furthest page reached, a typed range made sensible, the pool for a range, and the deal (every card once, no page twice
  in a row where that can be avoided, a new deck not opening on the page the last one ended on), plus the remembered range
  surviving storage that throws.
- The server: POST /api/workbook/check with `review: true` (what the shuffle sends) counts a pass but does not move "the
  page you were on", and a wrong attempt does not replace the answer you kept; without the flag nothing changed.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIB = WEB / "src" / "lib"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

needs_node = pytest.mark.skipif(
    NODE is None or not ESBUILD.exists(),
    reason="needs node and web/node_modules/esbuild (run npm install in web/)",
)

HARNESS = r"""
import * as W from "./shuffle.mjs";

const out = {};
// A book of 6 pages numbered 1..6; page p has p+1 exercises (so 27 in all), ids "p<n>-<k>".
const pages = [1, 2, 3, 4, 5, 6].map((n) => ({
  id: "p" + n, number: n, exercises: Array.from({ length: n + 1 }, (_, k) => ({ id: `p${n}-${k}` })),
}));
// A seeded random source, so the deal is repeatable.
const rng = (seed) => () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };

out.reached = {
  nothing: W.reachedPage(pages, [], ""),
  doneOn4: W.reachedPage(pages, ["p2-0", "p4-1"], ""),
  atPage5: W.reachedPage(pages, ["p2-0"], "p5"),
  atEarlier: W.reachedPage(pages, ["p4-0"], "p2"),
};
out.clean = {
  backwards: W.cleanRange({ from: 5, to: 2 }, pages),
  outside: W.cleanRange({ from: -3, to: 99 }, pages),
  nan: W.cleanRange({ from: NaN, to: 3 }, pages),
  fraction: W.cleanRange({ from: 2.4, to: 3.6 }, pages),
};
out.pool = {
  upTo3: W.poolFor(pages, { from: 1, to: 3 }).map((c) => c.exerciseId),
  just6: W.poolFor(pages, { from: 6, to: 6 }).length,
  none: W.poolFor(pages, { from: 9, to: 12 }).length,
};
{
  const pool = W.poolFor(pages, { from: 1, to: 6 });
  const runs = [];
  for (let seed = 1; seed <= 200; seed++) {
    const deck = W.deal(pool, rng(seed), "p6");
    const ids = deck.map((c) => c.exerciseId);
    let sideBySide = 0;
    for (let i = 1; i < deck.length; i++) if (deck[i].pageId === deck[i - 1].pageId) sideBySide++;
    runs.push({
      same: JSON.stringify([...ids].sort()) === JSON.stringify(pool.map((c) => c.exerciseId).sort()),
      count: ids.length, unique: new Set(ids).size, sideBySide, firstPage: deck[0].pageId,
      order: ids.join(","),
    });
  }
  out.deal = {
    allSame: runs.every((r) => r.same && r.count === 27 && r.unique === 27),
    maxSideBySide: Math.max(...runs.map((r) => r.sideBySide)),
    openedOnAvoided: runs.filter((r) => r.firstPage === "p6").length,
    distinctOrders: new Set(runs.map((r) => r.order)).size,
    // the pool itself is not reordered
    poolUntouched: pool.map((c) => c.exerciseId).join(",") === W.poolFor(pages, { from: 1, to: 6 }).map((c) => c.exerciseId).join(","),
    // one page alone cannot avoid repeats, and must not loop forever trying
    onePage: W.deal(W.poolFor(pages, { from: 3, to: 3 }), rng(7), "p3").length,
    empty: W.deal([], rng(1)).length,
  };
}
out.label = [W.rangeLabel({ from: 1, to: 21 }), W.rangeLabel({ from: 7, to: 7 })];
{
  const m = new Map();
  const st = { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, String(v)) };
  W.writeRange("python", { from: 28, to: 35 }, st);
  const bad = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };
  let threw = false;
  try { W.writeRange("python", { from: 1, to: 2 }, bad); } catch { threw = true; }
  m.set("code-coach:workbook-shuffle:dart", "{not json");
  out.storage = {
    back: W.readRange("python", st), otherLanguage: W.readRange("javascript", st),
    corrupt: W.readRange("dart", st), throwing: W.readRange("python", bad), threw,
  };
}
console.log(JSON.stringify(out));
"""


_cached: dict | None = None


def results() -> dict:
    global _cached
    if _cached is not None:
        return _cached
    tmp = Path(tempfile.mkdtemp(prefix="wb_shuffle_test_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(LIB / "workbookShuffle.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'shuffle.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120,
        )
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs")], capture_output=True, text=True, encoding="utf-8",
                             timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        _cached = json.loads(ran.stdout.strip().splitlines()[-1])
        return _cached
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@needs_node
class Rules(unittest.TestCase):
    def test_the_furthest_page_reached(self):
        r = results()["reached"]
        self.assertEqual(r["nothing"], 1, "before you start, 'up to where I am' is page 1")
        self.assertEqual(r["doneOn4"], 4, "the highest page with a solved exercise")
        self.assertEqual(r["atPage5"], 5, "the page you are on counts even with nothing solved on it")
        self.assertEqual(r["atEarlier"], 4, "being back on an earlier page does not shrink what you reached")

    def test_a_typed_range_is_made_sensible(self):
        c = results()["clean"]
        self.assertEqual(c["backwards"], {"from": 2, "to": 5})
        self.assertEqual(c["outside"], {"from": 1, "to": 6})
        self.assertEqual(c["nan"], {"from": 1, "to": 3})
        self.assertEqual(c["fraction"], {"from": 2, "to": 4})

    def test_the_pool_is_every_exercise_on_those_pages(self):
        p = results()["pool"]
        self.assertEqual(p["upTo3"], ["p1-0", "p1-1", "p2-0", "p2-1", "p2-2", "p3-0", "p3-1", "p3-2", "p3-3"])
        self.assertEqual(p["just6"], 7)
        self.assertEqual(p["none"], 0)

    def test_a_deal_is_every_card_once_shuffled(self):
        d = results()["deal"]
        self.assertTrue(d["allSame"], "200 deals: each is exactly the pool, nothing repeated or lost")
        self.assertGreater(d["distinctOrders"], 190, "it really is shuffled")
        self.assertTrue(d["poolUntouched"])

    def test_no_page_twice_in_a_row_when_it_can_be_avoided(self):
        d = results()["deal"]
        # 27 cards over 6 pages, the biggest page 7: always avoidable.
        self.assertEqual(d["maxSideBySide"], 0)
        self.assertEqual(d["openedOnAvoided"], 0, "a new deck does not open on the page the last one ended on")

    def test_one_page_or_nothing_still_deals(self):
        d = results()["deal"]
        self.assertEqual(d["onePage"], 4)
        self.assertEqual(d["empty"], 0)

    def test_labels(self):
        self.assertEqual(results()["label"], ["Pages 1–21", "Page 7"])

    def test_the_range_is_remembered_per_language_and_storage_never_throws(self):
        s = results()["storage"]
        self.assertEqual(s["back"], {"from": 28, "to": 35})
        self.assertIsNone(s["otherLanguage"])
        self.assertIsNone(s["corrupt"])
        self.assertIsNone(s["throwing"])
        self.assertFalse(s["threw"])


def _first_two_pages():
    from code_coach.workbook import pages

    book = [p for p in pages("python")]
    return book[0], book[1]


def _check(page, exercise, code, review):
    from code_coach.api import server
    from code_coach.api.schemas import WorkbookCheckRequest

    return server.workbook_check(
        WorkbookCheckRequest(page_id=page.id, exercise_id=exercise.id, code=code, language="python", review=review)
    )


def _progress():
    from code_coach.api import server

    return server._store.load()


class ReviewFlag(unittest.TestCase):
    """The shuffle's checks (review=True) leave your place and your kept answers alone."""

    def test_a_shuffle_pass_counts_but_does_not_move_your_page(self):
        p1, p2 = _first_two_pages()
        ex1, ex2 = p1.exercises[0], p2.exercises[0]
        self.assertTrue(_check(p1, ex1, ex1.answer("python"), review=False).passed)
        got = _check(p2, ex2, ex2.answer("python"), review=True)
        self.assertTrue(got.passed)
        progress = _progress()
        self.assertIn(ex2.id, progress.workbook_for("python"), "a shuffle pass marks the exercise done")
        self.assertEqual(progress.workbook_answers_for("python").get(ex2.id), ex2.answer("python"))
        from code_coach.api import server

        self.assertEqual(server.workbook("python")["at"], p1.id, "you are still on the page you were on")

    def test_a_wrong_shuffle_attempt_keeps_the_answer_you_had(self):
        p1, _ = _first_two_pages()
        ex = p1.exercises[0]
        right = ex.answer("python")
        self.assertTrue(_check(p1, ex, right, review=False).passed)
        self.assertFalse(_check(p1, ex, 'print("nope, wrong")', review=True).passed)
        self.assertEqual(_progress().workbook_answers_for("python").get(ex.id), right)

    def test_without_the_flag_nothing_changed(self):
        p1, p2 = _first_two_pages()
        ex = p2.exercises[0]
        self.assertFalse(_check(p2, ex, 'print("nope, wrong")', review=False).passed)
        self.assertEqual(_progress().workbook_answers_for("python").get(ex.id), 'print("nope, wrong")')
        from code_coach.api import server

        self.assertEqual(server.workbook("python")["at"], p2.id)
