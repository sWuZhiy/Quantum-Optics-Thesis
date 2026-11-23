"""Local FT-TC tricritical-candidate validation at zero transverse field.

The infinite-chain fourth-order coefficient is rooted by bisection. Exact
finite-ring Dyson paths then provide the sixth-order coefficient at that
temperature. The result is a local Landau acceptance test only: it does not
by itself establish the global phase boundary or uniqueness of a finite-h
minimum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

from ft_tc_landau_paths import landau_coefficients
from ft_tc_quartic import infinite_chain


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fourth_order_root(J: float, Delta: float, lower: float, upper: float,
                      tolerance: float = 1e-13, max_iterations: int = 100):
    """Bracket and bisect the infinite-chain a4(T)=0 root."""
    if lower <= 0 or upper <= lower or tolerance <= 0:
        raise ValueError("require 0 < lower < upper and tolerance > 0")
    f_lower = float(infinite_chain(lower, J, Delta)["a4"])
    f_upper = float(infinite_chain(upper, J, Delta)["a4"])
    if f_lower == 0:
        return lower, lower, 0, f_lower
    if f_upper == 0:
        return upper, upper, 0, f_upper
    if f_lower * f_upper > 0:
        raise ValueError("a4 does not change sign on the supplied bracket")
    iterations = 0
    while upper - lower > tolerance and iterations < max_iterations:
        middle = (lower + upper) / 2
        f_middle = float(infinite_chain(middle, J, Delta)["a4"])
        if f_lower * f_middle <= 0:
            upper, f_upper = middle, f_middle
        else:
            lower, f_lower = middle, f_middle
        iterations += 1
    root = (lower + upper) / 2
    return root, upper - lower, iterations, float(infinite_chain(root, J, Delta)["a4"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--T-bracket", type=float, nargs=2, default=[0.25, 0.27])
    parser.add_argument("--root-tolerance", type=float, default=1e-13)
    parser.add_argument("--N", type=int, nargs="+", default=[6, 8, 10, 12])
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.omega <= 0:
        parser.error("require omega>0")

    started = time.perf_counter()
    root, width, iterations, residual = fourth_order_root(
        args.J, args.Delta, *args.T_bracket, tolerance=args.root_tolerance)
    infinite = infinite_chain(root, args.J, args.Delta)
    finite = [landau_coefficients(root, args.J, args.Delta, N, 6, args.batch_size)
              for N in sorted(set(args.N))]
    a2 = float(infinite["a2"])
    g_local = math.sqrt(-args.omega / (16 * a2))
    for row in finite:
        row["g_equal_minus_g_local_h4_coefficient"] = (
            g_local * row["a6"] / (2 * -a2))

    source_dir = Path(__file__).parent
    source_names = ["ft_tc_tricritical_validate.py", "ft_tc_landau_paths.py",
                    "ft_tc_quartic.py"]
    parameters = vars(args).copy()
    parameters["output"] = None if args.output is None else str(args.output)
    output = {
        "model": "FT-TC zero-field local Landau validation",
        "units": "hbar=k_B=1",
        "parameters": parameters,
        "T_star": root,
        "T_star_final_bracket_width": width,
        "root_iterations": iterations,
        "a4_infinite_residual": residual,
        "a2_infinite": a2,
        "g_local": g_local,
        "finite_ring_coefficients": finite,
        "seed": None,
        "elapsed_seconds": time.perf_counter() - started,
        "sources_sha256": {name: _sha256(source_dir / name) for name in source_names},
        "limitations": (
            "a4 is an infinite-chain zero-field result; a6 is an exact finite-ring "
            "path sequence and requires N convergence. This is a local Landau test, "
            "not a global phase-boundary proof."
        ),
    }
    payload = json.dumps(output, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
