import os
import json
from uuid import uuid4
from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.model_service import analyze_audio
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.emotion_record import EmotionRecord
from app.models.user import User
from app.schemas.emotions import EmotionRecordResponse, WarningStatusPayload

router = APIRouter(prefix="/api/v1/emotions", tags=["Emotions"])

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
AUDIO_STORAGE_DIR = os.path.join(PROJECT_ROOT, "storage", "emotion_audio")
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)


def _ensure_pet_owner(db: Session, pet_id: str, user_id: str) -> None:
    pet = db.query(CatProfile).filter(CatProfile.id == pet_id, CatProfile.user_id == user_id).first()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")


def _parse_iso_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _build_record_response(record: EmotionRecord) -> dict:
    raw = {}
    if record.raw_result:
        try:
            raw = json.loads(record.raw_result)
        except json.JSONDecodeError:
            raw = {}

    translation = raw.get("translation") if isinstance(raw, dict) else None
    emotion_description = None
    if isinstance(translation, dict):
        emotion_description = translation.get("human") or translation.get("science")

    audio_path = raw.get("_audio_path") if isinstance(raw, dict) else None
    audio_url = f"/api/v1/emotions/records/{record.id}/audio" if isinstance(audio_path, str) and audio_path else None

    return {
        "id": record.id,
        "pet_id": record.pet_id,
        "label": record.label,
        "confidence": record.confidence,
        "record_time": record.record_time,
        "emotion_description": emotion_description,
        "audio_url": audio_url,
    }


def _get_record_audio_path(record: EmotionRecord) -> str | None:
    if not record.raw_result:
        return None
    try:
        raw = json.loads(record.raw_result)
    except json.JSONDecodeError:
        return None

    audio_path = raw.get("_audio_path") if isinstance(raw, dict) else None
    if not isinstance(audio_path, str) or not audio_path:
        return None
    if not os.path.isfile(audio_path):
        return None
    return audio_path


