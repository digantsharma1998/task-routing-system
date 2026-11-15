from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# -------------------------
# Task Schemas
# -------------------------

class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = ""
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    required_skills: list[str] = Field(default_factory=list)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"]
    status: Literal["pending", "assigned", "in_progress", "completed"]
    required_skills: list[str]

    class Config:
        from_attributes = True


# -------------------------
# Contributor Schemas
# -------------------------

class ContributorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    skills: list[str] = Field(default_factory=list)
    max_capacity: int = Field(default=5, ge=1)


class ContributorUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    skills: list[str] = Field(default_factory=list)
    max_capacity: int = Field(default=5, ge=1)
    available: bool = True


class ContributorResponse(BaseModel):
    id: int
    name: str
    email: str
    skills: list[str]
    max_capacity: int
    available: bool

    class Config:
        from_attributes = True


# -------------------------
# Assignment Schemas
# -------------------------

class AssignmentResponse(BaseModel):
    id: int
    task_id: int
    contributor_id: int
    status: Literal["assigned", "accepted", "rejected", "no_response"]
    assigned_at: datetime
    responded_at: Optional[datetime] = None
    response_timeout_seconds: int

    class Config:
        from_attributes = True