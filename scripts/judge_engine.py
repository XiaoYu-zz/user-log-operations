# -*- coding: utf-8 -*-
"""judge_engine — 软件研判任务 prompt v10 的规则引擎（知识库 v1 + 黑名单）。
输入 work/sorted_rows.json（step12_build 产出），输出 work/judged_rows.json + 统计。
黑名单(work/blacklist_sigs.json，源 sign.md)已接入：签名命中→软件名称=疑似流氓软件，
评分/网址/介绍/备注全空；优先级高于全部其他规则（商店分发冲突亦按黑名单，用户已确认）。
"""
import json
import os
import re
from collections import Counter, defaultdict

WORK = os.path.dirname(os.path.abspath(__file__))

URL_CANDIDATES = {
    "dingtalk": "https://www.dingtalk.com/download",
    "feishu": "https://www.feishu.cn/",
    "doubao": "https://www.doubao.com/download",
    "trae": "https://trae.com.cn/download",
    "zcode": "https://code.zhipuai.cn/",
    "qwenwork": "https://tongyi.aliyun.com/qianwen/",
    "genspark": "https://www.genspark.ai/",
    "zed": "https://zed.dev/download",
    "python": "https://www.python.org/downloads/",
    "go": "https://go.dev/dl/",
    "nodejs": "https://nodejs.org/zh-cn/download",
    "postgresql": "https://www.postgresql.org/download/windows/",
    "chrome": "https://www.google.cn/chrome/",
    "todesk": "https://www.todesk.com/download.html",
    "sunlogin": "https://sunlogin.oray.com/download",
    "discord": "https://discord.com/download",
    "sogou": "https://pinyin.sogou.com/",
    "meitu": "https://xiuxiu.meitu.com/",
    "360safe": "https://www.360.cn/",
    "zen": "https://zen-browser.app/",
    "coccoc": "https://coccoc.com/",
    "desktopcal": "https://www.desktopcal.com/",
    "teamviewer": "https://www.teamviewer.com/zh-cn/",
    "metaquotes": "https://www.metatrader5.com/",
    "jianying": "https://www.capcut.cn/",
    "emeditor": "https://www.emeditor.com/",
    "wb115": "https://115.com/",
    "ahs": "https://virbox.com/",
    "audacity": "https://www.audacityteam.org/",
    "idm": "https://www.internetdownloadmanager.com/",
    "deskflow": "https://deskflow.org/",
    "msedge": "https://www.microsoft.com/zh-cn/edge/download",
    "xwechat": "https://weixin.qq.com/",
    "lmstudio": "https://lmstudio.ai/",
    "yuanbao": "https://yuanbao.tencent.com/",
}

VALID_SIG_HINT = ("ltd", "inc", "llc", "corp", "co.,", "technolog", "company", "software",
                  "foundation", "gmbh", "有限", "科技", "股份", "网络", "信息", "软件", "工作室")


def dec(s):
    return s.replace("+", " ").strip().lower() if isinstance(s, str) else s


def norm_s(s):
    """签名规范化：与 step14 口径一致，小写、仅留字母数字与汉字（消空白/标点差异）。"""
    return re.sub(r"[^a-z0-9一-鿿]", "", s) if isinstance(s, str) else ""


def sig_validish(sd):
    return sd != "\\N" and any(h in sd for h in VALID_SIG_HINT)


# ---------------- 知识库 v1 ----------------
# 每条: (key, when(pd, fd, sd, row) -> True/组键后缀, name, score, url_key, intro, ai)
# score None -> 该组评分留空(游戏/黑名单); kind 由位置决定
def R(key, name, score, url=None, intro=None, ai=False, **extra):
    d = {"key": key, "name": name, "score": score, "url": URL_CANDIDATES.get(url),
         "intro": intro, "ai": ai, "url_key": url}
    d.update(extra)
    return d


