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
OBSIDIAN_DIR = Path("/home/node/obsidian-vault/Agents/Vince/Daily")

# Known cron session labels for naming
CRON_LABELS = {
    "linear-todo-check": "linear-todo-check (horse)",
    "autonomous-daily-tasks": "autonomous-daily-tasks (horse)",
    "daily-openclaw-backup": "daily-backup (horse)",
    "vince-daily-note-generator": "vince-daily-note (horse)",
    "weekly-git-repo-health-report": "weekly-git-health (horse)",
    "yt-channels-hourly": "yt-hourly (bird)",
    "yt-channels-daily": "yt-daily (bird)",
    "x-tracker-market": "x-market (bird)",
    "x-tracker-tech": "x-tech (bird)",
    "daily-world-news": "daily-world-news (bird)",
    "polymarket-scan": "polymarket-scan (bull)",
    "nicolas-daily-proposal": "daily-proposal (nicolas)",
    "daily-token-report": "token-report (main)",
    "daily-knowledge-digest": "knowledge-digest (main)",
    "yh-jp-proactive-check": "proactive-check (main)",
    "yh-jp-daily-ops-report": "ops-report (main)",
    "x-monitor-daily": "x-monitor (main)",
}


def emoji_bar(value, max_value, width=10):
    """Create an emoji bar chart."""
    if max_value == 0:
        return "░" * width
    filled = round((value / max_value) * width)
    return "█" * filled + "░" * (width - filled)


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
                        "label": d.get("label", ""),
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
    data = []

    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent = agent_dir.name
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.exists():
            continue

        for session_file in sessions_dir.glob("*.jsonl"):
            if ".deleted." in session_file.name:
                continue

            session_info, messages = parse_session(session_file)
            if messages:
                data.append({
                    "agent": agent,
                    "session_id": session_info.get("id", session_file.stem),
                    "session_ts": session_info.get("timestamp", ""),
                    "label": session_info.get("label", ""),
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


def model_downgrade_recommendation(avg_cost_per_run, label):
    """Suggest model downgrade based on cost."""
    if avg_cost_per_run > 0.5:
        return "⚠️ Consider haiku for simple steps"
    elif avg_cost_per_run > 0.1:
        return "💡 Review if opus needed"
    elif avg_cost_per_run < 0.01:
        return "✅ Efficient"
    return ""


def generate_report(days=7, save_obsidian=False):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=days - 1)
    last_week_start = week_start - timedelta(days=days)

    data = collect_all_data()

    # Aggregate
    daily_totals = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "new_tokens": 0})
    agent_totals = defaultdict(lambda: {"cost": 0.0, "tokens": 0, "new_tokens": 0, "sessions": set()})
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
        session_new_tokens = 0
        session_first_ts = None

        for msg in entry["messages"]:
            ts = parse_dt(msg["ts"])
            if not ts:
                continue
            if session_first_ts is None:
                session_first_ts = ts

            cost = msg["cost"]
            tokens = msg["totalTokens"]
            new_tokens = msg["input"] + msg["output"] + msg["cacheWrite"]
            day_key = ts.strftime("%Y-%m-%d")

            daily_totals[day_key]["cost"] += cost
            daily_totals[day_key]["tokens"] += tokens
            daily_totals[day_key]["new_tokens"] += new_tokens
            agent_totals[agent]["cost"] += cost
            agent_totals[agent]["tokens"] += tokens
            agent_totals[agent]["new_tokens"] += new_tokens
            agent_totals[agent]["sessions"].add(session_id)
            session_cost += cost
            session_tokens += tokens
            session_new_tokens += new_tokens

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
                "label": entry.get("label", ""),
                "ts": session_first_ts,
                "cost": session_cost,
                "tokens": session_tokens,
                "new_tokens": session_new_tokens,
            })

    # Top sessions last 7 days
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

    # Daily costs for bar chart
    daily_list = []
    for i in range(days - 1, -1, -1):
        day = (today_start - timedelta(days=i)).strftime("%Y-%m-%d")
        d = daily_totals.get(day, {"cost": 0.0, "tokens": 0, "new_tokens": 0})
        daily_list.append((day, d))

    max_day_cost = max((d["cost"] for _, d in daily_list), default=1)

    # Weekly cost (current + previous)
    week2_start = last_week_start - timedelta(days=days)
    last2_week_cost = 0.0
    for entry in data:
        for msg in entry["messages"]:
            ts = parse_dt(msg["ts"])
            if ts and week2_start <= ts < last_week_start:
                last2_week_cost += msg["cost"]

    # Budget recommendation based on actual usage (3 weeks of data)
    week_costs = [c for c in [last2_week_cost, last_week_cost, week_cost] if c > 0]
    if week_costs:
        avg_weekly = sum(week_costs) / len(week_costs)
        # Exclude outlier days for daily average
        all_day_costs = [d["cost"] for _, d in daily_list if d["cost"] > 0]
        if all_day_costs:
            # Use median-based: sort, take p75 as budget
            sorted_days = sorted(all_day_costs)
            p75_idx = int(len(sorted_days) * 0.75)
            recommended_daily = sorted_days[min(p75_idx, len(sorted_days) - 1)] * 1.5
            recommended_daily = max(recommended_daily, 2.0)  # floor $2
            recommended_weekly = avg_weekly * 1.3  # 30% buffer
        else:
            recommended_daily = BUDGET_DAILY
            recommended_weekly = BUDGET_DAILY * 7
    else:
        recommended_daily = BUDGET_DAILY
        recommended_weekly = BUDGET_DAILY * 7

    budget_alert = ""
    if today_cost >= BUDGET_DAILY:
        budget_alert = f"🚨 **BUDGET ALERT**: Today ${today_cost:.4f} exceeds limit ${BUDGET_DAILY:.2f}!"
    elif today_cost >= BUDGET_DAILY * 0.8:
        budget_alert = f"⚠️ **Budget Warning**: ${today_cost:.4f} today (80%+ of ${BUDGET_DAILY:.2f})"

    lines = []
    lines.append(f"# 📊 AI Token Usage Report")
    lines.append(f"Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}\n")

    if budget_alert:
        lines.append(budget_alert + "\n")

    # Compute daily average (this week, excluding today if partial)
    completed_days = [d["cost"] for day_str, d in daily_list[:-1] if d["cost"] > 0]
    daily_avg = sum(completed_days) / len(completed_days) if completed_days else 0

    lines.append("## 💰 Summary")
    lines.append(f"| Period | Cost |")
    lines.append(f"|--------|------|")
    lines.append(f"| Today | ${today_cost:.4f} |")
    lines.append(f"| Daily avg (excl today) | ${daily_avg:.4f} |")
    lines.append(f"| This week ({days}d) | ${week_cost:.4f} |")
    lines.append(f"| Last week ({days}d) | ${last_week_cost:.4f} |")
    lines.append(f"\n**Trend:** {trend}\n")

    lines.append("## 📈 Daily Cost (emoji bar)")
    for day, d in daily_list:
        bar = emoji_bar(d["cost"], max_day_cost, width=12)
        marker = " ← today" if day == today_start.strftime("%Y-%m-%d") else ""
        lines.append(f"`{day}` {bar} ${d['cost']:.4f}{marker}")

    lines.append("")
    lines.append("## 🤖 Agent Rankings (last 7 days)")
    sorted_agents = []
    for agent, stats in agent_totals.items():
        agent_week_cost = sum(
            msg["cost"] for entry in data
            if entry["agent"] == agent
            for msg in entry["messages"]
            if (ts := parse_dt(msg["ts"])) and ts >= week_start
        )
        n_sessions = len([s for s in recent_sessions if s["agent"] == agent])
        if agent_week_cost > 0:
            sorted_agents.append((agent, agent_week_cost, n_sessions))
    sorted_agents.sort(key=lambda x: x[1], reverse=True)

    max_agent_cost = max((c for _, c, _ in sorted_agents), default=1)
    lines.append(f"| Agent | Sessions | Cost | Bar |")
    lines.append(f"|-------|----------|------|-----|")
    for agent, cost, n_sessions in sorted_agents:
        bar = emoji_bar(cost, max_agent_cost, width=8)
        lines.append(f"| {agent} | {n_sessions} | ${cost:.4f} | {bar} |")

    lines.append("")
    lines.append("## 🔥 Top 5 Sessions (last 7 days)")
    for i, s in enumerate(top5, 1):
        ts_str = s["ts"].strftime("%m-%d %H:%M") if s["ts"] else "unknown"
        label = s.get("label", "") or s["session_id"][:8]
        lines.append(f"{i}. **{s['agent']}** `{label[:40]}` — ${s['cost']:.4f} [{ts_str}]")

    lines.append("")
    lines.append("## 💡 Model Optimization Recommendations")
    lines.append("Based on per-session costs for recurring cron jobs:\n")

    # Group recent sessions by label (only labeled/named cron sessions)
    label_costs = defaultdict(list)
    for s in recent_sessions:
        lbl = s.get("label", "")
        if lbl:
            label_costs[lbl].append(s["cost"])

    recs = []
    for label, costs in sorted(label_costs.items(), key=lambda x: -sum(x[1])):
        avg = sum(costs) / len(costs)
        total = sum(costs)
        rec = model_downgrade_recommendation(avg, label)
        recs.append(f"- **{label}**: avg ${avg:.4f}/run × {len(costs)} runs = ${total:.4f} {rec}")

    if recs:
        lines.extend(recs)
    else:
        lines.append("- No labeled cron sessions found in this period.")

    # Identify top cost drivers
    lines.append("")
    lines.append("**Top cost driver this period:**")
    if sorted_agents:
        top_agent = sorted_agents[0]
        pct = (top_agent[1] / week_cost * 100) if week_cost > 0 else 0
        lines.append(f"→ `{top_agent[0]}` agent at ${top_agent[1]:.4f} ({pct:.1f}% of total)")

    # Budget recommendation section
    lines.append("")
    lines.append("## 🎯 Budget Recommendation")
    lines.append(f"Based on {len(week_costs)} week(s) of actual usage:\n")
    lines.append(f"| Metric | Current | Recommended |")
    lines.append(f"|--------|---------|-------------|")
    lines.append(f"| Daily budget | ${BUDGET_DAILY:.2f} | ${recommended_daily:.2f} |")
    lines.append(f"| Weekly budget | ${BUDGET_DAILY * 7:.2f} | ${recommended_weekly:.2f} |")
    lines.append(f"\n_Recommended daily = P75 of active days × 1.5 (floor $2). Weekly = avg weekly × 1.3._")
    if today_cost > recommended_daily * 2:
        lines.append(f"\n⚠️ Today (${today_cost:.2f}) is {today_cost/recommended_daily:.1f}x the recommended daily budget — likely an outlier day.")

    report_text = "\n".join(lines)

    # Save to Obsidian
    if save_obsidian:
        today_str = today_start.strftime("%Y-%m-%d")
        obsidian_path = OBSIDIAN_DIR / f"{today_str}.md"
        OBSIDIAN_DIR.mkdir(parents=True, exist_ok=True)

        # Build compact token section for daily note
        token_section = f"""
## 💰 Token Usage ({today_str})
- Today: ${today_cost:.4f}
- 7-day total: ${week_cost:.4f}
- Trend: {trend}
- Top agent: {sorted_agents[0][0] if sorted_agents else 'N/A'} (${sorted_agents[0][1]:.4f})
"""
        # Append or create
        existing = ""
        if obsidian_path.exists():
            existing = obsidian_path.read_text()

        if "## 💰 Token Usage" in existing:
            # Replace section
            import re
            existing = re.sub(r"\n## 💰 Token Usage.*?(?=\n## |\Z)", token_section, existing, flags=re.DOTALL)
            obsidian_path.write_text(existing)
        else:
            with open(obsidian_path, "a") as f:
                f.write(token_section)

        print(f"[Obsidian] Saved token snapshot to {obsidian_path}", file=sys.stderr)

    return report_text


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    save_obs = "--obsidian" in sys.argv
    report = generate_report(days, save_obsidian=save_obs)
    print(report)
