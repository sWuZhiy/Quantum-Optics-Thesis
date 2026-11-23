"""Validate and summarize the returned FT-TC N=14 dense-ED archive.

The archive is treated as external raw data: no contained code is executed.
Each result's recorded source/input hashes are checked against both archive
entries and the current project tree before finite-size and cross-method
resolution diagnostics are computed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile


SOURCE_SUFFIXES = {
    "ft_tc_32gb_reentrant_ed.py": "code/src/ft_tc_32gb_reentrant_ed.py",
    "ft_tc_ed.py": "code/src/ft_tc_ed.py",
    "ft_tc_thermal_threshold.py": "code/src/ft_tc_thermal_threshold.py",
    "preflight_json": (
        "results/runs/2026-11-23-ft-tc-reentrant/reentrant-preflight.json"),
    "direct_reference_json": (
        "results/runs/2026-11-23-ft-tc-reentrant/direct-crosscheck-all.json"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _one_entry_ending(entries: list[str], suffix: str) -> str:
    matches = [name for name in entries if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"archive has {len(matches)} entries ending in {suffix}")
    return matches[0]


def classify_result(payload: dict) -> dict:
    """Apply the same empirical ED+NLCE resolution rule to an N=14 result."""
    depth = float(payload["values"]["observed_depth_below_g_local"])
    differences = payload["finite_size_differences"]
    N = int(payload["parameters"]["N"])
    finite_size_change = abs(float(differences[f"N{N}_minus_N12"]))
    nlce_difference = abs(float(differences[f"N{N}_minus_NLCE_Aitken"]))
    resolution = max(finite_size_change, nlce_difference)
    ratio = depth / resolution if resolution else float("inf")
    if depth <= 0:
        status = "unresolved_sign_flip_or_no_finite_field_advantage"
    elif ratio >= 10:
        status = "resolved_by_n14_and_nlce_spread"
    elif ratio >= 1:
        status = "marginal_against_n14_and_nlce_spread"
    else:
        status = "below_n14_and_nlce_spread"
    reference = payload.get("existing_reference") or {}
    return {
        "Delta": float(payload["parameters"]["Delta"]),
        "T": float(payload["parameters"]["T"]),
        "h": float(payload["parameters"]["h"]),
        "N": N,
        "g_local": float(payload["parameters"]["g_local"]),
        "g_equal_N14": float(payload["values"]["g_equal"]),
        "observed_depth_below_g_local": depth,
        "predicted_depth_below_g_local": float(
            payload["parameters"]["predicted_depth_below_g_local"]),
        "observed_to_predicted_depth_ratio": float(
            payload["values"]["observed_to_sixth_order_depth_ratio"]),
        "existing_ed_g_equal": reference.get("ed_g_equal"),
        "existing_nlce_g_equal_aitken": reference.get("nlce_g_equal_aitken"),
        "N14_minus_N12": float(differences[f"N{N}_minus_N12"]),
        "N14_minus_NLCE_Aitken": float(
            differences[f"N{N}_minus_NLCE_Aitken"]),
        "finite_size_change_abs": finite_size_change,
        "nlce_difference_abs": nlce_difference,
        "empirical_resolution": resolution,
        "signal_to_resolution_ratio": ratio,
        "resolution_status": status,
        "elapsed_seconds": float(payload["runtime"]["elapsed_seconds"]),
        "peak_process_memory_gib": payload["runtime"][
            "peak_process_memory_gib"],
        "runtime_python": payload["runtime"]["python"].splitlines()[0],
        "runtime_numpy": payload["runtime"]["numpy"],
        "runtime_platform": payload["runtime"]["platform"],
        "runtime_threads": payload["runtime"]["thread_environment"],
    }


def analyze_archive(archive_path: Path, project_root: Path) -> dict:
    raw_bytes = archive_path.read_bytes()
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.namelist()
        result_names = sorted(
            name for name in entries
            if Path(name).name.startswith("ed-N14-Delta")
            and name.endswith(".json"))
        if len(result_names) != 3:
            raise ValueError(f"expected 3 N=14 result JSONs, found {len(result_names)}")
        payloads = [json.loads(archive.read(name)) for name in result_names]
        if any(payload.get("status") != "complete" for payload in payloads):
            raise ValueError("at least one returned result is not complete")

        source_validation = []
        for result_name, payload in zip(result_names, payloads):
            for source_key, expected in payload["sources_sha256"].items():
                suffix = SOURCE_SUFFIXES[source_key]
                entry_name = _one_entry_ending(entries, suffix)
                archive_hash = sha256_bytes(archive.read(entry_name))
                local_path = project_root / suffix
                local_hash = sha256_file(local_path)
                source_validation.append({
                    "result": Path(result_name).name,
                    "source": source_key,
                    "expected": expected,
                    "archive_hash": archive_hash,
                    "local_hash": local_hash,
                    "archive_match": archive_hash == expected,
                    "local_match": local_hash == expected,
                })

        environment_name = _one_entry_ending(
            entries, "code/environment-32gb.yml")
        environment_text = archive.read(environment_name).decode("utf-8")
        match = re.search(r"python\s*=\s*([0-9]+\.[0-9]+)", environment_text)
        requested_python = match.group(1) if match else None
        runtime_versions = sorted({
            payload["runtime"]["python"].split()[0] for payload in payloads})
        environment_match = (
            requested_python is None
            or all(version.startswith(requested_python + ".")
                   for version in runtime_versions))

    all_hashes_match = all(
        row["archive_match"] and row["local_match"]
        for row in source_validation)
    if not all_hashes_match:
        raise ValueError("returned source/input hash validation failed")
    rows = sorted((classify_result(payload) for payload in payloads),
                  key=lambda row: row["Delta"])
    return {
        "processor_sha256": sha256_file(Path(__file__)),
        "raw_archive": str(archive_path),
        "raw_archive_sha256": sha256_bytes(raw_bytes),
        "seed": None,
        "source_validation": source_validation,
        "all_source_and_input_hashes_match_archive_and_local": all_hashes_match,
        "environment_validation": {
            "requested_python_major_minor": requested_python,
            "runtime_python_versions": runtime_versions,
            "python_environment_match": environment_match,
            "interpretation": (
                "runtime_deviates_from_handoff_environment; preserve as a "
                "reproducibility caveat, but source and input hashes match"
                if not environment_match else "runtime matches handoff environment"),
        },
        "values": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--project-root", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = analyze_archive(args.archive.resolve(), args.project_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
