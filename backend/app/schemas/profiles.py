from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    education: str | None = None
    skills: str | None = None  # comma-separated
    experience_level: str | None = None
    preferred_role: str | None = None
    preferred_location: str | None = None


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: str | None
    education: str | None
    skills: str | None
    experience_level: str | None
    preferred_role: str | None
    preferred_location: str | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
