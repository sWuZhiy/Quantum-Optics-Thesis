"""Compare infinite-space Trotter free energy with finite-chain ED at saved side minima.

The M extrapolations are diagnostics, not certified error bounds.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from ft_tc_transfer import free_energy


def intercept(rows, degree, count):
    last = rows[-count:]
    x = np.array([1 / row["M"] ** 2 for row in last])
    y = np.array([row["Phi"] for row in last])
    return float(np.polynomial.polynomial.polyfit(x, y, degree)[0])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--M", type=int, nargs="+", default=[10, 12, 14, 16, 18, 20])
    args = parser.parse_args()
    if len(set(args.M)) < 4:
        parser.error("require at least four distinct Trotter numbers")
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    p = data["parameters"]
    values = []
    start = time.perf_counter()
    for case in data["cases"]:
        phi, g = case["phi_Nsearch"], case["g"]
        h = 4 * g * phi
        rows = []
        for M in sorted(set(args.M)):
            v = free_energy(p["T"], p["J"], p["Delta"], h, M)
            rows.append({"M": M, "Phi": p["omega"] * phi * phi + v["f"],
                         "iterations": v["iterations"], "residual": v["residual"]})
        ed12 = next(item["Phi"] for item in case["verified_at_same_phi"]
                    if item["N"] == 12)
        values.append({"g": g, "phi": phi, "h": h, "values": rows,
                       "linear_last2": intercept(rows, 1, 2),
                       "linear_last3": intercept(rows, 1, 3),
                       "quadratic_last3": intercept(rows, 2, 3),
                       "quadratic_last4": intercept(rows, 2, 4),
                       "ED_N12_same_phi": ed12,
                       "normal_infinite": case["Phi_normal_infinite"]})
    source = Path(__file__).with_name("ft_tc_transfer.py")
    print(json.dumps({"input": str(args.input), "parameters": p, "M": args.M,
                      "transfer_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                      "seed": None, "elapsed_seconds": time.perf_counter() - start,
                      "cases": values}, indent=2))


if __name__ == "__main__":
    main()
