#!/bin/bash
# OpenClaw DDG Search Tool
# 
# Usage: ddg-search-tool.sh <query> [num_results]
# 
# This script integrates DuckDuckGo search with OpenClaw agents
# No API key required

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DDG_SCRIPT="$SCRIPT_DIR/skills/ddg-search/ddg_search.py"

# Get arguments
QUERY="$1"
NUM_RESULTS="${2:-10}"

# Validate input
if [ -z "$QUERY" ]; then
  echo "Error: Query required"
  echo "Usage: $0 <query> [num_results]"
  exit 1
fi

# Run search and output JSON
python3 "$DDG_SCRIPT" "$QUERY" -n "$NUM_RESULTS" --json
