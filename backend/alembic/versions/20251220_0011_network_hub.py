"""add network hub tables

Revision ID: 20251220_0011
Revises: 20251220_0010
Create Date: 2025-12-20
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20251220_0011"
down_revision = "20251220_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "connection_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("context_type", sa.String(length=40), nullable=True),
        sa.Column("context_id", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("requester_id", "target_user_id", "context_type", "context_id", name="uq_connection_request_pair_context"),
    )
    op.create_index("ix_connection_requests_requester_id", "connection_requests", ["requester_id"], unique=False)
    op.create_index("ix_connection_requests_target_user_id", "connection_requests", ["target_user_id"], unique=False)
    op.create_index("ix_connection_requests_status", "connection_requests", ["status"], unique=False)

    op.create_table(
        "message_threads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("thread_type", sa.String(length=20), nullable=False, server_default="direct"),
        sa.Column("user_a_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_b_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("context_type", sa.String(length=40), nullable=True),
        sa.Column("context_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("user_a_id", "user_b_id", "context_type", "context_id", name="uq_thread_pair_context"),
    )
    op.create_index("ix_message_threads_user_a_id", "message_threads", ["user_a_id"], unique=False)
    op.create_index("ix_message_threads_user_b_id", "message_threads", ["user_b_id"], unique=False)
    op.create_index("ix_message_threads_thread_type", "message_threads", ["thread_type"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("thread_id", sa.Integer(), sa.ForeignKey("message_threads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sender_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_messages_thread_id", "messages", ["thread_id"], unique=False)
    op.create_index("ix_messages_sender_id", "messages", ["sender_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_messages_sender_id", table_name="messages")
    op.drop_index("ix_messages_thread_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("ix_message_threads_thread_type", table_name="message_threads")
    op.drop_index("ix_message_threads_user_b_id", table_name="message_threads")
    op.drop_index("ix_message_threads_user_a_id", table_name="message_threads")
    op.drop_table("message_threads")

    op.drop_index("ix_connection_requests_status", table_name="connection_requests")
    op.drop_index("ix_connection_requests_target_user_id", table_name="connection_requests")
    op.drop_index("ix_connection_requests_requester_id", table_name="connection_requests")
    op.drop_table("connection_requests")

