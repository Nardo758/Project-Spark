"""Add saved_searches and lead_purchases tables

Revision ID: 20251220_0002
Revises: 20251220_0001
Create Date: 2024-12-20

"""
from alembic import op
import sqlalchemy as sa

revision = '20251220_0002'
down_revision = '20251220_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'saved_searches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('query', sa.String(length=500), nullable=True),
        sa.Column('filters', sa.JSON(), nullable=True),
        sa.Column('alert_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('alert_frequency', sa.String(length=50), nullable=False, server_default='daily'),
        sa.Column('last_alerted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('match_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_saved_searches_id'), 'saved_searches', ['id'], unique=False)
    op.create_index(op.f('ix_saved_searches_user_id'), 'saved_searches', ['user_id'], unique=False)

    op.create_table(
        'lead_purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('price_paid', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_charge_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lead_snapshot', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lead_purchases_id'), 'lead_purchases', ['id'], unique=False)
    op.create_index(op.f('ix_lead_purchases_user_id'), 'lead_purchases', ['user_id'], unique=False)
    op.create_index(op.f('ix_lead_purchases_lead_id'), 'lead_purchases', ['lead_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_lead_purchases_lead_id'), table_name='lead_purchases')
    op.drop_index(op.f('ix_lead_purchases_user_id'), table_name='lead_purchases')
    op.drop_index(op.f('ix_lead_purchases_id'), table_name='lead_purchases')
    op.drop_table('lead_purchases')
    
    op.drop_index(op.f('ix_saved_searches_user_id'), table_name='saved_searches')
    op.drop_index(op.f('ix_saved_searches_id'), table_name='saved_searches')
    op.drop_table('saved_searches')
