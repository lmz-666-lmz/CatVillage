from datetime import datetime, timedelta, timezone
import json
import os
from collections import Counter
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

import app.api.v1.ai_assistant as ai_assistant_module
import app.api.v1.social as social_module
import app.core.config as runtime_config
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash
from app.core.storage import safe_delete_file
from app.database.session import get_db
from app.models.ai_chat_history import AIChatHistory
from app.models.cat_profile import CatProfile
from app.models.emotion_record import EmotionRecord
from app.models.health import FeedingRecord, PetWeight
from app.models.message import Message
from app.models.social import SocialComment, SocialCommentLike, SocialDynamic, SocialFavorite, SocialLike
from app.models.user import User
from app.schemas.admin import AdminConfigPayload, AdminListResponse, AdminPasswordPayload, AdminStats, AdminTogglePayload, AdminTopicsPayload


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    return current_user


def envelope(data):
    return {"code": 200, "msg": "success", "data": data}


def _page(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def _admin_parse_images(raw_images: str | None) -> list[str]:
    if not raw_images:
        return []
    try:
        parsed = json.loads(raw_images)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if isinstance(item, str) and item.strip()]


def _safe_iso(value):
    return value.isoformat() if value else ""


def _mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}****{value[-4:]}"


def _display_name(user: User | None) -> str:
    if user is None:
        return ""
    return (user.nickname or "").strip() or user.username


def _count_since(db: Session, model, field, since: datetime) -> int:
    return db.query(model).filter(field >= since).count()


