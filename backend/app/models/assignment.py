from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"))

    contributor_id = Column(
        Integer,
        ForeignKey("contributors.id")
    )

    status = Column(String(30), default="assigned")

    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    responded_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    response_timeout_seconds = Column(
        Integer,
        nullable=False,
        default=20,
        server_default="20"
    )