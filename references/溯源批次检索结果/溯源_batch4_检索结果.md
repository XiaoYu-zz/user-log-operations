# 溯源批次4 检索结果（2026-09-11，主库+e2e 全数据）

来源：双数据集 kw_candidates + q16 离线证据 + 9 次联网检索。

## 离线高置信（13 个产品）

| 簇 | 数据集 | 行数 | 证据 | 提议 | 网址 |
|---|---|---|---|---|---|
| nvidia corporation | e2e | 23 | NVIDIA 签名 + nvidia app/oawrapper | NVIDIA App 8分 | nvidia.cn ✅ |
| codebuddy cn | e2e | 23 | vscode-*.node（VSCode fork）= 腾讯AI编程助手 | 腾讯CodeBuddy 9分AI | codebuddy.ai ✅ |
| ourplayer | e2e | 23 | 签名「上海卓安信息科技有限公司」9行 + aivmlib | OurPlay加速器（上海卓安）5分 | ourplay.net ✅ |
| mingw32 | e2e | 22 | \tools\mingw32 + w64devkit（Christopher Wellons 签名） | MinGW开发工具链 6分 | - |
| onedrive | e2e | 20 | onedrivesetup/filecoauth/filesync | Microsoft OneDrive 9分 | 留空（microsoft.com 不通） |
| sptlms2021 | e2e | 21 | sptlclient/spmsmain/stmsmain（7行 microsoft windows 疑似占位签名） | 洞察眼终端管控客户端（SPTL）5分 | sptlms.com（检索确认产品线） |
| casd4 | e2e | 21 | casddb/baselinediagram/folddrawing.arx（AutoCAD ARX） | CASD结构设计CAD插件 6分 | - |
| xivlaunchercn+dalamud | e2e | 29 | dalamud.injector/boot（FF14 插件框架） | 游戏（最终幻想14启动器/Dalamud） | - |
| feverapps\mcbedrock | e2e | 13 | MC 基岩版启动器目录 + cefwebview | 游戏（MC基岩版启动器） | - |
| wxwork | 主 | 9 | wxworklocal_3.4.0 + 腾讯签名 + crashpad | 企业微信（WeCom）组件 8分 | work.weixin.qq.com ✅ |
| clash verge | 主 | 7 | clash-verge.exe + verge-mihomo | Clash Verge 6分 | clash-verge-rev.github.io ✅ |
| author software\nvm | 主 | 7 | nvm.exe/node.exe | 开发环境（nvm/node）6分 | - |
| 7-zip | 主 | 6 | 7zg.exe/7-zip.dll | 7-Zip 8分 | 7-zip.org ✅ |

## 检索确认/中置信（8 个产品）

| 簇 | 数据集 | 行数 | 结论 | 提议 |
|---|---|---|---|---|
| teleagent | 主+e2e | 23 | GitHub 开源 TeleAgent（Telegram AI 代理, Python, 与 cp312 pyd 吻合） | TeleAgent（AI代理组件）6分AI（中置信） |
| 思享排版助手 | 主 | 15 | sixiangpaiban.* 文件名自证产品名，'jiang he' 个人签名 | 思享排版助手（Word排版插件）7分（中置信） |
| typeless | e2e | 12 | Typeless AI 语音输入应用（Electron 结构吻合） | Typeless AI语音输入 7分AI（中置信）typeless.co ✅ |
| codeg | 主 | ~10 | CodeG = Anomaly Innovations AI代码分析平台（签名直接吻合）；⚠️ '.codegeex'（智谱）是另一产品，特征用 \codeg\ 防误伤 | CodeG AI代码分析组件 7分AI（codeg.anoma.ly 不通留空） |
| sippr | e2e | 14 | SIPPR 疑似上海市政工程设计研究总院（有歧义），eep.* 企业应用平台框架 | 设计院EEP企业平台客户端 6分（中置信） |
| css | e2e | 37 | \css\ppms + uicommon/planlib，检索无果 | 企业内部管理系统客户端（CSS）5分（中置信） |
| omsenhance | 主 | 6 | 签名 T.E.C Solutions (G.Z.) Limited + pdb | 疑似企业内部OMS组件 5分（存疑） |

## 保持未知

- v01sec 48（三次检索零公开信息，观察项）、fn:exe 腾讯/无锡 18、pandafan 7（同名巧合）、qwms_pro 4、deja.exe 1、codeg 之外的 windowsapps 零散行。
- 注意：codeg 簇内 @up\.codegeex\mamba 2 行属智谱 CodeGeeX，未定性（保持未知，避免误判）。
