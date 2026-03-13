#!/bin/bash
# cron-monitor.sh — 檢查 cron job 執行狀態並通知
# 由 cron job 每 30 分鐘呼叫一次

JOBS=(
  "71c85d19-ff69-409f-b03d-9d7bed7c8268:daily-world-news"
  "eb29e401-2d35-4330-9cb6-5cd36b910e91:quant-invest-monday"
  "b45b7d5b-e9b3-44d0-8206-4b90eafb7b07:quant-invest-friday"
  "e1385348-4cb3-4449-9bb7-03dcdb2c999a:backup-reminder"
)

STATE_FILE="/tmp/cron-monitor-last.json"
NOW_MS=$(date +%s000)
THIRTY_MIN_AGO=$(( NOW_MS - 1800000 ))

# 初始化 state file
if [ ! -f "$STATE_FILE" ]; then
  echo '{}' > "$STATE_FILE"
fi

for entry in "${JOBS[@]}"; do
  JOB_ID="${entry%%:*}"
  JOB_NAME="${entry##*:}"
  
  # 取得最新一筆 run
  RESULT=$(openclaw cron runs --id "$JOB_ID" --limit 1 2>/dev/null)
  
  if [ -z "$RESULT" ]; then
    continue
  fi
  
  # 用 python 解析
  python3 << PYEOF "$RESULT" "$JOB_NAME" "$STATE_FILE" "$THIRTY_MIN_AGO"
import json, sys

result = json.loads(sys.argv[1])
job_name = sys.argv[2]
state_file = sys.argv[3]
threshold = int(sys.argv[4])

entries = result.get('entries', [])
if not entries:
    sys.exit(0)

latest = entries[0]
run_at = latest.get('runAtMs', 0)
status = latest.get('status', 'unknown')

# 讀取上次通知的 timestamp
with open(state_file) as f:
    state = json.load(f)

last_notified = state.get(job_name, 0)

# 只通知新的 run（且在最近 30 分鐘內）
if run_at > last_notified and run_at > threshold:
    duration = latest.get('durationMs', 0) / 1000
    delivered = latest.get('delivered', False)
    
    if status == 'ok':
        msg = f"✅ {job_name} 執行成功 | ⏱️ {duration:.0f}s | 📦 {'delivered' if delivered else 'not delivered'}"
    else:
        error = latest.get('error', latest.get('summary', 'unknown error'))[:200]
        msg = f"❌ {job_name} 執行失敗 | ⚠️ {error}"
    
    print(msg)
    
    # 更新 state
    state[job_name] = run_at
    with open(state_file, 'w') as f:
        json.dump(state, f)
PYEOF

done
