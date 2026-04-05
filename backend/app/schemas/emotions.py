from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EmotionRecordResponse(BaseModel):
    id: int
    pet_id: str
    label: str
    confidence: float | None = None
    record_time: datetime

    model_config = ConfigDict(from_attributes=True)


class WarningStatusPayload(BaseModel):
    status: str