# FT-TC 同模型双向引文核查（2026-11-20）

2026-11-21 续检：以 `Dicke-Ising` 搭配 `finite-temperature/thermal`、`longitudinal field`、`tricritical/phase diagram` 检索近期公开题录，并复核 [Leibig 等（2026）](https://arxiv.org/html/2601.10210) §5、[Koziol（2026）](https://arxiv.org/html/2605.27484) §VI–VII 与 [Hörmann（2026）](https://arxiv.org/html/2606.26081) §VI 的研究范围。本轮仍未命中同时满足 `zz/z/x`、非零纵场、完整平衡有限温全局相界的原文；返回的同轴核心工作仍以零温为对象，其他近邻工作有轴向或开放稳态差异。搜索引擎与引文索引的未命中不能证明不存在先例；Leibig 正式期刊正文仍未逐页核对。

## 检索对象与范围

候选是平衡、单模、一维周期链的 `zz/z/x` 哈密顿量：`H=ωa†a+ΔΣsᶻ+4JΣsᶻsᶻ+(2g/√N)(a+a†)Σsˣ`，`s=σ/2`、`Δ≠0`。要找的是同一模型的**完整有限温热力学相图和全局自由能边界**。有限逆温下投影到基态的 QMC、驱动开放稳态及另一轴向的可积模型不算覆盖。

2026-11-20 使用 OpenAlex 公开 works API，以 DOI/arXiv DOI 定位 Gammelmark–Mølmer（2011）、Granet（2023）、Rao 等（2025）、Langheld 等（2025）、Leibig 等（2026）、Koziol（2026）、Hörmann（2026），读取各自 `referenced_works` 与 `filter=cites:<work-id>`，再按题名、摘要和原文逐式筛查。并用 `Dicke-Ising`、`thermal/finite temperature`、`longitudinal field`、`tricritical` 的组合做独立关键词检索。**引用数据库有延迟和漏收，下面的计数只说明本次索引返回，不是全体文献数量。**

| 种子文献 | OpenAlex work ID | 前向引文返回数 | 本次后向交叉引用要点 |
| --- | --- | ---: | --- |
| Gammelmark–Mølmer 2011，DOI `10.1088/1367-2630/13/5/053035` | `W2093551820` | 88 | 早期热量子链先例 |
| Granet 2023，DOI `10.21468/SciPostPhys.14.5.133` | `W4378471575` | 9 | `zz/x/x`，无独立非零纵场 |
| Rao 等 2025，arXiv:2509.04391v2 | `W7080132981` | 9 | 引 Gammelmark、Langheld；`zz/y/x` |
| Langheld 等 2025，DOI `10.1103/lcvj-ksct` | `W4415608628` | 20 | 零温同轴基线 |
| Leibig 等 2026，DOI `10.21468/SciPostPhys.21.3.071` | `W7124457561` | 6 | 引 Gammelmark、Langheld；零温同轴 |
| Koziol 2026，arXiv:2605.27484v2 | `W7162692943` | 3 | 引 Gammelmark、Rao、Langheld、Leibig；零温三临界 |
| Hörmann 2026，arXiv:2606.26081v1 | `W7165846066` | 0 | 引上述核心先例；§VI 自述热边界未展开 |

## 前向引用中最接近的论文：逐篇排除理由

| 原文与已核位置 | 论文报告的对象 | 对当前缺口的判断 |
| --- | --- | --- |
| [Rao 等 2025](https://arxiv.org/html/2509.04391)，式 (1)、(11)，图 4 | `zz/y/x` 量子链：低温热三临界，零温单侧端点在有限温消失 | **强相关热先例**，但纵场与 Ising 不同轴；不覆盖 `zz/z/x` |
| [Leibig 等 2026](https://arxiv.org/html/2601.10210)，式 (1)、§3–4、结论 | `zz/z/x` 同模型，热力学极限自洽物质哈密顿量；结果是零温相图 | **同模型直接先例**，尚未见完整 `T>0` 相图；期刊版正文与 arXiv v1 的逐页差异仍待核 |
| [Koziol 2026](https://arxiv.org/html/2605.27484)，§III–VI | 同轴铁磁零温 Landau、三临界及有限尺寸标度 | 封住零温新颖性；不提供目标热相图 |
| [Hörmann 2026](https://arxiv.org/html/2606.26081)，§V.3、§VI | 同轴零温解析结构；§VI 说热边界延伸未在该文完成 | 缺口线索，不是所有文献未做的证明 |
| [Román-Roche 等 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12133256/)，§3.1 式 (4)–(6) | 可积横场链的零温相图与极化激元；指出另加纵场使物质模型解析不可积 | 不提供目标热相图；支持其数值难点 |
| [Mendonça 等 2026](https://arxiv.org/html/2607.17934)，§IV.2、§V | Dicke–Ising 非高斯变分与 DMRG 基态计算 | 零温方法基准，不是有限温自由能 |
| [Caballero-Benitez 2026](https://journals.aps.org/prresearch/abstract/10.1103/yzjp-fy85)，摘要、图 1；[预印本式与图](https://arxiv.org/html/2603.13693) | 泵浦空间模式调制下的广义 Dicke–Ising 关联与纠缠 | 2026-11-18 发表的新近引文；受泵浦有效模型和基态性质，不覆盖本题的无泵浦平衡热相图 |
| [Wang、Li、Chen 2026](https://arxiv.org/abs/2602.09912)，摘要 | 开放 Dicke–Ising 的耗散稳态 | 稳态相变不是 `exp(-βH)` 热平衡相变；正文尚未逐式核读 |

另查 Gammelmark（2011）的前向条目以及上述 2025–2026 同轴论文的前向条目，未见原文报告“`zz/z/x`、`Δ≠0`、完整 `T>0` 全局一级/二级边界”的论文。**这是截至本次索引和检索词的未命中，不是穷尽性的新颖性证明。** 若之后找到这样的同模型原文，应按[主张台账 C04](../project/claims.md)立即止损，并从当前路线撤下其投稿主张。

## 尚存的检索风险

- OpenAlex 未必收录最新预印本的引用关系；Hörmann 前向数为 0 尤其不能解释为没有后续工作。
- Leibig 正式期刊 PDF 与本地 arXiv v1 的逐页差异未完成核对。2026-11-20 补查[作者单位的期刊题录与摘要](https://cris.fau.de/publications/370578265/)及 [arXiv 版本历史](https://arxiv.org/abs/2601.10210)：前者明确报告 *quantum phase diagram*、多临界点及基态，后者截至检索只列 v1；[预印本 §5](https://arxiv.org/html/2601.10210)把有限温与热相变列为展望。该证据加强“已核内容为零温”的判断，但摘要不能代替期刊正文的逐页核查，也不能证明不存在其他同模型热论文；SciPost 正文在本次访问中未能打开。
- Rao、Gammelmark 的轴向差异已核到公式，但未把所有参数化论文逐式排除；定题和投稿前应复查 DOI、arXiv 新版本和引用数据库。

2026-11-21 再试 [SciPost 正式文章](https://scipost.org/SciPostPhys.21.3.071)及其 `/pdf`：网页访问未返回可读正文；PowerShell 对 PDF 地址拿到的是约 3.8 KB 的机器人验证 HTML 页面，不是论文 PDF，已删除该误命名文件。本次未绕过验证，故不能声称核对了正式版正文。当前可逐式引用的是 [Leibig 等（2026）arXiv:2601.10210v1 式 (1)、§3–5、图 3–8](https://arxiv.org/html/2601.10210)，其 §5 将有限温延伸作为展望；[作者单位的正式题录摘要](https://cris.fau.de/publications/370578265/)仅支持期刊论文报告量子基态相图。定题前如获得合法可读的正式 PDF，需补做版本差异核查。

2026-11-22 新近线索补核：[Román Roche（2020）萨拉戈萨大学硕士论文](https://zaguan.unizar.es/record/97667/files/TAZ-TFM-2020-206.pdf) §3.3 第 19–23 页式 (81)、(83)、(87)、(91)、图 6–7 的有限温 Ising–腔图，是 `xx/z/x`（旋转后 `zz/x/z`），而本项目是 `zz/z/x`；图 6 为物质均场，图 7 为 `N=8` 周期链。它是**同轴腔/交换的热近邻先例**，既限制宽泛方法与协同新颖性，也不满足目标模型的止损条件。并复核 [Hörmann（2026）§IV.1 式 (18)、§VI](https://arxiv.org/html/2606.26081v1)：同轴向目标模型的零温结构已经覆盖，作者明示热边界与三临界线尚未在该文求出；这一原文项目此前已收录，并非新的空白证明。近期公开题录仍未命中同一哈密顿量的完整平衡热图，索引漏收与 Leibig 正刊正文访问缺口继续保留。

2026-11-23 定题前复查（收尾）：以 `"Dicke-Ising" "finite temperature" thermal tricritical longitudinal field 2026` 与 `cavity coupled Ising chain superradiant "thermal phase"/"finite-temperature phase" 2026` 两组检索复查公开题录，返回的仍全部是已收录先例（[Otake–Bamba 2026](https://journals.aps.org/prresearch/abstract/10.1103/fxml-nv46) 经典同轴链、[Rao 等 2025](https://arxiv.org/abs/2509.04391) `zz/y/x` 热三临界、[Koziol 2026](https://arxiv.org/abs/2605.27484)、[Hörmann 2026](https://arxiv.org/html/2606.26081) 与 [Leibig 等 2026](https://doi.org/10.21468/SciPostPhys.21.3.071) 零温工作），未命中同一 `zz/z/x` 非零纵场模型的完整平衡热相图。Leibig 期刊全文在本机仍不可访问（SciPost 与 FAU 页面均被网络策略拦截，仅可经搜索获取元数据：作者、卷期 21, 071、2026-09-22 发表、摘要聚焦零温量子相图与多临界点精化）；期刊版与 arXiv v1 的逐页差异仍无法排除，正式引用继续以已核 arXiv v1 为限。索引漏收风险与上文相同。
