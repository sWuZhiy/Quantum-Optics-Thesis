# FT-TC 有界有限温预研：从正常态到全局等能筛查

日期：2026-11-22。研究对象是 [`theory/model.md`](../../../theory/model.md) 的**平衡有效哈密顿量**，取 `ℏ=k_B=1`、`ω=1`、`J=-0.2`（铁磁）。这里记录求解器校准和少数截面，不是审查通过的有限温相图、真实无驱动腔平台证明或开放系统稳态相图。

## 复现与版本

- 执行时 Git `HEAD=93578ed498c99b17acd7ac5e8ef59d380232ef30`；本轮新脚本在运行时未提交，故以源码 SHA-256 固定版本。`ft_tc_thermal_threshold.py`: `A100EC059DA091D4D5CF5C19476CEE6FAA8F0A4B5BA5D055A3642186C3A6A074`；`ft_tc_ed.py`: `C9F64B4CB9E2EBAFF19EC3E8098D00DA115F6CD1CCF907B85CF2B4F6242DAD59`；`ft_tc_nlce.py`: `B575E60B7758895AA765BD46DA3B779E4A0FE62F21B7CC324DB8CE6035009EFD`；`ft_tc_normal_curvature.py`: `1BB926F2F347E6230C736A211C832C61CFAB37286705308CD303684424E262D7`；`ft_tc_transfer.py`: `B61CCD212A593DAFC4BC3042C22FF4412C423DC810DB88B0905E55344C91B21E`；`ft_tc_landscape.py`: `879E9401918D471394DD5100FCB43593D3DB2235C6D821FCABB21288FB611085`。阈值 JSON 内还保存各依赖的哈希、完整命令参数、耗时与 `seed=null`。本轮没有随机数。
- 项目解释器：`D:\codex\quantum-optics-env\python.exe`，Python 3.12.13、NumPy 2.5.3；未安装新包。工作目录为仓库根目录。数据由脚本标准输出转存到本目录 JSON，未改动 `data/raw/`。
- 所有阈值 JSON 的 `g_equal` 用同一温度的 `f_spin(T,0)-f_spin(T,h)` 构造。ED 采用同一 `N` 的两个自由能；NLCE 的正常态用无限链经典转移矩阵精确值。公式与其适用范围见[模型文档](../../../theory/model.md)。

示例命令（PowerShell；其余文件的全部参数见各 JSON 的 `parameters`）：

```powershell
$py = 'D:\codex\quantum-optics-env\python.exe'
& $py code/src/ft_tc_normal_curvature.py --T 0.05 0.1 0.2 0.3 0.4 0.5 --J -0.2 --Delta 0.2 --omega 1 --g 0.49556 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-entry/normal-curvature-Delta0.2.json
& $py code/src/ft_tc_landscape.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --g 0.49 --points 31 --solver ed --N 8 10 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-entry/landscape-T0.1-g0.49-N8-N10.json
& $py code/src/ft_tc_thermal_threshold.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --method ed --N 10 12 --h-values 0.605 0.61 0.615 0.62 0.625 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-entry/threshold-T0.1-ED-N10-N12-fine.json
& $py code/src/ft_tc_thermal_threshold.py --T 0.1 --J -0.2 --Delta 0.2 --omega 1 --method nlce --L 10 11 12 --h-values 0.605 0.61 0.615 0.62 0.625 | Set-Content -Encoding utf8 results/runs/2026-11-22-ft-tc-t-entry/threshold-T0.1-NLCE-L10-L12-fine.json
& $py -m unittest discover -s code/tests -v
```

## 本轮已查截面

`g_local` 是**解析的无限链正常态局部失稳值**，不是一级线；`g_equal` 是已列横场网格中的最低正常/有限位移等能耦合，若网格最低落在边端，不能解释为内点极小。表内 NLCE 为 `L=10–12` 末三阶 Aitken 加速，ED 为周期链；两者接近不是严格误差界。

