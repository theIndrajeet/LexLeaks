"""Add category column to posts table

Revision ID: 85c452a34a1f
Revises: 
Create Date: 2025-07-01 21:15:04.551892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85c452a34a1f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add category column to posts table
    op.add_column('posts', sa.Column('category', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_posts_category'), 'posts', ['category'], unique=False)


def downgrade() -> None:
    # Remove category column from posts table
    op.drop_index(op.f('ix_posts_category'), table_name='posts')
    op.drop_column('posts', 'category')
