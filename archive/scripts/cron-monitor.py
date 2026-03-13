#!/usr/bin/env python3
"""cron-monitor.py — 檢查 cron job 執行狀態，輸出新的執行結果"""

import json
import subprocess
import sys
import os

JOBS = {
    "71c85d19-ff69-409f-b03d-9d7bed7c8268": "daily-world-news",
    "eb29e401-2d35-4330-9cb6-5cd36b910e91": "quant-invest-monday",
    "b45b7d5b-e9b3-44d0-8206-4b90eafb7b07": "quant-invest-friday",
    "e1385348-4cb3-4449-9bb7-03dcdb2c999a": "backup-reminder",
}

STATE_FILE = "/tmp/cron-monitor-state.json"

# 載入上次狀態
state = {}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)

notifications = []

for job_id, job_name in JOBS.items():
    try:
        result = subprocess.run(
            ["openclaw", "cron", "runs", "--id", job_id, "--limit", "1"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
    except Exception:
        continue

    entries = data.get("entries", [])
    if not entries:
        continue

    latest = entries[0]
    run_at = latest.get("runAtMs", 0)
    last_notified = state.get(job_id, 0)

    if run_at > last_notified:
        status = latest.get("status", "unknown")
        duration = latest.get("durationMs", 0) / 1000
        delivered = latest.get("delivered", False)

        if status == "ok":
            notifications.append(
                f"✅ {job_name} 執行成功 | ⏱️ {duration:.0f}s | 📦 {'delivered' if delivered else 'not delivered'}"
            )
        else:
            error = str(latest.get("error", latest.get("summary", "unknown")))[:200]
            notifications.append(
                f"❌ {job_name} 執行失敗 | ⚠️ {error}"
            )

        state[job_id] = run_at

# 儲存狀態
with open(STATE_FILE, "w") as f:
    json.dump(state, f)

# 輸出
if notifications:
    print("\n".join(notifications))
