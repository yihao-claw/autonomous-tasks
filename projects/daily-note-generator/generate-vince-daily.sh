#!/bin/bash
# generate-vince-daily.sh
# Auto-generates Vince's Daily Note each day
# Called by cron at JST 00:05

set -e

DATE=$(TZ=Asia/Tokyo date +%Y-%m-%d)
OUTPUT_FILE="/home/node/obsidian-vault/Agents/Vince/Daily/${DATE}.md"

# Skip if already has content beyond just backup entry
if [ -f "$OUTPUT_FILE" ] && [ $(wc -l < "$OUTPUT_FILE") -gt 10 ]; then
  echo "Daily note for $DATE already has content, skipping template injection."
  exit 0
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

cat > "$OUTPUT_FILE" << EOF
---
date: ${DATE}
tags:
  - daily
  - agent/horse
agent: Vince
---
# ${DATE} Vince Daily

## ✅ Tasks Completed
_（由每次任務執行後自動補充）_

## ⏭️ Skipped / Blocked
_（無）_

## 💡 Insights
_（由任務執行後補充）_

## 🔜 Next Session
_（由 autonomous-daily-tasks 填充）_

---
_Template auto-generated at $(date -u +%Y-%m-%dT%H:%M:%SZ) UTC_
EOF

echo "Created: $OUTPUT_FILE"
