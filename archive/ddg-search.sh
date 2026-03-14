#!/bin/bash
# DuckDuckGo Search wrapper for OpenClaw

query="$1"
num_results="${2:-10}"

if [ -z "$query" ]; then
  echo "Usage: ddg-search <query> [num_results]"
  echo "Example: ddg-search 'Claude AI' 5"
  exit 1
fi

python3 /home/node/.openclaw/workspace/skills/ddg-search/ddg_search.py "$query" -n "$num_results" --json
