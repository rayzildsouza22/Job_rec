from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    # Note: extracted_text can be large; we still expose it so the user can verify.
    extracted_text: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
