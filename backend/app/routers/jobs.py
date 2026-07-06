from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.jobs import Job
from app.models.users import User
from app.schemas.jobs import JobCreate, JobResponse, JobUpdate
from app.utils.admin import require_admin
from app.utils.oauth2 import get_current_user
from app.utils.vector_store import delete_job as qdrant_delete
from app.utils.vector_store import upsert_job as qdrant_upsert

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _job_to_embedding_text(job: Job) -> str:
    """Text we embed for a job. Kept small and focused."""
    parts = [
        f"Title: {job.title}",
        f"Company: {job.company}",
        f"Location: {job.location or ''}",
        f"Experience: {job.experience or ''}",
        f"Required skills: {job.required_skills}",
        f"Description: {job.description}",
    ]
    return "\n".join(parts)


@router.get("", response_model=List[JobResponse])
def list_jobs(
    q: Optional[str] = Query(None, description="Keyword filter"),
    location: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    if q:
        needle = f"%{q.lower()}%"
        stmt = select(Job).where(
            or_(
                Job.title.ilike(needle),
                Job.company.ilike(needle),
                Job.description.ilike(needle),
                Job.required_skills.ilike(needle),
            )
        ).order_by(Job.created_at.desc()).limit(limit)
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    return list(db.scalars(stmt))


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    _user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    job = Job(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    # Best-effort embed. If Qdrant is offline, we still keep the DB row.
    try:
        qdrant_upsert(job.id, _job_to_embedding_text(job))
    except Exception as exc:  # noqa: BLE001
        # Surface a warning but don't fail the API call.
        print(f"[jobs] Qdrant upsert failed for job {job.id}: {exc}")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    payload: JobUpdate,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    try:
        qdrant_upsert(job.id, _job_to_embedding_text(job))
    except Exception as exc:  # noqa: BLE001
        print(f"[jobs] Qdrant upsert failed for job {job.id}: {exc}")
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    try:
        qdrant_delete(job_id)
    except Exception as exc:  # noqa: BLE001
        print(f"[jobs] Qdrant delete failed for job {job_id}: {exc}")
    return None


@router.post("/{job_id}/reindex", status_code=status.HTTP_202_ACCEPTED)
def reindex_job(
    job_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Force a re-embed of one job. Useful after changing the embedding model."""
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    qdrant_upsert(job.id, _job_to_embedding_text(job))
    return {"status": "reindexed", "job_id": job.id}
