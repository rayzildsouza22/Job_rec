"""Recommendation endpoints.

Flow:
  1. Load the user's resume text (required).
  2. Optionally combine with profile skills.
  3. Ask Qdrant for top-K semantic matches -> list of (job_id, similarity).
  4. Fetch the full jobs from PostgreSQL.
  5. Compute matching/missing skills deterministically.
  6. Ask Groq (via LangChain) for a short natural-language explanation per job.
  7. Store each result as a recommendation history row.
  8. Return everything to the frontend.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.jobs import Job
from app.models.profiles import Profile
from app.models.recommendations import Recommendation
from app.models.resumes import Resume
from app.models.users import User
from app.schemas.recommendations import (
    RecommendationGenerateResponse,
    RecommendationHistoryItem,
    RecommendationItem,
    SkillGapResponse,
)
from app.utils.oauth2 import get_current_user
from app.utils.rag import explain_match, skill_gap_suggestions
from app.utils.skills import compare_skills, parse_skills
from app.utils.vector_store import search as qdrant_search

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def _load_user_context(db: Session, user: User) -> tuple[str, list[str]]:
    """Return (query_text, user_skills). Requires a resume to exist."""
    resume = db.scalar(select(Resume).where(Resume.user_id == user.id))
    if resume is None or not resume.extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume before requesting recommendations.",
        )
    profile = db.scalar(select(Profile).where(Profile.user_id == user.id))

    user_skills = parse_skills(profile.skills if profile else None)
    # Query text = resume text + profile hint (short). Same embedding model
    # used for jobs, so vectors are directly comparable.
    hint_parts: list[str] = []
    if profile:
        if profile.preferred_role:
            hint_parts.append(f"Preferred role: {profile.preferred_role}")
        if profile.skills:
            hint_parts.append(f"Skills: {profile.skills}")
        if profile.experience_level:
            hint_parts.append(f"Experience: {profile.experience_level}")
    query_text = resume.extracted_text
    if hint_parts:
        query_text = "\n".join(hint_parts) + "\n\n" + query_text
    return query_text, user_skills


@router.post("/generate", response_model=RecommendationGenerateResponse)
def generate_recommendations(
    top_k: int = 5,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    top_k = max(1, min(top_k, 10))
    query_text, user_skills = _load_user_context(db, current_user)

    # 1. Qdrant semantic search
    try:
        hits = qdrant_search(query_text, top_k=top_k)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=503,
            detail=f"Vector search unavailable: {exc}",
        )

    if not hits:
        return {"items": []}

    # 2. Fetch full job rows from PostgreSQL in one query
    job_ids = [h[0] for h in hits]
    stmt = select(Job).where(Job.id.in_(job_ids))
    jobs_by_id = {j.id: j for j in db.scalars(stmt)}

    # 3. Build response items
    items: List[RecommendationItem] = []
    for job_id, similarity in hits:
        job = jobs_by_id.get(job_id)
        if job is None:
            # Job was deleted after being embedded; skip.
            continue
        job_skills = parse_skills(job.required_skills)
        matching, missing = compare_skills(user_skills, job_skills)

        try:
            explanation = explain_match(
                resume_text=query_text,
                job_title=job.title,
                job_company=job.company,
                job_description=job.description,
                matching_skills=matching,
                missing_skills=missing,
            )
        except Exception as exc:  # noqa: BLE001
            # Fall back to deterministic explanation if LLM is unavailable.
            explanation = (
                f"Semantic similarity {similarity:.2f}. "
                f"Matching skills: {', '.join(matching) or 'none'}. "
                f"Missing skills: {', '.join(missing) or 'none'}. "
                f"(LLM unavailable: {exc})"
            )

        # 4. Persist to recommendation history
        db.add(
            Recommendation(
                user_id=current_user.id,
                job_id=job.id,
                similarity=similarity,
                explanation=explanation,
                matching_skills=",".join(matching),
                missing_skills=",".join(missing),
            )
        )

        items.append(
            RecommendationItem(
                job=job,  # type: ignore[arg-type]
                similarity=similarity,
                matching_skills=matching,
                missing_skills=missing,
                explanation=explanation,
            )
        )

    db.commit()
    return {"items": items}


@router.get("/history", response_model=List[RecommendationHistoryItem])
def read_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 200))
    stmt = (
        select(Recommendation)
        .where(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(stmt))


@router.get("/skill-gap/{job_id}", response_model=SkillGapResponse)
def skill_gap(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    resume = db.scalar(select(Resume).where(Resume.user_id == current_user.id))
    profile = db.scalar(select(Profile).where(Profile.user_id == current_user.id))
    user_skills = parse_skills(profile.skills if profile else None)

    job_skills = parse_skills(job.required_skills)
    matching, missing = compare_skills(user_skills, job_skills)

    resume_text = resume.extracted_text if resume else ""
    try:
        suggestions = skill_gap_suggestions(
            resume_text=resume_text,
            job_title=job.title,
            job_description=job.description,
            missing_skills=missing,
        )
    except Exception as exc:  # noqa: BLE001
        suggestions = f"(LLM unavailable: {exc})"

    return {
        "job_id": job.id,
        "matching_skills": matching,
        "missing_skills": missing,
        "suggestions": suggestions,
    }
