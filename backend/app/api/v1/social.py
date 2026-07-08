import json
import re
from pathlib import Path
from collections import Counter
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, update

from app.core.dependencies import get_current_user
from app.core.dependencies import get_optional_current_user
from app.core.storage import safe_delete_file, storage_service
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.social import SocialComment, SocialCommentLike, SocialDynamic, SocialFavorite, SocialFollow, SocialLike
from app.models.user import User
from app.schemas.social import (
    CommentBrief,
    CommentCreate,
    CommentResponse,
    DynamicResponse,
    DynamicUpdate,
    DynamicsListResponse,
    FollowerResponse,
    FollowersListResponse,
    HotTopic,
    HotTopicsResponse,
    LikeResponse,
    LikedUserBrief,
    LikerListResponse,
    LikerResponse,
    FavoriteResponse,
    DeleteResponse,
    FollowResponse,
    ResponseEnvelope
)

from collections import defaultdict

router = APIRouter(prefix="/social", tags=["social"])

DEFAULT_HOT_TOPICS = ["猫咪", "新手养猫", "喵喵台"]
MANAGED_HOT_TOPICS: list[dict[str, object]] = [
    {"id": f"default-{index + 1}", "topic": topic, "sortOrder": index + 1, "isRecommended": True, "isVisible": True}
    for index, topic in enumerate(DEFAULT_HOT_TOPICS)
]


def _normalize_topic_name(value: str | None) -> str:
    return str(value or "").strip().lstrip("#")


def get_managed_hot_topics() -> list[dict[str, object]]:
    return sorted(
        [topic for topic in MANAGED_HOT_TOPICS if bool(topic.get("isVisible", True))],
        key=lambda item: (int(item.get("sortOrder") or 0), str(item.get("topic") or "")),
    )

def _save_social_image(file: UploadFile) -> str:
    return storage_service.upload(file, sub_dir="social")

def _parse_images(raw_images: str | None) -> list[str]:
    if not raw_images:
        return []
    try:
        parsed = json.loads(raw_images)
    except (TypeError, json.JSONDecodeError):
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if isinstance(item, str) and item.strip()]


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


def _serialize_dynamic(dynamic: SocialDynamic, current_user: User | None, db: Session) -> DynamicResponse:
    user = db.query(User).filter(User.id == dynamic.user_id).first()
    cat = None
    if dynamic.cat_id:
        cat = db.query(CatProfile).filter(CatProfile.id == dynamic.cat_id).first()

    images = _parse_images(dynamic.images)
    favorite_count = db.query(func.count(SocialFavorite.id)).filter(SocialFavorite.dynamic_id == dynamic.id).scalar() or 0
    is_favorited = False
    is_following = False
    if current_user:
        is_liked = (
            db.query(SocialLike)
            .filter(
                SocialLike.dynamic_id == dynamic.id,
                SocialLike.user_id == current_user.id,
                SocialLike.is_active == True,
            )
            .first()
            is not None
        )
        is_favorited = (
            db.query(SocialFavorite)
            .filter(
                SocialFavorite.dynamic_id == dynamic.id,
                SocialFavorite.user_id == current_user.id,
            )
            .first()
            is not None
        )
        is_following = (
            db.query(SocialFollow)
            .filter(
                SocialFollow.follower_id == current_user.id,
                SocialFollow.followed_user_id == dynamic.user_id,
            )
            .first()
            is not None
        )
    else:
        is_liked = False

    # Recent likers
    recent_likers = []
    if current_user:
        liker_rows = (
            db.query(SocialLike, User)
            .join(User, SocialLike.user_id == User.id)
            .filter(
                SocialLike.dynamic_id == dynamic.id,
                SocialLike.is_active == True,
            )
            .order_by(SocialLike.created_at.desc())
            .limit(3)
            .all()
        )
        recent_likers = [
            {"user_id": u.id, "username": _display_name(u), "avatar": _avatar_url(u)}
            for _, u in liker_rows
        ]

    # Latest comment
    latest_comment = None
    latest_c = (
        db.query(SocialComment)
        .filter(SocialComment.dynamic_id == dynamic.id)
        .order_by(SocialComment.created_at.desc())
        .first()
    )
    if latest_c:
        c_user = db.query(User).filter(User.id == latest_c.user_id).first()
        if c_user:
            latest_comment = {
                "user_id": c_user.id,
                "username": _display_name(c_user),
                "avatar": _avatar_url(c_user),
                "content": latest_c.content,
                "created_at": latest_c.created_at.isoformat() if latest_c.created_at else "",
            }

    return DynamicResponse(
        id=dynamic.id,
        user_id=dynamic.user_id,
        cat_id=dynamic.cat_id,
        username=_display_name(user),
        cat_name=cat.name if cat else None,
        avatar=_avatar_url(user),
        content=dynamic.content,
        images=images,
        like_count=dynamic.like_count,
        comment_count=dynamic.comment_count,
        favorite_count=int(favorite_count),
        created_at=dynamic.created_at.isoformat() if dynamic.created_at else "",
        is_recommended=bool(dynamic.is_recommended),
        recommended_at=dynamic.recommended_at.isoformat() if dynamic.recommended_at else None,
        is_liked=is_liked,
        is_favorited=is_favorited,
        is_following=is_following,
        is_owner=bool(current_user and dynamic.user_id == current_user.id),
        recent_likers=recent_likers,
        latest_comment=latest_comment,
    )


