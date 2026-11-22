"""Exact zero-field thermal quadratic/quartic coefficients for the zz/z matter chain.

Objects (hbar=k_B=1, periodic chain):
    H_spin(h) = H0 + h*V,
    H0 = J sum sigma_z[i] sigma_z[i+1] + Delta/2 sum sigma_z[i],
    V  = (1/2) sum sigma_x[i].
At h=0 H0 is a classical Ising chain.  The Dyson expansion
    f_N(T,h) = f_0 + a2 h^2 + a4 h^4 + O(h^6)
has, per model.md:
    Z(h) = Z0 + h^2 Z2 + h^4 Z4 + O(h^6),
    a2 = -(T/N) (Z2/Z0),
    a4 = -(T/N) [Z4/Z0 - (Z2/Z0)^2/2].

A spin flip at site i costs  dE_i = -s_i [Delta + 2J (s_{i-1}+s_{i+1})], and in the
z-diagonal classical chain the imaginary-time pair propagator of site i is a
c-number:  sigma_x_i(t1) sigma_x_i(t2) = exp(-dE_i |t1-t2|).  Since operators at
different sites commute, the k=4 time-ordered amplitude factorizes per site, so
(no interleaved-sequence corrections):

    Z2/Z0 = (1/4) <sum_i B1(dE_i)>,
    Z4/Z0 = (1/16) < sum_i I(dE_i,dE_i) + sum_{i<j} B1(dE_i) B1(dE_j) >,

    B1(x) = int_0^b dt (b-t) e^{-x t} = [b x - 1 + e^{-b x}]/x^2,      b = beta = 1/T
    I(a,c) = int_{u+v+w<=b} (b-u-v-w) e^{-a u - c v} du dv dw
           = int_0^b dt4 int_0^{b-t4} dv int_0^{b-t4-v} dw int_0^{b-t4-v-w} du e^{-a u - c v},

with closed forms (R(x,y) = [f1(x)-f1(y)]/(x-y), f1(x) = (1-e^{-b x})/x):
    I(a,c)  = G(c)/a - [b - f1(c)]/(a^2 c) + [f1(c)-f1(a)]/[a^2 (a-c)],  G(x)=[x b^2/2 - b + f1(x)]/x^2
    I(a,a)  = [a b^2/2 - 2b + 2 f1(a)]/a^3 - f1'(a)/a^2
    I(0,c)  = [b - f1(c)]/c^3 - b^2/(2 c^2) + b^3/(6 c)
    I(0,0)  = b^4/24.

Both the exact finite chain (enumeration; N>=3) and the exact infinite chain
(2x2 transfer-matrix spectral decomposition; requires finite correlation
length) are provided.  The quartic coefficient of the cavity functional
Phi_T(phi) = omega phi^2 + f_spin(T,4g phi) is (4g)^4 a4; a4 > 0 at g_local
means a locally continuous transition, a4 < 0 means first order.
"""

import argparse
import hashlib
import json
import math
import time

import numpy as np

SPINS = np.array([-1.0, 1.0])
_EPS = 1e-6


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ---------------------------------------------------------------------------
# fundamental integrals with small-argument series
# ---------------------------------------------------------------------------

def f1(beta, x):
    """(1 - e^{-beta x})/x;  f1(0)=beta."""
    t = beta * x
    if abs(t) < 1e-6:
        return beta * (1 + t * (-0.5 + t * (1 / 6 + t * (-1 / 24 + t / 120))))
    return -math.expm1(-t) / x


def f1p(beta, x):
    """df1/dx;  f1'(0) = -beta^2/2."""
    t = beta * x
    if abs(t) < 1e-6:
        return -beta ** 2 / 2 + beta ** 3 * x / 3 - beta ** 4 * x * x / 8 \
            + beta ** 5 * x ** 3 / 30
    return (t * math.exp(-t) + math.expm1(-t)) / (x * x)


def B1(beta, x):
    """int_0^beta dt (beta-t) e^{-x t};  B1(0)=beta^2/2."""
    t = beta * x
    if abs(t) < 1e-6:
        return beta * beta / 2 - beta ** 3 * x / 6 + beta ** 4 * x * x / 24 \
            - beta ** 5 * x ** 3 / 120
    return (t + math.expm1(-t)) / (x * x)


def _G(beta, x):
    return (x * beta * beta / 2.0 - beta + f1(beta, x)) / (x * x)


def I0c(beta, c):
    """I(0,c)."""
    t = beta * c
    if abs(t) < 1e-6:
        return beta ** 4 / 24 - beta ** 5 * c / 40 + beta ** 6 * c * c / 180
    return (beta - f1(beta, c)) / (c ** 3) - beta * beta / (2.0 * c * c) \
        + beta ** 3 / (6.0 * c)


