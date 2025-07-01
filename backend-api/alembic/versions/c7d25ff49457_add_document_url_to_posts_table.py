"""Add document_url to posts table

Revision ID: c7d25ff49457
Revises: 85c452a34a1f
Create Date: 2025-07-01 22:32:18.901302

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d25ff49457'
down_revision: Union[str, None] = '85c452a34a1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add document_url column to posts table
    op.add_column('posts', sa.Column('document_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove document_url column from posts table
    op.drop_column('posts', 'document_url')
