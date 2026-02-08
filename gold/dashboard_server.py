"""Gold Tier Dashboard Server - serves HTML dashboard and parses Dashboard.md as JSON API."""

import json
import re
import os
import time
import psutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

DASHBOARD_MD = Path(__file__).parent / "AI_Employee_Vault" / "Dashboard.md"
DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"
PORT = 5050


def get_system_processes():
    """Get system process information for service monitoring."""
    processes = {}

    # Look for known AI Employee processes
    process_names = ['orchestrator', 'gmail_watcher', 'linkedin_watcher', 'facebook_watcher',
                     'approval_watcher', 'email_mcp_server', 'dashboard_server']

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            pinfo = proc.info
            for name in process_names:
                if name in pinfo['name'] or any(name in arg for arg in pinfo['cmdline']):
                    processes[name] = {
                        'pid': pinfo['pid'],
                        'status': pinfo['status'],
                        'uptime_seconds': int(time.time() - pinfo['create_time']),
                        'memory_percent': proc.memory_percent(),
                        'cpu_percent': proc.cpu_percent()
                    }
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return processes


def parse_dashboard_md(text: str) -> dict:
    """Parse Dashboard.md into structured JSON."""
    data = {
        "system_status": {},
        "services": [],
        "plan_stats": {},
        "email_approval_stats": {},
        "recent_activity": [],
        "pending_actions": [],
        "email_processing": {},
        "file_processing": {},
        "quick_stats": {},
        "service_monitoring": {},
    }

    # Add service monitoring information
    data["service_monitoring"] = get_system_processes()

    current_section = None
    for line in text.splitlines():
        line = line.strip()

        # Detect sections
        if line.startswith("## "):
            current_section = line[3:].strip().lower()
            continue

        if not line or line.startswith("---") or line.startswith("# AI Employee"):
            continue

        # Parse key-value lines like "- **Key**: Value"
        kv = re.match(r"^-\s+\*\*(.+?)\*\*:\s*(.+)$", line)
        # Parse plain list items
        plain = re.match(r"^-\s+(.+)$", line) if not kv else None
        # Parse bracketed activity: "- [timestamp] description"
        activity = re.match(r"^-\s+\[(.+?)\]\s+(.+)$", line)

        if current_section == "system status" and kv:
            key = kv.group(1).lower().replace(" ", "_")
            data["system_status"][key] = kv.group(2)

        elif current_section == "services" and kv:
            data["services"].append({"name": kv.group(1), "description": kv.group(2)})

        elif current_section == "plan generation stats" and kv:
            key = kv.group(1).lower().replace(" ", "_")
            data["plan_stats"][key] = kv.group(2)

        elif current_section == "email approval stats" and kv:
            key = kv.group(1).lower().replace(" ", "_")
            data["email_approval_stats"][key] = kv.group(2)

        elif current_section == "recent activity":
            if activity:
                data["recent_activity"].append({"time": activity.group(1), "event": activity.group(2)})
            elif plain:
                data["recent_activity"].append({"time": "", "event": plain.group(1)})

        elif current_section == "pending actions":
            if line not in ("[None]", "None"):
                if plain:
                    data["pending_actions"].append(plain.group(1))

        elif current_section == "email processing summary" and kv:
            key = kv.group(1).lower().replace(" ", "_").replace("(", "").replace(")", "")
            data["email_processing"][key] = kv.group(2)

        elif current_section == "file processing summary" and kv:
            key = kv.group(1).lower().replace(" ", "_")
            data["file_processing"][key] = kv.group(2)

        elif current_section == "quick stats" and kv:
            key = kv.group(1).lower().replace(" ", "_")
            data["quick_stats"][key] = kv.group(2)

    return data


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/dashboard":
            try:
                text = DASHBOARD_MD.read_text(encoding="utf-8")
                data = parse_dashboard_md(text)
                payload = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(payload)
            except FileNotFoundError:
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"Dashboard.md not found"}')
        elif self.path in ("/", "/index.html"):
            content = DASHBOARD_HTML.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"[dashboard] {args[0]}")


if __name__ == "__main__":
    print(f"Gold Dashboard running at http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), DashboardHandler).serve_forever()
