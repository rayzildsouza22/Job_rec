from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Recommendation(Base):
    """Recommendation history: one row per (user, job) result.

    Similarity is the raw Qdrant cosine score (not a hiring probability).
    """

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )
    similarity: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str] = mapped_column(Text)  # short LLM explanation
    matching_skills: Mapped[str] = mapped_column(Text)   # comma-separated
    missing_skills: Mapped[str] = mapped_column(Text)    # comma-separated
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="recommendations")
