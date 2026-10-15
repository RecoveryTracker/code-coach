"""Momentum's screen logic: what the strip and the toasts say for what the server sent.

web/src/lib/momentumView.ts is pure TypeScript (no React, no fetch), and the web project
has no JavaScript test runner, so - like tests/test_brain_round.py and
tests/test_farm_scene.py - this bundles it with the esbuild already in web/node_modules
and runs it in node. The inputs and every expected value are written here, in Python;
nothing is read back from the module to say what it should have said.

What is checked: which toasts an award earns and in what order; that a repeat earns none;
the limit of three on screen and who gives way first; that a level-up card is shown first
and survives a flood; the strip's numbers (XP bar, quest count, chest state, the 14 bars,
weekday names); and that nothing it says talks about losing anything.
"""

from __future__ import annotations

import functools
import json
import random
import shutil
import subprocess
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIB = WEB / "src" / "lib"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not ESBUILD.exists(),
    reason="needs node and web/node_modules/esbuild (run npm install in web/)",
)

HARNESS = r"""
import * as V from "./view.mjs";
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
let id = 0;
const next = () => ++id;
const brief = (ts) => ts.map((t) => [t.kind, t.text, t.sub ?? null, t.ms]);
const out = {};

out.awards = input.awards.map((r) => { id = 0; return brief(V.toastsForAward(r, next)); });
out.ids = (() => { id = 100; return V.toastsForAward(input.awards[3], next).map((t) => t.id); })();
out.answers = input.answer_lists.map((list) => { id = 0; return brief(V.toastsForAnswers(list, next)); });
out.answers_single = (() => { id = 0; return brief(V.toastsForAnswers(input.awards[0], next)); })();
out.answers_none = [null, undefined, []].map((x) => V.toastsForAnswers(x, () => 1).length);
out.welcome = input.welcomes.map((w) => V.welcomeView(w));
out.chests = input.chests.map((r) => { id = 0; return brief(V.toastsForChest(r, next)); });

// The stack: each scenario is [current kinds, incoming kinds] -> kinds left, in display order.
const mk = (kind, n) => ({ id: n, kind, text: kind + n, ms: 2500 });
out.stacks = input.stacks.map(([cur, inc]) => {
  let n = 0;
  const left = V.enqueue(cur.map((k) => mk(k, ++n)), inc.map((k) => mk(k, ++n)));
  return left.map((t) => [t.kind, t.id]);
});
out.dismissed = (() => {
  const list = [mk("xp", 1), mk("combo", 2), mk("quest", 3)];
  return V.dismiss(list, 2).map((t) => t.id).concat(V.dismiss(list, 99).map((t) => t.id));
})();
out.custom_max = V.enqueue([mk("xp", 1), mk("combo", 2)], [mk("quest", 3)], 2).map((t) => t.kind);

out.hud = input.summaries.map((s) => V.hudView(s));
out.hud_null = V.hudView(null);
out.mult = input.mults.map((m) => V.multText(m));
out.weekday = input.days.map((d) => V.weekday(d));
out.bars = V.bars(input.bars);

process.stdout.write(JSON.stringify(out));
"""


def quest(label: str, have: int, need: int, just: bool = False) -> dict:
    return {"id": label.lower().replace(" ", "-"), "label": label, "have": have, "need": need,
            "done": have >= need, "just_done": just}


def summary(**over) -> dict:
    s = {
        "ok": True, "xp_total": 1234, "level": 5, "title": "Apprentice", "xp_in_level": 340,
        "xp_for_next": 500, "streak": 5, "today_counted": True, "best_streak": 12, "freezes": 1,
        "quests": [quest("Solve 3 things", 2, 3), quest("Type a snippet", 1, 1), quest("Earn 100 XP", 40, 100)],
        "chest_ready": False, "chest_claimed": False, "today_xp": 40,
        "days_last_14": [{"day": (date(2026, 10, 2) + timedelta(days=i)).isoformat(), "xp": 0} for i in range(14)],
    }
    s.update(over)
    return s


