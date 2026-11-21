# `FT-TC` 投稿门槛 P0：新颖性备忘（待判定）

更新：2026-11-21。**结论：保留候选；P0 科学预审已有可执行方案，正式放行仍待题目范围确认和期刊正文补核。**依据[逐轴调查](../literature/ft-tc-axis-survey.md)、[差异矩阵](../literature/ft-tc-gap-matrix.md)、[双向引文](../literature/ft-tc-citation-audit-2026-11-20.md)、[方法试算](method-feasibility.md)及对 Mendonça 等（2025）后续的[补充预筛](../literature/mendonca-followup-survey.md)。定向检索尚未命中同模型完整热相图，不能提升为“无人做过”。完整判定见[P0 验收](p0-gate-review-2026-11-21.md)。

## 核心问题与最近先例

以 `ℏ=k_B=1`、`s_i^α=σ_i^α/2`、一维周期链定义

```text
H = ω a†a + Δ Σ_i s_i^z + 4J Σ_i s_i^z s_{i+1}^z
    + (2g/√N)(a+a†) Σ_i s_i^x ,  Δ ≠ 0.
```

这里 `J>0` 代表反铁磁；Mendonça 等（2025，DOI [`10.1103/z8gv-7yyk`](https://doi.org/10.1103/z8gv-7yyk)）式 (1) 的 Ising 截面用 `−4J_M Σs_i^z s_{i+1}^z`，故本式 `J=−J_M`，其余轴向相同。该文图 3、Langheld 等（2025，DOI [`10.1103/lcvj-ksct`](https://doi.org/10.1103/lcvj-ksct)）图 3–4、Leibig 等（2026，DOI [`10.21468/SciPostPhys.21.3.071`](https://doi.org/10.21468/SciPostPhys.21.3.071)）及 Hörmann（2026，[arXiv:2606.26081](https://arxiv.org/html/2606.26081)）覆盖这一轴向的**零温**基态边界、三临界与窄共存相。原作者 [2026 方法论文](https://arxiv.org/html/2607.17934) §IV.2 也已重审这些 Ising 特征。

有限温直接先例包括 Gammelmark–Mølmer（2011，DOI [`10.1088/1367-2630/13/5/053035`](https://doi.org/10.1088/1367-2630/13/5/053035)）的不同轴向量子链一、二阶边界，Rao 等（2025，[arXiv:2509.04391v2](https://arxiv.org/html/2509.04391)）的 `zz/y/x` 热三临界，Granet（2023，DOI [`10.21468/SciPostPhys.14.5.133`](https://doi.org/10.21468/SciPostPhys.14.5.133)）的 `zz/x/x` 热问题；Román‑Roche 等（2021，DOI [`10.1103/PhysRevLett.127.167201`](https://doi.org/10.1103/PhysRevLett.127.167201)）补充 §III.2 已给一般有限温临界响应条件，不能把自洽方法或热阈值本身作为新意。差异仍暂时落在**非零纵场 `zz/z/x` 的完整热全局自由能与零温三临界结构的热延伸**。

## 最小可能增量与反证

最低应给出：在同一 `H` 的固定参数和热力学极限下，受控确定一条零温一级/二级边界在 `T>0` 的连接方式；比较全部自由能极小值并识别真实共存线/终点；`T→0` 回到 Langheld、Leibig、Hörmann 的基线；用独立算法或解析极限检查。仅绘制低分辨率热相图、复述温度改变临界耦合、或加入静态同正交分量的 `A²−ξ` 重标定均不满足投稿增量。

最可能否决：① 同哈密顿量完整热相图已有工作；② 所选区域只给已有一般自洽理论的平凡数值代入，没有明确物理结构或可测预测；③ 非可积物质链的自由能和一级边界在本机可用资源内无法收敛；④ 归一化、符号或极限检查失败。任何一项成立即按[主张 C04](claims.md)降级或停止。

## 可追踪的检索边界

检索式包括 `"Dicke-Ising" "finite temperature" "longitudinal" "tricritical" 2026`、`"Dicke-Ising" "thermal" "tricritical" 2026`、`"cavity" "Ising" "longitudinal field" "finite temperature" superradiant`，并逐式核对上述定向找到的原文。2026-11-20 至 21 已对七篇核心种子作公开索引前后向引文交叉，逐篇排除理由见[引文审计](../literature/ft-tc-citation-audit-2026-11-20.md)。期刊正式版、未收录新稿和同模型异名工作仍可漏检；检索覆盖不足时不作“首次”的投稿表述。

## 目前决定

`FT-TC` 保持首要活动候选。方法预审已从“小尺寸基准”推进到一个铁磁截面上由开边界 NLCE 提供的逐阶无限链自由能；此结果**只证明有能力继续做定向 Z 校准**，不证明存在可投稿的热终点或三临界线。正式 P0 暂缓：Leibig 期刊版正文未取得，用户和导师尚未接受具体题目范围。Mendonça 的 XXZ 图 4 光子标度列为[独立备选 P0 预筛](../literature/mendonca-followup-survey.md)，不与 `FT-TC` 混成一个题目。
