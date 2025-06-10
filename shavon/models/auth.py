from __future__ import annotations

import binascii
import hashlib
import os

import sqlalchemy as sa
from sqlalchemy.orm import (
    mapped_column,
    Mapped,
)

from shavon.models import ModelBase
from shavon.utilities import dthelpers
from shavon import db
from shavon.utilities.dbhelpers import AsyncDatabaseConnection


class User(ModelBase):
    __tablename__ = "users"
    __table_args__ = (
        sa.Index("idx_users_email", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True,
    )
    email: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
    )
    date_created: Mapped[sa.DateTime] = mapped_column(
        dthelpers.TZDateTime,
        nullable=False,
        default=dthelpers.now,
    )

    @property
    def safe_email(self) -> str:
        email = self.email
        return email[:2] + "*"*(email.find('@')-2) + email[email.find('@'):]

    @staticmethod
    def hash_password(password: str, salt: str = None):
        """ Hash a password with PBKDF2.
            If no salt is provided, a new one will be generated.
        """
        if not salt:
            salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            password.encode('utf-8'),
            salt,
            100000
        )
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')
    
    @staticmethod
    def verify_password(hashed_password, pt_password):
        """ Compare a plaintext.
        """
        salt = hashed_password[:64]
        hashed_password = hashed_password[64:]
        pwdhash = hashlib.pbkdf2_hmac(
            'sha512',
            pt_password.encode('utf-8'),
            salt.encode('ascii'),
            100000
        )
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == hashed_password

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncDatabaseConnection,
        user_id: int,
    ) -> User | None:
        """ Get a user by their ID.
        """
        result = await session.execute(
            sa.select(cls).where(cls.id == user_id)
        )
        return result.scalars().first()


class LoginAttempt(ModelBase):
    __tablename__ = "login_attempts"

    ip_address: Mapped[int] = mapped_column(
        sa.String(45),
        nullable=False,
        primary_key=True,
    )
    attempt_count: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
    )
    last_attempt: Mapped[sa.DateTime] = mapped_column(
        dthelpers.TZDateTime,
        nullable=False,
        default=dthelpers.now,
    )

    @classmethod
    async def get_attempt(
        cls,
        session: AsyncDatabaseConnection,
        ip_address: str, 
    ) -> LoginAttempt:
        """ Get or create a login attempt record for the given IP address.
        """

        # Execute the query to retrieve an existing LoginAttempt
        result = await session.execute(
             sa.select(cls).where(cls.ip_address == ip_address)
        )
        record = result.scalars().first()

        # If no record exists, create a new one
        if record is None:
            print(f"Creating new LoginAttempt for IP: {ip_address}")
            record = cls(ip_address=ip_address, attempt_count=0)
        else:
            print(f"Found existing LoginAttempt for IP: {ip_address}, "
                  f"Current attempts: {record.attempt_count}")
        return record
    
    def increment(self) -> None:
        """ Increment the attempt count and update the last attempt time.
        """
        self.attempt_count += 1
        self.last_attempt = dthelpers.now()
        

