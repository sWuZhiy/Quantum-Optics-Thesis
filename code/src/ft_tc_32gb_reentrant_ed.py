"""Run the scientifically useful 32-GiB FT-TC dense-ED extension.

The current re-entrant-pocket evidence uses periodic thermal ED through N=12.
This driver evaluates the same pre-registered small-field probes at N=14, one
Delta at a time, and writes one resumable JSON file per slice.  N=14 has a
2-GiB float64 Hamiltonian before LAPACK work arrays and is therefore a useful
32-GiB-machine job.  The script refuses N>14 and performs a physical-memory
preflight to reduce the chance of paging or an out-of-memory crash.

It does not claim that a larger finite ring is a thermodynamic-limit proof.
"""

from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time


GIB = 1024 ** 3


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dense_ed_memory_estimate(N: int) -> dict:
    """Return transparent raw/heuristic memory estimates for dense float64 ED."""
    if N < 3 or N > 14:
        raise ValueError("the 32-GiB handoff supports 3 <= N <= 14")
    dimension = 1 << N
    matrix_bytes = dimension * dimension * 8
    # H, a possible LAPACK copy/eigenvector workspace, and temporary work arrays.
    # This is a planning heuristic rather than a guaranteed peak bound.
    estimated_peak_bytes = 5 * matrix_bytes
    return {
        "N": N,
        "hilbert_dimension": dimension,
        "dense_matrix_bytes": matrix_bytes,
        "dense_matrix_gib": matrix_bytes / GIB,
        "estimated_peak_bytes": estimated_peak_bytes,
        "estimated_peak_gib": estimated_peak_bytes / GIB,
        "estimate_kind": "heuristic_5x_dense_float64_matrix_not_a_strict_bound",
    }


def physical_memory() -> dict:
    """Return total/available physical memory using only the standard library."""
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return {"available": False}
        total = int(status.ullTotalPhys)
        available = int(status.ullAvailPhys)
    elif hasattr(os, "sysconf"):
        try:
            page_size = int(os.sysconf("SC_PAGE_SIZE"))
            total = page_size * int(os.sysconf("SC_PHYS_PAGES"))
            available = page_size * int(os.sysconf("SC_AVPHYS_PAGES"))
        except (OSError, ValueError):
            return {"available": False}
    else:
        return {"available": False}
    return {
        "available": True,
        "total_bytes": total,
        "available_bytes": available,
        "total_gib": total / GIB,
        "available_gib": available / GIB,
    }


def peak_process_memory_bytes() -> int | None:
    """Best-effort peak resident memory for the completed process."""
    if os.name == "nt":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            kernel32.GetCurrentProcess.restype = ctypes.c_void_p
            psapi.GetProcessMemoryInfo.argtypes = [
                ctypes.c_void_p,
                ctypes.POINTER(ProcessMemoryCounters),
                ctypes.c_ulong,
            ]
            psapi.GetProcessMemoryInfo.restype = ctypes.c_int
            handle = kernel32.GetCurrentProcess()
            ok = psapi.GetProcessMemoryInfo(
                handle, ctypes.byref(counters), counters.cb)
            return int(counters.PeakWorkingSetSize) if ok else None
        except OSError:
            return None
    try:
        import resource
        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return value if sys.platform == "darwin" else value * 1024
    except (ImportError, ValueError):
        return None


def select_preflight_case(payload: dict, Delta: float) -> dict:
    """Extract the pre-registered T, h*, and local threshold for one Delta."""
    matches = [row for row in payload["values"]
               if abs(float(row["Delta"]) - Delta) < 1e-12]
    if len(matches) != 1:
        raise ValueError(f"preflight has {len(matches)} rows for Delta={Delta}")
    row = matches[0]
    if row.get("status") != "two_root_slice_analyzed":
        raise ValueError(f"Delta={Delta} is not a completed two-root slice")
    inside = row["probes"]["inside_at_minimum_a4"]
    if inside.get("predicted_h_star") is None:
        raise ValueError(f"Delta={Delta} has no stable sixth-order h* probe")
    return {
        "J": float(row["J"]),
        "Delta": float(row["Delta"]),
        "omega": float(row["omega"]),
        "T": float(inside["T"]),
        "h": float(inside["predicted_h_star"]),
        "g_local": float(inside["g_local"]),
        "predicted_depth_below_g_local": float(
            inside["predicted_depth_below_g_local"]),
    }


def select_direct_reference(payload: dict | None, Delta: float) -> dict | None:
    if payload is None:
        return None
    matches = [row for row in payload["values"]
               if abs(float(row["Delta"]) - Delta) < 1e-12]
    if len(matches) != 1:
        return None
    direct = (matches[0].get("probes", {})
              .get("inside_at_minimum_a4", {})
              .get("direct_crosscheck"))
    if not direct:
        return None
    return {
        "h": float(direct["h"]),
        "ed_g_equal": {str(key): float(value)
                       for key, value in direct["ed_g_equal"].items()},
        "nlce_g_equal_aitken": float(direct["nlce"]["g_equal_aitken"]),
    }


def output_filename(Delta: float, N: int) -> str:
    return f"ed-N{N}-Delta{Delta:.8g}.json"


def configure_threads(threads: int) -> dict:
    if threads < 1:
        raise ValueError("threads must be positive")
    settings = {
        "OPENBLAS_NUM_THREADS": str(threads),
        "OMP_NUM_THREADS": str(threads),
        "MKL_NUM_THREADS": str(threads),
        "NUMEXPR_NUM_THREADS": str(threads),
    }
    for key, value in settings.items():
        os.environ[key] = value
    return settings


