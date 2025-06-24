"""db init

Revision ID: ccffb52c2466
Revises:
Create Date: 2025-06-03 13:37:01.446713

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "ccffb52c2466"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
