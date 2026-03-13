#!/bin/bash
# Auto-backup script for daily memory
# Runs every 2 hours to ensure conversation is logged

set -e

WORKSPACE="/home/node/.openclaw/workspace"
CURRENT_DATE=$(date +%Y-%m-%d)
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$MEMORY_DIR/${CURRENT_DATE}.md"

# Create memory directory if not exists
mkdir -p "$MEMORY_DIR"

# Get last modified time
if [ -f "$MEMORY_FILE" ]; then
    LAST_MODIFIED=$(stat -c %Y "$MEMORY_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    HOURS_SINCE=$((($NOW - $LAST_MODIFIED) / 3600))
    
    if [ $HOURS_SINCE -lt 2 ]; then
        echo "✓ Backup is recent (${HOURS_SINCE}h ago), skipping"
        exit 0
    fi
    
    echo "⚠️ Backup overdue: ${HOURS_SINCE}h since last update"
else
    echo "⚠️ No backup file for today, creating..."
fi

# Trigger OpenClaw to update the backup
# Use the gateway API to send a message to the main agent
GATEWAY_URL="http://127.0.0.1:18789"

# Send backup reminder via internal message
curl -s -X POST "$GATEWAY_URL/api/v1/sessions/agent:main:main/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "🔴 自動備份提醒：請立即更新 memory/'"$CURRENT_DATE"'.md，記錄最近的重要對話和完成的工作。如果沒有新內容，回覆 HEARTBEAT_OK。",
    "internal": true
  }' 2>&1 | grep -q "success" && echo "✓ Backup reminder sent" || echo "❌ Failed to send reminder"

# Log the check
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup check completed" >> "$MEMORY_DIR/backup-log.txt"
