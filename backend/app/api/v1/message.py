from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.message import Message
from app.models.social import SocialComment, SocialDynamic, SocialFollow, SocialLike
from app.models.user import User
from app.schemas.message import QuickMeowRequest, SendMessageRequest, UpdateReadStatusRequest

router = APIRouter(prefix="/api/v1", tags=["messages"])


def _display_name(user: User | None) -> str:
    if user is None:
        return ""
    nickname = (getattr(user, "nickname", "") or "").strip()
    if nickname:
        return nickname
    return user.username


def _avatar_url(user: User | None) -> str:
    if user is None:
        return ""
    return (getattr(user, "avatar_url", "") or "").strip()


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


def _visible_message_filter(current_user_id: str):
    return or_(
        and_(Message.sender_id == current_user_id, Message.sender_deleted_at.is_(None)),
        and_(Message.receiver_id == current_user_id, Message.receiver_deleted_at.is_(None)),
    )


def _mark_message_deleted_for_user(message: Message, user_id: str, deleted_at: datetime) -> None:
    if message.sender_id == user_id:
        message.sender_deleted_at = deleted_at
    if message.receiver_id == user_id:
        message.receiver_deleted_at = deleted_at


def _format_cat_summary(cat_names: list[str]) -> str:
    if not cat_names:
        return "TA 的猫咪：暂无公开猫咪"
    if len(cat_names) <= 2:
        return f"TA 的猫咪：{'、'.join(cat_names)}"
    return f"TA 的猫咪：{cat_names[0]}、{cat_names[1]}等 {len(cat_names)} 只"


def _serialize_friend(user: User, db: Session, is_following: bool = False) -> dict:
    cat_names = [
        name
        for (name,) in db.query(CatProfile.name)
        .filter(CatProfile.user_id == user.id)
        .order_by(CatProfile.created_at.desc())
        .limit(20)
        .all()
    ]
    return {
        "id": user.id,
        "userId": user.id,
        "username": user.username,
        "nickname": _display_name(user),
        "avatar": _avatar_url(user),
        "miaoId": user.username,
        "catNames": cat_names,
        "catSummary": _format_cat_summary(cat_names),
        "lastOnlineAt": "",
        "isOnline": False,
        "isFollowing": is_following,
    }


def _count_private_unread(db: Session, user_id: str) -> int:
    return int(
        db.query(func.count(Message.id))
        .filter(
            Message.receiver_id == user_id,
            Message.receiver_deleted_at.is_(None),
            Message.status != "read",
        )
        .scalar()
        or 0
    )


def _count_received_comments(db: Session, user_id: str) -> int:
    return int(
        db.query(func.count(SocialComment.id))
        .join(SocialDynamic, SocialComment.dynamic_id == SocialDynamic.id)
        .filter(
            SocialDynamic.user_id == user_id,
            SocialComment.user_id != user_id,
        )
        .scalar()
        or 0
    )


def _count_received_likes(db: Session, user_id: str) -> int:
    return int(
        db.query(func.count(SocialLike.id))
        .join(SocialDynamic, SocialLike.dynamic_id == SocialDynamic.id)
        .filter(
            SocialDynamic.user_id == user_id,
            SocialLike.user_id != user_id,
            SocialLike.is_active == True,
        )
        .scalar()
        or 0
    )


def _count_followers(db: Session, user_id: str) -> int:
    return int(
        db.query(func.count(SocialFollow.id))
        .filter(SocialFollow.followed_user_id == user_id)
        .scalar()
        or 0
    )


@router.get("/friends/list")
def get_friend_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    keyword: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(User).filter(User.id != current_user.id)

    if keyword:
        keyword_trimmed = keyword.strip()
        if keyword_trimmed:
            query = query.filter(
                or_(
                    User.username.like(f"%{keyword_trimmed}%"),
                    User.nickname.like(f"%{keyword_trimmed}%"),
                )
            )

    total = query.count()
    items = (
        query.order_by(User.id.asc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    following_ids: set[str] = set()
    user_ids = [item.id for item in items]
    if user_ids:
        following_rows = (
            db.query(SocialFollow.followed_user_id)
            .filter(
                SocialFollow.follower_id == current_user.id,
                SocialFollow.followed_user_id.in_(user_ids),
            )
            .all()
        )
        following_ids = {user_id for (user_id,) in following_rows}

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [_serialize_friend(item, db, item.id in following_ids) for item in items],
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


@router.get("/messages/unread-summary")
def get_unread_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    private_messages = _count_private_unread(db, current_user.id)
    comments = _count_received_comments(db, current_user.id)
    likes = _count_received_likes(db, current_user.id)
    followers = _count_followers(db, current_user.id)
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "privateMessages": private_messages,
            "comments": comments,
            "likes": likes,
            "followers": followers,
            "total": private_messages + comments + likes + followers,
        },
    }


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
        .filter(_visible_message_filter(current_user.id))
        .order_by(Message.sent_at.desc())
        .all()
    )

    conversations: dict[str, dict] = {}
    for message in messages:
        target_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        if target_id in conversations:
            continue
        conversations[target_id] = {
            "id": target_id,
            "targetUserId": target_id,
            "targetType": "user",
            "lastMessage": message.content,
            "lastMessageType": message.message_type,
            "unreadCount": 0,
            "updatedAt": message.sent_at.isoformat() if message.sent_at else "",
            "avatar": "",
            "nickname": "",
            "isOnline": False,
        }

    target_ids = list(conversations.keys())
    if target_ids:
        user_rows = db.query(User).filter(User.id.in_(target_ids)).all()
        user_map = {user.id: user for user in user_rows}

        unread_rows = (
            db.query(Message.sender_id, func.count(Message.id))
            .filter(
                Message.sender_id.in_(target_ids),
                Message.receiver_id == current_user.id,
                Message.receiver_deleted_at.is_(None),
                Message.status != "read",
            )
            .group_by(Message.sender_id)
            .all()
        )
        unread_map = {sender_id: count for sender_id, count in unread_rows}

        for target_id, item in conversations.items():
            target_user = user_map.get(target_id)
            item["nickname"] = _display_name(target_user)
            item["avatar"] = _avatar_url(target_user)
            item["unreadCount"] = int(unread_map.get(target_id, 0))

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


