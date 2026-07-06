from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.jobs import JobResponse


class SavedJobResponse(BaseModel):
    id: int
    job: JobResponse
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)
