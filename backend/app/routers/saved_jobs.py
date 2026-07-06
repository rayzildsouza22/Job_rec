from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.jobs import Job
from app.models.saved_jobs import SavedJob
from app.models.users import User
from app.schemas.saved_jobs import SavedJobResponse
from app.utils.oauth2 import get_current_user

router = APIRouter(prefix="/saved-jobs", tags=["Saved Jobs"])


@router.get("", response_model=List[SavedJobResponse])
def list_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(SavedJob)
        .where(SavedJob.user_id == current_user.id)
        .order_by(SavedJob.saved_at.desc())
    )
    saved_rows = list(db.scalars(stmt))
    # Attach job via a small manual lookup to keep the code beginner-friendly.
    result = []
    for row in saved_rows:
        job = db.get(Job, row.job_id)
        if job is not None:
            result.append({"id": row.id, "saved_at": row.saved_at, "job": job})
    return result


@router.post("/{job_id}", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = db.scalar(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == job_id,
        )
    )
    if existing:
        return {"id": existing.id, "saved_at": existing.saved_at, "job": job}

    row = SavedJob(user_id=current_user.id, job_id=job_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "saved_at": row.saved_at, "job": job}


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.scalar(
        select(SavedJob).where(
            SavedJob.user_id == current_user.id,
            SavedJob.job_id == job_id,
        )
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(row)
    db.commit()
    return None
