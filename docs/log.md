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