def Iaa(beta, a):
    """I(a,a)."""
    t = beta * a
    if abs(t) < 1e-6:
        return beta ** 4 / 24 - beta ** 5 * a / 60 + beta ** 6 * a * a / 144
    return (a * beta * beta / 2.0 - 2.0 * beta + 2.0 * f1(beta, a)) / (a ** 3) \
        - f1p(beta, a) / (a * a)


def Ipair(beta, a, c):
    if abs(a) < _EPS and abs(c) < _EPS:
        return beta ** 4 / 24.0
    if abs(a) < _EPS:
        return I0c(beta, c)
    if abs(c) < _EPS:
        return I0c(beta, a)
    if abs(a - c) < 1e-5 * max(1.0, abs(a), abs(c)):
        return Iaa(beta, 0.5 * (a + c))
    return _G(beta, c) / a - (beta - f1(beta, c)) / (a * a * c) \
        + (f1(beta, c) - f1(beta, a)) / (a * a * (a - c))


# ---------------------------------------------------------------------------
# triplet bookkeeping
# ---------------------------------------------------------------------------

def triplet_tables(J, Delta):
    """dE and spins for the 8 triplets (s_{i-1}, s_i, s_{i+1}) in +-1."""
    dE = np.empty(8)
    spins = np.empty((8, 3))
    for idx in range(8):
        a = SPINS[(idx >> 2) & 1]
        s = SPINS[(idx >> 1) & 1]
        b = SPINS[idx & 1]
        spins[idx] = (a, s, b)
        dE[idx] = -s * (Delta + 2.0 * J * (a + b))
    return dE, spins


def spin_index(spin):
    return int((spin + 1) / 2)


# ---------------------------------------------------------------------------
# finite periodic chain (exact enumeration)
# ---------------------------------------------------------------------------

