from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import ACCESS_TOKEN_EXPIRE_DAYS, create_access_token, get_password_hash, verify_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserProfileUpdate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _serialize_user(user: User) -> dict:
    payload = UserResponse.model_validate(user).model_dump()
    payload["nickname"] = (user.nickname or "").strip() or user.username
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


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    nickname = payload.nickname.strip()
    if not nickname:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="昵称不能为空")

    current_user.nickname = nickname
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {"code": 200, "msg": "更新成功", "data": _serialize_user(current_user)}