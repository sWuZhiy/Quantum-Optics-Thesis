"""Finite-chain zero-temperature normal/side-branch crossing scan.

For each transverse field h>0, solve the mixed-field Ising ground energy
e_N(h). The coupling g_equal(h)^2 = omega*h^2/[16*(e_N(0)-e_N(h))]
makes that field's cavity displacement equal in energy to the normal branch.
The minimum over h is a finite-chain approximation to the first global
superradiant threshold. A grid minimum does not locate an exact phase line.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

from ft_tc_ground_state import ground_state_energy


def scan(J, Delta, omega, sizes, fields, tol=1e-10, maxiter=160,
         g=None, measure_staggered=False):
    if omega <= 0 or any(h <= 0 for h in fields):
        raise ValueError("require omega>0 and positive transverse fields")
    if g is not None and g <= 0:
        raise ValueError("require g>0 when a cavity landscape is requested")
    output = []
    for N in sizes:
        normal = ground_state_energy(J, Delta, 0.0, N, tol=tol, maxiter=maxiter,
                                     measure_staggered=measure_staggered)
        rows = []
        for h in fields:
            result = ground_state_energy(J, Delta, h, N, tol=tol, maxiter=maxiter,
                                         measure_staggered=measure_staggered)
            if not result["converged"]:
                raise RuntimeError(f"Lanczos failed for N={N}, h={h}")
            gain = normal["energy_per_site"] - result["energy_per_site"]
            if gain <= 0:
                raise RuntimeError(f"non-positive spin energy gain for N={N}, h={h}")
            row = {"h": h, "e_spin": result["energy_per_site"],
                   "g_equal": math.sqrt(omega * h * h / (16 * gain)),
                   "iterations": result["iterations"],
                   "residual": result["residual"]}
            if g is not None:
                phi = h / (4 * g)
                row.update({"phi": phi, "photon_density_coherent": phi * phi,
                            "cavity_energy": omega * phi * phi + result["energy_per_site"],
                            "cavity_minus_normal": omega * phi * phi - gain})
            if measure_staggered:
                row["staggered_m2"] = result["staggered_m2"]
            rows.append(row)
        i = min(range(len(rows)), key=lambda k: rows[k]["g_equal"])
        item = {"N": N, "normal_energy": normal["energy_per_site"],
                "minimum_grid_index": i, "minimum_grid": rows[i],
                "values": rows}
        if measure_staggered:
            item["normal_staggered_m2"] = normal["staggered_m2"]
        if g is not None:
            j = min(range(len(rows)), key=lambda k: rows[k]["cavity_energy"])
            item["minimum_cavity_grid_index"] = j
            item["minimum_cavity_grid"] = rows[j]
        output.append(item)
    return output


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, default=1.0)
    p.add_argument("--g", type=float, default=None)
    p.add_argument("--N", type=int, nargs="+", default=[8, 12, 16])
    p.add_argument("--h-min", type=float, required=True)
    p.add_argument("--h-max", type=float, required=True)
    p.add_argument("--points", type=int, default=21)
    p.add_argument("--tol", type=float, default=1e-10)
    p.add_argument("--maxiter", type=int, default=160)
    p.add_argument("--staggered-m2", action="store_true")
    args = p.parse_args()
    if args.h_min <= 0 or args.h_max < args.h_min or args.points < 2:
        p.error("require 0<h_min<=h_max and points>=2")
    if args.g is not None and args.h_max > 4 * args.g * args.g / args.omega:
        p.error("requested field exceeds the full cavity-minimum interval h<=4*g^2/omega")
    started = time.perf_counter()
    fields = np.linspace(args.h_min, args.h_max, args.points).tolist()
    values = scan(args.J, args.Delta, args.omega, args.N, fields,
                  args.tol, args.maxiter, args.g, args.staggered_m2)
    sources = [Path(__file__), Path(__file__).with_name("ft_tc_ground_state.py")]
    print(json.dumps({"parameters": vars(args), "seed": None,
                      "source_sha256": {source.name: hashlib.sha256(source.read_bytes()).hexdigest()
                                        for source in sources},
                      "elapsed_seconds": time.perf_counter() - started,
                      "values": values}, indent=2))


if __name__ == "__main__":
    main()
