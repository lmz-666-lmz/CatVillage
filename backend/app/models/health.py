from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func

from app.database.session import Base


class PetWeight(Base):
    __tablename__ = "pet_weights"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pet_id = Column(String(64), ForeignKey("cat_profiles.id"), nullable=False, index=True)
    weight = Column(Float, nullable=False)
    record_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


class FeedingRecord(Base):
    __tablename__ = "feeding_records"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pet_id = Column(String(64), ForeignKey("cat_profiles.id"), nullable=False, index=True)
    food_type = Column(String(100), nullable=False)
    food_weight = Column(Float, nullable=False)
    feeding_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)