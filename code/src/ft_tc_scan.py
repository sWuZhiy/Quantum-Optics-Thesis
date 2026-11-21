"""Coarse finite-temperature cavity-landscape survey for FT-TC P0.

Only a grid diagnostic: local minima between samples can be missed.
Phi is restricted to [0,g/omega] by |<s_x>|<=1/2.
"""

import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from ft_tc_ed import free_energy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--T", type=float, nargs="+", required=True)
    parser.add_argument("--g", type=float, nargs="+", required=True)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--omega", type=float, required=True)
    parser.add_argument("--N", type=int, required=True)
    parser.add_argument("--points", type=int, default=33)
    args = parser.parse_args()
    if min(args.T) <= 0 or min(args.g) < 0 or args.omega <= 0 or args.points < 3:
        parser.error("require T>0, g>=0, omega>0, points>=3")
    started = time.perf_counter()
    cases = []
    for T in args.T:
        for g in args.g:
            phi = np.linspace(0, g / args.omega, args.points)
            values = [float(args.omega * x * x
                            + free_energy(T, args.J, args.Delta, 4 * g * float(x), args.N))
                      for x in phi]
            local = [i for i in range(args.points)
                     if (i == 0 or values[i] <= values[i - 1])
                     and (i == args.points - 1 or values[i] <= values[i + 1])]
            best = min(range(args.points), key=values.__getitem__)
            cases.append({"T": T, "g": g, "phi_grid": phi.tolist(), "Phi_grid": values,
                          "minimum_indices": local, "best_index": best,
                          "delta_best_vs_normal": values[best] - values[0]})
    source = Path(__file__).with_name("ft_tc_ed.py")
    print(json.dumps({"parameters": vars(args), "ed_sha256":
                      hashlib.sha256(source.read_bytes()).hexdigest(), "seed": None,
                      "elapsed_seconds": time.perf_counter() - started, "cases": cases}, indent=2))


if __name__ == "__main__":
    main()
