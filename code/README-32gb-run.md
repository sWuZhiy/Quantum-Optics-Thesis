# FT-TC 32GB 外部运行包

## 要跑什么

当前最有科研价值的 32GB 任务是把重入窄袋的周期热 ED 从 `N=12` 延伸到
`N=14`。`N=14` 的 Hilbert 空间维数为 16384，单个 `float64` 稠密矩阵正好
是 2 GiB，LAPACK 对角化还会使用矩阵副本和工作区。脚本采用 10 GiB 的启发式
峰值估计，并默认要求开跑前至少有 20 GiB 可用物理内存。

优先顺序：先跑 `Delta=.4001`；成功返回后再串行跑 `.4002` 和 `.40024`。
不要同时启动多个实例。曾经的 `M=24` 转移矩阵不列入本次任务，因为它的外推系统
误差已比目标端点信号大三至五个数量级，增加内存不会让它成为有效裁判。

## 1. 复制项目并建立环境

在 Windows PowerShell 中进入项目根目录。以下路径只是示例，可换到同学自己的磁盘：

```powershell
$env:CONDA_PKGS_DIRS = 'D:\quantum-optics-conda-pkgs'
conda env create --prefix 'D:\quantum-optics-32gb-env' `
  --file code/environment-32gb.yml
```

检查环境和 BLAS：

```powershell
conda run --prefix 'D:\quantum-optics-32gb-env' `
  python -c "import numpy as np; print(np.__version__); np.show_config()"
```

脚本只依赖 Python 标准库和 NumPy，不需要 CUDA、SciPy、TeNPy 或 Jupyter。

## 2. 先做无计算预检

```powershell
conda run --prefix 'D:\quantum-optics-32gb-env' `
  python code/src/ft_tc_32gb_reentrant_ed.py --dry-run
```

应看到 `N=14`、2 GiB 原矩阵、10 GiB 启发式峰值、当前总内存和可用内存。
若可用内存低于 20 GiB，先关闭浏览器、游戏和其他计算程序；不要直接使用
`--force-memory`，除非已经确认系统不会发生交换或内存溢出。

## 3. 先跑最重要的 `.4001`

```powershell
conda run --prefix 'D:\quantum-optics-32gb-env' `
  python code/src/ft_tc_32gb_reentrant_ed.py `
  --Delta 0.4001 --N 14 --threads 8
```

完成后应生成：

```text
results/runs/2026-11-23-ft-tc-32gb-n14/ed-N14-Delta0.4001.json
```

JSON 保存参数、`g_equal-g_local`、与既有 `N=8,10,12`/NLCE 的差、运行时间、
峰值进程内存、Python/NumPy 版本、线程设置和全部输入源码哈希。中断不会破坏其他
截面的结果；已完成文件默认跳过。

## 4. `.4001` 成功后再跑靠近端点的两点

```powershell
conda run --prefix 'D:\quantum-optics-32gb-env' `
  python code/src/ft_tc_32gb_reentrant_ed.py `
  --Delta 0.4002 0.40024 --N 14 --threads 8
```

这两个点可能仍受双精度自由能相减限制。即使 `N=14` 顺利结束，也不能仅凭更大
有限环把局部切触端点称为已验证的热力学极限相界。

## 5. 返回哪些文件

请把下面目录内生成的 JSON 原样发回，不要手工改数值：

```text
results/runs/2026-11-23-ft-tc-32gb-n14/
```

同时告知 CPU 型号、实际内存容量、操作系统，以及运行期间是否还开着其他大型程序。
不需要发送 Conda 环境目录或任何个人文件。
