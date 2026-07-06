from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobBase(BaseModel):
    company: str = Field(min_length=1, max_length=150)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    required_skills: str = Field(min_length=1)  # comma-separated
    location: str | None = None
    experience: str | None = None
    salary: str | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    company: str | None = None
    title: str | None = None
    description: str | None = None
    required_skills: str | None = None
    location: str | None = None
    experience: str | None = None
    salary: str | None = None


class JobResponse(JobBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
