---
name: linear-workflow
description: >
  Manage tasks through Linear with a structured lifecycle workflow.
  Use when the agent needs to: create Linear issues, update issue status,
  add descriptions/DOD, comment on issues, check for replies, or follow
  a plan→execute→report workflow on Linear. Also use when asked to
  "check Linear", "update the issue", "what's in backlog", or any
  task management query involving Linear.
---

# Linear Workflow

Structured task lifecycle management via Linear GraphQL API.

## Setup

- **API Token**: Store at `~/.openclaw/secrets/linear-token` (or set `LINEAR_API_TOKEN` env var)
- **API Reference**: See [references/linear-api.md](references/linear-api.md) for queries, mutations, and rate limits

## API Access

All Linear operations use the GraphQL API at `https://api.linear.app/graphql`:

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $(cat ~/.openclaw/secrets/linear-token)" \
  -d '{"query":"<GRAPHQL_QUERY>"}'
```

Before first use, query `teams` and `workflowStates` to get workspace-specific IDs. Cache these — they rarely change.

## Issue Lifecycle

Every task follows this lifecycle. Each phase requires updating the Linear issue.

### 1. Create (Backlog/Todo)

Create issue with:
- **Title**: Clear, actionable (e.g. "Set up daily X monitoring")
- **Description**: Background, goal, approach outline
- **DOD (Definition of Done)**: Checklist of verifiable completion criteria in the description

Description template:

```markdown
## Background
[Why this task exists]

## Goal
[What success looks like]

## Approach
- [ ] Step 1
- [ ] Step 2

## DOD (Definition of Done)
- [ ] Criterion 1 (verifiable)
- [ ] Criterion 2 (verifiable)

## Risks / Dependencies
- [Any blockers or external dependencies]
```

### 2. Plan (before starting)

Update the description with:
- Detailed execution steps
- Expected outputs (file paths, cron IDs, etc.)
- Risks and dependencies

### 3. Execute (In Progress)

- Move issue to `In Progress`
- Work on the task
- Add **comments** for progress updates, questions, or blockers

### 4. Complete (Done)

- Move issue to `Done`
- Append an **Execution Results** section to the description:

```markdown
## Execution Results
- **What was done**: [summary]
- **Outputs**: [file paths, cron IDs, URLs]
- **Issues encountered**: [problems and solutions]
- **Remaining items**: [if any]
```

## Daily Check-in Routine

When running daily/periodic tasks, include this routine:

1. **Check In Progress issues** — query issues with state "In Progress"
2. **Read comments** — check if the human left replies or decisions
3. **Act on feedback** — implement requested changes, reply with updates
4. **Check Backlog/Todo** — pick next tasks if capacity allows

```graphql
{
  issues(filter: { state: { type: { in: ["started"] } } }) {
    nodes {
      id identifier title
      comments(last: 5) { nodes { body createdAt user { name } } }
    }
  }
}
```

## Rules

- Every task, regardless of size, must have a Linear issue
- Never change status without updating the description
- Description must be clear enough for anyone to understand what happened by reading Linear alone
- Use comments for discussion; use description for the canonical record
- DOD is mandatory — no issue without verifiable completion criteria
