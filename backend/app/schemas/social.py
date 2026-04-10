from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SocialBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class CommentCreate(SocialBaseModel):
    content: str


class LikeResponse(SocialBaseModel):
    is_liked: bool
    like_count: int


class CommentResponse(SocialBaseModel):
    id: str
    user_id: str
    username: str
    avatar: str
    dynamic_id: str
    content: str
    created_at: str
    like_count: int = 0
    is_liked: bool = False
    is_owner: bool


class DynamicResponse(SocialBaseModel):
    id: str
    user_id: str
    cat_id: Optional[str] = None
    username: str
    cat_name: Optional[str] = None
    avatar: str
    content: str
    images: List[str] = Field(default_factory=list)
    like_count: int
    comment_count: int
    favorite_count: int = 0
    created_at: str
    is_liked: bool = False
    is_favorited: bool = False
    is_following: bool = False
    is_owner: bool = False
    comments: List[CommentResponse] = Field(default_factory=list)


class DynamicsListResponse(SocialBaseModel):
    list: List[DynamicResponse]
    total: int
    page: int
    page_size: int

class FollowResponse(SocialBaseModel):
    is_following: bool
    follower_count: int

class FavoriteResponse(SocialBaseModel):
    is_favorited: bool
    favorite_count: int

class HotTopic(SocialBaseModel):
    topic: str
    count: int

class HotTopicsResponse(SocialBaseModel):
    list: List[HotTopic]

class DeleteResponse(SocialBaseModel):
    success: bool

class FollowerResponse(SocialBaseModel):
    id: str
    user_id: str
    username: str
    nickname: str
    avatar: str
    last_online_at: str
    is_online: bool
    is_following: bool

class FollowersListResponse(SocialBaseModel):
    list: List[FollowerResponse]
    total: int
    page: int
    page_size: int
