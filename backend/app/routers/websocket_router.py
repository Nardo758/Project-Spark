"""
WebSocket Router

Real-time WebSocket endpoints
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.db.database import get_db
from app.websocket.manager import manager
from app.core.security import decode_access_token
from app.models.user import User

router = APIRouter()


async def get_user_from_token(token: str, db: Session) -> Optional[User]:
    """Get user from JWT token"""
    try:
        payload = decode_access_token(token)
        if not payload:
            return None

        email = payload.get("sub")
        if not email:
            return None

        user = db.query(User).filter(User.email == email).first()
        return user
    except:
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Main WebSocket endpoint for real-time updates

    Client should connect with JWT token as query parameter:
    ws://localhost:8000/api/v1/ws?token=<jwt_token>
    """
    # Authenticate user
    user = await get_user_from_token(token, db)

    if not user:
        await websocket.close(code=1008)  # Policy violation
        return

    # Connect user
    await manager.connect(websocket, user.id)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to OppGrid WebSocket",
            "user_id": user.id
        })

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            message_type = message.get("type")

            if message_type == "join_opportunity":
                # User joins opportunity room
                opportunity_id = message.get("opportunity_id")
                if opportunity_id:
                    manager.join_opportunity_room(user.id, opportunity_id)

                    # Notify others in room
                    await manager.broadcast_to_opportunity({
                        "type": "user_joined",
                        "opportunity_id": opportunity_id,
                        "user_id": user.id,
                        "user_name": user.name
                    }, opportunity_id)

                    # Send viewer count
                    viewer_count = manager.get_opportunity_viewers(opportunity_id)
                    await manager.broadcast_to_opportunity({
                        "type": "viewer_count",
                        "opportunity_id": opportunity_id,
                        "count": viewer_count
                    }, opportunity_id)

            elif message_type == "leave_opportunity":
                # User leaves opportunity room
                opportunity_id = message.get("opportunity_id")
                if opportunity_id:
                    manager.leave_opportunity_room(user.id, opportunity_id)

                    # Notify others
                    await manager.broadcast_to_opportunity({
                        "type": "user_left",
                        "opportunity_id": opportunity_id,
                        "user_id": user.id
                    }, opportunity_id)

                    # Send updated viewer count
                    viewer_count = manager.get_opportunity_viewers(opportunity_id)
                    await manager.broadcast_to_opportunity({
                        "type": "viewer_count",
                        "opportunity_id": opportunity_id,
                        "count": viewer_count
                    }, opportunity_id)

            elif message_type == "typing":
                # User is typing a comment
                opportunity_id = message.get("opportunity_id")
                if opportunity_id:
                    await manager.broadcast_to_opportunity({
                        "type": "typing",
                        "opportunity_id": opportunity_id,
                        "user_id": user.id,
                        "user_name": user.name,
                        "is_typing": message.get("is_typing", True)
                    }, opportunity_id)

            elif message_type == "ping":
                # Keepalive ping
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, user.id)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_users": manager.get_active_users_count(),
        "active_rooms": len(manager.opportunity_rooms)
    }
