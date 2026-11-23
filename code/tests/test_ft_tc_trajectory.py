"""Anchors for the thermal-tricritical trajectory module (J=-0.2)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_trajectory import (analyze_slice, bisect_a4_root,
                              locate_tangent_endpoint)  # noqa: E402


class TestBisection(unittest.TestCase):
    def test_known_root(self):
        root = bisect_a4_root(-0.2, 0.2, 0.25, 0.27)
        self.assertIsNotNone(root)
        self.assertAlmostEqual(root, 0.257263616274686, places=8)

    def test_no_root_deep_continuous_side(self):
        self.assertIsNone(bisect_a4_root(-0.2, 0.5, 0.005, 0.1))

    def test_sliver_crossing_near_zero_t_ratio(self):
        # Delta=0.4 (the zero-T tricritical ratio): a4 dips slightly negative
        # at small T and turns positive around T~0.11
        root = bisect_a4_root(-0.2, 0.4, 0.08, 0.2)
        self.assertIsNotNone(root)
        self.assertGreater(root, 0.08)
        self.assertLess(root, 0.2)

    def test_two_roots_just_above_zero_t_ratio(self):
        row = analyze_slice(-0.2, 0.4001, 1.0, (0.08, 0.18), 121,
                            a6_N=0, crosscheck=False)
        roots = row["roots"]
        self.assertEqual(len(roots), 2)
        self.assertAlmostEqual(roots[0]["T_star"], 0.10254856, places=5)
        self.assertAlmostEqual(roots[1]["T_star"], 0.13823331, places=5)
        self.assertEqual(roots[0]["branch"],
                         "continuous_to_first_order_on_heating")
        self.assertEqual(roots[1]["branch"],
                         "first_order_to_continuous_on_heating")

    def test_tangent_endpoint(self):
        endpoint = locate_tangent_endpoint(
            -0.2, 0.4, 0.4025, 0.09, 0.17,
            delta_tol=2e-6, temperature_tol=1e-8)
        self.assertAlmostEqual(endpoint["Delta_endpoint"], 0.4002585, places=4)
        self.assertAlmostEqual(endpoint["T_endpoint"], 0.1255994, places=3)


if __name__ == "__main__":
    unittest.main()