def _serialize_dynamic_list(items: list[SocialDynamic], current_user: User | None, db: Session) -> list[DynamicResponse]:
    if not items:
        return []

    user_ids = {item.user_id for item in items}
    dynamic_ids = {item.id for item in items}

    liked_ids: set[str] = set()
    favorited_ids: set[str] = set()
    following_user_ids: set[str] = set()
    if current_user and dynamic_ids:
        like_rows = (
            db.query(SocialLike.dynamic_id)
            .filter(
                SocialLike.dynamic_id.in_(dynamic_ids),
                SocialLike.user_id == current_user.id,
                SocialLike.is_active == True,
            )
            .all()
        )
        liked_ids = {dynamic_id for (dynamic_id,) in like_rows}

        favorite_rows = (
            db.query(SocialFavorite.dynamic_id)
            .filter(
                SocialFavorite.dynamic_id.in_(dynamic_ids),
                SocialFavorite.user_id == current_user.id,
            )
            .all()
        )
        favorited_ids = {dynamic_id for (dynamic_id,) in favorite_rows}

        followed_rows = (
            db.query(SocialFollow.followed_user_id)
            .filter(
                SocialFollow.followed_user_id.in_(user_ids),
                SocialFollow.follower_id == current_user.id,
            )
            .all()
        )
        following_user_ids = {user_id for (user_id,) in followed_rows}

    favorite_counts = {}
    favorite_rows = db.query(SocialFavorite.dynamic_id, func.count(SocialFavorite.id)).filter(SocialFavorite.dynamic_id.in_(dynamic_ids)).group_by(SocialFavorite.dynamic_id).all()
    favorite_counts = {dynamic_id: count for dynamic_id, count in favorite_rows}

    # Batch query recent likers (top 3 per dynamic)
    recent_likers_map: dict[str, list[dict]] = {}
    if dynamic_ids and current_user:
        like_rows = (
            db.query(SocialLike.dynamic_id, SocialLike.user_id)
            .filter(
                SocialLike.dynamic_id.in_(dynamic_ids),
                SocialLike.is_active == True,
            )
            .order_by(SocialLike.dynamic_id, SocialLike.created_at.desc())
            .all()
        )
        liker_user_ids = {row.user_id for row in like_rows}
        liker_user_map: dict[str, User] = {}
        if liker_user_ids:
            for u in db.query(User).filter(User.id.in_(liker_user_ids)).all():
                liker_user_map[u.id] = u
        temp_likers: dict[str, list] = defaultdict(list)
        for row in like_rows:
            if len(temp_likers[row.dynamic_id]) < 3:
                user = liker_user_map.get(row.user_id)
                if user:
                    temp_likers[row.dynamic_id].append({
                        "user_id": user.id,
                        "username": _display_name(user),
                        "avatar": _avatar_url(user),
                    })
        recent_likers_map = dict(temp_likers)

    # Batch query latest comment per dynamic
    latest_comment_map: dict[str, dict | None] = {}
    if dynamic_ids:
        subq = (
            db.query(
                SocialComment.dynamic_id,
                func.max(SocialComment.created_at).label("max_created")
            )
            .filter(SocialComment.dynamic_id.in_(dynamic_ids))
            .group_by(SocialComment.dynamic_id)
            .subquery()
        )
        latest_comments = (
            db.query(SocialComment)
            .join(subq,
                (SocialComment.dynamic_id == subq.c.dynamic_id) &
                (SocialComment.created_at == subq.c.max_created))
            .all()
        )
        comment_user_ids = {c.user_id for c in latest_comments}
        comment_user_map: dict[str, User] = {}
        if comment_user_ids:
            for u in db.query(User).filter(User.id.in_(comment_user_ids)).all():
                comment_user_map[u.id] = u
        for c in latest_comments:
            user = comment_user_map.get(c.user_id)
            if user:
                latest_comment_map[c.dynamic_id] = {
                    "user_id": user.id,
                    "username": _display_name(user),
                    "avatar": _avatar_url(user),
                    "content": c.content,
                    "created_at": c.created_at.isoformat() if c.created_at else "",
                }

    serialized: list[dict] = []
    for dynamic in items:
        data = DynamicResponse(
            id=dynamic.id,
            user_id=dynamic.user_id,
            cat_id=dynamic.cat_id,
            username=_display_name(dynamic.user),
            cat_name=dynamic.cat.name if dynamic.cat else None,
            avatar=_avatar_url(dynamic.user),
            content=dynamic.content,
            images=_parse_images(dynamic.images),
            like_count=dynamic.like_count,
            comment_count=dynamic.comment_count,
            favorite_count=int(favorite_counts.get(dynamic.id, 0)),
            created_at=dynamic.created_at.isoformat() if dynamic.created_at else "",
            is_recommended=bool(dynamic.is_recommended),
            recommended_at=dynamic.recommended_at.isoformat() if dynamic.recommended_at else None,
            is_liked=dynamic.id in liked_ids,
            is_favorited=dynamic.id in favorited_ids,
            is_following=dynamic.user_id in following_user_ids,
            is_owner=bool(current_user and dynamic.user_id == current_user.id),
            recent_likers=recent_likers_map.get(dynamic.id, []),
            latest_comment=latest_comment_map.get(dynamic.id),
        )
        serialized.append(data)

    return serialized


