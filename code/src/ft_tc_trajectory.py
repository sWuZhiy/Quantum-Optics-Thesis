"""Thermal-tricritical candidate roots and their finite-temperature endpoint.

For fixed ``J`` and ``Delta``, every sign-changing zero of the corrected
infinite-chain fourth-order coefficient ``a4(T)`` is located on a supplied
temperature interval.  This matters close to the zero-temperature
tricritical ratio: just above ``Delta=-2J``, ``a4`` can be positive at zero
temperature, negative at intermediate temperature, and positive again, so
there are *two* roots.  A single hard-coded bracket can silently miss this
re-entrant pocket.

The two roots merge at a tangent endpoint satisfying

    a4(T_endpoint, Delta_endpoint) = 0,
    partial_T a4(T_endpoint, Delta_endpoint) = 0.

The endpoint is found by minimizing ``a4`` over temperature for each Delta,
then bisecting the Delta at which that minimum changes sign.  Optional finite
rings use the corrected exact four-flip expression as an independent
convergence check.  These are local Landau candidates, not proved global
phase boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from ft_tc_landau_paths import landau_coefficients
from ft_tc_quartic import finite_chain, infinite_chain
from ft_tc_transfer import classical_chain, free_energy as transfer_free_energy


def _sha256(path):
    with open(path, "rb") as stream:
        return hashlib.sha256(stream.read()).hexdigest()


def _a4(T, J, Delta, N=None):
    result = (infinite_chain(T, J, Delta) if N is None
              else finite_chain(T, J, Delta, N))
    return float(result["a4"])


def bisect_a4_root(J, Delta, lower, upper, tol=1e-13, max_iter=100, N=None):
    """Bisect one sign-changing a4 root; return None without a bracket."""
    if lower <= 0 or upper <= lower or tol <= 0:
        raise ValueError("require 0 < lower < upper and tol > 0")
    f_lower = _a4(lower, J, Delta, N)
    f_upper = _a4(upper, J, Delta, N)
    if f_lower == 0.0:
        return lower
    if f_upper == 0.0:
        return upper
    if f_lower * f_upper > 0:
        return None
    iterations = 0
    while upper - lower > tol and iterations < max_iter:
        middle = 0.5 * (lower + upper)
        f_middle = _a4(middle, J, Delta, N)
        if f_lower * f_middle <= 0:
            upper, f_upper = middle, f_middle
        else:
            lower, f_lower = middle, f_middle
        iterations += 1
    return 0.5 * (lower + upper)


def find_a4_roots(J, Delta, lower, upper, points=401, tol=1e-13, N=None):
    """Find every sign-changing a4 root visible on a dense T grid."""
    if points < 3:
        raise ValueError("require points>=3")
    temperatures = np.linspace(lower, upper, points)
    values = np.array([_a4(float(T), J, Delta, N) for T in temperatures])
    roots = []
    for index in range(points - 1):
        left, right = float(temperatures[index]), float(temperatures[index + 1])
        f_left, f_right = float(values[index]), float(values[index + 1])
        if f_left == 0.0:
            root = left
        elif f_left * f_right < 0:
            root = bisect_a4_root(J, Delta, left, right, tol=tol, N=N)
        else:
            continue
        if root is not None and (not roots or abs(root - roots[-1]) > 10 * tol):
            roots.append(root)
    if values[-1] == 0.0 and (not roots or abs(upper - roots[-1]) > 10 * tol):
        roots.append(float(upper))
    return roots


def minimize_a4(J, Delta, lower, upper, tol=1e-12, max_iter=100, N=None):
    """Golden-section minimum of a4(T) on one unimodal endpoint bracket."""
    if lower <= 0 or upper <= lower or tol <= 0:
        raise ValueError("require 0 < lower < upper and tol > 0")
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    left, right = lower, upper
    first = right - ratio * (right - left)
    second = left + ratio * (right - left)
    f_first = _a4(first, J, Delta, N)
    f_second = _a4(second, J, Delta, N)
    iterations = 0
    while right - left > tol and iterations < max_iter:
        if f_first <= f_second:
            right, second, f_second = second, first, f_first
            first = right - ratio * (right - left)
            f_first = _a4(first, J, Delta, N)
        else:
            left, first, f_first = first, second, f_second
            second = left + ratio * (right - left)
            f_second = _a4(second, J, Delta, N)
        iterations += 1
    temperature = 0.5 * (left + right)
    return temperature, _a4(temperature, J, Delta, N)


def locate_tangent_endpoint(J, delta_lower, delta_upper,
                            temperature_lower, temperature_upper,
                            delta_tol=1e-12, temperature_tol=1e-12,
                            max_iter=100, N=None):
    """Locate the Delta where min_T a4 changes from negative to positive."""
    low_T, low_value = minimize_a4(
        J, delta_lower, temperature_lower, temperature_upper,
        tol=temperature_tol, N=N)
    high_T, high_value = minimize_a4(
        J, delta_upper, temperature_lower, temperature_upper,
        tol=temperature_tol, N=N)
    if low_value > 0 or high_value < 0:
        raise ValueError("endpoint Delta bracket must straddle min_T a4 = 0")
    iterations = 0
    while delta_upper - delta_lower > delta_tol and iterations < max_iter:
        middle = 0.5 * (delta_lower + delta_upper)
        middle_T, middle_value = minimize_a4(
            J, middle, temperature_lower, temperature_upper,
            tol=temperature_tol, N=N)
        if middle_value <= 0:
            delta_lower, low_T, low_value = middle, middle_T, middle_value
        else:
            delta_upper, high_T, high_value = middle, middle_T, middle_value
        iterations += 1
    Delta = 0.5 * (delta_lower + delta_upper)
    temperature, value = minimize_a4(
        J, Delta, temperature_lower, temperature_upper,
        tol=temperature_tol, N=N)
    return {"N": N, "Delta_endpoint": Delta, "T_endpoint": temperature,
            "a4_at_endpoint": value,
            "Delta_bracket_width": delta_upper - delta_lower,
            "iterations": iterations}


def small_field_sign(T, J, Delta, omega, h):
    """Transfer-matrix estimate of g_equal-g_local (last-three 1/M^2 fit)."""
    normal = classical_chain(T, J, Delta)
    Ms = (12, 16, 18, 20)
    values = []
    for M in Ms:
        f_h = float(transfer_free_energy(T, J, Delta, h, M)["f"])
        gain = normal - f_h
        values.append(math.sqrt(omega * h * h / (16 * gain)))
    inverse = np.array([1.0 / M ** 2 for M in Ms])
    fit = np.polyfit(inverse[-3:], np.array(values)[-3:], 2)
    extrapolated = float(np.polyval(fit, 0.0))
    a2 = float(infinite_chain(T, J, Delta)["a2"])
    g_local = math.sqrt(-omega / (16 * a2))
    return extrapolated - g_local


def _root_record(J, Delta, omega, root, a6_N, crosscheck, probe=None):
    infinite = infinite_chain(root, J, Delta)
    a2 = float(infinite["a2"])
    probe = min(0.01, root / 4.0) if probe is None else probe
    below = _a4(root - probe, J, Delta)
    above = _a4(root + probe, J, Delta)
    if below > 0 and above < 0:
        branch = "continuous_to_first_order_on_heating"
    elif below < 0 and above > 0:
        branch = "first_order_to_continuous_on_heating"
    else:
        branch = "unclassified"
    record = {
        "T_star": root,
        "branch": branch,
        "a4_residual": float(infinite["a4"]),
        "a4_below": below,
        "a4_above": above,
        "probe_dT": probe,
        "a2": a2,
        "g_local": math.sqrt(-omega / (16 * a2)),
    }
    if a6_N > 0:
        record[f"a6_N{a6_N}"] = landau_coefficients(
            root, J, Delta, a6_N, 6)["a6"]
    if crosscheck:
        record["small_field_sign_Tstar"] = small_field_sign(
            root, J, Delta, omega, 0.05)
        record["small_field_sign_below"] = small_field_sign(
            root - probe, J, Delta, omega, 0.05)
        record["small_field_sign_above"] = small_field_sign(
            root + probe, J, Delta, omega, 0.05)
    return record


def analyze_slice(J, Delta, omega, temperature_range, scan_points,
                  a6_N=10, crosscheck=False):
    roots = find_a4_roots(J, Delta, *temperature_range, points=scan_points)
    probes = []
    for index, root in enumerate(roots):
        separations = []
        if index > 0:
            separations.append(root - roots[index - 1])
        if index + 1 < len(roots):
            separations.append(roots[index + 1] - root)
        neighbour_probe = (min(separations) / 4.0 if separations else 0.01)
        probes.append(min(0.01, root / 4.0, neighbour_probe))
    return {"Delta": Delta, "J": J,
            "status": "candidate_roots" if roots else "no_root_in_range",
            "roots": [_root_record(J, Delta, omega, root, a6_N, crosscheck,
                                   probe=probes[index])
                      for index, root in enumerate(roots)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, nargs="+", required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--T-range", type=float, nargs=2, default=[0.08, 0.6])
    parser.add_argument("--scan-points", type=int, default=401)
    parser.add_argument("--a6-N", type=int, default=10,
                        help="finite ring for a6; use 0 to skip")
    parser.add_argument("--crosscheck", action="store_true",
                        help="run expensive transfer-matrix small-field checks")
    parser.add_argument("--endpoint-delta-bracket", type=float, nargs=2)
    parser.add_argument("--endpoint-T-bracket", type=float, nargs=2,
                        default=[0.09, 0.17])
    parser.add_argument("--endpoint-finite-N", type=int, nargs="*", default=[])
    parser.add_argument("--endpoint-a6-N", type=int, nargs="*", default=[])
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.omega <= 0:
        parser.error("require omega>0")

    started = time.perf_counter()
    values = [analyze_slice(args.J, Delta, args.omega, args.T_range,
                            args.scan_points, args.a6_N, args.crosscheck)
              for Delta in args.Delta]
    endpoint = None
    finite_endpoints = []
    endpoint_a6 = {}
    if args.endpoint_delta_bracket is not None:
        endpoint = locate_tangent_endpoint(
            args.J, *args.endpoint_delta_bracket, *args.endpoint_T_bracket)
        for N in args.endpoint_finite_N:
            finite_endpoints.append(locate_tangent_endpoint(
                args.J, *args.endpoint_delta_bracket, *args.endpoint_T_bracket,
                N=N))
        for N in args.endpoint_a6_N:
            endpoint_a6[str(N)] = landau_coefficients(
                endpoint["T_endpoint"], args.J,
                endpoint["Delta_endpoint"], N, 6)["a6"]
        endpoint["g_local"] = math.sqrt(
            -args.omega / (16 * float(infinite_chain(
                endpoint["T_endpoint"], args.J,
                endpoint["Delta_endpoint"])["a2"])))
        endpoint["a6_by_N"] = endpoint_a6

    parameters = vars(args).copy()
    parameters["output"] = None if args.output is None else str(args.output)
    source_dir = Path(__file__).parent
    payload = json.dumps({
        "parameters": parameters,
        "seed": None,
        "elapsed_seconds": time.perf_counter() - started,
        "sources_sha256": {
            "ft_tc_trajectory.py": _sha256(__file__),
            "ft_tc_quartic.py": _sha256(source_dir / "ft_tc_quartic.py"),
            "ft_tc_landau_paths.py": _sha256(source_dir / "ft_tc_landau_paths.py"),
        },
        "values": values,
        "tangent_endpoint_infinite": endpoint,
        "tangent_endpoint_finite_rings": finite_endpoints,
    }, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
