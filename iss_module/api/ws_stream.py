"""
DALS Phase 1 WebSocket Stream
Real-time telemetry streaming for live dashboard updates
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from typing import List, Dict, Any, Set
import json
import asyncio
import logging
from datetime import datetime, timezone
import weakref

# Configure logging
logger = logging.getLogger(__name__)

# WebSocket router
ws_router = APIRouter()

# Connection manager for WebSocket clients
class TelemetryConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscription_map: Dict[WebSocket, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscription_map[websocket] = set()
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscription_map:
            del self.subscription_map[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
        
    async def subscribe(self, websocket: WebSocket, modules: List[str]):
        """Subscribe WebSocket to specific module updates"""
        if websocket in self.subscription_map:
            self.subscription_map[websocket].update(modules)
            await self.send_personal_message(websocket, {
                "type": "subscription_update",
                "subscribed_modules": list(self.subscription_map[websocket]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to client: {e}")
            self.disconnect(websocket)
            
    async def broadcast_telemetry(self, module: str, data: dict):
        """Broadcast telemetry data to subscribed clients"""
        if not self.active_connections:
            return
            
        message = {
            "type": "telemetry_update",
            "module": module,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                # Check if client is subscribed to this module
                subscriptions = self.subscription_map.get(connection, set())
                if not subscriptions or module in subscriptions or "all" in subscriptions:
                    await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")
                disconnected.append(connection)
                
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
            
    async def send_status_update(self, status_data: dict):
        """Send system status updates to all connected clients"""
        message = {
            "type": "status_update",
            "data": status_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send status update: {e}")
                disconnected.append(connection)
                
        # Remove disconnected clients  
        for connection in disconnected:
            self.disconnect(connection)

# AI Comms Connection Manager
class AICommsConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.ai_sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session_data
        
    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if session_id:
            self.ai_sessions[session_id] = {
                "websocket": websocket,
                "connected_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }
        logger.info(f"New AI Comms connection. Total: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        # Clean up sessions
        sessions_to_remove = []
        for session_id, session_data in self.ai_sessions.items():
            if session_data["websocket"] == websocket:
                sessions_to_remove.append(session_id)
        for session_id in sessions_to_remove:
            del self.ai_sessions[session_id]
        logger.info(f"AI Comms disconnected. Total: {len(self.active_connections)}")
        
    async def broadcast_ai_message(self, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast AI message to all connected clients"""
        for connection in self.active_connections:
            if connection != exclude_websocket:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.warning(f"Failed to send AI message: {e}")
                    
    async def send_ai_response(self, session_id: str, response: dict):
        """Send response to specific AI session"""
        if session_id in self.ai_sessions:
            websocket = self.ai_sessions[session_id]["websocket"]
            try:
                await websocket.send_text(json.dumps({
                    "type": "ai_response",
                    "session_id": session_id,
                    "data": response,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
                self.ai_sessions[session_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
            except Exception as e:
                logger.error(f"Failed to send AI response to session {session_id}: {e}")

# Global connection managers
manager = TelemetryConnectionManager()
ai_manager = AICommsConnectionManager()

@ws_router.websocket("/ws/telemetry")
async def telemetry_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time telemetry streaming
    
    Client can send subscription messages to filter data:
    {"action": "subscribe", "modules": ["certsig", "caleon", "iss"]}
    {"action": "unsubscribe", "modules": ["certsig"]}
    {"action": "ping"}
    """
    await manager.connect(websocket)
    
    # Send welcome message
    await manager.send_personal_message(websocket, {
        "type": "welcome",
        "message": "Connected to DALS Phase 1 Telemetry Stream",
        "available_modules": ["certsig", "caleon", "iss"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "subscribe":
                    modules = message.get("modules", [])
                    await manager.subscribe(websocket, modules)
                    
                elif action == "unsubscribe":
                    modules = message.get("modules", [])
                    if websocket in manager.subscription_map:
                        for module in modules:
                            manager.subscription_map[websocket].discard(module)
                        await manager.send_personal_message(websocket, {
                            "type": "subscription_update",
                            "subscribed_modules": list(manager.subscription_map[websocket]),
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                        
                elif action == "ping":
                    await manager.send_personal_message(websocket, {
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
                else:
                    await manager.send_personal_message(websocket, {
                        "type": "error",
                        "message": f"Unknown action: {action}",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
            except json.JSONDecodeError:
                await manager.send_personal_message(websocket, {
                    "type": "error", 
                    "message": "Invalid JSON message",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Function to broadcast telemetry from API endpoints
async def broadcast_telemetry_update(module: str, data: dict):
    """
    Called by telemetry API endpoints to broadcast updates
    """
    await manager.broadcast_telemetry(module, data)

# Function to broadcast status updates
async def broadcast_status_update(status_data: dict):
    """
    Called by system monitoring to broadcast status changes
    """
    await manager.send_status_update(status_data)

# Background task for periodic status updates
async def periodic_status_broadcaster():
    """
    Background task to send periodic system status updates
    """
    while True:
        try:
            # Import here to avoid circular imports
            from .telemetry_api import telemetry_cache
            
            # Calculate status from current telemetry cache
            total_packets = sum(len(data_list) for data_list in telemetry_cache.values())
            active_modules = sum(1 for data_list in telemetry_cache.values() if len(data_list) > 0)
            
            status_data = {
                "total_packets": total_packets,
                "active_modules": active_modules,
                "system_health": "optimal" if active_modules >= 2 else "degraded" if active_modules >= 1 else "offline",
                "connected_clients": len(manager.active_connections)
            }
            
            await manager.send_status_update(status_data)
            
        except Exception as e:
            logger.error(f"Status broadcaster error: {e}")
            
        # Wait 30 seconds before next update
        await asyncio.sleep(30)

# Heartbeat monitor for WebSocket connections
async def websocket_heartbeat_monitor():
    """
    Monitor WebSocket connections and send periodic heartbeats
    """
    while True:
        try:
            if manager.active_connections:
                heartbeat_message = {
                    "type": "heartbeat",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "server_status": "active"
                }
                
                disconnected = []
                for connection in manager.active_connections:
                    try:
                        await connection.send_text(json.dumps(heartbeat_message))
                    except Exception as e:
                        logger.warning(f"Heartbeat failed for client: {e}")
                        disconnected.append(connection)
                
                # Remove disconnected clients
                for connection in disconnected:
                    manager.disconnect(connection)
                    
        except Exception as e:
            logger.error(f"Heartbeat monitor error: {e}")
            
        # Send heartbeat every 60 seconds
        await asyncio.sleep(60)

@ws_router.websocket("/ws/ai-comms")
async def ai_comms_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for AI communications deck
    
    Supports real-time AI interactions, reasoning sessions, and comms broadcasting
    """
    session_id = websocket.query_params.get("session_id", f"session_{datetime.now(timezone.utc).timestamp()}")
    await ai_manager.connect(websocket, session_id)
    
    # Send welcome message
    await websocket.send_text(json.dumps({
        "type": "comms_connected",
        "session_id": session_id,
        "message": "Connected to DALS AI Communications Deck",
        "capabilities": ["reasoning", "vault_queries", "telemetry", "broadcast"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }))
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ai_query":
                    # Process AI query
                    query = message.get("query", "")
                    context = message.get("context", {})
                    
                    # Simulate AI processing (replace with actual AI integration)
                    response = {
                        "query": query,
                        "response": f"Processing query: {query}",
                        "confidence": 0.85,
                        "processing_time": 0.123,
                        "sources": ["DALS Knowledge Base", "Live Telemetry"]
                    }
                    
                    await ai_manager.send_ai_response(session_id, response)
                    
                elif msg_type == "broadcast_message":
                    # Broadcast message to all AI comms clients
                    broadcast_data = {
                        "type": "broadcast",
                        "sender": session_id,
                        "message": message.get("message", ""),
                        "priority": message.get("priority", "normal"),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
                    await ai_manager.broadcast_ai_message(broadcast_data, websocket)
                    
                elif msg_type == "reasoning_request":
                    # Handle reasoning requests
                    reasoning_data = {
                        "type": "reasoning_started",
                        "session_id": session_id,
                        "query": message.get("query", ""),
                        "reasoning_steps": [],
                        "status": "processing"
                    }
                    
                    await websocket.send_text(json.dumps(reasoning_data))
                    
                    # Simulate reasoning steps
                    steps = [
                        "Analyzing query parameters",
                        "Consulting knowledge base", 
                        "Cross-referencing telemetry data",
                        "Formulating response"
                    ]
                    
                    for i, step in enumerate(steps):
                        await asyncio.sleep(0.5)  # Simulate processing time
                        step_data = {
                            "type": "reasoning_step",
                            "session_id": session_id,
                            "step": i + 1,
                            "description": step,
                            "progress": (i + 1) / len(steps)
                        }
                        await websocket.send_text(json.dumps(step_data))
                    
                    # Final response
                    final_response = {
                        "type": "reasoning_complete",
                        "session_id": session_id,
                        "conclusion": "Analysis complete - all systems nominal",
                        "confidence": 0.92,
                        "evidence_count": 15
                    }
                    
                    await websocket.send_text(json.dumps(final_response))
                    
                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "session_id": session_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
                
    except WebSocketDisconnect:
        ai_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"AI Comms WebSocket error: {e}")
        ai_manager.disconnect(websocket)