@router.post("/recognize")
async def recognize_cat_emotion(
    pet_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    # 验证音频格式
    if not file.filename.lower().endswith((".wav", ".mp3", ".m4a", ".aac", ".flac")):
        raise HTTPException(status_code=400, detail="unsupported audio format")
    
    _, ext = os.path.splitext(file.filename.lower())
    audio_disk_path = os.path.join(AUDIO_STORAGE_DIR, f"{uuid4().hex}{ext or '.wav'}")
    
    try:
        content = await file.read()
        with open(audio_disk_path, "wb") as audio_file:
            audio_file.write(content)

        # 调用你的核心算法！
        result = analyze_audio(audio_disk_path)
        if not isinstance(result, dict):
            result = {"label": "未知", "confidence": 0}
        result["_audio_path"] = audio_disk_path

        record = EmotionRecord(
            pet_id=pet_id,
            user_id=current_user.id,
            label=result.get("label", "未知"),
            confidence=result.get("confidence"),
            raw_result=json.dumps(result, ensure_ascii=False),
            record_time=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()

        response_payload = dict(result)
        response_payload["record_id"] = record.id
        response_payload["pet_id"] = pet_id
        response_payload["audio_url"] = f"/api/v1/emotions/records/{record.id}/audio"

        return {"code": 200, "msg": "success", "data": response_payload}
        
    except Exception as e:
        if os.path.isfile(audio_disk_path):
            os.remove(audio_disk_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/records/list")
def list_emotion_records(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    query = db.query(EmotionRecord).filter(
        EmotionRecord.pet_id == pet_id,
        EmotionRecord.user_id == current_user.id,
    )
    total = query.count()
    records = query.order_by(EmotionRecord.record_time.desc()).offset(skip).limit(limit).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": [EmotionRecordResponse.model_validate(_build_record_response(item)).model_dump() for item in records],
        },
    }


@router.get("/records/{record_id}")
def get_emotion_record_detail(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.id == record_id, EmotionRecord.user_id == current_user.id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emotion record not found")

    return {
        "code": 200,
        "msg": "success",
        "data": EmotionRecordResponse.model_validate(_build_record_response(record)).model_dump(),
    }


@router.get("/records/{record_id}/audio")
def stream_emotion_record_audio(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(EmotionRecord)
        .filter(EmotionRecord.id == record_id, EmotionRecord.user_id == current_user.id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emotion record not found")

    audio_path = _get_record_audio_path(record)
    if not audio_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audio file not found")

    return FileResponse(audio_path)


@router.get("/statistics")
def get_emotion_statistics(
    pet_id: str,
    days: int = Query(7, ge=1, le=365),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    end_time = _parse_iso_datetime(end_date) if end_date else datetime.now(timezone.utc)
    start_time = _parse_iso_datetime(start_date) if start_date else end_time - timedelta(days=days)
    records = (
        db.query(EmotionRecord)
        .filter(
            EmotionRecord.pet_id == pet_id,
            EmotionRecord.user_id == current_user.id,
            EmotionRecord.record_time >= start_time,
            EmotionRecord.record_time <= end_time,
        )
        .all()
    )

    counter = Counter(record.label for record in records)
    total = sum(counter.values())
    distribution = [
        {
            "label": label,
            "count": count,
            "percentage": round((count / total) * 100, 2) if total else 0,
        }
        for label, count in counter.most_common()
    ]

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "pet_id": pet_id,
            "days": max((end_time - start_time).days, 1),
            "total": total,
            "distribution": distribution,
        },
    }


@router.get("/weekly-report")
def get_weekly_report(
    pet_id: str,
    week_start: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    start_time = _parse_iso_datetime(week_start) if week_start else datetime.now(timezone.utc) - timedelta(days=7)
    end_time = start_time + timedelta(days=7)
    records = (
        db.query(EmotionRecord)
        .filter(
            EmotionRecord.pet_id == pet_id,
            EmotionRecord.user_id == current_user.id,
            EmotionRecord.record_time >= start_time,
            EmotionRecord.record_time <= end_time,
        )
        .all()
    )

    counter = Counter(record.label for record in records)
    total = sum(counter.values())
    happy_labels = {"开心", "开心/兴奋"}
    stress_labels = {"焦虑", "生气/暴躁", "疼痛警告", "警告/威胁", "打斗/攻击"}

    happy_count = sum(counter.get(label, 0) for label in happy_labels)
    stress_count = sum(counter.get(label, 0) for label in stress_labels)
    happy_ratio = (happy_count / total) * 100 if total else 0
    stress_ratio = (stress_count / total) * 100 if total else 0

    if total == 0:
        summary = "本周暂无情绪记录，建议每天记录几次叫声，方便更准确分析。"
    elif happy_ratio >= 70:
        summary = f"本周开心占比{happy_ratio:.1f}%，情绪状态非常稳定，请继续保持当前陪伴节奏。"
    elif stress_ratio >= 40:
        summary = f"本周紧张或负面情绪占比{stress_ratio:.1f}%，建议增加安抚互动并排查环境刺激。"
    else:
        summary = "本周整体情绪中等偏稳，可保持规律作息并继续观察变化趋势。"

    distribution = [
        {
            "label": label,
            "count": count,
            "percentage": round((count / total) * 100, 2) if total else 0,
        }
        for label, count in counter.most_common()
    ]

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "pet_id": pet_id,
            "period_days": 7,
            "total": total,
            "distribution": distribution,
            "summary": summary,
            "week_start": start_time.date().isoformat(),
            "week_end": end_time.date().isoformat(),
        },
    }


@router.get("/warnings/list")
def list_warnings(
    pet_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    _ = pet_id
    _ = status
    _ = skip
    _ = limit
    _ = current_user
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": 0,
            "list": [],
        },
    }


@router.put("/warnings/{warning_id}/status")
def mark_warning_status(
    warning_id: str,
    payload: WarningStatusPayload,
    current_user: User = Depends(get_current_user),
):
    _ = warning_id
    _ = payload
    _ = current_user
    return {
        "code": 200,
        "msg": "success",
        "data": {"success": True},
    }