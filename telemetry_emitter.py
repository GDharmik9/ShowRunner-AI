#!/usr/bin/env python3
"""
telemetry_emitter.py
Autonomous Render Farm Telemetry Emitter and Crash Simulator

This script simulates a 6-node VFX rendering cluster running Blender and Unreal Engine workloads.
It exposes Prometheus metrics via a built-in, zero-dependency lightweight HTTP server
and pushes log streams to a Grafana Loki endpoint. It includes an interactive CLI to trigger
failure modes (such as a CUDA Out-of-Memory error) on demand for live demonstrations.

Developed by a Site Reliability Engineer for VFX pipeline monitoring.
"""

import argparse
import http.server
import json
import random
import sys
import threading
import time
import urllib.request
from typing import Dict, Any, List

# --- COLOR DEFINITIONS FOR CLEAN TERMINAL OUTPUT ---
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"

# --- DEFAULT CONFIGURATION ---
DEFAULT_PROM_PORT = 8000
DEFAULT_LOKI_URL = "http://localhost:3100/loki/api/v1/push"
DEFAULT_TICK_INTERVAL = 2.0  # seconds between state updates and log pushes

# --- CLUSTER SIMULATOR STATE ---
class VFXClusterSimulator:
    def __init__(self, tick_interval: float, loki_url: str):
        self.tick_interval = tick_interval
        self.loki_url = loki_url
        self.running = True
        self.lock = threading.Lock()
        
        # Initialize 6 nodes with realistic GPU and workload characteristics
        self.nodes: Dict[str, Dict[str, Any]] = {
            "node-01": {
                "id": "node-01",
                "engine": "Blender",
                "vgpu_profile": "GRID_RTX6000-12Q",
                "vram_total_bytes": 12 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_OPENING_001",
                "frame": 1
            },
            "node-02": {
                "id": "node-02",
                "engine": "Blender",
                "vgpu_profile": "GRID_RTX6000-12Q",
                "vram_total_bytes": 12 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_OPENING_002",
                "frame": 45
            },
            "node-03": {
                "id": "node-03",
                "engine": "Blender",
                "vgpu_profile": "GRID_RTX6000-24Q",
                "vram_total_bytes": 24 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_BATTLE_012",
                "frame": 120
            },
            "node-04": {
                "id": "node-04",
                "engine": "Unreal Engine",
                "vgpu_profile": "GRID_RTX6000-24Q",
                "vram_total_bytes": 24 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_BATTLE_014",
                "frame": 300
            },
            "node-05": {
                "id": "node-05",
                "engine": "Unreal Engine",
                "vgpu_profile": "GRID_RTX6000-12Q",
                "vram_total_bytes": 12 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_CROWD_092",
                "frame": 15
            },
            "node-06": {
                "id": "node-06",
                "engine": "Unreal Engine",
                "vgpu_profile": "GRID_RTX6000-12Q",
                "vram_total_bytes": 12 * 1024 * 1024 * 1024,
                "vram_used_bytes": 0,
                "gpu_util": 0.0,
                "cpu_util": 0.0,
                "active_tasks": 0,
                "status": "HEALTHY",
                "shot": "VFX_CROWD_093",
                "frame": 88
            }
        }
        
        # Track statistics for rendering latency histograms
        self.latency_buckets = [1.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')]
        self.render_latencies: Dict[str, List[float]] = {nid: [] for nid in self.nodes}
        self.total_completed_frames: Dict[str, int] = {nid: 0 for nid in self.nodes}

    def update_simulation(self) -> List[Dict[str, Any]]:
        """Updates the internal telemetry states of the simulated nodes and returns generated logs."""
        logs_to_push = []
        with self.lock:
            for nid, node in self.nodes.items():
                if node["status"] == "HEALTHY":
                    # Simulating realistic rendering cycles
                    node["active_tasks"] = 1
                    node["gpu_util"] = round(random.uniform(75.0, 98.0), 2)
                    node["cpu_util"] = round(random.uniform(40.0, 70.0), 2)
                    
                    # VRAM behavior: Blender uses a bit less usually, Unreal Engine scales heavily
                    base_vram_pct = 0.55 if node["engine"] == "Blender" else 0.70
                    noise = random.uniform(-0.05, 0.05)
                    node["vram_used_bytes"] = int(node["vram_total_bytes"] * (base_vram_pct + noise))
                    
                    # Advance frames
                    node["frame"] += 1
                    render_time = round(random.uniform(4.5, 18.0), 3)
                    self.render_latencies[nid].append(render_time)
                    self.total_completed_frames[nid] += 1
                    
                    # Generate normal logs
                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "INFO",
                        "message": f"[{node['engine']}] Rendered frame {node['frame']} for shot {node['shot']} in {render_time}s on {node['vgpu_profile']}"
                    })
                    
                    # Occasional texture loading warnings
                    if random.random() < 0.15:
                        logs_to_push.append({
                            "node": nid,
                            "engine": node["engine"],
                            "level": "WARN",
                            "message": f"[{node['engine']}] Large texture fetch took longer than threshold (3.2s) for asset path: /vol/assets/scenes/{node['shot']}/textures/"
                        })
                
                elif node["status"] == "CRASHED_OOM":
                    # Peg GPU and saturate memory to simulate OOM condition before process termination
                    node["active_tasks"] = 0
                    node["gpu_util"] = 0.0
                    node["cpu_util"] = 5.0  # minimal idle CPU usage
                    # VRAM is saturated (pegged to 100%)
                    node["vram_used_bytes"] = node["vram_total_bytes"]
                    
                    # Generate critical error logs
                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "CRITICAL",
                        "message": f"[CUDA] CRITICAL: CUDA_ERROR_OUT_OF_MEMORY: Shot {node['shot']} failed on Node 4. Host allocation failed trying to map virtual frame buffer grid size 16384x16384."
                    })
                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "ERROR",
                        "message": f"[{node['engine']}] Fatal error crashed rendering core. Exit code 139 (Segmentation fault)."
                    })
                    
                elif node["status"] == "DEADLOCKED":
                    # Thread deadlock: High CPU, 0% GPU, no progress logs
                    node["active_tasks"] = 1
                    node["gpu_util"] = 0.0
                    node["cpu_util"] = 100.0  # Spinning CPU core
                    node["vram_used_bytes"] = int(node["vram_total_bytes"] * 0.45)
                    
                    logs_to_push.append({
                        "node": nid,
                        "engine": node["engine"],
                        "level": "WARN",
                        "message": f"[{node['engine']}] [Thread-0x7f1a] Deadlock warning: Render thread has been waiting on spinlock 0x8dfa2 for 120 seconds."
                    })

        return logs_to_push

    def trigger_oom_crash(self):
        """Simulate a sudden OOM crash scenario on Node 4."""
        with self.lock:
            node = self.nodes["node-04"]
            node["status"] = "CRASHED_OOM"
            node["shot"] = "VFX_BATTLE_014"
            node["frame"] = 300
        print(f"\n{RED}{BOLD}[TRIGGERED] CUDA OOM Crash activated on Node 4!{RESET}")

    def trigger_deadlock(self, node_id: str = "node-03"):
        """Simulate a thread deadlock on the specified node."""
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "DEADLOCKED"
                print(f"\n{RED}{BOLD}[TRIGGERED] Thread Deadlock activated on {node_id}!{RESET}")

    def recover_all(self):
        """Recover all nodes to normal, healthy rendering states."""
        with self.lock:
            for nid, node in self.nodes.items():
                if node["status"] != "HEALTHY":
                    node["status"] = "HEALTHY"
                    node["cpu_util"] = 0.0
                    node["gpu_util"] = 0.0
                    node["vram_used_bytes"] = 0
                    print(f"{GREEN}[RECOVERED] {nid} status reset to HEALTHY.{RESET}")

    def get_prometheus_metrics(self) -> str:
        """Serializes current states into plaintext Prometheus Exposition Format."""
        metrics_lines = []
        with self.lock:
            # Metric 1: gpu_memory_used_bytes
            metrics_lines.append("# HELP gpu_memory_used_bytes GPU VRAM Memory used in bytes")
            metrics_lines.append("# TYPE gpu_memory_used_bytes gauge")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'gpu_memory_used_bytes{{node_id="{nid}",engine="{node["engine"]}",vgpu_profile="{node["vgpu_profile"]}"}} {node["vram_used_bytes"]}'
                )

            # Metric 2: gpu_memory_total_bytes
            metrics_lines.append("# HELP gpu_memory_total_bytes GPU VRAM Total available memory in bytes")
            metrics_lines.append("# TYPE gpu_memory_total_bytes gauge")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'gpu_memory_total_bytes{{node_id="{nid}",engine="{node["engine"]}",vgpu_profile="{node["vgpu_profile"]}"}} {node["vram_total_bytes"]}'
                )

            # Metric 3: gpu_utilization_percent
            metrics_lines.append("# HELP gpu_utilization_percent GPU core utilization percentage (0-100)")
            metrics_lines.append("# TYPE gpu_utilization_percent gauge")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'gpu_utilization_percent{{node_id="{nid}",engine="{node["engine"]}"}} {node["gpu_util"]}'
                )

            # Metric 4: cpu_utilization_percent
            metrics_lines.append("# HELP cpu_utilization_percent Node CPU utilization percentage (0-100)")
            metrics_lines.append("# TYPE cpu_utilization_percent gauge")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'cpu_utilization_percent{{node_id="{nid}",engine="{node["engine"]}"}} {node["cpu_util"]}'
                )

            # Metric 5: active_task_count
            metrics_lines.append("# HELP active_task_count Number of concurrent render tasks currently executing")
            metrics_lines.append("# TYPE active_task_count gauge")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'active_task_count{{node_id="{nid}",engine="{node["engine"]}"}} {node["active_tasks"]}'
                )

            # Metric 6: render_frame_latency_seconds (Histogram)
            metrics_lines.append("# HELP render_frame_latency_seconds Render latency of frame completions")
            metrics_lines.append("# TYPE render_frame_latency_seconds histogram")
            for nid, node in self.nodes.items():
                latencies = self.render_latencies[nid]
                total_sum = sum(latencies)
                total_count = len(latencies)
                
                # Buckets
                cumulative_count = 0
                for bucket in self.latency_buckets:
                    cumulative_count = sum(1 for l in latencies if l <= bucket)
                    b_str = "+Inf" if bucket == float('inf') else str(bucket)
                    metrics_lines.append(
                        f'render_frame_latency_seconds_bucket{{node_id="{nid}",engine="{node["engine"]}",le="{b_str}"}} {cumulative_count}'
                    )
                metrics_lines.append(
                    f'render_frame_latency_seconds_sum{{node_id="{nid}",engine="{node["engine"]}"}} {total_sum:.4f}'
                )
                metrics_lines.append(
                    f'render_frame_latency_seconds_count{{node_id="{nid}",engine="{node["engine"]}"}} {total_count}'
                )

            # Metric 7: render_frames_completed_total (Counter)
            metrics_lines.append("# HELP render_frames_completed_total Total rendered frames completed since startup")
            metrics_lines.append("# TYPE render_frames_completed_total counter")
            for nid, node in self.nodes.items():
                metrics_lines.append(
                    f'render_frames_completed_total{{node_id="{nid}",engine="{node["engine"]}"}} {self.total_completed_frames[nid]}'
                )

            # Metric 8: node_status (Enriched metadata state gauge)
            metrics_lines.append("# HELP node_status Current status state of the node (1=HEALTHY, 0=CRASHED_OOM, -1=DEADLOCKED)")
            metrics_lines.append("# TYPE node_status gauge")
            for nid, node in self.nodes.items():
                status_val = 1
                if node["status"] == "CRASHED_OOM":
                    status_val = 0
                elif node["status"] == "DEADLOCKED":
                    status_val = -1
                metrics_lines.append(
                    f'node_status{{node_id="{nid}",engine="{node["engine"]}",status="{node["status"]}"}} {status_val}'
                )

        return "\n".join(metrics_lines) + "\n"

    def push_to_loki(self, raw_logs: List[Dict[str, Any]]):
        """Pushes structured logs to Loki endpoint using standard HTTP protocols."""
        if not raw_logs:
            return
        
        # Format the push request to fit Loki JSON standards
        # Loki API payload requires nanoseconds timestamp: str(time.time_ns())
        streams_dict = {}
        curr_ns = str(time.time_ns())
        
        for item in raw_logs:
            key = (item["node"], item["engine"], item["level"])
            if key not in streams_dict:
                streams_dict[key] = {
                    "stream": {
                        "node_id": item["node"],
                        "engine": item["engine"],
                        "level": item["level"],
                        "vfx_farm": "los_angeles_stage_b"
                    },
                    "values": []
                }
            streams_dict[key]["values"].append([curr_ns, f"{item['level']}: {item['message']}"])
        
        payload = {
            "streams": list(streams_dict.values())
        }
        
        # Issue post via python urllib to avoid strict external dependencies
        req_data = json.dumps(payload).encode('utf-8')
        try:
            req = urllib.request.Request(
                self.loki_url,
                data=req_data,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=3.0) as f:
                # Successfully pushed to Loki
                pass
        except Exception as e:
            # Gracefully ignore Loki connection errors when not configured/running locally
            # Output warning locally without halting simulator
            pass

