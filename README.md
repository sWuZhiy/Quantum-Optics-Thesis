# Quantum Optics Thesis

量子光学毕业设计工作区。具体研究问题、导师要求和论文格式尚待确定；这里先保存文献、推导、代码、数据与写作过程，避免结论和图表失去出处。

## 目录

| 路径 | 用途 |
| --- | --- |
| `project/` | 课题范围、阶段计划、决策与进度 |
| `literature/` | 原始文献、补充材料、审稿资料及阅读索引 |
| `theory/` | 模型定义、符号约定和解析推导 |
| `code/src/` | 可复用的计算与绘图代码 |
| `code/notebooks/` | 探索性计算；确认后的方法移入 `src/` |
| `code/tests/` | 数值实现的关键验证 |
| `data/raw/` | 原始数据，保留原貌；默认不提交到 Git |
| `data/processed/` | 由代码生成的中间数据；默认不提交到 Git |
| `results/runs/` | 每次计算的参数、日志和输出；默认不提交到 Git |
| `results/figures/` | 经过检查、准备引用到论文的图 |
| `thesis/` | 论文正文、学校模板与最终提交材料 |

## 当前状态

- 已收集 3 篇超辐射相变研究论文，以及其中一篇的补充材料和审稿文件；见 [文献索引](literature/README.md)。
- 当前暂定课题为含 `A²` 与反压缩的相互作用自旋–腔模型；[研究评估](project/research-assessment.md) 已记录文献重叠、精确映射及可执行路线。最终题目和学校要求尚待确认，见 [项目简述](project/brief.md)。
- 已建立[文献清单与阅读状态](literature/reading-list.md)、[BibLaTeX 引用库](literature/references.bib)、[平衡态优先的选题建议](project/topic-recommendation.md)和[中文 LaTeX 调研笔记](thesis/notes/main.tex)。
- 任何图表应能追溯到模型、数据、代码版本和参数。原始数据不要覆盖。

## 日常工作方式

1. 在 `project/brief.md` 确定当前目标；复杂工作拆成可验收的小任务。
2. 阅读文献时记下出处、页码、模型假设和仍待核查的问题。
3. 推导或计算完成后，记录参数、验证方法和结果位置。
4. 重要阶段更新 `project/progress.md`，检查 Git 差异后提交。

项目协作约定见 [AGENTS.md](AGENTS.md)。
