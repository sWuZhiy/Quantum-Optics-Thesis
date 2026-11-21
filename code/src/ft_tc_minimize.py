"""Refine a previously bracketed FT-TC side minimum using thermal ED.

Golden-section search assumes one minimum within [lo, hi]; it does not
discover other extrema or certify the thermodynamic limit.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from ft_tc_ed import free_energy
from ft_tc_transfer import classical_chain


def phi_energy(T, J, Delta, omega, g, phi, N):
    return omega * phi * phi + free_energy(T, J, Delta, 4 * g * phi, N)


def golden_min(fun, lo, hi, tolerance):
    ratio = (math.sqrt(5) - 1) / 2
    c = hi - ratio * (hi - lo)
    d = lo + ratio * (hi - lo)
    fc, fd = fun(c), fun(d)
    evaluations = 2
    while hi - lo > tolerance:
        if fc < fd:
            hi, d, fd = d, c, fc
            c = hi - ratio * (hi - lo)
            fc = fun(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + ratio * (hi - lo)
            fd = fun(d)
        evaluations += 1
    x = (lo + hi) / 2
    return x, fun(x), evaluations + 1


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, required=True)
    p.add_argument("--g", type=float, nargs="+", required=True)
    p.add_argument("--lo", type=float, required=True)
    p.add_argument("--hi", type=float, required=True)
    p.add_argument("--N-search", type=int, default=8)
    p.add_argument("--N-verify", type=int, nargs="+", default=[10, 12])
    p.add_argument("--tol", type=float, default=1e-6)
    a = p.parse_args()
    if min(a.T, a.omega, a.tol) <= 0 or min(a.g) < 0 or not 0 <= a.lo < a.hi:
        p.error("require T, omega, tol > 0; g >= 0; 0 <= lo < hi")
    if a.hi > min(a.g) / a.omega:
        p.error("side-minimum bracket must lie in every [0,g/omega]")
    start = time.perf_counter()
    normal = classical_chain(a.T, a.J, a.Delta)
    cases = []
    for g in a.g:
        objective = lambda phi: phi_energy(a.T, a.J, a.Delta, a.omega, g,
                                           phi, a.N_search)
        left, right = objective(a.lo), objective(a.hi)
        phi, value, count = golden_min(objective, a.lo, a.hi, a.tol)
        verified = [{"N": n, "Phi": phi_energy(a.T, a.J, a.Delta,
                                                 a.omega, g, phi, n)}
                    for n in a.N_verify]
        cases.append({"g": g, "phi_Nsearch": phi, "Phi_Nsearch": value,
                      "endpoint_Phi": [left, right], "evaluations": count,
                      "Phi_normal_infinite": normal, "verified_at_same_phi": verified})
    src = Path(__file__).with_name("ft_tc_ed.py")
    print(json.dumps({"parameters": vars(a), "ed_sha256":
                      hashlib.sha256(src.read_bytes()).hexdigest(), "seed": None,
                      "elapsed_seconds": time.perf_counter() - start,
                      "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
