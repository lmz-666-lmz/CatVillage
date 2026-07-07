from uuid import uuid4
from pathlib import Path
import base64
import binascii
import re

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_MAX_BYTES
from app.core.dependencies import get_current_user
from app.core.storage import safe_delete_file
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.emotion_record import EmotionRecord
from app.models.health import PetWeight, FeedingRecord
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
    avatar_url = avatar_url.strip()
    if not avatar_url.startswith("data:image/"):
        return avatar_url

    match = re.match(r"^data:image/([a-zA-Z0-9.+-]+);base64,(.+)$", avatar_url)
    if not match:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid avatar image")

    ext = match.group(1).lower().replace("jpeg", "jpg")
    payload = match.group(2)
    if ext not in {"jpg", "png", "gif", "webp", "bmp"}:
        ext = "jpg"

    try:
        binary = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid avatar image") from None
    if len(binary) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="avatar image too large")

    filename = f"{uuid4().hex}.{ext}"
    target = CAT_UPLOAD_DIR / filename
    target.write_bytes(binary)
    return f"/api/v1/uploads/cats/{filename}"


def _serialize_cat_profile(cat_profile: CatProfile) -> dict:
    return CatProfileResponse.model_validate(cat_profile).model_dump()


def _normalize_vaccine_status(value: str | None) -> str | None:
    if value is None:
        return None
    seen: set[str] = set()
    items: list[str] = []
    for raw in re.split(r"[、,，;；\n\r]+", str(value)):
        item = raw.strip()
        if not item or item in seen:
            continue
        seen.add(item)
        items.append(item)
    result = "、".join(items)
    return result or None


@router.post("", response_model=CatProfileResponseEnvelope)
def create_cat_profile(
    payload: CatProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    payload_data = payload.model_dump()
    payload_data["avatar_url"] = _persist_avatar_if_data_url(payload_data.get("avatar_url"))
    payload_data["vaccine_status"] = _normalize_vaccine_status(payload_data.get("vaccine_status"))

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
    if "vaccine_status" in update_data:
        update_data["vaccine_status"] = _normalize_vaccine_status(update_data.get("vaccine_status"))
    for field_name, field_value in update_data.items():
        # Skip None only for non-nullable columns; nullable profile fields may be cleared.
        if field_value is None and field_name in {"name", "is_neutered"}:
            continue
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

    # 提取需要清理的文件路径
    avatar_to_delete = cat_profile.avatar_url

    # 提取情绪记录中的音频路径
    emotion_records = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.pet_id == profile_id)
        .all()
    )
    audio_paths_to_delete: list[str] = []
    import json as _json
    for record in emotion_records:
        if record.raw_result:
            try:
                raw = _json.loads(record.raw_result)
                p = raw.get("_audio_path") if isinstance(raw, dict) else None
                if isinstance(p, str) and p:
                    audio_paths_to_delete.append(p)
            except _json.JSONDecodeError:
                pass

    # 删除关联数据：情绪记录、投喂记录、体重记录
    db.query(EmotionRecord).filter(EmotionRecord.pet_id == profile_id).delete()
    db.query(FeedingRecord).filter(FeedingRecord.pet_id == profile_id).delete()
    db.query(PetWeight).filter(PetWeight.pet_id == profile_id).delete()

    db.delete(cat_profile)
    db.commit()

    # 数据库提交成功后再尝试删除物理文件
    avatar_path = None
    if avatar_to_delete and avatar_to_delete.startswith("/api/v1/uploads/"):
        avatar_path = str(UPLOAD_ROOT / avatar_to_delete[len("/api/v1/uploads/"):])
    if avatar_path:
        safe_delete_file(avatar_path)
    for audio_path in audio_paths_to_delete:
        safe_delete_file(audio_path)

    return {"code": 200, "msg": "删除成功", "data": None}
