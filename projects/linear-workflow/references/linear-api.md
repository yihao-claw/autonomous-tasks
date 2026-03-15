# Linear GraphQL API Reference

## Authentication

```
Authorization: <LINEAR_API_TOKEN>
Endpoint: https://api.linear.app/graphql
```

Token location (environment-specific — override via SKILL.md or env var):
- Default: `~/.openclaw/secrets/linear-token`

## Common Queries

### List Issues by State

```graphql
{
  issues(filter: { state: { name: { eq: "In Progress" } } }) {
    nodes {
      id identifier title description
      state { name }
      priority priorityLabel
      assignee { name }
      comments { nodes { body createdAt user { name } } }
    }
  }
}
```

### Get Single Issue

```graphql
{
  issue(id: "<ISSUE_ID>") {
    id identifier title description
    state { name }
    priority priorityLabel
    comments { nodes { body createdAt user { name } } }
  }
}
```

### Search Issues by Identifier (e.g. YIH-14)

```graphql
{
  issueSearch(query: "YIH-14") {
    nodes { id identifier title state { name } }
  }
}
```

## Common Mutations

### Create Issue

```graphql
mutation {
  issueCreate(input: {
    teamId: "<TEAM_ID>"
    title: "Issue title"
    description: "Full markdown description"
    priority: 2
    stateId: "<STATE_ID>"
  }) {
    success
    issue { id identifier url }
  }
}
```

### Update Issue (description, state, etc.)

```graphql
mutation {
  issueUpdate(id: "<ISSUE_ID>", input: {
    description: "Updated description"
    stateId: "<STATE_ID>"
  }) {
    success
    issue { id identifier state { name } }
  }
}
```

### Add Comment

```graphql
mutation {
  commentCreate(input: {
    issueId: "<ISSUE_ID>"
    body: "Comment text in markdown"
  }) {
    success
    comment { id body }
  }
}
```

## Priority Values

| Value | Label    |
|-------|----------|
| 0     | No priority |
| 1     | Urgent   |
| 2     | High     |
| 3     | Medium   |
| 4     | Low      |

## Workflow States

Standard Linear states (type in parentheses):

- Backlog (backlog)
- Todo (unstarted)
- In Progress (started)
- In Review (started)
- Done (completed)
- Canceled (canceled)

State IDs are workspace-specific. Query `workflowStates` to get IDs for your workspace.

## Rate Limits

- 1500 requests per hour per API key
- Batch related reads into single queries when possible
- Use `updatedAt` filters for polling