def award(**over) -> dict:
    r = summary()
    r.update({"repeat": False, "base": 20, "combo": 1, "combo_mult": 1.0, "lucky": None, "gained": 20,
              "level_up": None, "streak_extended": False, "freeze_used": None, "freeze_earned": False})
    r.update(over)
    return r


AWARDS = [
    award(),                                                                  # 0 plain
    award(combo=4, combo_mult=1.4, gained=28),                                # 1 combo
    award(lucky=3, gained=60, base=20),                                       # 2 lucky x3 on 20
    award(combo=3, combo_mult=1.2, lucky=2, gained=48, base=20,
          quests=[quest("Type a snippet", 1, 1, just=True), quest("Earn 100 XP", 100, 100, just=True)],
          streak_extended=True, streak=7, freeze_earned=True,
          level_up={"level": 6, "title": "Coder"}),                           # 3 everything
    award(repeat=True, gained=0),                                             # 4 repeat
    {"ok": False},                                                            # 5 storage trouble
    award(streak_extended=True, streak=3),                                    # 6 streak, no freeze
    award(freeze_used="2026-10-14"),                                          # 7 a freeze spent
    award(freeze_earned=True),                                                # 8 earned, not extended
    award(gained=0, base=0, combo_mult=1.0),                                  # 9 nothing paid
    award(label="Farm: first pumpkin! (Python)", base=20, gained=20),         # 10 a milestone
    award(label="Farm: first pumpkin! (Python)", base=20, gained=44, combo=3, combo_mult=1.1,
          lucky=2),                                                           # 11 milestone + combo + luck
    award(label="Farm: first hay! (Original)", repeat=True, gained=0),        # 12 a labelled repeat
    award(label=None),                                                        # 13 label explicitly null
    award(label="", base=20, gained=20),                                      # 14 empty label
    award(label="Welcome back", base=15, gained=16, combo_mult=1.1, combo=2,
          level_up={"level": 3, "title": "Learner"}),                         # 15 the welcome-back
]

ANSWER_LISTS = [
    [AWARDS[10], award(label="Farm: first carrot! (Python)", base=15, gained=15), AWARDS[12]],
    [award(gained=0, base=0, quests=[quest("Harvest 50 items on the farm", 50, 50, just=True)])],
    [],
    [AWARDS[5], AWARDS[10]],
]

WELCOMES = [
    {"minutes": 95, "ripe": 0, "xp": 15, "language": "python"},
    {"minutes": 40, "ripe": 1, "xp": 15, "language": "original"},
    {"minutes": 600, "ripe": 37, "xp": 18, "language": "javascript"},
    {"minutes": 31, "ripe": 1234, "xp": 25, "language": "dart"},
]

CHESTS = [
    summary(gained=85, freeze_earned=False, level_up=None),
    summary(gained=120, freeze_earned=True, level_up={"level": 7, "title": "Practitioner"}),
    {"ok": False, "gained": 0},
]

STACKS = [
    [[], ["xp"]],
    [["xp", "combo"], ["lucky", "quest", "level"]],
    [["level"], ["level", "level", "level"]],
    [["xp", "combo", "quest"], ["level"]],
    [["quest", "streak", "lucky"], ["xp"]],
    [["xp"], ["combo", "xp", "combo", "xp", "combo"]],
    [["level", "xp"], ["level"]],
    [["xp", "combo"], ["milestone", "xp", "combo", "milestone", "quest"]],
    [["milestone", "xp", "combo"], ["level", "xp"]],
]

MULTS = [1.4, 2, 1.1000000000000001, 1.25, 1.0, 1.96]


