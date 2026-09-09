"""
Showrunner AI Agent Service (agent_service.py)
Backend orchestration service connecting Google Gemini to Grafana Cloud and the studio queue manager.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("showrunner-agent")

# Attempt Google GenAI SDK imports
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

app = FastAPI(
    title="Showrunner AI Backend Orchestrator",
    description="Agentic Cinema Technical Director backend orchestrating Gemini, Grafana, and render farm nodes.",
    version="1.0.0"
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------------
# IN-MEMORY CLUSTER STATE
# -------------------------------------------------------------------------
CLUSTER_STATE = {
    "node-01": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 6.5, "vram_total_gb": 12.0},
    "node-02": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 7.0, "vram_total_gb": 12.0},
    "node-03": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-24Q", "status": "HEALTHY", "vram_used_gb": 14.0, "vram_total_gb": 24.0},
    "node-04": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "status": "CRASHED_OOM", "vram_used_gb": 24.0, "vram_total_gb": 24.0},
    "node-05": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.5, "vram_total_gb": 12.0},
    "node-06": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.1, "vram_total_gb": 12.0},
}

RESOLUTION_EVENTS: List[str] = [
    "[SYSTEM] Cluster simulation online. Node 4 pre-loaded with CRASHED_OOM."
]

GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "stadiumflow-504913")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


# -------------------------------------------------------------------------
# OBSERVABILITY & REMEDIATION TOOLS
# -------------------------------------------------------------------------

def query_grafana_metrics(query: str = "node_status", time_range: str = "last-15m") -> str:
    """Queries Prometheus metrics to detect GPU utilization spikes and status drops."""
    logger.info(f"Tool Executing: query_grafana_metrics('{query}', '{time_range}')")
    lines = []
    for node, data in CLUSTER_STATE.items():
        lines.append(f'gpu_memory_used_bytes{{node_id="{node}",engine="{data["engine"]}"}} {int(data["vram_used_gb"] * 1024**3)}')
        lines.append(f'gpu_memory_total_bytes{{node_id="{node}",engine="{data["engine"]}"}} {int(data["vram_total_gb"] * 1024**3)}')
        status_val = 1 if data["status"] == "HEALTHY" else 0
        lines.append(f'node_status{{node_id="{node}",status="{data["status"]}"}} {status_val}')
    return "\n".join(lines)


def search_grafana_logs(logql: str = '{job="render_cluster"}', limit: int = 50) -> str:
    """Queries Loki logs using LogQL to find CUDA tracebacks and allocation failures."""
    logger.info(f"Tool Executing: search_grafana_logs('{logql}', limit={limit})")
    logs = [
        "2026-09-05T20:30:12Z [INFO] node-01 Blender: Render completed frame 124 successfully on Blender.",
        "2026-09-05T20:31:01Z [WARN] node-04 Unreal Engine: Host Virtual Memory spike detected. Total allocation > 90%.",
        "2026-09-05T20:31:03Z [CRITICAL] node-04 Unreal Engine: CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4.",
        "2026-09-05T20:31:04Z [CRITICAL] node-04 Unreal Engine: Process terminated with exit code 1. VRAM saturated."
    ]
    if "OOM" in logql or "CUDA" in logql or "node-04" in logql:
        return "\n".join([log for log in logs if "CUDA" in log or "OOM" in log or "CRITICAL" in log])
    return "\n".join(logs[:limit])


def remediate_render_node(node_id: str, action: str, shot_id: str) -> str:
    """Triggers automated remediation routines on a targeted render worker node."""
    logger.info(f"Tool Executing: remediate_render_node('{node_id}', '{action}', '{shot_id}')")
    if node_id not in CLUSTER_STATE:
        return f"Execution Error: Node '{node_id}' does not exist in active cluster inventory."

    node = CLUSTER_STATE[node_id]
    if action in ("reboot_hypervisor", "process_restart"):
        old_status = node["status"]
        node["status"] = "HEALTHY"
        node["vram_used_gb"] = round(node["vram_total_gb"] * 0.4, 1)
        event_msg = f"[REMEDIATION_SUCCESS] Executed '{action}' on {node_id} for shot {shot_id}. Status: {old_status} -> HEALTHY."
        RESOLUTION_EVENTS.append(event_msg)
        return event_msg
    elif action == "switch_to_tiled":
        node["vram_used_gb"] = round(node["vram_total_gb"] * 0.55, 1)
        node["status"] = "HEALTHY"
        event_msg = f"[REMEDIATION_SUCCESS] Configured Arnold tile-render switch on {node_id} for shot {shot_id}. VRAM footprint stabilized."
        RESOLUTION_EVENTS.append(event_msg)
        return event_msg
    else:
        return f"Unknown remediation action '{action}' specified."


# -------------------------------------------------------------------------
# PROMPT DEFINITIONS & SCHEMAS
# -------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are the 'Showrunner AI Technical Director', an expert autonomous guardian of visual effects render farm infrastructure.
Your mission is to monitor, diagnose, and remediate failures on our simulated GPU nodes using the provided tools.

CRITICAL OPERATIONAL RULES:
1. Grounding and Correlation Prerequisite:
   Before recommending or executing any remediation, you MUST correlate Prometheus metric spikes with Grafana Loki error logs.
   If a node reports a health drop (via query_grafana_metrics), actively search Loki (via search_grafana_logs) for the explicit error signature.
   Do NOT reboot nodes based on metrics alone. Confirm the error through corresponding logs first.

2. Remediation Routing:
   - For severe CUDA Out-of-Memory (OOM) failures, execute 'switch_to_tiled' to reduce VRAM pressure, or 'reboot_hypervisor' if crashed completely.
   - For locked or hung tasks (deadlocks), execute 'process_restart'.

3. Verification:
   After running a remediation tool, clearly summarize the result, the previous failed state, and verify the node has returned to healthy operations.
"""