| `T` | `Δ` | `g_local` | 有限横场网格结果 | 判读 |
| ---: | ---: | ---: | --- | --- |
| 0.1 | 0.2 | 0.499938849 | `h=0.615`：ED `N=12` 为 `0.495468365`；NLCE `L=12` 原序列 `0.495468654`、加速 `0.495468374` | 宽网格与细网格均有内点最低；与局部值相差约 `0.00447`，支持本截面的一级信号，尚非连续 `h` 相界定位 |
| 0.2 | 0.2 | 0.494014784 | `h=0.5`：ED `N=12` 为 `0.492020881`；NLCE `L=12` 原序列 `0.492024361`、加速 `0.492021056` | 检查的 `h` 内点最低，比局部值低约 `0.00199`，支持一级信号；未连续搜索 |
| 0.3 | 0.2 | 0.489095004 | ED `N=8,10` 的 `0.05≤h≤1.2` 网格最低在左端；NLCE 加速在已查 `h=0.05` 为 `0.489129534` | 小 `h` 的原 NLCE `L=10→12` 从 `0.495014570` 移到 `0.490158462`，加速与原序列差仍明显；此温度不能判跃迁阶数或热三临界点 |
| 0.1 | 0.4 | 0.547719317 | ED `N=8,10` 的 `0.05≤h≤1` 网格最低在左端 `0.547719377` | 处于零温三临界比值；只见局部阈值附近的粗筛，未证明有限温三临界位置 |
| 0.1 | 0.6 | 0.591607817 | ED `N=8,10` 的相同网格最低在左端 `0.591626719` | 连续侧粗筛，真实下确界可能位于 `h→0` |

`T=0.1,Δ=0.2` 的两幅完整允许位移范围 `0≤φ≤g/ω` 的 31 点 ED 景观：`g=0.49` 网格最低在 `φ=0`，`g=0.50` 在 `φ=0.35`；`N=8→10` 全网格最大 `Φ` 差约 `1.91×10⁻⁶`，两次运行各约 10.7 秒。它们验证宽耦合两侧，却无法排除狭窄额外驻点。阈值扫描在这一截面 `h=0.615` 的周期链 `N=10→12` 变化 `1.17×10⁻⁷`，NLCE 加速与 ED `N=12` 差 `8.99×10⁻⁹`；后者只是数值一致性，不能据此报九位有效数字的物理相界。

正常态曲率的三个 JSON 覆盖 `Δ=0.2,0.4,0.6` 与 `T=0.05–0.5`。例如 `Δ=0.2` 的 `g_local` 在 `T=0.1,0.2,0.3,0.4,0.5` 依次为 `0.499939,0.494015,0.489095,0.507255,0.539470`；这只是**局部阈值**随温度变化，不证明全局相界重入。

## 文件与下一项验收

- `normal-curvature-Delta0.2/0.4/0.6.json`：解析正常态，完整输入和温度表。
- `landscape-T0.1-g0.49/g0.50-N8-N10.json`：全允许位移粗网格。
- `threshold-T0.1-ED-N8-N10-coarse.json`、`threshold-T0.1-ED-N8-N10-N12-refine.json`、`threshold-T0.1-ED-N10-N12-fine.json` 与对应两份 `NLCE-L10-L12-refine/fine.json`：一级侧横场网格逐层细化。
- `threshold-T0.2-Delta0.2-ED-N8-N10.json`、`threshold-T0.2-Delta0.2-ED-N10-N12.json`、`threshold-T0.2-Delta0.2-NLCE-L10-L12.json`：第二个温度的有限横场证据。
- `threshold-T0.3-Delta0.2-ED-N8-N10.json`、`threshold-T0.3-Delta0.2-NLCE-L10-L12.json` 与 `threshold-T0.1-Delta0.4/0.6-ED-N8-N10.json`：向潜在阶数变化区的粗筛，尚不足以确定热拓扑。

下一步：对每条截面连续搜索**全部** `h` 驻点和 `0≤φ≤g/ω` 分支；在 `T≈0.3,Δ=0.2` 的小 `h` 区先补可靠的无限链自由能或四次响应，确认原 NLCE 与加速值是否收敛；再扩温度与 `Δ/J`。若 `L≤12` 不足，考虑有限温 MPS 纯化并保存配分函数的归一化尺度，用 ED/NLCE 双重基准。不得由这五条粗筛直接画可投稿热相图。
