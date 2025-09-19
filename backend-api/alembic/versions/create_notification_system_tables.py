"""Create notification system tables

Revision ID: create_notification_system_tables
Revises: c7d25ff49457
Create Date: 2025-01-19 21:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_notification_system_tables'
down_revision = 'c7d25ff49457'
branch_labels = None
depends_on = None


def upgrade():
    # Create notification_templates table
    op.create_table('notification_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=False),
        sa.Column('template_text', sa.Text(), nullable=False),
        sa.Column('emoji_set', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tone', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_notification_preferences table
    op.create_table('user_notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('frequency', sa.String(length=20), nullable=True),
        sa.Column('quiet_hours', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('impact_level', sa.String(length=20), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notifications_sent table
    op.create_table('notifications_sent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('style', sa.String(length=50), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('opened_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('clicked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('engagement_score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['notification_templates.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create notification_ab_tests table
    op.create_table('notification_ab_tests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('test_name', sa.String(length=100), nullable=False),
        sa.Column('variant_a', sa.Text(), nullable=False),
        sa.Column('variant_b', sa.Text(), nullable=False),
        sa.Column('winner', sa.String(length=1), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('test_duration', sa.Integer(), nullable=True),
        sa.Column('total_sends', sa.Integer(), nullable=True),
        sa.Column('variant_a_opens', sa.Integer(), nullable=True),
        sa.Column('variant_b_opens', sa.Integer(), nullable=True),
        sa.Column('variant_a_clicks', sa.Integer(), nullable=True),
        sa.Column('variant_b_clicks', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('idx_notifications_sent_user_id', 'notifications_sent', ['user_id'])
    op.create_index('idx_notifications_sent_sent_at', 'notifications_sent', ['sent_at'])
    op.create_index('idx_user_notification_preferences_user_id', 'user_notification_preferences', ['user_id'])
    op.create_index('idx_notification_ab_tests_created_at', 'notification_ab_tests', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_notification_ab_tests_created_at', table_name='notification_ab_tests')
    op.drop_index('idx_user_notification_preferences_user_id', table_name='user_notification_preferences')
    op.drop_index('idx_notifications_sent_sent_at', table_name='notifications_sent')
    op.drop_index('idx_notifications_sent_user_id', table_name='notifications_sent')
    
    # Drop tables
    op.drop_table('notification_ab_tests')
    op.drop_table('notifications_sent')
    op.drop_table('user_notification_preferences')
    op.drop_table('notification_templates')
