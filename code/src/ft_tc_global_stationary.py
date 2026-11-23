"""Continuous all-branch stationary-point search for g_equal(h) on the bounded
h interval, with cross-method error diagnostics.

For the FT-TC equilibrium effective model (hbar=k_B=1) and fixed T, J, Delta,
omega, the equality coupling of the normal branch and a finite field phi=h/(4g)
is g_equal(h)^2 = omega h^2 / [16 (f_spin(T,0)-f_spin(T,h))].  Its infimum
over h>0 is the first global loss of the normal minimum in the mean-field free
energy.  Because g_equal(h)^2 >= omega h/8, any point with g_equal <= g_ref
lies in h <= 8 g_ref^2/omega, so with g_ref = g_local the search domain is
bounded by h_max = 8 g_local^2/omega.

Pipeline for each T:
  1. analytic g_local (exact normal-branch curvature);
  2. dense log-uniform ED scan over [h_min, h_max] (default N=10) and
     detection of every interior local minimum of g_equal(h);
  3. golden-section refinement of each detected bracket (ED, N=12);
  4. cross-checks at each refined minimum: open-chain NLCE (L=10,11,12 with
     Aitken) and the infinite-space Suzuki-Trotter transfer matrix
     (M=16,18,20, quadratic 1/M^2 extrapolation, last-3 vs last-4 windows);
  5. per-minimum error diagnostics: ED N=10 vs N=12 change, NLCE vs ED
     difference, transfer extrapolation window spread.

This excludes wide unsampled branches but a discrete scan can never exclude an
arbitrarily narrow minimum; the continuous refinement assumes each detected
bracket contains a single minimum.  The output is a diagnostic, not a phase
boundary.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

from ft_tc_ed import free_energy as periodic_free_energy
from ft_tc_nlce import open_total_free_energy
from ft_tc_normal_curvature import normal_curvature
from ft_tc_thermal_threshold import aitken_last_three, equal_coupling
from ft_tc_transfer import classical_chain
from ft_tc_transfer import free_energy as transfer_free_energy


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def scan_minima(T, J, Delta, omega, h_min, h_max, points, N):
    """Dense ED scan of g_equal(h); return (h_grid, g_grid, bracket list)."""
    h_grid = np.geomspace(h_min, h_max, points)
    normal = periodic_free_energy(T, J, Delta, 0.0, N)
    g_grid = np.empty(points)
    for i, h in enumerate(h_grid):
        f_h = periodic_free_energy(T, J, Delta, h, N)
        g_grid[i] = equal_coupling(omega, h, normal, f_h)
    brackets = []
    for i in range(1, points - 1):
        if g_grid[i] < g_grid[i - 1] and g_grid[i] <= g_grid[i + 1]:
            brackets.append((float(h_grid[i - 1]), float(h_grid[i + 1]),
                             float(g_grid[i])))
    return h_grid, g_grid, brackets


def golden_refine(T, J, Delta, omega, N, lo, hi, tol):
    """Golden-section refinement of one g_equal(h) bracket (single minimum)."""
    normal = periodic_free_energy(T, J, Delta, 0.0, N)
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    a, b = lo, hi
    c = b - phi * (b - a)
    d = a + phi * (b - a)

    def evaluate(h):
        f_h = periodic_free_energy(T, J, Delta, h, N)
        return equal_coupling(omega, h, normal, f_h)

    fc, fd = evaluate(c), evaluate(d)
    while abs(b - a) > tol:
        if fc <= fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = evaluate(c)
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = evaluate(d)
    h_star = 0.5 * (a + b)
    return h_star, evaluate(h_star), abs(b - a)


def nlce_check(T, J, Delta, omega, h, orders):
    """Open-chain NLCE (raw sequence + Aitken) g_equal at one h."""
    normal = classical_chain(T, J, Delta)
    lengths = sorted(set(orders) | {L - 1 for L in orders})
    F = {L: open_total_free_energy(T, J, Delta, h, L) for L in lengths}
    sequence = [F[L] - F[L - 1] for L in orders]
    accelerated = aitken_last_three(sequence)
    if accelerated is None:
        accelerated = sequence[-1]
    return {"raw_last": sequence[-1],
            "raw_sequence": sequence,
            "aitken": accelerated,
            "g_equal_raw": equal_coupling(omega, h, normal, sequence[-1]),
            "g_equal_aitken": equal_coupling(omega, h, normal, accelerated)}


def transfer_check(T, J, Delta, omega, h, Ms):
    """Infinite-space transfer matrix g_equal with 1/M^2 extrapolation."""
    normal = classical_chain(T, J, Delta)
    rows = []
    for M in Ms:
        f_h = float(transfer_free_energy(T, J, Delta, h, M)["f"])
        rows.append({"M": M, "f_h": f_h,
                     "g_equal": equal_coupling(omega, h, normal, f_h)})
    values = np.array([r["g_equal"] for r in rows])
    inv = np.array([1.0 / M ** 2 for M in Ms])

    def quadratic_fit(mask):
        coeff = np.polyfit(inv[mask], values[mask], 2)
        return float(np.polyval(coeff, 0.0))

    # last-3 vs all-points windows (distinct only when len(Ms) >= 4)
    last3 = quadratic_fit(np.arange(len(Ms)) >= len(Ms) - 3)
    last4 = quadratic_fit(np.ones(len(Ms), dtype=bool))
    return {"rows": rows, "extrap_last3": last3, "extrap_last4": last4,
            "window_spread": abs(last3 - last4)}


def analyze(T, J, Delta, omega, scan, refine, crosscheck):
    if T <= 0 or omega <= 0 or scan["N"] < 3:
        raise ValueError("require T>0, omega>0, N>=3")
    curvature = normal_curvature(T, J, Delta, omega, 1.0)
    g_local = float(curvature["g_local"])
    h_max = 8.0 * g_local * g_local / omega

    h_grid, g_grid, brackets = scan_minima(
        T, J, Delta, omega, scan["h_min"], h_max, scan["points"], scan["N"])
    minima = []
    for lo, hi, g_scan in brackets:
        h_star, g_refined, width = golden_refine(
            T, J, Delta, omega, refine["N"], lo, hi, refine["tol"])
        entry = {"h_star": h_star, "g_equal": g_refined,
                 "bracket_width": width, "scan_value": g_scan}
        if crosscheck:
            entry["nlce"] = nlce_check(T, J, Delta, omega, h_star,
                                       crosscheck["orders"])
            entry["transfer"] = transfer_check(T, J, Delta, omega, h_star,
                                               crosscheck["Ms"])
            entry["error_diagnostics"] = {
                "ed_refine_n": refine["N"],
                "ed_scan_n": scan["N"],
                "ed_refine_minus_scan_value": g_refined - g_scan,
                "nlce_aitken_minus_ed": entry["nlce"]["g_equal_aitken"] - g_refined,
                "transfer_window_spread": entry["transfer"]["window_spread"],
                "transfer_last3_minus_ed":
                    entry["transfer"]["extrap_last3"] - g_refined,
            }
        minima.append(entry)
    minima.sort(key=lambda m: m["g_equal"])
    depth = g_local - minima[0]["g_equal"] if minima else None
    return {"T": T, "J": J, "Delta": Delta, "omega": omega,
            "g_local": g_local, "h_max": h_max,
            "scan_h_min": scan["h_min"], "scan_points": scan["points"],
            "minima": minima, "depth_below_g_local": depth,
            "left_edge_g_equal": float(g_grid[0]),
            "scan_g_min": float(g_grid.min()),
            "scan_g_min_h": float(h_grid[int(g_grid.argmin())])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--T", type=float, nargs="+", required=True)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--scan-n", type=int, default=10)
    parser.add_argument("--scan-h-min", type=float, default=0.005)
    parser.add_argument("--scan-points", type=int, default=200)
    parser.add_argument("--refine-n", type=int, default=12)
    parser.add_argument("--refine-tol", type=float, default=1e-4)
    parser.add_argument("--crosscheck", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    start = time.perf_counter()
    scan_cfg = {"N": args.scan_n, "h_min": args.scan_h_min,
                "points": args.scan_points}
    refine_cfg = {"N": args.refine_n, "tol": args.refine_tol}
    cross_cfg = None
    if args.crosscheck:
        cross_cfg = {"orders": [10, 11, 12], "Ms": [12, 16, 18, 20]}
    values = [analyze(T, args.J, args.Delta, args.omega,
                      scan_cfg, refine_cfg, cross_cfg) for T in args.T]
    parameters = vars(args).copy()
    parameters["output"] = None if args.output is None else str(args.output)
    payload = json.dumps({"parameters": parameters, "seed": None,
                          "elapsed_seconds": time.perf_counter() - start,
                          "sources_sha256": {
                              "ft_tc_global_stationary.py": _sha256(__file__)},
                          "values": values}, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
