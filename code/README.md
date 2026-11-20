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

启动顺序：先完成 `theory/model.md` 和 B1–B3 的解析基准，再实现 `model.py`、`ed.py` 及独立极限检查。通过后增加观测量和扫描入口；具体任务见[执行路线](../project/roadmap.md)。不要用空模块或未执行的示例命令代表完成。

程序输出写到 `results/runs/<日期>-<任务编号>-<短名称>/`。同一脚本接收配置文件，避免为每组参数复制一份程序。探索 notebook 要能从保存的输入重跑；成为论文依据的计算和绘图流程整理到 `src/`，不依赖 notebook 的隐藏执行状态。
