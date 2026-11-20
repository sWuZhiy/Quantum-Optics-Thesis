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

## Continuation: finite-chain ED and bounded cavity landscape

Code base before the continuation: Git `48eb429`. The deterministic ED/landscape scripts were added in this continuation; SHA-256: `ft_tc_ed.py` `C9F64B4CB9E2EBAFF19EC3E8098D00DA115F6CD1CCF907B85CF2B4F6242DAD59`, `ft_tc_landscape.py` `879E9401918D471394DD5100FCB43593D3DB2235C6D821FCABB21288FB611085`, `ft_tc_transfer.py` `8407FF1C7B629F51D81AFFE20EC358FFF7C1F29CA8628C147C887D6125A1EFFD`. Interpreter and units are as above; seed: none. All raw JSON files in this directory are output of the commands below, with parameters, runtime and values. The ED script uses dense periodic-chain exact diagonalization, with `N≤12` on this machine; its finite-size convergence is a diagnostic, not a formal infinite-chain bound.

```powershell
$py = 'D:\codex\quantum-optics-env\python.exe'
& $py code/src/ft_tc_landscape.py --solver transfer --T 0.3 --J -0.3 --Delta 0.6 --omega 1 --g 0.6708203932499369 --points 9 --M 10 14 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/landscape-T0.3.json
& $py code/src/ft_tc_landscape.py --solver ed --T 0.1 --J -0.3 --Delta 0.6 --omega 1 --g 0.6708203932499369 --points 17 --N 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/landscape-ed-T0.1.json
& $py code/src/ft_tc_ed.py --T 0.3 --J -0.3 --Delta 0.6 --h 0.45 --N 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/ed-T0.3-h0.45.json
& $py code/src/ft_tc_ed.py --T 0.3 --J -0.3 --Delta 0.6 --h 0.675 --N 4 6 8 10 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/ed-T0.3-h0.675.json
& $py code/src/ft_tc_ed.py --T 0.1 --J -0.3 --Delta 0.6 --h 0.45 --N 4 6 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/ed-T0.1-h0.45.json
& $py code/src/ft_tc_transfer.py --T 0.1 --J -0.3 --Delta 0.6 --h 0.45 --M 12 16 20 | Set-Content -Encoding utf8 results/runs/2026-11-20-ft-tc-p0/transfer-T0.1-h0.45.json
& $py -m unittest discover -s code/tests -p 'test_ft_tc_transfer.py' -v
```

`Φ(φ)` is even. Since `|m_x|≤1/2`, its derivative satisfies `dΦ/dφ≥2ωφ−2g` for `φ≥0`; hence every global minimizer lies in `[0,g/ω]`. This is a search-range proof, not a grid-resolution guarantee.

- At `T=0.1`, the 17-point ED grid spans `[0,g]`; the maximum absolute `N=12` versus `N=10` difference is `5.9×10⁻⁹` and the smallest **grid** value is `Φ(0)≈-0.6000000015`. No continuous minimization or phase classification follows.
- At `T=0.1,h=0.45`, ED gives `f_12=-0.6281152533567688`, with `f_8-f_12≈-2.3×10⁻¹³`. Transfer `M=12,16,20` quadratic `1/M²` extrapolation gives `-0.6281174601714403` (difference `2.21×10⁻⁶`); last-two linear extrapolation gives `-0.6281576668042903` (difference `4.24×10⁻⁵`). Thus this Trotter range should not be used by itself for close branch comparisons.
- At `T=0.3,φ=g/4,h=0.45`, ED `N=12` gives `Φ=-0.6009325549728755`; `N=10` differs by `1.27×10⁻¹⁰`. The transfer three-point quadratic fit gives about `-0.600933307`, within `7.5×10⁻⁷`. This test point is lower than `Φ(0)≈-0.600855961` by `7.66×10⁻⁵`, showing a finite-displacement trial state is favorable at this selected parameter; no phase boundary has been found.
- Five automated checks now pass: three original transfer checks plus ED `J=0` and finite-periodic-chain `h=0` limits. They validate implementation factors and mappings at tested points, not global phase topology.

The next gate is a continuous multi-start search of all extrema over `[0,g/ω]` for several `g,T`, with size and independent-method checks near the closest competing minima; then a `T→0` comparison to the published quantum boundary. The journal version of Leibig et al. remains pending a full-text comparison.
