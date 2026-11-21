# FT-TC P0: finite-temperature competing-branch reconnaissance (2026-11-21)

Base commit: `ad89753`. Interpreter: `D:\codex\quantum-optics-env\python.exe` (Python 3.12, NumPy). Units: `ℏ=k_B=1`, `H_spin=JΣσᶻ_iσᶻ_(i+1)+(Δ/2)Σσᶻ_i+(h_x/2)Σσˣ_i`, `Φ_T(φ)=ωφ²+f_spin(T,4gφ)`. Periodic spin chains; no random seed (deterministic dense diagonalization). New scan code SHA-256 `422CFC0DA35D2CC6E0F6FFA9F9A0884FE3E2B6C73D494362F1AACA14D78665F4`; ED code SHA-256 `C9F64B4CB9E2EBAFF19EC3E8098D00DA115F6CD1CCF907B85CF2B4F6242DAD59`. JSON files contain all scan grid values or fixed-field finite-size values, parameters and runtime.

```powershell
$py = 'D:\codex\quantum-optics-env\python.exe'
& $py code/src/ft_tc_scan.py --T 0.1 0.2 0.3 --g 0.62 0.65 0.67 0.69 0.72 --J -0.3 --Delta 0.6 --omega 1 --N 8 --points 25 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/coarse-N8.json
& $py code/src/ft_tc_scan.py --T 0.1 0.2 0.3 --g 0.54 0.56 0.58 0.60 0.62 0.64 --J -0.3 --Delta 0.3 --omega 1 --N 8 --points 41 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/first-order-side-N8.json
& $py code/src/ft_tc_scan.py --T 0.1 --g 0.600 0.602 0.604 0.606 0.608 0.610 0.612 0.614 --J -0.3 --Delta 0.3 --omega 1 --N 8 --points 81 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/coexistence-probe-N8.json
& $py code/src/ft_tc_ed.py --T 0.1 --J -0.3 --Delta 0.3 --h 0.8813664 --N 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/coexistence-side-g0.606.json
& $py code/src/ft_tc_ed.py --T 0.1 --J -0.3 --Delta 0.3 --h 0.9611264 --N 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/coexistence-side-g0.608.json
& $py code/src/ft_tc_ed.py --T 0.1 --J -0.3 --Delta 0.3 --h 0.0184832 --N 8 10 12 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/coexistence-near-zero-g0.608.json
& $py code/src/ft_tc_minimize.py --T 0.1 --J -0.3 --Delta 0.3 --omega 1 --g 0.606 0.608 --lo 0.3 --hi 0.5 --N-search 8 --N-verify 10 12 --tol 1e-6 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/refined-side.json
& $py -m unittest discover -s code/tests -p 'test_ft_tc_transfer.py' -v
```

The full possible global-minimum interval is `0≤φ≤g/ω` by evenness and `|m_x|≤1/2`; the finite grids do **not** guarantee finding every local minimum. The coarse scans were used only to choose a difficult first-order-side check. At `T=0.1,J=-0.3,Δ=0.3,ω=1`, `N=8` finds a normal grid minimum and a finite-φ grid minimum at both `g=0.606` and `g=0.608`. The infinite-chain **classical** normal value from the exact two-state transfer matrix is `Φ(0)=-0.45000003219301243`.

| g | sampled finite φ | ΔΦ=Φ(φ)−Φ(0), ED N=8 | ED N=10 | ED N=12 |
| ---: | ---: | ---: | ---: | ---: |
| 0.606 | 0.3636 | +0.0004266997 | +0.0004271298 | +0.0004271523 |
| 0.608 | 0.3952 | −0.0005322323 | −0.0005314050 | −0.0005313543 |

At `g=0.608,φ=0.0076`, ED N=12 gives `ΔΦ=+8.21065×10⁻⁷`, consistent with a locally stable normal branch at that sampled separation. The `N=10→12` change in the finite-φ comparison is `2.24×10⁻⁸` at `g=.606` and `5.07×10⁻⁸` at `.608`, far below the displayed branch gaps. Thus the tested parameter points strongly indicate an equal-free-energy crossing somewhere between them **if the two smooth minima persist**. This is a P0 method diagnostic, not a located thermodynamic first-order line: the side minima have not been continuously optimized, the `N→∞` error is not rigorously bounded, and an independent thermodynamic-limit solver has not checked the crossing. No finite-temperature tricritical location or novel phase is claimed.

At `Δ=.6`, the 25-point coarse scan showed an (N=8) small finite-φ grid minimum at `T=.3,g=.67`, while `T=.1,g=.67` had its grid minimum at `φ=0`. This is a screening observation only; it is not a reentrance claim. Five existing automated baseline checks passed.

Side-branch refinement: [golden-section script](../../../code/src/ft_tc_minimize.py) SHA-256 `FEA01050F40F8D450A040332A030120D8FBCF265EFC90DB0AC2AB2E93622B77C` minimized the **N=8** side branch in `[.3,.5]` to `φ=.36436552` at `g=.606` and `φ=.39515372` at `.608` (position tolerance `10⁻⁶`). Re-evaluation at these fixed positions with `N=12` gives `ΔΦ=+0.0004271294` and `−0.0005313553`, respectively, leaving the ordering unchanged. This is continuous optimization of the N=8 side branch only; N=12 minima, other extrema and the infinite-chain crossing still require their own checks.

Next: continuously minimize both branches around `g≈.607` at larger `N`, compare against an improved infinite-chain method, then vary `T` and `Δ/J`; reproduce the published zero-temperature boundary before drawing a thermal line.

## Follow-up: larger-chain side minima and infinite-space transfer check

Continuing the P0 gate, run from repository root (same interpreter, units and deterministic settings):

