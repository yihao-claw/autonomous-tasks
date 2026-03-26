#!/bin/bash
# System Health Dashboard - Daily Report
# Works without uptime/free/top commands (container-friendly)

set -euo pipefail

DATE=$(date -u '+%Y-%m-%d %H:%M UTC')
HOSTNAME=$(cat /proc/sys/kernel/hostname 2>/dev/null || echo "unknown")

# ─── Uptime ─────────────────────────────────────────────────────────────────
UPTIME_SECS=$(cat /proc/uptime | awk '{print int($1)}')
UPTIME_H=$(( UPTIME_SECS / 3600 ))
UPTIME_M=$(( (UPTIME_SECS % 3600) / 60 ))
UPTIME_STR="${UPTIME_H}h ${UPTIME_M}m"

# ─── Load Average ───────────────────────────────────────────────────────────
LOAD=$(cat /proc/loadavg | awk '{print $1, $2, $3}')

# ─── RAM ────────────────────────────────────────────────────────────────────
MEM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEM_FREE_KB=$(grep MemFree /proc/meminfo | awk '{print $2}')
MEM_AVAIL_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
MEM_USED_KB=$(( MEM_TOTAL_KB - MEM_AVAIL_KB ))
MEM_PCT=$(( MEM_USED_KB * 100 / MEM_TOTAL_KB ))
MEM_TOTAL_MB=$(( MEM_TOTAL_KB / 1024 ))
MEM_USED_MB=$(( MEM_USED_KB / 1024 ))
MEM_AVAIL_MB=$(( MEM_AVAIL_KB / 1024 ))

# ─── Disk ───────────────────────────────────────────────────────────────────
DISK_INFO=$(df -h / | tail -1)
DISK_USED=$(echo "$DISK_INFO" | awk '{print $3}')
DISK_TOTAL=$(echo "$DISK_INFO" | awk '{print $2}')
DISK_AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')
DISK_PCT=$(echo "$DISK_INFO" | awk '{print $5}' | tr -d '%')

# ─── CPU (1s sample from /proc/stat) ────────────────────────────────────────
get_cpu_pct() {
  local line1 line2
  line1=$(grep '^cpu ' /proc/stat)
  sleep 1
  line2=$(grep '^cpu ' /proc/stat)
  python3 -c "
a = list(map(int, '$line1'.split()[1:]))
b = list(map(int, '$line2'.split()[1:]))
da = sum(b) - sum(a)
didle = b[3] - a[3]
if da > 0:
    print(int(100 * (da - didle) / da))
else:
    print(0)
"
}
CPU_PCT=$(get_cpu_pct)

# ─── Docker ─────────────────────────────────────────────────────────────────
if command -v docker &>/dev/null 2>&1; then
  RUNNING=$(docker ps -q 2>/dev/null | wc -l | tr -d ' ')
  TOTAL_C=$(docker ps -aq 2>/dev/null | wc -l | tr -d ' ')
  DOCKER_LINE="🐳 Docker: ${RUNNING}/${TOTAL_C} containers running"
else
  DOCKER_LINE="🐳 Docker: not available"
fi

# ─── Bar Chart ──────────────────────────────────────────────────────────────
make_bar() {
  local pct=${1:-0}
  local filled=$(( pct / 10 ))
  local empty=$(( 10 - filled ))
  local bar=""
  for i in $(seq 1 $filled 2>/dev/null); do bar="${bar}█"; done
  for i in $(seq 1 $empty 2>/dev/null); do bar="${bar}░"; done
  echo "$bar"
}

DISK_BAR=$(make_bar "$DISK_PCT")
MEM_BAR=$(make_bar "$MEM_PCT")
CPU_BAR=$(make_bar "$CPU_PCT")

# ─── Alerts ─────────────────────────────────────────────────────────────────
ALERTS=""
STATUS_EMOJI="✅"

if [ "$DISK_PCT" -gt 80 ]; then
  ALERTS="${ALERTS}\n⚠️ Disk >80%: ${DISK_PCT}%"
  STATUS_EMOJI="🚨"
fi
if [ "$MEM_PCT" -gt 85 ]; then
  ALERTS="${ALERTS}\n⚠️ RAM >85%: ${MEM_PCT}%"
  STATUS_EMOJI="🚨"
fi

# ─── Build Message ──────────────────────────────────────────────────────────
MSG="${STATUS_EMOJI} *系統健康報告*
\`${HOSTNAME}\` — ${DATE}

⏱ Uptime: ${UPTIME_STR}
📊 Load: ${LOAD}

🖥 *CPU*
${CPU_BAR} ${CPU_PCT}%

🧠 *RAM*
${MEM_BAR} ${MEM_PCT}%
Used: ${MEM_USED_MB}MB / ${MEM_TOTAL_MB}MB (${MEM_AVAIL_MB}MB free)

💾 *Disk* (/)
${DISK_BAR} ${DISK_PCT}%
Used: ${DISK_USED} / ${DISK_TOTAL} (${DISK_AVAIL} free)

${DOCKER_LINE}"

if [ -n "$ALERTS" ]; then
  MSG="${MSG}

🚨 *ALERTS*$(echo -e "$ALERTS")"
fi

echo "$MSG"

# ─── Log ────────────────────────────────────────────────────────────────────
LOG_DIR="/home/node/.openclaw/workspace/logs"
mkdir -p "$LOG_DIR"
echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Disk: ${DISK_PCT}%, RAM: ${MEM_PCT}%, CPU: ${CPU_PCT}%, Load: ${LOAD}" >> "$LOG_DIR/system_health.log"
