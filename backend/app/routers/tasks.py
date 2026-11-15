from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.schemas import TaskCreate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db)):

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        required_skills=data.required_skills
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create task"
        )


@router.get("/", response_model=list[TaskResponse])
def get_tasks(db: Session = Depends(get_db)):

    return (
        db.query(Task)
        .order_by(Task.id.desc())
        .all()
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(Task).filter(
        Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task