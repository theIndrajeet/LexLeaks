"""add_verification_status_to_posts

Revision ID: b36c3c192e3d
Revises: c7d25ff49457
Create Date: 2024-12-28 09:40:31.780915

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b36c3c192e3d'
down_revision: Union[str, None] = 'c7d25ff49457'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add verification_status column to posts table
    op.add_column('posts', sa.Column('verification_status', sa.String(20), nullable=False, server_default='unverified'))


def downgrade() -> None:
    # Remove verification_status column from posts table
    op.drop_column('posts', 'verification_status')
