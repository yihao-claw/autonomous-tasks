#!/bin/bash
# generate-dan-daily.sh
# Auto-generates Dan's Daily Note each day at 00:05 UTC
# Called by cron, outputs to Obsidian vault

set -e

DATE=$(date -u +%Y-%m-%d)
YEAR=$(date -u +%Y)
MONTH=$(date -u +%m)
DAY=$(date -u +%d)
OUTPUT_FILE="/home/node/obsidian-vault/Agents/Dan/Daily/${DATE}.md"

# Skip if already exists
if [ -f "$OUTPUT_FILE" ]; then
  echo "Daily note for $DATE already exists, skipping."
  exit 0
fi

LINEAR_TOKEN=$(cat ~/.openclaw/secrets/linear-token)

# Get today's completed issues
DONE_ISSUES=$(curl -s -X POST https://api.linear.app/graphql \
  -H 'Content-Type: application/json' \
  -H "Authorization: $LINEAR_TOKEN" \
  -d "{\"query\":\"{ issues(filter: { state: { type: { eq: \\\"completed\\\" } }, updatedAt: { gte: \\\"${DATE}T00:00:00Z\\\" } }) { nodes { identifier title updatedAt } } }\"}" \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
nodes = data['data']['issues']['nodes']
if not nodes:
    print('| （今日無完成 issues） | — | — |')
else:
    for n in nodes:
        t = n['updatedAt'][11:16]
        print(f\"| {n['identifier']} | {n['title']} | {t} UTC |\")
")

cat > "$OUTPUT_FILE" << EOF
---
date: ${DATE}
tags: [daily, agent/dan]
agent: Dan
---

# ${DATE} Daily Note

## ✅ 今日完成的 Linear Issues

| Issue | 標題 | 完成時間 |
|-------|------|----------|
${DONE_ISSUES}

---

## 🤖 Agent 活動摘要

_（由各 agent 每日活動日誌彙整）_

### 🐴 Horse
$([ -f "/home/node/obsidian-vault/Agents/Horse/Daily/${DATE}.md" ] && echo "詳見 [[Agents/Horse/Daily/${DATE}]]" || echo "_今日無記錄_")

### 🐦 Bird
$([ -f "/home/node/obsidian-vault/Agents/Bird/Daily/${DATE}.md" ] && echo "詳見 [[Agents/Bird/Daily/${DATE}]]" || echo "_今日無記錄_")

---

## 🔜 待辦 / 未解決

_（由 Horse linear-todo-check 補充）_

---

_自動生成於 $(date -u +%Y-%m-%d\ %H:%M) UTC_
EOF

echo "Created: $OUTPUT_FILE"
