# X Tracker Skill — Bird 🐦

追蹤指定 X/Twitter 帳號的最新推文，篩選有價值內容，推送到 Telegram。

## 架構

- **Brightdata MCP** (`@brightdata/mcp`) 做 scraping，繞過 X 的反爬蟲
- **x-check-new.py** 解析 markdown、提取推文、對比 state 去重
- **Bird agent** 負責內容篩選、摘要、推送

## 配置檔

| 檔案 | 用途 |
|------|------|
| `x-accounts.json` | 追蹤帳號清單 |
| `x-tracker-state.json` | 去重狀態（已見 tweet IDs） |
| `secrets/brightdata.json` | API token（路徑：`/home/node/.openclaw/agents/bird/agent/secrets/brightdata.json`） |

## 執行流程

### Step 0 — 載入配置

```bash
cd /home/node/.openclaw/workspace/projects/x-tracker
BRIGHTDATA_API_TOKEN=$(python3 -c "import json; print(json.load(open('/home/node/.openclaw/agents/bird/agent/secrets/brightdata.json'))['BRIGHTDATA_API_TOKEN'])")
```

### Step 1 — 逐帳號 Scrape + 去重

對 `x-accounts.json` 中每個 `enabled: true` 的帳號：

```bash
# Scrape profile page
BRIGHTDATA_API_TOKEN="$TOKEN" bash scripts/x-scrape.sh "https://x.com/{handle}" 90 \
  > /tmp/x-{handle}.md

# Parse and deduplicate
cat /tmp/x-{handle}.md | python3 scripts/x-check-new.py \
  --handle @{handle} \
  --state x-tracker-state.json \
  --update-state
```

- `hasNew: false` → 跳過此帳號
- `hasNew: true` → 繼續 Step 2

**限流**：每個帳號 scrape 間隔至少 3 秒（`sleep 3`），避免 Brightdata rate limit。

### Step 2 — 內容篩選與摘要

對每條新推文，判斷是否值得推送：

**推送條件**（符合任一即推）：
- 原創觀點或深度分析（非單純轉推/meme）
- 重要產品/公司公告
- 有數據支撐的行業洞察
- 值得關注的技術趨勢

**跳過條件**：
- 純社交互動（「thanks」「congrats」）
- 廣告/推廣內容
- 無實質內容的短推（< 50 字且無數據）

對值得推送的推文，用 `web_search` 搜尋補充背景（1 次即可）。

### Step 3 — 推送 Telegram

格式：
```
🐦 {name} (@{handle})
📅 {date}

{摘要 — 用中文，2-4 行，提煉核心觀點}

💬 原文節選：「{tweet 核心句}」

🔗 {tweet_url}
```

多條推文可合併成一則訊息，用 `---` 分隔。

發送方式：`message` tool
- channel: telegram
- accountId: bird
- target: `-1003767828002`
- threadId: `36`

### Step 4 — 無新內容

所有帳號都沒有新推文 → 回覆 **HEARTBEAT_OK**，結束。

## 帳號管理

編輯 `x-accounts.json` 增減追蹤帳號：
```json
{
  "handle": "@username",
  "name": "Display Name",
  "category": "AI/ML",
  "enabled": true,
  "note": "簡介"
}
```

## Step 5 — 市場推文共享（給 Bull）

對 category 含 `Politics`、`Market`、`Breaking News`、`Geopolitics`、`Crypto`、`Prediction Market`、`Trading` 的帳號推文，額外寫入共享 feed：

```python
import json, os
from datetime import datetime, timedelta

FEED_PATH = "/home/node/.openclaw/shared/x-market-feed/latest.json"

# Read existing
feed = json.load(open(FEED_PATH))

# Append new market tweet
feed["tweets"].append({
    "id": tweet_id,
    "handle": handle,
    "name": name,
    "category": category,
    "text": tweet_text,
    "date": tweet_date,
    "url": tweet_url,
    "marketRelevance": "high" or "medium",
    "summary": "中文摘要",
    "relatedMarkets": ["iran", "tariff", ...]
})

# Prune older than 48h
cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
feed["tweets"] = [t for t in feed["tweets"] if t["date"] > cutoff]
feed["updatedAt"] = datetime.utcnow().isoformat() + "Z"

json.dump(feed, open(FEED_PATH, "w"), indent=2, ensure_ascii=False)
```

Bull 在掃描市場時讀取 `/home/node/.openclaw/shared/x-market-feed/latest.json` 即可獲得最新市場情報。

## 注意事項

- Brightdata 免費額度 **5000 次/月**，每次 scrape 1 次請求
- 5 個帳號 × 每天 2 次 = 300 次/月，充裕
- X profile page 只顯示最新 ~5-10 條推文（含 pinned）
- Pinned tweet 會重複出現，靠 tweet ID 去重
- 若 scrape 失敗（timeout/block），記錄錯誤但不中斷其他帳號
- State file 每個 handle 保留最近 200 個 tweet IDs
