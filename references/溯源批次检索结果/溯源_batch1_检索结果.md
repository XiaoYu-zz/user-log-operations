# 溯源批次1 检索结果（20260805~20260811 数据，2026-09-11）

候选来源：outputs/test_e2e/kw_candidates.json（厂商/产品复合词版，961 词），按样本行数降序取前 30 过目，本批检索前 10。

## ✅ 全确认（4 条）

| 关键词 | 行数 | 结论 | 证据 | 建议 |
|---|---|---|---|---|
| hearthstone | 122 | 炉石传说（暴雪卡牌游戏） | 路径 hearthstone\hearthstone_data；blizzard.bgsclient.dll；官网确认 | 归游戏类；网址 https://hs.blizzard.cn（已核 200） |
| ylgame | 47 | ylgame 对战平台（杭州战英网络） | 签名"杭州战英网络科技有限公司"；cefwebcore.dll 等客户端结构；下载站/企业信息确认 | 归游戏类；无独立官网，网址留空 |
| tencent/xwechat | 23 | 微信 4.0（腾讯） | tencent\xwechat 目录为微信 4.0 新版目录命名（com.tencent.xinWeChat） | known 9 分；网址 https://weixin.qq.com（已核 200） |
| 铁四院 | 39 | 铁四院智能勘察设计平台（中铁第四勘察设计院自研） | 路径 铁四院\智能勘察设计平台；.arx/.dll 勘察设计模块 | known 7 分；官网 crfsdi.com 本机不可达（403/证书），网址留空 |

## 🟡 部分确认（2 条）

| 关键词 | 行数 | 结论 | 证据 | 建议 |
|---|---|---|---|---|
| soft/mes | 24 | MES 制造执行系统客户端（具体厂商未查到） | plantumesclient.exe、tmesis.*.dll；MES 定义确认，plantumes/tmesis 无公开结果 | known 6 分，名称"MES制造执行系统客户端"，网址留空 |
| 元游棋牌大厅 | 24 | 元游棋牌大厅（上海元游网络，棋牌游戏） | 签名"上海元游网络科技有限公司"+自述名+autoupdate/crashreportx 结构；搜索两次遇限速未完成 | 归游戏类；下批补检索后定稿或按离线证据先入 |

## ⏸ 待定（保持未知）

| 关键词 | 行数 | 情况 |
|---|---|---|
| devicetesttools | 35 | 无公开信息；selenium/pytest 的 Python 脚本，疑似内部测试工具 |
| fn:yuanbaoupdateservice.exe | 23 | 疑似腾讯元宝更新服务，无直接证据；下批先本地核对路径再定 |

## ⚠️ 过目项（可疑/需拆分）

- **tools**（21 行）混合组：clashverge（代理工具）＋ mingw32（编译器）＋ llama.cpp（AI 推理）——需按更深路径段拆分后分别研判
- **msconfig**（14 行）：目录名伪装 Windows 系统工具，签名却为南京中科华赛 / syncfuture——疑似伪装，建议低分+备注
- **fn:exe**（16 行）：文件名即为 "exe" 的噪声行（anydesk、nous research 等混杂）

## 下批排队

teamviewer(23)、nvidia corporation/nvidia app(22)、casd4(21)、onedrive(20)、.local/teleagent(19)、codebuddy cn(18)、xivlaunchercn(18)、css(16)、ourplayer(23)、protect/wsus(24)、sippr(14)、sptlms2021(14)、.conda(13)、feverapps/mcbedrock(13)、lip正式客户端(13)、typeless(12)、qpct(12)、epic games(12)、zero(11)

## 来源

- 炉石传说官网: https://hs.blizzard.cn
- ylgame 平台: [多特手游](https://www.duote.com/soft/471988.html)、[绿色资源网](http://m.downcc.com/soft/287549.html)、[顺企网-杭州战英网络](https://www.11467.com/qiye/70269235.htm)、[百度百科-杭州战英网络](https://baike.baidu.com/item/杭州战英网络科技有限公司/22491920)
- 铁四院: 中铁第四勘察设计院 www.crfsdi.com（本机不可达）
- 微信 4.0 xwechat 目录: 公开技术资料（xwechat_files 为微信 4.0 新数据目录）
