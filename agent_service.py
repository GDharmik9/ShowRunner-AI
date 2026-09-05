"""
Showrunner AI Agent Service (agent_service.py)
Backend orchestration service connecting Google Gemini to Grafana Cloud and the studio queue manager.
"""

import os
import logging
import httpx
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Try to import google-genai, fall back to a mock or raise for structural clarity
try:
    from google import genai
    from google.genai import types
except ImportError:
    # Fallback to structural mocks to allow the code to run/validate without errors if SDK is missing in local runtime
    class MockTypes:
        class GenerateContentConfig:
            def __init__(self, **kwargs):
                self.__dict__.update(kwargs)
    class MockGenAI:
        class Client:
            def __init__(self, **kwargs):
                pass
    genai = MockGenAI()
    types = MockTypes()

# Initialize Logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("showrunner-agent")

app = FastAPI(
    title="Showrunner AI Backend Orchestrator",
    description="Agentic Cinema Technical Director backend orchestrating Gemini, Grafana, and render farm nodes.",
    version="1.0.0"
)

# -------------------------------------------------------------------------
# IN-MEMORY CLUSTER STATE (Mimicking telemetry_emitter.py nodes)
# -------------------------------------------------------------------------
CLUSTER_STATE = {
    "node-01": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 6.5, "vram_total_gb": 12.0},
    "node-02": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 7.0, "vram_total_gb": 12.0},
    "node-03": {"engine": "Blender", "vgpu_profile": "GRID_RTX6000-24Q", "status": "HEALTHY", "vram_used_gb": 14.0, "vram_total_gb": 24.0},
    "node-04": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-24Q", "status": "CRASHED_OOM", "vram_used_gb": 24.0, "vram_total_gb": 24.0},
    "node-05": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.5, "vram_total_gb": 12.0},
    "node-06": {"engine": "Unreal Engine", "vgpu_profile": "GRID_RTX6000-12Q", "status": "HEALTHY", "vram_used_gb": 8.1, "vram_total_gb": 12.0},
}

# In-memory mock log list for append-only log capture
RESOLUTION_EVENTS: List[str] = [
    "[SYSTEM] Cluster simulation online. Node 4 pre-loaded with CRASHED_OOM."
]

# Grafana Credentials (Environment Variables)
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_TOKEN = os.getenv("GRAFANA_TOKEN", "mock-service-account-token")
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")
PROM_URL = os.getenv("PROM_URL", "http://localhost:8000")  # From telemetry_emitter.py


# -------------------------------------------------------------------------
# NATIVE PYTHON TOOLS FOR GEMINI
# -------------------------------------------------------------------------

def query_grafana_metrics(query: str, time_range: str = "last-15m") -> str:
    """
    Queries active Prometheus time-series metrics from Grafana Cloud to detect GPU bottlenecks and spikes.
    
    Args:
        query: The exact PromQL statement to execute.
        time_range: The relative lookback window (e.g. 'last-15m', 'last-1h').
    """
    logger.info(f"Tool Executing: query_grafana_metrics('{query}', '{time_range}')")
    
    # In a real environment, this connects to the Grafana Cloud Prometheus HTTP API
    # Since we have a mock local state, we can simulate responses or query local telemetry_emitter if online
    try:
        # Simple local fetch helper (non-blocking mock fallback)
        endpoint = f"{PROM_URL}/metrics" if "localhost" in PROM_URL else f"{GRAFANA_URL}/api/datasources/proxy/1/api/v1/query"
        logger.info(f"Targeting Metrics endpoint: {endpoint}")
        
        # Simulating returns based on current in-memory cluster state
        lines = []
        for node, data in CLUSTER_STATE.items():
            lines.append(f'gpu_memory_used_bytes{{node_id="{node}",engine="{data["engine"]}"}} {int(data["vram_used_gb"] * 1024**3)}')
            lines.append(f'gpu_memory_total_bytes{{node_id="{node}",engine="{data["engine"]}"}} {int(data["vram_total_gb"] * 1024**3)}')
            status_val = 1 if data["status"] == "HEALTHY" else 0
            lines.append(f'node_status{{node_id="{node}",status="{data["status"]}"}} {status_val}')
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Metrics query failed: {e}")
        return f"Error fetching metrics from Prometheus: {str(e)}"