@router.get("/conversations/search")
def search_conversations(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keyword = q.strip()
    if not keyword:
        return {"code": 200, "msg": "success", "data": {"list": [], "total": 0}}

    visible_messages = (
        db.query(Message)
        .filter(_visible_message_filter(current_user.id))
        .order_by(Message.sent_at.desc())
        .all()
    )
    target_ids = {
        message.receiver_id if message.sender_id == current_user.id else message.sender_id
        for message in visible_messages
    }
    if not target_ids:
        return {"code": 200, "msg": "success", "data": {"list": [], "total": 0}}

    user_rows = db.query(User).filter(User.id.in_(target_ids)).all()
    user_map = {user.id: user for user in user_rows}
    matched_user_ids = {
        user.id
        for user in user_rows
        if keyword.lower() in (user.username or "").lower()
        or keyword.lower() in ((user.nickname or "")).lower()
    }

    latest_by_target: dict[str, Message] = {}
    matched_targets: dict[str, str] = {}
    for message in visible_messages:
        target_id = message.receiver_id if message.sender_id == current_user.id else message.sender_id
        latest_by_target.setdefault(target_id, message)
        content = message.content or ""
        if target_id in matched_targets:
            continue
        if target_id in matched_user_ids or keyword.lower() in content.lower():
            matched_targets[target_id] = content

    if not matched_targets:
        return {"code": 200, "msg": "success", "data": {"list": [], "total": 0}}

    unread_rows = (
        db.query(Message.sender_id, func.count(Message.id))
        .filter(
            Message.sender_id.in_(list(matched_targets.keys())),
            Message.receiver_id == current_user.id,
            Message.receiver_deleted_at.is_(None),
            Message.status != "read",
        )
        .group_by(Message.sender_id)
        .all()
    )
    unread_map = {sender_id: count for sender_id, count in unread_rows}

    items: list[dict] = []
    for target_id, snippet in matched_targets.items():
        latest = latest_by_target.get(target_id)
        if latest is None:
            continue
        target_user = user_map.get(target_id)
        items.append({
            "id": target_id,
            "targetUserId": target_id,
            "targetType": "user",
            "lastMessage": latest.content,
            "lastMessageType": latest.message_type,
            "unreadCount": int(unread_map.get(target_id, 0)),
            "updatedAt": latest.sent_at.isoformat() if latest.sent_at else "",
            "avatar": _avatar_url(target_user),
            "nickname": _display_name(target_user),
            "isOnline": False,
            "matchSnippet": snippet or latest.content,
        })

    total = len(items)
    start = (page - 1) * pageSize
    end = start + pageSize
    return {"code": 200, "msg": "success", "data": {"list": items[start:end], "total": total}}


@router.get("/conversations/{target_user_id}/messages")
def get_conversation_messages(
    target_user_id: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Message).filter(
        _visible_message_filter(current_user.id),
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
    items = (
        db.query(Message)
        .filter(
            _visible_message_filter(current_user.id),
            or_(
                (Message.sender_id == current_user.id) & (Message.receiver_id == target_user_id),
                (Message.sender_id == target_user_id) & (Message.receiver_id == current_user.id),
            ),
        )
        .all()
    )
    deleted_at = datetime.now(timezone.utc)
    for item in items:
        _mark_message_deleted_for_user(item, current_user.id, deleted_at)
        if item.sender_deleted_at is not None and item.receiver_deleted_at is not None:
            db.delete(item)
    db.commit()

    return {"code": 200, "msg": "success", "data": {"success": True, "deleted": len(items)}}
