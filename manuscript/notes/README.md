# 阶段研究汇总（LaTeX → PDF）

本目录放**阶段性研究汇总**：每份是一个研究阶段（如选题调研、P0 预审、热三临界验证）
完成后，AI 用论文文本形式整合该阶段的工作，编译成 PDF 供自己审阅和向导师汇报。

## 与 md 文件的分工

- [`docs/log.md`](../../docs/log.md)、[`manuscript/theory/`](../theory/) 是**逐条工作记录与推导**；
- 本目录是**按阶段整合的论文文本**，面向汇报与审阅，不是清单式记录。
- 每份汇总的结论必须能从 [`results/runs/`](../../results/runs/)、[`docs/claims.md`](../../docs/claims.md)
  追溯；汇总本身不新造结论。

## 工作流

1. 一个研究阶段（或内容足够）完成，用户让 AI 起草一份汇总。
2. AI 按 `template.tex` 起草，用**自然的论文文本**把这一阶段做了什么、物理上发生了什么
   讲清楚（不必套死板论文腔）；但文献引用要规范、不遗漏——背景结论、方法先例、每个物理
   结论的出处都用 `\cite{引用键}` 引用，键须在 [`literature/references.bib`](../../literature/references.bib)
   中真实存在，不手打编号、不引用未核对的文献。
3. **起草后必须先由用户过目内容并敲定**，再编译成 PDF。已定稿的内容不得被静默覆盖；
   修改前先确认。
4. 每份独立命名 `NN-主题.tex`，主题按内容定，不固定周期。序号仅用于排序。

## 索引

| 文件 | 阶段 | 状态 |
| --- | --- | --- |
| [01-选题与文献调研.tex](01-选题与文献调研.tex) | 选题与国内外研究现状 | 已定稿 |
| [02-有限温三临界结构与全局证据.tex](02-有限温三临界结构与全局证据.tex) | 热三临界候选、相图拓扑与证据分级 | 起草待定稿 |

## 本地编译

在项目根目录的 PowerShell 中，把 `<文件名>` 换成要编译的 `.tex`：

```powershell
$buildDir = Join-Path (Resolve-Path -LiteralPath 'manuscript/notes').Path 'build'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$env:PAR_GLOBAL_TEMP = $buildDir
$env:TEMP = $buildDir
$env:TMP = $buildDir
latexmk -cd -xelatex -interaction=nonstopmode -halt-on-error -outdir=build manuscript/notes/<文件名>.tex
```

本机 `C:\Windows\Temp` 的访问权限有问题，以上设置使 Biber 的临时文件落在项目内的
`build` 目录。生成的 PDF 位于 `manuscript/notes/build/<文件名>.pdf`，整个 `build`
目录不提交 Git。若需清理中间文件，只删除 `build`，不要删除 `.tex` 或引用库。

## 修改约定

1. 新增论文先在 [`literature/reading-list.md`](../../literature/reading-list.md) 记录出处与
   阅读状态，再添加唯一 BibLaTeX 条目。
2. 正文用 `\cite{引用键}`，不手打编号；更新论文版本时保持引用键稳定。
3. 每条物理结论写清是平衡基态、模拟有效基态还是驱动耗散稳态。
4. 正式写作前逐句核对原论文图号/公式、学校格式要求和文献争议。
