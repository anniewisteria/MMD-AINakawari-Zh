"""中文版补丁：让 mmd-mcp 的文字匹配认识「MMDZh 运行时汉化」后的中文控件文字。

为什么是「补丁」而不是改 mmd-mcp
--------------------------------
发行版 zip 自带一份 Python（3.10）和 site-packages 里的 mmd-mcp。直接改 site-packages
会在作者更新 zip 时被整个覆盖，且不利于对照上游。这里在 *本包加载时* 就地修改
mmd-mcp 的模块级全局字典 —— mmd_mcp.ui_language.matches()/variants() 是运行时才去读
LABELS 的，所以「from .ui_language import matches」的十几个调用点会自动全部生效，
不需要逐个文件去改，也不怕函数被 import 绑定。

关键事实（决定了这个补丁能成立）：
* MMDZh 是 MMDPlugin 的运行时 hook DLL，**不修改 MikuMikuDance.exe**。所以
  bone_state.VERIFIED_SHA256 和所有硬编码的内存偏移照样有效。
* MMDZh 词典刻意把骨骼名 / 表情名保留为日文（cp932），所以内存读出来的名字不变。
* 唯一坏掉的是「按控件文字定位 UI」：菜单「ヘルプ」→「帮助(&H)」、按钮 536
  「カメラ編/モデル編」→「相机编辑/模型编辑」、组合框 434 的项、对话框标题等。

因此这里做四件事：
1. ui_language.LABELS 追加「日文 → 中文」变体（含按钮 536、对话框标题、确认框）。
2. english_mode() 换成中文感知版本：中文一律按「非英语」处理（走日语模式那套分支），
   用 536 按钮的中文形判断；认不出时默认 False，绝不抛异常。
3. file_operations 的文件对话框标题集合追加中文标题；按钮文字集合追加「确定/取消/是」。
4. mmd_link.py 里的范围选择项 / 确认框文字映射（本模块提供常量，见 TRACKS_ZH）。

界面语言（i18n 的 "zh"）与这里的「UI 匹配按日语模式走」是两件事，互不干扰：
MMDLink.language() 返回 "zh" 让窗口出中文，MMDLink.english() 仍返回 False 让控件按
「中文变体」命中。两个函数本来就独立（见源码）。

作者更新后的维护点都集中在本文件 + mmd_link.py 的几行，见 tools/zh_patch/apply_zh_patch.py。
"""
import importlib

# ---------------------------------------------------------------------------
# 1. 日文原文 → MMDZh 汉化后的中文文字。
#    键必须与 mmd_mcp/ui_language.py 的 LABELS 键逐字一致；值可以是一个字符串或元组
#    （LABELS 原生支持这两种）。追加而不是替换，日文/英文原样保留。
# ---------------------------------------------------------------------------
ZH_LABELS = {
    # 控件 536：3D 画面下的「カメラ編／モデル編」切换按钮
    # 注意 MMDZh 词典里同时存在「相机编辑」「模型编辑」以及顶栏「相 机」「照 明」等带空格形，
    # 这里只收 536 按钮实际会出现的两种。
    "カメラ編": ("相机编辑", "相机编"),
    "モデル編": ("模型编辑", "模型编"),
    # 组合框 434（范围选择的对象）。MMDZh 词典：
    #   全ﾌﾚｰﾑ→全部帧 / 全ボーンﾌﾚｰﾑ→全部骨骼帧 / 全表情ﾌﾚｰﾑ→全部表情帧
    #   以及全角版 全フレーム→全部帧 / 全ボーンフレーム→全部骨骼帧 / 全表情フレーム→全部表情帧
    "全ボーンﾌﾚｰﾑ": ("全部骨骼帧", "全部骨骼"),
    "全ﾌﾚｰﾑ": ("全部帧",),
    "全表情ﾌﾚｰﾑ": ("全部表情帧",),
    # 文件对话框 / 确认框标题（file_operations.FILE_DIALOG_TITLES、scene_lifecycle.confirm）
    "モーションデータ読込": ("导入动作数据", "载入动作数据", "动作数据载入"),
    "モーションデータ保存": ("动作数据保存", "导出动作数据"),
    "ポーズデータ読込": ("导入姿势数据", "导入姿态数据"),
    "ポーズデータ保存": ("导出姿势数据", "保存姿势数据"),
    "画像ファイル出力": ("导出图片文件",),
    "ファイルを開く": ("打开文件", "打开"),
    "開く": ("打开",),
    "モデル情報": ("模型信息",),
    "新規作成": ("新建",),
    "モデル削除": ("删除模型",),
    "アクセサリ削除": ("删除附件",),
    "名前を付けて保存の確認": ("确认另存为",),
    "はい(&Y)": ("是(&Y)", "是"),
    "AVI出力設定": ("AVI输出设置",),
    "AVIデータ読込": ("AVI 数据载入", "导入AVI数据"),
    "AVI出力": ("导出AVI", "导出 AVI"),
    "背景画像データ読込": ("导入背景图片数据",),
    "WAVE Fileを開く": ("打开WAVE File",),
    "ファイルを保存する": ("保存文件",),
    "名前を付けて保存": ("另存为",),
    "外部親設定": ("外亲设定",),
    "モデル描画順設定": ("模型绘制顺序设置",),
    "モデル計算順設定": ("模型计算顺序设置",),
    "重力設定": ("重力设置", "重力设定"),
    "エッジ太さ設定": ("轮廓线厚度设置",),
    "地面影色設定": ("地面阴影颜色设置",),
    "出力画面サイズ変更": ("输出画面尺寸", "视频分辨率"),
    "ﾎﾞｰﾝﾌﾚｰﾑ位置角度補正": ("骨骼帧位置/角度校正", "骨骼位置/角度校正"),
    "ｶﾒﾗﾌﾚｰﾑ位置角度補正": ("相机帧位置/角度校正", "相机位置/角度校正"),
    "表情大きさ補正": ("表情幅度校正",),
    "バイアス付加": ("添加偏移",),
    "まばたき登録": ("眨眼注册",),
    "シフトするﾌﾚｰﾑ数": ("移动帧数",),
    "物理ON/OFFフレーム変換": ("物理帧开/关",),
    "時間拡大(縮小)率": ("时间放大(缩小)率",),
    "エフェクトファイル割り当て": ("特效文件配置",),
}

