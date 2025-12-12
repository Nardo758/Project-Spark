"""
WebSocket Connection Manager

Manages WebSocket connections and broadcasts
"""

from typing import Dict, List, Set
from fastapi import WebSocket
import json
from datetime import datetime


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Active connections: {user_id: [websocket1, websocket2, ...]}
        self.active_connections: Dict[int, List[WebSocket]] = {}

        # Room-based connections for opportunities
        # {opportunity_id: {user_id1, user_id2, ...}}
        self.opportunity_rooms: Dict[int, Set[int]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a WebSocket for a user"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            # Clean up if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

                # Remove from all opportunity rooms
                for room_users in self.opportunity_rooms.values():
                    room_users.discard(user_id)

    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user (all their connections)"""
        if user_id in self.active_connections:
            disconnected = []

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)

            # Clean up disconnected
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast_to_opportunity(self, message: dict, opportunity_id: int):
        """Broadcast message to all users viewing an opportunity"""
        if opportunity_id in self.opportunity_rooms:
            for user_id in self.opportunity_rooms[opportunity_id]:
                await self.send_personal_message(message, user_id)

    async def broadcast_global(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

    def join_opportunity_room(self, user_id: int, opportunity_id: int):
        """User joins an opportunity room"""
        if opportunity_id not in self.opportunity_rooms:
            self.opportunity_rooms[opportunity_id] = set()

        self.opportunity_rooms[opportunity_id].add(user_id)

    def leave_opportunity_room(self, user_id: int, opportunity_id: int):
        """User leaves an opportunity room"""
        if opportunity_id in self.opportunity_rooms:
            self.opportunity_rooms[opportunity_id].discard(user_id)

            # Clean up empty rooms
            if not self.opportunity_rooms[opportunity_id]:
                del self.opportunity_rooms[opportunity_id]

    def get_active_users_count(self) -> int:
        """Get count of currently connected users"""
        return len(self.active_connections)

    def get_opportunity_viewers(self, opportunity_id: int) -> int:
        """Get count of users viewing an opportunity"""
        if opportunity_id in self.opportunity_rooms:
            return len(self.opportunity_rooms[opportunity_id])
        return 0


# Global connection manager instance
manager = ConnectionManager()
