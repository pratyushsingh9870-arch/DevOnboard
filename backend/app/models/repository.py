from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Repository(Base):

    __tablename__ = "repositories"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    name = Column(String, nullable=False)

    full_name = Column(
        String,
        unique=True,
        nullable=False
    )

    github_url = Column(String, nullable=False)

    description = Column(String)

    # Tech stack
    primary_language = Column(String)

    languages = Column(JSON)

    detected_stack = Column(JSON)

    # Stats
    stars = Column(Integer, default=0)

    forks = Column(Integer, default=0)

    file_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    last_analyzed = Column(DateTime(timezone=True))

    def __repr__(self):

        return f"<Repository {self.full_name}>"