"""Initial database schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Departments table
    op.create_table(
        'departments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('ministry', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permissions', sa.JSON(), default=list),
        sa.Column('is_system', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('department_id', sa.String(36), sa.ForeignKey('departments.id'), nullable=True),
        sa.Column('role_id', sa.String(36), sa.ForeignKey('roles.id'), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_users_department_id', 'users', ['department_id'])
    op.create_index('ix_users_role_id', 'users', ['role_id'])

    # Documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=True),
        sa.Column('uploaded_by_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('extracted_data', sa.JSON(), nullable=True),
        sa.Column('processing_status', sa.String(50), default='pending'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_documents_uploaded_by_id', 'documents', ['uploaded_by_id'])

    # Vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('registration_no', sa.String(100), unique=True, nullable=True),
        sa.Column('gstin', sa.String(15), unique=True, nullable=True),
        sa.Column('pan', sa.String(10), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verification_date', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_vendors_gstin', 'vendors', ['gstin'])
    op.create_index('ix_vendors_name', 'vendors', ['name'])

    # Evaluations table
    op.create_table(
        'evaluations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('reference_id', sa.String(50), unique=True, nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), default='draft'),
        sa.Column('method', sa.String(50), default='qcbs'),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('tender_document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('created_by_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('processing_started_at', sa.DateTime(), nullable=True),
        sa.Column('processing_completed_at', sa.DateTime(), nullable=True),
        sa.Column('results_summary', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_evaluations_reference_id', 'evaluations', ['reference_id'])
    op.create_index('ix_evaluations_created_by_id', 'evaluations', ['created_by_id'])
    op.create_index('ix_evaluations_status', 'evaluations', ['status'])

    # Bids table
    op.create_table(
        'bids',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('evaluation_id', sa.String(36), sa.ForeignKey('evaluations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vendor_id', sa.String(36), sa.ForeignKey('vendors.id'), nullable=False),
        sa.Column('document_id', sa.String(36), sa.ForeignKey('documents.id'), nullable=True),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('bid_amount', sa.BigInteger(), nullable=True),  # Amount in paisa
        sa.Column('currency', sa.String(3), default='INR'),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('compliance_status', sa.String(50), nullable=True),
        sa.Column('compliance_issues', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('evaluation_id', 'vendor_id', name='uq_bids_evaluation_vendor'),
    )
    op.create_index('ix_bids_evaluation_id', 'bids', ['evaluation_id'])
    op.create_index('ix_bids_vendor_id', 'bids', ['vendor_id'])

    # Scores table
    op.create_table(
        'scores',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('bid_id', sa.String(36), sa.ForeignKey('bids.id', ondelete='CASCADE'), nullable=False),
        sa.Column('score_type', sa.String(50), nullable=False),  # technical, financial, compliance, total
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('max_score', sa.Float(), default=100.0),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('weighted_score', sa.Float(), nullable=True),
        sa.Column('breakdown', sa.JSON(), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('scored_by', sa.String(100), nullable=True),  # Agent name or user
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_scores_bid_id', 'scores', ['bid_id'])
    op.create_index('ix_scores_score_type', 'scores', ['score_type'])

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', sa.String(36), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])

    # Insert default roles
    op.execute("""
        INSERT INTO roles (id, name, description, permissions, is_system, created_at, updated_at)
        VALUES
        ('role-admin', 'Admin', 'System administrator with full access',
         '["evaluation:create", "evaluation:read", "evaluation:update", "evaluation:delete", "evaluation:run", "vendor:read", "vendor:create", "vendor:update", "document:upload", "document:read", "document:delete", "report:read", "report:export", "user:read", "user:create", "user:update", "user:delete", "audit:read", "settings:manage"]',
         1, datetime('now'), datetime('now')),
        ('role-evaluator', 'Evaluator', 'Can create and run evaluations',
         '["evaluation:create", "evaluation:read", "evaluation:update", "evaluation:run", "vendor:read", "vendor:create", "document:upload", "document:read", "report:read", "report:export"]',
         1, datetime('now'), datetime('now')),
        ('role-viewer', 'Viewer', 'Read-only access to evaluations and reports',
         '["evaluation:read", "vendor:read", "document:read", "report:read"]',
         1, datetime('now'), datetime('now'))
    """)


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('scores')
    op.drop_table('bids')
    op.drop_table('evaluations')
    op.drop_table('vendors')
    op.drop_table('documents')
    op.drop_table('users')
    op.drop_table('roles')
    op.drop_table('departments')
