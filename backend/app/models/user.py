from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
        index=True
    )

    full_name = Column(String)

    hashed_password = Column(
        String,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True
    )

    role = Column(
        String,
        default="developer"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    def __repr__(self):
        return f"<User {self.email}>"