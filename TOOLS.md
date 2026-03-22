# TOOLS.md - 工作笔记

## 通信渠道

| 渠道 | 工具 |
|---|---|
| 飞书 | feishu_doc, feishu_bitable, feishu_wiki, feishu_drive, feishu_chat |
| QQ | QQBot（消息、语音、图片） |

## 已安装 Skills（按类别）

### 核心能力
- **openclaw** — OpenClaw 运维
- **clawteam** — 多 Agent 协作编排（已激活）
- **github** — GitHub issue/PR/操作
- **gmail** — 邮件读写
- **weather** — 天气预报

### 数据 & 金融
- **akshare-stock** — A股行情/选股
- **us-stock-analysis** — 美股分析
- **binance-pro** — 加密货币交易
- **stock-watcher** — 自选股监控
- **trading-research** — 交易研究
- **daily-momentum-report** — 每日动量报告
- **a-stock-monitor** — A股量化监控
- **crypto-gold-monitor** — 加密货币 & 贵金属
- **coinank-openapi** — CoinAnk 加密数据（⚠️ 未配置 Key）

### 建筑 & 工程
- **afrexai-construction-estimator** — 全面工程造价估算
- **open-construction-estimate** — 公开造价数据库（5.5万+单价）
- **pandas-construction-analysis** — BIM 数据分析
- **estimate-builder** — 工程估算生成器
- **cost-prediction** — 工程成本 ML 预测

### 创作 & 媒体
- **image-cog** — AI 图片生成
- **music-cog** — 音乐生成
- **video-frames** — 视频帧提取
- **remotion-video-toolkit** — 视频制作
- **pdf** — PDF 处理
- **excel-xlsx** — Excel 处理
- **word-docx** — Word 文档
- **powerpoint-pptx** — PPT 制作
- **elevenlabs-music** — ElevenLabs 音乐生成

### 记忆系统
- **memory-lancedb-pro** — 生产级长期记忆（已激活 ✅）
- **memory-system-v2** — 快速语义记忆
- **memory-manager** — 三级记忆管理

### 任务 & 自动化
- **browser-automation** — 网页自动化
- **tmux** — 终端会话管理
- **news-aggregator** — 每日新闻聚合
- **ai-self-evolution** — 自我学习改进
- **proactive-agent** — 主动 Agent
- **skill-creator** — 技能创作
- **skill-vetter** — 技能安全审查

### 其他（按需使用）
- **obsidian** — Obsidian 笔记
- **notion** — Notion API
- **openai-whisper** — 本地语音转文字
- **canvas** — 画布展示
- **agent-browser** — Rust 无头浏览器
- **summarize** — URL/文件摘要

## API Key 状态

| Key | 状态 | 位置 |
|---|---|---|
| GEMINI_API_KEY | ✅ 已配置 | ~/.openclaw/.env |
| MINIMAX_API_KEY | ✅ 已配置 | ~/.openclaw/.env |
| JINA_API_KEY | ✅ 已配置 | ~/.openclaw/.env |
| COINANK_API_KEY | ❌ 未配置 | — |
| FINNHUB_API_KEY | ✅ 已配置 | openclaw.json env |
| TUSHARE_TOKEN | ✅ 已配置 | openclaw.json env |
| ALPHA_VANTAGE_API_KEY | ✅ 已配置 | openclaw.json env |

## 定时任务

- `cron/daily_stock_report.sh` — 每日股票动量报告推送

## 待补充

- [ ] SSH 主机配置
- [ ] 摄像头使用偏好
- [ ] TTS 语音偏好

---
_最后更新：2026-03-21_
