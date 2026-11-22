"""Independent limits and finite-matrix checks for the zero-T Lanczos solver."""

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_ground_state import ground_state_energy
from ft_tc_zero_t import zero_field_tfim_energy


def dense_ground_energy(J, Delta, h, N, boundary):
    """Direct Pauli-basis construction, independent of the solver matvec."""
    dimension = 1 << N
    H = np.zeros((dimension, dimension), dtype=float)
    for state in range(dimension):
        spin = [1 - 2 * ((state >> site) & 1) for site in range(N)]
        bonds = range(N) if boundary == "periodic" else range(N - 1)
        H[state, state] = J * sum(spin[i] * spin[(i + 1) % N] for i in bonds)
        H[state, state] += Delta / 2 * sum(spin)
        for site in range(N):
            H[state, state ^ (1 << site)] = h / 2
    return float(np.linalg.eigvalsh(H)[0])


def dense_staggered_m2(J, Delta, h, N):
    """Independent dense eigenvector and direct z-basis observable."""
    dimension = 1 << N
    H = np.zeros((dimension, dimension), dtype=float)
    m2 = np.empty(dimension, dtype=float)
    for state in range(dimension):
        spin = [1 - 2 * ((state >> site) & 1) for site in range(N)]
        H[state, state] = (J * sum(spin[i] * spin[(i + 1) % N] for i in range(N))
                           + Delta / 2 * sum(spin))
        m2[state] = (sum((-1) ** i * spin[i] for i in range(N)) / N) ** 2
        for site in range(N):
            H[state, state ^ (1 << site)] = h / 2
    eigenvalues, eigenvectors = np.linalg.eigh(H)
    return float(eigenvalues[0]), float(np.dot(eigenvectors[:, 0] ** 2, m2))


class GroundStateTests(unittest.TestCase):
    def test_independent_spins_and_field_sign(self):
        Delta, h = 0.6, 0.45
        exact = -math.hypot(Delta, h) / 2
        for n in (4, 8, 16):
            for field in (h, -h):
                result = ground_state_energy(0, Delta, field, n)
                self.assertTrue(result["converged"])
                self.assertAlmostEqual(result["energy_per_site"], exact, places=10)

    def test_classical_even_antiferromagnet_boundary_count(self):
        J, n = 0.3, 6
        self.assertAlmostEqual(ground_state_energy(J, 0, 0, n, "periodic")
                               ["energy_total"], -n * J)
        self.assertAlmostEqual(ground_state_energy(J, 0, 0, n, "open")
                               ["energy_total"], -(n - 1) * J)

    def test_mixed_field_against_dense_diagonalization(self):
        cases = [(-0.3, 0.3, 0.7, 8, "periodic"),
                 (0.3, 0.6, 0.45, 8, "open")]
        for J, Delta, h, n, boundary in cases:
            result = ground_state_energy(J, Delta, h, n, boundary)
            self.assertTrue(result["converged"])
            self.assertLess(result["residual"], 1e-9)
            self.assertAlmostEqual(result["energy_total"],
                                   dense_ground_energy(J, Delta, h, n, boundary),
                                   places=10)

    def test_tfim_finite_size_approaches_infinite_solution(self):
        J, h = -0.2, 0.5809964741595971
        exact = zero_field_tfim_energy(J, h, 32768)
        errors = [abs(ground_state_energy(J, 0, h, n)["energy_per_site"] - exact)
                  for n in (8, 12, 16)]
        self.assertTrue(errors[2] < errors[1] < errors[0])
        self.assertLess(errors[2], 1e-5)

    def test_failed_convergence_is_reported(self):
        result = ground_state_energy(-0.2, 0.2, 0.5, 8, maxiter=2, tol=1e-14)
        self.assertFalse(result["converged"])
        self.assertGreater(result["residual"], 1e-14)
        requested = ground_state_energy(-0.2, 0.2, 0.5, 8, maxiter=2,
                                        tol=1e-14, measure_staggered=True)
        self.assertIsNone(requested["staggered_m2"])

    def test_afm_staggered_m2_against_dense_eigenvector(self):
        J, Delta, h, n = 0.3, 0.1, 0.45, 8
        result = ground_state_energy(J, Delta, h, n, measure_staggered=True)
        exact_energy, exact_m2 = dense_staggered_m2(J, Delta, h, n)
        self.assertTrue(result["converged"])
        self.assertAlmostEqual(result["energy_total"], exact_energy, places=10)
        self.assertAlmostEqual(result["staggered_m2"], exact_m2, places=9)
        self.assertTrue(0 <= result["staggered_m2"] <= 1)
        self.assertNotIn("staggered_m2", ground_state_energy(J, Delta, h, n))

    def test_classical_afm_staggered_m2_and_domain(self):
        result = ground_state_energy(0.3, 0, 0, 6, measure_staggered=True)
        self.assertEqual(result["staggered_m2"], 1.0)
        with self.assertRaises(ValueError):
            ground_state_energy(0.3, 0, 0.4, 5, measure_staggered=True)
        with self.assertRaises(ValueError):
            ground_state_energy(0.3, 0, 0.4, 6, "open", measure_staggered=True)


if __name__ == "__main__":
    unittest.main()
