"""Post-processing for the global stationary-point sweep.

Compares the measured interior-minimum depth below g_local,
    depth(T) = g_local(T) - min_h g_equal(T,h),
with the local Landau prediction from the zero-field coefficients
    depth_Landau = g_local * a4^2 / (8 a6 |a2|)
(valid on the first-order side a4<0, where the interior minimum sits at
h*^2 = -a4/(2 a6)).  The quadratic collapse depth(T) ~ a4(T)^2 is the
signature that the finite-h minimum is the first-order precursor that
dissolves at T*.
"""

import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_quartic import infinite_chain  # noqa: E402
from ft_tc_landau_paths import landau_coefficients  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sweep", type=Path, required=True,
                        help="stationary-sweep JSON")
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--N", type=int, nargs="+", default=[10, 12])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    sweep = json.loads(args.sweep.read_text(encoding="utf-8"))
    rows = []
    for value in sweep["values"]:
        T = value["T"]
        infinite = infinite_chain(T, args.J, args.Delta)
        a2 = float(infinite["a2"])
        a4 = float(infinite["a4"])
        g_local = float(value["g_local"])
        a6_values = {}
        for N in args.N:
            coeff = landau_coefficients(T, args.J, args.Delta, N, 6)
            a6_values[str(N)] = coeff["a6"]
        a6 = a6_values[str(args.N[-1])]
        depth = value["depth_below_g_local"]
        row = {"T": T, "g_local": g_local, "a2": a2, "a4": a4,
               "a6": a6, "a6_by_N": a6_values,
               "depth_measured": depth,
               "h_star": (value["minima"][0]["h_star"] if value["minima"]
                          else None)}
        if a4 < 0 and depth is not None and a6 > 0:
            predicted = g_local * a4 * a4 / (8.0 * a6 * abs(a2))
            row["depth_landau_prediction"] = predicted
            row["predicted_h_star"] = math.sqrt(-a4 / (2.0 * a6))
            row["ratio_measured_over_predicted"] = depth / predicted
        rows.append(row)
    parameters = {key: (str(value) if isinstance(value, Path) else value)
                  for key, value in vars(args).items()}
    payload = json.dumps({"parameters": parameters, "rows": rows}, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