class UserMessage(BaseModel):
    message: Optional[str] = None
    prompt: Optional[str] = None

    def get_query(self) -> str:
        return self.message or self.prompt or "Audit cluster health"


def handle_mock_chat_flow(query_text: str) -> Dict[str, Any]:
    text_upper = query_text.upper()
    query_grafana_metrics("node_status")

    if any(k in text_upper for k in ["REMEDIATE", "FIX", "OOM", "NODE-04", "NODE 4", "AUDIT", "FAIL"]):
        search_grafana_logs('{node_id="node-04"}')
        remediate_render_node("node-04", "switch_to_tiled", "VFX_BATTLE_014")
        agent_text = (
            "### Showrunner AI Technical Director Report\n\n"
            "**1. Telemetry Ingested:**\n"
            "- Prometheus showed `node_status` on `node-04` at **0** (CRASHED_OOM).\n"
            "- Correlated with Loki Log stream: `CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4`.\n\n"
            "**2. Automated Action Taken:**\n"
            "- Successfully called `remediate_render_node` with action `switch_to_tiled` for **VFX_BATTLE_014**.\n\n"
            "**3. Node Restored:**\n"
            "- Target node `node-04` VRAM consumption scaled back. Status has returned to **HEALTHY**."
        )
        return {
            "status": "success",
            "agent_response": agent_text,
            "resolution_events": RESOLUTION_EVENTS
        }

    return {
        "status": "success",
        "agent_response": (
            "### Showrunner AI System Check\n\n"
            "Cluster telemetry evaluated. All nodes are operating normally.\n"
            f"Active system events logged:\n{chr(10).join(RESOLUTION_EVENTS)}"
        ),
        "resolution_events": RESOLUTION_EVENTS
    }


# -------------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------------

@app.post("/agent/chat")
async def handle_agent_turn(user_payload: UserMessage):
    query_text = user_payload.get_query()

    if not genai or not hasattr(genai, "Client"):
        logger.warning("Google GenAI SDK unavailable. Utilizing local solver.")
        return handle_mock_chat_flow(query_text)

    try:
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION,
        )

        tools_list = [query_grafana_metrics, search_grafana_logs, remediate_render_node]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools_list,
            temperature=0.2,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query_text,
            config=config,
        )

        chat_history = [
            types.Content(role="user", parts=[types.Part.from_text(text=query_text)]),
            response.candidates[0].content,
        ]

        max_turns = 5
        current_turn = 0

        while response.function_calls and current_turn < max_turns:
            current_turn += 1
            tool_responses = []

            for call in response.function_calls:
                t_name = call.name
                t_args = call.args or {}
                logger.info(f"Gemini invoked tool: {t_name} with args {t_args}")

                if t_name == "query_grafana_metrics":
                    result = query_grafana_metrics(**t_args)
                elif t_name == "search_grafana_logs":
                    result = search_grafana_logs(**t_args)
                elif t_name == "remediate_render_node":
                    result = remediate_render_node(**t_args)
                else:
                    result = f"Error: Tool '{t_name}' is not registered."

                tool_responses.append(
                    types.Part.from_function_response(
                        name=t_name,
                        response={"result": result},
                    )
                )

            chat_history.append(types.Content(role="tool", parts=tool_responses))
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=chat_history,
                config=config,
            )
            chat_history.append(response.candidates[0].content)

        final_text = response.text if response.text else "Investigation completed."
        return {
            "status": "success",
            "agent_response": final_text,
            "resolution_events": RESOLUTION_EVENTS,
        }

    except Exception as err:
        logger.warning(f"Vertex AI turn failed ({err}). Falling back to deterministic solver.")
        return handle_mock_chat_flow(query_text)


@app.get("/cluster/nodes")
def get_cluster_nodes():
    return CLUSTER_STATE


@app.get("/cluster/events")
def get_resolution_events():
    return {"events": RESOLUTION_EVENTS}


# -------------------------------------------------------------------------
# FRONTEND STATIC FILES (Must be placed AFTER all API endpoints)
# -------------------------------------------------------------------------
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {
            "service": "Showrunner AI Technical Director",
            "status": "online",
            "docs": "/docs",
            "cluster_state": "/cluster/nodes"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)