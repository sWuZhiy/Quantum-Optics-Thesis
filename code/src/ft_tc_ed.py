"""Periodic finite-chain exact diagonalization benchmark for FT-TC matter free energy.

H = J sum sigma_z[i] sigma_z[i+1] + Delta/2 sum sigma_z[i]
    + h/2 sum sigma_x[i].  Dense diagonalization limits usable N.
"""

import argparse
import json
import math
import time

import numpy as np


def free_energy(T, J, Delta, h, N):
    if T <= 0 or N < 3:
        raise ValueError("require T>0, N>=3")
    states = np.arange(1 << N, dtype=np.int64)
    bits = (states[:, None] >> np.arange(N)) & 1
    z = 1 - 2 * bits
    diag = J * (z * np.roll(z, -1, axis=1)).sum(axis=1) + Delta / 2 * z.sum(axis=1)
    H = np.diag(diag.astype(float))
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
