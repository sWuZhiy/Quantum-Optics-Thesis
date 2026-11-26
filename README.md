# Quantum Optics Thesis

量子光学毕业设计工作区：一维量子 Dicke–Ising 链（`zz` 交换、`z` 纵场、`x` 腔耦合）的
零温与有限温临界结构。本仓库保存文献、推导、代码、数据与写作过程，使每个结论和图表
都能追溯到模型、代码版本、参数与运行记录。

## 目录

| 路径 | 内容 | 什么时候看 |
| --- | --- | --- |
| [`docs/`](docs/) | 项目元文档：目标、主张、路线、决定、流水、用户观点 | 每轮开始 |
| [`manuscript/`](manuscript/) | 论文素材：`theory/`（推导与方法）、`notes/`（LaTeX 调研草稿） | 推导、写作 |
| [`literature/`](literature/) | PDF、引用库、逐篇综述、缺口矩阵与引文核查 | 查文献、写作引用 |
| [`code/`](code/) | `src/` 计算代码、`tests/` 自动测试、`notebooks/` 探索 | 计算 |
| [`data/`](data/) | `raw/` 原始输入（只读）、`processed/` 处理结果 | 数据 |
| [`results/`](results/) | `runs/` 每次运行记录、`figures/` 已核查图 | 查结果、出图 |

数据流：**配置与代码 → 单次运行记录 → 跨运行汇总 → 已核查图 → LaTeX 引用**。
`data/raw/` 不覆盖；`results/runs/` 与 `data/` 默认不进 Git，只有审查过的图进入
`results/figures/`。约定详见 [数据说明](data/README.md)、[结果说明](results/README.md)、
[代码说明](code/README.md)。

## 每轮开始读什么

1. [项目简述](docs/brief.md)——目标、范围与待定项。
2. [主张台账](docs/claims.md)——哪些结论仍有效、反证条件是什么。
3. [执行路线](docs/roadmap.md)——下一步做什么、怎样算完成。
4. [工作流水](docs/log.md) 末尾两行——上一轮做到哪里。

其余按需：已作决定看 [decisions.md](docs/decisions.md)，回顾用户观点看
[viewpoints.md](docs/viewpoints.md)，历史细节在 [`docs/archive/`](docs/archive/)。
**计划中的文件和图不算已完成产物。**

协作规则见 [AGENTS.md](AGENTS.md)；环境与解释器路径见 [code/README.md](code/README.md)。
