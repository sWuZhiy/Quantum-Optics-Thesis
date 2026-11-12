# 研究对话与文献总笔记

更新：2026-11-12。本页供回顾项目对话中的**用户观点、问题和查阅过的文献**。它是导航与观点记录，不替代[逐篇文献综述](../literature/reading-list.md)、[详细研究评估](research-assessment.md)、[阶段任务](roadmap.md)或[工作日志](progress.md)。引用键以[文献库](../literature/references.bib)为准；下文“论文报告”“我们的分析”“用户判断”分别标注，不能互换。

## 一眼看当前状态

- 研究对象仍在选择：受约束量子 Dicke–Ising 零温基线、有限温候选 `FT-TC`、同轴经典链候选 `CL-AF`。后两者**只是方案选项**，尚未获导师确认或产生本项目相图。
- 当前有文献综述、模型预判、执行路线、专用 Conda 环境和 LaTeX 调研草稿；`theory/model.md`、数值研究程序及经过验证的运行结果尚未建立。见[项目简述](brief.md)与[项目首页](../README.md)。
- 论文查阅深度不一：有些已逐页核读，有些只核摘要。具体范围见[阅读清单的逐篇条目](../literature/reading-list.md)；**“入库”不等于“读完”或“独立复现”**。
- 本页记录的原话只在有可回查记录时加引号；其余为对用户问题的忠实概括。回答与推断不写成用户已认可的观点。

## 对话如何发展

| 时间 | 对话主题 | 已形成的记录 | 当前定位 |
| --- | --- | --- | --- |
| 2026-09 | 项目结构、Conda 环境、逐步完成毕设、GitHub 同步与可移植性 | [项目入口](../README.md)、[环境说明](../code/README.md)、[执行路线](roadmap.md)、[决策记录](decisions.md) | 结构和工作顺序已写清；科学计算尚未开始 |
| 2026-09 | `A²`、反压缩与自旋相互作用能否形成有价值的平衡态课题 | [研究评估 §1–7](research-assessment.md)、[文献综述](../literature/reading-list.md) | 静态同一光场正交分量的二次项可压缩映射；新意要落在受约束路径或非等价物理问题 |
| 2026-10-18 | 有限温度三临界结构和受限可达性 | [FT-TC 文献包](../literature/reading-list.md)、[阶段 F](roadmap.md)、[决策记录](decisions.md) | 用户要求列为选项；零温基准和自由能方法是进入条件 |
| 2026-10-19 | 同轴经典链的铁磁协同与反铁磁竞争 | [研究评估 §8–9](research-assessment.md)、[CL1–CL7](roadmap.md) | 用户要求列为独立候选；已有混合范围 Ising 相图先例 |
| 2026-10-18 至 10-22 | Otake–Bamba、Gammelmark–Mølmer、Langheld、Leibig 等逐段阅读与方法比较 | [按日期的核读日志](progress.md)；Langheld 的本地深读笔记见下文 | 对论文、作者解释和本项目推断分别记录；没有据此生成新数值结果 |
| 2026-11-12 | 间隔一个月后的整体复核和删减 | [研究评估 §10](research-assessment.md)、[文献清单](../literature/reading-list.md) | 增补 Hörmann（2026）零温先例，更新 Leibig 期刊状态；两份重复建议文档已合并 |

## 你提出的研究观点、问题和工作偏好

以下“用户提出”只表示讨论过、要求记录或表达过偏好；没有明确确认的部分继续保持为待定。`P` 为本页的稳定编号，今后新观点向下追加。

