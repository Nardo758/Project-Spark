# 🚀 ENHANCED WORKSPACE DATABASE MIGRATION
# Migration script for OppGrid enhanced workspace feature

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = 'enhanced_workspace_2024'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create enhanced workspace tables"""
    
    # Create workflow type and status enums
    workflow_status_enum = sa.Enum('not_started', 'in_progress', 'completed', 'skipped', 'failed', name='workflowstatus')
    workflow_status_enum.create(op.get_bind())
    
    workflow_type_enum = sa.Enum('lean_validation', 'enterprise_b2b', 'product_market_fit', 'custom', name='workflowtype')
    workflow_type_enum.create(op.get_bind())
    
    artifact_type_enum = sa.Enum('interview', 'survey', 'document', 'analysis', 'prototype', 'competitor', 'financial', 'market', name='researchartifacttype')
    artifact_type_enum.create(op.get_bind())
    
    artifact_status_enum = sa.Enum('draft', 'in_progress', 'completed', 'archived', name='researchartifactstatus')
    artifact_status_enum.create(op.get_bind())
    
    # Create enhanced_user_workspaces table
    op.create_table('enhanced_user_workspaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('opportunity_id', sa.Integer(), nullable=False),
        sa.Column('custom_title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ai_context', sa.Text(), nullable=True),
        sa.Column('workflow_type', workflow_type_enum, nullable=False),
        sa.Column('workflow_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('current_stage', sa.String(length=100), nullable=True),
        sa.Column('current_phase', sa.String(length=100), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=True),
        sa.Column('stage_progress', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_research_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('research_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('validation_score', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', workflow_status_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_enhanced_user_workspaces_id', 'enhanced_user_workspaces', ['id'], unique=False)
    op.create_index('ix_enhanced_user_workspaces_user_id', 'enhanced_user_workspaces', ['user_id'], unique=False)
    op.create_index('ix_enhanced_user_workspaces_opportunity_id', 'enhanced_user_workspaces', ['opportunity_id'], unique=False)
    
    # Create enhanced_workflow_stages table
    op.create_table('enhanced_workflow_stages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('duration_weeks', sa.Integer(), nullable=True),
        sa.Column('status', workflow_status_enum, nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stage_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('research_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['enhanced_user_workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_enhanced_workflow_stages_id', 'enhanced_workflow_stages', ['id'], unique=False)
    op.create_index('ix_enhanced_workflow_stages_workspace_id', 'enhanced_workflow_stages', ['workspace_id'], unique=False)
    
    # Create enhanced_workflow_tasks table
    op.create_table('enhanced_workflow_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stage_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('task_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_assistance_requested', sa.Boolean(), nullable=True),
        sa.Column('ai_assistance_completed', sa.Boolean(), nullable=True),
        sa.Column('ai_assistance_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['stage_id'], ['enhanced_workflow_stages.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_enhanced_workflow_tasks_id', 'enhanced_workflow_tasks', ['id'], unique=False)
    op.create_index('ix_enhanced_workflow_tasks_stage_id', 'enhanced_workflow_tasks', ['stage_id'], unique=False)
    
    # Create enhanced_research_artifacts table
    op.create_table('enhanced_research_artifacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('stage_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('artifact_type', artifact_type_enum, nullable=False),
        sa.Column('status', artifact_status_enum, nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('ai_insights', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_summary', sa.Text(), nullable=True),
        sa.Column('ai_recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['stage_id'], ['enhanced_workflow_stages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['enhanced_user_workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_enhanced_research_artifacts_id', 'enhanced_research_artifacts', ['id'], unique=False)
    op.create_index('ix_enhanced_research_artifacts_workspace_id', 'enhanced_research_artifacts', ['workspace_id'], unique=False)
    op.create_index('ix_enhanced_research_artifacts_stage_id', 'enhanced_research_artifacts', ['stage_id'], unique=False)
    
    # Create enhanced_workspace_chat table
    op.create_table('enhanced_workspace_chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['enhanced_user_workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_enhanced_workspace_chat_id', 'enhanced_workspace_chat', ['id'], unique=False)
    op.create_index('ix_enhanced_workspace_chat_workspace_id', 'enhanced_workspace_chat', ['workspace_id'], unique=False)
    
    # Create custom_workflows table
    op.create_table('custom_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workflow_type', workflow_type_enum, nullable=False),
        sa.Column('workflow_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('workflow_stages', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('workflow_tasks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('workflow_tools', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('average_completion_time', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['enhanced_user_workspaces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_custom_workflows_id', 'custom_workflows', ['id'], unique=False)
    op.create_index('ix_custom_workflows_workspace_id', 'custom_workflows', ['workspace_id'], unique=False)
    op.create_index('ix_custom_workflows_created_by', 'custom_workflows', ['created_by'], unique=False)

def downgrade():
    """Drop enhanced workspace tables"""
    
    op.drop_table('custom_workflows')
    op.drop_table('enhanced_workspace_chat')
    op.drop_table('enhanced_research_artifacts')
    op.drop_table('enhanced_workflow_tasks')
    op.drop_table('enhanced_workflow_stages')
    op.drop_table('enhanced_user_workspaces')
    
    # Drop enums
    sa.Enum(name='workflowstatus').drop(op.get_bind())
    sa.Enum(name='workflowtype').drop(op.get_bind())
    sa.Enum(name='researchartifacttype').drop(op.get_bind())
    sa.Enum(name='researchartifactstatus').drop(op.get_bind())

# For manual execution
if __name__ == "__main__":
    upgrade()
    print("✅ Enhanced workspace tables created successfully!")