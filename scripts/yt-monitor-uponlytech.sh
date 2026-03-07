#!/bin/bash
# Monitor @Uponlytech YouTube channel for new videos
# Extracts video IDs from channel page, compares with known list

CHANNEL_URL="https://www.youtube.com/@Uponlytech/videos"
STATE_FILE="/home/node/.openclaw/workspace/memory/uponlytech-known-videos.txt"

# Ensure state file exists
mkdir -p "$(dirname "$STATE_FILE")"
touch "$STATE_FILE"

# Fetch current video IDs
CURRENT=$(curl -s "$CHANNEL_URL" | grep -oP '"videoId":"[^"]*"' | sort -u | sed 's/"videoId":"//;s/"//')

if [ -z "$CURRENT" ]; then
  echo "ERROR: Failed to fetch videos"
  exit 1
fi

# Find new videos
NEW_VIDEOS=""
while IFS= read -r vid; do
  if ! grep -qF "$vid" "$STATE_FILE"; then
    NEW_VIDEOS="$NEW_VIDEOS $vid"
  fi
done <<< "$CURRENT"

# Update state file
echo "$CURRENT" > "$STATE_FILE"

# Output new videos (if any)
NEW_VIDEOS=$(echo "$NEW_VIDEOS" | xargs)
if [ -n "$NEW_VIDEOS" ]; then
  echo "NEW:$NEW_VIDEOS"
else
  echo "NO_NEW"
fi
