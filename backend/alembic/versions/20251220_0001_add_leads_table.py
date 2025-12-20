"""add leads table

Revision ID: 20251220_0001
Revises: 20251219_0008
Create Date: 2024-12-20

"""
from alembic import op
import sqlalchemy as sa


revision = '20251220_0001'
down_revision = '20251219_0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('status', sa.Enum('new', 'contacted', 'qualified', 'nurturing', 'converted', 'lost', name='leadstatus'), nullable=False, server_default='new'),
        sa.Column('source', sa.Enum('organic', 'referral', 'paid_ads', 'social', 'partner', 'direct', 'other', name='leadsource'), nullable=False, server_default='organic'),
        sa.Column('interest_category', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_to_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('opportunity_id', sa.Integer(), sa.ForeignKey('opportunities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('last_contacted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_opt_in', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_sequence_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_email_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )
    op.create_index('ix_leads_status', 'leads', ['status'])


def downgrade() -> None:
    op.drop_index('ix_leads_status', table_name='leads')
    op.drop_table('leads')
    op.execute("DROP TYPE IF EXISTS leadstatus")
    op.execute("DROP TYPE IF EXISTS leadsource")
