"""
WebSocket streaming for real‑time patrol updates.

This module defines a simple connection manager for WebSockets and
exposes an endpoint at ``/ws`` that clients can connect to. When
patrol locations are updated via the REST API the manager's
``broadcast`` method is called, sending JSON messages to all
connected clients. This enables real‑time situational awareness
dashboards without polling.
"""

import json
from typing import List

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        """Broadcast a JSON message to all connected clients."""
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                # On error remove connection silently
                self.disconnect(connection)


manager = ConnectionManager()


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for clients to receive streaming patrol updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive; ignore client msgs
    except WebSocketDisconnect:
        manager.disconnect(websocket)