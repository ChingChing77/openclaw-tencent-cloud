#!/bin/bash
# 每日动量报告生成脚本 - 完整版
# 执行时间: 每个交易日晚间 (北京时间 20:45，美股开盘前)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$SCRIPT_DIR/cron.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始生成每日动量报告 =========="

# 读取 prompt
PROMPT=$(cat "$SCRIPT_DIR/prompt.md")

# 构建完整的分析任务
ANALYSIS_TASK="$PROMPT

---

请立即生成今日的《每日动量报告》。在生成报告前，你必须：
1. 搜索当前 VIX 指数和股指期货走势
2. 搜索今日市场热点和催化剂
3. 筛选符合 5% 观察名单标准的股票
4. 输出完整的报告

开始吧。"

# 使用 openclaw 命令执行分析
# 注意: 这里需要确保有正确的认证和环境

# 将任务写入临时文件供 agent 使用
echo "$ANALYSIS_TASK" > "$WORKSPACE/daily-momentum-agent/task.md"

log "任务已准备，调用 Agent 执行分析..."

# 通过 socket/pipe 或其他方式触发 agent
# 这里使用消息文件方式，等待下次 heartbeat 或手动触发

log "分析任务已生成，保存在 task.md"
log "请在 Agent 会话中执行分析或等待定时触发"
log "========== 任务完成 =========="
