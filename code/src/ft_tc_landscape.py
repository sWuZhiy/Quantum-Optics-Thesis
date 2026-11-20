"""Diagnostic cavity free-energy landscape for the FT-TC P0 check.

This is a grid and Trotter-extrapolation diagnostic, not a phase-boundary solver.
For omega>0 and g>=0, symmetry and |m_x|<=1/2 restrict every global
minimum of Phi(phi)=omega*phi**2+f_spin(T,4*g*phi) to 0<=phi<=g/omega.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from ft_tc_transfer import free_energy as transfer_free_energy
from ft_tc_ed import free_energy as ed_free_energy


def fits(values, degree, count):
    selected = values[-count:]
    x = np.array([1 / row["M"] ** 2 for row in selected])
    y = np.array([row["Phi"] for row in selected])
    return float(np.polynomial.polynomial.polyfit(x, y, degree)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--T", type=float, required=True)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--omega", type=float, required=True)
    parser.add_argument("--g", type=float, required=True)
    parser.add_argument("--points", type=int, default=11)
    parser.add_argument("--solver", choices=["transfer", "ed"], default="transfer")
    parser.add_argument("--M", type=int, nargs="+", default=[10, 14, 18, 20])
    parser.add_argument("--N", type=int, nargs="+", default=[8, 10, 12])
    args = parser.parse_args()
    if args.omega <= 0 or args.g < 0 or args.points < 3:
        parser.error("require omega>0, g>=0, points>=3")
    if args.solver == "transfer" and len(set(args.M)) < 3:
        parser.error("require at least three distinct Trotter numbers")
    if args.solver == "ed" and len(set(args.N)) < 2:
        parser.error("require at least two distinct chain lengths")
    m_values = sorted(set(args.M))
    n_values = sorted(set(args.N))
    start = time.perf_counter()
    result = []
    for phi in np.linspace(0, args.g / args.omega, args.points):
        rows = []
        if args.solver == "transfer":
            for m in m_values:
                value = transfer_free_energy(args.T, args.J, args.Delta, 4 * args.g * float(phi), m)
                rows.append({"M": m, "Phi": args.omega * float(phi) ** 2 + value["f"],
                             "iterations": value["iterations"], "residual": value["residual"]})
            result.append({"phi": float(phi), "h": 4 * args.g * float(phi), "values": rows,
                           "fit_1_over_M2_last2": fits(rows, 1, 2),
                           "fit_1_over_M2_last3": fits(rows, 1, 3),
                           "fit_1_over_M2_quadratic_last3": fits(rows, 2, 3)})
        else:
            for n in n_values:
                value = ed_free_energy(args.T, args.J, args.Delta, 4 * args.g * float(phi), n)
                rows.append({"N": n, "Phi": args.omega * float(phi) ** 2 + value})
            result.append({"phi": float(phi), "h": 4 * args.g * float(phi), "values": rows,
                           "last_size_difference": rows[-1]["Phi"] - rows[-2]["Phi"]})
    source = Path(__file__).with_name("ft_tc_transfer.py" if args.solver == "transfer" else "ft_tc_ed.py")
    print(json.dumps({"parameters": vars(args), "phi_interval_proof":
                      "symmetry; dPhi/dphi >= 2*omega*phi-2*g for phi>=0",
                      "solver_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                      "seed": None, "elapsed_seconds": time.perf_counter() - start,
                      "grid": result}, indent=2))


if __name__ == "__main__":
    main()
