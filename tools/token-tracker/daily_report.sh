#!/bin/bash
# Daily token usage report — run via cron
# Generates report and sends to Telegram if notable

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPORT=$(python3 "$SCRIPT_DIR/analyze.py" 7)

echo "$REPORT"
