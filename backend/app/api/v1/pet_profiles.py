from uuid import uuid4
from pathlib import Path
import base64
import binascii
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.user import User
from app.schemas.cat_profile import (
    CatProfileActionResponseEnvelope,
    CatProfileCreate,
    CatProfileListResponseEnvelope,
    CatProfileResponse,
    CatProfileResponseEnvelope,
    CatProfileUpdate,
)

router = APIRouter(prefix="/pet-profiles", tags=["pet-profiles"])

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"
CAT_UPLOAD_DIR = UPLOAD_ROOT / "cats"
CAT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _persist_avatar_if_data_url(avatar_url: str | None) -> str | None:
    if not avatar_url:
        return avatar_url
    if not avatar_url.startswith("data:image/"):
        return avatar_url

    match = re.match(r"^data:image/([a-zA-Z0-9.+-]+);base64,(.+)$", avatar_url)
    if not match:
        return avatar_url

    ext = match.group(1).lower().replace("jpeg", "jpg")
    payload = match.group(2)
    if ext not in {"jpg", "png", "gif", "webp", "bmp"}:
        ext = "jpg"

    try:
        binary = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error):
        return avatar_url

    filename = f"{uuid4().hex}.{ext}"
    target = CAT_UPLOAD_DIR / filename
    target.write_bytes(binary)
    return f"/api/v1/uploads/cats/{filename}"


def _serialize_cat_profile(cat_profile: CatProfile) -> dict:
    return CatProfileResponse.model_validate(cat_profile).model_dump()


@router.post("", response_model=CatProfileResponseEnvelope)
def create_cat_profile(
    payload: CatProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload_data = payload.model_dump()
    payload_data["avatar_url"] = _persist_avatar_if_data_url(payload_data.get("avatar_url"))

    cat_profile = CatProfile(
        id=str(uuid4()),
        user_id=current_user.id,
        **payload_data,
    )
    db.add(cat_profile)
    db.commit()
    db.refresh(cat_profile)
    return {"code": 200, "msg": "success", "data": _serialize_cat_profile(cat_profile)}


@router.get("/list", response_model=CatProfileListResponseEnvelope)
def list_cat_profiles(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # SQL Server requires ORDER BY when OFFSET/LIMIT is used.
    query = (
        db.query(CatProfile)
        .filter(CatProfile.user_id == current_user.id)
        .order_by(CatProfile.created_at.desc())
    )
    total = query.count()
    cat_profiles = query.offset((page - 1) * pageSize).limit(pageSize).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": [_serialize_cat_profile(cat_profile) for cat_profile in cat_profiles],
        },
    }


@router.get("/{profile_id}", response_model=CatProfileResponseEnvelope)
def get_cat_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cat_profile = (
        db.query(CatProfile)
        .filter(CatProfile.id == profile_id, CatProfile.user_id == current_user.id)
        .first()
    )
    if cat_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")
    return {"code": 200, "msg": "success", "data": _serialize_cat_profile(cat_profile)}


@router.put("/{profile_id}", response_model=CatProfileResponseEnvelope)
def update_cat_profile(
    profile_id: str,
    payload: CatProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cat_profile = (
        db.query(CatProfile)
        .filter(CatProfile.id == profile_id, CatProfile.user_id == current_user.id)
        .first()
    )
    if cat_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")

    update_data = payload.model_dump(exclude_unset=True)
    if "avatar_url" in update_data:
        update_data["avatar_url"] = _persist_avatar_if_data_url(update_data.get("avatar_url"))
    for field_name, field_value in update_data.items():
        setattr(cat_profile, field_name, field_value)

    db.commit()
    db.refresh(cat_profile)
    return {"code": 200, "msg": "success", "data": _serialize_cat_profile(cat_profile)}


@router.delete("/{profile_id}", response_model=CatProfileActionResponseEnvelope)
def delete_cat_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cat_profile = (
        db.query(CatProfile)
        .filter(CatProfile.id == profile_id, CatProfile.user_id == current_user.id)
        .first()
    )
    if cat_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")

    db.delete(cat_profile)
    db.commit()
    return {"code": 200, "msg": "删除成功", "data": None}
