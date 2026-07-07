from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.cat_profile import CatProfile
from app.models.health import FeedingRecord, PetWeight
from app.models.user import User
from app.schemas.health import FeedingCreate, FeedingRecordResponse, PetWeightResponse, WeightCreate

router = APIRouter(prefix="/api/v1/health", tags=["health"])


def _ensure_pet_owner(db: Session, pet_id: str, user_id: str) -> None:
    pet = db.query(CatProfile).filter(CatProfile.id == pet_id, CatProfile.user_id == user_id).first()
    if pet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat profile not found")


@router.post("/weight")
def create_weight_record(
    request: WeightCreate,  # <--- 修改了这里，避免 422 错误
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, request.pet_id, current_user.id)

    weight_record = PetWeight(
        pet_id=request.pet_id,
        weight=request.weight,
        record_date=request.record_date or datetime.now(timezone.utc),
    )
    db.add(weight_record)
    db.commit()
    db.refresh(weight_record)

    return {
        "code": 200,
        "msg": "success",
        "data": PetWeightResponse.model_validate(weight_record).model_dump(),
    }


@router.get("/weight/list")
def list_weight_records(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    query = db.query(PetWeight).filter(PetWeight.pet_id == pet_id)
    total = query.count()
    records = query.order_by(PetWeight.record_date.desc()).offset(skip).limit(limit).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": [PetWeightResponse.model_validate(record).model_dump() for record in records],
        },
    }


@router.post("/feeding")
def create_feeding_record(
    request: FeedingCreate,  # <--- 修改了这里
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, request.pet_id, current_user.id)

    feeding_record = FeedingRecord(
        pet_id=request.pet_id,
        food_type=request.food_type,
        food_weight=request.food_weight,
        feeding_time=request.feeding_time or datetime.now(timezone.utc),
    )
    db.add(feeding_record)
    db.commit()
    db.refresh(feeding_record)

    return {
        "code": 200,
        "msg": "success",
        "data": FeedingRecordResponse.model_validate(feeding_record).model_dump(),
    }


@router.get("/feeding/list")
def list_feeding_records(
    pet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_pet_owner(db, pet_id, current_user.id)

    query = db.query(FeedingRecord).filter(FeedingRecord.pet_id == pet_id)
    total = query.count()
    records = query.order_by(FeedingRecord.feeding_time.desc()).offset(skip).limit(limit).all()

    return {
        "code": 200,
        "msg": "success",
        "data": {
            "total": total,
            "list": [FeedingRecordResponse.model_validate(record).model_dump() for record in records],
        },
    }