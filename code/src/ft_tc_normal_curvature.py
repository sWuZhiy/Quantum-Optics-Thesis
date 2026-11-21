"""Exact normal-branch curvature for the infinite classical Ising chain.

At h_x=0 the zz/z matter chain is classical. A transverse spin flip at site i
costs dE=-s_i*(Delta+2*J*(s_{i-1}+s_{i+1})); the Kubo integral over its
three-site Gibbs probability gives the exact thermal x susceptibility.
Units: hbar=k_B=1, H_spin=J sum sigma_z sigma_z+Delta/2 sum sigma_z
                       +h_x/2 sum sigma_x.
"""

import argparse
import json
import math

import numpy as np


def normal_curvature(T, J, Delta, omega, g):
    if T <= 0 or omega <= 0 or g < 0:
        raise ValueError("require T>0, omega>0, g>=0")
    beta = 1 / T
    spins = np.array([-1.0, 1.0])
    transfer = np.exp(-beta * (J * spins[:, None] * spins[None, :]
                               + Delta * (spins[:, None] + spins[None, :]) / 4))
    values, vectors = np.linalg.eigh(transfer)
    lam = float(values[-1])
    v = np.abs(vectors[:, -1])
    q = 0.0
    probability_sum = 0.0
    for ia, a in enumerate(spins):
        for ispin, s in enumerate(spins):
            for ib, b in enumerate(spins):
                probability = v[ia] * transfer[ia, ispin] * transfer[ispin, ib] * v[ib] / lam**2
                delta_e = -s * (Delta + 2 * J * (a + b))
                response = beta if abs(delta_e) < 1e-14 else -math.expm1(-beta * delta_e) / delta_e
                q += probability * response
                probability_sum += probability
    chi_x = q / 4
    return {"T": T, "J": J, "Delta": Delta, "omega": omega, "g": g,
            "chi_x": chi_x, "g_local": math.sqrt(omega / (2 * q)),
            "phi_quadratic_coefficient": omega - 2 * g * g * q,
            "probability_sum": probability_sum,
            "f_normal": -T * math.log(lam)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--T", type=float, nargs="+", required=True)
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--Delta", type=float, required=True)
    p.add_argument("--omega", type=float, required=True)
    p.add_argument("--g", type=float, required=True)
    a = p.parse_args()
    print(json.dumps({"parameters": vars(a), "seed": None,
                      "values": [normal_curvature(T, a.J, a.Delta, a.omega, a.g)
                                 for T in a.T]}, indent=2))


if __name__ == "__main__":
    main()
