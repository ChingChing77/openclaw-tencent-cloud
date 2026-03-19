# MEMORY.md - 长期记忆

_这是黑莓的长期记忆库。只记录重要的、持久的facts/决策/教训。_

---

## 关于大力

- 使用 OpenClaw AI助手（名字：黑莓 🫐）
- 飞书和 QQ 是主要沟通渠道
- 喜欢惊喜
- 时区：Asia/Shanghai

## 系统配置

- **OpenClaw 版本：** 2026.3.13
- **模型：** minimax/MiniMax-M2.5-highspeed（主）| gemini/gemini-2.5-flash（备）
- **工作区 GitHub：** ChingChing77/openclaw-tencent-cloud
- **技能包：** ~90 个 skills 安装在 `~/.openclaw/workspace/skills/`
- **Gemini API Key：** ✅ 已配置
- **MiniMax API Key：** ✅ 已配置
- **CoinAnk API Key：** ❌ 未配置

## 重要决策记录

- 2026-03-19：workspace 备份到 GitHub，清理冗余文件，建立 memory 系统
- 2026-03-19：安装 OpenClaw 运维技能包（`skills/openclaw/`）
- 2026-03-19：pip 安装 anthropic 0.86.0 库
- 2026-03-19：固化黑莓风格（SOUL.md + IDENTITY.md）
- 2026-03-19：配置 Gemini API Key，设置模型备用
- 2026-03-19：升级 OpenClaw 2026.3.2 → 2026.3.13（安全修复+新功能）
- 2026-03-19：安装 coinank-openapi 技能包

## 工作区目录结构

```
~/.openclaw/workspace/
├── skills/           # 技能包
├── memory/           # 每日日志
├── MEMORY.md         # 长期记忆
├── cron/             # 定时脚本
├── scripts/          # 工具脚本
├── docs/             # 归档文档（.docx）
├── cost-system/      # 成本系统
├── plugins/          # 插件
└── [SOUL|AGENTS|USER|HEARTBEAT|TOOLS].md  # 核心文件
```

## 待补充

- [ ] 大力的偏好、习惯、项目动态
- [ ] 重要项目里程碑
- [ ] CoinAnk API Key 配置状态

---
_最后更新：2026-03-19_