def search_grafana_logs(logql: str, limit: int = 50) -> str:
    """
    Queries logs from Grafana Cloud Loki using LogQL to find error logs, CUDA tracebacks, or storage failures.
    
    Args:
        logql: The standard LogQL syntax query string.
        limit: Max number of log lines to retrieve.
    """
    logger.info(f"Tool Executing: search_grafana_logs('{logql}', limit={limit})")
    
    # Return mock or real historical trace logs based on current cluster failures
    logs = [
        "2026-09-04T23:14:12Z [INFO] node-01 Maya 2020: Render completed frame 124 successfully on Blender.",
        "2026-09-04T23:15:01Z [WARN] node-04 Unreal Engine: Host Virtual Memory spike detected. Total allocation > 85%.",
        "2026-09-04T23:15:03Z [CRITICAL] node-04 Unreal Engine: CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4.",
        "2026-09-04T23:15:04Z [CRITICAL] node-04 Unreal Engine: Process terminated with exit code 1. VRAM saturated."
    ]
    
    # Filter logs if logql specifies specific strings
    if "OOM" in logql or "CUDA" in logql:
        return "\n".join([log for log in logs if "CUDA" in log or "OOM" in log or "CRITICAL" in log])
    return "\n".join(logs[:limit])


def remediate_render_node(node_id: str, action: str, shot_id: str) -> str:
    """
    Triggers automated remediation routines on a targeted render worker node.
    
    Args:
        node_id: The identifier of the target worker node (e.g., 'node-04').
        action: The remediation path to take (e.g., 'reboot_hypervisor', 'process_restart', 'switch_to_tiled').
        shot_id: The ID of the visual effects shot experiencing issues.
    """
    logger.info(f"Tool Executing: remediate_render_node('{node_id}', '{action}', '{shot_id}')")
    
    if node_id not in CLUSTER_STATE:
        return f"Execution Error: Node '{node_id}' does not exist in active cluster inventory."
    
    node = CLUSTER_STATE[node_id]
    
    if action == "reboot_hypervisor" or action == "process_restart":
        old_status = node["status"]
        node["status"] = "HEALTHY"
        # Reduce memory utilization down to base usage post-restart
        node["vram_used_gb"] = round(node["vram_total_gb"] * 0.4, 1)
        
        event_msg = f"[REMEDIATION_SUCCESS] Executed '{action}' on {node_id} for shot {shot_id}. Status transitioned from {old_status} -> HEALTHY."
        RESOLUTION_EVENTS.append(event_msg)
        logger.info(event_msg)
        return event_msg
        
    elif action == "switch_to_tiled":
        node["vram_used_gb"] = round(node["vram_total_gb"] * 0.55, 1) # Tiling reduces memory pressure
        node["status"] = "HEALTHY"
        
        event_msg = f"[REMEDIATION_SUCCESS] Configured Arnold tile-render switch on {node_id} for shot {shot_id}. VRAM footprint stabilized."
        RESOLUTION_EVENTS.append(event_msg)
        logger.info(event_msg)
        return event_msg
        
    else:
        return f"Unknown remediation action '{action}' specified."


# -------------------------------------------------------------------------
# GEMINI ORCHESTRATOR LOOP
# -------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are the 'Showrunner AI Technical Director', an expert autonomous guardian of visual effects render farm infrastructure.
Your mission is to monitor, diagnose, and remediate failures on our simulated GPU nodes using the provided tools.

CRITICAL OPERATIONAL RULES:
1. Grounding and Correlation Prerequisite:
   Before recommending or executing any remediation, you MUST correlate Prometheus metric spikes with Grafana Loki error logs.
   For example, if a node reports a health status drop (via query_grafana_metrics), you must actively search Loki (via search_grafana_logs) to find the explicit error signature (such as a CUDA OOM crash) matching that timeline.
   Do NOT reboot or reconfigure nodes based on metrics alone. Confirm the crash or lockup through corresponding logs first!

2. Remediation Routing:
   - For severe CUDA Out-of-Memory (OOM) failures on a heavy rendering job (such as a hero shot), your best action is to execute 'switch_to_tiled' to reduce VRAM cache allocation, or trigger 'reboot_hypervisor' if the node has crashed completely.
   - For locked or hung tasks (such as deadlocks where CPU is at 100% but GPU flatlines), execute 'process_restart'.

3. Verification:
   After running a remediation tool, clearly summarize the result, the previous failed state, and verify the node has returned to healthy operations.
