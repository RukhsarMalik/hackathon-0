#!/usr/bin/env bash
#
# start_all.sh - Launch all AI Employee services with graceful shutdown
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PID_DIR=".pids"
VAULT_DIR="AI_Employee_Vault"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[START]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
err() { echo -e "${RED}[ERROR]${NC} $1"; }

# --- Prerequisite Checks ---

log "Checking prerequisites..."

# Check Python
if ! command -v python3 &>/dev/null; then
    err "python3 not found. Please install Python 3.13+"
    exit 1
fi
log "Python3: $(python3 --version)"

# Check Claude Code CLI
if ! command -v claude &>/dev/null; then
    warn "Claude Code CLI not found. Orchestrator will not be able to process tasks."
fi

# Check vault directory
if [ ! -d "$VAULT_DIR" ]; then
    err "Vault directory not found: $VAULT_DIR"
    exit 1
fi
log "Vault: $VAULT_DIR"

# --- Setup ---

mkdir -p "$PID_DIR"
mkdir -p "$VAULT_DIR/Logs"
mkdir -p "$VAULT_DIR/Pending_Approval"
mkdir -p "$VAULT_DIR/Done"

# --- Cleanup Function ---

cleanup() {
    echo ""
    log "Shutting down all services..."

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

    log "All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- Start Background Services ---

log "Starting background services..."

# Gmail Watcher
if [ -f "gmail_watcher.py" ]; then
    python3 gmail_watcher.py &
    echo $! > "$PID_DIR/gmail.pid"
    log "Gmail Watcher started (PID $!)"
else
    warn "gmail_watcher.py not found, skipping"
fi

# File System Watcher
if [ -f "filesystem_watcher.py" ]; then
    python3 filesystem_watcher.py &
    echo $! > "$PID_DIR/filesystem.pid"
    log "File System Watcher started (PID $!)"
else
    warn "filesystem_watcher.py not found, skipping"
fi

# LinkedIn Watcher
if [ -f "linkedin_watcher.py" ]; then
    python3 linkedin_watcher.py &
    echo $! > "$PID_DIR/linkedin.pid"
    log "LinkedIn Watcher started (PID $!)"
else
    warn "linkedin_watcher.py not found, skipping"
fi

# Approval Watcher
if [ -f "approval_watcher.py" ]; then
    python3 approval_watcher.py &
    echo $! > "$PID_DIR/approval.pid"
    log "Approval Watcher started (PID $!)"
else
    warn "approval_watcher.py not found, skipping"
fi

# Email MCP Server
if [ -f "email_mcp_server.py" ]; then
    python3 email_mcp_server.py &
    echo $! > "$PID_DIR/mcp_email.pid"
    log "Email MCP Server started (PID $!)"
else
    warn "email_mcp_server.py not found, skipping"
fi

sleep 1

# --- Start Orchestrator (Foreground) ---

log "Starting Orchestrator (foreground)..."
log "Press Ctrl+C to stop all services"
echo ""

python3 orchestrator.py &
ORCH_PID=$!
echo $ORCH_PID > "$PID_DIR/orchestrator.pid"

# Wait for orchestrator to exit
wait $ORCH_PID 2>/dev/null || true

cleanup
