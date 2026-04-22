"""Fusionando ramas paralelas

Revision ID: b5e5dc1f6eed
Revises: 429f53ff53a8
Create Date: 2026-04-21 22:59:00.409034

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5e5dc1f6eed'
down_revision: Union[str, Sequence[str], None] = '429f53ff53a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
