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

## 6. Cloud Run Deployment (Future State)
```bash
gcloud run deploy showrunner-backend \
    --source . \
    --region us-central1 \
    --service-account showrunner-agent-sa@stadiumflow-504913.iam.gserviceaccount.com \
    --allow-unauthenticated \
    --set-env-vars GOOGLE_CLOUD_PROJECT=stadiumflow-504913,GOOGLE_CLOUD_LOCATION=us-central1
```

## 7. Local ADC Setup
```bash
gcloud auth application-default login
# Credentials stored at: %APPDATA%\gcloud\application_default_credentials.json
```
