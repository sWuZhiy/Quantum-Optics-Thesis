# Project instructions for Codex

- 与用户默认使用中文交流；专业术语首次出现时可附英文名称。
- 项目目标以 `project/brief.md` 为准。该文件中的待定项不能擅自当作已确认要求。
- 阅读或引用文献时核对原文，标明作者/年份或 DOI，以及关键结论所在的页码、公式或图号；区分论文报告的结果、作者的解释和我们的推断。
- 明确区分真实系统的平衡超辐射相变、受驱动开放系统的稳态相变，以及量子模拟器中有效哈密顿量的基态性质。
- 推导写明哈密顿量、参数定义、近似、适用范围和所用单位；改变符号约定时同步更新相关说明。
- `data/raw/` 中的原始数据不可覆盖。处理流程应从原始数据生成 `data/processed/`；计算记录写入 `results/runs/`，包含代码版本、参数、随机种子和运行说明。
- 探索性 notebook 可以放在 `code/notebooks/`；需要重复使用的计算和绘图逻辑应整理到 `code/src/`。
- 本机项目解释器位于 `D:\codex\quantum-optics-env\python.exe`。安装项目 Conda 依赖时用环境的 `--prefix`，并把该命令会话的 `CONDA_PKGS_DIRS` 设为 `D:\codex\quantum-optics-conda-pkgs`；不要误用 PATH 中另一套 Python 或把新环境建回 C 盘。
- 不编造数据、引用或实验结果。数值结论应进行适当的收敛、极限或基准检查，并说明验证边界。
- 论文中的每张最终图应能追溯到生成脚本和输入。只把审查过的图放入 `results/figures/`。
- 对项目结构或研究方向有实质影响的选择记入 `project/decisions.md`；完成阶段性工作后更新 `project/progress.md`。