@functools.cache
def results() -> dict:
    days = [(date(2026, 1, 1) + timedelta(days=n * 11)).isoformat() for n in range(40)] + ["2026-10-15"]
    bars = [{"day": f"2026-10-{d:02d}", "xp": xp} for d, xp in zip(range(2, 16), [0, 50, 100, 1, 0, 25, 99, 0, 0, 0, 10, 0, 100, 37])]
    rng = random.Random(3)
    summaries = [
        summary(),
        summary(streak=0, today_counted=False, freezes=0, quests=[], chest_ready=False),
        summary(streak=5, today_counted=False, freezes=2),
        summary(streak=1, today_counted=True, chest_ready=True,
                quests=[quest("a", 1, 1), quest("b", 1, 1), quest("c", 1, 1)]),
        summary(chest_claimed=True, quests=[quest("a", 1, 1), quest("b", 1, 1), quest("c", 1, 1)]),
        summary(xp_in_level=0, xp_for_next=200),
        summary(xp_in_level=199, xp_for_next=200),
        summary(xp_in_level=999, xp_for_next=200),
        summary(xp_total=1234567),
    ] + [summary(streak=rng.randrange(0, 40), today_counted=rng.random() < 0.5, freezes=rng.randrange(0, 3),
                 xp_in_level=rng.randrange(0, 300), xp_for_next=rng.randrange(100, 900)) for _ in range(40)]
    tmp = Path(tempfile.mkdtemp(prefix="momentum_view_test_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        (tmp / "in.json").write_text(json.dumps({
            "awards": AWARDS, "answer_lists": ANSWER_LISTS, "welcomes": WELCOMES, "chests": CHESTS, "stacks": STACKS, "summaries": summaries,
            "mults": MULTS, "days": days, "bars": bars}), encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(LIB / "momentumView.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'view.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120)
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs"), str(tmp / "in.json")],
                             capture_output=True, text=True, timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        out = json.loads(ran.stdout.strip().splitlines()[-1])
        out["_summaries"] = summaries
        out["_days"] = days
        return out
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class ToastsForAwards(unittest.TestCase):
    def test_a_plain_award_says_the_xp_and_nothing_else(self) -> None:
        self.assertEqual(results()["awards"][0], [["xp", "+20 XP", None, 2500]])

    def test_a_combo_adds_one_line_with_the_multiplier(self) -> None:
        self.assertEqual(results()["awards"][1], [["xp", "+28 XP", None, 2500], ["combo", "Combo x1.4", None, 2500]])

    def test_luck_is_the_part_on_top_of_what_the_xp_line_says(self) -> None:
        # 20 base x 3 = 60 in all: "+20 XP" and the lucky line adds the other 40.
        self.assertEqual(results()["awards"][2], [["xp", "+20 XP", None, 2500], ["lucky", "Lucky! x3 (+40)", None, 2500]])

    def test_everything_at_once_comes_in_a_fixed_order(self) -> None:
        got = results()["awards"][3]
        self.assertEqual([t[0] for t in got], ["xp", "combo", "lucky", "quest", "quest", "streak", "level"])
        # gained 48 with lucky x2: the plain part is 24, the bonus 24
        self.assertEqual(got[0][1], "+24 XP")
        self.assertEqual(got[2][1], "Lucky! x2 (+24)")
        self.assertEqual([t[1] for t in got[3:5]], ["Quest done: Type a snippet", "Quest done: Earn 100 XP"])
        self.assertEqual(got[5][1], "Streak 7 - freeze earned")
        self.assertEqual(got[6][:3], ["level", "Level 6", "Coder"])

    def test_the_level_up_card_stays_longer_than_a_toast(self) -> None:
        got = results()["awards"][3]
        self.assertEqual(got[6][3], 4000)
        self.assertTrue(all(t[3] == 2500 for t in got[:6]))

    def test_a_repeat_or_a_failed_save_or_nothing_paid_celebrates_nothing(self) -> None:
        for i in (4, 5):
            self.assertEqual(results()["awards"][i], [])
        self.assertEqual(results()["awards"][9], [])

    def test_streak_lines(self) -> None:
        self.assertEqual(results()["awards"][6][1], ["streak", "Streak 3", None, 2500])
        self.assertEqual(results()["awards"][7][1], ["freeze", "Freeze used - your streak is safe", None, 2500])
        self.assertEqual(results()["awards"][8][1], ["freeze", "Freeze earned", None, 2500])

    def test_every_toast_has_its_own_id(self) -> None:
        ids = results()["ids"]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_the_chest(self) -> None:
        a, b, c = results()["chests"]
        self.assertEqual(a, [["chest", "Chest: +85 XP", None, 2500]])
        self.assertEqual([t[1] for t in b], ["Chest: +120 XP", "Freeze earned", "Level 7"])
        self.assertEqual(b[2][2], "Practitioner")
        self.assertEqual(c, [])


class TheLabelToast(unittest.TestCase):
    """A server-paid award says what it was for, first, then what it paid."""

    def test_the_label_leads_and_then_the_xp(self) -> None:
        self.assertEqual(results()["awards"][10], [["milestone", "Farm: first pumpkin! (Python)", None, 2500],
                                                   ["xp", "+20 XP", None, 2500]])

    def test_the_label_is_one_line_before_a_combo_and_a_lucky_bonus(self) -> None:
        got = results()["awards"][11]
        self.assertEqual([t[0] for t in got], ["milestone", "xp", "combo", "lucky"])
        self.assertEqual(got[0][1], "Farm: first pumpkin! (Python)")
        self.assertEqual(got[1][1], "+22 XP")  # 44 paid with lucky x2: the plain part is 22
        self.assertEqual(got[3][1], "Lucky! x2 (+22)")

    def test_a_repeat_says_nothing_even_with_a_label(self) -> None:
        self.assertEqual(results()["awards"][12], [])

    def test_no_label_or_an_empty_one_adds_no_line(self) -> None:
        self.assertEqual(results()["awards"][13], [["xp", "+20 XP", None, 2500]])
        self.assertEqual(results()["awards"][14], [["xp", "+20 XP", None, 2500]])
        self.assertEqual(results()["awards"][0], [["xp", "+20 XP", None, 2500]])

    def test_the_welcome_back_is_a_label_and_a_level_card_can_follow(self) -> None:
        got = results()["awards"][15]
        self.assertEqual([t[0] for t in got], ["milestone", "xp", "combo", "level"])
        self.assertEqual(got[0][1], "Welcome back")
        self.assertEqual(got[1][1], "+16 XP")

    def test_a_list_of_answers_is_told_oldest_first_each_in_its_own_order(self) -> None:
        a, quest_only, empty, with_failure = results()["answers"]
        self.assertEqual([t[1] for t in a], ["Farm: first pumpkin! (Python)", "+20 XP",
                                             "Farm: first carrot! (Python)", "+15 XP"])  # the repeat adds none
        self.assertEqual(quest_only, [["quest", "Quest done: Harvest 50 items on the farm", None, 2500]])
        self.assertEqual(empty, [])
        self.assertEqual([t[1] for t in with_failure], ["Farm: first pumpkin! (Python)", "+20 XP"],
                         "an answer the server could not keep is skipped, the rest still shown")

    def test_one_answer_or_nothing_also_works(self) -> None:
        self.assertEqual(results()["answers_single"], [["xp", "+20 XP", None, 2500]])
        self.assertEqual(results()["answers_none"], [0, 0, 0])

    def test_a_milestone_outranks_an_xp_line_but_not_a_level_card(self) -> None:
        # In a crowd the XP and combo lines give way before the label does.
        got = results()["stacks"][7]
        self.assertEqual([k for k, _ in got], ["milestone", "milestone", "quest"])
        # [milestone, xp, combo] + [level, xp]: the combo goes, then the older xp line; the level card leads.
        self.assertEqual([k for k, _ in results()["stacks"][8]], ["level", "milestone", "xp"])


class TheWelcomeCard(unittest.TestCase):
    def test_what_is_ripe_in_words(self) -> None:
        quiet, one, some, many = results()["welcome"]
        self.assertEqual(quiet["body"], "The farm is quiet and still.")
        self.assertEqual(one["body"], "1 tile is ripe.")
        self.assertEqual(some["body"], "37 tiles are ripe.")
        self.assertEqual(many["body"], "1,234 tiles are ripe.")

    def test_the_buttons_and_title(self) -> None:
        for w in results()["welcome"]:
            self.assertEqual((w["title"], w["claim"], w["dismiss"]),
                             ("Welcome back", "Claim welcome-back XP", "Not now"))

    def test_it_is_honest_that_the_farm_waits(self) -> None:
        for w in results()["welcome"]:
            self.assertIn("nothing grows while you are away", w["note"])

    def test_no_clock_no_pressure_and_nothing_about_losing_anything(self) -> None:
        banned = ("lose", "lost", "miss", "expire", "hurry", "last chance", "only", "left", "ago", "hour", "minute",
                  "count", "!", "don't", "before", "soon", "rot", "wilt", "die")
        for w in results()["welcome"]:
            for field in ("title", "body", "note", "claim", "dismiss"):
                text = w[field].lower()
                for word in banned:
                    self.assertNotIn(word, text, f"{field}: {w[field]!r}")


class TheStack(unittest.TestCase):
    def kinds(self, i: int) -> list[str]:
        return [k for k, _ in results()["stacks"][i]]

    def test_never_more_than_three_on_screen(self) -> None:
        for i in range(len(STACKS)):
            self.assertLessEqual(len(results()["stacks"][i]), 3)

    def test_a_short_stack_is_left_alone(self) -> None:
        self.assertEqual(self.kinds(0), ["xp"])

    def test_the_least_important_give_way_first_and_the_level_card_leads(self) -> None:
        self.assertEqual(self.kinds(1), ["level", "lucky", "quest"])

    def test_a_flood_of_level_ups_shows_one_card_the_newest(self) -> None:
        got = results()["stacks"][2]
        self.assertEqual([k for k, _ in got], ["level"])
        self.assertEqual([i for _, i in got], [4], "ids 1-3 are older cards; the last of the four stays")

    def test_a_new_level_up_replaces_an_old_one_and_leaves_the_rest(self) -> None:
        got = results()["stacks"][6]
        self.assertEqual(got, [["level", 3], ["xp", 2]])

    def test_a_level_up_is_never_what_goes_while_something_else_could(self) -> None:
        self.assertIn("level", self.kinds(3))
        self.assertEqual(self.kinds(3)[0], "level")
        self.assertEqual(self.kinds(3), ["level", "xp", "quest"])  # the combo went

    def test_a_quest_outranks_an_xp_line(self) -> None:
        self.assertEqual(self.kinds(4), ["quest", "streak", "lucky"])

    def test_a_combo_note_is_the_first_to_go(self) -> None:
        self.assertEqual(self.kinds(5), ["xp", "xp", "xp"])

    def test_dismiss_removes_one_and_ignores_an_unknown_id(self) -> None:
        self.assertEqual(results()["dismissed"], [1, 3, 1, 2, 3])

    def test_the_limit_can_be_set(self) -> None:
        self.assertEqual(results()["custom_max"], ["xp", "quest"])


class TheStrip(unittest.TestCase):
    def view(self, i: int) -> dict:
        return results()["hud"][i]

    def test_the_numbers_for_an_ordinary_day(self) -> None:
        v = self.view(0)
        self.assertEqual(v["streak"], "5")
        self.assertTrue(v["flameLit"])
        self.assertEqual(v["levelText"], "Lv 5 Apprentice")
        self.assertEqual(v["levelShort"], "Lv 5")
        self.assertEqual(v["xpPct"], round(340 / 500 * 100))
        self.assertEqual(v["xpText"], "340 / 500 XP")
        self.assertEqual((v["questText"], v["questsDone"], v["questsTotal"]), ("1/3", 1, 3))
        self.assertEqual(v["chest"], "locked")
        self.assertEqual(v["bestText"], "Best streak 12")
        self.assertEqual(v["freezes"], 1)
        self.assertEqual(v["totalText"], "1,234 XP in all")

    def test_a_streak_not_yet_added_to_today_is_dim_and_the_note_says_what_to_do(self) -> None:
        v = self.view(2)
        self.assertFalse(v["flameLit"])
        self.assertIn("do one thing today", v["streakNote"])
        self.assertIn("5 days", v["streakNote"])

    def test_no_streak_invites_a_start(self) -> None:
        v = self.view(1)
        self.assertEqual(v["streak"], "0")
        self.assertEqual(v["streakNote"], "Do one thing today to start a streak")
        self.assertEqual(v["questText"], "0/3", "three quests are expected even before any are listed")
        self.assertIn("every 7th day", v["freezeNote"])

    def test_one_day_is_not_plural(self) -> None:
        self.assertIn("1 day in a row", self.view(3)["streakNote"])

    def test_chest_states(self) -> None:
        self.assertEqual(self.view(3)["chest"], "ready")
        self.assertEqual(self.view(4)["chest"], "opened")
        self.assertEqual(self.view(0)["chest"], "locked")
        self.assertIn("ready", self.view(3)["chestNote"])

    def test_the_xp_bar_is_clamped_to_the_bar(self) -> None:
        self.assertEqual(self.view(5)["xpPct"], 0)
        self.assertEqual(self.view(6)["xpPct"], 100)  # 199/200 = 99.5 -> 100 by rounding
        self.assertEqual(self.view(7)["xpPct"], 100)

    def test_thousands_get_separators(self) -> None:
        self.assertEqual(self.view(8)["totalText"], "1,234,567 XP in all")

    def test_a_summary_that_has_not_arrived_yet_still_draws(self) -> None:
        v = results()["hud_null"]
        self.assertEqual((v["streak"], v["levelText"], v["questText"], v["xpPct"], v["chest"]),
                         ("0", "Lv 1 Beginner", "0/3", 0, "locked"))
        self.assertEqual(v["bars"], [])

    def test_the_words_never_talk_about_losing_anything(self) -> None:
        banned = ("lose", "lost", "break", "broken", "risk", "danger", "expire", "hurry", "last chance", "don't")
        for v in results()["hud"] + [results()["hud_null"]]:
            for field in ("streakNote", "freezeNote", "chestNote", "bestText", "levelText", "questText", "xpText"):
                text = v[field].lower()
                for word in banned:
                    self.assertNotIn(word, text, f"{field}: {v[field]!r}")
        # A missed day is named once, in the comfort: a freeze covers one.
        notes = [v["freezeNote"] for v in results()["hud"] if v["freezes"]]
        self.assertTrue(notes and all("covers one missed day" in n for n in notes))


class TheBars(unittest.TestCase):
    def test_bars_are_scaled_to_the_busiest_day_with_a_sliver_for_any_xp(self) -> None:
        bars = results()["bars"]
        xps = [0, 50, 100, 1, 0, 25, 99, 0, 0, 0, 10, 0, 100, 37]
        self.assertEqual([b["xp"] for b in bars], xps)
        pcts = [b["pct"] for b in bars]
        self.assertEqual([p == 0 for p in pcts], [x == 0 for x in xps])
        self.assertEqual(pcts[2], 100)
        self.assertEqual(pcts[1], 50)
        self.assertEqual(pcts[6], 99)
        self.assertGreaterEqual(pcts[3], 8, "one XP is still visible")
        self.assertEqual(pcts[12], 100)
        self.assertTrue(all(0 <= p <= 100 for p in pcts))

    def test_only_the_last_bar_is_today(self) -> None:
        self.assertEqual([b["today"] for b in results()["bars"]], [False] * 13 + [True])

    def test_labels_name_the_weekday_from_the_date_itself(self) -> None:
        for b in results()["bars"]:
            day = date.fromisoformat(b["day"])
            self.assertEqual(b["label"], f"{day.strftime('%a')}: {b['xp']} XP")

    def test_weekday_agrees_with_the_calendar(self) -> None:
        for text, got in zip(results()["_days"], results()["weekday"]):
            self.assertEqual(got, date.fromisoformat(text).strftime("%a"), text)

    def test_all_zero_days_draw_flat(self) -> None:
        zero = [b["pct"] for b in results()["hud"][1]["bars"]]
        self.assertEqual(zero, [0] * 14)


class Multipliers(unittest.TestCase):
    def test_one_decimal_always(self) -> None:
        self.assertEqual(results()["mult"], ["x1.4", "x2.0", "x1.1", "x1.3", "x1.0", "x2.0"])


if __name__ == "__main__":
    unittest.main()
