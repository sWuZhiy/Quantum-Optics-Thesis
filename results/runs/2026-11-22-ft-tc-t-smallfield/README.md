# `T=0.3` 小横场误差核查（FT-TC 有界热预研）

日期 2026-11-22。统一模型取 `ℏ=k_B=1`、`J=-0.2,Δ=0.2,ω=1,T=0.3`；比较周期热 ED、开链 NLCE 和固定 Trotter 切片数的无限空间转移矩阵。**这是正常态附近的数值诊断，不是热相界或跃迁阶数判定。**

## 复现条件与文件

运行时仓库 `HEAD=2a0604490e95e79c078ba4b2bac30c400f45d854`；使用 `D:\codex\quantum-optics-env\python.exe`（Python 3.12.13、NumPy 2.5.3），确定性计算，`seed=null`。代码 SHA-256：`ft_tc_thermal_threshold.py` 为 `A100EC059DA091D4D5CF5C19476CEE6FAA8F0A4B5BA5D055A3642186C3A6A074`、`ft_tc_ed.py` 为 `C9F64B4CB9E2EBAFF19EC3E8098D00DA115F6CD1CCF907B85CF2B4F6242DAD59`、`ft_tc_transfer.py` 为 `B61CCD212A593DAFC4BC3042C22FF4412C423DC810DB88B0905E55344C91B21E`、`ft_tc_nlce.py` 为 `B575E60B7758895AA765BD46DA3B779E4A0FE62F21B7CC324DB8CE6035009EFD`。ED JSON 自带全部源码哈希、参数和耗时；转移矩阵 JSON 自带参数、各 `M` 的 Perron 迭代残差及耗时。

