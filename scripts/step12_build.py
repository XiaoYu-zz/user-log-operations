# -*- coding: utf-8 -*-
"""Step 12: 软件研判管线第一步 — 规范化/排序/机械规则/自动分组, 产出分组全景概览。
判定原则遵循 Desktop/软件研判任务prompt.md v10; 本脚本只做结构化, 不做判定。
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(CWD, "outputs")
WORK = os.path.join(CWD, "work")

ENV_MAP = [
    ("%localappdata%", r"@up\appdata\local"),
    ("%appdata%", r"@up\appdata\roaming"),
    ("%userprofile%", "@up"),
    ("%programfiles(x86)%", r"c:\program files (x86)"),
    ("%programfiles%", r"c:\program files"),
    ("%programdata%", r"c:\programdata"),
    ("%systemroot%", r"c:\windows"),
    ("%windir%", r"c:\windows"),
    ("%public%", r"c:\users\public"),
    ("%temp%", r"@up\appdata\local\temp"),
    ("%homepath%", "@up"),
]

GENERIC = {"windows", "program files", "program files (x86)", "programdata", "appdata",
           "local", "roaming", "temp", "users", "user", "public", "common files",
           "microsoft", "shared", "download", "downloads", "install", "update",
           "packages", "apps", "bin", "lib", "data", "files"}


def norm_path(p):
    s = p.strip().lower().replace("/", "\\")
    s = re.sub(r"\\+", r"\\", s)
    for k, v in ENV_MAP:
        if s.startswith(k):
            s = v + s[len(k):]
            break
    # 缺盘符前缀补全（仅规范化用）
    for pref, full in [(r"\program files (x86)", r"c:\program files (x86)"),
                       (r"\program files", r"c:\program files"),
                       (r"\programdata", r"c:\programdata"),
                       (r"\windows", r"c:\windows")]:
        if s.startswith(pref):
            s = full + s[len(pref):]
            break
    return s


def flags(norm):
    f = {}
    f["help"] = norm == r"c:\windows\help" or norm.startswith(r"c:\windows\help")
    f["clickonce"] = r"\apps\2.0" in norm
    f["windowsapps"] = r"program files\windowsapps" in norm
    pkg = ""
    if f["windowsapps"]:
        m = re.search(r"windowsapps\\([^\\]+)", norm)
        if m:
            pkg = re.sub(r"^\d+", "", m.group(1).split("_")[0])
    f["pkg"] = pkg
    return f


def group_root(norm):
    """自动分组根：识别软件归属目录（启发式, 供判定用）。返回 (root, tag)。"""
    parts = norm.split("\\")
    if r"c:\windows" == norm or norm.startswith(r"c:\windows\\"):
        return ("@win", "ms")
    if norm.startswith(r"c:\windows\\"):
        seg = parts[2] if len(parts) > 2 else ""
        return ("@win\\" + seg, "ms")
    if norm.startswith(r"c:\program files\windowsapps"):
        return ("@store\\" + (re.search(r"windowsapps\\([^\\]+)", norm).group(1)), "store")
    if r"\steam\steamapps" in norm or r"\steamlibrary\steamapps" in norm:
        return ("@game\\steam", "game")
    for base, tag in [(r"@up\appdata\local\programs", "app"), (r"@up\appdata\local", "app"),
                      (r"@up\appdata\roaming", "app")]:
        if norm.startswith(base + "\\"):
            seg = parts[3] if base.count("\\") == 2 and len(parts) > 3 else parts[-1]
            # 取该基准后第一段
            idx = len(base.split("\\"))
            seg = parts[idx] if len(parts) > idx else seg
            if seg and seg not in GENERIC:
                return ("%s\\%s" % (base, seg), tag)
            return (base, tag)
    for base, label in [(r"c:\program files (x86)", "pf"), (r"c:\program files", "pf"),
                        (r"c:\programdata", "pd")]:
        if norm.startswith(base + "\\"):
            idx = len(base.split("\\"))
            seg = parts[idx] if len(parts) > idx else ""
            if seg in GENERIC or seg == "microsoft":
                seg2 = parts[idx + 1] if len(parts) > idx + 1 else ""
                if seg2:
                    return ("%s\\%s\\%s" % (base, seg, seg2), label)
                return (base, label)
            if seg:
                return ("%s\\%s" % (base, seg), label)
            return (base, label)
    head = "\\".join(parts[:2]) if len(parts) >= 2 else norm
    return (head, "raw")


def main():
    rows = list(csv.reader(open(os.path.join(OUT, "grey_final.csv"), encoding="utf-8-sig")))
    body = rows[1:]
    recs = []
    for r in body:
        src, md5, path, fn, sig = r[0], r[1], r[2], r[3], r[4]
        raw = path.strip()
        np_ = norm_path(path)
        unix = raw.startswith("/") or raw.startswith("~")  # 真正 Linux/Unix 风格
        unc = raw.startswith("\\\\")
        fl = flags(np_)
        root, tag = group_root(np_)
        recs.append({"src": src, "md5": md5, "path": path, "norm": np_, "fn": fn,
                     "sig": sig, "unix": unix, "unc": unc, **fl, "root": root, "tag": tag})

    # 排序: 路径升序(忽略大小写, 已 lower), 同路径按文件名, 再 md5
    recs.sort(key=lambda x: (x["norm"], x["fn"].strip().lower(), x["md5"]))

    with open(os.path.join(WORK, "sorted_rows.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False)

    # 概览
    lines = []
    n = len(recs)
    lines.append("TOTAL %d" % n)
    mech = {
        "help": sum(1 for r in recs if r["help"]),
        "clickonce": sum(1 for r in recs if r["clickonce"]),
        "windowsapps": sum(1 for r in recs if r["windowsapps"]),
        "linux": sum(1 for r in recs if r["unix"]),
        "unc": sum(1 for r in recs if r["unc"]),
        "rooted_win": sum(1 for r in recs if not r["unix"] and not r["unc"]
                          and not re.match(r"^[a-z]:\\", r["norm"]) and not r["norm"].startswith("@")),
        "no_sig": sum(1 for r in recs if r["sig"] == "\\N"),
    }
    lines.append("MECH " + json.dumps(mech))
    unix_ex = [r["path"] for r in recs if r["unix"]][:8]
    unc_ex = [r["path"] for r in recs if r["unc"]][:8]
    lines.append("LINUX_EX " + json.dumps(unix_ex, ensure_ascii=False))
    lines.append("UNC_EX " + json.dumps(unc_ex, ensure_ascii=False))

    sigs_all = Counter(r["sig"] for r in recs if r["sig"] != "\\N")
    for s, c in sigs_all.most_common():
        lines.append("SIG %d\t%s" % (c, s))

    by_root = defaultdict(list)
    for r in recs:
        by_root[r["root"]].append(r)
    lines.append("ROOTS %d" % len(by_root))
    top = sorted(by_root.items(), key=lambda kv: -len(kv[1]))
    for root, rs in top[:150]:
        sigs = Counter(x["sig"] for x in rs if x["sig"] != "\\N")
        fns = Counter(x["fn"].strip().lower() for x in rs)
        ex_path = rs[0]["path"][:100]
        lines.append("ROOT[%s|%d] sig=%s fn=%s ex=%s" % (
            root, len(rs),
            sigs.most_common(3), fns.most_common(3), ex_path))
    with open(os.path.join(WORK, "overview.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("BUILT: sorted_rows.json(%d) + overview.txt roots=%d" % (n, len(by_root)))


if __name__ == "__main__":
    main()
