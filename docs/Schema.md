# ShowRunner AI — Data Contracts & Payload Schemas

## 1. REST API Schemas

### POST /agent/chat — Request Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UserMessage",
  "type": "object",
  "properties": {
    "prompt": {
      "type": "string",
      "description": "Natural language SRE command or automated trigger.",
      "example": "Audit Node 4. Check Grafana metrics and Loki logs, then remediate."
    },
    "message": {
      "type": "string",
      "description": "Alternative key sent by React frontend components.",
      "example": "Node 4 has crashed with OOM. Remediate node-04 and stabilize VRAM."
    }
  }
}
```

### POST /agent/chat — Response Schema
```json
{
  "status": "success",
  "agent_response": "### Showrunner AI Technical Director Report\n\n**1. Telemetry Ingested:**\n- Prometheus showed node_status on node-04 at 0 (CRASHED_OOM).\n- Correlated: CUDA_ERROR_OUT_OF_MEMORY on Shot VFX_BATTLE_014.\n\n**2. Action Taken:**\n- remediate_render_node: switch_to_tiled on node-04.\n\n**3. Node Restored:**\n- Status returned to HEALTHY. VRAM: 13.2 GB (55%).",
  "resolution_events": [
    "[SYSTEM] Cluster simulation online. Node 4 pre-loaded with CRASHED_OOM.",
    "[REMEDIATION_SUCCESS] Arnold tile-render switch on node-04 for VFX_BATTLE_014. VRAM stabilized."
  ]
}
```

### GET /cluster/nodes — Response Schema
```json
{
  "node-01": { "engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 6.5, "vram_total_gb": 12 },
  "node-02": { "engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 7.0, "vram_total_gb": 12 },
  "node-03": { "engine": "Blender", "vgpu_profile": "GRID_RTX6000-24Q", "status": "HEALTHY", "vram_used_gb": 14.0, "vram_total_gb": 24 },
  "node-04": { "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "status": "CRASHED_OOM", "vram_used_gb": 24.0, "vram_total_gb": 24 },
  "node-05": { "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.5, "vram_total_gb": 12 },
  "node-06": { "engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.1, "vram_total_gb": 12 }
}
```

---

## 2. Telemetry Wire Formats

### Prometheus Exposition Format (GET :8000/metrics)
```
# HELP gpu_memory_used_bytes GPU VRAM memory used in bytes
# TYPE gpu_memory_used_bytes gauge
gpu_memory_used_bytes{node_id="node-01",engine="Blender"} 6979321856
gpu_memory_used_bytes{node_id="node-04",engine="Unreal Engine"} 25769803776

# HELP gpu_memory_total_bytes GPU VRAM total capacity in bytes
# TYPE gpu_memory_total_bytes gauge
gpu_memory_total_bytes{node_id="node-01",engine="Blender"} 12884901888
gpu_memory_total_bytes{node_id="node-04",engine="Unreal Engine"} 25769803776

# HELP node_status Node operational status (1=HEALTHY, 0=CRASHED_OOM)
# TYPE node_status gauge
node_status{node_id="node-01",status="HEALTHY"} 1
node_status{node_id="node-04",status="CRASHED_OOM"} 0
```

### Loki Push Payload (POST to Loki /loki/api/v1/push)
```json
{
  "streams": [
    {
      "stream": {
        "job": "render_cluster",
        "node_id": "node-04",
        "engine": "Unreal Engine",
        "level": "CRITICAL"
      },
      "values": [
        ["1772771463000000000", "[CUDA] CRITICAL: CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on node-04. Process terminated. Exit code 1."]
      ]
    }
  ]
}
```

---

## 3. Gemini Function Definitions (Tool Schemas)

### query_grafana_metrics
```python
def query_grafana_metrics(query: str, time_range: str = "last-15m") -> str:
    """
    Retrieves real-time GPU memory utilization and node status from the
    Prometheus-compatible cluster metrics endpoint.
    Args:
        query: PromQL-style query string or node filter
        time_range: Time window (default: last-15m)
    Returns:
        str: Formatted metrics summary for all matching nodes
    """
```

### search_grafana_logs
```python
def search_grafana_logs(
    logql: str = '{job="render_cluster"}',
    limit: int = 50
) -> str:
    """
    Queries Grafana Loki for render cluster log events matching a LogQL expression.
    Args:
        logql: LogQL stream selector and filter expression
        limit: Maximum number of log lines to return
    Returns:
        str: Formatted log entries with timestamps and labels
    """
```

### remediate_render_node
```python
def remediate_render_node(node_id: str, action: str, shot_id: str) -> str:
    """
    Executes a targeted SRE remediation action on the specified render node.
    Args:
        node_id: Target node identifier (e.g., "node-04")
        action: Remediation action: switch_to_tiled | process_restart | reboot_hypervisor
        shot_id: VFX shot identifier currently assigned to the node
    Returns:
        str: Confirmation message with new node state
    """
```
