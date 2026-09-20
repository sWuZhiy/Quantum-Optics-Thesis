# 代码

- `src/`：可复用的仿真、数据处理和绘图代码。
- `notebooks/`：探索性计算与可视化。
- `tests/`：针对解析极限、已知结果或数值收敛的验证。
- `configs/`：首次实现运行入口时建立；保存提交 Git 的小型输入配置。运行时将解析后的实际参数另存到对应运行目录，避免后来改配置失去历史依据。

## 已建立的 Python 环境

2026-09-20 使用本机 `D:\Anaconda\package\Scripts\conda.exe` 创建独立 Conda 环境 `quantum-optics-thesis`，当前解释器为 Python 3.12.13，路径是 `C:\Users\23317\.conda\envs\quantum-optics-thesis\python.exe`。已执行解释器和 `pip` 检查；数值包尚未安装，数值程序尚未实现。项目所需的最小环境声明见 [environment.yml](environment.yml)，以后增加经过实际验证的依赖。

在 **Anaconda Prompt / cmd** 中运行：

```bat
call "D:\Anaconda\package\condabin\conda.bat" activate quantum-optics-thesis
python --version
python -c "import sys; print(sys.executable)"
```

在 **PowerShell 或 Codex 命令行** 中可直接调用解释器，不依赖 `conda init` 或当前 PATH：

```powershell
& 'C:\Users\23317\.conda\envs\quantum-optics-thesis\python.exe' --version
& 'C:\Users\23317\.conda\envs\quantum-optics-thesis\python.exe' -c 'print(sum(range(10)))'
```

本机的 `conda` 未加入普通 PowerShell 的 PATH。需要调用 Conda 时用 `& 'D:\Anaconda\package\Scripts\conda.exe' ...`。在 Codex 当前 Windows 沙箱里，Conda 的硬件探测或激活命令创建临时文件时会遇到权限限制；此处优先使用上面的解释器绝对路径，已实际验证可运行。普通用户终端可用 Anaconda Prompt 的激活方式。环境建在用户的 Conda 目录，GitHub 同步的是 `environment.yml`，不是环境本体；无需重新安装 Anaconda。

第一版数值工作计划采用 Python 稀疏 ED。实施 C1 时检查 `numpy`、`scipy` 等实际需求，固定依赖版本并补上可运行的程序命令；不要在数值包尚未安装时将模型测试记为完成。

启动顺序：先完成 `theory/model.md` 和 B1–B3 的解析基准，再实现 `model.py`、`ed.py` 及独立极限检查。通过后增加观测量和扫描入口；具体任务见[执行路线](../project/roadmap.md)。不要用空模块或未执行的示例命令代表完成。

程序输出写到 `results/runs/<日期>-<任务编号>-<短名称>/`。同一脚本接收配置文件，避免为每组参数复制一份程序。探索 notebook 要能从保存的输入重跑；成为论文依据的计算和绘图流程整理到 `src/`，不依赖 notebook 的隐藏执行状态。
