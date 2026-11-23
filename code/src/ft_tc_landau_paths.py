"""Finite-chain zero-transverse-field Landau coefficients from exact paths.

The matter Hamiltonian is

    H(h) = J sum_i sigma^z_i sigma^z_{i+1}
           + Delta/2 sum_i sigma^z_i + h/2 sum_i sigma^x_i.

At h=0 the Hamiltonian is diagonal.  The Dyson coefficient of order m is a
sum over ordered spin-flip paths which return to the initial z configuration.
For one path with intermediate relative energies d_0=0,...,d_m=0, its
imaginary-time integral is the Hermite divided difference

    F_m(d_0,...,d_m) = (-1)^m [d_0,...,d_m] exp(-beta*x).

Repeated energies are handled with confluent derivatives in Decimal
arithmetic.  This automatically retains the changed intermediate energy when
two neighbouring Ising spins are flipped; no factorisation assumption is
made.  The implementation is intended as a controlled finite-chain benchmark
for m <= 6, not as a proof of the thermodynamic limit.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
from functools import lru_cache
import hashlib
import itertools
import json
import math
from pathlib import Path
import time

import numpy as np


def _sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def classical_data(T: float, J: float, Delta: float, N: int):
    if T <= 0 or N < 3:
        raise ValueError("require T>0 and N>=3")
    states = np.arange(1 << N, dtype=np.int64)
    bits = (states[:, None] >> np.arange(N)) & 1
    z = 1 - 2 * bits
    energy = (J * (z * np.roll(z, -1, axis=1)).sum(axis=1)
              + Delta / 2 * z.sum(axis=1))
    shifted = np.exp(-(energy - energy.min()) / T)
    weights = shifted / shifted.sum()
    return states, energy.astype(float), weights


@lru_cache(maxsize=None)
def _pattern_permutations(pattern: tuple[int, ...]):
    return tuple(sorted(set(itertools.permutations(pattern))))


def returning_sequences(N: int, order: int):
    """Yield ordered site sequences whose parity is even at every site."""
    if order == 2:
        for i in range(N):
            yield (i, i)
        return
    if order == 4:
        for i in range(N):
            yield (i, i, i, i)
        patterns = _pattern_permutations((0, 0, 1, 1))
        for i in range(N):
            for j in range(i + 1, N):
                sites = (i, j)
                for pattern in patterns:
                    yield tuple(sites[label] for label in pattern)
        return
    if order == 6:
        for i in range(N):
            yield (i,) * 6
        patterns_42 = _pattern_permutations((0, 0, 0, 0, 1, 1))
        for i in range(N):
            for j in range(N):
                if i == j:
                    continue
                sites = (i, j)
                for pattern in patterns_42:
                    yield tuple(sites[label] for label in pattern)
        patterns_222 = _pattern_permutations((0, 0, 1, 1, 2, 2))
        for i in range(N):
            for j in range(i + 1, N):
                for k in range(j + 1, N):
                    sites = (i, j, k)
                    for pattern in patterns_222:
                        yield tuple(sites[label] for label in pattern)
        return
    raise ValueError("only orders 2, 4, and 6 are supported")


def _possible_energy_increments(energy: np.ndarray, states: np.ndarray,
                                N: int, max_distinct_sites: int):
    values = [np.zeros_like(energy)]
    for count in range(1, max_distinct_sites + 1):
        for sites in itertools.combinations(range(N), count):
            mask = sum(1 << site for site in sites)
            values.append(energy[states ^ mask] - energy)
    rounded = np.round(np.concatenate(values), 12)
    return np.unique(rounded)


def _encode_rows(nodes: np.ndarray, possible: np.ndarray):
    rounded = np.round(nodes, 12)
    indices = np.searchsorted(possible, rounded)
    if np.any(indices >= possible.size):
        raise RuntimeError("energy-increment lookup overflow")
    if not np.allclose(possible[indices], rounded, atol=5e-12, rtol=0):
        raise RuntimeError("energy increment missing from lookup")
    indices.sort(axis=1)
    base = int(possible.size)
    powers = np.array([base ** k for k in range(nodes.shape[1])], dtype=np.int64)
    return indices.astype(np.int64) @ powers


def _decode_key(key: int, possible: np.ndarray, length: int):
    base = int(possible.size)
    values = []
    for _ in range(length):
        key, remainder = divmod(int(key), base)
        values.append(float(possible[remainder]))
    return tuple(values)


def confluent_simplex(beta: float, nodes: tuple[float, ...], precision: int = 60):
    """Return (-1)^m exp(-beta*x)[nodes] with repeated-node support."""
    with localcontext() as context:
        context.prec = precision
        b = Decimal(str(beta))
        z = sorted(Decimal(str(value)) for value in nodes)
        size = len(z)
        table = [[Decimal(0)] * size for _ in range(size)]
        for i, value in enumerate(z):
            table[i][0] = (-b * value).exp()
        for degree in range(1, size):
            factorial = Decimal(math.factorial(degree))
            for i in range(degree, size):
                if z[i] == z[i - degree]:
                    table[i][degree] = ((-b) ** degree
                                        * (-b * z[i]).exp() / factorial)
                else:
                    table[i][degree] = ((table[i][degree - 1]
                                         - table[i - 1][degree - 1])
                                        / (z[i] - z[i - degree]))
        sign = Decimal(-1) ** (size - 1)
        return float(sign * table[-1][-1])


def partition_coefficient(T: float, J: float, Delta: float, N: int,
                          order: int, batch_size: int = 64):
    states, energy, weights = classical_data(T, J, Delta, N)
    dimension = states.size
    possible = _possible_energy_increments(energy, states, N, order // 2)
    amplitude_cache: dict[int, float] = {}
    path_sum = np.zeros(dimension, dtype=float)
    sequence_count = 0
    beta = 1.0 / T
    batch: list[tuple[int, ...]] = []

    def consume(sequences):
        nonlocal sequence_count
        count = len(sequences)
        nodes = np.zeros((count, dimension, order + 1), dtype=float)
        for row, sequence in enumerate(sequences):
            current = states.copy()
            for step, site in enumerate(sequence[:-1], start=1):
                current ^= 1 << site
                nodes[row, :, step] = energy[current] - energy
        flat = nodes.reshape(-1, order + 1)
        keys = _encode_rows(flat, possible)
        unique = np.unique(keys)
        for key in unique:
            key_int = int(key)
            if key_int not in amplitude_cache:
                decoded = _decode_key(key_int, possible, order + 1)
                amplitude_cache[key_int] = confluent_simplex(beta, decoded)
        amplitudes = np.fromiter((amplitude_cache[int(key)] for key in keys),
                                 dtype=float, count=keys.size)
        path_sum[:] += amplitudes.reshape(count, dimension).sum(axis=0)
        sequence_count += count

    for sequence in returning_sequences(N, order):
        batch.append(sequence)
        if len(batch) >= batch_size:
            consume(batch)
            batch.clear()
    if batch:
        consume(batch)

    coefficient = float(weights @ path_sum) / (2 ** order)
    return {
        "order": order,
        "Z_order_over_Z0": coefficient,
        "sequence_count": sequence_count,
        "simplex_cache_size": len(amplitude_cache),
        "energy_increment_count": int(possible.size),
    }


def landau_coefficients(T: float, J: float, Delta: float, N: int,
                        max_order: int = 6, batch_size: int = 64):
    if max_order not in (2, 4, 6):
        raise ValueError("max_order must be 2, 4, or 6")
    rows = {}
    for order in (2, 4, 6):
        if order > max_order:
            break
        rows[order] = partition_coefficient(T, J, Delta, N, order, batch_size)
    z2 = rows[2]["Z_order_over_Z0"]
    result = {"T": T, "J": J, "Delta": Delta, "N": N,
              "max_order": max_order, "Z2Z0": z2,
              "a2": -(T / N) * z2, "paths": rows}
    if max_order >= 4:
        z4 = rows[4]["Z_order_over_Z0"]
        result.update({"Z4Z0": z4,
                       "a4": -(T / N) * (z4 - z2 * z2 / 2)})
    if max_order >= 6:
        z6 = rows[6]["Z_order_over_Z0"]
        z4 = rows[4]["Z_order_over_Z0"]
        result.update({"Z6Z0": z6,
                       "a6": -(T / N) * (z6 - z2 * z4 + z2 ** 3 / 3)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--T", type=float, nargs="+", required=True)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--N", type=int, nargs="+", default=[6, 8, 10])
    parser.add_argument("--max-order", type=int, choices=[2, 4, 6], default=6)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--output", type=Path, default=None,
                        help="optional JSON output path; stdout is used otherwise")
    args = parser.parse_args()
    start = time.perf_counter()
    values = []
    for temperature in args.T:
        for size in args.N:
            values.append(landau_coefficients(
                temperature, args.J, args.Delta, size,
                max_order=args.max_order, batch_size=args.batch_size))
    output_path = args.output
    parameters = vars(args).copy()
    parameters["output"] = None if output_path is None else str(output_path)
    payload = json.dumps({"parameters": parameters, "seed": None,
                          "elapsed_seconds": time.perf_counter() - start,
                          "sources_sha256": {
                              "ft_tc_landau_paths.py": _sha256(__file__)},
                          "values": values}, indent=2)
    if output_path is None:
        print(payload)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
        print(output_path)


if __name__ == "__main__":
    main()
