---
name: polymarket-paper
description: >
  Polymarket prediction market paper trading system. Scan markets for opportunities,
  execute simulated trades, track portfolio P&L, and generate daily reports.
  Use when: scanning Polymarket for trading opportunities, placing/closing paper trades,
  checking portfolio status, generating daily trading journals, or analyzing prediction
  market positions. Triggers on: polymarket, paper trading, prediction market, market scan,
  portfolio snapshot, trading journal.
---

# Polymarket Paper Trading

Paper trading system for Polymarket prediction markets using real market prices.

## Setup

Scripts are in `scripts/`. Data is stored at the project path (default: `~/.openclaw/workspace/projects/polymarket-paper/data/`).

Requires: `httpx` (`pip install httpx`)

## Core Commands

### Scan Markets

```bash
cd <project-path> && python3 scanner.py scan [limit]
```

Scans trending markets, filters by volume (>$10k) and identifies opportunities:
- **Near-certain**: YES/NO > 0.95 (high-confidence harvest)
- **Mispriced**: potential value bets
- **High-volume**: liquid markets for safe entry/exit

### Portfolio Snapshot

```bash
cd <project-path> && python3 trader.py snapshot
```

Shows all positions with current prices, P&L, and saves daily snapshot to `data/daily/YYYY-MM-DD.json`.

### Place Trade

```bash
cd <project-path> && python3 trader.py buy <condition_id> <YES|NO> <amount> [reason]
```

### Close Position

```bash
cd <project-path> && python3 trader.py sell <position_index> [amount]
```

### Trade History

```bash
cd <project-path> && python3 trader.py history
```

## Risk Controls (enforced)

- Max single trade: $100
- Max total exposure: $1,000
- Daily loss limit: $50 → stop trading for the day
- Min 24h volume: $10,000
- Every trade must have a recorded reason

## Daily Workflow

1. Run `trader.py snapshot` — capture current state
2. Run `scanner.py scan 30` — find new opportunities
3. Evaluate: close expiring positions? Open new ones?
4. Write daily journal to Obsidian: `Projects/Polymarket-Paper/YYYY-MM-DD.md`
5. Report summary to user

## Obsidian Integration

Daily journals go to `Projects/Polymarket-Paper/YYYY-MM-DD.md` with:
- Portfolio snapshot table
- Position details with entry/current prices and P&L
- Daily assessment and risk notes
- Tomorrow's action items

## Strategies

1. **High-confidence harvest** — Buy near-certain outcomes (>0.95) approaching expiry
2. **Hedge arbitrage** — Find logically opposing market pairs
3. **Value betting** — Identify mispriced events vs real-world probability