KNOWN = [
    # --- 游戏（过滤规则优先，评分/网址/介绍留空） ---
    R("game_steam", "游戏", None, when_kw=("steam\\steamapps", "\\steamlibrary\\steamapps")),
    R("game_wegame", "游戏", None, when_kw=("wegameapps", "腾讯游戏")),
    R("game_kk", "游戏", None, when_kw=("kkduizhan",)),
    R("game_xtlbb", "游戏", None, when_kw=("\\xtlbb",)),
    R("game_wooduan", "游戏", None, when_kw=("wooduan",), when_sig=("浙江无端",)),
    R("game_leidian", "游戏", None, when_kw=("\\leidian",), when_sig=("just okay",)),
    R("game_duoyi", "游戏", None, when_kw=("多益",)),
    R("game_pwrld", "游戏", None, when_kw=("perfectworld",), when_sig=("完美世界",)),
    R("game_shulong", "游戏", None, when_kw=("数龙", "冒险岛"), when_sig=("shulong",)),
    R("game_hdt", "游戏", None, when_kw=("hearthstonedecktracker",), when_sig=("hearthsim",)),
    R("game_maa", "游戏", None, when_kw=("\\maa",)),
    R("game_ace", "游戏", None, when_kw=("anticheatexpert",), when_sig=("aceville",)),
    R("game_hpjy", "游戏", None, when_kw=("\\hpjy",)),
    R("game_wemod", "游戏", None, when_kw=("wemod", "\\wand"), when_sig=("wemod",)),
    R("game_x5", "游戏", None, when_kw=("qq炫舞",)),
    R("game_gaijin", "游戏", None, when_sig=("gaijin",)),
    # --- PUA 厂商族（黑名单待接入，暂评分 2-4） ---
    R("pua_aishang", "@aishang", 3, when_kw=("fastpdf", "masterpdf", "wincleanapp", "xdzipapp",
                                             "wmeiplayer", "dllrepairofficial", "xdimageshow",
                                             "cadviewerve", "o2wallpaper", "printerhelper",
                                             "\\editor", "lenovosoftstore"),
      when_sig=("aishang", "chengdu aishang")),
    R("pua_mobozhi", "@mobozhi", 3, when_sig=("茉柏枘",)),
    R("pua_moting", "@moting", 3, when_sig=("莫停之",),
      when_kw=("wincompress360", "winmaster", "printmaster")),
    R("pua_2345", "@2345", 3, when_kw=("2345",), when_sig=("2345",)),
    R("pua_flash", "@flash", 3, when_kw=("flashcenter",), when_sig=("zhongcheng", "重橙")),
    R("pua_winr", "@winr360", 3, when_kw=("winr360",), when_sig=("little tomato",)),
    R("pua_winziper", "@winziper", 4, when_kw=("winziper",), when_sig=("渠缤",)),
    R("pua_chibao", "@chibao", 4, when_sig=("驰豹",)),
    R("pua_juhuo", "@juhuo", 4, when_sig=("聚火",)),
    R("pua_yujie", "@yujie", 4, when_sig=("宇界",), when_kw=(".dbx",)),
    R("pua_ludashi", "鲁大师", 4, when_kw=("ludashi",), when_sig=("奇鲁", "qilu")),
    R("pua_hongli", "弘历软件", 3, when_kw=("弘历",)),
    R("pua_gupiao", "@gupiao", 3, when_kw=("dianjingyitou",), when_sig=("约牛", "力多星", "liduoxing")),
    R("pua_xunjie", "@xunjie", 4, when_sig=("迅读",)),
    # --- 微软 / 系统组件 ---
    R("ms_windows", "Microsoft Windows", 9, when_kw=("softwaredistribution", "\\winsxs", "\\system32",
                                                     "\\syswow64", "\\assembly", "windows\\explorer",
                                                     "\\sysnative", "\\driverstore", "\\grouppolicy")),
    R("ms_dir", "Microsoft Windows", 9, ai_copilot=True,
      when_kw=("program files (x86)\\microsoft", "program files\\microsoft")),
    R("ms_sig", "Microsoft Windows", 9, when_sig=("microsoft windows", "microsoft corporation",
                                                  "microsoft windows publisher",
                                                  "microsoft dynamic code publisher",
                                                  "hardware compatibility publisher")),
    # --- 商店包在 store 分支单独处理（windowsapps） ---
    # --- 已知软件 ---
    R("dingtalk", "钉钉", 9, "dingtalk", "企业协作平台", when_kw=("dingding",), when_sig=("dingtalk",)),
    R("feishu", "飞书", 9, "feishu", "企业协作平台", when_kw=("feishu", "larkshell"), when_sig=("feishu",)),
    R("doubao", "豆包", 9, "doubao", "AI智能助手", True, when_kw=("doubao",)),
    R("trae", "Trae", 9, "trae", "AI编程IDE", True, when_kw=("trae cn", "\\trae")),
    R("zcode", "Zcode", 8, "zcode", "AI编程工具", True, when_kw=("\\zcode",), when_sig=("智谱",)),
    R("qwenwork", "QwenWork", 8, "qwenwork", "AI办公助手", True, when_kw=("qwenwork",)),
    R("genspark", "Genspark", 8, "genspark", "AI浏览器", True, when_kw=("genspark",), when_sig=("genspark",)),
    R("perplexity", "Perplexity Comet", 8, None, "AI浏览器", True, when_sig=("perplexity",)),
    R("browseai", "BrowseAI", 7, None, "AI网页自动化", True, when_sig=("browseai",)),
    R("zed", "Zed", 8, "zed", "代码编辑器", when_kw=("programs\\zed",), when_sig=("zed industries",)),
    R("vscode", "Microsoft VS Code", 8, None, "代码编辑器", when_kw=(".vscode",)),
    R("python", "Python", 8, "python", "编程语言运行时", when_kw=("programs\\python",),
      when_sig=("python software foundation",)),
    R("uv", "uv", 8, None, "Python包管理器", when_kw=("roaming\\uv", ".local\\bin")),
    R("golang", "Go", 8, "go", "编程语言工具链", when_kw=("program files\\go",)),
    R("nodejs", "Node.js", 8, "nodejs", "JS运行时", when_sig=("openjs",)),
    R("gitwin", "Git for Windows", 8, None, "版本控制工具", when_sig=("johannes schindelin",)),
    R("pgsql", "PostgreSQL", 8, "postgresql", "开源数据库", when_kw=("postgresql",)),
    R("chrome", "Google Chrome", 9, "chrome", "网页浏览器", when_kw=("google\\chrome", "program files\\google"),
      when_sig=("google llc",)),
    R("chromium_snap", "Chromium", 7, None, "浏览器开发版", when_kw=("chromium-browser-snapshots",)),
    R("agent_browser", "Chromium自动化浏览器", 7, None, "自动化浏览器组件", when_kw=(".agent-browser",)),
    R("discord", "Discord", 8, "discord", "游戏语音社区", when_kw=("discord",), when_sig=("discord",)),
    R("todesk", "ToDesk", 8, "todesk", "远程控制软件", when_kw=("todesk",), when_sig=("hainan youqu", "海南有趣")),
    R("oray", "向日葵", 8, "sunlogin", "远程控制软件", when_kw=("oray", "awesun"), when_sig=("贝锐", "oray")),
    R("teamviewer", "TeamViewer", 8, "teamviewer", "远程控制软件", when_kw=("teamviewer",),
      when_sig=("teamviewer",)),
    R("symantec", "Symantec Endpoint Protection", 8, None, "终端安全防护", when_kw=("symantec",)),
    R("ivanti", "Ivanti EPM", 7, None, "终端管理组件", when_kw=("ivanti", "landesk"), when_sig=("ivanti",)),
    R("manageengine", "ManageEngine UEMS", 7, None, "终端管理组件", when_kw=("manageengine",),
      when_sig=("zoho",)),
    R("egcloud", "亿格云安全组件", 7, None, "企业安全接入", when_kw=("yunshu",), when_sig=("亿格云", "aquila")),
    R("tianyi_sec", "天翼安全组件", 7, None, "企业安全组件", when_sig=("china telecom cybersecurity",)),
    R("telecom_q", "中电信量子组件", 7, None, "量子安全通信", when_sig=("china telecom quantum",),
      when_kw=("zdxlz",)),
    R("tec", "TEC远程组件", 7, None, "远程控制组件", when_sig=("tec solutions", "guangzhou tec")),
    R("lianruan", "联软UniAccess", 7, None, "终端管理组件", when_sig=("联软",)),
    R("yinggao", "盈高入网规范", 7, None, "终端安全管理", when_sig=("盈高",)),
    R("huawei_isep", "华为eSEP组件", 7, None, "终端安全组件", when_kw=("\\isep",)),
    R("huawei_nc", "华为NetCare组件", 7, None, "运维组件", when_kw=("netcare",)),
    R("huawei", "华为终端组件", 7, None, "终端组件", when_sig=("huawei",)),
    R("sogou", "搜狗输入法", 8, "sogou", "输入法", when_kw=("sogou",), when_sig=("sogou", "搜狗")),
    R("meitu", "美图秀秀", 8, "meitu", "图片处理软件", when_kw=("meitu",), when_sig=("meitu", "美图")),
    R("jianying", "剪映", 8, "jianying", "视频剪辑软件", when_sig=("douyin vision",)),
    R("safe360", "360安全卫士", 7, "360safe", "安全防护软件", when_kw=("360\\360safe",)),
    R("desktopcal", "桌面日历", 7, "desktopcal", "桌面日历工具", when_kw=("calendartask",),
      when_sig=("xiaowei",)),
    R("island", "Island", 7, None, "企业安全浏览器", when_kw=("\\island",)),
    R("coccoc", "Cốc Cốc", 7, "coccoc", "网页浏览器", when_kw=("coccoc",)),
    R("zen", "Zen Browser", 8, "zen", "网页浏览器", when_kw=("zen browser",),
      when_sig=("oscar gonzalez",)),
    R("emeditor", "EmEditor", 8, "emeditor", "文本编辑器", when_sig=("emurasoft",)),
    R("metaquotes", "MetaTrader", 7, "metaquotes", "交易平台", when_sig=("metaquotes",)),
    R("aisino", "航天信息组件", 7, None, "税务信息化", when_sig=("航天信息",)),
    R("sinopec", "中石化内网组件", 7, None, "企业内网组件", when_sig=("china petroleum",)),
    R("hongye", "清单计价专家", 7, None, "建筑计价软件", when_kw=("清单计价",), when_sig=("宏业",)),
    R("chuangxing", "创星医疗信息平台", 7, None, "医疗信息系统", when_kw=("创星医疗",)),
    R("jdwms", "京东WMS组件", 7, None, "仓储管理系统", when_kw=("jd.wms",)),
    R("weishibu", "微步在线组件", 7, None, "安全分析工具", when_sig=("微步在线",)),
    R("honggu", "红谷MES组件", 7, None, "制造执行系统", when_sig=("红谷",)),
    R("anxun", "安寻组件", 7, None, "考试安全组件", when_sig=("安寻",)),
    R("uusafe", "UUsafe组件", 7, None, "终端安全组件", when_sig=("uusafe",)),
    R("jinshan_av", "金山安全组件", 6, None, "安全防护组件", when_kw=("kingsoft antivirus",)),
    # --- 溯源 v2（2026-09-11 批次1：联网定性 + 离线高置信，模式均经数据段级核验） ---
    R("v2_wb115", "115网盘桌面版", 8, "wb115", "网盘客户端",
      when_kw=("115 desktop", "115-desktop"), when_sig=("上海魔之雨",)),
    R("v2_workbuddy", "腾讯WorkBuddy", 9, None, None, True, when_kw=("workbuddy",)),
    R("v2_ahs", "深思数盾Virbox组件", 7, "ahs", "软件保护授权组件",
      when_kw=("ahs protector", "ahsprotector"), when_sig=("深思数盾",)),
    R("v2_wuxing", "五星智投", 3, when_kw=("wuxingzhitou",)),
    R("v2_360hb", "360画报", 6, when_kw=("360hb tmp", "360hb_tmp", "360huabao")),
    R("v2_jinlong", "金龙管理软件", 7, None, "管理软件", when_kw=("金龙管理软件",)),
    R("pua2_bozhong", "博众投顾客户端", 3, when_sig=("广东博众智能科技",)),
    R("game_ncsoft", "游戏", None, when_kw=("ncsoft", "\\purple\\"), when_sig=("nc corporation",)),
    R("game_wow", "游戏", None, when_kw=("world of warcraft",)),
    R("game_hearthstone", "游戏", None, when_kw=("hearthstone",)),
    R("game_ylgame", "游戏", None, when_kw=("ylgame",), when_sig=("杭州战英",)),
    R("game_yuanyou", "游戏", None, when_kw=("元游棋牌",), when_sig=("上海元游",)),
    R("v2_dwrcs", "DameWare远程控制", 7, None, "远程管理组件",
      when_kw=("dwrcs",), when_sig=("solarwinds",)),
    R("v2_edge", "Microsoft Edge", 9, "msedge", "网页浏览器", when_kw=("microsoft\\edge",)),
    R("v2_audacity", "Audacity", 8, "audacity", "音频编辑软件",
      when_kw=("audacity",), when_sig=("musecy",)),
    R("v2_idm", "Internet Download Manager", 8, "idm", "下载工具",
      when_kw=("internet download manager",)),
    R("v2_uniaccess", "联软UniAccess", 7, None, "终端管理组件", when_kw=("uniaccesslite",)),
    R("v2_deskflow", "Deskflow", 7, "deskflow", "键鼠共享工具", when_kw=("deskflow",)),
    R("v2_whatsapp", "WhatsApp", 9, None, "即时通讯", when_kw=("whatsappdesktop",)),
    # --- 溯源 v3（2026-09-11 批次1：联网确认 + 用户过目，证据见 outputs/溯源_batch1_检索结果.md） ---
    R("v3_xwechat", "微信", 9, "xwechat", "即时通讯软件", when_kw=("xwechat",)),
    R("v3_tiesiyuan", "铁四院智能勘察设计平台", 7, None, "企业勘察设计软件", when_kw=("铁四院",)),
    R("v3_mes", "MES制造执行系统客户端", 6, None, "制造执行系统", when_kw=("soft\\mes", "plantumes")),
    R("v3_devtest", "内部测试工具", 5, None, "疑似企业内部测试工具", when_kw=("devicetesttools",)),
    R("pua_msconfig", "疑似伪装系统工具", 2, None, "目录名伪装Windows系统工具", when_kw=("msconfig",)),
    # --- 溯源 v3 遗留身份收尾（2026-09-11 检索确认，证据见对话与批次1清单） ---
    R("v3_lmstudio", "LM Studio", 8, "lmstudio", "本地大模型运行环境", True,
      when_kw=("\\bionic",), when_sig=("element labs",)),
    R("v3_alphaai", "AlphaAI法律智能平台", 8, None, "智能法律服务平台", True,
      when_kw=("alphaai",), when_sig=("北京新橙",)),
    # --- 溯源 v3 批次2（2026-09-11，证据见 outputs/溯源_batch2_检索结果.md，用户过目确认） ---
    R("v3_yuanbao", "腾讯元宝", 9, "yuanbao", "AI智能助手", True,
      when_kw=("yuanbao",), when_fn=("yuanbao",)),
    R("v3_cowork", "Claude Cowork组件", 8, None, "Claude桌面版智能工作组件", True,
      when_kw=("deeplink-cowork", "\\cowork")),
    R("v3_cpoc", "景桥软件CPOC客户端", 7, None, "企业客户端软件",
      when_kw=("cpoc",), when_sig=("南京景桥",)),
    R("v3_qpct", "青岛港CSP码头操作系统", 7, None, "港口集装箱码头操作系统",
      when_kw=("csp集装箱管理系统", "qpct")),
    R("v3_pyhanko", "PyHanko PDF签名组件", 7, None, "开源PDF数字签名库", when_kw=("pyhanko",)),
    R("v3_renjiao", "人教教学易", 7, None, "人教社多媒体教学软件", when_kw=("renjiaojiaoxueyi",)),
    R("v3_shangwo", "厦门尚沃网络组件", 4, None, "邮件营销服务商组件",
      when_kw=("protect\\wsus",), when_sig=("xiamen shangwo",)),
    R("v3_mes_zs", "MES正式区客户端（企业内部）", 6, None, "企业制造执行系统客户端",
      when_kw=("mes正式区客户端",)),
    R("v3_sogou_pkg", "搜狗输入法安装包", 8, "sogou", "输入法安装程序", when_fn=("sogou_pinyin",)),
    R("v3_brave", "Brave", 8, None, "网页浏览器", when_kw=("bravesoftware",)),
    R("pua_ymzy", "疑似支付欺诈工具（EM_RDP/EMBrowser）", 2, None, "与公开EMV/CNP欺诈工具生态吻合",
      when_kw=("ymzy", "em_rdp", "embrowser"), when_sig=("e-money holding",)),
]


