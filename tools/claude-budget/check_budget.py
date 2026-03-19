#!/usr/bin/env python3
"""
Check Claude usage budget from claudebar JSON.
Exit codes: 0=ok, 1=warning(>70%), 2=critical(>90%)

Usage:
  python3 check_budget.py              # Human-readable
  python3 check_budget.py --json       # JSON output
  python3 check_budget.py --alert-only # Only print if warning/critical
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

USAGE_FILE = Path("/home/node/.openclaw/claude_usage.json")
WARN_THRESHOLD = 70
CRITICAL_THRESHOLD = 90

ICONS = {"five_hour": "⏺", "seven_day": "⬡", "seven_day_sonnet": "✳"}


def load_usage() -> dict | None:
    if not USAGE_FILE.exists():
        return None
    try:
        with open(USAGE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def check():
    data = load_usage()
    if not data:
        print("❌ No usage data found", file=sys.stderr)
        return 2

    updated = data.get("updated_at", "unknown")
    stats = data.get("stats", {})

    max_pct = 0
    lines = []
    for key, info in stats.items():
        pct = info["percent"]
        icon = ICONS.get(key, "•")
        reset = info["resets"]
        status = "🟢" if pct < WARN_THRESHOLD else "🟡" if pct < CRITICAL_THRESHOLD else "🔴"
        lines.append(f"{status} {icon} {info['label']}: {pct}% (resets {reset})")
        max_pct = max(max_pct, pct)

    return max_pct, lines, updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--alert-only", action="store_true")
    args = parser.parse_args()

    result = check()
    if isinstance(result, int):
        sys.exit(result)

    max_pct, lines, updated = result
    level = 0 if max_pct < WARN_THRESHOLD else 1 if max_pct < CRITICAL_THRESHOLD else 2

    if args.json:
        print(json.dumps({"max_percent": max_pct, "level": level, "updated": updated}))
    elif args.alert_only:
        if level > 0:
            header = "⚠️ Claude 用量警告" if level == 1 else "🚨 Claude 用量危急"
            print(header)
            for line in lines:
                print(line)
    else:
        print(f"📊 Claude Budget ({updated[:19]})")
        for line in lines:
            print(line)

    sys.exit(level)


if __name__ == "__main__":
    main()
