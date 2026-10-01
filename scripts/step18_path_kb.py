# -*- coding: utf-8 -*-
"""step18: 路径特征知识库(work/path_kb.json)维护与导出(outputs/path_kb.csv)。

每次溯源批次完成并经用户过目后, 将当批「路径频次TOP10 且准确性高」的条目入库。
选取口径: 当批确认条目按频次降序, 已在库内的跳过并往后顺延, 补满10条新条目
(或当批确认条目用尽为止)——即"新条目TOP10", 而非"TOP10中出现的新条目"。
    python step18_path_kb.py --add <批次条目.json>   # 合并入库(按 feature 去重, 已有则更新)
    python step18_path_kb.py                        # 仅重新导出 CSV

条目格式(JSON数组):
    {"feature": "路径特征片段, fn: 开头表示按文件名匹配",
     "name": "溯源结果(软件名称)", "desc": "说明", "url": "网站(可空)",
     "score": "分数(game类为null)", "kind": "known|game|pua",
     "ai": "是否AI类", "batch": "来源批次", "date": "入库日期", "rows": "确认时样本行数"}

judge_engine.judge_all 每次运行自动加载 path_kb.json 并入规则匹配,
入库条目无需改引擎代码即对后续研判生效; 网址视为已在入库时核验。
"""
import argparse
import csv
import json
import os

WORK = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(WORK, "path_kb.json")
HEAD = ["路径特征", "溯源结果", "网站", "分数", "说明", "类别", "来源批次", "日期", "样本行数"]


def load():
    if os.path.exists(KB):
        return json.load(open(KB, encoding="utf-8"))
    return []


def save(entries):
    entries.sort(key=lambda e: (str(e.get("batch", "")), -(e.get("rows") or 0)))
    json.dump(entries, open(KB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def export(entries, out):
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(HEAD)
        for e in entries:
            w.writerow([e.get("feature"), e.get("name"), e.get("url") or "",
                        "" if e.get("score") is None else e.get("score"),
                        e.get("desc") or "", e.get("kind") or "known",
                        e.get("batch") or "", e.get("date") or "",
                        e.get("rows") if e.get("rows") is not None else ""])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--add", help="要合并的批次条目 JSON 文件(数组)")
    ap.add_argument("--csv-out",
                    default=os.path.join(os.path.dirname(WORK), "outputs", "path_kb.csv"))
    a = ap.parse_args()
    entries = load()
    if a.add:
        new = json.load(open(a.add, encoding="utf-8"))
        idx = {e.get("feature"): i for i, e in enumerate(entries)}
        added = updated = 0
        for e in new:
            feat = (e.get("feature") or "").strip()
            if not feat:
                continue
            e["feature"] = feat
            if feat in idx:
                entries[idx[feat]].update(e)
                updated += 1
            else:
                entries.append(e)
                idx[feat] = len(entries) - 1
                added += 1
        save(entries)
        print("PATH_KB added=%d updated=%d total=%d" % (added, updated, len(entries)))
    export(entries, a.csv_out)
    print("EXPORT -> %s (%d 条)" % (a.csv_out, len(entries)))


if __name__ == "__main__":
    main()
