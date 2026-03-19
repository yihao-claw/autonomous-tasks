#!/usr/bin/env python3
"""
AI Token Usage Tracker & Cost Dashboard
Analyzes OpenClaw session logs to report token usage and costs per agent.
"""

import json
import os
import glob
import sys
from datetime import datetime, timezone, timedelta
from collections import defaultdict

AGENTS_DIR = "/home/node/.openclaw/agents"
AGENTS = ["main", "horse", "bird", "bull", "newsbot"]

# Budget threshold (USD per day)
DAILY_BUDGET = 5.0


def parse_sessions(agent, days=7):
    """Parse session logs for an agent, returning usage stats."""
    sessions_dir = os.path.join(AGENTS_DIR, agent, "sessions")
    if not os.path.exists(sessions_dir):
        return []

    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for filepath in glob.glob(os.path.join(sessions_dir, "*.jsonl")):
        # Skip deleted files
        if ".deleted." in filepath:
            continue

        session_data = {
            "session_id": os.path.basename(filepath).replace(".jsonl", "")[:8],
            "agent": agent,
            "timestamp": None,
            "model": None,
            "total_input": 0,
            "total_output": 0,
            "total_cache_read": 0,
            "total_cache_write": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "turns": 0,
        }

        try:
            with open(filepath) as f:
                for line in f:
                    try:
                        d = json.loads(line.strip())
                    except:
                        continue

                    if d.get("type") == "session" and "timestamp" in d:
                        ts_str = d["timestamp"]
                        try:
                            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            session_data["timestamp"] = ts
                            # Skip sessions older than cutoff
                            if ts < cutoff:
                                session_data = None
                                break
                        except:
                            pass

                    elif d.get("type") == "message" and d.get("message", {}).get("role") == "assistant":
                        msg = d["message"]
                        usage = msg.get("usage", {})
                        if usage:
                            session_data["total_input"] += usage.get("input", 0)
                            session_data["total_output"] += usage.get("output", 0)
                            session_data["total_cache_read"] += usage.get("cacheRead", 0)
                            session_data["total_cache_write"] += usage.get("cacheWrite", 0)
                            session_data["total_tokens"] += usage.get("totalTokens", 0)
                            cost = usage.get("cost", {})
                            if cost:
                                session_data["total_cost"] += cost.get("total", 0)
                            session_data["turns"] += 1

                        if not session_data["model"] and msg.get("model"):
                            session_data["model"] = msg["model"]

        except Exception as e:
            continue

        if session_data and session_data["total_tokens"] > 0:
            results.append(session_data)

    return results


def generate_report(days=1):
    """Generate a markdown report for the specified number of days."""
    all_sessions = []
    for agent in AGENTS:
        sessions = parse_sessions(agent, days=days)
        all_sessions.extend(sessions)

    # Filter to requested day range
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent = [s for s in all_sessions if s["timestamp"] and s["timestamp"] >= cutoff]

    # Also get weekly data (re-fetch with 7d window)
    weekly_sessions = []
    for agent in AGENTS:
        s7 = parse_sessions(agent, days=7)
        weekly_sessions.extend(s7)
    week_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    weekly = [s for s in weekly_sessions if s["timestamp"] and s["timestamp"] >= week_cutoff]

    # Aggregate by agent
    def aggregate(sessions):
        by_agent = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "sessions": 0, "turns": 0})
        for s in sessions:
            by_agent[s["agent"]]["tokens"] += s["total_tokens"]
            by_agent[s["agent"]]["cost"] += s["total_cost"]
            by_agent[s["agent"]]["sessions"] += 1
            by_agent[s["agent"]]["turns"] += s["turns"]
        return by_agent

    today_stats = aggregate(recent)
    week_stats = aggregate(weekly)

    total_today_cost = sum(v["cost"] for v in today_stats.values())
    total_today_tokens = sum(v["tokens"] for v in today_stats.values())
    total_week_cost = sum(v["cost"] for v in week_stats.values())

    # Top sessions by cost
    top_sessions = sorted(recent, key=lambda x: x["total_cost"], reverse=True)[:5]

    # Build report
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    period = "今日" if days == 1 else f"過去 {days} 天"

    lines = [
        f"# 🤖 AI Token 用量報告",
        f"*{now}*",
        "",
        f"## 📊 {period}總覽",
        f"- **總 Token 數**: {total_today_tokens:,}",
        f"- **總估計成本**: ${total_today_cost:.4f}",
        f"- **Session 數**: {len(recent)}",
        "",
    ]

    # Budget warning
    if total_today_cost > DAILY_BUDGET:
        lines.append(f"⚠️ **預算警報**: 今日花費 ${total_today_cost:.2f} 超過 ${DAILY_BUDGET:.2f} 預算！")
        lines.append("")
    elif total_today_cost > DAILY_BUDGET * 0.8:
        lines.append(f"⚡ **預算提醒**: 今日花費 ${total_today_cost:.2f}，已達預算 80%")
        lines.append("")

    # By agent
    lines.append("## 👤 各 Agent 排名（今日）")
    sorted_agents = sorted(today_stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    for agent, stats in sorted_agents:
        if stats["tokens"] > 0:
            lines.append(f"- **{agent}**: {stats['tokens']:,} tokens | ${stats['cost']:.4f} | {stats['sessions']} sessions | {stats['turns']} turns")

    if not sorted_agents or all(v["tokens"] == 0 for v in today_stats.values()):
        lines.append("- *(今日無資料)*")

    lines.append("")

    # Weekly comparison
    lines.append("## 📈 本週趨勢（7天）")
    lines.append(f"- **週總成本**: ${total_week_cost:.4f}")
    lines.append(f"- **日均成本**: ${total_week_cost/7:.4f}")
    sorted_week = sorted(week_stats.items(), key=lambda x: x[1]["cost"], reverse=True)
    for agent, stats in sorted_week:
        if stats["tokens"] > 0:
            lines.append(f"- **{agent}**: {stats['tokens']:,} tokens | ${stats['cost']:.4f} (7d)")
    lines.append("")

    # Top sessions
    if top_sessions:
        lines.append(f"## 💸 最貴的 5 個 Sessions（今日）")
        for s in top_sessions:
            ts_str = s["timestamp"].strftime("%H:%M") if s["timestamp"] else "?"
            lines.append(f"- `{s['session_id']}` [{s['agent']}] {ts_str} — {s['total_tokens']:,} tokens | ${s['total_cost']:.4f} | model: {s['model'] or '?'}")
        lines.append("")

    lines.append(f"---")
    lines.append(f"*預算警戒線: ${DAILY_BUDGET}/day*")

    return "\n".join(lines)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(generate_report(days=days))
