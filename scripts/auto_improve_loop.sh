#!/bin/bash
# auto_improve_loop.sh — 每10分钟运行一次审阅-改进循环
# 由 launchd 或 cron 调用
# 日志写入 outputs/writing/auto_improve.log

set -euo pipefail

PROJECT_DIR="/Users/siyaozheng/Documents/经济增长因素研究"
LOG_FILE="$PROJECT_DIR/outputs/writing/auto_improve.log"
LOCK_FILE="$PROJECT_DIR/outputs/writing/.auto_improve.lock"
PYTHON="/opt/homebrew/bin/python3"
MAX_RUNTIME_SECONDS=540  # 9分钟，留1分钟缓冲

# 防止并发运行
if [ -f "$LOCK_FILE" ]; then
    LOCK_AGE=$(($(date +%s) - $(stat -f %m "$LOCK_FILE" 2>/dev/null || echo 0)))
    if [ "$LOCK_AGE" -lt "$MAX_RUNTIME_SECONDS" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SKIP: 上一轮仍在运行 (lock age=${LOCK_AGE}s)" >> "$LOG_FILE"
        exit 0
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] STALE LOCK: 清除过期锁 (age=${LOCK_AGE}s)" >> "$LOG_FILE"
fi

touch "$LOCK_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "======== 审阅-改进循环 开始 ========"

cd "$PROJECT_DIR"

# Step 1: 运行 orchestrator --paper --improve
log "Step 1: 运行 orchestrator --paper --improve"
if $PYTHON scripts/orchestrator.py --paper --improve >> "$LOG_FILE" 2>&1; then
    log "Step 1: ✓ 完成"
else
    log "Step 1: ✗ 失败 (exit code: $?)"
    rm -f "$LOCK_FILE"
    exit 0  # 不中断后续循环
fi

# Step 2: 检查剩余 TODO
TODO_FILE="$PROJECT_DIR/outputs/writing/improvement_todos.json"
if [ -f "$TODO_FILE" ]; then
    if $PYTHON -c "
import json, sys
with open('$TODO_FILE') as f:
    data = json.load(f)
todos = data.get('todos', data)
pending = [t for t in todos if isinstance(t, dict) and t.get('status') == 'pending']
manual = [t for t in pending if not t.get('auto_fixable')]
auto = [t for t in pending if t.get('auto_fixable')]
print(f'pending={len(pending)} manual={len(manual)} auto={len(auto)}')
" >> "$LOG_FILE" 2>&1; then
        log "Step 2: TODO 统计已记录"
    fi
fi

log "======== 审阅-改进循环 结束 ========"
rm -f "$LOCK_FILE"
