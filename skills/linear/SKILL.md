---
name: linear
description: Manage Linear project issues — create, list, update, search tasks. Use when asked to create issues, update task status, check project progress, mark tasks done, or manage the Linear board. Also use after completing any autonomous task to update its corresponding Linear issue status.
---

# Linear Task Management

## Quick Start

Use `scripts/linear.sh` for all Linear operations:

```bash
SKILL_DIR="skills/linear"

# List all issues
bash $SKILL_DIR/scripts/linear.sh list

# List by status: todo | done | inprogress | backlog
bash $SKILL_DIR/scripts/linear.sh list todo

# Create issue (priority: 1=Urgent 2=High 3=Medium 4=Low)
bash $SKILL_DIR/scripts/linear.sh create "Title" "Description" 2 "Vince"

# Update issue state (states: Todo, In Progress, In Review, Done, Canceled, Duplicate)
bash $SKILL_DIR/scripts/linear.sh update YIH-10 state "Done"
bash $SKILL_DIR/scripts/linear.sh update YIH-10 state "In Progress"

# Update priority
bash $SKILL_DIR/scripts/linear.sh update YIH-10 priority 1

# Search
bash $SKILL_DIR/scripts/linear.sh search "token"

# View comments on an issue
bash $SKILL_DIR/scripts/linear.sh comments YIH-10

# Add a comment to an issue
bash $SKILL_DIR/scripts/linear.sh add-comment YIH-10 "comment body"

# List labels and states
bash $SKILL_DIR/scripts/linear.sh labels
bash $SKILL_DIR/scripts/linear.sh states
```

## Labels

- **Vince** — Engineering/autonomous tasks agent
- **Dan** — Main assistant agent
- **April** — News/information agent

## Workflow

After completing a task that has a Linear issue:
1. Find the issue: `bash $SKILL_DIR/scripts/linear.sh search "task keywords"`
2. Mark done: `bash $SKILL_DIR/scripts/linear.sh update YIH-XX state "Done"`

When starting work on a task:
1. Mark in progress: `bash $SKILL_DIR/scripts/linear.sh update YIH-XX state "In Progress"`

## Config

- API token: `~/.openclaw/secrets/linear-token`
- Team ID: `352699df-f087-4db3-b3be-c3b6cb4c3519` (hardcoded in script)
- Organization: yihaowang
