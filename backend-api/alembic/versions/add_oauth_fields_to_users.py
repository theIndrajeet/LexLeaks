"""add_oauth_fields_to_users

Revision ID: add_oauth_fields_to_users
Revises: c7d25ff49457
Create Date: 2024-12-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_oauth_fields_to_users'
down_revision = 'b36c3c192e3d'
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth fields to users table
    op.add_column('users', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('profile_picture', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('oauth_provider', sa.String(50), nullable=True))
    
    # Make username and hashed_password nullable for OAuth users
    op.alter_column('users', 'username', nullable=True)
    op.alter_column('users', 'hashed_password', nullable=True)
    
    # Create indexes for new fields
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)


def downgrade():
    # Remove indexes
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    
    # Remove OAuth fields
    op.drop_column('users', 'oauth_provider')
    op.drop_column('users', 'profile_picture')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'email')
    
    # Make username and hashed_password non-nullable again
    op.alter_column('users', 'hashed_password', nullable=False)
    op.alter_column('users', 'username', nullable=False)