| 编号与性质 | 用户提出的内容 | 对话后的状态与回查 |
| --- | --- | --- |
| P01 · 暂定方向 | 研究反压缩与自旋相互作用对含 `A²` 项的超辐射相变的联合作用，希望研究价值超过简单加项扫描。 | 已写入[项目简述](brief.md)；静态单模模型是工作假设，具体平台和题目待确认。 |
| P02 · 路线偏好 | 优先考虑平衡态，有限温度也在范围内；若耗散机制有更明确价值，可作备选。 | 零温先做可信基线；若泵浦产生 `ξ`，实验室系的驱动稳态要另立模型。见[决策记录](decisions.md)。 |
| P03 · 方案选择 | 要求将 `FT-TC` “作为一个方案选项”，并收录所需文献。 | 已登记为候选，详见[FT-TC 核心文献包](../literature/reading-list.md)与[阶段 F](roadmap.md)；不代表最终题目或已证明创新。 |
| P04 · 方案选择 | 要求把同轴经典链的铁磁基准、反铁磁竞争与超辐射列入选题规划。 | 已登记 `CL-AF`，可从 CL1–CL3 独立预研；是否选作毕设主线仍待确定。见[项目简述](brief.md)。 |
| P05 · 物理问题 | “反铁磁是可以对抗 A² 项的吗，使得平衡态系统依然能突破 no-go 定理吗？” | Langheld 等（2025）补充 §IV、图 S9 报告其**有效模型示例**中反铁磁超辐射区部分可达；这不等于真实微观装置普遍突破禁戒。详见本机 Langheld 深读笔记“用户问题记录 1–2”。 |
| P06 · 方法问题 | 问虫洞量子蒙特卡洛（wormhole QMC）是否常用、可靠，以及与张量网络相比的计算量。 | 已在本机 Langheld 深读笔记“用户问题记录 3–4”区分无偏算法、统计误差、符号问题和任务依赖的计算成本；尚未为本项目实现该算法。 |
| P07 · 方法判断 | 你指出：远离临界区可能有更便宜、可定量的近似或数值方法；自己研究的特定 Tavis–Cummings（TC）耦合模型中，绝热消除/平均场的精度受失谐控制，修正方法可能改善；wormhole QMC 很强，但应用范围和使用团队较集中。 | 这是用户**研究判断**，并非本项目 TC 模型的已验证结果。对话认为近似精度需由具体小参数和基准检验；“wormhole 原理上不能算 TC”表述过强，Weber（2022）有 JC 类顶点讨论。详见本机深读笔记“用户判断记录 5”。 |
| P08 · 方法问题 | 问非临界点与临界点是否一般使用不同方法。 | 对话结论是求解器未必更换，但精度、尺寸、温度和相界判据通常要调整；一级边界还需全局能量或自由能比较。详见本机深读笔记“用户问题记录 6”。 |
| P09 · 项目工作偏好 | 希望知道如何一步步完成项目、代码和结果放在哪里、Conda 环境怎样使用，以及让其他 AI 能自然接手。 | [首页](../README.md)给启动顺序与产物位置，[协作约定](../AGENTS.md)给规则，[代码说明](../code/README.md)给解释器路径。 |
| P10 · 同步与回顾 | 后续**有改动时**推送到 `git@github.com:sWuZhiy/Quantum-Optics-Thesis.git`；希望有一份可回顾对话、文献和个人观点的总笔记。 | 本页即统一回顾入口；项目进度和科研结论仍分别保存在各自的主文档中。 |
| P11 · 投稿判断 | 问当前项目能否达到投稿水平、哪个方向更有潜力，并要求比较候选与既有工作的差异。 | [研究评估 §10](research-assessment.md)给阶段性判断：`FT-TC` 问题潜力较高但需可信热力学结果；`CL-AF` 入门成本较低但已知相图重叠较多。此为条件性评估，不是录用预测。 |

本机更详细的逐段阅读与用户问题原话保存在 `literature/notes/langheld-2025-wormhole-reading-notes.md`。该笔记及 `assets/` 截图目前未纳入公开 Git 仓库；本页保留无需截图即可理解的观点摘要，公开回查以[文献综述](../literature/reading-list.md)和论文原文为准。

## 主引文库：按问题查 22 篇

本表只给“为什么回看它”和最有用的原文入口；实际读到哪里、模型范围、图表与未核内容在[逐篇综述](../literature/reading-list.md)中。原文位置是阅读定位，不表示本项目重算了论文结果。带“摘要”的条目不得引用其尚未核查的具体公式。20 篇已有[本地 PDF 索引](../literature/README.md)；Hörmann（2026）与 Lee–Johnson（2004）目前只有在线引文。

