# 溯源批次2 检索结果（主库 18628 行，2026-09-11）

候选来源：outputs/kw_candidates.json（主库 top30）+ 本地路径核查 + 联网检索 13 次。

## ⚠️ 重点发现：疑似支付欺诈工具（需单独定性）

| 关键词 | 行数 | 结论 | 证据 |
|---|---|---|---|
| ymzy | 11 | **疑似支付欺诈工具（EM_RDP/EMBrowser）** | 签名 e-money holding co., ltd.；em_rdp.exe、embrowser.exe 与公开 EMV/CNP 欺诈工具生态（EM_RDP "CNP fraud 专用"、EMBrowser、non-VBV BIN、CVV shop）名称完全吻合；emtool/em_rdp 模块结构 |

## ✅ 检索确认（6 条）

| 关键词 | 行数 | 结论 | 证据 | 建议 |
|---|---|---|---|---|
| cowork | 17 | Claude Desktop Cowork 组件 | deeplink-cowork 安装 staging；openconsole/rg/winpty/elevate 与 Claude Code Windows 工具链吻合；Cowork 为 Claude 桌面版 agentic 功能 | known 8 分，AI 标注 |
| cpoc | 22 | 景桥软件 CPOC 客户端 | 签名南京景桥软件有限公司（2006 年成立、存续）；Qt6 客户端 | known 7 分 |
| qpct | 12 | 青岛港 CSP 集装箱码头操作系统 | QPCT=青岛前湾集装箱码头；CSP=山东港口科通（原补天科技）码头操作系统 | known 7 分 |
| pyhanko | 27 | PyHanko PDF 签名组件 | 开源 Python PDF 数字签名库（pyhanko + pyhanko_certvalidator） | known 7 分 |
| renjiaojiaoxueyi | 12 | 人教教学易 | 人教社多媒体教学软件（电子讲台）；注意：该品牌曾被仿冒做投资诈骗 App，与桌面教学软件无关 | known 7 分 |
| protect/wsus | 21 | 厦门尚沃网络组件 | 签名厦门尚沃网络科技（邮件营销 ESP）；msextract/realinfo 与其邮件基础设施品牌吻合；性质偏灰 | known 4 分（偏灰谨慎） |

## 🟦 离线高置信（7 条，本地证据充分）

| 关键词 | 行数 | 结论 | 证据 | 建议 |
|---|---|---|---|---|
| yuanbao | 21 | 腾讯元宝 | tencent\yuanbao + Tencent Technology 签名 | known 9 分，AI 标注，网址 yuanbao.tencent.com ✅200 |
| sysnative 等 | 21 | Microsoft Windows | \windows\sysnative、driverstore、grouppolicy 均系统目录（ms_windows 规则补路径） | ms_windows 补 "\\sysnative"/"\\driverstore"/"\\grouppolicy" |
| bravesoftware | ~10 | Brave 浏览器 | program files\bravesoftware\brave-browser | known 8 分，网址不可达留空 |
| fn:sogou_pinyin | 18 | 搜狗输入法安装包 | 安装包自述名（需引擎新增 when_fn 文件名匹配） | known 8 分，复用 sogou 网址 |
| workbuddy 平铺 | 8 | 腾讯 WorkBuddy | workbuddysharetarget.msix | v2_workbuddy 关键词 ".workbuddy"→"workbuddy" |
| .dbx 未签名行 | 7 | 同簇继承宇界 PUA | 同目录已签名行命中宇界工作室 PUA 规则 | pua_yujie 补 when_kw ".dbx"，4 分 |
| mes正式区客户端 | 14 | MES 正式区客户端 | 目录自述名 + yjcommon/dal 模块结构 | known 6 分（企业内部） |

## ⏸ 待定（保持未知）

- **v01sec 48 行**（最大单桶，无任何公开信息；axinstall.exe 有 ActiveX 安装器迹象，持续观察）
- teleagent 22（Teleport 内部 agent 代号线索弱，python 组件，存疑）
- 潼湖bis 13、lip正式客户端 15（企业内部系统迹象，无公开信息）
- cockpit tools 11、cpoc 深挖、rmes_client 10（搜索降级/未及检索，留批次3）
- fn:exe / software 混合组：建议 "software" 入 NOISE 拆分（五笔输入法、deepseek harness 等各自成词）

## 引擎配套改动（随本批）

when_fn 文件名匹配支持；ms_windows 补 3 个系统目录；v2_workbuddy/pua_yujie 关键词扩展；"software" 入 NOISE。

## 来源

- Claude Cowork: [About Cowork Beta (Anthropic Support)](https://support.anthropic.com/en/articles/12756597-about-cowork-beta)、[Claude Code Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- EM_RDP/EMBrowser 欺诈生态: paymenttools.com 相关公开页面（营销语明确提及 CNP fraud / cardable sites / CVV shops）
- QPCT/CSP: [QQCT 官网](https://qqct.com.cn)、[青岛港 CSP 门户](https://csp.qingdao-port.com)
- 南京景桥: [爱企查](https://aiqicha.baidu.com/s?q=南京景桥软件科技有限公司)
- pyHanko: [GitHub](https://github.com/matthiasvalstar/pyhanko)、[文档](https://pyhanko.readthedocs.io/)
- 人教教学易: 公开检索（含仿冒预警提示）
- 厦门尚沃: realinfo.cn 邮件基础设施公开讨论
