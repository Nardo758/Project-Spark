"""
WebSocket Event Broadcaster

Broadcasts events to WebSocket clients
"""

from typing import Optional
from datetime import datetime

from app.websocket.manager import manager


class WebSocketBroadcaster:
    """Service for broadcasting events via WebSocket"""

    @staticmethod
    async def broadcast_new_comment(
        opportunity_id: int,
        comment_id: int,
        user_id: int,
        user_name: str,
        content: str
    ):
        """Broadcast new comment on opportunity"""
        await manager.broadcast_to_opportunity({
            "type": "new_comment",
            "opportunity_id": opportunity_id,
            "comment_id": comment_id,
            "user_id": user_id,
            "user_name": user_name,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }, opportunity_id)

    @staticmethod
    async def broadcast_new_validation(
        opportunity_id: int,
        user_id: int,
        user_name: str,
        validation_count: int
    ):
        """Broadcast new validation on opportunity"""
        await manager.broadcast_to_opportunity({
            "type": "new_validation",
            "opportunity_id": opportunity_id,
            "user_id": user_id,
            "user_name": user_name,
            "validation_count": validation_count,
            "timestamp": datetime.utcnow().isoformat()
        }, opportunity_id)

    @staticmethod
    async def broadcast_opportunity_updated(
        opportunity_id: int,
        updated_fields: dict
    ):
        """Broadcast opportunity update"""
        await manager.broadcast_to_opportunity({
            "type": "opportunity_updated",
            "opportunity_id": opportunity_id,
            "updated_fields": updated_fields,
            "timestamp": datetime.utcnow().isoformat()
        }, opportunity_id)

    @staticmethod
    async def broadcast_notification(
        user_id: int,
        notification_id: int,
        title: str,
        message: str,
        link: Optional[str] = None
    ):
        """Broadcast notification to specific user"""
        await manager.send_personal_message({
            "type": "notification",
            "notification_id": notification_id,
            "title": title,
            "message": message,
            "link": link,
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)

    @staticmethod
    async def broadcast_new_follower(
        user_id: int,
        follower_id: int,
        follower_name: str
    ):
        """Broadcast new follower notification"""
        await manager.send_personal_message({
            "type": "new_follower",
            "follower_id": follower_id,
            "follower_name": follower_name,
            "timestamp": datetime.utcnow().isoformat()
        }, user_id)

    @staticmethod
    async def broadcast_global_announcement(
        title: str,
        message: str
    ):
        """Broadcast announcement to all connected users"""
        await manager.broadcast_global({
            "type": "announcement",
            "title": title,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })


ws_broadcaster = WebSocketBroadcaster()
