"""Independent small-matrix checks for the thermal matter transfer code."""

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_transfer import classical_chain, free_energy, independent_spin


class TransferTests(unittest.TestCase):
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
