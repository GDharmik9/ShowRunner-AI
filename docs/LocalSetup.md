# ShowRunner AI — Local Development & Runbook

## 1. Prerequisites
| Requirement | Minimum Version |
|:---|:---|
| Python | 3.10+ |
| Node.js + npm | 18.0.0+ |
| Google Cloud SDK (gcloud) | Latest |
| Grafana Cloud Account | Free or Pro tier |

## 2. Environment Variables (.env)
Create `.env` in the project root:
```ini
# Google Cloud Vertex AI
GOOGLE_CLOUD_PROJECT="stadiumflow-504913"
GOOGLE_CLOUD_LOCATION="us-central1"

# Grafana Cloud
GRAFANA_BASE_URL="https://happycurlew3577.grafana.net"
GRAFANA_SERVICE_ACCOUNT_TOKEN="glsa_your_service_account_token"
LOKI_PUSH_URL="https://logs-prod-028.grafana.net/loki/api/v1/push"
LOKI_USER_ID="1777022"
LOKI_INGESTION_TOKEN="glc_your_cloud_access_policy_token"

# Ports
PORT=8000
BACKEND_PORT=5000
```

## 3. Python Virtual Environment
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# macOS/Linux:
source venv/bin/activate

pip install --upgrade pip
pip install fastapi uvicorn google-genai httpx requests pydantic
```

## 4. Google Cloud ADC Authentication
```bash
gcloud auth application-default login
gcloud config set project stadiumflow-504913
```

## 5. Frontend Setup
```bash
cd frontend
npm install
npm install lucide-react
npm install -D tailwindcss@3 postcss autoprefixer
npx tailwindcss init -p
```
Verify `frontend/src/StudioCommandCenter.jsx` API base is `http://127.0.0.1:5000`.

## 6. 3-Terminal Execution Sequence

### Terminal 1 — Telemetry Emitter (Port 8000)
```bash
python telemetry_emitter.py \
  --port 8000 \
  --loki-url "https://logs-prod-028.grafana.net/loki/api/v1/push" \
  --loki-user "1777022" \
  --token "glc_your_cloud_access_policy_token"
```
Available CLI: `status`, `crash`, `recover`, `exit`

### Terminal 2 — Agent Orchestrator (Port 5000)
```bash
uvicorn agent_service:app --host 127.0.0.1 --port 5000 --reload
```
Swagger UI: `http://127.0.0.1:5000/docs`

### Terminal 3 — Studio Command Center (Port 5173)
```bash
cd frontend && npm run dev
```
UI: `http://localhost:5173`

## 7. Verification Tests

### PowerShell API Test
```powershell
$body = @{
  prompt = "Node 4 has crashed with OOM. Correlate Prometheus metrics with Loki logs, execute remediation on node-04 and stabilize VRAM."
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:5000/agent/chat" -Method Post -ContentType "application/json" -Body $body
```

### Chaos Injection Test
1. Check `http://127.0.0.1:5000/cluster/nodes` → node-04: `CRASHED_OOM`, `vram_used_gb: 24.0`
2. Submit remediation prompt to `/agent/chat`
3. Re-check `/cluster/nodes` → node-04: `HEALTHY`, `vram_used_gb: 13.2`
