# AI中割（MMD-AINakawari）中文版 + MMDZh 汉化兼容补丁

## 这个补丁解决什么

日本作者的 MMD-AINakawari 0.6.0 只认「MMD 9.32 x64 日文原版」。你的 MMDZh 是
**运行时 hook 的 MMDPlugin DLL，不修改 MikuMikuDance.exe 文件**，所以：

| 作者的校验 | 汉化插件下 |
|---|---|
| `MikuMikuDance.exe` 的 SHA256 | ✅ 不变，通过 |
| `bone_state` 的硬编码内存偏移 / 骨骼名 cp932 解码 | ✅ 不变（MMDZh 刻意保留骨骼名日文），通过 |
| 安装器 `check_version()` | ✅ 通过 |
| **靠「读控件文字」定位 UI** | ❌ 原来会坏 → 本补丁修好 |

截图里的报错「メニューバーに「ヘルプ」が見つからないので…」就是最后一类：
`nakawari_plugin.cpp` 的 `help_position()` 只认「ヘルプ/help」，被 MMDZh 翻成
「帮助(&H)」后返回 -1，`start()` 直接弹错退出，菜单/面板/消息钩子全没建立。
（它读「帮助」只是为了**找菜单栏最右边的位置**把 AI 菜单插进去，并不读内容。）

## 改了什么（相对上游 0.6.0）

**C++（需重编译一次 DLL）** — `mmd_plugin/`
- `help_position()`：认「帮助」+ 全部认不出时回退到菜单栏最后一项，**绝不再弹错退出**。
- 菜单标题 / 面板标题 / 按钮 / 错误弹窗文案直接写成中文。
- `mmd_english_mode()` / `camera_mode()` 认「模型编辑 / 相机编辑」。

**Python（纯文本，复制即生效，不动 site-packages）** — `mmd_ainakawari/`
- `i18n.py`：加 `zh` 语言、默认中文。
- `texts/zh_all.py`：**453 条**简体中文翻译表（与作者 `en_*.py` 键集合完全一致，占位符零差异）。
- `zh_compat.py`（新）：运行时给 `mmd_mcp.ui_language.LABELS` 注入中文控件文字变体，
  并替换 `english_mode()`。因为 `matches()` 运行时才读 `LABELS`，十几个调用点自动全生效。
  还补了文件对话框标题集合。
- `mmd_link.py`：`language()` 固定 `zh`；`_track()` 改为读组合框 434 里**实际存在**的项
  （日文 / 英文 / 中文三套都能命中）；`_accept_other_model()` 认中文确认框。
- `app.py` / `mmm_link.py` / `installer/window.py`：语言相关小调整。
- `panel.py` / `prompt_samples.txt`：面板按钮与示例列表中文（英文 prompt 保留，AI 只认英文）。
- `__init__.py`：包加载时自动 `zh_compat.apply()`。

> **MMDZh 一行都不用改**，「帮助(&H)」照旧汉化。

## 首次部署（以汉化测试那份 MMD 为例）

