#!/bin/bash
# 定时备份脚本 - 每天晚上10点自动运行
# Token 通过环境变量 GITHUB_TOKEN 传入，避免硬编码
set -e

WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

cd "$WORKSPACE"

# 配置 Git
git config user.name "OpenClaw Backup" 2>/dev/null || true
git config user.email "openclaw@backup.local" 2>/dev/null || true

# 暂存所有更改
git add -A

# 检查是否有更改
if git diff --cached --quiet; then
    echo "[$TIMESTAMP] 无更改，跳过提交"
    exit 0
fi

# 提交
git commit -m "Auto backup $TIMESTAMP"

# 推送（Token从环境变量读取，不写在脚本里）
if [ -n "$GITHUB_TOKEN" ]; then
    git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/ChingChing77/openclaw-tencent-cloud.git"
fi
git push origin main

echo "[$TIMESTAMP] 备份成功 ✓"
