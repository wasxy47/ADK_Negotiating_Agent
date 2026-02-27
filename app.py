import os
import json
import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, List

from adk.engine import AgentState
from agents.discovery_agent import discovery_agent
from agents.negotiator_agent import negotiator_agent
from agents.inventory_agent import inventory_agent
from agents.order_agent import order_agent
from mcp_servers.catalog_server import CATALOG_DB

app = FastAPI(title="Autonomous Retail Store API")

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Map agent names to instances
AGENTS = {
    "Discovery": discovery_agent,
    "Negotiator": negotiator_agent,
    "Inventory": inventory_agent,
    "OrderTaking": order_agent
}

# In-memory session store
sessions: Dict[str, AgentState] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_event(self, session_id: str, event_type: str, payload: Any, agent: str = "system"):
        if session_id in self.active_connections:
            message = {
                "type": event_type,
                "agent": agent,
                "payload": payload
            }
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                print(f"Error sending to {session_id}: {e}")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/catalog")
async def get_catalog():
    return JSONResponse(content={"products": CATALOG_DB})

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        if session_id not in sessions:
            # Initialize new session
            sessions[session_id] = AgentState(
                user_id=session_id, 
                messages=[], 
                shared_context={}, 
                current_agent="Discovery"
            )
        
        state = sessions[session_id]
        
        # Send initial sync_state
        await manager.send_event(session_id, "sync_state", {
            "messages": state.messages,
            "current_agent": state.current_agent,
            "shared_context": state.shared_context
        })

        while True:
            # Wait for user message
            data = await websocket.receive_text()
            try:
                msg_data = json.loads(data)
                user_message = msg_data.get("message", "")
            except:
                user_message = data
                
            if not user_message:
                continue

            # ── Always re-read from dict so reset/transitions are reflected ──
            state = sessions[session_id]

            if user_message.strip() == "/reset_session":
                sessions[session_id] = AgentState(
                    user_id=session_id, 
                    messages=[], 
                    shared_context={}, 
                    current_agent="Discovery"
                )
                # Send confirmation back so frontend knows the session is clean
                await manager.send_event(session_id, "sync_state", {
                    "messages": [],
                    "current_agent": "Discovery",
                    "shared_context": {}
                })
                continue

            if state.current_agent in ["Completed", "None"]:
                sessions[session_id] = AgentState(
                    user_id=session_id, 
                    messages=[], 
                    shared_context={}, 
                    current_agent="Discovery"
                )
                await manager.send_event(session_id, "reset_ui", {}, agent="system")
                continue
                
            state.messages.append({"role": "user", "content": user_message})
            
            # Helper callback for engine events
            async def emit_callback(event_type: str, payload: Any):
                await manager.send_event(session_id, event_type, payload, agent=state.current_agent)

            break_to_user = False
            while state.current_agent in AGENTS and not break_to_user:
                current_name = state.current_agent
                agent = AGENTS[current_name]
                
                # Await the async run logic
                state = await agent.run_async(state, emit_callback)
                # Keep sessions dict in sync after each agent run
                sessions[session_id] = state
                
                if state.current_agent != current_name:
                    # It transitioned
                    pass
                else:
                    break_to_user = True
                    
            if state.current_agent in ["Completed", "None"]:
                sessions[session_id] = AgentState(
                    user_id=session_id, 
                    messages=[], 
                    shared_context={}, 
                    current_agent="Discovery"
                )
                await manager.send_event(session_id, "reset_ui", {}, agent="system")

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        print(f"WS Error: {e}")
        manager.disconnect(session_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
