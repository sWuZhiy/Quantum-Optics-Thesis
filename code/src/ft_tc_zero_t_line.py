"""Zero-temperature first-order line g_c(Delta) for fixed J (Z2 closure).

For each Delta<0.4 the T=0 transition is first order below the local
threshold; the finite-chain Lanczos ground energy gives
    g_equal(h)^2 = omega h^2 / [16 (e_N(0) - e_N(h))],
and the minimum over h approximates the first global threshold g_c.  The line
must end at the zero-T tricritical point (Delta=-2J, g_tc=sqrt(-3 omega J/2))
where the minimum retreats to h->0.  Anchors: the integrable Delta=0 point
g_c=0.4090436682, the Langheld QMC value g_c=0.4955766 at Delta=0.2, and the
Koziol tricritical coupling sqrt(0.3) at Delta=0.4.  Grid minima are not an
exact phase line; N<=18 finite-chain results carry no strict thermodynamic
error bound.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

from ft_tc_ground_state import ground_state_energy


def _sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def g_equal(J, Delta, N, h, tol, maxiter, omega=1.0, normal=None):
    """Equal-energy coupling at fixed field, with an optional cached normal state."""
    if omega <= 0:
        raise ValueError("require omega>0")
    if normal is None:
        normal = ground_state_energy(
            J, Delta, 0.0, N, tol=tol, maxiter=maxiter)
    if not normal["converged"]:
        raise RuntimeError(f"normal-state Lanczos failed for N={N}")
    result = ground_state_energy(J, Delta, h, N, tol=tol, maxiter=maxiter)
    if not result["converged"]:
        raise RuntimeError(f"Lanczos failed for N={N}, h={h}")
    gain = normal["energy_per_site"] - result["energy_per_site"]
    if gain <= 0:
        raise RuntimeError(f"non-positive gain for N={N}, h={h}")
    return math.sqrt(omega * h * h / (16.0 * gain)), result


def locate_minimum(J, Delta, N, lo, hi, tol, maxiter, coarse=17, golden=30,
                   omega=1.0):
    """Coarse scan + golden-section refinement of g_equal(h) on [lo, hi]."""
    normal = ground_state_energy(J, Delta, 0.0, N, tol=tol, maxiter=maxiter)
    if not normal["converged"]:
        raise RuntimeError(f"normal-state Lanczos failed for N={N}")

    def evaluate(field):
        return g_equal(J, Delta, N, field, tol, maxiter,
                       omega=omega, normal=normal)

    fields = np.linspace(lo, hi, coarse)
    values = []
    for h in fields:
        values.append(evaluate(h)[0])
    values = np.array(values)
    best = int(values.argmin())
    if best == 0:
        a, b = fields[0], fields[1]
    elif best == coarse - 1:
        a, b = fields[-2], fields[-1]
    else:
        a, b = fields[best - 1], fields[best + 1]
    # golden section
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc = evaluate(c)[0]
    fd = evaluate(d)[0]
    for _ in range(golden):
        if fc <= fd:
            b, d, fd = d, c, fc
            c = b - phi * (b - a)
            fc = evaluate(c)[0]
        else:
            a, c, fc = c, d, fd
            d = a + phi * (b - a)
            fd = evaluate(d)[0]
    h_star = 0.5 * (a + b)
    g_star, result = evaluate(h_star)
    return h_star, g_star, result


def analyze_slice(J, Delta, sizes, h_range, tol, maxiter, omega=1.0):
    row = {"Delta": Delta, "J": J, "N_values": {}}
    for N in sizes:
        h_star, g_star, result = locate_minimum(
            J, Delta, N, *h_range, tol, maxiter, omega=omega)
        row["N_values"][str(N)] = {
            "h_c": h_star, "g_c": g_star,
            "phi_c": h_star / (4.0 * g_star),
            "e_spin": result["energy_per_site"],
            "residual": result["residual"]}
    infinite = (math.sqrt(-3.0 * omega * J / 2.0)
                if Delta >= -2.0 * J else None)
    row["koziol_tricritical_anchor"] = infinite
    row["local_threshold_T0"] = math.sqrt(
        omega * (Delta - 4.0 * J) / 4.0)
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, nargs="+", required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--N", type=int, nargs="+", default=[14, 16, 18])
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--maxiter", type=int, default=160)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.omega <= 0:
        parser.error("require omega>0")
    start = time.perf_counter()
    # default h-ranges (Delta -> (lo, hi)); the minimum retreats to h->0 at
    # the tricritical ratio
    defaults = {0.15: (0.3, 0.95), 0.2: (0.3, 0.95), 0.25: (0.2, 0.9),
                0.3: (0.1, 0.8), 0.35: (0.05, 0.6), 0.38: (0.03, 0.45),
                0.4: (0.01, 0.3)}
    values = []
    for Delta in args.Delta:
        h_range = defaults.get(Delta)
        if h_range is None:
            raise ValueError(f"no default h-range for Delta={Delta}")
        values.append(analyze_slice(args.J, Delta, args.N, h_range,
                                    args.tol, args.maxiter,
                                    omega=args.omega))
    parameters = {key: (str(value) if isinstance(value, Path) else value)
                  for key, value in vars(args).items()}
    payload = json.dumps({"parameters": parameters, "seed": None,
                          "elapsed_seconds": time.perf_counter() - start,
                          "sources_sha256": {
                              "ft_tc_zero_t_line.py": _sha256(__file__)},
                          "values": values}, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
