from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.network_hub import ConnectionRequest, ConnectionStatus, Message, MessageThread, ThreadType
from app.models.user import User
from app.schemas.network_hub import ConnectionRequestCreate, ConnectionRequestOut, MessageCreate, MessageOut, ThreadOut
from app.services.audit import log_event


router = APIRouter()


def _pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)


@router.get("/network/requests/incoming", response_model=list[ConnectionRequestOut])
def incoming_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(ConnectionRequest)
        .filter(ConnectionRequest.target_user_id == current_user.id)
        .order_by(ConnectionRequest.created_at.desc())
        .all()
    )


@router.get("/network/requests/outgoing", response_model=list[ConnectionRequestOut])
def outgoing_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(ConnectionRequest)
        .filter(ConnectionRequest.requester_id == current_user.id)
        .order_by(ConnectionRequest.created_at.desc())
        .all()
    )


@router.post("/network/requests", response_model=ConnectionRequestOut, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: ConnectionRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if payload.target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot connect to yourself")

    target = db.query(User).filter(User.id == payload.target_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target user not found")

    existing = (
        db.query(ConnectionRequest)
        .filter(
            ConnectionRequest.requester_id == current_user.id,
            ConnectionRequest.target_user_id == payload.target_user_id,
            ConnectionRequest.context_type == payload.context_type,
            ConnectionRequest.context_id == payload.context_id,
        )
        .first()
    )
    if existing and existing.status == ConnectionStatus.PENDING.value:
        return existing

    row = ConnectionRequest(
        requester_id=current_user.id,
        target_user_id=payload.target_user_id,
        status=ConnectionStatus.PENDING.value,
        context_type=payload.context_type,
        context_id=payload.context_id,
        message=payload.message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    log_event(
        db,
        action="network.request.created",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="connection_request",
        resource_id=row.id,
        metadata={"target_user_id": payload.target_user_id, "context_type": payload.context_type, "context_id": payload.context_id},
    )

    return row


@router.post("/network/requests/{request_id}/accept", response_model=ThreadOut)
def accept_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    if row.target_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if row.status != ConnectionStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Request is not pending")

    row.status = ConnectionStatus.ACCEPTED.value
    row.responded_at = datetime.utcnow()

    a, b = _pair(row.requester_id, row.target_user_id)
    thread = (
        db.query(MessageThread)
        .filter(
            MessageThread.user_a_id == a,
            MessageThread.user_b_id == b,
            MessageThread.context_type == row.context_type,
            MessageThread.context_id == row.context_id,
        )
        .first()
    )
    if not thread:
        thread = MessageThread(
            thread_type=ThreadType.DIRECT.value,
            user_a_id=a,
            user_b_id=b,
            context_type=row.context_type,
            context_id=row.context_id,
        )
        db.add(thread)

    db.commit()
    db.refresh(thread)

    log_event(
        db,
        action="network.request.accepted",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="connection_request",
        resource_id=row.id,
        metadata={"thread_id": thread.id},
    )

    return thread


@router.post("/network/requests/{request_id}/decline", response_model=ConnectionRequestOut)
def decline_request(
    request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    row = db.query(ConnectionRequest).filter(ConnectionRequest.id == request_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Request not found")
    if row.target_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if row.status != ConnectionStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Request is not pending")

    row.status = ConnectionStatus.DECLINED.value
    row.responded_at = datetime.utcnow()
    db.commit()
    db.refresh(row)

    log_event(
        db,
        action="network.request.declined",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="connection_request",
        resource_id=row.id,
        metadata={},
    )

    return row


@router.get("/network/threads", response_model=list[ThreadOut])
def list_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(MessageThread)
        .filter(or_(MessageThread.user_a_id == current_user.id, MessageThread.user_b_id == current_user.id))
        .order_by(MessageThread.last_message_at.desc().nullslast(), MessageThread.created_at.desc())
        .all()
    )


@router.get("/network/threads/{thread_id}/messages", response_model=list[MessageOut])
def list_messages(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    if current_user.id not in (thread.user_a_id, thread.user_b_id):
        raise HTTPException(status_code=403, detail="Not allowed")

    return db.query(Message).filter(Message.thread_id == thread_id).order_by(Message.created_at.asc()).all()


@router.post("/network/threads/{thread_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def post_message(
    thread_id: int,
    payload: MessageCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    thread = db.query(MessageThread).filter(MessageThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    if current_user.id not in (thread.user_a_id, thread.user_b_id):
        raise HTTPException(status_code=403, detail="Not allowed")

    msg = Message(thread_id=thread_id, sender_id=current_user.id, body=payload.body)
    db.add(msg)
    thread.last_message_at = datetime.utcnow()
    db.commit()
    db.refresh(msg)

    log_event(
        db,
        action="network.message.sent",
        actor=current_user,
        actor_type="user",
        request=request,
        resource_type="message",
        resource_id=msg.id,
        metadata={"thread_id": thread_id},
    )

    return msg

