"""create User and LoginAttempt models

Revision ID: 6926eefb0047
Revises: 
Create Date: 2025-06-09 04:00:16.116239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from shavon.utilities import dthelpers


# revision identifiers, used by Alembic.
revision: str = '6926eefb0047'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('login_attempts',
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('attempt_count', sa.Integer(), nullable=False),
        sa.Column('last_attempt', dthelpers.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('ip_address')
    )

    op.create_table('users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('date_created', dthelpers.TZDateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('login_attempts')
