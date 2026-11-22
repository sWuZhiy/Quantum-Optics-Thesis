"""Finite-temperature normal-to-light threshold diagnostic for the FT-TC model.

H_spin(h) = J sum_i sigma^z_i sigma^z_(i+1)
          + Delta/2 sum_i sigma^z_i + h/2 sum_i sigma^x_i,
Phi_T(phi) = omega*phi**2 + f_spin(T, 4*g*phi), with hbar=k_B=1.

For h>0, the coupling at which phi=h/(4*g) equals the normal branch is
g_equal(h)^2 = omega*h^2/[16*(f_spin(T,0)-f_spin(T,h))].  The infimum over
all h>0 is the first global loss of the normal minimum in this mean-field
free energy.  A finite grid/cluster scan is only a diagnostic, not a
thermodynamic phase boundary.  It does not find transitions between two
nonzero-photon branches or locate a tricritical endpoint.
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
from ft_tc_transfer import classical_chain


def equal_coupling(omega, h, f_normal, f_h):
    """Return a finite-h normal/side equality point, or None if unresolved."""
    if omega <= 0 or h <= 0:
        raise ValueError("require omega>0 and h>0")
    gain = f_normal - f_h
    if gain <= 0:
        return None
    return math.sqrt(omega * h * h / (16 * gain))


def aitken_last_three(values):
    """Aitken extrapolation of three consecutive NLCE orders, if stable."""
    first, middle, last = values[-3:]
    denominator = last - 2 * middle + first
    if abs(denominator) <= 1e-14:
        return None
    return last - (last - middle) ** 2 / denominator


def scan_ed(T, J, Delta, omega, h_values, sizes):
    normal = {n: periodic_free_energy(T, J, Delta, 0.0, n) for n in sizes}
    rows = []
    for h in h_values:
        estimates = []
        for n in sizes:
            f_h = periodic_free_energy(T, J, Delta, h, n)
            estimates.append({"N": n, "f_normal": normal[n], "f_h": f_h,
                              "gain": normal[n] - f_h,
                              "g_equal": equal_coupling(omega, h, normal[n], f_h)})
        rows.append({"h": h, "values": estimates})
    return rows


def scan_nlce(T, J, Delta, omega, h_values, orders):
    needed = sorted(set(orders) | {order - 1 for order in orders})
    normal_exact = classical_chain(T, J, Delta)
    F0 = {L: open_total_free_energy(T, J, Delta, 0.0, L) for L in needed}
    normal_orders = {L: F0[L] - F0[L - 1] for L in orders}
    rows = []
    for h in h_values:
        F = {L: open_total_free_energy(T, J, Delta, h, L) for L in needed}
        estimates = []
        sequence = []
        for L in orders:
            f_h = F[L] - F[L - 1]
            sequence.append(f_h)
            estimates.append({"L": L, "f_normal_exact": normal_exact,
                              "f_normal_order": normal_orders[L],
                              "f_h": f_h, "gain": normal_exact - f_h,
                              "g_equal": equal_coupling(omega, h, normal_exact, f_h)})
        row = {"h": h, "values": estimates}
        if len(orders) >= 3 and orders[-1] == orders[-2] + 1 == orders[-3] + 2:
            accelerated = aitken_last_three(sequence)
            row["f_Aitken"] = accelerated
            row["g_equal_Aitken"] = (None if accelerated is None else
                                     equal_coupling(omega, h, normal_exact, accelerated))
        rows.append(row)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, required=True)
    p.add_argument("--method", choices=("ed", "nlce"), required=True)
    p.add_argument("--N", type=int, nargs="+", default=[8, 10])
    p.add_argument("--L", type=int, nargs="+", default=[10, 11, 12])
    p.add_argument("--h-values", type=float, nargs="+", default=None)
    p.add_argument("--h-min", type=float, default=0.1)
    p.add_argument("--h-max", type=float, default=1.0)
    p.add_argument("--points", type=int, default=10)
    a = p.parse_args()
    if a.T <= 0 or a.omega <= 0:
        p.error("require T>0, omega>0")
    h_values = (sorted(set(a.h_values)) if a.h_values is not None else
                [float(h) for h in np.linspace(a.h_min, a.h_max, a.points)])
    if not h_values or any(h <= 0 for h in h_values):
        p.error("all h values must be positive")
    if a.method == "ed":
        sizes = sorted(set(a.N))
        if sizes[0] < 3:
            p.error("require N>=3")
    else:
        orders = sorted(set(a.L))
        if orders[0] < 2:
            p.error("require L>=2")
    start = time.perf_counter()
    rows = (scan_ed(a.T, a.J, a.Delta, a.omega, h_values, sizes)
            if a.method == "ed" else
            scan_nlce(a.T, a.J, a.Delta, a.omega, h_values, orders))
    label = "N" if a.method == "ed" else "L"
    groups = sizes if a.method == "ed" else orders
    minima = []
    for group in groups:
        candidates = [(row["h"], value["g_equal"])
                      for row in rows for value in row["values"]
                      if value[label] == group and value["g_equal"] is not None]
        if candidates:
            h_star, g_star = min(candidates, key=lambda pair: pair[1])
            minima.append({label: group, "h_grid_min": h_star, "g_grid_min": g_star,
                           "boundary_of_h_grid": h_star in (h_values[0], h_values[-1])})
    if a.method == "nlce":
        accelerated = [(row["h"], row.get("g_equal_Aitken")) for row in rows
                       if row.get("g_equal_Aitken") is not None]
        if accelerated:
            h_star, g_star = min(accelerated, key=lambda pair: pair[1])
            minima.append({"method": "Aitken_last_three", "h_grid_min": h_star,
                           "g_grid_min": g_star,
                           "boundary_of_h_grid": h_star in (h_values[0], h_values[-1])})
    source_dir = Path(__file__).parent
    sources = ["ft_tc_thermal_threshold.py", "ft_tc_ed.py", "ft_tc_nlce.py",
               "ft_tc_normal_curvature.py", "ft_tc_transfer.py"]
    out = {"model": "FT-TC thermal normal-branch threshold diagnostic",
           "units": "hbar=k_B=1", "parameters": vars(a),
           "h_values": h_values,
           "g_local_exact": normal_curvature(a.T, a.J, a.Delta, a.omega, 0)["g_local"],
           "f_normal_infinite_exact": classical_chain(a.T, a.J, a.Delta),
           "minima_on_sampled_h_grid": minima, "rows": rows,
           "sources_sha256": {name: hashlib.sha256((source_dir / name).read_bytes()).hexdigest()
                              for name in sources},
           "seed": None, "elapsed_seconds": time.perf_counter() - start,
           "limitations": "finite h grid and finite ED/NLCE orders; no continuous-h or independent-method convergence claim"}
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
