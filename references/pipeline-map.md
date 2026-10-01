# 软件研判全流程脚本清单（2026-09-11）

工作区根：`~/.platform-fabric/runs/<sessionId>/`（下文 `work/`、`outputs/` 均指其下）。
运行环境：Windows PowerShell 5.1，需 `$env:PYTHONIOENCODING='utf-8'`。

## 0. 一键入口（outputs/）

| 脚本 | 作用 | 用法 |
|---|---|---|
| `run_platform_pipeline.py` | **总入口**：取数+清洗+研判+关键词候选 | `python outputs/run_platform_pipeline.py <起始日> <结束日> [--out DIR] [--skip-fetch]` |
| `fetch_platform_all.py` | 内网日志数据平台多部分按日取数：part1/part2（各有单日上限）+uvrank1+uvrank2；强制 goto 入口视图捕获 `/api/` 鉴权头（页面挂载必发请求，搜索点击+整页刷新双兜底）；部分日容忍（跳过+SKIPPED_REPORT 汇总，全部失败才 exit 5）；SSO 过期时弹 Chrome 登录一次 | 由 run_platform_pipeline 调用；单独运行同参 |
| `fetch_platform_newapp.py` | 单日新样本视图冻结取数（调试用） | 独立运行 |

## 1. 清洗与研判层（work/）

| 脚本 | 作用 | 输入 → 输出 |
|---|---|---|
| `step12_build.py` | 规范化/排序/机械规则/分组（`+` 传输编码解码、NOISE 目录、路径旗标） | grey_final.csv → sorted_rows.json |
| `judge_engine.py` | **判定单一源**：KB v1+v2+v3 规则、黑名单（blacklist_sigs.json）、path_kb 自动加载（pkb_ 规则）、url_verify.json 网址缓存；输出 KINDS/SCORE_DIST/KW_BACKLOG 统计 | sorted_rows.json → judged_rows.json |
| `step14_blacklist.py` | sign.md 黑名单规范化（小写、仅留字母数字汉字）+命中预演；匹配=黑名单串⊆数据签名串 | work/sign.md → blacklist_sigs.json、blacklist_hits.json |
| `step16_extract_kw.py` | 未定性行关键词提取（厂商目录拆分、paths 证据字段；"tools" 入 NOISE） | judged_rows.json → kw 候选 |
| `step17_adjudicate.py` | **参数化研判 CLI**（替代 step13/15 手工流程）：build_recs（`+` 解码修复在规范化前）→ judge_all → 写 xlsx + kw_candidates.json | `python work/step17_adjudicate.py --csv <源csv> --out <产物目录> --work work` |
| `step18_path_kb.py` | path_kb 维护：`--add <json>` 合并去重（更新同名特征）；每次运行导出 `outputs/path_kb.csv`（列：路径特征\|溯源结果\|网站\|分数\|说明\|类别\|来源批次\|日期\|样本行数） | `python work/step18_path_kb.py [--add kb_batchN.json]` |

## 2. 溯源批次条目（work/kb_batch*.json，入库源）

| 文件 | 内容 |
|---|---|
| `kb_batch3.json` | 批次3：20 条（uv/京东WMS/红谷MES/Saby/敏捷DGS/格瑞普/上位机/MetaTrader/PotPlayer/Anaconda/CLIProxyAPI/潼湖BIS/公文办公/Kimi 等） |
| `kb_batch4.json` | 批次4：21 条（NVIDIA/CodeBuddy/OurPlay/洞察眼/CASD/CodeG/TeleAgent/Typeless/思享排版/企业微信/7-Zip/Clash Verge/MinGW/nvm/FF14/MC基岩/SIPPR/CSS/OMS 等） |
| `kb_batch4b.json` | 批次4补全：1 条（soft\mes，根目录盲区） |
| `kb_batch5.json` | 批次5：10 条（InteRIS/Epic×2/CodeG×2/CodeGeeX/QWMS/MES×3） |
| `kb_batch5b.json` | 批次5补全：5 条（\mes\、mes正式区、mes_v3、plantu mes、pcbpack.dll） |