def load_path_kb():
    """路径特征知识库(work/path_kb.json): 溯源批次确认的高置信条目(频次TOP10),
    运行时自动并入规则匹配, 入库无需改引擎代码; feature 以 fn: 开头按文件名匹配。
    条目网址视为入库时已核验, 引擎直接采用。"""
    p = os.path.join(WORK, "path_kb.json")
    if not os.path.exists(p):
        return []
    try:
        entries = json.load(open(p, encoding="utf-8"))
    except Exception:
        return []
    rules = []
    for i, e in enumerate(entries):
        feat = (e.get("feature") or "").strip()
        if not feat:
            continue
        r = {"key": "pkb_%03d" % i, "name": e.get("name"), "score": e.get("score"),
             "url": e.get("url") or None, "intro": e.get("desc"), "ai": bool(e.get("ai")),
             "url_key": None, "kind_hint": e.get("kind") or "known"}
        if feat.startswith("fn:"):
            r["when_fn"] = (feat[3:],)
        else:
            r["when_kw"] = (feat,)
        rules.append(r)
    return rules


def match_known(pd, fd, sd, row, extra=()):
    """按知识库顺序匹配(KNOWN + 路径特征库)，返回 rule 或 None。"""
    for r in list(KNOWN) + list(extra):
        kws = r.get("when_kw")
        if kws and any(k in pd for k in kws):
            return r
        if kws and any(k in fd for k in kws if k.startswith(".")):
            return r
        fns = r.get("when_fn")
        if fns and any(k in fd for k in fns):
            return r
        sgs = r.get("when_sig")
        if sgs and any(s in sd for s in sgs):
            return r
    return None


