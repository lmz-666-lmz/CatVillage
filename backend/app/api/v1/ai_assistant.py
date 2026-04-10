import os
import uuid  # <-- 我加了这个
from datetime import datetime, timezone  # <-- 我加了这个

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from fastapi import Query, status

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.ai_chat_history import AIChatHistory
from app.models.cat_profile import CatProfile
from app.models.health import PetWeight
from app.models.user import User
from app.schemas.ai_assistant import ChatHistoryResponse, ChatRequest

router = APIRouter(prefix="/api/v1/ai-assistant", tags=["AI Assistant"])

AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")

if not AI_API_KEY or AI_API_KEY.strip() in {"", "你的真实API密钥"}:
    print("warning: AI_API_KEY is missing or still a placeholder")

aclient = AsyncOpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL,
)


def _ensure_pet_owner(db: Session, pet_id: str, user_id: str) -> CatProfile:
    cat_profile = db.query(CatProfile).filter(CatProfile.id == pet_id, CatProfile.user_id == user_id).first()
    if cat_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")
    return cat_profile


@router.get("/history")
def get_chat_history(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    query = db.query(AIChatHistory).filter(
        AIChatHistory.pet_id == pet_id,
        AIChatHistory.user_id == current_user.id,
    )
    total = query.count()
    records = query.order_by(AIChatHistory.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": [
                {
                    "id": record.id,
                    "pet_id": record.pet_id,
                    "question": record.question,
                    "answer": record.answer,
                    "created_at": record.created_at.isoformat() if record.created_at else "",
                }
                for record in records
            ],
        },
    }


@router.delete("/sessions/{session_id}")
def clear_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = (
        db.query(AIChatHistory)
        .filter(AIChatHistory.pet_id == session_id, AIChatHistory.user_id == current_user.id)
        .delete()
    )
    db.commit()
    return {
        "code": 200,
        "msg": "success",
        "data": {"success": True, "deleted": deleted},
    }


@router.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not AI_API_KEY or AI_API_KEY.strip() in {"", "你的真实API密钥"}:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI API key is not configured")

    cat_profile = _ensure_pet_owner(db, request.pet_id, current_user.id)

    latest_weight = (
        db.query(PetWeight)
        .filter(PetWeight.pet_id == request.pet_id)
        .order_by(PetWeight.record_date.desc())
        .first()
    )

    weight_text = (
        f"最近一次体重为{latest_weight.weight}kg（记录时间：{latest_weight.record_date}）。"
        if latest_weight
        else "暂时没有体重记录。"
    )

    system_prompt = (
        "你是一个猫咪养育专家，请基于宠物档案提供科学、可执行、温和的建议。"
        f"当前咨询猫咪信息：名字{cat_profile.name}，品种{cat_profile.breed or '未知'}，"
        f"年龄{cat_profile.age if cat_profile.age is not None else '未知'}岁，"
        f"性别{cat_profile.gender if cat_profile.gender is not None else '未知'}，"
        f"绝育状态{'已绝育' if cat_profile.is_neutered else '未绝育'}，"
        f"病史{cat_profile.medical_history or '无'}，{weight_text}"
        "请避免给出超出普通养护场景的高风险医疗结论，必要时提醒线下就医。"
    )

    try:
        response = await aclient.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_message},
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"AI assistant request failed: {exc}") from exc

    reply_text = response.choices[0].message.content if response.choices else ""

    # ===================== 我修复的核心代码 =====================
    try:
        history = AIChatHistory(
            id=str(uuid.uuid4()),
            pet_id=request.pet_id,
            user_id=current_user.id,
            question=request.user_message,
            answer=reply_text,
            created_at=datetime.now(timezone.utc),
        )
        db.add(history)
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"⚠️ 聊天记录保存失败，已跳过保存：{exc}")
    # ==========================================================

    # 无论如何都返回结果给前端
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "pet_id": request.pet_id,
            "reply": reply_text,
            "used_context": {
                "breed": cat_profile.breed,
                "age": cat_profile.age,
                "latest_weight": latest_weight.weight if latest_weight else None,
            },
        },
    }


@router.post("/emergency-help/{warning_id}")
def emergency_help(
    warning_id: str,
    current_user: User = Depends(get_current_user),
):
    _ = warning_id
    _ = current_user
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "success": True,
            "advice": "请先安抚猫咪，观察呼吸与食欲变化，必要时尽快线下就医。",
            "next_steps": ["检查环境刺激", "记录症状变化", "联系兽医"],
        },
    }