"""Add session table

Revision ID: aaa60591f97f
Revises: 6926eefb0047
Create Date: 2025-06-10 04:01:45.662715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from shavon.utilities import dthelpers

# revision identifiers, used by Alembic.
revision: str = 'aaa60591f97f'
down_revision: Union[str, None] = '6926eefb0047'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table('sessions',
        sa.Column('session_key', sa.String(length=32), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', dthelpers.TZDateTime(), nullable=False),
        sa.Column('last_accessed', dthelpers.TZDateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('session_key')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('sessions')
