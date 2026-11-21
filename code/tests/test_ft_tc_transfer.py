"""Independent small-matrix checks for the thermal matter transfer code."""

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_transfer import classical_chain, free_energy, independent_spin
from ft_tc_ed import free_energy as finite_chain_free_energy
from ft_tc_normal_curvature import normal_curvature
from ft_tc_nlce import open_total_free_energy


class TransferTests(unittest.TestCase):
    def test_open_chain_nlce_analytic_limits(self):
        T, J, Delta, h, length = 0.3, -0.3, 0.6, 0.45, 5
        self.assertAlmostEqual(open_total_free_energy(T, 0, Delta, h, length)
                               - open_total_free_energy(T, 0, Delta, h, length - 1),
                               independent_spin(T, Delta, h), places=11)
        z = np.array([-1.0, 1.0])
        transfer = np.exp(-J * z[:, None] * z[None, :] / T
                          - Delta * (z[:, None] + z[None, :]) / (4 * T))
        edges = np.exp(-Delta * z / (4 * T))
        exact_logZ = math.log(float(edges @ np.linalg.matrix_power(transfer, length - 1) @ edges))
        self.assertAlmostEqual(open_total_free_energy(T, J, Delta, 0, length),
                               -T * exact_logZ, places=11)

    def test_normal_curvature_independent_spin_threshold(self):
        T, Delta = 0.5, 1.0
        result = normal_curvature(T, 0, Delta, 1, 0.5)
        expected = math.sqrt(Delta / (4 * math.tanh(Delta / (2 * T))))
        self.assertAlmostEqual(result["g_local"], expected, places=11)
        self.assertAlmostEqual(result["probability_sum"], 1.0, places=12)

    def test_normal_curvature_mixed_field_against_finite_chain(self):
        T, J, Delta, h = 0.1, -0.3, 0.3, 0.01
        result = normal_curvature(T, J, Delta, 1, 0.60693)
        ed_coefficient = (finite_chain_free_energy(T, J, Delta, h, 10)
                          - finite_chain_free_energy(T, J, Delta, 0, 10)) / h**2
        self.assertAlmostEqual(ed_coefficient, -result["chi_x"] / 2, places=5)
        zero_T_limit = math.sqrt((Delta - 4 * J) / 4)
        self.assertAlmostEqual(normal_curvature(0.02, J, Delta, 1, 0)["g_local"],
                               zero_T_limit, places=10)

    def test_finite_chain_ed_independent_spins(self):
        expected = independent_spin(0.1, 0.6, 0.45)
        for n in (4, 8):
            self.assertAlmostEqual(finite_chain_free_energy(0.1, 0, 0.6, 0.45, n),
                                   expected, places=11)

    def test_finite_chain_ed_classical_periodic_partition(self):
        T, J, Delta, n = 0.3, -0.3, 0.6, 6
        z = np.array([1.0, -1.0])
        mat = np.exp(-J * z[:, None] * z[None, :] / T
                     - Delta * (z[:, None] + z[None, :]) / (4 * T))
        expected = -T * math.log(float(np.trace(np.linalg.matrix_power(mat, n)))) / n
        self.assertAlmostEqual(finite_chain_free_energy(T, J, Delta, 0, n),
                               expected, places=11)

    def test_zero_transverse_field_is_exact_at_any_trotter_size(self):
        for J in (-0.3, 0.3):
            expected = classical_chain(0.5, J, 1.0)
            for M in (4, 8):
                self.assertAlmostEqual(free_energy(0.5, J, 1.0, 0, M)["f"], expected, places=9)

    def test_independent_spin_trotter_convergence(self):
        exact = independent_spin(0.5, 1.0, 0.8)
        errors = [abs(free_energy(0.5, 0, 1.0, 0.8, M)["f"] - exact)
                  for M in (4, 8, 12)]
        self.assertTrue(errors[2] < errors[1] < errors[0])

    def test_mixed_field_matrix_free_matches_dense_transfer(self):
        T, J, Delta, h, M = 0.5, -0.3, 1.0, 0.8, 4
        step = 1 / (T * M)
        states = np.arange(1 << M, dtype=np.uint32)
        bits = ((states[:, None] >> np.arange(M, dtype=np.uint32)) & 1)
        spins = 1 - 2 * bits.astype(float)
        flips = np.count_nonzero(bits != np.roll(bits, -1, axis=1), axis=1)
        u = step * abs(h) / 2
        logw = (-step * Delta / 2 * spins.sum(axis=1)
                + (M - flips) * math.log(math.cosh(u))
                + flips * math.log(math.sinh(u)))
        rootw = np.exp(logw / 2)
        transfer = (rootw[:, None]
                    * np.exp(-step * J * (spins @ spins.T))
                    * rootw[None, :])
        expected = -T * math.log(float(np.linalg.eigvalsh(transfer)[-1]))
        self.assertAlmostEqual(free_energy(T, J, Delta, h, M)["f"], expected, places=10)


if __name__ == "__main__":
    unittest.main()
