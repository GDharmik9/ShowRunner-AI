# ShowRunner AI — Studio Command Center (Frontend)

## 1. Technology Stack
| Technology | Purpose | Version |
|:---|:---|:---|
| React 18 | UI framework | 18.x |
| Vite | Build tool & dev server | 5.x |
| Tailwind CSS | Utility-first styling | 3.x |
| Lucide React | Icon system | Latest |
| Fetch API | REST communication to FastAPI | Native |

## 2. Component Hierarchy
```
<App>
  └── <StudioCommandCenter>
        ├── Header Bar
        │     ├── ShowRunner AI Logo + Title
        │     └── Cluster Health Summary (X/6 nodes healthy)
        ├── NodeGrid (6 GPU Worker Cards)
        │     ├── Node ID + Engine Badge (Blender / Unreal Engine)
        │     ├── vGPU Profile Label
        │     ├── VRAM Utilization Progress Bar (color-coded)
        │     ├── VRAM Used / Total Label
        │     └── Status Badge (HEALTHY=green / CRASHED_OOM=red)
        ├── Incident Resolution Timeline
        │     └── Append-only event log with timestamps and badges
        ├── Observability Pane
        │     ├── Loki Log Stream (last 20 raw log lines)
        │     └── Prometheus Metrics Summary
        └── Director Console
              ├── Preset Quick-Action Buttons
              ├── Custom Text Prompt Input
              ├── Submit Button
              └── Agent Response Markdown Renderer
```

## 3. UI State Transitions
| Node State | Visual Treatment | VRAM Bar Color |
|:---|:---|:---|
| HEALTHY | Green border, emerald pulse dot | Blue → Green gradient |
| CRASHED_OOM | Red border, amber alert icon | Red, saturated at 100% |
| Remediation In Progress | Yellow glow, spinner overlay | Animated transition |
| Remediation Complete | Green flash, REMEDIATION_SUCCESS badge | Drops to 55% (13.2 GB) |

## 4. Key API Integrations
```javascript
const API_BASE = "http://127.0.0.1:5000";

// Poll cluster state every 5 seconds
const fetchClusterState = async () => {
  const res = await fetch(`${API_BASE}/cluster/nodes`);
  const data = await res.json();
  setNodes(data);
};

// Submit agent prompt
const sendPrompt = async (prompt) => {
  setLoading(true);
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt })
  });
  const result = await res.json();
  setAgentLog(prev => [...prev, result.agent_response]);
  fetchClusterState(); // Refresh nodes after remediation
  setLoading(false);
};

// Chaos injection
const triggerCrash = () =>
  fetch(`http://127.0.0.1:8000/simulate/crash`, { method: "POST" })
    .then(() => fetchClusterState());
```

## 5. Startup
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```
