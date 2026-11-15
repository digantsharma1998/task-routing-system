from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.models.contributor import Contributor
from app.models.assignment import Assignment
from app.models.activity import ActivityLog


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_db)
):
    # -------------------------
    # TASK STATISTICS
    # -------------------------

    total_tasks = db.query(Task).count()

    task_statuses = {
        "pending": db.query(Task).filter(
            Task.status == "pending"
        ).count(),

        "assigned": db.query(Task).filter(
            Task.status == "assigned"
        ).count(),

        "in_progress": db.query(Task).filter(
            Task.status == "in_progress"
        ).count(),

        "completed": db.query(Task).filter(
            Task.status == "completed"
        ).count()
    }

    # -------------------------
    # ASSIGNMENT STATISTICS
    # -------------------------

    total_assignments = db.query(Assignment).count()

    assignment_statuses = {
        "assigned": db.query(Assignment).filter(
            Assignment.status == "assigned"
        ).count(),

        "accepted": db.query(Assignment).filter(
            Assignment.status == "accepted"
        ).count(),

        "rejected": db.query(Assignment).filter(
            Assignment.status == "rejected"
        ).count(),

        "no_response": db.query(Assignment).filter(
            Assignment.status == "no_response"
        ).count()
    }

    resolved_assignments = (
        assignment_statuses["accepted"]
        + assignment_statuses["rejected"]
        + assignment_statuses["no_response"]
    )

    acceptance_rate = (
        round(
            assignment_statuses["accepted"]
            / resolved_assignments * 100,
            2
        )
        if resolved_assignments else 0
    )

    timeout_rate = (
        round(
            assignment_statuses["no_response"]
            / total_assignments * 100,
            2
        )
        if total_assignments else 0
    )

    # -------------------------
    # CONTRIBUTOR STATISTICS
    # -------------------------

    contributors = db.query(Contributor).all()

    contributor_workload = []

    for contributor in contributors:

        active_assignments = db.query(Assignment).filter(
            Assignment.contributor_id == contributor.id,
            Assignment.status.in_(["assigned", "accepted"])
        ).count()

        capacity = contributor.max_capacity or 0

        utilization = (
            round(active_assignments / capacity * 100, 2)
            if capacity > 0 else 0
        )

        contributor_workload.append({
            "contributor_id": contributor.id,
            "name": contributor.name,
            "skills": contributor.skills or [],
            "available": contributor.available,
            "max_capacity": capacity,
            "active_assignments": active_assignments,
            "remaining_capacity": max(
                capacity - active_assignments, 0
            ),
            "utilization_percentage": utilization
        })

    total_contributors = len(contributors)

    available_contributors = sum(
        1 for contributor in contributors
        if contributor.available
    )

    # -------------------------
    # RECENT ACTIVITY
    # -------------------------

    recent_activities = db.query(ActivityLog).order_by(
        ActivityLog.id.desc()
    ).limit(10).all()

    activity_list = [
        {
            "id": activity.id,
            "entity_type": activity.entity_type,
            "entity_id": activity.entity_id,
            "action": activity.action,
            "details": activity.details,
            "created_at": activity.created_at
        }
        for activity in recent_activities
    ]

    # -------------------------
    # DASHBOARD RESPONSE
    # -------------------------

    return {
        "tasks": {
            "total": total_tasks,
            "by_status": task_statuses
        },
        "assignments": {
            "total": total_assignments,
            "by_status": assignment_statuses,
            "acceptance_rate": acceptance_rate,
            "timeout_rate": timeout_rate
        },
        "contributors": {
            "total": total_contributors,
            "available": available_contributors,
            "unavailable": (
                total_contributors - available_contributors
            ),
            "workload": contributor_workload
        },
        "recent_activities": activity_list
    }