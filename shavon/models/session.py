from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
    relationship,
)

from shavon.models import ModelBase
from shavon.utilities import random_alphanumeric
from shavon.utilities import dthelpers
from shavon.utilities.dbhelpers import AsyncDatabaseConnection
from shavon.models.auth import User


class Session(ModelBase):
    __tablename__ = "sessions"

    session_key: Mapped[str] = mapped_column(
        sa.String(32),
        nullable=False,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        dthelpers.TZDateTime,
        nullable=False,
        default=dthelpers.now,
    )
    last_accessed: Mapped[sa.DateTime] = mapped_column(
        dthelpers.TZDateTime,
        nullable=False,
        default=dthelpers.now,
    )
    ip_address: Mapped[str] = mapped_column(
        sa.String(45),
        nullable=True,
    )
    user_agent: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=True,
    )

    @classmethod
    async def create_session(
        cls,
        session: AsyncDatabaseConnection,
        user_id: int,
        ip_address: str = None,
        user_agent: str = None,
    ) -> Session:
        """Create a new session for the user."""

        # Session key must be unique
        unique_session_key = None
        found_unique_key = False

        # Check until a unique session key is found
        while not found_unique_key:
            unique_session_key = random_alphanumeric(32)
            statement = sa.select(
                sa.func.count(cls.session_key)
            ).where(
                cls.session_key == unique_session_key
            )

            result = await session.execute(statement)
            existing_count = result.scalar()
            if existing_count == 0:
                found_unique_key = True

        # Create the new session
        new_user_session = cls(
            user_id=user_id,
            session_key=unique_session_key,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        session.add(new_user_session)
        await session.flush()
        return new_user_session

    @classmethod
    async def get_by_user_and_key(
        cls,
        session: AsyncDatabaseConnection,
        user_id: int,
        session_key: str,
    ) -> Session | None:
        """Get a session by user_id and session_key."""
        result = await session.execute(
            sa.select(cls).where(
                sa.and_(
                    cls.user_id == user_id,
                    cls.session_key == session_key,
                )
            )
        )
        return result.scalars().first()

    async def update_last_accessed(
        self,
        session: AsyncDatabaseConnection,
    ) -> None:
        """Update the last_accessed timestamp."""
        self.last_accessed = dthelpers.now()
        session.add(self)
        await session.flush()

