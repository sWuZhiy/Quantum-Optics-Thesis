# FT-TC Z：零温已发表相图基线（2026-11-22）

这轮仅校准**平衡有效哈密顿量的零温**，不宣称新的有限温相界。基线提交为 `3eb4640`；运行使用 `D:\codex\quantum-optics-env\python.exe`（Python 3.12、NumPy 2.5.3），`ℏ=k_B=1`，所有算法确定性运行、随机种子不适用（`null`）。模型和归一化见[推导](../../../manuscript/theory/zero-t-baselines.md)。本目录 JSON 各自保存完整参数、运行时间、源文件 SHA-256、有限尺寸能量或积分结果、Lanczos 残差。

| 源文件 | 此轮 SHA-256 |
| --- | --- |
| `code/src/ft_tc_zero_t.py` | `dc69d80d06d3c91570fe18d300f8f1e12fa8c54158eb1fe676af5e135c3e3677` |
| `code/src/ft_tc_zero_t_scan.py` | `d79e14e9c081064f109f341ff80a81697e1427dbf3a17fbe3ee5e4f195c23ccd` |
| `code/src/ft_tc_ground_state.py` | `7b465a929cc7f9c73bdfd9f63ee741a19ad15031604bf6df44684c06e18425b8` |

## 复算命令

从仓库根目录在 PowerShell 中运行；`N=18` 的 Lanczos 任务请串行执行，以免与其他大矩阵作业争用内存。

```powershell
$py = 'D:\codex\quantum-optics-env\python.exe'
& $py code/src/ft_tc_zero_t.py --J -0.2 --omega 1 --Delta 0.2 0.4 0.6 --momenta 8192 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/koziol-8192.json
& $py code/src/ft_tc_zero_t.py --J -0.2 --omega 1 --Delta 0.2 0.4 0.6 --momenta 32768 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/koziol-32768.json
& $py code/src/ft_tc_zero_t.py --J -0.3 --omega 1 --Delta 0.3 0.6 0.9 --momenta 32768 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/project-Jm03-32768.json
& $py code/src/ft_tc_zero_t_scan.py --J -0.2 --Delta 0 --omega 1 --N 8 12 16 18 --h-min 0.54 --h-max 0.62 --points 9 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/ferro-zero-field-finite-N.json
& $py code/src/ft_tc_zero_t_scan.py --J -0.2 --Delta 0.2 --omega 1 --N 12 16 --h-min 0.611 --h-max 0.619 --points 17 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/ferro-first-order-fine.json
& $py code/src/ft_tc_ground_state.py --J -0.2 --Delta 0.2 --h 0.6165 --N 12 16 18 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/ferro-first-order-size-check.json
& $py code/src/ft_tc_zero_t_scan.py --J -0.2 --Delta 0.6 --omega 1 --N 8 12 16 --h-min 0.04 --h-max 0.4 --points 10 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/ferro-continuous-grid.json
& $py code/src/ft_tc_zero_t_scan.py --J 0.2 --Delta 0.6625 --omega 1 --g 0.26 --N 16 --h-min 0.005 --h-max 0.2704 --points 54 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/afm-full-field-N16.json
& $py code/src/ft_tc_zero_t_scan.py --J 0.2 --Delta 0.6625 --omega 1 --g 0.26 --N 12 16 18 --h-min 0.055 --h-max 0.085 --points 13 --staggered-m2 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/afm-coexistence-refined.json
& $py code/src/ft_tc_zero_t_scan.py --J 0.2 --Delta 0.6625 --omega 1 --g 0.26 --N 12 16 --h-min 0.18 --h-max 0.2704 --points 10 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-z/afm-high-field-grid.json
& $py -m unittest discover -s code/tests -v
```

## 已发表铁磁边界的对照

