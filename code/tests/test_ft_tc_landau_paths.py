"""Independent checks for the exact finite-chain Dyson-path expansion."""

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_landau_paths import (confluent_simplex, landau_coefficients,
                                returning_sequences)  # noqa: E402
from ft_tc_quartic import B1, finite_chain, infinite_chain  # noqa: E402
from ft_tc_tricritical_validate import fourth_order_root  # noqa: E402


class SimplexTests(unittest.TestCase):
    def test_repeated_zero_volume_and_pair_kernel(self):
        beta = 1.7
        for order in (2, 4, 6):
            self.assertAlmostEqual(
                confluent_simplex(beta, (0.0,) * (order + 1)),
                beta ** order / math.factorial(order), places=13)
        for x in (-1.2, -0.2, 0.0, 0.7, 1.5):
            self.assertAlmostEqual(
                confluent_simplex(beta, (0.0, x, 0.0)),
                B1(beta, x), places=13)

    def test_sequence_counts(self):
        N = 7
        expected = {
            2: N,
            4: N + 6 * math.comb(N, 2),
            6: N + 15 * N * (N - 1) + 90 * math.comb(N, 3),
        }
        for order, count in expected.items():
            self.assertEqual(sum(1 for _ in returning_sequences(N, order)), count)


class CoefficientTests(unittest.TestCase):
    def test_independent_spin_closed_forms(self):
        T, Delta, J = 1.0, 2.0, 0.0
        beta = 1.0 / T
        c = beta * Delta / 2.0
        t = math.tanh(c)
        a2 = -t / (4.0 * Delta)
        a4 = -beta * (1.0 - t * t - t / c) / (32.0 * Delta ** 2)
        A = t * c / 2.0
        B = c * c / 8.0 - t * c / 8.0
        C = t * c / 16.0 - c * c / 16.0 + t * c ** 3 / 48.0
        a6 = -T * (C - A * B + A ** 3 / 3.0) / Delta ** 6
        for N in (3, 4, 6):
            result = landau_coefficients(T, J, Delta, N, 6)
            self.assertAlmostEqual(result["a2"], a2, places=13)
            self.assertAlmostEqual(result["a4"], a4, places=13)
            self.assertAlmostEqual(result["a6"], a6, places=13)

    def test_interacting_dense_partition_series(self):
        T, J, Delta, N = 1.0, -0.2, 0.2, 4
        result = landau_coefficients(T, J, Delta, N, 6)
        states = np.arange(1 << N, dtype=np.int64)
        bits = (states[:, None] >> np.arange(N)) & 1
        z = 1 - 2 * bits
        diagonal = (J * (z * np.roll(z, -1, axis=1)).sum(axis=1)
                    + Delta / 2 * z.sum(axis=1))

        def partition(h):
            matrix = np.diag(diagonal.astype(float))
            for site in range(N):
                matrix[states, states ^ (1 << site)] = h / 2
            return float(np.exp(-np.linalg.eigvalsh(matrix) / T).sum())

        z0 = partition(0.0)
        for h in (0.04, 0.08, 0.12):
            exact = partition(h) / z0
            fourth = (1.0 + result["Z2Z0"] * h ** 2
                      + result["Z4Z0"] * h ** 4)
            sixth = fourth + result["Z6Z0"] * h ** 6
            self.assertLess(abs(exact - sixth), abs(exact - fourth) / 100.0)

    def test_quartic_implementations_and_thermodynamic_convergence(self):
        T, J, Delta = 0.257263, -0.2, 0.2
        for N in (6, 8):
            path = landau_coefficients(T, J, Delta, N, 4)
            local = finite_chain(T, J, Delta, N)
            self.assertAlmostEqual(path["a2"], local["a2"], places=13)
            self.assertAlmostEqual(path["a4"], local["a4"], places=12)
        thermodynamic = infinite_chain(T, J, Delta)
        finite12 = landau_coefficients(T, J, Delta, 12, 4)
        self.assertLess(abs(finite12["a4"] - thermodynamic["a4"]), 2e-6)

    def test_sixth_order_is_positive_at_corrected_candidate(self):
        values = [landau_coefficients(0.257263, -0.2, 0.2, N, 6)["a6"]
                  for N in (6, 8)]
        self.assertGreater(min(values), 0.03)
        self.assertLess(abs(values[-1] - values[-2]), 3e-4)

    def test_corrected_infinite_a4_root(self):
        root, width, _, residual = fourth_order_root(-0.2, 0.2, 0.25, 0.27)
        self.assertAlmostEqual(root, 0.25726361627468, places=11)
        self.assertLess(width, 1.1e-13)
        self.assertLess(abs(residual), 1e-13)


if __name__ == "__main__":
    unittest.main()
