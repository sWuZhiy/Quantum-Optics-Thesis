"""Thermal-limit free energy of the mixed-field Ising matter chain.

H = J sum sigma_z[i] sigma_z[i+1] + (Delta/2) sum sigma_z[i]
    + (h/2) sum sigma_x[i], with hbar = k_B = 1.

The spatial transfer matrix has dimension 2**M for M imaginary-time slices.
Its Perron root gives the infinite-chain free energy at fixed M. The
Trotter limit M -> infinity must be checked separately for each parameter.
"""

import argparse
import json
import math
import time

import numpy as np


def free_energy(T: float, J: float, Delta: float, h: float, M: int,
                tol: float = 1e-10, maxiter: int = 5000) -> dict:
    if T <= 0 or M < 2:
        raise ValueError("Require T>0 and M>=2")
    beta = 1.0 / T
    step = beta / M
    states = np.arange(1 << M, dtype=np.uint32)
    bits = ((states[:, None] >> np.arange(M, dtype=np.uint32)) & 1)
    spins = 1.0 - 2.0 * bits.astype(np.float64)
    flips = np.count_nonzero(bits != np.roll(bits, -1, axis=1), axis=1)
    u = step * abs(h) / 2.0
    if u == 0:
        logw = np.where(flips == 0, -step * Delta * spins.sum(axis=1) / 2, -np.inf)
    else:
        logw = (-step * Delta * spins.sum(axis=1) / 2
                + (M - flips) * math.log(math.cosh(u))
                + flips * math.log(math.sinh(u)))
    shift = float(np.max(logw))
    rootw = np.exp((logw - shift) / 2)
    z = np.array([1.0, -1.0])
    bond = np.exp(-step * J * z[:, None] * z[None, :])

    def apply(vec):
        arr = (rootw * vec).reshape((2,) * M)
        for axis in range(M):
            arr = np.tensordot(bond, arr, axes=(1, axis))
            arr = np.moveaxis(arr, 0, axis)
        return rootw * arr.reshape(-1)

    vec = np.ones(1 << M, dtype=np.float64)
    vec /= np.linalg.norm(vec)
    for iteration in range(1, maxiter + 1):
        acted = apply(vec)
        eigenvalue = float(vec @ acted)
        residual = float(np.linalg.norm(acted - eigenvalue * vec))
        if residual <= tol * max(1.0, abs(eigenvalue)):
            return {"M": M, "f": -T * (math.log(eigenvalue) + shift),
                    "iterations": iteration, "residual": residual,
                    "converged": True}
        vec = acted / np.linalg.norm(acted)
    raise RuntimeError(f"Perron iteration did not converge at M={M}")


def independent_spin(T, Delta, h):
    x = math.hypot(Delta, h) / (2 * T)
    return -T * (np.logaddexp(x, -x))


def classical_chain(T, J, Delta):
    z = np.array([1.0, -1.0])
    onsite = np.exp(-Delta * z / (4 * T))
    mat = onsite[:, None] * np.exp(-J * z[:, None] * z[None, :] / T) * onsite[None, :]
    return -T * math.log(float(np.linalg.eigvalsh(mat)[-1]))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--h", type=float, required=True)
    p.add_argument("--M", type=int, nargs="+", default=[6, 8, 10, 12])
    args = p.parse_args()
    start = time.perf_counter()
    values = [free_energy(args.T, args.J, args.Delta, args.h, m) for m in args.M]
    out = {"model": "mixed_field_ising_infinite_chain", "units": "hbar=kB=1",
           "parameters": {"T": args.T, "J": args.J, "Delta": args.Delta, "h": args.h},
           "values": values, "wall_seconds": time.perf_counter() - start}
    if args.J == 0:
        out["exact"] = independent_spin(args.T, args.Delta, args.h)
    if args.h == 0:
        out["exact"] = classical_chain(args.T, args.J, args.Delta)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
