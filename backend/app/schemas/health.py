from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WeightCreate(BaseModel):
    pet_id: str
    weight: float = Field(..., gt=0)
    record_date: datetime | None = None


class PetWeightResponse(BaseModel):
    id: int
    pet_id: str
    weight: float
    record_date: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedingCreate(BaseModel):
    pet_id: str
    food_type: str
    food_weight: float = Field(..., gt=0)
    feeding_time: datetime | None = None


class FeedingRecordResponse(BaseModel):
    id: int
    pet_id: str
    food_type: str
    food_weight: float
    feeding_time: datetime

    model_config = ConfigDict(from_attributes=True)