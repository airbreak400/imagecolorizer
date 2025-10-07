"""Add language support

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=10), nullable=True, default='en'),
        sa.Column('is_bot', sa.Boolean(), nullable=True, default=False),
        sa.Column('is_premium', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('total_requests', sa.Integer(), nullable=True, default=0),
        sa.Column('total_images_processed', sa.Integer(), nullable=True, default=0),
        sa.Column('is_blocked', sa.Boolean(), nullable=True, default=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    
    # Create requests table
    op.create_table('requests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('request_type', sa.String(length=50), nullable=False),
        sa.Column('file_id', sa.String(length=255), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True, default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create statistics table
    op.create_table('statistics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('total_users', sa.Integer(), nullable=True, default=0),
        sa.Column('active_users', sa.Integer(), nullable=True, default=0),
        sa.Column('total_requests', sa.Integer(), nullable=True, default=0),
        sa.Column('successful_requests', sa.Integer(), nullable=True, default=0),
        sa.Column('failed_requests', sa.Integer(), nullable=True, default=0),
        sa.Column('total_processing_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('average_processing_time', sa.Float(), nullable=True, default=0.0),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('statistics')
    op.drop_table('requests')
    op.drop_table('users')



