#!/bin/bash

# Memory search wrapper for OpenClaw
# Usage: memory_search.sh "query" [maxTokens]

cd /home/node/.openclaw/workspace
node scripts/search_memory_simple.js "$1" "${2:-500}"