> **注意**：`apply_zh_patch.py` 和 `build_dll.cmd` 是**命令行工具**，必须在命令行里带参数运行，
> **不能双击**、也不能放进 MMD 文件夹里。双击会一闪而过（因为它需要参数）。
> 本文的「第 2 步」就是那条完整命令。
>
> 目录名注意：你这份 MMD 用的是大写 **`Plugin\`**（不是 `plugin\`），DLL 要放到
> `Plugin\MMD-AINakawari\` 下。Windows 不区分大小写，两个写法指向同一个文件夹。

目标文件夹：`...\MikuMikuDanceE_v932x64\`（含 `Plugin\MMDZh\MMDZh.dll`）。
它原先**还没有 AI 插件**，而 `...\MikuMikuDanceE_v932x64日语原版+AI插件\` 是装好的完整版。

### 第 1 步：把已装好的插件整份复制过去

把 `MikuMikuDanceE_v932x64日语原版+AI插件\` 里的这 3 项复制到
`MikuMikuDanceE_v932x64\`（**MMD 要先关闭**）：

```
AIナカワリ導入.cmd
MMD-AINakawari\            （整份，含 python\ 和 app\，约 70MB）
Plugin\MMD-AINakawari\     （MMD-AINakawari.dll 和 .ini）
```

同时确认 exe 旁边有 `MMDPlugin.dll` / `d3d9.dll` / `d3dx9_43.dll`（汉化那份已有）。
或者：直接双击 `AIナカワリ導入.cmd`，让它自己装（它只校验 exe 哈希，MMDZh 不改 exe 所以能过）。

### 第 2 步：跑一键补丁脚本

**在「源码仓库」根目录打开命令行**（Win+R 输 `cmd`，再 `cd /d 源码仓库路径`），
执行下面这一整条（任意 Python 3.8+，不用装依赖）：

```
python tools\zh_patch\apply_zh_patch.py "D:\MMD\Tool\mmd观察解析pmm\MikuDanceStudio-main\PMM便携打包工具\MikuMikuDanceE_v932x64\MMD-AINakawari"
```

引号里是**已经装好 AI 插件的那个 `MMD-AINakawari` 文件夹**（含 `app\mmd_ainakawari\` 和 `python\`），
不是 MMD 根目录、也不是 zip。

它会复制 12 个文本/源文件，并把被覆盖的原文件留一份 `.orig` 备份。
**不动** `python\`、`site-packages\`、`work\`（你的设置和日志都保留）。

> 2026-11-13 已由我直接替你执行过这一步，12 个文件均已就位。
> 以后作者更新时你才需要自己再跑一次这条命令。

### 第 3 步：放置 MMD-AINakawari.dll（唯一需要编译的东西）

**已经帮你编译好了**，本仓库根目录就有 `MMD-AINakawari.dll`（211968 字节）。
你只需把它复制到：

```
MikuMikuDanceE_v932x64\Plugin\MMD-AINakawari\MMD-AINakawari.dll
```

> 2026-11-13 已确认：你放进去的那份与我编译的 SHA256 完全一致（`F23AECC3…`），**这步已完成**。

只有作者更新了 C++ 源码时才需要重新编译。**在源码仓库根目录的命令行**里跑：

```
tools\zh_patch\build_dll.cmd
```

（同样**不能双击**，也不能放进 MMD 文件夹。）

脚本会自动：
- 加载 `D:\MMD\VS\...\vs_builder\vc.bat`；
- 复制 `MMDZh\lib\mmd_plugin.h` 到 `work\mmdplugin\dev\` 并把 `WndProc` 签名
  从 `const CWPSTRUCT*` 改成 `CWPSTRUCT*`（**你本地所有头文件都是 const 版，
  而 AI 插件源码用的是官方 dev SDK 的非 const 版**；不改这个签名会报 C3668）；
- 加 `/DMAKE_MMD_PLUGIN` 编译，产出 `MMD-AINakawari.dll`（约 212KB）。

> 本仓库里**已经放了一份编译好的 `MMD-AINakawari.dll`**（根目录，211968 字节），
> 可以直接用，不必自己编。只有作者更新了 C++ 源码时才需要重新跑这个脚本。

把 DLL 覆盖到：

```
MikuMikuDanceE_v932x64\plugin\MMD-AINakawari\MMD-AINakawari.dll
```

若你的便携 MSVC 路径不同，编辑 `build_dll.cmd` 开头的 `VC=` 即可。

### 第 4 步：启动验证

开 MMD，应该看到：
- 菜单栏「帮助」右边出现「**AI中割**」→「**打开 AI中割 窗口**」；
- 右下角出现「**AI中割 简易操作**」面板，按钮「示例 ▼ / 生　成 / 撤销 / 详　细」；
- 详细窗口、设置、日志**全中文**；
- 打两个关键帧 →「生成」能把补间写回时间线。

若某句仍是日文，是翻译表漏了（不会崩，回退原文），把那句补进 `texts/zh_all.py` 即可。

## 作者出新版本时（这是「改动多不多」的答案）

每次更新 **2 步、约 5 分钟**：

1. 下载新版 zip，按它的 `AIナカワリ導入.cmd` 正常覆盖安装（会覆盖 `app\` 和 DLL）。
2. 重新跑一次 `apply_zh_patch.py` + 重编译/复制一次 DLL。

原因：
- **DLL 是二进制，必然被新版覆盖**，`help_position()` 那 4 行要重新打、重新编译。
- Python 改动被覆盖，但一键脚本会全部贴回去。
- `mmd_mcp`（site-packages）**完全没动过**，不用管。
- 翻译表若作者新增了界面文字：`zh_all.py` 补几条即可。**漏了不报错、不崩溃**，
  只是那句显示日文（i18n 的设计就是「表里没有就回退原文」）。
  可用仓库里的 `tests/check_i18n.py` 思路做键集合比对。

若作者重构了 `mmd_link.py` / `app.py`，一键脚本里的那几个文件要重新对照贴一次
（改动点都有醒目的「中文版」注释，grep `中文版` 即可找全）。

## Python 版本

**不用装任何 Python**。插件自带 3.10.19（zip 里的 `MMD-AINakawari\python\python.exe`），
AI 后端由 setup 用 uv 自动下载 3.10.19 / 3.12.12 到独立目录，并设了
`UV_PYTHON_PREFERENCE=only-managed`（不用电脑上其他 Python）。
你电脑里的 3.14.5 从头到尾不参与、不被覆盖、不冲突。

## 回滚

- Python 部分：`apply_zh_patch.py` 留下了 `.orig` 备份，删掉新文件、把 `.orig` 改回原名即可。
- DLL：用发行版 zip 里的原版 `MMD-AINakawari.dll` 覆盖回去。
- 权限修复（只在本会话做过一次，与插件无关）的撤销命令见
  `C:\Users\86155\AppData\Local\Temp\dsh-acl-recovery\` 下的 ROLLBACK 记录。