# --- METRICS HTTP SERVER FOR PROMETHEUS SCRAPING ---
class MetricsHTTPHandler(http.server.BaseHTTPRequestHandler):
    simulator: VFXClusterSimulator = None

    def do_GET(self):
        if self.path == "/metrics":
            try:
                metrics_payload = self.simulator.get_prometheus_metrics()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                self.end_headers()
                self.wfile.write(metrics_payload.encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Internal Exporter Error: {str(e)}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Use /metrics endpoint for scraping.")

    def log_message(self, format, *args):
        # Mute standard HTTP request logging in terminal to keep SRE console clean
        pass

def run_metrics_server(port: int, simulator: VFXClusterSimulator):
    """Binds and runs the Prometheus Exporter HTTP server on a background thread."""
    MetricsHTTPHandler.simulator = simulator
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, MetricsHTTPHandler)
    print(f"{GREEN}{BOLD}[EXPORTER] Exposing metrics at http://localhost:{port}/metrics{RESET}")
    httpd.serve_forever()

# --- BACKROUND SIMULATOR LOOP ---
def run_simulation_loop(simulator: VFXClusterSimulator):
    """Periodically ticks the simulation, advances states, and pushes logs."""
    while simulator.running:
        try:
            logs = simulator.update_simulation()
            # Push logs to Loki if configured
            simulator.push_to_loki(logs)
            
            # Print a subtle visual indicator in the SRE CLI to show simulation tick active
            sys.stdout.flush()
        except Exception as e:
            print(f"{RED}[ERROR] In simulation tick: {e}{RESET}")
        time.sleep(simulator.tick_interval)