def finite_chain(T, J, Delta, N):
    if T <= 0 or N < 3:
        raise ValueError("require T>0, N>=3")
    beta = 1.0 / T
    dE, _ = triplet_tables(J, Delta)
    b1vec = np.array([B1(beta, x) for x in dE])
    idg = np.array([Ipair(beta, dE[i], dE[i]) for i in range(8)])

    states = np.arange(1 << N, dtype=np.int64)
    bits = (states[:, None] >> np.arange(N)) & 1
    z = 1 - 2 * bits  # +-1, shape (2^N, N)
    zl = np.roll(z, 1, axis=1)
    zr = np.roll(z, -1, axis=1)
    idx = (4 * ((zl + 1) // 2) + 2 * ((z + 1) // 2) + ((zr + 1) // 2)).astype(int)
    counts = (idx[:, :, None] == np.arange(8)[None, None, :]).sum(axis=1)  # (2^N, 8)

    energy = J * (z * zr).sum(axis=1) + Delta / 2.0 * z.sum(axis=1)
    weights = np.exp(-beta * (energy - energy.min()))
    weights /= weights.sum()

    nb1 = counts @ b1vec
    # sum_{i<j} B1(dE_i) B1(dE_j) = [(sum B1)^2 - sum B1^2]/2
    pair = 0.5 * (nb1 * nb1 - counts @ (b1vec * b1vec))
    diag = counts @ idg

    z2z0 = 0.25 * float(weights @ nb1)
    z4z0 = (1.0 / 16.0) * float(weights @ (diag + pair))
    a2 = -(T / N) * z2z0
    a4 = -(T / N) * (z4z0 - 0.5 * z2z0 * z2z0)
    return {"N": N, "a2": a2, "a4": a4, "Z2Z0": z2z0, "Z4Z0": z4z0,
            "B1_average": float(weights @ nb1) / N}


# ---------------------------------------------------------------------------
# infinite chain via the 2x2 transfer matrix
# ---------------------------------------------------------------------------

def infinite_chain(T, J, Delta):
    if T <= 0:
        raise ValueError("require T>0")
    beta = 1.0 / T
    K = np.exp(-beta * (J * SPINS[:, None] * SPINS[None, :]
                        + Delta * (SPINS[:, None] + SPINS[None, :]) / 4.0))
    lam, vec = np.linalg.eigh(K)
    lam_max = float(lam[-1])
    lam_sub = float(lam[0])
    if lam_max - lam_sub < 1e-12 * lam_max:
        raise ValueError("subleading transfer eigenvalue degenerate with Perron root "
                         "(diverging correlation length); infinite-chain quartic unavailable")
    v = vec[:, -1] / np.linalg.norm(vec[:, -1])
    w = vec[:, 0] / np.linalg.norm(vec[:, 0])

    dE, tri = triplet_tables(J, Delta)
    b1vec = np.array([B1(beta, x) for x in dE])
    idg = np.array([Ipair(beta, dE[i], dE[i]) for i in range(8)])
    bbr1 = b1vec[:, None] * b1vec[None, :]

    # triplet marginals p_alpha (three-site probability of the infinite chain)
    p = np.empty(8)
    for idx in range(8):
        a, s, b = tri[idx]
        ia, isp, ib = spin_index(a), spin_index(s), spin_index(b)
        p[idx] = v[ia] * K[ia, isp] * K[isp, ib] * v[ib] / lam_max ** 2
    b1_avg = float(p @ b1vec)

    # r=1: joint probability of two adjacent triplets (4 spins, 3 bonds)
    r1 = np.zeros((8, 8))
    for idx in range(8):
        a0, s0, s1 = tri[idx]
        for jdx in range(8):
            a1, s1b, s2 = tri[jdx]
            if a1 != s0 or s1b != s1:
                continue
            ia0, is0, is1 = spin_index(a0), spin_index(s0), spin_index(s1)
            is2 = spin_index(s2)
            r1[idx, jdx] = v[ia0] * K[ia0, is0] * K[is0, is1] * K[is1, is2] * v[is2] \
                / lam_max ** 3

    # r>=2: geometric sum on the subleading eigenspace
    ua = np.zeros((8, 2))
    ub = np.zeros((8, 2))
    for idx in range(8):
        a, s, b = tri[idx]
        ia, isp, ib = spin_index(a), spin_index(s), spin_index(b)
        ua[idx, ib] = v[ia] * K[ia, isp] * K[isp, ib]  # one-hot in s_1 = b
        ub[idx, ia] = K[ia, isp] * K[isp, ib] * v[ib]  # one-hot in s_{r-1} = a
    geom = np.outer(ua @ w, w @ ub.T) / (lam_max ** 3 * (lam_max - lam_sub))

    # a4^N = -(T/16)<I_00> - (T/16)(1/N) sum_{i<j}<B1 B1>_c + (T/32) B1^2
    # (the N^2 background cancels: -(T/32)(N-1)B1^2 + (T/32) N B1^2); in the
    # infinite chain (1/N) sum_{i<j} -> (1/2) sum_{j!=0} = sum_{r>=1} one-sided,
    # so a4^inf = -(T/16)[<I_00> + sum_{r>=1}<B1 B1>_c] + (T/32) B1^2.
    conn = float(np.sum((r1 - np.outer(p, p)) * bbr1)) \
        + float(np.sum(geom * bbr1))

    a2 = -(T / 4.0) * b1_avg
    a4 = -(T / 16.0) * (float(p @ idg) + conn) + (T / 32.0) * b1_avg * b1_avg
    return {"a2": a2, "a4": a4, "B1_average": b1_avg,
            "lambda_max": lam_max, "lambda_sub": lam_sub,
            "triplet_marginals": p.tolist()}


def summarize(T, J, Delta, omega, fin, inf):
    a2 = inf["a2"]
    a4 = inf["a4"]
    out = {"T": T, "J": J, "Delta": Delta, "omega": omega,
           "a2_infinite": a2, "a4_infinite": a4}
    if a2 < 0:
        out["g_local"] = math.sqrt(-omega / (16.0 * a2))
        out["chi_x"] = -2.0 * a2
        out["phi_quartic_at_g_local"] = (4.0 * out["g_local"]) ** 4 * a4
    if fin is not None:
        out["finite"] = [{"N": f["N"], "a2": f["a2"], "a4": f["a4"]} for f in fin]
    A = Delta / 2.0 - 2.0 * J
    B = Delta / 2.0 - J
    out["a4_zero_T_reference"] = (Delta / 2.0 + J) / (128.0 * A ** 3 * B)
    out["a2_zero_T_reference"] = -1.0 / (8.0 * A)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, nargs="+", required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, default=1.0)
    p.add_argument("--N", type=int, nargs="*", default=[10, 12, 14])
    a = p.parse_args()
    start = time.perf_counter()
    values = []
    for T in a.T:
        fin = [finite_chain(T, a.J, a.Delta, N) for N in a.N] if a.N else None
        inf = infinite_chain(T, a.J, a.Delta)
        values.append(summarize(T, a.J, a.Delta, a.omega, fin, inf))
    print(json.dumps({"parameters": vars(a), "seed": None,
                      "elapsed_seconds": time.perf_counter() - start,
                      "sources_sha256": {"ft_tc_quartic.py": _sha256(__file__)},
                      "values": values}, indent=2))


if __name__ == "__main__":
    main()
