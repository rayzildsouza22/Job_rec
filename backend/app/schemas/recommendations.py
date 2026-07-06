from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.jobs import JobResponse


class RecommendationItem(BaseModel):
    job: JobResponse
    similarity: float  # raw Qdrant cosine similarity, not a hiring probability
    matching_skills: List[str]
    missing_skills: List[str]
    explanation: str


class RecommendationGenerateResponse(BaseModel):
    items: List[RecommendationItem]


class RecommendationHistoryItem(BaseModel):
    id: int
    job_id: int
    similarity: float
    explanation: str
    matching_skills: str
    missing_skills: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkillGapResponse(BaseModel):
    job_id: int
    matching_skills: List[str]
    missing_skills: List[str]
    suggestions: str  # short LLM guidance
