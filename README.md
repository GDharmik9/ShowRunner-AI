# ShowRunner AI: Autonomous VFX Render Farm Guardian

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Grafana Cloud Track](https://img.shields.io/badge/Grafana%20Cloud-Track-orange)](https://grafana.com)
[![Google Cloud Agentic Cinema](https://img.shields.io/badge/Google%20Cloud-Agentic%20Cinema-blue)](https://devpost.com)

ShowRunner AI is an autonomous, self-healing **"virtual render farm wrangler"** designed to resolve compute and GPU memory bottlenecks across visual effects (VFX) rendering pipelines. Built for the **Grafana Labs track** of the **Agentic Cinema Hackathon**, the system bridges **Google Cloud's Vertex AI Agent Builder (Gemini)** and **Grafana Cloud** using the **Model Context Protocol (MCP)** and native APIs.

By correlating Prometheus metric spikes with real-time Loki log patterns, ShowRunner AI detects crashes—such as CUDA Out-of-Memory (OOM) failures or thread deadlocks—and autonomously executes surgical remediations (e.g., dynamically splitting frame renders into smaller Arnold rendering tiles) to recover node health without manual human intervention.

---

## Architecture Overview

ShowRunner AI operates a secure, closed-loop telemetry and auto-remediation feedback system:

```
                      +------------------------------------------+
                      |      Studio Command Center Dashboard     |
                      |          (StudioCommandCenter.jsx)       |
                      +--------------------+---------------------+
                                           |
                                           v (Interactive Demo Actions)
+-----------------------------------+      |
|  Simulated 6-Node GPU VFX Farm    +------+ (Loki Push / Prom Scrape)
|      (telemetry_emitter.py)       |      |
+-----------------+-----------------+      v
                  |               +--------+------------+
                  | (Scraped      |    Grafana Cloud    |
                  |  Metrics)     | (Prometheus & Loki) |
                  |               +--------+------------+
                  v                        |
        +---------+---------+              | (Model Context Protocol /
        |   Grafana Alloy   |              |  JSON-RPC 2.0 Interface)
        |  Telemetry Agent  |              v
        +-------------------+     +--------+------------+
                                  |  Grafana MCP Server |
                                  |   (mcp-grafana)     |
                                  +--------+------------+
                                           |
                                           v (Targeted Query Results)
                                  +--------+------------+
                                  |   Agent Service     |
                                  |  (agent_service.py) |
                                  |  (Gemini Pro LLM)   |
                                  +--------+------------+
                                           |
                                           v (Surgical Resolution Webhook)
                                  +--------+------------+
                                  | Studio Queue Manager|
                                  |      (OpenCue)      |
                                  +---------------------+
```

---

## Core Repository Components

The project repository is structured around three modular components:

1.  **`telemetry_emitter.py` (VFX Infrastructure Simulator)**:
    *   Simulates a 6-node GPU render farm using real **NVIDIA Quadro RTX vDWS (Virtual Data Center Workstation)** profiles (GRID_RTX6000-12Q/24Q).
    *   Hosts a native HTTP metrics server on port `8000` presenting standard Prometheus Exposition data (`gpu_memory_used_bytes`, `gpu_utilization_percent`, `active_task_count`, `node_status`, `render_frame_latency_seconds`).
    *   Pushes live, formatted log streams (INFO, WARN, CRITICAL OOM) straight to Grafana Loki.
    *   Includes an interactive chaos engineering CLI shell to manually trigger, monitor, or recover CUDA OOM crashes and thread lockups on target nodes.

2.  **`agent_service.py` (FastAPI Agent Orchestrator)**:
    *   Built using the native **Google GenAI SDK** (`google-genai`) to configure Gemini as the *ShowRunner AI Technical Director*.
    *   Implements secure, declarative tool calling interfaces for querying Prometheus metrics, checking Loki log ranges, and performing remote remediation actions.
    *   Enforces strict correlation safety rules: Gemini must check both the metric spike history and corresponding log tracebacks to verify a crash signature before sending a fix.
    *   Features a mock queue-remediation executor to modify node states, drop VRAM burdens, and append resolution events.

3.  **`StudioCommandCenter.jsx` (React UI Command Center)**:
    *   A modern, dark-mode dashboard styled with Tailwind CSS.
    *   Displays 6 real-time health cards mapping core temperatures, VRAM capacities, and ongoing tasks.
    *   Features a Grafana Live Panel visualizing a simulated frame latency histogram and an live Loki terminal feed.
    *   Includes a side-by-side autonomous remediation timeline log and a **Director Chat Console** to prompt the Gemini agent in natural language.

---

## Prerequisites & Installation

### Local Infrastructure Setup

To run the complete ecosystem locally, you will need **Python 3.10+** and a running **Node.js** environment.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/ShowRunner-ai.git
    cd ShowRunner-ai
    ```

2.  **Install Python Dependencies**:
    ```bash
    pip install fastapi uvicorn httpx google-genai
    ```

3.  **Configure Environment Variables**:
    Set up your Google Cloud API credentials to allow the orchestrator to communicate with Gemini models:
    ```bash
    # Set your Google Gemini API Key
    export GEMINI_API_KEY="AIzaSyYourKeyHere..."

    # (Optional) Customize Grafana Cloud connection details
    export LOKI_ENDPOINT="http://localhost:3100/loki/api/v1/push"
    export GRAFANA_TOKEN="glsa_your_auth_token_here"
    ```

---

## Step-by-Step Running Guide

### Step 1: Start the VFX Telemetry Simulator
Open a new terminal window and run the telemetry simulator to spin up the 6-node virtual render farm and the interactive chaos console:

```bash
python3 telemetry_emitter.py
```
Upon startup, the simulator starts background threads and outputs a diagnostic grid showing the cluster is healthy:
```
NODE       | ENGINE          | PROFILE            | VRAM UTILIZATION          | GPU UTIL   | STATUS         
---------------------------------------------------------------------------------------------------------
node-01    | Blender         | GRID_RTX6000-12Q   | 6.2/12.0 GB (51.6%)       | 82.49%     | HEALTHY
node-02    | Blender         | GRID_RTX6000-12Q   | 7.1/12.0 GB (59.1%)       | 91.03%     | HEALTHY
node-03    | Blender         | GRID_RTX6000-24Q   | 13.8/24.0 GB (57.5%)      | 76.22%     | HEALTHY
node-04    | Unreal Engine   | GRID_RTX6000-24Q   | 16.5/24.0 GB (68.7%)      | 89.15%     | HEALTHY
node-05    | Unreal Engine   | GRID_RTX6000-12Q   | 8.1/12.0 GB (67.5%)       | 84.11%     | HEALTHY
node-06    | Unreal Engine   | GRID_RTX6000-12Q   | 8.3/12.0 GB (69.1%)       | 88.02%     | HEALTHY

ShowRunner-sre@farm-cluster>
```
*   Your metrics are now exposed for scraping at `http://localhost:8000/metrics`.
*   Simulated logs are automatically pushed via HTTP to your Loki target endpoint.

### Step 2: Start the FastAPI AI Agent Service
In a separate terminal window, initialize the FastAPI orchestration server to boot the Gemini loop:

```bash
python3 agent_service.py
```
This runs a local ASGI webserver on `http://localhost:5000`. The server registers all core function tools (Prometheus metrics query, Loki log query, queue webhook executor) and exposes the `/agent/chat` REST endpoint.

### Step 3: Launch the React Studio Command Center
Import the `StudioCommandCenter.jsx` component into your React/Vite development stack:

```bash
# Set up a clean React + Tailwind template
npm create vite@latest studio-dashboard -- --template react
cd studio-dashboard
npm install lucide-react tailwindcss postcss autoprefixer

# Initialize Tailwind and place StudioCommandCenter.jsx inside your src/ component folder
# Start the web development server
npm run dev
```
Open `http://localhost:5173` in your browser to view the interactive, dark-mode dashboard.

---

## Demonstrating the Autonomous Healing Loop

ShowRunner AI is designed to make a complete, self-healing loop visible during a live demo or presentation:

1.  **Inject a Failure**: In the simulator terminal, run `crash` or click the **"Inject CUDA OOM on Node 4"** trigger on your React dashboard. 
    *   Node 4 instantly registers an out-of-memory crash. 
    *   A metric spike pegs Node 4's VRAM to 100%.
    *   A critical traceback is emitted to the Loki stream: `CRITICAL CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4`.
2.  **Run the Agent Query**: Prompt the agent using the chat panel or issue a REST request:
    ```bash
    curl -X POST http://localhost:5000/agent/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "Audit Node 4 health and apply a fix if you detect any issues."}'
    ```
3.  **Agent Diagnostic Corroboration**: Gemini's system instructions restrict it from applying a reboot directly based on a basic warning. It executes tool calls to verify:
    *   `query_grafana_metrics` -> It sees `node_status` has dropped to `0` (OOM State) and `gpu_memory_used_bytes` is maxed.
    *   `search_grafana_logs` -> It matches the LogQL regex string to find `CUDA_ERROR_OUT_OF_MEMORY` for Shot `VFX_BATTLE_014`.
4.  **Surgical Remediation Execution**: Recognizing the CUDA memory overflow, the agent invokes `remediate_render_node(node_id="node-04", action="tiled_config_switch", shot_id="VFX_BATTLE_014")`. 
    *   The backend changes the engine setting to tiled rendering blocks (64x64).
    *   This drops the active VRAM footprint down to a safe `11.2GB`.
    *   The node's state indicators dynamically return to green `HEALTHY` status in real-time on your dashboard.

---

## Production Security, Guardrails, & Compliance

*   **Model Armor**: Acts as an inline DLP (Data Loss Prevention) shield to filter and mask prompt/response parameters, checking that proprietary local file directories, raw asset textures, or artist credentials are never leaked outside the secure studio environment.
*   **Role-Based API Tokenization**: Integrations with Grafana and queue managers are governed using strict, principal-level GCP Service Account profiles. Tool queries and write-back hooks are compartmentalized so that the LLM only has read access to metrics and write permissions on dedicated REST queue structures.
*   **Zero-State Grounding**: This system adheres strictly to source-grounded reasoning. It is designed to never invent telemetry stats, invent hypothetical nodes, or propose speculative reboots without verified evidence in Prometheus metrics and Loki logs.

---

## Roadmap

*   **Pillar 1: Rights Clearance RAG Integration**: Wire Vertex AI Search and RAG Engine into the render queue manager. This lets the agent search media clearance documents to flag copyright or actor rights conflicts on asset textures *prior* to allocating compute hours.
*   **Pillar 3: FinOps with ClickHouse & Google Compute Engine**: Integrate an **mcp-clickhouse** query layer. This allows the ShowRunner AI agent to analyze historical job logs and spot-node terminations inside a ClickHouse analytics lake, optimizing long-term infrastructure spend by mapping workloads directly to GCE Committed Use Discounts (CUD) and Preemptible virtual instances.

---

## License

This project is open-source software licensed under the [Apache License, Version 2.0](LICENSE). Feel free to modify, distribute, or incorporate into your studio's SRE pipeline.

## docs Links
- ### [Low-Level Design (LLD)](docs/LLD.md)
- ### [High-Level Design (HLD)](docs/HLD.md)
- ### [FlowChart](docs/FlowChart.md)
- ### [Schema](docs/Schema.md)
- ### [Google Setup GCD](docs/GCD.md)
- ### [Grafana](docs/Grafana.md)
- ### [Frontend](docs/Frontend.md)
- ### [backend](docs/backend.md)
- ### [LocalSetup](docs/LocalSetup.md)