"""Refine a bracketed FT-TC normal/finite-field equality candidate.

The equilibrium effective model and units are those of ft_tc_thermal_threshold.
Golden-section search assumes a single minimum in the supplied h interval.
It does not locate other extrema or prove an infinite-chain phase boundary.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

from ft_tc_ed import free_energy as periodic_free_energy
from ft_tc_nlce import open_total_free_energy
from ft_tc_normal_curvature import normal_curvature
from ft_tc_thermal_threshold import aitken_last_three, equal_coupling
from ft_tc_transfer import classical_chain


def make_evaluator(T, J, Delta, omega, method, N=None, orders=None):
    """Return (f_normal, evaluate_h) for one fixed numerical approximation."""
    if min(T, omega) <= 0:
        raise ValueError("require T>0 and omega>0")
    if method == "ed":
        if N is None or N < 3:
            raise ValueError("ED requires N>=3")
        normal = periodic_free_energy(T, J, Delta, 0.0, N)

        def evaluate(h):
            f_h = periodic_free_energy(T, J, Delta, h, N)
            return {"h": h, "f_h": f_h, "f_normal": normal,
                    "g_equal": equal_coupling(omega, h, normal, f_h)}

    elif method == "nlce":
        orders = sorted(set(orders or []))
        if len(orders) != 3 or orders[0] < 2 or orders[1] != orders[0] + 1 or orders[2] != orders[1] + 1:
            raise ValueError("NLCE requires three consecutive L>=2")
        normal = classical_chain(T, J, Delta)
        lengths = sorted(set(orders) | {L - 1 for L in orders})

        def evaluate(h):
            F = {L: open_total_free_energy(T, J, Delta, h, L) for L in lengths}
            sequence = [F[L] - F[L - 1] for L in orders]
            accelerated = aitken_last_three(sequence)
            if accelerated is None:
                if max(abs(sequence[i] - sequence[-1]) for i in range(2)) > 1e-12:
                    raise ArithmeticError("NLCE Aitken denominator unresolved")
                accelerated = sequence[-1]
            return {"h": h, "f_h": accelerated, "f_h_NLCE_raw": sequence[-1],
                    "f_h_NLCE_orders": dict(zip(orders, sequence)),
                    "aitken_used": accelerated != sequence[-1],
                    "f_normal": normal,
                    "g_equal": equal_coupling(omega, h, normal, accelerated),
                    "g_equal_raw": equal_coupling(omega, h, normal, sequence[-1])}

    else:
        raise ValueError("method must be ed or nlce")
    return normal, evaluate


def golden_refine(evaluate, lo, hi, tolerance, max_evaluations=32):
    """Minimize g_equal on a positive bracket, preserving every evaluation."""
    if not (0 < lo < hi) or tolerance <= 0 or max_evaluations < 5:
        raise ValueError("require 0<lo<hi, tolerance>0, max_evaluations>=5")
    if tolerance >= hi - lo:
        raise ValueError("tolerance must be smaller than bracket width")
    initial_lo, initial_hi = lo, hi
    rows = {}

    def at(h):
        if h not in rows:
            if len(rows) >= max_evaluations:
                raise RuntimeError("evaluation budget exhausted")
            row = evaluate(h)
            if row["g_equal"] is None or not math.isfinite(row["g_equal"]):
                raise ArithmeticError(f"nonpositive or unresolved matter free-energy gain at h={h}")
            rows[h] = row
        return rows[h]["g_equal"]

    at(lo)
    at(hi)
    ratio = (math.sqrt(5) - 1) / 2
    c = hi - ratio * (hi - lo)
    d = lo + ratio * (hi - lo)
    fc, fd = at(c), at(d)
    while hi - lo > tolerance:
        if fc <= fd:
            hi, d, fd = d, c, fc
            c = hi - ratio * (hi - lo)
            fc = at(c)
        else:
            lo, c, fc = c, d, fd
            d = lo + ratio * (hi - lo)
            fd = at(d)
    best = min(rows.values(), key=lambda row: row["g_equal"])
    return {"original_bracket": [initial_lo, initial_hi],
            "final_bracket": [lo, hi], "h_tolerance": tolerance,
            "best_evaluated": best,
            "at_original_edge": best["h"] in (initial_lo, initial_hi),
            "evaluations": [rows[h] for h in sorted(rows)]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, required=True)
    p.add_argument("--method", choices=["ed", "nlce"], required=True)
    p.add_argument("--N", type=int, default=10)
    p.add_argument("--L", type=int, nargs=3, default=[10, 11, 12])
    p.add_argument("--lo", type=float, required=True)
    p.add_argument("--hi", type=float, required=True)
    p.add_argument("--tol", type=float, default=0.005)
    p.add_argument("--max-evaluations", type=int, default=32)
    a = p.parse_args()
    started = time.perf_counter()
    try:
        normal, evaluate = make_evaluator(a.T, a.J, a.Delta, a.omega,
                                          a.method, a.N, a.L)
        refined = golden_refine(evaluate, a.lo, a.hi, a.tol, a.max_evaluations)
    except (ValueError, ArithmeticError, RuntimeError) as exc:
        p.error(str(exc))
    source_dir = Path(__file__).parent
    names = ["ft_tc_thermal_refine.py", "ft_tc_thermal_threshold.py", "ft_tc_ed.py",
             "ft_tc_nlce.py", "ft_tc_normal_curvature.py", "ft_tc_transfer.py"]
    print(json.dumps({"parameters": vars(a), "units": "hbar=k_B=1",
                      "f_normal_approximation": normal,
                      "f_normal_infinite_exact": classical_chain(a.T, a.J, a.Delta),
                      "g_local_exact": normal_curvature(a.T, a.J, a.Delta, a.omega, 0)["g_local"],
                      "refinement": refined,
                      "sources_sha256": {n: hashlib.sha256((source_dir / n).read_bytes()).hexdigest()
                                         for n in names},
                      "seed": None, "elapsed_seconds": time.perf_counter() - started,
                      "limitations": "one user-supplied h bracket; finite ED/NLCE; no global-extrema or strict error bound"},
                     indent=2))


if __name__ == "__main__":
    main()
