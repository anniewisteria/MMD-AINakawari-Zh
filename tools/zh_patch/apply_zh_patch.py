"""中文版补丁部署脚本：把源码仓库里的中文改动复制到任意一份「已安装」的 AI 插件上。

用法（在任意 Python 3.8+ 下运行，不需要装任何依赖）：

    python tools/zh_patch/apply_zh_patch.py <已安装插件的 MMD-AINakawari 文件夹>

例如：

    python tools/zh_patch/apply_zh_patch.py "D:\\MMD\\Tool\\...\\MikuMikuDanceE_v932x64\\MMD-AINakawari"

它做两件事：
  1. 把 10 个改过的 .py / .txt 复制到 <目标>\\app\\mmd_ainakawari\\ 下对应位置
     （不碰 python\\、不碰 site-packages\\、不碰已编译的 DLL、不碰 work\\ 里的设置与日志）。
  2. 提示你还需要「重编译一次 MMD-AINakawari.dll」（见同目录 README.md）。

设计原则：**不改 site-packages 里任何第三方文件**。mmd-mcp 的中文兼容全部通过
mmd_ainakawari/zh_compat.py 在运行时注入，所以作者更新 zip 后只要重新跑本脚本 + 重编译 DLL，
不用逐个去改 mmd_mcp 的十几个文件。

作者发新版时的完整步骤见 tools/zh_patch/README.md。
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # 仓库根
SRC = os.path.join(ROOT, "mmd_ainakawari")

# (仓库内相对路径, 目标内相对路径)。全部是纯文本，覆盖即可，可逆（原文件先备份为 .orig）。
FILES = [
    ("__init__.py",                 "app/mmd_ainakawari/__init__.py"),
    ("i18n.py",                     "app/mmd_ainakawari/i18n.py"),
    ("zh_compat.py",                "app/mmd_ainakawari/zh_compat.py"),
    ("mmd_link.py",                 "app/mmd_ainakawari/mmd_link.py"),
    ("mmm_link.py",                 "app/mmd_ainakawari/mmm_link.py"),
    ("app.py",                      "app/mmd_ainakawari/app.py"),
    ("panel.py",                    "app/mmd_ainakawari/panel.py"),
    ("samples.py",                  "app/mmd_ainakawari/samples.py"),
    ("prompt_samples.txt",          "app/mmd_ainakawari/prompt_samples.txt"),
    ("texts/zh_all.py",             "app/mmd_ainakawari/texts/zh_all.py"),
    ("installer/window.py",         "app/mmd_ainakawari/installer/window.py"),
]
# 安装脚本（在 MMD-AINakawari/app/tools/ 下，若该文件存在才复制）
# (源相对仓库根, 目标相对 MMD-AINakawari)
OPTIONAL_ROOT = [
    ("tools/install_plugin.py", "app/tools/install_plugin.py"),
]


def main():
    if len(sys.argv) != 2:
        print("用法: python apply_zh_patch.py <已安装插件的 MMD-AINakawari 文件夹>")
        return 2
    dest = os.path.abspath(sys.argv[1])
    app = os.path.join(dest, "app", "mmd_ainakawari")
    if not os.path.isdir(app):
        print(f"找不到 {app}\n请确认路径指向含 app\\mmd_ainakawari 的「MMD-AINakawari」文件夹。")
        return 2

    done, skipped = 0, []
    pairs = [(os.path.join(SRC, s.replace("/", os.sep)), d) for s, d in FILES]
    pairs += [(os.path.join(ROOT, s.replace("/", os.sep)), d) for s, d in OPTIONAL_ROOT]
    for src, dst_rel in pairs:
        dst = os.path.normpath(os.path.join(dest, dst_rel))
        if not os.path.isfile(src):
            skipped.append((src_rel, "源文件不存在"))
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        # 第一次部署时留一份原版备份，方便回滚（不覆盖已有 .orig）
        if os.path.isfile(dst) and not os.path.isfile(dst + ".orig"):
            try:
                shutil.copy2(dst, dst + ".orig")
            except OSError as e:
                print(f"  警告: 备份 {dst} 失败: {e}")
        shutil.copy2(src, dst)
        print("  复制", dst_rel)
        done += 1

    for name, why in skipped:
        print(f"  跳过 {name}: {why}")
    print(f"\n完成：复制 {done} 个文件，未改动 python\\、site-packages\\、work\\、DLL。")
    print("下一步：重编译 MMD-AINakawari.dll 并替换（见 tools/zh_patch/README.md）。")
    print("        若目标 MMD 里还没有 AI 插件，请先运行发行版 zip 里的「AIナカワリ導入.cmd」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
