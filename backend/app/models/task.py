from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class Task(Base):
    required_skills = Column(JSON, default=list)
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    priority = Column(String(20), default="medium")
    status = Column(String(30), default="pending")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )