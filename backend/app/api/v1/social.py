import json
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.social import SocialComment, SocialDynamic, SocialLike
from app.models.user import User
from app.schemas.social import CommentCreate

router = APIRouter(prefix="/api/v1/social", tags=["social"])


def _serialize_dynamic(dynamic: SocialDynamic, current_user: User, db: Session) -> dict:
    user = db.query(User).filter(User.id == dynamic.user_id).first()
    cat = None
    if dynamic.cat_id:
        cat = db.query(CatProfile).filter(CatProfile.id == dynamic.cat_id).first()

    images = json.loads(dynamic.images) if dynamic.images else []
    is_liked = (
        db.query(SocialLike)
        .filter(
            SocialLike.dynamic_id == dynamic.id,
            SocialLike.user_id == current_user.id,
            SocialLike.is_active.is_(True),
        )
        .first()
        is not None
    )

    return {
        "id": dynamic.id,
        "userId": dynamic.user_id,
        "catId": dynamic.cat_id,
        "username": user.username if user else "",
        "catName": cat.name if cat else None,
        "avatar": "",
        "content": dynamic.content,
        "images": images,
        "likeCount": dynamic.like_count,
        "commentCount": dynamic.comment_count,
        "createdAt": dynamic.created_at.isoformat() if dynamic.created_at else "",
        "isLiked": is_liked,
        "isOwner": dynamic.user_id == current_user.id,
    }


def _serialize_comment(comment: SocialComment, current_user: User, db: Session) -> dict:
    user = db.query(User).filter(User.id == comment.user_id).first()
    return {
        "id": comment.id,
        "userId": comment.user_id,
        "username": user.username if user else "",
        "avatar": "",
        "dynamicId": comment.dynamic_id,
        "content": comment.content,
        "createdAt": comment.created_at.isoformat() if comment.created_at else "",
        "isOwner": comment.user_id == current_user.id,
    }


@router.post("/dynamics")
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

    image_urls = [file.filename for file in images or []]

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

    return {"code": 200, "msg": "success", "data": _serialize_dynamic(dynamic, current_user, db)}


@router.get("/dynamics/list")
def list_dynamics(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    catId: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(SocialDynamic)
    if catId:
        query = query.filter(SocialDynamic.cat_id == catId)

    total = query.count()
    items = (
        query.order_by(SocialDynamic.created_at.desc())
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [_serialize_dynamic(item, current_user, db) for item in items],
            "total": total,
            "page": page,
            "pageSize": pageSize,
        },
    }


@router.get("/dynamics/{dynamic_id}")
def get_dynamic_detail(
    dynamic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dynamic = db.query(SocialDynamic).filter(SocialDynamic.id == dynamic_id).first()
    if dynamic is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dynamic not found")

    return {"code": 200, "msg": "success", "data": _serialize_dynamic(dynamic, current_user, db)}


@router.post("/dynamics/{dynamic_id}/like")
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
        dynamic.like_count += 1
    elif not like.is_active:
        like.is_active = True
        dynamic.like_count += 1

    db.commit()

    return {
        "code": 200,
        "msg": "success",
        "data": {"isLiked": True, "likeCount": dynamic.like_count},
    }


@router.delete("/dynamics/{dynamic_id}/like")
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
        dynamic.like_count = max(dynamic.like_count - 1, 0)
        db.commit()

    return {
        "code": 200,
        "msg": "success",
        "data": {"isLiked": False, "likeCount": dynamic.like_count},
    }


@router.post("/dynamics/{dynamic_id}/comments")
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
    dynamic.comment_count += 1
    db.commit()
    db.refresh(comment)

    return {"code": 200, "msg": "success", "data": _serialize_comment(comment, current_user, db)}


@router.delete("/comments/{comment_id}")
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

    return {"code": 200, "msg": "success", "data": {"success": True}}


@router.delete("/dynamics/{dynamic_id}")
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

    return {"code": 200, "msg": "success", "data": {"success": True}}


@router.get("/dynamics/my/list")
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

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "list": [_serialize_dynamic(item, current_user, db) for item in items],
            "total": total,
            "page": page,
            "pageSize": pageSize,
        },
    }
