"""Anchors for the zero-T first-order line driver (J=-0.2).

At Delta=0.2 the finite-chain minimum of g_equal(h) must reproduce the known
g_c~0.49556 (Langheld QMC 0.4955766); at the zero-T tricritical ratio
Delta=0.4 the minimum must approach the Koziol anchor sqrt(0.3)=0.5477226
with a small h_c (the first-order minimum retreats to h->0).  Small sizes and
few iterations keep the test fast.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_zero_t_line import g_equal, locate_minimum  # noqa: E402


class TestFirstOrderLine(unittest.TestCase):
    def test_delta_02_anchor(self):
        h_star, g_star, _ = locate_minimum(-0.2, 0.2, 12, 0.3, 0.95,
                                           1e-10, 100, coarse=9, golden=20)
        self.assertAlmostEqual(g_star, 0.49556, places=3)
        self.assertGreater(h_star, 0.4)
        self.assertLess(h_star, 0.8)

    def test_delta_04_anchor(self):
        h_star, g_star, _ = locate_minimum(-0.2, 0.4, 12, 0.01, 0.3,
                                           1e-10, 100, coarse=9, golden=20)
        self.assertAlmostEqual(g_star, math.sqrt(0.3), places=3)
        self.assertLess(h_star, 0.12)

    def test_omega_rescales_equal_energy_coupling(self):
        g_one, _ = g_equal(-0.2, 0.2, 8, 0.5, 1e-10, 100, omega=1.0)
        g_four, _ = g_equal(-0.2, 0.2, 8, 0.5, 1e-10, 100, omega=4.0)
        self.assertAlmostEqual(g_four, 2.0 * g_one, places=10)


if __name__ == "__main__":
    unittest.main()
