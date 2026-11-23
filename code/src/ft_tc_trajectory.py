"""Candidate thermal-tricritical trajectory T*(Delta) for fixed J.

For each Delta the infinite-chain fourth-order coefficient a4(T) (corrected
adjacent-bond kernel) is bisected for its sign change; the root T* is the
candidate temperature where the local first-order/continuous character
changes.  At each T* the script also computes g_local, the finite-ring sixth
coefficient a6 (N=10), and the transfer-matrix small-field sign of
g_equal-g_local at h=0.05 (the continuous-side h^4 signature).  A Delta
slice with no a4 sign change above T=0 is reported as such (the trajectory
is expected to terminate at the zero-T tricritical ratio Delta=-2J).

This is a trajectory of candidates from local Landau coefficients, not a
proved phase-diagram line.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

from ft_tc_landau_paths import landau_coefficients
from ft_tc_quartic import infinite_chain
from ft_tc_transfer import classical_chain, free_energy as transfer_free_energy


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def bisect_a4_root(J, Delta, lower, upper, tol=1e-13, max_iter=100):
    f_lower = float(infinite_chain(lower, J, Delta)["a4"])
    f_upper = float(infinite_chain(upper, J, Delta)["a4"])
    if f_lower * f_upper > 0:
        return None
    iterations = 0
    while upper - lower > tol and iterations < max_iter:
        middle = 0.5 * (lower + upper)
        f_middle = float(infinite_chain(middle, J, Delta)["a4"])
        if f_lower * f_middle <= 0:
            upper, f_upper = middle, f_middle
        else:
            lower, f_lower = middle, f_middle
        iterations += 1
    return 0.5 * (lower + upper)


def small_field_sign(T, J, Delta, h):
    """Transfer-matrix sign of g_equal-g_local at small h (last-3 1/M^2)."""
    omega = 1.0
    normal = classical_chain(T, J, Delta)
    Ms = (12, 16, 18, 20)
    values = []
    for M in Ms:
        f_h = float(transfer_free_energy(T, J, Delta, h, M)["f"])
        gain = normal - f_h
        values.append(math.sqrt(omega * h * h / (16 * gain)))
    inv = np.array([1.0 / M ** 2 for M in Ms])
    g = np.array(values)
    fit = np.polyfit(inv[-3:], g[-3:], 2)
    extrap = float(np.polyval(fit, 0.0))
    infinite = infinite_chain(T, J, Delta)
    g_local = math.sqrt(-1.0 / (16 * float(infinite["a2"])))
    return extrap - g_local


def analyze_slice(J, Delta, bracket):
    row = {"Delta": Delta, "J": J}
    if bracket is None:
        row["status"] = "no_a4_sign_change"
        return row
    root = bisect_a4_root(J, Delta, *bracket)
    if root is None:
        row["status"] = "no_a4_sign_change_in_bracket"
        return row
    infinite = infinite_chain(root, J, Delta)
    a2 = float(infinite["a2"])
    row.update({
        "status": "candidate",
        "T_star": root,
        "a4_residual": float(infinite["a4"]),
        "a2": a2,
        "g_local": math.sqrt(-1.0 / (16 * a2)),
        "a6_N10": landau_coefficients(root, J, Delta, 10, 6)["a6"],
    })
    row["small_field_sign_Tstar"] = small_field_sign(root, J, Delta, 0.05)
    row["small_field_sign_below"] = small_field_sign(root - 0.01, J, Delta, 0.05)
    row["small_field_sign_above"] = small_field_sign(root + 0.01, J, Delta, 0.05)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, nargs="+", required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    start = time.perf_counter()
    brackets = {
        0.15: (0.2, 0.6), 0.2: (0.25, 0.27), 0.25: (0.15, 0.3),
        0.3: (0.05, 0.3), 0.35: (0.02, 0.2), 0.4: (0.005, 0.1),
        0.45: (0.005, 0.1), 0.5: (0.005, 0.1),
    }
    values = []
    for Delta in args.Delta:
        bracket = brackets.get(Delta)
        if bracket is None:
            raise ValueError(f"no default bracket for Delta={Delta}; "
                             "add one or use --Delta values with known brackets")
        values.append(analyze_slice(args.J, Delta, bracket))
    parameters = {key: (str(value) if isinstance(value, Path) else value)
                  for key, value in vars(args).items()}
    payload = json.dumps({"parameters": parameters, "seed": None,
                          "elapsed_seconds": time.perf_counter() - start,
                          "sources_sha256": {
                              "ft_tc_trajectory.py": _sha256(__file__)},
                          "values": values}, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
