# FT-TC 一级侧横场连续细化（有界热预研）

日期：2026-11-22。取[统一平衡有效模型](../../../manuscript/theory/model.md)的 `ℏ=k_B=1,J=-0.2,Δ=0.2,ω=1`。先前[宽横场扫描](../2026-11-22-ft-tc-t-entry/README.md)在 `T=.1/.2` 各见一个内点最低，本轮用黄金分割法细化**预选括区**，并在选定位置用独立方法核对。它不是全 `h` 的连续全局证明，更不是投稿级热相界。

## 运行版本与复现

执行时 Git `HEAD=2a0604490e95e79c078ba4b2bac30c400f45d854`；本轮新增脚本尚未提交，其 SHA-256 为 `ft_tc_thermal_refine.py=79F1E34D6BFDFF7CDA91230F79B8284F8D88F0033D99A445DB6834886A420C37`。其余依赖的 SHA-256 保存在每份 JSON 的 `sources_sha256` 中。解释器 `D:\codex\quantum-optics-env\python.exe`，Python 3.12.13、NumPy 2.5.3；确定性计算，`seed=null`；未安装新包、未改原始数据。每份 JSON 包含完整 CLI 参数、全部被评价点的自由能、最终括区、源码哈希、耗时和失败范围说明。

仓库根目录 PowerShell 示例：

```powershell
$py = 'D:\codex\quantum-optics-env\python.exe'
& $py code/src/ft_tc_thermal_refine.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 12 --lo 0.58 --hi 0.66 --tol 0.003 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-continuous/refine-T0.1-ED-N12.json
& $py code/src/ft_tc_thermal_refine.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --method nlce --L 10 11 12 --lo 0.58 --hi 0.66 --tol 0.005 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-continuous/refine-T0.1-NLCE-L10-L12.json
& $py code/src/ft_tc_thermal_refine.py --T 0.2 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 12 --lo 0.42 --hi 0.54 --tol 0.003 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-continuous/refine-T0.2-ED-N12.json
& $py code/src/ft_tc_thermal_threshold.py --T 0.2 --J -0.2 --Delta 0.2 --omega 1 --method nlce --L 10 11 12 --h-values 0.48176501130047955 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-continuous/threshold-T0.2-NLCE-h0.481765.json
& $py -m unittest discover -s code/tests -v
```

## 核对结果

| 温度 | 精确正常态局部阈值 `g_local` | 连续细化的 ED 内点 | 无限链簇展开核对 | 运行精度边界 |
| ---: | ---: | --- | --- | --- |
| `T=.1` | `.499938848928` | `N=10/12` 均在已采样 `h≈.615016` 最低，`g_equal=.495468248639/.495468365571` | `L=10–12` Aitken 连续细化在同一 `h` 给 `.495468374563`；`L=12` 原序列在该点给 `.495468654159` | ED 最终括区 `[.613313,.616068]`，`Δh<.003`；NLCE 最终宽度 `<.005`；两法差 `8.99×10⁻⁹` 仅为一致性 |
| `T=.2` | `.494014784010` | `N=10/12` 在已采样 `h≈.481765` 最低，`g_equal=.492007814464/.492009022444` | **固定 ED 最优 `h`** 时 `L=10–12` Aitken 给 `.492009204720`，`L=12` 原序列 `.492012835325`；未对 NLCE 单独连续优化 | ED 最终括区 `[.480789,.483344]`，`Δh<.003`；NLCE/ED `N=12` 固定点差 `1.82×10⁻⁷`，不是误差上界 |

`T=.1` ED `N=10→12` 在同一 `h` 的等能耦合变化 `1.17×10⁻⁷`，`T=.2` 为 `1.21×10⁻⁶`；两个温度的有限 `h` 候选都低于解析 `g_local`，与[原始粗扫](../2026-11-22-ft-tc-t-entry/README.md)的一级侧信号一致。数值表中的很多位数只供复算与差分，不代表物理相界精度。黄金分割假定输入括区只有一个局部最低；对正常态首次失去全局优势，仍需以受控无限链自由能验证**全部** `0<h≤8g_ref²/ω`，或给出等价的全局证明。当前还缺近等能的误差预算、热三临界处小场四次响应和完整零温非零纵场边界。

`ft_tc_thermal_refine.py` 的两项新物理测试核对独立自旋 `J=Δ=0` 应取 `h→0` 连续阈值，以及 `J=0` 下 ED/NLCE 在同一有限 `h` 的等能关系。连同既有测试，`unittest discover` 共 22 项通过。`N=12` 两次细化分别约 56/70 秒；`T=.1` NLCE 细化约 61 秒，`T=.2` 的固定点 NLCE 约 12 秒；当前机器并行运行高截断转移矩阵时曾遇内存不足，后续大任务应串行。
