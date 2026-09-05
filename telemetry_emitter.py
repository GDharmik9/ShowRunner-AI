#!/usr/bin/env python3
"""
telemetry_emitter.py
Autonomous Render Farm Telemetry Emitter and Crash Simulator

Simulates a 6-node VFX rendering cluster running Blender and Unreal Engine workloads.
Exposes Prometheus metrics, pushes logs to Grafana Cloud Loki using Basic Auth,
and provides both an interactive CLI and HTTP endpoints for fault injection.
"""

import argparse
import base64
import http.server
import json
import os
import random
import sys
import threading
import time
import urllib.request
from typing import Dict, Any, List

# --- COLOR DEFINITIONS ---
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"

# --- DEFAULT CONFIGURATION (From Environment or Defaults) ---
DEFAULT_PROM_PORT = int(os.getenv("PORT", "8000"))
DEFAULT_LOKI_URL = os.getenv("LOKI_PUSH_URL", "https://logs-prod-028.grafana.net/loki/api/v1/push")
LOKI_USER_ID = os.getenv("LOKI_USER_ID", "1777022")
GRAFANA_TOKEN = os.getenv("GRAFANA_SERVICE_ACCOUNT_TOKEN", "")
DEFAULT_TICK_INTERVAL = 2.0


class VFXClusterSimulator:
    def __init__(self, tick_interval: float, loki_url: str, loki_user: str, loki_token: str):
        self.tick_interval = tick_interval
        self.loki_url = loki_url
        self.loki_user = loki_user
        self.loki_token = loki_token
        self.running = True
        self.lock = threading.Lock()

        # Build Basic Auth header if credentials exist
        self.auth_header = None
        if self.loki_user and self.loki_token:
            auth_str = f"{self.loki_user}:{self.loki_token}"
            b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
            self.auth_header = f"Basic {b64_auth}"

        # Initialize 6 virtualized GPU render nodes
        self.nodes: Dict[str, Dict[str, Any]] = {
            "node-01": {"id": "node-01", "engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "vram_total_bytes": 12 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_OPENING_001", "frame": 1},
            "node-02": {"id": "node-02", "engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "vram_total_bytes": 12 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_OPENING_002", "frame": 45},
            "node-03": {"id": "node-03", "engine": "Blender", "vgpu_profile": "GRID_RTX6000-24Q", "vram_total_bytes": 24 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_BATTLE_012", "frame": 120},
            "node-04": {"id": "node-04", "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "vram_total_bytes": 24 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_BATTLE_014", "frame": 300},
            "node-05": {"id": "node-05", "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "vram_total_bytes": 12 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_CROWD_092", "frame": 15},
            "node-06": {"id": "node-06", "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "vram_total_bytes": 12 * 1024**3, "vram_used_bytes": 0, "gpu_util": 0.0, "cpu_util": 0.0, "active_tasks": 1, "status": "HEALTHY", "shot": "VFX_CROWD_093", "frame": 88}
        }
        self.render_latencies: Dict[str, List[float]] = {nid: [] for nid in self.nodes}

    def update_simulation(self) -> List[Dict[str, Any]]:
        logs_to_push = []
        with self.lock:
            for nid, node in self.nodes.items():
                if node["status"] == "HEALTHY":
                    node["active_tasks"] = 1
                    node["gpu_util"] = round(random.uniform(70.0, 95.0), 2)
                    node["cpu_util"] = round(random.uniform(35.0, 65.0), 2)
                    base_vram = 0.55 if node["engine"] == "Blender" else 0.68
                    node["vram_used_bytes"] = int(node["vram_total_bytes"] * (base_vram + random.uniform(-0.04, 0.04)))
                    node["frame"] += 1
                    render_time = round(random.uniform(4.5, 14.0), 3)
                    self.render_latencies[nid].append(render_time)

                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "INFO",
                        "message": f"[{node['engine']}] Rendered frame {node['frame']} for {node['shot']} in {render_time}s on {node['vgpu_profile']}"
                    })
                elif node["status"] == "CRASHED_OOM":
                    node["active_tasks"] = 0
                    node["gpu_util"] = 0.0
                    node["cpu_util"] = 4.0
                    node["vram_used_bytes"] = node["vram_total_bytes"]  # 100% saturation
                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "CRITICAL",
                        "message": f"[CUDA] CRITICAL: CUDA_ERROR_OUT_OF_MEMORY: Shot {node['shot']} failed on {nid}. VRAM exhausted during allocation."
                    })
        return logs_to_push

    def trigger_oom_crash(self):
        with self.lock:
            node = self.nodes["node-04"]
            node["status"] = "CRASHED_OOM"
        print(f"\n{RED}{BOLD}[TRIGGERED] CUDA OOM Crash activated on Node 4!{RESET}")

    def recover_all(self):
        with self.lock:
            for nid, node in self.nodes.items():
                if node["status"] != "HEALTHY":
                    node["status"] = "HEALTHY"
                    node["vram_used_bytes"] = int(node["vram_total_bytes"] * 0.45)
                    print(f"{GREEN}[RECOVERED] {nid} restored to HEALTHY.{RESET}")

    def get_prometheus_metrics(self) -> str:
        lines = []
        with self.lock:
            lines.append("# HELP gpu_memory_used_bytes GPU VRAM Memory used in bytes\n# TYPE gpu_memory_used_bytes gauge")
            for nid, node in self.nodes.items():
                lines.append(f'gpu_memory_used_bytes{{node_id="{nid}",engine="{node["engine"]}"}} {node["vram_used_bytes"]}')

            lines.append("# HELP node_status Current status (1=HEALTHY, 0=CRASHED_OOM)\n# TYPE node_status gauge")
            for nid, node in self.nodes.items():
                val = 0 if node["status"] == "CRASHED_OOM" else 1
                lines.append(f'node_status{{node_id="{nid}",status="{node["status"]}"}} {val}')
        return "\n".join(lines) + "\n"

    def push_to_loki(self, raw_logs: List[Dict[str, Any]]):
        if not raw_logs or not self.loki_url:
            return

        streams = []
        curr_ns = str(time.time_ns())
        for item in raw_logs:
            streams.append({
                "stream": {
                    "job": "render_cluster",
                    "node_id": item["node"],
                    "engine": item["engine"],
                    "level": item["level"]
                },
                "values": [[curr_ns, f"{item['level']}: {item['message']}"]]
            })

        payload = json.dumps({"streams": streams}).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.auth_header:
            headers["Authorization"] = self.auth_header

        req = urllib.request.Request(self.loki_url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                if resp.status in (200, 204):
                    pass  # Success
        except urllib.error.HTTPError as e:
            print(f"{RED}[Loki Push Error] HTTP {e.code}: {e.reason}{RESET}")
        except Exception as e:
            print(f"{YELLOW}[Loki Push Warning] Unable to reach Loki: {e}{RESET}")


class CombinedHTTPHandler(http.server.BaseHTTPRequestHandler):
    simulator: VFXClusterSimulator = None

    def do_GET(self):
        if self.path == "/metrics":
            payload = self.simulator.get_prometheus_metrics()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload.encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "RUNNING", "endpoints": ["/metrics", "/simulate/crash", "/simulate/recover"]}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/simulate/crash":
            self.simulator.trigger_oom_crash()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "CRASH_TRIGGERED", "target": "node-04"}).encode("utf-8"))
        elif self.path == "/simulate/recover":
            self.simulator.recover_all()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "RECOVERED", "target": "all"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logging in the SRE terminal


