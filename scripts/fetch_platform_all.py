# -*- coding: utf-8 -*-
"""
内部日志数据平台 四部分数据 一键取数 + 整合清洗 脚本
====================================================
同时获取（接口路径 / 视图标识 / 筛选参数 / 字段名 / 单日上限均为占位，使用前按实际接口回填）:
    part1  新样本监控          /api/<内部接口-新样本>  (每日 uv 降序 Top-N)
    part2  灰样本监控-新出现    /api/<内部接口-灰样本>  (每日 uv 降序 Top-N)
    part3  灰样本监控-uv 排序  /api/<内部接口-灰样本>  (当日灰样本 uv 降序全集, 无固定上限)
    part4  安装包监控-uv 排序  /api/<内部接口-安装包>  (当日安装包 uv 降序全集, 无固定上限)

用法:
    python fetch_platform_all.py <开始日期> <结束日期> [--out 输出目录] [--profile Chrome配置目录]
                                 [--keep-json] [--no-clean | --clean-only]

    日期格式 yyyymmdd。输出:
        <out>/new_grey_part1.csv    原始: 新样本监控 (每日 uv 降序 Top-N)
        <out>/new_grey_part2.csv    原始: 灰样本监控-新出现 (每日 uv 降序 Top-N)
        <out>/uvrank_grey_part1.csv 原始: 灰样本监控-uv 排序 (当日灰样本全集)
        <out>/uvrank_grey_part2.csv 原始: 安装包监控-uv 排序 (当日安装包全集)
        <out>/new_grey.csv          清洗: 来源=new,     md5/路径/文件名/签名 四列, 表内 md5 去重
        <out>/uvrank_grey.csv       清洗: 来源=uvrank,  同上
        <out>/grey_final.csv        清洗: 两清洗表再合并, 再次 md5 去重(同 md5 归 new)

说明:
    - 无需手动打开任何页面: 脚本自动连接/拉起 Chrome(复用已登录 profile), 自动打开内网日志数据平台页面,
      现场捕获鉴权头(四部分接口通用), 逐日顺序请求。
      注意: 脚本不操作页面 UI(新出现/uv 排序 复选框、日期控件), 各视图的筛选条件
      由固定查询参数直接编码(参数为占位, 见 PARTS 配置), 页面停留在任何标签都不影响结果。
    - 仅 SSO 会话过期时需要你在弹出的 Chrome 窗口登录一次, 之后脚本自动继续。
    - 单日上限: part1/part2 各有限制(服务端 Top-N, 与页面展示/导出口径一致);
      uvrank 两部分无固定上限。
    - 内置逐日语义校验(字段名占位, 对应键名由 PARTS 的 vkeys 传入):
        new_grey_part1      要求每行「日期」==查询日期;
        new_grey_part2      要求每行「首次出现日」==「日期」==查询日期(即"该日新出现");
        uvrank_grey_part1/2 要求每行「日期」==查询日期、「首次出现日」<=查询日期、uv 降序。
      校验不过则跳过该日并在结束时汇总(部分日容忍, 该日数据不写入 CSV);
      某部分全部日期均失败才中止(exit 5, 不写 CSV)。
    - 鉴权头不落盘、不回显; 浏览器用完保持运行以加速下次调用。
    - 默认取数完成后自动整合清洗: 取 md5/路径/文件名/签名 四列(对应接口字段名为占位, 见 PARTS 配置),
      表内合并按 md5 去重(保留首现行, part1 在前), 插首列「来源」(new/uvrank);
      两清洗表再合并去重(同 md5 归 new), 得 grey_final.csv。
      --no-clean 只出四部分原始表; --clean-only 跳过取数, 仅对 <out> 已有的四部分 CSV 重新清洗(无需浏览器)。
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

CDP_PORT = 9222
CDP = "http://localhost:%d" % CDP_PORT
LOG_PLATFORM_URL = "https://<内网日志平台地址>/<入口路由>"
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]

HDR_DROP = ("host", "content-length", "connection", "accept-encoding", "cookie",
            "user-agent", "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
            "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site")

# 灰样本视图接口字段（新出现 与 uv 排序 两视图共用同一结构）
# ⚠️ 字段名为占位：按原顺序以 f01..f35 表示（序号 = CSV 列序，不可调整顺序）；
#    使用前须按接口实际返回字段名替换。_query_date 为脚本自加列，保留原名。
GREY_VIEW_FIELDS = [
    "f01", "f02", "f03", "f04", "f05", "f06",
    "f07", "f08", "f09", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16",
    "f17", "f18", "f19", "f20", "f21", "f22",
    "f23", "f24", "f25", "f26",
    "f27", "f28", "f29", "f30",
    "f31", "f32", "f33", "f34",
    "f35", "_query_date",
]

# 安装包视图接口字段
# ⚠️ 字段名为占位：按原顺序以 f01..f31 表示（序号 = CSV 列序，不可调整顺序）；
#    使用前须按接口实际返回字段名替换。
PKG_VIEW_FIELDS = [
    "f01", "f02", "f03", "f04", "f05", "f06",
    "f07", "f08", "f09", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16",
    "f17", "f18", "f19",
    "f20", "f21", "f22", "f23", "f24", "f25",
    "f26", "f27", "f28", "f29", "f30",
    "f31", "_query_date",
]

PARTS = [
    {
        "name": "new_grey_part1",
        "api": "/api/<内部接口-新样本>",
        "fixed": "<占位筛选参数>",
        "cap": None,  # 单日上限（按实际接口上限回填；None = 不做上限提示）
        "vtype": "today",
        # 字段名为占位：按原顺序以 f01..f09 表示（序号 = CSV 列序），使用前按实际接口字段名替换
        "fields": ["f01", "f02", "f03", "f04", "f05", "f06", "f07", "f08", "f09", "_query_date"],
        "zh": {"f01": "日期", "f02": "md5", "f03": "路径", "f04": "文件名",
               "f05": "签名", "f06": "级别", "f07": "最新级别",
               "f08": "pv", "f09": "uv", "_query_date": "查询日期"},
        "vkeys": ("f01", "f01", "f09"),  # (日期, 首次出现日, uv)
    },
    {
        "name": "new_grey_part2",
        "api": "/api/<内部接口-灰样本>",
        "fixed": "<排序参数+新出现筛选参数>",
        "cap": None,  # 单日上限（同上，按实际接口上限回填）
        "vtype": "newappear",
        "fields": GREY_VIEW_FIELDS,
        "zh": None,
        "vkeys": ("f35", "f04", "f03"),  # (日期, 首次出现日, uv)
    },
    {
        "name": "uvrank_grey_part1",
        "api": "/api/<内部接口-灰样本>",
        "fixed": "<排序参数>",
        "cap": None,
        "vtype": "uvrank",
        "fields": GREY_VIEW_FIELDS,
        "zh": None,
        "vkeys": ("f35", "f04", "f03"),  # (日期, 首次出现日, uv)
    },
    {
        "name": "uvrank_grey_part2",
        "api": "/api/<内部接口-安装包>",
        "fixed": "<排序参数>",
        "cap": None,
        "vtype": "uvrank",
        "fields": PKG_VIEW_FIELDS,
        "zh": None,
        "vkeys": ("f31", "f04", "f03"),  # (日期, 首次出现日, uv)
    },
]

FETCH_JS = """async (args) => {
    const r = await fetch(args.qs, {credentials: 'include', headers: args.hdrs});
    if (r.status !== 200) return {status: r.status, body: null};
    try { return {status: 200, body: await r.json()}; } catch(e) { return {status: 200, body: null}; }
}"""


def validate_rows(date, rows, vtype, *vkeys):
    """逐行校验日期语义，防止参数/接口语义漂移导致拉错视图。

    vkeys = (日期键, 首次出现日键, uv键)：对应三个字段在返回体中的键名。
    字段名占位后键名可变，由各 PART 的 vkeys 传入；缺省时回退为通用键名。

    vtype = today:     每行「日期」== 查询日期;
    vtype = newappear: 每行「首次出现日」与「日期」都等于查询日期(即"该日新出现");
    vtype = uvrank:    每行「日期」== 查询日期、「首次出现日」<= 查询日期、uv 降序。
    返回 None 表示通过，返回错误消息字符串表示校验失败。
    """
    dayk = vkeys[0] if len(vkeys) > 0 else "day"
    fkey = vkeys[1] if len(vkeys) > 1 else dayk
    uvk = vkeys[2] if len(vkeys) > 2 else "uv"
    if not rows:
        return None
    if vtype == "newappear":
        bad = [r for r in rows if r.get(fkey) != date or r.get(dayk) != date]
    elif vtype == "uvrank":
        bad = [r for r in rows if r.get(dayk) != date
               or not isinstance(r.get(fkey), str) or r[fkey] > date]
        if not bad:
            uvs = [r.get(uvk) for r in rows if isinstance(r.get(uvk), int)]
            if uvs and any(uvs[i] < uvs[i + 1] for i in range(len(uvs) - 1)):
                return "uv 非降序(期望服务端 uv 降序 Top-N)"
    else:
        bad = [r for r in rows if r.get(dayk) != date]
    if bad:
        sample = json.dumps(bad[0], ensure_ascii=False)[:200]
        return "%d/%d 行日期语义不符(期望 %s), 示例: %s" % (len(bad), len(rows), date, sample)
    return None


def log(msg):
    print(msg, flush=True)


# ---------------- 整合清洗（取数成功后自动执行；--clean-only 可单独运行） ----------------

CLEAN_HEADER = ["来源", "md5", "路径", "文件名", "签名"]


def _load_cols(path, idxs, expect):
    """读 CSV，按 1-based 列号取列，先校验表头防止错位。返回 [md5, 路径, 文件名, 签名] 行列表。"""
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    head = rows[0]
    for i, name in zip(idxs, expect):
        if head[i - 1] != name:
            raise ValueError("表头不符 %s: 第%d列=%r 期望=%r" % (os.path.basename(path), i, head[i - 1], name))
    return [[r[i - 1] if i - 1 < len(r) else "" for i in idxs] for r in rows[1:]]


def _dedup_by_md5(tagged):
    """tagged 行 = [来源, md5, 路径, 文件名, 签名]; 以 md5(忽略大小写)去重, 保留首次出现。"""
    seen, out, dups, empty = set(), [], 0, 0
    for r in tagged:
        k = r[1].strip().lower()
        if not k:
            empty += 1
            continue
        if k in seen:
            dups += 1
            continue
        seen.add(k)
        out.append(r)
    return out, dups, empty


def _write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(CLEAN_HEADER)
        w.writerows(rows)


def clean_and_merge(out_dir):
    """四部分原始 CSV -> 列筛选 + md5 去重 + 来源列 -> new_grey.csv / uvrank_grey.csv / grey_final.csv。"""
    p1 = _load_cols(os.path.join(out_dir, "new_grey_part1.csv"), [2, 3, 4, 5],
                    ["md5", "路径", "文件名", "签名"])
    p2 = _load_cols(os.path.join(out_dir, "new_grey_part2.csv"), [1, 7, 9, 13],
                    ["f01", "f07", "f09", "f13"])
    new_dedup, dup_new, empty_new = _dedup_by_md5([["new"] + r for r in p1 + p2])
    _write_csv(os.path.join(out_dir, "new_grey.csv"), new_dedup)

    u1 = _load_cols(os.path.join(out_dir, "uvrank_grey_part1.csv"), [1, 7, 9, 13],
                    ["f01", "f07", "f09", "f13"])
    u2 = _load_cols(os.path.join(out_dir, "uvrank_grey_part2.csv"), [1, 7, 9, 13],
                    ["f01", "f07", "f09", "f13"])
    uv_dedup, dup_uv, empty_uv = _dedup_by_md5([["uvrank"] + r for r in u1 + u2])
    _write_csv(os.path.join(out_dir, "uvrank_grey.csv"), uv_dedup)

    final, dup_final, empty_final = _dedup_by_md5(new_dedup + uv_dedup)
    _write_csv(os.path.join(out_dir, "grey_final.csv"), final)

    log("[clean] new_grey : %d + %d -> 去重删 %d -> %d 行" % (len(p1), len(p2), dup_new, len(new_dedup)))
    log("[clean] uvrank   : %d + %d -> 去重删 %d -> %d 行" % (len(u1), len(u2), dup_uv, len(uv_dedup)))
    log("[clean] final    : %d + %d -> 再去重删 %d -> %d 行 (new=%d, uvrank=%d)"
        % (len(new_dedup), len(uv_dedup), dup_final, len(final),
           sum(1 for r in final if r[0] == "new"), sum(1 for r in final if r[0] == "uvrank")))
    if empty_new or empty_uv:
        log("[clean] 警告: 存在空 md5 行已跳过 (new=%d, uvrank=%d)" % (empty_new, empty_uv))


def default_profile():
    session_profile = os.path.expandvars(
        r"%USERPROFILE%\.platform-fabric\runs\<sessionId>\work\chrome-profile")
    if os.path.isdir(session_profile):
        return session_profile
    return os.path.expandvars(r"%USERPROFILE%\.platform-fetch\chrome-profile")


def cdp_alive():
    import urllib.request
    try:
        with urllib.request.urlopen(CDP + "/json/version", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def launch_chrome(profile):
    for exe in CHROME_CANDIDATES:
        if os.path.exists(exe):
            subprocess.Popen([exe, "--remote-debugging-port=%d" % CDP_PORT,
                              "--user-data-dir=" + profile,
                              "--no-first-run", "--no-default-browser-check",
                              "--window-size=1440,900", LOG_PLATFORM_URL])
            return True
    return False


def date_range(d1, d2):
    import datetime
    a = datetime.datetime.strptime(d1, "%Y%m%d").date()
    b = datetime.datetime.strptime(d2, "%Y%m%d").date()
    if a > b:
        a, b = b, a
    out = []
    while a <= b:
        out.append(a.strftime("%Y%m%d"))
        a += datetime.timedelta(days=1)
    return out


def find_or_open_logpage(ctx):
    page = None
    for pg in ctx.pages:
        if "<内网日志平台地址>" in pg.url:
            page = pg
            break
    if page is None:
        page = ctx.new_page()
        page.goto(LOG_PLATFORM_URL, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    time.sleep(1)
    return page


def ensure_logged_in(page, timeout=300):
    def on_login():
        low = page.url.lower()
        return ("login" in low) or ("<内网样本平台地址>/login" in low)

    if not on_login():
        return True
    log("WAIT_LOGIN: 检测到 SSO 登录页，请在弹出的 Chrome 窗口完成登录（最多等 %d 秒）..." % timeout)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not on_login():
            log("LOGIN_DONE: " + page.url)
            try:
                page.goto(LOG_PLATFORM_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            time.sleep(1)
            return True
        time.sleep(2)
    log("LOGIN_TIMEOUT")
    return False


def capture_auth_headers(page):
    """现场捕获数据接口 XHR 的鉴权头（四部分接口通用）。
    策略: 监听 /api/ 请求; 先强制跳转入口视图（页面挂载必发数据请求,
    不依赖当前停留的视图与"搜索"按钮）; 无捕获再点"搜索"兜底; 仍无则整页刷新。
    """
    captured = []

    def on_request(req):
        if "/api/" in req.url and not req.url.endswith("/api/<日志上报接口>"):
            captured.append(dict(req.headers))

    page.on("request", on_request)
    try:
        page.goto(LOG_PLATFORM_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    for _ in range(10):
        time.sleep(0.5)
        if captured:
            break
    if not captured:  # 兜底1: 点击"搜索"触发查询
        try:
            page.locator("button", has_text="搜 索").first.click(timeout=10000)
        except Exception:
            try:
                page.get_by_text("搜索", exact=True).first.click(timeout=10000)
            except Exception:
                pass
        for _ in range(12):
            time.sleep(0.5)
            if captured:
                break
    if not captured:  # 兜底2: 整页刷新
        try:
            page.reload(wait_until="domcontentloaded", timeout=60000)
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        for _ in range(12):
            time.sleep(0.5)
            if captured:
                break
    page.remove_listener("request", on_request)
    if not captured:
        return None
    return {k: v for k, v in captured[-1].items() if k.lower() not in HDR_DROP}


def main():
    ap = argparse.ArgumentParser(description="内部日志数据平台 四部分数据一键取数")
    ap.add_argument("start", help="开始日期 yyyymmdd")
    ap.add_argument("end", help="结束日期 yyyymmdd")
    ap.add_argument("--out", default=None, help="输出目录（默认: 脚本目录）")
    ap.add_argument("--profile", default=None, help="Chrome user-data-dir")
    ap.add_argument("--keep-json", action="store_true", help="同时保存每日原始 JSON")
    ap.add_argument("--no-clean", action="store_true", help="仅拉取四部分原始数据，不做整合清洗")
    ap.add_argument("--clean-only", action="store_true",
                    help="跳过取数，仅对输出目录已有的四部分 CSV 重新清洗（无需浏览器）")
    args = ap.parse_args()

    try:
        time.strptime(args.start, "%Y%m%d")
        time.strptime(args.end, "%Y%m%d")
    except ValueError:
        log("ERROR: 日期格式应为 yyyymmdd")
        sys.exit(1)
    dates = date_range(args.start, args.end)
    out_dir = args.out or os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    profile = args.profile or default_profile()

    if args.clean_only:
        log("CLEAN_ONLY: 对 %s 中已有的四部分 CSV 重新清洗" % out_dir)
        try:
            clean_and_merge(out_dir)
        except ValueError as e:
            log("ERROR: 清洗失败 -> %s" % e)
            sys.exit(6)
        except FileNotFoundError as e:
            log("ERROR: 输出目录缺少原始部分 CSV -> %s" % e)
            sys.exit(6)
        log("ALL_DONE")
        return

    with sync_playwright() as p:
        if cdp_alive():
            log("ATTACH: 连接已有 Chrome (CDP :%d)" % CDP_PORT)
            browser = p.chromium.connect_over_cdp(CDP)
        else:
            log("LAUNCH: 拉起 Chrome（profile: %s）" % profile)
            if not launch_chrome(profile):
                log("ERROR: 未找到 Chrome")
                sys.exit(2)
            for _ in range(15):
                time.sleep(1)
                if cdp_alive():
                    break
            if not cdp_alive():
                log("ERROR: CDP 端口未就绪；若已有 Chrome 实例占用该 profile，请先关闭后重试")
                sys.exit(2)
            browser = p.chromium.connect_over_cdp(CDP)

        ctx = browser.contexts[0]
        page = find_or_open_logpage(ctx)
        if not ensure_logged_in(page):
            sys.exit(3)

        hdrs = capture_auth_headers(page)
        if not hdrs:
            log("ERROR: 未能捕获鉴权头（页面未发出数据请求），请确认页面加载正常")
            sys.exit(4)
        log("AUTH_OK: 鉴权头已现场捕获（四部分接口通用，不落盘、不回显）")

        summary = {}
        skipped = {}
        for part in PARTS:
            all_rows, per_day = [], {}
            skipped[part["name"]] = []
            for d in dates:
                qs = "%s?date=%s&%s" % (part["api"], d, part["fixed"])
                r = page.evaluate(FETCH_JS, {"qs": qs, "hdrs": hdrs})
                if r["status"] == 401:
                    log("[%s] DAY %s: 401 会话过期 -> 重新登录流程" % (part["name"], d))
                    page.goto(LOG_PLATFORM_URL, wait_until="domcontentloaded", timeout=60000)
                    if not ensure_logged_in(page):
                        sys.exit(3)
                    hdrs = capture_auth_headers(page)
                    if not hdrs:
                        log("ERROR: 重新捕获鉴权头失败")
                        sys.exit(4)
                    r = page.evaluate(FETCH_JS, {"qs": qs, "hdrs": hdrs})
                rows = r.get("body") if isinstance(r.get("body"), list) else []
                per_day[d] = len(rows)
                warn = ""
                if part["cap"] and len(rows) >= part["cap"]:
                    warn += "  [达到单日上限Top%d]" % part["cap"]
                if not rows:
                    warn += "  [警告: 该日 0 行，请人工确认是否符合预期]"
                log("[%s] DAY %s: rows=%d%s" % (part["name"], d, len(rows), warn))
                err = validate_rows(d, rows, part["vtype"], *part["vkeys"])
                if err:
                    log("WARN[%s] DAY %s: 语义校验未过 -> %s" % (part["name"], d, err))
                    log("       部分日容忍: 跳过该日继续（该日数据不写入 CSV），结束时汇总。")
                    skipped[part["name"]].append([d, str(err)[:150]])
                    time.sleep(0.5)
                    continue
                for row in rows:
                    row["_query_date"] = d
                all_rows.extend(rows)
                if args.keep_json:
                    with open(os.path.join(out_dir, "%s_%s.json" % (part["name"], d)), "w", encoding="utf-8") as f:
                        json.dump(rows, f, ensure_ascii=False, indent=1)
                time.sleep(0.5)

            if len(skipped[part["name"]]) >= len(dates):
                log("ERROR[%s]: 全部 %d 天均未通过语义校验，疑似接口语义/登录态系统性问题，已中止不写 CSV。"
                    % (part["name"], len(dates)))
                sys.exit(5)
            csv_path = os.path.join(out_dir, part["name"] + ".csv")
            with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow([part["zh"][x] if part["zh"] else x for x in part["fields"]])
                for row in all_rows:
                    w.writerow([row.get(x, "") for x in part["fields"]])
            summary[part["name"]] = {"rows": len(all_rows), "per_day": per_day, "csv": csv_path}
            log("[%s] MERGED: %d rows -> %s" % (part["name"], len(all_rows), csv_path))

        n_sk = sum(len(v) for v in skipped.values())
        if n_sk:
            log("SKIPPED_REPORT: 部分日容忍共跳过 %d 个部分-日（该日数据未写入，请核对周期完整性）: %s"
                % (n_sk, json.dumps({k: v for k, v in skipped.items() if v}, ensure_ascii=False)))
        log("SUMMARY: " + json.dumps({k: {"rows": v["rows"], "per_day": v["per_day"]}
                                      for k, v in summary.items()}, ensure_ascii=False))

        if not args.no_clean:
            log("CLEAN: 取数完成，开始整合清洗（列筛选 + md5 去重 + 来源列）")
            try:
                clean_and_merge(out_dir)
            except ValueError as e:
                log("ERROR: 清洗失败 -> %s" % e)
                sys.exit(6)
            log("CLEAN_DONE: 已生成 new_grey.csv / uvrank_grey.csv / grey_final.csv")
        log("ALL_DONE")


if __name__ == "__main__":
    main()
