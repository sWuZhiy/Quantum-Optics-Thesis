"""Targeted validation of the narrow re-entrant FT-TC candidate pocket.

For each supplied ``Delta`` with two sign-changing ``a4(T)`` roots, this
driver chooses one temperature below the lower root, the temperature where
``a4`` is most negative between the roots, and one temperature above the
upper root.  It then records:

* exact infinite-chain ``a2``/``a4`` and finite-ring ``a6`` convergence;
* the sixth-order Landau prediction for the finite-field minimum inside the
  pocket;
* optional direct ED/NLCE/transfer estimates at that predicted field;
* an optional coarse finite-ring scan for additional, remote minima over the
  rigorous bounded field interval.

The key output is an error-budget preflight.  A local Landau signal smaller
than the disagreement of the direct methods is reported as unresolved, not
as a confirmed global first-order pocket.  Conversely, a coarse remote scan
cannot rule out arbitrarily narrow unsampled minima.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from ft_tc_ed import free_energy as periodic_free_energy
from ft_tc_global_stationary import (nlce_check, scan_minima,
                                     transfer_check)
from ft_tc_landau_paths import landau_coefficients
from ft_tc_quartic import infinite_chain
from ft_tc_thermal_threshold import equal_coupling
from ft_tc_trajectory import find_a4_roots, minimize_a4


def _sha256(path):
    with open(path, "rb") as stream:
        return hashlib.sha256(stream.read()).hexdigest()


def choose_outside_probes(lower_root, upper_root, temperature_floor,
                          temperature_ceiling, minimum_offset=0.003,
                          gap_fraction=0.2):
    """Choose temperatures just outside a two-root interval."""
    if not temperature_floor < lower_root < upper_root < temperature_ceiling:
        raise ValueError("roots must lie strictly inside the temperature range")
    gap = upper_root - lower_root
    offset = max(minimum_offset, gap_fraction * gap)
    below = max(temperature_floor, lower_root - offset)
    above = min(temperature_ceiling, upper_root + offset)
    if below >= lower_root or above <= upper_root:
        raise ValueError("temperature range leaves no room for outside probes")
    return below, above


def _local_coefficients(T, J, Delta, omega):
    values = infinite_chain(T, J, Delta)
    a2 = float(values["a2"])
    a4 = float(values["a4"])
    return {"T": T, "a2": a2, "a4": a4,
            "g_local": math.sqrt(-omega / (16.0 * a2))}


def _landau_signal(T, J, Delta, omega, sizes):
    record = _local_coefficients(T, J, Delta, omega)
    a6_by_N = {str(N): float(landau_coefficients(
        T, J, Delta, N, 6)["a6"]) for N in sizes}
    a6 = a6_by_N[str(sizes[-1])]
    record["a6_by_N"] = a6_by_N
    record["a6_last"] = a6
    record["a6_last_size_change"] = (
        abs(a6_by_N[str(sizes[-1])] - a6_by_N[str(sizes[-2])])
        if len(sizes) >= 2 else None)
    if record["a4"] >= 0 or a6 <= 0:
        record["landau_status"] = "no_stable_finite_field_minimum_at_sixth_order"
        return record
    h_star = math.sqrt(-record["a4"] / (2.0 * a6))
    depth = (record["g_local"] * record["a4"] ** 2
             / (8.0 * a6 * abs(record["a2"])))
    denominator = -record["a2"] - record["a4"] * h_star ** 2 - a6 * h_star ** 4
    g_sixth = math.sqrt(omega / (16.0 * denominator))
    record.update({
        "landau_status": "stable_local_finite_field_minimum",
        "predicted_h_star": h_star,
        "predicted_depth_below_g_local": depth,
        "g_equal_sixth_order_at_h_star": g_sixth,
        "sixth_order_depth_below_g_local": record["g_local"] - g_sixth,
    })
    return record


def _direct_crosscheck(T, J, Delta, omega, h, ed_sizes, nlce_orders,
                       transfer_slices):
    ed = {}
    for N in ed_sizes:
        normal = periodic_free_energy(T, J, Delta, 0.0, N)
        finite = periodic_free_energy(T, J, Delta, h, N)
        ed[str(N)] = equal_coupling(omega, h, normal, finite)
    nlce = nlce_check(T, J, Delta, omega, h, nlce_orders)
    transfer = transfer_check(T, J, Delta, omega, h, transfer_slices)
    representatives = [ed[str(ed_sizes[-1])], nlce["g_equal_aitken"],
                       transfer["extrap_last3"]]
    diagnostics = {
        "ed_largest_minus_previous": (
            ed[str(ed_sizes[-1])] - ed[str(ed_sizes[-2])]
            if len(ed_sizes) >= 2 else None),
        "nlce_aitken_minus_ed_largest": (
            nlce["g_equal_aitken"] - ed[str(ed_sizes[-1])]),
        "transfer_last3_minus_ed_largest": (
            transfer["extrap_last3"] - ed[str(ed_sizes[-1])]),
        "transfer_window_spread": transfer["window_spread"],
        "representative_span": max(representatives) - min(representatives),
    }
    all_method_resolution = max(
        abs(value) for value in diagnostics.values() if value is not None)
    ed_nlce_resolution = max(
        abs(diagnostics["ed_largest_minus_previous"] or 0.0),
        abs(diagnostics["nlce_aitken_minus_ed_largest"]))
    return {"h": h, "ed_g_equal": ed, "nlce": nlce,
            "transfer": transfer, "error_diagnostics": diagnostics,
            "ed_nlce_empirical_resolution": ed_nlce_resolution,
            "all_method_empirical_resolution": all_method_resolution,
            # Backward-compatible alias: the conservative all-method value.
            "empirical_resolution": all_method_resolution}


def classify_resolution(predicted_depth, empirical_resolution):
    """Classify whether a predicted depth exceeds an empirical method spread."""
    if predicted_depth <= 0 or empirical_resolution < 0:
        raise ValueError("depth must be positive and resolution non-negative")
    if empirical_resolution == 0:
        return "resolved_by_reported_method_spread", math.inf
    ratio = predicted_depth / empirical_resolution
    if ratio >= 10.0:
        status = "resolved_by_reported_method_spread"
    elif ratio >= 1.0:
        status = "marginal_against_reported_method_spread"
    else:
        status = "below_reported_method_spread"
    return status, ratio


def _remote_scan(T, J, Delta, omega, h_min, points, N):
    local = _local_coefficients(T, J, Delta, omega)
    h_max = 8.0 * local["g_local"] ** 2 / omega
    h_grid, g_grid, brackets = scan_minima(
        T, J, Delta, omega, h_min, h_max, points, N)
    return {
        "N": N,
        "h_min": h_min,
        "h_max": h_max,
        "points": points,
        "scan_min_h": float(h_grid[int(g_grid.argmin())]),
        "scan_min_g_equal": float(g_grid.min()),
        "scan_min_minus_g_local": float(g_grid.min() - local["g_local"]),
        "interior_brackets": [
            {"h_lower": lo, "h_upper": hi, "scan_g_equal": value}
            for lo, hi, value in brackets],
    }


def enrich_row(row, direct, remote):
    """Add optional expensive checks to an existing preflight row."""
    if row.get("status") != "two_root_slice_analyzed":
        return row
    J = row["J"]
    Delta = row["Delta"]
    omega = row["omega"]
    probes = row["probes"]
    if remote is not None:
        for probe in probes.values():
            probe["remote_scan"] = _remote_scan(
                probe["T"], J, Delta, omega, remote["h_min"],
                remote["points"], remote["N"])
    inside = probes["inside_at_minimum_a4"]
    if direct is not None and inside.get("predicted_h_star") is not None:
        crosscheck = _direct_crosscheck(
            inside["T"], J, Delta, omega, inside["predicted_h_star"],
            direct["ed_sizes"], direct["nlce_orders"],
            direct["transfer_slices"])
        all_status, all_ratio = classify_resolution(
            inside["predicted_depth_below_g_local"],
            crosscheck["all_method_empirical_resolution"])
        ed_nlce_status, ed_nlce_ratio = classify_resolution(
            inside["predicted_depth_below_g_local"],
            crosscheck["ed_nlce_empirical_resolution"])
        crosscheck["all_method_signal_to_resolution_ratio"] = all_ratio
        crosscheck["all_method_resolution_status"] = all_status
        crosscheck["ed_nlce_signal_to_resolution_ratio"] = ed_nlce_ratio
        crosscheck["ed_nlce_resolution_status"] = ed_nlce_status
        # Backward-compatible aliases retain the conservative interpretation.
        crosscheck["signal_to_resolution_ratio"] = all_ratio
        crosscheck["resolution_status"] = all_status
        if (ed_nlce_status == "resolved_by_reported_method_spread"
                and all_status != "resolved_by_reported_method_spread"):
            crosscheck["combined_status"] = (
                "resolved_by_ed_nlce_but_transfer_extrapolation_unresolved")
        elif all_status == "resolved_by_reported_method_spread":
            crosscheck["combined_status"] = "resolved_by_all_reported_methods"
        else:
            crosscheck["combined_status"] = (
                "not_resolved_by_current_direct_method_spreads")
        inside["direct_crosscheck"] = crosscheck
    return row


def analyze_delta(J, Delta, omega, temperature_range, root_points,
                  temperature_floor, minimum_offset, gap_fraction, a6_sizes,
                  direct, remote):
    roots = find_a4_roots(
        J, Delta, *temperature_range, points=root_points)
    row = {"J": J, "Delta": Delta, "omega": omega,
           "roots": roots}
    if len(roots) != 2:
        row["status"] = "requires_exactly_two_sign_changing_roots"
        return row
    lower, upper = roots
    below, above = choose_outside_probes(
        lower, upper, temperature_floor, temperature_range[1],
        minimum_offset=minimum_offset, gap_fraction=gap_fraction)
    middle, minimum_a4 = minimize_a4(J, Delta, lower, upper)
    probes = {
        "below_lower_root": _local_coefficients(below, J, Delta, omega),
        "inside_at_minimum_a4": _landau_signal(
            middle, J, Delta, omega, a6_sizes),
        "above_upper_root": _local_coefficients(above, J, Delta, omega),
    }
    probes["inside_at_minimum_a4"]["minimum_a4_check"] = minimum_a4
    row.update({"status": "two_root_slice_analyzed",
                "probe_temperatures": {key: value["T"]
                                       for key, value in probes.items()},
                "probes": probes})
    return enrich_row(row, direct, remote)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, nargs="+", required=True)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--T-range", type=float, nargs=2,
                        default=[0.08, 0.18])
    parser.add_argument("--root-points", type=int, default=501)
    parser.add_argument("--temperature-floor", type=float, default=0.1)
    parser.add_argument("--minimum-offset", type=float, default=0.003)
    parser.add_argument("--gap-fraction", type=float, default=0.2)
    parser.add_argument("--a6-N", type=int, nargs="+", default=[8, 10, 12])
    parser.add_argument("--direct-crosscheck", action="store_true")
    parser.add_argument("--remote-scan", action="store_true")
    parser.add_argument("--remote-scan-n", type=int, default=8)
    parser.add_argument("--remote-h-min", type=float, default=0.03)
    parser.add_argument("--remote-points", type=int, default=160)
    parser.add_argument("--reuse-preflight", type=Path, default=None,
                        help="reuse roots/a6 from an earlier preflight JSON")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if args.omega <= 0 or args.root_points < 3:
        parser.error("require omega>0 and root-points>=3")
    if sorted(args.a6_N) != args.a6_N or min(args.a6_N) < 2:
        parser.error("a6-N must be sorted positive ring sizes")

    direct = None
    if args.direct_crosscheck:
        direct = {"ed_sizes": [8, 10, 12],
                  "nlce_orders": [10, 11, 12],
                  "transfer_slices": [12, 16, 18, 20]}
    remote = None
    if args.remote_scan:
        remote = {"N": args.remote_scan_n, "h_min": args.remote_h_min,
                  "points": args.remote_points}

    started = time.perf_counter()
    if args.reuse_preflight is None:
        values = [analyze_delta(
            args.J, Delta, args.omega, args.T_range, args.root_points,
            args.temperature_floor, args.minimum_offset, args.gap_fraction,
            args.a6_N, direct, remote) for Delta in args.Delta]
    else:
        previous = json.loads(args.reuse_preflight.read_text(encoding="utf-8"))
        values = []
        for Delta in args.Delta:
            matches = [row for row in previous["values"]
                       if abs(float(row["Delta"]) - Delta) < 1e-12]
            if len(matches) != 1:
                raise ValueError(
                    f"reuse preflight has {len(matches)} rows for Delta={Delta}")
            row = copy.deepcopy(matches[0])
            if abs(float(row["J"]) - args.J) > 1e-12:
                raise ValueError("reuse preflight J does not match")
            if abs(float(row["omega"]) - args.omega) > 1e-12:
                raise ValueError("reuse preflight omega does not match")
            values.append(enrich_row(row, direct, remote))
    parameters = vars(args).copy()
    parameters["output"] = None if args.output is None else str(args.output)
    parameters["reuse_preflight"] = (None if args.reuse_preflight is None
                                      else str(args.reuse_preflight))
    source_dir = Path(__file__).parent
    payload = json.dumps({
        "parameters": parameters,
        "seed": None,
        "elapsed_seconds": time.perf_counter() - started,
        "sources_sha256": {
            "ft_tc_reentrant_validate.py": _sha256(__file__),
            "ft_tc_global_stationary.py": _sha256(
                source_dir / "ft_tc_global_stationary.py"),
            "ft_tc_ed.py": _sha256(source_dir / "ft_tc_ed.py"),
            "ft_tc_nlce.py": _sha256(source_dir / "ft_tc_nlce.py"),
            "ft_tc_thermal_threshold.py": _sha256(
                source_dir / "ft_tc_thermal_threshold.py"),
            "ft_tc_transfer.py": _sha256(source_dir / "ft_tc_transfer.py"),
            "ft_tc_trajectory.py": _sha256(source_dir / "ft_tc_trajectory.py"),
            "ft_tc_quartic.py": _sha256(source_dir / "ft_tc_quartic.py"),
            "ft_tc_landau_paths.py": _sha256(
                source_dir / "ft_tc_landau_paths.py"),
        },
        "values": values,
    }, indent=2)
    if args.output is None:
        print(payload)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print(args.output)


if __name__ == "__main__":
    main()
