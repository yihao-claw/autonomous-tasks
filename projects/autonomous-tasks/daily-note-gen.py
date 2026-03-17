#!/usr/bin/env python3
"""
Daily Note Generator — Layer 1
Generates Obsidian daily note with:
- Linear Done issues (today)
- Agent activity summaries (Horse, Bird, Dan)
- Then sends a summary to Telegram

Usage: python3 daily-note-gen.py [--date YYYY-MM-DD]
"""

import os
import sys
import json
import datetime
import urllib.request
import re

# Config
VAULT_PATH = "/home/node/obsidian-vault"
LINEAR_TOKEN_PATH = "/home/node/.openclaw/secrets/linear-token"
DAILY_NOTE_PATH = os.path.join(VAULT_PATH, "Agents", "Daily")
AGENT_DAILY = {
    "Horse": os.path.join(VAULT_PATH, "Agents", "Horse", "Daily"),
    "Bird": os.path.join(VAULT_PATH, "Agents", "Bird", "Daily"),
    "Dan": os.path.join(VAULT_PATH, "Agents", "Dan", "Daily"),
}

def get_date(date_str=None):
    if date_str:
        return datetime.date.fromisoformat(date_str)
    return datetime.date.today()

def linear_query(query):
    token = open(LINEAR_TOKEN_PATH).read().strip()
    data = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql", data=data,
        headers={"Content-Type": "application/json", "Authorization": token}
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())

def get_done_issues(date):
    start = f"{date}T00:00:00Z"
    end = f"{date}T23:59:59Z"
    query = f'''{{
  issues(filter: {{ state: {{ type: {{ eq: "completed" }} }}, completedAt: {{ gte: "{start}", lte: "{end}" }} }}) {{
    nodes {{ identifier title completedAt }}
  }}
}}'''
    result = linear_query(query)
    return result.get("data", {}).get("issues", {}).get("nodes", [])

def read_agent_daily(agent, date):
    """Read agent's daily log file for given date."""
    path = os.path.join(AGENT_DAILY[agent], f"{date}.md")
    if not os.path.exists(path):
        return None
    content = open(path).read()
    return content

def extract_agent_summary(agent, content):
    """Extract key highlights from agent daily log."""
    if not content:
        return f"- 無記錄"
    
    lines = content.split('\n')
    highlights = []
    
    if agent == "Bird":
        # Extract task names and statuses
        for line in lines:
            if line.startswith('## 任務：') or line.startswith('**狀態：'):
                highlights.append(line.replace('## ', '').replace('**', ''))
            elif '發現新影片：' in line and '無' not in line:
                highlights.append('  ' + line.strip())
            elif '推送至 Telegram' in line or 'Telegram 推送' in line and '✅' in line:
                pass  # included via status
        # Deduplicate and limit
        seen = set()
        unique = []
        for h in highlights:
            if h not in seen:
                seen.add(h)
                unique.append(h)
        return '\n'.join(f"- {h}" for h in unique[:10]) if unique else "- 無重要動態"
    
    elif agent == "Horse":
        # Extract completed tasks
        in_completed = False
        for line in lines:
            if '## ✅' in line or '### ✅' in line:
                highlights.append(line.replace('## ', '').replace('### ', '').strip())
                in_completed = True
            elif line.startswith('## ') and in_completed:
                in_completed = False
            elif in_completed and line.startswith('- '):
                highlights.append('  ' + line.strip())
        return '\n'.join(f"- {h}" for h in highlights[:10]) if highlights else "- 無重要動態"
    
    elif agent == "Dan":
        # Extract 完成事項 section
        in_section = False
        for line in lines:
            if '## 完成事項' in line:
                in_section = True
            elif line.startswith('## ') and in_section:
                break
            elif in_section and line.startswith('- '):
                highlights.append(line.strip())
        return '\n'.join(highlights[:10]) if highlights else "- 無記錄"
    
    return "- 無記錄"

def generate_daily_note(date):
    date_str = str(date)
    
    # Get Linear done issues
    done_issues = get_done_issues(date)
    
    # Get agent summaries
    agent_summaries = {}
    for agent in ["Horse", "Bird", "Dan"]:
        content = read_agent_daily(agent, date_str)
        agent_summaries[agent] = extract_agent_summary(agent, content)
    
    # Format done issues
    if done_issues:
        issues_text = '\n'.join(
            f"- [{i['identifier']}] {i['title']}"
            for i in done_issues
        )
    else:
        issues_text = "- 無"
    
    note = f"""---
date: {date_str}
tags: [daily, auto-generated]
---

# {date_str} Daily Note

## ✅ 今日完成任務（Linear）

{issues_text}

## 🤖 Agent 活動摘要

### 🐴 Horse
{agent_summaries['Horse']}

### 🐦 Bird
{agent_summaries['Bird']}

### 🦁 Dan
{agent_summaries['Dan']}

---
*自動生成 by Horse daily-note-gen.py*
"""
    return note, done_issues, agent_summaries

def save_note(date, note):
    os.makedirs(DAILY_NOTE_PATH, exist_ok=True)
    path = os.path.join(DAILY_NOTE_PATH, f"{date}.md")
    with open(path, 'w') as f:
        f.write(note)
    return path

def build_telegram_summary(date, done_issues, agent_summaries):
    """Build a concise Telegram summary."""
    date_str = str(date)
    
    issues_text = '\n'.join(f"• [{i['identifier']}] {i['title']}" for i in done_issues) if done_issues else "• 無"
    
    # Simple one-liner per agent
    horse_lines = [l.strip('- ').strip() for l in agent_summaries['Horse'].split('\n') if l.strip().startswith('-')]
    bird_lines = [l.strip('- ').strip() for l in agent_summaries['Bird'].split('\n') if l.strip().startswith('-')]
    dan_lines = [l.strip('- ').strip() for l in agent_summaries['Dan'].split('\n') if l.strip().startswith('-')]
    
    horse_summary = horse_lines[0] if horse_lines else "無重要動態"
    bird_summary = bird_lines[0] if bird_lines else "無重要動態"
    dan_summary = dan_lines[0] if dan_lines else "無記錄"
    
    msg = f"""📅 **{date_str} Daily Note**

✅ **今日完成任務**
{issues_text}

🤖 **Agent 活動**
🐴 Horse: {horse_summary}
🐦 Bird: {bird_summary}
🦁 Dan: {dan_summary}

_Daily Note 已存入 Obsidian Vault_"""
    return msg

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--print-summary', action='store_true', help='Print Telegram summary to stdout')
    args = parser.parse_args()
    
    date = get_date(args.date)
    print(f"Generating daily note for {date}...")
    
    note, done_issues, agent_summaries = generate_daily_note(date)
    path = save_note(date, note)
    print(f"✅ Saved: {path}")
    
    summary = build_telegram_summary(date, done_issues, agent_summaries)
    
    if args.print_summary:
        print("\n--- TELEGRAM SUMMARY ---")
        print(summary)
    else:
        print("\n--- TELEGRAM SUMMARY ---")
        print(summary)
