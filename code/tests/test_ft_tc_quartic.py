"""Validation of the zero-field thermal quartic coefficients (ft_tc_quartic).

Checks: J=0 independent-spin closed forms (N>=3 chains and infinite chain),
an exact N=2 Z4 anchor, consistency of a2 with the exact normal-branch
curvature module, finite-N -> infinite-chain convergence, T->0 limits against
the Koziol/Langheld Landau coefficients, I(a,c) kernel quadrature and branch
consistency, and an end-to-end dense-ED check of f_N(T,h) against the Taylor
series.
"""

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_ed import free_energy  # noqa: E402
from ft_tc_normal_curvature import normal_curvature  # noqa: E402
from ft_tc_quartic import (B1, I0c, Iaa, Ipair, f1, finite_chain,  # noqa: E402
                           infinite_chain)


class TestSingleSpinJ0(unittest.TestCase):
    """J=0: independent spins; closed forms a2=-t/(4D), a4=-b(1-t^2-t/c)/(32D^2)."""

    def test_closed_forms(self):
        T, Delta, J = 1.0, 2.0, 0.0
        beta = 1.0 / T
        c = beta * Delta / 2.0
        t = math.tanh(c)
        a2_ref = -t / (4.0 * Delta)
        a4_ref = -beta * (1.0 - t * t - t / c) / (32.0 * Delta ** 2)
        inf = infinite_chain(T, J, Delta)
        self.assertAlmostEqual(inf["a2"], a2_ref, places=14)
        self.assertAlmostEqual(inf["a4"], a4_ref, places=14)
        for N in (4, 6, 8):
            fin = finite_chain(T, J, Delta, N)
            self.assertAlmostEqual(fin["a2"], a2_ref, places=13)
            self.assertAlmostEqual(fin["a4"], a4_ref, places=13)


class TestN2ExactAnchor(unittest.TestCase):
    """N=2 independent spins: Z4/Z0 = (2B + A^2)/D^4 with A=tc/2, B=c^2/8-tc/8."""

    def test_n2_anchor(self):
        # Exact N=2 independent-spin series: Z/Z0 = 1 + 2A u + (2B + A^2) u^2,
        # A = t c/2, B = c^2/8 - t c/8, u = h^2/D^2.  The quartic module kernels
        # (sum_i I + sum_{i<j} B1 B1) must reproduce this exactly.
        T, Delta, J = 1.0, 2.0, 0.0
        beta = 1.0 / T
        c = beta * Delta / 2.0
        t = math.tanh(c)
        A = t * c / 2.0
        B = c * c / 8.0 - t * c / 8.0
        z2z0_ref = 2.0 * A / Delta ** 2
        z4z0_ref = (2.0 * B + A * A) / Delta ** 4
        ps = np.array([math.exp(-beta * Delta / 2.0), math.exp(beta * Delta / 2.0)])
        ps = ps / ps.sum()
        dE = np.array([-Delta, Delta])  # dE = -Delta s
        b1avg = float(ps @ np.array([B1(beta, x) for x in dE]))
        idg = float(ps @ np.array([Ipair(beta, x, x) for x in dE]))
        z2 = 2.0 * b1avg / 4.0
        z4 = (2.0 * idg + b1avg * b1avg) / 16.0
        self.assertAlmostEqual(z2, z2z0_ref, places=14)
        self.assertAlmostEqual(z4, z4z0_ref, places=14)


class TestA2CurvatureConsistency(unittest.TestCase):
    """a2 = -chi_x/2 with chi_x = Q/4 from the independent curvature module."""

    def test_consistency(self):
        for T, J, Delta in ((0.1, -0.2, 0.2), (0.3, -0.2, 0.2),
                            (0.5, -0.3, 0.6), (0.2, 0.2, 0.3)):
            inf = infinite_chain(T, J, Delta)
            chi = normal_curvature(T, J, Delta, 1.0, 0.5)["chi_x"]
            self.assertAlmostEqual(inf["a2"], -chi / 2.0, places=12)


class TestFiniteInfiniteConvergence(unittest.TestCase):
    """Periodic-chain enumeration must approach the infinite-chain values."""

    def test_convergence(self):
        for T in (0.1, 0.3):
            inf = infinite_chain(T, -0.2, 0.2)
            prev = {}
            for N in (8, 10, 12, 14):
                fin = finite_chain(T, -0.2, 0.2, N)
                for key in ("a2", "a4"):
                    diff = abs(fin[key] - inf[key])
                    if key in prev:
                        self.assertLess(diff, prev[key])
                    prev[key] = diff
            # the finite chain must actually approach the infinite-chain value
            self.assertLess(prev["a4"], 1e-5 * max(1.0, abs(inf["a4"])))