def run_simulation_loop(simulator: VFXClusterSimulator):
    while simulator.running:
        try:
            logs = simulator.update_simulation()
            simulator.push_to_loki(logs)
        except Exception as e:
            print(f"{RED}[Error in simulation loop]: {e}{RESET}")
        time.sleep(simulator.tick_interval)


def run_cli_shell(simulator: VFXClusterSimulator, port: int):
    print(f"\n{BOLD}{CYAN}=== SHOWRUNNER AI: VIRTUAL VFX RENDER FARM TELEMETRY ==={RESET}")
    print(f"Scrape URL: {CYAN}http://localhost:{port}/metrics{RESET}")
    print(f"Loki Target: {CYAN}{simulator.loki_url}{RESET}")
    print(f"Loki User: {CYAN}{simulator.loki_user}{RESET}\n")

    while simulator.running:
        try:
            sys.stdout.write(f"{BOLD}showrunner-sre@{CYAN}farm-cluster{RESET}> ")
            sys.stdout.flush()
            cmd = sys.stdin.readline().strip().lower()
            if cmd == "status":
                print(f"\n{'NODE':<10} | {'ENGINE':<15} | {'VRAM UTILIZATION':<25} | {'STATUS':<15}")
                print("-" * 75)
                with simulator.lock:
                    for nid, n in sorted(simulator.nodes.items()):
                        used_gb = n["vram_used_bytes"] / (1024**3)
                        tot_gb = n["vram_total_bytes"] / (1024**3)
                        color = GREEN if n["status"] == "HEALTHY" else RED
                        print(f"{nid:<10} | {n['engine']:<15} | {used_gb:.1f}/{tot_gb:.1f} GB ({n['vram_used_bytes']/n['vram_total_bytes']*100:.1f}%) | {color}{n['status']}{RESET}")
                print()
            elif cmd == "crash":
                simulator.trigger_oom_crash()
            elif cmd == "recover":
                simulator.recover_all()
            elif cmd in ["exit", "quit"]:
                simulator.running = False
                break
        except KeyboardInterrupt:
            simulator.running = False
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PROM_PORT)
    parser.add_argument("--loki-url", type=str, default=DEFAULT_LOKI_URL)
    parser.add_argument("--loki-user", type=str, default=LOKI_USER_ID)
    parser.add_argument("--token", type=str, default=GRAFANA_TOKEN)
    args = parser.parse_args()

    simulator = VFXClusterSimulator(DEFAULT_TICK_INTERVAL, args.loki_url, args.loki_user, args.token)
    CombinedHTTPHandler.simulator = simulator

    # Start HTTP server on configured port
    httpd = http.server.HTTPServer(("", args.port), CombinedHTTPHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    # Start simulation tick thread
    threading.Thread(target=run_simulation_loop, args=(simulator,), daemon=True).start()

    # Start CLI shell on main thread
    run_cli_shell(simulator, args.port)


if __name__ == "__main__":
    main()