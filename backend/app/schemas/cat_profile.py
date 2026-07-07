from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CatProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=360)
    gender: Optional[int] = Field(None, ge=0, le=1)
    weight: Optional[float] = Field(None, gt=0, le=100)
    avatar_url: Optional[str] = None
    is_neutered: bool = False
    medical_history: Optional[str] = Field(None, max_length=1000)
    vaccine_status: Optional[str] = Field(None, max_length=100)


class CatProfileCreate(CatProfileBase):
    pass


class CatProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=360)
    gender: Optional[int] = Field(None, ge=0, le=1)
    weight: Optional[float] = Field(None, gt=0, le=100)
    avatar_url: Optional[str] = None
    is_neutered: Optional[bool] = None
    medical_history: Optional[str] = Field(None, max_length=1000)
    vaccine_status: Optional[str] = Field(None, max_length=100)


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
