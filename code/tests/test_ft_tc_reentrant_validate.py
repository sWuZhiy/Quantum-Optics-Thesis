"""Fast logic checks for the re-entrant-pocket validation driver."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_reentrant_validate import (choose_outside_probes,
                                      classify_resolution)  # noqa: E402


class ReentrantValidationTests(unittest.TestCase):
    def test_probe_selection_respects_roots_and_floor(self):
        below, above = choose_outside_probes(
            0.102548561, 0.138233309, 0.1, 0.18)
        self.assertEqual(below, 0.1)
        self.assertLess(below, 0.102548561)
        self.assertGreater(above, 0.138233309)

    def test_resolution_classification(self):
        status, ratio = classify_resolution(2e-6, 1e-7)
        self.assertEqual(status, "resolved_by_reported_method_spread")
        self.assertAlmostEqual(ratio, 20.0)
        status, ratio = classify_resolution(2e-9, 2e-7)
        self.assertEqual(status, "below_reported_method_spread")
        self.assertAlmostEqual(ratio, 0.01)
        status, ratio = classify_resolution(1e-9, 0.0)
        self.assertEqual(status, "resolved_by_reported_method_spread")
        self.assertTrue(math.isinf(ratio))


if __name__ == "__main__":
    unittest.main()
