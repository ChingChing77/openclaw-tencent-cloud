# TOOLS.md - 工作笔记

## 通信渠道

| 渠道 | 工具 |
|---|---|
| 飞书 | feishu_doc, feishu_bitable, feishu_wiki, feishu_drive, feishu_chat |
| QQ | QQBot（消息、语音、图片） |

## 已安装 Skills（按类别）

### 核心能力
- **openclaw** — OpenClaw 运维（安装于 2026-03-19）
- **github** — GitHub issue/PR/操作
- **gmail** — 邮件读写
- **weather** — 天气预报

### 数据 & 金融
- **akshare-stock** — A股行情/选股
- **binance-pro** — 加密货币交易
- **us-stock-analysis** — 美股分析
- **trading-research** — 交易研究
- **stock-watcher** — 自选股监控
- **coinank-openapi** — CoinAnk 加密数据 API（Key 未配置）

### 建筑 & 工程
- **afrexai-construction-estimator** — 全面工程造价估算
- **open-construction-estimate** — 公开造价数据库（5.5万+单价）
- **pandas-construction-analysis** — BIM 数据分析
- **estimate-builder** — 工程估算生成器

### 创作 & 媒体
- **image-cog** — AI 图片生成
- **music-cog** — 音乐生成
- **video-frames** — 视频帧提取
- **remotion-video-toolkit** — 视频制作
- **pdf** — PDF 处理
- **excel-xlsx** — Excel 处理
- **word-docx** — Word 文档
- **powerpoint-pptx** — PPT 制作

### 任务 & 自动化
- **browser-automation** — 网页自动化
- **tmux** — 终端会话管理
- **news-aggregator** — 每日新闻聚合
- **ai-self-evolution** — 自我学习改进
- **proactive-agent** — 主动 Agent
- **memory-system-v2** — 记忆系统

## 重要路径

```
~/.openclaw/workspace/
├── skills/                   # 技能包 (~90个)
├── memory/                   # 每日日志
├── cron/                     # 定时脚本
│   └── daily_stock_report.sh
├── scripts/                  # 工具脚本
├── docs/                     # 归档文档
└── .openclaw/               # 配置（不提交 git）
```

## API Key 状态

| Key | 状态 | 位置 |
|---|---|---|
| GEMINI_API_KEY | ✅ 已配置 | ~/.openclaw/.env |
| MINIMAX_API_KEY | ❌ 未配置 | — |
| COINANK_API_KEY | ❌ 未配置 | — |

## 待补充

- [ ] SSH 主机配置
- [ ] 摄像头使用偏好
- [ ] TTS 语音偏好

---

_随着使用持续更新_
