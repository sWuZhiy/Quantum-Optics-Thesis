"""Anchors for the global g_equal stationary-point search (J=-0.2, Delta=0.2).

At T=0.25<T* the bounded h-domain scan must find one interior minimum below
g_local (first-order side); at T=0.265>T* the sampled g_equal values must all
lie at or above g_local with the minimum at the scan's left edge (continuous
side).  Small ED sizes keep the test fast; the finite-size offsets of N=8 set
the tolerances.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_global_stationary import analyze  # noqa: E402

SCAN = {"N": 8, "h_min": 0.005, "points": 60}
REFINE = {"N": 8, "tol": 1e-3}


class TestBelowTstar(unittest.TestCase):
    def test_interior_minimum(self):
        result = analyze(0.25, -0.2, 0.2, 1.0, SCAN, REFINE, None)
        self.assertTrue(result["minima"])
        best = result["minima"][0]
        self.assertLess(best["g_equal"], result["g_local"])
        self.assertGreater(result["depth_below_g_local"], 0.0)
        self.assertGreater(best["h_star"], 0.02)
        self.assertLess(best["h_star"], 0.8)


class TestAboveTstar(unittest.TestCase):
    def test_no_minimum_below(self):
        result = analyze(0.265, -0.2, 0.2, 1.0, SCAN, REFINE, None)
        # every sampled value must lie above g_local (up to the N=8
        # finite-size offset ~1e-5) with the minimum at the left edge
        self.assertGreaterEqual(result["scan_g_min"],
                                result["g_local"] - 5e-5)
        self.assertLess(result["scan_g_min_h"], 0.02)
        self.assertIsNone(result["depth_below_g_local"])


if __name__ == "__main__":
    unittest.main()
