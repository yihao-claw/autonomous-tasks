#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Opportunity Radar — Full Scan ==="
echo "Started at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

run_script() {
    local name="$1"
    echo "▶ Running $name..."
    if python3 "scripts/$name" 2>&1; then
        echo "✅ $name completed"
    else
        echo "⚠️ $name failed (continuing...)"
    fi
    echo ""
}

# Phase 1: Scanners (can run independently)
run_script "scan_ptt.py"
run_script "scan_dcard.py"
run_script "scan_reddit.py"
run_script "scan_appstore.py"

# Phase 2: Scoring
run_script "scorer.py"

# Phase 3: Report
run_script "report.py"

echo "=== Done at: $(date -u '+%Y-%m-%d %H:%M:%S UTC') ==="
