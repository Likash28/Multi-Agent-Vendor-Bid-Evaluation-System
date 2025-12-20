"""
WebSocket Handler for Real-time Updates
"""

from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime
import json

websocket_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, evaluation_id: str):
        """Accept and register a new connection"""
        await websocket.accept()
        if evaluation_id not in self.active_connections:
            self.active_connections[evaluation_id] = []
        self.active_connections[evaluation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, evaluation_id: str):
        """Remove a connection"""
        if evaluation_id in self.active_connections:
            if websocket in self.active_connections[evaluation_id]:
                self.active_connections[evaluation_id].remove(websocket)
            if not self.active_connections[evaluation_id]:
                del self.active_connections[evaluation_id]

    async def broadcast(self, evaluation_id: str, message: dict):
        """Broadcast message to all connections for an evaluation"""
        if evaluation_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[evaluation_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)

            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead, evaluation_id)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()


@websocket_router.websocket("/evaluation/{evaluation_id}")
async def evaluation_progress(
    websocket: WebSocket,
    evaluation_id: str,
):
    """WebSocket endpoint for evaluation progress updates"""
    await manager.connect(websocket, evaluation_id)

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()

            # Handle ping/pong for connection keep-alive
            if data == "ping":
                await manager.send_personal(websocket, {"type": "pong"})

            # Handle other messages
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "evaluation_id": evaluation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, evaluation_id)


async def send_progress_update(evaluation_id: str, state: dict):
    """
    Send progress update to all connected clients.
    This function is called by the orchestrator during evaluation.
    """
    message = {
        "type": "progress",
        "step": state.get("current_step"),
        "logs": state.get("logs", [])[-5:],  # Last 5 logs
        "progress_percent": calculate_progress(state),
        "timestamp": datetime.utcnow().isoformat(),
    }
    await manager.broadcast(evaluation_id, message)


def calculate_progress(state: dict) -> int:
    """Calculate progress percentage based on current step"""
    steps = [
        "starting",
        "tender_parsing",
        "bid_parsing",
        "compliance_verification",
        "technical_evaluation",
        "financial_evaluation",
        "comparison_analysis",
        "report_generation",
        "completed",
    ]

    current_step = state.get("current_step", "starting")

    try:
        step_index = steps.index(current_step)
        return int((step_index / (len(steps) - 1)) * 100)
    except ValueError:
        return 0
