import json
import re
from pathlib import Path
from collections import Counter
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, update

from app.core.dependencies import get_current_user
from app.core.dependencies import get_optional_current_user
from app.core.storage import storage_service
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.social import SocialComment, SocialCommentLike, SocialDynamic, SocialFavorite, SocialFollow, SocialLike
from app.models.user import User
from app.schemas.social import (
    CommentCreate,
    CommentResponse,
    DynamicResponse,
    DynamicsListResponse,
    FollowerResponse,
    FollowersListResponse,
    HotTopic,
    HotTopicsResponse,
    LikeResponse,
    FavoriteResponse,
    DeleteResponse,
    FollowResponse,
    ResponseEnvelope
)

router = APIRouter(prefix="/social", tags=["social"])

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

    return DynamicResponse(
        id=dynamic.id,
        user_id=dynamic.user_id,
        cat_id=dynamic.cat_id,
        username=user.username if user else "",
        cat_name=cat.name if cat else None,
        avatar=getattr(user, "avatar", ""), # TODO: actual avatar
        content=dynamic.content,
        images=images,
        like_count=dynamic.like_count,
        comment_count=dynamic.comment_count,
        favorite_count=int(favorite_count),
        created_at=dynamic.created_at.isoformat() if dynamic.created_at else "",
        is_liked=is_liked,
        is_favorited=is_favorited,
        is_following=is_following,
        is_owner=bool(current_user and dynamic.user_id == current_user.id),
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

    serialized: list[dict] = []
    for dynamic in items:
        # TODO: avatar handling
        # User model may need an avatar field
        data = DynamicResponse(
            id=dynamic.id,
            user_id=dynamic.user_id,
            cat_id=dynamic.cat_id,
            username=dynamic.user.username if dynamic.user else "",
            cat_name=dynamic.cat.name if dynamic.cat else None,
            avatar=getattr(dynamic.user, "avatar", "") if dynamic.user else "",
            content=dynamic.content,
            images=_parse_images(dynamic.images),
            like_count=dynamic.like_count,
            comment_count=dynamic.comment_count,
            favorite_count=int(favorite_counts.get(dynamic.id, 0)),
            created_at=dynamic.created_at.isoformat() if dynamic.created_at else "",
            is_liked=dynamic.id in liked_ids,
            is_favorited=dynamic.id in favorited_ids,
            is_following=dynamic.user_id in following_user_ids,
            is_owner=bool(current_user and dynamic.user_id == current_user.id),
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
        username=user.username if user else "",
        avatar=getattr(user, "avatar", ""), # TODO
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

    if cursor:
        try:
            from dateutil.parser import isoparse
            cursor_dt = isoparse(cursor)
            query = query.filter(SocialDynamic.created_at < cursor_dt)
        except Exception:
            pass

    items = (
        query.order_by(SocialDynamic.created_at.desc())
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
            cursor=next_cursor,
            limit=limit,
            has_more=has_more,
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
                    nickname=getattr(user, "nickname", user.username), # TODO: actual nickname mapping
                    avatar=getattr(user, "avatar", ""), # TODO
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

    hot_list = [
        HotTopic(topic=topic, count=count)
        for topic, count in counter.most_common(limit)
    ]

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
        comment_user_rows = db.query(User.id, User.username).filter(User.id.in_(comment_user_ids)).all()
        comment_user_map = {user_id: username for user_id, username in comment_user_rows}

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
                avatar="",  # TODO: map actual user avatar
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
        dynamic.like_count += 1
    elif not like.is_active:
        like.is_active = True
        db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).update({SocialDynamic.like_count: SocialDynamic.like_count + 1})
        dynamic.like_count += 1

    db.commit()

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
        db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).update({SocialDynamic.like_count: func.greatest(SocialDynamic.like_count - 1, 0)})
        dynamic.like_count = max(dynamic.like_count - 1, 0)
        db.commit()

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
    dynamic.comment_count += 1
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

    db.query(SocialComment).filter(SocialComment.dynamic_id == dynamic_id).delete()
    db.query(SocialLike).filter(SocialLike.dynamic_id == dynamic_id).delete()
    db.delete(dynamic)
    db.commit()

    return ResponseEnvelope(data=DeleteResponse(success=True))


@router.get("/dynamics/my/list", response_model=ResponseEnvelope[DynamicsListResponse])
def list_my_dynamics(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    catId: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SocialDynamic).filter(SocialDynamic.user_id == current_user.id)
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
        )
    )
