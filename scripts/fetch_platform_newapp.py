# -*- coding: utf-8 -*-
"""
内部日志数据平台「新样本监控」冻结取数脚本
===========================================
用法:
    python fetch_platform_newapp.py <开始日期> <结束日期> [--out 输出目录] [--profile Chrome配置目录] [--keep-json]

    日期格式: yyyymmdd，如 20260901
    示例:
        python fetch_platform_newapp.py 20260901 20260907
        python fetch_platform_newapp.py 20260901 20260907 --out D:\\data --keep-json

行为:
    1. 优先连接已运行且开启调试端口(9222)的 Chrome；连不上则自动拉起 Chrome（复用指定 profile）。
    2. 自动打开内网日志数据平台「新样本监控」页面；若 SSO 过期会弹窗等待你登录一次。
    3. 现场捕获页面真实 XHR 的鉴权头（不落盘、不回显），逐天重放数据接口。
    4. 合并导出 CSV（utf-8-sig，Excel 可直接打开），文件名含日期区间。
    5. 浏览器保持运行，便于下次快速调用。

说明:
    - 接口存在单日硬上限（按 uv 降序 Top-N），与页面「导出全部数据」的口径一致。
    - 单日返回 401 时脚本会自动尝试重新登录流程后重试。
    - 接口路径 / 筛选参数 / 字段名均为占位，使用前按实际接口回填（见 API_PATH / FIELDS）。
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
API_PATH = "/api/<内部接口-新样本>"
CAP = None  # 单日上限（按实际接口上限回填；None = 不做上限提示）

# 字段名为占位：按原顺序以 f01..f09 表示（序号 = CSV 列序），使用前按实际接口字段名替换
FIELDS = ["f01", "f02", "f03", "f04", "f05", "f06", "f07", "f08", "f09", "_query_date"]
ZH = {"f01": "日期", "f02": "md5", "f03": "路径", "f04": "文件名",
      "f05": "签名", "f06": "级别", "f07": "最新级别",
      "f08": "pv", "f09": "uv", "_query_date": "查询日期"}


def log(msg):
    print(msg, flush=True)


def default_profile():
    # 优先沿用本会话已登录的 profile；不存在则用脚本自带的默认目录
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
    """若被重定向到登录页，等待用户手动完成登录。"""
    def on_login():
        low = page.url.lower()
        return ("login" in low) or ("<内网样本平台地址>/login" in low) or ("auth" in low and "<内网日志平台地址>" not in low)

    if not on_login() and page.locator("button", has_text="搜").count() > 0:
        return True
    if not on_login():
        # 页面结构可能未就绪，再等一次
        time.sleep(3)
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
    """触发一次页面搜索，现场捕获入口视图 XHR 的请求头。"""
    captured = []

    def on_request(req):
        if API_PATH in req.url:
            captured.append(dict(req.headers))

    page.on("request", on_request)
    btn = page.locator("button", has_text="搜 索").first
    try:
        btn.click(timeout=10000)
    except Exception:
        page.get_by_text("搜索", exact=True).first.click(timeout=10000)
    for _ in range(20):
        time.sleep(0.5)
        if captured:
            break
    page.remove_listener("request", on_request)
    if not captured:
        return None
    drop = ("host", "content-length", "connection", "accept-encoding", "cookie",
            "user-agent", "sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform",
            "sec-fetch-dest", "sec-fetch-mode", "sec-fetch-site")
    return {k: v for k, v in captured[-1].items() if k.lower() not in drop}


FETCH_JS = """async (args) => {
    const r = await fetch(args.qs, {credentials: 'include', headers: args.hdrs});
    if (r.status !== 200) return {status: r.status, body: null};
    try { return {status: 200, body: await r.json()}; } catch(e) { return {status: 200, body: null}; }
}"""


def fetch_day(page, hdrs, date):
    r = page.evaluate(FETCH_JS, {"qs": "%s?date=%s&<占位筛选参数>" % (API_PATH, date), "hdrs": hdrs})
    if r["status"] != 200:
        return r["status"], None
    rows = r["body"] if isinstance(r.get("body"), list) else []
    return 200, rows


def main():
    ap = argparse.ArgumentParser(description="内部日志数据平台 新样本监控 冻结取数脚本")
    ap.add_argument("start", help="开始日期 yyyymmdd")
    ap.add_argument("end", help="结束日期 yyyymmdd")
    ap.add_argument("--out", default=None, help="输出目录（默认: 脚本目录/exports）")
    ap.add_argument("--profile", default=None, help="Chrome user-data-dir")
    ap.add_argument("--keep-json", action="store_true", help="同时保存每日原始 JSON")
    args = ap.parse_args()

    d1, d2 = args.start, args.end
    try:
        t1, t2 = time.strptime(d1, "%Y%m%d"), time.strptime(d2, "%Y%m%d")
    except ValueError:
        log("ERROR: 日期格式应为 yyyymmdd")
        sys.exit(1)
    if t1 > t2:
        d1, d2 = d2, d1
    dates = []
    cur = time.strptime(d1, "%Y%m%d")
    end = time.strptime(d2, "%Y%m%d")
    while cur <= end:
        dates.append(time.strftime("%Y%m%d", cur))
        cur = time.struct_time((cur.tm_year, cur.tm_mon, cur.tm_mday + 1) + tuple(cur[i] for i in range(3, 9)))
        cur = time.strptime(time.strftime("%Y%m%d", cur), "%Y%m%d")

    out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
    os.makedirs(out_dir, exist_ok=True)
    profile = args.profile or default_profile()

    with sync_playwright() as p:
        browser = None
        if cdp_alive():
            log("ATTACH: 连接已有 Chrome (CDP :%d)" % CDP_PORT)
            browser = p.chromium.connect_over_cdp(CDP)
        else:
            log("LAUNCH: 拉起 Chrome（profile: %s）" % profile)
            if not launch_chrome(profile):
                log("ERROR: 未找到 Chrome，请安装或用 --profile 指定配置目录后手动打开页面")
                sys.exit(2)
            for _ in range(15):
                time.sleep(1)
                if cdp_alive():
                    break
            if not cdp_alive():
                log("ERROR: CDP 端口未就绪；若你已有一个 Chrome 实例占用了该 profile，请先关闭后重试")
                sys.exit(2)
            browser = p.chromium.connect_over_cdp(CDP)

        ctx = browser.contexts[0]
        page = find_or_open_logpage(ctx)
        if not ensure_logged_in(page):
            sys.exit(3)

        hdrs = capture_auth_headers(page)
        if not hdrs:
            log("ERROR: 未能捕获鉴权头（页面未发出入口视图请求），请确认页面已正常加载")
            sys.exit(4)
        log("AUTH_OK: 鉴权头已现场捕获（不落盘、不回显）")

        all_rows, per_day = [], {}
        for d in dates:
            status, rows = fetch_day(page, hdrs, d)
            if status == 401:
                log("DAY %s: 401 会话过期 -> 尝试重新登录" % d)
                page.goto(LOG_PLATFORM_URL, wait_until="domcontentloaded", timeout=60000)
                if not ensure_logged_in(page, timeout=300):
                    sys.exit(3)
                hdrs = capture_auth_headers(page)
                if not hdrs:
                    log("ERROR: 重新捕获鉴权头失败")
                    sys.exit(4)
                status, rows = fetch_day(page, hdrs, d)
            rows = rows or []
            per_day[d] = len(rows)
            log("DAY %s: status=%s rows=%d%s" % (d, status, len(rows),
                "  [达到单日上限，实际数据可能更多]" if (CAP and len(rows) >= CAP) else ""))
            for row in rows:
                row["_query_date"] = d
            all_rows.extend(rows)
            if args.keep_json:
                with open(os.path.join(out_dir, "newapp_%s.json" % d), "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=1)
            time.sleep(0.5)

        csv_path = os.path.join(out_dir, "newapp_%s_%s_merged.csv" % (d1, d2))
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow([ZH[x] for x in FIELDS])
            for row in all_rows:
                w.writerow([row.get(x, "") for x in FIELDS])

        log("PER_DAY: " + json.dumps(per_day))
        log("MERGED: %d rows -> %s" % (len(all_rows), csv_path))
        log("ALL_DONE")


if __name__ == "__main__":
    main()
