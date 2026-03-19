# SKILL.md — Autonomous Daily Tasks (Vince 🐴)

## Purpose
Vince's daily autonomous task runner. Executed once per day via cron job `7bdad333` at JST 01:00.

---

## Execution Flow

### 1. Load Context
```bash
# Read goals
cat /home/node/.openclaw/workspace/AUTONOMOUS.md

# Read memory
cat /home/node/obsidian-vault/Agents/Vince/MEMORY.md

# Check cron health (look for consecutiveErrors > 0)
openclaw cron list
```

### 2. Task Selection Rules
Pick **1–3 tasks** from AUTONOMOUS.md goals. Prioritize by:
1. **System health issues** (cron errors, broken tools) — always fix first
2. **High-leverage automation** (saves tokens/time daily)
3. **Quick wins** (< 5 min, meaningful output)
4. **Long-term projects** (advance by one concrete step)

Avoid picking tasks that require human decisions or external accounts not yet set up.

### 3. Execute Tasks
- Each task: implement → test → verify output exists
- If a task hits a blocker, note it and skip; don't spin
- Stay under **10 minutes total** — if a task is large, do one concrete sub-step

### 4. Git Commit (if code changed)
```bash
cd /home/node/.openclaw/workspace/projects/autonomous-tasks
git add -A
git commit -m "chore(daily): YYYY-MM-DD task summary"
git push
```

### 5. Write Daily Note
Path: `/home/node/obsidian-vault/Agents/Vince/Daily/YYYY-MM-DD.md`

```markdown
---
date: YYYY-MM-DD
tags:
  - daily
  - agent/horse
agent: Vince
---
# YYYY-MM-DD Vince Daily

## ✅ Tasks Completed
- [task name]: [what was done, output path/result]

## ⏭️ Skipped / Blocked
- [task name]: [reason]

## 💡 Insights
- [any lesson worth remembering]

## 🔜 Next Session
- [suggested next 1-2 tasks]
```

### 6. Update MEMORY.md (if significant)
Path: `/home/node/obsidian-vault/Agents/Vince/MEMORY.md`

Only update when: new decision made, important lesson learned, system architecture changed.

---

## Guardrails

- **Do NOT touch** April cron jobs: `yt-channels-hourly`, `yt-channels-daily`, `daily-world-news`
- **Do NOT edit** `AUTONOMOUS.md` from subagents (human-owned)
- Run `openclaw doctor --non-interactive` before any config changes
- If AUTONOMOUS.md has no goals → write status note and exit cleanly
- Sensitive data (tokens, cookies) → never commit to git

---

## Quality Standards

- Daily note must have at least one completed task entry (or explicit "nothing to do" note)
- Completed tasks must include concrete output (file path, cron ID, script name, etc.)
- No vague entries like "investigated X" — must state what was found/changed

---

## Subagent Usage

For tasks > 10 min or requiring parallel work:
```
sessions_spawn(runtime="subagent", task="...", streamTo="parent")
```
Then yield and receive results.

---

## GitHub

Repo: https://github.com/openyhclaw-dot/autonomous-tasks
Push after any code/script changes.
