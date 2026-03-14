#!/bin/bash
# Linear API helper script
# Usage: linear.sh <action> [args...]
# Actions: list, create, update, search, labels, states

set -euo pipefail

TOKEN=$(cat ~/.openclaw/secrets/linear-token)
API="https://api.linear.app/graphql"
TEAM_ID="352699df-f087-4db3-b3be-c3b6cb4c3519"

gql() {
  curl -s -X POST "$API" \
    -H "Content-Type: application/json" \
    -H "Authorization: $TOKEN" \
    -d "{\"query\":\"$1\"}"
}

case "${1:-help}" in
  list)
    # List issues, optional filter: all|todo|done|inprogress
    FILTER="${2:-all}"
    case "$FILTER" in
      todo) STATE_FILTER=", filter: { state: { type: { eq: \\\"unstarted\\\" } } }" ;;
      done) STATE_FILTER=", filter: { state: { type: { eq: \\\"completed\\\" } } }" ;;
      inprogress) STATE_FILTER=", filter: { state: { type: { eq: \\\"started\\\" } } }" ;;
      backlog) STATE_FILTER=", filter: { state: { type: { eq: \\\"backlog\\\" } } }" ;;
      *) STATE_FILTER="" ;;
    esac
    gql "{ team(id: \\\"$TEAM_ID\\\") { issues(first: 50 $STATE_FILTER) { nodes { identifier title priority state { name } labels { nodes { name } } } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for i in d['data']['team']['issues']['nodes']:
    labels=','.join(l['name'] for l in i['labels']['nodes'])
    p=['None','Urgent','High','Medium','Low'][i['priority']]
    print(f\"{i['identifier']} [{i['state']['name']}] ({p}) [{labels}] {i['title']}\")
"
    ;;

  create)
    # create "title" "description" priority(1-4) "labelName"
    TITLE="${2:?title required}"
    DESC="${3:-}"
    PRI="${4:-3}"
    LABEL="${5:-}"
    if [ -n "$LABEL" ]; then
      # Look up label id
      LID=$(gql "{ team(id: \\\"$TEAM_ID\\\") { labels(filter: { name: { eq: \\\"$LABEL\\\" } }) { nodes { id } } } }" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['team']['labels']['nodes'][0]['id'])")
      LABEL_ARG=", labelIds: [\\\"$LID\\\"]"
    else
      LABEL_ARG=""
    fi
    gql "mutation { issueCreate(input: { title: \\\"$TITLE\\\", description: \\\"$DESC\\\", teamId: \\\"$TEAM_ID\\\", priority: $PRI $LABEL_ARG }) { success issue { identifier title } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
i=d['data']['issueCreate']['issue']
print(f\"Created {i['identifier']}: {i['title']}\")
"
    ;;

  update)
    # update YIH-10 stateId|priority|title value
    ID="${2:?identifier required}"
    FIELD="${3:?field required}"
    VALUE="${4:?value required}"
    # Resolve issue id from identifier
    ISSUE_ID=$(gql "{ issue(id: \\\"$ID\\\") { id } }" 2>/dev/null | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['issue']['id'])" 2>/dev/null || echo "")
    if [ -z "$ISSUE_ID" ]; then
      # Try searching by identifier
      ISSUE_ID=$(gql "{ issues(filter: { team: { id: { eq: \\\"$TEAM_ID\\\" } } }) { nodes { id identifier } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for i in d['data']['issues']['nodes']:
    if i['identifier']=='$ID':
        print(i['id']); break
")
    fi
    case "$FIELD" in
      state)
        # Resolve state name to id
        SID=$(gql "{ team(id: \\\"$TEAM_ID\\\") { states { nodes { id name } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d['data']['team']['states']['nodes']:
    if s['name'].lower()=='${VALUE}'.lower():
        print(s['id']); break
")
        gql "mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { stateId: \\\"$SID\\\" }) { success issue { identifier state { name } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
i=d['data']['issueUpdate']['issue']
print(f\"Updated {i['identifier']} → {i['state']['name']}\")
"
        ;;
      priority)
        gql "mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { priority: $VALUE }) { success issue { identifier priority } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
i=d['data']['issueUpdate']['issue']
p=['None','Urgent','High','Medium','Low'][i['priority']]
print(f\"Updated {i['identifier']} priority → {p}\")
"
        ;;
      description|desc)
        # Escape the description for JSON
        ESCAPED=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip())[1:-1])" <<< "$VALUE")
        gql "mutation { issueUpdate(id: \\\"$ISSUE_ID\\\", input: { description: \\\"$ESCAPED\\\" }) { success issue { identifier title } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
i=d['data']['issueUpdate']['issue']
print(f\"Updated {i['identifier']} description\")
"
        ;;
      *)
        echo "Unknown field: $FIELD (use: state, priority, description)"
        exit 1
        ;;
    esac
    ;;

  search)
    QUERY="${2:?query required}"
    gql "{ searchIssues(term: \\\"$QUERY\\\", first: 10) { nodes { identifier title state { name } labels { nodes { name } } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for i in d['data']['searchIssues']['nodes']:
    labels=','.join(l['name'] for l in i['labels']['nodes'])
    print(f\"{i['identifier']} [{i['state']['name']}] [{labels}] {i['title']}\")
"
    ;;

  labels)
    gql "{ team(id: \\\"$TEAM_ID\\\") { labels { nodes { id name } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for l in d['data']['team']['labels']['nodes']:
    print(f\"{l['id']} {l['name']}\")
"
    ;;

  states)
    gql "{ team(id: \\\"$TEAM_ID\\\") { states { nodes { id name type } } } }" | python3 -c "
import json,sys
d=json.load(sys.stdin)
for s in d['data']['team']['states']['nodes']:
    print(f\"{s['id']} {s['name']} ({s['type']})\")
"
    ;;

  *)
    echo "Usage: linear.sh <action> [args...]"
    echo "Actions:"
    echo "  list [all|todo|done|inprogress|backlog]  - List issues"
    echo "  create \"title\" \"desc\" priority \"label\"    - Create issue (priority: 1=Urgent 2=High 3=Medium 4=Low)"
    echo "  update YIH-10 state \"Done\"                - Update issue state"
    echo "  update YIH-10 priority 2                  - Update issue priority"
    echo "  search \"query\"                            - Search issues"
    echo "  labels                                    - List labels"
    echo "  states                                    - List workflow states"
    ;;
esac
