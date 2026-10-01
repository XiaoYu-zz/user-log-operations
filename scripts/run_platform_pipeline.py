# -*- coding: utf-8 -*-
"""
内网日志数据平台 灰样本 全流程一键管线: 数据获取 → 数据清洗 → 软件研判溯源
==========================================================================
用法:
    python run_platform_pipeline.py <开始日期> <结束日期> [--out 输出目录] [--work 工作目录]
                                    [--skip-fetch]
    日期格式 yyyymmdd（也接受 2026-09-11）。单日传入相同日期即可。

产物(<out> 下):
    new_grey_part1/2.csv, uvrank_grey_part1/2.csv   原始四部分
    new_grey.csv / uvrank_grey.csv / grey_final.csv  清洗合并(来源|md5|路径|文件名|签名)
    grey_final_result.xlsx                          研判结果全量(10 列)
    kw_candidates.json                              溯源待查关键词(行数降序=重点溯源优先级)

流程:
    1) 取数+清洗: 调用同目录 fetch_platform_all.py —— 自动连接/拉起 Chrome 捕获鉴权,
       仅 SSO 过期时需要在弹出的 Chrome 里登录一次; 完成后自动整合清洗出 grey_final.csv。
    2) 研判溯源: 调用 work/step17_adjudicate.py —— 规范化/排序/分组 → 知识库+黑名单判定
       → 全量 xlsx + 溯源关键词候选清单。
--skip-fetch: 跳过取数(无需浏览器), 仅对 <out>/grey_final.csv 重新研判。
"""
import argparse
import os
import subprocess
import sys


def norm_date(s):
    return s.replace("-", "").replace("/", "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start", nargs="?", default=None, help="开始日期 yyyymmdd")
    ap.add_argument("end", nargs="?", default=None, help="结束日期 yyyymmdd")
    ap.add_argument("--out", default=None, help="输出目录(默认脚本所在 outputs 目录)")
    ap.add_argument("--work", default=None, help="工作目录(默认 <脚本上级>/work)")
    ap.add_argument("--skip-fetch", action="store_true", help="跳过取数, 仅重新研判")
    a = ap.parse_args()
    if not a.skip_fetch and (not a.start or not a.end):
        ap.error("需要 <开始日期> <结束日期>（或使用 --skip-fetch 跳过取数）")
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.abspath(a.out) if a.out else here
    work = os.path.abspath(a.work) if a.work else os.path.join(os.path.dirname(here), "work")
    os.makedirs(out, exist_ok=True)
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    py = sys.executable

    if not a.skip_fetch:
        cmd = [py, os.path.join(here, "fetch_platform_all.py"),
               norm_date(a.start), norm_date(a.end), "--out", out]
        print("[1/2] 取数+清洗:", " ".join(cmd), flush=True)
        rc = subprocess.call(cmd, env=env)
        if rc != 0:
            sys.exit("[1/2] 取数失败(exit %d): 若 SSO 过期, 请在弹出的 Chrome 窗口完成登录后重试" % rc)
    else:
        print("[1/2] 跳过取数(--skip-fetch)", flush=True)

    csvp = os.path.join(out, "grey_final.csv")
    if not os.path.exists(csvp):
        sys.exit("缺少 %s : 先执行取数, 或去掉 --skip-fetch" % csvp)

    cmd = [py, os.path.join(work, "step17_adjudicate.py"),
           "--csv", csvp, "--out", out, "--work", work]
    print("[2/2] 研判溯源:", " ".join(cmd), flush=True)
    rc = subprocess.call(cmd, env=env)
    if rc != 0:
        sys.exit("[2/2] 研判失败(exit %d)" % rc)
    print("完成: %s" % out, flush=True)


if __name__ == "__main__":
    main()
