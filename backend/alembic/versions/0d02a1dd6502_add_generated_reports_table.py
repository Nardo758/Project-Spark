"""add_generated_reports_table

Revision ID: 0d02a1dd6502
Revises: 20251220_0002
Create Date: 2025-12-21 13:11:12.153694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '0d02a1dd6502'
down_revision: Union[str, Sequence[str], None] = '20251220_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    reporttype = postgresql.ENUM('feasibility_study', 'market_analysis', 'strategic_assessment', 'progress_report', name='reporttype', create_type=False)
    reporttype.create(op.get_bind(), checkfirst=True)
    
    reportstatus = postgresql.ENUM('pending', 'generating', 'completed', 'failed', name='reportstatus', create_type=False)
    reportstatus.create(op.get_bind(), checkfirst=True)
    
    op.create_table('generated_reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('opportunity_id', sa.Integer(), nullable=True),
    sa.Column('report_type', reporttype, nullable=False),
    sa.Column('status', reportstatus, nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('confidence_score', sa.Integer(), nullable=True),
    sa.Column('generation_time_ms', sa.Integer(), nullable=True),
    sa.Column('tokens_used', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_generated_reports_created_at'), 'generated_reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_generated_reports_id'), 'generated_reports', ['id'], unique=False)
    op.create_index(op.f('ix_generated_reports_opportunity_id'), 'generated_reports', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_generated_reports_report_type'), 'generated_reports', ['report_type'], unique=False)
    op.create_index(op.f('ix_generated_reports_user_id'), 'generated_reports', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_generated_reports_user_id'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_report_type'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_opportunity_id'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_id'), table_name='generated_reports')
    op.drop_index(op.f('ix_generated_reports_created_at'), table_name='generated_reports')
    op.drop_table('generated_reports')
    op.execute("DROP TYPE IF EXISTS reporttype")
    op.execute("DROP TYPE IF EXISTS reportstatus")
