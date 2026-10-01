# 溯源批次3 检索结果（2026-09-11，主库）

来源：kw_candidates.json（Brave 补判后）+ q14/q15 离线证据 + 8 次联网检索（多次降级重试）。

## 离线高置信（无需检索，证据充分）

| 簇 | 行数 | 证据 | 提议 | 网址 |
|---|---|---|---|---|
| .local\bin + .local\share\uv + fn uvw/uvx | ~30 | uv.exe/uvw.exe/uvx.exe（Astral uv 包管理器标准安装布局） | uv Python包管理器 7分 | - |
| jd.wms3（fn）+ \wms\wms5.0-rh + \wms5.4.12 | 22 | jd.wms3.main.* 文件名（京东物流WMS v3 命名） | 京东WMS仓储管理系统 7分 | - |
| rmes_client | 15 | 签名「北京红谷软件技术有限公司」5行 + ddh.*/hmx.winforms/sqm 模块 | 红谷MES制造执行系统客户端 6分 | - |
| c:\program files\tensor（含 x86） | 9 | 签名「tensor company ltd」7行 + sabyadmin/diagnostic-tool/amprobe（СБИС/Saby 工具族） | Saby（СБИС）企业管理平台 7分 | - |
| agile dgs | 9 | 签名「jiangsu agile technology co., ltd.」9/9 + dgskrn/dgskrn64/netfilter 驱动族 + everything 捆绑 | 敏捷科技DGS文档安全组件 6分 | - |
| \格瑞普电池 | 8 | gerui.exe + zidongfengzhuang(自动封装)/diepian(叠片)/fuliao(辅料) 电池制造工序 dll | 格瑞普电池生产管理系统 5分 | - |
| \上位机\ | 8 | f330单路mcu上位机.exe + mydtsu666(电表型号)debugtool + tcp scanner 调试组件 | 工业设备上位机调试工具 5分 | - |
| \metaquotes | 7 | c:\programdata\metaquotes（MetaQuotes=MetaTrader 数据目录） | MetaTrader行情交易软件 7分 | 留空（本机不可达） |
| potupdate | 6 | potplayersetup64_154.exe + 签名「kakao corp.」 | PotPlayer播放器（Kakao）8分 | 留空（daum TLS 信任失败） |
| .conda | 6 | .conda\pkgs + py312 + python.exe（Anaconda 环境布局） | Python开发环境（Anaconda）6分 | - |
| microsoft.screensketch 7行 | 7 | program+files 路径 `+` 编码导致 flags 逃逸 | 不入库——已修 `+` 解码，自动归位 Microsoft Store 9分 | - |

## 联网检索确认

| 簇 | 行数 | 检索结论 | 提议 | 置信 |
|---|---|---|---|---|
| cockpit tools | 14 | cockpit-cliproxy = CLIProxyAPI（router-for-me，GitHub 2700+ star，Claude/Gemini/Codex CLI 转 API 代理）管理组件；样本为 Windows 端 "Cockpit Tools" v1.3.38 桌面版 | CLIProxyAPI管理组件（AI代理工具）7分 AI | 中高（名称唯一匹配，Windows 部署形态未直接见到）→ cliproxyapi.com 200 ✅ |
| pandafan | 7 | 检索命中 Panda Free Antivirus，但样本在 appdata\local 且带 ffmpeg/cronet/vulkan Electron 结构，与杀软部署形态矛盾 | 判定为同名巧合，**保持未知** | - |

## 检索无果（本地推断，中置信）

| 簇 | 行数 | 本地证据 | 提议 |
|---|---|---|---|
| \潼湖bis + \bis v2 | 20 | d:\潼湖bis/bis.exe/bisadmin/bisdataquery/bisfrhc 模块化业务系统；潼湖=惠州潼湖生态智慧区（检索确认地名，系统无公开资料） | 潼湖BIS业务信息系统客户端（企业内部）5分 |
| \lip正式客户端 | 15 | gwbgsystem(公文办公)/liporganization/resiwisdom dll 族，党政公文办公形态；resiwisdom 检索未确认到具体公司 | 公文办公系统客户端（企业内部）5分 |
| kimidata\daimon-share | 7 | Kimi桌面版数据目录 + curl-cffi/formulas/pwiz 等 Python 打包工具 | Kimi桌面版组件 7分 AI |

## 检索无果（保持未知）

- **v01sec 48 行**：三次检索（v01sec / axinstall.exe / axinstall+v01sec）零公开信息。axinstall.exe 本身是 Adobe/ActiveX 安装器常见名，但样本 48 行同 md5、位于 program files\v01sec、无签名——无法归因。观察项。
- **fn:exe 18 行**：签名 腾讯科技 + 无锡下载家园网络科技；"无锡下载家园" 检索无法确证与腾讯的关系。证据不足，保持未知。
- qwms_pro 4 行、\ris\interris 1 行、icnris_eis 1 行、pandafan 7 行、wmssoft/momgit 零散 3 行：保持未知。

## 顺带修复

- **`+` 传输编码解码前移（291 行）**：step17 build_recs 现在在规范化前解码 `+`→空格，与判定时 dec() 口径一致。program+files\windowsapps 下 39 行此前逃过 flags 识别（含 screensketch 7 行），修复后正确归入 Microsoft Store 分类。