# ---------------------------------------------------------------------------
# 2. 组合框 434 的「范围选择对象」中文名（mmd_link.py 的 _track() 用）
# ---------------------------------------------------------------------------
TRACKS_ZH = {
    "全ﾌﾚｰﾑ": "全部帧",
    "全ボーンﾌﾚｰﾑ": "全部骨骼帧",
    "全表情ﾌﾚｰﾑ": "全部表情帧",
}

# ---------------------------------------------------------------------------
# 3. 中文对话框标题（供 mmd_link._accept_other_model 等按标题认弹窗）
# ---------------------------------------------------------------------------
TITLE_LOAD_MOTION_ZH = ("导入动作数据", "载入动作数据", "动作数据载入", "load motion data", "モーションデータ読込")
TITLE_MODEL_INFO_ZH = ("模型信息", "model infomation", "モデル情報")
# 「此文件是供 ○○ 使用的动作数据… 要继续吗？」确认框里的中文标志词
ACCEPT_OTHER_MODEL_ZH = ("此文件是供", "只导入骨骼名称相同的动作", "要继续吗", "将只导入骨骼名称相同的动作")
# 「确定」按钮（MMDZh 把 OK / 了解 / ＯＫ 统一翻成「确定」）
BUTTON_OK_ZH = ("确定", "是(&Y)", "是", "OK", "了解", "ＯＫ")

# ---------------------------------------------------------------------------
# 补丁入口
# ---------------------------------------------------------------------------
_applied = False


def _zh_english_mode(reader):
    """中文感知的 english_mode：中文一律按「非英语」处理，认不出也不抛异常。

    mmd_mcp 里 english_mode() 只用来决定「内存里的模型名读日文栏还是英文栏」和
    inspect_bones 用哪一套名字。MMDZh 不改 exe、不改内存布局，模型名仍按日文（cp932）
    存放，所以返回 False 是正确的。原版在遇到未知文字时会抛 ValueError 导致整个生成中断。
    """
    try:
        label = reader.text(reader.control(536, "Button"))
    except Exception:
        return False
    if label in {"camera", "To camera", "To model"}:
        return True
    # 日文原貌、MMDZh 中文、以及认不出的任何文字 —— 都按日语（非英语）模式走
    return False


def apply():
    """把中文变体注入 mmd-mcp。可重复调用（幂等）。失败只记日志，不让窗口起不来。"""
    global _applied
    if _applied:
        return
    _applied = True
    try:
        ui_language = importlib.import_module("mmd_mcp.ui_language")
    except Exception as e:  # mmd-mcp 没装好时，先让窗口起来，日志里能看到
        try:
            from . import applog
            applog.write(f"中文兼容补丁: mmd_mcp 读取失败（{type(e).__name__}: {e}）")
        except Exception:
            pass
        return

    # (a) LABELS 原地追加中文变体 —— matches()/variants() 运行时才读它
    for key, zh in ZH_LABELS.items():
        old = ui_language.LABELS.get(key, ())
        if isinstance(old, str):
            old = (old,)
        else:
            old = tuple(old)
        if isinstance(zh, str):
            zh = (zh,)
        ui_language.LABELS[key] = old + tuple(x for x in zh if x not in old)

    # (b) english_mode 换成中文感知版本。
    #     注意 bone_state / bone_selection / bone_batch 里是
    #     「from .ui_language import english_mode」直接绑定函数对象，
    #     所以还要把这些模块里已绑定的名字也换掉。
    ui_language.english_mode = _zh_english_mode
    for name in ("bone_state", "bone_selection", "bone_batch", "timeline_transforms"):
        try:
            mod = importlib.import_module("mmd_mcp." + name)
            if hasattr(mod, "english_mode"):
                mod.english_mode = _zh_english_mode
        except Exception:
            pass

    # (c) 文件对话框标题 / 按钮文字集合追加中文
    try:
        fo = importlib.import_module("mmd_mcp.file_operations")
        fo.FILE_DIALOG_TITLES = set(fo.FILE_DIALOG_TITLES) | {
            "导入动作数据", "载入动作数据", "动作数据载入", "动作数据保存", "导出动作数据",
            "导入姿势数据", "导入姿态数据", "导出姿势数据", "保存姿势数据",
            "导出图片文件", "打开文件", "打开", "保存文件", "另存为", "确认另存为",
            "模型信息", "新建", "删除模型", "删除附件",
            "AVI输出设置", "AVI 数据载入", "导入AVI数据", "导出AVI", "导出 AVI",
            "导入背景图片数据", "打开WAVE File", "文件载入", "载入文件",
        }
        fo.SAVE_DIALOG_TITLES = set(fo.SAVE_DIALOG_TITLES) | {
            "动作数据保存", "导出动作数据", "导出姿势数据", "保存姿势数据",
            "导出图片文件", "保存文件", "另存为", "导出AVI", "导出 AVI",
        }
    except Exception:
        pass
