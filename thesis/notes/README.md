# LaTeX 准备阶段笔记

`main.tex` 是可持续修改的中文调研笔记，引用数据统一来自 [`literature/references.bib`](../../literature/references.bib)。这里先保持简洁、易改；正式题目、导师要求和研究结果明确后再迁移到 [APS 官方 REVTeX 4.2 模板](https://journals.aps.org/revtex/revtex-faq)的 PRL 版式，**不应把当前笔记误认为已可投稿的 PRL 稿件**。

## 本地编译

在项目根目录的 PowerShell 中运行：

```powershell
$buildDir = Join-Path (Resolve-Path -LiteralPath 'thesis/notes').Path 'build'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$env:PAR_GLOBAL_TEMP = $buildDir
$env:TEMP = $buildDir
$env:TMP = $buildDir
latexmk -cd -xelatex -interaction=nonstopmode -halt-on-error -outdir=build thesis/notes/main.tex
```

本机 `C:\Windows\Temp` 的访问权限有问题，以上设置使 Biber 的临时文件落在项目内的 `build` 目录。生成的 PDF 位于 `thesis/notes/build/main.pdf`，整个 `build` 目录不提交 Git。

若需清理编译中间文件，先确认目标确实是本目录下的 `build`；不要删除 `main.tex` 或引用库。

## 修改约定

1. 新增论文先在 `literature/reading-list.md` 记录出处、用途与阅读状态，再添加唯一 BibLaTeX 条目。
2. 正文用 `\cite{引用键}`，不要手打编号；更新论文版本时保留引用键稳定。
3. 每条物理结论写清模型是平衡基态、模拟有效基态还是驱动耗散稳态。
4. 正式写作前逐句核对原论文图号/公式、学校格式要求和文献争议。
