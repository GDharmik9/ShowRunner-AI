# ShowRunner AI — Grafana Cloud & Observability Architecture

## 1. Observability Stack
| Component | Role |
|:---|:---|
| Grafana Loki | Aggregates structured log streams from all 6 render workers |
| Grafana Prometheus | Scrapes and stores GPU memory utilization and node availability time-series |
| Grafana Dashboards | Visualization layer for ops team and live demo |

## 2. Grafana Cloud Endpoints
| Resource | Value |
|:---|:---|
| Base Grafana URL | `https://happycurlew3577.grafana.net` |
| Loki Push URL | `https://logs-prod-028.grafana.net/loki/api/v1/push` |
| Loki User ID | `1777022` |
| Auth Scheme | HTTP Basic Auth (User ID + Cloud Access Policy Token) |

## 3. Access Policy Setup (Required for Log Push)
> Standard Service Account tokens (`glsa_...`) only permit dashboard access.
> Log ingestion requires a **Cloud Access Policy** token (`glc_...`).

1. Navigate to **Administration → Users and access → Cloud access policies**
2. Create policy: `showrunner-ingest-policy`
3. Scopes: `logs:write` + `metrics:write`
4. Add token: `showrunner-loki-token`
5. Copy the generated `glc_...` token → set as `LOKI_INGESTION_TOKEN`

## 4. Loki JSON Ingestion Payload
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
        ["1772771463000000000", "CRITICAL: [CUDA] CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on node-04. Exit code 1."]
      ]
    }
  ]
}
```

## 5. Prometheus Metrics Served by Emitter
`http://localhost:8000/metrics`

| Metric Name | Type | Labels |
|:---|:---|:---|
| `gpu_memory_used_bytes` | Gauge | `node_id`, `engine` |
| `gpu_memory_total_bytes` | Gauge | `node_id`, `engine` |
| `node_status` | Gauge | `node_id`, `status` (1=HEALTHY, 0=CRASHED_OOM) |

## 6. Operational Queries

### PromQL Dashboard Queries
```promql
# Overall VRAM Utilization %
(sum(gpu_memory_used_bytes) / sum(gpu_memory_total_bytes)) * 100

# Nodes currently crashed
node_status == 0

# Per-node VRAM in GB
gpu_memory_used_bytes / 1073741824
```

### LogQL Investigation Queries
```logql
# All CUDA OOM errors
{job="render_cluster"} |= "CUDA_ERROR_OUT_OF_MEMORY"

# Node-04 critical events
{job="render_cluster", node_id="node-04"} |~ "(?i)critical|oom|fail"

# Last 50 errors across cluster
{job="render_cluster"} | level="CRITICAL" | limit 50
```
