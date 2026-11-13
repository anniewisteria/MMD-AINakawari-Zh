# AI中割（MMD-AINakawari）中文说明

> **关于中文版**：本仓库已汉化 —— 界面、日志、安装设置全中文，并兼容
> 「MMDZh 汉化的 MMD 9.32 x64」（前提是 exe 本体未被修改）。
> 中文改动共 12 个文件 + 1 个已编译的 DLL + 一键部署 bat，见 `zh_补丁包\`
> （部署方法：把补丁包放到 `MikuMikuDance.exe` 同目录，双击「一键部署中文版.bat」）。
> 2026-11-13 第二版 DLL 修复：重开工程后右下角面板偶尔变黑块、需鼠标划过才恢复的问题。

English: [README_en.md](README_en.md) ／ 日文原版: [README_Jap.md](README_Jap.md)

MMD（MikuMikuDance）和 MMM（MikuMikuMoving）里打好的关键帧与关键帧之间的空隙，由 AI 自动补间（中割り）填满。
只需在时间线上选中关键帧，按「生成」。中间帧的关键帧会直接写进时间线。

![MMD 右下角的简易操作面板](docs/images/panel_in_mmd.png)

内部生成动作的是 NVIDIA 的两个模型：

- **Kimodo**：根据英文句子（提示词）生成动作。在经过你打的关键帧姿势的同时，用「跳舞」「挥手」等动作填满空隙
- **MotionBricks**：不需要提示词，生成关键帧到关键帧之间的自然补间

| 生成前（在 30・60・90F 打了关键帧） | 生成后（重做了 30〜90F） |
|---|---|
| ![生成前](docs/images/timeline_before.png) | ![生成后](docs/images/timeline_after.png) |

> [!NOTE]
> 本项目是与 NVIDIA 无关的个人作品。

## 能做什么

| | 内容 |
|---|---|
| **AI 补间（MotionBricks）** | 不用提示词，连接关键帧之间（17〜57 帧）的空隙。可选「每个关键帧都停一下／保持惯性通过」「只有手腕用普通补间」 |
| **用提示词生成（Kimodo）** | 用英文句子指定动作，填充关键帧之间。每段可以写不同的句子（`run / 45: stop` 表示 45F 开始 stop）。详细窗口里还能「续写」（在最后一个关键帧后面加动作）或「仅用提示词生成」 |
| **示例提示词** | 不擅长英语也能从「向前走：A person walks forward.」这样的列表里选（7 类・44 条，中文版里分类和动作名已翻成中文，英文句子保留） |
| **只重做选中的关键帧之间** | 从时间线上选中的第一个到最后一个关键帧为止重做。范围外的动作连同补间曲线一起保留，范围两端与外部动作自然衔接 |
| **关键帧以外的线索**（Kimodo） | 只有「全亲」的关键帧当作「腰经过此处」的标记；只有脚 IK・腕 IK 的关键帧当作「手脚到达此处」的标记（MotionBricks 补间不使用） |
| **平滑停止** | 最后一个关键帧不会戛然而止，由 MotionBricks 自然减速停下 |
| **把走出的位移放到全亲**（Kimodo） | 把提示词让模型走出的移动量・转向量放到「全亲」的关键帧上，中心骨只留下走路的晃动。之后只动全亲就能改变走的位置和朝向 |
| **撤销** | 一次回到生成前的动作 |
| **中断生成** | 生成中「生成」按钮会变成「中断」。按下即停止生成，关键帧保持按下前的状态 |

## 运行环境

| | 需要什么 | 已验证的环境与用户报告 |
|---|---|---|
| OS | Windows 10／11（64bit） | Windows 11 |
| 软件 | MikuMikuDance 9.32 x64（日文版。英语模式也可以），或 MikuMikuMoving 1.2.9.2（64bit・附赠・试验版） | MMD 9.32 x64・MMM 1.2.9.2。**中文版另支持运行时汉化插件（如 MMDZh），前提是 exe 本体未被修改** |
| GPU | NVIDIA GTX 16 系／RTX 20 系以后。驱动用新版。其他 GPU 见下方「GPU 计算方式」 | RTX 3090（24GB）。有 GTX 1650（4GB）也能跑的报告 |
| 运行库 | [Microsoft Visual C++ 可再发行程序包（x64）](https://aka.ms/vs/17/release/vc_redist.x64.exe)。没装的话，安装设置会引导你 | |

安装方式不同，需要的容量不同。安装设置里取消勾选「自由书写提示词」，就可以不装读取提示词的 Llama 3（约 8GB），只用示例句子生成（之后也可以再装）。

| | 全部安装 | 只用示例句（不装 Llama） |
|---|---|---|
| 显存 | 6GB 以上（实际占用约 2.6GB） | 4GB 以上 |
| 内存 | 16GB 以上（读取提示词约用 8GB） | 8GB 以上（尚未验证） |
| 硬盘 | 约 21GB（Kimodo 约 15GB・MotionBricks 约 6GB） | 约 13GB |
| 下载量（仅安装时） | 约 12GB | 约 4GB |

- AI 部分实际占用：内存约 2.1GB（Kimodo 1.7GB・MotionBricks 0.4GB）、显存约 2.6GB（11-10 实测值）。验证用的电脑是 64GB 内存，也有 16GB 内存能跑的报告
- 提示词读取在 CPU 上运行（一句约 0.5 秒）。用过的内存会在关闭全部 MMD/MMM 或闲置 5 分钟后释放
- 装好后内存不够时，在详细窗口取消勾选「使用提示词读取（Llama 3）」，不用删除就能变成只用示例句的模式
- **8GB 内存的电脑尚未验证。跑通/跑不通都欢迎反馈**
- 详细窗口「Kimodo」标签页下方会显示这台电脑的 GPU 和内存能否运行

### GPU 计算方式

安装设置最后的「试做一次」会从上到下依次尝试这台电脑能用的方式，并记住通过的那一种。不需要手动选择。

| 方式 | 使用的 GPU | 速度参考 |
|---|---|---|
| CUDA | NVIDIA GPU（GTX 16 系／RTX 20 系以后） | 2 秒动作约 3 秒 |
| DirectML（0.3.0 起・试验性） | 支持 DirectX 12 的 GPU（AMD Radeon、Intel Arc 或核显、NVIDIA GTX 10 系等） | RTX 3090 与 CUDA 相同（2 秒动作 3 秒・10 秒动作 7 秒） |
| 不用 GPU | 不使用（纯 CPU） | 2 秒动作约 40 秒・10 秒动作 2〜4 分钟（Core i7-12700F） |

- 无论哪种方式，生成的动作质量都相同（同样的计算换不同的工具执行）
- DirectML 首次使用要转换模型（约 1 分钟），多占约 2GB 硬盘，Kimodo 内存约 3GB
- 当前用哪种方式显示在详细窗口「Kimodo」标签页下方的判定里（DirectML・不用 GPU 时）
- Intel 核显（Iris Xe・16GB 内存笔记本）有 DirectML 跑通的报告（据说比较耗时）
- **AMD GPU、Intel Arc、GTX 10 系的真机尚未验证。跑通/跑不通都欢迎反馈**（附上「故障排查」里提到的记录文件更好定位）

## 安装

MMD 和 MMM 用同一个 zip。`AIナカワリ導入.cmd` 会自动识别解压目录里是 `MikuMikuDance.exe` 还是 `MikuMikuMoving64.exe` 并装入。

### 1. 下载 zip 并解压到 MMD（MMM）文件夹
从 [Releases](https://github.com/BeamManP/MMD-AINakawari/releases) 的「Assets」下载 `MMD-AINakawari-<版本>.zip`（约 70MB）。
下方的「Source code (zip)」和页面绿色「Code」→「Download ZIP」是程序源码，里面没有 `AIナカワリ導入.cmd`。
**先关闭 MMD（MMM）**，把 zip 内容解压到 `MikuMikuDance.exe`（MMM 则是 `MikuMikuMoving64.exe`）所在的文件夹。内容是这 3 样：

```
AIナカワリ導入.cmd
MMD-AINakawari\          AI中割 本体（Python 和程序。MMM 用的 DLL 也在里面）
plugin\MMD-AINakawari\   给 MMD 加载的 DLL（MMM 时导入.cmd 会收拾掉）
```

### 2. 双击 `AIナカワリ導入.cmd`
弹出黑色窗口，自动装进找到的那个。「できました」（完成了）出现后按任意键关闭。

| | MMD 时 | MMM 时 |
|---|---|---|
| 放置内容 | 把 MMDPlugin（`MMDPlugin.dll`・`d3d9.dll`・`d3dx9_43.dll`）放到 `MikuMikuDance.exe` 旁边。已装 MMDPlugin 则不改动 | 把按钮・面板的 DLL 和与 MMM 通信的桥（MmmBridge）放进 MMM 的 `Plugins\`。不放置 MMDPlugin |
| MME | 已装 MME 时，把 MME 的文件（`d3d9.dll`・`MMEffect.dll` 等）移到 `plugin\mme\`。按 MMDPlugin 说明书的「同时使用 MME」摆法，MME 照常工作 | 无关 |
| 什么都不动就停止时（黑窗口里显示原因） | MMD 正在运行／MMD 不是 9.32 x64 日文版／存在既不是 MME 也不是 MMDPlugin 的 `d3d9.dll` 或 `d3dx9_43.dll` | MMM 正在运行／MMM 不是 1.2.9.2（64bit） |

- 出现 Windows「无法验证发布者」等警告时，按「运行」
- zip 解压到了 MMD・MMM 文件夹之外时，会弹出文件夹选择窗口，复制到所选文件夹
- 同一文件夹里同时有 MMD 和 MMM 时，黑窗口里会问装到哪个
- 插件底座 [MMDPlugin](https://bowlroll.net/file/121761)（ver0.41 64bit・おいがみ 制作）已包含在 zip 里

### 3. 启动并运行安装设置
1. 打开 AI中割 的详细窗口
   - MMD：菜单栏「AI中割」→「打开 AI中割 窗口」（日文版为「AIナカワリ」→「AIナカワリの窓を開く」）
   - MMM：工具栏的「**AI中割**」按钮
2. 按窗口下方的「**安装设置**」（セットアップ）
3. 决定安装位置（默认是剩余空间最多的盘的 `\AINakawari`）。请使用**只有半角英数字**的文件夹
4. 阅读许可协议，勾选「同意并安装」，按「**开始安装设置**」

接下来会下载并安装 Kimodo、MotionBricks 和运行它们的 Python，最后各试做一次确认。下载量约 12GB。

- 时间视网速 20 分钟〜2 小时。最耗时的是「搭建 Kimodo 的 Python 环境」（约 5GB）和读取提示词的模型（约 8GB）
- 进行中时，窗口下方的蓝字会显示「已用时间」和「至此已下载安装的量」。数字在涨就说明在正常推进
- 通信中断时会稍等片刻自动从断点重试。仍然停止时，稍等片刻再按一次「安装设置」
- 即使中途停止（失败・中止・电脑重启），再按一次「安装设置」就会从停下的那一步继续
- 安装设置窗口关掉后仍在后台进行。再按一次「安装设置」就能唤出

出现简易操作面板就可以使用了（MMD 是下排右侧的「AI中割 简易操作」，MMM 在左侧「插件」标签页里）。

![MMD 下排的简易操作面板](docs/images/bottom_strip.png)

## 用法

### 简易操作面板

![简易操作面板](docs/images/panel.png)

1. 选择模型，像平常一样摆姿势、打关键帧
2. 在时间线上**选中想重做范围的最初和最后的关键帧**（框选，或用 MMD 时间线下方的「范围选择」。选哪根骨骼的行都行）。面板会显示「选中关键帧 30〜90F」
3. 左上选择生成方式
   - **Kimodo**：在提示词（英文）里写动作。不会写就从「**示例 ▼**」里选
   - **MotionBricks**：不需要提示词（输入框变灰）
4. 按「**生　成**」（或在提示词框里按 Enter）。下方一行显示「生成中…」→「完成了」后，播放确认
5. 不满意就按「**撤销**」，或改提示词再「生成」

- 生成中「生成」会变成「**中断**」。发现选错范围或提示词写错时按下，即停止生成。关键帧保持原样。开始写回 MMD 后无法按下，那时等结束后用「撤销」
- 面板的「生成」按「填充关键帧之间」生成。其他生成方式和 seed 等详细设置在「**详　细**」窗口里
- 范围为「选中关键帧之间」（默认）时，选中 2 个以上关键帧前「生成」不可按。在详细窗口把范围改成「全部」后，面板也会对全部关键帧生成（面板的字变成「全部关键帧」）
- 在提示词框里输入时，MMD 的快捷键无效。点击框外（时间线等）或按 Esc 返回
- 相机・灯光・附件模式下不显示面板
- MMM 里，生成的动作按 **Ctrl+Z 一次**也能回到生成前

![示例列表](docs/images/samples.png)

### 详细窗口（面板的「详　细」，或 MMD 菜单・MMM 按钮）

![详细窗口](docs/images/window.png)

| 栏目 | 内容 |
|---|---|
| 标签页 | **Kimodo**（用提示词生成）／**MotionBricks**（无提示词补间）。与面板的选择联动 |
| 想做的事 | **填充关键帧之间**／**续写**（在范围末端之后追加指定帧数。范围是「全部」时在最后一个关键帧之后）／**仅用提示词生成**（不使用关键帧的姿势）／**跟随中心生成**（只让腰的位置和高度跟随中心关键帧与补间，姿势和动作由提示词生成。范围与填充相同） |
| 长度 | 续写时指「追加的帧数」。选 30〜60F 填 100，就生成 61〜160F（窗口里会显示生成范围）。追加位置上如有身体关键帧会红字提示，生成后那些关键帧会被生成的动作覆盖。手指・表情的关键帧保持原样 |
| 关键帧精简 | 只在补间曲线能表达的位置保留生成的关键帧（Kimodo 标签页在「长度」下方，MotionBricks 标签页在「手腕用 MMD 补间」下方）。滑杆共 5 档：**不精简／精细／普通（推荐）／粗糙／非常粗糙**。不精简的话，生成部分几乎每帧都有关键帧（「普通」档下，300 帧动作的整模关键帧从 9807 → 1017 个）。关键帧全身对齐到同一帧放置，该帧没动的骨骼不打。自己打的关键帧・范围两端・范围外的关键帧原样保留。精简数量会写进日志 |
| 全亲 | **承载移动**／**承载朝向**（Kimodo 标签页・默认关）。把走路产生的位移（腰轨迹的平整化）和转向量放进全亲的关键帧，中心骨只留走路的晃动。全亲的关键帧会精简到几个再打，身体外观与不承载时相同。只在「只有起始姿势是确定的」（仅用提示词生成・续写・范围后端没有关键帧的重做）时承载。范围中途或末端有身体关键帧时、以及全亲已有关键帧时照旧不承载，原因写在日志里（面板的「生成」是填充模式，基本不承载）。承载后改长度重做时，请先按「撤销」（上次打的全亲关键帧会被当作腰轨迹的标记读取） |
| 提示词 | 每行表示「从该帧到下一行帧」的动作。「＋ 在当前帧分段」增行。也有「示例 ▼」 |
| 提示词强度・关键帧强度 | 滑杆（0.5〜10）。推荐都是 2，可用「恢复推荐（2・2）」还原。句子动作太弱时把提示词强度调到 3〜5；关键帧前后卡顿时略调高关键帧强度 |
| 高级设置 | 计算次数・seed・后处理（脚底滑动・姿势） |
| 范围 | **选中关键帧之间**（默认）／**全部**（从最初到最后的关键帧） |

提示词和生成方式（Kimodo／MotionBricks）在面板与详细窗口之间共用。任一边改动，另一边同步。

### 出好动作的窍门
- 提示词用英语，「A person ＋ 动词」的形式最有效（例：`A person waves with their right hand.`）。日语基本无效
- 关键帧以 20 个左右为上限。太多会被关键帧束缚，动作变僵硬
- Kimodo 单段最长 300 帧（10 秒）（连接范围外惯性的几帧也算在内，选的范围要比这略短）。更长时分段生成
- 分段点紧后面有关键帧时，为保持连贯，分段点会自动后移 1 帧
- 第一次生成要多花 10〜20 秒加载模型。第二次起约 25 秒（含关键帧精简「普通」）

## 更新・卸载

**更新**：把新版 zip 同样解压覆盖到 MMD（MMM）文件夹，再双击一次 `AIナカワリ導入.cmd`。窗口设置（`MMD-AINakawari\app\work\`）会保留。之后打开「安装设置」，若显示「有更新」就按「更新」（只重做版本变化了的步骤）。

**中文版的更新**：装完新版 zip 后，把 `zh_补丁包\` 里的内容按原路径重新拖进去覆盖（或再跑一次一键部署 bat）。详见下文「中文版补充说明」。

**卸载**：关闭 MMD（MMM）后删除以下内容。

| | 删除的东西 |
|---|---|
| MMD | MMD 文件夹的 `AIナカワリ導入.cmd`・`MMD-AINakawari\`・`plugin\MMD-AINakawari\` |
| MMM | MMM 文件夹的 `AIナカワリ導入.cmd`・`MMD-AINakawari\`，以及 `Plugins\` 的 `MMM-AINakawari.dll`・`MMM-AINakawari.ini`・`MmmBridge.dll`・`MmmBridgeCore\` |
| 两者都要 | 安装设置时选的位置（例：`D:\AINakawari\`） |

MMD 时，MMDPlugin（`MMDPlugin.dll`・`d3d9.dll`・`d3dx9_43.dll`・`plugin\MMDPlugin\`）和移到 `plugin\mme\` 的 MME 会留下。如果没有在用其他 MMDPlugin 插件，删掉 MMDPlugin 的 3 个文件和 `plugin\MMDPlugin\`，把 `plugin\mme\` 里的内容放回 `MikuMikuDance.exe` 旁边即可复原。

## 故障排查

详细窗口「**日志**」→「**打开记录文件夹**」可打开记录文件夹（`MMD-AINakawari\app\work\`）。出问题时，把下面的文件附到 [Issues](https://github.com/BeamManP/MMD-AINakawari/issues) 反馈（**中文版用户也可直接把日志发给帮你汉化的人看**）。

| 文件 | 内容 |
|---|---|
| `app.log`（和 `app.log.1`） | 窗口日志・安装设置日志・失败时错误的详细信息 |
| `Kimodo_server.log`・`llama_server.log` 等以 `_server.log` 结尾的文件 | 后台运行的 Kimodo・提示词读取（llama.cpp）・MotionBricks 的记录（最近一次启动的） |

常见问题：
- **安装设置看起来不动了**：看窗口下方蓝字的时间和量。在涨就是在正常推进（大的部件单个约 2.5GB，视网速一步可能超过 30 分钟）。5 分钟后量仍不涨时，按「中止」再按一次「安装设置」。已完成的步骤会跳过，从断点继续
- **显示「通信似乎中断了」并停下**：稍等片刻再按一次「安装设置」。已下载的内容会保留，从断点继续。不会使用你自己装在别处的 PyTorch 等（安装设置会在安装位置内搭建专用环境）
- **装完却跑不动・中途停止后状态异常**：打开「安装设置」按「**检查并修复**」。它会确认已安装的内容（约 10 秒），只补装缺失的部分。对中途停止的文件夹再跑一次也一样从缺的地方修
- **安装设置的「试做一次」失败**：先更新 GPU 驱动，再按一次「安装设置」
- **换过 GPU**：打开「安装设置」会显示「有更新」，按「更新」。会重新试做，重新选择新 GPU 能用的方式（1〜2 分钟）
- **「空间不足」**：把安装位置换到剩余空间多的盘
- **MMD 一启动就闪退**：检查 `plugin\` 下有没有放了 AI中割 的 DLL 和 ini 之外的东西（比如 Python）。MMDPlugin 会尝试加载 `plugin\` 下的所有 DLL
- **清理 C 盘缓存后插件提示要下载模型**：AI 环境全部装在安装设置选的位置（如 `D:\AINakawari\`），清 C 盘不会删到它。先直接试一次生成；仍不行时打开「安装设置」按「检查并修复」。**不要删除**安装位置里的 `.venv\`・`uv\python\`・`hf_cache\`・`text_encoder\`・`assets\`（详见下文「中文版补充说明」）

## 已知限制
- 只支持 **PMX 模型**（不支持 PMD）。按标准骨骼名（中心・上半身・腕・肘等）寻找骨骼。没有的骨骼（上半身2・颈・单腕等）会跳过生成，日志提示「注意：模型中没有的骨骼已跳过」。**唯独缺少中心・下半身和任意一侧的脚・膝・脚踝**的模型，因身体位置和大小无法确定而停止
- 手指・表情・头发等不生成（保持补间）
- 地面按平坦的一张处理，以**范围内最低关键帧的脚**为地面。只要有一个关键帧的脚陷进地面，其他帧也会相应下沉（日志提示「注意：有脚底比其他关键帧低的关键帧」。请修正脚 IK 的高度）。上下楼梯这种每个关键帧地面高度不同的动作无法直接生成
- 关键帧姿势差异过大时，前臂・手腕可能在 1 帧内大幅转动（补间模式下可用「手腕用 MMD 补间」抑制）
- 只重做选中范围时，范围外的动作按移动 0.05・旋转 0.5° 以内的偏差保留。曲线无法表达的急变处，范围外也可能增加关键帧
- 关键帧精简（「普通」档）允许每根骨骼移动 0.05・旋转 0.5°、手腕・头・脚 IK 等位置 0.06（约 0.5cm）以内的偏差。「精细」是它的一半，「粗糙」是 2 倍，「非常粗糙」是 4 倍。精简会让生成多花几秒（300 帧约 6 秒）。Kimodo 生成的手腕等逐帧细颤的动作，连颤动也一起保留，所以关键帧减不了太多（想减就调「粗糙」）
- 关闭物理演算的关键帧，在生成或撤销后可能变回开启（未确认）
- MMD 只在 9.32 x64 日文版上验证过（有直接读取 MMD 内存的部分，其他版本无法运行）。**中文版在此之上兼容「不改 exe 文件的运行时汉化插件」（如 MMDZh）；若 exe 本体被修改过则无法运行**
- MMM 仅支持 1.2.9.2（64bit）（撤销功能依赖 MMM 未公开的内部结构）。只验证过 1 个模型和 2 个动作。**跑通/跑不通都欢迎反馈**
- MMM 里，改写的只是所选模型最下层动作层的骨骼（不碰表情和其他层）。还不支持从 zip 里加载的模型（会提示后停止）

## 许可与致谢
- 本仓库的代码：[MIT-0](LICENSE)
- 截图中的模型：Tda 式初音未来 V4X（Tda 制作）。模型不随 zip 附带。初音未来是 Crypton Future Media 株式会社的角色
- [Kimodo](https://github.com/nv-tlabs/kimodo)（NVIDIA）：代码 Apache-2.0，模型 [NVIDIA Open Model License](https://huggingface.co/nvidia/Kimodo-SOMA-RP-v1.2)
- [MotionBricks](https://github.com/NVlabs/motionbricks)（NVIDIA）：代码 Apache-2.0，模型 NVIDIA Open Model Agreement
- [Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)（Meta）：[Meta Llama 3 Community License](https://huggingface.co/fernandotonon/Llama-3-LLM2Vec-8B-Kimodo-TextEncoder-GGUF/blob/main/LICENSE-Llama-3.txt)・[使用政策](https://huggingface.co/fernandotonon/Llama-3-LLM2Vec-8B-Kimodo-TextEncoder-GGUF/blob/main/USE_POLICY-Llama-3.md)（Kimodo 读取提示词时使用）。**Built with Meta Llama 3**
- [LLM2Vec](https://huggingface.co/McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp)（McGill-NLP）：MIT
- [Llama-3-LLM2Vec-8B-Kimodo-TextEncoder-GGUF](https://huggingface.co/fernandotonon/Llama-3-LLM2Vec-8B-Kimodo-TextEncoder-GGUF)（fernandotonon 制作）：把 Llama 3 和 LLM2Vec 做成 8bit（GGUF Q8_0）的版本。提示词读取使用它（Meta Llama 3 Community License）
- [llama.cpp](https://github.com/ggml-org/llama.cpp)（ggml-org）：MIT。在 CPU 上运行提示词读取（安装设置下载官方 CPU 版）
- [MMDPlugin](https://bowlroll.net/file/121761)（おいがみ 制作）：随 zip 附带（依据说明书「本体转载限非商用、无需联系」）。`d3dx9_43.dll` 也是 MMDPlugin 的（不是微软 DirectX 的）
- [mmd-mcp](https://github.com/BeamManP/mmd-mcp)（MIT-0 等）
- [mmm-mcp](https://github.com/BeamManP/mmm-mcp)（MIT-0）：MMM 内部的桥（`MmmBridge.dll`・`MmmBridge.Core.dll`）。随 zip 附带
- MikuMikuMoving（Mogg 制作）：MMM 版按钮・面板与桥使用 MMM 的插件接口（`MikuMikuPlugin.dll`）。不附带 MMM 的文件。撤销的实现思路参考 mfakane 的 [MikuMikuMoving-Plugins](https://github.com/mfakane/MikuMikuMoving-Plugins)（WTFPL）
- zip 附带的 Python（python-build-standalone）与 uv 等的许可写在 zip 的 `MMD-AINakawari\THIRD_PARTY.txt`

AI 模型（Kimodo・MotionBricks・Llama 3・LLM2Vec）和 llama.cpp 都不在 zip 和本仓库里
（只有用示例句换算的 44 句・不足 1MB 的提示词读取结果放在 `mmd_ainakawari/text_cache`，让「不装 Llama」的模式也能用）。安装设置会从各自的发布处下载（在安装设置画面同意许可后）。

## 中文版补充说明

**这个仓库改了什么**：
- DLL（菜单・右下角面板・错误弹窗的中文文案 + 兼容汉化 MMD 的菜单定位）—— 已编译好，在 `zh_补丁包\`
- 12 个 Python/文本文件（界面・日志・安装设置全中文的翻译表 + 中文控件兼容层）—— 在 `zh_补丁包\app\`
- **不修改** `python\`、`site-packages\`、`work\`（你的设置和日志），也不修改 MMDZh 的任何文件

**作者更新后的部署**（全程拖拽，无命令行）：
1. 按上面「安装」一节正常装新版 zip（双击 `AIナカワリ導入.cmd`）
2. 把 `zh_补丁包\app` 文件夹拖到 `<MMD 文件夹>\MMD-AINakawari\` 上选「替换」
3. 把 `zh_补丁包\MMD-AINakawari.dll` 复制到 `<MMD 文件夹>\Plugin\MMD-AINakawari\` 覆盖
4. 若新界面冒出个别日文句子，是翻译表还没收录新文字，不影响使用；若作者改了菜单/面板相关的 C++ 代码，DLL 需要重新编译一次（`tools\zh_patch\build_dll.cmd`）

**清 C 盘缓存的注意事项**：AI 环境装在安装设置选的位置（如 `D:\AINakawari\`），C 盘缓存与它无关。该位置里**不能删**的东西：
| 不能删 | 是什么 | 删了的后果 |
|---|---|---|
| `kimodo\.venv\` | Kimodo 的 Python 环境 | 要重装（约 5GB 下载） |
| `uv\python\` | 上面 venv 依赖的基础 Python | venv 全部失效，要整个重装 |
| `kimodo\hf_cache\` | Kimodo 模型权重（约 1.1GB） | 重新下载 |
| `kimodo\text_encoder\` | 提示词读取的 GGUF（约 7.4GB） | 重新下载 |
| `kimodo\llamacpp\` | llama.cpp 的 llama-server | 重新下载 |
| `motionbricks\motionbricks\assets\` | MotionBricks 的 ONNX 模型（约 1.1GB） | 重新下载 |
| `motionbricks\.venv\` | MotionBricks 的 Python 环境 | 要重装 |

可以删的：安装位置里的 `hf_home\`・`setup_test\`（空文件夹）、`.trt-cache\`（删了下次生成先多等约 1 分钟）、`MMD-AINakawari\app\work\` 里的临时 VMD（插件自己也会清）。C 盘的 Temp、浏览器缓存、DXCache 随便清。

**回滚中文版**：第一次覆盖时每个被替换的文件旁边都留了 `.orig` 备份，把 `.orig` 改回原名即可恢复日文原版；DLL 用发行版 zip 里的原版覆盖回去。

## 开发者向

从仓库直接运行时，用 [mmd-mcp](https://github.com/BeamManP/mmd-mcp) 的 Python 环境（`pip install -e . numpy` 与 `scripts\build_native.cmd`。需要 Visual Studio 2022 的 C++）启动窗口。
- 手动运行安装设置：`python -m mmd_ainakawari.installer.steps D:\AINakawari`（uv 用 PATH 里的）
- 指定之前手动装好的 Kimodo・MotionBricks 位置：`python -m mmd_ainakawari.paths F:\kimodo F:\motionbricks`
- 构建 MMD 插件：`mmd_plugin\build.cmd`（把 MMDPlugin 开发文件 `mmdplugin_dev_ver0.41_x64` 的内容放到 `work\mmdplugin\dev`，或用环境变量 `AINAKAWARI_SDK` 传位置）。ini 参照 `mmd_plugin\MMD-AINakawari.ini.example`
  - **中文版**：`tools\zh_patch\build_dll.cmd` 会自动用本地 SDK 编译（含 WndProc 签名修正）
- 构建 MMM 的按钮・面板：`dotnet build mmm_plugin\MMM-AINakawari.csproj -c Release -p:MmmDir=<MMM 文件夹>\`（需要 .NET SDK）。ini 参照 `mmm_plugin\MMM-AINakawari.ini.example`。桥按 [mmm-mcp](https://github.com/BeamManP/mmm-mcp) 的 README 组装
- 制作分发 zip：`python tools\release\build_release.py --mmdplugin <MMDPlugin_v0.41_x64.zip> --mmm-mcp <mmm-mcp 仓库>`（参考 mmm-mcp 旁边的 `MikuMikuMoving64\` 组装。产物在 `work\release\`）

## 开发记录
原理・踩过的坑・实测数据汇总在 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)。
