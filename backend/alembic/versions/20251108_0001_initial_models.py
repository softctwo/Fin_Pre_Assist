"""initial models

Revision ID: 20251108_0001
Revises: 
Create Date: 2025-11-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251108_0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100)),
        sa.Column('role', sa.Enum('admin','user','viewer', name='userrole'), nullable=True),
        sa.Column('is_active', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )

    # documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False, index=True),
        sa.Column('type', sa.Enum('technical_proposal','business_proposal','quotation','bid_document','case_study','other', name='documenttype'), nullable=False, index=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=200), nullable=False),
        sa.Column('file_size', sa.Integer()),
        sa.Column('mime_type', sa.String(length=100)),
        sa.Column('content_text', sa.Text()),
        sa.Column('doc_metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('industry', sa.String(length=100), index=True),
        sa.Column('customer_name', sa.String(length=200), index=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('is_vectorized', sa.Integer(), server_default='0', index=True),
        sa.Column('vector_id', sa.String(length=100), index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),        
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_document_user_type_created','documents',['user_id','type','created_at'])
    op.create_index('ix_document_customer_industry','documents',['customer_name','industry'])
    op.create_index('ix_document_vectorized_created','documents',['is_vectorized','created_at'])

    # knowledge_base table
    op.create_table(
        'knowledge_base',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('category', sa.String(length=100), nullable=False, index=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('kb_metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('is_vectorized', sa.Integer(), server_default='0'),
        sa.Column('vector_id', sa.String(length=100)),
        sa.Column('weight', sa.Integer(), server_default='1'),
        sa.Column('is_active', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    # proposals table
    op.create_table(
        'proposals',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False, index=True),
        sa.Column('customer_name', sa.String(length=200), nullable=False, index=True),
        sa.Column('customer_industry', sa.String(length=100), index=True),
        sa.Column('customer_contact', sa.String(length=100)),
        sa.Column('requirements', sa.Text()),
        sa.Column('requirements_structured', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('executive_summary', sa.Text()),
        sa.Column('solution_overview', sa.Text()),
        sa.Column('technical_details', sa.Text()),
        sa.Column('implementation_plan', sa.Text()),
        sa.Column('pricing', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('full_content', sa.Text()),
        sa.Column('reference_documents', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('status', sa.Enum('draft','generating','completed','exported','archived', name='proposalstatus'), server_default='draft', index=True),
        sa.Column('proposal_metadata', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_proposal_user_status_created','proposals',['user_id','status','created_at'])
    op.create_index('ix_proposal_customer_status','proposals',['customer_name','status'])
    op.create_index('ix_proposal_industry_created','proposals',['customer_industry','created_at'])

    # templates table
    op.create_table(
        'templates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('type', sa.Enum('proposal','quotation','contract','presentation', name='templatetype'), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables', postgresql.JSON(astext_type=sa.Text())),
        sa.Column('file_path', sa.String(length=500)),
        sa.Column('is_default', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Integer(), server_default='1'),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )

    # proposal_versions table
    op.create_table(
        'proposal_versions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('proposal_id', sa.Integer(), sa.ForeignKey('proposals.id'), nullable=False, index=True),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('customer_name', sa.String(length=200)),
        sa.Column('customer_industry', sa.String(length=100)),
        sa.Column('customer_contact', sa.String(length=100)),
        sa.Column('content', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('changes_summary', sa.Text()),
        sa.Column('change_type', sa.String(length=50)),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), index=True),
        sa.Column('metadata_info', postgresql.JSON(astext_type=sa.Text())),
        sa.UniqueConstraint('proposal_id','version_number', name='uq_proposal_version'),
    )
    op.create_index('ix_version_proposal_created','proposal_versions',['proposal_id','created_at'])
    op.create_index('ix_version_created','proposal_versions',['created_at'])


def downgrade() -> None:
    op.drop_index('ix_version_created', table_name='proposal_versions')
    op.drop_index('ix_version_proposal_created', table_name='proposal_versions')
    op.drop_table('proposal_versions')

    op.drop_table('templates')

    op.drop_index('ix_proposal_industry_created', table_name='proposals')
    op.drop_index('ix_proposal_customer_status', table_name='proposals')
    op.drop_index('ix_proposal_user_status_created', table_name='proposals')
    op.drop_table('proposals')

    op.drop_table('knowledge_base')

    op.drop_index('ix_document_vectorized_created', table_name='documents')
    op.drop_index('ix_document_customer_industry', table_name='documents')
    op.drop_index('ix_document_user_type_created', table_name='documents')
    op.drop_table('documents')

    op.drop_table('users')

    # drop enums
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS proposalstatus')
    op.execute('DROP TYPE IF EXISTS templatetype')