def judge_all(recs, url_ok=None, blacklist=None):
    url_ok = url_ok or {}
    blacklist = blacklist or []
    kb_rules = load_path_kb()
    out = []
    for row in recs:
        pd, fd, sd = dec(row["norm"]), dec(row["fn"]), dec(row["sig"])
        rec = dict(row)
        rec.update({"kind": None, "name": None, "score": None, "url": None,
                    "intro": None, "ai": False, "gk": None})
        # 黑名单签名：过滤规则最高优先级（商店分发冲突也按黑名单）
        sn = norm_s(sd)
        bl_hit = next((bn for bn in blacklist if bn in sn), None) if sn else None
        # 机械规则
        if bl_hit is not None:
            rec.update(kind="black", name="疑似流氓软件", gk="b|" + sn)
        elif row["help"]:
            rec.update(kind="mech", name="未知", gk="m_help")
        elif row["clickonce"]:
            rec.update(kind="mech", name="应用缓存文件", gk="m_clickonce")
        elif row["unix"]:
            rec.update(kind="mech", name="非Windows样本", gk="m_linux")
        elif row["windowsapps"]:
            pkg = row["pkg"]
            if pkg.startswith("microsoft"):
                rec.update(kind="store_ms", name="Microsoft Windows", score=9, gk="m_store_ms")
            else:
                rec.update(kind="store", name="Microsoft Store", score=9, gk="m_store")
        else:
            r = match_known(pd, fd, sd, row, kb_rules)
            if r is not None:
                hint = r.get("kind_hint")
                if hint == "game" or r["key"].startswith("game_"):
                    rec.update(kind="game", name="游戏", gk="g_" + r["key"])
                elif hint == "pua" or r["key"].startswith("pua_"):
                    name = r["name"]
                    if name.startswith("@"):
                        name = product_name(pd) or "疑似PUA软件（签名命中）"
                    rec.update(kind="pua", name=name, score=r["score"], gk="k_" + r["key"])
                else:
                    name, score = r["name"], r["score"]
                    ai = bool(r.get("ai"))
                    if r.get("ai_copilot") and "\\copilot" in pd:
                        ai = True
                    is_pkb = r["key"].startswith("pkb_")
                    url = r["url"] if (is_pkb or url_ok.get(r["url_key"] or r["key"])) else None
                    rec["url_key"] = r["url_key"] or r["key"]
                    rec.update(kind="known", name=name, score=score, url=url,
                               intro=r["intro"] if url else None, ai=ai, gk="k_" + r["key"])
            else:
                parent = pd.rsplit("\\", 1)[0]
                leaf = parent.rsplit("\\", 1)[-1] if parent else ""
                if leaf in ("downloads", "desktop", "documents", "downloads\\", "desktop\\"):
                    gk = "u|%s|%s" % (parent, fd)
                else:
                    gk = "u|%s" % parent
                rec.update(kind="unknown", name="未知", gk=gk)
        out.append(rec)
    # 未知组统一评分：组内有可辨识签名 -> 5, 否则 4
    gsig = defaultdict(bool)
    for rec in out:
        if rec["kind"] == "unknown":
            gsig[rec["gk"]] = gsig[rec["gk"]] or sig_validish(dec(rec["sig"]))
    for rec in out:
        if rec["kind"] == "unknown":
            rec["score"] = 5 if gsig[rec["gk"]] else 4
    # 组内首行：填 url/intro/备注；其余行清空 url/intro
    seen = set()
    for rec in out:  # out 保持 sorted 顺序
        gk = rec["gk"]
        if gk in seen:
            rec["head"] = False
            rec["url"] = None
            rec["intro"] = None
            rec["ai"] = False
        else:
            seen.add(gk)
            rec["head"] = True
            if not rec.get("url"):
                rec["ai"] = False  # 无网址不标 AI
    return out


