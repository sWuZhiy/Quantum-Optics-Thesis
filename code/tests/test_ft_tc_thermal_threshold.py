"""Physical checks for the finite-temperature normal-branch threshold."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ft_tc_thermal_threshold import equal_coupling, scan_ed, scan_nlce
from ft_tc_transfer import independent_spin


class ThermalThresholdTests(unittest.TestCase):
    def test_independent_spin_formula_and_global_normal_condition(self):
        T, omega, h = 0.5, 1.0, 0.4
        f0 = independent_spin(T, 0.0, 0.0)
        fh = independent_spin(T, 0.0, h)
        g_equal = equal_coupling(omega, h, f0, fh)
        self.assertAlmostEqual(omega * (h / (4 * g_equal)) ** 2 + fh, f0, places=13)
        # For the free spin at Delta=0 the continuous threshold is sqrt(omega*T/2).
        self.assertGreater(g_equal, math.sqrt(omega * T / 2))

    def test_finite_ed_and_nlce_recover_independent_spins(self):
        T, Delta, h = 0.4, 0.3, 0.5
        expected = equal_coupling(1.0, h, independent_spin(T, Delta, 0),
                                  independent_spin(T, Delta, h))
        ed = scan_ed(T, 0.0, Delta, 1.0, [h], [4, 6])
        nlce = scan_nlce(T, 0.0, Delta, 1.0, [h], [3, 4, 5])
        for value in ed[0]["values"] + nlce[0]["values"]:
            self.assertAlmostEqual(value["g_equal"], expected, places=11)


if __name__ == "__main__":
    unittest.main()
