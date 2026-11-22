"""Zero-temperature analytic checks for the equilibrium Dicke--Ising baseline.

Units: hbar = k_B = 1, s = sigma/2. The spin-chain Hamiltonian is
H_s = J sum sigma_z[i] sigma_z[i+1] + Delta/2 sum sigma_z[i]
      + h/2 sum sigma_x[i], with h=4*g*phi and omega>0.

The Delta=0 ferromagnetic chain is an integrable transverse-field Ising
chain. This module computes its infinite-chain energy by momentum quadrature
and minimizes the normal/side-branch degeneracy coupling. For Delta>0, the
quadratic and quartic coefficients map Koziol (2026), Eqs. (10)--(14), to
the project convention; they are a local expansion, not a global phase test.
"""

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np


def zero_field_tfim_energy(J, h, momenta=32768):
    """Infinite-chain ground-state energy density at Delta=0, J<0."""
    if J >= 0 or momenta < 16:
        raise ValueError("require ferromagnetic J<0 and momenta>=16")
    if h == 0:
        return float(J)
    K = -J
    x = abs(h) / (2 * K)
    k = (np.arange(momenta) + 0.5) * math.pi / momenta
    dispersion = np.sqrt((x - 1) ** 2 + 4 * x * np.sin(k / 2) ** 2)
    return -K * float(np.mean(dispersion))


def zero_field_crossing(J, omega, momenta=32768, scan_points=801):
    """Minimize g(h) where a finite-field branch equals the normal state.

    The numerical search spans x=h/(2|J|) in [0.05, 8]. A coarse scan locates
    the minimum, then its stationary equation is solved by bisection. The
    returned scan and quadrature checks make the finite search domain explicit.
    """
    if J >= 0 or omega <= 0 or momenta < 16 or scan_points < 3:
        raise ValueError("require J<0, omega>0, momenta>=16, scan_points>=3")
    K = -J
    k = (np.arange(momenta) + 0.5) * math.pi / momenta
    sin_squared = np.sin(k / 2) ** 2

    def crossing_at_x(x):
        mean_dispersion = float(np.mean(np.sqrt((x - 1) ** 2 + 4 * x * sin_squared)))
        return math.sqrt(omega * K * x * x / (4 * (mean_dispersion - 1)))

    def crossing_stationarity(x):
        dispersion = np.sqrt((x - 1) ** 2 + 4 * x * sin_squared)
        mean_dispersion = float(np.mean(dispersion))
        mean_derivative = float(np.mean((x - 1 + 2 * sin_squared) / dispersion))
        return 2 * (mean_dispersion - 1) - x * mean_derivative

    xs = np.linspace(0.05, 8.0, scan_points)
    gs = [crossing_at_x(float(x)) for x in xs]
    i = int(np.argmin(gs))
    if i == 0 or i == len(xs) - 1:
        raise RuntimeError("crossing minimum reached search boundary")
    lo, hi = float(xs[i - 1]), float(xs[i + 1])
    if crossing_stationarity(lo) >= 0 or crossing_stationarity(hi) <= 0:
        raise RuntimeError("coarse minimum does not bracket a stationary point")
    for _ in range(80):
        midpoint = (lo + hi) / 2
        if crossing_stationarity(midpoint) < 0:
            lo = midpoint
        else:
            hi = midpoint
    x = (lo + hi) / 2
    g = crossing_at_x(x)
    h = 2 * K * x
    phi = h / (4 * g)
    dispersion = np.sqrt((x - 1) ** 2 + 4 * x * sin_squared)
    e_side = -K * float(np.mean(dispersion))
    # de/dh = -E'(x)/2 with E(x)=mean dispersion and h=2*K*x.
    mean_derivative = float(np.mean((x - 1 + 2 * sin_squared) / dispersion))
    return {"J": J, "omega": omega, "momenta": momenta,
            "scan_points": scan_points, "scan_interval_x": [float(xs[0]), float(xs[-1])],
            "x": x, "h": h, "phi": phi, "g_crossing": g,
            "g_normal_local": math.sqrt(omega * K),
            "normal_energy": J, "side_energy": omega * phi * phi + e_side,
            "energy_residual": omega * phi * phi + e_side - J,
            "stationarity_residual": 2 * omega * phi - 2 * g * mean_derivative,
            "scan_min_index": i}


def ferromagnetic_landau(J, Delta, omega):
    """Koziol's zero-T local coefficients in the project spin convention.

    Returns c2=omega-2*g^2/A and c4=2*g^4*(Delta/2+J)/(A^3*B),
    where A=Delta/2-2*J and B=Delta/2-J. Valid for J<0, Delta>0.
    """
    if J >= 0 or Delta <= 0 or omega <= 0:
        raise ValueError("require J<0, Delta>0, omega>0")
    A = Delta / 2 - 2 * J
    B = Delta / 2 - J
    return {"J": J, "Delta": Delta, "omega": omega, "A": A, "B": B,
            "g_local": math.sqrt(omega * A / 2),
            "c2_of_g": "omega - 2*g**2/A",
            "c4_prefactor_of_g4": 2 * (Delta / 2 + J) / (A**3 * B),
            "tricritical_Delta": -2 * J,
            "tricritical_g": math.sqrt(-1.5 * omega * J),
            "tricritical_c6": 7 * omega**3 / (180 * J**2)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--J", type=float, default=-0.2)
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--Delta", type=float, nargs="*", default=[0.2, 0.4, 0.6])
    parser.add_argument("--momenta", type=int, default=32768)
    parser.add_argument("--scan-points", type=int, default=801)
    args = parser.parse_args()
    start = time.perf_counter()
    result = {"parameters": vars(args), "seed": None,
              "zero_field": zero_field_crossing(args.J, args.omega, args.momenta,
                                                  args.scan_points),
              "landau": [ferromagnetic_landau(args.J, Delta, args.omega)
                         for Delta in args.Delta]}
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["elapsed_seconds"] = time.perf_counter() - start
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
