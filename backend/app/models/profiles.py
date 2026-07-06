from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Profile(Base):
    """One row per user. Stores simple career-related profile data."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Skills stored as a simple comma-separated string. Easy for students to read.
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preferred_role: Mapped[str | None] = mapped_column(String(150), nullable=True)
    preferred_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="profile")
