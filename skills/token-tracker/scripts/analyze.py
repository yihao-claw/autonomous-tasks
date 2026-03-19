#!/usr/bin/env python3
"""
Token Usage Tracker - Analyzes OpenClaw session logs for token usage and cost.
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

AGENTS_DIR = Path("/home/node/.openclaw/agents")
AGENTS = ["bird", "bull", "horse", "main", "newsbot"]

# Budget alert threshold
DAILY_BUDGET_USD = 5.0


def parse_date(ts_str):
    """Parse ISO timestamp to date string YYYY-MM-DD."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d"), dt
    except Exception:
        return None, None


def parse_session(filepath):
    """Parse a session JSONL file, return list of usage records."""
    records = []
    agent = filepath.parts[-3]  # agents/<agent>/sessions/<file>
    session_id = filepath.stem
    try:
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "message":
                    continue
                msg = d.get("message", {})
                if msg.get("role") != "assistant":
                    continue
                usage = msg.get("usage")
                if not usage:
                    continue
                date_str, dt = parse_date(d.get("timestamp", ""))
                if not date_str:
                    continue
                records.append({
                    "agent": agent,
                    "session_id": session_id,
                    "date": date_str,
                    "dt": dt,
                    "model": msg.get("model", "unknown"),
                    "input": usage.get("input", 0),
                    "output": usage.get("output", 0),
                    "cache_read": usage.get("cacheRead", 0),
                    "cache_write": usage.get("cacheWrite", 0),
                    "total_tokens": usage.get("totalTokens", 0),
                    "cost": usage.get("cost", {}).get("total", 0),
                })
    except Exception as e:
        pass
    return records


