"""merge_heads

Revision ID: 20c89abc458b
Revises: 19f70e25a1a2, u8w1q0u8p6av
Create Date: 2025-12-28 19:01:32.294032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20c89abc458b'
down_revision: Union[str, Sequence[str], None] = ('19f70e25a1a2', 'u8w1q0u8p6av')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
