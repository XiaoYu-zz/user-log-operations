# 路径特征知识库（path_kb 数据库导出）

> 生成日期：2026-09-11｜总条目：**77**｜机器库：work/path_kb.json（研判引擎自动加载，判定优先级：黑名单 > 内置规则 > 本库）｜人读CSV：outputs/path_kb.csv

特征带 `fn:` 前缀按文件名匹配，否则按路径子串匹配；网址为入库时实测可达（留空=无可达官网）。

## 批次1（8 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `hearthstone` | 游戏（炉石传说） | https://hs.blizzard.cn/ |  | game |  | 122 | 暴雪集换式卡牌游戏 |
| `ylgame` | 游戏（ylgame对战平台） | - |  | game |  | 47 | 杭州战英网络街机格斗对战平台 |
| `铁四院` | 铁四院智能勘察设计平台 | - | 7 | known |  | 41 | 中铁第四勘察设计院自研设计平台 |
| `devicetesttools` | 内部测试工具 | - | 5 | known |  | 35 | 疑似企业内部测试工具(selenium组件) |
| `teamviewer` | TeamViewer | https://www.teamviewer.com/ | 8 | known |  | 25 | 远程控制软件 |
| `tencent\xwechat` | 微信 | https://weixin.qq.com/ | 9 | known |  | 24 | 腾讯微信4.0 |
| `元游棋牌大厅` | 游戏（元游棋牌大厅） | - |  | game |  | 24 | 上海元游网络棋牌游戏 |
| `msconfig` | 疑似伪装系统工具 | - | 2 | pua |  | 14 | 目录名伪装Windows系统工具 |

## 批次2（10 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `pyhanko` | PyHanko PDF签名组件 | https://pyhanko.readthedocs.io/ | 7 | known |  | 27 | 开源PDF数字签名工具库 |
| `cpoc` | 景桥软件CPOC客户端 | - | 7 | known |  | 22 | 南京景桥软件联络中心系统 |
| `yuanbao` | 腾讯元宝 | https://yuanbao.tencent.com/ | 9 | known | AI | 21 | 腾讯AI助手 |
| `protect\wsus` | 厦门尚沃网络组件 | - | 4 | known |  | 21 | 邮件营销ESP相关组件 |
| `sogou_pinyin` | 搜狗输入法安装包 | https://pinyin.sogou.com/ | 8 | known |  | 18 | 搜狗输入法安装程序 |
| `deeplink-cowork` | Claude Cowork组件 | - | 8 | known | AI | 17 | Claude桌面版智能工作组件 |
| `mes正式区客户端` | MES正式区客户端（企业内部） | - | 6 | known |  | 14 | 制造执行系统正式区客户端 |
| `qpct` | 青岛港CSP码头操作系统 | - | 7 | known |  | 12 | 山东港口科通CSP集装箱码头系统 |
| `renjiaojiaoxueyi` | 人教教学易 | - | 7 | known |  | 12 | 人民教育出版社教学软件 |
| `ymzy` | 疑似支付欺诈工具（EM_RDP/EMBrowser） | - | 2 | pua |  | 11 | e-money holding, 与公开EMV/无卡支付欺诈工具生态吻合 |

