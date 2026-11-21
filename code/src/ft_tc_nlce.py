"""Finite-temperature 1D open-chain NLCE pilot for the mixed-field Ising chain.

For contiguous open clusters, the order-L thermodynamic free-energy estimate
is F_L-F_(L-1), where F_L=-T log Z_L is the total open-chain free energy.
The difference converges only when the thermal correlation length is short
compared with L. Dense diagonalization presently limits L to about 12.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np


def open_total_free_energy(T, J, Delta, h, L):
    if T <= 0 or L < 1:
        raise ValueError("require T>0 and L>=1")
    states = np.arange(1 << L, dtype=np.int64)
    bits = (states[:, None] >> np.arange(L)) & 1
    z = 1 - 2 * bits
    diagonal = J * (z[:, :-1] * z[:, 1:]).sum(axis=1) + Delta / 2 * z.sum(axis=1)
    H = np.diag(diagonal.astype(float))
    for site in range(L):
        H[states, states ^ (1 << site)] = h / 2
    energies = np.linalg.eigvalsh(H)
    return -T * float(np.logaddexp.reduce(-energies / T))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--h", type=float, required=True)
    p.add_argument("--L", type=int, nargs="+", default=list(range(4, 13)))
    a = p.parse_args()
    lengths = sorted(set(a.L) | {L - 1 for L in a.L})
    if min(lengths) < 1:
        p.error("require all L>=2")
    started = time.perf_counter()
    F = {L: open_total_free_energy(a.T, a.J, a.Delta, a.h, L) for L in lengths}
    rows = [{"L": L, "f_NLCE": F[L] - F[L - 1], "F_open": F[L]}
            for L in sorted(set(a.L))]
    # Aitken acceleration is reported only as a diagnostic: it assumes the
    # leading finite-cluster correction is approximately geometric.
    for i in range(2, len(rows)):
        if rows[i - 2]["L"] + 1 != rows[i - 1]["L"] or rows[i - 1]["L"] + 1 != rows[i]["L"]:
            continue
        previous, middle, current = (rows[j]["f_NLCE"] for j in (i - 2, i - 1, i))
        denominator = current - 2 * middle + previous
        if abs(denominator) > 1e-15:
            rows[i]["f_Aitken"] = current - (current - middle) ** 2 / denominator
    source = Path(__file__)
    print(json.dumps({"parameters": vars(a), "source_sha256":
                      hashlib.sha256(source.read_bytes()).hexdigest(),
                      "seed": None, "elapsed_seconds": time.perf_counter() - started,
                      "values": rows}, indent=2))


if __name__ == "__main__":
    main()
