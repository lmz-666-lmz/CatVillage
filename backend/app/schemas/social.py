from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    content: str


class LikeResponse(BaseModel):
    isLiked: bool
    likeCount: int


class CommentResponse(BaseModel):
    id: str
    userId: str
    username: str
    avatar: str
    dynamicId: str
    content: str
    createdAt: str
    isOwner: bool


class DynamicResponse(BaseModel):
    id: str
    userId: str
    catId: Optional[str] = None
    username: str
    catName: Optional[str] = None
    avatar: str
    content: str
    images: List[str] = Field(default_factory=list)
    likeCount: int
    commentCount: int
    createdAt: str
    isLiked: bool = False
    isOwner: bool = False

    model_config = ConfigDict(from_attributes=True)


class DynamicsListResponse(BaseModel):
    list: List[DynamicResponse]
    total: int
    page: int
    pageSize: int
