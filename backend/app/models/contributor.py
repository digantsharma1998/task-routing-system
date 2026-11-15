from sqlalchemy import Column, Integer, String, Boolean, JSON
from app.database import Base


class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    skills = Column(JSON, default=list)
    max_capacity = Column(Integer, default=5)
    available = Column(Boolean, default=True)