```powershell
& $py code/src/ft_tc_crosscheck.py --input results/runs/2026-11-21-ft-tc-p0/refined-side.json --M 10 12 14 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/infinite-chain-crosscheck.json
& $py code/src/ft_tc_minimize.py --T 0.1 --J -0.3 --Delta 0.3 --omega 1 --g 0.606 0.608 --lo 0.35 --hi 0.41 --N-search 12 --N-verify 10 12 --tol 0.0005 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/refined-side-N12.json
```

The new cross-check script is [`code/src/ft_tc_crosscheck.py`](../../../code/src/ft_tc_crosscheck.py), SHA-256 `326E9947FBD9EC79CF7EC13F64DF586E7F0D19675ECCB32019B35C657C0984B7`; the raw JSON contains each `M`, Perron residual and extrapolation window. At the fixed `N=8` side-minimum positions, the **infinite-space-chain at finite M** transfer calculation, extrapolated in `1/M²`, gives the following differences to the exact `φ=0` infinite-chain normal value:

| g | transfer quadratic last 3 M | transfer quadratic last 4 M | ED N=12 at same φ |
| ---: | ---: | ---: | ---: |
| .606 | +0.000423779 | +0.000421918 | +0.000427129 |
| .608 | −0.000535681 | −0.000538071 | −0.000531355 |

Both extrapolation windows preserve the branch ordering and differ from the finite-chain ED values by about `5.2–6.7×10⁻⁶`, much less than the endpoint branch gaps. This is an independent **spatial thermodynamic-limit formulation**, but `M→∞` has only been extrapolated; the fit spread is not a rigorous error bound.

Direct **N=12** golden-section refinement within the preselected side-branch bracket `[.35,.41]` gives `φ≈.364408` at `g=.606`, `Φ_side−Φ_normal≈+0.000427129961`; and `φ≈.395104` at `g=.608`, `Φ_side−Φ_normal≈−0.000531355747`. Position tolerance was `5×10⁻⁴`; energies were recomputed at the resulting positions. The N=12 refinement changes each side energy by less than `6×10⁻¹⁰` relative to the earlier N=8-minimum positions. It does not certify every extremum outside this bracket, the exact crossing g, the finite-temperature tricritical location or novelty. The next gate is a wider multi-start minimization and a tighter independent infinite-chain error estimate near equal free energies.

## Follow-up: narrower bracket and near-equality failure check

Use the same deterministic interpreter, Hamiltonian and units as above. `ft_tc_minimize.py` searches the side branch at `N=8` and re-evaluates at the same displacement with `N=10,12`; `ft_tc_crosscheck.py` uses the saved displacements for the spatially infinite Trotter transfer matrix.

```powershell
& $py code/src/ft_tc_minimize.py --T 0.1 --J -0.3 --Delta 0.3 --omega 1 --g 0.6068 0.6069 0.6070 --lo 0.35 --hi 0.41 --N-search 8 --N-verify 10 12 --tol 1e-6 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/refined-interior-N8-N12.json
& $py code/src/ft_tc_crosscheck.py --input results/runs/2026-11-21-ft-tc-p0/refined-interior-N8-N12.json --M 10 12 14 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/interior-infinite-chain-crosscheck.json
& $py code/src/ft_tc_scan.py --T 0.1 --g 0.6068 0.6070 --J -0.3 --Delta 0.3 --omega 1 --N 10 --points 81 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/interior-full-phi-N10.json
& $py code/src/ft_tc_minimize.py --T 0.1 --J -0.3 --Delta 0.3 --omega 1 --g 0.60693 --lo 0.35 --hi 0.41 --N-search 8 --N-verify 10 12 --tol 1e-6 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/near-equal-ED.json
& $py code/src/ft_tc_crosscheck.py --input results/runs/2026-11-21-ft-tc-p0/near-equal-ED.json --M 10 12 14 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-21-ft-tc-p0/near-equal-transfer.json
```

| g | side φ from N=8 search | ED N=12 ΔΦ at that φ | transfer quadratic last 3 M | transfer quadratic last 4 M |
| ---: | ---: | ---: | ---: | ---: |
| .6068 | .37908645 | +6.18665×10⁻⁵ | +5.80743×10⁻⁵ | +5.59736×10⁻⁵ |
| .6069 | .38063282 | +1.43316×10⁻⁵ | +1.04905×10⁻⁵ | +8.36327×10⁻⁶ |
| .6070 | .38213203 | −3.35777×10⁻⁵ | −3.74666×10⁻⁵ | −3.96199×10⁻⁵ |

The two methods agree on the **endpoint ordering** at `.6068` and `.6070`; their fixed-displacement differences are about `5.9–6.0×10⁻⁶`, and the transfer quadratic fit-window spread is `2.1–2.2×10⁻⁶`. The `N=10` grid of 81 points over the entire justified interval `[0,g/ω]` identifies two minima at each endpoint: `φ=0` and one near `.38`, with no additional grid minimum. A finite grid cannot exclude a narrow hidden extremum; the side minimum was locally optimized only at `N=8` for these interior g values.

At the near-equal probe `g=.60693`, `φ≈.38108763`, ED gives `ΔΦ_N10≈−3.8553×10⁻⁸` and `ΔΦ_N12≈−2.3858×10⁻⁹`, while the transfer last-4 quadratic extrapolation gives `≈−5.9930×10⁻⁶`. Here **both the N change and the method difference exceed the free-energy signal**. Neither the sign nor an accurate crossing point can be certified from this run. The conservative cross-method bracket supported by these diagnostics is `.6068<g<.6070` for this one slice, still subject to full-extremum and extrapolation checks; do not publish an exact first-order boundary from it.
