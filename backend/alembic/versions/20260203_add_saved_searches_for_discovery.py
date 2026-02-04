"""Add saved searches for opportunity discovery

Revision ID: 20260203_saved_searches
Revises: u8w1q0u8p6av
Create Date: 2026-02-03 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260203_saved_searches'
down_revision = 'u8w1q0u8p6av'  # Last migration in the chain
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade database schema"""
    
    # Check if table exists, if so, alter it; otherwise create it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'saved_searches' in inspector.get_table_names():
        # Table exists - migrate existing schema
        print("Table 'saved_searches' exists, migrating schema...")
        
        # Add new columns if they don't exist
        columns = [col['name'] for col in inspector.get_columns('saved_searches')]
        
        if 'notification_prefs' not in columns:
            op.add_column('saved_searches', 
                sa.Column('notification_prefs', postgresql.JSONB(), nullable=True))
            
            # Migrate old data: convert alert_enabled + alert_frequency to notification_prefs
            op.execute("""
                UPDATE saved_searches 
                SET notification_prefs = jsonb_build_object(
                    'email', alert_enabled,
                    'push', false,
                    'slack', false,
                    'frequency', COALESCE(alert_frequency, 'daily')
                )
                WHERE notification_prefs IS NULL
            """)
            
            # Make notification_prefs non-nullable after migration
            op.alter_column('saved_searches', 'notification_prefs', nullable=False)
        
        if 'is_active' not in columns:
            op.add_column('saved_searches', 
                sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
        
        # Change filters from JSON to JSONB if needed
        if 'filters' in columns:
            op.execute("ALTER TABLE saved_searches ALTER COLUMN filters TYPE jsonb USING filters::jsonb")
            op.alter_column('saved_searches', 'filters', nullable=False)
        
        # Remove old columns if they exist
        if 'query' in columns:
            op.drop_column('saved_searches', 'query')
        if 'alert_enabled' in columns:
            op.drop_column('saved_searches', 'alert_enabled')
        if 'alert_frequency' in columns:
            op.drop_column('saved_searches', 'alert_frequency')
    
    else:
        # Table doesn't exist - create fresh
        print("Creating new 'saved_searches' table...")
        
        op.create_table(
            'saved_searches',
            sa.Column('id', sa.Integer(), primary_key=True, index=True),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('filters', postgresql.JSONB(), nullable=False),
            sa.Column('notification_prefs', postgresql.JSONB(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
            sa.Column('last_notified_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('match_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()')),
        )
        
        op.create_index('ix_saved_searches_user_id', 'saved_searches', ['user_id'])


def downgrade():
    """Downgrade database schema"""
    
    # Revert to old schema
    op.add_column('saved_searches', sa.Column('query', sa.String(500), nullable=True))
    op.add_column('saved_searches', sa.Column('alert_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('saved_searches', sa.Column('alert_frequency', sa.String(50), nullable=False, server_default='daily'))
    
    # Migrate notification_prefs back to old columns
    op.execute("""
        UPDATE saved_searches 
        SET alert_enabled = (notification_prefs->>'email')::boolean,
            alert_frequency = notification_prefs->>'frequency'
    """)
    
    # Drop new columns
    op.drop_column('saved_searches', 'notification_prefs')
    op.drop_column('saved_searches', 'is_active')
    
    # Convert JSONB back to JSON
    op.execute("ALTER TABLE saved_searches ALTER COLUMN filters TYPE json USING filters::json")
