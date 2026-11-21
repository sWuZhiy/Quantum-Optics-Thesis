"""Locally minimize an open-chain NLCE estimate, then verify at larger order.

This assumes the selected side-branch bracket contains one minimum. Aitken
acceleration assumes the leading finite-cluster correction is geometric.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

from ft_tc_minimize import golden_min
from ft_tc_nlce import open_total_free_energy
from ft_tc_transfer import classical_chain


def aitken(a, b, c):
    return c - (c - b) ** 2 / (c - 2 * b + a)


def nlce_values(T, J, Delta, h, Lmax):
    F = {L: open_total_free_energy(T, J, Delta, h, L)
         for L in range(Lmax - 3, Lmax + 1)}
    f = {L: F[L] - F[L - 1] for L in range(Lmax - 2, Lmax + 1)}
    return {"raw_Lmax": f[Lmax],
            "aitken_Lmax": aitken(f[Lmax - 2], f[Lmax - 1], f[Lmax])}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, required=True)
    p.add_argument("--g", type=float, nargs="+", required=True)
    p.add_argument("--lo", type=float, required=True)
    p.add_argument("--hi", type=float, required=True)
    p.add_argument("--tol", type=float, default=1e-5)
    a = p.parse_args()
    if a.T <= 0 or a.omega <= 0 or a.tol <= 0 or min(a.g) < 0 or not 0 <= a.lo < a.hi:
        p.error("invalid parameters")
    if a.hi > min(a.g) / a.omega:
        p.error("bracket must fit inside [0,g/omega] for every g")
    start = time.perf_counter()
    normal = classical_chain(a.T, a.J, a.Delta)
    cases = []
    for g in a.g:
        objective = lambda phi: (a.omega * phi * phi
                                 + nlce_values(a.T, a.J, a.Delta, 4 * g * phi, 10)["aitken_Lmax"])
        phi, value, evaluations = golden_min(objective, a.lo, a.hi, a.tol)
        verified = []
        for Lmax in (10, 11, 12):
            estimate = nlce_values(a.T, a.J, a.Delta, 4 * g * phi, Lmax)
            verified.append({"Lmax": Lmax, "Phi_raw": a.omega * phi * phi + estimate["raw_Lmax"],
                             "Phi_Aitken": a.omega * phi * phi + estimate["aitken_Lmax"]})
        cases.append({"g": g, "phi": phi, "evaluations": evaluations,
                      "Phi_normal_infinite": normal, "search_Phi": value,
                      "verified": verified})
    source = Path(__file__).with_name("ft_tc_nlce.py")
    print(json.dumps({"parameters": vars(a), "nlce_sha256":
                      hashlib.sha256(source.read_bytes()).hexdigest(),
                      "seed": None, "elapsed_seconds": time.perf_counter() - start,
                      "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