`Δ=0,J=−0.2,ω=1` 的无限链横场 Ising 精确积分加全局等能最小化给 `g_c=0.40904366821157356`、`h_c≈0.58099648`、`φ_c≈0.35509441`，与 [Koziol（2026）第 5 页图 3、§VI](https://arxiv.org/pdf/2605.27484) 的 `0.4090436682` 一致。动量中点积分 `8192→32768` 的 `g_c` 差低于输出双精度末位；等能残差约 `3×10⁻¹⁷`，驻点残差 `1.1×10⁻¹⁶`。正常态局部失稳是 `√0.2=0.4472135955`，**不是**一级相界。独立周期链 Lanczos 网格最低 `g_equal` 随 `N=8,12,16,18` 为 `0.40853745,0.40898605,0.40903568,0.40904074`，向精确积分值靠近；此网格还存在 `h` 离散误差。

`J=−0.2,Δ=0.2`（文献 `ε=0.1`）的非可积一级侧，`N=12,16` 的 17 点横场网格均在 `h=0.6165` 取最低，得 `g_equal=0.49555844581,0.49555844943`。同一 `h` 下 `N=18` 为 `0.49555844945`，`N=16→18` 变化约 `1.4×10⁻¹¹`；这是**定点尺寸差**，不是全 `h` 连续极小值的严格误差。作者 [Langheld 等（2025）Zenodo 原始结果，DOI 10.5281/zenodo.15774230](https://zenodo.org/records/15774230) 的 `results/Ferro_chain_NtoS.csv` 在 `ε=0.1,J=−0.2` 报 QMC `g=0.4955765682`、提取误差 `dg=0.0000185428`（`level_crossing`）。我们的网格值接近其报告区间低端；QMC 的 `dg` 不是无限尺寸和温度全部系统误差的严格界。

`J=−0.2,Δ=0.6`（文献 `ε=0.3`）的连续侧，[Koziol（2026）式 (10)–(14)](https://arxiv.org/html/2605.27484) 与 [Langheld 等（2025）图 3(c)](https://arxiv.org/html/2409.15082) 给 `g_c=√0.35=0.5916079783`。有限链 `N=8,12,16` 在本次最小采样横场 `h=0.04` 给 `g_equal≈0.5916200674`，至 `h=0.4` 单调增到约 `0.5929673389`；这只核对局部连续行为，没有扫描整个允许位移区间。`J=−0.2` 的四次系数在 `Δ=0.4` 变号，解析三临界 `g_tc=√0.3=0.5477225575`；`J=−0.3` 的对应点为 `Δ=0.6,g_tc=√0.45=0.6708203932`。两者是文献已知解析基准。

## 反铁磁共存内点

从同一 Zenodo 原始结果 `results/Antiferro_chain_ANAS.csv` 与 `Antiferro_chain_ASPS.csv` 取 `J=+0.2,g=0.26`：作者报告纵场 `ε=0.3254240341±0.0001016021` 的 AN→AS 边界、`ε=0.3365386161±0.0002298402` 的 AS→PS 边界。选中间原始网格点 `ε=0.33125`，即本项目 `Δ=0.6625`。作者 `QMC_data/Antiferro_chain/ASPS_g0.26_lc/` 中 `L=1024,β=512` 的上扫原始行在此点给光子密度 `n_ph≈0.00450762`、交错磁序平方 `mag2≈0.888634`；它们是作者有限尺寸/有限逆温 QMC 报告，不是本项目结果。该 ZIP 仅在内存中核读，未把原始数据文件写入仓库。

本项目的 `N=16` 周期物质链在完整允许 `0≤h≤4g²/ω=0.2704` 的 54 点网格（`h=0` 另按解析正常态）上，最低采样点 `h≈0.070098`，`Φ_0−Φ_0(0)=−1.56677×10⁻⁴`；高场末点为 `+0.0072900`。局部 13 点网格在 `h=0.07` 得下表，`φ²` 为热力学自洽下的相干光子密度，`m_s²=⟨[Σ(-1)^iσ_i^z/N]^2⟩`：

| `N` | `Φ_0(0.07)−Φ_0(0)` | `φ²` | `m_s²` |
| ---: | ---: | ---: | ---: |
| 12 | `−1.56929×10⁻⁴` | `0.00453033` | `0.896158` |
| 16 | `−1.56665×10⁻⁴` | `0.00453033` | `0.893818` |
| 18 | `−1.56655×10⁻⁴` | `0.00453033` | `0.893018` |

这些有限链数值在同一点同时支持非零光场位移和强交错关联，且趋势与作者共存窗口相符；`m_s²` 仍有可见尺寸漂移，单个有限 `N` 的正值不证明热力学长程序。有限网格不能排除窄的隐藏极小；`N=18` 只在局部横场窗口测量，未完成整个区间的独立全局搜索。作者 QMC 的全模型能量和本项目有限链自洽 `Φ_0` 也不是同一有限尺寸对象，不能直接用其原始能量误差棒作为此处的误差界。

## 验证与资源边界

NumPy 矩阵自由 Lanczos 的 `N≤18` 结果附带收敛标记和残差。关键扫描最大 Ritz 残差约 `3.5×10⁻¹⁰`（总能量单位）；独立稠密 ED、`J=0` 单自旋、`Δ=0` 精确积分、反铁磁 `h=0` 和 `m_s²` 稠密本征矢对照已通过，共 18 项自动检查。默认 `N=18,maxiter=160` 预分配最多约 320 MiB Lanczos 基向量；与另一个扫描并发时一次内存分配失败，串行重跑通过。尚未完成 AFM 共存区的受控无限链外推、非零纵场完整零温相界或正式 P0/T 阶段放行。
