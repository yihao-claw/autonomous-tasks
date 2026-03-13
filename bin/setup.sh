#!/bin/bash
# setup.sh — Container restart self-healing
# Run this after container restart to restore missing binaries
# Horse 🐴 | 2026-03-13

set -e
BIN=/usr/local/bin
LOG_PREFIX="[setup.sh]"

log() { echo "$LOG_PREFIX $1"; }

# 1. obsidian-cli (notesmd-cli)
if ! command -v obsidian-cli &>/dev/null; then
  log "Installing obsidian-cli..."
  npm install -g notesmd-cli
  log "obsidian-cli installed: $(obsidian-cli --version 2>/dev/null)"
else
  log "obsidian-cli: OK ($(obsidian-cli --version 2>/dev/null))"
fi

# 2. yt-dlp
if ! command -v yt-dlp &>/dev/null; then
  log "Installing yt-dlp..."
  curl -sL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o $BIN/yt-dlp
  chmod +x $BIN/yt-dlp
  log "yt-dlp installed: $(yt-dlp --version)"
else
  log "yt-dlp: OK ($(yt-dlp --version))"
fi

# 3. ffmpeg
if ! command -v ffmpeg &>/dev/null; then
  log "Installing ffmpeg..."
  apt-get install -y ffmpeg -qq 2>/dev/null || \
    apk add ffmpeg --no-progress 2>/dev/null || \
    log "ffmpeg: could not install (unknown OS), manual install required"
else
  log "ffmpeg: OK"
fi

# 4. deno (optional, used by some scripts)
if ! command -v deno &>/dev/null; then
  log "Installing deno..."
  curl -fsSL https://deno.land/install.sh | sh -s -- --no-modify-path 2>/dev/null
  ln -sf /root/.deno/bin/deno $BIN/deno 2>/dev/null || \
    ln -sf /home/node/.deno/bin/deno $BIN/deno 2>/dev/null || true
  log "deno: $(deno --version 2>/dev/null | head -1 || echo 'installed but not in PATH')"
else
  log "deno: OK ($(deno --version 2>/dev/null | head -1))"
fi

log "Setup complete."
