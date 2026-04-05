from typing import List

from pydantic import BaseModel, ConfigDict, Field


class SendMessageRequest(BaseModel):
    receiver_id: str = Field(..., alias="receiverId")
    content: str
    message_type: str = Field(..., alias="messageType")

    model_config = ConfigDict(populate_by_name=True)


class QuickMeowRequest(BaseModel):
    receiver_id: str = Field(..., alias="receiverId")
    meow_type: str = Field(..., alias="meowType")

    model_config = ConfigDict(populate_by_name=True)


class UpdateReadStatusRequest(BaseModel):
    message_ids: List[str] = Field(..., alias="messageIds")

    model_config = ConfigDict(populate_by_name=True)


class FriendResponse(BaseModel):
    id: str
    userId: str
    username: str
    nickname: str
    avatar: str
    lastOnlineAt: str
    isOnline: bool


class MessageResponse(BaseModel):
    id: str
    senderId: str
    receiverId: str
    content: str
    messageType: str
    sentAt: str
    status: str


class ConversationResponse(BaseModel):
    id: str
    targetUserId: str
    targetType: str
    lastMessage: str
    lastMessageType: str
    unreadCount: int
    updatedAt: str
    avatar: str
    nickname: str
    isOnline: bool

    model_config = ConfigDict(from_attributes=True)
