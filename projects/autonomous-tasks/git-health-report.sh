#!/usr/bin/env bash
# git-health-report.sh
# Generates a weekly health report for all git repos in workspace/projects
# Sends report to Telegram via OpenClaw

set -euo pipefail

PROJECTS_DIR="/home/node/.openclaw/workspace/projects"
NOW=$(date +%s)
SEVEN_DAYS=$((7 * 24 * 3600))

report=""
warn_count=0
total=0

for repo_dir in "$PROJECTS_DIR"/*/; do
  [ -d "$repo_dir/.git" ] || continue
  name=$(basename "$repo_dir")
  total=$((total + 1))

  issues=()

  # Last commit time
  last_commit_ts=$(git -C "$repo_dir" log -1 --format="%ct" 2>/dev/null || echo 0)
  if [ "$last_commit_ts" -eq 0 ]; then
    last_commit_str="no commits"
    issues+=("⚠️ no commits")
  else
    age=$((NOW - last_commit_ts))
    last_commit_str=$(git -C "$repo_dir" log -1 --format="%cr" 2>/dev/null)
    if [ "$age" -gt "$SEVEN_DAYS" ]; then
      issues+=("🟡 stale (last commit: $last_commit_str)")
    fi
  fi

  # Uncommitted changes
  if ! git -C "$repo_dir" diff --quiet 2>/dev/null || ! git -C "$repo_dir" diff --cached --quiet 2>/dev/null; then
    issues+=("🔴 uncommitted changes")
  fi

  # Untracked files
  untracked=$(git -C "$repo_dir" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
  if [ "$untracked" -gt 0 ]; then
    issues+=("📄 $untracked untracked file(s)")
  fi

  # Unpushed commits
  branch=$(git -C "$repo_dir" branch --show-current 2>/dev/null || echo "")
  if [ -n "$branch" ]; then
    upstream=$(git -C "$repo_dir" rev-parse --abbrev-ref "@{upstream}" 2>/dev/null || echo "")
    if [ -n "$upstream" ]; then
      unpushed=$(git -C "$repo_dir" rev-list "$upstream..HEAD" --count 2>/dev/null || echo 0)
      if [ "$unpushed" -gt 0 ]; then
        issues+=("🔴 $unpushed unpushed commit(s)")
      fi
    else
      issues+=("⚠️ no upstream set")
    fi
  fi

  # Stale branches (>7 days without activity, not main/master)
  stale_branches=$(git -C "$repo_dir" for-each-ref --format='%(refname:short) %(committerdate:unix)' refs/heads/ 2>/dev/null | \
    awk -v now="$NOW" -v cutoff="$SEVEN_DAYS" '$1 !~ /^(main|master)$/ && (now - $2) > cutoff {print $1}' || true)
  if [ -n "$stale_branches" ]; then
    branch_list=$(echo "$stale_branches" | tr '\n' ', ' | sed 's/,$//')
    issues+=("🟡 stale branches: $branch_list")
  fi

  # Disk usage
  disk=$(du -sh "$repo_dir" 2>/dev/null | cut -f1)

  # Build status line
  if [ ${#issues[@]} -eq 0 ]; then
    status="✅"
  else
    status="⚠️"
    warn_count=$((warn_count + 1))
  fi

  report+="$status *$name* (${disk})\n"
  if [ "$last_commit_ts" -ne 0 ]; then
    report+="   Last commit: $last_commit_str\n"
  fi
  for issue in "${issues[@]}"; do
    report+="   $issue\n"
  done
  report+="\n"
done

summary="🐴 *Git Repo Health Report*\n$(date -u '+%Y-%m-%d %H:%M UTC')\n$total repos scanned, $warn_count with issues\n\n$report"

echo -e "$summary"
