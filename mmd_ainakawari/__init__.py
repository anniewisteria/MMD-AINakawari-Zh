"""AIナカワリ: MMD・MMM で打ったキーの間を NVIDIA Kimodo で埋める外部ツール。

中文版：在本包被导入时（早于 mmd_link / app 导入 mmd-mcp）注入中文控件文字兼容补丁。
不改 site-packages 里的任何文件，作者更新 zip 后重新贴本包即可。详见 zh_compat.py。
"""

__version__ = "0.6.0"  # 配布の zip の名前（tools/release/build_release.py）

# 中文版补丁。放在最前面执行：mmd_link.py 在 import 时就会 from mmd_mcp import ...，
# 必须先把中文变体注入 ui_language.LABELS，否则后续 matches() 调用拿到的是旧表。
try:
    from . import zh_compat as _zh_compat
    _zh_compat.apply()
except Exception as _e:  # 补丁本身出问题也不能让窗口起不来
    try:
        import sys as _sys
        print(f"[AINakawari zh] compat patch failed: {type(_e).__name__}: {_e}", file=_sys.stderr)
    except Exception:
        pass
