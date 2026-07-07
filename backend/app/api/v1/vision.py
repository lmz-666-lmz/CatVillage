import hashlib

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import UPLOAD_MAX_BYTES
from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.user import User


router = APIRouter(prefix="/api/v1/vision", tags=["vision"])


class FusionRequest(BaseModel):
    pet_id: str | None = None


def _ensure_pet_owner(db: Session, pet_id: str | None, user_id: str) -> None:
    if not pet_id:
        return
    pet = db.query(CatProfile).filter(CatProfile.id == pet_id, CatProfile.user_id == user_id).first()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")


def _pick_case(seed: bytes, cases: list[dict]) -> dict:
    index = seed[0] % len(cases)
    return cases[index]


@router.post("/recognize")
async def recognize_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    _ = current_user
    extension = (file.filename or "").lower().rsplit(".", 1)[-1]
    if extension not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported image format")

    content = await file.read()
    if len(content) > UPLOAD_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="uploaded file too large")

    seed = hashlib.sha256(content).digest()
    result = _pick_case(
        seed,
        [
            {
                "facialExpression": {"eyes": "柔和，瞳孔适中", "ears": "自然竖立", "mouth": "正常闭合"},
                "bodyPosture": {"posture": "舒适卧姿", "tail": "自然摆放", "relaxLevel": 82},
                "behaviorAnalysis": "猫咪整体姿态放松，环境适应度较好，可继续保持当前陪伴节奏。",
                "emotionScore": 84,
                "emotionLabel": "舒适",
            },
            {
                "facialExpression": {"eyes": "明亮有神", "ears": "转向声源", "mouth": "轻微张开"},
                "bodyPosture": {"posture": "站立观察", "tail": "轻微摆动", "relaxLevel": 64},
                "behaviorAnalysis": "猫咪处于好奇或轻度兴奋状态，适合进行短时间互动游戏。",
                "emotionScore": 72,
                "emotionLabel": "兴奋",
            },
            {
                "facialExpression": {"eyes": "睁大警觉", "ears": "竖起前倾", "mouth": "闭合紧张"},
                "bodyPosture": {"posture": "低伏或蜷缩", "tail": "贴近身体", "relaxLevel": 38},
                "behaviorAnalysis": "猫咪可能对环境变化保持警惕，建议降低噪音并提供安全躲藏空间。",
                "emotionScore": 46,
                "emotionLabel": "警惕",
            },
        ],
    )
    result["is_mock"] = True
    result["mock_notice"] = "当前为模拟数据，视觉识别功能基于规则匹配，非真实AI模型推理"
    return {"code": 200, "msg": "success", "data": result}


@router.post("/audio-visual-fusion")
def audio_visual_fusion(
    payload: FusionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, payload.pet_id, current_user.id)
    seed_value = (payload.pet_id or current_user.id).encode("utf-8")
    seed = hashlib.sha256(seed_value).digest()
    result = _pick_case(
        seed,
        [
            {
                "primaryEmotion": {"label": "平静舒适", "description": "视觉姿态与近期声音记录综合稳定", "confidence": 91},
                "otherEmotions": [
                    {"label": "警惕紧张", "description": "暂未出现持续高警惕信号", "confidence": 18, "color": "#ffa500"},
                    {"label": "不适焦虑", "description": "暂无明显异常组合特征", "confidence": 9, "color": "#ff6b6b"},
                    {"label": "愉快兴奋", "description": "存在少量互动兴奋信号", "confidence": 63, "color": "#4fb233"},
                ],
            },
            {
                "primaryEmotion": {"label": "警惕紧张", "description": "姿态警觉与高唤醒声音特征组合", "confidence": 76},
                "otherEmotions": [
                    {"label": "平静舒适", "description": "放松信号偏弱", "confidence": 22, "color": "#667eea"},
                    {"label": "不适焦虑", "description": "建议继续观察食欲和排泄", "confidence": 58, "color": "#ff6b6b"},
                    {"label": "愉快兴奋", "description": "互动兴奋特征有限", "confidence": 31, "color": "#4fb233"},
                ],
            },
        ],
    )
    result["fusionSteps"] = [
        {"name": "视觉编码", "detail": "提取姿态、眼神和耳位等轻量视觉特征"},
        {"name": "音频编码", "detail": "结合已有音频情绪标签和频谱特征"},
        {"name": "规则融合", "detail": "在低配服务器上用启发式融合替代重模型推理"},
        {"name": "情绪分类", "detail": "输出综合情绪标签和置信度"},
    ]
    result["is_mock"] = True
    result["mock_notice"] = "当前为模拟数据，视听融合功能基于规则匹配，非真实AI模型推理"
    return {"code": 200, "msg": "success", "data": result}
