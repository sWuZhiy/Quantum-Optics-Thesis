"""Anchors for the thermal-tricritical trajectory module (J=-0.2).

The bisection of the corrected infinite-chain a4(T) must reproduce the known
T*(0.2)=0.2572636..., must find no sign change on the deep continuous side
(Delta=0.5), and must find the shallow crossing near Delta=0.4 (first-order
sliver above the zero-T tricritical ratio).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_trajectory import bisect_a4_root  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