在仓库根目录执行：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_thermal_threshold.py --T 0.3 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 8 10 12 --h-values 0.025 0.05 0.1 0.2 0.4 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/ed-N8-N10-N12.json
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.3 --J -0.2 --Delta 0.2 --h 0.05 --M 12 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/transfer-h0.05-M12-M20.json
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.3 --J -0.2 --Delta 0.2 --h 0.1 --M 12 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/transfer-h0.1-M12-M20.json
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_thermal_threshold.py --T 0.3 --J -0.2 --Delta 0.2 --omega 1 --method nlce --L 10 11 12 --h-values 0.025 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/nlce-h0.025-L10-L12.json
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.3 --J -0.2 --Delta 0.2 --h 0.025 --M 12 16 18 20 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/transfer-h0.025-M12-M20.json
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_thermal_threshold.py --T 0.3 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 10 --h-values 1.3 1.4 1.5 1.6 1.7 1.8 1.9 2.0 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-smallfield/ed-N10-tail.json
```

解析无限链正常态 `f_spin(T,0)=-0.31881066118989493`、局部阈值 `g_local=0.48909500412766704`，均由既有[阈值记录](../2026-11-22-ft-tc-t-entry/threshold-T0.3-Delta0.2-NLCE-L10-L12.json)给出。下表中的 `g_equal(h)` 用 `g_equal²=ωh²/[16(f_spin(T,0)-f_spin(T,h))]`。ED 每个 `N` 用其自己的正常自由能相减，避免将有限尺寸正常值和无限链侧值混用；转移矩阵用解析无限链正常自由能。转移矩阵的“二次拟合”取末三个 `M=16,18,20` 的 `1/M²` 外推，NLCE 是既有记录的 `L=10–12` Aitken 加速值。

| `h` | 周期 ED `N=8/10/12` 的 `g_equal` | 转移矩阵二次外推 | NLCE 加速 | 数值限制 |
| ---: | --- | ---: | ---: | --- |
| .025 | `.489162487 / .489114085 / .489105482` | `.489103624` | `.489103362` | `N=10→12` 变 `8.60×10⁻⁶`；独立无限链外推均高于解析局部阈值，但仅差约 `8.6×10⁻⁶` |
| .05 | `.489188458 / .489140054 / .489131455` | `.489129599` | `.489129534` | 转移矩阵线性末两阶为 `.489129361`；拟合窗口变化远小于原始 `M=20` 与外推差，仍非严格误差界 |
| .1 | `.489294022 / .489245614 / .489237028` | `.489235177` | `.489235162` | 转移矩阵线性末两阶为 `.489234938`；ED 尺寸变化仍约 `8.59×10⁻⁶` |
| .2 | `.489742461 / .489694108 / .489685586` | 未算 | `.489683762` | 转移矩阵 `.2` 运行遇瞬时内存不足，未生成结果 |
| .4 | `.491914810 / .491867596 / .491859495` | 未算 | `.491857816` | 只作有限场背景检查 |

转移矩阵各 `M` 在 `.025/.05/.1` 的原始自由能、迭代次数和残差均在 JSON 内。`h=.025` 的末 3/4 个 `M` 二次 `1/M²` 拟合给 `g_equal=.48910362436/.48910362402`，窗口差很小；NLCE 加速给 `.48910336193`，二者差 `2.62×10⁻⁷`，都高于 `g_local=.48909500413`。`h=.05` 的二次拟合 `f_spin≈-0.319463749843`，与 NLCE 加速 `f_spin≈-0.319463750015` 很接近；`h=.05` 时周期 ED `N=12` 的绝对自由能偏差主要伴随其正常态有限尺寸偏差，不能直接比较绝对 `f_h` 而忽略同 `N` 正常值。三次转移矩阵运行约 `8.2/9.7/12.0` 秒，ED 五个横场、三个尺寸约 `32.7` 秒。

曾尝试 `h=.05` 的 `M=12,16,20,22,24`，`M=24` 在当前并行负载下分配 128 MiB 数组失败；尝试 `h=.2` 的 `M≤20` 时又在一次 8 MiB 中间数组分配处失败。两次均是 `numpy._core._exceptions._ArrayMemoryError`，未保存无效 JSON，也没有增大 `M` 或重试高内存任务。它们说明本机同时运行多个求解器时内存余量很紧，**不能**据运行失败推断物理模型本身无解。

## 本次判断

在已查 `h=.025–.4`，周期 ED 的 `g_equal(h)` 随 `h` 上升；转移矩阵 `M≤20` 外推与 NLCE 加速在 `.025/.05/.1` 接近，均高于精确 `g_local`。这使“此切片正常态可能以连续方式失稳”成为有根据的**下一项检验假设**。但 `.025` 的有限尺寸变化与 `g_equal-g_local` 同量级，原 NLCE 簇阶在小场变化很大；转移矩阵外推窗口一致不能替代严格误差界，有限采样也不能排除未查的窄有限横场极小。因此**本轮不能确定 `T=.3` 的跃迁阶数，更不能据它定位热三临界点**。下一步先对小 `h` 的四次响应或更长链热自由能建立独立收敛，再连续检查全部 `h` 驻点。

补充高场边界：模型的 `g_equal²≥ωh/8`；以 `h=.025` 的转移外推 `g_ref≈.489104`，若要找更低值，只需查 `h≤8g_ref²/ω≈1.914`。`ed-N10-tail.json` 在 `h=1.3–2.0` 的 8 个点给 `g_equal=.537126–.597881`，远高于小场候选；此前 `h=.05–1.2` 的 [ED 宽网格](../2026-11-22-ft-tc-t-entry/threshold-T0.3-Delta0.2-ED-N8-N10.json)也未见更低的采样点。这个有限区间的**离散**覆盖仍不能代替连续全局极小证明。

零场有限尺寸的额外诊断：解析 `2×2` 经典转移矩阵的本征值为 `λ_+=2.89418110,λ_-=1.21971315`，故零场关联长度 `ξ=−1/ln(λ_-/λ_+)≈1.15729`，每增加两个站点的首项指数比 `(λ_-/λ_+)²≈.1776086`。`g_equal,N(h)` 在 `N=8,10,12` 的两次尺寸增量比于 `h=.025/.05` 实测为 `.1777252/.1776546`，与该零场比率接近。**若经验地假定**有限 `h` 的主尺寸修正仍按该比率，得到 `g_equal,∞(.025/.05)≈.489103623/.489129597`，恰与独立转移矩阵外推接近。这只是三尺寸的经验外推和小横场一致性检查，不能当作严格热力学误差界；四次系数的受控计算式见[模型文档](../../../theory/model.md)。