def _serialize_comment(comment: SocialComment, current_user: User, db: Session) -> CommentResponse:
    user = db.query(User).filter(User.id == comment.user_id).first()
    like_count = db.query(func.count(SocialCommentLike.id)).filter(SocialCommentLike.comment_id == comment.id).scalar() or 0
    is_liked = False
    if current_user:
        is_liked = (
            db.query(SocialCommentLike)
            .filter(
                SocialCommentLike.comment_id == comment.id,
                SocialCommentLike.user_id == current_user.id,
            )
            .first()
            is not None
        )
    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        username=_display_name(user),
        avatar=_avatar_url(user),
        dynamic_id=comment.dynamic_id,
        content=comment.content,
        created_at=comment.created_at.isoformat() if comment.created_at else "",
        like_count=int(like_count),
        is_liked=is_liked,
        is_owner=comment.user_id == current_user.id,
    )


def _extract_topics(content: str) -> list[str]:
    # Match hashtag words like #猫咪健康 or #catlife (length 1-20), excluding spaces and '#'.
    raw = re.findall(r"#([^\s#]{1,20})", content or "")
    return [item.strip() for item in raw if item.strip()]


@router.post("/dynamics", response_model=ResponseEnvelope[DynamicResponse])
async def publish_dynamic(
    content: str = Form(...),
    cat_id: str | None = Form(None),
    catId: str | None = Form(None),
    images: list[UploadFile] | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resolved_cat_id = cat_id or catId
    if resolved_cat_id:
        cat = (
            db.query(CatProfile)
            .filter(CatProfile.id == resolved_cat_id, CatProfile.user_id == current_user.id)
            .first()
        )
        if cat is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")

    image_urls = [_save_social_image(file) for file in images or []]

    dynamic = SocialDynamic(
        id=str(uuid4()),
        user_id=current_user.id,
        cat_id=resolved_cat_id,
        content=content,
        images=json.dumps(image_urls, ensure_ascii=False),
        like_count=0,
        comment_count=0,
    )
    db.add(dynamic)
    db.commit()
    db.refresh(dynamic)

    return ResponseEnvelope(data=_serialize_dynamic(dynamic, current_user, db))


@router.get("/dynamics/list", response_model=ResponseEnvelope[DynamicsListResponse])
def list_dynamics(
    page: int = Query(1, ge=1),
    cursor: str | None = Query(None),
    limit: int = Query(10, ge=1, alias="pageSize"),
    catId: str | None = Query(None),
    scope: str = Query("all"),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SocialDynamic).options(
        joinedload(SocialDynamic.user),
        joinedload(SocialDynamic.cat)
    )
    if catId:
        query = query.filter(SocialDynamic.cat_id == catId)

    if scope == "following" and current_user is not None:
        followed_user_ids = (
            db.query(SocialFollow.followed_user_id)
            .filter(SocialFollow.follower_id == current_user.id)
            .all()
        )
        followed_user_id_set = {user_id for (user_id,) in followed_user_ids}
        if not followed_user_id_set:
            return ResponseEnvelope(
                data=DynamicsListResponse(
                    list=[],
                    cursor=None,
                    limit=limit,
                )
            )
        query = query.filter(SocialDynamic.user_id.in_(followed_user_id_set))
    elif scope == "following":
        return ResponseEnvelope(
            data=DynamicsListResponse(
                list=[],
                cursor=None,
                limit=limit,
            )
        )

    total = query.count()

    if cursor:
        try:
            from dateutil.parser import isoparse
            cursor_dt = isoparse(cursor)
            query = query.filter(SocialDynamic.created_at < cursor_dt)
        except Exception:
            pass
        items = (
            query.order_by(
                SocialDynamic.is_recommended.desc(),
                SocialDynamic.recommended_at.desc(),
                SocialDynamic.created_at.desc(),
            )
            .limit(limit + 1)
            .all()
        )
    else:
        items = (
            query.order_by(
                SocialDynamic.is_recommended.desc(),
                SocialDynamic.recommended_at.desc(),
                SocialDynamic.created_at.desc(),
            )
            .offset((page - 1) * limit)
            .limit(limit + 1)
            .all()
        )

    has_more = len(items) > limit
    items = items[:limit]

    next_cursor = None
    if has_more and items:
        next_cursor = items[-1].created_at.isoformat()

    try:
        safe_list = _serialize_dynamic_list(items, current_user, db)
    except Exception as exc:
        print(f"social.list_dynamics serialization failed: {exc}")
        safe_list = []

    return ResponseEnvelope(
        data=DynamicsListResponse(
            list=safe_list,
            total=total,
            page=page,
            page_size=limit,
            cursor=next_cursor,
            limit=limit,
            has_more=has_more,
        )
    )


@router.get("/dynamics/search", response_model=ResponseEnvelope[DynamicsListResponse])
def search_dynamics(
    q: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=50),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    keyword = q.strip().lstrip("#")
    if not keyword:
        return ResponseEnvelope(
            data=DynamicsListResponse(
                list=[],
                total=0,
                page=page,
                page_size=pageSize,
                limit=pageSize,
                has_more=False,
                cursor=None,
            )
        )

    pattern = f"%{keyword}%"
    query = (
        db.query(SocialDynamic)
        .options(joinedload(SocialDynamic.user), joinedload(SocialDynamic.cat))
        .join(User, SocialDynamic.user_id == User.id)
        .outerjoin(CatProfile, SocialDynamic.cat_id == CatProfile.id)
        .filter(
            or_(
                SocialDynamic.content.like(pattern),
                User.username.like(pattern),
                User.nickname.like(pattern),
                CatProfile.name.like(pattern),
            )
        )
        .order_by(SocialDynamic.is_recommended.desc(), SocialDynamic.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()
    return ResponseEnvelope(
        data=DynamicsListResponse(
            list=_serialize_dynamic_list(items, current_user, db),
            total=total,
            page=page,
            page_size=pageSize,
            limit=pageSize,
            has_more=(page * pageSize) < total,
            cursor=None,
        )
    )


@router.get("/users/followers/list", response_model=ResponseEnvelope[FollowersListResponse])
def list_followers(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    follower_rows = (
        db.query(User, SocialFollow.created_at)
        .join(SocialFollow, SocialFollow.follower_id == User.id)
        .filter(SocialFollow.followed_user_id == current_user.id)
        .order_by(SocialFollow.created_at.desc())
        .all()
    )

    total = len(follower_rows)
    start = (page - 1) * pageSize
    end = start + pageSize
    items = follower_rows[start:end]

    user_ids = [user.id for user, _created_at in items]
    following_ids: set[str] = set()
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

    return ResponseEnvelope(
        data=FollowersListResponse(
            list=[
                FollowerResponse(
                    id=user.id,
                    user_id=user.id,
                    username=user.username,
                    nickname=_display_name(user),
                    avatar=_avatar_url(user),
                    last_online_at=created_at.isoformat() if created_at else "",
                    is_online=getattr(user, "is_online", False), # TODO: actual online status
                    is_following=user.id in following_ids,
                )
                for user, created_at in items
            ],
            total=total,
            page=page,
            page_size=pageSize,
        )
    )


@router.get("/topics/hot", response_model=ResponseEnvelope[HotTopicsResponse])
def list_hot_topics(
    limit: int = Query(8, ge=1, le=30),
    sampleSize: int = Query(500, ge=50, le=2000),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(SocialDynamic.content)
        .order_by(SocialDynamic.created_at.desc())
        .limit(sampleSize)
        .all()
    )

    counter: Counter[str] = Counter()
    for (content,) in rows:
        counter.update(_extract_topics(content or ""))

    configured = get_managed_hot_topics()
    used: set[str] = set()
    hot_list: list[HotTopic] = []
    for item in configured:
        topic = _normalize_topic_name(str(item.get("topic") or ""))
        if not topic or topic in used:
            continue
        used.add(topic)
        hot_list.append(HotTopic(topic=topic, count=counter.get(topic, 0), is_default=counter.get(topic, 0) == 0))
        if len(hot_list) >= limit:
            break

    if len(hot_list) < limit:
        for topic, count in counter.most_common(limit):
            if topic in used:
                continue
            hot_list.append(HotTopic(topic=topic, count=count, is_default=False))
            used.add(topic)
            if len(hot_list) >= limit:
                break

    if not hot_list:
        hot_list = [HotTopic(topic=topic, count=0, is_default=True) for topic in DEFAULT_HOT_TOPICS[:limit]]

    return ResponseEnvelope(data=HotTopicsResponse(list=hot_list))


@router.get("/dynamics/{dynamic_id}", response_model=ResponseEnvelope[DynamicResponse])
def get_dynamic_detail(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    comments = (
        db.query(SocialComment)
        .filter(SocialComment.dynamic_id == dynamic_id)
        .order_by(SocialComment.created_at.asc())
        .all()
    )

    comment_user_ids = {comment.user_id for comment in comments}
    comment_user_map: dict[str, str] = {}
    if comment_user_ids:
        comment_user_rows = db.query(User).filter(User.id.in_(comment_user_ids)).all()
        comment_user_map = {item.id: _display_name(item) for item in comment_user_rows}

    comment_like_ids: set[str] = set()
    if comments and current_user:
        comment_ids = {comment.id for comment in comments}
        liked_comment_rows = (
            db.query(SocialCommentLike.comment_id)
            .filter(
                SocialCommentLike.comment_id.in_(comment_ids),
                SocialCommentLike.user_id == current_user.id,
            )
            .all()
        )
        comment_like_ids = {comment_id for (comment_id,) in liked_comment_rows}

    try:
        data = _serialize_dynamic(dynamic, current_user, db)
        data.comments = [
            CommentResponse(
                id=comment.id,
                user_id=comment.user_id,
                username=comment_user_map.get(comment.user_id, ""),
                avatar=_avatar_url(db.query(User).filter(User.id == comment.user_id).first()),
                dynamic_id=comment.dynamic_id,
                content=comment.content,
                created_at=comment.created_at.isoformat() if comment.created_at else "",
                like_count=int(db.query(func.count(SocialCommentLike.id)).filter(SocialCommentLike.comment_id == comment.id).scalar() or 0),
                is_liked=comment.id in comment_like_ids,
                is_owner=comment.user_id == current_user.id,
            )
            for comment in comments
        ]
    except Exception as exc:
        print(f"social.get_dynamic_detail failed id={dynamic_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Dynamic serialization failed") from exc

    return ResponseEnvelope(data=data)


@router.put("/dynamics/{dynamic_id}", response_model=ResponseEnvelope[DynamicResponse])
def update_dynamic(
    dynamic_id: str,
    payload: DynamicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")
    if dynamic.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    dynamic.content = payload.content.strip()
    db.commit()
    db.refresh(dynamic)
    return ResponseEnvelope(data=_serialize_dynamic(dynamic, current_user, db))


@router.post("/dynamics/{dynamic_id}/like", response_model=ResponseEnvelope[LikeResponse])
def like_dynamic(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    like = (
        db.query(SocialLike)
        .filter(SocialLike.dynamic_id == dynamic_id, SocialLike.user_id == current_user.id)
        .first()
    )
    if like is None:
        like = SocialLike(id=str(uuid4()), dynamic_id=dynamic_id, user_id=current_user.id, is_active=True)
        db.add(like)
        db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).update({SocialDynamic.like_count: SocialDynamic.like_count + 1})
    elif not like.is_active:
        like.is_active = True
        db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).update({SocialDynamic.like_count: SocialDynamic.like_count + 1})

    db.commit()
    db.refresh(dynamic)

    return ResponseEnvelope(data=LikeResponse(is_liked=True, like_count=dynamic.like_count))


@router.delete("/dynamics/{dynamic_id}/like", response_model=ResponseEnvelope[LikeResponse])
def unlike_dynamic(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    like = (
        db.query(SocialLike)
        .filter(SocialLike.dynamic_id == dynamic_id, SocialLike.user_id == current_user.id)
        .first()
    )
    if like and like.is_active:
        like.is_active = False
        dynamic.like_count = max((dynamic.like_count or 0) - 1, 0)
        db.commit()

    db.refresh(dynamic)
    return ResponseEnvelope(data=LikeResponse(is_liked=False, like_count=dynamic.like_count))


@router.post("/dynamics/{dynamic_id}/comments", response_model=ResponseEnvelope[CommentResponse])
def post_comment(
    dynamic_id: str,
    payload: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    comment = SocialComment(
        id=str(uuid4()),
        dynamic_id=dynamic_id,
        user_id=current_user.id,
        content=payload.content,
    )
    db.add(comment)
    db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).update({SocialDynamic.comment_count: SocialDynamic.comment_count + 1})
    db.commit()
    db.refresh(comment)

    return ResponseEnvelope(data=_serialize_comment(comment, current_user, db))


@router.post("/dynamics/{dynamic_id}/favorite", response_model=ResponseEnvelope[FavoriteResponse])
def toggle_favorite_dynamic(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    favorite = (
        db.query(SocialFavorite)
        .filter(
            SocialFavorite.dynamic_id == dynamic_id,
            SocialFavorite.user_id == current_user.id,
        )
        .first()
    )
    if favorite is None:
        db.add(SocialFavorite(id=str(uuid4()), dynamic_id=dynamic_id, user_id=current_user.id))
        is_favorited = True
    else:
        db.delete(favorite)
        is_favorited = False
    db.commit()

    favorite_count = db.query(func.count(SocialFavorite.id)).filter(SocialFavorite.dynamic_id == dynamic_id).scalar() or 0
    return ResponseEnvelope(
        data=FavoriteResponse(is_favorited=is_favorited, favorite_count=int(favorite_count))
    )


@router.post("/users/{user_id}/follow", response_model=ResponseEnvelope[FollowResponse])
def toggle_follow_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")

    target_user = db.query(User).filter(User.id == user_id).first()
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    follow = (
        db.query(SocialFollow)
        .filter(
            SocialFollow.follower_id == current_user.id,
            SocialFollow.followed_user_id == user_id,
        )
        .first()
    )
    if follow is None:
        db.add(SocialFollow(id=str(uuid4()), follower_id=current_user.id, followed_user_id=user_id))
        is_following = True
    else:
        db.delete(follow)
        is_following = False
    db.commit()

    follower_count = (
        db.query(func.count(SocialFollow.id))
        .filter(SocialFollow.followed_user_id == user_id)
        .scalar()
        or 0
    )

    return ResponseEnvelope(
        data=FollowResponse(is_following=is_following, follower_count=int(follower_count))
    )


@router.post("/comments/{comment_id}/like", response_model=ResponseEnvelope[LikeResponse])
def toggle_like_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(SocialComment).filter(SocialComment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    like = (
        db.query(SocialCommentLike)
        .filter(
            SocialCommentLike.comment_id == comment_id,
            SocialCommentLike.user_id == current_user.id,
        )
        .first()
    )
    if like is None:
        db.add(SocialCommentLike(id=str(uuid4()), comment_id=comment_id, user_id=current_user.id))
        is_liked = True
    else:
        db.delete(like)
        is_liked = False
    db.commit()

    like_count = db.query(func.count(SocialCommentLike.id)).filter(SocialCommentLike.comment_id == comment_id).scalar() or 0
    return ResponseEnvelope(
        data=LikeResponse(is_liked=is_liked, like_count=int(like_count))
    )


@router.delete("/comments/{comment_id}", response_model=ResponseEnvelope[DeleteResponse])
def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(SocialComment).filter(SocialComment.id == comment_id).first()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == comment.dynamic_id).first()
    if comment.user_id != current_user.id and (dynamic is None or dynamic.user_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    db.delete(comment)
    if dynamic:
        dynamic.comment_count = max(dynamic.comment_count - 1, 0)

    db.commit()

    return ResponseEnvelope(data=DeleteResponse(success=True))


@router.delete("/dynamics/{dynamic_id}", response_model=ResponseEnvelope[DeleteResponse])
def delete_dynamic(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    if dynamic.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    # 提取图片路径（在删除数据库记录之前）
    image_urls = _parse_images(dynamic.images)

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

    # 数据库提交成功后再尝试删除物理图片文件
    for url in image_urls:
        # API 路径如 /api/v1/uploads/social/xxx.jpg 转换为本地路径
        if url.startswith("/api/v1/uploads/"):
            file_path = Path(__file__).resolve().parents[3] / "uploads" / url[len("/api/v1/uploads/"):]
            safe_delete_file(str(file_path))

    return ResponseEnvelope(data=DeleteResponse(success=True))


@router.get("/dynamics/my/list", response_model=ResponseEnvelope[DynamicsListResponse])
def list_my_dynamics(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    catId: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(SocialDynamic)
        .options(joinedload(SocialDynamic.user), joinedload(SocialDynamic.cat))
        .filter(SocialDynamic.user_id == current_user.id)
    )
    if catId:
        query = query.filter(SocialDynamic.cat_id == catId)

    total = query.count()
    items = (
        query.order_by(SocialDynamic.created_at.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    try:
        safe_list = _serialize_dynamic_list(items, current_user, db)
    except Exception as exc:
        print(f"social.list_my_dynamics serialization failed: {exc}")
        safe_list = []

    return ResponseEnvelope(
        data=DynamicsListResponse(
            list=safe_list,
            total=total,
            page=page,
            page_size=pageSize,
            limit=pageSize,
            has_more=(page * pageSize) < total,
            cursor=None
        )
    )


@router.get("/dynamics/{dynamic_id}/likers", response_model=ResponseEnvelope[LikerListResponse])
def list_dynamic_likers(
    dynamic_id: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    query = (
        db.query(SocialLike, User)
        .join(User, SocialLike.user_id == User.id)
        .filter(
            SocialLike.dynamic_id == dynamic_id,
            SocialLike.is_active == True,
        )
        .order_by(SocialLike.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * pageSize).limit(pageSize).all()

    return ResponseEnvelope(
        data=LikerListResponse(
            list=[
                LikerResponse(
                    user_id=user.id,
                    username=_display_name(user),
                    avatar=_avatar_url(user),
                )
                for _, user in items
            ],
            total=total,
            page=page,
            page_size=pageSize,
        )
    )
