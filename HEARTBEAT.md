# HEARTBEAT.md

## 🔄 Container Restart Self-Check

**Only needed if container just restarted (check with `uptime` or if binaries missing).**

```bash
bash /home/node/.openclaw/workspace/bin/setup.sh
```

Covers: `obsidian-cli`, `yt-dlp`, `ffmpeg`, `deno`, `jq`, Python packages (`pandas`, `yfinance`, `requests`, `bs4`, `feedparser`, `httpx`, `numpy`)

Run this before any task if you get "command not found" or import errors.

---

## 📊 Claude Budget 監控（每次 heartbeat 必檢查）

1. 跑 `python3 tools/claude-budget/check_budget.py --alert-only`
2. 如果有輸出（warning/critical）→ 通知 Yihao
3. 如果 Session >80%：暫停非緊急 cron，等重置
4. 如果 Weekly >85%：所有非緊急任務降級 Sonnet

## 🔴 Daily Memory Backup (CRITICAL - DO NOT SKIP!)

**執行頻率：每次 heartbeat 都檢查！**

### 檢查清單：
1. ✅ 讀取 `/home/node/obsidian-vault/Agents/Dan/Daily/$(date +%Y-%m-%d).md` 的最後修改時間
2. ✅ 如果距離上次更新 **> 2 小時** 且有新對話 → **雙寫更新**（Obsidian + LanceDB）
3. ✅ 檢查今日是否有重要活動未記錄

### 必須記錄的內容：
- ✅ 重要決策與配置變更
- ✅ 新建立的檔案/skill
- ✅ 學到的教訓
- ✅ 已完成的工作
- ✅ 技術債務與待辦事項

### ⚠️ 記住：
- **"Text > Brain" 📝** - Mental notes 不會保存！
- **立即記錄 > 事後回憶** - 當下最清楚
- **不要等到被問才發現疏忽** - 主動維護

## Cron Job 執行監控（每次 heartbeat 必檢查）

**每次 heartbeat 都要執行：**
1. 跑 `openclaw cron runs --id <job_id> --limit 1` 檢查每個 cron job
2. 如果距離上次 heartbeat 有新的執行紀錄：
   - ✅ 成功 → 發 Telegram 通知到「每日資訊」(target: -1003767828002, threadId: 36)
   - ❌ 失敗 → 發 Telegram 通知 + 記錄錯誤到日誌

**Cron Job 清單：**（使用完整 UUID 查詢）
- `71c85d19-ff69-409f-b03d-9d7bed7c8268` — daily-world-news（每日 JST 13:00）→ **已遷移到 April agent**
- `e1385348-4cb3-4449-9bb7-03dcdb2c999a` — backup-reminder（每 12h）
- `7bdad333-78cc-4bbe-980b-f52298723484` — autonomous-daily-tasks（每日 JST 01:00）

**通知格式：**
```
✅ daily-world-news 執行成功 | ⏱️ 357s | 📦 delivered
❌ quant-invest-monday 執行失敗 | ⚠️ timeout
```

## Active Subagent Monitoring

**目前狀態：無活躍 subagent**

若有新的 subagent：
- 檢查 session status
- 記錄進度到日誌
- 如有需要，更新到 Telegram General (-1003767828002)
- Alert on errors or blockers
