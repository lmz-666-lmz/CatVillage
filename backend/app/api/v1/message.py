from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.message import Message
from app.models.user import User
from app.schemas.message import QuickMeowRequest, SendMessageRequest, UpdateReadStatusRequest

router = APIRouter(prefix="/api/v1", tags=["messages"])


def _serialize_message(message: Message) -> dict:
    return {
        "id": message.id,
        "senderId": message.sender_id,
        "receiverId": message.receiver_id,
        "content": message.content,
        "messageType": message.message_type,
        "sentAt": message.sent_at.isoformat() if message.sent_at else "",
        "status": message.status,
    }


def _serialize_friend(user: User) -> dict:
    return {
        "id": user.id,
        "userId": user.id,
        "username": user.username,
        "nickname": user.username,
        "avatar": "",
        "lastOnlineAt": "",
        "isOnline": False,
    }


@router.get("/friends/list")
def get_friend_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.id != current_user.id)
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [_serialize_friend(item) for item in items],
            "total": total,
        },
    }


@router.post("/messages/send")
def send_message(
    payload: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    message = Message(
        id=str(uuid4()),
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        content=payload.content,
        message_type=payload.message_type,
        status="sent",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"code": 200, "msg": "success", "data": _serialize_message(message)}


@router.put("/messages/{message_id}/revoke")
def revoke_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        return {"code": 200, "msg": "success", "data": {"success": False}}

    if message.sender_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    db.delete(message)
    db.commit()

    return {"code": 200, "msg": "success", "data": {"success": True}}


@router.put("/messages/read-status")
def update_read_status(
    payload: UpdateReadStatusRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = (
        db.query(Message)
        .filter(Message.id.in_(payload.message_ids), Message.receiver_id == current_user.id)
        .update({"status": "read"}, synchronize_session=False)
    )
    db.commit()

    return {"code": 200, "msg": "success", "data": {"success": updated > 0}}


@router.post("/messages/quick-meow")
def send_quick_meow(
    payload: QuickMeowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    receiver = db.query(User).filter(User.id == payload.receiver_id).first()
    if receiver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receiver not found")

    message = Message(
        id=str(uuid4()),
        sender_id=current_user.id,
        receiver_id=payload.receiver_id,
        content=payload.meow_type,
        message_type="quick_meow",
        status="sent",
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return {"code": 200, "msg": "success", "data": _serialize_message(message)}


@router.get("/conversations/list")
def get_conversation_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(Message)
        .filter(or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id))
        .order_by(Message.sent_at.desc())
        .all()
    )

    conversations: dict[str, dict] = {}
    for message in messages:
        target_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        if target_id in conversations:
            continue

        target_user = db.query(User).filter(User.id == target_id).first()
        unread_count = (
            db.query(Message)
            .filter(
                Message.sender_id == target_id,
                Message.receiver_id == current_user.id,
                Message.status != "read",
            )
            .count()
        )

        conversations[target_id] = {
            "id": target_id,
            "targetUserId": target_id,
            "targetType": "user",
            "lastMessage": message.content,
            "lastMessageType": message.message_type,
            "unreadCount": unread_count,
            "updatedAt": message.sent_at.isoformat() if message.sent_at else "",
            "avatar": "",
            "nickname": target_user.username if target_user else "",
            "isOnline": False,
        }

    conversation_list = list(conversations.values())
    total = len(conversation_list)
    start = (page - 1) * pageSize
    end = start + pageSize

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": conversation_list[start:end],
            "total": total,
        },
    }


@router.get("/conversations/{target_user_id}/messages")
def get_conversation_messages(
    target_user_id: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Message).filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.receiver_id == target_user_id),
            (Message.sender_id == target_user_id) & (Message.receiver_id == current_user.id),
        )
    )

    total = query.count()
    items = (
        query.order_by(Message.sent_at.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [_serialize_message(item) for item in items],
            "total": total,
            "page": page,
            "pageSize": pageSize,
        },
    }


@router.delete("/conversations/{target_user_id}")
def delete_conversation(
    target_user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = (
        db.query(Message)
        .filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.receiver_id == target_user_id),
                (Message.sender_id == target_user_id) & (Message.receiver_id == current_user.id),
            )
        )
        .delete(synchronize_session=False)
    )
    db.commit()

    return {"code": 200, "msg": "success", "data": {"success": deleted > 0}}
