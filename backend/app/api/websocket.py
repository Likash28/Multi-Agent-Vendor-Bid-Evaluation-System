"""
WebSocket Handler for Real-time Updates
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from datetime import datetime
import json
import logging

from app.dependencies import get_db
from app.core.auth import get_current_user_ws

logger = logging.getLogger(__name__)

websocket_router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, evaluation_id: str):
        """Register a new connection (WebSocket should already be accepted)"""
        if evaluation_id not in self.active_connections:
            self.active_connections[evaluation_id] = []
        self.active_connections[evaluation_id].append(websocket)
        logger.info(f"WebSocket registered for evaluation {evaluation_id}")

    def disconnect(self, websocket: WebSocket, evaluation_id: str):
        """Remove a connection"""
        if evaluation_id in self.active_connections:
            if websocket in self.active_connections[evaluation_id]:
                self.active_connections[evaluation_id].remove(websocket)
                logger.info(f"WebSocket disconnected for evaluation {evaluation_id}")
            if not self.active_connections[evaluation_id]:
                del self.active_connections[evaluation_id]

    async def broadcast(self, evaluation_id: str, message: dict):
        """Broadcast message to all connections for an evaluation"""
        if evaluation_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[evaluation_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.warning(f"Error sending message to WebSocket: {e}")
                    dead_connections.append(connection)

            # Clean up dead connections
            for dead in dead_connections:
                self.disconnect(dead, evaluation_id)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending personal message: {e}")


manager = ConnectionManager()


@websocket_router.websocket("/evaluation/{evaluation_id}")
async def evaluation_progress(
    websocket: WebSocket,
    evaluation_id: str,
    token: Optional[str] = Query(None),
):
    """WebSocket endpoint for evaluation progress updates"""
    # Accept the WebSocket connection first
    try:
        await websocket.accept()
    except Exception as e:
        logger.error(f"Error accepting WebSocket connection: {e}")
        return

    # Optional authentication - if token is provided, verify it
    user = None
    if token:
        try:
            async for db in get_db():
                user = await get_current_user_ws(token, db)
                break
            if not user:
                logger.warning(f"Invalid token for WebSocket connection to evaluation {evaluation_id}")
                try:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                except Exception:
                    pass
                return
        except Exception as e:
            logger.error(f"Error authenticating WebSocket connection: {e}")
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            except Exception:
                pass
            return

    # Register the connection
    try:
        if evaluation_id not in manager.active_connections:
            manager.active_connections[evaluation_id] = []
        manager.active_connections[evaluation_id].append(websocket)
        logger.info(f"WebSocket connected for evaluation {evaluation_id}")
    except Exception as e:
        logger.error(f"Error registering WebSocket connection: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
        return

    try:
        # Send initial connection confirmation
        await manager.send_personal(websocket, {
            "type": "connected",
            "evaluation_id": evaluation_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        while True:
            try:
                # Check if WebSocket is still connected before receiving
                # Wait for messages from client
                data = await websocket.receive_text()

                # Handle ping/pong for connection keep-alive
                if data == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
                    continue

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
                    logger.warning(f"Invalid JSON received from WebSocket: {data}")
                    pass

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally for evaluation {evaluation_id}")
                break
            except RuntimeError as e:
                # RuntimeError often indicates the connection is closed
                error_msg = str(e).lower()
                if "not connected" in error_msg or "closed" in error_msg:
                    logger.info(f"WebSocket connection closed for evaluation {evaluation_id}")
                    break
                else:
                    logger.error(f"Runtime error processing WebSocket message: {e}")
                    break
            except Exception as e:
                error_msg = str(e).lower()
                if "not connected" in error_msg or "closed" in error_msg:
                    logger.info(f"WebSocket connection closed for evaluation {evaluation_id}")
                    break
                logger.error(f"Error processing WebSocket message: {e}")
                # Don't continue if connection is broken
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for evaluation {evaluation_id}")
    except Exception as e:
        logger.error(f"WebSocket error for evaluation {evaluation_id}: {e}")
    finally:
        # Always clean up the connection
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
