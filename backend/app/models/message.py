from sqlalchemy import Column, DateTime, String, Text, func

from app.database.session import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, index=True)
    sender_id = Column(String(64), nullable=False, index=True)
    receiver_id = Column(String(64), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False, default="sent")
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class FriendLink(Base):
    __tablename__ = "friend_links"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    friend_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
