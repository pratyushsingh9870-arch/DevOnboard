from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
import uuid

from ..database import Base


class Documentation(Base):

    __tablename__ = "documentation"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    repo_id = Column(
        String,
        ForeignKey("repositories.id"),
        nullable=False
    )

    # readme / setup / architecture
    doc_type = Column(String, nullable=False)

    # AI generated content
    content = Column(Text, nullable=False)

    # Metadata
    generated_by = Column(
        String,
        default="openrouter-ai"
    )

    version = Column(String, default="1.0")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    def __repr__(self):

        return f"<Documentation {self.doc_type} for repo {self.repo_id}>"