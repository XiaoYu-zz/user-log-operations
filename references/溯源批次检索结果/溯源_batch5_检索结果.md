# 溯源批次5 检索结果（2026-09-11，主库+e2e 全数据）

来源：kw_candidates + 离线预检 + 7 次联网检索（QWMS 三次降级、天津跃普结果伪造）+ 4 个网址实测。

## 高置信（5 条入库）

| 簇 | 数据集 | 行数 | 证据 | 提议 | 网址 |
|---|---|---|---|---|---|
| \ris（interris/icnris） | 主 | 7 | 检索确认 InteRIS=放射信息系统（组件页 + 微软安全通报列 inteRIS.*.dll）；`\ris` 精确命中零误伤（prismlauncher 为 'ris' 子串噪声已排除） | InteRIS放射信息系统(RIS)客户端 6分 | -（无官网可达） |
| \epic games | e2e | 12 | program files (x86)\epic games\epic online services + ue_5.8（UE5） | Epic Games启动器/在线服务 9分 | -（epicgames.com 403） |
| fn:epicwebhelper | e2e | 5 | Steam 游戏目录内 Epic Online Services 运行时 | Epic在线服务SDK（游戏内组件）8分 | - |
| local\codeg + temp\codeg | 主+e2e | 8+3 | 延续批次4 Anomaly Innovations 定性；⚠️ '\codeg' 裸特征会误伤 '\codegeex-intellij'，必须带前缀 | CodeG AI代码分析组件 7分AI | - |
| （CodeGeeX） | e2e | 1 | codegeex-intellij-extension 文件名自证 | 智谱CodeGeeX JetBrains插件 7分AI | codegeex.cn ✅200 |

## 中置信（6 条入库）

| 簇 | 数据集 | 行数 | 结论 | 提议 |
|---|---|---|---|---|
| qwms_pro | 主 | 4 | qwms.winform.exe 文件名自证 WMS；三次检索全部降级 | QWMS仓库管理系统客户端 5分 |
| fn:lwmesclient + \mes\ | e2e | 11+13 | lwmesclient.exe + mes\小程序代码，厂商未明 | MES制造执行系统客户端（LW）6分 |
| fn:olprintdll.dll / fn:pcbpack.dll | 主 | 3+2 | mes 根目录组件（pcbpack/tindll 工厂推断） | MES客户端组件 6分 |
| \mes正式区客户端 | 主+e2e | 17 | 生产环境 MES 客户端目录 | MES正式区客户端（生产环境）6分 |
| \mes_v3 + \plantu mes | 双 | 2+3 | MES 客户端部署变体目录 | MES客户端 6分 |
| \mes安装程序 | e2e | 10 | ewin.aviservice/gregn6lib；检索命中艾普工华(武汉) EWIN MES 但 aviservice 关联被检索方 hedge | 疑似艾普工华EWIN MES组件 6分 |

## 保持未知

- **zero 14 行（天津跃普科技签名）**：检索返回结果自带「模拟数据」声明且 tjyuepu.com DNS 不解析——伪造证据链，用户确认保持未知（观察项）。
- .codegeex\mamba 2 行维持未知（批次4 口径不变）。

## 特征补全（MES 族，5 条，均沿用已确认 6 分定性）

`\mes\`（⚠️'\mes' 裸特征误伤 feishu messages 139 行，不可用）、`\mes正式区客户端`、`\mes_v3`、`\plantu mes`、`fn:pcbpack.dll`。

## 结果

path_kb 62→**77 条**。主库 unknown 1697→**1671**（known 4985, HEAD_URL 36, AI 6）；e2e 1561→**1529**（known 3352, HEAD_URL 30, AI 7）。

## 批次6 backlog

- 主库：v01sec 48（死）、fn:exe 18（死）、pandafan 7（死）、bin 6、xrunpro-秀英院区 6
- e2e：zero 11（用户已定）、像素蛋糕 10、dlp 10、tc_notice_setup 10、fn:exe 16（死）
