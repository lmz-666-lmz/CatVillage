from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CatProfileBase(BaseModel):
    name: str
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[int] = None
    weight: Optional[float] = None
    avatar_url: Optional[str] = None
    is_neutered: bool = False
    medical_history: Optional[str] = None
    vaccine_status: Optional[str] = None


class CatProfileCreate(CatProfileBase):
    pass


class CatProfileUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[int] = None
    weight: Optional[float] = None
    avatar_url: Optional[str] = None
    is_neutered: Optional[bool] = None
    medical_history: Optional[str] = None
    vaccine_status: Optional[str] = None


class CatProfileResponse(CatProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CatProfileListResponse(BaseModel):
    total: int
    list: List[CatProfileResponse]


class CatProfileResponseEnvelope(BaseModel):
    code: int = 200
    msg: str = "success"
    data: CatProfileResponse


class CatProfileListResponseEnvelope(BaseModel):
    code: int = 200
    msg: str = "success"
    data: CatProfileListResponse


class CatProfileActionResponseEnvelope(BaseModel):
    code: int = 200
    msg: str = "success"
    data: None = None
