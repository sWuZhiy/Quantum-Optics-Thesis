"""Periodic finite-chain exact diagonalization benchmark for FT-TC matter free energy.

H = J sum sigma_z[i] sigma_z[i+1] + Delta/2 sum sigma_z[i]
    + h/2 sum sigma_x[i].  Dense diagonalization limits usable N.
"""

import argparse
import json
import math
import time

import numpy as np


def _classical_energies(J, Delta, N):
    """Diagonal energies of the periodic zero-transverse-field chain."""
    states = np.arange(1 << N, dtype=np.int64)
    bits = (states[:, None] >> np.arange(N)) & 1
    z = 1 - 2 * bits
    energies = (J * (z * np.roll(z, -1, axis=1)).sum(axis=1)
                + Delta / 2 * z.sum(axis=1))
    return states, energies.astype(float)


def classical_periodic_free_energy(T, J, Delta, N):
    """Exact finite-ring free energy at h=0 without dense diagonalization."""
    if T <= 0 or N < 3:
        raise ValueError("require T>0, N>=3")
    _, energies = _classical_energies(J, Delta, N)
    logZ = float(np.logaddexp.reduce(-energies / T))
    return -T * logZ / N


def free_energy(T, J, Delta, h, N):
    if T <= 0 or N < 3:
        raise ValueError("require T>0, N>=3")
    if h == 0.0:
        return classical_periodic_free_energy(T, J, Delta, N)
    states, diag = _classical_energies(J, Delta, N)
    H = np.diag(diag)
    for site in range(N):
        H[states, states ^ (1 << site)] = h / 2
    eig = np.linalg.eigvalsh(H)
    logZ = float(np.logaddexp.reduce(-eig / T))
    return -T * logZ / N


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--T", type=float, required=True)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--h", type=float, required=True)
    parser.add_argument("--N", type=int, nargs="+", default=[4, 6, 8, 10])
    args = parser.parse_args()
    start = time.perf_counter()
    values = [{"N": n, "f": free_energy(args.T, args.J, args.Delta, args.h, n)}
              for n in args.N]
    print(json.dumps({"parameters": vars(args), "seed": None,
                      "elapsed_seconds": time.perf_counter() - start,
                      "values": values}, indent=2))


if __name__ == "__main__":
    main()
