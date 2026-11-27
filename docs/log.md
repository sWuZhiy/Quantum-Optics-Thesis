# 工作流水

更新：2026-11-26。这是**唯一按日期追加的工作记录**。每轮实质工作结束前在表尾加一行：
日期、本轮做了什么、结果与文件位置、下一步。即使没有新文献或新观点也记；纯状态查询和
闲聊不记。

分工（每件事只写一处）：

| 内容 | 位置 |
| --- | --- |
| 目标、范围、待定项 | [brief.md](brief.md) |
| 已确立/已否定结论及反证条件 | [claims.md](claims.md) |
| 下一步与验收标准 | [roadmap.md](roadmap.md) |
| 影响方向或结构的决定及理由 | [decisions.md](decisions.md) |
| 用户提出的观点、问题、偏好（`P` 编号） | [viewpoints.md](viewpoints.md) |
| 按日期的工作流水（本页） | 本页 |
| 文献核读与引文 | [reading-list.md](../literature/reading-list.md) |
| 推导与数值方法 | [manuscript/theory/](../manuscript/theory) |
| 单次运行记录 | [`results/runs/`](../results/runs) |

**历史流水**（2026-09 至 2026-11-25，原 `research-notebook`、`progress`、`decisions`
三份并行记录）已归入 [`archive/`](archive)，不在默认阅读路径。

## 2026-11 起的记录