def run_case(case: dict, N: int, memory_plan: dict, thread_settings: dict,
             preflight_path: Path, reference_path: Path | None,
             reference: dict | None, output_path: Path) -> dict:
    # Thread environment is configured before these imports in main().
    import numpy as np
    from ft_tc_ed import free_energy as periodic_free_energy
    from ft_tc_thermal_threshold import equal_coupling

    print(f"Delta={case['Delta']:.8g}, N={N}: building and diagonalizing ",
          f"dimension {1 << N} at h={case['h']:.12g}", flush=True)
    started = time.perf_counter()
    f_normal = periodic_free_energy(
        case["T"], case["J"], case["Delta"], 0.0, N)
    f_finite = periodic_free_energy(
        case["T"], case["J"], case["Delta"], case["h"], N)
    g_equal = equal_coupling(
        case["omega"], case["h"], f_normal, f_finite)
    if g_equal is None:
        raise RuntimeError("finite-field free-energy gain is non-positive")
    elapsed = time.perf_counter() - started
    peak = peak_process_memory_bytes()
    source_dir = Path(__file__).parent
    result = {
        "status": "complete",
        "model": "periodic_mixed_field_ising_thermal_dense_ed",
        "units": "hbar=kB=1",
        "parameters": {**case, "N": N},
        "values": {
            "f_normal_per_site": f_normal,
            "f_finite_field_per_site": f_finite,
            "g_equal": g_equal,
            "g_equal_minus_g_local": g_equal - case["g_local"],
            "observed_depth_below_g_local": case["g_local"] - g_equal,
            "observed_to_sixth_order_depth_ratio": (
                (case["g_local"] - g_equal)
                / case["predicted_depth_below_g_local"]),
        },
        "existing_reference": reference,
        "finite_size_differences": {},
        "memory_preflight": memory_plan,
        "runtime": {
            "elapsed_seconds": elapsed,
            "peak_process_memory_bytes": peak,
            "peak_process_memory_gib": None if peak is None else peak / GIB,
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "thread_environment": thread_settings,
            "seed": None,
        },
        "sources_sha256": {
            "ft_tc_32gb_reentrant_ed.py": _sha256(Path(__file__)),
            "ft_tc_ed.py": _sha256(source_dir / "ft_tc_ed.py"),
            "ft_tc_thermal_threshold.py": _sha256(
                source_dir / "ft_tc_thermal_threshold.py"),
            "preflight_json": _sha256(preflight_path),
        },
    }
    if reference_path is not None and reference_path.exists():
        result["sources_sha256"]["direct_reference_json"] = _sha256(
            reference_path)
    if reference:
        for size, value in reference["ed_g_equal"].items():
            result["finite_size_differences"][f"N{N}_minus_N{size}"] = (
                g_equal - value)
        result["finite_size_differences"][f"N{N}_minus_NLCE_Aitken"] = (
            g_equal - reference["nlce_g_equal_aitken"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"completed {output_path} in {elapsed:.1f} s", flush=True)
    return result


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    default_run = project_root / "results/runs/2026-11-23-ft-tc-reentrant"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path,
                        default=default_run / "reentrant-preflight.json")
    parser.add_argument("--direct-reference", type=Path,
                        default=default_run / "direct-crosscheck-all.json")
    parser.add_argument("--Delta", type=float, nargs="+", default=[0.4001])
    parser.add_argument("--N", type=int, default=14)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--min-available-gib", type=float, default=20.0,
                        help="additional free-memory floor before each case")
    parser.add_argument("--output-dir", type=Path,
                        default=project_root /
                        "results/runs/2026-11-23-ft-tc-32gb-n14")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-memory", action="store_true",
                        help="run despite a failed physical-memory preflight")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.min_available_gib < 0:
        parser.error("min-available-gib must be non-negative")
    try:
        estimate = dense_ed_memory_estimate(args.N)
        thread_settings = configure_threads(args.threads)
    except ValueError as exc:
        parser.error(str(exc))

    preflight_path = args.preflight.resolve()
    if not preflight_path.exists():
        parser.error(f"preflight JSON not found: {preflight_path}")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    reference_path = args.direct_reference.resolve()
    reference_payload = (json.loads(reference_path.read_text(encoding="utf-8"))
                         if reference_path.exists() else None)
    cases = [select_preflight_case(preflight, Delta) for Delta in args.Delta]
    required_gib = max(
        args.min_available_gib, 1.25 * estimate["estimated_peak_gib"])
    plan = {
        "cases": cases,
        "memory_estimate": estimate,
        "required_available_gib": required_gib,
        "physical_memory": physical_memory(),
        "thread_environment": thread_settings,
        "output_dir": str(args.output_dir.resolve()),
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return

    for case in cases:
        output_path = (args.output_dir.resolve()
                       / output_filename(case["Delta"], args.N))
        if output_path.exists() and not args.overwrite:
            try:
                existing = json.loads(output_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                existing = {}
            if existing.get("status") == "complete":
                print(f"skip completed {output_path}", flush=True)
                continue
            raise FileExistsError(
                f"incomplete/unreadable output exists: {output_path}; "
                "use --overwrite after inspecting it")
        memory = physical_memory()
        case_plan = {**estimate, "required_available_gib": required_gib,
                     "physical_memory_before_case": memory}
        if (memory.get("available")
                and memory["available_gib"] < required_gib
                and not args.force_memory):
            raise MemoryError(
                f"only {memory['available_gib']:.2f} GiB physical memory is "
                f"available; require {required_gib:.2f} GiB. Close other "
                "programs or use --force-memory at your own risk.")
        reference = select_direct_reference(
            reference_payload, case["Delta"])
        run_case(case, args.N, case_plan, thread_settings,
                 preflight_path, reference_path, reference, output_path)
        gc.collect()


if __name__ == "__main__":
    main()
