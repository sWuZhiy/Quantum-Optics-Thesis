"""Physical limiting checks for bracketed thermal equal-coupling refinement."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ft_tc_thermal_refine import golden_refine, make_evaluator


class ThermalRefineTests(unittest.TestCase):
    def test_independent_spin_continuous_onset_is_left_edge(self):
        T, omega = 0.5, 1.0
        _, evaluate = make_evaluator(T, 0.0, 0.0, omega, "ed", N=4)
        result = golden_refine(evaluate, 0.05, 0.4, 0.005)
        self.assertTrue(result["at_original_edge"])
        self.assertAlmostEqual(result["best_evaluated"]["h"], 0.05)
        # Delta=J=0 gives g_local=sqrt(omega*T/2); any finite h has g_equal above it.
        self.assertGreater(result["best_evaluated"]["g_equal"], math.sqrt(omega * T / 2))

    def test_nlce_and_ed_independent_spin_agree_at_fixed_h(self):
        ed_normal, ed = make_evaluator(0.4, 0.0, 0.3, 1.0, "ed", N=4)
        nlce_normal, nlce = make_evaluator(0.4, 0.0, 0.3, 1.0, "nlce", orders=[3, 4, 5])
        self.assertAlmostEqual(ed_normal, nlce_normal, places=12)
        self.assertAlmostEqual(ed(0.5)["g_equal"], nlce(0.5)["g_equal"], places=12)


if __name__ == "__main__":
    unittest.main()
