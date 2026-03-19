---
name: token-tracker
description: >
  AI token usage tracker & cost dashboard. Analyzes OpenClaw session logs
  to report daily/weekly token usage and costs per agent. Use when asked
  about AI spending, token usage, cost dashboard, or budget alerts.
---

# Token Usage Tracker

Analyzes `/home/node/.openclaw/agents/*/sessions/*.jsonl` session logs.

## Usage

```bash
# Full 7-day report (stdout)
python3 skills/token-tracker/scripts/analyze.py

# Custom days
python3 skills/token-tracker/scripts/analyze.py --days 14

# Save to file
python3 skills/token-tracker/scripts/analyze.py --output /tmp/token-report.md

# Budget alert only (exits 0 if OK, prints alert if over budget)
python3 skills/token-tracker/scripts/analyze.py --alert-only
```

## Budget

Default daily budget: **$5.00 USD** (edit `DAILY_BUDGET_USD` in `analyze.py`)

## Cron

A daily cron job (Vince label) sends the report to Telegram every morning at 09:00 JST (00:00 UTC).
Cron job ID: `ed75d732-9fc7-4dbd-8c37-06625dabe09b` (daily 00:00 UTC = 09:00 JST)

## Data Source

Session `.jsonl` files contain `message` records with `usage` fields:
- `input`, `output`, `cacheRead`, `cacheWrite`, `totalTokens`
- `cost.total` (USD)

## Agents Tracked

`bird`, `bull`, `horse`, `main`, `newsbot`
