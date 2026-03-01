"""rename 'completed' field in workout table to 'status'

Revision ID: 133fe333d9b4
Revises: 31d609f9530d
Create Date: 2026-03-01 08:02:32.053601

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "133fe333d9b4"
down_revision: Union[str, Sequence[str], None] = "31d609f9530d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column("workout", "completed", new_column_name="status")


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column("workout", "status", new_column_name="completed")