def product_name(pd):
    for k, n in [("fastpdf", "FastPDF"), ("masterpdf", "MasterPDF"), ("winclean", "WinCleanApp"),
                 ("xdzipapp", "XDZipApp"), ("wmeiplayer", "WMeiPlayer"), ("dllrepair", "DLLRepair官方版"),
                 ("xdimageshow", "XDImageShow"), ("cadviewer", "CADViewerE"), ("o2wallpaper", "O2Wallpaper"),
                 ("printerhelper", "PrinterHelper"), ("editor", "Editor组件"), ("lenovosoftstore", "联想软件商店软件"),
                 ("wincompress360", "WinCompress360"), ("winmaster", "WinMaster"), ("printmaster", "PrintMaster"),
                 ("2345explorer", "2345浏览器"), ("2345pic", "2345看图王"), ("2345", "2345软件"),
                 ("flashcenter", "Flash中心"), ("winr360", "WinR360"), ("winziper", "WinZiper")]:
        if k in pd:
            return n
    return None


def main():
    recs = json.load(open(os.path.join(WORK, "sorted_rows.json"), encoding="utf-8"))
    vf = os.path.join(WORK, "url_verify.json")
    url_ok = json.load(open(vf, encoding="utf-8")) if os.path.exists(vf) else {}
    if not url_ok:
        trial = judge_all(recs, url_ok={k: True for k in URL_CANDIDATES})
        keys = sorted({r["url_key"] for r in trial if r["head"] and r["url"] and r.get("url_key")})
        for k in keys:
            print("URL_TO_VERIFY\t%s\t%s" % (k, URL_CANDIDATES[k]))
        return
    bl_path = os.path.join(WORK, "blacklist_sigs.json")
    blacklist = [e["norm"] for e in json.load(open(bl_path, encoding="utf-8"))] if os.path.exists(bl_path) else []
    out = judge_all(recs, url_ok, blacklist)
    with open(os.path.join(WORK, "judged_rows.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    c = Counter(r["kind"] for r in out)
    print("KINDS", json.dumps(c, ensure_ascii=False))
    heads = [r for r in out if r["head"] and r["url"]]
    print("HEAD_WITH_URL", len(heads))
    print("SCORE_DIST", json.dumps(dict(Counter(r["score"] for r in out)), ensure_ascii=False))


if __name__ == "__main__":
    main()
