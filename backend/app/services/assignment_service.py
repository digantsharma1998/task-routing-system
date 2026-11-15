from app.models.contributor import Contributor
from app.models.assignment import Assignment


def find_best_contributor(db, required_skills, task_id=None):

    contributors = db.query(Contributor).filter(
        Contributor.available.is_(True)
    ).all()

    # Exclude contributors who have already been
    # considered for this task.
    previously_tried = set()

    if task_id is not None:
        previous_assignments = db.query(Assignment).filter(
            Assignment.task_id == task_id
        ).all()

        previously_tried = {
            assignment.contributor_id
            for assignment in previous_assignments
        }

    eligible = []

    required = {
        skill.strip().lower()
        for skill in (required_skills or [])
        if isinstance(skill, str) and skill.strip()
    }

    for contributor in contributors:

        if contributor.id in previously_tried:
            continue

        skills = {
            skill.strip().lower()
            for skill in (contributor.skills or [])
            if isinstance(skill, str) and skill.strip()
        }

        if not required.issubset(skills):
            continue

        active_count = db.query(Assignment).filter(
            Assignment.contributor_id == contributor.id,
            Assignment.status.in_(["assigned", "accepted"])
        ).count()

        capacity = contributor.max_capacity or 0

        if capacity <= 0 or active_count >= capacity:
            continue

        workload_score = (
            (capacity - active_count) / capacity
        ) * 100

        capacity_score = min(capacity / 10, 1) * 100

        skill_score = 100

        total_score = (
            workload_score * 0.50
            + capacity_score * 0.30
            + skill_score * 0.20
        )

        eligible.append({
            "score": total_score,
            "active_count": active_count,
            "contributor": contributor
        })

    if not eligible:
        return None

    eligible.sort(
        key=lambda item: (
            -item["score"],
            item["active_count"],
            item["contributor"].id
        )
    )

    return eligible[0]["contributor"]