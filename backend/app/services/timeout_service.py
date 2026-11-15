import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import case

from app.models.assignment import Assignment
from app.models.task import Task
from app.models.activity import ActivityLog
from app.services.assignment_service import find_best_contributor


def process_assignment_timeouts(db):
    """
    Process expired assignments and retry pending tasks.

    Rules:
    - Expired assignments become no_response.
    - Rejected and timed-out contributors are not selected again.
    - Pending tasks are retried when an eligible contributor is available.
    - Tasks with active assignments are never assigned again.
    - Conditional task updates help prevent duplicate assignments.
    """

    now = datetime.now(timezone.utc)

    reassigned_task_ids = []

    # --------------------------------------------------
    # 1. Find and process expired assignments
    # --------------------------------------------------

    expired_assignments = db.query(Assignment).filter(
        Assignment.status == "assigned"
    ).all()

    for assignment in expired_assignments:

        assigned_at = assignment.assigned_at

        if assigned_at is None:
            continue

        # SQLite may return naive datetimes.
        if assigned_at.tzinfo is None:
            assigned_at = assigned_at.replace(
                tzinfo=timezone.utc
            )

        timeout_seconds = (
            assignment.response_timeout_seconds or 20
        )

        cutoff = now - timedelta(
            seconds=timeout_seconds
        )

        if assigned_at > cutoff:
            continue

        assignment.status = "no_response"
        assignment.responded_at = now

        task = db.query(Task).filter(
            Task.id == assignment.task_id
        ).first()

        if task and task.status == "assigned":
            task.status = "pending"

        db.add(ActivityLog(
            entity_type="assignment",
            entity_id=assignment.id,
            action="no_response",
            details=(
                f"Contributor {assignment.contributor_id} "
                f"did not respond within "
                f"{timeout_seconds} seconds"
            )
        ))

    # Save timeout changes before finding pending tasks.
    db.flush()

    # --------------------------------------------------
    # 2. Process pending tasks in priority order
    # --------------------------------------------------

    priority_order = case(
        (Task.priority == "critical", 1),
        (Task.priority == "high", 2),
        (Task.priority == "medium", 3),
        (Task.priority == "low", 4),
        else_=5
    )

    pending_tasks = db.query(Task).filter(
        Task.status == "pending"
    ).order_by(
        priority_order,
        Task.id.asc()
    ).all()

    for task in pending_tasks:

        # Skip tasks with an active assignment.
        existing = db.query(Assignment).filter(
            Assignment.task_id == task.id,
            Assignment.status.in_([
                "assigned",
                "accepted"
            ])
        ).first()

        if existing:
            continue

        # Find an eligible contributor.
        contributor = find_best_contributor(
            db,
            task.required_skills or [],
            task_id=task.id
        )

        if not contributor:

            # Avoid creating the same unavailable event
            # on every background worker cycle.
            latest_event = db.query(ActivityLog).filter(
                ActivityLog.entity_type == "task",
                ActivityLog.entity_id == task.id,
                ActivityLog.action.in_([
                    "assigned",
                    "reassigned",
                    "reassignment_unavailable"
                ])
            ).order_by(
                ActivityLog.id.desc()
            ).first()

            if (
                latest_event is None
                or latest_event.action != "reassignment_unavailable"
            ):
                db.add(ActivityLog(
                    entity_type="task",
                    entity_id=task.id,
                    action="reassignment_unavailable",
                    details=(
                        "No eligible contributor is currently "
                        "available. The task will be retried."
                    )
                ))

            continue

        # --------------------------------------------------
        # 3. Claim the pending task atomically
        # --------------------------------------------------

        claim = db.query(Task).filter(
            Task.id == task.id,
            Task.status == "pending"
        ).update(
            {Task.status: "assigned"},
            synchronize_session=False
        )

        # Another request or worker may have claimed it.
        if claim != 1:
            continue

        task.status = "assigned"

        # Check whether this task has previous attempts.
        previous_attempt = db.query(Assignment).filter(
            Assignment.task_id == task.id
        ).first()

        assignment = Assignment(
            task_id=task.id,
            contributor_id=contributor.id,
            status="assigned",
            response_timeout_seconds=random.randint(5, 20)
        )

        db.add(assignment)
        db.flush()

        if previous_attempt:

            action = "reassigned"

            details = (
                f"Automatically reassigned to contributor "
                f"{contributor.id} after a previous attempt"
            )

        else:

            action = "assigned"

            details = (
                f"Automatically assigned to contributor "
                f"{contributor.id} by the background worker"
            )

        db.add(ActivityLog(
            entity_type="task",
            entity_id=task.id,
            action=action,
            details=details
        ))

        reassigned_task_ids.append(task.id)

    # --------------------------------------------------
    # 4. Commit all changes
    # --------------------------------------------------

    db.commit()

    return reassigned_task_ids