| 日期 | 本轮工作 | 结果与位置 | 下一步 |
| --- | --- | --- | --- |
| 2026-11-24 | 汇总 P0 阶段全部工作为完整报告（P37）。 | 新增 P0 报告：内容清单、理论框架、14 个求解器、四级证据数值表、7 项误差边界；59 项测试通过。理论部分已并入 [manuscript/theory/](../manuscript/theory)，全文归档在 [archive/p0-report-2026-11-24.md](archive/p0-report-2026-11-24.md)。 | 写作阶段以 `manuscript/theory/` 为底稿；端点证据等级不升级。 |
| 2026-11-25 | 内存采购调研（P38–P49，另一会话）。 | 结论记入 [viewpoints.md](viewpoints.md) 对应条目；属设备事项，不改变计算路线。 | 到货后核对 SPD/Rank。 |
| 2026-11-26 | 项目结构重整（P50）：拆分冗余元文档、目录对齐通行科研模板。 | 三份并行流水账 → 本页 + `archive/`；`project/` → `docs/`；`theory/` → `manuscript/theory/`；`thesis/notes/` → `manuscript/notes/`；6 份退役快照移入 `docs/archive/`；用户观点表独立为 `viewpoints.md`，文献地图并入 `literature/README.md`；新增 [numerics.md](../manuscript/theory/numerics.md)。同步重写 README 与 AGENTS 的更新规则。无新文献、无新数值，证据等级不变。 | 按新的单一流水规则继续；下一研究步骤见 [roadmap.md](roadmap.md)。 |
| 2026-11-26 | 明确归档规则（同 P50 跟进，无新编号）。 | 在 [AGENTS.md](../AGENTS.md) 增加约束：归档只能由用户要求或记入 `decisions.md` 的决定触发，禁止自动归档/删除，归档用 `git mv` 并记行。 | 无。 |
| 2026-11-26 | 新增解释材料层（同 P50 跟进，无新编号）。 | 新建 [`docs/explainers/`](explainers/README.md)：存放为用户理解而整理的说明，非权威、默认不读、不得作为证据；规则写入 [AGENTS.md](../AGENTS.md)。现有文档无需迁移。 | 无。 |
| 2026-11-26 | 整理 `literature/`（P50 跟进，无新编号）：PDF 分目录、索引加目录小节。 | 20 篇论文 PDF 移入 `literature/papers/`，Chen 补充材料与审稿文件移入 `literature/papers/supplementary/`（5 个已跟踪文件用 `git mv` 保历史）；顶层只剩 8 个索引文档。README 加目录表，`reading-list` 的 `%20` 编码链接统一为尖括号真实空格（本地可点击跳转），`.gitignore` 改为 `literature/papers/*.pdf`。链接已脚本校验，仅剩公式文本假阳性。无文献、数值或证据等级变化。 | 无。 |
| 2026-11-26 | 重定位 `manuscript/notes/` 为阶段研究汇总（P50 跟进，无新编号）。 | 原 `main.tex` 改名 `01-选题与文献调研.tex`（标题加“第一阶段”）；新增 `template.tex`（阶段汇总模板）与 `notes/README.md`（工作流：一个阶段完成后 AI 起草论文文本 → 用户过目敲定 → 编译 PDF）。约定写入 AGENTS.md 与 README。无文献、数值或证据等级变化。 | 下一研究阶段完成后按需起草第二份阶段汇总。 |
| 2026-11-26 | 起草第二阶段研究汇总（FT-TC 物理内容）。 | 新增 `manuscript/notes/02-有限温三临界结构与全局证据.tex`：论文文本整合模型与判据、热三临界候选 (T*,g*)、h⁴ 标度、深度塌缩、上支/重入窄袋/切触端点拓扑、.4001/.4002/.40024 证据分级与验证边界。数据取自 claims.md C04、model.md、zero-t-baselines.md 与运行记录，证据等级未越级。**待用户过目敲定后再编译**。 | 用户审阅后定稿编译成 PDF；此后按阶段继续。 |
| 2026-11-26 | 第二阶段汇总升级为正式论文风格（同 P50 跟进，无新编号）。 | `02-有限温三临界结构与全局证据.tex` 重写为引言（完整文献综述）/模型与自由能泛函/数值方法/结果（零温校准、热三临界候选、相图拓扑、证据分级）/讨论/结论 + 参考文献，全文 `\cite` 真实引用键。template.tex 与 notes/README 同步把“正式论文风格 + 文献引用”写为长期约定。无文献、数值或证据等级变化。 | 用户审阅后定稿编译。 |
| 2026-11-26 | 按用户反馈调整阶段汇总风格（同 P50 跟进，无新编号）。 | `02` 与 template 改为自然论文文本：文风放松、以讲清物理和工作内容为主线，但文献引用规范不遗漏（背景/方法/结论出处均 `\cite` 真实引用键）。无文献、数值或证据等级变化。 | 用户审阅后定稿编译。 |
| 2026-11-26 | 编译第二阶段汇总，解决 biber 中文文件名编码问题。 | `02` 编译成功：5 页 PDF（`build/02-finite-T-tricritical.pdf`），17 条参考文献全部解析、无 undefined 引用。根因是本机 biber 不认中文文件名（xelatex 可以），故 tex 文件名改为 ASCII（`01-topic-and-literature`、`02-finite-T-tricritical`），中文主题保留在 `\title` 与 README 索引。约定同步入 AGENTS.md、template、README。无文献、数值或证据等级变化。 | 用户审阅 PDF 内容后定稿或修订。 |
| 2026-11-27 | 概念答疑并整理为解释材料（模型轴向、纵场图像、闭合体系、平台对应）。 | 新增 [`docs/explainers/2026-11-27-轴向等价类与平台对应.md`](explainers/2026-11-27-轴向等价类与平台对应.md)：用"三轴夹角"作不变量说明 `yy/z/x`（Gammelmark）与 `zz/y/x`（Rao）严格等价，而本项目的 `zz/z/x` 属另一等价类（零场经典 vs 量子横场 Ising）；并列出平台对应（磁偶极原子、Rydberg、超导比特、磁振子晶体 → A 类）。平台对应与可积性论证标注为**我们的推断、待核**，未写入 `claims.md`。 | 若平台对应经原文核实成立，把夹角不变量论证提升到缺口矩阵逐式差异部分。 |
