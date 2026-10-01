# -*- coding: utf-8 -*-
"""path_kb.json -> outputs/path_kb数据库.md（按批次分组表格导出）"""
import json
import os

WORK = os.path.dirname(os.path.abspath(__file__))
kb = json.load(open(os.path.join(WORK, "path_kb.json"), encoding="utf-8"))
TICK = chr(96)  # 反引号

groups = {}
for e in kb:
    groups.setdefault(e.get("batch", "早期"), []).append(e)

order = ["种子(批次1+遗留身份)", "早期", "批次1", "批次2", "批次3", "批次4", "批次5"]


def key(b):
    for i, o in enumerate(order):
        if o in b:
            return (i, b)
    return (99, b)


lines = [
    "# 路径特征知识库（path_kb 数据库导出）",
    "",
    "> 生成日期：2026-09-11｜总条目：**%d**｜机器库：work/path_kb.json（研判引擎自动加载，判定优先级：黑名单 > 内置规则 > 本库）｜人读CSV：outputs/path_kb.csv" % len(kb),
    "",
    "特征带 `fn:` 前缀按文件名匹配，否则按路径子串匹配；网址为入库时实测可达（留空=无可达官网）。",
    "",
]
for b in sorted(groups, key=key):
    es = sorted(groups[b], key=lambda x: -x.get("rows", 0))
    lines.append("## %s（%d 条）" % (b, len(es)))
    lines.append("")
    lines.append("| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for e in es:
        f = e["feature"].replace("|", "\\|")
        n = e["name"].replace("|", "\\|")
        d = e.get("desc", "").replace("|", "\\|")
        u = e.get("url", "") or "-"
        ai = "AI" if e.get("ai") else ""
        sc = e.get("score", "")
        sc = "" if sc is None else sc
        lines.append(
            "| %s%s%s | %s | %s | %s | %s | %s | %s | %s |"
            % (TICK, f, TICK, n, u, sc, e.get("kind", "known"), ai, e.get("rows", ""), d)
        )
    lines.append("")
lines += [
    "---",
    "",
    "统计：known=%d / game=%d / pua=%d；AI 标注=%d；带网址=%d"
    % (
        sum(1 for e in kb if e.get("kind") == "known"),
        sum(1 for e in kb if e.get("kind") == "game"),
        sum(1 for e in kb if e.get("kind") == "pua"),
        sum(1 for e in kb if e.get("ai")),
        sum(1 for e in kb if e.get("url")),
    ),
    "",
]
out = os.path.join(WORK, "..", "outputs", "path_kb数据库.md")
open(out, "w", encoding="utf-8").write("\n".join(lines))
print("written", len(kb), "entries ->", os.path.abspath(out))
