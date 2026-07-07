from datetime import timedelta
from pathlib import Path
import base64
import binascii
import re
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_MAX_BYTES
from app.core.dependencies import get_current_user
from app.core.security import ACCESS_TOKEN_EXPIRE_DAYS, create_access_token, get_password_hash, verify_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"
USER_UPLOAD_DIR = UPLOAD_ROOT / "users"
USER_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
    if ext not in {"jpg", "png", "gif", "webp", "bmp"}:
        ext = "jpg"

    try:
        binary = base64.b64decode(match.group(2), validate=True)
    except (ValueError, binascii.Error):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid avatar image") from None

    if len(binary) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="avatar image too large")

    filename = f"{uuid4().hex}.{ext}"
    target = USER_UPLOAD_DIR / filename
    target.write_bytes(binary)
    return f"/api/v1/uploads/users/{filename}"


def _serialize_user(user: User) -> dict:
    payload = UserResponse.model_validate(user).model_dump()
    payload["nickname"] = (user.nickname or "").strip() or user.username
    payload["avatar_url"] = (getattr(user, "avatar_url", "") or "").strip() or None
    payload["avatarUrl"] = payload["avatar_url"]
    return payload


@router.post("/register")
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")

    user = User(
        id=str(uuid4()),
        username=payload.username,
        nickname=payload.username,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"code": 200, "msg": "注册成功", "data": _serialize_user(user)}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码不能为空",
        )

    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户已被禁用")

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS),
    )
    
    # 扁平化返回，专门为了适配 Swagger UI 的 Authorize 绿锁机制
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    _ = current_user
    return {"code": 200, "msg": "退出成功", "data": {"success": True}}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    avatar_url = (getattr(current_user, "avatar_url", "") or "").strip() or None
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": (current_user.nickname or "").strip() or current_user.username,
            "avatar_url": avatar_url,
            "avatarUrl": avatar_url,
            "is_admin": bool(current_user.is_admin),
            "is_active": bool(current_user.is_active),
        },
    }


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.nickname is not None:
        nickname = payload.nickname.strip()
        if not nickname:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="昵称不能为空")
        current_user.nickname = nickname
    if payload.avatar_url is not None:
        current_user.avatar_url = _persist_avatar_if_data_url(payload.avatar_url)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"code": 200, "msg": "更新成功", "data": _serialize_user(current_user)}
