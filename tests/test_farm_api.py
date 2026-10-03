"""Farm: the routes the screen calls, with what each answer must carry."""

from __future__ import annotations

import unittest

from code_coach.api.schemas import FarmCodeRequest, FarmUnlockRequest, FarmWarpRequest
from code_coach.api.server import (
    farm_code,
    farm_overview,
    farm_reset,
    farm_state,
    farm_unlock,
    farm_warp,
)
from code_coach.farm.runner import HOST, STARTER_CODE


class FarmRouteTests(unittest.TestCase):
    def test_the_screen_gets_everything_it_draws(self) -> None:
        o = farm_overview()
        for key in ("farm", "items", "unlocks", "functions", "code", "languages", "warps", "names", "features"):
            self.assertIn(key, o)
        self.assertEqual((o["farm"]["w"], o["farm"]["h"]), (1, 1))
        self.assertIn("python", o["languages"])
        self.assertEqual(o["code"]["python"], STARTER_CODE["python"])
        loops = next(u for u in o["unlocks"] if u["name"] == "Loops")
        self.assertEqual(loops["cost"], {"Hay": 5})
        self.assertTrue(loops["available"])
        self.assertFalse(loops["affordable"])

    def test_buying_needs_the_items(self) -> None:
        self.assertFalse(farm_unlock(FarmUnlockRequest(name="Loops"))["ok"])
        HOST._load().items["Hay"] = 5
        got = farm_unlock(FarmUnlockRequest(name="Loops"))
        self.assertTrue(got["ok"])
        self.assertIn("while", got["features"])

    def test_code_is_kept_per_language(self) -> None:
        farm_code(FarmCodeRequest(language="javascript", code="harvest();\n"))
        o = farm_overview()
        self.assertEqual(o["code"]["javascript"], "harvest();\n")
        self.assertEqual(o["language"], "javascript")

    def test_state_returns_output_from_a_line_on(self) -> None:
        HOST._load()  # this test's own save: loading it starts the output afresh
        HOST.output = [{"kind": "info", "text": "a"}, {"kind": "out", "text": "b"}]
        got = farm_state(since=1)
        self.assertEqual([line["text"] for line in got["output"]], ["b"])
        self.assertEqual(got["outputEnd"], 2)

    def test_warp_only_takes_offered_values(self) -> None:
        farm_warp(FarmWarpRequest(warp=8))
        self.assertEqual(HOST.warp, 8)
        farm_warp(FarmWarpRequest(warp=7))
        self.assertEqual(HOST.warp, 1)

    def test_reset_starts_over(self) -> None:
        HOST._load().items["Hay"] = 50
        o = farm_reset()
        self.assertEqual(o["items"]["Hay"], 0)


if __name__ == "__main__":
    unittest.main()
