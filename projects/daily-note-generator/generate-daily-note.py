#!/usr/bin/env python3
"""
Daily Note Generator for Obsidian vault.
Collects activity from all agents and creates a unified daily note.
Also sends a Telegram summary.
"""

import os
import json
import datetime
import urllib.request

TODAY = datetime.datetime.utcnow().strftime("%Y-%m-%d")
VAULT = "/home/node/obsidian-vault"
DAILY_DIR = f"{VAULT}/Daily"
AGENTS_DIR = f"{VAULT}/Agents"

os.makedirs(DAILY_DIR, exist_ok=True)

OUTPUT_FILE = f"{DAILY_DIR}/{TODAY}.md"

def fetch_linear_done_today():
    token = open(os.path.expanduser("~/.openclaw/secrets/linear-token")).read().strip()
    query = json.dumps({"query": f"""{{
      issues(filter: {{
        state: {{ type: {{ eq: "completed" }} }},
        updatedAt: {{ gte: "{TODAY}T00:00:00Z" }}
      }}) {{
        nodes {{ identifier title }}
      }}
    }}"""})
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=query.encode(),
        headers={"Content-Type": "application/json", "Authorization": token}
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    return data.get("data", {}).get("issues", {}).get("nodes", [])

def get_agent_daily(agent_name):
    daily_path = f"{AGENTS_DIR}/{agent_name}/Daily/{TODAY}.md"
    if not os.path.exists(daily_path):
        return None
    return open(daily_path).read()

def extract_key_lines(content, max_lines=50):
    """Extract content after frontmatter, up to max_lines."""
    lines = content.split("\n")
    start = 0
    if lines and lines[0].strip() == "---":
        for i, l in enumerate(lines[1:], 1):
            if l.strip() == "---":
                start = i + 1
                break
    return "\n".join(lines[start:start + max_lines])

def build_note():
    now_str = datetime.datetime.utcnow().strftime("%H:%M UTC")

    lines = [
        "---",
        f"date: {TODAY}",
        "tags: [daily, auto-generated]",
        "---",
        "",
        f"# {TODAY} Daily Note",
        "",
        f"_自動生成於 {now_str}_",
        "",
    ]

    # Linear Done today
    done_issues = fetch_linear_done_today()
    lines.append("## ✅ 今日完成任務（Linear）")
    if done_issues:
        for issue in done_issues:
            lines.append(f"- [{issue['identifier']}] {issue['title']}")
    else:
        lines.append("- 無")
    lines.append("")

    # Agent activity
    agents = ["Horse", "Bird", "Dan"]
    agent_summaries = {}

    lines.append("## 🤖 Agent 活動")
    lines.append("")

    for agent in agents:
        content = get_agent_daily(agent)
        agent_summaries[agent] = content
        lines.append(f"### {agent}")
        if content:
            lines.append(extract_key_lines(content))
        else:
            lines.append("_無今日日誌_")
        lines.append("")

    return "\n".join(lines), done_issues, agent_summaries

def send_telegram_summary(done_issues, agent_summaries):
    config_file = os.path.expanduser("~/.openclaw/config.json")
    if not os.path.exists(config_file):
        print("No config.json, skipping Telegram")
        return

    config = json.loads(open(config_file).read())
    plugins = config.get("plugins", [])
    chat_id = None
    bot_token = None

    for plugin in plugins:
        if plugin.get("type") == "telegram":
            bot_token_path = plugin.get("botTokenFile") or plugin.get("tokenFile")
            chat_id = plugin.get("chatId") or plugin.get("chat_id")
            if bot_token_path:
                bot_token = open(os.path.expanduser(bot_token_path)).read().strip()
            break

    if not chat_id or not bot_token:
        print("Missing Telegram config")
        return

    msg_lines = [
        f"📓 *{TODAY} 每日總結*",
        "",
        "*✅ 今日完成任務*",
    ]
    if done_issues:
        for issue in done_issues:
            msg_lines.append(f"• [{issue['identifier']}] {issue['title']}")
    else:
        msg_lines.append("• 無")

    msg_lines.append("")
    msg_lines.append("*🤖 Agent 活動*")
    for agent, content in agent_summaries.items():
        status = "✅ 有記錄" if content else "💤 無日誌"
        msg_lines.append(f"• {agent}: {status}")

    text = "\n".join(msg_lines)

    payload = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as r:
            result = json.loads(r.read())
            print(f"Telegram sent: message_id={result.get('result', {}).get('message_id')}")
    except Exception as e:
        print(f"Telegram send failed: {e}")

# --- Main ---
note_content, done_issues, agent_summaries = build_note()

with open(OUTPUT_FILE, "w") as f:
    f.write(note_content)
print(f"Written: {OUTPUT_FILE}")

send_telegram_summary(done_issues, agent_summaries)
