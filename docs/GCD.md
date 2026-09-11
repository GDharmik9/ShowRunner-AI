# ShowRunner AI — Google Cloud Deployment & Vertex AI (GCD)

## 1. Overview
ShowRunner AI runs its cognitive reasoning on Google Cloud Vertex AI using Gemini 2.5 Flash.
Authentication uses Application Default Credentials (ADC) to comply with GCP organization policies
that prohibit static API key generation.

## 2. Cloud Identity & Project
| Field | Value |
|:---|:---|
| Project ID | `stadiumflow-504913` |
| Region | `us-central1` |
| Service Account | `showrunner-agent-sa` |
| SA Email | `showrunner-agent-sa@stadiumflow-504913.iam.gserviceaccount.com` |

## 3. Required IAM Roles
| Role | Identifier | Purpose |
|:---|:---|:---|
| Vertex AI User | `roles/aiplatform.user` | Invoke Gemini models on Vertex AI |
| Service Usage Consumer | `roles/serviceusage.serviceUsageConsumer` | API quota consumption |

## 4. CLI Provisioning
```bash
gcloud config set project stadiumflow-504913

gcloud iam service-accounts create showrunner-agent-sa \
    --display-name="ShowRunner AI Technical Director Agent"

gcloud projects add-iam-policy-binding stadiumflow-504913 \
    --member="serviceAccount:showrunner-agent-sa@stadiumflow-504913.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding stadiumflow-504913 \
    --member="serviceAccount:showrunner-agent-sa@stadiumflow-504913.iam.gserviceaccount.com" \
    --role="roles/serviceusage.serviceUsageConsumer"
```

## 5. SDK Initialization (agent_service.py)
```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="stadiumflow-504913",
    location="us-central1"
)

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[query_grafana_metrics, search_grafana_logs, remediate_render_node],
    temperature=0.2
)
```

## 6. Cloud Run Deployment

### Frontend-only deployment

The backend is already deployed separately as `showrunner-backend`. For frontend
changes, deploy only the `frontend/` directory to the existing `showrunner-ai`
Cloud Run service:

```bash
cd frontend
gcloud run deploy showrunner-ai \
    --source . \
    --region us-central1 \
    --allow-unauthenticated
cd ..
```

This uses `frontend/Dockerfile`, builds the React application, and serves it as
a static site. It does not redeploy or modify `showrunner-backend`.

Open the URL printed by Cloud Run and verify the dashboard loads. The current
dashboard demo actions use local UI state; backend API wiring can be connected
separately when needed.

The root `Dockerfile` builds the Vite frontend and copies `frontend/dist` into
the FastAPI image. `agent_service.py` serves that build at `/`, while the API
remains available under `/agent/*` and `/cluster/*`. Deploy the root directory,
not `frontend/` by itself.

Build and test the frontend before deploying:
```bash
cd frontend
npm ci
npm run lint
npm run build
cd ..
```

Deploy the combined service:
```bash
gcloud run deploy showrunner-backend \
    --source . \
    --region us-central1 \
    --service-account showrunner-agent-sa@stadiumflow-504913.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=stadiumflow-504913,GOOGLE_CLOUD_LOCATION=us-central1
```

After deployment, open the URL printed by Cloud Run. Verify both paths:
* `/` loads the Studio Command Center.
* `/docs` loads the FastAPI documentation.
* `/cluster/nodes` returns the backend cluster state.

When only the frontend changes, repeat the same deployment. Cloud Run rebuilds
the image and replaces the currently running revision with the new frontend.

## 7. Local ADC Setup
```bash
gcloud auth application-default login
# Credentials stored at: %APPDATA%\gcloud\application_default_credentials.json
```
