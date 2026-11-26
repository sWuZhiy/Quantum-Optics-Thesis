# FT-TC 数值方法与误差边界

更新：2026-11-26。本文是 P0 阶段全部求解器的方法清单与误差边界，供论文
“数值方法”一节直接使用。理论推导见[统一模型](model.md)，零温基线见
[零温校准](zero-t-baselines.md)，原始数据见 [`results/runs/`](../../results/runs)。

## 1. 方法清单

| 求解器 | 文件 | 原理与参数 | 用途与限制 |
| --- | --- | --- | --- |
| 解析正常态曲率 | `code/src/ft_tc_normal_curvature.py` | [模型 §有限温局部阈值](model.md) 的 `2×2` 转移矩阵 + 三自旋概率，任意 `T>0` 精确 | `g_local`、`χ_x`；只判局部稳定 |
| 周期热 ED | `code/src/ft_tc_ed.py` | 稠密对角化 `N≤12`（`h=0` 对角直接配分和）；`f_spin(T,h)` | 有限链交叉；非热力学极限 |
| 开边界 NLCE | `code/src/ft_tc_nlce.py` | 连续簇展开 `L≤12`，`f_L=F_L−F_{L−1}` + 末三阶 Aitken | 无限链逐阶逼近；低温小场收敛慢 |
| Suzuki–Trotter 转移矩阵 | `code/src/ft_tc_transfer.py` | 固定 `M≤20/24` 虚时间切片的**无限空间**转移矩阵 Perron 根；`1/M²` 二次外推（末 3/4 点两窗口） | 独立无限空间交叉；极小场窗口漂移 ~`3.9e-6`，不具裁决力 |
| 零温 Lanczos | `code/src/ft_tc_ground_state.py`、`ft_tc_zero_t_scan.py`、`ft_tc_zero_t_line.py` | 矩阵自由完全重正交 Lanczos `N≤18`（基底 ≤320 MiB，串行）；粗扫 17 点 + 黄金分割 30 步 | 零温基态能；网格极小非精确相界 |
| 热阈值扫描/细化 | `code/src/ft_tc_thermal_threshold.py`、`ft_tc_thermal_refine.py` | `g_equal(h)` 的 ED/NLCE 网格 + 单括区黄金分割 | 预研诊断 |
| 热四次系数 | `code/src/ft_tc_quartic.py` | 有限链枚举 + 无限链转移矩阵谱分解（r=1 四自旋窗口、r≥2 次主导本征空间几何级数）；**最近邻对用六路径合流核** | 直接公式仅 `T≳0.1` 可靠（活化贡献 `e^{±β}` 相消） |
| 精确回返路径 | `code/src/ft_tc_landau_paths.py` | 2/4/6 阶全部回返序列 + `F_m` 合流差商（Decimal 60 位） | 零场系数的独立精确有限环实现，所有专用模块的对照基准 |
| 三临界验收 | `code/src/ft_tc_tricritical_validate.py` | 无限链 `a₄(T)=0` 二分（容差 1e-13）+ 精确路径 `a₆` | 局部 Landau 验收 |
| 全域驻点搜索 | `code/src/ft_tc_global_stationary.py` | 对数均匀粗扫（`N=10` 200 点）→ 全部内点极小检出 → 黄金分割（`N=12`）→ NLCE/转移交叉 + 逐极小误差诊断 | 有限域 `h≤8g_local²/ω`；离散扫描不能排除任意窄极小 |
| 深度-标度分析 | `code/src/ft_tc_stationary_analysis.py` | 深度 vs `g_local·a₄²/(8a₆|a₂|)` 对照 | Landau 塌缩检验（[模型 §Landau](model.md)） |
| 轨迹与端点 | `code/src/ft_tc_trajectory.py` | 全温区多根搜索（401/501 点扫描）+ 切触双根端点方程 `a₄=∂_T a₄=0`；有限环 `N=8,10,12` 独立端点 | 局部 Landau 候选拓扑 |
| 重入预检 | `code/src/ft_tc_reentrant_validate.py` | 双根内外温度探针 + 六阶预测深度 + 远场驻点扫描 | 重入窄袋全局预检 |
| 32GB 外部 ED | `code/src/ft_tc_32gb_reentrant_ed.py`、`ft_tc_32gb_return_analyze.py` | 外部 32GB 机器周期热 ED `N=14`（峰值内存 4.05 GiB，每点 200 s）；回传 ZIP 哈希审计 | 有限尺寸升级；`N=14` 为同类双精度 ED 的实用上限 |
| 自动测试 | `code/tests/` 18 个文件 | 59 项：解析锚点、闭式对照、稠密 ED 交叉、N 收敛、缩放回归等 | 每次运行 `unittest discover` |

## 2. 误差边界（写作时必须同时给出）

1. **数值可靠区间**：零场热系数直接公式仅 `T≳0.1` 可靠（活化构型贡献的
   `e^{±β}` 中间乘积在低温超出双精度）；`T→0` 用解析锚点，不直接求值。
2. **误差等级**：所有近等能误差为**数值诊断级**（ED `N` 收敛、NLCE 与 ED 差、
   转移两窗口差），不是严格误差界；严格界需独立 SSE/有限温 MPS 实现。
3. **转移矩阵限制**：在重入窄袋的极小场（深度 `1e-9–1e-11`），`M≤20` 外推窗口
   漂移约 `3.9e-6`，大 3–5 个量级，不参与裁决。
4. **双精度 ED 极限**：`Δ=.40024` 在 `N=12→14` 翻号，同类双精度有限环加尺寸收益
   不足（决策已冻结）；端点邻域需高精度响应/张量网络方法。
5. **离散扫描**：不能排除任意窄的未采样极小；黄金分割假定单括区单极小。
6. **外推非严格**：AFM 三点外推、`a₆` 无限链无闭式（有限环 `N` 收敛限定）。
7. **可复现性警告**：外部 32GB 运行使用 Python 3.13.14 而非交付的 3.12（源码与
   输入哈希全部匹配，结论分级未受影响）；正式引用末尾数位可复跑 `.4001` 交叉。
