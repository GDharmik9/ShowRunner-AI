# ShowRunner AI — Architecture & Operational Flowcharts

## 1. End-to-End Autonomous Remediation Sequence

```mermaid
sequenceDiagram
    autonumber
    actor Wrangler as VFX SRE / Wrangler
    participant UI as Studio Command Center (React :5173)
    participant API as FastAPI Orchestrator (:5000)
    participant Gemini as Gemini 2.5 Flash (Vertex AI)
    participant Tools as Native SRE Tools
    participant Prom as Prometheus / Cluster State
    participant Loki as Grafana Loki

    Wrangler->>UI: Submit "Audit Node 4 and remediate"
    UI->>API: POST /agent/chat { prompt: "Audit Node 4..." }
    API->>Gemini: generate_content(prompt + tool_definitions)

    Note over Gemini: Turn 1 — Detect Anomaly
    Gemini-->>API: FunctionCall: query_grafana_metrics("node_status")
    API->>Tools: Execute query_grafana_metrics()
    Tools->>Prom: Read CLUSTER_STATE
    Prom-->>Tools: node-04 status=0, vram=24.0GB
    Tools-->>API: Metric string
    API->>Gemini: FunctionResponse: { status: 0, vram: 24GB }

    Note over Gemini: Turn 2 — Correlate with Logs
    Gemini-->>API: FunctionCall: search_grafana_logs(node_id=node-04)
    API->>Tools: Execute search_grafana_logs()
    Tools->>Loki: HTTP GET with LogQL filter
    Loki-->>Tools: CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014
    Tools-->>API: Log stream
    API->>Gemini: FunctionResponse: log entries

    Note over Gemini: Turn 3 — Execute Remediation
    Gemini-->>API: FunctionCall: remediate_render_node(node-04, switch_to_tiled, VFX_BATTLE_014)
    API->>Tools: Execute remediate_render_node()
    Tools->>Prom: Update node-04 vram→13.2GB, status→HEALTHY
    Tools-->>API: REMEDIATION_SUCCESS message
    API->>Gemini: FunctionResponse: success

    Note over Gemini: Final Synthesis
    Gemini-->>API: Markdown report (Root Cause, Action, Status)
    API-->>UI: { agent_response, resolution_events }
    UI->>UI: Node 4 card → Green (55% VRAM), Timeline updated
    UI-->>Wrangler: Visual confirmation of self-healing
```

---

## 2. Cluster Node State Machine

```mermaid
stateDiagram-v2
    [*] --> HEALTHY: Cluster Boot / Server Init

    HEALTHY --> CRASHED_OOM: Memory Leak / Heavy Asset (VRAM = 24.0 GB / 100%)
    HEALTHY --> DEADLOCKED: Thread Contention (CPU=100%, GPU=0%)

    CRASHED_OOM --> INVESTIGATING: Gemini Correlates Metrics + Loki Logs
    DEADLOCKED --> INVESTIGATING: Gemini Detects GPU Flatline

    INVESTIGATING --> SWITCH_TO_TILED: CUDA OOM Root Cause Confirmed
    INVESTIGATING --> PROCESS_RESTART: Deadlock Root Cause Confirmed
    INVESTIGATING --> REBOOT_HYPERVISOR: Unrecoverable Fault

    SWITCH_TO_TILED --> HEALTHY: VRAM Lowered to 13.2 GB (55%)
    PROCESS_RESTART --> HEALTHY: Process Respawned (VRAM 40%)
    REBOOT_HYPERVISOR --> HEALTHY: Node Re-initialized
```

---

## 3. Telemetry Emitter Internal Architecture

```mermaid
flowchart TD
    subgraph "Main Process"
        CLI[Interactive SRE Shell\nstatus / crash / recover / exit]
    end
    subgraph "Thread 1: Simulation Loop Every 2s"
        T1[Tick Timer] --> CALC[Compute Synthetic VRAM + Frame Counts]
        CALC --> LOKI_PUSH[HTTP POST to Grafana Loki\n/loki/api/v1/push with Basic Auth]
    end
    subgraph "Thread 2: HTTP Server Port 8000"
        METRICS[GET /metrics] --> PROM_GEN[Generate Prometheus Gauge Text]
        CRASH[POST /simulate/crash] --> SET_CRASH[Force node-04 CRASHED_OOM\nVRAM = 24.0 GB]
        RECOVER[POST /simulate/recover] --> SET_RECOVER[Restore all nodes to HEALTHY]
    end
    CLI --> T1
    CLI --> METRICS
```

---

## 4. Agent Decision Flow

```mermaid
flowchart TD
    A[Incoming Prompt from UI or Wrangler] --> B{Vertex AI Available?}
    B -- Yes --> C[Gemini 2.5 Flash Multi-Turn Loop]
    B -- No --> D[Deterministic SRE Fallback Engine]

    C --> E[Turn 1: query_grafana_metrics]
    E --> F[Turn 2: search_grafana_logs]
    F --> G{Root Cause Identified?}
    G -- CUDA OOM --> H[remediate: switch_to_tiled]
    G -- Deadlock --> I[remediate: process_restart]
    G -- Unknown --> J[remediate: reboot_hypervisor]

    H & I & J --> K[Verify node status = HEALTHY]
    K --> L[Generate Structured Markdown Report]

    D --> M[Keyword Match: OOM / NODE-04 / CRASH]
    M --> N[Auto-call switch_to_tiled on node-04]
    N --> L

    L --> O[Return to Frontend: agent_response + resolution_events]
```
