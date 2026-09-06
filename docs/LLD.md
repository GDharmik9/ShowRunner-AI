# Low-Level Design

# ShowRunner AI — Low-Level Design (LLD)

## 1. Component Class & Module Architecture

### 1.1 `telemetry_emitter.py`
The telemetry emitter simulates a real-world multi-node production rendering cluster with independent thread pools for simulation ticks, Prometheus scraping, and CLI control.

- **Class `VFXClusterSimulator`**:
  - `__init__(tick_interval, loki_url, loki_user, loki_token)`: Initializes cluster nodes, memory profiles, locks, and Loki Basic Auth headers.
  - `update_simulation()`: Iterates through active nodes. Calculates synthetic GPU/CPU utilization, updates frame counts, allocates VRAM, and generates structured log lines.
  - `trigger_oom_crash()`: Sets `node-04` state to `CRASHED_OOM`, saturates VRAM to 100% (24.0 GB), drops GPU utilization to 0%, and logs critical CUDA errors.
  - `recover_all()`: Resets all failed nodes to `HEALTHY` and restores baseline memory usage (45%).
  - `get_prometheus_metrics() -> str`: Formats gauges in Prometheus 0.0.4 exposition format.
  - `push_to_loki(raw_logs)`: Batches log records with nanosecond timestamps (`time.time_ns()`) and sends HTTP POST to Loki ingestion API with Basic Auth (`Authorization: Basic <base64(user:token)>`).

- **Class `CombinedHTTPHandler(http.server.BaseHTTPRequestHandler)`**:
  - `do_GET()`: Routes `/metrics` to Prometheus generator and root status.
  - `do_POST()`: Exposes remote control webhooks `/simulate/crash` and `/simulate/recover`.

---

### 1.2 `agent_service.py`
FastAPI service orchestrating the multi-turn Gemini reasoning and tool execution loop.

- **Pydantic Model `UserMessage`**:
  ```python
  class UserMessage(BaseModel):
      message: Optional[str] = None
      prompt: Optional[str] = None
      def get_query(self) -> str:
          return self.message or self.prompt or "Audit cluster health"

   ```
Design Rationale: Accommodates both React frontend payloads (message), Swagger UI payloads (prompt), and PowerShell/cURL commands without 422 validation errors.

---

### 1.3 In-Memory Cluster State Store (CLUSTER_STATE):
```python
   CLUSTER_STATE = {
    "node-01": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 6.5, "vram_total_gb": 12},
    "node-02": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 7.0, "vram_total_gb": 12},
    "node-03": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-24Q", "status": "HEALTHY", "vram_used_gb": 14.0, "vram_total_gb": 24},
    "node-04": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "status": "CRASHED_OOM", "vram_used_gb": 24.0, "vram_total_gb": 24},
    "node-05": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.5, "vram_total_gb": 12},
    "node-06": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.1, "vram_total_gb": 12}
}
```

## 2. Gemini Function Calling Engine
The agent leverages Gemini's native tool invocation using the Google GenAI SDK (google-genai).

### Registered Tools:
### 1. `query_grafana_metrics(query: str, time_range: str = "last-15m") -> str`
 - Scrapes real-time node memory utilization and status flags across all 6 virtual workers.
### 2. `search_grafana_logs(logql: str = '{job="render_cluster"}', limit: int = 50) -> str`
 - Queries Loki log streams to extract critical error patterns, stack traces, and exit codes.
### 3. `remediate_render_node(node_id: str, action: str, shot_id: str) -> str`
   -  Supported actions:
      -  `switch_to_tiled`: Switches the renderer to sub-tile memory buffers. Drops VRAM from 100% to 55% (13.2 GB) and marks node as HEALTHY.
      -  `process_restart`: Kills deadlocked process. Resets VRAM to 40% (9.6 GB) and marks node as HEALTHY.
      - `reboot_hypervisor`: Complete host restart.

### Multi-Turn Agent Resolution Loop:
 ```python
     max_turns = 5
     current_turn = 0
    while response.function_calls and current_turn < max_turns:
        current_turn += 1
        tool_responses = []
        for call in response.function_calls:
            t_name = call.name
            t_args = call.args or {}
            # Dispatch to matching Python function
            result = execute_tool(t_name, t_args)
            tool_responses.append(
            types.Part.from_function_response(name=t_name, response={"result": result})
        )
        chat_history.append(types.Content(role="tool", parts=tool_responses))
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=chat_history,
        config=config
    )
```
---

## 3. Error Handling & Robustness Matrix

| Failure Scenario | Detection | Resolution |
|:---|:---|:---|
| Port 8080 collision on Windows | `[WinError 10013]` socket error | Backend moved to port 5000, bound to 127.0.0.1 |
| String parameter type collision | `AttributeError: 'str' object has no attribute 'message'` | UserMessage.get_query() handles polymorphic input |
| Google API Key blocked by org policy | API key creation denied | Switched to `genai.Client(vertexai=True)` with ADC |
| Loki HTTP 401 Unauthorized | Grafana Cloud rejection | Cloud Access Policy token with `logs:write` scope |
| External Network Outage | Exception in agent turn | Fallback to deterministic SRE engine |


