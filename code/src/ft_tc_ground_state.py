"""Matrix-free zero-temperature spin-chain ground-state benchmark.

H_spin(h) = J sum_i sigma_z[i] sigma_z[i+1]
          + Delta/2 sum_i sigma_z[i] + h/2 sum_i sigma_x[i].
The periodic sum has N bonds; the open sum has N-1 bonds. Units are
hbar = k_B = 1. A local z-axis gauge makes the transverse matrix elements
-abs(h)/2 without changing the spectrum, so a uniform positive initial
vector overlaps the unique ground state for h != 0.

The smallest Ritz value is returned only with an explicit residual and
convergence flag. Optional staggered_m2 is
<(sum_i (-1)^i sigma_z[i] / N)^2> for an even periodic chain. At h=0,
degenerate classical ground states are equally weighted (T -> 0 Gibbs limit).
These are finite-chain results, not a thermodynamic limit.
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np


def spin_hamiltonian_data(J, Delta, N, boundary):
    """Return diagonal and bit-flip indices, without allocating a dense H."""
    if N < 2 or N > 18 or (boundary == "periodic" and N < 3):
        raise ValueError("require 2 <= N <= 18, and N >= 3 for a periodic chain")
    if boundary not in ("periodic", "open"):
        raise ValueError("boundary must be 'periodic' or 'open'")
    states = np.arange(1 << N, dtype=np.int64)
    bits = ((states[:, None] >> np.arange(N)) & 1).astype(np.int8)
    z = 1 - 2 * bits
    zz = (z[:, :-1] * z[:, 1:]).sum(axis=1)
    if boundary == "periodic":
        zz += z[:, -1] * z[:, 0]
    diagonal = (J * zz + (Delta / 2) * z.sum(axis=1)).astype(np.float64)
    flips = np.stack([states ^ (1 << i) for i in range(N)])
    return diagonal, flips


def staggered_m2_diagonal(N):
    """Eigenvalues of the squared staggered magnetization in the z basis."""
    states = np.arange(1 << N, dtype=np.int64)
    staggered = np.zeros(len(states), dtype=np.float64)
    for site in range(N):
        staggered += (-1 if site % 2 else 1) * (1 - 2 * ((states >> site) & 1))
    return (staggered / N) ** 2


def ground_state_energy(J, Delta, h, N, boundary="periodic", tol=1e-10,
                        maxiter=160, measure_staggered=False):
    """Lowest finite-chain eigenvalue by fully reorthogonalized Lanczos.

    The residual is ||H q - lambda q||_2, estimated as beta_m times the
    last component of the normalized lowest tridiagonal eigenvector.
    A failed convergence flag means the returned Ritz estimate must not be
    used as a verified ground-state energy. When measurement is requested,
    staggered_m2 is None if Lanczos has not converged.
    """
    if tol <= 0 or maxiter < 2:
        raise ValueError("require tol>0 and maxiter>=2")
    if measure_staggered and (boundary != "periodic" or N % 2):
        raise ValueError("staggered_m2 requires an even periodic chain")
    diagonal, flips = spin_hamiltonian_data(J, Delta, N, boundary)
    dimension = len(diagonal)
    if h == 0:
        energy = float(np.min(diagonal))
        result = {"N": N, "J": J, "Delta": Delta, "h": h, "boundary": boundary,
                  "energy_total": energy, "energy_per_site": energy / N,
                  "iterations": 0, "residual": 0.0, "converged": True,
                  "dimension": dimension, "method": "diagonal"}
        if measure_staggered:
            ground_mask = abs(diagonal - energy) <= 1e-12 * max(1, abs(energy))
            result["staggered_m2"] = float(np.mean(staggered_m2_diagonal(N)[ground_mask]))
            result["observable_method"] = "T_to_zero_Gibbs_average_of_classical_ground_states"
        return result

    basis_rows = min(maxiter, dimension)
    if 8 * dimension * (basis_rows + N) > 1024**3:
        raise ValueError("Lanczos basis and flip indices would exceed 1 GiB")
    basis = np.empty((basis_rows, dimension), dtype=np.float64)
    v = np.full(dimension, 1 / np.sqrt(dimension), dtype=np.float64)
    v_previous = np.zeros_like(v)
    beta_previous = 0.0
    diagonal_T = []
    offdiagonal_T = []
    coupling = -abs(h) / 2
    energy = float("nan")
    residual = float("inf")
    converged = False

    for iteration in range(len(basis)):
        basis[iteration] = v
        w = diagonal * v
        for flip in flips:
            w += coupling * v[flip]
        if iteration:
            w -= beta_previous * v_previous
        alpha = float(np.dot(v, w))
        w -= alpha * v

        # Full reorthogonalization prevents duplicate Ritz values from
        # roundoff. A second pass is useful near degenerate Ising sectors.
        used_basis = basis[:iteration + 1]
        for _ in range(2):
            w -= (used_basis @ w) @ used_basis
        beta = float(np.linalg.norm(w))
        diagonal_T.append(alpha)

        if iteration == 0 or iteration % 5 == 4 or beta < 1e-13 or iteration == len(basis) - 1:
            T = np.diag(diagonal_T)
            if offdiagonal_T:
                off = np.asarray(offdiagonal_T)
                T += np.diag(off, 1) + np.diag(off, -1)
            values, vectors = np.linalg.eigh(T)
            energy = float(values[0])
            residual = beta * abs(float(vectors[-1, 0]))
            if residual <= tol * max(1.0, abs(energy)):
                converged = True
                break
        if beta < 1e-13:
            # Exact Krylov closure: no next Lanczos vector exists.
            break
        v_previous, v = v, w / beta
        beta_previous = beta
        offdiagonal_T.append(beta)

    result = {"N": N, "J": J, "Delta": Delta, "h": h, "boundary": boundary,
              "energy_total": energy, "energy_per_site": energy / N,
              "iterations": iteration + 1, "residual": residual,
              "converged": converged, "dimension": dimension,
              "method": "reorthogonalized_lanczos"}
    if measure_staggered:
        if converged:
            state = vectors[:, 0] @ basis[:iteration + 1]
            probabilities = state * state
            result["staggered_m2"] = float(
                np.dot(probabilities, staggered_m2_diagonal(N))
                / np.sum(probabilities))
            result["observable_method"] = "lowest_Ritz_vector"
        else:
            result["staggered_m2"] = None
            result["observable_method"] = "unavailable_unconverged"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, required=True)
    parser.add_argument("--Delta", type=float, required=True)
    parser.add_argument("--h", type=float, required=True)
    parser.add_argument("--N", type=int, nargs="+", default=[8, 10, 12])
    parser.add_argument("--boundary", choices=["periodic", "open"], default="periodic")
    parser.add_argument("--tol", type=float, default=1e-10)
    parser.add_argument("--maxiter", type=int, default=160)
    parser.add_argument("--staggered-m2", action="store_true")
    args = parser.parse_args()
    start = time.perf_counter()
    values = [ground_state_energy(args.J, args.Delta, args.h, n,
                                  args.boundary, args.tol, args.maxiter,
                                  args.staggered_m2)
              for n in args.N]
    output = {"parameters": vars(args), "seed": None,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "elapsed_seconds": time.perf_counter() - start, "values": values}
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
