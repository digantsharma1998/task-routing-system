from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contributor import Contributor
from app.schemas import (
    ContributorCreate,
    ContributorUpdate,
    ContributorResponse
)

router = APIRouter(
    prefix="/contributors",
    tags=["Contributors"]
)


@router.post(
    "/",
    response_model=ContributorResponse,
    status_code=201
)
def create_contributor(
    data: ContributorCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Contributor).filter(
        Contributor.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    contributor = Contributor(
        name=data.name,
        email=data.email,
        skills=data.skills,
        max_capacity=data.max_capacity
    )

    try:
        db.add(contributor)
        db.commit()
        db.refresh(contributor)

        return contributor

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create contributor"
        )


@router.get("/", response_model=list[ContributorResponse])
def get_contributors(db: Session = Depends(get_db)):
    return db.query(Contributor).all()


@router.put(
    "/{contributor_id}",
    response_model=ContributorResponse
)
def update_contributor(
    contributor_id: int,
    data: ContributorUpdate,
    db: Session = Depends(get_db)
):
    contributor = db.query(Contributor).filter(
        Contributor.id == contributor_id
    ).first()

    if not contributor:
        raise HTTPException(
            status_code=404,
            detail="Contributor not found"
        )

    existing_email = db.query(Contributor).filter(
        Contributor.email == data.email,
        Contributor.id != contributor_id
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    try:
        contributor.name = data.name
        contributor.email = data.email
        contributor.skills = data.skills
        contributor.max_capacity = data.max_capacity
        contributor.available = data.available

        db.commit()
        db.refresh(contributor)

        return contributor

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update contributor"
        )