## 3. 数据与配置（work/）

| 文件 | 作用 |
|---|---|
| `sign.md` | 用户提供的签名黑名单原始文档（372 条→去重 366） |
| `blacklist_sigs.json` / `blacklist_hits.json` | 黑名单规范化库 / 命中明细 |
| `url_verify.json` | 网址可达性缓存（实测 200 才 true） |
| `path_kb.json` | **路径特征知识库机器库**（77 条，引擎自动加载，溯源批次产物） |
| `sorted_rows.json` / `judged_rows.json` | 最后一次运行数据集的中间态（会被后跑的数据集覆盖，主库核对需用 xlsx） |
| `probe_day.py` | 只读探测接口「日期/首次出现日」字段分布（排查"当日数据未生成静默回退"） |

## 4. 历史一次性脚本（work/，已由现行管线取代，留档）

| 脚本组 | 说明 |
|---|---|
| `step1_platform_fetch.py` ~ `step9_pull_pkgview.py`（step1b/1c/1d、step2、step3a-3d、step4、step5a/5b、step6、step7、step8、step9/9_check） | 早期内网日志数据平台页面/API 探测与取数开发链（四个视图逐个击破），已被 `fetch_platform_all.py` 整合取代 |
| `step10_clean_merge.py` / `step10_check.py` / `verify_md5.py` / `verify_md5_clean.py` | 首批数据清洗合并与 md5 校验 |
| `step11_recon.py` | 数据侦察（来源/签名分布） |
| `step13_sample.py` / `step13_write_xlsx.py` | 样例 xlsx（739 行口径确认用） |
| `step15_write_full.py` / `step15b_verify.py` | 首批全量 xlsx 写入 + pandas 校验（校验逻辑仍可复用） |
| `step14b_inspect.py` | 黑名单命中人工检查 |
| `q1_*.py` ~ `q16_*.py`（q1_workbuddy、q2_pathcheck、q3_engineview、q4_kwinspect、q5_verify_e2e、q6_top30、q7_batch1_check、q8_legacy_id、q9_legacy_main、q10_legacy_check、q11_topkw、q12_ctx、q13_batch2_check、q14_ctx、q15_batch3、q16_batch4） | 各批次离线证据收集/边界核查/回归验证的一次性诊断脚本 |

## 5. 产物（outputs/）

| 文件 | 说明 |
|---|---|
| `grey_final.csv` | 主库源数据（18628 行：来源\|md5\|路径\|文件名\|签名） |
| `grey_final_result.xlsx` | **主库全量研判结果** |
| `test_e2e/grey_final.csv` / `test_e2e/grey_final_result.xlsx` | e2e 验证数据集（20260805-0811，19291 行）及结果 |
| `kw_candidates.json`（双库各自 out 目录） | 未定性行关键词候选（溯源输入） |
| `path_kb.csv` | 路径特征知识库人读导出（77 条） |
| `溯源_batch1~5_检索结果.md` | 各批检索证据清单 |
| `软件研判任务prompt.md` | 任务 prompt v11（本次更新版；Desktop 原件在会话可写根外） |

## 6. 管线数据流

```
run_platform_pipeline.py <起> <止>
  └─ fetch_platform_all.py（内网日志数据平台取数, 鉴权头捕获, 部分日容忍）
       └─ grey_final.csv
  └─ step17_adjudicate.py --csv ... --out ... --work work
       ├─ step12_build.build_recs（排序/规范化/'+'解码/分组）→ sorted_rows.json
       ├─ judge_engine.judge_all（KB+黑名单+path_kb 自动加载）→ judged_rows.json
       ├─ grey_final_result.xlsx（研判 5 列）
       └─ kw_candidates.json（未定性行关键词）

溯源批次闭环：
kw_candidates（行数降序）→ 离线证据(q*.py) + 联网检索(3个/轮) → 用户过目(高/中/存疑)
  → work/kb_batchN.json → step18_path_kb.py --add（path_kb.json + path_kb.csv）
  → step17 重跑双库 → 核对命中/误伤 → 更新 backlog → 下一批
```