"""

class UserMessage(BaseModel):
    message: str

@app.post("/agent/chat")
async def handle_agent_turn(user_payload: UserMessage):
    """
    Main API endpoint for driving a Gemini Agent session. Coordinates the tool-calling loop.
    """
    if "genai" not in globals() or not hasattr(genai, "Client"):
        # Fallback response if Google GenAI SDK is not fully authenticated or available
        logger.warn("Google GenAI SDK not fully loaded. Running local mock solver...")
        return handle_mock_chat_flow(user_payload.message)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not configured.")

    try:
        # Initialize Gemini Client (New modern google-genai SDK layout)
        client = genai.Client(api_key=api_key)
        
        # Configure tool definitions list
        tools_list = [query_grafana_metrics, search_grafana_logs, remediate_render_node]
        
        # Build configuration payload
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=tools_list,
            temperature=0.2, # Lower temperature for stable, deterministic SRE tooling
        )
        
        # Call the model
        model_name = "gemini-2.5-flash"  # Highly responsive and supports robust function calling
        response = client.models.generate_content(
            model=model_name,
            contents=user_payload.message,
            config=config
        )
        
        # Execute tool loop if model returned tool/function calls
        chat_history = [
            types.Content(role="user", parts=[types.Part.from_text(text=user_payload.message)]),
            response.candidates[0].content
        ]
        
        # Limit tool execution turns to prevent infinite loops (Self-healing safety guard)
        max_turns = 5
        current_turn = 0
        
        while response.function_calls and current_turn < max_turns:
            current_turn += 1
            tool_responses = []
            
            for call in response.function_calls:
                tool_name = call.name
                tool_args = call.args
                
                logger.info(f"Gemini requested tool call: {tool_name} with arguments {tool_args}")
                
                # Dynamic Tool Router
                if tool_name == "query_grafana_metrics":
                    result = query_grafana_metrics(**tool_args)
                elif tool_name == "search_grafana_logs":
                    result = search_grafana_logs(**tool_args)
                elif tool_name == "remediate_render_node":
                    result = remediate_render_node(**tool_args)
                else:
                    result = f"Error: Tool '{tool_name}' is not registered."
                
                # Append Response part
                tool_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": result}
                    )
                )
            
            # Send the tool responses back to Gemini to complete the loop
            chat_history.append(types.Content(role="tool", parts=tool_responses))
            
            response = client.models.generate_content(
                model=model_name,
                contents=chat_history,
                config=config
            )
            chat_history.append(response.candidates[0].content)
            
        final_answer = response.text if response.text else "No textual response generated by the agent."
        return {
            "status": "success",
            "agent_response": final_answer,
            "resolution_events": RESOLUTION_EVENTS
        }

    except Exception as err:
        logger.error(f"Agent Loop Execution Error: {err}")
        raise HTTPException(status_code=500, detail=f"Orchestration failure: {str(err)}")


def handle_mock_chat_flow(message: str) -> Dict[str, Any]:
    """
    SRE fallback simulator that mimics the Showrunner AI Agent's evaluation loop in local test environments.
    """
    message_upper = message.upper()
    
    # 1. Trigger correlation checks
    metrics_log = query_grafana_metrics("node_status")
    
    if "REMEDIATE" in message_upper or "FIX" in message_upper or "OOM" in message_upper or "NODE-04" in message_upper:
        # Check Loki logs for correlation proof
        logs_log = search_grafana_logs('{container="unreal-worker"}')
        
        if "CUDA_ERROR_OUT_OF_MEMORY" in logs_log:
            # SRE Decision Engine correlates spikes and error logs
            result = remediate_render_node("node-04", "switch_to_tiled", "VFX_BATTLE_014")
            
            agent_text = (
                "### Showrunner AI Technical Director Report\n\n"
                "**1. Telemetry Ingested:**\n"
                "- Prometheus showed `node_status` on `node-04` at **0** (CRASHED_OOM).\n"
                "- Correlated with Loki Log stream: `CUDA_ERROR_OUT_OF_MEMORY: Shot VFX_BATTLE_014 failed on Node 4`.\n\n"
                "**2. Automated Action Taken:**\n"
                f"- Successfully called `remediate_render_node` with action `switch_to_tiled` for **VFX_BATTLE_014**.\n\n"
                "**3. Node Restored:**\n"
                "- Target node `node-04` VRAM consumption scaled back. Status has returned to **HEALTHY**."
            )
            return {
                "status": "success",
                "agent_response": agent_text,
                "resolution_events": RESOLUTION_EVENTS
            }
    
    # General Query fallback
    return {
        "status": "success",
        "agent_response": (
            "### Showrunner AI System Check\n\n"
            "I have evaluated the virtual cluster metrics. All nodes except `node-04` are executing workloads normally.\n"
            f"Active system events logged:\n{chr(10).join(RESOLUTION_EVENTS)}"
        ),
        "resolution_events": RESOLUTION_EVENTS
    }

# -------------------------------------------------------------------------
# DIRECT INVENTORIES & METRICS API (FastAPI standard endpoints)
# -------------------------------------------------------------------------

@app.get("/cluster/nodes")
def get_cluster_nodes():
    """Retrieve the live state of all nodes in the rendering cluster."""
    return CLUSTER_STATE

@app.get("/cluster/events")
def get_resolution_events():
    """Retrieve history of all auto-remediation actions."""
    return {"events": RESOLUTION_EVENTS}


if __name__ == "__main__":
    import uvicorn
    # Execute the FastAPI API directly for local verification and development
    logger.info("Starting local agent orchestration server...")
    uvicorn.run(app, host="0.0.0.0", port=5000)
