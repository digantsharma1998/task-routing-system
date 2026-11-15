from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    action = Column(String(100))
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())