| 主题 | 论文与引文键 | 回看入口与核读范围 |
| --- | --- | --- |
| 禁戒与平台 | [Nataf–Ciuti 2010](https://doi.org/10.1038/ncomms1069) `Nataf2010NoGo` | 电偶极禁戒的假设；摘要、引言与主要论证已核 |
| 禁戒与平台 | [Zhang 等 2014](https://doi.org/10.1038/srep04083) `Zhang2014CircuitIsing` | 电路 Dicke–Ising 有效模型式 (10)、图 2–3；电路近似待复算 |
| 禁戒与平台 | [Chen 等 2021](https://doi.org/10.1038/s41467-021-26573-5) `Chen2021Antisqueezing` | 单自旋 Rabi 的 `A²` 与反压缩；正文图 1、3–4，补充 Note 1–3 已读；区分量子模拟器基态 |
| 泵浦与开放系统 | [Baumann 等 2010](https://doi.org/10.1038/nature09009) `Baumann2010OpenDicke` | 泵浦开放腔实验；摘要、图题已核 |
| 泵浦与开放系统 | [Zhu 等 2020](https://doi.org/10.1103/PhysRevLett.124.073602) `Zhu2020SqueezedLight` | 参量压缩与超辐射；目前核到摘要 |
| 泵浦与开放系统 | [Zhu 等 2024](https://doi.org/10.1103/PhysRevLett.132.193602) `Zhu2024Nonreciprocal` | 非互易双模泵浦问题；本地正文已读，细节待复核；文中 `J` 是模间耦合 |
| 量子 Ising 基线 | [Rohn 等 2020](https://doi.org/10.1103/PhysRevResearch.2.023131) `Rohn2020QuantizedIsing` | 光诱导横场；目前主要核摘要 |
| 量子 Ising 基线 | [Mendonça 等 2025](https://doi.org/10.1103/z8gv-7yyk) `Mendonca2025Matter` | Ising/XXZ 基态；正文式 (1)、图 2–4；Ising 区需并读 Comment |
| 量子 Ising 基线 | [Langheld 等 2025](https://doi.org/10.1103/lcvj-ksct) `Langheld2025Wormhole` | QMC 图 3–4；补充 §IV 式 (S33)–(S35)、图 S9 的 `A²` 可达区；已有专题深读 |
| 量子 Ising 基线 | [Hörmann 等 2025 Comment](https://arxiv.org/abs/2511.08452) `Hormann2025Comment` | 对窄共存区与阶数的异议；短文已核，后续争议待追踪 |
| 量子 Ising 基线 | [Leibig 等 2026](https://doi.org/10.21468/SciPostPhys.21.3.071) `Leibig2026SelfConsistent` | §2.2、§3–4；本地预印本已核读，期刊版差异待核 |
| 量子 Ising 基线 | [Koziol 2026](https://arxiv.org/abs/2605.27484) `Koziol2026Criticality` | 零温三临界；式 (12)–(14)、图 1–3 已核 |
| 量子 Ising 基线 | [Hörmann 2026](https://arxiv.org/html/2606.26081v1) `Hormann2026Folds` | §II、§V.3、§VI；零温相界已核相关段落，111 页预印本未全篇复算 |
| 自洽与谱学 | [Schellenberger–Schmidt 2024](https://doi.org/10.21468/SciPostPhysCore.7.3.038) `Schellenberger2024Mapping` | 正常相低能映射；摘要、范围已核 |
| 自洽与谱学 | [Román-Roche 等 2025](https://doi.org/10.1515/nanoph-2024-0568) `RomanRoche2025Bound` | 束缚极化激元；主文式 (1)–(3)、响应和附录相关段落已核 |
| 热相变 | [Lee–Johnson 2004](https://doi.org/10.1103/PhysRevLett.93.083001) `Lee2004FirstOrder` | 相互作用多量子比特腔一级跃迁先例；目前仅核元数据与摘要 |
| 热相变 | [Gammelmark–Mølmer 2011](https://doi.org/10.1088/1367-2630/13/5/053035) `Gammelmark2011Thermal` | 另一轴向量子链有限温自由能；式 (7)–(9)、图 4 与正文已核 |
| 热相变 | [Peng 等 2019](https://doi.org/10.1103/PhysRevA.100.063820) `Peng2019Unified` | 零温与有限温一般理论；目前仅核摘要 |
| 热相变 | [Otake–Bamba 2026](https://doi.org/10.1103/fxml-nv46) `Otake2026FiniteT` | 同轴经典链；式 (13)–(18)、图 3、附录 C–D；可作 `CL-AF` 基准 |
| 材料与响应 | [Bamba 等 2022](https://doi.org/10.1038/s42005-021-00785-z) `Bamba2022Magnonic` | ErFeO₃ 磁振子型平衡理论；模型和主要结果段落已核 |
| 材料与响应 | [Kim 等 2025](https://doi.org/10.1126/sciadv.adt1691) `Kim2025Magnonic` | 磁振子型光谱证据；主要实验段落已核 |
| 材料与响应 | [Sur 等 2026](https://doi.org/10.1038/s41467-026-73112-1) `Sur2026Critical` | 物质临界模增强腔响应；摘要和主要模型结论已核 |

### 对话中专题补查、尚未纳入主引文库的文献

这些是相关问题的**辅助证据或方法参照**，不是再增加一个默认阅读任务。正式写入论文前需按实际使用版本复核：

| 问题 | 已查文献与回看位置 |
| --- | --- |
| 经典同轴链的短程/全连接相互作用先例 | [Baker 1963](https://doi.org/10.1103/PhysRev.130.1406) 摘要；[Nagle 1970](https://doi.org/10.1103/PhysRevA.2.2124) 模型；[Henriques–Salinas 2015](https://arxiv.org/abs/1508.03543) 第 2 页式 (1)、第 5–6 页式 (14)–(24)；[Dantchev 等 2024](https://doi.org/10.1103/PhysRevE.110.L062104) 式 (1)、(10)–(11)。模型映射见[研究评估 §8–9](research-assessment.md)。 |
| 量子链和有效平台解析检查 | [Pfeuty 1970](https://doi.org/10.1016/0003-4916(70)90270-8) 第 84 页式 (3.2)、第 89 页；[Dimer 等 2007](https://doi.org/10.1103/PhysRevA.75.013804) §II 式 (11)、(16)；[Román-Roche 等 2021](https://doi.org/10.1103/PhysRevLett.127.167201) 及其补充材料。阅读过程见[2026-10 的进度](progress.md)。 |
| 数值方法与 TC 对话 | [Weber 2022](https://doi.org/10.1103/PhysRevB.105.165129) §III–VI 的 wormhole/JC 构造；[Schollwöck 2011](https://doi.org/10.1016/j.aop.2010.09.012) MPS 综述；[Kamar–Maghrebi 2024](https://doi.org/10.1103/PhysRevB.110.075114) 玻色局域维数。算法应用还查过 [Weber–Luitz–Assaad 2022](https://doi.org/10.1103/PhysRevLett.129.056402)、[Weber–Vojta 2023](https://doi.org/10.1103/PhysRevLett.130.186701)、[Ribeiro 等 2024](https://arxiv.org/abs/2311.07683) 和 [Weber 2025](https://doi.org/10.1103/mtq7-n96c)；具体评价在本机 Langheld 深读笔记。 |
| 2026 年方法与相图争议的后续线索 | [Mendonça 等 2026](https://arxiv.org/abs/2607.17934) 非高斯变分新方法；目前只核摘要，不能据此认定既有 Ising 争议已经解决。 |

## 当前共同认识与仍需验证的地方

| 命题 | 证据等级 | 下一步 |
| --- | --- | --- |
| 静态单模、同一正交分量上的 `D(a+a†)²-ξ(a+a†)²` 可在稳定域通过压缩变换映射到改参后的模型。 | 文献公式及本项目解析核查；[Langheld 补充 §IV](https://arxiv.org/html/2409.15082)、[Chen 补充 Note 1](https://doi.org/10.1038/s41467-021-26573-5)。 | 在 `theory/derivations.md` 写完整算符、能量常数、原光场观测量及适用条件。 |
| `FT-TC` 可能研究与现有零温量子链轴向一致的有限温度三临界结构。 | **研究问题/我们的推断**；[Gammelmark–Mølmer 2011](https://doi.org/10.1088/1367-2630/13/5/053035)已有另一轴向的热相图；[Hörmann 2026 §VI](https://arxiv.org/html/2606.26081v1)把热延伸列为展望。 | 先通过零温基准、全局自由能和热力学极限方法；不能预称发现新热相。 |
| `CL-AF` 的反铁磁竞争物理问题成立，但简单静态相图有混合范围 Ising 先例。 | 文献模型对照；[Otake–Bamba 2026](https://doi.org/10.1103/fxml-nv46)、[Nagle 1970](https://doi.org/10.1103/PhysRevA.2.2124) 与 [Dantchev 等 2024](https://doi.org/10.1103/PhysRevE.110.L062104)。 | 做 CL1–CL3 基准；若追求投稿，另找具体腔实现或光学测量增量。 |
| 本项目尚无数值结果，真实无泵浦平衡实现所需的 `D(g)`、`ξ` 微观来源也未固定。 | [项目现状](../README.md)与[未决要求](brief.md)。 | 明确模型/平台、复现基准；把模拟器有效基态、真实平衡相变和驱动稳态分别表述。 |

## 后续怎样续记

每次对话出现新的用户观点或疑问，在 **P 编号表**追加一行，保留原话或标为概括，并写“已回答／待核／候选／已确认”；讨论回答另指向原文或推导，不替用户作结论。新论文先进入[文献综述](../literature/reading-list.md)并标核读深度，再在本页文献地图加回查入口；正式引用才加入[引文库](../literature/references.bib)。阶段性工作和路径选择分别更新[进度](progress.md)与[决策](decisions.md)。