## 批次3（20 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `\.local\bin` | uv Python包管理器 | - | 7 | known |  | 15 | Astral uv 包管理器安装目录(uv/uvw/uvx) |
| `rmes_client` | 红谷MES制造执行系统客户端 | - | 6 | known |  | 15 | 北京红谷软件, ddh/hmx/sqm 模块族 |
| `\lip正式客户端` | 公文办公系统客户端（企业内部） | - | 5 | known |  | 15 | gwbgsystem公文办公/liporganization组件族 |
| `cockpit tools` | CLIProxyAPI管理组件（AI代理工具） | https://cliproxyapi.com | 7 | known | AI | 14 | CLIProxyAPI(Claude/Gemini/Codex CLI转API代理)Windows管理端 |
| `\潼湖bis` | 潼湖BIS业务信息系统客户端（企业内部） | - | 5 | known |  | 13 | 潼湖企业内部业务系统(bis.exe/bisadmin) |
| `\tensor\` | Saby（СБИС）企业管理平台 | - | 7 | known |  | 9 | 俄罗斯Tensor公司СБИС/Saby平台组件(sabyadmin/amprobe) |
| `agile dgs` | 敏捷科技DGS文档安全组件 | - | 6 | known |  | 9 | 江苏敏捷科技文档加密/防泄密驱动(dgskrn/netfilter) |
| `\.local\share\uv` | uv Python包管理器 | - | 7 | known |  | 8 | uv 包管理器数据/缓存目录 |
| `\wms\wms5.0-rh` | 京东WMS仓储管理系统 | - | 7 | known |  | 8 | 京东物流WMS 部署目录 |
| `\格瑞普电池` | 格瑞普电池生产管理系统 | - | 5 | known |  | 8 | 深圳格瑞普电池生产工序/条码管理(叠片/辅料/封装) |
| `\上位机\` | 工业设备上位机调试工具 | - | 5 | known |  | 8 | MCU/电表设备调试上位机(合肥派能等) |
| `fn:jd.wms3` | 京东WMS仓储管理系统 | - | 7 | known |  | 7 | 京东物流WMS v3 客户端模块(jd.wms3.main.*) |
| `\wms5.4.12` | 京东WMS仓储管理系统 | - | 7 | known |  | 7 | 京东物流WMS 增量更新目录 |
| `\metaquotes` | MetaTrader行情交易软件 | - | 7 | known |  | 7 | MetaQuotes MetaTrader 数据目录 |
| `\bis v2` | 潼湖BIS业务信息系统客户端（企业内部） | - | 5 | known |  | 7 | 同族BIS客户端(sfc/querystats模块) |
| `kimidata` | Kimi桌面版组件 | - | 7 | known | AI | 7 | Kimi桌面版数据目录(月之暗面) |
| `potupdate` | PotPlayer播放器（Kakao） | - | 8 | known |  | 6 | PotPlayer 安装/更新组件, Kakao签名 |
| `\.conda` | Python开发环境（Anaconda） | - | 6 | known |  | 6 | Anaconda conda 环境目录 |
| `fn:uvw` | uv Python包管理器 | - | 7 | known |  | 3 | Astral uv for Windows 可执行文件 |
| `fn:uvx` | uv Python包管理器 | - | 7 | known |  | 3 | Astral uvx 工具运行器 |

## 批次4（22 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `\css` | 企业内部管理系统客户端（CSS） | - | 5 | known |  | 37 | css/ppms内部管理系统(uicommon/planlib) |
| `soft\mes` | MES制造执行系统客户端 | - | 6 | known |  | 24 | soft/mes 目录下的 MES 客户端组件(customizeddesktop.resources, 与v3_mes同类) |
| `\nvidia corporation` | NVIDIA App | https://www.nvidia.cn/ | 8 | known |  | 23 | NVIDIA GPU管理与驱动组件(oawrapper) |
| `codebuddy` | 腾讯CodeBuddy | https://www.codebuddy.ai/ | 9 | known | AI | 23 | 腾讯AI编程助手(VSCode fork) |
| `ourplayer` | OurPlay加速器（上海卓安） | https://www.ourplay.net/ | 5 | known |  | 23 | 海外网络加速器, 上海卓安信息科技(检索确认) |
| `teleagent` | TeleAgent（AI代理组件） | - | 6 | known | AI | 23 | 开源Telegram AI代理(Python)或同名内部组件 |
| `mingw32` | MinGW开发工具链 | - | 6 | known |  | 22 | MinGW/w64devkit 编译工具链 |
| `sptlms2021` | 洞察眼终端管控客户端（SPTL） | - | 5 | known |  | 21 | 洞察眼MS/MIT系统(北京腾正天, 企业终端监控DLP, 检索确认) |
| `casd4` | CASD结构设计CAD插件 | - | 6 | known |  | 21 | AutoCAD ARX结构设计插件(梁柱板基础, 检索确认) |
| `microsoft\onedrive` | Microsoft OneDrive | - | 9 | known |  | 20 | OneDrive 同步客户端(local/onedrive, onedrivesetup/filecoauth) |
| `xivlaunchercn` | 游戏（最终幻想14启动器） | - |  | game |  | 18 | XIVLauncherCN 国服启动器 |
| `gwsxj123` | 思享排版助手（Word排版插件） | - | 7 | known |  | 15 | 文档排版Word插件(sixiangpaiban, jiang he签名) |
| `sippr` | 设计院EEP企业平台客户端（SIPPR） | - | 6 | known |  | 14 | 市政设计院企业应用平台(eep框架, 推断) |
| `mcbedrock` | 游戏（MC基岩版启动器） | - |  | game |  | 13 | feverapps MC基岩版启动组件 |
| `typeless` | Typeless AI语音输入 | https://typeless.co/ | 7 | known | AI | 12 | AI语音转文字输入应用(Electron) |
| `dalamud` | 游戏（FF14 Dalamud插件） | - |  | game |  | 11 | 最终幻想14 Dalamud 插件框架组件 |
| `\codeg\` | CodeG AI代码分析组件 | - | 7 | known | AI | 10 | Anomaly Innovations CodeG(签名吻合); 不含智谱codegeex |
| `wxwork` | 企业微信（WeCom）组件 | https://work.weixin.qq.com/ | 8 | known |  | 9 | 腾讯企业微信本地组件(wxworklocal) |
| `clash verge` | Clash Verge | https://clash-verge-rev.github.io/ | 6 | known |  | 7 | Clash Verge 代理客户端(mihomo内核) |
| `\nvm` | 开发环境（nvm/node） | - | 6 | known |  | 7 | nvm-windows Node版本管理 |
| `7-zip` | 7-Zip | https://www.7-zip.org/ | 8 | known |  | 6 | 开源压缩工具 |
| `omsenhance` | 疑似企业内部OMS组件 | - | 5 | known |  | 6 | T.E.C Solutions(G.Z.)签名, pdb内部构建 |

## 批次5（15 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `\mes正式区客户端` | MES正式区客户端（生产环境） | - | 6 | known |  | 17 | mes正式区客户端目录(生产环境部署); 沿用MES客户端6分定性 |
| `\mes\` | MES制造执行系统客户端 | - | 6 | known |  | 13 | \mes\ 纯目录(小程序代码等子组件); 与LW/olprintdll同族定性 |
| `\epic games` | Epic Games启动器/在线服务 | - | 9 | known |  | 12 | Epic Games Launcher + Epic Online Services + UE5(epic games\ue_5.8) |
| `fn:lwmesclient` | MES制造执行系统客户端（LW） | - | 6 | known |  | 11 | lwmesclient.exe + mes/小程序代码, 厂商未明 |
| `\mes安装程序` | 疑似艾普工华EWIN MES组件 | - | 6 | known |  | 10 | mes安装程序目录(ewin.aviservice/gregn6lib); 检索命中艾普工华(武汉)EWIN MES但aviservice关联被hedge |
| `\ris` | InteRIS放射信息系统(RIS)客户端 | - | 6 | known |  | 7 | InteRIS 放射科RIS客户端(检索确认: 组件页+微软安全通报列其DLL; 含icnris/cnris同族) |
| `fn:epicwebhelper` | Epic在线服务SDK（游戏内组件） | - | 8 | known |  | 5 | Steam游戏目录内 Epic Online Services 运行时组件 |
| `local\codeg` | CodeG AI代码分析组件 | - | 7 | known | AI | 5 | appdata/local/codeg(codeg-mcp, Anomaly Innovations); 补批次4根目录盲区, 不含codegeex |
| `qwms_pro` | QWMS仓库管理系统客户端 | - | 5 | known |  | 4 | qwms.winform.exe(WinForm WMS客户端, 文件名自证; 三次检索降级) |
| `fn:olprintdll.dll` | MES客户端组件 | - | 6 | known |  | 3 | mes根目录组件(olprintdll/pcbpack/tindll, 工厂MES推断) |
| `\plantu mes` | MES客户端(plantu部署) | - | 6 | known |  | 3 | plantu mes/mesclient 目录; 沿用MES客户端6分定性, 厂商未明 |
| `temp\codeg` | CodeG AI代码分析组件 | - | 7 | known | AI | 2 | temp/codeg-*-updater 更新包; 补批次4根目录盲区, 不含codegeex |
| `codegeex-intellij` | 智谱CodeGeeX JetBrains插件 | https://codegeex.cn | 7 | known | AI | 2 | codegeex-intellij-extension(文件名自证); 不含.codegeex\mamba(维持未知) |
| `\mes_v3` | MES系统客户端(V3) | - | 6 | known |  | 2 | mes_v3 目录变体; 沿用MES客户端6分定性 |
| `fn:pcbpack.dll` | MES客户端组件 | - | 6 | known |  | 2 | pcbpack.dll(与olprintdll/tindll同族, mes根目录); 沿用MES客户端组件定性 |

## 遗留身份（2 条）

| 路径特征 | 溯源结果 | 网站 | 分数 | 类别 | AI | 样本行数 | 说明 |
|---|---|---|---|---|---|---|---|
| `\bionic` | LM Studio | https://lmstudio.ai/ | 8 | known | AI | 6 | 本地大模型运行环境(Element Labs) |
| `alphaai` | AlphaAI法律智能平台 | - | 8 | known | AI | 2 | 北京新橙科技法律行业SaaS |

---

统计：known=69 / game=6 / pua=2；AI 标注=13；带网址=16
