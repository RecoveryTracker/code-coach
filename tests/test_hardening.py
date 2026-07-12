"""
Tests for local-exec hardening (Phase 3):
  - Host-header guard against DNS-rebinding.
  - Runner output cap + timeout.

Memory (RLIMIT_AS) is not asserted here: it's enforced on Linux but ignored on
macOS, so a cross-platform assertion would be flaky. The timeout and output cap
are the portable guards.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import time
import unittest

from code_coach.api.server import host_allowed
from code_coach.engine import MAX_OUTPUT_CHARS, run_code


class HostGuard(unittest.TestCase):
    def test_localhost_variants_allowed(self):
        for h in ("127.0.0.1:8765", "localhost:8765", "127.0.0.1", "localhost",
                  "[::1]:8765", ""):
            self.assertTrue(host_allowed(h), h)

    def test_foreign_hosts_rejected(self):
        for h in ("evil.example.com", "attacker.test", "169.254.1.1:8765",
                  "example.com:80"):
            self.assertFalse(host_allowed(h), h)


class RunnerCaps(unittest.TestCase):
    def test_normal_program_runs(self):
        out, err, rc = run_code("print(40 + 2)")
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), "42")

    def test_infinite_loop_times_out(self):
        start = time.time()
        out, err, rc = run_code("while True:\n    pass")
        elapsed = time.time() - start
        self.assertEqual(rc, 124)
        self.assertLess(elapsed, 6.0)  # ~3s timeout + slack

    def test_output_is_capped(self):
        out, err, rc = run_code('print("x" * 500000)')
        self.assertLessEqual(len(out), MAX_OUTPUT_CHARS + 64)
        self.assertIn("truncated", out)


if __name__ == "__main__":
    unittest.main()
