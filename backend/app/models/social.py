from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.database.session import Base


class SocialDynamic(Base):
    __tablename__ = "social_dynamics"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    cat_id = Column(String(64), nullable=True, index=True)
    content = Column(Text, nullable=False)
    images = Column(Text, nullable=True)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class SocialComment(Base):
    __tablename__ = "social_comments"

    id = Column(String(64), primary_key=True, index=True)
    dynamic_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SocialLike(Base):
    __tablename__ = "social_likes"

    id = Column(String(64), primary_key=True, index=True)
    dynamic_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