# --- INTERACTIVE SRE TERMINAL CLI ---
def run_cli_shell(simulator: VFXClusterSimulator, prom_port: int):
    """Launches an interactive console to inspect node statuses, inject and heal cluster faults."""
    print(f"\n{BOLD}{CYAN}=== SHOWRUNNER AI: VIRTUAL VFX RENDER FARM WORKER TERMINAL ==={RESET}")
    print(f"6-Node cluster simulation initialized. Press '{BOLD}help{RESET}' for command lists.")
    print(f"Scrape Endpoint: {CYAN}http://localhost:{prom_port}/metrics{RESET}")
    print(f"Loki Target: {CYAN}{simulator.loki_url}{RESET}\n")

    while simulator.running:
        try:
            sys.stdout.write(f"{BOLD}showrunner-sre@{CYAN}farm-cluster{RESET}> ")
            sys.stdout.flush()
            cmd_line = sys.stdin.readline()
            if not cmd_line:
                break
            
            cmd_parts = cmd_line.strip().split()
            if not cmd_parts:
                continue
            
            cmd = cmd_parts[0].lower()
            
            if cmd in ["help", "?"]:
                print(f"\n{BOLD}Available Commands:{RESET}")
                print(f"  {BOLD}status{RESET}        - Prints a dynamic table of all simulated GPU nodes & current states.")
                print(f"  {BOLD}crash{RESET}         - Simulates CUDA Out-Of-Memory (OOM) crash scenario on Node 4 (Unreal Engine).")
                print(f"  {BOLD}deadlock{RESET}      - Simulates heavy thread deadlock hang on Node 3 (Blender).")
                print(f"  {BOLD}recover{RESET}       - Triggers hot replacement, restarts processes, and restores cluster health.")
                print(f"  {BOLD}metrics{RESET}       - Print raw Prometheus metric payload to terminal.")
                print(f"  {BOLD}exit{RESET} / {BOLD}quit{RESET}   - Safe system shutdown.\n")
                
            elif cmd == "status":
                print(f"\n{BOLD}{'NODE':<10} | {'ENGINE':<15} | {'PROFILE':<18} | {'VRAM UTILIZATION':<25} | {'GPU UTIL':<10} | {'STATUS':<15}{RESET}")
                print("-" * 105)
                with simulator.lock:
                    for nid, node in sorted(simulator.nodes.items()):
                        vram_used_gb = node["vram_used_bytes"] / (1024 ** 3)
                        vram_total_gb = node["vram_total_bytes"] / (1024 ** 3)
                        vram_pct = (node["vram_used_bytes"] / node["vram_total_bytes"]) * 100
                        vram_bar = f"{vram_used_gb:.1f}/{vram_total_gb:.1f} GB ({vram_pct:.1f}%)"
                        
                        status_color = GREEN if node["status"] == "HEALTHY" else RED
                        status_str = f"{status_color}{node['status']}{RESET}"
                        
                        gpu_util_str = f"{node['gpu_util']}%"
                        
                        print(f"{node['id']:<10} | {node['engine']:<15} | {node['vgpu_profile']:<18} | {vram_bar:<25} | {gpu_util_str:<10} | {status_str:<15}")
                print()
                
            elif cmd == "crash":
                simulator.trigger_oom_crash()
                
            elif cmd == "deadlock":
                simulator.trigger_deadlock("node-03")
                
            elif cmd == "recover":
                print(f"\n{YELLOW}[RECOVERY] Sending SIGTERM/SIGKILL signals to failed renderer engines...{RESET}")
                time.sleep(1.0)
                print(f"{YELLOW}[RECOVERY] Clearing GPU command queues and restarting VM worker processes...{RESET}")
                time.sleep(1.0)
                simulator.recover_all()
                print(f"{GREEN}{BOLD}[RECOVERY] All systems nominal! Virtual cluster restored.{RESET}\n")
                
            elif cmd == "metrics":
                print(f"\n{CYAN}--- BEGIN PROMETHEUS METRIC PAYLOAD ---{RESET}")
                print(simulator.get_prometheus_metrics())
                print(f"{CYAN}--- END PROMETHEUS METRIC PAYLOAD ---{RESET}\n")
                
            elif cmd in ["exit", "quit"]:
                print(f"\n{YELLOW}Stopping simulator background threads and shutting down...{RESET}")
                simulator.running = False
                break
            else:
                print(f"{RED}Unknown command: '{cmd_line.strip()}'. Type 'help' to see valid commands.{RESET}")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}Ctrl+C intercepted. Stopping simulator background threads and shutting down...{RESET}")
            simulator.running = False
            break

