#!/bin/bash
# setup.sh — Container restart self-healing
# Run this after container restart to restore missing binaries
# Horse 🐴 | 2026-03-13

set +e  # continue even if individual installs fail
BIN=/usr/local/bin
LOG_PREFIX="[setup.sh]"

log() { echo "$LOG_PREFIX $1"; }

# 1. obsidian-cli (notesmd-cli binary in workspace bin/)
OBSIDIAN_BIN=/home/node/.openclaw/workspace/bin/obsidian-cli
if ! command -v obsidian-cli &>/dev/null; then
  log "Symlinking obsidian-cli from workspace bin..."
  ln -sf "$OBSIDIAN_BIN" /usr/local/bin/obsidian-cli
  log "obsidian-cli installed: $(/usr/local/bin/obsidian-cli --version 2>/dev/null)"
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
  if command -v apt-get &>/dev/null; then
    apt-get install -y ffmpeg -qq 2>/dev/null && log "ffmpeg installed via apt" || {
      apt-get update -qq 2>/dev/null
      apt-get install -y ffmpeg -qq 2>/dev/null && log "ffmpeg installed via apt (after update)" || log "ffmpeg: apt install failed"
    }
  elif command -v apk &>/dev/null; then
    apk add ffmpeg --no-progress 2>/dev/null && log "ffmpeg installed via apk" || log "ffmpeg: apk install failed"
  else
    log "ffmpeg: could not install (unknown package manager)"
  fi
else
  log "ffmpeg: OK ($(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f1-3))"
fi

# 4. deno (optional, used by some scripts)
DENO_BIN=${HOME}/.deno/bin/deno  # installs to $HOME/.deno (varies by user)
if ! command -v deno &>/dev/null && [ ! -f "$DENO_BIN" ]; then
  log "Installing deno (requires unzip)..."
  command -v unzip &>/dev/null || apt-get install -y unzip -qq 2>/dev/null
  curl -fsSL https://deno.land/install.sh | sh 2>/dev/null
  [ -f "$DENO_BIN" ] && ln -sf "$DENO_BIN" /usr/local/bin/deno && log "deno: $($DENO_BIN --version 2>/dev/null | head -1)" || log "deno: install failed"
elif [ -f "$DENO_BIN" ] && ! command -v deno &>/dev/null; then
  ln -sf "$DENO_BIN" /usr/local/bin/deno
  log "deno: symlinked — $($DENO_BIN --version 2>/dev/null | head -1)"
else
  log "deno: OK ($(deno --version 2>/dev/null | head -1))"
fi

# 5. Python packages
REQUIRED_PKGS="pandas yfinance requests bs4 feedparser httpx numpy"
MISSING=""
for pkg in $REQUIRED_PKGS; do
  # bs4 is imported as 'bs4', feedparser as 'feedparser', etc.
  python3 -c "import $pkg" 2>/dev/null || MISSING="$MISSING $pkg"
done
if [ -n "$MISSING" ]; then
  log "Installing missing Python packages:$MISSING..."
  # beautifulsoup4 is the installable name for bs4
  INSTALL_NAMES=$(echo "$MISSING" | sed 's/bs4/beautifulsoup4/g')
  pip install $INSTALL_NAMES -q 2>/dev/null && log "Installed:$MISSING" || log "WARNING: some packages may have failed"
else
  log "Python packages: OK (pandas, yfinance, requests, bs4, feedparser, httpx, numpy)"
fi

# 6. age (used by backup encryption)
if ! command -v age &>/dev/null; then
  log "Installing age..."
  AGE_VERSION="v1.3.1"
  AGE_URL="https://github.com/FiloSottile/age/releases/download/${AGE_VERSION}/age-${AGE_VERSION}-linux-arm64.tar.gz"
  TMP_DIR=$(mktemp -d)
  curl -sL "$AGE_URL" -o "$TMP_DIR/age.tar.gz" && \
    tar -xzf "$TMP_DIR/age.tar.gz" -C "$TMP_DIR" && \
    cp "$TMP_DIR/age/age" /usr/local/bin/age && \
    chmod +x /usr/local/bin/age && \
    log "age installed: $(age --version)" || log "age: install failed"
  rm -rf "$TMP_DIR"
else
  log "age: OK ($(age --version 2>/dev/null))"
fi

# 7. jq (used by linear scripts)
if ! command -v jq &>/dev/null; then
  log "Installing jq..."
  apt-get install -y jq -qq 2>/dev/null && log "jq installed" || log "jq: install failed"
else
  log "jq: OK ($(jq --version))"
fi

log "Setup complete."
