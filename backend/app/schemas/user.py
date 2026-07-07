from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserResponse(BaseModel):
    id: str
    username: str
    nickname: str | None = None
    avatar_url: str | None = None
    avatarUrl: str | None = None
    is_active: bool
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdate(BaseModel):
    nickname: str | None = Field(None, min_length=1, max_length=50)
    avatar_url: str | None = Field(None, alias="avatarUrl")

    model_config = ConfigDict(populate_by_name=True)
