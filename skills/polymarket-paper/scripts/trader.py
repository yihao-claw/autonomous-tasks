#!/usr/bin/env python3
"""Paper trading engine — simulate trades with real market prices."""

import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from scanner import get_midpoint, get_trending_markets

DATA_DIR = Path(__file__).parent / "data"
TRADES_FILE = DATA_DIR / "trades.json"
PORTFOLIO_FILE = DATA_DIR / "portfolio.json"
DAILY_LOG_DIR = DATA_DIR / "daily"

# Paper trading config
INITIAL_BALANCE = 1000.0  # Starting virtual USDC
MAX_POSITION_SIZE = 100.0  # Max per trade
MAX_TOTAL_EXPOSURE = 1000.0  # Max total


def init_data():
    """Initialize data directories and files."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DAILY_LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not PORTFOLIO_FILE.exists():
        portfolio = {
            "balance": INITIAL_BALANCE,
            "positions": [],
            "totalDeposited": INITIAL_BALANCE,
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
        PORTFOLIO_FILE.write_text(json.dumps(portfolio, indent=2))

    if not TRADES_FILE.exists():
        TRADES_FILE.write_text(json.dumps([], indent=2))


def load_portfolio():
    init_data()
    return json.loads(PORTFOLIO_FILE.read_text())


def save_portfolio(portfolio):
    PORTFOLIO_FILE.write_text(json.dumps(portfolio, indent=2, ensure_ascii=False))


def load_trades():
    init_data()
    return json.loads(TRADES_FILE.read_text())


def save_trades(trades):
    TRADES_FILE.write_text(json.dumps(trades, indent=2, ensure_ascii=False))


def paper_buy(condition_id, side, amount, question="", token_id=""):
    """Simulate buying a position."""
    portfolio = load_portfolio()
    trades = load_trades()

    if amount > MAX_POSITION_SIZE:
        print(f"Error: Max position size is ${MAX_POSITION_SIZE}")
        return None

    if amount > portfolio["balance"]:
        print(f"Error: Insufficient balance. Have ${portfolio['balance']:.2f}, need ${amount:.2f}")
        return None

    # Get current price
    price = get_midpoint(token_id)
    if price <= 0:
        print(f"Error: Could not get price for token {token_id}")
        return None

    shares = amount / price
    trade_id = str(uuid.uuid4())[:8]

    trade = {
        "id": trade_id,
        "type": "BUY",
        "conditionId": condition_id,
        "tokenId": token_id,
        "side": side.upper(),
        "question": question,
        "entryPrice": round(price, 4),
        "shares": round(shares, 4),
        "cost": round(amount, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "OPEN",
    }

    # Update portfolio
    portfolio["balance"] -= amount
    portfolio["positions"].append({
        "tradeId": trade_id,
        "conditionId": condition_id,
        "tokenId": token_id,
        "side": side.upper(),
        "question": question,
        "entryPrice": round(price, 4),
        "shares": round(shares, 4),
        "cost": round(amount, 2),
        "openedAt": trade["timestamp"],
    })

    trades.append(trade)
    save_portfolio(portfolio)
    save_trades(trades)

    print(f"📝 Paper BUY: {side.upper()} on '{question[:60]}...'")
    print(f"   Price: ${price:.4f} | Shares: {shares:.2f} | Cost: ${amount:.2f}")
    print(f"   Trade ID: {trade_id}")
    return trade


def paper_sell(trade_id):
    """Simulate selling/closing a position."""
    portfolio = load_portfolio()
    trades = load_trades()

    # Find position
    pos = None
    pos_idx = None
    for i, p in enumerate(portfolio["positions"]):
        if p["tradeId"] == trade_id:
            pos = p
            pos_idx = i
            break

    if pos is None:
        print(f"Error: Position {trade_id} not found")
        return None

    # Get current price
    current_price = get_midpoint(pos["tokenId"])
    if current_price <= 0:
        print(f"Error: Could not get price for token")
        return None

    proceeds = pos["shares"] * current_price
    pnl = proceeds - pos["cost"]
    pnl_pct = (pnl / pos["cost"]) * 100

    sell_trade = {
        "id": str(uuid.uuid4())[:8],
        "type": "SELL",
        "conditionId": pos["conditionId"],
        "tokenId": pos["tokenId"],
        "side": pos["side"],
        "question": pos["question"],
        "entryPrice": pos["entryPrice"],
        "exitPrice": round(current_price, 4),
        "shares": pos["shares"],
        "cost": pos["cost"],
        "proceeds": round(proceeds, 2),
        "pnl": round(pnl, 2),
        "pnlPct": round(pnl_pct, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CLOSED",
        "originalTradeId": trade_id,
    }

    # Update portfolio
    portfolio["balance"] += proceeds
    portfolio["positions"].pop(pos_idx)

    # Mark original trade as closed
    for t in trades:
        if t["id"] == trade_id:
            t["status"] = "CLOSED"
            t["exitPrice"] = round(current_price, 4)
            t["pnl"] = round(pnl, 2)
            t["pnlPct"] = round(pnl_pct, 2)
            t["closedAt"] = sell_trade["timestamp"]

    trades.append(sell_trade)
    save_portfolio(portfolio)
    save_trades(trades)

    emoji = "🟢" if pnl >= 0 else "🔴"
    print(f"{emoji} Paper SELL: {pos['side']} on '{pos['question'][:60]}...'")
    print(f"   Entry: ${pos['entryPrice']:.4f} → Exit: ${current_price:.4f}")
    print(f"   P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)")
    return sell_trade


def show_portfolio():
    """Display current portfolio with live P&L."""
    portfolio = load_portfolio()

    print("=" * 70)
    print("📊 POLYMARKET PAPER PORTFOLIO")
    print("=" * 70)
    print(f"💰 Cash Balance: ${portfolio['balance']:.2f}")
    print(f"📅 Started: {portfolio.get('createdAt', 'N/A')}")
    print()

    total_value = portfolio["balance"]
    total_cost = 0
    total_unrealized = 0

    if not portfolio["positions"]:
        print("No open positions.")
    else:
        print(f"{'Side':<5} {'Question':<40} {'Entry':>8} {'Now':>8} {'P&L':>10} {'P&L%':>8}")
        print("-" * 70)

        for pos in portfolio["positions"]:
            try:
                current = get_midpoint(pos["tokenId"])
                value = pos["shares"] * current
                pnl = value - pos["cost"]
                pnl_pct = (pnl / pos["cost"]) * 100 if pos["cost"] > 0 else 0
                total_value += value
                total_cost += pos["cost"]
                total_unrealized += pnl

                emoji = "🟢" if pnl >= 0 else "🔴"
                q = pos["question"][:38] + ".." if len(pos["question"]) > 40 else pos["question"]
                print(f"{pos['side']:<5} {q:<40} ${pos['entryPrice']:>6.4f} ${current:>6.4f} {emoji}${pnl:>+7.2f} {pnl_pct:>+7.2f}%")
            except Exception as e:
                print(f"{pos['side']:<5} {pos['question'][:40]:<40} ${pos['entryPrice']:>6.4f} {'ERR':>8} {'N/A':>10}")
                total_value += pos["cost"]  # assume no change on error

    print("=" * 70)
    total_pnl = total_value - INITIAL_BALANCE
    total_pnl_pct = (total_pnl / INITIAL_BALANCE) * 100
    emoji = "🟢" if total_pnl >= 0 else "🔴"
    print(f"💼 Total Portfolio Value: ${total_value:.2f}")
    print(f"📈 Unrealized P&L: ${total_unrealized:+.2f}")
    print(f"{emoji} Total P&L: ${total_pnl:+.2f} ({total_pnl_pct:+.2f}%)")
    print("=" * 70)

    return {
        "balance": portfolio["balance"],
        "totalValue": round(total_value, 2),
        "totalPnl": round(total_pnl, 2),
        "totalPnlPct": round(total_pnl_pct, 2),
        "positions": len(portfolio["positions"]),
    }


def save_daily_snapshot():
    """Save daily snapshot for tracking."""
    summary = show_portfolio()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snapshot_file = DAILY_LOG_DIR / f"{today}.json"

    snapshot = {
        "date": today,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **summary,
    }
    snapshot_file.write_text(json.dumps(snapshot, indent=2))
    print(f"\n📸 Daily snapshot saved: {snapshot_file}")
    return snapshot


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "portfolio"

    if cmd == "portfolio":
        show_portfolio()
    elif cmd == "snapshot":
        save_daily_snapshot()
    elif cmd == "buy":
        if len(sys.argv) < 6:
            print("Usage: python trader.py buy <condition_id> <token_id> <YES|NO> <amount> [question]")
            sys.exit(1)
        cid = sys.argv[2]
        tid = sys.argv[3]
        side = sys.argv[4]
        amt = float(sys.argv[5])
        q = sys.argv[6] if len(sys.argv) > 6 else ""
        paper_buy(cid, side, amt, question=q, token_id=tid)
    elif cmd == "sell":
        if len(sys.argv) < 3:
            print("Usage: python trader.py sell <trade_id>")
            sys.exit(1)
        paper_sell(sys.argv[2])
    else:
        print("Usage: python trader.py [portfolio|snapshot|buy|sell]")
