"""Independent published and analytic checks for the zero-T FM baseline."""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ft_tc_zero_t import ferromagnetic_landau, zero_field_crossing, zero_field_tfim_energy


class ZeroTemperatureBaselineTests(unittest.TestCase):
    def test_published_exact_zero_field_crossing_and_quadrature(self):
        # Koziol (2026), Sec. VI, Fig. 3: J_K/omega=.2, epsilon=0.
        values = [zero_field_crossing(-0.2, 1.0, momenta=n)
                  for n in (8192, 32768)]
        for result in values:
            self.assertAlmostEqual(result["g_crossing"], 0.4090436682, delta=3e-10)
            self.assertAlmostEqual(result["energy_residual"], 0.0, delta=2e-14)
            self.assertAlmostEqual(result["stationarity_residual"], 0.0, delta=2e-8)
            self.assertLess(result["g_crossing"], result["g_normal_local"])
        self.assertLess(abs(values[0]["g_crossing"] - values[1]["g_crossing"]), 1e-10)

    def test_tfim_energy_extreme_field_and_evenness(self):
        self.assertEqual(zero_field_tfim_energy(-0.2, 0.0), -0.2)
        self.assertAlmostEqual(zero_field_tfim_energy(-0.2, 1.0),
                               zero_field_tfim_energy(-0.2, -1.0), places=13)
        # First terms of the exact large-field expansion: -h/2 - J^2/(2h).
        self.assertAlmostEqual(zero_field_tfim_energy(-0.2, 100.0),
                               -50.0002, delta=2e-8)

    def test_tricritical_ratio_and_continuous_line(self):
        below, at, above = [ferromagnetic_landau(-0.2, d, 1.0)
                            for d in (0.2, 0.4, 0.6)]
        self.assertLess(below["c4_prefactor_of_g4"], 0)
        self.assertEqual(at["c4_prefactor_of_g4"], 0)
        self.assertGreater(above["c4_prefactor_of_g4"], 0)
        self.assertAlmostEqual(at["g_local"], math.sqrt(0.3), places=13)
        self.assertAlmostEqual(above["g_local"], math.sqrt(0.35), places=13)
        self.assertAlmostEqual(at["tricritical_Delta"], 0.4, places=13)
        self.assertAlmostEqual(at["tricritical_c6"], 35 / 36, places=13)


if __name__ == "__main__":
    unittest.main()
