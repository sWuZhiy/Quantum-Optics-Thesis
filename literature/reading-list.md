# 超辐射相变选题文献清单

更新：2026-09-19。引用键对应 [references.bib](references.bib)；每篇的内容概述见 [逐篇文献笔记](notes/README.md)，A² 问题见 [专项对照](a2-and-spin-interactions.md)。优先保存稳定 DOI 与作者提供的全文入口。这里收集**引用信息与阅读入口**，不会把网页摘要当成已完整阅读的论文，也不擅自将远程论文 PDF 混入本地原始资料。正式引用具体结论时，仍需核对原文公式、图号和版本。

## 核心文献

| 引用键 | 主题与用于论文的具体位置 | 原文入口 | 阅读状态 |
| --- | --- | --- | --- |
| `Nataf2010NoGo` | 静态电偶极腔 QED 的禁戒条件；引言中界定 `A²` 和 TRK 约束 | [期刊正文](https://www.nature.com/articles/ncomms1069) | 正文关键假设已核 |
| `Zhang2014CircuitIsing` | 国内团队参与的 Dicke–Ising 电路方案；四相与 AFM–超辐射共存的早期理论 | [期刊正文](https://www.nature.com/articles/srep04083) | 摘要、模型和结论已核 |
| `Rohn2020QuantizedIsing` | 一维 Dicke–Ising 中光诱导磁序转变与一级边界 | [期刊页面](https://journals.aps.org/prresearch/abstract/10.1103/PhysRevResearch.2.023131) | 摘要已核；公式待逐页读 |
| `Zhu2020SqueezedLight` | 国内团队参与的参量压缩光调控超辐射及三临界点；受泵浦情形 | [作者预印本](https://arxiv.org/abs/1907.00522) | 摘要已核；不要当作无泵浦平衡实验 |
| `Chen2021Antisqueezing` | `A²` 与独立反压缩项、反向相变、NMR 有效基态模拟 | [期刊正文](https://www.nature.com/articles/s41467-021-26573-5)；[本地 PDF](Experimental%20quantum%20simulation%20of%20superradiant%20phase%20transition%20beyond%20no-go%20theorem%20via%20antisqueezing.pdf) | 本地正文、补充材料和审稿文件已读；引文须区分“模拟基态”与真实热平衡 |
| `Schellenberger2024Mapping` | 有关联光–物质系统正常相的映射方法；可作理论对照 | [开放全文](https://scipost.org/SciPostPhysCore.7.3.038/pdf) | 摘要/结构已核；推导待逐页读 |
| `Mendonca2025Matter` | 用户上传的 Dicke–Ising/XXZ 基态相图、一级边界、XXZ 次线性光子标度 | [作者全文](https://arxiv.org/html/2503.04961)；[本地 PDF](Role%20of%20Matter%20Interactions%20in%20Superradiant%20Phenomena.pdf) | 本地正文已读；Ising 相图要与后续 QMC/Comment 对照 |
| `Langheld2025Wormhole` | 大尺度 QMC 基准；反铁磁共存相、跃迁阶数；**补充材料 §IV、图 S9 已讨论 `A²` 的可达区** | [作者全文和补充材料](https://arxiv.org/html/2409.15082) | 关键正文段落与补充材料 §IV 已核；本地尚无 PDF |
| `Hormann2025Comment` | 对 Mendonça 等 Ising 相图提出可核查的异议 | [作者全文](https://arxiv.org/html/2511.08452) | 全文短文已核；预印本状态待追踪 |
| `Sur2026Critical` | 自旋临界模增强腔响应和本征压缩；限制“磁临界性协同”的泛泛新颖性表述 | [期刊正文](https://www.nature.com/articles/s41467-026-73112-1) | 摘要和主要结论已核；具体模型需细读 |

## 背景和备选方向

### 有限温度平衡态

| 引用键 | 与本题的关系 | 原文入口 | 阅读状态 |
| --- | --- | --- | --- |
| `Peng2019Unified` | Dicke 类模型的零温与有限温度超辐射相变；说明热平衡研究不限于基态 | [APS 期刊摘要](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.100.063820) | 摘要已核；模型细节待通读 |
| `Otake2026FiniteT` | 腔耦合一维**经典** Ising 链的有限温度超辐射相变与精确临界温度；是有限温度方向的直接先例，但不等同于含量子自旋涨落与反压缩的模型 | [APS 期刊正文](https://doi.org/10.1103/fxml-nv46) | 摘要、模型类型和结论已核；公式待逐项核对 |

有限温度的热平衡态由配分函数和自由能决定；零温基态仅是 $T\to0$ 极限。静态单模压缩映射在任意温度仍精确成立，因此有限温度本身不能消除“参数重整化”的新颖性问题。

### 其他背景

| 引用键 | 使用边界 | 原文入口 |
| --- | --- | --- |
| `Baumann2010OpenDicke` | 驱动开放腔 Dicke 相变的经典实验；与静态热平衡区分 | [期刊正文](https://www.nature.com/articles/nature09009) |
| `Zhu2024Nonreciprocal` | 用户上传的双模、旋转、定向泵浦与驱动耗散稳态相变；文中 `J` 为模间跳跃，不是自旋相互作用 | [期刊页面](https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.132.193602)；[本地 PDF](Nonreciprocal%20Superradiant%20Phase%20Transitions%20and%20Multicriticality%20in%20a%20Cavity%20QED%20System.pdf) |
| `RomanRoche2025Bound` | Dicke–Ising 的平衡激发与束缚极化激元；如后续研究能谱再细读 | [开放全文](https://onlinelibrary.wiley.com/doi/full/10.1515/nanoph-2024-0568) |

## 本地辅助材料

- [Chen 补充材料](Supplementary%20Information-Experimental%20quantum%20simulation%20of%20superradiant.pdf)：压缩变换、参数条件、实验编码；引用时应引用主论文并注明补充材料位置。
- [Chen 审稿资料](Peer%20Review%20File.pdf)：关于“真正平衡态”与模拟有效基态的表述争论；帮助把握措辞，不代替正式论文引用。

## 引用核查规则

1. 优先引正式期刊版本；预印本保留 arXiv 版本号，发表后更新 `.bib`。
2. 在正文注明结论对应的模型、近似、零温/有限温、闭合/开放系统及图号。
3. `Mendonca2025Matter` 的 Ising 相图必须同时核对 `Langheld2025Wormhole` 与 `Hormann2025Comment`；不要把争议当作定论。
4. 禁戒定理、`A²` 与反压缩的关系只在清楚说明物理平台与 `D(g)` 约束后叙述。