def main():
    parser = argparse.ArgumentParser(description="Showrunner AI: Virtual VFX Render Farm Telemetry Emitter")
    parser.add_argument("--port", type=int, default=DEFAULT_PROM_PORT, help=f"Port to run the Prometheus Exporter (default: {DEFAULT_PROM_PORT})")
    parser.add_argument("--loki-url", type=str, default=DEFAULT_LOKI_URL, help=f"HTTP endpoint url for Grafana Loki Push API (default: {DEFAULT_LOKI_URL})")
    parser.add_argument("--interval", type=float, default=DEFAULT_TICK_INTERVAL, help=f"Metric tick update and Loki log push interval in seconds (default: {DEFAULT_TICK_INTERVAL})")
    args = parser.parse_args()

    # Step 1: Create the core simulator
    simulator = VFXClusterSimulator(tick_interval=args.interval, loki_url=args.loki_url)

    # Step 2: Spin up the built-in Prometheus metrics server thread
    server_thread = threading.Thread(
        target=run_metrics_server, 
        args=(args.port, simulator), 
        daemon=True
    )
    server_thread.start()

    # Step 3: Spin up the simulator task state and log emitter loop thread
    sim_thread = threading.Thread(
        target=run_simulation_loop, 
        args=(simulator,), 
        daemon=True
    )
    sim_thread.start()

    # Step 4: Run CLI interface inside the primary main thread
    run_cli_shell(simulator, args.port)

if __name__ == "__main__":
    main()
