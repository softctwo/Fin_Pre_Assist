"""add ai models table

Revision ID: add_ai_models_table
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_ai_models_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 创建ai_models表
    op.create_table('ai_models',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.String(length=500), nullable=True),
        sa.Column('base_url', sa.String(length=500), nullable=True),
        sa.Column('max_tokens', sa.Integer(), nullable=True),
        sa.Column('context_length', sa.Integer(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('top_p', sa.Float(), nullable=True),
        sa.Column('frequency_penalty', sa.Float(), nullable=True),
        sa.Column('presence_penalty', sa.Float(), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('headers', sa.JSON(), nullable=True),
        sa.Column('extra_params', sa.JSON(), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_calls', sa.Integer(), nullable=True),
        sa.Column('success_calls', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建索引
    op.create_index(op.f('ix_ai_models_id'), 'ai_models', ['id'])
    op.create_index(op.f('ix_ai_models_provider'), 'ai_models', ['provider'])
    op.create_index(op.f('ix_ai_models_is_enabled'), 'ai_models', ['is_enabled'])
    op.create_index(op.f('ix_ai_models_is_default'), 'ai_models', ['is_default'])


def downgrade():
    # 删除ai_models表
    op.drop_table('ai_models')