def load_all_records(days=7):
    """Load all usage records from the last N days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    all_records = []
    for agent in AGENTS:
        sessions_dir = AGENTS_DIR / agent / "sessions"
        if not sessions_dir.exists():
            continue
        for f in sessions_dir.glob("*.jsonl"):
            # Quick filter by file mtime
            mtime = f.stat().st_mtime
            if mtime < cutoff.timestamp():
                continue
            records = parse_session(f)
            all_records.extend(records)
    return all_records


def generate_report(days=7, today_only=False):
    """Generate markdown report."""
    records = load_all_records(days=days)
    if not records:
        return "No usage data found."

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    week_ago_str = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    prev_week_ago_str = (datetime.now(timezone.utc) - timedelta(days=14)).strftime("%Y-%m-%d")

    # Aggregate by date
    by_date = defaultdict(lambda: {"cost": 0, "tokens": 0, "input": 0, "output": 0})
    by_agent_date = defaultdict(lambda: defaultdict(lambda: {"cost": 0, "tokens": 0}))
    by_session = defaultdict(lambda: {"agent": "", "cost": 0, "tokens": 0, "date": "", "calls": 0})

    for r in records:
        by_date[r["date"]]["cost"] += r["cost"]
        by_date[r["date"]]["tokens"] += r["total_tokens"]
        by_date[r["date"]]["input"] += r["input"]
        by_date[r["date"]]["output"] += r["output"]
        by_agent_date[r["date"]][r["agent"]]["cost"] += r["cost"]
        by_agent_date[r["date"]][r["agent"]]["tokens"] += r["total_tokens"]
        sk = r["session_id"]
        by_session[sk]["agent"] = r["agent"]
        by_session[sk]["cost"] += r["cost"]
        by_session[sk]["tokens"] += r["total_tokens"]
        by_session[sk]["date"] = r["date"]
        by_session[sk]["calls"] += 1

    today_cost = by_date.get(today_str, {}).get("cost", 0)
    today_tokens = by_date.get(today_str, {}).get("tokens", 0)

    # This week vs last week
    this_week_cost = sum(v["cost"] for d, v in by_date.items() if d >= week_ago_str)
    prev_week_cost = sum(v["cost"] for d, v in by_date.items() if prev_week_ago_str <= d < week_ago_str)
    this_week_tokens = sum(v["tokens"] for d, v in by_date.items() if d >= week_ago_str)

    # Top 5 most expensive sessions
    top5 = sorted(by_session.values(), key=lambda x: x["cost"], reverse=True)[:5]

    # Today's agent breakdown
    today_agents = by_agent_date.get(today_str, {})
    agent_ranking = sorted(today_agents.items(), key=lambda x: x[1]["cost"], reverse=True)

    lines = []
    lines.append(f"# 🤖 Token Usage Report — {today_str}")
    lines.append("")

    # Budget alert
    if today_cost > DAILY_BUDGET_USD:
        lines.append(f"⚠️ **BUDGET ALERT**: Today's cost ${today_cost:.4f} exceeds daily budget ${DAILY_BUDGET_USD:.2f}!")
        lines.append("")

    lines.append("## 📊 Today's Summary")
    lines.append(f"- **Total Cost**: ${today_cost:.4f}")
    lines.append(f"- **Total Tokens**: {today_tokens:,}")
    input_t = by_date.get(today_str, {}).get("input", 0)
    output_t = by_date.get(today_str, {}).get("output", 0)
    lines.append(f"- Input: {input_t:,} | Output: {output_t:,}")
    lines.append("")

    lines.append("## 📅 This Week vs Last Week")
    delta = this_week_cost - prev_week_cost
    delta_pct = (delta / prev_week_cost * 100) if prev_week_cost > 0 else 0
    arrow = "📈" if delta > 0 else "📉"
    lines.append(f"- This week: **${this_week_cost:.4f}** ({this_week_tokens:,} tokens)")
    lines.append(f"- Last week: ${prev_week_cost:.4f}")
    if prev_week_cost > 0:
        lines.append(f"- Change: {arrow} {delta_pct:+.1f}% (${delta:+.4f})")
    lines.append("")

    lines.append("## 🏆 Today's Agent Ranking")
    if agent_ranking:
        for rank, (agent, data) in enumerate(agent_ranking, 1):
            lines.append(f"{rank}. **{agent}** — ${data['cost']:.4f} ({data['tokens']:,} tokens)")
    else:
        lines.append("_No activity today_")
    lines.append("")

    lines.append("## 💸 Top 5 Most Expensive Sessions (last 7 days)")
    for i, s in enumerate(top5, 1):
        lines.append(f"{i}. [{s['agent']}] {s['date']} — ${s['cost']:.4f} ({s['tokens']:,} tokens, {s['calls']} calls)")
    lines.append("")

    lines.append("## 📈 Daily Trend (last 7 days)")
    sorted_dates = sorted([d for d in by_date.keys() if d >= week_ago_str])
    for d in sorted_dates:
        v = by_date[d]
        marker = " ← today" if d == today_str else ""
        lines.append(f"- {d}: ${v['cost']:.4f} ({v['tokens']:,} tokens){marker}")
    lines.append("")

    return "\n".join(lines)


def check_budget_alert():
    """Check if today's spend exceeds budget. Return alert message or None."""
    records = load_all_records(days=1)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_cost = sum(r["cost"] for r in records if r["date"] == today_str)
    if today_cost > DAILY_BUDGET_USD:
        return f"⚠️ Budget Alert: Today's AI cost is ${today_cost:.4f}, exceeding the daily budget of ${DAILY_BUDGET_USD:.2f}!"
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Token Usage Tracker")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--alert-only", action="store_true", help="Only output budget alerts")
    parser.add_argument("--output", help="Output file path (default: stdout)")
    args = parser.parse_args()

    if args.alert_only:
        alert = check_budget_alert()
        if alert:
            print(alert)
        sys.exit(0)

    report = generate_report(days=args.days)

    if args.output:
        with open(args.output, "w") as f:
            f.write(report)
        print(f"Report written to {args.output}")
    else:
        print(report)
