"""添加预算范围和项目周期字段

Revision ID: add_budget_timeline_fields
Revises:
Create Date: 2025-11-09 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_budget_timeline_fields'
down_revision = 'add_ai_models_table'
branch_labels = None
depends_on = None


def upgrade():
    """添加预算范围和项目周期字段"""
    # 添加 budget_range 字段
    op.add_column('proposals', sa.Column('budget_range', sa.String(length=100), nullable=True))

    # 添加 timeline 字段
    op.add_column('proposals', sa.Column('timeline', sa.String(length=100), nullable=True))


def downgrade():
    """移除预算范围和项目周期字段"""
    # 移除 budget_range 字段
    op.drop_column('proposals', 'budget_range')

    # 移除 timeline 字段
    op.drop_column('proposals', 'timeline')