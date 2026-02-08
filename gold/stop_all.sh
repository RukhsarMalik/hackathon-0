#!/usr/bin/env bash
#
# stop_all.sh - Gracefully stop all AI Employee services
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_DIR=".pids"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[STOP]${NC} $1"; }

# Step 1: Tell watchdog to stop restarting
touch "$PID_DIR/watchdog.stop"
log "Watchdog auto-restart disabled"

# Step 2: Kill watchdog first
if [ -f "$PID_DIR/watchdog.pid" ]; then
    wpid=$(cat "$PID_DIR/watchdog.pid")
    if kill -0 "$wpid" 2>/dev/null; then
        log "Stopping watchdog (PID $wpid)..."
        kill "$wpid" 2>/dev/null || true
    fi
    rm -f "$PID_DIR/watchdog.pid"
fi

# Step 3: Kill all other services
for pidfile in "$PID_DIR"/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service=$(basename "$pidfile" .pid)
        if kill -0 "$pid" 2>/dev/null; then
            log "Stopping $service (PID $pid)..."
            kill "$pid" 2>/dev/null || true
        fi
        rm -f "$pidfile"
    fi
done

# Step 4: Clean up stop file
rm -f "$PID_DIR/watchdog.stop"

log "All services stopped."