class TestZeroTLimits(unittest.TestCase):
    """Zero-T Landau anchors, checked independently via the dense-ED ground energy.

    The direct thermal-quartic formula is not evaluated below T~0.1: the
    activated configurations contribute O(1) kernels weighted by e^{-b dE},
    and the resulting e^{+/-b}-scale cancellations exceed double precision
    at very low T (at T=0.01 the intermediate scales reach e^{+-100}).
    The zero-T reference itself is verified here against the exact N-spin
    ground energy of the transverse-field chain.
    """

    def test_zero_t_reference_via_ground_energy(self):
        J, Delta = -0.2, 0.2
        A = Delta / 2.0 - 2.0 * J
        B = Delta / 2.0 - J
        a2_ref = -1.0 / (8.0 * A)                      # -0.25
        a4_ref = (Delta / 2.0 + J) / (128.0 * A ** 3 * B)  # -1/48
        N = 10
        states = np.arange(1 << N, dtype=np.int64)
        bits = (states[:, None] >> np.arange(N)) & 1
        z = 1 - 2 * bits

        def ground(h):
            H = np.diag((J * (z * np.roll(z, -1, axis=1)).sum(axis=1)
                         + Delta / 2.0 * z.sum(axis=1)).astype(float))
            for site in range(N):
                H[states, states ^ (1 << site)] = h / 2.0
            return float(np.linalg.eigvalsh(H)[0]) / N

        e0 = ground(0.0)
        hs = [0.004, 0.008, 0.016]
        es = [ground(h) for h in hs]
        A_mat = np.array([[h ** 2, h ** 4, h ** 6] for h in hs])
        coef = np.linalg.solve(A_mat, [e - e0 for e in es])
        self.assertAlmostEqual(coef[0], a2_ref, places=4)
        self.assertAlmostEqual(coef[1], a4_ref, places=4)


class TestKernels(unittest.TestCase):
    """Quadrature anchors and branch consistency of the I(a,c) kernel."""

    def _quad(self, beta, a, c, n=36):
        gx, gw = np.polynomial.legendre.leggauss(n)
        total = 0.0
        for i, xi in enumerate(gx):
            w = (beta / 2) * (xi + 1)
            wj = (beta / 2) * gw[i]
            L = beta - w
            for j, yj in enumerate(gx):
                u = (L / 2) * (1 + yj)
                uj = (L / 2) * gw[j]
                vmax = L - u
                for k, yk in enumerate(gx):
                    v = (vmax / 2) * (1 + yk)
                    vj = (vmax / 2) * gw[k]
                    total += wj * uj * vj * (L - u - v) * math.exp(-a * u - c * v)
        return total

    def test_quadrature(self):
        for beta in (1.0, 2.5):
            for (a, c) in ((1.0, 2.0), (0.5, 2.0), (-2.0, -2.0), (2.0, -2.0),
                           (0.5, -0.3), (-0.6, 1.0)):
                self.assertAlmostEqual(Ipair(beta, a, c), self._quad(beta, a, c),
                                       places=10)

    def test_anchor_values(self):
        beta = 1.0
        # int_0^1 (1-t) e^{-t} dt = e^{-1}
        self.assertAlmostEqual(B1(beta, 1.0), math.exp(-1.0), places=14)
        # f1(1) = 1 - e^{-1}
        self.assertAlmostEqual(f1(beta, 1.0), 1.0 - math.exp(-1.0), places=14)
        # I(0,0) = beta^4/24
        self.assertAlmostEqual(Ipair(beta, 0.0, 0.0), beta ** 4 / 24.0, places=14)

    def test_symmetry(self):
        beta = 2.5
        rng = np.random.default_rng(7)
        for _ in range(30):
            a = float(rng.uniform(-2.0, 2.0))
            c = float(rng.uniform(-2.0, 2.0))
            self.assertAlmostEqual(Ipair(beta, a, c), Ipair(beta, c, a), places=10)

    def test_degenerate_branches(self):
        beta = 1.7
        for a in (0.3, -0.8, 1.2):
            # Iaa branch vs the same branch at c = a*(1+1e-6): must stay smooth
            # (the midpoint shift gives a first-order deviation ~ dI/da * 1e-6 a)
            self.assertAlmostEqual(Ipair(beta, a, a), Ipair(beta, a, a * (1 + 1e-6)),
                                   places=5)
            self.assertAlmostEqual(Iaa(beta, 1e-9),
                                   beta ** 4 / 24.0 - beta ** 5 * 1e-9 / 60.0,
                                   places=13)
        for c in (0.5, -1.1):
            self.assertAlmostEqual(Ipair(beta, 0.0, c), Ipair(beta, 1e-7, c), places=6)
        self.assertAlmostEqual(I0c(beta, 1e-10),
                               beta ** 4 / 24.0 - beta ** 5 * 1e-10 / 40.0,
                               places=13)


class TestEndToEndDenseED(unittest.TestCase):
    """f_N(T,h) from dense ED must match f0 + a2 h^2 + a4 h^4 at small h."""

    def test_taylor_series(self):
        T, J, Delta, N = 0.3, -0.2, 0.2, 8
        fin = finite_chain(T, J, Delta, N)
        f0 = free_energy(T, J, Delta, 0.0, N)
        for h in (0.002, 0.004):
            f = free_energy(T, J, Delta, h, N)
            self.assertAlmostEqual(f, f0 + fin["a2"] * h * h + fin["a4"] * h ** 4,
                                   places=9)


if __name__ == "__main__":
    unittest.main()
