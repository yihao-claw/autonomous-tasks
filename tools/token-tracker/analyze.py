#!/usr/bin/env python3
"""
Token Usage Tracker & Cost Dashboard
Analyzes OpenClaw session logs for all agents.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from pathlib import Path

AGENTS_DIR = Path("/home/node/.openclaw/agents")
BUDGET_DAILY = float(os.environ.get("BUDGET_DAILY", "5.0"))

def parse_session(session_file):
    """Parse a session JSONL file and return usage data."""
    messages = []
    session_info = {}
    
    try:
        with open(session_file) as f:
            for line in f:
                try:
                    d = json.loads(line.strip())
                except:
                    continue
                
                if d.get("type") == "session":
                    session_info = {
                        "id": d.get("id"),
                        "timestamp": d.get("timestamp"),
                    }
                
                if d.get("type") == "message":
                    msg = d.get("message", {})
                    usage = msg.get("usage")
                    if usage and usage.get("cost"):
                        messages.append({
                            "ts": d.get("timestamp"),
                            "model": msg.get("model", "unknown"),
                            "input": usage.get("input", 0),
                            "output": usage.get("output", 0),
                            "cacheRead": usage.get("cacheRead", 0),
                            "cacheWrite": usage.get("cacheWrite", 0),
                            "totalTokens": usage.get("totalTokens", 0),
                            "cost": usage.get("cost", {}).get("total", 0),
                        })
    except Exception as e:
        pass
    
    return session_info, messages


def collect_all_data():
    """Collect usage data from all agents."""
    data = []  # list of {agent, session_id, session_ts, messages}
    
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent = agent_dir.name
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.exists():
            continue
        
        for session_file in sessions_dir.glob("*.jsonl"):
            # Skip deleted files
            if ".deleted." in session_file.name:
                continue
            
            session_info, messages = parse_session(session_file)
            if messages:
                data.append({
                    "agent": agent,
                    "session_id": session_info.get("id", session_file.stem),
                    "session_ts": session_info.get("timestamp", ""),
                    "messages": messages,
                })
    
    return data


def parse_dt(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except:
        return None


def generate_report(days=7):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=days-1)
    last_week_start = week_start - timedelta(days=days)

    data = collect_all_data()

    # Aggregate: by day, by agent, by session
    daily_totals = defaultdict(lambda: {"cost": 0.0, "tokens": 0})
    agent_totals = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "sessions": set()})
    session_totals = []
    
    today_cost = 0.0
    today_tokens = 0
    week_cost = 0.0
    week_tokens = 0
    last_week_cost = 0.0

    for entry in data:
        agent = entry["agent"]
        session_id = entry["session_id"]
        session_cost = 0.0
        session_tokens = 0
        session_first_ts = None

        for msg in entry["messages"]:
            ts = parse_dt(msg["ts"])
            if not ts:
                continue
            if session_first_ts is None:
                session_first_ts = ts
            
            cost = msg["cost"]
            tokens = msg["totalTokens"]
            day_key = ts.strftime("%Y-%m-%d")
            
            daily_totals[day_key]["cost"] += cost
            daily_totals[day_key]["tokens"] += tokens
            agent_totals[agent]["cost"] += cost
            agent_totals[agent]["tokens"] += tokens
            agent_totals[agent]["sessions"].add(session_id)
            session_cost += cost
            session_tokens += tokens
            
            if ts >= today_start:
                today_cost += cost
                today_tokens += tokens
            if ts >= week_start:
                week_cost += cost
                week_tokens += tokens
            if last_week_start <= ts < week_start:
                last_week_cost += cost

        if session_cost > 0:
            session_totals.append({
                "agent": agent,
                "session_id": session_id,
                "ts": session_first_ts,
                "cost": session_cost,
                "tokens": session_tokens,
            })

    # Top 5 sessions by cost (last 7 days)
    recent_sessions = [s for s in session_totals 
                       if s["ts"] and s["ts"] >= week_start]
    top5 = sorted(recent_sessions, key=lambda x: x["cost"], reverse=True)[:5]

    # Trend
    trend = ""
    if last_week_cost > 0:
        pct = ((week_cost - last_week_cost) / last_week_cost) * 100
        arrow = "↑" if pct > 0 else "↓"
        trend = f"{arrow} {abs(pct):.1f}% vs previous {days} days (${last_week_cost:.4f})"
    else:
        trend = "No data from previous period"

    # Budget alert
    budget_alert = ""
    if today_cost >= BUDGET_DAILY:
        budget_alert = f"🚨 **BUDGET ALERT**: Today's cost ${today_cost:.4f} exceeds limit ${BUDGET_DAILY:.2f}!"
    elif today_cost >= BUDGET_DAILY * 0.8:
        budget_alert = f"⚠️ **Budget Warning**: ${today_cost:.4f} used today (80% of ${BUDGET_DAILY:.2f} limit)"

    # Generate report
    lines = []
    lines.append(f"# 📊 AI Token Usage Report")
    lines.append(f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}\n")

    if budget_alert:
        lines.append(budget_alert + "\n")

    lines.append("## 💰 Summary")
    lines.append(f"| Period | Tokens | Cost |")
    lines.append(f"|--------|--------|------|")
    lines.append(f"| Today | {today_tokens:,} | ${today_cost:.4f} |")
    lines.append(f"| This {days} days | {week_tokens:,} | ${week_cost:.4f} |")
    lines.append(f"\n**Trend:** {trend}\n")

    lines.append("## 🤖 Agent Rankings (last 7 days)")
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["cost"], reverse=True)
    lines.append(f"| Agent | Sessions | Tokens | Cost |")
    lines.append(f"|-------|----------|--------|------|")
    for agent, stats in sorted_agents:
        # Filter to last 7 days
        agent_week_cost = sum(
            msg["cost"] for entry in data 
            if entry["agent"] == agent
            for msg in entry["messages"]
            if (ts := parse_dt(msg["ts"])) and ts >= week_start
        )
        agent_week_tokens = sum(
            msg["totalTokens"] for entry in data
            if entry["agent"] == agent
            for msg in entry["messages"]
            if (ts := parse_dt(msg["ts"])) and ts >= week_start
        )
        n_sessions = len([s for s in recent_sessions if s["agent"] == agent])
        if agent_week_cost > 0:
            lines.append(f"| {agent} | {n_sessions} | {agent_week_tokens:,} | ${agent_week_cost:.4f} |")

    lines.append("\n## 🔥 Top 5 Most Expensive Sessions (last 7 days)")
    for i, s in enumerate(top5, 1):
        ts_str = s["ts"].strftime("%m-%d %H:%M") if s["ts"] else "unknown"
        lines.append(f"{i}. **{s['agent']}** `{s['session_id'][:8]}` — ${s['cost']:.4f} ({s['tokens']:,} tokens) [{ts_str}]")

    lines.append("\n## 📈 Daily Breakdown (last 7 days)")
    lines.append(f"| Date | Tokens | Cost |")
    lines.append(f"|------|--------|------|")
    for i in range(days-1, -1, -1):
        day = (today_start - timedelta(days=i)).strftime("%Y-%m-%d")
        d = daily_totals.get(day, {"cost": 0.0, "tokens": 0})
        marker = " ← today" if i == 0 else ""
        lines.append(f"| {day}{marker} | {d['tokens']:,} | ${d['cost']:.4f} |")

    return "\n".join(lines)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    report = generate_report(days)
    print(report)
