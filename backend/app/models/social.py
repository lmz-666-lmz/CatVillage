from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database.session import Base


class SocialDynamic(Base):
    __tablename__ = "social_dynamics"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    cat_id = Column(String(64), ForeignKey("cat_profiles.id"), nullable=True, index=True)
    content = Column(Text, nullable=False)
    images = Column(Text, nullable=True)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    cat = relationship("CatProfile", foreign_keys=[cat_id])


class SocialComment(Base):
    __tablename__ = "social_comments"

    id = Column(String(64), primary_key=True, index=True)
    dynamic_id = Column(String(64), ForeignKey("social_dynamics.id"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    dynamic = relationship("SocialDynamic", foreign_keys=[dynamic_id])


class SocialLike(Base):
    __tablename__ = "social_likes"

    id = Column(String(64), primary_key=True, index=True)
    dynamic_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SocialFavorite(Base):
    __tablename__ = "social_favorites"

    id = Column(String(64), primary_key=True, index=True)
    dynamic_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SocialFollow(Base):
    __tablename__ = "social_follows"

    id = Column(String(64), primary_key=True, index=True)
    follower_id = Column(String(64), nullable=False, index=True)
    followed_user_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SocialCommentLike(Base):
    __tablename__ = "social_comment_likes"

    id = Column(String(64), primary_key=True, index=True)
    comment_id = Column(String(64), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
