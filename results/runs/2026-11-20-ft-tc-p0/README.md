# FT-TC P0 finite-temperature matter-chain pilot — 2026-11-20

Code: repository base `de1d533`, plus `code/src/ft_tc_transfer.py` SHA-256 `8407FF1C7B629F51D81AFFE20EC358FFF7C1F29CA8628C147C887D6125A1EFFD`. Interpreter: `D:\codex\quantum-optics-env\python.exe` (Python 3.12.13, NumPy 2.5.3). Random seed: none; deterministic Perron iteration starts from the positive uniform vector. Units: `ℏ=k_B=1`; `H_spin=JΣσᶻ_iσᶻ_(i+1)+(Δ/2)Σσᶻ_i+(h/2)Σσˣ_i`. At each Trotter number `M`, the spatial transfer matrix gives the **infinite-chain** free energy; its `M→∞` limit remains to be extrapolated.

Run commands from repository root:

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.5 --J -0.3 --Delta 1 --h 0.8 --M 10 12 14 16 18 20
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.5 --J 0.3 --Delta 1 --h 0.8 --M 10 12 14 16 18 20
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.5 --J 0 --Delta 1 --h 0.8 --M 8 12 16 20
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.5 --J -0.3 --Delta 1 --h 0 --M 8 12 16 20
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.1 --J -0.3 --Delta 1 --h 0.8 --M 10 14 18 20
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.1 --J -0.3 --Delta 0.6 --h 0.4 --M 10 14 18 20
& 'D:\codex\quantum-optics-env\python.exe' -m unittest discover -s code/tests -p 'test_ft_tc_transfer.py' -v
```

| Case | `f_M` at M=10 | `f_M` at M=20 | Quadratic `1/M²` extrapolation, M=14,16,18,20 | Other check |
| --- | ---: | ---: | ---: | --- |
| `T=.5,J=-.3,Δ=1,h=.8` | `-0.8796538918243457` | `-0.8788884498021707` | `-0.8786322904153439` | M=16,18,20 fit gives `-0.8786322900803375` |
| `T=.5,J=+.3,Δ=1,h=.8` | `-0.6343518547945177` | `-0.6341186861035341` | `-0.634040636583677` | M=16,18,20 fit gives `-0.6340406364527366` |
| `T=.1,J=-.3,Δ=1,h=.8` | `-0.8963590263799222` | `-0.8785747478101682` | not evaluated at M=16 | Linear last two gives `-0.8722420`; quadratic M=14,18,20 gives `-0.8720522`: **insufficiently stable** |
| `T=.1,J=-.3,Δ=.6,h=.4` | `-0.627691551334676` | `-0.6236462987129132` | not evaluated at M=16 | Linear last two `-0.62224357`; quadratic M=14,18,20 `-0.62221844`: spread `2.5×10⁻⁵` |

All displayed Perron residuals in the mixed-field `T=.5` cases were below `1.1×10⁻¹⁰` in the scaled transfer matrix, with wall time about 4–5 seconds per six-point sequence. Fit spread is only a local extrapolation diagnostic, **not a rigorous error bound**. The low-temperature result is not precise enough for a first-order crossing.

Independent checks: at `J=0,T=.5,Δ=1,h=.8`, the analytic free energy is `-0.6774987678245061`; finite-M values move toward it (`M=8: -0.6780550893303394`, `M=20: -0.6775879300541077`). At `h=0,T=.5,J=-.3,Δ=1`, the 1D classical transfer-matrix value is `-0.8069382134244513` and the M=8–20 results agree to floating-point precision. A separate direct `N=4` quantum ED gives `f_4=-0.8786735912273239` for the mixed-field ferro case; finite-N Trotter transfer at M=4,6,8 extrapolates quadratically to `-0.8786740684716403` (difference `4.77×10⁻⁷`). The latter is an independent finite-N check of the Suzuki mapping, not a thermodynamic-limit error estimate.

The `Δ=.6,J=-.3` low-temperature trial uses the same **bare zero-temperature tricritical ratio** as Koziol (2026), Eq. (1) and Section VI: his ferromagnetic amplitude `J_K=.3`, splitting `ε=.3`, and our conventions `J=-J_K`, `Δ=2ε` after a global z spin flip. The chosen `h=.4` is only a matter-chain probe field, not a self-consistent cavity critical point. Fit spread there is still too large to certify a small first-order free-energy difference.

Additional local cavity-landscape stress test: set `ω=1`, `g=√0.45≈0.67082`, `T=.1`, `J=-.3`, `Δ=.6`, so `Φ_T(φ)=φ²+f_spin(T,4gφ)`. The `φ=0` value is `-0.6000000015` at `M=12,16,20`. At `φ=.30`, the **raw** `M=20` value is `-0.6048458207`, apparently lower; however the `1/M²` extrapolations are `-0.59979883` (last two linear) and `-0.59968029` (last three quadratic), with wider-window linear values down to `-0.59988969`. This changes the apparent branch ordering and leaves an extrapolation spread comparable to the putative free-energy difference. The sampled grid `φ=0,.05,.10,.15,.20,.25,.30` was only a stress test, not a complete minimization. Reproduce the key `φ=.30` checks with the script above using `--T 0.1 --J -0.3 --Delta 0.6 --h 0.8049844719 --M 12 14 16 18 20`, then add `φ²=.09` to each output. The exact h value from `4√0.45×.3` should be used for highest precision. **No phase assignment is justified from these values.**

Scope: one field point on each sign of J at moderate T, two low-T stress tests, a sparse local φ-grid, and analytic limits. No globally converged φ-landscape, first-order boundary, tricritical point, magnetization, or T→0 convergence has been established. P0.3 therefore remains **partial**.
