"""Every Momentum quest says where to do it, and that place is a real tab.

The popover turns each quest into a link, so a quest whose `go` names a mode
that does not exist (a typo, or a tab renamed later) would be a dead link on a
screen people use daily.
"""

import re
import unittest
from datetime import date
from pathlib import Path

from code_coach.momentum import rules

MODE_BAR = Path(__file__).resolve().parent.parent / "web" / "src" / "components" / "ModeBar.tsx"


def mode_ids() -> set[str]:
    """The tab ids the top bar defines, read from its source (the one list)."""
    text = MODE_BAR.read_text(encoding="utf-8")
    block = text.split("export const MODES = [", 1)[1].split("] as const", 1)[0]
    return set(re.findall(r'^\s+id:\s*"([a-z]+)"', block, flags=re.M))


class QuestLinks(unittest.TestCase):
    def test_the_mode_list_was_read(self):
        ids = mode_ids()
        # A sample of tabs that must exist for the links below to mean anything.
        self.assertTrue({"session", "brain", "farm", "workbook"} <= ids, ids)

    def test_every_quest_has_a_go_and_it_is_a_real_tab(self):
        ids = mode_ids()
        for quest in rules.POOL:
            go = rules.QUEST_GO.get(quest.id)
            self.assertIsNotNone(go, f"quest {quest.id} has no place to go")
            self.assertIn(go, ids, f"quest {quest.id} goes to a tab that does not exist: {go}")

    def test_no_link_for_a_quest_that_is_not_in_the_pool(self):
        self.assertLessEqual(set(rules.QUEST_GO), {q.id for q in rules.POOL})

    def test_quest_progress_carries_the_go(self):
        ids = rules.pick_quests(date(2026, 10, 19))
        shown = rules.quest_progress(ids, rules.DayStats())
        self.assertEqual(len(shown), len(ids))
        for item in shown:
            self.assertEqual(item["go"], rules.QUEST_GO[item["id"]])

    def test_a_farm_quest_goes_to_the_farm_and_the_brain_one_to_brain_drills(self):
        # Behaviour a person would notice, spelled out rather than derived.
        self.assertEqual(rules.QUEST_GO["farm_items"], "farm")
        self.assertEqual(rules.QUEST_GO["brain"], "brain")


if __name__ == "__main__":
    unittest.main()
