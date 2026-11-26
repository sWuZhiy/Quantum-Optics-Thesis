# 项目协作规则（AGENTS.md）

## 目录与事实来源

| 内容 | 唯一位置 |
| --- | --- |
| 目标、范围、待定项 | `docs/brief.md` |
| 主张、证据、反证条件 | `docs/claims.md` |
| 下一步与验收标准 | `docs/roadmap.md` |
| 影响方向或结构的选择及理由 | `docs/decisions.md` |
| 用户观点与问题（`P` 编号） | `docs/viewpoints.md` |
| 按日期的工作流水 | `docs/log.md` |
| 推导、方法、误差边界 | `manuscript/theory/` |
| 阶段研究汇总（论文文本） | `manuscript/notes/`（AI 起草，用户过目后定稿编译） |
| 文献核读与引用 | `literature/reading-list.md`、`literature/references.bib` |
| 单次运行记录 | `results/runs/` |
| 历史归档（退役的原文件） | `docs/archive/`（默认不读） |
| 解释材料（为用户理解而写） | `docs/explainers/`（默认不读、非证据） |

**一件事只写一处。** 同一结论不复制到多个文件；需要引用时用链接。发现同一内容出现在
两处，保留权威位置的那份，另一处改为链接。`docs/brief.md` 中的待定项不能当作已确认要求。

**归档只能显式决定。** 只有用户要求，或本轮作出并记入 `decisions.md` 的结构决定，才可把
文件移入 `docs/archive/`。不得自动归档、自动删除或凭“看起来过期”移动文件；归档用
`git mv`，内容保留，并在 `docs/log.md` 记一行。

**解释材料与证据分开。** 仅为用户理解而整理的说明写入 `docs/explainers/`，属非权威材料，
不得被 `claims.md`、`roadmap.md` 或论文引用；其中若产生新结论或新数值，必须移入对应的
权威位置（`results/runs/`、`manuscript/theory/` 等），不能只留在解释材料里。

## 记录

- 每轮实质工作或研究讨论结束前，在 `docs/log.md` 表尾追加**一行**：日期、做了什么、
  结果与文件位置、下一步。即使没有新文献或新观点也记；纯状态查询和闲聊不记。
- 新出现的用户观点、问题或偏好，在 `docs/viewpoints.md` 末尾追加 `P` 编号行，
  保留原话或标为概括，并写“已回答／待核／候选／已确认”；原话、转述、推断分开标注。
- 只有结论或路线真的改变时才更新 `claims.md`、`roadmap.md`、`brief.md`；
  影响方向或结构的选择写入 `decisions.md`，说明理由与代价。
- 详细阅读证据写在 `literature/reading-list.md`，不在 `log.md` 复制整篇综述。
- 阶段汇总（`manuscript/notes/NN-主题.tex`）：一个研究阶段完成后可按需起草论文文本汇总；
  起草后**必须等用户过目并敲定**才编译成 PDF，不得覆盖已定稿内容；命名按内容定，不固定周期。
  文件名用 ASCII（英文/拼音简写），中文主题写在 `\title` 与 notes/README 索引里——本机 biber
  不认中文文件名。编译在项目根目录用 latexmk（`-outdir=build`），临时目录指到
  `manuscript/notes/build` 规避 `C:\Windows\Temp` 权限问题。

## 科学规范

- 与用户默认使用中文交流；专业术语首次出现时附英文名称。
- 阅读或引用文献时核对原文，标明作者/年份或 DOI，以及关键结论所在的页码、公式或图号；
  区分论文报告的结果、作者的解释和我们的推断。
- 明确区分真实系统的平衡超辐射相变、受驱动开放系统的稳态相变，以及量子模拟器中
  有效哈密顿量的基态性质。
- 推导写明哈密顿量、参数定义、近似、适用范围和所用单位；改变符号约定时同步更新相关说明。
- 不编造数据、引用或实验结果。数值结论应有收敛、极限或基准检查，并说明验证边界；
  不得把数值诊断当成严格误差界。
- 每张最终图应能追溯到生成脚本和输入；只把审查过的图放入 `results/figures/`。
- 被否定的主张从当前入口移除，但在 `claims.md` 与 `decisions.md` 中保留淘汰理由，
  不静默删除历史。

## 计算与数据

- `data/raw/` 中的原始数据不可覆盖；处理流程从原始数据生成 `data/processed/`。
- 计算记录写入 `results/runs/`，包含代码版本、参数、随机种子和运行说明。
- 探索性 notebook 放在 `code/notebooks/`；可重复使用的计算和绘图逻辑整理到 `code/src/`，
  关键数值实现配 `code/tests/` 测试。
- 本机项目解释器为 `D:\codex\quantum-optics-env\python.exe`。安装 Conda 依赖时用该环境的
  `--prefix`，并把该命令会话的 `CONDA_PKGS_DIRS` 设为 `D:\codex\quantum-optics-conda-pkgs`；
  不要误用 PATH 中另一套 Python，也不要把新环境建回 C 盘。

## 版本控制

- 有改动时推送到 `git@github.com:sWuZhiy/Quantum-Optics-Thesis.git`。
- 提交前跑 `D:\codex\quantum-optics-env\python.exe -m unittest discover -s code/tests`。
- `literature/notes/` 是本地私有笔记，不得进入公开仓库；`tmp/` 为临时工作区，不入库。
