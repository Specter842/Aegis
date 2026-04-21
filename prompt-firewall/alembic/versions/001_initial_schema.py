"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-05-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('scan_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=True),
        sa.Column('app_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('raw_prompt', sa.Text(), nullable=False),
        sa.Column('normalized_prompt', sa.Text(), nullable=True),
        sa.Column('decision', sa.String(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('trace_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('trace_id')
    )
    op.create_index(op.f('ix_scan_requests_app_id'), 'scan_requests', ['app_id'], unique=False)
    op.create_index(op.f('ix_scan_requests_id'), 'scan_requests', ['id'], unique=False)
    op.create_index(op.f('ix_scan_requests_request_id'), 'scan_requests', ['request_id'], unique=False)
    op.create_index(op.f('ix_scan_requests_tenant_id'), 'scan_requests', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_scan_requests_user_id'), 'scan_requests', ['user_id'], unique=False)
    op.create_index(op.f('ix_scan_requests_trace_id'), 'scan_requests', ['trace_id'], unique=False)

    op.create_table('scan_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_fk', sa.Integer(), nullable=True),
        sa.Column('channel_id', sa.String(), nullable=False),
        sa.Column('source_type', sa.String(), nullable=False),
        sa.Column('source_ref', sa.String(), nullable=True),
        sa.Column('trust_level', sa.Integer(), nullable=True),
        sa.Column('text_content', sa.Text(), nullable=False),
        sa.Column('sanitized_content', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['request_fk'], ['scan_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scan_channels_id'), 'scan_channels', ['id'], unique=False)

    op.create_table('scan_detections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_fk', sa.Integer(), nullable=True),
        sa.Column('channel_fk', sa.Integer(), nullable=True),
        sa.Column('scanner_name', sa.String(), nullable=False),
        sa.Column('attack_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False),
        sa.Column('matched_text', sa.String(), nullable=True),
        sa.Column('explanation', sa.String(), nullable=True),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['channel_fk'], ['scan_channels.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['request_fk'], ['scan_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scan_detections_id'), 'scan_detections', ['id'], unique=False)

def downgrade() -> None:
    op.drop_table('scan_detections')
    op.drop_table('scan_channels')
    op.drop_table('scan_requests')
