import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.assignment import Assignment
from app.models.activity import ActivityLog
from app.schemas import AssignmentResponse
from app.services.assignment_service import find_best_contributor


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


def create_assignment(db, task, contributor, action="assigned"):
    """
    Create an assignment after safely claiming a pending task.
    """

    claim = db.query(Task).filter(
        Task.id == task.id,
        Task.status == "pending"
    ).update(
        {Task.status: "assigned"},
        synchronize_session=False
    )

    if claim != 1:
        return None

    task.status = "assigned"

    assignment = Assignment(
        task_id=task.id,
        contributor_id=contributor.id,
        status="assigned",
        response_timeout_seconds=random.randint(5, 20)
    )

    db.add(assignment)
    db.flush()

    db.add(ActivityLog(
        entity_type="task",
        entity_id=task.id,
        action=action,
        details=(
            f"Assigned to contributor {contributor.id}"
        )
    ))

    return assignment


@router.get("/", response_model=list[AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).order_by(
        Assignment.id.desc()
    ).all()


@router.post(
    "/auto/{task_id}",
    response_model=AssignmentResponse
)
def auto_assign_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    try:
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        if task.status != "pending":
            raise HTTPException(
                status_code=409,
                detail="Task is not pending"
            )

        existing = db.query(Assignment).filter(
            Assignment.task_id == task_id,
            Assignment.status.in_(["assigned", "accepted"])
        ).first()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Task already assigned"
            )

        contributor = find_best_contributor(
            db,
            task.required_skills or [],
            task_id=task.id
        )

        if not contributor:
            raise HTTPException(
                status_code=409,
                detail="No eligible contributor available"
            )

        assignment = create_assignment(
            db,
            task,
            contributor
        )

        if assignment is None:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Task was assigned by another request"
            )

        db.commit()
        db.refresh(assignment)

        return assignment

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.post(
    "/auto-next",
    response_model=AssignmentResponse
)
def auto_assign_next_task(
    db: Session = Depends(get_db)
):

    priority_order = case(
        (Task.priority == "critical", 1),
        (Task.priority == "high", 2),
        (Task.priority == "medium", 3),
        (Task.priority == "low", 4),
        else_=5
    )

    try:
        pending_tasks = db.query(Task).filter(
            Task.status == "pending"
        ).order_by(
            priority_order,
            Task.id.asc()
        ).all()

        for task in pending_tasks:

            existing = db.query(Assignment).filter(
                Assignment.task_id == task.id,
                Assignment.status.in_(["assigned", "accepted"])
            ).first()

            if existing:
                continue

            contributor = find_best_contributor(
                db,
                task.required_skills or [],
                task_id=task.id
            )

            if not contributor:
                continue

            assignment = create_assignment(
                db,
                task,
                contributor
            )

            if assignment is None:
                db.rollback()
                continue

            db.commit()
            db.refresh(assignment)

            return assignment

        raise HTTPException(
            status_code=409,
            detail="No pending task has an eligible contributor"
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.post(
    "/{assignment_id}/accept",
    response_model=AssignmentResponse
)
def accept_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):

    try:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=404,
                detail="Assignment not found"
            )

        now = datetime.now(timezone.utc)

        updated = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.status == "assigned"
        ).update(
            {
                Assignment.status: "accepted",
                Assignment.responded_at: now
            },
            synchronize_session=False
        )

        if updated != 1:
            raise HTTPException(
                status_code=409,
                detail="Assignment cannot be accepted"
            )

        db.query(Task).filter(
            Task.id == assignment.task_id,
            Task.status == "assigned"
        ).update(
            {Task.status: "in_progress"},
            synchronize_session=False
        )

        db.add(ActivityLog(
            entity_type="assignment",
            entity_id=assignment.id,
            action="accepted",
            details="Contributor accepted the assignment"
        ))

        db.commit()
        db.refresh(assignment)

        return assignment

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise


@router.post(
    "/{assignment_id}/reject",
    response_model=AssignmentResponse
)
def reject_assignment(
    assignment_id: int,
    db: Session = Depends(get_db)
):

    try:
        assignment = db.query(Assignment).filter(
            Assignment.id == assignment_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=404,
                detail="Assignment not found"
            )

        now = datetime.now(timezone.utc)

        updated = db.query(Assignment).filter(
            Assignment.id == assignment_id,
            Assignment.status == "assigned"
        ).update(
            {
                Assignment.status: "rejected",
                Assignment.responded_at: now
            },
            synchronize_session=False
        )

        if updated != 1:
            raise HTTPException(
                status_code=409,
                detail="Assignment cannot be rejected"
            )

        db.query(Task).filter(
            Task.id == assignment.task_id,
            Task.status == "assigned"
        ).update(
            {Task.status: "pending"},
            synchronize_session=False
        )

        db.add(ActivityLog(
            entity_type="assignment",
            entity_id=assignment.id,
            action="rejected",
            details="Contributor rejected the assignment"
        ))

        db.commit()
        db.refresh(assignment)

        return assignment

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise