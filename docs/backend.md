# ShowRunner AI — FastAPI Backend Orchestrator

## 1. Service Overview
`agent_service.py` is the cognitive core of ShowRunner AI. It:
- Maintains in-memory cluster state for all 6 GPU nodes
- Provides REST API endpoints consumed by the React frontend
- Drives multi-turn Gemini 2.5 Flash reasoning loops via native function calling
- Executes SRE remediations and logs all events to a resolution timeline

## 2. API Endpoints

### GET /
Health check and API discovery.
```json
{
  "service": "Showrunner AI Technical Director",
  "status": "online",
  "interactive_docs": "/docs",
  "cluster_state": "/cluster/nodes"
}
```

### GET /cluster/nodes
Returns live state for all 6 render nodes.
```json
{
  "node-01": { "engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 6.5, "vram_total_gb": 12 },
  "node-04": { "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "status": "CRASHED_OOM", "vram_used_gb": 24.0, "vram_total_gb": 24 }
}
```

### GET /cluster/events
Append-only audit trail of all autonomous remediation events.
```json
{
  "events": [
    "[SYSTEM] Cluster simulation online. Node 4 pre-loaded with CRASHED_OOM.",
    "[REMEDIATION_SUCCESS] Arnold tile-render switch applied on node-04. VRAM stabilized."
  ]
}
```

### POST /agent/chat
Primary inference route. Drives the Gemini reasoning + tool loop.

**Request:**
```json
{ "prompt": "Node 4 is down. Correlate logs and metrics, then remediate." }
```

**Response:**
```json
{
  "status": "success",
  "agent_response": "### Showrunner AI Report\n\n**Root Cause:** CUDA_ERROR_OUT_OF_MEMORY on node-04...",
  "resolution_events": ["[REMEDIATION_SUCCESS] Arnold tiled rendering active on node-04."]
}
```

## 3. SRE System Prompt
```
You are the 'Showrunner AI Technical Director', an expert autonomous guardian of
visual effects render farm infrastructure.

CRITICAL OPERATIONAL RULES:
1. GROUNDING REQUIREMENT: Before any remediation, you MUST correlate Prometheus
   metric spikes with Grafana Loki error logs. Do NOT act on metrics alone.
2. REMEDIATION ROUTING:
   - CUDA OOM failures → switch_to_tiled (reduce VRAM pressure)
   - Deadlocked processes → process_restart
   - Unrecoverable faults → reboot_hypervisor
3. VERIFICATION: After remediation, confirm node returned to HEALTHY status.
4. REPORTING: Produce a structured markdown report with Root Cause, Action Taken,
   and Restoration Status.
```

## 4. Deterministic Fallback (handle_mock_chat_flow)
Guarantees 100% uptime during live demos if Vertex AI is unreachable:
- Evaluates input keywords: `OOM`, `NODE-04`, `CRASH`, `REMEDIATE`
- Calls `remediate_render_node("node-04", "switch_to_tiled", "VFX_BATTLE_014")`
- Generates identical structured markdown report
- Appends `[REMEDIATION_SUCCESS]` to RESOLUTION_EVENTS

## 5. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