@router.get("/stats")
def get_admin_stats(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    stats = AdminStats(
        users=db.query(User).count(),
        pets=db.query(CatProfile).count(),
        dynamics=db.query(SocialDynamic).count(),
        emotion_records=db.query(EmotionRecord).count(),
        today_users=_count_since(db, User, User.created_at, today_start),
        today_dynamics=_count_since(db, SocialDynamic, SocialDynamic.created_at, today_start),
        messages=db.query(Message).count(),
        health_records=db.query(PetWeight).count() + db.query(FeedingRecord).count(),
        ai_chats=db.query(AIChatHistory).count(),
        active_users=db.query(User).filter(User.is_active == True).count(),
        disabled_users=db.query(User).filter(User.is_active == False).count(),
        admins=db.query(User).filter(User.is_admin == True).count(),
    )
    return envelope(stats.model_dump())


@router.get("/overview")
def get_admin_overview(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    since_24h = now - timedelta(days=1)
    since_7d = now - timedelta(days=7)

    daily_items = []
    for index in range(6, -1, -1):
        start = (now - timedelta(days=index)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        daily_items.append(
            {
                "date": start.date().isoformat(),
                "users": db.query(User).count() if index == 0 else 0,
                "dynamics": db.query(SocialDynamic).filter(SocialDynamic.created_at >= start, SocialDynamic.created_at < end).count(),
                "emotions": db.query(EmotionRecord).filter(EmotionRecord.record_time >= start, EmotionRecord.record_time < end).count(),
                "messages": db.query(Message).filter(Message.sent_at >= start, Message.sent_at < end).count(),
            }
        )

    recent_dynamics = (
        db.query(SocialDynamic, User)
        .outerjoin(User, User.id == SocialDynamic.user_id)
        .order_by(SocialDynamic.created_at.desc())
        .limit(5)
        .all()
    )
    recent_emotions = (
        db.query(EmotionRecord, CatProfile.name)
        .outerjoin(CatProfile, CatProfile.id == EmotionRecord.pet_id)
        .order_by(EmotionRecord.record_time.desc())
        .limit(5)
        .all()
    )

    return envelope(
        {
            "health": {
                "activeUsers": db.query(User).filter(User.is_active == True).count(),
                "disabledUsers": db.query(User).filter(User.is_active == False).count(),
                "admins": db.query(User).filter(User.is_admin == True).count(),
                "aiConfigured": bool(runtime_config.AI_API_KEY),
            },
            "today": {
                "dynamics": _count_since(db, SocialDynamic, SocialDynamic.created_at, since_24h),
                "emotions": _count_since(db, EmotionRecord, EmotionRecord.record_time, since_24h),
                "messages": _count_since(db, Message, Message.sent_at, since_24h),
                "aiChats": _count_since(db, AIChatHistory, AIChatHistory.created_at, since_24h),
            },
            "week": {
                "dynamics": _count_since(db, SocialDynamic, SocialDynamic.created_at, since_7d),
                "emotions": _count_since(db, EmotionRecord, EmotionRecord.record_time, since_7d),
                "messages": _count_since(db, Message, Message.sent_at, since_7d),
                "feedings": _count_since(db, FeedingRecord, FeedingRecord.feeding_time, since_7d),
                "weights": _count_since(db, PetWeight, PetWeight.record_date, since_7d),
            },
            "daily": daily_items,
            "recentActivities": [
                {
                    "id": dynamic.id,
                    "type": "dynamic",
                    "title": _display_name(user) or dynamic.user_id,
                    "desc": dynamic.content[:72],
                    "time": _safe_iso(dynamic.created_at),
                }
                for dynamic, user in recent_dynamics
            ]
            + [
                {
                    "id": str(record.id),
                    "type": "emotion",
                    "title": pet_name or record.pet_id,
                    "desc": f"{record.label} · {round((record.confidence or 0) * 100)}%",
                    "time": _safe_iso(record.record_time),
                }
                for record, pet_name in recent_emotions
            ],
        }
    )


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if keyword:
        value = f"%{keyword.strip()}%"
        query = query.filter(or_(User.username.like(value), User.nickname.like(value)))
    total, items = _page(query.order_by(User.username.asc()), page, pageSize)
    return envelope(
        AdminListResponse(
            list=[
                {
                    "id": item.id,
                    "username": item.username,
                    "nickname": _display_name(item),
                    "isActive": item.is_active,
                    "isAdmin": bool(getattr(item, "is_admin", False)),
                }
                for item in items
            ],
            total=total,
            page=page,
            pageSize=pageSize,
        ).model_dump()
    )


@router.put("/users/{user_id}/active")
def set_user_active(
    user_id: str,
    payload: AdminTogglePayload,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.id and not payload.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot disable current admin")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = payload.value
    db.commit()
    return envelope({"success": True})


@router.put("/users/{user_id}/admin")
def set_user_admin(
    user_id: str,
    payload: AdminTogglePayload,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.id and not payload.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot revoke current admin")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_admin = payload.value
    db.commit()
    return envelope({"success": True})


@router.put("/users/{user_id}/password")
def reset_user_password(
    user_id: str,
    payload: AdminPasswordPayload,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    password = (payload.password or "").strip()
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.hashed_password = get_password_hash(password)
    db.commit()
    return envelope({"success": True})


@router.get("/pets")
def list_pets(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(CatProfile, User).outerjoin(User, User.id == CatProfile.user_id)
    if keyword:
        value = f"%{keyword.strip()}%"
        query = query.filter(or_(CatProfile.name.like(value), CatProfile.breed.like(value), User.username.like(value)))
    total, items = _page(query.order_by(CatProfile.created_at.desc()), page, pageSize)
    return envelope(
        AdminListResponse(
            list=[
                {
                    "id": pet.id,
                    "name": pet.name,
                    "breed": pet.breed or "",
                    "age": pet.age,
                    "weight": pet.weight,
                    "owner": _display_name(user) or pet.user_id,
                    "createdAt": pet.created_at.isoformat() if pet.created_at else "",
                }
                for pet, user in items
            ],
            total=total,
            page=page,
            pageSize=pageSize,
        ).model_dump()
    )


@router.get("/dynamics")
def list_dynamics(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(SocialDynamic, User).outerjoin(User, User.id == SocialDynamic.user_id)
    if keyword:
        value = f"%{keyword.strip()}%"
        query = query.filter(or_(SocialDynamic.content.like(value), User.username.like(value), User.nickname.like(value)))
    total, items = _page(query.order_by(SocialDynamic.created_at.desc()), page, pageSize)
    return envelope(
        AdminListResponse(
            list=[
                {
                    "id": dynamic.id,
                    "content": dynamic.content,
                    "author": _display_name(user) or dynamic.user_id,
                    "likeCount": dynamic.like_count,
                    "commentCount": dynamic.comment_count,
                    "isRecommended": bool(dynamic.is_recommended),
                    "recommendedAt": dynamic.recommended_at.isoformat() if dynamic.recommended_at else "",
                    "createdAt": dynamic.created_at.isoformat() if dynamic.created_at else "",
                }
                for dynamic, user in items
            ],
            total=total,
            page=page,
            pageSize=pageSize,
        ).model_dump()
    )


@router.put("/dynamics/{dynamic_id}/recommend")
def set_dynamic_recommended(
    dynamic_id: str,
    payload: AdminTogglePayload,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")
    dynamic.is_recommended = payload.value
    dynamic.recommended_at = datetime.now(timezone.utc) if payload.value else None
    db.commit()
    return envelope({"success": True})


@router.get("/topics/hot")
def get_admin_hot_topics(
    limit: int = Query(20, ge=1, le=50),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    rows = db.query(SocialDynamic.content).order_by(SocialDynamic.created_at.desc()).limit(1000).all()
    counter: Counter[str] = Counter()
    for (content,) in rows:
        counter.update(social_module._extract_topics(content or ""))
    managed = []
    counter_map = dict(counter)
    for item in social_module.MANAGED_HOT_TOPICS:
        topic = social_module._normalize_topic_name(str(item.get("topic") or ""))
        managed.append({
            "id": item.get("id"),
            "topic": topic,
            "count": counter_map.get(topic, 0),
            "isDefault": counter_map.get(topic, 0) == 0,
            "sortOrder": int(item.get("sortOrder") or 0),
            "isRecommended": bool(item.get("isRecommended", False)),
            "isVisible": bool(item.get("isVisible", True)),
        })
    managed.sort(key=lambda item: (item["sortOrder"], item["topic"]))
    return envelope({"list": managed[:limit], "defaultTopics": [item["topic"] for item in managed if item.get("isVisible")]})


@router.put("/topics/default")
def update_default_topics(
    payload: AdminTopicsPayload,
    _admin: User = Depends(require_admin),
):
    topics: list[str] = []
    for raw in payload.topics:
        topic = str(raw or "").strip().lstrip("#")
        if topic and topic not in topics:
            topics.append(topic)
    if not topics:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Default topics cannot be empty")
    social_module.DEFAULT_HOT_TOPICS[:] = topics[:12]
    social_module.MANAGED_HOT_TOPICS[:] = [
        {"id": f"default-{index + 1}", "topic": topic, "sortOrder": index + 1, "isRecommended": True, "isVisible": True}
        for index, topic in enumerate(social_module.DEFAULT_HOT_TOPICS)
    ]
    return envelope({"success": True, "defaultTopics": social_module.DEFAULT_HOT_TOPICS})


@router.get("/topics")
def list_admin_topics(
    _admin: User = Depends(require_admin),
):
    items = sorted(social_module.MANAGED_HOT_TOPICS, key=lambda item: (int(item.get("sortOrder") or 0), str(item.get("topic") or "")))
    return envelope({"list": items, "total": len(items)})


@router.post("/topics")
def create_admin_topic(
    payload: dict,
    _admin: User = Depends(require_admin),
):
    topic = social_module._normalize_topic_name(str(payload.get("topic") or ""))
    if not topic:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="话题名不能为空")
    if any(social_module._normalize_topic_name(str(item.get("topic") or "")) == topic for item in social_module.MANAGED_HOT_TOPICS):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="话题已存在")
    sort_order = int(payload.get("sortOrder") or (len(social_module.MANAGED_HOT_TOPICS) + 1))
    item = {
        "id": uuid4().hex,
        "topic": topic,
        "sortOrder": sort_order,
        "isRecommended": bool(payload.get("isRecommended", True)),
        "isVisible": bool(payload.get("isVisible", True)),
    }
    social_module.MANAGED_HOT_TOPICS.append(item)
    return envelope(item)


@router.put("/topics/sort")
def sort_admin_topics(
    payload: dict,
    _admin: User = Depends(require_admin),
):
    orders = payload.get("items") or []
    order_map = {str(item.get("id")): int(item.get("sortOrder") or index + 1) for index, item in enumerate(orders) if isinstance(item, dict)}
    for item in social_module.MANAGED_HOT_TOPICS:
        item_id = str(item.get("id"))
        if item_id in order_map:
            item["sortOrder"] = order_map[item_id]
    return envelope({"success": True, "list": social_module.MANAGED_HOT_TOPICS})


@router.put("/topics/{topic_id}")
def update_admin_topic(
    topic_id: str,
    payload: dict,
    _admin: User = Depends(require_admin),
):
    item = next((topic for topic in social_module.MANAGED_HOT_TOPICS if str(topic.get("id")) == topic_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="话题不存在")
    if "topic" in payload:
        topic = social_module._normalize_topic_name(str(payload.get("topic") or ""))
        if not topic:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="话题名不能为空")
        item["topic"] = topic
    if "sortOrder" in payload:
        item["sortOrder"] = int(payload.get("sortOrder") or 0)
    if "isRecommended" in payload:
        item["isRecommended"] = bool(payload.get("isRecommended"))
    if "isVisible" in payload:
        item["isVisible"] = bool(payload.get("isVisible"))
    return envelope(item)


@router.delete("/topics/{topic_id}")
def delete_admin_topic(
    topic_id: str,
    _admin: User = Depends(require_admin),
):
    before = len(social_module.MANAGED_HOT_TOPICS)
    social_module.MANAGED_HOT_TOPICS[:] = [item for item in social_module.MANAGED_HOT_TOPICS if str(item.get("id")) != topic_id]
    if len(social_module.MANAGED_HOT_TOPICS) == before:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="话题不存在")
    return envelope({"success": True})


@router.delete("/dynamics/{dynamic_id}")
def delete_dynamic(
    dynamic_id: str,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    image_urls = _admin_parse_images(dynamic.images)

    comment_ids = [
        comment_id
        for (comment_id,) in db.query(SocialComment.id)
        .filter(SocialComment.dynamic_id == dynamic_id)
        .all()
    ]
    if comment_ids:
        db.query(SocialCommentLike).filter(SocialCommentLike.comment_id.in_(comment_ids)).delete(synchronize_session=False)
    db.query(SocialComment).filter(SocialComment.dynamic_id == dynamic_id).delete(synchronize_session=False)
    db.query(SocialLike).filter(SocialLike.dynamic_id == dynamic_id).delete(synchronize_session=False)
    db.query(SocialFavorite).filter(SocialFavorite.dynamic_id == dynamic_id).delete(synchronize_session=False)
    db.delete(dynamic)
    db.commit()

    for url in image_urls:
        if url.startswith("/api/v1/uploads/"):
            file_path = Path(__file__).resolve().parents[3] / "uploads" / url[len("/api/v1/uploads/"):]
            safe_delete_file(str(file_path))

    return envelope({"success": True})


@router.get("/emotion-records")
def list_emotion_records(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(EmotionRecord, CatProfile.name).outerjoin(CatProfile, CatProfile.id == EmotionRecord.pet_id)
    total, items = _page(query.order_by(EmotionRecord.record_time.desc()), page, pageSize)
    return envelope(
        AdminListResponse(
            list=[
                {
                    "id": record.id,
                    "petName": pet_name or record.pet_id,
                    "label": record.label,
                    "confidence": record.confidence,
                    "recordTime": record.record_time.isoformat() if record.record_time else "",
                }
                for record, pet_name in items
            ],
            total=total,
            page=page,
            pageSize=pageSize,
        ).model_dump()
    )


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    if user_id == admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete current admin")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return envelope({"success": True})


@router.get("/messages")
def list_messages(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Message, User.username, User.nickname).outerjoin(User, User.id == Message.sender_id)
    total, items = _page(query.order_by(Message.sent_at.desc()), page, pageSize)
    return envelope(
        AdminListResponse(
            list=[
                {
                    "id": msg.id,
                    "senderName": (nickname or username or msg.sender_id),
                    "receiverId": msg.receiver_id,
                    "content": msg.content[:100],
                    "messageType": msg.message_type,
                    "sentAt": msg.sent_at.isoformat() if msg.sent_at else "",
                }
                for msg, username, nickname in items
            ],
            total=total,
            page=page,
            pageSize=pageSize,
        ).model_dump()
    )


@router.get("/health-records")
def list_health_records(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    kind: str | None = Query(None),
    keyword: str | None = Query(None),
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    health_items = []
    if kind in (None, "", "weight"):
        weight_query = (
            db.query(PetWeight, CatProfile.name, User.username)
            .outerjoin(CatProfile, CatProfile.id == PetWeight.pet_id)
            .outerjoin(User, User.id == CatProfile.user_id)
        )
        if keyword:
            value = f"%{keyword.strip()}%"
            weight_query = weight_query.filter(or_(CatProfile.name.like(value), User.username.like(value)))
        for record, pet_name, username in weight_query.all():
            health_items.append(
                {
                    "id": record.id,
                    "kind": "weight",
                    "petName": pet_name or record.pet_id,
                    "owner": username or "",
                    "metric": f"{record.weight:g} kg",
                    "note": "体重记录",
                    "recordedAt": _safe_iso(record.record_date),
                }
            )

    if kind in (None, "", "feeding"):
        feeding_query = (
            db.query(FeedingRecord, CatProfile.name, User.username)
            .outerjoin(CatProfile, CatProfile.id == FeedingRecord.pet_id)
            .outerjoin(User, User.id == CatProfile.user_id)
        )
        if keyword:
            value = f"%{keyword.strip()}%"
            feeding_query = feeding_query.filter(
                or_(CatProfile.name.like(value), User.username.like(value), FeedingRecord.food_type.like(value))
            )
        for record, pet_name, username in feeding_query.all():
            health_items.append(
                {
                    "id": record.id,
                    "kind": "feeding",
                    "petName": pet_name or record.pet_id,
                    "owner": username or "",
                    "metric": f"{record.food_weight:g} g",
                    "note": record.food_type,
                    "recordedAt": _safe_iso(record.feeding_time),
                }
            )

    health_items.sort(key=lambda item: item["recordedAt"], reverse=True)
    total = len(health_items)
    start = (page - 1) * pageSize
    end = start + pageSize
    return envelope(AdminListResponse(list=health_items[start:end], total=total, page=page, pageSize=pageSize).model_dump())


@router.delete("/health-records/{kind}/{record_id}")
def delete_health_record(
    kind: str,
    record_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    model = PetWeight if kind == "weight" else FeedingRecord if kind == "feeding" else None
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported health record type")
    record = db.query(model).filter(model.id == record_id).first()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health record not found")
    db.delete(record)
    db.commit()
    return envelope({"success": True})


@router.get("/config")
def get_admin_config(
    admin: User = Depends(require_admin),
):
    return envelope(
        {
            "aiApiKey": _mask_secret(runtime_config.AI_API_KEY),
            "aiBaseUrl": runtime_config.AI_BASE_URL,
            "aiModel": runtime_config.AI_MODEL,
            "adminUsername": admin.username,
            "runtimeOnly": True,
        }
    )


@router.put("/config")
def update_admin_config(
    payload: AdminConfigPayload,
    _admin: User = Depends(require_admin),
):
    if payload.aiApiKey is not None and payload.aiApiKey.strip() and "*" not in payload.aiApiKey:
        runtime_config.AI_API_KEY = payload.aiApiKey.strip()
        ai_assistant_module.AI_API_KEY = runtime_config.AI_API_KEY
        os.environ["AI_API_KEY"] = runtime_config.AI_API_KEY
    if payload.aiBaseUrl is not None and payload.aiBaseUrl.strip():
        runtime_config.AI_BASE_URL = payload.aiBaseUrl.strip().rstrip("/")
        ai_assistant_module.AI_BASE_URL = runtime_config.AI_BASE_URL
        os.environ["AI_BASE_URL"] = runtime_config.AI_BASE_URL
    if payload.aiModel is not None and payload.aiModel.strip():
        runtime_config.AI_MODEL = payload.aiModel.strip()
        ai_assistant_module.AI_MODEL = runtime_config.AI_MODEL
        os.environ["AI_MODEL"] = runtime_config.AI_MODEL

    ai_assistant_module._ai_client = None
    return envelope({"success": True})


# ====== DELETE endpoints for all types ======

@router.delete("/pets/{pet_id}")
def delete_pet(pet_id: str, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    pet = db.query(CatProfile).filter(CatProfile.id == pet_id).first()
    if pet is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pet not found")

    avatar_to_delete = pet.avatar_url

    # 提取情绪记录中的音频路径
    emotion_records = db.query(EmotionRecord).filter(EmotionRecord.pet_id == pet_id).all()
    audio_paths: list[str] = []
    import json as _json2
    for rec in emotion_records:
        if rec.raw_result:
            try:
                raw = _json2.loads(rec.raw_result)
                p = raw.get("_audio_path") if isinstance(raw, dict) else None
                if isinstance(p, str) and p:
                    audio_paths.append(p)
            except _json2.JSONDecodeError:
                pass

    # 删除关联数据
    db.query(EmotionRecord).filter(EmotionRecord.pet_id == pet_id).delete()
    db.query(FeedingRecord).filter(FeedingRecord.pet_id == pet_id).delete()
    db.query(PetWeight).filter(PetWeight.pet_id == pet_id).delete()

    db.delete(pet); db.commit()

    # 清理物理文件
    if avatar_to_delete and avatar_to_delete.startswith("/api/v1/uploads/"):
        avatar_path = str(Path(__file__).resolve().parents[3] / "uploads" / avatar_to_delete[len("/api/v1/uploads/"):])
        safe_delete_file(avatar_path)
    for ap in audio_paths:
        safe_delete_file(ap)

    return envelope({"success": True})


@router.delete("/emotion-records/{record_id}")
def delete_emotion_record(record_id: int, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    rec = db.query(EmotionRecord).filter(EmotionRecord.id == record_id).first()
    if rec is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    # 提取音频路径
    audio_path = None
    if rec.raw_result:
        import json as _json3
        try:
            raw = _json3.loads(rec.raw_result)
            p = raw.get("_audio_path") if isinstance(raw, dict) else None
            if isinstance(p, str) and p:
                audio_path = p
        except _json3.JSONDecodeError:
            pass

    db.delete(rec); db.commit()

    if audio_path:
        safe_delete_file(audio_path)

    return envelope({"success": True})


@router.delete("/messages/{message_id}")
def delete_message(message_id: str, _admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if msg is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(msg); db.commit()
    return envelope({"success": True})
