# 代码

- `src/`：可复用的仿真、数据处理和绘图代码。
- `notebooks/`：探索性计算与可视化。
- `tests/`：针对解析极限、已知结果或数值收敛的验证。
- `configs/`：首次实现运行入口时建立；保存提交 Git 的小型输入配置。运行时将解析后的实际参数另存到对应运行目录，避免后来改配置失去历史依据。

## 已建立的 Python 环境

2026-09-20 创建独立 Conda 环境，随后迁至 **`D:\codex\quantum-optics-env`**。当前解释器为 Python 3.12.13，`pip` 已验证；与原 C 盘环境的 20 个包版本及构建号一致，原环境已移除。2026-11-20 已用现有 NumPy 2.5.3 实现一个 P0 有限温物质链转移矩阵试点；SciPy 和张量网络包仍未安装。最小环境声明见 [environment.yml](environment.yml)，以后增加经过实际验证的依赖。环境与仓库分开放，避免提交大体积程序文件。

在 **Anaconda Prompt / cmd** 中运行：

```bat
call "D:\Anaconda\package\condabin\conda.bat" activate "D:\codex\quantum-optics-env"
python --version
python -c "import sys; print(sys.executable)"
```

在 **PowerShell 或 Codex 命令行** 中可直接调用解释器，不依赖 `conda init` 或当前 PATH：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' --version
& 'D:\codex\quantum-optics-env\python.exe' -c 'print(sum(range(10)))'
```

本机的 `conda` 未加入普通 PowerShell 的 PATH。需要调用 Conda 时用 `& 'D:\Anaconda\package\Scripts\conda.exe' ...`，并用 `--prefix 'D:\codex\quantum-optics-env'` 指定环境；不能再用旧的 C 盘路径或仅凭环境名安装。项目专用包缓存已建立在 `D:\codex\quantum-optics-conda-pkgs`。**每次安装依赖前**，在该 PowerShell 会话设定 `$env:CONDA_PKGS_DIRS='D:\codex\quantum-optics-conda-pkgs'`，再运行 Conda 安装命令，避免新包缓存落到 C 盘。在 Codex 当前 Windows 沙箱里，Conda 的硬件探测或激活命令创建临时文件时可能遇到权限限制；直接使用上面的解释器绝对路径已验证可运行。GitHub 同步的是 `environment.yml`，不是环境本体。

P0 有限温试点可直接重跑：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_transfer.py --T 0.5 --J -0.3 --Delta 1 --h 0.8 --M 10 12 14 16 18 20
& 'D:\codex\quantum-optics-env\python.exe' -m unittest discover -s code/tests -p 'test_ft_tc_transfer.py' -v
```

命令从仓库根目录运行；输出是固定虚时间片数 `M` 下的无限长混合场 Ising 链自由能，仍须 `M→∞` 外推。参数、验证和失败边界见[本次运行记录](../results/runs/2026-11-20-ft-tc-p0/README.md)。后续稀疏 ED 若需要 SciPy，先按实际需求固定依赖版本；不把本次单点试算当成目标相图完成。

2026-11-22 的 Z2 零温校准使用现有 NumPy，无新依赖：`ft_tc_zero_t.py` 给 `Δ=0` 可积链精确积分和 Koziol 三临界系数对照；`ft_tc_ground_state.py` 用矩阵自由 Lanczos 算 `N≤18` 物质链基态能、残差和可选交错磁序平方；`ft_tc_zero_t_scan.py` 扫横场的全局等能候选与指定 `g` 的腔位移能量。示例：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_zero_t.py --J -0.2 --omega 1 --Delta 0.2 0.4 0.6
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_ground_state.py --J 0.2 --Delta 0.6625 --h 0.07 --N 12 16 18 --staggered-m2
& 'D:\codex\quantum-optics-env\python.exe' -m unittest discover -s code/tests -v
```

共 18 项自动基准通过；`N=18,maxiter=160` 的 Lanczos 基底默认最多预分配约 320 MiB，建议串行运行大尺寸。参数映射、已发表结果与所有实际运行命令见[Z2 记录](../results/runs/2026-11-22-ft-tc-z/README.md)。这仍是有限尺寸零温校准，完整相界和有限温研究未完成。

2026-11-22 已开始有界有限温预研。[`ft_tc_thermal_threshold.py`](src/ft_tc_thermal_threshold.py)按 `h=4gφ` 计算正常态与有限横场态的等能耦合，支持 `--method ed`（周期热 ED）或 `--method nlce`（开链簇展开）；同时输出解析正常态局部阈值、参数、源码哈希和耗时。示例：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_thermal_threshold.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 10 12 --h-values 0.605 0.61 0.615 0.62 0.625
& 'D:\codex\quantum-optics-env\python.exe' -m unittest discover -s code/tests -v
```

含新脚本共 20 项自动检查通过；全部已运行温度与误差限制见[热预研记录](../results/runs/2026-11-22-ft-tc-t-entry/README.md)。有限 `h` 网格最低值不是连续全局相界，`T≈.3` 的小场 NLCE 尚未收敛。

随后增加 [`ft_tc_thermal_refine.py`](src/ft_tc_thermal_refine.py)：在已由宽网格找到的单个 `h` 括区内，对 `g_equal(h)` 作黄金分割细化，输出每次评价的物质自由能和最终括区。示例：

```powershell
& 'D:\codex\quantum-optics-env\python.exe' code/src/ft_tc_thermal_refine.py --T 0.2 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 12 --lo 0.42 --hi 0.54 --tol 0.003
& 'D:\codex\quantum-optics-env\python.exe' -m unittest discover -s code/tests -v
```

目前全套 22 项测试通过；`T=.1/.2` 预选括区和 `T=.3` 小场的误差记录分别见[连续细化](../results/runs/2026-11-22-ft-tc-t-continuous/README.md)与[小场核查](../results/runs/2026-11-22-ft-tc-t-smallfield/README.md)。单括区优化和加速 NLCE 一致性都不能单独证明全局热相界。

启动顺序：先完成 `theory/model.md` 和 B1–B3 的解析基准，再实现 `model.py`、`ed.py` 及独立极限检查。通过后增加观测量和扫描入口；具体任务见[执行路线](../project/roadmap.md)。不要用空模块或未执行的示例命令代表完成。

程序输出写到 `results/runs/<日期>-<任务编号>-<短名称>/`。同一脚本接收配置文件，避免为每组参数复制一份程序。探索 notebook 要能从保存的输入重跑；成为论文依据的计算和绘图流程整理到 `src/`，不依赖 notebook 的隐藏执行状态。
